#!/usr/bin/env python3
"""G-S3-WEB gate — FW-05 / R-AUD-003 / R-AUD-015, real semantic checks.

The Web denominator is EXACTLY the five PIPD semantic documents:
    PIPD_BOOTSTRAP.md, PIPD_CANONICAL_CORE.md, PIPD_ROUTER_PROFILES.md,
    PIPD_ARTIFACT_SCHEMAS.md, PIPD_EVAL_HANDOFF.md
each carrying its source objects (object id / schema / schema version), a source
hash, a CapabilityLoss record and a NACK record, with content derived from the
canonical PIPD objects and profiles — not free text.

The site UI five files (index.html, app.js, styles.css, manifest.webmanifest,
README.md) are OPTIONAL_SITE_UI: explicitly excluded from the Web denominator and
incapable of passing this gate (R-AUD-003: the old gate passed on exactly those
five files).

Modes:
  default    regenerate the projection from the canonical sources, then check.
  --strict   check the delivered tree exactly as-is (no regeneration) and refuse
             every mutation with a typed reason:
               MUT-WEB-WRONGSET     wrong web set (UI files as the pack, missing
                                    or extra documents)
               MUT-EMPTY-PAYLOAD    empty document / empty record list
               MUT-MISSING-FIELD    missing meta field / record field
               MUT-SCOPE-WIDENING   scope widened beyond `dist/web/**`
               MUT-STALE-SOURCE     artifact does not match the live sources
               MUT-NOT-DERIVED      free-text or tampered document content
               MUT-WEB-WRONGSET     OPTIONAL_SITE_UI leaked into the denominator
Exit code 0 only on PASS. S5/S6 are NOT authorised: nothing here claims a live
HGK/GENIE integration PASS (fixture/mock contracts only).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT_DEFAULT = ROOT / "dist" / "web"
RECEIPT_DEFAULT = ROOT / ".hgk" / "artifacts" / "s3" / "WEB_PACK.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true",
                    help="audit the tree as-is; refuse every mutation with a typed reason")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="projection surface directory")
    ap.add_argument("--receipt", default=str(RECEIPT_DEFAULT), help="receipt JSON path")
    args = ap.parse_args()

    from pipd_ls_sp import projection

    out = Path(args.out)
    if not args.strict:
        projection.project_surfaces(ROOT, out)
    result = projection.check_web_surface(ROOT, out)
    result["mode"] = "STRICT_CHECK_ONLY" if args.strict else "REGENERATE_THEN_CHECK"
    result["candidate_head"] = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True,
        text=True).stdout.strip()
    receipt = Path(args.receipt)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8",
                       newline="")
    print(json.dumps(result, ensure_ascii=False, indent=1))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
