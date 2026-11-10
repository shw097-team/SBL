"""Record the one source-contract disagreement this lane measured, inside the ACK itself.

`FHS_PIPD-LS-PKG_W0_r26.md` §"資料與技術來源基線" declares for W4 the value
`704260c23f2f19a76614af63d97a8108c94f350f144e2918a69480e23f14b1`, which is 62 hex characters.
A SHA-256 is 64. The only W4 skeleton file on this host hashes to the 64-character value that differs
from it at the truncation point, so the table carries a truncated digest, not another file's digest.

The frozen r26 document is not edited. The ACK states the measurement and names who owns the text.
"""
from __future__ import annotations

import hashlib
import json
import pathlib

ACK = pathlib.Path(r"C:/Projects/Agent_Workspace/FHS_R26_WT/sbl-meta/evidence/"
                   r"fhs-w0-r26-repair-20261109/evidence/FHS_ORIGINAL_ACK.json")


def main() -> int:
    before = hashlib.sha256(ACK.read_bytes()).hexdigest()
    ack = json.loads(ACK.read_text(encoding="utf-8"))
    sc = ack["subject_scope"]["source_contract"]
    w4 = sc["w_skeletons"]["W4"]
    declared = w4["declared_sha256_in_r26_doc"]
    w4["declared_sha256_length"] = len(declared)
    w4["declared_sha256_is_a_sha256"] = len(declared) == 64
    w4["disagreement"] = (
        f"the r26 baseline table declares {len(declared)} hex characters for W4; a SHA-256 is 64. The "
        "measured file's 64-character digest differs from it only after the truncation point, so the "
        "table value is a truncated digest, not a digest of a different file")
    sc["source_contract_disagreements"] = [{
        "unit": "W4",
        "class": "DECLARED_DIGEST_TRUNCATED",
        "declared": declared,
        "declared_length": len(declared),
        "measured_sha256": w4["sha256"],
        "measured_length": len(w4["sha256"]),
        "measured_from": "evidence/L3/measure_source_contract_all.log",
        "owner_of_the_text": "the frozen r26 document (doc/FHS_PIPD-LS-PKG_W0_r26.md), which this "
                            "lane does not edit; the correction belongs to the r27 document lane",
        "gate_behaviour": "G24 re-derives bytes/lines/sha256 from the file against the ACK's own "
                          "`sha256` field (the measured value), so a truncated value quoted from the "
                          "frozen table is recorded here rather than turning the gate red on a "
                          "document this lane may not change",
    }]
    ACK.write_text(json.dumps(ack, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"ack_sha256_before": before,
                      "ack_sha256_after": hashlib.sha256(ACK.read_bytes()).hexdigest(),
                      "W4": {k: w4[k] for k in ("declared_sha256_length", "declared_sha256_is_a_sha256",
                                                "sha_agrees_with_r26_doc")}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
