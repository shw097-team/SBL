# Design — a count is a measurement, not a recollection

## Principle

**Every number in an evidence-bearing document is a measurement with a command behind it, and a
document that contradicts its own cited commit is a defect regardless of how plausible it looks.**
The overlay exists to describe an upstream tool exactly; a command count is one of the few claims in it
that can be settled byte-for-byte, which makes getting it wrong worse than getting a judgement wrong —
it is checkable, and it was not checked.

## The measurement

Counted at the commit the overlay itself cites (`f6335a94157c61da75d92121d14c43feb413e981`), by
enumerating subparsers in `src/pipd_ls_sp/cli.py`:

```sh
git show f6335a94…:src/pipd_ls_sp/cli.py | grep -o 'add_parser("[a-z-]*"' | wc -l   # → 13
```

`init  intake  profile  compile-pi  bind-pd  compile-ecp  compile-tqaep  validate  doctor  project
export  diff  repair` — thirteen names, `repair` included.

Two properties of this measurement matter for the record:

1. **It is inventory-shaped, not arithmetic-shaped.** The count is a list of names, so a later reader can
   see *which* command would be the 14th if one were ever added. "14" had no such list behind it, which
   is exactly why it survived review.
2. **`repair` being inside the 13 is the load-bearing part.** The 14 claim reads as "the thirteen plus
   repair", which suggests the counter treated `repair` as an addition to the canonical set. It is not:
   criterion E7 fixes the count at exactly 13 with no 14th, and `repair` is one of them. So the error was
   not an off-by-one in a tally; it mis-stated the composition of the inventory *and* asserted a
   forbidden total.

## Decision

Correct the three committed documents plus the accompanying evidence text to 13 with the qualifier
"(13 including `repair`; original E7 forbids a 14th)", and commit the correction on the repair branch so
the number is attributable to a revision.

Two supporting choices:

- **Keep the qualifier in the sentence.** "13" alone would be correct but silent about why 13 is not
  negotiable; the qualifier carries E7 to the reader at the point of use, which is the only place a
  future editor will look before "fixing" the number back.
- **Fix the evidence text together with the prose.** The private-overlay snapshot and its evidence are
  read as one artefact; correcting the prose alone would leave the defect alive in the evidence, where a
  reader is *more* likely to trust it because it looks like data. `summary.json` made the point sharply:
  it recorded `"actual_cli_count": 14` next to `"historical_cli_count": 13`, so the machine-readable
  "actual" value contradicted the "historical" one inside the same object. Only the actual field was
  wrong, which is the case that survives review longest, because the pair looks self-consistent at a
  glance.

## Rejected alternatives

- **Leave 14 and annotate it as disputed.** Rejected: the number is not disputed, it is wrong, and E7
  forbids the value. An annotation in a document whose purpose is exactness converts a measurement
  failure into an editorial stance.
- **Say "13 or 14 depending on counting method".** Rejected: there is no counting method under which the
  cited commit exposes 14 subcommands, and E7 removes the ambiguity by fixing the denominator. A hedge
  here would be false precision.
- **Fix only `PRE_V2_HANDOFF_20261102.md`.** Rejected: the routing contract and the upstream README are
  the two documents a downstream consumer is most likely to quote, and the README's version actively
  inverted the correction. A single-file fix would leave the strongest form of the error in place.
- **Add the CI grep guard in the same change.** Deferred rather than rejected: it is a defensible guard,
  but this change is a claims correction and CI configuration is a separate surface with its own review;
  the guard is recorded as an open owner decision in `tasks.md` instead of being smuggled in.

## Why this is not cosmetic

The overlay's downstream text derives claims from "the original PIPD CLI" — its command surface, its
compile/validate split, its receipt requirements. A stated inventory that includes a command set the
original does not have (or excludes one it does) is the kind of error that propagates: a consumer that
plans against 14 commands plans one command too many, and a checker that validates the overlay against
"14" would be validating against a document rather than against the source. The correction restores the
rule the overlay is supposed to follow — the source commit is the authority, and the document is a
reading of it.

## Risks and mitigations

- *Re-introduction by a later editor who "remembers" 14.* → The qualifier names E7 in the same sentence,
  the prohibition is written down in this change, and the verification command is a one-liner a reviewer
  can run.
- *A downstream copy of the 14 outside this repository.* → Stated as a consequence in the proposal rather
  than assumed fixed; those copies are outside this change's reach.
- *The count drifting if the upstream CLI changes.* → The claim is pinned to a commit hash, so a new
  upstream state requires a new measurement, not an edit to this sentence.
