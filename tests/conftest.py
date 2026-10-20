"""Test support: pin pytest scratch space to a writable directory.

The default ``pytest-of-<user>`` directory under the machine temp root is not
writable in this environment, so each session gets its own ``mkdtemp`` (the
temp root itself is writable) and it is removed again at session end.
"""

from __future__ import annotations

import os
import shutil
import tempfile

def scratch_root() -> str:
    """Writable per-run scratch base, OUTSIDE the repo tree.

    The repo-local ``.pytest_tmp`` was left un-writable by an earlier sandboxed
    lane (deny ACE that even takeown cannot reset), so scratch space lives under
    the machine temp root, overridable with SBL_TEST_TMP.
    """
    base = os.environ.get("SBL_TEST_TMP") or tempfile.gettempdir()
    path = os.path.join(base, "sbl-tests")
    os.makedirs(path, exist_ok=True)
    return path


_SCRATCH: dict[str, str] = {}


def pytest_configure(config) -> None:
    if config.option.basetemp:
        return
    scratch = tempfile.mkdtemp(prefix="sbl-pytest-")
    _SCRATCH["path"] = scratch
    config.option.basetemp = scratch


def pytest_unconfigure(config) -> None:
    scratch = _SCRATCH.pop("path", None)
    if scratch and os.path.isdir(scratch):
        shutil.rmtree(scratch, ignore_errors=True)
