#!/usr/bin/env python3
"""Deterministic lane child that ECHOES THE PROMPT IT WAS HANDED, with no model in the loop.

Why this exists (D-06, SP identity at pre-spawn): the dispatcher's SP gate prepends an identity block
to the prompt. Proving the block was built is not evidence that it reached the child, and proving the
child emitted a nonce proves only that SOME text the dispatcher liked came back. This stub closes the
gap by writing the exact argv it received to ``$HGK_STUB_PROMPT_OUT``, so a test can compare the bytes
the child actually got against the receipt's own ``prompt_sha256_after`` — a read-back, not a claim —
and, because it also prints the prompt as an assistant message, the dispatcher's existing nonce oracle
runs over the same text a real lane would see.

Contract:  ``python stub_lane_child_echo_prompt.py <codex argv...> --json <prompt>``
  * the prompt is the LAST argv element (that is where hgk-lane-dispatch.py puts it),
  * ``$HGK_STUB_PROMPT_OUT`` receives that prompt verbatim when set,
  * a usage row is appended to ``$HGK_STUB_USAGE`` (same convention as stub_lane_child.py, re-used by
    import so the two stubs can never disagree about row shape),
  * stdout carries one ``item.completed`` / ``agent_message`` item whose text IS the prompt, so the
    nonce inside an identity block is read from an assistant message exactly as for a real turn.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

import stub_lane_child as _base  # same directory: re-used so usage-row shape stays single-sourced


def prompt_from_argv(argv: list[str]) -> str:
    if "--json" in argv:
        i = argv.index("--json")
        if i + 1 < len(argv):
            return argv[i + 1]
    return argv[-1] if argv else ""


def main() -> int:
    prompt = prompt_from_argv(sys.argv)
    out = (os.environ.get("HGK_STUB_PROMPT_OUT") or "").strip()
    if out:
        p = pathlib.Path(out)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(prompt, encoding="utf-8")
    usage = _base.emit_usage(sys.argv)
    print(json.dumps({"type": "item.completed",
                      "item": {"type": "agent_message", "text": prompt}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
