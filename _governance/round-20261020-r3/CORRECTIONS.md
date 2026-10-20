# Corrections — two digest defects this round introduced and fixed

Both defects are the same root cause seen from two angles: **this Windows checkout stores CRLF in the
working tree while the repository stores LF**, so anything hashed from the filesystem carries bytes the
repository does not contain. A reviewer cloning on Linux would compute a different digest and conclude
the evidence was tampered with.

## 1. `ROUND_MANIFEST.json` v1/v2 listed files that were not published, and hashed the wrong bytes

- v1 was built with `os.walk`. `.gitignore` excludes `dist/` and `*.whl`, so the manifest listed the wheel
  and sdist as if they were committed. They were not. `DISTRIBUTION_NOTE.md` records the correct
  location (release assets) and `ROUND_MANIFEST.json` schema `/2` dropped them.
- `/2` still hashed the working tree, so every entry was a CRLF digest (e.g. `00_NORTH_STAR.md`: 2915 B /
  `08d3bda4…` on disk vs 2874 B / `a376bd12…` in the blob).
- `/3` hashes **repository blob content**: a verifier can reproduce every digest with
  `git show <rev>:<path> | sha256sum` on any platform. If your clone and the manifest disagree, check
  `core.autocrlf` before suspecting the evidence.

## 2. The signed acceptance quotes a working-copy digest for its raw receipt

`evidence/human/HUMAN_ACCEPTANCE_2026-10-20.json` records
`raw_receipts.sha256 = b28337e2da2266a7a0f1c1e2b0f96fac56aa99f4c2abd540caf892d1f5974de3`
for `M4LITE/receipts/M4LITE_RAW.json`. That is the **CRLF working-copy** digest (15413 B). The
repository blob is `be2125a8a8d7aadf…` (14993 B) and is identical apart from line endings.

The signed file is left exactly as signed — rewriting a receipt after signature would destroy the only
property that makes it worth anything. The portable digest is recorded here instead, and the receipt can
be re-derived at any time:

```
git show <evidence-rev>:_governance/round-20261020-r3/M4LITE/receipts/M4LITE_RAW.json | sha256sum
# be2125a8… (the content is byte-identical to what was reviewed; only the EOL differs)
```

The same applies to `AC_R2_RECEIPT.json`: disk `0e6361f1…` (22256 B) vs blob `1a52a07c…` (22009 B).

## 3. Open item, not silently patched

`TT-R3-EOL`: the repository has no `.gitattributes`, so `core.autocrlf=true` on a Windows host rewrites
every text file on checkout and makes cross-platform digests unstable. The fix is one file
(`* text=auto eol=lf` for text formats), but it changes `main`, which needs its own candidate and PR under
the same rules as any other product change. It is recorded here rather than applied inside an evidence
round.

**Rule extracted:** hash blobs, not files. A manifest is a statement about the repository, so it must be
built from `git ls-files` + `git cat-file`, never from `os.walk` + `open()`.
