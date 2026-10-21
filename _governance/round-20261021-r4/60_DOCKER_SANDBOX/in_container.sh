#!/usr/bin/env bash
# In-container acceptance for the candidate build. Runs in python:3.11-slim with /work mounted.
#
# What this proves: the wheel installs into a clean interpreter with no network and no
# pre-existing SBL, the stack surface (install/doctor/selftest/status/uninstall) works, the HGK
# adapter refuses an absent root instead of pretending, the three plugin packages validate against
# the vendored portable schema, and uninstall leaves no residue.
#
# What this does NOT prove: that any real host accepted the packages. There is no host in this
# container, so the "host" stage below is a simulation and is labelled as one.
set -u

RESULT=/work/SANDBOX_RESULT.json
WHEEL=$(ls /work/*.whl | head -1)
fail=0
note() { printf '%s\n' "$*" >&2; }

python -m venv /venv || { echo '{"ok":false,"stage":"venv","error":"create failed"}' > "$RESULT"; exit 9; }
/venv/bin/pip install --no-index --no-deps "$WHEEL" > /work/pip_install.log 2>&1 || {
  echo '{"ok":false,"stage":"pip_install"}' > "$RESULT"; exit 9; }

/venv/bin/python - <<'PY' > /work/SANDBOX_STEPS.jsonl
import json, shutil, subprocess, sys, zipfile, pathlib, os

steps = []
def run(name, argv, expect=0, cwd=None):
    proc = subprocess.run(argv, capture_output=True, text=True, cwd=cwd, timeout=180)
    ok = (proc.returncode == expect)
    steps.append({
        "step": name, "argv": argv, "rc": proc.returncode, "expected_rc": expect,
        "ok": ok, "stdout_head": proc.stdout[:600], "stderr_head": proc.stderr[:400],
    })
    return proc, ok

run("sbl-todo.init", ["/venv/bin/sbl-todo", "--data-dir", "/tmp/todo", "init"])
run("sbl-todo.add", ["/venv/bin/sbl-todo", "--data-dir", "/tmp/todo", "add", "--title", "sandbox item"])
run("sbl-todo.list", ["/venv/bin/sbl-todo", "--data-dir", "/tmp/todo", "list", "--json"])
run("sbl-stack.describe", ["/venv/bin/sbl-stack", "describe"])
run("sbl-stack.install", ["/venv/bin/sbl-stack", "install", "--root", "/tmp/stack"])
run("sbl-stack.doctor", ["/venv/bin/sbl-stack", "doctor", "--root", "/tmp/stack"])
run("sbl-stack.selftest", ["/venv/bin/sbl-stack", "selftest", "--workdir", "/tmp"])
run("sbl-stack.status", ["/venv/bin/sbl-stack", "status", "--root", "/tmp/stack"])

# NEG: a second install into the same non-empty directory must be refused, not silently merged.
run("NEG.stack.double-install", ["/venv/bin/sbl-stack", "install", "--root", "/tmp/stack"], expect=2)

# NEG: no HGK root inside this container -> the adapter must refuse, and install must write nothing.
run("NEG.harness.probe-missing", ["/venv/bin/sbl-harness", "probe", "--root", "/tmp/no-hgk"], expect=2)
run("NEG.harness.install-missing-root",
    ["/venv/bin/sbl-harness", "install", "--target", "/tmp/adapter", "--hgk-root", "/tmp/no-hgk"], expect=2)
steps.append({"step": "NEG.harness.install-wrote-nothing",
              "ok": not pathlib.Path("/tmp/adapter").exists(),
              "detail": "target must not exist after a refused install"})

# A synthetic HGK root proves the adapter install/doctor/uninstall path itself (not the native plane).
root = pathlib.Path("/tmp/fake-hgk")
(root / "src/hg_kseos").mkdir(parents=True, exist_ok=True)
(root / "src/hg_kseos/__init__.py").write_text('__version__ = "0.1.0"\n')
(root / "var/shared-spine").mkdir(parents=True, exist_ok=True)
(root / "var/shared-spine/hg-kseos.db").write_bytes(b"")
(root / "config").mkdir(exist_ok=True)
(root / "config/lane-route-slots.candidate.json").write_text("{}")
(root / "scripts").mkdir(exist_ok=True)
(root / "scripts/hgk-lane-dispatch.py").write_text("")
run("harness.probe-synthetic", ["/venv/bin/sbl-harness", "probe", "--root", "/tmp/fake-hgk"])
run("harness.install", ["/venv/bin/sbl-harness", "install", "--target", "/tmp/adapter",
                        "--hgk-root", "/tmp/fake-hgk"])
run("harness.doctor", ["/venv/bin/sbl-harness", "doctor", "--target", "/tmp/adapter"])
run("harness.uninstall", ["/venv/bin/sbl-harness", "uninstall", "--target", "/tmp/adapter"])
steps.append({"step": "harness.uninstalled-cleanly", "ok": not pathlib.Path("/tmp/adapter").exists()})

# Host-simulation stage: unpack each plugin into a host-like skills root and validate its bytes.
from sbl_sp.plugins import inspect_package, portable
host = pathlib.Path("/tmp/host/skills")
host.mkdir(parents=True, exist_ok=True)
for archive in sorted(pathlib.Path("/work").glob("sbl-*.zip")):
    report = inspect_package(archive)
    with zipfile.ZipFile(archive) as zf:
        manifest = json.loads(zf.read("plugin.json").decode("utf-8"))
        skill_paths = [n for n in zf.namelist() if n.startswith("skills/") and n.endswith("SKILL.md")]
        for sp in skill_paths:
            rel = sp.split("/")[1]
            target = host / rel
            target.mkdir(parents=True, exist_ok=True)
            (target / "SKILL.md").write_bytes(zf.read(sp))
        extracted = host / manifest["name"]
        extracted.mkdir(parents=True, exist_ok=True)
        (extracted / "plugin.json").write_bytes(zf.read("plugin.json"))
    steps.append({
        "step": "host.simulate." + manifest["name"],
        "ok": (manifest.get("$schema") == portable.CANONICAL_SCHEMA_URI
               and not report["schema_violations"] and not report["skill_violations"]),
        "sha256": report["sha256"],
        "entries": report["entries"],
        "schema_violations": report["schema_violations"],
        "skill_violations": report["skill_violations"],
        "note": "SIMULATED host: unpack + validate only, no host loader exists in this container",
    })

discovered = sorted(p.name for p in host.iterdir() if (p / "SKILL.md").is_file())
steps.append({"step": "host.simulate.discovery", "ok": len(discovered) == 3, "found": discovered})

# Teardown and residue.
run("stack.uninstall", ["/venv/bin/sbl-stack", "uninstall", "--root", "/tmp/stack"])
steps.append({"step": "stack.uninstalled-cleanly", "ok": not pathlib.Path("/tmp/stack").exists()})

uninstall = subprocess.run(["/venv/bin/pip", "uninstall", "-y", "sbl-v01"],
                           capture_output=True, text=True)
steps.append({"step": "pip.uninstall", "ok": uninstall.returncode == 0,
              "stdout_head": uninstall.stdout[:300], "stderr_head": uninstall.stderr[:300]})

site = [p.name for p in pathlib.Path("/venv/lib").glob("python3.*/site-packages/sbl*")]
steps.append({"step": "residue.site-packages", "ok": site == [], "found": site})
scripts = [p.name for p in pathlib.Path("/venv/bin").iterdir() if p.name.startswith("sbl-")]
steps.append({"step": "residue.console-scripts", "ok": scripts == [], "found": scripts})

for s in steps:
    print(json.dumps(s, ensure_ascii=False))
ok = all(s["ok"] for s in steps)
print(json.dumps({"step": "ALL", "ok": ok, "denominator": f"{sum(1 for s in steps if s['ok'])}/{len(steps)}"}))
sys.exit(0 if ok else 2)
PY
rc=$?

python - "$rc" <<'PY' > "$RESULT"
import json, sys, pathlib
rc = sys.argv[1]
lines = [json.loads(line) for line in pathlib.Path("/work/SANDBOX_STEPS.jsonl").read_text().splitlines() if line.strip()]
total = [s for s in lines if s.get("step") != "ALL"]
ok = rc == "0" and all(s["ok"] for s in total)
print(json.dumps({
    "ok": ok,
    "exit": int(rc),
    "denominator": f"{sum(1 for s in total if s['ok'])}/{len(total)}",
    "image": "python:3.11-slim",
    "host_stage": "SIMULATED",
    "steps": total,
}, ensure_ascii=False, indent=2))
PY
exit "$rc"
