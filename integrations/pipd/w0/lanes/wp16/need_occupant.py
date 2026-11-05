#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-16 -- Default30 Need -> Occupant matrix generator.

Reads (never writes) the W0 R4C source root and emits:

  * NEED_OCCUPANT_MATRIX.json / .md   30 Need rows with License / Windows-fit /
                                      Consumer / NOFIT columns, declared-vs-computed
                                      count comparison against CURRENT_CANDIDATE_STATE
  * TRANSLATOR_MAP.json               one translator spec per *selected* Donor24/Method25
                                      item; every spec carries is_installer=false
  * TECH_CHOICE_READBACK.json         per-Selected readback evidence (file, pointer,
                                      value, verify_method, verified) or UNBOUND

Hard rules encoded here (not merely documented):

  R1  No license value or Windows-fit value is ever invented.  Every emitted value is
      a byte-literal copy of a field of a named source file, or the literal string
      ``UNBOUND`` accompanied by a named HOLD.
  R2  ``install_state`` may only be NOT_INSTALLED / PIN_HOLD / HOST_PIN_HOLD.
      INSTALLED and VERIFIED are not representable: passing them raises
      INSTALL_STATE_FORBIDDEN.
  R3  A Donor24/Method25 item is a *translation recipe*, never an installer.  Any
      request to install through one raises METHOD_NOT_INSTALLER (the source corpus'
      own first-fail token METHOD_AS_INSTALL_DENY is carried alongside).
  R4  Nothing is installed, upgraded or downloaded by this tool.  There is no
      subprocess, network, or filesystem write outside ``--out``.

Status precedence (evaluated in this order, first hit wins):

  1. OCCUPANT_UNBOUND            -> status UNBOUND
  2. LICENSE_UNBOUND             -> status UNBOUND
  3. WINDOWS_NOFIT               -> status NOFIT
  4. NEED_REQUIRED_DOWNGRADE     -> status UNBOUND
  5. declared hold HOST_PIN_HOLD     -> status HOST_PIN_HOLD
  6. declared hold OCCUPANT_PIN_HOLD -> status OCCUPANT_PIN_HOLD
  7. otherwise                   -> status SELECTED

On the real W0 R4C sources rules 1-4 never fire, so the computed split is
28 OCCUPANT_PIN_HOLD + 2 HOST_PIN_HOLD; that split is then compared against the
declaration in CURRENT_CANDIDATE_STATE.gate_results[G3_TECH].evidence and against
the per-section state lines of W0_R3_TECH_CHOICE_AND_TRANSLATION.md.  Any divergence
is emitted as a named MISMATCH entry -- declared numbers are never overwritten.

CLI:
    python need_occupant.py --source-root <DIR> --out <DIR>

Exit codes: 0 clean, 1 MISMATCH present, 2 input/identity error, 3 hard refusal.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

SCHEMA_VERSION = "wp-fhs-16/1"
LANE = "WP-FHS-16"

# ---------------------------------------------------------------- vocabularies

STATUS_SELECTED = "SELECTED"
STATUS_OCCUPANT_PIN_HOLD = "OCCUPANT_PIN_HOLD"
STATUS_HOST_PIN_HOLD = "HOST_PIN_HOLD"
STATUS_NOFIT = "NOFIT"
STATUS_UNBOUND = "UNBOUND"
ALLOWED_STATUS = (
    STATUS_SELECTED,
    STATUS_OCCUPANT_PIN_HOLD,
    STATUS_HOST_PIN_HOLD,
    STATUS_NOFIT,
    STATUS_UNBOUND,
)

INSTALL_NOT_INSTALLED = "NOT_INSTALLED"
INSTALL_PIN_HOLD = "PIN_HOLD"
INSTALL_HOST_PIN_HOLD = "HOST_PIN_HOLD"
ALLOWED_INSTALL_STATE = (INSTALL_NOT_INSTALLED, INSTALL_PIN_HOLD, INSTALL_HOST_PIN_HOLD)
FORBIDDEN_INSTALL_STATES = ("INSTALLED", "VERIFIED")

KIND_DONOR = "DONOR"
KIND_METHOD = "METHOD"
KIND_HOST = "HOST"
KIND_NONE = "NONE"
ALLOWED_KIND = (KIND_DONOR, KIND_METHOD, KIND_HOST, KIND_NONE)
_KIND_RANK = {KIND_DONOR: 3, KIND_METHOD: 2, KIND_HOST: 1, KIND_NONE: 0}

# ---------------------------------------------------------------- refusal codes

R_OCCUPANT_UNBOUND = "OCCUPANT_UNBOUND"
R_LICENSE_UNBOUND = "LICENSE_UNBOUND"
R_WINDOWS_NOFIT = "WINDOWS_NOFIT"
R_METHOD_NOT_INSTALLER = "METHOD_NOT_INSTALLER"
R_NEED_REQUIRED_DOWNGRADE = "NEED_REQUIRED_DOWNGRADE"
R_INSTALL_STATE_FORBIDDEN = "INSTALL_STATE_FORBIDDEN"
R_INPUT_SHA_MISMATCH = "INPUT_SHA_MISMATCH"
R_TRANSLATION_ITEM_ABSENT = "TRANSLATION_ITEM_ABSENT"
R_ALIAS_EVIDENCE_MISSING = "ALIAS_EVIDENCE_MISSING"
R_UNKNOWN_TRANSLATOR = "UNKNOWN_TRANSLATOR"
R_NEED_CLASS_UNBOUND = "NEED_CLASS_UNBOUND"
R_NOFIT_REASON_UNBOUND = "NOFIT_REASON_UNBOUND"
R_SOURCE_FILE_ABSENT = "SOURCE_FILE_ABSENT"
R_ROW_SHA_MISMATCH = "ROW_SHA_MISMATCH"

# license field states
LIC_DECLARED = "LICENSE_DECLARED"
LIC_DECLARED_ACK_PENDING = "LICENSE_DECLARED_HOST_ACK_PENDING"
LIC_READER_HOLD = "LICENSE_READER_HOLD"
LIC_UNBOUND = "LICENSE_UNBOUND"

# windows fit states
FIT_UNBOUND = "UNBOUND"
FIT_FIT = "FIT"
FIT_NOFIT = "NOFIT"

REQUIRED_MARKER = "DESIGN_DEFAULT_REQUIRED"

# Source corpus' own token for "a method was used as an installer"; kept as a
# cross-reference only -- the lane's contract code is METHOD_NOT_INSTALLER.
CORPUS_METHOD_AS_INSTALL = "METHOD_AS_INSTALL_DENY"


class Refusal(Exception):
    """A contract refusal with a stable machine code."""

    def __init__(self, code, detail, **extra):
        self.code = code
        self.detail = detail
        self.extra = extra
        super().__init__("%s: %s" % (code, detail))

    def to_dict(self):
        out = {"code": self.code, "detail": self.detail}
        out.update(self.extra)
        return out


# ---------------------------------------------------------------- file helpers


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    with open(path, "rb") as fh:
        return sha256_bytes(fh.read())


def read_json(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_json(path, obj):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")


def write_text(path, text):
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def resolve_pointer(document, pointer):
    """Resolve an RFC6901-ish JSON pointer ("/12/license"). Raises KeyError."""
    if pointer in ("", "/"):
        return document
    node = document
    for raw in pointer.split("/"):
        if raw == "":
            continue
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            node = node[int(token)]
        elif isinstance(node, dict):
            node = node[token]
        else:
            raise KeyError(pointer)
    return node


def pointer_ok(document, pointer):
    try:
        resolve_pointer(document, pointer)
        return True
    except (KeyError, IndexError, ValueError, TypeError):
        return False


def ref(file_name, pointer):
    return "%s#%s" % (file_name, pointer)


# ---------------------------------------------------------------- source bundle

FILE_DEFAULT30 = "DEFAULT30_CHOICES.json"
FILE_WP16 = "WP16_TRANSLATION49.json"
FILE_TECH485 = "TECH485_COMPACT_REGISTRY.json"
FILE_CCS = "CURRENT_CANDIDATE_STATE.json"
FILE_MANIFEST = "INDEX_AND_MANIFEST_r4-candidate-b41d2e.json"
FILE_R3_MD = "W0_R3_TECH_CHOICE_AND_TRANSLATION.md"
FILE_TECH_ROWS = "W0_R2_TRACE_TECH_485.md"
FILE_NEG_NEED = os.path.join("negative_fixtures", "NEG-NEED.mutated.json")

REQUIRED_FILES = (FILE_DEFAULT30, FILE_WP16)
OPTIONAL_FILES = (
    FILE_TECH485,
    FILE_CCS,
    FILE_MANIFEST,
    FILE_R3_MD,
    FILE_TECH_ROWS,
    FILE_NEG_NEED,
)


class Sources(object):
    """Immutable view over the W0 R4C source root. Read-only by construction."""

    def __init__(self, root):
        self.root = root
        self.files = {}          # name -> info dict
        self.holds = []          # named holds discovered while loading
        self.default30 = []
        self.wp16 = []
        self.tech485 = []
        self.ccs = None
        self.manifest = None
        self.r3_text = ""
        self.r3_sections = []
        self.tech_row_lines = []
        self.neg_need_mutated = None
        self._load()

    # -- loading ---------------------------------------------------------
    def _path(self, name):
        return os.path.join(self.root, name)

    def _register(self, name, data, declared_sha):
        actual = sha256_bytes(data)
        info = {
            "file": name,
            "bytes": len(data),
            "sha256": actual,
            "declared_sha256": declared_sha,
            "identity": "MATCH" if declared_sha == actual else ("UNBOUND" if not declared_sha else "MISMATCH"),
        }
        self.files[name] = info
        if info["identity"] == "MISMATCH":
            self.holds.append(
                {
                    "code": R_INPUT_SHA_MISMATCH,
                    "file": name,
                    "declared_sha256": declared_sha,
                    "actual_sha256": actual,
                }
            )
        return info

    def _load(self):
        if not os.path.isdir(self.root):
            raise Refusal(R_SOURCE_FILE_ABSENT, "source root is not a directory", path=self.root)
        for name in REQUIRED_FILES:
            if not os.path.isfile(self._path(name)):
                raise Refusal(R_SOURCE_FILE_ABSENT, "required source file missing", file=name)

        manifest = None
        if os.path.isfile(self._path(FILE_MANIFEST)):
            try:
                manifest = read_json(self._path(FILE_MANIFEST))
            except ValueError:
                manifest = None
        self.manifest = manifest
        declared = {}
        if isinstance(manifest, dict):
            for entry in manifest.get("files") or []:
                if isinstance(entry, dict) and "path" in entry:
                    declared[entry["path"].replace("\\", "/")] = entry.get("sha256")

        for name in REQUIRED_FILES + OPTIONAL_FILES:
            path = self._path(name)
            if not os.path.isfile(path):
                self.holds.append({"code": R_SOURCE_FILE_ABSENT, "file": name, "detail": "optional source file absent"})
                continue
            with open(path, "rb") as fh:
                data = fh.read()
            self._register(name.replace("\\", "/"), data, declared.get(name.replace("\\", "/")))

        self.default30 = read_json(self._path(FILE_DEFAULT30))
        self.wp16 = read_json(self._path(FILE_WP16))
        if not isinstance(self.default30, list) or not isinstance(self.wp16, list):
            raise Refusal(R_SOURCE_FILE_ABSENT, "DEFAULT30_CHOICES.json / WP16_TRANSLATION49.json must be JSON arrays")

        if FILE_TECH485 in self.files:
            self.tech485 = read_json(self._path(FILE_TECH485))
        if FILE_CCS in self.files:
            self.ccs = read_json(self._path(FILE_CCS))
        if FILE_R3_MD in self.files:
            self.r3_text = read_text(self._path(FILE_R3_MD))
            self.r3_sections = parse_r3_sections(self.r3_text)
        if FILE_TECH_ROWS in self.files:
            self.tech_row_lines = read_text(self._path(FILE_TECH_ROWS)).split("\n")
        if FILE_NEG_NEED in self.files:
            self.neg_need_mutated = read_json(self._path(FILE_NEG_NEED))

    # -- queries ---------------------------------------------------------
    def tech485_by_id(self):
        out = {}
        for row in self.tech485:
            if isinstance(row, dict) and row.get("original_id"):
                out.setdefault(row["original_id"], []).append(row)
        return out

    def file_sha(self, name):
        info = self.files.get(name)
        return info["sha256"] if info else "UNBOUND"

    def verified_rows(self):
        """How many TECH485 rows this lane re-hashed successfully."""
        good = bad = 0
        for row in self.tech485:
            if not isinstance(row, dict):
                continue
            ok, _ = verify_row_sha(self.tech_row_lines, row)
            if ok:
                good += 1
            else:
                bad += 1
        return {"verified": good, "failed": bad, "total": good + bad}


def verify_row_sha(lines, row):
    """Recompute the registry's row_sha over the named physical line."""
    line_no = row.get("line")
    expected = row.get("row_sha")
    if not isinstance(line_no, int) or not isinstance(expected, str):
        return False, "row_missing_line_or_sha"
    if line_no < 1 or line_no > len(lines):
        return False, "line_out_of_range"
    raw = lines[line_no - 1]
    for candidate in (raw, raw.rstrip("\r"), raw.strip()):
        if sha256_bytes(candidate.encode("utf-8")) == expected:
            return True, "sha256(line)"
    return False, "sha_mismatch"


def parse_r3_sections(text):
    """Parse `## <id> -- <name>` sections of the r3 tech-choice md.

    Returns dict id -> {"name", "line", "state", "state_line", "windows_fit",
    "license_literal"} -- each value copied literally out of the md.
    """
    out = {}
    current = None
    for idx, line in enumerate(text.split("\n"), 1):
        head = re.match(r"^##\s+((?:Default30|Donor24|Method25):[A-Z0-9\-]+)\s+[—-]\s+(.+?)\s*$", line)
        if head:
            current = {"id": head.group(1), "name": head.group(2), "line": idx, "state": None, "state_line": None,
                       "windows_fit": None, "license_literal": None}
            out[head.group(1)] = current
            continue
        if line.startswith("## "):
            current = None
            continue
        if current is None:
            continue
        if current["state"] is None:
            hit = re.search(r"state\s*`([A-Z_]+)`", line)
            if hit:
                current["state"] = hit.group(1)
                current["state_line"] = idx
        if current["windows_fit"] is None:
            hit = re.search(r"Windows Fit\s*`([^`]+)`", line)
            if hit:
                current["windows_fit"] = hit.group(1)
        if current["license_literal"] is None:
            hit = re.search(r"License：(.+?)。(?:Action：|$)", line)
            if hit:
                current["license_literal"] = hit.group(1).strip()
    return out


# ---------------------------------------------------------------- selection

# Which Default30 Need is served by which Donor24 / Method25 item.
#
# Every rule names the *basis* on which the binding is asserted; the predicate is
# re-evaluated against the real WP16 rows at run time and the resolved ids must
# exist, so a stale or fabricated rule fails loudly instead of silently binding.
#
#   EXACT_NAME          normalised equality of the WP16 row name with `expected`
#   NORMALISED_NAME     equality after separator/version normalisation
#   NAME_CONTAINS       normalised `expected` occurs inside the normalised WP16 name
#   TOKEN_CONTAINS      `alias_token` occurs as a whole token of the WP16 name
#   LITERAL_ALIAS       WP16 name == `expected` AND `alias_token` occurs literally in
#                       one of the Need's own fields (listed in `alias_fields`)
SELECTION_RULES = (
    {"need_id": "Default30:P0-TOOL-010", "basis": "EXACT_NAME", "expected": "Spec Kit"},
    {"need_id": "Default30:P0-TOOL-011", "basis": "EXACT_NAME", "expected": "OpenSpec"},
    {"need_id": "Default30:P0-TOOL-016", "basis": "NORMALISED_NAME", "expected": "mattpocock/skills"},
    {"need_id": "Default30:P0-TOOL-017", "basis": "TOKEN_CONTAINS", "expected": "mattpocock/skills:grill-with-docs",
     "alias_token": "grill"},
    {"need_id": "Default30:P0-TOOL-020", "basis": "EXACT_NAME", "expected": "Superpowers"},
    {"need_id": "Default30:P0-TOOL-024", "basis": "NAME_CONTAINS", "expected": "Agent Skills"},
    {"need_id": "Default30:P0-TOOL-025", "basis": "LITERAL_ALIAS", "expected": "MCP", "alias_token": "MCP",
     "alias_fields": ("original_consumer", "hold_owner", "original_business")},
    {"need_id": "Default30:P0-TOOL-059", "basis": "EXACT_NAME", "expected": "Semgrep"},
    {"need_id": "Default30:P0-TOOL-060", "basis": "EXACT_NAME", "expected": "CodeQL"},
    {"need_id": "Default30:P0-TOOL-061", "basis": "EXACT_NAME", "expected": "Trivy"},
    {"need_id": "Default30:P0-TOOL-062", "basis": "EXACT_NAME", "expected": "GitHub Actions"},
    {"need_id": "Default30:P0-TOOL-063", "basis": "EXACT_NAME", "expected": "OpenSSF Scorecard"},
    {"need_id": "Default30:P0-TOOL-064", "basis": "LITERAL_ALIAS", "expected": "Syft", "alias_token": "Syft",
     "alias_fields": ("original_business", "original_consumer", "hold_owner")},
    {"need_id": "Default30:P0-TOOL-065", "basis": "LITERAL_ALIAS", "expected": "Cosign", "alias_token": "Cosign",
     "alias_fields": ("original_consumer", "hold_owner", "original_business")},
    {"need_id": "Default30:P0-TOOL-072", "basis": "NAME_CONTAINS", "expected": "SQLite"},
)

_VERSION_RE = re.compile(r"\bv?\d+(?:\.\d+)*\b")


def norm_name(value):
    if not isinstance(value, str):
        return ""
    text = value.strip().lower()
    text = _VERSION_RE.sub(" ", text)
    text = re.sub(r"[/:_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _wp16_name(row):
    return row.get("name") if isinstance(row, dict) else None


def _wp16_kind(row):
    ident = str(row.get("original_id", ""))
    if ident.startswith("Donor24:"):
        return KIND_DONOR
    if ident.startswith("Method25:"):
        return KIND_METHOD
    return KIND_NONE


def rule_matches(rule, wp16_row, need_record):
    basis = rule["basis"]
    name = _wp16_name(wp16_row)
    expected = rule.get("expected")
    if not isinstance(name, str):
        return False
    if basis in ("EXACT_NAME", "NORMALISED_NAME"):
        return norm_name(name) == norm_name(expected)
    if basis == "NAME_CONTAINS":
        needle = norm_name(expected)
        return bool(needle) and needle in norm_name(name)
    if basis == "TOKEN_CONTAINS":
        token = norm_name(rule.get("alias_token") or expected)
        return bool(token) and token in norm_name(name).split(" ")
    if basis == "LITERAL_ALIAS":
        if norm_name(name) != norm_name(expected):
            return False
        return alias_evidence(rule, need_record)["found"]
    return False


def alias_evidence(rule, need_record):
    """Locate the declared alias token inside the Need's own literal fields."""
    token = rule.get("alias_token") or rule.get("expected") or ""
    for field_name in rule.get("alias_fields") or ():
        value = need_record.get(field_name)
        if isinstance(value, str) and token in value:
            return {
                "found": True,
                "field": field_name,
                "token": token,
                "snippet": _snippet(value, token),
            }
    return {"found": False, "field": None, "token": token, "snippet": None}


def _snippet(text, token, width=90):
    pos = text.find(token)
    if pos < 0:
        return ""
    start = max(0, pos - width // 2)
    end = min(len(text), pos + len(token) + width // 2)
    return text[start:end].replace("\n", " ")


def select_items(sources, overrides=None):
    """Resolve Default30 Need -> selected Donor24/Method25 items.

    Returns (bindings, unnamed_holds). ``bindings`` maps need_id -> list of
    binding dicts. A rule that cannot be satisfied yields a named hold instead of
    a silent empty list.
    """
    overrides = overrides or {}
    by_id = {row.get("original_id"): row for row in sources.default30 if isinstance(row, dict)}
    wp16_ids = {row.get("original_id") for row in sources.wp16 if isinstance(row, dict)}
    bindings = {}
    holds = []
    for rule in SELECTION_RULES:
        need_id = rule["need_id"]
        record = by_id.get(need_id)
        if record is None:
            holds.append({"code": R_TRANSLATION_ITEM_ABSENT, "need_id": need_id, "detail": "need absent from DEFAULT30_CHOICES.json"})
            continue
        if need_id in overrides:
            record = dict(record)
            record.update({k: v for k, v in overrides[need_id].items() if k in record or k in ("selected_occupant",)})
        matched = []
        for row in sources.wp16:
            if not isinstance(row, dict):
                continue
            if rule_matches(rule, row, record):
                matched.append(row)
        if not matched:
            code = R_ALIAS_EVIDENCE_MISSING if rule["basis"] == "LITERAL_ALIAS" else R_TRANSLATION_ITEM_ABSENT
            detail = "no WP16 row satisfies basis %s for %r" % (rule["basis"], rule.get("expected"))
            holds.append({"code": code, "need_id": need_id, "detail": detail})
            continue
        rows = []
        for row in matched:
            ident = row.get("original_id")
            if ident not in wp16_ids:
                holds.append({"code": R_TRANSLATION_ITEM_ABSENT, "need_id": need_id, "detail": "resolved id missing"})
                continue
            binding = {
                "wp16_id": ident,
                "kind": _wp16_kind(row),
                "wp16_name": row.get("name"),
                "basis": rule["basis"],
                "expected": rule.get("expected"),
                "state": row.get("state"),
            }
            if rule["basis"] == "LITERAL_ALIAS":
                binding["alias_evidence"] = alias_evidence(rule, record)
            rows.append(binding)
        if rows:
            bindings.setdefault(need_id, []).extend(rows)
    return bindings, holds


# ---------------------------------------------------------------- field logic

_NOFIT_RE = re.compile(r"退場/NoFit[：:]\s*(.*?)(?:；\s*SELECTED_SOURCE|；\s*DETACH_ADAPTER|$)", re.S)
_LICENSE_HOLD_TOKEN = re.compile(r"HOLD|UNBOUND|DISCOVERY|UNRESOLVED|PENDING", re.I)
_SPDXISH = re.compile(r"\b(MIT|Apache(?:-2\.0)?|BSD(?:-[0-9]-\w+)?|ISC|MPL-2\.0|GPL-2\.0|GPL-3\.0|LGPL-3\.0|AGPL-3\.0|Unlicense)\b")


def classify_license(value):
    """Literal license text -> (state, reason). Never fabricates a license."""
    if value is None:
        return LIC_UNBOUND, "license field absent"
    if not isinstance(value, str) or not value.strip():
        return LIC_UNBOUND, "license field blank"
    text = value.strip()
    if text.upper() in ("UNBOUND", "LICENSE_UNBOUND"):
        return LIC_UNBOUND, "license declared UNBOUND"
    has_id = bool(_SPDXISH.search(text))
    has_hold = bool(_LICENSE_HOLD_TOKEN.search(text))
    if has_id and has_hold:
        return LIC_DECLARED_ACK_PENDING, "upstream license id present, Host/Reader clause still pending"
    if has_id:
        return LIC_DECLARED, "license id present in source literal"
    if has_hold:
        return LIC_READER_HOLD, "source literal carries a License/Reader HOLD"
    return LIC_READER_HOLD, "no license id and no explicit release in source literal"


def normalise_windows_fit(value):
    if value is False:
        return FIT_NOFIT, "source value is boolean false"
    if value is True:
        return FIT_FIT, "source value is boolean true"
    if value is None:
        return FIT_UNBOUND, "no windows_fit value in source"
    text = str(value)
    upper = text.upper()
    if "HOST_FIT_UNBOUND" in upper or "WINDOWS_FIT_UNBOUND" in upper or upper.strip() == "UNBOUND":
        return FIT_UNBOUND, "source literal declares UNBOUND"
    if "NOFIT" in upper or "NO_FIT" in upper or "NOT_SUPPORTED" in upper:
        return FIT_NOFIT, "source literal declares NOFIT"
    if "HOST_FIT_" in upper or "WINDOWS_FIT" in upper:
        return FIT_FIT, "source literal declares an explicit fit"
    return FIT_UNBOUND, "no recognised fit token in source literal"


def need_class_of(record):
    consumer = record.get("original_consumer") or ""
    owner = record.get("hold_owner") or ""
    for candidate in (consumer, owner):
        hit = re.match(r"^\s*([A-Z][A-Z0-9_]*)\.[A-Z0-9_]", candidate)
        if hit:
            return hit.group(1)
    return None


def nofit_reason_of(record):
    blob = record.get("original_business") or ""
    hit = _NOFIT_RE.search(blob)
    if hit:
        return hit.group(1).strip()
    return None


def allowed_install_state(hold_value, override=None):
    if override is not None:
        if override not in ALLOWED_INSTALL_STATE:
            raise Refusal(
                R_INSTALL_STATE_FORBIDDEN,
                "install_state %r is not permitted" % (override,),
                allowed=list(ALLOWED_INSTALL_STATE),
            )
        return override
    if hold_value == STATUS_HOST_PIN_HOLD:
        return INSTALL_HOST_PIN_HOLD
    if hold_value == STATUS_OCCUPANT_PIN_HOLD:
        return INSTALL_PIN_HOLD
    if hold_value is None or hold_value == "":
        return INSTALL_NOT_INSTALLED
    if hold_value in ALLOWED_INSTALL_STATE:
        return hold_value
    raise Refusal(
        R_INSTALL_STATE_FORBIDDEN,
        "declared hold %r cannot map to an install_state" % (hold_value,),
        allowed=list(ALLOWED_INSTALL_STATE),
    )


# ---------------------------------------------------------------- matrix build


def _evidence(file_name, pointer, value, sources, verify):
    return {
        "source_file": file_name,
        "pointer": pointer,
        "ref": ref(file_name, pointer),
        "value": value,
        "source_sha256": sources.file_sha(file_name),
        "verify": verify,
    }


def build_row(record, index, bindings, sources, overrides, ctx):
    need_id = record.get("original_id")
    ov = overrides.get(need_id) or {}
    refusals = []
    unbound_fields = []

    occupant_id = ov["selected_occupant"] if "selected_occupant" in ov else record.get("selected_occupant")
    occupant_id = occupant_id.strip() if isinstance(occupant_id, str) else occupant_id

    need_class = need_class_of(record)
    if not need_class:
        need_class = "UNBOUND"
        refusals.append({"code": R_NEED_CLASS_UNBOUND, "detail": "no namespaced consumer prefix"})
        unbound_fields.append({"field": "need_class", "code": R_NEED_CLASS_UNBOUND})

    required_declared = ov.get("required", record.get("required"))
    required = required_declared == REQUIRED_MARKER
    if not required:
        refusals.append(
            {
                "code": R_NEED_REQUIRED_DOWNGRADE,
                "detail": "required is %r, not %s" % (required_declared, REQUIRED_MARKER),
                "pointer": ref(FILE_DEFAULT30, "/%d/required" % index),
            }
        )

    # ---- occupant
    kind = KIND_NONE
    if not occupant_id:
        refusals.append({"code": R_OCCUPANT_UNBOUND, "detail": "selected_occupant is empty"})
        unbound_fields.append({"field": "occupant_id", "code": R_OCCUPANT_UNBOUND})
    else:
        for binding in bindings:
            if _KIND_RANK[binding["kind"]] > _KIND_RANK[kind]:
                kind = binding["kind"]
        if kind == KIND_NONE:
            kind = KIND_HOST
    if ov.get("occupant_kind_override"):
        kind = ov["occupant_kind_override"]
    if kind not in ALLOWED_KIND:
        raise Refusal(R_OCCUPANT_UNBOUND, "occupant_kind %r invalid" % (kind,))

    # ---- license
    if "license" in ov:
        license_literal = ov["license"]
    else:
        license_literal = record.get("license")
    license_state, license_reason = classify_license(license_literal)
    license_source_ref = ref(FILE_DEFAULT30, "/%d/license" % index)
    license_evidence = _evidence(
        FILE_DEFAULT30,
        "/%d/license" % index,
        license_literal,
        sources,
        "byte-literal copy of DEFAULT30_CHOICES.json field" if pointer_ok(sources.default30, "/%d/license" % index) else "pointer unresolved",
    )
    if license_state == LIC_UNBOUND:
        refusals.append({"code": R_LICENSE_UNBOUND, "detail": license_reason, "pointer": license_source_ref})
        unbound_fields.append({"field": "license", "code": R_LICENSE_UNBOUND})
        license_value = "UNBOUND"
    else:
        license_value = license_literal

    # ---- windows fit
    if "windows_fit" in ov:
        fit_raw = ov["windows_fit"]
        fit_source_ref = "OVERRIDE"
        fit_evidence = {"source_file": "OVERRIDE", "pointer": "OVERRIDE", "ref": "OVERRIDE",
                        "value": fit_raw, "source_sha256": "OVERRIDE", "verify": "test override"}
    else:
        fit_raw = record.get("fit")
        fit_source_ref = ref(FILE_DEFAULT30, "/%d/fit" % index)
        fit_evidence = _evidence(FILE_DEFAULT30, "/%d/fit" % index, fit_raw, sources, "byte-literal copy of DEFAULT30_CHOICES.json field")
    fit_state, fit_reason = normalise_windows_fit(fit_raw)
    if fit_state == FIT_NOFIT:
        refusals.append({"code": R_WINDOWS_NOFIT, "detail": fit_reason, "pointer": fit_source_ref})
    elif fit_state == FIT_UNBOUND:
        unbound_fields.append({"field": "windows_fit", "code": "WINDOWS_FIT_UNBOUND"})

    # ---- consumer / nofit
    consumer = ov.get("consumer", record.get("original_consumer"))
    consumer_ref = ref(FILE_DEFAULT30, "/%d/original_consumer" % index)
    nofit_reason = nofit_reason_of(record)
    if not nofit_reason:
        nofit_reason = "UNBOUND"
        refusals.append({"code": R_NOFIT_REASON_UNBOUND, "detail": "no 退場/NoFit clause in source record"})
        unbound_fields.append({"field": "nofit_reason", "code": R_NOFIT_REASON_UNBOUND})
        nofit_ref = "UNBOUND"
    else:
        nofit_ref = ref(FILE_DEFAULT30, "/%d/original_business" % index)

    # ---- install state + status
    hold_declared = ov.get("hold", record.get("hold"))
    install_state = allowed_install_state(hold_declared, ov.get("install_state"))

    codes = [r["code"] for r in refusals]
    if R_OCCUPANT_UNBOUND in codes:
        status = STATUS_UNBOUND
    elif R_LICENSE_UNBOUND in codes:
        status = STATUS_UNBOUND
    elif R_WINDOWS_NOFIT in codes:
        status = STATUS_NOFIT
    elif R_NEED_REQUIRED_DOWNGRADE in codes:
        status = STATUS_UNBOUND
    elif hold_declared == STATUS_HOST_PIN_HOLD:
        status = STATUS_HOST_PIN_HOLD
    elif hold_declared == STATUS_OCCUPANT_PIN_HOLD:
        status = STATUS_OCCUPANT_PIN_HOLD
    else:
        status = STATUS_SELECTED
    if status not in ALLOWED_STATUS:
        raise Refusal(R_INSTALL_STATE_FORBIDDEN, "status %r invalid" % (status,))

    # ---- TECH485 row + r3 section evidence
    tech_rows = ctx["tech485"].get(need_id) or []
    tech_evidence = []
    for row in tech_rows:
        ok, why = verify_row_sha(sources.tech_row_lines, row) if sources.tech_row_lines else (False, "row file absent")
        tech_evidence.append(
            {
                "source_file": FILE_TECH_ROWS,
                "line": row.get("line"),
                "row_sha": row.get("row_sha"),
                "verified": ok,
                "verify": "sha256(physical line) == row_sha (%s)" % why,
            }
        )
        if not ok:
            refusals.append({"code": R_ROW_SHA_MISMATCH, "detail": "TECH485 row_sha mismatch for %s" % need_id})
    r3 = ctx["r3_sections"].get(need_id) or {}
    r3_state = r3.get("state")
    if r3_state and hold_declared and r3_state != hold_declared:
        ctx["mismatches"].append(
            {
                "claim": "per-need declared hold state",
                "need_id": need_id,
                "declared_in": FILE_R3_MD,
                "declared": r3_state,
                "computed_from": ref(FILE_DEFAULT30, "/%d/hold" % index),
                "computed": hold_declared,
            }
        )

    row = {
        "need_id": need_id,
        "need_name": record.get("need"),
        "need_class": need_class,
        "required": required,
        "required_declared": required_declared,
        "occupant_id": occupant_id or "UNBOUND",
        "occupant_kind": kind,
        "occupant_items": [b["wp16_id"] for b in bindings],
        "license": license_value,
        "license_state": license_state,
        "license_source_ref": license_source_ref,
        "windows_fit": "UNBOUND" if fit_state == FIT_UNBOUND else fit_state,
        "windows_fit_evidence": fit_evidence,
        "consumer": consumer,
        "consumer_ref": consumer_ref,
        "nofit_reason": nofit_reason,
        "nofit_reason_ref": nofit_ref,
        "install_state": install_state,
        "status": status,
        "hold_declared": hold_declared,
        "hold_owner": record.get("hold_owner"),
        "version_decision": record.get("version_decision"),
        "refusals": refusals,
        "refusal_codes": codes,
        "unbound_fields": unbound_fields,
        "evidence": {
            "default30": [
                _evidence(FILE_DEFAULT30, "/%d/original_id" % index, record.get("original_id"), sources, "json pointer resolves"),
                _evidence(FILE_DEFAULT30, "/%d/need" % index, record.get("need"), sources, "json pointer resolves"),
                _evidence(FILE_DEFAULT30, "/%d/selected_occupant" % index, record.get("selected_occupant"), sources, "json pointer resolves"),
                _evidence(FILE_DEFAULT30, "/%d/required" % index, required_declared, sources, "json pointer resolves"),
                _evidence(FILE_DEFAULT30, "/%d/hold" % index, record.get("hold"), sources, "json pointer resolves"),
                _evidence(FILE_DEFAULT30, "/%d/version_decision" % index, record.get("version_decision"), sources, "json pointer resolves"),
                license_evidence,
                fit_evidence,
            ],
            "tech485_rows": tech_evidence,
            "r3_section": {
                "source_file": FILE_R3_MD,
                "line": r3.get("line"),
                "state": r3_state,
                "windows_fit": r3.get("windows_fit"),
                "verified": bool(r3_state),
                "verify": "section heading + `state` literal parsed from md",
                "agrees_with_default30_hold": (r3_state == hold_declared) if r3_state else None,
            },
        },
    }
    return row


def build_named_holds(rows, sources):
    """Aggregate every UNBOUND field into a named HOLD with a source pointer.

    A field is only honoured as UNBOUND when the source itself says so; the hold
    therefore always names the file/pointer that carries the UNBOUND literal.
    """
    buckets = {}
    for row in rows:
        for item in row["unbound_fields"]:
            bucket = buckets.setdefault(
                item["code"],
                {
                    "code": item["code"],
                    "field": item["field"],
                    "count": 0,
                    "need_ids": [],
                    "source_refs": [],
                    "detail": None,
                },
            )
            bucket["count"] += 1
            bucket["need_ids"].append(row["need_id"])
            pointer = row["windows_fit_evidence"]["ref"] if item["field"] == "windows_fit" else row["license_source_ref"]
            if len(bucket["source_refs"]) < 3 and pointer not in bucket["source_refs"]:
                bucket["source_refs"].append(pointer)
            if bucket["detail"] is None:
                if item["field"] == "windows_fit":
                    bucket["detail"] = "source literal %r" % (row["windows_fit_evidence"]["value"],)
                elif item["field"] == "license":
                    bucket["detail"] = "source license literal carries a Reader/Host HOLD only"
                else:
                    bucket["detail"] = item.get("code")
    if any(row["license_state"] == LIC_READER_HOLD for row in rows):
        bucket = buckets.setdefault(
            LIC_READER_HOLD,
            {"code": LIC_READER_HOLD, "field": "license", "count": 0, "need_ids": [], "source_refs": [], "detail": None},
        )
        for row in rows:
            if row["license_state"] == LIC_READER_HOLD:
                if row["need_id"] not in bucket["need_ids"]:
                    bucket["count"] += 1
                    bucket["need_ids"].append(row["need_id"])
                if len(bucket["source_refs"]) < 3 and row["license_source_ref"] not in bucket["source_refs"]:
                    bucket["source_refs"].append(row["license_source_ref"])
        bucket["detail"] = "license field is a Reader/Host HOLD, not a release-grade determination"
    if any(str(row.get("version_decision") or "").upper().startswith("PIN_UNBOUND") for row in rows):
        bucket = buckets.setdefault(
            "PIN_UNBOUND",
            {"code": "PIN_UNBOUND", "field": "version_pin", "count": 0, "need_ids": [], "source_refs": [], "detail": None},
        )
        for row in rows:
            if str(row.get("version_decision") or "").upper().startswith("PIN_UNBOUND"):
                if row["need_id"] not in bucket["need_ids"]:
                    bucket["count"] += 1
                    bucket["need_ids"].append(row["need_id"])
                for ev in row["evidence"]["default30"]:
                    if ev["pointer"].endswith("/version_decision") and len(bucket["source_refs"]) < 3:
                        if ev["ref"] not in bucket["source_refs"]:
                            bucket["source_refs"].append(ev["ref"])
        bucket["detail"] = "no immutable artifact pin; source version_decision is PIN_UNBOUND"
    holds = list(buckets.values())
    holds.sort(key=lambda h: (-h["count"], h["code"]))
    return holds


def build_matrix(sources, overrides=None):
    overrides = overrides or {}
    bindings, holds = select_items(sources, overrides)
    ctx = {"tech485": sources.tech485_by_id(), "r3_sections": sources.r3_sections, "mismatches": []}
    rows = []
    for index, record in enumerate(sources.default30):
        if not isinstance(record, dict):
            continue
        need_id = record.get("original_id")
        rows.append(build_row(record, index, bindings.get(need_id, []), sources, overrides, ctx))

    counts = {
        "needs_total": len(rows),
        "required_true": sum(1 for r in rows if r["required"]),
        "required_false": sum(1 for r in rows if not r["required"]),
        "selected": sum(1 for r in rows if r["status"] == STATUS_SELECTED),
        "occupant_pin_hold": sum(1 for r in rows if r["status"] == STATUS_OCCUPANT_PIN_HOLD),
        "host_pin_hold": sum(1 for r in rows if r["status"] == STATUS_HOST_PIN_HOLD),
        "nofit": sum(1 for r in rows if r["status"] == STATUS_NOFIT),
        "unbound": sum(1 for r in rows if r["status"] == STATUS_UNBOUND),
        "install_state": {
            state: sum(1 for r in rows if r["install_state"] == state) for state in ALLOWED_INSTALL_STATE
        },
        "occupant_kind": {kind: sum(1 for r in rows if r["occupant_kind"] == kind) for kind in ALLOWED_KIND},
        "license_state": {},
        "windows_fit": {},
        "with_translator": sum(1 for r in rows if r["occupant_items"]),
        "unbound_field_occurrences": sum(len(r["unbound_fields"]) for r in rows),
    }
    for r in rows:
        counts["license_state"][r["license_state"]] = counts["license_state"].get(r["license_state"], 0) + 1
        counts["windows_fit"][r["windows_fit"]] = counts["windows_fit"].get(r["windows_fit"], 0) + 1

    comparison = compare_with_declaration(sources, rows, counts)
    named_holds = build_named_holds(rows, sources)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "lane": LANE,
        "generated_from": {
            "source_root": sources.root,
            "files": sources.files,
        },
        "field_contract": {
            "status": list(ALLOWED_STATUS),
            "install_state": list(ALLOWED_INSTALL_STATE),
            "install_state_forbidden": list(FORBIDDEN_INSTALL_STATES),
            "occupant_kind": list(ALLOWED_KIND),
            "occupant_kind_meaning": {
                KIND_DONOR: "need is served by a Donor24 slot (native reuse recipe)",
                KIND_METHOD: "need is served only by a Method25 recipe (non-installer)",
                KIND_HOST: "need is served by a host/core-owned component; no Donor24/Method25 item selected",
                KIND_NONE: "no occupant declared",
            },
            "kind_precedence": "DONOR > METHOD > HOST > NONE",
            "status_precedence": [
                R_OCCUPANT_UNBOUND, R_LICENSE_UNBOUND, R_WINDOWS_NOFIT, R_NEED_REQUIRED_DOWNGRADE,
                STATUS_HOST_PIN_HOLD, STATUS_OCCUPANT_PIN_HOLD, STATUS_SELECTED,
            ],
            "license_states": [LIC_DECLARED, LIC_DECLARED_ACK_PENDING, LIC_READER_HOLD, LIC_UNBOUND],
        },
        "selection_rules": list(SELECTION_RULES),
        "resolved_bindings": {need_id: bindings[need_id] for need_id in bindings},
        "overrides_applied": overrides or {},
        "selection_holds": holds,
        "counts": counts,
        "declaration_comparison": comparison,
        "named_holds": named_holds,
        "holds": sources.holds + holds + [
            {"code": code, "need_id": r["need_id"], "detail": "row refusal"}
            for r in rows for code in r["refusal_codes"]
        ],
        "rows": rows,
    }
    return manifest, {"bindings": bindings, "selection_holds": holds, "mismatches": ctx["mismatches"]}


# ---------------------------------------------------------------- declaration

_G3_NEED_RE = re.compile(r"Default30\s+(\d+)\s*/\s*(\d+)\s*Required")
_G3_OCC_RE = re.compile(r"(\d+)\s*OCCUPANT_PIN_HOLD")
_G3_HOST_RE = re.compile(r"(\d+)\s*HOST_PIN_HOLD")


def compare_with_declaration(sources, rows, counts):
    declared = {"need_total": None, "required": None, "occupant_pin_hold": None, "host_pin_hold": None,
                "no_installed_or_verified_upgrade": None, "evidence_literal": None, "gate": None}
    if isinstance(sources.ccs, dict):
        for gate in sources.ccs.get("gate_results") or []:
            if isinstance(gate, dict) and gate.get("gate") == "G3_TECH":
                evidence = str(gate.get("evidence") or "")
                declared["gate"] = "G3_TECH"
                declared["evidence_literal"] = evidence
                hit = _G3_NEED_RE.search(evidence)
                if hit:
                    declared["required"] = int(hit.group(1))
                    declared["need_total"] = int(hit.group(2))
                hit = _G3_OCC_RE.search(evidence)
                if hit:
                    declared["occupant_pin_hold"] = int(hit.group(1))
                hit = _G3_HOST_RE.search(evidence)
                if hit:
                    declared["host_pin_hold"] = int(hit.group(1))
                declared["no_installed_or_verified_upgrade"] = ("無 INSTALLED/VERIFIED 升格" in evidence)
                break

    computed = {
        "need_total": counts["needs_total"],
        "required": counts["required_true"],
        "occupant_pin_hold": counts["occupant_pin_hold"],
        "host_pin_hold": counts["host_pin_hold"],
        "no_installed_or_verified_upgrade": not any(
            r["install_state"] in FORBIDDEN_INSTALL_STATES for r in rows
        ),
    }
    mismatches = []
    for key, declared_value in declared.items():
        if key in ("evidence_literal", "gate") or declared_value is None:
            continue
        actual = computed.get(key)
        if declared_value != actual:
            named = []
            if key == "occupant_pin_hold":
                named = [r["need_id"] for r in rows if r["status"] == STATUS_OCCUPANT_PIN_HOLD]
            elif key == "host_pin_hold":
                named = [r["need_id"] for r in rows if r["status"] == STATUS_HOST_PIN_HOLD]
            elif key == "required":
                named = [r["need_id"] for r in rows if not r["required"]]
            elif key == "need_total":
                named = [r["need_id"] for r in rows]
            mismatches.append(
                {
                    "claim": key,
                    "declared_in": FILE_CCS,
                    "declared_pointer": "/gate_results/G3_TECH/evidence",
                    "declared": declared_value,
                    "computed": actual,
                    "delta": (actual - declared_value) if isinstance(actual, int) and isinstance(declared_value, int) else None,
                    "computed_need_ids": named,
                }
            )
    return {
        "verdict": "MATCH" if not mismatches else "MISMATCH",
        "declared": declared,
        "computed": computed,
        "mismatches": mismatches,
        "note": "declared numbers are quoted verbatim from CURRENT_CANDIDATE_STATE; they are never rewritten",
    }


# ---------------------------------------------------------------- translators

_PAYLOAD_SPLIT = re.compile(r"^(.*?)\s*\+\s*(.+)$", re.S)
_BASE_INPUT_FIELDS = ("goal", "source_ref", "need")
_DONOR_BASE_FIELDS = ("source_sha256", "subject", "known_answers")

# uppercase tokens that look like codes but are not refusal codes
_CODE_STOPLIST = frozenset(
    {
        "SOURCE_SHA", "JSON", "PASS", "DEFER", "METHOD", "METHOD_ONLY", "SKILL", "SARIF", "SPDX", "SBOM",
        "HITL", "JTBD", "FUO", "ADR", "SQLITE", "FTS5", "BMAD", "OWASP", "SLSA", "ACP", "MCP", "PIPD",
        "SBL", "HGK", "HOST", "ECP", "HEAD", "SPEC", "TASK_DAG", "QUESTION_LEDGER",
    }
)
_CODE_RE = re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]+\b")


def extract_refusal_codes(row):
    """Codes carried by a WP16 row: its first_fail plus code-shaped tokens in
    ``negative`` / ``original_negative``.  Nothing is invented;
    METHOD_NOT_INSTALLER is appended because this lane's translator contract
    always refuses installer use."""
    codes = []
    first = (row.get("first_fail") or "").strip().strip("`")
    if first:
        codes.append(first)
    blobs = [str(row.get("negative") or ""), str(row.get("original_negative") or "")]
    for blob in blobs:
        for token in _CODE_RE.findall(blob):
            if token in _CODE_STOPLIST:
                continue
            codes.append(token)
    codes.append(R_METHOD_NOT_INSTALLER)
    seen = []
    for code in codes:
        if code and code not in seen:
            seen.append(code)
    return seen


def parse_input_schema(binding, row):
    literal = (row.get("input") or "").strip()
    payload = None
    fields = list(_BASE_INPUT_FIELDS) if binding["kind"] == KIND_METHOD else list(_DONOR_BASE_FIELDS)
    derivation = "WP16 input literal: 'Goal/SourceRef/Need + payload'" if binding["kind"] == KIND_METHOD \
        else "WP16 translation clause: 'Preserve original SourceSHA/Subject/known answers'"
    hit = _PAYLOAD_SPLIT.match(literal)
    if hit and binding["kind"] == KIND_METHOD:
        payload = hit.group(2).strip()
    elif binding["kind"] == KIND_METHOD:
        payload = literal
    schema = {
        "schema_id": "INPUT:%s" % binding["wp16_id"],
        "form": "OBJECT",
        "required_fields": [{"name": name, "type": "string", "source": "WP16 literal"} for name in fields],
        "payload_literal": payload if payload is not None else literal,
        "payload_derivation": derivation,
        "input_literal": literal,
        "additional_properties": False,
        "binding_evidence": "WP16_TRANSLATION49.json pointer /%d/input" % row["_index"],
    }
    if binding["kind"] == KIND_METHOD:
        schema["required_fields"].append(
            {"name": "payload", "type": "typed", "source": "WP16 literal after '+'", "literal": payload}
        )
    else:
        schema["required_fields"].append(
            {"name": "donor_input", "type": "typed", "source": "WP16 literal", "literal": literal}
        )
    return schema


def parse_output_schema(binding, row):
    literal = (row.get("concrete_output") or "").strip()
    parts = [p.strip() for p in re.split(r"[+/]", literal) if p.strip()]
    return {
        "schema_id": "OUTPUT:%s" % binding["wp16_id"],
        "form": "TYPED_ARTIFACT",
        "artifact_literal": literal,
        "artifact_parts": parts,
        "produced_as": "%s.MethodOutput" % binding["wp16_id"],
        "effect_ceiling": (row.get("effect") or "").strip(),
        "advisory_only": True,
        "binding_evidence": "WP16_TRANSLATION49.json pointer /%d/concrete_output" % row["_index"],
    }


def build_translator_map(sources, bindings, selection_holds):
    rows_by_id = {row.get("original_id"): row for row in sources.wp16 if isinstance(row, dict)}
    for idx, row in enumerate(sources.wp16):
        if isinstance(row, dict):
            row["_index"] = idx
    tech = sources.tech485_by_id()
    translators = []
    for need_id in sorted(bindings):
        for binding in bindings[need_id]:
            row = rows_by_id.get(binding["wp16_id"])
            if row is None:
                raise Refusal(R_TRANSLATION_ITEM_ABSENT, "row disappeared", wp16_id=binding["wp16_id"])
            row_evidence = []
            for reg in tech.get(binding["wp16_id"], []):
                ok, why = verify_row_sha(sources.tech_row_lines, reg) if sources.tech_row_lines else (False, "row file absent")
                row_evidence.append(
                    {
                        "source_file": FILE_TECH_ROWS,
                        "line": reg.get("line"),
                        "row_sha": reg.get("row_sha"),
                        "verified": ok,
                        "verify": "sha256(physical line) == row_sha (%s)" % why,
                    }
                )
            translators.append(
                {
                    "translator_id": "TRANSLATOR:%s" % binding["wp16_id"],
                    "wp16_id": binding["wp16_id"],
                    "need_id": need_id,
                    "need_name": next((r.get("need") for r in sources.default30
                                       if isinstance(r, dict) and r.get("original_id") == need_id), None),
                    "kind": binding["kind"],
                    "item_name": row.get("name"),
                    "occupant_class": _occupant_class(row),
                    "selection_basis": binding["basis"],
                    "selection_evidence": binding.get("alias_evidence") or {
                        "basis": binding["basis"], "expected": binding.get("expected")},
                    "input_schema": parse_input_schema(binding, row),
                    "output_schema": parse_output_schema(binding, row),
                    "refusal_codes": extract_refusal_codes(row),
                    "first_fail": row.get("first_fail"),
                    "corpus_installer_deny_token": CORPUS_METHOD_AS_INSTALL,
                    "is_installer": False,
                    "installer_request_refusal": R_METHOD_NOT_INSTALLER,
                    "source_ref": {
                        "wp16_pointer": ref(FILE_WP16, "/%d" % row["_index"]),
                        "wp16_file_sha256": sources.file_sha(FILE_WP16),
                        "row_sha_evidence": row_evidence,
                        "translation_literal": row.get("translation"),
                    },
                    "state": row.get("state"),
                    "disposition": row.get("disposition"),
                    "consumer": row.get("original_consumer"),
                    "effect": row.get("effect"),
                    "rollback": row.get("rollback"),
                    "host": row.get("host"),
                }
            )
    selected_ids = {t["wp16_id"] for t in translators}
    unselected = []
    for row in sources.wp16:
        if not isinstance(row, dict):
            continue
        ident = row.get("original_id")
        if ident in selected_ids:
            continue
        unselected.append(
            {
                "wp16_id": ident,
                "item_name": row.get("name"),
                "kind": _wp16_kind(row),
                "reason": "no Default30 Need in this wave selected this item",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "lane": LANE,
        "installer_claim": "NONE",
        "installed_count": 0,
        "is_installer_all_false": all(t["is_installer"] is False for t in translators),
        "contract": {
            "translator_is_recipe_only": True,
            "installer_request_response": R_METHOD_NOT_INSTALLER,
            "corpus_token_for_same_refusal": CORPUS_METHOD_AS_INSTALL,
            "method_only_policy": "a Method25 item may never be promoted to installer; install requests are refused",
            "installer_required_fields_forbidden": FORBIDDEN_INSTALL_STATES,
        },
        "generated_from": {"files": {k: v for k, v in sources.files.items() if k in (FILE_DEFAULT30, FILE_WP16, FILE_TECH485)}},
        "counts": {
            "translators": len(translators),
            "donor": sum(1 for t in translators if t["kind"] == KIND_DONOR),
            "method": sum(1 for t in translators if t["kind"] == KIND_METHOD),
            "needs_with_translator": len(bindings),
            "wp16_items_total": len([r for r in sources.wp16 if isinstance(r, dict)]),
            "unselected_items": len(unselected),
            "is_installer_true": sum(1 for t in translators if t["is_installer"] is not False),
        },
        "selection_holds": selection_holds,
        "translators": translators,
        "excluded_unselected": unselected,
    }


def _occupant_class(row):
    """Class token the WP16 row itself declares.

    Methods carry it literally as ``/ METHOD_ONLY (not installed claim)``; donors
    carry the equivalent disposition token (``正式 ACK=SELECTIVE_NATIVE_REUSE``).
    Nothing is inferred: missing both means UNBOUND.
    """
    blob = str(row.get("original_business") or "")
    hit = re.search(r"/\s*([A-Z][A-Z0-9_]+)\s*\(\s*not installed claim\s*\)", blob)
    if hit:
        return hit.group(1)
    disposition = str(row.get("disposition") or "")
    hit = re.search(r"ACK=([A-Z][A-Z0-9_]+)", disposition)
    if hit:
        return hit.group(1)
    return "UNBOUND"


def translator_index(tmap):
    return {t["translator_id"]: t for t in tmap["translators"]}


def translate(tmap, translator_id, mode="advisory", payload=None):
    """Apply one translation recipe, or refuse.

    ``mode='install'`` (or 'installer') always refuses with METHOD_NOT_INSTALLER:
    the recipe produces an advisory typed artifact and never an installation.
    """
    spec = translator_index(tmap).get(translator_id)
    if spec is None:
        raise Refusal(R_UNKNOWN_TRANSLATOR, "no such translator", translator_id=translator_id)
    if mode in ("install", "installer", "INSTALL", "INSTALLER"):
        raise Refusal(
            R_METHOD_NOT_INSTALLER,
            "translator %s is a %s recipe, not an installer" % (translator_id, spec["kind"]),
            translator_id=translator_id,
            wp16_id=spec["wp16_id"],
            corpus_first_fail=spec["corpus_installer_deny_token"],
            is_installer=spec["is_installer"],
        )
    missing = [f["name"] for f in spec["input_schema"]["required_fields"] if payload is not None and f["name"] not in payload]
    if payload is not None and missing:
        raise Refusal(spec["refusal_codes"][0], "missing input fields: %s" % ",".join(missing),
                      translator_id=translator_id, missing=missing)
    return {
        "translator_id": translator_id,
        "wp16_id": spec["wp16_id"],
        "is_installer": False,
        "installed": False,
        "produced_as": spec["output_schema"]["produced_as"],
        "artifact_literal": spec["output_schema"]["artifact_literal"],
        "effect": spec["output_schema"]["effect_ceiling"],
        "advisory_only": True,
        "state_upgrade": None,
    }


# ---------------------------------------------------------------- readback


def build_readback(sources, rows):
    by_id = {r["need_id"]: r for r in rows}
    entries = []
    unbound_total = 0
    for index, record in enumerate(sources.default30):
        if not isinstance(record, dict):
            continue
        need_id = record.get("original_id")
        row = by_id.get(need_id)
        if row is None:
            continue
        evidence = []
        for field_name in ("original_id", "need", "required", "selected_occupant", "version_decision",
                           "license", "fit", "hold", "original_consumer"):
            pointer = "/%d/%s" % (index, field_name)
            value = record.get(field_name)
            evidence.append(
                {
                    "claim": field_name,
                    "source_file": FILE_DEFAULT30,
                    "pointer": pointer,
                    "ref": ref(FILE_DEFAULT30, pointer),
                    "value": value,
                    "resolved": pointer_ok(sources.default30, pointer),
                    "source_sha256": sources.file_sha(FILE_DEFAULT30),
                }
            )
        for tech in row["evidence"]["tech485_rows"]:
            evidence.append(
                {
                    "claim": "TECH485 registry row",
                    "source_file": tech["source_file"],
                    "pointer": "line %s" % tech["line"],
                    "ref": "%s#L%s" % (tech["source_file"], tech["line"]),
                    "value": tech["row_sha"],
                    "resolved": tech["verified"],
                    "source_sha256": sources.file_sha(FILE_TECH485),
                }
            )
        r3 = row["evidence"]["r3_section"]
        evidence.append(
            {
                "claim": "r3 declared state",
                "source_file": FILE_R3_MD,
                "pointer": "line %s" % r3["line"],
                "ref": "%s#L%s" % (FILE_R3_MD, r3["line"]) if r3["line"] else "UNBOUND",
                "value": r3["state"],
                "resolved": bool(r3["verified"]),
                "source_sha256": sources.file_sha(FILE_R3_MD),
            }
        )
        unbound = []
        version = record.get("version_decision")
        if isinstance(version, str) and version.upper().startswith("PIN_UNBOUND"):
            unbound.append(
                {
                    "field": "version_pin",
                    "code": "PIN_UNBOUND",
                    "source_ref": ref(FILE_DEFAULT30, "/%d/version_decision" % index),
                    "detail": "source declares PIN_UNBOUND; no immutable artifact pin exists",
                }
            )
        if row["license_state"] in (LIC_READER_HOLD, LIC_UNBOUND):
            unbound.append(
                {
                    "field": "license",
                    "code": LIC_UNBOUND if row["license_state"] == LIC_UNBOUND else "LICENSE_READER_HOLD",
                    "source_ref": row["license_source_ref"],
                    "detail": "no release-grade license determination in source; Host/Reader ACK outstanding",
                }
            )
        if row["windows_fit"] == "UNBOUND":
            unbound.append(
                {
                    "field": "windows_fit",
                    "code": "WINDOWS_FIT_UNBOUND",
                    "source_ref": row["windows_fit_evidence"]["ref"],
                    "detail": "source literal HOST_FIT_UNBOUND; Windows loader/ACL/functional readback not observed",
                }
            )
        for u in unbound:
            unbound_total += 1
        entries.append(
            {
                "need_id": need_id,
                "need_name": record.get("need"),
                "selected": row["status"] in (STATUS_SELECTED, STATUS_OCCUPANT_PIN_HOLD, STATUS_HOST_PIN_HOLD),
                "status": row["status"],
                "install_state": row["install_state"],
                "evidence": evidence,
                "evidence_all_resolved": all(e["resolved"] for e in evidence),
                "unbound": unbound,
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "lane": LANE,
        "claim_ceiling": "AUTHOR_LOCAL_TEST",
        "input_identity": {k: v for k, v in sources.files.items()},
        "counts": {
            "needs": len(entries),
            "evidence_entries": sum(len(e["evidence"]) for e in entries),
            "evidence_unresolved": sum(1 for e in entries for ev in e["evidence"] if not ev["resolved"]),
            "unbound_total": unbound_total,
            "needs_with_unbound": sum(1 for e in entries if e["unbound"]),
            "tech485_rows_verified": sources.verified_rows(),
        },
        "entries": entries,
    }


# ---------------------------------------------------------------- markdown


def _md_cell(value):
    if value is None:
        return "UNBOUND"
    text = str(value).replace("|", "\\|").replace("\n", " ")
    return text if len(text) <= 120 else text[:117] + "..."


def render_markdown(matrix, tmap, readback):
    c = matrix["counts"]
    cmp = matrix["declaration_comparison"]
    lines = []
    lines.append("# WP-FHS-16 Default30 Need → Occupant 對照矩陣")
    lines.append("")
    lines.append("lane `%s`；schema `%s`；來源根 `%s`。" % (LANE, SCHEMA_VERSION, matrix["generated_from"]["source_root"]))
    lines.append("")
    lines.append("本檔由 `need_occupant.py` 從實體 JSON 解析產生，不是人工抄寫。每一列的 license、windows_fit、"
                 "consumer、nofit_reason 都是來源欄位的逐字副本，並附 JSON Pointer 來源參照；來源沒有給的欄位"
                 "標 `UNBOUND` 並列名具 HOLD。**本輪不安裝、不升級任何 Default30 項，也不把 Donor24/Method25 當 installer。**")
    lines.append("")
    lines.append("## 統計")
    lines.append("")
    lines.append("| 指標 | 值 |")
    lines.append("| --- | --- |")
    lines.append("| Need 分母 | %d |" % c["needs_total"])
    lines.append("| Required=true | %d |" % c["required_true"])
    lines.append("| Required=false | %d |" % c["required_false"])
    lines.append("| SELECTED | %d |" % c["selected"])
    lines.append("| OCCUPANT_PIN_HOLD | %d |" % c["occupant_pin_hold"])
    lines.append("| HOST_PIN_HOLD | %d |" % c["host_pin_hold"])
    lines.append("| NOFIT | %d |" % c["nofit"])
    lines.append("| UNBOUND（status） | %d |" % c["unbound"])
    lines.append("| install_state NOT_INSTALLED | %d |" % c["install_state"][INSTALL_NOT_INSTALLED])
    lines.append("| install_state PIN_HOLD | %d |" % c["install_state"][INSTALL_PIN_HOLD])
    lines.append("| install_state HOST_PIN_HOLD | %d |" % c["install_state"][INSTALL_HOST_PIN_HOLD])
    lines.append("| license DECLARED | %d |" % c["license_state"].get(LIC_DECLARED, 0))
    lines.append("| license DECLARED+HOST_ACK_PENDING | %d |" % c["license_state"].get(LIC_DECLARED_ACK_PENDING, 0))
    lines.append("| license READER_HOLD | %d |" % c["license_state"].get(LIC_READER_HOLD, 0))
    lines.append("| license UNBOUND | %d |" % c["license_state"].get(LIC_UNBOUND, 0))
    lines.append("| windows_fit UNBOUND | %d |" % c["windows_fit"].get("UNBOUND", 0))
    lines.append("| windows_fit FIT | %d |" % c["windows_fit"].get(FIT_FIT, 0))
    lines.append("| windows_fit NOFIT | %d |" % c["windows_fit"].get(FIT_NOFIT, 0))
    lines.append("| 有 Donor/Method translator 的 Need | %d |" % c["with_translator"])
    lines.append("| occupant_kind DONOR / METHOD / HOST / NONE | %d / %d / %d / %d |" % (
        c["occupant_kind"][KIND_DONOR], c["occupant_kind"][KIND_METHOD],
        c["occupant_kind"][KIND_HOST], c["occupant_kind"][KIND_NONE]))
    lines.append("| translator 數（donor / method） | %d（%d / %d） |" % (
        tmap["counts"]["translators"], tmap["counts"]["donor"], tmap["counts"]["method"]))
    lines.append("")
    lines.append("## 與 CURRENT_CANDIDATE_STATE 宣告對照")
    lines.append("")
    lines.append("宣告字串（逐字）：「%s」" % _md_cell(cmp["declared"]["evidence_literal"]))
    lines.append("")
    lines.append("判決：**%s**" % cmp["verdict"])
    lines.append("")
    lines.append("| 宣告項 | 宣告值 | 實算值 | 一致 |")
    lines.append("| --- | --- | --- | --- |")
    for key, declared_value in cmp["declared"].items():
        if key in ("evidence_literal", "gate"):
            continue
        computed_value = cmp["computed"].get(key)
        same = "YES" if declared_value == computed_value else "NO"
        lines.append("| %s | %s | %s | %s |" % (key, declared_value, computed_value, same))
    if cmp["mismatches"]:
        lines.append("")
        lines.append("### MISMATCH（具名差異，未改動宣告數字）")
        lines.append("")
        for m in cmp["mismatches"]:
            lines.append("- `%s`：宣告 %s，實算 %s（差 %s）；涉及 %d 筆，首筆 `%s`" % (
                m["claim"], m["declared"], m["computed"], m["delta"],
                len(m["computed_need_ids"]), (m["computed_need_ids"] or ["-"])[0]))
    lines.append("")
    lines.append("## 30 筆矩陣")
    lines.append("")
    lines.append("| # | need_id | need_class | required | occupant | kind | license | windows_fit | consumer | install_state | status |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for i, row in enumerate(matrix["rows"], 1):
        lines.append("| %d | `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            i, row["need_id"], row["need_class"], "true" if row["required"] else "false",
            _md_cell(row["occupant_id"]), row["occupant_kind"],
            _md_cell(row["license"]), row["windows_fit"], _md_cell(row["consumer"]),
            row["install_state"], row["status"]))
    lines.append("")
    lines.append("### License / Windows-fit / NOFIT 來源參照")
    lines.append("")
    lines.append("| need_id | license_state | license_source_ref | windows_fit_evidence | nofit_reason | nofit_ref |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for row in matrix["rows"]:
        lines.append("| `%s` | %s | `%s` | `%s` = %s | %s | `%s` |" % (
            row["need_id"], row["license_state"], row["license_source_ref"],
            row["windows_fit_evidence"]["ref"], _md_cell(row["windows_fit_evidence"]["value"]),
            _md_cell(row["nofit_reason"]), row["nofit_reason_ref"]))
    lines.append("")
    lines.append("## 本波受選 Donor/Method translator（全部 is_installer=false）")
    lines.append("")
    lines.append("| need_id | translator | kind | occupant_class | is_installer | refusal 首碼 | source_ref |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for t in tmap["translators"]:
        lines.append("| `%s` | `%s` | %s | %s | %s | %s | `%s` |" % (
            t["need_id"], t["translator_id"], t["kind"], t["occupant_class"],
            str(t["is_installer"]).lower(), t["refusal_codes"][0], t["source_ref"]["wp16_pointer"]))
    lines.append("")
    lines.append("未受選的 WP16 項（不產生 translator）：%d 筆；清單見 `TRANSLATOR_MAP.json` 的 `excluded_unselected`。" % tmap["counts"]["unselected_items"])
    lines.append("")
    lines.append("## Holds（具名）")
    lines.append("")
    lines.append("- `WINDOWS_FIT_UNBOUND`：%d/30，來源欄位 `fit` 逐字為 `DESIGN_NEED_RETAINED; HOST_FIT_UNBOUND`。" % c["windows_fit"].get("UNBOUND", 0))
    lines.append("- `LICENSE_READER_HOLD`：%d/30，來源 license 欄位只到 Reader/Host HOLD，未達可發佈的授權判定。" % c["license_state"].get(LIC_READER_HOLD, 0))
    lines.append("- `PIN_UNBOUND` / 版本未釘：見 `TECH_CHOICE_READBACK.json` 各筆 `unbound`。")
    lines.append("- `INSTALLED` / `VERIFIED`：本輪 0 筆，install_state 詞彙中不存在此二值。")
    lines.append("")
    lines.append("## 讀回與可宣稱上限")
    lines.append("")
    lines.append("- 讀回：`TECH_CHOICE_READBACK.json`（%d 筆 need、%d 條證據、TECH485 逐列 sha256 重算 %d/%d PASS）。" % (
        readback["counts"]["needs"], readback["counts"]["evidence_entries"],
        readback["counts"]["tech485_rows_verified"]["verified"], readback["counts"]["tech485_rows_verified"]["total"]))
    lines.append("- claim_ceiling：`AUTHOR_LOCAL_TEST`。本檔證明「作者本機可從來源 JSON 重算矩陣」，"
                 "不證明任何 Host 安裝、Bound、Invoked 或 Verified。")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------- orchestration


def build_all(sources, overrides=None):
    matrix, extra = build_matrix(sources, overrides)
    tmap = build_translator_map(sources, extra["bindings"], extra["selection_holds"])
    readback = build_readback(sources, matrix["rows"])
    if extra["mismatches"]:
        matrix["declaration_comparison"]["per_need_state_mismatches"] = extra["mismatches"]
        if matrix["declaration_comparison"]["verdict"] == "MATCH":
            matrix["declaration_comparison"]["verdict"] = "MISMATCH"
        for m in extra["mismatches"]:
            matrix["declaration_comparison"]["mismatches"].append(m)
    matrix["translator_map_counts"] = tmap["counts"]
    matrix["readback_counts"] = readback["counts"]
    return {"matrix": matrix, "translator_map": tmap, "readback": readback}


def write_outputs(bundle, out_dir):
    matrix = bundle["matrix"]
    tmap = bundle["translator_map"]
    readback = bundle["readback"]
    paths = {
        "matrix_json": os.path.join(out_dir, "NEED_OCCUPANT_MATRIX.json"),
        "matrix_md": os.path.join(out_dir, "NEED_OCCUPANT_MATRIX.md"),
        "translator_map": os.path.join(out_dir, "TRANSLATOR_MAP.json"),
        "readback": os.path.join(out_dir, "TECH_CHOICE_READBACK.json"),
    }
    write_json(paths["matrix_json"], matrix)
    write_text(paths["matrix_md"], render_markdown(matrix, tmap, readback))
    write_json(paths["translator_map"], tmap)
    write_json(paths["readback"], readback)
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description="WP-FHS-16 Default30 Need -> Occupant matrix generator")
    parser.add_argument("--source-root", required=True, help="W0 R4C source directory (read-only)")
    parser.add_argument("--out", required=True, help="output directory")
    parser.add_argument("--print-counts", action="store_true", help="print counts JSON to stdout")
    args = parser.parse_args(argv)

    try:
        sources = Sources(args.source_root)
        bundle = build_all(sources)
    except Refusal as exc:
        sys.stderr.write(json.dumps(exc.to_dict(), ensure_ascii=False) + "\n")
        return 3

    paths = write_outputs(bundle, args.out)
    matrix = bundle["matrix"]
    counts = matrix["counts"]
    verdict = matrix["declaration_comparison"]["verdict"]
    if args.print_counts:
        sys.stdout.write(json.dumps({"counts": counts, "verdict": verdict, "paths": paths}, ensure_ascii=False, indent=2) + "\n")
    else:
        sys.stdout.write(
            "needs=%d required=%d OCCUPANT_PIN_HOLD=%d HOST_PIN_HOLD=%d NOFIT=%d UNBOUND=%d translators=%d (%s)\n"
            % (counts["needs_total"], counts["required_true"], counts["occupant_pin_hold"], counts["host_pin_hold"],
               counts["nofit"], counts["unbound"], bundle["translator_map"]["counts"]["translators"], verdict)
        )
    for name, path in paths.items():
        sys.stdout.write("%-14s %s\n" % (name, path))
    if verdict != "MATCH":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
