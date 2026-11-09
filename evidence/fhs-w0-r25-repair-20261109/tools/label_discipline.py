"""Refuse a bare ORIGINAL_ACK claim — in prose **and** in machine-readable metadata.

`FHS_ORIGINAL_ACK` and the traditional `ORIGINAL_ACK` have different evidence bases: one is granted to a
role instantiated as lanes and is backed by spans, negatives and a disagreement register; the other requires
the original domain's reader. If the qualifier can be dropped without anything failing, the label decays
into a false statement within one round of retelling.

r20 repair (VERIFY R19 blocking defect 2): the first version of this tool only looked at the markdown and
at three JSON *keys* (`label|kind|claim`). A JSON consumer never sees the markdown, and it reads
`body.kind = "original_reader_ack"` and a prose `consequence` field just as readily. So the rule now walks
every string value of every author-produced machine-readable artefact and requires the `FHS_` qualifier on
each occurrence of the token, unless the string itself carries a negative marker or sits under a declared
negative/verbatim key.

Scan scope (declared, printed in the output, not inferred):
    out/*.json            the round's own assertions
    receipts/**/*.json    every receipt the round issues
    evidence/*.json       payload evidence
Excluded by name, with a reason, and printed as `excluded`:
    out/stage/**          a rebuildable copy of the files above; scanning it would double-count, not widen
    lanes/**, officer/**  other lanes' verbatim verdicts, which the author may quote but must not relabel
"""
import glob as _g
import hashlib
import json
import os
import re
import sys

ROUND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Two classes, because one list is how the bypass happened. An independent lane measured that
# "Traditional per-domain ORIGINAL_ACK 6/6 was obtained." passed G28: `traditional` was a negative marker,
# so the affirmative sentence that contains it was exempt. A word that can appear inside a claim may only
# exempt a string that asserts nothing positive.
# STRONG markers make the string non-assertive by themselves: a negation, a count of zero, a quotation,
# a hypothetical, or a deprecated-construct description. WEAK markers are words that also occur inside a
# real claim ("traditional", "bare"), so they exempt only a string that asserts nothing.
# r21 lane finding (third iteration on the same rule): a marker ANYWHERE in the string exempted the whole
# string, so "Traditional per-domain ORIGINAL_ACK 6/6 was obtained; examples follow." passed because
# `example` appeared later in the sentence. Markers are therefore clause-scoped: a marker exempts only the
# clause it sits in, and a positive assertion beats a weak marker in the same clause.
NEGATIVE_STRONG = ("NOT_CLAIMED", "not claimed", "不主張", "未取得", "不表示", "不得簡寫", "不可互換",
                   "不是", "並未", "並非", "not_claim", "cannot", "refused", "untouched", "never issued",
                   "0/6", "0 項", "原文", "引述", "quoted", "不建立", "一旦", "若要", "簡寫成", "改標成", "unless", "must carry",
                   "DEPRECATED", "HIST-0", "不採用", "歷史規劃")
NEGATIVE_WEAK = ("traditional", "傳統", "bare", "裸稱", "synthetic", "example")
# ASCII-safe boundaries: an earlier version wrote \b through a shell heredoc and the tool ended up holding a
# literal U+0008, so `obtained` stopped matching at all. Character classes are unambiguous.
POSITIVE = re.compile(r"([1-9]\s*/\s*6)|(?<![A-Za-z])(obtained|granted|issued)(?![A-Za-z])|已?取得", re.I)
SENT_SPLIT = re.compile(r"[。；;！?\n]")
CLAUSE_SPLIT = re.compile(r"[，,、]")


def _clause_at(text: str, pos: int) -> str:
    lo = 0
    hi = len(text)
    for m in SENT_SPLIT.finditer(text):
        if m.end() <= pos:
            lo = m.end()
        elif m.start() > pos:
            hi = m.start()
            break
    sent = text[lo:hi]
    base = lo
    clo, chi = base, hi
    for m in CLAUSE_SPLIT.finditer(sent):
        if base + m.end() <= pos:
            clo = base + m.end()
        elif base + m.start() > pos:
            chi = base + m.start()
            break
    return text[clo:chi]


def token_violations(text: str) -> list[tuple[int, str]]:
    """(offset, clause) for every token that is neither qualified, renamed, nor negated in its own clause."""
    bad = []
    for m in TOKEN.finditer(text):
        pre = text[max(0, m.start() - 5):m.start()].lower()
        if any(pre.endswith(q) for q in QUALIFIERS):
            continue
        clause = _clause_at(text, m.start())
        if RENAME.search(clause):
            continue
        low = clause.lower()
        if any(t.lower() in low for t in NEGATIVE_STRONG):
            continue
        if POSITIVE.search(clause):
            bad.append((m.start(), clause))
            continue
        if any(t.lower() in low for t in NEGATIVE_WEAK):
            continue
        bad.append((m.start(), clause))
    return bad


SKIP_KEYS = {"not_claimed", "not_claiming", "does_not_claim", "denied", "excluded", "non_claims", "non_claim", "still_open", "open_items", "blocked_on",
             "not_claimed_here", "claim_ceiling_exclusions"}
VERBATIM_KEYS = {"verbatim", "quote", "quoted", "owner_order_verbatim", "reader_verbatim"}
SKIP_TOPDIRS = {"lanes", "officer"}   # other lanes' verdict prose: quoted, not relabelled
TOKEN = re.compile(r"original_(?:reader_)?ack", re.I)
# A rename record names BOTH sides with an explicit arrow. It is the only shape allowed to carry the bare
# token: the direction is unambiguous and the qualified form is present in the same clause.
RENAME = re.compile(r"original_(?:reader_)?ack\s*(?:->|=>|→)\s*fhs_original_(?:reader_)?ack", re.I)
QUALIFIERS = ("fhs_", "bare_")


def doc_path() -> str:
    d = os.path.join(ROUND, "writeback", "W0")
    best = None
    for fn in os.listdir(d) if os.path.isdir(d) else []:
        m = re.match(r"FHS_PIPD-LS-PKG_W0_r(\d+)\.md$", fn)
        if m and (best is None or int(m.group(1)) > best[0]):
            best = (int(m.group(1)), os.path.join(d, fn))
    return best[1] if best else os.path.join(d, "FHS_PIPD-LS-PKG_W0_r19.md")


DOC = doc_path()


def _negative(s: str) -> bool:
    low = s.lower()
    if any(t.lower() in low for t in NEGATIVE_STRONG):
        return True
    if POSITIVE.search(s):
        return False          # a weak marker never exempts an affirmative sentence
    return any(t.lower() in low for t in NEGATIVE_WEAK)


def scan(text: str) -> list[dict]:
    """Prose rule, unchanged in behaviour from r19 except that the token set is stated once.

    The document is append-only, so a rule that tightened retroactively would light up chapters nobody may
    edit. Prose therefore keeps the line-level marker test; the clause-level test lives in the machine path
    (`_walk`), which is where an independent lane produced both counterexamples.
    """
    bad = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r"ORIGINAL_ACK", line):
            s0 = max(0, m.start() - 12)
            if line[s0:m.start()].endswith("FHS_") or line[max(0, m.start() - 4):m.start()] == "FHS_":
                continue
            if _negative(line):
                continue
            if re.search(r"ORIGINAL_ACK[^\n]{0,40}?(0|無任何|沒有|未達|未取得|不可達|不可行|不能|不再|false)", line, re.I):
                continue
            bad.append({"line": i, "code": "BARE_ORIGINAL_ACK_CLAIM", "text": line[:160]})
    return bad


def _walk(obj, ptr: str, rel: str, out: list):
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in SKIP_KEYS or kl in VERBATIM_KEYS or kl.endswith("_verbatim"):
                continue                      # negative container or the owner's literal words
            _walk(v, f"{ptr}/{k}", rel, out)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk(v, f"{ptr}[{i}]", rel, out)
    elif isinstance(obj, str):
        hits = token_violations(obj)
        if hits:
            off, clause = hits[0]
            out.append({"file": rel, "pointer": ptr, "code": "BARE_ORIGINAL_ACK_IN_MACHINE_READABLE",
                        "value": clause.strip()[:120]})


def scan_json(root: str) -> tuple[list[dict], list[dict]]:
    """Every author-produced machine-readable artefact; returns (violations, exclusions-with-reason).

    The scan scope is itself an artefact (`out/SCAN_SCOPE.json`) when present, so a reader can see which
    files were in scope and, for every exclusion, the reason — instead of inferring it from glob patterns
    in code. A scope file that would exclude a receipt or the principal definition is refused below.
    """
    bad, excluded = [], []
    scope_file = os.path.join(root, "out", "SCAN_SCOPE.json")
    scope = None
    if os.path.isfile(scope_file):
        scope = json.loads(open(scope_file, encoding="utf-8").read())
        for row in scope.get("exclude") or []:
            excluded.append({"path": row["pattern"], "reason": row["reason"],
                             "json_files": len(_g.glob(os.path.join(root, row["pattern"]), recursive=True))})
    must_scan = ("receipts/**/*.json", "out/PRINCIPAL_DEFINITION.json", "out/FHS_ORIGINAL_ACK.json")
    for pat in must_scan:
        for row in (scope or {}).get("exclude") or []:
            if pat.startswith(row["pattern"].rstrip("*").rstrip("/")) or row["pattern"] == pat:
                bad.append({"file": "out/SCAN_SCOPE.json", "pointer": "/exclude",
                            "code": "SCOPE_EXCLUDES_A_MUST_SCAN_ARTEFACT",
                            "value": f"{row['pattern']} would hide {pat}"})
    files = []
    files += sorted(_g.glob(os.path.join(root, "out", "*.json")))
    files += sorted(_g.glob(os.path.join(root, "receipts", "**", "*.json"), recursive=True))
    files += sorted(_g.glob(os.path.join(root, "evidence", "*.json")))
    for d in (() if scope else ("out/stage", *sorted(SKIP_TOPDIRS))):
        if os.path.isdir(os.path.join(root, d)):
            n = len(_g.glob(os.path.join(root, d, "**", "*.json"), recursive=True))
            excluded.append({"path": d + "/**", "json_files": n,
                             "reason": ("a rebuildable copy of out/, receipts/, evidence/; scanning it "
                                        "double-counts rather than widening") if d == "out/stage"
                             else "another lane's verbatim verdict text; quoted by the author, never relabelled"})
    for f in files:
        rel = os.path.relpath(f, root).replace(os.sep, "/")
        if rel.startswith("out/stage/") or rel.split("/")[0] in SKIP_TOPDIRS:
            continue
        if scope and not any(_fnmatch(rel, p) for p in (scope.get("scan") or [])):
            continue
        try:
            obj = json.loads(open(f, encoding="utf-8", errors="replace").read())
        except ValueError as e:
            bad.append({"file": rel, "pointer": "", "code": "UNDECODABLE_JSON", "value": str(e)[:80]})
            continue
        _walk(obj, "", rel, bad)
    return bad, excluded


def _fnmatch(rel: str, pattern: str) -> bool:
    import fnmatch
    if fnmatch.fnmatch(rel, pattern):
        return True
    # 'out/*.json' must not match out/history/x.json
    return False


def scan_scope(root: str) -> dict:
    """The declared scope, as numbers: how many artefacts the rule actually read, and what it skipped."""
    rows = []
    rows += sorted(_g.glob(os.path.join(root, "out", "*.json")))
    rows += sorted(_g.glob(os.path.join(root, "receipts", "**", "*.json"), recursive=True))
    rows += sorted(_g.glob(os.path.join(root, "evidence", "*.json")))
    scope_file = os.path.join(root, "out", "SCAN_SCOPE.json")
    scope = json.loads(open(scope_file, encoding="utf-8").read()) if os.path.isfile(scope_file) else None
    kept = []
    for f in rows:
        rel = os.path.relpath(f, root).replace(os.sep, "/")
        if rel.startswith("out/stage/") or rel.split("/")[0] in SKIP_TOPDIRS:
            continue
        if scope and not any(_fnmatch(rel, p) for p in (scope.get("scan") or [])):
            continue
        kept.append(rel)
    return {"scanned_files": len(kept), "files": kept,
            "scope_file": "out/SCAN_SCOPE.json" if scope else None}


def main() -> int:
    text = open(DOC, encoding="utf-8", errors="replace").read()
    prose = scan(text)
    machine, excluded = scan_json(ROUND)
    bad = prose + machine
    if "--selftest" in sys.argv:
        clean = len(bad)
        # control 1: the markdown sentence the rule exists to refuse
        after = scan(text + "\n| 已取得 ORIGINAL_ACK 6/6 |\n")
        fired_md = len(after) > len(prose)
        # controls 2-4 run on in-memory objects: `--selftest` must work where there is no writable temp
        # directory at all (measured under `codex exec --sandbox read-only`), and a control that needs a
        # filesystem proves nothing about the rule.
        jb = []
        _walk({"body": {"kind": "original_reader_ack", "count": "6/6"}}, "", "probe.json", jb)
        fired_kind = bool(jb)
        jb2 = []
        _walk({"consequence": "ORIGINAL_ACK 6/6 may be issued by the reader role"}, "", "probe2.json", jb2)
        fired_prose = bool(jb2)
        jb3 = []
        _walk({"label": "FHS_ORIGINAL_ACK", "kind": "fhs_original_reader_ack",
               "not_claimed": ["ORIGINAL_ACK"], "order_verbatim": "改標成 ORIGINAL_ACK"}, "", "probe3.json", jb3)
        quiet_ok = not jb3
        jb4 = []
        _walk({"consequence": "Traditional per-domain ORIGINAL_ACK 6/6 was obtained."}, "", "probe4.json", jb4)
        fired_traditional = bool(jb4)
        fired = fired_md and fired_kind and fired_prose and quiet_ok and fired_traditional
        print(json.dumps({"schema": "FHS.W0.LabelDiscipline/2", "document": os.path.basename(DOC),
                          "baseline_violations": clean, "fired_markdown": fired_md,
                          "fired_machine_kind": fired_kind, "fired_machine_prose": fired_prose,
                          "qualified_control_silent": quiet_ok,
                          "fired_affirmative_traditional": fired_traditional, "FIRED": fired,
                          "excluded": excluded}, ensure_ascii=False, indent=1))
        for b in (prose + machine)[:3]:
            print(f"   {b}")
        return 0 if fired else 5
    print(json.dumps({"schema": "FHS.W0.LabelDiscipline/2",
                      "document": os.path.basename(DOC),
                      "sha256": hashlib.sha256(open(DOC, "rb").read()).hexdigest(),
                      "violations": bad, "count": len(bad),
                      "prose_count": len(prose), "machine_count": len(machine),
                      "scan_scope": ["out/*.json", "receipts/**/*.json", "evidence/*.json"],
                      "excluded": excluded,
                      "rule": "every ORIGINAL_ACK token must carry FHS_ unless the same string is negative, "
                              "sits under a not_claimed / *_verbatim key, or is an explicit rename record "
                              "(bare token -> fhs_ token, both sides named)"},
                     ensure_ascii=False, indent=1))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
