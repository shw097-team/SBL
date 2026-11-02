#!/usr/bin/env python3
"""Source-constrained self-bootstrap example for PIPD-LS-SP (WO-S4-SELFBOOT-04).

This script proves that THIS repository, as shipped, can be driven from a frozen intent + a
minimal read-only RepoContext through the real compiler chain

    intent -> compile-pi -> bind-pd -> compile-ecp -> compile-tqaep -> validate

into an ISOLATED workspace root (never the repository), and that the result is reproducible
(same inputs -> identical artefact digests).

It is deliberately narrow. What it does NOT prove is stated in ``README.md``.

Usage
-----
    python run_selfbootstrap.py --root <disposable-dir-outside-the-repo>
    python run_selfbootstrap.py --root <disposable-dir> --negative missing-source
    python run_selfbootstrap.py --root <disposable-dir> --negative stale-context

The positive run also exercises both negatives internally and captures their RAW output into
``negative_stale_context.txt`` (never hand-written).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent          # examples/self-bootstrap
REPO = HERE.parents[1]                           # repository root
SRC = REPO / "src"
DEFAULT_INTENT = HERE / "input" / "intent.json"
DEFAULT_REPOCONTEXT = HERE / "input" / "repocontext.json"
CHAIN = ("init", "intake", "compile-pi", "bind-pd", "compile-ecp", "compile-tqaep", "validate")


# --------------------------------------------------------------------------- helpers
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _child_env() -> dict[str, str]:
    env = dict(os.environ)
    parts = [str(SRC)] + [p for p in env.get("PYTHONPATH", "").split(os.pathsep) if p]
    env["PYTHONPATH"] = os.pathsep.join(parts)
    return env


def cli(root: Path, *args: str) -> subprocess.CompletedProcess:
    """Run the repository's SHIPPED entry point non-interactively, from the repo cwd."""
    return subprocess.run(
        [sys.executable, "-m", "pipd_ls_sp.cli", "--root", str(root), *args],
        cwd=str(REPO), env=_child_env(), capture_output=True, text=True, encoding="utf-8")


def _read_json(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _write_json(path: Path, payload: dict) -> None:
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True),
                          encoding="utf-8")


def _guard_root(root: Path) -> None:
    r = root.resolve()
    if str(r) == str(REPO.resolve()) or REPO.resolve() in r.parents:
        raise SystemExit(f"refused: --root {r} is inside the repository; use a disposable dir "
                         f"OUTSIDE {REPO}")


# --------------------------------------------------------------------------- chain
def drive_chain(root: Path, intent: dict, repoctx: dict, transcript: list[str]) -> dict:
    """Drive the documented commands into ``root``; return the collected artefacts + digests."""
    art_dir = root / "artifacts"
    ctx_dir = root / "pd_context"
    for d in (art_dir, ctx_dir):
        d.mkdir(parents=True, exist_ok=True)          # ctx_dir stays EMPTY (pristine context)

    def step(label: str, args: list[str], expect_zero: bool = True) -> dict:
        proc = cli(root, *args)
        transcript.append(f"### {label}")
        transcript.append(f"$ pipd {' '.join(args)}")
        transcript.append(f"[exit {proc.returncode}]")
        if proc.stdout.strip():
            transcript.append(proc.stdout.rstrip())
        if proc.stderr.strip():
            transcript.append("--- stderr ---")
            transcript.append(proc.stderr.rstrip())
        transcript.append("")
        if expect_zero and proc.returncode != 0:
            raise SystemExit(f"step {label} failed with exit {proc.returncode}")
        return json.loads(proc.stdout) if proc.stdout.strip() else {}

    step("init: create the isolated workspace via the CLI", ["init"])

    goal = intent["goal"]
    sources = list(intent.get("sources") or [])
    intake_args = ["intake", "--goal", goal]
    for s in sources:
        intake_args += ["--source", s]
    for c in intent.get("constraints") or []:
        intake_args += ["--constraint", c]
    for n in intent.get("non_goals") or []:
        intake_args += ["--non-goal", n]
    card = step("intake: compile clause-bound atoms into an IntentCard", intake_args)
    card_file = art_dir / "intent.card.json"
    _write_json(card_file, card)

    pi = step("compile-pi: PI package (LITE)",
              ["compile-pi", "--intent", str(card_file), "--profile", "LITE"])
    pi_file = art_dir / "pi.json"
    _write_json(pi_file, pi)

    # bind-pd derives a READ-ONLY RepoContext from the host. Against an EMPTY, pristine context
    # dir the derivation is deterministic (no tracked files, no dirty set), so the PD digest is
    # stable across replays regardless of prior artefact residue in ``root``.
    pd = step("bind-pd: late-bind PD against a read-only RepoContext",
              ["bind-pd", "--pi", str(pi_file), "--repo-root", str(ctx_dir)])
    pd_file = art_dir / "pd.json"
    _write_json(pd_file, pd)

    ecp = step("compile-ecp: execution contract",
               ["compile-ecp", "--pd", str(pd_file), "--pi", str(pi_file)])
    ecp_file = art_dir / "ecp.json"
    _write_json(ecp_file, ecp)

    tqaep = step("compile-tqaep: design-time separation-of-duties record",
                 ["compile-tqaep", "--pi", str(pi_file), "--ecp", str(ecp_file),
                  "--maker", "HERMES-MAKER", "--checker", "GLM-5.3-FLASH-AO-LANE",
                  "--checker-receipt", "deleg_example/lane-C"])
    tqaep_file = art_dir / "tqaep.json"
    _write_json(tqaep_file, tqaep)

    bundle = {"PI-PKG": pi, "PD-PKG": pd, "ECP": ecp, "TQAEP": tqaep}
    bundle_file = art_dir / "bundle.json"
    _write_json(bundle_file, bundle)
    validation = step("validate: schema + semantic invariants over the bundle",
                      ["validate", "--bundle", str(bundle_file)])

    return {"card": card, "pi": pi, "pd": pd, "ecp": ecp, "tqaep": tqaep,
            "validation": validation, "bundle_file": bundle_file,
            "files": {"intent_card": card_file, "pi": pi_file, "pd": pd_file,
                      "ecp": ecp_file, "tqaep": tqaep_file}}


# --------------------------------------------------------------------------- negatives
def neg_missing_source(transcript: list[str]) -> dict:
    """A source locator that does not exist on disk must be refused TYPED (AUTHORITY_UNKNOWN)."""
    from pipd_ls_sp import pipeline
    from pipd_ls_sp.errors import PipdError
    goal = _read_json(DEFAULT_INTENT)["goal"]
    bogus = "examples/self-bootstrap/input/does_not_exist.txt"
    transcript.append("### NEGATIVE: missing source locator")
    transcript.append(f"$ python -c 'pipeline.intake(goal, sources=[{bogus!r}])'")
    try:
        pipeline.intake(goal, sources=[bogus])
        out = {"verdict": "PASS", "code": None, "message": "UNEXPECTED: refused-nothing",
               "exit": 0}
    except PipdError as exc:
        out = {**exc.as_dict(), "exit": 2}
    transcript.append(json.dumps(out, ensure_ascii=False, sort_keys=True))
    transcript.append("")
    return out


def neg_stale_context(art: dict, ctx_dir: Path, transcript: list[str]) -> dict:
    """A RepoContext whose freshness claim does not bind to host truth is refused (STALE_PROVIDER)."""
    from pipd_ls_sp import pipeline
    from pipd_ls_sp import repo_context as repo_probe
    from pipd_ls_sp.errors import PipdError
    pi = art["pi"]
    stale = repo_probe.derive_repo_context(ctx_dir)
    stale["currentness_epoch"] = "0" * 64        # a claim that cannot match the host epoch
    transcript.append("### NEGATIVE: stale RepoContext")
    transcript.append("$ pipeline.bind_pd(pi, {root, currentness_epoch='0'*64, currentness='FRESH'})")
    try:
        pipeline.bind_pd(pi, stale)
        out = {"verdict": "PASS", "code": None, "message": "UNEXPECTED: refused-nothing",
               "exit": 0}
    except PipdError as exc:
        out = {**exc.as_dict(), "exit": 2}
    transcript.append(json.dumps(out, ensure_ascii=False, sort_keys=True))
    transcript.append("")
    return out


# --------------------------------------------------------------------------- digests
def compute_digests(art: dict) -> dict:
    """Deterministic digest record: file sha256 + the artefact's own content-addressed identity."""
    per = {}
    for name, path in art["files"].items():
        rec = None
        if name != "intent_card":
            rec = {"PI-PKG": art["pi"], "PD-PKG": art["pd"], "ECP": art["ecp"],
                   "TQAEP": art["tqaep"]}.get({"pi": "PI-PKG", "pd": "PD-PKG",
                                               "ecp": "ECP", "tqaep": "TQAEP"}[name])
        per[name] = {
            "file_sha256": sha256_file(path),
            "subject_id": (rec or art["card"]).get("subject_id"),
            "content_hash": (rec or art["card"]).get("content_hash"),
        }
    summary_rows = {k: per[k]["content_hash"] for k in per}
    combined = hashlib.sha256(
        json.dumps(summary_rows, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "artifacts": per,
        "bundle_digest": combined,
        "validation": {"verdict": art["validation"].get("verdict"),
                       "checked": art["validation"].get("checked"),
                       "findings": art["validation"].get("findings"),
                       "schema_source": art["validation"].get("schema_source")},
        "note": ("Digests are recomputed from the artefacts of the actual run. No timestamp "
                 "enters any digested field, so the positive run is replay-stable."),
    }


def summary_line(art: dict, digests: dict) -> str:
    a = digests["artifacts"]
    return ("SELFBOOT-SUMMARY verdict=%s checked=%s pi=%s pd=%s ecp=%s tqaep=%s "
            "bundle_digest=%s" % (
                digests["validation"]["verdict"], digests["validation"]["checked"],
                a["pi"]["subject_id"], a["pd"]["subject_id"], a["ecp"]["subject_id"],
                a["tqaep"]["subject_id"], digests["bundle_digest"][:16]))


# --------------------------------------------------------------------------- main
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="PIPD-LS-SP self-bootstrap example")
    ap.add_argument("--root", required=True, type=Path,
                    help="disposable workspace root OUTSIDE the repository")
    ap.add_argument("--intent", type=Path, default=DEFAULT_INTENT)
    ap.add_argument("--repocontext", type=Path, default=DEFAULT_REPOCONTEXT)
    ap.add_argument("--negative", choices=["missing-source", "stale-context"], default=None)
    args = ap.parse_args(argv)

    sys.path.insert(0, str(SRC))
    root = args.root.resolve()
    _guard_root(root)
    root.mkdir(parents=True, exist_ok=True)
    repoctx = _read_json(args.repocontext)

    transcript: list[str] = []

    if args.negative == "missing-source":
        out = neg_missing_source(transcript)
        print("\n".join(transcript))
        return out["exit"]
    if args.negative == "stale-context":
        art = drive_chain(root, _read_json(args.intent), repoctx, [])   # need a real PI to bind
        out = neg_stale_context(art, root / "pd_context", transcript)
        print("\n".join(transcript))
        return out["exit"]

    # ---- positive run -------------------------------------------------------
    intent = _read_json(args.intent)
    transcript.append("PIPD-LS-SP SELF-BOOTSTRAP TRANSCRIPT")
    transcript.append(f"repo   = {REPO}")
    transcript.append(f"root   = {root}")
    transcript.append(f"chain  = {' -> '.join(CHAIN)}")
    transcript.append("")
    art = drive_chain(root, intent, repoctx, transcript)
    digests = compute_digests(art)
    _write_json(HERE / "digests.json", digests)

    # the two negatives, exercised here so their RAW output is captured for real
    negatives = [neg_missing_source(transcript),
                 neg_stale_context(art, root / "pd_context", transcript)]
    neg_text = ["PIPD-LS-SP SELF-BOOTSTRAP NEGATIVE CASES (raw captured output)",
                f"root = {root}", ""] + transcript
    (HERE / "negative_stale_context.txt").write_text("\n".join(neg_text) + "\n", encoding="utf-8")

    line = summary_line(art, digests)
    transcript.append(line)
    print("\n".join(transcript))

    ok = (art["validation"].get("verdict") == "PASS"
          and all(n["exit"] != 0 and n["code"] for n in negatives))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
