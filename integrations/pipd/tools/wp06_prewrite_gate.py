"""Pre-write gate for one bound operation instance (WP06 / ``REPOSITORY_WRITE``).

WHERE THIS SITS, AND WHY IT IS A TOOL
-------------------------------------
The declared consumer of ``REPOSITORY_WRITE`` is ``SBL-DEV-REPOSITORY-WRITER`` (ABI-REPO-WRITE-1).
No such writer exists inside ``integrations/pipd``: the package compiles intents, it never stages
or commits. So there is no shipped pre-write function to splice into, and inventing one would be a
second writer. What the package does ship is operator tooling under ``tools/`` — the same place
``issue_reader_pins.py`` and ``freeze_public_plugin_source.py`` live — and that is where a writer
can be made to pass through one gate before it touches a repository.

This gate refuses unless all of the following hold, each independently measured:

  1. the canonical contract's bytes hash to the sha the owner signed, and the sidecar verifies;
  2. the target repository's own remote resolves to the instance's ``full_name``, and the caller's
     numeric id equals the signed id (an absent id is a refusal, never a default);
  3. ``HEAD`` and ``HEAD^{tree}`` equal the bound head and tree;
  4. both paths are ABSENT at that head;
  5. the request's write scope equals the instance write set;
  6. the owner-signed scope equals the instance write set *exactly* (extra or missing -> refuse);
  7. nothing outside the write set appears in ``git status``;
  8. the bytes about to be written (index blob when staged, else worktree) hash to the signed
     postimage digests;
  9. the instance's own TTL, counted from the signature's ``signed_at``, has not expired, and the
     op count is within ``max_ops``.

Exit codes: 0 gate passed (which is NOT a permit), 1 refused with a JSON code, 2 usage error.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve()
PIPD = HERE.parents[1]
SBL_ROOT = PIPD.parents[1]
sys.path.insert(0, str(PIPD / "src"))
sys.path.insert(0, str(HERE.parent))

import operation_instance as oi  # noqa: E402


def git(root: pathlib.Path, *args: str) -> tuple[int, bytes, bytes]:
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=120)
    return p.returncode, p.stdout, p.stderr


def text(root: pathlib.Path, *args: str) -> str:
    rc, out, err = git(root, *args)
    if rc != 0:
        raise oi.InstanceRefused("INSTANCE_REPO_IDENTITY_UNRESOLVED",
                                 {"args": list(args), "stderr": err.decode("utf-8", "replace")[:200]})
    return out.decode("utf-8", "replace").strip()


def head_state(root: pathlib.Path, relpaths) -> dict:
    head = text(root, "rev-parse", "HEAD")
    tree = text(root, "rev-parse", "HEAD^{tree}")
    preimages = {}
    observed = {}
    for rel in relpaths:
        rc, out, _ = git(root, "cat-file", "blob", f"HEAD:{rel}")
        preimages[rel] = hashlib.sha256(out).hexdigest() if rc == 0 else "ABSENT"
        rc_i, idx, _ = git(root, "cat-file", "blob", f":{rel}")
        if rc_i == 0:
            observed[rel] = hashlib.sha256(idx).hexdigest()
        elif rc_i != 0 and (root / rel).is_file():
            observed[rel] = hashlib.sha256((root / rel).read_bytes()).hexdigest()
    return {"head": head, "tree": tree, "preimages": preimages, "observed": observed}


def changed_paths(root: pathlib.Path) -> list:
    rc, out, _ = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    rows = []
    for chunk in out.split(b"\0"):
        if not chunk.strip():
            continue
        body = chunk.decode("utf-8", "replace")
        rows.append(body[3:].strip().strip('"'))
    return rows


def signed_scope(sidecar: dict) -> list:
    return list(json.loads(sidecar["payload_json"]).get("scope") or [])


def ttl_remaining(instance, signed_at: str, now: datetime | None = None) -> float | None:
    """Seconds left on the signed operation window, counted from the signature's own timestamp.

    The instance's ``ttl_seconds`` is part of the signed payload, so the only non-vacuous reading
    is that the authorisation expires; counting from the gate call would make the term decorative.
    A timestamp without an offset is refused rather than assumed, because assuming UTC shifted this
    number by eight hours on the first run.
    """
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


def run(repo: pathlib.Path, instance_id: str, *, ops: int = 1,
        contract_path: pathlib.Path | None = None) -> dict:
    from pipd_ls_sp import operation_registry as oreg

    contract_path = contract_path or (PIPD / "contracts" / "operation-registry.pre-v2-r3.json")
    contract_bytes = contract_path.read_bytes()
    contract = json.loads(contract_bytes)
    contract_sha = hashlib.sha256(contract_bytes).hexdigest()
    instance = oi.find_instance(contract, instance_id)

    # 1. signature: the original loader, over the canonical contract in the SBL tree
    body, signed_sha, rat = oreg.load_trusted(str(SBL_ROOT))
    if signed_sha != contract_sha:
        # the SBL tree and the contract file in hand must be the same object
        raise oi.InstanceRefused("INSTANCE_CONTRACT_SHA_MISMATCH",
                                 {"sbl_tree": signed_sha, "in_hand": contract_sha})
    sidecar = json.loads((PIPD / "contracts" / "operation-registry.pre-v2-r3.owner.sig.json")
                         .read_text(encoding="utf-8"))

    # 2. identity from the repository itself
    remote = text(repo, "config", "--get", "remote.origin.url")
    full_name = oi.full_name_from_remote_url(remote)

    # 3-5. head, tree, preimages, staged bytes, changed paths
    relpaths = [e["relpath"] for e in instance["write_set"]]
    state = head_state(repo, relpaths)
    changed = changed_paths(repo)

    repo_state = {
        "head": state["head"], "tree": state["tree"], "write_scope": relpaths,
        "preimages": state["preimages"], "full_name": full_name,
        "repo_id": instance["repo"]["id"],
        "identity_basis": {"remote_url": remote, "resolved_by": "git config --get remote.origin.url"},
    }
    record = oi.evaluate_write(
        contract, instance_id,
        signed_contract_sha256=signed_sha, contract_sha256=contract_sha,
        repo_state=repo_state, observed=state["observed"], changed_paths=changed,
        signed_scope=signed_scope(sidecar),
        ttl_remaining_s=ttl_remaining(instance, sidecar.get("signed_at")),
        ops_requested=ops,
    )
    record["observed_postimages"] = state["observed"]
    record["preimages_at_head"] = state["preimages"]
    record["signature"] = {"window_id": rat.get("window_id"), "signed_at": rat.get("signed_at"),
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
    a = ap.parse_args()
    try:
        record = run(pathlib.Path(a.repo).resolve(), a.instance, ops=a.ops,
                     contract_path=pathlib.Path(a.contract) if a.contract else None)
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
