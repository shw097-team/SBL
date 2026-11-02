"""Deterministic primitives: canonical JSON, content-addressed ids, hashing."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def content_id(prefix: str, payload: Any, length: int = 16) -> str:
    """Content-addressed id. Same input lock -> same id (replay determinism)."""
    return f"{prefix}-{sha256_text(canonical_json(payload))[:length]}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


# Epoch fields are the ONLY fields allowed to differ between two replays of the
# same input lock (G-S4-REPLAY: no unexplained nondeterminism).
EPOCH_FIELDS = ("generated_at", "created_at", "updated_at", "run_id")
