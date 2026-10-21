#!/usr/bin/env python3
"""Copy the three VERIFY lane transcripts into the round evidence tree (orchestration evidence)."""

from __future__ import annotations

import glob
import json
from pathlib import Path

ROOT = Path(r"C:\Projects\Agent_Workspace\SBL\_governance\round-20261021-r5")
HGK = Path(r"C:\Projects\Agent_Workspace\HG-KSEOS")
OUT = ROOT / "20_TS05" / "VERIFICATION_ROUNDS"

ROUNDS = (
    ("var/R5-PREFLIGHT/verify_logs", "R5VERIFY0508", "50e4852"),
    ("var/R5-PREFLIGHT/verify_logs2", "R5VERIFY2ND01", "ab9a354"),
    ("var/R5-PREFLIGHT/verify_logs3", "R5VERIFY3RD01", "a6bcdd0"),
)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for rnd, (logs, nonce, sha) in enumerate(ROUNDS, 1):
        path = sorted(glob.glob(str(HGK / logs / "*stdout*")))[-1]
        text = None
        for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                item = json.loads(line).get("item") or {}
            except json.JSONDecodeError:
                continue
            if item.get("type") == "agent_message":
                text = item["text"]
        dest = OUT / f"round{rnd}_{nonce}.txt"
        dest.write_text(text or "", encoding="utf-8")
        lines = (text or "").splitlines()
        rows.append(
            {
                "round": rnd,
                "nonce": nonce,
                "reviewed_sha": sha,
                "lane": "VERIFY_SECURITY",
                "arm": "openai-codex/gpt-6.1-sol",
                "transcript": f"20_TS05/VERIFICATION_ROUNDS/{dest.name}",
                "verdict_line": lines[1] if len(lines) > 1 else None,
                "source_log": str(path),
            }
        )
    (OUT / "ROUNDS.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([{"round": r["round"], "sha": r["reviewed_sha"], "verdict": r["verdict_line"]} for r in rows], indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
