# FHS W0 r9 — 本輪自我錯誤（全部發生在這一輪，全部已修）

> 原則：錯要留在檔案裡，不能只留在對話裡。以下每一條都附「怎麼被發現」與「改了什麼」，
> 且都可以由 `tools/` 下的程式重跑驗證。

## E-R01｜`--prior` 沒有切換模式，第一次「差分」其實是同一棵樹跑兩次

**症狀**：gate 對「修補後的樹」與「修補前的回合」輸出**逐字相同**的十行判決。

**為什麼會發生**：`main()` 裡 `ctx = Ctx("r9", a.round, a.prior)` 把模式寫死，`--prior` 只被當成
「第二個目錄」而不是「要看哪一代產物」。

**怎麼被發現**：兩次輸出的 `G12` 都印出 `structural=25201 files=31`——那時 `lanes/B` 才剛寫完，
修補前的回合不可能有這個數字。輸出太一致本身就是證據。

**修法**：加 `--mode {r9,prior}`，且未指定時 `--prior` 在場即為 `prior`。修正後同一支閘對
r6 回合給出 `4 PASS／6 FAIL／…`，紅的正是缺陷還在的那幾項。

**教訓**：差分測試要先證明「兩邊不同」，否則它只是一次重跑。

## E-R02｜閘先假設 schema，四項檢查直接拋 `AttributeError`

**症狀**：`G15`／`G16` 以 `'str' object has no attribute 'get'` 結束，`G17` 數到 0 個 id。

**為什麼會發生**：我照著自己在 brief 裡寫的欄位名（`repos` 是 list、`match.lines` 是巢狀、
`seam.ids`）寫檢查，但 lane 交出來的是另一組同樣合理的形狀（`repos` 是 dict、`lines_match` 是扁平、
`seam.expected_ids`）。

**修法**：**改閘，不改產物**。每個檢查同時接受兩種形狀（`_repo_rows()`、`_match()`、`expected_ids or ids`），
並保留「欄位不存在就紅」的嚴格性——`DEPENDENCY_VERDICT_ABSENT` 仍然會咬。

**教訓**：gate 的職責是讀懂產物，不是要求產物長成 gate 的樣子。把產物改成迎合檢查，等於用檢查器定義事實。

## E-R03｜`G16` 第一版把上一輪的錯誤當成事實寫進檢查

**症狀**：初版 `G16` 要求「HG-KSEOS 的未宣告清單必須包含 `cryptography`」。

**為什麼會發生**：我直接採用了附錄 `A-01` 的敘述。實際去讀 `pyproject.toml` 才發現
`dependencies = ["cryptography>=42"]`，而 `src/hg_kseos/fhs/issuer_binding.py` 根本不存在。

**修法**：把檢查改成要求 `yaml`，並新增一條反向斷言——**任何把 `cryptography` 列為未宣告的產物一律紅**
（`CRYPTOGRAPHY_FALSELY_MARKED_UNDECLARED`）。也就是說，這條檢查現在同時防止「漏報」與「照抄舊錯」。

**教訓**：把別人的結論寫進檢查器，等於把那個結論升格成規則。檢查器只能編碼自己重算過的東西。

## E-R04｜A-01 檢查器把 first-party 模組與 dist/import 異名判成未宣告依賴

**症狀**：`undeclared=['run_acceptance','yaml']`，但 `run_acceptance` 是 repo 自己 `tools/` 下的模組
（`cli.py` 用 `sys.path.insert` 後 import），而 `PyYAML` 的 import 名就是 `yaml`。

**修法**：加 `local_module_names()`（掃 `tools/`、`src/hg_kseos/` 的 `.py` 檔名）與 `DIST_TO_IMPORT`
映射（`pyyaml→yaml` 等），並把兩者都記進 `RESULT.json` 的 `local_modules_excluded` 與 `declared_optional`。

**結果**：`before=UNDECLARED_DEPENDENCY ['yaml']` → `after=DECLARED_COVERS_IMPORTS []`。

**教訓**：一個「未宣告」的判定，必須先扣掉「它其實是自家的」與「它名字不一樣」。

## E-R05｜`patch -p0` 對 `a/` 前綴的 diff：找不到檔案

**症狀**：`can't find file to patch at input line 3`。

**修法**：改 `-p1`，並保留 `--binary`（CRLF 檔不加 `--binary` 會被判成行尾不同）。
套用後斷言「套用結果 == 候選檔 bytes」＝`True`，而不是只看 `patch` 的 exit code。

## E-R06｜r9 文件重建成兩次，第二次前沒有先確認「payload 會不會過期」

**症狀**：第一次 `stage_r9.py` 之後才發現 `GATE_R9.json` 還是 `9/10`（`G18` 因無載荷為 n/a）；
重建文件又會改 digest，讓 payload 立刻過期。

**修法**：固定時間戳（`FHS_ROUND_TS`）讓重建可重現，並把順序寫死成
`build → stage → verify → gate(no --json)`；另跑一次 `--json out/_gate_recheck.json` 只為比較
summary 是否相等（`stable: True`），比較完刪除。

**教訓**：載荷的 digest 依賴「最後一次寫入」的順序。順序不是流程偏好，是正確性的一部分。

## E-R07｜「十個缺陷」與「七個缺陷」在同一句話裡混用

**症狀**：`D.0` 初稿寫「r8 把上一輪量到的七個缺陷寫成句子」，但同一句又要交代 `A-01`／`A-02`／`A-03`
這三個附錄項，總數其實是 10。

**修法**：把處置表 `DEFECT_DISPOSITION` 提成單一來源，`D.0`、closeout sidecar 與計數全部由它推導
（`closed_count=8`、`owner_pending_count=2`），不再手寫任何一個數字。

**教訓**：同一個數字在兩個地方出現，就會有兩個版本；讓它只從一個 dict 出來。

---

## 本輪沒有發生但值得記住的三件事

1. **`G17` 在修補前是 PASS**——前輪的 SEAM 數是對的。差分抓不到「數字對但推導不可檢驗」這一類，
   只有注入（把 naive 改成 11）才證明它會咬。這說明差分與注入不是替代關係。
2. **`V-05` 早在 r8 發佈時就已修好**（SBL 載荷 19/19 本地解析），但沒有一支閘在看它。
   本輪補 `G18` 的價值不在「修一個壞掉的東西」，而在「讓修好的東西不會靜靜退化」。
3. **`V-03` 的 17 需要一條沒寫出來的規則**（剝掉檔名尾碼 `(N)`）。精確同名比對的結果是 0。
   一個數字若依賴未記載的正規化，它在下一個 reader 手裡就是另一個數字。

## E-R08｜位數抄對了，位置卻寫成自己早先 `find` 的結果

**症狀**：r9 章節 `D.2(4)` 寫「HG-KSEOS 的 8 個嵌套授權檔全部落在 `.hgk/checker-upgrade-20261009/.../.tmp/plugins/`
的 vendored 外掛快取樹內」。而同一句所引用的 `lanes/D/WP19_V2.json` 裡，那 8 筆的路徑**全部**是
`fhs_msc_handoff_20261030/WP-FHS-17/{candidate/package,evidence/rollback-root,evidence/stage-root,evidence/tamper-root}/`。

**為什麼會發生**：在 lane 回報之前，我自己跑過一次 `find . -iname "LICENSE*"`，那次走的是**檔案系統**，
所以掃到了 `.hgk/` 這種未追蹤的沙箱；lane 用的是 `git ls-files`，只算 tracked。兩個總數都是 8 是巧合，
我卻把「自己那次 find 的位置」接到「lane 的數字」上，於是產生一句**數字對、位置錯**的敘述。

**怎麼被發現**：批次回報送達後，我把摘要與自己引用的 artifact 逐欄對照——不是對照摘要，是對照 JSON 的
`nested_licences[].path_rel`。這一條如果只讀摘要（「HG-KSEOS 8，全在 WP-FHS-17 下」）不會發現，
因為摘要寫對了、是我章節寫錯了。

**修法**：`D.2(4)` 改成由 artifact 欄位導出（`hgk_prefixes`、`hgk_kinds` 從 `nested_licences` 算），
並把強度寫對：那 8 個是 **tracked** 的授權檔，`candidate/package/LICENSE` 第 3 行是
「Copyright (c) 2026 the owner of this system. All rights reserved.」。也就是說 HGK 的問題
從「沒有授權檔」變成「有四組 proprietary 授權檔」——後者是 owner 要回答的問題，不是量測缺口。

**教訓**：引用了哪個 artifact，就只能用那個 artifact 的欄位描述它。我自己的 `find` 是**另一個量測**，
它可以存在，但不能冒充被引用 artifact 的內容。差別不是精度，是**指涉對象**。
