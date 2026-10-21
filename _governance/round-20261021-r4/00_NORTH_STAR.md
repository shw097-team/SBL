# R4 核心大目標（North Star）

> Order: `SBL-R4-20261020-C3-FIVE-TOOLS-SWOF-W12`（`SBL｜HERMES HG-KSEOS Fabric 指揮薄 PROMPT｜R4`）
> External report: `SBL_EXTERNAL_ACCEPTANCE_AND_SWOF_CONTINUATION_R4_2026-10-20`，sha256 `b2fabefd…`
> Round executed 2026-10-21（Asia/Taipei）。Round dir: `_governance/round-20261021-r4/`

## 1. 一句話

在 HG-KSEOS 為唯一控制平面、Hermes 為受治理 runtime 的前提下，**修掉 R4 唯一 CONFIRMED_DEFECT**（c3 plugin manifest 缺 portable `$schema`），把五個工具各自做成**可獨立安裝／載入／使用／卸載**的工件並在 Docker 沙盒取得真收據，同時以 SBL `main` 精確 SHA 起 `SBL_TO_SWOF_W2_SHADOW_HANDOFF.v1` 交棒 SWOF W1/W2，**W3 一律 NO_EFFECT**。

## 2. 本輪四個必達（依 R4 §4）

| # | 目標 | 完成條件（fail-close） |
|---|---|---|
| A | Foundation 封存守護 | 只做讀回（`main=bedc119…`、`v0.1.0-foundation-preview`）；不重開 M4-LITE、不重發 release、不以 441/149/38 反向撤回 preview |
| B0 | `F-R4-C3-PLUGIN-SCHEMA-001` 最小修補 | root `plugin.json` 帶 `$schema=https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`、**嚴格 schema 驗證通過**（不是 JSON 語法通過）、`skills/<name>/SKILL.md` 正規 frontmatter、三包 byte 可重現、身份不可互換、CI 2/2（新 head） |
| B1–B4 | 五工具資格化 | `TOOLS5_HARNESS_MATRIX` 五行，每行有 package/install/load/invoke/deny/rollback/uninstall 的**實際命令與 exit**；沒有 Host 的欄位寫 `HOST_PENDING` + 具名 request，**不得寫 PASS** |
| C | SWOF W1/W2 接續 | `SBL_TO_SWOF_W2_SHADOW_HANDOFF.v1` 以實測 SHA 產出；`allowed`/`forbidden` 明列；SBL 不寫 SWOF repo |

## 3. 模型方案：mandate vs observed（DISCLOSED DEVIATION）

| 角色 | mandate（order 原文） | observed（本輪實測） | 處理 |
|---|---|---|---|
| PLAN（在 HERMES 內） | `GPT 6.1 SOL-MEDIUM`（OpenAI OAuth） | 本會話 pin = `deepseek-v4.1-flash` / `opencode-go`；`openai-codex/gpt-6.1-sol` 已在 config 註冊（`auxiliary.kanban_decomposer`、`triage_specifier` 使用）但**會話未切換** | **owner 2026-10-21 明示授權 DISCLOSED_DEVIATION**；本輪 PLAN 由 deepseek 擔任，收據雙欄記錄。切換會話模型是 owner 動作，maker 不自行改 config |
| EXECUTE | `DeepSeek V4.1 Flash`（OpenCode Go） | `opencode-go/deepseek-v4.1-flash`（lane smoke `SBLEXEC-SMOKE-01` `ok:true`） | 符合 |
| VERIFY / SECURITY | `GPT 6.1 SOL-MEDIUM`（OpenAI OAuth） | `openai-codex` ws `426`（relay 只服務 HTTP）；R4 §3 已判 `G-R4-HARNESS` 為 EVIDENCE_GAP | 不重派已證死車道；以 Docker 沙盒 + maker 側探針取代，**不宣稱 `INDEPENDENT_CASE_PASS`** |

**registry drift**：`config/lane-route-slots.candidate.json` rev10 仍寫 PLAN=`glm-5.3-flash` rank1、VERIFY=`deepseek-v4.1-flash` rank1，與 R4 mandate 不同。依前輪慣例以 **role mandate chain 逐輪覆蓋**，**不自改 registry**（registry 變更是 control-plane owner 的動作）。

## 4. 進入本輪的既有事實（readback，非推論）

| 對象 | 值 | 來源 |
|---|---|---|
| SBL `main` | `bedc11957d4fc2474b249b69d200829272c118ef` | `git ls-remote` |
| SBL Foundation release | `v0.1.0-foundation-preview`（prerelease），tag target `bedc119…` | `git ls-remote --tags` |
| c3 candidate | `39c604d52570922fdf84b6df9c9359765643b450`（`candidate/c3-20261020-v1`，**未 merge**） | `git ls-remote --heads` |
| R3 evidence | `cfedf094996a801493d5b9574cd14742668549c9` | `git ls-remote --heads` |
| SWOF `main` | `acdbfaadd19d12927eb5bd542b09ed230bbc481e` | `git ls-remote` |
| SWOF W2 source | `c333e47141393b4f6c39a13f70c96b31190f3c3d`（PR #7） | `git ls-remote` |
| SWOF R9E evidence | `963cadeae3e50873c6a3c7ef000ffbfcaa73f78c` | `git ls-remote` |
| PIPD-LS-SP `main` | `e95942abcb6aa07e69304607ab8afc22a74fc67d` | `git ls-remote` |
| portable plugin schema | `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json` HTTP 200, `application/json`, 1805 B | live fetch，vendored |
| HGK 版本 | `hg_kseos 0.1.0`（`HG-KSEOS/src`） | import probe |
| 車道埠 | `10101`/`10102` healthz 200；`10100`/`10103`/`10105` 000 | curl |

R4 `as_checked_2026_10_20` 的 8 個 SHA **全數與今日 live readback 相符** → 快照仍有效，無需重新 freeze。

## 5. 宣稱上限（進場即宣告，出場不得自行抬升）

- Foundation：`PASS_SCOPED_RELEASED_PRERELEASE` + `PARTIAL_CHALLENGE`（不變）。
- c3：修補後最高 `PACKAGED_HOST_PENDING`；`INSTALLED`／`EFFECTIVE_LOAD` 僅在 Docker/Hermes 有真收據的欄位才可寫。
- 五工具：逐列各自天花板；組合成功不得掩蓋單體失敗。
- SWOF：`W2_SHADOW_ONLY`；`W3` = `NOT_GRANTED`。
- 全程不得宣稱：`INDEPENDENT_CASE_PASS`、`HGK_NATIVE_EFFECT_READY`、`FULL_SBL_ACCEPTED`、`PRODUCTION`。

## 6. 反過度治理（R4 §6 停損）

不重裝 6 donor、不動 423 `DEFERRED`、不重開 v8 缺陷、不為修一個 manifest 去跑 441×149×38 測試乘積。同型失效最多兩個 narrow repair attempt，之後 checkpoint + escalate。
