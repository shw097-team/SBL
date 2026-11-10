"""FHS-3L&M — the hard entry contract for lane and model routing (repaired, r27).

This file does **not** own routing and must not become a second routing authority. It reads the existing
HG-KSEOS control plane (`config/lane-route-slots.candidate.json` pool and
`config/lane-routing-registry.yaml` epoch + retirement ledger) read-only, and answers three questions for
anyone about to run an FHS task:

    1. what may I choose, per lane?      -> `--menu`   (the owner's selectable menu, slot by slot)
    2. may this exact choice be used?    -> `--bind`   (fail-closed, writes one session-unique binding)
    3. is that binding still true?       -> `--assert` (re-reads the plane, refuses on any drift)

The distinction the owner asked for is preserved: a lane binding is a **control-plane fact**, a session pin
is a **conversation setting**. `--bind` never touches the registry and never writes a session pin; it only
records that, at this numeric epoch, the chosen arm was admitted for that lane. `--assert` re-reads the same
single registry and the same merged retirement ledger and fails closed if anything moved.

Repair notes (r27; EC-R26-002 defect 1 plus the E02/E03/E04/E08 holes):
  * no hardcoded control-plane path: `--hgk-root` -> env `HGK_ROOT` -> discovery file
    `config/hgk-root.txt` beside this tool -> `ERR_HGK_ROOT_UNRESOLVED` (a path is never guessed);
  * the epoch is the registry's top-level `epoch:` parsed as an **integer** (`ERR_EPOCH_UNRESOLVED` when it
    is absent or non-numeric), plus `status:` and `contract_epoch:` when present;
  * a binding is **session-unique and non-overwriting**: `lanes/bindings/<run_id>/<lane>_<slot>_<nonce>.json`
    created with `O_CREAT|O_EXCL`; a repeat of the same run+session+lane+slot is `BINDING_ALREADY_EXISTS`;
  * the record carries a **dual digest**: `binding_id` over the canonical body (a hand edit is detectable)
    and the plane digests `registry_sha256` / `pool_sha256` / `retired_ledger_sha256` (a plane move is
    detectable), reported as different codes;
  * the retirement ledger is read from BOTH the pool and the registry's `retired_arms:` section; a
    disagreement between them, or a retired arm still listed in a lane pool, is `HOLD_REGISTRY_POOL_DRIFT`,
    not a pass.

Exit codes: 0 ok, 2 slot/arm not on the owner's menu, 6 arm not in the lane's pool (or left it),
7 epoch/pool/ledger drift, an expired binding, or an unreadable epoch; 8 bad input / unresolved or invalid
HGK root / a tampered or incomplete binding record; 9 the arm is retired and must never be selected;
10 the binding already exists (collision, never overwritten).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROUND = HERE.parent
BINDING_ROOT = ROUND / "lanes" / "bindings"
DISCOVERY_CANDIDATES = (HERE / "config" / "hgk-root.txt", ROUND / "config" / "hgk-root.txt")
REGISTRY_REL = pathlib.Path("config") / "lane-routing-registry.yaml"
POOL_REL = pathlib.Path("config") / "lane-route-slots.candidate.json"
TZ = datetime.timezone(datetime.timedelta(hours=8))
DEFAULT_TTL_SECONDS = 3600

# Codes and the exit status each one carries. No code may carry a status outside this table, so every
# refusal is machine-readable and none of them is an uncaught traceback.
EXIT_FOR = {
    "OK": 0,
    "UNKNOWN_LANE": 2,
    "UNKNOWN_SLOT": 2,
    "MENU_SLOT_MISMATCH": 2,
    "NOT_IN_LANE_POOL": 6,
    "ARM_LEFT_POOL": 6,
    "ARM_NOT_IN_ANY_POOL": 6,
    "EPOCH_DRIFT": 7,
    "POOL_DIGEST_DRIFT": 7,
    "RETIRED_LEDGER_DRIFT": 7,
    "HOLD_REGISTRY_POOL_DRIFT": 7,
    "BINDING_EXPIRED": 7,
    "ERR_EPOCH_UNRESOLVED": 7,
    "ERR_HGK_ROOT_UNRESOLVED": 8,
    "ERR_HGK_ROOT_INVALID": 8,
    "ERR_BAD_INPUT": 8,
    "BINDING_TAMPERED": 8,
    "BINDING_INCOMPLETE": 8,
    "BINDING_UNREADABLE": 8,
    "BINDING_SCHEMA_UNSUPPORTED": 8,
    "RETIRED_ARM": 9,
    "BINDING_ALREADY_EXISTS": 10,
}

# The owner's menu, in the owner's order. `model` is the name a human reads. This table is the owner's
# declaration, not a routing decision taken by this tool.
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
RUN_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


# --------------------------------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------------------------------
def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canonical(obj) -> bytes:
    """Canonical JSON: sorted keys, no insignificant whitespace. Every digest here is taken over this."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def now() -> str:
    return datetime.datetime.now(TZ).isoformat(timespec="seconds")


def parse_iso(s: str) -> datetime.datetime:
    d = datetime.datetime.fromisoformat(s)
    return d if d.tzinfo else d.replace(tzinfo=TZ)


def arm_of(provider: str, model: str) -> str:
    return f"{provider}/{model}"


class Refused(Exception):
    """A typed refusal that ends the command with a named code and its documented exit status."""

    def __init__(self, code: str, **detail):
        super().__init__(code)
        self.code = code
        self.payload = {"ok": False, "error": code, "exit": EXIT_FOR[code], **detail}


# --------------------------------------------------------------------------------------------------
# discovery: where is the control plane?
# --------------------------------------------------------------------------------------------------
def resolve_root(explicit):
    """--hgk-root -> HGK_ROOT -> discovery file -> fail closed. No path is ever guessed."""
    if explicit:
        return pathlib.Path(explicit).expanduser().resolve(), "--hgk-root"
    env = os.environ.get("HGK_ROOT")
    if env:
        return pathlib.Path(env).expanduser().resolve(), "env:HGK_ROOT"
    for cand in DISCOVERY_CANDIDATES:
        if cand.is_file():
            lines = cand.read_text(encoding="utf-8").strip().splitlines()
            line = next((x.strip() for x in lines if x.strip() and not x.strip().startswith("#")), "")
            if line:
                return pathlib.Path(line).expanduser().resolve(), f"discovery_file:{cand}"
    raise Refused(
        "ERR_HGK_ROOT_UNRESOLVED",
        tried={"hgk_root_flag": False, "env_HGK_ROOT": None,
               "discovery_files": [str(p) for p in DISCOVERY_CANDIDATES]},
        fix=("pass --hgk-root <HG-KSEOS clone>, or set HGK_ROOT, or ship config/hgk-root.txt beside this "
             "tool; this contract will not guess a control-plane path"),
    )


def validate_root(root, source):
    missing = [str(root / rel) for rel in (REGISTRY_REL, POOL_REL) if not (root / rel).is_file()]
    if missing:
        raise Refused("ERR_HGK_ROOT_INVALID", hgk_root=str(root), discovery_source=source, missing=missing,
                      fix="the resolved root must be an HG-KSEOS clone carrying both config files")


# --------------------------------------------------------------------------------------------------
# control plane: ONE read of ONE registry and ONE pool, consumed by every subcommand
# --------------------------------------------------------------------------------------------------
def scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v in ("", "null", "~"):
        return None
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v


def parse_registry(txt):
    """Minimal, schema-tolerant reader for the top-level scalars and the `retired_arms:` section.

    stdlib only: the control plane ships YAML, but the lane entry path is not allowed to grow a dependency,
    so this reads exactly the shapes it consumes and nothing else.
    """
    out = {"retired_arms": {}}
    lines = txt.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" "))
        if indent != 0:
            i += 1
            continue
        if stripped.endswith(":"):
            key = stripped[:-1].strip()
            i += 1
            if key != "retired_arms":
                continue
            while i < len(lines):
                l2 = lines[i]
                s2 = l2.strip()
                if not s2 or s2.startswith("#"):
                    i += 1
                    continue
                ind2 = len(l2) - len(l2.lstrip(" "))
                if ind2 == 0:
                    break
                if ind2 == 2 and s2.endswith(":"):
                    arm = s2[:-1].strip().strip("\"'")
                    entry = {}
                    i += 1
                    while i < len(lines):
                        l3 = lines[i]
                        s3 = l3.strip()
                        if not s3 or s3.startswith("#"):
                            i += 1
                            continue
                        ind3 = len(l3) - len(l3.lstrip(" "))
                        if ind3 <= 2:
                            break
                        if ":" in s3:
                            k3, v3 = s3.split(":", 1)
                            entry[k3.strip()] = scalar(v3)
                        i += 1
                    out["retired_arms"][arm] = entry
                    continue
                i += 1
            continue
        if ":" in stripped:
            key, val = stripped.split(":", 1)
            out[key.strip()] = scalar(val)
        i += 1
    return out


def load_plane(explicit_root):
    root, source = resolve_root(explicit_root)
    validate_root(root, source)
    reg_raw = (root / REGISTRY_REL).read_bytes()
    pool_raw = (root / POOL_REL).read_bytes()
    reg = parse_registry(reg_raw.decode("utf-8", "replace"))
    try:
        pool_doc = json.loads(pool_raw)
    except Exception as exc:  # noqa: BLE001
        raise Refused("ERR_HGK_ROOT_INVALID", hgk_root=str(root), discovery_source=source,
                      detail=f"pool is not JSON: {exc}") from exc

    epoch = reg.get("epoch")
    if not isinstance(epoch, int) or isinstance(epoch, bool):
        raise Refused("ERR_EPOCH_UNRESOLVED", hgk_root=str(root), discovery_source=source,
                      registry_sha256=sha(reg_raw), observed=reg.get("epoch"),
                      fix=("the registry must carry a top-level integer `epoch:`; a missing or non-numeric "
                           "epoch means no numeric epoch can reach the binding, so the binding is refused"))

    pool_ledger = dict(pool_doc.get("retired_arms") or {})
    reg_ledger = dict(reg.get("retired_arms") or {})

    # Two ledgers may not disagree about WHAT is retired and WHAT replaces it. Free-text `reason` is
    # documentation and is deliberately not compared: the two files word it differently.
    def norm(d):
        return {a: (e.get("retired_epoch"), e.get("replacement")) for a, e in d.items()}

    if pool_ledger and reg_ledger and norm(pool_ledger) != norm(reg_ledger):
        raise Refused(
            "HOLD_REGISTRY_POOL_DRIFT", hgk_root=str(root), discovery_source=source, epoch=epoch,
            registry_sha256=sha(reg_raw), pool_sha256=sha(pool_raw),
            registry_ledger=norm(reg_ledger), pool_ledger=norm(pool_ledger),
            rule="the pool and the registry disagree about the retirement ledger; a hold, not a pass",
        )

    ledger = dict(pool_ledger)
    ledger.update(reg_ledger)
    ledger_source = {
        "pool": "config/lane-route-slots.candidate.json#retired_arms" if pool_ledger else None,
        "registry": "config/lane-routing-registry.yaml#retired_arms" if reg_ledger else None,
    }

    lanes = {ln["lane"]: ln for ln in pool_doc.get("lanes", []) if isinstance(ln, dict) and "lane" in ln}
    live = {}
    for lane, body in lanes.items():
        for e in body.get("ordered_pool", []):
            live.setdefault(arm_of(e.get("provider"), e.get("model")), []).append(
                {"lane": lane, "rank": e.get("rank")})

    drift = {arm: live[arm] for arm in ledger if arm in live}
    if drift:
        raise Refused(
            "HOLD_REGISTRY_POOL_DRIFT", hgk_root=str(root), discovery_source=source, epoch=epoch,
            registry_sha256=sha(reg_raw), pool_sha256=sha(pool_raw),
            retired_but_still_pooled=drift,
            rule=("a retired arm is still listed in a lane pool: the registry and the pool disagree, so "
                  "every answer built on this plane is withheld rather than reported as a pass"),
        )

    return {
        "hgk_root": str(root),
        "discovery_source": source,
        "registry_sha256": sha(reg_raw),
        "policy_epoch": epoch,
        "epoch": epoch,
        "epoch_status": reg.get("status"),
        "contract_epoch": reg.get("contract_epoch"),
        "pool_sha256": sha(pool_raw),
        "pool_schema": pool_doc.get("schema"),
        "pool_status": pool_doc.get("status"),
        "pool_lanes": lanes,
        "retired_ledger": ledger,
        "retired_ledger_source": ledger_source,
        "retired_ledger_sha256": sha(canonical(ledger)),
        "live_arm_sites": len(live),
    }


def pool_hit(plane, lane, provider, model):
    body = plane["pool_lanes"].get(LANE_ALIAS.get(lane, lane)) or {}
    return next((e for e in body.get("ordered_pool", [])
                 if e.get("provider") == provider and e.get("model") == model), None)


# --------------------------------------------------------------------------------------------------
# --menu
# --------------------------------------------------------------------------------------------------
def menu(plane):
    lanes = []
    total = admitted_total = 0
    for lane, slots in MENU.items():
        rows = []
        for s in slots:
            hit = pool_hit(plane, lane, s["provider"], s["model"])
            rows.append({**s, "admitted": hit is not None,
                         "pool_rank": hit.get("rank") if hit else None,
                         "transport_model": hit.get("transport_model") if hit else None,
                         "why_not": None if hit else "NOT_IN_LANE_POOL"})
            total += 1
            admitted_total += 1 if hit else 0
        lanes.append({"lane": lane, "pool_lane": LANE_ALIAS.get(lane, lane), "slots": rows})
    return {
        "schema": "FHS.3LM.Menu/2",
        "generated_at": now(),
        "hgk_root": plane["hgk_root"],
        "discovery_source": plane["discovery_source"],
        # numeric, at the top level, so no reader has to guess which of two epoch fields is the epoch
        "policy_epoch": plane["epoch"],
        "epoch_status": plane["epoch_status"],
        "contract_epoch": plane["contract_epoch"],
        "registry_sha256": plane["registry_sha256"],
        "pool_sha256": plane["pool_sha256"],
        "retired_ledger_sha256": plane["retired_ledger_sha256"],
        "retired_arms": sorted(plane["retired_ledger"]),
        "epoch": {"policy_epoch": plane["epoch"], "status": plane["epoch_status"],
                  "contract_epoch": plane["contract_epoch"],
                  "registry_sha256": plane["registry_sha256"]},
        "slot_count": total,
        "admitted_count": admitted_total,
        "all_admitted": total == admitted_total,
        "lanes": lanes,
        "rule": ("choose a slot; a slot whose arm is not in the lane pool is shown but refused "
                 "(NOT_IN_LANE_POOL) — adding an arm is a control-plane epoch change, not something this "
                 "task may do"),
    }


# --------------------------------------------------------------------------------------------------
# --bind
# --------------------------------------------------------------------------------------------------
def nonce_for(run_id, session_id, lane, slot):
    """Deterministic per (run, session, lane, slot).

    A random nonce would make a repeated bind look like a fresh binding and quietly create a second record
    for the same claim. Deriving it means: a different session gets a different file (two sessions in one
    slot cannot overwrite each other), and the same session gets the same path, so a repeat is an O_EXCL
    collision that is refused rather than an overwrite.
    """
    return sha(f"fhs3lm-nonce/1|{run_id}|{session_id}|{lane}|{slot}".encode("utf-8"))[:16]


def scan_same_arm(run_dir, provider, model, lane, slot):
    hits = []
    if not run_dir.is_dir():
        return hits
    for p in sorted(run_dir.glob("*.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if rec.get("provider") == provider and rec.get("model") == model:
            if rec.get("lane") != lane or rec.get("slot") != slot:
                hits.append(f"{rec.get('lane')}/{rec.get('slot')}")
    return sorted(set(hits))


def write_exclusive(path, payload):
    """Create-or-refuse. `O_CREAT|O_EXCL` is the whole collision guard: the name is claimed at creation, so a
    second writer is refused with BINDING_ALREADY_EXISTS instead of overwriting the first record."""
    data = (json.dumps(payload, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(path), os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_BINARY", 0), 0o644)
    except FileExistsError as exc:
        raise Refused("BINDING_ALREADY_EXISTS", path=str(path),
                      fix=("bindings are never overwritten; use a new --run-id/--session-id, or --assert the "
                           "existing record")) from exc
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    if path.read_bytes() != data:  # pragma: no cover - a filesystem fault, not a governance path
        raise Refused("BINDING_UNREADABLE", path=str(path), detail="readback differs from written bytes")


def bind(lane, slot, run_id, session_id, work_id, ttl, plane, allow_fallback=False):
    if lane not in MENU:
        raise Refused("UNKNOWN_LANE", lane=lane, known=sorted(MENU))
    slot_row = next((s for s in MENU[lane] if s["slot"] == slot), None)
    if slot_row is None:
        raise Refused("UNKNOWN_SLOT", lane=lane, slot=slot, known=[s["slot"] for s in MENU[lane]])

    arm = arm_of(slot_row["provider"], slot_row["model"])
    if arm in plane["retired_ledger"]:
        ent = plane["retired_ledger"][arm]
        raise Refused("RETIRED_ARM", lane=lane, slot=slot, arm=arm,
                      replacement=ent.get("replacement"), why=ent.get("reason"),
                      retired_epoch=ent.get("retired_epoch"), ordered_by=ent.get("ordered_by"),
                      ledger_source=plane["retired_ledger_source"],
                      rule="a retired arm is never selected, not even as a fallback; the replacement is named")

    hit = pool_hit(plane, lane, slot_row["provider"], slot_row["model"])
    if hit is None:
        if allow_fallback:
            fallback = next((s for s in MENU[lane]
                             if pool_hit(plane, lane, s["provider"], s["model"])), None)
            if fallback is not None:
                out = bind(lane, fallback["slot"], run_id, session_id, work_id, ttl, plane, False)
                out["fallback_from"] = slot
                out["fallback_reason"] = "NOT_IN_LANE_POOL"
                return out
        raise Refused("NOT_IN_LANE_POOL", lane=lane, slot=slot, arm=arm,
                      fix=("the pool for this lane has no such arm; adding one is an owner-ordered registry "
                           "epoch change. This task refuses rather than editing routing it does not own."))

    run_dir = BINDING_ROOT / run_id
    nonce = nonce_for(run_id, session_id, lane, slot)
    path = run_dir / f"{lane}_{slot}_{nonce}.json"

    bound = datetime.datetime.now(TZ).replace(microsecond=0)
    expires = bound + datetime.timedelta(seconds=ttl)
    same_arm_with = scan_same_arm(run_dir, slot_row["provider"], slot_row["model"], lane, slot)

    body = {
        "schema": "FHS.3LM.Binding/2",
        "run_id": run_id,
        "session_id": session_id,
        "work_id": work_id,
        "lane": lane,
        "slot": slot,
        "label": slot_row["label"],
        "pool_lane": LANE_ALIAS.get(lane, lane),
        "provider": slot_row["provider"],
        "model": slot_row["model"],
        "transport_model": hit.get("transport_model"),
        "pool_rank": hit.get("rank"),
        "policy_epoch": plane["epoch"],
        "epoch_status": plane["epoch_status"],
        "contract_epoch": plane["contract_epoch"],
        "registry_sha256": plane["registry_sha256"],
        "pool_sha256": plane["pool_sha256"],
        "retired_ledger_sha256": plane["retired_ledger_sha256"],
        "hgk_root": plane["hgk_root"],
        "discovery_source": plane["discovery_source"],
        "nonce": nonce,
        "nonce_derivation": "sha256('fhs3lm-nonce/1|run_id|session_id|lane|slot')[:16]",
        "ttl_seconds": ttl,
        "bound_at": bound.isoformat(timespec="seconds"),
        "expires_at": expires.isoformat(timespec="seconds"),
        "same_arm_lanes": bool(same_arm_with),
        "same_arm_with": same_arm_with,
        "sod_mandated": False,
        "plane": "LANE_CONTROL_PLANE",
        "not_a_session_pin": True,
        "not_a_session_pin_detail": ("a session pin in the desktop app is a conversation setting and does "
                                     "not bind a lane; this record is the lane binding, and only this record "
                                     "is read by --assert"),
    }
    binding_id = sha(canonical(body))
    record = {**body, "binding_id": binding_id}
    write_exclusive(path, record)
    return {"bound": True, "ok": True, "binding_id": binding_id,
            "path": str(path.relative_to(ROUND)).replace(os.sep, "/"), "record": record}


# --------------------------------------------------------------------------------------------------
# --assert
# --------------------------------------------------------------------------------------------------
def assert_binding(binding_path, plane):
    p = pathlib.Path(binding_path)
    if not p.is_absolute():
        p = pathlib.Path.cwd() / p
    try:
        raw = p.read_bytes()
        rec = json.loads(raw.decode("utf-8"))
    except FileNotFoundError as exc:
        raise Refused("BINDING_UNREADABLE", path=str(p), detail="no such binding file") from exc
    except Exception as exc:  # noqa: BLE001
        raise Refused("BINDING_UNREADABLE", path=str(p), detail=str(exc)) from exc
    if not isinstance(rec, dict):
        raise Refused("BINDING_UNREADABLE", path=str(p), detail="record is not a JSON object")
    if rec.get("schema") != "FHS.3LM.Binding/2":
        raise Refused("BINDING_SCHEMA_UNSUPPORTED", path=str(p), schema=rec.get("schema"),
                      supported=["FHS.3LM.Binding/2"],
                      fix="a /1 record carries no session, nonce or binding_id; re-bind through --bind")

    claimed = rec.get("binding_id")
    body = {k: v for k, v in rec.items() if k != "binding_id"}
    recomputed = sha(canonical(body))
    if claimed != recomputed:
        raise Refused("BINDING_TAMPERED", path=str(p), binding_id_claimed=claimed,
                      binding_id_recomputed=recomputed, binding_file_sha256=sha(raw),
                      rule=("binding_id is the sha256 of the canonical record body; a field that no longer "
                            "matches it was edited outside this contract"))

    required = ("run_id", "session_id", "work_id", "lane", "slot", "provider", "model", "policy_epoch",
                "registry_sha256", "pool_sha256", "nonce", "expires_at", "plane")
    missing = [k for k in required if k not in rec]
    if (missing or not isinstance(rec.get("run_id"), str) or not rec["run_id"].strip()
            or not isinstance(rec.get("session_id"), str) or not rec["session_id"].strip()):
        raise Refused("BINDING_INCOMPLETE", path=str(p), missing=missing,
                      run_id=rec.get("run_id"), session_id=rec.get("session_id"),
                      rule=("a binding without run/session identity, or without its plane fields, proves "
                            "nothing about who bound what"))

    lane, slot = rec["lane"], rec["slot"]
    arm = arm_of(rec["provider"], rec["model"])

    if rec["registry_sha256"] != plane["registry_sha256"] or rec["policy_epoch"] != plane["epoch"]:
        raise Refused("EPOCH_DRIFT", path=str(p), bound_registry_sha256=rec["registry_sha256"],
                      now_registry_sha256=plane["registry_sha256"],
                      bound_policy_epoch=rec["policy_epoch"], now_policy_epoch=plane["epoch"],
                      rule="any edit to the registry changes its digest; re-bind through --bind")

    if rec["pool_sha256"] != plane["pool_sha256"]:
        raise Refused("POOL_DIGEST_DRIFT", path=str(p), bound_pool_sha256=rec["pool_sha256"],
                      now_pool_sha256=plane["pool_sha256"],
                      rule="the lane pool moved since the binding; a digest that does not match is a drift")

    if arm in plane["retired_ledger"]:
        ent = plane["retired_ledger"][arm]
        raise Refused("RETIRED_ARM", path=str(p), arm=arm, replacement=ent.get("replacement"),
                      why=ent.get("reason"), retired_epoch=ent.get("retired_epoch"),
                      ledger_source=plane["retired_ledger_source"])

    if pool_hit(plane, lane, rec["provider"], rec["model"]) is None:
        raise Refused("ARM_LEFT_POOL", path=str(p), arm=arm, lane=lane,
                      pool_lane=LANE_ALIAS.get(lane, lane),
                      rule="the arm this record binds is no longer in that lane's ordered_pool")

    slot_row = next((s for s in MENU.get(lane, []) if s["slot"] == slot), None)
    if slot_row is None or slot_row["provider"] != rec["provider"] or slot_row["model"] != rec["model"]:
        raise Refused("MENU_SLOT_MISMATCH", path=str(p), lane=lane, slot=slot, bound_arm=arm,
                      menu_arm=(arm_of(slot_row["provider"], slot_row["model"]) if slot_row else None),
                      rule="the record's lane/slot no longer resolves to the arm it names")

    if datetime.datetime.now(TZ) >= parse_iso(rec["expires_at"]):
        raise Refused("BINDING_EXPIRED", path=str(p), bound_at=rec["bound_at"],
                      expires_at=rec["expires_at"], ttl_seconds=rec.get("ttl_seconds"), now=now(),
                      fix="re-bind with a fresh --ttl; an expired binding is not evidence of a current lane")

    return {"ok": True, "binding_ok": True, "path": str(p),
            "run_id": rec["run_id"], "session_id": rec["session_id"], "work_id": rec.get("work_id"),
            "lane": lane, "slot": slot, "arm": arm, "pool_rank": rec["pool_rank"],
            "policy_epoch": rec["policy_epoch"], "registry_sha256": rec["registry_sha256"],
            "pool_sha256": rec["pool_sha256"], "binding_id": rec["binding_id"], "nonce": rec["nonce"],
            "expires_at": rec["expires_at"], "same_arm_lanes": rec.get("same_arm_lanes", False),
            "retired_ledger_sha256_bound": rec.get("retired_ledger_sha256"),
            "retired_ledger_sha256_now": plane["retired_ledger_sha256"],
            "retired_ledger_changed": rec.get("retired_ledger_sha256") != plane["retired_ledger_sha256"],
            "epoch_unchanged": True, "pool_unchanged": True, "arm_pooled": True, "not_retired": True}


# --------------------------------------------------------------------------------------------------
# --assert-arm
# --------------------------------------------------------------------------------------------------
def assert_arm(arm, plane):
    ent = plane["retired_ledger"].get(arm)
    if ent is not None:
        raise Refused("RETIRED_ARM", arm=arm, replacement=ent.get("replacement"), why=ent.get("reason"),
                      retired_epoch=ent.get("retired_epoch"), ordered_by=ent.get("ordered_by"),
                      ledger_source=plane["retired_ledger_source"])
    hits = [(name, e.get("rank")) for name, body in plane["pool_lanes"].items()
            for e in body.get("ordered_pool", []) if arm_of(e.get("provider"), e.get("model")) == arm]
    if not hits:
        raise Refused("ARM_NOT_IN_ANY_POOL", arm=arm,
                      pools={k: [arm_of(e.get("provider"), e.get("model"))
                                 for e in v.get("ordered_pool", [])]
                             for k, v in plane["pool_lanes"].items()})
    return {"ok": True, "arm": arm, "lanes": hits, "policy_epoch": plane["epoch"],
            "registry_sha256": plane["registry_sha256"], "pool_sha256": plane["pool_sha256"],
            "retired": False}


# --------------------------------------------------------------------------------------------------
# cli
# --------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="FHS-3L&M hard entry contract (reads HG-KSEOS, owns no routing)")
    ap.add_argument("--hgk-root", help="path to the HG-KSEOS clone (else HGK_ROOT, else config/hgk-root.txt)")
    ap.add_argument("--menu", action="store_true")
    ap.add_argument("--plane", action="store_true",
                    help="print the resolved control plane and stop (read-only)")
    ap.add_argument("--bind", nargs=2, metavar=("LANE", "SLOT"))
    ap.add_argument("--run-id")
    ap.add_argument("--session-id")
    ap.add_argument("--work-id")
    ap.add_argument("--ttl", type=int, default=DEFAULT_TTL_SECONDS,
                    help="binding lifetime in seconds (default %d)" % DEFAULT_TTL_SECONDS)
    ap.add_argument("--assert", dest="assert_file")
    ap.add_argument("--assert-arm", metavar="PROVIDER/MODEL",
                    help="refuse a retired arm outright (exit 9) and say what replaced it")
    ap.add_argument("--allow-fallback", action="store_true",
                    help=("if the chosen slot's arm is not in the lane pool, bind the next admitted slot and "
                          "record it"))
    a = ap.parse_args(argv)

    try:
        if a.menu:
            print(json.dumps(menu(load_plane(a.hgk_root)), ensure_ascii=False, indent=1))
            return 0
        if a.plane:
            plane = load_plane(a.hgk_root)
            shown = {k: v for k, v in plane.items() if k != "pool_lanes"}
            shown["pool_lanes"] = {k: [arm_of(e.get("provider"), e.get("model"))
                                       for e in v.get("ordered_pool", [])]
                                   for k, v in plane["pool_lanes"].items()}
            print(json.dumps({"ok": True, **shown}, ensure_ascii=False, indent=1))
            return 0
        if a.assert_arm:
            print(json.dumps(assert_arm(a.assert_arm, load_plane(a.hgk_root)),
                             ensure_ascii=False, indent=1))
            return 0
        if a.bind:
            missing = [k for k, v in (("--run-id", a.run_id), ("--session-id", a.session_id)) if not v]
            if missing:
                raise Refused("ERR_BAD_INPUT", missing=missing,
                              fix=("--bind requires --run-id and --session-id; an anonymous binding cannot be "
                                   "session-unique"))
            if not RUN_ID_RE.fullmatch(a.run_id):
                raise Refused("ERR_BAD_INPUT", run_id=a.run_id,
                              rule="run_id must match ^[A-Za-z0-9._-]{1,64}$")
            if a.ttl < 0:
                raise Refused("ERR_BAD_INPUT", ttl=a.ttl, rule="ttl is seconds and may not be negative")
            out = bind(a.bind[0], a.bind[1], a.run_id, a.session_id, a.work_id, a.ttl,
                       load_plane(a.hgk_root), a.allow_fallback)
            print(json.dumps(out, ensure_ascii=False, indent=1))
            return 0
        if a.assert_file:
            print(json.dumps(assert_binding(a.assert_file, load_plane(a.hgk_root)),
                             ensure_ascii=False, indent=1))
            return 0
        ap.print_help()
        return 8
    except Refused as r:
        print(json.dumps(r.payload, ensure_ascii=False, indent=1))
        return r.payload["exit"]


if __name__ == "__main__":
    sys.exit(main())
