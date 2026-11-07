# WP-FHS-15｜TPM corpus 與三份 SPEC（作者端草稿）

宣稱上限：`AUTHOR_SIDE_SPEC_DRAFT_SOURCE_BOUND`。
本目錄不是 Owner SourceFreeze，不是原 PIPD schema `$id`，不帶 Original Reader ACK，不產生任何世界效果。
DonePredicate：`original three SPEC drafts + source readback + FUO ten columns`。

## 目錄

| 路徑 | 內容 |
|---|---|
| `specs/product_SPEC.md` / `.json` | PM 視角：persona／JTBD／FUO 十欄／差額驗收 |
| `specs/architecture_SPEC.md` / `.json` | SE 視角：五 seam／ADR／EffectClass／SoD NEG |
| `specs/program_SPEC.md` / `.json` | TPgM 視角：22 WP／36 邊／wave／stop-resume |
| `stages/STAGE_CONTRACTS.json` | 18 個 stage 契約（PM/SE/TPgM × T0–T5），逐列帶來源 span |
| `evidence/firstfail_codes.json` | 每個 firstfail code 在 W0 r6 的出現行與 span |
| `evidence/dag_check.json` | 22 WP／36 邊的實測結果（拓撲排序） |
| `evidence/*.log` | 三支檢查器的實際 stdout |
| `REPORT.json` | `FHS.WP15.Report/1`：計數、artifact 雜湊、命令、holds、not_claimed |

## 重現（三條命令）

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R6_20261108/evidence/WP15
python tools/verify_spans.py        # 重讀每個被引用檔、重切 span、比對 quoted_text；任一 FAIL 即 exit 1
python tools/spec_distinctness.py   # 三份 body 兩兩相似度 <= 0.85；consumer/NEG 集合互斥；16 欄與 FUO 十欄完整
python tools/negative_controls.py   # 注入三種故障，證明上面兩支檢查器真的會失敗（非空轉）
python tools/verify_dag.py          # 22 WP／36 邊／無環（Program SPEC 的 POS oracle）
```

`tools/build_wp15.py` 是產生器：所有 span 由 anchor 在真實 bytes 中定位後計算，不手打；
`tools/finalize_report.py` 重跑三支檢查器並寫出 `REPORT.json`。

## 已知差額（不補寫、不美化）

- W0 r6 CH-11 只宣告「18 Stage」這個**數量**，章內沒有任何 stage 列（全文 `PM:T0|SE:T0|TPgM:T0` 命中 0）。
  18 列的實質契約只存在於 `02_PIPD_LIFECYCLE_AND_TPM(4).md` 的 STATIC-v1 表（第 38–55 行）。
  本輪以來源量測計數 18，並記 `H-WP15-STAGE-ENUMERATION-GAP`。
- 三份 SPEC 的 `subject_id` 是作者端示例鍵 `FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001`，
  綁定狀態 `AUTHOR_W0_DEMO_SUBJECT__ORIGINAL_PIPD_UNBOUND`；不是既有 canonical SubjectID。
- 本次取代了先前輪次的兩個佔位：Architecture SPEC 470 chars、Program SPEC 385 chars
  （見 `FHS_W0W2_R4_20261107/evidence/E_docs/WP15_WP16_SPEC_INVENTORY.json`）。
