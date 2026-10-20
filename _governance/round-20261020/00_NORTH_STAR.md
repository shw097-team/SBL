# SBL v0.1｜核心大目標（North Star）與完成定義

```yaml
round: SBL-PIPDLS-20261020
project_id: HGK-PRJ-SBL-PIPDLS
run_id: RUN-DEF3C204
control_plane: HG-KSEOS
runtime_plane: current canonical Hermes (governed)
normative_package: 'C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG' (DOC-00..DOC-13)
working_source_mirror: 'C:\Projects\Agent_Workspace\_sbl_src_mirror'  # byte-identical robocopy of the read-only corpus, 306 files
product_root: 'C:\Projects\Agent_Workspace\SBL'
remote_target: 'https://github.com/shw097-team/SBL' (public, to be created)
claim_ceiling: LOCAL_BOOTSTRAP + CANDIDATE_ONLY — 不自我驗收、不自我升格
```

## 1. 唯一大目標（不可降級）

在 `C:\Projects\Agent_Workspace\SBL` 建立**真正可安裝、可操作、可測試、可重啟、可卸載、可回滾**的
SBL / SpecBuild Loop v0.1：以 `Guided Spec → Governed Build → Evidence-based Verify → Bounded Repair`
跑通一條 Shared Core、六個邏輯模組（SBLM01..SBLM06）、三個權責分離 SP（TPM-SP / Commander-SP /
External Challenge-SP）、三種模式（STANDALONE / PREW3_SHADOW NoEffect / SWOF_CONNECTED 受原生 ACK 管制）、
三條 Golden Journey（GJ01 CLI_TOOL、GJ02 Brownfield scoped patch、GJ03 AGENT_SKILL + SIMPLE_AGENT），
並把每輪合格候選與脫敏證據推到 `shw097-team/SBL` 公開 repo，供外部獨立驗收官與外部工程團隊使用。

## 2. 完成不是文件完成

「完成」的判定是**同一 frozen candidate 下**同時成立：

1. 真 Host/CLI 的使用者操作 FUO（GJ01 clean install → add → list --json → 重啟 → 卸載無殘留）。
2. 需求 trace closure：`SourceClause → REQ → SPEC → ACC → POS/NEG/EDGE/SEC → EEXP → DELIVER` 雙向可追、orphan=0。
3. 原始測試收據：每條測試的命令、exit code、分母、raw log SHA。
4. 有效權限與回滾：每次 repo-mutating effect 有 ONE ECP、permit、before/after、readback、rollback pointer。
5. 不同 Principal 的獨立驗證：VERIFY/SECURITY 車道（openai-codex/gpt-6.1-sol，read-only）真派發且
   `required_arm == served_arm`、`usage_receipt_ok`。
6. GitHub exact SHA readback：`source_candidate_sha + evidence_commit_sha` 可由第三方重讀。

## 3. Claim 分層（本輪只提升到有收據的層級）

`PROMPT_COMPILE_PASS` ≠ `RUNTIME_READY` ≠ `LOCAL_QUALIFIED` ≠ `INDEPENDENT_CASE_PASS` ≠ `RELEASED` ≠ `PRODUCTION`。

- 本輪目前可宣稱：車道模型方案可用（PLAN/VERIFY = gpt-6.1-sol、EXECUTE = deepseek-v4.1-flash，三張真實收據）。
- 本輪不得宣稱：任何產品功能已驗收、任何外部 PASS、任何 Release/Production 資格。

## 4. 非目標

- 不新增上位未授權功能；不調降任何驗收條件；不以備份取代 source。
- 不把 386 具名技術全數安裝（只裝准入 slot）。
- 不改寫 HG-KSEOS / Fabric 封存政策；不改 Oracle / RBWI / reducer。
- 不在無 Native ACK/Permit 情況下讓 `PREW3_SHADOW` 產生世界副作用或宣稱 `SWOF_CONNECTED` 已連接。

## 5. 來源權威（分域偏序）

產品規格：`SBL_PIPD-LS-PKG DOC-00..DOC-13`（本輪 SSOT；實體 14 檔，見 SOURCE_LEDGER）。
任務／Effect：HG-KSEOS Native 契約（Shared Spine WorkOrder、ECP/Permit、ExecutionBinding）。
治理／保證／互通：Fabric 契約面（只作 contract surface，不是第二控制平面）。
外部 OSS／網頁／AI 衍生知識：SUPPORT only，不升格 Normative。
