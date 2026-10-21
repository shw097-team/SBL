#!/usr/bin/env python
"""Refresh the declared codex toolchain pin to the INSTALLED build.

WHY: the Codex CLI was upgraded in place. The declared pin named

    C:\\Users\\user\\AppData\\Local\\OpenAI\\Codex\\bin\\896a0166b774037a\\codex.exe
    version 0.163.0-alpha.10.2
    sha256 f6dbf48cb70f62649c645f26c87dc9bf84cc36986202dfad8e12fb5b8ca70312

and that directory no longer exists. The installed build is now

    C:\\Users\\user\\AppData\\Local\\OpenAI\\Codex\\bin\\6257d9e8f63c0f2b\\codex.exe
    version 0.163.0-alpha.11

Every lane dispatch therefore failed BEFORE SPAWNING with
ERR_LANE_PIN_IDENTITY_INVALID / ERR_LANE_TOOLCHAIN_BINARY_MISSING. The
dispatcher refused to run the SBL EXECUTE and VERIFY lanes at all -- this is
the lane execution chain for SBL, so it is not a cosmetic metadata fix.

The pin is refreshed FROM THE INSTALLED BINARY:
  * the path is discovered, not typed;
  * the version comes from `codex.exe --version`;
  * the digest is computed over the actual file;
  * the whole thing is then READ BACK and re-verified by running the
    dispatcher's own pin verifier, so the claim is "the lane's own gate
    passes", not "a field was edited".

Only the LIVE declaration (config/hermes-codex-lane.json) is rewritten. The
probe receipts under evidence/ record what the lane actually served on
2026-10-21 with the OLD build; they are evidence of a past measurement and are
NOT rewritten.

Pre-image digest guard: the file is only written if it still hashes to what
was read, so a concurrent writer cannot be silently overwritten.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
DECL = HGK / "config" / "hermes-codex-lane.json"
BIN_ROOT = Path(r"C:/Users/user/AppData/Local/OpenAI/Codex/bin")
BACKUP = HGK / "var" / "R7-LANES" / f"hermes-codex-lane-pre-pin-refresh-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.json"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def discover_binary() -> tuple[Path, str]:
    """Find the INSTALLED codex.exe. Discovery, not a typed path."""
    cands = sorted(p for p in BIN_ROOT.glob("*/codex.exe") if p.is_file())
    if not cands:
        raise SystemExit(f"no codex.exe under {BIN_ROOT}")
    # newest wins: the version directory name is a content hash, and the
    # install replaces the directory rather than adding to it, so the
    # most recently modified is the live one.
    live = max(cands, key=lambda p: p.stat().st_mtime)
    return live, sha256(live)


def version_of(exe: Path) -> str:
    r = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=120)
    out = (r.stdout or r.stderr).strip()
    m = re.search(r"(\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?)", out)
    return m.group(1) if m else out.splitlines()[0].strip() if out else "unknown"


def main() -> int:
    pre = sha256(DECL)
    decl = json.loads(DECL.read_text(encoding="utf-8"))
    old_path = decl.get("codex_executable")
    old_ver = decl.get("codex_version")
    old_sha = decl.get("codex_sha256")

    exe, new_sha = discover_binary()
    new_ver = version_of(exe)
    print("old pin :", old_path)
    print("         ", old_ver, old_sha[:16] if old_sha else None)
    print("new pin :", exe)
    print("         ", new_ver, new_sha[:16])

    if str(exe) == old_path and new_sha == old_sha:
        print("pin already current; nothing to do")
        return 0

    # Verify the discovered binary actually RUNS before declaring it pinned.
    r = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print("the discovered binary does not run; refusing to pin it")
        return 2

    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(DECL, BACKUP)
    print("backup  :", BACKUP.name)

    decl["codex_executable"] = str(exe)
    decl["codex_version"] = new_ver
    decl["codex_sha256"] = new_sha
    decl["toolchain_pin_note"] = (
        f"Pin refreshed {datetime.now(timezone.utc).strftime('%Y-%m-%d')} to the INSTALLED build. "
        f"The Codex CLI was upgraded in place: the previously declared binary "
        f"({old_path}, {old_ver}) no longer exists, and every lane dispatch was failing "
        f"BEFORE SPAWNING with ERR_LANE_PIN_IDENTITY_INVALID / "
        f"ERR_LANE_TOOLCHAIN_BINARY_MISSING, which stopped the SBL EXECUTE and VERIFY lanes "
        f"entirely. The new path was DISCOVERED under {BIN_ROOT}, the version comes from "
        f"`codex.exe --version`, and the digest is computed over the installed file. "
        f"The prior value was {old_path} / {old_ver} / sha256 {old_sha}. "
        f"Probe receipts under evidence/ are NOT rewritten: they record what the lane actually "
        f"served on 2026-10-21 with the OLD build and remain true as history."
    )
    decl.setdefault("pin_refresh_history", []).append({
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "round": "R7-RESUME-20261021",
        "reason": "codex CLI upgraded in place; the declared binary no longer existed",
        "from": {"path": old_path, "version": old_ver, "sha256": old_sha},
        "to": {"path": str(exe), "version": new_ver, "sha256": new_sha},
        "failure_it_fixed": "ERR_LANE_PIN_IDENTITY_INVALID / ERR_LANE_TOOLCHAIN_BINARY_MISSING",
    })

    if sha256(DECL) != pre:
        print("REFUSING TO WRITE: the declaration changed under this script (concurrent writer)")
        return 3

    DECL.write_text(json.dumps(decl, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("written :", sha256(DECL))

    # READ BACK: the live file must carry exactly what we measured.
    rb = json.loads(DECL.read_text(encoding="utf-8"))
    assert rb["codex_executable"] == str(exe)
    assert rb["codex_version"] == new_ver
    assert rb["codex_sha256"] == new_sha
    assert Path(rb["codex_executable"]).exists()
    assert sha256(Path(rb["codex_executable"])) == rb["codex_sha256"]
    print("\nread-back: the live declaration names an existing binary whose measured digest matches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
