#!/usr/bin/env python3
"""R5 TS01 — verify the 14 DOC / 20 KP / 10 design volumes / 2 skills against R5 §11 SHA-256.

R5 §11 computed these digests from the bytes it actually read. Recomputing them here proves the
local corpus is the same corpus the acceptance report judged. A mismatch is a source-identity
finding, not something to paper over: the entry is recorded as MISMATCH with both digests.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(r"C:\Projects\Agent_Workspace\知識庫\實作相關DOC\Fabric vNext\Semantic World OS Fabric\SBL")
DOCS = ROOT / "SBL_PIPD-LS-PKG"
KP = (
    ROOT
    / "參考工程資料庫/GPTs_GENIEMAKER_設計實作/【3】GPTs_GENIEMAKER_開發實作+驗收指揮官"
    / "【2】GPTs_GENIEMAKER_開發實作+驗收指揮官_KP_Builder_ReleasePack_v2026.06.03-r2/KnowledgePack"
)
VOL = ROOT / "參考工程資料庫/GPTs_GENIEMAKER_設計實作/_10"
SKILLS = ROOT / "參考工程資料庫/SKILLS_PLUGIN"
OUT = Path(__file__).with_name("SOURCE_INTAKE.json")

EXPECTED_DOC = {
    "00": "bd9c1a85ea0cae68fa8cde617e5592fca6123f72b4caf1a9d2894167d9a82e01",
    "01": "43a0a7ed26d2adf9c2803062032019ccb6acce27cebb49af4d37c3cd4b0a3a2f",
    "02": "4ff0cda5ab00ba5f577151e5b004d2167d933e912e302c9e3529b237ccb9e035",
    "03": "ea69e1d3718ed86aecd74a3ebcc933960eacc30b586ab80fcb9f733037e33476",
    "04": "ee90cb1c86f6f7350c11c9c962233a89b035ca41ff82c8968f7968608fc6f6e0",
    "05": "3b47a0b6224b1984a4047cf53aac5ac50615c93a560fea46e1b43d079a5d9f27",
    "06": "64ea4977dab3093301f82dc7469413cc754998fc53946467842e06d83645102b",
    "07": "a366d3783c82089c5593ffabb0704d8507632cce45622684f7a0186f2ae310f8",
    "08": "c7029c1ff07abe3135d33d3abf858a5fecedd911b494cd69c16eb1ddb8158288",
    "09": "6450f7c15915ec8b304f4e5fd4093ea707434db8bae9d2bb6e66c30ab6eed2e1",
    "10": "a64aa21c977334dd74d660a86377ee10c4d329aa5fde0dae25ff81a3e69e8d8f",
    "11": "12f8705d780b76f264457c194a6ff359da8d74b5d6d8c83fa245b74d2a37508e",
    "12": "d1e470d82ca14319582cb8947aa52007927aa38e726249b1430804cfe8c8ca56",
    "13": "7cc0c8b17311130c875910b2548b93c28bd4e1c8ee04d300f85fc33d4c09beb1",
}

EXPECTED_KP = {
    "00_KNOW_INDEX.md": "5b42ababab952cb7946051baa8f99e23e560504ffb2fd35e8e38b02962917ec9",
    "01_AUTHORITY_BOUNDARY.md": "4fcbf184144d38918aa4599ee8665c8078f1992f107b6bd5e106a9b6d2e6e6a2",
    "02_OUTPUT_CONTRACT.md": "302b9eb2876fd92b090eb02b0e1c3ab22077cac18fc83381e30b2923ed2d8a0f",
    "03_INTAKE_P2E_HANDOFF.md": "f97afbe1e020d4ee9deea4ea6bf5a95e0f5aa4106e5508ab1c24a1a702aebb44",
    "04_PRODUCT_BUSINESS_RISK_ACCEPTANCE.md": "e6d357b7ecbeeb1ff972b7aae6fb7388566a73e0dfe92527f43c29c28ec81f01",
    "05_SDD_ADR_TASKSPEC.md": "97355259edde717eeaf249205c56c352506d7d1c5b18fcd434ce4cf234bfeb10",
    "06_BUILDER_CONFIG.md": "ac2357934eeca6f61684e44b1a21ebaf78998cf047ec2b4d29a54a0fc56a1ce0",
    "07_BUILDER_INSTRUCTIONS.md": "79d0bd91a4a24f0195e5148ce459256d8c05f38f75e150a5a54d6bbb264c3ee4",
    "08_KNOWLEDGE_RAG_SOURCE_TO_ANCHOR.md": "42e12f231f01e750652ca98536d81a22d31e0935f2cc9e2ccd730fb8671384c7",
    "09_OROCHI_FACTORY_ORDER.md": "578ca9310b5e7fe2ff880ce913ef24b7f6702a472a9bb347f9ace2ad6bc75403",
    "10_AGENTIC_SWE_HARNESS.md": "7773d221b1b15b7bb4bd355c337c3cfe051e6efa00e051d5e5c7c1e61c4de929",
    "11_EVIDENCE_REQUIREMENT_MATRIX.md": "577e1de7ff15f4d66aefcb8cb8ccfad678ecb68b4eb3592d2536549055be6559",
    "12_EVAL_REGRESSION_LLM_JUDGE.md": "ef8601f057f6b6a764410910257964607bd3e6baa735481a8b06dbcde7000cca",
    "13_SECURITY_PRIVACY_PROMPT_INJECTION.md": "f3b64233d0983ad60fa95c658757c15499d0eea38af98408973d33e1a5725e87",
    "14_APPS_ACTIONS_MCP_ROUTEOUT.md": "36e19f0e63555be39cb2976e819f01becf1e111d1dd737c9e0a84ee31b424934",
    "15_MEMORY_STATE_TRACE_REPLAY.md": "4d4ebb379ee732b9e9afea7f29bf60d566d4712e387c25f1dbf549178ff8503a",
    "16_RELEASE_PACKAGING_CHECKSUM_READBACK.md": "dc4e9bbca29b1053235cc624066b8d42366d66d7d1086717a9d18dda81875e0c",
    "17_UX_ONBOARDING_NO_BRAIN_FLOW.md": "f02c9507aa642910d18f90076f47a71c2db96329a4ac3303978e0068560d6155",
    "18_TT_CR_DRIFT_REGISTER.md": "b28b56aaaacb819b87ac66435963f538f99a1b061351c8748e225d6910252d6a",
    "19_KP_INDEX_CROSSWALK.md": "b0cd77297e1a57207ab41db683d14d0c8df12114315604c6da1efa81a1b9b561",
}

EXPECTED_VOL = {
    "01": "216a8cbab2c7737ab52bdc63a1dd6ba29e2d50bd4eeb25878c406eeb97b94b3a",
    "02": "8a4eb3a4412cb414f898bf0988a359c95bf07e488be5ced076611e2b6c5f3b32",
    "03": "d7a771f405c38da69ae0c13855f142d43c970d62b75dc68352a6af146c96ae7f",
    "04": "8d082e95124f8812fc4e06cb15137966073b75be6145f7426679894ecdb55c49",
    "05": "e0ed54539b374ee6a77f0b11f8ae6487f91b10944f4ac34bf778d81e9c67f3a9",
    "06": "1e0f2621576d69ee16c01cbfc32f9ae92dfe14c43e3801014ff0928851993c14",
    "07": "ead80aab9be7bbbb1e20428d15eae8030df36918b09436b8038db709a62adeb6",
    "08": "13e1f4a1299dc46622e07b3699cbc11519a1a3f9212a6460042943ec51a91fb5",
    "09": "12e6b3d827fa8642542fb5b9511fd8ca5b189acb2f2bc73febe694cf5585d900",
    "10": "d4472004a6f8cb0f084175462081bda5a53c9e87e8268eeca08aecb788727df1",
}

EXPECTED_SKILL = {
    "challenge-review-SKILL.md": "9ecd2366dc2353fc8aaf533161ae1e34abba37a80f345f5f78023325f8d26194",
    "construction-acceptance-prompt-compiler_SKILL.md": "214c7f048f7361fe0bc4a324a0c99aaaf0df4191a430b645b8a97d24620064b6",
}


def _lp(path: Path) -> Path:
    """Three KP files live past MAX_PATH; without the extended-length prefix is_file() is False."""
    text = str(path)
    if len(text) > 240 and not text.startswith("\\\\?\\"):
        return Path("\\\\?\\" + text)
    return path


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with _lp(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def row(path: Path, expected: str | None) -> dict:
    if not _lp(path).is_file():
        return {"path": str(path), "present": False, "expected": expected, "status": "MISSING"}
    actual = digest(path)
    status = "MATCH" if expected is None else ("MATCH" if actual == expected else "MISMATCH")
    return {
        "path": str(path),
        "present": True,
        "bytes": _lp(path).stat().st_size,
        "sha256": actual,
        "expected": expected,
        "status": status,
    }


def main() -> int:
    out: dict = {"round": "SBL-R5-20261021-C5", "task": "TS01", "groups": {}}

    docs = []
    for key, expected in EXPECTED_DOC.items():
        hits = sorted(DOCS.glob(f"*DOC-{key}.md"))
        docs.append(row(hits[0], expected) if hits else {"expected": expected, "status": "MISSING", "name": f"DOC-{key}"})
    out["groups"]["DOC_00_13"] = docs

    kps = [row(KP / name, expected) for name, expected in EXPECTED_KP.items()]
    out["groups"]["KP_00_19"] = kps

    vols = []
    for key, expected in EXPECTED_VOL.items():
        hits = sorted(VOL.glob(f"*vol-{key}*.md"))
        vols.append(row(hits[0], expected) if hits else {"expected": expected, "status": "MISSING", "name": f"vol-{key}"})
    out["groups"]["VOL_01_10"] = vols

    skills = []
    for name, expected in EXPECTED_SKILL.items():
        hits = list(ROOT.rglob(name))
        hits = [p for p in hits if p.is_file()]
        skills.append(row(hits[0], expected) if hits else {"expected": expected, "status": "MISSING", "name": name})
    out["groups"]["SKILLS"] = skills

    for name, rows in out["groups"].items():
        counts: dict[str, int] = {}
        for item in rows:
            counts[item["status"]] = counts.get(item["status"], 0) + 1
        out.setdefault("summary", {})[name] = {"total": len(rows), **counts}

    flat = [i for rows in out["groups"].values() for i in rows]
    out["all_match"] = all(i["status"] == "MATCH" for i in flat)
    out["total"] = len(flat)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"summary": out["summary"], "all_match": out["all_match"], "total": out["total"]}, ensure_ascii=False, indent=2))
    return 0 if out["all_match"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
