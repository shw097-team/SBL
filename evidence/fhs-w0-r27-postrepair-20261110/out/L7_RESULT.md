# L7 — r27 append-only 候選 ＋ 七份藍圖差額（EC-R26-010／012、R26-10、E12）

- **status**：`PASS`　**verdict**：`R27_APPEND_ONLY_CORRECTION_RECORDED`
- **r27**：`evidence/fhs-w0-r27-repair-20261110/doc/FHS_PIPD-LS-PKG_W0_r27.md`，689974 bytes，sha256 `9f2af277450669e3c4f71d3fff4e36c53dcdaa988db00f7f651ac4e24b077dbc`
- **前綴**：667205 bytes 與 r26 LF 形完全相同（`cmp` exit 0）；r26 raw 形 668,540／`0ea05544…` 與其只差 1,335 個 CRLF 行尾，去 CR 後逐位元相等 → 同一份文件兩種位元形式
- **CH27**：8 個小節（CH27.1–27.8）＋ CH27.V 可重現證明；每一節含 finding id、舊文逐字、新值、指令
- **藍圖差額**：7 份，全部 `PROPOSED_FOR_RATIFICATION`；12 個錨點 12/12 OK；29 個實跑案例（7 接受／22 拒絕）全部命中預期拒絕碼

## 命令與 exit（每行都有 log 與 log sha256，見 `out/L7_RESULT.json`）

| # | 命令 | exit | log |
|---|---|---|---|
| 1 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe pin_r26_identity.py` | 0 | `evidence/L7/logs/01_pin_r26_identity.log` |
| 2 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe build_r27.py` | 0 | `evidence/L7/logs/02_build_r27.log` |
| 3 | `head -c "$(stat -c%s 'C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-docs/evidence/fhs-w0-r26-repair-20261109/doc/` | 0 | `evidence/L7/logs/03_cmp_prefix.log` |
| 4 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe check_append_only.py --r26 C:/Projects/Agent_` | 0 | `evidence/L7/logs/04_check_append_only_pos.log` |
| 5 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe check_append_only.py --r26 C:/Projects/Agent_` | 1 | `evidence/L7/logs/05_neg_prefix_flip.log` |
| 6 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe check_append_only.py --r26 C:/Projects/Agent_` | 2 | `evidence/L7/logs/06_neg_truncated.log` |
| 7 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe run_amendment_negatives.py` | 0 | `evidence/L7/logs/07_amendment_negatives.log` |
| 8 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe pin_anchors.py` | 0 | `evidence/L7/logs/08_pin_anchors.log` |
| 9 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe measure_l7.py blueprint_measure.json` | 0 | `evidence/L7/logs/09_measure_l7.log` |
| 10 | `C:\Users\user\AppData\Local\Programs\Python\Python311\python.exe build_delta.py` | 0 | `evidence/L7/logs/10_build_delta.log` |
| 11 | `for c in VOTE_TYPE_INVALID MISSING_CANDIDATE_BINDING RAW_DIGEST_MISMATCH PROCESS_ID_DUPLICATE POOL_DIGEST_DRIF` | 0 | `evidence/L7/logs/11_contract_codes.log` |
| 12 | `for d in sbl-quorum sbl-3lm hgk-hook sbl-meta; do printf "## %%s branch=%%s HEAD=%%s\n" "$d" "$(git -C C:/Proj` | 0 | `evidence/L7/logs/13_landing_status.log` |
| 13 | `git -C C:/Projects/Agent_Workspace/FHS/HG-KSEOS rev-parse 52c9c21 86f40ec; echo "rev-parse EXIT=$?"; git -C C:` | 0 | `evidence/L7/logs/12_hgk_ancestry.log` |

## 負例（全部本輪實跑，含具名拒絕碼）

| id | 期望 | 實得 | exit |
|---|---|---|---|
| `neg_flip` | `PREFIX_NOT_IDENTICAL` | `PREFIX_NOT_IDENTICAL` | 1 |
| `neg_trunc` | `PREFIX_TRUNCATED` | `PREFIX_TRUNCATED` | 2 |
| `L0/NEG_PREFIX@1000` | `AMENDMENT_PREFIX_MISMATCH` | `AMENDMENT_PREFIX_MISMATCH` | 1 |
| `L0/NEG_ANCHOR` | `AMENDMENT_ANCHOR_MISSING` | `AMENDMENT_ANCHOR_MISSING` | 3 |
| `L0/NEG_MARKER` | `MARKER_MISSING` | `MARKER_MISSING` | 5 |
| `L1/NEG_PREFIX@1000` | `AMENDMENT_PREFIX_MISMATCH` | `AMENDMENT_PREFIX_MISMATCH` | 1 |
| `L1/NEG_ANCHOR` | `AMENDMENT_ANCHOR_MISSING` | `AMENDMENT_ANCHOR_MISSING` | 3 |
| `L1/NEG_MARKER` | `MARKER_MISSING` | `MARKER_MISSING` | 5 |
| `L1/NEG_DESIGNID` | `DESIGNID_COUNT_DRIFT` | `DESIGNID_COUNT_DRIFT` | 4 |
| `L2/NEG_PREFIX@1000` | `AMENDMENT_PREFIX_MISMATCH` | `AMENDMENT_PREFIX_MISMATCH` | 1 |
| `L2/NEG_ANCHOR` | `AMENDMENT_ANCHOR_MISSING` | `AMENDMENT_ANCHOR_MISSING` | 3 |
| `L2/NEG_MARKER` | `MARKER_MISSING` | `MARKER_MISSING` | 5 |
| `W1/NEG_PREFIX@1000` | `AMENDMENT_PREFIX_MISMATCH` | `AMENDMENT_PREFIX_MISMATCH` | 1 |
| `W1/NEG_ANCHOR` | `AMENDMENT_ANCHOR_MISSING` | `AMENDMENT_ANCHOR_MISSING` | 3 |
| `W1/NEG_MARKER` | `MARKER_MISSING` | `MARKER_MISSING` | 5 |
| `W2/NEG_PREFIX@1000` | `AMENDMENT_PREFIX_MISMATCH` | `AMENDMENT_PREFIX_MISMATCH` | 1 |
| `W2/NEG_ANCHOR` | `AMENDMENT_ANCHOR_MISSING` | `AMENDMENT_ANCHOR_MISSING` | 3 |
| `W2/NEG_MARKER` | `MARKER_MISSING` | `MARKER_MISSING` | 5 |
| `W3/NEG_PREFIX@1000` | `AMENDMENT_PREFIX_MISMATCH` | `AMENDMENT_PREFIX_MISMATCH` | 1 |
| `W3/NEG_ANCHOR` | `AMENDMENT_ANCHOR_MISSING` | `AMENDMENT_ANCHOR_MISSING` | 3 |
| `W3/NEG_MARKER` | `MARKER_MISSING` | `MARKER_MISSING` | 5 |
| `W4/NEG_PREFIX@1000` | `AMENDMENT_PREFIX_MISMATCH` | `AMENDMENT_PREFIX_MISMATCH` | 1 |
| `W4/NEG_ANCHOR` | `AMENDMENT_ANCHOR_MISSING` | `AMENDMENT_ANCHOR_MISSING` | 3 |
| `W4/NEG_MARKER` | `MARKER_MISSING` | `MARKER_MISSING` | 5 |

## 明確不主張

- `FULL_W0_CLOSEOUT`
- `NATIVE_SIGNED`
- `INDEPENDENT_PASS_CHALLENGE`
- `RELEASE_GRANTED`
- `CROSS_SESSION_HARD_ENTRY (for any host)`
- `any of the seven blueprint amendments being in force (all are PROPOSED_FOR_RATIFICATION)`
- `any CH27.5 refusal code being *proven to refuse* by this lane: what is measured here is string presence at a branch HEAD, not a captured refusal (that belongs to each lane's selftest log)`
- `FHS_ENTRY_* being landed anywhere (r27/fhs-entry-hook is still at acd9196)`
- `main_is_ancestor=true`
- `327 commits ahead`
- `r27 being signed, published, merged, or independently reviewed`

## 備註

1) Identity drift, recorded not reconciled: the brief names the frozen r26 as 668540 bytes / 0ea0554..., but the file at the worktree path is the LF form 667205 / 09c666d (git blob 9b3d0119). They are one document: 1,335 CRLF lines, CR-stripped equality proved (logs/01_pin_r26_identity.log), and `git hash-object` of the raw copy returns the same blob. r27's prefix is byte-identical to the LF form (cmp exit 0) and therefore to the declared identity under the repo's own eol=lf rule. 2) The CH27.5 status was measured twice on purpose: logs/11_contract_codes.log at HEAD 1cb8abb (before the sibling lanes committed) shows only RETIRED_ARM; logs/13_landing_status.log shows the current state (quorum codes in r27/quorum-g29@3099dec, binding codes in r27/fhs3lm-binding@5402fe3, FHS_ENTRY_* still absent, hgk-hook at acd9196). CH27.5 carries both, and claims string presence only. 3) No code changes, no pushes, no merges; r25/r26 untouched (byte-identical before and after). 4) 12_hgk_ancestry is a chained shell command: its process exit is the last echo's, so the interesting sub-exits (merge-base exit 1, is-ancestor exit 1) are printed inside the log rather than surfaced as the process status.
