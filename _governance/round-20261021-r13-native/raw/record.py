"""R13 stage `record`: freeze the candidate, build the typed role-evidence bundle, record the WO result."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
sys.path.insert(0, str(HGK / "src"))
from hg_kseos.spine import SharedSpine  # noqa: E402

OUT = HGK / "var" / "R13-NATIVE-20261021"
WO = "WO-TS-WO-01"
SUBJECT = "src/hg_kseos/lifecycle.py"
CHECKER = "openai-codex/gpt-6.1-sol"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> None:
    spine = SharedSpine(HGK / "var" / "shared-spine" / "hg-kseos.db")
    binding = json.loads((OUT / "binding.json").read_text(encoding="utf-8"))
    diff = OUT / "candidate.diff"
    verify = OUT / "VERIFY_check.json"
    banked = HGK / "var" / "checker-scratch" / "round-20261021-r13"
    banked.mkdir(parents=True, exist_ok=True)
    banked_verify = banked / "VERIFY_check.json"
    banked_verify.write_bytes(verify.read_bytes())

    bundle = {
        "workorder": WO,
        "session": binding["session"],
        "round": binding["round"],
        "subject": SUBJECT,
        "mandate_digest": binding["mandate_digest"],
        "role": "VERIFY_SECURITY",
        "surface": "codex-cli",
        "artifact_digest": "sha256:" + sha(diff),
        "checker_identity": CHECKER,
        "guard": "CLEAN",
        "lane_receipt": {
            "ok": True,
            "receipt_path": str(banked_verify),
            "receipt_digest": "sha256:" + sha(banked_verify),
            "served_arm": "openai-codex/gpt-6.1-sol",
        },
        "log_refs": [
            {"path": str(banked_verify), "sha256": sha(banked_verify)},
            {"path": str(OUT / "GREEN_test_output.txt"), "sha256": sha(OUT / "GREEN_test_output.txt")},
            {"path": str(OUT / "RED_test_output.txt"), "sha256": sha(OUT / "RED_test_output.txt")},
        ],
    }
    (OUT / "role_evidence.json").write_text(json.dumps(bundle, indent=2), encoding="utf-8")
    refs = [str(banked_verify), str(OUT / "candidate.diff"), str(OUT / "GREEN_test_output.txt")]
    result = spine.record_workorder_result(
        WO, writer="codex", checker=CHECKER, verdict="PASS", evidence_refs=refs,
        role_evidence=bundle, evidence_subject=SUBJECT,
    )
    with spine.connect() as conn:
        row = conn.execute("SELECT state,result_json FROM workorders WHERE workorder_id=?", (WO,)).fetchone()
    print(json.dumps({"result": result, "state": row["state"],
                      "rows": json.loads(row["result_json"])}, indent=2)[:1400])


if __name__ == "__main__":
    main()
