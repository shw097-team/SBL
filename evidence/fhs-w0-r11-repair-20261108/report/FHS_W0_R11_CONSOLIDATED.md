# FHS W0｜r11 整合交付（給外部驗收官）

> **一句話**：r10 修好的三個閘缺陷是「現在壞」，本回合修的是「**未來才會壞**」的三條假綠路徑——
> 空 manifest、不完整掃描、把 optional extra 當成已安裝。三條各有一個否證條件，並由車道直接 import
> 本回合的閘獨立重現（三項全部 reproduced）。另外改正一句我自己寫錯的 `yaml` 語意，並讓 CI 真的跑閘。
>
> **ClaimCeiling**：`AUTHOR_SIDE_MEASURED_WITH_SCOPED_HOLDS`
> **不主張**：`ORIGINAL_ACK`、`NATIVE_WORLDRAW`、`INDEPENDENT_PASS`、`RELEASE_GRANTED`、已併、已審、已發行、canonical 已定。

## 1｜可重算身份

| 事實 | 值 |
|---|---|
| 文件 | `FHS_PIPD-LS-PKG_W0_r11.md`，**577,257 B**，sha256 `24fb2d9ec5d2f220496647088463819bbc0a3082fc5fc754491408bda1d1316e` |
| SBL LF 版 | **577,175 B**，sha256 `1833e21b2c9a24e4f8a4f3426529043e601c23388fec32aaec273ebe055258ff` |
| 父本 | r10，568,120 B，`2285baaf37884399d85d114672a2a4ca155420af184e5c473d18b0d7a32f1859`，逐位元前綴 |
| 鏈 | r5→r6→r7→r8→r9→r10→r11，每環附 digest 與「是前一版的逐位元前綴」 |
| 閘 | **15/16 PASS**、blocking 0、open reporting 1 |
| selftest | 13 FIRED、2 EXEMPT、1 BASELINE_RED |
| 錯層稽核 | `out/LAYER_AUDIT.json` |

## 2｜七項 EC-R10 的處置

| ID | 判定 | 一句話 |
|---|---|---|
| `EC-R10-001` | **CLOSED** | 整合交付與報告改由 builder 產生；車道掃出 11 個 STALE 並全部重建 |
| `EC-R10-002` | **CLOSED** | `G18`：缺鍵 / 空集合 / 與 `expected_entry_set` 不符，三種都紅 |
| `EC-R10-003` | **CLOSED** | `G16b`：`scan_complete=false` → `UNQUALIFIED_INCOMPLETE_SCAN` |
| `EC-R10-004` | **CLOSED** | required／extras 分離，覆蓋以預設安裝為準，`G16c` 驗 optional 語意 |
| `EC-R10-005` | **CLOSED（更正）** | `yaml` 由 `fail-open` 改為 **DEGRADED_BUT_BOUNDED** |
| `EC-R10-006` | **CLOSED** | selftest 計數逐列導出；`G16b` 是 BASELINE_RED，不是 EXEMPT |
| `EC-R10-007` | **CLOSED** | 新增 workflow 呼叫 `gate_r11.py --profile payload` |

## 3｜三棵 HG-KSEOS（未變）

| | `HG-KSEOS@6c9fc73` | `r4-hgk@a7046a3` | `GitHub-main@acd9196f` |
|---|---|---|---|
| deps | null | [] | [] |
| 未宣告 | [{'module': 'yaml', 'distribution': 'PyYAML', 'verdict': 'FAIL_OPEN', 'import_sites': 1, 'paths': ['src/hg_kseos/lane_policy.py']}] | [{'module': 'cryptography', 'distribution': 'cryptography', 'verdict': 'UNGUARDED', 'import_sites': 10, 'paths': ['src/hg_kseos/fhs/issuer_binding.py', 'src/hg_kseos/native_admission.py', 'src/hg_kseos/user_trust.py']}, {'module': 'yaml', 'distribution': 'PyYAML', 'verdict': 'FAIL_OPEN', 'import_sites': 1, 'paths': ['src/hg_kseos/lane_policy.py']}] | [{'module': 'cryptography', 'distribution': 'cryptography', 'verdict': 'UNGUARDED', 'import_sites': 10, 'paths': ['src/hg_kseos/fhs/issuer_binding.py', 'src/hg_kseos/native_admission.py', 'src/hg_kseos/user_trust.py']}, {'module': 'yaml', 'distribution': 'PyYAML', 'verdict': 'FAIL_OPEN', 'import_sites': 1, 'paths': ['src/hg_kseos/lane_policy.py']}] |
| nested 授權 | 8 | 0 | 0 |
| CI | 0 | 0 | 0 |

`G16b` 因此仍 `OPEN`。哪一棵是 W0 基準 → `HGK-REF-CANONICAL`（owner）。

## 4｜一份 OWNER 待辦（不逐一回頭問）

| # | 待辦 | FirstFail | Resume |
|---|---|---|---|
| 1 | `HGK-REF-CANONICAL` | `TWO_CHECKOUTS_DIFFER` | 指名 HEAD 後重跑 `G16a/G16b` |
| 2 | `HGK-DEPENDENCY-EXTRA` | `UNDECLARED_DEPENDENCY` | 兩份 patch 已備，套用後應轉綠 |
| 3 | `AUTHORITY-COLLISIONS` | `NAME_COLLISION_DIFFERENT_DIGEST` | 指名 r6 權威 digest |
| 4 | `LICENCE-FABRIC-HGK` | `LICENCE_ABSENT_AT_ROOT` | 根層 LICENSE/NOTICE 落地 |
| 5 | `HGK-CI-ABSENT` | `CI_SERVICE_ABSENT` | 有 workflow 或明示不建 |
| 6 | `R1-ISSUER-REV14` | `REGISTRY_REV13_NO_ISSUER_RECOVERY` | 受保護終端開窗 |
| 7 | `PIPD-15-VALUESET` | `CONTRACT_FAMILY_VALUE_SET_UNCLOSED` | 15 family 閉合 |
| 8 | `ORIGINAL-ACK-18` | `ORIGINAL_READER_ACK_UNOBSERVED` | 任一原域 Reader 同 scope 收據 |

## 5｜自我錯誤

見 `out/SELF_ERRORS.md`（E-S01..E-S13）。本回合新增兩條：**手寫的數字會過時**（E-S12）、**修好的檢查本身還要有否證條件**（E-S13）。
