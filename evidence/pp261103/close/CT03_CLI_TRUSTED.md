# CT-03 收口：CLI 必須走受信任的 Canonical Operation→Effect ＋ Owner 簽章

**範圍**：只改 SBL `integrations/pipd`。rc.2 ZIP 位元組不動（`3a9da65…`）。

## 1. 改了什麼（最小相容差分）

| 檔案 | 變更 |
|---|---|
| `src/pipd_ls_sp/cli.py` | `compile-ecp --effect-intent` 不再接受呼叫者自帶的 registry 路徑＋自帶 SHA。改為呼叫 `operation_registry.load_trusted()`：契約必須是**committed canonical 路徑**、`HEAD` blob 與工作檔同值、並以 `owner-enrollment.json` 的公鑰驗證 Ed25519 簽章。呼叫者若仍傳 `--operation-registry`，只能等於該 canonical 路徑，否則 `REGISTRY_NOT_CANONICAL`；SHA 不符則 `REGISTRY_SHA_MISMATCH`；未 ratified 則 `OWNER_RATIFICATION_REQUIRED`。 |
| `src/pipd_ls_sp/operation_registry.py` | 新增 `repo_root_from_package()`（由模組位置推導，呼叫者無法指向自己的樹）、`_committed()`、`verify_owner_sidecar()`、`load_trusted()`。`cryptography` 缺失時 **fail closed**（`OWNER_SIGNATURE_VERIFIER_UNAVAILABLE`），不是放行。 |
| `src/pipd_ls_sp/errors.py` | 新增 `RegistryUntrusted(PipdError)`，`code=REGISTRY_UNTRUSTED`；CLI 以 typed envelope＋exit 2 回報。 |
| `pyproject.toml` / `integrations/pipd/pyproject.toml` | `tpm-pre-v2` 與 `test` extra 加入 `cryptography>=42`（驗簽所需，非品質選項）。 |

**未變**：13 CLI verbs、19 canonical families、ECP ABI、`--require-four` 語義。`effect_class` 仍只由契約中的 `operation_type` 決定，**不由路徑推斷**；輸出一律 `grant_state=NOT_GRANTED`、`claim_ceiling=DESIGN_ONLY`。

## 2. 受影檢測（本機實跑）

```
tests/test_ct03_cli_trusted_registry.py ............ 6 passed
  POS  canonical 載入＋簽章驗證：verified=True, authority=SOURCE_BOUND_OWNER_RATIFIED,
       contract_sha256=bedf8754…, grant_state=NOT_GRANTED, claim_ceiling=DESIGN_ONLY
  NEG1 --operation-registry <forged> --operation-registry-sha256 000…  -> exit 2, code=REGISTRY_NOT_CANONICAL
  NEG2 canonical 路徑 + 錯 SHA                                        -> exit 2, code=REGISTRY_SHA_MISMATCH
  NEG3 簽章被改（signature_hex=00…）                                  -> OWNER_SIGNATURE_INVALID
  NEG4 契約在簽章後被改（r3.1→r3.9）                                   -> SIGNED_CONTRACT_SHA_MISMATCH
  NEG5 未知 operation                                                  -> OPERATION_TYPE_UNKNOWN_OR_DUPLICATE
```

回歸（未退化）：

```
tests/test_pipd_adapter.py tests/test_sbl_tpm_sp_bundle.py           11 passed
integrations/pipd/tests/test_validate_four_objects.py
integrations/pipd/tests/test_pre_v2_adapters.py
integrations/pipd/tests/test_operation_registry_r3.py
integrations/pipd/tests/test_owner_ratification_r3.py                31 passed
CLI verbs = 13 ； registry.EXPECTED_FAMILIES = 19
```

## 3. 這證明了什麼、沒證明什麼

**證明**：正式 ECP 只能由「已提交、已簽章、且簽章當下等於現行位元組」的契約產生；呼叫者無法用自帶 JSON／自帶 SHA／改 `authority_state` 字串冒充。
**未證明**：任何 Native 執行資格。簽章綁的是**效果值集**，不是 Grant；`grant_state` 恆為 `NOT_GRANTED`。
