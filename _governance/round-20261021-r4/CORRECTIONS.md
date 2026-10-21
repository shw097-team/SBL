# CORRECTIONS — R4 本輪自己引入又修掉的缺陷

規則：本輪任何**自己造成**的缺陷寫在這裡，不寫進產品變更說明去美化；修法與證據一起列。
不是自己造成的發現（例如宿主/契約缺陷）另立 Finding，不混進這一頁。

## #1 `skill_name()` 把 `tpm_sp` 變成 `tpm`

**症狀**：`sbl_sp.plugins.skill_name("tpm_sp")` 回 `tpm`，於是套件內是 `skills/tpm/SKILL.md`，而
`SKILL.md` 的 frontmatter 寫 `name: tpm-sp` —— 目錄名與技能名不一致。第一次跑測試時三個 principal
全部 fail。

**成因**：`sp_id.replace("_sp", "")` 想砍尾綴，實際 `_sp` 就是尾綴本身，砍完只剩 `tpm`。

**修法**：`skill_name` 與 `_plugin_name` 一律用 `sp_id.replace("_", "-")`，技能名 == 目錄名 ==
frontmatter `name`。`validate_skill` 會擋下不一致，所以這個錯不會再靜默通過。

## #2 `check_wheel_contents.py` 用了執行環境的 setuptools，Windows runner 直接失敗

**症狀**：本機 `wheel contents OK`；CI `39524758836` 的 windows job 在
`Wheel carries its runtime data` 失敗，錯誤是
`configuration error: project.license must be valid exactly by one definition`。

**成因**：`import setuptools.build_meta` 取的是**直譯器當下的** setuptools。runner 上那份太舊，
不認 PEP 639 的字串式 `license = "MIT"`；本機的夠新所以過。等於這個檢查在測 runner 的建置工具，
不是在測產物。

**修法**：改為 `subprocess` 呼叫 `pip wheel`（吃 `[build-system].requires`，會拉新 setuptools），
並把 `requires` 提到 `setuptools>=77`。建置失敗即 fatal，不跳過。CI `39525131900` 2/2 綠。

## #3 安裝收據把「本機裝了」寫成「宿主接受了」

**症狀**：`INSTALL_RECEIPT.json` 寫 `host_install_state: INSTALLED_ON_THIS_HOST`，但同一次執行產生的
`stack.json` 寫 `host_install_state: NOT_INSTALLED`。同一份證據裡兩個相反宣稱。

**成因**：把「這台機器上有檔案」與「宿主接受了這個套件」壓進同一個欄位。

**修法**：拆成 `local_install_state: INSTALLED_ON_THIS_MACHINE` 與
`host_acceptance: NOT_HOST_ACCEPTED`；`install_local.py` 同步改。既有收據就地更正並留下
`correction` 欄位指向本節，不重跑（重跑會因目錄非空而拒絕，那反而是對的）。

## #4 Docker 沙盒腳本把 `$rc` 當成 shell 變數傳進 python

**症狀**：第一次跑沙盒，聚合步驟抛 `NameError: name 'rc' is not defined`。

**成因**：`python - "$rc" <<'PY'` 的參數是 `sys.argv[1]`，不是同名變數。

**修法**：`rc = sys.argv[1]`。沙盒第一輪同時抓到一個真的產品缺陷（見下），所以這一段花的時間是
值得的。

## #5 沙盒假設 `sbl-todo --help` 會成功

**症狀**：`sbl-todo.help` 步驟 fail。

**成因**：那是我的假設，不是產品的契約 —— 這個 CLI 對未知子命令直接報錯。

**修法**：改成真正的 FUO 三段（`init` / `add --title` / `list --json`），與 GJ01 說的一致。

---

# Finding（不是本輪的錯，本輪才發現）

## `F-R4-WHEEL-PACKAGEDATA-001` — wheel 少了 `sbl_sp/manifests/*.json`

**發現途徑**：Docker 沙盒第一次跑 `sbl-stack selftest`，`sp.manifests` 步驟拋
`SBL_E_UNKNOWN_SP: tpm_sp`。本機 183 個測試全綠，因為它們跑在原始碼樹上。

**為什麼一直沒被發現**：CI 用 `pip install -e .`，editable 安裝的所有資料檔都直接從原始碼樹解析，
`[tool.setuptools.package-data]` 漏一項對整個測試套件完全不可見。這個缺陷**從 Foundation 就存在**，
只是 GJ01 只用 `sbl-todo`，不需要 SP manifest。

**影響**：任何 `pip install` 這個 wheel 的使用者，呼叫 `load_manifest` 一律失敗。這不是候選分支的
問題，是已發佈 preview 的安裝面問題。

**修法**：補 `package-data`；新增 `tools/check_wheel_contents.py` 在 CI 建真 wheel 並斷言成員；
`setuptools>=77`。CI `39525131900` 兩個平台都跑這個步驟且綠。

**為什麼不回溯撤回 preview**：依 R4 §1/§8，已發佈的 `v0.1.0-foundation-preview` 只宣稱 `sbl-todo`
這條 FUO，而該 FUO 不經 `load_manifest`，因此不受此缺陷影響。這個缺陷屬於 c3 之後的 SP/Stack
surface，修正後隨新 candidate 走，不動已發行 bytes。

---

# 流程違規（已修正，未外溢）

## #6 在 secret scan 回 `BLOCKED` 的同一次呼叫裡就 commit 了

**發生什麼**：我把 `secret_scan` 與 `git commit` 串在同一個 `&&` 鏈。掃描先回
`{"verdict":"BLOCKED","files_scanned":274,"hard_findings":1}`（命中
`skills-preinstall.tar.gz` 內的一個 email address），commit 仍然在同一鏈後段執行。

**為什麼沒有外溢**：該 tar.gz 被 `.gitignore` 的 `_governance/**/*.tar.gz` 排除，因此**沒有任何
不安全位元組進入 commit**，也**沒有 push**。commit `ecf6b5f` 當時尚未推送。

**修法**：(a) 把 archive 移出 repo 樹到 `C:\Projects\_sbl_r4\`，只保留 digest；(b) 在
`ROLLBACK_MANIFEST.json` 記 `storage: OUTSIDE_PUBLISHED_TREE` 與原因；(c) 重跑掃描得
`CLEAN / 273 files / 0 hard_findings`；(d) 在 push 前 amend。

**教訓（寫進 skill）**：閘門與寫入不能串在同一個 `&&` 鏈 —— 閘門的 exit code 若不是非零，鏈就會
把「檢查」與「放行」當成同一步。掃描要獨立一次呼叫，讀完 verdict 才動手。

