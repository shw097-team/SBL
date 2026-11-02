"""POST-F01 quickstart regression: the checksum step must cover exactly what was downloaded.

The published ``v0.1.0-preview.2`` ``SHA256SUMS`` lists three assets (the wheel, the source
zip, the preview notes) while the README quickstart fetches only the wheel and ``SHA256SUMS``.
A bare ``sha256sum -c SHA256SUMS`` therefore exits non-zero with two "FAILED open or read"
lines. These tests pin the repaired contract and never touch the network:

  * every file a checksum command reads as input is a file the same block downloads;
  * the published wheel digest literal appears in both the bash and the PowerShell blocks;
  * ``pipd --root`` still precedes the subcommand everywhere it appears.
"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
README = ROOT / "README.md"

PUBLISHED_WHEEL_DIGEST = "3b59a985dc9fc1cd4c1c5ca9a7b779122459ab7cadc8f439e17063d6c934cc0c"
WHEEL = "pipd_ls_sp-0.1.1a4-py3-none-any.whl"
SHA256SUMS = "SHA256SUMS"

def _readme_text() -> str:
    return README.read_text(encoding="utf-8")


def _fenced_blocks(text: str, lang: str) -> list[str]:
    """Return the bodies of every ```lang fenced code block, in order."""
    pattern = re.compile(r"^```" + re.escape(lang) + r"[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
    return pattern.findall(text)


def _download_set(block: str) -> set[str]:
    """Files a shell block downloads: curl (any flags, incl. ``-fsSLO``) / Invoke-WebRequest /
    ``--output``. The filename is the trailing path segment of the destination."""
    names: set[str] = set()
    for line in block.splitlines():
        if line.strip().startswith("#"):
            continue
        if re.search(r"\bcurl\b", line):
            for match in re.finditer(r"\"([^\"]+)\"", line):
                names.add(Path(match.group(1)).name)
        for match in re.finditer(r"-OutFile\s+\"?([^\s\"']+)\"?", line):
            names.add(Path(match.group(1)).name)
        for match in re.finditer(r"--output[= ]\s*\"?([^\s\"']+)\"?", line):
            names.add(Path(match.group(1)).name)
    return {Path(n).name for n in names}


def _checksum_input_set(block: str) -> set[str]:
    """Files a checksum command reads as input in this block."""
    reads: set[str] = set()
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # POSIX: `... | sha256sum -c` verifies the lines piped in; the piped source file is
        # the checksum command's ONLY input, the digest-listed assets are NOT opened.
        if re.search(r"sha256sum\s+-c\s+-", line):
            for match in re.finditer(r"(\S+)\s*\|\s*sha256sum\s+-c\s+-", line):
                reads.add(Path(match.group(1)).name)
            continue
        # POSIX: `sha256sum -c <file>` opens <file>; if it is a sums file, every asset it
        # lists must itself have been downloaded.
        for match in re.finditer(r"sha256sum\s+-c\s+(\S+)", line):
            target = Path(match.group(1)).name
            if target == SHA256SUMS:
                reads |= _sums_entries(block)
            else:
                reads.add(target)
        # PowerShell: Get-FileHash -Path <file> opens <file>.
        for match in re.finditer(r"Get-FileHash\b[^\n]*?-Path\s+\"?([^\s\"']+)\"?", line):
            reads.add(Path(match.group(1)).name)
    return reads


def _sums_entries(block: str) -> set[str]:
    """Asset names referenced by the embedded published SHA256SUMS listing, if any."""
    names: set[str] = set()
    for match in re.finditer(r"^\s*[0-9a-f]{64}\s+\*?(\S+)\s*$", block, re.M):
        names.add(Path(match.group(1)).name)
    return names


class QuickstartChecksumScope(unittest.TestCase):
    def test_block_download_and_checksum_sets(self) -> None:
        text = _readme_text()
        bash_blocks = _fenced_blocks(text, "bash")
        ps_blocks = _fenced_blocks(text, "powershell")

        self.assertTrue(bash_blocks, "README has no ```bash quickstart block")
        self.assertTrue(ps_blocks, "README has no ```powershell quickstart block")

        quickstart_bash = next((b for b in bash_blocks if WHEEL in b and SHA256SUMS in b), None)
        self.assertIsNotNone(quickstart_bash, "no bash block fetches the wheel + SHA256SUMS")
        quickstart_ps = next((b for b in ps_blocks if WHEEL in b and SHA256SUMS in b), None)
        self.assertIsNotNone(quickstart_ps, "no powershell block fetches the wheel + SHA256SUMS")

        for label, block in (("bash", quickstart_bash), ("powershell", quickstart_ps)):
            with self.subTest(block=label):
                downloads = _download_set(block)
                checks = _checksum_input_set(block)
                # (a) the checksum command must cover exactly what was downloaded
                self.assertTrue(checks, f"{label}: no checksum command parsed")
                self.assertLessEqual(
                    checks,
                    downloads,
                    f"{label}: checksum reads {sorted(checks - downloads)} but the block only "
                    f"downloads {sorted(downloads)}",
                )
                self.assertIn(SHA256SUMS, downloads, f"{label}: SHA256SUMS is not downloaded")
                self.assertIn(WHEEL, downloads, f"{label}: the wheel is not downloaded")

    def test_published_digest_literal_in_both_blocks(self) -> None:
        text = _readme_text()
        bash_blocks = _fenced_blocks(text, "bash")
        ps_blocks = _fenced_blocks(text, "powershell")
        self.assertIn(PUBLISHED_WHEEL_DIGEST, text)
        self.assertTrue(
            any(PUBLISHED_WHEEL_DIGEST in b for b in bash_blocks),
            "published digest literal missing from the bash block",
        )
        self.assertTrue(
            any(PUBLISHED_WHEEL_DIGEST in b for b in ps_blocks),
            "published digest literal missing from the PowerShell block",
        )

    def test_unverified_one_line_install_is_present_and_labels_itself(self) -> None:
        text = _readme_text()
        url = (
            "https://github.com/shw097-team/PIPD-LS-SP/releases/download/"
            "v0.1.1-preview.4/pipd_ls_sp-0.1.1a4-py3-none-any.whl"
        )
        self.assertIn(f'python -m pip install "{url}"', text)
        lowered = text.lower()
        self.assertIn("no hash verification", lowered)

    def test_root_precedes_subcommand(self) -> None:
        text = _readme_text()
        for line in text.splitlines():
            stripped = line.strip()
            if "pipd --root" in stripped:
                # `--root` must be immediately followed by its value, then a subcommand.
                self.assertRegex(
                    stripped,
                    r"pipd --root \S+ \S+",
                    f"--root is not before the subcommand: {stripped!r}",
                )


class QuickstartBashFailFast(unittest.TestCase):
    """R1 (F07): the bash quickstart must fail fast and activate portably.

    On Windows ``.venv/bin/activate`` does not exist, so a bare ``. .venv/bin/activate`` exits
    non-zero while the unfailed block continues and ``pip install`` lands in the GLOBAL
    interpreter. The block must therefore (1) start with ``set -e`` so the first failing step
    aborts it, and (2) activate with a POSIX-or-Windows fallback so it never sources a
    path that does not exist on the host.
    """

    def _quickstart_bash(self) -> str:
        text = _readme_text()
        block = next(
            (b for b in _fenced_blocks(text, "bash") if WHEEL in b and SHA256SUMS in b), None)
        self.assertIsNotNone(block, "no bash block fetches the wheel + SHA256SUMS")
        return block

    def test_block_starts_with_set_e(self) -> None:
        lines = self._quickstart_bash().splitlines()
        self.assertTrue(lines, "bash quickstart block is empty")
        self.assertTrue(
            lines[0].startswith("set -e"),
            f"bash quickstart block must start with `set -e` (fail fast); first line is "
            f"{lines[0]!r}",
        )

    def test_block_activates_portably_with_windows_fallback(self) -> None:
        lines = self._quickstart_bash().splitlines()
        self.assertTrue(
            any("||" in ln and ".venv/Scripts/activate" in ln for ln in lines),
            "bash quickstart block has no line that falls back to `.venv/Scripts/activate` "
            "(the Windows layout)",
        )

    def test_no_bare_posix_only_activate(self) -> None:
        # A bare `. .venv/bin/activate` (no fallback) exits non-zero on Windows and — absent a
        # failing-fast guard — lets the block continue into a GLOBAL install.
        for line in self._quickstart_bash().splitlines():
            code = line.split("#", 1)[0]
            if ".venv/bin/activate" in code:
                self.assertIn(
                    "||",
                    code,
                    f"a POSIX-only `.venv/bin/activate` line can fail silently: {line!r}",
                )


class QuickstartPowerShellFailFast(unittest.TestCase):
    """R2 (F07, PowerShell): the PowerShell quickstart must fail fast.

    Under PowerShell ``$ErrorActionPreference = 'Stop'`` alone is NOT enough: native commands
    (``python -m venv``, ``python -m pip install``, ``pipd ...``) can exit non-zero without
    raising, so the block must ALSO guard each native step on ``$LASTEXITCODE``. These tests pin
    both halves of that contract. No network, no host interpreter — README text only.
    """

    def _quickstart_ps(self) -> str:
        text = _readme_text()
        block = next(
            (b for b in _fenced_blocks(text, "powershell") if WHEEL in b and SHA256SUMS in b), None)
        self.assertIsNotNone(block, "no powershell block fetches the wheel + SHA256SUMS")
        return block

    def _code_lines(self, block: str) -> list[str]:
        """Lines with comments stripped and blanks removed."""
        out: list[str] = []
        for line in block.splitlines():
            code = line.split("#", 1)[0].strip()
            if code:
                out.append(code)
        return out

    def test_first_code_line_sets_error_action_preference_stop(self) -> None:
        lines = self._code_lines(self._quickstart_ps())
        self.assertTrue(lines, "powershell quickstart block is empty")
        first = lines[0]
        self.assertIn(
            "$ErrorActionPreference",
            first,
            f"powershell block must set $ErrorActionPreference first (fail fast); first code "
            f"line is {first!r}",
        )
        self.assertRegex(
            first,
            r"\$ErrorActionPreference\s*=\s*['\"]Stop['\"]",
            f"powershell block must set $ErrorActionPreference to 'Stop'; first code line is "
            f"{first!r}",
        )

    def test_every_native_command_is_last_exit_code_guarded(self) -> None:
        # $ErrorActionPreference does not trap native-command failures in this host's pwsh
        # ($PSNativeCommandUseErrorActionPreference is False), so every native step must be
        # followed by an explicit `if ($LASTEXITCODE -ne 0) { throw ... }` guard. A native step
        # is any visible python/pipd invocation.
        lines = self._code_lines(self._quickstart_ps())
        native = [
            i for i, ln in enumerate(lines)
            if re.match(r"(python\b|pipd\b)", ln) and "LASTEXITCODE" not in ln
        ]
        self.assertTrue(native, "no native steps parsed from the powershell quickstart block")
        for i in native:
            nxt = lines[i + 1] if i + 1 < len(lines) else ""
            self.assertRegex(
                nxt,
                r"\$LASTEXITCODE\s+-ne\s+0",
                f"native step is not guarded on $LASTEXITCODE: {lines[i]!r} (next line {nxt!r})",
            )
            self.assertIn("throw", nxt, f"guard does not throw: {nxt!r}")


if __name__ == "__main__":
    unittest.main()
