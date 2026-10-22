"""SBLM03 - Governed Routing."""

from __future__ import annotations

from typing import Mapping

from .dto import RouteDecision, SpecAtom
from .errors import SBLError

DEFAULT_POLICY: dict[str, str | None] = {
    "CLI_TOOL": "SBLM04_GOVERNED_BUILD_BRIDGE",
    "BROWN_PATCH": "SBLM04_GOVERNED_BUILD_BRIDGE",
    "SKILL": "GJ03_SKILL_AGENT_BRIDGE",
    "AGENT_OS": None,
    "AI_SYSTEM": None,
    "DOC_SET": "SBLM02_SPEC_COMPILER",
    "REPAIR_TASK": "SBLM06_BOUNDED_REPAIR",
    "EVAL_HARNESS": "SBLM05_ACCEPTANCE_HARNESS",
}


class GovernedRouting:
    """Maps a spec atom kind onto exactly one permitted build target."""

    def __init__(self, policy: Mapping[str, str | None] | None = None) -> None:
        self.policy: dict[str, str | None] = dict(
            DEFAULT_POLICY if policy is None else policy
        )

    def route(self, atom: SpecAtom, kind: str) -> RouteDecision:
        if kind not in self.policy:
            raise SBLError(
                "SBL_E_UNKNOWN_KIND",
                f"unknown requirement kind: {kind!r}",
                {"kind": kind, "atom_id": getattr(atom, "atom_id", None)},
            )
        target = self.policy[kind]
        if target is None:
            raise SBLError(
                "SBL_E_PROHIBITED_KIND",
                "PROHIBITED_IN_V0_1",
                {"kind": kind, "atom_id": getattr(atom, "atom_id", None)},
            )
        return RouteDecision(
            atom_id=getattr(atom, "atom_id", ""),
            target=target,
            permitted=True,
            reason=f"{kind}_ROUTED",
        )
