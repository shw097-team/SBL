# FHS W0 — r22 結案與移交（2026-11-09）

## 0. 一句話

r20 關掉第四次驗收的兩個阻斷缺陷；r21 以第二十一章更正 r20 的文件漂移、關掉
`traditional` 弱標記繞過與 `G21` 豁免；r22 更正第二十一章自己的 BLOCKING 計數（16/16，不是 19/19），
並修掉 r21 車道量到的兩個規則缺陷：`\b` 經 heredoc 變成 U+0008、以及標記在字串任一處即豁免整串。

| 事實 | 值 |
|---|---|
| 交付文件 | FHS_PIPD-LS-PKG_W0_r22.md 638,888 B `c06e2b850da7e26bf2d326a7d80f3b397b40c6de1c589c82f478f55bf0f19d37` |
| 前綴 | r21（634,869 B）→ r22；r20 → r21；r13（592,369 B）仍為前綴 |
| 簽署範圍 | owner semantic acceptance 綁 **r21**（`receipts/OWNER_SEMANTIC_ACK_R21.signed.json`）；r22 是 r21 的逐位元延伸，builder 以 `startswith` 斷言 |
| 閘 | `tools/gate_r20.py`（GSTACK v6，21 項），0 BLOCKING FAIL，1 REPORTING OPEN（G16b） |
| 自測 | 16/16 BLOCKING FIRED；19 FIRED 總數（含 G16c/G20/G25）；G22 EXEMPT（REPORTING）；G16b BASELINE_RED（REPORTING）；`wrote_inside_round: false`、`round_tree_unchanged: true`；exit 0 |
| 標籤紀律 | 0 violations；5 個控制（含兩個 affirmative-`traditional` 反例）全 FIRED |
| Owner 窗口 | `WIN-fc83c1d80cb6`，ops 8/8，effect ceiling `READ_ONLY_PROBE` |
| 原域 ACK | 傳統 **0/6**；`FHS_ORIGINAL_ACK` 6/6 |

## 1. 三輪缺陷的軌跡（全部 NACK，逐次更深）

| 輪 | 抓到什麼 | 本輪處置 |
|---|---|---|
| r19 NACK | 自測就地寫檔（唯讀不可重現）；限定詞只到 markdown 與三個鍵 | r20 改 in-process overlay；新增 G28 與機器可讀掃描 |
| r20 NACK | 文件寫副本、實作是覆寫；`traditional` 弱標記被肯定句利用；`G21` 以豁免代替突變 | r21 append 第二十一章更正；標記分強弱；G21 改為突變 |
| r21 NACK | BLOCKING 計數說成 19/19（實為 16/16）；`\b` 落檔成 U+0008；標記在字串任一處即豁免整串 | r22 append 第二十二章更正；ASCII 邊界字元類；機器路徑改子句級 |

## 2. 規則的兩個路徑（刻意不同）

- **機器可讀**（`out/`、`receipts/`、`evidence/`）：子句級判定。標記只豁免所在子句，
  同子句有肯定斷言時弱標記不豁免。兩個反例現在都是 VIOLATION。
- **散文**：行級判定。文件 append-only，更嚴的規則會回溯點亮 94 行歷史章節（例如
  「AUTHOR_DESIGN ≠ ORIGINAL_READER_ACK」這類定義句），那些章節沒有任何人可以改。

## 3. 錯層稽核

| 層 | 位置 | 判定 |
|---|---|---|
| 權威層 | `SBL/main`、`Fabric/main` | 未寫入（合併待 PASS） |
| 候選層 | PR #58、PR #44 | r22 全部交付物 |
| 作者工作層 | `FHS_W0_R13_ACCEPTANCE_20261108/` | 全部來源 |
| 可棄層 | `out/stage/**` | 可重建載荷副本 |

控制平面變更：**無**。

## 4. 明確不主張

- 第二十章的機制描述正確（第二十一章已更正）。
- 第二十一章的計數正確（本章已更正）。
- 散文與機器路徑一樣嚴格。
- 傳統 per-domain `ORIGINAL_ACK`（0/6）。
- `G16b` 已閉合。
- 已合併、已審、已發行（除 §5 判決 PASS 且 PR 真的合併）。

## 5. 驗收與發布

獨立 VERIFY 車道以 `codex exec --sandbox read-only -m gpt-6.1-sol` 執行，判決寫在
`lanes/VERIFY_R22_VERDICT.json`。發布與合併只在 PASS 之後，PR head sha 與合併結果以 GitHub API 讀回。

## 6. 可重現指令

```text
cd C:\Projects\Agent_Workspace\FHS_W0_R13_ACCEPTANCE_20261108
python tools/gate_r20.py --round . --skip-hygiene
python tools/gate_r20.py --round . --skip-hygiene --selftest          # exit 0
python tools/verify_reader_ack.py
python tools/label_discipline.py --selftest
python tools/gate_r20.py --round out/stage/sbl/evidence/fhs-w0-r22-repair-20261109 --profile payload --scope payload --skip-hygiene
```
