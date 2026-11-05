#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Deterministically (re)build the WP-FHS-19 fixture trees under fixtures/.

Five trees, all synthetic:

  pos/                     every check PASS
  neg_notice_missing/      NOTICE removed                -> NOTICE_MISSING
  neg_sbom_mismatch/       SBOM lists undeclared libs    -> SBOM_COMPONENT_MISMATCH
  neg_undeclared_dep/      imports yaml, declares none   -> UNDECLARED_DEPENDENCY
  neg_secret/              fake credential shapes        -> SECRET_PATTERN_FOUND

Every "secret" in neg_secret/ is a placeholder built from obvious dummy
characters; no real credential is present in this repository.
"""
from __future__ import annotations

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIXTURES = os.path.join(ROOT, "fixtures")

LICENSE_TEXT = """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

SPDX-License-Identifier: Apache-2.0

FIXTURE NOTE: this is an abbreviated, synthetic licence text used only by the
WP-FHS-19 gate fixtures. It carries the SPDX identifier the gate resolves and a
recognisable Apache-2.0 header so both resolution paths are exercised.

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
1. Definitions. "License" shall mean the terms and conditions for use,
reproduction, and distribution as defined by Sections 1 through 9 of this
document. [ ... abridged fixture body ... ]
"""

NOTICE_TEXT = """pos-fixture
Copyright 2026 FHS W0 fixture authors

This product includes software developed as part of the FHS W0 synthetic
fixture set. No third-party attribution obligations are implied by this file.
"""

OWNER_LICENSE_DECISION = """schema: FHS_W0/OWNER_LICENSE_DECISION/v1
package: pos-fixture
spdx: Apache-2.0
decision: OWNER_GRANTED
decided_by: fixture-owner
note: synthetic fixture decision, not a real ownership record
"""

PYPROJECT = """[project]
name = "pos-fixture"
version = "0.1.0"
description = "WP-FHS-19 positive fixture"
requires-python = ">=3.11"
dependencies = ["jsonschema>=4.0"]
license = "Apache-2.0"
license-files = ["LICENSE", "NOTICE"]

[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
"""

SBOM_POS = """{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:0f7c1a2e-1111-4a2b-9c3d-000000000001",
  "version": 1,
  "metadata": {
    "timestamp": "2026-11-05T00:00:00Z",
    "component": {
      "type": "application",
      "name": "pos-fixture",
      "version": "0.1.0",
      "licenses": [{"license": {"id": "Apache-2.0"}}]
    }
  },
  "components": [
    {
      "type": "library",
      "name": "jsonschema",
      "version": "4.23.0",
      "purl": "pkg:pypi/jsonschema@4.23.0"
    }
  ]
}
"""

SBOM_MISMATCH = """{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:0f7c1a2e-1111-4a2b-9c3d-000000000002",
  "version": 1,
  "metadata": {
    "timestamp": "2026-11-05T00:00:00Z",
    "component": {"type": "application", "name": "pos-fixture", "version": "0.1.0"}
  },
  "components": [
    {"type": "library", "name": "jsonschema", "version": "4.23.0", "purl": "pkg:pypi/jsonschema@4.23.0"},
    {"type": "library", "name": "requests", "version": "2.32.3", "purl": "pkg:pypi/requests@2.32.3"},
    {"type": "library", "name": "urllib3", "version": "2.2.3", "purl": "pkg:pypi/urllib3@2.2.3"}
  ]
}
"""

INIT_PY = '''"""pos-fixture package."""

__all__ = ["core"]
'''

UTIL_PY = '''"""Local helper module (target of a relative import)."""


def helper(value):
    return str(value)
'''

CORE_PY = '''"""Imports one declared third-party library plus stdlib only."""

import json
import os

import jsonschema

from .util import helper


def validate(document, schema):
    jsonschema.validate(instance=document, schema=schema)
    return helper(os.path.basename("x.json")) + json.dumps(document)[:0]
'''

LOADER_PY = '''"""Loader used by the positive tree (stdlib only)."""

import pathlib


def load(path):
    return pathlib.Path(path).read_text(encoding="utf-8")
'''

LOADER_UNDECLARED_PY = '''"""Loader that imports a library the manifest never declares."""

import pathlib

import yaml


def load(path):
    return yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
'''

CI_YML = """name: fixture-ci
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m unittest discover -s tests -v
"""

README = """# pos-fixture

Synthetic positive fixture for the WP-FHS-19 supply-chain gate.

Re-run locally:

```
python -m unittest discover -s tests -v
```
"""

SECRETS_PY = '''"""Synthetic credential shapes -- every value below is a dummy placeholder.

No real credential exists here: the GitHub token bodies are repeated filler and
the AWS key is the vendor's published documentation example. The gate must
redact them: output carries only a 4-char prefix plus file:line.
"""

GITHUB_PAT = "github_pat_11AAADUMMYDUMMYDUMMY_0000000000000000000000000000000000000000000"
GITHUB_TOKEN = "ghp_000000000000000000000000000000000000"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"

PRIVATE_KEY_PLACEHOLDER = """-----BEGIN RSA PRIVATE KEY-----
MIIBOgIBAAJBAKfakefakefakefakefakefakefakefakefakefakefakefakefake
-----END RSA PRIVATE KEY-----
"""
'''


def write(rel: str, text: str) -> None:
    path = os.path.join(FIXTURES, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def build_pos_tree(name: str) -> None:
    write(f"{name}/LICENSE", LICENSE_TEXT)
    write(f"{name}/NOTICE", NOTICE_TEXT)
    write(f"{name}/OWNER_LICENSE_DECISION.yaml", OWNER_LICENSE_DECISION)
    write(f"{name}/pyproject.toml", PYPROJECT)
    write(f"{name}/SBOM.cdx.json", SBOM_POS)
    write(f"{name}/README.md", README)
    write(f"{name}/.github/workflows/ci.yml", CI_YML)
    write(f"{name}/src/pos_fixture/__init__.py", INIT_PY)
    write(f"{name}/src/pos_fixture/util.py", UTIL_PY)
    write(f"{name}/src/pos_fixture/core.py", CORE_PY)
    write(f"{name}/src/pos_fixture/loader.py", LOADER_PY)
    write(f"{name}/tests/test_smoke.py", "import unittest\n\n\nclass Smoke(unittest.TestCase):\n"
                                         "    def test_true(self):\n        self.assertTrue(True)\n")


def main() -> int:
    for tree in ("pos", "neg_notice_missing", "neg_sbom_mismatch",
                 "neg_undeclared_dep", "neg_secret"):
        target = os.path.join(FIXTURES, tree)
        if os.path.isdir(target):
            shutil.rmtree(target)

    build_pos_tree("pos")

    build_pos_tree("neg_notice_missing")
    os.remove(os.path.join(FIXTURES, "neg_notice_missing", "NOTICE"))

    build_pos_tree("neg_sbom_mismatch")
    write("neg_sbom_mismatch/SBOM.cdx.json", SBOM_MISMATCH)

    build_pos_tree("neg_undeclared_dep")
    write("neg_undeclared_dep/src/pos_fixture/loader.py", LOADER_UNDECLARED_PY)

    build_pos_tree("neg_secret")
    write("neg_secret/config/sample_credentials.py", SECRETS_PY)

    for tree in ("pos", "neg_notice_missing", "neg_sbom_mismatch",
                 "neg_undeclared_dep", "neg_secret"):
        count = sum(len(f) for _, _, f in os.walk(os.path.join(FIXTURES, tree)))
        print(f"built fixtures/{tree}: {count} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
