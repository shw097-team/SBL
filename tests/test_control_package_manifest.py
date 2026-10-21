"""The control-package manifest must fail closed, and must fail for the RIGHT reason.

The product repository pins the digest identity of SBL_PIPD-LS-PKG DOC-00..13
instead of vendoring 17 MB of upstream text, because a vendored copy becomes a
second authority that can drift from the first. That trade only works if the
manifest actually detects drift, so these tests build a synthetic 14-document
package in a temporary directory and prove three distinct failure modes:

    wrong size          -> ERR_SIZE_DRIFT
    same size, 1 byte   -> ERR_SHA256_DRIFT
    absent document     -> ERR_DOC_ABSENT

A same-length tamper is the case that matters most: a size-only check would pass
it, and a reviewer reading "14 docs, sizes match" would conclude the contract was
intact. The test asserts the sha256 path specifically, not merely a non-zero exit.

These tests never touch the real 17 MB control package, so they run on any
machine, including CI, and they cannot pass vacuously because the package happens
to be absent. unittest style, no pytest import, matching the rest of this suite.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "tools" / "check_control_package.py"
MANIFEST = REPO / "contracts" / "CONTROL_PACKAGE_MANIFEST.json"


def _make_package(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    for i in range(14):
        body = (
            f"# SBL_PIPD-LS-PKG_DOC-{i:02d}\n\nsynthetic control document {i}\n"
            + ("x" * (100 + i))
        )
        (root / f"SBL_PIPD-LS-PKG_DOC-{i:02d}.md").write_text(
            body, encoding="utf-8", newline="\n"
        )
    return root


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(TOOL), *args],
        capture_output=True,
        text=True,
        cwd=str(REPO),
        timeout=300,
    )


class ControlPackageManifestTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.mkdtemp(prefix="sbl_cp_manifest_")
        self.tmp = Path(self._tmp)
        self._saved_manifest = (
            MANIFEST.read_text(encoding="utf-8") if MANIFEST.exists() else None
        )
        self.pkg = _make_package(self.tmp / "pkg")
        out = _run("--write", "--root", str(self.pkg), "--mirror", str(self.pkg))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def tearDown(self) -> None:
        if self._saved_manifest is None:
            MANIFEST.unlink(missing_ok=True)
        else:
            MANIFEST.write_text(self._saved_manifest, encoding="utf-8", newline="\n")
        shutil.rmtree(self._tmp, ignore_errors=True)

    # ---------- positive ----------

    def test_clean_package_verifies(self) -> None:
        out = _run("--verify", "--root", str(self.pkg))
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertIn("CONTROL_PACKAGE_PINNED", out.stdout)
        self.assertIn("14 docs", out.stdout)

    def test_manifest_covers_every_doc_and_records_a_rollup(self) -> None:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["doc_count"], 14)
        docs = [r["doc"] for r in data["documents"]]
        self.assertEqual(docs, [f"DOC-{i:02d}" for i in range(14)])
        self.assertEqual(len(data["rollup_sha256"]), 64)
        self.assertEqual(
            data["total_bytes"], sum(r["bytes"] for r in data["documents"])
        )
        # the honest ceiling must travel with the pin, not be left to the reader
        self.assertIn("not", data["what_this_is_not"].lower())

    # ---------- negative: the three distinct failure modes ----------

    def test_same_length_tamper_is_caught_by_sha256(self) -> None:
        target = self.pkg / "SBL_PIPD-LS-PKG_DOC-00.md"
        original = target.read_bytes()
        mutated = bytearray(original)
        idx = len(mutated) // 2
        mutated[idx] = (mutated[idx] + 1) % 256 if mutated[idx] != 255 else mutated[idx] - 1
        target.write_bytes(bytes(mutated))
        self.assertEqual(
            target.stat().st_size, len(original), "precondition: the tamper kept the size"
        )

        out = _run("--verify", "--root", str(self.pkg))
        self.assertEqual(
            out.returncode, 1, f"a same-length tamper must fail verification: {out.stdout}"
        )
        self.assertIn(
            "ERR_SHA256_DRIFT",
            out.stderr,
            "the failure must be a digest mismatch, not a size mismatch -- otherwise "
            f"the test would pass for the wrong reason: {out.stderr}",
        )

    def test_wrong_size_is_caught(self) -> None:
        target = self.pkg / "SBL_PIPD-LS-PKG_DOC-05.md"
        target.write_text(target.read_text(encoding="utf-8") + "tampered\n", encoding="utf-8")
        out = _run("--verify", "--root", str(self.pkg))
        self.assertEqual(out.returncode, 1)
        self.assertIn("ERR_SIZE_DRIFT", out.stderr)

    def test_absent_document_is_a_failure_not_a_skip(self) -> None:
        (self.pkg / "SBL_PIPD-LS-PKG_DOC-13.md").unlink()
        out = _run("--verify", "--root", str(self.pkg))
        self.assertEqual(
            out.returncode, 1, "an absent contract document must never be skipped"
        )
        self.assertIn("ERR_DOC_ABSENT", out.stderr)

    def test_verify_without_manifest_fails_closed(self) -> None:
        MANIFEST.unlink(missing_ok=True)
        out = _run("--verify", "--root", str(self.pkg))
        self.assertEqual(out.returncode, 2)
        self.assertIn("ERR_NO_MANIFEST", out.stderr)


if __name__ == "__main__":
    unittest.main()
