"""The runtime-readiness matrix must only ever be satisfied by an acceptance
whose subject is that capability.

A readiness row is a claim of the shape "capability X is ready", and the
`acceptance_ids` are the only evidence that claim can rest on.  When a row
pointed at ACC-SBL_SHARED_CORE, a cell for `SP_PLUGIN_PACKAGE_TPM` could be
satisfied by an acceptance whose subject is `SBL_SHARED_CORE` -- a different
subject entirely -- and the matrix would still read READY.  Nothing in the
compiler caught it: every one of those acceptance ids existed and was legal, and
the compiler checks that locators and ids are present, not that the subject
matches the row that cites them.

This test pins the invariant directly.  It reads the CURRENT contract (the
highest R-numbered file in contracts/), not a hard-coded filename, so it keeps
its teeth when the next round adds SBL_C0_C9_CONTRACT-R10.json.  It is not
skipped in any environment: a missing contract is a failure, not an excuse.
"""

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CONTRACTS = REPO / "contracts"

# The four capabilities that were mis-bound; named so a regression names itself.
REPAIRED = (
    "SP_PLUGIN_PACKAGE_TPM",
    "SP_PLUGIN_PACKAGE_COMMANDER",
    "SP_PLUGIN_PACKAGE_CHALLENGE",
    "SP_HOST_INSTALL_REQUEST",
)


def _current_contract() -> Path:
    """Highest R-numbered contract in contracts/."""
    best = None
    best_n = -1
    for p in sorted(CONTRACTS.glob("SBL_C0_C9_CONTRACT*.json")):
        m = re.search(r"-R(\d+)\.json$", p.name)
        n = int(m.group(1)) if m else 0
        if n > best_n:
            best_n, best = n, p
    assert best is not None, f"no contract file found under {CONTRACTS}"
    return best


def _mismatches(contract: dict) -> list[tuple[str, str, str]]:
    subjects = {a["acceptance_id"]: a.get("subject_id") for a in contract["acceptance"]}
    bad = []
    for row in contract.get("runtime_readiness", []):
        for aid in row.get("acceptance_ids") or []:
            if aid not in subjects:
                bad.append((row["capability"], aid, "<missing acceptance>"))
                continue
            if subjects[aid] != row["capability"]:
                bad.append((row["capability"], aid, str(subjects[aid])))
    return bad


def test_current_contract_has_no_foreign_subject_acceptance():
    path = _current_contract()
    contract = json.loads(path.read_text(encoding="utf-8"))
    bad = _mismatches(contract)
    assert not bad, (
        f"{path.name}: {len(bad)} runtime_readiness cell(s) are satisfied by an "
        f"acceptance belonging to a different subject: {bad}"
    )


def test_the_four_repaired_capabilities_cite_their_own_acceptance():
    path = _current_contract()
    contract = json.loads(path.read_text(encoding="utf-8"))
    by_cap = {row["capability"]: row for row in contract.get("runtime_readiness", [])}
    subjects = {a["acceptance_id"]: a.get("subject_id") for a in contract["acceptance"]}

    missing = [c for c in REPAIRED if c not in by_cap]
    assert not missing, f"{path.name}: capabilities absent from runtime_readiness: {missing}"

    for cap in REPAIRED:
        ids = by_cap[cap].get("acceptance_ids") or []
        assert ids, f"{path.name}: {cap} has no acceptance_id at all"
        assert "ACC-SBL_SHARED_CORE" not in ids, (
            f"{path.name}: {cap} still falls back to ACC-SBL_SHARED_CORE, whose subject is "
            f"{subjects.get('ACC-SBL_SHARED_CORE')}"
        )
        assert f"ACC-{cap}" in ids, (
            f"{path.name}: {cap} must cite ACC-{cap} itself; it cites {ids}"
        )
        assert subjects.get(f"ACC-{cap}") == cap, (
            f"{path.name}: ACC-{cap} has subject_id {subjects.get(f'ACC-{cap}')}, expected {cap}"
        )


def test_every_acceptance_edge_has_a_self_consistent_subject():
    """The same invariant viewed from the other side, over every row."""
    path = _current_contract()
    contract = json.loads(path.read_text(encoding="utf-8"))
    ids = [a["acceptance_id"] for a in contract["acceptance"]]
    assert len(ids) == len(set(ids)), f"{path.name}: duplicate acceptance ids present"
    for row in contract["acceptance"]:
        assert row.get("subject_id"), f"{path.name}: {row['acceptance_id']} has no subject_id"


def test_repairing_requires_the_upstream_locator_to_resolve():
    """No acceptance edge may be created for a capability that carries no
    upstream locator in /execution_scope -- a binding that cannot name the
    clause that governs it cannot be accepted either."""
    path = _current_contract()
    contract = json.loads(path.read_text(encoding="utf-8"))
    scope = {r["capability"]: r for r in contract.get("execution_scope", [])}
    for cap in REPAIRED:
        assert cap in scope, f"{path.name}: {cap} missing from execution_scope"
        locs = scope[cap].get("source_locators") or []
        assert locs, f"{path.name}: {cap} carries no source_locators upstream"
