"""SBLM03 - Governed Routing."""

from __future__ import annotations

from typing import Mapping

from .dto import RouteDecision, SpecAtom
from .errors import SBLError

SUPPORTED = "SUPPORTED"
DEFERRED = "DEFERRED"
UNSUPPORTED = "UNSUPPORTED"

# DOC-01 names eight ProductKinds. This tuple is the denominator: what the product claims to
# recognise, not what it can execute. Execution is decided per kind by DEFAULT_DISPOSITIONS.
CANONICAL_KINDS: tuple[str, ...] = (
    "CLI_TOOL",
    "AGENT_SKILL",
    "SIMPLE_AGENT",
    "PLUGIN",
    "PROFILE",
    "AGENT_OS",
    "AI_SYSTEM",
    "GENIE/GENIE.md",
)

# One permitted target per kind, or None for a kind with no permitted target in v0.1.
#
# The canonical kind is spelled AGENT_SKILL, which is the name DOC-01 and WO-R14-TS15-KINDS use.
# The older spelling "SKILL" is the same kind and is kept as a deprecated alias, because callers and
# the C01/C17 contract route SKILL: the canonical rename is additive, so the alias is restored and
# not removed.
DEFAULT_POLICY: dict[str, str | None] = {
    "CLI_TOOL": "SBLM04_GOVERNED_BUILD_BRIDGE",
    "AGENT_SKILL": "GJ03_SKILL_AGENT_BRIDGE",
    # DEPRECATED alias: "SKILL" is the pre-rename spelling kept for callers and the C01/C17 contract;
    # it resolves to the same target as AGENT_SKILL and is outside CANONICAL_KINDS, so the eight-kind
    # denominator does not move.
    "SKILL": "GJ03_SKILL_AGENT_BRIDGE",
    "SIMPLE_AGENT": None,
    "PLUGIN": None,
    "PROFILE": None,
    "AGENT_OS": None,
    "AI_SYSTEM": None,
    "GENIE/GENIE.md": None,
    # BROWN_PATCH is not a DOC-01 ProductKind. It is the existing-repo patch route GJ02 uses; it is
    # kept so that journey keeps working, and it stays outside CANONICAL_KINDS so it is never counted
    # as one of the eight.
    "BROWN_PATCH": "SBLM04_GOVERNED_BUILD_BRIDGE",
}

# A recognition entry is not a success claim. SUPPORTED means the kind has a runnable lifecycle in
# this tree today. DEFERRED and UNSUPPORTED are refused by name, so a caller receives a typed
# refusal instead of a route it cannot use.
DEFAULT_DISPOSITIONS: dict[str, str] = {
    "CLI_TOOL": SUPPORTED,
    "AGENT_SKILL": SUPPORTED,
    # The alias inherits AGENT_SKILL's disposition; without this the deprecation would be a refusal.
    "SKILL": SUPPORTED,
    "SIMPLE_AGENT": DEFERRED,
    "PLUGIN": DEFERRED,
    "PROFILE": DEFERRED,
    "AGENT_OS": UNSUPPORTED,
    "AI_SYSTEM": UNSUPPORTED,
    "GENIE/GENIE.md": UNSUPPORTED,
    "BROWN_PATCH": SUPPORTED,
}

DISPOSITION_REASONS: dict[str, str] = {
    "CLI_TOOL": (
        "routes to the governed build bridge; build order, writeset and apply are implemented and tested"
    ),
    "AGENT_SKILL": (
        "routes to the GJ03 skill-agent bridge; discover, load, invoke and unload exist in sbl_sp/bridge.py"
    ),
    "SIMPLE_AGENT": (
        "no permitted target in v0.1; the bounded single-agent lifecycle (stop, credential revoke, "
        "provider-off) is not implemented"
    ),
    "PLUGIN": (
        "DOC-01 DEFERRED_UNVERIFIED / ADMISSION_HOLD; needs publisher, version, licence, permissions "
        "and a host readback before a target may exist"
    ),
    "PROFILE": (
        "DOC-01 DEFERRED_UNVERIFIED; a profile that does not change real host behaviour is not a "
        "product kind, and no host binding exists"
    ),
    "AGENT_OS": "DOC-01 UNSUPPORTED_V0_1 / NO_FIT; v0.1 ships no secondary control plane",
    "AI_SYSTEM": "DOC-01 UNSUPPORTED_V0_1 / NO_FIT; v0.1 produces bounded artefacts, not systems",
    "GENIE/GENIE.md": (
        "DOC-01 SWOF_RESERVED_COMPATIBILITY_ONLY; native read references only, no SBL generation right"
    ),
    "BROWN_PATCH": (
        "not a canonical ProductKind; the existing-repo patch route is kept for GJ02 and excluded "
        "from the eight-kind denominator"
    ),
}

# Where the disposition for each canonical kind is enforced, and where a SUPPORTED kind's lifecycle
# actually lives. Symbol references rather than line numbers, because line numbers rot.
CODE_REFS: dict[str, str] = {
    "CLI_TOOL": "sbl_core/m03_routing.py:DEFAULT_DISPOSITIONS['CLI_TOOL'] + sbl_core/m04_bridge.py:GovernedBuildBridge",
    "AGENT_SKILL": "sbl_core/m03_routing.py:DEFAULT_DISPOSITIONS['AGENT_SKILL'] + sbl_sp/bridge.py:SkillBridge",
    "SIMPLE_AGENT": "sbl_core/m03_routing.py:DEFAULT_DISPOSITIONS['SIMPLE_AGENT']",
    "PLUGIN": "sbl_core/m03_routing.py:DEFAULT_DISPOSITIONS['PLUGIN']",
    "PROFILE": "sbl_core/m03_routing.py:DEFAULT_DISPOSITIONS['PROFILE']",
    "AGENT_OS": "sbl_core/m03_routing.py:DEFAULT_DISPOSITIONS['AGENT_OS']",
    "AI_SYSTEM": "sbl_core/m03_routing.py:DEFAULT_DISPOSITIONS['AI_SYSTEM']",
    "GENIE/GENIE.md": "sbl_core/m03_routing.py:DEFAULT_DISPOSITIONS['GENIE/GENIE.md']",
}


class GovernedRouting:
    """Maps a spec atom kind onto exactly one permitted build target."""

    def __init__(
        self,
        policy: Mapping[str, str | None] | None = None,
        dispositions: Mapping[str, str] | None = None,
    ) -> None:
        self.policy: dict[str, str | None] = dict(
            DEFAULT_POLICY if policy is None else policy
        )
        self.dispositions: dict[str, str] = dict(
            DEFAULT_DISPOSITIONS if dispositions is None else dispositions
        )

    def disposition(self, kind: str) -> str:
        """Returns the declared state of a kind, defaulting to UNSUPPORTED for anything undeclared."""

        return self.dispositions.get(kind, UNSUPPORTED)

    def kind_matrix(self) -> list[dict[str, str]]:
        """Returns one machine-readable row per canonical kind, in DOC-01 order."""

        return [
            {
                "kind": kind,
                "disposition": self.disposition(kind),
                "reason": DISPOSITION_REASONS.get(kind, ""),
                "code_ref": CODE_REFS.get(kind, ""),
            }
            for kind in CANONICAL_KINDS
        ]

    def route(self, atom: SpecAtom, kind: str) -> RouteDecision:
        if kind not in self.policy:
            raise SBLError(
                "SBL_E_UNKNOWN_KIND",
                f"unknown requirement kind: {kind!r}",
                {"kind": kind, "atom_id": getattr(atom, "atom_id", None)},
            )
        disposition = self.disposition(kind)
        detail = {
            "kind": kind,
            "atom_id": getattr(atom, "atom_id", None),
            "disposition": disposition,
            "reason": DISPOSITION_REASONS.get(kind, ""),
        }
        # Refuse before touching the target: a deferred or unsupported kind must not produce a
        # decision at all, so there is nothing a caller can mistake for permission.
        if disposition == DEFERRED:
            raise SBLError(
                "SBL_E_DEFERRED_KIND",
                f"kind is recognised but deferred in v0.1, so it cannot be dispatched: {kind!r}",
                detail,
            )
        if disposition != SUPPORTED:
            raise SBLError("SBL_E_PROHIBITED_KIND", "PROHIBITED_IN_V0_1", detail)
        target = self.policy[kind]
        if target is None:
            raise SBLError("SBL_E_PROHIBITED_KIND", "PROHIBITED_IN_V0_1", detail)
        return RouteDecision(
            atom_id=getattr(atom, "atom_id", ""),
            target=target,
            permitted=True,
            reason=f"{kind}_ROUTED",
        )
