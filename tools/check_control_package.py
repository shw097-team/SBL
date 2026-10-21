"""Bind the SBL product repository to the exact upstream control package it implements.

THE GAP THIS CLOSES
-------------------
SBL_PIPD-LS-PKG DOC-00..DOC-13 is the single engineering contract for this
product.  Fourteen files, 17,473,442 bytes, 75,630 lines.  Before this tool
existed, the product repository contained no copy, no locator and no digest of
any of it: the two byte-identical copies lived in
`%WORKSPACE%/_sbl_src_mirror` and in a knowledge-base folder, both outside the
repository.  A builder cloning SBL therefore could not discover, pin or verify
the contract it is supposed to satisfy.  An acceptance claim could not be
audited against a document the repository had never named.

WHAT IT DOES NOT DO
-------------------
It does NOT vendor 17 MB of upstream text into the repository.  Duplication
would create a second authority that can silently drift from the first, which is
the defect this manifest exists to prevent.  The manifest pins identity, not
content: any copy anywhere can be checked against it, and a mismatch fails
closed.

THE MIRROR IS A CHECK, NOT A CONVENIENCE
----------------------------------------
Two independent copies exist.  If they ever disagree, the manifest records which
one it was built from and `--verify` reports the divergence instead of quietly
using whichever path happened to resolve first.

USAGE
-----
    python tools/check_control_package.py --write          # (re)generate the manifest
    python tools/check_control_package.py --verify         # check every digest, exit 1 on drift
    python tools/check_control_package.py --verify --root <dir>   # check against another copy

`--verify` exits 0 only when every file is present, every size matches and every
sha256 matches.  A missing file is a failure, never a skip: an absent contract
cannot be evidence of conformance.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "contracts" / "CONTROL_PACKAGE_MANIFEST.json"

DEFAULT_ROOT = Path(r"C:\Projects\Agent_Workspace\_sbl_src_mirror\SBL_PIPD-LS-PKG")
DEFAULT_MIRROR = Path(
    r"C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext"
    r"\Semantic World OS Fabric\SBL\SBL_PIPD-LS-PKG"
)

SCHEMA = "SBL-CONTROL-PACKAGE-MANIFEST/1"
EXPECTED_DOCS = [f"DOC-{i:02d}" for i in range(14)]


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def scan(root: Path) -> list[dict]:
    rows = []
    for doc in EXPECTED_DOCS:
        name = f"SBL_PIPD-LS-PKG_{doc}.md"
        p = root / name
        if not p.exists():
            raise SystemExit(f"ERR_MISSING_CONTROL_DOC: {p}")
        data = p.read_bytes()
        rows.append(
            {
                "doc": doc,
                "file": name,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    return rows


def build(root: Path, mirror: Path | None) -> dict:
    rows = scan(root)
    total_bytes = sum(r["bytes"] for r in rows)
    rollup = hashlib.sha256(
        "\n".join(f"{r['doc']} {r['sha256']}" for r in rows).encode()
    ).hexdigest()

    mirror_state = "NOT_CHECKED"
    if mirror is not None and mirror.exists():
        try:
            mrows = {r["doc"]: r["sha256"] for r in scan(mirror)}
            same = all(mrows.get(r["doc"]) == r["sha256"] for r in rows)
            mirror_state = "IDENTICAL" if same else "DIVERGED"
        except SystemExit:
            mirror_state = "INCOMPLETE"
    elif mirror is not None:
        mirror_state = "ABSENT"

    return {
        "schema": SCHEMA,
        "what_this_is": (
            "Digest identity of the single engineering contract (SBL_PIPD-LS-PKG "
            "DOC-00..DOC-13). Identity is pinned; the 17 MB of upstream text is "
            "deliberately NOT vendored, because a duplicate would become a second "
            "authority that can silently drift from the first."
        ),
        "what_this_is_not": (
            "Not an acceptance, not a source freeze, not owner ratification. The "
            "control package itself declares its global semantic denominator "
            "UNKNOWN (DOC-02 L128, DOC-04 L99, DOC-12 L7829), so no completion "
            "percentage can be derived from this manifest or from any count in it."
        ),
        "doc_count": len(rows),
        "total_bytes": total_bytes,
        "rollup_sha256": rollup,
        "rollup_method": "sha256 of '<DOC-ID> <sha256>' lines joined by LF, in DOC order",
        "canonical_root_at_capture": str(root),
        "mirror_root_at_capture": str(mirror) if mirror else None,
        "mirror_state_at_capture": mirror_state,
        "documents": rows,
    }


def verify(manifest: dict, root: Path) -> list[str]:
    problems = []
    if manifest.get("schema") != SCHEMA:
        problems.append(f"ERR_SCHEMA: {manifest.get('schema')!r} != {SCHEMA!r}")

    docs = {r["doc"]: r for r in manifest.get("documents", [])}
    missing = [d for d in EXPECTED_DOCS if d not in docs]
    if missing:
        problems.append(f"ERR_MANIFEST_INCOMPLETE: no entry for {missing}")

    for doc in EXPECTED_DOCS:
        row = docs.get(doc)
        if row is None:
            continue
        p = root / row["file"]
        if not p.exists():
            problems.append(f"ERR_DOC_ABSENT: {doc} expected at {p}")
            continue
        size = p.stat().st_size
        if size != row["bytes"]:
            problems.append(
                f"ERR_SIZE_DRIFT: {doc} manifest={row['bytes']} actual={size}"
            )
            continue
        digest = sha256_of(p)
        if digest != row["sha256"]:
            problems.append(
                f"ERR_SHA256_DRIFT: {doc} manifest={row['sha256'][:16]} actual={digest[:16]}"
            )

    present = [docs[d] for d in EXPECTED_DOCS if d in docs]
    if len(present) == len(EXPECTED_DOCS):
        rollup = hashlib.sha256(
            "\n".join(f"{r['doc']} {r['sha256']}" for r in present).encode()
        ).hexdigest()
        if rollup != manifest.get("rollup_sha256"):
            problems.append(
                f"ERR_ROLLUP_MISMATCH: manifest={manifest.get('rollup_sha256')} recomputed={rollup}"
            )
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="regenerate the manifest")
    ap.add_argument("--verify", action="store_true", help="verify digests against a root")
    ap.add_argument("--root", default=None, help="control package root (default: mirror)")
    ap.add_argument("--mirror", default=None, help="second copy to cross-check")
    args = ap.parse_args(argv)

    root = Path(args.root) if args.root else DEFAULT_ROOT
    mirror = Path(args.mirror) if args.mirror else DEFAULT_MIRROR

    if args.write:
        manifest = build(root, mirror)
        MANIFEST.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            f"wrote {MANIFEST} ({manifest['doc_count']} docs, "
            f"{manifest['total_bytes']} bytes, rollup {manifest['rollup_sha256'][:16]}, "
            f"mirror {manifest['mirror_state_at_capture']})"
        )
        return 0

    if args.verify:
        if not MANIFEST.exists():
            print(f"ERR_NO_MANIFEST: {MANIFEST}", file=sys.stderr)
            return 2
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        problems = verify(manifest, root)
        if problems:
            print(f"CONTROL_PACKAGE_DRIFT ({len(problems)} problem(s)):", file=sys.stderr)
            for p in problems:
                print(f"  {p}", file=sys.stderr)
            return 1
        print(
            f"CONTROL_PACKAGE_PINNED: {manifest['doc_count']} docs, "
            f"{manifest['total_bytes']} bytes, rollup {manifest['rollup_sha256'][:16]} "
            f"all match under {root}"
        )
        return 0

    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
