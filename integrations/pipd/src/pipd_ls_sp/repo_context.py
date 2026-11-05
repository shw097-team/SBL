"""Repository/host probes for PD late binding (R-AUD-009 / CAP_PD_LATE_BINDING).

The RepoContext is DERIVED from the repository and host at bind time (git probes when the root is
a checkout, filesystem probes otherwise - degraded and DISCLOSED, never silently). Caller-supplied
head / tracked_files / currentness values are unverified CLAIMS: they are recorded as claims and
never trusted; a freshness claim (currentness / currentness_epoch) is only accepted when it binds
to host truth at bind time, otherwise it is REFUSED (stale or spoofed). Missing RepoContext fails
closed: no PD and therefore no PREDEV_READY readiness is ever emitted without one.
"""
from __future__ import annotations

import locale
import os
import re
import subprocess
from pathlib import Path
from typing import Any

from .errors import EffectUnknown, RepoContextMissing, StaleProvider
from .util import canonical_json, sha256_bytes, sha256_file, sha256_text

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
    out = _git_exec(root, *args)
    return out if out is not None and out.returncode == 0 else None


def _git_exec(root: Path, *args: str) -> "subprocess.CompletedProcess[str] | None":
    """Run git and return the completed process whatever its exit code (None if it never ran).

    Callers that must DISCLOSE *why* a probe failed need stderr, which `_git` deliberately hides.
    """
    try:
        return subprocess.run(["git", "-C", str(root), *args],
                              capture_output=True, text=True, timeout=30)
    except Exception:
        return None


def _norm(rel: str) -> str:
    return rel.replace("\\", "/")


def _in_scope(rel: str, scope: "str | list[str] | tuple[str, ...]") -> bool:
    """True when a repo-relative path falls inside any of the scope patterns."""
    entry = _norm(rel)
    rules = [scope] if isinstance(scope, str) else list(scope or [])
    for rule in rules:
        rule = _norm(str(rule or "").strip())
        if not rule:
            continue
        if rule == entry:
            return True
        if rule.endswith("/**"):
            pre = rule[:-3]
            if pre and (entry == pre or entry.startswith(pre + "/")):
                return True
        elif rule.endswith("*") and entry.startswith(rule[:-1]):
            return True
    return False


def _manifest_rows(files: list[str], root: Path) -> list[list[Any]]:
    rows: list[list[Any]] = []
    for rel in files:
        p = root / rel
        try:
            rows.append([rel, p.stat().st_size, sha256_file(p)])
        except OSError:
            rows.append([rel, -1, "MISSING"])
    return rows


def _resolve_git_root(root: Path, errors: list[str]) -> "str | None":
    """Resolve the REAL toplevel of the checkout containing `root` (never raise)."""
    out = _git_exec(root, "rev-parse", "--show-toplevel")
    if out is None:
        errors.append("git_root: git executable unavailable or timed out")
        return None
    if out.returncode != 0 or not out.stdout.strip():
        reason = (out.stderr or out.stdout or "").strip().splitlines()
        errors.append("git_root: git rev-parse --show-toplevel failed"
                      + (f": {reason[0]}" if reason else ""))
        return None
    return str(Path(out.stdout.strip()))


_ACL_PRINCIPAL = re.compile(r"^\s*(.+?):\(")


def _acl_principals(text: str, target: Path) -> set[str]:
    """Principal names from icacls output; the leading file path on line 1 is stripped first.

    A principal may contain spaces ("NT AUTHORITY\\SYSTEM"), so this cannot be a whitespace-split.
    """
    prefixes = [str(target), str(target).replace("\\", "/"), target.name]
    found: set[str] = set()
    for line in text.splitlines():
        body = line
        for prefix in prefixes:
            if body.lower().startswith(prefix.lower()):
                body = body[len(prefix):]
                break
        match = _ACL_PRINCIPAL.match(body)
        if match:
            principal = match.group(1).strip()
            if principal and not principal.lower().startswith("successfully"):
                found.add(principal)
    return found


def _decode_host_output(raw: bytes) -> str:
    """icacls writes in the host OEM/ANSI codepage, not UTF-8; decode without ever raising."""
    for encoding in ("utf-8", locale.getpreferredencoding(False) or "utf-8", "mbcs"):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, LookupError):
            continue
    return raw.decode("utf-8", errors="replace")


def _probe_acl(files: list[str], root: Path,
               writable_scope: "str | list[str] | tuple[str, ...] | None") -> dict[str, Any]:
    """Observe filesystem ACLs for every file inside writable_scope. Never overstate.

    `state` is OBSERVED only when icacls succeeded for EVERY in-scope file on Windows; anything
    else (no in-scope file, non-Windows host, missing tool, any icacls failure) is UNVERIFIED
    with a recorded reason. An UNVERIFIED block is never promoted to VERIFIED.
    """
    targets = [rel for rel in files if _in_scope(rel, writable_scope or [])]
    block: dict[str, Any] = {"state": "UNVERIFIED", "acl_state": "UNVERIFIED",
                             "principals": [], "raw_sha256": None,
                             "platform": os.name, "tool": "icacls",
                             "files": targets, "reason": None,
                             "observed_count": 0, "unverified_count": len(targets)}
    if not targets:
        block["reason"] = "no file inside write_scope to observe (ACL not probed)"
        return block
    if os.name != "nt":
        block["reason"] = f"icacls is Windows-only; ACL not observable on platform {os.name!r}"
        return block
    principals: set[str] = set()
    chunks: list[str] = []
    failures: list[str] = []
    for rel in targets:
        try:
            cp = subprocess.run(["icacls", str(root / rel)],
                                capture_output=True, timeout=30)
        except Exception as exc:  # tool missing, timeout, permission
            failures.append(f"{rel}: {exc.__class__.__name__}: {exc}")
            continue
        stdout = _decode_host_output(cp.stdout or b"")
        stderr = _decode_host_output(cp.stderr or b"")
        if cp.returncode != 0:
            detail = (stderr or stdout).strip().splitlines()
            failures.append(f"{rel}: icacls exit {cp.returncode}"
                            + (f": {detail[0]}" if detail else ""))
            continue
        chunks.append(f"{rel}\n{stdout}")
        principals.update(_acl_principals(stdout, root / rel))
    block["observed_count"] = len(targets) - len(failures)
    block["unverified_count"] = len(failures)
    if failures:
        block["reason"] = ("ACL not fully observed: " + "; ".join(failures[:5])
                           + ("" if len(failures) <= 5 else f" (+{len(failures) - 5} more)"))
        return block
    block.update(state="OBSERVED", acl_state="OBSERVED",
                 principals=sorted(principals),
                 raw_sha256=sha256_text("\n".join(chunks)), reason=None)
    return block


def _capture_preimage(root: Path, git_root: "str | None", rows: list[list[Any]],
                      preimage_dir: "Path | str | None",
                      writable_scope: "str | list[str] | tuple[str, ...] | None",
                      errors: list[str]) -> dict[str, Any]:
    """Copy pre-image bytes OUTSIDE the repository; refuse a preimage root inside it."""
    out: dict[str, Any] = {"captured": False, "preimage_dir": None,
                           "preimage_refs": [], "refusal": None}
    if preimage_dir is None or not str(preimage_dir).strip():
        out["refusal"] = ("capture_preimage=True requires an explicit caller-supplied "
                          "preimage_dir outside writable_scope")
        errors.append("PREIMAGE_SCOPE_DENY: " + str(out["refusal"]))
        return out
    given = Path(preimage_dir)
    if not given.is_absolute():
        out["refusal"] = f"preimage_dir must be an absolute path, got {str(preimage_dir)!r}"
        errors.append("PREIMAGE_SCOPE_DENY: " + str(out["refusal"]))
        return out
    try:
        target = given.resolve()
    except OSError as exc:
        out["refusal"] = f"preimage_dir cannot be resolved: {exc}"
        errors.append("PREIMAGE_SCOPE_DENY: " + str(out["refusal"]))
        return out
    repo_roots = [root.resolve()]
    if git_root:
        repo_roots.append(Path(git_root).resolve())
    for repo_root in repo_roots:
        if target == repo_root or repo_root in target.parents:
            out["refusal"] = (f"preimage_dir {target} is inside the probed repository "
                              f"{repo_root}; it must be a temp root outside writable_scope")
            errors.append("PREIMAGE_SCOPE_DENY: " + str(out["refusal"]))
            return out
        for rule in ([writable_scope] if isinstance(writable_scope, str)
                     else list(writable_scope or [])):
            rule_path = Path(str(rule)).expanduser()
            if rule_path.is_absolute() and (target == rule_path.resolve()
                                            or rule_path.resolve() in target.parents):
                out["refusal"] = f"preimage_dir {target} is inside writable_scope {rule}"
                errors.append("PREIMAGE_SCOPE_DENY: " + str(out["refusal"]))
                return out
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        out["refusal"] = f"preimage_dir cannot be created: {exc}"
        errors.append(f"PREIMAGE_CAPTURE_FAILED: {out['refusal']}")
        return out
    refs: list[dict[str, Any]] = []
    failures: list[str] = []
    for rel, size, digest in rows:
        if digest == "MISSING":
            failures.append(f"{rel}: pre-image missing on disk")
            continue
        src = root / rel
        dst = target / rel
        try:
            data = src.read_bytes()
            got = sha256_bytes(data)
            if got != digest:
                failures.append(f"{rel}: bytes changed between manifest and capture")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
        except OSError as exc:
            failures.append(f"{rel}: {exc}")
            continue
        refs.append({"rel": rel, "path": str(dst), "sha256": got, "bytes": len(data)})
    if failures:
        errors.append("PREIMAGE_CAPTURE_FAILED: " + "; ".join(failures[:5])
                      + ("" if len(failures) <= 5 else f" (+{len(failures) - 5} more)"))
    out.update(captured=bool(refs) and not failures, preimage_dir=str(target),
               preimage_refs=refs)
    return out


def _capabilities(git_root_resolved: bool, index_ok: bool, untracked_ok: bool,
                  acl_state: str, capture_state: str) -> dict[str, str]:
    """Machine-readable presence flags so no upstream has to GUESS what was actually observed."""
    return {
        "git_root": "PRESENT" if git_root_resolved else "ABSENT",
        "index": "PRESENT" if index_ok else "ABSENT",
        "index_digest": "PRESENT" if index_ok else "ABSENT",
        "staged_changes": "PRESENT" if index_ok else "ABSENT",
        "untracked": "PRESENT" if untracked_ok else "ABSENT",
        "acl": acl_state,
        "preimage_bytes": "OPTIONAL_CAPTURE",
        "preimage_capture": capture_state,
    }


def probe_repository(root: "Path | str", *, write_scope: "str | list[str] | None" = "src/**",
                     capture_preimage: bool = False,
                     preimage_dir: "Path | str | None" = None) -> dict[str, Any]:
    """Derive head/branch/dirty/tracked_files/manifest from the host itself.

    git probes when the root is a checkout; otherwise filesystem probes, degraded and disclosed
    (probe == "filesystem", degraded == True). A root that cannot be probed at all is a missing
    RepoContext (fail closed). W2 CH-15 adds live git_root / index / untracked / acl /
    per_file_preimage evidence, each DISCLOSED in `capabilities` and in `errors` on failure.
    """
    root = Path(root)
    if not str(root).strip() or not root.is_dir():
        raise RepoContextMissing(f"RepoContext root missing: {root}")
    root_input = str(root)
    errors: list[str] = []
    head = branch = None
    dirty_tracked: list[str] = []
    untracked: list[str] = []
    staged: list[str] = []
    index_digest = None
    tracked: list[str] | None = None
    probe = "filesystem"
    degraded_reason = "not a git checkout: degraded to filesystem probes (disclosed)"
    git_root = _resolve_git_root(root, errors)
    ls = _git(root, "ls-files")
    index_ok = False
    untracked_ok = False
    if ls is not None:
        probe = "git"
        degraded_reason = None
        tracked = [_norm(l) for l in ls.stdout.splitlines() if l.strip()]
        head_out = _git(root, "rev-parse", "HEAD")
        head = head_out.stdout.strip() if head_out else None
        br = _git(root, "rev-parse", "--abbrev-ref", "HEAD")
        branch = br.stdout.strip() if br else None
        st = _git(root, "status", "--porcelain", "-uno")
        dirty_tracked = [l.rstrip() for l in st.stdout.splitlines() if l.strip()] if st else []
        idx = _git_exec(root, "ls-files", "-s")
        if idx is not None and idx.returncode == 0:
            index_digest = sha256_text(idx.stdout)
            index_ok = True
        else:
            detail = ((idx.stderr or "").strip().splitlines() if idx is not None else [])
            errors.append("index: `git ls-files -s` failed; index_digest unavailable"
                          + (f": {detail[0]}" if detail else ""))
        stg = _git_exec(root, "diff", "--cached", "--name-only")
        if stg is not None and stg.returncode == 0:
            staged = [_norm(l) for l in stg.stdout.splitlines() if l.strip()]
        else:
            errors.append("staged_changes: `git diff --cached --name-only` failed; "
                          "staged set unavailable")
        st_all = _git_exec(root, "status", "--porcelain", "--untracked-files=normal")
        if st_all is not None and st_all.returncode == 0:
            untracked = [_norm(l[3:].strip().strip('"'))
                         for l in st_all.stdout.splitlines() if l.startswith("?? ")]
            untracked_ok = True
        else:
            errors.append("untracked: `git status --porcelain --untracked-files=normal` failed; "
                          "untracked set unavailable")
    if tracked is None:
        try:
            tracked = [str(p.relative_to(root)).replace("\\", "/")
                       for p in sorted(root.rglob("*"))
                       if p.is_file() and ".git" not in p.parts and "__pycache__" not in p.parts]
        except OSError as exc:
            raise RepoContextMissing(f"repository probes failed for {root}: {exc}") from exc
    rows = _manifest_rows(tracked, root)
    manifest = sha256_text(canonical_json(rows))
    acl = _probe_acl(tracked, root, write_scope)
    preimage: dict[str, Any] = {"manifest": [{"rel": r[0], "size": r[1], "sha256": r[2]}
                                             for r in rows],
                                "manifest_sha256": manifest,
                                "captured": False, "preimage_dir": None,
                                "preimage_refs": [], "refusal": None}
    if capture_preimage:
        preimage.update(_capture_preimage(root, git_root, rows, preimage_dir,
                                          write_scope, errors))
        capture_state = ("CAPTURED" if preimage["captured"]
                         else "SCOPE_DENY" if preimage.get("refusal") else "FAILED")
    else:
        capture_state = "NOT_REQUESTED"
    state = {"root": str(root), "root_input": root_input,
             "probe": probe,
             "degraded": bool(degraded_reason), "degraded_reason": degraded_reason,
             "git_root": git_root, "git_root_resolved": bool(git_root),
             "head": head, "branch": branch,
             "dirty": bool(dirty_tracked), "dirty_tracked": sorted(dirty_tracked),
             "index_digest": index_digest, "staged_changes": sorted(staged),
             "staged_count": len(staged),
             "untracked": sorted(untracked), "untracked_count": len(untracked),
             "tracked_files": len(tracked), "manifest_sha256": manifest,
             "per_file_preimage": preimage,
             "acl": acl, "acl_state": acl["state"],
             "errors": errors,
             "capabilities": _capabilities(bool(git_root), index_ok, untracked_ok,
                                           acl["state"], capture_state)}
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
                        capture_preimage: bool = False,
                        preimage_dir: "Path | str | None" = None) -> dict[str, Any]:
    """Build a derived RepoContext: host truth + readiness, with the writable-scope check.

    `capture_preimage` defaults to False so existing callers keep the exact prior behaviour; when
    True a caller-supplied `preimage_dir` outside writable_scope receives the pre-image bytes.
    """
    state = probe_repository(root, write_scope=writable_scope,
                             capture_preimage=capture_preimage, preimage_dir=preimage_dir)
    return {"root": state["root"], "root_input": state["root_input"],
            "probe": state["probe"],
            "degraded": state["degraded"], "degraded_reason": state["degraded_reason"],
            "git_root": state["git_root"], "git_root_resolved": state["git_root_resolved"],
            "head": state["head"], "branch": state["branch"],
            "dirty": state["dirty"], "dirty_tracked": state["dirty_tracked"],
            "index_digest": state["index_digest"], "staged_changes": state["staged_changes"],
            "staged_count": state["staged_count"],
            "untracked": state["untracked"], "untracked_count": state["untracked_count"],
            "tracked_files": state["tracked_files"], "manifest_sha256": state["manifest_sha256"],
            "per_file_preimage": state["per_file_preimage"],
            "acl": state["acl"], "acl_state": state["acl_state"],
            "errors": state["errors"], "capabilities": state["capabilities"],
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
