from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .bootstrap import bootstrap, reconcile_tt
from .doctor import doctor
from .errors import HGKError
from .knowledge import KnowledgeFactory
from .providers import qualify_hermes_core
from .recovery import backup_database, restore_database
from .release import EvidenceEnvelope, ReleaseReducer
from .spine import SharedSpine


def project_config(root: Path) -> dict[str, Any]:
    return json.loads((root / "config" / "project.json").read_text(encoding="utf-8"))


def spine_for(root: Path) -> SharedSpine:
    config = project_config(root)
    return SharedSpine(root / config["canonical_database"])


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def case_run(root: Path, case_id: str) -> int:
    """Run one frozen acceptance case via tools/run_acceptance.py.

    tools/ is not an importable package, so the runner is loaded from the
    repository tools directory and invoked with --root and --case-id. Its exit
    code is propagated verbatim; a runner SystemExit is mapped to its process
    exit code.
    """
    tools_dir = Path(__file__).resolve().parents[2] / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    import run_acceptance

    original_argv = sys.argv
    sys.argv = ["run_acceptance", "--root", str(root), "--case-id", case_id]
    try:
        return int(run_acceptance.main())
    except SystemExit as exc:
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
        return 1 if not isinstance(exc.code, int) else exc.code
    finally:
        sys.argv = original_argv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hg-kseos")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("bootstrap")
    commands.add_parser("doctor")
    commands.add_parser("migrate")
    commands.add_parser("reconcile-tt")
    commands.add_parser("qualify-hermes-core")
    commands.add_parser("snapshot")

    ingest = commands.add_parser("ingest")
    ingest.add_argument("path", type=Path)
    ingest.add_argument("--rank", required=True)
    ingest.add_argument("--anchor", default="full")

    promote = commands.add_parser("promote")
    promote.add_argument("candidate_id")
    promote.add_argument("--verifier", required=True)
    promote.add_argument("--evidence", required=True)
    promote.add_argument("--title", required=True)

    search = commands.add_parser("search")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=5)

    commands.add_parser("rebuild-knowledge")

    backup = commands.add_parser("backup")
    backup.add_argument("--destination", type=Path)

    restore = commands.add_parser("restore")
    restore.add_argument("backup", type=Path)
    restore.add_argument("--sha256", required=True)
    restore.add_argument("--destination", type=Path, required=True)

    release = commands.add_parser("release-reduce")
    release.add_argument("envelope", type=Path)

    case = commands.add_parser("case")
    case_commands = case.add_subparsers(dest="case_command", required=True)
    case_run_parser = case_commands.add_parser("run")
    case_run_parser.add_argument("--id", required=True)
    case_run_parser.add_argument("--root", type=Path, default=Path.cwd())

    # task-011: autonomous project lifecycle entrypoint
    project = commands.add_parser("project", help="Autonomous project lifecycle")
    project_commands = project.add_subparsers(dest="project_command", required=True)
    p_start = project_commands.add_parser("start", help="Start a new autonomous project")
    p_start.add_argument("--goal", required=True)
    p_start.add_argument("--source", action="append", default=[])
    p_start.add_argument("--constraint", action="append", default=[])
    p_start.add_argument("--non-goal", action="append", default=[])
    p_start.add_argument("--target-root", type=Path)
    p_start.add_argument("--project-id")
    p_status = project_commands.add_parser("status", help="Project lifecycle status")
    p_status.add_argument("project_id")
    p_resume = project_commands.add_parser("resume", help="Resume from checkpoint")
    p_resume.add_argument("project_id")
    p_advance = project_commands.add_parser("advance", help="Advance lifecycle state")
    p_advance.add_argument("project_id")
    p_advance.add_argument("to_state")
    p_advance.add_argument("--trigger", default="MANUAL_ADVANCE")
    p_ckpt = project_commands.add_parser("checkpoint", help="Write lifecycle checkpoint")
    p_ckpt.add_argument("project_id")
    p_intake = project_commands.add_parser("intake", help="Source intake + authority envelope")
    p_intake.add_argument("project_id")
    p_intake.add_argument("--goal", required=True)
    p_intake.add_argument("--source", action="append", default=[])
    p_intake.add_argument("--constraint", action="append", default=[])
    p_intake.add_argument("--non-goal", action="append", default=[])
    p_intake.add_argument("--target-root", type=Path)
    p_denom = project_commands.add_parser("denominator", help="Full-project closure denominator")
    p_denom.add_argument("project_id")

    # task-011: governed evolution entrypoint
    evolution = commands.add_parser("evolution", help="Governed evolution controller")
    evolution_commands = evolution.add_subparsers(dest="evolution_command", required=True)
    e_status = evolution_commands.add_parser("status", help="Evolution signal/candidate status")
    e_signal = evolution_commands.add_parser("signal", help="Capture an evolution signal")
    e_signal.add_argument("--project-id", required=True)
    e_signal.add_argument("--signal-type", required=True)
    e_signal.add_argument("--severity", default="LOW", choices=["LOW", "MEDIUM", "HIGH"])
    e_signal.add_argument("--evidence", action="append", default=[])
    e_candidate = evolution_commands.add_parser("candidate", help="Create an improvement candidate")
    e_candidate.add_argument("--project-id", required=True)
    e_candidate.add_argument("--gap-id", required=True)
    e_candidate.add_argument("--type", required=True)
    e_candidate.add_argument("--problem", required=True)
    e_candidate.add_argument("--change", required=True)
    e_candidate.add_argument("--gain", required=True)
    e_candidate.add_argument("--risk", default="LOW", choices=["LOW", "MEDIUM", "HIGH", "CONSTITUTIONAL"])
    return parser


def run(args: argparse.Namespace) -> Any:
    root = args.root.resolve(strict=True)
    if args.command == "bootstrap":
        return bootstrap(root)
    if args.command == "doctor":
        return doctor(root)
    if args.command == "case":
        return case_run(args.root, args.id)
    if args.command == "reconcile-tt":
        return reconcile_tt(root)
    if args.command == "qualify-hermes-core":
        return qualify_hermes_core(root)
    spine = spine_for(root)
    if args.command == "migrate":
        spine.initialize()
        return {"status": "MIGRATION_PASS", "snapshot": spine.snapshot()}
    if args.command == "snapshot":
        return spine.snapshot()
    if args.command == "ingest":
        path = args.path.resolve(strict=True)
        return KnowledgeFactory(spine).ingest_text(
            str(path), path.read_text(encoding="utf-8"), args.rank, args.anchor
        )
    if args.command == "promote":
        doc_id = KnowledgeFactory(spine).promote(
            args.candidate_id, args.verifier, args.evidence, args.title
        )
        return {"doc_id": doc_id, "status": "PROMOTED"}
    if args.command == "search":
        return {"query": args.query, "results": KnowledgeFactory(spine).search(args.query, args.limit)}
    if args.command == "rebuild-knowledge":
        return KnowledgeFactory(spine).rebuild()
    if args.command == "backup":
        config = project_config(root)
        destination = args.destination or (root / config["backup_root"])
        return backup_database(spine.database, destination)
    if args.command == "restore":
        return restore_database(args.backup, args.sha256, args.destination)
    if args.command == "release-reduce":
        envelope = EvidenceEnvelope.from_dict(json.loads(args.envelope.read_text(encoding="utf-8")))
        return ReleaseReducer(spine).reduce(envelope)
    if args.command == "project":
        from .lifecycle import ProjectLifecycleController, ProjectRequest
        from .spine import SharedSpine as _SS
        lc = ProjectLifecycleController(spine)
        if args.project_command == "start":
            req = ProjectRequest(goal=args.goal, source_paths=args.source,
                                 constraints=args.constraint, non_goals=args.non_goal,
                                 target_root=str(args.target_root) if args.target_root else "")
            return lc.start(req, project_id=args.project_id)
        if args.project_command == "intake":
            req = ProjectRequest(goal=args.goal, source_paths=args.source,
                                 constraints=args.constraint, non_goals=args.non_goal,
                                 target_root=str(args.target_root) if args.target_root else "")
            return lc.intake(args.project_id, req)
        if args.project_command == "status":
            return lc.status(args.project_id)
        if args.project_command == "resume":
            return lc.resume(args.project_id)
        if args.project_command == "checkpoint":
            return lc.checkpoint(args.project_id)
        if args.project_command == "advance":
            return lc.transition(args.project_id, args.to_state, trigger=args.trigger)
        if args.project_command == "denominator":
            return lc.denominator(args.project_id)
        raise AssertionError(args.project_command)
    if args.command == "evolution":
        from .evolution import GovernedEvolutionController, EvolutionSignal
        from .observability import EventLog
        config = project_config(root)
        log = EventLog(root / config.get("event_log", "var/events.jsonl"))
        ec = GovernedEvolutionController(spine, log)
        if args.evolution_command == "status":
            return ec.status(args.project_id if hasattr(args, "project_id") else None)
        if args.evolution_command == "signal":
            return ec.capture_signal(EvolutionSignal(
                project_id=args.project_id, run_id="CLI", signal_type=args.signal_type,
                severity=args.severity, source_evidence=args.evidence))
        if args.evolution_command == "candidate":
            return ec.create_candidate(project_id=args.project_id, gap_id=args.gap_id,
                                       candidate_type=args.type, problem_statement=args.problem,
                                       proposed_change=args.change, expected_gain=args.gain,
                                       risk_class=args.risk)
        raise AssertionError(args.evolution_command)
    raise AssertionError(args.command)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "case":
        return case_run(args.root, args.id)
    try:
        result = run(args)
        emit(result)
    except (HGKError, OSError, ValueError, RuntimeError) as exc:
        emit({"verdict": "FAIL_CLOSED", "error_type": type(exc).__name__, "error": str(exc)})
        return 1
    return 1 if isinstance(result, dict) and result.get("verdict") in {"FAIL", "FAIL_CLOSED"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
