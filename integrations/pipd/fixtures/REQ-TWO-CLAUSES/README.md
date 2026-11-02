# REQ-TWO-CLAUSES / two different source clauses

Oracle: each atom carries file + clause id/span pointing at exactly one source clause; locators
never merge across clauses.

Positive case: `source.txt` and `source-b.txt` each state one requirement (near-identical wording
on purpose). Compiling both sources must yield two DISTINCT atoms whose source locators differ in
file and clause id/span. The old compiler bound every atom to `card['sources'][0]`, collapsing
both clauses onto one locator.

Negative case: a shared atom id or a shared locator across the two clauses must FAIL the oracle.
