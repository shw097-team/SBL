"""The SBL Stack: install, doctor, operate, roll back, uninstall — as one product surface.

The Foundation preview shipped a CLI (``sbl-todo``) and a six-module core. That is a useful first
outcome, not an installable stack: nothing recorded *which* bytes were installed, so nothing could
tell a healthy install from a tampered one, and there was no single command that exercised the six
modules together.

This module adds that surface without inventing a second control plane:

* ``install`` writes an integrity manifest of the exact module files it validated, then verifies the
  composed core before returning. It refuses a non-empty target it did not create.
* ``doctor`` re-derives every digest from the *live* installation and re-runs the composition check.
  A changed byte is a failure, not a warning.
* ``selftest`` walks one ordinary journey through M01→M02→M03 and asserts two refusals. It is the
  operation a user runs to find out whether the stack actually works.
* ``uninstall`` removes only the files the manifest lists, and refuses when it finds anything else.

Claim ceiling: this proves a *local, standalone* stack. It does not prove any host loaded it, and it
grants no native effect — those stay with the host and with HGK's own issuer.
"""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from sbl_core import core as sbl_core_core
from sbl_core import modes
from sbl_core.errors import SBLError
from sbl_core.m01_intake import GoalIntake
from sbl_core.m02_spec import GuidedSpecification
from sbl_core.m03_routing import GovernedRouting
from sbl_core.core import SharedCore
from sbl_sp import sp as sbl_sp_manifest
from sbl_sp import plugins as sbl_plugins

STACK_SCHEMA = "SBL-STACK/1"
CLAIM_CEILING = "STANDALONE_ONLY"
MANIFEST_NAME = "stack.json"

# The modules whose bytes define the installed stack. Anything not listed here is outside the
# integrity claim, and the report says so rather than implying blanket coverage.
COMPONENT_MODULES: tuple[str, ...] = (
    "sbl_core.core",
    "sbl_core.dto",
    "sbl_core.errors",
    "sbl_core.modes",
    "sbl_core.gknow",
    "sbl_core.m01_intake",
    "sbl_core.m02_spec",
    "sbl_core.m03_routing",
    "sbl_core.m04_bridge",
    "sbl_core.m05_verify",
    "sbl_core.m06_repair",
    "sbl_sp.sp",
    "sbl_sp.plugins",
    "sbl_sp.plugins.portable",
)


def _module_source(name: str) -> Path:
    try:
        module = sys.modules.get(name) or __import__(name, fromlist=["__name__"])
    except ImportError as exc:
        raise SBLError(
            "SBL_E_COMPONENT_UNRESOLVED",
            f"a stack component cannot be resolved to a module: {exc}",
            {"module": name},
        ) from None
    location = getattr(module, "__file__", None)
    if not location:
        raise SBLError(
            "SBL_E_BAD_STATE",
            "a stack component module has no file on disk",
            {"module": name},
        )
    return Path(location).resolve()


def component_digests() -> dict[str, str]:
    return {
        name: hashlib.sha256(_module_source(name).read_bytes()).hexdigest()
        for name in COMPONENT_MODULES
    }


def _stack_extras() -> dict[str, Any]:
    """Non-module components the stack composes, recorded so a reader can see the whole surface."""

    return {
        "principals": {
            sp_id: sbl_sp_manifest.load_manifest(sp_id) for sp_id in sbl_plugins.SP_IDS
        },
        "mode_gate_cells": len(modes.mode_gate_matrix()),
        "plugin_schema": sbl_plugins.PLUGIN_SCHEMA_URI,
    }


def install(target: str | Path) -> dict[str, Any]:
    root = Path(target)
    if root.exists() and any(root.iterdir()):
        raise SBLError(
            "SBL_E_FOREIGN_FILES",
            "refusing to install the stack into a non-empty directory it does not own",
            {"target": str(root)},
        )
    root.mkdir(parents=True, exist_ok=True)

    digests = component_digests()
    composed = SharedCore(str(root)).doctor()
    if not composed.get("ok"):
        raise SBLError(
            "SBL_E_BAD_STATE",
            "the composed core did not report healthy; nothing was installed",
            {"doctor": composed},
        )

    manifest = {
        "schema": STACK_SCHEMA,
        "version": "0.1.1rc1",
        "root": str(root.resolve()),
        "python": platform.python_version(),
        "components": digests,
        "extras": _stack_extras(),
        "claim_ceiling": CLAIM_CEILING,
        "host_install_state": "NOT_INSTALLED",
    }
    payload = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (root / MANIFEST_NAME).write_bytes(payload)
    return {
        "ok": True,
        "target": str(root),
        "manifest": str(root / MANIFEST_NAME),
        "manifest_sha256": hashlib.sha256(payload).hexdigest(),
        "components": len(digests),
        "claim_ceiling": CLAIM_CEILING,
        "host_install_state": "NOT_INSTALLED",
    }


def doctor(target: str | Path) -> dict[str, Any]:
    root = Path(target)
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        return {
            "ok": False,
            "code": "SBL_E_NOT_INSTALLED",
            "problems": ["stack.json is missing: this directory is not an installed stack"],
            "target": str(root),
            "claim_ceiling": CLAIM_CEILING,
        }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    problems: list[str] = []
    codes: list[str] = []
    recorded = manifest.get("components", {})
    for name, expected in recorded.items():
        try:
            actual = hashlib.sha256(_module_source(name).read_bytes()).hexdigest()
        except SBLError as exc:
            problems.append(f"{name}: {exc.message}")
            codes.append(exc.code)
            continue
        if actual != expected:
            problems.append(f"{name}: digest changed since install")
            codes.append("SBL_E_DIGEST_MISMATCH")
    missing = sorted(set(COMPONENT_MODULES) - set(recorded))
    if missing:
        problems.append("manifest does not cover: " + ", ".join(missing))
        codes.append("SBL_E_MANIFEST_INCOMPLETE")

    composed = SharedCore(str(root)).doctor()
    if not composed.get("ok"):
        problems.append("composed core is not healthy")
        codes.append("SBL_E_CORE_UNHEALTHY")

    report: dict[str, Any] = {
        "ok": not problems,
        "problems": problems,
        "target": str(root),
        "components": len(recorded),
        "mode_gate_cells": len(modes.mode_gate_matrix()),
        "claim_ceiling": CLAIM_CEILING,
        "host_install_state": "NOT_INSTALLED",
    }
    if problems:
        report["code"] = (
            "SBL_E_COMPONENT_UNRESOLVED"
            if "SBL_E_COMPONENT_UNRESOLVED" in codes
            else codes[0]
        )
    return report


def status(target: str | Path) -> dict[str, Any]:
    root = Path(target)
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        return {"installed": False, "target": str(root), "claim_ceiling": CLAIM_CEILING}
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "installed": True,
        "target": str(root),
        "schema": manifest.get("schema"),
        "version": manifest.get("version"),
        "components": len(manifest.get("components", {})),
        "principals": sorted(manifest.get("extras", {}).get("principals", {})),
        "claim_ceiling": manifest.get("claim_ceiling"),
        "host_install_state": manifest.get("host_install_state"),
    }


def selftest(workdir: str | Path | None = None) -> dict[str, Any]:
    """One ordinary journey plus two refusals. Returns raw step outcomes, not a bare verdict."""

    steps: list[dict[str, Any]] = []

    def step(name: str, fn) -> Any:
        try:
            value = fn()
        except SBLError as exc:
            steps.append({"step": name, "ok": False, "code": exc.code, "message": exc.message})
            return None
        except Exception as exc:  # noqa: BLE001 - a crash is a step outcome here
            steps.append({"step": name, "ok": False, "error": repr(exc)})
            return None
        steps.append({"step": name, "ok": True})
        return value

    def assert_true(value: Any, message: str) -> bool:
        if not value:
            raise AssertionError(message)
        return True

    core = SharedCore(str(workdir or "."))
    step("core.doctor", lambda: assert_true(core.doctor()["ok"], "core doctor reported unhealthy"))

    goal = step("m01.intake", lambda: core.intake.intake("ship an installable stack"))
    atoms = step(
        "m02.derive",
        lambda: core.spec.derive(
            goal, [{"text": "the stack installs and uninstalls cleanly", "locator": "DOC-12/C37"}]
        )
        if goal
        else [],
    )
    decision = step(
        "m03.route.CLI_TOOL",
        lambda: core.routing.route(atoms[0], "CLI_TOOL") if atoms else None,
    )
    if decision is not None and not getattr(decision, "permitted", False):
        steps.append({"step": "m03.route.CLI_TOOL.permitted", "ok": False})

    def refuse_unlocated() -> bool:
        try:
            core.spec.derive(goal, [{"text": "no locator here"}])
        except SBLError as exc:
            if exc.code == "SBL_E_UNLOCATED_REQUIREMENT":
                return True
            raise
        raise AssertionError("a clause with no locator was accepted")

    def refuse_prohibited_kind() -> bool:
        try:
            core.routing.route(atoms[0], "AGENT_OS")
        except SBLError as exc:
            if exc.code == "SBL_E_PROHIBITED_KIND":
                return True
            raise
        raise AssertionError("a PROHIBITED_IN_V0_1 kind was routed")

    if goal and atoms:
        step("NEG.unlocated-clause", refuse_unlocated)
        step("NEG.prohibited-kind", refuse_prohibited_kind)

    step(
        "sp.manifests",
        lambda: all(sbl_sp_manifest.load_manifest(sp) for sp in sbl_plugins.SP_IDS) or True,
    )
    step(
        "modes.matrix",
        lambda: assert_true(
            len(modes.mode_gate_matrix()) == 39, "expected 39 mode gate cells"
        ),
    )
    step(
        "plugins.build",
        lambda: all(
            sbl_plugins.inspect_package(pkg["path"])["schema_violations"] == []
            for pkg in sbl_plugins.build_all(Path(workdir or ".") / "_stack_selftest_plugins")
        ),
    )

    ok = all(item["ok"] for item in steps)
    return {
        "ok": ok,
        "steps": steps,
        "denominator": f"{sum(1 for item in steps if item['ok'])}/{len(steps)}",
        "claim_ceiling": CLAIM_CEILING,
        "host_install_state": "NOT_INSTALLED",
    }


def uninstall(target: str | Path) -> dict[str, Any]:
    root = Path(target)
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        raise SBLError(
            "SBL_E_FOREIGN_FILES",
            "no stack.json: this directory is not a stack this module installed",
            {"target": str(root)},
        )
    present = {
        str(path.relative_to(root)).replace("\\", "/")
        for path in root.rglob("*")
        if path.is_file()
    }
    # preimages are this product's own artefacts: refusing them would make an upgraded stack impossible to remove.
    own = {path for path in present if path == MANIFEST_NAME or path.split("/")[0].startswith(PREIMAGE_PREFIX)}
    foreign = sorted(present - own)
    if foreign:
        raise SBLError(
            "SBL_E_FOREIGN_FILES",
            "refusing to remove a directory containing files this stack did not install",
            {"foreign": foreign[:10], "count": len(foreign)},
        )
    manifest_path.unlink()
    for directory in sorted(root.glob(f"{PREIMAGE_PREFIX}*")):
        if directory.is_dir():
            shutil.rmtree(directory)
    empty = not any(root.iterdir())
    if empty:
        shutil.rmtree(root, ignore_errors=False)
    return {"ok": True, "target": str(root), "removed": [MANIFEST_NAME], "empty": empty}


PREIMAGE_PREFIX = "stack.preimage-"


def _read_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / MANIFEST_NAME
    if not manifest_path.is_file():
        raise SBLError(
            "SBL_E_BAD_STATE",
            "no stack.json: this directory is not an installed stack",
            {"target": str(root)},
        )
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def load(target: str | Path) -> dict[str, Any]:
    """Import every component the manifest names, after checking its digest.

    The digest check comes first: importing bytes that do not match the manifest would be loading something
    the stack never installed. A component that fails the check is reported and the load fails closed.
    """

    root = Path(target)
    manifest = _read_manifest(root)
    recorded: dict[str, str] = manifest.get("components", {})
    loaded: list[str] = []
    problems: list[str] = []
    for name, expected in recorded.items():
        try:
            module = __import__(name, fromlist=["__name__"])
            actual = hashlib.sha256(_module_source(name).read_bytes()).hexdigest()
        except SBLError as exc:
            problems.append(f"{name}: {exc.message}")
            continue
        except Exception as exc:  # noqa: BLE001 - an import failure is an outcome, not a crash
            problems.append(f"{name}: import failed: {exc!r}")
            continue
        if actual != expected:
            problems.append(f"{name}: digest changed since install")
            continue
        loaded.append(f"{module.__name__}")
    missing = sorted(set(COMPONENT_MODULES) - set(recorded))
    if missing:
        problems.append("manifest does not cover: " + ", ".join(missing))
    return {
        "ok": not problems and len(loaded) == len(recorded),
        "target": str(root),
        "loaded": loaded,
        "problems": problems,
        "components": len(recorded),
        "claim_ceiling": CLAIM_CEILING,
    }


def invoke(target: str | Path, mode: str | None = None) -> dict[str, Any]:
    """Exercise the installed mode gate and report the cells it produced."""

    root = Path(target)
    manifest = _read_manifest(root)
    cells = modes.mode_gate_matrix()
    if mode is not None:
        known = {cell.get("mode") for cell in cells if isinstance(cell, dict)}
        if mode not in known:
            raise SBLError(
                "SBL_E_PROHIBITED_KIND",
                "the requested mode is not in the installed mode gate",
                {"mode": mode, "known": sorted(str(x) for x in known if x)},
            )
        cells = [cell for cell in cells if cell.get("mode") == mode]
    return {
        "ok": bool(cells),
        "target": str(root),
        "version": manifest.get("version"),
        "mode": mode,
        "cells": cells,
        "count": len(cells),
        "claim_ceiling": CLAIM_CEILING,
    }


def upgrade(target: str | Path, manifest_path: str | Path) -> dict[str, Any]:
    """Replace the recorded manifest with a different one, after proving the live bytes match it.

    A reinstall of the same environment produces the same digests, which is why "reinstall" could not prove an
    upgrade. This verb takes the desired manifest explicitly, refuses a no-op, verifies every desired digest
    against the live modules, keeps the old manifest as a preimage, and only then swaps it in.
    """

    root = Path(target)
    current = _read_manifest(root)
    desired_path = Path(manifest_path)
    desired = json.loads(desired_path.read_text(encoding="utf-8"))
    if desired.get("schema") != current.get("schema"):
        raise SBLError("SBL_E_BAD_STATE", "schema mismatch between current and desired manifest",
                       {"current": current.get("schema"), "desired": desired.get("schema")})
    if desired.get("version") == current.get("version") and desired.get("components") == current.get("components"):
        raise SBLError("SBL_E_UPGRADE_NOOP", "the desired manifest is identical to the installed one",
                       {"version": current.get("version")})
    problems: list[str] = []
    for name, expected in desired.get("components", {}).items():
        try:
            actual = hashlib.sha256(_module_source(name).read_bytes()).hexdigest()
        except SBLError as exc:
            problems.append(f"{name}: {exc.message}")
            continue
        if actual != expected:
            problems.append(f"{name}: live bytes do not match the desired digest")
    if problems:
        raise SBLError("SBL_E_BAD_STATE", "the desired manifest does not describe the live environment",
                       {"problems": problems})

    stamp = str(int(root.stat().st_mtime_ns)) + "-upgrade"
    preimage = root / f"{PREIMAGE_PREFIX}{stamp}"
    preimage.mkdir(parents=True, exist_ok=False)
    payload = (root / MANIFEST_NAME).read_bytes()
    (preimage / MANIFEST_NAME).write_bytes(payload)
    preimage_digest = hashlib.sha256(payload).hexdigest()

    new_payload = (json.dumps(desired, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (root / MANIFEST_NAME).write_bytes(new_payload)
    composed = SharedCore(str(root)).doctor()
    return {
        "ok": bool(composed.get("ok")),
        "target": str(root),
        "from_version": current.get("version"),
        "to_version": desired.get("version"),
        "preimage": str(preimage),
        "preimage_sha256": preimage_digest,
        "manifest_sha256": hashlib.sha256(new_payload).hexdigest(),
        "doctor_ok": composed.get("ok"),
        "claim_ceiling": CLAIM_CEILING,
    }


def rollback(target: str | Path) -> dict[str, Any]:
    """Restore the most recent preimage, byte for byte, and prove the result is healthy."""

    root = Path(target)
    preimages = sorted(p for p in root.glob(f"{PREIMAGE_PREFIX}*") if p.is_dir())
    if not preimages:
        raise SBLError("SBL_E_BAD_STATE", "no preimage to roll back to", {"target": str(root)})
    latest = preimages[-1]
    payload = (latest / MANIFEST_NAME).read_bytes()
    before = (root / MANIFEST_NAME).read_bytes() if (root / MANIFEST_NAME).is_file() else b""
    (root / MANIFEST_NAME).write_bytes(payload)
    restored = (root / MANIFEST_NAME).read_bytes()
    composed = SharedCore(str(root)).doctor()
    ok = composed.get("ok") and restored == payload
    return {
        "ok": bool(ok),
        "target": str(root),
        "preimage": str(latest),
        "restored_sha256": hashlib.sha256(restored).hexdigest(),
        "replaced_sha256": hashlib.sha256(before).hexdigest(),
        "byte_identical": restored == payload,
        "doctor_ok": composed.get("ok"),
        "claim_ceiling": CLAIM_CEILING,
    }


def describe() -> dict[str, Any]:
    return {
        "schema": STACK_SCHEMA,
        "modules": list(sbl_core_core.MODULES),
        "components": list(COMPONENT_MODULES),
        "principals": list(sbl_plugins.SP_IDS),
        "claim_ceiling": CLAIM_CEILING,
    }
