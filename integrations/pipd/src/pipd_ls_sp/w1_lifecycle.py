"""W1 · WP-FHS-05 — the canonical PIPD lifecycle chain (Intake → SourceFreeze → Profile →
PI(strict)+sidecar → RepoContext → PD → DEV/OPS ECP → PlannedTQAEP).

Why this module exists
----------------------
`WP-FHS-05` does not ask for a new compiler: it asks that the ORIGINAL writers run in a fixed
order, that the two separation rules the W1 contract makes normative become executable, and that
the chain end in a record that names its own ceiling. Nothing here issues authority:

* the 13-command CLI is untouched (no 14th command; this is library-only),
* the 19 contract families are untouched (no new schema family, no new `schema_version`),
* every emitted leg is `AUTHOR_DESIGN_ONLY` / `EFFECT_UNBOUND`; the on-host legs
  (`installed`, `loaded`, `invoked`, `consumer ACK`) stay `NOT_RUN`.

Two executable separation rules
-------------------------------
1. **strict PI payload vs the `SBL.PI.Crosswalk` sidecar.** The sidecar is a non-record projection:
   it is never a strict payload, and it is never Raw evidence (`is_raw=False`). A strict payload
   that carries a `_`-prefixed sidecar key is refused with
   `WP-FHS-05.FIRST_FAIL:PIPD_FORMAL_PROMOTION_HOLD`.
2. **DEV vs OPS effect path.** One PD yields two ECP candidates with distinct effect classes and
   distinct permission scopes. Reusing one permission basis for both is refused
   (`ECP_DEV_OPS_MIXED`) instead of silently emitting one record twice.

RepoContext is late-bound and DERIVED: a caller-supplied HEAD is a claim, and a claim that
disagrees with the local probe is refused (`PD_REPOCONTEXT_UNBOUND`), never promoted.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from . import pipeline
from . import repo_context as repo_probe
from .errors import PipdError, RepoContextMissing, TqSodFail
from .util import canonical_json, sha256_bytes, sha256_text

SCHEMA = "FHS.W1.WP05.LifecycleChain@1"
STRICT_CEILING = "AUTHOR_DESIGN_ONLY"
ON_HOST_LEGS = ("installed", "loaded", "invoked", "consumer_ack")


class LifecycleRefusal(PipdError):
    """A chain invariant was violated; the message names the leg that refused."""

    code = "LIFECYCLE_REFUSED"


class SourceFreezeFail(PipdError):
    code = "SOURCE_FREEZE_FAIL"


class SidecarContamination(PipdError):
    """The sidecar payload was presented as the strict PI payload (or as Raw)."""

    code = "PIPD_FORMAL_PROMOTION_HOLD"


class DevOpsPathMixed(PipdError):
    """DEV and OPS effect paths shared one permission basis."""

    code = "ECP_DEV_OPS_MIXED"


class RepoContextForeign(PipdError):
    """A RepoContext claim did not match the local probe (e.g. a remote HEAD presented as local)."""

    code = "PD_REPOCONTEXT_UNBOUND"


# ---------------------------------------------------------------- 1. SourceFreeze
def _digest_tree(root: Path, *, cap: int = 4096) -> dict[str, Any]:
    entries: list[tuple[str, str, int]] = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if rel.split("/")[0] in {".git", "__pycache__", "node_modules"}:
            continue
        entries.append((rel, sha256_bytes(path.read_bytes()), path.stat().st_size))
        if len(entries) >= cap:
            break
    aggregate = sha256_text(canonical_json([(rel, sha) for rel, sha, _ in entries]))
    return {"kind": "directory", "files": len(entries), "bytes": sum(n for _, _, n in entries),
            "sha256": aggregate, "manifest": entries[:cap]}


def source_freeze(paths: list[str]) -> dict[str, Any]:
    """Freeze every source locator to a digest before any compilation may read it.

    Refusals are typed and happen before a PI exists: an empty set, a locator that does not
    resolve, or two locators with identical bytes (one source, counted twice) all refuse.
    """
    locators = [str(p) for p in (paths or []) if str(p).strip()]
    if not locators:
        raise SourceFreezeFail("source freeze requires at least one resolvable source locator")
    sources: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for raw in locators:
        p = Path(raw)
        if not p.exists():
            raise SourceFreezeFail(f"source locator does not resolve: {raw}")
        if p.is_dir():
            rec = _digest_tree(p)
            rec.pop("manifest", None)
            digest = rec["sha256"]
        else:
            data = p.read_bytes()
            digest = sha256_bytes(data)
            rec = {"kind": "file", "files": 1, "bytes": len(data), "sha256": digest}
        if digest in seen:
            raise SourceFreezeFail(
                f"duplicate source content: {raw} and {seen[digest]} freeze to the same digest")
        seen[digest] = raw
        sources.append({"locator": p.as_posix(), **rec})
    body = {"schema": "PIPD.SourceFreeze@1", "sources": sources,
            "count": len(sources), "claim_ceiling": "SOURCE_READ"}
    body["content_hash"] = sha256_text(canonical_json(body))
    body["subject_id"] = "SF-" + body["content_hash"][:16]
    return body


# ---------------------------------------------------------------- 2. PI strict / sidecar
def split_pi(pi: dict[str, Any]) -> dict[str, Any]:
    """Split a compiled PI into its strict record and its crosswalk sidecar.

    The two halves must be disjoint by construction; if a strict key is missing or a sidecar key
    leaked into the strict body, that is the W1 first-fail, not a formatting problem.
    """
    side = {k: v for k, v in pi.items() if k.startswith("_")}
    strict = {k: v for k, v in pi.items() if not k.startswith("_")}
    if not side:
        raise SidecarContamination("PI carries no sidecar: the crosswalk leg cannot be silently absent")
    if not strict.get("stable_semantic_contract") or not strict.get("content_hash"):
        raise SidecarContamination("strict PI payload is missing its sealed semantic body")
    sidecar = {
        "schema": "SBL.PI.Crosswalk@2",
        "subject_id": strict["subject_id"],
        "strict_sha256": sha256_text(canonical_json(strict)),
        "profile_meta": side.get("_profile_meta"),
        "is_raw": False,
        "evidence_class": "SIDECAR_NOT_RAW",
        "claim_ceiling": STRICT_CEILING,
        "note": ("non-record projection: it documents how the profile was computed and can never "
                 "be promoted into the strict payload or used as execution evidence"),
    }
    return {"strict": strict, "sidecar": sidecar,
            "digests": {"strict": sidecar["strict_sha256"],
                        "sidecar": sha256_text(canonical_json(sidecar))}}


def assert_strict_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Refuse a promotion payload that carries sidecar keys (the WP-FHS-05 first-fail)."""
    leaked = sorted(k for k in payload if k.startswith("_"))
    if leaked:
        raise SidecarContamination(
            "strict payload carries sidecar keys " + ", ".join(leaked)
            + ": sidecar metadata cannot be promoted into a strict record")
    return payload


# ---------------------------------------------------------------- 3. RepoContext gate
def assert_repo_context_local(pd: dict[str, Any], repo_root: str) -> dict[str, Any]:
    """Prove the PD's RepoContext came from the LOCAL probe, not from a caller claim."""
    ctx = pd.get("RepoContext") or {}
    if not ctx.get("root"):
        raise RepoContextMissing("PD has no RepoContext (no PREDEV_READY without one)")
    derived = repo_probe.probe_repository(repo_root)
    if ctx.get("probe") != derived.get("probe") or ctx.get("head") != derived.get("head"):
        raise RepoContextForeign(
            "RepoContext disagrees with the local probe "
            f"(pd={ctx.get('probe')}:{ctx.get('head')} local={derived.get('probe')}:{derived.get('head')})")
    if ctx.get("currentness_epoch") != derived.get("currentness_epoch"):
        raise RepoContextForeign("RepoContext currentness epoch is stale against the local probe")
    return {"state": "LOCAL_PROBE_MATCHES", "probe": derived.get("probe"),
            "head": derived.get("head"), "branch": derived.get("branch"),
            "dirty": derived.get("dirty"), "tracked_files": derived.get("tracked_files")}


# ---------------------------------------------------------------- 4. DEV / OPS paths
def dev_ops_ecp(pi: dict[str, Any], pd: dict[str, Any]) -> dict[str, Any]:
    """Emit the DEV and OPS effect candidates from one PD, with distinct permission bases."""
    dev = pipeline.compile_ecp(pd, pi)
    dev = dict(dev)
    dev["effect_intent"] = {"effect_class": "DEV_REPO_WRITE",
                            "statement": dev.get("effect_intent"),
                            "state": "EFFECT_UNBOUND", "claim_ceiling": STRICT_CEILING}
    # The body changed, so the identity must be re-issued: a mutated body under the old digest is
    # exactly what validate.semantic_invariants refuses.
    pipeline._seal(dev, "ECP")

    scope = (pd.get("late_bound_construction_binding") or {}).get("writable_scope") or ""
    ops_scope = "HOST_OP:UNBOUND"
    if not scope:
        raise LifecycleRefusal("OPS path needs the PD's bound writable scope as its contrast basis")
    payload = {"pd": pd["subject_id"], "pi": pi["subject_id"], "effects": ["HOST_OP"]}
    ops = pipeline._seal(pipeline._rec(
        "ECP", "ECP", payload,
        effect_intent={"effect_class": "HOST_OP",
                       "statement": "host-level operation candidate (installed/loaded leg)",
                       "state": "EFFECT_UNBOUND", "claim_ceiling": STRICT_CEILING},
        permission={"scope": ops_scope, "basis": "ORIGINAL_HOST_ISSUER_ONLY", "token_required": True,
                    "grant_state": "NOT_GRANTED"},
        retries={"policy": "reconcile_first", "on_unknown": "WORLD_READER_RECONCILE",
                 "reconcile_reader": "ORIGINAL_HOST_WORLD_READER"},
        idempotency={"key": pipeline.content_id("IDEM", {**payload, "e": "HOST_OP"}),
                     "guarantee": "DESIGN_ONLY"},
        readback={"required": True, "kind": "HOST_WORLD_RAW", "state": "NOT_RUN"},
        rollback={"required": True, "recovery": {"host_recovery": "ORIGINAL_INSTALLER_INVERSE"},
                  "state": "RECOVERY_DESIGN_ONLY"}), "ECP")

    dev_basis = (dev.get("permission") or {}).get("scope")
    ops_basis = (ops.get("permission") or {}).get("scope")
    if dev_basis and dev_basis == ops_basis:
        raise DevOpsPathMixed(
            f"DEV and OPS effect paths share one permission basis ({dev_basis!r}); separate them")
    if dev["effect_intent"]["effect_class"] == ops["effect_intent"]["effect_class"]:
        raise DevOpsPathMixed("DEV and OPS effect classes collapsed into one path")
    return {"dev": dev, "ops": ops,
            "separation": {"dev_scope": dev_basis, "ops_scope": ops_basis,
                           "dev_class": dev["effect_intent"]["effect_class"],
                           "ops_class": ops["effect_intent"]["effect_class"],
                           "shared_permission_basis": False,
                           "claim_ceiling": STRICT_CEILING}}


# ---------------------------------------------------------------- 5. chain
def run_chain(goal: str, sources: list[str], *, repo_root: str, profile: str = "LITE",
              writable_scope: str = "src/**", maker: str = "PIPD-MAKER",
              checker: str = "", checker_receipt: str = "",
              subject: str = "FHS-W1-WP05") -> dict[str, Any]:
    """Run the eight legs in order and return the chain record.

    Every leg contributes `(name, artifact id, digest, reader, state)`. A leg that cannot run
    refuses the chain with its own typed code; nothing is emitted as a stand-in for a missing leg.
    """
    stages: list[dict[str, Any]] = []

    def stage(name: str, art: dict[str, Any], reader: str, state: str = "PASS") -> None:
        stages.append({"leg": name, "subject_id": art.get("subject_id"),
                       "digest": art.get("content_hash") or art.get("strict_sha256"),
                       "reader": reader, "state": state})

    freeze = source_freeze(sources)
    stage("source_freeze", freeze, "PIPD SourceFreeze writer")

    card = pipeline.intake(goal, sources=sources)
    stage("intake", card, "PIPD intake compiler")

    axes = sorted({a.get("axis") or "intent" for a in card.get("atoms") or []}) or ["intent"]
    pb, profile_full = pipeline.profile_record(profile, axes)
    stage("profile", pb, "PIPD profile compiler")

    pi = pipeline.compile_pi(card, profile)
    strict = split_pi(pi)
    assert_strict_payload(strict["strict"])
    stage("compile_pi_strict", strict["strict"], "SBL PIPD PI writer")
    stages.append({"leg": "compile_pi_sidecar", "subject_id": strict["sidecar"]["subject_id"],
                   "digest": strict["digests"]["sidecar"], "reader": "SBL.PI.Crosswalk@2 reader",
                   "state": "SIDECAR_NOT_RAW"})

    ctx = repo_probe.derive_repo_context(repo_root, writable_scope=writable_scope)
    stage("repo_context", {"subject_id": "RC-" + str(ctx.get("currentness_epoch"))[:12],
                           "content_hash": ctx.get("manifest_sha256")},
          f"{ctx.get('probe')} probe", "LOCAL_PROBE")

    pd = pipeline.bind_pd(pi, ctx)
    local = assert_repo_context_local(pd, repo_root)
    stage("bind_pd", pd, "SBL PIPD PD writer", "LATE_BOUND")

    both = dev_ops_ecp(strict["strict"], pd)
    stage("ecp_dev", both["dev"], "SBL PIPD ECP writer")
    stage("ecp_ops", both["ops"], "ORIGINAL HOST ISSUER (not run)", "EFFECT_UNBOUND")

    if not checker.strip() or not checker_receipt.strip():
        raise TqSodFail("TQAEP requires a distinct checker identity and its execution receipt")
    tqaep = pipeline.compile_tqaep(strict["strict"], both["dev"], maker=maker, checker=checker,
                                   checker_execution_receipt=checker_receipt)
    stage("tqaep", tqaep, "SBL TQAEP writer", "DESIGN_CANDIDATE")

    from . import validate as pipd_validate
    verdict = pipd_validate.validate_bundle(
        {"PI-PKG": strict["strict"], "PD-PKG": pd, "ECP": both["dev"]})
    if verdict.get("verdict") != "PASS":
        raise LifecycleRefusal("strict bundle failed canonical validation: "
                               + canonical_json(verdict.get("findings") or []))

    record = {
        "schema": SCHEMA,
        "subject": subject,
        "goal_sha256": sha256_text(goal),
        "profile": {"name": profile_full.get("profile"), "axes": axes,
                    "vetoes": profile_full.get("vetoes")},
        "source_freeze_sha256": freeze["content_hash"],
        "stages": stages,
        "artifacts": {"source_freeze": freeze, "intent": card, "profile": pb,
                      "pi_strict": strict["strict"], "pi_sidecar": strict["sidecar"],
                      "repo_context": ctx, "pd": pd, "ecp_dev": both["dev"], "ecp_ops": both["ops"],
                      "tqaep": tqaep},
        "repo_context_check": local,
        "effect_paths": both["separation"],
        "validation": {"verdict": verdict.get("verdict"),
                       "findings": verdict.get("findings") or []},
        "native": {leg: "NOT_RUN" for leg in ON_HOST_LEGS},
        "claim_ceiling": STRICT_CEILING,
        "notes": ["no host effect was attempted; installed/loaded/invoked/consumer_ack are NOT_RUN",
                  "DEV and OPS candidates are separate records with separate permission bases",
                  "the sidecar is not raw evidence and is excluded from the strict digest"],
    }
    record["content_hash"] = sha256_text(canonical_json({k: v for k, v in record.items()
                                                         if k != "content_hash"}))
    record["subject_id"] = "W1WP05-" + record["content_hash"][:16]
    return record


def digest_of(path: str | Path) -> str:
    """Small helper for callers that want the on-disk digest of a frozen source."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
