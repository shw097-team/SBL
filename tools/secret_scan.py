"""Pre-publication scrub gate for the SBL repository.

Scans every tracked file for secrets, credentials and PII shapes that must never reach a public remote.
Exit 0 = clean, exit 1 = hard findings (publication must stop), exit 2 = scanner error.

Usage: python tools/secret_scan.py [--root .] [--json-out evidence/security/SECRET_SCAN.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

HARD_RULES = [
    ("github_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("github_classic_token", re.compile(r"ghp_[A-Za-z0-9]{20,}")),
    ("aws_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private_key_block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("assigned_secret", re.compile(r"(?i)\b(?:api[_-]?key|secret|password|passwd|token)\b\s*[:=]\s*['\"][^'\"\s]{16,}['\"]")),
    ("token_file_reference_with_value", re.compile(r"GITHUB-REPO_SHW097-4\.txt\s*[:=]\s*\S{8,}")),
    ("taiwan_id", re.compile(r"\b[A-Z][12]\d{8}\b")),
    # The domain part must consume hyphens and every label, otherwise the match truncates at a
    # hyphen and an address on "example.com-<suffix>" looks like the allowed "example.com"
    # (R5-NEW-01).
    ("email_address", re.compile(r"\b[\w.+-]+@(?:[\w-]+\.)+[\w-]{2,}\b")),
]
# Allowed exceptions, applied PER RULE to the matched span. A single global substring list was
# bypassable twice over: appending "example.com" to a line hid a token (round 1), and putting the
# allowlisted text INSIDE the matched value hid it again (round 2, NEW-03). So an allowance is a
# property of the rule and of the matched value, never of the surrounding text.
ALLOW_EMAIL_DOMAINS = ("example.com", "example.invalid", "users.noreply.github.com")
# No local-part allowances. A local-part allowance is what produced the R6-NEW-01 bypass: the
# matcher truncated "alice!user" to "user", which was then "allowlisted". The domain is the only
# thing an allowance may key on.
ALLOW_PLACEHOLDER_VALUES = frozenset(
    {"<token>", "<your-token>", "<api-key>", "<redacted>", "x-access-token", "changeme"}
)


def _value_of(matched: str) -> str:
    """The right-hand side of an ``assigned_secret``-style match, unquoted.

    Split on the FIRST separator only. Splitting on the last one let a value like
    ``"xxxx=changeme"`` collapse to ``changeme`` and pass as a placeholder -- the bypass the third
    independent checker demonstrated (R3-NEW-01).
    """

    text = matched.replace("'", '"')
    cut = len(text)
    for separator in (":", "="):
        index = text.find(separator)
        if index != -1:
            cut = min(cut, index)
    return text[cut + 1 :].strip().strip('"')


def _allowed(rule: str, matched: str) -> bool:
    lowered = matched.lower()
    if rule == "email_address":
        _, _, domain = lowered.rpartition("@")
        # A domain-label boundary is required: an address on ``attackerexample.com`` must not be
        # treated as ``example.com`` (R4-NEW-01), and only the domain may carry an allowance.
        return any(
            domain == allowed or domain.endswith("." + allowed) for allowed in ALLOW_EMAIL_DOMAINS
        )
    if rule in ("assigned_secret", "token_file_reference_with_value"):
        return _value_of(lowered) in ALLOW_PLACEHOLDER_VALUES
    return False
SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "_local", "raw"}
SKIP_SUFFIXES = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".zip", ".whl", ".exe", ".dll"}
# The scanner must not scan its own receipts: a finding excerpt stored in a report would
# re-trigger on the next run and turn the gate into a self-poisoning loop.
SKIP_RELATIVE = {"evidence/security/SECRET_SCAN.json"}
MASK_KEEP = 3


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in sorted(filenames):
            path = Path(dirpath) / name
            if path.suffix.lower() in SKIP_SUFFIXES:
                continue
            # Raw model/lane transcripts are never published (see .gitignore); they are kept
            # locally with a digest manifest instead, so scanning them would only re-flag
            # superseded fixture text quoted in an old transcript.
            if path.name.startswith("attempt-") and path.parent.name == "lanes":
                continue
            yield path


def _mask(line: str) -> str:
    """Keep a short prefix so a finding is locatable without republishing the value."""
    return line[:MASK_KEEP] + "***" if len(line) > MASK_KEEP else "***"


def scan(root: Path) -> dict:
    findings = []
    scanned = 0
    for path in iter_files(root):
        if str(path.relative_to(root)).replace("\\", "/") in SKIP_RELATIVE:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:  # unreadable file is itself a finding
            findings.append({"file": str(path.relative_to(root)), "rule": "unreadable", "detail": str(exc)})
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), start=1):
            for rule, pattern in HARD_RULES:
                hit = None
                for match in pattern.finditer(line):
                    matched = match.group(0)
                    if _allowed(rule, matched):
                        continue
                    hit = match
                    break
                if hit is not None:
                    findings.append({
                        "file": str(path.relative_to(root)),
                        "line": lineno,
                        "rule": rule,
                        "excerpt": _mask(line.strip())[:120],
                    })
    return {
        "schema": "SBL-SECRET-SCAN/1",
        "root": str(root),
        "files_scanned": scanned,
        "hard_findings": len(findings),
        "findings": findings,
        "verdict": "CLEAN" if not findings else "BLOCKED",
        "rules": [r for r, _ in HARD_RULES],
        "note": "Detection only; a CLEAN verdict is a pre-publication gate, not a security audit.",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--json-out", default="")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    # A root that does not exist, or one with nothing scannable in it, measured nothing. Reporting
    # CLEAN there is a false negative on the whole gate (R5-NEW-02).
    if not root.is_dir():
        print(json.dumps({"verdict": "ERROR", "detail": "root is not a directory", "root": str(root)}, ensure_ascii=False))
        return 2
    try:
        result = scan(root)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"verdict": "ERROR", "detail": str(exc)}, ensure_ascii=False))
        return 2
    if result["files_scanned"] == 0:
        print(json.dumps({"verdict": "ERROR", "detail": "no files were scanned", "root": str(root)}, ensure_ascii=False))
        return 2
    if args.json_out:
        out = Path(args.json_out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("verdict", "files_scanned", "hard_findings")}, ensure_ascii=False))
    for f in result["findings"][:20]:
        print(f"  {f['rule']}: {f['file']}:{f.get('line', '?')} :: {f.get('excerpt', '')[:80]}")
    return 0 if result["verdict"] == "CLEAN" else 1


if __name__ == "__main__":
    sys.exit(main())
