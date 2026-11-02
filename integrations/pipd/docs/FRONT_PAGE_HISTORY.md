# Front-page history moved out of `README.md` (round R6, 2026-10-11)

In round **R6-20261011-main-front-page** the repository front page was rewritten from an
append-only log into a current-state page. Nothing here was deleted — the sections that used to
live on `README.md` and no longer belong on a front page are preserved **verbatim** below, with
their original headings and wording intact.

Two things moved here:

1. the **R3 audit-repair status** section (a dated snapshot that was being read as current state), and
2. the trailing **`## 8. Correction of a wording overclaim (round 2 finding)`** fragment — a
   numbered section with no sections 1–7 that had accumulated at the end of the file, plus the
   licence-gap paragraph it followed.

Original front page at the move: `README.md` in `main` @ `de3a1d9e3a6298fa0dd29fafbf11d850e30c743a`.

---

## R3 audit-repair status (2026-10-09, FW-10 / FW-12 / R-AUD-008 / R-AUD-012 / R-AUD-013)

True denominators, failures named — no percentage ever hides a hard FAIL:

| area | state | denominator |
|---|---|---|
| unit suite | see `.hgk/artifacts/STATUS_R3.json#tests` | `python -B -m unittest discover -s tests -t .` — real counts + named failing tests, raw log in the round receipt |
| knowledge readiness (`G-KNOWLEDGE-READY`) | **PARTIAL** | 160 unique sources / 153 physically indexed / 7 quarantined by the sanitizer; the 7 are now **owner-dispositioned** (2 `safe-clean`, 5 `safe-reference`, 0 undecided) in `.hgk/knowledge/QUARANTINE_DISPOSITION_R3.json`. The physical number stays 153/160 — it is NOT padded to 160/160 — until `TT-HGK-SANITIZER-UNANCHORED-KEY-PATTERN` closes |
| quarantine negative controls | PASS | a live credential and an unframed injection are **not** released even when claimed harmless; an undecided item stays quarantined (`python tools/quarantine_review.py --report`) |
| TT / CR register | 17 rows | 1 CLOSED (fresh-verified) · 4 PARTIAL · 9 OPEN · 2 OPEN_OWNER_GATE · 1 TEMP_CLOSED — every row carries owner, current state, raw-evidence pointer and explicit close criterion (`.hgk/artifacts/TT_REGISTER.json`) |
| KP rule-polarity (`R-AUD-013`) | OPEN, resolved by the authorised source | `ORACLE_DISAGREEMENT` entry `OD-R3-001`: upper Evidence/Regression requirement prevails over the KP02/KP11/KP12 `MUST NOT` rows; KP files not edited; calibration negative keeps a genuine `MUST NOT` prohibition (`TT-ORACLE-DISAGREEMENT-KP-R04`) |
| PRE-W3 cross-project | **TEMP_CLOSED** | independently closed; never derived from S0–S4 evidence (`TT-PRE-W3-CROSS-PROJECT`, HITL owner required) |
| evidence-MD generator | refusal-protected | `tools/build_evidence_md.py` refuses to print PASS when any hard gate row is FAIL (typed `HARD_GATE_FAIL`, exit 2, no document written) |

> **Superseded in part by later rounds.** The TT/CR register figure above is the R3 snapshot; the
> R4 round recorded 22 rows / 18 blocking. Treat this table as history, not as current counts.

## License (as written on the R3 front page)

No license is granted — see `LICENSE`. The authoritative source corpus declares none; this is
recorded as source gap `TT-PIPD-LICENSE-001`.

> **Superseded (round R5Q, 2026-10-10).** The owner granted **Apache-2.0** for the limited
> S4 open-source preview, effective at the release commit carrying it (tag `v0.1.0-preview.1`).
> This paragraph is preserved as the R3-era record; see `README.md` for the current licence
> position on this branch and on the release.

## 8. Correction of a wording overclaim (round 2 finding)

README.md previously implied the knowledge layer introduced no new store and was read-only. Both were inaccurate: derived knowledge index built through the HGK SharedSpine typed API; it is a SEPARATE physical SQLite file that carries the HGK schema but contains ZERO governance rows (0 projects/requirements/taskspecs/workorders/events) and is never written by the orchestration plane. Correct description: 'derived, non-authoritative knowledge index' - not 'read-only' and not 'no second store'.
