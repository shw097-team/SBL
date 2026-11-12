#!/usr/bin/env python3
"""Layer audit and self-error register for the round.

Three layers, kept apart on purpose:
  authoritative   read-only inputs and other people's live systems
  candidate       everything this round produced; nobody has accepted it
  discardable     tools, raw partitions, logs -- reproducible, not evidence of acceptance

The audit records every place where a thing sits on the wrong layer, and the
self-error register records what this round got wrong before it got it right.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime


def sha(p: str) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def main() -> int:
    R = sys.argv[1] if len(sys.argv) > 1 else "."
    now = datetime.now().astimezone().isoformat(timespec="seconds")

    def entry(path, layer, what, state):
        full = os.path.join(R, path)
        row = {"path": path, "layer": layer, "what": what, "state": state}
        if os.path.isfile(full):
            row["bytes"] = os.path.getsize(full)
            row["sha256"] = sha(full)
        return row

    audit = {
        "schema": "FHS.LayerAudit/1",
        "round": "FHS-W0-R6-EXEC-20261108",
        "generated_at": now,
        "authoritative_inputs_read_only": [
            entry("evidence/WP00/raw/SOURCE_LOCK.json", "AUTHORITATIVE_INPUT_MEASURED",
                  "digest readback of the 31 sources and six upper documents; the files themselves were only read", "READ_ONLY"),
            entry("evidence/WP19/LICENCE_INVENTORY.json", "AUTHORITATIVE_INPUT_MEASURED",
                  "licence/NOTICE state of the three repositories, read from their worktrees", "READ_ONLY"),
            entry("evidence/WP19/CI_INVENTORY.json", "AUTHORITATIVE_INPUT_MEASURED",
                  "live CI state read from the GitHub API with a token; the repos were not written", "READ_ONLY"),
        ],
        "candidate_layer": [
            entry("writeback/W0/FHS_PIPD-LS-PKG_W0_r7.md", "CANDIDATE",
                  "as-built revision: r6 body byte-identical plus the appended chapter", "NOT_ACCEPTED"),
            entry("out/W0_WP_MATRIX.json", "CANDIDATE", "per-WP measured state with hashed evidence refs", "NOT_ACCEPTED"),
            entry("evidence/WP15/specs/product_SPEC.json", "CANDIDATE", "Product SPEC draft", "NOT_ACCEPTED"),
            entry("evidence/WP15/specs/architecture_SPEC.json", "CANDIDATE", "Architecture SPEC draft", "NOT_ACCEPTED"),
            entry("evidence/WP15/specs/program_SPEC.json", "CANDIDATE", "Program SPEC draft", "NOT_ACCEPTED"),
            entry("evidence/WP16/tables/DONOR24.json", "CANDIDATE", "24 donor slots with licence state made explicit", "NOT_ACCEPTED"),
            entry("evidence/WP16/tables/METHOD25.json", "CANDIDATE", "25 method slots with original use stated", "NOT_ACCEPTED"),
            entry("evidence/WP21/tables/ORACLE96.json", "CANDIDATE", "96 oracle cells, each NOT_EXECUTED", "NOT_ACCEPTED"),
        ],
        "discardable_layer": [
            entry("evidence/WP01/raw/U0_byte_partition.jsonl", "DISCARDABLE_REPRODUCIBLE",
                  "19 MB partition table; rebuildable from the 31 sources by tools/u0_partition.py", "REPRODUCIBLE"),
            entry("evidence/WP01/raw/U1_subclaims.jsonl", "DISCARDABLE_REPRODUCIBLE",
                  "2.6 MB subclaim candidates; rebuildable by tools/u1_subclaims.py", "REPRODUCIBLE"),
            entry("tools/gstack_w0.py", "DISCARDABLE_REPRODUCIBLE", "invariant gate; itself a tool, not evidence", "REPRODUCIBLE"),
            entry("out/GSTACK_INJECTED.json", "DISCARDABLE_REPRODUCIBLE",
                  "the non-vacuity proof: the gate's verdict on a deliberately violated tree", "REPRODUCIBLE"),
        ],
        "misplacements": [
            {"id": "L-01", "what": "the r6 control document exists both in the previous round directory and in the Fabric mirror (INTEGRATION/FHS/docs/as-built/W0/)",
             "why_it_matters": "two copies of one document invite a reader to quote whichever is handier",
             "state": "ACCEPTED_BY_DESIGN", "detail": "the Fabric copy is declared NON_AUTHORITATIVE in INTEGRATION/FHS/docs/as-built/README.md; the round copy is the working parent of r7. r7 is published to the same mirror with the same declaration, so the pair stays distinguishable by layer, not by filename"},
            {"id": "L-02", "what": "19 MB and 2.6 MB raw tables sit inside the round directory",
             "why_it_matters": "a naive publish would put a 19 MB derived table into a repository",
             "state": "CONTAINED", "detail": "they live under evidence/*/raw/, the gate refuses oversize outside raw/, and the publish step excludes raw/ by name"},
            {"id": "L-03", "what": "the WP-16 report was mutated four times during the non-vacuity test",
             "why_it_matters": "a mutated evidence file that was not restored would silently disagree with its own report",
             "state": "RESTORED_AND_PROVEN", "detail": "each mutation was made from a byte backup and restored with cp -p; the restored sha256 equals the pre-injection value recorded in the test transcript (ae17b9fa…, cf21cd62…, a823b6bc…) and the gate returned to 15/15 PASS"},
            {"id": "L-04", "what": "the round wrote nothing into any repository until the publish step",
             "why_it_matters": "G8 must be able to say 'the repos are unchanged' as a comparison, not a claim",
             "state": "PROVEN", "detail": "G8 compares HEAD and dirty-path count against the WP-00 baseline for all three worktrees: 0 drift"},
        ],
        "not_done_and_who_owns_it": [
            {"item": "original-domain acceptance of any W0 work package", "owner": "Original Domain Reader/Owner", "count": 0},
            {"item": "issuer re-issue to registry rev 14", "owner": "OWNER (protected terminal, owner key)", "count": 1},
            {"item": "authoritative copy of each colliding source name", "owner": "Original Domain Owner", "count": 17},
            {"item": "licence determination for Fabric and HG-KSEOS", "owner": "OWNER", "count": 2},
            {"item": "value-set closure for 15 PIPD contract families", "owner": "Original PIPD contract Owner", "count": 15},
        ],
    }
    json.dump(audit, open(os.path.join(R, "out/LAYER_AUDIT.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    errors = [
        ("E-01", "WP-01 產物的 `head` 預覽以 bytes 截斷 120",
         "1,045 個抽樣中有 91 個尾端被切成 U+FFFD，中文尾字被切半",
         "由回合層獨立檢查器 `tools/verify_u0_partition.py` 發現；**未改寫車道產物**，改為在檢查器裡把截斷痕跡與真正的 offset 不符分開計數，並在 r7 §B.3 `D-W0-R7-09` 公開記錄",
         "偏移與覆蓋完全正確（31/31 檔位元全覆蓋），這是預覽瑕疵不是分割瑕疵"),
        ("E-02", "我自己寫的 GSTACK 閘把誠實的「不宣稱」判成裸聲稱",
         "三份 SPEC 的 `本 SPEC 不宣稱：ORIGINAL_ACK…` 被 G5b 判 FAIL",
         "擴充豁免詞表加入 `不宣稱`／`不聲明`／`不得`，**沒有**去改 SPEC 的措辭來迎合掃描器",
         "掃描器修正後仍需證明會咬：注入一句真的裸聲稱，G5b 立刻 FAIL"),
        ("E-03", "閘的 source 解析器只認檔名，不認 SourceID",
         "`FHS-BODY-02` 這類 SourceID 被判為 unresolved，131 個 ref 一度全紅",
         "由 WP-00 的 source lock 建立 SourceID→檔名映射；另外把控制稿本身與其 r5 父本加入可解析集合",
         "**沒有**放寬 span 斷言：解析成功後仍要求逐位元等於 quoted_text"),
        ("E-04", "閘的計數對帳只認一種鍵名",
         "WP-16 用 `measured.donor_slots_found`、WP-21 用 `counts.ac15`，閘一開始判為未宣告",
         "改為別名解析（flatten 後接受 4 組同義鍵）",
         "仍要求表格實際列數等於宣告數；注入 `donor_slots_found=26`（表實為 24）立刻 FAIL"),
        ("E-05", "我把子代理的中途摘要當成終值寫進 r7 章節",
         "章節初稿寫「23 條驗收」，WP-15 最終報告實為 15 條（6 POS／9 NEG）；相似度也誤植為 0.2139",
         "改由建置器直接讀取車道的最終 `REPORT.json` 取值，並回頭修正章節文字",
         "這是本輪最該記住的一條：**摘要不是產物**，只有落地檔案裡的欄位才是"),
        ("E-07", "發佈時我把「位元保全」放在 repo 既有不變量之上",
         "第一次推 SBL 時用本地 `.gitattributes * -text` 保全 CRLF 位元；SBL 既有的 `tests/test_reproducible_build.py::test_git_objects_are_lf_clean` 直接判紅（17 個 blob 含 CRLF），連帶使 `test_repro_mutation_probe` 失去意義（乾淨樹不通過）",
         "以 repo 規則為準：移除 `-text`、把 payload 正規化為 LF，並在 `MANIFEST.json` 逐檔記錄**兩個** digest（`sha256_round` 為車道量測位元、`sha256_published` 為實際入庫位元），附「以 universal newlines 正規化回合副本即可對上」的橋接說明；Fabric 無此不變量，鏡像改回位元精確",
         "重推後 SBL 四項檢查全綠（windows／ubuntu test、pipd-compat、supply-chain），且 r7 的 r6 前綴在正規化後仍 byte-identical"),
        ("E-06", "建置器一開始把不存在的 `evidence/WP00/REPORT.json` 列為引用",
         "建置以 exit 3 失敗",
         "補寫 WP-00 的報告產生器 `tools/wp00_report.py`，讓報告由量測產生而非手寫",
         "失敗是正確行為——引用不存在的路徑就該建置失敗，不是警告"),
    ]
    lines = ["# 本輪自我錯誤登記（FHS W0 r7）", "",
             "> 只記本輪真的犯過、且已被自己抓到的錯。每條都寫：錯在哪、怎麼被發現、怎麼修、修完怎麼證明還會咬。", ""]
    for eid, what, symptom, fix, proof in errors:
        lines += [f"## {eid}｜{what}", "", f"- **症狀**：{symptom}", f"- **處置**：{fix}",
                  f"- **修後證明**：{proof}", ""]
    open(os.path.join(R, "out/SELF_ERRORS.md"), "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print(f"layer audit written ({len(audit['misplacements'])} misplacements, {len(errors)} self-errors)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
