from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .errors import InvariantViolation
from .util import sha256_file


REQUIRED_FILES = (
    "src/hlpe/plan/compiler.py",
    "src/hlpe/shared/canonical.py",
    "src/hlpe/shared/models.py",
    "src/hlpe/shared/requirements.py",
    "src/hlpe/shared/tokens.py",
    "src/hlpe/shared/permissions.py",
    "src/hlpe/cli.py",
    "schemas/plan/approved-plan-pack.schema.json",
    "schemas/bootstrap/bootstrap-pack.schema.json",
)


def qualify_hlpe(path: Path, expected_head: str) -> dict[str, object]:
    path = path.resolve(strict=True)
    missing = [item for item in REQUIRED_FILES if not (path / item).is_file()]
    if missing:
        raise InvariantViolation(f"ERR_HLPE_REQUIRED_FILES:{missing}")
    env = os.environ.copy()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    base = ["git", "-c", f"safe.directory={path}", "-C", str(path)]
    head = subprocess.run(base + ["rev-parse", "HEAD"], check=True, capture_output=True, text=True, env=env).stdout.strip()
    if head != expected_head:
        raise InvariantViolation(f"ERR_HLPE_HEAD_DRIFT:{head}")
    status = subprocess.run(base + ["status", "--porcelain"], check=True, capture_output=True, text=True, env=env).stdout
    if status:
        raise InvariantViolation("ERR_HLPE_TARGET_DIRTY")
    hashes = {item: sha256_file(path / item) for item in REQUIRED_FILES}
    return {"path": str(path), "head": head, "clean": True, "required_files": hashes, "status": "QUALIFIED_SCOPE"}
