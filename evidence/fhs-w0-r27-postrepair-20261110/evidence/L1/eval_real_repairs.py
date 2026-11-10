"""R26/L1 — the two signed r25 repairs, evaluated verbatim, before and after the repair.

No assertion is typed here: both verifiers are imported and run, and their returned dicts are printed.
Also measures the R26-01_GAP field gap (session_id/process_id) and both raw-resolution roots.
"""
from __future__ import annotations

import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-quorum/evidence/fhs-w0-r26-repair-20261109"
BASELINE = os.path.join(HERE, "verify_quorum.BASELINE.py")
REPAIRED = os.path.join(ROUND, "tools", "verify_quorum.py")
PROVENANCE = "C:/Projects/Agent_Workspace/FHS/FHS_W0_R13_ACCEPTANCE_20261108"

TARGETS = [("receipts/reader/WP-FHS-00.signed.json", "WP-FHS-00:L1:817", "exceptions_preserved"),
           ("receipts/reader/WP-FHS-01.signed.json", "WP-FHS-01:L1:812", "scope_preserved")]


def load(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def props():
    for rel, clause, name in TARGETS:
        with open(os.path.join(ROUND, rel), encoding="utf-8") as fh:
            body = json.loads(fh.read())["body"]
        cand = (body.get("quorum_candidate_sha256")
                or (body.get("binding") or {}).get("candidate_sha256"))
        for c in body.get("clauses") or []:
            if c.get("clause_id") == clause and name in (c.get("preservation") or {}):
                yield rel, clause, name, cand, c["preservation"][name]


def gap_measurement() -> dict:
    fields = ["lane_id", "candidate_sha256", "source_sha256", "clause_id", "property",
              "raw_path", "raw_file", "raw_sha256", "timestamp", "at", "session_id", "process_id"]
    tally = {f: 0 for f in fields}
    votes = 0
    for _rel, _cl, _n, _c, prop in props():
        for v in prop["votes_r25"]:
            votes += 1
            for f in fields:
                if v.get(f) not in (None, ""):
                    tally[f] += 1
    return {"votes_measured": votes, "present": tally,
            "absent": [f for f in fields if tally[f] == 0]}


def main() -> int:
    base = load(BASELINE, "vq_baseline")
    rep = load(REPAIRED, "vq_repaired")
    rows = []
    for rel, clause, name, cand, prop in props():
        rows.append({
            "receipt": rel, "clause_id": clause, "property": name, "effective_candidate": cand,
            "votes_r25": len(prop["votes_r25"]),
            "baseline": {k: base.evaluate(prop, effective_candidate=cand).get(k)
                         for k in ("verdict", "first_fail", "agreeing")},
            "repaired_default": {k: rep.evaluate(prop, effective_candidate=cand, raw_root=ROUND).get(k)
                                 for k in ("verdict", "first_fail", "agreeing")},
            "repaired_raw_bindings": rep.evaluate(prop, effective_candidate=cand, raw_root=ROUND).get("raw_bindings"),
            "repaired_in_process_no_raw_root": rep.evaluate(prop, effective_candidate=cand).get("verdict"),
            "repaired_provenance_raw_root": rep.evaluate(prop, effective_candidate=cand,
                                                         raw_root=PROVENANCE).get("raw_bindings"),
            "repaired_strict": {k: rep.evaluate(prop, effective_candidate=cand, raw_root=ROUND,
                                                strict=True).get(k) for k in ("verdict", "first_fail")},
        })
    out = {"schema": "FHS.W0.RealRepairsEval/1", "targets": len(rows),
           "repaired_verifier_sha256": rep.__dict__.get("__file__") and
           __import__("hashlib").sha256(open(REPAIRED, "rb").read()).hexdigest(),
           "rows": rows, "gap": gap_measurement()}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
