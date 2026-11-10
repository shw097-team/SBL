# Claim ceiling statement — FHS W0 r27 (2026-11-10)

> 一頁。對每個 token 回答三件事：**要成真需要什麼**、**本輪之後什麼為真**、**本輪被允許主張什麼**。
> 本輪唯一被允許的總結 token：`R27_APPEND_ONLY_CORRECTION_RECORDED`。
> 對應文件：`evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md` 的 CH27.8。

| token | 本輪允許主張 | 一句話理由 |
|---|---|---|
| `FULL_W0_CLOSEOUT` | **`NOT_CLAIMED`** | 22 個 full gate 仍有 6 個只能在有 31 冊本地來源的主機上跑；本輪沒有 full-profile 22/22 的執行記錄 |
| `NATIVE_SIGNED` | **`NOT_CLAIMED`** | 本輪沒有動用任何 owner 金鑰、沒有開簽章窗、沒有 mint 任何簽章 |
| `INDEPENDENT_PASS_CHALLENGE` | **`NOT_CLAIMED`** | r26 的 external challenge 是本輪修補的**對象**，不是被推翻的對象；r27 沒有第二個 credential 的獨立判定 |
| `RELEASE_GRANTED` | **`NOT_CLAIMED`** | 沒有 `GHP-02`、沒有發行、沒有發行後讀回 |
| `CROSS_SESSION_HARD_ENTRY` | **`NOT_CLAIMED`** | 只可能在「hook 已安裝且已量測」的那一台主機、那一個 dispatcher 上成立；其他 host／desktop session 一律不主張 |

---

## 1. `FULL_W0_CLOSEOUT`

**要成真需要**：一次在具備 31 冊本地來源的主機上、以 full profile 跑完 22 個 gate 且 22/22 通過的
執行記錄；每個 WP 達到各自的 claim 級別；原域 Reader 的 ACK 到位（不是 maker 端量測）。

**本輪之後為真**：payload profile 16/16（`evidence/L3/gate_baseline.log`，`VERDICT PASS pass=16/16`），
而 full profile 的 22 個之中有 6 個（`G11,G13,G16a,G16b,G19,G26`）只能在本地來源主機上跑——這個差額
在本輪被寫成 `not_runnable_in_CI`，不再被誤寫成 `excluded`（見 r27 文件 CH27.4）。
maker 端的 WP 量測不算 domain acceptance；六個 WP 在原域的 Reader 收據數仍是 **0**。

**允許**：`PARTIAL_FULL_PROFILE` 的**描述**（16/16 payload ＋ 6 個具名未跑），不是 closeout。

## 2. `NATIVE_SIGNED`

**要成真需要**：OWNER 在自己的受保護終端、以自己的金鑰，對**這一份** candidate 的 payload digest 簽章；
簽章窗有時戳與時區；簽章收據可被第三方用公開金鑰重驗。

**本輪之後為真**：本輪只產生文字與量測。沒有金鑰操作、沒有簽章窗、沒有新收據；既有 7 份簽章收據
（`receipts/reader/*.signed.json` 6 份 ＋ `receipts/OWNER_SEMANTIC_ACK_R26.signed.json`）**未被本輪
觸碰、未被本輪重簽**。r26 收據綁的是 r26 的 subject，不是 r27。

**允許**：`UNSIGNED_DOCUMENT`。任何把 r27 讀成「已簽」的引用都越界。

## 3. `INDEPENDENT_PASS_CHALLENGE`

**要成真需要**：一個與 maker 不同 credential 的獨立 reviewer，對**同一個** candidate 給出 verdict，
並附上它自己的 Raw；且該 verdict 必須涵蓋本輪修補過的每一項 finding。

**本輪之後為真**：r26 的 external challenge 指出的缺陷已被**逐項回應**（EC-R26-001…013 各有車道卡），
本文件的 CH27 只更正其中屬於文件層的敘述。r27 沒有經過任何獨立審查——它就是被審查的對象。

**允許**：`CHALLENGE_RESPONSE_RECORDED`。不是 `PASS`，也不是 `PASS_CHALLENGE`。

## 4. `RELEASE_GRANTED`

**要成真需要**：原 Publisher 以 `GHP-02` 對同 Candidate／Scope／Channel 給出准入，並有發行後讀回；
在此之前還需要同 BuildDigest 的 License／NOTICE／SBOM／scanner raw／rollback。

**本輪之後為真**：沒有任何一項。CI 綠（就算有）不是 Release；PR 綠燈不是 Release；文件完成不是 Release
（L0 §00.1 的 PUBLICATION 層）。三個 repo 只多了候選分支，沒有合併、沒有發行。

**允許**：`RELEASE_NOT_GRANTED`。

## 5. `CROSS_SESSION_HARD_ENTRY`

**要成真需要**：在**每一台**要主張的主機上，spawn 點都被機械攔截（不是 prompt 一行），且該主機上有
一次「無 binding → 零 spawn」的實跑記錄；desktop app session 與其他 repo 的 spawn 點也要各自有同樣證據。

**本輪之後為真**：本輪只主張「在某一個 repo 的某一個 dispatcher 上，入口可以被做成機械的」——而且那
件事屬於 L5 車道（branch `r27/fhs-entry-hook`），尚未落地：`evidence/L7/logs/13_landing_status.log`
量到該 worktree 仍停在 `acd9196`，`FHS_ENTRY_*` 十個全部 `NONE`（同批量測中，quorum 與 binding 兩個
家族的拒絕碼已在 `r27/quorum-g29@3099dec` 與 `r27/fhs3lm-binding@5402fe3` 落地，但那是別人的契約，
不能替入口能力背書）。對其他 host、其他 session、其他 repo：**沒有任何量測**。

**允許**：只允許「`FHS_ENTRY_*` 是契約名、有擁有者檔案」這句話；連「單機有效」都要等 L5 的 selftest log。

---

## 6. 本輪可以主張什麼

```
R27_APPEND_ONLY_CORRECTION_RECORDED
```

展開為三句可稽核的話：

1. r27 文件的前 667,205 bytes 與 r26 逐位元相同（`cmp` exit 0；`prefix_identical: true`；
   兩個 sha256 均為 `09c666da…`），r26 的 raw 形（668,540 bytes／`0ea05544…`）與該 LF 形只差 1,335 個
   CRLF 行尾，去 CR 後逐位元相等——同一份文件，兩種位元形式。
2. CH27 的八個小節逐項更正了 r26 的陳舊主張，每個小節都帶 finding id、舊文逐字引用、新值與可重現指令。
3. 七份藍圖的差額是 `PROPOSED_FOR_RATIFICATION`，且有 29 個實跑案例（7 接受／22 拒絕）證明「合法修正
   只能是純插入」。

**不在這句話裡的**：本文件被 ratify、被簽章、被獨立審查通過、被發行，或任何跨主機的硬入口能力。
