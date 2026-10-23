"""The checker must not invent time: every clock names the field it came from.

Two regressions are pinned here.

1. A receipt with no timestamp field is UNKNOWN, never "old". An old file mtime
   must not buy a SUPERSEDED that the receipt body cannot support: UNKNOWN is a
   VIOLATION, however stale the file is.
2. A pool time read from the declaration file's mtime is a labelled fallback,
   so any SUPERSEDED verdict built on it carries ``superseded_confidence: LOW``.
   A time read from the pool's own revision record carries ``HIGH``.

The checker is imported from its exact path, unmodified: these tests observe the
predicate, they do not re-describe it.
"""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from datetime import datetime, timezone

CHECKER = (
    r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
    r"/tools/check_lane_consistency.py"
)

# The pool served today, in both label forms the checker itself passes in.
POOL = ["gpt-6.1-sol", "openai-codex/gpt-6.1-sol"]

# A retired arm the curated list does declare -- so only the missing time can
# stop it from being excused as history.
RETIRED_ARM = "opencode-go/minimax-m3.1-flash-free"
PRIOR_ARMS = [RETIRED_ARM, "minimax-m3.1-flash-free"]

RECEIPT_TIME = "2026-10-01T00:00:00+00:00"
POOL_TIME = "2026-10-20T00:00:00+00:00"


def _checker():
    """Load the checker by exact path; nothing is monkeypatched."""
    spec = importlib.util.spec_from_file_location(
        "check_lane_consistency_time_sources", CHECKER
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_missing_receipt_timestamp_is_a_violation_not_a_supersession():
    """An old file with no timestamp inside it is UNKNOWN, and UNKNOWN is red."""
    checker = _checker()
    receipt = {
        "lane": "EXECUTE",
        "attempts": [{"rank": 1, "model": RETIRED_ARM}],
    }

    # Only the receipt body is consulted: both fields come back empty.
    stamp, source = checker.receipt_time_from_receipt(receipt)
    assert stamp is None, "a receipt with no time field must read as UNKNOWN"
    assert source is None

    with tempfile.TemporaryDirectory() as scratch:
        path = os.path.join(scratch, "EXECUTE__NO_TIME.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(receipt, handle)
        # An old mtime is exactly the trap: it must not become the time.
        os.utime(path, (0, 0))
        assert os.path.getmtime(path) < 1_600_000_000

        # The helper receives what the body yields -- None -- even though an old
        # file exists on disk. If the checker read mtime, this would SUPERSEDE.
        verdict, reason = checker.classify_arm_with_reason(
            receipt["attempts"][0]["model"],
            POOL,
            stamp,
            POOL_TIME,
            PRIOR_ARMS,
        )

    assert verdict == checker.VIOLATION
    assert reason == checker.REASON_UNKNOWN_TIME


def _receipt():
    """A green turn that served a retired arm: only the pool time is in question."""
    return {
        "lane": "EXECUTE",
        "generated_utc": RECEIPT_TIME,
        "attempts": [{
            "rank": 1,
            "model": RETIRED_ARM,
            "transport_model": RETIRED_ARM,
            "usage_model": RETIRED_ARM,
            "provider": "opencode-go",
            "usage_provider": "opencode-go",
            "nonce_present": True,
            "exit": 0,
        }],
    }


def _evaluate(checker, declaration, pool_time, pool_time_source):
    table = {
        "EXECUTE": {
            1: {
                "rank": 1,
                "provider": "openai-codex",
                "model": "gpt-6.1-sol",
                "source": "test",
                "notes": [],
            }
        }
    }
    return checker._evaluate_receipt(
        "<memory>",
        _receipt(),
        table,
        declaration,
        pool_time,
        PRIOR_ARMS,
        pool_time_source=pool_time_source,
    )


def test_pool_time_from_file_mtime_is_marked_low_confidence():
    """The revision record earns HIGH; an mtime proxy only ever earns LOW."""
    checker = _checker()

    with tempfile.TemporaryDirectory() as scratch:
        path = os.path.join(scratch, "hermes-codex-lane.json")
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("{}")

        # No revision record anywhere: the file's mtime is the only time left.
        mtime_epoch = datetime(2026, 10, 20, tzinfo=timezone.utc).timestamp()
        os.utime(path, (mtime_epoch, mtime_epoch))
        no_record = {"lane": "EXECUTE", "revision": "rev-2", "history": []}
        pool_time, pool_time_source = checker.resolve_pool_time(no_record, path)
        assert pool_time_source == checker.POOL_TIME_FILE_MTIME

        low = _evaluate(checker, no_record, pool_time, pool_time_source)

        # A matching revision record supplies the time even though the file is old.
        os.utime(path, (0, 0))
        with_record = {
            "lane": "EXECUTE",
            "revision": "rev-2",
            "history": [{"revision": "rev-2", "at_utc": POOL_TIME}],
        }
        pool_time, pool_time_source = checker.resolve_pool_time(with_record, path)
        assert pool_time_source == checker.POOL_TIME_REVISION_RECORD

        high = _evaluate(checker, with_record, pool_time, pool_time_source)

    assert low["verdict"] == checker.SUPERSEDED
    assert low["pool_time_source"] == "file_mtime"
    assert low["superseded_confidence"] == checker.CONFIDENCE_LOW == "LOW"

    assert high["verdict"] == checker.SUPERSEDED
    assert high["pool_time_source"] == "revision_record"
    assert high["superseded_confidence"] == checker.CONFIDENCE_HIGH == "HIGH"
