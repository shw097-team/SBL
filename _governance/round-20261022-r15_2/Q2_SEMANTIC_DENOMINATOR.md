# Q2 — M4 semantic denominator: measured proposal

`source`: `tools/measure_semantic_denominator.py` (outcome `workers/q2_semantic/DENOMINATOR_PROPOSAL.json`,
unit index `workers/q2_semantic/UNIT_INDEX.json`). Orchestrator-exempt measurement: every number below comes
from one script run against the frozen DOC bytes, and reproduces by re-running it.

## Counting rule (stated so the count is checkable, not asserted)

- **unit** = an addressable clause heading (level 2–4) in a frozen DOC whose text starts with an ID token
  (`Rnn` / `Cnn` / `Unn` / `Fnn` / `Gnn` / `Knn` / `Pnn`, optionally dotted). Locator = `<file>:<line>`.
- **sub-obligation** = a sentence inside that unit carrying a normative marker (必須/不得/禁止/應/僅/一律/
  shall/must/MUST/SHALL/never/cannot/只能). Mechanical, not semantic interpretation.
- **cited_by_build** = the unit ID occurs at least once in the SBL worktree outside the DOC set
  (`src`/`tests`/`evidence_ledger`/`contracts`/`skills`/`openspec`/`tools`). A citation is a *trace* signal;
  it is not an oracle and not an acceptance.
- **unresolved** = a unit that carries ≥1 normative sentence **and** has zero build citations.

## Measured

| Quantity | Value |
|---|---|
Frozen DOC files | 14 (`DOC-00` … `DOC-13`), 17,473,442 bytes total |
Identified semantic units | **1,274** |
Units carrying normative sentences | 858 (12,744 normative sentences) |
Units cited anywhere in the build tree | **35** |
Units with normative content and **zero** build citation | **829** |
Duplicate clause IDs across DOCs | **143** (e.g. `C01.2`, `C02`, `C05.3` appear in more than one DOC) |
Authoritative semantic total | `NOT_ESTABLISHED` |
`FULL_SEMANTIC_PASS` | `false` |

Per-DOC clause units: DOC-00 50, DOC-01 116, DOC-02 55, DOC-03 73, DOC-04 86, DOC-05 225, DOC-06 36,
DOC-07 115, DOC-08 45, DOC-09 95, DOC-10 18, DOC-11 202, DOC-12 27, DOC-13 131.

## What this actually establishes — and what it does not

Establishes: the corpus has a countable clause structure, the count reproduces from bytes, and the
product's trace into that structure is **thin** (35 of 1,274 units are cited at all; 829 normative units are
cited nowhere). That is a finding about M4, not a formality: the earlier numbers in play (20 units,
1,743 structural packets) cannot be reconciled with 1,274 addressable clauses, so none of them was the
denominator.

Does not establish: an authoritative total, an applicability determination, an oracle per unit, or coverage.
143 duplicated clause IDs mean an ID alone is **not** a unique key across DOCs — any downstream mapping must
key on `(doc, clause_id)`, and the duplicate set is the first thing an authoritative pass has to reconcile.

## Printing, verbatim

> Measured proposal only: 1274 identified semantic units; 829 unresolved obligations; authoritative semantic
> total and FULL_SEMANTIC_PASS not established.

M4 stays `PARTIAL`; the proposal is the deliverable, the ceiling is unchanged.
