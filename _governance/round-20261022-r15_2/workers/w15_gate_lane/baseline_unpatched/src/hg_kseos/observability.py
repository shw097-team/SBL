from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .errors import InvariantViolation
from .util import canonical_json, sha256_text, utc_now


@dataclass(frozen=True)
class StructuredEvent:
    trace_id: str
    event_id: str
    entity_type: str
    entity_id: str
    state: str
    taxonomy: str
    payload: dict[str, Any]


class EventLog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: StructuredEvent) -> str:
        if not event.trace_id or not event.event_id or not event.taxonomy:
            raise InvariantViolation("ERR_OBSERVABILITY_REQUIRED_FIELD")
        record = event.__dict__ | {"at": utc_now()}
        record["event_digest"] = sha256_text(canonical_json(record))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        return record["event_digest"]


def no_progress(events: list[dict[str, Any]], threshold: int = 2) -> bool:
    if threshold < 2 or len(events) < threshold:
        return False
    tail = events[-threshold:]
    return len({(item.get("entity_id"), item.get("state"), item.get("payload_digest")) for item in tail}) == 1
