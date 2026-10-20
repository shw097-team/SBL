# Owner decisions — 2026-10-20 (post-FAR)

Provenance: the owner read `80_FAR_RULING.md` and replied, in session, *「用戶授權簽FAR建議的四件事」* —
an instruction to sign the four items the ruling had left to the owner. This file records what was signed,
what it authorises, and what it deliberately does **not** authorise. It is an owner instruction recorded by
the orchestrator; it is not a cryptographic signature and does not create a checker receipt.

## 1. Acceptance route (M4)

Signed: the FAR's option 4/5 combination — **authorise a substitute independent checker**, run as a distinct
session against a frozen SHA, when the mandated `codex-cli` + `openai-codex/gpt-6.1-sol` carrier cannot
transport. Conditions the signature attaches:

- the substitute keeps the mandated **checker model** (`gpt-6.1-sol`, medium) and changes only the carrier;
- the receipt is labelled `SUBSTITUTE_CHECKER_RECEIPT`, never `INDEPENDENT_CASE_PASS`, and the carrier
  deviation is stated in the receipt itself;
- the checker runs read-only on a copy and must report `subject_mutation`;
- the orchestrator does not author the findings, only transcribes and hashes them.

Not signed, and not implied: any relaxation of the M1–M4 scope, any waiver of a failing finding, or any
permission to call a maker self-check an independent result.

## 2. `main` publication control

Signed: a **bounded manual merge control** in place of branch protection, because the protection API returns
`403` to this connection and ruleset absence is therefore unproven. The control names, at execution time:

- accepted candidate SHA and tree, and the base `main` SHA it was accepted against;
- the checks that passed (local gates, hosted CI run and both job ids, scanner verdict);
- the publication method (fast-forward only, no force, no bypass);
- readback proof after publication (`git ls-remote`, remote tree hash).

## 3. R1 licence

Signed: **MIT** for owner-controlled original code, on the strength of `SHIPPED_MATERIAL_INVENTORY.md`.
`LICENSE` (MIT, `Copyright (c) 2026 shw097-team`), `NOTICE` and the inventory ship with the candidate.
Excluded from the licence: the specification corpus, the 20 KP documents, the GENIEMAKER volumes, the
Fabric / PIPD-LS-SP / SWOF repositories, and the G-KNOW index — all of which are referenced, not redistributed.

Condition left open by the ruling and accepted here: if the owner wants a legal entity or natural person
named as copyright holder, that is a one-line change to `LICENSE` before any release tag.

## 4. R3 effect scope

Signed: **`STANDALONE_ONLY`** for this build and any preview derived from it, declared in `README.md` and
`NOTICE`. No HGK-governed effect is claimed; no WorkOrder/ECP/Permit/ExecutionBinding exists for it;
`PREW3_SHADOW` stays `NO_EFFECT`; `SWOF_CONNECTED` keeps refusing without a Native Receiver ACK.
A native-effect claim would require one real repo-mutating GJ02 with those artefacts bound, which this round
did not produce.

## What these four signatures do not do

They do not merge anything by themselves, do not create an independent PASS, do not authorise a release tag
or package publication (`R2` remains open, `HOLD_UNTIL_R1_R3` narrows to `R2` only), and do not authorise
production or SWOF W3.
