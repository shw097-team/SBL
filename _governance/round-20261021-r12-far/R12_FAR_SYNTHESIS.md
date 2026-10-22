# FAR R12 swarm synthesis — five owner decisions closed (2026-10-23)

**Synthesizer**: kanban `t_5f76be91` (board `sbl-r12-far`), released by the verifier gate
`t_00d2062c` = `PASS_WITH_RECORDED_RESIDUALS` (all 5 worker handoffs + 5 blackboard updates
re-verified against disk/remote, not taken on claim).
**Landing branch**: `evidence/r12-far-close-20261023`, cut from `origin/main@dc5428f`
(the docs/claims alignment `4519f768` (PR #6) and the subagent-corrected FAR study (PR #7/#8)
are already ancestors of it).
**Claim ceiling**: candidate-only, locally verified, pushed to origin; NOT owner-signed, NOT
externally accepted, no native/host effect, no completion percentage (D-04 ceiling).

## 1. What this commit lands

All five FAR R12 owner decisions are now closed in the canonical round docs, with every
decision record in one place under `_governance/round-20261021-r12-far/`:

| # | Decision | ID / record | Status |
|---|---|---|---|
| O-1 / D-11 | PLAN lane declaration vs mandate chain | `DEC-R12-D11-O1-20261023` → `D11_O1_LANE_DECLARATION_DECISION.md` | CLOSED_SUPERSEDED_BY_EVENTS; standing rule = rebind-on-order + mandate chain as per-round assertion layer |
| O-2 / D-07 | Checker scratch grant | `DEC-R12-D07-O2-20261023` → `O2_D07_CHECKER_SCRATCH_GRANT.md` + `o2_checker_scratch/` | GRANTED (scope+expiry+subject digest); R9-02 acceptance round itself stays OPEN |
| O-3 / D-08 | Nine untracked HGK test modules | `O3_D08_ADOPTION_RECORD.md` (mirror of HG-KSEOS `f380719`, blob-identical `3fb9e0c9`) | ADOPTED; R9-05 clean-checkout parity stays PARTIAL |
| O-4 / D-14 | Plugin packaging authority | `O4_NOBJ017_EXCEPTION_RECORD.md` + `.json` | ChatGPT private GPT (GA, DOC-12 C36.3) chosen; NOBJ-017 stays PROHIBITED; C-016..018 stay HOST_PENDING |
| O-5 / D-15 | GPTB KP R04 polarity | `CR-GPTB-KP-R04-POLARITY.md` (mirror of `evidence/r12-20261021-far@72ee999`, byte-identical) | ACKNOWLEDGED, recorded, 0 DOC/KP sources modified |

`openspec/changes/far-r12-20261021/tasks.md`: O-1..O-5 all `[x]` with one-line dispositions.
`FAR_DEVIATION_STUDY.md`: D-07/D-08/D-11/D-14/D-15 rows and the O-1..O-5 decision table
updated to decided, each pointing at its record. O-1's edits (previously uncommitted in
worktree `_r12_docs`, flagged `O-1-landing-at-risk` by the verifier) are landed by this commit.

## 2. Record provenance (byte-preservation)

- `O2_D07_CHECKER_SCRATCH_GRANT.md` + `o2_checker_scratch/*` + `CR-GPTB-KP-R04-POLARITY.md`:
  `git checkout origin/evidence/r12-20261021-far -- <paths>` — blob-identical, including the
  CR's sha256 `860c0456…` the verifier independently read back from the remote.
- `O3_D08_ADOPTION_RECORD.md`: written from HG-KSEOS `codex/hgk-final-closure-002:docs/ADOPTION-D08-O3-UNTRACKED-TESTS-20261023.md`;
  `git hash-object` match `3fb9e0c97f1a9179639f40527c4d2f62a673c448` on both sides.
- `O4_NOBJ017_EXCEPTION_RECORD.md` + `.json`: copied from the kanban task attachments
  (`t_0d384783`), the artifacts the verifier validated as `json_valid`.
- `D11_O1_LANE_DECLARATION_DECISION.md`: the untracked file from `_r12_docs` (6922 B, the
  file the verifier inventoried).

## 3. Recorded residuals (open after this synthesis)

1. **D-11b** (issuer-owned): rev-32 `sod.*` narrative prose is stale and pinned green by
   projection `expected` values. One issuer rebind commit must move prose + pins together.
2. **Pool rev21 `automatic_selection` defect (verifier residual R-new1)**: measured RED at
   `1dcc59d`; the concurrent R15.2 session's repair is visible locally at
   `2c0209f`/`c0c661f` (`automatic_selection` back on the rank-1 arm in all three lanes) but
   the repair card `t_d5596d34` was still `running` when this synthesis was written — not
   closed, not pushed-verified here. Not one of the five workers caused it; none of the five
   touched the pool file.
   *Addendum (synthesizer re-measure, after the repair card closed `t_d5596d34`):* the card
   completed with its own readback (`2c0209f` one-commit fix + `c0c661f` TT receipt
   `TT-R12-POOLREV21-AUTOSEL`). Independently re-measured here at HG-KSEOS HEAD `237969e`
   (the R15.2 session's later pin-binding commit): `test_lane_policy.py` +
   `test_lane_scope_isolation.py` = **10 passed / 90 subtests, exit 0**; `config/` tree clean.
   The repair's own residual stands: the registry-vs-pool one-commit violation from `9c36a77`
   (registry epoch 32 / assignment rev 32 still declaring EXECUTE rank-1 = minimax) remains
   OPEN and folds into residual 1 (D-11b, issuer-owned).
3. **O-5 citation defect (verifier-noted, minor)**: the CR's metadata corpus path spells
   `驗收指標官` while the real directory is `驗收指揮官`; content was verified against the
   real directory. Left uncorrected here (the CR is a pushed record; corrections belong to a
   superseding CR or the Knowledge Owner).
4. **KP corpus canonical designation**: 7 byte-identical corpus copies, canonical not
   designated; `19_KP_INDEX_CROSSWALK` row deferred to the Knowledge Owner (R7 OWNER-4).
5. **R9-02 / R9-05**: O-2 removes the scratch blocker but the acceptance round itself stays
   OPEN; O-3 closes ownership/traceability but clean-checkout parity stays PARTIAL.

## 4. Side effects of this synthesis (fully disclosed)

- **SBL repo**: new branch `evidence/r12-far-close-20261023` from `origin/main@dc5428f`
  (worktree `C:/Projects/Agent_Workspace/_r12_close`); 1 commit, additive:
  2 modified round docs (`tasks.md`, `FAR_DEVIATION_STUDY.md`) + 5 decision records +
  `o2_checker_scratch/` evidence bundle. No `contracts/`, `sbl_core/`, `sbl_sp/`, `sbl_cli/`,
  `tests/`, `skills/` or `docs/` file touched. Pushed non-force; branch is new, no ref rewritten.
- **Control-package pin**: not touched — `contracts/CONTROL_PACKAGE_MANIFEST.json` unchanged
  in this commit (verified in the diff); the pin's subject is the external
  `SBL_PIPD-LS-PKG` mirror, outside this repo. Re-verified from this landing branch after
  the commit: `tools/check_control_package.py --verify` → `CONTROL_PACKAGE_PINNED: 14 docs,
  17473442 bytes, rollup 01b972c80341e1b8`, exit 0 — the pin the round goal requires is
  intact.
- **HG-KSEOS**: not modified by this synthesis (the pool repair is the sibling card's work).
- **`_r12_docs` worktree**: its uncommitted O-1 edits were copied out as a patch and landed
  here; the original uncommitted state was left in place untouched (that worktree is shared).
- **Kanban**: this card completes with structured metadata; cross-worker notes appended to
  the swarm root `t_c1b4d403`.
