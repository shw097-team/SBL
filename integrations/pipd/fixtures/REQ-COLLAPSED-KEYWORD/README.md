# REQ-COLLAPSED-KEYWORD / the negative fixture the old classifier falsely collapsed

Oracle: clause identity is authoritative: an obligation and its prohibition sharing one keyword
must stay two atoms with opposite polarity.

`source.txt` holds two DIFFERENT source clauses: the obligation 系統交付發行說明 and the
prohibition 系統不得交付遙測資料. The pre-R-AUD-005 five-keyword classifier matched 交付 in both
and emitted ONE REQ-DELIVER keyword atom - a prohibition silently collapsed into an obligation
bucket. `negative/case.json` records that old outcome as the rejected negative fixture; the
clause-bound compiler must emit two distinct atoms (MUST / MUST NOT) instead.
