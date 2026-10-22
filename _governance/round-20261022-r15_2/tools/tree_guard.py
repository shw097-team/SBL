#!/usr/bin/env python3
"""Whole-tree two-sided digest guard.

Fixes AO-F01: the previous guard excluded the write-set directory from BOTH snapshots, so an
ADDITION (the only effect a writer produces) could never be observed. This one:
  * walks every file under each root with NO write-set exclusion,
  * records (path -> sha256, size),
  * diffs two snapshots into ADDED / REMOVED / MODIFIED,
  * and separately records `git status --porcelain` for every governed repo.

Usage:
  python tools/tree_guard.py snap  --out before.json --root <dir> [--root <dir> ...] --repo <path> ...
  python tools/tree_guard.py diff  --before before.json --after after.json --out diff.json
"""
import argparse, hashlib, json, os, subprocess, sys

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "node_modules"}
SKIP_EXT = {".pyc", ".pyo"}


def digest(root: str) -> dict:
    out = {}
    root = os.path.abspath(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if os.path.splitext(name)[1] in SKIP_EXT:
                continue
            fp = os.path.join(dirpath, name)
            try:
                h = hashlib.sha256()
                with open(fp, "rb") as fh:
                    for chunk in iter(lambda: fh.read(1 << 20), b""):
                        h.update(chunk)
                rel = os.path.relpath(fp, root).replace("\\", "/")
                out[rel] = {"sha256": h.hexdigest(), "bytes": os.path.getsize(fp)}
            except OSError as exc:
                out[os.path.relpath(fp, root).replace("\\", "/")] = {"sha256": None, "error": str(exc)}
    return out


def git_status(repo: str) -> dict:
    try:
        head = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=120).stdout.strip()
        st = subprocess.run(["git", "-C", repo, "status", "--porcelain=v1", "-uall"],
                            capture_output=True, text=True, timeout=180).stdout
        entries = [ln for ln in st.splitlines() if ln.strip()]
        return {"repo": repo, "head": head, "dirty_count": len(entries), "entries": entries[:200]}
    except Exception as exc:  # noqa: BLE001
        return {"repo": repo, "error": str(exc)}


def cmd_snap(a) -> int:
    snap = {"roots": {}, "repos": {}, "generated_utc": subprocess.run(
        ["date", "-u", "+%FT%TZ"], capture_output=True, text=True).stdout.strip()}
    for r in a.root:
        snap["roots"][os.path.abspath(r)] = digest(r)
    for r in a.repo:
        snap["repos"][os.path.abspath(r)] = git_status(r)
    total = sum(len(v) for v in snap["roots"].values())
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(snap, fh, ensure_ascii=False, indent=2)
    print(f"snap {a.out}: roots={len(a.root)} files={total} repos={len(a.repo)}")
    return 0


def cmd_diff(a) -> int:
    b = json.load(open(a.before, encoding="utf-8"))
    c = json.load(open(a.after, encoding="utf-8"))
    added, removed, modified = [], [], []
    for root, bfiles in b["roots"].items():
        cfiles = c["roots"].get(root, {})
        for p in sorted(set(cfiles) - set(bfiles)):
            added.append({"root": root, "path": p, "bytes": cfiles[p].get("bytes")})
        for p in sorted(set(bfiles) - set(cfiles)):
            removed.append({"root": root, "path": p})
        for p in sorted(set(bfiles) & set(cfiles)):
            if bfiles[p].get("sha256") != cfiles[p].get("sha256"):
                modified.append({"root": root, "path": p,
                                 "before": bfiles[p].get("sha256"), "after": cfiles[p].get("sha256")})
    repo_drift = []
    for repo, bstat in b["repos"].items():
        cstat = c["repos"].get(repo, {})
        if bstat.get("head") != cstat.get("head") or bstat.get("dirty_count") != cstat.get("dirty_count"):
            repo_drift.append({"repo": repo, "head_before": bstat.get("head"), "head_after": cstat.get("head"),
                               "dirty_before": bstat.get("dirty_count"), "dirty_after": cstat.get("dirty_count")})
    out = {"added": added, "removed": removed, "modified": modified, "repo_drift": repo_drift,
           "counts": {"added": len(added), "removed": len(removed), "modified": len(modified),
                      "repo_drift": len(repo_drift)},
           "generated_utc": c.get("generated_utc")}
    with open(a.out, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print(json.dumps(out["counts"], ensure_ascii=False))
    for x in added[:10]:
        print("  ADDED  ", os.path.basename(x["root"]), x["path"])
    for x in removed[:10]:
        print("  REMOVED", os.path.basename(x["root"]), x["path"])
    for x in modified[:10]:
        print("  MODIFIED", os.path.basename(x["root"]), x["path"])
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snap"); s.add_argument("--out", required=True)
    s.add_argument("--root", action="append", default=[]); s.add_argument("--repo", action="append", default=[])
    d = sub.add_parser("diff"); d.add_argument("--before", required=True); d.add_argument("--after", required=True)
    d.add_argument("--out", required=True)
    a = ap.parse_args()
    return cmd_snap(a) if a.cmd == "snap" else cmd_diff(a)


if __name__ == "__main__":
    sys.exit(main())
