"""Typed capability-delta ABI for HGK native upgrades (R14-TS08).

The round needs an answer to a question that install/doctor output cannot answer: *which HGK capabilities can be
reused as they are, which need an adapter, which are missing, and which need a native upgrade?* Adapters must not
be able to claim a native capability they merely wrap, so the delta is typed and every row carries its evidence.

Application semantics (the negative cases the command document demands, all enforced here rather than documented):
  * replay        - a delta whose nonce was already applied is refused (ERR_DELTA_REPLAY)
  * expiry        - a delta past `expires_at` is refused (ERR_DELTA_EXPIRED)
  * partial effect- an item failing mid-apply rolls back every applied item; nothing is left half-installed
                    (ERR_DELTA_PARTIAL_EFFECT, with the rolled-back ids named)
  * rollback      - every applied delta returns a rollback pointer that removes exactly its items

Nothing here issues a permit and nothing here upgrades code: a NEEDS_NATIVE_UPGRADE row is a *finding*, and the
only way to clear it is a scoped HGK root WorkOrder.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

REUSE_AS_IS = "REUSE_AS_IS"
REUSE_WITH_ADAPTER = "REUSE_WITH_ADAPTER"
MISSING = "MISSING"
NEEDS_NATIVE_UPGRADE = "NEEDS_NATIVE_UPGRADE"

SCHEMA = "HGK-CAPABILITY-DELTA/1"

# The capabilities the command document asks about, each with the symbol that proves it exists natively.
CAPABILITIES = [
    # Symbols were CALIBRATED against the modules, not guessed: a first pass used invented names
    # (resolve_route/admit/validate_transition) and the instrument reported three false NEEDS_NATIVE_UPGRADE
    # rows. A measuring device that has not been calibrated invents work.
    ("lane_routing", "src/hg_kseos/lane_policy.py", "route_for_lane"),
    ("lane_admission", "src/hg_kseos/lane_admission.py", "decide_status"),
    ("workorder_spine", "src/hg_kseos/spine.py", "record_workorder_result"),
    ("lease_exclusion", "src/hg_kseos/spine.py", "acquire_lease"),
    ("lifecycle_transitions", "src/hg_kseos/lifecycle.py", "def transition"),
    ("knowledge_repoint", "src/hg_kseos/knowledge.py", "repoint_source"),
    ("delta_abi", "src/hg_kseos/capability_delta.py", "apply_delta"),
]


SURFACE_SKIP = ("_", "main")


def surface(root: Path) -> list[dict]:
    """Every public function/method in src/hg_kseos, with whether any test names it.

    The curated CAPABILITIES list answers "can we reuse the seven things we happen to care about". This answers
    "what does the native surface actually consist of, and what is untested" - without it the delta can be green
    while most of the surface has never been exercised.
    """
    import re
    tests_text = chr(10).join(p.read_text(encoding="utf-8", errors="replace")
                              for p in (Path(root) / "tests").glob("test_*.py"))
    rows = []
    for mod in sorted((Path(root) / "src/hg_kseos").glob("*.py")):
        if mod.name.startswith("_"):
            continue
        text = mod.read_text(encoding="utf-8", errors="replace")
        for name in sorted(set(re.findall(r"^\s*def ([a-zA-Z][a-zA-Z0-9_]*)", text, re.M))):
            if name.startswith(SURFACE_SKIP):
                continue
            rows.append({"module": f"src/hg_kseos/{mod.name}", "symbol": name,
                         "state": "REUSE_AS_IS" if name in tests_text else "UNTESTED_SURFACE",
                         "tested": name in tests_text})
    return rows


def _now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def compute(root: Path) -> dict:
    """Measure the native surface. A capability is REUSE_AS_IS only if the module AND the symbol exist."""
    rows = []
    for name, rel, symbol in CAPABILITIES:
        p = Path(root) / rel
        if not p.is_file():
            rows.append({"capability": name, "state": MISSING, "module": rel, "symbol": symbol,
                         "evidence": "module absent"})
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        probe = symbol if symbol.startswith("def ") else f"def {symbol}"
        has_symbol = probe + "(" in text or probe + " (" in text
        tests = list((Path(root) / "tests").glob(f"test_*{name.split('_')[0]}*.py"))
        if has_symbol:
            rows.append({"capability": name, "state": REUSE_AS_IS, "module": rel, "symbol": symbol,
                         "evidence": f"{rel}:{probe}; tests={[t.name for t in tests]}",
                         "adapter_required": False})
        else:
            rows.append({"capability": name, "state": NEEDS_NATIVE_UPGRADE, "module": rel, "symbol": symbol,
                         "evidence": f"{rel} exists but exports no {symbol}", "adapter_required": True})
    counts = {}
    for r in rows:
        counts[r["state"]] = counts.get(r["state"], 0) + 1
    surf = surface(root)
    surf_counts: dict[str, int] = {}
    for r in surf:
        surf_counts[r["state"]] = surf_counts.get(r["state"], 0) + 1
    return {"schema": SCHEMA, "generated_at": _now(), "rows": rows, "counts": counts,
            "surface": {"total": len(surf), "counts": surf_counts, "rows": surf},
            "adapter_is_not_a_native_upgrade": True}


def _ensure(con: sqlite3.Connection) -> None:
    con.executescript("""
    CREATE TABLE IF NOT EXISTS capability_deltas (
        delta_id TEXT PRIMARY KEY, nonce TEXT UNIQUE, expires_at TEXT, applied_at TEXT, rollback_pointer TEXT);
    CREATE TABLE IF NOT EXISTS capability_delta_items (
        delta_id TEXT, item_id TEXT, capability TEXT, state TEXT, payload TEXT,
        PRIMARY KEY (delta_id, item_id));
    """)


class DeltaRefused(Exception):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail

    def receipt(self) -> dict:
        return {"schema": "HGK-DELTA-DENIED/1", "code": self.code, "detail": self.detail, "applied": False}


def apply_delta(db: Path, delta: dict, *, now: str | None = None, fail_item: str | None = None) -> dict:
    """Apply atomically. Any refusal leaves the spine byte-identical to before the call."""
    now = now or _now()
    if delta.get("schema") != SCHEMA:
        raise DeltaRefused("ERR_DELTA_SCHEMA", str(delta.get("schema")))
    expires = delta.get("expires_at")
    if expires and expires < now:
        raise DeltaRefused("ERR_DELTA_EXPIRED", f"expires {expires} < now {now}")
    items = delta.get("items") or []
    if not items:
        raise DeltaRefused("ERR_DELTA_EMPTY", "a delta must carry at least one item")
    digest = hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()
    delta_id = delta.get("delta_id") or f"DELTA-{digest[:16]}"
    nonce = delta.get("nonce") or delta_id
    con = sqlite3.connect(db)
    try:
        _ensure(con)
        if con.execute("SELECT 1 FROM capability_deltas WHERE nonce=?", (nonce,)).fetchone():
            raise DeltaRefused("ERR_DELTA_REPLAY", f"nonce {nonce} already applied")
        applied: list[str] = []
        try:
            for it in items:
                if fail_item and it.get("item_id") == fail_item:
                    raise RuntimeError("injected failure")
                con.execute("INSERT INTO capability_delta_items VALUES (?,?,?,?,?)",
                            (delta_id, it["item_id"], it.get("capability", ""), it.get("state", ""),
                             json.dumps(it, sort_keys=True)))
                applied.append(it["item_id"])
        except Exception as exc:  # partial effect must not survive
            con.rollback()
            raise DeltaRefused("ERR_DELTA_PARTIAL_EFFECT",
                               f"{exc}: rolled back {len(applied)} applied item(s) {applied}") from exc
        rollback_pointer = f"RB-{delta_id}"
        con.execute("INSERT INTO capability_deltas VALUES (?,?,?,?,?)",
                    (delta_id, nonce, expires, now, rollback_pointer))
        con.commit()
    finally:
        con.close()
    return {"schema": "HGK-DELTA-APPLIED/1", "delta_id": delta_id, "nonce": nonce,
            "items_applied": [i["item_id"] for i in items], "applied": True,
            "rollback_pointer": rollback_pointer, "applied_at": now,
            "evidence_digest": "sha256:" + digest}


def rollback(db: Path, delta_id: str) -> dict:
    con = sqlite3.connect(db)
    try:
        _ensure(con)
        row = con.execute("SELECT rollback_pointer FROM capability_deltas WHERE delta_id=?", (delta_id,)).fetchone()
        if row is None:
            raise DeltaRefused("ERR_DELTA_UNKNOWN", delta_id)
        removed = con.execute("SELECT item_id FROM capability_delta_items WHERE delta_id=?", (delta_id,)).fetchall()
        con.execute("DELETE FROM capability_delta_items WHERE delta_id=?", (delta_id,))
        con.execute("DELETE FROM capability_deltas WHERE delta_id=?", (delta_id,))
        con.commit()
    finally:
        con.close()
    return {"schema": "HGK-DELTA-ROLLED-BACK/1", "delta_id": delta_id, "rollback_pointer": row[0],
            "items_removed": [r[0] for r in removed], "rolled_back": True}
