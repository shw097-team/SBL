# 95 — SBL → SWOF W2 shadow handoff (read-only)

下游不需要 SBL 完成 441 項安裝才開工。這份交接只給三件東西：精確的 SBL 來源身分、可允許的
唯讀範圍、以及明確的禁止範圍。其餘由 SWOF 自己的 Owner 與 Gate 決定。

JSON 正本：`95_SWOF_W2_SHADOW_HANDOFF.json`。

## 已釘死的來源

| 角色 | 身分 | 本輪如何確認 |
|---|---|---|
| SBL 主體 | `bedc11957d4fc2474b249b69d200829272c118ef` | `git ls-remote` 回讀 |
| SBL 發行 | `v0.1.0-foundation-preview`（prerelease） | Release API，tag 指向 `bedc119` |
| Foundation wheel | `95e57c44…`（27,181 B） | R4 報告與 Release asset digest 相符 |
| c3 plugin 候選 | `68c276d3…`（**未合併**） | 本次推上去的 candidate 分支，CI `39525131900` 2/2 |
| SWOF 主線 | `acdbfaa…` | `git ls-remote`，與 R4 快照一致 |
| SWOF W2 來源 | `c333e47…`（PR #7） | 同上 |
| SWOF R9E 證據 | `963cade…` | 同上 |

**c3 的舊 SHA 作廢。** R4 報告列的三個 ZIP digest（`eb26683d` / `f981d53f` / `75a904c4`）屬於
`39c604d`，那份 manifest 沒有 portable `$schema`，wheel 也缺 `sbl_sp/manifests/*.json`。修補後重
產生的三份是 `c1987c3e` / `2c408822` / `cb917f83`。任何下游若已引用舊 digest，需重新取件。

## 允許與禁止

允許：W1/W2 唯讀審查、`NO_EFFECT` 影子執行、Issue→Task→PR 規劃、以及**在 SWOF 自己授權下的**
受影修補。

禁止：世界副作用、W3 自動准入、SWOF native ACK 自簽、SBL 代寫 SWOF verdict、SBL 代做發行。

W3 一律 `NOT_GRANTED`。這一輪 SBL 沒有、也不會產生 receiver acknowledgement：SBL 的 HMAC
ModeGate 是演示格式，不是 SWOF 的 Permit。

## 下一手（SWOF Owner）

1. 鎖 `main acdbfaa` + W2 `c333e47` + R9E `963cade`，判定 PR #1–#7 哪個該 archive。
2. 只對 R9E 屬性做受影 replay，先定 W1/W2 原生 Gate，再談 merge 順序。
3. 走 SWOF 自己的通道合併，不 force；基線變動要重新 freeze。
4. W3 可以寫 PRD-lite / SDD / ADR / TaskSpec / 負例；在 Wave Admission 與 native Permit 之前不啟動
   會改世界的 runtime。

本輪 SBL 對 SWOF 只做了兩件事：讀四個 SHA、把這份檔案放進自己的證據分支。
