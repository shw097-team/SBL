"""Frozen data-transfer objects for the SBL shared core."""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Iterable


def _hex12(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()[:12]


def goal_id_for(title: str) -> str:
    """Deterministic goal id: ``G-`` + sha256(stripped, lowercased title)[:12]."""

    return "G-" + _hex12(str(title).strip().lower())


def atom_id_for(text: str) -> str:
    """Deterministic atom id: ``A-`` + sha256(text)[:12]."""

    return "A-" + _hex12(str(text))


def order_id_for(head: str, writeset: Any) -> str:
    """Deterministic order id from HEAD and the sorted writeset paths."""

    if isinstance(writeset, WriteSet):
        paths = writeset.paths
    elif isinstance(writeset, str):
        paths = (writeset,)
    else:
        paths = tuple(writeset or ())
    joined = ",".join(sorted(str(p) for p in paths))
    return "O-" + _hex12(f"{head}|{joined}")


def _plain(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _plain(getattr(value, field.name))
            for field in dataclasses.fields(value)
        }
    if isinstance(value, (list, tuple, set, frozenset)):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    return value


class _DTO:
    """Mixin adding a JSON-able ``to_dict`` to frozen dataclasses."""

    def to_dict(self) -> dict[str, Any]:
        return _plain(self)


@dataclass(frozen=True)
class Goal(_DTO):
    goal_id: str
    title: str
    description: str = ""
    requester: str = "local"


@dataclass(frozen=True)
class SpecAtom(_DTO):
    atom_id: str
    text: str
    locator: str


@dataclass(frozen=True)
class RouteDecision(_DTO):
    atom_id: str
    target: str
    permitted: bool
    reason: str


@dataclass(frozen=True)
class RepoContextDTO(_DTO):
    root: str
    head: str
    tracked_files: int
    dirty: bool


@dataclass(frozen=True)
class WriteSet(_DTO):
    paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        raw: Iterable[str] | str | None = self.paths
        if raw is None:
            normalized: tuple[str, ...] = ()
        elif isinstance(raw, str):
            normalized = (raw,)
        else:
            normalized = tuple(str(item) for item in raw)
        object.__setattr__(self, "paths", normalized)


@dataclass(frozen=True)
class BuildOrder(_DTO):
    order_id: str
    root: str
    head: str
    writeset: WriteSet


@dataclass(frozen=True)
class EvidenceItem(_DTO):
    gate_id: str
    command: str
    exit_code: int
    stdout_sha256: str
    denominator: int


@dataclass(frozen=True)
class Verdict(_DTO):
    gate_id: str
    maker: str
    checker: str
    status: str
    claim_level: str


@dataclass(frozen=True)
class RepairPlan(_DTO):
    plan_id: str
    first_fail: str
    scope: str
    max_attempts: int
    rollback_pointer: str
    action: str


@dataclass(frozen=True)
class ModeDecision(_DTO):
    mode: str
    effect: str
    allowed: bool
    no_effect: bool
    reason: str


@dataclass(frozen=True)
class TodoItem(_DTO):
    id: str
    title: str
    status: str
