# AGENTS.md — SBL

Conventions an agent must follow in this repository.

1. **Candidate only.** Work lands on a branch and through a PR; nothing writes `main` directly.
2. **No force-push.** If a rewrite is unavoidable, preserve the old tip first and use `--force-with-lease`.
3. **Evidence before claims.** A PASS is a file with a sha256 and a command that reproduces it
   (see `b1_closure_20261028/EVIDENCE_INDEX.md`). An unmeasured statement is labelled as such.
4. **Never commit** databases (`*.db`), key envelopes (`*.enc`, `*.key`), raw lane output, or credentials.
   The push guard in the B1 closure round fails closed on them.
5. **Claim ceiling.** Local verification ≠ external acceptance ≠ release. State which one you have.
6. **One unlock, one signature.** Owner-key operations are batched; each passphrase prompt must cover
   every signature planned in that pass.
7. **Rollback points.** Promotion is a merge commit plus a tag; never a rewrite of history.

B1 closure scope for this repository: SBL side: GWO-SBL evidence and the SourceFreeze HOLD ruling (upstream act, not a package signature)
