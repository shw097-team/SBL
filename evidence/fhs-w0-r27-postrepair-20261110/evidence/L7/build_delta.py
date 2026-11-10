#!/usr/bin/env python3
"""build_delta.py — emits out/BLUEPRINT_AFFECTED_SCOPE_DELTA.json + .md.

Numbers (bytes/lines/sha256) come from evidence/L7/blueprint_measure.json, which was
produced by measure_l7.py against the real files. Anchor line numbers come from
anchors.json, already verified by pin_anchors.py; the anchor LINE TEXT is re-read
from the real file here so the delta quotes it instead of retyping it.

Nothing in this script writes to the knowledge base.
"""
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(os.path.dirname(HERE))          # .../FHS_W0_R26_POSTREPAIR_20261110
OUT = os.path.join(RUN, "out")
KB = "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖"

MEAS = json.load(open(os.path.join(HERE, "blueprint_measure.json"), encoding="utf-8"))["measured"]
ANCH = json.load(open(os.path.join(HERE, "anchors.json"), encoding="utf-8"))
MEAS_BY = {}
for m in MEAS:
    MEAS_BY[m["doc"].split("_")[0]] = m

MARKER = "R27-APPEND"

PROPOSALS = [
    {
        "doc_id": "L0",
        "title": "《FHS_總藍圖》r4",
        "purpose": "模型多樣性可選＋受保護身份邊界（EC-R26-012）、單一 Owner／單一 Issuer、證據升格否決權",
        "consumer": "原 OWNER（唯一 Human Owner）簽核；下游 consumer = 原 HGK PLAN／Fabric Policy Reader 與 Protected Checker／Publisher",
        "constraints": ["不改 §00.3 既有四條硬邊界任一字元", "不新增第五條硬邊界", "不重編 §00–§13 章號"],
        "spans": [
            {
                "span": "L0-S4",
                "proposed": "| PROMOTION VETO | 某層證據只能在其原 Consumer、同 Subject／Scope、帶該層自己的 Raw 之下被上一層引用；跨層引用需具名 join | 以上一層的**存在**替下一層背書（例：CI 綠＝RELEASE、PR 綠燈＝Publisher 已發行、文件完成＝Native 已載入） |",
            },
            {
                "span": "L0-S2",
                "proposed": "  - **本條不因模型選擇而變**：車道可共用同一模型或同一 provider（`model_diversity_optional = true`），但 Maker、Issuer、Checker、Publisher 的 OS／Credential／Trust 仍不得折疊；credential 分離不因「合格模型只有一個」而降級。",
            },
            {
                "span": "L0-S1",
                "proposed": (
                    "#### 06.2B｜模型多樣性可選、受保護身份不變（r27 追加，PROPOSED_FOR_RATIFICATION）\n\n"
                    "`model_diversity_optional = true`：任何車道不得因「與另一車道共用同一模型或同一 provider」被拒絕；"
                    "`same_arm_lanes` 只記錄，永不作為失敗條件。\n\n"
                    "`protected_identity_permissions = UNCHANGED`：Maker ≠ Issuer／Checker／Publisher（**credential 軸**）；"
                    "Writer 不得自簽 protected pass；一個通用目的 token 不得升格為 Publisher key。\n\n"
                    "兩個軸互不推導：模型自由度變大，不會讓 credential 分離變鬆。任何要移除 credential 分離的提案，"
                    "都是另一件治理修訂，須逐效果另行裁決。\n\n"
                    "POS：九個槽由少於三個模型服務時，路由仍成立。NEG：以「模型已多樣化」推定 SoD 已滿足 → 拒收；"
                    "以同一 token 產生並批准受保護通過 → 拒收。"
                ),
            },
            {
                "span": "L0-S3",
                "proposed": "5. **單一 OWNER／單一 Issuer 不因車道模型可選而變**：OWNER 仍為唯一 Human Owner；Issuer 仍是原 HG-KSEOS 唯一 Issuer；Fabric 仍只做 Policy／FAR，SBL 仍只做產品與 SBL-hosted PIPD。本節不新增第二 Issuer、第二 Policy DB、第二 Release Writer。",
            },
        ],
        "negative_semantic": "以本節推定「credential 分離已滿足」的引用，必須被原 Protected Checker 拒收（consumer 端執行，本輪未執行）",
    },
    {
        "doc_id": "L1",
        "title": "《FHS_PIPD-LS-PKG_藍圖》r4",
        "purpose": "單一 FHS-3L&M ABI／九槽、Registry／Pool／Session／ActualServed 四型契約、quorum 真票約束",
        "consumer": "Original PIPD Intake／Authority／Profile Reader；CH-19 段另需 Hermes Host/PID ＋ HGK Lane Reader（`H-LANE-06`）；CH-43 quorum 段另需原 Protected Checker／Challenge Consumer",
        "constraints": [
            "**不得改動 84 個 DesignID**（本輪實測：60 個 `FHS-DR-###` ＋ 24 個 `INT-##` = 84）",
            "不新增 CH-50 之後的一級章",
            "不重述 CH-03／CH-16 已定義的共用 envelope 欄位",
        ],
        "spans": [
            {
                "span": "L1-S1",
                "proposed": (
                    "## r27｜`FHS-3L&M` 單一 ABI 與九槽（PROPOSED_FOR_RATIFICATION）\n\n"
                    "- 本文件只承認**一個** `FHS-3L&M` ABI：三車道 × 三槽 = **九槽**，唯讀自原 HGK "
                    "`lane-routing-registry.yaml` 與 `lane-route-slots.candidate.json`；不得另建第二 router／registry／pool。\n"
                    "- 每車道 pool 的臂數以 registry 為準（本輪實測 PLAN 6、EXECUTE 4、VERIFY_SECURITY 5）；候選臂不得超出 pool。\n"
                    "- 每次派工須有 run-scoped binding：`run_id, session_id, work_id, lane, slot, provider, model, pool_rank, "
                    "policy_epoch(int), registry_sha256, pool_sha256, retired_ledger_sha256, nonce, bound_at, expires_at`；"
                    "以 `O_CREAT|O_EXCL` 建立，碰撞即拒，不得覆寫。\n"
                    "- `same_arm_lanes` 一律記錄，永不作為拒絕理由（見 L0 §06.2B）。\n\n"
                    "NEG：同一 binding 被兩個 session 覆寫；以 `Selected` 冒充 `ActualServed`；以字串型號當 `policy_epoch`。"
                ),
            },
            {
                "span": "L1-S2",
                "proposed": (
                    "## r27｜Registry／Pool／Session／ActualServed 四型契約（PROPOSED_FOR_RATIFICATION）\n\n"
                    "| 型 | 必要欄 | 拒收條件 |\n|---|---|---|\n"
                    "| `Registry` | `epoch`(int)、`status`(IN_FORCE¦CANDIDATE)、`retired_arms{}`、自身 sha256 | epoch 非整數；退役臂仍在任一 live 位置 |\n"
                    "| `Pool` | 逐車道 `arms[]`（`rank`, `provider/model`）、自身 sha256 | 臂不在該車道 pool；rank 重複 |\n"
                    "| `Session` | `run_id, session_id, process_id`(fresh PID)、`lane, slot, binding_id, expires_at` | 同 `(lane,slot)` 覆寫；過期；body digest ≠ `binding_id` |\n"
                    "| `ActualServed` | `request_id, response_id, provider, api_mode, profile_sha, host_pid, model_usage_raw` | 只有 Selected／只有 HTTP 200／只有 UI 顯示 |\n\n"
                    "`Selected ≠ ActualServed`；缺 `ActualServed` raw 一律 `NOT_OBSERVED`，不得以字串型號推斷。\n"
                    "registry 的退役段與 pool 的 `retired_arms` 不一致時 → `HOLD`（不得擇一採用）。"
                ),
            },
            {
                "span": "L1-S3",
                "proposed": (
                    "## r27｜quorum 真票約束（PROPOSED_FOR_RATIFICATION）\n\n"
                    "- 一個 `DECIDED` preservation property 需 ≥2 張**有效**票，且票來自互異的 lane 身份、同 candidate、同 span。\n"
                    "- 有效票必要欄（缺一不計票）：`lane_id, candidate_sha256, source_sha256, clause_id, property, raw_path, "
                    "raw_sha256, timestamp, session_id, process_id`。\n"
                    "- 票值必須 `type(v) is bool`；JSON 整數 `1`、字串 `\"true\"` 不是票。\n"
                    "- raw 必須可重算：`sha256(bytes(raw_path)) == raw_sha256`；不可解析或不等即不計票。\n"
                    "- 同一 `lane_id` 或同一 `(session_id, process_id)` 的重複票只算一票（不是兩張）。\n\n"
                    "NEG：以 dict 形狀 `{\"A\": true}` 取代具名票；以 `\"00\"*32` 假 digest 過關；把兩張同 process 的票算成 quorum。"
                ),
            },
        ],
        "negative_semantic": "把九槽寫成「三個模型」，或新增第二個 registry／router，必須被原 HGK Lane Reader 拒收（consumer 端執行，本輪未執行）",
    },
    {
        "doc_id": "L2",
        "title": "《FHS_PIPD-LS-PKG_全波次藍圖》r4",
        "purpose": "W0-A／W1／W2／W3／W4 的責任切分與 resume predicate",
        "consumer": "原 TPM Program／PLAN Reader",
        "constraints": ["**不新增 WP #23**", "**不新增 DAG 邊 #37**", "不改 22 WP／36 邊的既有身份與方向"],
        "spans": [
            {
                "span": "L2-S1",
                "proposed": (
                    "### 4.r27-SP｜W0-A／W1／W2／W3／W4 責任切分與 resume predicate（PROPOSED_FOR_RATIFICATION）\n\n"
                    "| 相位 | 允許的效果 | 唯一 WriteSet | 不得做的事 | resume predicate |\n|---|---|---|---|---|\n"
                    "| `W0-A` | `SOURCE_READ` ＋ `LOCAL_DRAFT_WRITE` | 隔離 output root | 不 mint Permit、不寫任何 repo | 31 冊 snapshot manifest ＋ 三 SPEC 草稿 ＋ W0 cursor |\n"
                    "| `W1` | 路由／registry／issuer／host 的**讀回** | 無（唯讀） | 不寫 repo、不發任何世界效果 | 九槽可 bind、`--assert` 全綠、retired ledger 可讀 |\n"
                    "| `W2` | 受保護、可逆的寫入 | 具名 repo 的 allowed-writeset | 跨 Scope、自簽 Checker、無 Permit 先寫 | Permit＋epoch＋preimage＋rollback commit raw |\n"
                    "| `W3` | UX／Host 矩陣／normal mode | 文件與規格 | 新增世界效果、以 UI 顯示當 served | fresh PID 之三 Lane `ActualServed` raw |\n"
                    "| `W4` | Release／Retire **候選** | release artifact | 把 CI 綠當 Release | `GHP-02` ＋ 發行後 readback |\n\n"
                    "resume predicate 的共同形狀：`last_good + first_fail + next_legal_action`，且必須指名原 Reader；"
                    "沒有原 Reader 的讀回，就不是 resume，是重新開始。\n\n"
                    "**邊界**：本節不新增 WP、不新增 DAG 邊；任何超出 22 WP／36 邊的提案，都在 L2 之外處理。"
                ),
            }
        ],
        "negative_semantic": "任何引入 WP #23 或 DAG 邊 #37 的提案，必須被原 Program Reader 拒收（consumer 端執行，本輪未執行）",
    },
    {
        "doc_id": "W1",
        "title": "《FHS_PIPD-LS-PKG_W1_藍圖&skeleton》r5",
        "purpose": "native startup／discovery hook、Codex CLI 的 lane-bound dispatch、單一 issuer／pool／registry 綁定",
        "consumer": "SBL-hosted PIPD 原 Writer／Receiver ＋ 原 HGK Registry／Issuer",
        "constraints": ["不新增 launcher", "不改 24 張 L2 Design Obligation 的身份", "不把 W1 寫成會寫 repo 的相位"],
        "spans": [
            {
                "span": "W1-S1",
                "proposed": (
                    "## W1-r27｜native startup／discovery hook 與 lane-bound dispatch（PROPOSED_FOR_RATIFICATION）\n\n"
                    "- 組態發現只走原生 startup 路徑（profiles／gateway state／`hgk-lane-dispatch.py`），不得另造第二個 launcher 或第二套 discovery。\n"
                    "- Codex CLI 的每一次派工必須綁定 `(lane, slot, arm, policy_epoch, binding_id)`；未綁定即**不得 spawn**，且拒絕必須發生在建立子程序之前。\n"
                    "- 一個 Issuer、一個 pool、一個 registry：W1 只讀，不寫、不投影、不複製成第二份；`registry_sha256` 與 `pool_sha256` 記進每一次讀回。\n\n"
                    "NEG：以 `AGENTS.md` 的一行提示取代機械攔截；以 Selected 臂直接 spawn；在 W1 內寫回 registry。"
                ),
            }
        ],
        "negative_semantic": "以 prompt 一行取代 lane binding 的派工，必須被 dispatch guard 以 `FHS_ENTRY_ASSERT_REQUIRED` 拒（由 L5 車道執行；本文件不宣稱）",
    },
    {
        "doc_id": "W2",
        "title": "《FHS_PIPD-LS-PKG_W2_藍圖&skeleton》r5",
        "purpose": "真寫入前的 Permit／epoch／preimage／allowed-writeset 四件套；source-read ACL 不變",
        "consumer": "原 DEV Repo Reader ＋ 原 HGK Issuer ＋ WorldRaw Consumer",
        "constraints": ["不放寬 `SOURCE_READ` ACL", "不改 W2 四主 WP 的身份", "不新增依賴邊"],
        "spans": [
            {
                "span": "W2-S1",
                "proposed": (
                    "### W2-r27｜真寫入前的四件套：Permit／epoch／preimage／allowed-writeset（PROPOSED_FOR_RATIFICATION）\n\n"
                    "- 任何 `REPO_DEV_WRITE` 生效前，必須同時具備：①原 HGK Permit（同 Subject／Scope）②有效的 numeric policy epoch "
                    "③目標寫入集的 preimage digest ④具名的 allowed-writeset。缺一即拒，且在寫入前拒。\n"
                    "- 四件齊備才可寫；寫後必須留下 rollback commit 與世界讀回（world diff ＋ Raw）。\n"
                    "- **`SOURCE_READ` 的 ACL 完全不變**：本節不放寬任何讀取權限，也不允許寫入路徑借用讀取 ACL 或反向借用。\n\n"
                    "NEG：以 Candidate ECP 充當 Permit；以字串 epoch 充當有效 epoch；寫入範圍超出 allowed-writeset 仍宣稱完成。"
                ),
            }
        ],
        "negative_semantic": "缺 Permit 仍寫入的情形，必須被原 HGK Issuer 拒（consumer 端執行，本輪未執行）",
    },
    {
        "doc_id": "W3",
        "title": "《FHS_PIPD-LS-PKG_W3_藍圖&skeleton》r5",
        "purpose": "可選的三車道九槽 UI、跨 host loader／ActualServed 讀回、fallback 邊界、fresh-PID 驗收",
        "consumer": "Hermes original Runtime／Launcher／Provider Raw Reader → HGK Lane／Journal Consumer",
        "constraints": ["不把 UI 顯示升格為 served", "不新增第六個工程波次", "不改 W18 的 E33–E42 身份"],
        "spans": [
            {
                "span": "W3-S1",
                "proposed": (
                    "## 0.4B｜三車道九槽 UI、跨 host loader／ActualServed 讀回與 fallback 邊界（PROPOSED_FOR_RATIFICATION）\n\n"
                    "- UI 的三車道九槽是**可選呈現**：未顯示不等於未服務，顯示也不等於 served。一切以 `ActualServed` raw 為準。\n"
                    "- 跨 host 讀回必須帶 loader 身分（`profile_sha, host_pid, process_origin`）與 `request_id → response_id → actual_served` 的因果鏈；跨 host 借收據一律拒。\n"
                    "- fallback 只在原 Policy 已批准的集合內成立，且有界（次數／成本／該 lane 的效果）；越界即 PARK 該 lane 的受影工作，不動全域 `model.default`。\n"
                    "- fresh-PID 驗收：新 process、普通 Goal、零 B1 專用 prompt，三 Lane 各自可讀回；缺一即 `LANE_ACTUALSERVE_HOLD`。\n\n"
                    "NEG：以 UI 綠燈或 200 回應宣稱 served；以舊 B1 主機的 Raw 冒充 normal-mode 驗收。"
                ),
            }
        ],
        "negative_semantic": "以 UI 顯示或 200 當 served 的引用，必須以既有 `LANE_ACTUALSERVE_HOLD` 拒（consumer 端執行，本輪未執行）",
    },
    {
        "doc_id": "W4",
        "title": "《FHS_PIPD-LS-PKG_W4_藍圖&skeleton》r5",
        "purpose": "CI 綠 ≠ Release、供應鏈／授權／SBOM／rollback、受保護 Publisher 閘",
        "consumer": "原 Protected Checker ＋ 原 Publisher（`GHP-02`）",
        "constraints": ["不改 `E-FULL-01..08` 的原 ID 與完成門檻", "不改 `W4-01..12` 的身份", "不新增依賴邊"],
        "spans": [
            {
                "span": "W4-S1",
                "proposed": (
                    "### 2.1B｜CI 綠 ≠ Release；供應鏈、授權與 rollback 的受保護 Publisher 閘（PROPOSED_FOR_RATIFICATION）\n\n"
                    "- CI 綠只證明該 repo 的規則集對該 commit 通過；它不是 Release，也不是任何 Checker verdict。\n"
                    "- Release 前必須具備**同一 BuildDigest** 下的：授權（License）、NOTICE、SBOM、scanner raw、rollback/last-good/dual-read。缺一即 `RELEASE_SUPPLY_CHAIN_EVIDENCE_MISSING`。\n"
                    "- 發行只能由原 Publisher 以 `GHP-02` 對同 Candidate／Scope／Channel 給出，並留下發行後讀回；沒有讀回就沒有 `P2_FULL_PKG_RELEASE_DONE`。\n"
                    "- 通用目的 token 不得升格為 Publisher key；Maker 不得自簽 protected pass（見 L0 §06.2B 與 §00.3）。\n\n"
                    "NEG：以 CI green 自稱 Release（應得 `RELEASE_NOT_GRANTED`）；缺 SBOM 仍判 E26 通過。"
                ),
            }
        ],
        "negative_semantic": "CI 綠即宣告發行的引用，必須以既有 `RELEASE_NOT_GRANTED` 拒（consumer 端執行，本輪未執行）",
    },
]


def anchor_text(doc, span_id):
    spec = ANCH["docs"][doc]
    path = os.path.join(KB, spec["file"])
    lines = open(path, "rb").read().split(b"\n")
    for s in spec["spans"]:
        if s["id"] == span_id:
            return s, lines[s["line"] - 1].decode("utf-8", "replace").rstrip("\r")
    raise KeyError(span_id)


def main():
    negs = json.load(open(os.path.join(HERE, "amendment_negatives.json"), encoding="utf-8"))["cases"]
    out = {
        "schema": "FHS.R27.BlueprintAffectedScopeDelta/1",
        "generated_from": "evidence/L7/blueprint_measure.json + evidence/L7/anchors.json (pin_anchors.py, 12/12 OK)",
        "append_only_rule": ANCH["append_only_rule"],
        "status": "PROPOSED_FOR_RATIFICATION",
        "not_in_force": "none of these seven amendments is in force; each needs the named original consumer's ratification, one document at a time",
        "documents": [],
    }
    for p in PROPOSALS:
        m = MEAS_BY[p["doc_id"]]
        spans = []
        for sp in p["spans"]:
            a, text = anchor_text(p["doc_id"], sp["span"])
            spans.append({
                "span_id": sp["span"],
                "anchor_line": a["line"],
                "anchor_kind": a["kind"],
                "anchor_text_verbatim": text,
                "marker": "%s:%s" % (MARKER, p["doc_id"]),
                "proposed_text": sp["proposed"],
            })
        cases = [c for c in negs if c["doc"] == p["doc_id"]]
        out["documents"].append({
            "doc_id": p["doc_id"],
            "title": p["title"],
            "path": m["path"],
            "sha256": m["sha256"],
            "bytes": m["bytes"],
            "lines_lf_split": m["lines_lf_split"],
            "status": "PROPOSED_FOR_RATIFICATION",
            "purpose": p["purpose"],
            "spans": spans,
            "ratify_by": p["consumer"],
            "negative_executed": [
                {"case": c["case"], "exit": c["exit"], "code": c["code"],
                 "input": os.path.basename(c["input"]), "input_sha256": c["input_sha256"]}
                for c in cases
            ],
            "negative_owed_to_consumer": p["negative_semantic"],
            "constraints": p["constraints"],
        })
    os.makedirs(OUT, exist_ok=True)
    jp = os.path.join(OUT, "BLUEPRINT_AFFECTED_SCOPE_DELTA.json")
    json.dump(out, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", jp, len(open(jp, "rb").read()), "bytes")

    md = []
    md.append("# 七份藍圖的受影範圍差額（r27）— 全部 `PROPOSED_FOR_RATIFICATION`\n")
    md.append("> 本檔是**提案**，不是修訂。七份文件全部維持現行 bytes 不變；每一份的修訂都是「在釘住的錨點行"
              "插入一段帶 `<!-- R27-APPEND:<DOC> -->` 的追加文字」，原文一個字都不改。\n")
    md.append("> 產出來源：`evidence/L7/blueprint_measure.json`（實測 bytes/lines/sha256）＋ "
              "`evidence/L7/anchors.json`（12 個錨點，`pin_anchors.py` 12/12 OK，log `evidence/L7/m10_anchor_pins.log`）。\n")
    md.append("> 負例：`evidence/L7/run_amendment_negatives.py` 對七份文件實跑 29 個案例（7 個接受 ＋ 22 個拒絕），"
              "全部命中預期拒絕碼，log `evidence/L7/m07_amendment_negatives.log`。\n")
    md.append("\n## 0. 七份文件現值（實測）\n")
    md.append("| doc | 檔案 | bytes | lines(LF split) | sha256 | 錨點數 |")
    md.append("|---|---|---|---|---|---|")
    for d in out["documents"]:
        md.append("| `%s` | `%s` | %d | %d | `%s` | %d |"
                  % (d["doc_id"], os.path.basename(d["path"]), d["bytes"], d["lines_lf_split"],
                     d["sha256"], len(d["spans"])))
    md.append("\n## 1. 逐份提案\n")
    for d in out["documents"]:
        md.append("### %s — %s\n" % (d["doc_id"], d["title"]))
        md.append("- **狀態**：`PROPOSED_FOR_RATIFICATION`（未生效）")
        md.append("- **檔案**：`%s`" % d["path"])
        md.append("- **現值**：%d bytes／%d lines／`%s`" % (d["bytes"], d["lines_lf_split"], d["sha256"]))
        md.append("- **要補的洞**：%s" % d["purpose"])
        md.append("- **必須 ratify 的原 consumer**：%s" % d["ratify_by"])
        md.append("- **不得動到的東西**：%s" % "；".join(d["constraints"]))
        for s in d["spans"]:
            md.append("")
            md.append("#### 錨點 `%s`（第 %d 行，`%s`）\n" % (s["span_id"], s["anchor_line"], s["anchor_kind"]))
            md.append("原文（逐字，不動）：\n")
            md.append("```")
            md.append(s["anchor_text_verbatim"])
            md.append("```\n")
            md.append("插入文字（帶 `<!-- %s -->` 標記）：\n" % s["marker"])
            md.append("```markdown")
            md.append(s["proposed_text"])
            md.append("```")
        md.append("")
        md.append("**負例（本輪實跑）**：")
        for c in d["negative_executed"]:
            md.append("- `%s` → exit %d，`%s`（輸入 `%s`，sha256 `%s…`）"
                      % (c["case"], c["exit"], c["code"], c["input"], c["input_sha256"][:16]))
        md.append("- **尚欠原 consumer 端執行的語義負例**：%s" % d["negative_owed_to_consumer"])
        md.append("")
    md.append("## 2. 負例工具與它證明什麼\n")
    md.append("`evidence/L7/check_blueprint_amendment.py` 對「修正後的檔案」要求四件事同時成立：")
    md.append("①前 N bytes 與釘住的原文逐位元相同（`AMENDMENT_PREFIX_MISMATCH`，exit 1）"
              "②錨點行仍在原位且未被改寫（`AMENDMENT_ANCHOR_MISSING`，exit 3）"
              "③L1 的 84 個 DesignID 分母不變（`DESIGNID_COUNT_DRIFT`，exit 4）"
              "④追加段恰好出現一次標記（`MARKER_MISSING`，exit 5）。")
    md.append("\n這四條合起來的意思：一份「合法修正」只能是**純插入**，而且插入點與分母都不能漂。"
              "只驗 prefix 不驗錨點，會漏掉「原文被換掉、但新舊檔前綴剛好相同」以外的所有情況；"
              "只驗錨點不驗 prefix，則任何改寫都能過關。\n")
    md.append("## 3. 明確不在本提案內的主張\n")
    md.append("- 七份文件**都還沒有被 ratify**，本輪不主張任何一份已修訂。")
    md.append("- 提案文字本身**不是** new authority：它若與 L0／原 Domain Canonical 衝突，以原 Reader 為準。")
    md.append("- L1 的 84 個 DesignID、L2 的 22 WP／36 邊、W4 的 `E-FULL-01..08` 與 `W4-01..12` 都**不新增、不改號**。")
    md.append("- 沒有任何提案會讓 `FULL_W0_CLOSEOUT`／`NATIVE_SIGNED`／`PASS_CHALLENGE`／`RELEASE` 成立。")
    mp = os.path.join(OUT, "BLUEPRINT_AFFECTED_SCOPE_DELTA.md")
    open(mp, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", mp, len(open(mp, "rb").read()), "bytes")


if __name__ == "__main__":
    main()
