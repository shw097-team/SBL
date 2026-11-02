# PRE-V2 candidate handoff — 2026-11-02

Receipt-free planning and six Effect-specific original ECP projections are implemented
as an additive candidate. Canonical SBL entry remains `sbl_sp/plugins/tpm_sp/SKILL.md`.
Public changes: adapter, four closed Sidecar schemas, source fixture, 47 attacks,
original-Reader reproducer, package-data wiring and the upstream PIPD patch.
The public owner-baseline overlay includes all 14 updated Skills. Raw 24 DOC Corpus and original-ID locator ledger stay local.

ClaimCeiling: **AUTHOR_DESIGN_ONLY / partial candidate with HOLDs**. This is not
a merged RC, independent acceptance, Host qualification or release.

- Private unittest: **184 PASS**, including original 107, blueprint 28, new 47 and 2 BOM tamper checks.
- Original PIPD affected legacy: **53 PASS**; final new owner controls: **25 PASS**.
- Original main CLI/Reader: three canonical objects accepted, **FULL graph closure**.
- Owner candidate Sidecar Reader/CLI: receipt-free plan accepted with real fixture bytes.
- Legacy semantic replay: **63 PASS, 1 BLOCKED** original graph fixture.
- Full SBL suite: **HOLD**, bounded UTF-8/real-Host rerun timed out after 240s.
- Codex: **14 loaded; explicit Trigger, real source Reader Used, Nontrigger and original rollback PASS**.
- Ordinary-goal implicit Trigger read the actual workflow/source and completed its model turn; process exit timed out (124), retained as transport HOLD.
- ChatGPT: **PRIVATE_UPDATE_NOT_RUN / EXECUTOR_UNBOUND**; no official update interface here.

Actual PIPD main has **13 commands** (13 including repair; original E7 forbids a
14th), and **19 canonical Schema families**. Original canonical IDs/default
live-receipt behavior stay unchanged.
Owner candidate commit: `c7892703da60121c3f3ccb8ae6999ff98c943d3c` (local only). Patch SHA256: `48b8846e37a93813edbcb52145ffd78ab5e70a8f6b0e2980aed9caa25c7fa1d0`.

Source identity retention: original 949 requirements, 192 cells and 282 cases/nodes
have individual locators preserved privately. Other denominators 149/50/39/96
remain separately tracked. Locator presence is not semantic or Native qualification.
The original SourceManifest origin paths are stale; exact release/corpus bytes
match, source-owner ratification stays HOLD. Synthetic regression cases are named
as synthetic and cannot stand for the original FUO/Case/Oracle registries.

Critical open items: bind original Effect/Case/Oracle/FUO registries and receivers;
resolve full repair scope (original CLI fixes src/**); complete full SBL build checks;
obtain official same-plugin update and real ChatGPT compiler execution. The old
graph example remains a preserved counterexample; no test was deleted or expectation
edited to turn it green. No efficiency improvement was measured.

Reproduce: `python -m unittest discover -s tests -p test_tpm_pre_v2.py -v`;
`python tools/check_tpm_pre_v2_compat.py --pipd-root <original> --out <scratch>`.
For upstream tests/application see `sbl_sp/plugins/tpm_sp/pre_v2/upstream/README.md`.
Raw commands and output are retained privately; public evidence carries exits and SHA.

Rollback: revert this candidate commit on an isolated branch or reinstall the
retained original private ZIP; fresh Host must load the original 14 Skill SHA values.
The demonstrated rollback already did so. No main was pushed, merged or force-pushed.

**FHS_PIPD-LS-PKG_v2 formal generation readiness: NO.** Bounded author planning may
continue while these affected binding/Host holds remain explicit.

Final private ZIP SHA256: c4181e247e13905b565bb53938d153c4c719fd65c34cc12d7f11d13c761f8f86
