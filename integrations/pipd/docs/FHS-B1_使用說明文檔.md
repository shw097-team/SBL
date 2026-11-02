# FHS-B1 使用說明文檔（HG-KSEOS／Fabric／SBL 整合版）

版本：`FHS-B1-DOC-2026-10-28`　對齊：`FHS_MSC_B1_PIPD_LS_PKG_00～08`　狀態：**本地已升格基線**
本文件是三個棧的**單一入口**；各棧細節見各自 repo 的 `docs/*使用說明文檔.md`。

---

## 0. 三十秒版

| 問題 | 答案 |
|---|---|
| 這是什麼 | FHS-MSC B1（Bootstrap Repair PIPD-LS PKG_00～08）在**真 native 路徑**上的閉環實作與證據集 |
| 現在到哪 | 閘門合取 PASS、無殘餘 blocker、宣告與裁決皆 owner 簽章、本地升格為 `B1-LOCAL-2026-10-28` |
| 我要怎麼確認 | 下面 §2 的四條命令，全部可在本機重跑 |
| 我要看證據 | `b1_closure_20261028/EVIDENCE_INDEX.md`（四個 repo 皆有） |
| 不要誤會 | 這**不是** release（`release: NOT_RUN`），**不是** repo `main` 已合併，**不是**第三方驗收 |

## 1. 三個棧各做什麼（責任邊界）

| 棧 | 角色 | 本輪實際交付 | 明確不做 |
|---|---|---|---|
| **HG-KSEOS** | 治理／車道／native admission kernel | `native_admission.assert_protected()` 改純 .NET ACL（D-16）；車道 arm alias（`served_arm_raw`）；B1 證據索引 | 不簽 SBL 的 permit；不改 kernel 驗證語義 |
| **Fabric** | policy／contract 的**消費**端 | GWO-FABRIC 證據；consumer-only 讀回 | **沒有 activator**：不代簽、不促升、不產生 PASS |
| **SBL** | 來源／知識／藍圖（DOC-00～13） | GWO-SBL 證據；SourceFreeze HOLD 的裁決記錄 | 不自行凍結上游（凍結是上游 owner 的動作） |

> 三者關係用一句話記：**SBL 定義語義、Fabric 提供契約與政策、HG-KSEOS 執行並留證**。
> 任何一棧都不能用自己的輸出代替另一棧的驗收（PKG_08 L45「互不借 PASS」）。

## 2. 五分鐘驗證（四條命令，皆有已知輸出）

```bash
# 1) 閘門總狀態
cd C:/Projects/Agent_Workspace/var/B1-PIPD-PKG-20261027 && python gates.py
# 期望：G-A 6/6 PASS, GWO ALL_THREE_PASS, G-B PASS, gates_conjunction PASS, mission_complete true, blocker null

# 2) native 信任根（需可讀 ACL）
PYTHONPATH=C:/Projects/Agent_Workspace/HG-KSEOS/src python -c "from hg_kseos.native_admission import ProtectedRegistry as P; print(P().snapshot())"
# 期望：status ACTIVE, keys 1, sids_distinct True

# 3) 宣告／裁決／升格收據驗章
cd C:/Projects/Agent_Workspace/var/B1-CONT-20261028 && python - <<'EOF'
import json,pathlib,sys; sys.path.insert(0,'wave1'); import declaration_lib as dl
reg=json.loads(pathlib.Path(r'C:/Projects/Agent_Workspace/var/B1-PIPD-PKG-20261027/admission/registry/runner-registry.json').read_text(encoding='utf-8'))
pub=(reg.get('owner_enrollment') or {}).get('public_hex') or ''
for f in ('wave1/DECLARATION_v1.json','wave1/OWNER_RULING_v1.json','wave3/PROMOTION_RECEIPT.json'):
    print(f, dl.verify(json.loads(pathlib.Path(f).read_text(encoding='utf-8')), pub))
EOF
# 期望：三行皆 (True, 'VERIFIED')

# 4) 升格前回推點是否仍一致
python wave3/verify_snapshot.py
# 期望：verdict MATCH_WITH_DECLARED_DELTA（僅 README.md、AGENTS.md 兩處升格宣告）
```

## 3. native E2E 閉環長什麼樣

```
workorder request ──digest──► scope.request_sha256（registry，提權寫入，1 小時 TTL）
        │
        ├─ owner 解鎖一次 ──► mint source_freeze / task_kind / oracle_ratification 三個 reference（簽章）
        │
        └─ kernel authorize() ──► canonical_events(native_admission) ＋ lease ＋ nonce
                                   │
                                   └─ 交易內執行 effect → 收據（entity/state/rollback_ref）
```

**實測規模**：245 筆 `native_admission`（1 張首發 `WO-B1-NATIVE-001` ＋ 244 案 corpus）、735 個 nonce、
245 個 lease、corpus `case_fail 0`。收據：`wave2/NATIVE_ADMISSION_RECEIPT.json`、`wave2/CORPUS_NATIVE_RECEIPT.json`。

三個必備名詞（`native_admission.KINDS`）：`source_freeze`、`task_kind`、`oracle_ratification`。
少任何一個，`authorize()` 會以具名錯誤碼拒絕——**不要**用放寬檢查的方式讓它通過。

## 4. 無人值守建議（可用，但有明確上限）

| 項目 | 現況 | 建議做法 |
|---|---|---|
| reference TTL | registry `max_ttl_seconds 3600`（`native-trust-maintenance.ps1:151` 硬性 >3600 直接 throw） | **不要**為了長跑而放寬 TTL；用「排程解鎖 ＋ journal 續跑」 |
| 續跑 | `wave2/wave2_queue.py`、`wave2/run_corpus_native.py` 逐案寫 journal，可從斷點續 | 中斷後重跑同一命令即可，無需重簽 |
| 解鎖節奏 | 一次解鎖可涵蓋該次全部簽章（load-once） | 把同一目的的多個簽章排進同一次口令提示 |
| 失敗處理 | 逐案 journal 記錄 typed refusal | 失敗即 park、記錄原因，不靜默重試 |

## 5. 證據地圖（問題 → 檔案 → 指令）

| 問題 | 檔案 | 指令／判讀 |
|---|---|---|
| 全部閘門過了嗎 | `artifacts/GATES.json` | 讀 `gates_conjunction`、`G-A`、`GWO`、`G-B` |
| mission 為何是 true | 同上 | `mission_complete` ＋ `why_not_complete` ＋ `declared_ceilings[].blocks_mission_completion` |
| native 還是 sandbox | `wave2/*RECEIPT.json` | 比對 `entity_id`／`event_id` 與 `SESSION_STATE.json#gate_c_corpus_native` |
| claim ceiling 是誰說的 | `wave1/DECLARATION_v1.json` | `declaration_lib.verify(dec, registry.owner_enrollment.public_hex)`（bindings `9fb04a82…`，簽於 2026-10-28T15:02:55） |
| 兩條宣告誰裁定 | `wave1/OWNER_RULING_v1.json` | 同上（bindings `a587491e…`，簽於 14:43:36） |
| 本地升格憑什麼 | `wave3/PROMOTION_RECEIPT.json` | 同上（bindings `5a19f3cd…`，簽於 15:18:03，版本 `B1-LOCAL-2026-10-28`） |
| 12/30 是不是缺口 | `FAR_B1_v9_20261028.md` | 分母＝registry 列數；PKG_00～08 無 30-route 要求；書面要求僅 `INSTALLED`（30/30 已滿足） |
| 哪些分支可併 main | `wave3/candidate_screen.json` | `git merge-tree --write-tree origin/main <branch>` 逐支；目前 **0 支**合格 |

## 6. 已修的三個真實缺陷（含事故，照實寫）

1. **`claim_ceiling` 不在簽章覆蓋內**（`signed_payload()` 只蓋 4 個純量）→ 改用 owner 簽的宣告綁「文字＋registry sha＋量測」，
   漂移即 `BINDINGS_MISMATCH`。`FAR_B1_v6`。
2. **兩條殘餘 blocker 是寫死字串**（`gates.py:232-234`，且引用的 `DOC-13 L2775` 並不支持該主張）→ 改成量測，
   再由 owner 簽裁決清除。`FAR_B1_v7`。
3. **D-8 派工謊報**：`resolve()` 用子字串比對，`native_issuer` 會被派到 `issuer_subject_runner.py` →
   改讀簽章 registry 的精確查表；修後 `12 exact / 18 具名拒絕 / 0 派錯`。`FAR_B1_v9`。

**事故 2 件（均已修正並留痕）**
- 重簽時第一次簽到 candidate 快取的舊 sha（18 列）→ 改為簽前 `rebuild()` 從磁碟重算 ＋ `sha_not_on_disk` fail-closed
- 宣告簽章第一次簽了「寫入前還會被改動」的 body → 建 `declaration_lib` 讓 seal/verify 共用同一份定義

## 7. 升格、合併、回推

| 動作 | 現況 | 怎麼做 |
|---|---|---|
| 本地升格 | **已完成** `B1-LOCAL-2026-10-28` | `PROMOTED.json` 為指標；回推點 `SNAPSHOTS/B1_PRE_PROMOTION_20261028/` |
| 回推 | 指令在手 | `tar -xf surface.tar` → `python wave3/verify_snapshot.py`（應 MATCH…） |
| repo 合併 | **未做**（`main` 未動） | 四個 PR（HG-KSEOS#3、Fabric#19、PIPD-LS-SP#21、SBL#14）待 owner 簽 repo 端收據後合併 |
| 合併後回推點 | 建議 | 在 `main` 打 tag `b1-promote-20261028`，記錄 PR head sha |

## 8. 不要做的事（防誤用，逐條都有理由）

1. 不要為了 `12/30` 去實作 18 條 typed-refusal：其中 8 條輸入不存在（ECP／host load／golden fixtures），做了就是造假。
2. 不要把 `claim_ceiling` 或 `authorization` 當成「已簽內容」：它們不在簽章覆蓋內，只有宣告能證明變更。
3. 不要放寬 TTL 換取長跑：改用排程解鎖 ＋ journal 續跑。
4. 不要用 Fabric consumer 冒充 activator：Fabric 沒有促升能力。
5. 不要把 sandbox 的執行說成 native：sandbox ceiling 是 `AUTHOR_SIDE_EXECUTED_SANDBOX`，與 native admission 不可混用。
6. 不要在未簽 repo 端收據前合併 PR。

## 9. 名詞表

| 名詞 | 意思 |
|---|---|
| native admission | kernel 以 owner 簽章的 reference ＋ registry scope 授權，寫入 `canonical_events` 的准入 |
| reference | 對三種 kind（`source_freeze`／`task_kind`／`oracle_ratification`）之一簽出的短期憑證 |
| declared ceiling | 已量測但仍在的限制，帶 `claim_weight`；不是 blocker，也不許當成 PASS |
| blocking declaration | 需要 owner 裁定才能清除的宣告；未裁定時 `mission_complete` 必為 false |
| inventory | 數量清點（如 12/30），沒有上游要求時不得當作缺口 |
| rollback point | 逐檔 sha256 的快照 ＋ 一行還原指令，不是「再跑一次就好」 |

## 10. 變更記錄

| 日期 | 變更 |
|---|---|
| 2026-10-28 | 建立本整合文件；納入 FAR v5～v10 的裁決、D-8／D-16 修復、native corpus 245 筆、宣告／裁決／升格三份簽章與回推點 |
