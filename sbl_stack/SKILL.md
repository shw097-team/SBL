---
name: sbl-stack
description: Operate the installable SBL stack — install, doctor, selftest, status and uninstall one local STANDALONE deployment
---

# SBL Stack

You are operating the SBL stack as a deployed product surface, not as a source checkout.

Source basis: `DOC-12` C36/C43/C49 (installable packaging and host surfaces); `DOC-04` C12–C15
(one shared core, three principals).

## What it does

1. **Install.** `sbl-stack install --root <dir>` writes an integrity manifest of the exact module
   files it validated, then verifies the composed M01..M06 core before returning. It refuses a
   non-empty directory it did not create — never work around that by clearing the directory.
2. **Doctor.** `sbl-stack doctor --root <dir>` re-derives every digest from the live installation and
   re-runs the composition check. A changed byte is a failure, not a warning.
3. **Selftest.** `sbl-stack selftest` walks one ordinary journey (intake → specification → routing)
   and asserts two refusals: a clause with no locator, and a kind that is `PROHIBITED_IN_V0_1`.
4. **Status / uninstall.** `sbl-stack status` reports the recorded ceiling. `sbl-stack uninstall`
   removes only what the manifest lists and refuses a directory holding anything else.

## What it must never do

- Report `INSTALLED`, `EFFECTIVE_LOAD` or `PRODUCTION` on the strength of a local install. The
  ceiling for this surface is `STANDALONE_ONLY`; the host column stays `HOST_PENDING`.
- Grant a native effect. WorkOrder / ExecutionBinding / Permit belong to HG-KSEOS's own issuer.
- Edit the installed module files to make `doctor` pass — that is the thing `doctor` exists to catch.
