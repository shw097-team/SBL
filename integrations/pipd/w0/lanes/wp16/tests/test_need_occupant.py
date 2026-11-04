#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-16 acceptance tests -- POS + NEG, stdlib unittest only.

POS  the shipped 30-row matrix is complete: every Need is classified, every row
     carries a license field with a resolvable source pointer, every Windows-fit
     and license value is either sourced or named UNBOUND, install_state never
     leaves {NOT_INSTALLED, PIN_HOLD, HOST_PIN_HOLD}, and every one of the
     selected Donor24/Method25 translators has is_installer=false.

NEG  the four contract refusal codes are each proven against a single injected
     defect, plus the corpus' own negative fixture:
       METHOD_NOT_INSTALLER  a method/donor recipe asked to act as installer
       LICENSE_UNBOUND       a Need whose license field is absent
       WINDOWS_NOFIT         a Need whose windows_fit is false
       OCCUPANT_UNBOUND      a Need with no occupant
       NEED_REQUIRED_DOWNGRADE  required downgraded away from
                                DESIGN_DEFAULT_REQUIRED (NEG-NEED.mutated.json)
       INSTALL_STATE_FORBIDDEN  an attempt to declare INSTALLED

Run:
    python -m unittest discover -s tests -v
"""

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.dirname(HERE)
if LANE not in sys.path:
    sys.path.insert(0, LANE)

import need_occupant as no  # noqa: E402

DEFAULT_SOURCE_ROOT = (
    r"C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric"
    r"\FHS／FHS-MSC／SBL\FHS\PIPD-LS-PKG\定案\W0\FHS_PIPD-LS-PKG_W0_R4C"
)


def source_root():
    root = os.environ.get("WP16_SOURCE_ROOT") or DEFAULT_SOURCE_ROOT
    if not os.path.isdir(root):
        raise RuntimeError("source root not found: %s (set WP16_SOURCE_ROOT)" % root)
    return root


_CACHE = {}


def load():
    """Load sources + build all artifacts once (read-only on the source root)."""
    if not _CACHE:
        src = no.Sources(source_root())
        _CACHE["sources"] = src
        _CACHE["bundle"] = no.build_all(src)
    return _CACHE["sources"], _CACHE["bundle"]


def build_with(overrides):
    src = _CACHE.get("sources") or load()[0]
    return no.build_all(src, overrides=overrides)


def row_of(matrix, need_id):
    for row in matrix["rows"]:
        if row["need_id"] == need_id:
            return row
    raise AssertionError("row not found: %s" % need_id)


CONTRACT_FIELDS = (
    "need_id",
    "need_class",
    "required",
    "occupant_id",
    "occupant_kind",
    "license",
    "license_source_ref",
    "windows_fit",
    "windows_fit_evidence",
    "consumer",
    "consumer_ref",
    "nofit_reason",
    "install_state",
    "status",
)


class TestPosMatrix(unittest.TestCase):
    """POS: the shipped matrix is complete, sourced, and honest about UNBOUND."""

    @classmethod
    def setUpClass(cls):
        cls.sources, cls.bundle = load()
        cls.matrix = cls.bundle["matrix"]
        cls.rows = cls.matrix["rows"]

    def test_need_denominator_equals_source_bytes(self):
        on_disk = no.read_json(os.path.join(self.sources.root, no.FILE_DEFAULT30))
        self.assertEqual(len(on_disk), 30, "DEFAULT30_CHOICES.json must hold 30 Needs")
        self.assertEqual(len(self.rows), len(on_disk), "matrix denominator must equal the source array length")
        self.assertEqual([r["need_id"] for r in self.rows], [e["original_id"] for e in on_disk])

    def test_all_thirty_needs_classified_with_contract_fields(self):
        self.assertEqual(len(self.rows), 30)
        for row in self.rows:
            for field in CONTRACT_FIELDS:
                self.assertIn(field, row, "%s missing field %s" % (row.get("need_id"), field))
            self.assertTrue(row["need_id"].startswith("Default30:"))
            self.assertIn(row["status"], no.ALLOWED_STATUS)
            self.assertIn(row["occupant_kind"], no.ALLOWED_KIND)
            self.assertIsInstance(row["required"], bool)
            self.assertTrue(row["need_class"])
            self.assertTrue(row["occupant_id"], "%s has no occupant" % row["need_id"])
            self.assertTrue(row["consumer"], "%s has no consumer" % row["need_id"])

    def test_every_row_carries_a_license_field_with_source_pointer(self):
        for row in self.rows:
            self.assertIn("license", row)
            self.assertTrue(row["license"], "%s license rendered empty" % row["need_id"])
            self.assertTrue(row["license_source_ref"].startswith(no.FILE_DEFAULT30 + "#/"))
            pointer = row["license_source_ref"].split("#", 1)[1]
            self.assertTrue(
                no.pointer_ok(self.sources.default30, pointer),
                "license pointer does not resolve: %s" % row["license_source_ref"],
            )
            # either the value is the source literal, or it is the literal UNBOUND
            self.assertTrue(
                row["license"] == no.resolve_pointer(self.sources.default30, pointer) or row["license"] == "UNBOUND",
                "%s license is not a byte-literal copy" % row["need_id"],
            )
            self.assertIn(
                row["license_state"],
                (no.LIC_DECLARED, no.LIC_DECLARED_ACK_PENDING, no.LIC_READER_HOLD, no.LIC_UNBOUND),
            )

    def test_every_windows_fit_is_sourced_or_unbound(self):
        for row in self.rows:
            evidence = row["windows_fit_evidence"]
            self.assertIn(row["windows_fit"], (no.FIT_UNBOUND, no.FIT_FIT, no.FIT_NOFIT))
            self.assertTrue(evidence["ref"])
            if evidence["source_file"] == no.FILE_DEFAULT30:
                pointer = evidence["pointer"]
                self.assertTrue(no.pointer_ok(self.sources.default30, pointer))
                self.assertEqual(
                    no.resolve_pointer(self.sources.default30, pointer),
                    evidence["value"],
                    "%s windows_fit_evidence is not a byte-literal copy" % row["need_id"],
                )
            if row["windows_fit"] == no.FIT_UNBOUND:
                self.assertIn(
                    "UNBOUND",
                    str(evidence["value"]).upper(),
                    "%s is UNBOUND but the source does not say so" % row["need_id"],
                )

    def test_status_counts_match_the_declaration(self):
        counts = self.matrix["counts"]
        self.assertEqual(counts["needs_total"], 30)
        self.assertEqual(counts["required_true"], 30)
        self.assertEqual(counts["occupant_pin_hold"], 28)
        self.assertEqual(counts["host_pin_hold"], 2)
        self.assertEqual(counts["selected"], 0)
        self.assertEqual(counts["nofit"], 0)
        self.assertEqual(counts["unbound"], 0)
        self.assertEqual(counts["occupant_pin_hold"] + counts["host_pin_hold"], 30)
        comparison = self.matrix["declaration_comparison"]
        self.assertEqual(comparison["verdict"], "MATCH")
        self.assertEqual(comparison["mismatches"], [])
        self.assertEqual(comparison["declared"]["occupant_pin_hold"], 28)
        self.assertEqual(comparison["declared"]["host_pin_hold"], 2)
        self.assertEqual(comparison["declared"]["required"], 30)

    def test_install_state_never_leaves_the_allowed_vocabulary(self):
        for row in self.rows:
            self.assertIn(row["install_state"], no.ALLOWED_INSTALL_STATE)
        states = {row["install_state"] for row in self.rows}
        self.assertEqual(states, {no.INSTALL_PIN_HOLD, no.INSTALL_HOST_PIN_HOLD})
        # no row may carry INSTALLED / VERIFIED anywhere in its own payload
        forbidden = set(no.FORBIDDEN_INSTALL_STATES)

        def scalars(node):
            if isinstance(node, dict):
                for value in node.values():
                    for item in scalars(value):
                        yield item
            elif isinstance(node, list):
                for value in node:
                    for item in scalars(value):
                        yield item
            else:
                yield node

        for row in self.rows:
            for value in scalars(row):
                if isinstance(value, str):
                    self.assertNotIn(value.strip(), forbidden, "%s carries the state %r" % (row["need_id"], value))
        self.assertEqual(self.matrix["field_contract"]["install_state_forbidden"], ["INSTALLED", "VERIFIED"])
        # the aggregate declaration says the same thing
        self.assertTrue(self.matrix["declaration_comparison"]["computed"]["no_installed_or_verified_upgrade"])

    def test_host_pin_hold_rows_are_the_two_declared_needs(self):
        host = sorted(r["need_id"] for r in self.rows if r["status"] == no.STATUS_HOST_PIN_HOLD)
        self.assertEqual(host, ["Default30:P0-TOOL-001", "Default30:P0-TOOL-011"])

    def test_occupant_kind_taxonomy_is_consistent_with_bindings(self):
        kinds = {r["occupant_kind"] for r in self.rows}
        self.assertTrue(kinds <= set(no.ALLOWED_KIND))
        self.assertEqual(self.matrix["counts"]["occupant_kind"][no.KIND_NONE], 0)
        wp16_ids = {row["original_id"] for row in self.sources.wp16}
        for row in self.rows:
            if row["occupant_kind"] in (no.KIND_DONOR, no.KIND_METHOD):
                self.assertTrue(row["occupant_items"], "%s claims %s without an item" % (row["need_id"], row["occupant_kind"]))
            if row["occupant_kind"] == no.KIND_HOST:
                self.assertFalse(row["occupant_items"])
            for item in row["occupant_items"]:
                self.assertIn(item, wp16_ids)
                if row["occupant_kind"] == no.KIND_DONOR:
                    self.assertTrue(item.startswith("Donor24:") or item.startswith("Method25:"))

    def test_selection_rules_re_verify_against_the_live_registry(self):
        bindings = self.matrix["resolved_bindings"]
        self.assertTrue(bindings)
        by_id = {row["original_id"]: row for row in self.sources.wp16}
        records = {row["original_id"]: row for row in self.sources.default30}
        for rule in no.SELECTION_RULES:
            need_record = records[rule["need_id"]]
            for binding in bindings.get(rule["need_id"], []):
                row = by_id[binding["wp16_id"]]
                self.assertTrue(
                    no.rule_matches(rule, row, need_record),
                    "rule %s no longer matches %s" % (rule["need_id"], binding["wp16_id"]),
                )
        self.assertEqual(self.matrix["selection_holds"], [])

    def test_every_unbound_field_has_a_named_hold(self):
        named = {h["code"] for h in self.matrix["named_holds"]}
        self.assertIn("WINDOWS_FIT_UNBOUND", named)
        self.assertIn(no.LIC_READER_HOLD, named)
        for row in self.rows:
            for item in row["unbound_fields"]:
                self.assertIn(item["code"], named, "%s/%s has no named hold" % (row["need_id"], item["field"]))
            if row["license"] == "UNBOUND":
                self.assertIn(no.R_LICENSE_UNBOUND, row["refusal_codes"])

    def test_tech485_rows_are_rehashed_not_trusted(self):
        verified = self.sources.verified_rows()
        self.assertEqual(verified["failed"], 0)
        self.assertEqual(verified["verified"], verified["total"])
        self.assertEqual(verified["total"], 485)
        for row in self.rows:
            for ev in row["evidence"]["tech485_rows"]:
                self.assertTrue(ev["verified"], "%s TECH485 row_sha failed" % row["need_id"])
                self.assertTrue(ev["row_sha"])


class TestPosTranslators(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources, cls.bundle = load()
        cls.tmap = cls.bundle["translator_map"]

    def test_all_translators_are_not_installers(self):
        self.assertGreater(len(self.tmap["translators"]), 0)
        for spec in self.tmap["translators"]:
            self.assertIs(spec["is_installer"], False, "%s claims installer" % spec["translator_id"])
            self.assertNotIn(True, [t["is_installer"] for t in self.tmap["translators"]])
        self.assertTrue(self.tmap["is_installer_all_false"])
        self.assertEqual(self.tmap["installer_claim"], "NONE")
        self.assertEqual(self.tmap["counts"]["is_installer_true"], 0)

    def test_each_translator_has_full_spec(self):
        for spec in self.tmap["translators"]:
            for key in ("translator_id", "input_schema", "output_schema", "refusal_codes", "is_installer", "source_ref"):
                self.assertIn(key, spec)
            self.assertIn(no.R_METHOD_NOT_INSTALLER, spec["refusal_codes"])
            self.assertTrue(spec["input_schema"]["required_fields"])
            self.assertTrue(spec["output_schema"]["artifact_literal"])
            self.assertTrue(spec["output_schema"]["advisory_only"])
            self.assertTrue(spec["source_ref"]["wp16_pointer"].startswith(no.FILE_WP16 + "#/"))

    def test_only_selected_items_get_a_translator(self):
        counts = self.tmap["counts"]
        self.assertEqual(counts["wp16_items_total"], 49)
        self.assertEqual(counts["translators"] + counts["unselected_items"], 49)
        selected = {t["wp16_id"] for t in self.tmap["translators"]}
        for item in self.tmap["excluded_unselected"]:
            self.assertNotIn(item["wp16_id"], selected)
        # GSD / gstack / BMAD donors and methods are not Default30 Needs in this wave
        for absent in ("Donor24:SLOT-GS-01", "Donor24:SLOT-GT-01", "Method25:METHOD-01"):
            self.assertNotIn(absent, selected)

    def test_translator_source_rows_verify(self):
        for spec in self.tmap["translators"]:
            self.assertTrue(spec["source_ref"]["row_sha_evidence"], spec["translator_id"])
            for ev in spec["source_ref"]["row_sha_evidence"]:
                self.assertTrue(ev["verified"])
            self.assertEqual(spec["source_ref"]["wp16_file_sha256"], self.sources.file_sha(no.FILE_WP16))

    def test_translate_produces_advisory_artifact(self):
        spec = self.tmap["translators"][0]
        out = no.translate(self.tmap, spec["translator_id"], mode="advisory")
        self.assertIs(out["is_installer"], False)
        self.assertIs(out["installed"], False)
        self.assertIsNone(out["state_upgrade"])
        self.assertTrue(out["advisory_only"])
        self.assertEqual(out["produced_as"], spec["output_schema"]["produced_as"])


class TestNegatives(unittest.TestCase):
    """NEG: each contract code is proven by exactly one injected defect."""

    @classmethod
    def setUpClass(cls):
        cls.sources, cls.bundle = load()
        cls.tmap = cls.bundle["translator_map"]

    def test_neg_method_as_installer_refused(self):
        method = [t for t in self.tmap["translators"] if t["kind"] == no.KIND_METHOD][0]
        donor = [t for t in self.tmap["translators"] if t["kind"] == no.KIND_DONOR][0]
        for spec in (method, donor):
            with self.assertRaises(no.Refusal) as caught:
                no.translate(self.tmap, spec["translator_id"], mode="install")
            self.assertEqual(caught.exception.code, "METHOD_NOT_INSTALLER")
            detail = caught.exception.to_dict()
            self.assertEqual(detail["translator_id"], spec["translator_id"])
            self.assertIs(detail["is_installer"], False)
            self.assertEqual(detail["corpus_first_fail"], "METHOD_AS_INSTALL_DENY")

    def test_neg_method_only_item_carries_its_own_deny_token(self):
        grill = [t for t in self.tmap["translators"] if t["wp16_id"] == "Method25:METHOD-02"][0]
        self.assertEqual(grill["occupant_class"], "METHOD_ONLY")
        self.assertIn("METHOD_AS_INSTALL_DENY", grill["refusal_codes"])
        with self.assertRaises(no.Refusal) as caught:
            no.translate(self.tmap, grill["translator_id"], mode="installer")
        self.assertEqual(caught.exception.code, "METHOD_NOT_INSTALLER")

    def test_neg_missing_license_is_license_unbound(self):
        need_id = "Default30:P0-TOOL-003"
        matrix = build_with({need_id: {"license": ""}})["matrix"]
        row = row_of(matrix, need_id)
        self.assertIn("LICENSE_UNBOUND", row["refusal_codes"])
        self.assertEqual(row["status"], no.STATUS_UNBOUND)
        self.assertEqual(row["license"], "UNBOUND")
        self.assertEqual(row["license_state"], no.LIC_UNBOUND)
        self.assertIn({"field": "license", "code": "LICENSE_UNBOUND"}, row["unbound_fields"])
        self.assertEqual(matrix["counts"]["unbound"], 1)

    def test_neg_windows_fit_false_is_windows_nofit(self):
        need_id = "Default30:P0-TOOL-004"
        matrix = build_with({need_id: {"windows_fit": False}})["matrix"]
        row = row_of(matrix, need_id)
        self.assertIn("WINDOWS_NOFIT", row["refusal_codes"])
        self.assertEqual(row["windows_fit"], no.FIT_NOFIT)
        self.assertEqual(row["status"], no.STATUS_NOFIT)
        self.assertEqual(matrix["counts"]["nofit"], 1)

    def test_neg_no_occupant_is_occupant_unbound(self):
        need_id = "Default30:P0-TOOL-005"
        matrix = build_with({need_id: {"selected_occupant": ""}})["matrix"]
        row = row_of(matrix, need_id)
        self.assertIn("OCCUPANT_UNBOUND", row["refusal_codes"])
        self.assertEqual(row["status"], no.STATUS_UNBOUND)
        self.assertEqual(row["occupant_kind"], no.KIND_NONE)
        self.assertEqual(row["occupant_id"], "UNBOUND")
        self.assertEqual(matrix["counts"]["unbound"], 1)

    def test_neg_required_downgrade_is_refused_and_named(self):
        need_id = "Default30:P0-TOOL-006"
        matrix = build_with({need_id: {"required": "OPTIONAL"}})["matrix"]
        row = row_of(matrix, need_id)
        self.assertIn("NEED_REQUIRED_DOWNGRADE", row["refusal_codes"])
        self.assertFalse(row["required"])
        self.assertEqual(row["status"], no.STATUS_UNBOUND)
        self.assertEqual(matrix["counts"]["required_true"], 29)
        comparison = matrix["declaration_comparison"]
        self.assertEqual(comparison["verdict"], "MISMATCH")
        claims = {m["claim"]: m for m in comparison["mismatches"]}
        self.assertIn("required", claims)
        self.assertEqual(claims["required"]["declared"], 30)
        self.assertEqual(claims["required"]["computed"], 29)
        self.assertEqual(claims["required"]["delta"], -1)
        self.assertIn(need_id, claims["required"]["computed_need_ids"])

    def test_neg_corpus_fixture_neg_need_mutated(self):
        fixture_path = os.path.join(self.sources.root, no.FILE_NEG_NEED)
        self.assertTrue(os.path.isfile(fixture_path), "corpus negative fixture must exist")
        mutated = no.read_json(fixture_path)
        self.assertNotEqual(mutated["required"], no.REQUIRED_MARKER)
        matrix = build_with({mutated["original_id"]: {"required": mutated["required"]}})["matrix"]
        row = row_of(matrix, mutated["original_id"])
        self.assertIn("NEED_REQUIRED_DOWNGRADE", row["refusal_codes"])
        self.assertEqual(row["status"], no.STATUS_UNBOUND)

    def test_neg_installed_install_state_forbidden(self):
        need_id = "Default30:P0-TOOL-008"
        with self.assertRaises(no.Refusal) as caught:
            build_with({need_id: {"install_state": "INSTALLED"}})
        self.assertEqual(caught.exception.code, "INSTALL_STATE_FORBIDDEN")
        with self.assertRaises(no.Refusal) as caught:
            build_with({need_id: {"install_state": "VERIFIED"}})
        self.assertEqual(caught.exception.code, "INSTALL_STATE_FORBIDDEN")

    def test_neg_alias_evidence_missing_refuses_to_bind(self):
        need_id = "Default30:P0-TOOL-025"
        matrix = build_with(
            {need_id: {"original_consumer": "nothing here", "hold_owner": "nothing here", "original_business": "nothing here"}}
        )["matrix"]
        codes = [h["code"] for h in matrix["selection_holds"]]
        self.assertIn("ALIAS_EVIDENCE_MISSING", codes)
        row = row_of(matrix, need_id)
        self.assertEqual(row["occupant_items"], [])
        self.assertEqual(row["occupant_kind"], no.KIND_HOST)

    def test_neg_unknown_translator(self):
        with self.assertRaises(no.Refusal) as caught:
            no.translate(self.tmap, "TRANSLATOR:Donor24:SLOT-NOPE", mode="advisory")
        self.assertEqual(caught.exception.code, "UNKNOWN_TRANSLATOR")


class TestPosOutputsAndDeterminism(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources, cls.bundle = load()

    def test_cli_writes_four_artifacts_and_exits_zero(self):
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            code = no.main(["--source-root", self.sources.root, "--out", tmp])
            self.assertEqual(code, 0)
            expected = (
                "NEED_OCCUPANT_MATRIX.json",
                "NEED_OCCUPANT_MATRIX.md",
                "TRANSLATOR_MAP.json",
                "TECH_CHOICE_READBACK.json",
            )
            for name in expected:
                path = os.path.join(tmp, name)
                self.assertTrue(os.path.isfile(path), "missing artifact %s" % name)
                self.assertGreater(os.path.getsize(path), 0)
            matrix = no.read_json(os.path.join(tmp, "NEED_OCCUPANT_MATRIX.json"))
            self.assertEqual(len(matrix["rows"]), 30)
            md = no.read_text(os.path.join(tmp, "NEED_OCCUPANT_MATRIX.md"))
            self.assertIn("OCCUPANT_PIN_HOLD", md)
            self.assertIn("MATCH", md)

    def test_output_is_deterministic(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(no.main(["--source-root", self.sources.root, "--out", a]), 0)
            self.assertEqual(no.main(["--source-root", self.sources.root, "--out", b]), 0)
            for name in ("NEED_OCCUPANT_MATRIX.json", "TRANSLATOR_MAP.json", "TECH_CHOICE_READBACK.json"):
                self.assertEqual(
                    no.sha256_file(os.path.join(a, name)),
                    no.sha256_file(os.path.join(b, name)),
                    "%s is not deterministic" % name,
                )

    def test_input_identity_matches_the_manifest(self):
        for name in (no.FILE_DEFAULT30, no.FILE_WP16, no.FILE_TECH485, no.FILE_CCS):
            info = self.sources.files[name]
            self.assertEqual(info["identity"], "MATCH", "%s does not match INDEX_AND_MANIFEST" % name)
            self.assertEqual(info["sha256"], no.sha256_file(os.path.join(self.sources.root, name)))

    def test_readback_resolves_every_pointer(self):
        readback = self.bundle["readback"]
        self.assertEqual(readback["counts"]["needs"], 30)
        self.assertEqual(readback["counts"]["evidence_unresolved"], 0)
        for entry in readback["entries"]:
            self.assertTrue(entry["evidence"], entry["need_id"])
            for ev in entry["evidence"]:
                self.assertTrue(ev["resolved"], "%s unresolved %s" % (entry["need_id"], ev["ref"]))
            self.assertEqual(entry["status"], row_of(self.bundle["matrix"], entry["need_id"])["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
