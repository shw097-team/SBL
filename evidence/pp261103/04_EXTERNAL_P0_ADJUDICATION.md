# PRE-V2 TPM：PR #25 證據解讀與前置退出判準勘誤（2026-11-03）

> 工程鑑定備註；不改寫 PR #18/#25 歷史證據、不授予 Native 效果或主用資格、不修改 rc.2 ZIP/Runtime。
> **既有正式結論維持 `PRE_V2_CLOSEOUT=NO`**。本註記只校正部分 P0 計數、錯置的解除條件和 GitHub 路由，避免前置修補被下游 Native 驗收不當卡住。

## 上位規範與新 GitHub 路由

- 唯一前置施工/退出依據：《`sbl-tpm-sp_前置修補藍圖`》r2，`SBL-TPM-SP-PRE-V2-BLUEPRINT/2026-11-02-r2-SUBSTANTIVE`（SHA256 `e985b8859c2e0841548737e0bb83e5204e043584f0db8af201e8ae2388ec2719`）的 CT-00～05、§6.2 十個適用 P0 與安全負例不退化。
- 前置合格之後**才**以合格 TPM 生成 `FHS_PIPD-LS-PKG_v2`；FHS 22 WP、Native W0～W3、正式 Protected Checker/Publisher 不屬本輪 TPM 前置結案必要條件。
- Fabric `INTEGRATION/FHS/repository-map.json` 的 `FHS-NAV/v2` 是**只讀導航**，`effect_permission=NONE`；`sbl_product` 和 `pipd_canonical` 的工程主 Repo 均為 SBL。PIPD-LS-SP GitHub `archived=true`、`write_authority=NONE`，僅供歷史參考。跨 Repo 先讀 Fabric 入口，真正寫入依原 Domain Owner 及各 Repo 分別受影 PR；不得因導航存在就推到 Fabric/PIPD 或取得 HGK Grant。

## PR #25 與前輪的可重用實證

- SBL PR #25 已合併，`main=cf8859aea56198c3d8ce87eb4d5cc794f27b7486`，MAIN CI `41562534208`（Ubuntu、Windows、PIPD Compat）成功；PR #25 為**證據增量，非程式修復**。
- rc.2 封存 SHA256 `3a9da65561ab19cad90a6d7cbfb2eae0abf59b87ba565a118790bce5612326a8`，173 files／14 Skills；ZIP 與隔離 Installed Copy 一致，不能宣稱已完成真 Loaded/Used。
- 當期 Canonical PIPD Writer/Reader 在 SBL `integrations/pipd/`（0.1.1a5）；13 CLI／19 Family；原 Writer 四件 `validate --require-four` 正例和錯 Schema 負例已在 SBL 受影重驗。作者 `@2` Sidecar 不等同 Canonical ACK。

## 必須修正的證據解讀（不額外創設 Gate）

1. **P0 計數**：`01_ACCEPTANCE.md` 逐列有五個明寫 PASS（LIFECYCLE、PI_ID、PD_REALITY、COMPATIBILITY、AUTHOR_TESTS［部分］），五個明寫 HOLD；總計卻寫 `PASS 4/HOLD 6`。若 `AUTHOR_TESTS` 僅有五個新負例、不能以可信歷史 RawRef 覆蓋原 §6.1 適用 24 Topic，應在正式總計將該項列 HOLD／證據不足，才會是 4/6；或提供已有、可釘版本的 RawRef 再更新。**不強制重跑完整 664 件**。
2. **P0_TQAEP_FUO**：原 CT-04 明定 `Runner unbound → Design okay, Qualified HOLD`。前置 P0 要的是 Required Case／原 Oracle／FUO／Runner 狀態和適用來源的**設計級實質關聯**；不得因 `TQAEP_DESIGNED / NOT_GRANTED`、`RUNNER_UNBOUND`、缺 Live Checker Receipt **單獨**判前置 FAIL/HOLD。現有兩 Case／FUO 帶作者派生身份，原 Case/Oracle/FUO 的來源權威未充分釘定，故仍可依此真正差額 HOLD；**解除不以 Native Checker 執行為前提**。
3. **P0_HOST_INVOKE**：原 §6.2 要 Fresh Codex `Installed→Loaded→Invoked/Used` 與 Nontrigger，不要 HGK `work_id`、Preimage/Postimage、Protected Checker 或 Native Grant。作者 Gate 的 `host_invoked=NOT_RUN` 與 `native_e2e=NOT_RUN` **不能單獨否定 Codex Skill 的 Host 使用**。
4. **rc.2 Host 歷史說法衝突**：`evidence/pre-primary-20261102/RUN-20261102-GJ02-01/04_closeout.md`、`02_checkrun.json` 及 PR #18 **記載** 0.3.0-rc.2 的真 Codex 會話、工具使用與 3 SPEC，部分成功依賴一次隔離 `danger-full-access` 診斷；PR #25 則依 `HOST_ACTUAL_USED.json` 的舊 `NOT_RUN` 以及缺新 Host 事件，稱 rc.2「從未執行」。兩者矛盾，公開 GitHub `raw/EVENTS_OMITTED.json` 又說完整事件 JSONL 留本地。**可證的是 Installed/Enabled 和先前聲稱的 Host 會話，尚不足以獨立釘定同一 rc.2 ZIP→Loaded→Invoked/Used 的完整身分鏈；不可絕對宣稱「從未執行」，也不可在缺 Raw 時直接判 Host PASS**。需要時只做一筆符合原限制的 Fresh Host/Skill 顯式＋普通 Goal/Nontrigger 受影確認。
5. **P0_SOURCE_BASELINE**：來源、Manifest、Skill 身分與原 Source Pointer 由其本身證據評定；`Loaded/Used` 應歸入 `P0_HOST_INVOKE`，不可重複當作 Source 基線失敗的充分原因。原來源 `ORIGINAL_OWNER_UNVERIFIED` 如果確實影響本次 Scope，才以其本身權威差額另記。
6. **P0_AUTHOR_TESTS**：本輪五個具名安全負例確有 `5 passed`，但不等於原 24 Topic 全部可宣 PASS；過去 `664 passed/20 skipped` 無保存 Raw，此數字不可當本輪獨立證據。對受影 Topic 重用 SHA/RepoHEAD 對得上的歷史測試與 MAIN CI，不重做無關套件。
7. **P0_ROLLBACK**：隔離 Repository 的 `git checkout -- .` 真實生效、Plugin 安裝/卸載/重裝存在清單；真 Host 重新載入舊版未證，故 Host 級回退仍 HOLD；不要求「原世界已生效的 Native Effect 可由 git rollback 撤銷」。

## 一次性 Owner 裁決／受影解除

**本輪正式驗收仍為 `PRE_V2_CLOSEOUT=NO`**，理由至少包括：原 Effect Authority/Consumer 接線未取得、rc.2 Host 適用受限模式的 Loaded/Used 身分尚未充分釘定、Host 級重載回退未證；Case/Oracle/FUO 及 Author Topics 則按原 P0 **以實際適用來源與可重用 Raw**補判，不能額外要求 Live Checker。

- **SBL 原 Product＋PIPD Compiler Owner／HGK Effect Owner**：在 SBL canonical `integrations/pipd` 與原 Reader/Consumer 建立**最小、版本化、受權的 Operation→Effect 接線**。現役 19-family 契約固定，不得逕加第 20 Family；不可借候選設計 Registry 自簽 Native Grant。
- **Hermes/Codex Host Owner**：以原政策允許的受限 Host（非永久 `danger-full-access`）完成**一筆** rc.2 Fresh Loaded/Used + Nontrigger，並在同一隔離環境重新載入舊版/回退讀回；已錄下的可重用證據不得重跑。若模型憑證讀取的明確工具審批拒絕，合法停在 HOLD，不以 Owner 一般授權繞過。
- **適用 PI／Case Reader 與作者測試**：只補真正未證的原 ID／Case／FUO 設計關聯和受影 Topic Raw；禁止把 282 Native Cases、Live Checker、FHS v2 主產包生產列為 PRE-V2 結案先決條件。

全部適用 P0 與安全負例在**原標準**內 PASS 才宣布前置結案；若原 Owner/Host 不可合法接線，保持 NO 並停止本輪，不將其包裝成下一個新專案。

## 參照

- Fabric：`INTEGRATION/FHS/{README.md,repository-map.json,AGENTS.md}`、`AGENTS.md`（FHS-NAV/v2／導航不授權）。
- SBL：`evidence/pp261103/{01_ACCEPTANCE.md,02_HOST_ROLLBACK.md,p0/PRECHECK.md,samples/EVIDENCE_MAP.md}`；`evidence/pre-primary-20261102/RUN-20261102-GJ02-01/{04_closeout.md,02_checkrun.json,raw/EVENTS_OMITTED.json}`。
- 本註記為**針對公開證據的工程裁定**，不聲稱已獨立讀取本地私人 Host JSONL／Owner 密鑰。
