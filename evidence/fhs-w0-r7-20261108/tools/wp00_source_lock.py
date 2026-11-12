#!/usr/bin/env python3
"""WP-FHS-00 source lock.

Recomputes, from bytes on this machine, the 31 original source snapshots declared
in W0 r6 CH-04, the four upper design documents (L0/L1/L2/W0-skeleton) and the
control document, plus the three repository HEADs.

Nothing here is inferred: every digest is read from the file, every line count is
counted, and every mismatch is recorded rather than repaired.

Usage:  python wp00_source_lock.py --out <json>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys

KB = r"C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\FHS／FHS-MSC／SBL"
SRC = r"C:\Projects\Agent_Workspace\FHS_W1_Work_Final\FHS_W1_Work_Final\sources"
PKG = KB + r"\FHS\PIPD-LS-PKG"

# SourceID, file, bytes, lines, sha256 -- transcribed from W0 r6 CH-04 table.
DECLARED = [
    ("SBL-DOC-00", "SBL_PIPD-LS-PKG_DOC-00(1).md", 465363, 1591, "bd9c1a85ea0cae68fa8cde617e5592fca6123f72b4caf1a9d2894167d9a82e01"),
    ("SBL-DOC-01", "SBL_PIPD-LS-PKG_DOC-01(1).md", 1041962, 4938, "43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f"),
    ("SBL-DOC-02", "SBL_PIPD-LS-PKG_DOC-02(1).md", 1148207, 11084, "4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035"),
    ("SBL-DOC-03", "SBL_PIPD-LS-PKG_DOC-03(1).md", 1704253, 4851, "ea69e1d3718ed86aecd74a3ebcc933960eacc30b586ab80fcb9f733037e33476"),
    ("SBL-DOC-04", "SBL_PIPD-LS-PKG_DOC-04(1).md", 618110, 3036, "ee90cb1c86f6f7350c11c9c962233a89b035ca41ff82c8968f7968608fc6f6e0"),
    ("SBL-DOC-05", "SBL_PIPD-LS-PKG_DOC-05(1).md", 2382349, 7888, "3b47a0b6224b1984a4047cf53aac5ac50615c93a560fea46e1b43d079a5d9f27"),
    ("SBL-DOC-06", "SBL_PIPD-LS-PKG_DOC-06(1).md", 1554880, 2858, "64ea4977dab3093301f82dc7469413cc754998fc53946467842e06d83645102b"),
    ("SBL-DOC-07", "SBL_PIPD-LS-PKG_DOC-07(1).md", 1265128, 3620, "a366d3783c82089c5593ffabb0704d8507632cce45622684f7a0186f2ae310f8"),
    ("SBL-DOC-08", "SBL_PIPD-LS-PKG_DOC-08(1).md", 925526, 11139, "c7029c1ff07abe3135d33d3abf858a5fecedd911b494cd69c16eb1ddb8158288"),
    ("SBL-DOC-09", "SBL_PIPD-LS-PKG_DOC-09(1).md", 904598, 3978, "6450f7c15915ec8b304f4e5fd4093ea707434db8bae9d2bb6e66c30ab6eed2e1"),
    ("SBL-DOC-10", "SBL_PIPD-LS-PKG_DOC-10(1).md", 1397936, 3888, "a64aa21c977334dd74d660a86377ee10c4d329aa5fde0dae25ff81a3e69e8d8f"),
    ("SBL-DOC-11", "SBL_PIPD-LS-PKG_DOC-11(1).md", 1831131, 5005, "12f8705d780b76f264457c194a6ff359da8d74b5d6d8c83fa245b74d2a37508e"),
    ("SBL-DOC-12", "SBL_PIPD-LS-PKG_DOC-12(1).md", 982931, 7940, "d1e470d82ca14319582cb8947aa52007927aa38e726249b1430804cfe8c8ca56"),
    ("SBL-DOC-13", "SBL_PIPD-LS-PKG_DOC-13(1).md", 1251068, 3814, "7cc0c8b17311130c875910b2548b93c28bd4e1c8ee04d300f85fc33d4c09beb1"),
    ("FHS-BODY-00", "00_INDEX_AND_DECISION(4).md", 8236, 83, "cb4727d5b0c190aba40559f72b6989964659923eed6c27504ab62acfdc3b2635"),
    ("FHS-BODY-01", "01_PRODUCT_AUTHORITY_SPINE(4).md", 17661, 145, "e257dfcd01f2e8afeda1dd88fdd33b4ef7346bf224572e60935bf9834d25b02c"),
    ("FHS-BODY-02", "02_PIPD_LIFECYCLE_AND_TPM(4).md", 73292, 858, "c336d3d9d702834e84bc2e45037e21e6ac56fb99c7abcb3adea372d901824ea2"),
    ("FHS-BODY-03", "03_ARCHITECTURE_ABI_AND_EFFECT(4).md", 12144, 106, "58628861e63956ae31b1ac17404c093533226688f975f5fa11b9b82adecd1284"),
    ("FHS-BODY-04", "04_FABRIC_HGK_CONTROL(4).md", 16794, 120, "a7d54bdeb9129e7e1979bbc1af1944189b1054760e76424f8ffd8547a682eb1f"),
    ("FHS-BODY-05", "05_COMMANDER_GUIDE_AND_NATIVE_PLAN(3).md", 6726, 59, "ee47e07455767c063fd0700440b46d27592caea4638c39407b9af1309a2b44d5"),
    ("FHS-BODY-06", "06_FHS_EXECUTE_HERMES_RUNTIME(4).md", 16807, 117, "6bc5de0d26c8d13f4227ac9b48a66b808af0eb1108dc3012941e9c0c1ee362d5"),
    ("FHS-BODY-07", "07_ACCEPTANCE_CHALLENGE(4).md", 211405, 1370, "81a8c2f1cc4629f59829f11f87aebd14cd57f7c4dd0970d672880e90e2899741"),
    ("FHS-BODY-08", "08_TECHNOLOGY_DEFAULT_HOTSWAP(4).md", 1128554, 5900, "1df04680319796aa253256c5da9c8adea47a5601abfe17086f3598d4f0470f8d"),
    ("FHS-BODY-09", "09_SBL_DOC00_13_FULL_UPGRADE(4).md", 300559, 2198, "1a0fcbdd77998bc9beed039407b96a1163c634052583813a98193f4d49769185"),
    ("FHS-BODY-09A", "09A_R15_949_ORIGINAL_ATOMS(4).md", 1855910, 12639, "ce14d5d45ef76ded7cd60e4faec34119749c29fee31d9b6e1b78738179612410"),
    ("FHS-BODY-09B", "09B_KIND_MODE_HOST_192(4).md", 474159, 3050, "aed2234821768307d81991aa56d5ff3a98fc9b884ff79e2930f2b9c4ae8e441d"),
    ("FHS-BODY-10", "10_B1_W18_SELF_BOOTSTRAP(4).md", 7761, 76, "13b0764732bc1501e7c823b12be0d0be3a54afdaec5f77a5e90111c1947fa70a"),
    ("FHS-BODY-10A", "10A_B1_TQAEP_120_124_38(4).md", 572218, 8042, "39ffde0115cdf894806a4d3bf270046b68f8786956507480db47b2a154a8c4e1"),
    ("FHS-BODY-10B", "10B_B1_PI27_PD31(4).md", 44264, 405, "7c33e2472a6510a6c15b5b8eee2fca6dd9e4865c7ad3beb8c19d1e4618886f64"),
    ("FHS-BODY-11", "11_WORKPACKAGES_AND_DAG(4).md", 46467, 380, "6c526c991b5996c2d4f862f153fbf580d456f78b45d2a714abe11bcb9a9cc811"),
    ("FHS-BODY-12", "12_VERIFICATION_AND_DELIVERY(4).md", 15368, 153, "e4f7512a27ecbec1ce6a4569654ce33c4bf3265361a5ec141418a313fd25dd45"),
]

# Upper design documents. Declared digests are the ones the W0 r6 frontmatter binds.
UPPER = [
    ("L0", PKG + r"\藍圖\FHS_總藍圖_r4.md", "7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d"),
    ("L1", PKG + r"\藍圖\FHS_PIPD-LS-PKG_藍圖_r4.md", "cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b"),
    ("L2", PKG + r"\藍圖\FHS_PIPD-LS-PKG_全波次藍圖_r4.md", "bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37"),
    ("W0-SKELETON", PKG + r"\藍圖&skeleton\FHS_PIPD-LS-PKG_W0_藍圖_skeleton_2026-11-04_r4.md", "4f8d67fd9978f6ce67014736991b88cec2c90d9ba31229475f6556db5114622a"),
    ("W0-R6", r"C:\Projects\Agent_Workspace\FHS_W0W2_R4_20261107\writeback\W0\FHS_PIPD-LS-PKG_W0_r6.md", "69a08e7fae0404d7fc33842d66c28a21684a6d13caa6ac40ba7a269411db28d5"),
    ("W0-R5-PARENT", r"C:\Projects\Agent_Workspace\FHS_W0W2_R4_20261107\evidence\E_docs\FHS_PIPD-LS-PKG_W0_r5.md", "60b0c36e1bde6d0be1127461aa87a6bbb91dd69d6a31875d216ad8ddc88dbf0b"),
]

REPOS = [
    ("Fabric", r"C:\Projects\Agent_Workspace\worktrees\r4-fabric"),
    ("SBL", r"C:\Projects\Agent_Workspace\worktrees\r4-sbl"),
    ("HG-KSEOS", r"C:\Projects\Agent_Workspace\worktrees\r4-hgk"),
]


def digest(path: str):
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    return n, h.hexdigest()


def count_lines(path: str) -> int:
    with open(path, "rb") as fh:
        return fh.read().count(b"\n") + 1


def git(repo: str, *args: str) -> str:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True,
                          text=True, check=False).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = []
    for sid, name, dbytes, dlines, dsha in DECLARED:
        path = os.path.join(SRC, name)
        row = {"source_id": sid, "file": name, "path": path,
               "declared": {"bytes": dbytes, "lines": dlines, "sha256": dsha}}
        if not os.path.isfile(path):
            row["observed"] = None
            row["verdict"] = "SOURCE_ABSENT"
        else:
            b, s = digest(path)
            ln = count_lines(path)
            row["observed"] = {"bytes": b, "lines": ln, "sha256": s}
            ok = (b == dbytes and s == dsha)
            row["bytes_match"] = b == dbytes
            row["sha_match"] = s == dsha
            row["lines_match"] = ln == dlines
            row["verdict"] = "MATCH" if ok else "SOURCE_SHA_MISMATCH"
        rows.append(row)

    upper = []
    for name, path, declared in UPPER:
        if not os.path.isfile(path):
            upper.append({"name": name, "path": path, "verdict": "DOC_ABSENT"})
            continue
        b, s = digest(path)
        upper.append({"name": name, "path": path, "bytes": b, "sha256": s,
                      "declared_sha256": declared,
                      "verdict": "MATCH" if s == declared else "DOC_SHA_MISMATCH"})

    repos = []
    for name, path in REPOS:
        repos.append({
            "repo": name, "path": path,
            "head": git(path, "rev-parse", "HEAD"),
            "branch": git(path, "rev-parse", "--abbrev-ref", "HEAD"),
            "origin_main": git(path, "rev-parse", "origin/main"),
            "dirty_paths": len([p for p in git(path, "status", "--porcelain").splitlines() if p.strip()]),
        })

    matched = sum(1 for r in rows if r["verdict"] == "MATCH")
    report = {
        "schema": "FHS.WP00.SourceLock/1",
        "wave": "WP-FHS-00",
        "generated_at": __import__("datetime").datetime.now().astimezone().isoformat(timespec="seconds"),
        "effect": "SOURCE_READ",
        "source_dir": SRC,
        "counts": {"declared": len(rows), "match": matched,
                   "absent": sum(1 for r in rows if r["verdict"] == "SOURCE_ABSENT"),
                   "mismatch": sum(1 for r in rows if r["verdict"] == "SOURCE_SHA_MISMATCH")},
        "sources": rows,
        "upper_documents": upper,
        "repositories": repos,
        "claim_ceiling": "AUTHOR_SIDE_SNAPSHOT_VERIFIED; owner currentness NOT observed",
        "not_claimed": ["ORIGINAL_SOURCE_FREEZE", "OWNER_CURRENTNESS_CONFIRMED",
                        "ORIGINAL_READER_ACK"],
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)

    print(f"sources {matched}/{len(rows)} MATCH; absent={report['counts']['absent']} "
          f"mismatch={report['counts']['mismatch']}")
    for r in rows:
        if r["verdict"] != "MATCH":
            print("  FAIL", r["source_id"], r["verdict"],
                  (r.get("observed") or {}).get("sha256"), "vs", r["declared"]["sha256"])
    for u in upper:
        print(f"  upper {u['name']}: {u['verdict']}")
    for r in repos:
        print(f"  repo {r['repo']}: {r['branch']} {r['head'][:10]} dirty={r['dirty_paths']}")
    return 0 if (matched == len(rows) and all(u["verdict"] == "MATCH" for u in upper)) else 1


if __name__ == "__main__":
    sys.exit(main())
