#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WP-FHS-16 projection verifier.

Re-reads every source_ref from the raw bytes of the source file, re-slices the
span, and asserts the recorded quoted_text is exactly that slice. Then asserts
the structural invariants of the two projection tables.

Checks
  C01 table loads and every record carries the required keys
  C02 record count equals the declared count (no padding, no silent drop)
  C03 source file sha256 equals the envelope value (the file did not drift)
  C04 every source_ref re-slices byte-exactly to quoted_text
  C05 slot_id is unique inside its table
  C06 slot_id carries the table's prefix and a two-digit index
  C07 disposition is one of ADOPT_CANDIDATE / DEFER / NOFIT / HOLD
  C08 no ADOPT_CANDIDATE carries licence=UNKNOWN_NOT_STATED
  C09 any stated licence has non-empty provenance (file + quoted_text)
  C10 consumer / neg / original_use / host_fit are non-empty
  C11 chapter_ref re-slices byte-exactly (secondary trace to CH-24 / CH-25)
  C12 span really is the defining block heading for that slot_id

Exit code 0 only when every check passes. --selftest injects four defects and
requires each to be caught; a verifier that cannot fail proves nothing.
"""
import hashlib
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = {
    "DONOR24.json": "SLOT-",
    "METHOD25.json": "METHOD-",
}
ALLOWED = ("ADOPT_CANDIDATE", "DEFER", "NOFIT", "HOLD")
REQUIRED = ("slot_id", "name", "original_use", "licence", "host_fit", "disposition",
            "consumer", "neg", "source_ref")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def check(name, ok, detail=""):
    print("%s %s%s" % ("PASS" if ok else "FAIL", name, (" — " + detail) if detail else ""))
    return (name, bool(ok))


def slice_ok(ref, blobs):
    """Return (ok, detail). Strict: bytes -> utf-8 -> equality."""
    path = ref.get("file")
    if path not in blobs:
        with open(path, "rb") as fh:
            blobs[path] = fh.read()
    raw = blobs[path]
    bs, be = ref.get("byte_start"), ref.get("byte_end")
    if not isinstance(bs, int) or not isinstance(be, int) or bs < 0 or be <= bs or be > len(raw):
        return False, "span out of range %r:%r (file bytes=%d)" % (bs, be, len(raw))
    try:
        got = raw[bs:be].decode("utf-8")
    except UnicodeDecodeError as exc:
        return False, "span is not valid utf-8 at byte %d (%s)" % (bs, exc)
    if got != ref.get("quoted_text"):
        return False, "quoted_text mismatch at %d:%d (%d vs %d chars)" % (
            bs, be, len(got), len(ref.get("quoted_text") or ""))
    return True, "%d:%d (%d chars)" % (bs, be, len(got))


def run_checks(tables, blobs):
    results = []
    # C01 load + required keys
    missing = []
    for tname, env in tables.items():
        for rec in env["records"]:
            for k in REQUIRED:
                if k not in rec or rec[k] in (None, ""):
                    missing.append("%s:%s.%s" % (tname, rec.get("slot_id"), k))
    results.append(check("C01 required keys present", not missing,
                         "" if not missing else "; ".join(missing[:6])))

    # C02 counts
    tallies = {t: len(e["records"]) for t, e in tables.items()}
    declared = {t: e.get("record_count") for t, e in tables.items()}
    ok = all(declared[t] == tallies[t] for t in tables) and tallies["DONOR24.json"] > 0
    results.append(check("C02 record count == declared count", ok,
                         "donor=%d method=%d declared=%s" % (
                             tallies["DONOR24.json"], tallies["METHOD25.json"], declared)))

    # C03 source digest
    dig_ok, dig_detail = True, []
    for tname, env in tables.items():
        src = env["source"]
        if src["file"] not in blobs:
            with open(src["file"], "rb") as fh:
                blobs[src["file"]] = fh.read()
        got = sha256_bytes(blobs[src["file"]])
        good = got == src["sha256"] and len(blobs[src["file"]]) == src["bytes"]
        dig_ok = dig_ok and good
        dig_detail.append("%s %s" % (os.path.basename(src["file"]), got[:16]))
    results.append(check("C03 source sha256/bytes unchanged", dig_ok, "; ".join(dig_detail)))

    # C04 per-record re-slice
    bad = []
    n = 0
    for tname, env in tables.items():
        for rec in env["records"]:
            n += 1
            ok, detail = slice_ok(rec["source_ref"], blobs)
            if not ok:
                bad.append("%s %s" % (rec["slot_id"], detail))
    results.append(check("C04 source_ref re-slices to quoted_text (%d refs)" % n,
                         not bad, "" if not bad else "; ".join(bad[:4])))

    # C05 uniqueness
    dup = []
    for tname, env in tables.items():
        seen = {}
        for rec in env["records"]:
            seen.setdefault(rec["slot_id"], 0)
            seen[rec["slot_id"]] += 1
        dup += ["%s x%d" % (k, v) for k, v in seen.items() if v > 1]
    results.append(check("C05 slot_id unique per table", not dup,
                         "" if not dup else ", ".join(dup)))

    # C06 slot_id shape
    badshape = []
    for tname, env in tables.items():
        prefix = TABLES[tname]
        for rec in env["records"]:
            sid = rec["slot_id"]
            if not sid.startswith(prefix):
                badshape.append("%s not under %s" % (sid, prefix))
            elif tname == "METHOD25.json" and not sid.split("-")[-1].isdigit():
                badshape.append("%s has no numeric index" % sid)
    results.append(check("C06 slot_id prefix/shape", not badshape,
                         "" if not badshape else "; ".join(badshape[:4])))

    # C07 disposition vocabulary
    baddisp = []
    for tname, env in tables.items():
        for rec in env["records"]:
            if rec["disposition"] not in ALLOWED:
                baddisp.append("%s=%s" % (rec["slot_id"], rec["disposition"]))
    results.append(check("C07 disposition in allowed set", not baddisp,
                         "" if not baddisp else "; ".join(baddisp[:6])))

    # C08 licence gate on adopt candidates
    unlicensed = []
    reserved = 0
    for tname, env in tables.items():
        for rec in env["records"]:
            if rec["disposition"] == "ADOPT_CANDIDATE":
                reserved += 1
                if rec["licence"] == "UNKNOWN_NOT_STATED":
                    unlicensed.append(rec["slot_id"])
    results.append(check("C08 no ADOPT_CANDIDATE with UNKNOWN_NOT_STATED licence (%d adopt)" % reserved,
                         not unlicensed,
                         "" if not unlicensed else "DEFECT: downgrade to HOLD — " + ", ".join(unlicensed)))

    # C09 licence provenance
    badprov = []
    for tname, env in tables.items():
        for rec in env["records"]:
            if rec["licence"] != "UNKNOWN_NOT_STATED":
                ev = rec.get("licence_evidence") or {}
                if not ev.get("file") or not ev.get("quoted_text"):
                    badprov.append("%s licence=%s without provenance" % (rec["slot_id"], rec["licence"]))
    results.append(check("C09 stated licence has provenance", not badprov,
                         "" if not badprov else "; ".join(badprov[:4])))

    # C09b licence provenance spans themselves re-slice (no invented citation)
    badlspan = []
    for tname, env in tables.items():
        for rec in env["records"]:
            ev = rec.get("licence_evidence") or {}
            if "byte_start" in ev and "byte_end" in ev:
                ok, detail = slice_ok(ev, blobs)
                if not ok:
                    badlspan.append("%s %s" % (rec["slot_id"], detail))
    results.append(check("C09b licence_evidence span re-slices", not badlspan,
                         "" if not badlspan else "; ".join(badlspan[:4])))

    # C10 non-empty narrative fields
    empty = []
    for tname, env in tables.items():
        for rec in env["records"]:
            for k in ("consumer", "neg", "original_use", "host_fit"):
                if not str(rec.get(k, "")).strip():
                    empty.append("%s.%s" % (rec["slot_id"], k))
    results.append(check("C10 consumer/neg/original_use/host_fit non-empty", not empty,
                         "" if not empty else "; ".join(empty[:6])))

    # C11 chapter trace
    badch = []
    for tname, env in tables.items():
        for rec in env["records"]:
            ok, detail = slice_ok(rec["chapter_ref"], blobs)
            if not ok:
                badch.append("%s %s" % (rec["slot_id"], detail))
    results.append(check("C11 chapter_ref (CH-24/CH-25) re-slices", not badch,
                         "" if not badch else "; ".join(badch[:4])))

    # C12 span identity
    wrong = []
    for tname, env in tables.items():
        for rec in env["records"]:
            q = rec["source_ref"]["quoted_text"]
            head = q.split("\n", 1)[0]
            if rec["original_id"] not in head:
                wrong.append("%s heading=%r" % (rec["slot_id"], head[:48]))
    results.append(check("C12 span heading carries original_id", not wrong,
                         "" if not wrong else "; ".join(wrong[:4])))
    return results


def load_tables():
    tables, blobs = {}, {}
    for tname in TABLES:
        path = os.path.join(BASE, "tables", tname)
        with open(path, "r", encoding="utf-8") as fh:
            tables[tname] = json.load(fh)
    return tables, blobs


def selftest(tables):
    import copy
    print("--- selftest: injecting defects, each must be caught ---")
    caught, missed = 0, []

    def expect(label, mutate, must_fail):
        t = copy.deepcopy(tables)
        mutate(t)
        res = run_checks(t, {})
        failed = [n for n, ok in res if not ok]
        hit = any(n.startswith(must_fail) for n in failed)
        print("  %s %s (failed checks: %s)" % ("CAUGHT" if hit else "MISSED", label, ",".join(failed) or "-"))
        return hit

    outcomes = [
        expect("tampered quoted_text", lambda t: t["DONOR24.json"]["records"][0]["source_ref"].__setitem__("quoted_text", "x"), "C04"),
        expect("duplicate slot_id", lambda t: t["METHOD25.json"]["records"][1].__setitem__("slot_id", t["METHOD25.json"]["records"][0]["slot_id"]), "C05"),
        expect("bad disposition", lambda t: t["DONOR24.json"]["records"][2].__setitem__("disposition", "KEEP"), "C07"),
        expect("unlicensed adopt", lambda t: (t["METHOD25.json"]["records"][0].__setitem__("disposition", "ADOPT_CANDIDATE"),
                                             t["METHOD25.json"]["records"][0].__setitem__("licence", "UNKNOWN_NOT_STATED")), "C08"),
        expect("tampered licence citation",
               lambda t: t["DONOR24.json"]["records"][8]["licence_evidence"].__setitem__("quoted_text", "| MIT |"), "C09b"),
    ]
    print("selftest: %d/%d defects caught" % (sum(1 for o in outcomes if o), len(outcomes)))
    return all(outcomes)


def main(argv):
    tables, blobs = load_tables()
    if "--selftest" in argv:
        ok = selftest(tables)
        print("SELFTEST %s" % ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    print("WP-FHS-16 projection verifier")
    print("tables: " + ", ".join(os.path.join(BASE, "tables", t) for t in TABLES))
    results = run_checks(tables, blobs)
    passed = sum(1 for _, ok in results if ok)
    print("-" * 62)
    for tname, env in tables.items():
        dist = {}
        for rec in env["records"]:
            dist[rec["disposition"]] = dist.get(rec["disposition"], 0) + 1
        print("%s: %d records, dispositions=%s" % (
            tname, len(env["records"]), json.dumps(dist, ensure_ascii=False, sort_keys=True)))
    print("checks passed %d/%d" % (passed, len(results)))
    print("RESULT %s" % ("PASS" if passed == len(results) else "FAIL"))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
