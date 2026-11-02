# C1 — Operation/Effect Registry Reconnaissance

Scope: `SBL`, `PIPD`, `Fabric`, `HG-KSEOS` under `C:/Projects/Agent_Workspace`.
Date: 2026-11-03. Read-only; nothing added, committed or modified outside this directory.

Question: does an **original Operation/Effect Registry** exist — an authoritative mapping
`operation_type -> effect_class` carrying an **owner** and a **version / policy epoch**?

---

## 1. Exact commands run

```bash
cd /c/Projects/Agent_Workspace

# 1a. filename sweep (registry-like names)
find SBL PIPD Fabric HG-KSEOS -type d \( -name .git -o -name node_modules -o -name __pycache__ \) -prune \
     -o -type f -iname '*registry*' -print
rg --files -g '!**/.git/**' -g '!**/node_modules/**' -g '!**/__pycache__/**' -g '!**/site-packages/**' \
     -g '!**/.venv*/**' SBL PIPD Fabric HG-KSEOS \
  | grep -iE 'operation.?registr|effect.?registr|effect_?map|operation-types|operation_types|effects\.json|effect_?class|EffectClass'

# 1b. term sweep
rg -l -g '*.json' -g '*.yaml' -g '*.yml' -g '*.py' -g '!**/.git/**' -g '!**/node_modules/**' \
   -g '!**/__pycache__/**' -g '!**/site-packages/**' -g '!**/.venv*/**' \
   -e 'effect_class|EffectClass|operation_type|opentype|HOST_OPERATIONS|REMOTE_RELEASE' \
   SBL PIPD Fabric HG-KSEOS

# 1c. the decisive schema-name test
rg -n -g '!**/.git/**' -g '!**/site-packages/**' -e 'OperationRegistry' SBL PIPD Fabric HG-KSEOS

# 1d. value-set sweep
rg -l -e 'REPOSITORY_WRITE|HOST_OPERATIONS|REMOTE_RELEASE' SBL PIPD Fabric HG-KSEOS   # 62 files
rg -n -e 'effect.ceiling|effect_ceiling|EFFECT_CEILING' HG-KSEOS PIPD Fabric

# 1e. KB design matrix + enum absence
rg -n 'effect_class|effect class' SBL/sbl-tpm-sp-0.2.0rc1/references/corpus/sbl/SBL_PIPD-LS-PKG_DOC-0{4,5}.md
awk 'NR>1430 && NR<2100' .../SBL_PIPD-LS-PKG_DOC-05.md | grep -oP '^\| `[^`]+` \| `[^`]+` \| `[^`]+` \| `\K[A-Z_]+' | sort | uniq -c
ls PIPD/schemas/*.schema.json | wc -l          # 19
rg -l '"enum"' PIPD/schemas/*.schema.json | wc -l   # 0

# 1f. live readers
rg -n 'from \.registry|registry\.(load|families|EXPECTED)' PIPD/src/pipd_ls_sp/*.py
rg -n 'OperationRegistry|operation_registry|effect_registry' Fabric HG-KSEOS PIPD/src PIPD/tools
```

---

## 2. Hits table

| # | Path | What it actually is | Live / historical |
|---|------|---------------------|-------------------|
| 1 | `PIPD/schemas/registry.json` | `schema: PIPD-S0-CONTRACT-REGISTRY/1`. The **19 contract families** (§7.3), each with `contract`, `owner: PIPD`, `consumers`, `required_fields`, `schema_file`. Contract inventory — **no operation types, no effect classes**. | LIVE (read at runtime) — but not an effect registry |
| 2 | `PIPD/src/pipd_ls_sp/registry.py` | Loader for #1: `EXPECTED_FAMILIES = 19`, `SOURCE_ORDER`, `SCHEMA_SEAM_ONLY_UNTIL_S5/S6`. | LIVE code |
| 3 | `PIPD/src/pipd_ls_sp/validate.py:11,40` / `workspace.py:11,54,173` | The only runtime readers of #1/#2 (`registry.load_schema`, `load_registry`) — schema lookup for contract validation. | LIVE consumers (schemas only) |
| 4 | `PIPD/schemas/ECP.schema.json:28-36` | `effect_class` = `{"type":"string"}` — **no enum**. Carries `x-s0-vocabulary: {status: CANDIDATE_VOCABULARY_PENDING_OWNER, source: "PKG_02_DOC_B1_PD ...; 0 hits in SBL KB DOC-00..13", values: [READ_ONLY_PROBE, REPOSITORY_WRITE, HOST_OPERATIONS, USER_DATA_EFFECT], to_close: "Owner ratifies the value set, then collapse to enum and update registry.json required_fields"}`. | LIVE schema, **self-declared unratified** |
| 5 | `PIPD/src/pipd_ls_sp/pipeline.py:384-389` | The only runtime *decision procedure* for effect_class: `"REPOSITORY_WRITE" if scope and not scope.startswith(("/", "C:", "\\\\")) else "HOST_OPERATIONS"`. Path/scope-prefix heuristic; comment states it is "derived from the permission the ECP actually grants … rather than asserted". | LIVE code — heuristic, not registry-driven |
| 6 | `PIPD/docs/evidence/R21-FAR-20261101/s5/patch/PIPD/src/pipd_ls_sp/pipeline.py` | Patched copy of #5, same prefix derivation. Plus `tools/*.py`, `wp12/*`, `wp13/grant_envelope.json`, `ledgers/S6_EDGE_EFFECT_LEDGER.json`, `SESSION_STATE.json` — per-run envelopes carrying an `effect_class` value. | HISTORICAL evidence |
| 7 | `SBL/sbl-tpm-sp-0.2.0rc1/references/corpus/sbl/SBL_PIPD-LS-PKG_DOC-05.md:1428-2100` | Design matrix "Mode × ProductKind × EffectClass × Host 576 條預期路由 (F09)", 8×3×8×3 = 576 rows, **fully written out**: column 4 counts exactly 72× each of `UNINSTALL, TEST, ROLLBACK, RESTORE, READ, DEPLOY, CODE_WRITE, BACKUP`. Keyed `(ProductKind, ProductStatus, Mode, EffectClass, Host) -> route` — i.e. the **inverse direction** of `operation_type -> effect_class`, and a markdown table, not a machine artifact. Header itself says all `NoEffect default=YES`; it is a *design* route, not native authority. | DESIGN / historical text |
| 8 | `SBL/.../SBL_PIPD-LS-PKG_DOC-04.md:884` | `TaskNode@1 = {..., effect_class, ...}` — the field name exists; no value set, no enum. | DESIGN text |
| 9 | `SBL/.../SBL_PIPD-LS-PKG_DOC-05.md:1327` | `unique(effect_instance=(subject,effect_class,target,lane,stage))` — consumes the field, does not define its values. | DESIGN text |
| 10 | `SBL/sbl-tpm-sp-0.2.0rc1/references/index/authority-registry.json` | `schema: SBL.AuthorityRegistry@1`, `bindings: []` (**empty**), `state: NO_RATIFIED_BINDINGS_IMPORTED`, note "Family codes and source hashes do not issue authority". Name-match only: SBL **authority** registry, and it carries zero bindings. **Structural precedent** for an `SBL.*Registry` artifact with an authority state, but no `OperationRegistry` member. | LIVE file, empty by design |
| 11 | `HG-KSEOS/ops/session-20261031/tools/owner_window.py:44,246` | `EFFECT_ORDER = ["READ_ONLY_PROBE","REPOSITORY_WRITE","HOST_OPERATIONS","USER_DATA_EFFECT"]`, enforced: `if req.get("effect_class") and EFFECT_ORDER.index(...) > cap: refuse("REFUSED_EFFECT_CLASS_ABOVE_WINDOW")`. A hard-coded **ordered privilege ladder** for signing windows. No schema, no owner field, no version/epoch, no authority_state; script-local (committed in `287c8df`). | LIVE code — ceiling gate, not a mapping |
| 12 | `HG-KSEOS/config/issuer/OWNER_AUTHORIZATION.json:50` | `--effect-ceiling REPOSITORY_WRITE` appears inside `authorization_quote` (owner prose quoting a command). No code accepts that flag. | HISTORICAL / prose |
| 13 | `Fabric/stage/RP002-STAGE-HGK/POLICY/RP002_CHANGE_CLASS_ROUTER.staged.json` | `class_count: 9`, `class_names` = CONFIG_PREAPPROVED / CONSTITUTIONAL_CHANGE / DOMAIN_CHANGE / PIPELINE_CHANGE / PROFILE_CHANGE / PROVIDER_UPGRADE / RUNTIME_TRANSIENT / SKILL_CHANGE / STACK_CHANGE → `route`. **Change classes, not effect classes**; filename says `.staged`. | STAGED (not active) |
| 14 | `Fabric/evidence/LANE-RELIABILITY-CLOSURE-20261016/implementation/canonical/config/lane-routing-registry.yaml` | Model-lane routing. Header: "STATUS: CANDIDATE … NOT accepted, NOT promoted, and NOT active." | HISTORICAL / candidate |
| 15 | `HG-KSEOS/scripts/host_matrix.py` | Parses a 192-cell `Kind×Mode×Host×legacy` matrix out of a delivery markdown for **evidence completeness**. No effect classes. | LIVE tool, unrelated axis |
| 16 | `*_SIDE_EFFECTS.json`, `delegation_effects.jsonl` | Name-match only: R7 side-effect inventories / delegation effect logs. | HISTORICAL |

### Decisive negative results
- `rg 'OperationRegistry'` over all four repos → **0 hits.** The schema name the candidate adapter demands (`SBL.OperationRegistry.Binding@2`, `pre_v2_adapter.py:210`) exists **only inside the candidate adapter itself** (outside these four repos). No file, doc, or type in SBL/PIPD/Fabric/HG-KSEOS declares it.
- `PIPD/schemas/*.schema.json` → 19 files, **0 containing `"enum"`**.
- No file named `*operation*registry*`, `*effect*registry*`, `*effect_map*`, `operation-types.json`, `effects.json` anywhere in the four repos.
- Fabric: **0 hits** for `operation_type`, `effect_class`, `REPOSITORY_WRITE`, `HOST_OPERATIONS`, `REMOTE_RELEASE`. No Fabric policy code reads any registry.
- No name-matched `*HARD_BLOCKER*` document found on disk, although `ECP.schema.json` cites "FAR_HARD_BLOCKERS_20261027.md B-3" as the closure path.

---

## 3. Registry readers (question 3)

| Consumer | Reads an operation/effect registry? |
|---|---|
| PIPD `validate.py` / `workspace.py` | Reads `schemas/registry.json` — the **contract** registry only (`load_schema`). Never reads an effect mapping. |
| PIPD `pipeline.py` | Does **not** read any registry to classify effect; derives `effect_class` from a path/scope prefix (#5). |
| Fabric policy | No registry read; no effect-class terms at all. |
| HG-KSEOS issuer | Enforces `EFFECT_ORDER` as a hard-coded ladder (#11); reads no registry file. |
| Candidate adapter (`pre_v2_adapter.py`) | **The only reader that demands an operation registry**, and it refuses without one: `need(...schema=='SBL.OperationRegistry.Binding@2' and authority_state in (...),'OPERATION_REGISTRY_UNBOUND')`, then `rows=[r for r in operation_registry.get('operations',[]) if r.get('operation_type')==operation]`, `need(len(rows)==1,'OPERATION_TYPE_UNKNOWN_OR_DUPLICATE')`, `effect=row.get('effect_class')`. |

So: the only reader is the candidate adapter. Every live consumer either ignores effect classification (schema loaders, Fabric) or replaces it with a hard-coded heuristic (PIPD pipeline, HGK effect ladder).

---

## 4. Candidate registry fields (question 4)

No candidate registry exists, therefore **no path, no sha256, no schema, no owner, no version/epoch, no authority_state can be pinned.** Three disjoint vocabularies exist, and none is an authoritative registry:

| Vocabulary | Where | Size | Owner ratified? | Version / epoch? | authority_state? |
|---|---|---|---|---|---|
| V1 `READ, TEST, CODE_WRITE, DEPLOY, BACKUP, RESTORE, ROLLBACK, UNINSTALL` | SBL KB DOC-05:1430 (576-row design table) | 8 | No (design text; "真原生決策由 SBL DOC01, DOC11, PIPD DOC05, SWOF/HGK Native Owner 取交集") | No | No |
| V2 `READ_ONLY_PROBE, REPOSITORY_WRITE, HOST_OPERATIONS, USER_DATA_EFFECT` | `PIPD/schemas/ECP.schema.json` `x-s0-vocabulary` | 4 | No — `CANDIDATE_VOCABULARY_PENDING_OWNER` | No | No (`to_close` says owner must ratify then collapse to enum) |
| V3 same 4 literals, ordered | `HG-KSEOS/.../owner_window.py:44` `EFFECT_ORDER` | 4 | No | No | No |

V2's own schema records that its values have "0 hits in SBL KB DOC-00..13" — so V2 and V1 are irreconciled, and V3 silently reuses V2's literals in a script.

### sha256 of the files that would have to change (for reference, not a pin)
```
c58a8f3ed42808ba20f0102bb6fc7074d4fa321ea779879aa5ceefc6864d1de8  PIPD/schemas/ECP.schema.json
85100a8e5ba6320f6648d33a14099fb999b2c452a94aff1652854d2550065e9d  PIPD/schemas/registry.json
da689a174a6f0fe5e09e82e1d64d31a49a3872bec7acc79cd9027f1b662bf8ad  PIPD/src/pipd_ls_sp/pipeline.py
3b47a0b6224b1984a4047cf53aac5ac50615c93a560fea46e1b43d079a5d9f27  SBL/.../SBL_PIPD-LS-PKG_DOC-05.md
d2a4ff4f6f58943012878d09d5c07157c89b81f7fa6ccbea413d9c5e2645bbf0  _candidate_sbl_tpm_sp_20261102/patch/pipd-wt/src/pipd_ls_sp/pre_v2_adapter.py
```

---

## Verdict

**EFFECT_REGISTRY_UNBOUND** — no original Operation/Effect Registry exists in SBL, PIPD, Fabric or HG-KSEOS. `SBL.OperationRegistry` has zero occurrences in all four repos; the 19 canonical PIPD schemas contain zero enums; and every live consumer either ignores effect classification or substitutes a path-prefix heuristic (`pipeline.py:388`) / hard-coded ladder (`owner_window.py:44`).

**One precise interface gap.** A single machine-readable artifact must be created that the candidate adapter already knows how to consume:

- **File that would have to exist:** `PIPD/schemas/operation-registry.json` (+ companion `PIPD/schemas/OperationRegistry.schema.json`), registered as a family row in `PIPD/schemas/registry.json` (`PIPD-S0-CONTRACT-REGISTRY/1`) so `pipd_ls_sp.registry.load_registry()` can pin it by content hash.
- **Schema name required by the consumer:** `SBL.OperationRegistry.Binding@2` (`pre_v2_adapter.py:210`) — declared nowhere today; it must be authored, not discovered.
- **Shape required:** `operations[]` rows of exactly `{operation_type, effect_class}`, unique per `operation_type` (`OPERATION_TYPE_UNKNOWN_OR_DUPLICATE` otherwise), plus top-level `schema`, `owner`, `version`/policy epoch, and `authority_state` ∈ {`SYNTHETIC_ONLY`, `SOURCE_BOUND_OWNER_UNVERIFIED`}.
- **Owner that would have to ratify it:** PIPD as contract owner (every family in `registry.json` carries `owner: "PIPD"`), with the effect_class value set signed by the sole owner/issuer in `HG-KSEOS/config/issuer` — because the value set is currently `CANDIDATE_VOCABULARY_PENDING_OWNER` and irreconciled between V1 (8 KB classes) and V2/V3 (4 classes).

Until that file exists with a ratified value set, C1 cannot pin a registry; the adapter's `OPERATION_REGISTRY_UNBOUND` refusal is correct and should stand.
