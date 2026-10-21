# R9-06: target-repository HEAD and fail-closed lifecycle admission

## Finding and exact current source

Repository: `C:/Projects/Agent_Workspace/HG-KSEOS` (read-only investigation).

`src/hg_kseos/lifecycle.py:459-463`:

```python
    @staticmethod
    def _repo_head() -> str:
        import subprocess
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""
```

1. **Wrong repository:** line 462 provides neither `cwd=` nor `git -C`; Git inherits process CWD. Calls at lines 383 and 604 therefore persist the launcher's HEAD, not the project's `target_root`. The intended target is already persisted in `intent_json` at lines 251-253 and exposed by `plan()` at lines 290-292.
2. **Silent Git failure:** line 463 turns a nonzero Git exit into `""`. `_repo_head` itself has no exception handler: it does NOT catch `InvariantViolation` or arbitrary Python exceptions. An execution failure such as missing Git still propagates.
3. **Caller swallows invariant failures:** `admit_requirement()` places HEAD resolution/workorder creation inside `try` at lines 590-605, then unconditionally suppresses `InvariantViolation` at lines 606-607 and returns claimed TaskSpec/WorkOrder IDs at lines 608-609. An empty HEAD is rejected by `SharedSpine.create_workorder()` at `src/hg_kseos/spine.py:305-306`, but that rejection is swallowed here. Simply making `_repo_head` raise `InvariantViolation` while leaving it inside this try would retain the defect. Resolve HEAD before this broad idempotency handler.

Relevant current caller (`src/hg_kseos/lifecycle.py:601-609`):

```python
            self.spine.create_workorder(
                f"WO-{ts_id}", ts_id, writer="codex",
                worktree=Path("worktrees") / ts_id.lower(),
                base_head=self._repo_head(),
            )
        except InvariantViolation:
            pass  # idempotent resume
        return {"requirement_id": requirement_id, "requirement_state": "FROZEN",
                "taskspec": ts_id, "workorder": f"WO-{ts_id}"}
```

## Minimal production patch (26-line zero-context unified diff)

No formatting-only changes. This diff uses `-U0` to keep the complete production patch under 30 lines; apply with `git apply --unidiff-zero <patch-file>`. The regression test is supplied separately below, not counted in the production diff.

```diff
--- a/src/hg_kseos/lifecycle.py
+++ b/src/hg_kseos/lifecycle.py
@@ -383 +383 @@
-                base_head=self._repo_head(),
+                base_head=self._repo_head(project_id),
@@ -459,2 +459 @@
-    @staticmethod
-    def _repo_head() -> str:
+    def _repo_head(self, project_id: str) -> str:
@@ -462,2 +461,9 @@
-        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
-        return r.stdout.strip() if r.returncode == 0 else ""
+        with self.spine.connect() as conn:
+            row = conn.execute("SELECT intent_json FROM project_lifecycles WHERE project_id=?", (project_id,)).fetchone()
+        target = json.loads(row[0]).get("target_root", "")
+        if not target:
+            raise InvariantViolation("ERR_REPO_HEAD_TARGET_REQUIRED")
+        r = subprocess.run(["git", "-C", target, "rev-parse", "HEAD"], capture_output=True, text=True)
+        if r.returncode != 0:
+            raise InvariantViolation(f"ERR_REPO_HEAD:{target}:{r.stderr.strip()}")
+        return r.stdout.strip()
@@ -589,0 +596 @@
+        base_head = self._repo_head(project_id)
@@ -604 +611 @@
-                base_head=self._repo_head(),
+                base_head=base_head,
```

## Ready-to-land pytest test

Add the following as `tests/test_r9_06_repo_head.py`. These two test functions expand to six cases: both public admission paths with distinct real Git repositories, and both paths with a missing target or an existing non-repository target. No mocked Git output, fabricated hashes, or signature changes are needed in the tests. All commits are actually created by Git in isolated test directories.

```python
import subprocess

import pytest

from hg_kseos.errors import InvariantViolation
from hg_kseos.lifecycle import ProjectLifecycleController, ProjectRequest
from hg_kseos.spine import SharedSpine


def _git(path, *args):
    return subprocess.run(
        ["git", "-C", str(path), *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def _repo(path, message):
    path.mkdir()
    _git(path, "init", "-q")
    _git(path, "-c", "user.name=Regression", "-c",
         "user.email=regression@example.invalid", "-c", "commit.gpgsign=false",
         "commit", "--allow-empty", "-qm", message)
    return _git(path, "rev-parse", "HEAD")


def _controller(tmp_path, target):
    spine = SharedSpine(tmp_path / "spine.db")
    spine.initialize()
    lc = ProjectLifecycleController(spine)
    request = ProjectRequest(goal="Package", target_root=str(target))
    lc.start(request, project_id="R9-06")
    lc.intake("R9-06", request)
    for state in ("INTENT_BOUND", "REQUIREMENTS_READY", "DESIGN_READY"):
        lc.transition("R9-06", state, trigger="TEST")
    lc.plan("R9-06")
    return lc


def _admit(lc, entrypoint):
    if entrypoint == "admit_workorders":
        return lc.admit_workorders("R9-06")
    return lc.admit_requirement("R9-06", "REQ-R9-06-LATE", "Late obligation")


@pytest.mark.parametrize("entrypoint", ["admit_workorders", "admit_requirement"])
def test_repo_head_uses_target_not_process_cwd(tmp_path, monkeypatch, entrypoint):
    cwd = tmp_path / "launcher"
    launcher_head = _repo(cwd, "launcher")
    target = tmp_path / "target"
    target_head = _repo(target, "target")
    assert launcher_head != target_head
    monkeypatch.chdir(cwd)
    assert cwd.resolve() != target.resolve()
    lc = _controller(tmp_path, target)

    _admit(lc, entrypoint)

    with lc.spine.connect() as conn:
        heads = [row[0] for row in conn.execute("SELECT base_head FROM workorders")]
    assert heads
    assert set(heads) == {target_head}


@pytest.mark.parametrize("entrypoint", ["admit_workorders", "admit_requirement"])
@pytest.mark.parametrize("invalid_target", ["missing", "non_repo"])
def test_repo_head_invalid_target_propagates_invariant(
    tmp_path, monkeypatch, entrypoint, invalid_target,
):
    cwd = tmp_path / "launcher"
    _repo(cwd, "launcher")
    monkeypatch.chdir(cwd)
    target = tmp_path / invalid_target
    if invalid_target == "non_repo":
        target.mkdir()
    lc = _controller(tmp_path, target)

    with pytest.raises(InvariantViolation, match="ERR_REPO_HEAD"):
        _admit(lc, entrypoint)

    with lc.spine.connect() as conn:
        assert conn.execute("SELECT COUNT(*) FROM workorders").fetchone()[0] == 0
```

## Verification

Executed the six focused regression cases against the current source: **6 failed** (two wrong-HEAD assertions; four missing expected `InvariantViolation` failures). Executed the identical tests after applying the exact 26-line diff to the module **in memory only**: **6 passed**. Exit codes were `[1, 0]`. The production source SHA-256 was identical before and after both runs: `a172e16ccca5924e35fdbaa132802a6b0cbb0f389b2db3aecda14b150f609e86`.

The repository has not been patched and no test file was added there. Bytecode and pytest caches were disabled; fixture directories were temporary and cleaned up. The first harness command had a Python string-escaping error and was corrected before the successful RED/GREEN run. Its inherited `TMPDIR` resolved to the Windows system temp directory rather than the documented Hermes scratch directory; the repeatable runner below therefore pins Hermes scratch explicitly.

The final repeatable runner passed `git apply --check --unidiff-zero` without applying the diff and repeated **6 failed in 4.52s -> 6 passed in 4.23s**, with fixtures explicitly under Hermes scratch. On Windows, feeding the LF patch to Git as UTF-8 bytes is required here: `subprocess.run(..., text=True, input=diff)` translated stdin to CRLF and caused a false apply-check failure; the runner avoids that translation.

Full-suite execution is outside this focused verification; no claim of full-suite compatibility is made. In particular, the invalid legacy target fixtures noted below must be updated deliberately.

### Reproducible read-only runner

Run from the repository root with the supplied venv and `PYTHONPATH=.../src`; set `PYTHONDONTWRITEBYTECODE=1`. Extract this `verification-runner` block and execute it with the report path as its first argument. It uses Git's own read-only `apply --check`, then runs RED and GREEN in separate child processes. All source modifications are in memory.

```verification-runner
import hashlib
import linecache
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import types

import pytest
import hg_kseos.lifecycle as lifecycle

report = Path(sys.argv[1]).resolve()
text = report.read_text(encoding="utf-8")
runner = text.split("```verification-runner\n", 1)[1].split("\n```", 1)[0]
if len(sys.argv) == 2:
    diff = text.split("```diff\n", 1)[1].split("```", 1)[0]
    assert len(diff.splitlines()) == 26
    subprocess.run(
        ["git", "apply", "--check", "--unidiff-zero", "-"],
        input=diff.encode("utf-8"), check=True,
    )
    results = [subprocess.run(
        [sys.executable, "-c", runner, str(report), mode],
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    ).returncode for mode in ("RED", "GREEN")]
    print("RED_GREEN_EXIT_CODES", results)
    assert results == [1, 0], results
    sys.exit(0)

source_path = Path(lifecycle.__file__)
original = source_path.read_bytes()
if sys.argv[2] == "GREEN":
    diff = text.split("```diff\n", 1)[1].split("```", 1)[0]
    lines = original.decode("utf-8").splitlines(keepends=True)
    patch_lines = diff.splitlines(keepends=True)
    out, cursor, index = [], 0, 2
    while index < len(patch_lines):
        match = re.match(r"@@ -([0-9]+)(?:,([0-9]+))? [+]([0-9]+)(?:,([0-9]+))? @@", patch_lines[index])
        assert match, patch_lines[index]
        start, count = int(match[1]), int(match[2] or 1)
        offset = start - 1 if count else start
        out.extend(lines[cursor:offset])
        cursor, index = offset, index + 1
        while index < len(patch_lines) and not patch_lines[index].startswith("@@"):
            line = patch_lines[index]
            if line.startswith("-"):
                assert lines[cursor].rstrip("\r\n") == line[1:].rstrip("\r\n")
                cursor += 1
            elif line.startswith("+"):
                out.append(line[1:])
            else:
                raise AssertionError(line)
            index += 1
    out.extend(lines[cursor:])
    exec(compile("".join(out), str(source_path), "exec"), lifecycle.__dict__)

test = text.split("```python\n")[-1].split("```", 1)[0]
virtual_path = str(report.parent / "test_r9_06_repo_head.py")
linecache.cache[virtual_path] = (len(test), None, test.splitlines(True), virtual_path)

class MemoryModule(pytest.Module):
    def _getobj(self):
        module = types.ModuleType("test_r9_06_repo_head")
        module.__file__ = virtual_path
        sys.modules[module.__name__] = module
        exec(compile(test, virtual_path, "exec"), module.__dict__)
        return module

class Collector:
    def pytest_collect_file(self, file_path, parent):
        if file_path == report:
            return MemoryModule.from_parent(parent, path=file_path)

scratch = Path("C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/cache/scratch")
scratch.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="r9-06-", dir=scratch) as temp:
    print("MODE", sys.argv[2], flush=True)
    code = pytest.main([
        str(report), "-q", "--tb=short", "-p", "no:cacheprovider",
        "--basetemp", str(Path(temp) / "fixtures"),
    ], plugins=[Collector()])
assert source_path.read_bytes() == original
print("SOURCE_SHA256", hashlib.sha256(original).hexdigest(), "UNCHANGED", flush=True)
sys.exit(code)
```

## Scope notes

- The patch intentionally rejects empty/missing/non-Git targets instead of falling back to CWD. Existing tests/consumers using `target_root="worktrees"` without a Git repository must supply a valid target; preserving their accidental CWD fallback would preserve R9-06.
- This is not an admission-transaction redesign: requirement registration/freezing can precede a HEAD-resolution failure. The negative tests require exception propagation and no workorder creation, not rollback of earlier requirement rows.
- `checkpoint()` overwrites `intent_json` with a checkpoint sidecar at lines 415-418, potentially discarding `target_root`. That separate issue now fails closed rather than selecting CWD silently; preserving intent across checkpoints is outside this minimal patch.
- Existing unrelated repository modifications were present at intake and were not modified.
