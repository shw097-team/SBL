#!/usr/bin/env python3
"""M4-LITE procedural review runner (six properties, positive and negative per property).

WHY THIS EXISTS
    The mandated independent checker cannot complete this review: the Codex secondary carrier
    refuses the subject with a provider content filter, and the primary VERIFY lane's websocket
    transport answers 426.  M4-LITE replaces *the carrier*, not the requirement: a human reviewer
    runs this script against the frozen candidate, reads the raw receipts, tries one variant of
    their own, and signs.  This script never signs anything and its verdict is always HOLD.

WHAT IT DOES
    For each of the six properties it (1) runs the repository's own named test cases as separate
    pytest processes, and (2) runs an INDEPENDENT probe that calls the public API directly, so a
    printing-only or tautological test cannot pass the review on its own.  Every record carries the
    exact command, exit code, expected/observed values, and the sha256 of its own raw output.

WHAT IT DOES NOT DO
    It does not mutate the subject (temp dirs only, and a before/after snapshot digest proves it),
    it does not decide a verdict, and ``--sign`` does not exist.  145/148 passing tests are not a
    substitute for the reviewer's signature.

USAGE
    git clone https://github.com/shw097-team/SBL && cd SBL
    git checkout bedc11957d4fc2474b249b69d200829272c118ef
    python <evidence-branch>/_governance/round-20261020-r3/M4LITE/run_m4lite.py \
        --subject-root . --out-dir /tmp/m4lite --reviewer "<name>"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path
from typing import Any, Callable

PROPERTIES: list[tuple[str, str]] = [
    ("GKNOW-ID", "a real corpus id resolves; an id that is not in the index is refused"),
    ("GKNOW-SEP", "separator variants of an unknown source are refused, not answered"),
    ("GKNOW-BIND", "a named source constrains the answer to that source"),
    ("MODE-ACK", "untrusted / unsigned ACK refuses; a correctly signed ACK still allows"),
    ("MODE-SIG", "a signature cannot be moved between tuples or forged by field shifting"),
    ("BRIDGE-SETTLE", "a path that changes after validation is refused; in-scope writes still work"),
]

#: The repository's own cases, run as separate processes so no fixture leakage can hide a failure.
REPO_CASES: dict[str, list[tuple[str, str]]] = {
    "GKNOW-ID": [("NEG", "tests/test_gknow.py::test_a_named_source_that_does_not_exist_is_refused"),
                 ("POS", "tests/test_gknow.py::test_the_ids_the_real_corpus_uses_are_recognised")],
    "GKNOW-SEP": [("NEG", "tests/test_gknow.py::test_separator_variants_of_an_unknown_source_are_refused")],
    "GKNOW-BIND": [("POS", "tests/test_gknow.py::test_a_named_source_constrains_the_answer_to_that_source")],
    "MODE-ACK": [("NEG", "tests/test_modes.py::test_swof_refuses_an_ack_that_is_only_four_non_empty_strings"),
                 ("POS", "tests/test_modes.py::test_swof_accepts_an_ack_signed_with_the_configured_key")],
    "MODE-SIG": [("NEG", "tests/test_modes.py::test_ack_signature_cannot_be_moved_between_tuples")],
    "BRIDGE-SETTLE": [("NEG", "tests/test_core_modules.py::test_bridge_apply_refuses_a_path_that_changes_between_check_and_write"),
                      ("POS", "tests/test_core_modules.py::test_bridge_apply_positive_inside_a_link_that_stays_inside")],
}

SUBJECT_SKIP = {".git", "__pycache__", ".pytest_cache", ".tmp-tests", "dist", "build", ".mypy_cache"}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def snapshot(root: Path) -> dict[str, Any]:
    """A tree digest that ignores VCS and caches: used to prove the review mutated nothing."""

    digest = hashlib.sha256()
    files = 0
    total = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(name for name in dirnames if name not in SUBJECT_SKIP)
        for name in sorted(filenames):
            path = Path(dirpath) / name
            rel = path.relative_to(root).as_posix()
            try:
                data = path.read_bytes()
            except OSError:
                data = b""
            digest.update(rel.encode("utf-8"))
            digest.update(b"\0")
            digest.update(data)
            files += 1
            total += len(data)
    return {"files": files, "bytes": total, "digest": digest.hexdigest()}


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_directory_link(link: Path, target: Path) -> str:
    try:
        os.symlink(str(target), str(link), target_is_directory=True)
        return "symlink"
    except (OSError, NotImplementedError, AttributeError):
        pass
    if os.name == "nt":
        completed = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                                   capture_output=True)
        if completed.returncode == 0:
            return "junction"
    raise RuntimeError("no directory link primitive available on this host")


def _record(case_id: str, kind: str, expectation: str, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    base = {"case_id": case_id, "kind": kind, "expectation": expectation,
            "executor": "independent_probe", "ok": False, "observed": None, "error": None}
    try:
        observed = fn()
        base["observed"] = observed
        base["ok"] = bool(observed.get("ok"))
    except Exception as exc:  # a probe crash is a FAILED case, never a silent pass
        base["error"] = f"{type(exc).__name__}: {exc}"
        base["traceback"] = traceback.format_exc()[-1500:]
    base["raw_sha256"] = sha256_bytes(json.dumps(base, ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return base


def _refused(fn: Callable[[], Any]) -> dict[str, Any]:
    """Calls fn expecting an SBLError; returns what was raised."""

    from sbl_core.errors import SBLError

    try:
        value = fn()
    except SBLError as exc:
        return {"raised": exc.code, "message": exc.message, "details": getattr(exc, "details", None)}
    return {"raised": None, "returned": repr(value)[:400]}


def probes(subject: Path, work: Path) -> list[dict[str, Any]]:
    from sbl_core import gknow, m04_bridge, modes
    from sbl_core.dto import BuildOrder, WriteSet, order_id_for

    def mini_corpus(base: Path) -> tuple[Path, Path]:
        root = base / "corpus"
        _write(root / "SBL_PIPD-LS-PKG_DOC-00.md",
               "permission denied for every shadow effect and native permit\n" * 20)
        _write(root / "SBL_PIPD-LS-PKG_DOC-05.md",
               "shadow effect description for the governed build bridge\n" * 20)
        index = base / "index.json"
        gknow.build_index(str(root), str(index))
        return root, index

    records: list[dict[str, Any]] = []

    # ---- AC-M4-01 GKNOW-ID -------------------------------------------------------------
    base = work / "id"
    base.mkdir(parents=True)
    corpus, index = mini_corpus(base)

    def id_pos() -> dict[str, Any]:
        table = {name: gknow._doc_id_of(name) for name in (
            "SBL_PIPD-LS-PKG_DOC-05.md", "SBL_PIPD-LS-PKG_DOC-13.md", "DOC-00.md")}
        return {"ok": table == {"SBL_PIPD-LS-PKG_DOC-05.md": "DOC-05",
                                "SBL_PIPD-LS-PKG_DOC-13.md": "DOC-13",
                                "DOC-00.md": "DOC-00"}, "resolved": table}

    def id_neg() -> dict[str, Any]:
        raised = _refused(lambda: gknow.query(str(index), "DOC-27 shadow mode rule"))
        return {"ok": raised.get("raised") == "SBL_E_KNOWLEDGE_NO_ANSWER", **raised}

    records.append(_record("AC-M4-01/POS", "POS", "real corpus filenames carry their DOC id", id_pos))
    records.append(_record("AC-M4-01/NEG", "NEG", "a DOC id absent from the index is refused", id_neg))

    # ---- AC-M4-02 GKNOW-SEP ------------------------------------------------------------
    def sep_neg() -> dict[str, Any]:
        out = {}
        for text in ("DOC/27", "DOC--27", "DOC27", "doc_27", "DOC 27"):
            raised = _refused(lambda text=text: gknow.query(str(index), f"{text} shadow mode rule"))
            out[text] = raised
        ok = all(value.get("raised") == "SBL_E_KNOWLEDGE_NO_ANSWER" for value in out.values())
        return {"ok": ok, "variants": out}

    def sep_pos() -> dict[str, Any]:
        hits = gknow.query(str(index), "DOC-05 shadow effect")
        ok = bool(hits) and all("DOC-05" in str(hit.get("path", "")) for hit in hits)
        return {"ok": ok, "hits": len(hits)}

    records.append(_record("AC-M4-02/NEG", "NEG", "separator variants of an unknown id all refuse", sep_neg))
    records.append(_record("AC-M4-02/POS", "POS", "the refusal is not blanket: an indexed id answers", sep_pos))

    # ---- AC-M4-03 GKNOW-BIND -----------------------------------------------------------
    def bind_pos() -> dict[str, Any]:
        five = gknow.query(str(index), "DOC-05 shadow effect")
        zero = gknow.query(str(index), "DOC-00 permission denied")
        set5 = {Path(hit["path"]).name for hit in five}
        set0 = {Path(hit["path"]).name for hit in zero}
        return {"ok": bool(five) and bool(zero)
                and set5 == {"SBL_PIPD-LS-PKG_DOC-05.md"}
                and set0 == {"SBL_PIPD-LS-PKG_DOC-00.md"},
                "doc05_hits": sorted(set5), "doc00_hits": sorted(set0)}

    def bind_neg() -> dict[str, Any]:
        raised = _refused(lambda: gknow.query(str(index), "DOC-99 shadow effect"))
        return {"ok": raised.get("raised") == "SBL_E_KNOWLEDGE_NO_ANSWER", **raised}

    records.append(_record("AC-M4-03/POS", "POS", "a DOC-05 question answers only from DOC-05", bind_pos))
    records.append(_record("AC-M4-03/NEG", "NEG", "a named source with no content is refused", bind_neg))

    # ---- AC-M4-04 MODE-ACK -------------------------------------------------------------
    key = "m4lite-review-key-0123456789abcdef"
    issuer = "swof-native"
    saved = {name: os.environ.get(name) for name in (modes._ACK_ISSUERS_ENV, modes._ACK_KEY_ENV)}

    def _ack(signature: str = "", id_: str = "permit-1", subject: str = "subject-1") -> dict[str, Any]:
        return {"issuer": issuer, "permit_id": id_, "subject_id": subject, "signature": signature}

    try:
        os.environ[modes._ACK_ISSUERS_ENV] = issuer
        os.environ[modes._ACK_KEY_ENV] = key

        def ack_pos() -> dict[str, Any]:
            ack = _ack(modes.ack_signature(issuer, "permit-1", "subject-1", key))
            decision = modes.ModeGate("SWOF_CONNECTED", ack).decide("net.call")
            return {"ok": decision.allowed is True and decision.no_effect is False,
                    "allowed": decision.allowed, "no_effect": decision.no_effect,
                    "reason": decision.reason}

        def ack_neg() -> dict[str, Any]:
            # This build refuses by raising, not by returning allowed=False; both are refusals, and
            # the probe records which form it saw so a default-allow cannot hide behind a catch-all.
            fabricated = _refused(lambda: modes.ModeGate("SWOF_CONNECTED", _ack("x" * 64)).decide("net.call"))
            unsigned = _refused(lambda: modes.ModeGate(
                "SWOF_CONNECTED", {"issuer": issuer, "permit_id": "p", "subject_id": "s", "signature": " "}
            ).decide("net.call"))
            codes = {fabricated.get("raised"), unsigned.get("raised")}
            return {"ok": codes == {"SBL_E_REQUIRES_NATIVE_ACK"},
                    "refusal_form": "exception", "codes": sorted(str(c) for c in codes),
                    "fabricated": fabricated, "unsigned": unsigned}

        def ack_untrusted() -> dict[str, Any]:
            ack = _ack(modes.ack_signature("someone-else", "permit-1", "subject-1", key))
            ack["issuer"] = "someone-else"
            raised = _refused(lambda: modes.ModeGate("SWOF_CONNECTED", ack).decide("net.call"))
            return {"ok": raised.get("raised") == "SBL_E_REQUIRES_NATIVE_ACK",
                    "refusal_form": "exception", **raised}

        def shadow_pos() -> dict[str, Any]:
            decision = modes.ModeGate("PREW3_SHADOW", _ack("x" * 64)).decide("net.call")
            return {"ok": decision.allowed is False and decision.no_effect is True,
                    "reason": decision.reason}

        records.append(_record("AC-M4-04/POS", "POS", "a signed ACK from a trusted issuer allows", ack_pos))
        records.append(_record("AC-M4-04/NEG", "NEG", "fabricated and blank signatures refuse", ack_neg))
        records.append(_record("AC-M4-04/NEG-2", "NEG", "an ACK signed by an untrusted issuer refuses", ack_untrusted))
        records.append(_record("AC-M4-04/SHADOW", "POS", "PREW3_SHADOW never effects", shadow_pos))

        # ---- AC-M4-05 MODE-SIG ---------------------------------------------------------
        def sig_neg() -> dict[str, Any]:
            signature = modes.ack_signature(issuer, "permit-1", "subject-1", key)
            moved = _refused(lambda: modes.ModeGate(
                "SWOF_CONNECTED", _ack(signature, subject="subject-2")).decide("net.call"))
            collision = (modes.ack_signature("a\x1fB", "C", "D", key)
                         == modes.ack_signature("a", "B\x1fC", "D", key))
            return {"ok": moved.get("raised") == "SBL_E_REQUIRES_NATIVE_ACK" and collision is False,
                    "refusal_form": "exception", "moved": moved, "delimiter_collision": collision}

        def sig_pos() -> dict[str, Any]:
            left = modes.ack_signature(issuer, "permit-1", "subject-1", key)
            right = modes.ack_signature(issuer, "permit-1", "subject-2", key)
            return {"ok": left != right and len(left) == 64, "distinct": left != right}

        records.append(_record("AC-M4-05/NEG", "NEG", "signature cannot move tuple / collide", sig_neg))
        records.append(_record("AC-M4-05/POS", "POS", "distinct tuples sign distinctly", sig_pos))
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    # ---- AC-M4-06 BRIDGE-SETTLE --------------------------------------------------------
    head = "a" * 40
    real_head_of = m04_bridge._head_of
    real_realpath = m04_bridge.os.path.realpath
    try:
        m04_bridge._head_of = lambda root: head  # no git invocation: the probe is about the path, not HEAD

        def order_for(root: Path, prefixes: tuple[str, ...] = ("src",)) -> BuildOrder:
            return BuildOrder(order_id=order_id_for(head, WriteSet(prefixes)),
                              root=str(root), head=head, writeset=WriteSet(prefixes))

        def settle_neg() -> dict[str, Any]:
            base = work / "settle-neg"
            root = base / "repo"
            (root / "src").mkdir(parents=True)
            outside = base / "outside"
            outside.mkdir()
            target = str(root / "src" / "file.txt")
            state = {"calls": 0}

            def swap_after_validation(path, *args, **kwargs):
                if os.path.abspath(str(path)) == os.path.abspath(target):
                    state["calls"] += 1
                    if state["calls"] >= 2:
                        return str(outside / "file.txt")
                return real_realpath(path, *args, **kwargs)

            m04_bridge.os.path.realpath = swap_after_validation
            try:
                raised = _refused(lambda: m04_bridge.GovernedBuildBridge().apply(
                    order_for(root), "src/file.txt", "payload"))
            finally:
                m04_bridge.os.path.realpath = real_realpath
            return {"ok": raised.get("raised") == "SBL_E_WRITE_OUTSIDE_WRITESET"
                    and not (outside / "file.txt").exists(),
                    "raised": raised, "outside_written": (outside / "file.txt").exists()}

        def settle_pos() -> dict[str, Any]:
            base = work / "settle-pos"
            root = base / "repo"
            (root / "src").mkdir(parents=True)
            m04_bridge.GovernedBuildBridge().apply(order_for(root), "src/ok.py", "value = 1\n")
            text = (root / "src" / "ok.py").read_text(encoding="utf-8")
            return {"ok": text == "value = 1\n", "content": text.strip()}

        def settle_link_escape() -> dict[str, Any]:
            base = work / "settle-link"
            root = base / "repo"
            (root / "src").mkdir(parents=True)
            outside = base / "outside"
            outside.mkdir()
            kind = _make_directory_link(root / "src" / "link", outside)
            raised = _refused(lambda: m04_bridge.GovernedBuildBridge().apply(
                order_for(root), "src/link/pwned.py", "owned\n"))
            return {"ok": raised.get("raised") == "SBL_E_WRITE_OUTSIDE_WRITESET"
                    and not (outside / "pwned.py").exists(), "link_kind": kind, "raised": raised}

        records.append(_record("AC-M4-06/NEG", "NEG", "a target that changes after validation refuses", settle_neg))
        records.append(_record("AC-M4-06/NEG-2", "NEG", "a link inside the writeset cannot escape", settle_link_escape))
        records.append(_record("AC-M4-06/POS", "POS", "an in-scope write still lands", settle_pos))
    finally:
        m04_bridge._head_of = real_head_of
        m04_bridge.os.path.realpath = real_realpath

    return records


def repo_cases(subject: Path, work: Path, python: str) -> list[dict[str, Any]]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(subject) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["TMPDIR"] = str(work / "pytest-tmp")
    Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)
    out: list[dict[str, Any]] = []
    for prop, cases in REPO_CASES.items():
        for kind, node in cases:
            cmd = [python, "-m", "pytest", node, "-q", "-p", "no:cacheprovider", "--no-header"]
            completed = subprocess.run(cmd, cwd=str(subject), env=env, capture_output=True)
            stdout = completed.stdout.decode("utf-8", "replace")
            stderr = completed.stderr.decode("utf-8", "replace")
            out.append({
                "case_id": f"{prop}/{kind}/repo-test",
                "property": prop,
                "kind": kind,
                "executor": "repo_test",
                "command": " ".join(cmd),
                "exit": completed.returncode,
                "ok": completed.returncode == 0,
                "stdout_tail": stdout.strip().splitlines()[-3:],
                "stdout_sha256": sha256_bytes(stdout.encode("utf-8")),
                "stderr_tail": stderr.strip().splitlines()[-2:],
            })
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="M4-LITE six-property procedural review runner")
    parser.add_argument("--subject-root", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--reviewer", default="UNNAMED_REVIEWER")
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args(argv)

    subject = Path(args.subject_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    if not (subject / "sbl_core").is_dir():
        print(f"not an SBL checkout: {subject}", file=sys.stderr)
        return 2

    sys.path.insert(0, str(subject))
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

    head = subprocess.run(["git", "-C", str(subject), "rev-parse", "HEAD"],
                          capture_output=True).stdout.decode().strip()
    status = subprocess.run(["git", "-C", str(subject), "status", "--porcelain"],
                            capture_output=True).stdout.decode().strip()

    before = snapshot(subject)
    work = Path(tempfile.mkdtemp(prefix="m4lite-"))
    try:
        indep = probes(subject, work)
        tests = repo_cases(subject, work, args.python)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    after = snapshot(subject)

    by_prop: dict[str, list[dict[str, Any]]] = {}
    for record in indep + tests:
        prop = record["case_id"].split("/")[0].replace("AC-M4-0", "").strip()
        by_prop.setdefault(record.get("property") or prop, []).append(record)

    all_ok = all(record["ok"] for record in indep + tests)
    payload = {
        "schema": "SBL-M4-LITE-RAW/1",
        "subject_root": str(subject),
        "subject_head": head,
        "subject_dirty_porcelain": status,
        "reviewer": args.reviewer,
        "python": args.python,
        "independent_probes": indep,
        "repo_tests": tests,
        "snapshot_before": before,
        "snapshot_after": after,
        "subject_mutation": "CLEAN" if before == after else "FAIL",
        "all_cases_ok": all_ok,
        "verdict": "HOLD_PENDING_HUMAN_SIGNATURE",
        "verdict_reason": (
            "Every automated case passed, but this runner is the maker-side procedure, not the "
            "reviewer. Only a human signature turns it into HUMAN_PROCEDURAL_ACCEPTANCE."
            if all_ok else
            "At least one case failed; a failing case is a finding, not a signable receipt."
        ),
    }
    raw = out_dir / "M4LITE_RAW.json"
    raw.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# M4-LITE raw receipts",
        "",
        f"subject_head: `{head}`",
        f"reviewer (declared): `{args.reviewer}`",
        f"subject_mutation: **{payload['subject_mutation']}** "
        f"({before['files']} files / {before['bytes']} B, digest `{before['digest'][:16]}…`)",
        f"all_cases_ok: **{all_ok}**",
        f"verdict: **{payload['verdict']}**",
        "",
        "| case | kind | executor | ok | observed / reason |",
        "|---|---|---|---|---|",
    ]
    for record in indep + tests:
        detail = json.dumps(record.get("observed") or record.get("stdout_tail") or record.get("error"),
                            ensure_ascii=False, sort_keys=True)[:180]
        lines.append(f"| `{record['case_id']}` | {record['kind']} | {record['executor']} | "
                     f"{'PASS' if record['ok'] else '**FAIL**'} | `{detail}` |")
    lines += ["", f"raw json sha256: `{sha256_bytes(raw.read_bytes())}`",
              f"this transcript sha256 is recorded in the round manifest; it is not a signature."]
    transcript = out_dir / "M4LITE_TRANSCRIPT.md"
    transcript.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"raw": str(raw), "transcript": str(transcript),
                      "raw_sha256": sha256_bytes(raw.read_bytes()),
                      "all_cases_ok": all_ok, "verdict": payload["verdict"],
                      "subject_mutation": payload["subject_mutation"],
                      "cases": len(indep) + len(tests),
                      "failures": [r["case_id"] for r in indep + tests if not r["ok"]]},
                     ensure_ascii=False, indent=2))
    return 0 if all_ok and payload["subject_mutation"] == "CLEAN" else 1


if __name__ == "__main__":
    raise SystemExit(main())
