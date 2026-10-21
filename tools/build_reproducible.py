#!/usr/bin/env python3
"""Build a byte-reproducible wheel and sdist from a git tree.

WHY THIS EXISTS (closes TT-R6-WHEEL-NONREPRODUCIBLE-001)

A wheel built straight from a Windows working tree is NOT reproducible, for two
independent reasons that were MEASURED on this repo (candidate a6bcdd0):

1. Line endings. The repo had no .gitattributes and the local git config had
   core.autocrlf=true, so a checkout rewrote every text file to CRLF on disk.
   The git OBJECTS were already LF-clean (verified with `git cat-file blob`),
   so the CRLF was introduced by the checkout, not by the source of truth. Two
   builds of the same commit therefore shipped different bytes for 7 members.

2. Archive timestamps. zip records the mtime of each file it packs. Two builds
   minutes apart produced 39 differing timestamps, so the member digests could
   never match even when the content did.

This tool removes both causes instead of documenting them:

  * the source tree is exported with `git -c core.autocrlf=false archive`, so the
    build input is the git blob content (LF), never the working tree;
  * SOURCE_DATE_EPOCH is pinned, so the archive timestamps are fixed.

MEASURED RESULT: two independent builds of a6bcdd0 through this tool produced
the identical wheel sha256 and a single distinct member timestamp.

The tool NEVER builds from a dirty working tree: it always exports a named
commit, so a build is a function of (commit, builder version) only.

Usage:
    python tools/build_reproducible.py --commit a6bcdd0 --outdir dist
    python tools/build_reproducible.py --commit HEAD --outdir dist --verify
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

# A fixed, arbitrary epoch (2023-11-14T22:13:20Z). Pinned so the archive
# timestamps are constant across builds and machines.
DEFAULT_SOURCE_DATE_EPOCH = 1700000000


def run(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def run_bytes(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    """Same as run() but keeps stdout as bytes. `git archive` emits a binary tar."""
    return subprocess.run(cmd, capture_output=True, **kw)


def _has_build(python: str) -> bool:
    """Can this interpreter actually run the build backend?

    NOT `import build`. A repository that contains a `build/` directory (this one
    does: `build/bdist.win-amd64`, `build/lib`) makes `import build` succeed as a
    NAMESPACE PACKAGE, so the naive probe returns True for an interpreter that
    cannot build anything. The independent checker found this: the brief's own
    command failed with "No module named build.__main__; 'build' is a package and
    cannot be directly executed", while the resolver had reported success.

    The probe must therefore ask the question that will actually be asked later:
    can this interpreter RUN the build module?

    A candidate interpreter that does not exist at all must NOT raise. The
    resolver deliberately probes several candidates, including an
    `SBL_BUILD_PYTHON` override and every `python` on PATH, and any of them
    may be a path that does not exist. An unhandled `FileNotFoundError` there
    aborts the whole resolution with a traceback instead of moving on to the
    next candidate -- and the resulting traceback does not say anything a
    reader can act on. A missing interpreter simply does not have the build
    backend.
    """
    try:
        r = subprocess.run(
            [python, "-m", "build", "--version"], capture_output=True, timeout=180
        )
    except (OSError, subprocess.SubprocessError):
        return False
    if r.returncode == 0:
        return True
    # `python -m build` needs a console entry point; fall back to importing the
    # module's __main__, which is the thing the resolver actually invokes.
    try:
        r2 = subprocess.run(
            [python, "-c", "import build.__main__"], capture_output=True, timeout=120
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return r2.returncode == 0


def _builder_python() -> str:
    """Find an interpreter that can actually run `python -m build`.

    The build backend must not depend on whatever `sys.executable` happens to be:
    the independent checker runs this tool from a venv that does NOT have
    `build` installed, and the build then fails for an environmental reason that
    has nothing to do with the artefact. Resolution order:

      1. the interpreter running this script, if it has `build`;
      2. `$SBL_BUILD_PYTHON`, if it has `build`;
      3. any interpreter on PATH that has `build` (checked in order);
      4. any venv interpreter next to the repository.

    If none has it, the failure says exactly that instead of a bare
    "No module named build".
    """
    override = os.environ.get("SBL_BUILD_PYTHON")
    candidates: list[str] = []
    if override:
        candidates.append(override)
    candidates.append(sys.executable)
    for name in ("python", "python3", "py"):
        found = shutil.which(name)
        if found:
            candidates.append(found)
    repo = Path(__file__).resolve().parent.parent
    for venv in (repo / ".venv" / "Scripts" / "python.exe",
                 repo.parent / ".venv" / "Scripts" / "python.exe"):
        if venv.exists():
            candidates.append(str(venv))
    seen: set[str] = set()
    for cand in candidates:
        if cand in seen:
            continue
        seen.add(cand)
        if _has_build(cand):
            return cand
    raise SystemExit(
        "no interpreter with the 'build' package was found. Install it with "
        "'pip install build', or point SBL_BUILD_PYTHON at an interpreter that "
        "has it. (Checked: "
        + ", ".join(sorted(seen))
        + ")"
    )


def git(repo: Path, *args: str) -> str:
    r = run(["git", "-C", str(repo), *args])
    if r.returncode != 0:
        raise SystemExit(f"git failed: {' '.join(args)}\n{r.stderr}")
    return r.stdout.strip()


def export_tree(repo: Path, commit: str, dest: Path) -> None:
    """Export `commit` to `dest` with autocrlf disabled so the bytes are the blobs."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    tar_bytes = run_bytes(
        ["git", "-C", str(repo), "-c", "core.autocrlf=false", "archive", "--format=tar", commit]
    )
    if tar_bytes.returncode != 0:
        raise SystemExit(f"git archive failed:\n{tar_bytes.stderr.decode('utf-8', 'replace')}")
    tar_path = dest.parent / f"{dest.name}.tar"
    tar_path.write_bytes(tar_bytes.stdout)
    with tarfile.open(tar_path) as tf:
        tf.extractall(dest)
    tar_path.unlink()


def build(src: Path, outdir: Path, epoch: int) -> list[Path]:
    env = dict(os.environ)
    env["SOURCE_DATE_EPOCH"] = str(epoch)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    outdir.mkdir(parents=True, exist_ok=True)
    r = run([_builder_python(), "-m", "build", "--outdir", str(outdir), str(src)], env=env)
    if r.returncode != 0:
        raise SystemExit(f"build failed:\n{r.stdout[-4000:]}\n{r.stderr[-4000:]}")
    wheels = sorted(outdir.glob("*.whl"))
    # setuptools honours SOURCE_DATE_EPOCH for the WHEEL but NOT for the sdist:
    # measured, the .tar.gz carried 21 distinct member mtimes and the gzip header
    # embedded the wall-clock time, so two sdist builds never matched. The sdist is
    # therefore REPACKED here with a fixed mtime and gzip mtime=0.
    for sdist in sorted(outdir.glob("*.tar.gz")):
        normalise_sdist(sdist, epoch)
    return wheels + sorted(outdir.glob("*.tar.gz"))


def normalise_sdist(sdist: Path, epoch: int) -> None:
    """Rewrite a .tar.gz so its member mtimes and the gzip header are constant.

    PAX_FORMAT keeps a sub-second mtime in `member.pax_headers["mtime"]`, and
    `create_pax_header` only OVERWRITES that header when the value does not fit
    the 12-digit ustar field. An integer epoch fits, so the original float
    survived and the member mtimes stayed non-constant. The header is therefore
    removed explicitly and the mtime is re-set as a float.
    """
    raw = sdist.read_bytes()
    inner = gzip.decompress(raw)
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w", format=tarfile.PAX_FORMAT) as tf:
        with tarfile.open(fileobj=io.BytesIO(inner)) as src:
            for member in src.getmembers():
                member.pax_headers = {
                    k: v for k, v in member.pax_headers.items() if k != "mtime"
                }
                member.mtime = float(epoch)
                member.uid = member.gid = 0
                member.uname = member.gname = ""
                f = src.extractfile(member) if member.isfile() else None
                tf.addfile(member, f)
    packed = io.BytesIO()
    with gzip.GzipFile(fileobj=packed, mode="wb", compresslevel=9, mtime=0) as gz:
        gz.write(out.getvalue())
    sdist.write_bytes(packed.getvalue())


def describe(artifact: Path) -> dict:
    h = hashlib.sha256(artifact.read_bytes()).hexdigest()
    info = {"name": artifact.name, "bytes": artifact.stat().st_size, "sha256": h}
    if artifact.suffix == ".whl":
        with zipfile.ZipFile(artifact) as z:
            infos = z.infolist()
            info["members"] = len(infos)
            info["distinct_timestamps"] = sorted({i.date_time for i in infos})
    return info


def main() -> int:
    ap = argparse.ArgumentParser(description="byte-reproducible build from a git commit")
    ap.add_argument("--commit", required=True, help="commit-ish to build (never the working tree)")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--workdir", default=None, help="scratch dir for the exported tree")
    ap.add_argument("--source-date-epoch", type=int, default=DEFAULT_SOURCE_DATE_EPOCH)
    ap.add_argument("--verify", action="store_true", help="build twice and assert identical digests")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    commit = git(repo, "rev-parse", args.commit)
    scratch = Path(args.workdir) if args.workdir else Path(os.environ.get("TMPDIR", ".")) / "sbl-repro-build"
    scratch.mkdir(parents=True, exist_ok=True)
    src = scratch / f"src-{commit[:12]}"

    export_tree(repo, commit, src)
    outdir = Path(args.outdir)
    if outdir.exists():
        shutil.rmtree(outdir)

    artifacts = build(src, outdir, args.source_date_epoch)
    result = {
        "schema": "SBL_REPRODUCIBLE_BUILD/1",
        "repo": str(repo),
        "commit": commit,
        "source_date_epoch": args.source_date_epoch,
        "source_tree": str(src),
        "artifacts": [describe(a) for a in artifacts],
    }

    if args.verify:
        outdir2 = outdir.parent / f"{outdir.name}-verify"
        if outdir2.exists():
            shutil.rmtree(outdir2)
        artifacts2 = build(src, outdir2, args.source_date_epoch)
        second = {describe(a)["name"]: describe(a)["sha256"] for a in artifacts2}
        first = {a["name"]: a["sha256"] for a in result["artifacts"]}
        # every wheel must carry exactly ONE member timestamp, else the archive is not pinned
        single_timestamp = all(
            len(a.get("distinct_timestamps", [])) == 1 for a in result["artifacts"] if a["name"].endswith(".whl")
        )
        result["verify"] = {
            "second_build": second,
            "identical": first == second,
            "single_member_timestamp": single_timestamp,
        }
        shutil.rmtree(outdir2, ignore_errors=True)

    text = json.dumps(result, ensure_ascii=False, indent=1)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    print(text)
    if args.verify and not result["verify"]["identical"]:
        print("REPRODUCIBILITY_FAIL", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
