"""Inventory ATX headings.

Contract (ts23_SCOPE.md): 1-6 hashes, then at least one space or tab, then text. The ATX closing sequence is removed. Text
is kept as written - leading and trailing whitespace trimmed, internal whitespace preserved, no Unicode normalisation. An
undecodable file exits 2 with ERR_INPUT on stderr and nothing on stdout.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HEADING = re.compile(r"^(#{1,6})[ \t]+(.*)$")
CLOSING = re.compile(r"[ \t]+#+$")


def _lines(text):
    """Split on LF, CRLF and CR only.

    str.splitlines() also splits on U+2028, U+2029, NEL, VT and FF, which would silently cut heading text in
    half even though the contract keeps text exactly as written. Those characters are content here.
    """
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def inventory(path):
    headings = []
    text = Path(path).read_text(encoding="utf-8")
    for number, line in enumerate(_lines(text), 1):
        match = HEADING.match(line)
        if not match:
            continue
        body = CLOSING.sub("", match.group(2)).strip(" 	")
        if not body:
            continue
        headings.append({"line": number, "level": len(match.group(1)), "text": body})
    return headings


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        headings = inventory(args.path)
    except OSError as exc:
        sys.stderr.write("ERR_INPUT: " + str(exc) + "\n")
        return 2
    except UnicodeError as exc:
        sys.stderr.write("ERR_INPUT: " + str(exc) + "\n")
        return 2
    print(json.dumps({"path": str(args.path.resolve()), "headings": headings}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
