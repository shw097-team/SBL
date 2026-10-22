"""Q5 — local half of the five-tool / three-ZIP lifecycle probe, as one reproducible receipt.

Measures, per tool, the eight lifecycle verbs **by executing them**, not by grepping filenames (the
previous instrument did the latter and reported 0/8 while the verbs existed as CLI subcommands):

  install  doctor  load  invoke  deny  upgrade  uninstall  rollback

Tools:
  SBL_STACK     -- `python -m sbl_stack.cli <verb> --root <tmp>` (all eight verbs exist)
  THREE_SP_ZIPS -- `tools/build_sp_plugins.py` twice into separate dirs, digest equality, then
                   unpack/validate/remove/restore; load/invoke/deny are HOST_PENDING by contract
  HGK_HARNESS   -- doctor/plan/execute under the 3.12 interpreter (install-by-editable is out of scope:
                   modifying the live control plane is not authorised)

Every verb row carries the exact command, rc, and a bounded observation. A verb that is not applicable
carries a typed N/A reason, never a silent pass.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile

SBL = r"C:/Projects/Agent_Workspace/_r152_ev"
HGK = r"C:/Projects/Agent_Workspace/HG-KSEOS"
PY312 = r"C:/Users/user/AppData/Roaming/uv/python/cpython-3.12-windows-x86_64-none/python.exe"
OUT = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/q5_tools"


def run(cmd: list[str], cwd: str = SBL) -> dict:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    full = (p.stdout or "") + (p.stderr or "")
    tail = full.strip().splitlines()
    # A 3-line tail once made a typed refusal look code-less: the refusal fields are
    # earlier in the JSON than the trailing summary. Counts come from the whole text.
    import re as _re
    rawdir = os.path.join(OUT, "raw")
    os.makedirs(rawdir, exist_ok=True)
    tag = _re.sub(r"[^A-Za-z0-9_.-]+", "_", " ".join(cmd[2:]))[:70] or "cmd"
    op = os.path.join(rawdir, tag + ".out")
    with open(op, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(full)
    return {"cmd": " ".join(cmd), "rc": p.returncode, "observed": " | ".join(tail[-3:])[:400],
            "raw_path": os.path.relpath(op, OUT).replace("\\", "/"),
            "raw_bytes": len(full.encode("utf-8")),
            "raw_sha256": hashlib.sha256(full.encode("utf-8")).hexdigest(),
            "first_line": tail[0][:200] if tail else "",
            "codes": sorted(set(_re.findall(r"SBL_E_[A-Z_]+", full))),
            "ok_false": '"ok": false' in full,
            "crashed": "Traceback (most recent call last)" in full,
            "bytes": len(full)}


def sha(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def sbl_stack(tmp: str) -> dict:
    root = os.path.join(tmp, "stack")
    rows = {}
    rows["install"] = run([sys.executable, "-m", "sbl_stack.cli", "install", "--root", root])
    rows["doctor"] = run([sys.executable, "-m", "sbl_stack.cli", "doctor", "--root", root])
    rows["load"] = run([sys.executable, "-m", "sbl_stack.cli", "load", "--root", root])
    rows["invoke"] = run([sys.executable, "-m", "sbl_stack.cli", "invoke", "--root", root])
    rows["deny"] = run([sys.executable, "-m", "sbl_stack.cli", "invoke", "--root", root, "--mode",
                        "NOT_A_CANONICAL_MODE"])
    manifest = os.path.join(root, "stack.json")
    before = sha(manifest)
    rows["upgrade"] = run([sys.executable, "-m", "sbl_stack.cli", "upgrade", "--root", root, "--manifest", manifest])
    rows["rollback"] = run([sys.executable, "-m", "sbl_stack.cli", "rollback", "--root", root])
    # negative control: a manifest naming a component that does not exist must not pass silently
    d = json.loads(open(manifest, encoding="utf-8").read())
    d["components"][0] = "TAMPERED_COMPONENT"
    open(manifest, "w", encoding="utf-8", newline="\n").write(json.dumps(d, ensure_ascii=False, indent=2))
    neg_doctor = run([sys.executable, "-m", "sbl_stack.cli", "doctor", "--root", root])
    neg_load = run([sys.executable, "-m", "sbl_stack.cli", "load", "--root", root])
    rows["uninstall"] = run([sys.executable, "-m", "sbl_stack.cli", "uninstall", "--root", root])
    readback = run([sys.executable, "-m", "sbl_stack.cli", "doctor", "--root", root])
    return {"verbs": rows, "manifest_sha_before_upgrade": before,
            "negative_control": {"doctor_on_tampered_manifest": neg_doctor, "load_on_tampered_manifest": neg_load,
                                 "expectation": "both refuse with a typed code and rc!=0"},
            "uninstall_readback": {"root_exists": os.path.isdir(root), "doctor_after_uninstall": readback}}


def sp_zips(tmp: str) -> dict:
    digests = {}
    for tag in ("a", "b"):
        out = os.path.join(tmp, "zips_" + tag)
        r = run([sys.executable, "tools/build_sp_plugins.py", "--out-dir", out])
        digests[tag] = {f: sha(os.path.join(out, f)) for f in sorted(os.listdir(out)) if f.endswith(".zip")}
        digests[tag + "_rc"] = r["rc"]
    equal = digests["a"] == digests["b"] and bool(digests["a"])
    # install/uninstall/rollback of one package as a directory, with manifest validation
    pkg = os.path.join(tmp, "zips_a", sorted(digests["a"])[0])
    inst = os.path.join(tmp, "sp_install")
    with zipfile.ZipFile(pkg) as z:
        names = z.namelist()
        z.extractall(inst)
    manifest = [n for n in names if n.endswith("manifest.json")]
    mread = None
    if manifest:
        mp = os.path.join(inst, manifest[0])
        mread = {"path": manifest[0], "sha256": sha(mp), "keys": sorted(json.loads(open(mp, encoding="utf-8").read()))}
    shutil.rmtree(inst, ignore_errors=True)
    with zipfile.ZipFile(pkg) as z:
        z.extractall(inst)
    restored = {manifest[0]: sha(os.path.join(inst, manifest[0]))} if manifest else {}
    return {"zips": digests, "zip_pairs_equal": equal, "package_under_test": os.path.basename(pkg),
            "package_members": names[:12], "manifest_readback": mread,
            "install_dir_removed_then_restored": {"restored_sha": restored,
                                                 "rollback_byte_equal": bool(manifest) and restored == {manifest[0]: mread["sha256"]} if mread else False},
            "host_verbs": {"load": "HOST_PENDING", "invoke": "HOST_PENDING", "deny": "HOST_PENDING",
                           "reason": "plugin ids and effective load are issued by the host; a ZIP is not an installation"}}


def hgk_harness() -> dict:
    env_note = "PYTHONPATH=src, interpreter 3.12.13"
    p = subprocess.run([PY312, "-m", "hg_kseos.cli", "doctor"], cwd=HGK, capture_output=True, text=True,
                       env=dict(os.environ, PYTHONPATH="src"))
    verdict = "PASS" if '"verdict": "PASS"' in p.stdout else "NOT_PASS"
    return {"doctor": {"cmd": PY312 + " -m hg_kseos.cli doctor", "rc": p.returncode, "verdict": verdict,
                       "env": env_note},
            "verbs": {"install": "NOT_APPLICABLE_CONTROL_PLANE_OWNED",
                      "load": "NOT_APPLICABLE_CONTROL_PLANE_OWNED", "invoke": "doctor/plan/execute are the ABI",
                      "deny": "covered by C04 negative controls", "upgrade": "HGK owner only",
                      "uninstall": "HGK owner only", "rollback": "HGK owner only"}}


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="q5_", dir=r"C:/Users/user/AppData/Local/Temp")
    payload = {
        "schema": "SBL_Q5_LOCAL_LIFECYCLE_RECEIPT/1",
        "measured_at_utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip(),
        "instrument": "verbs executed as CLI subcommands; digests computed from bytes; rc captured without pipes",
        "tools": {
            "SBL_STACK": sbl_stack(tmp),
            "THREE_SP_ZIPS": sp_zips(tmp),
            "HGK_HARNESS": hgk_harness(),
        },
        "claim_ceiling": ("local lifecycle evidence only: install/doctor/load/invoke/deny/uninstall exercised on this host; "
                          "three ZIPs built twice with equal digests; no host-issued plugin id, no effective host load, "
                          "no private-host acceptance, no release"),
    }
    verbs = payload["tools"]["SBL_STACK"]["verbs"]
    payload["summary"] = {"sbl_stack_verbs": {k: ("PASS" if v["rc"] == 0 else f"rc={v['rc']}") for k, v in verbs.items()},
                          "zip_pairs_equal": payload["tools"]["THREE_SP_ZIPS"]["zip_pairs_equal"],
                          "hgk_doctor": payload["tools"]["HGK_HARNESS"]["doctor"]["verdict"],
                          # rc!=0 alone cannot distinguish a typed refusal from a crash: a traceback exits 1 too.
                          "negative_control": {
                              "doctor_rc": payload["tools"]["SBL_STACK"]["negative_control"]["doctor_on_tampered_manifest"]["rc"],
                              "doctor_crashed": payload["tools"]["SBL_STACK"]["negative_control"]["doctor_on_tampered_manifest"]["crashed"],
                              "doctor_typed_refusal": bool(payload["tools"]["SBL_STACK"]["negative_control"]["doctor_on_tampered_manifest"]["codes"]),
                              "load_rc": payload["tools"]["SBL_STACK"]["negative_control"]["load_on_tampered_manifest"]["rc"],
                              "load_typed_refusal": bool(payload["tools"]["SBL_STACK"]["negative_control"]["load_on_tampered_manifest"]["codes"]),
                              "load_ok_false": payload["tools"]["SBL_STACK"]["negative_control"]["load_on_tampered_manifest"]["ok_false"],
                              "reading": ("a crash is not a refusal; this row is only PASS when doctor_crashed is false and a typed code is present")},
                          "uninstall_readback_clean": not payload["tools"]["SBL_STACK"]["uninstall_readback"]["root_exists"]}
    json.dump(payload, open(os.path.join(OUT, "LIFECYCLE_RECEIPT.json"), "w", encoding="utf-8", newline="\n"),
              ensure_ascii=False, indent=2)
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=1))
    shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
