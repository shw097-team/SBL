"""lane_policy.py — HG-KSEOS model-lane routing policy library (CANDIDATE).

# HGK-LANE-POLICY-ANCHOR: single canonical policy module for FAR-LANE-SOD-003.

This is the library half of the candidate lane-enforcement kit. It reads the single-source
registry (`config/lane-routing-registry.yaml`), projects the full policy document, checks the live
projection sites for drift (returning every disagreement as a JSON pointer), checks the
maker/checker SoD invariant, and renders receipts.

Everything here is CANDIDATE. It never mutates the live sites it reads; `check_drift` opens live
files read-only. Standard library only (PyYAML is used for YAML parsing and is the one optional
dependency, with a pure-`json` fallback for JSON-shaped files).

Anchor used by tests/test_lane_policy.py: the first line of this file. A drift-injection subcase
may replace this line with a wall-clock/`created_at`-free alternative to prove the file is the live
module, so keep the anchor on line 1.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

__all__ = [
    "LANE_ORDER",
    "load_registry",
    "load_site",
    "resolve_pointer",
    "normalize_model",
    "route_for_lane",
    "project_policy",
    "check_sod",
    "sod_declaration_exemption",
    "check_drift",
    "render_receipt",
    "registry_epoch",
    "check_exclusions",
    "ANCHOR",
]

ANCHOR = "HGK-LANE-POLICY-ANCHOR"
LANE_ORDER = ("PLAN", "EXECUTE", "VERIFY_SECURITY")

_HERE = Path(__file__).resolve()
REPO_ROOT = _HERE.parent.parent.parent
DEFAULT_REGISTRY = REPO_ROOT / "config" / "lane-routing-registry.yaml"


# --------------------------------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------------------------------
def _json_load_unique(text: str) -> Any:
    """Parse JSON, rejecting duplicate object keys (a real routing-fact hazard)."""

    def _pair_hook(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        seen: set[str] = set()
        for key, _ in pairs:
            if key in seen:
                raise ValueError(f"duplicate JSON object key: {key!r}")
            seen.add(key)
        return dict(pairs)

    return json.loads(text, object_pairs_hook=_pair_hook)


def _yaml_load_unique(text: str) -> Any:
    """Parse YAML, rejecting duplicate mapping keys when PyYAML is available."""
    try:
        import yaml  # local import; optional dependency
    except Exception:  # pragma: no cover - only when PyYAML absent
        return None

    class _UniqueKeyLoader(yaml.SafeLoader):
        pass

    def _construct_mapping(loader, node, deep=False):
        loader.flatten_mapping(node)
        result: dict[Any, Any] = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in result:
                raise ValueError(f"duplicate YAML mapping key: {key!r}")
            result[key] = loader.construct_object(value_node, deep=deep)
        return result

    _UniqueKeyLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
    )
    return yaml.load(text, Loader=_UniqueKeyLoader)  # noqa: S506 - SafeLoader subclass


def load_site(path: Path) -> Any:
    """Read a projection site read-only and parse it (JSON preferred, YAML fallback)."""
    text = Path(path).read_text(encoding="utf-8")
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return _json_load_unique(text)
    if suffix in (".yaml", ".yml"):
        parsed = _yaml_load_unique(text)
        if parsed is not None:
            return parsed
        # Fallback: YAML files that are json-shaped YAML parse as JSON only when quoted.
        return _json_load_unique(text)
    # Unknown suffix: try JSON, then YAML.
    try:
        return _json_load_unique(text)
    except Exception:
        parsed = _yaml_load_unique(text)
        if parsed is None:
            raise
        return parsed


def load_registry(path: Path | None = None) -> dict[str, Any]:
    """Load the single-source registry document."""
    registry_path = Path(path) if path is not None else DEFAULT_REGISTRY
    doc = load_site(registry_path)
    if not isinstance(doc, dict) or doc.get("schema") != "HGK-LANE-ROUTING-REGISTRY/1":
        raise ValueError(f"not a HGK-LANE-ROUTING-REGISTRY/1 document: {registry_path}")
    return doc


def registry_epoch(registry: dict[str, Any]) -> int:
    return int(registry["epoch"])


# --------------------------------------------------------------------------------------------------
# JSON pointer + model identity
# --------------------------------------------------------------------------------------------------
def resolve_pointer(doc: Any, pointer: str) -> Any:
    """Resolve an RFC-6901 JSON pointer against a parsed document; raise KeyError if absent."""
    if pointer in ("", "/"):
        return doc
    if not pointer.startswith("/"):
        raise KeyError(f"pointer must start with '/': {pointer!r}")
    cur = doc
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, list):
            cur = cur[int(token)]
        elif isinstance(cur, dict):
            cur = cur[token]
        else:
            raise KeyError(f"cannot descend into {type(cur).__name__} at {token!r} for {pointer}")
    return cur


def normalize_model(model: str) -> str:
    """Normalize a model id to a comparison token: lowercase, drop any provider prefix."""
    token = str(model).strip().lower()
    if "/" in token:
        token = token.split("/")[-1]
    return token


def route_for_lane(registry: dict[str, Any], lane: str) -> dict[str, Any] | None:
    for route in registry.get("routes", []):
        if route.get("lane") == lane:
            return route
    return None


def _compact_route(route: dict[str, Any]) -> dict[str, Any]:
    return {
        "lane": route["lane"],
        "engine": route["engine"],
        "provider": route["provider"],
        "model": route["model"],
        "canonical_identity": route.get("canonical_identity", normalize_model(route["model"])),
        "auth": route["auth"],
        "oauth": bool(route.get("oauth", False)),
        "fallbacks": list(route.get("fallbacks", [])),
        "admission_status": route.get("admission_status", "UNPROVEN"),
        # V5: reasoning_effort is routing-relevant and must survive compaction, otherwise a declared
        # per-lane effort is silently dropped from the projection and cannot be drift-checked.
        "reasoning_effort": route.get("reasoning_effort"),
        # W1.2b (round HGK-SOLUTION-APPLY-20261012): the projected dispatch must carry the arm
        # list and the selection authority rather than dropping them. Without these three fields a
        # dual-arm route (VERIFY_SECURITY A/B) projects as only its primary route, so an operator
        # alternate arm is unreachable through the projection. Carried by deep copy so the caller
        # cannot mutate the parsed registry.
        "arms": copy.deepcopy(route["arms"]) if route.get("arms") else [],
        "selection_authority": route.get("selection_authority"),
        "selected_arm": route.get("selected_arm"),
    }


# --------------------------------------------------------------------------------------------------
# projection
# --------------------------------------------------------------------------------------------------
def project_policy(registry: dict[str, Any], *, registry_path: Path | None = None) -> dict[str, Any]:
    """Produce the full projected policy document from the registry."""
    routes = {lane: _compact_route(route_for_lane(registry, lane)) for lane in LANE_ORDER
              if route_for_lane(registry, lane) is not None}
    lane_chains = {
        lane: ([routes[lane]] + list(routes[lane]["fallbacks"])) if lane in routes else []
        for lane in LANE_ORDER
    }
    doc = {
        "schema": "HGK-LANE-POLICY/1",
        "status": "CANDIDATE",
        "epoch": registry_epoch(registry),
        "source_registry": {
            "path": registry.get("source_of_routes", {}).get("path", "config/lane-routing-registry.yaml"),
            "sha256": _sha256_file(registry_path) if registry_path and registry_path.exists() else None,
        },
        "routes": routes,
        "lane_chains": lane_chains,
        "invariants": dict(registry.get("invariants", {})),
        "sod_invariants": copy.deepcopy(registry.get("sod_invariants", {})),
        "projections": [
            {"id": p.get("id"), "path": p.get("path"),
             "bindings": [b.get("pointer") for b in p.get("bindings", [])]}
            for p in registry.get("projections", [])
        ],
        "claim_ceiling": "CANDIDATE_ONLY",
    }
    return doc


# --------------------------------------------------------------------------------------------------
# SoD
# --------------------------------------------------------------------------------------------------
def check_sod(maker: Any, checker: Any, *, axis: str = "canonical_identity") -> tuple[bool, str]:
    """Return (ok, reason). ok is False when maker and checker share a normalized model token.

    `maker`/`checker` may be a model id string or a mapping with a `model`/`canonical_identity`
    field. A missing/empty model is a violation (fail closed).
    """
    m = _identity(maker, axis)
    c = _identity(checker, axis)
    if not m or not c:
        return False, f"SOD_UNDETERMINED maker={m!r} checker={c!r}"
    if m == c:
        return False, f"SOD_VIOLATION maker_model={m} == checker_model={c}"
    return True, f"SOD_OK {m} != {c}"


def sod_declaration_exemption(
    registry: dict[str, Any],
    maker_lane: str | None,
    checker_lane: str | None,
) -> tuple[str | None, str]:
    """Return (conflict_id, reason) for an OWNER-ORDERED same-model lane exemption.

    A same-model (maker_lane, checker_lane) pair is EXEMPTED only when the registry declares BOTH:
      * an `sod_invariants.pairs` entry whose maker/checker match the pair (either orientation) with
        `distinct_required` exactly false; and
      * an `sod_invariants.declared_conflicts` entry listing that EXACT pair with `status` exactly
        `OWNER_ORDERED_IN_FORCE`.

    Returns the conflict id when exempted; otherwise None plus a short reason. This is a pure read of
    the registry document and never weakens `check_sod` (which stays a two-token comparison).
    """
    if not maker_lane or not checker_lane:
        return None, "UNDETERMINED lane pair (maker_lane/checker_lane unresolved)"
    sod = registry.get("sod_invariants") or {}
    pair = None
    for entry in sod.get("pairs") or []:
        if {entry.get("maker"), entry.get("checker")} == {maker_lane, checker_lane}:
            pair = entry
            break
    if pair is None:
        return None, f"no sod_invariants.pairs entry for {maker_lane}/{checker_lane}"
    if pair.get("distinct_required") is not False:
        return None, (f"pair {maker_lane}/{checker_lane} distinct_required is not false "
                      f"(got {pair.get('distinct_required')!r})")
    for conflict in sod.get("declared_conflicts") or []:
        if conflict.get("status") != "OWNER_ORDERED_IN_FORCE":
            continue
        for declared in conflict.get("pairs") or []:
            if not isinstance(declared, (list, tuple)) or len(declared) != 2:
                continue
            if {declared[0], declared[1]} == {maker_lane, checker_lane}:
                cid = conflict.get("id")
                return cid, (f"pair {maker_lane}/{checker_lane} exempted by declared conflict "
                             f"{cid} status=OWNER_ORDERED_IN_FORCE")
    return None, (f"no OWNER_ORDERED_IN_FORCE declared_conflicts entry lists "
                  f"{maker_lane}/{checker_lane}")


def _identity(worker: Any, axis: str) -> str:
    if isinstance(worker, dict):
        value = worker.get(axis) or worker.get("model") or ""
    else:
        value = worker or ""
    return normalize_model(value)


def check_exclusions(
    registry: dict[str, Any],
    round_id: str | None = None,
    provider: str | None = None,
    model: str | None = None,
) -> tuple[bool, str]:
    """C4 round model-exclusion guard.

    A model family the owner excludes for a round must not be restorable by a registry default or an
    inherited child setting. Given the resolved provider/model for a governed dispatch, refuse when
    either matches `round_model_exclusions` in the registry.

    Return (ok, code). ok is True only when the resolved route is NOT excluded. A missing/empty
    provider or model is UNDETERMINED and therefore refused (fail closed): an undefined route cannot
    be proven to be outside the excluded set.
    """
    block = registry.get("round_model_exclusions") or {}
    prefixes = [str(p).lower() for p in block.get("excluded_model_prefixes", [])]
    providers = [str(p).lower() for p in block.get("excluded_providers", [])]
    rid = round_id or block.get("scope", "")
    prov = str(provider or "").strip().lower()
    tok = normalize_model(model or "")
    if not prov or not tok:
        return False, f"SOD_UNDETERMINED excluded_guard round={rid} provider={provider!r} model={model!r}"
    for p in prefixes:
        if tok.startswith(p):
            return False, f"ERR_MODEL_FAMILY_EXCLUDED_ROUND round={rid} model={model} matches prefix {p!r}"
    if prov in providers:
        return False, f"ERR_MODEL_FAMILY_EXCLUDED_ROUND round={rid} provider={provider} is excluded"
    return True, f"EXCLUSION_OK round={rid} provider={provider} model={model}"


# --------------------------------------------------------------------------------------------------
# drift
# --------------------------------------------------------------------------------------------------
def check_drift(
    registry_path: Path | None = None,
    *,
    root: Path | None = None,
    registry: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Compare live projection sites against the registry; return every disagreement.

    Each finding is a dict: {code, path, pointer, expected, actual, severity, id}. Codes:
      DRIFT_VALUE       active site disagrees with the registry        (severity: error)
      COVERAGE_GAP      projection/site/pointer missing or unresolved (severity: error)
      PROJECTION_DEBT   a recorded debt site still differs            (severity: warn)
    An empty list means the active sites are conformant.
    """
    reg = registry if registry is not None else load_registry(registry_path)
    reg_path = Path(registry_path) if registry_path is not None else DEFAULT_REGISTRY
    base = Path(root) if root is not None else reg_path.parent.parent

    findings: list[dict[str, Any]] = []
    projections = reg.get("projections")
    if not isinstance(projections, list) or not projections:
        findings.append(_finding("COVERAGE_GAP", "-", "-", "non-empty projections[]", None, "error"))
        return findings

    for projection in projections:
        site_path = projection.get("path")
        pid = projection.get("id", site_path)
        if not site_path:
            findings.append(_finding("COVERAGE_GAP", str(pid), "-", "path", None, "error"))
            continue
        resolved = (base / site_path) if not Path(site_path).is_absolute() else Path(site_path)
        if not resolved.exists():
            findings.append(_finding("COVERAGE_GAP", str(site_path), "-", "file exists", None, "error"))
            continue
        try:
            doc = load_site(resolved)
        except Exception as exc:  # parse failure is a hard coverage gap
            findings.append(_finding("COVERAGE_GAP", str(site_path), "-", "parseable", f"{type(exc).__name__}: {exc}", "error"))
            continue

        for binding in projection.get("bindings", []):
            pointer = binding.get("pointer")
            expected = binding.get("expected")
            actual = _try_pointer(doc, pointer)
            if actual is _MISSING:
                findings.append(_finding("COVERAGE_GAP", site_path, pointer, expected, None, "error", pid))
            elif actual != expected:
                findings.append(_finding("DRIFT_VALUE", site_path, pointer, expected, actual, "error", pid))

        for debt in projection.get("debt", []):
            pointer = debt.get("pointer")
            expected = debt.get("expected")
            actual = _try_pointer(doc, pointer)
            if actual is _MISSING or actual != expected:
                findings.append(_finding("PROJECTION_DEBT", site_path, pointer, expected,
                                         None if actual is _MISSING else actual, "warn", pid))

    return findings


class _Missing:
    pass


_MISSING = _Missing()


def _try_pointer(doc: Any, pointer: str | None) -> Any:
    if not pointer:
        return _MISSING
    try:
        return resolve_pointer(doc, pointer)
    except (KeyError, IndexError, ValueError, TypeError):
        return _MISSING


def _finding(code, path, pointer, expected, actual, severity, pid=None) -> dict[str, Any]:
    return {
        "code": code,
        "id": pid,
        "path": path,
        "pointer": pointer,
        "expected": expected,
        "actual": actual,
        "severity": severity,
    }


def drift_is_fatal(findings: list[dict[str, Any]]) -> bool:
    return any(f.get("severity") == "error" for f in findings)


# --------------------------------------------------------------------------------------------------
# receipt
# --------------------------------------------------------------------------------------------------
def render_receipt(
    *,
    registry: dict[str, Any],
    findings: list[dict[str, Any]] | None = None,
    checked_sites: int = 0,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    findings = findings or []
    receipt: dict[str, Any] = {
        "schema": "HGK-LANE-DRIFT/1",
        "status": "CANDIDATE",
        "epoch": registry_epoch(registry),
        "checked_sites": int(checked_sites),
        "fatal": drift_is_fatal(findings),
        "findings": findings,
        "claim_ceiling": "CANDIDATE_ONLY",
    }
    if extra:
        receipt.update(extra)
    return receipt


def count_checked_sites(registry: dict[str, Any]) -> int:
    return sum(
        len(p.get("bindings", [])) + len(p.get("debt", []))
        for p in registry.get("projections", [])
    )


# --------------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------------
def _sha256_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _load_structured(path: Path) -> Any:  # backwards-compatible alias
    return load_site(path)


_ = re  # keep the stdlib import explicit; used by future pointer validation
