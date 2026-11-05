#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-00 source_probe 驗收測試（unittest，標準庫）。

POS：真實 ZIP + 真實正文 + 真實 source root，跑一次必須 first_fail == "NONE"。
NEG（三份，每份都用臨時複本突變，真實來源不被寫入）：
  NEG-1  ZIP 改一個 byte        -> first_fail == SOURCE_ZIP_SHA_MISMATCH
  NEG-2  manifest 宣告不存在的成員 -> first_fail == MANIFEST_MEMBER_MISSING
  NEG-3  remote_head 改成不同 sha -> first_fail == REMOTE_HEAD_DRIFT

每條斷言都指名錯誤碼（first_fail 與 checks[].code 的 state），不只看 exit code。
執行：cd lanes/wp00 && python -m unittest discover -s tests -v
"""

import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, LANE)

import source_probe  # noqa: E402

SRC = os.environ.get(
    "FHS_SRC_ROOT",
    "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
    "Semantic World OS Fabric/FHS／FHS-MSC／SBL/FHS/PIPD-LS-PKG/定案/W0/"
    "FHS_PIPD-LS-PKG_W0_R4C",
)
ZIP = os.environ.get("FHS_ZIP", SRC + ".zip")
HEADS = os.environ.get(
    "FHS_HEADS",
    "C:/Projects/Agent_Workspace/var/FHS_W0_IMPLEMENTATION_20261105_0305/"
    "source_readback/REMOTE_HEADS.json",
)

# 量測得到的真相（2026-11-05 本機實測；測試會重新量測並與這些值比對）
EXPECT_ZIP_SHA = "f3838fb095e56ea8d636e5c52f4bd69e9d529d110569b87376c168ea35ab2a2a"
EXPECT_ZIP_BYTES = 3281542
EXPECT_ZIP_MEMBERS = 592
EXPECT_BODY_SHA = "56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a"
EXPECT_BODY_BYTES = 463034
EXPECT_BODY_H1 = 50
EXPECT_DECLARED = 591
EXPECT_PRESENT = 592
EXPECT_SOURCE31 = 31
EXPECT_UPPER22 = 22
EXPECT_DIRTY = {"Fabric": 1948, "SBL": 58837, "HG-KSEOS": 2}


def _require_inputs():
    missing = [p for p in (SRC, ZIP, HEADS) if not os.path.exists(p)]
    if missing:
        raise unittest.SkipTest("input(s) absent: {}".format(missing))


def _strip_generated_at(obj):
    if isinstance(obj, dict):
        return {
            k: _strip_generated_at(v)
            for k, v in obj.items()
            if k != "generated_at"
        }
    if isinstance(obj, list):
        return [_strip_generated_at(v) for v in obj]
    return obj


def _read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def _run(tmpdir, **overrides):
    kwargs = dict(
        zip_path=ZIP,
        source_root=SRC,
        out_dir=tmpdir,
        expect_zip_sha=EXPECT_ZIP_SHA,
        heads_path=HEADS,
        generated_at="2026-11-05T03:30:00+08:00",
    )
    kwargs.update(overrides)
    return source_probe.run_probe(**kwargs)


def _run_cli(out_dir, **overrides):
    """走真正的 CLI 路徑（argparse + main()），回傳 (rc, manifest_json)。"""
    import contextlib
    import io

    argv = ["--zip", overrides.get("zip_path", ZIP),
            "--source-root", overrides.get("source_root", SRC),
            "--out", out_dir,
            "--expect-zip-sha", overrides.get("expect_zip_sha", EXPECT_ZIP_SHA),
            "--heads", overrides.get("heads_path", HEADS),
            "--generated-at", "2026-11-05T03:30:00+08:00"]
    if overrides.get("manifest_path"):
        argv += ["--manifest", overrides["manifest_path"]]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = source_probe.main(argv)
    with open(os.path.join(out_dir, "SOURCE_MANIFEST.json"), encoding="utf-8") as fh:
        man = json.load(fh)
    return rc, man, buf.getvalue()


def _check(manifest_out, code):
    for c in manifest_out["probe"]["checks"]:
        if c["code"] == code:
            return c
    raise AssertionError("check code {} not present in ledger".format(code))


class PosRealInputs(unittest.TestCase):
    """POS：真實 ZIP、真實正文、真實 source root。"""

    @classmethod
    def setUpClass(cls):
        _require_inputs()
        cls.tmp = tempfile.mkdtemp(prefix="fhs_wp00_pos_")
        cls.man, cls.repo, cls.host, cls.paths = _run(cls.tmp)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_00_no_blocking_failure(self):
        self.assertEqual(self.man["probe"]["first_fail"], "NONE")
        self.assertEqual(self.man["probe"]["state"], "PROBE_PASS")
        failed = [c for c in self.man["probe"]["checks"] if c["state"] == "FAIL"]
        self.assertEqual(failed, [], "no check may be FAIL on real inputs")

    def test_01_zip_identity(self):
        z = self.man["source_zip"]
        self.assertEqual(z["sha256"], EXPECT_ZIP_SHA)
        self.assertEqual(z["bytes"], EXPECT_ZIP_BYTES)
        self.assertEqual(z["member_count"], EXPECT_ZIP_MEMBERS)
        self.assertTrue(z["sha_matches_expected"])
        self.assertEqual(z["duplicate_member_names"], [])
        self.assertEqual(
            sum(1 for m in z["members"] if not m.get("readable")), 0, "all members readable"
        )
        for m in z["members"]:
            self.assertRegex(m["sha256"], r"^[0-9a-f]{64}$")

    def test_02_body_identity_matches_state_declaration(self):
        b = self.man["body"]
        self.assertEqual(b["sha256"], EXPECT_BODY_SHA)
        self.assertEqual(b["bytes"], EXPECT_BODY_BYTES)
        self.assertEqual(b["h1_count"], EXPECT_BODY_H1)
        self.assertEqual(b["chapter_id_count"], EXPECT_BODY_H1)
        self.assertTrue(b["matches"]["sha256_state"])
        self.assertTrue(b["matches"]["bytes_state"])
        self.assertTrue(b["matches"]["chapters_state"])
        self.assertEqual(_check(self.man, "BODY_SHA_MISMATCH")["state"], "PASS")
        self.assertEqual(_check(self.man, "BODY_CHAPTER_COUNT_MISMATCH")["state"], "PASS")

    def test_03_manifest_two_way_sets_nonzero_denominators(self):
        m = self.man["manifest"]
        self.assertEqual(m["declared"]["unique"], EXPECT_DECLARED)
        self.assertEqual(m["present"], EXPECT_PRESENT)
        self.assertEqual(m["missing"], [])
        self.assertEqual(m["undeclared"], [])
        self.assertEqual(m["duplicate_declarations"], [])
        self.assertEqual(m["sha_mismatches"], [])
        self.assertEqual(m["bytes_mismatches"], [])
        self.assertEqual(m["self_excluded"], ["INDEX_AND_MANIFEST_r4-candidate-b41d2e.json"])
        # 雙向比對的分母都必須非零
        self.assertGreater(len(m["missing"]) + self.man["counts"]["manifest_declared_unique"], 0)
        self.assertGreater(self.man["counts"]["manifest_present_files"], 0)
        self.assertGreater(self.man["counts"]["manifest_declared_unique"], 0)
        self.assertIn("0 of 591 declared members absent", _check(self.man, "MANIFEST_MEMBER_MISSING")["detail"])
        self.assertIn("0 of 592 present files undeclared", _check(self.man, "MANIFEST_MEMBER_UNDECLARED")["detail"])

    def test_04_zip_member_set_equals_disk_set(self):
        cc = self.man["manifest"]["zip_cross_check"]
        self.assertEqual(cc["count_in_zip_not_on_disk"], 0)
        self.assertEqual(cc["count_on_disk_not_in_zip"], 0)
        self.assertEqual(cc["zip_members"], cc["fs_files"])

    def test_05_source31_and_upper22_census(self):
        self.assertEqual(self.man["source31"]["declared_count"], EXPECT_SOURCE31)
        self.assertEqual(self.man["source31"]["parseable"], EXPECT_SOURCE31)
        self.assertEqual(self.man["source31"]["unparseable"], 0)
        self.assertEqual(self.man["source31"]["physical_identity_states"], {"PASS": EXPECT_SOURCE31})
        self.assertEqual(self.man["source31"]["gaps"], [])
        self.assertEqual(self.man["upper22"]["declared_count"], EXPECT_UPPER22)
        self.assertEqual(self.man["upper22"]["parseable"], EXPECT_UPPER22)
        self.assertEqual(self.man["upper22"]["unparseable"], 0)
        self.assertEqual(self.man["upper22"]["states"], {"IDENTITY_MATCH": EXPECT_UPPER22})
        self.assertEqual(self.man["upper22"]["gaps"], [])

    def test_06_repo_triple_state_dirty_counts(self):
        repos = self.repo["repos"]
        self.assertEqual(sorted(repos), ["Fabric", "HG-KSEOS", "SBL"])
        measured = {n: repos[n]["measured"]["dirty_count"] for n in repos}
        self.assertEqual(measured, EXPECT_DIRTY)
        self.assertEqual(self.repo["summary"]["dirty_total_across_repos"], sum(EXPECT_DIRTY.values()))
        for name, entry in repos.items():
            self.assertRegex(entry["measured"]["local_head"], r"^[0-9a-f]{40}$")
            self.assertEqual(entry["state"], "LOCAL_DRIFTED_FROM_REMOTE")
            self.assertFalse(entry["flags"]["local_equals_remote"])
            self.assertTrue(entry["flags"]["local_head_matches_declaration"])
            self.assertTrue(entry["flags"]["remote_declaration_corroborated"])

    def test_07_host_probe_observations(self):
        h = self.host
        self.assertEqual(h["os"]["system"], "Windows")
        self.assertRegex(h["python"]["version"], r"^3\.\d+\.\d+")
        self.assertRegex(h["git"]["version"], r"^git version")
        self.assertIn(h["hermes"]["state"], ("OBSERVED", "NOT_OBSERVED"))
        if h["hermes"]["state"] == "OBSERVED":
            self.assertTrue(h["hermes"]["version_raw_first_line"])
        self.assertTrue(h["profile"]["runtime_profile_path"]["exists"])
        self.assertEqual(_check(self.man, "HOST_PROFILE_PATH_MISSING")["state"], "PASS")

    def test_08_declared_holds_are_warn_not_fail(self):
        obs = {c["code"]: c for c in self.man["probe"]["checks"] if c["severity"] == "WARN"}
        self.assertIn("MANIFEST_CLOSURE_RULE_READING", obs)
        self.assertEqual(obs["MANIFEST_CLOSURE_RULE_READING"]["state"], "OBSERVED")
        # Fabric 的本機 origin/main 落後 API 讀到的遠端 head：記錄，不判 FAIL
        self.assertIn("REMOTE_TRACKING_REF_STALE", obs)
        for code, c in obs.items():
            self.assertNotEqual(c["state"], "FAIL", "WARN check {} must not be FAIL".format(code))


class NegZipByteMutation(unittest.TestCase):
    """NEG-1：ZIP 改一個 byte -> SOURCE_ZIP_SHA_MISMATCH。"""

    def test_first_fail_is_zip_sha_mismatch(self):
        _require_inputs()
        tmp = tempfile.mkdtemp(prefix="fhs_wp00_neg1_")
        try:
            bad_zip = os.path.join(tmp, "mutated.zip")
            shutil.copy2(ZIP, bad_zip)
            size = os.path.getsize(bad_zip)
            offset = size // 2
            with open(bad_zip, "r+b") as fh:
                fh.seek(offset)
                original = fh.read(1)
                fh.seek(offset)
                fh.write(bytes([original[0] ^ 0xFF]))
            with open(bad_zip, "rb") as fh:
                mutated_sha = hashlib.sha256(fh.read()).hexdigest()
            self.assertNotEqual(mutated_sha, EXPECT_ZIP_SHA, "mutation must change the file hash")

            out = os.path.join(tmp, "out")
            rc, man, _stdout = _run_cli(out, zip_path=bad_zip)
            self.assertEqual(rc, 3, "CLI must exit 3 on a blocking failure")
            self.assertEqual(man["probe"]["first_fail"], "SOURCE_ZIP_SHA_MISMATCH")
            self.assertEqual(man["probe"]["state"], "PROBE_FAIL")
            first = [c for c in man["probe"]["checks"] if c["state"] == "FAIL"][0]
            self.assertEqual(first["code"], "SOURCE_ZIP_SHA_MISMATCH")
            self.assertEqual(first["seq"], 1)
            self.assertEqual(man["source_zip"]["sha256"], mutated_sha)
            self.assertFalse(man["source_zip"]["sha_matches_expected"])
            self.assertIn(mutated_sha, first["detail"])
            self.assertIn(EXPECT_ZIP_SHA, first["detail"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class NegManifestDeclaresAbsentMember(unittest.TestCase):
    """NEG-2：manifest 宣告一個不存在的成員 -> MANIFEST_MEMBER_MISSING。"""

    def test_first_fail_is_manifest_member_missing(self):
        _require_inputs()
        tmp = tempfile.mkdtemp(prefix="fhs_wp00_neg2_")
        try:
            src_manifest = os.path.join(SRC, source_probe.MANIFEST_NAME)
            with open(src_manifest, encoding="utf-8") as fh:
                data = json.load(fh)
            ghost = "NEGATIVE_PROBE_DECLARED_BUT_ABSENT.md"
            data["files"].append(
                {
                    "path": ghost,
                    "role": "supporting",
                    "note": "injected by tests/test_source_probe.py NEG-2",
                    "sha256": "0" * 64,
                    "bytes": 1,
                }
            )
            bad_manifest = os.path.join(tmp, "INDEX_MUTATED.json")
            with open(bad_manifest, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(data, fh, ensure_ascii=False, indent=2)

            out = os.path.join(tmp, "out")
            rc, man, _stdout = _run_cli(out, manifest_path=bad_manifest)
            self.assertEqual(rc, 3, "CLI must exit 3 on a blocking failure")
            self.assertEqual(man["probe"]["first_fail"], "MANIFEST_MEMBER_MISSING")
            first = [c for c in man["probe"]["checks"] if c["state"] == "FAIL"][0]
            self.assertEqual(first["code"], "MANIFEST_MEMBER_MISSING")
            self.assertIn(ghost, man["manifest"]["missing"])
            self.assertEqual(len(man["manifest"]["missing"]), 1)
            self.assertEqual(man["manifest"]["undeclared"], [])
            # 前面的 ZIP 身分檢查仍必須是 PASS（證明紅燈來自這一層）
            self.assertEqual(_check(man, "SOURCE_ZIP_SHA_MISMATCH")["state"], "PASS")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class NegRemoteHeadDrift(unittest.TestCase):
    """NEG-3：remote_head 改成不同 sha -> REMOTE_HEAD_DRIFT。"""

    def test_first_fail_is_remote_head_drift(self):
        _require_inputs()
        tmp = tempfile.mkdtemp(prefix="fhs_wp00_neg3_")
        try:
            with open(HEADS, encoding="utf-8") as fh:
                heads = json.load(fh)
            real_remote = heads["repos"]["SBL"]["remote_head"]
            forged = "abcdef0123456789" * 2 + "abcdef01"  # 40 hex, 與任何真實 head 不同
            self.assertEqual(len(forged), 40)
            self.assertNotEqual(forged, real_remote)
            heads["repos"]["SBL"]["remote_head"] = forged
            bad_heads = os.path.join(tmp, "REMOTE_HEADS_MUTATED.json")
            with open(bad_heads, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(heads, fh, ensure_ascii=False, indent=2)

            out = os.path.join(tmp, "out")
            rc, man, _stdout = _run_cli(out, heads_path=bad_heads)
            self.assertEqual(rc, 3, "CLI must exit 3 on a blocking failure")
            with open(os.path.join(out, "REPO_TRIPLE_STATE.json"), encoding="utf-8") as fh:
                repo = json.load(fh)
            self.assertEqual(man["probe"]["first_fail"], "REMOTE_HEAD_DRIFT")
            first = [c for c in man["probe"]["checks"] if c["state"] == "FAIL"][0]
            self.assertEqual(first["code"], "REMOTE_HEAD_DRIFT")
            self.assertIn(forged, first["detail"])
            self.assertIn(real_remote, first["detail"])

            sbl = repo["repos"]["SBL"]
            self.assertFalse(sbl["flags"]["remote_declaration_corroborated"])
            self.assertEqual(sbl["declared"]["remote_head"], forged)
            self.assertEqual(sbl["declared"]["remote_main_readback"], real_remote)
            self.assertEqual(repo["summary"]["remote_declaration_conflicts"], 1)
            # 未突變的兩庫仍被背書
            self.assertTrue(repo["repos"]["Fabric"]["flags"]["remote_declaration_corroborated"])
            self.assertTrue(repo["repos"]["HG-KSEOS"]["flags"]["remote_declaration_corroborated"])
            # 前面的結構層檢查仍為 PASS（紅燈只來自 repo 宣告層）
            for code in (
                "SOURCE_ZIP_SHA_MISMATCH",
                "BODY_SHA_MISMATCH",
                "MANIFEST_MEMBER_MISSING",
                "MANIFEST_MEMBER_UNDECLARED",
                "SOURCE31_PARSE_GAP",
                "UPPER22_PARSE_GAP",
            ):
                self.assertEqual(_check(man, code)["state"], "PASS", code)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


class Determinism(unittest.TestCase):
    """同一 out 目錄連跑兩次、同一 generated_at -> 三個輸出檔 byte-identical；
    不同 generated_at -> 除 generated_at 外完全相同。"""

    def test_two_runs_identical_except_generated_at(self):
        _require_inputs()
        tmp = tempfile.mkdtemp(prefix="fhs_wp00_det_")
        try:
            out = os.path.join(tmp, "out")  # 同一個 out 目錄，排除路徑回聲差異
            names = ["SOURCE_MANIFEST.json", "REPO_TRIPLE_STATE.json", "HOST_PROBE.json"]

            _run(out, generated_at="2026-11-05T03:30:00+08:00")
            first_bytes = {n: _read_bytes(os.path.join(out, n)) for n in names}
            _run(out, generated_at="2026-11-05T03:30:00+08:00")
            second_bytes = {n: _read_bytes(os.path.join(out, n)) for n in names}
            _run(out, generated_at="2026-11-05T04:45:59+08:00")
            third_bytes = {n: _read_bytes(os.path.join(out, n)) for n in names}

            for name in names:
                self.assertEqual(
                    first_bytes[name], second_bytes[name],
                    "{} differs between two identical runs".format(name),
                )
                self.assertNotEqual(
                    first_bytes[name], third_bytes[name],
                    "{} should differ only in generated_at".format(name),
                )
                ja = _strip_generated_at(json.loads(first_bytes[name].decode("utf-8")))
                jc = _strip_generated_at(json.loads(third_bytes[name].decode("utf-8")))
                self.assertEqual(ja, jc, "{} differs beyond generated_at".format(name))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
