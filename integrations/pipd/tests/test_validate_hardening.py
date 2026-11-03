"""Pins the validator hardening adopted at U04 C4 (digest binding + oracle polarity).

Question 1 (digest binding): is a record's content_hash RECOMPUTED from its body and compared,
so a body edited after sealing is refused?

Question 2 (oracle polarity): is a risk_guard.oracle.expected / acceptance_cue that contradicts
risk_guard.polarity refused, or is any string accepted?

Every record here is built through the real pipeline (intake -> compile_pi -> bind_pd ->
compile_ecp / compile_tqaep / compile_construction_contract) against a throwaway git repo, so
nothing is hand-faked. The POS cases prove the check does not fire on honest records; the NEG cases pin the two gaps
that were found during the C4 audit: (1) content_hash was only recomputed for the five
release-bound families, so an edited RequirementAtom/EvidenceExpectation/ClaimCeiling passed, and
(2) no invariant compared risk_guard.oracle.expected or acceptance_cue with risk_guard.polarity.
"""
from __future__ import annotations

import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # integrations/pipd
sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline, validate  # noqa: E402

SCHEMAS = ROOT / "schemas"

GOAL = ("The system must record an audit log for every release read. "
        "The system must not emit telemetry to third parties.")


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=str(cwd), check=True,
                   capture_output=True, text=True)


class Fixture:
    """Real records, built once through the public pipeline."""

    def __init__(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.repo = base / "repo"
        self.repo.mkdir()
        _git(self.repo, "init", "-q")
        _git(self.repo, "config", "user.email", "audit@example.invalid")
        _git(self.repo, "config", "user.name", "audit")
        (self.repo / "README.md").write_text("audit fixture\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", "fixture")

        # The clause source is the FILE: an atom is bound to the text it was compiled from.
        self.source = self.repo / "REQUIREMENTS.md"
        self.source.write_text(GOAL + "\n", encoding="utf-8")
        _git(self.repo, "add", "-A")
        _git(self.repo, "commit", "-q", "-m", "clauses")

        self.card = pipeline.intake(GOAL, sources=[str(self.source)])
        if len(self.card["atoms"]) < 2:
            raise RuntimeError(f"fixture needs a MUST and a MUST NOT atom, got {len(self.card['atoms'])}")
        self.pi = pipeline.compile_pi(self.card)
        self.pd = pipeline.bind_pd(self.pi, {"root": str(self.repo), "writable_scope": "src/**"})
        self.ecp = pipeline.compile_ecp(self.pd, self.pi)
        self.tqaep = pipeline.compile_tqaep(self.pi, self.ecp, maker="maker-a", checker="checker-b",
                                            checker_execution_receipt="receipt-checker-b-001")
        self.cc = pipeline.compile_construction_contract(self.pd)

    def bundle(self) -> dict:
        return {"PI-PKG": copy.deepcopy(self.pi), "PD-PKG": copy.deepcopy(self.pd),
                "ECP": copy.deepcopy(self.ecp), "TQAEP": copy.deepcopy(self.tqaep),
                "ConstructionContract": copy.deepcopy(self.cc)}

    def atom(self, index: int = 0) -> dict:
        return copy.deepcopy(pipeline.atoms_of(self.pi)[index])

    def close(self) -> None:
        self._tmp.cleanup()


_FIX: Fixture | None = None


def setUpModule() -> None:
    global _FIX
    _FIX = Fixture()


def tearDownModule() -> None:
    if _FIX:
        _FIX.close()


def _findings(contract: str, record: dict) -> list[str]:
    return validate.validate_record(contract, record, SCHEMAS) + \
        validate.semantic_invariants(contract, record)


def _bundle_findings(bundle: dict) -> list[dict]:
    return validate.validate_bundle(bundle, SCHEMAS)["findings"]


def _digest_ok(record: dict) -> None:
    """Re-issue just the content hash so a NEG case is about SEMANTICS, not the digest."""
    record["content_hash"] = validate._body_hash(record)


def _remint_pi_with_atom(pi: dict, index: int, mutate) -> dict:
    """Produce a PI whose mutated atom is CONSISTENTLY re-minted (digest + trace all valid)."""
    out = copy.deepcopy(pi)
    atom = out["stable_semantic_contract"]["atoms"][index]
    mutate(atom)
    pipeline._seal(atom, "ATOM")
    pipeline._seal(out, "PI")           # body (incl. the atom) re-hashed first
    out["trace"] = [pipeline._rec("TraceLink", "TL",
                                  {"f": out["subject_id"], "t": a["subject_id"]},
                                  from_type="PI-PKG", from_id=out["subject_id"],
                                  from_hash=out["content_hash"],
                                  to_type="RequirementAtom", to_id=a["subject_id"],
                                  to_hash=a["content_hash"],
                                  rationale="PI derives this atom from the frozen intent")
                    for a in out["stable_semantic_contract"]["atoms"]]
    return out


# ------------------------------------------------------------------ POS control
class PosControl(unittest.TestCase):
    def test_pos_pipeline_records_validate_clean(self):
        self.assertEqual(_findings("PI-PKG", _FIX.pi), [])
        self.assertEqual(_findings("PD-PKG", _FIX.pd), [])
        self.assertEqual(_findings("ECP", _FIX.ecp), [])
        self.assertEqual(_findings("TQAEP", _FIX.tqaep), [])
        self.assertEqual(_findings("ConstructionContract", _FIX.cc), [])
        self.assertEqual(_findings("RequirementAtom", _FIX.atom(0)), [])

    def test_pos_bundle_passes_with_full_closure(self):
        out = validate.validate_bundle(_FIX.bundle(), SCHEMAS)
        self.assertEqual(out["verdict"], "PASS", out["findings"])
        self.assertEqual(out["closure"], "FULL")

    def test_pos_resealing_an_untouched_record_stays_valid(self):
        for name, rec in (("PI-PKG", _FIX.pi), ("PD-PKG", _FIX.pd), ("ECP", _FIX.ecp),
                          ("TQAEP", _FIX.tqaep), ("ConstructionContract", _FIX.cc)):
            clone = copy.deepcopy(rec)
            _digest_ok(clone)
            self.assertEqual(_findings(name, clone), [], name)


# ------------------------------------------------------- Q1: digest binding
class DigestBindingNeg(unittest.TestCase):
    """A body edited AFTER sealing must be refused. All of these keep the stale content_hash."""

    CASES = {
        "PI-PKG": ("acceptance", lambda r: r["acceptance"].__setitem__("mode", "unbound")),
        "PD-PKG": ("currentness", lambda r: r["currentness"].__setitem__("state", "STALE")),
        "ECP": ("effect_intent", lambda r: r.__setitem__("effect_intent", "delete the repo")),
        "TQAEP": ("oracles", lambda r: r["oracles"].__setitem__(0, "always true")),
        "ConstructionContract": ("rollback", lambda r: r.__setitem__("rollback", "none")),
    }

    def test_neg_release_bound_body_mutation_is_refused(self):
        for name, (field, mutate) in self.CASES.items():
            with self.subTest(family=name, field=field):
                rec = copy.deepcopy(getattr(_FIX, {"PI-PKG": "pi", "PD-PKG": "pd", "ECP": "ecp",
                                                   "TQAEP": "tqaep",
                                                   "ConstructionContract": "cc"}[name]))
                before = rec["content_hash"]
                mutate(rec)
                self.assertNotEqual(validate._body_hash(rec), before, "mutation must change the body")
                found = [f for f in _findings(name, rec) if "content_hash does not match" in f]
                self.assertTrue(found, f"{name}: body mutation after sealing was NOT refused: "
                                       f"{_findings(name, rec)}")

    def test_neg_atom_body_mutation_is_refused(self):
        """RequirementAtom is NOT in RELEASE_BOUND: is its digest checked at all?"""
        atom = _FIX.atom(0)
        atom["acceptance_cue"] = "MUST NOT: the system silently skips the audit log"
        found = _findings("RequirementAtom", atom)
        self.assertTrue(any("content_hash does not match" in f for f in found),
                        f"RequirementAtom: body mutation after sealing was NOT refused: {found}")

    def test_neg_bundle_refuses_atom_mutation(self):
        atom = _FIX.atom(0)
        atom["owner"] = "someone-else"
        out = validate.validate_bundle({"RequirementAtom": atom}, SCHEMAS)
        self.assertEqual(out["verdict"], "FAIL", out)

    def test_neg_non_release_bound_families_have_no_digest_check(self):
        """The gate is `contract in RELEASE_BOUND`, so the other 14 families are unchecked."""
        atom = _FIX.atom(0)
        atom["owner"] = "someone-else"                      # schema-valid, body changed
        ee = pipeline.evidence_expectations(_FIX.tqaep, "producer-a")[0]
        ee["postcondition"] = "the oracle was never evaluated"
        ccl = pipeline.claim_ceiling(["LOCAL_QUALIFIED"])
        ccl["allowed_claims"] = ["PROMPT_COMPILE_PASS"]     # still a declared, non-forbidden claim
        cases = {"RequirementAtom": atom, "EvidenceExpectation": ee, "ClaimCeiling": ccl}
        for contract, rec in cases.items():
            with self.subTest(family=contract):
                self.assertNotIn(contract, validate.RELEASE_BOUND)
                found = _findings(contract, rec)
                others = [f for f in found if "content_hash does not match" not in f]
                self.assertEqual(others, [], "the mutation must be invisible to every other check")
                self.assertTrue(any("content_hash does not match" in f for f in found),
                                f"{contract}: body mutation after sealing was NOT refused")
                self.assertEqual(validate.validate_bundle({contract: rec}, SCHEMAS)["verdict"],
                                 "FAIL", f"{contract}: bundle PASSed a mutated body")

    def test_neg_trace_hash_tamper_is_refused_in_bundle(self):
        bundle = _FIX.bundle()
        bundle["PI-PKG"]["trace"][0]["to_hash"] = "0" * 64
        out = validate.validate_bundle(bundle, SCHEMAS)
        self.assertEqual(out["verdict"], "FAIL", out)


# ---------------------------------------------------- Q2: oracle polarity
class OraclePolarityNeg(unittest.TestCase):
    """A polarity that contradicts its own oracle / cue must be refused."""

    def test_neg_must_with_forbidden_oracle_is_refused(self):
        atom = _FIX.atom(0)
        atom["risk_guard"]["polarity"] = "MUST"
        atom["risk_guard"]["oracle"]["expected"] = "forbidden"
        _digest_ok(atom)
        found = _findings("RequirementAtom", atom)
        self.assertTrue(any("polarity" in f for f in found),
                        f"MUST + expected=forbidden accepted: {found}")

    def test_neg_negation_atom_asserting_a_positive_predicate_is_refused(self):
        atom = _FIX.atom(1)
        atom["risk_guard"]["polarity"] = "MUST NOT"
        atom["risk_guard"]["oracle"]["expected"] = "required"
        atom["acceptance_cue"] = "MUST NOT: " + str(atom["acceptance_cue"]).split(": ", 1)[-1]
        _digest_ok(atom)
        found = _findings("RequirementAtom", atom)
        self.assertTrue(any("polarity" in f for f in found),
                        f"MUST NOT + expected=required accepted: {found}")

    def test_neg_undeclared_polarity_token_is_refused(self):
        for token in ("MAY", "SHOULD", "must", "MUST_NOT", "", None):
            with self.subTest(polarity=token):
                atom = _FIX.atom(0)
                atom["risk_guard"]["polarity"] = token
                _digest_ok(atom)
                found = _findings("RequirementAtom", atom)
                self.assertTrue(any("polarity" in f for f in found),
                                f"undeclared polarity {token!r} accepted: {found}")

    def test_neg_cue_prefix_disagreeing_with_polarity_is_refused(self):
        atom = _FIX.atom(1)                      # a MUST NOT atom
        head = str(atom["acceptance_cue"]).split(": ", 1)[-1]
        atom["acceptance_cue"] = f"MUST: {head}"
        _digest_ok(atom)
        found = _findings("RequirementAtom", atom)
        self.assertTrue(any("polarity" in f for f in found),
                        f"cue saying MUST on a MUST NOT atom accepted: {found}")

    def test_neg_bundle_refuses_polarity_flip_through_pi(self):
        """The minted-at-source route: a fully consistent (re-minted) PI carrying a flipped atom."""
        flipped = _remint_pi_with_atom(
            _FIX.pi, 0, lambda a: (a["risk_guard"].__setitem__("polarity", "MUST"),
                                   a["risk_guard"]["oracle"].__setitem__("expected", "forbidden")))
        out = validate.validate_bundle({"PI-PKG": flipped}, SCHEMAS)
        # The digest is NOT what refuses this: the PI was re-minted consistently on purpose.
        self.assertEqual([f for f in out["findings"] if "content_hash does not match" in f["detail"]],
                         [], "this case must be refused on polarity, not on the digest")
        self.assertTrue(any("polarity" in f.get("detail", "") for f in out["findings"]),
                        f"a PI whose atom has MUST + expected=forbidden passed validate_bundle: {out}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
