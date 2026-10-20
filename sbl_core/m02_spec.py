"""SBLM02 - Guided Specification."""

from __future__ import annotations

from typing import Any, Mapping

from .dto import Goal, SpecAtom, atom_id_for
from .errors import SBLError


class GuidedSpecification:
    """Derives source-bound spec atoms from guided clauses."""

    def derive(self, goal: Goal, clauses: list[dict[str, Any]]) -> list[SpecAtom]:
        if not isinstance(clauses, (list, tuple)) or len(clauses) == 0:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "specification requires at least one clause",
                {"goal_id": getattr(goal, "goal_id", None)},
            )
        atoms: list[SpecAtom] = []
        seen: set[str] = set()
        for index, clause in enumerate(clauses):
            if not isinstance(clause, Mapping):
                raise SBLError(
                    "SBL_E_BAD_STATE",
                    "clause must be a mapping with text and locator",
                    {"index": index, "type": type(clause).__name__},
                )
            text = str(clause.get("text") or "").strip()
            locator = str(clause.get("locator") or "").strip()
            if not text:
                raise SBLError(
                    "SBL_E_BAD_STATE",
                    "clause text is empty",
                    {"index": index, "goal_id": getattr(goal, "goal_id", None)},
                )
            if not locator:
                raise SBLError(
                    "SBL_E_UNLOCATED_REQUIREMENT",
                    "clause has no source locator binding",
                    {"index": index, "text": text[:120]},
                )
            if text in seen:
                continue
            seen.add(text)
            atoms.append(
                SpecAtom(atom_id=atom_id_for(text), text=text, locator=locator)
            )
        return atoms
