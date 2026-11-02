#!/usr/bin/env python3
"""S2 verifier envelope: a disposable byte-copy, a per-file snapshot, a three-way delta guard.

A verifier must run inside a *disposable* copy of the product tree, with its scratch **outside**
both trees, so that the product's own guards (secret scan, deny-list scan) never see the verifier's
footprint and a frozen candidate cannot be dirtied by the check itself (R4 failure class C4).

Three subcommands:

* ``init --src <repo> --dst <copy> [--scratch <dir>]``
  Walk ``src`` into a byte-copy at ``dst``, INCLUDING ``.git`` (so the copy is a real git checkout)
  and EXCLUDING ``__pycache__`` dirs and ``*.pyc`` files. Assert the copy's HEAD equals the
  source's; if it differs, fail. Write the envelope record to ``--scratch``
  (default ``%TEMP%\\r4h\\envelope``).
* ``snapshot --repo <path> --out <file>``
  Record HEAD, dirty count and a ``{relpath: sha256}`` manifest over the repo's tracked files.
  A file listed by git but missing on disk is recorded as ``"MISSING"``.
* ``verify --before <json> --after <json> [--allow-added <regex> ...]``
  Classify every path as MODIFIED / REMOVED / ADDED. Exit non-zero when any MODIFIED or REMOVED
  path exists, or when an ADDED path matches none of the allow-rules. The three-way split is the
  whole point: a before/after guard that reports ANY difference as drift would flag the very file
  the brief mandated the writer to create, and a guard that cries wolf is worse than none.

Refusals (non-zero, clear message): ``--dst`` inside ``--src`` (or the reverse), and ``--scratch``
inside either tree. The envelope's value *is* the boundary it asserts, so the boundary is checked
before a single byte is written.

Destruction guards (H2-DEFECT-02): ``init`` additionally refuses a blank/whitespace-only ``--dst``
before normalisation (STOP-1); a resolved ``--dst`` that is the cwd, the user home, or a
filesystem/drive root (STOP-2); a ``--dst`` equal to ``--src`` or an ancestor of it (STOP-3); and an
existing non-empty ``--dst`` unless ``--allow-destroy`` is given (STOP-5). Before any removal it
prints the absolute path being destroyed (STOP-4). ``--allow-destroy`` never bypasses STOP-1..STOP-3.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ENVELOPE_SCHEMA = "PIPD-ROUND-ENVELOPE/1"
SNAPSHOT_SCHEMA = "PIPD-ROUND-SNAPSHOT/1"
BOUNDARY_SCHEMA = "PIPD-ROUND-BOUNDARY-CHECK/1"
MISSING = "MISSING"

# Only caches are excluded from the copy: `.git` must survive so the copy is a real checkout.
EXCLUDE_DIRS = {"__pycache__"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}


# --------------------------------------------------------------------------- helpers


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _within(child: Path, ancestor: Path) -> bool:
    """True when ``child`` is ``ancestor`` or lives inside it (both resolved)."""
    try:
        return child.resolve().is_relative_to(ancestor.resolve())
    except OSError:  # pragma: no cover - resolve failure is pathological on this host
        return False


# An MSYS/POSIX-style path such as ``/c/Users/x`` (drive letter as the first segment).
_MSYS_RE = re.compile(r"^/([A-Za-z])/(.*)$")


def _norm_path(value: str | os.PathLike) -> str:
    """Normalise a CLI path argument to an expanded, drive/host-absolute string.

    On Windows an MSYS-style argument (``/c/Users/x``) is rewritten to ``c:/Users/x`` *before*
    normalising, so the house habit of POSIX-style paths does not silently become a relative
    ``\\c\\Users\\x`` under the current drive (defect H2-DEFECT-01). A native drive-absolute path
    (``C:\\x`` or ``C:/x``) survives unchanged; ``~`` is expanded.
    """
    text = str(value)
    if os.name == "nt":
        m = _MSYS_RE.match(text)
        if m:
            text = f"{m.group(1)}:/{m.group(2)}"
    return os.path.abspath(os.path.expanduser(text))


def guard_paths(src: Path, dst: Path, scratch: Path) -> list[str]:
    """Return the refusal messages for the src/dst/scratch boundary (empty list == admissible).

    A verifier envelope only means something if the copy is *outside* the source and the scratch is
    *outside both*; a scratch inside the tested tree is exactly the C4 failure the envelope prevents.
    """
    problems: list[str] = []
    if _within(dst, src):
        problems.append(f"--dst {dst} resolves inside --src {src}: the copy must be a separate tree")
    if _within(src, dst):
        problems.append(f"--src {src} resolves inside --dst {dst}: the source must not live in the copy")
    if _within(scratch, src):
        problems.append(f"--scratch {scratch} resolves inside --src {src}: scratch must be outside the tested tree")
    if _within(scratch, dst):
        problems.append(f"--scratch {scratch} resolves inside --dst {dst}: scratch must be outside the copy")
    return problems


def is_blank(value: object) -> bool:
    """True for a missing, empty, or whitespace-only path argument (STOP-1).

    A genuinely empty argument normalises to the current working directory
    (``os.path.abspath("") == os.getcwd()``), which is exactly how H2-DEFECT-02 let an empty ``--dst``
    resolve onto the repo root; a blank value is therefore never a valid destination and is refused
    **before** any normalisation.
    """
    return value is None or not str(value).strip()


def is_fs_root(path: Path) -> bool:
    """True when ``path`` is a filesystem/drive root (``C:\\``, ``/``): a path with no parent."""
    resolved = path.resolve()
    return resolved.parent == resolved


def guard_destination(src: Path, dst: Path) -> list[str]:
    """STOP-2/STOP-3: refusals for a destination that must never be destroyed.

    Independent of :func:`guard_paths` (which models *containment between the three arguments*) and
    structurally able to cover the one case those guards are blind to: a destination that resolved
    onto a place the tool must never touch, whatever the other arguments say.
    """
    problems: list[str] = []
    r = dst.resolve()
    if r == Path.cwd().resolve():
        problems.append(f"--dst {r} is the current working directory: refusing to destroy the cwd")
    try:
        home = Path.home().resolve()
    except (RuntimeError, OSError):  # pragma: no cover - home is always resolvable in practice
        home = None
    if home is not None and r == home:
        problems.append(f"--dst {r} is the user home directory: refusing to destroy the home directory")
    if is_fs_root(r):
        problems.append(f"--dst {r} is a filesystem/drive root: refusing to destroy a root")
    if r == src.resolve():
        problems.append(f"--dst {r} equals --src: refusing to destroy the source tree")
    return problems


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def git_head(repo: Path) -> str:
    """HEAD via ``git -C <repo> rev-parse HEAD``; "" when git is absent or the repo is unbound."""
    try:
        proc = _git(repo, "rev-parse", "HEAD")
    except (FileNotFoundError, OSError):
        return ""
    if proc.returncode != 0:
        return ""
    return proc.stdout.strip()


def git_dirty_count(repo: Path) -> int:
    """Number of entries ``git status --porcelain`` reports (0 when git is unavailable)."""
    try:
        proc = _git(repo, "status", "--porcelain")
    except (FileNotFoundError, OSError):
        return 0
    if proc.returncode != 0:
        return 0
    return sum(1 for line in proc.stdout.splitlines() if line.strip())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def copy_tree(src: Path, dst: Path) -> int:
    """Byte-copy ``src`` into ``dst`` (incl. ``.git``), pruning caches. Returns files copied."""
    copied = 0
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        rel = Path(root).relative_to(src)
        (dst / rel).mkdir(parents=True, exist_ok=True)
        for name in files:
            if Path(name).suffix.lower() in EXCLUDE_SUFFIXES:
                continue
            shutil.copy2(Path(root) / name, dst / rel / name)
            copied += 1
    return copied


# --------------------------------------------------------------------------- snapshot


def snapshot_repo(repo: Path) -> dict:
    """Build a snapshot record over the repo's tracked files (git ls-files + on-disk sha256)."""
    files: dict[str, str] = {}
    try:
        proc = _git(repo, "ls-files")
        listing = proc.stdout.splitlines() if proc.returncode == 0 else []
    except (FileNotFoundError, OSError):
        listing = []
    for raw in listing:
        rel = raw.strip()
        if not rel:
            continue
        on_disk = Path(repo) / rel
        files[rel] = sha256_file(on_disk) if on_disk.is_file() else MISSING
    return {
        "schema": SNAPSHOT_SCHEMA,
        "repo": str(repo),
        "head": git_head(repo),
        "dirty": git_dirty_count(repo),
        "as_of": _now(),
        "files": dict(sorted(files.items())),
    }


# --------------------------------------------------------------------------- verify


def classify_delta(before: dict, after: dict, allow_res: list[re.Pattern]) -> dict:
    """Classify the before/after file maps into MODIFIED / REMOVED / ADDED.

    An ADDED path that matches any allow-rule is ``allowed_added`` (a mandated creation, NOT drift);
    an ADDED path matching no rule is ``unexpected_added``. Verdict is DRIFT when any MODIFIED or
    REMOVED path exists, or any unexpected addition exists.
    """
    b = before.get("files", {})
    a = after.get("files", {})
    modified = sorted(p for p in b if p in a and b[p] != a[p])
    removed = sorted(p for p in b if p not in a)
    added = sorted(p for p in a if p not in b)
    allowed_added = [p for p in added if any(rx.search(p) for rx in allow_res)]
    unexpected_added = [p for p in added if p not in set(allowed_added)]
    drift = bool(modified or removed or unexpected_added)
    return {
        "schema": BOUNDARY_SCHEMA,
        "modified": modified,
        "removed": removed,
        "added": added,
        "allowed_added": allowed_added,
        "unexpected_added": unexpected_added,
        "verdict": "DRIFT" if drift else "CLEAN",
    }


def _print_named(label: str, items: list[str]) -> None:
    if items:
        for it in items:
            print(f"{label}: {it}")
    else:
        print(f"{label}: (none)")


# --------------------------------------------------------------------------- commands


def cmd_init(args: argparse.Namespace) -> int:
    # STOP-1: refuse a blank/whitespace-only --dst BEFORE any normalisation. _norm_path("") ==
    # os.path.abspath("") == the cwd, so a blank destination would silently become the working
    # directory and rmtree would destroy it (H2-DEFECT-02). This check precedes every other step.
    if is_blank(getattr(args, "dst", None)):
        print("round_envelope init: REFUSED - --dst '' is blank: an empty path is never a valid "
              "destination", file=sys.stderr)
        return 2
    src = Path(_norm_path(args.src))
    dst = Path(_norm_path(args.dst))
    scratch = Path(_norm_path(args.scratch)) if args.scratch else Path(tempfile.gettempdir()) / "r4h" / "envelope"

    if not src.is_dir():
        print(f"round_envelope init: --src {src} is not a directory", file=sys.stderr)
        return 2

    # STOP-2 (cwd / home / drive root) and STOP-3 (dst == src, or dst an ancestor of src — the latter
    # is also covered by the guard_paths containment checks below, both directions). These answer
    # "is this destination safe to destroy at all", which the containment guards cannot.
    problems = guard_destination(src, dst) + guard_paths(src, dst, scratch)
    if problems:
        for p in problems:
            print(f"round_envelope init: REFUSED - {p}", file=sys.stderr)
        return 2

    # STOP-5: --allow-destroy (default OFF) merely permits destroying an existing NON-EMPTY
    # destination. STOP-1..STOP-3 have already refused above, so this flag cannot bypass them.
    if not args.allow_destroy and dst.is_dir() and any(dst.iterdir()):
        print(f"round_envelope init: REFUSED - --dst {dst.resolve()} exists and is non-empty: "
              "pass --allow-destroy to replace it", file=sys.stderr)
        return 2

    src_head = git_head(src)
    # Fail closed: an uncreatable destination (e.g. a path exceeding Windows MAX_PATH, or a parent
    # that is a file) must be a named refusal, not an opaque os-level traceback.
    try:
        if dst.exists():
            # STOP-4: name the exact absolute path about to be destroyed before destroying it, so the
            # destructive step is visible in the log rather than silent.
            print(f"round_envelope init: removing existing destination {dst.resolve()}", file=sys.stderr)
            shutil.rmtree(dst)
        dst.mkdir(parents=True, exist_ok=True)
        copied = copy_tree(src, dst)
    except OSError as exc:
        print(f"round_envelope init: REFUSED: destination path too long or uncreatable: {dst} "
              f"({exc.__class__.__name__}: {exc})", file=sys.stderr)
        return 2
    dst_head = git_head(dst)
    # Re-read the source *after* the copy so a source that moved mid-run is reported, not absorbed.
    src_head_after = git_head(src)

    head_ok = bool(src_head) and src_head == dst_head == src_head_after
    assertions = [
        {"id": "copy_created", "status": "PASS",
         "detail": f"{copied} files copied into {dst} (incl. .git, excl. __pycache__/*.pyc)"},
        {"id": "dst_outside_src", "status": "PASS",
         "detail": f"{dst} is not inside {src}"},
        {"id": "scratch_outside_trees", "status": "PASS",
         "detail": f"{scratch} is outside {src} and {dst}"},
        {"id": "head_equals_source", "status": "PASS" if head_ok else "FAIL",
         "detail": f"src HEAD={src_head or '(unbound)'} dst HEAD={dst_head or '(unbound)'}"},
    ]

    record = {
        "schema": ENVELOPE_SCHEMA,
        "src": str(src.resolve()),
        "dst": str(dst.resolve()),
        "scratch": str(scratch.resolve()),
        "head": src_head,
        "dirty": git_dirty_count(src),
        "created_at": _now(),
        "assertions": assertions,
    }
    try:
        scratch.mkdir(parents=True, exist_ok=True)
        out = scratch / "envelope.json"
        out.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    except OSError as exc:
        print(f"round_envelope init: REFUSED: scratch path too long or uncreatable: {scratch} "
              f"({exc.__class__.__name__}: {exc})", file=sys.stderr)
        return 2
    print(json.dumps(record, ensure_ascii=False, indent=1))

    if not head_ok:
        print(f"round_envelope init: FAIL - copy HEAD {dst_head or '(unbound)'} != "
              f"source HEAD {src_head or '(unbound)'}", file=sys.stderr)
        return 1
    print(f"round_envelope init: envelope written to {out}", file=sys.stderr)
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    repo = Path(_norm_path(args.repo))
    if not repo.is_dir():
        print(f"round_envelope snapshot: --repo {repo} is not a directory", file=sys.stderr)
        return 2
    record = snapshot_repo(repo)
    out = Path(_norm_path(args.out))
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, ensure_ascii=False, indent=1), encoding="utf-8", newline="")
    except OSError as exc:
        print(f"round_envelope snapshot: REFUSED: output path too long or uncreatable: {out} "
              f"({exc.__class__.__name__}: {exc})", file=sys.stderr)
        return 2
    print(json.dumps({"schema": record["schema"], "repo": record["repo"], "head": record["head"],
                      "dirty": record["dirty"], "files": len(record["files"]), "out": str(out)},
                     ensure_ascii=False, indent=1))
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    before = json.loads(Path(_norm_path(args.before)).read_text(encoding="utf-8"))
    after = json.loads(Path(_norm_path(args.after)).read_text(encoding="utf-8"))
    try:
        allow_res = [re.compile(r) for r in args.allow_added]
    except re.error as exc:
        print(f"round_envelope verify: invalid --allow-added regex: {exc}", file=sys.stderr)
        return 2

    result = classify_delta(before, after, allow_res)
    _print_named("MODIFIED", result["modified"])
    _print_named("REMOVED", result["removed"])
    _print_named("ADDED", result["added"])
    _print_named("ALLOWED_ADDED", result["allowed_added"])
    _print_named("UNEXPECTED_ADDED", result["unexpected_added"])
    print(f"VERDICT: {result['verdict']}")
    print(json.dumps(result, ensure_ascii=False, indent=1))

    if result["verdict"] != "CLEAN":
        print(f"round_envelope verify: FAIL - MODIFIED={len(result['modified'])} "
              f"REMOVED={len(result['removed'])} "
              f"UNEXPECTED_ADDED={len(result['unexpected_added'])}", file=sys.stderr)
        return 1
    return 0


# --------------------------------------------------------------------------- main


def _build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="round_envelope",
        description="S2 verifier envelope: disposable byte-copy, per-file snapshot, three-way delta guard.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="materialise a disposable byte-copy and write an envelope record")
    p_init.add_argument("--src", required=True, help="source repo to copy")
    p_init.add_argument("--dst", required=True, help="destination copy (must be outside src)")
    p_init.add_argument("--scratch", default=None,
                        help="envelope output dir (default: %%TEMP%%\\r4h\\envelope); must be outside src and dst")
    p_init.add_argument("--allow-destroy", action="store_true",
                        help="permit destroying an existing non-empty --dst (STOP-1..STOP-3 still refuse)")
    p_init.set_defaults(func=cmd_init)

    p_snap = sub.add_parser("snapshot", help="record HEAD/dirty and a per-file sha256 manifest")
    p_snap.add_argument("--repo", required=True)
    p_snap.add_argument("--out", required=True)
    p_snap.set_defaults(func=cmd_snapshot)

    p_ver = sub.add_parser("verify", help="classify before/after snapshots as MODIFIED/REMOVED/ADDED")
    p_ver.add_argument("--before", required=True)
    p_ver.add_argument("--after", required=True)
    p_ver.add_argument("--allow-added", action="append", default=[], metavar="REGEX",
                       help="regex; an ADDED path matching any rule is allowed (never drift)")
    p_ver.set_defaults(func=cmd_verify)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
