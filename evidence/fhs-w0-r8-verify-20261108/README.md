# FHS W0 r8 verification evidence（2026-11-08）

對 `FHS_PIPD-LS-PKG_W0_r6` 的本地實作所做的獨立重驗：六個工作包、四條隔離車道、
一支 16 項閘、一份逐項對帳與七個缺陷處置。

- 判決：六個 WP 頭條數字 **REPRODUCED**（兩項帶規則相依說明）；原域 `ORIGINAL_ACK` **0**。
- 閘：`out/GATE_R8_OBJECT.json` = 16/16 PASS；同一支閘對 r7 為 15/16（`G10` 紅）。
- 負控：`lanes/GATE_NEG/GATE_NEG_RESULT.json` = 三層注入、紅在且僅紅在 `G2`/`G5b`/`G6`。
- 缺陷：`out/CORRECTIONS.json`（含 11 筆發佈 digest 更正）與 r8 章節 `C.3`。
- 文件本體在 Fabric 鏡像 `INTEGRATION/FHS/docs/as-built/W0/r8/`（**本 payload 不重複攜帶文件，也不宣告它的 digest**）。

本目錄所有檔案以 LF 提交（SBL 的 `test_git_objects_are_lf_clean` 要求）；`MANIFEST.json`
只宣告本 payload 自己攜帶的檔案，因此每個 digest 在此 payload 內都可解析。
