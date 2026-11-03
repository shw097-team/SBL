# CHANGE-pre-v2-final-acceptance

**Status:** decided, no code change in this round.
**Decision:** `PRE_V2_CLOSEOUT=NO` for `sbl-tpm-sp 0.3.0-rc.2`.

## proposal.md

### Why

The r2 blueprint closes the pre-repair phase only when every *applicable* one of the ten P0 views
carries a real read-back and the safety negatives do not regress. This round ran CT-00..CT-05
against the live host, the isolated Codex `CODEX_HOME`, and the original PIPD writer — now read
from its new home in SBL. Four views pass, six are held. Because two of the held views have no
evidence at all rather than weak evidence, the round cannot close.

### What is proven

- rc.2 identity: zip `3a9da655…` (173 members, 14 `SKILL.md`), installed copy byte-identical
  (`plugin.json` `48d704bc…`), enabled in an isolated `CODEX_HOME`.
- The canonical writer/reader moved: `PIPD-LS-SP` is archived, `SBL main b7445b0`
  (`integrations/pipd`, `pipd-ls-sp 0.1.1a5`) is canonical. It still yields 13 CLI verbs and
  19 schema families, and it accepts the same four-object bundle: `PASS / checked 4 /
  closure FULL / complete true / exit 0`.
- Refusals hold: wrong-schema ECP (exit 1), missing TQAEP under `--require-four` (fail closed),
  fake grant / cross-subject / blind retry / wrong host / nested receipt (5 named tests pass).
- Repo-level rollback was actually executed, and the defect returned (`1 failed, 1 passed`).

### What is not proven

- `P0_HOST_INVOKE`: rc.2 has **never** been executed by the host. The earlier "installed and
  loaded" impression belongs to `0.3.0-rc.1`; `HOST_ACTUAL_USED.json` records rc.2 as `NOT_RUN`.
- `P0_ECP_TYPED`: there is no original operation/effect registry to bind, so no effect-specific
  ECP exists; `EFFECT_UNBOUND` is carried, not worked around.
- `P0_ROLLBACK`: no host reload of the previous version.
- `P0_TQAEP_FUO`: planned only, no live checker receipt.

### No code change

Nothing under `integrations/pipd/`, `sbl_sp/` or the plugin source was modified. The evidence
bundle is additive.

### Not in scope

No `FHS_PIPD-LS-PKG_v2` package, no W0–W3, no native issuer/checker/publisher, no ChatGPT private
host, no host switch, no new governance plane, no second registry.

## tasks.md

- [x] CT-00 baseline — `00_BASELINE.json` (95 commands), `BASELINE_RAW.md`, `DRIFT_NOTE.md`
- [x] CT-01 planned/live separation — `TQAEP_DESIGNED` / `NOT_GRANTED`, fake receipts refused
- [x] CT-02 PI/PD identity — original IDs from the original writer; host label not passed off
- [ ] CT-03 typed ECP — **HOLD**, `EFFECT_REGISTRY_UNBOUND`
- [x] CT-04 case/Oracle/FUO — planned binding recorded, `RUNNER_UNBOUND` kept honest
- [ ] CT-05 host invoke — **HOLD**, no rc.2 host run; `HOST-124` unfixed
- [x] compatibility on the new canonical tree — 13 verbs, 19 families, `--require-four` exit 0
- [x] rollback at repo level — executed, defect reproduced
- [ ] rollback at host level — **HOLD**
- [x] adversarial precheck — 10/10 claims reproduced, 0 refuted

## design.md

### Why the round stops instead of stretching

The stop-loss rule is "same FirstFail, no new reason → do not retry". Two views are not FirstFails
awaiting a fix; they are absences of the only thing that could produce evidence. A host run needs
the host's model credentials, and that read was not authorised in this round, so the honest move is
to record the absence rather than to substitute the `danger-full-access` run — which the control
plan forbids as a qualification basis.

### Why the canonical-writer move does not change the verdict

Moving the writer into SBL preserved its ABI (13/19) and its four-object reader, and the round
re-ran the check against the new tree rather than trusting the old one. The move does not create an
effect registry, so `P0_ECP_TYPED` is unaffected.

### Why `P0_AUTHOR_TESTS` is downgraded

The previously quoted "664 passed / 20 skipped" has no archived log and was not reproduced here.
The five named safety negatives were re-run and pass; that is the part this round can stand behind.

### Owner actions

1. Fix `HOST-124` or use a policy-allowed restricted mode, then run one fresh goal and read back
   `Installed → Loaded → Invoked/Used`.
2. re-run the previous version reload for the host-level rollback leg.
3. Have the PIPD contract owner and the HG-KSOS issuer ratify an operation/effect registry as a
   registered family (no twentieth family without a compatibility analysis).
4. Re-adjudicate `PRE_V2_CLOSEOUT` once; the already-passing views need not be re-run.
