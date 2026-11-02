"""WO-S4R2M-DOC-CAL-01: the front page routes a reader down one of two paths, and describes
``--root`` the way the parser actually behaves.

The README's ``## Choose your path: CLI or Skills`` section must separate the *published wheel*
(the CLI + 19 installed schemas, and nothing loaded into a web host) from the *candidate-branch
mount pack* (document consumption, not a published release asset, native load not demonstrated).
The README's ``--root`` wording must no longer claim the option *always* precedes the subcommand:
``src/pipd_ls_sp/cli.py`` adds a subcommand-local ``--root`` (``dest="sub_root"``) to ``project``
and ``export``, and the dispatcher resolves ``getattr(args, "sub_root", None) or args.root``.

These tests are the machine-checkable half of both claims. They read README text only and drive the
CLI surface (``python -m pipd_ls_sp.cli``) through ``sys.executable`` with this repository's ``src``
on ``PYTHONPATH``, so they never depend on a machine-specific interpreter path. They touch no
``src/**``, ``schemas/**`` or network.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
README = ROOT / "README.md"

ENV = {**os.environ, "PYTHONPATH": str(SRC),
       "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}


def _readme_text() -> str:
    return README.read_text(encoding="utf-8")


def _headings(text: str) -> dict[str, int]:
    """Line index of each ``## `` heading, keyed by its exact title text."""
    found: dict[str, int] = {}
    for i, line in enumerate(text.splitlines()):
        if line.startswith("## "):
            found[line[3:].strip()] = i
    return found


def _section(text: str, title: str) -> str:
    """The body of the ``## <title>`` section, up to the next ``## `` heading."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == f"## {title}":
            start = i + 1
            break
    if start is None:
        raise AssertionError(f"section {title!r} not found")
    end = len(lines)
    for j in range(start, len(lines)):
        if lines[j].startswith("## "):
            end = j
            break
    return "\n".join(lines[start:end])


def _cli(cwd: Path, *args: str) -> "subprocess.CompletedProcess[str]":
    return subprocess.run([sys.executable, "-B", "-m", "pipd_ls_sp.cli", *args],
                          cwd=str(cwd), env=ENV, capture_output=True, text=True, encoding="utf-8")


class ChooseYourPathSection(unittest.TestCase):
    """The routing heading exists, and sits between ``## Start here`` and ``## Quickstart``."""

    def test_new_heading_exists_between_start_here_and_quickstart(self) -> None:
        headings = _headings(_readme_text())
        self.assertIn("Start here", headings)
        self.assertIn("Choose your path: CLI or Skills", headings)
        self.assertIn("Quickstart", headings)
        self.assertLess(
            headings["Start here"],
            headings["Choose your path: CLI or Skills"],
            "the routing section must follow `## Start here`",
        )
        self.assertLess(
            headings["Choose your path: CLI or Skills"],
            headings["Quickstart"],
            "the routing section must precede `## Quickstart`",
        )

    def test_section_names_both_paths_and_their_artefacts(self) -> None:
        section = _section(_readme_text(), "Choose your path: CLI or Skills")
        # CLI / headless harness: the immutable published wheel + its digest.
        self.assertIn("v0.1.1-preview.4", section)
        self.assertIn("pipd_ls_sp-0.1.1a4-py3-none-any.whl", section)
        self.assertIn(
            "3b59a985dc9fc1cd4c1c5ca9a7b779122459ab7cadc8f439e17063d6c934cc0c", section)
        self.assertIn("doctor", section)
        # Skills / document consumption: the candidate-branch mount pack, not a release asset.
        self.assertIn("dist/mount/PIPD-LS-SP_S4_WEB_MOUNT_v0.1.1-preview.3.zip", section)
        self.assertIn("MANIFEST.sha256", section)

    def test_cli_path_is_not_claimed_to_load_skills_into_a_host(self) -> None:
        section = _section(_readme_text(), "Choose your path: CLI or Skills")
        self.assertRegex(
            section,
            r"does \*\*not\*\*\s+install or auto-load the eight logical skills",
            "the section must say the wheel does not load the skills into a web host",
        )
        self.assertIn("19", section)

    def test_skills_path_names_manual_route_and_does_not_assert_native_load(self) -> None:
        section = _section(_readme_text(), "Choose your path: CLI or Skills")
        # The manual / Knowledge document route must be named.
        self.assertRegex(section, r"Knowledge", "the manual/Knowledge route must be named")
        self.assertIn("SKILL.md", section)
        self.assertIn("PIPD_LS_SP_QUICKSTART_PROMPT.md", section)
        # From preview.3 the pack is genuinely a release asset of the tag, so the old "not a
        # published release asset" wording is factually superseded. The protective intent stays:
        # the pack must be named as an asset of the same tag, and native load is still unclaimed.
        self.assertIn("as a release asset of the same tag", section)
        # Native loading is explicitly NOT demonstrated.
        self.assertIn("not yet demonstrated", section)
        # ...and the section must not assert a native load as if it had been shown.
        self.assertIsNone(
            re.search(
                r"native[^.\n]*(?<!not )(?<!not yet )\b(load|upload|install)\b[^.\n]*"
                r"\b(is|was|has been)\b[^.\n]*\b(demonstrated|verified|confirmed|supported|proven)\b",
                section,
                re.I,
            ),
            "the section must not claim a native skill load was demonstrated",
        )
        # The document path does not run the CLI on the reader's machine.
        self.assertRegex(section, r"does \*\*not\*\* execute `pipd`")


class RootWordingIsTruthful(unittest.TestCase):
    """The README no longer states the absolute ``--root``-must-always-precede rule."""

    def test_no_absolute_global_must_precede_claim(self) -> None:
        text = _readme_text()
        # The old absolute phrasing: an emphasised GLOBAL paired with an unconditional rule.
        self.assertNotRegex(text, r"--root` is a \*\*GLOBAL\*\* option",
                            "the blanket `--root` is GLOBAL claim is still present")
        for line in text.splitlines():
            if re.search(r"--root", line, re.I) and re.search(r"must precede", line, re.I):
                self.assertNotRegex(
                    line, r"GLOBAL",
                    f"--root must-precede is still phrased as a blanket GLOBAL rule: {line!r}",
                )

    def test_corrected_statement_names_project_and_export_exception(self) -> None:
        text = _readme_text()
        # The corrected sentence spans several wrapped lines; take it as a region.
        m = re.search(
            r"For `init`.*?accept `--root` after the\s+subcommand",
            text,
            re.S,
        )
        self.assertIsNotNone(m, "the corrected --root sentence is missing")
        sentence = m.group(0)
        self.assertIn("additionally", sentence)
        self.assertRegex(
            sentence, r"`project` and `export`\s+\*\*additionally\*\* accept `--root`")
        for cmd in ("init", "intake", "profile", "compile-pi", "bind-pd",
                    "compile-ecp", "compile-tqaep", "validate", "doctor"):
            self.assertIn(
                f"`{cmd}`", sentence,
                f"the corrected statement must name `{cmd}` in the global-option list",
            )
        self.assertIn("`--root` is a global option", sentence)


class DocumentedRootFormsRun(unittest.TestCase):
    """The three documented positives exit 0; a refused form exits non-zero."""

    def test_three_positives_exit_zero_and_refusal_exits_nonzero(self) -> None:
        with tempfile.TemporaryDirectory(prefix="pipd_s4r2m_route_") as tmp:
            cwd = Path(tmp)  # scratch dir OUTSIDE the repository; `./demo` is relative to it
            init = _cli(cwd, "--root", "./demo", "init")
            self.assertEqual(init.returncode, 0,
                             f"`pipd --root ./demo init` failed: {init.stdout[:300]}")
            for label, args in (
                ("project", ("project", "--root", "./demo", "--dry-run")),
                ("export", ("export", "--root", "./demo", "--dry-run")),
            ):
                proc = _cli(cwd, *args)
                self.assertEqual(
                    proc.returncode, 0,
                    f"`pipd {label} --root ./demo --dry-run` failed: {proc.stdout[:300]}",
                )
            refused = _cli(cwd, "init", "--root", "./demo")
            self.assertNotEqual(
                refused.returncode, 0,
                "`pipd init --root ./demo` must be refused (init has no subcommand-local --root)",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
