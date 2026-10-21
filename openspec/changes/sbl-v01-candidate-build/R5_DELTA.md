# R5 Delta — openspec change `sbl-v01-candidate-build`

## Added

- `ACC-R5_UNINSTALL_BOUNDARY`：HGK adapter 卸載邊界的能力驗收邊（正：安裝→doctor→卸載無殘留且
  manifest 宣告 digest 與檔案一致；負：`../outside.txt`、絕對路徑、symlink、junction 祖先、非 allowlist
  鍵、malformed manifest 全部 typed 拒絕且外部 sentinel bytes 不變；恢復：拒絕後目錄、manifest、
  sentinel 皆保留）。

## Changed

- `sbl_harness.uninstall` 的刪除集合由「manifest 鍵」改為「installer 固定檔案清單」，並加上
  resolve 內含、link 拒絕、digest 前置比對、目錄清掃限界。
- `sbl_core.errors` 新增 `SBL_E_MANIFEST_UNTRUSTED`。

## Unchanged / not reopened

- Foundation `main` 合併與 `v0.1.0-foundation-preview`。
- c3-v2 的 plugin schema / package-data / stack / wheel 工作。
- `sbl_core` m01..m06 邏輯。
- 441 / 149 / 38 frozen ledger。

## Scope note

本 delta 只關閉 `F-R5-HARNESS-UNINSTALL-TRAVERSAL-001`；`SBL_FULL_DOC_CONTRACT_PASS` 不在本 delta
的能力範圍內，TS07–TS25 仍 OPEN。
