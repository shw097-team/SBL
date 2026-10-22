# EXECUTE brief — bounded repair: `sbl-stack doctor` must refuse a tampered manifest with a typed code

You are the bounded writer. You may edit **only** these two product files:
- `sbl_stack/__init__.py` (the `doctor()` function and, if needed, one small helper next to it)
- `tests/test_stack_verbs.py` (add one regression test; do not delete or weaken existing tests)

Do not touch anything else in the tree, do not commit, do not dispatch or spawn anything.

## The measured defect (reproduce it first, do not take my word)

Fresh install, then rename a component in the installed manifest to a name that does not exist, then run doctor:

```bash
T="C:/Users/user/AppData/Local/Temp/repair_doctor"
rm -rf "$T" && mkdir -p "$T"
python -m sbl_stack.cli install --root "$T/root"          # rc 0
python - "$T" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1])/"root"/"stack.json"
d=json.loads(p.read_text(encoding="utf-8")); d["components"][0]="TAMPERED_COMPONENT"
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
PY
python -m sbl_stack.cli doctor --root "$T/root"; echo "rc=$?"
```

Observed: `ModuleNotFoundError: No module named '0'` with a raw traceback, exit 1. Expected: a typed refusal
`{"ok": false, "code": "SBL_E_COMPONENT_UNRESOLVED", ...}` and exit 2, like every other refusal in this CLI
(`invoke --mode NOT_A_CANONICAL_MODE` already does exactly that with `SBL_E_PROHIBITED_KIND`, rc=2).

## The fix, in this shape

1. In `doctor()`, wrap each component's resolution/import in `try/except Exception as exc:` and append a
   problem string that names the component and the exception type — never let the exception escape.
   `ok` must become `False` and the returned payload must carry a typed `code`
   (`SBL_E_COMPONENT_UNRESOLVED`) plus the `problems` list it already has.
2. Do not swallow a *real* doctor failure: a component that resolves but fails its digest check must still
   produce the digest problem it produces today. Only the *resolution* path changes.
3. Add one test to `tests/test_stack_verbs.py` named
   `test_doctor_refuses_a_manifest_naming_a_nonexistent_component` that asserts: rc == 2 via the CLI's
   `main()` return (or the function's `ok is False` + `code == "SBL_E_COMPONENT_UNRESOLVED"`), the message
   names the bad component, and no exception propagates.

## Prove it

```bash
# RED before your fix / GREEN after — record both if you can reproduce RED first
python -m pytest -q -p no:cacheprovider tests/test_stack_verbs.py
python -m pytest -q -p no:cacheprovider tests            # full suite must stay green (227 passed / 4 skipped baseline)
python -m sbl_stack.cli doctor --root <healthy install>  # still rc 0 on an untouched install
```

Write `workers/q5_repair/REPAIR.json` with:
`{"defect": "...", "red": {"cmd": "...", "rc": 1, "observed": "ModuleNotFoundError..."},
  "fix_files": ["sbl_stack/__init__.py", "tests/test_stack_verbs.py"], "green": {"cmd": "...", "rc": 0, "passed": N},
  "regression": {"cmd": "pytest -q", "rc": 0, "passed": N, "skipped": 4},
  "healthy_install_still_ok": true, "scope": "no other file touched"}`

## Rules

- Minimal change. If the fix requires restructuring the module, stop and write the blocker instead.
- Numbers in REPAIR.json must come from commands you ran this turn.
- Final message: the RED rc/observed line, the GREEN counts, and the two file paths you changed.
