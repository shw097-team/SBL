#!/usr/bin/env python3
"""skill_pack_check — discover -> load -> route checker for the 8 PIPD SkillContract packs.

FW-03 / R-AUD-002: PGK-07 claimed 8 skills but pointed at five OpenSpec donor files. An
OpenSpec donor is NOT a PIPD skill. This checker demands the real `skills/pipd-*` packs and
REFUSES (typed reason, non-zero exit):

  * MARKER_ONLY_PACK      — a directory holding only a free-text file, no schemas
  * MISSING_SCHEMA        — a pack without schemas/input.schema.json / schemas/output.schema.json
  * DUPLICATE_SKILL_NAME  — two packs declaring the same frontmatter name
  * UNEXPECTED_ENTRY      — a 9th / duplicate entry beyond the exact 8 packs

It also validates frontmatter, validates every declared schema and reference file exists,
round-trips input/output payloads through the declared Draft 2020-12 schemas (verifying each
case's named expected first-fail invariant), and verifies trigger / non-trigger routing.

Usage:
  python tools/skill_pack_check.py --all [--skills-root PATH]
  python tools/skill_pack_check.py --skill pipd-pi-compile [--skills-root PATH]

Output: a single JSON document on stdout. Exit 0 iff state == PASS.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment gate
    print(json.dumps({"checker": "skill-pack-check/1", "state": "REFUSED",
                      "refusals": [{"code": "TOOL_MISSING", "path": "yaml",
                                    "reason": "PyYAML is required to load tests/cases.yaml"}]}))
    raise SystemExit(2)

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - environment gate
    print(json.dumps({"checker": "skill-pack-check/1", "state": "REFUSED",
                      "refusals": [{"code": "TOOL_MISSING", "path": "jsonschema",
                                    "reason": "jsonschema is required for Draft 2020-12 round-trips"}]}))
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
DRAFT = "https://json-schema.org/draft/2020-12/schema"

EXPECTED_NAMES = ("pipd-route-intake", "pipd-authority-source", "pipd-profile-tailor",
                  "pipd-pi-compile", "pipd-pd-bind", "pipd-execution-contract",
                  "pipd-assurance-tqaep", "pipd-package-project")

REQUIRED_DECLARED = ("schemas/input.schema.json", "schemas/output.schema.json",
                     "references/contract.md", "references/examples.md", "tests/cases.yaml")

CASE_KINDS = ("POS", "NEG", "EDGE", "SEC")
CLAIM_LADDER = ["PROMPT_COMPILE_PASS", "HGK_ADMITTED", "RUNTIME_READY", "LOCAL_QUALIFIED",
                "INDEPENDENT_PASS", "PUBLICATION_APPROVED", "RELEASED", "PRODUCTION_VERIFIED"]

STRUCTURAL_CODES = {"MARKER_ONLY_PACK", "SKILL_MD_MISSING", "MISSING_SCHEMA",
                    "DUPLICATE_SKILL_NAME", "UNEXPECTED_ENTRY", "MISSING_PACK",
                    "NAME_MISMATCH", "FRONTMATTER_INVALID", "DECLARED_FILE_MISSING",
                    "SCHEMA_INVALID"}


# ----------------------------------------------------------------- semantic rules
def sem_distinct(payload: dict, fields: list) -> bool:
    """Rule `distinct`: the named input fields must be pairwise distinct (case/whitespace
    insensitive) and non-empty. This is the TQ_SOD invariant: the maker can never be the
    independent checker."""
    vals = [str(payload.get(f, "")).strip().casefold() for f in fields]
    return all(vals) and len(vals) == len(set(vals))


def sem_claim_gate(payload: dict, fields: list | None = None) -> bool:
    """Rule `claim_gate`: LOCAL_QUALIFIED and above require a bound approval receipt plus an
    independent checker identity; below that rung no approval is needed."""
    claims = payload.get("allowed_claims") or []
    rungs = [CLAIM_LADDER.index(c) for c in claims if c in CLAIM_LADDER]
    if not rungs:
        return True
    if max(rungs) < CLAIM_LADDER.index("LOCAL_QUALIFIED"):
        return True
    approval = payload.get("approval") or {}
    return (bool(str(approval.get("approval_receipt", "")).strip())
            and bool(str(approval.get("checker_identity", "")).strip()))


SEMANTIC_RULES = {"distinct": sem_distinct, "claim_gate": sem_claim_gate}


# ----------------------------------------------------------------- helpers
def first_fail(schema: dict, payload: object, scope: str) -> str | None:
    """Return the deterministic first failing invariant id (`<scope>.<keyword>`) or None.

    Deterministic order: sorted by instance path, then keyword name. A well-formed NEG case
    violates exactly one constraint, so the order rarely matters; it is defined anyway."""
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload),
                    key=lambda e: (tuple(str(p) for p in e.absolute_path), e.validator))
    if not errors:
        return None
    return f"{scope}.{errors[0].validator}"


def canonical_roundtrip(payload: object) -> bool:
    try:
        return json.loads(json.dumps(payload, ensure_ascii=False, sort_keys=True)) == payload
    except (TypeError, ValueError):
        return False


def load_frontmatter(skill_md: Path) -> tuple[dict | None, str | None]:
    text = skill_md.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "SKILL.md does not open with YAML frontmatter"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, "SKILL.md frontmatter is not terminated"
    try:
        data = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as exc:
        return None, f"frontmatter is not valid YAML: {exc}"
    if not isinstance(data, dict):
        return None, "frontmatter is not a mapping"
    return data, None


def route_match(utterance: str, triggers_by_pack: dict) -> list:
    u = utterance.casefold()
    return sorted(name for name, trig in triggers_by_pack.items()
                  if any(t.casefold() in u for t in trig))


class Checker:
    def __init__(self, skills_root: Path, check_all: bool, selected: list | None):
        self.root = skills_root
        self.check_all = check_all
        self.selected = selected
        self.refusals: list[dict] = []
        self.rows: list[dict] = []
        self.cases_run = 0
        self.cases_passed = 0
        self.loaded = 0
        self.routed = 0
        self.discovered = 0

    def refuse(self, code: str, path: str, reason: str) -> None:
        self.refusals.append({"code": code, "path": path, "reason": reason})

    # ------------------------------------------------------------- run
    def run(self) -> dict:
        if not self.root.is_dir():
            self.refuse("MISSING_ROOT", str(self.root), "skills root does not exist")
            return self.result()
        entries = {p.name: p for p in sorted(self.root.iterdir())
                   if p.is_dir() and not p.name.startswith(".") and p.name != "__pycache__"}
        self.discovered = len(entries)

        # Phase A: structural per pack.
        for name, path in entries.items():
            has_skill = (path / "SKILL.md").is_file()
            has_in = (path / "schemas" / "input.schema.json").is_file()
            has_out = (path / "schemas" / "output.schema.json").is_file()
            if not has_skill and not has_in and not has_out:
                self.refuse("MARKER_ONLY_PACK", str(path),
                            "pack holds only free-text: no SKILL.md and no input/output schemas")
            elif not has_skill:
                self.refuse("SKILL_MD_MISSING", str(path), "pack has no SKILL.md")
            elif not (has_in and has_out):
                self.refuse("MISSING_SCHEMA", str(path),
                            "pack lacks schemas/input.schema.json and/or schemas/output.schema.json")

        # Phase B: frontmatter names (duplicate skill name).
        frontmatters: dict[str, dict] = {}
        seen_names: dict[str, str] = {}
        for name, path in entries.items():
            skill_md = path / "SKILL.md"
            if not skill_md.is_file():
                continue
            fm, err = load_frontmatter(skill_md)
            if err:
                self.refuse("FRONTMATTER_INVALID", str(skill_md), err)
                continue
            frontmatters[name] = fm
            declared = str(fm.get("name", ""))
            if not declared:
                self.refuse("FRONTMATTER_INVALID", str(skill_md), "frontmatter has no name")
                continue
            if declared in seen_names:
                self.refuse("DUPLICATE_SKILL_NAME", str(skill_md),
                            f"skill name {declared!r} already declared by {seen_names[declared]}")
            else:
                seen_names[declared] = str(skill_md)

        # Phase C: exact entry set (9th / duplicate entry, missing pack).
        for name in entries:
            if name not in EXPECTED_NAMES:
                self.refuse("UNEXPECTED_ENTRY", str(entries[name]),
                            f"{name!r} is not one of the 8 PIPD SkillContracts")
        if self.check_all:
            for expected in EXPECTED_NAMES:
                if expected not in entries:
                    self.refuse("MISSING_PACK", str(self.root / expected),
                                f"required SkillContract pack {expected!r} is absent")

        if self.refusals:
            return self.result()

        # Phase D: deep validation (frontmatter, declared files, schemas, cases, routing).
        triggers_by_pack = {name: list(frontmatters[name].get("triggers") or [])
                            for name in entries if name in frontmatters}
        names = list(EXPECTED_NAMES) if self.check_all else [
            n for n in (self.selected or []) if n in entries]
        for name in names:
            self.check_pack(name, entries[name], frontmatters.get(name), triggers_by_pack)
        return self.result()

    # ------------------------------------------------------------- deep checks
    def check_pack(self, name: str, path: Path, fm: dict | None, triggers_by_pack: dict) -> None:
        if fm is None:
            self.refuse("FRONTMATTER_INVALID", str(path / "SKILL.md"), "frontmatter did not load")
            return
        before = len(self.refusals)

        if str(fm.get("name", "")) != name:
            self.refuse("NAME_MISMATCH", str(path / "SKILL.md"),
                        f"frontmatter name {fm.get('name')!r} != directory name {name!r}")
        desc = fm.get("description", "")
        if not isinstance(desc, str) or not desc.lstrip().startswith("Use when "):
            self.refuse("DESC_TRIGGER_INVALID", str(path / "SKILL.md"),
                        "description must open with a self-contained 'Use when ...' trigger")
        triggers = fm.get("triggers") or []
        if (not isinstance(triggers, list) or not triggers
                or not all(isinstance(t, str) and t.strip() for t in triggers)):
            self.refuse("FRONTMATTER_INVALID", str(path / "SKILL.md"),
                        "triggers must be a non-empty list of strings")

        # every declared schema / reference / test file must exist inside the pack
        declared: list[str] = []
        for key in ("schemas", "references", "tests"):
            items = fm.get(key) or []
            if not isinstance(items, list):
                self.refuse("FRONTMATTER_INVALID", str(path / "SKILL.md"),
                            f"{key} must be a list of relative paths")
                items = []
            declared += [str(i) for i in items]
        for rel in REQUIRED_DECLARED:
            if rel not in declared:
                self.refuse("FRONTMATTER_INVALID", str(path / "SKILL.md"),
                            f"{rel} is not declared in frontmatter")
        for rel in declared:
            rel_path = Path(rel)
            if rel_path.is_absolute() or ".." in rel_path.parts:
                self.refuse("DECLARED_FILE_MISSING", str(path / rel),
                            "declared path escapes the pack")
            elif not (path / rel_path).is_file():
                self.refuse("DECLARED_FILE_MISSING", str(path / rel), "declared file does not exist")

        schemas: dict[str, dict] = {}
        for scope in ("input", "output"):
            schema_path = path / "schemas" / f"{scope}.schema.json"
            if not schema_path.is_file():
                continue  # already refused structurally
            try:
                doc = json.loads(schema_path.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                self.refuse("SCHEMA_INVALID", str(schema_path), f"not parseable JSON: {exc}")
                continue
            problems = []
            if doc.get("$schema") != DRAFT:
                problems.append("$schema must be the Draft 2020-12 URI")
            if doc.get("type") != "object":
                problems.append("root type must be object")
            if doc.get("additionalProperties") is not False:
                problems.append("root additionalProperties must be false")
            if not doc.get("$id"):
                problems.append("$id must be present")
            try:
                Draft202012Validator.check_schema(doc)
            except Exception as exc:  # noqa: BLE001 - jsonschema raises many classes
                problems.append(f"not a valid Draft 2020-12 schema: {exc}")
            if problems:
                self.refuse("SCHEMA_INVALID", str(schema_path), "; ".join(problems))
            else:
                schemas[scope] = doc

        cases_doc = None
        cases_path = path / "tests" / "cases.yaml"
        if cases_path.is_file():
            try:
                cases_doc = yaml.safe_load(cases_path.read_text(encoding="utf-8"))
            except yaml.YAMLError as exc:
                self.refuse("CASES_INVALID", str(cases_path), f"not parseable YAML: {exc}")

        row = {"name": name, "case_kinds": [], "roundtrips": 0, "cases_run": 0,
               "cases_passed": 0, "routes_verified": False}
        if len(self.refusals) != before or cases_doc is None or len(schemas) != 2:
            if cases_doc is None and (path / "tests" / "cases.yaml").is_file():
                pass  # parse error already refused
            elif cases_doc is None:
                self.refuse("CASES_INVALID", str(cases_path), "cases.yaml is absent or empty")
            self.rows.append(row)
            return

        cases = cases_doc.get("cases") if isinstance(cases_doc, dict) else None
        problems = []
        if cases_doc.get("schema") != "PIPD-SKILL-CASES/1":
            problems.append("cases.yaml schema must be PIPD-SKILL-CASES/1")
        if cases_doc.get("skill") != name:
            problems.append(f"cases.yaml skill must be {name!r}")
        if not isinstance(cases, list) or not cases:
            problems.append("cases.yaml must carry a non-empty cases list")
            cases = []
        ids = [c.get("id") for c in cases if isinstance(c, dict)]
        if len(ids) != len(set(ids)):
            problems.append("case ids must be unique")
        kinds = {c.get("kind") for c in cases if isinstance(c, dict)}
        for kind in CASE_KINDS:
            if kind not in kinds:
                problems.append(f"cases.yaml must carry at least one {kind} case")
        for c in cases:
            if not isinstance(c, dict):
                problems.append("every case must be a mapping")
                continue
            for field in ("id", "kind", "expect", "first_fail", "input", "route"):
                if field not in c:
                    problems.append(f"case {c.get('id', '?')} is missing {field}")
            if c.get("kind") not in CASE_KINDS:
                problems.append(f"case {c.get('id', '?')} has unknown kind {c.get('kind')!r}")
            if c.get("expect") not in ("ACCEPT", "REFUSE"):
                problems.append(f"case {c.get('id', '?')} has unknown expect {c.get('expect')!r}")
            if c.get("expect") == "ACCEPT" and c.get("first_fail") != "NONE":
                problems.append(f"case {c.get('id', '?')} ACCEPT must name first_fail NONE")
            if c.get("expect") == "REFUSE" and c.get("first_fail") in (None, "", "NONE"):
                problems.append(f"case {c.get('id', '?')} REFUSE must name its expected first-fail")
            route = c.get("route") or {}
            if route.get("expect") not in ("ROUTE", "NO_ROUTE"):
                problems.append(f"case {c.get('id', '?')} has unknown route expectation")
            if not isinstance(route.get("utterance"), str):
                problems.append(f"case {c.get('id', '?')} route.utterance must be a string")
            semantic = c.get("semantic")
            if semantic is not None and (not isinstance(semantic, dict)
                                         or semantic.get("rule") not in SEMANTIC_RULES):
                problems.append(f"case {c.get('id', '?')} declares an unknown semantic rule")
        if problems:
            self.refuse("CASES_INVALID", str(cases_path), "; ".join(problems))
            self.rows.append(row)
            return

        # ------------------------------------------------ cases: round-trip + first-fail + routing
        row["case_kinds"] = sorted({c["kind"] for c in cases})
        routes_ok = 0
        for c in cases:
            self.cases_run += 1
            row["cases_run"] += 1
            ok = True
            in_fail = (first_fail(schemas["input"], c["input"], "input")
                       if isinstance(c.get("input"), dict) else "input.type")
            out_payload = c.get("output")
            out_fail = (first_fail(schemas["output"], out_payload, "output")
                        if out_payload is not None else None)
            overall = in_fail or out_fail

            if c["expect"] == "ACCEPT":
                if out_payload is None:
                    ok = False
                    why = "ACCEPT case must carry both input and output payloads"
                elif overall is not None:
                    ok = False
                    why = f"ACCEPT case rejected at {overall}"
                elif not (canonical_roundtrip(c["input"]) and canonical_roundtrip(out_payload)):
                    ok = False
                    why = "payload does not survive a canonical JSON round-trip"
                else:
                    row["roundtrips"] += 2
                    why = ""
                semantic = c.get("semantic")
                if ok and semantic is not None:
                    rule = SEMANTIC_RULES[semantic["rule"]]
                    if not rule(c["input"], semantic.get("fields")):
                        ok = False
                        why = f"semantic rule {semantic['rule']} is violated on an ACCEPT case"
            else:  # REFUSE
                expected = c["first_fail"]
                if expected.startswith("semantic."):
                    rule_name = expected.split(".", 1)[1]
                    if rule_name not in SEMANTIC_RULES:
                        ok = False
                        why = f"unknown semantic first-fail {expected!r}"
                    elif overall is not None:
                        ok = False
                        why = (f"expected first-fail {expected} but the schema layer fires first "
                               f"at {overall}")
                    else:
                        rule = SEMANTIC_RULES[rule_name]
                        fields = (c.get("semantic") or {}).get("fields")
                        if rule(c["input"], fields):
                            ok = False
                            why = f"expected {expected} but semantic rule {rule_name} holds"
                        else:
                            why = ""
                elif overall is None:
                    ok = False
                    why = f"expected first-fail {expected} but every payload validates"
                elif overall != expected:
                    ok = False
                    why = f"expected first-fail {expected} but the first failure is {overall}"
                else:
                    why = ""

            # trigger / non-trigger routing
            matched = route_match(c["route"]["utterance"], triggers_by_pack)
            if c["route"]["expect"] == "ROUTE":
                if name not in matched or len(matched) != 1:
                    ok = False
                    why = why or f"utterance routes to {matched}, expected exactly [{name}]"
                else:
                    routes_ok += 1
            else:
                if name in matched:
                    ok = False
                    why = why or f"non-trigger utterance routed to {name}"
                else:
                    routes_ok += 1

            if ok:
                self.cases_passed += 1
                row["cases_passed"] += 1
            else:
                self.refuse("CASE_FAIL", f"{name}/tests/cases.yaml:{c['id']}", why)

        row["routes_verified"] = routes_ok == len(cases) and any(
            c["route"]["expect"] == "ROUTE" for c in cases)
        if row["routes_verified"]:
            self.routed += 1
        else:
            self.refuse("ROUTING_FAIL", str(cases_path), "trigger/non-trigger routing did not verify")
        self.loaded += 1
        self.rows.append(row)

    # ------------------------------------------------------------- result
    def result(self) -> dict:
        if not self.refusals:
            state = "PASS"
        elif any(r["code"] in STRUCTURAL_CODES for r in self.refusals):
            state = "REFUSED"
        else:
            state = "FAIL"
        return {"checker": "skill-pack-check/1", "state": state,
                "skills_root": str(self.root),
                "discovered": self.discovered, "loaded": self.loaded, "routed": self.routed,
                "cases_run": self.cases_run, "cases_passed": self.cases_passed,
                "first_failing_invariant": self.refusals[0]["code"] if self.refusals else "NONE",
                "refusals": self.refusals, "skills": self.rows}


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description="PIPD skill-pack discover/load/route checker")
    ap.add_argument("--all", action="store_true", help="check all 8 packs (exact-set gate)")
    ap.add_argument("--skill", action="append", default=None,
                    help="check one named pack (repeatable; skips the exact-set gate)")
    ap.add_argument("--skills-root", default=str(ROOT / "skills"),
                    help="skills root to discover packs under (default: <repo>/skills)")
    args = ap.parse_args(argv)
    if not args.all and not args.skill:
        print(json.dumps({"checker": "skill-pack-check/1", "state": "REFUSED",
                          "refusals": [{"code": "USAGE_INVALID", "path": "argv",
                                        "reason": "pass --all or --skill NAME"}]}, indent=1))
        return 2
    result = Checker(Path(args.skills_root), args.all, args.skill).run()
    print(json.dumps(result, indent=1, ensure_ascii=False))
    return 0 if result["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
