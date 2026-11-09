# FHS W0 r18 修補報告

| 項 | 值 |
|---|---|
| 文件 | `writeback/W0/FHS_PIPD-LS-PKG_W0_r18.md` |
| 位元數 | 619,413 B |
| sha256 | `1bc8d1af46beb30bccd1989f2b8b299c4e5a5f827e5e069d56bf87a5800e01ae` |
| 父本 | r12 582,469 B `139ff44013654373…`，逐位元前綴 |
| 完成等級 | **W0_AUTHOR_DESIGN_COMPLETE** |
| 簽章需求 | 0（未開窗） |

## 三項檢查的轉換

見文件第十四章 14.3。`G13` 與 `G19` 的判定現在來自磁碟上的 bytes；`G22` 如實降級為自報。

## 三項仍開著的原因

見 `writeback/W0/W0_CLOSEOUT_DECISION.json` 的 `still_open`：只有六項，且每一項都指名擁有者。

## 不主張

`formal_w0_acceptance`、`ORIGINAL_ACK`、`RELEASE_GRANTED`、`NATIVE_WORLDRAW`。
