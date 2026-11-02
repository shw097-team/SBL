# PRE-V2 candidate handoff — 2026-11-02

Receipt-free planning and six Effect-specific original ECP projections are implemented
as an additive candidate. Canonical SBL entry remains `sbl_sp/plugins/tpm_sp/SKILL.md`.
Public changes: adapter, four closed Sidecar schemas, source fixture, 47 attacks,
original-Reader reproducer, package-data wiring and the upstream PIPD patch.
Private 14-Skill updates, raw 24 DOC Corpus and original-ID locator ledger stay local.

ClaimCeiling: **AUTHOR_DESIGN_ONLY / partial candidate with HOLDs**. This is not
a merged RC, independent acceptance, Host qualification or release.

- Private unittest: **182 PASS**, including original 107, blueprint 28 and new 47.
- Original PIPD affected legacy: **53 PASS**; final new owner controls: **25 PASS**.
- Original main CLI/Reader: three canonical objects accepted, **FULL graph closure**.
- Owner candidate Sidecar Reader/CLI: receipt-free plan accepted with real fixture bytes.
- Legacy semantic replay: **63 PASS, 1 BLOCKED** original graph fixture.
- Full SBL suite: **HOLD**, bounded UTF-8/real-Host rerun timed out after 240s.
- Codex: **14 loaded; explicit Trigger, real source Reader Used, Nontrigger and original rollback PASS**.
- ChatGPT: **PRIVATE_UPDATE_NOT_RUN / EXECUTOR_UNBOUND**; no official update interface here.

Actual PIPD main has **14 commands**, including repair, and **19 canonical Schema
families**. Original canonical IDs/default live-receipt behavior stay unchanged.
Owner candidate commit: `31a3897b871778a14530efdec92a918f0b9d7413` (local only). Patch SHA256: `a892412d018d39cca5bf20103e380c9dcc05d153211506c385e06ec4a32c0ea1`.

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
