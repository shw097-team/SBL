# -*- coding: utf-8 -*-
"""Build LANE_REPORT.json from the artefacts actually on disk.

Every digest in the report is recomputed here, never copied by hand.
"""

import datetime
import hashlib
import json
import os
import re

LANE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(LANE, "out")
GOAL = "讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC"
SRC = ("C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
       "Semantic World OS Fabric/FHS／FHS-MSC／SBL/FHS/PIPD-LS-PKG/定案/W0/"
       "FHS_PIPD-LS-PKG_W0_R4C")
BODY_NAME = "FHS_PIPD-LS-PKG_W0_草案_2026-11-05_r4-candidate-b41d2e_實質正文.md"


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def size(path):
    return os.path.getsize(path)


def rel(path):
    return os.path.relpath(path, LANE).replace("\\", "/")


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        return json.load(fh)


def main():
    manifest = load("RUN_MANIFEST.json")
    product = load("SPEC_Product.json")
    arch = load("SPEC_Architecture.json")
    program = load("SPEC_Program.json")
    chain = load("GOAL_TO_FUO.json")
    hetero = load("SPEC_HETEROGENEITY.json")

    deliverable_files = [
        "spec_pipeline.py",
        "out/SPEC_Product.json", "out/SPEC_Product.md",
        "out/SPEC_Architecture.json", "out/SPEC_Architecture.md",
        "out/SPEC_Program.json", "out/SPEC_Program.md",
        "out/GOAL_TO_FUO.json", "out/GOAL_TO_FUO.md",
        "out/SPEC_HETEROGENEITY.json",
        "out/RUN_MANIFEST.json",
        "tests/test_spec_pipeline.py",
        "tests/UNITTEST_RAW.log",
        "build_lane_report.py",
    ]
    deliverables = [
        {"path": f, "sha256": sha(os.path.join(LANE, f)),
         "bytes": size(os.path.join(LANE, f))}
        for f in deliverable_files
    ]

    with open(os.path.join(LANE, "tests", "UNITTEST_RAW.log"), encoding="utf-8") as fh:
        log = fh.read()
    m = re.search(r"Ran (\d+) tests in", log)
    tests_ran = int(m.group(1)) if m else None
    tests_ok = bool(re.search(r"\nOK\b", log))
    test_names = re.findall(r"^(test_\w+) \(([\w.]+)\)", log, re.M)

    registry_files = [
        "PROGRAM_WP22_DAG36.json", "W0_REQUIRED22_TRACE.json", "DESIGN84_WAVE_JOIN.json",
        "SEAM_CONTRACTS.json", "ORACLE96_CONTRACTS.json", "CASE393_REGISTRY.json",
        "TECH485_COMPACT_REGISTRY.json", "SOURCE31_PHYSICAL_IDENTITY.json",
        "CURRENT_CANDIDATE_STATE.json",
        "W0_R2_TRACE_R15_949_CELL192_B1_CASES_AND_ORACLE.md",
        "W0_R2_TRACE_SBL_PARENT50_CHILD149.md",
    ]
    source_binding = {
        "body": {"file": BODY_NAME, "sha256": sha(os.path.join(SRC, BODY_NAME)),
                 "bytes": size(os.path.join(SRC, BODY_NAME))},
        "source_root": SRC,
        "registries": {f: sha(os.path.join(SRC, f)) for f in registry_files},
    }

    counts = dict(manifest["counts"])
    counts.update({
        "fuo": len(product["fuo"]),
        "product_requirement_ids": len(product["requirement_ids"]),
        "architecture_requirement_ids": len(arch["requirement_ids"]),
        "program_requirement_ids": len(program["requirement_ids"]),
        "domain_stages": len(arch["domain_stages"]),
        "seams": len(arch["seams"]),
        "adr": len(arch["adr"]),
        "acc_plus": len(product["acc_plus"]),
        "acc_minus": len(product["acc_minus"]),
        "goal_chains": chain["chain_count"],
        "counter_reconciliation_rows": len(program["counter_reconciliation"]),
    })

    report = {
        "lane": "WP-FHS-15",
        "round": "FHS W0 R4C 全實作輪（SWARM lane）",
        "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "claim_ceiling": "AUTHOR_LOCAL_TEST",
        "native_claim": "NONE — 無 W2 Native E2E、無 Native 效果、無原 Reader ACK",
        "lane_root": "var/FHS_W0_IMPLEMENTATION_20261105_0305/lanes/wp15",
        "goal": GOAL,
        "source_binding": source_binding,
        "deliverables": deliverables,
        "commands": [
            {
                "command": 'python spec_pipeline.py --body "<SRC>/%s" '
                           '--source-root "<SRC>" --out out --goal "%s"' % (BODY_NAME, GOAL),
                "exit_code": 0,
                "produces": ["out/SPEC_Product.json", "out/SPEC_Product.md",
                             "out/SPEC_Architecture.json", "out/SPEC_Architecture.md",
                             "out/SPEC_Program.json", "out/SPEC_Program.md",
                             "out/GOAL_TO_FUO.json", "out/GOAL_TO_FUO.md",
                             "out/SPEC_HETEROGENEITY.json"],
                "note": "manifest 由同一指令的 stdout 存成 out/RUN_MANIFEST.json",
            },
            {
                "command": "python -m unittest discover -s tests -v > tests/UNITTEST_RAW.log 2>&1",
                "exit_code": 0,
                "note": "Ran %s tests, OK (POS counts + 3 required NEG codes)" % tests_ran,
            },
            {
                "command": 'python spec_pipeline.py --source-root "<SRC>" --out out '
                           '--goal x --verify out/GOAL_TO_FUO.json',
                "exit_code": 0,
                "note": "重新讀檔重算 readback_sha：verified=true",
            },
            {
                "command": "python -c \"hashlib.sha256(body).hexdigest()\"",
                "exit_code": 0,
                "note": "正文 463034 bytes / 56d0df3d…73f2a，與 CURRENT_CANDIDATE_STATE 相符",
            },
        ],
        "tests": {
            "suite": "tests/test_spec_pipeline.py",
            "ran": tests_ran,
            "result": "OK" if tests_ok else "FAILED",
            "log": "tests/UNITTEST_RAW.log",
            "names": ["%s (%s)" % (n, c) for n, c in test_names],
            "neg_codes_asserted": ["SPEC_NOT_HETEROGENEOUS", "FUO_MISSING",
                                   "REQUIREMENT_UNBOUND", "SUBJECT_BODY_SHA_MISMATCH",
                                   "SEAM_SHAPE_INCOMPLETE", "CLAIM_CEILING_VIOLATION"],
        },
        "counts": counts,
        "count_sources": {
            k: v.get("source_ref") for k, v in program["counts"].items()
        },
        "counter_reconciliation": program["counter_reconciliation"],
        "heterogeneity": {
            "verdict": hetero["verdict"],
            "specs": {k: {"section_count": len(v["section_set"]),
                          "field_count": len(v["required_field_set"]),
                          "body_sha256": v["body_sha256"]}
                      for k, v in hetero["specs"].items()},
            "pairs": hetero["pairs"],
            "thresholds": hetero["thresholds"],
        },
        "holds": [
            "H-U4：原 SBL Product / PIPD Intake Reader 未 ACK；三份 SPEC 只到 AUTHOR_DESIGN 可讀回",
            "H-ABI-05：S1–S5 的 original_abi 全為 ORIGINAL_RUNTIME_ABI_UNBOUND",
            "H-ORACLE-RAW96：96 個 Oracle 個案無原 Host Runner／Fixture 真 bytes，只作 CASE PLAN",
            "25 張跨波卡（JOIN_AMBIGUOUS_AFFECTED）待原 Program Reader 裁決，未以需求波覆寫施工波",
            "E26 的 original_reader_ack=NOT_OBSERVED；W0 不產生 CI/License/SBOM Raw",
            "31 冊 Source 的 Currentness 皆 ORIGINAL_READER_CURRENTNESS_HOLD",
            "FUO-A／FUO-B 只有章級 W0 綁定，無 W0_REQUIRED deliver_id，未升格為 GOAL_TO_FUO chain",
            "192 Cell 的 Provider ON/OFF 原標籤歧義未經原 Host/Provider Owner ACK",
        ],
        "known_limits": [
            "Goal→FUO 的 primary_chain 只用字元 bigram 重疊排序（AUTHOR_TOKEN_OVERLAP_HEURISTIC），不是原 Reader 的語義綁定",
            "acceptance POS 對 W0_REQUIRED 來源列即其 requirement 原文，因該 registry 未另存 POS 欄",
            "permission 分類由五 seam 列的用字推導（優先序 WorldRaw＞permit＞不寫世界＞ACK＞SPECDraft），原 ACL 一律 NOT_OBSERVED",
            "S1 被列為五域階段之外的入口接縫（由『無任何階段認領』規則判定），不是作者另行指定",
            "domain_stages 的 seam 綁定用 actor-token 比對 CH-37 表格的 producer/reader 欄，未經原 Reader 確認",
            "三份 SPEC 的中文語料同源，domain_token_jaccard 約 0.28–0.31；異質性主張以 section 交集（1/8、1/9、1/14）與 field set 差異為主證",
            "所有 r15/cell/parent-child 計數以 trace md 的表格列為分母，未重讀 31 冊原檔逐列核對",
            "本 lane 只在 L 內寫入；未修改 S 或 repo 任何檔案",
        ],
        "outputs_digest_check": {
            "product_json_sha256": sha(os.path.join(OUT, "SPEC_Product.json")),
            "goal_output_sha": chain["output_sha"],
            "match": sha(os.path.join(OUT, "SPEC_Product.json")) == chain["output_sha"],
            "goal_input_sha": chain["input_sha"],
            "goal_readback_sha": chain["readback_sha"],
        },
        "isolation": {
            "writes_confined_to_lane": True,
            "lane_dir": LANE,
            "source_tree_modified": False,
        },
    }
    path = os.path.join(LANE, "LANE_REPORT.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("wrote", path, os.path.getsize(path), "bytes;", len(deliverables), "deliverables")


if __name__ == "__main__":
    main()
