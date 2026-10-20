"""M1: the CI definition is itself a reviewed artefact, so it gets a regression test.

The external acceptance report (SBL-EIAR-20261020-R1, D1) found that both GitHub jobs failed with
``No module named pytest`` because the workflow installed the package and then ran pytest without
installing it. It also found a step that can only ever fail on a hosted runner, because it reads a
private path that exists only on the maker's machine. Neither can be caught by running the suite
locally, so they are asserted here against the workflow text itself.
"""

from __future__ import annotations

import re
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_ci_installs_pytest_before_it_runs_the_suite() -> None:
    text = _text()
    install = re.search(r"pip install\s+\"?pytest", text)
    assert install is not None, "CI never installs pytest, so the suite cannot run"
    run = text.find("pytest -q")
    assert run != -1, "CI never runs the suite"
    assert install.start() < run, "pytest must be installed before the suite runs"


def test_ci_never_reads_the_private_source_mirror() -> None:
    text = _text()
    assert "_sbl_src_mirror" not in text, (
        "a hosted runner cannot see the private mirror; that step can only fail there"
    )


def test_ci_verifies_the_published_manifest_where_the_corpus_is_absent() -> None:
    text = _text()
    assert "--self-check" in text, (
        "CI must verify the published source manifest, not claim a byte check it cannot perform"
    )


def test_ci_does_not_swallow_failures() -> None:
    text = _text()
    assert "continue-on-error" not in text
    assert "|| true" not in text
