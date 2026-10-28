## 0c. Wave 2 工具鏈已建置並跑滿 corpus（2026-10-28，0 解鎖 0 提權）

- `wave2/wave2_queue.py`：可續跑佇列（park／resume／append-only journal），自測 6/6。
- `wave2/run_case_cli.py`：單案 CLI；**關鍵修正**——`b1run` 把 SB/CASES/LEASES/JOURNAL 寫死，所有 case 共用一個 sandbox，重跑 POS 會看到上一次的 effect bytes 而假失敗（實測 1 done/2 parked → 修正後 4 done/0 parked）。
- `wave2/native_admit_bridge.py`：bundle 建構＋**直接呼叫 `hg_kseos.native_admission.verify_signature`** 驗簽；自測 5/5（含 4 個負例）。
- `wave2/gb_native_rederive.py`：G-B 以 native effect 重導，5/5 通過；發現 `revoke.registry_revoked_epochs=[]`（撤銷未進 registry）。
- **corpus：244/244 done、0 parked**（120 parents + 124 children），ceiling 仍是 `AUTHOR_SIDE_EXECUTED_SANDBOX`。
- 收據：`wave2/WAVE2_RECEIPT.json`。

---

## 0b. Wave 1 前置已完成（2026-10-28 晚）

- **D-13 修好**：`owner_ceremony.ensure_key()` 不再在信封存在時生成新金鑰（原本會靜默輪替 owner 身分並落明文）。實測：真路徑 + 無口令 → `REFUSED_OWNER_KEY_LOCKED` rc=6，`~/.hgk-owner` 仍只有 `owner.key.enc`。
- **D-14 修好**：load-once，31 次開封 → 0（`wave1/ceremony_fix_acceptance.json`，四項全過）。
- **待 OWNER**：`wave1/elevated_setup.ps1 -Apply`（一次提權）→ 填 `wave1/native_registry_proposal.json` 的 7 個未定欄位 → 簽 rev10（`wave0/runner_registry.rev10.candidate_v2.json`）。

---

## 0. Wave 0 已完成（2026-10-28，0 解鎖 / 0 提權 / 0 簽章 / 0 promotion）

證據：`wave0/WAVE0_RECEIPT.json`（16 artefact + sha256）、`wave0/n2_selftest.json`（19/19）、
`wave0/n6_alias_probe.json`（4/4）、`wave0/fabric_stage/promotion_receipt.json`（4 raw、正確拒絕）、
`wave0/registry_rev10_proposal.json`（待簽 root `14b67608…`）。

- N-6 alias 已宣告並落地在 dispatcher（`ARM_ALIASES` / `canonical_arm`），收據同時記 `served_arm_raw`。
- N-2 六支 runner 已實作並自測（正例＋刻意負例），**尚未綁進 registry**：`executable_path`/`sha256` 在 Merkle leaf 內，綁定需 OWNER 簽（實測 `REFUSED_REGISTRY_ROOT_MISMATCH`）。
- N-4 M1：真 consumer `CONSUMER_OK`，activator 正確拒絕（`REFUSED_NO_LOADED_SUBJECT`），不偽造 ACK。
- 待 OWNER：`wave0/owner_ceremony_loadonce.patch`（1 次口令簽 7 個簽章）→ 簽 rev 10 → 提權安裝。

---

# RESUME_HERE — B1 接續（2026-10-28）

給下一個 SESSION：不需要重新推導，照下面順序即可直行。

## 0. 一句話現況

B1 sandbox 閘門全 PASS（G-A 6/6、三張 GWO、G-B 3/3），`mission_complete=false`，五條殘餘阻擋已逐條量測。
最終獨立 VERIFY 車道（gpt-6.1-sol）回 **C1–C6 PASS、C7 FAIL**，C7 的內容是「GWO-FABRIC 是 `fabric_local` 本地重實作，不是真 Fabric activator」。

## 1. 立即要讀的檔案（依序，皆為現行版）

1. `var/B1-PIPD-PKG-20261027/artifacts/GATES.json` — 閘門oracle（含 `why_not_complete` 5 條、`sandbox_conjunction`、`mission_complete_blocker`）
2. `var/B1-PIPD-PKG-20261027/artifacts/STATE.json` — GATES 的投影（`gates`、`implementation.gates` 皆已派生）
3. `var/B1-CONT-20261028/CONTINUATION_REPORT.md` — 本回合修補 R-1..R-8、獨立驗收四次逐次發現
4. `var/B1-CONT-20261028/SESSION_STATE.json` — 機器可讀狀態
5. `var/B1-PIPD-PKG-20261027/artifacts/G_B_EVIDENCE.json`、`GWO_*_EVIDENCE.json`、`CHECKER_PRINCIPAL.json`

## 2. 環境事實（實測，不是推論）

- `python` = 3.11.17；HG-KSEOS 的 `.venv/Scripts/python.exe` 可用；doctor/conformance 需 ≥3.12（用 uv 3.12）。
- Codex CLI **0.164.0-alpha.11.1**，`C:\Users\user\AppData\Local\OpenAI\Codex\bin\2993767bd1dfb009\codex.exe`，sha `1103e9e09c71fa2cd0afd6d8f3b9a2d63174fe8efd7cb5bd09f1cb14ef58a098`。
- `config/active-policy.json` 已重新 designate：digest `69e9f10907cb7c707168ac1b47309b3a8deb7d653b4615cb4e9b8ada7cf1d51b`、16181 bytes、MATCH=True。
- `~/.codex/config.toml` 目前把 model provider 指到 **desktop_router**，所以車道 `served_arm=desktop_router/gpt-6.1-sol`，`--require-arm openai-codex/gpt-6.1-sol` 會得到 `ERR_REQUIRED_ARM_NOT_SERVED`（模型與付費方都對，只有 provider 標籤不符）。
- 目前 **NOT_ELEVATED**；`ProgramData\HG-KSEOS\native-admission\registry.json` 與 `LOCALAPPDATA\HG-KSEOS\native-admission\registry.json` 都不存在。

## 3. 下一步（依可行性排序）

**計畫依據**：`var/B1-CONT-20261028/FAR_B1_N1N6_20261028.md`（六項逐項裁決＋三波執行方案）。要點：`source_freeze`／`task_kind`／`oracle_ratification` 是 HGK native 准入的三把鑰匙（`native_admission.py:25-26`），所以 sourcefreeze 是 N-1 的前置，不是 release 的尾端。Wave 0 不需任何簽章即可執行。

1. **N-2（可立即做）**：24/30 route 只有 typed-refusal stub。逐 route 實作 effect；每條要有 raw + readback + 負例。`admission/registry/runner-registry.json#rows[].coverage` 是名單。
2. **N-4（可立即做）**：把 `fabric_local` 換成真 Fabric activator／consumer（`Fabric/FABRIC/control/PROMOTION_POLICY.yaml` 的 requires 六項），同一 sha 跑 STAGE→ACTIVE→LOADED，並確認負例（錯 sha／錯 epoch／無 receipt）。
3. **N-1（需 OWNER 決策）**：native-admission registry 由 OWNER 簽，machine scope 需提權；user scope 需 OWNER 明示接受 `SAME_OS_USER` 上限。
4. **N-3（需 OWNER 提供）**：第二個 Windows principal。
5. **N-6（需 OWNER 裁決）**：是否接受 `desktop_router/gpt-6.1-sol` 作為 VERIFY 車道歸屬。

## 4. 不要重做的事

- 不要重跑三張 GWO 或 G-B 的既成證據（已是 10-28 的真實執行）。
- 不要把 `GWO_FABRIC_STATUS.json` / `G_B_STATUS.json` 當現況（已標 `superseded_by`）。
- 不要用 `INDEPENDENT_AUDIT.json` 當 OWNER 指定車道收據（它是 mimo-v2.6-flash）。
- 不要為讓 checker 說 PASS 而改題目；題目固定 `var/B1-CONT-20261028/BRIEF_B1_VERIFY_GATES_20261028.md`。

## 5. 已知陷阱（本回合踩到的）

- 車道 `--sandbox read-only` 在此主機禁止所有 CreateProcess → 檢查器讀不到檔。要 `workspace-write --allow-sandbox-escalation --guard-subject <subject>`。
- `--cwd` 決定沙箱根；brief 放在 cwd 之外會讀不到（出現 `NONCE_UNAVAILABLE`，那是真話不是模型故障）。
- dispatcher 的 `ok=false code=ERR_NO_ARM_EMITTED_NONCE` 不等於模型沒回答：去 `var/B1-CONT-20261028/VERIFY_SECURITY/attempt-*/attempt-*stdout.txt` 抽最後一個 `agent_message`。
- 前台 terminal 約 420s 上限；一次車道 130–160s，夠用但別串多個。

## 2026-10-28 13:36 — GATE A 完成（rev10 已簽已裝）

- `registry_rev 10`、`sha256 fe20832642cb0f7b…`、`verify_registry = (True,'OWNER_SIGNATURE_VERIFIED')`
- 30 列簽章 + 1 root = **31 次簽章、1 次解鎖**；`owner_key_id OWNER-B1-d42c654cd1afba80`
- `runners 12 / not_registered 19 / EFFECT_IMPLEMENTED 12 / 30 列 sha 全對`
- reference 延後：`SCOPE_EMPTY`（沒有 workorder request digest 就不簽，避免偽造綁定）
- 收據 `wave1/apply_result.json`；失敗版收據 `MERKLE_VERIFY_FAILED / REFUSED_OWNER_KEY_ID_MISMATCH` 為 D-18 證據

### GATE B 現況：Partial（信任根可載入，但不足以跑真 workorder）

`ProtectedRegistry().snapshot()` → ACTIVE、三個互異 SID、7 個 approved files、負例仍拒絕。
但 `NativeAdmission.authorize()` 會逐項拒絕，實測缺：

| 缺什麼 | 會在哪一行拒絕 |
|---|---|
| `scope.database_path` | `CANONICAL_DATABASE` |
| `scope.head` 是 rev9 merkle root，不是 git HEAD | `WORKORDER_HEAD` / `HEAD_CHANGED_BEFORE_COMMIT` |
| `keys[]` 用 `public_hex`，kernel 要 `public_spki_b64` | `KEY_ALGORITHM` |
| `max_ttl_seconds` / `task_kinds` / `revoked_nonces` / `approval_source` | 形狀不符 `HGK-NATIVE-REGISTRY/1` |
| `scope.request_sha256` 空 | `REQUEST_SCOPE` |

`scripts/native-trust-maintenance.ps1 -Mode Enable` 不能直接用：它拒覆寫既有 registry
（`ERR_EXISTING_REGISTRY_USE_REVIEWED_REVISION_NOT_OVERWRITE`），且要求 machine CNG RSA 憑證；本機
`Cert:` 讀不到、`active-policy.json` 也沒有 `policy_epoch`（`policy_epoch` 是 Enable 的硬條件 ≥1）。

### 下一步（需要 OWNER 兩個宣告，不是我代填）

1. `policy_epoch` 值（≥1）與要綁的 git-rooted worktree（必須包含 approved runners；B1 工作區不是 git repo，
   `git -C var/B1-PIPD-PKG-20261027` → not a repository）。
2. 授權一次提權的「reviewed revision」改寫（0 解鎖），再跑一次口令 mint 3 個 reference + admit。

---

## 2026-10-28 05:56Z — GATE C：第一張真 native workorder 已 ADMITTED

- `event_id EVT-NATIVE-bbb8decbfbff`、`entity WO-B1-NATIVE-001`、`expected_version 0 → 1`
- `actor = owner SID …-1000`（不是 checker/maker）
- 3 個 nonce 已寫入、lease `WO-B1-NATIVE-001 generation 1`
- 信任根 rev **14**（root_identity 為量測的檔案系統身分 `32165637:…`）
- 收據 `wave2/NATIVE_ADMISSION_RECEIPT.json`、DB 副本模擬 `wave2/authorize_simulation.json`

### 這次花掉的代價與根因（下次不要再犯）

六次口令拒絕，全部是我的實作猜錯 kernel 介面：`task_kind` scope → 時區 `Z` → `task_kinds` 形狀 →
generation `0` 被 `or 1` 吃掉 → 自寫 canonical → `root_identity` 語意。**正確做法**：先用一次性金鑰 +
DB 副本把 `authorize()` 全路徑跑綠（`simulate_authorize.py`），再請 owner 輸口令。這一條已寫進流程。

### 仍未完成

- 覆蓋率 `12/30`（residual `RUNNER_COVERAGE_PARTIAL`）→ `mission_complete` 仍 false
- 244 案 corpus 走 `wave2_queue`，**不是** native admission；兩者是不同 ceiling
- reference TTL 本次 1 小時（`expires 2026-10-28T06:53Z`）

## 2026-10-28 06:19Z — 244 案 corpus 全部走 native admission

- `canonical_events` 內 `native_admission` 事件 **245**（1 張首發 + 244 案），`distinct targets 245`
- `native_admission_nonces 735`、`native_admission_leases 245`
- journal 245 列 / 244 個 distinct case；`TQ-B1-A1-SEC` 有一列 replay 拒絕（同一案 2 秒內第二次嘗試），
  DB 內每案仍只有一筆 ADMITTED → 重放守門有效
- 收據 `wave2/CORPUS_NATIVE_RECEIPT.json`（`admitted 240 / refused 1 / skipped 3`、587.8 s、case_fail 0）
- 覆蓋率未變（`12/30`，declared ceiling）

### 宣告簽章：仍未完成（1 次解鎖）

第一次摺進 corpus unlock 的簽章**無法驗證**：我先把 body 算好才補 `signed_by`/`signed_at`，所以簽的位元組
不等於寫入的位元組（實測 `bindings_match False`、`InvalidSignature`）。已建 `wave1/declaration_lib.py`
讓 seal/verify 共用同一份定義（離線測：seal→VERIFIED、改文字→BINDINGS_MISMATCH），宣告已重置為 UNSIGNED，
閘門顯示 `DECLARATION_DRIFT(text_stale)` + `CLAIM_DECLARATION_UNSIGNED`。

下一步只需：`wave1/sign_declaration.py --apply`（一次口令），然後才可把 `claim_ceiling` 文字改成已簽內容。

## 2026-10-28 14:32 — 宣告已簽並驗證通過（FAR v6 完成）

```
declaration_signature (True,'VERIFIED')   signed_by OWNER-B1-412b351937be72a1
registry_sha_pinned_matches True           text_matches_registry True
```

- `claim_ceiling` 已由「CANARY_DEMO_KEYS_NOT_OWNER; 6 of 30」改為實測值，改動前後與「為何允許」
  記在 `wave1/claim_ceiling_edit.json`，且由已簽宣告綁定（改字即 `BINDINGS_MISMATCH`）
- 閘門：`gates_conjunction PASS`、`mission_complete false`，只剩兩條真 blocker：
  `SAME_OS_PRINCIPAL`、`SOURCEFREEZE_HOLD / RELEASE_NOT_RUN`
- `CLAIM_DECLARATION_UNSIGNED` 與 `DECLARATION_DRIFT` 均已消失

### 剩下兩條各自需要什麼（未做，不宣稱）

| blocker | 需要 | 成本 |
|---|---|---|
| `SAME_OS_PRINCIPAL` | checker/maker 各自的 key material（B1-CHECKER `…-1006`、B1-MAKER `…-1007` 已存在但未持金鑰） | 每個 principal 一次登入/金鑰封裝 + registry 重簽 |
| `SOURCEFREEZE_HOLD / RELEASE_NOT_RUN` | owner 對凍結位元組簽 `source_freeze` reference 並執行 release | 1 解鎖 + 1 次 release 動作 |

## 2026-10-28 14:4x — FAR v7：兩條殘餘是寫死的字串，已改成量測

- 量測：`gates.py:232-234` 兩條 `rs.append(...)` 是**硬編碼**，與同函式 docstring「never a static list」矛盾；
  `DOC-13 L2775` 實際是 F22/F23/F24 審計列，**沒有**「第二 principal／key material」條文 → 引用錯誤
- 量測：native registry `owner …-1000 / checker …-1006 / maker …-1007` distinct=True、`keys` 只有 owner 一把
  → kernel 的 `PRINCIPAL_SEPARATION`（3 個互異 SID）**已滿足**；per-principal key material 無已讀條文要求
- 量測：`input_20261027/FHS_MSC_B1_PIPD_LS_PKG_00…08` front matter **9/9 皆是 `formal_sourcefreeze: HOLD`**，
  且 `DOC-00 L327-330` 標上游九冊 `READABLE_USER_INPUT;NOT_FORMAL_SOURCEFREEZE`
  → 缺的不是一張簽章，是上游從未正式凍結；簽 reference 只會製造假象
- 裁決 D1..D5 見 `FAR_B1_v7_20261028.md`；本輪 **0 簽章／0 解鎖／0 提權**
- gates 現況：`conjunction PASS`、`why_not_complete []`、`mission_complete false`，
  `mission_complete_blocker = declarations awaiting owner ruling: PRINCIPAL_SEPARATION_MEASURED, SOURCEFREEZE_DECLARED_HOLD`
  （`gates.py` 新增 `open_rulings` 條件：有待裁決宣告時 mission_complete 不得為真）

## 2026-10-28 14:43 — owner ruling 已簽；`mission_complete = true`（條件式）

```
OWNER_RULING_v1.json  verify (True,'VERIFIED')  signed_by OWNER-B1-412b351937be72a1  bindings a587491e…
  PRINCIPAL_SEPARATION_MEASURED -> ACCEPTED_AS_SUFFICIENT
  SOURCEFREEZE_DECLARED_HOLD    -> ACCEPTED_AS_DECLARED_HOLD

gates: conjunction PASS | why_not_complete [] | mission_complete True
drift test: 改 bound_value → False (OWNER_RULING_BINDINGS_MISMATCH)；還原 → True
```

`mission_complete` 的定義（本輪新增）：`gates conjunction PASS` 且 `why_not_complete` 為空
且 **沒有任何待裁決的 blocking declaration**。它**不**代表 promotion、release、第三方驗收。

仍未做／仍不宣稱：`release: NOT_RUN`、`RUNNER_COVERAGE 12/30`、獨立 check 同機同 OS 使用者、
上游 `formal_sourcefreeze: HOLD` 未變。

## 2026-10-28 — FAR v9：`12/30` 是本地指標，不是 PKG 要求

- 分母 30 = `runner-registry.json` 列數；PKG_06 949 個 R15 id 與其交集 0
- 唯一有文字者：OpenSpec `tasks.md` L19（每條至少 `INSTALLED`）→ 實測 **30/30 已滿足**
- 18 個 typed-refusal 名稱**全部**見於 PKG 文件，但「全部都要有 effect」**0 條文字**
- `gates.py`：`RUNNER_COVERAGE_DECLARED` → `ROUTE_INSTALL_REQUIREMENT`（satisfied）
  ＋ `EFFECT_IMPLEMENTED_INVENTORY`（`claim_weight: none`）＋ `READY_RUNNING_ZERO`（PKG_08 L49，只讀狀態欄位）
- 依 PKG_08 L45/L47/L49/L102-106 量測：本 SESSION 的 PKG_00～08 驗收**已完成**
- 撤回 v8 的 D1／D3：不為 30/30 造 8 條沒有輸入的 runner；TTL 不動（政策上限，無人值守用排程解鎖＋續跑）
- 待辦：D-8（子字串謊報）與下次 registry 變更批次重簽（1 解鎖／31 簽章）；sourcefreeze (a) 待 owner 凍結

## 2026-10-28 — D-8 修復完成（FAR v9 D4）

```
generic_route_runner.resolve(): 子字串比對 -> 精確查表（讀簽章 registry）
修前 2 條派錯（native_issuer->issuer_subject, native_receiver->bridge_handoff）/ 25 條回 None / 3 正確
修後 12 條 exact / 18 條具名 typed refusal / 0 派錯
registry sha d7019575… rev10 verify (True,'OWNER_SIGNATURE_VERIFIED')  rows sha != disk: 0
declaration 同一次解鎖重綁並重簽，pin 新 sha，VERIFIED；native trust root 7 pins 未受影響
```

**事故（已記錄）**：第一次 STEP 8 簽的是 candidate 快取的舊 sha（18 列），根因是 live path 直接簽
`pf["candidate"]["rows"]` 且 G1 不檢查 row sha vs 磁碟；已修為簽章前 `rebuild()` 從磁碟重算、G1 對
`sha_not_on_disk` fail-closed。共花 2 次解鎖、0 提權。
