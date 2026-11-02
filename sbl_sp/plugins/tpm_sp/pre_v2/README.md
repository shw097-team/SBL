# PRE-V2 author adapter candidate

The previous TPM planning route mixed receipt-free plans with live Checker
receipts and generic ECP defaults. This additive adapter preserves canonical
PIPD records and original identities, emits closed design Sidecars, probes real
Git currentness, and rejects authority-shaped inputs. It does not issue grants,
qualify a Host, accept a product, or publish a release.

`adapter.py` is MIT SBL code. The canonical entry remains
`sbl_sp/plugins/tpm_sp/SKILL.md`. Full 14-skill private packages retain the
24-document Corpus locally; restricted source text and historical raw lane
output are excluded from this public branch.

Run the public regression from the repository root:

Install the optional author dependency with `pip install '.[tpm-pre-v2]'` in an
isolated environment; the private package pins the same jsonschema version.

```text
python -m unittest discover -s tests -p test_tpm_pre_v2.py -v
```

The original Writer integration is supplied under `upstream/`. Apply its patch
only to PIPD main `f6335a94157c61da75d92121d14c43feb413e981` in a separate
candidate checkout. It adds options to existing commands, preserves the actual
14-command set and 19 canonical Schema families, and retains every existing
canonical `$id`. `--planned-sidecar` accepts an author plan without weakening
the original live receipt path. `--effect-intent` projects the six typed effects
through the original ECP Writer. All projected effects remain EFFECT_UNBOUND.

Original CLI examples, after applying the upstream patch:

```text
pipd compile-ecp --pi PI.json --pd PD.json --effect-intent ECP.intent.json --operation-registry operations.json --operation-registry-sha256 <owner-pin>
pipd compile-tqaep --pi PI.json --pd PD.json --ecp ECP.json --planned-sidecar PlannedTQAEP.json --fixture-root fixtures
pipd validate --bundle bundle.json --planned-sidecar PlannedTQAEP.json --fixture-root fixtures
```

Use `OriginalPipd` with an externally obtained complete code+Schema pin set.
`crosswalk` replays the original PI compiler against actual source bytes.
`probe_repo` and `require_current` bind exact preimages and observe tracked and
untracked state; they prove process access, never an HGK effect grant.
Effect and Case registries must be read through `registry` with external pins.
Synthetic fixtures establish author consistency only. `package_design` calls
the actual original Reader and requires nonempty FULL graph closure.

The plan preserves Case, Requirement, Clause/SourceSHA, Oracle, FUO, POS/NEG
fixture hashes, raw schema, expected WorldRaw and Host/Profile/Kind/Mode.
Unbound runners stay named RUNNER_UNBOUND. No API in this module raises a plan
to Qualified or same-scope usability. Those require the original Protected
Checker, complete FUO coverage and identical Subject/Candidate/Scope/Host/
PolicyEpoch. Release remains with the original Publisher.

Rollback uses the retained original private archive or `git revert` of this
candidate on an isolated branch. Uninstall the shadow marketplace plugin before
loading the original in a fresh session. The active account plugin was not
updated. Native W0–W3 and ChatGPT Host acceptance remain outside local author
evidence. See the branch handoff report for actual PASS/FAIL/HOLD states.
