#!/usr/bin/env python3
"""S4POST Stage B: freeze the eight public skill packs into a source ledger.

The public plugin builder (``build_public_plugin.py``) may only consume the eight ``skills/pipd-*``
packs through a frozen ledger produced here from a *clean checkout*. The ledger pins the repo, the
commit (40 hex), the tree (40 hex), the exact eight skill names and a ``path -> sha256`` for every
file under them, and it is the binding the owner derivation records must match
(``source_sha256``). This tool REFUSES (typed reason, non-zero exit) instead of warning:

  * ``DIRTY_WORKTREE``          git status --porcelain is not empty
  * ``NOT_REPO_ROOT``           the given root is not the git top-level
  * ``GIT_UNAVAILABLE`` / ``GIT_FAILED``  git could not run
  * ``WRONG_SKILL_SET``         the skills root is missing or carries an unexpected skill
  * ``SYMLINK_MEMBER``          a symlinked file or directory inside a skill
  * ``NON_REGULAR_FILE``        a special/irregular file inside a skill (FIFO, socket, ...)
  * ``HIDDEN_OR_SPECIAL_MEMBER`` a dot-file/dot-directory inside a skill
  * ``SKILLS_ROOT_MISSING``     the skills root does not exist

Text members are canonicalised to LF (the repository pins ``* text=auto eol=lf``) so the same
checkout hashes identically on any platform; binary members are hashed raw. No git history is
written, no commit is created, nothing is published.

CLI
---
``--repo-root DIR``            repository root (default: the directory of this file)
``--skills-root DIR``          override the skills root (default: <repo>/skills)
``--out FILE``                 write the ledger JSON to FILE (default: stdout only)
``--no-git``                   skip the git clean/commit/tree gates (fixtures; requires the
                               ``--ledger-commit`` and ``--ledger-tree`` overrides)
``--ledger-commit HEX40``      freeze this commit instead of the git HEAD (fixtures/audits)
``--ledger-tree HEX40``        freeze this tree instead of the git HEAD^{tree}
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

LEDGER_VERSION = "PIPD-PUBLIC-PLUGIN-SOURCE-LEDGER/1"
EXPECTED_SKILLS = (
    "pipd-assurance-tqaep",
    "pipd-authority-source",
    "pipd-execution-contract",
    "pipd-package-project",
    "pipd-pd-bind",
    "pipd-pi-compile",
    "pipd-profile-tailor",
    "pipd-route-intake",
)
HEX40 = re.compile(r"^[0-9a-f]{40}$")


class FreezeRefusal(Exception):
    """A fail-closed refusal. ``code`` is the machine-checkable typed reason."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"REFUSED {code}: {detail}")
        self.code = code
        self.detail = detail


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_bytes(data: bytes) -> bytes:
    """Canonical member bytes: LF-normalised for text, raw for binary."""
    if b"\x00" in data:
        return data
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return data
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _git(repo: Path, *args: str) -> str:
    git = shutil.which("git")
    if git is None:
        raise FreezeRefusal("GIT_UNAVAILABLE", "no `git` executable on PATH")
    proc = subprocess.run([git, "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise FreezeRefusal(
            "GIT_FAILED",
            f"`git {' '.join(args)}` exited {proc.returncode}: "
            f"{(proc.stderr or proc.stdout).strip()}",
        )
    return proc.stdout


def _walk_skill_files(repo_root: Path, skill_dir: Path) -> dict[str, str]:
    """Every regular file under one skill, as ``repo-relative POSIX path -> canonical sha256``."""
    files: dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(skill_dir, topdown=True, followlinks=False):
        dirnames.sort()
        filenames.sort()
        for d in list(dirnames):
            p = Path(dirpath) / d
            if p.is_symlink():
                raise FreezeRefusal("SYMLINK_MEMBER", str(p))
            if d.startswith(".") or d in ("__pycache__",):
                raise FreezeRefusal("HIDDEN_OR_SPECIAL_MEMBER", str(p))
        for f in filenames:
            p = Path(dirpath) / f
            st = os.lstat(p)
            if stat.S_ISLNK(st.st_mode):
                raise FreezeRefusal("SYMLINK_MEMBER", str(p))
            if not stat.S_ISREG(st.st_mode):
                raise FreezeRefusal(
                    "NON_REGULAR_FILE",
                    f"{p} is not a regular file (mode {oct(stat.S_IMODE(st.st_mode))})")
            if f.startswith(".") or f in ("__pycache__",):
                raise FreezeRefusal("HIDDEN_OR_SPECIAL_MEMBER", str(p))
            rel = p.relative_to(repo_root).as_posix()
            files[rel] = _sha256_bytes(canonical_bytes(p.read_bytes()))
    return files


def _skill_entries(skills_root: Path) -> dict[str, Path]:
    if not skills_root.is_dir():
        raise FreezeRefusal("SKILLS_ROOT_MISSING", str(skills_root))
    entries: dict[str, Path] = {}
    for child in sorted(skills_root.iterdir()):
        if child.name.startswith(".") or child.name == "__pycache__":
            continue
        if child.is_symlink():
            raise FreezeRefusal("SYMLINK_MEMBER", str(child))
        if not child.is_dir():
            raise FreezeRefusal("NON_REGULAR_FILE",
                                f"{child} sits directly in the skills root and is not a skill dir")
        entries[child.name] = child
    return entries


def freeze(repo_root: Path, skills_root: Path | None = None, *, require_git: bool = True,
           commit_override: str | None = None, tree_override: str | None = None,
           repo_url_override: str | None = None,
           expected_skills: tuple[str, ...] = EXPECTED_SKILLS) -> dict:
    """Produce the frozen source ledger. Raises :class:`FreezeRefusal` on any deviation."""
    repo_root = Path(repo_root).resolve()
    skills_root = Path(skills_root).resolve() if skills_root is not None else repo_root / "skills"

    if require_git:
        top = _git(repo_root, "rev-parse", "--show-toplevel").strip()
        if Path(top).resolve() != repo_root:
            raise FreezeRefusal("NOT_REPO_ROOT",
                                f"git top-level {top!r} != given repo root {repo_root}")
        dirty = _git(repo_root, "status", "--porcelain", "--untracked-files=normal").strip()
        if dirty:
            raise FreezeRefusal("DIRTY_WORKTREE",
                                "worktree is not clean:\n" + "\n".join(dirty.splitlines()[:20]))
        commit = _git(repo_root, "rev-parse", "HEAD").strip()
        tree = _git(repo_root, "rev-parse", "HEAD^{tree}").strip()
        repo_url = _git(repo_root, "remote", "get-url", "origin").strip() or "NO_REMOTE"
    else:
        if commit_override is None or tree_override is None:
            raise FreezeRefusal("FIXTURE_OVERRIDE_MISSING",
                                "--no-git requires --ledger-commit and --ledger-tree")
        commit, tree = commit_override, tree_override
        repo_url = repo_url_override or "FIXTURE_NO_GIT"

    for label, value in (("commit", commit), ("tree", tree)):
        if not HEX40.match(value):
            raise FreezeRefusal("IDENTITY_INVALID",
                                f"{label} is not 40 hex chars: {value!r}")

    entries = _skill_entries(skills_root)
    missing = [n for n in expected_skills if n not in entries]
    extra = [n for n in sorted(entries) if n not in set(expected_skills)]
    if missing or extra:
        raise FreezeRefusal("WRONG_SKILL_SET",
                            f"expected exactly {sorted(expected_skills)}; "
                            f"missing={missing} extra={extra}")

    files: dict[str, str] = {}
    for name in sorted(entries):
        files.update(_walk_skill_files(repo_root, entries[name]))

    total = sum(len(canonical_bytes((repo_root / rel).read_bytes())) for rel in files)
    return {
        "ledger_version": LEDGER_VERSION,
        "repo": repo_url,
        "commit": commit,
        "tree": tree,
        "skills": sorted(entries),
        "canonicalization": "text=LF;binary=raw",
        "file_count": len(files),
        "total_canonical_bytes": total,
        "files": files,
    }


def canonical_json(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--skills-root", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--no-git", action="store_true", help="fixture mode (no git gates)")
    ap.add_argument("--ledger-commit", default=None)
    ap.add_argument("--ledger-tree", default=None)
    ap.add_argument("--repo-url", default=None)
    args = ap.parse_args(argv)
    try:
        ledger = freeze(
            Path(args.repo_root),
            Path(args.skills_root) if args.skills_root else None,
            require_git=not args.no_git,
            commit_override=args.ledger_commit,
            tree_override=args.ledger_tree,
            repo_url_override=args.repo_url,
        )
    except FreezeRefusal as exc:
        print(str(exc))
        return 2
    text = canonical_json(ledger)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8", newline="")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
