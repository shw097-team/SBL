# L3 結果 — 來源中介資料修補 + 七份 owner 簽章真驗

**status: PASS**（三項 defect 已修並以本輪真實命令佐證；兩項 finding 誠實轉為 OPEN）
分支 `r27/metadata-hygiene`，commits `dde086d`、`8353ae6`。未 push、未動 main。

## Part A — L1 bytes/lines（EC-R26-004 / EC-R26-011）

| 項目 | 修正前 | 修正後（本輪量測） |
|---|---|---|
| `source_contract.l1.bytes` | `111331`（其實是 31 冊行數總和） | `6224679` |
| `source_contract.l1.lines` | 不存在 | `28005`（`len(read_bytes().split(b"\n"))`） |
| 31 冊行數 | 塞在 `l1.bytes` | `source_contract.source_inventory.total_lines = 111331` |
| `l0` / `l2` / `w_skeletons` | 不存在 | 每單位帶 `path` / `bytes` / `lines` / `sha256` / `measured_from` / `measured_sha256_of_source` / `measured_at` |

- L1 實檔：`.../藍圖/FHS_PIPD-LS-PKG_藍圖_r4.md`，`st_size=6224679`、`lines=28005`、`sha256=cbdd75fd…`（與 ACK 原 `l1.sha256` 相同，故 owner 簽章所綁的值沒動）。
  log `evidence/L3/measure_l1_blueprint.log`（exit 0，sha256 `0bab1f9e…`）。
- 另有一份 byte-identical 複本在 `%TEMP%/bp_r4/L1.md`（同 sha256、同 bytes）。

### 76 property 分母（EC-R26-004）

`32-4=28` 是把「全部 32 條 clause」和「單一 WP 的 4 個 property」混在一起減。實測：

```
WP-FHS-15  12 clauses  48 properties
WP-FHS-16   4          16
WP-FHS-19   2           8
WP-FHS-21   1           4
TOTAL      19          76      → 19 x 4 = 76
```

parser 與 76 一致（沒有硬套）。log `evidence/L3/count_preservation_properties.log`（exit 0，sha256 `33b4fff2…`）。

### G24 typed check + 負例

在 `tools/gate_r20.py` 的 G24 內新增 `_g24_source_contract_bytes()`：每個宣告的 L0/L1/L2/W1–W4
`bytes`/`lines` 都從檔案本身重導，不符即拒絕。

| 負例 | mutation | observed code | exit | log |
|---|---|---|---|---|
| NEG-1 | `l1.bytes → 111331`（原缺陷） | `SOURCE_CONTRACT_BYTES_MISMATCH` | 1 | `gate_negative_mutated_ack.log` |
| NEG-2 | `l1.lines → 28004`（錯的換行慣例） | `SOURCE_CONTRACT_BYTES_MISMATCH` | 1 | `gate_negative_lines_ack.log` |
| NEG-3 | `l1.sha256 → 64 個 0` | `SOURCE_CONTRACT_SHA_MISMATCH` | 1 | `gate_negative_sha_ack.log` |
| NEG-4 | 移除全部單位 | `SOURCE_CONTRACT_ABSENT` | 1 | `gate_negative_absent_ack.log` |
| **控制組** | 同一 mirror 不改 | `OK`，16/16 PASS、8/8 重導 | 0 | `mirror_control.log` |

### 就地修改的選擇（Part A.5）

走 **in-place**，理由可重算：ACK 不被任何簽章覆蓋（無 signed envelope 引用其檔案 digest；owner
語意接受只內嵌 `source_contract.l1.sha256` 與 `coverage_basis`，兩者皆未變動），所以修完後重跑
`verify_public_bundle.py` 仍 **7/7** — 這是「沒動到簽章 payload」的直接量測。它只被 payload 自己的
`MANIFEST.json` / `SHA256SUMS` 綁，已在同一 commit 重算並保留 `provenance_history`。
修補前 byte-identical 備份：`evidence/L3/FHS_ORIGINAL_ACK.r26_before.json`（`4c8307bb…`）。
**沒有**另寫 `FHS_ORIGINAL_ACK_R27.json`：`_COMMON.md` 明文禁止第二份受治理工件副本。

## Part B — EVIDENCE_SCOPE（EC-R26-009）

- `profiles.full.excluded = {}`；
- 同六個 gate 移到 `profiles.full.not_runnable_in_CI`，各一行理由；
- 依據：`gate/GATE_R26.json`（`scope=full`，21 PASS + 1 OPEN）六個 gate 都有真實 detail 行 —— 它們**跑過**，只是 CI 無法重現。
- `profiles.payload.excluded` 保留不動，因為 `--scope payload` 確實會移除這六個。

digest 變更（`digest_ledger.csv`，sha256 `1574acd0…`）：

```
EVIDENCE_SCOPE.json  dad2d715…(711B)  -> d710b203…(2905B)
FHS_ORIGINAL_ACK.json 4c8307bb…(10328B) -> b37ee99f…(20395B)
tools/gate_r20.py    4a7f3986…(106988B) -> 0b162197…(111345B)
MANIFEST.json        8f17ff96…  -> 2980993788…
SHA256SUMS           e482ef07…  -> 5919f109…
```

## Part C — 七份 owner 簽章真驗（EC-R26-008 / R26-06）

`tools/verify_public_bundle.py`（cryptography 50.0.2）。canonicalisation 取自簽章者本身
`sign_r26.py:25-26`：`json.dumps(body, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")`。
**可重現，不是 `CANONICALISATION_UNRESOLVED`。**

```
WP-FHS-00 / 01 / 15 / 16 / 19 / 21 / OWNER_SEMANTIC_ACK_R26   → 7/7 signature_valid=True
每個 recomputed payload_sha256 == envelope 宣告 == bundle 宣告
```

log `verify_public_bundle.log`（exit 0，sha256 `3c60b06f…`）；self-test 6/6 mutation 全數
`InvalidSignature` 拒絕（`verify_public_bundle_selftest.log`，sha256 `0af49391…`）。

### FINDING_R26-06_TZ_UNQUALIFIED（OPEN）

```
sequence.preauth_at  = "2026-11-09T19:22:25"        ← 無 offset
sequence.verify_pass_at = "2026-11-09T20:10:01+08:00"
sequence.signed_at      = "2026-11-09T20:10:02+08:00"
```
同一個未限定字串也被寫進簽章 body 的 `preauthorised_at`。`preauth_at < verify_pass_at` 因此要讀者
自己假設時區；按 UTC 讀會比按 +08:00 讀晚 8 小時，同一個 bundle 在兩種讀法下可能得出不同結論。
**未改寫**（改了就變成一張沒人簽過的收據）。owner 需重簽：新 envelope（新 `payload_sha256`、
新 `signature_hex`）+ `preauthorised_at` 帶明確 offset + bundle 的 `sequence` 與 `semantic_ack` 五個欄位。

## 另外量到、未修（誠實條列）

- **FINDING_R26-02_W4_DIGEST_TRUNCATED**：r26 基線表給 W4 的「SHA-256」是 **62 個 hex 字元**（SHA-256 是 64）。本機唯一 W4 skeleton 實測為 64 字元值，分歧點就在截斷處 → 是**截斷的 digest**，不是別的檔案的 digest。已記入
  `FHS_ORIGINAL_ACK.json#source_contract.source_contract_disagreements`，文字擁有者是 r27 文件車道。
- `tools/verify_reader_ack.py` 在 payload 版面跑不起來（`FileNotFoundError lanes/CLAUSES.json`；payload 放的是 `evidence/CLAUSES.json`）。**既有版面耦合，非本車道造成**；能跑的 G29 quorum reader 通過。
- full profile 在本機 15/22（`exit 2`）：G11/G13/G19/G26 缺 31 冊語料與 r26 round 的 `out/` 樹。**不宣稱 full 22/22**。

## Not claimed

full-profile 22/22 PASS、owner 意圖與 body 一致、r26 文件自身的 source-contract 表已正確、
六份 reader 收據是對 r26 的簽章（它們是對 r15 candidate）、G16b closed、`NATIVE_SIGNED` /
`RELEASE_GRANTED` / `INDEPENDENT_PASS`。
