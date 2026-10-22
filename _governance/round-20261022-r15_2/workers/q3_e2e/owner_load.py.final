"""owner_load - count open work orders per owner across JSONL work-order files.

Usage: python owner_load.py <work-orders.jsonl> [more-work-orders.jsonl ...]

Several files may be given. Work orders are identified by ``id``; when the same id appears more
than once, the entry from the newest file (by modification time, ties broken by argument order)
wins. Only work orders whose status is ``open`` are counted. A malformed line is reported on
stderr and skipped rather than aborting the run.
"""

from __future__ import annotations

import json
import os
import sys

STATUS_OPEN = "open"


def read_orders(path):
    """Returns the well-formed work-order records in one JSONL file."""

    orders = []
    with open(path, "r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    "warning: {}:{}: malformed JSON line skipped ({})".format(
                        path, number, exc.msg
                    ),
                    file=sys.stderr,
                )
                continue
            if not isinstance(record, dict) or "id" not in record:
                print(
                    "warning: {}:{}: record without an id skipped".format(path, number),
                    file=sys.stderr,
                )
                continue
            orders.append(record)
    return orders


def merge_newest_wins(paths):
    """Merges the files by id, keeping the entry from the newest file."""

    merged = {}
    for path in sorted(paths, key=os.path.getmtime):
        for record in read_orders(path):
            merged[str(record["id"])] = record
    return merged


def count_open_by_owner(orders):
    """Counts open work orders per owner."""

    counts = {}
    for record in orders.values():
        if str(record.get("status", "")).strip().lower() != STATUS_OPEN:
            continue
        owner = str(record.get("owner") or "unassigned")
        counts[owner] = counts.get(owner, 0) + 1
    return counts


def main(argv=None):
    paths = [str(item) for item in (sys.argv[1:] if argv is None else argv)]
    if not paths:
        print("usage: owner_load.py <work-orders.jsonl> [more.jsonl ...]", file=sys.stderr)
        return 2
    missing = [path for path in paths if not os.path.isfile(path)]
    if missing:
        print("error: no such file: {}".format(", ".join(missing)), file=sys.stderr)
        return 2
    counts = count_open_by_owner(merge_newest_wins(paths))
    for owner in sorted(counts):
        print("{}\t{}".format(owner, counts[owner]))
    if not counts:
        print("no open work orders")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
