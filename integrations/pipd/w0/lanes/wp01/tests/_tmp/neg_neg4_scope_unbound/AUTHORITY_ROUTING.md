# AUTHORITY_ROUTING — WP-FHS-01 權威分流（FHS_W0_IMPL/AUTHORITY_ROUTING/v1）

- source_root: `C:\Projects\Agent_Workspace\var\FHS_W0_IMPLEMENTATION_20261105_0305\payload\sbl\integrations\pipd\w0\lanes\wp01\tests\fixtures\neg4_scope_unbound`
- readback_root: `C:\Projects\Agent_Workspace\var\FHS_W0_IMPLEMENTATION_20261105_0305\payload\sbl\integrations\pipd\w0\lanes\wp01\tests\fixtures\neg4_scope_unbound\_no_readback`
- claim_ceiling: `AUTHOR_LOCAL_TEST`（作者本地可重跑；非 Native、非受保護 Checker）
- may_mint_permit: `false`（全部 1 筆）

## 統計

| 項目 | 值 |
| --- | --- |
| 總筆數 | 1 |
| CANONICAL_ORIGINAL | 1 |
| GOVERNANCE_MIRROR | 0 |
| SKILL_SIDECAR | 0 |
| HISTORICAL_ARCHIVED | 0 |
| AUTHOR_CANDIDATE | 0 |
| SOURCE31 宣告／實際路由 | 1 / 1 |
| may_authorize_write=true | 0 |
| may_mint_permit=true | 0 |
| HOLD 筆數 | 1 |

`may_authorize_write=true` 為 0 的理由：閘門要求 class=CANONICAL_ORIGINAL＋顯式 write_authority 授權＋已宣告非 NONE 的 effect_permission＋無 HOLD。本輪無任何來源同時滿足（31 原件與 SBL 原始碼未宣告 write_authority；mirror effect_permission=NONE；PIPD archived/write_authority=NONE；Skill 非 permit；作者產物為 candidate）。

## 規則

| Rule | 陳述 | 碼 |
| --- | --- | --- |
| R1 | effect_permission=NONE → may_authorize_write=false；GOVERNANCE_MIRROR 一律不可授寫（evidence: repository-map.json:$.effect_permission） | `AUTHORITY_MIRROR_NOT_WRITABLE` |
| R2 | archived=true 或 write_authority=NONE → HISTORICAL_ARCHIVED，且不得為 canonical（evidence: repository-map.json:$.historical_repositories.*） | `HISTORICAL_ARCHIVED_NOT_CANONICAL` |
| R3 | Skill/Sidecar 不得作為 Canonical Compiler 或 Checker（evidence: PLUGIN_USAGE_AND_GHP01.json:$.canonical_compiler / $.host_loaded） | `SKILL_NOT_PERMIT` |
| R4 | 同一 canonical_key（subject_id#artifact_key）出現兩個 CANONICAL_ORIGINAL → HOLD | `AUTHORITY_CONFLICT_DUAL_CANONICAL` |
| R5 | 缺 subject/scope 綁定，或 subject_ref 與當前 candidate body 不符 → HOLD（evidence: SBL AuthorityBinding.schema.json requires subject_id minLength 8） | `AUTHORITY_SCOPE_UNBOUND` |
| R6 | Profile 與 Role 與 Worker 不可互換（evidence: SBL ProfileBinding.schema.json:$.properties.profile.enum = LITE\|STANDARD\|ASSURED，非 role/worker 識別） | `PROFILE_ROLE_CONFLATED` |
| R7 | Mirror 讀回的 git blob sha1 與 REPOS_RECHECK 記錄的 ref blob 不符 → HOLD（bytes ≠ blob ⇒ 授權欄位出處不可證） | `AUTHORITY_MIRROR_IDENTITY_UNVERIFIED` |
| R8 | canonical_compiler=NOT_RUN 或 host_loaded=NOT_OBSERVED → HOLD（本輪無 canonical 編譯收據） | `CANONICAL_COMPILER_NOT_RUN` |
| R9 | SOURCE31 每筆 currentness=ORIGINAL_READER_CURRENTNESS_HOLD → 聚合 HOLD（檔案身份通過 ≠ 原 Reader 當期性已確認） | `ORIGINAL_READER_CURRENTNESS_UNVERIFIED` |

## 檢查結果

```json
{
 "mirror_identity": {
  "status": "NOT_CHECKED"
 },
 "r4_dual_canonical_groups": {
  "canonical_keys": 1,
  "conflicting_keys": 0
 },
 "source31_currentness": {
  "currentness_hold_entries": 0,
  "declared_entries": 1
 }
}
```

## CANONICAL_ORIGINAL（1）

| source_id | class | evidence_field | reason_code |
| --- | --- | --- | --- |
| `SYN-UNBOUND` | CANONICAL_ORIGINAL | `SOURCE31_PHYSICAL_IDENTITY.json:$[0].physical_identity` = PASS | `AUTHORITY_SCOPE_UNBOUND` |

## GOVERNANCE_MIRROR（0）

| source_id | class | evidence_field | reason_code |
| --- | --- | --- | --- |

## SKILL_SIDECAR（0）

| source_id | class | evidence_field | reason_code |
| --- | --- | --- | --- |

## HISTORICAL_ARCHIVED（0）

| source_id | class | evidence_field | reason_code |
| --- | --- | --- | --- |

## AUTHOR_CANDIDATE（0）

| source_id | class | evidence_field | reason_code |
| --- | --- | --- | --- |

## HOLD（1）

| hold_id | code | owner | required_raw | resume_predicate |
| --- | --- | --- | --- | --- |
| `H-AUTH-R4C-001-SCOPE` | `AUTHORITY_SCOPE_UNBOUND` | Original Owner of synthetic/corpus/UNBOUND.md（artifact 的 subject Owner） | 能解析到當前 candidate body sha256 的 subject/scope 綁定（或原 Owner 明示該 artifact 的 subject 與當前 candidate 之對應） | 該 artifact 宣告的 subject_ref 等於當前 candidate body sha256，或原 Owner 出具 binding 讀回 |

## 非宣稱

- 不宣稱任何 Native/Permit/WorkOrder/受保護 Checker 判決
- 不宣稱 mirror 讀回與 ref blob byte-exact（見 mirror_identity 檢查與 HOLD）
- 不宣稱 31 份原件當期性（currentness HOLD 未解）
- 不宣稱 PIPD-LS-SP 的 archived 狀態由本輪變更
- 分類為本輪 LANE 內可重跑的作者分流結果，claim ceiling=AUTHOR_LOCAL_TEST
