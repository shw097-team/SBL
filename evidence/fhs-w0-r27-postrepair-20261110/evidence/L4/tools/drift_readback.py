#!/usr/bin/env python3
"""Read-only harness: run the repo's OWN drift reader (hg_kseos.lane_policy.check_drift)
against a given repo root and dump the findings as JSON. No writes to the repo.

Usage: python drift_readback.py <repo_root> <out_json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2])
sys.path.insert(0, str(root / "src"))
from hg_kseos import lane_policy as lp  # noqa: E402

registry = lp.load_registry(root / "config" / "lane-routing-registry.yaml")
findings = lp.check_drift(root / "config" / "lane-routing-registry.yaml", root=root)
fatal = [f for f in findings if f.get("severity") == "error"]
payload = {
    "schema": "L4.DriftReadback/1",
    "reader": "hg_kseos.lane_policy.check_drift (repo's own, unmodified)",
    "root": str(root),
    "registry_epoch": lp.registry_epoch(registry),
    "findings_total": len(findings),
    "findings_fatal": len(fatal),
    "fatal_codes": sorted({f["code"] for f in fatal}),
    "fatal_ids": sorted({f["id"] for f in fatal}),
    "drift_is_fatal": lp.drift_is_fatal(findings),
    "findings": findings,
}
out.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps({k: payload[k] for k in ("registry_epoch", "findings_total", "findings_fatal",
                                          "fatal_codes", "fatal_ids", "drift_is_fatal")},
                 ensure_ascii=False))
