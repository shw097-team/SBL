#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WP-FHS-15 distinctness / completeness checker.

Three assertions, all fail-closed:

 1. Pairwise similarity of the three SPEC bodies stays at or below 0.85.
    Two independent measures are computed and BOTH must pass:
      a) sentence-shingle Jaccard (k=2, i.e. pairs of consecutive sentences)
      b) character 5-gram Jaccard over the normalised body
    A copy that only renames headings scores ~0.9+ on (b); genuinely different
    prose lands far lower.

 2. The consumer sets of the three SPECs are pairwise disjoint.
 3. The NEG firstfail-code sets of the three SPECs are pairwise disjoint.

It also asserts the 16 required fields are present and non-empty, that the FUO
table has all ten columns, and that acceptance entries carry the six keys.

Exit codes: 0 = all assertions pass, 1 = any assertion fails.

Usage: python tools/spec_distinctness.py [--root <evidence/WP15>] [--threshold 0.85]
"""
import argparse
import itertools
import json
import os
import re
import sys
import unicodedata

FIELDS = ["artifact_id", "version", "goal", "subject_ref", "source_refs", "scope",
          "persona_or_owner", "jtbd", "fuo", "non_goals", "assumptions", "decisions",
          "acceptance", "open_questions", "affected_holds", "original_reader",
          "claim_ceiling"]
TEN = ["who", "trigger", "input", "operation", "output", "observable proof",
       "consumer", "first_fail", "stop_rule", "resume_predicate"]
ACC_KEYS = ["id", "kind", "statement", "oracle", "consumer", "firstfail_code"]
NAMES = ["product", "architecture", "program"]

PUNCT = set("。，、；：！？「」『』（）〈〉《》—…·|#>*`-– \t\r\n\"'()[]{}.,;:!?/\\+=")


def norm(text):
    text = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in text if ch not in PUNCT).lower()


def sentences(text):
    raw = re.split(r"[。！？；\n]+", unicodedata.normalize("NFKC", text))
    out = []
    for s in raw:
        n = norm(s)
        if len(n) >= 8:
            out.append(n)
    return out


def shingles(seq, k):
    if len(seq) < k:
        return set(seq)
    return {tuple(seq[i:i + k]) for i in range(len(seq) - k + 1)}


def grams(text, k=5):
    n = norm(text)
    if len(n) < k:
        return {n}
    return {n[i:i + k] for i in range(len(n) - k + 1)}


def jacc(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def body_of(root, name):
    p = os.path.join(root, "specs", "%s_SPEC.md" % name)
    with open(p, encoding="utf-8") as fh:
        return fh.read()


def load(root, name):
    p = os.path.join(root, "specs", "%s_SPEC.json" % name)
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def ckey(x):
    """Normalise a consumer string so formatting variants collapse."""
    x = unicodedata.normalize("NFKC", x)
    x = re.sub(r"[（(][^）)]*[）)]", "", x)          # drop parentheticals
    x = re.sub(r"[\s\u3000]+", "", x)
    return "".join(ch for ch in x if ch not in PUNCT)


def consumers(spec):
    s = {spec["fuo"]["columns"]["consumer"], spec["original_reader"]["reader"]}
    for a in spec["acceptance"]:
        s.add(a["consumer"])
    return {ckey(x) for x in s}


def negcodes(spec):
    return {a["firstfail_code"] for a in spec["acceptance"] if a["kind"] == "NEG"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=None)
    ap.add_argument("--threshold", type=float, default=0.85)
    a = ap.parse_args()
    root = a.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    specs = {n: load(root, n) for n in NAMES}
    bodies = {n: body_of(root, n) for n in NAMES}
    fails = []

    print("== 1. field completeness ==")
    for n in NAMES:
        s = specs[n]
        missing = [f for f in FIELDS if f not in s or s[f] in (None, "", [], {})]
        cols = s["fuo"]["columns"]
        miss_cols = [c for c in TEN if not str(cols.get(c, "")).strip()]
        bad_acc = [x.get("id") for x in s["acceptance"]
                   if any(k not in x for k in ACC_KEYS) or x.get("kind") not in ("POS", "NEG")]
        kinds = [x["kind"] for x in s["acceptance"]]
        status = "PASS" if not (missing or miss_cols or bad_acc) else "FAIL"
        if status == "FAIL":
            fails.append("%s completeness" % n)
        print("%-14s %s  fields=%d/%d missing=%s  fuo_cols=%d/10 missing=%s  "
              "acc=%d (POS=%d NEG=%d) bad_acc=%s"
              % (n, status, len(FIELDS) - len(missing), len(FIELDS), missing or "-",
                 len(TEN) - len(miss_cols), miss_cols or "-", len(s["acceptance"]),
                 kinds.count("POS"), kinds.count("NEG"), bad_acc or "-"))

    print("\n== 2. pairwise body similarity (threshold %.2f) ==" % a.threshold)
    rows = []
    for x, y in itertools.combinations(NAMES, 2):
        s1 = shingles(sentences(bodies[x]), 2)
        s2 = shingles(sentences(bodies[y]), 2)
        sent = jacc(s1, s2)
        g1, g2 = grams(bodies[x]), grams(bodies[y])
        ch = jacc(g1, g2)
        worst = max(sent, ch)
        status = "PASS" if worst <= a.threshold else "FAIL"
        if status == "FAIL":
            fails.append("similarity %s/%s %.3f" % (x, y, worst))
        rows.append({"pair": [x, y], "sentence_shingle_jaccard": round(sent, 6),
                     "char5gram_jaccard": round(ch, 6), "max": round(worst, 6),
                     "status": status})
        print("%-24s sentence_shingle(2g)=%.4f  char_5gram=%.4f  max=%.4f  %s"
              % ("%s vs %s" % (x, y), sent, ch, worst, status))

    print("\n== 3. disjoint consumer / NEG sets ==")
    cons = {n: consumers(specs[n]) for n in NAMES}
    negs = {n: negcodes(specs[n]) for n in NAMES}
    for n in NAMES:
        print("%-14s consumers=%d %s" % (n, len(cons[n]), sorted(cons[n])))
        print("%-14s NEG codes=%d %s" % (n, len(negs[n]), sorted(negs[n])))
    for x, y in itertools.combinations(NAMES, 2):
        ic, ineg = cons[x] & cons[y], negs[x] & negs[y]
        st = "PASS" if not ic and not ineg else "FAIL"
        if st == "FAIL":
            fails.append("set overlap %s/%s cons=%s neg=%s" % (x, y, ic, ineg))
        print("disjoint %-22s consumers=%s NEG=%s  %s"
              % ("%s / %s" % (x, y), sorted(ic) or "∅", sorted(ineg) or "∅", st))

    print("\n== 4. body sizes (bytes) ==")
    for n in NAMES:
        b = len(bodies[n].encode("utf-8"))
        print("%-14s %6d bytes  %5d chars" % (n, b, len(bodies[n])))

    print("-" * 100)
    print("RESULT %s  (threshold %.2f, pairs=%d)" % ("PASS" if not fails else "FAIL",
                                                     a.threshold, len(rows)))
    if fails:
        for f in fails:
            print("  fail:", f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
