# CT-05 收口：真舊版 rc.1 在 Codex Host 載入，再恢復 rc.2

**Host**：linux container（Debian 12 / kernel `6.6.87.2-microsoft-standard-WSL2` / image `node@sha256:18a6d90f…`），`codex-cli 0.164.0`，sandbox `RUNTIME_SECCOMP_UNCONFINED`（限制已於前輪登載，未新增 Gate）。
**同一 `CODEX_HOME`**：`far/container/codex-home`（現役 `~/.codex` 未動）。

## 版本身分（真封包，非捏造）

| 版本 | 來源 | ZIP SHA256 | plugin.json SHA256 | Skills |
|---|---|---|---|---|
| rc.1 | `_candidate_sbl_tpm_sp_20261102/input/sbl-tpm-sp-0.3.0-rc.1-private-final.zip` | `c4181e247e13905b565bb53938d153c4c719fd65c34cc12d7f11d13c761f8f86` | `246efaf455d9bfae…` | 14 |
| rc.2 | `shadow/codex-case`（既有候選） | `3a9da65561ab19cad90a6d7cbfb2eae0abf59b87ba565a118790bce5612326a8` | `48d704bcb0a175ba…` | 14 |

## Stage A — 舊版真的被 Codex 載入並使用

```
codex-cli 0.164.0
Added plugin `sbl-tpm-sp` from marketplace `sbl-pre-old-local`.
Installed plugin root: /codex-home/plugins/cache/sbl-pre-old-local/sbl-tpm-sp/0.3.0-rc.1
sbl-tpm-sp@sbl-pre-old-local  installed, enabled  0.3.0-rc.1  /old/plugins/sbl-tpm-sp
"version": "0.3.0-rc.1"                       ← cache 內 plugin.json 實值
codex exec … 「只讀 /codex-home/plugins 的 plugin.json，回版本字串」
  CMD sed -n '1,40p' /codex-home/plugins/cache/sbl-pre-old-local/sbl-tpm-sp/0.3.0-rc.1/plugin.json   exit 0
  AGENT 0.3.0-rc.1
  TURN_COMPLETED
```

## Stage B — 恢復 rc.2 並再次被載入

```
sbl-tpm-sp@sbl-pre-primary-local  not installed        ← 舊版已不在
Added plugin `sbl-tpm-sp` from marketplace `sbl-pre-primary-local`.
Installed plugin root: /codex-home/plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2
sbl-tpm-sp@sbl-pre-primary-local  installed, enabled  0.3.0-rc.2
"version": "0.3.0-rc.2"
codex exec … 同問題
  CMD cat /codex-home/plugins/cache/sbl-pre-primary-local/sbl-tpm-sp/0.3.0-rc.2/plugin.json  exit 0
  AGENT 0.3.0-rc.2
  TURN_COMPLETED
```

## 為什麼這不是「卸裝同一版就當回退」

- 舊版是**真封包**（ZIP SHA 與 `plugin.json` 版本、雜湊都可獨立核對），不是改字串或複製目錄。
- 兩次 `exec` 都由模型**自己讀取 cache 內的 `plugin.json`** 並回報版本，等於 `Loaded` 之後的 `Used` 讀回，而不是只信 `plugin list`。
- 版本序列為 `rc.2 → rc.1 → rc.2`，兩個方向都有 `installed, enabled` 與 `AGENT` 版本字串。

## 前一次失敗（保留，不隱藏）

第一次嘗試只 `remove` 了 rc.2，卻沒有把 `sbl-pre-old-local` 市場寫進 `config.toml`，因此 rc.1 **從未安裝**；該次 exec 讀到的是掛載的 `/market`，回報 `0.3.0-rc.2`，屬無效證據。已改為兩個獨立 run（各只掛一個市場）重做，`ct05_rollback.log` 保留為失敗軌跡。
