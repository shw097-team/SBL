# REQ-NEGATION / negation fixtures

Oracle: polarity follows the negation scope: 不得 clause -> MUST NOT; the prohibition and the
obligation never merge.

Positive case: `source.txt` holds a prohibition (系統不得交付遙測資料), its positive counterpart
(系統交付發行說明) and a distributive negation (測試與交付分別不得遺漏與延遲). All three must
compile to DISTINCT atoms with the correct MUST / MUST NOT polarity - the old keyword classifier
bucketed the prohibition under the same `release` axis as the obligation.

Negative case: an atom whose polarity is normalized away (prohibition rendered as MUST) must be
rejected by the oracle.
