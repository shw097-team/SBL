"""Disposable Maker tests; these do not execute a native USER Golden WorkOrder."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sbl_cli import sbl_todo as todo


class TodoAtomicSaveTests(unittest.TestCase):
    def test_existing_legacy_temp_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            foreign = root / todo.TMP_FILE
            foreign.write_bytes(b'pre-existing-user-file')
            todo._save_state(root, {'schema': todo.SCHEMA, 'items': []})
            self.assertTrue(foreign.exists(), 'a pre-existing file was consumed')
            self.assertEqual(foreign.read_bytes(), b'pre-existing-user-file')

    def test_failed_replace_preserves_old_state_without_own_residue(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / todo.DATA_FILE
            target.write_bytes(b'original-state-bytes')
            with patch.object(todo.os, 'replace', side_effect=OSError('injected-before-replace')):
                with self.assertRaisesRegex(OSError, 'injected-before-replace'):
                    todo._save_state(root, {'schema': todo.SCHEMA, 'items': []})
            self.assertEqual(target.read_bytes(), b'original-state-bytes')
            self.assertEqual([p.name for p in root.iterdir()], [todo.DATA_FILE])

    def test_fsync_precedes_atomic_replace(self):
        with tempfile.TemporaryDirectory() as directory:
            original = todo.os.replace
            with patch.object(todo.os, 'fsync', wraps=todo.os.fsync) as flushed:
                def replace(source, target):
                    flushed.assert_called_once()
                    original(source, target)
                with patch.object(todo.os, 'replace', side_effect=replace):
                    todo._save_state(Path(directory), {'schema': todo.SCHEMA, 'items': []})
            self.assertEqual(json.loads((Path(directory) / todo.DATA_FILE).read_text())['items'], [])


if __name__ == '__main__':
    unittest.main()
