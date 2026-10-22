"""Q3/M2 re-run driver: one non-prebuilt CLI tool through the real SBL modules.

    python _governance/round-20261022-r15_2/workers/q3_e2e/q3b_stages.py all
    python .../q3b_stages.py pipeline|mutate|repair|regression|cleanup

Scratch root: C:/Users/user/AppData/Local/Temp/q3b (outside every git repo).
The product tree is read-only for this driver; every write lands in the scratch root or in
``workers/q3_e2e/``.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCRATCH = Path(r"C:\Users\user\AppData\Local\Temp\q3b")
SBL = Path(r"C:\Projects\Agent_Workspace\_r152_ev")
Q3 = SBL / "_governance" / "round-20261022-r15_2" / "workers" / "q3_e2e"
LOGS = Q3 / "logs_q3b"

TARGET = SCRATCH / "target"
TESTS = SCRATCH / "tests"
PYTMP = SCRATCH / "pytmp"
STACK = SCRATCH / "stack"

TOOL_REL = "generated/owner_load.py"
TOOL = TARGET / TOOL_REL
HARNESS = TESTS / "test_owner_load.py"
PREMUT = LOGS / "owner_load.pre_mutation.py"

PRODUCT_DIRS = ("sbl_core", "sbl_stack", "sbl_cli", "tests")

HARNESS_TEXT = '''"""Independent harness for the generated owner_load CLI tool.

The tool lives inside the scratch governed repository at ../target/generated/owner_load.py, the only
place the SBL M04 write bridge was allowed to write. This harness sits outside that repository, so a
mutation to the tool cannot reach the test that judges it.
"""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "target" / "generated" / "owner_load.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("owner_load_under_test", TOOL)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_jsonl(path, rows):
    path.write_text("".join(row + "\\n" for row in rows), encoding="utf-8", newline="\\n")


def parse(stdout):
    counts = {}
    for line in stdout.splitlines():
        if not line.strip():
            continue
        owner, _, value = line.partition("\\t")
        counts[owner.strip()] = int(value.strip())
    return counts


def test_counts_open_work_orders_per_owner(tmp_path, capsys):
    tool = load_tool()
    orders = tmp_path / "orders.jsonl"
    write_jsonl(
        orders,
        [
            '{"id": "WO-1", "owner": "alice", "status": "open"}',
            '{"id": "WO-2", "owner": "alice", "status": "open"}',
            '{"id": "WO-3", "owner": "bob", "status": "open"}',
            '{"id": "WO-4", "owner": "bob", "status": "closed"}',
        ],
    )

    assert tool.main([str(orders)]) == 0
    counts = parse(capsys.readouterr().out)

    assert counts == {"alice": 2, "bob": 1}


def test_duplicate_id_newest_file_wins(tmp_path, capsys):
    tool = load_tool()
    older = tmp_path / "older.jsonl"
    newer = tmp_path / "newer.jsonl"
    write_jsonl(older, ['{"id": "WO-1", "owner": "bob", "status": "open"}'])
    write_jsonl(newer, ['{"id": "WO-1", "owner": "alice", "status": "open"}'])
    os.utime(older, (1_000_000, 1_000_000))
    os.utime(newer, (2_000_000, 2_000_000))

    assert tool.main([str(older), str(newer)]) == 0
    counts = parse(capsys.readouterr().out)

    assert counts == {"alice": 1}


def test_malformed_line_is_reported_and_skipped(tmp_path, capsys):
    tool = load_tool()
    orders = tmp_path / "orders.jsonl"
    write_jsonl(
        orders,
        [
            '{"id": "WO-1", "owner": "alice", "status": "open"}',
            '{"id": "WO-2", "owner": "bob", status: open',
        ],
    )

    assert tool.main([str(orders)]) == 0
    captured = capsys.readouterr()

    assert parse(captured.out) == {"alice": 1}
    assert "malformed json line skipped" in captured.err.lower()
'''

SOURCE_LINE = "    for path in sorted(paths, key=os.path.getmtime):"
MUTANT_LINE = "    for path in sorted(paths, key=os.path.getmtime, reverse=True):"


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _rmtree(path: Path) -> None:
    """Removes a tree whose files may be read-only (git objects are, on Windows)."""

    def on_error(func, target, exc_info):  # noqa: ANN001 - shutil callback signature
        try:
            os.chmod(target, stat.S_IWRITE)
            func(target)
        except OSError:
            pass

    if path.exists():
        shutil.rmtree(path, onerror=on_error)
    if path.exists():
        raise SystemExit(f"could not remove {path}")


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def child_env() -> dict[str, str]:
    """Temp inside the scratch root (outside every git repo) and no .pyc writes."""

    env = dict(os.environ)
    env.update(
        {
            "TEMP": str(SCRATCH),
            "TMP": str(SCRATCH),
            "TMPDIR": str(SCRATCH),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    return env


def run(cmd: list[str], cwd: Path, log: str | None = None) -> dict:
    completed = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True, env=child_env(), check=False
    )
    output = (completed.stdout or "") + (completed.stderr or "")
    if log:
        LOGS.mkdir(parents=True, exist_ok=True)
        _write(LOGS / log, output)
    return {
        "cmd": " ".join(cmd),
        "exit_code": completed.returncode,
        "log": log,
        "tail": [line for line in output.splitlines() if line.strip()][-8:],
        "stdout_tail": [line for line in (completed.stdout or "").splitlines() if line.strip()][-12:],
        "output": output,
    }


def run_pytest(label: str) -> dict:
    basetemp = PYTMP / Path(label).stem
    basetemp.mkdir(parents=True, exist_ok=True)
    result = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(basetemp),
            str(HARNESS),
        ],
        cwd=SCRATCH,
        log=label,
    )
    summary = [line for line in result["output"].splitlines() if " passed" in line or " failed" in line]
    failures = [line for line in result["output"].splitlines() if line.startswith("FAILED")]
    return {
        "exit_code": result["exit_code"],
        "log": f"logs_q3b/{label}",
        "passed": result["exit_code"] == 0,
        "summary": summary[-1].strip() if summary else "",
        "failed_tests": failures,
        "first_fail": first_assert(result["output"]),
    }


def first_assert(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("E ") and ("assert" in stripped or "AssertionError" in stripped):
            return stripped[2:].strip()
    return ""


def parse_counts(summary: str) -> dict:
    counts = {}
    for token, key in (("passed", "passed"), ("failed", "failed"), ("error", "errors")):
        for part in summary.replace("=", " ").split(","):
            words = part.split()
            if len(words) >= 2 and words[1].startswith(token):
                try:
                    counts[key] = int(words[0])
                except ValueError:
                    pass
    return counts


def snapshot_product() -> dict:
    files = {}
    for name in PRODUCT_DIRS:
        for path in sorted((SBL / name).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            files[str(path.relative_to(SBL)).replace("\\", "/")] = _sha(path)
    status = subprocess.run(
        ["git", "-C", str(SBL), "status", "--porcelain"], capture_output=True, text=True
    ).stdout
    return {
        "files": files,
        "digest": _sha_bytes(json.dumps(files, sort_keys=True).encode("utf-8")),
        "git_status_digest": _sha_bytes(status.encode("utf-8")),
        "git_status": [line for line in status.splitlines()],
        "head": subprocess.run(
            ["git", "-C", str(SBL), "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip(),
    }


def stage_pipeline() -> dict:
    sys.path.insert(0, str(SBL))
    from sbl_core.dto import WriteSet
    from sbl_core.m01_intake import GoalIntake
    from sbl_core.m02_spec import GuidedSpecification
    from sbl_core.m03_routing import GovernedRouting
    from sbl_core.m04_bridge import GovernedBuildBridge, bind_repo_context
    from sbl_core.m05_verify import EvidenceVerification

    TOOL_TEXT = (Q3 / "owner_load.py.final").read_text(encoding="utf-8")

    _rmtree(TARGET)
    TARGET.mkdir(parents=True)
    _write(TARGET / "README.md", "# scratch governed repository for Q3/M2\n")
    for cmd in (
        ["git", "init", "-q"],
        ["git", "config", "user.email", "q3b@local"],
        ["git", "config", "user.name", "q3b"],
        ["git", "add", "README.md"],
        ["git", "commit", "-q", "-m", "scratch base"],
    ):
        result = run(cmd, cwd=TARGET)
        if result["exit_code"] != 0:
            raise SystemExit(f"scratch repo setup failed: {result['cmd']}: {result['tail']}")

    rows = []
    goal = GoalIntake().intake(
        "read JSONL work orders and print the open ones grouped by owner, newest file wins on duplicate id",
        "bounded e2e task Q3/M2 re-run: one non-prebuilt CLI_TOOL through M01..M06",
        "q3_e2e",
    )
    clauses = [
        {
            "text": "count only work orders whose status is open, grouped by owner",
            "locator": "workers/q3_e2e/_BRIEF_Q3_E2E.md#the-task-to-build",
        },
        {
            "text": "when one id appears in several files the newest file wins",
            "locator": "workers/q3_e2e/_BRIEF_Q3_E2E.md#the-task-to-build",
        },
        {
            "text": "a malformed JSONL line is reported and skipped, not fatal",
            "locator": "workers/q3_e2e/_BRIEF_Q3_E2E.md#the-task-to-build",
        },
        {
            "text": "the generated tool is written only inside the declared writeset",
            "locator": "workers/q3_e2e/_BRIEF_Q3_E2E.md#the-task-to-build",
        },
    ]
    atoms = GuidedSpecification().derive(goal, clauses)
    if len(atoms) < 4:
        raise SystemExit(f"spec derived {len(atoms)} atoms, need >= 4")
    rows.append(
        {
            "module": "SBLM01",
            "entry_point": "GoalIntake.intake",
            "input": "<plain-language request>",
            "output": goal.goal_id,
            "decision": "goal accepted",
            "code_ref": "sbl_core/m01_intake.py:GoalIntake.intake",
        }
    )
    rows.append(
        {
            "module": "SBLM02",
            "entry_point": "GuidedSpecification.derive",
            "input": goal.goal_id,
            "output": [atom.atom_id for atom in atoms],
            "decision": f"{len(atoms)} source-bound atoms derived",
            "code_ref": "sbl_core/m02_spec.py:GuidedSpecification.derive",
        }
    )

    decision = GovernedRouting().route(atoms[0], "CLI_TOOL")
    if not decision.permitted or decision.target != "SBLM04_GOVERNED_BUILD_BRIDGE":
        raise SystemExit(f"routing refused CLI_TOOL: {decision.to_dict()}")
    rows.append(
        {
            "module": "SBLM03",
            "entry_point": "GovernedRouting.route",
            "input": atoms[0].atom_id,
            "kind": "CLI_TOOL",
            "output": decision.target,
            "decision": f"permitted={decision.permitted} ({decision.reason})",
            "code_ref": "sbl_core/m03_routing.py:GovernedRouting.route",
        }
    )

    ctx = bind_repo_context(str(TARGET))
    bridge = GovernedBuildBridge()
    order = bridge.prepare(ctx, WriteSet(("generated",)))
    applied = bridge.apply(order, TOOL_REL, TOOL_TEXT)
    if not TOOL.is_file():
        raise SystemExit("M04 reported an apply but no file landed")
    rows.append(
        {
            "module": "SBLM04",
            "entry_point": "GovernedBuildBridge.prepare/apply",
            "input": ctx.head,
            "output": applied.order_id,
            "writeset_passed": ["generated"],
            "written_path": TOOL_REL,
            "decision": (
                f"wrote {TOOL_REL} inside writeset {list(applied.writeset.paths)} "
                f"({len(TOOL_TEXT)} bytes, sha256 {_sha_bytes(TOOL_TEXT.encode('utf-8'))[:16]}...)"
            ),
            "code_ref": "sbl_core/m04_bridge.py:GovernedBuildBridge.prepare/apply",
            "honest_note": (
                "M04 governs WHERE the bytes land (repo context, HEAD, writeset, lexical and real "
                "path containment). The bytes themselves are authored by the bounded writer: this "
                "tree has no product code-generation module, so they are not presented as generated code."
            ),
        }
    )

    refusals = {}
    for label, path in (("outside_writeset", "elsewhere/owner_load.py"), ("traversal", "../escape.py")):
        try:
            bridge.apply(order, path, "x\n")
        except Exception as exc:  # SBLError expected
            refusals[label] = getattr(exc, "code", type(exc).__name__)
        else:
            refusals[label] = "NOT_REFUSED"
    if any(value == "NOT_REFUSED" for value in refusals.values()):
        raise SystemExit(f"writeset containment not enforced: {refusals}")

    _write(HARNESS, HARNESS_TEXT)
    baseline = run_pytest("01_baseline_pytest.txt")

    verifier = EvidenceVerification()
    verifier.record(
        "Q3B-BASELINE",
        f"{sys.executable} -m pytest -q -p no:cacheprovider {HARNESS}",
        baseline["exit_code"],
        (LOGS / "01_baseline_pytest.txt").read_text(encoding="utf-8"),
        3,
    )
    verdict = verifier.verdict(
        "Q3B-BASELINE",
        "q3_e2e_bounded_writer",
        "pytest:test_owner_load.py",
        "PASS" if baseline["passed"] else "FAIL",
        "LOCAL",
        "LOCAL",
    )
    rows.append(
        {
            "module": "SBLM05",
            "entry_point": "EvidenceVerification.record/verdict",
            "input": "Q3B-BASELINE",
            "output": verdict.status,
            "decision": f"verdict {verdict.status} at claim level {verdict.claim_level} (denominator 3, exit {baseline['exit_code']})",
            "code_ref": "sbl_core/m05_verify.py:EvidenceVerification.record/verdict",
        }
    )

    trace = {
        "schema": "Q3-PIPELINE-TRACE/2",
        "run": "re-run q3b, unique brief, nonce-bearing",
        "goal_id": goal.goal_id,
        "atom_count": len(atoms),
        "atom_ids": [atom.atom_id for atom in atoms],
        "kind": "CLI_TOOL",
        "target_repo": str(TARGET),
        "repo_head": ctx.head,
        "writeset": ["generated"],
        "writeset_after_apply": list(applied.writeset.paths),
        "written_path": TOOL_REL,
        "tool_sha256": _sha(TOOL),
        "baseline": baseline,
        "containment_refusals": refusals,
        "rows": rows,
        "claim_ceiling": "one tool on one host through the real modules; local claim only",
    }
    _write(Q3 / "PIPELINE_TRACE.json", json.dumps(trace, indent=2) + "\n")
    LOGS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(TOOL, PREMUT)
    return trace


def stage_mutate() -> dict:
    before = TOOL.read_bytes()
    before_sha = _sha_bytes(before)
    text = before.decode("utf-8")
    if text.count(SOURCE_LINE) != 1:
        raise SystemExit("mutation target line not unique; refusing to invent a mutation")
    after_text = text.replace(SOURCE_LINE, MUTANT_LINE, 1)
    _write(TOOL, after_text)
    diff = "".join(
        difflib.unified_diff(
            text.splitlines(keepends=True),
            after_text.splitlines(keepends=True),
            fromfile="generated/owner_load.py (baseline)",
            tofile="generated/owner_load.py (mutant)",
        )
    )
    _write(Q3 / "MUTATION.diff", diff)
    run_result = run_pytest("02_mutant_pytest.txt")
    result = {
        "replaced_line": SOURCE_LINE.strip(),
        "mutation_line": MUTANT_LINE.strip(),
        "changed_lines": 1,
        "tool_sha256_before": before_sha,
        "tool_sha256_mutant": _sha(TOOL),
        "run": run_result,
        "counts": parse_counts(run_result["summary"]),
        "failing_tests": run_result["failed_tests"],
        "first_fail": run_result["first_fail"],
        "assertion_failure": bool(run_result["first_fail"]) and not run_result["passed"],
    }
    _write(LOGS / "02_mutation.json", json.dumps(result, indent=2) + "\n")
    return result


def stage_repair() -> dict:
    sys.path.insert(0, str(SBL))
    from sbl_core.m06_repair import BoundedRepair

    mutation = json.loads((LOGS / "02_mutation.json").read_text(encoding="utf-8"))
    plan = BoundedRepair().plan(
        mutation["first_fail"], ["logs_q3b/02_mutant_pytest.txt"], attempts=1
    )

    mutant_sha = _sha(TOOL)
    expected = PREMUT.read_bytes()
    # Byte-for-byte restore from the saved pre-mutation copy, not a re-derived edit.
    TOOL.write_bytes(expected)
    restored_sha = _sha(TOOL)
    run_result = run_pytest("03_repaired_pytest.txt")
    result = {
        "plan": plan.to_dict(),
        "restore_method": "copy of the pre-mutation bytes saved before the mutation was applied",
        "sha256_pre_mutation": _sha_bytes(expected),
        "sha256_mutated": mutant_sha,
        "sha256_after_repair": restored_sha,
        "sha256_equal": _sha_bytes(expected) == restored_sha,
        "mutant_differs_from_baseline": mutant_sha != restored_sha,
        "run": run_result,
        "counts": parse_counts(run_result["summary"]),
    }
    _write(LOGS / "03_repair.json", json.dumps(
        {k: v for k, v in result.items() if k != "run"} | {"run": {k: v for k, v in run_result.items() if k != "output"}},
        indent=2) + "\n")
    return result


def stage_regression() -> dict:
    xml_path = LOGS / "04_regression.xml"
    result = run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "tests/test_core_modules.py",
            "tests/test_kind_matrix.py",
            f"--junitxml={xml_path}",
        ],
        cwd=SBL,
        log="04_regression_pytest.txt",
    )
    summary = [line for line in result["output"].splitlines() if " passed" in line or " failed" in line]
    # The brief's command carries ``-q`` while PYTEST_ADDOPTS and pyproject addopts already add
    # ``-p no:cacheprovider`` and ``-q``; double-quiet suppresses the terminal summary line, so the
    # counts are read from the JUnit XML that the same run wrote instead of inferred from prose.
    counts: dict[str, int] = {}
    xml_note = ""
    try:
        root = ET.parse(xml_path).getroot()
        suite = root if root.tag == "testsuite" else root.find("testsuite")
        counts = {key: int(suite.get(key)) for key in ("tests", "failures", "errors", "skipped")}
        xml_note = f"counts read from {xml_path.name}"
    except Exception as exc:  # noqa: BLE001 - a missing report is an outcome, not a crash
        xml_note = f"junit xml unreadable: {type(exc).__name__}"
    payload = {
        "cmd": result["cmd"],
        "cwd": str(SBL),
        "exit_code": result["exit_code"],
        "summary": summary[-1].strip() if summary else "",
        "summary_absent_reason": (
            "none" if summary else "terminal summary suppressed by double -q (PYTEST_ADDOPTS + pyproject addopts + explicit -q)"
        ),
        "counts": counts,
        "counts_source": xml_note,
        "junit_xml": str(xml_path.relative_to(Q3)).replace("\\", "/"),
        "counts_from_summary_line": parse_counts(summary[-1] if summary else ""),
        "failed_tests": [line for line in result["output"].splitlines() if line.startswith("FAILED")],
    }
    _write(LOGS / "04_regression.json", json.dumps(payload, indent=2) + "\n")
    return payload


def stage_cleanup() -> dict:
    uninstall = run(
        [sys.executable, "-m", "sbl_stack.cli", "uninstall", "--root", str(STACK)],
        cwd=SBL,
        log="05_uninstall.txt",
    )
    doctor = run(
        [sys.executable, "-m", "sbl_stack.cli", "doctor", "--root", str(STACK)],
        cwd=SBL,
        log="06_doctor_after_uninstall.txt",
    )
    typed = None
    try:
        payload = json.loads(doctor["output"])
        typed = payload.get("problems") or payload.get("code")
    except Exception:
        typed = None

    generated = TARGET / "generated"
    resolved = generated.resolve()
    if not str(resolved).lower().startswith(str(SCRATCH.resolve()).lower()):
        raise SystemExit(f"refusing to delete outside the scratch root: {resolved}")
    removed = []
    if resolved.is_dir():
        removed = sorted(
            str(p.relative_to(SCRATCH)).replace("\\", "/") for p in resolved.rglob("*") if p.is_file()
        )
        shutil.rmtree(resolved)
    listing = sorted(str(p.relative_to(TARGET)).replace("\\", "/") for p in TARGET.rglob("*"))
    target_listing = sorted(p.name for p in TARGET.iterdir())
    scratch_listing = sorted(p.name for p in SCRATCH.iterdir())
    payload = {
        "uninstall_rc": uninstall["exit_code"],
        "doctor_after_uninstall_rc": doctor["exit_code"],
        "doctor_typed_problem": typed,
        "doctor_refused": doctor["exit_code"] != 0,
        "generated_dir_exists_after": resolved.is_dir(),
        "removed_files": removed,
        "target_root_listing_after": target_listing,
        "target_listing_after": listing,
        "scratch_listing_after": scratch_listing,
    }
    _write(LOGS / "07_cleanup.json", json.dumps(payload, indent=2) + "\n")
    return payload


def stage_snapshot() -> dict:
    """Proves the product tree was untouched: mtime anchor, per-file sha256, HEAD-blob comparison.

    The anchor is the first file this run wrote. Any product ``.py`` with a later mtime was touched
    during the run. Files git already reported dirty before this brief were left dirty by earlier,
    separately authorised briefs, so they are compared byte-for-byte with ``git show HEAD:<path>``
    only to say *which* of them still differ -- never presented as this run's doing.
    """

    anchor = (LOGS / "00_install.txt").stat().st_mtime
    files: dict[str, dict] = {}
    touched = []
    for name in PRODUCT_DIRS:
        for path in sorted((SBL / name).rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            rel = str(path.relative_to(SBL)).replace("\\", "/")
            mtime = path.stat().st_mtime
            files[rel] = {"sha256": _sha(path), "mtime": mtime}
            if mtime >= anchor - 1:
                touched.append(rel)
    digest = _sha_bytes(json.dumps(files, sort_keys=True).encode("utf-8"))
    status = subprocess.run(
        ["git", "-C", str(SBL), "status", "--porcelain"], capture_output=True, text=True
    ).stdout
    dirty = [line for line in status.splitlines()]
    payload = {
        "anchor": "mtime of logs_q3b/00_install.txt (first write of this run)",
        "anchor_epoch": anchor,
        "product_file_count": len(files),
        "product_tree_digest": digest,
        "product_files_touched_since_anchor": touched,
        "git_status": dirty,
        "git_status_digest": _sha_bytes(status.encode("utf-8")),
        "git_status_count": len(dirty),
        "head": subprocess.run(
            ["git", "-C", str(SBL), "rev-parse", "HEAD"], capture_output=True, text=True
        ).stdout.strip(),
        "writes_made_by_this_run": [
            str(SCRATCH),
            str(LOGS),
            "workers/q3_e2e/q3b_stages.py",
            "workers/q3_e2e/Q3_RESULT.json",
            "workers/q3_e2e/PIPELINE_TRACE.json",
            "workers/q3_e2e/MUTATION.diff",
        ],
        "outside_scope_unchanged": not touched,
    }
    _write(LOGS / "08_outside_scope.json", json.dumps(payload, indent=2) + "\n")
    return payload


def main() -> int:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    command = sys.argv[1] if len(sys.argv) > 1 else "all"

    if command in ("install", "all"):
        _rmtree(STACK)
        install = run(
            [sys.executable, "-m", "sbl_stack.cli", "install", "--root", str(STACK)],
            cwd=SBL,
            log="00_install.txt",
        )
        if install["exit_code"] != 0:
            raise SystemExit(f"install failed rc={install['exit_code']}: {install['tail']}")
        _write(LOGS / "00_install.json", json.dumps({"exit_code": install["exit_code"]}, indent=2) + "\n")
        if command == "install":
            return 0

    stages = {
        "pipeline": stage_pipeline,
        "mutate": stage_mutate,
        "repair": stage_repair,
        "regression": stage_regression,
        "cleanup": stage_cleanup,
        "snapshot": stage_snapshot,
    }
    if command == "all":
        before = snapshot_product()
        _write(LOGS / "SNAPSHOT_BEFORE.json", json.dumps(before, indent=2) + "\n")
        trace = stage_pipeline()
        mutation = stage_mutate()
        repair = stage_repair()
        regression = stage_regression()
        cleanup = stage_cleanup()
        after = snapshot_product()
        _write(LOGS / "SNAPSHOT_AFTER.json", json.dumps(after, indent=2) + "\n")
        unchanged = (
            before["digest"] == after["digest"]
            and before["git_status_digest"] == after["git_status_digest"]
        )
        payload = {
            "baseline": trace["baseline"],
            "mutation": {k: v for k, v in mutation.items() if k != "run"},
            "repair": {k: v for k, v in repair.items() if k != "run"},
            "regression": regression,
            "cleanup": cleanup,
            "outside_scope": {
                "product_files_digest_before": before["digest"],
                "product_files_digest_after": after["digest"],
                "file_count": len(before["files"]),
                "git_status_digest_before": before["git_status_digest"],
                "git_status_digest_after": after["git_status_digest"],
                "unchanged": unchanged,
                "head": after["head"],
            },
        }
        _write(LOGS / "RUN_SUMMARY.json", json.dumps(payload, indent=2) + "\n")
        print(json.dumps(payload, indent=2))
        return 0

    if command not in stages:
        raise SystemExit("usage: q3b_stages.py [install|pipeline|mutate|repair|regression|cleanup|all]")
    payload = stages[command]()
    printable = {k: v for k, v in payload.items() if k not in ("rows", "files", "git_status")}
    print(json.dumps(printable, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
