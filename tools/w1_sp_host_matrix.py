#!/usr/bin/env python3
"""WP-FHS-11 — Portable SP host matrix: selected → installed → loaded → invoked → non-trigger → removed.

This tool runs INSIDE a host interpreter (the fresh venv the distribution was installed into), so
every leg is a real process reading the installed tree — not a package ZIP being described.

What it refuses to do: report `LOADED` because a ZIP exists, or report one installation receipt for
three principals. Each SP gets its own leg set and its own digests; a Host that was not exercised is
recorded `NOT_RUN` instead of being inferred from a neighbour.

Usage:
    <host-python> tools/w1_sp_host_matrix.py --out <path.json> [--host-label win-py311-venv]

Exit 0 iff every exercised leg is PASS/its declared state and the removal leg proved the import is
gone in a FRESH process.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata as md
import json
import os
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

SP_IDS = ("tpm_sp", "commander_sp", "external_challenge_sp")


def sha_obj(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--host-label", default="local-venv")
    ap.add_argument("--skills-root", default="", help="PIPD skills root for the 8-skill matrix")
    ap.add_argument("--skip-removal", action="store_true")
    args = ap.parse_args()

    # The host reader must read the INSTALLED tree, never the working copy: with cwd inside the
    # repository, sys.path[0] imports the repo's sbl_sp and the whole matrix would describe bytes
    # nobody installed. A neutral cwd is the only version of this check that means anything.
    neutral = Path(tempfile.mkdtemp(prefix="w1-sp-neutral-"))
    os.chdir(neutral)

    from sbl_sp import plugins, sp

    dist_version = md.version("sbl-v01")
    sbl_pkg = Path(importlib.import_module("sbl_sp").__file__).resolve().parent
    host = {"label": args.host_label, "platform": platform.platform(),
            "python": sys.version.split()[0], "executable": sys.executable,
            "distribution": {"name": "sbl-v01", "version": dist_version,
                             "location": str(sbl_pkg.parent.parent)},
            "reader": "python importlib.metadata + installed tree import",
            "resolved_sbl_sp": str(sbl_pkg),
            "import_cwd": str(neutral)}

    work = Path(tempfile.mkdtemp(prefix="w1-sp-"))
    packages = {p["sp_id"]: p for p in plugins.build_all(work)} if hasattr(plugins, "build_all") else {}
    matrix = []
    for sp_id in SP_IDS:
        legs = {}
        pkg = packages.get(sp_id, {})
        legs["selected"] = {"state": "PASS", "reader": "sbl_sp.plugins.SP_IDS",
                            "value": sp_id in plugins.SP_IDS}
        legs["built"] = {"state": "PASS" if pkg else "NOT_RUN", "sha256": pkg.get("sha256"),
                         "bytes": pkg.get("bytes"), "entries": pkg.get("entries")}
        plugin_dir = sbl_pkg / "plugins" / sp_id
        legs["installed"] = {"state": "PASS" if plugin_dir.is_dir() else "FAIL",
                             "path": str(plugin_dir),
                             "files": sorted(p.name for p in plugin_dir.glob("*")) if plugin_dir.is_dir() else []}
        manifest = plugins.plugin_manifest(sp_id)
        text = plugins.skill_text(sp_id)
        violations = plugins.validate_skill(text, plugins.skill_name(sp_id))
        legs["loaded"] = {"state": "PASS" if not violations else "FAIL",
                          "plugin_name": manifest.get("name"),
                          "plugin_schema": manifest.get("$schema"),
                          "skill_name": plugins.skill_name(sp_id),
                          "violations": violations,
                          "plugin_manifest_sha256": sha_obj(manifest),
                          "skill_sha256": hashlib.sha256(text.encode()).hexdigest()}
        record = plugins.principal_record(sp_id)
        loaded_manifest = sp.load_manifest(sp_id)
        legs["invoked"] = {"state": "PASS",
                           "calls": ["sp.load_manifest", "plugins.principal_record",
                                     "plugins.plugin_manifest", "plugins.validate_skill"],
                           "role": record.get("role"),
                           "permissions": loaded_manifest.get("permissions"),
                           "read_only": record.get("read_only")}
        other = next(s for s in SP_IDS if s != sp_id)
        other_text = plugins.skill_text(other)
        wrong = plugins.validate_skill(other_text, plugins.skill_name(sp_id))
        try:
            sp.load_manifest("no_such_principal")
            refused = False
        except Exception:
            refused = True
        legs["nontrigger"] = {"state": "PASS" if (wrong and refused) else "FAIL",
                              "foreign_skill_violations": len(wrong),
                              "unknown_sp_refused": refused,
                              "note": "another principal's skill text does not validate under this name"}
        matrix.append({"sp_id": sp_id, "legs": legs,
                       "evidence_class": "HOST_BOUND_LOCAL_VENV",
                       "claim_ceiling": "INSTALLED_AND_INVOKED_ON_THIS_HOST"})

    skills = {"state": "NOT_RUN"}
    if args.skills_root:
        checker = Path(args.skills_root) / "tools" / "skill_pack_check.py"
        if checker.is_file():
            run = subprocess.run([sys.executable, str(checker), "--all",
                                  "--skills-root", str(Path(args.skills_root) / "skills")],
                                 capture_output=True, text=True)
            try:
                payload = json.loads(run.stdout or "{}")
            except ValueError:
                payload = {"raw": (run.stdout or "")[:2000]}
            skills = {"state": payload.get("state", "UNPARSEABLE"), "exit_code": run.returncode,
                      "checker": str(checker), "summary": {k: payload.get(k) for k in
                                                           ("count", "packs", "refusals") if k in payload}}

    removal = {"state": "NOT_RUN"}
    if not args.skip_removal:
        un = subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "sbl-v01"],
                            capture_output=True, text=True)
        probe = subprocess.run([sys.executable, "-c", "import sbl_sp"], capture_output=True,
                               text=True, cwd=str(neutral))
        residue = sorted(str(p) for p in sbl_pkg.glob("*")) if sbl_pkg.exists() else []
        removal = {"state": "REMOVED" if probe.returncode != 0 else "RESIDUE_PRESENT",
                   "uninstall_exit": un.returncode,
                   "fresh_process_import_exit": probe.returncode,
                   "residue_files": residue,
                   "note": "removal is proven by a FRESH process failing to import, not by the uninstall exit code"}

    record = {
        "schema": "FHS.W1.WP11.SPHostMatrix@1",
        "host": host,
        "hosts_not_exercised": [
            {"host": "hermes-desktop-host", "state": "NOT_RUN",
             "reason": "no host-side loader/invocation path was exercised for this principal on the desktop app"},
            {"host": "hgk-runtime-host", "state": "NOT_RUN",
             "reason": "HGK runtime install is a HOST_OP held by the original issuer"},
        ],
        "sp_matrix": matrix,
        "pipd_skills_8": skills,
        "removal": removal,
        "claim_ceiling": "HOST_BOUND_INSTALLED_AND_INVOKED__NO_DESKTOP_LOAD",
        "not_claimed": ["desktop-app loaded", "three hosts exercised", "release"],
    }
    record["matrix_sha256"] = sha_obj({k: v for k, v in record.items() if k != "matrix_sha256"})
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    states = {m["sp_id"]: {k: v["state"] for k, v in m["legs"].items()} for m in matrix}
    print(json.dumps({"out": str(out), "host": host["label"], "distribution": dist_version,
                      "states": states, "skills": skills.get("state"),
                      "removal": removal["state"], "matrix_sha256": record["matrix_sha256"]},
                     ensure_ascii=False, indent=1))
    ok = all(all(v in ("PASS", "NOT_RUN") for v in legs.values()) for legs in states.values())
    return 0 if ok and (args.skip_removal or removal["state"] == "REMOVED") else 1


if __name__ == "__main__":
    raise SystemExit(main())
