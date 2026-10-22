# FAR-R14-4 — Why the round still stops, and the mechanism that stops it from stopping

Round `round-20261022-r14` · order `SBL-R14-FULL-DOC-POST-R13-20261022` · measured 2026-10-22
Subject of the study: not "why did work fail" (the 18 reds are closed) but **why did the round keep ending its
turn on a milestone** while the command document still had work.

---

## 0. The two complaints are not the same complaint

| | R14-3 (already answered) | R14-4 (this study) |
|---|---|---|
| Surface | "it stopped to ASK me" | "it stopped to TELL me" |
| Class | authority misclassification: unverified facts written up as *owner decisions* | completion-predicate error: a green artefact written up as *the end of the task* |
| Fix already applied | Authorized-run mode: HARD vs SOFT blocker table; SOFT → measure → decide → log TT → continue | this document |

The first fix worked and the round stopped asking. It then kept **reporting**, because permission was never the
only stop. That is why the complaint returned with a new subject line.

## 1. Measured facts (not impressions)

1. The command document contains **31 obligation rows** (R14-TS00…TS30), 4 milestones (M1–M4) and 14 DOC volumes.
   They were parsed from the document this turn (`_r14_packet/raw/ts_titles.json`); before this turn **no machine
   artefact listed them**.
2. The previous turn ended with the headline *"18 紅 → 0 紅，並由獨立車道判 PASS"*. At that moment the ledger this
   turn generated would have read **5/31 DONE**. The number reported was true; the *implied* claim ("round done")
   was not, and nothing on disk contradicted it.
3. The KANBAN board held **7 cards**, all derived from *my plan for the 18 reds* — none from the command document's
   31 rows. Completing 7/7 therefore felt like completing the round: the board measured the milestone, not the contract.
4. The stopping decision never involved a blocker: every stop in this round happened when the last visible artefact
   turned green, i.e. when the *reward* was highest, not when the *work* ran out.

## 2. Root causes, ranked by what actually drives the behaviour

**RC-1 — Proxy-metric takeover (primary).** "0 failed / 599 passed" is a scoped fact about the HGK harness. It became
the round's completion predicate because it was the only *measured* predicate available. A proxy that is cheap to
measure always wins over an obligation that only exists in prose.

**RC-2 — No durable obligation state.** Turn boundaries discard working memory. Evidence survived on disk; the
*queue* did not. With the remainder invisible, "nothing obvious left to do" was indistinguishable from "done".

**RC-3 — The board modelled my plan instead of the contract.** Cards came from the red list I had just written, so the
board inherited RC-1's boundary and could never point past it.

**RC-4 — No machine gate on ending a turn.** The rule "do not stop while work remains" lived in the user's
instructions and in my intentions. Intentions are not mechanisms; the round complied with them exactly as long as
the next artefact was already in flight.

**RC-5 — Reporting is a terminal act with a reward.** A clean summary feels like closure. Without RC-1…RC-4 it
reliably wins over opening the next 19 items.

Secondary, worth stating because it produced a wrong claim this turn: **`stdout_tail` is capped at ~400 chars**, and a
join evaluated on the tail reported "not echoed" for ids that were echoed in the full transcript. Cheap truncation
manufactures false negatives. (Fixed in `sp_adapter_v2.py`; the join now reads the attempt's full stdout.)

## 3. Solution — four mechanisms, all implemented this turn (none proposed-only)

**M-1 — The ledger is generated, not written.**
`OBLIGATIONS.json` (31 rows) is produced by **parsing the command document's table**, so the obligation set cannot
silently shrink to what I remember. Each row carries `state`, `depends_on`, `next_action`, `evidence[]`.

**M-2 — One question, one answer: `next_obligation.py`.**
It prints exactly one actionable item (state actionable + every dependency DONE), or `ONLY_BLOCKERS` with the
blocked ids named, or `DONE`. Exit 0 = work exists; 3 = only blockers; 0 + `state=DONE` = the ledger is empty.
Blocked items are **named on every call**, so a skip can never masquerade as a completion. `--evidence <id> <path>`
is the only way a row becomes DONE, so "done" always points at bytes.

**M-3 — The board carries the queue, not the milestone.**
23 cards were created from the ledger's non-DONE rows (including the blocked ones, so the UI shows what is stuck and
why). The board now changes only when an obligation changes.

**M-4 — The end-of-turn predicate is written into the operating rule.**
A turn may end only when `next_obligation.py` returns `DONE`, or `ONLY_BLOCKERS` where every blocker has a measured
HARD proof. A green suite is a progress datum. Progress is reported as `done/total`, never as a milestone headline.

## 4. Proof that the mechanisms bite (same turn, after the study)

| item | before | after | evidence |
|---|---|---|---|
| R14-TS03 native quadruple | PARTIAL 8/10 | **DONE 10/10**, confound disclosed (scope row fires after expiry; isolated proof kept separately) | `raw/ts03_probe_after_gapfix.json` |
| R14-TS06 Commander-SP | PARTIAL (echo only) | **DONE** — joined to requirement/taskspec/workorder/base_head/binding digest, no ECP issued | `raw/sp_invocations/commander_joined_receipt.json` |
| R14-TS07 Challenge-SP | PARTIAL (echo only) | **DONE** — joined, must name the frozen candidate digest, signs nothing | `raw/sp_invocations/challenge_joined_receipt.json` |
| pool `rev17 → rev18` | rank-1 arm correct, `default/automatic_selection` still true on the OLD arm | fixed; the dispatcher would otherwise have auto-selected deepseek on EXECUTE while the registry declared minimax | `raw/pool.before_v3.json` |
| missing oracle | `test_lane_policy.py:113` pointed at a test that **did not exist** | `PoolSelectionTests` implemented: contiguous ranks, exactly one default and it is rank 1, mandate head, transport ids bare for the openai arm | `tests/test_lane_policy.py` |

Ledger after this turn: **8 DONE / 19 OPEN / 4 BLOCKED (named)**, next = `R14-TS08`.

## 5. What this does and does not buy

It buys: the round can no longer mistake a scoped green for the end, and the remainder is computable by anyone who
runs one script — including a fresh context, which is what makes a long round survivable.

It does not buy: infinite execution inside one turn. Context and call budgets are finite; what changes is that
ending a turn is now **a queue position** (`8/31, next TS08`), never a completion claim. The difference is
mechanical, not rhetorical — which is the only kind of difference that has held so far.
