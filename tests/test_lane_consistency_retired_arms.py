"""Supersession must not excuse an arm that no revision ever declared.

`classify_arm()` used to return SUPERSEDED for ANY arm absent from the current pool
whenever the receipt predated it. A hijacked model, a typo, or a hand-edited receipt
therefore read as "history" instead of "never authorized". The narrowing adds a
third fact -- the arm must appear in the retired-arm list a PRIOR revision really
declared -- so only a genuinely retired arm can be excused.

The four cases below pin the boundary: pool membership, retired-and-older,
absent-from-both (the hole), and retired-but-undated.

The checker is imported from its exact path, unmodified: these tests observe the
predicate, they do not re-describe it.
"""
from __future__ import annotations

import importlib.util

CHECKER = (
    r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2"
    r"/tools/check_lane_consistency.py"
)

# Label arms as bare models and as `provider/model`: the checker passes both forms,
# so an alias cannot masquerade as a rebind.
POOL = [
    "gpt-6.1-sol",
    "openai-codex/gpt-6.1-sol",
    "deepseek-v4.1-flash",
    "opencode-go/deepseek-v4.1-flash",
]

PRIOR = [
    "minimax-m3.1-flash-free",
    "opencode-go/minimax-m3.1-flash-free",
]

BEFORE_POOL = "2026-10-01T00:00:00+00:00"
AT_POOL = "2026-10-20T00:00:00+00:00"


def _checker_module():
    """Load the checker by exact path; nothing is monkeypatched."""
    spec = importlib.util.spec_from_file_location("check_lane_consistency", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_an_arm_in_the_current_pool_is_consistent():
    """Membership in today's pool decides it; the retired list is irrelevant."""
    classify_arm = _checker_module().classify_arm
    assert classify_arm(
        "openai-codex/gpt-6.1-sol", POOL, BEFORE_POOL, AT_POOL, PRIOR
    ) == "CONSISTENT"
    # A live arm stays CONSISTENT even with no prior list at all.
    assert classify_arm("deepseek-v4.1-flash", POOL, BEFORE_POOL, AT_POOL) == "CONSISTENT"


def test_an_arm_in_prior_arms_with_an_older_receipt_is_superseded():
    """A genuinely retired arm, served before the rebind, is history - once its provider is stated.

    B13/B14: the pair (model, provider) is what the retired list declares, so a receipt that names the model and no
    provider anywhere has not said enough to be acquitted. It is refused as ARM_IDENTITY_UNVERIFIABLE; the same
    receipt with the provider stated is SUPERSEDED.
    """
    module = _checker_module()
    classify_arm = module.classify_arm
    assert classify_arm(
        "opencode-go/minimax-m3.1-flash-free", POOL, BEFORE_POOL, AT_POOL, PRIOR
    ) == "SUPERSEDED"
    # The bare-model form must match too, when the provider is carried separately.
    assert classify_arm(
        "minimax-m3.1-flash-free", POOL, BEFORE_POOL, AT_POOL, PRIOR, served_provider="opencode-go"
    ) == "SUPERSEDED"
    verdict, reason = module.classify_arm_with_reason(
        "minimax-m3.1-flash-free", POOL, BEFORE_POOL, AT_POOL, PRIOR
    )
    assert (verdict, reason) == (module.VIOLATION, module.REASON_ARM_IDENTITY_UNVERIFIABLE)


def test_an_arm_in_neither_list_is_a_violation_named_unauthorized_arm():
    """The hole: an arm no revision declared is never 'superseded', however old."""
    module = _checker_module()
    for served in (
        "anthropic/claude-opus-legacy",
        "openai-codex/gpt-6.1-sol-shadow",  # typos and near-misses must not match
        "evil-provider/hijacked-model",
    ):
        verdict, reason = module.classify_arm_with_reason(
            served, POOL, BEFORE_POOL, AT_POOL, PRIOR
        )
        assert verdict == "VIOLATION", f"{served!r} must not be SUPERSEDED"
        assert reason == module.UNAUTHORIZED_ARM, (
            f"{served!r} carries reason {reason!r}, expected UNAUTHORIZED_ARM"
        )
        # No prior list at all: still a violation, never an excuse.
        assert module.classify_arm(served, POOL, BEFORE_POOL, AT_POOL) == "VIOLATION"


def test_an_arm_in_prior_arms_but_with_an_unknown_time_is_a_violation():
    """A retired arm still needs proof it came first; a missing stamp is not proof."""
    module = _checker_module()
    for unknown in (None, "", "   ", "not-a-timestamp", "2026-13-45T99:99:99Z"):
        verdict = module.classify_arm(
            "opencode-go/minimax-m3.1-flash-free", POOL, unknown, AT_POOL, PRIOR
        )
        assert verdict == "VIOLATION", (
            f"receipt_time={unknown!r} must be VIOLATION, got {verdict!r}"
        )
        assert verdict != "SUPERSEDED"
