"""Packet-only DOC-08 coverage measurement; never writes PIPD or the ledger.

Only DETERMINISTIC schema/semantic-contract checks are implemented here. This
is not native OracleRef qualification or functional invocation of eight skills.
"""
from __future__ import annotations
import argparse
import collections
import copy
import datetime
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import jsonschema
import yaml

BASE = Path('C:/Projects/Agent_Workspace')
REPO = BASE / 'HG-KSEOS'
OUT = BASE / '_r14_packet/raw'
PIPD = BASE / 'PIPD/skills'
DOC = BASE / '知識庫/實作相關DOC/Fabric vNext/Semantic World OS Fabric/SBL/SBL_PIPD-LS-PKG/SBL_PIPD-LS-PKG_DOC-08.md'
SELF = Path(__file__).resolve()

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def normative():
    cells = []
    for line_no, line in enumerate(DOC.read_text(encoding='utf-8').splitlines(), 1):
        parts = [s.strip() for s in line.split('|')[1:-1]]
        if len(parts) == 8 and '/' in parts[0] and parts[1].startswith('L'):
            test_class, oracle = parts[0].split('/')
            cells.append(dict(test_class=test_class, oracle_type=oracle, source_rule=parts[1],
                predicate=parts[2], typed_input_required=parts[3], typed_output_required=parts[4],
                mutation=parts[5], first_fail=parts[6], owner_consumer=parts[7], doc08_line=line_no))
    assert len(cells) == 96 and len({(c['test_class'], c['oracle_type']) for c in cells}) == 96
    return cells

def execute(skill, test_class):
    """Real repo validator + runtime predicates; exact_eq only, no oracle fanout."""
    conformance = load_module('ts17_repo_conformance', REPO/'scripts/pipd_skills_conformance.py')
    from hg_kseos.semantic_oracle import check_distinct, check_claim_gate
    root = PIPD/skill
    cases = yaml.safe_load((root/'tests/cases.yaml').read_text(encoding='utf-8'))['cases']
    selected = [c for c in cases if c['kind'] == test_class]
    assert selected, 'No fixture: not an execution'
    schemas = {side: json.loads((root/f'schemas/{side}.schema.json').read_text(encoding='utf-8')) for side in ('input','output')}
    for schema in schemas.values():
        jsonschema.validators.validator_for(schema).check_schema(schema)
    controls = []
    positive = next(c for c in cases if c['id'] == 'POS-001')
    for side, schema in schemas.items():
        valid = conformance.validate(positive[side], schema)[0]
        broken = copy.deepcopy(positive[side])
        field = schema['required'][0]
        del broken[field]
        rejected = not conformance.validate(broken, schema)[0]
        controls.append(dict(side=side, valid_accepted=valid, invalid_rejected=rejected, mutation='delete /'+field))
        assert valid and rejected
    observations = []
    for case in selected:
        checks = {side: dict(zip(('accepted','error'), conformance.validate(case[side], schema)))
                  for side, schema in schemas.items() if side in case}
        rejected = any(not c['accepted'] for c in checks.values())
        semantic = None
        if case.get('first_fail') == 'semantic.distinct':
            semantic = check_distinct(case['input'], case.get('output'))
        elif case.get('first_fail') == 'semantic.claim_gate':
            semantic = check_claim_gate(case['input'], case.get('output'))
        if semantic is not None:
            assert semantic['verdict'] != 'NOT_APPLICABLE'
            rejected = rejected or semantic['verdict'] == 'VIOLATED'
        expected = case['expect']
        observed = 'REFUSE' if rejected else 'ACCEPT'
        observations.append(dict(case_id=case['id'], rationale=case.get('rationale'),
            first_fail_declared=case.get('first_fail'), expected_value=expected, observed_value=observed,
            exact_eq=expected == observed, schema_checks=checks, semantic_result=semantic))
    result = dict(skill=skill, test_class=test_class, oracle_type='DETERMINISTIC',
        decision_operator='exact_eq', scope='SCHEMA_AND_PURE_SEMANTIC_CONTRACT_ONLY',
        source_owned_outputs_are_fixtures_not_generated=True, controls=controls, observations=observations,
        ok=all(o['exact_eq'] for o in observations))
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['ok'] else 1

def main():
    conformance = load_module('ts17_repo_conformance_inventory', REPO/'scripts/pipd_skills_conformance.py')
    skills = conformance.OFFICIAL
    assert len(skills) == len(set(skills)) == 8
    native = normative()
    classes = list(dict.fromkeys(c['test_class'] for c in native))
    types = list(dict.fromkeys(c['oracle_type'] for c in native))
    frozen = [DOC, REPO/'var/R14-OBLIGATIONS/OBLIGATIONS.json']
    frozen += sorted((BASE/'PIPD').rglob('*.schema.json'))
    frozen += [PIPD/s/'tests/cases.yaml' for s in skills]
    frozen += [REPO/'scripts/pipd_skills_conformance.py', REPO/'src/hg_kseos/semantic_oracle.py', SELF]
    before = {p.as_posix(): sha(p) for p in frozen}
    status_before = subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True)
    commit = subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
    inventory = []
    terms = types + skills + ['semantic.distinct','semantic.claim_gate']
    for folder in ('src','scripts','tests','tools'):
        for path in sorted((REPO/folder).rglob('*.py')):
            text = path.read_text(encoding='utf-8', errors='replace')
            hits = [t for t in terms if t in text]
            if hits:
                inventory.append(dict(path=path.as_posix(), sha256=sha(path), matching_identifiers=hits))
    executions = {}
    env = dict(os.environ, PYTHONPATH='src', PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8')
    for skill in skills:
        fixture_doc = yaml.safe_load((PIPD/skill/'tests/cases.yaml').read_text(encoding='utf-8'))
        for cls in classes:
            if not any(c['kind'] == cls for c in fixture_doc['cases']):
                continue
            args = ['./.venv/Scripts/python.exe','-B',SELF.as_posix(),'--skill',skill,'--test-class',cls]
            command = 'PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8 ' + shlex.join(args)
            proc = subprocess.run(args, cwd=REPO, env=env, capture_output=True, text=True, encoding='utf-8',timeout=60)
            record = dict(skill=skill, test_class=cls, oracle_type='DETERMINISTIC', command=command,
                cwd=REPO.as_posix(), exit_code=proc.returncode,
                checked_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), stdout=proc.stdout, stderr=proc.stderr)
            if proc.returncode == 0:
                record['measurement'] = json.loads(proc.stdout)
                assert record['measurement']['ok']
            path = OUT/f'ts17_v2_execution_{skill}_{cls}.json'
            path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            executions[skill, cls] = dict(command=command, cwd=REPO.as_posix(), exit_code=proc.returncode,
                evidence_path=path.as_posix(), evidence_sha256=sha(path))
    cells = []
    missing = {
        'STATE_READBACK':'No skill/class-bound native pre/post state transition runner and digests executed; schema rejection is not state readback.',
        'PROPERTY':'No skill/class-bound generated cases, invariant and seed runner executed; ordinary parametrization is not property coverage.',
        'REFERENCE_OUTPUT':'No skill/class-bound pinned reference comparison executed; stored fixture outputs and hashes alone are not pinned_reference_eq.',
        'STATISTICAL':'No skill/class-bound dataset/calibration/confidence/threshold benchmark executed.',
        'SEMANTIC_JUDGE':'No skill/class-bound pinned judge, rubric and human calibration executed. semantic.distinct/claim_gate are deterministic predicates, not calibrated judges.',
        'HUMAN':'No skill/class-bound signed human decision, rubric, principal and consent/basis executed/read back.',
        'COMPOSITE':'No skill/class-bound ordered component oracle runner, failure policy and raw component receipts executed; checking input/output schemas together is not DOC-08 COMPOSITE.'}
    for skill, n in itertools.product(skills,native):
        row = dict(skill=skill, **n, state='DECLARED_ONLY', qualification_scope='NOT_EXECUTED',
            command=None, exit_code=None, evidence_path=None, evidence_sha256=None)
        receipt = executions.get((skill,n['test_class'])) if n['oracle_type'] == 'DETERMINISTIC' else None
        if receipt:
            row.update(receipt)
            row['qualification_scope'] = 'SCHEMA_AND_PURE_SEMANTIC_CONTRACT_ONLY'
            row['state'] = 'RUNTIME_QUALIFIED' if receipt['exit_code'] == 0 else 'DECLARED_ONLY'
            row['reason'] = ('Exact acceptance/refusal equality on this skill/class source fixtures using the repo validator and, where needed, repo semantic predicates. Not skill output generation or native qualification.' if receipt['exit_code'] == 0 else 'Execution failed; retained DECLARED_ONLY.')
        else:
            row['reason'] = missing.get(n['oracle_type'],'No source skill/class fixtures or dedicated executable coverage identified; no unrelated HGK tests substituted.')
        row['full_doc08_functional_native_qualification'] = False
        cells.append(row)
    assert len(cells) == len(skills)*len(native)
    counts = collections.Counter(c['state'] for c in cells)
    by_type = {t: dict(collections.Counter(c['state'] for c in cells if c['oracle_type']==t)) for t in types}
    unqualified = [t for t in types if not any(c['oracle_type']==t and c['state']=='RUNTIME_QUALIFIED' for c in cells)]
    after = {p.as_posix():sha(p) for p in frozen}
    assert before == after, 'Source or ledger mutated'
    status_after = subprocess.check_output(['git','-C',str(REPO),'status','--porcelain'],text=True)
    assert status_after == status_before
    result = dict(schema='R14-TS17-DOC08-SHAPED-MEASUREMENT/2',
        measured_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), repository=REPO.as_posix(), commit=commit,
        qualification_definition='Executed local DETERMINISTIC schema/semantic CONTRACT oracle with exact_eq and row-specific fixtures; never native PIPD admission, functional skill invocation, independent acceptance or release. Other OracleTypes require their own executable semantics and cannot inherit this result.',
        doc08_functional_gap='POS here validates declared fixture outputs; no feature_invoked proof. SEC rejects malicious contract payloads, but effect/egress is not observed. NEG no-state-diff is not runtime-world readback. These local oracle executions do not satisfy the whole C39.1 journey or Native ALL.',
        dimensions=dict(skills=skills,test_classes=classes,oracle_types=types,normative_cells_per_skill=len(native)),
        totals=dict(cells_total=len(cells),cells_runtime_qualified=counts['RUNTIME_QUALIFIED'],cells_declared_only=counts['DECLARED_ONLY'],
            executions=len(executions),by_oracle_type=by_type,full_doc08_functional_native_qualified=0),
        unqualified_oracle_types=unqualified,
        partially_qualified_oracle_types=[t for t in types if 0 < sum(c['oracle_type']==t and c['state']=='RUNTIME_QUALIFIED' for c in cells) < len(skills)*len(classes)],
        normative_source=dict(path=DOC.as_posix(),sha256=sha(DOC),cell_table_lines=[native[0]['doc08_line'],native[-1]['doc08_line']]),
        provenance=dict(input_sha256=before, source_and_ledger_unchanged=before==after,git_status_unchanged=status_before==status_after,
            source_inventory=inventory,measurement_builder_path=SELF.as_posix()),
        historical_correction='TT-R14-037: 96 class x skill rows were not 96 class x OracleType cells. This artifact contains eight separate 96-cell oracle matrices. Prior schema-only 30/96 cannot be projected to all oracle types. Two negative schemas still accept their fixtures; HGK deterministic runtime predicates now refuse both.',
        cells=cells)
    matrix = OUT/'ts17_matrix_v2.json'
    matrix.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines = ['# TS17 DOC-08-shaped runtime measurement','',
        f"- {len(cells)} cells = {len(skills)} skills × {len(classes)} TestClasses × {len(types)} OracleTypes.",
        f"- Local contract-oracle execution: **{counts['RUNTIME_QUALIFIED']} RUNTIME_QUALIFIED / {counts['DECLARED_ONLY']} DECLARED_ONLY**; {len(executions)} isolated commands.",
        '- Scope: DETERMINISTIC schema/semantic-contract checks only. **Full DOC-08 functional/native qualification: 0**. POS fixture output validation does not invoke a skill; NEG/SEC do not establish runtime-world state or egress. These limits are explicit in the JSON, not acceptance claims.',
        '- The two schema-accepted negatives remain schema-accepted. Actual HGK semantic.distinct and semantic.claim_gate predicates are executed to refuse them; neither is a SEMANTIC_JUDGE.',
        '- No state propagated to other OracleTypes, no invented fixtures or output generation, no ledger or PIPD edits. No independent checker/acceptance issued by this measurement.',
        f'- Repository commit: `{commit}`.',
        '- Every cell, normative predicate and source rule is in `ts17_matrix_v2.json`; qualified cells carry exact command, cwd, exit, evidence path and SHA-256. Evidence files contain full stdout/stderr and raw expected/observed values.',
        '', '## Unqualified OracleTypes','']
    lines += ['- '+t+': '+missing[t] for t in unqualified]
    lines += ['', '## Per OracleType', '', '| OracleType | RUNTIME_QUALIFIED | DECLARED_ONLY |','| --- | ---: | ---: |']
    lines += [f"| {t} | {by_type[t].get('RUNTIME_QUALIFIED',0)} | {by_type[t].get('DECLARED_ONLY',0)} |" for t in types]
    (OUT/'ts17_matrix_v2.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(matrix_path=matrix.as_posix(),**result['totals'],unqualified_oracle_types=unqualified)))

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--skill')
    parser.add_argument('--test-class')
    args=parser.parse_args()
    if args.skill and args.test_class:
        raise SystemExit(execute(args.skill,args.test_class))
    main()
