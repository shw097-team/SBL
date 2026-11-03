"""The reader pin issuer must describe a committed tree, and only a committed one.

POS: a committed reader tree yields one pin per file, relative to the reader root, with a
stable set digest.
NEG: an untracked file, an uncommitted edit, and a missing reader folder are all refused,
because a pin set that describes bytes which are not at HEAD would drift on the next checkout.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "integrations" / "pipd" / "tools" / "issue_reader_pins.py"


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def make_reader(tmp: Path) -> Path:
    reader = tmp / "integrations" / "pipd"
    (reader / "src" / "pipd_ls_sp").mkdir(parents=True)
    (reader / "schemas").mkdir(parents=True)
    (reader / "src" / "pipd_ls_sp" / "cli.py").write_text("print('cli')\n", encoding="utf-8")
    (reader / "src" / "pipd_ls_sp" / "registry.py").write_text("EXPECTED = 1\n", encoding="utf-8")
    (reader / "schemas" / "ECP.schema.json").write_text('{"$id": "urn:x"}\n', encoding="utf-8")
    (tmp / "integrations").mkdir(exist_ok=True)
    subprocess.run(["git", "init", "-q"], cwd=tmp, check=True)
    git(tmp, "config", "core.autocrlf", "false")
    git(tmp, "config", "user.email", "pins@example.invalid")
    git(tmp, "config", "user.name", "pins")
    git(tmp, "add", "-A")
    git(tmp, "commit", "-q", "-m", "reader")
    return reader


def run(reader: Path) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, str(TOOL), "--reader-root", str(reader)],
                          capture_output=True, timeout=120)
    return proc.returncode, json.loads(proc.stdout.decode("utf-8", "replace") or "{}")


def test_pos_emits_one_pin_per_file(tmp_path: Path) -> None:
    reader = make_reader(tmp_path)
    code, body = run(reader)
    assert code == 0, body
    assert body["schema"] == "SBL.ORIGINAL_READER_PINS@1"
    assert body["reader_root"] == "integrations/pipd"
    assert body["git_dirty"] is False
    assert body["file_count"] == 3
    assert set(body["files"]) == {
        "schemas/ECP.schema.json",
        "src/pipd_ls_sp/cli.py",
        "src/pipd_ls_sp/registry.py",
    }
    assert len(body["pin_set_sha256"]) == 64
    # the digest is a function of (path, content) only
    code2, body2 = run(reader)
    assert code2 == 0 and body2["pin_set_sha256"] == body["pin_set_sha256"]


def test_neg_untracked_file_refused(tmp_path: Path) -> None:
    reader = make_reader(tmp_path)
    (reader / "src" / "pipd_ls_sp" / "operation_registry.py").write_text("new = 1\n", encoding="utf-8")
    code, body = run(reader)
    assert code == 2
    assert body["code"].startswith("READER_TREE_DIRTY")


def test_neg_uncommitted_edit_refused(tmp_path: Path) -> None:
    reader = make_reader(tmp_path)
    (reader / "src" / "pipd_ls_sp" / "cli.py").write_text("print('edited')\n", encoding="utf-8")
    code, body = run(reader)
    assert code == 2
    assert body["code"].startswith("READER_TREE_DIRTY")


def test_neg_missing_folder_refused(tmp_path: Path) -> None:
    reader = make_reader(tmp_path)
    for f in (reader / "schemas").iterdir():
        f.unlink()
    (reader / "schemas").rmdir()
    # commit the deletion: a clean tree with a missing folder is the case under test,
    # otherwise the dirty guard fires first (which is also correct, just a different code).
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "drop schemas")
    code, body = run(reader)
    assert code == 2
    assert body["code"] == "READER_FOLDER_MISSING:schemas"
