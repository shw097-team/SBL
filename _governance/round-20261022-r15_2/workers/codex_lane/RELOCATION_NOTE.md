# CODEX_HOME relocation note

The gate run recorded in `log_execute.log` / `log_verify.log` printed:

```
CODEX_HOME=C:\Projects\Agent_Workspace\_r152_ev\_governance\round-20261022-r15_2\workers\codex_lane\home
```

That was true **at run time**. Immediately afterwards the isolated home was moved out of the repository, because
copying the sealed home drags the entire plugin tree into the evidence worktree (and `getsize` then fails on plugin
junctions). It now lives at:

```
%TEMP%\\r152\\codex_home_isolated
```

Consequences for an external auditor:

- The two committed profiles `exe.config.toml` / `ver.config.toml` in that home are **not** in this branch; only the
  briefs, the codex stdout logs and the sha256 guards are. Re-running requires re-copying the sealed home first
  (see the `hgk-codex-lane-recipe` skill).
- The logs are unmodified originals; this note is appended rather than edited into them, so the run remains
  byte-reproducible as recorded.
- The later bounded write + independent check (`log_writer.log`, `log_checker.log`, `guard_before.txt` /
  `guard_after.txt`) ran against the **same** recipe before the relocation, so the guard still frames the write.
