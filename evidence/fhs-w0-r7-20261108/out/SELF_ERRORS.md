# 本輪自我錯誤登記（FHS W0 r7）

> 只記本輪真的犯過、且已被自己抓到的錯。每條都寫：錯在哪、怎麼被發現、怎麼修、修完怎麼證明還會咬。

## E-01｜WP-01 產物的 `head` 預覽以 bytes 截斷 120

- **症狀**：1,045 個抽樣中有 91 個尾端被切成 U+FFFD，中文尾字被切半
- **處置**：由回合層獨立檢查器 `tools/verify_u0_partition.py` 發現；**未改寫車道產物**，改為在檢查器裡把截斷痕跡與真正的 offset 不符分開計數，並在 r7 §B.3 `D-W0-R7-09` 公開記錄
- **修後證明**：偏移與覆蓋完全正確（31/31 檔位元全覆蓋），這是預覽瑕疵不是分割瑕疵

## E-02｜我自己寫的 GSTACK 閘把誠實的「不宣稱」判成裸聲稱

- **症狀**：三份 SPEC 的 `本 SPEC 不宣稱：ORIGINAL_ACK…` 被 G5b 判 FAIL
- **處置**：擴充豁免詞表加入 `不宣稱`／`不聲明`／`不得`，**沒有**去改 SPEC 的措辭來迎合掃描器
- **修後證明**：掃描器修正後仍需證明會咬：注入一句真的裸聲稱，G5b 立刻 FAIL

## E-03｜閘的 source 解析器只認檔名，不認 SourceID

- **症狀**：`FHS-BODY-02` 這類 SourceID 被判為 unresolved，131 個 ref 一度全紅
- **處置**：由 WP-00 的 source lock 建立 SourceID→檔名映射；另外把控制稿本身與其 r5 父本加入可解析集合
- **修後證明**：**沒有**放寬 span 斷言：解析成功後仍要求逐位元等於 quoted_text

## E-04｜閘的計數對帳只認一種鍵名

- **症狀**：WP-16 用 `measured.donor_slots_found`、WP-21 用 `counts.ac15`，閘一開始判為未宣告
- **處置**：改為別名解析（flatten 後接受 4 組同義鍵）
- **修後證明**：仍要求表格實際列數等於宣告數；注入 `donor_slots_found=26`（表實為 24）立刻 FAIL

## E-05｜我把子代理的中途摘要當成終值寫進 r7 章節

- **症狀**：章節初稿寫「23 條驗收」，WP-15 最終報告實為 15 條（6 POS／9 NEG）；相似度也誤植為 0.2139
- **處置**：改由建置器直接讀取車道的最終 `REPORT.json` 取值，並回頭修正章節文字
- **修後證明**：這是本輪最該記住的一條：**摘要不是產物**，只有落地檔案裡的欄位才是

## E-07｜發佈時我把「位元保全」放在 repo 既有不變量之上

- **症狀**：第一次推 SBL 時用本地 `.gitattributes * -text` 保全 CRLF 位元；SBL 既有的 `tests/test_reproducible_build.py::test_git_objects_are_lf_clean` 直接判紅（17 個 blob 含 CRLF），連帶使 `test_repro_mutation_probe` 失去意義（乾淨樹不通過）
- **處置**：以 repo 規則為準：移除 `-text`、把 payload 正規化為 LF，並在 `MANIFEST.json` 逐檔記錄**兩個** digest（`sha256_round` 為車道量測位元、`sha256_published` 為實際入庫位元），附「以 universal newlines 正規化回合副本即可對上」的橋接說明；Fabric 無此不變量，鏡像改回位元精確
- **修後證明**：重推後 SBL 四項檢查全綠（windows／ubuntu test、pipd-compat、supply-chain），且 r7 的 r6 前綴在正規化後仍 byte-identical

## E-06｜建置器一開始把不存在的 `evidence/WP00/REPORT.json` 列為引用

- **症狀**：建置以 exit 3 失敗
- **處置**：補寫 WP-00 的報告產生器 `tools/wp00_report.py`，讓報告由量測產生而非手寫
- **修後證明**：失敗是正確行為——引用不存在的路徑就該建置失敗，不是警告
