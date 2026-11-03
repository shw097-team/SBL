# tasks — sbl-tpm-sp 0.3.1-rc.1

- [x] reader pin issuer implemented and merged (SBL `a5d3a767`, PR #35)
- [x] pin set issued from a clean checkout: 35 files, `f0b287dd…`, `git_head a5d3a767`
- [x] pin set signed by owner window `WIN-9d10aa7face0` (1/20 ops, `READ_ONLY_PROBE`)
- [x] candidate rebuilt: 176 members, 14 `SKILL.md`, 0 bytecode/cache, `f00c5792…`
- [x] candidate author suite: 186 passed
- [x] host chain on the final bytes: install -> loaded -> skill used -> nontrigger -> downgrade rc.2 -> restore 0.3.1-rc.1
- [x] archived with `SHA256SUMS`; rc.1/rc.2 untouched
- [ ] (deferred) wire `CASE_ORACLE_DECLARATION` into a loader — unchanged scope from the previous round
