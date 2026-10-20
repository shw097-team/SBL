# SBL v0.1｜BUILD SPEC (PLAN-authored, slice-bound)

Status: PLAN-authored implementation spec for the Round-2 bounded writer.
Authority: `contracts/SBL_C0_C9_CONTRACT.json` (PROMPT_COMPILE_PASS) + `_governance/round-20261020/00_NORTH_STAR.md`.
Write root: `C:/Projects/Agent_Workspace/SBL` ONLY. Never write outside it. Never touch `C:/Projects/Agent_Workspace/知識庫/**`
or `C:/Projects/Agent_Workspace/_sbl_src_mirror/**` (read-only source corpus).

Language/runtime: Python 3.11 (stdlib only; no third-party imports in product code). Tests use `pytest`.
Every module must be importable as `python -c "import <module>"` from the repo root.

Error model (single source of truth): `sbl_core/errors.py`
```python
class SBLError(Exception):
    def __init__(self, code: str, message: str, detail: dict | None = None) -> None: ...
    code: str
    message: str
    detail: dict
    def as_dict(self) -> dict   # {"ok": False, "code": ..., "message": ..., "detail": {...}}
```
Required codes (exact strings):
`SBL_E_EMPTY_TITLE`, `SBL_E_DUPLICATE_TITLE`, `SBL_E_UNLOCATED_REQUIREMENT`, `SBL_E_UNKNOWN_KIND`,
`SBL_E_PROHIBITED_KIND`, `SBL_E_WRITE_OUTSIDE_WRITESET`, `SBL_E_STALE_HEAD`, `SBL_E_SELF_CHECK_FORBIDDEN`,
`SBL_E_CLAIM_CEILING_EXCEEDED`, `SBL_E_UNKNOWN_SP`, `SBL_E_PERMISSION_DENIED`, `SBL_E_KNOWLEDGE_NO_ANSWER`,
`SBL_E_PROVIDER_OFF`, `SBL_E_REQUIRES_NATIVE_ACK`, `SBL_E_REPAIR_WITHOUT_EVIDENCE`, `SBL_E_FOREIGN_FILES`,
`SBL_E_BAD_STATE`.

---

## Slice A — Shared Core (modules SBLM01..SBLM06, modes, G-KNOW)

Files (create): `sbl_core/__init__.py`, `sbl_core/errors.py`, `sbl_core/dto.py`, `sbl_core/m01_intake.py`,
`sbl_core/m02_spec.py`, `sbl_core/m03_routing.py`, `sbl_core/m04_bridge.py`, `sbl_core/m05_verify.py`,
`sbl_core/m06_repair.py`, `sbl_core/modes.py`, `sbl_core/gknow.py`, `sbl_core/core.py`.
Tests (create): `tests/__init__.py`, `tests/test_core_modules.py`, `tests/test_modes.py`, `tests/test_gknow.py`.

### sbl_core/dto.py
Frozen dataclasses with `to_dict()` returning plain JSON-able dicts: `Goal(goal_id,title,description,requester)`,
`SpecAtom(atom_id,text,locator)`, `RouteDecision(atom_id,target,permitted,reason)`,
`RepoContextDTO(root,head,tracked_files,dirty)`, `WriteSet(paths)`, `BuildOrder(order_id,root,head,writeset)`,
`EvidenceItem(gate_id,command,exit_code,stdout_sha256,denominator)`,
`Verdict(gate_id,maker,checker,status,claim_level)`, `RepairPlan(plan_id,first_fail,scope,max_attempts,rollback_pointer,action)`,
`ModeDecision(mode,effect,allowed,no_effect,reason)`, `TodoItem(id,title,status)`.
IDs are deterministic: `goal_id = "G-" + sha256(title.strip().lower())[:12]`, `atom_id = "A-" + sha256(text)[:12]`,
`order_id = "O-" + sha256(head + "|" + ",".join(sorted(writeset.paths)))[:12]`.

### sbl_core/m01_intake.py  (SBLM01 Goal Intake)
`class GoalIntake: def intake(self, title: str, description: str = "", requester: str = "local") -> Goal`
- strip title; empty/whitespace-only → `SBLError("SBL_E_EMPTY_TITLE", ...)`.
- deterministic `goal_id` per dto rule; refuses `len(title) > 200` with `SBL_E_BAD_STATE`.

### sbl_core/m02_spec.py  (SBLM02 Guided Specification)
`class GuidedSpecification: def derive(self, goal: Goal, clauses: list[dict]) -> list[SpecAtom]`
- each clause needs non-empty `text` AND non-empty `locator` (source binding). Missing locator →
  `SBLError("SBL_E_UNLOCATED_REQUIREMENT")`. Zero clauses → `SBLError("SBL_E_BAD_STATE")`.
- preserves input order; `atom_id` per dto rule; duplicate text collapses to one atom (idempotent).

### sbl_core/m03_routing.py  (SBLM03 Governed Routing)
`DEFAULT_POLICY = {"CLI_TOOL": "SBLM04_GOVERNED_BUILD_BRIDGE", "BROWN_PATCH": "SBLM04_GOVERNED_BUILD_BRIDGE", "SKILL": "GJ03_SKILL_AGENT_BRIDGE", "AGENT_OS": None, "AI_SYSTEM": None}`
`class GovernedRouting: def __init__(self, policy=DEFAULT_POLICY); def route(self, atom: SpecAtom, kind: str) -> RouteDecision`
- kind not in policy → `SBL_E_UNKNOWN_KIND`.
- policy value `None` (AGENT_OS / AI_SYSTEM) → `RouteDecision(permitted=False, reason="PROHIBITED_IN_V0_1")` and
  `raise SBLError("SBL_E_PROHIBITED_KIND")` — choose ONE deterministic behaviour: it RAISES (tests assert the code).
- permitted mapping → `RouteDecision(permitted=True, target=<module>)`.

### sbl_core/m04_bridge.py  (SBLM04 Governed Build Bridge)
`def bind_repo_context(root: str) -> RepoContextDTO`  (uses `git -C <root> rev-parse HEAD`, `git -C <root> status --porcelain`;
no git repo → `SBL_E_BAD_STATE`; head is the 40-char sha, `tracked_files` via `git ls-files | wc -l`).
`class GovernedBuildBridge:`
- `def prepare(self, ctx: RepoContextDTO, writeset: WriteSet) -> BuildOrder` — refuses empty writeset (`SBL_E_BAD_STATE`).
- `def apply(self, order: BuildOrder, path: str, content: str) -> BuildOrder` — resolve `path` against
  `order.root`; reject absolute paths, `..` traversal, or any resolved path not under one of the writeset
  prefixes → `SBL_E_WRITE_OUTSIDE_WRITESET`; re-read HEAD and refuse if it changed → `SBL_E_STALE_HEAD`;
  otherwise write the file (parents created) and return a NEW order whose `writeset` includes the applied path.

### sbl_core/m05_verify.py  (SBLM05 Evidence Verification)
`class EvidenceVerification:`
- `def record(self, gate_id, command, exit_code, stdout: str, denominator: int) -> EvidenceItem` — stores
  `stdout_sha256`, refuses `denominator <= 0` with `SBL_E_BAD_STATE`.
- `def verdict(self, gate_id, maker: str, checker: str, status: str, claim_ceiling: str, claim: str) -> Verdict`
  - `maker.strip().lower() == checker.strip().lower()` → `SBL_E_SELF_CHECK_FORBIDDEN`
  - claim rank > ceiling rank (`LOCAL`=0, `PACKAGE`=1, `EXTERNAL_ACCEPTANCE`=2, `PRODUCTION`=3) →
    `SBL_E_CLAIM_CEILING_EXCEEDED`
  - status in the proxy set {"FILE_EXISTS","SYMBOL_EXISTS","SUMMARY_ONLY","DOCUMENTED"} → `SBL_E_BAD_STATE`.

### sbl_core/m06_repair.py  (SBLM06 Bounded Repair)
`class BoundedRepair: def plan(self, first_fail: str, evidence_refs: list[str], attempts: int = 0, max_attempts: int = 3) -> RepairPlan`
- empty `evidence_refs` → `SBL_E_REPAIR_WITHOUT_EVIDENCE`.
- `attempts >= max_attempts` → plan with `action="STOP_ESCALATE"` (no exception, no further patch permitted).
- otherwise `action="NARROW_REPAIR"`; `rollback_pointer` is a string the caller supplies as `evidence_refs[0]`.

### sbl_core/modes.py  (SBL 39 ModeGate = G00..G12 x 3)
`MODES = ("STANDALONE", "PREW3_SHADOW", "SWOF_CONNECTED")`, `GATE_IDS = tuple(f"G{i:02d}" for i in range(13))`.
`def mode_gate_matrix() -> list[dict]` → 39 rows `{"gate_id": "SBL-G00-STANDALONE", "mode": ..., "gate": "G00",
"disposition": "ACTIVE"|"SHADOW_NOEFFECT"|"BLOCKED_EXTERNAL"}`; unique ids; len == 39.
`class ModeGate:`
- `def __init__(self, mode: str, native_ack: dict | None = None)`; unknown mode → `SBL_E_UNKNOWN_MODE`
  (add this code to errors.py).
- `def decide(self, effect: str) -> ModeDecision`
  - STANDALONE + effect in {"local.write","local.read"} → allowed True, no_effect False.
  - PREW3_SHADOW → allowed False, no_effect True, reason "SHADOW_READ_ONLY_NO_EFFECT" (ANY effect).
  - SWOF_CONNECTED → requires `native_ack` dict carrying all of `issuer`, `permit_id`, `subject_id`, `signature`
    with non-empty values; otherwise `SBLError("SBL_E_REQUIRES_NATIVE_ACK")`. With a complete ack: allowed True.

### sbl_core/gknow.py  (G-KNOW local-first, source-bound)
`def build_index(corpus_root: str, out_path: str) -> dict` — walk `**/*.md` + `**/*.json`, skip files
> 2 MiB, chunk by 40 non-empty lines, per chunk record `{locator: "<abs path>#L<start>-<end>", path, start, end,
sha256, text}`; write JSON `{"schema":"SBL-GKNOW-INDEX/1","chunks":[...]}`; return summary counts.
`def query(index_path: str, text: str, top_k: int = 5, min_score: float = 0.34) -> list[dict]`
- token-overlap score (lowercased alphanumeric tokens, score = |q ∩ chunk| / |q|); sorted desc; truncate to top_k.
- empty/absent match (max score < min_score) → `SBLError("SBL_E_KNOWLEDGE_NO_ANSWER")`; never fabricate a hit.
CLI: `python -m sbl_core.gknow {build --corpus DIR --out FILE | query --index FILE --text T [--json]}`,
prints JSON `{"ok":true,"hits":[...]}` or the `SBLError.as_dict()` with exit code 2 on refusal.

### sbl_core/core.py
`class SharedCore: def __init__(self, root: str)` composing GoalIntake, GuidedSpecification, GovernedRouting,
GovernedBuildBridge, EvidenceVerification, BoundedRepair; `def doctor(self) -> dict` returning
`{"schema":"SBL-CORE-DOCTOR/1","modules":["SBLM01",...,"SBLM06"],"ok":true,"root":<abs>}`.

### Acceptance (Slice A)
`python -m pytest tests/test_core_modules.py tests/test_modes.py tests/test_gknow.py -q` → all pass, denominator > 0.
Each test file must contain at least one POSITIVE and one NEGATIVE case asserting the exact error code.

---

## Slice B — SPs, CLI journey (GJ01), skill bridge (GJ03), brownfield patch (GJ02), rollback, source verify

Files: `sbl_sp/__init__.py`, `sbl_sp/sp.py`, `sbl_sp/bridge.py`, `sbl_sp/manifests/tpm_sp.json`,
`sbl_sp/manifests/commander_sp.json`, `sbl_sp/manifests/external_challenge_sp.json`,
`sbl_cli/__init__.py`, `sbl_cli/sbl_todo.py`, `sbl_cli/__main__.py`, `skills/sbl_todo/SKILL.md`,
`skills/sbl_todo/skill.json`, `tools/verify_source.py`.
Tests: `tests/test_sp_isolation.py`, `tests/test_gj03_bridge.py`, `tests/e2e/__init__.py`,
`tests/e2e/test_gj01_cli.py`, `tests/e2e/test_gj02_patch.py`, `tests/e2e/test_rollback.py`.

### sbl_sp/sp.py
Manifest JSON shape: `{"schema":"SBL-SP-MANIFEST/1","sp_id":..., "name":..., "role":..., "permissions":[...],
"forbidden":[...], "read_only": bool}`. Required permissions:
- `tpm_sp`: `["goal.read","spec.write","evidence.read"]`, forbidden `["product.write","challenge.sign"]`
- `commander_sp`: `["product.write","build.route","evidence.read"]`, forbidden `["challenge.sign","verdict.sign"]`
- `external_challenge_sp`: `["evidence.read","challenge.sign"]`, forbidden `["product.write","goal.write"]`, read_only true
`def load_manifest(sp_id) -> dict` (unknown → `SBL_E_UNKNOWN_SP`); `def assert_permission(sp_id, action)` →
`SBLError("SBL_E_PERMISSION_DENIED")` when absent or listed in `forbidden`.
`def sign_verdict(principal_id: str, maker_principal: str, verdict: dict) -> dict` — same principal as maker →
`SBL_E_SELF_CHECK_FORBIDDEN`; caller must hold `challenge.sign`.

### sbl_sp/bridge.py  (GJ03 host bridge)
`class SkillBridge:`
- `__init__(self, manifest_path: str)`; `discover()` → `{"skill": name, "triggers": [...], "permissions": [...]}`.
- `match(intent: str) -> bool` — case-insensitive substring/regex match over manifest `triggers`.
- `effective_load(host: dict) -> dict` — returns `{"skill":..., "loaded": True, "host": host.get("name"),
  "trace_id": "L-" + sha256(...)}, requires `host["provider_on"] is True` else `SBL_E_PROVIDER_OFF`.
- `invoke(action: str, provider_on: bool) -> dict` — action not in manifest permissions → `SBL_E_PERMISSION_DENIED`;
  `provider_on` False → `SBL_E_PROVIDER_OFF`; `action` starting with `repo.` or `net.` → `SBL_E_PERMISSION_DENIED`.
- `unload()` → `{"unloaded": True, "residue": []}`.
`skills/sbl_todo/skill.json`: `{"schema":"SBL-SKILL-MANIFEST/1","name":"sbl-todo","description":"...",
"triggers":["todo","task list","待辦"],"permissions":["todo.read","todo.write"],
"forbidden":["repo.write","net.call"],"entry":"sbl_cli.sbl_todo"}`.

### sbl_cli/sbl_todo.py  (GJ01 first FUO)
Data dir: `--data-dir` > env `SBL_TODO_HOME` > `~/.sbl_todo`. State file `<data-dir>/data.json`
`{"schema":"SBL-TODO-STATE/1","items":[{"id","title","status","created"}]}`, id = `"T-" + sha256(title)[:10]`.
Commands (all print one JSON object per invocation, exit 0 on success):
- `init` → creates dir + empty state, `{"ok":true,"data_dir":...}`.
- `add --title T` → `{"ok":true,"item":{...},"status":"open"}`; empty → exit 2 `SBL_E_EMPTY_TITLE`;
  duplicate title → exit 3 `SBL_E_DUPLICATE_TITLE`; persists atomically (temp file + `os.replace`).
- `list [--json]` → `{"ok":true,"items":[...],"count":N}`; human mode prints `id<TAB>status<TAB>title`.
- `remove --id ID` → `{"ok":true,"removed":ID}`; unknown id → exit 4 `SBL_E_BAD_STATE`.
- `uninstall --yes` → deletes ONLY files it owns (`data.json` + dir); any other file present → exit 5
  `SBL_E_FOREIGN_FILES`; after success the data dir is removed and `{"ok":true,"uninstalled":true}`.
`python -m sbl_cli.sbl_todo` and `python -m sbl_cli` both work.

### tools/verify_source.py
`python tools/verify_source.py --verify` → recompute the 14 DOC sha256 from `_sbl_src_mirror/SBL_PIPD-LS-PKG`,
compare against `evidence/source/SOURCE_VERIFY.json` (aggregate + per doc), print JSON
`{"ok":bool,"docs":14,"aggregate_sha256":...,"mismatches":[...]}` and exit 0/1.

### Acceptance (Slice B)
`python -m pytest tests/test_sp_isolation.py tests/test_gj03_bridge.py tests/e2e -q` → all pass.
`python tools/verify_source.py --verify` → exit 0.

---

## Slice C — CI, packaging metadata, docs

Files: `pyproject.toml` (name `sbl-v01`, no deps, `[project.scripts] sbl-todo = "sbl_cli.sbl_todo:main"`),
`.github/workflows/ci.yml` (matrix ubuntu-latest/windows-latest, python 3.11, run `python -m pytest -q`),
`docs/ARCHITECTURE.md` (module map + one diagram in monospace), `docs/JOURNEYS.md` (GJ01/02/03 exact commands),
`README.md` (rewrite: what this is, install, the three journeys, claim ceiling `CANDIDATE_ONLY`).
Acceptance: `python -m pytest -q` green; `python -c "import pyproject_check"` skipped; YAML parses
(`python -c "import yaml,sys;yaml.safe_load(open('.github/workflows/ci.yml'))"` only if PyYAML present,
otherwise state NOT_RUN).

## Hard rules for every slice
0. Test scratch space: create temporary directories under `<repo>/.tmp-tests/` (add `.tmp-tests/` to `.gitignore`)
   and remove them in the test teardown. Do NOT use the system temp dir and do NOT write outside the repo root.

1. Never write outside `C:/Projects/Agent_Workspace/SBL`. Never read/write the source corpus trees for anything but reading.
2. No network calls, no credentials, no git write verbs (`add/commit/checkout/switch/reset/merge/rebase` are NOT allowed
   in product code; `git rev-parse` / `git ls-files` / `git status` reads ARE allowed).
3. No third-party imports in product code (`pytest` only in tests).
4. Every refusal is a typed `SBLError` with one of the codes above — never a bare `Exception` and never a silent `None`.
5. Tests must fail if the behaviour is removed (assert the exact code/JSON, not just "it raised").
