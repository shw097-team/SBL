"""Clause identity, not keyword coverage, is authoritative (R-AUD-005 / R-AUD-009).

R-AUD-005: requirements are compiled from source clauses into distinct atoms - compound
(各有／分別／對應), negated, same-keyword-different-meaning, no-keyword and multi-clause inputs all
stay distinct; semantic collapse is refused; every atom traces SRC→REQ/Child→SPEC→ACC→VER→EVD→
DEL→GATE with no orphans.

R-AUD-009: bind_pd derives head/branch/dirty/tracked_files/manifest/currentness from the
repository/host itself; caller values are unverified claims; a stale or spoofed freshness claim is
refused; a missing RepoContext fails closed (no PREDEV_READY).
"""
import copy
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Self-bootstrap, same rule as every other test file here: a test file must be runnable standalone.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, repo_context, requirements  # noqa: E402
from pipd_ls_sp.errors import (AuthorityUnknown, EffectUnknown, IntakeInvalid,  # noqa: E402
                               PiSemanticFail, RepoContextMissing, StaleProvider)

FIXTURES = ROOT / "fixtures"
GOAL = "實作審計系統。"
GIT = shutil.which("git")


def compile_fixture(*names):
    return requirements.compile_requirements(
        "goal", [str(FIXTURES / n / "source.txt") for n in names])


def _expand_text(text: str):
    """Compile one inline source text into atoms through a real (temporary) file source."""
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "inline.txt"
        path.write_text(text, encoding="utf-8")
        return requirements.compile_requirements("goal", [str(path)])


class AtomicRequirements(unittest.TestCase):
    def test_no_keyword_requirement_is_preserved(self):
        card = pipeline.intake('每頁保留三列。', sources=[str(ROOT)])
        atoms = pipeline.atoms_of(pipeline.compile_pi(card))
        self.assertEqual(len(atoms), 1)
        self.assertEqual(atoms[0]['source_clause']['text'], '每頁保留三列')
        self.assertEqual(atoms[0]['risk_guard']['polarity'], 'MUST')


class ClauseBoundCompiler(unittest.TestCase):
    """R-AUD-005: clause-bound atomic requirement compiler."""

    def test_compound_distributive_clauses_yield_distinct_atoms(self):
        atoms = compile_fixture("REQ-COMPOUND")
        texts = [a["source_clause"]["text"] for a in atoms]
        self.assertEqual(len(atoms), 4, texts)
        for subject in ("測試", "交付", "輸出", "輸入"):
            self.assertEqual(sum(subject in t for t in texts), 1, texts)
        self.assertEqual(len({a["req_id"] for a in atoms}), 4)
        self.assertEqual(len({a["risk_guard"]["oracle"]["id"] for a in atoms}), 4)
        self.assertEqual(len({a["risk_guard"]["negative_fixture"] for a in atoms}), 4)

    def test_negation_keeps_polarity_and_distinct_atoms(self):
        atoms = compile_fixture("REQ-NEGATION")
        self.assertEqual(len(atoms), 4)
        by_text = {a["source_clause"]["text"]: a for a in atoms}
        self.assertEqual(by_text["系統不得交付遙測資料"]["risk_guard"]["polarity"], "MUST NOT")
        self.assertEqual(by_text["系統交付發行說明"]["risk_guard"]["polarity"], "MUST")
        # A distributive negation distributes its scope to every subject binding.
        self.assertEqual(by_text["測試分別不得遺漏"]["risk_guard"]["polarity"], "MUST NOT")
        self.assertEqual(by_text["交付分別延遲"]["risk_guard"]["polarity"], "MUST NOT")
        # The prohibition and its positive counterpart never merge.
        self.assertEqual(len({a["req_id"] for a in atoms}), 4)
        self.assertEqual(len({a["risk_guard"]["negative_fixture"] for a in atoms}), 4)

    def test_same_keyword_different_meaning_stays_distinct(self):
        atoms = compile_fixture("REQ-SAME-KEYWORD")
        self.assertEqual(len(atoms), 2)
        a, b = atoms
        self.assertIn("驗收", a["source_clause"]["text"])
        self.assertIn("驗收", b["source_clause"]["text"])
        self.assertNotEqual(a["req_id"], b["req_id"])
        self.assertNotEqual(a["risk_guard"]["oracle"]["id"], b["risk_guard"]["oracle"]["id"])
        self.assertNotEqual(a["risk_guard"]["negative_fixture"], b["risk_guard"]["negative_fixture"])
        # Both statements share the SAME advisory keyword axis - the old bucket that collapsed
        # them. Axis tagging may classify; it may never decide atom existence or merge clauses.
        self.assertEqual(a["axis"], "verification")
        self.assertEqual(b["axis"], "verification")

    def test_no_keyword_clauses_still_compile(self):
        atoms = compile_fixture("REQ-NO-KEYWORD")
        self.assertEqual(len(atoms), 2)
        self.assertEqual({a["source_clause"]["text"] for a in atoms},
                         {"每頁保留三列", "標題置中"})

    def test_two_different_source_clauses_yield_distinct_locators(self):
        pair = requirements.compile_requirements(
            "goal", [str(FIXTURES / "REQ-TWO-CLAUSES" / "source.txt"),
                     str(FIXTURES / "REQ-TWO-CLAUSES" / "source-b.txt")])
        self.assertEqual(len(pair), 2)
        a, b = pair
        self.assertNotEqual(a["source_clause"]["file"], b["source_clause"]["file"])
        self.assertNotEqual(a["req_id"], b["req_id"])
        self.assertNotEqual(a["source_clause"]["source_sha256"],
                            b["source_clause"]["source_sha256"])
        for atom in pair:
            self.assertTrue(atom["source_clause"]["clause_id"].startswith("clause-"))
            self.assertEqual(len(atom["source_clause"]["span"]), 2)
        # The id is bound to the clause locator: solo compilation keeps the pair's ids.
        solo = requirements.compile_requirements(
            "goal", [str(FIXTURES / "REQ-TWO-CLAUSES" / "source.txt")])
        self.assertEqual(solo[0]["req_id"], a["req_id"])

    def test_negative_fixture_old_classifier_falsely_collapsed(self):
        case = json.loads((FIXTURES / "REQ-COLLAPSED-KEYWORD" / "negative" / "case.json")
                          .read_text(encoding="utf-8"))
        clauses = [s for s in case["expected_atoms"]]
        # Frozen copy of the pre-R-AUD-005 five-keyword classifier: one bucket per axis keyword.
        old_rules = [("REQ-INTENT", "intent", r"(?i)(implement|build|實作|建置|開發|施工)"),
                     ("REQ-KNOWLEDGE", "knowledge", r"(?i)(knowledge|source|知識|來源|規格|spec)"),
                     ("REQ-VERIFY", "verification", r"(?i)(test|verify|accept|測試|驗收|驗證)"),
                     ("REQ-DELIVER", "release", r"(?i)(deliver|publish|release|交付|發佈|發布|公開)"),
                     ("REQ-GOVERN", "trust_boundary", r"(?i)(govern|admission|workorder|治理|准入|裁決)")]
        text = (FIXTURES / "REQ-COLLAPSED-KEYWORD" / "source.txt").read_text(encoding="utf-8")
        buckets = sorted({f"{rid}/{ax}" for rid, ax, pat in old_rules
                          for clause in clauses if re.search(pat, clause["text"])})
        self.assertEqual(buckets, case["old_classifier"]["buckets"], "old classifier model drifted")
        # The old route emitted ONE keyword atom for the whole goal: two source clauses - an
        # obligation and its prohibition - collapsed into it. Record that as the rejected outcome.
        self.assertEqual(case["old_classifier"]["atoms_emitted"], 1)
        self.assertEqual(len(clauses), 2)
        self.assertIn("系統交付發行說明。", text)
        self.assertIn("系統不得交付遙測資料。", text)
        atoms = compile_fixture("REQ-COLLAPSED-KEYWORD")
        self.assertEqual([a["risk_guard"]["polarity"] for a in atoms], ["MUST", "MUST NOT"])
        self.assertEqual([a["source_clause"]["text"] for a in atoms],
                         [c["text"] for c in clauses])

    def test_ambiguous_compound_is_refused_not_collapsed(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "ambiguous.txt"
            src.write_text("甲、乙、丙分別對應驗收與發佈。\n", encoding="utf-8")
            with self.assertRaises(IntakeInvalid):
                requirements.compile_requirements("goal", [str(src)])
        with self.assertRaises(IntakeInvalid):
            requirements._expand("各有多項驗收條件")

    def test_semantic_collapse_is_refused(self):
        atoms = copy.deepcopy(compile_fixture("REQ-SAME-KEYWORD"))
        with self.assertRaises(PiSemanticFail):
            requirements.validate_atoms([atoms[0], copy.deepcopy(atoms[0])])
        shared_oracle = copy.deepcopy(atoms)
        shared_oracle[1]["risk_guard"]["oracle"]["id"] = shared_oracle[0]["risk_guard"]["oracle"]["id"]
        with self.assertRaises(PiSemanticFail):
            requirements.validate_atoms(shared_oracle)
        shared_fixture = copy.deepcopy(atoms)
        shared_fixture[1]["risk_guard"]["negative_fixture"] = \
            shared_fixture[0]["risk_guard"]["negative_fixture"]
        with self.assertRaises(PiSemanticFail):
            requirements.validate_atoms(shared_fixture)
        with self.assertRaises(PiSemanticFail):
            requirements.validate_atoms([{"req_id": "REQ-INTENT", "axis": "intent"}])
        with self.assertRaises(PiSemanticFail):
            requirements.validate_atoms([])

    def test_every_atom_traces_orphan_free(self):
        atoms = (compile_fixture("REQ-COMPOUND", "REQ-NEGATION", "REQ-SAME-KEYWORD",
                                 "REQ-NO-KEYWORD", "REQ-COLLAPSED-KEYWORD"))
        trace = requirements.obligation_trace(atoms)
        self.assertEqual(requirements.trace_findings(atoms, trace), [])
        self.assertEqual(len(trace["nodes"]), 8 * len(atoms))
        self.assertEqual(len(trace["edges"]), 7 * len(atoms))
        ids = {n["id"] for n in trace["nodes"]}
        incoming = {}
        for edge in trace["edges"]:
            self.assertIn(edge["from"], ids, "edge source orphan")
            self.assertIn(edge["to"], ids, "edge target orphan")
            incoming[edge["to"]] = incoming.get(edge["to"], 0) + 1
        for atom in atoms:
            chain = [n for n in trace["nodes"] if n["requirement"] == atom["req_id"]]
            self.assertEqual([n["stage"] for n in chain], list(requirements.STAGES))
            self.assertEqual(incoming.get(chain[0]["id"], 0), 0, "SRC must be the root")
            for node in chain[1:]:
                self.assertEqual(incoming.get(node["id"]), 1, "each stage has exactly one parent")
        # A dropped node is detected as an incomplete/orphaned trace, never silently accepted.
        broken = copy.deepcopy(trace)
        broken["nodes"] = broken["nodes"][:-1]
        self.assertTrue(requirements.trace_findings(atoms, broken))

    def test_atoms_carry_stable_ids_and_full_provenance(self):
        first = compile_fixture("REQ-COMPOUND")
        second = compile_fixture("REQ-COMPOUND")
        self.assertEqual([a["req_id"] for a in first], [a["req_id"] for a in second])
        for atom in first:
            self.assertRegex(atom["req_id"], r"^REQ-[0-9a-f]{20}$")
            loc = atom["source_clause"]
            self.assertTrue(loc["file"])
            self.assertTrue(loc["clause_id"].startswith("clause-"))
            self.assertEqual(len(loc["span"]), 2)
            self.assertRegex(loc["source_sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(atom["owner"])
            guard = atom["risk_guard"]
            self.assertIn(guard["polarity"], ("MUST", "MUST NOT"))
            self.assertTrue(atom["acceptance_cue"].startswith(guard["polarity"] + ":"))
            self.assertRegex(guard["oracle"]["id"], r"^ORACLE-REQ-[0-9a-f]{20}$")
            self.assertTrue(guard["oracle"]["predicate"])
            self.assertIn(guard["oracle"]["expected"], ("required", "forbidden"))
            self.assertTrue(guard["negative_fixture"])

    def test_five_axis_route_is_not_authoritative(self):
        self.assertFalse(hasattr(pipeline, "ATOM_RULES"),
                         "the five-keyword axis route must not survive as an intake authority")
        card = pipeline.intake("每頁保留三列。", sources=[str(ROOT)])
        self.assertEqual(len(card["atoms"]), 1)
        # A legacy five-axis card cannot inject keyword atoms: compile_pi re-derives the atom set
        # from the card's source clauses and ignores the keyword claim entirely.
        legacy = {"goal": "每頁保留三列。", "sources": [str(ROOT)], "constraints": [],
                  "non_goals": [], "subject_id": "INTENT-x", "content_hash": "0" * 64,
                  "schema_version": "IntentCard@1",
                  "atoms": [{"req_id": "REQ-INTENT", "axis": "intent"}]}
        atoms = pipeline.atoms_of(pipeline.compile_pi(legacy))
        self.assertEqual(len(atoms), 1)
        self.assertNotIn("REQ-INTENT", [a["req_id"] for a in atoms])
        self.assertIsInstance(atoms[0]["source_clause"], dict)
        self.assertEqual(atoms[0]["source_clause"]["text"], "每頁保留三列")
        # A clause-bound claim that diverges from its source clauses is refused, not merged.
        tampered = dict(card)
        tampered["atoms"] = copy.deepcopy(card["atoms"])
        tampered["atoms"][0] = dict(tampered["atoms"][0], req_id="REQ-FORGED")
        with self.assertRaises(PiSemanticFail):
            pipeline.compile_pi(tampered)

    def test_filler_goal_produces_no_package(self):
        for goal in ("嗯嗯。", "。。。", "啊，喔。"):
            with self.assertRaises(IntakeInvalid):
                pipeline.intake(goal, sources=[str(ROOT)])

    def test_normative_claim_without_source_is_refused(self):
        with self.assertRaises(IntakeInvalid):
            requirements.compile_requirements("實作系統", [])
        with self.assertRaises(AuthorityUnknown):
            pipeline.intake("實作系統", sources=[])


class RepoContextBinding(unittest.TestCase):
    """R-AUD-009: PD binding reads the real repository context."""

    @classmethod
    def setUpClass(cls):
        cls.pi = pipeline.compile_pi(pipeline.intake(GOAL, sources=[str(ROOT)]), "LITE")

    def test_bind_pd_derives_real_repository_context(self):
        claims = {"root": str(ROOT), "head": "HEAD", "tracked_files": 3,
                  "writable_scope": "src/**"}
        pd = pipeline.bind_pd(self.pi, claims)
        ctx = pd["RepoContext"]
        self.assertEqual(ctx["probe"], "git" if GIT else "filesystem")
        if GIT:
            head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                  capture_output=True, text=True).stdout.strip()
            tracked = subprocess.run(["git", "-C", str(ROOT), "ls-files"],
                                     capture_output=True, text=True).stdout.splitlines()
            self.assertEqual(ctx["head"], head, "PD must carry the host's git HEAD, not the claim")
            self.assertEqual(ctx["tracked_files"], len([l for l in tracked if l.strip()]))
            self.assertIsInstance(ctx["dirty"], bool)
            self.assertTrue(ctx["branch"])
        self.assertRegex(ctx["manifest_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(ctx["currentness_epoch"], r"^[0-9a-f]{64}$")
        self.assertEqual(ctx["readiness"], "PREDEV_READY")
        # Caller values were recorded as UNVERIFIED claims and never trusted into the record.
        self.assertFalse(ctx["caller_claims"]["head"]["verified"])
        self.assertFalse(ctx["caller_claims"]["head"]["matches_host"])
        self.assertFalse(ctx["caller_claims"]["tracked_files"]["verified"])
        self.assertNotEqual(ctx["tracked_files"], 3)
        self.assertNotEqual(ctx["head"], "HEAD")
        self.assertEqual(pd["currentness"]["state"], "FRESH")
        self.assertEqual(pd["currentness"]["claims_verified"], [])

    def test_spoofed_fresh_claim_is_refused(self):
        # The R-AUD-009 defect: a caller asserting FRESH was accepted. Now refused.
        with self.assertRaises(StaleProvider):
            pipeline.bind_pd(self.pi, {"root": str(ROOT), "currentness": "FRESH"})
        derived = repo_context.derive_repo_context(ROOT)
        with self.assertRaises(StaleProvider):
            pipeline.bind_pd(self.pi, {"root": str(ROOT), "currentness": "FRESH",
                                       "currentness_epoch": derived["currentness_epoch"],
                                       "tracked_files": 999999})
        with self.assertRaises(StaleProvider):
            pipeline.bind_pd(self.pi, {"root": str(ROOT), "currentness": "FRESH",
                                       "currentness_epoch": derived["currentness_epoch"],
                                       "manifest_sha256": "f" * 64})

    def test_forged_epoch_fresh_claim_is_refused(self):
        with self.assertRaises(StaleProvider):
            pipeline.bind_pd(self.pi, {"root": str(ROOT), "currentness": "FRESH",
                                       "currentness_epoch": "0" * 64})

    def test_stale_context_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "a.txt").write_text("x = 1\n", encoding="utf-8")
            stale = repo_context.derive_repo_context(td)
            (Path(td) / "b.txt").write_text("y = 2\n", encoding="utf-8")
            fresh = repo_context.derive_repo_context(td)
            self.assertNotEqual(stale["currentness_epoch"], fresh["currentness_epoch"],
                                "epoch must fingerprint the repository state")
            with self.assertRaises(StaleProvider):
                pipeline.bind_pd(self.pi, stale)

    @unittest.skipUnless(GIT, "git is required for the checkout-probe variant")
    def test_stale_git_context_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "repo"
            repo.mkdir()
            (repo / "a.txt").write_text("x = 1\n", encoding="utf-8")
            base = [GIT, "-C", str(repo)]
            subprocess.run(base + ["init", "-q"], capture_output=True)
            subprocess.run(base + ["add", "."], capture_output=True)
            subprocess.run(base + ["-c", "user.name=t", "-c", "user.email=t@t",
                                   "commit", "-q", "-m", "base"], capture_output=True)
            stale = repo_context.derive_repo_context(repo)
            self.assertEqual(stale["probe"], "git")
            (repo / "b.txt").write_text("y = 2\n", encoding="utf-8")
            subprocess.run(base + ["add", "."], capture_output=True)
            subprocess.run(base + ["-c", "user.name=t", "-c", "user.email=t@t",
                                   "commit", "-q", "-m", "next"], capture_output=True)
            with self.assertRaises(StaleProvider):
                pipeline.bind_pd(self.pi, stale)

    def test_verified_snapshot_binds(self):
        derived = repo_context.derive_repo_context(ROOT)
        pd = pipeline.bind_pd(self.pi, derived)
        self.assertEqual(pd["RepoContext"]["caller_claims"]["currentness"]["verified"], True)
        self.assertIn("currentness_epoch", pd["currentness"]["claims_verified"])
        self.assertEqual(pd["currentness"]["state"], "FRESH")

    def test_missing_repo_context_fails_closed(self):
        for ctx in (None, {}, {"writable_scope": "src/**"},
                    {"root": str(ROOT / "definitely-not-here")}):
            with self.assertRaises(RepoContextMissing):
                pipeline.bind_pd(self.pi, ctx)
        try:
            pipeline.bind_pd(self.pi, None)
        except RepoContextMissing as exc:
            self.assertEqual(exc.code, "REPO_CONTEXT_MISSING")
            self.assertNotIn("readiness", exc.as_dict(),
                             "the refusal envelope must not carry a readiness claim")
        # PREDEV_READY is only ever minted by a successful derivation.
        derived = repo_context.derive_repo_context(ROOT)
        self.assertEqual(derived["readiness"], "PREDEV_READY")

    def test_non_git_root_degrades_and_discloses(self):
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "a.txt").write_text("x = 1\n", encoding="utf-8")
            (Path(td) / "sub").mkdir()
            (Path(td) / "sub" / "b.py").write_text("y = 2\n", encoding="utf-8")
            ctx = repo_context.derive_repo_context(td)
            self.assertEqual(ctx["probe"], "filesystem")
            self.assertTrue(ctx["degraded"])
            self.assertTrue(ctx["degraded_reason"])
            self.assertIsNone(ctx["head"])
            self.assertEqual(ctx["tracked_files"], 2)
            pd = pipeline.bind_pd(self.pi, ctx)
            self.assertEqual(pd["RepoContext"]["probe"], "filesystem")
            self.assertTrue(pd["RepoContext"]["degraded"])
            self.assertTrue(pd["RepoContext"]["degraded_reason"])

    def test_writable_scope_is_reported_as_subset_check(self):
        pd = pipeline.bind_pd(self.pi, {"root": str(ROOT), "writable_scope": "src/**"})
        check = pd["late_bound_construction_binding"]["writable_scope_check"]
        self.assertEqual(check["requested"], ["src/**"])
        self.assertTrue(check["subset"])
        self.assertEqual(check["verdict"], "PASS")
        self.assertTrue(repo_context.writable_scope_subset_check("src/pipd_ls_sp/**")["subset"])
        for scope in ("../**", "schemas/**", "**"):
            with self.assertRaises(EffectUnknown):
                pipeline.bind_pd(self.pi, {"root": str(ROOT), "writable_scope": scope})
            self.assertFalse(repo_context.writable_scope_subset_check(scope)["subset"])

    def test_tracked_files_exclude_vcs_internals(self):
        with tempfile.TemporaryDirectory() as td:
            syn = Path(td) / "syn"
            (syn / "src").mkdir(parents=True)
            (syn / "src" / "a.py").write_text("x = 1\n", encoding="utf-8")
            (syn / "README.md").write_text("# syn\n", encoding="utf-8")
            (syn / ".git" / "objects" / "aa").mkdir(parents=True)
            (syn / ".git" / "objects" / "aa" / "blob").write_text("pack\n", encoding="utf-8")
            (syn / "__pycache__").mkdir()
            (syn / "__pycache__" / "m.pyc").write_text("bytecode\n", encoding="utf-8")
            self.assertEqual(repo_context.tracked_file_count(syn), 2)
            self.assertEqual(repo_context.probe_repository(syn)["tracked_files"], 2)


class FocusRepairPolarityAndBoundary(unittest.TestCase):
    """R5 §4.2/§4.3: the focused semantic repair, with positive AND negative coverage.

    D1: the pre-repair negation surface missed `不允許`／`請勿`／`should not`, so a prohibition was
    silently compiled as a MUST, and one clause-level negation flattened a neighbouring positive
    obligation into the same polarity. D2: the pre-repair scanner treated every ASCII period as a
    clause boundary, so `api.example.com` and `v1.2.3` dissolved into meaningless atoms.
    """

    def test_unlisted_prohibition_phrasings_are_negated(self):
        atoms = compile_fixture("REQ-NEG-PHRASES")
        self.assertEqual(len(atoms), 3)
        by_text = {a["source_clause"]["text"]: a for a in atoms}
        self.assertEqual(by_text["系統不允許傳送個資"]["risk_guard"]["polarity"], "MUST NOT")
        self.assertEqual(
            by_text["The system should not publish customer secrets"]["risk_guard"]["polarity"],
            "MUST NOT")
        # The pre-existing baseline phrasings must keep their meaning.
        self.assertEqual(by_text["系統不得上傳遙測"]["risk_guard"]["polarity"], "MUST NOT")
        self.assertEqual(len({a["risk_guard"]["negative_fixture"] for a in atoms}), 3)

    def test_positive_and_negative_scope_are_not_flattened(self):
        atoms = compile_fixture("REQ-MIXED-SCOPE")
        self.assertEqual(len(atoms), 2)
        by_text = {a["source_clause"]["text"]: a for a in atoms}
        self.assertEqual(by_text["系統必須記錄稽核日誌"]["risk_guard"]["polarity"], "MUST")
        self.assertEqual(by_text["不得外洩個資"]["risk_guard"]["polarity"], "MUST NOT")
        self.assertEqual(len({a["req_id"] for a in atoms}), 2)

    def test_ambiguous_negation_scope_is_refused_not_guessed(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "ambiguous.txt"
            src.write_text("系統必須不得外洩個資。\n", encoding="utf-8")
            with self.assertRaises(IntakeInvalid):
                requirements.compile_requirements("goal", [str(src)])
        with self.assertRaises(IntakeInvalid):
            requirements._expand("系統必須不得外洩個資")

    def test_domain_version_and_decimal_stay_one_atom(self):
        atoms = compile_fixture("REQ-D2-TOKENS")
        self.assertEqual(len(atoms), 3)
        self.assertEqual([a["source_clause"]["text"] for a in atoms],
                         ["系統不得上傳至 api.example.com", "版本必須為 v1.2.3", "比例必須為 1.25"])
        self.assertEqual(atoms[0]["risk_guard"]["polarity"], "MUST NOT")
        self.assertEqual(atoms[1]["risk_guard"]["polarity"], "MUST")

    def test_real_sentence_boundary_still_splits(self):
        atoms = compile_fixture("REQ-D2-SENTENCES")
        self.assertEqual([a["source_clause"]["text"] for a in atoms],
                         ["系統必須記錄日誌", "版本必須為 1.2"])

    def test_token_atoms_keep_their_original_source_span(self):
        source = (FIXTURES / "REQ-D2-TOKENS" / "source.txt").read_text(encoding="utf-8")
        for atom in compile_fixture("REQ-D2-TOKENS"):
            clause = atom["source_clause"]
            span = clause["span"]
            self.assertEqual(source[span[0]:span[1]], clause["text"])
            self.assertTrue(clause["clause_id"].startswith("clause-"))

    def test_same_polarity_segments_are_not_merged_into_one_atom(self):
        """A run of prohibitions stays per-obligation: one atom per boundary segment, never one atom.

        An earlier revision of this repair merged same-polarity segments back into a single atom.
        That is the same collapse the module exists to refuse: validate_atoms cannot see an obligation
        that was folded into another atom's text, so the obligation silently disappears from checks.
        """
        for text, expected in [
            ("系統不得交付遙測資料，不得上傳日誌。", 2),
            ("系統不得外洩個資，不得延遲交付。", 2),
            ("系統不得外洩個資以及不得延遲。", 2),
            ("The system must not log data, must not leak data.", 2),
        ]:
            with self.subTest(text=text):
                atoms = _expand_text(text)
                self.assertEqual(len(atoms), expected)
                self.assertTrue(all(a["risk_guard"]["polarity"] == "MUST NOT" for a in atoms))

    def test_a_negation_governs_a_following_uncued_segment(self):
        """The scope defect D1 fixed, pinned in the direction the old compiler got wrong.

        `不得外洩個資，延遲交付` used to compile the second, cue-less segment as MUST. It is inside the
        prohibition's scope, so it is MUST NOT - while a segment carrying its own positive modality
        keeps MUST.
        """
        atoms = _expand_text("系統不得外洩個資，延遲交付。")
        self.assertEqual([a["risk_guard"]["polarity"] for a in atoms], ["MUST NOT", "MUST NOT"])
        atoms = _expand_text("系統不得外洩個資，必須上傳日誌。")
        self.assertEqual([a["risk_guard"]["polarity"] for a in atoms], ["MUST NOT", "MUST"])

    def test_a_prohibition_whose_object_contains_a_modal_word_is_not_refused(self):
        """Fail-closed must not become fail-always: `必須的` is an adjective here, not an obligation."""
        atoms = _expand_text("系統不得使用必須的憑證。")
        self.assertEqual(len(atoms), 1)
        self.assertEqual(atoms[0]["risk_guard"]["polarity"], "MUST NOT")

    def test_period_between_two_letters_still_ends_a_clause(self):
        """A no-space sentence end (`A.Task`) is a boundary; a token (`api.example.com`) is not."""
        atoms = _expand_text("Do task A.Task B must run.")
        self.assertEqual([a["source_clause"]["text"] for a in atoms], ["Do task A", "Task B must run"])
        atoms = _expand_text("Rate is 5.Use 3.")
        self.assertEqual([a["source_clause"]["text"] for a in atoms], ["Rate is 5", "Use 3"])
        # ...while the token cases stay one atom each, which is the D2 repair itself.
        atoms = _expand_text("系統不得上傳至 api.example.com。")
        self.assertEqual(len(atoms), 1)

    def test_distributive_and_baseline_negation_regressions_hold(self):
        # The pre-existing negation fixture is the regression oracle for D1: its four atoms,
        # polarities and distributive sub-scopes must be byte-identical after the repair.
        atoms = compile_fixture("REQ-NEGATION")
        self.assertEqual(len(atoms), 4)
        by_text = {a["source_clause"]["text"]: a for a in atoms}
        self.assertEqual(by_text["系統不得交付遙測資料"]["risk_guard"]["polarity"], "MUST NOT")
        self.assertEqual(by_text["測試分別不得遺漏"]["risk_guard"]["polarity"], "MUST NOT")
        self.assertEqual(len({a["req_id"] for a in atoms}), 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
