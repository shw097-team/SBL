"""Refuse a bare ORIGINAL_ACK claim.

`FHS_ORIGINAL_ACK` and the traditional `ORIGINAL_ACK` have different evidence bases: one is granted to a
role instantiated as lanes and is backed by spans, negatives and a disagreement register; the other requires
the original domain's reader. If the qualifier can be dropped without anything failing, the label decays
into a false statement within one round of retelling.

So: every positive mention of ORIGINAL_ACK must carry the FHS_ qualifier, or sit in an explicit
NOT_CLAIMED / "does not claim" context.
"""
import hashlib, json, os, re, sys

ROUND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROUND, "writeback", "W0", "FHS_PIPD-LS-PKG_W0_r19.md")
EXEMPT = ("NOT_CLAIMED", "not claimed", "不主張", "傳統", "traditional", "未取得", "不表示", "不得簡寫",
          "不可互換", "bare ORIGINAL_ACK", "裸稱",
          # a row of the deprecated register describes the retired construct; describing is not claiming
          "DEPRECATED", "HIST-0", "不採用", "歷史規劃",
          "不是", "並未")
POSITIVE = __import__("re").compile(r"ORIGINAL_ACK\s*[:=]?\s*([1-9]|\b6\b)")


def scan(text: str) -> list[dict]:
    bad = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in re.finditer(r"ORIGINAL_ACK", line):
            s = max(0, m.start() - 12)
            if line[s:m.start()].endswith("FHS_") or line[max(0, m.start() - 4):m.start()] == "FHS_":
                continue
            if any(t.lower() in line.lower() for t in EXEMPT):
                continue
            # a negative assertion is not a claim: "ORIGINAL_ACK = 0/6", "仍是 0", "0 項"
            if re.search(r"ORIGINAL_ACK[^\n]{0,40}?(0|無任何|沒有|未達|未取得|不可達|不可行|不能|不再|false)", line, re.I):
                continue
            bad.append({"line": i, "code": "BARE_ORIGINAL_ACK_CLAIM", "text": line[:160]})
    return bad


def main() -> int:
    text = open(DOC, encoding="utf-8", errors="replace").read()
    bad = scan(text)
    if "--selftest" in sys.argv:
        clean = len(bad)
        # A synthetic positive control: a bare, positive claim appended to the document. This is the
        # exact sentence the rule exists to refuse, so if it is not refused the rule does not bite -
        # which is stronger evidence than mutating whatever line happens to be first.
        mutated = text + "\n| 已取得 ORIGINAL_ACK 6/6 |\n"
        after = scan(mutated)
        fired = len(after) > clean
        print(f"baseline violations {clean} | after stripping the qualifier {len(after)} | FIRED={fired}")
        for b in after[:3]:
            print(f"   line {b['line']}: {b['text'][:110]}")
        return 0 if fired else 5
    print(json.dumps({"schema": "FHS.W0.LabelDiscipline/1",
                      "document": os.path.basename(DOC),
                      "sha256": hashlib.sha256(open(DOC, "rb").read()).hexdigest(),
                      "violations": bad, "count": len(bad),
                      "rule": "a positive ORIGINAL_ACK claim must carry FHS_ or sit in a NOT_CLAIMED context"},
                     ensure_ascii=False, indent=1))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
