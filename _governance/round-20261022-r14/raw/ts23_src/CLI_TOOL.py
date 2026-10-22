"""Read-only byte and line-terminator census.

The contract is written in ts23_SCOPE.md. Two rules drive this file: the input is read as BYTES (never decoded), and an
input error exits 2 with ERR_INPUT on stderr and nothing on stdout.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def census(path):
    data = path.read_bytes()
    terminators = data.count(b"\n") + data.count(b"\r") - data.count(b"\r\n")
    return {"path": str(path.resolve()), "bytes": len(data), "newlines": terminators,
            "sha256": hashlib.sha256(data).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        result = census(args.path)
    except OSError as exc:
        sys.stderr.write("ERR_INPUT: " + str(exc) + "\n")
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
