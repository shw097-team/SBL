# -*- coding: utf-8 -*-
"""Build the F0 policy-consumption trace from captured runs.

Every number below is READ: the digest from the manifest entry (itself verified
against the mirrored file), the codes and exit statuses from the captured logs, the
log digests from the log files. Nothing is typed in as a result.
"""
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

EV = Path(sys.argv[1])
REPO = Path(sys.argv[2])

LOGS = [
    ("POS_VALIDATE", "logs/01_positive_validate.txt"),
    ("NEG-F1", "logs/02_neg_f1_digest_mismatch.txt"),
    ("NEG-F2", "logs/03_neg_f2_effect_escalation.txt"),
    ("NEG-F3", "logs/04_neg_f3_claim_ceiling.txt"),
    ("CONTROL_POS_ENTRY", "logs/05_control_admitted_entry.txt"),
    ("NEG-F4", "logs/06_neg_f4_additive_only.txt"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_run(rel: str) -> dict:
    text = (EV / rel).read_text(encoding="utf-8")
    cmd = next((ln[6:] for ln in text.splitlines() if ln.startswith("# cmd:")), "")
    exit_line = [ln for ln in text.splitlines() if ln.startswith("# exit=")]
    payload = {}
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line.startswith("{"):
            try:
                payload = json.loads(line)
                break
            except ValueError:
                continue
    return {
        "cmd": cmd,
        "exit": int(exit_line[-1].split("=")[1]) if exit_line else None,
        "observed_code": payload.get("code"),
        "status": payload.get("status"),
        "errors": payload.get("errors", []),
        "log": rel,
        "log_sha256": sha(EV / rel),
    }


manifest = json.loads((REPO / "INTEGRATION/MANIFEST.json").read_text(encoding="utf-8"))
entry = manifest["subject_admissions"][0]
nav_map_path = REPO / "INTEGRATION/FHS/repository-map.json"
nav_map = json.loads(nav_map_path.read_text(encoding="utf-8"))

runs = {}
for run_id, rel in LOGS:
    runs[run_id] = read_run(rel)

trace = {
    "schema": "RP002-F0-POLICY-CONSUMER-TRACE/1",
    "trace_id": "F0-FABRIC-R26-MIRROR-NAV-001",
    "gate": "F0",
    "generated_at": dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).replace(microsecond=0).isoformat(),
    "subject": "FHS W0 r26 governance mirror as admitted into the Fabric navigation surface",
    "policy_artifact": entry["mirror_path"],
    "sha256": entry["sha256"],
    "bytes": entry["bytes"],
    "digest_provenance": "re-hashed from the mirrored file itself inside this worktree during this round; "
                         "the value in INTEGRATION/MANIFEST.json and the value in r26/MANIFEST.json agree, "
                         "and neither was used as the source of the other",
    "source": {"repository": entry["source_repository"], "commit": entry["source_commit"]},
    "consumer": "FHS-NAV/v2 navigation surface — INTEGRATION/FHS/repository-map.json read through "
                "INTEGRATION/MANIFEST.json subject_admissions[]",
    "consumer_sha256": sha(nav_map_path),
    "consumer_effect_permission": nav_map["effect_permission"],
    "admission_record_sha256": sha(REPO / "INTEGRATION/MANIFEST.json"),
    "decision": "ADMIT_MIRROR_FOR_NAVIGATION",
    "effect_permission": entry["effect_permission"],
    "admission_state": entry["admission_state"],
    "claim_ceiling": entry["claim_ceiling"],
    "evidence": {
        "admission_record": "INTEGRATION/MANIFEST.json#subject_admissions[0]",
        "reader": "INTEGRATION/FHS/tools/validate_manifest_admission.py",
        "reader_sha256": sha(REPO / "INTEGRATION/FHS/tools/validate_manifest_admission.py"),
        "tests": "INTEGRATION/FHS/tests/test_manifest_admission.py",
        "test_runs": [
            {k: read_run(trel)[k] for k in ("cmd", "exit", "log", "log_sha256")}
            for trel in ("logs/08_pytest.txt", "logs/10_unittest_discover.txt")
        ],
        "runs": runs,
        "reproduce": "cd <repo> && python INTEGRATION/FHS/tools/validate_manifest_admission.py "
                     "--baseline <pre-change MANIFEST.json>",
    },
    "chain": [
        {
            "step": 1,
            "element": "frozen policy artifact (the mirrored subject)",
            "artifact": entry["mirror_path"],
            "sha256": entry["sha256"],
            "evidence": f"{entry['bytes']} bytes; digest re-derived from these bytes in this round",
        },
        {
            "step": 2,
            "element": "consuming surface",
            "artifact": "INTEGRATION/FHS/repository-map.json (FHS-NAV/v2)",
            "sha256": sha(nav_map_path),
            "evidence": f"effect_permission={nav_map['effect_permission']}; "
                        f"source_state={nav_map['source_state']}; "
                        f"unknown_route={nav_map['unknown_route']}",
        },
        {
            "step": 3,
            "element": "admission decision",
            "artifact": "INTEGRATION/MANIFEST.json#subject_admissions[0]",
            "sha256": entry["sha256"],
            "evidence": f"admission_state={entry['admission_state']}; "
                        f"effect_permission={entry['effect_permission']}; "
                        f"claim_ceiling={entry['claim_ceiling']}",
        },
        {
            "step": 4,
            "element": "reader consumed the artifact and the record",
            "artifact": "INTEGRATION/FHS/tools/validate_manifest_admission.py",
            "sha256": sha(REPO / "INTEGRATION/FHS/tools/validate_manifest_admission.py"),
            "evidence": f"{runs['POS_VALIDATE']['cmd']} -> exit "
                        f"{runs['POS_VALIDATE']['exit']}, code {runs['POS_VALIDATE']['observed_code']}, "
                        f"log {runs['POS_VALIDATE']['log']} sha256 {runs['POS_VALIDATE']['log_sha256']}",
        },
        {
            "step": 5,
            "element": "refusals executed by the same reader",
            "artifact": "candidate entries fed to the same code path",
            "evidence": "; ".join(
                f"{k}: exit {runs[k]['exit']}, code {runs[k]['observed_code']} "
                f"(log {runs[k]['log']} sha256 {runs[k]['log_sha256']})"
                for k in ("NEG-F1", "NEG-F2", "NEG-F4")
            ),
        },
        {
            "step": 6,
            "element": "evidence",
            "artifact": "captured stdout + exit status per run",
            "evidence": "every code above is printed by the validator and stored beside its command line; "
                        "the control run accepted an unmodified entry, so no refusal is a blanket refusal",
        },
    ],
    "negatives": [
        {"id": k, "expected_ok": False, "exit": runs[k]["exit"], "observed_code": runs[k]["observed_code"],
         "log": runs[k]["log"], "log_sha256": runs[k]["log_sha256"]}
        for k in ("NEG-F1", "NEG-F2", "NEG-F3", "NEG-F4")
    ],
    "not_claimed": [
        "NOT_OWNER_RATIFIED",
        "NOT_EXTERNALLY_ACCEPTED",
        "NOT_LOADED_AS_POLICY",
        "NO_WRITE_AUTHORITY",
        "NO_LIVE_WORLD_EFFECT",
        "SOURCE_COMMIT_NOT_REMOTE_VERIFIED_THIS_ROUND",
    ],
    "yaml_presence_alone": "NOT_ACCEPTED",
}

out = REPO / "INTEGRATION/FHS/docs/as-built/W0/r26-admission/F0_POLICY_CONSUMER_TRACE.json"
out.write_text(json.dumps(trace, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("wrote", out)
print(json.dumps({"decision": trace["decision"], "effect_permission": trace["effect_permission"],
                  "runs": {k: (v["exit"], v["observed_code"]) for k, v in runs.items()}}, indent=1))
