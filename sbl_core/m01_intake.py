"""SBLM01 - Goal Intake."""

from __future__ import annotations

from .dto import Goal, goal_id_for
from .errors import SBLError

MAX_TITLE_LENGTH = 200


class GoalIntake:
    """Turns a raw request into a deterministic, validated Goal."""

    def intake(
        self, title: str, description: str = "", requester: str = "local"
    ) -> Goal:
        if not isinstance(title, str):
            raise SBLError(
                "SBL_E_BAD_STATE",
                "goal title must be a string",
                {"type": type(title).__name__},
            )
        cleaned = title.strip()
        if not cleaned:
            raise SBLError(
                "SBL_E_EMPTY_TITLE",
                "goal title is empty after stripping",
                {"raw_length": len(title)},
            )
        if len(cleaned) > MAX_TITLE_LENGTH:
            raise SBLError(
                "SBL_E_BAD_STATE",
                f"goal title exceeds {MAX_TITLE_LENGTH} characters",
                {"length": len(cleaned), "max": MAX_TITLE_LENGTH},
            )
        return Goal(
            goal_id=goal_id_for(cleaned),
            title=cleaned,
            description=str(description),
            requester=str(requester),
        )
