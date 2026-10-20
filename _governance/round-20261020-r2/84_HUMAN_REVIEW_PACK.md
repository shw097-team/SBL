# Human review pack — M4 by an independent human reviewer

This is what FAR option 5 looks like in practice, and the only remaining route while the mandated checker
provider refuses this code. It is written so a reviewer who did not build the product can finish in roughly
an hour, on evidence that is already in the tree.

**The orchestrator cannot fill this in.** If the reviewer is the owner, that is acceptable under FAR option 5
and the result is labelled `HUMAN_PROCEDURAL_ACCEPTANCE`, never `INDEPENDENT_CASE_PASS`. If it is a third
party, record their identity; separation from the maker is what matters.

## Subject

| Field | Value |
|---|---|
| repo | `github.com/shw097-team/SBL` |
| candidate | `candidate/r2-20261020-v13` @ `bedc11957d4fc2474b249b69d200829272c118ef` |
| base | `main` @ `ca6830d9fc9d89b7b87e818670dd67b393472d79` (unchanged) |
| hosted CI | run `39426671565`, both jobs success |
| prior receipts | `83_CHECKER_RUNS_15_17.md`, `evidence/checker/*` |
| packet | `76_ACCEPTANCE_PACKET.md` |

## How to get a working copy

```
git clone https://github.com/shw097-team/SBL
cd SBL && git checkout bedc11957d4fc2474b249b69d200829272c118ef
```

Then, with `C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe` (or any Python 3.11+):

```
python tools/run_gates.py                 # expect 11/11 exit 0, 148 passed in G-SUITE-FULL
python -m pytest -p no:cacheprovider      # expect 148 passed
python tools/secret_scan.py --root .      # expect CLEAN, 195 files, 0 hard findings
python tools/verify_source.py --self-check
```

`verify_source.py --verify` needs the private corpus and will report `ENV` without it; that is expected, and
`--self-check` is the check that runs anywhere.

## The six properties to sign off

Each one has a refused case and a working case. The tests named are the fastest way in; read them, run them,
then try one variant of your own.

| Property | How to see it | What "pass" means |
|---|---|---|
| GKNOW-ID | `tests/test_gknow.py::test_the_ids_the_real_corpus_uses_are_recognised` | real filenames such as `SBL_PIPD-LS-PKG_DOC-05.md` resolve to `DOC-05`; `DOC-27` is refused |
| GKNOW-SEP | `::test_separator_variants_of_an_unknown_source_are_refused` | `DOC/27`, `DOC--27`, `DOC27`, `doc_27` are all refused as unknown |
| GKNOW-BIND | `::test_a_named_source_constrains_the_answer_to_that_source` | a `DOC-05` question returns only `DOC-05` hits |
| MODE-ACK | `tests/test_modes.py::test_swof_refuses_an_ack_that_is_only_four_non_empty_strings` and `::test_swof_accepts_an_ack_signed_with_the_configured_key` | fabricated / untrusted / unsigned ACKs refuse; a correctly signed ACK still allows |
| MODE-SIG | `::test_ack_signature_cannot_be_moved_between_tuples` | two different tuples cannot share a signature |
| BRIDGE-SETTLE | `tests/test_core_modules.py::test_bridge_apply_refuses_a_path_that_changes_between_check_and_write` and `::test_bridge_apply_positive_inside_a_link_that_stays_inside` | a path that changes after validation is refused; an in-writeset write and an inside link still work |

Read `sbl_core/m04_bridge.py`, `sbl_core/modes.py` and `sbl_core/gknow.py` against those tests. The product is
small; this is the whole of the risky surface.

## What to look for beyond the tests

1. Does `README` still claim anything the code does not do? In particular `STANDALONE_ONLY` and the
   `SWOF_CONNECTED` refusal, now that the ACK is verified.
2. Does `SHIPPED_MATERIAL_INVENTORY.md` match the tree? (`git ls-files` and compare.)
3. Is any maker claim phrased as if it were independent? (It must not be.)
4. Any place where a refusal became a blanket refusal, or where an error path silently returns success.

## Sign-off block

Fill this in and commit it as `evidence/human/HUMAN_ACCEPTANCE_<date>.json` (or send it back and the
orchestrator will record it verbatim):

```json
{
  "schema": "SBL-HUMAN-PROCEDURAL-ACCEPTANCE/1",
  "reviewer_identity": "<name or handle>",
  "reviewer_independence": "<not the maker / owner-reviewing-own-product>",
  "subject_sha": "bedc11957d4fc2474b249b69d200829272c118ef",
  "date_utc": "<iso8601>",
  "checks_run": ["<command>"],
  "properties": {"GKNOW-ID": "pass", "GKNOW-SEP": "pass", "GKNOW-BIND": "pass",
                 "MODE-ACK": "pass", "MODE-SIG": "pass", "BRIDGE-SETTLE": "pass"},
  "findings": [],
  "verdict": "PASS | FAIL | PARTIAL",
  "label": "HUMAN_PROCEDURAL_ACCEPTANCE",
  "limits": "what this review did not cover",
  "carrier_note": "the mandated model provider refused this code; this review substitutes for that receipt"
}
```

With a `PASS` here and nothing else outstanding, the FAR merge sequence becomes executable: fast-forward
`main` to the reviewed SHA, read back, and record `MERGED`. Release still waits on `R2`.
