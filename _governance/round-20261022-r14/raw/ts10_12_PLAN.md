# R14-TS10 / TS11 / TS12 — measured deployment and distributable plan

**Disposition: PLAN_READY / IMPLEMENTATION_NOT_ACCEPTED.** No repository, installed skill, HGK state, Git state, Host account or release was modified. Writes are confined to this `raw/` output directory. The word **proposed** below means design, not an observation or approval. `UNMEASURED` means no claim of success. This plan cannot grant Native authority.

## Evidence convention and reproducibility of this inspection

Every measured assertion cites `E###` in `ts10_12_measurements.json`, `X###` in `ts10_12_extra.json`, or the denial/CR file. These files contain the actual command/expression, exit status and full output, including file bytes as text and measured SHA-256. Appendix A gives command/output excerpts; full per-module digests are not paraphrased away. The actual inspection entry commands were:

```bash
python -B C:/Projects/Agent_Workspace/_r14_packet/raw/ts10_12_measure.py
python -B C:/Projects/Agent_Workspace/_r14_packet/raw/ts10_12_extra.py
```

Both returned exit 0. `-B`/`PYTHONDONTWRITEBYTECODE=1` prevented Python import cache writes. Workdir was `C:/Users/user`. PATH and the active Python environment were measured; this was **not** an exhaustive all-disks/all-profiles binary search. Other installations therefore remain UNMEASURED, not declared nonexistent.

### Normative locators actually read

- Round order: TS10–TS12 lines 152–154; CHK10–CHK12 lines 220–222; draft and authority constraints lines 78, 113, 197. Hash and exact selected text: X007.
- DOC-11: C29/C30 native chain and bounded recovery; selected exact source lines/hash: X004. No local adapter may become a second issuer.
- DOC-12: C36.3; C43 supplychain at lines 1299–1307 and 1443–1486; C-016..018 lines 1693–1695; reproducibility/BuildManifest.lock lines 1740–1742. Exact outputs/hash: X005.
- DOC-06: NOBJ-017 at lines 317, 753, 1174: quarantined / original deny / no activation. Exact outputs/hash: X006. The round explicitly prohibits promoting that Draft. Design-method mentions in DOC-12 are not an override.
- The claimed R13 CR path under `SBL/_governance/round-20261021-r13-native/` is **absent in this checkout** (E092); filename discovery found the copy at `C:/Projects/Agent_Workspace/_r13_far/CR-PLUGIN-SCHEMA-AUTHORITY.md` (X008). It was read and hashed, not treated as a new approval. Full copy/readback: `ts10_12_denials_cr.json` last record. Its clauses 1–4 say no draft shipping, no local-load-as-Host claim, and three HOST_PENDING surfaces until a new written non-draft Owner choice.

## A. Actual five-tool artifacts on this machine

Path abbreviations are exact, not guesses:

```text
H = C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes
S = C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent/venv/Lib/site-packages
P = C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent/venv/Scripts
K = C:/Projects/Agent_Workspace/HG-KSEOS
I = C:/Projects/Agent_Workspace/SBL-install
```

Installed distribution metadata says `sbl-v01==0.1.1rc1`, with `sbl-harness`, `sbl-stack`, `sbl-todo` console entrypoints (E015). The separate source checkout `C:/Projects/Agent_Workspace/SBL/pyproject.toml` says `0.1.0`, only `sbl-todo`, and `setuptools>=68` (E090). These are **different source/runtime baselines**, not zero drift.

| Tool | Actual current artifacts | Existence / broken surface / precise ceiling |
|---|---|---|
| TPM-SP | `H/skills/sbl/tpm-sp/{SKILL.md,README.md,plugin.json}`; installed implementation `S/sbl_sp/manifests/tpm_sp.json`, `S/sbl_sp/plugins/tpm_sp/SKILL.md` | E038–E043, E030/E036: all three deployed files exist; no `tpm-sp` PATH command (E004). README target `skills/tpm-sp/SKILL.md` is missing relative to deployed root; flat `SKILL.md` exists. Local skill read succeeded via skill_view; not Host invocation qualification. |
| Commander-SP | `H/skills/sbl/commander-sp/{SKILL.md,README.md,plugin.json}`; `S/sbl_sp/manifests/commander_sp.json`, `S/sbl_sp/plugins/commander_sp/SKILL.md` | E044–E049, E028/E032: exists, no `commander-sp` PATH command (E005); same README/layout failure. No real SP→WO invocation measured. |
| External Challenge-SP | `H/skills/sbl/external-challenge-sp/{SKILL.md,README.md,plugin.json,references/git-branch-ruling.md}`; `S/sbl_sp/manifests/external_challenge_sp.json`, `S/sbl_sp/plugins/external_challenge_sp/SKILL.md` | E050–E055, E029/E033: exists, no `external-challenge-sp` PATH command (E006); **same README defect here too**. Deployed SKILL differs from packaged skill; E051 vs E033 hashes differ. Do not overwrite its added review/reference material. |
| HGK Native upgrade + Harness | `K/_sbl_harness_adapter/{adapter.json,MANIFEST.json,plugin.json,skills/hgk-governed-runtime/SKILL.md}`; second adapter `I/hgk-adapter`; flattened skill `H/skills/sbl/hgk-governed-runtime`; `P/sbl-harness.EXE`; `S/sbl_harness/` | Native-root adapter doctor exit 0 / ROOT_READY / HOST_PENDING / NOT_GRANTED (E096); `I/hgk-adapter` doctor also exit 0 (X003). Flattened skill doctor exit 2: MANIFEST.json missing (E097). Native source/spine/registry/dispatcher paths exist per probe, but no Native upgrade acceptance was measured. No `hgk-governed-runtime` PATH command (E007). |
| Full SBL Stack | `P/sbl-stack.EXE`; `S/sbl_stack/{__init__.py,cli.py,SKILL.md}`; `I/stack/stack.json`; `H/skills/sbl/sbl-stack/SKILL.md` | E002/E021–E023/E061–E067: exists. Doctor on actual installed stack exit 2 with **13 mismatches among 14 components** (X002). Record says version 0.1.0 / Python 3.11.9 / STANDALONE_ONLY / NOT_INSTALLED; active Python is 3.11.17 (E001/E067). This is not a full Host-loaded deployment. |

`hermes` resolves to `P/hermes.EXE` (E008); `codex` resolves to null (E009). Hermes version, actual canonical project host bindings, clean Codex/Codex CLI lifecycle and restart receipts are UNMEASURED; PATH-null alone does not rule out an embedded/private Codex distribution. No Host matrix cell is silently waived.

### Existing local ZIPs are not formal TS11 distribution

E068 measured these historical fixtures under `I/_stack_selftest_plugins/`:

| File | Bytes | Actual SHA-256 |
|---|---:|---|

| `sbl-commander-sp-0.1.0.zip` | 2316 | `2c408822c54202fea8900459a96b5602a210aec6d87feb31af1467255af93a25` |
| `sbl-external-challenge-sp-0.1.0.zip` | 2400 | `cb917f83c7addce632b3d6568260d769d4627f0a58842f3113cdab99e6564891` |
| `sbl-tpm-sp-0.1.0.zip` | 2273 | `c1987c3eefa92b33b8294679718e646d4641f2828d0b7717058df536743bcbf0` |

They are measured historical 0.1.0 files, not current-version release assets, clean-double-build receipts, scanner passes, or ChatGPT identities. Other discovered ZIP/manifest paths are in E080/E082; fixture presence is not qualification. No draft-based packager was executed.

## B. Eight lifecycle verbs — current state by tool

Legend: **EXISTS** = source/entrypoint found (not necessarily qualified); **MISSING / BUILD** = absent from measured public surface and needs implementation; **UNMEASURED** = effect not tested. These are tool-specific surfaces, not claims that every possible external wrapper was exhaustively searched.

| Tool | installer | doctor | load | invoke | deny | upgrade | uninstall | rollback |
|---|---|---|---|---|---|---|---|---|
| TPM-SP | MISSING standalone installer; package-files builder only (E031) | MISSING deployed-bundle doctor; offline validate_skill/inspect_package exist (E031) | EXISTS readable SKILL (E039, skill_view); effective Host load UNMEASURED | MISSING dedicated command (E004); manifest read is not invoke | EXISTS `assert_permission` (E037), product.write denial measured below; Host denial UNMEASURED | MISSING version migration/transaction API (E031) | MISSING owned-file Host uninstaller (E031) | MISSING prior-version restore/receipt (E031) |
| Commander-SP | MISSING standalone installer (E031) | MISSING deployed-bundle doctor (E031) | EXISTS readable SKILL (E045); effective Host load UNMEASURED | MISSING dedicated command (E005); SP→WO join UNMEASURED | EXISTS library gate; challenge.sign denial measured; native boundary UNMEASURED | MISSING (E031) | MISSING (E031) | MISSING (E031) |
| Challenge-SP | MISSING standalone installer (E031) | MISSING deployed-bundle doctor (E031) | EXISTS readable SKILL (E051); effective Host load UNMEASURED | MISSING dedicated command (E006); independent frozen-subject run UNMEASURED | EXISTS library gate; product.write denial measured; Host readonly enforcement UNMEASURED | MISSING (E031); preserve local reference additions | MISSING (E031) | MISSING (E031) |
| HGK+Harness | EXISTS `sbl-harness install --target ... --hgk-root ...` (E095/E024); Native upgrade requires separate Owner WO | EXISTS; two adapter roots PASS, flat skill FAIL (E096/E097/X003) | Skill readable (E057); no `load` command (E095); Native Host effective binding UNMEASURED | ABI advertises plan/execute/verify but CLI only probe/install/doctor/uninstall (E095); true native invoke UNMEASURED / adapter bridge BUILD | EXISTS root/version and uninstall foreign-file/link guards in source (E024); current live deny/revoke/expiry UNMEASURED | MISSING command (E095); build native-owner approved delta + adapter transaction separately | EXISTS `uninstall --target` (E095); NOT run on installations | MISSING command/checkpoint orchestration (E095); native rollback UNMEASURED |
| Full Stack | EXISTS `sbl-stack install --root` (E093/E021); writes manifest, not a copied runtime | EXISTS; FAIL 13/14 (X002) | Skill readable (E062); no load command; effective Host load BUILD/UNMEASURED | EXISTS standalone `selftest --workdir` (E093/E021); not executed because it calls draft-based build_all; real user/Host invocation BUILD | EXISTS standalone unlocated-clause/prohibited-kind selftest logic (E021); not run; full Host deny BUILD | MISSING command (E093) | EXISTS `uninstall --root` (E093/E021); NOT run | MISSING command (E093); reinstall is not verified rollback |

Measured library negatives (one Python process, exit 0 because expected exceptions were caught):

```python
from sbl_sp.sp import assert_permission
from sbl_core.errors import SBLError
for sp,action in [('tpm_sp','product.write'),('commander_sp','challenge.sign'),('external_challenge_sp','product.write')]:
    try: assert_permission(sp,action)
    except SBLError as e: print(e.as_dict())
```

Output for each: `ok=false`, `code=SBL_E_PERMISSION_DENIED`, message `specialised principal is not permitted to perform this action`, detail naming the exact SP/action. Full actual outputs: `ts10_12_denials_cr.json` records 1–3. This proves only the in-process policy gate, NOT Host tool isolation, valid signing authority or native Permit enforcement.

### Proposed bounded implementation and acceptance contract (not implemented)

Create one **non-authoritative lifecycle adapter interface** per tool with all eight verbs. It may call existing install/doctor functions, but may not mint ECP/Permit/WorkOrder or create a parallel control plane. Native admission remains HGK; supplychain signing remains DOC-07 C44. A common lifecycle runner is implementation code, not a new issuer. Before implementation obtain a scoped WorkOrder and exact writeset; this assignment grants output-only design writes.

For every applicable canonical Hermes / Codex host / Codex CLI cell, freeze tool ID+version+package digest+Host version+ABI+runtime path+principal; then collect:

1. **installer**: install from a clean extracted artifact into an owned empty version directory, validate hashes/schema/permissions, atomically activate; reject foreign files, junction/reparse escape, traversal, stale/unsigned lock and wrong Host ABI. Raw before/after file lists + exit.
2. **doctor**: verify full content allowlist (not just the 14 modules), loaded runtime origin, interpreter executable digest, exact dependency hashes, Host loader hash, native ABI/registry epoch; fail on any missing/extra/changed runtime file. Mutable DB state is not a constant runtime digest: bind its ID/schema/issuer/epoch separately. No auto-rebaseline.
3. **load**: use that Host's admitted loader, record host-issued invocation/binding identity, loaded SKILL/runtime digest and actual resolver path; restart and re-read effective load. Skill discovery or skill_view text alone cannot PASS this step.
4. **invoke**: TPM source-bound proposal; Commander frozen TaskSpec→native WO handoff; Challenge different principal→frozen candidate→raw checker run; Harness native plan/execute/verify under issuer; Stack same-subject five-tool E2E. Require input/output digest, invocation ID, native receipt where applicable; generic model usage is insufficient.
5. **deny**: cross-permission attempt, missing/expired/revoked native authority, wrong subject/SHA, non-trigger, forged checker, replay and path escape; prove no forbidden writes via scoped before/after readback, not just a refusal string.
6. **upgrade**: freeze prior package/config/active-pointer checkpoint; stage new immutable runtime; run full doctor and POS/NEG; activate atomically only if lawful; reject unknown schema migration or changed authority; deliberately interrupt before/after activation and confirm recovery.
7. **uninstall**: unload host binding first, remove only signed/owned allowlisted files; preserve foreign files and independent evidence; restart and prove no discovery/trigger and no owned residue. Removing a skill is not permission to remove a Python distribution shared by other tools.
8. **rollback**: restore approved previous content/config/pointer checkpoint; doctor old bytes and Host restart/readback must match old lock; no recomputation of old expected digests from the changed live tree. Native partial/world effects need native compensating receipt, not merely filesystem rollback.

No guessed `hermes load`/`codex plugin install` commands are specified: their exact supported Host entrypoints/version remain UNMEASURED and must be discovered by the Host Owner before running this matrix. Gate is per-tool, per-applicable-host, per-verb; record exclusions only with Owner authority.

### D-17 README/layout repair cone

E043/E049/E055 show the same measured failure: README says `skills/<name>/SKILL.md`, exists=false, flat `SKILL.md` exists=true. The installed builder intentionally generates archive layout `skills/<name>/SKILL.md` (E031), while the deployed Hermes tree is flat. **Inference:** a package README was carried into a flattened Host deployment without rewriting its path; the historical copying command was not recovered (UNMEASURED).

Proposed repair: preserve archive layout and its archive README; generate a separate Hermes-install README that points to `./SKILL.md`, or use an Owner-approved loader layout which really retains the nested path. Verify every literal README entrypath exists in its own delivery surface, frontmatter name equals the installed directory name, and restart/load/invoke/deny still work. Include Challenge too; do not erase its added references. Not repaired here.

### D-18 measured 13/14 mismatch and zero-drift closure plan

X002 reproduces the failure, exit 2, components=14, thirteen `digest changed since install` problems. X001 independently hashes the exact recorded modules and confirms installed_mismatches=13. It also compares the current separate SBL source checkout: source_mismatches=3 (one changed file and two absent plugin-module files), not the same denominator as the installed runtime.

**Measured explanation, not a guessed history:** stack.json records 0.1.0/Python 3.11.9; active distribution is 0.1.1rc1/Python 3.11.17 (E067/E015/E001). The stack installer stores a digest manifest over imports in the current interpreter; it does not copy these modules into its target. Doctor resolves modules again from its own interpreter (E021). Therefore this old manifest and the currently selected imported runtime disagree. Which historical upgrade/copy caused that disagreement is UNMEASURED; it is unsafe to label all differences approved.

Proposed closure:

- Keep the failed old manifest and measured per-module before digests as evidence. Obtain Build/Host Owner decision on the intended baseline; do not edit stack.json to match arbitrary current bytes.
- Build a complete approved source snapshot, not the incomplete 0.1.0 checkout pretending to be the 0.1.1rc1 runtime. Freeze exact package version, runtime/schema/permission source bytes and dependency lock; do not accept broad `setuptools>=68` as a toolchain lock (E090).
- Install that artifact into a new isolated immutable runtime, not an editable source tree/shared evolving Hermes venv; generated launcher must select that exact interpreter/site-packages. Inventory package/skill/schema/reference/config and entrypoints too. Pin native source/dispatcher/registry ABI by exact approved content/epoch; `HGK version=0.1.0` alone is insufficient (E024/E096).
- Compare artifact lock → installed file digest → import `__file__` origin digest → host-loaded digest. Expected count must come from a signed/frozen complete allowlist. Require missing=extra=changed=0, runtime pins drift=0; single-byte tamper and shadowed-import tests must still fail.
- Run doctor, install/load/invoke/deny/restart/uninstall-residue/upgrade/rollback with independent checker receipts. Only then close D-18 for that candidate. Existing native-root adapter PASS cannot close Stack drift or Native upgrade acceptance.

## C. TS11 deterministic ZIP build — exact candidate workflow

**Existing builder is not a lawful current release path.** E031/E034/E035 show it emits/validates `https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`; E031 hardcodes version 0.1.1rc1 and uses fixed ZIP dates/sorted entries. That is measured implementation, NOT authority to activate the prohibited Draft. It was inspected, not run. Stack selftest includes that builder, so it was intentionally not run (E021). A distributable neutral Agent Skill ZIP must be distinguished from a ChatGPT plugin, and its final schema/layout must be approved by the packaging Owner.

A candidate, stdlib-only **neutral archive harness** is supplied at `ts10_12_double_build.py`. It never imports sbl_sp/plugins and never calls a Host. It consumes preapproved files verbatim, fixed manifest/schema/permissions hashes and exact version from an Owner-frozen staging lock. Its private lock schema `SBL-REPRO-LOCK/1` is solely an internal build-input format, not a claimed official Host/plugin schema. Nonempty receipt refs are **not** cryptographic approval validation; the trusted Native/C44 verifier must authenticate those refs before this mechanical harness is invoked. Final production lock/staging are deliberately absent, not fake-filled.

### Required lock input (proposed, not fabricated)

`raw/ts10_12_approved_build.lock.json` must contain:

- `lock_schema="SBL-REPRO-LOCK/1"`, `python_version="3.11.17"`, exact `builder_sha256`, authenticated `approval_receipt_ref`, `schema_authority_ref`, absolute `staging_root` contained under this output directory.
- Exactly three `packages[]`, IDs `tpm-sp`, `commander-sp`, `external-challenge-sp`; fixed Owner-chosen `version`, `schema_digest`, `permissions_digest`; explicit `files[]` with `source_path` relative to staging root, safe `archive_path`, actual `sha256`. The freeze must bind schema/permissions digests to the correct included files using the approved validator; the mechanical ZIP harness does not replace semantic/schema qualification.
- Allowed contents: exact approved SKILL entry + all declared references/resources, approved neutral manifest/schema (NOT the Draft plugin.json), README matching actual layout, LICENSE, NOTICE. No private DOC corpus, credentials, signing keys, absolute local runtime paths, arbitrary source-tree sweep or test output. The specific final archive layout is `UNMEASURED / OWNER_SCHEMA_PENDING`, not invented here.
- Runtime/permission separation: TPM grants goal.read/spec.write/evidence.read, forbids product.write/challenge.sign (E030); Commander grants product.write/build.route/evidence.read, forbids challenge.sign/verdict.sign (E028); Challenge readonly with evidence.read/challenge.sign, forbids product.write/goal.write (E029). These are current declarations to reconcile with the frozen spec, not permission to write outside a native WO or sign without an independent credential.

### Commands to run after lock/schema/Native admission exists

Run in bash, from `C:/Users/user`. These commands are exact and use the supplied harness, but **have not built the three production SP packages**, because approved lock/staging/scanner authority is missing. Existing build roots must be absent; the harness refuses reuse and never deletes anything. For a rerun use a newly authorized fresh output root containing the pinned harness, not recursive cleanup of an old evidence root.

```bash
P='C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent/venv/Scripts/python.exe'
R='C:/Projects/Agent_Workspace/_r14_packet/raw'
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 TZ=UTC LC_ALL=C SOURCE_DATE_EPOCH=315532800
"$P" -B -I "$R/ts10_12_double_build.py" --lock "$R/ts10_12_approved_build.lock.json" --build-id A
"$P" -B -I "$R/ts10_12_double_build.py" --lock "$R/ts10_12_approved_build.lock.json" --build-id B
"$P" -B -I "$R/ts10_12_double_build.py" --lock "$R/ts10_12_approved_build.lock.json" --compare
```

Run each only if previous exit=0; A/B are separate Python processes, independently reload/hash frozen files, use separate newly-created output directories and no build cache. Both use the same approved immutable input freeze; trusted runner must prevent staging/lock changes during the pair and verify its digest before/after. No signing/publishing/network occurs inside the deterministic build. The compare report is not an independent checker signature.

### Every nondeterminism surface to pin or eliminate

| Source | Required control in this design |
|---|---|
| Source version and dirty inputs | Owner-frozen version string, exact source allowlist and per-file SHA, lock digest, no dynamic version from current date/branch/working tree; three package IDs fixed, no accidental local Challenge-reference omission |
| Schema and permissions | Approved schema bytes and authority receipt fixed; canonical manifest bytes and policy digest fixed; no runtime discovery of capabilities or use of the quarantined schema |
| Python/build code | Exact 3.11.17 interpreter **binary SHA**, archive-harness SHA and standard-library/toolchain distribution digest in BuildManifest.lock; version string check alone is not a full binary pin |
| Dependencies/build backend | No pip resolution/network in archive builder; any runtime wheel/toolchain supplied from immutable hash-locked offline inputs; build backend exact version/hash, not setuptools>=68 |
| File enumeration | Explicit allowlist, byte-sorted ASCII archive paths, no glob traversal order; reject duplicate/casefold collisions, traversal, absolute paths, links/reparse escape; no directory entries |
| mtimes / atime / ctime | Archive uses no filesystem timestamps: every ZipInfo is explicitly 1980-01-01 00:00:00 (epoch 315532800). Input bytes verified; if a staging generator/scanner embeds mtime, normalize it to the same epoch before freeze or exclude its output from archive |
| ZIP timestamps/timezones | Explicit DOS date tuple, TZ=UTC as defense in depth; no localtime conversion or current wall clock |
| ZIP OS flags/modes | create_system=3; create/extract_version=20; fixed regular-file 0644 external attrs, internal attrs=0; empty extra/comment; empty archive comment; ASCII names avoid encoding-flag variation; allowZip64=False |
| Compression/tool version | ZIP_STORED: no DEFLATE/zlib/platform-dependent compressor variance. Larger ZIP is intentional. If compression adopted later, exact implementation/version/level becomes a new lock input and clean pair must be rerun |
| Text/JSON | Staged file bytes are hashed verbatim. Any upstream generation pins UTF-8/no BOM/LF, JSON sort_keys and separators, list ordering and final-newline policy before freeze; build does not silently normalize signed input |
| Absolute paths/user identity/locale | No local-root/user/hostname strings in payload; generator must use stable relative paths and canonical Unicode policy, no locale sorting; `-I` isolates ambient import paths, no sbl source import |
| Random UUIDs/nonces/current timestamps | None generated inside archive; any semantic ID fixed by approved input, runtime nonces and build receipts remain outside |
| SBOM/license/scanner metadata | Producer/version/config/rules/database digest and inventory input fixed; SBOM generated timestamp/serial sorted or frozen under C44 reproducibility policy. Prefer final-archive SBOM/license/scan/provenance as digest-bound sidecars, so subject_sha does not create a self-referential archive cycle |
| Signatures/attestations/publishing metadata | Keep out of the reproducible ZIP; sign final digest externally by authorized C44/publisher. Variable signing times/certificates do not alter ZIP bytes |
| Concurrency/cache | Distinct clean roots and processes; input freeze immutable for both; fail on existing outputs; no cache/network; compare actual SHA and bytes with independent clean-room verification |

Thus **algorithmic ZIP determinism is exercised**, while **three-SP clean reproducibility remains UNMEASURED** until approved real input bytes and full trusted toolchain lock exist. The actual harmless fixture command was:

```bash
python -B -I C:/Projects/Agent_Workspace/_r14_packet/raw/ts10_12_double_build.py --selftest
```

Exit 0 output: `{"algorithm_only": true, "equal": true, "sha256": "b7d39f27697060b1a99a96d22016274a58062fe259e513f19f4dcc82098cc2d8", "host_qualified": false}`. It used two benign text files with reversed insertion order. These are **not** SP ZIPs and that digest must never be used as a product digest. Subsequent final-harness `--help` exits 0, and the real build command with missing approved lock exits 1 / FileNotFoundError; raw outputs in `ts10_12_harness_checks.json`. No invented release SHA is supplied.

### Remaining formal TS11 exits

After building: independently reopen both archives, ensure identical exact allowlist, detect duplicate paths/zip-slip/links/zip bombs, clean-extract to two authorized fresh roots, verify every file against lock, parse SKILL frontmatter and README target existence, validate approved schema/permissions and perform isolated Host loading separately. Require all three packages' SBOM/license/secret receipts bound to **final archive digest**. Then authorized Publisher uploads only approved assets; independent downloader fetches each authorized asset URI and checks its byte count/SHA against local output, signature and immutable asset identity. No upload, URL, remote SHA, download or Host ID was measured here. ZIP PACKAGED is separate from HOST_EFFECTIVE and TS12.

## D. Host supplychain tooling — measured missing, not silently assumed

| Tool requested | Command actually evaluated | Output | Status |
|---|---|---|---|
| syft | `shutil.which('syft')`; `importlib.metadata.distribution('syft')` | null; PackageNotFoundError | MISSING from PATH/active Python (E010/E018); other disks UNMEASURED |
| pip-licenses | same two probes for pip-licenses | null; PackageNotFoundError | MISSING (E011/E016) |
| detect-secrets | same two probes for detect-secrets | null; PackageNotFoundError | MISSING (E012/E017) |
| trivy | same two probes for trivy | null; PackageNotFoundError | MISSING (E013/E019) |
| grype | same two probes for grype | null; PackageNotFoundError | MISSING (E014/E020) |

No `--version` output was invented for absent programs. A missing CLI path yields no invocation. Python metadata absence for a non-Python tool is supplemental only; PATH is the primary binary availability measurement. `C:/Projects/Agent_Workspace/SBL/tools/secret_scan.py` **does exist**, SHA/content in E091, but its execution/coverage and sentinel tests are UNMEASURED. It is not represented as detect-secrets, an SBOM generator, license audit or a C44 trusted attestation. Its Git-aware/repository behavior was not executed under this task's no-Git restriction.

**Blocked gate:** `SECRET_SCAN_REQUIRED / C44_RECEIPT_MISSING / PROVENANCE_MISSING`, not PASS. Under DOC-12 lines 1307/1466/1742/6965–6975 (X005), DOC-07 C44 owns actual SBOM/provenance/scanner Writer. Request that Owner's same-subject trusted receipts, or obtain scoped authority to provision exact pinned scanner binaries into an isolated tool root and qualify them; do not install all missing tools globally or silently create a substitute issuer. Need at least appropriate SBOM producer + license/NOTICE accounting + secret scan, with vulnerability scanning where required by applicability. `pip-licenses` alone inventories an environment, not necessarily the three delivered packages or all bundled text licenses.

Proposed scan pipeline after tooling admission: discover exact executable path→record version/binary/config/rules digest→run against clean extracted approved payloads and final archive inventory→positive planted-secret/license/SBOM-subject-mismatch sentinel tests in isolated fixtures→require no unexpected findings and recorded exceptions→C44 authenticate subject/digest/signature→independent verifier readback. Do not print secret matches into public evidence; emit redacted locators and bounded private evidence refs. Commands for absent third-party CLIs are deliberately not represented as executed; choose/document their supported pinned invocation only after the Owner supplies those exact versions. This design does not plan around missing scanners by pretending a local inventory JSON is an SBOM.

## E. TS12 authority and exact HOST_PENDING contract

No ChatGPT login, account/workspace capability, official current Host packaging API/schema, upload/create/install endpoint or permission was probed in this task: **UNMEASURED**. This is not an assertion that any particular current OpenAI feature exists or does not exist. The authority analysis is based on the measured local R13 CR and R14 order, not web speculation. Three local skills/ZIP files are not three Host-issued IDs.

A superseding **CR-PLUGIN-SCHEMA-AUTHORITY** would have to grant ALL of the following, with exact issuer/approver, timestamp, scope and validity/revocation:

1. **Product/source authority:** competent DOC-06/DOC-12 source Owner names the exact official **non-draft** Host interface and frozen schema/version/hash; resolves applicability to C-016, C-017, C-018 and the original NOBJ-017 deny. A mention of a newer method or broad preauthorization is not a grant. If the proposal still requires the prohibited Draft, STOP; this task grants no power to remove that ban.
2. **Host/account authority:** actual ChatGPT workspace/account Owner/admin authorizes private creation, installation, use, testing, uninstall and any required network/storage/tool scopes for each of the three principals; names target tenant/workspace and privacy restrictions, eligible account feature/ABI, credential broker and allowed side effects. An official interface must actually be available for that account; CR text cannot manufacture capability.
3. **Package/supplychain authority:** fixed three versions, approved package/schema/permission digests and licenses, allowed distribution destination, C44 scan/provenance receipts, no private DOCs/keys in payload. Design-neutral ZIP authority does not automatically grant Host installation or public publication.
4. **Native execution authority:** separate HGK Owner-issued scoped WO/Binding/Lease/Permit-equivalent for any product/world effect; Commander cannot issue its own permit. Challenge read-only candidate scope and distinct principal/credential. Account-install authority is not a native write/signing authority.
5. **Qualification and rollback authority:** exact test workspace/write/output roots, authorized test tools and safe negatives, Host-issued three distinct IDs, receipts for create→install→true @invoke→non-trigger→forbidden/deny→uninstall→post-uninstall no-trigger and residue readback; restart/effective-load, upgrade/rollback where applicable. Separate independent verifier and Owner acceptance; revocation/expiry and recovery instructions. If selected interface cannot deliver those literal obligations, open a product CR rather than declare a substitute interface equivalent.

Until then publish these exact per-surface records (not fake IDs):

| Surface | Principal | status | host_issued_id | create/install/@invoke/non-trigger/deny/uninstall | required unblock trigger |
|---|---|---|---|---|---|
| C-016 | TPM-SP | HOST_PENDING | null — not issued/proven | NOT_RUN / UNMEASURED | superseding non-draft schema CR + Host Owner grant + true Host receipts |
| C-017 | Commander-SP | HOST_PENDING | null — not issued/proven | NOT_RUN / UNMEASURED | same, plus native bounded write authority for effect test |
| C-018 | Challenge-SP | HOST_PENDING | null — not issued/proven | NOT_RUN / UNMEASURED | same, plus distinct readonly checker identity/credential |

**Precise required public language:**

> C-016 (TPM-SP), C-017 (Commander-SP), and C-018 (External Challenge-SP) remain HOST_PENDING. No ChatGPT private-plugin installation or Host-issued ID has been established by this evidence packet; create/install/@invoke/non-trigger/deny/uninstall qualifications were not run. Local Hermes skill readability and portable ZIP presence prove neither ChatGPT installation nor native authority. The Agent Plugins 1.0 Working Draft is not an admitted shipping or activation surface. Resume only after a superseding written Owner CR selects an official non-draft interface, the target Host/account Owner grants the scoped actions, and an independent checker reads back three distinct Host-issued identities with same-candidate lifecycle receipts. Until then TS12 is HOLD; no HOST_EFFECTIVE, 3/3 installed, FULL_PRODUCT_PASS or world-effect claim is permitted.

Qualified ChatGPT IDs proven by this packet: **0/3**. This is an evidence denominator, not a claim to have exhaustively audited every private account. ZIP-only work may proceed under its own lawful admission; M4 stays OPEN per R14 order.

## Appendix A — measured command/output index

Full output including source text/digests is in the accompanying JSON. These excerpts are literal command outputs or programmatic selections from them, not invented test transcripts.

### E001
Command/expression: `sys.version; sys.executable; os.getcwd()`; exit `0`.
```json
{
  "version": "3.11.17 (main, Oct  3 2026, 01:03:09) [MSC v.1944 64 bit (AMD64)]",
  "executable": "C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\hermes-agent\\venv\\Scripts\\python.exe",
  "cwd": "C:\\Users\\user"
}
```

### E002
Command/expression: `shutil.which('sbl-stack')`; exit `0`.
```json
"C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\hermes-agent\\venv\\Scripts\\sbl-stack.EXE"
```

### E003
Command/expression: `shutil.which('sbl-harness')`; exit `0`.
```json
"C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\hermes-agent\\venv\\Scripts\\sbl-harness.EXE"
```

### E004
Command/expression: `shutil.which('tpm-sp')`; exit `0`.
```json
null
```

### E005
Command/expression: `shutil.which('commander-sp')`; exit `0`.
```json
null
```

### E006
Command/expression: `shutil.which('external-challenge-sp')`; exit `0`.
```json
null
```

### E007
Command/expression: `shutil.which('hgk-governed-runtime')`; exit `0`.
```json
null
```

### E008
Command/expression: `shutil.which('hermes')`; exit `0`.
```json
"C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\hermes-agent\\venv\\Scripts\\hermes.EXE"
```

### E009
Command/expression: `shutil.which('codex')`; exit `0`.
```json
null
```

### E010
Command/expression: `shutil.which('syft')`; exit `0`.
```json
null
```

### E011
Command/expression: `shutil.which('pip-licenses')`; exit `0`.
```json
null
```

### E012
Command/expression: `shutil.which('detect-secrets')`; exit `0`.
```json
null
```

### E013
Command/expression: `shutil.which('trivy')`; exit `0`.
```json
null
```

### E014
Command/expression: `shutil.which('grype')`; exit `0`.
```json
null
```

### E015
Command/expression: `importlib.metadata.distribution('sbl-v01')`; exit `0`.
```json
{
  "version": "0.1.1rc1",
  "root": "C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\hermes-agent\\venv\\Lib\\site-packages",
  "entrypoints": "[console_scripts]\nsbl-harness = sbl_harness.cli:main\nsbl-stack = sbl_stack.cli:main\nsbl-todo = sbl_cli.sbl_todo:main\n"
}
```

### E016
Command/expression: `importlib.metadata.distribution('pip-licenses')`; exit `1`.
```json
"PackageNotFoundError"
```

### E017
Command/expression: `importlib.metadata.distribution('detect-secrets')`; exit `1`.
```json
"PackageNotFoundError"
```

### E018
Command/expression: `importlib.metadata.distribution('syft')`; exit `1`.
```json
"PackageNotFoundError"
```

### E019
Command/expression: `importlib.metadata.distribution('trivy')`; exit `1`.
```json
"PackageNotFoundError"
```

### E020
Command/expression: `importlib.metadata.distribution('grype')`; exit `1`.
```json
"PackageNotFoundError"
```

### E043
Command/expression: `README relative skill paths under C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\skills\sbl\tpm-sp`; exit `0`.
```json
[
  {
    "declared": "skills/tpm-sp/SKILL.md",
    "exists": false,
    "flat_entry_exists": true
  }
]
```

### E049
Command/expression: `README relative skill paths under C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\skills\sbl\commander-sp`; exit `0`.
```json
[
  {
    "declared": "skills/commander-sp/SKILL.md",
    "exists": false,
    "flat_entry_exists": true
  }
]
```

### E055
Command/expression: `README relative skill paths under C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\skills\sbl\external-challenge-sp`; exit `0`.
```json
[
  {
    "declared": "skills/external-challenge-sp/SKILL.md",
    "exists": false,
    "flat_entry_exists": true
  }
]
```

### E061
Command/expression: `sorted(Path('C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\skills\\sbl\\sbl-stack').rglob("*"))`; exit `0`.
```json
[
  "SKILL.md"
]
```

### E067
Command/expression: `Path('C:\\Projects\\Agent_Workspace\\SBL-install\\stack\\stack.json').read_bytes(); sha256(bytes)`; exit `0`.
```json
{
  "path": "C:\\Projects\\Agent_Workspace\\SBL-install\\stack\\stack.json",
  "exists": true,
  "bytes": 2867,
  "sha256": "30b0ffce048e9de5719576bf2f48a1dc1bc1826709e455344bc78e3e4f06e230"
}
```

### E090
Command/expression: `Path('C:\\Projects\\Agent_Workspace\\SBL\\pyproject.toml').read_bytes(); sha256(bytes)`; exit `0`.
```json
{
  "path": "C:\\Projects\\Agent_Workspace\\SBL\\pyproject.toml",
  "exists": true,
  "bytes": 492,
  "sha256": "479ddc64e4d2f23d8ca8b4fe8784c19ae114c5ac0cff1b2e95b062895f3efd09"
}
```

### E092
Command/expression: `Path('C:\\Projects\\Agent_Workspace\\SBL\\_governance\\round-20261021-r13-native\\CR-PLUGIN-SCHEMA-AUTHORITY.md').is_file()`; exit `0`.
```json
{
  "path": "C:\\Projects\\Agent_Workspace\\SBL\\_governance\\round-20261021-r13-native\\CR-PLUGIN-SCHEMA-AUTHORITY.md",
  "exists": false
}
```

### E093
Command/expression: `C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\hermes-agent\venv\Scripts\sbl-stack.EXE --help`; exit `0`.
```json
{
  "stdout": "usage: sbl-stack [-h] {install,doctor,status,uninstall,selftest,describe} ...\n\ninstallable SBL stack\n\npositional arguments:\n  {install,doctor,status,uninstall,selftest,describe}\n    install             install the stack into a directory\n    doctor              verify an installed stack\n    status              describe an installed stack\n    uninstall           remove an installed stack\n    selftest            run the ordinary journey and two refusals\n    describe            print the stack surface\n\noptions:\n  -h, --help            show this help message and exit\n",
  "stderr": ""
}
```

### E095
Command/expression: `C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\hermes-agent\venv\Scripts\sbl-harness.EXE --help`; exit `0`.
```json
{
  "stdout": "usage: sbl-harness [-h] {probe,install,doctor,uninstall} ...\n\nHGK harness adapter\n\npositional arguments:\n  {probe,install,doctor,uninstall}\n    probe               read-only probe of an HGK root\n    install             install the adapter into a directory\n    doctor              verify an installed adapter\n    uninstall           remove an installed adapter\n\noptions:\n  -h, --help            show this help message and exit\n",
  "stderr": ""
}
```

### E096
Command/expression: `C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\hermes-agent\venv\Scripts\sbl-harness.EXE doctor --target C:\Projects\Agent_Workspace\HG-KSEOS\_sbl_harness_adapter`; exit `0`.
```json
{
  "stdout": "{\n  \"ok\": true,\n  \"problems\": [],\n  \"target\": \"C:\\\\Projects\\\\Agent_Workspace\\\\HG-KSEOS\\\\_sbl_harness_adapter\",\n  \"probe\": {\n    \"status\": \"ROOT_READY\",\n    \"root\": \"C:\\\\Projects\\\\Agent_Workspace\\\\HG-KSEOS\",\n    \"pin\": {\n      \"package\": \"hg_kseos\",\n      \"version\": \"0.1.0\",\n      \"version_range\": \">=0.1.0,<0.2.0\",\n      \"root_env\": \"HGK_ROOT\",\n      \"default_root\": \"C:/Projects/Agent_Workspace/HG-KSEOS\",\n      \"source_subdir\": \"src/hg_kseos\",\n      \"spine_relpath\": \"var/shared-spine/hg-kseos.db\",\n      \"lane_registry_relpath\": \"config/lane-route-slots.candidate.json\",\n      \"dispatcher_relpath\": \"scripts/hgk-lane-dispatch.py\"\n    },\n    \"observed_version\": \"0.1.0\",\n    \"abi\": {\n      \"name\": \"hgk-harness-abi/1\",\n      \"provides\": [\n        \"plan\",\n        \"execute\",\n        \"verify\"\n      ],\n      \"requires_native\": [\n        \"WorkOrder\",\n        \"ExecutionBinding\",\n        \"Permit\"\n      ],\n      \"not_provided\": [\n        \"native_effect\",\n        \"permit_signing\",\n        \"workorder_admission\"\n      ]\n    },\n    \"checks\": [\n      {\n        \"check\": \"root_exists\",\n        \"ok\": true,\n        \"detail\": \"HGK root directory\",\n        \"path\": \"C:\\\\Projects\\\\Agent_Workspace\\\\HG-KSEOS\"\n      },\n      {\n        \"check\": \"package_present\",\n        \"ok\": true,\n        \"detail\": \"hg_kseos package directory\",\n        \"path\": \"C:\\\\Projects\\\\Agent_Workspace\\\\HG-KSEOS\\\\src\\\\hg_kseos\"\n      },\n      {\n        \"check\": \"spine_present\",\n        \"ok\": true,\n        \"detail\": \"shared spine database\",\n        \"path\": \"C:\\\\Projects\\\\Agent_Workspace\\\\HG-KSEOS\\\\var\\\\shared-spine\\\\hg-kseos.db\"\n      },\n      {\n        \"check\": \"lane_registry_present\",\n        \"ok\": true,\n        \"detail\": \"lane route slots\",\n        \"path\": \"C:\\\\Projects\\\\Agent_Workspace\\\\HG-KSEOS\\\\config\\\\lane-route-slots.candidate.json\"\n      },\n      {\n        \"check\": \"dispatcher_present\",\n        \"ok\": true,\n        \"detail\": \"lane dispatcher entry point\",\n        \"path\": \"C:\\\\Projects\\\\Agent_Workspace\\\\HG-KSEOS\\\\scripts\\\\hgk-lane-dispatch.py\"\n      },\n      {\n        \"check\": \"import\",\n        \"ok\": true,\n        \"detail\": \"imported hg_kseos from the root\",\n        \"path\": \"C:\\\\Projects\\\\Agent_Workspace\\\\HG-KSEOS\\\\src\\\\hg_kseos\\\\__init__.py\"\n      }\n    ],\n    \"claim_ceiling\": \"HOST_PENDING\",\n    \"native_effect\": \"NOT_GRANTED\"\n  },\n  \"abi\": \"hgk-harness-abi/1\",\n  \"claim_ceiling\": \"HOST_PENDING\",\n  \"native_effect\": \"NOT_GRANTED\"\n}\n",
  "stderr": ""
}
```

### E097
Command/expression: `C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\hermes-agent\venv\Scripts\sbl-harness.EXE doctor --target C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\skills\sbl\hgk-governed-runtime`; exit `2`.
```json
{
  "stdout": "{\n  \"ok\": false,\n  \"problems\": [\n    \"MANIFEST.json is missing\"\n  ],\n  \"target\": \"C:\\\\Users\\\\user\\\\AppData\\\\Local\\\\Packages\\\\OpenAI.Codex_2p2nqsd0c76g0\\\\LocalCache\\\\Local\\\\hermes\\\\skills\\\\sbl\\\\hgk-governed-runtime\"\n}\n",
  "stderr": ""
}
```

### X002
Command: `C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\hermes-agent\venv\Scripts\sbl-stack.exe doctor --root C:\Projects\Agent_Workspace\SBL-install\stack`; exit `2`.
```json
{
  "ok": false,
  "problems": [
    "sbl_core.core: digest changed since install",
    "sbl_core.dto: digest changed since install",
    "sbl_core.errors: digest changed since install",
    "sbl_core.modes: digest changed since install",
    "sbl_core.gknow: digest changed since install",
    "sbl_core.m01_intake: digest changed since install",
    "sbl_core.m02_spec: digest changed since install",
    "sbl_core.m03_routing: digest changed since install",
    "sbl_core.m04_bridge: digest changed since install",
    "sbl_core.m05_verify: digest changed since install",
    "sbl_core.m06_repair: digest changed since install",
    "sbl_sp.sp: digest changed since install",
    "sbl_sp.plugins: digest changed since install"
  ],
  "target": "C:\\Projects\\Agent_Workspace\\SBL-install\\stack",
  "components": 14,
  "mode_gate_cells": 39,
  "claim_ceiling": "STANDALONE_ONLY",
  "host_install_state": "NOT_INSTALLED"
}

```

### X003
Command: `C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\hermes-agent\venv\Scripts\sbl-harness.exe doctor --target C:\Projects\Agent_Workspace\SBL-install\hgk-adapter`; exit `0`.
```json
{
  "ok": true,
  "problems": [],
  "target": "C:\\Projects\\Agent_Workspace\\SBL-install\\hgk-adapter",
  "probe": {
    "status": "ROOT_READY",
    "root": "C:\\Projects\\Agent_Workspace\\HG-KSEOS",
    "pin": {
      "package": "hg_kseos",
      "version": "0.1.0",
      "version_range": ">=0.1.0,<0.2.0",
      "root_env": "HGK_ROOT",
      "default_root": "C:/Projects/Agent_Workspace/HG-KSEOS",
      "source_subdir": "src/hg_kseos",
      "spine_relpath": "var/shared-spine/hg-kseos.db",
      "lane_registry_relpath": "config/lane-route-slots.candidate.json",
      "dispatcher_relpath": "scripts/hgk-lane-dispatch.py"
    },
    "observed_version": "0.1.0",
    "abi": {
      "name": "hgk-harness-abi/1",
      "provides": [
        "plan",
        "execute",
        "verify"
      ],
      "requires_native": [
        "WorkOrder",
        "ExecutionBinding",
        "Permit"
      ],
      "not_provided": [
        "native_effect",
        "permit_signing",
        "workorder_admission"
      ]
    },
    "checks": [
      {
        "check": "root_exists",
        "ok": true,
        "detail": "HGK root directory",
        "path": "C:\\Projects\\Agent_Workspace\\HG-KSEOS"
      },
      {
        "check": "package_present",
        "ok": true,
        "detail": "hg_kseos package directory",
        "path": "C:\\Projects\\Agent_Workspace\\HG-KSEOS\\src\\hg_kseos"
      },
      {
        "check": "spine_present",
        "ok": true,
        "detail": "shared spine database",
        "path": "C:\\Projects\\Agent_Workspace\\HG-KSEOS\\var\\shared-spine\\hg-kseos.db"
      },
      {
        "check": "lane_registry_present",
        "ok": true,
        "detail": "lane route slots",
        "path": "C:\\Projects\\Agent_Workspace\\HG-KSEOS\\config\\lane-route-slots.candidate.json"
      },
      {
        "check": "dispatcher_present",
        "ok": true,
        "detail": "lane dispatcher entry point",
        "path": "C:\\Projects\\Agent_Workspace\\HG-KSEOS\\scripts\\hgk-lane-dispatch.py"
      },
      {
        "check": "import",
        "ok": true,
        "detail": "imported hg_kseos from the root",
        "path": "C:\\Projects\\Agent_Workspace\\HG-KSEOS\\src\\hg_kseos\\__init__.py"
      }
    ],
    "claim_ceiling": "HOST_PENDING",
    "native_effect": "NOT_GRANTED"
  },
  "abi": "hgk-harness-abi/1",
  "claim_ceiling": "HOST_PENDING",
  "native_effect": "NOT_GRANTED"
}

```

### X001 exact component before/after digest comparison
Command: read installed stack manifest, resolve file paths in named site-packages/source roots, SHA-256 each file; exit 0. Full path details in X001.

| Module | Recorded SHA-256 | Active runtime SHA-256 | Match |
|---|---|---|---|
| sbl_core.core | `6b4c8a7d61359c9dc7c464d482233713f8a854557aecb06a70bc4b3c8cc364fa` | `5320c9328579ea890d464a82f7f077debbb81dfe8653c96668a7bd62dc1ce181` | False |
| sbl_core.dto | `2676c25c059abf1e4ff6d31de9d6e11325db20dadb99ea3188efa261102bada3` | `791b23a010e7f8ffaa843a66c63548f1bc5e4463c93e709570948e9488308a85` | False |
| sbl_core.errors | `7b48ea4f6266af88c144fdb68568379a86ea477f0077dd0cb7ab3bde35384e80` | `4e58742d97e64db347666efce65cd55068ab82c12bfd61900b09f3b16ce43fc9` | False |
| sbl_core.modes | `1791cb074ace2aca9da7ea6160ef66f4c01fc372a59c0d450fdfbf97dec0e275` | `b0d81ee6f2f15334dc1f47dfd7a46fbe4534cd4a89e43ff0ca57d6ac5d0631a9` | False |
| sbl_core.gknow | `55dcd60ce1605490cd890c12f5b0e2a81431453798c28f4485bcf4e4c8e5e651` | `b5bb8d153335aaec965f1f472c4d3b91cb90584ed3af5e7fa5dd4581dcfb2e45` | False |
| sbl_core.m01_intake | `901fc9cee105095066b12f6f4fe0082414a2653f63391d01fb4618126510d00e` | `4657a529b74fd6cc4c7bb82e87218e76990768a7b4b1c3339e890ed6081dfaec` | False |
| sbl_core.m02_spec | `4d2fa59b167b39812bd75b91df717261f0204463244667d2522dc0b59790848a` | `40334929817546d538c985335f2547a769c1882170625391d08ca110e987b98e` | False |
| sbl_core.m03_routing | `724bf1a610f633d51661452c92517053de3fd382942472782753b8361cc06f5a` | `fdb62afadaf00fd2b09a29998a8071ea0f3b20730a529ac2c1037d6a205f8673` | False |
| sbl_core.m04_bridge | `05600f94cf37bc83d376ac5a57e8ac9926968226306868180e3357a37c0eb47f` | `2681739185065dfce73f1c08f8decf1281808ca926f9aeea5bebd035018874ff` | False |
| sbl_core.m05_verify | `d28eda1d1d76d9febbbccdbeb092887dc54a91ebf532359c23db53aabe514e99` | `5adbf4903120739b991a5688ba51a2e7e985208081e7d8c332348e935588ee88` | False |
| sbl_core.m06_repair | `6d37daf89df264625b6bee96a8ab9b5fd618793a215061639133c28420cd303e` | `51b1f0c16c6b11b324940c980f677b9e3786a1a3e5eb3d7cfdc892d3241a3f84` | False |
| sbl_sp.sp | `28309b3b5ec1e0b605aafa7bfee19914642c8a070efcb84adb98ee96b7330884` | `8fa61b8346466d09a2c7f636f54dc2d40a782ac079ed5e1142d56d812731711f` | False |
| sbl_sp.plugins | `fa3456a69605392ccbd646cf2c18c75cf9a8b8cdcdcbbd32cb9454fc2118af46` | `0febb130f38f7c9abcf5d1243ae825b0636d649f78e2df3703a3fb8ccc95f188` | False |
| sbl_sp.plugins.portable | `df286703831281243d779106df40cfbe4681003e0afddc3a2b5b0a2ad0bd7e81` | `df286703831281243d779106df40cfbe4681003e0afddc3a2b5b0a2ad0bd7e81` | True |

### Source hashes and CR readback

- X004: command `Path('C:\\Projects\\Agent_Workspace\\知識庫\\實作相關DOC\\Fabric vNext\\Semantic World OS Fabric\\SBL\\SBL_PIPD-LS-PKG\\SBL_PIPD-LS-PKG_DOC-11.md').read_bytes(); sha256; regex '^#{1,5} .*C29|^#{1,5} .*C30|ONE ECP|Checker.*Maker|原生'` → SHA-256 `12f8705d780b76f264457c194a6ff359da8d74b5d6d8c83fa245b74d2a37508e` (exit 0). Exact source-line excerpts are saved in the same JSON record.
- X005: command `Path('C:\\Projects\\Agent_Workspace\\知識庫\\實作相關DOC\\Fabric vNext\\Semantic World OS Fabric\\SBL\\SBL_PIPD-LS-PKG\\SBL_PIPD-LS-PKG_DOC-12.md').read_bytes(); sha256; regex '^#{1,5} .*C36|^#{1,5} .*C43|^#{1,5} .*C49|C-016|C-017|C-018|HOST_PENDING|determin|SBOM|NOBJ-017'` → SHA-256 `d1e470d82ca14319582cb8947aa52007927aa38e726249b1430804cfe8c8ca56` (exit 0). Exact source-line excerpts are saved in the same JSON record.
- X006: command `Path('C:\\Projects\\Agent_Workspace\\知識庫\\實作相關DOC\\Fabric vNext\\Semantic World OS Fabric\\SBL\\SBL_PIPD-LS-PKG\\SBL_PIPD-LS-PKG_DOC-06.md').read_bytes(); sha256; regex 'NOBJ-017|Agent Plugins 1.0'` → SHA-256 `64ea4977dab3093301f82dc7469413cc754998fc53946467842e06d83645102b` (exit 0). Exact source-line excerpts are saved in the same JSON record.
- X007: command `Path('C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\attachments\\SBL_R14_POST_R13_HERMES_HGK_FABRIC_FULL_PRODUCT_COMMAND_PROMPT_2026-10-22.md').read_bytes(); sha256; select TS10..12/CHK10..12 and authority lines` → SHA-256 `6fa44f5570032acd767942a922ff256995bdc287531084f3183cc54e410e12ce` (exit 0). Exact source-line excerpts are saved in the same JSON record.
- R13 recovered CR: `Path('C:/Projects/Agent_Workspace/_r13_far/CR-PLUGIN-SCHEMA-AUTHORITY.md').read_bytes()` → SHA-256 `bf8117c00ff06f9ea0be9f84d6fc00881994b2abedbd19dd935e492b0452806b` (exit 0); clauses say HOST_PENDING, not approval of Draft.

### Harness checks actually executed
```json
[
  {
    "command": "python -B -I C:\\Projects\\Agent_Workspace\\_r14_packet\\raw\\ts10_12_double_build.py --help",
    "exit": 0,
    "stdout": "usage: ts10_12_double_build.py [-h] [--lock LOCK] [--selftest]\n                               [--build-id {A,B}] [--compare]\n\nCandidate neutral ZIP harness, NOT a Host/plugin schema or release approval.\nConsumes an Owner-approved, hash-pinned staging lock; never invokes draft\nplugin code. Only output-root writes; ZIP_STORED deliberately removes zlib\nvariance.\n\noptions:\n  -h, --help        show this help message and exit\n  --lock LOCK\n  --selftest\n  --build-id {A,B}\n  --compare\n",
    "stderr": ""
  },
  {
    "command": "python -B -I C:\\Projects\\Agent_Workspace\\_r14_packet\\raw\\ts10_12_double_build.py --lock C:\\Projects\\Agent_Workspace\\_r14_packet\\raw\\ts10_12_approved_build.lock.json --build-id A",
    "exit": 1,
    "stdout": "",
    "stderr": "Traceback (most recent call last):\n  File \"C:\\Projects\\Agent_Workspace\\_r14_packet\\raw\\ts10_12_double_build.py\", line 85, in <module>\n    if __name__=='__main__': main()\n                             ^^^^^^\n  File \"C:\\Projects\\Agent_Workspace\\_r14_packet\\raw\\ts10_12_double_build.py\", line 39, in main\n    lock=json.loads(a.lock.read_text(encoding='utf-8'))\n                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\hermes-agent\\.hermes-runtime\\python\\cpython-3.11.17-windows-x86_64-none\\Lib\\pathlib.py\", line 1058, in read_text\n    with self.open(mode='r', encoding=encoding, errors=errors) as f:\n         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n  File \"C:\\Users\\user\\AppData\\Local\\Packages\\OpenAI.Codex_2p2nqsd0c76g0\\LocalCache\\Local\\hermes\\hermes-agent\\.hermes-runtime\\python\\cpython-3.11.17-windows-x86_64-none\\Lib\\pathlib.py\", line 1044, in open\n    return io.open(self, mode, buffering, encoding, errors, newline)\n           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\nFileNotFoundError: [Errno 2] No such file or directory: 'C:\\\\Projects\\\\Agent_Workspace\\\\_r14_packet\\\\raw\\\\ts10_12_approved_build.lock.json'\n"
  }
]
```

## Final obligation disposition

“Ready-to-build” means the bounded design is specified; it is not a Native permit, accepted build or Host qualification. The first commands below are read-only/resumable prerequisites; mutation waits for the stated Owners.

| obligation | ready-to-build | blocked-on | first command to run |
|---|---|---|---|
| R14-TS10 — five independent Host lifecycles + runtime pins=0 drift | PARTIAL: artifact/40-cell verb inventory and narrow repair design ready; lifecycle upgrade/rollback/load/invoke adapters need building | scoped Native/Host WOs; intended runtime/source freeze; actual Host ABI/version discovery; Codex entrypoint resolution; D-17/D-18 repair and independent clean-Host matrix | `python -B C:/Projects/Agent_Workspace/_r14_packet/raw/ts10_12_extra.py` (reproduce Stack doctor + exact digest comparison before Owner-scoped repair) |
| R14-TS11 — three distributable SP ZIPs | PARTIAL: neutral deterministic archive harness exercised with benign fixture; formal SP pair NOT_BUILT | approved non-draft packaging/schema/version lock and staging; complete licensed inputs; C44 scanner/SBOM/license/secret receipts; trusted interpreter/hash lock; Publisher authority and remote asset download readback | `python -B -I C:/Projects/Agent_Workspace/_r14_packet/raw/ts10_12_double_build.py --help` (then, only with approved lock, execute the exact A/B/compare commands above) |
| R14-TS12 — three private ChatGPT plugins | NO: authority/capability assessment only; 0/3 qualified identities | superseding written non-draft Owner CR; actual target Host/account capability and scoped authority; Native effect authorization; independent Host-issued lifecycle receipts | `python -B -c "from pathlib import Path; print(Path('C:/Projects/Agent_Workspace/_r13_far/CR-PLUGIN-SCHEMA-AUTHORITY.md').read_text(encoding='utf-8'))"` (read authority boundary; do not create/install a plugin) |

