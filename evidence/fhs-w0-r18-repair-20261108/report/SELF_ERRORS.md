# 本回合自我錯誤（r12）

## E-S18｜我的閘有 16/16 可以在沒有證據時通過——紅隊證明了它

**做了什麼**：r11 之後我以為「三個假綠路徑已封」。車道以攻擊者視角對 16 項各試一次：**20/23 次攻擊在無證據下取得 PASS，16/16 檢查全被攻破**（3 個負控正確被拒，所以問題不在測試工具）。

**最嚴重的一項**：`G21`。交接寫 `1,234 B` 加一個不屬於任何檔的 sha，manifest 的 `shipment` 寫同一組錯值——兩者互為印證，閘印出「with a matching digest」。而那個 digest 不是該檔的 sha（實測 207 B / `517fc7…`）。

**根因（同一個病的第四種形態）**：`G13` 讀不存在的鍵、`G18` 空集合 0/0、`G16` 把一棵樹的事實凍成規則、`G21` **拿產物比產物**。檢查一直是「artifact A 與 artifact B 一致」，而 A 與 B 都是我在同一次執行裡寫的。一致什麼都不證明。

**最弱的不是某一項，是其中一個 profile**：`--profile payload`（就是 CI 跑的那個）下，`G16a` 的 `metadata_sha256` 是 `{}`，比對量化在空集合；`G16b` 把每個 subject 丟進 `not_here` → **分母為零，永遠綠**。我上一輪還把「CI 真的跑閘」當成主要成果。

**規則**：**檢查必須重算，不能對照。** 閘要 reopen 原始 bytes（31 冊原檔、文件本身、payload 檔案、pyproject），而不是讀另一份產物。

---

## E-S19｜修完一項就宣告勝利，是我這一連串回合的固定錯誤

**模式**：r9 修 `G13/G16/G10` → 宣告；r10 被指出 `G18/G16b/G16c` → 修 → 宣告；r11 被指出三條 profile 路徑 → 修 → 宣告；r12 紅隊再把 16 項全破。

**代價**：四輪的外部驗收，每一輪都在修上一輪修出來的檢查，而不是把「檢查怎麼才算有證據」這件事本身定下來。

**規則**：**新增一項檢查，必須同時附上「它怎麼被無證據通過」的嘗試**。沒有攻擊紀錄的檢查不算交付。本回合已把 `G11`、`G18`、`G16a`、`G16b`、`G21` 五處改成重算，並用紅隊的原始 fixture 回放驗證（`G11` → `LINE_RECORD_WITHOUT_NUMBERS`、`G18` → `EXPECTED_SET_DISAGREES_WITH_DISK`）。

---

## E-S20｜我把「owner 授權」與「owner 選擇」混在一起

**做了什麼**：收到「OWNER 正式裁決，授權你修補」。有一瞬間的誘惑是把八項 owner 待辦全部標成 CLOSED——因為「owner 說可以」。

**但我不能**：授權的是**行動**，不是**事實**。`ORIGINAL_ACK` 需要原域 Reader 的簽名，我寫一張就是偽造收據；`PIPD-15-VALUESET` 是產品語義，我編一組就是捏造需求；`LICENCE` 是法律行為。

**處置**：`out/OWNER_RULING_W0_R12.json` 把每一項的**授權等級**分開寫：`MAKER_DECISION_UNDER_OWNER_AUTHORISATION`（可決定）、`TAKEOFF_REFUSED`（不接）、`NOT_A_MAKER_DECISION`（不是我能決定的）、`OUT_OF_SCOPE_BY_NATURE`（授權也做不到）、`REQUIRES_PROTECTED_TERMINAL`（要開窗）。

**規則**：**每一項裁決都要標明它自己的權威來源。** 一份沒有分級的「全部已解決」清單，就是這個堆疊最擅長製造的那種文件。

---

## E-S21｜HG-KSEOS 的修補我停手了，理由寫在裁決檔裡

**做了什麼**：本來要對 HG-KSEOS 開 branch＋PR 修 `cryptography` 依賴。讀了該 repo 的 `AGENTS.md`：**「Do not push, merge, deploy, access secrets, broaden permissions」**。

**判斷**：那是該 repo 的不變量，不是我的偏好。這次授權是對 W0 回合的，不是對另一個控制平面開的通行證。所以修補維持 `PATCH_VERIFIED_NOT_APPLIED`，並在裁決檔記明「需要一條指名 HG-KSEOS 的 owner 指令」。

**規則**：**broad authorization 不等于 blanket permission。** 别的 repo 的自訂規則優先於我的方便。
