"""Rebuild ``sbom/manifest.json`` from the tree using the canonical inventory order.

Ordering comes from :func:`core.canonical_order`, the same function
``package_preflight`` uses to validate, so a BOM built here on Windows validates
on POSIX and the reverse. The BOM excludes its own bytes; the archive receipt
pins the complete ZIP.

Usage:  python scripts/refresh_bom.py <package-root>
"""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

try:
    from .core import canonical_order
except ImportError:
    from core import canonical_order

FORBIDDEN = ('.git', '__pycache__', 'node_modules', '.venv')


def refresh(root) -> dict:
    root = Path(root).resolve(strict=True)
    path = root / 'sbom' / 'manifest.json'
    bom = json.loads(path.read_text(encoding='utf-8'))
    bom['version'] = json.loads((root / 'plugin.json').read_text(encoding='utf-8'))['version']
    rows = []
    for file in canonical_order(root, [p for p in root.rglob('*') if p.is_file()]):
        rel = file.relative_to(root).as_posix()
        if (any(part in FORBIDDEN for part in file.relative_to(root).parts)
                or file.suffix == '.pyc' or rel == 'sbom/manifest.json'):
            continue
        raw = file.read_bytes()
        rows.append({'path': rel, 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
    bom['files'] = rows
    for component in bom.get('components', []):
        if component.get('name') == 'installed PIPD P4':
            component['license'] = 'Apache-2.0_SOURCE_OWNER_ENGINEERING_GRANT'
            component['license_conflict'] = ('historical proprietary position superseded; '
                                             'raw DOC rights not asserted')
    bom['self_inventory_rule'] = ('BOM excludes its own bytes; archive receipt pins '
                                  'the complete ZIP')
    bom['inventory_order'] = 'core.canonical_order: casefold(POSIX path), then exact path'
    path.write_text(json.dumps(bom, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return {'version': bom['version'], 'files': len(rows)}


if __name__ == '__main__':
    print(json.dumps(refresh(Path(sys.argv[1])), indent=2))
