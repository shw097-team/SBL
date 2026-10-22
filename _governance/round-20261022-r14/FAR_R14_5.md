# FAR-R14-5 — 68 advisories in the runtime, zero in the deliverable

**Round** `SBL-R14-FULL-DOC-POST-R13-20261022` · **Obligation** `R14-TS11` · **At** 2026-10-22

## 1. What changed in the basis

`R14-TS11` had been held `PARTIAL` with the note *"no third-party scanner on this host: SBOM/licence/secret results are
self-authored."* That note was true of the five originally named tools (`syft`, `trivy`, `grype`, and two others), and it
was allowed to stand for several rounds while hand-written SBOM figures were reported next to real scanner output — a
mixture that hides which numbers a tool produced and which a person did.

Two of the missing capabilities are pip-installable and were installed this round:

| tool | version | what it replaced |
|---|---|---|
| `cyclonedx-bom` | 7.5.0 | the hand-written SBOM |
| `pip-audit` | 2.10.1 | the absence of any advisory source |

`detect-secrets` 1.5.0 and `pip-licenses` remain third-party and were re-run rather than re-quoted.

## 2. Measurements

| scan | tool | result |
|---|---|---|
| SBOM | `cyclonedx-bom` 7.5.0 | CycloneDX **1.6**, **171** components, `sha256 69efcde1…` |
| vulnerabilities | `pip-audit` 2.10.1 | **68** advisories, **9** packages, **all 9** have a published fix |
| licences | `pip-licenses` | **166** distributions, **1** `UNKNOWN` (`agent-client-protocol 0.9.0`) |
| secrets | `detect-secrets` 1.5.0 | **0** hits in `ts11_build_output/unpacked` |

Affected packages: `aiohttp` 8, `pillow` 24, `pyjwt` 14, `pip` 12, `httpx2` 5, `setuptools` 2, `certifi` 1, `httpcore2` 1, `mcp` 1.

## 3. The decision question

Are the three SP ZIPs distributable while the host runtime carries 68 advisories?

## 4. Evidence that decides it

Parsed from the deliverables themselves (`tomllib` over `pyproject.toml`, both builds):

| package | version | licence | declared dependencies |
|---|---|---|---|
| `commander-sp` (`sbl-v01`) | 0.1.0 | MIT | **none** |
| `external-challenge-sp` (`sbl-v01`) | 0.1.0 | MIT | **none** |
| `tpm-sp` (`sbl-v01`) | 0.1.0 | MIT | **none** |

Zero declared dependencies means the deliverables' dependency closure is empty: **no advisory above can reach code shipped
in the ZIPs**. The `UNKNOWN` licence is `agent-client-protocol`, which none of the three declares.

## 5. Decision

**`PASS_FOR_THE_DELIVERABLE_WITH_HOST_RUNTIME_DEBT`.** `R14-TS11` closes on three third-party scans plus an empty
dependency closure, not on a claim that the environment is healthy.

Three options were weighed:

1. **Upgrade the 9 packages now.** Rejected for this round: `aiohttp`, `pillow`, `pyjwt` and `mcp` are the Hermes runtime's
   own dependencies, and changing them is a runtime change with its own verification burden — the same class of change that
   produced the eight-failure rebind earlier today. Doing it inside an evidence round would be an unverified mutation of the
   plane that is supposed to be the measuring instrument.
2. **Report the scans as clean.** Rejected outright.
3. **Close the obligation on the deliverable's empty closure, register the runtime debt.** Chosen.

## 6. Debt registered (not remediated)

| item | count | owner action |
|---|---|---|
| host-runtime advisories with published fixes | 68 advisories / 9 packages | upgrade in a dedicated runtime round, then re-run `pip-audit` |
| `agent-client-protocol` licence metadata | 1 distribution | obtain licence text or drop the dependency |

Neither item touches the three ZIPs. Both remain open and are named here so that "TS11 DONE" cannot be read as "the host is
clean".

## 7. Ceiling

`THREE_MIT_SOURCE_ZIPS_DISTRIBUTABLE_NO_DECLARED_DEPENDENCIES`. Not claimed: that the runtime is free of vulnerabilities,
that the three scans replace `syft`/`trivy`/`grype`, or that an external principal accepted this deviation.
