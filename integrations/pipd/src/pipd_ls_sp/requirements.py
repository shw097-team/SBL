"""Clause-bound atomic requirement compiler (R-AUD-005 / CAP_ATOMIC_REQUIREMENT_COMPILER).

Requirements are compiled from SOURCE CLAUSES into distinct atoms - never from keyword axes. Each
atom carries a stable id, a source locator (file + clause id/span + child), an owner, an acceptance
cue, a distinct oracle, a distinct negative fixture and a polarity (MUST / MUST NOT). Compound
inputs (各有／分別／對應) expand into per-subject atoms; ambiguous compounds are REFUSED (a semantic
collapse must fail, never bucket); negations keep their clause scope; no-keyword requirements are
preserved; two different source clauses never merge.

File sources are authoritative UTF-8 text. A directory source explicitly binds the submitted goal
as an inline clause source. Offsets are Unicode character offsets. The trace describes
obligations, not fabricated execution/evidence verdicts.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .errors import IntakeInvalid, PiSemanticFail
from .util import canonical_json, sha256_text

STAGES = ('SRC', 'REQ/Child', 'SPEC', 'ACC', 'VER', 'EVD', 'DEL', 'GATE')
DISTRIBUTIVE = ('各有', '分別', '對應')
# D1 (R5 §4.2): the negation surface must cover the source-bound prohibition phrasings, not only the
# MUST-NOT baseline. A prohibition that is not recognised here silently becomes a MUST.
NEGATION = re.compile(r'(?i)\b(?:must not|shall not|should not|never|may not|is not allowed to)\b'
                      r'|不得|禁止|不可|不應|嚴禁|不准|不允許|不許可|請勿')
# D1c (R5 §4.2): an explicit positive obligation modal, used ONLY to detect a genuinely ambiguous
# negation scope. The lookarounds keep a negated modal ("不應該", "must not") from reading as a
# positive one, and bare 需/應 are deliberately excluded so "不得需要…" is not a false refusal.
POSITIVE_MODAL = re.compile(r'(?i)\b(?:must|shall|should|required|need to)\b(?!\s+not)'
                            r'|(?<!不)(?:必須|應該)')
# D2 (R5 §4.3): marks that ALWAYS end a clause. An ASCII period is handled separately because it is
# also the internal separator of domains, versions and decimals.
TERMINAL_PUNCT = '。；;\n!?！？'
FILLER_CHARS = re.compile(r'[\s。．.，,、；;：:！!？?…~〜—\-_*()\[\]{}「」『』"\']')
FILLER_TOKENS = re.compile(r'嗯+|啊+|哦+|噢+|喔+|呃+|嘛+|呢+|吧+|哈+|呀+|欸+|喂+|唉+|哎+')

# ADVISORY ONLY: profile-axis hints. This five-axis keyword map is NOT an authoritative route for
# atom creation - atoms come from clauses regardless of any keyword match (see AXIS note below).
AXIS_HINTS = [
    ("intent", r"(?i)(implement|build|實作|建置|開發|施工)"),
    ("knowledge", r"(?i)(knowledge|source|知識|來源|規格|spec)"),
    ("verification", r"(?i)(test|verify|accept|測試|驗收|驗證)"),
    ("release", r"(?i)(deliver|publish|release|交付|發佈|發布|公開)"),
    ("trust_boundary", r"(?i)(govern|admission|workorder|治理|准入|裁決)"),
]


def advisory_axis(statement: str) -> str:
    """Advisory profile-axis tag for one statement; never a gate on atom existence."""
    for axis, pattern in AXIS_HINTS:
        if re.search(pattern, statement):
            return axis
    return "intent"


def _is_clause_terminator(text: str, index: int) -> bool:
    """D2 (R5 §4.3): an ASCII period ends a clause only when it is NOT internal to a token.

    The pre-repair scanner treated `.` as an unconditional boundary, so `api.example.com` split into
    three meaningless atoms and `v1.2.3` into three more, and the requirement count stopped matching
    the source. A period flanked on BOTH sides by ASCII alphanumerics is internal (domain, version,
    decimal); anywhere else it is sentence-final and does end the clause.
    """
    previous = text[index - 1] if index > 0 else ''
    following = text[index + 1] if index + 1 < len(text) else ''
    if not (previous.isascii() and previous.isalnum()
            and following.isascii() and following.isalnum()):
        return True
    # Flanked by ASCII alphanumerics: a token separator (domain, version, decimal) UNLESS the next
    # character opens a new sentence. An uppercase ASCII letter after the period is a sentence start,
    # so `Do task A.Task B must run.` still ends its first clause even when no space is typed.
    return following.isupper()


def _parts(text: str):
    # Keep offsets in the original source, including repeated identical sentences.
    segment_start = 0
    for index, char in enumerate(text):
        ends_clause = char in TERMINAL_PUNCT or (char == '.' and _is_clause_terminator(text, index))
        if not ends_clause:
            continue
        raw = text[segment_start:index]
        clause = raw.strip()
        start = segment_start + (len(raw) - len(raw.lstrip()))
        end = start + len(clause)
        if clause:
            yield start, end, clause
        segment_start = index + 1
    raw = text[segment_start:]
    clause = raw.strip()
    start = segment_start + (len(raw) - len(raw.lstrip()))
    end = start + len(clause)
    if clause:
        yield start, end, clause


def _split_subjects(text: str) -> list[str]:
    return [s.strip() for s in re.split(r'、|與|和|及', text) if s.strip()]


def _expand(clause: str) -> list[tuple[str, bool]]:
    """Expand one clause into (statement, negation-inherited) obligation statements.

    Distributive grammar (各有／分別／對應) binds subjects to predicates explicitly; when the binding
    is ambiguous the compound is REFUSED - a silent collapse into one atom is the R-AUD-005 defect.
    A distributive expansion shares one negation scope, so the negation distributes to every child.
    """
    distributive = re.search(r'各有|分別|對應', clause)
    if distributive:
        left, right = clause[:distributive.start()], clause[distributive.end():]
        right = re.sub(r'^(?:分別|對應|各有)+', '', right).strip()
        subjects = _split_subjects(left)
        if len(subjects) < 2 or not right:
            raise IntakeInvalid('ambiguous compound: explicit subjects and predicates required')
        negated = bool(NEGATION.search(clause))
        if distributive.group() == '各有':
            return [(s + '有' + right, negated) for s in subjects]
        predicates = [p.strip() for p in re.split(r'、|與|和|及', right) if p.strip()]
        marker = distributive.group()
        if len(predicates) == len(subjects):
            pairs = zip(subjects, predicates)
        elif len(predicates) == 1:
            pairs = [(s, predicates[0]) for s in subjects]
        elif len(subjects) == 1:
            pairs = [(subjects[0], p) for p in predicates]
        else:
            raise IntakeInvalid('ambiguous compound: subject/predicate cardinality differs')
        return [(s + marker + p, negated) for s, p in pairs]
    # Punctuation/conjunction boundaries delimit independent obligations (own negation scope).
    segments = [s.strip() for s in re.split(r'，|,|以及|\band\b', clause) if s.strip()]
    negation = NEGATION.search(clause)
    if not negation:
        segments = [s.strip() for seg in segments
                    for s in re.split(r'與|和|及', seg) if s.strip()]
        return [(s, False) for s in segments]
    if len(segments) <= 1:
        # One clause-level negation and a positive modal with no boundary to separate them: the scope
        # is genuinely ambiguous, so refuse by type instead of guessing. Only the inverted order
        # (modal first, negation second) is ambiguous; a negation first governs what follows it.
        modal = POSITIVE_MODAL.search(clause)
        if modal and modal.start() < negation.start():
            raise IntakeInvalid('ambiguous negation scope: a positive obligation and a negation '
                                'share one clause with no boundary to split them')
        return [(clause, True)]
    # One atom per boundary segment, with the clause-level negation governing the segments that follow
    # it until one states its own positive modality. Segments are NOT merged back into a single atom:
    # merging hides an obligation from validate_atoms, which is the collapse this module exists to
    # refuse. Each segment gets its own polarity, which is what the pre-repair compiler got wrong in
    # the other direction (a covered segment was compiled as MUST).
    obligations: list[tuple[str, bool]] = []
    inherited = False
    for segment in segments:
        if NEGATION.search(segment):
            inherited = True
            obligations.append((segment, True))
        elif POSITIVE_MODAL.search(segment):
            inherited = False
            obligations.append((segment, False))
        else:
            obligations.append((segment, inherited))
    return obligations


def _is_filler(statement: str) -> bool:
    residue = FILLER_TOKENS.sub('', FILLER_CHARS.sub('', statement))
    return not residue


def _polarity(statement: str, negation_inherited: bool) -> str:
    if negation_inherited or NEGATION.search(statement):
        return 'MUST NOT'
    return 'MUST'


def compile_requirements(goal: str, sources: list[str]) -> list[dict[str, Any]]:
    """Compile source clauses into clause-bound atomic requirements.

    A directory source binds the submitted goal as its inline clause source; a file source is read
    as authoritative clause text. Normative claims without a source locator are refused.
    """
    if not sources:
        raise IntakeInvalid('normative claim without a source locator is refused')
    atoms: list[dict[str, Any]] = []
    for source in sources:
        path = Path(source)
        inline = path.is_dir()
        try:
            text = goal if inline else path.read_text(encoding='utf-8')
        except (OSError, UnicodeError) as exc:
            raise IntakeInvalid(f'cannot read clause source: {path}') from exc
        for start, end, clause in _parts(text):
            clause_id = f'clause-{start}-{end}'
            for child, (statement, negation_inherited) in enumerate(_expand(clause)):
                if _is_filler(statement):
                    continue
                polarity = _polarity(statement, negation_inherited)
                locator = {'file': str(path), 'kind': 'inline-goal' if inline else 'file',
                           'clause_id': clause_id, 'span': [start, end], 'child': child,
                           'text': statement, 'source_text': clause,
                           'source_sha256': sha256_text(text)}
                rid = 'REQ-' + sha256_text(canonical_json(locator))[:20]
                atoms.append({'req_id': rid, 'source_clause': locator, 'owner': 'PIPD-EC',
                              'axis': advisory_axis(statement),
                              'acceptance_cue': f'{polarity}: {statement}',
                              'risk_guard': {
                                  'polarity': polarity,
                                  'oracle': {'id': 'ORACLE-' + rid, 'predicate': statement,
                                             'expected': 'forbidden' if polarity == 'MUST NOT'
                                             else 'required'},
                                  'negative_fixture': f'fixtures/{rid}/negative',
                                  'failure_condition': f'violate {polarity}: {statement}'}})
    if not atoms:
        raise IntakeInvalid('goal produced zero requirement atoms')
    validate_atoms(atoms)
    return atoms


def validate_atoms(atoms: list[dict[str, Any]]) -> None:
    """Refuse semantic collapse: shared identity, shared oracle or shared negative fixture."""
    if not atoms:
        raise PiSemanticFail('zero source clauses')
    if len({a['req_id'] for a in atoms}) != len(atoms):
        raise PiSemanticFail('semantic collapse: duplicate source atom')
    for a in atoms:
        if not isinstance(a.get('source_clause'), dict) or not isinstance(a.get('risk_guard'), dict):
            raise PiSemanticFail('legacy keyword atoms are not clause-bound')
        sc = a['source_clause']
        if not (sc.get('file') and sc.get('clause_id') and sc.get('span') is not None
                and a.get('owner') and a.get('acceptance_cue')):
            raise PiSemanticFail('atom lacks its source locator/owner/acceptance cue')
        rg = a['risk_guard']
        oracle = rg.get('oracle') or {}
        if not (oracle.get('id') and oracle.get('predicate') and rg.get('negative_fixture')):
            raise PiSemanticFail('atom lacks its oracle or negative fixture')
        if rg.get('polarity') not in ('MUST', 'MUST NOT'):
            raise PiSemanticFail('atom lacks a MUST / MUST NOT polarity')
    if len({a['risk_guard']['oracle']['id'] for a in atoms}) != len(atoms):
        raise PiSemanticFail('semantic collapse: shared oracle')
    if len({a['risk_guard']['negative_fixture'] for a in atoms}) != len(atoms):
        raise PiSemanticFail('semantic collapse: shared negative fixture')


def source_id_for(file: str, clause_id: str, source_sha256: str) -> str:
    """Stable hash reference to a normalized source clause (one entry per source clause)."""
    return 'SRC-' + sha256_text(canonical_json(
        {'file': file, 'clause_id': clause_id, 'sha256': source_sha256}))[:20]


def source_table(atoms: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Normalized source table: ONE entry per source clause (payload economy).

    An atom used to embed its clause twice - `text` (the derived statement) plus a byte-identical
    `source_text` copy - and repeat `source_sha256` on every atom bound to the same clause. Here
    each distinct clause is stored once (`source_id`, `sha256`, single `text`) and each atom carries
    only a stable `source_ref` into this table. Nothing semantic is dropped: the statement, the
    locator span/child and the polarity/oracle stay on the atom.
    """
    table: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any]] = set()
    for a in atoms:
        sc = a['source_clause']
        key = (sc.get('file'), sc.get('clause_id'))
        if key in seen:
            continue
        seen.add(key)
        sha = sc.get('source_sha256', '')
        table.append({'source_id': source_id_for(sc.get('file', ''), sc.get('clause_id', ''), sha),
                      'sha256': sha, 'text': sc.get('source_text', '')})
    return table


def normalized_locator(sc: dict[str, Any]) -> dict[str, Any]:
    """Atom-side locator after de-duplication: span/child + a stable `source_ref` hash pointer.

    The duplicated `source_text` (the whole clause copied onto every atom bound to it) and the
    per-atom `source_sha256` are removed; both are recoverable from the normalized source table via
    `source_ref`. The atom keeps its own derived `text` (the statement it binds) - that is per-atom
    content, not a copy of the clause.
    """
    ref = source_id_for(sc.get('file', ''), sc.get('clause_id', ''), sc.get('source_sha256', ''))
    return {'file': sc.get('file'), 'kind': sc.get('kind'), 'clause_id': sc.get('clause_id'),
            'span': sc.get('span'), 'child': sc.get('child'), 'text': sc.get('text'),
            'source_ref': ref}


def resolve_source_clause(atom: dict[str, Any], table: list[dict[str, Any]]) -> dict[str, Any]:
    """Resolve an atom's locator against the normalized table -> the pre-dedupe locator shape."""
    sc = dict(atom['source_clause'])
    entry = next((e for e in table if e['source_id'] == sc.get('source_ref')), None)
    if entry is not None:
        sc['source_text'] = entry['text']
        sc['source_sha256'] = entry['sha256']
        if 'text' not in sc:
            sc['text'] = entry['text']
    return sc


def obligation_trace(atoms: list[dict[str, Any]]) -> dict[str, Any]:
    """SRC -> REQ/Child -> SPEC -> ACC -> VER -> EVD -> DEL -> GATE per atom, no orphans."""
    nodes, edges = [], []
    for atom in atoms:
        previous = None
        for stage in STAGES:
            node = {'id': stage + ':' + atom['req_id'], 'stage': stage,
                    'requirement': atom['req_id'], 'status': 'OBLIGATION'}
            nodes.append(node)
            if previous:
                edges.append({'from': previous, 'to': node['id']})
            previous = node['id']
    return {'nodes': nodes, 'edges': edges, 'claim': 'planned obligations only'}


def trace_findings(atoms: list[dict[str, Any]], trace: dict[str, Any]) -> list[str]:
    expected = obligation_trace(atoms)
    if trace == expected:
        return []
    findings = ['SRC→REQ/Child→SPEC→ACC→VER→EVD→DEL→GATE incomplete or altered']
    got_ids = {n.get('id') for n in trace.get('nodes', [])}
    expected_ids = {n['id'] for n in expected['nodes']}
    for missing in sorted(expected_ids - got_ids):
        findings.append(f'missing obligation node {missing}')
    for extra in sorted(got_ids - expected_ids, key=str):
        findings.append(f'orphan obligation node {extra}')
    endpoints = {n.get('id') for n in trace.get('nodes', [])}
    for edge in trace.get('edges', []):
        for side in ('from', 'to'):
            if edge.get(side) not in endpoints:
                findings.append(f'edge endpoint orphan {edge.get(side)}')
    return findings
