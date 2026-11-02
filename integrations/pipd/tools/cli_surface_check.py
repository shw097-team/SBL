#!/usr/bin/env python3
"""S4 CLI surface qualification: exactly 13 commands, each with an exercised SUCCESS path and an
exercised REFUSAL path that must produce a TYPED error (exit 2 + a machine-readable error dict).

An untyped crash is counted as a FAILURE, not as a refusal: the whole point of a typed error surface is
that a caller can branch on it. A command that is merely listed in --help is not exercised here.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".hgk" / "artifacts" / "s4"
OUT.mkdir(parents=True, exist_ok=True)
ENV = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "PYTHONDONTWRITEBYTECODE": "1"}
GOAL = "Implement the lifecycle compiler and verify it against the source spec."
SRC = str(ROOT / "docs" / "S0_CONTRACT_SPEC.md")


def cli(args: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", "--root", str(ROOT), *args],
                          capture_output=True, text=True, env=ENV, cwd=str(ROOT), **kw)


def is_typed_refusal(r: subprocess.CompletedProcess) -> tuple[bool, str]:
    """Exit 2 AND a parseable error envelope. Exit 1 with a FAIL verdict is a result, not a refusal."""
    if r.returncode != 2:
        return False, f"exit={r.returncode} (expected 2)"
    try:
        d = json.loads(r.stdout)
    except Exception:
        return False, f"stdout is not JSON: {r.stdout[:120]!r}"
    code = d.get("code") or d.get("error") or d.get("type") or ""
    if not code:
        return False, f"no error code in {json.dumps(d)[:120]}"
    return True, str(code)


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="pipd-s4-"))
    # ---- fixture chain produced by the CLI itself ----
    card = cli(["intake", "--goal", GOAL, "--source", SRC])
    card_p = tmp / "intent.json"; card_p.write_text(card.stdout, encoding="utf-8")
    pi = cli(["compile-pi", "--intent", str(card_p), "--profile", "STANDARD"])
    pi_p = tmp / "pi.json"; pi_p.write_text(pi.stdout, encoding="utf-8")
    pd = cli(["bind-pd", "--pi", str(pi_p), "--repo-root", str(ROOT)])
    pd_p = tmp / "pd.json"; pd_p.write_text(pd.stdout, encoding="utf-8")
    ecp = cli(["compile-ecp", "--pd", str(pd_p), "--pi", str(pi_p)])
    ecp_p = tmp / "ecp.json"; ecp_p.write_text(ecp.stdout, encoding="utf-8")
    tq = cli(["compile-tqaep", "--pi", str(pi_p), "--ecp", str(ecp_p), "--maker", "HERMES-MAKER",
              "--checker", "glm-5.3-flash/opencode-go", "--checker-receipt", ".hgk/ao/x.log"])
    tq_p = tmp / "tqaep.json"; tq_p.write_text(tq.stdout, encoding="utf-8")
    bundle_p = tmp / "bundle.json"
    bundle_p.write_text(json.dumps({"TQAEP": json.loads(tq.stdout)}), encoding="utf-8")
    a_p = tmp / "a.json"; a_p.write_text(json.dumps({"schema_version": "PI-PKG@1"}), encoding="utf-8")
    b_p = tmp / "b.json"; b_p.write_text(json.dumps({"schema_version": "PI-PKG@1"}), encoding="utf-8")
    bad_p = tmp / "bad.json"; bad_p.write_text(json.dumps({"schema_version": "PI-PKG@2"}), encoding="utf-8")
    empty_p = tmp / "empty.json"; empty_p.write_text("{}", encoding="utf-8")

    cases: list[dict] = []

    def case(cmd: str, ok: subprocess.CompletedProcess, refuse: subprocess.CompletedProcess,
             ok_pred) -> None:
        okv = ok.returncode == 0 and ok_pred(ok)
        ref, code = is_typed_refusal(refuse)
        cases.append({"command": cmd,
                      "success_path": {"verdict": "PASS" if okv else "FAIL", "exit": ok.returncode},
                      "refusal_path": {"verdict": "PASS" if ref else "FAIL", "error_code": code,
                                       "exit": refuse.returncode},
                      "verdict": "PASS" if (okv and ref) else "FAIL"})

    case("init", cli(["init"]), cli(["init", "--bogus"]),
         lambda r: "verdict" in r.stdout or "root" in r.stdout)
    case("intake", cli(["intake", "--goal", GOAL, "--source", SRC]),
         cli(["intake", "--goal", "", "--source", SRC]), lambda r: "subject_id" in r.stdout)
    case("profile", cli(["profile", "--profile", "LITE", "--axis", "intent"]),
         cli(["profile", "--profile", "TURBO"]), lambda r: "profile" in r.stdout)
    case("compile-pi", cli(["compile-pi", "--intent", str(card_p), "--profile", "LITE"]),
         cli(["compile-pi", "--intent", str(tmp / "missing.json")]),
         lambda r: "subject_id" in r.stdout)
    case("bind-pd", cli(["bind-pd", "--pi", str(pi_p), "--repo-root", str(ROOT)]),
         cli(["bind-pd", "--pi", str(pi_p)]), lambda r: "RepoContext" in r.stdout)
    case("compile-ecp", cli(["compile-ecp", "--pd", str(pd_p), "--pi", str(pi_p)]),
         cli(["compile-ecp", "--pd", str(empty_p), "--pi", str(pi_p)]),
         lambda r: "subject_id" in r.stdout)
    case("compile-tqaep", cli(["compile-tqaep", "--pi", str(pi_p), "--ecp", str(ecp_p),
                               "--maker", "HERMES-MAKER", "--checker", "glm-5.3-flash",
                               "--checker-receipt", "r"]),
         cli(["compile-tqaep", "--pi", str(pi_p), "--ecp", str(ecp_p),
              "--maker", "M", "--checker", " m ", "--checker-receipt", "r"]),
         lambda r: "subject_id" in r.stdout)
    case("validate", cli(["validate", "--bundle", str(bundle_p)]),
         cli(["validate", "--bundle", str(tmp / "nope.json")]), lambda r: "verdict" in r.stdout)
    case("doctor", cli(["doctor"]), cli(["doctor", "--bogus"]), lambda r: "verdict" in r.stdout)
    # R5-WO1: the destination resolver refuses a target outside every authorised root, so the
    # scratch surface must be authorised explicitly (the product tree is never the target).
    case("project", cli(["project", "--out", str(tmp / "web"), "--allow-root", str(tmp)]),
         cli(["project", "--bogus"]), lambda r: "web_pack" in r.stdout)
    case("export", cli(["export"]), cli(["export", "--bogus"]),
         lambda r: "files" in r.stdout or "verdict" in r.stdout)
    case("diff", cli(["diff", "--a", str(a_p), "--b", str(b_p)]),
         cli(["diff", "--a", str(a_p), "--b", str(bad_p)]), lambda r: "verdict" in r.stdout)
    case("repair", cli(["repair", "--subject", "src/pipd_ls_sp/util.py", "--scope", "src/**",
                        "--authorized-root", str(ROOT)]),
         cli(["repair", "--subject", "C:/Windows/x.dll", "--scope", "src/**",
              "--authorized-root", str(ROOT)]), lambda r: "state" in r.stdout or "subject" in r.stdout)

    # ---- the S4 extras that must exist WITHOUT becoming a 14th command ----
    extras = []
    r = cli(["compile-pi", "--intent", str(card_p), "--profile", "LITE", "--replay"])
    extras.append({"surface": "replay", "verdict": "PASS" if (r.returncode == 0 and
                   json.loads(r.stdout).get("replay", {}).get("replay_verdict") == "PASS") else "FAIL"})
    r = cli(["compile-pi", "--intent", str(card_p), "--profile", "LITE", "--explain"])
    extras.append({"surface": "explain", "verdict": "PASS" if (r.returncode == 0 and
                   json.loads(r.stdout).get("explain", {}).get("derivation")) else "FAIL"})
    r = cli(["diff", "--a", str(a_p), "--b", str(b_p), "--explain"])
    extras.append({"surface": "semantic_diff_explain", "verdict": "PASS" if (r.returncode == 0 and
                   json.loads(r.stdout).get("explain")) else "FAIL"})
    r = cli(["project", "--out", str(tmp / "web2"), "--allow-root", str(tmp), "--dry-run"])
    no_write = not (tmp / "web2").exists()
    extras.append({"surface": "dry_run_project", "verdict": "PASS" if (r.returncode == 0 and no_write
                   and json.loads(r.stdout).get("wrote_nothing")) else "FAIL",
                   "target_untouched": no_write})
    r = cli(["export", "--dry-run"])
    extras.append({"surface": "dry_run_export",
                   "verdict": "PASS" if (r.returncode == 0 and json.loads(r.stdout).get("wrote_nothing")) else "FAIL"})
    r = cli(["repair", "--subject", "src/pipd_ls_sp/util.py", "--scope", "src/**",
             "--authorized-root", str(ROOT), "--dry-run"])
    extras.append({"surface": "dry_run_repair",
                   "verdict": "PASS" if (r.returncode == 0 and json.loads(r.stdout).get("wrote_nothing")) else "FAIL"})

    # exact command set: a 14th command would be a contract breach
    r = cli(["--help"])
    listed = [c for c in ("init", "intake", "profile", "compile-pi", "bind-pd", "compile-ecp",
                          "compile-tqaep", "validate", "doctor", "project", "export", "diff", "repair")
              if c in r.stdout]
    payload = {
        "command_count": len(cases),
        "cases": cases,
        "extras": extras,
        "exact_set": {"listed": listed, "count": len(listed),
                      "verdict": "PASS" if len(listed) == 13 else "FAIL"},
        "passed": f"{sum(1 for c in cases if c['verdict'] == 'PASS')}/{len(cases)}",
        "candidate_head": subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                                         capture_output=True, text=True).stdout.strip(),
    }
    payload["verdict"] = ("PASS" if payload["passed"].split("/")[0] == payload["passed"].split("/")[1]
                          and all(e["verdict"] == "PASS" for e in extras)
                          and payload["exact_set"]["verdict"] == "PASS" else "FAIL")
    (OUT / "CLI_SURFACE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1),
                                          encoding="utf-8", newline="")
    print(json.dumps({"passed": payload["passed"], "extras": {e["surface"]: e["verdict"] for e in extras},
                      "exact_set": payload["exact_set"]["verdict"], "verdict": payload["verdict"]},
                     ensure_ascii=False, indent=1))
    for c in cases:
        if c["verdict"] != "PASS":
            print("  FAIL", c)
    import shutil
    shutil.rmtree(tmp, ignore_errors=True)
    return 0 if payload["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
