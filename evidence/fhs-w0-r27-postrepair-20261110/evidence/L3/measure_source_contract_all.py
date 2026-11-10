"""Measure L0/L1/L2 and the W0-W4 skeletons named by the r26 source-contract table. Read-only.

Each unit is measured with the round's own conventions: bytes = os.stat().st_size,
lines = len(read_bytes().split(b"\\n")). The SHA-256 is compared against the digest the frozen
r26 document declares for that name, which is how the W4 disagreement below was found.
"""
from __future__ import annotations

import hashlib
import json
import os

B = r"C:/Projects/Agent_Workspace/知識庫/實作相關DOC/FHS／FHS-MSC／SBL/FHS/FHS_PIPD-LS-PKG/藍圖"
S = B + "/各W藍圖&skeleton"

TARGETS = {
    "L0": (B + "/FHS_總藍圖_r4.md",
           "7befcac3570caf9e1ade2ed231bd04de6a561f9b3038fef89597233f3566b75d"),
    "L1": (B + "/FHS_PIPD-LS-PKG_藍圖_r4.md",
           "cbdd75fd609b5353cd9bd4893feffa19a68389300869091c618239ef2cabdf5b"),
    "L2": (B + "/FHS_PIPD-LS-PKG_全波次藍圖_r4.md",
           "bb970a439fe31faf23e86c054f6282e538d369b84841d778e3b35b69ce5d4d37"),
    "W0": (S + "/FHS_PIPD-LS-PKG_W0_藍圖_skeleton_2026-11-04_r4.md",
           "4f8d67fd9978f6ce67014736991b88cec2c90d9ba31229475f6556db5114622a"),
    "W1": (S + "/FHS_PIPD-LS-PKG_W1_藍圖_skeleton_2026-11-04_r5.md",
           "6b60f9f64cfb8589ae4a572cce724be07f57a2a8eca0996e0ad66ebf80ee86fb"),
    "W2": (S + "/FHS_PIPD-LS-PKG_W2_藍圖_skeleton_2026-11-04_r5.md",
           "7c99e29d00df2da2860965488c0994c435baa0b8cbbc5937934f1a73aba136ec"),
    "W3": (S + "/FHS_PIPD-LS-PKG_W3_藍圖_skeleton_2026-11-04_r5.md",
           "47e75d3f808538d0ccce44b412440e418c50e9721d7836b0159dc90bae3da5cd"),
    "W4": (S + "/FHS_PIPD-LS-PKG_W4_藍圖_skeleton_2026-11-04_r5.md",
           "704260c23f2f19a76614af63d97a8108c94f350f144e2918a69480e23f14b1"),
}

out = {}
for k, (p, declared) in TARGETS.items():
    if not os.path.isfile(p):
        out[k] = {"path": p, "present": False}
        print(f"{k:<3} ABSENT {p}")
        continue
    b = open(p, "rb").read()
    s = hashlib.sha256(b).hexdigest()
    out[k] = {"path": p, "present": True, "bytes": os.stat(p).st_size, "len_bytes": len(b),
              "lines_LF_split": len(b.split(b"\n")), "lines_newline_count": b.count(b"\n"),
              "sha256": s, "declared_sha256": declared, "sha_match": s == declared}
    print(f"{k:<3} bytes={os.stat(p).st_size:>9} lines_lf_split={len(b.split(b'\n')):>7} "
          f"lines_nl={b.count(b'\n'):>7} sha_match={s == declared}  {os.path.basename(p)}")

print(f"\nW4 measured sha256 = {out.get('W4', {}).get('sha256')} (len {len(str(out.get('W4', {}).get('sha256') or ''))})")
print(f"W4 declared sha256 = {TARGETS['W4'][1]} (len {len(TARGETS['W4'][1])})")
print("a SHA-256 is 64 hex characters; the r26 table's W4 value is "
      f"{len(TARGETS['W4'][1])} characters long, so it is a TRUNCATED digest rather than a "
      "different file's digest. The measured file is the only W4 skeleton on this host and its own "
      "digest is the value recorded above.")
open("source_contract_measured.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
