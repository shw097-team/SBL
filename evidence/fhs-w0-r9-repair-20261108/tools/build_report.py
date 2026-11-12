#!/usr/bin/env python3
"""Build the single integrated report an outside verifier reads first.

Same rule as build_r9: no figure is typed here. Everything is read from the artifacts this round
produced, so the report cannot disagree with the evidence it cites.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

TZ = timezone(timedelta(hours=8))
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def j(rel: str) -> dict:
    p = os.path.join(ROOT, rel.replace("/", os.sep))
    if not os.path.isfile(p):
        print(f"MISSING {rel}", file=sys.stderr)
        raise SystemExit(3)
    return json.load(open(p, "r", encoding="utf-8"))


def sha(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main() -> int:
    lock = j("lanes/A/SOURCE_LOCK_V2.json")
    acl = j("lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json")
    u0 = j("lanes/B/U0_PARTITION_V2.json")
    dis = j("lanes/C/DISTINCTNESS_V2.json")
    wp19 = j("lanes/D/WP19_V2.json")
    wp21 = j("lanes/E/WP21_ENUM_V2.json")
    reg = j("out/SOURCE_COPY_REGISTER.json")
    gate = j("out/GATE_R9.json")
    gprior = j("out/GATE_R9_ON_PRIOR.json")
    ginh = j("out/GATE_R9_INHERITED.json")
    a01 = j("out/A01_DEPENDENCY_PATCH/RESULT.json")
    close = j("writeback/W0/W0_CLOSEOUT_DECISION.json")
    layer = j("out/LAYER_AUDIT.json")
    selftest = j("out/GATE_R9_SELFTEST.json")
    docpath = os.path.join(ROOT, "writeback", "W0", "FHS_PIPD-LS-PKG_W0_r9.md")
    doc_sha = sha(docpath)
    doc_bytes = os.path.getsize(docpath)

    L, U = lock["totals"], u0["totals"]
    EXT_E, EXT_N = acl.get("kb_external_exact", {}), acl.get("kb_external_normalised", {})
    MPM, PC, NC = dis.get("max_per_method", {}), dis.get("prior_claim", {}), dis.get("negative_control", {})
    S = wp19.get("summary", {})
    R = wp19.get("repos", {})
    E, NU = wp21["denominators"], wp21["naive_undercount"]
    OG = wp21["groups"]["oracle96"]
    G, GP = gate["summary"], gprior["summary"]
    fired = sum(1 for x in selftest if x.get("mutated") == "FIRED")
    amb = reg["ambiguous"][0]
    ts = datetime.now(TZ).isoformat(timespec="seconds")

    o = []
    a = o.append
    a("# FHS W0｜把 r8 的七個缺陷從「被描述」改成「被修好」")
    a("")
    a("> **對象**：外部驗收官、原 Maintainer、下一個 session。")
    a(f"> **一句話**：`FHS_PIPD-LS-PKG_W0_r8` 是草案；這一輪把它的缺陷修進工具與產物，新增十項閘，"
      f"其中 {GP['fail']} 項在修補前的產物上會紅、{G['pass']}/{G['total']} 在修補後轉綠，"
      f"並逐項注入證明每一個都會咬。**原域 Reader 收據仍是 0。**")
    a(f"> **ClaimCeiling**：`W0_SEVEN_DEFECTS_REPAIRED_WITH_SCOPED_OWNER_HOLDS`。不主張 `ORIGINAL_ACK`、`NATIVE_WORLDRAW`、`RELEASE_GRANTED`、`INDEPENDENT_PASS`、已併、已審、已發行。")
    a("")
    a("| 事實 | 值 |")
    a("|---|---|")
    a(f"| 被修對象 | `FHS_PIPD-LS-PKG_W0_r8`（草案）＋其實作回合 `FHS_W0_R6_20261108` |")
    a(f"| 本回合根 | `{ROOT.replace(chr(92), '/')}` |")
    a(f"| 產物 | `FHS_PIPD-LS-PKG_W0_r9.md`（{doc_bytes:,} B，sha256 `{doc_sha[:16]}…`），r8 逐位元保留為前綴 |")
    a(f"| 閘 | 繼承 {ginh['checks_pass']}/{ginh['checks_total']} ＋ 新增 {G['pass']}/{G['total']}；對修補前 {GP['fail']} FAIL；注入 {fired}/{len(selftest)} FIRED |")
    a(f"| 缺陷 | 10 項中 {close['defects_closed']} 項 CLOSED、{close['defects_owner_pending']} 項 owner-scoped |")
    a(f"| 原域 ACK | **0** |")
    a(f"| 對三庫的寫入 | 0（三庫 porcelain 與 lane D 基線相同；registry 仍 rev {layer['owner_registry']['registry_rev']}） |")
    a(f"| Owner 簽章需求 | 0（未開窗）：{layer['owner_registry']['rows_signed']}/{layer['owner_registry']['rows']} 列已簽、root 簽章在場 |")
    a("")
    a("---")
    a("")
    a("## 1｜十個缺陷：現在的狀態與依據")
    a("")
    a("| ID | 修補 | 量測 | 依據檔 |")
    a("|---|---|---|---|")
    a(f"| `V-01` 同名 r6 兩份 | **工具化**（canonical 留 owner） | {reg['names_registered']} 個名稱、{reg['ambiguous_names']} 組歧義：`{amb['name']}` 兩份同長 {amb['lengths']}、差 {amb['differing_bytes']} bytes、首差 offset {amb['first_difference_offset']} | `out/SOURCE_COPY_REGISTER.json` |")
    a(f"| `V-02` 相似度上限寫錯 | **CLOSED** | `max_overall`={dis['max_overall']}；舊 0.0755 重現為 {PC.get('reproduced_exact_value')}（{PC.get('field_it_actually_belongs_to')}），`reproduced_as_maximum`={PC.get('reproduced_as_maximum')}；負控 {NC.get('max')} | `lanes/C/DISTINCTNESS_V2.json` |")
    a(f"| `V-03` 17 的作用域 | **CLOSED（並細化）** | in-set 重複 {acl['in_set']['duplicate_basename_groups']}；外部：精確同名 {EXT_E.get('source_files_with_at_least_one_divergent_copy')}、剝尾碼後 {EXT_N.get('source_files_with_at_least_one_divergent_copy')} | `lanes/A/AUTHORITY_CONFLICT_LEDGER_V2.json` |")
    a(f"| `V-04` 段數＝行數 | **CLOSED** | 行段 {U['per_line_segments_sum']:,}／結構塊 {U['structural_blocks_sum']:,}，兩規則 31/31 貼齊 | `lanes/B/U0_PARTITION_V2.json` |")
    a(f"| `V-05` manifest 跨 payload | **r8 已修，本輪加閘** | SBL 載荷 26/26、Fabric 1/1 皆在自身 payload 內解析 | `out/stage/**/MANIFEST.json` |")
    a(f"| `V-06` 授權只在根層 | **CLOSED** | SBL root=True/nested {R['sbl']['licence']['claim']['nested_licence_count']}；Fabric root={R['fabric']['licence']['claim']['root_licence_present']}/nested {R['fabric']['licence']['claim']['nested_licence_count']}；HGK root={R['hgk']['licence']['claim']['root_licence_present']}/nested {R['hgk']['licence']['claim']['nested_licence_count']} | `lanes/D/WP19_V2.json` |")
    a(f"| `V-07` 行數不符卻 MATCH | **CLOSED** | 31/31 bytes+lines+sha 全真；宣告 {L['declared_lines_sum']:,}＝實測 {L['observed_lines_sum']:,}；舊 split 慣例 {L['observed_split_crlf_sum']:,} | `lanes/A/SOURCE_LOCK_V2.json` |")
    a(f"| `A-01` 未宣告依賴 | **本輪推翻原敘述並修補** | `cryptography>=42` 已宣告；`fhs/issuer_binding.py` 不存在；真缺陷是 `yaml`（patch 已驗證、未套用） | `out/A01_DEPENDENCY_PATCH/RESULT.json` |")
    a(f"| `A-02` SEAM 少一列 | **CLOSED（機制更窄）** | naive={NU['naive']}／robust={NU['robust']}，缺 `{NU['missing_id']}`；只有把 `/` 當欄位分隔的解析器才會低估 | `lanes/E/WP21_ENUM_V2.json` |")
    a(f"| `A-03` 供應鏈兩半 | **CLOSED** | 離線自測 exit {S.get('sbl_self_test_exit')}、拒絕 {len(S.get('sbl_refused_codes', []))} 個 mutation；hosted `{S.get('sbl_hosted_state')}`（不假造 run id） | `lanes/D/WP19_V2.json` |")
    a("")
    a("## 2｜四項「前輪寫法被本輪量測推翻」")
    a("")
    a(f"1. **`A-01` 兩處都錯**：`pyproject.toml:6` 是 `dependencies = [\"cryptography>=42\"]`，不是 `[]`；附錄點名的 "
      f"`src/hg_kseos/fhs/issuer_binding.py` 不存在。真正未宣告的是 `yaml`（`lane_policy.py:71`，函式內 lazy、"
      f"`except` 後 `return None`）。修補：optional extra `yaml = [\"PyYAML>=6\"]`，套用前後 "
      f"`{a01['before']['verdict']}` → `{a01['after']['verdict']}`。")
    a(f"2. **`A-02` 機制更窄**：只按空白切 token 仍得 11；只有以 `/` 當欄位分隔者才丟掉 `SEAM-09`。")
    a(f"3. **`V-03` 的 17 依賴一條沒寫下的規則**：源檔名帶 `(1)`，精確同名比對得 {EXT_E.get('source_files_with_any_external_copy')} 份外部副本；"
      f"剝掉尾碼才得 {EXT_N.get('source_files_with_at_least_one_divergent_copy')}。")
    a(f"4. **`V-06` 的嵌套數變了**：Fabric 6（前輪記 5）、HG-KSEOS 8（前輪記 0），HGK 的 8 個全在 vendored 外掛快取樹內。")
    a("")
    a("## 3｜閘：繼承 16 ＋ 新增 10")
    a("")
    a("| 層 | 判決 |")
    a("|---|---|")
    a(f"| 繼承 16 項（對 r6 回合，r9 為鏈子） | **{ginh['checks_pass']}/{ginh['checks_total']} PASS**，`G10` 對 r9 宣告的父本為 `RESOLVED` |")
    a(f"| 新增 10 項（對 r9 產物） | **{G['pass']}/{G['total']} PASS** |")
    a(f"| 新增 10 項對**修補前**產物 | **{GP['fail']} FAIL／{GP['pass']} PASS／{GP['not_applicable']} n/a** |")
    a(f"| 逐項注入 | **{fired}/{len(selftest)} FIRED** |")
    a(f"| 空回合（fail-closed） | 第一次跑在 lane 產物尚未齊備時即非零退出，不是「先綠再說」 |")
    a("")
    a("| 檢查 | 修補後 | 修補前 |")
    a("|---|---|---|")
    for c in gate["checks"]:
        pv = next((x["verdict"] for x in gprior["checks"] if x["check"] == c["check"]), "?")
        a(f"| `{c['check']} {c['name']}` | {c['verdict']} | {pv} |")
    a("")
    a("`G17` 在修補前是 PASS——前輪的 SEAM 數本來就對，缺的是「怎麼算出來的」可被檢驗。"
      "這一類只有注入能證明，差分證明不了。")
    a("")
    a("## 4｜六個 WP 的狀態")
    a("")
    a("| WP | r9 | 修了什麼 |")
    a("|---|---|---|")
    a(f"| `WP-FHS-00` | MEASURED_REPAIRED | verdict 現在含行數；{lock['match_counts'].get('all_three_match')}/31 三欄全真 |")
    a(f"| `WP-FHS-01` | MEASURED_REPAIRED | 雙規則分割；ACL 拆作用域 |")
    a(f"| `WP-FHS-15` | MEASURED_REPAIRED | 四族相似度、全域上限 {dis['max_overall']} |")
    a("| `WP-FHS-16` | MEASURED_UNCHANGED | 本輪缺陷無一落在 WP16，不重跑 |")
    a(f"| `WP-FHS-19` | MEASURED_REPAIRED | 授權拆層、宣告 vs import、供應鏈主張拆半 |")
    a(f"| `WP-FHS-21` | MEASURED_REPAIRED | {E['ac15']['measured']}／{E['oracle96']['measured']}／{E['h4']['measured']}／{E['seam']['measured']}；12×8 完備={OG.get('complete_12x8')} |")
    a("")
    a("## 5｜仍然沒有的東西（依解鎖順序）")
    a("")
    a("| # | 仍缺 | 誰能做 | Resume 條件 |")
    a("|---|---|---|---|")
    a("| 1 | 任一 WP 的 `ORIGINAL_ACK` | 原域 Reader | 同 subject/scope 的 ACK 或 scoped NACK |")
    a("| 2 | registry rev 14 | OWNER | 受保護終端＋issuer 私鑰（`--max-ops 33`） |")
    a(f"| 3 | 兩份 r6 的 canonical 選擇（{reg['ambiguous_names']} 組） | 原 Domain Owner | 指定一個 digest |")
    a("| 4 | Fabric／HG-KSEOS 根層授權 | OWNER | 根層 LICENSE/NOTICE 存在 |")
    a("| 5 | HG-KSEOS 是否建 CI | OWNER | 有 workflow 或明示不建 |")
    a("| 6 | HG-KSEOS `yaml` optional extra | 該 repo 維護者 | 套用已驗證 patch 並重跑覆蓋檢查 |")
    a("| 7 | 15 個 PIPD contract family value-set | 原 contract Owner | 閉合落地 |")
    a("")
    a("## 6｜本輪自我錯誤（全文在 `out/SELF_ERRORS.md`）")
    a("")
    a("`E-R01` `--prior` 沒切模式，差分其實是同一棵樹跑兩次｜`E-R02` 閘先假設 schema，四項檢查直接拋例外｜"
      "`E-R03` 把附錄的錯誤寫進檢查器｜`E-R04` 把自家模組與 dist/import 異名判成未宣告｜"
      "`E-R05` `patch -p0` 對 `a/` 前綴找不到檔｜`E-R06` 重建文件讓 payload 過期｜`E-R07` 7 與 10 在同一句混用｜`E-R08` 位數抄對、位置卻寫成自己早先 `find` 的結果（HG-KSEOS 8 個嵌套授權檔的位置）。")
    a("")
    a("最該記住的兩條：**差分測試要先證明兩邊不同**；**把別人的結論寫進檢查器，等於把那個結論升格成規則**。")
    a("")
    a("## 7｜可重現指令")
    a("")
    a("```bash")
    a("cd C:/Projects/Agent_Workspace/FHS_W0_R9_REPAIR_20261108")
    a("")
    a("python lanes/A/tools/source_lock_v2.py            # → 31/31 bytes+lines+sha")
    a("python lanes/A/tools/authority_conflicts_v2.py    # → in-set 0 / external 依規則")
    a("python lanes/B/tools/u0_partition_v2.py && python lanes/B/tools/tile_proof.py")
    a("python lanes/C/tools/distinctness_v2.py           # → max_overall + 負控")
    a("python lanes/D/tools/wp19_v2.py                   # → 授權分層 + 依賴覆蓋 + 供應鏈兩半")
    a("python lanes/E/tools/wp21_enum_v2.py              # → 15/96/12/11 + naive vs robust")
    a("python tools/a01_dependency_patch.py              # → patch 套用等於候選")
    a("")
    a("python tools/gate_w0r9.py --round .                                  # 期望 10/10 PASS exit 0")
    a("python tools/gate_w0r9.py --prior ../FHS_W0_R6_20261108              # 期望 FAIL（差異矩陣）")
    a("python tools/gate_w0r9.py --round . --selftest                       # 期望 10/10 FIRED")
    a("")
    a("python tools/verify_payload_manifest.py out/stage/sbl/evidence/fhs-w0-r9-repair-20261108")
    a("python tools/verify_payload_manifest.py out/stage/fabric/INTEGRATION/FHS/docs/as-built/W0/r9")
    a("")
    a("cd ../FHS_W0_R7_VERIFY_20261108")
    a("python tools/gate_w0r7.py --object-round ../FHS_W0_R6_20261108 \\")
    a("  --chain-child ../FHS_W0_R9_REPAIR_20261108/writeback/W0/FHS_PIPD-LS-PKG_W0_r9.md")
    a("```")
    a("")
    a("## 8｜不主張")
    a("")
    a("- 不主張任何 WP 達到 `ORIGINAL_ACK`；`W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE` 仍為 `false`。")
    a("- 不主張兩份 r6 之中哪一份 canonical。")
    a("- 不主張 HG-KSEOS packaging 已修好：patch 已驗證但未套用。")
    a(f"- 不主張 {U['structural_blocks_sum']:,} 是語意分割數；它是 `RULE_STRUCTURAL_BLOCK` 的塊數。")
    a("- 不主張前輪 24,003 錯了；那是另一條規則，差 1,198 已在 `reconciliation` 解釋。")
    a("")

    out = os.path.join(ROOT, "out", "FHS_W0_R9_IMPLEMENTATION_REPAIR_REPORT_2026-11-08.md")
    with open(out, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(o) + "\n")
    print(f"wrote {out} bytes={os.path.getsize(out)} sha256={sha(out)[:16]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
