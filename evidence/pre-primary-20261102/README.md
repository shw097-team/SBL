# PRE-V2 pre-primary run — sbl-tpm-sp 0.3.0-rc.2 on a real Codex host

`RUN-20261102-GJ02-01` (2026-11-02, isolate workspace, Windows 11 + Codex CLI 0.164.0).

Result: **`PRE_V2_DESIGN_SIDECAR_READY` + `NATIVE_GOLDEN_HOLD`**. Not
`PRE_V2_GENERATION_READY`, not `NATIVE_GOLDEN_SLICE_PASS`.

What is proven here:

- the package installs into a real Codex host from a **local marketplace** and reports
  `installed, enabled, 0.3.0-rc.2`; the manifest shape that works is in
  `RUN-20261102-GJ02-01/04_closeout.md`;
- a fresh session on **DeepSeek V4.1 Flash (opencode-go)** loads the 14 skills, follows
  `tpm-setup`, and produces `host_notes.md` with honest ceilings;
- an ordinary goal with no plan hints fixes the sandbox defect (tests 2 passed, no test
  expectation edited) and an unrelated goal triggers nothing;
- the **original PIPD writer** turns the same case into PI (17 atoms), PD (real HEAD
  `70757870`, dirty recorded), ECP and a design-ceiling TQAEP, and `validate` returns
  `PASS / checked 4 / closure FULL`;
- `compile-tqaep` without a receipt refuses with `TQ_SOD`; an arbitrary receipt string is
  accepted only as `TQAEP_DESIGNED / NOT_GRANTED`;
- uninstall/reinstall is real (`not installed` -> `installed, enabled`).

What is **not** proven: effect-specific ECP (no operation registry), PlannedTQAEP `@2`
through the author gate, TQAEP usability (no protected checker), owner autonomy, and any
Native effect. See `03_native_receipt_refs.json`.

Files: `00_run_manifest.json`, `02_checkrun.json` (G01–G12 with original test refs),
`03_native_receipt_refs.json`, `04_closeout.md`, `01_products/` (3 SPECs + PIPD objects +
`host_notes.md`), `raw/` (trimmed host/issuer outputs; the full event JSONL stays local).

No corpus, credential, grant, nonce or private key is included.
