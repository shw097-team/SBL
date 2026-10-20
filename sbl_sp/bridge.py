"""Skill bridge: discovery, matching, governed loading and invocation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from sbl_core.errors import SBLError


class SkillBridge:
    """A bridge bound to one skill manifest file."""

    def __init__(self, manifest_path: str) -> None:
        self.manifest_path = str(manifest_path)
        try:
            raw = Path(self.manifest_path).read_text(encoding="utf-8")
        except OSError as exc:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "skill manifest is missing or unreadable",
                {"path": self.manifest_path},
            ) from exc
        try:
            manifest: Any = json.loads(raw)
        except (TypeError, ValueError) as exc:
            raise SBLError(
                "SBL_E_BAD_STATE",
                "skill manifest is not valid JSON",
                {"path": self.manifest_path},
            ) from exc
        if not isinstance(manifest, dict):
            raise SBLError(
                "SBL_E_BAD_STATE",
                "skill manifest must be a JSON object",
                {"path": self.manifest_path},
            )
        self.manifest: dict = manifest
        self.name: str = str(manifest.get("name") or "")

    def discover(self) -> dict:
        return {
            "schema": "SBL-SKILL-DISCOVER/1",
            "skill": self.name,
            "triggers": list(self.manifest.get("triggers") or []),
            "permissions": list(self.manifest.get("permissions") or []),
        }

    def match(self, intent: str) -> bool:
        text = str(intent or "").lower()
        return any(
            str(trigger).lower() in text
            for trigger in (self.manifest.get("triggers") or [])
        )

    def effective_load(self, host: dict) -> dict:
        if not isinstance(host, dict) or host.get("provider_on") is not True:
            raise SBLError(
                "SBL_E_PROVIDER_OFF",
                "skill may not load while the host provider is off",
                {"skill": self.name},
            )
        host_name = host.get("name")
        seed = self.name + str(host_name or "")
        digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
        return {
            "schema": "SBL-SKILL-LOAD/1",
            "skill": self.name,
            "loaded": True,
            "host": host_name,
            "trace_id": "L-" + digest[:12],
        }

    def invoke(self, action: str, provider_on: bool) -> dict:
        if provider_on is not True:
            raise SBLError(
                "SBL_E_PROVIDER_OFF",
                "skill may not be invoked while the host provider is off",
                {"skill": self.name, "action": action},
            )
        permissions = set(self.manifest.get("permissions") or ())
        forbidden = set(self.manifest.get("forbidden") or ())
        if (
            action not in permissions
            or str(action).startswith(("repo.", "net."))
            or action in forbidden
        ):
            raise SBLError(
                "SBL_E_PERMISSION_DENIED",
                "skill is not permitted to perform this action",
                {"skill": self.name, "action": action},
            )
        return {"ok": True, "skill": self.name, "action": action}

    def unload(self) -> dict:
        return {"schema": "SBL-SKILL-UNLOAD/1", "unloaded": True, "residue": []}
