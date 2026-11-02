# 06 — Owner Decision and Closing (rc.2 four-item closure)

Round: 2026-11-03 Asia/Taipei. Supersedes none of the earlier raw results; it adds the four
remaining items (M1–M4) and records the promotion decision.

## Owner decision (one bounded authorization)

Approved and executed inside this scope: READ, isolated DRAFT, affected adapter/tests repair,
PR review and merge, and a promotion decision for the already-verified local Codex pre-primary
flow. Not granted and not claimed: any protected HGK effect, any independent checker verdict,
any release, any change to `~/.codex`, any push to a protected MAIN outside a merged PR.

## M1 — Operation Registry / effect-specific ECP: `EFFECT_REGISTRY_UNBOUND`

- The 19 PIPD schema families carry no operation-type or effect-class enum (inspected; zero enums).
- No original Operation/Effect Registry artifact exists in SBL, PIPD, Fabric or HG-KSEOS; the only
  `SBL.OperationRegistry.Binding@2` shape is the candidate adapter's own.
- The only effect mapping inside the original pipeline is a path heuristic in the R21 variant
  (`REPOSITORY_WRITE if scope and not scope.startswith("/", "C:", "\\\\")`), which the control plan
  explicitly forbids using as an effect classifier.
- Kept: the generic ECP from the original writer. No registry, issuer or grant was invented.

## M2 — PlannedTQAEP@2 author bundle: `PASS`

- Bundle: `evidence/pp261102/b/` (manifest, PI, PD, ECP, PlannedTQAEP, `source/test_billing.py`,
  `registry/operation_registry.json`, four fixtures, NOTE).
- Requirement ids and clause texts are the **original PIPD writer's**, for the same source bytes
  (`tests/test_billing.py`, sha256 `33170cc1…`). FUO, case ids and the operation-type registry are
  author-derived and labelled.
- Gate: `AUTHOR_CONTRACT_CONSISTENT`, requirements 2, cases 2, `effect_state=DESIGN_ONLY_NOT_ADMITTED`,
  `checker=NOT_RUN`, `release=FAIL_CLOSED`.
- Negatives all fail closed: missing PlannedTQAEP (exit 1); PI polarity flipped with re-signed
  manifest and candidate digests → `PI_TRACE_OR_ORACLE_MISMATCH`; injected
  `checker_execution_receipt` → `FORBIDDEN_DESIGN_KEY:$.checker_execution_receipt`.

## M2b — `validate --bundle` four-object denominator: `PASS` (merged)

- `scope` (`FOUR_OBJECT` | `PARTIAL_BUNDLE`), `complete`, `missing[]`, `required[]` added;
  `--require-four` fails closed with a `DENOMINATOR` finding.
- `closure` deliberately keeps its trace-graph meaning: a single PI legitimately closes against its
  own atoms, and three pre-existing tests assert exactly that. Redefining `closure` was rejected for
  that reason (see the OpenSpec design record).
- Tests: 4 new; full suite **664 passed / 20 skipped**. Merged to PIPD `main` as `7073fe2`.

## M3 — natural Goal routing: `PASS_WITH_CANONICAL_ACK_HOLD`

- Fresh Codex session, `deepseek-v4.1-flash` via `opencode_go`, no skill named in the goal.
- It fixed the defect (2 lines; two NEW tests added, no expectation edited), wrote
  `docs/product-requirement.md`, `docs/technical-architecture.md`, `docs/execution-plan.md`, and
  produced `docs/pipd/{PI,PD,ECP,PlannedTQAEP}.json` plus manifest/registry/source.
- Its own bundle passes the author gate (`AUTHOR_CONTRACT_CONSISTENT`, 2 requirements, 3 cases).
- **Canonical ACK fails**: the host-authored objects are `@2` design objects; the original canonical
  reader rejects them (`PI-PKG: Additional properties … 'stable_semantic_contract' is a required
  property`). Canonical ACK exists only for the writer chain (`01_products/pipd`, `checked 4`, PASS).
  Saying "the host produced canonical PIPD objects" would be false.

## M4 — thin governance at design level: `PASS_DESIGN_LEVEL`

- Two dependent design steps with **0** human approvals; the gate produced byte-identical results on
  both runs (KnownAnswer reuse, candidate `93387936…`).
- READ/DRAFT ran without a grant, without issuer contact and without an unrelated OPS/RELEASE gate.
- 6/6 design-level refusals pass: cross-subject, blind retry, nested fake grant, false-qualified,
  wrong host, nested receipt.
- Still `NOT_RUN`: G06/G07/G08 native autonomy, settlement and UNKNOWN recovery (no broker, no spine).

## Promotion decision (single, final for this round)

**`PRE_V2_DESIGN_SIDECAR_READY`** — not `PRE_V2_GENERATION_READY`, because (a) the effect-specific
ECP is unbound and (b) the canonical ACK covers the writer chain, not the host-authored objects.
**`NATIVE_GOLDEN_HOLD`** stands: no original issuer, checker or publisher was reachable, and the
lane mandate carries `nonce=None`, which is not an effect grant.

Local pre-primary use of the Codex flow stays limited to the verified, explicit/design-level path.
No host setting was switched: `~/.codex` and the real plugin cache were never modified, so the
"switch and roll back" step is a no-op rather than a claim.

## Pull requests

| PR | Repo | Result |
|---|---|---|
| #15 | SBL | rc.2 repair + the CLI-count correction (`dadeb91`); merged after CI |
| #18 | SBL | real-host evidence for rc.2; **merged** as `24d1205` |
| #26 | PIPD-LS-SP | additive pre-v2 adapters + four-object denominator; **merged** as `7073fe2` |

## Residual technical debt

1. `HOST-124`: `--sandbox workspace-write` makes Codex resolve `pwsh.exe` to the WindowsApps store
   alias, every `exec_command` is blocked by policy and the turn hangs to exit 124. `danger-full-access`
   was used for isolated diagnosis only; it is **not** an unattended default.
2. `EFFECT_REGISTRY_UNBOUND`: needs the original registry owner, not a fabricated one.
3. `AUTO_ROUTE` canonical leg: host-authored objects are `@2`; canonical ACK still requires the writer.
4. The pinned upstream patch (`pipd-pre-v2.patch`, sha256 `48b8846e…`) contains a superseded
   "14 commands" sentence in its docstring hunk. The patch bytes stay pinned as a historical
   artifact; the applied source was corrected separately in PIPD.
5. OpenCode Go key pool: two of three keys return `429 GoUsageLimitError`, one returns `401`.
