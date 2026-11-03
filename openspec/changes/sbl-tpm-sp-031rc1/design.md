# design — why a new candidate rather than a patched rc.2

The pin set is content-addressed: it names every reader module by digest. When the reader changed,
the candidate that pins it became a *different candidate*, not a stale copy of the old one. Overwriting
```
rc.2 would also violate the sealed-artifact rule, so `0.3.1-rc.1` is the honest identity for it.

Two things were deliberately not done:

1. **The candidate does not compute its own pins.** `OriginalPipd` already refuses a pin set that
   disagrees with the reader; letting the candidate generate that set would make the check circular.
   The set comes from `integrations/pipd/tools/issue_reader_pins.py`, which refuses a dirty tree and
   re-reads every file from the `HEAD` blob.
2. **The owner signature is not a grant.** It ratifies a 35-file identity statement at a named commit.
   Runtime authority remains the digest comparison; `grant_state` stays `NOT_GRANTED` and
   `claim_ceiling` stays `DESIGN_ONLY`.

A first build leaked four `.pytest_cache` files into the archive (the author suite had been run inside
the tree). The adversarial diff against rc.2 caught it, the tree was cleaned, and the artifact rebuilt
with a new digest. That is why the published SHA is `f00c5792…` and not the earlier `d150977d…`.
