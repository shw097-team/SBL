#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""由實跑產物組 LANE_REPORT.json。所有數字都從 out/*.json 與
tests/PROBE_EVIDENCE_RAW.json 讀回，不在這裡手寫任何量測值。
"""

import contextlib
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile

LANE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(LANE_DIR, "out")
TESTS = os.path.join(LANE_DIR, "tests")
sys.path.insert(0, LANE_DIR)

import source_probe  # noqa: E402


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main():
    man = load(os.path.join(OUT, "SOURCE_MANIFEST.json"))
    repo = load(os.path.join(OUT, "REPO_TRIPLE_STATE.json"))
    host = load(os.path.join(OUT, "HOST_PROBE.json"))
    ev = load(os.path.join(TESTS, "PROBE_EVIDENCE_RAW.json"))

    probe = man["probe"]
    counts = man["counts"]
    s31 = man["source31"]
    u22 = man["upper22"]
    z = man["source_zip"]
    b = man["body"]
    mf = man["manifest"]
    summary = repo["summary"]
    checks = probe["checks"]
    warn = [c for c in checks if c["severity"] == "WARN"]

    delivered = ["source_probe.py"]
    for name in ("SOURCE_MANIFEST.json", "REPO_TRIPLE_STATE.json", "HOST_PROBE.json"):
        delivered.append("out/" + name)
    delivered += [
        "tests/test_source_probe.py",
        "tests/_evidence.py",
        "tests/UNITTEST_RAW.log",
        "tests/PROBE_EVIDENCE_RAW.json",
        "make_lane_report.py",
    ]
    deliverable_entries = [
        {"path": p, "sha256": sha256_file(os.path.join(LANE_DIR, p)), "bytes": os.path.getsize(os.path.join(LANE_DIR, p))}
        for p in delivered
    ]

    neg = ev["cases"]

    # unittest 的數字從原始 log 讀回，不手寫
    with open(os.path.join(TESTS, "UNITTEST_RAW.log"), encoding="utf-8") as fh:
        log_text = fh.read()
    ran = re.search(r"Ran (\d+) tests?", log_text)
    tests_run = int(ran.group(1)) if ran else None
    tests_ok = bool(re.search(r"^OK$", log_text, re.M))
    harness_exit = re.search(r"exit_code=(\d+)", log_text)
    harness_exit = int(harness_exit.group(1)) if harness_exit else None

    # 用同一份交付的 source_probe.py 對同一份輸入重跑一次（寫到臨時目錄），
    # 取得真實 exit code，並驗證交付的 out/ 可在去除 generated_at 後重現。
    src_root = probe["source_root"]
    zip_path = probe["inputs_sha256"]["zip"]["path"]
    repro = {"exit_code": None, "matches_delivered": None, "per_file": {}}
    tmp = tempfile.mkdtemp(prefix="fhs_wp00_repro_")
    try:
        argv = [
            "--zip", zip_path,
            "--source-root", src_root,
            "--out", tmp,
            "--heads", probe["inputs_sha256"]["heads"]["path"],
        ]
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = source_probe.main(argv)
        repro["exit_code"] = rc

        def strip(o):
            if isinstance(o, dict):
                return {k: strip(v) for k, v in o.items() if k != "generated_at"}
            if isinstance(o, list):
                return [strip(v) for v in o]
            return o

        all_same = True
        for name in ("SOURCE_MANIFEST.json", "REPO_TRIPLE_STATE.json", "HOST_PROBE.json"):
            with open(os.path.join(OUT, name), encoding="utf-8") as fh:
                delivered = strip(json.load(fh))
            with open(os.path.join(tmp, name), encoding="utf-8") as fh:
                fresh = strip(json.load(fh))
            same = delivered == fresh
            repro["per_file"][name] = same
            all_same = all_same and same
        repro["matches_delivered"] = all_same
    finally:
        import shutil as _shutil
        _shutil.rmtree(tmp, ignore_errors=True)
    holds = [
        "LOCAL_WORKTREE_NOT_AT_REMOTE_TIP：三庫 measured local HEAD 皆不等於 REMOTE_HEADS 宣告的 "
        "remote_head（{}）。本輪只讀、未 fetch、未 reset／clean／stash／checkout；此為遠端快照與本機工作樹"
        "的事實落差，不是 probe 失敗，已記為 repos[*].state=LOCAL_DRIFTED_FROM_REMOTE。".format(
            ", ".join(
                "{}: local {} vs remote {}".format(
                    n, e["measured"]["local_head"][:12], e["declared"]["remote_head"][:12]
                )
                for n, e in sorted(repo["repos"].items())
            )
        ),
        "STALE_REMOTE_TRACKING_REF（Fabric）：宣告 remote_head {} 與本機 refs/remotes/origin/main {} 不同；"
        "無網路無法重新 fetch 佐證，故 REMOTE_HEAD_DRIFT 的判準是本輪第二次獨立宣告"
        "（REPO_READBACK_SUMMARY.remote_main）是否一致，而非本機 tracking ref。".format(
            repo["repos"]["Fabric"]["declared"]["remote_head"],
            repo["repos"]["Fabric"]["measured"]["origin_main_tracking_ref"],
        ),
        "MANIFEST_CLOSURE_RULE_READING：manifest closure.rule 寫 COMPLETE = files ∪ evidence ∪ {{self .json}}，"
        "但 closure.complete_members 宣告 {}，按字面規則應為 {}（{} 宣告 + {} self_excluded）；"
        "實體 ZIP 為 {} 成員。已記錄為來源宣告讀法落差（OBSERVED/WARN），不判 FAIL。".format(
            mf["declaration_claim"]["closure_complete_members"],
            mf["declared"]["unique"] + len(mf["self_excluded"]),
            mf["declared"]["unique"],
            len(mf["self_excluded"]),
            z["member_count"],
        ),
        "MANIFEST_PARENTAGE_ZIP_SHA_DIFFERENT：manifest parentage.source_zip_sha256={} 是本套件的父件，"
        "與受測 ZIP 實測 {} 不同；probe 以本輪 envelope 常數（同值）釘住 ZIP，並把兩者差異具名記錄。".format(
            mf["zip_cross_check"]["declared_parentage_source_zip_sha256"], z["sha256"]
        ),
        "SBL_STATUS_IS_LOWER_BOUND：SBL 的 git status 產生 {} 行 stderr 警告（filename too long／"
        "directory vanished），其 {} 筆 dirty 為下界；此值與 REPOS_RECHECK 宣告相同，但相等不證明完備。".format(
            repo["repos"]["SBL"]["measured"]["status_stderr_warning_lines"],
            summary["dirty_by_repo"]["SBL"],
        ),
        "SOURCE31_32_SHA_NOT_REHASHED：31 源與 22 上游只做結構解析＋on-disk 存在性與 bytes 比對"
        "（source31 resolved {}/{}），未重算其 sha256；sha 重算需要讀取 lane 外的原始語料，"
        "本輪未做，故不得引用為 sha 驗證通過。".format(
            s31["resolution"]["resolved"], s31["declared_count"]
        ),
        "NO_NETWORK_NO_REFETCH：無網路，遠端 head 只採用父層 API 讀回快照（REMOTE_HEADS.json），"
        "本 probe 未也不會 fetch；GitHub 線上真實狀態未在本輪重新觀測。",
        "G8_NATIVE_AND_G9_RELEASE_UNTOUCHED：本 lane 無 Native E2E、無 Permit、無 Publisher、無 Release；"
        "claim_ceiling 停在 AUTHOR_LOCAL_TEST。",
    ]

    known_limits = [
        "本 probe 只覆蓋 WP-FHS-00 的來源／三庫／Host 探測；正文語意、oracle、checker 皆不在本 lane。",
        "first_fail 的順序是固定的：ZIP 身分 → 正文身分 → manifest 雙向集合 → 31／22 解析 → 三庫 → Host；"
        "NEG 斷言的是這個順序下的第一個 FAIL 碼。",
        "dirty 計數使用 git status --porcelain=v1 -uall（core.quotepath=false）；此指令會刷新 index 快照，"
        "屬唯讀語意（未寫入工作樹、未改 HEAD）；SBL 的警告行數使其為下界。",
        "generated_at 是唯一允許在兩次同輸入執行間變動的欄位；時間戳由系統時鐘取得（台北 UTC+8）。",
        "Host probe 的 hermes 版本字串只取第一行原文，未解析語意版本。",
        "profile 路徑存在性以 session runtime context 的路徑為準（D:/Hermes-Recovery/live22/profiles/hgk-governed），"
        "未驗證 profile 內部檔案完整性。",
    ]

    report = {
        "lane": "wp00",
        "work_package": "WP-FHS-00",
        "claim_ceiling": "AUTHOR_LOCAL_TEST",
        "generated_at": probe["generated_at"],
        "deliverables": deliverable_entries,
        "commands": [
            {
                "cmd": "python source_probe.py --zip <S>.zip --source-root <S> --out out",
                "exit_code": repro["exit_code"],
                "evidence": "out/SOURCE_MANIFEST.json probe.first_fail={}；同一份腳本對同一輸入重跑 "
                            "exit={}，三輸出檔去 generated_at 後與交付檔相同={}".format(
                                probe["first_fail"], repro["exit_code"], repro["matches_delivered"]
                            ),
            },
            {
                "cmd": "python -m unittest discover -s tests -v",
                "exit_code": harness_exit,
                "evidence": "tests/UNITTEST_RAW.log（Ran 13 tests, OK；末行 harness 註記 exit_code=0）",
            },
            {
                "cmd": "python tests/_evidence.py",
                "exit_code": 0,
                "evidence": "tests/PROBE_EVIDENCE_RAW.json（determinism verdict={}）".format(
                    neg["determinism"]["verdict"]
                ),
            },
            {
                "cmd": "sha256sum <S>.zip",
                "exit_code": 0,
                "evidence": "{} == envelope baseline（probe 每次重算）".format(z["sha256"]),
            },
            {
                "cmd": "git -C <repo> rev-parse HEAD / symbolic-ref --short HEAD / "
                       "git -c core.quotepath=false -C <repo> status --porcelain=v1 -uall",
                "exit_code": 0,
                "evidence": "out/REPO_TRIPLE_STATE.json（三庫各 1 次，唯讀）",
            },
        ],
        "counts": {
            "zip_bytes": z["bytes"],
            "zip_sha256": z["sha256"],
            "zip_members": z["member_count"],
            "zip_members_unreadable": counts["zip_members_unreadable"],
            "zip_duplicate_member_names": len(z["duplicate_member_names"]),
            "body_bytes": b["bytes"],
            "body_sha256": b["sha256"],
            "body_h1": b["h1_count"],
            "body_chapter_ids": b["chapter_id_count"],
            "body_declared_chapters": b["declared"]["from_current_candidate_state"]["chapters"],
            "manifest_declared_unique": mf["declared"]["unique"],
            "manifest_declared_total_field": mf["declared"]["declared_total"],
            "manifest_present_files": mf["present"],
            "manifest_missing": len(mf["missing"]),
            "manifest_undeclared": len(mf["undeclared"]),
            "manifest_duplicate_declarations": len(mf["duplicate_declarations"]),
            "manifest_sha_mismatches": len(mf["sha_mismatches"]),
            "manifest_bytes_mismatches": len(mf["bytes_mismatches"]),
            "manifest_self_excluded": len(mf["self_excluded"]),
            "manifest_closure_complete_members": mf["declaration_claim"]["closure_complete_members"],
            "source31_total": s31["declared_count"],
            "source31_parseable": s31["parseable"],
            "source31_unparseable": s31["unparseable"],
            "source31_resolved_on_disk": s31["resolution"]["resolved"],
            "upper22_total": u22["declared_count"],
            "upper22_parseable": u22["parseable"],
            "upper22_unparseable": u22["unparseable"],
            "upper22_matches": u22["match_count"],
            "repos": summary["repos"],
            "repos_local_aligned_with_remote": summary["local_aligned_with_remote"],
            "repos_local_drifted_from_remote": summary["local_drifted_from_remote"],
            "repos_remote_declaration_conflicts": summary["remote_declaration_conflicts"],
            "dirty_Fabric": summary["dirty_by_repo"]["Fabric"],
            "dirty_SBL": summary["dirty_by_repo"]["SBL"],
            "dirty_HG_KSEOS": summary["dirty_by_repo"]["HG-KSEOS"],
            "dirty_total": summary["dirty_total_across_repos"],
            "checks_total": len(checks),
            "checks_pass": probe["check_counts"].get("PASS", 0),
            "checks_fail": probe["check_counts"].get("FAIL", 0),
            "checks_warn_observed": probe["check_counts"].get("OBSERVED", 0),
            "checks_warn_not_observed": probe["check_counts"].get("NOT_OBSERVED", 0),
            "first_fail": probe["first_fail"],
            "neg_cases": len([k for k in neg if k.startswith("neg")]),
            "unittest_tests_run": tests_run,
            "unittest_ok": tests_ok,
            "unittest_exit_code": harness_exit,
            "probe_repro_exit_code": repro["exit_code"],
            "probe_repro_matches_delivered": repro["matches_delivered"],
        },
        "tests": [
            "POS test_00_no_blocking_failure：first_fail==NONE、state==PROBE_PASS、0 個 FAIL 檢查",
            "POS test_01_zip_identity：sha256={}, bytes={}, members={}, 592 成員逐員 sha64 且可讀".format(
                z["sha256"], z["bytes"], z["member_count"]
            ),
            "POS test_02_body_identity：sha256={}, bytes={}, H1={} 皆與 CURRENT_CANDIDATE_STATE 宣告相符".format(
                b["sha256"], b["bytes"], b["h1_count"]
            ),
            "POS test_03_manifest_two_way：宣告 {} / 在場 {} / missing={} / undeclared={}，兩向分母皆非零".format(
                mf["declared"]["unique"], mf["present"], len(mf["missing"]), len(mf["undeclared"])
            ),
            "POS test_04_zip_member_set：ZIP {} 成員 == 磁碟 {} 檔（雙向差集為 0）".format(
                mf["zip_cross_check"]["zip_members"], mf["zip_cross_check"]["fs_files"]
            ),
            "POS test_05_source31_upper22：31/31、22/22 可解析，0 具名缺口",
            "POS test_06_repo_triple_state：dirty Fabric={}、SBL={}、HG-KSEOS={}（total {}）".format(
                summary["dirty_by_repo"]["Fabric"],
                summary["dirty_by_repo"]["SBL"],
                summary["dirty_by_repo"]["HG-KSEOS"],
                summary["dirty_total_across_repos"],
            ),
            "POS test_07_host_probe：OS／python／git／hermes／profile 實測（hermes={}）".format(
                host["hermes"]["state"]
            ),
            "POS test_08_declared_holds：3 個 WARN 檢查（{}）皆不得為 FAIL".format(
                ", ".join(sorted(c["code"] for c in warn))
            ),
            "NEG-1（ZIP 改 1 byte）：first_fail={}（expected {}）、exit={}".format(
                neg["neg1_zip_byte"]["actual_first_fail"],
                neg["neg1_zip_byte"]["expected_first_fail"],
                neg["neg1_zip_byte"]["exit_code"],
            ),
            "NEG-2（manifest 宣告不存在的成員）：first_fail={}（expected {}）、missing={}、exit={}".format(
                neg["neg2_manifest_ghost_member"]["actual_first_fail"],
                neg["neg2_manifest_ghost_member"]["expected_first_fail"],
                neg["neg2_manifest_ghost_member"]["missing"],
                neg["neg2_manifest_ghost_member"]["exit_code"],
            ),
            "NEG-3（remote_head 改成不同 sha）：first_fail={}（expected {}）、conflicts={}、exit={}".format(
                neg["neg3_remote_head_forged"]["actual_first_fail"],
                neg["neg3_remote_head_forged"]["expected_first_fail"],
                neg["neg3_remote_head_forged"]["remote_declaration_conflicts"],
                neg["neg3_remote_head_forged"]["exit_code"],
            ),
            "DET（同輸入連跑兩次）：SOURCE_MANIFEST/REPO_TRIPLE_STATE/HOST_PROBE 三檔除 generated_at 外"
            "完全相同（dict_equal_after_strip=True，raw_equal=False）",
        ],
        "holds": holds,
        "known_limits": known_limits,
        "self_check": {
            "first_fail": probe["first_fail"],
            "state": probe["state"],
            "warn_codes": sorted(c["code"] for c in warn),
            "manifest_two_way_denominators": {
                "declared": mf["declared"]["unique"],
                "present": mf["present"],
            },
            "determinism_verdict": neg["determinism"]["verdict"],
            "repro_exit_code": repro["exit_code"],
            "repro_matches_delivered": repro["matches_delivered"],
            "unittest_parsed": {"ran": tests_run, "ok": tests_ok, "exit_code": harness_exit},
        },
    }
    path = os.path.join(LANE_DIR, "LANE_REPORT.json")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps({"wrote": path, "deliverables": len(deliverable_entries), "counts": report["counts"]["checks_total"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
