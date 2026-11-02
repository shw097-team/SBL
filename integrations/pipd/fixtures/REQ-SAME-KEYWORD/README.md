# REQ-SAME-KEYWORD / same keyword, different meaning

Oracle: clause identity (file + clause id/span) is authoritative; keyword equality never merges
atoms.

Positive case: `source.txt` states two different requirements that share the keyword 驗收
(驗收報告 = the acceptance report vs 驗收門檻 = the acceptance threshold). The compiler must emit
two DISTINCT atoms (distinct id, oracle, negative fixture) even though the old five-axis
classifier bucketed both under `verification`.

Negative case: a merged atom carrying both clauses must be rejected by the oracle.
