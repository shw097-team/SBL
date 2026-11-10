# VERIFY / Acceptance Challenge brief — independent re-derivation of the r27 repairs

You are the **VERIFY_SECURITY** lane, acting as Acceptance Challenge. You are **read-only**: you may read
files and run commands that read; you must not edit, create, delete, push, merge, or install anything.
If a check cannot be run, write `UNPROVEN` and say why. A verdict that repeats the maker's summary is worth
nothing; the whole point of a second process is to try to falsify the claims.

## What was claimed (each claim has a falsifier — run it)

Worktrees (read them, do not modify them):

- `S = C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-integration` (branch `r27/postrepair-integration`)
- `B = C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge` (branch `r27/epoch41-bridge`)
- `H = C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-hook` (branch `r27/fhs-entry-hook`)
- `F = C:/Projects/Agent_Workspace/FHS_R26_WT/fabric-mirror` (branch `r27/r26-mirror-admission`)
- Round evidence: `C:/Projects/Agent_Workspace/FHS_W0_R26_POSTREPAIR_20261110`

Python: `C:/Users/user/AppData/Local/Programs/Python/Python311/python.exe` (has pytest 9.1.1).
The payload round root inside S is `evidence/fhs-w0-r26-repair-20261109`.

| # | Claim | Falsifier to execute |
|---|---|---|
| C1 | G29 no longer accepts a vote with no candidate binding | run `tools/verify_quorum.py --selftest`; then construct your OWN property dict with `votes_r25 = {"A": true, "B": true}` and call the predicate via a tiny script; expect a refusal, not `ACCEPTABLE_FOR_FHS_READER_SCOPE` |
| C2 | G29 no longer accepts a fabricated raw digest | same file, a vote whose `raw_path` resolves but whose declared `raw_sha256` is `"00"*32`; expect `RAW_DIGEST_MISMATCH` |
| C3 | G29 no longer accepts JSON `1` as a boolean | a vote with value `1`; expect `VOTE_TYPE_INVALID` |
| C4 | The real r25 repair votes still count | run `tools/verify_quorum.py --root .`; report `properties_checked` and every finding verbatim; the two repaired properties (WP-FHS-00, WP-FHS-01) must still be accepted |
| C5 | Bindings are per-run and unoverwritable | `tools/selftest_fhs_3lm.py` (needs `--tool --hgk-root C:/Projects/Agent_Workspace/FHS_R26_WT/hgk-bridge --epoch33-root <round>/evidence/L2/probe/epoch33 --workdir <scratch> --logdir <scratch> --json-out <scratch>/x.json`); then bind twice by hand into a scratch dir and show two distinct `binding_id`s |
| C6 | `--assert` refuses pool drift / expiry / tampering | bind once, then (on COPIES) alter the pool bytes, set ttl 0, and edit `model`; `--assert` must give `POOL_DIGEST_DRIFT`, `BINDING_EXPIRED`, `BINDING_TAMPERED` with non-zero exits |
| C7 | The retired arm is refused | `tools/fhs_3lm.py --assert-arm opencode-go/mimo-v2.6-pro --hgk-root B` → exit 9 |
| C8 | The seven owner signatures really verify | `python tools/verify_public_bundle.py` inside S's payload → must print 7/7 and exit 0; then flip one byte in a COPY of one receipt and show it fails |
| C9 | L1 metadata is now true | re-measure the L1 file yourself (`藍圖/FHS_PIPD-LS-PKG_藍圖_r4.md` under the knowledge base path with full-width slashes) and compare with `evidence/FHS_ORIGINAL_ACK.json` |
| C10 | The 76-property denominator is right | count `preservation` keys per clause in the six reader receipts; WP-FHS-15/16/19/21 must total 19 clauses × 4 = 76 |
| C11 | `EVIDENCE_SCOPE.full.excluded` is empty | read the file; the six gates must be under `not_runnable_in_CI` |
| C12 | The r27 document is append-only | `cmp` the first N bytes of `evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md` against the whole r26 document; print both sizes and shas |
| C13 | HGK history is disjoint, not "327 ahead" | in `C:/Projects/Agent_Workspace/FHS/HG-KSEOS` run `git merge-base acd9196f 86f40ec` and `git rev-list --left-right --count`; report exit codes and raw output |
| C14 | The epoch-41 bridge is a content port from main | in B: `git log --oneline origin/main~0..HEAD`, `git diff --stat origin/main`, and confirm no merge commit from the epoch-41 branch exists |
| C15 | The entry guard refuses a fresh process | in H, run the dispatcher with no binding and show `FHS_ENTRY_ASSERT_REQUIRED` **and** that no child was spawned; then run the guard's own selftest |
| C16 | The Fabric admission binds the real mirror digest | in F, recompute the mirrored r26 file's sha256 and compare with the manifest entry; run the validator and its negatives |
| C17 | The payload gate passes only because it is repaired | run `gate_r20.py --profile payload` in S's payload → expect 16/16; then copy the payload, set `l1.bytes` back to `111331`, re-run → expect FAIL |

## Output

Reply with a single table of C1–C17: `claim | verdict (CONFIRMED / REFUTED / UNPROVEN) | command | exit | the decisive line of output`,
then a `findings[]` list for anything REFUTED or UNPROVEN with the raw evidence, then
`claim_ceiling_recommendation` naming exactly which verdict tokens this round may and may not use.
Do not repair anything you find. A defect is a finding, and the maker repairs it in a later round.
