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

---

## 已在本回合關閉的 Owner 項目（不再是待決）

### CLOSED-OWNER-A — 車道模型綁定（回合中指示，2026-10-21）
**指示**：PLAN 執行模型與 VERIFY/SECURITY checker 模型改為 `minimax-m3.1-flash-free`（opencode-go）；
EXECUTE 未提及。

**已執行**：
- `HG-KSEOS/config/lane-route-slots.candidate.json` revision 11（commit `3f81b4b7d32da0f9eaae01c7ecd05728206f33d9`）
  的 rank-1 改為 `opencode-go/minimax-m3.1-flash-free`（PLAN、VERIFY_SECURITY）；
  `openai-codex/gpt-6.1-sol` 降為 rank-2 fallback（**未移除**）。
- **在 canonical pool 上實測**（非 bounded probe pool）：兩條車道皆
  `served_arm == required_arm`、`nonce_present=true`、`usage HTTP 200`、`exit=0`。

**已釐清的歧義**：並行程序曾寫入另一版本（EXECUTE rank-1 也改為 minimax）並留下 merge 衝突與 stash。
已向 Owner 確認 → **EXECUTE 維持 `deepseek-v4.1-flash`**；工作樹還原為受裁決的 revision 11，
stash **丟棄而非套用**，工作樹乾淨、stash 清單為空。

**已揭露的限制**：HG-KSEOS **沒有 git remote**，此綁定僅存在本機 commit，未發布到任何 GitHub repo。
外部驗收官可由本 repo 的 `40_VERIFY/lane_rebind_minimax/` 查驗量測，但看不到該 commit 本身。

**已記錄的衝突**：planner 與 checker 現為**同一身分**。dispatcher 不執行 maker==checker REFUSE（D1），
故這是「已記錄的重疊」而非「被阻擋」——**checker 不再對 planner 提供模型軸上的獨立性**。
這是該指示的直接後果，已寫入 pool 的 `identity_overlaps_recorded_not_enforced` 與 R7 status。

---

## OWNER-4 — 是否將 R7 的可重現建置修復併入 main（PR #3）

**對象**：`candidate/r7-20261021-repro-build` @ `59d2138750223b325159fab536f218a0d9aa4ab5`，
相對 `a6bcdd0`（PR #2 的 head）多 3 個 commit、4 個檔案：
`.gitattributes`、`tools/build_reproducible.py`、`tests/test_reproducible_build.py`、
`tests/test_repro_mutation_probe.py`。

**依據**：本回合已關閉 `TT-R6-WHEEL-NONREPRODUCIBLE-001`。獨立 checker 第一輪實機找到**兩個真缺陷**
（F8 測試只斷言原始碼文字，2/3 的合約破壞變異仍全過；F9 建置依賴 ambient interpreter 的 `build` 套件），
兩者皆已在 `59d2138` 修復並以 mutation probe 保護。量測：`identical=true`、`single_member_timestamp=true`、
202 passed / 2 skipped。

**預設值**：**先合併 PR #2，再以 `a6bcdd0` 為 base 開 PR #3 併入此修復**，理由：
PR #2 的 head 是 R6 報告引用的受審物件，直接改它會使報告引用的 SHA 失效。

**機械步驟**：
```bash
# 0) 遠端新鮮度檢查
git ls-remote origin refs/heads/main refs/heads/candidate/c3-20261021-v2 refs/heads/candidate/r7-20261021-repro-build
# 1) 合併 PR #2（見 OWNER-1）後，main == a6bcdd0
# 2) 以 main 為 base 開 PR #3，head = candidate/r7-20261021-repro-build
# 3) CI 需在雙 OS 上重跑（新增的 mutation probe 會在 CI 上實際破壞機制並斷言測試變紅）
```

**不做會怎樣**：可重現建置能力只存在於候選分支；後續 C3 prerelease 的資產 digest 無法被第三方重現，
OWNER-2 的發布前提（`receipt.verify.identical == true`）在 main 上無法成立。

**前置條件**：本回合的獨立 VERIFY 第二輪（arm `opencode-go/minimax-m3.1-flash-free`，
nonce `R7CHK-NC-20261021-A2`）必須先產出裁決。該裁決尚未產出時，PR #3 應等待而非先行。

---

## OWNER-5 — 決定 4 個 contract capability 的 binding 修復時機

**對象**：`SBL/contracts/SBL_C0_C9_CONTRACT-R6.json` 中 4 個 capability，其 acceptance 指向
`ACC-SBL_SHARED_CORE`，但各自另有專屬 acceptance ID。

**依據**：本回合逐項交叉比對 34 條 acceptance edge 後確認為**真實 binding defect**，非命名慣例。
compiler 位於知識庫唯讀 SSOT（`…/Semantic World OS Fabric/SBL`），本回合未修改。

**預設值**：在**下一個 contract 回合**（R8）修復，並在該回合重建 contract receipt。
不在本回合改，因為 R6/R7 的報告都引用了現有 contract 的編譯收據，改動會使那些引用失效。

**機械步驟**：在 R8 回合內，改 compiler SSOT 中這 4 個 capability 的 acceptance 指向，
重建 `SBL_C0_C9_CONTRACT-R7.json`，重跑 lint / activation / acceptance / compile 四道閘門，
並保留新舊兩份 receipt 供比對。

**不做會怎樣**：契約圖中 4 個 capability 實際驗證的是 shared core 的 acceptance，
其專屬 acceptance 形同未被檢查——契約宣稱的覆蓋率高於實際覆蓋率。
