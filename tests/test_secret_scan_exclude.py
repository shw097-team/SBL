"""C22: the gate must be scoped, not weakened.

``python tools/secret_scan.py`` was BLOCKED on 54 hard findings, every one of them inside
``_governance/`` (published evidence logs, a G-KNOW index, a PR-creation record, the TT register).
Those files are hashed by other rounds, so scrubbing them to buy a green would destroy evidence.
The fix is an ``--exclude`` glob that narrows *which paths* are read, never which values are
tolerated.

These three tests are the negative controls for that claim. They run entirely in ``tmp_path``: a
fixture planted in the real repo would both flag the repo and depend on it, so nothing here reads
or writes the working tree.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "tools") not in sys.path:
    sys.path.insert(0, str(REPO / "tools"))

import secret_scan  # noqa: E402  (path-managed import on purpose)

# Assembled at runtime so this file never contains a literal the scanner would flag. The local part
# is deliberately not an allowlisted domain: example.com would pass on its own merits and the test
# would then be measuring the allowlist instead of the exclusion.
PLANTED_EMAIL = "alice" + "@" + "acme-evidence-log.test"
EXCLUDE = ["_governance/**"]


def _plant(tmp_path: Path, relative: str, text: str) -> Path:
    path = tmp_path / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _rules(result: dict) -> set[str]:
    return {finding["rule"] for finding in result["findings"]}


def _files(result: dict) -> set[str]:
    """Findings report the path with the platform separator; compare on a normalised spelling."""

    return {finding["file"].replace("\\", "/") for finding in result["findings"]}


def test_a_governance_finding_is_not_reported_when_the_subtree_is_excluded(tmp_path: Path) -> None:
    _plant(tmp_path, "_governance/x.log", f"contact: {PLANTED_EMAIL}\n")

    result = secret_scan.scan(tmp_path, EXCLUDE)

    assert result["verdict"] == "CLEAN", "an excluded subtree must not contribute findings"
    assert result["hard_findings"] == 0
    assert "email_address" not in _rules(result)
    # The exclusion is reported rather than silent: a scoped receipt must be distinguishable from
    # a whole-tree one without knowing the command line that produced it.
    assert result["excluded_files"] == 1
    assert result["excludes"] == EXCLUDE


def test_the_same_finding_is_reported_when_no_exclusion_is_passed(tmp_path: Path) -> None:
    _plant(tmp_path, "_governance/x.log", f"contact: {PLANTED_EMAIL}\n")

    result = secret_scan.scan(tmp_path)  # default: no exclusions

    assert result["verdict"] == "BLOCKED", "the default gate must stay as wide as it was"
    assert "email_address" in _rules(result)
    assert result["excluded_files"] == 0
    assert result["excludes"] == []


def test_a_product_finding_is_still_reported_under_the_same_exclusion(tmp_path: Path) -> None:
    _plant(tmp_path, "_governance/x.log", f"contact: {PLANTED_EMAIL}\n")
    _plant(tmp_path, "sbl_core/x.py", f"CONTACT = {PLANTED_EMAIL!r}\n")

    result = secret_scan.scan(tmp_path, EXCLUDE)

    assert result["verdict"] == "BLOCKED", "an exclusion for one subtree must not quiet another"
    flagged = _files(result)
    assert "sbl_core/x.py" in flagged
    assert not any(name.startswith("_governance") for name in flagged)
    assert "email_address" in _rules(result)
