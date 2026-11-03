# 結案、移交與工程衛生（2026-11-03 第三輪：受影建置與主用升格）

> 本文件是這一輪的正式結案與移交。它放在 repo 裡而**不是**放在 run 目錄，理由見 §3。
> 上位：`sbl-tpm-sp_前置修補藍圖` r2；本輪只做「重新簽 pin → 0.3.1-rc.1 → 重跑 Host 鏈 → 升為現役主用」。

---

## 1. 交付

| 項 | 值 |
|---|---|
| 版本 | `sbl-tpm-sp 0.3.1-rc.1` |
| ZIP | `_archive/sbl-tpm-sp/2026-11-03/sbl-tpm-sp-0.3.1-rc.1-private.zip` |
| SHA256 | `f00c579280b0db51a850e13f7f3d000539dd86b298a1e5d4ade339a4d8e1a6cc` |
| 大小／成員 | 5,121,699 bytes／176（14 `SKILL.md`，0 bytecode，0 cache） |
| 與 rc.2 差分 | 新增 3／修改 3／刪除 0 |
| 主用狀態 | **已升格**，範圍＝已驗 Linux Codex host，`DESIGN_ONLY` |
| SBL MAIN | `7d08363851`（PR #35、#36、#37、#38、#39） |
| 指標檔 | `_archive/sbl-tpm-sp/CURRENT.json` |

歷史版本未被覆寫：rc.1 `c4181e24…`、rc.2 `3a9da65…`，`sha256sum -c SHA256SUMS` 三檔全 `OK`。

## 2. 這輪實際改變了什麼

1. **pin 由 reader 端簽發**（`issue_reader_pins.py`，35 檔、`f0b287dd…`、`git_head a5d3a767`），
   owner 在 `WIN-9d10aa7face0` 簽 `RATIFY_READER_PIN_SET`（1/20 ops）。候選不自寫 pin，避免循環驗證。
2. **重建成 0.3.1-rc.1**：reader 修好後身分改變（14→15 模組），舊 pin 集合必然不完整。
3. **Host 鏈一次跑完**（單一 run、同一隔離 `CODEX_HOME`）：安裝→載入→Skill 使用→Nontrigger→降版 rc.2→回復。
4. **升為現役主用**，但只限已驗範圍；Windows 原生 host 明確排除。
5. **把建置程序工具化**（`tools/build_tpm_sp_candidate.py`＋7 tests），讓成品可重現。

## 3. 可棄層／候選層稽核（本輪重點）

| 稽核對象 | 發現 | 處置 |
|---|---|---|
| **建置程序** | 只在 session／run 目錄，從未入庫。成品可封存、**配方不可重現** | PR #39：工具化＋測試；保真度 176/176 內容相符 |
| 升格安裝失敗紀錄 | 第一次 stdout 被同路徑覆寫而遺失，且未揭露 | PR #38：具名記錄失敗，並註明「引文不是重製檔」 |
| 三段式批次失敗（run B） | 只留本機 log，未入庫 | `BUILD_031RC1.md` 與 PR #36 說明；**庫內仍只放成功那條** |
| 成品 ZIP | 已在 `_archive` 並有 `SHA256SUMS` | 無誤置 |
| `CURRENT.json` | 權威版在 `_archive/` 頂層；run 目錄有副本 | 副本視為附屬，不入庫重複 |
| 中間產物 | `pkg-031rc1`、`market-031rc1`、promotion 解包、數十個 `plugins-clone-*`（共 634 M） | 清除至 82 M；ZIP 已封存，可用工具重建 |
| worktree | `deliver/sbl-pins` 仍註冊 | 已移除＋`worktree prune` |
| 分支 | 本輪 4 條已合併分支殘留 | local＋remote 已刪（先驗 `merge-base --is-ancestor`） |
| 憑證 | 每輪即時清零 | 本次清零；掃描無 `.ghtok*`／`*.curlrc` 殘留 |
| SBL 主樹髒檔 | `contracts/compiled/thin-prompt.md` 等，時間戳 10-21／10-23 | **非本輪產生，未動** |

**結論**：本輪沒有把「唯一副本」留在可棄層。唯一真正的層級錯置是**建置配方**，已修。

## 4. 移交：怎麼用

```bash
# 1) 從封存安裝（marketplace 需 plugins/sbl-tpm-sp 佈局，不是 zip 頂層）
unzip sbl-tpm-sp-0.3.1-rc.1-private.zip -d market/plugins/
codex plugin add sbl-tpm-sp@<marketplace-name>
codex plugin list | grep tpm      # 期望：installed, enabled  0.3.1-rc.1
```

**配對硬條件**：SBL `main ≥ 00f2722d`。舊 reader 會以 `ORIGINAL_READER_PIN_SET` / `ORIGINAL_READER_DRIFT` 拒絕。

```bash
# 2) 重建（從同一個樹得到同樣內容）
python integrations/pipd/tools/build_tpm_sp_candidate.py \
  --tree <extracted>/sbl-tpm-sp --version 0.3.1-rc.1 \
  --pins READER_PINS.json --signature READER_PINS.owner.sig.json \
  --out out.zip [--normalise-timestamps]
```

mtimes 是輸入；要時鐘無關的 digest 需 `--normalise-timestamps`（會與 `f00c5792…` 不同，這是預期）。

```bash
# 3) 回退
codex plugin remove sbl-tpm-sp@<marketplace>
codex plugin add sbl-tpm-sp@sbl-pre-primary-local   # rc.2, 3a9da65…
```

回退同時失去受信任 registry 載入路徑——新版出問題時，優先同版重建。

## 5. 未結／界線（不得視為已合格）

| 項 | 狀態 |
|---|---|
| Windows 原生 Codex host | `HOST_124_HOLD`（MXC 沙盒無法建子程序；PS7 只解 shell 層） |
| 硬化 sandbox | `RUNTIME_SECCOMP_UNCONFINED`（殘留 F-1：`kernel.unprivileged_userns_clone=1` 後以預設 seccomp 重跑） |
| Native GJ02 | `NATIVE_GOLDEN_HOLD`（無原 Issuer／Checker／Publisher） |
| 原 Effect Registry | `EFFECT_REGISTRY_UNBOUND`（僅 source-bound + owner-ratified 契約） |
| Grant | `NOT_GRANTED` 全程未變 |
| TQAEP | `TQAEP_DESIGNED`，`independent_acceptance=NOT_GRANTED` |
| HG-KSEOS PR #10 | 仍 open，需 repo owner 合併 |
| OpenCode Go 金鑰池 | 3 把中 2 把 429、1 把 401；輪替是 Owner 的動作 |

**裁決不變**：`PRE_V2_CLOSEOUT=YES`（Linux Codex host × `DESIGN_ONLY`）。升格 ≠ Qualified。
