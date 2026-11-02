#!/usr/bin/env python3
"""Run all 13 pipd commands end to end and freeze the raw receipts."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
ART = ROOT / ".hgk" / "artifacts" / "s1"
OUT = ROOT / ".hgk" / "artifacts" / "cli"
OUT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)
env = dict(os.environ, PYTHONPATH=str(SRC), PYTHONDONTWRITEBYTECODE="1")


def run(args: list[str]) -> dict:
    proc = subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", "--root", str(ROOT)] + args,
                          capture_output=True, text=True, env=env, cwd=str(ROOT))
    body = proc.stdout.strip() or proc.stderr.strip()
    try:
        payload = json.loads(body)
    except Exception:
        payload = {"raw": body[:400]}
    return {"args": args, "exit": proc.returncode, "payload": payload}


def main() -> int:
    (ART / "bundle.json").write_text(json.dumps({
        "PI-PKG": json.loads((ART / "pi_pkg.json").read_text(encoding="utf-8")),
        "PD-PKG": json.loads((ART / "pd_pkg.json").read_text(encoding="utf-8")),
        "ECP": json.loads((ART / "ecp.json").read_text(encoding="utf-8")),
        "TQAEP": json.loads((ART / "tqaep.json").read_text(encoding="utf-8")),
        "ConstructionContract": json.loads((ART / "construction_contract.json").read_text(encoding="utf-8")),
    }, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    (ART / "tmp_diff.json").write_text(json.dumps({"schema_version": "X@1", "verdict": "PASS"}), encoding="utf-8", newline="")

    plan = [
        ["init"],
        ["intake", "--goal", "以治理控制平面實作 PIPD-LS-SP 系統並完成測試驗收與公開交付",
         "--source", str(ROOT), "--constraint", "HGK-only control plane",
         "--non-goal", "no second control plane"],
        ["profile", "--profile", "STANDARD", "--axis", "intent", "--axis", "verification"],
        ["compile-pi", "--intent", str(ART / "intent_card.json"), "--profile", "LITE"],
        ["bind-pd", "--pi", str(ART / "pi_pkg.json"), "--repo-root", str(ROOT), "--head", "HEAD"],
        ["compile-ecp", "--pd", str(ART / "pd_pkg.json"), "--pi", str(ART / "pi_pkg.json")],
        ["compile-tqaep", "--pi", str(ART / "pi_pkg.json"), "--ecp", str(ART / "ecp.json"),
         "--maker", "HERMES-MAKER", "--checker", "GLM-5.3-FLASH-AO-LANE",
         "--checker-receipt", "deleg_5a26d6d5/lane-C"],
        ["validate", "--bundle", str(ART / "bundle.json")],
        ["doctor"],
        # R-AUD-015 guard: never let the smoke write the delivered tree; the product
        # projection goes to a scratch dir so the real dist/web stays canonical.
        # R5-WO1: the destination resolver refuses a target outside every authorised root,
        # so the scratch surface must be authorised explicitly.
        # --allow-replace keeps the run idempotent across repeated invocations
        # (the scratch target survives from a prior run).
        ["project", "--out", str(ART / "web_projection"), "--allow-root", str(ART),
         "--allow-replace"],
        # R5-WO3: exercise the new portable-bundle path (`--out` + `--allow-root`),
        # still exactly 13 commands. The product tree is never the target.
        ["export", "--out", str(ART / "export_bundle"), "--allow-root", str(ART),
         "--allow-replace"],
        ["diff", "--a", str(ART / "claim_ceiling.json"), "--b", str(ART / "claim_ceiling.json")],
        ["repair", "--subject", "PI-PKG", "--scope", "src/**", "--maker", "HERMES-MAKER",
         "--authorized-root", str(ROOT)],
    ]
    receipts = []
    # Phase 1 = the commands whose OUTPUT the rest of the chain consumes. `intake` returns the
    # IntentCard, but it has no `--out` verb and the plan used to leave it in the captured payload
    # while `compile-pi` read the CHECKED-IN .hgk/artifacts/s1/intent_card.json. That committed card
    # names its source as a developer-machine absolute path ("C:\\Projects\\Agent_Workspace\\PIPD"),
    # which exists on the author's Windows box and on no other host, so compile-pi passed locally
    # and failed on hosted Linux with INTAKE_INVALID: cannot read clause source (S4R3-F001). The
    # smoke now persists the card THIS run produced and every downstream verb reads that.
    head = plan[:3]
    receipts += [run(p) for p in head]
    produced_card = receipts[1]["payload"]
    if isinstance(produced_card, dict) and produced_card.get("schema_version") == "IntentCard@1":
        (ART / "intent_card.json").write_text(
            json.dumps(produced_card, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    receipts += [run(p) for p in plan[3:]]
    reds = [r for r in receipts if r["exit"] != 0]
    summary = {"schema": "PIPD-CLI-SMOKE/1", "commands_run": len(receipts),
               "expected": 13, "nonzero_exit": len(reds),
               "verdicts": {r["args"][0]: r["payload"].get("verdict", "n/a") for r in receipts},
               "reds": reds, "receipts": receipts}
    (OUT / "CLI_SMOKE.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    print(json.dumps({k: summary[k] for k in ("commands_run", "expected", "nonzero_exit", "verdicts")},
                     ensure_ascii=False, indent=1))
    return 0 if len(receipts) == 13 and not reds else 2


if __name__ == "__main__":
    raise SystemExit(main())
