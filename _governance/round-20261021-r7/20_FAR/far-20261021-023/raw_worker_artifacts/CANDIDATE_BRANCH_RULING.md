## CANDIDATE BRANCH RULING

測量快照：2026-10-21T13:17:41.776843+08:00。

**結論：僅 SBL PR#2 推薦 MERGE_NOW（scoped）；PIPD-LS-SP 沒有推薦整枝 merge。這是工程併入建議，不是已 merge 或全合約通過。**

SBL main=`bedc11957d4fc2474b249b69d200829272c118ef`；PIPD-LS-SP main=`e95942abcb6aa07e69304607ab8afc22a74fc67d`；PR#2 open、未 merged、head=`a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2`、base=SBL main，API mergeable=true/clean。

49 個非 main 分支：MERGE_NOW 1、SUPERSEDED 26、EVIDENCE_ONLY 16、NOT_RECOMMENDED 3、DO_NOT_MERGE 3。

表中 ahead/behind=候選/main；差異為 merge-base→候選（main...head）；檔案含 binary，+/- 僅文字行。CI 是各凍結 head SHA 的可見 check-runs，不是 main 或 merge-result 的推測。NO_RUNS 不是 PASS，未併後繼支線也不是 main 已有。

| 分支 | repo | ahead/behind | 檔案數/行數 | 與 main 衝突? | 被誰 supersede? | 裁決 | 理由（一句話）|
|---|---|---:|---:|---|---|---|---|
| `candidate/c3-20261020-v1` | SBL | 1/0 | 7 / +401/−1 | 否（exit 0） | candidate/c3-20261021-v2（未併） | **SUPERSEDED** | v1 為 v2 祖先，應只處理 v2；CI=test (ubuntu-latest, py3.11):success,test (windows-latest, py3.11):success |
| `candidate/c3-20261021-v2` | SBL | 6/0 | 27 / +2576/−63 | 否（exit 0） | — | **MERGE_NOW** | PR#2 為可乾淨併入的產品增量，雙平台 CI 成功；僅 scoped merge；CI=test (ubuntu-latest, py3.11):success,test (windows-latest, py3.11):success |
| `candidate/r2-20261020-v10` | SBL | 0/6 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=test (ubuntu-latest, py3.11):success,test (windows-latest, py3.11):success |
| `candidate/r2-20261020-v11` | SBL | 0/2 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=test (ubuntu-latest, py3.11):success,test (windows-latest, py3.11):success |
| `candidate/r2-20261020-v12` | SBL | 0/1 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=test (ubuntu-latest, py3.11):success,test (windows-latest, py3.11):success |
| `candidate/r2-20261020-v13` | SBL | 0/0 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=test (ubuntu-latest, py3.11):success,test (windows-latest, py3.11):success |
| `evidence/r2-20261020-c1` | SBL | 0/8 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=NO_RUNS |
| `evidence/r2-20261020-c2` | SBL | 0/3 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=NO_RUNS |
| `evidence/r2-20261020-c3` | SBL | 6/0 | 46 / +18175/−4 | 否（exit 0） | evidence/r6-20261021-c6（未併證據鏈） | **EVIDENCE_ONLY** | 治理契約及驗收證據，不是產品交付分支；CI=NO_RUNS |
| `evidence/r4-20261021-c4` | SBL | 15/0 | 82 / +26674/−4 | 否（exit 0） | evidence/r6-20261021-c6（未併證據鏈） | **EVIDENCE_ONLY** | 治理契約及驗收證據，不是產品交付分支；CI=NO_RUNS |
| `evidence/r5-20261021-c5` | SBL | 19/0 | 116 / +31945/−4 | 否（exit 0） | evidence/r6-20261021-c6（未併證據鏈） | **EVIDENCE_ONLY** | 治理契約及驗收證據，不是產品交付分支；CI=NO_RUNS |
| `evidence/r6-20261021-c6` | SBL | 25/0 | 166 / +42672/−4 | 否（exit 0） | — | **EVIDENCE_ONLY** | 治理契約及驗收證據，不是產品交付分支；CI=NO_RUNS |
| `chore/s4post-verification-harness` | PIPD-LS-SP | 18/94 | 76 / +9930/−292 | 是（exit 1） | main（部分 patch-equivalent） | **NOT_RECOMMENDED** | 僅一個非等價 patch 殘留，整枝會帶回舊 README 及治理衝突；CI=offline-gate:success |
| `docs/preview4-sums-count-truthfulness-20261014` | PIPD-LS-SP | 0/22 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `docs/r5r3-asset-reproducibility-readback` | PIPD-LS-SP | 0/11 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `docs/repo-state-and-handover-refresh-20261016` | PIPD-LS-SP | 0/11 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success |
| `docs/three-install-routes-20261016` | PIPD-LS-SP | 0/2 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:failure |
| `evidence/cnv-pipd-ls-sp-20261015-r6` | PIPD-LS-SP | 4/19 | 567 / +65305/−0 | 否（exit 0） | — | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `evidence/cnv-r7-0-validator-hardening-20261015` | PIPD-LS-SP | 1/19 | 16 / +2848/−0 | 否（exit 0） | — | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `feat/s4post-triple-upgrade-20261012` | PIPD-LS-SP | 1/162 | 7 / +1398/−0 | 是（exit 1） | main（全部 patch-equivalent） | **SUPERSEDED** | git cherry 唯一提交為「-」，雖仍衝突但無新 patch 可併；CI=offline-gate:failure |
| `feat/s4post-triple-upgrade-20261012-r2` | PIPD-LS-SP | 17/94 | 76 / +9930/−292 | 是（exit 1） | main（部分 patch-equivalent） | **NOT_RECOMMENDED** | 僅一個非等價 patch 殘留，整枝會帶回舊 README 及治理衝突；CI=offline-gate:success |
| `feat/s4post-triple-upgrade-20261013-r3` | PIPD-LS-SP | 0/71 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:failure |
| `feat/s4r3-stage-b-distribution-20261013` | PIPD-LS-SP | 17/70 | 47 / +8389/−13 | 是（exit 1） | — | **DO_NOT_MERGE** | CI workflow、README、USER_GUIDE 及治理記錄均實測衝突；CI=offline-gate:success |
| `feat/s4r3-stageb-successor-20261013` | PIPD-LS-SP | 0/36 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `feat/s4r5x-manifest-fit-20261014` | PIPD-LS-SP | 0/35 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success |
| `feat/s4r5y-plugin-publication-20261014` | PIPD-LS-SP | 0/34 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `feat/s4r5z-evidence-readme-20261014` | PIPD-LS-SP | 2/34 | 208 / +24819/−0 | 是（exit 1） | r5z-evidence-return-20261014（未併） | **EVIDENCE_ONLY** | 證據重載且 README 衝突，產品等價 patch 已在 main；CI=offline-gate:success,verify:failure |
| `feat/s4r5z-readme-plugin-route-20261014` | PIPD-LS-SP | 0/32 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `feat/s4r7-main-upgrade-and-repo-state-20261014` | PIPD-LS-SP | 0/30 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `fix/r5r2-segment-and-boundary-20261014` | PIPD-LS-SP | 0/22 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `fix/r5r3-preview4-identity-and-route` | PIPD-LS-SP | 0/13 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `fix/s4-external-challenge-20261012-r1-provenance-trace` | PIPD-LS-SP | 11/166 | 174 / +70806/−68 | 是（exit 1） | — | **DO_NOT_MERGE** | preview.3 pack 與 RELEASE_TUPLE 身分衝突，不得以整枝覆蓋解決；CI=NO_RUNS |
| `fix/s4post-far-adjudication-20261012` | PIPD-LS-SP | 3/164 | 17 / +47980/−41 | 否（exit 0） | — | **NOT_RECOMMENDED** | 雖乾淨合併，但 head offline-gate 失敗且含大批 writer logs；CI=offline-gate:failure |
| `fix/s4post-integration-repair-20261012` | PIPD-LS-SP | 0/160 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:failure |
| `fix/s4r3-stage-a-ci-truthfulness-20261013` | PIPD-LS-SP | 0/61 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `fix/s4r5r-d1d2-claimceiling-preview4-20261014` | PIPD-LS-SP | 0/24 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `fix/s4r6-closeout-doc-identity-and-update-route-20261016` | PIPD-LS-SP | 0/8 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `fix/s4r7-readme-main-sha-truthfulness-20261014` | PIPD-LS-SP | 0/28 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=offline-gate:success,verify:success |
| `r5-s4-evidence` | PIPD-LS-SP | 1/264 | 2 / +145/−0 | 否（exit 0） | — | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=NO_RUNS |
| `r5-s4-readme` | PIPD-LS-SP | 1/264 | 1 / +217/−71 | 是（exit 1） | — | **DO_NOT_MERGE** | README 實測衝突且落後 main 264 個提交，未見 head CI；CI=NO_RUNS |
| `r5r-evidence-return-20261014` | PIPD-LS-SP | 9/23 | 85 / +9228/−0 | 否（exit 0） | — | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `r5r3-closeout-evidence-20261016` | PIPD-LS-SP | 7/12 | 112 / +8227/−3 | 否（exit 0） | — | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `r5r3-evidence-return-20261016` | PIPD-LS-SP | 13/19 | 80 / +9665/−0 | 否（exit 0） | — | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `r5z-evidence-return-20261014` | PIPD-LS-SP | 16/34 | 368 / +38169/−0 | 是（exit 1） | — | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `r6-closeout-evidence-20261016` | PIPD-LS-SP | 10/11 | 113 / +10444/−0 | 是（exit 1） | unmerged-merge-evidence-20261016（未併證據鏈） | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `repo-hygiene-evidence-20261016` | PIPD-LS-SP | 22/11 | 143 / +12670/−0 | 是（exit 1） | unmerged-merge-evidence-20261016（未併證據鏈） | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `s4-final-closeout-evidence-20261016` | PIPD-LS-SP | 14/11 | 127 / +11748/−0 | 是（exit 1） | unmerged-merge-evidence-20261016（未併證據鏈） | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |
| `s4-r2-affected-only-20261011` | PIPD-LS-SP | 0/174 | 0 / +0/−0 | 否（exit 0） | main（ancestry） | **SUPERSEDED** | 已是 main 祖先或同一 SHA，無待併提交；CI=NO_RUNS |
| `unmerged-merge-evidence-20261016` | PIPD-LS-SP | 26/11 | 155 / +13659/−0 | 是（exit 1） | — | **EVIDENCE_ONLY** | 新增主要為歷史證據封包，不能以 CI 成功推定需進產品 main；CI=offline-gate:success |

### 逐分支 Git 與 CI 測量索引

測量起點：2026-10-21T13:17:41.776843+08:00；git version 2.53.0.windows.1。

| repo / 分支 | head SHA | merge-base SHA | top-level 檔案分佈 | CI check-runs |
|---|---|---|---|---|
| SBL / `candidate/c3-20261020-v1` | `39c604d52570922fdf84b6df9c9359765643b450` | `bedc11957d4fc2474b249b69d200829272c118ef` | (root):1；sbl_sp:4；tests:1；tools:1 | test (ubuntu-latest, py3.11):success, test (windows-latest, py3.11):success |
| SBL / `candidate/c3-20261021-v2` | `a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2` | `bedc11957d4fc2474b249b69d200829272c118ef` | .github:1；evidence:8；(root):1；sbl_core:1；sbl_harness:2；sbl_sp:6；sbl_stack:3；tests:3；tools:2 | test (ubuntu-latest, py3.11):success, test (windows-latest, py3.11):success |
| SBL / `candidate/r2-20261020-v10` | `2d1c32d6c48fdc09a7d529fc4535482283552487` | `2d1c32d6c48fdc09a7d529fc4535482283552487` | 無三點差異 | test (ubuntu-latest, py3.11):success, test (windows-latest, py3.11):success |
| SBL / `candidate/r2-20261020-v11` | `b5fd5d0a4f9eddf91cb98d7c2aafd77776fca295` | `b5fd5d0a4f9eddf91cb98d7c2aafd77776fca295` | 無三點差異 | test (ubuntu-latest, py3.11):success, test (windows-latest, py3.11):success |
| SBL / `candidate/r2-20261020-v12` | `815057dd7e8c1d9a2c982d9c56121081aa06dc21` | `815057dd7e8c1d9a2c982d9c56121081aa06dc21` | 無三點差異 | test (ubuntu-latest, py3.11):success, test (windows-latest, py3.11):success |
| SBL / `candidate/r2-20261020-v13` | `bedc11957d4fc2474b249b69d200829272c118ef` | `bedc11957d4fc2474b249b69d200829272c118ef` | 無三點差異 | test (ubuntu-latest, py3.11):success, test (windows-latest, py3.11):success |
| SBL / `evidence/r2-20261020-c1` | `31e95995c3b3899d928e2a0600bc53413f4eeb9a` | `31e95995c3b3899d928e2a0600bc53413f4eeb9a` | 無三點差異 | NO_RUNS |
| SBL / `evidence/r2-20261020-c2` | `4b15cdfc31a44c705c4cfc24b971446222c985ae` | `4b15cdfc31a44c705c4cfc24b971446222c985ae` | 無三點差異 | NO_RUNS |
| SBL / `evidence/r2-20261020-c3` | `cfedf094996a801493d5b9574cd14742668549c9` | `bedc11957d4fc2474b249b69d200829272c118ef` | _governance:31；contracts:8；evidence:6；openspec:1 | NO_RUNS |
| SBL / `evidence/r4-20261021-c4` | `02e14d4343619ef509011f5629215efe25e75746` | `bedc11957d4fc2474b249b69d200829272c118ef` | (root):1；_governance:60；contracts:13；evidence:6；openspec:2 | NO_RUNS |
| SBL / `evidence/r5-20261021-c5` | `4db3fc4dfe262bf56afa7eebfc737c65fc4b9a01` | `bedc11957d4fc2474b249b69d200829272c118ef` | (root):1；_governance:88；contracts:18；evidence:6；openspec:3 | NO_RUNS |
| SBL / `evidence/r6-20261021-c6` | `3d06f3da83488219a3dcdf608c937b8c5285810c` | `bedc11957d4fc2474b249b69d200829272c118ef` | (root):1；_governance:130；contracts:23；evidence:6；evidence_ledger:3；openspec:3 | NO_RUNS |
| PIPD-LS-SP / `chore/s4post-verification-harness` | `eea1543d5dc653b66431b9aac396fb635c39c8b7` | `9863c5552190c4100837df7c7dcd182229346d47` | .github:1；.hgk:70；(root):1；openspec:1；packaging:3 | offline-gate:success |
| PIPD-LS-SP / `docs/preview4-sums-count-truthfulness-20261014` | `4b918b2ba013c00b3b7af76d8e0d13246736b7fc` | `4b918b2ba013c00b3b7af76d8e0d13246736b7fc` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `docs/r5r3-asset-reproducibility-readback` | `97a01dab95bc53a08b8c372e3c3b04e69a923d7d` | `97a01dab95bc53a08b8c372e3c3b04e69a923d7d` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `docs/repo-state-and-handover-refresh-20261016` | `196456106ece060e00aec37813d070c79ab36c0d` | `196456106ece060e00aec37813d070c79ab36c0d` | 無三點差異 | offline-gate:success |
| PIPD-LS-SP / `docs/three-install-routes-20261016` | `beb56501a18112dda6fcb8bbf8e61f4d2a6373dc` | `beb56501a18112dda6fcb8bbf8e61f4d2a6373dc` | 無三點差異 | offline-gate:failure |
| PIPD-LS-SP / `evidence/cnv-pipd-ls-sp-20261015-r6` | `d89e7f33ec14aa6fc14c35f3ad6c6202d7fc0d00` | `dba4b19456777d3b597fdf71480f6423dd974243` | EVIDENCE:567 | offline-gate:success |
| PIPD-LS-SP / `evidence/cnv-r7-0-validator-hardening-20261015` | `eae636d8668027887977a797b20e63899465ad8d` | `dba4b19456777d3b597fdf71480f6423dd974243` | evidence:16 | offline-gate:success |
| PIPD-LS-SP / `feat/s4post-triple-upgrade-20261012` | `38f9067d47162c9ecaaa34bb699fbecefb969301` | `c34c5a9f2d9c858c80beba43eca1547bf31af445` | .hgk:1；packaging:3；tools:3 | offline-gate:failure |
| PIPD-LS-SP / `feat/s4post-triple-upgrade-20261012-r2` | `d3bb4e92f00b256f1ba6abeaba7049113c00cedb` | `9863c5552190c4100837df7c7dcd182229346d47` | .github:1；.hgk:70；(root):1；openspec:1；packaging:3 | offline-gate:success |
| PIPD-LS-SP / `feat/s4post-triple-upgrade-20261013-r3` | `e71fee6dd3aa73724baec4e8d9cc72127fbe36ed` | `e71fee6dd3aa73724baec4e8d9cc72127fbe36ed` | 無三點差異 | offline-gate:success, verify:failure |
| PIPD-LS-SP / `feat/s4r3-stage-b-distribution-20261013` | `c52c219e9e17349e45fac924a4ea6149573e8627` | `517d7a5d3f00935e1589908f456dfacea8fd8a74` | .github:1；.hgk:41；(root):1；docs:4 | offline-gate:success |
| PIPD-LS-SP / `feat/s4r3-stageb-successor-20261013` | `940a37d00d5c1d12dfc9ae5d2325d8837b08501b` | `940a37d00d5c1d12dfc9ae5d2325d8837b08501b` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `feat/s4r5x-manifest-fit-20261014` | `e00ab7b68c914c9a531beb9b5cb6e5ebbd794277` | `e00ab7b68c914c9a531beb9b5cb6e5ebbd794277` | 無三點差異 | offline-gate:success |
| PIPD-LS-SP / `feat/s4r5y-plugin-publication-20261014` | `062d84ae3e951d02b2ba6bb732359b18799d2864` | `062d84ae3e951d02b2ba6bb732359b18799d2864` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `feat/s4r5z-evidence-readme-20261014` | `51bd8e5fc1127d3ebfbece606da5573daf9ab3f6` | `062d84ae3e951d02b2ba6bb732359b18799d2864` | .hgk:126；PIPD_S4_R4_EVIDENCE_RETURN:3；PIPD_S4_R5Y_GPT_PLUGIN_EVIDENCE_RETURN:78；(root):1 | offline-gate:success, verify:failure |
| PIPD-LS-SP / `feat/s4r5z-readme-plugin-route-20261014` | `96434958171ff31ebb982733f898b9c9e9c75c0b` | `96434958171ff31ebb982733f898b9c9e9c75c0b` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `feat/s4r7-main-upgrade-and-repo-state-20261014` | `6dc5ec22d003cb8e8c885df82fb1aa0d16da9852` | `6dc5ec22d003cb8e8c885df82fb1aa0d16da9852` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `fix/r5r2-segment-and-boundary-20261014` | `749dc322dbdef4a0bc17f7dc5abf6c19e0231ed7` | `749dc322dbdef4a0bc17f7dc5abf6c19e0231ed7` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `fix/r5r3-preview4-identity-and-route` | `4cbb22fc9be3c9b91840aacef90da754d3d7414d` | `4cbb22fc9be3c9b91840aacef90da754d3d7414d` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `fix/s4-external-challenge-20261012-r1-provenance-trace` | `eef951acdfe0e2b4d93dde7732d264441d9bd674` | `0a05f4fde899d5990a8c098e3feaa2d9d1d7e0de` | .hgk:135；(root):1；dist:11；docs:3；examples:2；openspec:4；schemas:2；src:2；tests:9；tools:5 | NO_RUNS |
| PIPD-LS-SP / `fix/s4post-far-adjudication-20261012` | `ad33c0c679ac329a38cb9b0c0127a51211e3e09e` | `f3c80ec5f97fd6163192491efaae184a773b421c` | .hgk:12；docs:1；tests:2；tools:2 | offline-gate:failure |
| PIPD-LS-SP / `fix/s4post-integration-repair-20261012` | `52542c395a0f91dc2ba4bd6123acd4cdecd780dc` | `52542c395a0f91dc2ba4bd6123acd4cdecd780dc` | 無三點差異 | offline-gate:failure |
| PIPD-LS-SP / `fix/s4r3-stage-a-ci-truthfulness-20261013` | `759b9f0dc880b2f960363b2ceaa68446c770061d` | `759b9f0dc880b2f960363b2ceaa68446c770061d` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `fix/s4r5r-d1d2-claimceiling-preview4-20261014` | `5219dc7e4f9d96701326e864b694658e3601a3b3` | `5219dc7e4f9d96701326e864b694658e3601a3b3` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `fix/s4r6-closeout-doc-identity-and-update-route-20261016` | `c17aa761b26033fc0a2a2aa3df5ad0f61f2e5a20` | `c17aa761b26033fc0a2a2aa3df5ad0f61f2e5a20` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `fix/s4r7-readme-main-sha-truthfulness-20261014` | `7f126aa1133cc899791812a582abad6c9d09e8a8` | `7f126aa1133cc899791812a582abad6c9d09e8a8` | 無三點差異 | offline-gate:success, verify:success |
| PIPD-LS-SP / `r5-s4-evidence` | `2ad1f16bf44eb14868eaac6dfa764516490de27c` | `5094939606ba9331ed768743eb5b806ad159e639` | .hgk:2 | NO_RUNS |
| PIPD-LS-SP / `r5-s4-readme` | `f418153aac2cf7e5a4080d6412f8fe15ffca34b6` | `5094939606ba9331ed768743eb5b806ad159e639` | (root):1 | NO_RUNS |
| PIPD-LS-SP / `r5r-evidence-return-20261014` | `fb6e835d3539840a8d90e609a660dcd07e1c0acd` | `cc6c1930765160697e7e51d6e37735b9220a30db` | PIPD_S4_R5R_PREVIEW4_EVIDENCE_RETURN:47；PIPD_S4_R5S_PREVIEW4_VERIFY_CLOSE:38 | offline-gate:success |
| PIPD-LS-SP / `r5r3-closeout-evidence-20261016` | `1000fe25f478a5df651856cc93b2a254c155f6b8` | `d3bd5456afbff21a8c8837994a49f57be3e1b97e` | (root):1；R5R3_PREVIEW4_CLOSEOUT_20261016:111 | offline-gate:success |
| PIPD-LS-SP / `r5r3-evidence-return-20261016` | `728849b20dedea7cad3964ebe09436463abb90c5` | `dba4b19456777d3b597fdf71480f6423dd974243` | R5R3_PREVIEW4_EVIDENCE_RETURN:77；openspec:3 | offline-gate:success |
| PIPD-LS-SP / `r5z-evidence-return-20261014` | `a0882fd721f8e48d8818a07ad3f2cbf6cf140f34` | `062d84ae3e951d02b2ba6bb732359b18799d2864` | .hgk:194；PIPD_S4_R4_EVIDENCE_RETURN:3；PIPD_S4_R5Y_GPT_PLUGIN_EVIDENCE_RETURN:78；PIPD_S4_R5Z_SESSION_CONFORMANCE_RETURN:39；PIPD_S4_R6_FAR_AND_ALIGNMENT_RETURN:35；PIPD_S4_R7_RETURN:18；(root):1 | offline-gate:success |
| PIPD-LS-SP / `r6-closeout-evidence-20261016` | `71e70f747c30bcd42d407fd045261a9669345ddb` | `552bbde073806e254f84e95039f05c9767608aa1` | (root):1；S4_R6_CLOSEOUT_RETURN:90；docs:1；far-r17:17；openspec:3；tests:1 | offline-gate:success |
| PIPD-LS-SP / `repo-hygiene-evidence-20261016` | `4435dab712bd04545c3a1f769fd5ce2a49ae0f54` | `552bbde073806e254f84e95039f05c9767608aa1` | (root):1；PIPD_REPO_HYGIENE_AND_HANDOVER_RETURN:16；S4_FINAL_PR18_EXECUTION_RETURN:14；S4_R6_CLOSEOUT_RETURN:90；docs:1；far-r17:17；openspec:3；tests:1 | offline-gate:success |
| PIPD-LS-SP / `s4-final-closeout-evidence-20261016` | `5750c6904ea6a12fde4a7ce56936d516f661c428` | `552bbde073806e254f84e95039f05c9767608aa1` | (root):1；S4_FINAL_PR18_EXECUTION_RETURN:14；S4_R6_CLOSEOUT_RETURN:90；docs:1；far-r17:17；openspec:3；tests:1 | offline-gate:success |
| PIPD-LS-SP / `s4-r2-affected-only-20261011` | `3f6c7dc52b73cfcba03dccbe576ade75bec1890d` | `3f6c7dc52b73cfcba03dccbe576ade75bec1890d` | 無三點差異 | NO_RUNS |
| PIPD-LS-SP / `unmerged-merge-evidence-20261016` | `8cbf856e7f3849085429cf4b5627b55ff0b006ca` | `552bbde073806e254f84e95039f05c9767608aa1` | (root):1；PIPD_REPO_HYGIENE_AND_HANDOVER_RETURN:16；PIPD_UNMERGED_CANDIDATE_MERGE_RETURN:12；S4_FINAL_PR18_EXECUTION_RETURN:14；S4_R6_CLOSEOUT_RETURN:90；docs:1；far-r17:17；openspec:3；tests:1 | offline-gate:success |

## EVIDENCE-ONLY 理由分類

1. **SBL 治理與驗收支線不是產品增量。** `evidence/r6-20261021-c6` 的三點差異為 166 檔、+42,672/−4；top-level 為 `_governance` 130、`contracts` 23、`evidence` 6、`evidence_ledger` 3、`openspec` 3、root 1，沒有 `sbl_core`、`sbl_sp`、`sbl_stack` 或 `sbl_harness` 產品程式變更。c3→c4→c5→c6 是 ancestry 證據鏈，不是已併 main 的產品鏈。保留證據 SHA 與查閱入口，不應為了讓報告出現在 main 而整枝併入。
2. **PIPD 的 CNV 分支是封包，不是已安裝的 validator 修復。** `evidence/cnv-pipd-ls-sp-20261015-r6` 全部 567 檔在 `EVIDENCE/`；`evidence/cnv-r7-0-validator-hardening-20261015` 全部 16 檔在 `evidence/`，包括 `R7_VALIDATOR_DIFF.patch`。patch 以文件存在，不等於對產品程式已套用；兩者 CI 成功均不足以改判 MERGE_NOW。PR#14、#15 目前仍 open。
3. **歷史 evidence-return 不自動成為 release 所需內容。** `r5r-evidence-return-20261014` 的 85 檔分布在 `PIPD_S4_R5R_PREVIEW4_EVIDENCE_RETURN/` 47 與 `PIPD_S4_R5S_PREVIEW4_VERIFY_CLOSE/` 38；`r5r3-evidence-return-20261016` 的 80 檔為 return 77 與 openspec 3。這些適合用固定 SHA 作外部證據，不需搬進產品主線。
4. **名稱是 evidence 不代表沒有產品副作用。** `r5r3-closeout-evidence-20261016` 的 112 檔中 111 檔是 closeout 封包，但另一檔 `.gitattributes` 將三行 `* text=auto eol=lf`、`*.png binary`、`*.db binary` 改成一行 `* -text`。這是整個 repo 的文字處理政策變更；即使 merge-tree exit 0，也不應偽裝成純證據併入。
5. **混有產品或文件的證據鏈須拆分。** `r6-closeout-evidence-20261016` 及其三個後繼分支均與 main 的 `tests/test_r6_doc_identity_guard.py` 發生 add/add 衝突，並帶有 `docs/install/README.md` 增量；`r5z-evidence-return-20261014` 帶回 README 衝突。應保留封包並另開必要的最小修補，不能一律用 theirs 消衝突。

### PIPD-LS-SP 官方八個 skills：main 實際內容

固定主線 `e95942abcb6aa07e69304607ab8afc22a74fc67d`；以下八個均存在於 `skills/<名稱>/SKILL.md`，各自宣告 version 1，並引用 input/output schemas、contract、examples、cases。完整原文已保存於 `skills-main.json`；這裡是契約摘要，不是執行成功宣告。

| skill | main 上的實際契約內容 |
|---|---|
| `pipd-route-intake` | 接收 goal 與 source locators；拒絕空 goal、零 locators 與越界路徑；抽取 requirement atoms，產生內容定址 IntentCard，交給 PI compiler。 |
| `pipd-authority-source` | 以 sha256、文件 locators 固定 source families；F1/F2/F3/F5/F6 為 R1，其餘 R2；產生 AuthorityBinding 與 SourceFreezeManifest，拒絕衝突或非 CURRENT 來源。 |
| `pipd-profile-tailor` | 僅允許 LITE/STANDARD/ASSURED 與九個 canonical axes；拒絕未知或重複 axes；safety veto 只能升級；provider-off parity 可將 LITE 升 STANDARD，axis ceilings 為 3/6/10。 |
| `pipd-pi-compile` | 要求 frozen IntentCard、effective profile、非零 atoms；每個 atom 必含 source_clause/owner/acceptance_cue/risk_guard；acceptance 綁定 DOC-03 DOMAIN_ORACLES；生成 TraceLinks 並拒絕未宣告 sidecar keys。 |
| `pipd-pd-bind` | 要求真實 RepoContext 的 root/head/tracked_files/currentness/writable_scope；拒絕空或越界 scope 與 `**`；保留實際 FRESH/STALE；PD late binding 的 scope 是 affected_only。 |
| `pipd-execution-contract` | PD/PI references 轉成 ConstructionContract 與 ECP；明示 changes/tests/rollback/evidence；permission 需 token、at-most-once、residue-scan readback、必備 rollback；retry max 1/backoff none。 |
| `pipd-assurance-tqaep` | maker 與 checker 必須不同，含忽略大小寫／空白比較；拒絕缺失或 SELF_ATTESTED checker receipt；要求 trace links；逐 atom 產生 oracle、正負 fixtures、evidence expectation。 |
| `pipd-package-project` | 要求非空 artifact bundle、allowed claims 與 producer；僅允許八階 claim ladder；LOCAL_QUALIFIED 以上需 approval receipt 與獨立 checker；重算 trace closure，拒絕 orphan/hash mismatch。 |

## DO_NOT_MERGE 風險清單

- **`fix/s4-external-challenge-20261012-r1-provenance-trace`：release 身分與既有 bytes 衝突。** `merge-tree` exit 1，衝突包括 `dist/mount/pipd-ls-sp-s4-chatgpt-mount-v0.1.1-preview.3/MANIFEST.sha256`、`SKILL.md`、quickstart、README、五個 references，以及 `docs/RELEASE_TUPLE.json` 與 preview.3 erratum。main 的 tuple 目前記載 preview.3 曾 in-place 替換及 preview.4 的獨立 tag/build-source/asset identities；舊支線整檔取 theirs 會覆寫這些後續記錄。這裡只驗證 Git blobs 與 tuple 內容，沒有重新下載 release assets 斷言 bytes 一致。
- **`feat/s4r3-stage-b-distribution-20261013`：舊交付控制面衝突。** 六個衝突路徑包含 `.github/workflows/public-plugin-verify.yml`、`README.md`、`docs/USER_GUIDE.md`、R3 finding ledger、RAW_INDEX 與 index builder；不能以單一 offline-gate success 遮蔽衝突，也不能直接宣稱其所有 17 個獨有提交均被 successor 替代，因 `git cherry main head` 全部是 `+`。
- **`r5-s4-readme`：過時安裝說明衝突。** 只改 README（+217/−71），但與 main 分岔後落後 264 個提交，實測 README content conflict，head 沒有 check-runs；不得拿舊說明覆蓋主線。
- **另外三個 NOT_RECOMMENDED 的具體阻擋。** `chore/s4post-verification-harness` 與 `feat/s4post-triple-upgrade-20261012-r2` 分別已有 17/18、16/17 個非 merge patch 在 main 等價出現，但各剩一個非等價 CI patch，整枝仍造成 README 及七個治理檔衝突；應只評估剩餘 CI 差異。`fix/s4post-far-adjudication-20261012` 雖 merge-tree exit 0，但 head `offline-gate=failure`，同時變更 `tools/verify_evidence_digests.py`、新增 eligibility probe 與測試，且夾帶 26,154、1,569、18,160 行的三份 writer logs，不能直接放行。
- **SUPERSEDED 也不表示可以放心重併。** `feat/s4post-triple-upgrade-20261012` 的唯一 patch 在 main 等價存在（git cherry 顯示 `- 38f9067...`），但仍對 plugin/derivations 與兩個 builder 產生 add/add 衝突。正確動作是不併，不是「修完衝突再重併」。

## 建議執行順序

1. **重新凍結 SHA 與 owner admission。** 真正執行前重讀兩 repo 的 `ls-remote --heads`、PR#2 head/base；若不再是 SBL main=`bedc11957d4fc2474b249b69d200829272c118ef`、head=`a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2`，本裁決須重測。讀 branch protection／required checks；本次 protection API 為 403，不能推定未受保護。
2. **唯一整枝推薦：SBL PR#2。** Owner 以受保護 PR 流程併入 `candidate/c3-20261021-v2`；不先併 v1、不併 evidence 支線、不 force push。Gate：merge-base 與 main 相同、ahead/behind 6/0、27 檔 +2,576/−63、merge-tree exit 0、Ubuntu/Windows Python 3.11 head checks 均 completed/success，並確認 PR 核准與 required checks 無缺漏。
3. **PR#2 本輪可重現 gate。** 在 scratch detached HEAD 重跑：`python -m pytest -p no:cacheprovider -rs` → exit 0、191 passed/3 skipped；`python tools/check_wheel_contents.py` → exit 0、wheel 39 members、八個 required runtime data 路徑全部 OK；`python tools/verify_source.py --self-check` → exit 0、14-doc manifest 自洽，但沒有 corpus byte verification。若 owner 要求所有測試不得 skip，需在可建 symlink 且有 jsonschema 的環境補跑；禁止把 skip 算 PASS。
4. **併入後回讀，而非只相信按鈕。** 檢查 PR merged 狀態、main 新 SHA 及候選 SHA ancestry（採 merge commit 時）；若採 squash，則比較預期合併 tree 與實際 tree，不能用 ancestry 假裝能驗證 squash。重跑 main CI、wheel runtime data 與 source manifest gate；不因此把 `PACKAGED_HOST_PENDING`、`PARTIAL_CHALLENGE` 或 `FAIL_FULL_CONTRACT` 自動升級。
5. **PIPD 現階段不推薦任何整枝 merge。** 對已併 ancestry 分支或全部 patch-equivalent 分支不做重複併入；保留 evidence SHA。若要救回 NOT_RECOMMENDED 的一個 CI patch或 FAR validator 修補，從當時最新 main 建立新的最小 scoped PR，而非重用舊分支；先檢視 main 已有相同行為與 mutation fixtures，再補 head CI 與 integration merge-tree；required gates 未全過不得合併。
6. **release 與治理資料另案。** 對 preview.3/preview.4 的 tag、asset name、digest、tuple 變更需獨立 Release Owner admission 與下載 bytes 重算；不得移動既有 tag、覆蓋 release asset 或把歷史 tuple 重寫成目前 main 的身分。純證據只用固定 SHA 引用；確有主線文件需求時另做窄版索引 PR。

## 限制

- 本輪完成 SBL 12、PIPD-LS-SP 37 個非 main 遠端分支，共 49 個；遠端含 main 分別為 13、38 個。原先「約 37 分支」不是 37 個含 main 的上限。本輪覆核 `ls-remote` 與開始快照相同。
- 使用隔離 bare clones、scratch detached checkout 與 GitHub REST GET；沒有 push、merge、tag、release，也未變更原 SBL 工作樹或原有分支。初讀原工作樹已有 `?? _governance/round-20261021-r7/`；末讀另見 `?? openspec/changes/sbl-v01-candidate-build/R7_DELTA.md`，顯示有本子任務以外的並行寫入，不能宣稱整個工作樹狀態完全不變。本子任務只寫 scratch，未碰觸這些檔案。
- 統計定義是 `git diff --stat main...head` 與 `--numstat`（merge-base→候選的三點差異）；`ahead/behind` 是候選/main 的獨有提交數。檔案數包含 binary，但 +/− 只計文字行，binary 的 `-` 不當作零內容。已併祖先顯示 0 檔，是無候選增量，不是與 main tip bytes 完全相同；另存 `main_tip_stat`。
- `git merge-tree --write-tree main head` 僅寫 scratch object database、不建 merge commit、不改 refs/index/工作樹；exit 0 為無衝突、1 為有衝突，不是功能驗收通過。方法依 Git 官方文件；patch 等價依 `git cherry`，不是僅憑分支名稱判斷。
- 無 gh CLI；以 token-authenticated urllib 讀取各 head SHA 的 statuses、check-runs、Actions runs，無 API 錯誤或達到 100 筆分頁上限。表內 CI 保留可見 check 名稱及 conclusion；`NO_RUNS` 不是 PASS。legacy statuses 全為 pending/0，不把它誤當有工作執行中；以實際 check-runs 與 Actions conclusions 判讀。未下載完整 CI job logs，沒有假稱重跑所有 PIPD 測試。
- `/rules/branches/main` 對兩 repo 回傳空陣列，但 `/branches/main/protection` 皆 HTTP 403；required checks／review protection 完整狀態為 NOT_VERIFIED，而非「沒有規則」。
- SBL 三個 skip：兩個需要 Windows symlink 權限，一個缺 jsonschema。初次 archive-only 測試因缺 Git metadata 失敗，加入 scratch detached Git metadata 後通過；wheel 初次遇 Windows 長路徑，再跑遇殘留 build directory，改用全新 scratch source 與 extended-length TEMP 後通過。初次失敗及成功重跑均保留，未以編造結果取代。
- 八個 PIPD skills 的存在及文本已逐一讀取；未宣稱八個技能在本主機已實際載入／獨立驗收／端到端執行成功。未把 2026-10-16 舊 FAR 裁決當成本輪 Git 證據。
- 原始證據、精確 SHA、每分支 merge-base、top-level 分布及 conflict paths：`audit.json`、`MEASUREMENTS.md`；技能全文：`skills-main.json`；PR/protection readbacks：`remote-gates.json`；本機測試：`sbl-gates.json`、`wheel-fresh-extended-path.json`。都在同一 scratch 目錄，另有重現腳本與失敗紀錄。
