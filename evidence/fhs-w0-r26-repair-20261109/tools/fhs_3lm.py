"""FHS-3L&M — the hard entry contract for lane and model routing.

This file does **not** own routing and must not become a second routing authority. It reads the existing
HG-KSEOS control plane (`config/lane-routes.yaml` projection, `config/lane-route-slots.candidate.json` pool,
`config/lane-routing-registry.yaml` epoch) read-only, and answers two questions for anyone about to run an FHS
task:

    1. what may I choose, per lane?      -> `--menu`   (the owner's selectable menu, slot by slot)
    2. may this exact choice be used?    -> `--bind`   (fail-closed, writes one run-scoped binding record)

The distinction the owner asked for is preserved here: a lane binding is a **control-plane fact**, a session pin
is a **conversation setting**. `--bind` never touches the registry and never writes a session pin; it only
records that, at this epoch, the chosen arm was admitted for that lane. `--assert` re-reads the registry and
fails closed if the epoch moved or the arm left the pool.

Exit codes: 0 ok, 2 slot/arm not on the owner's menu, 6 arm not in the lane's pool, 7 epoch drift,
8 bad input, 9 the arm is retired and must never be selected.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROUND = HERE.parent
HGK = pathlib.Path(r"C:\Projects\Agent_Workspace\HG-KSEOS")
POOL = HGK / "config" / "lane-route-slots.candidate.json"
REGISTRY_YAML = HGK / "config" / "lane-routing-registry.yaml"
BINDING_DIR = ROUND / "lanes" / "bindings"
TZ = datetime.timezone(datetime.timedelta(hours=8))

# The owner's menu, in the owner's order. `model` is the name a human reads; `match` is how we find it in the pool.
MENU = {
    "PLAN": [
        {"slot": "primary", "label": "GPT 6.1 SOL-MEDIUM", "model": "gpt-6.1-sol", "provider": "openai-codex"},
        {"slot": "opt1", "label": "DEEPSEEK V4.1 FLASH", "model": "deepseek-v4.1-flash", "provider": "opencode-go"},
        {"slot": "opt2", "label": "MiMo-V2.6-Flash", "model": "mimo-v2.6-flash", "provider": "opencode-go"},
    ],
    "EXECUTE": [
        {"slot": "primary", "label": "DEEPSEEK V4.1 FLASH", "model": "deepseek-v4.1-flash", "provider": "opencode-go"},
        {"slot": "opt1", "label": "MiMo-V2.6-Flash", "model": "mimo-v2.6-flash", "provider": "opencode-go"},
        {"slot": "opt2", "label": "GPT-6-luna", "model": "gpt-6-luna", "provider": "openai-codex"},
    ],
    "VERIFY": [
        {"slot": "primary", "label": "GPT 6.1 SOL-MEDIUM", "model": "gpt-6.1-sol", "provider": "openai-codex"},
        {"slot": "opt1", "label": "DEEPSEEK V4.1 FLASH", "model": "deepseek-v4.1-flash", "provider": "opencode-go"},
        {"slot": "opt2", "label": "MiMo-V2.6-Flash", "model": "mimo-v2.6-flash", "provider": "opencode-go"},
    ],
}
# the pool names the verify lane VERIFY_SECURITY; the owner's menu says VERIFY
LANE_ALIAS = {"VERIFY": "VERIFY_SECURITY", "SECURITY": "VERIFY_SECURITY"}


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def now() -> str:
    return datetime.datetime.now(TZ).isoformat(timespec="seconds")


def load_pool() -> dict:
    raw = POOL.read_bytes()
    d = json.loads(raw)
    return {"raw_sha256": sha(raw), "lanes": {ln["lane"]: ln for ln in d["lanes"]}}


def epoch() -> dict:
    raw = REGISTRY_YAML.read_bytes() if REGISTRY_YAML.is_file() else b""
    txt = raw.decode("utf-8", "replace")
    out = {"registry_sha256": sha(raw)}
    for line in txt.splitlines():
        if line.startswith("registry_version:"):
            out["registry_version"] = line.split(":", 1)[1].strip().strip('"')
        if line.startswith("registry_epoch:"):
            out["registry_epoch"] = line.split(":", 1)[1].strip().strip('"')
        if line.startswith("updated_at:"):
            out["updated_at"] = line.split(":", 1)[1].strip().strip('"')
    return out


def menu() -> dict:
    pool = load_pool()
    ep = epoch()
    lanes = []
    for lane, slots in MENU.items():
        pool_lane = pool["lanes"].get(LANE_ALIAS.get(lane, lane))
        rows = []
        for s in slots:
            hit = None
            for e in (pool_lane or {}).get("ordered_pool", []):
                if e.get("provider") == s["provider"] and e.get("model") == s["model"]:
                    hit = e
                    break
            rows.append({**s, "admitted": hit is not None,
                         "pool_rank": hit.get("rank") if hit else None,
                         "transport_model": hit.get("transport_model") if hit else None,
                         "why_not": None if hit else "NOT_IN_LANE_POOL"})
        lanes.append({"lane": lane, "pool_lane": LANE_ALIAS.get(lane, lane), "slots": rows})
    return {"schema": "FHS.3LM.Menu/1", "generated_at": now(), "epoch": ep, "pool_sha256": pool["raw_sha256"],
            "lanes": lanes,
            "rule": ("choose a slot; a slot whose arm is not in the lane pool is shown but refused (NOT_IN_LANE_POOL) "
                     "— adding an arm is a control-plane epoch change, not something this task may do")}


def retired_arms(pool: dict) -> dict:
    """The retirement ledger is the control plane's own record; this layer reads it and never writes it."""
    try:
        raw = json.loads(POOL.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {}
    return raw.get("retired_arms") or {}


def bind(lane: str, slot: str, allow_fallback: bool = False) -> tuple[int, dict]:
    m = menu()
    lane_row = next((x for x in m["lanes"] if x["lane"] == lane), None)
    if lane_row is None:
        return 8, {"error": "UNKNOWN_LANE", "lane": lane, "known": sorted(MENU)}
    row = next((x for x in lane_row["slots"] if x["slot"] == slot), None)
    if row is None:
        return 8, {"error": "UNKNOWN_SLOT", "slot": slot, "known": [s["slot"] for s in lane_row["slots"]]}
    retired = retired_arms({})
    arm = f"{row['provider']}/{row['model']}"
    if arm in retired:
        return 9, {"error": "RETIRED_ARM", "lane": lane, "slot": slot, "arm": arm,
                   "replacement": retired[arm].get("replacement"),
                   "why": retired[arm].get("reason"),
                   "rule": "a retired arm is never selected, not even as a fallback; the replacement is named"}
    if not row["admitted"]:
        fallback = next((x for x in lane_row["slots"] if x["admitted"]), None)
        rec_out = {"error": "NOT_IN_LANE_POOL", "lane": lane, "slot": slot,
                   "arm": f"{row['provider']}/{row['model']}",
                   "fix": ("the pool for this lane has no such arm; adding one is an owner-ordered registry epoch "
                           "change. This task refuses rather than editing routing it does not own.")}
        if allow_fallback and fallback:
            code, out = bind(lane, fallback["slot"], False)
            out["fallback_from"] = slot
            out["fallback_reason"] = "NOT_IN_LANE_POOL"
            return 0, out
        return 6, rec_out
    BINDING_DIR.mkdir(parents=True, exist_ok=True)
    rec = {"schema": "FHS.3LM.Binding/1", "lane": lane, "slot": slot, "label": row["label"],
           "provider": row["provider"], "model": row["model"], "transport_model": row["transport_model"],
           "pool_rank": row["pool_rank"], "bound_at": now(), "epoch": m["epoch"], "pool_sha256": m["pool_sha256"],
           "plane": "LANE_CONTROL_PLANE",
           "not_a_session_pin": ("a session pin in the desktop app is a conversation setting and does not bind a "
                                 "lane; this record is the lane binding, and only this record is read by --assert")}
    path = BINDING_DIR / f"{lane}_{slot}.json"
    path.write_text(json.dumps(rec, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0, {"bound": True, "path": str(path.relative_to(ROUND)).replace(os.sep, "/"), **rec}


def assert_binding(path: str) -> tuple[int, dict]:
    rec = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    pool = load_pool()
    ep = epoch()
    if rec["epoch"].get("registry_sha256") != ep["registry_sha256"]:
        return 7, {"ok": False, "first_fail": "EPOCH_DRIFT", "bound": rec["epoch"], "now": ep}
    lane = rec["lane"]
    pool_lane = pool["lanes"].get(LANE_ALIAS.get(lane, lane)) or {}
    hit = next((e for e in pool_lane.get("ordered_pool", [])
                if e.get("provider") == rec["provider"] and e.get("model") == rec["model"]), None)
    if hit is None:
        return 6, {"ok": False, "first_fail": "ARM_LEFT_POOL", "arm": f"{rec['provider']}/{rec['model']}"}
    return 0, {"ok": True, "lane": lane, "arm": f"{rec['provider']}/{rec['model']}", "pool_rank": hit.get("rank"),
               "epoch_unchanged": True}


def main() -> int:
    ap = argparse.ArgumentParser(description="FHS-3L&M hard entry contract (reads HG-KSEOS, owns no routing)")
    ap.add_argument("--menu", action="store_true")
    ap.add_argument("--bind", nargs=2, metavar=("LANE", "SLOT"))
    ap.add_argument("--assert", dest="assert_file")
    ap.add_argument("--assert-arm", metavar="PROVIDER/MODEL",
                    help="refuse a retired arm outright (exit 9) and say what replaced it")
    ap.add_argument("--allow-fallback", action="store_true",
                    help="if the chosen slot's arm is not in the lane pool, bind the next admitted slot and record it")
    a = ap.parse_args()
    if a.menu:
        print(json.dumps(menu(), ensure_ascii=False, indent=1))
        return 0
    if a.assert_arm:
        ret = retired_arms({})
        if a.assert_arm in ret:
            print(json.dumps({"ok": False, "error": "RETIRED_ARM", "arm": a.assert_arm,
                              "replacement": ret[a.assert_arm].get("replacement"),
                              "why": ret[a.assert_arm].get("reason")}, ensure_ascii=False, indent=1))
            return 9
        pool = load_pool()
        hit = [(name, e["rank"]) for name, d in pool["lanes"].items()
               for e in d.get("ordered_pool", [])
               if f"{e.get('provider')}/{e.get('model')}" == a.assert_arm]
        print(json.dumps({"ok": bool(hit), "arm": a.assert_arm, "lanes": hit}, ensure_ascii=False, indent=1))
        return 0 if hit else 6
    if a.bind:
        code, out = bind(a.bind[0], a.bind[1], a.allow_fallback)
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return code
    if a.assert_file:
        code, out = assert_binding(a.assert_file)
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return code
    ap.print_help()
    return 8


if __name__ == "__main__":
    sys.exit(main())
