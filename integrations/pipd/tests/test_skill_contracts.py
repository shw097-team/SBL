"""FW-03: exercise the real discover/load/route executable, not donor files."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
NAMES = {'pipd-route-intake', 'pipd-authority-source', 'pipd-profile-tailor',
         'pipd-pi-compile', 'pipd-pd-bind', 'pipd-execution-contract',
         'pipd-assurance-tqaep', 'pipd-package-project'}


class SkillContracts(unittest.TestCase):
    def run_check(self, skills=None):
        cmd = [sys.executable, '-B', str(ROOT / 'tools/skill_pack_check.py'), '--all']
        if skills is not None:
            cmd += ['--skills-root', str(skills)]
        result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertTrue(result.stdout.strip(), result.stderr)
        return result.returncode, json.loads(result.stdout)

    def test_exact_eight_discover_load_route(self):
        self.assertTrue((ROOT / 'tools/skill_pack_check.py').is_file(),
                        'FW-03 checker is not materialised')
        rc, result = self.run_check()
        self.assertEqual(rc, 0, result)
        self.assertEqual(result['state'], 'PASS')
        self.assertEqual(result['discovered'], 8)
        self.assertEqual(result['loaded'], 8)
        self.assertEqual(result['routed'], 8)
        self.assertEqual({row['name'] for row in result['skills']}, NAMES)
        self.assertEqual(result['cases_passed'], result['cases_run'])
        for row in result['skills']:
            self.assertEqual(set(row['case_kinds']), {'POS', 'NEG', 'EDGE', 'SEC'})
            self.assertGreaterEqual(row['roundtrips'], 2)

    # ---------------------------------------------------------------- refusal gates
    def _skills_copy(self, td):
        skills = Path(td) / 'skills'
        shutil.copytree(ROOT / 'skills', skills)
        return skills

    def _assert_refused(self, skills, expected_code):
        rc, result = self.run_check(skills=skills)
        self.assertNotEqual(rc, 0, f'{expected_code} must exit non-zero')
        self.assertEqual(result['state'], 'REFUSED', result)
        codes = [r['code'] for r in result['refusals']]
        self.assertIn(expected_code, codes, result['refusals'])
        self.assertEqual(result['first_failing_invariant'], expected_code, result['refusals'])
        return result

    def test_marker_only_pack_is_refused(self):
        # a directory holding only a free-text file is NOT a skill (PGK-07's donor stand-in)
        with tempfile.TemporaryDirectory() as td:
            skills = self._skills_copy(td)
            pack = skills / 'pipd-pd-bind'
            shutil.rmtree(pack)
            pack.mkdir()
            (pack / 'NOTES.md').write_text(
                'placeholder from PGK-07; five OpenSpec donor files were used instead\n',
                encoding='utf-8', newline='')
            result = self._assert_refused(skills, 'MARKER_ONLY_PACK')
            self.assertTrue(any('free-text' in r['reason'] for r in result['refusals']))

    def test_missing_input_schema_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self._skills_copy(td)
            (skills / 'pipd-pi-compile' / 'schemas' / 'input.schema.json').unlink()
            self._assert_refused(skills, 'MISSING_SCHEMA')

    def test_missing_output_schema_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self._skills_copy(td)
            (skills / 'pipd-assurance-tqaep' / 'schemas' / 'output.schema.json').unlink()
            self._assert_refused(skills, 'MISSING_SCHEMA')

    def test_duplicate_skill_name_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self._skills_copy(td)
            # a second pack that declares the already-taken name pipd-route-intake
            shutil.copytree(skills / 'pipd-route-intake', skills / 'pipd-route-intake-copy')
            self._assert_refused(skills, 'DUPLICATE_SKILL_NAME')

    def test_ninth_entry_is_refused(self):
        with tempfile.TemporaryDirectory() as td:
            skills = self._skills_copy(td)
            extra = skills / 'pipd-observer-notes'
            shutil.copytree(skills / 'pipd-package-project', extra)
            skill_md = extra / 'SKILL.md'
            text = skill_md.read_text(encoding='utf-8')
            skill_md.write_text(text.replace('name: pipd-package-project',
                                             'name: pipd-observer-notes', 1),
                                encoding='utf-8', newline='')
            result = self._assert_refused(skills, 'UNEXPECTED_ENTRY')
            self.assertTrue(any('9th' in r['reason'] or 'not one of the 8' in r['reason']
                                for r in result['refusals']))


if __name__ == '__main__':
    unittest.main()
