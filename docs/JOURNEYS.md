# SBL v0.1 journeys

Claim ceiling: **`CANDIDATE_ONLY`**. Every command below was executed from the
repository root while this document was written; the output under each command
is the output that run produced. Timestamps, ids and HEAD shas differ between
machines, so compare shape and exit codes, not literal values.

The `exit N` lines are annotations of the process exit code, not stdout; the
CLI writes exactly one JSON object to stdout per invocation.

Shell notes, because they change the commands:

- Commands are written for the **PowerShell** prompt used on this host; GJ02
  uses a PowerShell here-string piped into `python -`. The same body also ran
  through `bash -lc "python - <<'PY' ... PY"` with the same results.
- `python` here resolves to the interpreter on `PATH`. On this host that is a
  3.11 runtime; a different interpreter that has `pytest` installed is
  C:/Projects/Agent_Workspace/HG-KSEOS/.venv/Scripts/python.exe. The five-file
  Slice C tree does not pin an interpreter.
- `--data-dir` is a **global** option: it must come before the subcommand. The
  observed refusal for the other order is shown in GJ01's negative case.
- `python -m sbl_cli.sbl_todo` prints a `RuntimeWarning` about the module
  already being imported by `sbl_cli/__init__.py`. It is harmless and appears
  on every invocation; it is omitted from the transcripts below.
- `--help` is not a supported flag. It is treated as an unknown subcommand and
  refused with exit code 2; use the subcommand list in the JSON refusal instead.

## GJ01 — `sbl-todo` local tool lifecycle

Fresh state, add one item, read it back in a separate process, then uninstall.

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo init
```

```text
{"ok": true, "data_dir": "C:\\Projects\\Agent_Workspace\\SBL\\.demo"}
exit 0
```

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo add --title "buy milk"
```

```text
{"ok": true, "item": {"id": "T-933260194c", "title": "buy milk", "status": "open", "created": "2026-10-20T06:05:28Z"}, "status": "open"}
exit 0
```

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo list --json
```

```text
{"ok": true, "items": [{"id": "T-933260194c", "title": "buy milk", "status": "open", "created": "2026-10-20T06:05:28Z"}], "count": 1}
exit 0
```

Separate-process readback (a new process, same data dir, same id):

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo list --json
```

```text
{"ok": true, "items": [{"id": "T-933260194c", "title": "buy milk", "status": "open", "created": "2026-10-20T06:05:28Z"}], "count": 1}
exit 0
```

Negative case — the same title again is refused with exit code 3:

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo add --title "buy milk"
```

```text
{"ok": false, "code": "SBL_E_DUPLICATE_TITLE", "message": "an item with this title already exists", "detail": {"id": "T-933260194c", "title": "buy milk"}}
exit 3
```

Negative case — a blank title is refused with exit code 2. The state file is
not rewritten (covered by `tests/e2e/test_rollback.py`).

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo add --title "   "
```

```text
{"ok": false, "code": "SBL_E_EMPTY_TITLE", "message": "title must not be empty", "detail": {"title": "   "}}
exit 2
```

Negative case — the global option after the subcommand is refused:

```powershell
python -m sbl_cli.sbl_todo init --data-dir ./.demo
```

```text
{"ok": false, "code": "SBL_E_BAD_STATE", "message": "unexpected argument '--data-dir'", "detail": {"args": ["--data-dir", "./.demo"]}}
exit 4
```

Uninstall, then prove no residue remains:

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo uninstall --yes
```

```text
{"ok": true, "uninstalled": true}
exit 0
```

```powershell
if (Test-Path -LiteralPath .demo) { "RESIDUE_PRESENT" } else { "NO_RESIDUE" }
```

```text
NO_RESIDUE
```

Negative case — `uninstall` refuses to delete a directory that holds a file it
does not own (exit code 5), and the state file survives:

```powershell
python -m sbl_cli.sbl_todo --data-dir ./.demo-foreign add --title "keep"
Set-Content -LiteralPath ./.demo-foreign/stranger.txt -Value "keep me`n" -NoNewline
python -m sbl_cli.sbl_todo --data-dir ./.demo-foreign uninstall --yes
```

```text
{"ok": true, "item": {"id": "T-6ca7ea2fee", "title": "keep", "status": "open", "created": "2026-10-20T06:04:04Z"}, "status": "open"}
{"ok": false, "code": "SBL_E_FOREIGN_FILES", "message": "data dir contains files that sbl-todo does not own", "detail": {"data_dir": "C:\\Projects\\Agent_Workspace\\SBL\\.demo-foreign", "files": ["stranger.txt"]}}
exit 5
```

Remove the leftover fixture directory with the same interpreter that created
it, since `rmdir` inside the CLI only removes empty or owned directories:

```powershell
python -c "import pathlib,shutil;shutil.rmtree('.demo-foreign',ignore_errors=True);print(pathlib.Path('.demo-foreign').exists())"
```

```text
False
```

## GJ02 — brownfield patch: bind, prepare, apply, red→green, refusals, rollback

This is a short script rather than a sequence of one-liners because the fixture
has to be a committed git repository. It creates `.tmp-docs/gj02` **inside the
repo root**, and the only git write verbs (`init`, `add`, `commit`,
`checkout --`) run inside that fixture, never against this repository.

```powershell
@'
import os, shutil, stat, subprocess, sys
from pathlib import Path
from sbl_core.dto import WriteSet
from sbl_core.errors import SBLError
from sbl_core.m04_bridge import GovernedBuildBridge, bind_repo_context

ROOT = Path('.tmp-docs/gj02').resolve()
BASELINE = 'def add(a, b):\n    return a - b\n'
FIXED = 'def add(a, b):\n    return a + b\n'

def purge(path):
    if not path.exists():
        return
    for base, _dirs, files in os.walk(path):
        for name in files:
            try:
                os.chmod(os.path.join(base, name), stat.S_IWRITE)
            except OSError:
                pass
    shutil.rmtree(path, ignore_errors=True)

def git(*args):
    done = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    return done.stdout.strip()

def red_green():
    done = subprocess.run([sys.executable, '-B', '-c', 'import calc; assert calc.add(2, 3) == 5'],
        cwd=ROOT, capture_output=True, text=True,
        env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    return 'green' if done.returncode == 0 else 'red'

purge(ROOT)
ROOT.mkdir(parents=True)
git('init', '-q')
git('config', 'user.email', 'mode.agent@example.com')
git('config', 'user.name', 'Mode Agent')
git('config', 'core.autocrlf', 'false')
(ROOT / 'calc.py').write_text(BASELINE, encoding='utf-8', newline='\n')
git('add', '-A'); git('commit', '-qm', 'baseline')
print('1 baseline:', red_green())
ctx = bind_repo_context(str(ROOT))
order = GovernedBuildBridge().prepare(ctx, WriteSet(['calc.py']))
print('2 order:', order.order_id, 'head', ctx.head[:12], 'dirty', ctx.dirty)
GovernedBuildBridge().apply(order, 'calc.py', FIXED)
print('3 after apply:', red_green(), '| bytes match FIXED:', (ROOT / 'calc.py').read_text(encoding='utf-8') == FIXED)
try:
    GovernedBuildBridge().apply(order, 'other.py', 'x = 1\n')
except SBLError as exc:
    print('4 out-of-writeset:', exc.code, '| other.py exists:', (ROOT / 'other.py').exists())
(ROOT / 'notes.txt').write_text('later work\n', encoding='utf-8')
git('add', 'notes.txt'); git('commit', '-qm', 'later')
try:
    GovernedBuildBridge().apply(order, 'calc.py', BASELINE)
except SBLError as exc:
    print('5 stale head:', exc.code)
git('checkout', '--', 'calc.py')
print('6 rollback:', red_green(), '| bytes restored:', (ROOT / 'calc.py').read_text(encoding='utf-8') == BASELINE, '| porcelain:', repr(git('status', '--porcelain')))
print('7 head:', git('rev-parse', 'HEAD')[:12])
'@ | python -
```

Observed output:

```text
1 baseline: red
2 order: O-d557666aa2e8 head 0a17e398d4bc dirty False
3 after apply: green | bytes match FIXED: True
4 out-of-writeset: SBL_E_WRITE_OUTSIDE_WRITESET | other.py exists: False
5 stale head: SBL_E_STALE_HEAD
6 rollback: red | bytes restored: True | porcelain: ''
7 head: 4cd05a0a2f84
exit 0
```

What the lines mean:

1. The baseline fails the check (`red`).
2. `prepare` issues a deterministic order id binding the current `HEAD`.
3. `apply` inside the writeset turns the check `green`, byte for byte.
4. Writing `other.py`, which no prefix in the writeset covers, is refused and
   nothing is created.
5. After a second commit moves `HEAD`, the old order is refused as stale.
6. `git checkout -- calc.py` restores the baseline bytes, the check is `red`
   again, and the working tree is clean.
7. Rollback did not move `HEAD`; it only restored the file.

Clean up the fixture (remove read-only git objects before the tree):

```powershell
python -c "import os,shutil,stat,pathlib;p=pathlib.Path('.tmp-docs/gj02');[os.chmod(os.path.join(b,n),stat.S_IWRITE) for b,d,f in os.walk(p) for n in f];shutil.rmtree(p,ignore_errors=True);pathlib.Path('.tmp-docs').rmdir() if not any(pathlib.Path('.tmp-docs').iterdir()) else None;print(pathlib.Path('.tmp-docs').exists())"
```

```text
False
```

## GJ03 — skill discovery, match, effective load, unload

Load `skills/sbl_todo/skill.json` through `sbl_sp.bridge.SkillBridge` and show
the positive and negative match, the `provider_on=False` refusal, and an
unload with no residue.

```powershell
python -c "from sbl_sp.bridge import SkillBridge; b=SkillBridge('skills/sbl_todo/skill.json'); print('discover:', b.discover()); print('match todo:', b.match('add a TODO for the review')); print('match unrelated:', b.match('deploy the release'))"
```

```text
discover: {'schema': 'SBL-SKILL-DISCOVER/1', 'skill': 'sbl-todo', 'triggers': ['todo', 'task list', '待辦'], 'permissions': ['todo.read', 'todo.write']}
match todo: True
match unrelated: False
exit 0
```

```powershell
python -c "from sbl_sp.bridge import SkillBridge; from sbl_core.errors import SBLError; b=SkillBridge('skills/sbl_todo/skill.json'); print('load:', b.effective_load({'name':'codex','provider_on':True}))
try:
    b.effective_load({'name':'codex','provider_on':False})
except SBLError as e:
    print('refused:', e.code, e.as_dict())
print('unload:', b.unload())"
```

```text
load: {'schema': 'SBL-SKILL-LOAD/1', 'skill': 'sbl-todo', 'loaded': True, 'host': 'codex', 'trace_id': 'L-7f9eb405f7af'}
refused: SBL_E_PROVIDER_OFF {'ok': False, 'code': 'SBL_E_PROVIDER_OFF', 'message': 'skill may not load while the host provider is off', 'detail': {'skill': 'sbl-todo'}}
unload: {'schema': 'SBL-SKILL-UNLOAD/1', 'unloaded': True, 'residue': []}
exit 0
```

Negative case — the manifest's forbidden and unknown actions are refused:

```powershell
python -c "from sbl_sp.bridge import SkillBridge; from sbl_core.errors import SBLError; b=SkillBridge('skills/sbl_todo/skill.json')
for action in ('repo.write','net.call','todo.delete'):
    try:
        b.invoke(action, provider_on=True)
    except SBLError as e:
        print(action, '->', e.code)
print('permitted ->', b.invoke('todo.write', provider_on=True))"
```

```text
repo.write -> SBL_E_PERMISSION_DENIED
net.call -> SBL_E_PERMISSION_DENIED
todo.delete -> SBL_E_PERMISSION_DENIED
permitted -> {'ok': True, 'skill': 'sbl-todo', 'action': 'todo.write'}
```

The `trace_id` is derived from skill name plus host name, so it is stable for a
given pair; `residue: []` means unload released everything it loaded.
