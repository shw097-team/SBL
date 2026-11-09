"""Verify the six reader receipts — signature first, then structure, with no fail-open.

Three rules this file exists to enforce, each bought with a defect found by an independent lane:

1. Signature before structure. A structural check on an unsigned body verifies nothing.
2. A clause span is re-derived, never trusted. `clause_id` is itself a coordinate (`WP-FHS-xx:L1:<n>`),
   so the line is located from the id, not from a path the receipt supplies. A path that is absent, a line
   that does not exist, or bytes that hash differently are REFUSALS - not checks to skip.
3. A lane comparison must name distinct lanes. Two entries both called `A` is one lane wearing two hats.

Refusal codes
    SIGNATURE_INVALID / ENVELOPE_MALFORMED      cryptography first
    FIELD_ABSENT / FIELD_EMPTY                  blueprint field set (L0.md:377)
    NO_CLAUSES                                  certifies nothing
    CLAUSE_ID_UNPARSEABLE / SPAN_NOT_RESOLVED   the id does not name a real line
    CLAUSE_DIGEST_DRIFT                         the line's bytes changed
    PRESERVATION_MISSING                        a clause has no four-property judgement
    NO_NEGATIVE_FIXTURE / NEGATIVE_DOES_NOT_BITE
    READER_IS_MAKER / LANES_NOT_DISTINCT
    OPEN_DISAGREEMENT                           the register still holds one for this work package
    SELF_REFERENCE / COVERAGE_UNDECLARED
"""
from __future__ import annotations
import hashlib, json, os, re, sys

ROUND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = ["Subject", "SourceSHA", "CandidateSHA", "Scope", "Host", "PolicyEpoch", "OriginalConsumer"]
PROPS = ("parent_preserved", "exceptions_preserved", "negations_preserved", "scope_preserved")
MAKER = "hermes-execute-lane"
CID = re.compile(r"^([A-Z]{2}-FHS-\d{2}):L1:(\d+)$")
REGISTRY = r"C:\Projects\Agent_Workspace\var\B1-PIPD-PKG-20261027\admission\registry\runner-registry.json"


def canon(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify_signature(env: dict) -> tuple[bool, str]:
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        reg = json.load(open(REGISTRY, encoding="utf-8"))
        pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(reg["owner_enrollment"]["public_hex"]))
        body = env["body"]
        p = canon(body)
        if hashlib.sha256(p).hexdigest() != env.get("payload_sha256"):
            return False, "payload digest mismatch"
        pub.verify(bytes.fromhex(env["signature_hex"]), p)
        return True, ""
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def verify(body: dict, env_ok: bool, ctx: dict) -> list[tuple[str, str]]:
    bad: list[tuple[str, str]] = []
    if not env_ok:
        bad.append(("envelope", "SIGNATURE_INVALID"))
    for f in FIELDS:
        v = body.get(f)
        if v is None:
            bad.append((f, "FIELD_ABSENT"))
        elif isinstance(v, str) and not v.strip():
            bad.append((f, "FIELD_EMPTY"))

    clauses = body.get("clauses") or []
    if not clauses:
        bad.append(("clauses", "NO_CLAUSES"))
    for c in clauses:
        cid = c.get("clause_id") or ""
        m = CID.match(cid)
        if not m:
            bad.append((cid or "?", "CLAUSE_ID_UNPARSEABLE"))
            continue
        n = int(m.group(2))
        lines = ctx["l1"]
        if n < 1 or n > len(lines):
            bad.append((cid, "SPAN_NOT_RESOLVED"))
            continue
        if hashlib.sha256(lines[n - 1]).hexdigest() != c.get("clause_sha256"):
            bad.append((cid, "CLAUSE_DIGEST_DRIFT"))
        sp = c.get("span") or {}
        if sp.get("line_start") != n:
            bad.append((cid, "SPAN_NOT_RESOLVED"))
        pres = c.get("preservation") or {}
        if not all(p in pres and pres[p].get("value") in (True, False) for p in PROPS):
            bad.append((cid, "PRESERVATION_MISSING"))

    # r25 / EC-R24-002: a boolean value is not a decision. The signed vote count is checked here too, so a
    # receipt that says DECIDED without two agreeing valid votes is refused by this verifier and not only by G29.
    try:
        import importlib.util as _iu
        _sp = _iu.spec_from_file_location("verify_quorum_inline",
                                          os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_quorum.py"))
        _m = _iu.module_from_spec(_sp)
        _sp.loader.exec_module(_m)
        for _c in body.get("clauses") or []:
            for _name, _prop in (_c.get("preservation") or {}).items():
                _v = _m.evaluate(_prop, effective_candidate=(body.get("quorum_candidate_sha256")
                                 or (body.get("binding") or {}).get("candidate_sha256")
                                 or body.get("CandidateSHA")))
                if _v["verdict"] != "ACCEPTABLE_FOR_FHS_READER_SCOPE":
                    bad.append((_c.get("clause_id"), _v["first_fail"]))
    except ImportError:
        bad.append(("quorum", "QUORUM_CHECKER_ABSENT"))

    fx = ctx["fixtures"].get(body.get("Subject"))
    if not fx:
        bad.append(("negative_fixture", "NO_NEGATIVE_FIXTURE"))
    else:
        probe = fx.get("wrong_reading_probe") or {}
        if (fx.get("must_return") != "REJECTED:FORBIDDEN_SHORTCUT_ASSERTED"
                or probe.get("pos_cell_now_contains_shortcut") is not True
                or probe.get("pos_column_located_structurally") is not True):
            bad.append(("negative_fixture", "NEGATIVE_DOES_NOT_BITE"))

    ident = (body.get("reader_identity") or "").strip().lower()
    if not ident or ident == MAKER:
        bad.append(("reader_identity", "READER_IS_MAKER"))
    lanes = [str(d.get("lane") or "").strip().upper() for d in (body.get("dual_lane_comparison") or [])]
    lanes = [x for x in lanes if x]
    if len(lanes) < 2 or len(set(lanes)) != len(lanes):
        bad.append(("dual_lane_comparison", "LANES_NOT_DISTINCT"))

    for row in (ctx["register"].get("receipts") or ctx["register"].get("issuability") or []):
        if row.get("wp") == body.get("Subject") and not row.get("issuable", True):
            bad.append(("disagreement_register", "OPEN_DISAGREEMENT"))

    blob = json.dumps(body, ensure_ascii=False).lower()
    if '"bytes"' in blob or "self_sha256" in blob:
        bad.append(("self", "SELF_REFERENCE"))
    if body.get("citation_density") == "UNDER_CITED" and not body.get("coverage_basis"):
        bad.append(("coverage_basis", "COVERAGE_UNDECLARED"))
    return bad


def load_ctx() -> dict:
    C = json.load(open(os.path.join(ROUND, "lanes", "CLAUSES.json"), encoding="utf-8"))
    return {"l1": open(C["source"], "rb").read().split(b"\n"),
            "fixtures": json.load(open(os.path.join(ROUND, "lanes", "DEDICATED_NEGATIVES.json"),
                                       encoding="utf-8"))["by_wp"],
            "register": json.load(open(os.path.join(ROUND, "lanes", "DISAGREEMENT_REGISTER.json"),
                                       encoding="utf-8"))}


def main() -> int:
    ctx = load_ctx()
    d = os.path.join(ROUND, "receipts", "reader")
    files = sorted(f for f in os.listdir(d) if f.endswith(".signed.json"))
    if not files:
        print("no signed envelopes in receipts/reader")
        return 2
    if "--selftest" in sys.argv:
        env = json.load(open(os.path.join(d, files[0]), encoding="utf-8"))
        ok, why = verify_signature(env)
        base = verify(env["body"], ok, ctx)
        print(f"selftest on {files[0]} | signature {ok} | BASELINE {'CLEAN' if not base else base}")
        if not ok:
            print(f"  cannot mutate: baseline does not verify ({why})")
            return 1

        def cl(b):
            return b["clauses"][0]

        mutants = {
            "drop clauses": lambda b: {**b, "clauses": []},
            "blank reader": lambda b: {**b, "reader_identity": ""},
            "reader is maker": lambda b: {**b, "reader_identity": MAKER},
            "duplicate lanes": lambda b: {**b, "dual_lane_comparison": [{"lane": "A"}, {"lane": "A"}]},
            "drop a field": lambda b: {k: v for k, v in b.items() if k != "PolicyEpoch"},
            "fabricate a digest": lambda b: {**b, "clauses": [dict(cl(b), clause_sha256="0" * 64)] + b["clauses"][1:]},
            "nonexistent line": lambda b: {**b, "clauses": [dict(cl(b), clause_id="WP-FHS-00:L1:999999")] + b["clauses"][1:]},
            "strip preservation": lambda b: {**b, "clauses": [dict(cl(b), preservation={})] + b["clauses"][1:]},
        }
        fired = 0
        for name, fn in mutants.items():
            got = verify(fn(env["body"]), True, ctx)
            hit = bool(got) and got != base
            fired += hit
            print(f"  {name:<22} -> {'FIRED' if hit else 'MISSED'} {got[:2] if got else ''}")
        print(f"  fired {fired}/{len(mutants)}")
        return 0 if fired == len(mutants) else 5

    bad_total = 0
    for f in files:
        env = json.load(open(os.path.join(d, f), encoding="utf-8"))
        ok, why = verify_signature(env)
        bad = verify(env["body"], ok, ctx)
        bad_total += bool(bad)
        print(f"{f:<30} sig={'OK' if ok else 'BAD ' + why:<12} {'PASS' if not bad else 'REFUSED ' + str(bad)}")
    print(f"\n{len(files) - bad_total}/{len(files)} receipts verified")
    return 0 if bad_total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
