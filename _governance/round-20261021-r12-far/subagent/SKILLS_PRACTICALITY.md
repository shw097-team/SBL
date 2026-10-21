# Candidate skills: host practicality and landing ruling

Assessment date: 2026-10-21. Scope: five live Hermes skill directories and two canonical bundles; read-only subject inspection, not installation, promotion, or acceptance. Only this requested report was intentionally written. No install, uninstall, build, compiler-output write, native admission, database operation, or product/deployment repair was run. Read-only Python checks used `-B`/`PYTHONDONTWRITEBYTECODE=1` to avoid bytecode writes during qualification.

## Decision

**The useful material is mostly available already; copying it into SBL would not establish runtime readiness.** The three principal prompts can guide bounded work now. The HGK adapter passes its installation/root probe but has no authority to grant native effects. The stack's installed integrity check currently fails. Both canonical bundles have all their linked reference files, but neither has the required literal `SKILL.md` filename; challenge-review fails its own skill-root check for that reason.

| Candidate | Usable now without new authority? | Landing recommendation |
|---|---|---|
| tpm-sp | Yes: conversation-level clarification/source-bound handoff; no product writes or acceptance. | NEEDS-WORK — its prompt is usable, but the candidate directory's README points to a nonexistent packaged skill path. |
| commander-sp | Yes: read/freeze inputs and prepare a bounded order; no execution writes under this audit's authority. | NEEDS-WORK — usable instruction text is not a complete runnable/authorized build package, and its README package path is broken. |
| external-challenge-sp | Yes: read-only, candidate-bound advisory review; not a signed canonical challenge verdict. | KEEP-EXTERNAL — the live copy contains host-local research additions and should not silently become the product's canonical reviewer. |
| hgk-governed-runtime | Yes: inspect config and run the read-only adapter doctor; no native execution authority. | KEEP-EXTERNAL — this is a machine-bound adapter/config, not a portable control package or a native admission implementation. |
| sbl-stack | Yes: status and diagnosis; no claim of healthy deployment, and no lifecycle mutations here. | NEEDS-WORK — doctor reports live-source digest drift, and operator instructions omit required arguments for several commands. |
| construction-acceptance-prompt-compiler | Yes: explicit Python lint/activation/acceptance and in-memory checks; not automatic skill discovery or runtime qualification. | KEEP-EXTERNAL — retain one externally pinned canonical compiler/schema rather than duplicate the governing methodology in product source. |
| challenge-review | Partly: manual reading and direct validator functions; the supplied skill package does not qualify as-is. | KEEP-EXTERNAL — retain one canonical external checker and resolve its filename defect with its owner before release-significant use. |

These labels assess the complete supplied directories, not merely whether their prose is sensible. No whole candidate directory warrants LAND-AS-IS on this evidence. KEEP-EXTERNAL is a distribution boundary, not a claim that the external material has no defects.

## Locations and measured baseline

- `H = C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/skills/sbl`
- `C = C:/Projects/Agent_Workspace/知識庫/工程基座/construction-acceptance-prompt-compiler/construction-acceptance-prompt-compiler`
- `R = C:/Projects/Agent_Workspace/知識庫/工程基座/challenge-review`
- Product inspected: `C:/Projects/Agent_Workspace/SBL`.
- Deployments inspected: `C:/Projects/Agent_Workspace/SBL-install/{stack,hgk-adapter}`.

The file counts below are recursive observed counts, including existing bytecode where noted. All five Hermes entries were successfully retrieved through `skill_view`; that proves this session could retrieve their instructions, not automatic routing, sandbox enforcement, plugin installation, or functional invocation.

Important host distinction: `python` is the Hermes venv interpreter, version 3.11.17. `python3` resolves to the WindowsApps shim; it was not established as a working interpreter. Use `python -B`, not an assumed functioning `python3`. PATH `sbl-stack` and `sbl-harness` resolve to the Hermes venv's executables; module discovery resolves their Python implementations under **`C:/Projects/Agent_Workspace/_r12_docs`**, not automatically the product worktree or the deployment interpreter recorded in adapter.json. That makes cross-surface claims especially unsafe.

## 1. tpm-sp

**Actual contents — 3 files.** `SKILL.md`, `plugin.json`, `README.md`. Frontmatter has only `name: tpm-sp` and `description`. Sections: What you do; What you refuse; Output shape; Limits. It defines source-ledger discipline, bounded handoff fields (`goal`, `fuo`, non-goals, assumptions, decisions, positive/negative acceptance, questions, sources), and no build/self-acceptance. The plugin declares version 0.1.0, product-manager identity, goal.read/spec.write/evidence.read permissions, forbidden product.write/challenge.sign, and HOST_PENDING/NOT_INSTALLED. There are no scripts, assets, tests, or reference files. DOC-01/DOC-03/DOC-04 are external source locators, not bundled documents. The SKILL.md bytes match the corresponding `_r12_docs/sbl_sp/plugins/tpm_sp/SKILL.md`.

**Use now.** Its conversational behavior needs no new authority; persisted specifications need an explicitly allowed output scope. This audit can assess the rules, not exercise a new product write.

**One effectiveness check.** On a bounded real request, compare the produced handoff against SKILL.md's Output shape: require every field and source locator plus both acceptance cases; ask it to assert an unlocated requirement and require UNVERIFIED instead. This behavioral canary is **not run** here; successful skill retrieval alone is weaker evidence.

**Landing risk / exact gap.** README.md claims `skills/tpm-sp/SKILL.md`, but `H/tpm-sp/skills/tpm-sp/SKILL.md` does not exist: the actual entry is directly at `H/tpm-sp/SKILL.md`. Copying this flattened directory as a portable plugin perpetuates the false layout. Bare DOC identifiers need a resolvable source-ledger route, not a vendored copy of the owner-held books. Plugin permissions are declarations, not tool-enforced grants.

**Recommendation: NEEDS-WORK.** Keep the prompt usable, but choose and validate either a direct-skill layout or a real portable-plugin layout before landing the complete candidate.

## 2. commander-sp

**Actual contents — 3 files.** `SKILL.md`, `plugin.json`, `README.md`. Frontmatter: name and description only. Sections: What you do; What you refuse; Output shape; Limits. Requires frozen PI/PD, execution contract, acceptance plan, repository root/HEAD/write set, reversible steps and raw evidence; forbids out-of-set/link-escape writes, stale-HEAD execution and maker acceptance. Output is a build order, commands/exits/stdout hashes, candidate SHA, locators and open items. Plugin declares build-commander, product.write/build.route/evidence.read, forbidden challenge.sign/verdict.sign, HOST_PENDING/NOT_INSTALLED. No scripts/assets/tests/references. The SKILL.md matches `_r12_docs/sbl_sp/plugins/commander_sp/SKILL.md` byte-for-byte.

**Use now.** Read and prepare a build order from supplied frozen inputs. Missing inputs should stop preparation. Actual building is not authorized by loading this prompt and is expressly outside this audit.

**One effectiveness check.** Supply a frozen HEAD/write set, then present a changed HEAD or a write outside that set: require refusal and a re-preparation/open item, not a command that changes the subject. **Not run**; no frozen build order was supplied in this assessment.

**Landing risk / exact gap.** README.md's `skills/commander-sp/SKILL.md` is missing under the candidate directory; only the flattened SKILL.md exists. There is no bundled executable enforcing HEAD or write-set checks, so shipping the prose as an enforcing build runtime overstates it. Duplicating embedded skill text and deployed copies creates a maintenance drift surface.

**Recommendation: NEEDS-WORK.** Land only after package layout/source ownership and a refusal canary are defined; do not confuse this prompt with build admission or enforcement.

## 3. external-challenge-sp

**Actual contents — 4 files.** `SKILL.md`, `plugin.json`, `README.md`, `references/git-branch-ruling.md`. Frontmatter: name and description only. Sections: What you do; What you refuse; Output shape; Read-only branch research; Limits. Outputs advisory PASS/FAIL/PARTIAL/BLOCKED variants with subject SHA, command/exit/raw hashes, findings and coverage exclusions; explicitly says this is not PASS_CHALLENGE without canonical validation and a distinct signer. Plugin declares independent-challenger/read_only, evidence.read/challenge.sign, forbidden product.write/goal.write. The linked branch reference exists and covers isolated Git research, ancestry/patch equivalence, CI interpretation, scratch-test pitfalls, enumeration and five branch-ruling labels. No scripts, assets or tests.

**Use now.** Read-only advisory review is practical. Its branch-reference workflow can create clones, merge-tree objects, and scratch metadata: those steps must not be performed against a protected subject under a read-only audit. No signing keys or challenge authority were used.

**One effectiveness check.** For a frozen SHA and evidence-manifest digest, independently reproduce one claim and one counterexample, then require each reported finding to bind command, exit, raw-output hash and coverage gaps; a summary-only PASS must remain unproven. **Not run** as a subject-specific challenge in this task.

**Landing risk / exact gaps.** README's nested `skills/external-challenge-sp/SKILL.md` does not exist in this flattened directory. More importantly, the live SKILL.md differs from `_r12_docs/sbl_sp/plugins/external_challenge_sp/SKILL.md`; the local branch-research addition is not a byte-identical canonical product copy. Generic role verdicts differ from the canonical challenge-review closed report/verdict contract. A declared challenge.sign permission is not a distinct signer's actual authority.

**Recommendation: KEEP-EXTERNAL.** Preserve this host-local reviewer/research aid separately and route formal challenge reports to the pinned canonical validator instead of silently vendoring its local evolution.

## 4. hgk-governed-runtime

**Actual contents — 3 files.** `SKILL.md`, `adapter.json`, `plugin.json`; no scripts/assets/tests/references. Frontmatter: name and description only. Sections: What it does; What it must never do. adapter.json declares SBL-HGK-ADAPTER/1, hgk-harness-abi/1, plan/execute/verify descriptors, native WorkOrder/ExecutionBinding/Permit requirements, HGK 0.1.0 pin/root/spine/registry/dispatcher paths, a historical Windows/Python/interpreter observation, HOST_PENDING and NOT_GRANTED. Plugin repeats the ABI and root observation. The live skill and adapter config each match their installed deployment counterparts byte-for-byte.

**Use now / observed check.** `PYTHONDONTWRITEBYTECODE=1 sbl-harness doctor --target 'C:/Projects/Agent_Workspace/SBL-install/hgk-adapter'` returned **exit 0, ok=true, ROOT_READY, observed_version=0.1.0**, no problems. Its checks establish root/package/spine/registry/dispatcher presence and root-bound import/version only. They do not open the database or prove a WorkOrder→ExecutionBinding→Permit→effect chain. The actual CLI offers probe/install/doctor/uninstall, not plan/execute/verify commands; those ABI labels are declarations, not exercised entry points.

**One effectiveness check.** The doctor command above is an available read-only prerequisite check; actual governed effectiveness would additionally require an independently checked native trace and exact effect readback, which cannot be manufactured or authorized by this skill.

**Landing risk / exact gap.** The host copy's adjacent adapter.json exists, but installed `skills/hgk-governed-runtime/SKILL.md` says to read adapter.json "next to this skill" while `SBL-install/hgk-adapter/skills/hgk-governed-runtime/adapter.json` is absent: the actual file is at deployment root. Shipping the observed host root/interpreter as product defaults is nonportable. Neither the green doctor nor the plugin observation grants native authority.

**Recommendation: KEEP-EXTERNAL.** Keep machine configuration and the pinned HGK dependency outside product control logic, and have the adapter owner fix its deployed config-location instruction without copying HGK itself into SBL.

## 5. sbl-stack

**Actual contents — 1 file.** `SKILL.md`; name/description frontmatter, What it does and What it must never do. It documents install/doctor/selftest/status/uninstall, integrity refusal, STANDALONE_ONLY and HOST_PENDING boundaries. No manifest, scripts, references, assets or tests live in this skill directory; the commands depend on separately installed Python packages.

**Use now / observed check.** `PYTHONDONTWRITEBYTECODE=1 sbl-stack doctor --root 'C:/Projects/Agent_Workspace/SBL-install/stack'` returned **exit 2, ok=false**, with 13 changed component digests out of 14 recorded components. The changes reported are core, dto, errors, modes, gknow, M01–M06, sbl_sp.sp and sbl_sp.plugins. Status returned exit 0 and recorded installed=true/version=0.1.0/STANDALONE_ONLY/NOT_INSTALLED. This is an integrity mismatch between recorded pins and the currently resolved code, not proof that files physically under the deployment were corrupted. The current CLI resolves `_r12_docs`, so source/interpreter provenance needs reconciliation before any repair conclusion.

**One effectiveness check.** Re-run the doctor command above and require exit 0 with every recorded component rehashed; the observed failure proves the refusal path is currently active but does not prove a healthy installation. A positive/negative journey selftest was **not run**: source inspection shows selftest calls plugin building and writes `_stack_selftest_plugins` under its workdir.

**Landing risk / exact gaps.** CLI source requires --root for status and uninstall, but the skill shows bare commands. A bare selftest defaults workdir to the current directory, risking generated artifacts in a product checkout. Shipping only this text does not provide the referenced CLIs. Landing a claim of an operational stack while its current doctor is red would contradict the skill itself.

**Recommendation: NEEDS-WORK.** Reconcile the runtime/pins through the owner-controlled process and document exact root/workdir arguments before landing operator instructions as a usable product surface.

## 6. construction-acceptance-prompt-compiler

**Actual contents — 22 files.** Entry file is **`construction-acceptance-prompt-compiler_SKILL.md`, not `SKILL.md`**. Its frontmatter has name/description; sections: Establish the working boundary; Compile C0–C9; Enforce hard invariants; Run deterministic validation; Render only compiled decisions; Return the compiler result. Linked references all exist: source-routing.md, contract-model.md, activation-runtime.md, acceptance-evidence.md, termination-permissions.md, rendering-and-antipatterns.md, prompt-contract.schema.json. Other files: scripts/prompt_contract_compiler.py; four evo contract JSONs (evo004_contract, evo004r5_contract, evo005r6_contract, evo005r7_contract); tests/test_prompt_contract_compiler.py; fixtures/baseline.json and golden.json; agents/openai.yaml; assets/icon.svg; four existing CPython 3.11/3.12 bytecode files. The agent config has implicit invocation and product metadata, not proof of discovery in Hermes.

The Python compiler contains lint, activation, acceptance, render, compile, hash and duplication commands. Compile writes report/prompt/receipt and withdraws stale executable outputs on failure. Schema validation is attempted through jsonschema; these checks ran successfully on this host. No third-party install was performed.

**Use now / observed check.** `python -B '<C>/scripts/prompt_contract_compiler.py' lint '<C>/tests/fixtures/baseline.json'` returned **exit 0, PROMPT_COMPILE_PASS, error_count=0** (replace <C> with the exact root above). Five selected read-only unittest methods passed: baseline, 18 golden fixture subcases, ten-section rendering, duplication detection, CLI lint; 5 tests, 0 failures/errors/skips. Output-writing tests were deliberately excluded. Passing a baseline with open runtime work proves contract checks, not closed runtime readiness.

**One effectiveness check.** Re-run the bundled golden-fixture method in memory under `PYTHONDONTWRITEBYTECODE=1 python -B` and require all 18 expected verdict/code sets, including refusal controls. This check was run successfully here; no compiler outputs were written.

**Landing risk / exact gaps.** No linked reference is missing. The literal discovery entry `C/SKILL.md` is missing, and documented python3 commands require adaptation to the working host interpreter. Vendoring creates a second schema/compiler/control-method copy with a byte-identity maintenance burden; shipping example historical contracts or pyc files adds stale/run-specific material. The compiler itself expressly forbids creating a second workflow/control plane and forbids compiler-pass→runtime-pass promotion.

**Recommendation: KEEP-EXTERNAL.** Use a locator/digest-pinned external compiler and have its owner resolve discovery/command packaging; do not fork its normative schema and methods inside SBL.

## 7. challenge-review

**Actual contents — 15 files.** Entry is **`challenge-review-SKILL.md`, not `SKILL.md`**; name/description-only frontmatter. Sections: Role; Invariants; Intake; Workflow (freeze/inventory, reconstruct acceptance, challenge, calibrate/adjudicate, report/stop); Safety and permissions; Qualification. All six required references exist: adjudication-resume.md, evidence-intake.md, finding-contract.md, gate-calibration.md, rp002-profile.md, security-permissions.md. Other files: scripts/verify_review_bundle.py and validate_package.py; assets/EXTERNAL_CHALLENGE_REPORT.template.md and icon.svg; agents/openai.yaml; evals/trigger_cases.jsonl (12 cases); tests/test_package_validation.py and test_verify_review_bundle.py. The validator implements closed report/intake validation, pointer/hash/subject binding, deterministic Markdown, package checks and a self-test. No standalone JSON schema file is required by this SKILL; its validator supplies the closed contract.

**Use now / observed check.** `python -B '<R>/scripts/verify_review_bundle.py' --skill-root '<R>'` returned **exit 1, status=FAIL, skill_errors=["SKILL.md: missing"]**. Directly parsing the actual alternate-named entry gave no frontmatter errors; comparing the validator's REQUIRED_REFERENCES with the directory gave an empty missing list; the trigger-case check also gave no errors. These narrower successes do not cancel the failing skill-root check.

**One effectiveness check.** The skill-root command above must return clean before a packaged skill claim. For a real challenge, its documented `--bundle-root ROOT --intake INTAKE --report REPORT` validation must also accept subject-bound raw evidence and deterministic Markdown; no frozen review bundle was supplied, so no PASS_CHALLENGE was issued. Self-test/full suites were not run because they write temporary evidence, and package-wrapper tests depend on distribution layout that is not present here.

**Landing risk / exact gaps.** No required reference or linked template is missing. `R/SKILL.md` is missing and its own tests/validator expect that literal filename. A source bundle does not establish a valid distribution ZIP or installed plugin wrapper. Copying this validator/report schema into the product it judges increases correlated maker/checker maintenance risk and duplicates the canonical control package. The RP-002 profile is scoped external guidance, not SBL/HGK acceptance authority.

**Recommendation: KEEP-EXTERNAL.** Preserve the canonical checker outside its subject, request the smallest owner-approved packaging fix, and require genuine package and frozen-evidence qualification before formal use.

## What should not ship

**DO-NOT-SHIP forms (not blanket rejection of the underlying methods):**

1. Either canonical bundle copied wholesale into SBL as a new normative control plane or a mutable duplicate of the canonical compiler/checker.
2. A challenge-review distribution claiming qualification while its own `--skill-root` check fails, or either bundle advertised as an automatically discoverable skill without a literal SKILL.md entry.
3. Host-observed adapter.json/root/interpreter/ROOT_READY data published as portable defaults or current native-execution proof.
4. A "healthy installed stack" assertion based on status alone while doctor reports 13 digest mismatches.
5. Flattened principal directories advertised as valid portable plugin packages while their own README-bound nested skill paths do not resolve.
6. Existing pyc caches, historical evo task contracts, credentials/signing material, native HGK code/databases, or owner-held specification books included merely to make a self-contained-looking product package.

SBL's current `pyproject.toml` declares only the sbl-todo executable and the sbl_core/sbl_sp/sbl_cli package list. Therefore copying these prompts into skills/ alone would not ship the separate sbl-stack/sbl-harness implementations. `SHIPPED_MATERIAL_INVENTORY.md` explicitly excludes the owner-held specification corpus and describes locator-only reuse; importing canonical external content would require a provenance/distribution decision, not a silent expansion of that inventory. No licensing conclusion or permission to redistribute was inferred from a plugin's MIT field.

## Evidence and completion boundary

Read directly: all five live skill entries, adjacent manifests/READMEs/config, the branch reference, both actual canonical entry documents, their linked Markdown references, compiler/test code, validator/package-test portions, resolved CLI implementation paths, product packaging/inventory. Measured missing links/paths and byte comparisons in Python rather than inferring from skill descriptions.

Not run: installations/uninstalls, selftests that generate plugin packages, full write-producing test suites, product builds, native WorkOrder/Permit issuance, signed independent acceptance, real release/distribution qualification, or behavioral role canaries without a frozen task. No repairs were attempted. This report is a practicality/landing recommendation, not HOST_INSTALLED, EFFECTIVE_LOAD, native-effect, release, or production acceptance evidence.
