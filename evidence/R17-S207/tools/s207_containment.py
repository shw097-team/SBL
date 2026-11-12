"""S2-07 S207-CONTAINMENT-LOCK: measure the containment, per card, without moving it.

Two in-process evaluations of the real selector (tools/advance.py), same queue, same ledger:
  A) with RG04_ARM.json present  -> what the HOST may dispatch now
  B) with rg04_arm() patched to None -> what the host WOULD dispatch if the arm were deleted
Nothing is deleted, no card state is written: the only writes are the two READY_SET
snapshots under receipts/ (advance.py's --out target) and this receipt.

The point of (B) is OD-14: the 14 deferred cards must be re-admitted one by one, so the
report needs the list, its classes, and which of them could carry an effect.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

VAR = Path("C:/Projects/Agent_Workspace/var/R17-20261023")
TOOLS = VAR / "tools"
OUT = VAR / "receipts/R17_S207_CONTAINMENT.json"
TPE = timezone(timedelta(hours=8))


def load_advance():
    spec = importlib.util.spec_from_file_location("advance_probe", TOOLS / "advance.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["advance_probe"] = mod
    spec.loader.exec_module(mod)
    return mod


def run(mod, out_name):
    """Call main() with --out into receipts, return the parsed snapshot."""
    out = VAR / "receipts" / out_name
    old = sys.argv
    sys.argv = ["advance.py", "--out", str(out)]
    try:
        mod.main()
    finally:
        sys.argv = old
    return json.loads(out.read_text(encoding="utf-8"))


def ids(doc):
    return [c["id"] for c in (doc.get("next") and [doc["next"]] or [])] if False else doc


def ready_ids(doc):
    """advance.py only reports the single next card; read the buckets for the full sets."""
    out = []
    for k in ("READY_READONLY", "READY_ISOLATED_CANDIDATE", "READY_ADMITTED_EFFECT"):
        for c in doc.get("buckets", {}).get(k, []):
            out.append({"id": c.get("id"), "bucket": k, "command": (c.get("command") or "")[:120],
                        "why": (c.get("why") or "")[:100], "queue_state": c.get("queue_state"),
                        "source": c.get("source")})
    return out


def main():
    arm_path = VAR / "RG04_ARM.json"
    arm = json.loads(arm_path.read_text(encoding="utf-8")) if arm_path.exists() else None

    mod = load_advance()
    armed = run(mod, "S207_READY_ARMED.json")          # real state, arm present
    mod2 = load_advance()
    mod2.rg04_arm = lambda: None                       # counterfactual: arm deleted
    unarmed = run(mod2, "S207_READY_NOARM.json")

    a_ready, b_ready = ready_ids(armed), ready_ids(unarmed)
    # advance.py reports buckets BEFORE the arm gate, so the dispatchable set is derived with the
    # same rule the driver uses (id in allowlist) and then reconciled against the driver's own counts.
    allow = {str(x) for x in ((arm or {}).get("allowlist") or [])}
    dispatchable = [c for c in b_ready if c["id"] in allow]
    gated = sorted(c["id"] for c in b_ready if c["id"] not in allow)
    reconcile = {"armed_ready_count_matches": len(dispatchable) == (armed.get("ready_count") or 0),
                 "armed_gated_count_matches": len(gated) == (armed.get("rg04_gated") or 0),
                 "driver_ready_count": armed.get("ready_count"),
                 "driver_gated": armed.get("rg04_gated")}

    # per-card requalification view: an effect-capable card needs a native permit, so it is
    # never released in bulk; read-only/isolated cards are released one at a time with a receipt.
    q = json.loads((VAR / "RESUME_QUEUE_R17.json").read_text(encoding="utf-8"))
    rows = {r["id"]: r for r in (q if isinstance(q, list) else q.get("rows", []))}
    # authoritative classes come from the driver's own CARDS table, not from a regex guess
    card_table = {k: v[0] for k, v in getattr(mod, "CARDS", {}).items()}

    per_card = []
    for cid in gated:
        row = rows.get(cid) or {}
        cls = card_table.get(cid) or "SUBTASK_NOT_IN_CARDS_TABLE"
        effect_capable = cls == "READY_ADMITTED_EFFECT" 
        per_card.append({
            "id": cid, "driver_class": cls, "queue_state": row.get("state"),
            "family": row.get("family"), "owner_class": row.get("owner_class"),
            "effect_capable_without_permit": effect_capable,
            "admission": ("NATIVE_PERMIT_REQUIRED" if effect_capable
                          else "READ_ONLY_ISOLATED_RELEASABLE_ONE_BY_ONE"),
            "requalify_evidence_needed": ("native workorder + permit + effective sandbox"
                                          if effect_capable else "single-card dry run + envelope unchanged"),
        })

    receipt = {
        "schema": "R17_S207_CONTAINMENT/1",
        "generated_local": datetime.now(TPE).isoformat(timespec="seconds"),
        "arm_present": arm is not None,
        "arm_sha256": __import__("hashlib").sha256(arm_path.read_bytes()).hexdigest() if arm_path.exists() else None,
        "arm_allowlist": (arm or {}).get("allowlist"),
        "armed": {"decision": armed.get("decision"), "ready_count": armed.get("ready_count"),
                  "gated": armed.get("rg04_gated"), "cursor": armed.get("cursor"),
                  "next": (armed.get("next") or {}).get("id"),
                  "counts": armed.get("counts")},
        "counterfactual_no_arm": {"decision": unarmed.get("decision"),
                                  "ready_count": unarmed.get("ready_count"),
                                  "next": (unarmed.get("next") or {}).get("id"),
                                  "counts": unarmed.get("counts")},
        "dispatchable_now": dispatchable,
        "reconcile": reconcile,
        "gated_cards": gated,
        "gated_count": len(gated),
        "per_card_requalification": per_card,
        "effect_capable_in_gated_set": sum(1 for c in per_card if c["effect_capable_without_permit"]),
        "writer_hold": (VAR / "HOLD_EXECUTE_WRITER.json").exists(),
    }
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"armed_ready": armed.get("ready_count"), "armed_gated": armed.get("rg04_gated"),
                      "noarm_ready": unarmed.get("ready_count"), "gated_cards": len(gated),
                      "effect_capable": receipt["effect_capable_in_gated_set"],
                      "out": str(OUT)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
