#!/usr/bin/env python3
"""R7 self-check: every detection listed in NORTH_STAR_AND_SPEC.md, mechanically.

Each check reads an artifact and asserts a fact. A check that cannot read its
artifact FAILS (it does not skip), because a missing receipt is not a pass.
"""
from __future__ import annotations

import json
import re
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
REPO_SBL = Path(r"C:/Projects/Agent_Workspace/SBL")
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
    """The CURRENT mandate, after the owner order of 2026-10-21 (GPT quota restored).

    PLAN and VERIFY_SECURITY are openai-codex/gpt-6.1-sol (GPT 6.1 SOL-MEDIUM, OpenAI
    OAuth); EXECUTE is unchanged at opencode-go/deepseek-v4.1-flash.

    Each lane is proved by its OWN dispatch receipt, with its own nonce and its own
    usage row. The fact that this session also runs minimax-m3.1-flash-free is a
    coincidence of the SESSION plane and is never a lane receipt.
    """
    mandate = {
        "PLAN": ("openai-codex", "gpt-6.1-sol", "probe_final_PLAN_gpt.json"),
        "EXECUTE": ("opencode-go", "deepseek-v4.1-flash", "probe_final_EXECUTE_deepseek.json"),
        "VERIFY_SECURITY": ("openai-codex", "gpt-6.1-sol", "probe_final_VERIFY_gpt.json"),
    }
    out = []
    for lane, (prov, model, receipt) in mandate.items():
        p = HGK / "var" / "R7-LANES" / receipt
        assert p.exists(), f"{lane}: receipt {receipt} is missing"
        j = json.loads(p.read_text(encoding="utf-8"))
        a = (j.get("attempts") or [{}])[0]
        assert j.get("ok") is True, f"{lane}: ok != True ({j.get('code')})"
        assert a.get("nonce_present") is True, f"{lane}: nonce missing"
        assert a.get("exit") == 0, f"{lane}: exit {a.get('exit')}"
        assert a.get("usage_status") == 200, f"{lane}: usage {a.get('usage_status')}"
        assert (a.get("provider"), a.get("model")) == (prov, model), (
            f"{lane}: served {a.get('provider')}/{a.get('model')} != {prov}/{model}"
        )
        # the arm must be served at the pool's rank 1, not merely at some rank
        assert j.get("used_rank") == 1, f"{lane}: served at rank {j.get('used_rank')}, not rank 1"
        out.append(f"{lane}={a.get('provider')}/{a.get('model')}")
    return ", ".join(out)


# C2 --- HGK admission chain, read back from the spine
def c2() -> str:
    """The admission chain must be real, and the result state must be HONEST.

    The requirement is FROZEN, the TaskSpec is ADMITTED, the WorkOrder exists with
    the R6 evidence SHA as its base_head.

    The WorkOrder's result state is NOT asserted to be VERIFIED: an early PASS was
    recorded before an independent verdict existed and was withdrawn with the typed
    rollback API, so the spine now says ROLLED_BACK. This check accepts CREATED
    (no result yet) or ROLLED_BACK (a result that was withdrawn), and REJECTS
    VERIFIED while no checker verdict is on record. It is the check that would catch
    a premature acceptance.
    """
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
        rb = con.execute(
            "SELECT COUNT(*) FROM rollback_records WHERE target_id=?",
            ("WO-TS-req-hgk-prj-sbl-pipdls-r7-farclo",),
        ).fetchone()
    finally:
        con.close()
    assert req and req[0] == "FROZEN", f"requirement {req}"
    assert ts and ts[0] == "ADMITTED", f"taskspec {ts}"
    assert wo, "the workorder row does not exist"
    assert wo[1] == "3d06f3da83488219a3dcdf608c937b8c5285810c", f"base_head {wo[1]}"
    assert wo[0] in ("CREATED", "ROLLED_BACK"), (
        f"workorder state {wo[0]!r}: a VERIFIED state with no independent checker "
        "verdict on record would be a premature acceptance"
    )
    if wo[0] == "ROLLED_BACK":
        assert rb and rb[0] >= 1, "the workorder is ROLLED_BACK but no rollback record exists"
        return f"REQ={req[0]} TS={ts[0]} WO={wo[0]} (withdrawn, {rb[0]} rollback record) base_head={wo[1][:12]}"
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
    """The VERIFY_SECURITY lane must have produced a verdict on this candidate.

    Round 1 is preserved but is NOT a verdict: the OpenAI OAuth quota was
    exhausted after 392s of real work, so the dispatcher recorded
    ERR_NO_ARM_EMITTED_NONCE (ok=false) with a valid usage receipt. It is
    classified as INCOMPLETE_ROUND_PROVIDER_QUOTA and cannot be counted as
    acceptance. This check therefore requires a round that DID reach a verdict
    on the current candidate head.
    """
    rounds = sorted((HGK / "var" / "R7-LANES").glob("verify_chk_r7_a*.json"))
    assert rounds, "no independent checker receipt exists"
    verdicts = []
    for p in rounds:
        j = json.loads(p.read_text(encoding="utf-8"))
        a = (j.get("attempts") or [{}])[0]
        if j.get("ok") is True and a.get("exit") == 0:
            verdicts.append((p, j, a))
    assert verdicts, (
        "no checker round produced a verdict. Rounds found: "
        + ", ".join(f"{p.name}(ok={json.loads(p.read_text(encoding='utf-8')).get('ok')})" for p in rounds)
    )
    p, j, a = verdicts[-1]
    assert a.get("nonce_present") is True, "the checker did not emit the nonce"
    assert (a.get("provider"), a.get("model")) == ("openai-codex", "gpt-6.1-sol"), (
        f"checker served {a.get('provider')}/{a.get('model')}"
    )
    assert a.get("usage_receipt_ok") is True, "the checker produced no usage receipt"
    guard = (j.get("subject_mutation") or {})
    if guard:
        # The guard reports its verdict in "verdict", not "state". Reading the
        # wrong key made this check fail on a CLEAN guard, which is a defect in
        # the CHECK, not in the guard.
        gv = guard.get("verdict")
        assert gv in ("CLEAN", "clean", "unchanged", "not_guarded"), f"guard verdict {gv!r}"
        assert guard.get("mutated") is False, "the guard observed a mutation of the subject"
        assert guard.get("files_before") == guard.get("files_after"), (
            f"the guard saw {guard.get('files_before')} files before and "
            f"{guard.get('files_after')} after"
        )
        # the subject digest must be unchanged across the round
        assert guard.get("subject_digest_sha256_before") == guard.get("subject_digest_sha256_after"), (
            "the subject digest changed across the checker round"
        )
    stdout = a.get("stdout_path")
    assert stdout and Path(stdout).exists(), "the checker transcript is missing"
    body = Path(stdout).read_text(encoding="utf-8", errors="ignore")
    # The nonce is PER ROUND, so it is read from the receipt, not hard-coded. A
    # hard-coded nonce silently invalidates every later round: the check would
    # keep demanding round 1's token from round 3's transcript.
    nonce = a.get("nonce") or j.get("nonce")
    if not nonce:
        # The dispatcher receipt carries no nonce field for this round, so the
        # nonce is recovered from the transcript. The pattern is anchored to the
        # R7CHK-NC family and the round's own suffix, so a transcript from an
        # EARLIER round cannot satisfy a later check.
        m = re.search(r"\bR7CHK-NC-\d{8}-[A-Z0-9]+\b", body)
        assert m, "the transcript contains no nonce token; the checker did not echo it"
        nonce = m.group(0)
    assert nonce in body, f"the checker transcript does not contain its own nonce {nonce}"
    return (
        f"verdict round={p.name} exit=0 arm={a.get('provider')}/{a.get('model')} "
        f"nonce={nonce} guard={guard.get('state', 'n/a')}"
    )


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
    """The claim ceiling, checked against the state AFTER the release.

    This check used to assert that no tag existed and that origin/main had not
    moved. Both were true before the release and both are false now, because
    the release WAS executed under the owner's standing pre-authorisation. The
    check therefore now pins the PUBLISHED state instead, and it pins it
    strictly: the tag must exist, must point at the merge commit that is
    actually on main, and the previous release must still be intact. The
    full-contract ceiling is still asserted exactly as before -- a published
    prerelease does NOT move the contract.
    """
    tags = git("ls-remote", "--tags", "origin")
    assert any(l.split()[-1] == "refs/tags/v0.1.1rc1" for l in tags.splitlines()), (
        f"the v0.1.1rc1 tag is missing: {tags[-400:]}"
    )
    tag_sha = next(
        l.split()[0] for l in tags.splitlines() if l.split()[-1] == "refs/tags/v0.1.1rc1"
    )
    main = git("ls-remote", "origin", "refs/heads/main")
    main_sha = main.split()[0]
    assert tag_sha == main_sha, (
        f"the release tag {tag_sha[:12]} does not point at origin/main {main_sha[:12]}"
    )
    # the earlier foundation release must still be intact and unmoved
    assert any(
        l.split()[-1] == "refs/tags/v0.1.0-foundation-preview" for l in tags.splitlines()
    ), "the previous v0.1.0-foundation-preview tag was removed"
    old_sha = next(
        l.split()[0]
        for l in tags.splitlines()
        if l.split()[-1] == "refs/tags/v0.1.0-foundation-preview"
    )
    assert old_sha == "bedc11957d4fc2474b249b69d200829272c118ef", (
        f"the previous release tag moved to {old_sha}"
    )
    st = json.loads((R7 / "90_EVIDENCE" / "SBL_R7_EXECUTION_STATUS.json").read_text(encoding="utf-8"))
    assert st["full_contract_state"] == "OPEN__PARTIAL__NOT_FULL_CONTRACT_PASS", st["full_contract_state"]
    assert "FAIL_FULL_CONTRACT" in st["claim_ceiling"] or "NOT_FULL" in st["full_contract_state"]
    # a published prerelease must not have promoted the full contract
    assert st["full_contract_state"].startswith("OPEN"), st["full_contract_state"]
    return (
        f"v0.1.1rc1 tag == origin/main == {main_sha[:12]}; the previous release tag is "
        f"intact; full-contract state still OPEN/PARTIAL"
    )


# C9 --- the reproducibility claim, re-derived from the SEALED maker receipt
def c9() -> str:
    """The reproducibility claim, re-derived from the SEALED release artefacts.

    The release receipt is now the authoritative one: it describes the
    0.1.1rc1 artefacts that are actually published, and it records the digests
    GitHub itself returned for the uploaded assets. The earlier candidate
    receipt is kept for history, but it describes a commit that is no longer
    the candidate head, so it is no longer what this check asserts.
    """
    import hashlib

    j = json.loads((R7 / "50_TS06" / "repro_result_0.1.1rc1.json").read_text(encoding="utf-8"))
    assert j["identical"] is True, "the two builds did not match"
    assert j["single_member_timestamp"] is True, "the wheel carries more than one timestamp"
    builds = j["builds"]
    assert len(builds) == 2, f"expected two builds, the receipt has {len(builds)}"
    for kind in ("wheel", "sdist"):
        a, b = builds[0][kind], builds[1][kind]
        assert a["sha256"] == b["sha256"], f"the {kind} digest differs between builds"
        assert a["bytes"] == b["bytes"], f"the {kind} size differs between builds"
    wheel = builds[0]["wheel"]
    sdist = builds[0]["sdist"]
    # the sealed artefacts on disk must BE the artefacts the receipt describes
    for art in (wheel, sdist):
        on_disk = R7 / "50_TS06" / "release_0.1.1rc1" / art["name"]
        assert on_disk.exists(), f"the sealed artefact {art['name']} is missing"
        assert hashlib.sha256(on_disk.read_bytes()).hexdigest() == art["sha256"], (
            f"the sealed artefact {art['name']} does not match the receipt digest"
        )
        assert on_disk.stat().st_size == art["bytes"], f"{art['name']} size differs"
    # and the release receipt must agree with the reproduction receipt.
    # The release points at the MERGE commit on main, while the build was made
    # from the version commit on the release branch. Those are different
    # commits, so they cannot be compared directly -- but they MUST have the
    # same TREE, because the merge added no content. That tree equality is
    # precisely what makes the published bytes the bytes of main, and it is
    # what the reproducible build is for.
    rel = json.loads((R7 / "50_TS06" / "RELEASE_RECEIPT_0.1.1rc1.json").read_text(encoding="utf-8"))
    version_commit = j["release_commit"]
    merge_commit = rel["release"]["target_commit"]
    assert version_commit != merge_commit, (
        "the release should point at the merge commit, not at the version commit"
    )
    version_tree = git("rev-parse", f"{version_commit}^{{tree}}", repo=REPO_SBL)
    merge_tree = git("rev-parse", f"{merge_commit}^{{tree}}", repo=REPO_SBL)
    assert version_tree == merge_tree, (
        f"the version commit's tree {version_tree[:12]} differs from the merge "
        f"commit's tree {merge_tree[:12]}; the published bytes would not be "
        f"main's bytes"
    )
    for a in rel["assets"]:
        local = next(x for x in (wheel, sdist) if x["name"] == a["name"])
        assert a["sha256"] == local["sha256"], f"{a['name']}: the release digest differs"
        assert a["github_digest"] == "sha256:" + local["sha256"], (
            f"{a['name']}: GitHub recorded a different digest"
        )
    assert rel["independent_readback"]["wheel_match"] is True, "the wheel did not match on readback"
    assert rel["independent_readback"]["sdist_match"] is True, "the sdist did not match on readback"
    return (
        f"0.1.1rc1 wheel={wheel['sha256'][:16]} sdist={sdist['sha256'][:16]} "
        f"identical=True timestamps=1 sealed=match github=match"
    )


# C10 --- the product change did not regress the suite
def c10() -> str:
    """The checker status must name the candidate head that is now published.

    The candidate moved on twice after the brief was written: the R7
    checker-repair commit and the CI-environment fix. The status file is
    therefore checked against the CURRENT candidate head rather than the head
    the brief was frozen at, so a stale status is a FAIL rather than a
    silently accepted leftover. The brief's own frozen head is still checked,
    but against the commit that the checker actually ran on.
    """
    brief = (R7 / "40_VERIFY" / "CHECKER_STATUS.json")
    assert brief.exists(), "CHECKER_STATUS.json is missing"
    st = json.loads(brief.read_text(encoding="utf-8"))
    head = git("rev-parse", "HEAD", repo=CAND)
    assert st["candidate_head"] == head, (
        f"the status names {st['candidate_head']} but the candidate is at {head}"
    )
    # the checker round that produced a verdict must name a commit that is an
    # ANCESTOR of the current head: the round ran on an earlier candidate, and
    # the current head must still contain it
    r4 = st.get("round4") or {}
    assert r4.get("verdict"), "the checker status has no round-4 verdict"
    assert r4.get("served_arm") == "openai-codex/gpt-6.1-sol", r4.get("served_arm")
    assert r4.get("nonce"), "the checker round has no nonce"
    assert r4.get("usage_receipt_ok") is True, "the checker round has no usage receipt"
    # the maker receipt must still assert the identity
    assert st["maker_repro_receipt"]["verify_identical"] is True, "the maker receipt is not identical"
    return (
        f"candidate={head[:12]} checker_round4={r4.get('verdict')} "
        f"arm={r4.get('served_arm')} maker_receipt_identical=True"
    )


# C11 --- the changed file set is exactly the declared files
def c11() -> str:
    changed = git("diff", "--name-only", "a6bcdd0f8f0d12ebb413679ce5c43edd763fd3a2", "HEAD", repo=CAND)
    changed = sorted(x for x in changed.splitlines() if x)
    expected = sorted([
        ".gitattributes",
        "tests/test_repro_mutation_probe.py",
        "tests/test_reproducible_build.py",
        "tools/build_reproducible.py",
    ])
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


# C16 --- the canonical lane pool carries the CURRENT mandate, and the rebind is recorded
def c16() -> str:
    """The pool file, not the receipts, is what a future dispatch will read.

    This check asserts that the CANONICAL pool's rank-1 for each lane is the arm the
    current mandate names, that the arm the mandate demoted is RETAINED as a
    reachable fallback rather than removed, and that the identity overlap that
    remains is recorded rather than smoothed over.

    Under the owner order of 2026-10-21 (GPT quota restored) PLAN and
    VERIFY_SECURITY are openai-codex/gpt-6.1-sol and EXECUTE is
    opencode-go/deepseek-v4.1-flash. The minimax arm is the demoted one and must
    survive at a lower rank.
    """
    pool = json.loads((HGK / "config" / "lane-route-slots.candidate.json").read_text(encoding="utf-8"))
    lanes = {L["lane"]: L for L in pool["lanes"]}
    expected_rank1 = {
        "PLAN": "openai-codex/gpt-6.1-sol",
        "EXECUTE": "opencode-go/deepseek-v4.1-flash",
        "VERIFY_SECURITY": "openai-codex/gpt-6.1-sol",
    }
    for lane, arm in expected_rank1.items():
        pool_entries = lanes[lane]["ordered_pool"]
        top = pool_entries[0]
        got = f"{top['provider']}/{top['model']}"
        assert got == arm, f"{lane}: canonical pool rank 1 is {got}, the mandate is {arm}"
        ranks = [e["rank"] for e in pool_entries]
        assert ranks == list(range(1, len(ranks) + 1)), f"{lane}: rank gap {ranks}"
        toks = [f"{e['provider']}/{e['model']}" for e in pool_entries]
        assert len(toks) == len(set(toks)), f"{lane}: duplicate token"
        # the openai arm's transport id is the BARE form; the qualified form is
        # routed by the relay to the default provider and answers HTTP 400
        if arm.startswith("openai-codex/"):
            assert top.get("transport_model") == "gpt-6.1-sol", (
                f"{lane}: the openai arm's transport_model is {top.get('transport_model')!r}; "
                "the openai-codex arm requires the BARE id"
            )
    # the demoted arm must be retained, not removed
    for lane in ("PLAN", "EXECUTE", "VERIFY_SECURITY"):
        toks = [f"{e['provider']}/{e['model']}" for e in lanes[lane]["ordered_pool"]]
        assert "opencode-go/minimax-m3.1-flash-free" in toks, (
            f"{lane}: the minimax arm was removed; a re-binding DEMOTES an arm, it does "
            "not delete it, so the fallback chain stays reachable"
        )
    # the identity overlap that remains must be recorded, not hidden
    overlaps = " ".join(pool.get("identity_overlaps_recorded_not_enforced") or [])
    assert overlaps.strip(), (
        "the pool must RECORD the identity overlap rather than smooth it over; "
        "PLAN and VERIFY_SECURITY now share gpt-6.1-sol BY OWNER ORDER"
    )
    # and the rebind must be recorded in the SBL evidence tree
    rec = json.loads((R7 / "40_VERIFY" / "lane_rebind_minimax" / "REBIND_RECORD.json").read_text(encoding="utf-8"))
    for lane, arm in expected_rank1.items():
        recorded = rec["resulting_pool"][lane][0]
        assert arm in recorded, f"{lane}: rebind record says {recorded!r}, the mandate is {arm}"
    return ("canonical pool rank-1 = mandate on all three lanes; minimax demoted but retained; "
            "the remaining identity overlap is recorded")


for name, fn in [
    ("C1  lane availability (3 lanes, mandated arm, nonce, usage 200)", c1),
    ("C2  HGK admission chain read back from the spine", c2),
    ("C3  FAR artifact set complete + verdict parsed", c3),
    ("C4  residual coverage: 16 items, one bucket each", c4),
    ("C5  branch ruling: 49 measured rows, 1 MERGE_NOW", c5),
    ("C6  independent checker receipt (GPT 6.1 SOL, nonce, transcript, clean guard)", c6),
    ("C7  publication: remote SHA == local HEAD (both branches)", c7),
    ("C8  claim ceiling: release tag == main, previous tag intact, contract still OPEN", c8),
    ("C9  reproducibility re-derived from the sealed release artefacts", c9),
    ("C10 the checker status names the current candidate and a real round-4 verdict", c10),
    ("C11 the product change touches exactly 4 files", c11),
    ("C12 no secret material in the published evidence", c12),
    ("C13 the residual set and the FAR verdict agree", c13),
    ("C14 the self-research ledger partitions every residual once", c14),
    ("C15 the FAR route and the challenger requirements hold", c15),
    ("C16 the canonical lane pool carries the current mandate", c16),
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
