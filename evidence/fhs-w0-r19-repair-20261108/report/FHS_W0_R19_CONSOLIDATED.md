# FHS W0 r19｜對外交付整合

> 給外部驗收官與下一個 session。**完成等級：`W0_AUTHOR_DESIGN_COMPLETE`。**
> `formal_w0_acceptance` 未取得，且本回合以量測證明它無法由 Maker 簽發（見第十四章 14.4）。

## 1｜文件身分

- `writeback/W0/FHS_PIPD-LS-PKG_W0_r19.md` — 621,333 B — sha256 `7f2aec39ae5c85f89e0d9da13f510750d68993ddfad839123627091bd93933f0`
- 父本 r12 — 582,469 B — `139ff440136543731c1401b17b03ff56e886f80b7dcc08b5fb83892032744c46` — 逐位元前綴（builder 內以 `startswith` 斷言）

## 2｜這一版做的事

| # | 變更 | 依據 |
|---|---|---|
| 1 | 完成等級 `HOLD_NOT_ACCEPTED` → `W0_AUTHOR_DESIGN_COMPLETE` | W0 skeleton L81 |
| 2 | `V-01` 由 owner 陳述結案，canonical = `69a08e7f` | owner 為唯一持有者 |
| 3 | `G13` 改為從 31 檔重算 in-set 分組 | 不再讀 ledger 的兩個數字 |
| 4 | `G19` 改為逐檔重新雜湊並 walk 三個 root | 新增 `UNDECLARED_COPY_ON_DISK` |
| 5 | `G22` 降為 `REPORTING`，標註 `SELF_REPORTED_BY_THE_SUBJECT` | 主體是閘自己，無法外部重算 |
| 6 | r12 的 `parent_version` 標籤錯誤更正 | digest 一直是 r11 的 |

## 3｜六項具名待辦（Maker 側已無可修項）

| 項目 | 擁有者 | 條件 |
|---|---|---|
| `formal_w0_acceptance` | owner 或第二 principal | 信封無此 kind；且 maker 不得自簽 |
| `ORIGINAL_ACK` 0/6 | 各原域 Reader | 本人簽名 |
| `G16b` 依賴覆蓋 | owner | 需指名 HG-KSEOS 的授權才可套 patch |
| `LICENCE` | owner | 法律行為 |
| `PIPD-15-VALUESET` | owner | 產品語義 |
| `R1-ISSUER-REV14` | owner | 需開 owner 金鑰窗 |

## 4｜自我錯誤（本回合）

前幾輪我反覆犯的是「以產物對照產物」，本回合把 `G13`／`G19` 也改成重算。
另外我上一輪把 r10 的舊測值（567,669 B）當成發佈身分，宣稱與驗收報告有 451 B 落差——**那是錯的**：
磁碟上 r10 = 568,120 B／`2285baaf`，與報告表頭完全一致。此更正已寫入交接與本章第 4 節。

## 5｜重現

```bash
python tools/build_r19.py
python tools/gate_r19.py --round . --skip-hygiene
python tools/gate_r19.py --round . --skip-hygiene --selftest --quiet
```
