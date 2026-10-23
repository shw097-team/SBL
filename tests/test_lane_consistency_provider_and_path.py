"""Two holes the independent checker opened on 2026-10-23, pinned so they cannot reopen.

Finding 1 (SUPERSESSION_LEAK, checker line ~864): a receipt naming the retired MODEL `minimax-m3.1-flash-free` with
provider AND usage_provider set to an invented provider was reported SUPERSEDED, because the retired list was expanded
to bare model labels and the historical branch only compared call against bill. A retired model does not authorise an
undeclared provider.

Finding 2 (MTIME_LABEL_ONLY, checker line ~475): with no revision timestamp, moving the declaration file's mtime turned
an older receipt from VIOLATION into SUPERSEDED, with only a LOW-confidence label attached. A label is not a control.

Finding 3 (TAUTOLOGICAL_TEST): the previous time-source test handed `None` straight to the pure classifier, so it would
still pass if the evaluator-level mtime fallback came back. The second test here goes through `_evaluate_receipt`.
"""
from __future__ import annotations

import importlib.util
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[1] / "_governance" / "round-20261022-r15_2" / "tools" / "check_lane_consistency.py"


def _checker():
    spec = importlib.util.spec_from_file_location("checker_provider_and_path", CHECKER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_retired_model_does_not_authorise_an_undeclared_provider():
    checker = _checker()
    verdict, reason = checker.classify_arm_with_reason(
        "minimax-m3.1-flash-free",
        ["opencode-go/deepseek-v4.1-flash"],       # today's pool
        "2026-10-19T10:00:00+00:00",               # older than the pool
        "2026-10-20T00:00:00+00:00",
        ["minimax-m3.1-flash-free"],               # retired floor: the bare label the loader also emits
        None,
        served_provider="evil-provider",           # ... but the receipt names an invented provider
        prior_pairs={"minimax-m3.1-flash-free": {"opencode-go"}},
    )
    assert verdict == checker.VIOLATION
    assert reason == checker.REASON_PROVIDER_NOT_RETIRED


def test_the_retired_pair_still_earns_the_excuse():
    checker = _checker()
    assert checker.classify_arm(
        "minimax-m3.1-flash-free",
        ["opencode-go/deepseek-v4.1-flash"],
        "2026-10-19T10:00:00+00:00",
        "2026-10-20T00:00:00+00:00",
        ["minimax-m3.1-flash-free"],
        served_provider="opencode-go",
        prior_pairs={"minimax-m3.1-flash-free": {"opencode-go"}},
    ) == checker.SUPERSEDED


def test_evaluator_level_mtime_cannot_buy_supersession():
    """Goes through the evaluator, so restoring an mtime fallback inside it would fail this test."""
    checker = _checker()
    with tempfile.TemporaryDirectory() as scratch:
        decl_path = os.path.join(scratch, "lane-route-slots.candidate.json")
        with open(decl_path, "w", encoding="utf-8") as handle:
            handle.write("{}")
        moved = datetime(2026, 10, 25, tzinfo=timezone.utc).timestamp()
        os.utime(decl_path, (moved, moved))

        decl = {"lane": "EXECUTE", "revision": "rev-x", "history": []}
        pool_time, pool_time_source = checker.resolve_pool_time(decl, decl_path)
        assert pool_time_source == checker.POOL_TIME_FILE_MTIME

        receipt = {
            "lane": "EXECUTE",
            "generated_utc": "2026-10-15T00:00:00Z",   # older than the touched file
            "attempts": [{"rank": 1, "provider": "opencode-go", "model": "minimax-m3.1-flash-free",
                          "usage_provider": "opencode-go", "exit": 0, "nonce_present": True,
                          "usage_status": 200}],
        }
        table = {"EXECUTE": {1: {"provider": "opencode-go", "model": "deepseek-v4.1-flash"}}}
        out = checker._evaluate_receipt(
            os.path.join(scratch, "receipt.json"), receipt, table, decl,
            pool_time=pool_time, prior_arms=["minimax-m3.1-flash-free", "opencode-go/minimax-m3.1-flash-free"],
            pool_time_source=pool_time_source,
        )
    blob = json.dumps(out, ensure_ascii=False)
    assert "SUPERSEDED" not in blob, "an mtime-derived pool time must not acquit anyone"
    assert "POOL_TIME_NOT_AUTHORITATIVE" in blob or "VIOLATION" in blob


def test_a_qualified_label_cannot_ride_a_retired_model_to_supersession():
    """B8, finding SUPERSESSION_LEAK still open at :647: a receipt naming the arm provider-qualified missed the
    bare-keyed pair map, so the provider was never checked. Both label forms must reach the same guard."""
    checker = _checker()
    for label in ("minimax-m3.1-flash-free", "opencode-go/minimax-m3.1-flash-free"):
        verdict, reason = checker.classify_arm_with_reason(
            label,
            ["opencode-go/deepseek-v4.1-flash"],
            "2026-10-19T10:00:00+00:00",
            "2026-10-20T00:00:00+00:00",
            ["minimax-m3.1-flash-free"],
            None,
            served_provider="evil-provider",
            prior_pairs={"minimax-m3.1-flash-free": {"opencode-go"}},
        )
        assert verdict == checker.VIOLATION, "label %r rode a retired model past the provider guard" % label
        # Which refusal fires depends on the label form, and both are refusals:
        #   bare model + provider=evil-provider          -> the provider never declared this model
        #   opencode-go/model + provider=evil-provider   -> the label and the provider field contradict each other
        expected = (checker.REASON_PROVIDER_NOT_RETIRED if "/" not in label
                    else checker.REASON_ARM_LABEL_PROVIDER_CONFLICT)
        assert reason == expected, "label %r refused for %r, expected %r" % (label, reason, expected)


def test_evaluator_never_uses_the_receipt_file_mtime_when_the_receipt_has_no_time():
    """B8, finding TAUTOLOGICAL_TEST still open: the earlier evaluator test supplied generated_utc, so it never
    exercised the missing-timestamp path. This receipt carries NO time field at all, and its file mtime is ancient."""
    checker = _checker()
    with tempfile.TemporaryDirectory() as scratch:
        decl_path = os.path.join(scratch, "lane-route-solts.json")
        with open(decl_path, "w", encoding="utf-8") as handle:
            handle.write("{}")
        decl = {"lane": "EXECUTE", "revision": "rev-x", "history": [{"revision": "rev-x", "at_utc": "2026-10-20T00:00:00Z"}]}
        pool_time, pool_time_source = checker.resolve_pool_time(decl, decl_path)

        receipt_path = os.path.join(scratch, "receipt.json")
        with open(receipt_path, "w", encoding="utf-8") as handle:
            handle.write("{}")
        old = datetime(2026, 10, 1, tzinfo=timezone.utc).timestamp()   # file mtime predates the pool: an "old" file
        os.utime(receipt_path, (old, old))

        receipt = {   # deliberately NO generated_utc / generated_at / at_utc
            "lane": "EXECUTE",
            "attempts": [{"rank": 1, "provider": "opencode-go", "model": "minimax-m3.1-flash-free",
                          "usage_provider": "opencode-go", "exit": 0, "nonce_present": True, "usage_status": 200}],
        }
        table = {"EXECUTE": {1: {"provider": "opencode-go", "model": "deepseek-v4.1-flash"}}}
        out = checker._evaluate_receipt(
            receipt_path, receipt, table, decl,
            pool_time=pool_time, prior_arms=["minimax-m3.1-flash-free"],
            pool_time_source=pool_time_source,
        )
    blob = json.dumps(out, ensure_ascii=False)
    assert "SUPERSEDED" not in blob, "an undated receipt bought an excuse from its file mtime"
    assert "UNKNOWN_RECEIPT_TIME" in blob


def test_a_label_prefix_that_contradicts_the_provider_field_is_refused():
    """B9: `evil-provider/minimax-...` with provider=opencode-go was reduced to the bare model and excused.

    The prefix is a provider statement. When the receipt carries both, they must agree; a disagreement is a forged
    identity, not an old arm.
    """
    checker = _checker()
    verdict, reason = checker.classify_arm_with_reason(
        "evil-provider/minimax-m3.1-flash-free",
        ["opencode-go/deepseek-v4.1-flash"],
        "2026-10-19T10:00:00+00:00",
        "2026-10-20T00:00:00+00:00",
        ["minimax-m3.1-flash-free"],
        None,
        served_provider="opencode-go",
        prior_pairs={"minimax-m3.1-flash-free": {"opencode-go"}},
    )
    assert verdict == checker.VIOLATION
    assert reason == checker.REASON_ARM_LABEL_PROVIDER_CONFLICT


def test_a_qualified_label_with_no_provider_field_still_checks_the_pair():
    """The label alone may state the provider - and then it must still be a provider that declared the arm."""
    checker = _checker()
    assert checker.classify_arm_with_reason(
        "evil-provider/minimax-m3.1-flash-free",
        ["opencode-go/deepseek-v4.1-flash"],
        "2026-10-19T10:00:00+00:00",
        "2026-10-20T00:00:00+00:00",
        ["minimax-m3.1-flash-free"],
        None,
        served_provider=None,
        prior_pairs={"minimax-m3.1-flash-free": {"opencode-go"}},
    ) == (checker.VIOLATION, checker.REASON_PROVIDER_NOT_RETIRED)


def test_an_unreadable_pair_map_denies_the_excuse_instead_of_skipping_the_guard(monkeypatch=None):
    """B10: `load_prior_pairs` returned {} on a read failure, so the provider guard was skipped - fail-open on missing
    evidence. The checked loader reports the problem and the evaluator turns it into a refusal."""
    import tempfile as _tf
    checker = _checker()
    missing = os.path.join(_tf.gettempdir(), "definitely-not-a-retired-arms-file.json")
    pairs, problem = checker.load_prior_pairs_checked(missing)
    assert pairs == {} and problem, "an unreadable list must report a problem, not look empty"
    ok_pairs, no_problem = checker.load_prior_pairs_checked()
    assert no_problem is None and ok_pairs, "the real list must load cleanly for the other tests to mean anything"


def test_secondary_identity_fields_must_agree_with_the_claim_not_with_each_other():
    """B11: transport_model and usage_model both saying NEVER-DECLARED-MODEL is self-consistent, and that self
    consistency was enough to excuse a retired arm. All identity-bearing fields must name the claimed arm."""
    checker = _checker()
    with tempfile.TemporaryDirectory() as scratch:
        decl_path = os.path.join(scratch, "decl.json")
        with open(decl_path, "w", encoding="utf-8") as handle:
            handle.write("{}")
        decl = {"lane": "EXECUTE", "revision": "rev-9", "history": [{"revision": "rev-9", "at_utc": "2026-10-20T00:00:00Z"}]}
        pool_time, pool_time_source = checker.resolve_pool_time(decl, decl_path)
        receipt = {
            "lane": "EXECUTE",
            "generated_utc": "2026-10-19T00:00:00Z",
            "attempts": [{
                "rank": 1,
                "provider": "opencode-go",
                "model": "minimax-m3.1-flash-free",          # the claim: a retired arm
                "transport_model": "NEVER-DECLARED-MODEL",   # both secondary fields agree with each other
                "usage_model": "NEVER-DECLARED-MODEL",       # ... and with nothing else
                "usage_provider": "opencode-go",
                "exit": 0, "nonce_present": True, "usage_status": 200,
            }],
        }
        table = {"EXECUTE": {1: {"provider": "opencode-go", "model": "deepseek-v4.1-flash"}}}
        out = checker._evaluate_receipt(
            os.path.join(scratch, "r.json"), receipt, table, decl,
            pool_time=pool_time, prior_arms=["minimax-m3.1-flash-free"],
            pool_time_source=pool_time_source,
        )
    blob = json.dumps(out, ensure_ascii=False)
    # The arm itself is legitimately retired, so a historical verdict is fine - what must not survive is a PASS.
    assert "NEVER-DECLARED-MODEL" in blob
    assert out.get("verdict") == checker.VIOLATION, (
        "a self-consistent pair of secondary fields must not pass the receipt")
    assert "claimed model" in blob, "the note must show the comparison that failed"


def test_the_provider_guard_is_on_by_default_not_only_when_a_caller_passes_evidence():
    """B12: omitting prior_pairs returned the weaker rule, so the PUBLIC classifier still excused an undeclared
    provider/model pair. The guard must load its own evidence, and refuse when it cannot."""
    checker = _checker()
    verdict, reason = checker.classify_arm_with_reason(
        "minimax-m3.1-flash-free",
        ["opencode-go/deepseek-v4.1-flash"],
        "2026-10-19T10:00:00+00:00",
        "2026-10-20T00:00:00+00:00",
        ["minimax-m3.1-flash-free"],
        None,
        served_provider="evil-provider",
        # prior_pairs deliberately omitted: the default must not be "no check"
    )
    assert verdict == checker.VIOLATION
    assert reason == checker.REASON_PROVIDER_NOT_RETIRED
