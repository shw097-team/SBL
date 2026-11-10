"""Signed-vote quorum: the predicate the r24 external challenge showed was missing.

r24's `verify_reader_ack.py` accepted a preservation decision whose `value` was a boolean, without asking how
many **valid, distinct, same-candidate** votes backed it. Two signed decisions had one agreeing vote and were
still marked `DECIDED`. This module is the predicate, its deterministic negative fixtures, and a scanner over
the signed receipts.

Rules (each one is a refusal with its own code):
    VALUE_NOT_BOOLEAN            the declared value is not a real bool (`1` is not `True`)
    STATE_NOT_DECIDED            a property that is not DECIDED cannot be counted as decided
    REREAD_EVIDENCE_MISSING      `resolved_by` is asserted without `reread_refs`
    LANE_ID_DUPLICATE            the same lane voted twice; only one vote per lane counts
    STALE_CANDIDATE_VOTE         a vote names a candidate other than the effective one
    SIGNED_VOTE_QUORUM_FAIL      fewer than `quorum_min` valid votes agree with the declared value

r27/L1 repair (external challenge 7.1 — three false greens). A repair vote — an entry of `votes_r25`, the
set that decides a repaired property — is countable ONLY when the whole binding is present, typed and
re-derived. Each shortfall is its own refusal:
    VOTE_TYPE_INVALID            `type(vote) is not bool` (JSON `1`, `"true"`, `1.0` are not votes)
    MISSING_CANDIDATE_BINDING    a required field of the vote is absent/empty, so the vote binds nothing
    PROCESS_IDENTITY_MISSING     `--strict` only: `session_id` / `process_id` absent (see R26-01_GAP)
    RAW_EVIDENCE_UNREADABLE      the vote's raw transcript cannot be resolved under `--raw-root`
    RAW_DIGEST_MISMATCH          the resolved transcript does not re-hash to the declared `raw_sha256`
    PROCESS_ID_DUPLICATE         two votes of one property carry the same (session_id, process_id)

Counting rules are kept separate from integrity rules: an integrity refusal vetoes the property on its own,
while a lane duplicate only removes a vote and lets the quorum arithmetic decide (so a duplicated lane whose
remaining votes still reach quorum is reported, not silently dropped).
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
import tempfile

QUORUM_MIN = 2

# the round this module is shipped inside; `evaluate()` called in-process (verify_reader_ack.py) resolves
# relative raw paths against it rather than against whatever cwd the caller happens to have
ROUND_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# R26-01: the binding a repair vote must carry to be countable at all.
REQUIRED_VOTE_FIELDS = ("lane_id", "candidate_sha256", "source_sha256", "clause_id", "property",
                        "raw_path", "raw_sha256", "timestamp")
# declared aliases, not silent fallbacks: the two signed r25 repairs spell these two fields `raw_file`
# and `at` (measured 4/4 votes), and both names are reported back under `field_sources`.
FIELD_ALIASES = {"raw_path": ("raw_path", "raw_file"), "timestamp": ("timestamp", "at")}
# measured 4/4 absent from the two signed repairs -> opt-in only, so the round's own signed repairs stay
# countable without editing them (finding R26-01_GAP)
STRICT_ONLY_FIELDS = ("session_id", "process_id")

INTEGRITY_CODES = ("MISSING_CANDIDATE_BINDING", "VOTE_TYPE_INVALID", "STALE_CANDIDATE_VOTE",
                   "RAW_EVIDENCE_UNREADABLE", "RAW_DIGEST_MISMATCH", "PROCESS_ID_DUPLICATE",
                   "PROCESS_IDENTITY_MISSING", "NO_LANE_IDENTITY")
COUNTING_CODES = ("LANE_ID_DUPLICATE",)


# --------------------------------------------------------------------------------------- field helpers
def _norm(p) -> str:
    return ("" if p is None else str(p)).replace("\\", "/").strip()


def _field(vote: dict, name: str):
    """(value, key) for a required field, honouring the declared alias table."""
    for key in FIELD_ALIASES.get(name, (name,)):
        if key in vote:
            val = vote[key]
            if isinstance(val, str):
                val = val.strip()
            if val not in (None, ""):
                return val, key
    return None, None


def _sha_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def _manifest_rows(raw_root: str) -> dict:
    """The round's own payload manifest, indexed by both the payload path and the measured-from path.

    It is the payload's declared binding between the copy it ships (`path`/`sha256`) and the digest that
    was measured where the transcript was written (`measured_from`/`sha256_as_measured`, `normalised`).
    A vote's `raw_sha256` may be either identity, so the anchor is read from here instead of guessing.
    """
    path = os.path.join(raw_root, "MANIFEST.json")
    try:
        with open(path, encoding="utf-8") as fh:
            man = json.loads(fh.read())
    except (OSError, ValueError):
        return {}
    rows = {}
    for row in man.get("files") or []:
        for key in ("measured_from", "path"):
            k = _norm(row.get(key))
            if k:
                rows.setdefault(k, row)
    return rows


def _bind_raw(vote: dict, raw_root: str, manifest: dict):
    """Re-derive the vote's raw-transcript binding. -> (ok, code, detail).

    Resolution is declared, not searched until something matches: `<raw-root>/<raw_path>` and then the
    payload copy `<raw-root>/votes/<basename>`. The digest must then equal the bytes on disk, or equal
    the manifest's `sha256_as_measured` while the payload copy still hashes to the manifest's `sha256`.
    """
    raw_path, raw_key = _field(vote, "raw_path")
    declared, raw_sha_key = _field(vote, "raw_sha256")
    if not raw_path or not declared:
        return False, "MISSING_CANDIDATE_BINDING", {"missing": ["raw_path" if not raw_path else "raw_sha256"]}
    declared = str(declared).strip().lower()
    base = os.path.basename(_norm(raw_path))
    tried = []
    for cand in (os.path.join(raw_root, _norm(raw_path)), os.path.join(raw_root, "votes", base)):
        cand = os.path.normpath(cand)
        if cand in tried:
            continue
        tried.append(cand)
        if os.path.isfile(cand) and _sha_file(cand) == declared:
            return True, None, {"form": "raw_bytes", "resolved": _rel(cand, raw_root),
                                "declared_digest": declared, "field_sources": {raw_key: _norm(raw_path),
                                                                               raw_sha_key: "raw_sha256"}}
    row = manifest.get(_norm(raw_path))
    if row and _norm(row.get("path")) and os.path.isfile(os.path.join(raw_root, _norm(row["path"]))):
        copy = os.path.join(raw_root, _norm(row["path"]))
        tried.append(os.path.normpath(copy))
        anchored = (_norm(row.get("sha256_as_measured")).lower() == declared
                    and _norm(row.get("sha256")).lower() == _sha_file(copy))
        detail = {"form": "manifest_as_measured", "resolved": _rel(copy, raw_root),
                  "measured_from": row.get("measured_from"), "declared_digest": declared,
                  "payload_digest": _norm(row.get("sha256"))}
        if anchored:
            return True, None, detail
        return False, "RAW_DIGEST_MISMATCH", detail
    if not any(os.path.isfile(t) for t in tried):
        return False, "RAW_EVIDENCE_UNREADABLE", {"tried": [_rel(t, raw_root) for t in tried],
                                                  "declared_digest": declared}
    return False, "RAW_DIGEST_MISMATCH", {"tried": [_rel(t, raw_root) for t in tried],
                                          "declared_digest": declared}


def _rel(path: str, root: str) -> str:
    try:
        return os.path.relpath(path, root).replace(os.sep, "/")
    except ValueError:
        return path


# --------------------------------------------------------------------------------------- vote readers
def _repair_votes(votes, effective_candidate, raw_root, strict):
    """`votes_r25`: the set that decides a repaired property. Nothing counts unless fully bound."""
    valid, dropped, integrity, bindings = {}, [], [], []
    if isinstance(votes, dict):
        # today the dict shape skipped the candidate check entirely; a lane->bool map cannot carry one
        for lane in votes:
            lane = str(lane or "").strip() or None
            item = {"lane": lane, "why": "MISSING_CANDIDATE_BINDING",
                    "missing": list(REQUIRED_VOTE_FIELDS)}
            dropped.append(item)
            integrity.append(item)
        return valid, dropped, integrity, bindings
    seen_process = {}
    for raw in votes or []:
        if not isinstance(raw, dict):
            item = {"lane": None, "why": "MISSING_CANDIDATE_BINDING",
                    "detail": "vote is not an object: " + type(raw).__name__}
            dropped.append(item)
            integrity.append(item)
            continue
        lane = str(_field(raw, "lane_id")[0] or "").strip() or None
        missing = [f for f in REQUIRED_VOTE_FIELDS if _field(raw, f)[0] in (None, "")]
        if missing:
            item = {"lane": lane, "why": "MISSING_CANDIDATE_BINDING", "missing": missing}
            dropped.append(item)
            integrity.append(item)
            continue
        if strict:
            gap = [f for f in STRICT_ONLY_FIELDS if _field(raw, f)[0] in (None, "")]
            if gap:
                item = {"lane": lane, "why": "PROCESS_IDENTITY_MISSING", "missing": gap}
                dropped.append(item)
                integrity.append(item)
                continue
        vote = raw.get("vote")
        if type(vote) is not bool:
            item = {"lane": lane, "why": "VOTE_TYPE_INVALID", "type": type(vote).__name__,
                    "value": vote if isinstance(vote, (int, float, str, bool)) else None}
            dropped.append(item)
            integrity.append(item)
            continue
        cand = str(_field(raw, "candidate_sha256")[0])
        if effective_candidate and cand != str(effective_candidate):
            item = {"lane": lane, "why": "STALE_CANDIDATE_VOTE", "vote_candidate": cand,
                    "effective_candidate": str(effective_candidate)}
            dropped.append(item)
            integrity.append(item)
            continue
        if lane is None:
            item = {"lane": None, "why": "NO_LANE_IDENTITY"}
            dropped.append(item)
            integrity.append(item)
            continue
        if lane in valid:
            dropped.append({"lane": lane, "why": "LANE_ID_DUPLICATE"})
            continue
        sess = _field(raw, "session_id")[0]
        proc = _field(raw, "process_id")[0]
        if sess not in (None, "") and proc not in (None, ""):
            key = (str(sess).strip(), str(proc).strip())
            if key in seen_process:
                item = {"lane": lane, "why": "PROCESS_ID_DUPLICATE", "process_id": key[1],
                        "session_id": key[0], "first_lane": seen_process[key]}
                dropped.append(item)
                integrity.append(item)
                continue
            seen_process[key] = lane
        ok, code, detail = _bind_raw(raw, raw_root, _manifest_rows(raw_root))
        if not ok:
            item = {"lane": lane, "why": code, **detail}
            dropped.append(item)
            integrity.append(item)
            continue
        bindings.append({"lane": lane, **detail})
        valid[lane] = vote
    return valid, dropped, integrity, bindings


def _legacy_votes(votes, effective_candidate):
    """The pre-repair `votes` shape, kept as history. Exact typing only: `1` is not a vote."""
    out, dropped = {}, []
    if isinstance(votes, dict):
        items = list(votes.items())
    else:
        items = [((v or {}).get("lane_id") or (v or {}).get("lane"), (v or {}).get("vote"))
                 for v in votes or [] if isinstance(v, dict)]
    for lane, vote in items:
        lane = str(lane or "").strip()
        if not lane:
            dropped.append({"lane": None, "why": "NO_LANE_IDENTITY"})
            continue
        if lane in out:
            dropped.append({"lane": lane, "why": "LANE_ID_DUPLICATE"})
            continue
        if vote == "UNKNOWN" or vote is None:
            continue                      # abstention: not a vote
        if type(vote) is not bool:
            dropped.append({"lane": lane, "why": "VOTE_TYPE_INVALID", "type": type(vote).__name__})
            continue
        out[lane] = vote
    # a structured vote list carries the candidate each lane read
    if not isinstance(votes, dict):
        stale = set()
        for v in votes or []:
            if not isinstance(v, dict):
                continue
            lane = str(v.get("lane_id") or v.get("lane") or "").strip()
            if v.get("candidate_sha256") and effective_candidate and v["candidate_sha256"] != effective_candidate:
                dropped.append({"lane": lane, "why": "STALE_CANDIDATE_VOTE"})
                stale.add(lane)
        for lane in stale:
            out.pop(lane, None)
    return out, dropped


# --------------------------------------------------------------------------------------------- decide
def evaluate(prop: dict, *, effective_candidate: str = None, quorum_min: int = QUORUM_MIN,
             raw_root: str = None, strict: bool = False) -> dict:
    """Decide one preservation property. Returns {verdict, first_fail, agreeing, dissenting, dropped}."""
    value = prop.get("value")
    if type(value) is not bool:
        return {"verdict": "HOLD", "first_fail": "VALUE_NOT_BOOLEAN", "agreeing": 0, "dissenting": 0,
                "dropped": [], "value_type": type(value).__name__}
    state = prop.get("state")
    if state != "DECIDED":
        return {"verdict": "HOLD", "first_fail": "STATE_NOT_DECIDED", "agreeing": 0, "dissenting": 0,
                "dropped": [], "state": state}
    if prop.get("resolved_by") and not (prop.get("reread_refs") or prop.get("repaired_readback_refs")):
        return {"verdict": "HOLD", "first_fail": "REREAD_EVIDENCE_MISSING", "agreeing": 0, "dissenting": 0,
                "dropped": [], "resolved_by": prop.get("resolved_by")}
    # a repaired property carries the re-read votes in `votes_r25`; those are the ones that count, and the
    # pre-repair `votes` stay beside them as history rather than being overwritten
    repair = bool(prop.get("votes_r25"))
    source = prop.get("votes_r25") if repair else prop.get("votes")
    if repair:
        valid, dropped, integrity, bindings = _repair_votes(source, effective_candidate,
                                                           raw_root or ROUND_ROOT, strict)
    else:
        valid, dropped = _legacy_votes(source, effective_candidate)
        integrity, bindings = [], []
    agreeing = sum(1 for v in valid.values() if v is value)
    dissenting = sum(1 for v in valid.values() if v is not value)
    out = {"agreeing": agreeing, "dissenting": dissenting, "valid_lanes": sorted(valid), "dropped": dropped,
           "vote_source": "votes_r25" if repair else "votes"}
    if bindings:
        out["raw_bindings"] = bindings
    if integrity:
        # the first offending vote of the transcribing order names the refusal; nothing below it can be
        # counted, so the quorum arithmetic is reported for context but does not decide
        veto = next((d["why"] for d in integrity if d["why"] in INTEGRITY_CODES), integrity[0]["why"])
        return {"verdict": "HOLD", "first_fail": veto, **out}
    if agreeing < quorum_min:
        return {"verdict": "HOLD", "first_fail": "SIGNED_VOTE_QUORUM_FAIL", **out}
    return {"verdict": "ACCEPTABLE_FOR_FHS_READER_SCOPE", "first_fail": None, **out}


def scan_receipts(root: str, raw_root: str = None, strict: bool = False) -> dict:
    """Every property of every signed reader receipt, evaluated. Fail-closed on an unreadable receipt."""
    findings, checked = [], 0
    repair_props = legacy_props = 0
    raw_root = raw_root or root
    files = sorted(glob.glob(os.path.join(root, "receipts", "**", "*.signed.json"), recursive=True))
    for f in files:
        rel = os.path.relpath(f, root).replace(os.sep, "/")
        try:
            with open(f, encoding="utf-8") as fh:
                env = json.loads(fh.read())
        except ValueError as e:
            findings.append({"file": rel, "first_fail": "RECEIPT_UNDECODABLE", "detail": str(e)[:120]})
            continue
        body = env.get("body") or {}
        # the candidate the re-read votes were cast on; when a round re-reads a later, prefix-compatible
        # revision the receipt names it here instead of pretending the older binding was what was read
        cand = (body.get("quorum_candidate_sha256")
                or (body.get("binding") or {}).get("candidate_sha256") or body.get("CandidateSHA"))
        for c in body.get("clauses") or []:
            for prop_name, prop in (c.get("preservation") or {}).items():
                checked += 1
                if (prop or {}).get("votes_r25"):
                    repair_props += 1
                else:
                    legacy_props += 1
                r = evaluate(prop, effective_candidate=cand, raw_root=raw_root, strict=strict)
                if r["verdict"] != "ACCEPTABLE_FOR_FHS_READER_SCOPE":
                    findings.append({"file": rel, "wp": body.get("Subject"), "clause_id": c.get("clause_id"),
                                     "property": prop_name, **r})
    return {"receipts": len(files), "properties_checked": checked,
            "repair_properties": repair_props, "legacy_properties": legacy_props,
            "raw_root": os.path.abspath(raw_root), "strict": strict,
            "findings": findings, "ok": not findings}


# -------------------------------------------------------------------------------------------- fixtures
_RAW_BYTES = b"FHS r25 transcript\r\nlane: PLAN\r\nvote: true\r\n"
_RAW_SHA = hashlib.sha256(_RAW_BYTES).hexdigest()
# the payload copy is a different rendering of the same transcript (the real r25 pair is exactly this
# shape: measured 17735 B at `lanes/votes/`, 17661 B at `votes/`, only 74 B apart across 167 lines, so it
# is NOT a line-ending twin). The manifest carries the two declared identities.
_COPY_BYTES = b"FHS r25 transcript (normalised copy)\nlane: PLAN\nvote: true\n"
_COPY_SHA = hashlib.sha256(_COPY_BYTES).hexdigest()
_AS_BYTES = b"FHS r25 transcript\r\nlane: PLAN\r\nvote: true\r\n[trailing as-measured tail]\r\n"
_AS_SHA = hashlib.sha256(_AS_BYTES).hexdigest()
_DRIFT_BYTES = b"FHS r25 transcript (drifted after signing)\n"
_FABRICATED = "00" * 32


def _rv(**over):
    """A fully bound repair vote; `over` perturbs exactly one field per fixture."""
    v = {"lane_id": "PLAN", "vote": True, "candidate_sha256": "cand-eff", "source_sha256": "src-1",
         "clause_id": "WP-FX:L1:1", "property": "scope_preserved",
         "raw_file": "lanes/votes/raw_fixture_r25.txt", "raw_sha256": _RAW_SHA,
         "timestamp": "2026-11-09T18:32:59+08:00"}
    v.update(over)
    return v


def _fixture(value, state, votes, **kw):
    p = {"value": value, "state": state, "votes": votes}
    p.update(kw)
    return p


def _repair_fixture(value, votes, raw_root="@TMP@", **kw):
    p = {"value": value, "state": "DECIDED", "votes_r25": votes, "votes": {"A": True, "B": True},
         "_raw_root": raw_root}
    p.update(kw)
    return p


CASES = [
    # (id, property, expected first_fail)
    ("NEG-Q1", _fixture(True, "DECIDED", {"A": "UNKNOWN", "B": "UNKNOWN", "T": True}), "SIGNED_VOTE_QUORUM_FAIL"),
    ("NEG-Q2", _fixture(True, "DECIDED", {"A": "UNKNOWN", "B": True, "T": False}), "SIGNED_VOTE_QUORUM_FAIL"),
    ("POS-Q3", _fixture(True, "DECIDED", {"A": True, "B": True, "T": False}), None),
    ("NEG-Q4", _fixture(True, "DECIDED", {"A": True, "A ": True}), "SIGNED_VOTE_QUORUM_FAIL"),
    ("NEG-Q7", _fixture(True, "DECIDED", {"A": True, "B": True}, resolved_by="POST_REPAIR_REREAD"),
     "REREAD_EVIDENCE_MISSING"),
    ("NEG-Q1b", _fixture(True, "HOLD", {"A": True, "B": True}), "STATE_NOT_DECIDED"),
    ("NEG-Q5", _fixture(True, "DECIDED", [{"lane": "A", "vote": True, "candidate_sha256": "old"},
                                          {"lane": "B", "vote": True, "candidate_sha256": "new"}]),
     "SIGNED_VOTE_QUORUM_FAIL"),
    # --- r27/L1: the three false-green classes, each as its own executed refusal -------------------
    ("NEG-Q8", _repair_fixture(True, {"A": True, "B": True}), "MISSING_CANDIDATE_BINDING"),
    ("NEG-Q9", _repair_fixture(True, [_rv(lane_id="PLAN", raw_sha256=_FABRICATED),
                                      _rv(lane_id="VERIFY", raw_sha256=_FABRICATED)]), "RAW_DIGEST_MISMATCH"),
    ("NEG-Q10", _repair_fixture(True, [_rv(lane_id="PLAN", vote=1), _rv(lane_id="VERIFY", vote=1)]),
     "VOTE_TYPE_INVALID"),
    ("NEG-Q11", _repair_fixture(True, [_rv(lane_id="PLAN", session_id="s1", process_id="p1"),
                                       _rv(lane_id="VERIFY", session_id="s1", process_id="p1")]),
     "PROCESS_ID_DUPLICATE"),
    ("NEG-Q13", _repair_fixture(True, [_rv(lane_id="PLAN", raw_file="lanes/votes/absent_r25.txt"),
                                       _rv(lane_id="VERIFY", raw_file="lanes/votes/absent_r25.txt")]),
     "RAW_EVIDENCE_UNREADABLE"),
    ("NEG-Q15", _repair_fixture(True, [_rv(lane_id="PLAN", vote="true"),
                                       _rv(lane_id="VERIFY", vote="true")]), "VOTE_TYPE_INVALID"),
    ("NEG-Q16", _repair_fixture(True, [_rv(lane_id="PLAN", candidate_sha256="cand-old"),
                                       _rv(lane_id="VERIFY", candidate_sha256="cand-old")]),
     "STALE_CANDIDATE_VOTE"),
    # --- positive control: a vote bound to the manifest's as-measured identity is still countable ---
    ("POS-Q12", _repair_fixture(True, [_rv(lane_id="PLAN", raw_file="lanes/votes/raw_copy_r25.txt",
                                          raw_sha256=_AS_SHA),
                                       _rv(lane_id="VERIFY", raw_file="lanes/votes/raw_copy_r25.txt",
                                          raw_sha256=_AS_SHA)]), None),
    # --- and the anchor is fail-closed: a payload copy that drifted from its manifest row refuses ------
    ("NEG-Q17", _repair_fixture(True, [_rv(lane_id="PLAN", raw_file="lanes/votes/raw_copy_r25.txt",
                                          raw_sha256=_AS_SHA),
                                       _rv(lane_id="VERIFY", raw_file="lanes/votes/raw_copy_r25.txt",
                                          raw_sha256=_AS_SHA)]), "RAW_DIGEST_MISMATCH"),
    ("POS-Q14", _repair_fixture(True, [_rv(lane_id="PLAN"), _rv(lane_id="VERIFY")]), None),
]


def _manifest(declared_as_measured: str) -> dict:
    return {"schema": "FHS.W0.PayloadManifest/3", "files": [
        {"path": "votes/raw_copy_r25.txt", "sha256": _COPY_SHA, "bytes": len(_COPY_BYTES),
         "measured_from": "lanes/votes/raw_copy_r25.txt", "sha256_as_measured": declared_as_measured,
         "bytes_as_measured": len(_AS_BYTES), "normalised": True}]}


def _materialise(tmp: str) -> None:
    """Write the fixture round the CASES point at: raw bytes, a manifest-anchored copy, a drifted copy."""
    for cid, _prop, _want in CASES:
        base = os.path.join(tmp, cid, "votes")
        os.makedirs(base, exist_ok=True)
        if cid in ("POS-Q14", "NEG-Q9", "NEG-Q11"):
            with open(os.path.join(base, "raw_fixture_r25.txt"), "wb") as fh:
                fh.write(_RAW_BYTES)
        if cid == "POS-Q12":
            with open(os.path.join(base, "raw_copy_r25.txt"), "wb") as fh:
                fh.write(_COPY_BYTES)
            with open(os.path.join(tmp, cid, "MANIFEST.json"), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(_manifest(_AS_SHA), fh, ensure_ascii=False, indent=1)
        if cid == "NEG-Q17":
            # the copy drifted after signing: it matches neither the vote digest nor its manifest row
            with open(os.path.join(base, "raw_copy_r25.txt"), "wb") as fh:
                fh.write(_DRIFT_BYTES)
            with open(os.path.join(tmp, cid, "MANIFEST.json"), "w", encoding="utf-8", newline="\n") as fh:
                json.dump(_manifest(_AS_SHA), fh, ensure_ascii=False, indent=1)


def _run_case(cid: str, prop: dict, want: str, tmp: str, strict: bool = False) -> dict:
    rr = prop.get("_raw_root")
    rr = os.path.join(tmp, cid) if rr in (None, "@TMP@") else rr
    p = {k: v for k, v in prop.items() if k != "_raw_root"}
    r = evaluate(p, effective_candidate="cand-eff", raw_root=rr, strict=strict)
    got = r["first_fail"]
    return {"case": cid, "expected": want, "got": got, "verdict": r["verdict"],
            "agreeing": r.get("agreeing"), "dissenting": r.get("dissenting"),
            "first_drop": (r.get("dropped") or [None])[0], "ok": got == want}


def selftest(only: str = None, strict: bool = False) -> int:
    rows, bad = [], 0
    with tempfile.TemporaryDirectory(prefix="fhs-quorum-selftest-") as tmp:
        _materialise(tmp)
        for cid, prop, want in CASES:
            if only and cid != only:
                continue
            row = _run_case(cid, prop, want, tmp, strict=strict)
            bad += 0 if row["ok"] else 1
            rows.append(row)
    doc = {"schema": "FHS.W0.VoteQuorum/1", "cases": len(rows), "failed": bad, "strict": strict,
           "rows": rows, "SELFTEST": "OK" if bad == 0 else "FAIL"}
    print(json.dumps(doc, ensure_ascii=False, indent=1))
    return 0 if bad == 0 else 5


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROUND_ROOT)
    ap.add_argument("--raw-root", default=None,
                    help="root the votes' relative raw paths resolve against (default: --root)")
    ap.add_argument("--strict", action="store_true",
                    help="also require session_id/process_id on every repair vote (R26-01_GAP fields)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--case", default=None, help="run one selftest case by id")
    ap.add_argument("--json-out", default=None)
    a = ap.parse_args()
    if a.selftest or a.case:
        return selftest(only=a.case, strict=a.strict)
    rep = scan_receipts(a.root, raw_root=a.raw_root, strict=a.strict)
    rep["schema"] = "FHS.W0.VoteQuorumScan/1"
    text = json.dumps(rep, ensure_ascii=False, indent=1)
    if a.json_out:
        with open(a.json_out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")
    print(text)
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
