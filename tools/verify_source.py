"""Verify the frozen 14-document source package against its recorded digests."""

from __future__ import annotations

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "evidence" / "source" / "SOURCE_VERIFY.json"
FALLBACK_ROOT = Path("C:/Projects/Agent_Workspace/_sbl_src_mirror/SBL_PIPD-LS-PKG")


def _digest(path: Path) -> str:
    hasher = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _aggregate(digests: list[str]) -> str:
    joined = "\n".join(sorted(digests)) + "\n"
    return sha256(joined.encode("utf-8")).hexdigest()


def _resolve(entry: dict[str, Any]) -> Path:
    recorded = entry.get("path")
    if isinstance(recorded, str) and recorded.strip():
        candidate = Path(recorded)
        if candidate.is_file():
            return candidate
    doc = str(entry.get("doc") or "")
    return FALLBACK_ROOT / f"{doc}.md"


def verify() -> dict[str, Any]:
    record = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    docs = record.get("docs") or []
    computed: list[str] = []
    mismatches: list[dict[str, Any]] = []
    for entry in docs:
        doc = str(entry.get("doc") or "")
        path = _resolve(entry)
        if not path.is_file():
            mismatches.append(
                {"doc": doc, "reason": "missing", "path": str(path)}
            )
            continue
        actual = _digest(path)
        computed.append(actual)
        expected = str(entry.get("sha256") or "")
        if actual != expected:
            mismatches.append(
                {
                    "doc": doc,
                    "reason": "sha256",
                    "expected": expected,
                    "actual": actual,
                    "path": str(path),
                }
            )
    aggregate = _aggregate(computed) if len(computed) == len(docs) else None
    recorded_aggregate = record.get("aggregate_sha256")
    if aggregate is None or aggregate != recorded_aggregate:
        mismatches.append(
            {
                "doc": "AGGREGATE",
                "reason": "aggregate_sha256",
                "expected": recorded_aggregate,
                "actual": aggregate,
            }
        )
    return {
        "ok": not mismatches,
        "docs": len(docs),
        "aggregate_sha256": aggregate,
        "recorded_aggregate": recorded_aggregate,
        "mismatches": mismatches,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify", action="store_true", help="recompute and compare all digests"
    )
    parser.add_argument("--json-out", default=None, help="optional report path")
    args = parser.parse_args(argv)
    if not args.verify:
        parser.print_help(sys.stderr)
        return 2
    report = verify()
    text = json.dumps(report, ensure_ascii=False)
    sys.stdout.write(text + "\n")
    sys.stdout.flush()
    if args.json_out:
        target = Path(args.json_out)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
