---
artifact_id: FHS_vNEXT_PLP_藍圖
source_manifest_sha256: bbcfb1331c6c7c7cf804bbc476d038992788c630975ee82268d87da0058e3096
supersedes: none (new L1 candidate)
scope: author candidate; not ratified
claim_ceiling: AUTHOR_DESIGN_WITH_SCOPED_HOLDS
rollback_ref: keep the previous effective document unchanged until an original reader adopts this file
generated: 2026-11-12T20:45:46
---

# FHS vNEXT PLP 藍圖（L1 作者候選）

## 1. 同 Subject 三 SPEC

PM／SE／TPgM 三份 SPEC 共用 `Goal / SubjectRef / Scope / SourceManifestSHA`，而在
`Artifact / OriginalConsumer / ACC / body sha256` 上兩兩不同。判準由 `ops/tools/spec_identity_check.py` 提供，
本回合實測 `ok=true`、錯誤 Manifest 走 exit 14。

## 2. 原 Writer 與 Binding

- 只有原 SBL PIPD Writer 能編 PI/PD/ECP/TQAEP；本根只產生作者端草案。
- `pipd-authority-source` 需 AuthorityBinding ＋ SourceFreezeManifest；`pipd-package-project` 核 canonical bodies/Reader/graph/Case。
- W0 母本 r26 `0ea05544…`（668,540 B）；作者端修訂 r7 `35daf4c1…`（677,204 B，正文 byte-identical）。

## 3. Maker / Checker 與 SoD

- 每個 ordered_pool 條目必須有 `rank:int`、`provider`、`model`；rank 1 為唯一自動選用。
- SoD 以 **model** 與 **provider** 兩軸判定；本回合 VERIFY_SECURITY 的 assignment 只派 `gpt-6.1-sol`，
  因此 deepseek 作為 checker 會被原域 `ERR_ARM_NOT_IN_ASSIGNMENT` 拒絕（實測），須由原域改派而非繞過。
- **兩軸只是必要條件，不是獨立驗收的充分條件。** 任一審查回合另需同時具備：`WorkOrder`（受影任務與範圍）、
  `Principal`（Maker 的可信身分，來自 assignment／WorkOrder 而非自述）、`Checker`（另一 Principal 的指派記錄）、
  `Scope`（被審物件的 Subject／SourceSHA／版本）、`Nonce`（由模型本身回聲，否則是 `ERR_NO_ARM_EMITTED_NONCE`）、
  以及**原 Guard 的責任歸屬**（Protected 路徑的 fail-closed 由原 HGK Issuer／Guard 判定，不由本根代替）。
- 本回合 H16 仍是 `PASS_WRAPPER_SCOPED`：**不同模型 ≠ 已獨立驗收**。原 HGK Protected Path 未正式關閉前，
  L1 不得把「model／provider 不同」寫成 SoD 已完成或驗收已獨立。
- `--force-rank` 不得成為繞過 assignment 的路徑（本回合已於 wrapper fail-closed）。

## 4. Source 與 ABI 追溯

E0 SourceSnapshot 釘住 9 份輸入（r2／r26／Baseline 底稿／R2 Report／W1 Handoff／R4 ZIP／r7／AsBuilt／控制書），
逐份 `path / bytes / sha256 / observed_at`；Git 物件以 blob（LF）計。

## 5. POS / NEG

- POS：三 SPEC 身分、FUO 存在、G16b PASS、served==required 由原回執證明。
- NEG：同 Principal maker/checker 拒絕；退役臂拒絕；未派定臂拒絕；來源 digest 不符即 `SOURCE_SCOPE_HOLD`。

## 6. 本次未主張

原 Reader 採納、Canonical 版本、Protected Effect、Multi-Host 資格化。
