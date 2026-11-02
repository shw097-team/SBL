# Design — naming the four-object denominator without breaking trace closure

## Principle

**A result must state the denominator it was computed against, and a name that already means something
must not be given a second meaning.** The bug was not a missing check — every record in the bundle was
checked, and the graph among them was closed. The bug was that the only two fields a reader looks at
(`checked`, `closure`) could not distinguish "all four objects closed" from "the three that were
supplied closed among themselves".

Two independent concepts were being carried by one word:

| concept | question it answers | field that now answers it |
|---|---|---|
| **denominator** | which objects were *supposed* to be present, and were they? | `scope`, `required`, `missing`, `complete` |
| **closure** | do the trace edges *among the present records* resolve? | `closure` (unchanged) |

## Decision

Add the denominator as new fields; keep `closure` at its existing meaning; make enforcement opt-in.

- `scope` is derived, not configured: `FOUR_OBJECT` when `missing == []`, else `PARTIAL_BUNDLE`.
  Deriving it from one constant (`RELEASE_FOUR`) means the label, the `missing` list and the `required`
  list can never disagree, and adding a fifth required object later would be a one-line change with no
  second place to forget.
- `complete` is a convenience boolean equal to `missing == []`. It exists because the common consumer
  question is binary, and asking a caller to test list emptiness invites `if result["missing"]:` on a
  `None`.
- `verdict` keeps meaning "did every check that ran pass". A partial bundle therefore still returns
  `PASS`: a scoped validate is a legitimate operation, and turning it into a FAIL by default would break
  every existing scoped workflow (the LITE slice, single-record re-validation after a repair).
- `--require-four` is where the caller states the claim ceiling it needs. When it is given and an object
  is absent, the failure is reported as a `DENOMINATOR` finding — the same `kind` the empty-bundle guard
  already uses — so a report groups "you checked the wrong thing" separately from "a record is invalid".
  Flag-off is the default because the safe default for a *scoped* tool is to answer the scoped question;
  the strict form is one word away for any caller that is about to quote completeness.
- `required` is emitted literally rather than implied by documentation, so a consumer can render
  "3 of 4" without hard-coding the four contract names, and so a stale doc cannot silently disagree with
  what the validator enforced.

## Rejected alternative — redefine `closure` to mean four-object completeness

The obvious minimal patch is to make `closure` return `PARTIAL` (or `FAILED`) unless all four objects are
present, on the theory that `closure: FULL` was the misleading token. **Rejected**, for three reasons:

1. **It breaks legitimate closure.** `closure_findings` operates on a bundle's trace edges, and a single
   `PI-PKG` closes against its own nested atoms with no other record present. That graph *is* fully
   closed. Calling it `PARTIAL` would make a true statement false, and the LITE slice — which validates
   exactly that shape — would start reporting a defect where none exists.
2. **It destroys a working signal.** `FULL` / `SCHEMA_ONLY` / `FAILED` already distinguish "edges
   resolved", "no edges to resolve" (a legal partial, labelled so it cannot be read as closed) and "orphan
   or hash-mismatched edge". Folding denominator state into that field leaves no field that answers
   "are the trace edges sound?", which is the question the S4EXT-R1 repair was built to answer.
3. **It moves the ambiguity instead of removing it.** A reader who saw `closure: PARTIAL` would still not
   know *which* object was missing, so a second field would be needed anyway — at which point the original
   `closure` meaning has been lost for no gain. Two orthogonal fields cost one extra key; one overloaded
   field costs a regression.

A second rejected option — making `--require-four` the default and adding `--allow-partial` — was dropped
because it silently converts every existing scoped invocation from `PASS` to `FAIL`, which is a breaking
change disguised as hardening, and because the failure would surface in callers that never asked about
completeness.

## Consistency with existing guards

- The empty-bundle guard (`C-4`) already refuses `checked=0` as a `DENOMINATOR` finding. This change is
  the same argument applied one level up: zero objects is not a verification result, three of four is not
  a four-object result, and in both cases the honest output names the gap rather than returning a verdict
  that overstates it.
- `checked` is untouched: it counts records actually schema-checked, so `checked=3` with
  `required` length 4 is now a legible pair instead of a contradiction.

## Testing strategy

Deterministic units only — no network, no native host. `tests/test_validate_four_objects.py` builds one
four-object slice through `pipeline` (`intake → compile_pi → bind_pd → compile_ecp → compile_tqaep`) and
derives the partial bundle by dropping `TQAEP`, so the two cases differ in exactly one object:

- four objects → `PASS`, `scope=FOUR_OBJECT`, `complete=True`, `missing=[]`, `closure=FULL`;
- three objects → `PASS`, `scope=PARTIAL_BUNDLE`, `complete=False`, `missing=["TQAEP"]`, `checked=3`;
- three objects with `require_four=True` → `FAIL`, a `DENOMINATOR` finding whose detail names `TQAEP`;
- the CLI surface itself (subprocess): default exits 0 and prints `PARTIAL_BUNDLE`; `--require-four`
  exits non-zero.

The regression requirement is carried by the pre-existing suites that assert `closure: FULL` on
non-four-object bundles (`tests/test_s4ext_trace_closure.py`, `tests/test_s1_lite_slice.py`): if anyone
later redefines `closure`, those fail without being edited.

## Risks and mitigations

- *A consumer reads `verdict` alone and still claims completeness* → `scope`/`complete` are in the same
  result object, and the strict flag exists for the moment of quoting; a reader that prints only `verdict`
  is outside this repo and is listed as follow-up rather than silently patched.
- *Denominator drift between doc and code* → one tuple, emitted as `required`; a doc that disagrees with
  the output is detectable by reading the output.
- *A future fifth required object* → adding it to `RELEASE_FOUR` changes `scope`, `missing`, `required`
  and enforcement together; no other site encodes the four names.
