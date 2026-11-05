#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產生 LANE_REPORT.json：對 lane 內每個交付物算 sha256，並把真實命令/退出碼、
counts、holds、known_limits 寫成機器可讀報告。不重跑任何步驟、不改任何交付物。
"""

import hashlib
import json
import os
import re

LANE_DIR = os.path.dirname(os.path.abspath(__file__))
REAL_ROOT = ("C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
             "Semantic World OS Fabric/FHS／FHS-MSC／SBL/FHS/PIPD-LS-PKG/定案/W0/"
             "FHS_PIPD-LS-PKG_W0_R4C")

DELIVERABLES = [
    ("authority_router.py", "CLI 權威分流器：--source-root/--out，五類分類 + typed HOLD"),
    ("out/AUTHORITY_ROUTING.json", "31 源逐筆分類 + 統計 + holds"),
    ("out/AUTHORITY_ROUTING.md", "人類可讀表（每列 source_id/class/evidence_field/reason_code）+ HOLD 表"),
    ("tests/test_authority_router.py", "unittest：POS 真實來源 31 筆 + 5 條 NEG + 閘門單元"),
    ("tests/make_fixtures.py", "NEG 合成 fixture 產生器（可重跑）"),
    ("tests/UNITTEST_RAW.log", "unittest 真實輸出"),
    ("make_lane_report.py", "本報告產生器（對交付物算 sha256、抄錄命令與退出碼）"),
    ("tests/fixtures/neg1_mirror_as_authority/repository-map.json", "NEG-1 mirror-as-authority fixture"),
    ("tests/fixtures/neg1_mirror_as_authority/SOURCE31_PHYSICAL_IDENTITY.json", "NEG-1 來源根"),
    ("tests/fixtures/neg2_skill_as_permit/PLUGIN_USAGE_AND_GHP01.json", "NEG-2 skill-as-permit fixture"),
    ("tests/fixtures/neg2_skill_as_permit/SOURCE31_PHYSICAL_IDENTITY.json", "NEG-2 來源根"),
    ("tests/fixtures/neg3_dual_canonical/SOURCE31_PHYSICAL_IDENTITY.json", "NEG-3 dual canonical fixture"),
    ("tests/fixtures/neg4_scope_unbound/SOURCE31_PHYSICAL_IDENTITY.json", "NEG-4 scope missing fixture"),
    ("tests/fixtures/neg5_profile_role_conflated/SOURCE31_PHYSICAL_IDENTITY.json", "NEG-5 profile/role conflation fixture"),
]

COMMANDS = [
    {
        "cmd": 'python tests/make_fixtures.py',
        "cwd": "lanes/wp01",
        "exit_code": 0,
        "note": "產生 5 個合成 NEG 來源根",
    },
    {
        "cmd": ('python authority_router.py --source-root "%s" --out out' % REAL_ROOT),
        "cwd": "lanes/wp01",
        "exit_code": 0,
        "note": "對真實 R4C 來源根跑到 out/AUTHORITY_ROUTING.{json,md}",
    },
    {
        "cmd": 'python -m unittest discover -s tests -p "test_*.py" -v > tests/UNITTEST_RAW.log 2>&1',
        "cwd": "lanes/wp01",
        "exit_code": 0,
        "note": "25 tests, OK（POS 13 + NEG 5 + 閘門 3 + R1/R2/R3 單元 4）",
    },
]

KNOWN_LIMITS = [
    "R4（dual canonical）與 R6（profile/role/worker 混用）在真實來源 0 觸發：R4C 語料無重複 canonical 宣告，"
    "也無任何檔案宣告 actor_binding；兩條規則的存在性由合成 fixture（neg3/neg5）證明，非由真實來源證明。",
    "REPO_PINS 37 筆的 authority_class 由 repo/path 角色規則推導（來源檔只給 sha256 與 runtime_binding，"
    "未逐檔宣告 authority class）；evidence_field 指向 pin 的 sha256 欄位，class 屬推導值。",
    "CASE393_REGISTRY.json（393 案）與 ORACLE96_CONTRACTS.json（96 案）欄位集合不同（CASE393 無 "
    "expected_first_fail / source_id 欄），故本 lane 不做跨檔契約一致性判定，避免把 schema 差異誤判為權威衝突。",
    "NAV mirror 讀回與 ref blob 不一致：fabric_repository-map.json 1535B/git-blob c668fff4… vs ref "
    "b623b7b7…/1536B；Fabric INTEGRATION/FHS/README.md 5403B vs 5321B（SBL integrations/pipd/README.md "
    "39146B 完全相符，故非全域換行正規化）。已轉 HOLD H-AUTH-R4C-002；R1 的 effect_permission 出處因此"
    "僅限讀回內容而非 ref blob。閘門 fail-closed，未因此放寬任何判定。",
    "31 份 SOURCE31 原件的 currentness 仍為 ORIGINAL_READER_CURRENTNESS_HOLD（31/31），本 lane 未解；"
    "僅確認 manifest 的 physical_identity=PASS 與 sha256 欄位存在。",
    "canonical_compiler=NOT_RUN、host_loaded=NOT_OBSERVED（PLUGIN_USAGE_AND_GHP01.json），本輪無 canonical "
    "編譯與 host load 收據 → HOLD H-AUTH-R4C-003；未宣稱任何 Native/受保護 Checker 結果。",
    "無網路：未比對 GitHub 線上內容；mirror 的 ref blob 只依 REPOS_RECHECK.json 的本地 ref 讀回值。",
    "本 lane 只讀 JSON 宣告欄位，不解析正文語意；正文層的權威主張（.md 內文）不在判定範圍。",
    "未逐筆 stat 31 份原件的實體路徑（沿用 manifest 宣告 + UPSTREAM_IDENTITY 先前讀回），"
    "僅對 37 個 pin 的 offline_path 逐一算 sha256 並全數相符。",
]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    routing = json.load(open(os.path.join(LANE_DIR, "out", "AUTHORITY_ROUTING.json"),
                             encoding="utf-8"))
    stats = routing["statistics"]
    log = open(os.path.join(LANE_DIR, "tests", "UNITTEST_RAW.log"), encoding="utf-8").read()
    m = re.search(r"Ran (\d+) tests", log)
    tests_run = int(m.group(1)) if m else None
    tests_ok = log.rstrip().endswith("OK")

    deliverables = []
    for rel, role in DELIVERABLES:
        path = os.path.join(LANE_DIR, rel)
        deliverables.append({
            "path": rel,
            "role": role,
            "bytes": os.path.getsize(path),
            "sha256": sha256(path),
        })

    report = {
        "lane": "WP-FHS-01",
        "lane_id": "WP-FHS-01-AUTHORITY-ROUTER",
        "lane_dir": LANE_DIR,
        "round": "FHS_W0_R4C_FULL_IMPLEMENTATION_20261105_0305",
        "source_root": REAL_ROOT,
        "deliverables": deliverables,
        "deliverables_self": {
            "path": "LANE_REPORT.json",
            "role": "本報告；依設計不自算自身 sha256（避免自指）",
            "sha256": None,
        },
        "commands": COMMANDS,
        "tests": {
            "framework": "unittest (stdlib)",
            "raw_log": "tests/UNITTEST_RAW.log",
            "tests_run": tests_run,
            "result": "OK" if tests_ok else "FAILED",
            "pos": 13,
            "neg": 5,
            "unit": 7,
            "neg_codes": {
                "neg1_mirror_as_authority": "AUTHORITY_MIRROR_NOT_WRITABLE",
                "neg2_skill_as_permit": "SKILL_NOT_PERMIT",
                "neg3_dual_canonical": "AUTHORITY_CONFLICT_DUAL_CANONICAL",
                "neg4_scope_unbound": "AUTHORITY_SCOPE_UNBOUND",
                "neg5_profile_role_conflated": "PROFILE_ROLE_CONFLATED",
            },
        },
        "counts": {
            "entries_total": stats["total_entries"],
            "by_class": stats["by_class"],
            "by_group": stats["by_group"],
            "source31_declared": stats["source31_declared"],
            "source31_routed": stats["source31_routed"],
            "entries_without_evidence_field": stats["entries_without_evidence_field"],
            "may_authorize_write_true": stats["may_authorize_write_true"],
            "may_mint_permit_true": stats["may_mint_permit_true"],
            "holds_total": stats["holds_total"],
            "holds_by_code": stats["holds_by_code"],
            "rules_implemented": 9,
            "rules_required": 6,
        },
        "holds": [
            {
                "hold_id": h["hold_id"],
                "code": h["code"],
                "reason": h["reason"],
                "owner": h["owner"],
                "required_raw": h["required_raw"],
                "resume_predicate": h["resume_predicate"],
                "source_ids": h["source_ids"],
            }
            for h in routing["holds"]
        ],
        "claim_ceiling": "AUTHOR_LOCAL_TEST",
        "non_claims": routing["non_claims"],
        "known_limits": KNOWN_LIMITS,
    }
    out = os.path.join(LANE_DIR, "LANE_REPORT.json")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("wrote %s (%d deliverables, tests_run=%s ok=%s, holds=%d)"
          % (out, len(deliverables), tests_run, tests_ok, stats["holds_total"]))


if __name__ == "__main__":
    main()
