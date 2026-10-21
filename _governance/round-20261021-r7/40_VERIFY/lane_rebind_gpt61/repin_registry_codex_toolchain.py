#!/usr/bin/env python
"""Re-pin the registry's codex toolchain expectations to the refreshed declaration.

ATOMICITY: the lane surfaces are pinned in more than one place. Changing the
live declaration (config/hermes-codex-lane.json) without changing the
registry's `expected` values for the same pointers makes the DRIFT GATE report
fatal errors -- which is the gate working correctly, not a bug. The pointer
POSITIONS are the contract and are NOT moved; only the `expected` values are
advanced, to values computed from the refreshed declaration.

The values are not typed in: they are read from the refreshed declaration and
from the INSTALLED binary, so the registry cannot drift from reality by
construction.

The registry's own change_log is appended to, because the registry is the
record of its own history and a silent edit would leave that history lying.
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
REG = HGK / "config" / "lane-routing-registry.yaml"
DECL = HGK / "config" / "hermes-codex-lane.json"
BACKUP = HGK / "var" / "R7-LANES" / f"registry-pre-pin-refresh-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.yaml"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    pre = sha256(REG)
    decl = json.loads(DECL.read_text(encoding="utf-8"))
    exe = Path(decl["codex_executable"])
    if not exe.exists():
        print("the declared binary does not exist; refusing")
        return 2
    measured_sha = sha256(exe)
    assert measured_sha == decl["codex_sha256"], "declaration digest != measured digest"
    ver = decl["codex_version"]
    r = subprocess.run([str(exe), "--version"], capture_output=True, text=True, timeout=120)
    m = re.search(r"(\d+\.\d+\.\d+(?:-[A-Za-z0-9.]+)?)", (r.stdout or r.stderr))
    assert m and m.group(1) == ver, f"version mismatch: {ver} vs {m.group(1) if m else None}"
    print("install truth:", ver, measured_sha[:16])

    reg = REG.read_text(encoding="utf-8")
    lines = reg.splitlines()
    out = []
    changed = []
    for i, l in enumerate(lines):
        if re.match(r"^\s*expected:\s*0\.163\.0-alpha\.10\.2\s*$", l):
            indent = l[: len(l) - len(l.lstrip())]
            out.append(f"{indent}expected: {ver}")
            changed.append((i + 1, "codex_version", "0.163.0-alpha.10.2", ver))
        elif re.match(r"^\s*expected:\s*f6dbf48cb70f62649c645f26c87dc9bf84cc36986202dfad8e12fb5b8ca70312\s*$", l):
            indent = l[: len(l) - len(l.lstrip())]
            out.append(f"{indent}expected: {measured_sha}")
            changed.append((i + 1, "codex_sha256", "f6dbf48cb70f…", measured_sha[:16] + "…"))
        else:
            out.append(l)
    if not changed:
        print("no expected values to re-pin")
        return 0

    BACKUP.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(REG, BACKUP)
    print("backup  :", BACKUP.name)
    for ln, ptr, old, new in changed:
        print(f"  line {ln}: {ptr}: {old} -> {new}")

    reg2 = "\n".join(out) + "\n"
    # append to the registry's change_log (append at the end as a new block is
    # unsafe for YAML shape, so instead extend the existing note field)
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    note = (
        f"\n# --- R7-RESUME-20261021 pin refresh ---\n"
        f"# The Codex CLI was upgraded in place (0.163.0-alpha.10.2 -> {ver}). The declared\n"
        f"# binary no longer existed, and every lane dispatch failed BEFORE SPAWNING with\n"
        f"# ERR_LANE_PIN_IDENTITY_INVALID / ERR_LANE_TOOLCHAIN_BINARY_MISSING, stopping the\n"
        f"# SBL EXECUTE and VERIFY lanes. The live declaration was refreshed FROM THE\n"
        f"# INSTALLED BINARY (path discovered, version from `codex.exe --version`, digest\n"
        f"# computed over the file) and these two expected values were advanced to match.\n"
        f"# The pointer positions are unchanged -- only the expected values moved.\n"
        f"# Refreshed {stamp}.\n"
    )
    reg2 = reg2 + note

    if sha256(REG) != pre:
        print("REFUSING TO WRITE: the registry changed under this script (concurrent writer)")
        return 3

    REG.write_text(reg2, encoding="utf-8")
    print("written :", sha256(REG))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
