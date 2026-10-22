from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .errors import InvariantViolation


EXPECTED = {"skills": 18, "agents": 10, "prompts": 12, "workflows": 8, "state-machines": 6}
SKILL_SECTIONS = (
    "Purpose",
    "Trigger",
    "Do-not-trigger",
    "Inputs",
    "Preconditions",
    "Procedure",
    "Outputs",
    "Evidence",
    "Errors",
    "Security",
    "Stop",
    "Escalation",
    "Rollback",
    "Tests",
    "Runtime status",
)


def _require(value: bool, code: str) -> None:
    if not value:
        raise InvariantViolation(code)


def validate_controls(control_root: Path) -> dict[str, Any]:
    root = control_root.resolve(strict=True)
    results: dict[str, list[dict[str, str]]] = {key: [] for key in EXPECTED}
    names: set[str] = set()
    for path in sorted((root / "skills").glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        _require(text.startswith("---\n") and "\n---\n" in text[4:], f"ERR_SKILL_FRONTMATTER:{path}")
        match = re.search(r"(?m)^name:\s*([^\r\n]+)$", text)
        _require(match is not None, f"ERR_SKILL_NAME:{path}")
        name = match.group(1).strip() if match else ""
        _require(name == path.parent.name, f"ERR_SKILL_IDENTITY:{path}")
        _require(name not in names, f"ERR_SKILL_COLLISION:{name}")
        names.add(name)
        missing = [section for section in SKILL_SECTIONS if f"## {section}" not in text]
        _require(not missing, f"ERR_SKILL_SECTIONS:{name}:{missing}")
        _require("Do-not-trigger" in text and "Rollback" in text and "Evidence" in text, f"ERR_SKILL_BEHAVIOR:{name}")
        results["skills"].append({"id": name, "verdict": "PASS"})
    required_agent = ("|mission|", "|write_scope|", "|tool_whitelist|", "|stop_conditions|", "|forbidden_effects|", "|evidence|")
    for path in sorted((root / "agents").glob("AP-*.md")):
        text = path.read_text(encoding="utf-8")
        _require(all(field in text for field in required_agent), f"ERR_AGENT_CONTRACT:{path.name}")
        _require("self-grant" in text or "self-granted" in text, f"ERR_AGENT_PRIVILEGE_GUARD:{path.name}")
        results["agents"].append({"id": path.stem, "verdict": "PASS"})
    required_prompt = ("|role|", "|objective|", "|tool_policy|", "|reject_or_abstain|", "|evidence|", "|status|")
    for path in sorted((root / "prompts").glob("PC-*.md")):
        text = path.read_text(encoding="utf-8")
        _require(all(field in text for field in required_prompt), f"ERR_PROMPT_CONTRACT:{path.name}")
        _require("hidden chain-of-thought" in text or "hidden reasoning" in text, f"ERR_PROMPT_REASONING_GUARD:{path.name}")
        results["prompts"].append({"id": path.stem, "verdict": "PASS"})
    for path in sorted((root / "workflows").glob("WF-*.md")):
        text = path.read_text(encoding="utf-8")
        _require("|edge|from|to|guard|output|failure / compensation|timeout / checkpoint|" in text, f"ERR_WORKFLOW_GRAPH:{path.name}")
        _require("Terminal semantics" in text and "Cancellation propagates" in text, f"ERR_WORKFLOW_TERMINAL:{path.name}")
        results["workflows"].append({"id": path.stem, "verdict": "PASS"})
    for path in sorted((root / "state-machines").glob("SM-*.md")):
        text = path.read_text(encoding="utf-8")
        _require("Invalid transition" in text and "INVALID_TRANSITION" in text, f"ERR_STATE_MACHINE_NEGATIVE:{path.name}")
        _require("Requalification" in text and "|" in text, f"ERR_STATE_MACHINE_REQUALIFY:{path.name}")
        results["state-machines"].append({"id": path.stem, "verdict": "PASS"})
    observed = {key: len(value) for key, value in results.items()}
    _require(observed == EXPECTED, f"ERR_CONTROL_DENOMINATOR:{observed}")
    agents_files = sorted(root.rglob("AGENTS.md"))
    _require(bool(agents_files), "ERR_AGENTS_SCOPE_ABSENT")
    for path in agents_files:
        text = path.read_text(encoding="utf-8")
        lowered = text.casefold()
        _require(any(term in lowered for term in ("no ", "never ", "not ")), f"ERR_AGENTS_DENY_GUARD:{path}")
        _require(
            any(term in lowered for term in ("evidence", "provenance", "rollback", "restore", "hash")),
            f"ERR_AGENTS_AUDIT_GUARD:{path}",
        )
    return {
        "verdict": "PASS",
        "counts": observed,
        "behavior_results": results,
        "agents_effective_load": [str(path.relative_to(root)).replace("\\", "/") for path in agents_files],
    }
