"""C17: a real lifecycle for three kinds -- CLI_TOOL, AGENT_SKILL, SIMPLE_AGENT.

These tests drive the code that ships in this tree, not a copy beside it:
``sbl_core/m03_routing.py`` (routing and dispositions), ``sbl_core/m04_bridge.py`` (the governed
build bridge) and ``sbl_sp/bridge.py`` (the skill bridge). Each test names the kind and the verb it
exercises, and every assertion is read off that source.

Two product facts are asserted as they are, not as one might wish them to be; both are recorded in
``workers/execute_r153/EXECUTE_RECEIPT_C17.json`` under ``deviations``:

* ``SkillBridge.unload()`` keeps no load ledger, so "unload before load" is not a refusal: it
  returns the documented unload shape. ``SBL_E_NOT_LOADED`` is not in the error vocabulary either.
* ``sbl_sp/manifests/*.json`` declare no ``triggers``, so a bridge bound to one of them can never
  ``match``. The AGENT_SKILL positive path therefore uses ``skills/sbl_todo/skill.json``, the real
  manifest that declares triggers and permissions.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from sbl_core.dto import SpecAtom, WriteSet, atom_id_for, order_id_for  # noqa: E402
from sbl_core.errors import SBLError  # noqa: E402
from sbl_core.m03_routing import GovernedRouting  # noqa: E402
from sbl_core.m04_bridge import GovernedBuildBridge, bind_repo_context  # noqa: E402
from sbl_sp.bridge import SkillBridge  # noqa: E402

#: The real manifest that declares triggers *and* permissions.
SKILL_MANIFEST = REPO_ROOT / "skills" / "sbl_todo" / "skill.json"

#: A hostile inherited environment must not be able to break the fixture, otherwise a red result
#: says nothing about the product. Mirrors the guard in ``tests/e2e/test_gj02_patch.py``.
GIT_ENV = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
GIT_ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_TERMINAL_PROMPT": "0"})


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        text=True,
        check=False,
        env=dict(GIT_ENV),
    )
    assert completed.returncode == 0, completed.stderr
    return completed.stdout.strip()


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A throwaway git repo with a resolvable HEAD, built without ``git commit``.

    ``bind_repo_context`` requires ``git rev-parse HEAD`` to yield 40 hex characters, so an unborn
    branch is not enough. A commit object is created with ``commit-tree`` over the empty tree and
    HEAD is pointed at it with ``update-ref``; no work-tree commit is ever made.
    """

    root = tmp_path / "repo"
    root.mkdir(parents=True, exist_ok=True)
    try:
        _git(root, "init", "-q")
        _git(root, "config", "user.email", "c17.agent@example.com")
        _git(root, "config", "user.name", "C17 Agent")
        _git(root, "config", "core.autocrlf", "false")
    except AssertionError as exc:  # pragma: no cover - depends on the host, not the code
        pytest.skip(f"ENV: git cannot create a repository in this sandbox: {exc}")
    # ``mktree`` reads the listing from stdin; feeding it an empty listing yields the empty tree.
    empty_tree = subprocess.run(
        ["git", "-C", str(root), "mktree"],
        capture_output=True,
        text=True,
        input="",
        check=False,
        env=dict(GIT_ENV),
    )
    if empty_tree.returncode != 0:  # pragma: no cover - depends on the host, not the code
        pytest.skip(f"ENV: git cannot build an empty tree here: {empty_tree.stderr}")
    tree = empty_tree.stdout.strip()
    identity = {
        "GIT_AUTHOR_NAME": "C17 Agent",
        "GIT_AUTHOR_EMAIL": "c17.agent@example.com",
        "GIT_COMMITTER_NAME": "C17 Agent",
        "GIT_COMMITTER_EMAIL": "c17.agent@example.com",
    }
    made = subprocess.run(
        ["git", "-C", str(root), "commit-tree", tree, "-m", "baseline"],
        capture_output=True,
        text=True,
        check=False,
        env={**GIT_ENV, **identity},
    )
    if made.returncode != 0:  # pragma: no cover - depends on the host, not the code
        pytest.skip(f"ENV: git cannot create a commit object here: {made.stderr}")
    _git(root, "update-ref", "HEAD", made.stdout.strip())
    return root


@pytest.fixture()
def atom() -> SpecAtom:
    return SpecAtom(atom_id_for("c17"), "c17", "docs/c17.md#L1")


# --------------------------------------------------------------------- CLI_TOOL


def test_c17_cli_tool_apply_writes_inside_writeset_and_returns_digest(repo: Path) -> None:
    """CLI_TOOL, positive: bind_repo_context -> prepare -> apply writes the file and returns a digest."""

    ctx = bind_repo_context(str(repo))
    assert len(ctx.head) == 40
    assert all(ch in "0123456789abcdef" for ch in ctx.head)
    assert ctx.dirty is False
    assert os.path.normcase(os.path.realpath(ctx.root)) == os.path.normcase(str(repo.resolve()))

    bridge = GovernedBuildBridge()
    writeset = WriteSet(["src"])
    order = bridge.prepare(ctx, writeset)

    # prepare() derives the order id from HEAD and the sorted writeset paths (sbl_core/dto.py).
    assert order.order_id == order_id_for(ctx.head, writeset)
    assert order.order_id.startswith("O-")
    assert len(order.order_id) == 2 + 12
    assert order.head == ctx.head
    assert order.writeset.paths == ("src",)

    content = "def add(a, b):\n    return a + b\n"
    applied = bridge.apply(order, "src/tool.py", content)

    written = repo / "src" / "tool.py"
    assert written.is_file()
    # apply() opens with newline="\\n", so the bytes on disk are the bytes handed in.
    assert written.read_bytes() == content.encode("utf-8")

    # The returned order carries a digest: the same order id, which is "O-" + 12 hex characters,
    # and the effective writeset now also names the file that was actually written.
    assert applied.order_id == order.order_id
    assert applied.order_id[2:] == order_id_for(ctx.head, writeset)[2:]
    assert all(ch in "0123456789abcdef" for ch in applied.order_id[2:])
    assert applied.writeset.paths == ("src", "src/tool.py")
    assert applied.head == ctx.head


def test_c17_cli_tool_writeset_outside_repo_prefix_is_refused(
    repo: Path, tmp_path: Path
) -> None:
    """CLI_TOOL, negative: a writeset naming a path outside the repo is refused and nothing is written."""

    ctx = bind_repo_context(str(repo))
    bridge = GovernedBuildBridge()
    outside = tmp_path / "outside"
    outside.mkdir()

    # prepare() does NOT validate prefixes; the refusal is raised by apply() before anything is
    # opened. Both the traversal route and the not-under-prefix route must be refused.
    traversal = bridge.prepare(ctx, WriteSet(["../outside"]))
    with pytest.raises(SBLError) as caught:
        bridge.apply(traversal, "../outside/evil.py", "pwned\n")
    assert caught.value.code == "SBL_E_WRITE_OUTSIDE_WRITESET"
    assert not (outside / "evil.py").exists()

    scoped = bridge.prepare(ctx, WriteSet(["src"]))
    with pytest.raises(SBLError) as caught:
        bridge.apply(scoped, "other/tool.py", "x = 1\n")
    assert caught.value.code == "SBL_E_WRITE_OUTSIDE_WRITESET"
    assert not (repo / "other").exists()

    # An absolute path is refused by the same check, and leaves no file behind.
    absolute = str(tmp_path / "outside" / "abs.py")
    with pytest.raises(SBLError) as caught:
        bridge.apply(scoped, absolute, "x = 1\n")
    assert caught.value.code == "SBL_E_WRITE_OUTSIDE_WRITESET"
    assert not (tmp_path / "outside" / "abs.py").exists()

    # Nothing at all was created inside the repo by the refused writes.
    assert not (repo / "other").exists()
    assert _git(repo, "status", "--porcelain") == ""


# ------------------------------------------------------------------ AGENT_SKILL


def test_c17_agent_skill_discover_match_load_invoke_unload() -> None:
    """AGENT_SKILL, positive: discover -> match -> effective_load -> invoke -> unload."""

    bridge = SkillBridge(str(SKILL_MANIFEST))

    discovered = bridge.discover()
    assert discovered["schema"] == "SBL-SKILL-DISCOVER/1"
    assert discovered["skill"] == "sbl-todo"
    assert "todo" in discovered["triggers"]
    assert "todo.write" in discovered["permissions"]

    # match() lowercases the intent and reports a bool.
    assert bridge.match("Please add a TODO for the review") is True
    assert bridge.match("deploy the release") is False

    loaded = bridge.effective_load({"name": "codex", "provider_on": True})
    assert loaded["schema"] == "SBL-SKILL-LOAD/1"
    assert loaded["loaded"] is True
    assert loaded["skill"] == "sbl-todo"
    assert loaded["host"] == "codex"
    assert loaded["trace_id"].startswith("L-")
    assert len(loaded["trace_id"]) == 2 + 12

    # A permitted action returns the documented success shape.
    assert bridge.invoke("todo.write", provider_on=True) == {
        "ok": True,
        "skill": "sbl-todo",
        "action": "todo.write",
    }

    unloaded = bridge.unload()
    assert unloaded == {
        "schema": "SBL-SKILL-UNLOAD/1",
        "unloaded": True,
        "residue": [],
    }

    # The lifecycle has to stay inside the manifest: repo./net. actions are refused even when the
    # host provider is on, because the bridge is not a general-purpose escape hatch.
    for action in ("repo.write", "net.call", "todo.delete"):
        with pytest.raises(SBLError) as caught:
            bridge.invoke(action, provider_on=True)
        assert caught.value.code == "SBL_E_PERMISSION_DENIED"


def test_c17_agent_skill_provider_off_refused_and_unload_has_no_load_ledger() -> None:
    """AGENT_SKILL, negative: provider-off invoke and load are refused; unload has no load ledger.

    The refusal half is asserted as the source documents it. The "unload before load is refused"
    clause is NOT supportable: ``SkillBridge`` keeps no load state (its only attributes are
    ``manifest_path``, ``manifest`` and ``name``), so ``unload()`` returns the documented unload
    shape unconditionally. Asserting a refusal here would be a guess, so the test asserts the
    actual behaviour and the deviation is recorded in the receipt.
    """

    bridge = SkillBridge(str(SKILL_MANIFEST))

    with pytest.raises(SBLError) as caught:
        bridge.invoke("todo.read", provider_on=False)
    assert caught.value.code == "SBL_E_PROVIDER_OFF"
    assert caught.value.detail["skill"] == "sbl-todo"

    with pytest.raises(SBLError) as caught:
        bridge.effective_load({"name": "codex", "provider_on": False})
    assert caught.value.code == "SBL_E_PROVIDER_OFF"

    # Actual documented behaviour: unload without a prior load succeeds and reports no residue.
    assert bridge.unload() == {
        "schema": "SBL-SKILL-UNLOAD/1",
        "unloaded": True,
        "residue": [],
    }
    # And there is no load ledger to be stale: the bridge holds no per-load state at all.
    assert set(vars(bridge)) == {"manifest_path", "manifest", "name"}


# ----------------------------------------------------------------- SIMPLE_AGENT


def test_c17_simple_agent_nofit_raises_deferred_without_a_decision(
    atom: SpecAtom, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SIMPLE_AGENT, NoFit: route raises SBL_E_DEFERRED_KIND and constructs no RouteDecision."""

    from sbl_core import m03_routing

    constructed: list[tuple] = []

    class SpyRouteDecision(m03_routing.RouteDecision):  # type: ignore[misc]
        def __init__(self, *args, **kwargs):
            constructed.append((args, kwargs))
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(m03_routing, "RouteDecision", SpyRouteDecision)

    routing = GovernedRouting()
    assert routing.disposition("SIMPLE_AGENT") == m03_routing.DEFERRED
    assert routing.policy.get("SIMPLE_AGENT") is None

    with pytest.raises(SBLError) as caught:
        routing.route(atom, "SIMPLE_AGENT")

    assert caught.value.code == "SBL_E_DEFERRED_KIND"
    assert caught.value.detail["kind"] == "SIMPLE_AGENT"
    assert caught.value.detail["disposition"] == "DEFERRED"
    assert caught.value.detail["atom_id"] == atom.atom_id
    assert caught.value.detail["reason"].strip()
    # Refusal happens before the target is touched, so nothing exists that could read as permission.
    assert constructed == []


def test_c17_unknown_kind_raises_unknown_kind_code(atom: SpecAtom) -> None:
    """Unknown kind: route refuses with SBL_E_UNKNOWN_KIND, distinct from the deferred/prohibited codes."""

    with pytest.raises(SBLError) as caught:
        GovernedRouting().route(atom, "NOT_A_KIND")

    assert caught.value.code == "SBL_E_UNKNOWN_KIND"
    assert caught.value.code not in {"SBL_E_DEFERRED_KIND", "SBL_E_PROHIBITED_KIND"}
    assert caught.value.detail["kind"] == "NOT_A_KIND"
    assert caught.value.detail["atom_id"] == atom.atom_id
    assert "disposition" not in caught.value.detail
