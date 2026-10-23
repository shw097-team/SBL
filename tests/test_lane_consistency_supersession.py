"""classify_arm() must judge a served arm against the pool that was in force, and no further.

The checker treats a re-bind as history, not as an amnesty: a receipt that serves an
arm absent from today's pool is SUPERSEDED only when the receipt is strictly older
than the pool revision. The four cases below pin that boundary, including the one
that matters most -- a missing timestamp must never buy the excuse.

The checker is imported from its exact path, unmodified: these tests observe the
predicate, they do not re-describe it.
"""
from __future__ import annotations

import importlib.util
import json

CHECKER = (
    r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
    r"/tools/check_lane_consistency.py"
)
RETIRED_ARMS = (
    r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
    r"/RETIRED_ARMS_R153.json"
)


def _classify_arm():
    """Load classify_arm from the checker by exact path; nothing is monkeypatched."""
    spec = importlib.util.spec_from_file_location("check_lane_consistency", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.classify_arm


# The pool in force today, in both label forms the checker itself passes in.
POOL = [
    "gpt-6.1-sol",
    "openai-codex/gpt-6.1-sol",
    "minimax-m3.1-flash-free",
    "opencode-go/minimax-m3.1-flash-free",
]

BEFORE_POOL = "2026-10-01T00:00:00+00:00"
AT_POOL = "2026-10-20T00:00:00+00:00"
AFTER_POOL = "2026-10-21T00:00:00+00:00"


def test_an_arm_in_the_pool_is_consistent_whatever_the_times_say():
    """Presence in the pool decides the verdict; the timestamps are irrelevant."""
    classify_arm = _classify_arm()
    for receipt_time in (BEFORE_POOL, AT_POOL, AFTER_POOL, None):
        assert classify_arm("openai-codex/gpt-6.1-sol", POOL, receipt_time, AT_POOL) == (
            "CONSISTENT"
        ), f"an arm the pool still serves must be CONSISTENT at receipt_time={receipt_time!r}"


def test_an_arm_absent_from_the_pool_and_older_than_it_is_superseded():
    """A genuinely retired arm, served before the rebind, is history, not a fault.

    The never-declared case -- an arm no revision ever authorised -- now belongs to
    test_lane_consistency_retired_arms.py, where it is a VIOLATION.
    """
    classify_arm = _classify_arm()

    with open(RETIRED_ARMS, encoding="utf-8") as handle:
        retired = [entry["arm"] for entry in json.load(handle)["arms"]]
    assert retired, "RETIRED_ARMS_R153.json must name at least one retired arm"
    arm = retired[0]

    # The shared POOL above predates the rebind and still lists this arm. What the
    # pool serves now is what remains once the retired arm is removed -- in both
    # label forms, so the bare model cannot slip back in as "live".
    retired_labels = {arm, arm.split("/", 1)[-1]}
    pool_now = [label for label in POOL if label not in retired_labels]
    assert arm not in pool_now, f"{arm!r} is still in the pool this test passes in"

    assert classify_arm(arm, pool_now, BEFORE_POOL, AT_POOL, retired) == "SUPERSEDED"
    # A minute earlier still counts, so this really is the strict "<" boundary.
    assert classify_arm(arm, pool_now, "2026-10-19T23:59:59+00:00", AT_POOL,
                        retired) == "SUPERSEDED"
    # At or after the rebind the same retired arm is no longer history.
    assert classify_arm(arm, pool_now, AT_POOL, AT_POOL, retired) == "VIOLATION"
    assert classify_arm(arm, pool_now, AFTER_POOL, AT_POOL, retired) == "VIOLATION"


def test_an_arm_absent_from_the_pool_and_dated_at_or_after_it_is_a_violation():
    """The rebind only excuses turns taken before it."""
    classify_arm = _classify_arm()
    assert classify_arm("anthropic/claude-opus-legacy", POOL, AFTER_POOL, AT_POOL) == (
        "VIOLATION"
    )
    # Same instant is not "before", so it must not be excused either.
    assert classify_arm("anthropic/claude-opus-legacy", POOL, AT_POOL, AT_POOL) == (
        "VIOLATION"
    )


def test_an_unknown_receipt_time_is_a_violation_never_superseded():
    """A missing timestamp cannot prove the receipt came first."""
    classify_arm = _classify_arm()
    for unknown in (None, "", "   ", "not-a-timestamp", "2026-13-45T99:99:99Z"):
        verdict = classify_arm("anthropic/claude-opus-legacy", POOL, unknown, AT_POOL)
        assert verdict == "VIOLATION", (
            f"receipt_time={unknown!r} must be VIOLATION, got {verdict!r}: "
            "an unknown time never proves the receipt predates the pool"
        )
        assert verdict != "SUPERSEDED"
