#!/usr/bin/env python3
"""Execute the four L4 cases at CLI level and capture each raw log + exit code.

A fixture is a directory holding config/ with the three live control-plane files. NEG-H1/H2/H3 mutate exactly
one site of a private copy; POS-H4 runs against the ported worktree itself. Nothing is written inside the repo.

Usage: python run_negatives.py <worktree> <evidence_dir>
"""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

WT = Path(sys.argv[1]).resolve()
EV = Path(sys.argv[2]).resolve()
PY = sys.executable
VALIDATOR = WT / "scripts" / "lane_epoch_validate.py"
FILES = [
    "config/lane-routing-registry.yaml",
    "config/lane-route-slots.candidate.json",
    "config/model-lane-assignment.json",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_fixture(name: str) -> Path:
    root = EV / "neg" / name
    if root.exists():
        shutil.rmtree(root)
    for rel in FILES:
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(WT / rel, dst)
    return root


def run(root: Path, tag: str) -> dict:
    log = EV / f"{tag}.log"
    proc = subprocess.run([PY, str(VALIDATOR), "--root", str(root)],
                          capture_output=True, text=True, encoding="utf-8")
    body = (
        f"$ {PY} scripts/lane_epoch_validate.py --root {root}\n"
        f"--- stdout ---\n{proc.stdout}"
        f"--- stderr ---\n{proc.stderr}"
        f"EXIT={proc.returncode}\n"
    )
    log.write_text(body, encoding="utf-8")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"verdict": "UNPARSEABLE_OUTPUT", "primary_code": None, "codes": []}
    return {"tag": tag, "root": str(root), "exit": proc.returncode,
            "verdict": payload["verdict"], "primary_code": payload["primary_code"],
            "codes": payload["codes"], "log": str(log), "log_sha256": sha256(log)}


rows = []

# ---- POS-H4: the ported tree, unmutated ------------------------------------------------------
rows.append(run(WT, "pos_h4_ported_epoch41"))

# ---- NEG-H1: registry says retired, EXECUTE pool still lists the arm -------------------------
root = make_fixture("neg_h1")
pool_path = root / "config/lane-route-slots.candidate.json"
doc = json.loads(pool_path.read_text(encoding="utf-8"))
hit = 0
for node in doc["lanes"]:
    if node["lane"] != "EXECUTE":
        continue
    for entry in node["ordered_pool"]:
        if entry["rank"] == 2:
            entry["provider"] = "opencode-go"
            entry["model"] = "mimo-v2.6-pro"
            entry["transport_model"] = "opencode-go/mimo-v2.6-pro"
            hit += 1
assert hit == 1, hit
pool_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
rows.append(run(root, "neg_h1_retirement_drift"))

# ---- NEG-H2: epoch non-numeric ---------------------------------------------------------------
root = make_fixture("neg_h2")
reg = root / "config/lane-routing-registry.yaml"
lines = reg.read_text(encoding="utf-8").splitlines()
hits = [i for i, ln in enumerate(lines) if ln.rstrip() == "epoch: 41"]
assert len(hits) == 1, hits
lines[hits[0]] = "epoch: forty-one"
reg.write_text("\n".join(lines) + "\n", encoding="utf-8")
rows.append(run(root, "neg_h2_epoch_unparseable"))

# ---- NEG-H3: PLAN rank 4 (the owner-ordered admission slot) holds the retired arm -------------
root = make_fixture("neg_h3")
pool_path = root / "config/lane-route-slots.candidate.json"
doc = json.loads(pool_path.read_text(encoding="utf-8"))
hit = 0
for node in doc["lanes"]:
    if node["lane"] != "PLAN":
        continue
    for entry in node["ordered_pool"]:
        if entry["rank"] == 4:
            entry["provider"] = "opencode-go"
            entry["model"] = "mimo-v2.6-pro"
            entry["transport_model"] = "opencode-go/mimo-v2.6-pro"
            hit += 1
assert hit == 1, hit
pool_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
rows.append(run(root, "neg_h3_retired_arm_in_pool"))

out = EV / "negatives_executed.json"
out.write_text(json.dumps(rows, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
for r in rows:
    print(f"{r['tag']:34s} exit={r['exit']} verdict={r['verdict']:9s} code={r['primary_code']} "
          f"log={r['log']} sha256={r['log_sha256']}")
print(f"index={out} sha256={sha256(out)}")
