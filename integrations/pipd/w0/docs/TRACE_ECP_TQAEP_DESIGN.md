# WP-FHS-21 — ECP / TQAEP 在 W0 的欄位與拒絕規則（TRACE_ECP_TQAEP_DESIGN）

狀態：`AUTHOR_LOCAL_TEST`／`AUTHOR_STATIC`；`native = NOT_RUN`；`wp19_done = false`。
本文件只描述 W0 作者端 projection 與拒絕規則，**不**宣稱 PIPD 正式 `ECP`／`TQAEP` 生成。

---

## 1. 釘住的原始介面（唯讀）

| 物件 | 值 | SHA-256 |
|---|---|---|
| `ECP` family（registry index 12） | `urn:pipd:s0:ECP:1`，`additionalProperties=false` | `33688671e6eec18229e3da35a210f0c88799d4e21c5378d0518cd1e4213c7331` |
| `TQAEP` family（registry index 13） | `urn:pipd:s0:TQAEP:1`，`additionalProperties=false` | `1e704b3f9942bdbe15cdfc9b1be9baf8880ac39841ef91fd7ddf2084eb0a9fa6` |
| `schemas/registry.json`（19 families） | `REQUIRED_NOW` 全 19 條 | `85100a8e5ba6320f6648d33a14099fb999b2c452a94aff1652854d2550065e9d` |
| `integrations/pipd/src/pipd_ls_sp/cli.py` | 13 subcommand（與 S2 pin 同值） | `321e9512e61ddcf57498820472605237f93064a78275812327648107aba59f7c` |

原始 required 欄位（不可改名、不可增刪）：

- **ECP**：`effect_intent`, `permission`, `retries`, `idempotency`, `readback`, `rollback`, `subject_id`, `version`, `content_hash`, `schema_version`（owner `PIPD/ECP semantics`；consumer `HGK/TQAEP`）。
- **TQAEP**：`tests`, `oracles`, `fixtures`, `acceptance`, `requalification`, `subject_id`, `version`, `content_hash`, `schema_version`（owner `PIPD/TQAEP semantics`；consumer `Independent checker/release`）。

分層不變式（INT-13／CH-15／CH-41）：`PI source-bound`、`PD 晚綁 Repo`、`ECP 非 Admission`、`TQAEP 依 Original Oracle`。

---

## 2. 本波 ECP projection（欄位）

本波只出 **envelope**，envelope 的 `ecp_body` 恰好是上面 10 個原始 required 名，一個不多、一個不少；作者側資訊全部放在**兄弟鍵** `author_meta`，不進 body（因此不觸犯 `additionalProperties=false`）。

```json
{
  "projection_schema": "FHS.W0.ECP_PROJECTION/v1",
  "canonical_id_claimed": false,
  "ecp_body": {
    "effect_intent":  {"effect_class": "DEV|OPS|USER|RELEASE", "operation_type": "…|EFFECT_UNBOUND", "target_scope": "…", "write_set": "…|UNBOUND"},
    "permission":     {"expected_permission": "NONE_GRANTED|EXPECTED_ONLY|UNBOUND", "issuer": "ORIGINAL_HGK_ONLY", "policy_epoch": "NOT_OBSERVED", "loaded_sha": "NOT_OBSERVED", "permit_issued": false},
    "retries":        {"declared": true, "max_attempts": "UNBOUND"},
    "idempotency":    {"nonce_ref": "UNBOUND", "replay_window": "UNBOUND"},
    "readback":       {"world_reader": "ORIGINAL_WORLD_READER_UNBOUND", "expected_raw": "EXPECTED_NOT_OBSERVED"},
    "rollback":       {"preimage_ref": "UNBOUND", "rollback_ref": "UNBOUND"},
    "subject_id":     "FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001",
    "version":        "W0-AUTHOR-PROJECTION",
    "content_hash":   "<sha256(canon(ecp_body 除 content_hash 外)>",
    "schema_version": "ECP.author-projection/1"
  },
  "author_meta": {
    "claim_ceiling": "AUTHOR_LOCAL_TEST",
    "runtime_binding": "UNBOUND",
    "is_admission": false,
    "cli_command": "none — 本波為 compile-ecp 輸出之唯讀消費者",
    "source_projection_of": "urn:pipd:s0:ECP:1"
  }
}
```

規則：

1. `permit_issued` 恆為 `false`；本波不簽發 Permit、不建 Lease、不造 SharedSpine。
2. `effect_class` 只允許單值；`DEV`／`OPS`／`USER`／`RELEASE` 不得混用（CH-15）。
3. 無法從原 Reader 取得的欄位一律寫 `UNBOUND`／`NOT_OBSERVED` 字面 token，**不得**填猜測值或預設值。
4. ECP 不得被當成 Admission 憑據；`S4` 的 `permission` 只承載 `NONE_GRANTED`／`EXPECTED_ONLY`，語義為「期望值」而非授權。

---

## 3. 本波 TQAEP projection（欄位）

`tqaep_body` 同樣只有原始 9 個 required 名；數值全部可由 runner 輸出重算。

```json
{
  "projection_schema": "FHS.W0.TQAEP_PROJECTION/v1",
  "canonical_id_claimed": false,
  "tqaep_body": {
    "tests": [
      {"case_id": "AC-C39-POS-DETERMINISTIC", "case_type": "POS",
       "oracle_type": "DETERMINISTIC", "source_parent": "…", "expected_firstfail": "MISSING_POS_FUNCTION"}
    ],
    "oracles": [
      {"oracle_type": "DETERMINISTIC", "independent": true,
       "executor": "FHS-W0-WP21-STRUCTURAL-ADAPTER/1", "native": false,
       "predicate": ["eq_path", ["expected_value", "observed_value"]]}
    ],
    "fixtures": [{"pos": "fixtures/<case>.pos.json", "domain_neg": "…", "oracle_neg": "…", "sha256": "…"}],
    "acceptance": {"expected_equal_observed": 96, "replay_rows": 288,
                   "replay_consistent": 288, "seam_sealed": 5,
                   "swap_mismatch": 48},
    "requalification": {"wave": "W4", "e26": "UNSATISFIED_WP19_RAW_MISSING",
                        "wp19_done": false, "native": "NOT_RUN"},
    "subject_id": "FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001",
    "version": "W0-AUTHOR-PROJECTION",
    "content_hash": "<sha256(canon(tqaep_body 除 content_hash 外)>",
    "schema_version": "TQAEP.author-projection/1"
  },
  "author_meta": {
    "claim_ceiling": "AUTHOR_LOCAL_TEST",
    "independent_checker": "ORIGINAL_CHECKER_UNBOUND",
    "maker": "author", "checker": "ORIGINAL_CHECKER_UNBOUND",
    "source_projection_of": "urn:pipd:s0:TQAEP:1"
  }
}
```

規則：

1. `tests` 恆為 96（12 case_type × 8 oracle_type）；`fixtures` 恆為 288（96 × POS/DOMAIN_NEG/ORACLE_NEG）。
2. `oracles[].executor` 只允許宣告式 adapter；`native` 恆 `false`，不得以作者觀察冒充原 Oracle 裁決。
3. `acceptance.expected_equal_observed` 必須逐案可重算；`expected_firstfail` **不得**作為 adapter 的輸入（見 §5 R6）。
4. `requalification.e26` 在本波只能是 `UNSATISFIED_WP19_RAW_MISSING`；TraceClosure 不得填入。

---

## 4. 拒絕規則（FirstFail）對照表

`執行` 欄誠實標示本波是否真的被 runner／測試觸發；`design` 表示本波只宣告、W1/W2 才會有原 Reader 可執行。

| # | code | 觸發 | 執行 | 證據 |
|---|---|---|---|---|
| R1 | `ECP_AS_PERMIT_DENY` | ECP body 出現 `permit_issued=true`，或以 ECP 意圖冒 HGK Issuer Permit | 部分（欄位層） | `out/SEAM_S1_S5.json` S4 `effect_permission.permit_issued=false`；`tests` 斷言 |
| R2 | `EFFECT_CLASS_COLLAPSED` | DEV/OPS/USER/RELEASE 混用或全歸一類 | design | 本波不執行 effect；W2 CH-15 原 ECP Writer 才判 |
| R3 | `ECP_ADMISSION_CONFUSION` | ECP 被當 Admission／WorkOrder | design | INT-13 分層；S4 僅 `NONE_GRANTED` |
| R4 | `ECP_CANONICAL_ID_CLAIMED` | projection 自稱 `urn:pipd:s0:ECP:1` 正式件 | 是（結構） | `projection_schema` 分離＋`canonical_id_claimed=false`；輸出檔名不含 `PI-PKG/PD-PKG/ECP/TQAEP` |
| R5 | `ORACLE_TYPE_OR_SCOPE_MISMATCH` | fixture 換手（型別/範圍不符） | 是（48/48） | `ORACLE96_RUN_RAW.json` swap 48/48；`adapter_shape_gate` 精確鍵集比對 |
| R6 | `FIRSTFAIL_MISMATCH` | `expected_firstfail` 被改或 observed 不同 | 是（96 列＋NEG） | `out/ORACLE96_RUN_RAW.json` `verdict`；NEG 測 `TestNegFirstFail` |
| R7 | `TQAEP_SELF_SIGNED` | maker 與 checker 同一主體 | 是（S5） | `SEAM_S1_S5.json` S5 `principal_separated=true`；NEG 測 `test_s5_principal_collapse_is_named` |
| R8 | `EVIDENCE_LAUNDERING_DENY` | 字串 `PASS` 無 Raw／無 observed | 是（結構） | adapter 對違規 fixture 只回 class code，永不回 `AUTHOR_FIXTURE_STATIC_PASS` |
| R9 | `WP19_RAW_SUBSTITUTION` | 以 TraceClosure 充 WP19 CI/License/NOTICE/SBOM raw | 是（狀態） | `out/TRACE_CLOSURE_AUTHOR_STATIC.json`：`scope=AUTHOR_STATIC`、`wp19_done=false`、E26 `UNSATISFIED_WP19_RAW_MISSING` |
| R10 | `SEAM_FIELD_MISSING` | seam 必要欄位（含 `permission`／effect 面）缺漏 | 是 | NEG 測 `test_missing_permission_yields_seam_field_missing` |
| R11 | `DAG_E26_DIRECTION_INVALID` | E26 反向或端點被改 | 是 | NEG 測 `test_reversed_e26_yields_direction_invalid` |
| R12 | `WAVE_COUNT_MISMATCH` | 84/25/22 計數漂移 | 是 | NEG 測 `TestNegWaves`（3 條） |
| R13 | `ORIGINAL_READER_ACK_UNOBSERVED` | 無原 Reader ACK 就想升格 | 是（狀態） | `SEAM_S1_S5.json`、`W1_W4_CONSUMER_HANDOFF.json` |

---

## 5. 與原 PIPD 19-schema 的界線

1. **不新增第 14 個 CLI 命令**。原 `cli.py`（pin `321e9512…`）恰有 13 個 subcommand：
   `init`, `intake`, `profile`, `compile-pi`, `bind-pd`, `compile-ecp`, `compile-tqaep`,
   `validate`, `doctor`, `project`, `export`, `diff`, `repair`。
   `trace_runner.py` 的 CLI 是**作者側工具**（`--source-root`／`--out`），不在 PIPD 命令面內，也不呼叫任何 pipd 子命令。
2. **不動 19 families**：本波不新增、不改名、不重排 `registry.json`（19 條 `REQUIRED_NOW` 不變，SHA 見 §1），也不新增 schema 檔。
3. **不宣 `$id`**：`urn:pipd:s0:ECP:1`／`urn:pipd:s0:TQAEP:1` 只作「唯讀來源標註」（`source_projection_of`），本波輸出不得自稱該 `$id` 的實例。
4. **不塞作者欄位**：因 `additionalProperties=false`，任何作者欄位都不得寫進 canonical body；projection body 只放原始 required 名，作者資訊一律放 `author_meta` 兄弟鍵。
5. **不冒正式產物**：輸出檔名與內容不得出現 `PI-PKG`／`PD-PKG`／`ECP`／`TQAEP` 正式件語義；一律以 `*_RUN_RAW`／`SEAM_S1_S5`／`TRACE_CLOSURE_AUTHOR_STATIC` 命名，`claim_ceiling=AUTHOR_LOCAL_TEST`。
6. **不改原 Reader 責任**：Producer/Consumer 只是 `original_consumer` 字串來源；本波不簽 ACK、不簽 Permit、不建 queue/journal、不寫 Repo。

---

## 6. 本波明確不做

- 不執行 `compile-ecp`／`compile-tqaep`，不產 canonical `ECP`／`TQAEP`。
- 不執行任何 Host / Issuer / Protected Checker / Publisher effect。
- 不產 WP-FHS-19 的 CI／License／NOTICE／SBOM raw；E26 維持 Hard 且未滿足。
- 不以 96/96、288/288 的 static 對齊推論 Native 或 release readiness。
