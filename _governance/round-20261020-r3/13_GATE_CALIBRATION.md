# 13 — Gate calibration (what each gate can and cannot prove)

The point of this page is to stop a green board from being read as a product claim. Every gate below
proves a narrow thing; the "cannot prove" column is the part that matters when someone quotes a number.

| Gate | Deterministic input | Positive case | Negative case | Denominator | Proves | Cannot prove |
|---|---|---|---|---|---|---|
| G-CORE-MODULES | `tests/test_core_modules.py` | spec order is idempotent; a write inside the write set lands; an inside link still works | traversal, absolute path, drive letter, outside prefix, symlink escape, settle-time swap, stale HEAD all refused | 47 | the bridge refuses escapes it knows about | that no other escape exists; that a hostile concurrent writer cannot race the handle |
| G-MODES-NOEFFECT | `tests/test_modes.py` | a signed ACK from a trusted issuer allows `net.call`; PREW3_SHADOW never effects | fabricated / blank / untrusted-issuer ACKs refuse; a signature cannot move tuple | 14 | ACK verification is credential-bound, not string-bound | 39 mode×gate cells against a real host; any Native effect |
| G-KNOW | `tests/test_gknow.py` | real filenames resolve to `DOC-05`; a DOC-05 question answers only DOC-05 | `DOC-27`, `DOC/27`, `DOC--27`, `DOC27`, `doc_27` refused; no-answer and upper-bound enforced | 15 | retrieval is source-bound and refuses rather than fabricating a locator | CJK recall, 61 long paths, semantic recall, version identity |
| G-SP-ISOLATION | `tests/test_sp_isolation.py` | three principals carry distinct permissions | cross-principal writes and challenge signing are refused | 18 | the principals are separated in-process | that three plugins are installed on any host |
| G-GJ03-BRIDGE | `tests/test_gj03_bridge.py` | discovery, trigger and unload work through the bridge | non-trigger and denied permission paths | 7 | the skill *bridge* behaves | a real host loader, plugin id, effective load |
| G-GJ01-CLI | `tests/e2e/test_gj01_cli.py` | init/add/list across processes | empty title refused | 7 | the CLI persists state in a real process | that a wheel installs cleanly (that is AC-R2) |
| G-GJ02-PATCH | `tests/e2e/test_gj02_patch.py` | a bounded patch on a real git fixture | cross-root, race and rollback negatives | 7 | bounded build works on a fixture repo | a native ECP/permit, or an arbitrary external repo |
| G-ROLLBACK | `tests/e2e/test_rollback.py` | rollback restores the prior state | a rollback without evidence refuses | 4 | reversible steps work | crash-consistent replay under power loss |
| G-SOURCE-FREEZE | `tools/verify_source.py --verify` | 14/14 books re-hash to the frozen aggregate | a mutated book fails the aggregate | 14 docs | the normative books match their frozen hashes | that the books' *content* is right; KP/volumes are not covered |
| G-SEC-SCAN | `tools/secret_scan.py` | CLEAN over the tree | fixture emails/tokens are still detected (self-test) | 229 files (candidate worktree) | no obvious secret shape is committed | a determined exfiltration, or secrets in history |
| G-SUITE-FULL | `pytest` | 156 passed on the C candidate, 148 on v13 | the same negatives, aggregated | 156 / 148 | nothing new beyond the above | any host, native or released state |

## Calibration discipline applied this round

1. **No denominator was allowed to become zero.** `run_gates.py` pins `PYTEST_DISABLE_PLUGIN_AUTOLOAD`
   and the CI workflow carries a single `-q`: a second `-q` swallows the `N passed` line and a gate that
   prints nothing is indistinguishable from a gate that ran nothing.
2. **A refusal is only a pass when the refusal is provable.** The M4-LITE probes record which *form* the
   refusal took (`exception` vs `allowed=False`) instead of accepting either shape silently.
3. **Unit tests are never promoted.** `test_sp_plugins.py` asserts the ceiling `HOST_PENDING`; it does
   not assert an installation, because it cannot observe one.
4. **Maker-side vs independent.** Everything in this table was executed by the maker. The independent
   column of R3 remains empty except for the external audit's own read-only observations, which are
   quoted as observations and not re-signed here.
