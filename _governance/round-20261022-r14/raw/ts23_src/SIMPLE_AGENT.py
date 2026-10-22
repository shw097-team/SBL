"""Bounded deterministic evidence review. No LLM, no external actions, no writes.

Contract (ts23_SCOPE.md): the queue is a JSON array of paths read in order; --max-steps bounds the run; each entry records
path, exact bytes and the digest of those bytes; halt_reason is BUDGET when the step limit stopped the run and
QUEUE_EXHAUSTED when the queue ran out. A queue that is not a JSON array, or an entry that cannot be read, exits 2 with
ERR_INPUT on stderr and nothing on stdout - nothing is silently skipped.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def review(queue, max_steps=2):
    fixed = tuple(queue)
    max_steps = max(0, max_steps)   # a negative budget means review nothing, and that is BUDGET
    if not isinstance(queue, list):
        raise TypeError("queue must be a JSON array of paths")
    reviewed = []
    for index, path in enumerate(fixed):
        if index >= max_steps:
            break
        data = Path(path).read_bytes()
        reviewed.append({"path": str(path), "bytes": len(data),
                         "sha256": hashlib.sha256(data).hexdigest()})
    budget_hit = len(reviewed) < len(fixed)
    return {"steps": len(reviewed), "remaining": len(fixed) - len(reviewed),
            "reviews": reviewed,
            "halt_reason": "BUDGET" if budget_hit else "QUEUE_EXHAUSTED"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue", type=Path)
    parser.add_argument("--max-steps", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        queue = json.loads(args.queue.read_text(encoding="utf-8"))
        if not isinstance(queue, list):
            raise ValueError("queue must be a JSON array of paths")
        result = review(queue, args.max_steps)
    except (OSError, ValueError, TypeError) as exc:
        sys.stderr.write("ERR_INPUT: " + str(exc) + "\n")
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
