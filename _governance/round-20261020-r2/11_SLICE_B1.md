# Slice B1 (bounded, small) — SP separation + skill bridge + skill manifest

Root: `C:/Projects/Agent_Workspace/SBL` only. Python 3.11 stdlib only (tests may use pytest).
Existing code: `sbl_core/` (errors.SBLError, dto dataclasses). Import it, do not modify it.

Create exactly these files:

## 1. `sbl_sp/__init__.py` (re-export the public API)
`from .sp import load_manifest, assert_permission, sign_verdict, MANIFEST_DIR`

## 2. `sbl_sp/manifests/tpm_sp.json`
```json
{"schema":"SBL-SP-MANIFEST/1","sp_id":"tpm_sp","name":"TPM-SP","role":"product-manager",
 "permissions":["goal.read","spec.write","evidence.read"],
 "forbidden":["product.write","challenge.sign"],"read_only":false}
```
## 3. `sbl_sp/manifests/commander_sp.json`
```json
{"schema":"SBL-SP-MANIFEST/1","sp_id":"commander_sp","name":"Commander-SP","role":"build-commander",
 "permissions":["product.write","build.route","evidence.read"],
 "forbidden":["challenge.sign","verdict.sign"],"read_only":false}
```
## 4. `sbl_sp/manifests/external_challenge_sp.json`
```json
{"schema":"SBL-SP-MANIFEST/1","sp_id":"external_challenge_sp","name":"External Challenge-SP","role":"independent-challenger",
 "permissions":["evidence.read","challenge.sign"],
 "forbidden":["product.write","goal.write"],"read_only":true}
```

## 5. `sbl_sp/sp.py`
- `MANIFEST_DIR = Path(__file__).parent / "manifests"`
- `load_manifest(sp_id: str) -> dict`: unknown id (or path traversal in the id) → `SBLError("SBL_E_UNKNOWN_SP", ...)`.
- `assert_permission(sp_id: str, action: str) -> None`: manifest not found → `SBL_E_UNKNOWN_SP`; `action` in
  `forbidden` OR absent from `permissions` → `SBLError("SBL_E_PERMISSION_DENIED", ...)` with detail
  `{"sp_id":..., "action":...}`; otherwise returns None.
- `sign_verdict(principal_id: str, maker_principal: str, verdict: dict) -> dict`:
  requires `assert_permission(principal_id, "challenge.sign")`; if `principal_id.strip().lower() ==
  maker_principal.strip().lower()` → `SBLError("SBL_E_SELF_CHECK_FORBIDDEN", ...)`; returns
  `{"schema":"SBL-CHALLENGE-VERDICT/1","principal":principal_id,"maker":maker_principal,"verdict":verdict,
  "signature":"SIG-" + sha256(json.dumps([principal_id, verdict], sort_keys=True))[:16]}`.
  Order matters: permission check first, then self-sign check.

## 6. `sbl_sp/bridge.py`
`class SkillBridge`:
- `__init__(self, manifest_path: str)` — loads JSON; missing file → `SBLError("SBL_E_BAD_STATE", ...)`.
- `discover(self) -> dict` → `{"schema":"SBL-SKILL-DISCOVER/1","skill":name,"triggers":[...],"permissions":[...]}`.
- `match(self, intent: str) -> bool` — True iff any trigger appears case-insensitively in `intent`.
- `effective_load(self, host: dict) -> dict` — `host["provider_on"] is not True` → `SBLError("SBL_E_PROVIDER_OFF")`;
  else `{"schema":"SBL-SKILL-LOAD/1","skill":name,"loaded":True,"host":host.get("name"),
  "trace_id":"L-"+sha256(name+host name)[:12]}`.
- `invoke(self, action: str, provider_on: bool) -> dict` — `provider_on` False → `SBL_E_PROVIDER_OFF`;
  `action` absent from manifest `permissions` OR starting with `repo.`/`net.` OR in `forbidden` →
  `SBLError("SBL_E_PERMISSION_DENIED")`; else `{"ok":True,"skill":name,"action":action}`.
- `unload(self) -> dict` → `{"schema":"SBL-SKILL-UNLOAD/1","unloaded":True,"residue":[]}`.

## 7. `skills/sbl_todo/skill.json`
```json
{"schema":"SBL-SKILL-MANIFEST/1","name":"sbl-todo",
 "description":"Create and list local todo items through the sbl-todo CLI",
 "triggers":["todo","task list","待辦"],
 "permissions":["todo.read","todo.write"],
 "forbidden":["repo.write","net.call"],
 "entry":"sbl_cli.sbl_todo"}
```
## 8. `skills/sbl_todo/SKILL.md`
Short skill doc (frontmatter `name`/`description`, when-to-use, the exact CLI commands from Slice B2 once they
exist; for now document `init/add/list/remove/uninstall` as the planned surface and say the CLI is built in the
next slice). 30-60 lines max.

## 9. `tests/test_sp_isolation.py` and `tests/test_gj03_bridge.py`
At least 4 tests each, covering: manifest load for all three, unknown sp refusal, permission refusal on a
forbidden action, maker==checker self-sign refusal, positive challenge sign by a distinct principal, bridge
discover/match true+false, effective_load provider-off refusal, invoke forbidden action refusal, unload residue empty.
Assert the EXACT `SBLError.code` (use `pytest.raises(SBLError)` and compare `exc.value.code`).

## Acceptance command
`python -m pytest tests/test_sp_isolation.py tests/test_gj03_bridge.py -q` → all pass, count >= 8.
Use interpreter `C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe`.
Scratch files (if any) go under `<repo>/.pytest_tmp/` (already gitignored) — never the system temp dir.
No git write commands, no network, no writes outside the repo root.
