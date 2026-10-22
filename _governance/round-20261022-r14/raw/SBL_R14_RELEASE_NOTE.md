# SBL R14 Release Note

Status: PARTIAL / REMOTE_CANDIDATE_UNCONFIRMED. This is an evidence/supply-chain
packet, not an externally accepted production release.

## Independent subject bindings

- HG-KSEOS candidate `refs/heads/codex/hgk-final-closure-002`: `eec2f17720d3774b3ce88dd00f880444935ff17b` (local git rev-parse).
- Evidence `refs/heads/evidence/r14-20261022-native`: `e5116e9edf1e23acc354ff05b7d7963884db539d` (local git rev-parse and remote readback).
- These are independent SHAs. The evidence SHA is a pinned pre-TS28 publication,
  not a claim that it already contains this new packet.

## Contains

A digest inventory of OBLIGATIONS.json, all 315 recursively discovered
pre-existing packet JSONs, and 9 scripts added under HG-KSEOS/scripts
since `9fa79dd` (the explicitly scoped pre-round source baseline).
The release also contains actual remote ref output and fetched-object comparisons,
a self-authored secret-pattern measurement, installed-distribution licence metadata,
and a self-authored CycloneDX-shaped component inventory. Component package hashes
measure METADATA/PKG-INFO only, not complete installed distributions or wheels.
The scripts are measured local source artifacts; their remote delivery is NOT established.

## Does not contain or claim

- M3 acceptance, semantic completeness, end-to-end correctness, or external acceptance.
- Qualification/installation of host-pending surfaces; three private plugin surfaces
  remain HOST_PENDING. No host authority is conferred by publishing this packet.
- A third-party secret, licence, SBOM or vulnerability scan. syft, pip-licenses,
  detect-secrets, trivy and grype are absent. All such inventories are labelled
  SELF_AUTHORED_NO_THIRD_PARTY_SCANNER.
- A signed release, provenance attestation, resolved dependency graph, or package-wide
  binary integrity proof. Metadata fields are not a licence scan or legal conclusion.
- A zero-literal-hit assertion: broad literal grep can match ordinary task words and
  scanner-rule declarations. The scan report lists every file/line and distinguishes
  those from token-shaped candidates without suppressing the literal findings.

## Remote readback and limits

The supplied SBL remote advertises the evidence ref at the exact pinned SHA.
It does not advertise `refs/heads/codex/hgk-final-closure-002`. HG-KSEOS has no configured remote;
no candidate history is pushed to an invented target. Remote artifact counts and
any stale/missing paths are recorded in ts28_remote_readback.json, from fresh
remote objects rather than the existing checkout. TS28 outputs remain local-only
pending coordinated evidence publication; this packet does not claim otherwise.

## Reproduction

Run `python _r14_packet/raw/ts28_build_release.py` from the workspace. This writes only
the TS28 packet prefix and its evidence raw mirror, fetches public evidence objects,
and prints measured counts. It does not mutate source, rewrite history, or push.
A subsequent independent publisher must scan the exact publication set, publish
additively, and read every published blob back. Changing any measured input requires
a new snapshot and invalidates its earlier digest binding.
