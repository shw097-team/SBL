---
artifact_id: FHS_vNEXT_PLP_W1
source_manifest_sha256: bbcfb1331c6c7c7cf804bbc476d038992788c630975ee82268d87da0058e3096
supersedes: none (first W1 entry specification)
scope: W1 entry readiness; not a repository, not a work order execution
claim_ceiling: AUTHOR_DESIGN_WITH_SCOPED_HOLDS
rollback_ref: W0 remains the effective baseline; nothing in W1 is created until its WorkOrder is bound
---

# FHS vNEXT PLP W1 入口規格（作者候選）

## 1. W1 的責任邊界

W1 建立**有權**私有單庫 `shw097-team/FHS`、一棵 Git root、原 Fabric／SBL／HGK 模組、Caller／CLI／Schema／ABI、
CI／Secret Scanner／License，以及手冊能力主接線。W1 不執行 Protected Effect（W2）、不跑 4Host×3SP 資格化（W3）、
不做 Cutover（W4）。

## 2. 入口七列（對應 BASELINE §7），逐列附證據

| # | W1 Entry | 所需證據 | 本回合證據 | 狀態 |
|---|---|---|---|---|
| 1 | 既有 Hermes 可重啟 | Profile／CWD／venv／Gateway | `out/E0_SOURCE_SNAPSHOT.json`；selfcheck 16/16 | READY |
| 2 | HGK 不混 Epoch／獨立身份 | Owner Selected Authority；H16 FailClosed | registry 41/41、assignment r44、pool r37；H16 wrapper scoped | READY |
| 3 | SBL PIPD 原編譯入口 | 原 `integrations/pipd`、CI/ABI/Reader | 匯入樹唯讀；接線屬 W1 | READY_WITH_HOLD |
| 4 | Fabric 導航與權限 | FHS-NAV/v2、`effect_permission=NONE` | 兩個入口面已撤（`out/W0_ENTRY_SURFACE_WITHDRAWAL.json`） | READY |
| 5 | GitHub FHS 單庫候選 | Owner／RepoName／ACL／Module Boundaries | W0 禁止建立；未建立 | READY_NOT_CREATED_BY_DESIGN |
| 6 | W0 源與六 WP | 31 source、SPEC/FUO、SourceSHA、ReaderMap | Baseline A–D 各一次；r7 byte-identical | READY |
| 7 | Scope／Hold | G16b/G22 若宣告全掃需 true；分帳 | G16b PASS，NEG 可復現；未宣告全掃 | REPORTED_OPEN_CONDITIONAL |

## 3. 第一個 WorkOrder 的綁定欄位（未執行）

```
goal:             W1 最小試點：Source → 三 SPEC → PIPD 已批准 Reader/ABI → 原域候選 → 受界本地測試
subject:          FHS_vNEXT_PLP_W1 §2 第 6 列（W0 源與六 WP）
source_manifest:  bbcfb1331c6c7c7cf804bbc476d038992788c630975ee82268d87da0058e3096
repo_context:     shw097-team/FHS（不存在；建立需原 Owner 授權）
original_owner:   SBL PIPD Writer / HGK Issuer（依受影域）
consumer:         FHS_NEXT 外部工程團隊
cli_abi:          未綁定（W1 建立後回填）
acc_pos:          三 SPEC 身分不變、FUO 可讀、SourceSHA 可重算
acc_neg:          錯誤 Manifest exit 14；未派定臂拒絕；退役臂拒絕
first_fail:       RepoContext 缺 → 不得偽造 canonical PD
resume:           取得 RepoContext 後由原 Writer 生成 PI/PD
```

## 4. 手冊能力四分類（W1 判準）

`REUSE_VERIFIED` / `REBIND` / `REQUALIFY` / `DEFER_OR_NOFIT`，依 Need／Effect／OriginalOwner／Host 實判；
不以「57 列都要在 W0 執行」作前置。

## 5. 本次未主張

未建立 `shw097-team/FHS`、未產生 canonical PD、未取得 RepoContext、未執行任何 WorkOrder。
