# FHS W0 r7 —— 執行證據與候選產物

`round: FHS-W0-R6-EXEC-20261108` ｜ `claim_ceiling: W0_SIX_WP_MEASURED_WITH_SCOPED_HOLDS`

**這個目錄不是驗收，也不是發行。** 它是 W0 六個工作包的作者端實測與候選產物，供原域 Reader 接手判定。

## 這是什麼

| 路徑 | 內容 |
|---|---|
| `writeback/W0/FHS_PIPD-LS-PKG_W0_r7.md` | W0 回寫本文。r6 母本 481,212 bytes 逐位元保留＋追加 As-Built 章節 |
| `out/FHS_W0_R6_SESSION_EXECUTION_READY...` | 給外部驗收官的單一整合報告（六 WP 現狀／阻斷／自我錯誤／可重現指令） |
| `out/W0_WP_MATRIX.json` | 逐 WP 實測值與每個證據檔的 sha256 |
| `evidence/WP01/` | 31 檔 111,331 段 byte-exact 分割、84 個 DesignID 交叉表、權威衝突台帳、19 個 schema family 綁定 |
| `evidence/WP15/` | 三份 source-bound SPEC 草稿（Product／Architecture／Program）＋18 條 Stage 契約 |
| `evidence/WP16/` | 24 donor／25 method slot 投影，授權未陳述者一律 HOLD |
| `evidence/WP19/` | 三庫授權／NOTICE／SBOM／依賴／CI 盤點（含 3 處缺席） |
| `evidence/WP21/` | AC15／Oracle96／H4／SEAM 共 134 列可執行 oracle 計畫 |

## 明確不主張

- 不主張任何 WP 達到原域 `ORIGINAL_ACK`：收據數為 **0**。
- 不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`（仍為 `false`）。
- 不主張 Fabric policy 生效、Issuer 恢復、T2 或任何世界效果。
- 不主張三份 SPEC 是原 PIPD schema `$id`，或 49 個 slot 任一已核可採用。
- 不主張 134 列 oracle 已被保護檢查者判定（每列 `NOT_EXECUTED / RUNNER_UNBOUND`）。

## 如何複核

```bash
python tools/wp00_source_lock.py --out /tmp/SOURCE_LOCK.json     # 期望 31/31 + 上層 6/6
python tools/gstack_w0.py --round . --json /tmp/GSTACK.json      # 期望 15/15 PASS
```

`MANIFEST.json` 列出每個檔案的 sha256；兩份多 MB 的衍生表（U0/U1 全量）**不隨此處發佈**，改以 digest 記錄，可用 `tools/verify_u0_partition.py` 重建後比對。

## 層級

`NON_AUTHORITATIVE_TO_SBL_READER`。產品語義仍由 SBL Product Reader 判定；此目錄不授權任何寫入或發行。
