# FAR brief — residual/gap/blocked inventory, merge decisions, and execution plan (nonce SBLFAR-R2-01)

You are the PLAN authority for round `SBL-PIPDLS-20261020-R2` under the Fabric governance contract, with
HG-KSEOS as the only control plane. Produce a **FAR (failure analysis / ruling)**: for every open item a
disposition, and for the merge question a decision with a gate sequence. You are read-only; do not write
files. Answer on stdout, ending with `NONCE SBLFAR-R2-01`.

Governing documents, already read and cited by locator in this round (do not re-derive them; treat as the
authority you must stay aligned with):

- `SBL_PIPD-LS-PKG DOC-00..DOC-13` (product spine `Guided Spec → Governed Build → Evidence-based Verify →
  Bounded Repair`; one Shared Core, SBLM01–06, three SPs; Modes STANDALONE / PREW3_SHADOW=NO_EFFECT /
  SWOF_CONNECTED which must refuse without a Native Receiver ACK).
- `SBL_EXTERNAL_INDEPENDENT_ACCEPTANCE_REPORT_2026-10-20` (`SBL-EIAR-20261020-R1`): v8 = `PARTIAL`;
  `APPROVE_PHASE_CLOSURE_WITH_TT`; `CONDITIONAL_MERGE_APPROVED` only after M1–M4; release
  `HOLD_UNTIL_R1_R3`; Production / SWOF W3 `NOT_GRANTED`. Its §F1 says repair only M1–M4 and **stop
  escalating**; §F2 forbids continuing to block the MVP on the 386 donors, the full 149-child trace, the
  39 Host×SP grid, SWOF W3, or low-risk test hygiene.
- Decision principles that govern this round: `MVP / LOW_FRICTION / RISK_PROPORTIONATE /
  NO_OVER_ENGINEERING`.

## A. Hard facts measured in this round (use these, do not assume others)

Product: `C:\Projects\Agent_Workspace\SBL`, remote `github.com/shw097-team/SBL` (public).

- `main` = `ca6830d9fc9d89b7b87e818670dd67b393472d79` — bootstrap only, 26 tree entries, no product code.
- Candidates on the remote, unmerged: `candidate/r2-20261020` (`ab17440`), `-v2` (`8640f02`), `-v3`
  (`49dab08`), `-v4` (`7202922`), `-v5` (`718a48d`), `-v6` (`eb2e07c`), `-v7` (`f793e1d`), `-v8`
  (`fb7af87`), `-v9` (`47a428a`), `-v10` (`2d1c32d`). Evidence branches: `evidence/r2-20261020-c1`
  (`31e9599`), `-c2` (`a1c7662`). Historical `wip/r2-r6-localpart` (`7f33e5c`).
- Current candidate `2d1c32d` (`candidate/r2-20261020-v10`), parent lineage v8 → v9 → v10.
- Local gates on `2d1c32d`: 11/11 `exit 0`; `G-SUITE-FULL` 137 passed; denominators
  `46, 10, 9, 18, 7, 7, 7, 4, 137`; `secret_scan` CLEAN 190 files, 0 hard findings; Python 3.12.14 and
  `py -3.11` green; a clean Python 3.11.9 venv installed from a copy green.
- Real GitHub CI on `2d1c32d`: run `39411780991`, jobs `118591058137` (ubuntu) and `118591058453`
  (windows), both `success`, each `136 passed, 1 skipped`, manifest self-check `{"ok": true}`.
- `v9` (`47a428a`) CI run `39411165230` **failed** on both platforms for two test defects that only a
  hosted runner exposes (a test needing the private corpus; a literal path compared against an 8.3 short
  name). Both fixed on `2d1c32d`.

Repair state on `2d1c32d`:

- **M1 CLOSED**: CI installs pytest before the suite; the step that could only fail on a runner (private
  mirror path) is replaced by `tools/verify_source.py --self-check`, which states
  `byte_verification: NOT_PERFORMED`; the second `-q` that erased the pytest summary is gone; a test
  asserts all of this.
- **M2 FIXED (maker side)**: `GovernedBuildBridge.apply` now resolves the real destination and re-checks it
  against the real root and writeset before writing; `SBL_E_WRITE_OUTSIDE_WRITESET` on escape; tests for
  escape, for an inside link that must still write, and for the lexical negatives.
- **M3 FIXED (maker side)**: the 2 MiB cap that silently dropped `DOC-05` (2,382,349 B) is above the
  largest book; skips are recorded as `coverage_gaps`; a question naming an unindexed source raises
  `SBL_E_KNOWLEDGE_NO_ANSWER`, one naming a skipped source raises `SBL_E_KNOWLEDGE_COVERAGE_GAP`; every hit
  is stamped `authority: NON_AUTHORITATIVE_LOCATOR`. CJK tokenisation, 61 Windows long-path files and
  semantic recall are **not** fixed and are declared limitations.
- **M4 NOT EXECUTED**: four dispatches of the mandated VERIFY route (`codex-cli`,
  `openai-codex/gpt-6.1-sol`, rank 2, `required_arm == served_arm`) failed identically:
  `codex_api::endpoint::responses_websocket: failed to connect to websocket: HTTP error: 426 Upgrade
  Required, url: ws://127.0.0.1:10101/v1/responses`. Measured lane state: relay `10101` serves HTTP
  (`/healthz` 200, `/v1/models` ok) but not websocket; `10102` identical; the lane-scoped doors
  `10103` (VERIFY) and `10105` (EXECUTE) are **down** (`000`); codex `0.163.0-alpha.10.2` rejects
  `-c prefer_websockets=false` as an unrecognised setting, so the client-side workaround is gone; the
  catalogue lists `gpt-5.6-sol` and 89 others by `slug`, never `gpt-6.1-sol`, so the client logs
  `Model metadata for gpt-6.1-sol not found` and uses fallback metadata. Every attempt still recorded
  `subject_mutation` 838 → 838 files, added/changed/removed 0, so the freeze itself held.

Skills / bases available and in use: `construction-acceptance-prompt-compiler` (C0–C9 compiler, four
stages, `PROMPT_COMPILE_PASS` on the CONTINUATION contract), `challenge-review` (independent challenge),
the 20 `00_KNOW_INDEX..19_KP_INDEX_CROSSWALK` KP documents, `GPTs_GENIEMAKER_設計實作 vol-01..10`,
`Fabric`, `PIPD-LS-SP` (eight skill roots), local `HG-KSEOS` (Kanban / Swarm / GStack / OpenSpec, lane
router, shared spine `var/shared-spine/hg-kseos.db`).

## B. The complete residual / gap / blocked / owner list to rule on

Rule on every line. Marker `D` = owner decision, `G` = governance gap, `H` = hold-scoped, `T` = technical
debt.

1. `M4` independent clean-room checker receipt on a frozen SHA (blocked by the lane transport above).
2. `R1` licence: repo has no `LICENSE`; `README` says "pending owner ruling"; donors and sources come from
   the owner's own corpus and public repos. Which licence, and what must accompany it.
3. `R2` reproducible package: pinned-SHA installable artefact, clean install → GJ01 → uninstall readback,
   manifest/SHA/notes.
4. `R3` native/HITL boundary: whether the public preview may claim HGK-governed effect at all, or must be
   declared `STANDALONE_ONLY` until one real repo-mutating GJ02 carries WorkOrder/ECP/Permit/ExecutionBinding.
5. `VERIFY10-TOOLING-01`: `tests/test_core_modules.py:140` assumes `mkdtemp` is outside a git worktree (`T`).
6. G-KNOW limits: CJK tokenisation, 61 Windows long-path files (261–305 chars), semantic recall (`H`).
7. `50/149` child-requirement trace closure (`H`).
8. `39` Host×SP ModeGate grid, real-host effective load (`H`).
9. `CR-ORACLE-001`, `N14_PROVISIONAL`, Profile/GRP missing artefacts (`G`/`H`).
10. Donor ledger: 441 rows, ACTIVE 1 / NATIVE_SUBSTITUTED 6 / STANDBY 3 / PROHIBITED 8 / DEFERRED 423;
    160 of 386 keys are governance rules rather than techniques; `METHOD-18` has no source evidence (`H`).
11. Missing gate IDs `TS11` / `CHK09` — the requirement exists in `DOC-00 R04.r3`, `DOC-01 R08.2A`,
    `DOC-06 C32-C33` but no gate carries the id (`G`).
12. GitHub `main` is unprotected; the branch-protection API returns `403` to this connection, so absence of
    rulesets is not proven (`G`).
13. `SWOF` W3 Connected: correctly refused without a Native Receiver ACK (`D` by SWOF owner).
14. Ten unmerged candidate branches plus two evidence branches and one wip branch on the remote — what to
    keep, what to delete, what to merge.
15. Kanban board `sbl-pipdls-20261020` (7 cards closed for the v1–v8 work) is stale for M1–M4; the board
    CLI was not reachable in this session (`T`).
16. OpenSpec change `sbl-v01-candidate-build` is validated at v8 state; the v10 delta is not in it (`T`).

## C. The questions you must answer (the owner asked exactly these)

1. For every item in §B: **how it closes**, or **who must decide**, with the lowest-friction route that is
   still honest. No item may be left without a disposition.
2. Which candidate artefacts and skills are **worth landing** (practical, reusable, low friction), and
   which should be dropped rather than maintained.
3. **Which unmerged candidates should go to `main`**, in what order, through what gate sequence — given
   that M4 (independent receipt) is unavailable today. State plainly whether the honest answer is "merge
   `2d1c32d` now with a declared receipt gap", "merge nothing until M4", or something else, and defend it
   against the report's own §F2 (which forbids using unrelated items to block the MVP).
4. How to **close M4 without breaking model SoD** while the relay cannot serve websocket. Rank the options
   by friction: restart the lane doors; enable ws on the relay; register the `gpt-6.1-sol` slug; authorise
   a different checker principal; accept a documented procedural alternative.
5. Licence recommendation for `R1`, with the compatibility reasoning, and what the owner must sign.
6. Branch hygiene: which of the 13 branches stay, which are deleted, and what the rollback pointer is.
7. An **execution plan** the orchestrator can run today: ordered steps, exact commands or acceptance
   checks, what each step proves, and where a human signature is required.

## D. Constraints you must respect

- Low friction, risk proportional, no over-engineering. Do not propose rebuilding the product, a new RAG
  pipeline, a new governance document set, or a 386-item installation programme.
- Do not propose weakening a security test, moving a denominator, or `continue-on-error`.
- Do not propose claiming `INDEPENDENT_CASE_PASS`, `MERGED`, `RELEASED`, `PRODUCTION` or `SWOF_CONNECTED`
  on evidence that does not exist.
- The owner pre-authorises your ruling and expects the orchestrator to execute it; so the ruling must be
  executable by an orchestrator with a shell, git, the GitHub token locator, and no checker lane.
- Prefer disposals that survive the next external review unchanged.

## E. Output format — one JSON object, nothing after the closing nonce line

```
{
  "nonce": "SBLFAR-R2-01",
  "items": [{"id": "M4", "disposition": "CLOSE_NOW|OWNER_DECISION|DEFER|DROP|HOLD_SCOPED",
             "route": "...", "why": "...", "effort": "XS|S|M|L", "owner": "<role>"}],
  "land": {"crew": [{"artefact": "...", "verdict": "LAND|DROP", "why": "..."}]},
  "merge": {"decision": "...", "target_sha": "...", "order": ["..."], "gates": ["..."],
            "receipt_gap": "...", "defence": "..."},
  "m4": {"recommendation": "...", "options": [{"option": "...", "friction": "...", "risk": "..."}]},
  "licence": {"recommendation": "...", "reasoning": "...", "owner_signature": "..."},
  "branches": {"keep": ["..."], "delete": ["..."], "rollback_pointer": "..."},
  "execution_plan": [{"step": 1, "action": "...", "command_or_check": "...", "proves": "...", "hitl": false}],
  "claim_ceiling_after": "...",
  "risks": ["..."]
}
```

End with the line `NONCE SBLFAR-R2-01`.
