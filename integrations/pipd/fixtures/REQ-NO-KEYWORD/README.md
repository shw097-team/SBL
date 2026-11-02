# REQ-NO-KEYWORD / no-keyword requirement

Oracle: atom existence is clause-driven, not keyword-driven; zero keyword matches must not mean
zero atoms.

Positive case: `source.txt` states two requirements that match none of the five keyword axes
(每頁保留三列 / 標題置中). Both must compile to atoms. The old intake raised
`IntakeInvalid: goal produced zero requirement atoms` for exactly this input - it treated
'a requirement exists' as 'five keyword axes are present'.

Negative case: reporting zero atoms for this clause set must FAIL the oracle.
