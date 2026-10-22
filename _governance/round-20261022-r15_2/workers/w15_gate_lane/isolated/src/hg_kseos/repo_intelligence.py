from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .errors import InvariantViolation
from .security import ensure_within


def analyze_python_change(repo_root: Path, changed_files: list[Path], diff_line_budget: int, changed_lines: int) -> dict[str, Any]:
    root = repo_root.resolve(strict=True)
    if changed_lines < 0 or changed_lines > diff_line_budget:
        raise InvariantViolation(f"ERR_DIFF_BUDGET:{changed_lines}>{diff_line_budget}")
    symbols: dict[str, list[str]] = {}
    dependencies: dict[str, list[str]] = {}
    impacted_tests: set[str] = set()
    for supplied in changed_files:
        path = ensure_within(supplied, root)
        if path.suffix != ".py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        relative = path.relative_to(root).as_posix()
        symbols[relative] = sorted(
            node.name for node in ast.walk(tree) if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        )
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        dependencies[relative] = sorted(imports)
        stem = path.stem
        impacted_tests.update(
            item.relative_to(root).as_posix() for item in root.glob(f"tests/**/test*{stem}*.py")
        )
    return {
        "verdict": "PASS",
        "changed_lines": changed_lines,
        "diff_line_budget": diff_line_budget,
        "symbols": symbols,
        "dependencies": dependencies,
        "impacted_tests": sorted(impacted_tests),
    }
