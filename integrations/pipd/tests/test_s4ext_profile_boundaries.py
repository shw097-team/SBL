"""S4EXT-R1 (TT-S4EXT-006 / O009): the profile trio's untested boundaries.

O009 of the external challenge recorded that ``src/pipd_ls_sp/profiles.py`` already had REAL
protection (LITE/STANDARD/ASSURED, ``axes=None`` default, typed refusal for a non-list, empty list,
non-string, unknown and duplicated axes, ``risk_assessment = NOT_ASSESSED`` without evidence) and
that those defences must NOT be re-recorded as missing work. What was missing was a focused
regression on the thresholds and on the hostile-input paths:

* the 3/4 axis boundary (LITE ``max_axes = 3``) and the 6/7 boundary (STANDARD ``max_axes = 6``);
* ``provider_off_required`` firing TOGETHER with axis complexity -- the escalation must stay
  conservative, and the LITE axis floor must not be relaxed to STANDARD's just because the
  provider-off override moved the effective profile;
* the caller's own list/tuple must not be mutated (the record must consume the normalised list);
* a non-string ``requested`` must be a TYPED refusal. It used to be a bare ``AttributeError`` from
  ``(requested or "").upper()`` whenever a truthy non-string reached the function;
* an unknown risk must never be downgraded, and ``risk_evidence`` must never mint an approval.

Deterministic; runnable standalone.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, profiles  # noqa: E402
from pipd_ls_sp.errors import ProfileVeto, UnsupportedSurface  # noqa: E402

SCHEMAS_DIR = ROOT / "schemas"
THREE = ["intent", "verification", "release"]
FOUR = ["intent", "verification", "release", "trust_boundary"]
SIX = ["intent", "verification", "release", "trust_boundary", "host_surface", "knowledge"]
SEVEN = SIX + ["tech_candidates"]


class AxisThresholdTests(unittest.TestCase):
    """The exact thresholds the report called untested."""

    def test_lite_accepts_three_axes_unchanged(self) -> None:
        full = profiles.compute_profile("LITE", axes=list(THREE))
        self.assertEqual(full["profile"], "LITE")
        self.assertFalse(full["escalated"])
        self.assertIsNone(full["escalation_reason"])

    def test_lite_escalates_to_assured_at_four_axes(self) -> None:
        full = profiles.compute_profile("LITE", axes=list(FOUR))
        self.assertEqual(full["profile"], "ASSURED")
        self.assertTrue(full["escalated"])
        self.assertEqual(full["escalation_reason"], "axis_complexity")

    def test_standard_accepts_six_axes_unchanged(self) -> None:
        full = profiles.compute_profile("STANDARD", axes=list(SIX))
        self.assertEqual(full["profile"], "STANDARD")
        self.assertFalse(full["escalated"])

    def test_standard_escalates_to_assured_at_seven_axes(self) -> None:
        full = profiles.compute_profile("STANDARD", axes=list(SEVEN))
        self.assertEqual(full["profile"], "ASSURED")
        self.assertEqual(full["escalation_reason"], "axis_complexity")

    def test_assured_at_ten_axes_is_a_no_op(self) -> None:
        axes = ["intent", "knowledge", "verification", "release", "trust_boundary",
                "preexisting_repo", "profile", "tech_candidates", "host_surface"]
        full = profiles.compute_profile("ASSURED", axes=axes)   # 9 axes, ASSURED max is 10
        self.assertEqual(full["profile"], "ASSURED")

    def test_escalation_only_ever_raises_the_depth_floor(self) -> None:
        depth = {"LITE": 0, "STANDARD": 1, "ASSURED": 2}
        for requested in ("LITE", "STANDARD", "ASSURED"):
            for axes in (["intent"], THREE, FOUR, SEVEN):
                full = profiles.compute_profile(requested, axes=axes)
                self.assertGreaterEqual(depth[full["profile"]], depth[requested],
                                        f"{requested} with {len(axes)} axes went DOWN")


class ProviderOffInteractionTests(unittest.TestCase):
    """provider-off and axis complexity can fire together; the result must stay conservative."""

    def test_provider_off_alone_escalates_lite_to_standard(self) -> None:
        full = profiles.compute_profile("LITE", axes=list(THREE), provider_off_required=True)
        self.assertEqual(full["profile"], "STANDARD")
        self.assertEqual(full["escalation_reason"], "provider_off_parity")

    def test_provider_off_plus_axis_complexity_escalates_to_assured(self) -> None:
        full = profiles.compute_profile("LITE", axes=list(FOUR), provider_off_required=True)
        self.assertEqual(full["profile"], "ASSURED",
                         "the more severe of the two triggers must win")
        self.assertEqual(full["escalation_reason"], "axis_complexity")

    def test_the_lite_axis_floor_is_not_relaxed_by_the_override(self) -> None:
        """A provider-off override does NOT license STANDARD's 6-axis ceiling for a LITE request.

        Four axes still escalate: the threshold is evaluated against the REQUESTED profile, which is
        the stricter reading. Relaxing it as a side effect of the override would be a silent
        downgrade of exactly the safety floor the escalation exists to hold.
        """
        with_override = profiles.compute_profile("LITE", axes=list(FOUR), provider_off_required=True)
        without = profiles.compute_profile("LITE", axes=list(FOUR))
        self.assertEqual(with_override["profile"], without["profile"])

    def test_provider_off_on_standard_and_assured_is_a_no_op(self) -> None:
        for name in ("STANDARD", "ASSURED"):
            full = profiles.compute_profile(name, axes=list(THREE), provider_off_required=True)
            self.assertEqual(full["profile"], name)
            self.assertFalse(full["escalated"])


class InputImmutabilityTests(unittest.TestCase):
    """The caller's list/tuple is never mutated, and both containers are accepted."""

    def test_list_input_is_not_mutated(self) -> None:
        supplied = ["verification", "intent", "knowledge"]
        snapshot = list(supplied)
        full = profiles.compute_profile("LITE", axes=supplied)
        self.assertEqual(supplied, snapshot, "compute_profile mutated the caller's list")
        self.assertEqual(full["axes"], ["intent", "knowledge", "verification"])

    def test_tuple_is_accepted_and_returns_a_list(self) -> None:
        full = profiles.compute_profile("LITE", axes=("intent", "knowledge"))  # type: ignore[arg-type]
        self.assertEqual(full["axes"], ["intent", "knowledge"])
        self.assertIsInstance(full["axes"], list)

    def test_record_consumes_exactly_the_normalised_list(self) -> None:
        rec, full = pipeline.profile_record("LITE", ["verification", "intent", "knowledge"])
        self.assertEqual(rec["axes"], full["axes"])
        self.assertEqual(rec["axes"], sorted(set(rec["axes"])))

    def test_axes_none_defaults_to_one_axis(self) -> None:
        full = profiles.compute_profile("LITE", axes=None)
        self.assertEqual(full["axes"], ["intent"])
        self.assertEqual(full["profile"], "LITE")


class TypedRefusalTests(unittest.TestCase):
    """A malformed request is always a typed refusal, never a native exception."""

    def test_non_string_requested_is_a_typed_profile_veto(self) -> None:
        for bad in (7, 3.5, ["LITE"], {"profile": "LITE"}, True):
            with self.assertRaises(ProfileVeto, msg=f"{bad!r} must be typed-refused"):
                profiles.compute_profile(bad)  # type: ignore[arg-type]

    def test_non_string_requested_does_not_raise_attribute_error(self) -> None:
        try:
            profiles.compute_profile(12345)  # type: ignore[arg-type]
        except ProfileVeto:
            pass
        except AttributeError as exc:  # the pre-repair failure mode
            self.fail(f"a truthy non-string request leaked a native AttributeError: {exc}")

    def test_none_and_empty_string_are_still_unknown_profile(self) -> None:
        for bad in (None, "", "   "):
            with self.assertRaises(ProfileVeto):
                profiles.compute_profile(bad)  # type: ignore[arg-type]

    def test_unknown_profile_name_is_refused_case_insensitively(self) -> None:
        self.assertEqual(profiles.compute_profile("lite")["profile"], "LITE",
                         "a lower-case request resolves to the canonical name")
        for bad in ("lite2", "PRODUCTION", "assured ", " ASSURED"):
            with self.assertRaises(ProfileVeto, msg=f"{bad!r} must be refused"):
                profiles.compute_profile(bad)

    def test_unknown_axis_stays_unsupported_surface(self) -> None:
        with self.assertRaises(UnsupportedSurface):
            profiles.compute_profile("LITE", axes=["intent", "not_an_axis"])

    def test_duplicate_axis_is_refused(self) -> None:
        with self.assertRaises(ProfileVeto):
            profiles.compute_profile("LITE", axes=["intent", "intent"])

    def test_non_string_axis_is_refused(self) -> None:
        with self.assertRaises(ProfileVeto):
            profiles.compute_profile("LITE", axes=["intent", 3])  # type: ignore[list-item]

    def test_non_list_axes_is_refused(self) -> None:
        for bad in ("intent", 3, {"intent": True}):
            with self.assertRaises(ProfileVeto):
                profiles.compute_profile("LITE", axes=bad)  # type: ignore[arg-type]

    def test_empty_axes_is_refused(self) -> None:
        with self.assertRaises(ProfileVeto):
            profiles.compute_profile("LITE", axes=[])

    def test_enum_values_cannot_be_downgraded(self) -> None:
        """No input path may return a profile outside the declared trio."""
        for axes in (["intent"], THREE, FOUR, SEVEN):
            for requested in ("LITE", "STANDARD", "ASSURED"):
                self.assertIn(profiles.compute_profile(requested, axes=axes)["profile"],
                              ("LITE", "STANDARD", "ASSURED"))


class RiskHonestyTests(unittest.TestCase):
    """Unknown risk is NOT_ASSESSED; evidence never mints an approval or a lowering."""

    def test_absent_evidence_states_not_assessed(self) -> None:
        full = profiles.compute_profile("LITE", axes=["intent"])
        self.assertEqual(full["risk_assessment"], "NOT_ASSESSED")

    def test_supplied_evidence_is_unverified_not_verified(self) -> None:
        full = profiles.compute_profile("LITE", axes=["intent"],
                                        risk_evidence={"score": 0.01, "source": "maker"})
        self.assertEqual(full["risk_assessment"], "EVIDENCE_SUPPLIED_UNVERIFIED")
        self.assertNotIn("LOW_RISK_VERIFIED", json.dumps(full))

    def test_risk_evidence_cannot_lower_the_depth_floor(self) -> None:
        with_evidence = profiles.compute_profile("LITE", axes=list(FOUR),
                                                 risk_evidence={"score": 0.0})
        without = profiles.compute_profile("LITE", axes=list(FOUR))
        self.assertEqual(with_evidence["profile"], without["profile"])
        self.assertNotIn("LOW_RISK", json.dumps(with_evidence["profile"]))

    def test_profile_result_carries_no_approval_or_acceptance_field(self) -> None:
        full = profiles.compute_profile("LITE", axes=["intent"],
                                        risk_evidence={"score": 0.0})
        for forbidden in ("approved", "approval", "accepted", "verdict", "pass",
                          "claim_ceiling", "independent_pass"):
            self.assertNotIn(forbidden, {k.lower() for k in full},
                             f"a profile computation must never mint '{forbidden}'")

    def test_the_record_contract_is_not_widened(self) -> None:
        rec, full = pipeline.profile_record("LITE", ["intent"])
        self.assertNotIn("risk_assessment", rec,
                         "the honest marker must stay in the sidecar, not the record")
        self.assertIn("risk_assessment", full)
        schema = json.loads((SCHEMAS_DIR / "ProfileBinding.schema.json").read_text(encoding="utf-8"))
        self.assertNotIn("risk_assessment", schema["properties"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
