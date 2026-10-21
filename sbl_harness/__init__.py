"""The HGK harness adapter — the SBL-side half of "upgraded HG-KSEOS".

What this is: a *pinned dependency declaration plus an installable adapter*, not a copy of HGK.
HG-KSEOS is the sole normative control plane and its native root is upgraded only by its own owner
under its own WorkOrder. Copying that code into SBL, or minting WorkOrders/Permits from here, would
create a second control plane — the one thing the governance contract forbids.

So the deliverable is deliberately split:

* the adapter is real and testable — it declares the pinned HGK version, the harness ABI it speaks,
  where the native root is expected, and it can be installed, doctor'd and uninstalled on its own;
* the *native* claims are not made here. ``claim_ceiling`` stays ``HOST_PENDING`` until an owner, on
  the real host, executes a WorkOrder → ExecutionBinding → Permit trace and reads the effect back.

The probe is honest by construction: a missing or unrelated root produces a typed refusal with the
reason, never a fabricated "OK".
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from sbl_core.errors import SBLError
from sbl_sp.plugins import portable

ADAPTER_VERSION = "0.1.1rc1"
CLAIM_CEILING = "HOST_PENDING"
PLUGIN_NAME = "sbl-hgk-harness"
SKILL_NAME = "hgk-governed-runtime"

HGK_PIN: dict[str, str] = {
    "package": "hg_kseos",
    "version": "0.1.0",
    "version_range": ">=0.1.0,<0.2.0",
    "root_env": "HGK_ROOT",
    "default_root": "C:/Projects/Agent_Workspace/HG-KSEOS",
    "source_subdir": "src/hg_kseos",
    "spine_relpath": "var/shared-spine/hg-kseos.db",
    "lane_registry_relpath": "config/lane-route-slots.candidate.json",
    "dispatcher_relpath": "scripts/hgk-lane-dispatch.py",
}

HARNESS_ABI: dict[str, Any] = {
    "name": "hgk-harness-abi/1",
    "provides": [
        "plan",  # read-only planning against a frozen source
        "execute",  # bounded write inside a declared write-set
        "verify",  # read-only independent check
    ],
    "requires_native": [
        "WorkOrder",
        "ExecutionBinding",
        "Permit",
    ],
    "not_provided": [
        "native_effect",  # only HGK's own issuer may grant this
        "permit_signing",
        "workorder_admission",
    ],
}

_ADAPTER_FILE = "adapter.json"
_MANIFEST_FILE = "MANIFEST.json"
# The ONLY relative paths an uninstall may ever delete: exactly the files ``install`` writes.
# A manifest is data, so a key it carries never widens the deletable set.
_DELETABLE_RELPATHS = frozenset({_ADAPTER_FILE, "plugin.json", f"skills/{SKILL_NAME}/SKILL.md"})
_ABS_DRIVE = re.compile(r"^[A-Za-z]:")


def _resolve_deletable(root_dir: Path, root_resolved: Path, rel: object) -> Path:
    """Map a manifest file key to a deletable path, or refuse with a typed error.

    Four conditions, each independently necessary: the key must be a plain relative path (no NUL,
    not absolute, no drive prefix), it must be one of the paths this adapter installs, resolving it
    must stay inside the install root (which also catches a junction/reparse-point parent that
    leaves the root), and the path itself must not be a link.
    """

    if not isinstance(rel, str) or not rel or "\x00" in rel:
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "manifest file key is not a usable relative path",
            {"key": repr(rel)},
        )
    normalized = rel.replace("\\", "/")
    if normalized.startswith("/") or _ABS_DRIVE.match(normalized) or Path(normalized).is_absolute():
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "manifest file key is absolute; an uninstall may only delete adapter-owned relative paths",
            {"key": rel},
        )
    if normalized not in _DELETABLE_RELPATHS:
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "manifest file key is outside this adapter's fixed file allowlist",
            {"key": rel, "allowed": sorted(_DELETABLE_RELPATHS)},
        )
    path = root_dir / normalized
    try:
        resolved = path.resolve(strict=False)
    except OSError as exc:  # unreachable parent, bad name, dangling junction
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "manifest path cannot be resolved inside the install root",
            {"key": rel, "error": type(exc).__name__},
        ) from exc
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "manifest path resolves outside the install root",
            {"key": rel, "resolved": str(resolved), "root": str(root_resolved)},
        )
    is_junction = getattr(os.path, "isjunction", None)
    if path.is_symlink() or (is_junction is not None and is_junction(path)):
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "manifest path is a link; an uninstall never follows a link out of the install root",
            {"key": rel},
        )
    return path
_SKILL_BODY = """---
name: hgk-governed-runtime
description: Route bounded plan/execute/verify work through the pinned HG-KSEOS native control plane; never mint Permits or claim native effect
---

# HGK governed runtime (adapter)

This skill is an *adapter*, not a control plane. It tells an agent harness how to reach the pinned
HG-KSEOS root, what ABI it can speak, and where the boundary of its authority is.

## What it does

1. **Resolve the root.** Read `adapter.json` next to this skill and use its `hgk_root`; never guess a
   different root and never invent a spine database.
2. **Probe before use.** Call the adapter's `doctor` first. A failed probe means the native plane is
   not reachable — report `HOST_PENDING`, do not substitute a local simulation for it.
3. **Stay inside the ABI.** `plan`, `execute`, `verify` are readable entry points. `WorkOrder`,
   `ExecutionBinding` and `Permit` are *required from the native plane*; this adapter cannot issue,
   sign or admit any of them.

## What it must never do

- Mint a Permit, admit a WorkOrder, or self-sign an acknowledgement.
- Describe a local Python check as a native effect.
- Modify the HGK root: upgrades there belong to the HGK owner under a separate WorkOrder.
"""


def resolve_root(explicit: str | Path | None = None) -> Path:
    """Resolve the HGK root without asserting it exists."""

    if explicit:
        return Path(explicit)
    env = os.environ.get(HGK_PIN["root_env"])
    if env:
        return Path(env)
    return Path(HGK_PIN["default_root"])


def probe(root: str | Path | None = None) -> dict[str, Any]:
    """Read-only inspection of an HGK root. Returns a status, never a bare boolean."""

    resolved = resolve_root(root)
    checks: list[dict[str, Any]] = []

    def record(name: str, ok: bool, detail: str, path: Path | None = None) -> None:
        checks.append(
            {
                "check": name,
                "ok": ok,
                "detail": detail,
                "path": str(path) if path else None,
            }
        )

    record("root_exists", resolved.is_dir(), "HGK root directory", resolved)
    source = resolved / HGK_PIN["source_subdir"]
    record("package_present", source.is_dir(), "hg_kseos package directory", source)
    spine = resolved / HGK_PIN["spine_relpath"]
    record("spine_present", spine.is_file(), "shared spine database", spine)
    registry = resolved / HGK_PIN["lane_registry_relpath"]
    record("lane_registry_present", registry.is_file(), "lane route slots", registry)
    dispatcher = resolved / HGK_PIN["dispatcher_relpath"]
    record("dispatcher_present", dispatcher.is_file(), "lane dispatcher entry point", dispatcher)

    # A second import check that cannot be satisfied by an unrelated directory: the package must be
    # importable *from this root* and expose the pinned version. Any module already cached under the
    # same name is set aside and restored, so probing a synthetic root cannot poison the process.
    found_version: str | None = None
    if source.is_dir():
        import importlib

        probe_path = str(source.parent)
        added = probe_path not in sys.path
        if added:
            sys.path.insert(0, probe_path)
        prior = sys.modules.pop("hg_kseos", None)
        try:
            module = importlib.import_module("hg_kseos")
            found_version = str(getattr(module, "__version__", "")) or None
            location = Path(getattr(module, "__file__", "") or "").resolve()
            inside = source.resolve() in location.parents
        except Exception as exc:  # noqa: BLE001 - import failure is a probe result, not a crash
            record("import", False, f"import hg_kseos failed: {exc}")
        else:
            record(
                "import",
                bool(found_version) and inside,
                "imported hg_kseos from the root" if inside else "hg_kseos resolved elsewhere",
                location,
            )
        finally:
            sys.modules.pop("hg_kseos", None)
            if prior is not None:
                sys.modules["hg_kseos"] = prior
            if added:
                try:
                    sys.path.remove(probe_path)
                except ValueError:
                    pass

    satisfied = all(item["ok"] for item in checks)
    if not satisfied:
        status = "REFUSED_ROOT_UNUSABLE"
    elif found_version and found_version != HGK_PIN["version"]:
        status = "REFUSED_VERSION_MISMATCH"
    else:
        status = "ROOT_READY"

    return {
        "status": status,
        "root": str(resolved),
        "pin": dict(HGK_PIN),
        "observed_version": found_version,
        "abi": dict(HARNESS_ABI),
        "checks": checks,
        "claim_ceiling": CLAIM_CEILING,
        "native_effect": "NOT_GRANTED",
    }


def plugin_manifest(probe_result: dict[str, Any] | None = None) -> dict[str, Any]:
    result = probe_result or probe()
    return {
        "$schema": portable.CANONICAL_SCHEMA_URI,
        "name": PLUGIN_NAME,
        "version": ADAPTER_VERSION,
        "description": (
            "Adapter for the pinned HG-KSEOS native control plane: declares the dependency, the "
            "harness ABI and the boundaries of its authority"
        ),
        "license": "MIT",
        "keywords": ["sbl", "hgk", "governance", "harness-adapter"],
        "extensions": {
            "org.sbl.harness": {
                "abi": dict(HARNESS_ABI),
                "hgk_pin": dict(HGK_PIN),
                "observed": {
                    "status": result["status"],
                    "version": result["observed_version"],
                    "root": result["root"],
                },
                "claim_ceiling": CLAIM_CEILING,
                "native_effect": "NOT_GRANTED",
            }
        },
    }


def _write(path: Path, data: bytes) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def install(target: str | Path, hgk_root: str | Path | None = None) -> dict[str, Any]:
    """Install the adapter into ``target``. A failed probe installs nothing."""

    resolved_target = Path(target)
    if resolved_target.exists() and any(resolved_target.iterdir()):
        raise SBLError(
            "SBL_E_FOREIGN_FILES",
            "refusing to install into a non-empty directory this adapter does not own",
            {"target": str(resolved_target)},
        )

    result = probe(hgk_root)
    if result["status"] != "ROOT_READY":
        raise SBLError(
            "SBL_E_BAD_STATE",
            "the pinned HGK root is not usable; nothing was installed",
            {"status": result["status"], "checks": result["checks"][:3]},
        )

    manifest = plugin_manifest(result)
    portable.assert_valid(manifest, where=f"{PLUGIN_NAME}/plugin.json")
    files: dict[str, bytes] = {
        "plugin.json": (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8"),
        f"skills/{SKILL_NAME}/SKILL.md": _SKILL_BODY.encode("utf-8"),
        _ADAPTER_FILE: (
            json.dumps(
                {
                    "schema": "SBL-HGK-ADAPTER/1",
                    "abi": HARNESS_ABI,
                    "hgk_pin": HGK_PIN,
                    "hgk_root": result["root"],
                    "observed_version": result["observed_version"],
                    "host": {
                        "platform": platform.platform(),
                        "python": platform.python_version(),
                        "executable": sys.executable,
                    },
                    "claim_ceiling": CLAIM_CEILING,
                    "native_effect": "NOT_GRANTED",
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n"
        ).encode("utf-8"),
    }
    digests = {rel: _write(resolved_target / rel, payload) for rel, payload in files.items()}
    _write(
        resolved_target / "MANIFEST.json",
        (json.dumps({"files": digests}, indent=2) + "\n").encode("utf-8"),
    )
    return {
        "ok": True,
        "target": str(resolved_target),
        "files": sorted(files),
        "digests": digests,
        "probe_status": result["status"],
        "claim_ceiling": CLAIM_CEILING,
        "native_effect": "NOT_GRANTED",
    }


def doctor(target: str | Path) -> dict[str, Any]:
    """Re-verify an installed adapter: files intact, root still usable, ABI unchanged."""

    root_dir = Path(target)
    adapter_path = root_dir / _ADAPTER_FILE
    manifest_path = root_dir / "MANIFEST.json"
    problems: list[str] = []
    if not adapter_path.is_file():
        problems.append("adapter.json is missing")
    if not manifest_path.is_file():
        problems.append("MANIFEST.json is missing")
    if problems:
        return {"ok": False, "problems": problems, "target": str(root_dir)}

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for rel, expected in manifest.get("files", {}).items():
        path = root_dir / rel
        if not path.is_file():
            problems.append(f"{rel} is missing")
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            problems.append(f"{rel} digest changed")

    adapter = json.loads(adapter_path.read_text(encoding="utf-8"))
    result = probe(adapter.get("hgk_root"))
    if result["status"] != "ROOT_READY":
        problems.append(f"HGK root probe is {result['status']}")
    if adapter.get("abi", {}).get("name") != HARNESS_ABI["name"]:
        problems.append("adapter ABI name changed since install")

    return {
        "ok": not problems,
        "problems": problems,
        "target": str(root_dir),
        "probe": result,
        "abi": adapter.get("abi", {}).get("name"),
        "claim_ceiling": CLAIM_CEILING,
        "native_effect": "NOT_GRANTED",
    }


def uninstall(target: str | Path) -> dict[str, Any]:
    """Remove exactly what ``install`` wrote. Refuses when the directory holds anything else.

    The manifest is treated as untrusted input: it can narrow what is deleted (a file that is gone
    is simply skipped) but it can never widen it. Every key must be one of the paths ``install``
    writes, resolve inside the install root, and still match the digest the manifest declares — so
    a tampered manifest refuses the uninstall instead of deleting something outside the adapter.
    """

    root_dir = Path(target)
    if not root_dir.is_dir():
        raise SBLError("SBL_E_BAD_STATE", "nothing to uninstall", {"target": str(root_dir)})
    manifest_path = root_dir / _MANIFEST_FILE
    if manifest_path.is_symlink():
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "MANIFEST.json is a link; refusing to uninstall from a manifest that lives elsewhere",
            {"target": str(root_dir)},
        )
    if not manifest_path.is_file():
        raise SBLError(
            "SBL_E_FOREIGN_FILES",
            "no MANIFEST.json: this adapter did not install here",
            {"target": str(root_dir)},
        )
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "MANIFEST.json is not readable JSON; refusing to delete anything",
            {"target": str(root_dir), "error": type(exc).__name__},
        ) from exc
    if not isinstance(manifest, dict):
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "MANIFEST.json is not an object",
            {"target": str(root_dir)},
        )
    files = manifest.get("files", {})
    if not isinstance(files, dict):
        raise SBLError(
            "SBL_E_MANIFEST_UNTRUSTED",
            "MANIFEST.json 'files' is not an object of path -> digest",
            {"target": str(root_dir)},
        )

    root_resolved = root_dir.resolve(strict=True)
    deletable: list[tuple[str, str, Path]] = []
    for key, expected in files.items():
        path = _resolve_deletable(root_dir, root_resolved, key)
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise SBLError(
                "SBL_E_MANIFEST_UNTRUSTED",
                "MANIFEST.json declares a digest that is not a sha256 hex string",
                {"key": key},
            )
        deletable.append((key, key.replace("\\", "/"), path))

    present = {
        str(path.relative_to(root_dir)).replace("\\", "/")
        for path in root_dir.rglob("*")
        if path.is_file()
    }
    foreign = sorted(present - {norm for _, norm, _ in deletable} - {_MANIFEST_FILE})
    if foreign:
        raise SBLError(
            "SBL_E_FOREIGN_FILES",
            "refusing to remove a directory containing files this adapter did not write",
            {"foreign": foreign},
        )

    for key, _, path in deletable:
        if not path.is_file():
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != files[key]:
            raise SBLError(
                "SBL_E_MANIFEST_UNTRUSTED",
                "a file changed since install; refusing to delete a file the manifest no longer describes",
                {"key": key, "declared": files[key], "actual": actual},
            )

    removed: list[str] = []
    for key, norm, path in sorted(deletable, key=lambda item: item[2], reverse=True):
        if path.is_file():
            path.unlink()
            removed.append(norm)
    if manifest_path.is_file():
        manifest_path.unlink()
        removed.append(_MANIFEST_FILE)
    removed.sort()

    # Directory cleanup is bounded to the directories install() creates. It never walks the tree:
    # an rglob-based sweep follows a junction out of the root (found by the R5 VERIFY lane, which
    # constructed exactly that escape), so the sweep is replaced by an explicit, contained list.
    is_junction = getattr(os.path, "isjunction", None)
    for rel_dir in (f"skills/{SKILL_NAME}", "skills"):
        directory = root_dir / rel_dir
        if directory.is_symlink() or (is_junction is not None and is_junction(directory)):
            continue
        try:
            resolved = directory.resolve(strict=True)
        except OSError:
            continue
        if resolved != root_resolved and root_resolved not in resolved.parents:
            continue
        if directory.is_dir() and not any(directory.iterdir()):
            directory.rmdir()
    empty = not any(root_dir.iterdir())
    if empty:
        shutil.rmtree(root_dir, ignore_errors=False)
    return {"ok": True, "target": str(root_dir), "removed": removed, "empty": empty}
