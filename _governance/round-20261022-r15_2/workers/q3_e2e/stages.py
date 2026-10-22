"""Q3 / M2 driver: one non-prebuilt CLI tool through the real SBL modules.

Stages, run in order with the repository root as the working directory:

    python _governance/round-20261022-r15_2/workers/q3_e2e/stages.py pipeline
    python _governance/round-20261022-r15_2/workers/q3_e2e/stages.py mutate
    python _governance/round-20261022-r15_2/workers/q3_e2e/stages.py repair

The tool bytes are authored by this bounded writer. No product code-generation module exists in
the tree, so what the pipeline genuinely provides and what it does not is stated per stage in
``PIPELINE_TRACE.json`` rather than implied.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

SCRATCH = Path(r"C:\Users\user\AppData\Local\Temp\q3_e2e")
SBL = Path(r"C:\Projects\Agent_Workspace\_r152_ev")
Q3 = SBL / "_governance" / "round-20261022-r15_2" / "workers" / "q3_e2e"
LOGS = Q3 / "logs"

TARGET = SCRATCH / "target"
TOOL_REL = "generated/owner_load.py"
TOOL = TARGET / TOOL_REL
HARNESS_DIR = SCRATCH / "generated"
HARNESS = HARNESS_DIR / "test_owner_load.py"

TOOL_TEXT = '''"""owner_load - count open work orders per owner across JSONL work-order files.

Usage: python owner_load.py <work-orders.jsonl> [more-work-orders.jsonl ...]

Several files may be given. Work orders are identified by ``id``; when the same id appears more
than once, the entry from the newest file (by modification time, ties broken by argument order)
wins. Only work orders whose status is ``open`` are counted. A malformed line is reported on
stderr and skipped rather than aborting the run.
"""

from __future__ import annotations

import json
import os
import sys

STATUS_OPEN = "open"


def read_orders(path):
    """Returns the well-formed work-order records in one JSONL file."""

    orders = []
    with open(path, "r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    "warning: {}:{}: malformed JSON line skipped ({})".format(
                        path, number, exc.msg
                    ),
                    file=sys.stderr,
                )
                continue
            if not isinstance(record, dict) or "id" not in record:
                print(
                    "warning: {}:{}: record without an id skipped".format(path, number),
                    file=sys.stderr,
                )
                continue
            orders.append(record)
    return orders


def merge_newest_wins(paths):
    """Merges the files by id, keeping the entry from the newest file."""

    merged = {}
    for path in sorted(paths, key=os.path.getmtime):
        for record in read_orders(path):
            merged[str(record["id"])] = record
    return merged


def count_open_by_owner(orders):
    """Counts open work orders per owner."""

    counts = {}
    for record in orders.values():
        if str(record.get("status", "")).strip().lower() != STATUS_OPEN:
            continue
        owner = str(record.get("owner") or "unassigned")
        counts[owner] = counts.get(owner, 0) + 1
    return counts


def main(argv=None):
    paths = [str(item) for item in (sys.argv[1:] if argv is None else argv)]
    if not paths:
        print("usage: owner_load.py <work-orders.jsonl> [more.jsonl ...]", file=sys.stderr)
        return 2
    missing = [path for path in paths if not os.path.isfile(path)]
    if missing:
        print("error: no such file: {}".format(", ".join(missing)), file=sys.stderr)
        return 2
    counts = count_open_by_owner(merge_newest_wins(paths))
    for owner in sorted(counts):
        print("{}\\t{}".format(owner, counts[owner]))
    if not counts:
        print("no open work orders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

HARNESS_TEXT = '''"""Independent harness for the generated owner_load CLI tool.

The tool lives inside the scratch governed repository at ../target/generated/owner_load.py, which is
the only place the SBL M04 write bridge was allowed to write. This harness deliberately sits outside
that repository, so a mutation to the tool cannot reach the tests that judge it.
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


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_pytest(label: str) -> dict:
    """Runs the three baseline cases and records the raw output."""

    # The inherited TEMP/TMPDIR points at a directory this host cannot enumerate
    # (``pytest-of-user`` raises WinError 5), so pytest's own basetemp resolution fails before any
    # test runs. Pin both the temp root and the basetemp explicitly instead of inheriting them.
    basetemp = SCRATCH / "pytest_tmp" / Path(label).stem
    basetemp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env.update(
        {
            "TEMP": str(SCRATCH),
            "TMP": str(SCRATCH),
            "TMPDIR": str(SCRATCH),
            "PYTHONDONTWRITEBYTECODE": "1",
        }
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--basetemp",
            str(basetemp),
            HARNESS.name,
        ],
        cwd=str(HARNESS_DIR),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    output = completed.stdout + completed.stderr
    LOGS.mkdir(parents=True, exist_ok=True)
    _write(LOGS / label, output)
    return {
        "exit_code": completed.returncode,
        "log": str((LOGS / label).relative_to(Q3)).replace("\\", "/"),
        "passed": completed.returncode == 0,
        "tail": [line for line in output.splitlines() if line.strip()][-6:],
    }


def first_fail_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("E ") and "assert " in stripped:
            return stripped[2:].strip()
    for line in text.splitlines():
        if line.startswith(">"):
            return line.strip()
    return ""


def stage_pipeline() -> dict:
    sys.path.insert(0, str(SBL))
    from sbl_core.m01_intake import GoalIntake
    from sbl_core.m02_spec import GuidedSpecification
    from sbl_core.m03_routing import GovernedRouting
    from sbl_core.m04_bridge import GovernedBuildBridge, bind_repo_context
    from sbl_core.m05_verify import EvidenceVerification
    from sbl_core.dto import WriteSet

    rows = []
    goal = GoalIntake().intake(
        "count open work orders per owner from JSONL files, newest file wins on duplicate ids",
        "bounded e2e task Q3/M2: one non-prebuilt CLI_TOOL through M01..M06",
        "q3_e2e",
    )
    atoms = GuidedSpecification().derive(
        goal,
        [
            {
                "text": "count only work orders whose status is open, grouped by owner",
                "locator": "workers/q3_e2e/_BRIEF.md#step-4-baseline-pass",
            },
            {
                "text": "when one id appears in several files the newest file wins",
                "locator": "workers/q3_e2e/_BRIEF.md#the-task",
            },
            {
                "text": "a malformed JSONL line is reported and skipped, not fatal",
                "locator": "workers/q3_e2e/_BRIEF.md#step-4-baseline-pass",
            },
            {
                "text": "the tool is written only inside the declared writeset",
                "locator": "workers/q3_e2e/_BRIEF.md#step-3-drive-the-pipeline",
            },
        ],
    )
    rows.append(
        {
            "module": "SBLM01",
            "input": "<plain-language request>",
            "output": goal.goal_id,
            "decision": "goal accepted",
            "code_ref": "sbl_core/m01_intake.py:GoalIntake.intake",
        }
    )
    rows.append(
        {
            "module": "SBLM02",
            "input": goal.goal_id,
            "output": [atom.atom_id for atom in atoms],
            "decision": "{} source-bound atoms derived".format(len(atoms)),
            "code_ref": "sbl_core/m02_spec.py:GuidedSpecification.derive",
        }
    )

    routing = GovernedRouting()
    decision = routing.route(atoms[0], "CLI_TOOL")
    rows.append(
        {
            "module": "SBLM03",
            "input": atoms[0].atom_id,
            "output": decision.target,
            "decision": "permitted={} ({})".format(decision.permitted, decision.reason),
            "code_ref": "sbl_core/m03_routing.py:GovernedRouting.route",
        }
    )

    ctx = bind_repo_context(str(TARGET))
    bridge = GovernedBuildBridge()
    order = bridge.prepare(ctx, WriteSet(("generated",)))
    applied = bridge.apply(order, TOOL_REL, TOOL_TEXT)
    rows.append(
        {
            "module": "SBLM04",
            "input": ctx.head,
            "output": applied.order_id,
            "decision": "wrote {} inside writeset {} ({} bytes, sha256 {}...)".format(
                TOOL_REL, list(applied.writeset.paths), len(TOOL_TEXT), _sha(TOOL_TEXT)[:16]
            ),
            "code_ref": "sbl_core/m04_bridge.py:GovernedBuildBridge.prepare/apply",
            "honest_note": (
                "M04 governs WHERE the bytes land (repo context, HEAD, writeset, link escape). The "
                "bytes themselves were authored by the bounded writer: this tree has no product "
                "code-generation module, so this is not presented as generated code."
            ),
        }
    )

    _write(HARNESS, HARNESS_TEXT)
    baseline = run_pytest("03_baseline_pytest.txt")

    verifier = EvidenceVerification()
    verifier.record(
        "Q3-BASELINE",
        "python -m pytest -q test_owner_load.py",
        baseline["exit_code"],
        (LOGS / "03_baseline_pytest.txt").read_text(encoding="utf-8"),
        3,
    )
    verdict = verifier.verdict(
        "Q3-BASELINE",
        "q3_e2e_bounded_writer",
        "pytest:test_owner_load.py",
        "PASS" if baseline["passed"] else "FAIL",
        "LOCAL",
        "LOCAL",
    )
    rows.append(
        {
            "module": "SBLM05",
            "input": "Q3-BASELINE",
            "output": verdict.status,
            "decision": "verdict {} at claim level {} (denominator 3, exit {})".format(
                verdict.status, verdict.claim_level, baseline["exit_code"]
            ),
            "code_ref": "sbl_core/m05_verify.py:EvidenceVerification.record/verdict",
        }
    )

    trace = {
        "schema": "Q3-PIPELINE-TRACE/1",
        "goal_id": goal.goal_id,
        "atom_ids": [atom.atom_id for atom in atoms],
        "kind": "CLI_TOOL",
        "target_repo": str(TARGET),
        "repo_head": ctx.head,
        "writeset": list(order.writeset.paths),
        "written_path": TOOL_REL,
        "tool_sha256": _sha(TOOL_TEXT),
        "baseline": baseline,
        "rows": rows,
        "claim_ceiling": "one tool on one host through the real modules; local claim only",
    }
    _write(Q3 / "PIPELINE_TRACE.json", json.dumps(trace, indent=2) + "\n")
    _write(Q3 / "owner_load.py.final", TOOL_TEXT)
    return trace


def stage_mutate() -> dict:
    before = TOOL.read_text(encoding="utf-8")
    if SOURCE_LINE not in before:
        raise SystemExit("mutation target line not found; refusing to invent a mutation")
    after = before.replace(SOURCE_LINE, MUTANT_LINE, 1)
    _write(TOOL, after)
    diff = "".join(
        difflib.unified_diff(
            before.splitlines(keepends=True),
            after.splitlines(keepends=True),
            fromfile="generated/owner_load.py (baseline)",
            tofile="generated/owner_load.py (mutant)",
        )
    )
    _write(Q3 / "MUTATION.diff", diff)
    run = run_pytest("04_mutant_pytest.txt")
    text = (LOGS / "04_mutant_pytest.txt").read_text(encoding="utf-8")
    result = {
        "mutation_line": MUTANT_LINE.strip(),
        "replaced_line": SOURCE_LINE.strip(),
        "changed_lines": 1,
        "run": run,
        "first_fail": first_fail_line(text),
        "failing_tests": [
            line for line in text.splitlines() if line.startswith("FAILED")
        ],
    }
    _write(Q3 / "logs" / "04_mutation.json", json.dumps(result, indent=2) + "\n")
    return result


def stage_repair() -> dict:
    from sbl_core.m06_repair import BoundedRepair

    mutation = json.loads((LOGS / "04_mutation.json").read_text(encoding="utf-8"))
    first_fail = mutation["first_fail"]
    evidence_refs = [
        str((LOGS / "04_mutant_pytest.txt").relative_to(Q3)).replace("\\", "/")
    ]
    plan = BoundedRepair().plan(first_fail, evidence_refs, attempts=1)

    current = TOOL.read_text(encoding="utf-8")
    repaired = current.replace(MUTANT_LINE, SOURCE_LINE, 1)
    if repaired == current:
        raise SystemExit("repair line not present; the mutation is not the one recorded")
    _write(TOOL, repaired)
    run = run_pytest("06_repaired_pytest.txt")
    result = {
        "plan": plan.to_dict(),
        "repair_line": SOURCE_LINE.strip(),
        "run": run,
        "restored_to_baseline_bytes": repaired == (Q3 / "owner_load.py.final").read_text(encoding="utf-8"),
    }
    _write(Q3 / "logs" / "05_repair.json", json.dumps(result, indent=2) + "\n")
    return result


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "pipeline":
        payload = stage_pipeline()
    elif command == "mutate":
        payload = stage_mutate()
    elif command == "repair":
        payload = stage_repair()
    else:
        raise SystemExit("usage: stages.py pipeline|mutate|repair")
    print(json.dumps({k: v for k, v in payload.items() if k != "rows"}, indent=2))
    raise SystemExit(0)
