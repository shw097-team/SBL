"""Pre-spawn SP identity gate (R13 follow-through, deviation D-06).

R13 ran a real writer lane and a real checker lane, and recorded honestly that both were LANES and not
SP identities: nothing in the dispatch resolved, pinned or carried a Challenge-SP identity, so
"checker lane" and "Challenge-SP" were one thing under two names. These tests lock the adapter down
that separates them, and each one names the defect it would otherwise allow:

  I-1  an identity could be dispatched on a lane it is not bound to (challenge as an EXECUTE writer)
  I-2  an identity could be "present" while its procedure file was missing or empty (a name, not an
       identity) - i.e. a vacuous resolution
  I-3  the child could receive a prompt that never contained the identity, with the receipt still
       reading as if the identity had been delivered
  I-4  identity-shaped flags could be passed and silently ignored, so a receipt implied a join that
       was never attempted
  I-5  the chain join could carry caller-chosen text instead of ids read back from the spine
  I-6  a run whose child never echoed the invocation id could still be reported ok:true

All of these are DETERMINISTIC and spawn NO model: the child is the stub fixture, the pool is a
fixture, the spine is a fixture sqlite, and the skills root is a fixture directory. The refusal tests
are built from the POSITIVE command with exactly one argument changed, so each refusal proves the
tested condition rather than some earlier gate (AGENTS.md rule 6).
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


disp = _load("hgk_lane_dispatch", ROOT / "scripts" / "hgk-lane-dispatch.py")
spid = _load("hgk_sp_identity", ROOT / "scripts" / "hgk_sp_identity.py")

REAL_POOL = ROOT / "config" / "lane-route-slots.candidate.json"
STUB_ECHO = ROOT / "tests" / "fixtures" / "stub_lane_child_echo_prompt.py"
STUB_PLAIN = ROOT / "tests" / "fixtures" / "stub_lane_child.py"
ARM = {"rank": 1, "provider": "opencode-go", "model": "deepseek-v4.1-flash",
       "transport_model": "opencode-go/deepseek-v4.1-flash",
       "identity_requirement": "none", "feasibility": "DISPATCHABLE"}
SPINE_PROSE = "PROSE-FROM-THE-SPINE-THAT-MUST-NOT-REACH-A-PROMPT"


def _skills_root(tmp, *, empty=False) -> pathlib.Path:
    root = pathlib.Path(tmp) / "skills"
    for name in ("external-challenge-sp", "commander-sp"):
        d = root / name
        d.mkdir(parents=True, exist_ok=True)
        if empty:
            (d / "SKILL.md").write_text("", encoding="utf-8")
        else:
            (d / "SKILL.md").write_text(f"{name} PROCEDURE FIXTURE v1\nread-only, evidence-carrying\n",
                                        encoding="utf-8")
    return root


def _pool(tmp, lane: str) -> pathlib.Path:
    doc = json.loads(REAL_POOL.read_text(encoding="utf-8"))
    for ln in doc["lanes"]:
        if ln["lane"] == lane:
            ln["ordered_pool"] = [dict(ARM)]
    p = pathlib.Path(tmp) / f"pool-{lane}.json"
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    return p


def _spine(tmp, *, with_wo: bool = True) -> pathlib.Path:
    """A spine-shaped fixture: the columns read_chain() selects, and one WorkOrder with prose in the
    taskspec objective so a leak of that prose into the prompt is detectable."""
    p = pathlib.Path(tmp) / "spine.db"
    con = sqlite3.connect(p)
    con.executescript(
        "CREATE TABLE workorders (workorder_id TEXT PRIMARY KEY, taskspec_id TEXT, state TEXT,"
        " base_head TEXT, writer TEXT, rollback_pointer TEXT);"
        "CREATE TABLE taskspecs (taskspec_id TEXT PRIMARY KEY, requirement_id TEXT, state TEXT,"
        " objective TEXT, permissions_json TEXT);")
    if with_wo:
        con.execute("INSERT INTO taskspecs VALUES (?,?,?,?,?)",
                    ("TS-TEST-01", "REQ-TEST-PLAN", "ADMITTED", SPINE_PROSE,
                     json.dumps({"role_binding": {"schema": "HGK-ROLE-BINDING/1",
                                                  "workorder": "WO-TEST-01"}})))
        con.execute("INSERT INTO workorders VALUES (?,?,?,?,?,?)",
                    ("WO-TEST-01", "TS-TEST-01", "CREATED", "b" * 40, "codex", "RB-WO-TEST-01"))
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


def _cmd(tmp, *, lane="VERIFY_SECURITY", sp="challenge", invocation=None, nonce=None,
         workorder=None, skills=None, spine=None, stub=STUB_ECHO, prompt="x", extra=()):
    tmp = pathlib.Path(tmp)
    cmd = [sys.executable, str(ROOT / "scripts" / "hgk-lane-dispatch.py"),
           "--lane", lane, "--prompt", prompt,
           "--pool", str(_pool(tmp, lane)),
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


class RegistryAndResolution(unittest.TestCase):
    """Unit level: what the registry authorises and what resolve_identity() refuses."""

    def test_I1_identity_is_bound_to_exactly_one_lane(self):
        self.assertEqual(spid.REGISTRY["challenge"]["lane"], "VERIFY_SECURITY")
        self.assertEqual(spid.REGISTRY["commander"]["lane"], "PLAN")

    def test_I1_challenge_on_a_writer_lane_is_refused(self):
        r = spid.resolve_identity("challenge", lane="EXECUTE", nonce="n", invocation_id="n")
        self.assertFalse(r["ok"])
        self.assertEqual(r["code"], spid.ERR_SP_IDENTITY_LANE_MISMATCH)
        self.assertIn("VERIFY_SECURITY", r["detail"])

    def test_unknown_identity_is_typed_not_defaulted(self):
        r = spid.resolve_identity("definitely-not-an-sp", lane="VERIFY_SECURITY")
        self.assertFalse(r["ok"])
        self.assertEqual(r["code"], spid.ERR_SP_IDENTITY_UNKNOWN)

    def test_invocation_id_must_be_well_formed_and_name_this_identity(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-")
        skills = _skills_root(tmp)
        for bad in (None, "", "SPINV-CHALLENGE-short", "SPINV-NOPE-0123456789ab",
                    "SPINV-COMMANDER-0123456789ab"):
            r = spid.resolve_identity("challenge", skills_root=skills, lane="VERIFY_SECURITY",
                                      nonce=bad, invocation_id=bad)
            self.assertFalse(r["ok"], bad)
            self.assertEqual(r["code"], spid.ERR_SP_IDENTITY_INVOCATION_ID_MALFORMED, bad)

    def test_I3_nonce_must_be_the_invocation_id(self):
        """Without this binding the dispatcher's nonce oracle cannot certify the identity block, so a
        run could pass its nonce while the child never saw an identity at all."""
        tmp = tempfile.mkdtemp(prefix="hgk-sp-")
        skills = _skills_root(tmp)
        inv = spid.new_invocation_id("challenge")
        r = spid.resolve_identity("challenge", skills_root=skills, lane="VERIFY_SECURITY",
                                  nonce="HGK_LANE_NONCE_OK", invocation_id=inv)
        self.assertFalse(r["ok"])
        self.assertEqual(r["code"], spid.ERR_SP_IDENTITY_NONCE_MISMATCH)

    def test_I2_missing_and_empty_procedures_are_both_refused(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-")
        inv = spid.new_invocation_id("challenge")
        absent = pathlib.Path(tmp) / "no-such-root"
        r = spid.resolve_identity("challenge", skills_root=absent, lane="VERIFY_SECURITY",
                                  nonce=inv, invocation_id=inv)
        self.assertEqual(r["code"], spid.ERR_SP_IDENTITY_SKILL_UNUSABLE)
        empty = _skills_root(pathlib.Path(tmp) / "e", empty=True)
        r2 = spid.resolve_identity("challenge", skills_root=empty, lane="VERIFY_SECURITY",
                                   nonce=inv, invocation_id=inv)
        self.assertEqual(r2["code"], spid.ERR_SP_IDENTITY_SKILL_UNUSABLE)
        self.assertIn("empty", r2["detail"])

    def test_resolution_pins_the_procedure_bytes(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-")
        skills = _skills_root(tmp)
        inv = spid.new_invocation_id("challenge")
        r = spid.resolve_identity("challenge", skills_root=skills, lane="VERIFY_SECURITY",
                                  nonce=inv, invocation_id=inv)
        self.assertTrue(r["ok"], r)
        want = hashlib.sha256(
            (skills / "external-challenge-sp" / "SKILL.md").read_bytes()).hexdigest()
        self.assertEqual(r["identity"]["skill_sha256"], want)
        self.assertEqual(r["identity"]["claim_ceiling"], spid.CLAIM_CEILING)
        self.assertFalse(r["identity"]["issued_permit"])
        self.assertFalse(r["identity"]["signed_acceptance"])

    def test_I5_chain_join_carries_ids_read_from_the_spine_not_prose(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-")
        skills = _skills_root(tmp)
        spine = _spine(tmp)
        inv = spid.new_invocation_id("challenge")
        r = spid.resolve_identity("challenge", skills_root=skills, lane="VERIFY_SECURITY",
                                  nonce=inv, invocation_id=inv, spine=spine,
                                  workorder="WO-TEST-01")
        self.assertTrue(r["ok"], r)
        chain = r["identity"]["chain"]
        self.assertEqual(chain["workorder_id"], "WO-TEST-01")
        self.assertEqual(chain["taskspec_id"], "TS-TEST-01")
        self.assertEqual(chain["base_head"], "b" * 40)
        self.assertTrue(chain["spine_binding_digest"].startswith("sha256:"))
        block = spid.build_block(r["identity"])
        self.assertIn("WO-TEST-01", block)
        self.assertIn("SPINV-CHALLENGE-", block)
        self.assertNotIn(SPINE_PROSE, block, "free-form spine text must never reach a lane prompt")

    def test_I5_unknown_workorder_and_unreadable_spine_are_typed(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-")
        skills = _skills_root(tmp)
        inv = spid.new_invocation_id("challenge")
        r = spid.resolve_identity("challenge", skills_root=skills, lane="VERIFY_SECURITY",
                                  nonce=inv, invocation_id=inv,
                                  spine=_spine(tmp, with_wo=False), workorder="WO-NOPE")
        self.assertFalse(r["ok"])
        self.assertEqual(r["code"], spid.ERR_SP_IDENTITY_WORKORDER_UNKNOWN)
        r2 = spid.resolve_identity("challenge", skills_root=skills, lane="VERIFY_SECURITY",
                                   nonce=inv, invocation_id=inv,
                                   spine=pathlib.Path(tmp) / "absent.db", workorder="WO-TEST-01")
        self.assertFalse(r2["ok"])
        self.assertEqual(r2["code"], spid.ERR_SP_IDENTITY_CHAIN_UNAVAILABLE)


class PreSpawnGateEndToEnd(unittest.TestCase):
    """The gate end-to-end: zero spawn on refusal, read-back proof on success."""

    def _positive(self, *, sp="challenge", **kw):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-e2e-")
        skills = _skills_root(tmp)
        spine = _spine(tmp)
        inv = spid.new_invocation_id(sp)
        cmd = _cmd(tmp, sp=sp, invocation=inv, nonce=inv, skills=skills, spine=spine,
                   workorder="WO-TEST-01", **kw)
        return _run(cmd, tmp=tmp), inv, skills, spine, pathlib.Path(tmp)

    def _refusal(self, *, expect_code, **kw):
        """Build the POSITIVE command and break exactly one thing."""
        tmp = tempfile.mkdtemp(prefix="hgk-sp-ref-")
        skills = _skills_root(tmp)
        spine = _spine(tmp)
        inv = spid.new_invocation_id("challenge")
        overrides = dict(sp="challenge", invocation=inv, nonce=inv, skills=skills, spine=spine,
                         workorder="WO-TEST-01")
        overrides.update(kw)
        cmd = _cmd(tmp, **overrides)
        (p, rec, t) = _run(cmd, tmp=tmp)
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertIsNotNone(rec, "a refusal must write its own receipt")
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["code"], expect_code, p.stdout)
        self.assertNotIn("attempts", rec, "a pre-spawn refusal must record zero attempts")
        logs = t / "logs"
        self.assertFalse(logs.is_dir() and any(logs.iterdir()), "nothing may be spawned on refusal")
        return rec, t

    def test_I3_identity_block_is_injected_and_the_child_really_received_it(self):
        (p, rec, _t), inv, skills, spine, tmp = self._positive()
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(rec["ok"], rec.get("code"))
        ident = rec["sp_identity"]
        self.assertTrue(ident["ok"])
        self.assertEqual(ident["sp_id"], "SBL-ACCEPTANCE-CHALLENGE-SP")
        self.assertTrue(ident["identity_block_injected_pre_spawn"])
        self.assertTrue(ident["invocation_id_echoed"])
        # READ-BACK: hash the bytes the child was actually handed and compare with the receipt.
        child_prompt = (tmp / "child_prompt.txt").read_text(encoding="utf-8")
        self.assertEqual(hashlib.sha256(child_prompt.encode("utf-8")).hexdigest(),
                         ident["prompt_sha256_after"])
        self.assertIn("=== HGK SP IDENTITY", child_prompt)
        self.assertIn(inv, child_prompt)
        self.assertIn("WO-TEST-01", child_prompt)
        self.assertTrue(child_prompt.endswith("\n\nx"), child_prompt[-40:])
        # the caller's prompt is not destroyed, only prefixed
        self.assertTrue(rec["sp_identity"]["skill_sha256"])
        self.assertFalse(ident["issued_permit"])
        self.assertFalse(ident["signed_acceptance"])

    def test_I1_e2e_challenge_on_plan_lane_refuses(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-lane-")
        skills = _skills_root(tmp)
        inv = spid.new_invocation_id("challenge")
        cmd = _cmd(tmp, lane="PLAN", sp="challenge", invocation=inv, nonce=inv, skills=skills)
        p, rec, t = _run(cmd, tmp=tmp)
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertEqual(rec["code"], spid.ERR_SP_IDENTITY_LANE_MISMATCH)
        self.assertFalse((t / "logs").is_dir())

    def test_unknown_identity_refuses(self):
        self._refusal(expect_code=spid.ERR_SP_IDENTITY_UNKNOWN, sp="not-an-sp")

    def test_I2_unusable_procedure_root_refuses(self):
        missing = pathlib.Path(tempfile.mkdtemp(prefix="hgk-sp-noskill-"))
        self._refusal(expect_code=spid.ERR_SP_IDENTITY_SKILL_UNUSABLE, skills=missing)

    def test_I3_nonce_not_equal_to_invocation_id_refuses(self):
        self._refusal(expect_code=spid.ERR_SP_IDENTITY_NONCE_MISMATCH, nonce="HGK_LANE_NONCE_OK")

    def test_I4_identity_flags_without_identity_refuse(self):
        tmp = tempfile.mkdtemp(prefix="hgk-sp-dangling-")
        cmd = _cmd(tmp, sp=None, invocation=None, nonce=None,
                   skills=_skills_root(tmp), spine=_spine(tmp), workorder="WO-TEST-01")
        p, rec, t = _run(cmd, tmp=tmp)
        self.assertEqual(p.returncode, 4, p.stdout + p.stderr)
        self.assertEqual(rec["code"], disp.ERR_SP_IDENTITY_FLAG_WITHOUT_IDENTITY)
        self.assertFalse((t / "logs").is_dir())

    def test_I5_unknown_workorder_refuses_e2e(self):
        self._refusal(expect_code=spid.ERR_SP_IDENTITY_WORKORDER_UNKNOWN, workorder="WO-NOPE")

    def test_I6_child_that_never_echoes_the_id_is_not_ok_and_claims_no_join(self):
        """Injection happened, the child answered, but the identity never came back: the run must not
        be ok, and the receipt must report invocation_id_echoed=false instead of implying a join."""
        tmp = tempfile.mkdtemp(prefix="hgk-sp-silent-")
        skills = _skills_root(tmp)
        spine = _spine(tmp)
        inv = spid.new_invocation_id("challenge")
        cmd = _cmd(tmp, sp="challenge", invocation=inv, nonce=inv, skills=skills, spine=spine,
                   workorder="WO-TEST-01", stub=STUB_PLAIN)
        p, rec, _ = _run(cmd, tmp=tmp)
        self.assertNotEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(rec["ok"])
        self.assertEqual(rec["code"], "ERR_NO_ARM_EMITTED_NONCE", p.stdout)
        self.assertTrue(rec["sp_identity"]["identity_block_injected_pre_spawn"])
        self.assertFalse(rec["sp_identity"]["invocation_id_echoed"])

    def test_legacy_dispatch_without_sp_flags_is_unchanged(self):
        """No SP flags -> no identity field at all, so a pre-existing receipt shape is untouched."""
        tmp = tempfile.mkdtemp(prefix="hgk-sp-legacy-")
        cmd = _cmd(tmp, sp=None, invocation=None, nonce=None, skills=None, spine=None,
                   workorder=None, stub=STUB_PLAIN)
        # the plain nonce default is what a legacy caller gets
        p, rec, _ = _run(cmd, tmp=tmp)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue(rec["ok"], rec.get("code"))
        self.assertNotIn("sp_identity", rec)


if __name__ == "__main__":
    unittest.main()
