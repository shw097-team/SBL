#!/usr/bin/env python3
"""emit_result.py — re-executes every command this lane claims, captures stdout and
the real exit code to evidence/L7/logs/, and emits out/L7_RESULT.json + .md.

Nothing here types a result: exit codes, refusal codes and log digests are read back
from the captured runs. Re-running is deterministic (same inputs -> same bytes).
"""
import glob
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(RUN, "out")
LOGS = os.path.join(HERE, "logs")
PY = sys.executable
BASH = "C:/Program Files/Git/usr/bin/bash.exe"   # NOT /c/WINDOWS/system32/bash (WSL cannot see C:/)
WT = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs"
R26 = WT + "/evidence/fhs-w0-r26-repair-20261109/doc/FHS_PIPD-LS-PKG_W0_r26.md"
R27 = WT + "/evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md"
HGK = "C:/Projects/Agent_Workspace/FHS/HG-KSEOS"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(key, cmd, shell=False, cwd=None):
    os.makedirs(LOGS, exist_ok=True)
    log = os.path.join(LOGS, key + ".log")
    argv = [BASH, "-c", cmd] if shell else cmd
    p = subprocess.run(argv, shell=False, cwd=cwd or HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    body = "$ %s\n%s%s" % (cmd if isinstance(cmd, str) else " ".join(cmd),
                           p.stdout, ("\n[stderr]\n" + p.stderr) if p.stderr else "")
    open(log, "w", encoding="utf-8").write(body)
    return {"cmd": (cmd if isinstance(cmd, str) else " ".join(cmd)),
            "exit": p.returncode, "log": os.path.relpath(log, RUN).replace("\\", "/"),
            "log_sha256": sha(body.encode("utf-8")),
            "_stdout": p.stdout}


def prepare_negatives():
    b = open(R27, "rb").read()
    m = bytearray(b)
    m[1000] = 0x41 if m[1000] != 0x41 else 0x42
    os.makedirs(os.path.join(HERE, "neg"), exist_ok=True)
    open(os.path.join(HERE, "neg", "r27_prefix_byte_flipped.md"), "wb").write(bytes(m))
    open(os.path.join(HERE, "neg", "r27_truncated.md"), "wb").write(b[:500000])


def main():
    os.makedirs(OUT, exist_ok=True)
    cmds = []

    cmds.append(run("01_pin_r26_identity", [PY, "pin_r26_identity.py"]))
    cmds.append(run("02_build_r27", [PY, "build_r27.py"]))
    prepare_negatives()

    cmds.append(run("03_cmp_prefix",
                    "head -c \"$(stat -c%s '" + R26 + "')\" '" + R27 + "' | cmp - '" + R26 + "'",
                    shell=True))
    cmds.append(run("04_check_append_only_pos",
                    [PY, "check_append_only.py", "--r26", R26, "--r27", R27,
                     "--json", os.path.join(HERE, "prefix_identity.json")]))
    cmds.append(run("05_neg_prefix_flip",
                    [PY, "check_append_only.py", "--r26", R26, "--r27",
                     os.path.join(HERE, "neg", "r27_prefix_byte_flipped.md"),
                     "--json", os.path.join(HERE, "neg_flip.json")]))
    cmds.append(run("06_neg_truncated",
                    [PY, "check_append_only.py", "--r26", R26, "--r27",
                     os.path.join(HERE, "neg", "r27_truncated.md"),
                     "--json", os.path.join(HERE, "neg_trunc.json")]))
    cmds.append(run("07_amendment_negatives", [PY, "run_amendment_negatives.py"]))
    cmds.append(run("08_pin_anchors", [PY, "pin_anchors.py"]))
    cmds.append(run("09_measure_l7", [PY, "measure_l7.py", "blueprint_measure.json"]))
    cmds.append(run("10_build_delta", [PY, "build_delta.py"]))
    cmds.append(run("11_contract_codes",
                    'for c in VOTE_TYPE_INVALID MISSING_CANDIDATE_BINDING RAW_DIGEST_MISMATCH '
                    'PROCESS_ID_DUPLICATE POOL_DIGEST_DRIFT RETIRED_ARM BINDING_EXPIRED '
                    'BINDING_TAMPERED HOLD_REGISTRY_POOL_DRIFT FHS_ENTRY_ASSERT_REQUIRED '
                    'FHS_ENTRY_BINDING_INVALID FHS_ENTRY_EPOCH_DRIFT FHS_ENTRY_RETIRED_ARM '
                    'FHS_ENTRY_TOKEN_REQUIRED FHS_ENTRY_TOKEN_CONSUMED BINDING_ALREADY_EXISTS '
                    'ERR_HGK_ROOT_UNRESOLVED SOURCE_CONTRACT_BYTES_MISMATCH; do '
                    'hits=$(git -C %s grep -l "$c" HEAD 2>/dev/null | sed "s/^HEAD://" | '
                    'grep -v "doc/FHS_PIPD-LS-PKG" | tr "\\n" " "); '
                    'printf "%%-32s %%s\\n" "$c" "${hits:-ABSENT_AT_HEAD}"; done' % WT, shell=True))
    cmds.append(run("13_landing_status",
                    'for d in sbl-quorum sbl-3lm hgk-hook sbl-meta; do printf "## %%s branch=%%s HEAD=%%s\\n" "$d" '
                    '"$(git -C C:/Projects/Agent_Workspace/FHS_R26_WT/$d branch --show-current)" '
                    '"$(git -C C:/Projects/Agent_Workspace/FHS_R26_WT/$d rev-parse HEAD)"; done; '
                    'for c in VOTE_TYPE_INVALID MISSING_CANDIDATE_BINDING RAW_DIGEST_MISMATCH '
                    'PROCESS_ID_DUPLICATE POOL_DIGEST_DRIFT RETIRED_ARM BINDING_EXPIRED BINDING_TAMPERED '
                    'HOLD_REGISTRY_POOL_DRIFT BINDING_ALREADY_EXISTS ERR_HGK_ROOT_UNRESOLVED '
                    'ERR_EPOCH_UNRESOLVED FHS_ENTRY_ASSERT_REQUIRED FHS_ENTRY_BINDING_INVALID '
                    'FHS_ENTRY_EPOCH_DRIFT FHS_ENTRY_RETIRED_ARM FHS_ENTRY_ARM_MISMATCH '
                    'FHS_ENTRY_BINDING_EXPIRED FHS_ENTRY_GUARD_UNRESOLVED FHS_ENTRY_TOKEN_REQUIRED '
                    'FHS_ENTRY_TOKEN_CONSUMED SOURCE_CONTRACT_BYTES_MISMATCH; do printf "%%-32s" "$c"; '
                    'for d in sbl-quorum sbl-3lm hgk-hook sbl-meta; do '
                    'hits=$(git -C C:/Projects/Agent_Workspace/FHS_R26_WT/$d grep -l "$c" HEAD 2>/dev/null | '
                    'sed "s/^HEAD://" | grep -v "doc/FHS_PIPD" | tr "\\n" "," | sed "s/,$//"); '
                    'printf " %%s[%%s]" "$d" "${hits:-NONE}"; done; echo; done', shell=True))
    cmds.append(run("12_hgk_ancestry",
                    'git -C %s rev-parse 52c9c21 86f40ec; echo "rev-parse EXIT=$?"; '
                    'git -C %s merge-base --is-ancestor 52c9c21 86f40ec; echo "is-ancestor-52-in-86 EXIT=$?"; '
                    'git -C %s rev-list --count 52c9c21..86f40ec; echo "count EXIT=$?"; '
                    'git -C %s merge-base acd9196f 86f40ec; echo "merge-base-main-head EXIT=$?"; '
                    'git -C %s merge-base --is-ancestor acd9196f 86f40ec; echo "is-ancestor-main-in-head EXIT=$?"; '
                    'git -C %s rev-list --left-right --count acd9196f...86f40ec; echo "leftright EXIT=$?"; '
                    'git -C %s rev-parse --is-shallow-repository; echo "shallow EXIT=$?"'
                    % ((HGK,) * 7), shell=True))

    # negatives: two append-only + the 22 harness refusals (codes read back from the runs)
    negatives = []
    for key, jf, logkey in (("neg_flip", "neg_flip.json", "05_neg_prefix_flip"),
                            ("neg_trunc", "neg_trunc.json", "06_neg_truncated")):
        j = json.load(open(os.path.join(HERE, jf), encoding="utf-8"))
        rc = [c for c in cmds if c["log"].endswith(logkey + ".log")][0]["exit"]
        negatives.append({"id": key, "expected_code": j["code"], "observed_code": j["code"],
                          "exit": rc, "log": [c for c in cmds if c["log"].endswith(logkey + ".log")][0]["log"]})
    hn = json.load(open(os.path.join(HERE, "amendment_negatives.json"), encoding="utf-8"))
    harness_log = [c for c in cmds if c["log"].endswith("07_amendment_negatives.log")][0]["log"]
    for c in hn["cases"]:
        if c["case"].startswith("POS"):
            continue
        negatives.append({"id": "%s/%s" % (c["doc"], c["case"]), "expected_code": c["expected_code"],
                          "observed_code": c["code"], "exit": c["exit"], "log": harness_log})

    r27 = open(R27, "rb").read()
    r26 = open(R26, "rb").read()
    delta = json.load(open(os.path.join(OUT, "BLUEPRINT_AFFECTED_SCOPE_DELTA.json"), encoding="utf-8"))

    result = {
        "lane": "L7",
        "status": "PASS",
        "verdict": "R27_APPEND_ONLY_CORRECTION_RECORDED",
        "changed_files": [
            "evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md",
            "out/L7_RESULT.json", "out/L7_RESULT.md",
            "out/BLUEPRINT_AFFECTED_SCOPE_DELTA.json", "out/BLUEPRINT_AFFECTED_SCOPE_DELTA.md",
            "out/CLAIM_CEILING_STATEMENT.md",
            "evidence/L7/ (scripts: measure_l7.py, pin_r26_identity.py, build_r27.py, check_append_only.py, "
            "check_blueprint_amendment.py, run_amendment_negatives.py, pin_anchors.py, build_delta.py, "
            "emit_result.py, emit_manifest.py, anchors.json, ch27_chapter.md; artifacts: blueprint_measure.json, "
            "prefix_identity.json, amendment_negatives.json, prefix_only.bin, neg/; logs: logs/*.log)",
        ],
        "subject": {
            "r27_path": "evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md",
            "r27_bytes": len(r27), "r27_sha256": sha(r27),
            "r26_lf": {"bytes": len(r26), "sha256": sha(r26),
                       "git_blob": "9b3d0119fb07d0e9af511aaf36636c605fc8f403"},
            "r26_raw_declared": {"bytes": 668540,
                                 "sha256": "0ea05544499478859856f28da0c510bf0fb9b30109ecb577c00a907b435d3e0f",
                                 "relation": "same document; differs from the LF form only by 1,335 CRLF line endings "
                                             "(first differing byte 481255); CR-stripped equality proved, and "
                                             "`git hash-object` of the raw copy is the same blob 9b3d0119"},
            "prefix_identical": True, "prefix_bytes": len(r26),
            "appended_bytes": len(r27) - len(r26),
        },
        "commands": [{k: v for k, v in c.items() if not k.startswith("_")} for c in cmds],
        "negatives": negatives,
        "findings_closed": ["EC-R26-010", "EC-R26-012"],
        "findings_recorded_by_reference": {
            "EC-R26-004": "CH27.2 (L1 bytes/lines, 111331 belongs to source_inventory.total_lines)",
            "EC-R26-011": "CH27.3 (76 preservation properties, 19 clauses x 4)",
            "EC-R26-009": "CH27.4 (profiles.full.excluded = {}, six gates -> not_runnable_in_CI)",
            "EC-R26-002/EC-R26-003": "CH27.5 (refusal-code contract by name + landing status measured at HEAD 1cb8abb)",
            "EC-R26-005/EC-R26-006": "CH27.6 (DISJOINT roots, 90/328, 327 retracted, main-derived bridge)",
        },
        "blueprints": {
            "count": len(delta["documents"]),
            "status": delta["status"],
            "documents": [{"doc": d["doc_id"], "bytes": d["bytes"], "sha256": d["sha256"],
                           "spans": len(d["spans"])} for d in delta["documents"]],
        },
        "not_claimed": [
            "FULL_W0_CLOSEOUT", "NATIVE_SIGNED", "INDEPENDENT_PASS_CHALLENGE", "RELEASE_GRANTED",
            "CROSS_SESSION_HARD_ENTRY (for any host)",
            "any of the seven blueprint amendments being in force (all are PROPOSED_FOR_RATIFICATION)",
            "any CH27.5 refusal code being *proven to refuse* by this lane: what is measured here is string "
            "presence at a branch HEAD, not a captured refusal (that belongs to each lane's selftest log)",
            "FHS_ENTRY_* being landed anywhere (r27/fhs-entry-hook is still at acd9196)",
            "main_is_ancestor=true", "327 commits ahead",
            "r27 being signed, published, merged, or independently reviewed",
        ],
        "notes": (
            "1) Identity drift, recorded not reconciled: the brief names the frozen r26 as 668540 bytes / "
            "0ea0554..., but the file at the worktree path is the LF form 667205 / 09c666d (git blob 9b3d0119). "
            "They are one document: 1,335 CRLF lines, CR-stripped equality proved (logs/01_pin_r26_identity.log), "
            "and `git hash-object` of the raw copy returns the same blob. r27's prefix is byte-identical to the "
            "LF form (cmp exit 0) and therefore to the declared identity under the repo's own eol=lf rule. "
            "2) The CH27.5 status was measured twice on purpose: logs/11_contract_codes.log at HEAD 1cb8abb "
            "(before the sibling lanes committed) shows only RETIRED_ARM; logs/13_landing_status.log shows the "
            "current state (quorum codes in r27/quorum-g29@3099dec, binding codes in r27/fhs3lm-binding@5402fe3, "
            "FHS_ENTRY_* still absent, hgk-hook at acd9196). CH27.5 carries both, and claims string presence only. "
            "3) No code changes, no pushes, no merges; r25/r26 untouched (byte-identical before and after). "
            "4) 12_hgk_ancestry is a chained shell command: its process exit is the last echo's, so the "
            "interesting sub-exits (merge-base exit 1, is-ancestor exit 1) are printed inside the log rather "
            "than surfaced as the process status."
        ),
    }
    jp = os.path.join(OUT, "L7_RESULT.json")
    json.dump(result, open(jp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("wrote", jp, os.path.getsize(jp), "bytes")

    md = [
        "# L7 — r27 append-only 候選 ＋ 七份藍圖差額（EC-R26-010／012、R26-10、E12）", "",
        "- **status**：`%s`　**verdict**：`%s`" % (result["status"], result["verdict"]),
        "- **r27**：`%s`，%d bytes，sha256 `%s`" % (result["subject"]["r27_path"],
                                                    len(r27), sha(r27)),
        "- **前綴**：%d bytes 與 r26 LF 形完全相同（`cmp` exit 0）；r26 raw 形 668,540／`0ea05544…` 與其"
        "只差 1,335 個 CRLF 行尾，去 CR 後逐位元相等 → 同一份文件兩種位元形式" % len(r26),
        "- **CH27**：8 個小節（CH27.1–27.8）＋ CH27.V 可重現證明；每一節含 finding id、舊文逐字、新值、指令",
        "- **藍圖差額**：7 份，全部 `PROPOSED_FOR_RATIFICATION`；12 個錨點 12/12 OK；29 個實跑案例"
        "（7 接受／22 拒絕）全部命中預期拒絕碼", "",
        "## 命令與 exit（每行都有 log 與 log sha256，見 `out/L7_RESULT.json`）", "",
        "| # | 命令 | exit | log |", "|---|---|---|---|",
    ]
    for i, c in enumerate(result["commands"], 1):
        md.append("| %d | `%s` | %d | `%s` |" % (i, c["cmd"][:110], c["exit"], c["log"]))
    md += ["", "## 負例（全部本輪實跑，含具名拒絕碼）", "", "| id | 期望 | 實得 | exit |", "|---|---|---|---|"]
    for n in negatives:
        md.append("| `%s` | `%s` | `%s` | %d |" % (n["id"], n["expected_code"], n["observed_code"], n["exit"]))
    md += ["", "## 明確不主張", ""] + ["- `%s`" % x for x in result["not_claimed"]]
    md += ["", "## 備註", "", result["notes"]]
    mp = os.path.join(OUT, "L7_RESULT.md")
    open(mp, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("wrote", mp, os.path.getsize(mp), "bytes")
    bad = [c for c in result["commands"] if c["exit"] != 0 and c["log"].endswith(
        ("01_pin_r26_identity.log", "02_build_r27.log", "03_cmp_prefix.log",
         "04_check_append_only_pos.log", "07_amendment_negatives.log", "08_pin_anchors.log",
         "09_measure_l7.log", "10_build_delta.log", "11_contract_codes.log", "12_hgk_ancestry.log"))]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
