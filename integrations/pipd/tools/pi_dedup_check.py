#!/usr/bin/env python3
"""Measure the PI source-clause de-duplication honestly, raw-first (R4 / W5, repaired by W9).

The pre-dedupe PI embedded every atom's clause TWICE inside `source_clause`: `text` (the derived
statement) plus a byte-identical `source_text` copy, and it repeated the whole source clause payload
on every atom bound to the same clause. The de-duplication moves each distinct clause into a single
`sources[]` table entry and leaves each atom a stable `source_ref` hash pointer.

Honesty note (W9): removing `source_text` did NOT eliminate all clause duplication. Many atoms keep
a locator `text` that is byte-identical to the source-table entry's `text`; those residual clause
bytes are reported separately (`residual_duplicate_atoms` / `residual_duplicated_bytes`) and are
never counted as eliminated. `duplication_eliminated` covers only the `source_text` copies that were
actually dropped. The size effect is reported as a signed delta, including when the current tree is
LARGER than the pre-change shape (payload growth, not economy).

Modes:
  --before   measure the raw (pre-dedupe) PI shape: duplicated atoms/bytes + payload bytes
  --after    measure the CURRENT tree and write PERF_AFTER.json (both measurements side by side)
  --check    re-derive the invariants (including no baseline atom lost); non-zero on any violation
"""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline as P, requirements as R  # noqa: E402

RAW = ROOT / ".hgk" / "rounds" / "R4-20261009-focused-repair" / "W5" / "raw"
PERF_BEFORE = RAW / "PERF_BEFORE.json"
PERF_AFTER = RAW / "PERF_AFTER.json"
GOAL = "de-duplication sample goal: implement the PIPD lifecycle compiler"

# The two PI source files whose HEAD revision is the honest "before" baseline.
HEAD_BASELINE_FILES = ("src/pipd_ls_sp/pipeline.py", "src/pipd_ls_sp/requirements.py")

# Compiled in the extracted HEAD tree; prints the pre-dedupe PI payload size.
_HEAD_MEASURE_SNIPPET = (
    "import json,sys,glob\n"
    "sys.path.insert(0,'src')\n"
    "from pipd_ls_sp import pipeline as P, requirements as R\n"
    "GOAL='de-duplication sample goal: implement the PIPD lifecycle compiler'\n"
    "sources=sorted(glob.glob('fixtures/*/source*.txt'))\n"
    "pi=P.compile_pi(P.intake(GOAL,sources=sources),'LITE')\n"
    "print(json.dumps({'pi_payload_bytes': len(json.dumps(pi,ensure_ascii=False).encode()),"
    "'atoms': len(pi['stable_semantic_contract']['atoms'])}))\n"
)


def sample_sources() -> list[str]:
    """The PIPD clause corpus under fixtures/** (every `source*.txt`)."""
    return sorted(str(p) for p in (ROOT / "fixtures").glob("*/source*.txt"))


def _raw_atoms() -> list[dict[str, Any]]:
    return R.compile_requirements(GOAL, sample_sources())


def _payload_bytes(obj: Any) -> int:
    return len(json.dumps(obj, ensure_ascii=False).encode())


def compile_after_pi() -> dict[str, Any]:
    """The CURRENT tree's PI: sources[] table + per-atom source_ref, no embedded source_text."""
    card = P.intake(GOAL, sources=sample_sources())
    return P.compile_pi(card, "LITE")


def _source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _extract_archive_members(tf: "tarfile.TarFile", dest: Path) -> None:
    """Materialise archive members one at a time, refusing anything that could escape ``dest``.

    ``git archive HEAD`` cannot itself emit ``..``, so this is defence in depth rather than a fix
    for a live attack: relative paths only, no absolute or drive prefix, and regular
    files/directories only - never a symlink, hardlink, device or FIFO. ``extractall`` is
    deliberately NOT used; every member is written by hand so no member-selection behaviour of the
    stdlib can widen the surface.
    """
    import shutil as _shutil

    dest = dest.resolve()
    for member in tf.getmembers():
        name = member.name.replace("\\", "/")
        parts = [q for q in name.split("/") if q not in ("", ".")]
        if (not parts or any(q == ".." for q in parts) or name.startswith("/")
                or (len(name) > 1 and name[1] == ":")):
            raise tarfile.TarError(f"unsafe member path refused: {member.name!r}")
        if not (member.isfile() or member.isdir()):
            raise tarfile.TarError(
                f"non-file member refused: {member.name!r} (type {member.type!r})")
        target = dest / Path(*parts)
        if target != dest and dest not in target.parents:
            raise tarfile.TarError(f"member escapes the destination: {member.name!r}")
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        source = tf.extractfile(member)
        if source is None:
            raise tarfile.TarError(f"member has no readable payload: {member.name!r}")
        with source, open(target, "wb") as out:
            _shutil.copyfileobj(source, out)


def head_baseline() -> dict[str, Any] | None:
    """Materialise the REAL ``HEAD`` sources and measure the pre-change PI payload there.

    Returns ``None`` (never a fabricated shrinkage) whenever git or the HEAD objects are
    unavailable - the caller then declares the baseline SYNTHETIC_FROM_CURRENT. On success the
    result carries ``baseline_source == "HEAD"`` and the sha256 of the two files actually compiled.
    """
    tmp = tempfile.mkdtemp(prefix="pi_dedup_head_")
    dest = Path(tmp)
    try:
        try:
            proc = subprocess.run(
                ["git", "-C", str(ROOT), "archive", "HEAD"],
                capture_output=True,
            )
        except (FileNotFoundError, OSError):
            return None
        if proc.returncode != 0 or not proc.stdout:
            return None
        try:
            with tarfile.open(fileobj=__import__("io").BytesIO(proc.stdout)) as tf:
                _extract_archive_members(tf, dest)
        except (tarfile.TarError, OSError):
            return None
        missing = [f for f in HEAD_BASELINE_FILES if not (dest / f).exists()]
        if missing:
            return None
        run = subprocess.run([sys.executable, "-c", _HEAD_MEASURE_SNIPPET],
                             cwd=str(dest), capture_output=True, text=True)
        if run.returncode != 0:
            return None
        line = next((ln for ln in reversed(run.stdout.splitlines()) if ln.strip().startswith("{")),
                    None)
        if line is None:
            return None
        measured = json.loads(line)
        return {
            "baseline_source": "HEAD",
            "head_sha256": {f: _source_sha256(dest / f) for f in HEAD_BASELINE_FILES},
            "pi_payload_bytes": measured["pi_payload_bytes"],
            "atoms": measured["atoms"],
        }
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


def baseline_info() -> dict[str, Any]:
    """The honest size baseline: real HEAD when available, else SYNTHETIC_FROM_CURRENT.

    The synthetic path never claims shrinkage (``shrinkage_claimed == False``) and keeps the
    honest ``current_tree_larger`` field computed from the current tree's resolved view.
    """
    head = head_baseline()
    current_before = measure_before()
    resolved = materialized_bytes()
    if head is not None:
        baseline_bytes = head["pi_payload_bytes"]
        return {
            "baseline_source": "HEAD",
            "baseline_bytes": baseline_bytes,
            "head_sha256": head["head_sha256"],
            "shrinkage_claimed": resolved < baseline_bytes,
            "current_tree_larger": resolved > baseline_bytes,
            "serialized_delta_bytes": measure_after()["pi_payload_bytes"] - baseline_bytes,
            "resolved_delta_bytes": resolved - baseline_bytes,
        }
    return {
        "baseline_source": "SYNTHETIC_FROM_CURRENT",
        "baseline_bytes": current_before["pi_payload_bytes"],
        "head_sha256": {},
        "shrinkage_claimed": False,
        "current_tree_larger": resolved > current_before["pi_payload_bytes"],
        "serialized_delta_bytes": measure_after()["pi_payload_bytes"] - current_before["pi_payload_bytes"],
        "resolved_delta_bytes": resolved - current_before["pi_payload_bytes"],
    }


def measure_before() -> dict[str, Any]:
    """Reconstruct the pre-dedupe PI: re-inject source_text/source_sha256 onto every atom."""
    pi = copy.deepcopy(compile_after_pi())
    raw = _raw_atoms()
    by_key = {(a["source_clause"]["file"], a["source_clause"]["clause_id"]): a["source_clause"]
              for a in raw}
    dup_atoms = 0
    dup_bytes = 0
    atoms = pi["stable_semantic_contract"]["atoms"]
    for a in atoms:
        sc = a["source_clause"]
        src = by_key.get((sc.get("file"), sc.get("clause_id")))
        if src is None:
            continue
        if src.get("source_text") == sc.get("text"):
            dup_atoms += 1
            dup_bytes += len(src.get("source_text", "").encode())
        sc["source_text"] = src.get("source_text", "")
        sc["source_sha256"] = src.get("source_sha256", "")
    pi["stable_semantic_contract"]["sources"] = []  # pre-dedupe had no shared table
    return {"atoms": len(atoms), "distinct_clauses": len({(s["source_clause"]["file"], s["source_clause"]["clause_id"]) for s in raw}),
            "duplicate_atoms": dup_atoms, "duplicated_bytes": dup_bytes,
            "pi_payload_bytes": _payload_bytes(pi)}


def measure_after(pi: dict[str, Any] | None = None) -> dict[str, Any]:
    """The de-duplicated PI: one sources[] entry per distinct clause, source_ref on every atom."""
    pi = pi if pi is not None else compile_after_pi()
    ssc = pi["stable_semantic_contract"]
    atoms = ssc["atoms"]
    sources = ssc["sources"]
    raw = _raw_atoms()
    distinct = len({(a["source_clause"]["file"], a["source_clause"]["clause_id"]) for a in raw})
    dup_atoms = sum(1 for a in atoms
                    if a["source_clause"].get("source_text") == a["source_clause"].get("text"))
    dup_bytes = sum(len(a["source_clause"].get("source_text", "").encode()) for a in atoms
                    if a["source_clause"].get("source_text") == a["source_clause"].get("text"))
    residual = residual_duplication(pi)
    return {"atoms": len(atoms), "distinct_clauses": distinct, "source_entries": len(sources),
            "atoms_with_source_ref": sum(1 for a in atoms if a["source_clause"].get("source_ref")),
            "duplicate_atoms": dup_atoms, "duplicated_bytes": dup_bytes,
            "residual_duplicate_atoms": residual["residual_duplicate_atoms"],
            "residual_duplicated_bytes": residual["residual_duplicated_bytes"],
            "pi_payload_bytes": _payload_bytes(pi),
            "resolved_materialized_bytes": materialized_bytes(pi)}


def residual_duplication(pi: dict[str, Any] | None = None) -> dict[str, Any]:
    """Measure duplication on the RESOLVED view, not just `source_text`.

    An atom's stored locator `text` is byte-identical to the text of the source-table entry it
    points at whenever `source_clause.text == sources[source_ref].text`. That is residual
    duplication of clause bytes that still ships on every such atom: the atom did NOT shed its copy
    of the clause, so it must not be reported as eliminated.
    """
    pi = pi if pi is not None else compile_after_pi()
    ssc = pi["stable_semantic_contract"]
    atoms = ssc["atoms"]
    table = {s["source_id"]: s for s in ssc.get("sources", [])}
    atoms_hit: list[str] = []
    bytes_hit = 0
    for a in atoms:
        sc = a["source_clause"]
        entry = table.get(sc.get("source_ref"))
        if entry is None:
            continue
        if sc.get("text") == entry.get("text"):
            atoms_hit.append(a.get("req_id", ""))
            bytes_hit += len((entry.get("text") or "").encode("utf-8"))
    return {"residual_duplicate_atoms": len(atoms_hit),
            "residual_duplicated_bytes": bytes_hit,
            "residual_atom_ids": atoms_hit}


def materialized_bytes(pi: dict[str, Any] | None = None) -> int:
    """Serialized size of the *materialized/resolved* view: every atom re-expanded to its
    pre-change locator shape (source_text + source_sha256 re-injected from the table).

    This is the shape a consumer that resolves each atom actually holds. It is LARGER than the
    de-duplicated serialization because the clause text now also ships as each atom's `text`
    locator; comparing the two is the honest size effect.
    """
    pi = pi if pi is not None else compile_after_pi()
    ssc = pi["stable_semantic_contract"]
    table = {s["source_id"]: s for s in ssc.get("sources", [])}
    resolved = copy.deepcopy(pi)
    for a in resolved["stable_semantic_contract"]["atoms"]:
        sc = a["source_clause"]
        entry = table.get(sc.get("source_ref"))
        if entry is not None:
            sc["source_text"] = entry.get("text", "")
            sc["source_sha256"] = entry.get("sha256", "")
    return _payload_bytes(resolved)


def _pre_dedupe_locator(raw_atom: dict[str, Any]) -> dict[str, Any]:
    return dict(raw_atom["source_clause"])


def baseline_req_ids() -> set[str]:
    """The pre-change shape's requirement-id set: every atom the compiler binds from the corpus."""
    return {a["req_id"] for a in _raw_atoms()}


def evaluate(pi: dict[str, Any] | None = None,
             baseline: set[str] | None = None) -> dict[str, Any]:
    """Re-derive every de-duplication invariant; `first_fail` is "" iff all hold.

    `baseline` is the pre-change requirement-id set. A PI that has *lost an atom* relative to the
    baseline is a semantic regression (de-duplication may re-key, never drop), so any missing
    baseline id is a failure.
    """
    pi = pi if pi is not None else compile_after_pi()
    if baseline is None:
        baseline = baseline_req_ids()
    ssc = pi["stable_semantic_contract"]
    sources = ssc["sources"]
    atoms = ssc["atoms"]
    raw = _raw_atoms()
    distinct = {(a["source_clause"]["file"], a["source_clause"]["clause_id"]) for a in raw}
    fails: list[str] = []
    present = {a.get("req_id") for a in atoms}
    missing = sorted(baseline - present)
    if missing:
        fails.append(f"atoms lost vs baseline: {len(missing)} requirement id(s) absent, "
                     f"e.g. {missing[:3]}")
    if len(sources) != len(distinct):
        fails.append(f"sources[{len(sources)}] != distinct clauses[{len(distinct)}]")
    if len({s["source_id"] for s in sources}) != len(sources):
        fails.append("duplicate source_id in sources[]")
    for a in atoms:
        sc = a["source_clause"]
        if "source_text" in sc:
            fails.append(f"atom {a.get('req_id')} still carries source_text")
        if not sc.get("source_ref"):
            fails.append(f"atom {a.get('req_id')} lacks source_ref")
    # Round-trip: every atom resolves back to its pre-dedupe locator.
    raw_by_req = {a["req_id"]: a for a in raw}
    for atom in atoms:
        raw_atom = raw_by_req.get(atom["req_id"])
        if raw_atom is None:
            continue
        resolved = R.resolve_source_clause(atom, sources)
        want = _pre_dedupe_locator(raw_atom)
        if resolved.get("source_text") != want.get("source_text") or \
                resolved.get("source_sha256") != want.get("source_sha256"):
            fails.append(f"atom {atom.get('req_id')} does not round-trip to its pre-dedupe locator")
    dup = sum(len(a["source_clause"].get("source_text", "").encode()) for a in atoms
              if a["source_clause"].get("source_text") == a["source_clause"].get("text"))
    if dup:
        fails.append(f"duplicated source_text bytes remain: {dup}")
    return {"first_fail": fails[0] if fails else "", "fails": fails}


def _print(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=1))


def cmd_before() -> int:
    before = measure_before()
    existing = None
    if PERF_BEFORE.exists():
        existing = PERF_BEFORE.read_text(encoding="utf-8", errors="replace")
    _print({"mode": "before",
            "perf_before_file": str(PERF_BEFORE),
            "perf_before_file_is_json": bool(existing and existing.lstrip().startswith("{")),
            "perf_before_note": ("existing PERF_BEFORE.json is a prior failed run (crash traceback), "
                                 "so the before numbers are re-measured raw-first here"),
            "measurement": before})
    return 0


def cmd_after() -> int:
    before = measure_before()
    after = measure_after()
    res = evaluate()
    baseline = baseline_info()
    # Honest size effect. Two serializations are reported:
    #   * serialized_delta_bytes  = current de-duplicated serialization vs the pre-change shape
    #     (the table removes the repeated source_text, so this is smaller/negative);
    #   * resolved_delta_bytes    = the atom-resolved view of the CURRENT tree vs the pre-change
    #     shape. Because atoms still carry a `text` locator byte-identical to their table entry,
    #     this is LARGER/positive - the current tree is bigger, not "payload economy".
    serialized_delta = after["pi_payload_bytes"] - before["pi_payload_bytes"]
    resolved_delta = after["resolved_materialized_bytes"] - before["pi_payload_bytes"]
    report = {
        "before": before,
        "after": after,
        "pre_change_pi_bytes": before["pi_payload_bytes"],
        "current_pi_bytes": after["pi_payload_bytes"],
        "current_resolved_materialized_bytes": after["resolved_materialized_bytes"],
        "serialized_delta_bytes": serialized_delta,
        "resolved_delta_bytes": resolved_delta,
        "baseline_source": baseline["baseline_source"],
        "baseline_bytes": baseline["baseline_bytes"],
        "baseline_head_sha256": baseline["head_sha256"],
        "shrinkage_claimed": baseline["shrinkage_claimed"],
        "current_tree_larger": baseline["current_tree_larger"],
        "payload_economy_claimed": serialized_delta < 0 and resolved_delta <= 0,
        # Scoped claim: these are the *source_text* copies actually dropped from atoms. The
        # residual_* fields below are clause bytes that were NOT removed and are never counted here.
        "duplication_eliminated": before["duplicated_bytes"] - after["duplicated_bytes"],
        "residual_duplicate_atoms": after["residual_duplicate_atoms"],
        "residual_duplicated_bytes": after["residual_duplicated_bytes"],
        "first_fail": res["first_fail"] if after["duplicated_bytes"] == 0 else
                      (res["first_fail"] or "duplicated_bytes != 0 after change"),
    }
    RAW.mkdir(parents=True, exist_ok=True)
    PERF_AFTER.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8",
                          newline="")
    _print({"mode": "after", "perf_after_file": str(PERF_AFTER), **report})
    return 0


def cmd_check() -> int:
    res = evaluate()
    before = measure_before()
    after = measure_after()
    baseline = baseline_info()
    serialized_delta = after["pi_payload_bytes"] - before["pi_payload_bytes"]
    resolved_delta = after["resolved_materialized_bytes"] - before["pi_payload_bytes"]
    report = {"mode": "check", "first_fail": res["first_fail"], "fails": res["fails"],
              "residual_duplicate_atoms": after["residual_duplicate_atoms"],
              "residual_duplicated_bytes": after["residual_duplicated_bytes"],
              "baseline_source": baseline["baseline_source"],
              "baseline_bytes": baseline["baseline_bytes"],
              "baseline_head_sha256": baseline["head_sha256"],
              "shrinkage_claimed": baseline["shrinkage_claimed"],
              "pre_change_pi_bytes": before["pi_payload_bytes"],
              "current_pi_bytes": after["pi_payload_bytes"],
              "current_resolved_materialized_bytes": after["resolved_materialized_bytes"],
              "serialized_delta_bytes": serialized_delta,
              "resolved_delta_bytes": resolved_delta,
              "current_tree_larger": baseline["current_tree_larger"],
              "verdict": "FAIL" if res["first_fail"] else "PASS"}
    _print(report)
    return 0 if not res["first_fail"] else 1


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = next((a for a in argv if a in ("--before", "--after", "--check")), None)
    if mode is None:
        print("usage: pi_dedup_check.py --before|--after|--check", file=sys.stderr)
        return 2
    return {"--before": cmd_before, "--after": cmd_after, "--check": cmd_check}[mode]()


if __name__ == "__main__":
    raise SystemExit(main())
