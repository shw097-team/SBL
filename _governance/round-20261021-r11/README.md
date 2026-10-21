# R11 Evidence Packet — `round-20261021-r11`（intake / baseline / lane-mandate）

本目錄是 `SBL-R11-20261021-POST-R8-R9-R10-FULL-CONTRACT` 的**第一輪證據切片**。
它證明的是「來源身份、車道 mandate、bundle 可用性、環境分母」，**不是**任何 DOC 語義條款、Native 效果、Host 安裝或全案驗收。

## 檔案

| 檔案 | 內容 |
|---|---|
| `00_ROUND_PLAN.md` | 核心大目標 / 治理邊界 / mandate chain / 執行SPEC / **TS00–TS48 任務清單** / **CHK00–52 檢測清單** / GOAL_FIDELITY_DIFF / 下一步 |
| `10_BASELINE.md` | Host、五 repo git 狀態、HGK conformance 新分母、source pin、compiler bundle、host install readback、native 狀態 |
| `20_SOURCE_LEDGER.json` | 14 DOC（bytes+SHA）+ rollup + mirror equality、20 KP、2 Skill、10 design vols、compiler/challenge bundle、控制編譯收據、missing_critical |
| `30_MANDATE_CHAIN.md` | Owner 模型 mandate vs epoch 29 宣告面、三次車道探針、capability ceiling、消除 drift 的兩個合法選項 |
| `40_FINDINGS.md` | F-R8-001..010、R9-02..07、SP-INT、本輪新發現 `O-R11-001..007`、未關閉 CR |
| `50_RETURN.json` | `SBL_R11_EVIDENCE_RETURN.v1` 對映（欄位缺者顯式 `null`，不假填） |
| `hgk_conformance.log` | HGK `b22706e` 完整 pytest 輸出（`-rf` 失敗清單） |
| `mandate_probes/` | 三車道 dispatcher receipt + 每次 attempt 的原始 stdout/stderr |
| `compile_control/` | 官方 compiler 對 R9 控制契約四階段的 receipt/report |
| `host_readback/` | `sbl-stack status`、`sbl-harness doctor` 的原始 JSON |
| `verify_r11_packet.py` | 可重跑驗證器：自行重算 14 DOC/rollup/mirror/KP 並與 ledger 比對 |
| `verifier_output.txt` | 上列驗證器的實際輸出（PASS, rc=0） |

## 外部驗收官如何重算（不需要信任本 packet 的敘述）

```bash
python verify_r11_packet.py \
  --ledger 20_SOURCE_LEDGER.json \
  --docs-dir "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG" \
  --mirror-dir "C:/Projects/Agent_Workspace/_sbl_src_mirror/SBL_PIPD-LS-PKG" \
  --kp-dir "C:/Projects/Agent_Workspace/知識庫/工程基座/GPTs_GENIEMAKER_開發實作+驗收指揮官_KP_Builder_ReleasePack_v2026.06.03-r2/KnowledgePack"
```

預期：14 行 `MATCH`、`TOTAL bytes=17473442`、rollup `01b972c8…f9d`、`PASS (source identity only…)`、exit 0。
缺任何輸入 → exit 2（不靜默通過）。

## 這份 packet 刻意**沒有**主張的事

- 沒有 Native WorkOrder / ONE ECP / Permit / ExecutionBinding（本輪 `NOT_AUTHORIZED`）。
- 沒有 Commander-SP / Challenge-SP 的真調用（只有車道 mandate 探針）。
- 沒有 ChatGPT 私人 Plugin Host 資格（0/3，`HOST_PENDING`）。
- 沒有 149 Child / 441 identity / 38 Surface 的 runtime 驗收，也沒有任何完成百分比（語義分母 `UNKNOWN`）。
- `SBL_FULL_PRODUCT` = **OPEN**。
