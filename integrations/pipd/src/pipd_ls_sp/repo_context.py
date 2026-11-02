"""Repository/host probes for PD late binding (R-AUD-009 / CAP_PD_LATE_BINDING).

The RepoContext is DERIVED from the repository and host at bind time (git probes when the root is
a checkout, filesystem probes otherwise - degraded and DISCLOSED, never silently). Caller-supplied
head / tracked_files / currentness values are unverified CLAIMS: they are recorded as claims and
never trusted; a freshness claim (currentness / currentness_epoch) is only accepted when it binds
to host truth at bind time, otherwise it is REFUSED (stale or spoofed). Missing RepoContext fails
closed: no PD and therefore no PREDEV_READY readiness is ever emitted without one.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from .errors import EffectUnknown, RepoContextMissing, StaleProvider
from .util import canonical_json, sha256_file, sha256_text

# Writable scope the construction binding admits by default (R2 repair-scope hardening): a
# requested writable scope is reported and enforced as a SUBSET check, never echoed as free text.
ADMITTED_WRITABLE_SCOPE = ("src/**", "tests/**", "tools/**", "fixtures/**")

# Caller-supplied values inside a RepoContext dict that are claims until host-verified.
CLAIM_KEYS = ("head", "branch", "dirty", "tracked_files", "manifest", "manifest_sha256",
              "currentness", "currentness_epoch", "writable_scope")
FRESHNESS_KEYS = ("currentness", "currentness_epoch")
STATE_KEYS = ("head", "branch", "dirty", "tracked_files", "manifest_sha256")


def tracked_file_count(root: Path) -> int:
    """Count VCS-tracked files, or files in the tree when it is not a checkout.

    `git ls-files` when the subject IS a git checkout; otherwise the count of files in the tree
    EXCLUDING `.git/` and `__pycache__/`. Never count version-control internals as project files.
    """
    try:
        out = subprocess.run(["git", "-C", str(root), "ls-files"],
                             capture_output=True, text=True, timeout=30)
        if out.returncode == 0:
            return len([l for l in out.stdout.splitlines() if l.strip()])
    except Exception:
        pass
    return sum(1 for p in root.rglob("*") if p.is_file()
               and ".git" not in p.parts and "__pycache__" not in p.parts)


def _git(root: Path, *args: str) -> "subprocess.CompletedProcess[str] | None":
    try:
        out = subprocess.run(["git", "-C", str(root), *args],
                             capture_output=True, text=True, timeout=30)
    except Exception:
        return None
    return out if out.returncode == 0 else None


def _manifest(files: list[str], root: Path) -> str:
    rows = []
    for rel in files:
        p = root / rel
        try:
            rows.append([rel, p.stat().st_size, sha256_file(p)])
        except OSError:
            rows.append([rel, -1, "MISSING"])
    return sha256_text(canonical_json(rows))


def probe_repository(root: "Path | str") -> dict[str, Any]:
    """Derive head/branch/dirty/tracked_files/manifest from the host itself.

    git probes when the root is a checkout; otherwise filesystem probes, degraded and disclosed
    (probe == "filesystem", degraded == True). A root that cannot be probed at all is a missing
    RepoContext (fail closed).
    """
    root = Path(root)
    if not str(root).strip() or not root.is_dir():
        raise RepoContextMissing(f"RepoContext root missing: {root}")
    head = branch = None
    dirty_tracked: list[str] = []
    tracked: list[str] | None = None
    probe = "filesystem"
    degraded_reason = "not a git checkout: degraded to filesystem probes (disclosed)"
    ls = _git(root, "ls-files")
    if ls is not None:
        probe = "git"
        degraded_reason = None
        tracked = [l.replace("\\", "/") for l in ls.stdout.splitlines() if l.strip()]
        head_out = _git(root, "rev-parse", "HEAD")
        head = head_out.stdout.strip() if head_out else None
        br = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
        branch = br.stdout.strip() if br else None
        st = _git(root, "status", "--porcelain", "-uno")
        dirty_tracked = [l.rstrip() for l in st.stdout.splitlines() if l.strip()] if st else []
    if tracked is None:
        try:
            tracked = [str(p.relative_to(root)).replace("\\", "/")
                       for p in sorted(root.rglob("*"))
                       if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts]
        except OSError as exc:
            raise RepoContextMissing(f"repository probes failed for {root}: {exc}") from exc
    manifest = _manifest(tracked, root)
    state = {"root": str(root), "probe": probe,
             "degraded": bool(degraded_reason), "degraded_reason": degraded_reason,
             "head": head, "branch": branch,
             "dirty": bool(dirty_tracked), "dirty_tracked": sorted(dirty_tracked),
             "tracked_files": len(tracked), "manifest_sha256": manifest}
    state["currentness_epoch"] = currentness_epoch(state)
    return state


def currentness_epoch(state: dict[str, Any]) -> str:
    """Epoch fingerprint of the repository state the snapshot was captured against."""
    return sha256_text(canonical_json({
        "head": state.get("head"), "branch": state.get("branch"),
        "dirty_tracked": state.get("dirty_tracked"),
        "tracked_files": state.get("tracked_files"),
        "manifest_sha256": state.get("manifest_sha256"),
    }))


def writable_scope_subset_check(requested: "str | list[str]",
                                authorized: "tuple[str, ...] | list[str] | None" = None,
                                ) -> dict[str, Any]:
    """Report the requested writable scope as a SUBSET check against the admitted scope."""
    auth = tuple(authorized if authorized is not None else ADMITTED_WRITABLE_SCOPE)
    req = [requested] if isinstance(requested, str) else list(requested or [])
    findings = []

    def _covered(entry: str, rule: str) -> bool:
        if entry == rule:
            return True
        if rule.endswith("/**"):
            pre = rule[:-3]
            return bool(pre) and (entry == pre or entry.startswith(pre + "/"))
        return False

    for entry in req:
        clean = (entry or "").strip().replace("\\", "/")
        bad = (not clean or clean in ("*", "**", "/") or ".." in clean.split("/")
               or clean.startswith("/") or (len(clean) > 1 and clean[1] == ":"))
        if bad:
            findings.append(f"escapes the authorised root: {entry!r}")
            continue
        if not any(_covered(clean, rule) for rule in auth):
            findings.append(f"not a subset of the admitted scope: {entry!r}")
    subset = not findings and bool(req)
    if not req:
        findings.append("no writable scope requested")
    return {"requested": req, "authorized": list(auth), "subset": subset,
            "verdict": "PASS" if subset else "FAIL", "findings": findings}


def derive_repo_context(root: "Path | str", *, writable_scope: str = "src/**",
                        authorized_scope: "tuple[str, ...] | list[str] | None" = None,
                        ) -> dict[str, Any]:
    """Build a derived RepoContext: host truth + readiness, with the writable-scope check."""
    state = probe_repository(root)
    return {"root": state["root"], "probe": state["probe"],
            "degraded": state["degraded"], "degraded_reason": state["degraded_reason"],
            "head": state["head"], "branch": state["branch"],
            "dirty": state["dirty"], "dirty_tracked": state["dirty_tracked"],
            "tracked_files": state["tracked_files"], "manifest_sha256": state["manifest_sha256"],
            "currentness": "FRESH", "currentness_epoch": state["currentness_epoch"],
            "readiness": "PREDEV_READY",
            "writable_scope": writable_scope,
            "writable_scope_check": writable_scope_subset_check(writable_scope, authorized_scope)}


def claims_of(repo_context: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Split caller values into (all claims, freshness-corroborating evidence claims).

    Top-level claim keys are the caller's asserted context: when the dict also asserts freshness,
    those state keys are offered as corroboration and are checked against the host. Values under
    the explicit `claims` key are caller-labelled unverified claims: recorded, never corroborating.
    """
    top = {k: repo_context[k] for k in CLAIM_KEYS if k in repo_context}
    explicit = {k: v for k, v in (repo_context.get("claims") or {}).items()
                if isinstance(k, str) and k in CLAIM_KEYS}
    evidence = {k: v for k, v in top.items() if k in STATE_KEYS}
    merged = dict(top)
    merged.update(explicit)
    return merged, evidence


def verify_freshness_claims(claims: dict[str, Any], derived: dict[str, Any],
                            evidence: dict[str, Any] | None = None) -> dict[str, bool]:
    """Verify caller freshness claims against host truth; refuse stale or spoofed claims.

    A freshness claim (currentness / currentness_epoch) is accepted ONLY when it carries a
    currentness_epoch that matches the host-derived epoch at bind time, its state evidence does not
    contradict the host, and its currentness value matches the host-derived value. A bare
    `currentness: FRESH` assertion with nothing bindable is unverifiable and REFUSED - that
    assertion is exactly the R-AUD-009 defect vector ("a caller asserting FRESH was accepted").
    Returns the claim keys that were actually host-verified.
    """
    verified: dict[str, bool] = {}
    if not any(k in claims for k in FRESHNESS_KEYS):
        return verified  # no freshness claim: plain claims are recorded, never trusted
    epoch_claim = claims.get("currentness_epoch")
    if not isinstance(epoch_claim, str) or not epoch_claim.strip():
        raise StaleProvider("unverifiable freshness claim: currentness asserted without a "
                            "currentness_epoch bound to host state")
    if epoch_claim != derived["currentness_epoch"]:
        raise StaleProvider("stale currentness claim: claimed epoch "
                            f"{epoch_claim[:16]}... != host-derived "
                            f"{derived['currentness_epoch'][:16]}...")
    verified["currentness_epoch"] = True
    for key, value in (evidence or {}).items():
        if value != derived.get(key):
            raise StaleProvider(f"spoofed freshness claim: {key}={value!r} "
                                f"contradicts host truth {derived.get(key)!r}")
        verified[key] = True
    currentness = claims.get("currentness")
    if currentness is not None:
        if currentness != derived.get("currentness"):
            raise StaleProvider(f"stale currentness claim: {currentness!r} contradicts "
                                f"host-derived {derived.get('currentness')!r}")
        verified["currentness"] = True
    return verified


def resolve_writable_scope(requested: str, *,
                           authorized: "tuple[str, ...] | list[str] | None" = None) -> dict[str, Any]:
    """Report AND enforce the writable scope as a subset check (fail closed on escapes)."""
    check = writable_scope_subset_check(requested, authorized)
    if not check["subset"]:
        raise EffectUnknown("writable scope is not a subset of the admitted scope: "
                            + "; ".join(check["findings"]))
    return check
