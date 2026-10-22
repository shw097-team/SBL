"""Commander-SP identity on the PLAN lane (R13 follow-through, deviation D-06, PLAN half).

The sibling card wired (and tested) the challenge/VERIFY pre-spawn half of D-06; the dispatcher
gate and `scripts/hgk_sp_identity.py` are generic over the identity name, and the registry binds
`commander` to the PLAN lane. This file is the PLAN-half matrix, and each test names the defect it
would otherwise allow:

  P-1  a Commander-SP could be dispatched as an EXECUTE writer (the build principal signing its own
       build) or as the VERIFY checker — the registry binding must refuse both before any spawn
  P-2  a Challenge-tagged invocation id could ride a commander dispatch (identity/tag confusion), so
       the receipt would name an SP that never ran
  P-3  the PLAN pre-handoff could be produced without the child ever receiving the identity block,
       while the receipt still read as identity-carrying
  P-4  the chain join on a PLAN dispatch could carry caller-chosen text instead of spine ids, so the
       "pre-handoff binds the R13 chain" claim would rest on the prompt author
  P-5  a legacy PLAN dispatch (no SP flags) could start reporting an identity it never resolved

All deterministic, NO model in the loop: stub child, fixture pool, fixture spine, fixture skills
root. The fixture helpers are deliberately self-contained (a small copy of the sibling card's
fixtures) rather than imported: two concurrently-running cards coupling through one uncommitted
test file would let either card's edit break the other's suite. Each refusal is built from the
positive command with exactly one argument changed, so it proves the tested condition rather than
some earlier gate (AGENTS.md rule 6).
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


disp = _load("hgk_lane_dispatch_plan", ROOT / "scripts" / "hgk-lane-dispatch.py")
spid = _load("hgk_sp_identity_plan", ROOT / "scripts" / "hgk_sp_identity.py")

REAL_POOL = ROOT / "config" / "lane-route-slots.candidate.json"
STUB_ECHO = ROOT / "tests" / "fixtures" / "stub_lane_child_echo_prompt.py"
STUB_PLAIN = ROOT / "tests" / "fixtures" / "stub_lane_child.py"
ARM = {"rank": 1, "provider": "opencode-go", "model": "deepseek-v4.1-flash",
       "transport_model": "opencode-go/deepseek-v4.1-flash",
       "identity_requirement": "none", "feasibility": "DISPATCHABLE"}
SPINE_PROSE = "PROSE-FROM-THE-SPINE-THAT-MUST-NOT-REACH-A-PROMPT"
WO, TS = "WO-R13F-01", "TS-R13F-01"


def _skills_root(tmp, *, empty=False) -> pathlib.Path:
    root = pathlib.Path(tmp) / "skills"
    for name in ("commander-sp", "external-challenge-sp"):
        d = root / name
        d.mkdir(parents=True, exist_ok=True)
        if empty:
            (d / "SKILL.md").write_text("", encoding="utf-8")
        else:
            (d / "SKILL.md").write_text(f"{name} PROCEDURE FIXTURE v1\nbounded proposal, no ECP\n",
                                        encoding="utf-8")
    return root


def _pool(tmp) -> pathlib.Path:
    doc = json.loads(REAL_POOL.read_text(encoding="utf-8"))
    for ln in doc["lanes"]:
        if ln["lane"] == "PLAN":
            ln["ordered_pool"] = [dict(ARM)]
    p = pathlib.Path(tmp) / "pool-PLAN.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return p


def _spine(tmp) -> pathlib.Path:
    """A spine-shaped fixture carrying a role binding, so the join has a digest to echo."""
    p = pathlib.Path(tmp) / "spine.db"
    con = sqlite3.connect(p)
    con.executescript(
        "CREATE TABLE workorders (workorder_id TEXT PRIMARY KEY, taskspec_id TEXT, state TEXT,"
        " base_head TEXT, writer TEXT, rollback_pointer TEXT);"
        "CREATE TABLE taskspecs (taskspec_id TEXT PRIMARY KEY, requirement_id TEXT, state TEXT,"
        " objective TEXT, permissions_json TEXT);")
    con.execute("INSERT INTO taskspecs VALUES (?,?,?,?,?)",
                (TS, "REQ-R13F-PLAN", "ADMITTED", SPINE_PROSE,
                 json.dumps({"role_binding": {"schema": "HGK-ROLE-BINDING/1", "workorder": WO}})))
    con.execute("INSERT INTO workorders VALUES (?,?,?,?,?,?)",
                (WO, TS, "VERIFIED", "c" * 40, "codex", "RB-WO-R13F-01"))
    con.commit()
    con.close()
    return p


def _env(tmp) -> dict:
    env = dict(os.environ)
    env["HGK_STUB_MODE"] = "clean"
    env["HGK_STUB_USAGE"] = str(pathlib.Path(tmp) / "usage.jsonl")
    env["HGK_STUB_USAGE_LINE"] = json.dumps(
        {"provider": "opencode-go", "model": "deepseek-v4.1-flash", "status": 200})
    env["HGK_STUB_PROMPT_OUT"] = str(pathlib.Path(tmp) / "child_prompt.txt")
    env.pop("HGK_STUB_EMIT_NONCE", None)
    return env


def _cmd(tmp, *, sp="commander", invocation=None, nonce=None, workorder=None,
         skills=None, spine=None, stub=STUB_ECHO, prompt="bounded plan pre-handoff", extra=()):
    tmp = pathlib.Path(tmp)
    cmd = [sys.executable, str(ROOT / "scripts" / "hgk-lane-dispatch.py"),
           "--lane", "PLAN", "--prompt", prompt,
           "--pool", str(_pool(tmp)),
           "--codex-executable", str(stub),
           "--usage", str(tmp / "usage.jsonl"),
           "--attempt-log-dir", str(tmp / "logs"),
           "--json-out", str(tmp / "receipt.json"),
           "--relay-home", str(tmp / "no-such-relay-home"),
           "--timeout", "60"]
    if sp:
        cmd += ["--sp-identity", sp]
    if invocation:
        cmd += ["--sp-invocation-id", invocation]
    if nonce:
        cmd += ["--nonce", nonce]
    if workorder:
        cmd += ["--sp-workorder", workorder]
    if skills:
        cmd += ["--sp-skills-root", str(skills)]
    if spine:
        cmd += ["--sp-spine", str(spine)]
    cmd += list(extra)
    return cmd


def _run(cmd, *, tmp, timeout=120):
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       stdin=subprocess.DEVNULL, timeout=timeout, cwd=str(ROOT), env=_env(tmp))
    rec_path = pathlib.Path(tmp) / "receipt.json"
    rec = json.loads(rec_path.read_text(encoding="utf-8")) if rec_path.is_file() else None
    return p, rec, pathlib.Path(tmp)


class CommanderRegistry(unittest.TestCase):
    """Unit level: what the registry authorises for the PLAN half."""

    def test_P1_commander_is_bound_to_PLAN(self):
        self.assertEqual(spid.REGISTRY["commander"]["lane"], "PLAN")
        self.assertEqual(spid.REGISTRY["commander"]["sp_id"], "SBL-COMMANDER-SP")

    def test_P1_commander_as_writer_or_checker_is_refused(self):
        """The build principal must never be the writer it bounds nor the checker that judges it."""
        for lane in ("EXECUTE", "VERIFY_SECURITY"):
            r = spid.resolve_identity("commander", lane=lane, nonce="n", invocation_id="n")
            self.assertFalse(r["ok"], lane)
            self.assertEqual(r["code"], spid.ERR_SP_IDENTITY_LANE_MISMATCH, lane)
            self.assertIn("PLAN", r["detail"], lane)

    def test_P2_a_challenge_tagged_id_is_refused_for_commander(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-tag-")
        skills = _skills_root(tmp)
        bad = "SPINV-CHALLENGE-0123456789ab"
        r = spid.resolve_identity("commander", skills_root=skills, lane="PLAN",
                                  nonce=bad, invocation_id=bad)
        self.assertFalse(r["ok"])
        self.assertEqual(r["code"], spid.ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED)
        self.assertIn("COMMANDER", r["detail"])

    def test_P4_chain_join_on_the_plan_side_carries_spine_ids_not_prose(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-join-")
        skills = _skills_root(tmp)
        spine = _spine(tmp)
        inv = spid.new_invocation_id("commander")
        r = spid.resolve_identity("commander", skills_root=skills, lane="PLAN", nonce=inv,
                                  invocation_id=inv, spine=spine, workorder=WO)
        self.assertTrue(r["ok"], r)
        chain = r["identity"]["chain"]
        self.assertEqual(chain["workorder_id"], WO)
        self.assertEqual(chain["taskspec_id"], TS)
        self.assertEqual(chain["base_head"], "c" * 40)
        self.assertTrue(chain["spine_binding_digest"].startswith("sha256:"))
        block = spid.build_block(r["identity"])
        self.assertIn(WO, block)
        self.assertIn("SPINV-COMMANDER-", block)
        self.assertNotIn(SPINE_PROSE, block, "free-form spine text must never reach a lane prompt")

    def test_resolution_pins_the_commander_procedure_bytes(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-pin-")
        skills = _skills_root(tmp)
        inv = spid.new_invocation_id("commander")
        r = spid.resolve_identity("commander", skills_root=skills, lane="PLAN", nonce=inv,
                                  invocation_id=inv)
        self.assertTrue(r["ok"], r)
        want = hashlib.sha256((skills / "commander-sp" / "SKILL.md").read_bytes()).hexdigest()
        self.assertEqual(r["identity"]["skill_sha256"], want)
        self.assertEqual(r["identity"]["skill_path"], str(skills / "commander-sp" / "SKILL.md"))
        self.assertFalse(r["identity"]["issued_permit"])
        self.assertFalse(r["identity"]["signed_acceptance"])


class PlanPreHandoffEndToEnd(unittest.TestCase):
    """The PLAN pre-handoff end-to-end: zero spawn on refusal, byte read-back on success."""

    def _positive(self, **kw):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-ok-")
        skills = _skills_root(tmp)
        spine = _spine(tmp)
        inv = spid.new_invocation_id("commander")
        cmd = _cmd(tmp, invocation=inv, nonce=inv, skills=skills, spine=spine, workorder=WO, **kw)
        return _run(cmd, tmp=tmp), inv, skills, pathlib.Path(tmp)

    def _refusal(self, *, expect_code, **kw):
        """Build the POSITIVE command and break exactly one thing."""
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-ref-")
        skills = _skills_root(tmp)
        spine = _spine(tmp)
        inv = spid.new_invocation_id("commander")
        overrides = dict(invocation=inv, nonce=inv, skills=skills, spine=spine, workorder=WO)
        overrides.update(kw)
        cmd = _cmd(tmp, **overrides)
        p, rec, t = _run(cmd, tmp=tmp)
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertIsNotNone(rec, "a refusal must write its own receipt")
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["code"], expect_code, p.stdout)
        self.assertNotIn("attempts", rec, "a pre-spawn refusal must record zero attempts")
        self.assertFalse((t / "logs").is_dir() and any((t / "logs").iterdir()),
                         "nothing may be spawned on refusal")
        return rec, t

    def test_P3_the_identity_block_reaches_the_child_and_the_join_is_observed(self):
        (p, rec, _t), inv, skills, tmp = self._positive()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(rec["ok"], rec.get("code"))
        ident = rec["sp_identity"]
        self.assertTrue(ident["ok"])
        self.assertEqual(ident["sp_id"], "SBL-COMMANDER-SP")
        self.assertEqual(ident["bound_lane"], "PLAN")
        self.assertTrue(ident["identity_block_injected_pre_spawn"])
        self.assertTrue(ident["invocation_id_echoed"])
        # READ-BACK: hash the bytes the child was actually handed and compare with the receipt.
        child_prompt = (tmp / "child_prompt.txt").read_text(encoding="utf-8")
        self.assertEqual(hashlib.sha256(child_prompt.encode("utf-8")).hexdigest(),
                         ident["prompt_sha256_after"])
        self.assertIn("=== HGK SP IDENTITY", child_prompt)
        self.assertIn(inv, child_prompt)
        self.assertIn(WO, child_prompt)
        self.assertIn("SBL-COMMANDER-SP", child_prompt)
        self.assertTrue(child_prompt.endswith("\n\nbounded plan pre-handoff"), child_prompt[-60:])
        self.assertEqual(ident["chain"]["workorder_id"], WO)
        self.assertFalse(ident["issued_permit"])
        self.assertFalse(ident["signed_acceptance"])

    def test_P1_commander_on_a_writer_lane_refuses_e2e(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-lane-")
        skills = _skills_root(tmp)
        inv = spid.new_invocation_id("commander")
        cmd = _cmd(tmp, extra=(), skills=skills)
        # the dispatcher validates --lane in-contract, so drive the mismatch at the gate seam by
        # dispatching the challenge identity's mirror: commander on VERIFY is the sibling's lane.
        cmd[cmd.index("--lane") + 1] = "VERIFY_SECURITY"
        cmd += ["--sp-invocation-id", inv, "--nonce", inv]
        p, rec, t = _run(cmd, tmp=tmp)
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertEqual(rec["code"], spid.ERR_SP_IDENTITY_LANE_MISMATCH)
        self.assertFalse((t / "logs").is_dir())

    def test_P2_challenge_tagged_invocation_id_refuses_e2e(self):
        self._refusal(expect_code=spid.ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED,
                      invocation="SPINV-CHALLENGE-0123456789ab",
                      nonce="SPINV-CHALLENGE-0123456789ab")

    def test_P3_nonce_that_is_not_the_invocation_id_refuses(self):
        self._refusal(expect_code=spid.ERR_SP_IDENTITY_NONCE_MISMATCH, nonce="HGK_LANE_NONCE_OK")

    def test_P3_child_that_never_echoes_the_id_is_not_ok_and_claims_no_join(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-silent-")
        skills = _skills_root(tmp)
        spine = _spine(tmp)
        inv = spid.new_invocation_id("commander")
        cmd = _cmd(tmp, invocation=inv, nonce=inv, skills=skills, spine=spine, workorder=WO,
                   stub=STUB_PLAIN)
        p, rec, _ = _run(cmd, tmp=tmp)
        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["code"], "ERR_NO_ARM_EMITTED_NONCE", p.stdout)
        self.assertTrue(rec["sp_identity"]["identity_block_injected_pre_spawn"])
        self.assertFalse(rec["sp_identity"]["invocation_id_echoed"])

    def test_P4_unknown_workorder_on_the_plan_join_refuses(self):
        self._refusal(expect_code=spid.ERR_SP_IDENTITY_WORKORDER_UNKNOWN, workorder="WO-NOPE")

    def test_P2_unusable_commander_procedure_refuses(self):
        missing = pathlib.Path(tempfile.mkdtemp(prefix="hgk-sp-plan-noskill-"))
        self._refusal(expect_code=spid.ERR_SP_IDENTITY_SKILL_UNUSABLE, skills=missing)

    def test_P5_legacy_plan_dispatch_reports_no_identity_at_all(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-legacy-")
        cmd = _cmd(tmp, sp=None, invocation=None, nonce=None, skills=None, spine=None,
                   workorder=None, stub=STUB_PLAIN)
        p, rec, _ = _run(cmd, tmp=tmp)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(rec["ok"], rec.get("code"))
        self.assertNotIn("sp_identity", rec)

    def test_identity_flags_without_identity_refuse_on_plan(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-plan-dangling-")
        cmd = _cmd(tmp, sp=None, invocation=None, nonce=None,
                   skills=_skills_root(tmp), spine=_spine(tmp), workorder=WO)
        p, rec, t = _run(cmd, tmp=tmp)
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertEqual(rec["code"], disp.ERR_SP_IDENTITY_FLAG_WITHOUT_IDENTITY)
        self.assertFalse((t / "logs").is_dir())


if __name__ == "__main__":
    unittest.main()
