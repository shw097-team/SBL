"""G1/G2 candidate guard: per-source clause-set intake + read-only adjudication checking.

What these tests pin, in order of how easy each is to break later:

1.  ``compile_pinned_clauses`` is the SAME compiler as ``compile_requirements``: for a document
    with no refusal the atoms are equal, atom for atom, including their ids. If a future edit
    changes one path and not the other, this fails.
2.  Failure isolation is the only difference: a document that aborts the whole compile at clause 2
    still yields clause 3 here, with clause 2's refusal recorded verbatim.
3.  A span that ``_parts`` did not yield is refused by name - never trimmed, merged or re-derived.
4.  The 13-verb exact set and every verb's FAILURE_CODES string are unchanged.
5.  ``intake`` still refuses a missing ``--goal`` exactly as before when ``--clause-set`` is absent.
6.  ``validate --adjudications`` is READ-ONLY: the bundle result is byte-identical with and
    without the flag, and a decision set that is merely incomplete cannot fail a valid bundle.
7.  A record with only ``reader_identity`` / ``authority_ref`` is UNVERIFIED, not a decision.
8.  With no reader key enrolled, even a correctly signed record is UNVERIFIED.
9.  A TEST_FIXTURE_ONLY enrollment verifies the signature but can never claim original authority.
10. An enrollment file that is not TEST_FIXTURE_ONLY cannot be substituted.
11. ``INTAKE_INVALID`` recorded as a reader NACK is refused by name.
12. A maker identity in the reader field is refused as self-acceptance.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import adjudication, clause_set, pipeline, requirements  # noqa: E402
from pipd_ls_sp.cli import COMMANDS, FAILURE_CODES  # noqa: E402
from pipd_ls_sp.errors import IntakeInvalid  # noqa: E402
from pipd_ls_sp.util import canonical_json, sha256_text  # noqa: E402

ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
DOC = ("Service must log every refusal。"
       "Operator must not delete the audit trail；"
       "Reviewer must sign the release。")


def cli(*args: str) -> tuple[int, dict]:
    proc = subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", *args],
                          capture_output=True, text=True, env=ENV, cwd=str(ROOT))
    try:
        return proc.returncode, json.loads(proc.stdout)
    except json.JSONDecodeError:  # pragma: no cover - a crash would surface here
        raise AssertionError(f"stdout was not JSON: {proc.stdout!r} stderr={proc.stderr!r}")


class PinnedClausesAreTheSameCompiler(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.doc = self.dir / "doc.md"
        self.doc.write_text(DOC, encoding="utf-8")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_atoms_equal_compile_requirements_when_nothing_is_refused(self) -> None:
        spans = [(s, e) for s, e, _ in requirements._parts(DOC)]
        self.assertEqual(len(spans), 3)
        rows = requirements.compile_pinned_clauses(DOC, str(self.doc), spans)
        self.assertEqual([r["state"] for r in rows], ["ATOMS"] * 3)
        pinned = [a for r in rows for a in r["atoms"]]
        whole = requirements.compile_requirements(DOC, [str(self.doc)])
        self.assertEqual(canonical_json(pinned), canonical_json(whole),
                         "pinned-clause atoms diverged from compile_requirements")

    def test_one_bad_clause_does_not_lose_the_rest(self) -> None:
        bad = "共有三種各有不同的處理方式；Service must log every refusal。"
        bad_doc = self.dir / "bad.md"
        bad_doc.write_text(bad, encoding="utf-8")
        with self.assertRaises(IntakeInvalid):
            requirements.compile_requirements(bad, [str(bad_doc)])
        spans = [(s, e) for s, e, _ in requirements._parts(bad)]
        rows = requirements.compile_pinned_clauses(bad, str(bad_doc), spans)
        self.assertEqual(rows[0]["state"], "REFUSED")
        self.assertEqual(rows[0]["code"], "INTAKE_INVALID")
        self.assertIn("ambiguous compound", rows[0]["message"])
        self.assertEqual(rows[-1]["state"], "ATOMS")
        self.assertTrue(rows[-1]["atoms"], "the clause after the refusal must still compile")

    def test_span_that_parts_did_not_yield_is_refused_by_name(self) -> None:
        rows = requirements.compile_pinned_clauses(DOC, str(self.doc), [(1, 5)])
        self.assertEqual(rows[0]["state"], "REFUSED")
        self.assertEqual(rows[0]["code"], "SPAN_NOT_A_CLAUSE_BOUNDARY")

    def test_source_id_is_the_compilers_own_derivation(self) -> None:
        spans = [(s, e) for s, e, _ in requirements._parts(DOC)]
        card = clause_set.run(self._clause_file(spans), self.doc)
        subject_sha = sha256_text(DOC)
        for entry in card["sources"]:
            expected = requirements.source_id_for(str(self.doc), entry["clause_id"], subject_sha)
            self.assertEqual(entry["source_id"], expected)
            self.assertEqual(entry["state"], "ATOMS")
            self.assertTrue(entry["polarity"])
        self.assertEqual(card["schema_version"], "ClauseSetIntake@1")
        self.assertEqual(card["reader_disposition"], "NOT_PRODUCED_BY_COMPILER")
        self.assertEqual(card["verdict"], "PASS")

    def test_a_declared_source_id_that_does_not_derive_is_refused(self) -> None:
        spans = [(s, e) for s, e, _ in requirements._parts(DOC)]
        path = self.dir / "forged.tsv"
        path.write_text("clause_id\tspan_start\tspan_end\tsource_id\n"
                        f"clause-{spans[0][0]}-{spans[0][1]}\t{spans[0][0]}\t{spans[0][1]}\t"
                        "SRC-00000000000000000000\n", encoding="utf-8")
        card = clause_set.run(path, self.doc)
        self.assertEqual(card["sources"][0]["code"], "SOURCE_ID_MISMATCH")
        self.assertEqual(card["verdict"], "FAIL")

    def _clause_file(self, spans: list[tuple[int, int]]) -> Path:
        path = self.dir / "clauses.tsv"
        lines = ["clause_id\tspan_start\tspan_end"]
        lines += [f"clause-{s}-{e}\t{s}\t{e}" for s, e in spans]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path


class SurfaceIsStillThirteenVerbs(unittest.TestCase):
    def test_exact_verb_set(self) -> None:
        self.assertEqual(COMMANDS, ("init", "intake", "profile", "compile-pi", "bind-pd",
                                    "compile-ecp", "compile-tqaep", "validate", "doctor",
                                    "project", "export", "diff", "repair"))
        self.assertEqual(len(COMMANDS), 13)

    def test_failure_codes_unchanged(self) -> None:
        self.assertEqual(FAILURE_CODES["intake"], "INTAKE_INVALID/AUTHORITY_UNKNOWN")
        self.assertEqual(FAILURE_CODES["validate"], "VALIDATION_FAIL")
        self.assertEqual(len(FAILURE_CODES), 13)

    def test_intake_without_goal_is_still_a_usage_refusal(self) -> None:
        code, out = cli("intake", "--source", str(ROOT))
        self.assertEqual(code, 2)
        self.assertEqual(out, {"verdict": "FAIL", "code": "USAGE_INVALID",
                               "message": "invalid command line; see --help for the 13 commands"})

    def test_clause_set_without_subject_is_typed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c.tsv"
            path.write_text("clause_id\tspan_start\tspan_end\nclause-0-1\t0\t1\n", encoding="utf-8")
            code, out = cli("intake", "--clause-set", str(path))
        self.assertEqual(code, 2)
        self.assertEqual(out["code"], "INPUT_SHAPE_INVALID")


class AdjudicationIsReadOnly(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        doc = self.dir / "doc.md"
        doc.write_text("Service must log every refusal.", encoding="utf-8")
        self.intent = pipeline.intake("Service must log every refusal", sources=[str(self.dir)])
        pi = pipeline.compile_pi(self.intent, "LITE")
        (self.dir / "pi.json").write_text(json.dumps(pi), encoding="utf-8")
        (self.dir / "bundle.json").write_text(json.dumps({"PI-PKG": pi}), encoding="utf-8")
        self.subject = doc
        self.doc_text = doc.read_text(encoding="utf-8")
        self.subject_sha = sha256_text(self.doc_text)
        span = next((s, e) for s, e, _ in requirements._parts(self.doc_text))
        self.span = [span[0], span[1]]
        self.clause_sha = sha256_text(self.doc_text[span[0]:span[1]])
        self.source_id = requirements.source_id_for(str(doc), f"clause-{span[0]}-{span[1]}",
                                                    self.subject_sha)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def record(self, **over) -> dict:
        body = {"schema": "SBL.SourceAdjudication@1", "source_id": self.source_id,
                "subject_sha256": self.subject_sha,
                "clause_id": f"clause-{self.span[0]}-{self.span[1]}", "span": self.span,
                "clause_sha256": self.clause_sha, "decision": "ACCEPT",
                "basis": "quoted ruling", "reader_id": "ORIGINAL_SBL_PIPD_READER",
                "decided_at": "2026-11-17T00:00:00+00:00",
                "claim_ceiling": "READER_ADJUDICATION_NOT_PRODUCT_ACCEPTANCE"}
        body.update(over)
        return body

    def write(self, name: str, records: list[dict]) -> Path:
        path = self.dir / name
        path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")
        return path

    def check(self, records: list[dict], **kw):
        return adjudication.check(self.write("a.jsonl", records),
                                  subject=self.subject, **kw)

    def test_bundle_verdict_is_byte_identical_with_and_without_the_flag(self) -> None:
        bundle = str(self.dir / "bundle.json")
        plain_code, plain = cli("validate", "--bundle", bundle)
        path = self.write("unsigned.jsonl", [self.record()])
        flag_code, flagged = cli("validate", "--bundle", bundle, "--adjudications", str(path),
                                 "--subject", str(self.subject))
        self.assertEqual(flag_code, plain_code)
        self.assertEqual({k: v for k, v in flagged.items() if k != "adjudication"}, plain)
        self.assertEqual(flagged["adjudication"]["read_only"], True)
        self.assertEqual(flagged["adjudication"]["wrote_nothing"], True)

    def test_unsigned_record_is_unverified(self) -> None:
        block = self.check([self.record(reader_identity="ORIGINAL_SBL_PIPD_READER",
                                        authority_ref="owner-envelope/whatever")])
        self.assertEqual(block["verdict"], "UNVERIFIED")
        self.assertEqual(block["states"]["VERIFIED"], 0)
        self.assertIn("ADJUDICATION_UNSIGNED", [f["code"] for f in block["findings"]])
        self.assertFalse(block["original_reader_signature_verified"])

    def test_no_enrolled_key_means_unverified_even_when_signed(self) -> None:
        private, enrollment = self._key()
        rec = self.record()
        rec["signature"] = _sign(rec, private)
        block = self.check([rec])
        self.assertEqual(block["reader_key"]["state"], "READER_KEY_NOT_ENROLLED")
        self.assertEqual(block["verdict"], "UNVERIFIED")

    def test_fixture_enrollment_verifies_but_never_claims_original_authority(self) -> None:
        private, enrollment = self._key()
        rec = self.record(reader_id="TEST_FIXTURE_READER")
        rec["signature"] = _sign(rec, private)
        block = self.check([rec], enrollment=enrollment)
        self.assertEqual(block["states"]["VERIFIED"], 1)
        self.assertEqual(block["verdict"], "COMPLETE_FIXTURE_KEY_ONLY")
        self.assertFalse(block["original_reader_signature_verified"])
        self.assertEqual(block["claim_ceiling"], "FIXTURE_KEY_NOT_ORIGINAL_READER")

    def test_non_fixture_enrollment_cannot_be_substituted(self) -> None:
        private, enrollment = self._key()
        body = json.loads(enrollment.read_text(encoding="utf-8"))
        body["authority"] = "ORIGINAL_READER"
        enrollment.write_text(json.dumps(body), encoding="utf-8")
        rec = self.record(reader_id="TEST_FIXTURE_READER")
        rec["signature"] = _sign(rec, private)
        block = self.check([rec], enrollment=enrollment)
        self.assertIn("READER_ENROLLMENT_NOT_TEST_FIXTURE",
                      [f["code"] for f in block["findings"]])
        self.assertEqual(block["states"]["VERIFIED"], 0)

    def test_compiler_refusal_recorded_as_nack_is_refused_by_name(self) -> None:
        private, enrollment = self._key()
        rec = self.record(decision="NACK", reader_id="TEST_FIXTURE_READER",
                          basis="INTAKE_INVALID - the compiler refused this clause")
        rec["signature"] = _sign(rec, private)
        block = self.check([rec], enrollment=enrollment)
        self.assertEqual(block["verdict"], "REFUSED")
        codes = [f["code"] for f in block["findings"]]
        self.assertIn("INTAKE_INVALID_IS_NOT_A_DISPOSITION", codes)
        self.assertEqual(block["by_decision"]["NACK"], 0,
                         "a refused NACK must not be counted in the decision histogram")

    def test_maker_may_not_be_the_reader(self) -> None:
        private, enrollment = self._key()
        rec = self.record(reader_id="TEST_FIXTURE_READER")
        rec["signature"] = _sign(rec, private)
        block = self.check([rec], enrollment=enrollment, maker="TEST_FIXTURE_READER")
        self.assertIn("SELF_ACCEPT", [f["code"] for f in block["findings"]])

    def test_tampered_span_is_caught_from_the_subject_bytes(self) -> None:
        private, enrollment = self._key()
        start, end = self.span[0] + 1, self.span[1] + 1
        rec = self.record(span=[start, end], reader_id="TEST_FIXTURE_READER",
                          clause_sha256=sha256_text(self.doc_text[start:end]))
        rec["signature"] = _sign(rec, private)
        block = self.check([rec], enrollment=enrollment)
        self.assertIn("ADJUDICATION_SOURCE_MISMATCH",
                      [f["code"] for f in block["findings"]])

    def _key(self):
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        private = Ed25519PrivateKey.generate()
        public_hex = private.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw).hex()
        enrollment = self.dir / "test_enrollment.json"
        enrollment.write_text(json.dumps({
            "schema": "SBL.READER_ENROLLMENT@1", "reader_id": "TEST_FIXTURE_READER",
            "authority": "TEST_FIXTURE_ONLY", "state": "READER_KEY_ENROLLED",
            "reader_public_hex": public_hex, "reader_fingerprint": "test"}), encoding="utf-8")
        return private, enrollment


def _sign(record: dict, private) -> dict:
    payload = canonical_json({k: record.get(k) for k in adjudication.PAYLOAD_FIELDS}).encode("utf-8")
    return {"alg": "ed25519", "reader_id": record["reader_id"],
            "payload_sha256": sha256_text(payload.decode("utf-8")),
            "signature_hex": private.sign(payload).hex()}


if __name__ == "__main__":
    unittest.main()
