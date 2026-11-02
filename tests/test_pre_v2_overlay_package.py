"""The published private-overlay snapshot must carry the repaired BOM ordering.

The overlay is a partial copy of the private package that ships in
``sbl-tpm-sp-*.zip``. Nothing else in this repo imports it, so before this test the
snapshot could silently keep the pre-repair ``sorted(root.rglob(...))`` collector
and disagree with the sealed archive. CR-06 records the defect: ``sorted(Path)`` is
casefolded on Windows and byte-ordered on POSIX, so a BOM built on one OS failed
``validate_bom`` on the other.

This test loads the overlay modules by file path (they are plain modules, not a
package on ``sys.path``) and pins the behaviour, not the implementation.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import pytest

OVERLAY = (Path(__file__).resolve().parents[1] / "sbl_sp" / "plugins" / "tpm_sp"
           / "pre_v2" / "private-overlay" / "scripts")


def _load(name: str):
    if str(OVERLAY) not in sys.path:
        sys.path.insert(0, str(OVERLAY))
    spec = importlib.util.spec_from_file_location(f"_overlay_{name}", OVERLAY / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"_overlay_{name}"] = module
    spec.loader.exec_module(module)
    return module


def test_overlay_snapshot_is_present_and_self_consistent() -> None:
    for name in ("core.py", "package_preflight.py", "refresh_bom.py",
                 "run_author_tests.py"):
        assert (OVERLAY / name).is_file(), f"overlay snapshot is missing {name}"


def test_overlay_inventory_order_is_platform_independent(tmp_path: Path) -> None:
    core = _load("core")
    for name in ("B.txt", "a.txt", "C.txt", "d/x.txt"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"x")
    ordered = [p.relative_to(tmp_path).as_posix()
               for p in core.canonical_order(tmp_path, [p for p in tmp_path.rglob("*")
                                                        if p.is_file()])]
    assert ordered == ["a.txt", "B.txt", "C.txt", "d/x.txt"]


def test_overlay_validate_bom_refuses_one_byte_drift(tmp_path: Path) -> None:
    _load("core")
    preflight = _load("package_preflight")
    raw = b"candidate"
    (tmp_path / "sbom").mkdir()
    (tmp_path / "sbom" / "manifest.json").write_text(json.dumps({
        "schema": "SBL.AdmittedEquivalentBOM@1",
        "version": "0.3.0-rc.2",
        "files": [{"path": "candidate.txt",
                   "sha256": hashlib.sha256(raw).hexdigest(),
                   "bytes": len(raw)}]}), encoding="utf-8")
    preflight.validate_bom(tmp_path, {"version": "0.3.0-rc.2"}, [("candidate.txt", raw)])
    with pytest.raises(Exception) as excinfo:
        preflight.validate_bom(tmp_path, {"version": "0.3.0-rc.2"},
                               [("candidate.txt", b"candidatf")])
    assert "BOM_FILE_DRIFT" in str(excinfo.value)
