#!/usr/bin/env python3
"""R15.2 round: source freeze + expected-hash reconciliation. READ-ONLY on sources.

Emits SOURCE_FREEZE.json into the round directory. Never writes to any source file.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone, timedelta

ROUND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SBL_KNOW = r"C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric"
SBL_DOC_DIR = os.path.join(SBL_KNOW, "SBL", "SBL_PIPD-LS-PKG")
PIPD_DOC_DIR = os.path.join(SBL_KNOW, "PIPD", "PIPD_LS")
ATT = r"C:\Users\user\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\hermes\attachments"
BUNDLE = r"C:\Projects\Agent_Workspace\知識庫\工程基座\construction-acceptance-prompt-compiler\construction-acceptance-prompt-compiler"
REPOS = {
    "SBL": r"C:\Projects\Agent_Workspace\SBL",
    "Fabric": r"C:\Projects\Agent_Workspace\Fabric",
    "HG-KSEOS": r"C:\Projects\Agent_Workspace\HG-KSEOS",
    "PIPD": r"C:\Projects\Agent_Workspace\PIPD",
}

# R15.1 §1.1 author-side manifest (bytes, sha256) for the 24 upper documents.
EXPECTED = {
    "PIPD_LS_DOC-00_2026-10-07_r2_HIGH_RETENTION_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md": (251982, "be3a672ec20aa0e6b5e0e35097fc08de749bfe7f59f827d18e38aef67dd68ea4"),
    "PIPD_LS_DOC-01_2026-10-07_r2_HIGH_RETENTION_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md": (177451, "b753f2e5cdd5598a818f8a113d57b7f815aeb3f1dfa061ce74c76bb3553ac8c7"),
    "PIPD_LS_DOC-02_2026-10-07_r2_HIGH_RETENTION_AUDIT_PATCHED_FULL_REPAIR_FULL_SUBSTANTIVE_BODY (1).md": (1306240, "a021998dd3b63015e89af1dd40e0b413744a69b872da46c6bf5f4d92f7f23d0b"),
    "PIPD_LS_DOC-03_2026-10-07_r2_AUDIT_REPAIR_FULL_SUBSTANTIVE_BODY.md": (454167, "d89d82dcd2c8603ec6b86c5ec8c40845e4594bc181adf5272bd48a3de7c88f0f"),
    "PIPD_LS_DOC-04_2026-10-07_r2_HIGH_RETENTION_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md": (181988, "fa64d84da3d747b183e4affff62f4d2fb86c80bb5075f5dd933c09b20caeddcf"),
    "PIPD_LS_DOC-05_2026-10-07_r2_HIGH_RETENTION_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md": (227894, "7b40584540c162cda6debfd09a4c04321416706acdb03a7a3c2b41383dc585f4"),
    "PIPD_LS_DOC-06_2026-10-07_r2_HIGH_RETENTION_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md": (405028, "20e44ea4dd8e53c9b0a076ce861136bbea86f52687019307f6e995cd9079d303"),
    "PIPD_LS_DOC-07_2026-10-07_r2_HIGH_RETENTION_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md": (689563, "a68dae1c3670d07bcfa3476a1e37463c534594df5cd65d8dab0dca064b5a9fc1"),
    "PIPD_LS_DOC-08_2026-10-07_r2_HIGH_RETENTION_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md": (197972, "e46caa7e440392a6cfa7a86421aead5bce8a2a229fec97b133429db6b6748e42"),
    "PIPD_LS_DOC-09_2026-10-07_r2_HIGH_RETENTION_AUDIT_PATCHED_FULL_REPAIR_FULL_SUBSTANTIVE_BODY.md": (144948, "eaf0aefe2b4711c140fc3274223d88fdc38ad4ec2b7184f756a0f2471f3b0b54"),
    "SBL_PIPD-LS-PKG_DOC-00.md": (465363, "bd9c1a85ea0cae68fa8cde617e5592fca6123f72b4caf1a9d2894167d9a82e01"),
    "SBL_PIPD-LS-PKG_DOC-01.md": (1041962, "43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f"),
    "SBL_PIPD-LS-PKG_DOC-02.md": (1148207, "4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035"),
    "SBL_PIPD-LS-PKG_DOC-03.md": (1704253, "ea69e1d3718ed86aecd74a3ebcc933960eacc30b586ab80fcb9f733037e33476"),
    "SBL_PIPD-LS-PKG_DOC-04.md": (618110, "ee90cb1c86f6f7350c11c9c962233a89b035ca41ff82c8968f7968608fc6f6e0"),
    "SBL_PIPD-LS-PKG_DOC-05.md": (2382349, "3b47a0b6224b1984a4047cf53aac5ac50615c93a560fea46e1b43d079a5d9f27"),
    "SBL_PIPD-LS-PKG_DOC-06.md": (1554880, "64ea4977dab3093301f82dc7469413cc754998fc53946467842e06d83645102b"),
    "SBL_PIPD-LS-PKG_DOC-07.md": (1265128, "a366d3783c82089c5593ffabb0704d8507632cce45622684f7a0186f2ae310f8"),
    "SBL_PIPD-LS-PKG_DOC-08.md": (925526, "c7029c1ff07abe3135d33d3abf858a5fecedd911b494cd69c16eb1ddb8158288"),
    "SBL_PIPD-LS-PKG_DOC-09.md": (904598, "6450f7c15915ec8b304f4e5fd4093ea707434db8bae9d2bb6e66c30ab6eed2e1"),
    "SBL_PIPD-LS-PKG_DOC-10.md": (1397936, "a64aa21c977334dd74d660a86377ee10c4d329aa5fde0dae25ff81a3e69e8d8f"),
    "SBL_PIPD-LS-PKG_DOC-11.md": (1831131, "12f8705d780b76f264457c194a6ff359da8d74b5d6d8c83fa245b74d2a37508e"),
    "SBL_PIPD-LS-PKG_DOC-12.md": (982931, "d1e470d82ca14319582cb8947aa52007927aa38e726249b1430804cfe8c8ca56"),
    "SBL_PIPD-LS-PKG_DOC-13.md": (1251068, "7cc0c8b17311130c875910b2548b93c28bd4e1c8ee04d300f85fc33d4c09beb1"),
}

R15_1_NAME = "SBL_HGK_FABRIC_PIPD_LS_PKG_R15_1_FULL_SUBSTANTIVE_INTEGRATED_REPAIR_REPLACEMENT_2026-10-22.md"
R15_1_EXPECTED_SHA = "8276b1bda39c323cd565fa3215f3ccbfb7219b153ee7316f11380efaeb517dcf"
R15_2_NAME = "SBL_HERMES_HGK_FABRIC_R15_2_THIN_CONSTRUCTION_ACCEPTANCE_COMMAND_2026-10-22.md"


def digest(path: str) -> dict:
    h = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
            n += len(chunk)
    with open(path, "rb") as fh:
        lines = sum(1 for _ in fh)
    return {"path": path, "bytes": n, "lines": lines, "sha256": h.hexdigest()}


def git(repo: str, *args: str) -> str:
    try:
        out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, timeout=120)
        return (out.stdout or out.stderr).strip()
    except Exception as exc:  # pragma: no cover
        return f"ERROR:{exc}"


def main() -> None:
    entries = []
    for name, (exp_bytes, exp_sha) in EXPECTED.items():
        p = os.path.join(SBL_DOC_DIR, name) if name.startswith("SBL_PIPD-LS-PKG") else os.path.join(PIPD_DOC_DIR, name)
        if not os.path.exists(p):
            entries.append({"name": name, "status": "MISSING_ON_DISK", "expected": {"bytes": exp_bytes, "sha256": exp_sha}})
            continue
        d = digest(p)
        ok = (d["bytes"] == exp_bytes and d["sha256"] == exp_sha)
        entries.append({"name": name, "status": "MATCH" if ok else "MISMATCH",
                        "observed": d, "expected": {"bytes": exp_bytes, "sha256": exp_sha}})

    r151 = os.path.join(ATT, R15_1_NAME)
    r152 = os.path.join(ATT, R15_2_NAME)
    local_r151 = os.path.join(SBL_KNOW, "SBL", R15_1_NAME)
    contractors = []
    for label, p, exp in (
        ("R15.1_attachment", r151, R15_1_EXPECTED_SHA),
        ("R15.1_local_copy", local_r151, R15_1_EXPECTED_SHA),
        ("R15.2_attachment", r152, None),
    ):
        if os.path.exists(p):
            d = digest(p)
            d.update({"name": label, "expected_sha256": exp,
                      "status": ("MATCH" if exp and d["sha256"] == exp else ("UNPINNED" if exp is None else "MISMATCH"))})
            contractors.append(d)
        else:
            contractors.append({"name": label, "status": "MISSING_ON_DISK", "path": p})

    bundle_files = [
        "construction-acceptance-prompt-compiler_SKILL.md",
        "references/source-routing.md", "references/contract-model.md",
        "references/activation-runtime.md", "references/acceptance-evidence.md",
        "references/termination-permissions.md", "references/rendering-and-antipatterns.md",
        "references/prompt-contract.schema.json", "scripts/prompt_contract_compiler.py",
        "tests/test_prompt_contract_compiler.py",
    ]
    bundle = []
    for rel in bundle_files:
        p = os.path.join(BUNDLE, rel)
        bundle.append(digest(p) if os.path.exists(p) else {"name": rel, "status": "MISSING_ON_DISK"})

    skills = []
    for label, p in (
        ("challenge-review-SKILL", os.path.join(SBL_KNOW, "SBL", "參考工程資料庫", "SKILLS_PLUGIN", "challenge-review-SKILL.md")),
        ("construction-acceptance-prompt-compiler_SKILL(bundle)", os.path.join(BUNDLE, "construction-acceptance-prompt-compiler_SKILL.md")),
    ):
        skills.append(digest(p) | {"name": label} if os.path.exists(p) else {"name": label, "status": "MISSING_ON_DISK"})

    repos = {}
    for label, path in REPOS.items():
        repos[label] = {
            "path": path,
            "head": git(path, "rev-parse", "HEAD"),
            "branch": git(path, "branch", "--show-current") or "(detached)",
            "dirty_porcelain_count": len([ln for ln in git(path, "status", "--porcelain=v1", "-uall").splitlines() if ln.strip()]),
            "toplevel": git(path, "rev-parse", "--show-toplevel"),
        }

    observed = [e for e in entries if e["status"] in ("MATCH", "MISMATCH")]
    tz = timezone(timedelta(hours=8))
    manifest = {
        "schema": "SBL_R15_2_SOURCE_FREEZE/1",
        "round": "round-20261022-r15_2",
        "generated_at": datetime.now(tz).isoformat(),
        "claim_ceiling": "SOURCE_FREEZE_LOCAL_READ_ONLY; not an Owner signature, not a Native admission",
        "counts": {
            "documents_expected": len(EXPECTED),
            "documents_match": sum(1 for e in entries if e["status"] == "MATCH"),
            "documents_mismatch": sum(1 for e in entries if e["status"] == "MISMATCH"),
            "documents_missing": sum(1 for e in entries if e["status"] == "MISSING_ON_DISK"),
        },
        "documents": entries,
        "contracts": contractors,
        "compiler_bundle": bundle,
        "skills": skills,
        "repositories": repos,
        "notes": [
            "SHA verification is byte-level against the R15.1 author-side manifest; MATCH proves identity of bytes, not that this local copy is the Owner-frozen canonical original.",
            "Repository HEAD/dirty are live Windows readback at generation time, not GitHub hints.",
        ],
    }
    out = os.path.join(ROUND, "SOURCE_FREEZE.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
    print(json.dumps(manifest["counts"], ensure_ascii=False))
    print("observed_docs", len(observed), "->", out)
    for e in entries:
        if e["status"] != "MATCH":
            print("NOT-MATCH:", e["status"], e["name"])
    for c in contractors:
        print("contract:", c.get("name"), c.get("status"))


if __name__ == "__main__":
    main()
