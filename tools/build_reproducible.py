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
import hashlib
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
    tar_bytes = run(
        ["git", "-C", str(repo), "-c", "core.autocrlf=false", "archive", "--format=tar", commit]
    )
    if tar_bytes.returncode != 0:
        raise SystemExit(f"git archive failed:\n{tar_bytes.stderr}")
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
    r = run([sys.executable, "-m", "build", "--outdir", str(outdir), str(src)], env=env)
    if r.returncode != 0:
        raise SystemExit(f"build failed:\n{r.stdout[-4000:]}\n{r.stderr[-4000:]}")
    return sorted(outdir.glob("*.whl")) + sorted(outdir.glob("*.tar.gz"))


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
        result["verify"] = {
            "second_build": second,
            "identical": first == second,
            "identical_members": all(
                describe(a).get("distinct_timestamps") == [tuple(int(x) for x in describe(a)["distinct_timestamps"][0])]
                for a in result["artifacts"]
            ),
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
