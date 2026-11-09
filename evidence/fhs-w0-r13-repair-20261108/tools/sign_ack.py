"""Sign the acceptance instrument with the owner key that the window holds.

The window signs arbitrary bytes; the only thing it checks is that the declared payload_sha256 equals
sha256(body). So this client refuses to be the place where meaning gets invented:

  * it takes the body from the PLAN lane's spec and does not add or drop a field;
  * it refuses a body that carries its own digest or size;
  * it refuses a body that asserts ORIGINAL_ACK positively;
  * it removes ops_used from the body, because that number does not exist until after signing - a
    signature cannot cover a fact that only exists once the signature is made;
  * it verifies the returned signature against the enrolled public key before writing anything.

The passphrase never passes through here: the window already holds the unlocked key.
"""
from __future__ import annotations
import hashlib, importlib.util, json, os, pathlib, re, sys

ROUND = pathlib.Path(__file__).resolve().parent.parent
TOOL = pathlib.Path(os.environ.get("HGK_OWNER_WINDOW_TOOL") or
                    r"C:\Projects\Agent_Workspace\HG-KSEOS\ops\session-20261031\tools\owner_window.py")
REGISTRY = pathlib.Path(r"C:\Projects\Agent_Workspace\var\B1-PIPD-PKG-20261027\admission\registry\runner-registry.json")
SPEC = ROUND / "lanes" / "PLAN_ACK_SPEC.json"
OUT = ROUND / "receipts" / "OWNER_SEMANTIC_ACK.signed.json"


def canon_jcs(obj) -> bytes:
    """JCS-style: sorted keys, no whitespace, UTF-8, no ASCII escaping. Stated so a verifier can repeat it."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_tool():
    spec = importlib.util.spec_from_file_location("owner_window", str(TOOL))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    spec = json.load(open(SPEC, encoding="utf-8"))
    body = dict(spec.get("body") or {})
    problems = []

    flat = json.dumps(body, ensure_ascii=False)
    if re.search(r'"(body_sha256|self_sha256|own_digest|self_bytes)"', flat):
        problems.append("body carries its own digest or size")
    if re.search(r'"(ORIGINAL_ACK|original_ack)"\s*:\s*(true|"ACK"|"PASS")', flat):
        problems.append("body asserts ORIGINAL_ACK positively")
    body.pop("ops_used", None)
    if isinstance(body.get("window"), dict) and "ops_used" in body["window"]:
        # the count of operations only exists once this signature is made, so it cannot be inside the
        # bytes being signed; it is recorded beside the signature instead
        body["window"].pop("ops_used", None)
    if not body.get("receipts") or not isinstance(body.get("receipts"), (list, dict)):
        problems.append("body does not bind the receipts")
    if problems:
        print(json.dumps({"signed": False, "refused": problems}, ensure_ascii=False, indent=1))
        return 3

    payload = canon_jcs(body)
    payload_sha = hashlib.sha256(payload).hexdigest()

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tool = load_tool()
    try:
        r = tool._post("/sign", {"kind": spec.get("kind") or "owner_semantic_accept",
                                 "effect_class": "READ_ONLY_PROBE",
                                 "enrollments_sha256": tool.enrollment_sha(reg),
                                 "payload_sha256": payload_sha,
                                 "body_json": payload.decode("utf-8")})
    except Exception as e:
        print(json.dumps({"signed": False, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False, indent=1))
        return 4

    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    pub = bytes.fromhex(reg["owner_enrollment"]["public_hex"])
    try:
        Ed25519PublicKey.from_public_bytes(pub).verify(bytes.fromhex(r["signature_hex"]), payload)
        verified = True
    except Exception:
        verified = False
    if not verified:
        print(json.dumps({"signed": False, "error": "SIGNATURE_DOES_NOT_VERIFY", "response": r}, ensure_ascii=False, indent=1))
        return 5

    out = {
        "schema": "FHS.W0.OwnerSemanticAckSigned/1",
        "round": spec.get("round") or "FHS_W0_R13_ACCEPTANCE_20261108",
        "body": body,
        "canonical_rule": spec.get("canonical_rule") or {"function": "jcs-compact", "encoding": "utf-8",
                                                          "notes": "sorted keys, separators (',',':'), ensure_ascii=False"},
        "payload_sha256": payload_sha,
        "signature_hex": r["signature_hex"],
        "alg": "ed25519",
        "signature_meta": {"window_id": r.get("window_id"), "ops_used": r.get("ops_used"),
                           "signed_at": __import__("datetime").datetime.now(
                               __import__("datetime").timezone(__import__("datetime").timedelta(hours=8))
                           ).isoformat(timespec="seconds"),
                           "instructions_signed_with": "kind=owner_semantic_accept via window",
                           "registry_rev_at_open": json.load(open(tool.WINDOW_FILE, encoding="utf-8")).get("policy_epoch_at_open"),
                           "why_that_name": ("the window stores the runner registry revision under a field "
                                             "called policy_epoch_at_open; naming it the same as the lane "
                                             "policy epoch is the collision VERIFY ACK-1 found")},
        "owner_fingerprint": json.load(open(tool.WINDOW_FILE, encoding="utf-8")).get("owner_fingerprint"),
        "verified_locally_against": "owner_enrollment.public_hex",
        "not_claimed": ["ORIGINAL_ACK", "NATIVE_SIGNED", "RELEASE_GRANTED", "principal_separation"],
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({"signed": True, "verified": True, "payload_sha256": payload_sha,
                      "signature_prefix": r["signature_hex"][:24], "window_id": r.get("window_id"),
                      "ops_used": r.get("ops_used"), "written": str(OUT)}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
