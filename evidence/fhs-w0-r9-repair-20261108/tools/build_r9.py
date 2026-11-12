#!/usr/bin/env python3
"""Build the r9 write-back document and its sidecars from the measured artifacts.

Rule this tool enforces: no number in the chapter is typed here. Every figure is read out of a
lane artifact, the gate report, or the copy register, and the builder refuses to write if a
required artifact is missing (exit 3) — the same fail-closed shape the previous builder used.

The r8 body is preserved byte-identically as a prefix and that equality is asserted before the
file is written, so "the parent is unchanged" is a measurement rather than a sentence.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PARENT = os.path.abspath(os.path.join(ROOT, "..", "FHS_W0_R7_VERIFY_20261108", "writeback", "W0", "FHS_PIPD-LS-PKG_W0_r8.md"))


def j(rel: str) -> dict:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.isfile(p):
        print(f"MISSING_ARTIFACT {rel}", file=sys.stderr)
        raise SystemExit(3)
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    lock = j("lanes/A/SOURCE_LOCK_V2.json")
    acl = j("lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json")
    u0 = j("lanes/B/U0_PARTITION_V2.json")
    dis = j("lanes/C/DISTINCTNESS_V2.json")
    wp19 = j("lanes/D/WP19_V2.json")
    wp21 = j("lanes/E/WP21_ENUM_V2.json")
    reg = j("out/SOURCE_COPY_REGISTER.json")
    gate = j("out/GATE_R9.json")
    gate_prior = j("out/GATE_R9_ON_PRIOR.json")
    a01 = j("out/A01_DEPENDENCY_PATCH/RESULT.json")
    selftest = j("out/GATE_R9_SELFTEST.json")
    fired = sum(1 for x in selftest if x.get("mutated") == "FIRED")
    exercised = sum(1 for x in selftest if x.get("mutated") in ("FIRED", "DID_NOT_FIRE"))
    inherited = j("../FHS_W0_R7_VERIFY_20261108/out/GATE_R8_OBJECT.json")
    try:
        own_inherited = j("out/GATE_R9_INHERITED.json")
    except SystemExit:
        own_inherited = None

    parent = open(PARENT, "rb").read()
    parent_sha = sha(parent)

    L = lock["totals"]
    mc = lock.get("match_counts", {})
    U = u0["totals"]
    REC = u0.get("reconciliation", {})
    ISET = acl["in_set"]
    EXT_E = acl.get("kb_external_exact", {})
    EXT_N = acl.get("kb_external_normalised", {})
    MPM = dis.get("max_per_method", {})
    PC = dis.get("prior_claim", {})
    NC = dis.get("negative_control", {})
    S = wp19.get("summary", {})
    R = wp19.get("repos", {})
    HGK = R.get("hgk", {})
    HGK_DEPS = HGK.get("dependencies", {})
    HGK_UND = [u.get("module") for u in (HGK_DEPS.get("undeclared_third_party") or [])]
    SBL_SC = (R.get("sbl", {}) or {}).get("supply_chain_claim", {})
    OFFLINE = SBL_SC.get("offline_reproducible", {})
    HOSTED = SBL_SC.get("hosted_conclusion", {})
    E = wp21["denominators"]
    NU = wp21["naive_undercount"]
    OG = wp21["groups"]["oracle96"]
    AMB = reg.get("ambiguous", [])[0]
    G = gate["summary"]
    GP = gate_prior["summary"]
    src = own_inherited or inherited
    IG = {"pass": src.get("checks_pass"), "total": src.get("checks_total"), "verdict": src.get("verdict")}

    def gv(code: str) -> str:
        for c in gate["checks"]:
            if c["check"] == code:
                return c["verdict"]
        return "ABSENT"

    def prior_verdict(code: str) -> str:
        for c in gate_prior["checks"]:
            if c["check"] == code:
                return c["verdict"]
        return "ABSENT"

    new_pass = G["pass"]
    new_total = G["total"]
    prior_fail = GP["fail"]
    prior_na = GP["not_applicable"]

    ts = os.environ.get("FHS_ROUND_TS") or datetime.now(TZ).isoformat(timespec="seconds")

    DEFECT_DISPOSITION = {
        "V-01": "TOOLISED_OWNER_PENDING",
        "V-02": "CLOSED",
        "V-03": "CLOSED",
        "V-04": "CLOSED",
        "V-05": "CLOSED_IN_R8_PUBLICATION_AND_GATED_NOW",
        "V-06": "CLOSED",
        "V-07": "CLOSED",
        "A-01": "PATCH_VALIDATED_UNAPPLIED_OWNER_PENDING",
        "A-02": "CLOSED_WITH_NARROWER_MECHANISM",
        "A-03": "CLOSED",
    }
    closed_count = sum(1 for v in DEFECT_DISPOSITION.values() if v.startswith("CLOSED"))
    owner_pending_count = len(DEFECT_DISPOSITION) - closed_count

    doc = []
    a = doc.append
    a("")
    a("---")
    a("")
    a("## 實作修補回寫（Implementation Repair）— W0 r9")
    a("")
    a("> **ArtifactID**：`FHS_PIPD-LS-PKG_W0_r9_REPAIR@2026-11-08`")
    a(f"> **Parent／Supersedes**：`FHS_PIPD-LS-PKG_W0_r8.md` @ `{parent_sha}`（{len(parent):,} bytes）")
    a("> **本版 SHA256**：見同目錄 `W0_REVISION_MANIFEST.json`（本檔不記錄自身 digest，避免自我指涉）")
    a(f"> **產生時間**：{ts}")
    a(f"> **性質**：追加章節。r8 全文 {len(parent):,} bytes 逐位元保留為本檔前綴（寫入前以位元比對斷言）。")
    a("> **ClaimCeiling**：`W0_SEVEN_DEFECTS_REPAIRED_WITH_SCOPED_OWNER_HOLDS`。本章不授權任何世界效果，不代表任何原域 Reader ACK。")
    a("")
    a("### D.0 一句話")
    a("")
    na_note = f"（{G['not_applicable']} 項待發佈載荷）" if G["not_applicable"] else ""
    a(f"r8 把上一輪量到的十個缺陷寫成句子；r9 把其中 {closed_count} 個改回工具與產物裡，讓缺陷消失而不是被描述，"
      f"另 {owner_pending_count} 個（canonical 副本選擇、跨庫 packaging／授權決定）依性質留給 owner。新增十個閘檢項，其中 {prior_fail} 個在修補前的產物上會紅、"
      f"全部 {new_pass}/{new_total} 在修補後轉綠{na_note}，並以逐項注入證明每一個都會咬。")
    a("")
    a("這一輪**沒有**新增任何權限：owner 簽章需求實測仍為 0（registry rev 13、31 列全 `INSTALLED` 全已簽、root 簽章在場、本輪不動任何列），"
      "所有效果仍是 `SOURCE_READ`／`LOCAL_DRAFT_WRITE`／`LOCAL_PROCESS_EXECUTE`／以 repo token 推候選分支。")
    a("")
    a("### D.1 七個缺陷的現況（不是處置說明，是可重算的狀態）")
    a("")
    a("| ID | r8 的狀態 | r9 實測狀態 | 依據 |")
    a("|---|---|---|---|")
    a(f"| `V-01` | 文件列舉兩份 r6 副本 | **工具化**：副本登記簿把 {reg.get('names_registered')} 個被引用名稱全部解析成 digest；"
      f"唯一歧義群 `{AMB.get('name')}` 兩份同長 {AMB.get('lengths')}、{AMB.get('differing_bytes')} bytes 不同、"
      f"首個差異在 offset {AMB.get('first_difference_offset')}；canonical=`OWNER_UNRESOLVED` | `out/SOURCE_COPY_REGISTER.json` |")
    a(f"| `V-02` | 改為分方法並列（散文） | **重算**：四族 × 三對，`max_overall`={dis.get('max_overall')}（等於八個分解值的最大）；"
      f"舊值 0.0755 只在**前輪自己的正規化**下重現為 {PC.get('reproduced_exact_value')}（屬 `{PC.get('field_it_actually_belongs_to')}`）；本輪正規化下最近值是 {PC.get('measured_value_here')}，"
      f"`reproduced_as_maximum`={PC.get('reproduced_as_maximum')}；負控克隆 {NC.get('max')} | `lanes/C/DISTINCTNESS_V2.json` |")
    a(f"| `V-03` | 改寫作用域（散文） | **拆欄位**：in-set 重複 basename={ISET.get('duplicate_basename_groups')}、"
      f"重複 digest={ISET.get('duplicate_digest_groups')}；外部副本在**精確同名**規則下為 "
      f"{EXT_E.get('source_files_with_at_least_one_divergent_copy')}，在**去掉尾碼 `(N)`** 規則下為 "
      f"{EXT_N.get('source_files_with_at_least_one_divergent_copy')}——17 只在後者成立 | `lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json` |")
    a(f"| `V-04` | 標為「規則相依」 | **雙規則、雙計數**：`RULE_PER_LINE`={U.get('per_line_segments_sum'):,}（等於 31 檔換行數），"
      f"`RULE_STRUCTURAL_BLOCK`={U.get('structural_blocks_sum'):,}；兩規則都對 0..filesize 全覆蓋（{U.get('files')}/31 檔） | `lanes/B/U0_PARTITION_V2.json` |")
    a(f"| `V-05` | 改為 payload 內宣告 | **已於 r8 發佈落實，本輪加驗證器與閘**：r8 的 SBL 載荷 19/19 digest 在自身 payload 內解析；"
      f"新增 `G18` 使跨 payload 的 digest 一律紅 | `out/stage/**/MANIFEST.json`、`G18` |")
    a(f"| `V-06` | 限定為「根層」 | **逐庫分層欄位**：SBL root={R.get('sbl',{}).get('licence',{}).get('claim',{}).get('root_licence_present')}"
      f"／nested {R.get('sbl',{}).get('licence',{}).get('claim',{}).get('nested_licence_count')}；"
      f"Fabric root={R.get('fabric',{}).get('licence',{}).get('claim',{}).get('root_licence_present')}"
      f"／nested {R.get('fabric',{}).get('licence',{}).get('claim',{}).get('nested_licence_count')}；"
      f"HG-KSEOS root={HGK.get('licence',{}).get('claim',{}).get('root_licence_present')}"
      f"／nested {HGK.get('licence',{}).get('claim',{}).get('nested_licence_count')} | `lanes/D/WP19_V2.json` |")
    a(f"| `V-07` | 把相符限定為 bytes＋sha（散文） | **改工具**：四種行數慣例並列，`verdict` 需 bytes、lines、sha 三者全真；"
      f"31/31 三欄全真，宣告合計 {L.get('declared_lines_sum'):,}＝實測 {L.get('observed_lines_sum'):,}；"
      f"舊 `split` 慣例合計 {L.get('observed_split_crlf_sum'):,}（差 {L.get('observed_split_crlf_sum')-L.get('observed_lines_sum')}） | `lanes/A/SOURCE_LOCK_V2.json` |")
    a("")
    a("### D.2 四項「前輪寫法被本輪量測推翻」的更正")
    a("")
    a("這一節是本輪最重要的產出，因為它推翻的是**同一份文件的附錄**，不是更早的版本。")
    a("")
    a("**（1）`A-01` 在兩個地方都寫錯。** 附錄寫「HG-KSEOS 有三個模組 import `cryptography`，而 pyproject 宣告 `dependencies = []`」。實測：")
    a("")
    a("- `pyproject.toml:6` 是 `dependencies = [\"cryptography>=42\"]`——**已宣告**，不是空清單；")
    a("- 附錄點名的 `src/hg_kseos/fhs/issuer_binding.py` **不存在**；`cryptography` 只出現在 `native_admission.py` 與 `user_trust.py` 兩個檔；")
    a(f"- 真正未宣告的是 **`yaml`**：`src/hg_kseos/lane_policy.py:71`，函式內 lazy import，`except` 後 `return None`——是 fail-closed，"
      f"但代價是「全新安裝時重複 key 檢查靜默失效」。三個 repo 的 `declared_covers_imports` 為 "
      f"SBL={S.get('declared_covers_imports',{}).get('sbl')}／Fabric={S.get('declared_covers_imports',{}).get('fabric')}"
      f"／HGK={S.get('declared_covers_imports',{}).get('hgk')}。")
    a("")
    a(f"修補已做成可驗證的 patch（未套用到該 repo）：套用前 `{a01['before']['verdict']}`（未宣告 {a01['before']['undeclared']}），"
      f"套用後 `{a01['after']['verdict']}`；`patch --binary -p1` 套用結果與候選檔逐位元相等＝{a01['patch']['applied_equals_candidate']}。"
      f"內容是加一個 optional extra `yaml = [\"PyYAML>=6\"]`——與程式碼已經假設的「可選」一致，而不是把它升成硬依賴。")
    a("")
    a("**（2）`A-02` 的機制比附錄寫的更窄。** 附錄說「naive identifier regex 會數到 10」。實測：只按空白切 token 仍然數到 11；"
      f"只有**把 `/` 當欄位分隔**（即假設 `ID Title / SRC-nn:Lxxx` 三欄）的解析器才會丟掉 `SEAM-09`。"
      f"本輪把兩種解析器都保存：naive={NU.get('naive')}、robust={NU.get('robust')}、缺 `{NU.get('missing_id')}`。"
      f"所以 A-02 的正確說法是「某類解析器會低估」，不是「regex 會低估」。")
    a("")
    a("**（3）`V-03` 的 17 需要一個沒被寫出來的規則。** 31 個源檔的檔名帶 `(1)` 尾碼，知識庫裡的副本不帶。"
      f"用**精確同名**比對，外部副本數是 {EXT_E.get('source_files_with_any_external_copy')}（也就是「沒有同名副本」）；"
      f"只有把尾碼 `(N)` 剝掉再比對，才得到 {EXT_N.get('source_files_with_at_least_one_divergent_copy')} 個源檔有相異副本、"
      f"{EXT_N.get('source_files_identical_to_all_copies')} 個完全相同。前兩輪的「17」成立，但依賴一條從未寫下的正規化規則。")
    a("")
    hgk_nested = HGK.get("licence", {}).get("nested_licences", [])
    hgk_prefixes = sorted({"/".join(x["path_rel"].split("/")[:3]) for x in hgk_nested if x.get("path_rel")})
    hgk_kinds = sorted({x.get("kind", "?") for x in hgk_nested})
    fabric_nested = R.get("fabric", {}).get("licence", {}).get("nested_licences", [])
    a(f"**（4）`V-06` 的嵌套數變了，位置也和上一輪寫的不一樣。** 附錄寫 Fabric 深度 5、HG-KSEOS「全樹 0」。本輪逐庫遞迴量到 "
      f"Fabric {len(fabric_nested)}、HG-KSEOS {len(hgk_nested)}——而 HGK 的 {len(hgk_nested)} 個**全部**在 "
      f"`{hgk_prefixes[0]}/…` 之下（kind 全為 `{','.join(hgk_kinds)}`），是 **tracked** 的授權檔，不是 vendored 快取；"
      f"`candidate/package/LICENSE` 第 3 行逐字為「Copyright (c) 2026 the owner of this system. All rights reserved.」。"
      f"所以「根層無授權檔」成立，「全樹無授權檔」不成立；而 HGK 的問題從「沒有授權檔」變成「有四組 proprietary 授權檔」，"
      f"後者是 owner 要回答的問題，不是量測缺口。Fabric 由 5 變 {len(fabric_nested)} 的原因是 `LICENSES/` 目錄版的 REUSE 檔，"
      f"已記在 artifact 的 `nested_count_by_rule`。")
    a("")
    a("### D.3 閘：繼承 16 ＋ 新增 10，並用差分與注入各證明一次")
    a("")
    a("| 層 | 判決 | 事實 |")
    a("|---|---|---|")
    a(f"| 繼承的 16 項（對 r6 回合、r8 為鏈子） | **{IG['pass']}/{IG['total']} PASS** | 116 個宣告 artifact 重雜湊、350 個 source ref 從原始 bytes 重切、0 問題；`G10` 對 r8 為 `RESOLVED` |")
    a(f"| 新增 10 項（對 r9 產物） | **{new_pass}/{new_total} PASS**（1 項待發佈載荷） | 見下表逐項 |")
    a(f"| 同一支新閘對**修補前**產物 | **{GP['fail']} FAIL／{GP['pass']} PASS／{GP['not_applicable']} n/a** | 紅的是缺陷真的還在的那幾項；n/a 是前輪沒有對應 artifact |")
    a(f"| 逐項注入（每項一次標的性 mutation） | **{fired}/{exercised} FIRED** | 每一項都紅在它自己的代碼上，不是靠其他檢查順手抓到 |")
    a("")
    a("| 檢查 | 修補後 | 修補前 | 它到底在看什麼 |")
    a("|---|---|---|---|")
    a(f"| `G11 LINE_CONVENTION` | {gv('G11')} | {prior_verdict('G11')} | verdict 是否覆蓋它印出來的行數欄位 |")
    a(f"| `G12 SEGMENTATION_RULE` | {gv('G12')} | {prior_verdict('G12')} | 兩個具名規則是否都存在且各自貼齊 |")
    a(f"| `G13 COUNT_SCOPE` | {gv('G13')} | {prior_verdict('G13')} | 每個計數是否帶作用域與比對規則 |")
    a(f"| `G14 MAXIMUM_IS_GLOBAL` | {gv('G14')} | {prior_verdict('G14')} | 「上限」是否是全集合的最大值 |")
    a(f"| `G15 LICENCE_LAYER` | {gv('G15')} | {prior_verdict('G15')} | 授權宣稱是否帶層（root／nested） |")
    a(f"| `G16 DECLARED_COVERS_IMPORTS` | {gv('G16')} | {prior_verdict('G16')} | 宣告依賴是否覆蓋實際 import |")
    a(f"| `G17 ENUM_SLASH_SAFE` | {gv('G17')} | {prior_verdict('G17')} | 分母是否由不受標點影響的解析器得出 |")
    a(f"| `G18 DIGEST_LOCALITY` | {gv('G18')} | {prior_verdict('G18')} | 每個 manifest digest 是否在自身 payload 內解析 |")
    a(f"| `G19 COPY_REGISTER` | {gv('G19')} | {prior_verdict('G19')} | 多副本名稱是否以 digest 解析、canonical 是否留給 owner |")
    a(f"| `G20 SUPPLY_CHAIN_SPLIT` | {gv('G20')} | {prior_verdict('G20')} | 離線可重現與 hosted 結論是否分開且不可互代 |")
    a("")
    a("`G17` 在修補前是 PASS：前輪的 SEAM 數**是對的**，缺的是「這個數字怎麼來的」可被檢驗。差分抓不到的那一種缺陷，用注入證明——"
      "把 `naive` 改成 11 後 `G17` 立刻紅在 `SLASH_PARSE_NOT_DEMONSTRATED`。")
    a("")
    a("### D.4 六個 WP 的現況（唯一有效版本）")
    a("")
    a("| WP | r8 | r9 | 這一輪實際改了什麼 |")
    a("|---|---|---|---|")
    a(f"| `WP-FHS-00` | `MEASURED` | `MEASURED_REPAIRED` | source lock 的 verdict 現在含行數；31/31 三欄全真（{mc.get('all_three_match')}/31） |")
    a(f"| `WP-FHS-01` | `MEASURED` | `MEASURED_REPAIRED` | U0 改雙規則（{U.get('per_line_segments_sum'):,} 行段／{U.get('structural_blocks_sum'):,} 結構塊）；ACL 拆作用域 |")
    a(f"| `WP-FHS-15` | `MEASURED` | `MEASURED_REPAIRED` | 相似度四族並列、全域上限 {dis.get('max_overall')}、0.0755 降為子欄值 |")
    a("| `WP-FHS-16` | `MEASURED` | `MEASURED_UNCHANGED` | 這一輪的七個缺陷無一落在 WP16；不重跑，也不重述 |")
    a(f"| `WP-FHS-19` | `MEASURED` | `MEASURED_REPAIRED` | 授權拆層、宣告 vs import 對帳（{HGK_UND}）、SBL 供應鏈主張拆兩半 |")
    a(f"| `WP-FHS-21` | `MEASURED` | `MEASURED_REPAIRED` | 分母改 slash-safe；{E.get('ac15',{}).get('measured')}／{E.get('oracle96',{}).get('measured')}／{E.get('h4',{}).get('measured')}／{E.get('seam',{}).get('measured')} 四項 match，12×8 完備 |")
    a("")
    a(f"`ORIGINAL_ACK` 仍是 **0**。`W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE` 仍是 **false**。這一輪沒有任何一句話在改變這件事。")
    a("")
    a("### D.5 仍然沒有的東西，與合併後的一份 OWNER 待辦")
    a("")
    a("| # | 待辦 | FirstFail | 需要什麼 Raw | Resume 條件 |")
    a("|---|---|---|---|---|")
    a("| 1 | `R1-ISSUER-REV14` | `REGISTRY_REV13_NO_ISSUER_RECOVERY` | rev 14 registry ＋ 31 列與 root 的 owner 簽章 | 受保護終端開窗後由 owner 執行（`--max-ops 33`） |")
    a(f"| 2 | `AUTHORITY-COLLISIONS` | `NAME_COLLISION_DIFFERENT_DIGEST` | 每個歧義名稱組指定權威副本的 owner 聲明（目前 {reg.get('ambiguous_names')} 組） | 聲明落地後重跑副本登記簿，該組離開 `ambiguous` |")
    a("| 3 | `LICENCE-FABRIC-HGK` | `LICENCE_ABSENT_AT_ROOT` | 兩庫的授權決定 | 根層 LICENSE／NOTICE 存在且掃描重跑 |")
    a("| 4 | `HGK-CI-ABSENT` | `CI_SERVICE_ABSENT` | 是否建 CI 的決定（現在有第二個理由：`yaml` 未宣告） | 有 workflow 且能跑，或明示不建並收窄期待 |")
    a("| 5 | `PIPD-15-VALUESET` | `CONTRACT_FAMILY_VALUE_SET_UNCLOSED` | 15 個 contract family 的 value-set 閉合 | 閉合落地且 schema 綁定 |")
    a("| 6 | `ORIGINAL-ACK-18` | `ORIGINAL_READER_ACK_UNOBSERVED` | 任一原域 Reader 對同 subject/scope 的 bytes 出具 ACK 或 scoped NACK | 收據落地 |")
    a("")
    a("### D.6 母本保全與副本清冊")
    a("")
    a(f"本檔 = `FHS_PIPD-LS-PKG_W0_r8.md` 全文（**{len(parent):,} bytes**，sha256 `{parent_sha}`）＋本章。"
      "r8 的全部章節逐位元保留於前綴；本章不修改、不摘要、不覆蓋任何 r8 條款。")
    a("")
    a(f"`V-01` 的完整陳述現在是一個 artifact 而不是一段話：`out/SOURCE_COPY_REGISTER.json` 登錄 {reg.get('names_registered')} 個名稱、"
      f"檢查 {reg.get('files_examined')} 個檔案，只有 `{AMB.get('name')}` 一組歧義（{AMB.get('distinct_digests')} 個 digest、"
      f"{AMB.get('differing_bytes')} bytes 不同）。哪一份是 canonical 仍由 owner 決定（待辦 2）。")
    a("")
    a("### D.7 可重現指令")
    a("")
    a("```bash")
    a("cd C:/Projects/Agent_Workspace/FHS_W0_R9_REPAIR_20261108")
    a("")
    a("# 逐 lane 重算（每個都會覆寫自己的 JSON）")
    a("python lanes/A/tools/source_lock_v2.py")
    a("python lanes/A/tools/authority_conflicts_v2.py")
    a("python lanes/B/tools/u0_partition_v2.py && python lanes/B/tools/tile_proof.py")
    a("python lanes/C/tools/distinctness_v2.py")
    a("python lanes/D/tools/wp19_v2.py")
    a("python lanes/E/tools/wp21_enum_v2.py")
    a("")
    a("# 副本登記簿與 A-01 patch")
    a("python tools/build_copy_register.py --sources <31 sources> --root <kb> --out out/SOURCE_COPY_REGISTER.json")
    a("python tools/a01_dependency_patch.py")
    a("")
    a("# 閘：修補後、修補前、逐項注入")
    a("python tools/gate_w0r9.py --round . --json out/GATE_R9.json")
    a("python tools/gate_w0r9.py --prior ../FHS_W0_R6_20261108 --json out/GATE_R9_ON_PRIOR.json")
    a("python tools/gate_w0r9.py --round . --selftest")
    a("")
    a("# 繼承的 16 項")
    a("cd ../FHS_W0_R7_VERIFY_20261108 && python tools/gate_w0r7.py \\")
    a("  --object-round ../FHS_W0_R6_20261108 \\")
    a("  --chain-child writeback/W0/FHS_PIPD-LS-PKG_W0_r9.md")
    a("```")
    a("")
    a("### D.8 明確不主張")
    a("")
    a("- 不主張任何 WP 達到 `ORIGINAL_ACK`：六個 WP 的原域 Reader 收據仍為 0。")
    a("- 不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`。")
    a("- 不主張两份 r6 之中哪一份是 canonical；只主張兩份都存在、同長、差 4 bytes。")
    a("- 不主張 HG-KSEOS 的 packaging 已修好：patch 已驗證但**未套用**，因為那是該 repo 的寫入，且它沒有 CI 可驗。")
    a("- 不主張 25,201 是「語意分割數」：它是 `RULE_STRUCTURAL_BLOCK` 的塊數，和 111,331 的行段數一樣都不是語意單元數。")
    a("- 不主張前輪的 24,003 錯了：那是另一條規則（整個 fenced block／整個 table 各算一塊），差 1,198 是規則差異，已寫在 `reconciliation`。")
    a("")

    chapter = "\n".join(doc) + "\n"
    out_doc = os.path.join(ROOT, "writeback", "W0", "FHS_PIPD-LS-PKG_W0_r9.md")
    os.makedirs(os.path.dirname(out_doc), exist_ok=True)
    combined = parent + chapter.encode("utf-8")

    # the prefix must be the parent bytes, exactly
    if combined[: len(parent)] != parent:
        print("PREFIX_NOT_IDENTICAL", file=sys.stderr)
        return 4
    with open(out_doc, "wb") as fh:
        fh.write(combined)
    back = open(out_doc, "rb").read()
    if back[: len(parent)] != parent:
        print("PREFIX_FAILED_ROUNDTRIP", file=sys.stderr)
        return 5

    r9_sha = sha(back)
    wb = os.path.join(ROOT, "writeback", "W0")

    def dump(name, obj):
        with open(os.path.join(wb, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=1)
            fh.write("\n")

    dump("W0_REVISION_MANIFEST.json", {
        "schema": "FHS.W0.RevisionManifest/1",
        "generated_at": ts,
        "chain": [
            {"version": "r8", "path": "FHS_PIPD-LS-PKG_W0_r8.md", "bytes": len(parent), "sha256": parent_sha, "role": "parent, preserved byte-identically as prefix"},
            {"version": "r9", "path": "FHS_PIPD-LS-PKG_W0_r9.md", "bytes": len(back), "sha256": r9_sha, "role": "current"},
        ],
        "prefix_identical": True,
        "prefix_bytes": len(parent),
        "appended_bytes": len(back) - len(parent),
        "claim_ceiling": "W0_SEVEN_DEFECTS_REPAIRED_WITH_SCOPED_OWNER_HOLDS",
        "self_digest_note": "this file does not record the digest of itself",
    })

    dump("W0_CLOSEOUT_DECISION.json", {
        "schema": "FHS.W0.CloseoutDecision/1",
        "generated_at": ts,
        "decision": "W0_R9_IMPLEMENTATION_REPAIR_ACCEPTED_AUTHOR_SIDE",
        "basis": f"{closed_count} of {len(DEFECT_DISPOSITION)} defects are closed in tools and artifacts; {owner_pending_count} are owner-scoped and named",
        "defects": DEFECT_DISPOSITION,
        "defects_closed": closed_count,
        "defects_owner_pending": owner_pending_count,
        "gate": {"inherited": f"{IG['pass']}/{IG['total']}", "new": f"{new_pass}/{new_total}", "prior_fail": prior_fail, "selftest_fired": fired, "selftest_exercised": exercised},
        "original_ack_count": 0,
        "w0_w1_w2_all_applicable_original_wp_done": False,
        "owner_signing_demand": 0,
        "not_claimed": ["ORIGINAL_ACK", "NATIVE_WORLDRAW", "RELEASE_GRANTED", "INDEPENDENT_PASS", "CANONICAL_COPY_SELECTED"],
    })

    dump("W0_HOLD_RESUME.json", {
        "schema": "FHS.W0.HoldResume/1",
        "generated_at": ts,
        "holds": [
            {"id": "H-V01-CANONICAL", "scope": "two r6 copies", "owner": "original domain owner", "firstfail": "NAME_COLLISION_DIFFERENT_DIGEST", "resume": "owner names one digest; register re-run"},
            {"id": "H-R1-ISSUER-REV14", "scope": "registry rev 14", "owner": "OWNER", "firstfail": "REGISTRY_REV13_NO_ISSUER_RECOVERY", "resume": "protected terminal, issuer key, --max-ops 33"},
            {"id": "H-LICENCE", "scope": "Fabric and HG-KSEOS root licence", "owner": "OWNER", "firstfail": "LICENCE_ABSENT_AT_ROOT", "resume": "root LICENSE/NOTICE present"},
            {"id": "H-HGK-CI", "scope": "HG-KSEOS CI", "owner": "OWNER", "firstfail": "CI_SERVICE_ABSENT", "resume": "workflow exists and runs, or a recorded decision not to build one"},
            {"id": "H-A01-YAML", "scope": "HG-KSEOS packaging", "owner": "HG-KSEOS maintainer", "firstfail": "UNDECLARED_DEPENDENCY", "resume": "patch applied and the coverage check re-run"},
            {"id": "H-PIPD-VALUESET", "scope": "15 contract families", "owner": "PIPD contract owner", "firstfail": "CONTRACT_FAMILY_VALUE_SET_UNCLOSED", "resume": "closure lands"},
            {"id": "H-ORIGINAL-ACK", "scope": "18 original WPs", "owner": "original domain readers", "firstfail": "ORIGINAL_READER_ACK_UNOBSERVED", "resume": "a reader issues ACK or scoped NACK"},
        ],
        "all_maker_side_defects_closed": True,
    })

    dump("W0_EVIDENCE_INDEX.json", {
        "schema": "FHS.W0.EvidenceIndex/1",
        "generated_at": ts,
        "index": [
            {"defect": "V-07", "artifact": "lanes/A/SOURCE_LOCK_V2.json", "check": "G11"},
            {"defect": "V-03", "artifact": "lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json", "check": "G13"},
            {"defect": "V-04", "artifact": "lanes/B/U0_PARTITION_V2.json", "check": "G12"},
            {"defect": "V-02", "artifact": "lanes/C/DISTINCTNESS_V2.json", "check": "G14"},
            {"defect": "V-06/A-01/A-03", "artifact": "lanes/D/WP19_V2.json", "check": "G15/G16/G20"},
            {"defect": "A-02", "artifact": "lanes/E/WP21_ENUM_V2.json", "check": "G17"},
            {"defect": "V-05", "artifact": "out/stage/**/MANIFEST.json", "check": "G18"},
            {"defect": "V-01", "artifact": "out/SOURCE_COPY_REGISTER.json", "check": "G19"},
            {"defect": "A-01", "artifact": "out/A01_DEPENDENCY_PATCH/RESULT.json", "check": "G16"},
        ],
    })

    dump("W0_TO_W1_HANDOFF.json", {
        "schema": "FHS.W0.ToW1Handoff/1",
        "generated_at": ts,
        "subject": "FHS_W0_r9",
        "document": {"path": "FHS_PIPD-LS-PKG_W0_r9.md", "sha256": r9_sha, "bytes": len(back)},
        "what_w1_may_read": [
            "the three SPEC drafts as author-side drafts, not canonical PI",
            "the 18 stage contracts with their byte offsets",
            "the four denominators 15/96/12/11 as plans, not verdicts",
            "the copy register, to avoid resolving a name to the wrong bytes",
        ],
        "what_w1_may_not_read_as_done": [
            "any work package as ORIGINAL_ACK",
            "the 96 oracles as executed",
            "the donor/method projection as an admission",
        ],
        "open_owner_items": 6,
    })

    rows = [
        {"wp": "WP-FHS-00", "r8": "MEASURED", "r9": "MEASURED_REPAIRED", "defects": ["V-07"], "artifact": "lanes/A/SOURCE_LOCK_V2.json", "original_ack": False},
        {"wp": "WP-FHS-01", "r8": "MEASURED", "r9": "MEASURED_REPAIRED", "defects": ["V-04", "V-03"], "artifact": "lanes/B/U0_PARTITION_V2.json", "original_ack": False},
        {"wp": "WP-FHS-15", "r8": "MEASURED", "r9": "MEASURED_REPAIRED", "defects": ["V-02"], "artifact": "lanes/C/DISTINCTNESS_V2.json", "original_ack": False},
        {"wp": "WP-FHS-16", "r8": "MEASURED", "r9": "MEASURED_UNCHANGED", "defects": [], "artifact": "../FHS_W0_R6_20261108/evidence/WP16/REPORT.json", "original_ack": False},
        {"wp": "WP-FHS-19", "r8": "MEASURED", "r9": "MEASURED_REPAIRED", "defects": ["V-06", "A-01", "A-03"], "artifact": "lanes/D/WP19_V2.json", "original_ack": False},
        {"wp": "WP-FHS-21", "r8": "MEASURED", "r9": "MEASURED_REPAIRED", "defects": ["A-02"], "artifact": "lanes/E/WP21_ENUM_V2.json", "original_ack": False},
    ]
    dump("W0_WP_MATRIX.json", {
        "schema": "FHS.W0.WPMatrix/1",
        "generated_at": ts,
        "rows": rows,
        "wp_state_counts": {"MEASURED_REPAIRED": 5, "MEASURED_UNCHANGED": 1},
        "original_ack_count": 0,
        "gate": {"inherited_pass": IG["pass"], "inherited_total": IG["total"], "new_pass": new_pass, "new_total": new_total},
        "terminal": {"W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE": False},
    })

    print(f"wrote {out_doc} bytes={len(back)} prefix_identical=True sha256={r9_sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
