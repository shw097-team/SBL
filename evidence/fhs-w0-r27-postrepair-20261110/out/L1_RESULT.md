# L1 — G29 signed-vote quorum 修復（EC-R26-003 / resume predicate R26-01）

**狀態：PASS**　branch `r27/quorum-g29`　commit `3099dec65cc29f04fcc4ae17f6a976f0a6b76832`
成果 JSON：`out/L1_RESULT.json`（所有數字由 `evidence/L1/build_result.py` 執行後讀回，未手打）

## 修復內容（`evidence/fhs-w0-r26-repair-20261109/tools/verify_quorum.py`，就地修，角色不變）

三個 false-green 類別現在各自以具名碼拒絕並 exit 1：

| 類別 | 新拒絕碼 | mirror 證據 |
|---|---|---|
| dict 形 `votes_r25` 無 per-vote candidate | `MISSING_CANDIDATE_BINDING` | `10_neg_FG1_DICT_NO_BINDING.log` exit 1 |
| 捏造 `raw_sha256`（`00`*32），實檔不符 | `RAW_DIGEST_MISMATCH` | `10_neg_FG2_FABRICATED_RAW.log` exit 1 |
| JSON 整數 `1` 當布林票 | `VOTE_TYPE_INVALID` | `10_neg_FG3_INT_ONE_VOTE.log` exit 1 |
| 同 process 兩票（新增） | `PROCESS_ID_DUPLICATE` | `10_neg_FG4_PROCESS_DUP.log` exit 1 |
| raw 逐字稿解析不到 | `RAW_EVIDENCE_UNREADABLE` | `10_neg_FG5_RAW_ABSENT.log` exit 1 |
| `value` 本身是整數 `1` | `VALUE_NOT_BOOLEAN` | `10_neg_FG6_INT_ONE_VALUE.log` exit 1 |
| 對照組（同一支 binary、合格票） | — | `10_neg_POS_CONTROL.log` **exit 0** |

`--selftest` 由 7 案擴為 **17 案**，全數 expected/observed 相符：`02_selftest.log` exit 0
（`ff23380612279cc13389cfd84e4cd2ca7bbb75b8c0daf31ccc8c4de2f4581f49`）。
保留 `NEG-Q1/Q2/Q4/Q5/Q7/Q1b`、`POS-Q3` 綠燈；新增 `NEG-Q8/Q9/Q10/Q11/Q13/Q15/Q16/Q17`、`POS-Q12/Q14`。

其他規則：`--raw-root`（預設 = round root）；lane 重複仍只扣票由 quorum 算術決定（故 `NEG-Q4` 維持
`SIGNED_VOTE_QUORUM_FAIL`）；integrity 類拒絕則獨立否決該 property。

## 真實簽章票仍然有效（未改任何 signed receipt）

`05_real_repairs_eval.log`（`187c7812d7b9b399a8f372a9b4ac86333d9fd4709bcfc8d473f9eafc00119977`）：

- `WP-FHS-00:L1:817 exceptions_preserved`：baseline `ACCEPTABLE_FOR_FHS_READER_SCOPE` → 修復後
  `ACCEPTABLE_FOR_FHS_READER_SCOPE`，binding form `manifest_as_measured`；以 provenance 當 `--raw-root`
  則為 `raw_bytes`（`889f1685…` 精確命中）。
- `WP-FHS-01:L1:812 scope_preserved`：同上，`2f3df8fc…`。
- 全 round 掃描：`receipts=10`、`properties_checked=128`、`repair_properties=2`、
  `legacy_properties=126`、`findings=[]`、`ok=true`、exit 0（`03_scan_round.log`
  `ccf5ea3d3570ecc2bc0727c0ff14ee0beae03a8167c0b227fa0168f4572f1739`）。

**量測到的關鍵事實**：兩張真票的 `raw_sha256` **不等於** payload 內 `votes/raw_*_r25.txt` 的位元組摘要
（PLAN：宣稱 `889f1685…`／實檔 `664147c5…`；VERIFY：`2f3df8fc…`／`f6356547…`），且兩者相差 74 B 卻差 167 行，
**不是**行尾正規化孿生。宣告摘要對應的是產地 `lanes/votes/` 的 as-measured 位元組，而 payload
`MANIFEST.json` 本身就宣告了這一對（`sha256_as_measured`／`sha256`）。因此修復採「manifest 錨定」：只有當
`sha256_as_measured == raw_sha256` **且** payload 副本重算等於 manifest `sha256` 時才計票（`NEG-Q17`
證明副本漂移會被 `RAW_DIGEST_MISMATCH` 擋下）。

## R26-01_GAP（明確選擇 (b) `--strict` 專屬）

4/4 真票缺 `raw_path`（用 `raw_file`）、`timestamp`（用 `at`）、`session_id`、`process_id`。
前兩者以宣告別名表讀取（不靜默）；後兩者**只**在 `--strict` 下要求，否則 `PROCESS_IDENTITY_MISSING`
（`05` log 顯示兩張真票在 strict 下即 HOLD）。理由：量測 0/4，若設為硬要求就必須改 signed receipt 才能維持驗證，
而 `_COMMON.md` 禁止。此為 `R26-01_GAP`，非未竟事項。

## CI

`.github/workflows/fhs-w0-gate.yml`：r26 selftest 步驟標籤改為 17 cases，並**新增** fail-closed 掃描步驟
`python tools/verify_quorum.py --root .`；其餘步驟未動。五個 r26 步驟實際重跑：
`08_ci_steps.log`（`539cf3403ff45b218f9e62effc459c40c08dc514ed1b570ba8c72561d5ac009f`）
`ALL_STEPS_EXIT: 0`；round gate `VERDICT PASS pass=16/16 blocking_fail=0`（`06_gate_payload.log`
`05514dbdead8ad6b724835f79ffa7037ee94b44d9f2aaa3254881f725d36b2c7`）。

## 未主張

- 126 個 legacy `votes`（dict 形）property 仍無 per-vote candidate binding（本修復契約只涵蓋 `votes_r25`，
  量測值見 `legacy_properties`）；其型別已改為精確（`VOTE_TYPE_INVALID`）。
- `verify_reader_ack.py` 在本 payload 無法執行（`lanes/CLAUSES.json` 未隨 payload 出貨），此為既有狀況、
  與本次修改無關（`07_reader_ack.log` exit 1）；其 in-process `evaluate()` 路徑已直接驗證
  （`05` log `repaired_in_process_no_raw_root` = `ACCEPTABLE_FOR_FHS_READER_SCOPE`）。
- 未 push、未開 PR、未動 main；`QUORUM_MIN`（2）與 signed 檔 schema 未變；r25 round 自己的
  `verify_quorum.py` 未動。

## 檔案

```
evidence/fhs-w0-r26-repair-20261109/tools/verify_quorum.py   4a86ef7d4942dd064c43e5ec19be584d0be7a36f0115a03b174880ebf1a9d2a4
evidence/fhs-w0-r26-repair-20261109/MANIFEST.json            c775cf38dafeade572f5aaac01ffea8384d969c46b0fa89e8373e309decea7d8
evidence/fhs-w0-r26-repair-20261109/SHA256SUMS               10e43543c570618abccbd772c33c231d84a7763de51c5920df882437365868cc
.github/workflows/fhs-w0-gate.yml                            ea5b98cd1e458c8279ba7710945fdbbe57f08fddeb58d90328aab2fd5a52e7f1
```
