#!/usr/bin/env python3
"""Owner-authorised local install onto this machine's Hermes host.

Order matters and is enforced here: the rollback point must already exist, the wheel must install
into a fresh venv with ``--no-index --no-deps`` (so a network dependency cannot mask a missing
package-data entry), the stack and adapter must pass their own doctor, and only then are the five
skill surfaces copied into ``HERMES_HOME/skills/sbl``.

Nothing here claims a host accepted anything. The receipt records exactly which digests were written
where, and the effective-load check is a separate command whose output is appended to the receipt.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERMES_HOME = Path(
    os.environ.get(
        "HERMES_HOME",
        r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes",
    )
)
INSTALL_ROOT = Path(r"C:\Projects\Agent_Workspace\SBL-install")
DIST = Path(r"C:\Projects\_sbl_r4\dist")
PLUGIN_ZIPS = Path(r"C:\Projects\_sbl_r4\sandbox")
HGK_ROOT = Path(r"C:\Projects\Agent_Workspace\HG-KSEOS")
ROUND = Path(__file__).resolve().parent
SKILL_CATEGORY = HERMES_HOME / "skills" / "sbl"
PY = r"C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(argv: list[str], **kwargs) -> dict:
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=600, **kwargs)
    return {
        "argv": argv,
        "rc": proc.returncode,
        "stdout_head": proc.stdout[:800],
        "stderr_head": proc.stderr[:800],
    }


def main() -> int:
    receipt: dict = {"schema": "SBL-ROUND-R4-LOCAL-INSTALL/1", "steps": []}

    rollback = ROUND.parent / "90_HERMES_ROLLBACK" / "ROLLBACK_MANIFEST.json"
    if not rollback.is_file():
        print("no rollback point: refusing to install", file=sys.stderr)
        return 2
    receipt["rollback_point"] = json.loads(rollback.read_text(encoding="utf-8"))["archive"]

    wheel = sorted(DIST.glob("*.whl"))[-1]
    receipt["wheel"] = {"path": wheel.name, "bytes": wheel.stat().st_size, "sha256": sha256(wheel)}

    if INSTALL_ROOT.exists() and any(INSTALL_ROOT.iterdir()):
        print(f"{INSTALL_ROOT} is not empty; refusing to reuse it", file=sys.stderr)
        return 2
    INSTALL_ROOT.mkdir(parents=True, exist_ok=True)

    venv = INSTALL_ROOT / ".venv"
    receipt["steps"].append(run([PY, "-m", "venv", str(venv)]))
    vpy = venv / "Scripts" / "python.exe"
    pip = [str(vpy), "-m", "pip"]
    receipt["steps"].append(dict(run(pip + ["install", "--no-index", "--no-deps", str(wheel)]),
                                 step="pip.install"))

    stack_root = INSTALL_ROOT / "stack"
    adapter_root = INSTALL_ROOT / "hgk-adapter"
    for name, argv in (
        ("stack.install", [str(venv / "Scripts" / "sbl-stack.exe"), "install", "--root", str(stack_root)]),
        ("stack.doctor", [str(venv / "Scripts" / "sbl-stack.exe"), "doctor", "--root", str(stack_root)]),
        ("stack.selftest", [str(venv / "Scripts" / "sbl-stack.exe"), "selftest", "--workdir", str(INSTALL_ROOT)]),
        ("harness.install",
         [str(venv / "Scripts" / "sbl-harness.exe"), "install", "--target", str(adapter_root),
          "--hgk-root", str(HGK_ROOT)]),
        ("harness.doctor", [str(venv / "Scripts" / "sbl-harness.exe"), "doctor", "--target", str(adapter_root)]),
    ):
        step = run(argv)
        step["step"] = name
        receipt["steps"].append(step)

    installed: list[dict] = []
    SKILL_CATEGORY.mkdir(parents=True, exist_ok=True)

    for archive in sorted(PLUGIN_ZIPS.glob("sbl-*.zip")):
        with zipfile.ZipFile(archive) as zf:
            manifest = json.loads(zf.read("plugin.json").decode("utf-8"))
            skill_members = [n for n in zf.namelist() if n.startswith("skills/") and n.endswith("SKILL.md")]
            for member in skill_members:
                skill = member.split("/")[1]
                target = SKILL_CATEGORY / skill
                target.mkdir(parents=True, exist_ok=True)
                written = []
                for rel, payload in (
                    ("SKILL.md", zf.read(member)),
                    ("plugin.json", zf.read("plugin.json")),
                    ("README.md", zf.read("README.md")),
                ):
                    path = target / rel
                    path.write_bytes(payload)
                    written.append({"file": rel, "sha256": hashlib.sha256(payload).hexdigest()})
                installed.append(
                    {
                        "tool": manifest["name"],
                        "kind": "agent-skill",
                        "path": str(target),
                        "source_zip": archive.name,
                        "source_zip_sha256": sha256(archive),
                        "files": written,
                    }
                )

    # The HGK adapter's own skill, taken from the installed adapter (same bytes, one source).
    adapter_skill_src = adapter_root / "skills" / "hgk-governed-runtime" / "SKILL.md"
    if adapter_skill_src.is_file():
        target = SKILL_CATEGORY / "hgk-governed-runtime"
        target.mkdir(parents=True, exist_ok=True)
        body = adapter_skill_src.read_bytes()
        (target / "SKILL.md").write_bytes(body)
        shutil.copy2(adapter_root / "adapter.json", target / "adapter.json")
        shutil.copy2(adapter_root / "plugin.json", target / "plugin.json")
        installed.append(
            {
                "tool": "sbl-hgk-harness",
                "kind": "agent-skill",
                "path": str(target),
                "source_zip": None,
                "files": [{"file": "SKILL.md", "sha256": hashlib.sha256(body).hexdigest()}],
            }
        )

    stack_skill_src = venv / "Lib" / "site-packages" / "sbl_stack" / "SKILL.md"
    if stack_skill_src.is_file():
        target = SKILL_CATEGORY / "sbl-stack"
        target.mkdir(parents=True, exist_ok=True)
        body = stack_skill_src.read_bytes()
        (target / "SKILL.md").write_bytes(body)
        installed.append(
            {
                "tool": "sbl-stack",
                "kind": "agent-skill",
                "path": str(target),
                "source_zip": None,
                "files": [{"file": "SKILL.md", "sha256": hashlib.sha256(body).hexdigest()}],
            }
        )

    receipt["installed"] = installed
    receipt["install_root"] = str(INSTALL_ROOT)
    receipt["hermes_skills_category"] = str(SKILL_CATEGORY)
    receipt["claim_ceiling"] = "LOCAL_STANDALONE_INSTALL"
    # Two different facts, deliberately not merged: this machine now has the artefacts, and no host
    # has accepted them. The stack's own manifest says NOT_INSTALLED for the same reason.
    receipt["local_install_state"] = "INSTALLED_ON_THIS_MACHINE"
    receipt["host_acceptance"] = "NOT_HOST_ACCEPTED"
    receipt["effective_load"] = "SEE EFFECTIVE_LOAD STEP"
    (ROUND / "INSTALL_RECEIPT.json").write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    bad = [s for s in receipt["steps"] if s["rc"] != 0]
    print(json.dumps({"steps": len(receipt["steps"]), "failed": [s.get("step") for s in bad],
                      "installed": len(installed)}, indent=2))
    for step in bad:
        print(step.get("step"), step["stderr_head"][:300], file=sys.stderr)
    return 0 if not bad else 2


if __name__ == "__main__":
    raise SystemExit(main())
