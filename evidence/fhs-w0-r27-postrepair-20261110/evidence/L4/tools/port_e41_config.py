#!/usr/bin/env python3
"""H2 — port the epoch-41 config control plane onto the main-derived bridge worktree.

Byte-faithful first: every file is taken from `git show 86f40ec:config/<path>` in the authoritative clone.
Then exactly three edits are re-applied to config/lane-routing-registry.yaml so the file describes the
port honestly:

  E1  authorization_basis  += r27 bridge note + owner order 2026-11-09 (admit mimo-v2.6-flash to PLAN rank 4,
                             retire mimo-v2.6-pro)
  E2  source_of_routes     += the LF digest of the ported assignment beside the branch's own CRLF-twin digest
                             (a normalization twin is a second identity, not a mismatch to reconcile silently)
  E3  port_provenance      = new additive block: which ref the bytes came from and why a cherry-pick was impossible

Each edit asserts count == 1 before writing, so a silent second occurrence fails loudly.

Usage: python port_e41_config.py <worktree> <clone>
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORKTREE = Path(sys.argv[1]).resolve()
CLONE = Path(sys.argv[2]).resolve()
SRC_REF = "86f40ec114f19bbd35314e376da4d0bed9805b22"

PORT = [
    "config/lane-route-slots.candidate.json",
    "config/model-lane-assignment.json",
    "config/lane-routing-registry.yaml",
]


def show(path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(CLONE).replace("\\", "/"), "show", f"{SRC_REF}:{path}"],
        check=True, capture_output=True,
    ).stdout


def norm_crlf(b: bytes) -> bytes:
    return b.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")


report = {"schema": "L4.PortReport/1", "source_ref": SRC_REF, "files": {}}

for rel in PORT:
    src = show(rel)
    dst = WORKTREE / rel
    dst.write_bytes(src)
    report["files"][rel] = {
        "bytes": len(src),
        "sha256_source": hashlib.sha256(src).hexdigest(),
        "sha256_written": hashlib.sha256(dst.read_bytes()).hexdigest(),
        "byte_identical_to_source": hashlib.sha256(dst.read_bytes()).hexdigest() == hashlib.sha256(src).hexdigest(),
        "crlf_twin_sha256": hashlib.sha256(norm_crlf(src)).hexdigest(),
    }

# ---- edits on the ported registry -------------------------------------------------------------
reg_path = WORKTREE / "config/lane-routing-registry.yaml"
text = reg_path.read_bytes().decode("utf-8")
orig_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()

ASSIGN_LF = report["files"]["config/model-lane-assignment.json"]["sha256_source"]
ASSIGN_CRLF = report["files"]["config/model-lane-assignment.json"]["crlf_twin_sha256"]

BRIDGE_NOTE = (
    " R27 BRIDGE (2026-11-10, lane L4): these bytes are a CONTENT PORT of config/lane-routing-registry.yaml "
    "as carried on branch config/plan-mimo-flash-20261109 at 86f40ec114f19bbd35314e376da4d0bed9805b22. "
    "That lineage and main share NO root commit (git merge-base acd9196f 86f40ec -> exit 1, no output), "
    "so no cherry-pick and no fast-forward range exists; the epoch-41 authority content was re-applied onto "
    "main as bytes. Owner order 2026-11-09: opencode-go/mimo-v2.6-flash is ADMITTED to the PLAN pool at rank 4 "
    "and opencode-go/mimo-v2.6-pro is RETIRED from every lane pool (retired_arms); the retired arm must never "
    "be selectable again. Status IN_FORCE is the owner-ordered candidate state of this file; the PR that "
    "carries it is a CANDIDATE until the owner merges it, and nothing here claims the epoch is effective on "
    "any host."
)

# E1 — extend authorization_basis (single-quoted YAML scalar: internal quotes already doubled)
marker = "no alternate checker identity or diversity is implied.'"
assert text.count(marker) == 1, f"authorization_basis tail matched {text.count(marker)} times"
text = text.replace(marker, "no alternate checker identity or diversity is implied." + BRIDGE_NOTE + "'", 1)

# E2 — record both digests of the ported projection behind source_of_routes
old_sor = (
    "  revision: 43\n"
    "  sha256: 8ac813570f406f3a949ce736cff45b5ecdaee347b9538f7ececcb474ff48be63\n"
)
assert text.count(old_sor) == 1, f"source_of_routes block matched {text.count(old_sor)} times"
new_sor = (
    "  revision: 43\n"
    f"  sha256: {ASSIGN_CRLF}\n"
    f"  sha256_lf: {ASSIGN_LF}\n"
    "  digest_normalization: 'the tracked bytes are LF; a Windows checkout materialises CRLF, and the pin "
    "inherited from the epoch-41 branch was taken over the CRLF twin. Both digests name the same ported "
    "projection; neither is re-derived at read time.'\n"
)
text = text.replace(old_sor, new_sor, 1)

# E3 — additive provenance block, placed immediately before the route table
anchor = "routes:\n- lane: PLAN\n"
assert text.count(anchor) == 1, f"routes anchor matched {text.count(anchor)} times"
provenance = (
    "port_provenance:\n"
    "  schema: HGK-CONTENT-PORT/1\n"
    "  lane: L4-hgk-bridge\n"
    "  round: FHS-W0-r26-postrepair-20261110\n"
    "  ported_at_utc: '2026-11-10'\n"
    f"  source_ref: {SRC_REF}\n"
    "  source_branch: config/plan-mimo-flash-20261109\n"
    "  source_repo: C:/Projects/Agent_Workspace/FHS/HG-KSEOS\n"
    "  source_is_ancestor_of_main: false\n"
    "  source_sha256_lf: SHA_PLACEHOLDER\n"
    "  target_base_ref: acd9196fcd748638673848bf62a426dcc3c22dc1\n"
    "  method: content_port_not_cherry_pick\n"
    "  why: 'the two lineages are disjoint at the root commit, so a cherry-pick or a fast-forward merge "
    "would either fail or invent a merge that never existed'\n"
    "  in_scope: 'config/lane-routing-registry.yaml, config/lane-route-slots.candidate.json, "
    "config/model-lane-assignment.json'\n"
    "  out_of_scope: 'issuer keys, ACLs, dependencies, licences, scripts/ and every non-config path (H3, a "
    "separate owner decision)'\n"
    "  claim_ceiling: 'a candidate branch. Not effective on any host until the owner merges it and the own "
    "CI of this repo is green.'\n"
)
# the registry's own pre-edit bytes are what the port is provenance for
provenance = provenance.replace("SHA_PLACEHOLDER", orig_sha)
text = text.replace(anchor, provenance + anchor, 1)

reg_path.write_bytes(text.encode("utf-8"))
report["registry_edits"] = {
    "pre_edit_sha256": orig_sha,
    "post_edit_sha256": hashlib.sha256(reg_path.read_bytes()).hexdigest(),
    "edits": ["E1 authorization_basis extended", "E2 source_of_routes sha256_lf + digest_normalization",
              "E3 port_provenance block"],
}

# A port that parses under the reader the domain actually uses is the only port worth reporting.
# PyYAML is not a dependency of this script: when it is absent the report says so instead of claiming a check.
try:
    import yaml  # noqa: PLC0415
except ImportError:  # pragma: no cover
    report["yaml_verified"] = "SKIPPED (PyYAML absent)"
else:
    doc = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    assert doc["schema"] == "HGK-LANE-ROUTING-REGISTRY/1", doc.get("schema")
    assert doc["epoch"] == 41 and isinstance(doc["epoch"], int), doc.get("epoch")
    assert doc["status"] == "IN_FORCE", doc.get("status")
    assert doc["contract_epoch"] == 34, doc.get("contract_epoch")
    assert "opencode-go/mimo-v2.6-pro" in (doc.get("retired_arms") or {}), "retired_arms missing"
    assert len(doc["routes"]) == 3, [r.get("lane") for r in doc["routes"]]
    report["yaml_verified"] = {
        "reader": f"PyYAML {yaml.__version__} safe_load",
        "epoch": doc["epoch"], "status": doc["status"], "contract_epoch": doc["contract_epoch"],
        "routes": [r["lane"] for r in doc["routes"]],
        "retired_arms": sorted(doc["retired_arms"]),
        "port_provenance_present": "port_provenance" in doc,
    }

print(json.dumps(report, ensure_ascii=False, indent=1))