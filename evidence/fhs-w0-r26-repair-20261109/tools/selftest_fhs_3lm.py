#!/usr/bin/env python3
"""selftest_fhs_3lm.py — executed proof for the repaired FHS-3L&M hard entry contract (E01..E08).

Every case below runs the repaired tool as a subprocess, captures stdout/stderr/exit to a log file, and
compares the observed exit status and refusal code against what the case declares. Nothing is typed in as a
result: the JSON this script emits is derived from the captured logs.

Fixtures it builds (all under --workdir, never in the control plane, never in the worktree round):
  * scratch rounds      <case>/tools/fhs_3lm.py  — a byte-identical copy of the tool, so ROUND resolves
                                                  inside the scratch tree and bindings cannot touch the repo
  * probe/pool_drift    real registry bytes + a pool copy with one unrelated transport_model edited (E03)
  * probe/no_pool_ledger real registry bytes + a pool copy whose retired_arms is null, i.e. NO pool ledger,
                          so only the registry's retirement section can decide (E04c)
  * probe/registry_vs_pool real registry bytes + the real epoch-33 pool bytes, which still list the arm the
                          registry retires (E08)

stdlib only. Exit 0 only when every case matches.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REGISTRY_REL = pathlib.Path("config") / "lane-routing-registry.yaml"
POOL_REL = pathlib.Path("config") / "lane-route-slots.candidate.json"
RETIRED_ARM = "opencode-go/mimo-v2.6-pro"
REPLACEMENT = "opencode-go/mimo-v2.6-flash"

RESULTS: list[dict] = []


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def record(case: str, expected: int, observed: int, code, log_path: pathlib.Path, checks: list,
           note: str = "") -> None:
    ok = expected == observed and all(c["ok"] for c in checks)
    RESULTS.append({
        "case": case,
        "expected_exit": expected,
        "observed_exit": observed,
        "code": code,
        "ok": ok,
        "log": str(log_path),
        "log_sha256": sha256(log_path.read_bytes()) if log_path.is_file() else None,
        "checks": checks,
        "note": note,
    })
    print(f"[{'PASS' if ok else 'FAIL'}] {case:<5} expect={expected} observed={observed} code={code}"
          + (f"  {note}" if note else ""))


def chk(name: str, ok: bool, **detail) -> dict:
    return {"check": name, "ok": bool(ok), **detail}


class Runner:
    def __init__(self, tool: pathlib.Path, logdir: pathlib.Path, scratch: pathlib.Path):
        self.tool = tool
        self.logdir = logdir
        self.scratch = scratch
        self.logdir.mkdir(parents=True, exist_ok=True)
        self.scratch.mkdir(parents=True, exist_ok=True)
        self.tool_sha = sha256(tool.read_bytes())

    def round_dir(self, name: str) -> pathlib.Path:
        """A scratch round: <name>/tools/fhs_3lm.py, byte-identical to the tool under test."""
        rnd = self.scratch / name
        (rnd / "tools").mkdir(parents=True, exist_ok=True)
        dst = rnd / "tools" / "fhs_3lm.py"
        shutil.copyfile(self.tool, dst)
        assert sha256(dst.read_bytes()) == self.tool_sha, "scratch copy is not byte-identical to the tool"
        return rnd

    def run(self, case: str, label: str, rnd: pathlib.Path, args: list[str], env_extra=None):
        env = {k: v for k, v in os.environ.items() if k != "HGK_ROOT"}
        env.update(env_extra or {})
        argv = [sys.executable, str(rnd / "tools" / "fhs_3lm.py"), *args]
        p = subprocess.run(argv, cwd=str(rnd), env=env, capture_output=True, text=True)
        log = self.logdir / f"{case}_{label}.log"
        log.write_text(
            "$ " + " ".join(argv) + "\n"
            f"cwd={rnd}\nexit={p.returncode}\n--- stdout ---\n{p.stdout}\n--- stderr ---\n{p.stderr}\n",
            encoding="utf-8")
        payload: dict = {}
        if p.stdout.strip():
            try:
                payload = json.loads(p.stdout)
            except json.JSONDecodeError:
                payload = {"_unparsed_stdout": p.stdout}
        if not isinstance(payload, dict):
            payload = {"_unparsed_stdout": p.stdout}
        return p.returncode, payload, log


def write_json(path: pathlib.Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def build_probes(hgk: pathlib.Path, epoch33: pathlib.Path, scratch: pathlib.Path) -> dict:
    reg = (hgk / REGISTRY_REL).read_bytes()
    pool_txt = (hgk / POOL_REL).read_text(encoding="utf-8")
    probes = {}

    d = scratch / "probe" / "pool_drift"
    (d / "config").mkdir(parents=True, exist_ok=True)
    (d / REGISTRY_REL).write_bytes(reg)
    doc = json.loads(pool_txt)
    plan = next(ln for ln in doc["lanes"] if ln["lane"] == "PLAN")
    edited = next(e for e in plan["ordered_pool"] if e["rank"] == 3)
    edited["transport_model"] = str(edited.get("transport_model")) + "-DRIFT-PROBE"
    (d / POOL_REL).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    probes["pool_drift"] = d

    d = scratch / "probe" / "no_pool_ledger"
    (d / "config").mkdir(parents=True, exist_ok=True)
    (d / REGISTRY_REL).write_bytes(reg)
    doc = json.loads(pool_txt)
    doc["retired_arms"] = None
    (d / POOL_REL).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    probes["no_pool_ledger"] = d

    d = scratch / "probe" / "registry_vs_pool"
    (d / "config").mkdir(parents=True, exist_ok=True)
    (d / REGISTRY_REL).write_bytes(reg)
    shutil.copyfile(epoch33 / POOL_REL, d / POOL_REL)
    probes["registry_vs_pool"] = d

    # a pool where the arm the E03 binding names has been removed from its lane, everything else intact
    d = scratch / "probe" / "arm_left_pool"
    (d / "config").mkdir(parents=True, exist_ok=True)
    (d / REGISTRY_REL).write_bytes(reg)
    doc = json.loads(pool_txt)
    execute = next(ln for ln in doc["lanes"] if ln["lane"] == "EXECUTE")
    execute["ordered_pool"] = [e for e in execute["ordered_pool"]
                               if not (e.get("provider") == "opencode-go"
                                       and e.get("model") == "deepseek-v4.1-flash")]
    (d / POOL_REL).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    probes["arm_left_pool"] = d
    return probes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True)
    ap.add_argument("--hgk-root", required=True, help="the epoch-41 control plane (real HG-KSEOS clone)")
    ap.add_argument("--epoch33-root", required=True,
                    help="an extracted epoch-33 config root (registry 33 + pool with retired_arms: null)")
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--logdir", required=True)
    ap.add_argument("--json-out", required=True)
    a = ap.parse_args()

    tool = pathlib.Path(a.tool).resolve()
    hgk = pathlib.Path(a.hgk_root).resolve()
    e33 = pathlib.Path(a.epoch33_root).resolve()
    scratch = pathlib.Path(a.workdir).resolve()
    logdir = pathlib.Path(a.logdir).resolve()
    R = Runner(tool, logdir, scratch)
    # the cases are written to be re-runnable: their own scratch trees are rebuilt from scratch each time, so
    # a second run cannot pass on a file the first run left behind (or fail on a collision it created).
    for name in ("bare", "real", "probe", "tamper"):
        shutil.rmtree(scratch / name, ignore_errors=True)
    probes = build_probes(hgk, e33, scratch)

    reg_sha = sha256((hgk / REGISTRY_REL).read_bytes())
    pool_sha = sha256((hgk / POOL_REL).read_bytes())
    print(f"tool        {tool}\nfa_tool_sha {R.tool_sha}\nhgk_root    {hgk}\nregistry    {reg_sha}\n"
          f"pool        {pool_sha}\nprobes      {sorted(probes)}\n")

    bare = R.round_dir("bare")            # no discovery file, so root discovery can fail closed

    # ---- E00a: no --hgk-root, no HGK_ROOT, no discovery file -> ERR_HGK_ROOT_UNRESOLVED -----------
    rc, out, log = R.run("E00a", "root_unresolved", bare, ["--menu"])
    record("E00a", 8, rc, out.get("error"), log,
           [chk("code", out.get("error") == "ERR_HGK_ROOT_UNRESOLVED", got=out.get("error")),
            chk("tried_listed", isinstance(out.get("tried"), dict))])

    # ---- E00b: a root without the two config files -> ERR_HGK_ROOT_INVALID -------------------------
    empty = scratch / "probe" / "empty_root"
    empty.mkdir(parents=True, exist_ok=True)
    rc, out, log = R.run("E00b", "root_invalid", bare, ["--hgk-root", str(empty), "--menu"])
    record("E00b", 8, rc, out.get("error"), log,
           [chk("code", out.get("error") == "ERR_HGK_ROOT_INVALID", got=out.get("error")),
            chk("missing_listed", bool(out.get("missing")))])

    real = R.round_dir("real")

    # ---- E01: --menu on the real epoch-41 plane: 9 slots, 9 admitted, numeric epoch 41 -------------
    rc, m, log = R.run("E01", "menu_epoch41", real, ["--menu", "--hgk-root", str(hgk)])
    slots = {f"{ln['lane']}/{s['slot']}": s for ln in m.get("lanes", []) for s in ln.get("slots", [])}
    rows = [{"lane": ln["lane"], "slot": s["slot"], "arm": f"{s['provider']}/{s['model']}",
             "admitted": s["admitted"], "pool_rank": s["pool_rank"], "why_not": s["why_not"]}
            for ln in m.get("lanes", []) for s in ln.get("slots", [])]
    write_json(logdir.parent / "E01_menu_rows.json", {"policy_epoch": m.get("policy_epoch"), "rows": rows})
    record("E01", 0, rc, None, log, [
        chk("schema_v2", m.get("schema") == "FHS.3LM.Menu/2", got=m.get("schema")),
        chk("epoch_numeric_41", m.get("policy_epoch") == 41 and isinstance(m.get("policy_epoch"), int),
            got=m.get("policy_epoch")),
        chk("epoch_status_in_force", m.get("epoch_status") == "IN_FORCE", got=m.get("epoch_status")),
        chk("contract_epoch_34", m.get("contract_epoch") == 34, got=m.get("contract_epoch")),
        chk("slot_count_9", m.get("slot_count") == 9, got=m.get("slot_count")),
        chk("admitted_9", m.get("admitted_count") == 9 and len(rows) == 9, got=m.get("admitted_count")),
        chk("all_admitted", m.get("all_admitted") is True),
        chk("registry_sha_equals_file", m.get("registry_sha256") == reg_sha),
        chk("pool_sha_equals_file", m.get("pool_sha256") == pool_sha),
        chk("plane_plan_opt2_is_flash", slots["PLAN/opt2"]["model"] == "mimo-v2.6-flash"
            and slots["PLAN/opt2"]["pool_rank"] == 4, got=slots["PLAN/opt2"]),
        chk("alive_epoch41", m.get("generated_at") is not None),
    ], note="9/9 admitted, epoch 41 from config/lane-routing-registry.yaml")

    # ---- E01b: --plane pins the discovery source, the ledger and its dual origin --------------------
    rc, p, log = R.run("E01b", "plane", bare, ["--plane", "--hgk-root", str(hgk)])
    record("E01b", 0, rc, None, log, [
        chk("epoch_41", p.get("policy_epoch") == 41, got=p.get("policy_epoch")),
        chk("discovery_source_flag", p.get("discovery_source") == "--hgk-root",
            got=p.get("discovery_source")),
        chk("retired_present", RETIRED_ARM in (p.get("retired_ledger") or {}),
            got=sorted((p.get("retired_ledger") or {}))),
        chk("ledger_dual_source", (p.get("retired_ledger_source") or {}).get("pool") is not None
            and (p.get("retired_ledger_source") or {}).get("registry") is not None,
            got=p.get("retired_ledger_source")),
        chk("live_arm_sites", p.get("live_arm_sites") == 7, got=p.get("live_arm_sites")),
    ])

    # ---- E02: session-unique, non-overwriting bindings --------------------------------------------
    rc, b1, log = R.run("E02a", "bind_run_a", real,
                        ["--bind", "PLAN", "primary", "--run-id", "run-e02-a", "--session-id", "sess-e02a1",
                         "--work-id", "W-L2", "--hgk-root", str(hgk)])
    p1 = real / "lanes" / "bindings" / "run-e02-a" / f"PLAN_primary_{b1.get('record', {}).get('nonce', '')}.json"
    f1_sha = sha256(p1.read_bytes()) if p1.is_file() else None
    record("E02a", 0, rc, None, log, [
        chk("bound", b1.get("ok") is True and b1.get("bound") is True),
        chk("path_shape", str(b1.get("path", "")).startswith("lanes/bindings/run-e02-a/PLAN_primary_")
            and str(b1.get("path", "")).endswith(".json"), got=b1.get("path")),
        chk("binding_id_64hex", isinstance(b1.get("binding_id"), str) and len(b1.get("binding_id")) == 64),
        chk("record_session", (b1.get("record") or {}).get("session_id") == "sess-e02a1"),
        chk("record_policy_epoch_int", (b1.get("record") or {}).get("policy_epoch") == 41
            and isinstance((b1.get("record") or {}).get("policy_epoch"), int)),
        chk("record_not_a_session_pin", (b1.get("record") or {}).get("not_a_session_pin") is True),
        chk("file_matches_path", p1.is_file(), got=str(p1)),
    ])

    rc, b2, log = R.run("E02b", "bind_run_b", real,
                        ["--bind", "PLAN", "primary", "--run-id", "run-e02-b", "--session-id", "sess-e02b1",
                         "--hgk-root", str(hgk)])
    p2 = real / "lanes" / "bindings" / "run-e02-b" / f"PLAN_primary_{b2.get('record', {}).get('nonce', '')}.json"
    record("E02b", 0, rc, None, log, [
        chk("bound", b2.get("ok") is True),
        chk("distinct_path", b2.get("path") != b1.get("path"), got=[b1.get("path"), b2.get("path")]),
        chk("distinct_binding_id", b2.get("binding_id") != b1.get("binding_id")),
        chk("both_files_exist", p1.is_file() and p2.is_file()),
        chk("first_file_untouched", sha256(p1.read_bytes()) == f1_sha if p1.is_file() else False),
    ], note="two run-ids, same lane/slot, no overwrite")

    rc, b3, log = R.run("E02c", "bind_run_a_other_session", real,
                        ["--bind", "PLAN", "primary", "--run-id", "run-e02-a", "--session-id", "sess-e02a2",
                         "--hgk-root", str(hgk)])
    record("E02c", 0, rc, None, log, [
        chk("bound", b3.get("ok") is True),
        chk("distinct_path_same_run", b3.get("path") != b1.get("path"), got=[b1.get("path"), b3.get("path")]),
        chk("distinct_binding_id", b3.get("binding_id") != b1.get("binding_id")),
    ], note="same run, second session: session-unique inside one run")

    rc, b4, log = R.run("E02d", "bind_collision", real,
                        ["--bind", "PLAN", "primary", "--run-id", "run-e02-a", "--session-id", "sess-e02a1",
                         "--hgk-root", str(hgk)])
    record("E02d", 10, rc, b4.get("error"), log, [
        chk("code", b4.get("error") == "BINDING_ALREADY_EXISTS", got=b4.get("error")),
        chk("first_file_untouched", sha256(p1.read_bytes()) == f1_sha if p1.is_file() else False),
        chk("no_third_file", len(list((real / "lanes" / "bindings" / "run-e02-a").glob("*.json"))) == 2,
            got=len(list((real / "lanes" / "bindings" / "run-e02-a").glob("*.json")))),
    ], note="same run+session+lane+slot is refused, never overwritten")

    # ---- E03: pool moved under a valid binding -> POOL_DIGEST_DRIFT -------------------------------
    rc, b5, log = R.run("E03a", "bind_for_pool_drift", real,
                        ["--bind", "EXECUTE", "primary", "--run-id", "run-e03",
                         "--session-id", "sess-e03", "--hgk-root", str(hgk)])
    bind3 = real / str(b5.get("path", ""))
    record("E03a", 0, rc, None, log, [chk("bound", b5.get("ok") is True),
                                      chk("file_exists", bind3.is_file(), got=str(bind3))])

    rc, o3c, log = R.run("E03b", "assert_control_same_binding", real,
                        ["--assert", str(bind3), "--hgk-root", str(hgk)])
    record("E03b", 0, rc, None, log, [
        chk("ok", o3c.get("ok") is True),
        chk("pool_unchanged", o3c.get("pool_unchanged") is True),
        chk("pool_sha_is_file", o3c.get("pool_sha256") == pool_sha),
    ], note="the control: the same binding still asserts against the unmutated plane")

    rc, o3, log = R.run("E03c", "assert_pool_drift", real,
                        ["--assert", str(bind3), "--hgk-root", str(probes["pool_drift"])])
    record("E03c", 7, rc, o3.get("error"), log, [
        chk("code", o3.get("error") == "POOL_DIGEST_DRIFT", got=o3.get("error")),
        chk("digests_differ", o3.get("bound_pool_sha256") != o3.get("now_pool_sha256")),
        chk("bound_digest_is_real_pool", o3.get("bound_pool_sha256") == pool_sha),
    ], note="pool copy mutated, registry untouched: the drift is attributed to the pool, not the epoch")

    # ---- E04: retirement ledger from BOTH sources ------------------------------------------------
    rc, o4a, log = R.run("E04a", "assert_arm_retired_epoch41", real,
                         ["--assert-arm", RETIRED_ARM, "--hgk-root", str(hgk)])
    record("E04a", 9, rc, o4a.get("error"), log, [
        chk("code", o4a.get("error") == "RETIRED_ARM", got=o4a.get("error")),
        chk("replacement", o4a.get("replacement") == REPLACEMENT, got=o4a.get("replacement")),
        chk("retired_epoch_41", o4a.get("retired_epoch") == 41, got=o4a.get("retired_epoch")),
        chk("ledger_dual", (o4a.get("ledger_source") or {}).get("pool") and
            (o4a.get("ledger_source") or {}).get("registry"), got=o4a.get("ledger_source")),
    ])

    rc, o4b, log = R.run("E04b", "assert_arm_epoch33", real,
                         ["--assert-arm", RETIRED_ARM, "--hgk-root", str(e33)])
    record("E04b", 0, rc, None, log, [
        chk("plane_epoch_33", o4b.get("policy_epoch") == 33, got=o4b.get("policy_epoch")),
        chk("retired_false", o4b.get("retired") is False, got=o4b.get("retired")),
        chk("pooled_in_plan", any(name == "PLAN" for name, _ in o4b.get("lanes", [])),
            got=o4b.get("lanes")),
    ], note=("MEASURED, not a pass: the epoch-33 registry carries no retirement section and the epoch-33 "
             "pool carries no ledger, so nothing retires this arm at epoch 33; the retirement is an epoch-41 "
             "fact"))

    rc, o4c, log = R.run("E04c", "assert_arm_registry_only_ledger", real,
                         ["--assert-arm", RETIRED_ARM, "--hgk-root", str(probes["no_pool_ledger"])])
    record("E04c", 9, rc, o4c.get("error"), log, [
        chk("code", o4c.get("error") == "RETIRED_ARM", got=o4c.get("error")),
        chk("pool_ledger_absent", (o4c.get("ledger_source") or {}).get("pool") is None,
            got=(o4c.get("ledger_source") or {}).get("pool")),
        chk("registry_ledger_decided", (o4c.get("ledger_source") or {}).get("registry") is not None,
            got=(o4c.get("ledger_source") or {}).get("registry")),
    ], note="pool retired_arms nulled on a copy: the registry retirement section alone refuses")

    # ---- E05: the same arm in PLAN and VERIFY is recorded, not refused -----------------------------
    rc, b5a, log = R.run("E05a", "bind_plan_primary", real,
                         ["--bind", "PLAN", "primary", "--run-id", "run-e05", "--session-id", "sess-e05-plan",
                          "--hgk-root", str(hgk)])
    record("E05a", 0, rc, None, log, [
        chk("bound", b5a.get("ok") is True),
        chk("same_arm_lanes_false", (b5a.get("record") or {}).get("same_arm_lanes") is False),
    ])
    rc, b5b, log = R.run("E05b", "bind_verify_primary_same_arm", real,
                         ["--bind", "VERIFY", "primary", "--run-id", "run-e05", "--session-id", "sess-e05-ver",
                          "--hgk-root", str(hgk)])
    rec5 = b5b.get("record") or {}
    record("E05b", 0, rc, None, log, [
        chk("bound_same_arm", b5b.get("ok") is True and rec5.get("model") == "gpt-6.1-sol", got=rec5.get("model")),
        chk("same_arm_lanes_true", rec5.get("same_arm_lanes") is True, got=rec5.get("same_arm_lanes")),
        chk("same_arm_with_named", rec5.get("same_arm_with") == ["PLAN/primary"], got=rec5.get("same_arm_with")),
        chk("sod_not_mandated", rec5.get("sod_mandated") is False),
    ], note="PLAN and VERIFY both on openai-codex/gpt-6.1-sol: allowed and recorded")
    rc, o5, log = R.run("E05c", "assert_same_arm_binding", real,
                        ["--assert", str(real / str(b5b.get("path", ""))), "--hgk-root", str(hgk)])
    record("E05c", 0, rc, None, log, [
        chk("ok", o5.get("ok") is True),
        chk("same_arm_lanes_reported", o5.get("same_arm_lanes") is True, got=o5.get("same_arm_lanes")),
    ])

    # ---- E06: --ttl 0 binds, then the binding is expired ------------------------------------------
    rc, b6, log = R.run("E06a", "bind_ttl0", real,
                        ["--bind", "EXECUTE", "primary", "--run-id", "run-e06", "--session-id", "sess-e06",
                         "--ttl", "0", "--hgk-root", str(hgk)])
    rec6 = b6.get("record") or {}
    record("E06a", 0, rc, None, log, [
        chk("bound", b6.get("ok") is True),
        chk("ttl_zero", rec6.get("ttl_seconds") == 0, got=rec6.get("ttl_seconds")),
        chk("expires_eq_bound", rec6.get("expires_at") == rec6.get("bound_at"),
            got=[rec6.get("bound_at"), rec6.get("expires_at")]),
    ])
    rc, o6, log = R.run("E06b", "assert_expired", real,
                        ["--assert", str(real / str(b6.get("path", ""))), "--hgk-root", str(hgk)])
    record("E06b", 7, rc, o6.get("error"), log, [
        chk("code", o6.get("error") == "BINDING_EXPIRED", got=o6.get("error")),
        chk("times_reported", o6.get("expires_at") == rec6.get("expires_at"), got=o6.get("expires_at")),
    ], note="ttl 0: the record is genuine but no longer evidence of a current lane")

    # ---- E07: one edited field in a binding copy -> BINDING_TAMPERED -------------------------------
    tam = scratch / "tamper" / "PLAN_primary_tampered.json"
    tam.parent.mkdir(parents=True, exist_ok=True)
    doc = json.loads(p1.read_text(encoding="utf-8"))
    doc["model"] = "deepseek-v4.1-flash"
    write_json(tam, doc)
    rc, o7, log = R.run("E07", "assert_tampered_model", real,
                        ["--assert", str(tam), "--hgk-root", str(hgk)])
    record("E07", 8, rc, o7.get("error"), log, [
        chk("code", o7.get("error") == "BINDING_TAMPERED", got=o7.get("error")),
        chk("claimed_vs_recomputed", o7.get("binding_id_claimed") != o7.get("binding_id_recomputed")),
        chk("claimed_is_original", o7.get("binding_id_claimed") == b1.get("binding_id")),
    ], note="model edited, binding_id left in place -> digest mismatch, not an epoch story")

    # ---- E08: pool still lists an arm the registry retires -> HOLD_REGISTRY_POOL_DRIFT -------------
    rc, m8, log = R.run("E08a", "menu_registry_pool_drift", real,
                        ["--menu", "--hgk-root", str(probes["registry_vs_pool"])])
    record("E08a", 7, rc, m8.get("error"), log, [
        chk("code", m8.get("error") == "HOLD_REGISTRY_POOL_DRIFT", got=m8.get("error")),
        chk("names_the_arm", RETIRED_ARM in (m8.get("retired_but_still_pooled") or {}),
            got=m8.get("retired_but_still_pooled")),
    ], note="epoch-41 registry + epoch-33 pool: the menu is withheld instead of printing a mixed plane")
    rc, o8, log = R.run("E08b", "assert_arm_drift", real,
                        ["--assert-arm", RETIRED_ARM, "--hgk-root", str(probes["registry_vs_pool"])])
    record("E08b", 7, rc, o8.get("error"), log, [
        chk("code", o8.get("error") == "HOLD_REGISTRY_POOL_DRIFT", got=o8.get("error")),
    ], note="--assert-arm refuses the drift before it can call the arm retired-or-live")

    # ---- E09: the numeric epoch is compared, not just the digest ------------------------------------
    rc, o9, log = R.run("E09", "assert_epoch_drift", real,
                        ["--assert", str(bind3), "--hgk-root", str(e33)])
    record("E09", 7, rc, o9.get("error"), log, [
        chk("code", o9.get("error") == "EPOCH_DRIFT", got=o9.get("error")),
        chk("epochs_named", o9.get("bound_policy_epoch") == 41 and o9.get("now_policy_epoch") == 33,
            got=[o9.get("bound_policy_epoch"), o9.get("now_policy_epoch")]),
    ], note="41 -> 33: both the digest and the integer epoch are compared")

    # ---- E10: removing the bound arm from its lane pool is caught by the pool digest first ----------
    rc, o10, log = R.run("E10", "assert_arm_removed_from_pool", real,
                         ["--assert", str(bind3), "--hgk-root", str(probes["arm_left_pool"])])
    record("E10", 7, rc, o10.get("error"), log, [
        chk("code", o10.get("error") == "POOL_DIGEST_DRIFT", got=o10.get("error")),
        chk("digest_moved", o10.get("bound_pool_sha256") != o10.get("now_pool_sha256")),
    ], note=("an arm removed from a lane pool moves the pool bytes, so the digest check refuses first; "
             "ARM_LEFT_POOL stays as the second line of defence and is not claimed as a first refusal"))

    # ---- E11: the collision guard holds under concurrent writers (O_EXCL, not check-then-write) -----
    conc = real / "lanes" / "bindings" / "run-e11"
    argv_common = [sys.executable, str(real / "tools" / "fhs_3lm.py"), "--bind", "EXECUTE", "opt1",
                   "--run-id", "run-e11", "--session-id", "sess-e11", "--hgk-root", str(hgk)]
    env = {k: v for k, v in os.environ.items() if k != "HGK_ROOT"}
    procs = [subprocess.Popen(argv_common, cwd=str(real), env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
             for _ in range(6)]
    outs = []
    for p in procs:
        so, se = p.communicate()
        outs.append((p.returncode, so, se))
    codes = [rc for rc, _, _ in outs]
    log = logdir / "E11_concurrent_binds.log"
    log.write_text("$ 6 x (--bind EXECUTE opt1 --run-id run-e11 --session-id sess-e11)\n"
                   + "\n".join(f"proc{i}: exit={rc}\n{so}\n{se}"
                               for i, (rc, so, se) in enumerate(outs)), encoding="utf-8")
    files = sorted(conc.glob("*.json")) if conc.is_dir() else []
    ok_digest = False
    if len(files) == 1:
        doc = json.loads(files[0].read_text(encoding="utf-8"))
        claimed = doc.pop("binding_id", None)
        ok_digest = claimed == sha256(json.dumps(doc, sort_keys=True, separators=(",", ":"),
                                                ensure_ascii=False).encode("utf-8"))
    record("E11", 1, codes.count(0), "BINDING_ALREADY_EXISTS" if codes.count(10) == 5 else None, log, [
        chk("exactly_one_winner", codes.count(0) == 1, got=codes),
        chk("five_refusals_exit10", codes.count(10) == 5, got=codes),
        chk("single_file", len(files) == 1, got=[f.name for f in files]),
        chk("survivor_digest_valid", ok_digest),
    ], note="6 writers, one name: one binding, five BINDING_ALREADY_EXISTS (expected_exit=1 winner)")

    # ---- summary ----------------------------------------------------------------------------------
    failed = [r for r in RESULTS if not r["ok"]]
    summary = {
        "schema": "FHS.3LM.Selftest/1",
        "tool": str(tool),
        "tool_sha256": R.tool_sha,
        "hgk_root": str(hgk),
        "registry_sha256": reg_sha,
        "pool_sha256": pool_sha,
        "epoch33_root": str(e33),
        "cases": RESULTS,
        "case_count": len(RESULTS),
        "failed": [r["case"] for r in failed],
        "verdict": "PASS" if not failed else "FAIL",
    }
    write_json(pathlib.Path(a.json_out), summary)
    print(f"\n{summary['verdict']}: {len(RESULTS) - len(failed)}/{len(RESULTS)} cases matched"
          + (f"  failed={summary['failed']}" if failed else ""))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
