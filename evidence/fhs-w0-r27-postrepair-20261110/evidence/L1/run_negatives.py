"""R26/L1 — execute the negative fixtures as receipt trees, not as in-process assertions.

One mirror round per refusal class under `mirror_neg/`, each scanned by the verifier as a CHILD process
(`verify_quorum.py --root <mirror> --raw-root <mirror>`), so every row is a real exit code plus a real
`first_fail` read back from the child's own JSON. `POS_CONTROL` is the same binary on a well-formed
receipt: without it a refusal cannot be distinguished from a verifier that refuses everything.

Usage: python run_negatives.py [--verifier PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND = ("C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-quorum/evidence/fhs-w0-r26-repair-20261109")
MIRROR = os.path.join(HERE, "mirror_neg")
PY = sys.executable

RAW = b"FHS r25 transcript\r\nlane: PLAN\r\nvote: true\r\n"
RAW_SHA = hashlib.sha256(RAW).hexdigest()
FABRICATED = "00" * 32
EFF = "cand-eff"


def rv(**over):
    v = {"lane_id": "PLAN", "vote": True, "candidate_sha256": EFF, "source_sha256": "src-1",
         "clause_id": "WP-NEG:L1:1", "property": "scope_preserved",
         "raw_file": "lanes/votes/raw_r25.txt", "raw_sha256": RAW_SHA,
         "timestamp": "2026-11-09T18:32:59+08:00"}
    v.update(over)
    return v


CASES = {
    # id: (expected first_fail, property, write the raw transcript?)
    "FG1_DICT_NO_BINDING": ("MISSING_CANDIDATE_BINDING",
                            {"value": True, "state": "DECIDED", "votes_r25": {"A": True, "B": True}}, True),
    "FG2_FABRICATED_RAW": ("RAW_DIGEST_MISMATCH",
                           {"value": True, "state": "DECIDED",
                            "votes_r25": [rv(lane_id="PLAN", raw_sha256=FABRICATED),
                                          rv(lane_id="VERIFY", raw_sha256=FABRICATED)]}, True),
    "FG3_INT_ONE_VOTE": ("VOTE_TYPE_INVALID",
                         {"value": True, "state": "DECIDED",
                          "votes_r25": [rv(lane_id="PLAN", vote=1), rv(lane_id="VERIFY", vote=1)]}, True),
    "FG4_PROCESS_DUP": ("PROCESS_ID_DUPLICATE",
                        {"value": True, "state": "DECIDED",
                         "votes_r25": [rv(lane_id="PLAN", session_id="s1", process_id="p1"),
                                       rv(lane_id="VERIFY", session_id="s1", process_id="p1")]}, True),
    "FG5_RAW_ABSENT": ("RAW_EVIDENCE_UNREADABLE",
                       {"value": True, "state": "DECIDED",
                        "votes_r25": [rv(lane_id="PLAN"), rv(lane_id="VERIFY")]}, False),
    "FG6_INT_ONE_VALUE": ("VALUE_NOT_BOOLEAN",
                          {"value": 1, "state": "DECIDED",
                           "votes_r25": [rv(lane_id="PLAN"), rv(lane_id="VERIFY")]}, True),
    "POS_CONTROL": (None,
                    {"value": True, "state": "DECIDED",
                     "votes_r25": [rv(lane_id="PLAN"), rv(lane_id="VERIFY")]}, True),
}


def build(cid: str, prop: dict, write_raw: bool) -> str:
    root = os.path.join(MIRROR, cid)
    os.makedirs(os.path.join(root, "receipts", "reader"), exist_ok=True)
    os.makedirs(os.path.join(root, "votes"), exist_ok=True)
    if write_raw:
        with open(os.path.join(root, "votes", "raw_r25.txt"), "wb") as fh:
            fh.write(RAW)
    env = {"body": {"Subject": "WP-NEG", "quorum_candidate_sha256": EFF,
                    "clauses": [{"clause_id": "WP-NEG:L1:1",
                                 "preservation": {"scope_preserved": prop}}]}}
    with open(os.path.join(root, "receipts", "reader", "WP-NEG.signed.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(env, fh, ensure_ascii=False, indent=1)
    return root


def run(verifier: str, root: str) -> dict:
    p = subprocess.run([PY, verifier, "--root", root, "--raw-root", root],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    try:
        rep = json.loads(p.stdout)
    except ValueError:
        return {"exit": p.returncode, "ok": None, "first_fail": "UNPARSABLE_STDOUT",
                "stdout_head": p.stdout[:200], "stderr_head": p.stderr[:400]}
    first = (rep.get("findings") or [{}])[0]
    return {"exit": p.returncode, "ok": rep.get("ok"), "properties_checked": rep.get("properties_checked"),
            "first_fail": first.get("first_fail"), "verdict": first.get("verdict"),
            "agreeing": first.get("agreeing"), "detail": first.get("dropped") or first.get("missing")}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verifier", default=os.path.join(ROUND, "tools", "verify_quorum.py"))
    a = ap.parse_args()
    with open(a.verifier, "rb") as fh:
        vsha = hashlib.sha256(fh.read()).hexdigest()
    rows, bad = [], 0
    for cid, (want, prop, write_raw) in CASES.items():
        root = build(cid, prop, write_raw)
        r = run(a.verifier, root)
        good = (r["exit"] == 0) if want is None else (r["first_fail"] == want and r["exit"] != 0)
        bad += 0 if good else 1
        rows.append({"id": cid, "expected_code": want, "observed_code": r["first_fail"],
                     "exit": r["exit"], "ok_field": r["ok"], "verdict": r["verdict"],
                     "agreeing": r["agreeing"], "as_expected": good,
                     "mirror": os.path.relpath(root, HERE).replace(os.sep, "/"), "detail": r.get("detail")})
    out = {"schema": "FHS.W0.NegativeMirrors/1", "verifier": a.verifier, "verifier_sha256": vsha,
           "cases": len(rows), "as_expected": sum(1 for r in rows if r["as_expected"]), "failed": bad,
           "rows": rows, "RESULT": "OK" if bad == 0 else "FAIL"}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0 if bad == 0 else 5


if __name__ == "__main__":
    sys.exit(main())
