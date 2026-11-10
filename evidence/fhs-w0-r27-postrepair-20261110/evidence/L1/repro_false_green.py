"""R26/L1 — reproduce the three false-green classes against the PRE-REPAIR verifier.

Builds one minimal mirror round per class under the evidence dir (native python cannot read MSYS /tmp),
runs the baseline verifier over each mirror as a child process, and prints the observed verdict + code +
child exit code. Nothing here types a result: every line is read back from the child's stdout.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASELINE = os.path.join(HERE, "verify_quorum.BASELINE.py")
MIRROR = os.path.join(HERE, "mirror_false_green")
PY = sys.executable

FABRICATED = "00" * 32
REAL_RAW = b"FHS r25 transcript\r\nlane: PLAN\r\nvote: true\r\n"


def _raw_vote(**over):
    v = {
        "lane_id": "PLAN",
        "vote": True,
        "candidate_sha256": "cand-eff",
        "source_sha256": "src-1",
        "clause_id": "WP-FG:L1:1",
        "property": "scope_preserved",
        "raw_file": "lanes/votes/raw_r25.txt",
        "raw_sha256": FABRICATED,
        "at": "2026-11-09T18:32:59+08:00",
    }
    v.update(over)
    return v


CLASSES = {
    "FG1_MISSING_CANDIDATE_SHA_ACCEPTED": {
        "value": True,
        "state": "DECIDED",
        "votes_r25": {"A": True, "B": True},
    },
    "FG2_TAMPERED_RAW_HASH_NOT_CHECKED": {
        "value": True,
        "state": "DECIDED",
        "votes_r25": [_raw_vote(lane_id="PLAN"), _raw_vote(lane_id="VERIFY")],
    },
    "FG3_INTEGER_ONE_AS_BOOLEAN_ACCEPTED": {
        "value": 1,
        "state": "DECIDED",
        "votes_r25": [_raw_vote(lane_id="PLAN", vote=1),
                      _raw_vote(lane_id="VERIFY", vote=1)],
    },
    "FG3b_INTEGER_VOTES_BOOL_VALUE": {
        "value": True,
        "state": "DECIDED",
        "votes_r25": [_raw_vote(lane_id="PLAN", vote=1),
                      _raw_vote(lane_id="VERIFY", vote=1)],
    },
}


def build(cls: str, prop: dict) -> str:
    root = os.path.join(MIRROR, cls)
    rec = os.path.join(root, "receipts", "reader")
    os.makedirs(rec, exist_ok=True)
    os.makedirs(os.path.join(root, "votes"), exist_ok=True)
    # the raw transcript is really on disk; its bytes are NOT the fabricated digest
    with open(os.path.join(root, "votes", "raw_r25.txt"), "wb") as fh:
        fh.write(REAL_RAW)
    env = {"body": {"Subject": "WP-FG", "quorum_candidate_sha256": "cand-eff",
                    "clauses": [{"clause_id": "WP-FG:L1:1",
                                 "preservation": {"scope_preserved": prop}}]}}
    with open(os.path.join(rec, "WP-FG.signed.json"), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(env, fh, ensure_ascii=False, indent=1)
    return root


def run(verifier: str, root: str) -> dict:
    p = subprocess.run([PY, verifier, "--root", root], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    try:
        rep = json.loads(p.stdout)
    except ValueError:
        rep = {"_unparsable_stdout": p.stdout[:400], "_stderr": p.stderr[:400]}
    first = (rep.get("findings") or [{}])[0]
    return {"root": os.path.relpath(root, HERE).replace(os.sep, "/"), "exit": p.returncode,
            "ok": rep.get("ok"), "properties_checked": rep.get("properties_checked"),
            "first_fail": first.get("first_fail"), "verdict": first.get("verdict"),
            "agreeing": first.get("agreeing"), "dropped": first.get("dropped")}


def main() -> int:
    verifier = sys.argv[1] if len(sys.argv) > 1 else BASELINE
    rows = []
    for cls, prop in CLASSES.items():
        root = build(cls, prop)
        rows.append({"class": cls, **run(verifier, root)})
    out = {"schema": "FHS.W0.FalseGreenRepro/1", "verifier": os.path.basename(verifier),
           "verifier_sha256": _sha(verifier), "classes": len(CLASSES), "rows": rows,
           "false_greens": [r["class"] for r in rows if r["ok"] is True]}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


def _sha(path: str) -> str:
    import hashlib
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


if __name__ == "__main__":
    sys.exit(main())
