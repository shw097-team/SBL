"""Profile trio: LITE / STANDARD / ASSURED over one canonical truth (總藍圖 §7.3 #04)."""
from __future__ import annotations

from .errors import ProfileVeto, UnsupportedSurface

# axes -> artifact depth floor, required assurance
PROFILES = {
    "LITE": {"artifact_depth": "L1_SCHEMA_CONTRACT", "assurance": ["deterministic_validator"],
             "target_resolution": "package", "max_axes": 3},
    "STANDARD": {"artifact_depth": "L3_INTEGRATION_RUNTIME",
                 "assurance": ["deterministic_validator", "negative_security"],
                 "target_resolution": "integration", "max_axes": 6},
    "ASSURED": {"artifact_depth": "L4_FAILURE_RECOVERY",
                "assurance": ["deterministic_validator", "negative_security", "adversarial",
                              "independent_checker"],
                "target_resolution": "runtime", "max_axes": 10},
}
AXES = ("intent", "knowledge", "verification", "release", "trust_boundary",
        "preexisting_repo", "profile", "tech_candidates", "host_surface")


def compute_profile(requested: str, *, axes: list[str] | None = None,
                    provider_off_required: bool = False,
                    risk_evidence: dict | None = None) -> dict:
    """Resolve the effective profile over ONE canonical axis list.

    Fail-closed axis handling (D2): a malformed axis set is a typed refusal BEFORE any
    escalation math runs, and the NORMALISED list this function returns is the exact list the
    caller must emit, so the escalation basis (the axis count) and the emitted record can
    never disagree. ``pipeline.profile_record`` consumes ``result["axes"]`` verbatim.

    Risk honesty (D3): there is no per-axis risk score here. ``risk_assessment`` is
    ``"NOT_ASSESSED"`` unless risk evidence is explicitly supplied, and the ladder value
    ``"LOW_RISK_VERIFIED"`` is never emitted - an axis count is not a risk score.
    """
    if requested is None or isinstance(requested, str):
        name = (requested or "").upper()
    else:
        # O009: `(requested or "").upper()` raised a bare AttributeError for a truthy non-string
        # (an int/object reached this function straight from a caller, not through argparse).
        # A malformed request is a TYPED refusal, never a native AttributeError.
        raise ProfileVeto(
            f"profile must be a string, got {type(requested).__name__} ({requested!r})")
    if name not in PROFILES:
        raise ProfileVeto(f"unknown profile {requested!r}")
    cfg = PROFILES[name]

    # ---- axis validation: fail closed, before any escalation math ----
    if axes is None:
        used = ["intent"]
    elif not isinstance(axes, (list, tuple)):
        raise ProfileVeto(
            f"axes must be a list of canonical axis names, got {type(axes).__name__}")
    else:
        used = list(axes)
    if not used:
        raise ProfileVeto("axes must be a non-empty list (an empty axis set binds no surface)")
    nonstr = [a for a in used if not isinstance(a, str)]
    if nonstr:
        raise ProfileVeto(f"axes must be strings; non-string entries {nonstr!r} refused")
    unknown = sorted({a for a in used if a not in AXES})
    if unknown:
        raise UnsupportedSurface(f"unknown axes {unknown}")
    dupes = sorted({a for a in used if used.count(a) > 1})
    if dupes:
        raise ProfileVeto(f"duplicated axis/axes refused (double-counted complexity): {dupes}")
    normalised = sorted(set(used))

    override = None
    # safety veto may ESCALATE depth, never reduce it
    if provider_off_required and name == "LITE":
        override = "STANDARD"
    if len(normalised) > cfg["max_axes"]:
        override = "ASSURED" if name != "ASSURED" else override
    effective = override or name

    # D3: state the absent risk assessment honestly. No evidence supplied -> NOT_ASSESSED.
    # Evidence supplied is recorded as UNVERIFIED, never rounded up to LOW_RISK_VERIFIED.
    risk_assessment = "NOT_ASSESSED" if not risk_evidence else "EVIDENCE_SUPPLIED_UNVERIFIED"
    return {"profile": effective,
            "requested_profile": name,
            "escalated": bool(override),
            "escalation_reason": "provider_off_parity" if override == "STANDARD" else
                                 ("axis_complexity" if override == "ASSURED" else None),
            "axes": normalised,
            "risk_assessment": risk_assessment,
            "vetoes": [],
            "artifact_depth": PROFILES[effective]["artifact_depth"],
            "assurance": PROFILES[effective]["assurance"],
            "canonical_truth": "single",  # all three profiles read one canonical truth
            }
