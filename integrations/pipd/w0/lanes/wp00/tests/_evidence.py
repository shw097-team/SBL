#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""量測用證據腳本（不是 unittest，不會被 discover 收集）。

產出 tests/PROBE_EVIDENCE_RAW.json，內容全部是實跑量到的：
  1) determinism：同一 out 目錄連跑兩次（generated_at 不同），
     逐檔比對 byte 相同 / 去 generated_at 後 dict 相同，並記錄每次的 sha256。
  2) neg：三個突變各自走真正 CLI，記錄 first_fail 與 exit code。
"""

import contextlib
import hashlib
import io
import json
import os
import shutil
import sys
import tempfile

LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LANE)
sys.path.insert(0, os.path.join(LANE, "tests"))

import source_probe  # noqa: E402
from test_source_probe import (  # noqa: E402
    EXPECT_ZIP_SHA,
    HEADS,
    SRC,
    ZIP,
    _strip_generated_at,
)

OUT = os.path.join(LANE, "tests", "PROBE_EVIDENCE_RAW.json")
NAMES = ["SOURCE_MANIFEST.json", "REPO_TRIPLE_STATE.json", "HOST_PROBE.json"]


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def call_cli(out_dir, **kw):
    argv = [
        "--zip", kw.get("zip_path", ZIP),
        "--source-root", kw.get("source_root", SRC),
        "--out", out_dir,
        "--expect-zip-sha", kw.get("expect_zip_sha", EXPECT_ZIP_SHA),
        "--heads", kw.get("heads_path", HEADS),
        "--generated-at", kw.get("generated_at", "2026-11-05T03:30:00+08:00"),
    ]
    if kw.get("manifest_path"):
        argv += ["--manifest", kw["manifest_path"]]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = source_probe.main(argv)
    with open(os.path.join(out_dir, "SOURCE_MANIFEST.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    return rc, man


def read(path):
    with open(path, "rb") as fh:
        return fh.read()


def main():
    result = {"command": "python tests/_evidence.py", "cases": {}}

    # ---- 1) determinism
    tmp = tempfile.mkdtemp(prefix="fhs_wp00_ev_det_")
    try:
        out = os.path.join(tmp, "out")
        snapshots = []
        for stamp in ("2026-11-05T03:30:00+08:00", "2026-11-05T04:47:13+08:00"):
            rc, man = call_cli(out, generated_at=stamp)
            snap = {"generated_at": stamp, "exit_code": rc, "files": {}}
            for name in NAMES:
                data = read(os.path.join(out, name))
                snap["files"][name] = {
                    "sha256": sha_bytes(data),
                    "bytes": len(data),
                }
            snap["first_fail"] = man["probe"]["first_fail"]
            snapshots.append((snap, man))
        a_snap, a_man = snapshots[0]
        b_snap, b_man = snapshots[1]
        per_file = {}
        for name in NAMES:
            ja = _strip_generated_at(
                json.loads(read(os.path.join(tmp, "out", name)).decode("utf-8"))
            )
            per_file[name] = {
                "sha256_run1": a_snap["files"][name]["sha256"],
                "sha256_run2": b_snap["files"][name]["sha256"],
                "byte_identical": a_snap["files"][name]["sha256"]
                == b_snap["files"][name]["sha256"],
                "differs_only_in_generated_at": True,  # rewritten below with the real comparison
            }
        # 真正的比對：重新各跑一次到兩個新目錄，用同一 out 內容讀回來比 dict
        dir_a = os.path.join(tmp, "a")
        dir_b = os.path.join(tmp, "b")
        call_cli(dir_a, generated_at="2026-11-05T03:30:00+08:00")
        call_cli(dir_b, generated_at="2026-11-05T04:47:13+08:00")
        for name in NAMES:
            ja = _strip_generated_at(json.loads(read(os.path.join(dir_a, name)).decode("utf-8")))
            jb = _strip_generated_at(json.loads(read(os.path.join(dir_b, name)).decode("utf-8")))
            same_after_strip = ja == jb
            raw_a = read(os.path.join(dir_a, name))
            raw_b = read(os.path.join(dir_b, name))
            per_file[name]["differs_only_in_generated_at"] = (
                same_after_strip and raw_a != raw_b
            )
            per_file[name]["dict_equal_after_strip"] = same_after_strip
            per_file[name]["raw_equal"] = raw_a == raw_b
        result["cases"]["determinism"] = {
            "run1": a_snap,
            "run2": b_snap,
            "per_file": per_file,
            "verdict": "PASS"
            if all(v["differs_only_in_generated_at"] for v in per_file.values())
            else "FAIL",
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- 2) NEG 1: zip byte mutation
    tmp = tempfile.mkdtemp(prefix="fhs_wp00_ev_neg1_")
    try:
        bad_zip = os.path.join(tmp, "mutated.zip")
        shutil.copy2(ZIP, bad_zip)
        size = os.path.getsize(bad_zip)
        off = size // 2
        with open(bad_zip, "r+b") as fh:
            fh.seek(off)
            byte = fh.read(1)
            fh.seek(off)
            fh.write(bytes([byte[0] ^ 0xFF]))
        rc, man = call_cli(os.path.join(tmp, "out"), zip_path=bad_zip)
        result["cases"]["neg1_zip_byte"] = {
            "mutation": "single byte XOR 0xFF at offset {} (of {})".format(off, size),
            "expected_first_fail": "SOURCE_ZIP_SHA_MISMATCH",
            "actual_first_fail": man["probe"]["first_fail"],
            "exit_code": rc,
            "measured_zip_sha256": man["source_zip"]["sha256"],
            "expected_zip_sha256": EXPECT_ZIP_SHA,
            "file_sha_changed": man["source_zip"]["sha256"] != EXPECT_ZIP_SHA,
            "first_fail_check_seq": [
                c["seq"] for c in man["probe"]["checks"] if c["state"] == "FAIL"
            ][:1],
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- 3) NEG 2: manifest declares an absent member
    tmp = tempfile.mkdtemp(prefix="fhs_wp00_ev_neg2_")
    try:
        with open(os.path.join(SRC, source_probe.MANIFEST_NAME), encoding="utf-8") as fh:
            data = json.load(fh)
        ghost = "NEGATIVE_PROBE_DECLARED_BUT_ABSENT.md"
        data["files"].append(
            {
                "path": ghost,
                "role": "supporting",
                "note": "injected by tests/_evidence.py NEG-2",
                "sha256": "0" * 64,
                "bytes": 1,
            }
        )
        bad_manifest = os.path.join(tmp, "INDEX_MUTATED.json")
        with open(bad_manifest, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
        rc, man = call_cli(os.path.join(tmp, "out"), manifest_path=bad_manifest)
        result["cases"]["neg2_manifest_ghost_member"] = {
            "mutation": "append declared files[] entry for {}".format(ghost),
            "expected_first_fail": "MANIFEST_MEMBER_MISSING",
            "actual_first_fail": man["probe"]["first_fail"],
            "exit_code": rc,
            "missing": man["manifest"]["missing"],
            "undeclared": man["manifest"]["undeclared"],
            "declared_unique": man["manifest"]["declared"]["unique"],
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # ---- 4) NEG 3: remote_head forged
    tmp = tempfile.mkdtemp(prefix="fhs_wp00_ev_neg3_")
    try:
        with open(HEADS, encoding="utf-8") as fh:
            heads = json.load(fh)
        real = heads["repos"]["SBL"]["remote_head"]
        forged = "abcdef0123456789" * 2 + "abcdef01"
        heads["repos"]["SBL"]["remote_head"] = forged
        bad_heads = os.path.join(tmp, "REMOTE_HEADS_MUTATED.json")
        with open(bad_heads, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(heads, fh, ensure_ascii=False, indent=2)
        rc, man = call_cli(os.path.join(tmp, "out"), heads_path=bad_heads)
        with open(os.path.join(tmp, "out", "REPO_TRIPLE_STATE.json"), encoding="utf-8") as fh:
            repo = json.load(fh)
        result["cases"]["neg3_remote_head_forged"] = {
            "mutation": "REMOTE_HEADS.repos.SBL.remote_head -> {}".format(forged),
            "expected_first_fail": "REMOTE_HEAD_DRIFT",
            "actual_first_fail": man["probe"]["first_fail"],
            "exit_code": rc,
            "real_readback_remote_main": real,
            "declared_remote_head": repo["repos"]["SBL"]["declared"]["remote_head"],
            "remote_declaration_conflicts": repo["summary"]["remote_declaration_conflicts"],
            "clean_repos_corroborated": [
                n
                for n, e in repo["repos"].items()
                if e["flags"]["remote_declaration_corroborated"]
            ],
        }
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2, sort_keys=True)
        fh.write("\n")
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    ok = result["cases"]["determinism"]["verdict"] == "PASS" and all(
        result["cases"][k]["actual_first_fail"] == result["cases"][k]["expected_first_fail"]
        and result["cases"][k]["exit_code"] == 3
        for k in ("neg1_zip_byte", "neg2_manifest_ghost_member", "neg3_remote_head_forged")
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
