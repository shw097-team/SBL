# Checker runs 15–17 — three attempts, two receipts, six defects, no verdict

Three dispatches of the substitute independent checker (owner-authorised carrier, mandated model
`openai-codex/gpt-6.1-sol`, medium). Raw transcripts: `evidence/checker/`, digests below.

| Run | Nonce | Outcome | What it produced |
|---|---|---|---|
| 15 | `SBLR2-VERIFY-15` | completed, `ok:true`, 501.1 s, `subject_mutation` 912→912 clean | verdict **FAIL**, four MEDIUM product findings |
| 16 | `SBLR2-VERIFY-16` | cut off mid-run by the model provider | two reproduced escapes in the transcript, no verdict |
| 17 | `SBLR2-VERIFY-17` | cut off mid-run by the model provider, again | no finding recorded, no verdict |

| File | bytes | sha256 |
|---|---|---|
| `evidence/checker/VERIFY_15_receipt.json` | 15938 | `518099d0f6083d8b1a1217e240dcfec81b11ac9079da86ad20d82ce55005db06` |
| `evidence/checker/VERIFY_16_partial.txt` | 96 | `65c2190e57fb10bff1989551ec545cef27ae25b3269eda3e60e652c4595d4b90` |
| `evidence/checker/VERIFY_17_partial.txt` | 103 | `698bce4655f0c63314e3364125ed1c8ae9fa630872073df09f436b6dc33cfadc` |

## The six defects the checker found

Run 15, verdict `FAIL`, four findings, all reproduced by the maker before fixing:

- **`V15-GKNOW-01`** — `DOC_ID_RE` required `\b` before `DOC`, so the corpus's own filenames
  (`SBL_PIPD-LS-PKG_DOC-05.md`) never produced an identity. All 14 books indexed, 177 `DOC-05` chunks
  present, `indexed_doc_ids=[]`, and every real question refused with `SBL_E_KNOWLEDGE_NO_ANSWER`. My M3
  fix had made the honest refusal into a blanket one.
- **`V15-GKNOW-02`** — the named source was only checked for existence; scoring still ran over every chunk,
  so a `DOC-05` question returned `DOC-00` at score 1.0.
- **`V15-GKNOW-03`** — `DOC/27` and `DOC--27` bypassed the named-source refusal entirely.
- **`V15-MODE-01`** — the serious one: `SWOF_CONNECTED` accepted four non-empty strings as a "native ACK", so
  a fabricated ACK made `decide("net.call")` return `allowed=true, no_effect=false`. The product's README
  claimed the opposite.

Run 16, cut off before a verdict, two more from its transcript:

- **`V16-BRIDGE-01`** — junction swap between validation and write: the check and the `open` were two
  different instants, so replacing an allowed directory with a link in between escaped the writeset.
- **`V16-MODE-02`** — signature collision: the HMAC material joined the three fields with a bare separator,
  so `("issuer","a\x1fB","C")` and `("issuer","a","B\x1fC")` produced interchangeable signatures.

All six are fixed in the candidate line below, each with a test that fails without the fix.

## Why there is still no verdict

Runs 16 and 17 both ended with the provider refusing the content:

```
"This content was flagged for possible cybersecurity risk. If this seems wrong, try rephrasing your request.
If you're doing authorized security work that requires more cyber permissive safeguards, apply for Daybreak
access via https://platform.openai.com/settings/organization/status-and-access before retrying."
```

then `turn.failed`, after which the dispatcher's retry hit the known `426` websocket error. Run 17 used a
deliberately reworded brief; it was still refused, which places the trigger in what the checker *reads* —
the containment and signature code itself — rather than in how the task was phrased. Rewording is not a fix,
and deliberately obfuscating the material to slip past a classifier would be the wrong move, so it was not
attempted.

**Conclusion**: the mandated checker model, on this provider, cannot complete a review of this code. That is
a capability limit of the carrier, not a property of the candidate, and it is not something the orchestrator
may paper over by declaring its own results independent.

## Candidate line

| Candidate | SHA | Change |
|---|---|---|
| v11 | `b5fd5d0a4f9eddf91cb98d7c2aafd77776fca295` | R1/R3 product side: LICENSE, NOTICE, inventory, STANDALONE_ONLY |
| v12 | `815057dd7e8c1d9a2c982d9c56121081aa06dc21` | the four run-15 findings |
| **v13** | `bedc11957d4fc2474b249b69d200829272c118ef` | the two run-16 findings |

Hosted CI: v11 run `39420937990` (136 passed, 1 skipped ×2); v12 run `39423788123` (145 passed, 1 skipped ×2);
**v13 run `39426671565`, both jobs success**. Local: 11/11 gates, 148 passed, scanner CLEAN 195 files.

## What this means for the merge

The FAR ruling is unchanged and still governs: **merge nothing until M4 is satisfied**. A partial transcript
is not a receipt; a fixed defect with a test is not an independent confirmation that the fix holds. The merge
gate therefore stays closed, and the remaining options are the ones the ruling already listed: repair the
transport and re-run the mandated route, or an independent human reviewer performs the check and signs
`HUMAN_PROCEDURAL_ACCEPTANCE` (`84_HUMAN_REVIEW_PACK.md` is written for exactly that).
