# HERMES_023_FHS_W0_W1_INTEGRATION_RESULT

- **Contract**：`FHS-HERMES-023-NATIVE-INTEGRATION@2026-11-10-r2`（執行 `…DEEP_WIRING_THIN_CONTROL_r2_2026-11-10.md`）
- **執行者**：本地 **Hermes v0.23.0 GUI／`hgk-governed`**（PID 22880／`786a3156d1db`／`D:\Hermes-Recovery\port-serve-home`），非 Codex
- **執行時間**：2026-11-10 11:00–12:05（Asia/Taipei）
- **唯一 Overall Verdict**：**`PARTIAL_INTEGRATION`**
- **一句話**：W0 六個原 WP 的本波驗收原子 **13/17 有真證據**（其中 11 項是本回合在 h23 重跑、4 項附可執行負控），但 **`WP-FHS-01` 的 19 契約族有 15 族 oracle enum 仍 HOLD**、**W0→W1 的 E01 消費未被證明**、**E36 完全沒有消費證據**，因此 NI-05／NI-09 未通過，只能到 `PARTIAL_INTEGRATION`；本輪**沒有**任何 Native／Independent／Release 主張，也**沒有**改動 FHS-3L&M、W0 已簽位元或正式 h22。

---

## 1｜Host 身份與隔離（NI-01）

身份**不取自 PATH**，而取自各 Gateway 自己寫的 `gateway_state.json`；同一台機器上兩個 Gateway 同時在跑，這是本輪必須先分清的事實。

| 項 | h23（本輪執行者） | h22（正式，未觸碰） |
|---|---|---|
| PID | **22880** | **15576** |
| code_version／code_sha | `0.23.0`／`786a3156d1db06bd9fc014c014cea4c8023653fd` | `0.22.5`／`36396528a2a9ff52244a32fcf2f606dee5972b36` |
| Home | `D:\Hermes-Recovery\port-serve-home` | `D:\Hermes-Recovery\live22` |
| Profile | `hgk-governed`（served: default + hgk-governed） | served: default + hgk-governed |
| 本輪動作 | 讀取、量測、寫本回合目錄 | **零寫入、零重啟、零遷移** |
| 讀回時間 | `updated_at 2026-11-10T02:55Z` | `updated_at 2026-11-10T03:24Z` |

`code_sha` 與 `git -C D:\Hermes-Recovery\hermes-0230-stage rev-parse HEAD` 逐字相同（`m1_freeze.py` 的 `identity_sha_matches_tree: true`）。Raw：`evidence/MEASURE1_FREEZE.json#/facts/gateway`、`D:/Hermes-Recovery/live22/gateway_state.json`。

## 2｜層級 A：已簽來源可在 h23 被消費（**成立**）

| 檢查 | 實測 | Raw |
|---|---|---|
| W0 r26 身份 | **668,540 B／`0ea0554…`**，三個位置（Session 附件 ×2、Round fabric stage）**同一 digest，1 個 distinct** | `MEASURE1_FREEZE.json#/checks/w0_r26_identity` |
| 六份 Reader 收據 | 以**原** `tools/verify_reader_ack.py` 實跑：`6/6 receipts verified`、**exit 0** | `evidence/reader_and_quorum.txt` |
| Quorum | 原 `verify_quorum.py`：12 envelopes／**128 preservation properties**／`findings: []` | 同上 |
| Owner Semantic ACK | canonical payload `08d5db98…` **重導一致**；Ed25519 對 `OWNER-B1-d42c654cd1afba80` **驗簽 True**；所引 6 份收據 payload **6/6 相符** | `evidence/OWNER_ACK_REDERIVED.json` |
| GSTACK（原 `gate_r20.py` 對已簽 round） | **21/22 PASS、0 blocking、1 open reporting（G16b）**，含 G11 由 31 檔重算 111,331 行／22,281,767 B、G19 重雜湊 437 份副本 | `evidence/GATE_R26_ON_H23.json` |

**A 的界線**：這證明「被簽的位元可被原 Reader 與原 Gate 消費」，**不證明** W0 功能完成，也不證明原域 Owner 對本輪新增內容的接受。六份收據的 `OriginalConsumer` 全部是**同一個**「SBL Original Source/Requirement/Corpus Semantic Reader」，且綁的是候選 `r15`——**7 個 WP 產物的 digest 在收據與 lanes 中出現 0 次**；收據是「32 個 locator 的受界證據」，不是六個 WP 的功能驗收（見 §5）。

## 3｜W0 六 WP 全契約覆蓋（COV-01～05）

矩陣本體：`out/W0_023_COVERAGE_MATRIX.json`（17 atoms／9 edges／22WP×36Edge 身份表／每 WP 十一欄位塊）。

### 3.1 逐 WP 摘要

| WP | 原子 | 已覆蓋 | HOLD／PARTIAL／DEFERRED | 判 |
|---|---:|---:|---|---|
| `WP-FHS-00` | 4 | 2 | A3 `PARTIAL`（E01 消費未證）、A4 `HOLD`（HG-KSEOS 5 個 dirty path） | **部分** |
| `WP-FHS-01` | 3 | 2 | A2 `HOLD`（19 族中 **15 族 `ORACLE_ENUM_ABSENT`**，見 D-01） | **部分** |
| `WP-FHS-15` | 3 | 3 | —（含**真實 consumer NACK**） | **成立** |
| `WP-FHS-16` | 3 | 2 | A3 `WAVE_DEFERRED`（E35 屬 W1） | **成立** |
| `WP-FHS-19` | 2 | 2 | —（SBOM／依賴已逐庫重讀） | **成立** |
| `WP-FHS-21` | 2 | 2 | —（Runner 未綁，狀態即 `PLAN_NOT_RUN`） | **成立** |

### 3.2 本回合實際量到什麼（不是引用舊報告）

| 原子 | 實測值 | 負控（本回合真的執行） |
|---|---|---|
| WP00 A1 | 31/31 檔 re-hash＝宣告 digest；22,281,767 B；111,331 行 | `NEG-WP00-byteflip`：鏡像翻 1 byte → `SHA_MISMATCH`，偵測成功 |
| WP00 A2 | 三棵 worktree 的 local HEAD／branch／dirty 與 live remote main **分欄記錄**；2/3 的 local≠remote（feature branch），HG-KSEOS dirty=5 | `BASE-inventory` |
| WP01 A1 | in-set 31、`duplicate_sha_groups=0`、17 組正規化同名外部副本 | `BASE-sources` |
| WP01 A2 | 19/19 家族繫到真實 schema 檔；但 **15 族 `ORACLE_ENUM_ABSENT` 為 HOLD** | `BASE-slots` |
| WP01 A3 | 行段 111,331／結構塊 25,201；31/31 檔 tile 完整 | `NEG-WP00-byteflip` |
| WP15 A1 | SPEC bytes 9,116／9,267／9,691；**兩種獨立方法**都判相異（工具 0.2134、獨立 difflib 0.5522，門檻 0.85） | `NEG-WP15-tools`：NC-1/2/3 三種注入全部被抓 |
| WP15 A2 | **52/52 span 回切逐位元相同**；18 stage；15 ACC（6 POS＋9 NEG）；FUO 10 欄 | 同上 |
| WP15 A3 | 原 `pipd intake` 實跑 → **`INTAKE_INVALID`、exit 2**，指到 `01_PRODUCT_AUTHORITY_SPINE(4).md` **char 8183（FUO-01 的「對應」）**；同一 binary 對 `00_INDEX` **exit 0 並回 atoms** | `NEG-WP15-intake-NACK` ＋ `POS-WP15-intake-control` |
| WP16 A1/A2 | 24＋25＝49，零填充零重複；**52 條 source_ref 全部回切**；13/13 檢查 | `NEG-WP16-duplicate-id`：複製 slot id → unique 48，被抓 |
| WP19 A1 | 三庫 live：SBL＝MIT＋NOTICE＋**CycloneDX 1.5 SBOM**＋`supply-chain` job success；Fabric＝根層無授權、僅 vendored 授權、**只有 sbom 產生器無 SBOM**；HG-KSEOS＝**零授權檔**、SBOM 是 `SBOM/1` 盤點且自述 `SUPPLY_CHAIN_UNVERIFIED`、**無 CI** | `NEG-WP19-drop-repo`：抽掉 Fabric → 偵測缺庫 |
| WP21 A1/A2 | 15／96／12／11＝**134 列**、155/155、**12×8 完全交叉乘積**、`__CORRUPT__001..096` 連續 | `NEG-WP21-drop-one-case`（96→95、cross 96→95）＋ `NEG-WP21-discriminate`（POS pass／NEG fail／laundering 被 scope 拒） |

負控總表：`evidence/NEGATIVES.json`（4 baseline ＋ 8 negative／consumer，`all_negatives_detected: true`，exit 0）。

### 3.3 22 WP／36 Edge 身份（COV-01）

由 r26 本文直接解析：**22 個 WP**（`WP-FHS-00…21`，含主波）與 **36 條 Edge**（`E01…E36`，含 `Wx→Wy`）全數具名，與宣告一致；逐列見 `out/W0_023_COVERAGE_MATRIX.json#/cov01_identity`，每 WP 的 `Trigger/Input/Operation/Output/POS/NEG/Reader-Consumer/Host/EvidenceRef/Invalidation` 十一欄見 `#/cov01_per_wp_fields`。

## 4｜COV-04 接線：消費，不是清點

| Edge | 生產者→消費者 | 判 | 依據 |
|---|---|---|---|
| `E01` 00→01 | PARTIAL | WP01 **自己重雜湊同一 31 檔**（`sha_match=31`），但 `SOURCE_LOCK.json` 的 digest `49c65214…` **未出現在 ledger**；「同來源集」與「消費了 manifest」在此不可分辨 |
| `E27` 00→15 | **CONSUMED** | 52 條引文 span 回切到原始 bytes（跨 4 份來源） |
| `E28` 00→16 | **CONSUMED** | 49 slot 的 **52 條** `source_ref` 全部回切（C04） |
| `E33` 00→19 | PARTIAL | 掃描輸入集恰為三庫名，但 `digest_cited=false`；**名稱集合不是消費**，已由 `out/W0_W1_HANDOFF_ENVELOPE.json` 以作者端 join 補，`consumer_readback: NOT_OBSERVED` |
| `E36` 01→21 | **NOT_EVIDENCED（HOLD）** | 134 列由 BODY-07 的 TestClass×OracleType 編成；binding 的 4 個有 enum 的家族與 8 個 oracle type **交集為 0**，沒有任何 binding 的值跨越 |
| `E12/E35/E26/E16` | HANDOFF_READY_EFFECT_HELD | 分別為 W1 PLAN／W1 Host matrix／W4 Release／W2 Protected run；本輪**不執行**，也未簽任何收據 |

## 5｜兩個不同的問題必須分開講（本輪最重要的更正）

| 問題 | 答案 | 依據 |
|---|---|---|
| (a) 下游有沒有**消費**上游產物？ | `E27`／`E28` 有；`E01`／`E33` 部分；`E36` 沒有 | §4 |
| (b) 契約指定的**原 Reader** 有沒有出具 readback？ | **0/6** | 六份收據可驗簽、可驗 payload，但 `OriginalConsumer` 全為同一個 shared reader，綁 `r15`，**沒有任何 WP 產物 digest**（`evidence/R4_FRESH_SESSION_GOAL.md`） |
| (c) 有沒有**具名 typed consumer 回應**？ | 有 1 個：`WP-FHS-15` 的 `INTAKE_INVALID`（NACK，非接受） | `evidence/INTAKE_NACK_RAW.txt` |

把 (a) 當成 (b) 就是本輪最容易犯的錯；`FHS_ORIGINAL_ACK 6/6` 只在「32 個引用 locator 的受界證據」這個意義上成立。

## 6｜NI-01～09 判決

| ID | 判 | 依據／缺口 |
|---|---|---|
| `NI-01` HOST | **PASS** | h23 與 h22 以各自 `gateway_state.json` 分離；`code_sha` = 原始碼樹 HEAD |
| `NI-02` FHS-3L&M 原物 | **PASS** | `--menu` **9/9 admitted**；4 份既有 binding `--assert` 全 `ok`（registry `811bf1a5` 未變）；`--assert-arm mimo-v2.6-pro` → **exit 9 RETIRED_ARM**；**未改一行** |
| `NI-03` Lane Live | **LIVE_UNVERIFIED** | 三車道 rank-1 的 `ActualServed` 收據存在於前輪（epoch 41 未變、pin 已修、relay 200），本輪**未重派**；且 Codex app/runtime 版本錯位（`26.1103.4239.0` vs `26.1105.1297.0`）使子程序工具面仍不可用 |
| `NI-04` 日常入口 | **PASS（受限）** | 新 child session 以普通 Goal 直接讀本地證據並產出 artifact，未貼長 Prompt、未自造 Issuer |
| `NI-05` W0 六 WP | **FAIL（不可宣稱）** | 13/17 原子覆蓋；`WP-FHS-01` A2 與 `WP-FHS-00` A4 仍 HOLD、A3 PARTIAL |
| `NI-06` 原生／持久 | **PASS（任務級）** | 新 session 真模型＋真工具＋artifact；**未測 Kanban Resume**（本輪未聲稱長任務） |
| `NI-07` 影響／機密 | **PASS** | 零 world write；未簽 Permit；Token 未進 argv／stdout／Repo（見 §9） |
| `NI-08` GitHub 原域 | 見 §9 | Fabric-first；候選分支＋PR；`main` 未直寫 |
| `NI-09` W0→W1 完整性 | **FAIL（不可宣稱）** | 22/36 身份完整、`E27/E28` 真消費、`E36` 無消費、`E01/E33` 部分 |

**NI-05／NI-09 不通過 ⇒ tier B 不成立 ⇒ 唯一可用 Overall 為 `PARTIAL_INTEGRATION`。**

## 7｜新發現的缺陷（不是進度落後，是文件與製程的洞）

| ID | 內容 | 影響 | 誰能修 |
|---|---|---|---|
| `D-01` | `PROFILE_ORACLE_BINDING.json` 摘要寫 `families_hold: 0`，同一檔的 holds 陣列寫 `ORACLE_ENUM_ABSENT ×15 / resolution HOLD` | 引用摘要的讀者會少報 15 個缺口 | 原 PIPD contract Owner |
| `D-02` | E01 的「消費」只能由 WP01 自報的 `sha_match=31` 支撐，manifest digest 未跨界 | 同來源集被誤讀成消費 | WP-01 產物加一行 manifest digest |
| `D-03` | E36 的 binding 與 oracle plan 在值域上無交集（4 enum 家族 vs 8 oracle type） | 兩份 artifact 都在，join 不存在 | 重產 WP-21 表並記錄 binding digest |
| `D-04` | 三庫供應鏈狀態差異大：SBL 有 SBOM／授權／supply-chain job；Fabric 只有產生器、根層無授權；HG-KSEOS 零授權檔、SBOM 僅盤點、**無 CI** | 「三庫 CI 綠」不是可成立的句子 | 各庫 Owner |
| `D-05` | Codex `OpenAI.Codex`（26.1103.4239.0）比 `OpenAI.CodexPrimaryRuntime`（26.1105.1297.0）舊 → 子程序 `registered Core launch requires an installed app` | 車道只能服務模型，讀不到 brief | Owner 對齊 app 版本 |
| `D-06` | HGK 本地 in-force epoch **41**，GitHub `main` 仍 epoch **33**（`acd9196f`） | 兩個平面不可互推 | HGK Owner |
| `D-07` | 前輪 `SOURCE_LOCK`（V1 慣例）對 31 檔判 `lines_match:false` 卻 `verdict:MATCH` | 已由 V3 的雙慣例修好，此處只登記歷史 | 已完成 |

## 8｜三車道帳（不含未觀測的升格）

| 車道 | Required | Selected | Invoked | ActualServed | 本輪判 |
|---|---|---|---|---|---|
| PLAN | `openai-codex/gpt-6.1-sol` | 同名（binding `ok`） | 前輪 receipt（本輪未重派） | `gpt-6.1-sol`（前輪 receipt） | `LIVE_UNVERIFIED` |
| EXECUTE | `opencode-go/deepseek-v4.1-flash` | 同名 | 前輪 receipt | `opencode-go/deepseek-v4.1-flash` | `LIVE_UNVERIFIED` |
| VERIFY_SECURITY | `openai-codex/gpt-6.1-sol` | 同名 | 前輪 receipt | `gpt-6.1-sol` | `LIVE_UNVERIFIED` |

`Selected` 從不算 PASS；本輪**沒有**任何新的派工收據，因此三車道維持 `LIVE_UNVERIFIED`。退役臂 `mimo-v2.6-pro` 被契約本身拒絕（exit 9），未被洗成合格服務。

**對控制包的更正**：r2 §1 仍寫 PLAN／VERIFY 因「缺 `openai-codex` provider」而 `EXECUTOR_UNBOUND`；前輪 §11.6 已撤回該理由（真正原因是 spawn 前的 pin 失效，pin 已修）。本輪未重派，故不採用任一解釋作為結論，只記 `LIVE_UNVERIFIED`。

## 9｜GitHub 發表（Fabric-first；候選，不直寫 main）

> 本節於推送後回填；推送前的狀態為 `PUBLISH_PENDING`。

- 認證：`C:\Projects\Agent_Workspace\API KEY\GITHUB-REPO_SHW097-4.txt` **只**由 Git 的 `GIT_ASKPASS` 私有消費（`git -c credential.helper= credential fill` 證明可取用），**Token 未出現在 argv、stdout、日誌、URL 或 Repo**；`git push --dry-run` 已驗證寫入權。
- 順序：Fabric（讀 `AGENTS.md`／`INTEGRATION/FHS/README.md`／`get FHS/AGENTS.md`／repository-map 語義）→ SBL（`integrations/pipd` 為 canonical）→ HG-KSEOS（僅去敏量測／具名缺口）。
- 邊界：不改 `INTEGRATION/MANIFEST.json`、不改 `repository-map.json`、不改 HGK 三車道與 registry；只新增本輪證據目錄。

| Repo | 分支 | Commit | PR | 遠端讀回 |
|---|---|---|---|---|
| Fabric | `docs/fhs-hermes-023-integration-20261110` | `見 PR 頁面`（本檔多次 commit 會移動 head；逐次推送 sha 記於 `out/PUBLICATION_LOG.json`） | **#50** https://github.com/shw097-team/Fabric/pull/50 | `open`／base `main`／head sha 相符／`mergeable_state=unstable` |
| SBL | `evidence/fhs-hermes-023-integration-20261110` | `見 PR 頁面`（本檔多次 commit 會移動 head；逐次推送 sha 記於 `out/PUBLICATION_LOG.json`） | **#65** https://github.com/shw097-team/SBL/pull/65 | `open`／base `main`／head sha 相符／`mergeable_state=unstable` |
| HG-KSEOS | — | — | — | **`PUBLISH_HOLD`**（具名理由見下） |

### 9.1 發表結果與界線

- **兩個 PR 皆已建立且遠端可讀回**（HTTP 201 → 再讀 `state=open`，head sha 與本地推送一致）。`unstable` 只表示檢查未定，**不是** merge、**不是** CI PASS、**不是** 任何原域 ACK。
- **Fabric 的提交以 plumbing 完成**（`hash-object` → `update-index` → `write-tree` → `commit-tree` → `push`），因為該機磁碟只剩 16 MB，`git worktree add` 無法 materialise 4,253 個檔案（`No space left on device`）。物件與 tree 完全相同，差別只在沒有 checkout 到工作區。
- **HG-KSEOS 不發 PR，記 `PUBLISH_HOLD`**：本輪對該庫沒有真正的領域差額——唯二的 HGK 事實（本地 in-force epoch **41** 對 GitHub `main` epoch **33**；Codex app/runtime 版本錯位造成的工具面缺陷）都屬 HGK 自己的控制平面，需要 Owner 決策，且 HGK `main` 沒有 CI 可驗證變更。發一個純說明 PR 只會製造「看起來處理了」的假象。Resume：Owner 決定是否要一份 HGK evidence note。
- 三個庫的 `INTEGRATION/MANIFEST.json`、`repository-map.json`、lane registry、pool、assignment **均未改動**；本輪只新增各自目錄下的檔案。
- Falcon 檢查：Token 只經由 `git credential fill`（`GIT_ASKPASS`）取得，並以 curl 的 **stdin config** 傳遞；未出現在 argv、stdout、日誌、URL 或任何 Repo 檔案中。

## 10｜明顯**不**主張的事

1. 不主張 W0 功能在 0.23.0 完成覆蓋：**13/17 原子**，`NI-05`／`NI-09` 未通過。
2. 不主張任何 WP 取得契約指定的**原 Reader readback**（0/6）；六份收據是 32 locator 的受界證據。
3. 不主張三車道本輪 Live：`LIVE_UNVERIFIED`，且子程序工具面 `TOOL_PLANE_UNBOUND`。
4. 不主張 `NATIVE_SIGNED`／`INDEPENDENT`／`RELEASE_GRANTED`／已合併／已審／已發行。
5. 不主張 W0 r26 的任何位元被本輪改善或重簽；`FHS_ORIGINAL_ACK 6/6` 未升格。
6. 不主張 h22 被本輪以任何方式影響（零寫入、零重啟）。
7. 不主張 `E36` 已被消費；`E01`／`E33` 只是 `PARTIAL`。

## 11｜最小續工（依成本排序）

| # | 動作 | 解鎖 |
|---|---|---|
| 1 | `worktrees/r4-hgk` 的 5 個 dirty path 收斂 | `WP-FHS-00` A4 |
| 2 | 原 PIPD contract Owner 對 15 族 enum 作出閉合或「本波不適用」裁決 | `WP-FHS-01` A2 |
| 3 | WP-01 ledger 記一行 `SOURCE_LOCK.json` digest | `E01` → CONSUMED |
| 4 | 重產 WP-21 表並記錄 `profile_oracle_binding.sha256` | `E36` |
| 5 | Owner 對齊 Codex app 與 runtime 版本 | 車道工具面 |
| 6 | HGK `main` 與本地 epoch 41 的收斂決策 | `NI-03` 可重驗 |

## 12｜Raw 索引（最少集）

| 檔案 | 用途 |
|---|---|
| `evidence/MEASURE1_FREEZE.json` | 身份、r26 三副本、31 來源、6 上層文件、三庫 RepoContext |
| `evidence/reader_and_quorum.txt` | 原 Reader 6/6、quorum 128 |
| `evidence/OWNER_ACK_REDERIVED.json` | Owner ACK payload／Ed25519／6 receipts |
| `evidence/GATE_R26_ON_H23.json` | GSTACK 21/22、0 blocking |
| `evidence/NEGATIVES.json` ＋ `NEG_*.log` | 4 baseline ＋ 8 負控 |
| `evidence/INTAKE_NACK_RAW.txt`／`INTAKE_CONTROL_RAW.txt` | pipd intake 的 NACK 與對照組 |
| `evidence/WP19_LIVE.json`／`WP19_INVENTORY_V2.json` | 三庫 CI／授權／SBOM／依賴 |
| `evidence/WIRING_CONSUMPTION.json` | E01/E27/E28/E33/E36 與後波 4 邊 |
| `evidence/R4_FRESH_SESSION_GOAL.md` | 新 session 的普通 Goal 產物 |
| `evidence/INDEP_REDERIVATION.{json,md}` | 獨立重算（不看本回合 JSON） |
| `evidence/ADVERSARIAL_CHALLENGE.md` | 對抗式挑戰 10 條（本輪修補依據） |
| `out/W0_023_COVERAGE_MATRIX.json` | 覆蓋矩陣本體 |
| `out/W0_W1_HANDOFF_ENVELOPE.json` | W0→W1 作者端 join（非收據） |
| `tools/m1…m7` | 全部可重跑 |

## 13｜重現

```bash
cd C:/Projects/Agent_Workspace/FHS_HERMES_023_NATIVE_INTEGRATION_20261110
PY=D:/Hermes-Recovery/hermes-0230-stage/.venv/Scripts/python.exe
$PY tools/m1_freeze.py          # 身份／r26／31 來源／6 上層／三庫
$PY tools/m2_wp19_live.py       # 三庫 CI/授權 live
$PY tools/m7_wp19_inventory.py  # SBOM／依賴／授權層
$PY tools/m3_wiring.py          # 消費邊 ＋ handoff envelope
$PY tools/m6_negatives.py       # 4 baseline ＋ 8 負控（exit 0）
$PY tools/m4_owner_ack.py       # Owner ACK 重導
$PY tools/m5_matrix.py          # 覆蓋矩陣
# 原 Gate 與原 Reader（在已簽 round 上）
cd ../FHS_W0_R13_ACCEPTANCE_20261108 && $PY tools/verify_reader_ack.py && $PY tools/gate_r20.py --round . --skip-hygiene
```
