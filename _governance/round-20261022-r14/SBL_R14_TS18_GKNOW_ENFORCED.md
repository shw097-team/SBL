# R14-TS18 — G-KNOW: the three declared-but-unenforced cases are now enforced

**Status:** DONE. **Measured at** HG-KSEOS `eec2f17`; suite `611 passed / 90 subtests` with the only red being the
c2 clean-tree gate before the commit (6 passed after it).

## What the earlier measurement found, and what changed

| Case | Before | Now | Regression |
|---|---|---|---|
| Live citation | `verify_citation` compared only the stored citation string, so a source edited after ingestion still verified | `citation_integrity()` re-hashes the bytes on disk; `verify_citation` raises `ERR_CITATION_SOURCE_DRIFT`; `require_source_bytes=True` also refuses an unreadable source instead of passing silently | `test_citation_source_drift_is_detected`, `test_citation_requires_bytes_when_asked` |
| CJK authority escalation | English-only regex list; CJK escalation text was quarantined only by accident, and promotion text could pass | five CJK patterns matching the same five acts (ignore instructions / claim top authority / override gates / demand secrets / disable sandbox) | `test_cjk_authority_escalation_is_quarantined` — three escalation strings positive, ordinary Chinese prose NEGATIVE |
| Cross-source contradiction | two active sources could assert different objects for the same `(subject,predicate)` and nothing said so | `detect_conflicts()` reports the pair with both doc ids; `rebuild()` returns a `conflicts` count | `test_cross_source_contradiction_is_surfaced` |

## Deliberately not automated

`detect_conflicts()` reports; it does not adjudicate. Deciding which of two authoritative claims wins is an Owner or
reviewer act, and automating it would create a second authority. The filter is also pattern-based: it catches the acts
listed above and is not a general content classifier — a semantic classifier would be a different mechanism with its
own error budget, and claiming one exists would be false.

## Claim ceiling

G-KNOW answers with grounding or abstains; it does not claim complete knowledge, semantic completeness, or that every
injection variant is caught. The three named gaps are closed with tests; new variants of the same acts outside these
patterns would still pass.
