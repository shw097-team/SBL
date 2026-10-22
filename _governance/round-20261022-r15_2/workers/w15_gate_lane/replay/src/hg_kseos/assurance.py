from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import InvariantViolation


def require(condition: bool, code: str) -> None:
    if not condition:
        raise InvariantViolation(code)


def resolve_instruction_chain(rows: list[dict[str, object]]) -> list[str]:
    ordered = sorted(rows, key=lambda row: int(row["scope_rank"]))
    highest_authority = -1
    accepted: list[str] = []
    for row in ordered:
        authority = int(row["authority_rank"])
        require(not bool(row.get("stale")), "ERR_STALE_INSTRUCTION")
        require(authority >= highest_authority, "ERR_INSTRUCTION_PRECEDENCE_OVERRIDE")
        highest_authority = authority
        accepted.append(str(row["id"]))
    return accepted


class SkillRegistry:
    def __init__(self) -> None:
        self.skills: dict[str, tuple[frozenset[str], bool]] = {}

    def install(self, name: str, triggers: set[str], implicit_allowed: bool) -> None:
        require(name not in self.skills, "ERR_SKILL_NAME_COLLISION")
        occupied = set().union(*(entry[0] for entry in self.skills.values())) if self.skills else set()
        require(not (occupied & triggers), "ERR_SKILL_TRIGGER_COLLISION")
        self.skills[name] = (frozenset(triggers), implicit_allowed)

    def route(self, name: str, explicit: bool) -> str:
        require(name in self.skills, "ERR_SKILL_UNKNOWN")
        require(explicit or self.skills[name][1], "ERR_SKILL_IMPLICIT_FORBIDDEN")
        return name

    def remove(self, name: str) -> None:
        require(name in self.skills, "ERR_SKILL_UNKNOWN")
        del self.skills[name]
        require(name not in self.skills, "ERR_SKILL_REMOVAL_RESIDUE")


def negotiate_mcp(client: str, server: str, dual_era: set[tuple[str, str]]) -> str:
    if client == server:
        return "PINNED_CONFORMANT"
    require((client, server) in dual_era, "ERR_MCP_REVISION_INCOMPATIBLE")
    return "DUAL_ERA_ADAPTER"


def require_fresh_base(expected: str, current: str) -> None:
    require(expected == current, "ERR_STALE_BASE")


def deterministic_gate(deterministic_pass: bool, judge_pass: bool) -> str:
    del judge_pass
    require(deterministic_pass, "ERR_DETERMINISTIC_ORACLE_FAIL")
    return "PASS"


def telemetry_gate(captures_prompt: bool, explicit_opt_in: bool, redacted: bool) -> None:
    require(not captures_prompt or (explicit_opt_in and redacted), "ERR_TELEMETRY_PROMPT_PRIVACY")


def budget_decision(spend: int, degrade_at: int, stop_at: int) -> str:
    require(0 <= degrade_at <= stop_at, "ERR_BUDGET_POLICY")
    if spend >= stop_at:
        return "STOP_ESCALATE"
    if spend >= degrade_at:
        return "DEGRADE"
    return "CONTINUE"


def reconcile_sbom(declared: set[str], observed: set[str]) -> None:
    require(declared == observed, "ERR_SBOM_UNEXPLAINED_DEPENDENCY")


def migration_gate(left: object, right: object) -> None:
    require(left == right, "ERR_MIGRATION_DUAL_READ_MISMATCH")


def validate_receiver_packet(packet: dict[str, object], capabilities: set[str]) -> str:
    require(bool(packet.get("rollback")), "ERR_RECEIVER_ROLLBACK_MISSING")
    required = set(packet.get("required_capabilities", []))
    require(required <= capabilities, "ERR_RECEIVER_CAPABILITY")
    if packet.get("receiver_verdict") == "NACK":
        require(bool(packet.get("field_defects")), "ERR_RECEIVER_NACK_WITHOUT_DEFECT")
        return "REWORK"
    return "ACK"


def exact_behavior_set(before: set[str], after: set[str]) -> None:
    require(before <= after, "ERR_LEGACY_BEHAVIOR_REMOVED")


def reconcile_release_identity(release_tag: str, registry_tag: str, release_hash: str, registry_hash: str) -> None:
    require(release_tag == registry_tag and release_hash == registry_hash, "ERR_RELEASE_REGISTRY_DRIFT")


def require_archive_failure_propagation(validation_ok: bool, exit_code: int) -> None:
    require(validation_ok or exit_code != 0, "ERR_ARCHIVE_FALSE_SUCCESS")


def validate_rollback_pointer(pointer: Path) -> None:
    require(pointer.exists(), "ERR_ROLLBACK_POINTER_MISSING")


def prompt_contract(output: dict[str, object], required: set[str], requests_hidden_reasoning: bool) -> None:
    require(not requests_hidden_reasoning, "ERR_HIDDEN_CHAIN_OF_THOUGHT_REQUEST")
    require(required <= set(output), "ERR_PROMPT_OUTPUT_SCHEMA")


def security_veto(veto: bool, human_override: bool) -> str:
    require(not veto or human_override, "ERR_SECURITY_VETO_BLOCKING")
    return "PASS"


def provider_compatibility(required: set[str], candidate: set[str]) -> None:
    require(required <= candidate, "ERR_PROVIDER_CAPABILITY_GAP")


@dataclass
class EffectToken:
    token: str
    expires_at: int
    consumed: bool = False

    def consume(self, now: int) -> None:
        require(now <= self.expires_at, "ERR_EFFECT_TOKEN_EXPIRED")
        require(not self.consumed, "ERR_EFFECT_TOKEN_REPLAY")
        self.consumed = True


def select_permission_mode(supports_profiles: bool, supports_legacy: bool) -> str:
    if supports_profiles:
        return "PERMISSION_PROFILE"
    require(supports_legacy, "ERR_NO_COMPATIBLE_PERMISSION_MODE")
    return "LEGACY_SANDBOX"
