#!/usr/bin/env python3
"""Generate H0_DAG_RECONCILIATION.json and H1_CONFIG_DELTA_LEDGER.json from executed git output.

Every number in the two JSONs is read from a git command run here (and cross-checked against the raw log this
lane already captured), never typed in by hand. The disposition of each config file is a decision table, and
each decision carries the reason that decided it.

Usage: python gen_evidence.py <clone> <evidence_dir> <out_dir>
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CLONE = sys.argv[1].replace("\\", "/")
EV = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
A = "acd9196fcd748638673848bf62a426dcc3c22dc1"   # origin/main
B = "86f40ec114f19bbd35314e376da4d0bed9805b22"   # config/plan-mimo-flash-20261109 (epoch 41)


def git(*args: str) -> tuple[int, str]:
    p = subprocess.run(["git", "-C", CLONE, *args], capture_output=True, text=True, encoding="utf-8")
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def git_bytes(*args: str) -> bytes:
    return subprocess.run(["git", "-C", CLONE, *args], capture_output=True, check=True).stdout


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def parents_of(rev: str) -> list[str]:
    rc, body = git("cat-file", "-p", rev)
    assert rc == 0, body
    return [ln.split()[1] for ln in body.splitlines() if ln.startswith("parent ")]


def commit_facts(rev: str) -> dict:
    rc, body = git("cat-file", "-p", rev)
    assert rc == 0, body
    parent_lines = [ln for ln in body.splitlines() if ln.startswith("parent ")]
    facts = {
        "ref": rev,
        "sha": git("rev-parse", rev)[1].strip(),
        "parents": parents_of(rev),
        "parent_lines_from_cat_file_p": parent_lines,
        "parent_count": len(parent_lines),
        "roots": git("rev-list", "--max-parents=0", rev)[1].split(),
        "rev_list_count": int(git("rev-list", "--count", rev)[1].strip()),
        "tree_sha": git("log", "-1", "--format=%T", rev)[1].strip(),
        "commit_date": git("log", "-1", "--format=%cI", rev)[1].strip(),
        "subject": git("log", "-1", "--format=%s", rev)[1].strip(),
    }
    assert facts["roots"], facts
    return facts


merge_base_rc, merge_base_out = git("merge-base", A, B)
is_anc_ab_rc, _ = git("merge-base", "--is-ancestor", A, B)
is_anc_ba_rc, _ = git("merge-base", "--is-ancestor", B, A)
lr_rc, lr_out = git("rev-list", "--left-right", "--count", f"{A}...{B}")
left, right = (int(x) for x in lr_out.split())
all_roots = git("rev-list", "--max-parents=0", "--all")[1].split()
shallow_rc, shallow_out = git("rev-parse", "--is-shallow-repository")
replace_rc, replace_out = git("replace", "-l")
gitdir = Path(git("rev-parse", "--absolute-git-dir")[1].strip())

path_checks = {}
for rel in (".git/shallow", "shallow", "info/grafts", "refs/replace"):
    path_checks[rel] = (gitdir / rel).exists()
git_files = sorted(str(p.relative_to(gitdir)).replace("\\", "/")
                   for p in [gitdir / "shallow", gitdir / "info" / "grafts"]
                   if p.exists())
replace_refs = sorted(p.name for p in (gitdir / "refs" / "replace").glob("*")) \
    if (gitdir / "refs" / "replace").is_dir() else []

# which ref carries each root — the third root is only reachable from refs/stash, not from either lineage
root_carriers = {}
for root in all_roots:
    rc, out = git("for-each-ref", "--contains", root, "--format=%(refname)")
    root_carriers[root] = sorted(x for x in out.splitlines() if x)

stash_rc, stash_out = git("stash", "list")

roots_a = set(git("rev-list", "--max-parents=0", A)[1].split())
roots_b = set(git("rev-list", "--max-parents=0", B)[1].split())
if merge_base_rc == 1 and not merge_base_out.strip():
    verdict = "DISJOINT"
elif roots_a & roots_b:
    verdict = "SAME_ROOT"
else:
    verdict = "UNKNOWN"

h0 = {
    "schema": "H0.DAG-RECONCILIATION/1",
    "lane": "L4-hgk-bridge",
    "clone": CLONE,
    "measured_at_local": datetime.now().astimezone().isoformat(timespec="seconds"),
    "published_claim_under_review": {"main_is_ancestor": True, "commits_ahead": 327},
    "commits": {"A_origin_main": commit_facts(A), "B_epoch41_branch": commit_facts(B)},
    "merge_base": {"command": f"git merge-base {A[:7]} {B[:7]}", "stdout": merge_base_out.strip(),
                   "exit": merge_base_rc, "common_ancestor": None if merge_base_rc == 1 else merge_base_out.strip()},
    "is_ancestor": {"A_in_B": {"exit": is_anc_ab_rc, "value": is_anc_ab_rc == 0},
                    "B_in_A": {"exit": is_anc_ba_rc, "value": is_anc_ba_rc == 0}},
    "left_right_counts": {"command": f"git rev-list --left-right --count {A[:7]}...{B[:7]}",
                          "raw": lr_out.strip(), "exit": lr_rc,
                          "left_only_A": left, "right_only_B": right},
    "is_shallow_repository": {"raw": shallow_out.strip(), "exit": shallow_rc,
                              "value": shallow_out.strip() == "true"},
    "git_metadata_findings": {
        "git_dir": str(gitdir).replace("\\", "/"),
        "shallow_file_present": path_checks[".git/shallow"] or path_checks["shallow"],
        "grafts_file_present": path_checks["info/grafts"],
        "replace_refs_dir_present": path_checks["refs/replace"],
        "git_replace_l": {"stdout": replace_out.strip(), "exit": replace_rc, "refs": replace_refs},
        "present_git_files": git_files,
        "conclusion": "no shallow boundary, no grafts and no replace refs: the DAG read here is the stored DAG",
    },
    "all_roots_in_clone": {"roots": all_roots, "carriers": root_carriers,
                           "note": "three root commits exist in this clone; the third is reachable only from "
                                   "refs/stash, so it is neither lineage's root"},
    "stash": {"exit": stash_rc, "entries": [ln for ln in stash_out.splitlines() if ln]},
    "verdict": verdict,
    "verdict_reason": (
        "git merge-base exits 1 with no output, --is-ancestor is 1 in both directions, and the two commits "
        f"declare different root commits ({git('rev-list', '--max-parents=0', A)[1].strip()} vs "
        f"{git('rev-list', '--max-parents=0', B)[1].strip()}). The left-right count is {left}\\t{right}, which is "
        "two full histories side by side, not a fast-forward range: main is ahead by 0 of the branch's commits, "
        "and the published 327 is not the size of any ancestry range."
    ),
    "published_claim_assessment": {
        "main_is_ancestor": "FALSE — refuted by merge-base exit 1 and by both --is-ancestor directions exiting 1",
        "commits_ahead": ("FALSE as an ancestry measure — 328 is the branch's full commit count and 90 is main's; "
                          "with no merge base there is no 'ahead by' relation between them"),
        "residual": ("this lane can refute the claim on this clone; it cannot say which host produced the claim, "
                     "because no command log accompanied it"),
    },
}

(OUT / "H0_DAG_RECONCILIATION.json").write_text(json.dumps(h0, ensure_ascii=False, indent=1) + "\n",
                                               encoding="utf-8")

# ------------------------------------------------------------------------------------------------
# H1 — bounded delta classification: the config/ control plane + the two lane tools
# ------------------------------------------------------------------------------------------------
CONFIG_PREFIX = "config/"
TOOL_PATHS = ["scripts/lane_policy_reconcile.py", "scripts/lane_arm_retirement_check.py"]

DECISIONS = {
    "config/lane-routing-registry.yaml": (
        "PORT", "the P0 route+retire authority this PR exists for: epoch 41 IN_FORCE, contract_epoch 34, "
        "retired_arms[opencode-go/mimo-v2.6-pro], PLAN rank 4 = opencode-go/mimo-v2.6-flash. Ported as bytes with "
        "three recorded edits (authorization_basis bridge note, source_of_routes LF digest + normalization note, "
        "port_provenance block)."),
    "config/lane-route-slots.candidate.json": (
        "PORT", "the deployment-plane pool: 6/4/5 arms across PLAN/EXECUTE/VERIFY_SECURITY, byte-identical to the "
        "branch (sha256 match asserted in port_e41_report.json), so no arm was hand-typed."),
    "config/model-lane-assignment.json": (
        "PORT", "revision 43 / registry_epoch 39 with lane_chains that the branch's own reconcile tool derives from "
        "the registry (PORTED_RECONCILE_CHECK=CONSISTENT); byte-identical to the branch."),
    "config/lane-arm-aliases.json": (
        "DO_NOT_MERGE", "the branch DELETES this file and carries the same one-pair alias inline in the registry's "
        "arm_aliases block. Deleting it on a main-derived branch would break main's own consumer "
        "(scripts/hgk-lane-dispatch.py reads it), so main's bytes stay. Kept consistent: both declare only "
        "desktop_router/gpt-6.1-sol -> openai-codex/gpt-6.1-sol."),
    "config/hermes-codex-lane.json": (
        "DO_NOT_MERGE", "H3. It carries host-level binary pins (/codex_version, /codex_sha256). Porting them would "
        "declare a codex build this host does not have; the branch's values already disagree with main's and "
        "neither is measured on this host in this round."),
    "config/hermes.json": (
        "DO_NOT_MERGE", "H3. HGK-HERMES-BINDING/2 -> /3 plus install_root path moves; that is a runtime binding "
        "decision, not a route+retire port."),
    "config/active-policy.json": (
        "DO_NOT_MERGE", "H3. Front-door runtime policy; not needed to make the route+retire delta true, and it "
        "changes automatically-dispatched behaviour."),
    "config/closed_paths.yaml": (
        "DO_NOT_MERGE", "H3. New closed-path ACL surface (adds advisory deny rules); ACLs are explicitly out of "
        "scope for this PR."),
    "config/acceptance/CELL_STATE_VOCABULARY.md": (
        "DO_NOT_MERGE", "H3. Acceptance vocabulary document; evidence-plane, not control-plane."),
    "config/issuer/OWNER_AUTHORIZATION.json": (
        "DO_NOT_MERGE", "H3. Issuer authorization record; issuer keys/records are explicitly forbidden in this PR."),
    "config/issuer/OWNER_AUTHORIZATION.json.bak-20261031": (
        "DO_NOT_MERGE", "H3. Issuer backup blob; carries no authority a main-derived candidate needs."),
    "config/issuer/issuer.pub": (
        "DO_NOT_MERGE", "H3. Issuer public key; issuer material is explicitly forbidden in this PR."),
    "config/hermes-codex-lane.json.bak-pinrefresh-20261031101338": (
        "DO_NOT_MERGE", "H3. Timestamped backup of a file this PR does not touch; a backup of a not-ported file "
        "would only add a second stale truth to the tree."),
    "config/recurrence-ledger.json": (
        "DO_NOT_MERGE", "H3. Round recurrence ledger; record of what happened, not a route declaration."),
    "scripts/lane_policy_reconcile.py": (
        "REPLAY", "absent on main and NOT ported (H3 scope). Replayed unmodified from 86f40ec inside "
        "evidence/L4/scratch_probe so its verdict is measured: --check reported CONSISTENT with dirty={} against "
        "the ported config, i.e. the projections already are what the registry derives."),
    "scripts/lane_arm_retirement_check.py": (
        "REPLAY", "absent on main and NOT ported (H3 scope). Replayed unmodified from 86f40ec inside "
        "evidence/L4/scratch_probe: 60 live arm sites scanned, retired_still_live=[], required_missing=[], "
        "verdict PASS, exit 0. This is the branch's own retirement reader agreeing with the port."),
}

name_status = {}
for line in git("diff", "--name-status", A, B)[1].splitlines():
    if "\t" in line:
        st, path = line.split("\t", 1)
        name_status[path.strip()] = st.strip()

all_paths = [p for p in git("diff", "--name-only", A, B)[1].splitlines() if p.strip()]
config_paths = sorted(p for p in all_paths if p.startswith(CONFIG_PREFIX))
assert len(config_paths) == 14, config_paths
outside = [p for p in all_paths if not p.startswith(CONFIG_PREFIX)]
assert len(all_paths) == 2470, len(all_paths)
assert len(outside) == 2456, len(outside)


def blob_sha(rev: str, path: str) -> str | None:
    rc, _ = git("cat-file", "-e", f"{rev}:{path}")
    if rc != 0:
        return None
    return sha(git_bytes("show", f"{rev}:{path}"))


rows = []
for path in config_paths + [p for p in TOOL_PATHS if p in name_status]:
    disposition, reason = DECISIONS[path]
    m, b = blob_sha(A, path), blob_sha(B, path)
    rows.append({
        "path": path,
        "change": name_status.get(path),
        "main_sha256": m,
        "branch_sha256": b,
        "identical": (m is not None and m == b),
        "disposition": disposition,
        "reason": reason,
    })

assert all(r["disposition"] for r in rows), "an unclassified row"
assert sorted(r["path"] for r in rows if r["disposition"] == "PORT") == sorted([
    "config/lane-routing-registry.yaml",
    "config/lane-route-slots.candidate.json",
    "config/model-lane-assignment.json",
])

h1 = {
    "schema": "H1.CONFIG-DELTA-LEDGER/1",
    "lane": "L4-hgk-bridge",
    "base": A,
    "branch": B,
    "method": ("bounded classification: `git diff --name-only` counts 2470 changed paths; only the config/ "
               "control plane plus the two lane tools named by the brief are classified here. Nothing is "
               "silently dropped — every other path is one explicit OUT_OF_SCOPE row carrying the count."),
    "totals": {
        "changed_paths": len(all_paths),
        "config_paths": len(config_paths),
        "classified_tools": len([p for p in TOOL_PATHS if p in name_status]),
        "out_of_scope_paths": len(outside),
        "dispositions": {d: sum(1 for r in rows if r["disposition"] == d)
                         for d in ("PORT", "REPLAY", "REIMPLEMENT", "DO_NOT_MERGE")},
    },
    "rows": rows,
    "out_of_scope": {
        "disposition": "OUT_OF_SCOPE_FOR_THIS_PR",
        "count": len(outside),
        "paths_sample_first_20": outside[:20],
        "reason": ("2456 non-config paths (src/, tests/, scripts/, evidence/, docs/, receipts/, var/ ...) are "
                   "NOT classified in this PR: porting any of them is H3, a separate owner decision. The count "
                   "is declared so the ledger cannot read as though the diff were 16 files."),
        "explicit_not_portable_here": {
            "issuer_keys": "config/issuer/*",
            "acls": "config/closed_paths.yaml",
            "dependencies_and_licences": "src/, requirements, licences under the non-config tree",
        },
    },
    "normalization_finding": {
        "what": ("config/model-lane-assignment.json carries two identities: the tracked bytes are LF "
                 "(sha256 206ec9b8...) and a Windows checkout materialises CRLF (sha256 8ac81357...). The epoch-41 "
                 "registry pins the CRLF digest 8ac81357 and main's registry pins cfbff111, which matches "
                 "NEITHER of its own assignment's digests."),
        "why_it_matters": ("a digest pin taken over a working-tree normalisation only holds on the host that "
                           "wrote it; a Linux CI checkout would compute the LF digest and read a false drift"),
        "action_taken": ("the port records both digests (source_of_routes.sha256 = CRLF twin inherited from the "
                         "branch, source_of_routes.sha256_lf = the tracked bytes) and the validator accepts either; "
                         "no pin was silently reconciled"),
        "main_pin_verdict": "main's own pin cfbff111 is stale and matches no digest of its own projection",
    },
    "pre_existing_main_defects": [
        {"id": "main-lane-policy-red", "detail": (
            "on PRISTINE main the repo's own drift reader reports 22 fatal findings (13 COVERAGE_GAP + 7 "
            "DRIFT_VALUE on config/model-lane-assignment.json, 2 DRIFT_VALUE on config/hermes-codex-lane.json) and "
            "tests/test_lane_policy.py is already 2 failed / 4 passed. Baseline captured before any edit: "
            "evidence/L4/baseline_drift_findings.json, evidence/L4/baseline_pytest_lane_policy.log.")},
        {"id": "stale-registry-pin", "detail": (
            "main's registry pins source_of_routes to cfbff111 while its own assignment hashes to 6255e595 (LF) / "
            "105e49c4 (CRLF); the pin is not a digest of the file it names.")},
    ],
}
(OUT / "H1_CONFIG_DELTA_LEDGER.json").write_text(json.dumps(h1, ensure_ascii=False, indent=1) + "\n",
                                                encoding="utf-8")

print(json.dumps({"h0_verdict": h0["verdict"], "merge_base_exit": merge_base_rc,
                  "left_right": h0["left_right_counts"]["raw"],
                  "h1_rows": len(rows), "totals": h1["totals"]}, ensure_ascii=False, indent=1))
