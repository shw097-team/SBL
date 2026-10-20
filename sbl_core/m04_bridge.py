"""SBLM04 - Governed Build Bridge."""

from __future__ import annotations

import os
import subprocess

from .dto import BuildOrder, RepoContextDTO, WriteSet, order_id_for
from .errors import SBLError


def _run_git(root: str, *args: str) -> str:
    try:
        completed = subprocess.run(
            ["git", "-C", root, *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise SBLError(
            "SBL_E_BAD_STATE", "git is unavailable", {"root": root, "error": str(exc)}
        ) from exc
    if completed.returncode != 0:
        raise SBLError(
            "SBL_E_BAD_STATE",
            f"git {' '.join(args)} failed",
            {
                "root": root,
                "exit": completed.returncode,
                "stderr": completed.stderr.strip(),
            },
        )
    return completed.stdout


def _head_of(root: str) -> str:
    return _run_git(root, "rev-parse", "HEAD").strip()


def bind_repo_context(root: str) -> RepoContextDTO:
    """Read HEAD, porcelain status and tracked-file count for ``root``."""

    if not root:
        raise SBLError("SBL_E_BAD_STATE", "repo root is required", {"root": root})
    resolved = os.path.abspath(root)
    if not os.path.isdir(resolved):
        raise SBLError(
            "SBL_E_BAD_STATE", "repo root is not a directory", {"root": resolved}
        )
    head = _head_of(resolved)
    if len(head) != 40 or any(ch not in "0123456789abcdef" for ch in head.lower()):
        raise SBLError(
            "SBL_E_BAD_STATE", "not a git work tree", {"root": resolved, "head": head}
        )
    status = _run_git(resolved, "status", "--porcelain")
    tracked_lines = [
        line for line in _run_git(resolved, "ls-files").splitlines() if line.strip()
    ]
    return RepoContextDTO(
        root=resolved,
        head=head,
        tracked_files=len(tracked_lines),
        dirty=bool(status.strip()),
    )


def _normalize_prefix(prefix: str) -> str:
    cleaned = str(prefix).replace("\\", "/").strip()
    while cleaned.startswith("./"):
        cleaned = cleaned[2:]
    return cleaned.rstrip("/")


def _is_under(relative: str, prefix: str) -> bool:
    if prefix in ("", "."):
        return True
    return relative == prefix or relative.startswith(prefix + "/")


class GovernedBuildBridge:
    """Prepare and apply writes strictly inside the declared writeset."""

    def prepare(self, ctx: RepoContextDTO, writeset: WriteSet) -> BuildOrder:
        if writeset is None or not tuple(writeset.paths):
            raise SBLError(
                "SBL_E_BAD_STATE",
                "writeset must declare at least one path prefix",
                {"root": getattr(ctx, "root", None)},
            )
        return BuildOrder(
            order_id=order_id_for(ctx.head, writeset),
            root=ctx.root,
            head=ctx.head,
            writeset=writeset,
        )

    def apply(self, order: BuildOrder, path: str, content: str) -> BuildOrder:
        if not isinstance(path, str) or not path.strip():
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "write path must be a non-empty relative path",
                {"path": path},
            )
        raw = path.replace("\\", "/").strip()
        if raw.startswith("/") or (len(raw) > 1 and raw[1] == ":"):
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "absolute write paths are refused",
                {"path": path},
            )
        root = os.path.abspath(order.root)
        target = os.path.abspath(os.path.join(root, raw))
        try:
            relative = os.path.relpath(target, root).replace("\\", "/")
        except ValueError as exc:
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "write path cannot be resolved against the order root",
                {"path": path, "root": root},
            ) from exc
        if relative == ".." or relative.startswith("../"):
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "path traversal is refused",
                {"path": path, "root": root},
            )
        prefixes = [
            _normalize_prefix(prefix) for prefix in order.writeset.paths
        ]
        if not any(_is_under(relative, prefix) for prefix in prefixes):
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "resolved path is outside the declared writeset",
                {"path": relative, "writeset": list(order.writeset.paths)},
            )
        # Lexical containment is not containment: ``allowed -> outside_dir`` passes abspath/relpath
        # and then writes through the link (external acceptance report R1, D2). Resolve the real
        # destination and re-check it against the real root before touching the file.
        real_root = os.path.realpath(root)
        real_target = os.path.realpath(target)
        try:
            real_relative = os.path.relpath(real_target, real_root).replace("\\", "/")
        except ValueError as exc:
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "write target cannot be resolved against the repository root",
                {"path": path, "root": root},
            ) from exc
        if real_relative == ".." or real_relative.startswith("../"):
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "write target resolves outside the repository root through a link",
                {"path": path, "real_target": real_target, "real_root": real_root},
            )
        if not any(_is_under(real_relative, prefix) for prefix in prefixes):
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "resolved real destination leaves the declared writeset",
                {"path": real_relative, "writeset": list(order.writeset.paths)},
            )

        current_head = _head_of(root)
        if current_head != order.head:
            raise SBLError(
                "SBL_E_STALE_HEAD",
                "HEAD moved since the build order was prepared",
                {"expected": order.head, "actual": current_head},
            )
        # The check above and the write below are not the same instant. A checker reproduced a
        # junction-swap escape by replacing a directory with a link between them (V16-BRIDGE-01), so:
        # resolve again immediately before opening, write to the RESOLVED path rather than the literal
        # one, and verify after the write that the file really landed inside the root.
        settled = os.path.realpath(target)
        if settled != real_target:
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "write target changed between validation and write",
                {"path": path, "validated": real_target, "at_write": settled},
            )
        parent = os.path.dirname(real_target)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(real_target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        landed = os.path.realpath(real_target)
        if os.path.relpath(landed, real_root).replace("\\", "/").startswith(".."):
            try:
                os.unlink(real_target)
            except OSError:
                pass
            raise SBLError(
                "SBL_E_WRITE_OUTSIDE_WRITESET",
                "write landed outside the repository root and was removed",
                {"path": path, "landed": landed, "real_root": real_root},
            )
        applied = tuple(order.writeset.paths)
        if relative not in set(prefixes):
            applied = applied + (relative,)
        return BuildOrder(
            order_id=order.order_id,
            root=order.root,
            head=order.head,
            writeset=WriteSet(applied),
        )
