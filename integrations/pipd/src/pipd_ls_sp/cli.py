"""`pipd` CLI - exactly the 13 commands of 總藍圖 §5.9.3 (exact-set, no 14th)."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from . import __version__, pipeline, profiles, registry, validate, workspace
from .errors import PipdError

COMMANDS = ("init", "intake", "profile", "compile-pi", "bind-pd", "compile-ecp",
            "compile-tqaep", "validate", "doctor", "project", "export", "diff", "repair")
FAILURE_CODES = {
    "init": "INIT_CONFLICT/PROFILE_STALE",
    "intake": "INTAKE_INVALID/AUTHORITY_UNKNOWN",
    "profile": "PROFILE_VETO/UNSUPPORTED_SURFACE",
    "compile-pi": "PI_SCHEMA/PI_SEMANTIC/TRACE_FAIL",
    "bind-pd": "REPO_CONTEXT_MISSING/STALE_PROVIDER",
    "compile-ecp": "ECP_PERMISSION/EFFECT_UNKNOWN",
    "compile-tqaep": "TQ_TRACE/TQ_ORACLE/TQ_SOD",
    "validate": "VALIDATION_FAIL",
    "doctor": "TOOL_DRIFT/HOST_UNSUPPORTED/COLLISION/RESIDUE/SEMVER",
    "project": "PROJECTION_LOSS/ADAPTER_FAIL/UNSAFE_DESTINATION",
    "export": "EXPORT_HASH/SECRET_SCAN/UNSAFE_DESTINATION",
    "diff": "DIFF_INCOMPATIBLE_SCHEMA",
    "repair": "REPAIR_SCOPE/DEPENDENCY/SELF_ACCEPT",
}


def _emit(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pipd", description=f"PIPD-LS-SP compiler CLI {__version__} (13 commands)")
    p.add_argument("--root", type=Path, default=Path.cwd())
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    s = sub.add_parser("intake"); s.add_argument("--goal", required=True)
    s.add_argument("--source", action="append", default=[])
    s.add_argument("--constraint", action="append", default=[])
    s.add_argument("--non-goal", action="append", default=[])
    s = sub.add_parser("profile"); s.add_argument("--profile", default="LITE")
    s.add_argument("--axis", action="append", default=[])
    s = sub.add_parser("compile-pi"); s.add_argument("--intent", type=Path, required=True)
    s.add_argument("--profile", default="LITE")
    s.add_argument("--explain", action="store_true")
    s.add_argument("--replay", action="store_true")
    s = sub.add_parser("bind-pd"); s.add_argument("--pi", type=Path, required=True)
    s.add_argument("--repo-root", type=Path); s.add_argument("--head", default="")
    s = sub.add_parser("compile-ecp"); s.add_argument("--pd", type=Path, required=True)
    s.add_argument("--pi", type=Path, required=True)
    s.add_argument("--explain", action="store_true")
    s = sub.add_parser("compile-tqaep"); s.add_argument("--pi", type=Path, required=True)
    s.add_argument("--ecp", type=Path, required=True)
    s.add_argument("--maker", default="HERMES-MAKER")
    s.add_argument("--checker", default="GLM-5.3-FLASH-AO-LANE")
    s.add_argument("--checker-receipt", dest="checker_receipt", default="")
    s.add_argument("--explain", action="store_true")
    s = sub.add_parser("validate"); s.add_argument("--bundle", type=Path, required=True)
    s.add_argument("--explain", action="store_true")
    sub.add_parser("doctor")
    s = sub.add_parser("project"); s.add_argument("--out", type=Path, default=None)
    # `--root` is a global option, but accept it after the subcommand too so
    # `pipd project --out ... --root <root>` is not a usage error.
    s.add_argument("--root", dest="sub_root", type=Path, default=None)
    s.add_argument("--dry-run", dest="dry_run", action="store_true")
    s.add_argument("--allow-root", dest="allow_root", type=Path, action="append", default=[])
    s.add_argument("--allow-replace", dest="allow_replace", action="store_true")
    s = sub.add_parser("export"); s.add_argument("--out", type=Path, default=None)
    s.add_argument("--dry-run", dest="dry_run", action="store_true")
    # R5-WO3: `export --out` publishes a portable bundle, so it shares the R5-WO1
    # destination policy: repeatable --allow-root / --allow-replace + the
    # PIPD_PROJECT_ALLOWED_ROOTS environment variable.
    s.add_argument("--root", dest="sub_root", type=Path, default=None)
    s.add_argument("--allow-root", dest="allow_root", type=Path, action="append", default=[])
    s.add_argument("--allow-replace", dest="allow_replace", action="store_true")
    s = sub.add_parser("diff"); s.add_argument("--a", type=Path, required=True)
    s.add_argument("--b", type=Path, required=True)
    s.add_argument("--explain", action="store_true")
    s = sub.add_parser("repair"); s.add_argument("--subject", required=True)
    s.add_argument("--authorized-root", dest="authorized_root", default="")
    s.add_argument("--scope", action="append", default=[])
    s.add_argument("--maker", default="HERMES-MAKER")
    s.add_argument("--dry-run", dest="dry_run", action="store_true")
    return p


def _explain(cmd: str, record: dict, extra: dict | None = None) -> dict:
    """A deterministic, human-readable derivation of a decision.

    Nothing here is model-generated: every line is derived from the record's own fields, so the
    explanation cannot drift from the artefact it explains.
    """
    why: list[str] = [f"command={cmd}", f"subject_id={record.get('subject_id', '?')}",
                      f"schema_version={record.get('schema_version', '?')}",
                      f"content_hash={str(record.get('content_hash', ''))[:16]}"]
    for key in ("profile", "verdict", "checked", "state", "scope", "writable_scope", "allowed_claims"):
        if key in record:
            why.append(f"{key}={json.dumps(record[key], ensure_ascii=False)}")
    if "findings" in record and record["findings"]:
        why.append(f"findings={len(record['findings'])}: "
                   + "; ".join(f.get("detail", "")[:60] for f in record["findings"][:3]))
    if extra:
        why += [f"{k}={json.dumps(v, ensure_ascii=False)[:120]}" for k, v in extra.items()]
    return {"explain": {"command": cmd, "derivation": why,
                        "generated_by": "deterministic field projection (no model consulted)"}}


def run(args: argparse.Namespace) -> dict:
    root: Path = (getattr(args, "sub_root", None) or args.root).resolve()
    cmd = args.command
    if cmd == "init":
        return workspace.init_workspace(root)
    if cmd == "intake":
        return pipeline.intake(args.goal, sources=args.source,
                               constraints=args.constraint, non_goals=args.non_goal)
    if cmd == "profile":
        return profiles.compute_profile(args.profile, axes=args.axis or ["intent"])
    if cmd == "compile-pi":
        card = _read_json(args.intent, "intent card")
        out = pipeline.compile_pi(card, args.profile)
        if getattr(args, "replay", False):
            # replay identity: the same input lock must reproduce the same ids, byte for byte
            again = pipeline.compile_pi(card, args.profile)
            same = (json.dumps(pipeline.strip_sidecar(out), sort_keys=True)
                    == json.dumps(pipeline.strip_sidecar(again), sort_keys=True))
            out = dict(out)
            out["replay"] = {"iterations": 2, "identity_equal": same,
                             "subject_id": out["subject_id"],
                             "replay_verdict": "PASS" if same else "FAIL"}
        if getattr(args, "explain", False):
            out = dict(out); out.update(_explain("compile-pi", out))
        return out
    if cmd == "bind-pd":
        pi = _read_json(args.pi, "PI package")
        ctx = None
        if args.repo_root:
            # R-AUD-009: RepoContext is DERIVED from the repository/host; --head is an unverified
            # caller claim, never an authoritative head and never a self-asserted FRESH currentness.
            ctx = pipeline.repo_probe.derive_repo_context(args.repo_root, writable_scope="src/**")
            if args.head:
                ctx.setdefault("claims", {})["head"] = args.head
        return pipeline.bind_pd(pi, ctx)
    if cmd == "compile-ecp":
        out = pipeline.compile_ecp(_read_json(args.pd, "PD package"),
                                   _read_json(args.pi, "PI package"))
        if getattr(args, "explain", False):
            out = dict(out); out.update(_explain("compile-ecp", out,
                                                 {"idempotency": out.get("idempotency", {})}))
        return out
    if cmd == "compile-tqaep":
        out = pipeline.compile_tqaep(_read_json(args.pi, "PI package"),
                                     _read_json(args.ecp, "ECP"),
                                     maker=args.maker, checker=args.checker,
                                     checker_execution_receipt=args.checker_receipt)
        if getattr(args, "explain", False):
            out = dict(out); out.update(_explain("compile-tqaep", out,
                                                 {"sod": (out.get("acceptance") or [{}])[0]}))
        return out
    if cmd == "validate":
        bundle = _read_json(args.bundle, "validation bundle")
        # CE-1: resolve schemas through the SAME registry chain `doctor` uses
        # (OVERRIDE -> INSTALLED -> SOURCE), with a workspace-local `<root>/schemas`
        # winning only when it actually contains registry.json. The chosen surface is
        # reported so the operator can see which copy produced the verdict.
        schemas_dir, mode, tried = registry.resolve_for_validate(root)
        out = validate.validate_bundle(bundle, schemas_dir)
        out["schema_source"] = {"mode": mode,
                                "path": str(schemas_dir) if schemas_dir is not None else "",
                                "tried": tried}
        if schemas_dir is None:
            out["verdict"] = "FAIL"
            out.setdefault("findings", []).append(
                {"contract": "*", "kind": "SCHEMA_RESOLUTION",
                 "detail": "no schemas directory containing registry.json; tried: "
                           + "; ".join(tried)})
        if getattr(args, "explain", False):
            out = dict(out); out.update(_explain("validate", out))
        return out
    if cmd == "doctor":
        return workspace.doctor(root)
    if cmd == "project":
        from .projection import resolve_output_destination
        out_omitted = args.out is None
        target = args.out if not out_omitted else (root / "dist" / "web")
        authorized = list(getattr(args, "allow_root", []) or [])
        env_roots = os.environ.get("PIPD_PROJECT_ALLOWED_ROOTS", "")
        if env_roots:
            authorized += [Path(p) for p in env_roots.split(os.pathsep) if p.strip()]
        # The built-in generated surface is always authorized.
        authorized.append(root / "dist")
        allow_replace = True if (out_omitted or getattr(args, "allow_replace", False)) else None
        planned = ["PIPD_BOOTSTRAP.md", "PIPD_CANONICAL_CORE.md", "PIPD_ROUTER_PROFILES.md",
                   "PIPD_ARTIFACT_SCHEMAS.md", "PIPD_EVAL_HANDOFF.md", "PROJECTION_IR.json",
                   "host_generic-skills/SKILL.md", "host_hgk-receiver/receiver-map.json",
                   "host_genie-adapter/object-crosswalk.json",
                   ".pipd-generated-surface.json"]
        if getattr(args, "dry_run", False):
            # Run the SAME resolver (typed refusal on a dangerous target); a safe
            # dry-run reports the plan and writes nothing anywhere.
            resolved = resolve_output_destination(root, target, authorized_roots=authorized,
                                                  allow_replace=allow_replace)
            return {"verdict": "PASS", "dry_run": True, "would_write": planned,
                    "target": str(resolved), "wrote_nothing": True,
                    "destination_safety": {"safe": True, "code": None,
                                           "resolved": str(resolved), "reason": ""},
                    "explain": {"derivation": ["dry-run: the target tree was not touched"]}}
        return workspace.project_surfaces(root, target, authorized_roots=authorized,
                                          allow_replace=allow_replace)
    if cmd == "export":
        # R5-WO3 (REQ-PIPD-R5-EXPORT-003): `export` is a PORTABLE EXPORT. With
        # --out it writes <name>.tar.gz + export_manifest.json + SHA256SUMS to the
        # resolved destination; without --out it keeps the read-only in-memory
        # manifest projection and says so. The destination is resolved with the
        # EXISTING R5-WO1 resolver before any create/delete.
        out_given = args.out is not None
        if not out_given:
            man = workspace.export_manifest(root)
            man["mode"] = "READ_ONLY_MANIFEST"
            man["wrote_nothing"] = True
            man["dry_run"] = bool(getattr(args, "dry_run", False)) or None
            man["note"] = ("no --out given: nothing was written; this is the "
                           "read-only manifest projection (pass --out <dir> "
                           "--allow-root <dir> for a portable bundle)")
            return man

        from .export_bundle import plan as _export_plan
        from .export_bundle import write_bundle
        from .projection import resolve_output_destination

        authorized = list(getattr(args, "allow_root", []) or [])
        env_roots = os.environ.get("PIPD_PROJECT_ALLOWED_ROOTS", "")
        if env_roots:
            authorized += [Path(p) for p in env_roots.split(os.pathsep) if p.strip()]
        # The built-in default export root is <root>/dist.
        authorized.append(root / "dist")
        allow_replace = True if getattr(args, "allow_replace", False) else None

        # Resolve BEFORE any create/delete: a refusal is the same typed
        # UNSAFE_DESTINATION envelope the R5-WO1 `project` branch emits.
        target = resolve_output_destination(root, args.out, authorized_roots=authorized,
                                            allow_replace=allow_replace)

        if getattr(args, "dry_run", False):
            p = _export_plan(root)
            archive_name = f"{(target.name or 'export')}.tar.gz"
            return {"verdict": "PASS", "dry_run": True, "mode": "DRY_RUN",
                    "target": str(target), "file_count": p["file_count"],
                    "manifest_sha256": p["manifest_sha256"],
                    "would_write": sorted([archive_name, "export_manifest.json", "SHA256SUMS"]),
                    "wrote_nothing": True,
                    "destination_safety": {"safe": True, "code": None,
                                           "resolved": str(target), "reason": ""}}

        return write_bundle(root, target, authorized_roots=authorized,
                            allow_replace=allow_replace)
    if cmd == "diff":
        out = workspace.semantic_diff(_read_json(args.a, "artefact A"),
                                      _read_json(args.b, "artefact B"))
        if getattr(args, "explain", False):
            out = dict(out); out.update(_explain("diff", out))
        return out
    if cmd == "repair":
        cand = workspace.repair_candidate(args.subject, scope=args.scope, maker=args.maker,
                                          authorized_root=args.authorized_root or str(root))
        if getattr(args, "dry_run", False):
            return {"verdict": "PASS", "dry_run": True, "candidate": cand, "wrote_nothing": True,
                    "explain": {"derivation": ["dry-run: the scope was validated but nothing was written"]}}
        return cand
    raise AssertionError(cmd)


def _tracked_file_count(root: Path) -> int:
    """Count VCS-tracked files, or files in the tree when it is not a checkout.

    This used to be `sum(1 for _ in root.rglob("*") if _.is_file())`, which counted every object
    inside `.git/` - hundreds of internals that change on every repack - under a field literally
    named `tracked_files`. An independent checker caught the drift. Never count version-control
    internals as project files. The probe now lives in repo_context (R-AUD-009 derives the whole
    RepoContext there); this wrapper keeps the authoritative definition's exact behavior.
    """
    from . import repo_context
    return repo_context.tracked_file_count(root)


def _read_json(p: Path, what: str) -> dict:
    """Read a JSON input with TYPED failures.

    Before this, a missing or malformed input path escaped as FileNotFoundError /
    JSONDecodeError. `main()` only caught PipdError, so the CLI printed a traceback and exited 1 -
    an UNTYPED crash that a caller cannot branch on. A typed refusal is the whole contract of this
    surface, so I/O and parse failures are typed here.
    """
    from .errors import InputShapeInvalid, IoNotFound, ParseInvalid
    try:
        text = Path(p).read_text(encoding="utf-8")
    except OSError as exc:
        raise IoNotFound(f"cannot read {what} at {p}: {exc.strerror or type(exc).__name__}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ParseInvalid(f"{what} at {p} is not valid JSON: {exc.msg} at line {exc.lineno}") from exc
    if not isinstance(data, dict):
        raise InputShapeInvalid(f"{what} at {p} must be a JSON object, got {type(data).__name__}")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        # argparse exits 2 with a usage line on stderr and NOTHING on stdout. Publish the same
        # machine-readable envelope the domain refusals use, so every non-zero exit is branchable.
        if exc.code not in (0, None):
            _emit({"verdict": "FAIL", "code": "USAGE_INVALID",
                   "message": "invalid command line; see --help for the 13 commands"})
            return 2
        raise
    try:
        result = run(args)
    except PipdError as exc:
        _emit(exc.as_dict())
        return 2
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        # Last-resort type completeness: an unexpected input shape becomes a typed envelope instead
        # of a traceback. The class name is preserved so the cause is still identifiable.
        from .errors import InputShapeInvalid
        _emit(InputShapeInvalid(f"{type(exc).__name__}: {str(exc)[:200]}").as_dict())
        return 2
    _emit(result)
    return 0 if result.get("verdict", "PASS") != "FAIL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
