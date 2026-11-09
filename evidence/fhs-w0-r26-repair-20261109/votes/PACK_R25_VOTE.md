# FHS W0 受影條款重讀投票包（r25）

## 你要做的一件事
針對下面兩個「受影條款」，各自回答一個是非題。你只讀，不改檔，不寫任何東西。
每一題都必須給 `true` / `false` / `UNKNOWN` 之一，並附一句不超過 40 字的理由。
`UNKNOWN` 代表你讀完後仍無法判定——不要為了湊票而猜。

## 題目 1：WP-FHS-00:L1:817，性質 `exceptions_preserved`

**原文（L1 藍圖第 817 行，節錄）**
```
| FHS-DR-020 | ...／r4:L39–74 | 資料與來源／A | 來源 Currentness 由原有權 Reader 讀回 |
SourceBytesSHA≠Owner EffectiveRevision；unknown→affected HOLD | [CH-04] |
SBL Original Source/Requirement/Corpus Semantic Reader | 新舊版本衝突不會被靜默覆蓋 |
作者端 SHA 自封 OWNER_CURRENT_CONFIRMED | MANDATORY_SPEC_AND_NEG；CONDITIONAL_EFFECT_ONLY | OWNER_READER_ACK_PENDING |
```

**候選（FHS_PIPD-LS-PKG_W0_r24.md）在該條款的三處落地**
```
415: | `FHS-DR-020` `L1-r4:L817` | W0 | SBL Original Source/Requirement/Corpus Semantic Reader | 新舊版本衝突不會被靜默覆蓋 | 作者端 SHA 自封 OWNER_CURRENT_CONFIRMED；`DESIGN_OBLIGATION_MISSING`（若失卡） |
603: | `FHS-DR-020` `L1-r4:L817` | `W0_REQUIRED` | W0/`WP-FHS-00` | 資料與來源／A；來源 Currentness 由原有權 Reader 讀回；SourceBytesSHA≠Owner EffectiveRevision；unknown→affected HOLD；[CH-04](#ch-04) | SBL Original Source/Requirement/Corpus Semantic Reader | 新舊版本衝突不會被靜默覆蓋 | 作者端 SHA 自封 OWNER_CURRENT_CONFIRMED；`DESIGN_OBLIGATION_MISSING`（若失卡） |
3559: | `FHS-DR-020` | L817 | `MANDATORY_SPEC_AND_NEG；CONDITIONAL_EFFECT_ONLY` | `db25b1ada1312254` |
```

**問題**：候選是否保存了原文的 **例外條件（exception）**——特別是
「`SourceBytesSHA≠Owner EffectiveRevision`」與「`unknown→affected HOLD`」這兩個必須保留的例外／停止條件，
且沒有把它們改寫成無條件通過？

## 題目 2：WP-FHS-01:L1:812，性質 `scope_preserved`

**原文（L1 藍圖第 812 行，節錄）**
```
| FHS-DR-015 | ...／r4:L74–109 | 資料與來源／A | 每個原 Parent/Child/NEG/Exception/Applicability 必保存 |
Source span/Parent Context/OriginalID/OriginalOwner/Consumer Crosswalk | [CH-03]/[CH-27] |
SBL Original Source/Requirement/Corpus Semantic Reader | 每個原 ID 有候選或具名 HOLD |
原字串關鍵字命中代 SOURCE_TRACE_PASS | MANDATORY_SPEC_AND_NEG；IF_TRIGGERED_OR_AFFECTED_SCOPE | OWNER_READER_ACK_PENDING |
```

**候選的落地**：`FHS-DR-015` 在 `W0_REQUIRED` 交叉表中由 `WP-FHS-01` 承接，
範圍限定為 `IF_TRIGGERED_OR_AFFECTED_SCOPE`（觸發或受影才適用），並要求
「每個原 ID 有候選或具名 HOLD」，反例為「原字串關鍵字命中代 SOURCE_TRACE_PASS」。

**問題**：候選是否保存了原文的 **適用範圍（scope）**——也就是
「`MANDATORY_SPEC_AND_NEG` 搭配 `IF_TRIGGERED_OR_AFFECTED_SCOPE`」這個有條件的範圍，
而沒有把它擴大成「所有 WP 一律必做」或縮小成「可選」？

## 輸出格式（只輸出這一個 JSON，不要其他文字）
```json
{"lane":"PLAN|VERIFY","arm":"<你被指派的 lane 名稱>","read_source_bytes":true,
 "votes":[
  {"clause_id":"WP-FHS-00:L1:817","property":"exceptions_preserved","vote":true,
   "reason":"<=40 字","evidence_lines":"415,603,3559"},
  {"clause_id":"WP-FHS-01:L1:812","property":"scope_preserved","vote":true,
   "reason":"<=40 字","evidence_lines":"<你實際引用的候選行號>"}
 ],
 "notes":"<=60 字，可寫你認為還缺什麼"}
```
`vote` 只能是 `true`、`false` 或 `"UNKNOWN"`。整體以 `FHS_VOTE_OK` 結尾。
