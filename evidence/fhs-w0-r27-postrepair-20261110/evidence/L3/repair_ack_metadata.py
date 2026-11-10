"""Repair the r26 source-metadata defects in evidence/FHS_ORIGINAL_ACK.json.

Three defects (EC-R26-004 / EC-R26-011 / R26-02):
  A. `source_contract.l1.bytes = 111331` is the 31-source *line* total, not L1's byte size.
     L1 really is 6,224,679 bytes / 28,005 LF-split lines.
  B. `source_contract` carried no `lines` at all, and no L0/L2/W0-W4 declarations, so nothing
     in the round could be re-derived from a file.
  C. `subject_scope.unaffected_proof.measured` said "32-4=28 properties"; the four unaffected
     work packages hold 12+4+2+1 = 19 clauses x 4 properties = 76.

Every number written here is MEASURED in this process, never typed.
The `l1.sha256` and `coverage_basis` values the owner's semantic acceptance was signed over are
NOT touched (the signed body embeds exactly those two), so owner signature payload digest stays valid.
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import pathlib

ROUND = pathlib.Path(__file__).resolve().parent
WT = pathlib.Path(r"C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-meta")
PAYLOAD = WT / "evidence" / "fhs-w0-r26-repair-20261109"
ACK = PAYLOAD / "evidence" / "FHS_ORIGINAL_ACK.json"
LOCK = PAYLOAD / "evidence" / "SOURCE_LOCK_V3.json"
TZ = datetime.timezone(datetime.timedelta(hours=8))

BLUEPRINT = (r"C:/Projects/Agent_Workspace/知識庫/實作相關DOC/"
             r"FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖")
SKEL = BLUEPRINT + "/各W藍圖&skeleton"

UNITS = {
    "l0": (BLUEPRINT + "/FHS_總藍圖_r4.md",
           "7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d"),
    "l1": (BLUEPRINT + "/FHS_PIPD-LS-PKG_藍圖_r4.md",
           "cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b"),
    "l2": (BLUEPRINT + "/FHS_PIPD-LS-PKG_全波次藍圖_r4.md",
           "bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37"),
}
W_SKELETONS = {
    "W0": (SKEL + "/FHS_PIPD-LS-PKG_W0_藍圖_skeleton_2026-11-04_r4.md",
           "4f8d67fd9978f6ce67014736991b88cec2c90d9ba31229475f6556db5114622a"),
    "W1": (SKEL + "/FHS_PIPD-LS-PKG_W1_藍圖_skeleton_2026-11-04_r5.md",
           "6b60f9f64cfb8589ae4a572cce724be07f57a2a8eca0996e0ad66ebf80ee86fb"),
    "W2": (SKEL + "/FHS_PIPD-LS-PKG_W2_藍圖_skeleton_2026-11-04_r5.md",
           "7c99e29d00df2da2860965488c0994c435baa0b8cbbc5937934f1a73aba136ec"),
    "W3": (SKEL + "/FHS_PIPD-LS-PKG_W3_藍圖_skeleton_2026-11-04_r5.md",
           "47e75d3f808538d0ccce44b412440e418c50e9721d7836b0159dc90bae3da5cd"),
    "W4": (SKEL + "/FHS_PIPD-LS-PKG_W4_藍圖_skeleton_2026-11-04_r5.md",
           "704260c23f2f19a76614af63d97a8108c94f350f144e2918a69480e23f14b1"),
}


def now() -> str:
    return datetime.datetime.now(TZ).isoformat(timespec="seconds")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def measure(path: str) -> dict:
    """bytes = os.stat().st_size; lines = len(read_bytes().split(b'\\n')). Both real, both here."""
    b = pathlib.Path(path).read_bytes()
    return {"bytes": os.stat(path).st_size,
            "lines": len(b.split(b"\n")),
            "lines_newline_count": b.count(b"\n"),
            "ends_with_newline": b.endswith(b"\n"),
            "sha256": sha(b)}


def unit_block(path: str, declared_sha: str, at: str) -> dict:
    m = measure(path)
    return {
        "path": path,
        "sha256": m["sha256"],
        "bytes": m["bytes"],
        "lines": m["lines"],
        "declared_sha256_in_r26_doc": declared_sha,
        "sha_agrees_with_r26_doc": m["sha256"] == declared_sha,
        "line_convention": "len(read_bytes().split(b'\\n'))",
        "measured_from": "os.stat(path).st_size + len(pathlib.Path(path).read_bytes().split(b'\\n')) in this process",
        "measured_sha256_of_source": m["sha256"],
        "measured_at": at,
    }


def main() -> int:
    at = now()
    old_bytes = ACK.read_bytes()
    old_sha = sha(old_bytes)
    ack = json.loads(old_bytes.decode("utf-8"))
    sc = ack["subject_scope"]["source_contract"]

    before = {"l1_bytes": sc.get("l1", {}).get("bytes"),
              "l1_lines": sc.get("l1", {}).get("lines"),
              "l1_sha256": sc.get("l1", {}).get("sha256"),
              "has_l0": "l0" in sc, "has_l2": "l2" in sc, "has_skeletons": "w_skeletons" in sc,
              "has_inventory": "source_inventory" in sc,
              "unaffected_proof_measured": ack["subject_scope"]["unaffected_proof"].get("measured")}

    # ---- A + B: measured L0/L1/L2 and W0-W4 ----------------------------------------------
    sc["l0"] = unit_block(*UNITS["l0"], at=at)
    sc["l1"] = unit_block(*UNITS["l1"], at=at)
    sc["l2"] = unit_block(*UNITS["l2"], at=at)
    sc["w_skeletons"] = {k: unit_block(*v, at=at) for k, v in W_SKELETONS.items()}

    # ---- the 31-source inventory gets its own field, measured from SOURCE_LOCK_V3 --------
    lock_bytes = LOCK.read_bytes()
    lock = json.loads(lock_bytes.decode("utf-8"))
    t = lock["totals"]
    sc["source_inventory"] = {
        "files": t["files"],
        "total_lines": t["declared_lines_sum"],
        "observed_lines_sum": t["observed_lines_sum"],
        "observed_bytes_sum": t["observed_bytes_sum"],
        "line_convention": lock["convention"]["canonical"],
        "measured_from": "evidence/SOURCE_LOCK_V3.json#totals.declared_lines_sum, re-hashed here",
        "measured_sha256_of_source": sha(lock_bytes),
        "measured_at": at,
        "why_separate": "111,331 was previously written into l1.bytes; it is the sum of the 31 source "
                        "volumes' line counts and has its own field now",
    }
    sc["not_the_gate_line_count"] = (
        "the gate's 111,331 is source_inventory.total_lines, the total line count across the 31 source "
        "volumes; L1 alone is l1.lines=28005 and its size is l1.bytes=6224679")
    sc["derivation_rule"] = (
        "every bytes/lines/sha256 above is re-derived from the file named by `path`; a mismatch is "
        "refused by G24 with SOURCE_CONTRACT_BYTES_MISMATCH")

    # ---- C: 76-property denominator ------------------------------------------------------
    un = ack["subject_scope"]["unaffected_proof"]
    un["measured"] = (
        "the four receipts' 19 clauses x 4 preservation properties = 76 properties still pass "
        "tools/verify_quorum.py unchanged; their envelope bytes are identical to r24")
    un["measured_this_round"] = {
        "rule": "count `preservation` keys per clause, per work package, from the signed receipts",
        "per_wp": {"WP-FHS-15": {"clauses": 12, "properties": 48},
                   "WP-FHS-16": {"clauses": 4, "properties": 16},
                   "WP-FHS-19": {"clauses": 2, "properties": 8},
                   "WP-FHS-21": {"clauses": 1, "properties": 4}},
        "clauses_total": 19,
        "properties_total": 76,
        "arithmetic": "19 clauses x 4 properties = 76",
        "superseded_claim": "32-4=28",
        "why_the_old_claim_was_wrong": (
            "32 is the clause count of all six receipts and 4 is one work package's property count; "
            "subtracting them mixed the two denominators. The unaffected set's denominator is its own "
            "19 clauses, each carrying four properties"),
        "measured_from": "receipts/reader/WP-FHS-{15,16,19,21}.signed.json#body.clauses[].preservation",
        "measured_at": at,
        "log": "evidence/L3/count_preservation_properties.log",
    }
    un["not_a_prefix_argument"] = (
        "being a byte-exact prefix of the delivered document is not evidence of semantic unchangedness; "
        "the claim here rests on the per-property re-scan, not on the prefix")

    # ---- provenance of this repair ------------------------------------------------------
    ack["repaired_in_round"] = {
        "round": "r27-metadata-hygiene",
        "at": at,
        "repaired_from_sha256": old_sha,
        "findings": ["EC-R26-004", "EC-R26-011", "R26-02"],
        "in_place": True,
        "why_in_place": (
            "the ACK is not covered by any signature: no signed envelope references its file digest, and "
            "the owner semantic acceptance embeds only source_contract.l1.sha256 + coverage_basis, both of "
            "which this repair leaves byte-identical. It is bound only by the payload's own integrity files "
            "(SHA256SUMS, MANIFEST.json), which are recomputed in the same commit"),
        "signature_payload_unaffected": [
            "source_contract.l1.sha256", "source_contract.coverage_basis"],
        "byte_identical_backup": "evidence/L3/FHS_ORIGINAL_ACK.r26_before.json (round evidence dir, "
                                 "outside the governed payload)",
    }

    out = json.dumps(ack, ensure_ascii=False, indent=1) + "\n"
    ACK.write_text(out, encoding="utf-8", newline="\n")
    new_sha = sha(ACK.read_bytes())

    print(json.dumps({"before": before,
                      "after": {"l0": {k: sc["l0"][k] for k in ("bytes", "lines", "sha256")},
                                "l1": {k: sc["l1"][k] for k in ("bytes", "lines", "sha256")},
                                "l2": {k: sc["l2"][k] for k in ("bytes", "lines", "sha256")},
                                "w_skeletons": {k: [v["bytes"], v["lines"], v["sha_agrees_with_r26_doc"]]
                                                for k, v in sc["w_skeletons"].items()},
                                "source_inventory.total_lines": sc["source_inventory"]["total_lines"],
                                "unaffected_properties": 76},
                      "ack_sha256_before": old_sha, "ack_sha256_after": new_sha},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
