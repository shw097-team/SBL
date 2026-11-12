---
artifact_id: FHS_vNEXT_總藍圖
source_manifest_sha256: bbcfb1331c6c7c7cf804bbc476d038992788c630975ee82268d87da0058e3096
supersedes: none (new L0 candidate)
scope: author candidate; not ratified
claim_ceiling: AUTHOR_DESIGN_WITH_SCOPED_HOLDS
rollback_ref: keep the previous effective document unchanged until an original reader adopts this file
generated: 2026-11-12T20:45:46
---

# FHS vNEXT 總藍圖（L0 作者候選）

## 1. 產品與生存根

- 產品：以 Hermes v0.23.1 為唯一 Commander，於 `C:\Projects\Agent_Workspace\FHS_NEXT` 施工；不重建 W0、不新增 Profile。
- 生存根：所有產物位於 `FHS_NEXT` 或 `FHS_NEXT_Workspace`（業主最高裁決 OD-3）；違反者為無效規劃，不得作為 HOLD。
- 單一原域權威：Fabric＝治理鏡像（`effect_permission=NONE`）、SBL＝產品工程指揮入口、HG-KSEOS＝原生授權／狀態／驗收控制平面。

## 2. 不可縮小的分母

`50 CH`、`22 WP`、`36 Edge`、`31 Source`、`485 OriginalSlotID`、`949 原子`、`192 Cell`、`96 Oracle`、`282 B1 Case`。
本文件不縮小任何分母；W0 只證其**適用**部分。

## 3. 波次分工（不提前）

| 波次 | 內容 | 本回合狀態 |
|---|---|---|
| W0 | Source／三 SPEC／FUO／Trace／Handoff | 受界完成；見 Baseline 與 r7 |
| W1 | 私有單庫、模組 ABI、手冊能力主接線 | 入口已備（`FHS_vNEXT_PLP_W1.md`），未建立 repo |
| W2 | 第一個合法 Protected Slice | 未開始 |
| W3 | 4 Host×3 SP／192 Cell 資格化 | 未開始 |
| W4 | 可逆 Cutover 與舊根退場 | 未開始 |

## 4. 控制平面現況（實測）

registry `epoch 41` / `contract_epoch 41`；assignment `revision 44` / `registry_epoch 41`；pool `revision 37` / `epoch 41`；
三車道 primary：PLAN `gpt-6.1-sol`、EXECUTE `deepseek-v4.1-flash`、VERIFY_SECURITY `gpt-6.1-sol`。
OD-4 移除 6 臂（`mimo-v2.6-pro`、`glm-5.3`、`glm-5.3-flash`、`z-ai/glm-5.3`、`z-ai/glm-5.3-flash`、`minimax-m3.1-flash-free`）。

## 5. POS / NEG

- POS：SourceSnapshot 全 SHA 可重算；G19 394/394（73 群）；selfcheck 16/16；G16b PASS（NEG 可復現）。
- NEG：退役臂 `--require-arm glm-5.3` → `ERR_LANE_REQUIRED_ARM_ABSENT`；未派定臂 `--require-arm` → `ERR_ARM_NOT_IN_ASSIGNMENT`；
  `--force-rank` 落在未派定臂 → `ERR_FORCE_RANK_ARM_NOT_ASSIGNED`（本回合新增）。

## 6. 本次未主張

原域 Canonical、Native Grant、Independent PASS、Release、GitHub main 合併（除已合併之 PR #19–#22、#24）。
