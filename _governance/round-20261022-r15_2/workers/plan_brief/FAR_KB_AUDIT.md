# PLAN brief — audit what I just built against the SBL knowledge base (mandatory grounding)

Owner directive: every FAR must be grounded in the SBL KB. Read these files at these locators before ruling; every
ruling needs `file#line`. If the KB contradicts the implementation, the KB wins and you say so plainly.

KB root: `C:/Projects/Agent_Workspace/知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL`

| locator | why it matters |
|---|---|
| `SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-07.md#3254` and `#3394` | the KB already defines an `independent_checker_ref` shape; my clause adds a principal registry, grants and ancestry. Does the clause agree with, extend, or contradict it? |
| `DOC-07.md#2400` | `sod_trust` filter marked PROVISIONAL_FILTER_ONLY — is separation of duties in the KB a filter or a law? |
| `DOC-13.md#713` | `C47.4 Loop C — SWOF W2 Frozen Shadow → W3 Native Admission (只讀到受權為止)` — the KB's own W3 conditions |
| `DOC-05.md#6080` | `W5 SWOF_NATIVE_STAGE_VERSION_UNRESOLVED` wording for a pending native stage |
| `DOC-11.md#969` | `idempotency_key: opaque, host-issued when applicable` — the KB's host-issued vocabulary |
| `DOC-00.md#14`, `DOC-01.md#16`, `DOC-05.md#17`, `DOC-13.md#20` | the KB's own `independent_checker: NOT_EXECUTED` claim-ceiling convention |

## What I built today (audit each; do not assume it is right)

1. `Fabric/FABRIC/control/SOD_POLICY.yaml` new block `principal_separation` (schema FABRIC-PRINCIPAL-SEPARATION/1):
   principal registry + pinned digest, identity = attested controller (not alias/session/model), grant records with
   ancestry, five predicates P0-P5, admissibility IDENTITY_SEPARATION_ADMISSIBLE / INADMISSIBLE -> NOT_ESTABLISHED.
2. `Fabric/FABRIC/assurance/principals.json` + `principals.pinned.sha256`: 4 principals, 2 grants, owner as trust root.
3. `tools/check_principal_separation.py` (offline, exit nonzero on fail) + `tests/test_principal_separation.py`
   (11 tests: admissible pair, same principal, alias of same controller, model-name-is-not-a-principal, unregistered,
   delegation from producer, subject not frozen, expired grant, tampered registry bytes, no checker grant, stale attestation).
4. `Fabric/FABRIC/assurance/admissions/W3/W3-SWOF-R153-01.owner-attested.json`: status PENDING_SCOPE_CONFIRMATION,
   signature null, ceiling OWNER_ATTESTED_W3_AUTHORIZATION_RECORDED__NO_EFFECT_UNTIL_SCOPE_CONFIRMED.
5. `C21_HOST_ID_INVENTORY.json`: three bundles frozen with zip+manifest sha256; host ids null; blocker recorded as
   Cloudflare interstitial on the CLI browser + no CDP endpoint; the proven R5Y path needs FDA foreground control.

## Answer these, with citations

Q1 Does `principal_separation` contradict `independent_checker_ref` in DOC-07? If yes, give the exact edit that makes
   them one doctrine instead of two.
Q2 Is `IDENTITY_SEPARATION_ADMISSIBLE -> NOT_ESTABLISHED on failure` consistent with the KB's claim-ceiling convention
   (`independent_checker: NOT_EXECUTED`)? Or should the failure verdict use the KB's own vocabulary?
Q3 Does DOC-13 C47.4 impose conditions on W3 that my PENDING_SCOPE_CONFIRMATION record violates or omits? Name them.
Q4 Is 'host-issued' in DOC-11 the same object as a ChatGPT plugin id, or something else that my C21 inventory
   conflates? If it differs, say what C21 may and may not claim.
Q5 Which KB document is the authority for the SBL release seal (C24), and does deferring it violate any ordering rule
   the KB states?

## Output

{"citations_used":["path#line"],"q1":{"verdict":"AGREE|EXTEND|CONTRADICT","why":"...","edit":"exact text or null"},
 "q2":{...},"q3":{"conditions_missed":[...],"edit":"..."},"q4":{"verdict":"...","c21_may_claim":"...","c21_may_not":"..."},
 "q5":{"authority_doc":"...","deferral_ok":true|false,"why":"..."},
 "corrections":[{"file":"...","what":"<=120 chars","why_cited":"path#line"}],
 "unresolved_in_kb":["questions the KB genuinely does not answer"],
 "claim_ceiling":"..."}

If a cited locator does not contain what this brief claims, say so explicitly - do not paper over it.
