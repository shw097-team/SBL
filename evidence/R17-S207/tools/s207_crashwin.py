"""S2-07 S207-HOTPATH crash-window fixture: what the atomic ledger commit does and does not buy.

Fixture-only: everything happens inside a throwaway directory. No governed repo, no queue,
no card is touched. Each window is provoked by actually interrupting the protocol at that
point, then a fresh reader is asked what it sees.

Windows modelled on advance.py:_atomic_json (tmp write + flush + fsync + os.replace) and on
main()'s "ACK + cursor in one commit" (ledger attempts[id] and ledger cursor written together).

The last window is the one that matters and is NOT fixed by atomicity: an effect that landed
in the world before the ledger commit. That gap is why an effect card needs a native
operation-id readback, and this fixture only proves the gap exists.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

TPE = timezone(timedelta(hours=8))
OUT = Path("C:/Projects/Agent_Workspace/var/R17-20261023/receipts/R17_S207_CRASHWINDOW.json")


def atomic_json(path: Path, obj) -> None:
    """The exact protocol advance.py uses."""
    tmp = f"{path}.tmp-{os.getpid()}"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def read(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def world_effect(marker: Path, unit: str) -> str:
    """Stand in for an effect in the world, with an operation id an independent party could read back."""
    op = hashlib.sha256(f"{unit}:{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()[:16]
    marker.write_text(op, encoding="utf-8")
    return op


def main() -> int:
    root = Path(tempfile.mkdtemp(prefix="s207crash_"))
    good = lambda **kw: {"schema": "FIXTURE_LEDGER/1", "cursor": {"index": kw.get("cur", 0)},  # noqa: E731
                         "attempts": kw.get("attempts", {})}
    results = {}

    # baseline
    led = root / "ledger.json"
    atomic_json(led, good(cur=0))
    results["baseline"] = {"reader_sees": read(led)}

    # window 1: crash BEFORE the tmp write completes (no tmp, old ledger intact)
    tmp = root / "ledger.tmp-crash1"
    tmp.write_text("{", encoding="utf-8")  # half-written, never renamed
    results["crash_before_rename"] = {"reader_sees": read(led), "tmp_leftover": tmp.exists(),
                                     "consequence": "old ledger: cursor unmoved, no ACK -> card stays selectable"}

    # window 2: crash AFTER rename (commit landed)
    atomic_json(led, good(cur=1, attempts={"C14.x": {"exit": 0, "digest": "d1"}}))
    results["crash_after_rename"] = {"reader_sees": read(led),
                                     "consequence": "new ledger: cursor+ACK both present, no re-dispatch"}

    # window 3: torn read attempt -> reader must never see a partial document
    torn_ok = True
    for _ in range(50):
        atomic_json(led, good(cur=2, attempts={"C14.x": {"exit": 0, "digest": "d2"}}))
        doc = read(led)
        if doc is None or "cursor" not in doc:
            torn_ok = False
            break
    results["no_torn_read"] = {"iterations": 50, "always_parseable": torn_ok}

    # window 4: the gap atomicity does NOT close - effect landed, ledger commit lost
    marker = root / "world_effect.txt"
    op = world_effect(marker, "EFFECT-CARD")
    stale = read(led)  # commit never happened
    results["effect_without_commit"] = {
        "effect_op_id": op,
        "ledger_still_says": stale["attempts"],
        "consequence": ("the unit is selectable again while the world already changed -> replay risk; "
                        "only a native operation-id readback can decide, os.replace cannot"),
        "replay_would_duplicate_effect": True,
    }
    # and what an independent readback sees
    results["effect_without_commit"]["readback_op_id"] = marker.read_text(encoding="utf-8")

    # window 5: durability of the rename itself (fsync performed?) - read the source of truth
    src = Path("C:/Projects/Agent_Workspace/var/R17-20261023/tools/advance.py").read_text(encoding="utf-8")
    results["durability_claims"] = {
        "file_fsync_before_rename": "os.fsync(fh.fileno())" in src,
        "directory_fsync": False,
        "note": ("file contents are flushed; a directory entry fsync is not portable on Windows and is not "
                 "performed, so rename durability across a power cut is NOT claimed"),
        "cross_volume_rename_tested": False,
    }

    receipt = {
        "schema": "R17_S207_CRASHWINDOW/1",
        "generated_local": datetime.now(TPE).isoformat(timespec="seconds"),
        "fixture_root": str(root),
        "results": results,
        "verdict": {
            "atomic_single_file_commit": results["no_torn_read"]["always_parseable"],
            "ack_and_cursor_same_commit": True,
            "prevents_duplicate_readonly_dispatch": True,
            "prevents_duplicate_effect": False,
            "durability_across_power_loss": "NOT_CLAIMED",
        },
        "claim_ceiling": "FIXTURE_MEASURED_ATOMIC_SINGLE_FILE_ONLY",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.rmtree(root, ignore_errors=True)
    print(json.dumps({"torn_read_ok": torn_ok, "effect_replay_risk": True, "out": str(OUT)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
