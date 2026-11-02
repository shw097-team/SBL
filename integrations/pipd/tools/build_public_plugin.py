#!/usr/bin/env python3
"""S4POST Stage B: build the deterministic, fail-closed public Skills-only plugin candidate.

This tool turns the eight ``skills/pipd-*`` packs into ONE portable plugin ZIP. It is
fail-closed by construction: every owner-gated input that has not been supplied yet makes the build
REFUSE with a typed reason (non-zero exit), never warn. Nothing here publishes anything; the output
is a *candidate* whose receipt says ``claim_ceiling: LOCAL_PACKAGER_PASS_ONLY`` and
``official_portal_verification: NOT_EXECUTED``.

Two manifests, one package:
  * ``plugin.json`` is the OFFICIAL Agent Plugins 1.0 package-root manifest. It is validated
    against the byte-locked vendor schema ``vendor-plugin.schema.json`` (a byte copy of
    ``https://agent-plugins.org/schemas/1.0.0/plugin.schema.json``), so a private PIPD manifest
    placed at the root would be refused by ``additionalProperties: false``.
  * ``plugin.release.json`` is PIPD's own release bookkeeping (claim ceiling, portal state,
    publisher record, icon digests, the eight skill names and the pinned digest of the official
    vendor schema). The same object is embedded in the official manifest under the vendor-blessed
    ``extensions["com.pipd.s4"]`` namespace, and both copies must agree.

Owner-gated inputs (all missing on purpose in the checked-in candidate):
  * a per-skill derivation record in ``derivations.json`` whose ``source_sha256`` matches the
    frozen ledger (each ``SKILL.md`` carries non-portable frontmatter, so a byte-copy projection is
    impossible and every skill needs an owner-approved derivation),
  * the pinned digest of the official (vendor) schema in ``official_schema_sha256``,
  * the publisher identity,
  * the icon digests.

Typed refusals added by the vendor-schema lock: ``VENDOR_SCHEMA_MISSING``, ``VENDOR_SCHEMA_INVALID``,
``VENDOR_SCHEMA_ID_MISMATCH``, ``OFFICIAL_SCHEMA_ID_MISMATCH``, ``VENDOR_SCHEMA_DIGEST_MISMATCH``,
``RELEASE_BOOKKEEPING_MISSING`` and ``RELEASE_EXTENSION_MISMATCH``. The former
``OFFICIAL_SCHEMA_DIGEST_MISMATCH`` is subsumed by ``VENDOR_SCHEMA_DIGEST_MISMATCH``: the pinned
digest now names the official vendor schema bytes, not the local subset.

Determinism: fixed ZIP metadata (1980-01-01, mode 0644, DEFLATED level 9). The archive is written
to a scratch file, read back and compared member-by-member before it is promoted into place, so two
builds from the same inputs are byte-identical.

CLI
---
``--source-root DIR``     frozen checkout (default: the repository of this file)
``--ledger FILE``         frozen source ledger from ``freeze_public_plugin_source.py``
``--source-commit HEX40`` the pinned source commit (must equal the ledger commit)
``--packaging-root DIR``  authoring directory (default: <repo>/packaging/public-plugin)
``--out-dir DIR``         release directory for the candidate ZIP (must not overlap the repo)
``--generate-icons``      (re)write the deterministic PNG icons into the packaging assets first
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import tempfile
import zipfile
import zlib
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
from freeze_public_plugin_source import (  # noqa: E402  (sibling tool, stdlib-only)
    EXPECTED_SKILLS,
    canonical_bytes,
)

# PIPD's release bookkeeping document (``plugin.release.json``); the local ``plugin.schema.json``
# subset pins this closed key set.
RELEASE_SCHEMA_ID = "PIPD-PUBLIC-PLUGIN-MANIFEST/1"
# The official Agent Plugins 1.0 vendor schema: its ``$id`` is the manifest ``$schema``, and its
# exact bytes are pinned here so a swapped schema cannot silently widen the accepted manifest.
VENDOR_SCHEMA_ID = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
VENDOR_SCHEMA_SHA256 = "0a4aad95ce337878ad38802ebf0daa3fde76abe3f65400c86bcbb1ec0b3ab883"
VENDOR_SCHEMA_FILENAME = "vendor-plugin.schema.json"
RELEASE_BOOKKEEPING_FILENAME = "plugin.release.json"
# The vendor-blessed reverse-domain namespace that carries PIPD's own release bookkeeping.
RELEASE_EXTENSION_KEY = "com.pipd.s4"
# The extension namespaces REVIEWED for this package (CR-EXT-UNREVIEWED). The locked vendor schema
# permits arbitrary object-valued reverse-domain namespaces, so without this gate an unreviewed
# namespace is accepted and preserved in the ZIP at exit 0. Adding a namespace is a review decision
# recorded against the release, not a build-time input, so the gate refuses anything outside this
# set. `com.openai` carries the interface block the public listing reads; `com.pipd.s4` carries the
# bookkeeping that is checked against `plugin.release.json` verbatim.
REVIEWED_EXTENSION_NAMESPACES = ("com.openai", RELEASE_EXTENSION_KEY)
PORTABLE_KEYS = ("name", "description", "license", "compatibility", "metadata", "allowed-tools")
NON_PORTABLE_KEYS = ("version", "owner", "triggers", "schemas", "references", "tests")

FIXED_DATE_TIME = (1980, 1, 1, 0, 0, 0)
FIXED_MODE = 0o644
COMPRESS_LEVEL = 9

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
PLACEHOLDERS = frozenset(
    {"", "OWNER_INPUT_REQUIRED", "TODO", "TBD", "PLACEHOLDER", "CHANGEME", "<owner>", "NONE"}
)

PNG_SIG = b"\x89PNG\r\n\x1a\n"

DERIVATION_MISSING_TEMPLATE = (
    "no owner derivation record for skill '{skill}' (derivations.json is empty by design; "
    "every skill needs an owner-approved record whose source_sha256 matches the frozen ledger)"
)


class Refusal(Exception):
    """A fail-closed build refusal. ``code`` is the machine-checkable typed reason."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"REFUSED {code}: {detail}")
        self.code = code
        self.detail = detail


# --------------------------------------------------------------------------- helpers
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(doc) -> bytes:
    return (json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def is_placeholder(value) -> bool:
    return value is None or (isinstance(value, str) and value.strip().upper() in PLACEHOLDERS)


def _path_is_symlink(path) -> bool:
    """Seam for tests: a single predicate the symlink gates consult."""
    return os.path.islink(path)


# --------------------------------------------------------------------------- PNG (stdlib only)
def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def png_icon_bytes(size: int = 128) -> bytes:
    """A deterministic RGBA icon: no Pillow, no new dependency, no wall-clock input."""
    if size < 8:
        raise ValueError("icon size must be at least 8 px")
    raw = bytearray()
    for y in range(size):
        raw.append(0)  # filter type 0 (None)
        for x in range(size):
            r = (x * 255) // (size - 1)
            g = (y * 255) // (size - 1)
            border = x < size // 16 or x >= size - size // 16 or y < size // 16 or y >= size - size // 16
            b = 0x10 if border else 0x60
            raw += bytes((r, g, b, 255))
    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return (PNG_SIG + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _png_chunk(b"IEND", b""))


def png_errors(data: bytes) -> list[str]:
    """Decode the PNG structurally: signature, chunk CRCs, IHDR and an inflated IDAT."""
    if len(data) < 8:
        return ["too_short"]
    if data[:8] != PNG_SIG:
        return ["signature"]
    errors: list[str] = []
    pos = 8
    width = height = bit_depth = color_type = None
    idat = bytearray()
    seen_ihdr = seen_iend = False
    first_chunk = None
    while pos < len(data):
        if pos + 8 > len(data):
            errors.append("truncated_chunk_header")
            break
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        chunk_type = data[pos + 4:pos + 8]
        pos += 8
        if pos + length + 4 > len(data):
            errors.append(f"truncated_chunk_body:{chunk_type.decode('latin1')}")
            break
        body = data[pos:pos + length]
        crc = data[pos + length:pos + length + 4]
        pos += length + 4
        if first_chunk is None:
            first_chunk = chunk_type
            if chunk_type != b"IHDR":
                errors.append("ihdr_not_first")
        if crc != struct.pack(">I", zlib.crc32(chunk_type + body) & 0xFFFFFFFF):
            errors.append(f"crc:{chunk_type.decode('latin1')}")
        if chunk_type == b"IHDR":
            seen_ihdr = True
            if len(body) != 13:
                errors.append("ihdr_length")
            else:
                width, height, bit_depth, color_type, _comp, _filt, interlace = struct.unpack(
                    ">IIBBBBB", body)
                if width == 0 or height == 0:
                    errors.append("ihdr_zero_dimension")
                if bit_depth != 8:
                    errors.append("ihdr_bit_depth")
                if color_type not in (0, 2, 4, 6):
                    errors.append("ihdr_color_type")
                if interlace != 0:
                    errors.append("ihdr_interlace")
        elif chunk_type == b"IDAT":
            idat += body
        elif chunk_type == b"IEND":
            seen_iend = True
            break
    if not seen_ihdr:
        errors.append("ihdr_missing")
    if not seen_iend:
        errors.append("iend_missing")
    if seen_ihdr and seen_iend and width and height:
        channels = {0: 1, 2: 3, 4: 2, 6: 4}.get(color_type, 0)
        try:
            inflated = zlib.decompress(bytes(idat))
        except zlib.error:
            errors.append("idat_inflate")
        else:
            if channels == 0 or len(inflated) != height * (1 + width * channels):
                errors.append("idat_size")
    return errors


# --------------------------------------------------------------------------- JSON-schema subset
def _type_ok(value, typ: str) -> bool:
    if typ == "object":
        return isinstance(value, dict)
    if typ == "array":
        return isinstance(value, list)
    if typ == "string":
        return isinstance(value, str)
    if typ == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if typ == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if typ == "boolean":
        return isinstance(value, bool)
    if typ == "null":
        return value is None
    return True


def validate_subset(instance, schema, path: str = "$") -> list[dict]:
    """A tiny, dependency-free JSON-Schema subset validator (local subset AND vendor schema).

    Supported keywords: ``type``, ``const``, ``enum``, ``minLength``, ``maxLength``, ``pattern``,
    ``minimum``, ``maximum``, ``minItems``, ``maxItems``, ``uniqueItems``, ``items``, ``required``,
    ``properties`` and both forms of ``additionalProperties`` (``false`` closes the key set; an
    object schema validates every key that ``properties`` does not name).
    """
    errors: list[dict] = []
    if not isinstance(schema, dict):
        return errors
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(instance, t) for t in types):
            return [{"path": path, "keyword": "type", "message": f"expected one of {types}"}]
    if "const" in schema and instance != schema["const"]:
        errors.append({"path": path, "keyword": "const",
                       "message": f"expected const {schema['const']!r}"})
    if "enum" in schema and instance not in schema["enum"]:
        errors.append({"path": path, "keyword": "enum",
                       "message": f"expected one of {schema['enum']!r}"})
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append({"path": path, "keyword": "minLength", "message": "too short"})
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            errors.append({"path": path, "keyword": "maxLength", "message": "too long"})
        if "pattern" in schema and re.search(schema["pattern"], instance) is None:
            errors.append({"path": path, "keyword": "pattern",
                           "message": f"does not match {schema['pattern']!r}"})
    if isinstance(instance, int) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append({"path": path, "keyword": "minimum", "message": "below minimum"})
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append({"path": path, "keyword": "maximum", "message": "above maximum"})
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append({"path": path, "keyword": "minItems", "message": "too few items"})
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            errors.append({"path": path, "keyword": "maxItems", "message": "too many items"})
        if schema.get("uniqueItems"):
            seen = {json.dumps(item, sort_keys=True) for item in instance}
            if len(seen) != len(instance):
                errors.append({"path": path, "keyword": "uniqueItems", "message": "duplicates"})
        items = schema.get("items")
        if isinstance(items, dict):
            for i, item in enumerate(instance):
                errors += validate_subset(item, items, f"{path}[{i}]")
    if isinstance(instance, dict):
        for required_key in schema.get("required", []):
            if required_key not in instance:
                errors.append({"path": f"{path}.{required_key}", "keyword": "required",
                               "message": "required property is absent"})
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties")
        if extra is False:
            for key in instance:
                if key not in props:
                    errors.append({"path": f"{path}.{key}", "keyword": "additionalProperties",
                                   "message": "additional property is not allowed"})
        for key, value in instance.items():
            if key in props:
                errors += validate_subset(value, props[key], f"{path}.{key}")
            elif isinstance(extra, dict):
                errors += validate_subset(value, extra, f"{path}.{key}")
    return errors


# --------------------------------------------------------------------------- frontmatter
def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1]
    return value


def parse_skill_md(text: str) -> tuple[list[str], dict, str]:
    """Split ``SKILL.md`` into (ordered keys, mapping, body). Never mutates the body text."""
    first_nl = text.find("\n")
    if first_nl == -1 or text[:first_nl].strip() != "---":
        raise Refusal("SKILL_FRONTMATTER_INVALID", "SKILL.md does not open with a `---` line")
    pos = first_nl + 1
    fm_lines: list[str] = []
    body: str | None = None
    while True:
        nl = text.find("\n", pos)
        if nl == -1:
            if text[pos:].strip() == "---":
                body = ""
                break
            raise Refusal("SKILL_FRONTMATTER_INVALID", "frontmatter is not terminated by `---`")
        line = text[pos:nl]
        if line.strip() == "---":
            body = text[nl + 1:]
            break
        fm_lines.append(line)
        pos = nl + 1
    mapping: dict[str, object] = {}
    keys: list[str] = []
    current: str | None = None
    for raw in fm_lines:
        line = raw.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.lstrip().startswith("- "):
            if current is None:
                raise Refusal("SKILL_FRONTMATTER_INVALID", "list item without a preceding key")
            cast = mapping[current]
            if not isinstance(cast, list):
                raise Refusal("SKILL_FRONTMATTER_INVALID", f"key {current!r} mixes scalar and list")
            cast.append(_unquote(line.lstrip()[2:]))
            continue
        if ":" not in line:
            raise Refusal("SKILL_FRONTMATTER_INVALID",
                          f"frontmatter line is not `key: value`: {line!r}")
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            raise Refusal("SKILL_FRONTMATTER_INVALID", f"empty frontmatter key: {line!r}")
        if key in mapping:
            raise Refusal("SKILL_FRONTMATTER_INVALID", f"duplicate frontmatter key {key!r}")
        if value == "":
            mapping[key] = []
            current = key
        else:
            mapping[key] = _unquote(value)
            current = None
        keys.append(key)
    if not keys:
        raise Refusal("SKILL_FRONTMATTER_INVALID", "frontmatter carries no keys")
    if body is None:
        raise Refusal("SKILL_FRONTMATTER_INVALID", "frontmatter has no body")
    return keys, mapping, body


def _emit_frontmatter(mapping: dict, keys: list[str]) -> str:
    lines = ["---"]
    for key in keys:
        value = mapping[key]
        if isinstance(value, list):
            lines.append(f"{key}:")
            lines.extend(f"  - {item}" for item in value)
        else:
            lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def project_skill_md(skill: str, source_bytes: bytes, record: dict) -> tuple[bytes, dict]:
    """Project one derived ``SKILL.md``: keep portable keys only, body byte-identical."""
    try:
        text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Refusal("SKILL_NOT_UTF8", f"{skill}/SKILL.md is not UTF-8: {exc}") from exc
    keys, mapping, body = parse_skill_md(text)
    # The frontmatter `name` is the skill's portable identity: it must name this skill directory.
    if mapping.get("name") != skill:
        raise Refusal("SKILL_FRONTMATTER_INVALID",
                      f"{skill}: frontmatter `name` is {mapping.get('name')!r}; "
                      f"it must be the skill name {skill!r}")
    kept = [k for k in keys if k in PORTABLE_KEYS]
    dropped = [k for k in keys if k not in PORTABLE_KEYS]
    if set(record.get("kept_keys", [])) != set(kept):
        raise Refusal("DERIVATION_KEY_SET_MISMATCH",
                      f"{skill}: record kept_keys {record.get('kept_keys')} != observed {kept}")
    if set(record.get("dropped_keys", [])) != set(dropped):
        raise Refusal("DERIVATION_KEY_SET_MISMATCH",
                      f"{skill}: record dropped_keys {record.get('dropped_keys')} != observed {dropped}")
    projected = (_emit_frontmatter(mapping, kept) + body).encode("utf-8")
    # The body must survive the projection byte-for-byte.
    _pk, _pm, projected_body = parse_skill_md(projected.decode("utf-8"))
    if projected_body.encode("utf-8") != body.encode("utf-8"):
        raise Refusal("PROJECTION_BODY_CHANGED", f"{skill}: frontmatter projection changed the body")
    return projected, {"kept_keys": kept, "dropped_keys": dropped}


# --------------------------------------------------------------------------- source walking
def _list_skill_dirs(skills_root: Path) -> dict[str, Path]:
    if not skills_root.is_dir():
        raise Refusal("SKILLS_ROOT_MISSING", str(skills_root))
    out: dict[str, Path] = {}
    for child in sorted(skills_root.iterdir()):
        if child.name.startswith(".") or child.name == "__pycache__":
            continue
        if _path_is_symlink(child):
            raise Refusal("SOURCE_SYMLINK", str(child))
        if not child.is_dir():
            raise Refusal("SOURCE_SPECIAL_MEMBER", f"{child} is not a skill directory")
        out[child.name] = child
    return out


def _walk_source_files(repo_root: Path, skill_dir: Path) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for dirpath, dirnames, filenames in os.walk(skill_dir, topdown=True, followlinks=False):
        dirnames.sort()
        filenames.sort()
        for d in list(dirnames):
            p = Path(dirpath) / d
            if _path_is_symlink(p):
                raise Refusal("SOURCE_SYMLINK", str(p))
            if d.startswith(".") or d == "__pycache__":
                raise Refusal("HIDDEN_OR_SPECIAL_MEMBER", str(p))
        for f in filenames:
            p = Path(dirpath) / f
            if _path_is_symlink(p):
                raise Refusal("SOURCE_SYMLINK", str(p))
            if not p.is_file():
                raise Refusal("SOURCE_SPECIAL_MEMBER", str(p))
            if f.startswith("."):
                raise Refusal("HIDDEN_OR_SPECIAL_MEMBER", str(p))
            files[p.relative_to(repo_root).as_posix()] = canonical_bytes(p.read_bytes())
    return files


# --------------------------------------------------------------------------- output-root gates
def _find_symlink_ancestor(path: Path) -> Path | None:
    for anc in (path, *path.parents):
        if _path_is_symlink(anc):
            return anc
    return None


def check_output_root(out_dir: Path, source_root: Path) -> None:
    symlink = _find_symlink_ancestor(out_dir)
    if symlink is not None:
        raise Refusal("OUTPUT_ROOT_SYMLINK", f"{symlink} is a symlink; refusing to write through it")
    out_res = out_dir.resolve()
    repo_res = source_root.resolve()
    dist_res = (repo_res / "dist").resolve()
    if out_res == dist_res or dist_res in out_res.parents:
        raise Refusal("OUTPUT_ROOT_IN_DIST",
                      f"output root {out_res} is inside the release directory {dist_res}")
    if out_res == repo_res or repo_res in out_res.parents:
        raise Refusal("OUTPUT_ROOT_OVERLAPS_REPO",
                      f"output root {out_res} overlaps the repository {repo_res}")
    if out_res in repo_res.parents:
        raise Refusal("OUTPUT_ROOT_OVERLAPS_REPO",
                      f"output root {out_res} is an ancestor of the repository {repo_res}")
    if os.name == "posix" and out_dir.exists() and (os.stat(out_dir).st_mode & 0o002):
        raise Refusal("OUTPUT_ROOT_WORLD_WRITABLE", f"output root {out_dir} is world-writable")


# --------------------------------------------------------------------------- ZIP
def _write_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for arcname in sorted(members):
            info = zipfile.ZipInfo(arcname, date_time=FIXED_DATE_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = FIXED_MODE << 16
            info.create_system = 0
            zf.writestr(info, members[arcname], compress_type=zipfile.ZIP_DEFLATED,
                        compresslevel=COMPRESS_LEVEL)


def _exclusive_write(path: Path, data: bytes) -> None:
    """Create a release sidecar exclusively; refuse a pre-existing path of any kind.

    ``Path.write_bytes`` opens an existing name and truncates the inode behind it, so an attacker who
    can prepopulate the output directory - with a symlink, or with a hardlink to a file outside it -
    can make the builder overwrite that file. Measured against this tool as AO-01 of the round's
    independent acceptance challenge. ``O_EXCL`` refuses any pre-existing name (a hardlink is an
    ordinary regular file, so only exclusivity closes it) and ``O_NOFOLLOW`` refuses a symlink.
    """
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o644)
    except FileExistsError as exc:
        raise Refusal("OUTPUT_MEMBER_EXISTS",
                      f"{path} already exists; refusing to overwrite an existing release member") from exc
    except OSError as exc:
        raise Refusal("OUTPUT_MEMBER_UNSAFE",
                      f"{path} cannot be created exclusively: {exc}") from exc
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
    except BaseException:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def _verify_zip(path: Path, members: dict[str, bytes]) -> None:
    with zipfile.ZipFile(path) as zf:
        infos = zf.infolist()
        if [i.filename for i in infos] != sorted(members):
            raise Refusal("INTERNAL_ZIP_MISMATCH", "member names or order differ from the plan")
        for info in infos:
            if info.date_time != FIXED_DATE_TIME:
                raise Refusal("INTERNAL_ZIP_MISMATCH", f"non-fixed date_time on {info.filename}")
            if (info.external_attr >> 16) != FIXED_MODE:
                raise Refusal("INTERNAL_ZIP_MISMATCH", f"non-fixed mode on {info.filename}")
            if info.compress_type != zipfile.ZIP_DEFLATED:
                raise Refusal("INTERNAL_ZIP_MISMATCH", f"unexpected compression on {info.filename}")
            if zf.read(info.filename) != members[info.filename]:
                raise Refusal("INTERNAL_ZIP_MISMATCH", f"member bytes differ for {info.filename}")


# --------------------------------------------------------------------------- build
def _load_json(path: Path, code: str) -> dict:
    if not path.is_file():
        raise Refusal(code, f"required input is absent: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise Refusal(code, f"{path} is not parseable JSON: {exc}") from exc


def _load_vendor_schema(packaging_root: Path) -> tuple[bytes, dict]:
    """Load the byte-locked official vendor schema: the lock is the ``$id`` AND the exact bytes.

    The bytes fetched once from the Agent Plugins 1.0 specification are committed next to the
    manifests, so this gate can be re-run offline; it is NOT the vendor's own validator, which
    stays NOT_EXECUTED.
    """
    path = packaging_root / VENDOR_SCHEMA_FILENAME
    if not path.is_file():
        raise Refusal("VENDOR_SCHEMA_MISSING", f"the locked vendor schema is absent: {path}")
    data = path.read_bytes()
    try:
        doc = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Refusal("VENDOR_SCHEMA_INVALID", f"{path} is not parseable JSON: {exc}") from exc
    if not isinstance(doc, dict):
        raise Refusal("VENDOR_SCHEMA_INVALID", f"{path} is not a JSON object")
    if doc.get("$id") != VENDOR_SCHEMA_ID:
        raise Refusal("VENDOR_SCHEMA_ID_MISMATCH",
                      f"vendor schema $id is {doc.get('$id')!r}; expected {VENDOR_SCHEMA_ID!r}")
    observed = sha256_bytes(data)
    if observed != VENDOR_SCHEMA_SHA256:
        raise Refusal("VENDOR_SCHEMA_DIGEST_MISMATCH",
                      f"vendor schema bytes hash to {observed}; the locked digest is "
                      f"{VENDOR_SCHEMA_SHA256}")
    return data, doc


def _check_owner_inputs(release: dict, vendor_schema_bytes: bytes, derivations_doc: dict,
                        skill_paths: dict[str, str], ledger_files: dict[str, str]) -> dict[str, dict]:
    """Gate every owner input. The FIRST missing input raises, in canonical skill order."""
    records = derivations_doc.get("derivations")
    if not isinstance(records, list):
        raise Refusal("DERIVATIONS_INVALID", "derivations.json must carry a `derivations` list")
    by_skill: dict[str, dict] = {}
    for record in records:
        if isinstance(record, dict) and isinstance(record.get("skill"), str):
            by_skill[record["skill"]] = record

    for skill in sorted(EXPECTED_SKILLS):
        record = by_skill.get(skill)
        if record is None:
            raise Refusal("OWNER_INPUT_MISSING", DERIVATION_MISSING_TEMPLATE.format(skill=skill))
        source_rel = skill_paths[skill]
        if record.get("source_path") != source_rel:
            raise Refusal("DERIVATION_RECORD_INVALID",
                          f"{skill}: source_path {record.get('source_path')!r} != {source_rel!r}")
        if record.get("source_sha256") != ledger_files.get(source_rel):
            raise Refusal("DERIVATION_SOURCE_MISMATCH",
                          f"{skill}: source_sha256 does not match the frozen ledger")
        if is_placeholder(record.get("approved_by")) or is_placeholder(record.get("approval_receipt")):
            raise Refusal("DERIVATION_RECORD_INVALID",
                          f"{skill}: approved_by / approval_receipt must name the owner approval")
        if not isinstance(record.get("kept_keys"), list) or not isinstance(record.get("dropped_keys"), list):
            raise Refusal("DERIVATION_RECORD_INVALID", f"{skill}: kept_keys/dropped_keys must be lists")

    pinned = release.get("official_schema_sha256")
    if is_placeholder(pinned):
        raise Refusal("OWNER_INPUT_MISSING",
                      "official_schema_sha256 (the digest of the official Agent Plugins vendor "
                      "schema) is not pinned (value is a placeholder)")
    if not HEX64.match(str(pinned)):
        raise Refusal("OFFICIAL_SCHEMA_DIGEST_INVALID",
                      f"official_schema_sha256 is not 64 hex chars: {pinned!r}")
    observed = sha256_bytes(vendor_schema_bytes)
    if pinned != observed:
        raise Refusal("VENDOR_SCHEMA_DIGEST_MISMATCH",
                      f"pinned official_schema_sha256 {pinned} does not match the vendor schema "
                      f"bytes it validates against ({observed})")

    publisher = release.get("publisher") or {}
    if any(is_placeholder(publisher.get(key)) for key in ("name", "identity", "identity_sha256")):
        raise Refusal("OWNER_INPUT_MISSING",
                      "publisher identity is not pinned (name/identity/identity_sha256 are placeholders)")
    if not HEX64.match(str(publisher.get("identity_sha256"))):
        raise Refusal("PUBLISHER_IDENTITY_INVALID", "publisher.identity_sha256 is not 64 hex chars")

    icons = release.get("icons")
    if not isinstance(icons, list) or not icons:
        raise Refusal("OWNER_INPUT_MISSING", "the release bookkeeping pins no icons")
    for icon in icons:
        rel = icon.get("path")
        if is_placeholder(icon.get("sha256")):
            raise Refusal("OWNER_INPUT_MISSING", f"icon digest for '{rel}' is not pinned")
    return by_skill


def build_plugin(*, source_root: Path, ledger: dict, source_commit: str | None,
                 packaging_root: Path, out_dir: Path, generate_icons: bool = False,
                 expected_skills: tuple[str, ...] = EXPECTED_SKILLS) -> dict:
    source_root = Path(source_root).resolve()
    packaging_root = Path(packaging_root).resolve()
    out_dir = Path(out_dir)

    # --- identity gates -----------------------------------------------------------------
    if source_commit is None:
        raise Refusal("SOURCE_COMMIT_NULL", "the pinned source commit is null; refusing to build")
    if not HEX40.match(str(source_commit)):
        raise Refusal("SOURCE_COMMIT_INVALID", f"source commit is not 40 hex chars: {source_commit!r}")
    if source_commit != ledger.get("commit"):
        raise Refusal("SOURCE_COMMIT_MISMATCH",
                      f"source commit {source_commit} != ledger commit {ledger.get('commit')}")

    # --- output-root gates --------------------------------------------------------------
    check_output_root(out_dir, source_root)

    # --- source set vs the frozen ledger ------------------------------------------------
    skills_root = source_root / "skills"
    dirs = _list_skill_dirs(skills_root)
    unexpected = sorted(n for n in dirs if n not in set(expected_skills))
    if unexpected:
        raise Refusal("UNEXPECTED_SKILL",
                      f"the plugin is exactly 8 skills; found extra skill(s) {unexpected}")
    missing_skill = sorted(n for n in expected_skills if n not in dirs)
    if missing_skill:
        raise Refusal("MISSING_SKILL", f"frozen ledger expects skill(s) {missing_skill}")
    if sorted(dirs) != sorted(ledger.get("skills", [])):
        raise Refusal("SKILL_SET_CHANGED", "on-disk skill set != frozen ledger skill set")

    disk_files: dict[str, bytes] = {}
    for name in sorted(dirs):
        disk_files.update(_walk_source_files(source_root, dirs[name]))
    ledger_files = dict(ledger.get("files", {}))
    extra = sorted(set(disk_files) - set(ledger_files))
    missing = sorted(set(ledger_files) - set(disk_files))
    if extra or missing:
        raise Refusal("SOURCE_SET_CHANGED",
                      f"source set changed vs the frozen ledger; extra={extra} missing={missing}")
    for rel in sorted(ledger_files):
        if sha256_bytes(disk_files[rel]) != ledger_files[rel]:
            raise Refusal("SOURCE_DIGEST_MISMATCH", f"{rel} does not match the frozen ledger")

    # --- the official root manifest + the locked vendor schema ---------------------------
    manifest = _load_json(packaging_root / "plugin.json", "MANIFEST_MISSING")
    release = _load_json(packaging_root / RELEASE_BOOKKEEPING_FILENAME,
                         "RELEASE_BOOKKEEPING_MISSING")
    vendor_bytes, vendor_doc = _load_vendor_schema(packaging_root)
    # (a) the official manifest must name the vendor schema it is validated against
    if manifest.get("$schema") != VENDOR_SCHEMA_ID:
        raise Refusal("OFFICIAL_SCHEMA_ID_MISMATCH",
                      f"the root manifest `$schema` must be the vendor $id {VENDOR_SCHEMA_ID!r}, "
                      f"got {manifest.get('$schema')!r}")
    # (b) validate the official manifest against the vendor schema with our own subset validator
    violations = validate_subset(manifest, vendor_doc)
    if violations:
        first = violations[0]
        raise Refusal("MANIFEST_SCHEMA_VIOLATION",
                      f"{first['path']}: {first['keyword']} — {first['message']}")

    # (c) CR-IDENTITY-BIND: the official manifest must carry the SAME identity as the release
    # bookkeeping. The ZIP root directory and the release receipt are both named from the
    # bookkeeping's `plugin_id`, so an official manifest naming something else ships ONE artefact
    # carrying TWO contradicting identities, and a reviewer reading either one alone is misled. The
    # earlier builder validated the manifest's SHAPE only, so a valid-but-different name, or a
    # version bound to nothing, was accepted at exit 0.
    plugin_id = release.get("plugin_id")
    if not isinstance(plugin_id, str) or not plugin_id.strip():
        raise Refusal("RELEASE_IDENTITY_INVALID",
                      "the release bookkeeping carries no non-empty `plugin_id`")
    if manifest.get("name") != plugin_id:
        raise Refusal("MANIFEST_IDENTITY_MISMATCH",
                      f"official manifest `name` {manifest.get('name')!r} != release plugin_id "
                      f"{plugin_id!r}; the ZIP root and the receipt are named from the plugin_id")
    if manifest.get("version") != release.get("version"):
        raise Refusal("MANIFEST_VERSION_MISMATCH",
                      f"official manifest `version` {manifest.get('version')!r} != release version "
                      f"{release.get('version')!r}")
    if manifest.get("license") != release.get("license"):
        raise Refusal("MANIFEST_LICENSE_MISMATCH",
                      f"official manifest `license` {manifest.get('license')!r} != release license "
                      f"{release.get('license')!r}")

    # (d) CR-EXT-UNREVIEWED: only REVIEWED extension namespaces may appear. The locked vendor schema
    # permits arbitrary object-valued namespaces, so without this gate unreviewed content ships.
    extensions = manifest.get("extensions")
    if not isinstance(extensions, dict) or not extensions:
        raise Refusal("MANIFEST_EXTENSIONS_INVALID",
                      "the official manifest must carry a non-empty `extensions` object")
    unreviewed = sorted(set(extensions) - set(REVIEWED_EXTENSION_NAMESPACES))
    if unreviewed:
        raise Refusal("EXTENSION_NAMESPACE_UNREVIEWED",
                      f"unreviewed extension namespace(s) {unreviewed}; the reviewed namespaces are "
                      f"{sorted(REVIEWED_EXTENSION_NAMESPACES)}. Adding one is a review decision, "
                      f"not a build input.")

    # --- PIPD's release bookkeeping + the local subset ------------------------------------
    schema_path = packaging_root / "plugin.schema.json"
    schema_bytes = schema_path.read_bytes() if schema_path.is_file() else None
    if schema_bytes is None:
        raise Refusal("SCHEMA_MISSING", f"local schema subset is absent: {schema_path}")
    try:
        schema_doc = json.loads(schema_bytes.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise Refusal("SCHEMA_INVALID", f"{schema_path} is not parseable JSON: {exc}") from exc
    violations = validate_subset(release, schema_doc)
    if violations:
        first = violations[0]
        raise Refusal("MANIFEST_SCHEMA_VIOLATION",
                      f"plugin.release.json {first['path']}: {first['keyword']} — {first['message']}")
    if sorted(release.get("skills", [])) != sorted(expected_skills):
        raise Refusal("MANIFEST_SCHEMA_VIOLATION",
                      "the release bookkeeping skills must name exactly the eight frozen skills")
    embedded = (manifest.get("extensions") or {}).get(RELEASE_EXTENSION_KEY)
    if embedded != release:
        raise Refusal("RELEASE_EXTENSION_MISMATCH",
                      f"the root manifest extensions[{RELEASE_EXTENSION_KEY!r}] must be the "
                      f"{RELEASE_BOOKKEEPING_FILENAME} object verbatim")

    derivations_doc = _load_json(packaging_root / "derivations.json", "DERIVATIONS_MISSING")

    # --- icons (owner-gated, validated after generation) --------------------------------
    icons = release.get("icons") or []
    if generate_icons:
        for icon in icons:
            target = packaging_root / icon["path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(png_icon_bytes(int(icon.get("size", 128))))

    # --- owner-input gate (FIRST missing input refuses, deterministically) --------------
    skill_paths = {name: f"skills/{name}/SKILL.md" for name in expected_skills}
    records = _check_owner_inputs(release, vendor_bytes, derivations_doc, skill_paths, ledger_files)

    for icon in icons:
        target = packaging_root / icon["path"]
        if not target.is_file() or _path_is_symlink(target):
            raise Refusal("ICON_MISSING", f"pinned icon is absent or not a regular file: {target}")
        data = target.read_bytes()
        if sha256_bytes(data) != icon["sha256"]:
            raise Refusal("ICON_DIGEST_MISMATCH", f"{icon['path']} does not match its pinned digest")
        problems = png_errors(data)
        if problems:
            raise Refusal("ICON_INVALID", f"{icon['path']}: {problems[0]}")

    # --- assemble the plugin member set -------------------------------------------------
    plugin_id = str(release["plugin_id"])
    root = plugin_id
    members: dict[str, bytes] = {}
    mapping_rows: list[dict] = []
    for name in sorted(expected_skills):
        skill_prefix = f"skills/{name}/"
        for rel in sorted(r for r in disk_files if r.startswith(skill_prefix)):
            rest = rel[len(skill_prefix):]
            dest = f"{root}/{rel}"
            if rest == "SKILL.md":
                dest_bytes, _ = project_skill_md(name, disk_files[rel], records[name])
                mode = "DERIVED_WITH_OWNER_APPROVAL"
            else:
                dest_bytes = disk_files[rel]
                mode = "EXACT"
            members[dest] = dest_bytes
            mapping_rows.append({
                "source_path": rel,
                "source_sha256": ledger_files[rel],
                "destination_path": dest,
                "destination_sha256": sha256_bytes(dest_bytes),
                "mode": mode,
            })
    members[f"{root}/plugin.json"] = canonical_json_bytes(manifest)
    members[f"{root}/{RELEASE_BOOKKEEPING_FILENAME}"] = canonical_json_bytes(release)
    members[f"{root}/plugin.schema.json"] = schema_bytes
    members[f"{root}/{VENDOR_SCHEMA_FILENAME}"] = vendor_bytes
    members[f"{root}/derivations.json"] = canonical_json_bytes(derivations_doc)
    for icon in icons:
        members[f"{root}/{icon['path']}"] = (packaging_root / icon["path"]).read_bytes()

    for arcname in members:
        for part in arcname.split("/"):
            if part.startswith(".") or part in ("__pycache__", "Thumbs.db"):
                raise Refusal("HIDDEN_OR_SPECIAL_MEMBER", f"refusing to package {arcname!r}")

    mapping_doc = {
        "schema": "PIPD-PUBLIC-PLUGIN-SOURCE-MAPPING/1",
        "plugin_id": plugin_id,
        "source_commit": source_commit,
        "source_tree": ledger.get("tree"),
        "source_ledger_version": ledger.get("ledger_version"),
        "entries": mapping_rows,
    }
    mapping_bytes = canonical_json_bytes(mapping_doc)
    members[f"{root}/SOURCE_TO_PLUGIN_MAPPING.json"] = mapping_bytes
    receipt_doc = {
        "schema": "PIPD-PUBLIC-PLUGIN-RELEASE-RECEIPT/1",
        "plugin_id": plugin_id,
        "version": release.get("version"),
        "source_commit": source_commit,
        "source_tree": ledger.get("tree"),
        "source_ledger_version": ledger.get("ledger_version"),
        "official_schema_sha256": str(release.get("official_schema_sha256")),
        "official_schema_id": VENDOR_SCHEMA_ID,
        "claim_ceiling": "LOCAL_PACKAGER_PASS_ONLY",
        "official_portal_verification": "NOT_EXECUTED",
        "member_count": len(members) + 1,
        "mapping_sha256": sha256_bytes(mapping_bytes),
        "determinism": {"zip_mtime": "1980-01-01T00:00:00Z", "mode": "0644",
                        "compression": "DEFLATED:9"},
    }
    receipt_bytes = canonical_json_bytes(receipt_doc)
    members[f"{root}/RELEASE_RECEIPT.json"] = receipt_bytes

    # --- deterministic ZIP, read-back verify, then promote ------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)
    if _path_is_symlink(out_dir):
        raise Refusal("OUTPUT_ROOT_SYMLINK", f"{out_dir} became a symlink; refusing to write")
    final_zip = out_dir / f"{plugin_id}.zip"
    if _path_is_symlink(final_zip) or final_zip.exists():
        raise Refusal("OUTPUT_ARTIFACT_EXISTS",
                      f"{final_zip} already exists; refusing to replace an existing release artifact")
    fd, tmp_name = tempfile.mkstemp(prefix=".public-plugin-", suffix=".zip", dir=str(out_dir))
    os.close(fd)
    tmp_zip = Path(tmp_name)
    sidecar = final_zip.with_name(final_zip.name + ".sha256")
    mapping_path = out_dir / "SOURCE_TO_PLUGIN_MAPPING.json"
    receipt_path = out_dir / "RELEASE_RECEIPT.json"
    promoted = False
    created: list[Path] = []
    try:
        _write_zip(tmp_zip, members)
        _verify_zip(tmp_zip, members)
        # The sidecars are created EXCLUSIVELY and BEFORE the artifact is promoted, so a pre-seeded
        # output member refuses the whole build while nothing has been published yet. Only members
        # this call actually created are rolled back: a member that was already there (and caused the
        # refusal) is left exactly as the attacker/operator left it, never deleted.
        digest = sha256_bytes(tmp_zip.read_bytes())
        for target, payload in ((sidecar, f"{digest}  {final_zip.name}\n".encode("utf-8")),
                                (mapping_path, mapping_bytes),
                                (receipt_path, receipt_bytes)):
            _exclusive_write(target, payload)
            created.append(target)
        os.replace(tmp_zip, final_zip)
        promoted = True
    finally:
        if tmp_zip.exists():
            tmp_zip.unlink()
        if not promoted:
            for partial in created:
                if partial.exists() and not _path_is_symlink(partial):
                    try:
                        partial.unlink()
                    except OSError:
                        pass

    return {
        "verdict": "BUILT",
        "out_zip": str(final_zip),
        "zip_sha256": digest,
        "sidecar": str(sidecar),
        "member_count": len(members),
        "mapping": str(mapping_path),
        "receipt": str(receipt_path),
        "claim_ceiling": "LOCAL_PACKAGER_PASS_ONLY",
        "official_portal_verification": "NOT_EXECUTED",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    default_repo = Path(__file__).resolve().parents[1]
    ap.add_argument("--source-root", default=str(default_repo))
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--source-commit", default=None)
    ap.add_argument("--packaging-root", default=None)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--generate-icons", action="store_true")
    args = ap.parse_args(argv)
    source_root = Path(args.source_root).resolve()
    packaging_root = (Path(args.packaging_root) if args.packaging_root
                      else source_root / "packaging" / "public-plugin")
    try:
        ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"REFUSED LEDGER_UNREADABLE: {exc}")
        return 2
    try:
        report = build_plugin(
            source_root=source_root,
            ledger=ledger,
            source_commit=args.source_commit,
            packaging_root=packaging_root,
            out_dir=Path(args.out_dir),
            generate_icons=args.generate_icons,
        )
    except Refusal as exc:
        print(str(exc))
        return 2
    print(f"BUILT {report['out_zip']} sha256={report['zip_sha256']} "
          f"members={report['member_count']} "
          f"claim_ceiling={report['claim_ceiling']} "
          f"official_portal_verification={report['official_portal_verification']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
