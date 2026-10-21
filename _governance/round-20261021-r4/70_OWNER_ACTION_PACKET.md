# 70 — Owner action packet（R4）

本輪 owner 已授權兩件事：以 `DISCLOSED_DEVIATION` 跑 PLAN，以及「先 Docker 沙盒、PASS 後建 rollback
點、再在本機 Hermes 安裝測試」。以下動作**仍然只能由 owner 或另一個主體執行**，我沒有代做。

## A1 — 合併 c3 portable-manifest 修補

- candidate：`candidate/c3-20261021-v2` @ `68c276d354dae2b1bc2baef290f89e539fb34751`
- CI：run `39525131900`，ubuntu + windows 3.11 **2/2 success**，含新增的 `Wheel carries its runtime data`
- 基準：`bedc119`（`main`）
- 你要做的：開 PR（或直接對已存在的 PR 按 merge），**不要 force、不要 squash 掉 `68c276d`**
- 合併後 ceiling 只到 `PACKAGED_HOST_PENDING`；`INSTALLED` 屬於宿主側事實，不在這次合併裡

不可用 `39c604d` 取代：那份缺 `$schema`，且 wheel 沒有 `sbl_sp/manifests/*.json`。

## A2 — 三 SP 在 ChatGPT 私人外掛的 create / install / connect

我在這個環境沒有 Plugin Creator 的寫入通道，也沒有你的帳戶授權，所以這一步是 **HOST_PENDING**，
不是我漏做。你需要：

1. 三份 `_governance/round-20261021-r4/40_SP_PACKAGES/*.zip`
2. 分別建三個**不同** principal 的私人外掛（TPM / Commander / Challenge），不要用同一份複製三次
3. 記下宿主發的 plugin id、`@` 叫用的正例、一個越權反例、以及卸載後的 readback
4. 把四個欄位回填到 `20_TOOLS5_HARNESS_MATRIX.json` 對應列的 `host_issued_identity` / `uninstall`

在 `host_issued_identity` 有值之前，本輪對這三列的結論是：**已封裝、已在本機 Hermes 載入、未在
ChatGPT 上被接受**。

## A3 — SWOF PR #7 與 W1/W2

SBL 這一側只交付 `95_SWOF_W2_SHADOW_HANDOFF.json`。合併、驗收、W3 准入全部屬於 SWOF Owner 與
HGK native issuer。**不要**把 R9E 的 evidence-only PASS 當成整個 W2 的外部驗收。

## A4 — CR-PLUGIN-SCHEMA-AUTHORITY 的裁定

`CR_PLUGIN_SCHEMA_AUTHORITY.md` 有三個選項（B1/B2/B3）。在裁定前，三份套件的 ceiling 停在
`PACKAGED_HOST_PENDING`。這件事擋的是**跨宿主宣稱**，不擋 A1 的合併。

## A5 — 要不要留著本機安裝

依你的指示，五個工具目前**留在本機**：`HERMES_HOME/skills/sbl/` 下五個目錄，加上
`C:\Projects\Agent_Workspace\SBL-install\` 的 venv / stack / hgk-adapter。

回推點：`90_HERMES_ROLLBACK/skills-preinstall.tar.gz`（633 檔、58,542,537 B、sha256 `602b4f47…`）。
要回到安裝前：把該 tar 解回 `HERMES_HOME`，再刪掉 `skills/sbl`。`ROLLBACK_MANIFEST.json` 有逐檔
digest 可核對。
