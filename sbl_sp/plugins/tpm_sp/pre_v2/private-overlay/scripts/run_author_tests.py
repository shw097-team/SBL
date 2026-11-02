"""Single author-test entry point for the private package (BUG-TEST-ENTRY).

``python -m unittest discover -s tests`` only resolves the design gate when the
package root and ``scripts/`` are on ``sys.path``, which depends on the caller's
cwd and shell. This wrapper pins both paths, discovers the same suite and exits
with the real unittest status, so Windows and POSIX run one identical entry.

Usage:  python scripts/run_author_tests.py [-q]
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    verbosity = 1 if ('-q' in argv or '--quiet' in argv) else 2
    for path in (ROOT, ROOT / 'scripts'):
        entry = str(path)
        if entry not in sys.path:
            sys.path.insert(0, entry)
    suite = unittest.TestLoader().discover(str(ROOT / 'tests'), pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    print(f'RAN={result.testsRun} FAILURES={len(result.failures)} '
          f'ERRORS={len(result.errors)} SKIPPED={len(result.skipped)}')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(main())
