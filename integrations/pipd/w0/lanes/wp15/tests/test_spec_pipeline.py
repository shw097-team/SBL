# -*- coding: utf-8 -*-
"""WP-FHS-15 unittest suite.

POS  — the pipeline generates the three SPECs and every headline count equals an
       independent recount performed here, straight from the source bytes.
NEG  — the three documented failure examples fail with their exact codes:
       SPEC_NOT_HETEROGENEOUS / FUO_MISSING / REQUIREMENT_UNBOUND.

Run:  python -m unittest discover -s tests -v      (from the lane root)
No network, no pip, stdlib only.
"""

import copy
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
import unittest

LANE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if LANE_ROOT not in sys.path:
    sys.path.insert(0, LANE_ROOT)

import spec_pipeline as sp  # noqa: E402

DEFAULT_SOURCE_ROOT = (
    "C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/"
    "Semantic World OS Fabric/FHS／FHS-MSC／SBL/FHS/PIPD-LS-PKG/定案/W0/"
    "FHS_PIPD-LS-PKG_W0_R4C"
)
GOAL = "讓 FHS 在 W0 邊界內把一個 intent 轉成可驗證的三份 SPEC"
BODY_SHA = "56d0df3db6765ee780689ea687824ca891f5a366797e04cfe6ae7c0928173f2a"

SEAM_REQUIRED_KEYS = [
    "abi", "reader", "effect", "permission", "pos", "neg",
    "firstfail", "resume", "typed_handoff",
]


def source_root():
    return os.environ.get("FHS_W0_SOURCE_ROOT", DEFAULT_SOURCE_ROOT)


def body_path(root):
    cands = [f for f in os.listdir(root) if f.endswith("_實質正文.md")]
    if len(cands) != 1:
        raise RuntimeError("body not unique: %s" % cands)
    return os.path.join(root, cands[0])


def load_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def sha256_file(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


class PipelinePOS(unittest.TestCase):
    """One pipeline run, then independent verification of everything it claims."""

    @classmethod
    def setUpClass(cls):
        cls.root = source_root()
        if not os.path.isdir(cls.root):
            raise unittest.SkipTest("source root not available: %s" % cls.root)
        cls.body = body_path(cls.root)
        cls.out = tempfile.mkdtemp(prefix="wp15_pos_", dir=os.path.dirname(__file__))
        cls.manifest = sp.run_pipeline(cls.body, cls.root, cls.out, GOAL)
        cls.product = load_json(os.path.join(cls.out, "SPEC_Product.json"))
        cls.arch = load_json(os.path.join(cls.out, "SPEC_Architecture.json"))
        cls.program = load_json(os.path.join(cls.out, "SPEC_Program.json"))
        cls.chain = load_json(os.path.join(cls.out, "GOAL_TO_FUO.json"))
        cls.hetero = load_json(os.path.join(cls.out, "SPEC_HETEROGENEITY.json"))
        with open(os.path.join(cls.out, "SPEC_Product.md"), encoding="utf-8") as fh:
            cls.product_md = fh.read()
        with open(os.path.join(cls.out, "SPEC_Architecture.md"), encoding="utf-8") as fh:
            cls.arch_md = fh.read()
        with open(os.path.join(cls.out, "SPEC_Program.md"), encoding="utf-8") as fh:
            cls.program_md = fh.read()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    # -- body identity ----------------------------------------------------- #
    def test_body_identity(self):
        actual = sha256_file(self.body)
        self.assertEqual(actual, BODY_SHA, "source body moved; recount is void")
        self.assertEqual(self.manifest["body"]["sha256"], BODY_SHA)
        self.assertEqual(self.manifest["body"]["bytes"], 463034)
        self.assertEqual(self.manifest["body"]["chapters"], 50)

    # -- 50 chapters ------------------------------------------------------- #
    def test_50_chapters_ch00_to_ch49(self):
        with open(self.body, encoding="utf-8") as fh:
            text = fh.read()
        h1 = re.findall(r"^# (CH-\d\d)｜", text, re.M)
        self.assertEqual(len(h1), 50, "body H1 recount")
        self.assertEqual(h1, ["CH-%02d" % i for i in range(50)])
        got = [c["chapter_id"] for c in self.program["chapters"]]
        self.assertEqual(got, h1, "SPEC_Program chapter list != body H1 list")
        self.assertEqual(self.program["counts"]["chapters"]["value"], 50)
        for c in self.program["chapters"]:
            self.assertTrue(c["title"], "chapter title must not be empty: %s" % c)

    # -- 22 WP / 36 Edge / E26 -------------------------------------------- #
    def test_22_wp_36_edges_e26_direction(self):
        prog = load_json(os.path.join(self.root, "PROGRAM_WP22_DAG36.json"))
        self.assertEqual(len(prog["work_packages"]), 22)
        self.assertEqual(len(prog["edges"]), 36)
        self.assertEqual([w["id"] for w in prog["work_packages"]],
                         [w["wp_id"] for w in self.program["work_packages"]])
        self.assertEqual([e["id"] for e in prog["edges"]],
                         [e["edge_id"] for e in self.program["edges"]])

        e26 = [e for e in prog["edges"] if e["id"] == "E26"][0]
        self.assertEqual(e26["predecessor"], "WP-FHS-19")
        self.assertEqual(e26["successor"], "WP-FHS-14")
        d = self.program["e26_direction"]
        self.assertEqual(d["edge_id"], "E26")
        self.assertEqual(d["from"], "WP-FHS-19")
        self.assertEqual(d["to"], "WP-FHS-14")
        self.assertEqual(d["direction"], "WP-FHS-19→WP-FHS-14")
        # reversal must be a different string — proves direction is not a label
        self.assertNotEqual(d["direction"], "WP-FHS-14→WP-FHS-19")
        bind = prog["operation_binding"]["edges"]
        b26 = [b for b in bind if b["edge"] == "E26"][0]
        self.assertEqual((b26["predecessor"], b26["successor"]),
                         (e26["predecessor"], e26["successor"]))
        self.assertEqual(self.program["counts"]["e26"]["predecessor"], "WP-FHS-19")
        self.assertEqual(self.program["counts"]["e26"]["successor"], "WP-FHS-14")

    # -- 84 cards / 25 wave splits ---------------------------------------- #
    def test_84_cards_25_wave_split(self):
        cards = load_json(os.path.join(self.root, "DESIGN84_WAVE_JOIN.json"))
        self.assertEqual(len(cards), 84)
        mismatch = [c for c in cards
                    if c["requirement_delivery_wave"] != c["wp_primary_wave"]]
        self.assertEqual(len(mismatch), 25)
        self.assertEqual(self.program["counts"]["design84_cards"]["value"], 84)
        self.assertEqual(self.program["counts"]["wave_split_25"]["value"], 25)
        self.assertEqual(len(self.program["design84"]["cards"]), 84)
        self.assertEqual(len(self.program["design84"]["wave_split_cards"]), 25)
        got = {c["original_id"] for c in self.program["design84"]["wave_split_cards"]}
        self.assertEqual(got, {c["original_id"] for c in mismatch})

    # -- 22 W0_REQUIRED --------------------------------------------------- #
    def test_22_w0_required(self):
        req = load_json(os.path.join(self.root, "W0_REQUIRED22_TRACE.json"))
        self.assertEqual(len(req), 22)
        self.assertEqual(self.program["counts"]["w0_required"]["value"], 22)
        self.assertEqual([r["original_id"] for r in req],
                         [r["original_id"] for r in self.program["w0_required22"]])
        for r in req:
            self.assertTrue(r["source_sha"])
            self.assertTrue(r["source_span"])
            self.assertTrue(r["deliver_id"])

    # -- 31 source / 949 R15 / 192 cell / 50+149 / 96 / 485 / 393 --------- #
    def test_source31(self):
        src = load_json(os.path.join(self.root, "SOURCE31_PHYSICAL_IDENTITY.json"))
        self.assertEqual(len(src), 31)
        self.assertEqual(self.program["counts"]["sources31"]["value"], 31)
        self.assertEqual(len(self.program["sources31"]), 31)

    def test_r15_949_and_cell_192(self):
        path = os.path.join(self.root, "W0_R2_TRACE_R15_949_CELL192_B1_CASES_AND_ORACLE.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        r15 = re.findall(r"^\| `(R15-\d+)`", text, re.M)
        cell = re.findall(r"^\| `(CELL-[^`]+)`", text, re.M)
        self.assertEqual(len(r15), 949)
        self.assertEqual(len(set(r15)), 949)
        self.assertEqual(len(cell), 192)
        self.assertEqual(len(set(cell)), 192)
        self.assertEqual(self.program["counts"]["r15_949"]["value"], 949)
        self.assertEqual(self.program["counts"]["cell192"]["value"], 192)
        self.assertEqual(len(self.program["r15_949"]["ids"]), 949)
        self.assertEqual(len(self.program["cell_192"]["ids"]), 192)

    def test_parent50_child149(self):
        path = os.path.join(self.root, "W0_R2_TRACE_SBL_PARENT50_CHILD149.md")
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        parents = re.findall(r"^\| (U\d\d) \|", text, re.M)
        children = re.findall(r"^\| (U\d\d\.\d+) \|", text, re.M)
        self.assertEqual(len(parents), 50)
        self.assertEqual(len(set(parents)), 50)
        self.assertEqual(len(children), 149)
        self.assertEqual(len(set(children)), 149)
        self.assertEqual(self.program["parent_child"]["parent_50"], 50)
        self.assertEqual(self.program["parent_child"]["child_149"], 149)
        # every child's parent must exist
        for cid in children:
            self.assertIn(cid.split(".")[0], set(parents))

    def test_oracle96(self):
        orc = load_json(os.path.join(self.root, "ORACLE96_CONTRACTS.json"))
        self.assertEqual(len(orc), 96)
        self.assertEqual(len({c["case_id"] for c in orc}), 96)
        self.assertEqual(self.program["counts"]["oracle96"]["value"], 96)
        self.assertEqual(len(self.program["oracle96"]["case_ids"]), 96)
        classes = {}
        for c in orc:
            classes[c["test_class"]] = classes.get(c["test_class"], 0) + 1
        self.assertEqual(classes, self.program["oracle96"]["classes"])

    def test_tech485(self):
        tech = load_json(os.path.join(self.root, "TECH485_COMPACT_REGISTRY.json"))
        self.assertEqual(len(tech), 485)
        self.assertEqual(self.program["counts"]["tech485"]["value"], 485)
        fam = {}
        for t in tech:
            fam[t["family"]] = fam.get(t["family"], 0) + 1
        self.assertEqual(fam, self.program["tech485"]["families"])
        self.assertEqual(sum(fam.values()), 485)

    def test_case393_is_96_plus_b1_plus_ac(self):
        cases = load_json(os.path.join(self.root, "CASE393_REGISTRY.json"))
        self.assertEqual(len(cases), 393)
        fam = {}
        for c in cases:
            fam[c["family"]] = fam.get(c["family"], 0) + 1
        self.assertEqual(fam.get("OriginalOracle96"), 96)
        self.assertEqual(sum(fam.values()), 393)
        self.assertEqual(self.program["counts"]["case393"]["value"], 393)
        self.assertEqual(self.program["counts"]["case393"]["families"], fam)

    # -- every count carries a verifiable source_ref ---------------------- #
    def test_every_count_has_verifiable_source_ref(self):
        counts = self.program["counts"]
        self.assertGreaterEqual(len(counts), 15)
        for key, rec in counts.items():
            self.assertIn("value", rec, key)
            ref = rec["source_ref"]
            self.assertTrue(ref["file"], key)
            self.assertTrue(ref["selector"], key)
            sha = ref.get("file_sha256")
            if sha:
                self.assertEqual(sha, sha256_file(os.path.join(self.root, ref["file"])),
                                 "stale source_ref sha for %s" % key)
            if isinstance(rec["value"], int):
                self.assertGreater(rec["value"], 0, key)

    def test_counter_reconciliation_all_match(self):
        rows = self.program["counter_reconciliation"]
        self.assertGreaterEqual(len(rows), 7)
        for row in rows:
            self.assertIsNotNone(row["declared"], "unparsed claim: %s" % row["claim"])
            self.assertEqual(row["declared"], row["computed"],
                             "declared != computed for %s" % row["claim"])
            self.assertTrue(row["match"])

    # -- Product SPEC shape ---------------------------------------------- #
    def test_product_fields(self):
        for key in ("jtbd", "fuo", "mvp", "non_goals", "acc_plus", "acc_minus",
                    "requirement_ids", "subject"):
            self.assertIn(key, self.product)
        self.assertTrue(self.product["jtbd"]["statement"])
        self.assertTrue(self.product["mvp"]["statement"])
        self.assertTrue(self.product["non_goals"]["statement"])
        self.assertGreaterEqual(len(self.product["acc_plus"]), 2)
        self.assertGreaterEqual(len(self.product["acc_minus"]), 2)
        # ACC+ / ACC- must not be the same statements
        plus = {a["statement"] for a in self.product["acc_plus"]}
        minus = {a["statement"] for a in self.product["acc_minus"]}
        self.assertTrue(plus - minus, "ACC+ has no statement absent from ACC-")
        codes = {c for a in self.product["acc_minus"] for c in a.get("firstfail_codes", [])}
        codes |= {a["expected_first_fail"] for a in self.product["acc_minus"]
                  if a.get("expected_first_fail")}
        self.assertIn("FUO_NOT_OBSERVABLE", codes)
        self.assertEqual(self.product["subject"]["body_sha256"], BODY_SHA)

    def test_fuo_register(self):
        fuo = self.product["fuo"]
        self.assertGreaterEqual(len(fuo), 3)
        self.assertEqual(len({f["fuo_id"] for f in fuo}), len(fuo))
        for f in fuo:
            self.assertTrue(f["fuo_id"])
            self.assertTrue(f["statement"])
            self.assertTrue(f["source_ref"]["file"])
            self.assertTrue(f["acceptance"]["pos"])
            self.assertTrue(f["acceptance"]["neg"])
        origins = {f["fuo_origin"].split()[0] for f in fuo}
        self.assertIn("W0_REQUIRED22_TRACE.json", origins)
        self.assertIn("CH-01", origins)

    def test_requirement_ids_bound_to_registry(self):
        reg = sp.SourceIndex(self.body, self.root).requirement_registry()
        for spec in (self.product, self.arch):
            self.assertTrue(spec["requirement_ids"])
            for rid in spec["requirement_ids"]:
                self.assertIn(rid, reg, "%s cites unbound %s" % (spec["spec_kind"], rid))
                self.assertTrue(reg[rid]["bound"])

    # -- Architecture SPEC shape ----------------------------------------- #
    def test_architecture_five_stages(self):
        stages = self.arch["domain_stages"]
        self.assertEqual(len(stages), 5)
        names = " ".join(s["name"] for s in stages)
        for token in ("Fabric Policy", "PIPD Compiler", "Native Issuer",
                      "Hermes", "Checker"):
            self.assertIn(token, names)
        for s in stages:
            self.assertTrue(s["seam_refs"], "%s resolved no seam" % s["stage_id"])
            self.assertTrue(s["forbidden"])
            self.assertTrue(s["source_ref"]["chapter"])
        # each seam must be reachable from at least one stage, or be the declared
        # entry seam (S1), which is recorded rather than silently dropped
        covered = {m["seam"] for s in stages for m in s["seam_refs"]}
        entry = self.arch["entry_seam"]
        self.assertIsNotNone(entry)
        self.assertEqual(entry["seam"], "S1")
        self.assertIn("entry seam", entry["resolve_rule"])
        self.assertTrue(entry["source_ref"]["line"])
        self.assertEqual(covered | {entry["seam"]}, {"S1", "S2", "S3", "S4", "S5"})
        self.assertNotIn(entry["seam"], covered)
        self.assertIn("入口接縫", self.arch_md)

    def test_architecture_five_seams_full_shape(self):
        seams = self.arch["seams"]
        self.assertEqual([s["seam"] for s in seams], ["S1", "S2", "S3", "S4", "S5"])
        for s in seams:
            for key in SEAM_REQUIRED_KEYS:
                self.assertIn(key, s, "%s missing %s" % (s["seam"], key))
                self.assertTrue(s[key], "%s empty %s" % (s["seam"], key))
            self.assertTrue(s["abi"]["declared"])
            self.assertTrue(s["reader"]["original_reader"])
            self.assertEqual(s["reader"]["ack"], "NOT_OBSERVED")
            self.assertEqual(s["effect"]["executed"], "NOT_RUN")
            self.assertTrue(s["permission"]["mode"])
            self.assertTrue(s["pos"]["statement"])
            self.assertTrue(s["neg"]["statement"])
            self.assertTrue(s["firstfail"]["primary"])
            self.assertTrue(s["resume"]["resume"])
            self.assertTrue(s["typed_handoff"]["input"])
            self.assertTrue(s["typed_handoff"]["output"])
            self.assertEqual(len(s["typed_handoff"]["fixture_sha256"]), 3)

    def test_architecture_principal_separation(self):
        ps = self.arch["principal_separation"]
        self.assertEqual(ps["human_owner_count"], 1)
        self.assertEqual(len(ps["technical_principals"]), 3)
        self.assertTrue(ps["identity_collapse_is_a_failure"])
        self.assertGreaterEqual(len(ps["evidence"]), 4)
        self.assertIn("唯一 Human Owner 不是 Maker／Issuer／Checker 同一個技術 Principal。",
                      ps["assertion"])
        self.assertIn("唯一 Human Owner 不是 Maker／Issuer／Checker 同一個技術 Principal。",
                      self.arch_md)
        sw = self.arch["single_writer"]
        self.assertIn("Protected Checker", " ".join(sw["non_transferable"]))
        self.assertIn("Publisher", " ".join(sw["non_transferable"]))
        self.assertTrue(self.arch["domain_boundary_statement"]["no_second_issuer"])

    # -- heterogeneity ---------------------------------------------------- #
    def test_heterogeneity_report(self):
        self.assertEqual(self.hetero["verdict"], "HETEROGENEOUS")
        specs = self.hetero["specs"]
        self.assertEqual(set(specs), {"Product", "Architecture", "Program"})
        for name, doc, md in (("Product", self.product, self.product_md),
                             ("Architecture", self.arch, self.arch_md),
                             ("Program", self.program, self.program_md)):
            self.assertEqual(specs[name]["required_field_set"], sorted(doc.keys()))
            self.assertEqual(specs[name]["section_set"], sp._sections_of_md(md))
            self.assertEqual(specs[name]["body_sha256"], sp.sha256_text(md))
            self.assertGreaterEqual(len(specs[name]["section_set"]), 8)
        for pair, rec in self.hetero["pairs"].items():
            self.assertFalse(rec["field_sets_equal"], pair)
            self.assertTrue(rec["fields_only_in_a"], pair)
            self.assertTrue(rec["fields_only_in_b"], pair)
            self.assertTrue(rec["section_strictly_smaller_than_each"], pair)
            self.assertLessEqual(rec["section_jaccard"], 0.25, pair)
            self.assertLessEqual(rec["domain_token_jaccard"], 0.35, pair)

    def test_md_bodies_are_not_title_swaps(self):
        sections = {n: set(sp._sections_of_md(m)) for n, m in
                    (("P", self.product_md), ("A", self.arch_md), ("G", self.program_md))}
        for a, b in (("P", "A"), ("P", "G"), ("A", "G")):
            inter = sections[a] & sections[b]
            self.assertLess(len(inter), len(sections[a]))
            self.assertLess(len(inter), len(sections[b]))
        # the only shared section is the contractual Subject block
        self.assertEqual(sections["P"] & sections["A"], {sp.SHARED_SECTION})
        # and the bodies really differ
        self.assertNotEqual(self.product_md, self.arch_md)
        self.assertNotEqual(self.product_md, self.program_md)
        self.assertNotEqual(self.arch_md, self.program_md)

    # -- subject ---------------------------------------------------------- #
    def test_same_subject_three_specs(self):
        shas = {d["subject"]["body_sha256"] for d in (self.product, self.arch, self.program)}
        sids = {d["subject"]["subject_id"] for d in (self.product, self.arch, self.program)}
        self.assertEqual(shas, {BODY_SHA})
        self.assertEqual(sids, {"FHS-W0-EXAMPLE-SOURCE-BOUND-SPEC-001"})
        for d in (self.product, self.arch, self.program):
            self.assertEqual(d["claim_ceiling"], "AUTHOR_LOCAL_TEST")
            self.assertEqual(d["native_effect"], "NOT_RUN")

    # -- goal chain ------------------------------------------------------- #
    def test_goal_chain_readback(self):
        doc = self.chain
        self.assertEqual(doc["goal"], GOAL)
        self.assertEqual(doc["input_sha"], sp.sha256_text(GOAL))
        self.assertEqual(doc["output_sha"],
                         sha256_file(os.path.join(self.out, "SPEC_Product.json")))
        # readback_sha recomputed by re-reading the file from disk
        reread = load_json(os.path.join(self.out, "GOAL_TO_FUO.json"))
        self.assertEqual(reread["readback_sha"], sp.compute_readback_sha(reread))
        self.assertEqual(sp.verify_readback(os.path.join(self.out, "GOAL_TO_FUO.json"))
                         ["verified"], True)
        self.assertGreaterEqual(doc["chain_count"], 3)
        self.assertEqual(doc["chain_count"], len(doc["chains"]))
        product_fuo = {f["fuo_id"] for f in self.product["fuo"]}
        for ch in doc["chains"]:
            self.assertEqual([s["kind"] for s in ch["steps"]],
                             ["GOAL", "PRODUCT_SPEC", "W0_DELIVER", "FUO"])
            self.assertIn(ch["fuo_id"], product_fuo)
            self.assertTrue(ch["deliver_id"].startswith("DEL-W0-"))
            self.assertTrue(ch["readback"]["fuo_present_in_product_spec"])
            self.assertTrue(ch["readback"]["deliver_present_in_product_spec"])
            self.assertEqual(ch["steps"][0]["sha256"], doc["input_sha"])
            self.assertEqual(ch["steps"][1]["sha256"], doc["output_sha"])
        self.assertIn(doc["primary_chain"], {c["chain_id"] for c in doc["chains"]})
        self.assertIn("readback_sha", doc)

    def test_manifest_outputs_exist(self):
        outs = self.manifest["outputs"]
        for name in ("SPEC_Product.json", "SPEC_Product.md",
                     "SPEC_Architecture.json", "SPEC_Architecture.md",
                     "SPEC_Program.json", "SPEC_Program.md",
                     "GOAL_TO_FUO.json", "GOAL_TO_FUO.md",
                     "SPEC_HETEROGENEITY.json"):
            self.assertIn(name, outs)
            self.assertEqual(outs[name]["sha256"],
                             sha256_file(os.path.join(self.out, name)))
        self.assertEqual(self.manifest["claim_ceiling"], "AUTHOR_LOCAL_TEST")
        self.assertEqual(self.manifest["native_effect"], "NOT_RUN")


class PipelineNEG(unittest.TestCase):
    """The three named failure examples must fail with their exact codes."""

    @classmethod
    def setUpClass(cls):
        cls.root = source_root()
        if not os.path.isdir(cls.root):
            raise unittest.SkipTest("source root not available: %s" % cls.root)
        cls.body = body_path(cls.root)
        cls.out = tempfile.mkdtemp(prefix="wp15_neg_", dir=os.path.dirname(__file__))
        sp.run_pipeline(cls.body, cls.root, cls.out, GOAL)
        cls.product = load_json(os.path.join(cls.out, "SPEC_Product.json"))
        cls.arch = load_json(os.path.join(cls.out, "SPEC_Architecture.json"))
        with open(os.path.join(cls.out, "SPEC_Product.md"), encoding="utf-8") as fh:
            cls.product_md = fh.read()
        cls.index = sp.SourceIndex(cls.body, cls.root)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def test_neg_spec_not_heterogeneous(self):
        """三份內容相同、只換標題/artifact_id -> SPEC_NOT_HETEROGENEOUS."""
        clones = {}
        mds = {}
        for kind in ("Product", "Architecture", "Program"):
            doc = copy.deepcopy(self.product)
            doc["spec_kind"] = kind
            doc["artifact_id"] = kind.upper()  # the only change: a new title
            clones[kind] = doc
            mds[kind] = self.product_md.replace(
                "SPEC_Product", "SPEC_%s" % kind, 1
            )
        with self.assertRaises(sp.SpecError) as ctx:
            sp.assert_heterogeneity(clones, mds)
        self.assertEqual(ctx.exception.code, "SPEC_NOT_HETEROGENEOUS")
        self.assertIn("identical required_field_set", ctx.exception.detail)

    def test_neg_fuo_missing(self):
        """Product SPEC 沒有 FUO -> FUO_MISSING."""
        doc = copy.deepcopy(self.product)
        doc["fuo"] = []
        with self.assertRaises(sp.SpecError) as ctx:
            sp.assert_fuo(doc)
        self.assertEqual(ctx.exception.code, "FUO_MISSING")

        # a FUO row without acceptance is the same failure, not a pass
        doc2 = copy.deepcopy(self.product)
        doc2["fuo"][0]["acceptance"]["neg"] = ""
        with self.assertRaises(sp.SpecError) as ctx2:
            sp.assert_fuo(doc2)
        self.assertEqual(ctx2.exception.code, "FUO_MISSING")

        # and the pipeline itself refuses to emit a FUO-less product
        saved = sp.build_product
        try:
            def broken(index, goal):
                d, m = saved(index, goal)
                d["fuo"] = []
                return d, m
            sp.build_product = broken
            tmp = tempfile.mkdtemp(prefix="wp15_neg_fuo_", dir=os.path.dirname(__file__))
            try:
                with self.assertRaises(sp.SpecError) as ctx3:
                    sp.run_pipeline(self.body, self.root, tmp, GOAL)
                self.assertEqual(ctx3.exception.code, "FUO_MISSING")
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
        finally:
            sp.build_product = saved

    def test_neg_requirement_unbound(self):
        """引用不存在的 RequirementID -> REQUIREMENT_UNBOUND."""
        doc = copy.deepcopy(self.product)
        doc["requirement_ids"] = sorted(set(doc["requirement_ids"]) | {"INT-99"})
        doc["requirement_bindings"].append(
            {"requirement_id": "INT-99", "spec_kind": "Product", "note": "fabricated"}
        )
        with self.assertRaises(sp.SpecError) as ctx:
            sp.assert_requirements(doc, self.index)
        self.assertEqual(ctx.exception.code, "REQUIREMENT_UNBOUND")
        self.assertEqual(ctx.exception.payload["unbound"], ["INT-99"])

        # a real id that no registry row binds (only prose) is also rejected
        doc2 = copy.deepcopy(self.product)
        doc2["requirement_ids"] = ["INT-02"]
        doc2["requirement_bindings"] = [{"requirement_id": "INT-02"}]
        self.assertNotIn("INT-02", self.index.counts()["w0_required"]["ids"])
        # INT-02 IS bound by a Design84 card, so this must pass
        sp.assert_requirements(doc2, self.index)

        doc3 = copy.deepcopy(self.product)
        doc3["requirement_ids"] = ["FHS-DR-099"]
        doc3["requirement_bindings"] = [{"requirement_id": "FHS-DR-099"}]
        with self.assertRaises(sp.SpecError) as ctx3:
            sp.assert_requirements(doc3, self.index)
        self.assertEqual(ctx3.exception.code, "REQUIREMENT_UNBOUND")

    def test_neg_subject_body_sha_mismatch(self):
        """正文 sha 與 CURRENT_CANDIDATE_STATE 不一致 -> SUBJECT_BODY_SHA_MISMATCH."""
        tmp = tempfile.mkdtemp(prefix="wp15_neg_body_", dir=os.path.dirname(__file__))
        try:
            with open(self.body, "rb") as fh:
                raw = fh.read()
            bad = os.path.join(tmp, os.path.basename(self.body))
            with open(bad, "wb") as fh:
                fh.write(raw[:-40] + b"\n" * 40)  # same size, different bytes
            index = sp.SourceIndex(bad, self.root)
            with self.assertRaises(sp.SpecError) as ctx:
                sp.build_subject(index)
            self.assertEqual(ctx.exception.code, "SUBJECT_BODY_SHA_MISMATCH")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_neg_claim_ceiling_violation(self):
        """無來源卻宣權威 / 自稱 Native -> CLAIM_CEILING_VIOLATION（CH-00 NEG）."""
        doc = copy.deepcopy(self.product)
        doc["claim_ceiling"] = "NATIVE_PASS"
        with self.assertRaises(sp.SpecError) as ctx:
            sp.assert_claim_ceiling(doc)
        self.assertEqual(ctx.exception.code, "CLAIM_CEILING_VIOLATION")

        doc2 = copy.deepcopy(self.arch)
        doc2["native_effect"] = "OBSERVED"
        with self.assertRaises(sp.SpecError) as ctx2:
            sp.assert_claim_ceiling(doc2)
        self.assertEqual(ctx2.exception.code, "CLAIM_CEILING_VIOLATION")

        doc3 = {"claim_ceiling": "AUTHOR_LOCAL_TEST", "native_effect": "NOT_RUN"}
        with self.assertRaises(sp.SpecError) as ctx3:
            sp.assert_claim_ceiling(doc3)
        self.assertEqual(ctx3.exception.code, "CLAIM_CEILING_VIOLATION")
        self.assertIn("no source-bound rows", ctx3.exception.detail)

        # the three real SPECs all pass
        for d in (self.product,
                  load_json(os.path.join(self.out, "SPEC_Architecture.json")),
                  load_json(os.path.join(self.out, "SPEC_Program.json"))):
            self.assertTrue(sp.assert_claim_ceiling(d))

    def test_neg_seam_shape_incomplete(self):
        """A seam that dropped a typed facet must be rejected, not silently shipped."""
        arch = load_json(os.path.join(self.out, "SPEC_Architecture.json"))
        sp.assert_seam_shape(arch)  # the real one passes

        broken = copy.deepcopy(arch)
        del broken["seams"][3]["typed_handoff"]
        with self.assertRaises(sp.SpecError) as ctx:
            sp.assert_seam_shape(broken)
        self.assertEqual(ctx.exception.code, "SEAM_SHAPE_INCOMPLETE")
        self.assertEqual(ctx.exception.payload["seam"], "S4")

        # the Product SPEC must not smuggle architecture facets in
        self.assertNotIn("seams", self.product)


if __name__ == "__main__":
    unittest.main(verbosity=2)
