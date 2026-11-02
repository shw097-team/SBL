#!/usr/bin/env python3
"""S4 -> S5..S8 typed integration seams.

The R2 order explicitly keeps S5..S8 OUT of the delivery gate but requires the typed seam schemas,
compatibility fixtures and a dependency ledger so the next phase is not blocked. This builds those
artefacts and marks every live effect NOT_RUN - a seam is not an execution.
"""
from __future__ import annotations
import json, hashlib, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".hgk" / "artifacts" / "s4"
FIX = ROOT / "fixtures" / "s5_s8"
SEAMS = [
    ("S5", "HGK Receiver Shadow / Canary", ["ExecutionHandoff", "ExecutionBindingRef", "ArtifactIdentity"]),
    ("S6", "GENIE Product Compiler", ["GENIEProjectionRef", "SurfaceProjectionManifest"]),
    ("S7", "JIT runtime world-effect factory", ["SurfaceProjectionManifest", "ProfileBinding"]),
    ("S8", "SGM authority cutover", ["AuthorityBinding", "WorkOrderCandidate", "TaskSpecSeed"]),
]


def schema_ok(name: str) -> bool:
    p = ROOT / "schemas" / f"{name}.schema.json"
    if not p.exists():
        return False
    d = json.loads(p.read_text(encoding="utf-8"))
    return bool(d.get("$id")) and isinstance(d.get("properties"), dict) and bool(d["properties"])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True); FIX.mkdir(parents=True, exist_ok=True)
    rows = []
    for stage, title, schemas in SEAMS:
        present = {s: schema_ok(s) for s in schemas}
        fixture = {"stage": stage, "seam_schemas": schemas,
                   "fixture_kind": "compatibility", "live_status": "NOT_RUN",
                   "asserted": {"itch_contract_only": True, "no_live_receiver_ack": True,
                                "no_world_effect": True}}
        fp = FIX / f"{stage.lower()}_compat.json"
        fp.write_text(json.dumps(fixture, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
        rows.append({
            "stage": stage, "title": title, "typed_seam_schemas": present,
            "all_seams_present": all(present.values()),
            "compatibility_fixture": str(fp.relative_to(ROOT)).replace("\\", "/"),
            "fixture_sha256": hashlib.sha256(fp.read_bytes()).hexdigest(),
            "live_effect": "NOT_RUN", "delivery_gate": False,
            "claim": "DESIGN_ONLY_FOR_NEXT_PHASE",
            "blocking_preconditions": (
                ["real HGK Receiver ACK + canary budget", "independent shadow-mode acceptance"]
                if stage == "S5" else
                ["GENIE compiler admission", "SurfaceProjectionManifest producer"] if stage == "S6" else
                ["world-effect sandbox admission", "JIT budget policy"] if stage == "S7" else
                ["SGM authority grant", "cutover rollback plan approved by owner"]),
        })
    payload = {
        "why": "S5..S8 are explicitly out of this round's gate; only the typed seam, its compatibility "
               "fixture and this ledger are delivered.",
        "stages": rows,
        "live_effects_claimed": 0,
        "candidate_head": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                         capture_output=True, text=True).stdout.strip(),
    }
    payload["verdict"] = "PASS" if all(r["all_seams_present"] for r in rows) and len(rows) == 4 else "FAIL"
    (OUT / "S5_S8_BACKLOG.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                            encoding="utf-8", newline="")
    print(json.dumps({"stages": [r["stage"] for r in rows],
                      "seams_present": {r["stage"]: r["all_seams_present"] for r in rows},
                      "live_effects_claimed": 0, "verdict": payload["verdict"]}, ensure_ascii=False, indent=1))
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
