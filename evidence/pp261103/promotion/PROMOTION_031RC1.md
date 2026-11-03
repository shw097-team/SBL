# 主用升格：`sbl-tpm-sp 0.3.1-rc.1`

**Owner 授權**：2026-11-03，口頭指示「授權把 0.3.1-rc.1 升為現役主用」。
**生效範圍**：**已驗的 Linux Codex Host**（design ceiling）。
**不在範圍**：Windows 原生 Codex host（`HOST_124_HOLD`）、硬化 sandbox（`RUNTIME_SECCOMP_UNCONFINED`）。

---

## 一、升格對象

| 項 | 值 |
|---|---|
| 版本 | `0.3.1-rc.1` |
| ZIP | `_archive/sbl-tpm-sp/2026-11-03/sbl-tpm-sp-0.3.1-rc.1-private.zip` |
| SHA256 | `f00c579280b0db51a850e13f7f3d000539dd86b298a1e5d4ade339a4d8e1a6cc` |
| 成員／Skills | 176／14（0 bytecode、0 cache） |
| 內附 pin 集合 | 35 檔，`pin_set_sha256 f0b287dd…`，`git_head a5d3a767`（SBL 簽發＋owner 簽章） |

## 二、配對要求（升格後必須遵守）

**插件 `0.3.1-rc.1` 必須與 SBL `main ≥ 00f2722d` 一起使用。**

理由：插件的 `OriginalPipd` 要求 pin 集合與 reader 的 `src/pipd_ls_sp/**/*.py` ＋ `schemas/**/*.json`
逐檔相等。`operation_registry.py`（第 15 個模組）與 `cli.py`／`errors.py` 的變更都記在這個 pin 集合裡。
把新插件裝到舊 reader 上，會以 `ORIGINAL_READER_PIN_SET` 或 `ORIGINAL_READER_DRIFT` 拒絕——這是設計行為，不是故障。

| 組合 | 結果 |
|---|---|
| 0.3.1-rc.1 ＋ SBL ≥ `00f2722d` | 可用（本輪 Host 鏈已驗） |
| 0.3.1-rc.1 ＋ SBL < `a5d3a767` | 拒絕（pin 不符） |
| 0.3.0-rc.2 ＋ 任何 reader | 仍可用，但**不含**受信任 registry 載入與 owner  ratification 路徑 |

## 三、升格動作（本次實際執行）

1. 從**封存 ZIP**（非建置目錄）解包安裝到全新隔離 `CODEX_HOME` → `installed, enabled 0.3.1-rc.1`，
   並以一次 exec 讀回 `AGENT_PROMOTED 0.3.1-rc.1`。證明**被封存的那個位元組**就是被升格的那個。
2. 建立 `_archive/sbl-tpm-sp/CURRENT.json` 指標（機器可讀）：版本、SHA、範圍、配對 reader、回退指令。
3. 本文件寫入 SBL `evidence/pp261103/promotion/`，與既有 NO/YES 紀錄並存，不覆寫歷史。

## 四、明示不做

| 項目 | 原因 |
|---|---|
| 不動 Windows 現役 `~/.codex` 的 plugin cache | 該 host 的 MXC 沙盒無法建立子程序，未經本輪驗收；在此升格等於以未驗環境冒「已合格」 |
| 不宣稱硬化 sandbox | 容器以 `--security-opt seccomp=unconfined` 執行 |
| 不發 Grant／不改 Native 權限 | 升格只改變「預設使用哪個候選」，不改變效果權威 |

## 五、回退（單一指令級）

```bash
# 回到 0.3.0-rc.2（封存於同一目錄，SHA 3a9da65…）
codex plugin remove sbl-tpm-sp@<marketplace>
codex plugin add   sbl-tpm-sp@sbl-pre-primary-local   # 指向 rc.2 市場
```

回退後插件會回到「不接受 caller-supplied registry」之前的行為，因此**同時失去**本輪的受信任載入路徑；
若只是要排除新版問題，優先把 `0.3.1-rc.1` 換成同版重建，而不是退回 rc.2。

## 六、升格後的 Claim Ceiling

`DESIGN_ONLY`；`grant_state=NOT_GRANTED`；無 Native 效果、無 Live Checker、無 Publisher Release；
未生成 `FHS_PIPD-LS-PKG_v2` 主產包。升格≠Qualified。

---

## 七、本節補記：第一次升格安裝失敗（誠實揭露）

第一次「從封存 ZIP 安裝」的嘗試**失敗**，而且失敗方式值得記下來，因為任何重做的人都會撞到：

```
Installed plugin root: /codex-home/plugins/cache/sbl-pre-promoted/sbl-tpm-sp/local
sbl-tpm-sp@sbl-pre-promoted  installed, enabled  local    /promoted/plugins/sbl-tpm-sp
AGENT_PROMOTED No version field is present.
```

原因：封存 ZIP 的頂層目錄是 `sbl-tpm-sp/`，而 marketplace 期待的是 `plugins/sbl-tpm-sp`。
我把 ZIP 解到市場根目錄，於是 `plugins/sbl-tpm-sp` 只是一個**空目錄**，Codex 從中讀不到
`plugin.json`，版本顯示為 `local`，模型也就誠實地回答「沒有版本欄位」。

這不是成品缺陷，是我的 harness 佈局錯誤；修正為解到 `plugins/` 之後重跑，才有
`installed, enabled 0.3.1-rc.1` 與 `AGENT_PROMOTED 0.3.1-rc.1`。

**證據狀態**：`promotion_install.log` 是**成功那次**的完整輸出；第一次的原始 stdout 已被同路徑覆寫而遺失，
上面四行是逐字引自該次執行輸出，不以重製檔冒充。若日後要保留失敗軌跡，應在每次嘗試使用獨立檔名。
