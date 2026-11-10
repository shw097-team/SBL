# evidence/fhs-hermes-023-integration-20261110

Round evidence for **Hermes 0.23.0 × FHS W0→W1 integration**, 2026-11-10.
Verdict: **`PARTIAL_INTEGRATION`**. Claim ceiling: author-side measurement.

## Files

| file | what it is |
|---|---|
| `HERMES_023_FHS_W0_W1_INTEGRATION_RESULT.md` | the round's single report |
| `W0_023_COVERAGE_MATRIX.json` | 17 atoms / 9 edges / 22 WP · 36 edge identity / per-WP eleven fields |
| `MEASURE1_FREEZE.json` | gateway identity, W0 r26 three copies, 31 sources, 6 upper documents, repo context |
| `reader_and_quorum.txt` | the original reader (6/6) and the quorum scan (128 properties) |
| `OWNER_ACK_REDERIVED.json` | owner-ACK payload re-derived, Ed25519 verified, 6/6 receipt refs |
| `GATE_R26_ON_H23.json` | the round's own gate over the signed document: 21/22, 0 blocking, 1 open reporting |
| `NEGATIVES.json` | 4 baselines + 8 negative/consumer controls, all detected |
| `INTAKE_NACK_RAW.txt` / `INTAKE_CONTROL_RAW.txt` | the real `pipd intake` refusal (exit 2) and the accepting control (exit 0) |
| `WP19_LIVE.json` / `WP19_INVENTORY_V2.json` | live CI / licence / NOTICE / SBOM / dependency state of the three repos |
| `WIRING_CONSUMPTION.json` | E01 / E27 / E28 / E33 / E36 plus the four later-wave edges |
| `R4_FRESH_SESSION_GOAL.md` | a fresh session's ordinary goal, and why only one WP has a downstream readback |
| `INDEP_REDERIVATION.json` | counts re-derived without reading this round's JSON |
| `ADVERSARIAL_CHALLENGE.md` | the ten findings that forced this round's reclassification |

## Reproduce

```bash
cd C:/Projects/Agent_Workspace/FHS_HERMES_023_NATIVE_INTEGRATION_20261110
PY=D:/Hermes-Recovery/hermes-0230-stage/.venv/Scripts/python.exe
$PY tools/m1_freeze.py && $PY tools/m2_wp19_live.py && $PY tools/m7_wp19_inventory.py
$PY tools/m3_wiring.py && $PY tools/m6_negatives.py && $PY tools/m4_owner_ack.py && $PY tools/m5_matrix.py
```

The six signed reader receipts verify and are **not** per-WP acceptance: they bind candidate `r15` and
name one shared consumer. Do not cite them as six work packages accepted.
