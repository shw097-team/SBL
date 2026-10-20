# TS11 / CHK09 crosswalk — closing an identifier gap without manufacturing coverage

The external round recorded that gate ids `TS11` and `CHK09` do not exist anywhere in `DOC-00..13` or the
round state, while the requirement they were supposed to carry does. This file closes **the bookkeeping
only**. Where no executed evidence exists it says `NOT_IMPLEMENTED`, because an alias is not a test.

## 1. What the requirement actually is

| Locator | Requirement |
|---|---|
| `DOC-00 R04.r3` (`SBL_PIPD-LS-PKG_DOC-00.md:595`) | Six donors × 24 core slots: disposition decided from the original behaviour, and **no seventh compiler** invented |
| `DOC-00 R04.r3.1` (`:624`) | The 24 slots carry an executable functional contract, not a name list |
| `DOC-00 R04.r3.2` (`:652`) | The `386/386` universe split by authority: 226 technical items vs 160 historical rules, never merged into an "installed count" |
| `DOC-00 R04.r3.3` (`:883`) | `160/160` rule dispositions, which are rules and not 160 tools |
| `DOC-00 R04.r3.4` (`:1048`) | `25/25` methods with trigger, non-trigger, IO, contention and exit |
| `DOC-00 R04.r3.5` (`:1078`) | The 15 preferred wheels with a non-degrading selection threshold |
| `DOC-01 R08.2A` (`SBL_PIPD-LS-PKG_DOC-01.md:1985`) | All 386 ids, each with a typed admission behaviour and a silent-loss guard |
| `DOC-06 C32` (`SBL_PIPD-LS-PKG_DOC-06.md:126`) | Six method donors / 24 core capabilities: purpose, absorption and exit, per-slot design of `mode / host / permit / readback / revoke / rollback` |
| `DOC-06 C33` | The same universe's identity/authority treatment for the technical keys |

## 2. What exists today

| Artefact | Locator | Covers |
|---|---|---|
| 441-row disposition table | `_governance/round-20261020-r2/17_DONORS/DISPOSITION_TABLE.json` (sha `db412a60…`) | every donor row with a disposition: ACTIVE 1, NATIVE_SUBSTITUTED 6, STANDBY 3, PROHIBITED 8, DEFERRED 423 |
| Citation trace | `17_DONORS/TRACE.md` | 851 citations, 0 resolution failures |
| Gap register | `17_DONORS/GAPS.md` | `CR-386UNIVERSE` still open at `DOC-00:1437`; `METHOD-18` has no source evidence |
| Identity split | same table | 160 of 386 keys classified as governance rules, not installation obligations |

## 3. Coverage verdict

| Requirement | Covered by an executed gate? | State |
|---|---|---|
| R04.r3 / R04.r3.1 — six donors × 24 slots with a functional contract | No | `NOT_IMPLEMENTED` — the ledger records dispositions; no gate asserts the 24-slot functional contract |
| R04.r3.2 / R08.2A — 386/386 typed admission with a silent-loss guard | Partial | `PARTIAL` — the ledger enumerates all rows and their citations resolve; no gate fails when a row loses its source |
| R04.r3.3 — 160/160 rule dispositions | Yes, as data | `PRESENT_AS_DATA` — the 160 are classified; nothing asserts they stay classified |
| R04.r3.4 — 25/25 methods with trigger/non-trigger/IO | No | `NOT_IMPLEMENTED` |
| R04.r3.5 — 15 preferred wheels | No | `NOT_IMPLEMENTED` |
| C32 / C33 — per-slot design of mode/host/permit/readback/revoke/rollback | No | `NOT_IMPLEMENTED` |

## 4. Disposition

- `TS11` := **donor/slot/universe ledger and disposition completeness**. Existing artefact: the 441-row
  table. Gate coverage: `PARTIAL` (see §3). Scoped follow-up `TT-DONOR-GATE-01`: a gate that fails when a
  ledger row loses its citation or its typed admission field.
- `CHK09` := **the same requirement's check step**, i.e. verifying that no donor row silently disappeared
  between revisions. Gate coverage: `NOT_IMPLEMENTED`. Scoped follow-up `TT-DONOR-GATE-02`.

Both ids are now **named**; neither is claimed as tested. Per the FAR ruling this closes the identifier gap
and nothing else, and the two `TT`s are non-blocking for the MVP under report §F2.
