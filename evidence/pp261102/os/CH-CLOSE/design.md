# Design — rc.2 closeout decision record

Three decisions were made in this round. Only one of them (`D1`) touched code, and it was merged before
this record; `D2` was a decision **not** to change code; `D3` is the promotion ruling this record exists
to preserve.

## Context

`validate --bundle` reported `{"checked": 3, "closure": "FULL", "verdict": "PASS"}` on a bundle that was
missing its TQAEP. Every individual claim in that line was true: three records were checked, the trace
graph among those three resolved, and every check that ran passed. The line was still the sole input to
a conclusion it could not support — "the four-object set is complete" — because no field in the result
answered *which objects were supposed to be there*.

That is the shape of the defect worth recording: not a missing check, but a result that cannot be quoted
at its real denominator.

## D1 — the four-object denominator belongs in the validator

**Added** (`RELEASE_FOUR` in `validate.py`, merged `7073fe2` / PR #26):

| field | answers |
|---|---|
| `scope` | `FOUR_OBJECT` when `missing == []`, else `PARTIAL_BUNDLE` |
| `required` | the denominator, emitted literally |
| `missing` | which required objects are absent |
| `complete` | `missing == []` |
| `--require-four` | turns an absent object into a `DENOMINATOR` finding and a non-zero exit |

Why:

1. **The claim was already being made.** The closeout quotes "checked 4" and the round verdict depends on
   four objects existing. A number that is load-bearing must be emitted by the tool that computed it,
   not counted by hand in a markdown file.
2. **`scope` is derived, not configured.** It comes from one constant, so the label, `required` and
   `missing` cannot disagree, and a future fifth required object is a one-line change with no second
   place to forget.
3. **Enforcement stays opt-in.** A scoped validate is a legitimate operation (LITE slice, single-record
   re-validation after a repair). Defaulting to strict would have converted every existing scoped
   invocation from `PASS` to `FAIL` — a breaking change disguised as hardening. `--require-four` is one
   word away for the caller who is about to quote completeness.
4. **The failure lands in its own class.** A `DENOMINATOR` finding groups "you checked the wrong thing"
   apart from "a record is invalid", which is the same class the existing empty-bundle guard (`C-4`)
   already uses for `checked=0`. Zero of four and three of four are the same error at different scales.

This is why `HOST-124`'s sibling finding `FIND-VALIDATE-CLOSURE` is answered by `D1` and not by a
separate completeness pass.

## D2 — `closure` is not redefined

**Rejected alternative:** make `closure` return `PARTIAL` / `FAILED` unless all four objects are present,
on the theory that `closure: FULL` was the misleading token.

Rejected, for three reasons:

1. **It breaks legitimate closure.** `closure_findings` operates on the trace edges of the records that
   are present. A single `PI-PKG` closes against its own nested atoms with nothing else in the bundle;
   that graph *is* fully closed. Labelling it `PARTIAL` would make a true statement false, and the LITE
   slice — which validates exactly that shape — would start reporting a defect that does not exist.
2. **It destroys a working signal.** `FULL` / `SCHEMA_ONLY` / `FAILED` distinguish "edges resolved",
   "no edges to resolve" and "orphan or hash-mismatched edge". Folding denominator state into that field
   leaves no field answering "are the trace edges sound?", which is the question the trace-closure
   repair exists to answer.
3. **It converts passing tests into rewritten tests.** Three assertions in
   `tests/test_s4ext_trace_closure.py` (lines 99 / 106 / 114) and two in
   `tests/test_s4ext_first_run_portable.py` (lines 162 / 187, the CLI string) pin `closure: FULL` on
   bundles that are *not* four objects. Redefining `closure` either breaks them or forces them to be
   edited — and editing a test to accommodate a semantic change is how a broken invariant becomes an
   invisible one. Two orthogonal fields cost one extra key; one overloaded field costs a regression.

The ambiguity also would not have gone away: a reader seeing `closure: PARTIAL` still would not know
*which* object was missing, so a second field would be needed anyway, at which point the original
meaning had been spent for nothing.

## D3 — the round stops at the sidecar

`PRE_V2_DESIGN_SIDECAR_READY`, not `PRE_V2_GENERATION_READY`.

The second label is normally read as "nice to have, nearly there". It is not that here. It requires two
artefacts that do not exist, and inventing either one would be the exact failure this round was built to
detect:

| missing artefact | what it would license | state |
|---|---|---|
| pinned original Operation/Effect Registry | an **effect-specific** ECP (typed effect class, not generic) | `EFFECT_REGISTRY_UNBOUND` |
| canonical shape for host-authored objects | canonical ACK on the natural-goal route | `CANONICAL_ACK_HOLD` |

Everything else about the round is real: the package installs on a real Codex host, the model route
served, the natural goal produced three planning documents and four `@2` objects that pass the author
gate, the denominator is enforceable in the validator, and design-level governance ran on zero
approvals with 6/6 refusals. None of that proves a typed effect or a host-side canonical ACK, and the
honest label for "the design sidecar is ready and the effect side is not" is what was chosen.

## Next owner action

**One action, one owner: bind the original Operation/Effect Registry.**

Not "write a registry". The action is to obtain the *authoritative* one — or the Fabric/HG-KEOS reader
that owns the mapping — and pin it by digest so an effect class can be resolved from it rather than
inferred. The path heuristic that exists today (`REPOSITORY_WRITE if scope and not scope.startswith('/',
'C:', '\\\\')`) is explicitly forbidden as a classifier by the control plan; using it would close the
finding on paper and produce a wrong effect class in practice.

What binding it buys:

- a typed ECP can be compiled and validated, so G04 stops being a hold;
- the four-object bundle can then be quoted at `effect_state` beyond `DESIGN_ONLY_NOT_ADMITTED`.

What binding it does **not** buy: it does not make host-authored `@2` objects canonical, and it does not
produce an issuer, a protected checker or a grant. Those stay `NATIVE_GOLDEN_HOLD`.

Order of work from here — each step is a separate round, and no step may be claimed from the one before:

1. Bind the registry by digest; compile and validate a **typed** ECP. This closes the first blocker.
2. Resolve the canonical ACK question one way: have the host write canonical shapes, or add a declared
   `@2`-aware path to the reader. Until then the natural-goal route is `PASS_WITH_CANONICAL_ACK_HOLD`.
3. Only with both closed may the host path be proposed for `PRE_V2_GENERATION_READY` — and Native
   qualification would still require an original issuer, checker and publisher, which is a separate
   track and not implied by `GENERATION_READY`.

## Consequences and risks

- **A reader that prints only `verdict` can still overstate completeness.** `scope`/`complete` sit in the
  same result object, and `--require-four` exists for the moment of quoting; a consumer that ignores both
  is a follow-up in another repo, not silently patched here.
- **Stale evidence outlives the fix.** The archived `validate.out` files predate `D1`, so a reader of the
  published tree sees the old shape. Tracked as a re-capture task, not a code task.
- **The `@2` gap is structural, not cosmetic.** If a later round "fixes" it by loosening the canonical
  reader's `required` list, the canonical guarantee is gone. The legitimate options are the two named in
  step 2.

## Not decided here

No decision on the native track, on release, on a second approval path, or on the `HOST-124` sandbox
defect. Recording them as open is deliberate: a closeout that decides everything it touches cannot be
audited.
