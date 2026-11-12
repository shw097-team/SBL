# WP-FHS-19 供應鏈掃描摘要（SOURCE_READ）

- 產生時間：2026-11-07T16:43:25Z（UTC）
- 工作包：WP-FHS-19；effect class：SOURCE_READ
- 主張上限：`SOURCE_READ_INVENTORY_ONLY`

## 一、逐 repo 對照表

| Repo | HEAD | Licence | NOTICE | SBOM | 依賴宣告 | Workflow | CI 判定 |
|---|---|---|---|---|---|---|---|
| Fabric | `d75e97654279` | ABSENT | ABSENT | ABSENT | 6（選用 0／lock 0） | 1 | GREEN_NO_SUPPLY_CHAIN_JOB |
| SBL | `47d4e600dd9b` | LICENSE MIT | present | integrations/pipd/SBOM.cdx.json CycloneDX 1.5 components=8 unsigned | 3（選用 9／lock 6） | 1 | SUPPLY_CHAIN_JOB_GREEN_AT_READBACK |
| HG-KSEOS | `a7046a36956e` | ABSENT | ABSENT | SBOM_PRESENT_NOT_CYCLONEDX | 0（選用 0／lock 0） | 0 | CI_SERVICE_ABSENT |

CI 判定用語（識別碼保留英文）：
- `SUPPLY_CHAIN_JOB_GREEN_AT_READBACK`：該 repo 的 CI 有 supply-chain job，且回讀到的結論為 success。
- `GREEN_NO_SUPPLY_CHAIN_JOB`：CI 綠燈，但工作內容與授權／SBOM／依賴無關，因此不能當作供應鏈證據。
- `CI_SERVICE_ABSENT`：沒有 workflow 檔、沒有 run、沒有 check run——這是缺席，不是通過。

## 一之二、SBOM 與依賴宣告的實測細節

- SBOM.cdx.json 的 8 個 component 全部沒有 hashes 欄位：SBOM 內沒有任何雜湊，因此無法用它驗證任何一個相依套件的位元組。
- 其中 5 個 component（pyyaml、build、setuptools、wheel、pytest）版本為字面值 'UNPINNED'，即文件自承未釘版。
- 文件的 properties 自述 scope 為 'declared python dependency set only (no transitive closure computed)'：它宣告的是直接依賴集合，不含遞迴閉包，因此不是一份完整 SBOM。
- 全檔沒有 signature 成員，也沒有簽署者或 transparency log 資訊。

依賴宣告來源（宣告數／範圍）：
- Fabric：declared=6（root 0、nested 6）、optional=0、lock pins=0、hash_pinned=False、root manifest=False
- SBL：declared=3（root 0、nested 3）、optional=9、lock pins=6、hash_pinned=False、root manifest=True
- HG-KSEOS：declared=0（root 0、nested 0）、optional=0、lock pins=0、hash_pinned=False、root manifest=True

## 二、缺席面（明列，不略過）

- Fabric：repo 根層 LICENSE 與 NOTICE 皆缺席
- HG-KSEOS：repo 根層 LICENSE 與 NOTICE 皆缺席
- Fabric：沒有任何格式的 SBOM 文件
- HG-KSEOS：CI_SERVICE_ABSENT——無 workflow 檔、0 個 workflow run、0 個 check run
- Fabric：CI 只有一個 job（fhs-nav-static），沒有 supply-chain job
- 三個 repo 皆無：簽章 SBOM、provenance attestation、SLSA statement
- 三個 repo 皆無：弱點／advisory 掃描（本 lane 未執行）

## 三、這份掃描證明什麼

- 三個 repo 各自存在哪些 licence／notice／SBOM／workflow 檔案，附位元組數與 sha256，後續任何關於這些檔案的主張都可以對回摘要值。
- 存在哪些 SBOM 文件，以及每一份是否解析成功、是 CycloneDX 還是 SPDX、spec 版本為何、實測 component 數為何。
- 存在哪些依賴宣告、出自哪個檔案、各自貢獻幾行。
- 存在哪些 workflow 檔、宣告哪些事件、定義哪些 job，以及 GitHub 回報的最新 run 與 main head 上的 check run——含 run id 與 job 層級結論。
- 三個 repo 中有兩個在根層沒有授權檔、一個完全沒有 CI 服務；這些都以明列的缺席呈現，而不是靜默略過。

## 四、這份掃描不證明什麼

- CI 綠燈不是供應鏈 attestation。它只證明被點名的 job 在被點名的 commit 上退出碼為 0；對於建置輸入是什麼、由誰產生、SBOM 與出貨產物是否相符，它什麼都不證明。
- 解析成功不是簽章。SBOM.cdx.json 解析成功並列出 8 個 component，但它沒有簽章、沒有簽署者身分、也沒有 transparency log 紀錄，因此其真實性與完整性未經證實。
- component 數是「文件列了幾個」的計數，不是與已安裝環境或 wheel 的對帳。這裡沒有任何一步把 SBOM 與解析後的 lock、或與 SBOM 所描述的產物做比對。
- workflow 的觸發事件與 job 是以行／縮排掃描取得，不是 YAML 解析：若 workflow 使用 anchors、merge keys 或多文件語法，會被讀漏。
- 根層沒有 LICENSE 是量測結果，不是法律結論：它既不授予也不否認權利，也不代表 owner 的意圖。
- 沒有做弱點掃描、沒有查 advisory、沒有驗證 provenance（SLSA／in-toto）、沒有驗簽，也沒有做 release qualification。
- 即時 CI 回讀是帶 token 的 REST 讀取，不是 original CI reader ACK：沒有取得 job log、沒有 artefact digest、也沒有 runner attestation。

## 五、可重現指令

```sh
cd C:/Projects/Agent_Workspace/FHS_W0_R6_20261108/evidence/WP19
python scripts/wp19_scan.py     # 本地檔案盤點 + sha256
python scripts/fetch_ci.py       # 以 curl -K 讀 GitHub API，token 不進 argv
python scripts/build_reports.py  # 由 raw 產生六份交付物
```

## 六、原始證據位置

- `raw/<repo>/scan.txt`：逐 repo 的平面掃描紀錄（LICENCE／NOTICE／SBOM／DEP／CI，每行一筆，含 sha256）
- `raw/<repo>/tracked_files.txt`：`git ls-files` 全量清單
- `raw/<repo>/git_head.txt`：HEAD、分支、remote、最後 commit
- `raw/<repo>/api/*.json`：GitHub REST 原始回應（含 HTTP 標頭檔）
- `raw/_local_scan.json`：本地掃描的完整結構化輸出
- `raw/_api_fetch_meta.json`：取證後設資料（token 未落地殘留、config 已刪除）
