# Slice B2 (bounded) — `sbl-todo` CLI (GJ01), source verifier, brownfield patch (GJ02), rollback

Root: `C:/Projects/Agent_Workspace/SBL` only. Python 3.11 stdlib only (tests may use pytest).
Existing: `sbl_core/` (SBLError, dto, m04_bridge.bind_repo_context/GovernedBuildBridge), `sbl_sp/`.
Do not modify `sbl_core/` or `sbl_sp/`. Import them.

## 1. `sbl_cli/__init__.py`
`from .sbl_todo import main` (empty otherwise).

## 2. `sbl_cli/sbl_todo.py`
Module-level `main(argv: list[str] | None = None) -> int`.

Data dir resolution (in order): `--data-dir PATH` (global option accepted BEFORE the subcommand),
env `SBL_TODO_HOME`, else `Path.home() / ".sbl_todo"`. State file: `<data_dir>/data.json`
`{"schema":"SBL-TODO-STATE/1","items":[{"id","title","status","created"}]}`. `id = "T-" + sha256(title)[:10]`.

Subcommands (every invocation prints exactly ONE JSON object on stdout; errors print `SBLError.as_dict()`):
| command | success output | failures (exit code / code) |
|---|---|---|
| `init` | `{"ok":true,"data_dir":"<abs>"}` | 0 |
| `add --title T` | `{"ok":true,"item":{...},"status":"open"}` | 2 `SBL_E_EMPTY_TITLE` / 3 `SBL_E_DUPLICATE_TITLE` |
| `list [--json]` | `{"ok":true,"items":[...],"count":N}` (`--json` and default both emit JSON; without `--json` also print `id<TAB>status<TAB>title` lines to stderr, human channel) | 0 |
| `remove --id ID` | `{"ok":true,"removed":"ID"}` | 4 `SBL_E_BAD_STATE` (unknown id) |
| `uninstall --yes` | `{"ok":true,"uninstalled":true}` | 5 `SBL_E_FOREIGN_FILES` (any file other than `data.json` present in data dir) |

Rules: writes are atomic (write `<data.json>.tmp` then `os.replace`); `add` creates the data dir if missing;
`uninstall` without `--yes` prints `{"ok":false,"code":"SBL_E_BAD_STATE",...}` exit 4 (confirmation required) and
deletes nothing; after a successful uninstall `<data_dir>` no longer exists. Unknown subcommand → exit 2 with
`SBL_E_BAD_STATE`. Exit codes are returned from `main`, and `if __name__ == "__main__": raise SystemExit(main())`.

## 3. `sbl_cli/__main__.py`
`from .sbl_todo import main; raise SystemExit(main())` so `python -m sbl_cli` works.

## 4. `tools/verify_source.py`
`python tools/verify_source.py --verify` → read `evidence/source/SOURCE_VERIFY.json`, recompute sha256 of the 14
files listed in its `docs[]` (paths are absolute under `_sbl_src_mirror`; if a listed path is missing, fall back to
`r"C:/Projects/Agent_Workspace/_sbl_src_mirror/SBL_PIPD-LS-PKG/" + "<DOC-xx>.md"`), recompute the aggregate as
`sha256("\n".join(sorted(doc_sha)) + "\n")`, compare with the recorded `aggregate_sha256` and each per-doc digest.
Print `{"ok":bool,"docs":14,"aggregate_sha256":...,"recorded_aggregate":...,"mismatches":[...]}`; exit 0 iff ok.
`--json-out PATH` optional.

## 5. `tests/e2e/__init__.py` (empty)

## 6. `tests/e2e/test_gj01_cli.py`  — GJ01 golden journey
Helper `run(args)` = `subprocess.run([sys.executable, "-m", "sbl_cli.sbl_todo", *args], cwd=REPO, capture_output=True, text=True)`
plus `json.loads(stdout)`.
Cases (each a separate test):
1. `init` then `add --title "unique-<uuid>"` → `ok`, item id starts `T-`, status `open`.
2. `list --json` in a SEPARATE process → same id, title, status (this is the restart readback).
3. `add` duplicate title → exit 3, code `SBL_E_DUPLICATE_TITLE`.
4. `add --title "   "` → exit 2, code `SBL_E_EMPTY_TITLE`.
5. `remove --id <real>` → ok, then `list` count decremented; `remove --id T-nope` → exit 4.
6. `uninstall --yes` → ok, data dir gone (assert `not path.exists()`), then `list` still works and returns count 0.
7. `uninstall --yes` with a foreign file written into the data dir → exit 5 `SBL_E_FOREIGN_FILES` and the dir still exists.
Data dirs: `<repo>/.pytest_tmp/gj01/<case>/` (create/remove in fixtures).

## 7. `tests/e2e/test_gj02_patch.py` — GJ02 brownfield scoped patch
Fixture: create `<repo>/.pytest_tmp/gj02/` , `git init -q`, write `calc.py` (`def add(a,b): return a-b`) and
`tests_local.py` (`assert add(2,3)==5` run via `python -m pytest tests_local.py`? simpler: a `run_tests()` that
executes `python -c "import calc; assert calc.add(2,3)==5"`), `git add -A && git commit -qm baseline`.
(Git WRITE verbs are permitted ONLY inside this temp fixture; never against the SBL repo.)
Cases:
1. `bind_repo_context(root)` returns the 40-char HEAD and `dirty is False`.
2. `GovernedBuildBridge().prepare(ctx, WriteSet(["calc.py"]))` → order id starts `O-`.
3. RED: the baseline check fails (`add(2,3) != 5`).
4. `apply(order, "calc.py", fixed_source)` → GREEN: the check passes.
5. NEGATIVE: `apply(order, "other.py", "x=1")` → `SBL_E_WRITE_OUTSIDE_WRITESET` and `other.py` does not exist.
6. NEGATIVE: make a new commit in the fixture repo after prepare, then `apply(...)` → `SBL_E_STALE_HEAD`.
7. ROLLBACK: `git -C <root> checkout -- calc.py` restores the baseline bytes; assert the RED check fails again and
   `git rev-parse HEAD` equals the baseline head recorded before the patch.

## 8. `tests/e2e/test_rollback.py`
1. CLI uninstall rollback: after `uninstall --yes` a re-`init` + `list` works and reports 0 items.
2. Patch rollback leaves no residue: after the GJ02 rollback the fixture repo `git status --porcelain` is empty.
3. `SBLError.as_dict()` is JSON-serialisable for a refused call (ceiling refused) and carries `code`.
4. A refused CLI call must not create/modify `data.json` (digest before == after).

## Acceptance command
`python -m pytest tests/e2e -q` → all pass; and `python tools/verify_source.py --verify` → exit 0.
Interpreter `C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe`.
No network. No writes outside the repo root. No git write verbs against the SBL repo itself.
