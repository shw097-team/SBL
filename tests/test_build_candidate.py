"""The candidate build must be re-derivable from durable inputs.

The published 0.3.1-rc.1 was assembled by hand in a session directory: unzip the old
candidate, bump two manifests, drop in the reader's pin set, clean caches, zip. The artifact
is archived, but that recipe existed only in a transcript — which is exactly the "procedure
lives in a disposable layer" problem this round was supposed to close. These tests pin the
recipe down so a rebuild is a command, not an oral tradition.
"""
from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "integrations" / "pipd" / "tools" / "build_tpm_sp_candidate.py"


def pin_set(tmp: Path, files: dict[str, str] | None = None) -> Path:
    files = files or {"src/pipd_ls_sp/cli.py": "a" * 64, "schemas/PI.schema.json": "b" * 64}
    payload = {
        "schema": "SBL.ORIGINAL_READER_PINS@1",
        "reader_root": "integrations/pipd",
        "git_head": "a5d3a7676384d0e1124bc898b3f9596e5455f276",
        "file_count": len(files),
        "pin_set_sha256": "c" * 64,
        "files": files,
    }
    path = tmp / "READER_PINS.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def tree(tmp: Path, version: str = "0.3.0-rc.2") -> Path:
    root = tmp / "sbl-tpm-sp"
    (root / ".codex-plugin").mkdir(parents=True)
    (root / "skills").mkdir()
    (root / "skills" / "SKILL.md").write_text("# skill\n", encoding="utf-8")
    for rel in ("plugin.json", ".codex-plugin/plugin.json"):
        (root / rel).write_text(json.dumps({"name": "sbl-tpm-sp", "version": version}), encoding="utf-8")
    return root


def run(root: Path, pins: Path, out: Path, version: str = "0.3.1-rc.1",
        signature: Path | None = None, normalise: bool = False) -> tuple[int, dict]:
    cmd = [sys.executable, str(TOOL), "--tree", str(root), "--version", version,
           "--pins", str(pins), "--out", str(out)]
    if signature is not None:
        cmd += ["--signature", str(signature)]
    if normalise:
        cmd += ["--normalise-timestamps"]
    proc = subprocess.run(cmd, capture_output=True, timeout=180)
    return proc.returncode, json.loads(proc.stdout.decode("utf-8", "replace") or "{}")


def test_pos_bumps_both_manifests_and_embeds_pins(tmp_path: Path) -> None:
    code, body = run(tree(tmp_path), pin_set(tmp_path), tmp_path / "out.zip")
    assert code == 0, body
    assert body["version"] == "0.3.1-rc.1"
    assert set(body["manifests"]) == {"plugin.json", ".codex-plugin/plugin.json"}
    assert body["pins"]["file_count"] == 2
    assert body["bytecode"] == 0
    # mtimes are an INPUT by documented design (evidence/pp261103/close/CLOSEOUT_031RC1.md:68), so the
    # default build is not clock-independent and says so.
    assert body["normalised"] is False
    with zipfile.ZipFile(tmp_path / "out.zip") as zf:
        names = set(zf.namelist())
        manifest = json.loads(zf.read("sbl-tpm-sp/plugin.json"))
        nested = json.loads(zf.read("sbl-tpm-sp/.codex-plugin/plugin.json"))
    assert "sbl-tpm-sp/references/reader-pins/READER_PINS.json" in names
    assert manifest["version"] == nested["version"] == "0.3.1-rc.1"


def test_pos_same_inputs_give_the_same_digest(tmp_path: Path) -> None:
    """Same inputs -> same digest, asked in the mode whose inputs exclude the wall clock.

    The default build stamps members with their mtimes, and the tool rewrites two members on every
    run, so two default builds that straddle a 2-second DOS-timestamp boundary legitimately differ —
    that is the documented behaviour, not a defect (CLOSEOUT_031RC1.md:68). Asserting determinism
    therefore has to request `--normalise-timestamps`; asserting it on the default mode made this test
    depend on how fast the runner happened to be.
    """
    root, pins = tree(tmp_path), pin_set(tmp_path)
    first = run(root, pins, tmp_path / "a.zip", normalise=True)[1]
    second = run(root, pins, tmp_path / "b.zip", normalise=True)[1]
    assert first["normalised"] is True and second["normalised"] is True
    assert first["sha256"] == second["sha256"]
    assert first["members"] == second["members"]


def test_pos_bytecode_never_reaches_the_artifact(tmp_path: Path) -> None:
    root = tree(tmp_path)
    (root / "skills" / "__pycache__").mkdir()
    (root / "skills" / "__pycache__" / "x.pyc").write_bytes(b"\x00")
    (root / "stale.pyo").write_bytes(b"\x00")
    code, body = run(root, pin_set(tmp_path), tmp_path / "out.zip")
    assert code == 0, body
    assert body["bytecode"] == 0
    with zipfile.ZipFile(tmp_path / "out.zip") as zf:
        assert not any("__pycache__" in n or n.endswith((".pyc", ".pyo")) for n in zf.namelist())


def test_neg_pin_count_must_match_the_listed_files(tmp_path: Path) -> None:
    pins = pin_set(tmp_path)
    payload = json.loads(pins.read_text(encoding="utf-8"))
    payload["file_count"] = 99
    pins.write_text(json.dumps(payload), encoding="utf-8")
    code, body = run(tree(tmp_path), pins, tmp_path / "out.zip")
    assert code == 2
    assert body["code"] == "PINS_COUNT_MISMATCH"


def test_neg_signature_for_a_different_pin_set_is_refused(tmp_path: Path) -> None:
    sig = tmp_path / "sig.json"
    sig.write_text(json.dumps({"pin_set_sha256": "d" * 64, "signature_hex": "00"}), encoding="utf-8")
    code, body = run(tree(tmp_path), pin_set(tmp_path), tmp_path / "out.zip", signature=sig)
    assert code == 2
    assert body["code"] == "SIGNATURE_DIGEST_MISMATCH"


def test_neg_tree_without_a_manifest_is_refused(tmp_path: Path) -> None:
    empty = tmp_path / "empty"
    empty.mkdir()
    code, body = run(empty, pin_set(tmp_path), tmp_path / "out.zip")
    assert code == 2
    assert body["code"] == "NOT_A_PLUGIN_TREE"


def test_neg_manifest_for_another_plugin_is_refused(tmp_path: Path) -> None:
    root = tree(tmp_path)
    (root / "plugin.json").write_text(json.dumps({"name": "someone-else"}), encoding="utf-8")
    code, body = run(root, pin_set(tmp_path), tmp_path / "out.zip")
    assert code == 2
    assert body["code"] == "MANIFEST_NAME_MISMATCH"
