# FHS W0｜r9 草案的收斂性驗收（Convergent Acceptance）

> **對象**：外部驗收官、原 Maintainer、下一個 session。
> **一句話**：把 `FHS_PIPD-LS-PKG_W0_r9` 當草案，對它「把前輪十個缺陷修進工具」的主張做收斂性驗收。**十項裡四項真正關閉、三項關閉但帶漂移、三項不成立或只能由 owner 收**；另外量到**八項新缺陷**，其中三項是 HIGH，而且三項都指向同一個病：**判決說的不是它名字說的事**。原域 Reader 收據仍是 **0**。
> **ClaimCeiling**：`AUTHOR_SIDE_MEASURED_WITH_SCOPED_HOLDS`。不主張 `ORIGINAL_ACK`、`NATIVE_WORLDRAW`、`INDEPENDENT_PASS`、`RELEASE_GRANTED`、已併、已審、已發行。

| 事實 | 值 |
|---|---|
| 被驗對象 | `FHS_PIPD-LS-PKG_W0_r9`（552,605 B，sha256 `c15693d8…`），r8 逐位元為其前綴 |
| 收斂範圍 | 前輪點名的十項：`V-01`…`V-07`、`A-01`…`A-03` |
| 逐項判定 | 4 CLOSED｜3 CLOSED_WITH_DRIFT｜3 HOLD/NOT_CLOSED |
| 新缺陷 | 8（3 HIGH、4 MED、1 LOW） |
| 閘 | 繼承 16/16；新增 10/10；對前輪 2/6/2；selftest 10/10 FIRED；我自建磁碟注入 4/4 命中且零連帶 |
| 原域 ACK | **0** |
| 對三庫寫入 | 0（`HG-KSEOS` 有 2 個 untracked 檔，早於本回合與 r9） |
| Owner 簽章需求 | 0（未開窗；信封與 `owner_prompt.py` 已定位） |

---

## 1｜怎麼驗的：三條互不採信的證據線

| 線 | 做什麼 | 能主張 | 不能主張 |
|---|---|---|---|
| 母代理 | 自寫程式直接從原始 bytes 重算 31 檔、r9 結構不變量、閘重跑、**在磁碟上**注入缺陷 | `AUTHOR_SIDE_MEASURED` | 不是原域 Reader |
| 五條 SWARM 車道 | 各自獨立重導 `V-01/V-03`、`V-04/V-07`、`V-02`、`V-06/A-01/A-03`、閘鑑識；各寫自己的目錄、無憑證 | `AUTHOR_SIDE_INDEPENDENT_REDERIVATION` | 不能 push、不能自簽判決 |
| GSTACK | 不信任何自報：重算 digest、重切 span、對帳計數 | `GATE_VERDICT` | 綠燈不是驗收 |

**反偽造**：車道報的每一個「重現」，母代理都用**不同寫法**再算一次；對不上的以母代理為準並記錄。本回合三次出現這種不一致（`V-02` 的 0.2454 vs 0.2679、`V-06` 的 8 vs 0、`A-01` 的「已宣告」vs「空清單」），三次都不是算錯，而是**量在不同的東西上**。

---

## 2｜十項逐項判定

| ID | r9 的主張 | 本回合判定 | 實測 |
|---|---|---|---|
| `V-01` | 工具化；canonical 留 owner | **HOLD**（owner） | r6 是**三份**不是兩份：`FHS_W0W2_R4_20261107/writeback`、`worktrees/r4-fabric/…/as-built/W0/`、知識庫。副本登記簿的 root 清單漏了 `worktrees/` |
| `V-02` | CLOSED，`max_overall=0.245432` | **CLOSED_WITH_DRIFT** | 缺陷真的修好（0.0755 已降為子欄值）。但數字綁方法：我算 0.267852（char-5gram），車道五族最大 0.368972（tf-idf）。文件說「等於八個分解值的最大」，矩陣其實是 5 族×3 對＝15 值 |
| `V-03` | CLOSED，0／0／17 | **CLOSED** | 以更寬的 root 重導仍成立：in-set 0、精確同名 0、剝尾碼 17；282 筆同名列全部重雜湊 |
| `V-04` | CLOSED，111,331／25,201 | **CLOSED_WITH_DRIFT** | 兩數都真、兩規則都 31/31 貼齊。但 25,201 **只能**用他們的 fence-aware 分類器重現；照公開文字實作會得 23,692～26,080（我試的四種讀法；工具內建 naive 讀法給 26,078）／25,602（車道） |
| `V-05` | CLOSED ＋ 加 G18 | **CLOSED**（記錄漂移） | 34/34 digest 在自身 payload 內解析。但同一件事在三個地方有三個值：`GATE_R9.json` 27/27、報告 26+1、現樹 34/34 |
| `V-06` | CLOSED，SBL 2／Fabric 6／HGK 8 | **HOLD**（HIGH） | 全部 ref 相依。SBL 2 成立；Fabric 5（嚴格）或 6（多加「LICENSES/ 目錄」規則）；**HGK 在兩個受審 HEAD 上都是 0**，8 只存在於另兩條分支 |
| `V-07` | CLOSED，verdict 需三欄 | **CLOSED** | 31/31 bytes+lines+sha 全真；宣告 111,331＝實測 111,331；`split('\n')` 的 111,362 是每檔多一個尾空元素 |
| `A-01` | 「前輪兩處都錯」；patch 已驗證未套用 | **NOT_CLOSED**（HIGH） | 這是**跨兩棵樹的比較**，見 §3。在 `worktrees/r4-hgk` 上前輪的敘述逐字成立；缺陷仍在（patch 未套用） |
| `A-02` | CLOSED，naive 10／robust 11 | **CLOSED_WITH_DRIFT** | 列舉正確（11）。但那個「naive」是特指**以 `/` 當欄位分隔**的解析器；普通的 `\b(SEAM-\d{2})\b` 一樣得 11 |
| `A-03` | CLOSED，離線／hosted 分離 | **CLOSED** | `--self-test` exit 0、baseline PASS、3/3 mutation 被拒；hosted 維持 `NOT_OBSERVED`，沒有假造 run id |

**「8 of 10 closed」不成立**：逐項是 4／3／3。這個差別不是記帳問題——**三項 HOLD 剛好就是三項牽涉「第二棵樹」的**，把它們平均掉，正好把本回合最重要的發現平均掉。

---

## 3｜三項 HIGH：判決說的不是它名字說的事

### `N-01`｜`G16` 在自己的 detail 寫 `False`，仍給 PASS；而且把某一棵樹的事實凍結成規則

```
G16 DECLARED_COVERS_IMPORTS  PASS
detail: hgk: undeclared=['yaml']; declared_covers_imports=False
```

`gate_w0r9.py:350-372` 的語意是「artifact 誠實回報未宣告集合就給過」，所以 `False` 是**通過條件**。名字與判決表卻讓讀者讀成「宣告已覆蓋 import」。更嚴重的是這一段：

```python
if "cryptography" in und:
    return False, "CRYPTOGRAPHY_FALSELY_MARKED_UNDECLARED", \
        "the artifact repeats the previous round's claim that cryptography is undeclared; pyproject declares cryptography>=42"
```

**它把「cryptography 已宣告」寫成規則。** 在 `worktrees/r4-hgk`（`dependencies = []`）上，**正確的量測會被這條規則判紅**。閘不是檢查事實，是檢查你有沒有複述它的結論。

### `N-02`｜`G13` 是死斷言：閘讀的鍵，artifact 從來不寫

```
gate:     inb.get("duplicate_digest_groups", inb.get("duplicate_digests"))
artifact: "duplicate_sha256_groups": 0
```

把真正的欄位改成 `4`，閘照樣 `PASS "in-set dup=0"`。這與 `V-07` 是同一形狀：**判決與它所引用的欄位無關**。r9 說 V-07 已關，但同一形狀在新加的第 13 項上原樣重演。

### `N-03`｜`G10` 解析的是文件裡某個舊章節的宣告，不是這份文件自己的宣告

r9 的鏈是 `r5 → r6 → r7 → r9`：**r8 根本不在鏈上**，而 `G10` 印出的「declared parent `264787b0`」是 r9 內嵌的 r7 章節寫的。r9 自己在 front matter 宣告的父本 `ccd545b5`（r8）**從未被檢查**。

文件本身沒問題——我逐位元驗過 r9 的前 539,712 bytes 等於 r8。問題是**閘給的保證是假的**：它保證的是別人的宣告。

---

## 4｜樹身分：兩棵 HG-KSEOS，兩個相反的答案

| | `HG-KSEOS`（r9 量這棵） | `worktrees/r4-hgk`（前輪量這棵） |
|---|---|---|
| HEAD | `6c9fc73`（2026-11-03） | `a7046a3`（2026-11-06，`#13`/`#14` 之後） |
| `pyproject.toml:6` | `dependencies = ["cryptography>=42"]` | `dependencies = []` |
| `src/hg_kseos/fhs/issuer_binding.py` | **不存在** | **存在** |
| `cryptography` 出現處 | 2 個模組 | 3 個模組，其中 `user_trust.py:30-31` 是**模組層無保護 import** |
| `fhs_msc_handoff_20261030/WP-FHS-17/` | 存在（8 個授權檔） | 不存在 |
| 兩者關係 | `git merge-base --is-ancestor` → **互不為祖先** | |

前輪說「3 個模組 import cryptography，而 pyproject 宣告 `[]`」——在 `r4-hgk` 上**逐字成立**。
r9 說「已宣告、`issuer_binding.py` 不存在」——在 `HG-KSEOS` 上**逐字成立**。
**兩句都真，比較是假的。** r9 把它寫成「前輪兩處都錯」，並用這個結論寫進 `G16` 的規則。

**未宣告集合**：在 `r4-hgk` 是 `{cryptography, yaml}`（r9 只報 `yaml`）。`yaml` 在 `lane_policy.py:71` 是函式內 lazy、`except: return None`——**靜默**，不是 fail-closed：全新安裝時重複 key 檢查直接消失。

---

## 5｜六個 W0 主責 WP 的現狀

| WP | r9 自述 | 本回合 | 依據 |
|---|---|---|---|
| `WP-FHS-00` | `MEASURED_REPAIRED` | **PASS**（`SOURCE_READ`） | 31/31 bytes+lines+sha；22,281,767 B；`count("\n")`=111,331（我自算） |
| `WP-FHS-01` | `MEASURED_REPAIRED` | **PASS** | 84 卡（24 INT＋60 FHS-DR）、22 個 `W0_REQUIRED`、兩規則 31/31 貼齊 |
| `WP-FHS-15` | `MEASURED_REPAIRED` | **PASS_WITH_DRIFT** | 3 份相異 SPEC、15 ACC、18 Stage；相似度上限隨方法 0.2454～0.3690 |
| `WP-FHS-16` | `MEASURED_UNCHANGED` | **CARRIED_NOT_RE_MEASURED** | 本輪缺陷無一落在此，未重跑（不假裝驗過） |
| `WP-FHS-19` | `MEASURED_REPAIRED` | **HOLD** | 授權數 ref 相依；`A-01` 缺陷仍在 |
| `WP-FHS-21` | `MEASURED_REPAIRED` | **PASS** | AC15 15、Oracle96 **96＝12×8**（我從原檔自算）、H4 12、SEAM 11 |

其餘 16 個 WP（`02`–`14`、`17`、`18`、`20`）主波在 W1–W4，**本回合一個都沒量，也不對它們主張任何事**。

---

## 6｜閘的實測

| 情境 | 結果 |
|---|---|
| 繼承 16 項（`gate_w0r7.py`，object=r6，chain child=r9） | **16/16 PASS**，exit 0 |
| 新增 10 項（`gate_w0r9.py --round .`） | **10/10 PASS**，exit 0；digest 34/34（記錄是 27/27） |
| 對前輪產物（`--prior ../FHS_W0_R6_20261108`） | **2 PASS／6 FAIL／2 n/a**，exit 1 |
| `--selftest` | **10/10 FIRED**，但 **exit 0**（HANDOVER 寫 exit 1） |
| **我的磁碟注入** | M1 改 `lines_match`→紅 G11；M2 壓 `max_overall`→紅 G14；M3 把兩規則合成一數→紅 G12；M4 `seam=10`→紅 G17。**各自只紅自己、零連帶**，還原後回 10/10 |
| 空載荷（複製時排除 `stage/`） | **G18 FAIL、exit 1** —— fail-closed 行為正確 |

**閘確實會咬，但咬的不是名字說的那件事**：`G13` 咬不到（死斷言）、`G16` 咬反（正確量測被判紅）、`G10` 咬錯對象。

---

## 7｜明確不主張

- 不主張任何 WP 達到 `ORIGINAL_ACK`：六個 WP 的原域 Reader 收據仍為 **0**。
- 不主張 `W0_W1_W2_ALL_APPLICABLE_ORIGINAL_WP_DONE=true`。
- 不主張 Fabric policy 生效、Issuer 恢復（registry 仍 rev 13 `3254714b…`）、任何 Permit、任何世界效果。
- 不主張 `HG-KSEOS` 兩棵樹之中哪一棵是 canonical；只主張兩棵都存在、互不為祖先、對同一行給出相反答案。
- 不主張 25,201 是「語意分割數」；它是 `RULE_STRUCTURAL_BLOCK` 在特定分類器下的塊數。
- 不主張 r9 的十項修補無效：四項確實關閉，三項關閉但帶漂移。
- 不主張兩個 PR 已併、已審、已發行。

---

## 8｜一份 OWNER 待辦（不逐一回頭問）

| # | 待辦 | FirstFail | 需要什麼 | Resume |
|---|---|---|---|---|
| 1 | `R1-ISSUER-REV14` | `REGISTRY_REV13_NO_ISSUER_RECOVERY` | rev 14 registry＋31 列與 root 簽章 | 受保護終端開窗（`owner_prompt.py`）後執行 issuer |
| 2 | `AUTHORITY-COLLISIONS` | `NAME_COLLISION_DIFFERENT_DIGEST` | r6 的權威 digest（**三份**，非兩份） | 指名後重跑副本登記簿 |
| 3 | `HGK-REF-CANONICAL` | `TWO_CHECKOUTS_DIFFER` | `HG-KSEOS@6c9fc73` 與 `r4-hgk@a7046a3` 哪個是 W0 基準 | 指名後重測 `A-01`／`V-06` |
| 4 | `LICENCE-FABRIC-HGK` | `LICENCE_ABSENT_AT_ROOT` | 兩庫根層授權決定 | 根層 LICENSE/NOTICE 存在 |
| 5 | `HGK-CI-ABSENT` | `CI_SERVICE_ABSENT` | 是否建 CI | 有 workflow 或明示不建 |
| 6 | `HGK-DEPENDENCY-EXTRA` | `UNDECLARED_DEPENDENCY` | 在 `r4-hgk` 上補 `cryptography` 與 `yaml`（或改回宣告） | patch 套用並重跑覆蓋檢查 |
| 7 | `PIPD-15-VALUESET` | `CONTRACT_FAMILY_VALUE_SET_UNCLOSED` | 15 個 family 的 value-set | 閉合且 schema 綁定 |
| 8 | `ORIGINAL-ACK-18` | `ORIGINAL_READER_ACK_UNOBSERVED` | 任一原域 Reader 的同 scope ACK/NACK | 收據落地 |

---

## 9｜可重現指令

```bash
cd C:/Projects/Agent_Workspace/FHS_W0_R10_ACCEPT_20261108

# 我的母代理量測
python tools/reverify_mother.py                 # → out/REDERIVATION_MOTHER.json
python tools/layer_audit_r10.py                 # → out/LAYER_AUDIT_R10.json

# 閘：三種模式
cd ../FHS_W0_R9_REPAIR_20261108
python tools/gate_w0r9.py --round . --json ../FHS_W0_R10_ACCEPT_20261108/out/GATE_R10_RERUN.json
python tools/gate_w0r9.py --prior ../FHS_W0_R6_20261108 --json ../FHS_W0_R10_ACCEPT_20261108/out/GATE_R10_PRIOR.json
python tools/gate_w0r9.py --round . --selftest

# 繼承 16 項
cd ../FHS_W0_R7_VERIFY_20261108 && python tools/gate_w0r7.py \
  --object-round ../FHS_W0_R6_20261108 \
  --chain-child ../FHS_W0_R9_REPAIR_20261108/writeback/W0/FHS_PIPD-LS-PKG_W0_r9.md

# 我自己的磁碟注入（四項，各自只紅自己）
cd ../FHS_W0_R10_ACCEPT_20261108 && python tools/inject_gate.py

# 樹身分
git -C C:/Projects/Agent_Workspace/HG-KSEOS rev-parse --short HEAD
git -C C:/Projects/Agent_Workspace/worktrees/r4-hgk rev-parse --short HEAD
diff <(sed -n 6p C:/Projects/Agent_Workspace/HG-KSEOS/pyproject.toml) \
     <(sed -n 6p C:/Projects/Agent_Workspace/worktrees/r4-hgk/pyproject.toml)
```

---

## 10｜本回合自我錯誤（全文 `out/SELF_ERRORS.md`）

`E-A01` 差點把「25,201 不可重現」寫成缺陷，實際是我沒照規則實作 → 照做後完全相同｜`E-A02` 用錯鍵讀閘判決，把 10/10 讀成 0/10｜`E-A03` 只掃五個 root，漏掉 `worktrees/` 的第三份 r6｜`E-A04` 把「相對 HEAD 髒」寫成「被寫入」｜`E-A05` 差點沿用 HANDOVER 的「SHA256SUMS 應全 OK」，實測 58/59。

最該記住的兩條：**不可重現有兩種，先排除「我沒照規則」**；**文件說「應全 OK」時，還是要跑**。
