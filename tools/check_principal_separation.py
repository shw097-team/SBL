"""Offline enforcer for FABRIC-PRINCIPAL-SEPARATION/1 (SOD_POLICY.yaml: principal_separation).

Answers exactly one question: are the producer and the checker *distinct attested controllers*, on this frozen
subject, with grants that do not descend from the producer? It does not judge competence or intent, and
IDENTITY_SEPARATION_ADMISSIBLE is not an acceptance - the acceptance officer must still decide on evidence.

Exit 0 only when every predicate is true. Fail closed: unknown counts as failure.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone

FAB = r"C:/Projects/Agent_Workspace/Fabric/FABRIC"
REGISTRY = os.path.join(FAB, "assurance", "principals.json")
PIN = os.path.join(FAB, "assurance", "principals.pinned.sha256")
REQUIRED_SUBJECT = ("candidate_sha256", "environment_sha256", "abi_sha256")


def _sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _now(ts: str | None = None) -> datetime:
    if ts is None:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))


def load(path: str = REGISTRY) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def pin_ok(path_registry: str = REGISTRY, path_pin: str = PIN) -> tuple[bool, str]:
    """P1: the registry bytes must match an owner-pinned digest, else every verdict over it is void."""
    if not os.path.exists(path_pin):
        return False, "PIN_MISSING"
    pinned = open(path_pin, encoding="utf-8").read().split()[0].strip()
    actual = _sha(path_registry)
    return (pinned == actual), ("PIN_MATCH" if pinned == actual else "PIN_MISMATCH")


def resolve(reg: dict, identity: str) -> list[dict]:
    """P2: an identity resolves through principal_id or an alias, never by inventing a new controller."""
    return [p for p in reg.get("principals") or []
            if p.get("principal_id") == identity or identity in (p.get("aliases") or [])]


def attestation_ok(reg: dict, p: dict, at: datetime) -> tuple[bool, str]:
    att = p.get("attestation") or {}
    att_id = att.get("attestor_principal_id")
    trusted = {t.get("principal_id") for t in reg.get("trust_roots") or []}
    if att_id not in trusted:
        return False, "ATTESTOR_UNTRUSTED"
    if att.get("revoked"):
        return False, "ATTESTATION_REVOKED"
    try:
        if _now(att.get("expires_at")) < at:
            return False, "ATTESTATION_EXPIRED"
    except Exception:
        return False, "ATTESTATION_UNDATED"
    return True, "ATTESTED"


def ancestry_hits_producer(reg: dict, grant: dict, producer_ids: set[str]) -> bool:
    """P5: walk the delegation chain over GRANTORS; a producer anywhere in the authority chain disqualifies the
    checker. A grant held by the producer itself is not disqualifying - that is the maker's own authority."""
    by_id = {g.get("grant_id"): g for g in reg.get("grants") or []}
    seen: set[str] = set()
    cur = grant
    while cur:
        gid = cur.get("grant_id")
        if gid in seen:
            return True
        seen.add(gid)
        if cur.get("authority_principal_id") in producer_ids:
            return True
        nxt = cur.get("delegation_parent_grant_id")
        cur = by_id.get(nxt) if nxt else None
    return False


def check_verdict(verdict: dict, reg: dict | None = None, at: datetime | None = None,
                  registry: str = REGISTRY, pin: str = PIN) -> dict:
    reg = reg if reg is not None else load(registry)
    at = at or _now()
    preds: list[dict] = []

    ok_pin, pin_note = pin_ok(registry, pin)
    preds.append({"id": "P1_registry_pinned", "ok": ok_pin, "note": pin_note})

    subject = verdict.get("subject") or {}
    subj_ok = all(isinstance(subject.get(k), str) and len(subject.get(k, "")) == 64 for k in REQUIRED_SUBJECT)
    preds.append({"id": "P0_subject_bound", "ok": subj_ok,
                  "note": ",".join(sorted(subject)) or "missing"})

    producers = verdict.get("producer_identity") or []
    if isinstance(producers, str):
        producers = [producers]
    prod_recs: list[dict] = []
    res_ok = True
    for ident in producers:
        hits = resolve(reg, ident)
        if len(hits) != 1:
            res_ok = False
        prod_recs += hits
    # DOC-07#3394 calls the canonical field `independent_checker_ref`; this checks the KB field when present and
    # refuses a verdict whose two spellings resolve to different principals.
    ref = verdict.get("independent_checker_ref")
    ident = verdict.get("independent_checker_identity") or ""
    chk_hits = resolve(reg, ref or ident)
    if ref and ident and ref != ident:
        alt = resolve(reg, ident)
        if {(h.get("principal_id") or "") for h in alt} != {(h.get("principal_id") or "") for h in chk_hits}:
            chk_hits = []
    res_ok = res_ok and len(chk_hits) == 1 and bool(producers)
    preds.append({"id": "P2_identity_resolved", "ok": res_ok,
                  "note": "producers=%d checker=%d" % (len(prod_recs), len(chk_hits))})

    prod_ids = {p.get("principal_id") or "" for p in prod_recs}
    prod_ctrls = {p.get("controller_id") or "" for p in prod_recs}
    chk_ids = {c.get("principal_id") or "" for c in chk_hits}
    chk_ctrls = {c.get("controller_id") or "" for c in chk_hits}
    distinct = bool(chk_hits) and not (prod_ids & chk_ids) and not (prod_ctrls & chk_ctrls)
    preds.append({"id": "P3_distinct_controller", "ok": distinct,
                  "note": "checker=%s producer=%s" % (sorted(chk_ctrls), sorted(prod_ctrls))})

    att_ok, att_note = True, []
    for p in prod_recs + chk_hits:
        good, note = attestation_ok(reg, p, at)
        att_ok = att_ok and good
        att_note.append("%s:%s" % (p.get("principal_id"), note))
    preds.append({"id": "P4_attestation_valid", "ok": att_ok, "note": "; ".join(att_note)})

    want = list(verdict.get("grant_ids") or [])
    grants = [g for g in reg.get("grants") or [] if g.get("grant_id") in want]
    g_ok = len(grants) == len(want) and bool(want)
    g_note = [] if g_ok else ["GRANT_MISSING"]
    for g in grants:
        if g.get("revoked"):
            g_ok = False
            g_note.append("%s:REVOKED" % g.get("grant_id"))
        try:
            if _now(g.get("expires_at")) < at:
                g_ok = False
                g_note.append("%s:EXPIRED" % g.get("grant_id"))
        except Exception:
            g_ok = False
            g_note.append("%s:UNDATED" % g.get("grant_id"))
        if g.get("subject") and g.get("subject") != subject:
            g_ok = False
            g_note.append("%s:SUBJECT_MISMATCH" % g.get("grant_id"))
        if ancestry_hits_producer(reg, g, prod_ids):
            g_ok = False
            g_note.append("%s:PRODUCER_ANCESTRY" % g.get("grant_id"))
    chk_roles = {g.get("role") for g in grants if g.get("principal_id") in chk_ids}
    if "final_checker" not in chk_roles:
        g_ok = False
        g_note.append("NO_FINAL_CHECKER_GRANT")
    preds.append({"id": "P5_grant_bound_and_clean", "ok": g_ok, "note": "; ".join(g_note) or "ok"})

    all_ok = all(p["ok"] for p in preds)
    return {"schema": "FABRIC-PRINCIPAL-SEPARATION-RESULT/1",
            "verdict_id": verdict.get("verdict_id"),
            "registry_snapshot_sha256": _sha(registry) if os.path.exists(registry) else None,
            "subject": subject,
            "predicates": preds,
            "result": "IDENTITY_SEPARATION_ADMISSIBLE" if all_ok else "INADMISSIBLE",
            "acceptance_effect": None if all_ok else "NOT_ESTABLISHED",
            "claim_ceiling": "two identities are distinct and attested; competence and independence in intent are not established",
            "failure_ceiling": None if all_ok else "NO_IDENTITY_SEPARATION_ESTABLISHED__ACCEPTANCE_NOT_ESTABLISHED",
            "kb_basis": ["SBL_PIPD-LS-PKG_DOC-07.md#3254", "SBL_PIPD-LS-PKG_DOC-07.md#3394",
                         "SBL_PIPD-LS-PKG_DOC-07.md#132"],
            "evaluated_at_utc": at.strftime("%Y-%m-%dT%H:%M:%SZ")}


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_principal_separation.py <verdict.json>")
        return 2
    with open(argv[1], encoding="utf-8") as fh:
        res = check_verdict(json.load(fh))
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res["result"] == "IDENTITY_SEPARATION_ADMISSIBLE" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
