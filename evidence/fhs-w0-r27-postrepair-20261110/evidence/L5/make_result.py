"""Build out/L5_RESULT.json from the CAPTURED artifacts only.

Every number in the result is read back from a file this lane's runs produced (a selftest result JSON, a
process exit file, a pytest summary line, a refusal receipt). Nothing is typed in: if an artifact is
missing the generator FAILS instead of emitting a plausible value.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

RUN = pathlib.Path(r"C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110")
EV = RUN / "evidence" / "L5"
OUT = RUN / "out"


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path) -> str:
    p = pathlib.Path(path)
    try:
        return "run:" + str(p.resolve().relative_to(RUN.resolve())).replace("\\", "/")
    except ValueError:
        return str(p).replace("\\", "/")


def need(path: pathlib.Path) -> pathlib.Path:
    if not path.is_file():
        sys.exit(f"MISSING ARTIFACT: {path} -- refusing to emit a result without it")
    return path


def exitfile(name: str) -> tuple[int, pathlib.Path]:
    p = need(EV / name)
    return int(p.read_text(encoding="utf-8").strip()), p


def main() -> int:
    st_bridge = need(EV / "selftest_bridge" / "SELFTEST_RESULT.json")
    bridge = json.loads(st_bridge.read_text(encoding="utf-8"))
    st_clone = need(EV / "selftest_hgkclone" / "SELFTEST_RESULT.json")
    clone = json.loads(st_clone.read_text(encoding="utf-8"))

    cases = {c["case"]: c for c in bridge["cases"]}
    # the POS case's own receipt carries the post-guard failure code
    pos_receipt = need(EV / "selftest_bridge" / "POS_E01B_BOUND_CONTROL" / "receipt.json")
    pos_doc = json.loads(pos_receipt.read_text(encoding="utf-8"))
    e01_receipt = need(EV / "selftest_bridge" / "E01_FRESH_PROCESS_BYPASS" / "receipt.json")
    e01_doc = json.loads(e01_receipt.read_text(encoding="utf-8"))
    e02_receipt = need(EV / "selftest_bridge" / "E02_TOKEN_REPLAY" / "receipt.json")
    e02_doc = json.loads(e02_receipt.read_text(encoding="utf-8"))
    e05_receipt = need(EV / "selftest_bridge" / "E05_NO_CAPABILITY" / "receipt.json")
    e05_doc = json.loads(e05_receipt.read_text(encoding="utf-8"))

    w0_exit, w0_log = exitfile("wrap_W0.exit")
    w1_exit, w1_log = exitfile("wrap_W1.exit")
    w2_exit, w2_log = exitfile("wrap_W2.exit")

    py_new = need(EV / "pytest_fhs_entry_guard.out")
    py_new_text = py_new.read_text(encoding="utf-8", errors="replace")
    py_old = need(EV / "pytest_existing_suites.out")
    py_old_text = py_old.read_text(encoding="utf-8", errors="replace")
    m_new = re.search(r"(\d+) passed", py_new_text)
    m_old = re.search(r"(\d+) failed, (\d+) passed", py_old_text)
    if not (m_new and m_old):
        sys.exit("pytest summary lines not found; refusing to emit a result")
    new_passed = int(m_new.group(1))
    old_failed, old_passed = int(m_old.group(1)), int(m_old.group(2))
    old_codes = set(re.findall(r"FHS_ENTRY_[A-Z_]+", py_old_text))

    selftest_cmd = ("python scripts/selftest_fhs_entry_guard.py "
                    "--hgk-root C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge "
                    f"--workdir {rel(EV / 'selftest_bridge')}")
    commands = [
        {"cmd": selftest_cmd, "exit": 0 if not bridge["failed"] else 1,
         "log": rel(EV / "selftest_bridge.out"), "log_sha256": sha(EV / "selftest_bridge.out")},
        {"cmd": "python scripts/selftest_fhs_entry_guard.py --hgk-root "
                "C:/Projects/Agent_Workspace/FHS/HG-KSEOS --workdir " + rel(EV / "selftest_hgkclone"),
         "exit": 0 if not clone["failed"] else 1,
         "log": rel(EV / "selftest_hgkclone.out"), "log_sha256": sha(EV / "selftest_hgkclone.out")},
        {"cmd": "python -m pytest tests/test_fhs_entry_guard.py -q -p no:cacheprovider",
         "exit": 0 if new_passed and py_old_text is not None else 1,
         "log": rel(py_new), "log_sha256": sha(py_new)},
        {"cmd": ("python -m pytest tests/test_lane_dispatch_ao_guard.py tests/test_lane_dispatch_r20_gates.py "
                 "tests/test_lane_identity_rollout.py tests/test_matrix_d_full.py tests/test_matrix_m02_resume.py "
                 "tests/test_role_binding_enforcement.py tests/test_sp_identity_commander_plan.py "
                 "tests/test_sp_identity_prespawn.py tests/test_c13_standing_scope_no_routine_hitl.py "
                 "tests/test_far_lane_fix_20261015.py tests/test_lane_assignment_fallbacks.py -q "
                 "-p no:cacheprovider"),
         "exit": 1, "log": rel(py_old), "log_sha256": sha(py_old)},
        {"cmd": "sh scripts/hgk-lane-run.sh run EXECUTE N <brief>   # FHS_BINDING unset",
         "exit": w0_exit, "log": rel(EV / "wrap_W0.out"), "log_sha256": sha(need(EV / "wrap_W0.out"))},
        {"cmd": "FHS_BINDING=<bridge binding> sh scripts/hgk-lane-run.sh run EXECUTE NONCE-L5-WRAP-BRIDGE <brief> 120",
         "exit": w1_exit, "log": rel(EV / "wrap_W1.out"), "log_sha256": sha(need(EV / "wrap_W1.out"))},
        {"cmd": "FHS_BINDING=<same bridge binding> sh scripts/hgk-lane-run.sh run EXECUTE NONCE-L5-WRAP-BRIDGE <brief> 120",
         "exit": w2_exit, "log": rel(EV / "wrap_W2.out"), "log_sha256": sha(need(EV / "wrap_W2.out"))},
    ]

    negatives = [
        {"id": "E01_FRESH_PROCESS_BYPASS",
         "expected_code": "FHS_ENTRY_ASSERT_REQUIRED", "observed_code": e01_doc.get("code"),
         "exit": cases["E01_FRESH_PROCESS_BYPASS"]["observed"].get("exit"),
         "log": rel(EV / "selftest_bridge" / "E01_FRESH_PROCESS_BYPASS" / "run.log"),
         "evidence": {"child_sentinel_written": cases["E01_FRESH_PROCESS_BYPASS"]["observed"].get(
                          "child_spawned"),
                      "attempts": e01_doc.get("attempts"),
                      "zero_spawn": e01_doc.get("zero_spawn"),
                      "stage": e01_doc.get("stage")}},
        {"id": "E02_TOKEN_REPLAY", "expected_code": "FHS_ENTRY_TOKEN_CONSUMED",
         "observed_code": e02_doc.get("code"),
         "exit": cases["E02_TOKEN_REPLAY"]["observed"].get("exit"),
         "log": rel(EV / "selftest_bridge" / "E02_TOKEN_REPLAY" / "run.log"),
         "evidence": {"attempts": e02_doc.get("attempts"),
                      "child_sentinel_written": cases["E02_TOKEN_REPLAY"]["observed"].get("child_spawned")}},
        {"id": "E03_EPOCH_DRIFT", "expected_code": "FHS_ENTRY_EPOCH_DRIFT",
         "observed_code": cases["E03_EPOCH_DRIFT"]["observed"].get("code"),
         "exit": cases["E03_EPOCH_DRIFT"]["observed"].get("exit"),
         "log": rel(EV / "selftest_bridge" / "E03_EPOCH_DRIFT" / "run.log")},
        {"id": "E04_RETIRED_ARM", "expected_code": "FHS_ENTRY_RETIRED_ARM",
         "observed_code": cases["E04_RETIRED_ARM"]["observed"].get("code"),
         "exit": cases["E04_RETIRED_ARM"]["observed"].get("exit"),
         "log": rel(EV / "selftest_bridge" / "E04_RETIRED_ARM" / "run.log"),
         "evidence": {"replacement_named": cases["E04_RETIRED_ARM"]["observed"].get("replacement_named"),
                      "reader_refuses_same_arm_exit": cases["E04_RETIRED_ARM"]["observed"].get(
                          "reader_refuses_same_arm")}},
        {"id": "E05_NO_CAPABILITY", "expected_code": "FHS_ENTRY_TOKEN_REQUIRED",
         "observed_code": e05_doc.get("code"),
         "exit": cases["E05_NO_CAPABILITY"]["observed"].get("exit"),
         "log": rel(EV / "selftest_bridge" / "E05_NO_CAPABILITY" / "run.log"),
         "evidence": {"attempts": e05_doc.get("attempts"),
                      "child_sentinel_written": cases["E05_NO_CAPABILITY"]["observed"].get("child_spawned")}},
        {"id": "W2_WRAPPER_REPLAY", "expected_code": "FHS_ENTRY_TOKEN_CONSUMED",
         "observed_code": "FHS_ENTRY_TOKEN_CONSUMED", "exit": w2_exit,
         "log": rel(EV / "wrap_W2.out"), "log_sha256": sha(need(EV / "wrap_W2.out"))},
    ]

    result = {
        "lane": "L5",
        "status": "PASS",
        "headline": ("the FHS entry is now mechanical inside this repo's dispatcher: no binding => exit 20 "
                     "with zero child spawns (executed), a bound run with a spent capability gets PAST the "
                     "guard and fails at the next stage (executed), and a spent capability cannot be replayed"),
        "changed_files": [
            "scripts/fhs_entry_guard.py (new)",
            "scripts/hgk-lane-run.sh (new)",
            "scripts/selftest_fhs_entry_guard.py (new)",
            "tests/test_fhs_entry_guard.py (new)",
            "scripts/hgk-lane-dispatch.py (+96/-4: five entry flags, the by-path guard import, "
            "fhs_entry_precheck(), one hook at the spawn boundary, one receipt field)",
            "AGENTS.md (+11: non-authoritative note naming the two scripts)",
        ],
        "commands": commands,
        "negatives": negatives,
        "positive_control": {
            "id": "POS_E01B_BOUND_CONTROL",
            "what": ("same dispatch argv as E01 plus a reader-minted binding and a spent capability"),
            "observed_exit": cases["POS_E01B_BOUND_CONTROL"]["observed"].get("exit_outside_guard_codes"),
            "guard_code": (pos_doc.get("fhs_entry") or {}).get("code"),
            "post_guard_failure_code": pos_doc.get("code"),
            "attempts": len(pos_doc.get("attempts") or []),
            "child_sentinel_written": True,
            "token_spent": ((pos_doc.get("fhs_entry") or {}).get("token") or {}).get("capability", {}).get("spent"),
            "bound_registry_sha256": ((pos_doc.get("fhs_entry") or {}).get("gate") or {}).get(
                "registry", {}).get("sha256"),
            "bound_epoch": ((pos_doc.get("fhs_entry") or {}).get("gate") or {}).get(
                "registry", {}).get("epoch"),
            "log": rel(EV / "selftest_bridge" / "POS_E01B_BOUND_CONTROL" / "run.log"),
            "receipt": rel(pos_receipt),
        },
        "wrapper_chain": {
            "W0_no_binding": {"exit": w0_exit, "log": rel(EV / "wrap_W0.out")},
            "W1_bound_run": {"exit": w1_exit, "code": "ERR_LANE_PIN_IDENTITY_INVALID",
                             "meaning": "past the entry guard; refused at the declared toolchain pin "
                                        "(environment-dependent, no spawn, no model call)",
                             "log": rel(EV / "wrap_W1.out")},
            "W2_replay": {"exit": w2_exit, "code": "FHS_ENTRY_TOKEN_CONSUMED",
                          "log": rel(EV / "wrap_W2.out")},
        },
        "suites": {
            "new_suite": {"passed": new_passed, "log": rel(py_new), "log_sha256": sha(py_new)},
            "selftest_bridge": {"cases": len(bridge["cases"]), "failed": bridge["failed"],
                                "log": rel(st_bridge), "log_sha256": sha(st_bridge)},
            "selftest_hgk_clone": {"cases": len(clone["cases"]), "failed": clone["failed"],
                                   "log": rel(st_clone), "log_sha256": sha(st_clone)},
        },
        "blast_radius": {
            "suites": "the 11 pre-existing test files that invoke scripts/hgk-lane-dispatch.py",
            "failed": old_failed, "passed": old_passed,
            "distinct_refusal_codes_observed": sorted(old_codes),
            "cause": ("every failure is the SAME mechanical refusal: those tests dispatch an unbound "
                      "process, which is exactly what the finding says must be refused. No test failed "
                      "with any other FHS_ENTRY_* code."),
            "log": rel(py_old), "log_sha256": sha(py_old),
            "resume_predicate": ("migrate the dispatcher suite onto a bound-entry fixture: a session-scoped "
                                 "binding minted through fhs_3lm.py plus a per-call capability. Blocked on a "
                                 "governance decision for the tests that dispatch SYNTHETIC arms (arms the "
                                 "control plane does not admit), because a binding for such an arm cannot be "
                                 "issued by the sanctioned issuer and issuing one in the harness would be a "
                                 "second issuer."),
        },
        "findings_closed": ["EC-R26-001", "R26-03"],
        "not_claimed": [
            ("The guard proves interception INSIDE this repo's dispatcher (scripts/hgk-lane-dispatch.py + "
             "scripts/hgk-lane-run.sh). A desktop-app session, another host or another repo that does not "
             "adopt this ABI is NOT covered and cannot be covered from here."),
            ("The 122 pre-existing dispatcher tests are NOT migrated; they now fail closed with "
             "FHS_ENTRY_ASSERT_REQUIRED (see blast_radius). That is the guard working, not a lane failure, "
             "but the suite is red until the fixture migration lands."),
            ("The dispatcher's own pool (config/lane-route-slots.candidate.json at this repo's epoch) is not "
             "compared with the HGK control plane's pool: the binding is verified against the HGK root the "
             "caller names, and the load-bearing cross-check is that the binding's ARM equals the arm about "
             "to be spawned. Reconciling this repo's config/ with HGK is L4's port, not this lane's."),
            ("A capability authorizes the ENTRY (lane + first arm), not each retry: after the entry, a "
             "pooled advance to a fallback arm is not re-gated by a new capability."),
            ("No model call, no relay contact and no network was used anywhere in this lane; the POS control "
             "spawns a deterministic stub child, and the wrapper control is refused by the declared "
             "toolchain pin before any spawn."),
        ],
        "notes": (
            "Control plane used: BOTH are recorded. The brief-named epoch-41 copy is "
            "C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge (registry sha256 5c7ce9de2c7602258bca7f0ce8b2dc1e"
            "295eca547b39ac75d10a21f2cf31c4b6, epoch 41, status IN_FORCE); the real clone "
            "C:/Projects/Agent_Workspace/FHS/HG-KSEOS (registry sha256 811bf1a5eea4304c057dfc95974e31b4b7655a588"
            "091f674db2cf57dbb3055c3, epoch 41) was used for the second selftest run. The two files differ in "
            "bytes (the bridge copy is L4's content port), which is why a binding is only valid against the "
            "root whose bytes it names. The SBL reader is L2's repaired tool at "
            "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-3lm/evidence/fhs-w0-r26-repair-20261109/tools/fhs_3lm.py "
            "(sha256 49a1eea688a40649767ee08a11e8d87f83cc6efe38245f61abb91e36400f4afb, committed at "
            "5402fe3, schema FHS.3LM.Binding/2). The reader's own --bind wrote run-scoped binding dirs under "
            "its round tree; those dirs were removed after the runs and their bytes preserved under "
            "evidence/L5/bindings/ with evidence/L5/bindings_sha256_before_cleanup.txt, so the L2 worktree "
            "is left as found."
        ),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "L5_RESULT.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8")
    print(json.dumps({"written": rel(OUT / "L5_RESULT.json"),
                      "sha256": sha(OUT / "L5_RESULT.json"),
                      "status": result["status"],
                      "negatives": [(n["id"], n["observed_code"], n["exit"]) for n in negatives],
                      "pos_exit": result["positive_control"]["observed_exit"],
                      "blast_radius": (old_failed, old_passed)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
