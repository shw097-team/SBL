# Owner Decisions — R7 (SBL-R7-FAR-RESIDUAL-CLOSURE)

> 這些是 FAR 裁決後，**每一項都只需 Owner 一次動作**即可關閉的項目。
> 每項都有：依據、預設值、理由、機械可執行的步驟、以及「不做會怎樣」。
> 這不是待辦清單，是一張「按下按鈕」的清單。
>
> 產生依據：`Fabric/fabric-autonomous-research/runs/FAR-20261021-023-sbl-r7-residual-closure/ResearchHandoff.yaml`
> 與 `VERDICT.json`。裁決依據：上位 `SBL_PIPD-LS-PKG_DOC-00..13` + R6 獨立驗收報告主文。

---

## OWNER-1 — 合併 PR #2（scoped，非 force）

**對象**：`shw097-team/SBL` PR #2，head `a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2`，base `main`。

**依據**：R6 報告主文裁決 `RECOMMEND_MERGE_SCOPED_NOW`，並明載「本 Reviewer 未實際按下 merge」。
本回合量測：merge-tree exit 0（無衝突）、`main` 是 head 的祖先（可 fast-forward）、ahead/behind = 6/0、
27 檔 +2,576/−63、該 head 的雙 OS CI（`ubuntu-latest` / `windows-latest`, py3.11）皆 `success`。
49 個候選分支中，**只有這一個**被裁決為 `MERGE_NOW`。

**預設值**：`merge_method=merge`（非 squash），不刪分支。

**理由**：squash 會摧毀 R6 報告引用的 6 個受審 commit 身分（含三個 harness 卸載邊界修復），
並改變報告引用的 SHA。`merge` 保留受審物件圖，且分支仍可追溯。

**機械步驟**：
```bash
# 0) 新鮮度檢查（main 與 head 必須仍是下列 SHA，mergeable_state 必須是 clean）
git ls-remote origin refs/heads/main refs/heads/candidate/c3-20261021-v2
curl -s https://api.github.com/repos/shw097-team/SBL/pulls/2 | python -c "import sys,json;d=json.load(sys.stdin);print(d['mergeable_state'],d['head']['sha'],d['base']['sha'])"

# 1) 非 force 合併（帶 head SHA 防護）
curl -s -X POST https://api.github.com/repos/shw097-team/SBL/pulls/2/merge \
  -H "Authorization: Bearer $GH_TOKEN" -H "Content-Type: application/json" \
  -d '{"merge_method":"merge","sha":"a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2"}'

# 2) 遠端回讀
git ls-remote origin refs/heads/main   # 必須等於 a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2
```

**不做會怎樣**：PR #2 的 SP plugin 套件化與 harness 卸載邊界修復無法進入 main，後續 C3 prerelease 無基線。

---

## OWNER-2 — 發布 C3 experimental prerelease（0.1.1rc1）

**對象**：新版本 `0.1.1rc1`，tag `v0.1.1rc1`，asset 為新 build 的 wheel + sdist。

**依據**：R6 報告裁決 `CONDITIONAL_PREVIEW`（merge 後用新 SHA 建 wheel/sdist、clean venv 試用/卸載、
版本與 scope 不混用 0.1.0 既有 bytes，再公開 prerelease；未完成前不得稱已發布）。
本回合已備妥：9 步執行方案、每步 gate、失敗處置、rollback、紅線（`ResearchHandoff.yaml`）。

**預設值**：版本 `0.1.1rc1`、tag `v0.1.1rc1`、先建 **draft** 再公開、
`merge_method=merge`、發布前逐項回讀 asset digest。

**理由**：
- 不可沿用 `0.1.0`：已發布的 `v0.1.0-foundation-preview` 有自己的 digests，沿用會使新舊 bytes 無法區分，
  並改寫已成立的 release 身分。
- 為何先 draft：draft 可在公開前刪除，公開後就必須走撤回或缺陷公告流程。
- 為何用可重現建置：本回合已關閉 wheel 非可重現性，發布資產的 digest 因此可被第三方重現與比對。

**機械步驟**（完整 9 步見 `ResearchHandoff.yaml`）：
```bash
# 3) 在合併後的 main 上切新分支，改 version = 0.1.1rc1
# 4) 可重現建置 + 自驗
python tools/build_reproducible.py --commit <new-sha> --outdir dist --verify --json-out receipt.json
#    判據：receipt.verify.identical == true 且 single_member_timestamp == true
# 5) clean venv 生命週期：install → 執行每個 entry point → uninstall → 殘留必須為 []
# 6) 記錄 wheel/sdist sha256、source commit、lifecycle 結果
# 7) 建 DRAFT release，上傳資產，GET 回讀並逐項比對 digest
# 8) PATCH draft=false（僅在 1-7 全通過且 Owner 明確核准後）
```

**不做會怎樣**：產品變更無法對外提供可驗收的發行物；外部驗收官只能看候選分支，無安裝載體。

---

## OWNER-3 — 裁定 plugin schema 的權威文件

**對象**：`CR-PLUGIN-SCHEMA-AUTHORITY`（R6 遺留，OPEN）。

**預設值**：**DOC-12 是 plugin schema 的權威文件**。

**理由**：三個 `SP_PLUGIN_PACKAGE_*` capability 的 acceptance 指向 `DOC-12#C-001..C-003`，
`SP_HOST_INSTALL_REQUEST` 指向 `DOC-12#C-016..C-018`；DOC-12 的 surface ledger 是唯一擁有這些
plugin 條目的 DOC。`ACC-PLUGIN-SCHEMA-AUTHORITY` 的 source locator 應改指 DOC-12。
（另見本回合量測到的 binding 缺陷：4 個 `runtime_readiness` capability 目前錯誤指向
`ACC-SBL_SHARED_CORE`，而 34 個 acceptance 其實各自都有對應 id，該修正屬下一個 contract 回合。）

**機械步驟**：在下一個 contract 回合把 `ACC-PLUGIN-SCHEMA-AUTHORITY` 的
`source_locators` 改為 `SBL_PIPD-LS-PKG_DOC-12#C-001`，並修正上述 4 個 capability 的
`acceptance_ids` 指向各自的 `ACC-SP_PLUGIN_PACKAGE_*` / `ACC-SP_HOST_INSTALL_REQUEST`。

**不做會怎樣**：plugin 驗收邊持續指向不相干的 acceptance 邊，runtime readiness 的 cell
可能被錯誤的驗收項滿足。

---

## OWNER-4 — 裁定 GPTB KnowledgePack R04 的 polarity

**對象**：`CR-GPTB-KP-R04-POLARITY`（R6 遺留，OPEN）。

**預設值**：**在擁有 R04 的 KnowledgePack corpus 內記錄該 polarity 裁決**，並在
`19_KP_INDEX_CROSSWALK` 建立對應條目。

**理由**：polarity 裁決屬於擁有該 KP 的 corpus；若只寫在本回合的證據檔，下一回合即失真。
（依 `00_KNOW_INDEX`～`19_KP_INDEX_CROSSWALK` 的既有結構，KP 裁決的落點是 corpus，不是 round evidence。）

**機械步驟**：在 KnowledgePack 的 R04 條目寫入 polarity 裁決 + 依據 locator，於 crosswalk 新增一列。

**不做會怎樣**：R04 的正反極性持續未定義，依賴它的能力無法取得可引用的裁決依據。

---

## 一句話版

| # | 項目 | 一次動作 | 不做的後果 |
|---|---|---|---|
| OWNER-1 | 合併 PR #2 | 點 merge（`merge_method=merge`） | 產品增量無法進 main |
| OWNER-2 | 發布 C3 prerelease | 核准 tag/version/scope，走 draft→publish | 無可安裝的發行物 |
| OWNER-3 | plugin schema 權威 | 宣告 DOC-12 | 驗收邊持續錯配 |
| OWNERER-4 | R04 polarity | 在 KP corpus 記錄 | R04 極性未定義 |

**仍然不能由本回合關閉的**（各自缺的是特定權限，不是「再努力一下」）：
`TT-CHALLENGE-BUNDLE-MISSING`（缺簽署的 challenge bundle）、`R6-TS12`（缺 Native issuer 的
WorkOrder/ONE ECP/Permit）、`R6-TS21`（3 個 ChatGPT 私人 Plugin，缺 Host 授權，0/3 不變）、
`R6-TS22-23-24`（38 surfaces 的 Host 證據，NOT_ADMITTED 仍是 NOT_ADMITTED）。
