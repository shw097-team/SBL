"""SharedCore composition root."""

from __future__ import annotations

import os

from .m01_intake import GoalIntake
from .m02_spec import GuidedSpecification
from .m03_routing import GovernedRouting
from .m04_bridge import GovernedBuildBridge
from .m05_verify import EvidenceVerification
from .m06_repair import BoundedRepair

DOC_SCHEMA = "SBL-CORE-DOCTOR/1"
MODULES: tuple[str, ...] = (
    "SBLM01",
    "SBLM02",
    "SBLM03",
    "SBLM04",
    "SBLM05",
    "SBLM06",
)


class SharedCore:
    """Composes M01..M06 over one repository root."""

    def __init__(self, root: str) -> None:
        self.root = os.path.abspath(root)
        self.intake = GoalIntake()
        self.spec = GuidedSpecification()
        self.routing = GovernedRouting()
        self.bridge = GovernedBuildBridge()
        self.verify = EvidenceVerification()
        self.repair = BoundedRepair()

    def doctor(self) -> dict:
        return {
            "schema": DOC_SCHEMA,
            "modules": list(MODULES),
            "ok": True,
            "root": self.root,
        }
