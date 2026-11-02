# REQ-COMPOUND / compound clause fixtures

Oracle: compound expansion binds subjects to predicates 1:1; atom count == subject count.

Positive case: `source.txt` compound clauses (各有／分別／對應) must yield one DISTINCT atom per
subject binding, each with its own id, oracle and negative fixture.

Negative case: an ambiguous compound (cardinality mismatch) must be REFUSED - a semantic collapse
into a single keyword bucket is the R-AUD-005 defect.
