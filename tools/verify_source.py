"""Verify the frozen 14-document source package against its recorded digests."""

from __future__ import annotations

import argparse
import json
import re
import sys
from hashlib import sha256
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "evidence" / "source" / "SOURCE_VERIFY.json"
FALLBACK_ROOT = Path("C:/Projects/Agent_Workspace/_sbl_src_mirror/SBL_PIPD-LS-PKG")

#: The control package is exactly DOC-00..DOC-13. A receipt that lists fewer documents must not
#: verify: an empty inventory used to return ok=true (VERIFY-01).
REQUIRED_DOCS = tuple(f"DOC-{i:02d}" for i in range(14))


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


def verify(record_path: Path | None = None) -> dict[str, Any]:
    record = json.loads(Path(record_path or EVIDENCE).read_text(encoding="utf-8"))
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
    present = [str(entry.get("doc") or "") for entry in docs]
    missing_docs = [d for d in REQUIRED_DOCS if d not in present]
    unexpected_docs = [d for d in present if d not in REQUIRED_DOCS]
    duplicates = sorted({d for d in present if present.count(d) > 1})
    if missing_docs or unexpected_docs or duplicates:
        mismatches.append(
            {
                "doc": "INVENTORY",
                "reason": "document_inventory",
                "missing_docs": missing_docs,
                "unexpected_docs": unexpected_docs,
                "duplicates": duplicates,
                "required_count": len(REQUIRED_DOCS),
                "actual_count": len(present),
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


def self_check(record_path: Path | None = None) -> dict[str, Any]:
    """Verify the published record without the corpus (for hosts that cannot see the source).

    This is not the byte check. It proves the record is internally consistent: the exact inventory,
    well-formed digests, and an aggregate that is really the hash of the listed per-document digests.
    A hosted CI runner has no access to the private corpus, so faking a green byte check there would
    be worse than saying plainly what was verified (external acceptance report R1, D1).
    """

    record = json.loads(Path(record_path or EVIDENCE).read_text(encoding="utf-8"))
    docs = record.get("docs") or []
    problems: list[dict[str, Any]] = []
    present = [str(entry.get("doc") or "") for entry in docs]
    missing_docs = [d for d in REQUIRED_DOCS if d not in present]
    unexpected_docs = [d for d in present if d not in REQUIRED_DOCS]
    duplicates = sorted({d for d in present if present.count(d) > 1})
    if missing_docs or unexpected_docs or duplicates:
        problems.append(
            {
                "reason": "document_inventory",
                "missing_docs": missing_docs,
                "unexpected_docs": unexpected_docs,
                "duplicates": duplicates,
            }
        )
    digests: list[str] = []
    for entry in docs:
        value = str(entry.get("sha256") or "")
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            problems.append({"reason": "malformed_sha256", "doc": str(entry.get("doc") or "")})
        digests.append(value)
    aggregate = _aggregate(digests) if all(re.fullmatch(r"[0-9a-f]{64}", d) for d in digests) else None
    recorded_aggregate = record.get("aggregate_sha256")
    if aggregate is None or aggregate != recorded_aggregate:
        problems.append(
            {"reason": "aggregate_sha256", "expected": recorded_aggregate, "actual": aggregate}
        )
    if record.get("doc_count") not in (None, len(docs)):
        problems.append(
            {"reason": "doc_count", "expected": record.get("doc_count"), "actual": len(docs)}
        )
    return {
        "ok": not problems,
        "mode": "SELF_CHECK_MANIFEST_ONLY",
        "byte_verification": "NOT_PERFORMED (no corpus on this host)",
        "docs": len(docs),
        "aggregate_sha256": aggregate,
        "recorded_aggregate": recorded_aggregate,
        "problems": problems,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify", action="store_true", help="recompute and compare all digests"
    )
    parser.add_argument(
        "--self-check",
        action="store_true",
        help="verify the published record without the corpus (manifest-only, for hosted CI)",
    )
    parser.add_argument("--json-out", default=None, help="optional report path")
    parser.add_argument(
        "--record",
        default=None,
        help="verify an alternative SOURCE_VERIFY.json (default: evidence/source/SOURCE_VERIFY.json)",
    )
    args = parser.parse_args(argv)
    if not args.verify and not args.self_check:
        parser.print_help(sys.stderr)
        return 2
    if args.self_check and not args.verify:
        report = self_check(Path(args.record) if args.record else None)
    else:
        report = verify(Path(args.record) if args.record else None)
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
