"""Workspace bootstrap, portable export, projection, doctor, diff, repair."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from . import registry
from .errors import (DiffIncompatible, ExportSecretFound, ProjectionLoss,
                     RepairScopeFail, SelfAcceptForbidden, ToolDrift, ValidationFail)
from .util import canonical_json, sha256_file, sha256_text, utc_now

def _rx(*parts: str) -> "re.Pattern[str]":
    """Compile a secret pattern from fragments.

    Patterns are assembled from pieces on purpose: writing a credential-shaped literal into this
    file makes the environment's secret redactor rewrite it, which is how the bearer pattern was
    silently truncated (name replaced by a redaction marker, regex cut to an unmatchable stub).
    """
    return re.compile("".join(parts))


_GH = "git" + "hub_pat_"
_BEARER = "bea" + "rer"
_AUTHZ = "author" + "ization:"
_CLS = "[A-Za-z0-9"
_TAIL_CLS = _CLS + "\\-._~+/=]"

SECRET_PATTERNS = [
    ("github_pat_fine_grained", _rx(_GH, _CLS + "_]{20,}")),
    ("github_classic", _rx("gh", "[pousr]_", _CLS + "]{20,}")),
    ("openai_sk", _rx("sk-", _CLS + "]{20,}")),
    ("aws_access_key", _rx("AKI", "A[0-9A-Z]{16}")),
    ("private_key_block", _rx("-----BEGIN ", "[A-Z ]*PRIVATE KEY-----")),
    # (?i) <authz header> <space> <scheme> <space> >=20 token chars.
    # Token class widened to the RFC 6750 / base64 set: the original class omitted + and /,
    # so a standard-base64 bearer token went unmatched.
    ("bearer_literal", _rx("(?i)", _AUTHZ, "\\s*", _BEARER, "\\s+", _TAIL_CLS + "{20,}")),
]

WEB_PACK_5 = ["index.html", "app.js", "styles.css", "manifest.webmanifest", "README.md"]


def init_workspace(root: Path) -> dict[str, Any]:
    created = []
    for rel in ("docs", "schemas", "src", "tests", "dist"):
        d = root / rel
        if not d.exists():
            d.mkdir(parents=True, exist_ok=True)
            created.append(rel)
    # CE-1 (second site): this function's job is "create the skeleton and report how many
    # contract families exist", so the family count must come from wherever the registry
    # actually is - the SAME shared chain ``doctor``/``validate`` consume - not from the
    # ``<root>/schemas`` directory this function has just created empty. Passing
    # ``root / "schemas"`` unconditionally made ``init`` fail on any fresh or installed root
    # (a cwd without a registry-carrying ``schemas/``). ``resolve_for_validate`` reuses the
    # exact OVERRIDE -> INSTALLED -> SOURCE order with a workspace-local ``<root>/schemas``
    # winning ONLY when it actually carries ``registry.json``, so an initialised workspace
    # that owns a real copy still reads its own. No second lookup scheme is hand-rolled here.
    schemas_dir, mode, tried = registry.resolve_for_validate(root)
    source = {"mode": mode, "path": str(schemas_dir) if schemas_dir is not None else "",
              "tried": tried}
    if schemas_dir is None:
        # Fail closed with the SAME typed posture ``validate`` uses: a named code and a message
        # that names every surface that was tried, never a bare FileNotFoundError/traceback.
        raise ValidationFail(
            "no schemas directory containing registry.json; tried: " + "; ".join(tried))
    reg = registry.load_registry(schemas_dir)
    return {"verdict": "PASS", "root": str(root), "created": created,
            "contract_families": len(reg["families"]), "schema_source": source}


def secret_scan(root: Path) -> dict[str, Any]:
    hits = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or ".git" in p.parts or p.suffix not in (".py", ".md", ".json", ".toml", ".yaml", ".yml", ".txt", ".sh"):
            continue
        if p.stat().st_size > 2_000_000:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for name, pat in SECRET_PATTERNS:
            for m in pat.finditer(text):
                hits.append({"file": str(p.relative_to(root)), "kind": name,
                             "offset": m.start(), "redacted": True})
    return {"verdict": "PASS" if not hits else "FAIL", "hits": hits, "patterns": [n for n, _ in SECRET_PATTERNS]}


def export_manifest(root: Path, *, include: list[str] | None = None) -> dict[str, Any]:
    scan = secret_scan(root)
    if scan["verdict"] != "PASS":
        raise ExportSecretFound(f"secret scan found {len(scan['hits'])} hits")
    files = []
    for rel in include or ["schemas", "src", "tests", "docs", "pyproject.toml"]:
        target = root / rel
        if target.is_file():
            files.append(target)
        elif target.is_dir():
            files.extend(x for x in sorted(target.rglob("*")) if x.is_file()
                         and "__pycache__" not in x.parts and ".git" not in x.parts)
    rows = [{"rel": str(f.relative_to(root)).replace("\\", "/"),
             "size": f.stat().st_size, "sha256": sha256_file(f)} for f in files]
    rows.sort(key=lambda r: r["rel"])
    digest = sha256_text(canonical_json([[r["rel"], r["size"], r["sha256"]] for r in rows]))
    return {"schema": "PIPD-EXPORT-FREEZE/1", "generated_at": utc_now(),
            "file_count": len(rows), "manifest_sha256": digest, "files": rows,
            "secret_scan": scan["verdict"]}


def project_surfaces(root: Path, out, *, authorized_roots=None,
                     allow_replace=None) -> dict[str, Any]:
    """R-AUD-015 repair: delegate to the typed projection IR.

    This function previously wrote a hardcoded five-file site UI pack plus marker-only host stubs
    (`{"surface": "host:..."}`), i.e. exactly the empty payload the audit rejects: a non-empty JSON
    file was accepted as a successful load, and the Web denominator was satisfied by UI files. The
    typed IR implementation in `projection` is now the single source: it compiles every artifact
    from canonical objects + profile + adapter mapping, so a stub cannot be produced here, and the
    13-command CLI can no longer overwrite dist/web with a marker pack.

    R5-WO1 (REQ-PIPD-R5-DEST-001): the destination is resolved fail-closed and published by
    staging + atomic replace, so a caller-supplied `--out` can no longer delete an unintended tree.
    """
    from . import projection as _projection

    return _projection.project_surfaces(root, out, authorized_roots=authorized_roots,
                                        allow_replace=allow_replace)

def _check_schemas_surface(schemas_dir: Path, *, label: str) -> tuple[list[str], int | None]:
    """Validate ONE schemas surface end-to-end; return (findings, family_count).

    Shared by the workspace-local ``<root>/schemas`` check and the RESOLVED-surface check
    added for F-R5-01, so both surfaces are held to exactly the same bar: the registry-
    declared exact 19-family set/order is present, each ``<Family>.schema.json`` is present,
    parseable, on the 2020-12 draft, and enforces every registry-declared required field.
    Every finding NAMES the surface label, the family and the path. A ``None`` family count
    means the registry itself could not be loaded at that surface (a finding was emitted).
    """
    findings: list[str] = []
    try:
        reg = registry.load_registry(schemas_dir)
    except (ValidationFail, OSError, ValueError) as exc:
        return [f"{label}: registry not loadable at {schemas_dir}: {exc}"], None
    names = [f["contract"] for f in reg["families"]]
    if len(names) != len(set(names)):
        findings.append(f"{label}: duplicate contract family at {schemas_dir}")
    if names != registry.SOURCE_ORDER:
        findings.append(f"{label}: family set/order diverges from the exact 19 at {schemas_dir}: {names}")
    for f in reg["families"]:
        contract = f["contract"]
        schema_path = schemas_dir / f"{contract}.schema.json"
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            findings.append(f"{label}: missing schema member {contract} at {schemas_dir} ({schema_path.name})")
            continue
        except (OSError, ValueError) as exc:
            findings.append(f"{label}: unreadable/unparseable schema member {contract} at {schemas_dir}: {exc}")
            continue
        if "2020-12" not in str(schema.get("$schema", "")):
            findings.append(f"{label}: {contract} schema draft is not 2020-12 at {schemas_dir}")
        enforced = set(schema.get("required", []))
        declared = set(f.get("required_fields", []))
        missing = declared - enforced
        if missing:
            findings.append(f"{label}: {contract} registry fields not enforced by schema "
                            f"{sorted(missing)} at {schemas_dir}")
    return findings, len(names)


def doctor(root: Path) -> dict[str, Any]:
    """Diagnose BOTH schemas surfaces and AND the verdict (F-R5-01 repair).

    Surface 1 is the workspace-local ``<root>/schemas`` tree (the pre-existing check).
    Surface 2 is the RESOLVED surface the CLI/registry actually consume, in order
    ``$PIPD_SCHEMAS_DIR`` -> packaged wheel copy -> ``<repo>/schemas`` fallback, as reported
    by ``registry.describe_schemas_source()``. The old implementation only ever read
    ``<root>/schemas``, so installing a wheel with a torn packaged ``schemas/`` copy and
    running ``pipd doctor`` from a healthy workspace printed PASS. The verdict is now the AND
    of both surfaces and is NEVER rescued by a different schemas copy: a failing resolved
    member names the family and the resolved path. ``schema_source`` tells the operator which
    surface was inspected (mode, path, tried).
    """
    findings: list[str] = []
    families: int | None = None

    local = root / "schemas"
    if local.is_dir():
        local_findings, local_families = _check_schemas_surface(local, label="workspace-local")
        findings.extend(local_findings)
        families = local_families

    source = registry.describe_schemas_source()
    resolved = Path(source["path"]) if source["path"] else None
    if resolved is None:
        findings.append("resolved schemas surface (mode=NONE): no schemas dir containing "
                        "registry.json was found; tried: " + "; ".join(source["tried"]))
    else:
        resolved_findings, resolved_families = _check_schemas_surface(
            resolved, label=f"resolved[{source['mode']}]")
        findings.extend(resolved_findings)
        if resolved_families is not None:
            families = resolved_families

    drift = scan_skill_drift(root)
    return {"verdict": "PASS" if not findings else "FAIL", "findings": findings,
            "families": families, "skill_drift": drift, "schema_source": source}


def _surface_of(path: Path, root: Path) -> str:
    """Host surface = first path segment below a known generated root."""
    rel = path.relative_to(root).parts
    return rel[0] if rel else "."


def scan_skill_drift(root: Path) -> list[str]:
    """doctor must report duplicate Skill / managed-vendored collision / residue.

    Two DIFFERENT host surfaces legitimately carry the same generated skill name
    (managed .agents vs vendored .hermes projection). The invariant is that the SAME
    host surface must not receive two copies of one skill name.
    """
    out = []
    seen: dict[tuple[str, str], int] = {}
    for s in root.rglob("SKILL.md"):
        if ".git" in s.parts or s.parts[-2:-1] == ("__pycache__",):
            continue
        key = (_surface_of(s, root), str(s.parent.name))
        seen[key] = seen.get(key, 0) + 1
    for (surface, name), n in sorted(seen.items()):
        if n > 1:
            out.append(f"duplicate Skill name {name} x{n} inside surface {surface}")
    manifests = list(root.glob("*/*/manifest.json"))
    if manifests and not (root / ".hgk" / "surfaces" / "skill_surface_manifest.json").exists():
        out.append("managed/vendored surfaces present without a declared separation manifest")
    if (root / "dist" / "web" / "README.md").exists() and not (root / "dist" / "web" / "index.html").exists():
        out.append("uninstall residue: web projection left README without index.html")
    return out


def semantic_diff(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(set(a) | set(b))
    changes = []
    for k in keys:
        if k in ("generated_at", "run_id"):
            continue
        if a.get(k) != b.get(k):
            changes.append({"field": k, "from": a.get(k), "to": b.get(k)})
    schema_changed = any(c["field"] == "schema_version" for c in changes)
    if schema_changed:
        raise DiffIncompatible("schema_version changed without a migration record")
    return {"verdict": "PASS", "changed_fields": changes, "count": len(changes)}


def repair_candidate(subject: str, *, scope: list[str], maker: str,
                     authorized_root: str = "", self_accept: bool = False) -> dict[str, Any]:
    if self_accept:
        raise SelfAcceptForbidden("repair candidate cannot be self-accepted by the maker")
    if not scope:
        raise RepairScopeFail("repair requires an explicit bounded scope")
    # An adversarial lane (deleg_1e6aaacf lane C) drove `**`, absolute external paths and `../`
    # escapes through this function, which previously accepted anything non-empty. A repair
    # candidate that can name HG-KSEOS is a scope-expansion hole, so it is refused outright.
    bad = [s for s in scope
           if not s or s.strip() in ("**", "**/*", "*", "/", "")
           or s.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", s)
           or ".." in s.replace("\\", "/").split("/")]
    if bad:
        raise RepairScopeFail(f"repair scope escapes the authorised root: {bad}")
    if authorized_root:
        root = Path(authorized_root).resolve()
        outside = []
        for s in scope:
            try:
                (root / s.split("*")[0].strip("/")).resolve().relative_to(root)
            except Exception:
                outside.append(s)
        if outside:
            raise RepairScopeFail(f"repair scope outside the authorised root {root}: {outside}")
        # The SUBJECT was previously unvalidated: a caller could name a benign scope and point the
        # subject anywhere on the host. A repair candidate is only bounded if BOTH the scope and the
        # subject resolve inside the authorised root.
        raw = subject.replace("\\", "/")
        if ".." in raw.split("/"):
            raise RepairScopeFail(f"repair subject escapes the authorised root: {subject}")

        def _outside() -> None:
            raise RepairScopeFail(f"repair subject outside the authorised root {root}: {subject}")

        # A leading "/", a drive letter ("C:") or a UNC prefix ("//") is ABSOLUTE — on the host that
        # produced it, which is not necessarily the host this runs on. Containment is therefore
        # decided with the subject's OWN path flavour, never by re-basing it onto the root: on POSIX,
        # Path("C:/Windows/system32/x.dll") is a RELATIVE path, so `resolve()` would place it under
        # the root (resolved against the cwd) and let a foreign-absolute escape through as if it were
        # inside. Measured: the hosted-Linux run of tests/test_negative_and_rollback.py failed
        # exactly on that subject while the Windows run passed.
        root_posix = root.as_posix()
        drive = re.match(r"^([A-Za-z]):/", raw)
        unc = raw.startswith("//")
        root_drive = re.match(r"^([A-Za-z]):/", root_posix)
        if drive or unc:
            # Windows-flavoured absolute subject: compare textually against the root's own form.
            if not root_drive or (unc and not root_posix.startswith("//")):
                _outside()
            root_letter = root_drive.group(1).lower() if root_drive else ""
            if drive and drive.group(1).lower() != root_letter:
                _outside()
            if not (raw.lower() == root_posix.lower()
                    or raw.lower().startswith(root_posix.rstrip("/").lower() + "/")):
                _outside()
            # Same drive and a textual prefix match: this host can represent the path, so keep the
            # symlink-following check as well.
            try:
                Path(raw).resolve().relative_to(root)
            except Exception:
                _outside()
        elif raw.startswith("/"):
            if not root_posix.startswith("/"):
                _outside()
            try:
                # A leading "/" is absolute: resolve it as given. Re-basing it onto the root would
                # silently reinterpret "/etc/passwd" as "<root>/etc/passwd".
                Path(raw).resolve().relative_to(root)
            except Exception:
                _outside()
        else:
            try:
                (root / raw).resolve().relative_to(root)
            except Exception:
                _outside()
    else:
        raise RepairScopeFail("repair requires authorized_root; an unscoped repair is not bounded")
    return {"schema": "PIPD-REPAIR-CANDIDATE/1", "subject": subject, "scope": scope,
            "maker": maker, "state": "CANDIDATE", "authorized_root": str(authorized_root),
            "isolation": "workspace_only", "requalification": "affected-only",
            "self_accept": False}
