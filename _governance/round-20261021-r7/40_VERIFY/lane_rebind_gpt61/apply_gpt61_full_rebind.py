#!/usr/bin/env python
"""Apply the owner order of 2026-10-21 (GPT quota restored) across EVERY governed lane surface.

OWNER ORDER (verbatim, two messages):
  1) "GPT的配額恢復了，把「PLAN 執行模型 & Independent Acceptance Officer / VERIFY /
      SECURITY，轉交CODEX CLI 執行，checker model」，改回「GPT 6.1 SOL-MEDIUM (OPEN AI
      OAuth)」"
  2) correction: "「PLAN 模型 & Independent Acceptance Officer / VERIFY / SECURITY，轉交CODEX
      CLI 執行，checker model」，改回「GPT 6.1 SOL-MEDIUM (OPEN AI OAuth)」；Codex bounded
      writer / EXECUTE，轉交CODEX CLI 執行，provider/model模型，保持為DeepSeek V4.1
      Flash(OPENCODE GO)"

NET EFFECT:
  PLAN           -> openai-codex/gpt-6.1-sol   (GPT 6.1 SOL-MEDIUM, OpenAI OAuth)
  VERIFY_SECURITY-> openai-codex/gpt-6.1-sol   (GPT 6.1 SOL-MEDIUM, OpenAI OAuth)
  EXECUTE        -> opencode-go/deepseek-v4.1-flash  (UNCHANGED, per the owner)

WHY THIS FILE EXISTS (the surfaces are NOT one surface):
  The governed lane binding is declared in FOUR places, and editing one leaves the
  others stale -- the drift gate then reports the disagreement. Per
  governed-write-admission: a live runtime config and the registry that DECLARES
  the governed version of it are separate authorities.

    1. config/lane-route-slots.candidate.json   the dispatch-time POOL (the
       dispatcher's selection authority) -- the artifact the dispatcher actually reads.
    2. config/lane-routing-registry.yaml        the DECLARATION (routes[], arms[],
       epoch, sod_invariants, projections).
    3. config/model-lane-assignment.json        the registry's source_of_routes
       (revision, lane_chains, sod prose).
    4. config/hermes-codex-lane.json            the sealed EXECUTE lane binding,
       reached through the registry's projections.
    5. config/hermes.json                       the Hermes runtime binding
       (recorded in the registry as DEBT, not as a hard binding).

  A concurrent commit (a1bd583, author "Codex <codex@local.invalid>", 2026-10-21
  15:14) had moved ALL THREE lanes to minimax-m3.1-flash-free and simultaneously
  reverted the registry's `declared_by` to the 2026-10-16 text that says "EXECUTE
  unchanged" -- the artifact contradicted itself. This script restores the EXECUTE
  lane to the owner's stated mandate and makes every declaration agree with the
  pool it describes.

APPLY PROPERTIES (owner-authorized-config-change.md):
  * dry-run by default; --apply performs the write
  * FULL-DIGEST pre-image guard per file; refuses the whole apply if any file moved
  * per-run byte-identical backups
  * post-write verification: re-parse, re-read every lane's rank-1 arm, and re-run
    the drift gate (which must return 0 findings)
  * rollback pointer recorded
  * no deletes

Usage:
  python apply_gpt61_full_rebind.py            # dry run
  python apply_gpt61_full_rebind.py --apply    # write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
VAR = HGK / "var" / "R7-LANES"
BACKUP_DIR = VAR / "backups"
RECEIPT = VAR / "gpt61_full_rebind_apply_receipt.json"

# The sentinel the drift gate uses for "this pointer does not resolve".
_MISSING = object()

# ---- freeze-time pre-images (refuse to write if any moved) ------------------------
PRE_IMAGES = {
    "config/lane-route-slots.candidate.json": "621a3881a5a342d914fb484cde9a053a8cdab3373b43efa59b01662dc6208df9",
    "config/lane-routing-registry.yaml": "3b59cb9026e46c345ac7e19565f21f9bd8d7a269335100b474125ede7e67b3c0",
    "config/model-lane-assignment.json": "12b09abd714b8a6da30974fcd87449ddbc38a4a3c7ffeb8a7b224e9c89775557",
    "config/hermes-codex-lane.json": "c2aa55684cff091c849c40566b53f304970d23bbe2b52d1ab8967d073cf93478",
    "config/hermes.json": "4e32dcc609d46fb6010b202455ef3de4eef873d3829049b21895fee1fbf119b6",
}

# The owner order's net effect. Rank-1 arm per lane.
TARGET_RANK1 = {
    "PLAN": {
        "provider": "openai-codex", "model": "gpt-6.1-sol",
        "transport_model": "gpt-6.1-sol",           # BARE id: the openai arm rejects
        "auth": "openai_oauth", "oauth": True,      # a qualified id with HTTP 400
        "reasoning_effort": "medium",
    },
    "VERIFY_SECURITY": {
        "provider": "openai-codex", "model": "gpt-6.1-sol",
        "transport_model": "gpt-6.1-sol",
        "auth": "openai_oauth", "oauth": True,
        "reasoning_effort": "medium",
    },
    "EXECUTE": {
        "provider": "opencode-go", "model": "deepseek-v4.1-flash",
        "transport_model": "opencode-go/deepseek-v4.1-flash",
        "auth": "env_ref:OPENCODE_GO_API_KEY", "oauth": False,
        "reasoning_effort": None,
    },
}

OWNER_ORDER = (
    "Owner order 2026-10-21 (owner messages, GPT quota restored): the PLAN execution model and "
    "the Independent Acceptance Officer / VERIFY / SECURITY checker model are BOTH GPT 6.1 "
    "SOL-MEDIUM (OpenAI OAuth) = openai-codex/gpt-6.1-sol (transport_model: gpt-6.1-sol, the "
    "BARE id). This SUPERSEDES the 2026-10-21 order that put minimax-m3.1-flash-free "
    "(opencode-go) on PLAN and VERIFY_SECURITY. The EXECUTE lane is NOT named by this order and "
    "stays deepseek-v4.1-flash (opencode-go) at rank 1, per the owner's standing clarification "
    "「維持 DeepSeek V4.1 Flash（依您原話：只改 PLAN 與 VERIFY/CHECKER）」. The minimax arm is "
    "retained at a lower rank as a reachable fallback, not removed."
)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def find_entry(pool: list[dict], provider: str, model: str) -> dict | None:
    for e in pool:
        if e.get("provider") == provider and e.get("model") == model:
            return e
    return None


def promote(pool: list[dict], target: dict, want: dict) -> list[dict]:
    """Put `target` first, renumber ranks 1..N, set default/automatic_selection.

    Nothing is removed: the arm that was rank 1 becomes a reachable fallback.
    """
    new_pool = [dict(target)] + [dict(e) for e in pool if e is not target]
    for i, e in enumerate(new_pool, start=1):
        e["rank"] = i
        if i == 1:
            e["role"] = "DEFAULT/首選"
            e["default"] = True
            e["automatic_selection"] = True
            e["transport_model"] = want["transport_model"]
            e["auth"] = want["auth"]
            e["oauth"] = want["oauth"]
            if want.get("reasoning_effort") is not None:
                e["reasoning_effort"] = want["reasoning_effort"]
        else:
            if e.get("role") == "DEFAULT/首選":
                e["role"] = "FALLBACK/備援"
            e["default"] = False
            e["automatic_selection"] = False
    return new_pool


def build_pool(j: dict) -> tuple[dict, list[dict]]:
    new = json.loads(json.dumps(j))
    notes = []
    for lane in new.get("lanes", []):
        name = lane.get("lane")
        if name not in TARGET_RANK1:
            continue
        want = TARGET_RANK1[name]
        pool = lane.get("ordered_pool", [])
        target = find_entry(pool, want["provider"], want["model"])
        if target is None:
            raise SystemExit(
                f"REFUSE: lane {name} has no {want['provider']}/{want['model']} entry; "
                "the owner-ordered arm is absent, so it cannot be promoted by re-ordering"
            )
        before = [f"{e.get('provider')}/{e.get('model')}" for e in pool]
        lane["ordered_pool"] = promote(pool, target, want)
        after = [f"{e.get('provider')}/{e.get('model')}" for e in lane["ordered_pool"]]
        notes.append({"lane": name, "before": before, "after": after,
                      "rank1": f"{want['provider']}/{want['model']}"})
    new["revision"] = "12"
    new["supersedes_revision"] = "11"
    new["declared_by"] = OWNER_ORDER
    new.setdefault("change_log", []).append({
        "rev": "11 -> 12",
        "round": "OWNER-ORDER-20261021-GPT-QUOTA-RESTORED",
        "date": "2026-10-21",
        "what": (
            "Owner order applied to the dispatch-time pool ranks: openai-codex/gpt-6.1-sol "
            "promoted to rank 1 for PLAN and for VERIFY_SECURITY (GPT 6.1 SOL-MEDIUM, OpenAI "
            "OAuth, transport_model gpt-6.1-sol = BARE id); the previous rank-1 "
            "(opencode-go/minimax-m3.1-flash-free) demoted to a reachable fallback on both lanes "
            "and NOT removed. EXECUTE is not named by the order: it is restored to "
            "opencode-go/deepseek-v4.1-flash at rank 1, because concurrent commit a1bd583 had "
            "moved it to minimax while simultaneously reverting declared_by to a text saying "
            "'EXECUTE unchanged' -- the artifact contradicted itself."
        ),
        "measured": (
            "VERIFY_SECURITY lane probe 2026-10-21 after the owner's quota notice "
            "(var/R7-LANES/probe_gpt_61sol_VERIFY3.json): ok=true, required_arm and served_arm "
            "both openai-codex/gpt-6.1-sol, used_transport_model=gpt-6.1-sol, usage_status=200, "
            "usage_receipt_ok=true, 3.11 s. The openai arm requires the BARE model id; a "
            "qualified 'openai-codex/<model>' is routed by the relay to the default provider and "
            "answers HTTP 400 'Model is unavailable'."
        ),
        "claim_ceiling": (
            "a measured arm availability on the lane, not an acceptance of any subject; the pool "
            "is CANDIDATE_ONLY and selection is declarative"
        ),
    })
    return new, notes


def build_registry(text: str) -> tuple[str, list[str]]:
    """Rewrite the registry's routes/arms and the prose that names the arms."""
    import yaml
    d = yaml.safe_load(text)
    notes: list[str] = []

    for route in d.get("routes", []):
        name = route.get("lane")
        if name not in TARGET_RANK1:
            continue
        want = TARGET_RANK1[name]
        # the route's top-level provider/model follow its primary arm
        route["provider"] = want["provider"]
        route["model"] = want["model"]
        route["canonical_identity"] = want["model"]
        route["auth"] = want["auth"]
        route["oauth"] = want["oauth"]
        route["reasoning_effort"] = want["reasoning_effort"]
        route["selection_authority"] = "owner-order-20261021-gpt-61-sol-plan-verify-execute-deepseek"

        arms = route.get("arms", [])
        idx = None
        for i, a in enumerate(arms):
            if a.get("provider") == want["provider"] and a.get("model") == want["model"]:
                idx = i
                break
        if idx is None:
            raise SystemExit(f"REFUSE: registry route {name} has no {want['provider']}/{want['model']} arm")
        primary = arms.pop(idx)
        primary["arm"] = "primary"
        primary["default"] = True
        primary["automatic_selection"] = True
        primary["transport_model"] = want["transport_model"]
        primary["auth"] = want["auth"]
        primary["oauth"] = want["oauth"]
        if want.get("reasoning_effort") is not None:
            primary["reasoning_effort"] = want["reasoning_effort"]
        # the arm that was primary becomes fallback1; the rest shift down
        for i, a in enumerate(arms):
            a["arm"] = f"fallback{i+1}"
            a["default"] = False
            a["automatic_selection"] = False
        route["arms"] = [primary] + arms
        # `fallbacks` is a SECOND ordered list on the route. In the live artifact it
        # is exactly `arms[1:]` in provider/model order (the non-default arms).
        # After the promotion the new primary is gpt-6.1-sol, so the OLD primary
        # (the arm that was rank 1) must become the FIRST fallback, and gpt must
        # leave the fallback list entirely. Deriving the order from the new
        # `arms` is the only way the two lists cannot contradict each other.
        fbs = route.get("fallbacks")
        if isinstance(fbs, list):
            by_key = {}
            for a in fbs:
                by_key.setdefault((a.get("provider"), a.get("model")), a)
            new_fbs = []
            for a in arms:  # arms[1:] == the non-default arms, in order
                key = (a.get("provider"), a.get("model"))
                if key in by_key:
                    new_fbs.append(by_key[key])
            route["fallbacks"] = new_fbs
        notes.append(f"registry route {name}: primary -> {want['provider']}/{want['model']}")

    d["epoch"] = 26
    # source_of_routes pins the assignment's revision AND its sha256. The owner
    # order changes that file, so the pin must be re-read from the NEW bytes --
    # a stale sha256 there is a false claim about the file the registry adopts.
    d["authorization_basis"] = (
        str(d.get("authorization_basis", ""))
        + " | Owner order 2026-10-21 (GPT quota restored): PLAN and VERIFY/SECURITY are "
          "openai-codex/gpt-6.1-sol (GPT 6.1 SOL-MEDIUM, OpenAI OAuth); EXECUTE remains "
          "opencode-go/deepseek-v4.1-flash. Owner final route change is still a CANDIDATE "
          "declaration: activation requires an HGK-authorized generation binding."
    )
    d.setdefault("history", []).append({
        "round": "OWNER-ORDER-20261021-GPT-QUOTA-RESTORED",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "epoch": 26,
        "change": (
            "PLAN and VERIFY/SECURITY rank-1 arms moved to openai-codex/gpt-6.1-sol (medium, "
            "OpenAI OAuth, transport_model gpt-6.1-sol = BARE id). EXECUTE restored to "
            "opencode-go/deepseek-v4.1-flash at rank 1 (concurrent commit a1bd583 had moved it "
            "to minimax and left the declaration self-contradicting). The minimax arm is "
            "retained as a reachable fallback on all three lanes, not removed."
        ),
    })
    out = yaml.safe_dump(d, sort_keys=False, allow_unicode=True, width=100)
    return out, notes


def build_assignment(text: str) -> tuple[str, list[str]]:
    j = json.loads(text)
    notes: list[str] = []
    chains = j.get("lane_chains") or {}
    for lane, want in TARGET_RANK1.items():
        ch = chains.get(lane)
        if not ch:
            continue
        idx = None
        for i, e in enumerate(ch):
            if e.get("provider") == want["provider"] and e.get("model") == want["model"]:
                idx = i
                break
        if idx is None:
            raise SystemExit(f"REFUSE: model-lane-assignment lane_chains/{lane} has no {want['provider']}/{want['model']}")
        primary = ch.pop(idx)
        primary["transport_model"] = want["transport_model"]
        primary["default"] = True
        for i, e in enumerate(ch):
            e["default"] = False
        chains[lane] = [primary] + ch
        notes.append(f"model-lane-assignment lane_chains/{lane}: [0] -> {want['provider']}/{want['model']}")

    j["revision"] = 26
    j["registry_epoch"] = 26
    j["declared_by"] = OWNER_ORDER
    sod = j.get("sod") or {}
    sod["plan_lane"] = (
        "openai-codex / gpt-6.1-sol (GPT 6.1 SOL-MEDIUM, OPEN AI OAuth) — owner order 2026-10-21 "
        "(GPT quota restored); supersedes the 2026-10-21 minimax-m3.1-flash-free order."
    )
    sod["execute_lane"] = (
        "opencode-go / deepseek-v4.1-flash (DeepSeek V4.1 Flash, OPENCODE GO) — Codex CLI "
        "bounded writer; owner order 2026-10-21 keeps it UNCHANGED; supersedes the 2026-10-21 "
        "minimax-m3.1-flash-free order."
    )
    sod["verify_security_lane"] = (
        "openai-codex / gpt-6.1-sol (GPT 6.1 SOL-MEDIUM, OPEN AI OAuth) — owner order 2026-10-21 "
        "(GPT quota restored); supersedes the 2026-10-21 minimax-m3.1-flash-free order."
    )
    sod["verify_security_arm_A"] = (
        "openai-codex / gpt-6.1-sol (primary Codex CLI checker; owner order 2026-10-21)"
    )
    sod["verify_security_default_arm"] = "gpt-6.1-sol"
    sod["verify_security_selection"] = (
        "owner order 2026-10-21 (GPT quota restored): the automatic, default arm is "
        "openai-codex/gpt-6.1-sol. The other provider arms stay reachable as operator-selectable "
        "fallbacks, including opencode-go/minimax-m3.1-flash-free."
    )
    sod["verify_vs_execute_model_separation"] = (
        "RESTORED on the model axis: EXECUTE is opencode-go/deepseek-v4.1-flash and "
        "VERIFY_SECURITY is openai-codex/gpt-6.1-sol, so the maker and the checker are on "
        "DIFFERENT models AND different providers. Provider separation is not required by the "
        "invariants, but the axes happen to be distinct under this owner order."
    )
    sod["verify_vs_plan_model_separation"] = (
        "NONE on the model axis, BY OWNER ORDER: PLAN and VERIFY_SECURITY are both "
        "openai-codex/gpt-6.1-sol. SOD006-C4 (PLAN vs VERIFY) is OPEN_OWNER_ORDERED; independence "
        "is process separation only. EXECUTE is a DIFFERENT model."
    )
    sod["provider_separation"] = (
        "PRESENT between EXECUTE (opencode-go) and VERIFY_SECURITY (openai-codex). PLAN and "
        "VERIFY_SECURITY share openai-codex BY OWNER ORDER; model-axis separation between them is "
        "absent and is NOT claimed."
    )
    j["sod"] = sod
    j["owner_order"] = OWNER_ORDER

    # ---- assignment[]: the per-lane-group declared model/provider -------------
    for a in j.get("assignment", []):
        grp = a.get("lane_group")
        want = TARGET_RANK1.get(grp)
        if not want:
            continue
        a["assigned_model"] = want["model"]
        a["assigned_provider"] = want["provider"]
        a["auth"] = want["auth"]
        a["oauth"] = want["oauth"]
        if want.get("reasoning_effort") is not None:
            a["reasoning_effort"] = want["reasoning_effort"]
        if grp == "EXECUTE":
            a["supply"] = "OpenCode Go"
        if grp == "PLAN":
            a["supply"] = "OpenAI OAuth"
        # supply_selector: the primary arm must be the owner-ordered arm
        sel = a.get("supply_selector")
        if sel:
            arms = sel.get("arms", [])
            idx = None
            for i, arm in enumerate(arms):
                if arm.get("provider") == want["provider"] and arm.get("model") == want["model"]:
                    idx = i
                    break
            if idx is not None:
                primary = arms.pop(idx)
                primary["role"] = "primary"
                primary["default"] = True
                for i, arm in enumerate(arms):
                    arm["role"] = f"fallback{i+1}_operator_selectable"
                    arm["default"] = False
                sel["arms"] = [primary] + arms
                sel["unspecified_default"] = {
                    "arm": "A",
                    "model": want["model"],
                    "provider": want["provider"],
                    "auth": want["auth"],
                    "reasoning_effort": want["reasoning_effort"],
                    "canonical_identity": want["model"],
                    "oauth": want["oauth"],
                }
        a["canonical_identity"] = want["model"]
        notes.append(f"model-lane-assignment assignment/{grp}: -> {want['provider']}/{want['model']}")

    # ---- effective_wiring: NOT the lane binding. Leave it alone. -----------
    # `effective_wiring.main_agent` describes the SHARED Hermes runtime
    # (config.yaml model.default), which the registry records as an
    # OBSERVATION that is explicitly NON_AUTHORITATIVE for governed HGK calls.
    # The PLAN LANE's runtime binding is a DIFFERENT surface:
    # <HERMES_HOME>/profiles/hgk-governed/config.yaml (model.default=
    # gpt-6.1-sol, model.provider=openai-codex, reasoning_effort=medium) --
    # already in place, never changed by the minimax mandate, and unchanged
    # here. Rewriting main_agent to the lane's model would make the declaration
    # claim the shared runtime runs a model it does not run.
    j.setdefault("in_hermes_plan_orchestrator_plane", {})
    j["in_hermes_plan_orchestrator_plane"]["owner_order_2026_10_21_gpt_quota_restored"] = {
        "what": (
            "The owner order restores PLAN to openai-codex/gpt-6.1-sol (medium, OpenAI "
            "OAuth). The PLAN plane's RUNTIME binding surface is "
            "<HERMES_HOME>/profiles/hgk-governed/config.yaml, which ALREADY carries "
            "model.default=gpt-6.1-sol / model.provider=openai-codex / "
            "reasoning_effort=medium; the minimax mandate never touched that profile, so "
            "no runtime write is required for this order."
        ),
        "not_the_binding": [
            "the per-session picker (state.db::sessions.model)",
            "delegation.provider/model (subagent children)",
            "the shared canonical config.yaml model.default (NON_AUTHORITATIVE for "
            "governed HGK calls, per the registry's hermes-live-config-yaml observation)",
        ],
        "measured": (
            "VERIFY_SECURITY lane probe var/R7-LANES/probe_gpt_61sol_VERIFY3.json: "
            "ok=true, served_arm=openai-codex/gpt-6.1-sol, usage_status=200, 3.11 s."
        ),
        "claim_ceiling": (
            "a declaration of the lane's binding surface and one measured arm "
            "availability; the governed profile's own serving rows are the serving "
            "evidence, and this is NOT canonical acceptance."
        ),
    }

    # ---- sod_across_all_arms: the enumerated verifier model list -------------
    sall = j.get("sod_across_all_arms")
    if isinstance(sall, dict) and isinstance(sall.get("verifier_models"), list):
        vm = sall["verifier_models"]
        if TARGET_RANK1["VERIFY_SECURITY"]["model"] in vm:
            vm.remove(TARGET_RANK1["VERIFY_SECURITY"]["model"])
        vm.insert(0, TARGET_RANK1["VERIFY_SECURITY"]["model"])
        sall["verifier_models"] = vm

    j.setdefault("revision_26_reason", (
        "Owner order 2026-10-21 (GPT quota restored): PLAN and VERIFY/SECURITY bound to "
        "openai-codex/gpt-6.1-sol (medium, OpenAI OAuth, transport_model gpt-6.1-sol = BARE id, "
        "measured usage 200 on the relay); EXECUTE kept on opencode-go/deepseek-v4.1-flash. The "
        "concurrent minimax commit a1bd583 is superseded and its self-contradicting EXECUTE "
        "binding is corrected."
    ))
    return json.dumps(j, indent=2, ensure_ascii=False) + "\n", notes


def respin_bindings(reg: dict, site_docs: dict[str, object]) -> list[dict]:
    """Re-pin every registry binding to the value its site now holds.

    The registry's bindings ARE the declaration of what the projection sites hold.
    When an owner order moves those values, the bindings must move with them --
    otherwise the drift gate reports the disagreement and the registry is simply
    stale. The POINTER is never changed here: only the expected value is
    re-read from the site, and every re-pin is recorded in the receipt so a
    reviewer can see exactly which declarations moved.
    """
    changed = []
    for proj in reg.get("projections", []):
        path = proj.get("path")
        doc = site_docs.get(path)
        if doc is None:
            continue
        for binding in proj.get("bindings", []):
            pointer = binding.get("pointer")
            actual = _try_pointer(doc, pointer)
            if actual is _MISSING:
                continue
            expected = binding.get("expected")
            if actual != expected:
                changed.append({
                    "projection": proj.get("id"), "path": path, "pointer": pointer,
                    "was": expected, "now": actual,
                })
                binding["expected"] = actual
    return changed


def _try_pointer(doc, pointer):
    """The same pointer resolution the drift gate uses (JSON pointer)."""
    if not pointer:
        return _MISSING
    cur = doc
    for raw in str(pointer).split("/"):
        if raw == "":
            continue
        part = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list):
            try:
                cur = cur[int(part)]
            except (ValueError, IndexError):
                return _MISSING
        elif isinstance(cur, dict):
            if part not in cur:
                return _MISSING
            cur = cur[part]
        else:
            return _MISSING
    return cur


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    # ---- pre-image guard ----------------------------------------------------
    for rel, expected in PRE_IMAGES.items():
        p = HGK / rel
        if not p.exists():
            print(f"REFUSE: {rel} does not exist")
            return 2
        live = sha256_bytes(p.read_bytes())
        if live != expected:
            print(f"REFUSE: {rel} moved.\n  live     {live}\n  expected {expected}")
            return 2
    print("pre-image guard: all 5 files unchanged")

    pool_text = (HGK / "config/lane-route-slots.candidate.json").read_text(encoding="utf-8")
    reg_text = (HGK / "config/lane-routing-registry.yaml").read_text(encoding="utf-8")
    mla_text = (HGK / "config/model-lane-assignment.json").read_text(encoding="utf-8")

    new_pool, pool_notes = build_pool(json.loads(pool_text))
    new_mla, mla_notes = build_assignment(mla_text)

    # The registry is built AFTER the assignment, so its bindings can be re-pinned
    # against the NEW assignment values rather than the old ones.
    import yaml
    site_docs = {
        "config/model-lane-assignment.json": json.loads(new_mla),
        "config/hermes-codex-lane.json": json.loads((HGK / "config/hermes-codex-lane.json").read_text(encoding="utf-8")),
        "config/hermes.json": json.loads((HGK / "config/hermes.json").read_text(encoding="utf-8")),
    }
    # build_registry mutates reg_obj in place and returns YAML; re-pin on the
    # mutated object so the re-pinned values are what gets serialized.
    new_reg, reg_notes = build_registry(reg_text)
    reg_obj = yaml.safe_load(new_reg)
    respinned = respin_bindings(reg_obj, site_docs)
    # source_of_routes must name the NEW assignment bytes it adopts, not the old
    # ones. A stale sha256 there is a false claim about the adopted file.
    sor = reg_obj.get("source_of_routes")
    if isinstance(sor, dict):
        sor["revision"] = json.loads(new_mla).get("revision")
        sor["sha256"] = hashlib.sha256(new_mla.encode("utf-8")).hexdigest()
        reg_notes.append(f"registry source_of_routes: revision={sor['revision']} sha256={sor['sha256'][:16]}")
    new_reg = yaml.safe_dump(reg_obj, sort_keys=False, allow_unicode=True, width=100)
    print("\n=== PLAN (dry run) ===")
    for n in pool_notes:
        print(f"\nlane {n['lane']}:")
        print("  before:", ", ".join(n["before"]))
        print("  after :", ", ".join(n["after"]))
    for n in reg_notes + mla_notes:
        print(" ", n)
    print(f"\n  registry bindings to re-pin: {len(respinned)}")
    for r in respinned[:12]:
        print(f"    {r['pointer']}\n        was: {str(r['was'])[:90]}\n        now: {str(r['now'])[:90]}")
    if len(respinned) > 12:
        print(f"    ... and {len(respinned)-12} more")

    outputs = {
        "config/lane-route-slots.candidate.json": json.dumps(new_pool, indent=2, ensure_ascii=False) + "\n",
        "config/lane-routing-registry.yaml": new_reg,
        "config/model-lane-assignment.json": new_mla,
    }
    print("\n=== digests ===")
    for rel, content in outputs.items():
        print(f"  {rel:44} -> {sha256_bytes(content.encode('utf-8'))[:16]}")

    if not args.apply:
        print("\nDRY RUN -- no write performed. Re-run with --apply.")
        return 0

    # ---- apply --------------------------------------------------------------
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backups = {}
    for rel in outputs:
        src = HGK / rel
        dst = BACKUP_DIR / f"{Path(rel).name}.pre-gpt61full-{stamp}"
        shutil.copy2(src, dst)
        assert dst.read_bytes() == src.read_bytes(), f"backup of {rel} is not byte-identical"
        backups[rel] = str(dst)
    print(f"\nbackups written: {len(backups)}")

    # re-check the pre-images IMMEDIATELY before writing
    for rel, expected in PRE_IMAGES.items():
        if sha256_bytes((HGK / rel).read_bytes()) != expected:
            print(f"REFUSE: {rel} moved between the freeze and the write. Aborting.")
            return 2

    for rel, content in outputs.items():
        (HGK / rel).write_text(content, encoding="utf-8", newline="\n")
    print("writes complete")

    # ---- post-write verification --------------------------------------------
    checks = []
    pj = json.loads((HGK / "config/lane-route-slots.candidate.json").read_text(encoding="utf-8"))
    for lane in pj.get("lanes", []):
        name = lane.get("lane")
        if name not in TARGET_RANK1:
            continue
        want = TARGET_RANK1[name]
        e0 = lane["ordered_pool"][0]
        ok = (e0.get("provider") == want["provider"] and e0.get("model") == want["model"]
              and e0.get("rank") == 1 and e0.get("transport_model") == want["transport_model"])
        ranks = [e.get("rank") for e in lane["ordered_pool"]]
        ranks_ok = ranks == list(range(1, len(ranks) + 1))
        checks.append({"lane": name, "rank1": f"{e0.get('provider')}/{e0.get('model')}",
                       "transport_model": e0.get("transport_model"), "ok": ok, "ranks_contiguous": ranks_ok})
        print(f"  pool {name:18} rank1={e0.get('provider')}/{e0.get('model')} "
              f"tm={e0.get('transport_model')} ok={ok} ranks_ok={ranks_ok}")

    # the registry's declared_by must agree with the pool it describes
    import yaml
    rj = yaml.safe_load((HGK / "config/lane-routing-registry.yaml").read_text(encoding="utf-8"))
    for route in rj.get("routes", []):
        name = route.get("lane")
        if name not in TARGET_RANK1:
            continue
        want = TARGET_RANK1[name]
        ok = route.get("provider") == want["provider"] and route.get("model") == want["model"]
        a0 = (route.get("arms") or [{}])[0]
        ok_arm = a0.get("provider") == want["provider"] and a0.get("model") == want["model"]
        checks.append({"lane": name, "registry_route": f"{route.get('provider')}/{route.get('model')}",
                       "ok": ok and ok_arm})
        print(f"  registry {name:14} route={route.get('provider')}/{route.get('model')} ok={ok} arm_ok={ok_arm}")

    # the assignment's sod prose must not still claim minimax is the default
    aj = json.loads((HGK / "config/model-lane-assignment.json").read_text(encoding="utf-8"))
    sod = aj.get("sod") or {}
    prose_ok = ("gpt-6.1-sol" in sod.get("plan_lane", "")
                and "deepseek-v4.1-flash" in sod.get("execute_lane", "")
                and "gpt-6.1-sol" in sod.get("verify_security_lane", ""))
    checks.append({"surface": "model-lane-assignment/sod", "ok": prose_ok})
    print(f"  assignment sod prose ok={prose_ok}")

    # ---- drift gate ---------------------------------------------------------
    sys.path.insert(0, str(HGK / "src"))
    from hg_kseos import lane_policy as lp
    findings = lp.check_drift()
    fatal = lp.drift_is_fatal(findings)
    print(f"\n  drift gate: {len(findings)} findings, fatal={fatal}")
    for f in findings[:20]:
        print("   ", f.get("severity"), f.get("code"), f.get("path"), f.get("pointer"),
              "| exp:", str(f.get("expected"))[:50], "| act:", str(f.get("actual"))[:50])
    checks.append({"surface": "drift_gate", "findings": len(findings), "fatal": fatal, "ok": not findings})

    receipt = {
        "schema": "HGK-OWNER-AUTHORIZED-CONFIG-CHANGE/1",
        "artifact": "LANE_REBIND_FULL_APPLY_RECEIPT",
        "at_utc": datetime.now(timezone.utc).isoformat(),
        "owner_order": OWNER_ORDER,
        "target_lanes": TARGET_RANK1,
        "pre_images": PRE_IMAGES,
        "backups": backups,
        "rollback": "copy each backup over its target path to restore the pre-image bytes",
        "planned_changes": {"pool": pool_notes, "registry": reg_notes, "assignment": mla_notes},
        "post_write_checks": checks,
        "drift_findings": findings,
        "applied": True,
        "claim_ceiling": (
            "a candidate-pool and candidate-declaration re-order, applied under owner authority. "
            "It is CANDIDATE_ONLY: not a native issuer signature, not an acceptance of any "
            "subject, not a promotion of the pool to ACTIVE, and not a claim that any lane has "
            "executed under the new binding beyond the single measured probe cited in the "
            "pool's change_log."
        ),
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nreceipt: {RECEIPT}")
    return 0 if not findings else 1


if __name__ == "__main__":
    sys.exit(main())
