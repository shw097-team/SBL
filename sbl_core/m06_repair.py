"""SBLM06 - Bounded Repair."""

from __future__ import annotations

from hashlib import sha256
from typing import Iterable

from .dto import RepairPlan
from .errors import SBLError


def _plan_id(first_fail: str, scope: str, attempts: int) -> str:
    digest = sha256(f"{first_fail}|{scope}|{attempts}".encode("utf-8")).hexdigest()
    return "R-" + digest[:12]


class BoundedRepair:
    """Plans narrow repairs and hard-stops once the attempt cap is reached."""

    def plan(
        self,
        first_fail: str,
        evidence_refs: list[str],
        attempts: int = 0,
        max_attempts: int = 3,
    ) -> RepairPlan:
        if not isinstance(evidence_refs, (list, tuple)) or len(evidence_refs) == 0:
            raise SBLError(
                "SBL_E_REPAIR_WITHOUT_EVIDENCE",
                "repair requires at least one evidence reference",
                {"first_fail": first_fail},
            )
        if not any(str(ref).strip() for ref in evidence_refs):
            raise SBLError(
                "SBL_E_REPAIR_WITHOUT_EVIDENCE",
                "repair evidence references are blank",
                {"first_fail": first_fail},
            )
        rollback_pointer = str(evidence_refs[0])
        scope = "NARROW" if str(first_fail).strip() else "UNKNOWN"
        exhausted = int(attempts) >= int(max_attempts)
        return RepairPlan(
            plan_id=_plan_id(str(first_fail), scope, int(attempts)),
            first_fail=str(first_fail),
            scope=scope,
            max_attempts=int(max_attempts),
            rollback_pointer=rollback_pointer,
            action="STOP_ESCALATE" if exhausted else "NARROW_REPAIR",
        )
