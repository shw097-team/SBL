"""M02 -- resume keeps the role binding: the persisted binding SURVIVES a resume.

Acceptance matrix row M02, whose declared scope is the *full repaired runtime path, not a helper
alone*. A resume is modelled the only honest way: a NEW interpreter/process that re-opens the SAME
spine file and the SAME session/workorder from disk -- never an in-memory object left over from the
seeding phase.

What is proven here, end to end:

1. ``role_binding.find_session_binding(spine, SESSION)`` in the RESUMED process returns the same
   ``workorder`` and the same ``binding_digest`` the PRE-resume process computed (the two facts are
   handed across the process boundary as bytes on disk, in ``facts.json``).
2. The REAL ``scripts/hgk-lane-dispatch.py`` subprocess (the same shape as ``DispatcherPreSpawn`` /
   M07a) dispatched IN the resumed process still forces the persisted arm: ``required_arm`` and
   ``role_binding_served_arm`` both equal the binding's arm, exit 0, one spawn.
3. NEGATIVE controls on the same fixture shape: a resume whose binding was altered in between
   (arm / round / session) is refused with ITS OWN typed code, so 1 and 2 cannot pass merely
   because "nothing was checked".

Behavioural only: real code, real subprocesses, assertions on exit codes / typed codes / digests /
bytes. No production helper is imported-and-patched and no source text is asserted.

Claim ceiling: binding retention is proven across a fresh process re-opening the same spine on THIS
host. It does not prove retention across a host reboot, a Hermes profile swap, or a spine migration.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRATCH_ROOT = pathlib.Path("C:/Projects/Agent_Workspace/TEST_RESULTS")
# The interpreter the existing dispatcher tests use (the hermes-agent venv), NOT this runner's own.
HGK_PY = pathlib.Path(
    r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/"
    r"hermes-agent/venv/Scripts/python.exe"
)
POOL = ROOT / "config" / "lane-route-slots.candidate.json"
DISPATCHER = ROOT / "scripts" / "hgk-lane-dispatch.py"
STUB = ROOT / "tests" / "fixtures" / "stub_lane_child.py"

sys.path.insert(0, str(ROOT / "src"))
from hg_kseos import role_binding  # noqa: E402
from hg_kseos.spine import SharedSpine  # noqa: E402

REQ = "REQ-M02"
TASKSPEC = "TS-M02"
WO = "WO-M02-RESUME-20261023"
ROUND = "W2-MATRIX-CLOSURE-20261023"
SESSION = "20261023_120000_m02resume"
BASE = "903e47cddeceb40cb8f5f5793105533b3988a463"
SUBJECT = "hgk/tests/test_matrix_m02_resume.py"
EXPIRY = "2099-01-01T00:00:00+00:00"

# The RESUMED process: a separate interpreter that re-opens the spine path from disk, re-derives the
# session binding, and re-validates the persisted document against the facts the PRE-resume process
# wrote to disk. A typed refusal is reported as a code, never raised into the test runner.
RESUME_PROBE = r"""
import json, os, sys
from pathlib import Path

sys.path.insert(0, os.environ["HGK_SRC"])
from hg_kseos.spine import SharedSpine
from hg_kseos import role_binding

facts = json.loads(Path(os.environ["HGK_FACTS"]).read_text(encoding="utf-8"))
spine = SharedSpine(Path(os.environ["HGK_SPINE"]))
out = {"session": facts["session"], "found": False, "same_workorder": False, "same_digest": False,
       "same_arm": False, "refusals": {}}

found = role_binding.find_session_binding(spine, facts["session"])
out["found"] = found is not None
if found is not None:
    doc = found["binding"]
    arm = role_binding.resolve_arm(doc, "EXECUTE")
    out["workorder"] = found["workorder"]
    out["digest"] = role_binding.binding_digest(doc)
    out["arm"] = arm["arm"]
    out["rank"] = arm["rank"]
    out["same_workorder"] = str(found["workorder"]) == str(facts["workorder"])
    out["same_digest"] = out["digest"] == facts["digest"]
    out["same_arm"] = arm["arm"] == facts["arm"]

canonical = role_binding.load_canonical_binding(spine, facts["workorder"])
out["canonical_digest"] = canonical["binding_digest"]
for field, claims in (("session", {"session": facts["session"]}),
                      ("round", {"round": facts["round"]}),
                      ("model", {"model": facts["model"]})):
    try:
        role_binding.validate_binding(canonical["binding"], lane="EXECUTE", **claims)
        out["refusals"][field] = None
    except role_binding.BindingError as exc:
        out["refusals"][field] = exc.code
print(json.dumps(out, sort_keys=True))
"""


def _mandate_digest() -> str:
    return "sha256:" + hashlib.sha256(b"m02-mandate").hexdigest()


def _execute_arms() -> list[dict]:
    """The EXECUTE deployment plane, read from the pool artifact as a test INPUT.

    Rank 1 is today's default; rank 2 supplies a genuinely different arm for the negative control,
    so the fixture follows a re-bind instead of pinning a model name that the pool may retire.
    """
    doc = json.loads(POOL.read_text(encoding="utf-8"))
    lane = next(entry for entry in doc["lanes"] if entry.get("lane") == "EXECUTE")
    arms = []
    for entry in lane["ordered_pool"]:
        if not isinstance(entry, dict):
            continue
        arms.append({"rank": int(entry["rank"]), "provider": str(entry["provider"]),
                     "model": str(entry["model"]),
                     "default": bool(entry.get("default")),
                     "arm": f"{entry['provider']}/{entry['model']}"})
    if len(arms) < 2:
        raise AssertionError(f"the EXECUTE pool must carry at least two arms, got {arms!r}")
    return arms


def _non_default_arm(arms: list[dict]) -> dict:
    """An arm that is NOT the pool's own default.

    This is what keeps the positive case from being VACUOUS: if the fixture bound the pool default,
    ``required_arm == binding arm`` would hold even for a dispatcher that never consulted the
    persisted binding at all. Binding a non-default arm makes the equality prove that the binding
    really drove the selection (it had to move the run OFF the default).
    """
    for arm in arms:
        if not arm["default"]:
            return arm
    raise AssertionError(f"the EXECUTE pool declares no non-default arm: {arms!r}")


def _binding(arm: dict, *, deliverable: dict | None, **over) -> dict:
    doc = {
        "schema": role_binding.ROLE_BINDING_SCHEMA,
        "round": ROUND,
        "session": SESSION,
        "workorder": WO,
        "base_head": BASE,
        "subject": SUBJECT,
        "scope": [SUBJECT],
        "expiry": EXPIRY,
        "mandate_digest": _mandate_digest(),
        "roles": {
            "EXECUTE": {"provider": arm["provider"], "model": arm["model"],
                        "surface": "codex-cli", "rank": arm["rank"]},
            "VERIFY_SECURITY": {"provider": arm["provider"], "model": arm["model"],
                                "surface": "codex-cli", "rank": arm["rank"]},
        },
    }
    if deliverable is not None:
        doc["deliverable"] = deliverable
    doc.update(over)
    return doc


class ResumeFixture(unittest.TestCase):
    """Seed a temp spine under TEST_RESULTS, read the PRE-resume facts, resume elsewhere."""

    def setUp(self):
        SCRATCH_ROOT.mkdir(parents=True, exist_ok=True)
        self.tmp = pathlib.Path(tempfile.mkdtemp(prefix=f"hgk-m02-{self.__class__.__name__}-",
                                                 dir=str(SCRATCH_ROOT)))
        self.db = self.tmp / "spine.db"
        self.arms = _execute_arms()
        self.arm = self.arms[0]
        payload = b"M02 deliverable that really landed on disk\n"
        (self.tmp / "deliverable.py").write_bytes(payload)
        self.deliverable = {"path": "deliverable.py",
                            "sha256": hashlib.sha256(payload).hexdigest()}

    def _seed(self, binding: dict) -> None:
        """FROZEN requirement -> TaskSpec carrying ROLE_BINDING_KEY -> admitted WorkOrder."""
        spine = SharedSpine(self.db)
        spine.initialize()
        spine.create_project()
        spine.register_requirement(REQ, "src#m02", "resume binding retention", "ACC-M02",
                                   "oracle", "t", "neg")
        spine.acquire_lease(REQ, "maker", "tok")
        spine.transition_requirement(REQ, "FROZEN", "maker", "tok", 0, "E1", "K1")
        spine.create_taskspec(TASKSPEC, REQ, "do", "maker", self.tmp,
                              {role_binding.ROLE_BINDING_KEY: binding}, ["unit"], "evidence")
        spine.create_workorder(WO, TASKSPEC, "writer-m02", self.tmp, BASE)

    def _pre_resume_facts(self, binding: dict) -> dict:
        """The PRE-resume process: read the persisted document back off disk, record the facts."""
        spine = SharedSpine(self.db)
        canonical = role_binding.load_canonical_binding(spine, WO)
        found = role_binding.find_session_binding(spine, binding["session"])
        arm = role_binding.resolve_arm(canonical["binding"], "EXECUTE")
        facts = {"workorder": canonical["workorder"], "digest": canonical["binding_digest"],
                 "arm": arm["arm"], "rank": arm["rank"], "model": arm["model"],
                 "session": binding["session"], "round": binding["round"],
                 "subject": binding["subject"]}
        if found is not None:
            facts["session_workorder"] = found["workorder"]
            facts["session_digest"] = role_binding.binding_digest(found["binding"])
        else:
            facts["session_workorder"] = None
            facts["session_digest"] = None
        (self.tmp / "facts.json").write_text(json.dumps(facts, sort_keys=True), encoding="utf-8")
        (self.tmp / "binding.json").write_text(json.dumps(binding), encoding="utf-8")
        return facts

    def _resume_probe(self) -> dict:
        """The RESUMED process: a brand-new interpreter re-opening the spine path from disk."""
        env = dict(os.environ)
        env["HGK_SRC"] = str(ROOT / "src")
        env["HGK_SPINE"] = str(self.db)
        env["HGK_FACTS"] = str(self.tmp / "facts.json")
        proc = subprocess.run([str(HGK_PY), "-c", RESUME_PROBE], capture_output=True, text=True,
                              encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL,
                              timeout=120, cwd=str(ROOT), env=env)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        return json.loads(proc.stdout.strip().splitlines()[-1])

    def _dispatch(self, extra: list[str]) -> subprocess.CompletedProcess:
        env = dict(os.environ)
        env["HGK_SPINE_DB"] = str(self.db)
        env["HGK_STUB_MODE"] = "clean"
        env["HGK_STUB_USAGE"] = str(self.tmp / "usage.jsonl")
        env["HGK_STUB_USAGE_LINE"] = json.dumps(
            {"provider": self.arm["provider"], "model": self.arm["model"], "status": 200})
        cmd = [str(HGK_PY), str(DISPATCHER), "--lane", "EXECUTE", "--prompt", "M02 resume case",
               "--workorder", WO, "--json-out", str(self.tmp / "receipt.json"),
               "--codex-executable", str(STUB), "--usage", str(self.tmp / "usage.jsonl"),
               "--cwd", str(self.tmp), "--relay-home", str(self.tmp / "no-such-relay-home")] + extra
        return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", stdin=subprocess.DEVNULL, timeout=180,
                              cwd=str(ROOT), env=env)

    def _receipt(self) -> dict:
        return json.loads((self.tmp / "receipt.json").read_text(encoding="utf-8"))

    def _ledger_rows(self) -> int:
        path = self.tmp / "usage.jsonl"
        if not path.is_file():
            return 0
        return len([ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()])

    def _alter_persisted_binding(self, binding: dict) -> None:
        """Model an operator edit of the persisted row BETWEEN the two processes.

        A fixture mutation under TEST_RESULTS on a throwaway spine: it deliberately writes the row
        directly instead of using the typed transition API, because the point of the control is that
        the RESUMED process must re-read whatever bytes are now on disk.
        """
        spine = SharedSpine(self.db)
        with spine.transaction() as connection:
            row = connection.execute(
                "SELECT permissions_json FROM taskspecs WHERE taskspec_id=?", (TASKSPEC,)).fetchone()
            permissions = json.loads(row["permissions_json"])
            permissions[role_binding.ROLE_BINDING_KEY] = binding
            connection.execute("UPDATE taskspecs SET permissions_json=? WHERE taskspec_id=?",
                               (json.dumps(permissions, sort_keys=True), TASKSPEC))


class M02ResumeRetention(ResumeFixture):
    """Positive: the binding and the forced arm both survive a fresh process re-opening the spine."""

    def test_resume_keeps_the_same_binding_and_forces_the_same_arm(self):
        # Bind a NON-DEFAULT arm: the pool default would make arm equality vacuous, because a
        # dispatcher that ignored the persisted binding would still land on the same arm.
        bound = _non_default_arm(self.arms)
        self.arm = bound
        binding = _binding(bound, deliverable=self.deliverable)
        self._seed(binding)
        facts = self._pre_resume_facts(binding)
        self.assertNotEqual(facts["arm"], next(a["arm"] for a in self.arms if a["default"]))

        # (1) the resumed process re-derives the SAME workorder + digest from the file on disk
        resumed = self._resume_probe()
        self.assertTrue(resumed["found"], resumed)
        self.assertTrue(resumed["same_workorder"], resumed)
        self.assertTrue(resumed["same_digest"], resumed)
        self.assertTrue(resumed["same_arm"], resumed)
        self.assertEqual(resumed["workorder"], facts["workorder"])
        self.assertEqual(resumed["digest"], facts["digest"])
        self.assertEqual(resumed["canonical_digest"], facts["digest"])
        self.assertEqual(resumed["workorder"], facts["session_workorder"])
        self.assertEqual(resumed["digest"], facts["session_digest"])
        self.assertIsNone(resumed["refusals"]["session"], resumed)
        self.assertIsNone(resumed["refusals"]["round"], resumed)
        self.assertIsNone(resumed["refusals"]["model"], resumed)

        # (2) the REAL dispatcher, run as its own process in the resumed round, forces the arm the
        #     persisted binding names -- no --require-arm passed, so it is DERIVED, not echoed back.
        proc = self._dispatch(["--role-binding-file", str(self.tmp / "binding.json")])
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        receipt = self._receipt()
        self.assertTrue(receipt["ok"], receipt)
        self.assertEqual(receipt["served_arm"], facts["arm"])
        self.assertEqual(receipt["required_arm"], facts["arm"])
        self.assertEqual(receipt["role_binding_served_arm"], facts["arm"])
        self.assertEqual(receipt["binding_forced_rank"], facts["rank"])
        self.assertEqual(receipt["role_binding"]["role_binding_digest"], facts["digest"])
        self.assertEqual(receipt["role_binding"]["role_binding_source"], "canonical-spine")
        self.assertEqual(receipt["session"], SESSION)
        self.assertEqual(receipt["round"], ROUND)
        self.assertEqual(receipt["subject"], SUBJECT)
        # exactly one spawn: one real attempt and one usage row in the scratch ledger
        self.assertEqual(len(receipt["attempts"]), 1, receipt["attempts"])
        self.assertFalse(any(a.get("injected") for a in receipt["attempts"]))
        self.assertEqual(self._ledger_rows(), 1)


class M02ResumeRefusesAnAlteredBinding(ResumeFixture):
    """Negative controls: a resume after the persisted binding changed is refused, typed, no spawn."""

    def test_altered_arm_refuses_with_arm_mismatch(self):
        """The resuming caller still requires the arm it recorded; the row now names another arm."""
        seeded = _binding(self.arm, deliverable=self.deliverable)
        self._seed(seeded)
        facts = self._pre_resume_facts(seeded)
        self.assertNotEqual(self.arms[1]["arm"], facts["arm"])
        self._alter_persisted_binding(_binding(self.arms[1], deliverable=self.deliverable))
        self.assertEqual(self._ledger_rows(), 0)

        # No projection file is handed in, so the PERSISTED row is the only authority and the
        # refusal that fires is the arm contradiction itself -- not a stale-file mismatch.
        proc = self._dispatch(["--require-arm", facts["arm"]])
        self.assertEqual(proc.returncode, 4, proc.stdout + proc.stderr)
        receipt = self._receipt()
        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["code"], "ERR_ROLE_BINDING_ARM_MISMATCH")
        self.assertIn(self.arms[1]["arm"], json.dumps(receipt))
        # refused before any spawn: no usage row was appended and no attempt dir was created
        self.assertEqual(self._ledger_rows(), 0)
        self.assertFalse((self.tmp / "receipt.json.logs").exists())

    def test_altered_round_refuses_with_round_mismatch(self):
        seeded = _binding(self.arm, deliverable=self.deliverable)
        self._seed(seeded)
        self._pre_resume_facts(seeded)
        self._alter_persisted_binding(
            _binding(self.arm, deliverable=self.deliverable, round="OTHER-ROUND-20261023"))
        self.assertEqual(self._ledger_rows(), 0)

        proc = self._dispatch(["--round", ROUND, "--output-root", str(self.tmp / "out")])
        self.assertEqual(proc.returncode, 4, proc.stdout + proc.stderr)
        receipt = self._receipt()
        self.assertFalse(receipt["ok"])
        self.assertEqual(receipt["code"], "ERR_ROLE_BINDING_ROUND_MISMATCH")
        self.assertEqual(self._ledger_rows(), 0)
        # refused while resolving the binding, so no derived attempt dir was ever created
        self.assertFalse((self.tmp / "out").exists())

    def test_altered_session_no_longer_resolves_the_old_binding(self):
        seeded = _binding(self.arm, deliverable=self.deliverable)
        self._seed(seeded)
        facts = self._pre_resume_facts(seeded)
        self._alter_persisted_binding(
            _binding(self.arm, deliverable=self.deliverable, session="20261023_999999_other"))

        resumed = self._resume_probe()
        # the old session no longer resolves to this workorder ...
        self.assertFalse(resumed["found"], resumed)
        self.assertFalse(resumed["same_digest"], resumed)
        # ... and re-validating the persisted row against the resumed session is a typed refusal
        self.assertEqual(resumed["refusals"]["session"], "ERR_ROLE_BINDING_SESSION_MISMATCH")
        self.assertNotEqual(resumed["canonical_digest"], facts["digest"])
        self.assertEqual(self._ledger_rows(), 0)


if __name__ == "__main__":
    unittest.main()
