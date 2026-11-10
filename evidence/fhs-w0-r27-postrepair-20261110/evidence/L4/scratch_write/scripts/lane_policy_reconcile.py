#!/usr/bin/env python3
"""Project the one lane policy onto every file that declares it.

`config/lane-routing-registry.yaml` is the authority (`source_of_routes`). The same policy is
declared again in `config/model-lane-assignment.json` (`lane_chains`) and in
`config/lane-route-slots.candidate.json` (`ordered_pool`). On 2026-10-30 the three disagreed:
the registry said PLAN rank-1 = gpt-6.1-sol, the assignment still said deepseek, and the slot pool
said deepseek — so the conformance test failed against the file it was meant to certify, and a
reader believed whichever file it opened first.

This tool makes the copies projections:

  * it derives `lane_chains` and each lane's `ordered_pool` from the registry;
  * it preserves per-arm metadata already present in the slot pool (auth, transport notes, effort)
    by keying on (provider, model), so a rank change does not lose provenance;
  * it refuses to write a chain that contradicts itself (rank-1 repeated inside its own fallbacks,
    duplicate arms);
  * it records the epoch digest it projected from, so a later reader can tell which policy the
    file came from.

Usage:
    python scripts/lane_policy_reconcile.py --check     # exit 2 when any declaration has drifted
    python scripts/lane_policy_reconcile.py --write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "lane-routing-registry.yaml"
ASSIGNMENT = ROOT / "config" / "model-lane-assignment.json"
SLOTS = ROOT / "config" / "lane-route-slots.candidate.json"

# per-lane arm metadata that only the slot pool carries; kept when projecting
CARRY_KEYS = ("auth", "oauth", "reasoning_effort", "transport_vocabulary_note",
              "probe_note", "provenance", "canonical_identity")


def transport_for(provider: str, model: str) -> str:
    """The transport token follows the provider's declared vocabulary, never a remembered string.

    Measured defect: after the epoch-40 rebind the VERIFY_SECURITY route still carried the epoch-39
    `transport_model: opencode-go/mimo-v2.6-flash` while provider/model said openai-codex/gpt-6.1-sol. The
    projection copied it faithfully, so the slot pool DECLARED gpt-6.1-sol and would have SENT MiMo -- the exact
    "sends one arm, declares another" class this file exists to prevent. Deriving the token from the provider
    (openai-codex takes a bare model id; everything else is provider/model) makes a stale field unable to lie.
    """
    return model if provider == "openai-codex" else f"{provider}/{model}"


def arms_of(registry: dict) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for route in registry["routes"]:
        lane = route["lane"]
        chain = [{"provider": route["provider"], "model": route["model"],
                  "transport_model": transport_for(route["provider"], route["model"])}]
        chain += [{"provider": f["provider"], "model": f["model"],
                   "transport_model": transport_for(f["provider"], f["model"])}
                  for f in route.get("fallbacks", [])]
        out[lane] = chain
    return out


def validate(chains: dict[str, list[dict]]) -> list[str]:
    problems: list[str] = []
    for lane, chain in chains.items():
        seen = set()
        for i, arm in enumerate(chain):
            key = (arm["provider"], arm["model"])
            if key in seen:
                problems.append(f"{lane}: duplicate arm {key[0]}/{key[1]} at position {i}")
            seen.add(key)
        if len({(a["provider"], a["model"]) for a in chain}) != len(chain):
            problems.append(f"{lane}: chain is not a set of distinct arms")
    return problems


ARM_LETTERS = "ABCDEFGH"


def project_chains(chains: dict[str, list[dict]], efforts: dict[str, str | None]) -> dict[str, list[dict]]:
    """Emit the projection shape the drift checker binds: every declared field must exist.

    A missing key is a COVERAGE_GAP, not a "false" -- that distinction is why the checker refused a
    projection that looked correct to a human reader.
    """
    out = {}
    for lane, chain in chains.items():
        out[lane] = []
        for i, arm in enumerate(chain):
            row = dict(arm)
            row["arm"] = ARM_LETTERS[i]
            row["role"] = "primary" if i == 0 else f"fallback{i}"
            row["default"] = i == 0
            row["automatic_selection"] = i == 0
            row["reasoning_effort"] = efforts.get(lane) if i == 0 else None
            out[lane].append(row)
    return out


def project_pool(chains: dict[str, list[dict]], slots: dict) -> tuple[dict, bool]:
    changed = False
    existing = {lane["lane"]: lane for lane in slots.get("lanes", [])}
    for lane, chain in chains.items():
        if lane not in existing:
            continue
        node = existing[lane]
        by_key = {(e.get("provider"), e.get("model")): e for e in node.get("ordered_pool", [])}
        pool = []
        for i, arm in enumerate(chain):
            key = (arm["provider"], arm["model"])
            base = dict(by_key.get(key, {}))
            base.update({"rank": i + 1, "provider": arm["provider"], "model": arm["model"],
                         "transport_model": arm.get("transport_model", arm["model"])})
            for k in CARRY_KEYS:
                if k in by_key.get(key, {}):
                    base[k] = by_key[key][k]
            base["role"] = "DEFAULT/首選" if i == 0 else f"FALLBACK{i}/備援{i}"
            base["default"] = i == 0
            base["automatic_selection"] = i == 0
            pool.append(base)
        if [[p["provider"], p["model"]] for p in node.get("ordered_pool", [])] != \
           [[p["provider"], p["model"]] for p in pool]:
            changed = True
        node["ordered_pool"] = pool
    return slots, changed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if a.check == a.write:
        print("choose exactly one of --check / --write")
        return 64

    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    assignment = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    slots = json.loads(SLOTS.read_text(encoding="utf-8"))

    chains = arms_of(registry)
    efforts = {r["lane"]: r.get("reasoning_effort") for r in registry["routes"]}
    problems = validate(chains)
    if problems:
        print(json.dumps({"verdict": "REGISTRY_CONTRADICTS_ITSELF", "problems": problems},
                         ensure_ascii=False, indent=1))
        return 2

    chains = project_chains(chains, efforts)
    projected_slots, slots_changed = project_pool(chains, slots)

    dirty = {}
    cur = assignment.get("lane_chains", {})
    for lane, chain in chains.items():
        if [[c.get("provider"), c.get("model")] for c in cur.get(lane, [])] != \
           [[c["provider"], c["model"]] for c in chain]:
            dirty.setdefault("assignment", []).append(lane)
    if slots_changed:
        dirty.setdefault("slot_pool", []).append("*")

    epoch_digest = hashlib.sha256(REGISTRY.read_bytes()).hexdigest()
    if a.check:
        out = {"verdict": "DRIFT" if dirty else "CONSISTENT", "dirty": dirty,
               "registry_epoch": registry.get("epoch"), "registry_sha256": epoch_digest}
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return 2 if dirty else 0

    assignment["lane_chains"] = chains
    assignment["lane_chains_projected_from"] = {
        "source": "config/lane-routing-registry.yaml",
        "epoch": registry.get("epoch"),
        "sha256": epoch_digest,
        "projected_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "rule": "lane_chains and the slot pool are projections; edit the registry, then re-run this tool",
    }
    projected_slots["revision"] = int(projected_slots.get("revision", 0)) + 1
    projected_slots["supersedes_revision"] = int(projected_slots.get("revision", 0))
    projected_slots.setdefault("change_log", []).append({
        "rev": projected_slots["revision"],
        "at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "reason": ("projected from lane-routing-registry epoch "
                   f"{registry.get('epoch')}: the owner order of 2026-10-24 puts PLAN and "
                   "VERIFY/SECURITY rank 1 on openai-codex/gpt-6.1-sol and keeps EXECUTE on "
                   "opencode-go/deepseek-v4.1-flash; the demoted primary stays reachable as fallback 1"),
        "evidence": f"config/lane-routing-registry.yaml sha256 {epoch_digest}",
    })
    projected_slots["status"] = "CANDIDATE"

    ASSIGNMENT.write_text(json.dumps(assignment, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    SLOTS.write_text(json.dumps(projected_slots, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"verdict": "PROJECTED", "dirty": dirty, "registry_epoch": registry.get("epoch"),
                      "registry_sha256": epoch_digest[:16], "slot_pool_revision": projected_slots["revision"]},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
