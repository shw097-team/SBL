"""Case runner binding — the missing producer behind the FHS W2 `RUNNER_UNBOUND` stop.

Why this module exists
----------------------
`pre_v2_adapter.planned_tqaep` can *plan* a case, and it deliberately requires
`runner_binding == "RUNNER_UNBOUND"`: a plan must not pretend a runner exists. But nothing in this
repository could ever *bind* a real runner, so every affected native case stayed at
`RUNNER_UNBOUND` and no original RED/GREEN could be produced. Measured across the FHS W0-W2
rounds; this module is that binding side.

What it is
----------
* `build_entry(...)`   — pin one case to real bytes: oracle, runner, POS/NEG fixtures, probe.
* `verify_entry(...)`  — re-derive every digest from disk; drift is a typed refusal.
* `run_entry(...)`     — execute the case and report what actually happened.

Claim ceiling
-------------
A `world_state="GREEN"` here is `AUTHOR_SIDE_EXECUTION`: the declared bytes ran and agreed with
the declared expectation. It is **not** an original-runner receipt, an independent checker
verdict, or a release. `run_entry` therefore always reports the process exit code, the observed
values and the digests it used, so a downstream reader can re-derive the same result instead of
trusting this module's opinion.

Refusals are typed (`CaseRunnerRefusal.code`) and fail closed: a missing file, an unpinned
fixture, a POS/NEG collision or a drifted digest never degrades into a warning.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

SCHEMA = "SBL.CaseRunner.Entry@1"

#: A runner entry is only ever bound when these are present and hashable.
REQUIRED = ("case_id", "original_requirement_id", "original_oracle_id", "clause_id", "fuo_id",
            "parent_neg", "oracle", "runner", "positive_fixture", "negative_fixture",
            "raw_schema", "evidence_expectation", "checker_role", "runner_owner",
            "applicability")

CODES = ("CASE_RUNNER_REQUIRED_FIELD", "CASE_RUNNER_FILE_MISSING", "CASE_RUNNER_POS_NEG_COLLISION",
         "CASE_RUNNER_ORACLE_EMPTY", "CASE_RUNNER_RUNNER_EMPTY", "CASE_RUNNER_ENTRY_DRIFT",
         "CASE_RUNNER_BINDING_STATE", "CASE_RUNNER_APPLICABILITY", "CASE_RUNNER_PROBE_INVALID",
         "CASE_RUNNER_EXEC_FAILED", "CASE_RUNNER_RUNNER_NOT_OWNED")

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class CaseRunnerRefusal(Exception):
    """Typed refusal: the entry cannot be bound, verified or executed as declared."""

    def __init__(self, message: str, *, code: str) -> None:
        super().__init__(message)
        self.code = code

    def as_dict(self) -> dict[str, Any]:
        return {"verdict": "REFUSED", "code": self.code, "message": str(self)}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _need_file(root: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise CaseRunnerRefusal(f"{label} is not a declared path", code="CASE_RUNNER_REQUIRED_FIELD")
    candidate = Path(relative)
    target = candidate if candidate.is_absolute() else (root / candidate)
    if not target.is_file():
        raise CaseRunnerRefusal(f"{label} does not exist: {target}", code="CASE_RUNNER_FILE_MISSING")
    return target


def _canonical(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def build_entry(*, root: str | Path, case_id: str, original_requirement_id: str,
                original_oracle_id: str, clause_id: str, fuo_id: str, parent_neg: str,
                oracle: str, runner: str, positive_fixture: str, negative_fixture: str,
                raw_schema: str, evidence_expectation: str, checker_role: str,
                runner_owner: str, applicability: dict[str, str],
                probe: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pin one case to the exact bytes of its oracle, runner and fixtures.

    `parent_neg` is the parent negative clause this case is allowed to exercise; it is recorded,
    never invented. `applicability` must name host/profile/kind/mode, because a case that does not
    say where it applies cannot be consumed by an original receiver.
    """
    base = Path(root).resolve(strict=True)
    declared = {"case_id": case_id, "original_requirement_id": original_requirement_id,
                "original_oracle_id": original_oracle_id, "clause_id": clause_id,
                "fuo_id": fuo_id, "parent_neg": parent_neg, "raw_schema": raw_schema,
                "evidence_expectation": evidence_expectation, "checker_role": checker_role,
                "runner_owner": runner_owner}
    for field, value in declared.items():
        if not isinstance(value, str) or not value.strip():
            raise CaseRunnerRefusal(f"{field} is empty", code="CASE_RUNNER_REQUIRED_FIELD")
    if not isinstance(applicability, dict):
        raise CaseRunnerRefusal("applicability must be a mapping", code="CASE_RUNNER_APPLICABILITY")
    for axis in ("host", "profile", "kind", "mode"):
        if not isinstance(applicability.get(axis), str) or not applicability[axis].strip():
            raise CaseRunnerRefusal(f"applicability.{axis} is empty",
                                    code="CASE_RUNNER_APPLICABILITY")

    oracle_path = _need_file(base, oracle, "oracle")
    runner_path = _need_file(base, runner, "runner")
    pos_path = _need_file(base, positive_fixture, "positive_fixture")
    neg_path = _need_file(base, negative_fixture, "negative_fixture")

    oracle_sha, runner_sha = _sha(oracle_path), _sha(runner_path)
    pos_sha, neg_sha = _sha(pos_path), _sha(neg_path)
    if not oracle_path.stat().st_size:
        raise CaseRunnerRefusal("oracle bytes are empty", code="CASE_RUNNER_ORACLE_EMPTY")
    if not runner_path.stat().st_size:
        raise CaseRunnerRefusal("runner bytes are empty", code="CASE_RUNNER_RUNNER_EMPTY")
    if pos_sha == neg_sha:
        raise CaseRunnerRefusal(
            "positive and negative fixtures are the same bytes; a case whose counter-example is "
            "its own example proves nothing", code="CASE_RUNNER_POS_NEG_COLLISION")

    if probe is not None:
        if not isinstance(probe, dict) or not probe.get("module") or not probe.get("function"):
            raise CaseRunnerRefusal("probe needs module and function", code="CASE_RUNNER_PROBE_INVALID")
        if "input" not in probe:
            raise CaseRunnerRefusal("probe needs an input", code="CASE_RUNNER_PROBE_INVALID")

    entry: dict[str, Any] = {
        "schema": SCHEMA,
        **declared,
        "applicability": dict(applicability),
        "oracle": {"path": oracle, "sha256": oracle_sha, "bytes": oracle_path.stat().st_size},
        "runner": {"path": runner, "sha256": runner_sha, "bytes": runner_path.stat().st_size,
                   "abi": "SBL.CASE_RUNNER_RUN@1"},
        "positive_fixture": {"path": positive_fixture, "sha256": pos_sha,
                             "bytes": pos_path.stat().st_size},
        "negative_fixture": {"path": negative_fixture, "sha256": neg_sha,
                             "bytes": neg_path.stat().st_size},
        "runner_binding": "RUNNER_BOUND",
        "claim_ceiling": "AUTHOR_SIDE_EXECUTION",
    }
    if probe is not None:
        entry["probe"] = probe
    entry["runner_entry_sha256"] = hashlib.sha256(_canonical(entry)).hexdigest()
    return entry


def verify_entry(entry: dict[str, Any], root: str | Path) -> dict[str, Any]:
    """Re-derive every digest from disk. Drift is refused, never warned about."""
    if not isinstance(entry, dict) or entry.get("schema") != SCHEMA:
        raise CaseRunnerRefusal("entry is not a case runner entry", code="CASE_RUNNER_REQUIRED_FIELD")
    if entry.get("runner_binding") != "RUNNER_BOUND":
        raise CaseRunnerRefusal(
            f"entry claims runner_binding={entry.get('runner_binding')!r}; only a bound entry may run",
            code="CASE_RUNNER_BINDING_STATE")
    body = {k: v for k, v in entry.items() if k != "runner_entry_sha256"}
    expected_entry_sha = hashlib.sha256(_canonical(body)).hexdigest()
    if entry.get("runner_entry_sha256") != expected_entry_sha:
        raise CaseRunnerRefusal("entry bytes do not match its own runner_entry_sha256",
                                code="CASE_RUNNER_ENTRY_DRIFT")

    base = Path(root).resolve(strict=True)
    observed: dict[str, str] = {}
    for field, label in (("oracle", "oracle"), ("runner", "runner"),
                         ("positive_fixture", "positive_fixture"),
                         ("negative_fixture", "negative_fixture")):
        block = entry.get(field)
        if not isinstance(block, dict) or not _HEX64.match(str(block.get("sha256") or "")):
            raise CaseRunnerRefusal(f"{field} carries no pinned sha256",
                                    code="CASE_RUNNER_REQUIRED_FIELD")
        rel = block.get("path")
        if not isinstance(rel, str) or not rel.strip():
            raise CaseRunnerRefusal(f"{field} carries no path", code="CASE_RUNNER_REQUIRED_FIELD")
        target = _need_file(base, rel, label)
        got = _sha(target)
        if got != block["sha256"]:
            raise CaseRunnerRefusal(
                f"{field} drifted: entry pins {block['sha256'][:12]}, disk has {got[:12]}",
                code="CASE_RUNNER_ENTRY_DRIFT")
        observed[field] = got
    return {"verified": True, "digests": observed, "runner_entry_sha256": expected_entry_sha}


def run_entry(entry: dict[str, Any], *, subject_root: str | Path, python: str | None = None,
              timeout: int = 120) -> dict[str, Any]:
    """Execute the bound case by launching its declared runner against `subject_root`.

    The runner is a real file whose bytes are pinned in the entry; it must print one JSON object
    describing what it observed. This function re-verifies every digest first, so a drifted oracle
    or runner cannot be executed as if it were the pinned case. Nothing from the subject is imported
    into this process.
    """
    subject = Path(subject_root).resolve(strict=True)
    verify_entry(entry, subject)
    exe = python or sys.executable
    runner_path = _need_file(subject, entry["runner"]["path"], "runner")

    started = time.time()
    proc = subprocess.run([exe, str(runner_path), str(subject)], cwd=str(subject),
                          capture_output=True, text=True, timeout=timeout, errors="replace",
                          env={**__import__("os").environ, "PYTHONPATH": str(subject),
                               "PYTHONDONTWRITEBYTECODE": "1"})
    elapsed = round(time.time() - started, 3)
    stdout = proc.stdout or ""
    try:
        payload = json.loads(stdout.strip().splitlines()[-1]) if stdout.strip() else {}
    except Exception:
        payload = {}
    if not isinstance(payload, dict) or payload.get("verdict") not in ("GREEN", "RED"):
        raise CaseRunnerRefusal(
            "runner did not emit a typed verdict object (exit %s): %s"
            % (proc.returncode, (proc.stderr or stdout)[-300:]),
            code="CASE_RUNNER_EXEC_FAILED")

    return {
        "schema": "SBL.CaseRunner.WorldRaw@1",
        "case_id": entry["case_id"],
        "original_oracle_id": entry["original_oracle_id"],
        "original_requirement_id": entry["original_requirement_id"],
        "runner_entry_sha256": entry["runner_entry_sha256"],
        "oracle": {"path": entry["oracle"]["path"], "sha256": entry["oracle"]["sha256"]},
        "runner": {"path": entry["runner"]["path"], "sha256": entry["runner"]["sha256"],
                   "abi": entry["runner"]["abi"], "exit": proc.returncode, "elapsed_s": elapsed,
                   "stdout_sha256": hashlib.sha256(stdout.encode()).hexdigest(),
                   "stderr_sha256": hashlib.sha256((proc.stderr or "").encode()).hexdigest(),
                   "stderr_tail": (proc.stderr or "")[-400:]},
        "observed": payload,
        "world_state": payload["verdict"],
        "subject_root": str(subject),
        "claim_ceiling": "AUTHOR_SIDE_EXECUTION",
        "note": ("this reports one process run against pinned bytes; it is not an original-runner "
                 "receipt and not an independent checker verdict"),
    }


def preimage(subject_root: str | Path, paths: list[str]) -> dict[str, str]:
    """Digest the pre-image of the exact write set so a rollback can prove restoration."""
    base = Path(subject_root).resolve(strict=True)
    return {rel: (_sha(base / rel) if (base / rel).is_file() else "ABSENT") for rel in paths}


def restore(subject_root: str | Path, digests: dict[str, str], backup_dir: str | Path) -> dict[str, Any]:
    """Restore files from a caller-supplied backup and prove the bytes came back."""
    base = Path(subject_root).resolve(strict=True)
    backup = Path(backup_dir)
    restored = {}
    for rel, want in digests.items():
        src = backup / rel
        if not src.is_file():
            raise CaseRunnerRefusal(f"backup has no {rel}", code="CASE_RUNNER_FILE_MISSING")
        dst = base / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
        got = _sha(dst)
        restored[rel] = {"expected": want, "observed": got, "restored": got == want}
    return {"restored": restored, "exact": all(v["restored"] for v in restored.values())}


if __name__ == "__main__":  # pragma: no cover - operator probe, not a gate
    if len(sys.argv) < 4:
        print("usage: case_runner.py run <entry.json> <subject_root> | verify <entry.json> <subject_root>")
        raise SystemExit(2)
    mode, entry_path, subject_root = sys.argv[1], sys.argv[2], sys.argv[3]
    payload = json.loads(Path(entry_path).read_text(encoding="utf-8"))
    try:
        if mode == "run":
            print(json.dumps(run_entry(payload, subject_root=subject_root), ensure_ascii=False, indent=1))
        else:
            print(json.dumps(verify_entry(payload, subject_root), ensure_ascii=False, indent=1))
    except CaseRunnerRefusal as exc:
        print(json.dumps(exc.as_dict(), ensure_ascii=False, indent=1))
        raise SystemExit(1)
