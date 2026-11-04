#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-01 authority_router 的 unittest 套件。

POS：對真實 R4C 來源根跑出 31 筆（分母取自 SOURCE31_PHYSICAL_IDENTITY.json 實際筆數），
     每筆都有可解析的 evidence_field，五類齊備，may_authorize_write / may_mint_permit 全 false，
     且真實來源上出現的四個具名 HOLD 都在。
NEG：五個合成 fixture，各自斷言「具體碼」——mirror-as-authority、skill-as-permit、
     dual canonical、scope missing、profile/role conflation。
UNIT：寫入閘門不是恆假函數（真值表逐項驗）。

執行：python -m unittest -v tests.test_authority_router  （於 lanes/wp01 下）
"""

import json
import os
import subprocess
import sys
import unittest

LANE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROUTER = os.path.join(LANE, "authority_router.py")
TESTS = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(TESTS, "fixtures")
TMP = os.path.join(TESTS, "_tmp")

REAL_ROOT = os.environ.get(
    "FHS_R4C_SOURCE_ROOT",
    "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/"
    "FHS／FHS-MSC／SBL/FHS/PIPD-LS-PKG/定案/W0/FHS_PIPD-LS-PKG_W0_R4C",
)

sys.path.insert(0, LANE)
import authority_router as ar  # noqa: E402


def run_router(root, out, readback=None):
    argv = [sys.executable, ROUTER, "--source-root", root, "--out", out, "--quiet"]
    if readback is not None:
        argv += ["--readback-root", readback]
    return subprocess.run(argv, capture_output=True, text=True, encoding="utf-8",
                          cwd=LANE)


def load_out(out_dir):
    with open(os.path.join(out_dir, "AUTHORITY_ROUTING.json"), encoding="utf-8") as fh:
        return json.load(fh)


def rows_by_id(doc):
    return {row["source_id"]: row for row in doc["entries"]}


def holds_by_code(doc):
    out = {}
    for hold in doc["holds"]:
        out.setdefault(hold["code"], []).append(hold)
    return out


class RealCorpusPOS(unittest.TestCase):
    """POS：真實來源 31 筆分類 + 全欄位證據 + 五類齊備 + 真實 HOLD。"""

    @classmethod
    def setUpClass(cls):
        if not os.path.isdir(REAL_ROOT):
            raise unittest.SkipTest("real R4C source root not present: %s" % REAL_ROOT)
        cls.out = os.path.join(TMP, "pos_out")
        os.makedirs(TMP, exist_ok=True)
        cls.proc = run_router(REAL_ROOT, cls.out)
        if cls.proc.returncode != 0:
            raise AssertionError("router failed: rc=%s stderr=%s"
                                 % (cls.proc.returncode, cls.proc.stderr))
        cls.doc = load_out(cls.out)
        with open(os.path.join(REAL_ROOT, "SOURCE31_PHYSICAL_IDENTITY.json"),
                  encoding="utf-8") as fh:
            cls.src31 = json.load(fh)

    def test_01_exit_zero_and_artifacts_written(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr)
        self.assertTrue(os.path.isfile(os.path.join(self.out, "AUTHORITY_ROUTING.json")))
        self.assertTrue(os.path.isfile(os.path.join(self.out, "AUTHORITY_ROUTING.md")))
        self.assertGreater(os.path.getsize(os.path.join(self.out, "AUTHORITY_ROUTING.md")), 2000)

    def test_02_source31_denominator_not_shrunk(self):
        declared = len(self.src31)
        self.assertEqual(declared, self.doc["statistics"]["source31_declared"])
        self.assertEqual(self.doc["statistics"]["source31_routed"], declared)
        self.assertGreaterEqual(declared, 31, "31 源分母不得少於 SOURCE31 實際筆數")
        routed = [r for r in self.doc["entries"] if r["group"] == "SOURCE31"]
        self.assertEqual(len(routed), declared)
        self.assertEqual(len({r["source_id"] for r in routed}), declared)

    def test_03_every_entry_has_resolvable_evidence_field(self):
        inputs = self.doc["inputs"]
        self.assertGreater(len(self.doc["entries"]), 0)
        for row in self.doc["entries"]:
            with self.subTest(source_id=row["source_id"]):
                field = row["evidence_field"]
                self.assertTrue(field, "evidence_field 不可為空")
                self.assertIn(":$", field, "evidence_field 必須是 JSON 欄位路徑")
                file_key = field.split(":$", 1)[0]
                self.assertIn(file_key, inputs, "evidence 指向未載入的檔案")
                self.assertTrue(inputs[file_key]["present"])
                self.assertIn(row["authority_class"], ar.CLASSES)
                self.assertIn(row["reason_code"], ar.REASON_PRIORITY)
        self.assertEqual(self.doc["statistics"]["entries_without_evidence_field"], 0)

    def test_04_no_write_authority_and_no_permit_mint(self):
        self.assertEqual(self.doc["statistics"]["may_authorize_write_true"], 0)
        self.assertEqual(self.doc["statistics"]["may_mint_permit_true"], 0)
        for row in self.doc["entries"]:
            with self.subTest(source_id=row["source_id"]):
                self.assertIs(row["may_mint_permit"], False)
                self.assertIs(row["may_authorize_write"], False)
                self.assertNotIn("may_mint_permit\": true", json.dumps(row))

    def test_05_all_five_classes_present(self):
        counts = self.doc["statistics"]["by_class"]
        self.assertEqual(sorted(counts), sorted(ar.CLASSES))
        for cls in ar.CLASSES:
            self.assertGreater(counts[cls], 0, "class %s 應有成員" % cls)

    def test_06_groups_match_source_files(self):
        groups = self.doc["statistics"]["by_group"]
        for name, file_key in (("ORACLE96", "ORACLE96_CONTRACTS.json"),
                               ("SEAM5", "SEAM_CONTRACTS.json"),
                               ("REPO_PINS", "ORIGINAL_READER_SOURCE_PINS.json")):
            with open(os.path.join(REAL_ROOT, file_key), encoding="utf-8") as fh:
                declared = len(json.load(fh))
            with self.subTest(group=name):
                self.assertEqual(groups.get(name, 0), declared)

    def test_07_real_holds_are_named_and_actionable(self):
        holds = holds_by_code(self.doc)
        for code in (ar.C_SCOPE_UNBOUND, ar.C_MIRROR_IDENTITY,
                     ar.C_COMPILER_NOT_RUN, ar.C_CURRENTNESS):
            with self.subTest(code=code):
                self.assertIn(code, holds, "真實來源應觸發 %s" % code)
                for hold in holds[code]:
                    for key in ("hold_id", "owner", "required_raw", "resume_predicate",
                                "evidence", "blocked_operation"):
                        self.assertTrue(hold.get(key), "%s.%s 不可為空" % (code, key))
                    self.assertTrue(hold["source_ids"])

    def test_08_mirror_never_promoted(self):
        mirrors = [r for r in self.doc["entries"] if r["authority_class"] == "GOVERNANCE_MIRROR"]
        self.assertTrue(mirrors)
        for row in mirrors:
            with self.subTest(source_id=row["source_id"]):
                self.assertIs(row["may_authorize_write"], False)
                self.assertEqual(row["reason_code"], ar.C_MIRROR_NOT_WRITABLE)
        repomap = rows_by_id(self.doc)["GOV:NAV-REPOMAP"]
        self.assertEqual(repomap["evidence_value"], "FABRIC_HOSTED_NON_AUTHORITATIVE_INDEX")
        self.assertEqual(self.doc["checks"]["mirror_identity"]["match"], False)

    def test_09_archived_pipd_is_historical_not_canonical(self):
        hist = [r for r in self.doc["entries"] if r["authority_class"] == "HISTORICAL_ARCHIVED"]
        self.assertEqual(len(hist), 1)
        row = hist[0]
        self.assertIn("PIPD-LS-SP", row["source_id"])
        self.assertEqual(row["reason_code"], ar.C_HISTORICAL)
        self.assertIs(row["may_authorize_write"], False)

    def test_10_skill_is_sidecar_not_compiler(self):
        skill = rows_by_id(self.doc)["SKILL:sbl-tpm-sp"]
        self.assertEqual(skill["authority_class"], "SKILL_SIDECAR")
        self.assertEqual(skill["evidence_value"], "NOT_RUN")
        self.assertIs(skill["may_authorize_write"], False)
        # 沒有任何 SKILL_SIDECAR 被歸為 canonical
        for row in self.doc["entries"]:
            if row["authority_class"] == "SKILL_SIDECAR":
                self.assertNotEqual(row["authority_class"], "CANONICAL_ORIGINAL")

    def test_11_source31_rows_are_canonical_but_read_only(self):
        rows = [r for r in self.doc["entries"] if r["group"] == "SOURCE31"]
        self.assertEqual(len(rows), len(self.src31))
        for row in rows:
            with self.subTest(source_id=row["source_id"]):
                self.assertEqual(row["authority_class"], "CANONICAL_ORIGINAL")
                self.assertEqual(row["reason_code"], ar.P_DOC31)
                self.assertIs(row["may_authorize_write"], False)

    def test_12_stale_author_hold_binding_is_held(self):
        """真實資料：ADDITIONAL_SCOPED_HOLDS_r4c 綁的 candidate body sha 與當前 candidate 不同。"""
        row = rows_by_id(self.doc)["AUTH:ADDITIONAL-SCOPED-HOLDS"]
        self.assertEqual(row["reason_code"], ar.C_SCOPE_UNBOUND)
        with open(os.path.join(REAL_ROOT, "CURRENT_CANDIDATE_STATE.json"),
                  encoding="utf-8") as fh:
            current = json.load(fh)["candidate_body_sha256"]
        self.assertNotEqual(row["evidence_value"], current)
        self.assertIn(current[:12], " ".join(row["rules_applied"]))
        hold = holds_by_code(self.doc)[ar.C_SCOPE_UNBOUND][0]
        self.assertIn("AUTH:ADDITIONAL-SCOPED-HOLDS", hold["source_ids"])

    def test_13_markdown_lists_every_row_and_hold(self):
        with open(os.path.join(self.out, "AUTHORITY_ROUTING.md"), encoding="utf-8") as fh:
            md = fh.read()
        for cls in ar.CLASSES:
            self.assertIn("## %s" % cls, md)
        for row in self.doc["entries"]:
            self.assertIn("`%s`" % row["source_id"], md)
        for hold in self.doc["holds"]:
            self.assertIn(hold["hold_id"], md)


class WriteGateUnit(unittest.TestCase):
    """UNIT: 閘門是真值函數 —— 不是恆假。"""

    def gate(self, cls="CANONICAL_ORIGINAL", **declared):
        base = {"write_authority": "GRANTED", "effect_permission": "GRANTED",
                "artifact_kind": "ORIGINAL_DOCUMENT", "archived": False}
        base.update(declared)
        return ar.AuthorityRouter.gate_authorizes_write(cls, base, [])

    def test_explicit_grant_can_pass(self):
        self.assertTrue(self.gate())

    def test_absent_grant_denied(self):
        self.assertFalse(self.gate(write_authority=None))
        self.assertFalse(self.gate(write_authority="NONE"))
        self.assertFalse(self.gate(effect_permission=None))
        self.assertFalse(self.gate(effect_permission="NONE"))
        self.assertFalse(self.gate(archived=True))
        self.assertFalse(self.gate(cls="GOVERNANCE_MIRROR"))
        self.assertFalse(self.gate(cls="SKILL_SIDECAR", artifact_kind="SKILL"))
        self.assertFalse(self.gate(cls="AUTHOR_CANDIDATE"))

    def test_blocker_dominates(self):
        self.assertFalse(ar.AuthorityRouter.gate_authorizes_write(
            "CANONICAL_ORIGINAL",
            {"write_authority": "GRANTED", "effect_permission": "GRANTED",
             "artifact_kind": "ORIGINAL_DOCUMENT", "archived": False},
            [ar.C_MIRROR_NOT_WRITABLE]))


class NegativeFixtures(unittest.TestCase):
    """NEG: 每個 fixture 斷言具體碼，且不得因此得到任何授寫。

    「真實 red」的證明方式：這些 fixture 的受測列都明示 write_authority=GRANTED、
    effect_permission=GRANTED，因此若對應規則沒觸發，寫入閘門本身會回 True；
    測試同時斷言閘門「counterfactual 為 True」，證明 False 是規則造成而非恆假。
    """

    def run_fixture(self, name):
        root = os.path.join(FIXTURES, name)
        self.assertTrue(os.path.isdir(root), "fixture missing: %s" % root)
        out = os.path.join(TMP, "neg_" + name)
        proc = run_router(root, out, readback=os.path.join(root, "_no_readback"))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        doc = load_out(out)
        return doc

    def assert_no_write_anywhere(self, doc):
        self.assertEqual(doc["statistics"]["may_authorize_write_true"], 0)
        self.assertEqual(doc["statistics"]["may_mint_permit_true"], 0)
        for row in doc["entries"]:
            self.assertIs(row["may_authorize_write"], False)

    def assert_counterfactual_would_write(self, row):
        """拿掉規則後閘門會放行 → 證明 False 是規則的功勞，不是閘門恆假。"""
        self.assertIs(
            ar.AuthorityRouter.gate_authorizes_write(
                row["authority_class"], row["declared"], []),
            True,
            "counterfactual gate 應放行；否則本 NEG 無法證明規則真的 red",
        )

    def test_neg1_mirror_as_authority(self):
        doc = self.run_fixture("neg1_mirror_as_authority")
        row = rows_by_id(doc)["GOV:NAV-REPOMAP"]
        self.assertEqual(row["authority_class"], "GOVERNANCE_MIRROR")
        self.assertEqual(row["reason_code"], "AUTHORITY_MIRROR_NOT_WRITABLE")
        self.assertIs(row["may_authorize_write"], False)
        # 即使 mirror 自己宣告 write_authority=GRANTED 也不行
        self.assertEqual(row["declared"]["write_authority"], "GRANTED")
        # 碼必須來自 R1，而不是 mirror 的「正向」碼
        self.assertNotEqual(row["reason_code"], ar.P_NAV)
        route = rows_by_id(doc)["GOV:ROUTE:sbl_product"]
        self.assertEqual(route["reason_code"], "AUTHORITY_MIRROR_NOT_WRITABLE")
        self.assert_no_write_anywhere(doc)

    def test_neg2_skill_as_permit(self):
        doc = self.run_fixture("neg2_skill_as_permit")
        row = rows_by_id(doc)["SKILL:sbl-tpm-sp"]
        self.assertEqual(row["authority_class"], "SKILL_SIDECAR")
        self.assertEqual(row["reason_code"], "SKILL_NOT_PERMIT")
        self.assertIs(row["may_authorize_write"], False)
        self.assertEqual(row["declared"]["role_claim"], "CANONICAL_COMPILER")
        self.assertNotEqual(row["reason_code"], ar.C_SKILL_SIDECAR)
        hold = holds_by_code(doc)["SKILL_NOT_PERMIT"][0]
        self.assertIn("SKILL:sbl-tpm-sp", hold["source_ids"])
        self.assertTrue(hold["required_raw"])
        self.assert_no_write_anywhere(doc)

    def test_neg3_dual_canonical(self):
        doc = self.run_fixture("neg3_dual_canonical")
        rows = rows_by_id(doc)
        for sid in ("SYN-DUP-A", "SYN-DUP-B"):
            with self.subTest(source_id=sid):
                self.assertEqual(rows[sid]["authority_class"], "CANONICAL_ORIGINAL")
                self.assertEqual(rows[sid]["reason_code"],
                                 "AUTHORITY_CONFLICT_DUAL_CANONICAL")
                self.assertIs(rows[sid]["may_authorize_write"], False)
                self.assert_counterfactual_would_write(rows[sid])
        hold = holds_by_code(doc)["AUTHORITY_CONFLICT_DUAL_CANONICAL"][0]
        self.assertEqual(sorted(hold["source_ids"]), ["SYN-DUP-A", "SYN-DUP-B"])
        self.assertIn("SUBJ-DUP-001", hold["reason"])
        self.assertEqual(rows["SYN-DUP-A"]["declared"]["write_authority"], "GRANTED")
        self.assert_no_write_anywhere(doc)

    def test_neg4_scope_unbound(self):
        doc = self.run_fixture("neg4_scope_unbound")
        row = rows_by_id(doc)["SYN-UNBOUND"]
        self.assertEqual(row["reason_code"], "AUTHORITY_SCOPE_UNBOUND")
        self.assertIs(row["may_authorize_write"], False)
        self.assert_counterfactual_would_write(row)
        hold = holds_by_code(doc)["AUTHORITY_SCOPE_UNBOUND"][0]
        self.assertIn("SYN-UNBOUND", hold["source_ids"])
        self.assertIn("subject/scope", hold["reason"])
        self.assert_no_write_anywhere(doc)

    def test_neg5_profile_role_conflated(self):
        doc = self.run_fixture("neg5_profile_role_conflated")
        row = rows_by_id(doc)["SYN-PROFILE"]
        self.assertEqual(row["reason_code"], "PROFILE_ROLE_CONFLATED")
        self.assertIs(row["may_authorize_write"], False)
        self.assert_counterfactual_would_write(row)
        hold = holds_by_code(doc)["PROFILE_ROLE_CONFLATED"][0]
        self.assertIn("SYN-PROFILE", hold["source_ids"])
        self.assertIn("profile_id == role_id", hold["reason"])
        self.assert_no_write_anywhere(doc)


class RuleR1Unit(unittest.TestCase):
    """UNIT: R1 是可測條件語句 —— effect_permission=NONE 才降級，不是無條件降級。"""

    def setUp(self):
        self.router = ar.AuthorityRouter(LANE, os.path.join(TMP, "unit_out"))

    def hint(self, **declared):
        base = {
            "group": "SOURCE31",
            "source_id": "UNIT-ROW",
            "path": "synthetic/UNIT-ROW.md",
            "evidence_field": "SOURCE31_PHYSICAL_IDENTITY.json:$[0].physical_identity",
            "evidence_value": "PASS",
            "evidence_support": [],
            "hint_class": "CANONICAL_ORIGINAL",
            "declared": {
                "artifact_kind": "ORIGINAL_DOCUMENT",
                "write_authority": "GRANTED",
                "effect_permission": "GRANTED",
                "archived": False,
                "role_claim": None,
                "actor_binding": None,
            },
            "subject_id": "UNIT-ROW",
            "scope_id": "UNIT-SCOPE",
            "artifact_key": "ORIGINAL_DOCUMENT",
            "canonical_key": None,
            "notes": [],
        }
        base["declared"].update(declared)
        return base

    def test_effect_permission_none_blocks_write(self):
        row = self.router._classify_one(self.hint(effect_permission="NONE"))
        self.assertIs(row["may_authorize_write"], False)
        self.assertEqual(row["reason_code"], "AUTHORITY_EFFECT_PERMISSION_NONE")

    def test_effect_permission_granted_allows_write(self):
        row = self.router._classify_one(self.hint(effect_permission="GRANTED"))
        self.assertIs(row["may_authorize_write"], True)

    def test_r2_forces_historical(self):
        row = self.router._classify_one(self.hint(archived=True))
        self.assertEqual(row["authority_class"], "HISTORICAL_ARCHIVED")
        self.assertEqual(row["reason_code"], "HISTORICAL_ARCHIVED_NOT_CANONICAL")
        self.assertIs(row["may_authorize_write"], False)

    def test_r3_downgrades_skill(self):
        row = self.router._classify_one(self.hint(artifact_kind="SKILL"))
        self.assertEqual(row["authority_class"], "SKILL_SIDECAR")
        self.assertIs(row["may_authorize_write"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
