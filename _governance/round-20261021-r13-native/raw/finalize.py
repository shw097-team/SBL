"""R13 stage `finalize`: project transitions, checkpoint, and two typed negative controls."""
from __future__ import annotations

import json
import sys
from pathlib import Path

HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
sys.path.insert(0, str(HGK / "src"))
from hg_kseos.lifecycle import ProjectLifecycleController  # noqa: E402
from hg_kseos.spine import SharedSpine  # noqa: E402

OUT = HGK / "var" / "R13-NATIVE-20261021"
spine = SharedSpine(HGK / "var" / "shared-spine" / "hg-kseos.db")
c = ProjectLifecycleController(spine)
rec: dict = {"negatives": {}}

# 1) project lifecycle forward to EVOLUTION_REVIEW + checkpoint
pid = "HGKR13-WO"
rec["state_before"] = c.status(pid)["state"]
for st in ("EXECUTING", "VERIFYING", "EVOLUTION_REVIEW"):
    c.transition(pid, st, trigger="R13_WO_VERIFIED", workorder_refs=["WO-TS-WO-01"])
rec["checkpoint"] = c.checkpoint(pid, evidence_refs=[str(OUT / "candidate.diff")])["state"]
rec["state_after"] = c.status(pid)["state"]

# 2) negative control A: maker cannot accept its own work
try:
    spine.record_workorder_result("WO-TS-WO-02", writer="codex", checker="codex", verdict="PASS",
                                  evidence_refs=["x"])
    rec["negatives"]["self_review"] = "NO_DENIAL(!!)"
except Exception as exc:
    rec["negatives"]["self_review"] = f"{type(exc).__name__}: {exc}"

# 3) negative control B: a VERIFIED workorder cannot be re-judged (no replay of a pass)
try:
    spine.record_workorder_result("WO-TS-WO-01", writer="codex", checker="openai-codex/gpt-6.1-sol",
                                  verdict="PASS", evidence_refs=["x"])
    rec["negatives"]["replay_verified"] = "NO_DENIAL(!!)"
except Exception as exc:
    rec["negatives"]["replay_verified"] = f"{type(exc).__name__}: {exc}"

# 4) negative control C: an expired binding must refuse
from datetime import UTC, datetime, timedelta  # noqa: E402
from hg_kseos import role_binding  # noqa: E402

b = json.loads((OUT / "binding.json").read_text(encoding="utf-8"))
expired = dict(b, expiry=(datetime.now(UTC) - timedelta(minutes=1)).isoformat())
try:
    role_binding.validate_binding(expired, workorder_id=b["workorder"], subject=b["subject"],
                                  base_head=b["base_head"])
    rec["negatives"]["expired_binding"] = "NO_DENIAL(!!)"
except Exception as exc:
    rec["negatives"]["expired_binding"] = f"{type(exc).__name__}: {exc}"

(OUT / "stage_finalize.json").write_text(json.dumps(rec, indent=2), encoding="utf-8")
print(json.dumps(rec, indent=2, ensure_ascii=False))
