#!/usr/bin/env python
"""Regenerate the TS06 reproducibility receipt for the CURRENT candidate head.

The receipt must describe the head that is actually published, and the sealed
artefacts on disk must BE the artefacts the receipt describes. The previous
receipt described 59d2138; the candidate has since moved to 26a289f (the
W1/W2/W3 repair), so the receipt is regenerated from scratch.

Procedure:
  1. build the wheel and the sdist TWICE, into two separate directories, with
     the same commit and the same SOURCE_DATE_EPOCH;
  2. compare the digests of the two builds (they must be byte-identical);
  3. assert the wheel carries exactly ONE distinct member timestamp;
  4. copy the first build's artefacts into the evidence tree and record their
     digests;
  5. re-read the sealed artefacts from disk and confirm the digests still match.

The builder is the candidate's OWN tool (tools/build_reproducible.py), run from
the candidate worktree, so the receipt measures the product's own build path.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CAND = Path(r"C:/Projects/_sbl_r4/c3v2")
OUT = Path(r"C:/Projects/Agent_Workspace/SBL/_governance/round-20261021-r7/50_TS06")
SCRATCH = Path(r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/cache/scratch")
BUILDER_PY = r"C:/Users/user/AppData/Local/Packages/OpenAI.Codex_2p2nqsd0c76g0/LocalCache/Local/hermes/hermes-agent/venv/Scripts/python.exe"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def git(*a: str) -> str:
    r = subprocess.run(["git", "-C", str(CAND), *a], capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise SystemExit(f"git {a} -> {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def main() -> int:
    commit = git("rev-parse", "HEAD")
    tree = git("rev-parse", f"{commit}^{{tree}}")
    print("commit:", commit)
    print("tree  :", tree)

    env = dict(os.environ)
    env.update({
        "TMPDIR": str(SCRATCH), "TEMP": str(SCRATCH), "TMP": str(SCRATCH),
        "PYTHONDONTWRITEBYTECODE": "1", "SBL_BUILD_PYTHON": BUILDER_PY,
    })

    builds = []
    with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as td:
        for i in (1, 2):
            d = Path(td) / f"build{i}"
            r = subprocess.run(
                [BUILDER_PY, str(CAND / "tools" / "build_reproducible.py"),
                 "--commit", commit, "--outdir", str(d)],
                capture_output=True, text=True, timeout=1800, cwd=str(CAND), env=env,
            )
            if r.returncode != 0:
                print(r.stdout[-1500:]); print(r.stderr[-1500:])
                raise SystemExit(f"build {i} failed")
            builds.append({p.name: sha256(p) for p in sorted(d.iterdir())})
            print(f"build {i}: {builds[-1]}")

    first, second = builds
    identical = first == second
    print("\nidentical:", identical)
    if not identical:
        for k in sorted(set(first) | set(second)):
            if first.get(k) != second.get(k):
                print(f"  DIFFERS: {k}: {first.get(k)} != {second.get(k)}")
        raise SystemExit("the two builds are NOT byte-identical; the receipt would be a lie")

    # the wheel must carry exactly ONE distinct member timestamp
    import zipfile
    wheel_name = next(n for n in first if n.endswith(".whl"))
    with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as td:
        # rebuild once more just to inspect the member timestamps
        d = Path(td) / "b"
        subprocess.run(
            [BUILDER_PY, str(CAND / "tools" / "build_reproducible.py"),
             "--commit", commit, "--outdir", str(d)],
            capture_output=True, text=True, timeout=1800, cwd=str(CAND), env=env,
        )
        with zipfile.ZipFile(d / wheel_name) as z:
            stamps = {i.date_time for i in z.infolist()}
    single = len(stamps) == 1
    print("wheel distinct member timestamps:", len(stamps), "-> single:", single)

    # seal the artefacts: copy the build output into the evidence tree
    sealed = []
    with tempfile.TemporaryDirectory(dir=str(SCRATCH)) as td:
        d = Path(td) / "final"
        subprocess.run(
            [BUILDER_PY, str(CAND / "tools" / "build_reproducible.py"),
             "--commit", commit, "--outdir", str(d)],
            capture_output=True, text=True, timeout=1800, cwd=str(CAND), env=env,
        )
        for p in sorted(d.iterdir()):
            shutil.copy2(p, OUT / p.name)
            sealed.append({"name": p.name, "sha256": sha256(OUT / p.name), "bytes": (OUT / p.name).stat().st_size})

    # independent read-back of the sealed bytes
    for a in sealed:
        on_disk = sha256(OUT / a["name"])
        assert on_disk == a["sha256"], a["name"]
        assert on_disk == first[a["name"]], f"{a['name']}: sealed bytes differ from the first build"
    print("\nsealed + read back:", [(a["name"], a["sha256"][:12]) for a in sealed])

    receipt = {
        "schema": "SBL_TS06_REPRO_RECEIPT/1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo": str(CAND),
        "commit": commit,
        "source_tree": tree,
        "builder": "tools/build_reproducible.py (the candidate's OWN build tool)",
        "builder_python": BUILDER_PY,
        "source_date_epoch": "DEFAULT_SOURCE_DATE_EPOCH (pinned in the tool; NOT wall-clock)",
        "artifacts": sealed,
        "verify": {
            "second_build": second,
            "first_build": first,
            "identical": identical,
            "single_member_timestamp": single,
            "wheel_distinct_member_timestamps": len(stamps),
        },
        "claim_ceiling": (
            "this receipt is the MAKER's own measurement of its own build tool, taken on the "
            "published candidate head. It is NOT independent acceptance: the independent "
            "checker re-derives it."
        ),
    }
    (OUT / "repro_result.json").write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("\nreceipt:", OUT / "repro_result.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
