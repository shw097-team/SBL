"""Thin TPM -> PIPD adapter (U04 C1/C2).

The adapter is deliberately thin: it takes an SBL TPM hand-off, asks the **installed**
``pipd-ls-sp`` distribution to compile the bounded chain

    IntentCard -> PI-PKG -> PD-PKG -> ConstructionContract -> ECP -> TQAEP

and returns the artefacts plus the compiler's own validation verdict. It contains no compiler
logic of its own — no schema, no oracle, no writer. If ``pipd_ls_sp`` is not installed it refuses
with ``SBL_E_PROVIDER_OFF`` instead of degrading into a second implementation.

Authority: the PIPD TQAEP this produces is a **design-time candidate**. The compiler records a
distinct checker identity, sets ``independent_acceptance = NOT_GRANTED`` and states what a live
checker must re-run. The adapter does not upgrade that ceiling and does not accept its own work.
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from sbl_core.errors import SBLError

ADAPTER_ID = "sbl-tpm-sp/pipd-adapter@0"
PIPD_DISTRIBUTION = "pipd-ls-sp"
PIPD_IMPORT = "pipd_ls_sp"

# PIPD typed refusal -> SBL typed refusal. No new SBL codes: the existing table is used, so a
# consumer of sbl_core.errors keeps one vocabulary.
_REFUSAL_MAP = {
    "AuthorityUnknown": "SBL_E_UNLOCATED_REQUIREMENT",
    "IntakeInvalid": "SBL_E_EMPTY_TITLE",
    "RepoContextMissing": "SBL_E_PROVIDER_OFF",
    "StaleProvider": "SBL_E_STALE_HEAD",
    "EffectUnknown": "SBL_E_WRITE_OUTSIDE_WRITESET",
    "TqSodFail": "SBL_E_SELF_CHECK_FORBIDDEN",
    "TqTraceFail": "SBL_E_BAD_STATE",
    "TqOracleFail": "SBL_E_BAD_STATE",
    "PiSchemaFail": "SBL_E_BAD_STATE",
    "PiSemanticFail": "SBL_E_BAD_STATE",
    "ValidationFail": "SBL_E_BAD_STATE",
    "IoNotFound": "SBL_E_BAD_STATE",
}

REQUIRED_HANDOFF = ("goal", "sources")


def _load() -> tuple[Any, Any, Any]:
    """Import the installed compiler, or refuse. Never fall back to a local copy."""
    try:
        pipeline = importlib.import_module(f"{PIPD_IMPORT}.pipeline")
        validate = importlib.import_module(f"{PIPD_IMPORT}.validate")
        errors = importlib.import_module(f"{PIPD_IMPORT}.errors")
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised by the no-pipd path
        raise SBLError(
            "SBL_E_PROVIDER_OFF",
            f"the {PIPD_DISTRIBUTION} distribution is not installed; the adapter will not "
            "substitute a second compiler",
            {"distribution": PIPD_DISTRIBUTION, "missing": getattr(exc, "name", "")},
        ) from None
    return pipeline, validate, errors


def _translate(exc: Exception) -> SBLError:
    code = _REFUSAL_MAP.get(type(exc).__name__, "SBL_E_BAD_STATE")
    return SBLError(code, str(exc), {"compiler_refusal": type(exc).__name__})


def _check_handoff(handoff: dict[str, Any]) -> None:
    if not isinstance(handoff, dict):
        raise SBLError("SBL_E_BAD_STATE", "the TPM hand-off must be an object")
    missing = [k for k in REQUIRED_HANDOFF if not handoff.get(k)]
    if missing:
        raise SBLError(
            "SBL_E_UNLOCATED_REQUIREMENT",
            "the TPM hand-off is missing the fields the compiler needs",
            {"missing": missing},
        )


def compile_handoff(
    handoff: dict[str, Any],
    repo_root: str | Path,
    *,
    profile: str = "LITE",
    maker: str = "SBL-TPM",
    checker: str = "",
    checker_execution_receipt: str = "",
    repo_context_claims: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compile one TPM hand-off into the bounded PIPD chain.

    ``handoff`` keys: ``goal`` (str), ``sources`` (repo-relative locators), optionally
    ``constraints`` and ``non_goals`` (lists). ``repo_context_claims`` are caller claims only —
    the compiler re-derives head/branch/dirty from the host and refuses a stale or spoofed claim.
    """
    _check_handoff(handoff)
    pipeline, validate_mod, errors_mod = _load()

    root = Path(repo_root)
    sources = []
    for locator in handoff["sources"]:
        candidate = Path(locator)
        sources.append(str(candidate if candidate.is_absolute() else (root / candidate)))

    try:
        card = pipeline.intake(
            handoff["goal"],
            sources=sources,
            constraints=list(handoff.get("constraints") or []),
            non_goals=list(handoff.get("non_goals") or []),
        )
        pi = pipeline.compile_pi(card, profile)
        context: dict[str, Any] = {"root": str(root)}
        context.update(repo_context_claims or {})
        pd = pipeline.bind_pd(pi, context)
        contract = pipeline.compile_construction_contract(pd)
        ecp = pipeline.compile_ecp(pd, pi)
        tqaep = pipeline.compile_tqaep(
            pi,
            ecp,
            maker=maker,
            checker=checker,
            checker_execution_receipt=checker_execution_receipt,
        )
    except errors_mod.PipdError as exc:
        raise _translate(exc) from None

    bundle = {"PI-PKG": pi, "PD-PKG": pd, "ConstructionContract": contract, "ECP": ecp, "TQAEP": tqaep}
    verdict = validate_mod.validate_bundle(bundle)
    if verdict.get("verdict") != "PASS":
        raise SBLError(
            "SBL_E_BAD_STATE",
            "the compiler produced a bundle that does not validate",
            {"findings": verdict.get("findings", [])[:10], "closure": verdict.get("closure")},
        )

    return {
        "adapter": ADAPTER_ID,
        "distribution": PIPD_DISTRIBUTION,
        "artifacts": bundle,
        "validation": verdict,
        "claim_ceiling": {
            "level": "PROMPT_COMPILE_PASS",
            "independent_acceptance": "NOT_GRANTED",
            "note": "design-time compile only; a live checker must re-run before any independent "
                    "acceptance, host load or release is claimed",
        },
    }
