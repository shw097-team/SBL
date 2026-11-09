# ACCEPTANCE OFFICER BRIEF — FHS W0 r13

You are the **Acceptance Officer** for round `FHS_W0_R13_ACCEPTANCE_20261108`.
You are a **distinct process** with a **distinct model** from the maker. You run read-only.
You must **not repair** anything. If a defect exists, you report NACK and stop.

Your sandbox is `read-only`. You cannot write. Do not attempt to.

## What you are judging

A candidate document and its round evidence, on disk at:

```
C:\Projects\Agent_Workspace\FHS_W0_R13_ACCEPTANCE_20261108\
```

Key files (absolute paths, all readable):

| What | Path |
|---|---|
| Candidate document | `writeback\W0\FHS_PIPD-LS-PKG_W0_r13.md` |
| Revision manifest (chain + shipment) | `writeback\W0\W0_REVISION_MANIFEST.json` |
| Closeout decision | `writeback\W0\W0_CLOSEOUT_DECISION.json` |
| Gate result | `out\GATE_R13.json` |
| Gate selftest | `out\GATE_R13_SELFTEST.json` |
| Handover | `HANDOVER_R13_2026-11-08.md` |
| Owner window assessment | `out\OWNER_WINDOW_DEMAND_ASSESSMENT.json` |
| The gate itself | `tools\gate_r13.py` |
| Parent revision r12 | `writeback\W0\FHS_PIPD-LS-PKG_W0_r12.md` |
| 31 source documents (corpus) | `C:\Projects\Agent_Workspace\FHS_W1_Work_Final\FHS_W1_Work_Final\sources` |

## What the round claims

The round claims, and you must independently check each of these **against the bytes on disk**,
not against any summary written by the maker:

1. `FHS_PIPD-LS-PKG_W0_r12.md` is a **byte-exact prefix** of `FHS_PIPD-LS-PKG_W0_r13.md`.
2. The size and sha256 in `W0_REVISION_MANIFEST.json` for `r13` equal the actual file's size and sha256.
3. The `r12` chain entry's `parent_version` and `parent_sha256` name the **same file** (the label must not
   contradict the digest). Note: this entry carries a `parent_version_corrected_from` field; check the
   correction is internally consistent.
4. `W0_CLOSEOUT_DECISION.json` declares `completion_level = W0_AUTHOR_DESIGN_COMPLETE` and its `defects`
   map names every defect it calls CLOSED, and every such id appears in the document body.
5. The document does **not** state its own byte count or digest anywhere (self-reference check).
6. The document states the **parent's** size and digest, and they match the actual r12 file.
7. `ORIGINAL_ACK` is declared as 0/6 and is **not** claimed anywhere as obtained.
8. No claim of `formal_w0_acceptance`, `RELEASE_GRANTED`, `NATIVE_WORLDRAW`, or `INDEPENDENT_PASS`
   appears as an assertion of fact anywhere in the document or the round artifacts.
9. `GATE_R13.json` reports 0 blocking failures.
10. The gate's `G11` check really re-hashes the 31 source files (read `tools\gate_r13.py`, find `g11_line_convention`,
    and confirm it opens the corpus rather than reading a stored number).
11. The gate's `G13` really re-derives the in-set duplicate counts from the corpus (find `g13_count_scope`).
12. The gate's `G19` really re-hashes each declared copy and walks each declared root (find `g19_copy_register`).
13. The gate's `G22` is `REPORTING`, not `BLOCKING`, and its output carries the string
    `SELF_REPORTED_BY_THE_SUBJECT`.
14. `out\OWNER_WINDOW_DEMAND_ASSESSMENT.json` states a measured `required_signatures` and a reason for
    not opening the envelope. Check the number is consistent with the registry it names
    (`C:\Projects\Agent_Workspace\var\B1-PIPD-PKG-20261027\admission\registry\runner-registry.json`:
    count rows and count rows missing an owner signature).
15. The document's chapter 14.5 lists the same still-open items as `W0_CLOSEOUT_DECISION.json`'s
    `still_open` list, with no item silently dropped in either direction.

## Output format (STRICT)

End your reply with exactly one fenced JSON block, no prose after it:

```json
{
  "officer": "acceptance-officer/codex-cli/gpt-6.1-sol",
  "mode": "VERIFY_ONLY",
  "items": [
    {"id": 1, "claim": "short label", "verdict": "PASS|FAIL|NOT_VERIFIABLE", "evidence": "what you actually read and what it said"}
  ],
  "overall": "PASS|NACK",
  "blocking_defects": ["..."],
  "notes": "anything a reader must know, including anything you could not verify"
}
```

Rules for your verdict:
- `PASS` only if you personally read the bytes and they agree.
- `NOT_VERIFIABLE` if the file or the ability to check is absent — never silently upgrade it to PASS.
- `overall` is `NACK` if any item is `FAIL`. A `NOT_VERIFIABLE` does **not** force NACK but must be listed.
- You are not permitted to fix anything you find.
