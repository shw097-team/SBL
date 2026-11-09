"""Signed-vote quorum: the predicate the r24 external challenge showed was missing.

r24's `verify_reader_ack.py` accepted a preservation decision whose `value` was a boolean, without asking how
many **valid, distinct, same-candidate** votes backed it. Two signed decisions had one agreeing vote and were
still marked `DECIDED`. This module is the predicate, its deterministic negative fixtures, and a scanner over
the signed receipts.

Rules (each one is a refusal with its own code):
    VALUE_NOT_BOOLEAN          the declared value is not true/false
    STATE_NOT_DECIDED          a property that is not DECIDED cannot be counted as decided
    REREAD_EVIDENCE_MISSING    `resolved_by` is asserted without `reread_refs`
    LANE_ID_DUPLICATE          the same lane voted twice; only one vote per lane counts
    STALE_CANDIDATE_VOTE       a vote names a candidate other than the effective one
    SIGNED_VOTE_QUORUM_FAIL    fewer than `quorum_min` valid votes agree with the declared value
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

QUORUM_MIN = 2


def _valid_votes(votes, effective_candidate):
    """Normalise votes to {lane: vote} keeping only votes that may be counted."""
    out, dropped = {}, []
    if isinstance(votes, dict):
        items = list(votes.items())
    else:
        items = [(v.get("lane_id") or v.get("lane"), v.get("vote")) for v in votes or []]
    for lane, vote in items:
        lane = str(lane or "").strip()
        if not lane:
            dropped.append({"lane": None, "why": "NO_LANE_IDENTITY"})
            continue
        if lane in out:
            dropped.append({"lane": lane, "why": "LANE_ID_DUPLICATE"})
            continue
        if vote == "UNKNOWN" or vote is None:
            continue                      # abstention: not a vote
        if vote not in (True, False):
            dropped.append({"lane": lane, "why": "VOTE_NOT_BOOLEAN"})
            continue
        out[lane] = vote
    # a structured vote list carries the candidate each lane read
    if not isinstance(votes, dict):
        by_lane = {}
        for v in votes or []:
            lane = str(v.get("lane_id") or v.get("lane") or "").strip()
            if v.get("candidate_sha256") and effective_candidate and v["candidate_sha256"] != effective_candidate:
                dropped.append({"lane": lane, "why": "STALE_CANDIDATE_VOTE"})
                by_lane[lane] = "STALE"
        for lane, why in by_lane.items():
            if why == "STALE":
                out.pop(lane, None)
    return out, dropped


def evaluate(prop: dict, *, effective_candidate: str = None, quorum_min: int = QUORUM_MIN) -> dict:
    """Decide one preservation property. Returns {verdict, first_fail, agreeing, dissenting, dropped}."""
    value = prop.get("value")
    state = prop.get("state")
    if value not in (True, False):
        return {"verdict": "HOLD", "first_fail": "VALUE_NOT_BOOLEAN", "agreeing": 0, "dissenting": 0, "dropped": []}
    if state != "DECIDED":
        return {"verdict": "HOLD", "first_fail": "STATE_NOT_DECIDED", "agreeing": 0, "dissenting": 0,
                "dropped": [], "state": state}
    if prop.get("resolved_by") and not (prop.get("reread_refs") or prop.get("repaired_readback_refs")):
        return {"verdict": "HOLD", "first_fail": "REREAD_EVIDENCE_MISSING", "agreeing": 0, "dissenting": 0,
                "dropped": [], "resolved_by": prop.get("resolved_by")}
    # a repaired property carries the re-read votes in `votes_r25`; those are the ones that count, and the
    # pre-repair `votes` stay beside them as history rather than being overwritten
    source = prop.get("votes_r25") if prop.get("votes_r25") else prop.get("votes")
    valid, dropped = _valid_votes(source, effective_candidate)
    agreeing = sum(1 for v in valid.values() if v is value)
    dissenting = sum(1 for v in valid.values() if v is not value)
    if agreeing < quorum_min:
        return {"verdict": "HOLD", "first_fail": "SIGNED_VOTE_QUORUM_FAIL", "agreeing": agreeing,
                "dissenting": dissenting, "valid_lanes": sorted(valid), "dropped": dropped}
    return {"verdict": "ACCEPTABLE_FOR_FHS_READER_SCOPE", "first_fail": None, "agreeing": agreeing,
            "dissenting": dissenting, "valid_lanes": sorted(valid), "dropped": dropped}


def scan_receipts(root: str) -> dict:
    """Every property of every signed reader receipt, evaluated. Fail-closed on an unreadable receipt."""
    findings, checked = [], 0
    files = sorted(glob.glob(os.path.join(root, "receipts", "**", "*.signed.json"), recursive=True))
    for f in files:
        rel = os.path.relpath(f, root).replace(os.sep, "/")
        try:
            env = json.loads(open(f, encoding="utf-8").read())
        except ValueError as e:
            findings.append({"file": rel, "first_fail": "RECEIPT_UNDECODABLE", "detail": str(e)[:120]})
            continue
        body = env.get("body") or {}
        # the candidate the re-read votes were cast on; when a round re-reads a later, prefix-compatible
        # revision the receipt names it here instead of pretending the older binding was what was read
        cand = (body.get("quorum_candidate_sha256")
                or (body.get("binding") or {}).get("candidate_sha256") or body.get("CandidateSHA"))
        for c in body.get("clauses") or []:
            for prop_name, prop in (c.get("preservation") or {}).items():
                checked += 1
                r = evaluate(prop, effective_candidate=cand)
                if r["verdict"] != "ACCEPTABLE_FOR_FHS_READER_SCOPE":
                    findings.append({"file": rel, "wp": body.get("Subject"), "clause_id": c.get("clause_id"),
                                     "property": prop_name, **r})
    return {"receipts": len(files), "properties_checked": checked, "findings": findings,
            "ok": not findings}


def _fixture(value, state, votes, **kw):
    p = {"value": value, "state": state, "votes": votes}
    p.update(kw)
    return p


CASES = [
    # (id, property, expected first_fail)
    ("NEG-Q1", _fixture(True, "DECIDED", {"A": "UNKNOWN", "B": "UNKNOWN", "T": True}), "SIGNED_VOTE_QUORUM_FAIL"),
    ("NEG-Q2", _fixture(True, "DECIDED", {"A": "UNKNOWN", "B": True, "T": False}), "SIGNED_VOTE_QUORUM_FAIL"),
    ("POS-Q3", _fixture(True, "DECIDED", {"A": True, "B": True, "T": False}), None),
    ("NEG-Q4", _fixture(True, "DECIDED", {"A": True, "A ": True}), "SIGNED_VOTE_QUORUM_FAIL"),
    ("NEG-Q7", _fixture(True, "DECIDED", {"A": True, "B": True}, resolved_by="POST_REPAIR_REREAD"), "REREAD_EVIDENCE_MISSING"),
    ("NEG-Q1b", _fixture(True, "HOLD", {"A": True, "B": True}), "STATE_NOT_DECIDED"),
    ("NEG-Q5", _fixture(True, "DECIDED", [{"lane": "A", "vote": True, "candidate_sha256": "old"},
                                          {"lane": "B", "vote": True, "candidate_sha256": "new"}]),
     "SIGNED_VOTE_QUORUM_FAIL"),
]


def selftest() -> int:
    rows, bad = [], 0
    for cid, prop, want in CASES:
        r = evaluate(prop, effective_candidate="new")
        got = r["first_fail"]
        ok = (got == want)
        bad += 0 if ok else 1
        rows.append({"case": cid, "expected": want, "got": got, "verdict": r["verdict"], "ok": ok})
    print(json.dumps({"schema": "FHS.W0.VoteQuorum/1", "cases": len(CASES), "failed": bad, "rows": rows,
                      "SELFTEST": "OK" if bad == 0 else "FAIL"}, ensure_ascii=False, indent=1))
    return 0 if bad == 0 else 5


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rep = scan_receipts(a.root)
    rep["schema"] = "FHS.W0.VoteQuorumScan/1"
    text = json.dumps(rep, ensure_ascii=False, indent=1)
    if a.json_out:
        open(a.json_out, "w", encoding="utf-8", newline="\n").write(text + "\n")
    print(text)
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
