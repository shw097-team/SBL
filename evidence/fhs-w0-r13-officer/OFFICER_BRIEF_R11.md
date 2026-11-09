# ACCEPTANCE OFFICER BRIEF — ROUND 11

You are the **Acceptance Officer** for round `FHS_W0_R13_ACCEPTANCE_20261108`.
Distinct process, distinct model, read-only, `VERIFY_ONLY`. Do not repair anything.

## What round 10 found

Round 10 reproduced a real divergence: under **your** restricted account `G19` returned
`ROOT_WALK_ERRORS` on `FHS_W0W2_R4_20261107/inc3/work/acl_probe2/protected_b2d1b6e9` (WinError 5, access
denied, including through the extended-length path), while the maker's run passed. The same program was
therefore giving two different verdicts depending on **who ran it** — and your negative control's baseline
collapsed with it, so `check_bites` read false.

## What was changed, and the reasoning

A subtree that is unreadable because it was **built** unreadable is a known fixture, not an unknown
region — but only if nothing the register declares lives under it. `g19_copy_register` now splits
traversal failures:

1. For each failure it extracts the path quoted in the error and asks whether **any declared member path
   starts with that directory**. If one does, the check refuses with
   `ROOT_WALK_ERRORS_OVER_DECLARED_COPY` — an exclusion can never hide a declared copy.
2. Failures whose path carries `acl_probe` or `protected_` and which cover no declared member are recorded
   as excluded fixtures and **counted in the output**.
3. Every other failure still refuses with `ROOT_WALK_ERRORS`.

This is why your round-10 finding mattered: without it, the check was green for the maker and red for you,
and neither of us could say which was true.

## What to check

Items 1–24 as before, plus:

25. **The exclusion cannot hide a declared copy.** Read the `walk_errors` branch of `g19_copy_register`.
    Confirm the `covers_declared` test uses the path parsed out of the error message and the same
    normalisation as the declared set, and that a hit refuses rather than excludes.
26. **Your own account is the test.** You run restricted; the maker does not. Run the gate as you did in
    round 10 and report whether `G19` now returns `OK` with the excluded-fixture count, or still refuses.
    If it still refuses, quote the error and the path — that is the finding, not a nuisance.
27. **The negative control must bite again.** With the baseline restored under your account, the member
    tampering case must still produce `MEMBER_DIGEST_DRIFT` and `check_bites: true`.

## Output format (STRICT)

```json
{
  "officer": "acceptance-officer/codex-cli/gpt-6.1-sol/round-11",
  "mode": "VERIFY_ONLY",
  "items": [{"id": 1, "claim": "label", "verdict": "PASS|FAIL|NOT_VERIFIABLE", "evidence": "what you read"}],
  "g19_under_your_account": {"verdict": "", "excluded_fixtures": 0, "detail": ""},
  "bundle_observed": {"rounds_on_disk": 0, "rounds_in_bundle": 0, "terminal_in_bundle": "", "matches": true},
  "negative_control": {"ran": true, "check_bites": true, "observed": ""},
  "overall": "PASS|NACK",
  "blocking_defects": [],
  "notes": ""
}
```

`PASS` only if you personally read the bytes. `overall` is `NACK` if any item is `FAIL`.
