# SBL round R3 — North Star (核心大目標)

**Round**: `round-20261020-r3`  ｜ **Instruction**: `SBL-R3-V13-FULL-COVERAGE-20261020` (`SBL-HGK-THIN-ROUTEOUT/3`)
**Entry claims**: `CANDIDATE_ONLY; NOT_MERGED; NOT_RELEASED; M4_LITE_OPEN; R2_OPEN`
**Entry HEADs**: `main=ca6830d9fc9d89b7b87e818670dd67b393472d79`, `candidate/r2-20261020-v13=bedc11957d4fc2474b249b69d200829272c118ef`,
`evidence/r2-20261020-c3=6cb9d03f6fe5f43baf379b5a9a2e7ad328d38dce`

## 1. 不變的目標

依 SBL DOC-00..13 建立可實際安裝、操作、卸載、回滾、驗證的 SBL / SpecBuild Loop；使用者體驗為
`Guided Spec → Governed Build → Evidence-based Verify → Bounded Repair`。SBL 是獨立產品，不是 SWOF GENIE，也不是 HGK 本身。

## 2. 本輪三個互不冒充的 Claim Tracks

| Track | 內容 | 本輪唯一可宣稱的終態 | 不可宣稱 |
|---|---|---|---|
| **A** v13 foundation 合併資格 | 六性質 POS/NEG 的非 Maker 人工程序覆核 + CI + PR + Owner manual merge | `MERGE_READY_HUMAN_REVIEWED`（人類簽名後）；Owner 真 merge + readback 才 `MERGED` | `INDEPENDENT_CASE_PASS` |
| **B** 狹義 Preview 封裝 | 由 `bedc119` 打 wheel+sdist → clean venv install → 跨進程 FUO → uninstall → residue/digest | `FOUNDATION_PREVIEW_READY`（Owner 發 Release 後才 `RELEASED`） | 三 SP 已裝、通用 Skill/Agent builder |
| **C** FULL DESIGN | 三 SP 封裝/identity、Host install request、HGK Harness、PIPD 8 Writer、441/149/38 ledger、ProductKind/GJ | `PARTIAL_FULL_DESIGN` + 具名 TT | `FULL_DESIGN_QUALIFIED` |

## 3. 分層宣告（不可互換）

`PROMPT_COMPILE_PASS` ≠ `PIPD_PI_PD_BOUND` ≠ `HGK_NATIVE_EFFECT_READY` ≠ `STANDALONE_TEST_PASS` ≠ `CI_PASS`
≠ `HUMAN_PROCEDURAL_ACCEPTANCE` ≠ `INDEPENDENT_CASE_PASS` ≠ `MERGED` ≠ `FOUNDATION_PREVIEW_RELEASED`
≠ `THREE_PRIVATE_PLUGINS_HOST_VERIFIED` ≠ `FULL_SBL_ACCEPTED` ≠ `SWOF_W3/PRODUCTION`。

## 4. 本輪模型方案（車道 ≠ 會話）

| 角色 | 綁定 | 本輪實測狀態 |
|---|---|---|
| PLAN / Orchestrator | `openai-codex/gpt-6.1-sol`（medium, OpenAI OAuth） | PLAN lane `--force-rank 2` 可用（R2 已實測 `ok:true`） |
| EXECUTE bounded writer | `opencode-go/deepseek-v4.1-flash` | EXECUTE lane smoke `ok:true` |
| VERIFY / SECURITY | Codex CLI + `gpt-6.1-sol` | `openai-codex` websocket 426；以 PLAN lane read-only 作**同 principal、不同載體**替補（Owner 於 R2 `90_OWNER_DECISIONS.md` 已授權） |

會話模型（本 session 互動）與車道模型是兩個平面；本輪不把會話 pin 當車道綁定。

## 5. 停止條件

- 一份有效 M4-LITE 人類收據後 **停止模型反證**（不開第 18 輪）。
- 任一 Provider/Host/權威不可用 → checkpoint + escalate，不加治理層、不改 Oracle、不降門檻。
- 人類簽名缺席 → `M4_LITE_HOLD`，Maker 不得代簽。
