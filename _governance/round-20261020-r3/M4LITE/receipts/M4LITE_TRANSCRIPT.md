# M4-LITE raw receipts

subject_head: `bedc11957d4fc2474b249b69d200829272c118ef`
reviewer (declared): `ORCHESTRATOR_AUTOMATED_PROCEDURE (not a signature)`
subject_mutation: **CLEAN** (183 files / 1243314 B, digest `c4d6f6d46fa6ef40…`)
all_cases_ok: **True**
verdict: **HOLD_PENDING_HUMAN_SIGNATURE**

| case | kind | executor | ok | observed / reason |
|---|---|---|---|---|
| `AC-M4-01/POS` | POS | independent_probe | PASS | `{"ok": true, "resolved": {"DOC-00.md": "DOC-00", "SBL_PIPD-LS-PKG_DOC-05.md": "DOC-05", "SBL_PIPD-LS-PKG_DOC-13.md": "DOC-13"}}` |
| `AC-M4-01/NEG` | NEG | independent_probe | PASS | `{"details": null, "message": "the question names a source id that is not in the index", "ok": true, "raised": "SBL_E_KNOWLEDGE_NO_ANSWER"}` |
| `AC-M4-02/NEG` | NEG | independent_probe | PASS | `{"ok": true, "variants": {"DOC 27": {"details": null, "message": "the question names a source id that is not in the index", "raised": "SBL_E_KNOWLEDGE_NO_ANSWER"}, "DOC--27": {"det` |
| `AC-M4-02/POS` | POS | independent_probe | PASS | `{"hits": 1, "ok": true}` |
| `AC-M4-03/POS` | POS | independent_probe | PASS | `{"doc00_hits": ["SBL_PIPD-LS-PKG_DOC-00.md"], "doc05_hits": ["SBL_PIPD-LS-PKG_DOC-05.md"], "ok": true}` |
| `AC-M4-03/NEG` | NEG | independent_probe | PASS | `{"details": null, "message": "the question names a source id that is not in the index", "ok": true, "raised": "SBL_E_KNOWLEDGE_NO_ANSWER"}` |
| `AC-M4-04/POS` | POS | independent_probe | PASS | `{"allowed": true, "no_effect": false, "ok": true, "reason": "NATIVE_ACK_VERIFIED"}` |
| `AC-M4-04/NEG` | NEG | independent_probe | PASS | `{"codes": ["SBL_E_REQUIRES_NATIVE_ACK"], "fabricated": {"details": null, "message": "SWOF_CONNECTED requires a verifiable native acknowledgement", "raised": "SBL_E_REQUIRES_NATIVE_` |
| `AC-M4-04/NEG-2` | NEG | independent_probe | PASS | `{"details": null, "message": "SWOF_CONNECTED requires a verifiable native acknowledgement", "ok": true, "raised": "SBL_E_REQUIRES_NATIVE_ACK", "refusal_form": "exception"}` |
| `AC-M4-04/SHADOW` | POS | independent_probe | PASS | `{"ok": true, "reason": "SHADOW_READ_ONLY_NO_EFFECT"}` |
| `AC-M4-05/NEG` | NEG | independent_probe | PASS | `{"delimiter_collision": false, "moved": {"details": null, "message": "SWOF_CONNECTED requires a verifiable native acknowledgement", "raised": "SBL_E_REQUIRES_NATIVE_ACK"}, "ok": tr` |
| `AC-M4-05/POS` | POS | independent_probe | PASS | `{"distinct": true, "ok": true}` |
| `AC-M4-06/NEG` | NEG | independent_probe | PASS | `{"ok": true, "outside_written": false, "raised": {"details": null, "message": "write target changed between validation and write", "raised": "SBL_E_WRITE_OUTSIDE_WRITESET"}}` |
| `AC-M4-06/NEG-2` | NEG | independent_probe | PASS | `{"link_kind": "junction", "ok": true, "raised": {"details": null, "message": "write target resolves outside the repository root through a link", "raised": "SBL_E_WRITE_OUTSIDE_WRIT` |
| `AC-M4-06/POS` | POS | independent_probe | PASS | `{"content": "value = 1", "ok": true}` |
| `GKNOW-ID/NEG/repo-test` | NEG | repo_test | PASS | `[".                                                                        [100%]"]` |
| `GKNOW-ID/POS/repo-test` | POS | repo_test | PASS | `[".                                                                        [100%]"]` |
| `GKNOW-SEP/NEG/repo-test` | NEG | repo_test | PASS | `["....                                                                     [100%]"]` |
| `GKNOW-BIND/POS/repo-test` | POS | repo_test | PASS | `[".                                                                        [100%]"]` |
| `MODE-ACK/NEG/repo-test` | NEG | repo_test | PASS | `[".                                                                        [100%]"]` |
| `MODE-ACK/POS/repo-test` | POS | repo_test | PASS | `[".                                                                        [100%]"]` |
| `MODE-SIG/NEG/repo-test` | NEG | repo_test | PASS | `[".                                                                        [100%]"]` |
| `BRIDGE-SETTLE/NEG/repo-test` | NEG | repo_test | PASS | `[".                                                                        [100%]"]` |
| `BRIDGE-SETTLE/POS/repo-test` | POS | repo_test | PASS | `[".                                                                        [100%]"]` |

raw json sha256: `b28337e2da2266a7a0f1c1e2b0f96fac56aa99f4c2abd540caf892d1f5974de3`
this transcript sha256 is recorded in the round manifest; it is not a signature.
