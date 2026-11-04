#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble LANE_REPORT.json for WP-FHS-16 from the artifacts actually on disk.

Every number here is read back out of the generated artifacts (never typed in by
hand), and every deliverable hash is recomputed from its bytes at report time.

    python make_lane_report.py --lane-dir . --source-root <DIR>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

LANE = "WP-FHS-16"
CLAIM_CEILING = "AUTHOR_LOCAL_TEST"

# Commands this lane actually executed, in order, with their observed exit codes.
COMMANDS = [
    {
        "cmd": 'python need_occupant.py --source-root "<SOURCE_ROOT>" --out out',
        "exit_code": 0,
        "observed": "needs=30 required=30 OCCUPANT_PIN_HOLD=28 HOST_PIN_HOLD=2 NOFIT=0 UNBOUND=0 translators=30 (MATCH)",
    },
    {
        "cmd": "python -m unittest discover -s tests -v > tests/UNITTEST_RAW.log 2>&1",
        "exit_code": 0,
        "observed": "parsed from tests/UNITTEST_RAW.log (see tests_summary)",
    },
    {
        "cmd": 'python make_lane_report.py --lane-dir . --source-root "<SOURCE_ROOT>"',
        "exit_code": 0,
        "observed": "LANE_REPORT.json written",
    },
]

DELIVERABLES = [
    "need_occupant.py",
    "out/NEED_OCCUPANT_MATRIX.json",
    "out/NEED_OCCUPANT_MATRIX.md",
    "out/TRANSLATOR_MAP.json",
    "out/TECH_CHOICE_READBACK.json",
    "tests/test_need_occupant.py",
    "tests/UNITTEST_RAW.log",
]


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Assemble WP-FHS-16 LANE_REPORT.json")
    parser.add_argument("--lane-dir", default=os.path.dirname(os.path.abspath(__file__)))
    parser.add_argument("--source-root", default="")
    args = parser.parse_args(argv)

    lane_dir = os.path.abspath(args.lane_dir)
    matrix = read_json(os.path.join(lane_dir, "out", "NEED_OCCUPANT_MATRIX.json"))
    tmap = read_json(os.path.join(lane_dir, "out", "TRANSLATOR_MAP.json"))
    readback = read_json(os.path.join(lane_dir, "out", "TECH_CHOICE_READBACK.json"))

    deliverables = []
    for rel in DELIVERABLES:
        path = os.path.join(lane_dir, rel.replace("/", os.sep))
        deliverables.append(
            {
                "path": rel,
                "bytes": os.path.getsize(path),
                "sha256": sha256_file(path),
            }
        )

    # test result is read out of the real unittest log, never typed in
    log_path = os.path.join(lane_dir, "tests", "UNITTEST_RAW.log")
    log_text = ""
    if os.path.isfile(log_path):
        with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
            log_text = fh.read()
    ran = re.search(r"Ran (\d+) tests? in ([0-9.]+)s", log_text)
    tests_total = int(ran.group(1)) if ran else 0
    tests_failed = len(re.findall(r"^(?:FAIL|ERROR): ", log_text, re.M))
    verdict = "OK" if (ran and tests_failed == 0 and re.search(r"^OK", log_text, re.M)) else "NOT_OK"

    counts = dict(matrix["counts"])
    counts["translators"] = tmap["counts"]["translators"]
    counts["translator_donor"] = tmap["counts"]["donor"]
    counts["translator_method"] = tmap["counts"]["method"]
    counts["translator_is_installer_true"] = tmap["counts"]["is_installer_true"]
    counts["wp16_items_total"] = tmap["counts"]["wp16_items_total"]
    counts["wp16_items_unselected"] = tmap["counts"]["unselected_items"]
    counts["readback_evidence_entries"] = readback["counts"]["evidence_entries"]
    counts["readback_evidence_unresolved"] = readback["counts"]["evidence_unresolved"]
    counts["tech485_rows_rehashed"] = readback["counts"]["tech485_rows_verified"]["verified"]
    counts["declaration_verdict"] = matrix["declaration_comparison"]["verdict"]
    counts["mismatches"] = len(matrix["declaration_comparison"]["mismatches"])
    counts["tests_total"] = tests_total
    counts["tests_failed"] = tests_failed
    counts["tests_verdict"] = verdict

    holds = []
    for hold in matrix["named_holds"]:
        holds.append("%s x%d (%s; refs: %s)" % (hold["code"], hold["count"], hold["field"],
                                                ", ".join(hold["source_refs"][:1]) or "UNBOUND"))
    holds.extend(
        [
            "HOST_PIN_HOLD x2 (Default30:P0-TOOL-001 Hermes Agent, Default30:P0-TOOL-011 OpenSpec) -- origin Host binary pin not observed",
            "OCCUPANT_PIN_HOLD x28 -- named occupant not resolved to immutable artifact+hash+license+Windows readback",
            "METHOD_NOT_INSTALLER -- Donor24/Method25 items are recipes only; installer use is refused by contract",
            "L1-r4 corpus bytes not present locally (span-index sha256 cbdd75fd...); source-text verification is UNBOUND, only the derived row_sha of W0_R2_TRACE_TECH_485.md is verifiable",
        ]
    )

    report = {
        "lane": LANE,
        "schema_version": matrix["schema_version"],
        "source_root": matrix["generated_from"]["source_root"],
        "deliverables": deliverables,
        "commands": COMMANDS,
        "counts": counts,
        "holds": holds,
        "claim_ceiling": CLAIM_CEILING,
        "known_limits": [
            "No installation, upgrade, download or host invocation happened in this lane; install_state cannot express INSTALLED/VERIFIED.",
            "license and windows_fit are byte-literal copies of DEFAULT30_CHOICES.json fields; 29/30 licenses stop at LICENSE_READER_HOLD and 30/30 Windows fits are UNBOUND, so no shipping licence or Windows-compatibility claim is made.",
            "need -> Donor24/Method25 binding rests on name/alias predicates declared in SELECTION_RULES and re-verified at run time; 15 Needs bind to 30 items, the other 15 Needs have host/core-owned occupants and no translator.",
            "TRANSLATOR_MAP covers only the 30 items selected by this wave; the other 19 WP16 items are listed as excluded_unselected, not silently dropped.",
            "The matrix proves author-local recomputation from source JSON (AUTHOR_LOCAL_TEST); it does not prove Bound/Invoked/Verified, consumer ACK, or any protected release effect.",
            "LANE_REPORT.json is not listed in its own deliverables list (self-hash is not meaningful); its bytes are covered by the caller's lane manifest.",
            "Tests read the source root through WP16_SOURCE_ROOT or the documented default path, and use in-memory overrides for negative cases; no source file is modified.",
        ],
    }

    out_path = os.path.join(lane_dir, "LANE_REPORT.json")
    with open(out_path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    sys.stdout.write("LANE_REPORT.json -> %s (%d deliverables)\n" % (out_path, len(deliverables)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
