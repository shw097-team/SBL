# 關鍵漂移：原 PIPD Writer 已在 ARCHIVE 後移轉到 SBL（本輪必讀）

觀測時間：2026-11-03（CT-00 期間實讀）

## 事實

| 項 | 舊（本輪 Prompt 假設） | 當期實讀 |
|---|---|---|
| 原 canonical writer | `PIPD-LS-SP` `main` `a25fb56` | **SBL `main` `b7445b0`**，套件 `pipd-ls-sp 0.1.1a5`，來源 `SBL/integrations/pipd/` |
| PIPD 狀態 | 可用原 Reader | `PIPD-LS-SP@221dc61`，**`archived=true`**、`MAINTENANCE_FROZEN`、`write_authority=NONE` |
| 相關 PR | — | SBL #22（U04 C4 port + 0.1.1a5）、#23（ARCHIVE_ADMIN_HOLD，實測 403）、#24（C4 結案：archive 已完成並回讀） |
| 我的上一輪 | SBL `579d53a`（PR #21） | 仍存在於歷史，未被改寫 |

## 對本輪的影響

1. **CT-00 的真值必須以 SBL `b7445b0` 為 Host/Reader 身份**，不是 PIPD repo。PIPD 只能作歷史 RawRef 引用。
2. **P0_COMPATIBILITY 須對新 canonical 樹重驗**，不能只引舊 PIPD 的 13/19。
3. C2 的四件 bundle 是 schema 級的，跨樹可攜；已在新樹上重跑（見下）。

## 已在新 canonical 樹上的重驗（真跑）

```
worktree: _run_sbl_tpm_pre_v2_final_20261103/deliver/sbl-main  (detach origin/main b7445b0)
PYTHONPATH=<wt>/integrations/pipd/src python -c "build_parser()"
  -> cli_verbs 13
  -> verbs: bind-pd, compile-ecp, compile-pi, compile-tqaep, diff, doctor, export,
            init, intake, profile, project, repair, validate
pipd_ls_sp.registry.EXPECTED_FAMILIES -> 19
pipd validate --bundle RUN-20261102-GJ02-01/c2/bundle.json --require-four -> exit 0
   (輸出：samples/validate_sbl_0111a5.out)
```

## 尚未因漂移而改變的結論

- `EFFECT_REGISTRY_UNBOUND` 仍成立：新樹同樣沒有 operation/effect registry（`integrations/pipd/schemas/` 40 個 json 中無 operation-registry；adapter 仍要求外部 `SBL.OperationRegistry.Binding@2`）。
- `CANONICAL_TQAEP_HANDOFF_HOLD` 仍成立：adapter `grant_state='NOT_GRANTED'`、`claim_ceiling='AUTHOR_DESIGN_ONLY'`（`pre_v2_adapter.py:235-237`）、case/runner `NOT_RUN`（同檔 274-275）。
- `HOST-124` 仍在：Codex 以 `"C:\Users\user\AppData\Local\Microsoft\WindowsApps\pwsh.exe" -Command …` 執行；該 alias 指向 Store 版 PowerShell 7.6.9，`workspace-write` 下被 policy 拒。

## 本輪處置

- 不追改 SBL `main`（U04 屬另一已結案工作流），只在使用它的當期值作本輪身份與相容性依據。
- 交付 PR 只帶本輪 evidence bundle，不改 `integrations/pipd/` 任何程式。
