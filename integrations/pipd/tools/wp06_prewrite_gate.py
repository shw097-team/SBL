"""Pre-write gate for one bound operation instance (WP06 / ``REPOSITORY_WRITE``).

WHAT CHANGED AFTER THE OWNER'S H-16 CORRECTION
---------------------------------------------
The first version resolved the repository identity from ``remote.origin.url`` alone and let the
caller supply the numeric id, which meant the gate could be satisfied by the object it was
supposed to check. It also treated any non-zero ``git cat-file`` as "absent", and it had no
cross-call op accounting. All four are corrected here:

  * **identity** is attested, not asserted: a live ``GET /repos/<full_name>`` (or a recorded
    attestation file naming that read) must return the numeric id the owner signed.
    ``remote.origin.url`` is corroboration only - it can never be authority on its own.
  * **protected root**: the repository must sit inside a root that the original HGK registry
    protects. Without such a binding there is no lawful write, whatever the contract says.
  * **presence is measured, not inferred**: ``git ls-tree`` decides whether a path exists at HEAD;
    a ``cat-file`` failure that is not "path absent" is an unreadable object, not an absence.
  * **ops are consumed across calls**: a nonce derived from the signed instance is claimed with an
    exclusive create, so replay is refused and ``max_ops`` means something. Zero or negative ops
    are refused. TTL is counted from the signature's own ``signed_at`` and is never restarted.
  * **TOCTOU**: head, tree and index are re-read after the decision; a change between the read and
    the verdict is refused rather than written over.

Exit codes: 0 gate passed (NOT a permit), 1 refused with a JSON code, 2 usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve()
PIPD = HERE.parents[1]
SBL_ROOT = PIPD.parents[1]
sys.path.insert(0, str(PIPD / "src"))
sys.path.insert(0, str(HERE.parent))

import operation_instance as oi  # noqa: E402

DEFAULT_REGISTRY = pathlib.Path(r"C:/ProgramData/HG-KSEOS/native-admission/registry.json")
DEFAULT_JOURNAL = pathlib.Path(os.environ.get("LOCALAPPDATA", str(pathlib.Path.home()))) / "hermes" / "wp06-gate"
TOKEN_FILE = pathlib.Path("C:/Projects/Agent_Workspace/API KEY/GITHUB-REPO_SHW097-4.txt")


# --------------------------------------------------------------------------- git plumbing
def git(root: pathlib.Path, *args: str) -> tuple[int, bytes, bytes]:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=120)
    return p.returncode, p.stdout, p.stderr


def rev(root: pathlib.Path, spec: str) -> str:
    rc, out, err = git(root, "rev-parse", spec)
    if rc != 0:
        raise oi.InstanceRefused("GIT_OBJECT_UNREADABLE",
                                 {"spec": spec, "stderr": err.decode("utf-8", "replace")[:200]})
    return out.decode().strip()


def paths_at_head(root: pathlib.Path) -> set:
    """Every path at HEAD, from ls-tree. Presence is decided here, not from an rc code."""
    rc, out, err = git(root, "ls-tree", "-r", "--name-only", "-z", "HEAD")
    if rc != 0:
        raise oi.InstanceRefused("GIT_OBJECT_UNREADABLE",
                                 {"args": "ls-tree", "stderr": err.decode("utf-8", "replace")[:200]})
    return {p for p in out.decode("utf-8", "replace").split("\0") if p}


def blob_at_head(root: pathlib.Path, rel: str, head_paths: set) -> tuple[str, str]:
    """(digest, state) with state PRESENT or ABSENT. A present-but-unreadable path is corruption."""
    if rel not in head_paths:
        return "", "ABSENT"
    rc, out, err = git(root, "cat-file", "blob", f"HEAD:{rel}")
    if rc != 0:
        raise oi.InstanceRefused("GIT_OBJECT_UNREADABLE",
                                 {"relpath": rel, "stderr": err.decode("utf-8", "replace")[:200]})
    return hashlib.sha256(out).hexdigest(), "PRESENT"


def staged_digest(root: pathlib.Path, rel: str) -> str | None:
    """Digest of the index blob when staged, else the worktree file, else None."""
    rc, out, _ = git(root, "cat-file", "blob", f":{rel}")
    if rc == 0:
        return hashlib.sha256(out).hexdigest()
    path = root / rel
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def changed_paths(root: pathlib.Path) -> list:
    """Full ``-z`` parse: a rename/copy record carries its target inline and its source in the next field."""
    rc, out, err = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if rc != 0:
        raise oi.InstanceRefused("GIT_STATUS_UNREADABLE",
                                 {"stderr": err.decode("utf-8", "replace")[:200]})
    fields = [f.decode("utf-8", "replace") for f in out.split(b"\0")]
    rows, i = [], 0
    while i < len(fields):
        rec = fields[i]
        if len(rec) < 4:
            i += 1
            continue
        xy, path = rec[:2], rec[3:]
        rows.append(path)
        if "R" in xy or "C" in xy:
            if i + 1 < len(fields) and fields[i + 1].strip():
                rows.append(fields[i + 1])
                i += 1
        i += 1
    return rows


def snapshot(root: pathlib.Path) -> dict:
    rc, out, _ = git(root, "ls-files", "-s", "-z")
    index_digest = hashlib.sha256(out).hexdigest() if rc == 0 else "UNREADABLE"
    return {"head": rev(root, "HEAD"), "tree": rev(root, "HEAD^{tree}"), "index_sha256": index_digest}


# --------------------------------------------------------------------------- identity
def attest_repo_id(full_name: str, *, attestation_file: pathlib.Path | None = None) -> dict:
    """The numeric id must come from a read of GitHub, recorded with its own digest."""
    if attestation_file is not None:
        if not attestation_file.is_file():
            raise oi.InstanceRefused("INSTANCE_REPO_ID_UNATTESTED", {"file": str(attestation_file)})
        body = attestation_file.read_bytes()
        doc = json.loads(body)
        if doc.get("full_name") != full_name or not doc.get("id"):
            raise oi.InstanceRefused("INSTANCE_REPO_ID_UNATTESTED", {"file": str(attestation_file)})
        return {"id": int(doc["id"]), "full_name": full_name, "source": doc.get("source"),
                "source_sha256": hashlib.sha256(body).hexdigest(), "fetched_at": doc.get("fetched_at")}
    if not TOKEN_FILE.is_file():
        raise oi.InstanceRefused("INSTANCE_REPO_ID_UNATTESTED", {"reason": "no token file for the read"})
    token = TOKEN_FILE.read_text(encoding="utf-8").strip()
    req = urllib.request.Request(f"https://api.github.com/repos/{full_name}")
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "hgk-wp06-gate")
    try:
        with urllib.request.urlopen(req, timeout=45) as r:
            raw = r.read()
    except urllib.error.HTTPError as exc:
        raise oi.InstanceRefused("INSTANCE_REPO_ID_UNATTESTED",
                                 {"status": exc.code, "full_name": full_name}) from None
    except Exception as exc:  # noqa: BLE001
        raise oi.InstanceRefused("INSTANCE_REPO_ID_UNATTESTED",
                                 {"error": f"{type(exc).__name__}: {exc}"}) from None
    doc = json.loads(raw)
    return {"id": int(doc["id"]), "full_name": doc["full_name"],
            "source": f"GITHUB_REST_GET /repos/{full_name}",
            "source_sha256": hashlib.sha256(raw).hexdigest(),
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}


def protected_root_binding(repo: pathlib.Path, registry_path: pathlib.Path) -> dict:
    """The repository must live inside a root the original registry protects."""
    if not registry_path.is_file():
        raise oi.InstanceRefused("INSTANCE_PROTECTED_ROOT_UNBOUND", {"registry": str(registry_path)})
    reg = json.loads(registry_path.read_text(encoding="utf-8"))
    root = reg.get("root")
    if not root:
        raise oi.InstanceRefused("INSTANCE_PROTECTED_ROOT_UNBOUND",
                                 {"registry": str(registry_path), "reason": "registry has no root"})
    protected = pathlib.Path(root)
    try:
        inside = repo.resolve().is_relative_to(protected.resolve())
    except Exception:  # noqa: BLE001 - a root that cannot be resolved is not a binding
        inside = False
    if not inside:
        raise oi.InstanceRefused("INSTANCE_PROTECTED_ROOT_UNBOUND",
                                 {"repo": str(repo), "protected_root": root,
                                  "registry_mission": reg.get("mission_id"),
                                  "registry_revision": (reg.get("revision") or {}).get("number")})
    return {"protected_root": root,
            "root_identity": (reg.get("scope") or {}).get("root_identity"),
            "mission_id": reg.get("mission_id"),
            "registry_revision": (reg.get("revision") or {}).get("number"),
            "registry_path": str(registry_path)}


# --------------------------------------------------------------------------- ops journal
def consume_op(journal_dir: pathlib.Path, nonce: str, ops: int) -> dict:
    """Claim the instance's nonce exactly once. The exclusive create is the whole concurrency story."""
    if int(ops) <= 0:
        raise oi.InstanceRefused("INSTANCE_OPS_INVALID", {"requested": ops})
    journal_dir.mkdir(parents=True, exist_ok=True)
    target = journal_dir / f"{nonce}.json"
    try:
        fd = os.open(str(target), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        prior = json.loads(target.read_text(encoding="utf-8"))
        raise oi.InstanceRefused("INSTANCE_REPLAY_REFUSED",
                                 {"nonce": nonce, "first_used_at": prior.get("at"),
                                  "ops": prior.get("ops")}) from None
    payload = {"nonce": nonce, "ops": int(ops), "at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    try:
        os.write(fd, json.dumps(payload, ensure_ascii=False).encode())
    finally:
        os.close(fd)
    return payload


def nonce_for(instance, contract_sha: str, signed_at: str) -> str:
    body = json.dumps({"instance": instance["instance_id"], "contract": contract_sha,
                       "head": instance["repo"]["head_at_bind"], "signed_at": signed_at,
                       "writeset": [e["relpath"] for e in instance["write_set"]]},
                      sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(body).hexdigest()


# --------------------------------------------------------------------------- ttl
def ttl_remaining(instance, signed_at: str, now: datetime | None = None) -> float | None:
    """Seconds left, counted from the signature. Never restarted, never extended at call time."""
    ttl = instance.get("ttl_seconds")
    if not ttl or not signed_at:
        return None
    try:
        stamp = datetime.fromisoformat(signed_at)
    except ValueError:
        return None
    if stamp.tzinfo is None:
        return None
    now = now or datetime.now(timezone.utc)
    return float(ttl) - (now - stamp.astimezone(timezone.utc)).total_seconds()


# --------------------------------------------------------------------------- the gate
def run(repo: pathlib.Path, instance_id: str, *, ops: int = 1,
        contract_path: pathlib.Path | None = None,
        registry_path: pathlib.Path = DEFAULT_REGISTRY,
        journal_dir: pathlib.Path = DEFAULT_JOURNAL,
        attestation_file: pathlib.Path | None = None,
        consume: bool = True) -> dict:
    from pipd_ls_sp import operation_registry as oreg

    contract_path = contract_path or (PIPD / "contracts" / "operation-registry.pre-v2-r3.json")
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    contract_sha = hashlib.sha256(contract_bytes).hexdigest()
    instance = oi.find_instance(contract, instance_id)

    body, signed_sha, rat = oreg.load_trusted(str(SBL_ROOT))
    if signed_sha != contract_sha:
        raise oi.InstanceRefused("INSTANCE_CONTRACT_SHA_MISMATCH",
                                 {"sbl_tree": signed_sha, "in_hand": contract_sha})
    sidecar = json.loads((PIPD / "contracts" / "operation-registry.pre-v2-r3.owner.sig.json")
                         .read_text(encoding="utf-8"))
    signed_at = sidecar.get("signed_at") or ""
    signed_scope = list(json.loads(sidecar["payload_json"]).get("scope") or [])

    # identity: an attested read, corroborated by the repository's own remote
    attested = attest_repo_id(instance["repo"]["full_name"], attestation_file=attestation_file)
    remote = git(repo, "config", "--get", "remote.origin.url")[1].decode("utf-8", "replace").strip()
    remote_name = oi.full_name_from_remote_url(remote)
    if remote_name != attested["full_name"]:
        raise oi.InstanceRefused("INSTANCE_REPO_IDENTITY_MISMATCH",
                                 {"remote": remote_name, "attested": attested["full_name"]})

    # protected root: no lawful write outside a root the original registry protects
    protected = protected_root_binding(repo, registry_path)

    # repo state, measured
    before = snapshot(repo)
    head_paths = paths_at_head(repo)
    relpaths = [e["relpath"] for e in instance["write_set"]]
    preimages, observed = {}, {}
    for rel in relpaths:
        digest, state = blob_at_head(repo, rel, head_paths)
        preimages[rel] = "ABSENT" if state == "ABSENT" else digest
        got = staged_digest(repo, rel)
        if got:
            observed[rel] = got
    changed = changed_paths(repo)

    nonce = nonce_for(instance, contract_sha, signed_at)
    claim = consume_op(journal_dir, nonce, ops) if consume else {"nonce": nonce, "ops": int(ops),
                                                                 "at": "(not consumed)"}

    record = oi.evaluate_write(
        contract, instance_id,
        signed_contract_sha256=signed_sha, contract_sha256=contract_sha,
        repo_state={"head": before["head"], "tree": before["tree"], "write_scope": relpaths,
                    "preimages": preimages, "repo_id": attested["id"],
                    "full_name": attested["full_name"]},
        observed=observed, changed_paths=changed, signed_scope=signed_scope,
        ttl_remaining_s=ttl_remaining(instance, signed_at), ops_requested=ops,
    )

    # TOCTOU: the tree must be the one the decision was made against
    after = snapshot(repo)
    if after != before:
        raise oi.InstanceRefused("INSTANCE_TOCTOU_DRIFT", {"before": before, "after": after})

    record["identity_attestation"] = attested
    record["protected_root"] = protected
    record["op_claim"] = claim
    record["observed_postimages"] = observed
    record["preimages_at_head"] = preimages
    record["tree_state"] = before
    record["signature"] = {"window_id": rat.get("window_id"), "signed_at": signed_at,
                           "owner_fingerprint": rat.get("owner_fingerprint"),
                           "grant_state": rat.get("grant_state"),
                           "claim_ceiling": rat.get("claim_ceiling")}
    return record


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--instance", default="OP-WP06-FHSVNEXT-ADD-01")
    ap.add_argument("--ops", type=int, default=1)
    ap.add_argument("--contract", default=None)
    ap.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    ap.add_argument("--journal-dir", default=str(DEFAULT_JOURNAL))
    ap.add_argument("--attestation-file", default=None)
    ap.add_argument("--no-consume", action="store_true",
                    help="dry run: evaluate without claiming the nonce")
    a = ap.parse_args()
    try:
        record = run(pathlib.Path(a.repo).resolve(), a.instance, ops=a.ops,
                     contract_path=pathlib.Path(a.contract) if a.contract else None,
                     registry_path=pathlib.Path(a.registry),
                     journal_dir=pathlib.Path(a.journal_dir),
                     attestation_file=pathlib.Path(a.attestation_file) if a.attestation_file else None,
                     consume=not a.no_consume)
    except oi.InstanceRefused as exc:
        print(json.dumps({"gate": "REFUSED", "code": exc.code, "detail": exc.detail,
                          "claim_ceiling": oi.CLAIM_CEILING}, ensure_ascii=False, indent=1))
        return 1
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"gate": "REFUSED", "code": "GATE_ERROR",
                          "detail": f"{type(exc).__name__}: {exc}"}, ensure_ascii=False, indent=1))
        return 1
    print(json.dumps(record, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
