"""Strict validation of a portable Agent Plugins 1.0.0 ``plugin.json``.

Why this module exists: a JSON file that *parses* is not a plugin manifest. The portable schema at
``https://agent-plugins.org/schemas/1.0.0/plugin.schema.json`` (vendored byte-for-byte in
``schema/plugin.schema.json``) sets ``additionalProperties: false``, so an internal key like
``permissions`` placed at the top level makes the manifest *invalid* even though ``json.loads`` is
happy. The earlier packaging emitted ``"schema": "SBL-AGENT-PLUGIN/1"`` and no ``$schema`` at all,
which a conforming host does not recognise as this format at all.

The validator below is a hand-written re-implementation of the vendored schema's constraints, kept
dependency-free because the product declares no runtime dependencies. It is cross-checked against
``jsonschema`` in the test suite when that library is importable; the cross-check is skipped (and the
skip is recorded) where it is not.

The rules implemented, and nothing beyond them:

* required ``$schema`` (const, exact string) and ``name``;
* the ten allowed top-level keys, and no others;
* ``name`` type/length/pattern;
* string types for version/description/homepage/repository/license;
* ``author`` an object whose only allowed keys are name/email/url, each a string;
* ``keywords`` an array of strings;
* ``extensions`` an object whose every value is an object.

Known limitations, stated rather than implied: the vendored schema is not a general-purpose JSON
Schema engine, so constructs it does not use (``$ref``, ``allOf``, ``if/then``) are not supported by
this re-implementation; and the Agent Plugins *semantic* requirements (what a client does with
``skills/`` or ``mcp.json``) are outside any JSON Schema and are therefore not enforced here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

CANONICAL_SCHEMA_URI = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
SCHEMA_PATH = Path(__file__).parent / "schema" / "plugin.schema.json"

ALLOWED_TOP_LEVEL = frozenset(
    {
        "$schema",
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "extensions",
    }
)
REQUIRED_TOP_LEVEL = ("$schema", "name")
AUTHOR_KEYS = frozenset({"name", "email", "url"})

# Transcribed from the vendored schema's `name.pattern`. Escapes are doubled because the JSON
# document stores them as `\\.`; here they are ordinary regex escapes.
NAME_PATTERN = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
NAME_MAX = 64


def load_schema() -> dict[str, Any]:
    """Return the vendored schema. Callers compare against the bytes this round shipped."""

    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _is_str(value: Any) -> bool:
    return isinstance(value, str)


def validate_manifest(manifest: Mapping[str, Any]) -> list[str]:
    """Return a list of violations. Empty list means valid under the vendored schema."""

    errors: list[str] = []
    if not isinstance(manifest, Mapping):
        return ["manifest is not a JSON object"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in manifest:
            errors.append(f"missing required key {key!r}")

    if "$schema" in manifest and manifest["$schema"] != CANONICAL_SCHEMA_URI:
        errors.append(
            f"$schema must equal {CANONICAL_SCHEMA_URI!r}, got {manifest['$schema']!r}"
        )

    extra = sorted(set(manifest) - ALLOWED_TOP_LEVEL)
    if extra:
        errors.append(
            "additionalProperties is false; illegal top-level keys: " + ", ".join(extra)
        )

    name = manifest.get("name")
    if name is not None:
        if not _is_str(name):
            errors.append("name must be a string")
        else:
            if not 1 <= len(name) <= NAME_MAX:
                errors.append(f"name length must be 1..{NAME_MAX}, got {len(name)}")
            if not NAME_PATTERN.match(name):
                errors.append(f"name {name!r} violates the portable name pattern")

    for key in ("version", "description", "homepage", "repository", "license"):
        if key in manifest and not _is_str(manifest[key]):
            errors.append(f"{key} must be a string")

    if "author" in manifest:
        author = manifest["author"]
        if not isinstance(author, Mapping):
            errors.append("author must be an object")
        else:
            bad = sorted(set(author) - AUTHOR_KEYS)
            if bad:
                errors.append("author allows only name/email/url; got " + ", ".join(bad))
            for key, value in author.items():
                if not _is_str(value):
                    errors.append(f"author.{key} must be a string")

    if "keywords" in manifest:
        keywords = manifest["keywords"]
        if not isinstance(keywords, list) or not all(_is_str(item) for item in keywords):
            errors.append("keywords must be an array of strings")

    if "extensions" in manifest:
        extensions = manifest["extensions"]
        if not isinstance(extensions, Mapping):
            errors.append("extensions must be an object")
        else:
            for namespace, payload in extensions.items():
                if not isinstance(payload, Mapping):
                    errors.append(f"extensions[{namespace!r}] must be an object")

    return errors


def is_valid(manifest: Mapping[str, Any]) -> bool:
    return not validate_manifest(manifest)


def assert_valid(manifest: Mapping[str, Any], *, where: str = "plugin.json") -> None:
    """Raise on an invalid manifest. Imported lazily so this module stays import-light."""

    errors = validate_manifest(manifest)
    if errors:
        from sbl_core.errors import SBLError

        raise SBLError(
            "SBL_E_PLUGIN_SCHEMA",
            f"{where} does not conform to the portable plugin schema",
            {"where": where, "violations": errors, "schema": CANONICAL_SCHEMA_URI},
        )
