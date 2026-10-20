# 95 — SWOF W2 handoff (sanitised, shadow only)

> **Ceiling: `W2_SHADOW_ONLY`.** Nothing here is a W3 receiver acknowledgement, and none can be produced
> from the SBL side. `SWOF_W3` and `PRODUCTION` remain `NOT_GRANTED`.

## What SWOF may consume

| Item | Value | Meaning |
|---|---|---|
| Product | `shw097-team/SBL` | independent product; not SWOF GENIE, not HGK |
| Foundation candidate | `bedc11957d4fc2474b249b69d200829272c118ef` | reviewed by the audit, not merged |
| C-track candidate | `39c604d52570922fdf84b6df9c9359765643b450` | plugin packaging slice, CI green |
| Packaging preview | wheel `95e57c44…` / sdist `5babefeb…` | builds from `bedc119`, clean-install verified |
| Mode | `PREW3_SHADOW` | any effect request is `no_effect=true` by construction |
| `SWOF_CONNECTED` | refused | needs a native ACK signed by a configured issuer; absent |

## What the handoff carries

1. **No-effect shadow contract.** `ModeGate("PREW3_SHADOW").decide(anything)` returns
   `allowed=false, no_effect=true`. This is asserted by tests, not promised by prose.
2. **The ACK shape SWOF would have to produce.** `{"issuer", "permit_id", "subject_id", "signature"}`
   where the signature is `HMAC-SHA256(key, "len:issuer|len:permit_id|len:subject_id")` and `issuer` must
   appear in `SBL_SWOF_ACK_ISSUERS` with a key in `SBL_SWOF_ACK_KEY`. Without both environment values the
   gate refuses (`NO_TRUSTED_ISSUERS_CONFIGURED` / `NO_VERIFICATION_KEY_CONFIGURED`), which is the
   correct behaviour for a world SBL cannot verify.
3. **Trace ids.** Evidence locators in `_governance/round-20261020-r3/` are stable and content-hashed;
   a SWOF receiver can bind to them without reading SBL's private corpus.

## What SWOF must not assume

- That `MERGED` happened: `main` is still `ca6830d`.
- That a release exists: no tag, no Release, no published wheel.
- That the three plugins are installed: packages exist, ids do not.
- That a `PASS_CHALLENGE` exists: the mandated checker never completed a verdict; a human procedural
  acceptance, if signed, is explicitly not the same thing.

## Next legal step on the SWOF side

SWOF's own registry, receiver and Owner ACK are required to move from W2 shadow to W3. SBL cannot
generate that receipt, and this handoff deliberately does not pretend to. When SWOF has a receiver it
wants to test, the SBL side can supply: the no-effect gate tests, the ACK verification code
(`sbl_core/modes.py`), and the frozen product SHA — nothing that would let SBL write a SWOF verdict.
