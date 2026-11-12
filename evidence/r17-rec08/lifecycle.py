#!/usr/bin/env python3
"""REC08 F3-d — real lifecycle for the three generated Kinds.

Each verb returns a typed, raw-carrying result. Nothing here reports success from a filename:
`install` re-reads what landed, `invoke` records stdout/stderr/exit, `deny` proves the refusal
path, `uninstall` proves absence of residue.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PY = sys.executable


def _run(cmd: list[str], cwd: Path | None = None, timeout: int = 240) -> dict:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    return {"cmd": cmd, "exit": p.returncode, "stdout": p.stdout[-4000:], "stderr": p.stderr[-2000:]}


def _sha_dir(root: Path) -> dict:
    out = {}
    for f in sorted(root.rglob("*")):
        if f.is_file():
            out[str(f.relative_to(root)).replace("\\", "/")] = hashlib.sha256(f.read_bytes()).hexdigest()
    return out


# ------------------------------------------------------------------ CLI_TOOL
def cli_install(project: Path, dist: str, prefix: Path) -> dict:
    venv = prefix / "venv"
    venv.mkdir(parents=True, exist_ok=True)
    r = {"kind": "CLI_TOOL", "verb": "install", "dist": dist, "prefix": str(prefix)}
    r["venv"] = _run([PY, "-m", "venv", str(venv)])
    vpy = venv / "Scripts" / "python.exe"
    if not vpy.is_file():
        return {**r, "ok": False, "code": "VENV_UNCREATED"}
    # offline, backend from the venv itself: no network, no silent download of a build backend.
    r["pip"] = _run([str(vpy), "-m", "pip", "install", "--no-build-isolation", "--no-index",
                     "-q", str(project)])
    entry = venv / "Scripts" / f"{dist}.exe"
    r["entrypoint"] = str(entry)
    r["entrypoint_exists"] = entry.is_file()
    site = sorted((venv / "Lib" / "site-packages").glob(f"{dist.replace('-', '_')}-*"))
    r["installed_dist_info"] = [str(s.name) for s in site]
    r["ok"] = bool(r["pip"]["exit"] == 0 and r["entrypoint_exists"] and site)
    r["code"] = None if r["ok"] else "CLI_INSTALL_INCOMPLETE"
    return r


def cli_invoke(entry: Path, args: list[str], stdin: str | None = None) -> dict:
    p = subprocess.run([str(entry), *args], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", input=stdin, timeout=120)
    return {"verb": "invoke", "args": args, "exit": p.returncode,
            "stdout": p.stdout, "stderr": p.stderr}


def cli_uninstall(prefix: Path, dist: str) -> dict:
    vpy = prefix / "venv" / "Scripts" / "python.exe"
    r = {"kind": "CLI_TOOL", "verb": "uninstall", "prefix": str(prefix)}
    r["pip_uninstall"] = _run([str(vpy), "-m", "pip", "uninstall", "-y", "-q", dist]) if vpy.is_file() else {}
    entry = prefix / "venv" / "Scripts" / f"{dist}.exe"
    r["entrypoint_gone_before_teardown"] = not entry.is_file()
    shutil.rmtree(prefix, ignore_errors=True)
    r["residue"] = prefix.exists()
    r["ok"] = r["entrypoint_gone_before_teardown"] and not r["residue"]
    r["code"] = None if r["ok"] else "CLI_UNINSTALL_RESIDUE"
    return r


# ------------------------------------------------------------------ AGENT_SKILL
FRONT = re.compile(r"^---\n(.*?)\n---\n", re.S)


def skill_discover(host_dir: Path) -> dict:
    """A skill is discovered only if the HOST-side tree yields parseable frontmatter."""
    found = []
    for md in sorted(host_dir.glob("*/SKILL.md")):
        text = md.read_text(encoding="utf-8", errors="replace")
        m = FRONT.match(text)
        if not m:
            found.append({"path": str(md), "parsed": False, "reason": "NO_FRONTMATTER"})
            continue
        head = m.group(1)
        name = re.search(r"^name:\s*(\S+)", head, re.M)
        desc = re.search(r"^description:\s*(.+)$", head, re.M)
        trig = re.findall(r"^\s+-\s+(.+)$", head.split("triggers:", 1)[1], re.M) if "triggers:" in head else []
        found.append({"path": str(md), "parsed": bool(name and desc),
                      "name": name.group(1) if name else None,
                      "description": desc.group(1).strip() if desc else None,
                      "triggers": [t.strip() for t in trig]})
    return {"verb": "discover", "host_dir": str(host_dir), "skills": found,
            "discovered": [f["name"] for f in found if f.get("parsed")]}


def skill_match(skill: dict, utterance: str) -> bool:
    """Deterministic trigger match: a trigger phrase must appear as a substring, case-folded."""
    u = utterance.casefold()
    return any(t.casefold() in u for t in skill.get("triggers", []))


def skill_install(src: Path, host_dir: Path) -> dict:
    name = src.name
    dst = host_dir / name
    host_dir.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    disc = skill_discover(host_dir)
    mine = next((s for s in disc["skills"] if Path(s["path"]).parent.name == name), None)
    r = {"kind": "AGENT_SKILL", "verb": "install", "src": str(src), "dst": str(dst),
         "files": sorted(_sha_dir(dst)), "discovery": mine}
    r["ok"] = bool(mine and mine.get("parsed"))
    r["code"] = None if r["ok"] else "SKILL_NOT_DISCOVERED"
    return r


def skill_uninstall(host_dir: Path, name: str) -> dict:
    dst = host_dir / name
    shutil.rmtree(dst, ignore_errors=True)
    r = {"kind": "AGENT_SKILL", "verb": "uninstall", "path": str(dst),
         "residue": dst.exists(), "still_discovered": name in skill_discover(host_dir)["discovered"]}
    r["ok"] = (not r["residue"]) and (not r["still_discovered"])
    r["code"] = None if r["ok"] else "SKILL_UNINSTALL_RESIDUE"
    return r


# ------------------------------------------------------------------ SIMPLE_AGENT
def agent_install(src: Path, host_dir: Path) -> dict:
    name = src.name
    dst = host_dir / name
    host_dir.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    cfg = json.loads((dst / "agent.json").read_text(encoding="utf-8"))
    r = {"kind": "SIMPLE_AGENT", "verb": "install", "dst": str(dst),
         "files": sorted(_sha_dir(dst)),
         "allowlist": cfg["tools"]["allowed"], "denylist": cfg["tools"]["denied"],
         "stop_policy": cfg["stop_policy"]}
    r["ok"] = bool((dst / "runner.py").is_file() and cfg["stop_policy"]["self_directed_loop"] is False)
    r["code"] = None if r["ok"] else "AGENT_INSTALL_INCOMPLETE"
    return r


def agent_run(dst: Path, plan: list, work: Path, tag: str) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    plan_f, rec_f = work / f"{tag}.plan.json", work / f"{tag}.receipt.json"
    plan_f.write_text(json.dumps({"plan": plan}, ensure_ascii=False), encoding="utf-8")
    p = subprocess.run([PY, str(dst / "runner.py"), str(plan_f), str(rec_f)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=120)
    body = json.loads(p.stdout) if p.stdout.strip().startswith("{") else {}
    return {"verb": "run", "tag": tag, "exit": p.returncode,
            "stdout": p.stdout[-2000:], "stderr": p.stderr[-1000:],
            "receipt_path": str(rec_f), "receipt_exists": rec_f.is_file(), "receipt": body}


def agent_uninstall(host_dir: Path, name: str) -> dict:
    dst = host_dir / name
    shutil.rmtree(dst, ignore_errors=True)
    r = {"kind": "SIMPLE_AGENT", "verb": "uninstall", "path": str(dst), "residue": dst.exists()}
    r["ok"] = not r["residue"]
    r["code"] = None if r["ok"] else "AGENT_UNINSTALL_RESIDUE"
    return r
