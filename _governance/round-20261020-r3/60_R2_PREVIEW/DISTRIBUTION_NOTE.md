# Distribution note — where the preview artefacts actually live

The two build outputs are **not** committed to git. `.gitignore` excludes `dist/` and `*.whl`, which is
deliberate: a binary in a git history cannot be re-verified as cheaply as a release asset, and it would put
a build output in the same tree as the source it was built from.

They are published as release assets instead:

| File | Bytes | SHA-256 | Release | Asset id |
|---|---|---|---|---|
| `sbl_v01-0.1.0-py3-none-any.whl` | 27181 | `95e57c44614d9480673ebd7834293beda0dab3bb5e0c8851d5a6dd4460cd7c50` | `v0.1.0-foundation-preview` | 659583499 |
| `sbl_v01-0.1.0.tar.gz` | 36278 | `5babefeb0aee7eaeade692ef8bdeee85ab2e0021ed044c31819fdde3215bf15d` | `v0.1.0-foundation-preview` | 659583554 |

GitHub reports its own `sha256:` digest for each uploaded asset, and both match the digests computed
locally before upload. That agreement is the readback: it is not a claim that the bytes are correct, only
that the bytes you download are the bytes that were tested.

## Correction recorded here rather than hidden

The first version of `ROUND_MANIFEST.json` was computed with `os.walk` over the working tree, so it listed
the gitignored `dist/` files as if they were published. They were not in the commit, which means the
manifest described a tree that did not exist on the remote. The manifest now derives from `git ls-files`
(manifest schema `/2`) and names the two external artefacts separately. Lesson: a manifest built from the
filesystem will always eventually describe files the repository does not have.

## Rebuild instead of trusting these numbers

```
git clone https://github.com/shw097-team/SBL && cd SBL
git checkout bedc11957d4fc2474b249b69d200829272c118ef
python <evidence-branch>/_governance/round-20261020-r3/60_R2_PREVIEW/run_r2.py
```

`run_r2.py` exports the commit with `git archive`, builds in a scratch directory, installs into a fresh
3.11 venv with `--no-index`, runs the CLI across process boundaries, uninstalls and scans for residue.
Wheel bytes are not promised to be bit-identical across setuptools versions; the sha256 above identifies
*this* build, and the receipt identifies what was verified.
