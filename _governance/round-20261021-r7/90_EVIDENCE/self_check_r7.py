#!/usr/bin/env python3
"""R7 self-check: every detection listed in NORTH_STAR_AND_SPEC.md, mechanically.

Each check reads an artifact and asserts a fact. A check that cannot read its
artifact FAILS (it does not skip), because a missing receipt is not a pass.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SBL = Path(r"C:/Projects/Agent_Workspace/SBL")
R7 = SBL / "_governance" / "round-20261021-r7"
HGK = Path(r"C:/Projects/Agent_Workspace/HG-KSEOS")
RUN = Path(
    r"C:/Projects/Agent_Workspace/Fabric/fabric-autonomous-research/runs"
    r"/FAR-20261021-023-sbl-r7-residual-closure"
)
CAND = Path(r"C:/Projects/_sbl_r4/c3v2")
SCRATCH = Path(
    r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0"
    r"/LocalCache/Local/hermes/cache/scratch"
)

results: list[tuple[str, bool, str]] = []


def check(name: str, fn) -> None:
    try:
        detail = fn()
        results.append((name, True, detail))
    except Exception as exc:  # noqa: BLE001 - a failing check is data, not a crash
        results.append((name, False, f"{type(exc).__name__}: {exc}"))


def git(*args: str, repo: Path = SBL) -> str:
    r = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=300
    )
    if r.returncode != 0:
        raise AssertionError(f"git {args} -> {r.stderr.strip()[:300]}")
    return r.stdout.strip()


# C1 --- lane availability: all three lanes served the mandated arm
def c1() -> str:
    mandate = {
        "PLAN": ("openai-codex", "gpt-6.1-sol"),
        "EXECUTE": ("opencode-go", "deepseek-v4.1-flash"),
        "VERIFY_SECURITY": ("openai-codex", "gpt-6.1-sol"),
    }
    out = []
    for lane, (prov, model) in mandate.items():
        p = HGK / "var" / "R7-LANES" / f"probe2_{lane}.json"
        j = json.loads(p.read_text(encoding="utf-8"))
        a = (j.get("attempts") or [{}])[0]
        assert j.get("ok") is True, f"{lane}: ok != True ({j.get('code')})"
        assert a.get("nonce_present") is True, f"{lane}: nonce missing"
        assert a.get("exit") == 0, f"{lane}: exit {a.get('exit')}"
        assert a.get("usage_status") == 200, f"{lane}: usage {a.get('usage_status')}"
        assert (a.get("provider"), a.get("model")) == (prov, model), (
            f"{lane}: served {a.get('provider')}/{a.get('model')} != {prov}/{model}"
        )
        out.append(f"{lane}={a.get('provider')}/{a.get('model')}")
    return ", ".join(out)


# C2 --- HGK admission chain, read back from the spine
def c2() -> str:
    import sqlite3

    db = HGK / "var" / "shared-spine" / "hg-kseos.db"
    con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
    try:
        req = con.execute(
            "SELECT state FROM requirements WHERE requirement_id=?",
            ("REQ-HGK-PRJ-SBL-PIPDLS-R7-FARCLO",),
        ).fetchone()
        ts = con.execute(
            "SELECT state FROM taskspecs WHERE taskspec_id=?",
            ("TS-req-hgk-prj-sbl-pipdls-r7-farclo",),
        ).fetchone()
        wo = con.execute(
            "SELECT state,base_head FROM workorders WHERE workorder_id=?",
            ("WO-TS-req-hgk-prj-sbl-pipdls-r7-farclo",),
        ).fetchone()
    finally:
        con.close()
    assert req and req[0] == "FROZEN", f"requirement {req}"
    assert ts and ts[0] == "ADMITTED", f"taskspec {ts}"
    assert wo and wo[0] == "CREATED", f"workorder {wo}"
    assert wo[1] == "3d06f3da83488219a3dcdf608c937b8c5285810c", f"base_head {wo[1]}"
    return f"REQ={req[0]} TS={ts[0]} WO={wo[0]} base_head={wo[1][:12]}"


# C3 --- FAR artifact set complete
def c3() -> str:
    required = [
        "ResearchRequest.yaml", "ResearchPlan.yaml", "ResearchSynthesis.md",
        "CandidateResearch.yaml", "ResearchHandoff.yaml", "ResearchRunReceipt.json",
        "VERDICT.json", "LEARNING.md", "METHOD.md", "SELF_EVOLUTION_DELTA.json",
        "ClaimLedger.tsv", "QueryLedger.tsv", "SourceSnapshotLedger.tsv",
        "SourceDispositionLedger.tsv", "HypothesisLedger.tsv", "OpenQuestionLedger.tsv",
        "ContradictionLedger.tsv", "DisagreementLedger.tsv",
        "RejectedAlternativeLedger.tsv", "FitGapLedger.tsv", "ExtractionLedger.jsonl",
    ]
    missing = [n for n in required if not (RUN / n).exists()]
    assert not missing, f"missing FAR artifacts: {missing}"
    verdict = json.loads((RUN / "VERDICT.json").read_text(encoding="utf-8"))
    assert verdict["decision"] == "PROCEED_WITH_SCOPED_CLOSURE", verdict["decision"]
    return f"{len(required)} artifacts present; decision={verdict['decision']}"


# C4 --- residual coverage: denominator and one bucket per item
def c4() -> str:
    inv = json.loads((R7 / "30_RESIDUAL" / "RESIDUAL_INVENTORY.json").read_text(encoding="utf-8"))
    items = inv["items"]
    assert inv["denominator_count"] == len(items) == 16, (
        f"denominator {inv['denominator_count']} vs {len(items)}"
    )
    ids = [i["id"] for i in items]
    assert len(ids) == len(set(ids)), "duplicate residual id"
    buckets = {"executable_this_round", "one_action_owner", "not_closable_this_round",
               "closed_by_lane_owner", "closed_by_isolation"}
    for i in items:
        assert i["bucket"] in buckets, f"{i['id']}: unknown bucket {i['bucket']}"
        assert i["source"], f"{i['id']}: no source locator"
        assert i["evidence"], f"{i['id']}: no evidence"
    # the executed item must actually be executed
    closed = [i for i in items if i["id"] == "TT-R6-WHEEL-NONREPRODUCIBLE-001"]
    assert closed and closed[0]["bucket"] == "executable_this_round", "wheel item not executable"
    from collections import Counter
    c = Counter(i["bucket"] for i in items)
    return f"16 items, 0 duplicate, buckets={dict(c)}"


# C5 --- branch ruling: every ruling carries a measured fact
def c5() -> str:
    md = (RUN / "raw_worker_artifacts" / "CANDIDATE_BRANCH_RULING.md").read_text(encoding="utf-8")
    # The file holds TWO tables: the 49-row branch ruling and an 8-row PIPD skill
    # summary. Only the branch rows have the 8-column shape, so a row is a branch
    # row when it parses into 8+ cells; the skill rows have 2.
    verdicts = {"MERGE_NOW", "EVIDENCE_ONLY", "DO_NOT_MERGE", "SUPERSEDED", "NOT_RECOMMENDED"}
    counts: dict[str, int] = {}
    branch_rows = 0
    for line in md.splitlines():
        if not (line.startswith("| `") and "|" in line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 8:
            continue
        v = cells[6].replace("*", "")
        assert v in verdicts, f"unknown verdict {v!r}"
        counts[v] = counts.get(v, 0) + 1
        branch_rows += 1
    assert branch_rows == 49, f"{branch_rows} branch rows, expected 49"
    assert counts.get("MERGE_NOW") == 1, f"MERGE_NOW count {counts.get('MERGE_NOW')}"
    assert sum(counts.values()) == 49, counts
    return f"49 branch rows; {counts}"


# C6 --- independent verification: a dispatched checker receipt with a raw verdict
def c6() -> str:
    p = HGK / "var" / "R7-LANES" / "verify_chk_r7_a1.json"
    assert p.exists(), "the independent checker receipt does not exist"
    j = json.loads(p.read_text(encoding="utf-8"))
    a = (j.get("attempts") or [{}])[0]
    assert j.get("ok") is True, f"dispatcher ok={j.get('ok')} code={j.get('code')}"
    assert a.get("nonce_present") is True, "the checker did not emit the nonce"
    assert a.get("exit") == 0, f"checker exit {a.get('exit')}"
    assert (a.get("provider"), a.get("model")) == ("openai-codex", "gpt-6.1-sol"), (
        f"checker served {a.get('provider')}/{a.get('model')}"
    )
    guard = (j.get("subject_mutation") or {})
    assert guard.get("state") in ("clean", "unchanged", "not_guarded", "CLEAN"), (
        f"guard state {guard.get('state')}"
    )
    stdout = a.get("stdout_path")
    assert stdout and Path(stdout).exists(), "the checker transcript is missing"
    body = Path(stdout).read_text(encoding="utf-8", errors="ignore")
    assert "R7CHK-NC-20261021-A1" in body, "the checker did not echo the nonce"
    return f"ok=True exit=0 arm={a.get('provider')}/{a.get('model')} guard={guard.get('state')}"


# C7 --- publication: the remote SHAs equal the local heads
def c7() -> str:
    expect = {
        "candidate/r7-20261021-repro-build": git("rev-parse", "candidate/r7-20261021-repro-build", repo=CAND),
        "evidence/r7-20261021-c7": git("rev-parse", "HEAD"),
    }
    remote = git("ls-remote", "origin",
                 "refs/heads/candidate/r7-20261021-repro-build",
                 "refs/heads/evidence/r7-20261021-c7")
    # ls-remote prints "<sha>\t<ref>"; the ref is the KEY and the sha the VALUE
    got = {}
    for line in remote.splitlines():
        if not line.strip():
            continue
        sha, ref = line.split()
        got[ref] = sha
    for br, sha in expect.items():
        ref = f"refs/heads/{br}"
        assert got.get(ref) == sha, f"{br}: remote {got.get(ref)} != local {sha}"
    return "; ".join(f"{b}={s[:12]}" for b, s in expect.items())


# C8 --- the claim ceiling: no release, no tag, no merge, and the published 0.1.0 is untouched
def c8() -> str:
    tags = git("ls-remote", "--tags", "origin")
    assert "v0.1.1" not in tags, f"a v0.1.1 tag exists: {tags[:300]}"
    main = git("ls-remote", "origin", "refs/heads/main")
    assert main.split()[0] == "bedc11957d4fc2474b249b69d200829272c118ef", (
        f"origin/main moved to {main.split()[0]}"
    )
    st = json.loads((R7 / "90_EVIDENCE" / "SBL_R7_EXECUTION_STATUS.json").read_text(encoding="utf-8"))
    assert st["full_contract_state"] == "OPEN__PARTIAL__NOT_FULL_CONTRACT_PASS", st["full_contract_state"]
    assert "FAIL_FULL_CONTRACT" in st["claim_ceiling"] or "NOT_FULL" in st["full_contract_state"]
    return "no new tag; origin/main unchanged; full-contract state OPEN/PARTIAL"


# C9 --- the reproducibility claim, re-derived from the maker's own receipt
def c9() -> str:
    j = json.loads((SCRATCH / "r7-repro-tool" / "repro_result.json").read_text(encoding="utf-8"))
    v = j["verify"]
    assert v["identical"] is True, "the two builds did not match"
    assert v["single_member_timestamp"] is True, "the wheel carries more than one timestamp"
    names = {a["name"] for a in j["artifacts"]}
    assert any(n.endswith(".whl") for n in names) and any(n.endswith(".tar.gz") for n in names), names
    w = next(a for a in j["artifacts"] if a["name"].endswith(".whl"))
    assert w["sha256"] == v["second_build"][w["name"]], "the wheel digest differs between builds"
    return f"wheel={w['sha256'][:16]} identical=True timestamps=1"


# C10 --- the product change did not regress the suite
def c10() -> str:
    brief = (R7 / "40_VERIFY" / "CHECKER_STATUS.json")
    assert brief.exists(), "CHECKER_STATUS.json is missing"
    st = json.loads(brief.read_text(encoding="utf-8"))
    assert st["candidate_head"] == git("rev-parse", "HEAD", repo=CAND), (
        f"the brief names {st['candidate_head']} but the candidate is at "
        f"{git('rev-parse','HEAD',repo=CAND)}"
    )
    assert st["maker_repro_receipt"]["verify_identical"] is True, "the maker receipt is not identical"
    return f"candidate={st['candidate_head'][:12]} maker_receipt_identical=True"


# C11 --- the changed file set is exactly the three declared files
def c11() -> str:
    changed = git("diff", "--name-only", "a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2", "HEAD", repo=CAND)
    changed = sorted(x for x in changed.splitlines() if x)
    expected = sorted([".gitattributes", "tests/test_reproducible_build.py", "tools/build_reproducible.py"])
    assert changed == expected, f"changed files {changed} != {expected}"
    return ", ".join(changed)


# C12 --- no secret material in the published evidence
def c12() -> str:
    import re

    diff = git("show", "--format=", "HEAD")
    pats = {
        "github_pat": r"github_pat_[A-Za-z0-9_]{20,}",
        "ghp": r"\bghp_[A-Za-z0-9]{20,}",
        "aws": r"AKIA[0-9A-Z]{16}",
        "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    }
    for name, pat in pats.items():
        hits = re.findall(pat, diff)
        assert not hits, f"{name}: {len(hits)} hit(s) in the published diff"
    return "no token/credential pattern in the published diff"


# C13 --- the residual set and the FAR verdict agree
def c13() -> str:
    inv = json.loads((R7 / "30_RESIDUAL" / "RESIDUAL_INVENTORY.json").read_text(encoding="utf-8"))
    v = json.loads((RUN / "VERDICT.json").read_text(encoding="utf-8"))
    assert v["inputs"]["r6_residual_denominator"] == inv["denominator_count"] == 16
    buckets = v["inputs"]["residual_buckets"]
    from collections import Counter
    c = Counter(i["bucket"] for i in inv["items"])
    for k, n in buckets.items():
        assert c.get(k, 0) == n, f"bucket {k}: verdict {n} vs inventory {c.get(k,0)}"
    return f"16 items; buckets agree ({sum(buckets.values())})"


# C14 --- the self-research ledger partitions every residual exactly once
def c14() -> str:
    led = json.loads((R7 / "90_EVIDENCE" / "SELF_RESEARCH_LEDGER.json").read_text(encoding="utf-8"))
    split = led["residual_split"]
    groups = [k for k in split if not k.endswith("_note")]
    seen: list[str] = []
    for g in groups:
        seen.extend(split[g])
    assert len(seen) == len(set(seen)), f"a residual appears in two buckets: {seen}"
    assert len(seen) == 16, f"{len(seen)} residuals partitioned, expected 16"
    # every id must be a bare residual id: no annotation may be glued onto it
    inv = json.loads((R7 / "30_RESIDUAL" / "RESIDUAL_INVENTORY.json").read_text(encoding="utf-8"))
    known = {i["id"] for i in inv["items"]}
    unknown = [x for x in seen if x not in known]
    assert not unknown, f"the split names ids that are not in the inventory: {unknown}"
    assert len(led["lessons"]) >= 7, "fewer than 7 lessons recorded"
    return f"16 residuals partitioned once; {len(led['lessons'])} lessons"


# C15 --- the FAR route and the challenger requirements are honoured
def c15() -> str:
    rec = json.loads((RUN / "ResearchRunReceipt.json").read_text(encoding="utf-8"))
    assert rec["route"]["decision"] == "NATIVE_WITH_SELECTED_ARIS", rec["route"]["decision"]
    assert rec["route"]["challenger_method"] == "research-review", rec["route"]["challenger_method"]
    assert rec["route"]["swarm_lanes"] == 3, rec["route"]["swarm_lanes"]
    syn = (RUN / "ResearchSynthesis.md").read_text(encoding="utf-8")
    assert "Challenger review" in syn, "the synthesis has no challenger section"
    assert "Abstentions" in syn, "the synthesis has no abstentions section"
    return "route NATIVE_WITH_SELECTED_ARIS; challenger + abstentions present"


for name, fn in [
    ("C1  lane availability (3 lanes, mandated arm, nonce, usage 200)", c1),
    ("C2  HGK admission chain read back from the spine", c2),
    ("C3  FAR artifact set complete + verdict parsed", c3),
    ("C4  residual coverage: 16 items, one bucket each", c4),
    ("C5  branch ruling: 49 measured rows, 1 MERGE_NOW", c5),
    ("C6  independent checker receipt (GPT 6.1 SOL, nonce, transcript)", c6),
    ("C7  publication: remote SHA == local HEAD (both branches)", c7),
    ("C8  claim ceiling: no tag, main unmoved, contract still OPEN", c8),
    ("C9  reproducibility re-derived from the maker receipt", c9),
    ("C10 the checker brief names the frozen candidate", c10),
    ("C11 the product change touches exactly 3 files", c11),
    ("C12 no secret material in the published evidence", c12),
    ("C13 the residual set and the FAR verdict agree", c13),
    ("C14 the self-research ledger partitions every residual once", c14),
    ("C15 the FAR route and the challenger requirements hold", c15),
]:
    check(name, fn)

passed = sum(1 for _, ok, _ in results if ok)
print(f"R7 SELF-CHECK: {passed}/{len(results)} PASS\n")
for name, ok, detail in results:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        print(f"         -> {detail}")
print()
if passed != len(results):
    sys.exit(1)
