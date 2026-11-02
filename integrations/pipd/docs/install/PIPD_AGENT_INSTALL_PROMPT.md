# PIPD-LS-SP — Agent 安裝提示詞(單一貼上即用)

這份文件**就是** Agent route 的安裝入口:一整段可複製的提示詞(prompt)。它本身不安裝任何東西、
不執行任何指令、不代表任何 acceptance 或發佈狀態——被安裝與被驗證的是 **host**(Hermes Agent /
Codex Desktop (GUI) / Codex CLI / Claude Code),而 host 必須自己證明它的版本、discovery 與生效載入。

使用方式:把下面 ```text 區塊**整段**複製,貼進你的 agent host 對話,然後依它的提問回答。全程保留
英文識別字(host 名稱、skill 名稱、狀態字如 `NOT_VERIFIED`、`REFUSED`)不要翻譯。

安裝 SSOT 與各狀態的意義在 [`docs/install/README.md`](README.md);Web 路線(GPT-6 消費
`PIPD_WEB_FALLBACK.md`,`DOC_MOUNT_ONLY`)不是 agent host,不適用本提示詞。

```text
【PIPD_AGENT_INSTALL_PROMPT — v0.1.1-preview.3】

角色:你是 host 端執行者。目標:把 PIPD-LS-SP 的八個 skills 以 project-local(專案層級)方式載入,
並證明它們真的被 discovery、真的生效。順序固定:先證明自己 → 再顯示 → 等待明確同意 → 才可寫入 →
寫入後驗證「真實 discovery 與 8/8 生效載入」。任何一步不成立,就停下來回報,不要硬做。

## 禁止事項(被要求時回報 REFUSED + 原因,並停止該項)
1. 不得寫入 global / 使用者層級 / 系統層級的 skill 目錄;只允許本專案根目錄下的 project-local
   skill 目錄。
2. 不得修改 AGENTS.md 或 CLAUDE.md(任何路徑、任何形式、任何理由)。
3. 不得要求、讀取、輸出、儲存或回報任何 token / API key / cookie / credential / secret;
   不得啟用或設定 MCP server;不得 commit、不得 push、不得建立 tag、不得發佈(no publish)。
4. 不得捏造指令。你的原生安裝/上傳指令若依 host 版本而異,必須先證明自己的版本與 discovery,
   並在顯示時標明「此指令依你的 host 版本而定」。
5. 不得聲稱 S4 acceptance、不得聲稱通過 portal 審核(portal approved)、不得聲稱已公開發佈
   (public plugin published)。
6. 目前不存在公開的 plugin directory listing。若我要求你「從 directory 安裝」,回報
   NOT_AVAILABLE(沒有可安裝的 listing),不要模擬一條不存在的路徑。

## 第 0 步 — 自我識別與權限宣告(只讀;先做,不要寫入)
逐項明確回答,不要含糊:
- host 身分:host 名稱、完整版本字串、你實際使用的模型/版本。
- OS:作業系統與版本;shell 種類與版本。
- 權限宣告:是否可執行 shell(可/不可)、可寫入哪些路徑(逐項列出)、是否有網路(有/無)。
- 專案根目錄:解析出 project root 的**絕對路徑**,並說明判斷依據(例如 .git、pyproject.toml、
  既有 skills 目錄)。若無法唯一決定,停下來問我,不要猜。
- 既有同名 skills:列出專案內所有既有的 pipd-* skill 目錄與其檔案;沒有就明確說「無」。
  你必須自行確認你的 host 真正採用的 discovery 路徑(本 repo 觀察到的 project-local skill
  目錄包括 .agents/skills/ 與 .hermes/skills/,但那是觀察,不是你的答案)。

## 第 1 步 — 證明你自己的版本與 discovery(仍不要寫入)
- 說明你的 host 如何 discovery skills:實際路徑、檔名規則、frontmatter 必要欄位、載入時機。
- 你的原生安裝/上傳指令(若存在)完整顯示;不存在或依版本而異時,明確說「本 host 無原生指令 /
  依版本而定」,並要求我提供版本資訊或明示改用檔案複製路徑。

## 第 2 步 — 顯示(等待同意前的最終要點;一律只顯示,不寫入)
- pinned source:來源 repo,以及你解析到的 40-hex commit;若你使用 zip,顯示該 zip 的 sha256。
  若無法解析出 40-hex commit(例如只有浮動分支尖端),停止並回報 REFUSED,不得用分支尖端代替。
- 目標路徑:即將寫入的**每一個絕對路徑**,逐檔列出。
- 檔案數量:即將寫入的檔案總數;並列出 diff against existing config(既有同名 skills 的比對):
  哪些新增、哪些覆寫、哪些衝突。
- uninstall path:如何完整移除你即將寫入的東西,逐檔列出。
- 你即將寫入的每個檔案,各自的 sha256。

## 第 3 步 — 明確同意閘門(STOP)
在你完成第 2 步、且收到我明確的「同意」之前:不得寫入任何檔案、不得執行任何安裝指令。
未取得同意時,只回報計畫後停止。

## 第 4 步 — 寫入(只寫入你在第 2 步已顯示的路徑)
- 只寫入第 2 步列出的 project-local 路徑;不得延伸到全域目錄;不得寫入其他任何地方。
- 不得修改 AGENTS.md / CLAUDE.md。
- 寫入後直接進入第 5 步驗證。

## 第 5 步 — 驗證「真實 discovery 與生效載入」,不是檔案存在
- 重新載入 / 重新 discovery,並用你自己的 discovery 輸出證明這八個 skills 被發現:
  pipd-route-intake, pipd-authority-source, pipd-profile-tailor, pipd-pi-compile, pipd-pd-bind,
  pipd-execution-contract, pipd-assurance-tqaep, pipd-package-project。
- 回報 effective load = n/8。必須是 8/8 才叫生效載入。
- 每個 host 各給一個 positive trigger 與一個 negative trigger 的**實測**結果:
  positive = 該 skill 應該被觸發的輸入;negative = 該 skill 不應該被觸發的輸入。兩者都要附實際輸出,
  不是預期值。
- 若你只複製了檔案,或無法證明 discovery,或無法給出觸發實測:回報 NOT_VERIFIED。
  不得因為「檔案存在」就回報 PASS。

## 第 6 步 — 最終回報(逐項列出;缺一項即視為未完成)
- host / OS / 版本
- pinned source(repo + 40-hex commit;若有 zip,附 sha256)
- effective skill count(生效載入數 n/8)
- refusal cases(本次你拒絕了哪些要求,逐條列出)
- raw log paths(每一步的原始輸出路徑)
並明確聲明:本流程不代表 S4 acceptance、未通過任何 portal 審核、未公開發佈任何 public plugin。
```
