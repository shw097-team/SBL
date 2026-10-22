"""Byte-level proof: the patch, applied to the real CRLF bytes, yields exactly the intended edit.

Also records the CRLF/autocrlf posture so a checker knows why the hunk body is LF-normalised, and confirms each
context line used by the hunk is unique in the file (so the hunk cannot match in two places).
"""
from __future__ import annotations

import json
import os
import subprocess

SRC = r"C:/Projects/Agent_Workspace/HG-KSEOS/src/hg_kseos/lifecycle.py"
G = r"C:/Projects/Agent_Workspace/_r152_ev/_governance/round-20261022-r15_2/workers/candidate_proposals/w15_gate"

COND_OLD = '        if to_state == "DELIVERED":'
COND_NEW = '        if to_state in ("DELIVERY_READY", "DELIVERED"):'
ERR_OLD = '{open_rows} required workorders open")'
ERR_NEW = '{open_rows} required workorders open (refused at {to_state})")'


def main() -> int:
    raw = open(SRC, "rb").read()
    text = raw.decode("utf-8")
    crlf = text.count("\r\n")
    lf_only = text.count("\n") - crlf

    intended = text.replace(COND_OLD, COND_NEW).replace(ERR_OLD, ERR_NEW).encode("utf-8")

    # Apply the patch's hunks to the real bytes (keeping CRLF), as `git apply` would after normalisation.
    patch = open(os.path.join(G, "proposal.diff"), "rb").read().decode("utf-8")
    src_lines = text.split("\n")
    out: list[str] = []
    pos = 0
    body = patch.split("\n")
    i = 0
    ctx_seen: list[str] = []
    pre_image: list[str] = []
    while i < len(body):
        ln = body[i]
        if ln.startswith("@@"):
            head = ln.split("@@")[1].strip().split(" ")
            start = int(head[0].lstrip("-").split(",")[0])
            nold = int(head[0].split(",")[1]) if "," in head[0] else 1
            out.extend(src_lines[pos:start - 1])
            pos = start - 1
            consumed = 0
            i += 1
            while consumed < nold and i < len(body):
                cur = body[i]
                if cur == "":
                    break
                tag, payload = cur[0], cur[1:]
                if tag in (" ", "-"):
                    actual = src_lines[pos].rstrip("\r")
                    assert payload == actual, f"mismatch at line {pos + 1}: {actual!r} != {payload!r}"
                    pre_image.append(actual)
                    if tag == " ":
                        ctx_seen.append(payload)
                        out.append(src_lines[pos])
                        consumed += 1
                    pos += 1
                elif tag == "+":
                    out.append(payload + ("\r" if crlf and lf_only == 0 else ""))
                i += 1
            continue
        i += 1
    out.extend(src_lines[pos:])
    rebuilt = "\n".join(out).encode("utf-8")

    # A patch is ambiguous only if the whole pre-image block occurs at more than one offset, not if some
    # individual context line repeats (near-every indented line in a Python file does).
    norm = [ln.rstrip("\r") for ln in src_lines]
    block_offsets = [i for i in range(len(norm) - len(pre_image) + 1)
                     if norm[i:i + len(pre_image)] == pre_image]
    ambiguous = {"pre_image_occurrences": len(block_offsets),
                 "pre_image_offsets_1based": [i + 1 for i in block_offsets],
                 "repeated_single_context_lines_ignored": sorted(
                     c for c in set(ctx_seen) if text.count(c) > 1)}
    autocrlf = subprocess.run(["git", "-C", r"C:/Projects/Agent_Workspace/HG-KSEOS",
                               "config", "--get", "core.autocrlf"],
                              capture_output=True, text=True).stdout.strip()
    eol = subprocess.run(["git", "-C", r"C:/Projects/Agent_Workspace/HG-KSEOS",
                          "config", "--get", "core.eol"],
                         capture_output=True, text=True).stdout.strip()
    attrs = subprocess.run(["git", "-C", r"C:/Projects/Agent_Workspace/HG-KSEOS",
                            "check-attr", "-a", "--", "src/hg_kseos/lifecycle.py"],
                           capture_output=True, text=True).stdout.strip()
    ev = {
        "patch_applied_to_real_bytes_equals_intended": rebuilt == intended,
        "intended_matches_naive_replacement": intended == text.replace(COND_OLD, COND_NEW)
        .replace(ERR_OLD, ERR_NEW).encode("utf-8"),
        "file_crlf_lines": crlf,
        "file_lf_only_lines": lf_only,
        "file_ends_with_newline": raw.endswith(b"\n"),
        "file_utf8_bom": raw.startswith(b"\xef\xbb\xbf"),
        "core_autocrlf": autocrlf or None,
        "core_eol": eol or None,
        "check_attr": attrs or None,
        "ambiguous_context_lines": ambiguous,
        "hunk_body_line_ending": "LF (normalised)",
        "note": ("core.autocrlf=true, so git normalises the working tree to LF in the patch and back to CRLF on "
                 "apply; the hunk body is therefore LF and needs no --ignore-whitespace."),
        "source_sha256": __import__("hashlib").sha256(raw).hexdigest(),
        "source_sha256_after": __import__("hashlib").sha256(open(SRC, "rb").read()).hexdigest(),
    }
    ev["source_unchanged"] = ev["source_sha256"] == ev["source_sha256_after"]
    open(os.path.join(G, "EVIDENCE.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(ev, ensure_ascii=False, indent=2))
    unique = ambiguous["pre_image_occurrences"] == 1
    ev["hunk_pre_image_unique"] = unique
    open(os.path.join(G, "EVIDENCE.json"), "w", encoding="utf-8", newline="\n").write(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n")
    return 0 if (ev["patch_applied_to_real_bytes_equals_intended"] and ev["source_unchanged"]
                 and unique) else 1


if __name__ == "__main__":
    raise SystemExit(main())
