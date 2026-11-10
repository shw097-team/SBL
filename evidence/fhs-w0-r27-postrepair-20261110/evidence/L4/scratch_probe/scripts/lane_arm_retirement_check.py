"""Fail-closed check that a retired arm cannot reappear anywhere live.

The owner order of 2026-11-09 retired `opencode-go/mimo-v2.6-pro` and admitted
`opencode-go/mimo-v2.6-flash` to the PLAN pool. A retirement that lives only in prose is a suggestion; this
check makes it a fact: any retired arm found in a live arm, fallback, ordered pool or lane chain is a refusal.

Live = config/lane-routing-registry.yaml, config/lane-route-slots.candidate.json,
config/model-lane-assignment.json. Evidence and history files are not scanned: they record what was true then.

Exit: 0 clean, 4 a retired arm is live, 5 a required admission is missing.
"""
from __future__ import annotations

import json
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
REG = ROOT / "config/lane-routing-registry.yaml"
POOL = ROOT / "config/lane-route-slots.candidate.json"
ASG = ROOT / "config/model-lane-assignment.json"
REQUIRED = {("PLAN", "opencode-go/mimo-v2.6-flash")}


def norm(model: str, provider: str = "") -> str:
    return model if "/" in model or not provider else f"{provider}/{model}"


def live_arms() -> list[tuple[str, str]]:
    out = []
    reg = yaml.safe_load(REG.read_text(encoding="utf-8"))
    for lane in reg.get("routes", []):
        for field in ("arms", "fallbacks"):
            for a in lane.get(field, []):
                out.append((f"registry:{lane['lane']}:{field}", norm(a.get("model", ""), a.get("provider", ""))))
        out.append((f"registry:{lane['lane']}:rank1", norm(lane.get("model", ""), lane.get("provider", ""))))
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    for lane in pool.get("lanes", []):
        for e in lane.get("ordered_pool", []):
            out.append((f"pool:{lane['lane']}", norm(e.get("model", ""), e.get("provider", ""))))
    asg = json.loads(ASG.read_text(encoding="utf-8"))
    for role, chain in (asg.get("lane_chains") or {}).items():
        for i, e in enumerate(chain):
            out.append((f"assignment:{role}[{i}]", norm(e.get("model", ""), e.get("provider", ""))))
    return out


def main() -> int:
    reg = yaml.safe_load(REG.read_text(encoding="utf-8"))
    retired = {f"{k}" for k in (reg.get("retired_arms") or {})}
    live = live_arms()
    hits = [(where, arm) for where, arm in live if arm in retired]
    live_set = {a for _, a in live}
    missing = [list(r) for r in REQUIRED if r[1] not in live_set]
    print(json.dumps({
        "schema": "HGK.LaneArmRetirement/1",
        "epoch": reg.get("epoch"),
        "retired": sorted(retired),
        "live_arm_sites": len(live),
        "retired_still_live": hits,
        "required_missing": missing,
        "verdict": "PASS" if not hits and not missing else "FAIL",
    }, ensure_ascii=False, indent=1))
    if hits:
        return 4
    if missing:
        return 5
    return 0


if __name__ == "__main__":
    sys.exit(main())
