# GOAL_TO_FUO｜Goal → Product SPEC → W0 Deliver → FUO 可讀回鏈

> claim_ceiling=`AUTHOR_LOCAL_TEST`；native_effect=`NOT_RUN`

## 輸入 Goal

```text
讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC
```

| digest | 值 | 規則 |
|---|---|---|
| input_sha | `5b9017816b5af080c85d5f66355f80b9753fd4839e24707a22fd82aca079bdb8` | sha256(goal.encode('utf-8')) |
| output_sha | `e60dc4bb3dc97d4741cede8c9e9e779f92e5171eda03b3ad6b1e36c6fbca5f3c` | sha256(bytes of out/SPEC_Product.json) |
| readback_sha | `d8789363dde838e9dc9fc762b9c36c0977af8f76e0bff5c4ea6c884f674d66d2` | sha256(canonical_json(doc without 'readback_sha'))；canonical = sort_keys + separators(',',':') + ensure_ascii=False + UTF-8 |

## 主鏈 CHAIN-FUO-INT-03（共 11 條，全部由 Product SPEC 的 FUO 實算）

### FUO-FHS-DR-002 → `DEL-W0-FHS-DR-002`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-FHS-DR-002` | `-` | {"deliver_id": "DEL-W0-FHS-DR-002", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-E… |
| 4 | FUO | `FUO-FHS-DR-002` | `15a1fc1fc6891aa6` | Goal 不需先選九個 MissionOptions 或填完整 PIPD Schema |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`15a1fc1fc6891aa6235abbf7868984c14fbb688e2187feaab25e43834b830b1d`
- goal_relevance（bigram 重疊，僅排序用）= 0.055556

### FUO-FHS-DR-003 → `DEL-W0-FHS-DR-003`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-FHS-DR-003` | `-` | {"deliver_id": "DEL-W0-FHS-DR-003", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-E… |
| 4 | FUO | `FUO-FHS-DR-003` | `876601b8af8126fd` | 模糊 Goal 可以進三 SPEC，來源缺件只保留受影 Need |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`876601b8af8126fd2a94214f036ef4bf953f59b60d47f80c4c0879a85a2517d3`
- goal_relevance（bigram 重疊，僅排序用）= 0.111111

### FUO-FHS-DR-021 → `DEL-W0-FHS-DR-021`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-FHS-DR-021` | `-` | {"deliver_id": "DEL-W0-FHS-DR-021", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-E… |
| 4 | FUO | `FUO-FHS-DR-021` | `cb81cedd6c2b1960` | Portable TPM 能以 PM/SE/TPgM 產三獨立 SPEC |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`cb81cedd6c2b19608473bd9e3902c6f9f8c8bdd63c46acba9c7d6ffcebf987e7`
- goal_relevance（bigram 重疊，僅排序用）= 0.111111

### FUO-FHS-DR-022 → `DEL-W0-FHS-DR-022`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-FHS-DR-022` | `-` | {"deliver_id": "DEL-W0-FHS-DR-022", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-E… |
| 4 | FUO | `FUO-FHS-DR-022` | `4ed61e0655b07977` | 18 Stage/K0–K3 及原問題去重仍遵守 |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`4ed61e0655b079776f72e43766528aa322fcce468ab7a15b43bfe0f433e05d2d`
- goal_relevance（bigram 重疊，僅排序用）= 0.027778

### FUO-FHS-DR-047 → `DEL-W0-FHS-DR-047`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-FHS-DR-047` | `-` | {"deliver_id": "DEL-W0-FHS-DR-047", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-E… |
| 4 | FUO | `FUO-FHS-DR-047` | `0e2df8d69c2cc508` | LOCAL_DRAFT_WRITE 需隔離 output root/原文未修改 |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`0e2df8d69c2cc5084847e4a4832c0dcc74009b17f8b85ff657c2cd16a90ae43e`
- goal_relevance（bigram 重疊，僅排序用）= 0.027778

### FUO-FHS-DR-055 → `DEL-W0-FHS-DR-055`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-FHS-DR-055` | `-` | {"deliver_id": "DEL-W0-FHS-DR-055", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-E… |
| 4 | FUO | `FUO-FHS-DR-055` | `0dbea6bb837ac3e6` | L0/L1/L2/L3 是文檔視圖，非四套 Canonical |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`0dbea6bb837ac3e60a7ecfc1b4a36b8ab4cf5ffb11a12ef12f58be63b1dd63f2`
- goal_relevance（bigram 重疊，僅排序用）= 0.055556

### FUO-INT-01 → `DEL-W0-INT-01`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-INT-01` | `-` | {"deliver_id": "DEL-W0-INT-01", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-EXAMP… |
| 4 | FUO | `FUO-INT-01` | `5e03d14224a5fcea` | 以 Subject+Scope+SourceSHA 鍵重用 KnownAnswer/QuestionLedger，只有差額重問 |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`5e03d14224a5fcea75818f8b3767b2a98bc8cb15bb33e767df8cece4dd0008d7`
- goal_relevance（bigram 重疊，僅排序用）= 0.083333

### FUO-INT-03 → `DEL-W0-INT-03`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-INT-03` | `-` | {"deliver_id": "DEL-W0-INT-03", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-EXAMP… |
| 4 | FUO | `FUO-INT-03` | `a3a2ae508726367c` | 短 Goal 可產直接有用答案／SPEC，寫入則需實際 Diff/Host |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`a3a2ae508726367c4482f398b5cb8f81412f2b9f715189a4bd7bd51c458fe221`
- goal_relevance（bigram 重疊，僅排序用）= 0.138889

### FUO-INT-04 → `DEL-W0-INT-04`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-INT-04` | `-` | {"deliver_id": "DEL-W0-INT-04", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-EXAMP… |
| 4 | FUO | `FUO-INT-04` | `fb00bbd7b218bfda` | A 全量產品語義守恆；B 最短合法 Effect 路徑 |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`fb00bbd7b218bfdadb70223065fd71ed3d998568a36ee372cd26045376940d25`
- goal_relevance（bigram 重疊，僅排序用）= 0.055556

### FUO-INT-12 → `DEL-W0-INT-12`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-INT-12` | `-` | {"deliver_id": "DEL-W0-INT-12", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-EXAMP… |
| 4 | FUO | `FUO-INT-12` | `cd3f22cf8a768da9` | PM JTBD/FUO；SE ADR/ABI；TPgM DAG/Exit |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`cd3f22cf8a768da908652b3bf9289f4c5a3897ed05a7c443582ce364f5f432fe`
- goal_relevance（bigram 重疊，僅排序用）= 0.138889

### FUO-INT-18 → `DEL-W0-INT-18`

| # | step | ref | sha256 | value |
|---|---|---|---|---|
| 1 | GOAL | `user_goal` | `5b9017816b5af080` | 讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC |
| 2 | PRODUCT_SPEC | `SPEC_Product.json` | `e60dc4bb3dc97d47` | SPEC-Product-W0-wp15-local |
| 3 | W0_DELIVER | `DEL-W0-INT-18` | `-` | {"deliver_id": "DEL-W0-INT-18", "primary_wp_id": "WP-FHS-15", "subject_id": "FHS-W0-EXAMP… |
| 4 | FUO | `FUO-INT-18` | `a32e5a4e493303c7` | 六類 Effect 對應最低充分原 Evidence |

- readback：fuo_in_spec=True / deliver_in_spec=True / statement_sha256=`a32e5a4e493303c769fb94c87e32b6ecfc213e3d0b17c2100b4e8ec0487cfb05`
- goal_relevance（bigram 重疊，僅排序用）= 0.055556

### 宣告但未升格為 chain 的 FUO

- `FUO-A`, `FUO-B`
- CH-01 宣告的 FUO-A／FUO-B 只有章級 W0 綁定，沒有 W0_REQUIRED 的 deliver_id，因此不升格為 chain，只列名。

### 綁定方法與上限

- method：`AUTHOR_TOKEN_OVERLAP_HEURISTIC` — character-bigram overlap between the goal and each FUO's statement+acceptance-pos+acceptance-neg; rank only, NOT an original Reader semantic binding
- original_reader_ack：`NOT_OBSERVED`
- 本鏈只證明「同一份 Product SPEC 內可讀回」，不證明原 SBL/PIPD Reader 接受。
