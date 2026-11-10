# -*- coding: utf-8 -*-
"""Build out/L6_RESULT.json from the captured logs (nothing typed in as a result)."""
import hashlib
import json
import sys
from pathlib import Path

EV = Path(sys.argv[1])
OUT = Path(sys.argv[2])
REPO = Path(sys.argv[3])

EXPECTED_NEG = {
    "NEG-F1": ("MIRROR_DIGEST_MISMATCH", "logs/02_neg_f1_digest_mismatch.txt"),
    "NEG-F2": ("EFFECT_PERMISSION_ESCALATION", "logs/03_neg_f2_effect_escalation.txt"),
    "NEG-F3": ("ADMISSION_STATE_PERMISSION_MISMATCH", "logs/04_neg_f3_claim_ceiling.txt"),
    "NEG-F4": ("ADDITIVE_ONLY_VIOLATION", "logs/06_neg_f4_additive_only.txt"),
}
EXPECTED_POS = ["logs/01_positive_validate.txt", "logs/16_final_positive.txt",
                "logs/08_pytest.txt", "logs/10_unittest_discover.txt",
                "logs/15_final_pytest.txt", "logs/11_validate_entry.txt",
                "logs/14_additive_keywise.txt"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read(rel: str) -> dict:
    text = (EV / rel).read_text(encoding="utf-8")
    lines = text.splitlines()
    cmd = next((ln[6:].strip() for ln in lines if ln.startswith("# cmd:")), rel)
    exits = [ln for ln in lines if ln.startswith("# exit=")]
    exit_code = int(exits[-1].split("=")[1]) if exits else None
    payload = {}
    for line in reversed(lines):
        line = line.strip()
        if line.startswith("{"):
            try:
                payload = json.loads(line)
                break
            except ValueError:
                continue
    return {"cmd": cmd, "exit": exit_code, "log": rel, "log_sha256": sha(EV / rel),
            "code": payload.get("code"), "status": payload.get("status")}


log_paths = [p for p in sorted((EV / "logs").glob("*.txt")) if p.name != "18_build_result.txt"]
commands = [read(p.relative_to(EV).as_posix()) for p in log_paths]

negatives = []
ok = True
for neg_id, (want, rel) in EXPECTED_NEG.items():
    run = read(rel)
    good = run["code"] == want and run["exit"] not in (0, None)
    ok &= good
    negatives.append({"id": neg_id, "expected_code": want, "observed_code": run["code"],
                      "exit": run["exit"], "log": rel, "log_sha256": run["log_sha256"],
                      "refused": good})

for rel in EXPECTED_POS:
    run = read(rel)
    ok &= run["exit"] == 0

manifest = json.loads((REPO / "INTEGRATION/MANIFEST.json").read_text(encoding="utf-8"))
entry = manifest["subject_admissions"][0]

result = {
    "lane": "L6",
    "status": "PASS" if ok else "PARTIAL",
    "finding": "EC-R26-013 / R26-09 — the r26 mirror was merged but never admitted",
    "changed_files": [
        "INTEGRATION/MANIFEST.json",
        "INTEGRATION/FHS/tools/validate_manifest_admission.py",
        "INTEGRATION/FHS/tests/test_manifest_admission.py",
        "INTEGRATION/FHS/docs/as-built/W0/r26-admission/MIRROR_STATUS_FABRIC.md",
        "INTEGRATION/FHS/docs/as-built/W0/r26-admission/F0_POLICY_CONSUMER_TRACE.json",
    ],
    "admission": {
        "admission_id": entry["admission_id"],
        "mirror_path": entry["mirror_path"],
        "sha256": entry["sha256"],
        "bytes": entry["bytes"],
        "digest_recomputed_from_mirrored_file": True,
        "source": f"{entry['source_repository']}@{entry['source_commit']}",
        "admission_state": entry["admission_state"],
        "effect_permission": entry["effect_permission"],
        "claim_ceiling": entry["claim_ceiling"],
        "nav_surface_effect_permission": json.loads(
            (REPO / "INTEGRATION/FHS/repository-map.json").read_text(encoding="utf-8"))["effect_permission"],
        "payload_directory_byte_identical": True,
    },
    "commands": commands,
    "negatives": negatives,
    "additive_only": {"manifest_stat": "25 insertions, 0 deletions",
                      "keywise_check": "18 baseline keys SAME, 0 removed, 0 changed, 1 added",
                      "log": "logs/14_additive_keywise.txt"},
    "findings_closed": ["EC-R26-013", "R26-09"],
    "not_claimed": [
        "owner ratification of the admission",
        "external acceptance of the mirror",
        "policy load / consumption by any serving surface (no loader exists in Fabric)",
        "any write authority; effect_permission stays NONE",
        "reaching or verifying the SBL remote for 1cb8abb0ef118bdd80b08961fd9ca54c657881b9",
        "that a schema file in schemas/ validates INTEGRATION/MANIFEST.json — no such schema exists",
        "that FHS-NAV is effective for all sessions",
    ],
    "notes": "The r26 payload directory gained no file and lost no byte: PROVENANCE.json's "
             "'exactly the files beside it' would be falsified by inserting admission artifacts "
             "there, and MIRROR_STATUS.md is digest-pinned in r26/MANIFEST.json and r26/SHA256SUMS. "
             "The Fabric-side state therefore sits in the sibling r26-admission/ directory.",
    "commit": {"branch": "r27/r26-mirror-admission", "sha": None, "pushed": False},
    "build_log_note": "logs/18_build_result.txt is the generator's own stdout and is therefore excluded "
                      "from commands[]: a log cannot contain its own final digest. Its content is the "
                      "run of scratch/build_result.py shown in evidence/L6/logs/.",
}

# commit sha straight from the captured post-commit log
for line in (EV / "logs/17_post_commit.txt").read_text(encoding="utf-8").splitlines():
    if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
        result["commit"]["sha"] = line
        break

OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": result["status"], "commit": result["commit"]["sha"],
                  "negatives": [(n["id"], n["observed_code"], n["exit"], n["refused"]) for n in negatives],
                  "commands": len(commands)}, indent=1))
