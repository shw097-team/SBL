"""R26/L1 — build L1_RESULT.json from executed commands only.

Every row here is produced by running the command in this process and reading back its exit code and
stdout; nothing is typed in. Logs are written under evidence/L1/ and hashed after the run.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-quorum/evidence/fhs-w0-r26-repair-20261109"
WT = "C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-quorum"
PY = sys.executable
VQ = os.path.join(ROUND, "tools", "verify_quorum.py")


def sha(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run(name: str, argv: list, cwd: str, shell_cmd: str = None) -> dict:
    log = os.path.join(HERE, name)
    if shell_cmd:
        p = subprocess.run(["bash", "-lc", shell_cmd], cwd=cwd, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
    else:
        p = subprocess.run(argv, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace")
    body = p.stdout + (("\n--- stderr ---\n" + p.stderr) if p.stderr.strip() else "")
    with open(log, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    return {"cmd": shell_cmd or " ".join(_q(a) for a in argv), "exit": p.returncode,
            "log": os.path.relpath(log, HERE).replace(os.sep, "/"), "log_sha256": sha(log),
            "stdout": p.stdout}


def _q(s: str) -> str:
    return s if (" " not in s and '"' not in s) else '"' + s + '"'


def first_fail(stdout: str):
    try:
        d = json.loads(stdout)
    except ValueError:
        return None, None
    if "findings" in d:
        f = (d.get("findings") or [{}])[0]
        return d.get("ok"), f.get("first_fail")
    return d.get("SELFTEST"), d.get("failed")


CI_STEPS = [
    ("r26 payload manifest resolves inside its own payload",
     [PY, "tools/verify_payload_manifest.py", "--root", "."]),
    ("r26 gate (payload profile, includes G29)",
     [PY, "tools/gate_r20.py", "--round", ".", "--profile", "payload", "--scope", "payload",
      "--skip-hygiene"]),
    ("r26 signed vote quorum (17 cases)", [PY, "tools/verify_quorum.py", "--selftest"]),
    ("r26 signed vote quorum scan (signed receipts, fail-closed)",
     [PY, "tools/verify_quorum.py", "--root", "."]),
    ("r26 checksums", ["sha256sum", "-c", "SHA256SUMS"]),
]


def replay_ci() -> dict:
    """Run each workflow step as its own child and record its real exit code."""
    log = os.path.join(HERE, "08_ci_steps.log")
    chunks, worst = [], 0
    for name, argv in CI_STEPS:
        p = subprocess.run(argv, cwd=ROUND, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        chunks.append(
            "=== STEP: %s\n=== CMD: %s\n%s%s=== EXIT: %d\n"
            % (name, " ".join(argv), p.stdout,
               ("--- stderr ---\n" + p.stderr if p.stderr.strip() else ""), p.returncode))
        worst = worst or p.returncode
    with open(log, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(chunks))
        fh.write("=== ALL_STEPS_EXIT: %d\n" % worst)
    return {"cmd": "replay of the 5 r26 workflow steps (see 08_replay_ci_steps.sh)", "exit": worst,
            "log": os.path.relpath(log, HERE).replace(os.sep, "/"), "log_sha256": sha(log),
            "stdout": "\n".join(chunks)}


def main() -> int:
    cmds, negatives = [], []

    # 1. baseline: the three false greens, reproduced against the pre-repair file
    cmds.append(run("01_false_green_BASELINE.log",
                    [PY, os.path.join(HERE, "repro_false_green.py"),
                     os.path.join(HERE, "verify_quorum.BASELINE.py")], HERE))

    # 2. selftest, 17 cases
    cmds.append(run("02_selftest.log", [PY, VQ, "--selftest"], ROUND))

    # 3. receipt scan over the round (fail-closed default)
    cmds.append(run("03_scan_round.log",
                    [PY, VQ, "--root", ".", "--json-out", os.path.join(HERE, "03_scan_round.json")], ROUND))

    # 4. mirrors, all cases in one child-process run
    cmds.append(run("04_negatives_repaired.log", [PY, os.path.join(HERE, "run_negatives.py")], HERE))

    # 5. the two real signed repairs, before/after, plus the GAP measurement
    cmds.append(run("05_real_repairs_eval.log", [PY, os.path.join(HERE, "eval_real_repairs.py")], HERE))

    # 6. round gate (payload profile, G29 included)
    cmds.append(run("06_gate_payload.log",
                    [PY, "tools/gate_r20.py", "--round", ".", "--profile", "payload",
                     "--scope", "payload", "--skip-hygiene"], ROUND))

    # 7. the reader-ACK consumer (records its own pre-existing environment refusal)
    cmds.append(run("07_reader_ack.log", [PY, "tools/verify_reader_ack.py"], ROUND))

    # 8. the workflow's five steps, replayed one child process at a time with per-step exit codes
    cmds.append(replay_ci())

    # 9. one child-process log per mirror (the per-case negatives)
    mirror = os.path.join(HERE, "mirror_neg")
    for cid in sorted(os.listdir(mirror)):
        root = os.path.join(mirror, cid)
        if not os.path.isdir(root):
            continue
        row = run("10_neg_%s.log" % cid, [PY, VQ, "--root", root, "--raw-root", root], ROUND)
        cmds.append(row)
        ok, ff = first_fail(row["stdout"])
        want = {"FG1_DICT_NO_BINDING": "MISSING_CANDIDATE_BINDING",
                "FG2_FABRICATED_RAW": "RAW_DIGEST_MISMATCH",
                "FG3_INT_ONE_VOTE": "VOTE_TYPE_INVALID",
                "FG4_PROCESS_DUP": "PROCESS_ID_DUPLICATE",
                "FG5_RAW_ABSENT": "RAW_EVIDENCE_UNREADABLE",
                "FG6_INT_ONE_VALUE": "VALUE_NOT_BOOLEAN",
                "POS_CONTROL": None}[cid]
        good = (row["exit"] == 0) if want is None else (ff == want and row["exit"] != 0)
        negatives.append({"id": cid, "expected_code": want, "observed_code": ff, "exit": row["exit"],
                          "ok_field": ok, "as_expected": good, "log": row["log"],
                          "log_sha256": row["log_sha256"]})

    selftest_rows = json.loads(open(os.path.join(HERE, "02_selftest.log"), encoding="utf-8").read())
    for r in selftest_rows["rows"]:
        negatives.append({"id": "selftest:" + r["case"], "expected_code": r["expected"],
                          "observed_code": r["got"], "exit": 0 if r["ok"] else 5,
                          "ok_field": r["ok"], "as_expected": r["ok"], "log": "02_selftest.log",
                          "log_sha256": cmds[1]["log_sha256"]})

    changed = subprocess.run(["git", "show", "--name-only", "--pretty=format:", "HEAD"], cwd=WT,
                             capture_output=True, text=True).stdout.split()
    scan = json.loads(open(os.path.join(HERE, "03_scan_round.json"), encoding="utf-8").read())
    gate = open(os.path.join(HERE, "06_gate_payload.log"), encoding="utf-8").read()
    verdict = next((ln for ln in gate.splitlines() if ln.startswith("VERDICT")), "")
    real = json.loads(open(os.path.join(HERE, "05_real_repairs_eval.log"), encoding="utf-8").read())

    result = {
        "lane": "L1",
        "status": "PASS" if all(n["as_expected"] for n in negatives) and scan["ok"] else "PARTIAL",
        "changed_files": changed,
        "file_digests": {f: sha(os.path.join(WT, f)) for f in changed},
        "commit": subprocess.run(["git", "rev-parse", "HEAD"], cwd=WT, capture_output=True,
                                 text=True).stdout.strip(),
        "branch": subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=WT,
                                 capture_output=True, text=True).stdout.strip(),
        "commands": [{k: c[k] for k in ("cmd", "exit", "log", "log_sha256")} for c in cmds],
        "negatives": negatives,
        "scan": {k: scan[k] for k in ("receipts", "properties_checked", "repair_properties",
                                      "legacy_properties", "findings", "ok")},
        "gate_verdict": verdict,
        "real_repairs": [{"clause_id": r["clause_id"], "property": r["property"],
                          "baseline": r["baseline"], "repaired_default": r["repaired_default"],
                          "binding_forms": sorted({b["form"] for b in (r["repaired_raw_bindings"] or [])}),
                          "provenance_binding_forms": sorted({b["form"] for b in
                                                              (r["repaired_provenance_raw_root"] or [])}),
                          "repaired_strict": r["repaired_strict"]} for r in real["rows"]],
        "gap_R26_01": real["gap"],
        "findings_closed": ["EC-R26-003", "R26-01"],
        "not_claimed": [
            "the 126 pre-repair properties whose countable source is the legacy `votes` dict are NOT held to the "
            "per-vote candidate binding: the repair-vote contract applies to `votes_r25` only (bounded scope, "
            "measured legacy_properties above); their typing is now exact (VOTE_TYPE_INVALID) but they still "
            "carry no per-vote candidate sha",
            "`session_id`/`process_id` are a --strict-only requirement (R26-01_GAP): measured 0/4 present on the "
            "two signed r25 repairs, so a hard requirement would refuse the round's own signed votes",
            "verify_reader_ack.py cannot run in this tree (lanes/CLAUSES.json is not shipped in the payload "
            "scope); its in-process evaluate() path was exercised directly instead (05 log, "
            "repaired_in_process_no_raw_root)",
            "no push, no PR, no merge: work exists only on r27/quorum-g29",
            "QUORUM_MIN (2) and the schema of signed files are unchanged",
            "the r25 round's own tools/verify_quorum.py is untouched; its CI step still runs 7 cases",
        ],
        "notes": "raw_sha256 in the two signed r25 repairs does not match the round's payload copy "
                 "(votes/raw_*.txt) byte for byte: measured 889f... vs 664147... for PLAN, and the pair differs "
                 "by 74 B across 167 lines, so it is not a line-ending twin. The declared digest is the digest "
                 "of the transcript where it was produced, and the payload MANIFEST declares exactly that pair "
                 "(sha256_as_measured / sha256). The repaired verifier therefore accepts the manifest-anchored "
                 "identity only when both sides re-hash, and still accepts exact bytes when --raw-root points "
                 "at lanes/votes/ (05 log, form raw_bytes).",
    }
    outdir = os.path.join(os.path.dirname(os.path.dirname(HERE)), "out")
    os.makedirs(outdir, exist_ok=True)
    for target in (os.path.join(outdir, "L1_RESULT.json"), os.path.join(HERE, "L1_RESULT.json")):
        with open(target, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(result, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "branch", "commit", "negatives_total_ok",
                                             "scan", "gate_verdict") if k in result}, indent=1))
    print("negatives:", sum(1 for n in negatives if n["as_expected"]), "/", len(negatives))
    print("written", os.path.join(HERE, "L1_RESULT.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
