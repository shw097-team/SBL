# FHS W0 r19 修補報告

| 項 | 值 |
|---|---|
| 文件 | `writeback/W0/FHS_PIPD-LS-PKG_W0_r19.md` |
| 位元數 | 621,333 B |
| sha256 | `7f2aec39ae5c85f89e0d9da13f510750d68993ddfad839123627091bd93933f0` |
| 父本 | r12 582,469 B `139ff44013654373…`，逐位元前綴 |
| 完成等級 | **W0_AUTHOR_DESIGN_COMPLETE** |
| 簽章需求 | 0（未開窗） |

## 三項檢查的轉換

見文件第十四章 14.3。`G13` 與 `G19` 的判定現在來自磁碟上的 bytes；`G22` 如實降級為自報。

## 三項仍開著的原因

見 `writeback/W0/W0_CLOSEOUT_DECISION.json` 的 `still_open`：只有六項，且每一項都指名擁有者。

## 不主張

`formal_w0_acceptance`、`ORIGINAL_ACK`、`RELEASE_GRANTED`、`NATIVE_WORLDRAW`。
