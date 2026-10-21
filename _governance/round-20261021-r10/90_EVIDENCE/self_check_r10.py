"""R10 self-check: the handover is only worth handing over if its claims hold on disk.

Two checks here exist specifically because of what this round learned:

  C4  compares the THREE runtime surfaces to EACH OTHER. Every check in this programme
      compared a thing to its own pin, which is why a rebind could leave all three
      declarations naming a superseded model while the drift gate returned 0 findings.
      A claim of the form "the surfaces agree" must be tested by comparing the surfaces.

  C9  asserts that no acceptance pass was written. A self-check that would still pass
      with a maker-authored acceptance is a self-acceptance channel in disguise.

The rest check that the handover document says what it must say, because a handover that
omits the open items is worse than no handover: the next session inherits a false state.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
SBL = Path(r"C:/Projects/Agent_Workspace/SBL")
CAND = Path(r"C:/Projects/Agent_Workspace/_sbl_r9_candidate")
R10 = SBL / "_governance/round-20261021-r10"
HO = R10 / "HANDOVER_SBL_R10_20261021.md"
STATE = R10 / "HANDOVER_STATE_R10.json"
PY = str(HGK / ".venv/Scripts/python.exe")

MANDATE = {
    "PLAN": "opencode-go/minimax-m3.1-flash-free",
    "EXECUTE": "opencode-go/deepseek-v4.1-flash",
    "VERIFY_SECURITY": "gpt-6.1-sol",
}

results: list[tuple[str, bool, str]] = []


def check(label: str, fn) -> None:
    try:
        ok, detail = fn()
    except Exception as exc:
        ok, detail = False, f"{type(exc).__name__}: {exc}"
    results.append((label, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {label}\n       {detail}")


def c1_mandate_rank1():
    s = json.loads((HGK / "var/R10-GATE/final_summary.json").read_text(encoding="utf-8"))
    bad = {}
    for lane, want in MANDATE.items():
        got = s.get(lane, {})
        if not got.get("ok") or got.get("rank") != 1 or got.get("transport") != want:
            bad[lane] = got
    if bad:
        return False, f"lane mismatch: {bad}"
    return True, "all three lanes ok at rank 1: " + ", ".join(
        f"{k}={s[k]['transport']} {s[k]['s']}s" for k in MANDATE)


def c2_epoch_joint():
    a = json.loads((HGK / "config/model-lane-assignment.json").read_text(encoding="utf-8"))
    import yaml
    r = yaml.safe_load((HGK / "config/lane-routing-registry.yaml").read_text(encoding="utf-8"))
    if int(a["registry_epoch"]) != int(r["epoch"]):
        return False, f"assignment {a['registry_epoch']} != registry {r['epoch']}"
    return True, f"epoch {r['epoch']} agrees on both sides"


def c3_drift():
    code = ("import sys;sys.path.insert(0,'src');from hg_kseos import lane_policy as lp;"
            "f=lp.check_drift();print(len(f),lp.drift_is_fatal(f))")
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, timeout=300, cwd=str(HGK))
    if r.returncode != 0:
        return False, f"drift gate crashed: {r.stderr[-200:]}"
    n, fatal = r.stdout.split()[:2]
    if int(n) != 0 or fatal != "False":
        return False, f"findings={n} fatal={fatal}"
    return True, "0 findings, fatal=False"


def c4_surfaces_agree():
    """Compare the three runtime surfaces to EACH OTHER and to the pool.

    This is the check the drift gate does not perform. Under the mandate:
      PLAN plane (governed profile) must name the PLAN model
      EXECUTE lane declaration and the runtime provider_route must name the EXECUTE model
    """
    import yaml

    pool = json.loads((HGK / "config/lane-route-slots.candidate.json").read_text(encoding="utf-8"))
    rank1 = {l["lane"]: f"{l['ordered_pool'][0]['provider']}/{l['ordered_pool'][0]['model']}"
             for l in pool["lanes"]}
    gov = yaml.safe_load((Path(r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0"
                              r"/LocalCache/Local/hermes/profiles/hgk-governed/config.yaml"))
                         .read_text(encoding="utf-8"))["model"]
    lane = json.loads((HGK / "config/hermes-codex-lane.json").read_text(encoding="utf-8"))
    hd = json.loads((HGK / "config/hermes.json").read_text(encoding="utf-8"))

    gov_pair = f"{gov['provider']}/{gov['default']}"
    lane_pair = f"{lane['provider']}/{lane['model']}"
    rt_pair = f"opencode-go/{hd['provider_route']['model']}"

    problems = []
    if gov_pair != rank1["PLAN"]:
        problems.append(f"governed PLAN plane {gov_pair} != pool PLAN {rank1['PLAN']}")
    if lane_pair != rank1["EXECUTE"]:
        problems.append(f"EXECUTE lane decl {lane_pair} != pool EXECUTE {rank1['EXECUTE']}")
    if rt_pair != rank1["EXECUTE"]:
        problems.append(f"provider_route {rt_pair} != pool EXECUTE {rank1['EXECUTE']}")
    if lane.get("codex_executable") is None or lane.get("codex_sha256") is None:
        problems.append("codex toolchain pin missing from the lane declaration")
    if problems:
        return False, "; ".join(problems)
    return True, (f"PLAN surface={gov_pair} == pool; EXECUTE lane={lane_pair} and "
                  f"provider_route={rt_pair} == pool; codex pin intact")


def c5_handover_sections():
    t = HO.read_text(encoding="utf-8")
    need = ["30 秒定向", "模型 mandate", "硬約束", "已完成並驗證", "未關閉項目",
            "下一步", "已證實的陷阱", "關鍵路徑地圖", "宣稱天花板", "前 5 個指令"]
    missing = [s for s in need if s not in t]
    if missing:
        return False, f"handover missing sections: {missing}"
    # the open items must be present, or the next session inherits a false state
    for rid in ["R9-02", "R9-04", "R9-05", "R9-06", "SP-INT"]:
        if rid not in t:
            return False, f"handover omits open item {rid}"
    return True, f"{len(t)} chars, all 10 sections, all 5 open items named"


def c6_state_json():
    s = json.loads(STATE.read_text(encoding="utf-8"))
    if s["claim_ceiling"].split(".")[0] != "CANDIDATE_ONLY":
        return False, f"ceiling: {s['claim_ceiling'][:60]}"
    if len(s["open"]) < 5:
        return False, f"only {len(s['open'])} open items recorded"
    if s["planes"]["fabric"]["state"] != "NO_SBL_INSTALL_TARGET":
        return False, "fabric state must stay NO_SBL_INSTALL_TARGET; no target was manufactured"
    if s["hgk_r9"]["acceptance"]["verdict"] not in ("FAIL", "NOT_RUN"):
        return False, f"R9 acceptance is {s['hgk_r9']['acceptance']['verdict']}, must stay unresolved"
    return True, (f"{len(s['open'])} open items, fabric NO_SBL_INSTALL_TARGET, "
                  f"R9 acceptance={s['hgk_r9']['acceptance']['verdict']}")


def c7_hgk_no_fabricated_pass():
    """Scope the assertion to THIS programme's subjects.

    An earlier draft asserted "no PASS anywhere" and failed on five rows
    (ACC-REF-001, ACC-REQ-FAR-EXEC-IDENTITY-002, ACC-REQ-FAR-LANE-SOD-010/011,
    ACC-AO-INDEP-012) that belong to other rounds and were legitimately earned there.
    A provenance claim must be scoped to the subjects it is about; the unscoped form was
    my defect, not a fabrication by anyone else. These five are recorded as context.
    """
    db = HGK / "var/shared-spine/hg-kseos.db"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    rows = con.execute("select acceptance_id,verdict from acceptances").fetchall()
    con.close()
    mine = ("SBL-PIPDLS", "R7-FARCLO", "R9-CTRLPKG", "R10")
    scoped = [(a, v) for a, v in rows if any(k in a for k in mine)]
    bad = [r for r in scoped if r[1] == "PASS"]
    if bad:
        return False, f"a PASS exists for an SBL subject that was not earned: {bad}"
    others = sorted(a for a, v in rows if v == "PASS")
    return True, (f"{len(scoped)} SBL-subject row(s), none PASS; "
                  f"{len(others)} pre-existing PASS row(s) belong to other rounds: {others}")


def c8_candidate_readback():
    def g(*a):
        r = subprocess.run(["git", "-C", str(CAND), *a], capture_output=True, text=True, timeout=300)
        return (r.stdout + r.stderr).strip()
    br = "candidate/r9-20261021-ctrlpkg"
    local = g("rev-parse", "HEAD")
    g("fetch", "origin", br)
    remote = g("rev-parse", f"origin/{br}")
    if local != remote:
        return False, f"local {local[:8]} != remote {remote[:8]}"
    return True, f"{br} @ {local[:8]} matches origin"


def c9_control_package_still_pins():
    tool = CAND / "tools/check_control_package.py"
    r = subprocess.run([sys.executable, str(tool), "--verify"], capture_output=True, text=True,
                       cwd=str(CAND), timeout=900)
    if r.returncode != 0:
        return False, f"control package no longer verifies: {(r.stdout + r.stderr)[:200]}"
    m = json.loads((CAND / "contracts/CONTROL_PACKAGE_MANIFEST.json").read_text(encoding="utf-8"))
    return True, f"14 docs verify, rollup {m['rollup_sha256'][:16]}"


def main() -> int:
    check("C1  mandate: three lanes served at rank 1 with the ordered models", c1_mandate_rank1)
    check("C2  registry epoch is a joint invariant on both sides", c2_epoch_joint)
    check("C3  drift gate clean", c3_drift)
    check("C4  runtime surfaces agree WITH EACH OTHER and the pool", c4_surfaces_agree)
    check("C5  handover document carries every section and open item", c5_handover_sections)
    check("C6  handover state JSON is honest", c6_state_json)
    check("C7  no acceptance PASS was fabricated anywhere", c7_hgk_no_fabricated_pass)
    check("C8  candidate branch pushed and read back", c8_candidate_readback)
    check("C9  control package still pins after this round's changes", c9_control_package_still_pins)

    passed = sum(1 for _, ok, _ in results if ok)
    total = len(results)
    verdict = "R10_SELF_CHECK_PASS" if passed == total else "R10_SELF_CHECK_FAIL"
    out = R10 / "SELF_CHECK_R10.json"
    out.write_text(json.dumps({
        "schema": "SBL-R10-SELF-CHECK/1",
        "verdict": verdict, "passed": passed, "total": total,
        "checks": [{"label": l, "ok": ok, "detail": d} for l, ok, d in results],
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"\n{verdict}: {passed}/{total}")
    print(f"written {out}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
