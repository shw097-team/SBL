"""WO-S4-WEB-02: the versioned Web/ChatGPT mount pack — build, verify, refusals and UAT pins.

This module tests the *deliverable* pack and the tool that builds/verifies it:

  * positive: the pack builds into a byte-deterministic ZIP, ``--verify`` recomputes every manifest
    digest and returns PASS, and every document carries a source locator + the release identity;
  * negatives (each must be NAMED and must make verification non-zero):
      - a mutated member                  -> MUTATED_MEMBER
      - a member not listed in manifest   -> UNMANIFESTED_FILE
      - a manifest entry absent from ZIP  -> MANIFEST_ENTRY_NOT_IN_ZIP
      - a path that escapes the pack root -> ESCAPES_PACK_ROOT
  * content pins for the five-case consumer UAT (cases 1-4 as deterministic content checks, case 5
    as an extraction/navigation check), with the native-upload path recorded NOT_SUPPORTED.

The pack is authoring content; the tool is the only writer of ``dist/mount/**``. The tests never
touch the network and never write outside a temporary directory.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from tools import build_mount_pack as BMP  # noqa: E402

PACK_ROOT = ROOT / "dist" / "mount" / "pipd-ls-sp-s4-chatgpt-mount-v0.1.0-preview.2"
PACK_NAME = PACK_ROOT.name
ZIP = ROOT / "dist" / "mount" / "PIPD-LS-SP_S4_WEB_MOUNT_v0.1.0-preview.2.zip"
SIDECAR = ZIP.with_name(ZIP.name + ".sha256")
UAT = (ROOT / ".hgk" / "rounds" / "POSTRELEASE-20261011-s4-narrow-repair" / "evidence"
       / "WEB_MOUNT_UAT.json")

RELEASE_IDENTITY = "v0.1.0-preview.2"
RELEASE_TAG_COMMIT = "8faa64e581e8c25f5ec355475e29561847da3ead"
CONTENT_FILES = [
    "README_MOUNT.md",
    "PIPD_LS_SP_QUICKSTART_PROMPT.md",
    "SKILL.md",
    "references/PIPD_S4_CORE.md",
    "references/PIPD_SOURCE_MAP.md",
    "references/PIPD_8_SKILLS_INDEX.md",
    "references/PIPD_PROFILE_AND_SAFETY.md",
    "references/PIPD_EXAMPLES.md",
]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_zip(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as zf:
        return {n: zf.read(n) for n in zf.namelist()}


def _write_zip(path: Path, members: dict[str, bytes]) -> None:
    """Rewrite a zip deterministically, preserving the tool's fixed per-member stamp."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, data in members.items():
            info = zipfile.ZipInfo(name, date_time=BMP.FIXED_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 0
            zf.writestr(info, data)


class MountPackBuildTests(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.td = Path(self._td.name)

    def tearDown(self):
        self._td.cleanup()

    def _build(self, name="pack") -> Path:
        pack = self.td / PACK_NAME
        if not pack.exists():
            shutil.copytree(PACK_ROOT, pack)
        out = self.td / f"{name}.zip"
        BMP.build_pack(pack, out)
        return out

    # ------------------------------------------------------------- positive

    def test_pack_directory_has_exact_expected_files(self):
        present = {p.relative_to(PACK_ROOT).as_posix() for p in PACK_ROOT.rglob("*") if p.is_file()}
        self.assertEqual(present, set(CONTENT_FILES) | {BMP.MANIFEST_NAME})

    def test_build_is_byte_deterministic(self):
        a = self._build("a")
        b = self._build("b")
        self.assertEqual(a.read_bytes(), b.read_bytes(), "same inputs must yield identical ZIP bytes")

    def test_verify_passes_and_names_nothing(self):
        out = self._build()
        ok, problems = BMP.verify_pack(out)
        self.assertTrue(ok, problems)
        self.assertEqual(problems, [])

    def test_manifest_recomputes_from_members(self):
        out = self._build()
        members = _read_zip(out)
        manifest = members[f"{PACK_NAME}/{BMP.MANIFEST_NAME}"].decode("utf-8")
        entries = {
            rel: digest
            for digest, rel in (line.split("  ", 1) for line in manifest.splitlines() if line.strip())
        }
        self.assertEqual(set(entries), set(CONTENT_FILES))
        for rel in CONTENT_FILES:
            self.assertEqual(entries[rel], _sha256(members[f"{PACK_NAME}/{rel}"]))
        self.assertEqual(list(entries), sorted(entries))

    def test_manifest_is_last_archive_entry(self):
        out = self._build()
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
        self.assertEqual(names[-1], f"{PACK_NAME}/{BMP.MANIFEST_NAME}")
        first_entry_rel = (_read_zip(out)[f"{PACK_NAME}/{BMP.MANIFEST_NAME}"]
                           .decode("utf-8").splitlines()[0].split("  ", 1)[1])
        self.assertNotEqual(first_entry_rel, BMP.MANIFEST_NAME)

    def test_all_members_are_stamped_fixed(self):
        out = self._build()
        with zipfile.ZipFile(out) as zf:
            for info in zf.infolist():
                self.assertEqual(info.date_time, BMP.FIXED_DATE_TIME)

    # ------------------------------------------------------------ negatives

    def test_mutated_member_is_refused_and_named(self):
        out = self._build()
        members = _read_zip(out)
        target = f"{PACK_NAME}/references/PIPD_S4_CORE.md"
        members[target] = members[target] + b"\n<!-- tampered -->\n"
        _write_zip(out, members)
        ok, problems = BMP.verify_pack(out)
        self.assertFalse(ok)
        self.assertIn("MUTATED_MEMBER: references/PIPD_S4_CORE.md", problems)

    def test_member_not_in_manifest_is_refused_and_named(self):
        out = self._build()
        members = _read_zip(out)
        members[f"{PACK_NAME}/EXTRA.md"] = b"leak\n"
        _write_zip(out, members)
        ok, problems = BMP.verify_pack(out)
        self.assertFalse(ok)
        self.assertIn("UNMANIFESTED_FILE: EXTRA.md", problems)

    def test_manifest_entry_missing_from_zip_is_refused_and_named(self):
        out = self._build()
        members = _read_zip(out)
        del members[f"{PACK_NAME}/references/PIPD_EXAMPLES.md"]
        _write_zip(out, members)
        ok, problems = BMP.verify_pack(out)
        self.assertFalse(ok)
        self.assertIn("MANIFEST_ENTRY_NOT_IN_ZIP: references/PIPD_EXAMPLES.md", problems)

    def test_path_escaping_pack_root_is_refused_and_named(self):
        out = self.td / "escape.zip"
        members = _read_zip(self._build())
        members["../evil.md"] = b"escape\n"
        _write_zip(out, members)
        ok, problems = BMP.verify_pack(out)
        self.assertFalse(ok)
        self.assertIn("ESCAPES_PACK_ROOT: ../evil.md", problems)

    def test_absolute_path_is_refused(self):
        out = self.td / "abs.zip"
        members = _read_zip(self._build())
        members["/etc/evil.md"] = b"escape\n"
        _write_zip(out, members)
        ok, problems = BMP.verify_pack(out)
        self.assertFalse(ok)
        self.assertIn("ESCAPES_PACK_ROOT: /etc/evil.md", problems)

    def test_verify_nonexistent_zip_refused(self):
        ok, problems = BMP.verify_pack(self.td / "nope.zip")
        self.assertFalse(ok)
        self.assertTrue(any(p.startswith("ZIP_NOT_FOUND") for p in problems))

    # ------------------------------------------------ content requirements

    def test_every_document_carries_locator_and_release_identity(self):
        for rel in CONTENT_FILES:
            text = (PACK_ROOT / rel).read_text(encoding="utf-8")
            self.assertIn(RELEASE_IDENTITY, text, f"{rel} lacks the release identity")
            self.assertIn(RELEASE_TAG_COMMIT, text, f"{rel} lacks the tag commit")
            self.assertIn("Source Locators", text, f"{rel} lacks a source locator section")

    def test_eight_existing_skills_and_no_ninth(self):
        index = (PACK_ROOT / "references/PIPD_8_SKILLS_INDEX.md").read_text(encoding="utf-8")
        for skill in ("pipd-route-intake", "pipd-authority-source", "pipd-profile-tailor",
                      "pipd-pi-compile", "pipd-pd-bind", "pipd-execution-contract",
                      "pipd-assurance-tqaep", "pipd-package-project"):
            self.assertIn(skill, index)
        dispatcher = (PACK_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("dispatcher", dispatcher.lower())
        self.assertIn("not a ninth skill", dispatcher.lower())
        for skill in ("pipd-route-intake", "pipd-package-project"):
            self.assertIn(skill, dispatcher)

    def test_dispatcher_declares_triggers_and_non_triggers(self):
        text = (PACK_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Trigger", text)
        self.assertIn("## Non-trigger", text)
        self.assertIn("chit-chat", text)
        for code in ("NO_SOURCE_LOCATOR", "MISSING_INPUT", "UNAUTHORISED_ACTION",
                     "S5_S6_NOT_AUTHORISED", "UNKNOWN_RISK_NOT_ASSESSED"):
            self.assertIn(code, text)

    def test_readme_mount_marks_unavailable_capabilities(self):
        text = (PACK_ROOT / "README_MOUNT.md").read_text(encoding="utf-8")
        for capability in ("tool execution", "repository writing", "CLI invocation",
                           "HITL authority", "network / file access"):
            self.assertIn(capability, text, f"README_MOUNT misses capability row: {capability}")
        self.assertGreaterEqual(text.count("NOT_AVAILABLE"), 5)
        self.assertIn("Plugins", text)
        self.assertIn("Create -> Upload", text)
        self.assertIn("did not exercise", text.lower())
        self.assertIn("external executor", text.lower())

    def test_quickstart_prompt_bounds_the_role(self):
        text = (PACK_ROOT / "PIPD_LS_SP_QUICKSTART_PROMPT.md").read_text(encoding="utf-8")
        low = text.lower()
        self.assertIn("design assistant", low)
        for doc in ("SKILL.md", "PIPD_S4_CORE.md", "PIPD_SOURCE_MAP.md"):
            self.assertIn(doc, text)
        self.assertIn("executor", low)
        self.assertIn("typed refusal", low)
        self.assertIn("never fabricate", low)
        for part in ("SOURCE LOCATORS", "ACTUAL EVIDENCE", "CLAIM CEILING", "NEXT STEP"):
            self.assertIn(part, text)

    def test_pack_contains_no_obvious_secret(self):
        banned = re.compile(r"(gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
                            r"-----BEGIN [A-Z ]*PRIVATE KEY-----)")
        for rel in CONTENT_FILES:
            text = (PACK_ROOT / rel).read_text(encoding="utf-8")
            self.assertIsNone(banned.search(text), f"{rel} appears to contain a secret")

    # --------------------------------------------------- published artifact

    def test_published_zip_verifies_and_matches_sidecar(self):
        self.assertTrue(ZIP.is_file(), "the published ZIP is missing; run the build command")
        ok, problems = BMP.verify_pack(ZIP)
        self.assertTrue(ok, problems)
        digest = _sha256(ZIP.read_bytes())
        recorded = SIDECAR.read_text(encoding="utf-8").split()[0]
        self.assertEqual(digest, recorded)

    def test_uat_evidence_file_coverage(self):
        self.assertTrue(UAT.is_file(), "the UAT evidence file is missing")
        data = json.loads(UAT.read_text(encoding="utf-8"))
        cases = {c["case_id"]: c for c in data["cases"]}
        self.assertEqual(len(cases), 5)
        for cid, case in cases.items():
            for key in ("fixed_input", "expected", "observed", "raw_output", "verdict",
                        "claim_ceiling"):
                self.assertIn(key, case, f"{cid} missing {key}")
            self.assertIn(case["verdict"], ("PASS", "FAIL", "NOT_SUPPORTED"))
        for cid, case in cases.items():
            if case["verdict"] != "PASS":
                self.assertEqual(case["verdict"], "NOT_SUPPORTED", cid)
                self.assertTrue(case.get("reason"), f"{cid} needs a reason")


if __name__ == "__main__":
    unittest.main()
