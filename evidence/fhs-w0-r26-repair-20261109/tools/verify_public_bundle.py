#!/usr/bin/env python3
"""Verify the seven owner signatures in PUBLIC_VERIFICATION_BUNDLE.json with real Ed25519.

No simulation, no prefix comparison. For every signature reference this re-derives the signed
payload bytes, re-computes their SHA-256, compares that against the declared `payload_sha256`
(both the bundle's and the envelope's own), and then runs an actual Ed25519 verification against
the enrolled owner public key. A matching 16-hex `signature_hex_prefix` is printed for the reader's
convenience and never counted as evidence.

Canonicalisation. The signer (`FHS_W0_R13_ACCEPTANCE_20261108/tools/sign_r26.py`) builds the payload as

    json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

and the round's own reader (`tools/verify_reader_ack.py`) and editor (`tools/verify_quorum.py`) use
the identical `canon()`. This file uses the same one. Two candidates are computed and printed when the
primary one does not reproduce, so a failure is reported as CANONICALISATION_UNRESOLVED with both
measured digests instead of being guessed at.

Exit codes
    0  all seven signatures verify and every declared digests reproduces
    1  the first file that fails (named on stdout) — verification is not fail-open
    2  the bundle or the public key is absent/malformed
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

ROUND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUNDLE = os.path.join(ROUND, "evidence", "PUBLIC_VERIFICATION_BUNDLE.json")

CANON_PRIMARY = "json.dumps(body, sort_keys=True, separators=(',',':'), ensure_ascii=False).encode('utf-8')"
CANON_ASCII = "json.dumps(body, sort_keys=True, separators=(',',':'), ensure_ascii=True).encode('utf-8')"

#: positional offsets in an ISO-8601 string after which a UTC offset / Z must appear
_TZ_MARKERS = ("+", "-", "Z", "z")


def canon_primary(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canon_ascii(o) -> bytes:
    return json.dumps(o, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def has_offset(ts: str) -> bool:
    """True when an ISO-8601 timestamp carries an explicit UTC offset or Z."""
    if not isinstance(ts, str) or "T" not in ts:
        return False
    return any(m in ts[10:] for m in _TZ_MARKERS)


def refs_from_bundle(b: dict) -> list[dict]:
    """The bundle's seven references: six reader receipts plus the semantic acceptance."""
    out = []
    for s in b.get("signatures") or []:
        out.append({"file": s["file"], "kind": s.get("kind"),
                    "declared_payload_sha256": s.get("payload_sha256"),
                    "declared_prefix": s.get("signature_hex_prefix")})
    sem = b.get("semantic_ack") or {}
    if sem.get("file"):
        out.append({"file": sem["file"], "kind": sem.get("kind"),
                    "declared_payload_sha256": sem.get("payload_sha256"),
                    "declared_prefix": sem.get("signature_hex_prefix")})
    return out


def verify_seven(pub_hex: str, bundle: dict) -> tuple[list[dict], str | None]:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    pk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
    rows, first_fail = [], None
    for ref in refs_from_bundle(bundle):
        path = os.path.join(ROUND, ref["file"].replace("/", os.sep))
        row = {"file": ref["file"], "kind": ref["kind"],
               "declared_payload_sha256": ref["declared_payload_sha256"],
               "declared_prefix": ref["declared_prefix"]}
        if not os.path.isfile(path):
            row.update({"verdict": "FILE_ABSENT", "signature_valid": False})
            rows.append(row)
            if first_fail is None:
                first_fail = ref["file"]
            continue
        try:
            env = json.loads(open(path, "r", encoding="utf-8").read())
        except ValueError as e:
            row.update({"verdict": f"ENVELOPE_MALFORMED: {e}", "signature_valid": False})
            first_fail = first_fail or ref["file"]
            rows.append(row)
            continue
        body = env.get("body")
        sig_hex = env.get("signature_hex") or ""
        payload = canon_primary(body)
        recomputed = sha(payload)
        row["envelope_payload_sha256"] = env.get("payload_sha256")
        row["recomputed_payload_sha256"] = recomputed
        row["payload_digest_matches_declared"] = (
            recomputed == ref["declared_payload_sha256"] == env.get("payload_sha256"))
        row["signature_hex_prefix"] = sig_hex[:16]
        row["prefix_matches_declared"] = row["signature_hex_prefix"] == ref["declared_prefix"]

        # both candidates are always measured so an unresolved canonicalisation is reported, not guessed
        row["candidate_sha_primary"] = recomputed
        row["candidate_sha_ascii"] = sha(canon_ascii(body))

        valid = False
        why = ""
        try:
            pk.verify(bytes.fromhex(sig_hex), payload)
            valid = True
        except Exception as e:  # InvalidSignature and malformed hex both land here
            why = f"{type(e).__name__}"
            if not row["payload_digest_matches_declared"]:
                why = "CANONICALISATION_UNRESOLVED " + why
        row["signature_valid"] = valid
        row["signature_error"] = why
        row["verdict"] = ("VERIFIED" if valid and row["payload_digest_matches_declared"]
                          else "FAILED")
        if row["verdict"] != "VERIFIED" and first_fail is None:
            first_fail = ref["file"]
        rows.append(row)
    return rows, first_fail


def tz_finding(bundle: dict, env_rows: dict) -> dict:
    """FINDING_R26-06_TZ_UNQUALIFIED — measured, not read off a comment.

    `preauth_at` carries no UTC offset while `verify_pass_at`/`signed_at` carry `+08:00`, so the
    order predicate `preauth_at < verify_pass_at` is only decidable if the reader assumes a zone.
    """
    seq = bundle.get("sequence") or {}
    pre, ver, sig = seq.get("preauth_at"), seq.get("verify_pass_at"), seq.get("signed_at")
    unqualified = [k for k, v in (("preauth_at", pre), ("verify_pass_at", ver), ("signed_at", sig))
                   if v is not None and not has_offset(v)]
    sem_seq = (env_rows.get("receipts/OWNER_SEMANTIC_ACK_R26.signed.json") or {}).get("sequence") or {}
    sem_unqualified = [k for k, v in sem_seq.items()
                       if k in ("preauth_at", "verify_pass_at", "signed_at")
                       and isinstance(v, str) and not has_offset(v)]
    return {
        "id": "FINDING_R26-06_TZ_UNQUALIFIED",
        "state": "OPEN",
        "where": ["evidence/PUBLIC_VERIFICATION_BUNDLE.json#sequence",
                  "receipts/OWNER_SEMANTIC_ACK_R26.signed.json#sequence"],
        "measured": {"bundle_sequence": seq, "bundle_fields_without_offset": unqualified,
                     "signed_envelope_sequence": sem_seq,
                     "signed_envelope_fields_without_offset": sem_unqualified,
                     "now_local_offset": "+08:00"},
        "why_it_matters": (
            "`preauth_at` is the owner window's opening time and the only lower bound on the signing "
            "order. Without a zone the predicate `preauth_at < verify_pass_at <= signed_at` is evaluated "
            "in whatever zone the reader assumes; read as UTC it is 08:00 later than read as +08:00, so "
            "a bundle that would fail the order check under one reading passes under the other"),
        "not_fixed_here": (
            "the bundle and the signed envelope are signatures; rewriting either would change a signed "
            "payload digest and produce a receipt that no owner signed. This round does not re-sign"),
        "closes_when": (
            "the owner re-signs a semantic acceptance whose body carries `preauthorised_at` WITH an "
            "explicit offset (the body already does: sign_r26.py writes `win['opened_at']` into "
            "`body.preauthorised_at`) and republishes a bundle whose `sequence.preauth_at` is the same "
            "qualified string; then payload_sha256 and signature_hex change and this verifier must be "
            "re-run against the new envelope"),
        "exact_resign_scope": {
            "envelope": "receipts/OWNER_SEMANTIC_ACK_R26.signed.json (new file, new payload_sha256)",
            "bundle_fields": ["sequence.preauth_at", "sequence.verify_pass_at", "sequence.signed_at",
                              "semantic_ack.payload_sha256", "semantic_ack.signature_hex_prefix"],
            "documented_by": "the new bundle must state the offset it qualifies all three with",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", default=BUNDLE)
    ap.add_argument("--json", default=None, help="write the full measurement here")
    ap.add_argument("--selftest", action="store_true",
                    help="mutate one signed body and prove the verifier refuses (exit 1, named code)")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()

    if not os.path.isfile(a.bundle):
        print(json.dumps({"verdict": "BLOCKED", "code": "BUNDLE_ABSENT", "path": a.bundle}))
        return 2
    bundle = json.loads(open(a.bundle, "r", encoding="utf-8").read())
    pub_hex = ((bundle.get("public_key") or {}).get("hex") or "").strip()
    if len(pub_hex) != 64:
        print(json.dumps({"verdict": "BLOCKED", "code": "PUBLIC_KEY_MALFORMED", "hex": pub_hex}))
        return 2

    if a.selftest:
        return selftest(pub_hex, bundle, a)

    rows, first_fail = verify_seven(pub_hex, bundle)
    env_rows = {}
    for ref in refs_from_bundle(bundle):
        p = os.path.join(ROUND, ref["file"].replace("/", os.sep))
        if os.path.isfile(p):
            try:
                env_rows[ref["file"]] = json.loads(open(p, "r", encoding="utf-8").read())
            except ValueError:
                pass
    finding = tz_finding(bundle, env_rows)

    ok = sum(1 for r in rows if r["verdict"] == "VERIFIED")
    report = {
        "schema": "FHS.W0.PublicBundleVerify/1",
        "bundle": a.bundle.replace("\\", "/"),
        "bundle_sha256": sha(open(a.bundle, "rb").read()),
        "public_key_hex": pub_hex,
        "key_id": (bundle.get("public_key") or {}).get("key_id"),
        "canonicalisation": CANON_PRIMARY,
        "signatures": rows,
        "summary": {"total": len(rows), "verified": ok, "failed": len(rows) - ok,
                    "first_fail": first_fail},
        "findings": [finding],
        "verdict": "ALL_SEVEN_VERIFIED" if ok == len(rows) == 7 else "VERIFY_FAILED",
        "claim_ceiling": "SIGNATURE_VALIDITY_ONLY_NOT_OWNER_INTENT",
        "not_claimed": ["that the owner's intent is correctly captured by the body",
                        "NATIVE_SIGNED", "RELEASE_GRANTED"],
    }
    if not a.quiet:
        print(f"{'file':<46} {'recomputed':<18} {'declared':<18} {'digest':<7} {'sig':<9} prefix")
        for r in rows:
            rc = (r.get("recomputed_payload_sha256") or "-")[:16]
            dc = (r.get("declared_payload_sha256") or "-")[:16]
            print(f"{r['file']:<46} {rc:<18} {dc:<18} "
                  f"{str(r.get('payload_digest_matches_declared')):<7} "
                  f"{str(r['signature_valid']):<9} "
                  f"{r.get('signature_hex_prefix', '-')}"
                  f"{'' if r.get('prefix_matches_declared') else ' (declared ' + str(r.get('declared_prefix')) + ')'}")
        print(f"\n{ok}/{len(rows)} signatures verified against owner key {pub_hex[:16]}... "
              f"({report['summary']['first_fail'] or 'no failure'})")
        print(f"[OPEN] {finding['id']}: preauth_at={finding['measured']['bundle_sequence'].get('preauth_at')!r} "
              f"carries no UTC offset while verify_pass_at="
              f"{finding['measured']['bundle_sequence'].get('verify_pass_at')!r} does")
        print("VERDICT " + report["verdict"])

    if a.json:
        os.makedirs(os.path.dirname(os.path.abspath(a.json)) or ".", exist_ok=True)
        with open(a.json, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(report, fh, ensure_ascii=False, indent=1)
            fh.write("\n")

    if report["verdict"] != "ALL_SEVEN_VERIFIED":
        print(f"FIRST_FAIL {first_fail}")
        return 1
    return 0


def selftest(pub_hex: str, bundle: dict, a) -> int:
    """One mutation must be refused with a named code. A verifier nobody has tried to fool is a guess."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    pk = Ed25519PublicKey.from_public_bytes(bytes.fromhex(pub_hex))
    ref = refs_from_bundle(bundle)[0]
    path = os.path.join(ROUND, ref["file"].replace("/", os.sep))
    env = json.loads(open(path, "r", encoding="utf-8").read())
    payload = canon_primary(env["body"])
    base_ok = True
    try:
        pk.verify(bytes.fromhex(env["signature_hex"]), payload)
    except Exception:  # noqa: BLE001
        base_ok = False
    print(f"selftest on {ref['file']} | baseline signature {'OK' if base_ok else 'BAD'}")
    if not base_ok:
        print("cannot mutate: the baseline does not verify, so a refusal would prove nothing")
        return 3

    mutants = {"append a body key": lambda b: {**b, "selftest_nonce": 1},
               "drop one existing body key": lambda b: {k: v for k, v in b.items()
                                                        if k != sorted(b)[0]},
               "perturb one body value": lambda b: {**b, sorted(b)[1]: _bump(b[sorted(b)[1]])},
               "re-serialise with indent (same object)": None}

    def deep(b):
        import copy
        c = copy.deepcopy(b)
        for clause in c.get("clauses") or []:
            for prop in (clause.get("preservation") or {}).values():
                if isinstance(prop, dict) and isinstance(prop.get("value"), bool):
                    prop["value"] = not prop["value"]
                    return c
        rr = c.get("reader_receipts") or []
        if rr:
            rr[0] = {**rr[0], "payload_sha256": "0" * 64}
        return c

    mutants["flip one deep preservation value"] = deep

    fired = 0
    total = 0
    for name, fn in mutants.items():
        total += 1
        if fn is None:
            p = json.dumps(env["body"], sort_keys=True, indent=1).encode("utf-8")
        else:
            p = canon_primary(fn(env["body"]))
        digest_moved = sha(p) != env["payload_sha256"]
        refused = False
        code = ""
        try:
            pk.verify(bytes.fromhex(env["signature_hex"]), p)
        except Exception as e:  # noqa: BLE001
            refused = True
            code = type(e).__name__
        good = refused and digest_moved
        fired += 1 if good else 0
        print(f"  {name:<42} digest_moved={str(digest_moved):<5} "
              f"refused={str(refused):<5} {code:<18} {'FIRED' if good else 'MISSED'}")
    # a pure re-serialisation (same body, ascii escape) must ALSO fail: proof the digest is over bytes,
    # not over a parsed object that two different serialisers could resemble
    p_ascii = canon_ascii(env["body"])
    ascii_differs = sha(p_ascii) != env["payload_sha256"]
    ascii_refused = False
    try:
        pk.verify(bytes.fromhex(env["signature_hex"]), p_ascii)
    except Exception:  # noqa: BLE001
        ascii_refused = True
    total += 1
    print(f"  {'ascii-escaped re-serialisation':<42} digest_moved={str(ascii_differs):<5} "
          f"refused={str(ascii_refused):<5} {'':<18} "
          f"{'FIRED' if (ascii_differs and ascii_refused) else 'MISSED'}")
    fired += 1 if (ascii_differs and ascii_refused) else 0
    print(f"  fired {fired}/{total}")
    return 0 if fired == total else 1


def _bump(v):
    if isinstance(v, bool):
        return not v
    if isinstance(v, int):
        return v + 1
    if isinstance(v, str):
        return v + "SELFTEST"
    if isinstance(v, list):
        return v + ["SELFTEST"]
    if isinstance(v, dict):
        return {**v, "selftest_nonce": 1}
    return "SELFTEST"


if __name__ == "__main__":
    sys.exit(main())
