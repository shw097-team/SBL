"""SBL portable planning adapters v1. Local checks never issue authority.

Trusted native receipts must be read by an external protected reader. This
module deliberately has no API which turns a caller boolean into admission.
"""
from __future__ import annotations
import hashlib
import json
import re
from collections import Counter
from pathlib import Path, PurePosixPath, PureWindowsPath

SHA = re.compile(r"[0-9a-f]{64}\Z")
RISK_AXES = ('authority_complexity', 'side_effect_risk', 'integration_count',
             'irreversibility_risk', 'assurance_requirement', 'permission_scope',
             'data_sensitivity', 'financial_or_physical_effect', 'blast_radius',
             'operational_consequence', 'brownfield_complexity', 'runtime_autonomy')
CONTEXT_AXES = ('intent','knowledge','verification','release','trust_boundary',
                'preexisting_repo','profile','tech_candidates','host_surface')
RISK_CONTEXT_MAP = {
    'authority_complexity':['trust_boundary'], 'side_effect_risk':['host_surface','verification'],
    'integration_count':['tech_candidates'], 'irreversibility_risk':['release','verification'],
    'assurance_requirement':['verification'], 'permission_scope':['trust_boundary','host_surface'],
    'data_sensitivity':['knowledge','trust_boundary'], 'financial_or_physical_effect':['host_surface','verification'],
    'blast_radius':['release','trust_boundary'], 'operational_consequence':['host_surface'],
    'brownfield_complexity':['preexisting_repo'], 'runtime_autonomy':['host_surface','trust_boundary']}
EFFECTS = ('READ_ONLY','REPO_WRITE','HOST','USER','REMOTE')

def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def json_digest(obj) -> str:
    # Adapter encoding only, not a claim to DOC-06 RFC8785/JCS equivalence.
    return digest(json.dumps(obj, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode('utf-8'))

class Refusal(ValueError):
    def __init__(self, code, scope='candidate', resume='repair affected input'):
        super().__init__(code)
        self.envelope = {'schema':'PIPD.ErrorEnvelope@1', 'first_fail':code,
                         'affected_scope':[scope], 'allowed_next_action':'READ_ONLY_OR_UNAFFECTED_READY',
                         'resume_predicate':resume, 'status':'BLOCKED',
                         'claim_ceiling':'AUTHOR_SIDE_REPAIR_CANDIDATE'}

def require(condition, code, scope='candidate'):
    if not condition:
        raise Refusal(code, scope)

def read_contained(root: Path, relative: str) -> bytes:
    """Reject lexical escapes, NTFS reparses, hardlinks and observed replacement.

    Identity checks detect observed races; this is not an OS handle-based proof
    against a hostile concurrent writer. Formal protected-reader claims stay HOLD.
    """
    root=Path(root).resolve(strict=True)
    require(isinstance(relative,str) and relative and '\\' not in relative and ':' not in relative,
            'PATH_INVALID')
    parts=PurePosixPath(relative).parts
    require(not PurePosixPath(relative).is_absolute() and all(p not in ('.','..') for p in parts),
            'PATH_ESCAPE')
    cursor=root
    for part in parts:
        cursor=cursor/part
        s=cursor.lstat()
        require(not cursor.is_symlink() and not getattr(s,'st_file_attributes',0)&0x400,
                'REPARSE_POINT')
    require(cursor.resolve(strict=True).is_relative_to(root),'PATH_ESCAPE')
    before=cursor.stat()
    require(cursor.is_file() and before.st_nlink==1,'HARDLINK_OR_NOT_FILE')
    raw=cursor.read_bytes()
    after=cursor.stat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==
            (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'SOURCE_RACE')
    return raw

def corpus_manifest(root: Path, expected_manifest_sha=None):
    raw=read_contained(root,'references/corpus/SourceManifest.json')
    if expected_manifest_sha is not None:
        require(digest(raw)==expected_manifest_sha,'MANIFEST_DRIFT')
    obj=json.loads(raw)
    require(obj.get('schema')=='SBL.CorpusManifest@1','MANIFEST_SCHEMA')
    require(obj.get('required_group_counts')=={'pipd':10,'sbl':14},'DENOMINATOR')
    files=obj.get('files')
    require(isinstance(files,list) and len(files)==24,'DENOMINATOR')
    expected={f'{g}-{i:02d}' for g,n in [('PIPD',10),('SBL',14)] for i in range(n)}
    require({r.get('source_id') for r in files}==expected,'SOURCE_ID_DENOMINATOR')
    require(len({r.get('path') for r in files})==24,'DUPLICATE_PATH')
    require(Counter(r.get('group') for r in files)=={'pipd':10,'sbl':14},'DENOMINATOR')
    for row in files:
        require(row.get('required') is True and SHA.fullmatch(str(row.get('sha256',''))),'BAD_SOURCE_PIN')
        require(row['source_id'].startswith(row['group'].upper()+'-'),'SOURCE_GROUP_MISMATCH')
        raw=read_contained(root,row['path'])
        raw.decode('utf-8','strict')
        require(digest(raw)==row['sha256'],'SOURCE_DRIFT',row['source_id'])
    return obj

def read_clause(root: Path, source_id: str, line_from: int, line_to: int):
    mf=corpus_manifest(root)
    rows=[r for r in mf['files'] if r['source_id']==source_id]
    require(len(rows)==1,'SOURCE_MISSING')
    row=rows[0]
    raw=read_contained(root,row['path'])
    require(digest(raw)==row['sha256'],'SOURCE_DRIFT',source_id)
    lines=raw.decode('utf-8').splitlines()
    require(type(line_from)==int and type(line_to)==int and 1<=line_from<=line_to<=len(lines),
            'LINE_RANGE')
    require(line_to-line_from<250,'PROGRESSIVE_DISCLOSURE_LIMIT')
    return {'source_id':source_id,'sha256':row['sha256'],'line_from':line_from,
            'line_to':line_to,'authority_state':row['authority_state'],
            'text':'\n'.join(lines[line_from-1:line_to])}

class ArtifactResolver:
    """Pinned local Reader; catalog provenance must come from its actual owner.

    Catalog signatures/authority are not inferred. Local fixtures can exercise
    exact identity but cannot qualify the canonical source authority.
    """
    def __init__(self, root: Path, catalog_path: str, expected_catalog_sha: str):
        raw=read_contained(root,catalog_path)
        require(SHA.fullmatch(expected_catalog_sha) and digest(raw)==expected_catalog_sha,'CATALOG_DRIFT')
        catalog=json.loads(raw)
        require(catalog.get('schema')=='SBL.ArtifactCatalog@1','CATALOG_SCHEMA')
        require(catalog.get('encoding')=='pipd-python-json@1','ENCODING_UNSUPPORTED')
        require(isinstance(catalog.get('records'),list) and catalog['records'],'EMPTY_CATALOG')
        self.root=Path(root); self.catalog_sha=expected_catalog_sha; self.records={}
        for row in catalog['records']:
            key=(row['subject_id'],row['content_hash'])
            require(key not in self.records,'DUPLICATE_ARTIFACT')
            require(row.get('version') and row.get('schema_version') and SHA.fullmatch(row['file_sha256']),
                    'ARTIFACT_METADATA')
            self.records[key]=row

    def resolve(self, ref):
        key=(ref.get('subject_id'),ref.get('content_hash'))
        require(key in self.records,'UNRESOLVED_REFERENCE')
        row=self.records[key]
        require(row.get('currentness')=='CURRENT','STALE_ARTIFACT',key[0])
        raw=read_contained(self.root,row['path'])
        require(digest(raw)==row['file_sha256'],'ARTIFACT_FILE_DRIFT',key[0])
        obj=json.loads(raw)
        require((obj.get('subject_id'),obj.get('content_hash'))==key,'ARTIFACT_IDENTITY',key[0])
        require(obj.get('version')==row['version'] and obj.get('schema_version')==row['schema_version'],
                'ARTIFACT_VERSION',key[0])
        body={k:v for k,v in obj.items() if k not in
              ('subject_id','version','content_hash','schema_version','trace','_profile_meta')}
        require(json_digest(body)==key[1],'ARTIFACT_BODY_HASH',key[0])
        require(key[0].endswith('-'+key[1][:16]),'ARTIFACT_SUBJECT_HASH',key[0])
        return obj

    def graph(self, refs, declared_edges):
        require(type(declared_edges)==int and declared_edges>=0,'GRAPH_EDGE_TYPE')
        objects=[self.resolve(ref) for ref in refs]
        seen=set()
        for obj in objects:
            for edge in obj.get('trace',[]):
                parent=self.resolve({'subject_id':edge['from_id'],'content_hash':edge['from_hash']})
                child=self.resolve({'subject_id':edge['to_id'],'content_hash':edge['to_hash']})
                require(parent['subject_id']==obj['subject_id'],'GRAPH_WRONG_PARENT')
                require(edge['from_type']==parent['schema_version'].split('@')[0] and
                        edge['to_type']==child['schema_version'].split('@')[0],'GRAPH_TYPE')
                key=(edge['from_id'],edge['from_hash'],edge['to_id'],edge['to_hash'])
                require(key not in seen,'GRAPH_DUPLICATE_EDGE')
                seen.add(key)
        require(len(seen)==declared_edges,'GRAPH_EDGE_COUNT')
        return {'edges':len(seen),'catalog_sha256':self.catalog_sha,
                'provenance':'PINNED_LOCAL_READER_ONLY','formal_authority':'UNVERIFIED'}

def fixture_joins(skill, inp, out):
    """Cross-object fixture invariants, separate from JSON Schema validation.

    These compare fixture projections, and never turn historic receipt strings
    or scalar references into live authority.
    """
    if skill=='pipd-pi-compile':
        atoms={a['subject_id']:a['content_hash'] for a in out['stable_semantic_contract']['atoms']}
        require(len(atoms)==len(inp['atoms']),'ATOM_COUNT')
        require(len(out['trace'])==len(atoms),'TRACE_COUNT')
        for edge in out['trace']:
            require(edge['to_id'] in atoms and edge['to_hash']==atoms[edge['to_id']], 'WRONG_ATOM_HASH')
            require(edge['from_id']==out['subject_id'] and edge['from_hash']==out['content_hash'],'WRONG_PARENT_HASH')
        require(len({e['to_id'] for e in out['trace']})==len(atoms),'TRACE_DUPLICATE')
        require(out['stable_semantic_contract']['profile_binding']['profile']==inp['profile'], 'PROFILE_PROVENANCE')
    elif skill=='pipd-execution-contract':
        require(out['construction_contract']['subject']==inp['pd']['subject_id'],'WRONG_PD_SUBJECT')
    elif skill=='pipd-assurance-tqaep':
        for acc in out['acceptance']:
            require(acc['checker_execution_receipt']==inp['checker_execution_receipt'],'WRONG_CHECKER_RECEIPT')
            require(acc['maker_identity']==inp['maker'] and acc['checker_identity']==inp['checker'],'WRONG_PRINCIPAL')
    elif skill=='pipd-package-project':
        require(out['trace_closure']['edges']==inp['bundle']['trace_edges'],'GRAPH_PROVENANCE_MISSING')
    return {'verdict':'PASS','claim_ceiling':'FIXTURE_CROSS_JOIN_ONLY'}

def risk_mapping(data):
    require(data.get('schema')=='SBL.RiskMapping@1','RISK_SCHEMA')
    scores=data.get('scores',{})
    require(set(scores)==set(RISK_AXES),'RISK_AXIS_MISSING')
    require(type(data.get('provider_off_required')) is bool,'PROVIDER_OFF_REQUIRED')
    require(data.get('target') in ('SYSTEM','SKILL_PLUGIN','AGENT_HARNESS'),'TARGET_UNKNOWN')
    for axis,row in scores.items():
        require(isinstance(row,dict) and type(row.get('score'))==int and 0<=row['score']<=3
                and bool(row.get('rationale')) and bool(row.get('evidence_refs')),'RISK_EVIDENCE_MISSING',axis)
    requested=data.get('requested_profile')
    require(requested in ('LITE','STANDARD','ASSURED'),'PROFILE_UNKNOWN')
    s={k:v['score'] for k,v in scores.items()}
    veto=(s['financial_or_physical_effect']>=2 or s['permission_scope']>=3 or
          s['irreversibility_risk']>=3 or s['blast_radius']>=3 or s['assurance_requirement']>=3 or
          s['authority_complexity']>=3 or
          (s['runtime_autonomy']>=2 and max(s['permission_scope'],s['side_effect_risk'],s['data_sensitivity'])>=2) or
          (s['data_sensitivity']>=2 and s['side_effect_risk']>=2) or
          (s['brownfield_complexity']>=3) or sum(s.values())>=24)
    floor='ASSURED' if veto else ('LITE' if max(s.values())<=1 and sum(s.values())<=8
          and data['target']!='AGENT_HARNESS' else 'STANDARD')
    if data['provider_off_required'] and floor=='LITE': floor='STANDARD'
    ladder=['LITE','STANDARD','ASSURED']
    effective=ladder[max(ladder.index(floor),ladder.index(requested))]
    # All 12 facts are retained; the nine context labels cannot encode their scores.
    contexts={'intent','profile'}
    for axis,score in s.items():
        if score: contexts.update(RISK_CONTEXT_MAP[axis])
    return {'schema':'SBL.RiskProjection@1','effective_profile_candidate':effective,
            'source_scores':scores,'context_axes':[a for a in CONTEXT_AXES if a in contexts],
            'mapping_version':'risk12-context9-proposal@1',
            'axis_provenance':{a:{'score':s[a],'context_labels':RISK_CONTEXT_MAP[a]} for a in RISK_AXES},
            'lossiness':'NON_EQUIVALENT_12_SCORES_VS_9_CONTEXT_LABELS',
            'formal_profile_state':'HOLD_FOR_PROFILE_OWNER','veto':veto,
            'source_ref':data.get('source_ref'),'claim_ceiling':'DESIGN_CANDIDATE'}

def planned_tqaep(subject, atoms):
    require(SHA.fullmatch(subject or '') and isinstance(atoms,list) and atoms,'PLAN_SUBJECT_ATOMS')
    require(len(set(a.get('req_id') for a in atoms))==len(atoms),'DUPLICATE_REQUIREMENT')
    tests=[]
    for atom in atoms:
        require(all(atom.get(k) for k in ('req_id','source_ref','oracle_ref','positive_fixture','negative_fixture')),
                'ORACLE_OR_FIXTURE_MISSING')
        tests.append(dict(atom))
    return {'schema':'SBL.PlannedTQAEP@1','subject_sha256':subject,'state':'PLANNED',
            'tests':tests,'claim_ceiling':'DESIGN_CANDIDATE','live_acceptance':'NOT_RUN'}

def formal_evidence(claim, record, expected_subject, expected_operation, expected_epoch):
    # No arbitrary JSON receipt can attest its own authenticity. This adapter
    # verifies joins and emits a request for the real protected reader.
    require(record.get('subject_sha256')==expected_subject,'EVIDENCE_SUBJECT')
    require(record.get('operation')==expected_operation and record.get('epoch')==expected_epoch,'EVIDENCE_OPERATION_EPOCH')
    maker=record.get('maker_principal'); checker=record.get('checker_principal')
    require(isinstance(maker,str) and isinstance(checker,str) and maker.strip() and checker.strip()
            and maker.strip().casefold()!=checker.strip().casefold(),'PRINCIPAL_SEPARATION')
    require(record.get('maker_can_modify_checker') is False,'CHECKER_MUTABLE')
    return {'status':'BLOCKED','first_fail':'PROTECTED_RECEIPT_READER_REQUIRED',
            'requested_claim':claim,'claim_ceiling':'CANDIDATE_ONLY'}

def oracle_binding(data, expected_doc07_sha):
    require(data.get('schema')=='SBL.OracleBinding@1','ORACLE_SCHEMA')
    require(data.get('canonical_owner')=='PIPD_LS_DOC-07','ORACLE_WRITER')
    require(data.get('canonical_source_sha256')==expected_doc07_sha,'ORACLE_SHA')
    require(bool(data.get('legacy_doc03_locator')) and bool(data.get('oracle_ref')),'ORACLE_LOCATOR')
    return {'status':'BLOCKED','conflict_id':'CR-ORACLE-001','first_fail':'OWNER_RATIFICATION_READER_REQUIRED',
            'allowed_next_action':'PLAN_WITH_BOTH_SOURCE_PROJECTIONS'}

def effect_route(effect, *, outcome='NOT_ATTEMPTED'):
    require(effect in EFFECTS,'UNKNOWN_EFFECT')
    require(outcome in ('NOT_ATTEMPTED','KNOWN_FAILED','KNOWN_SUCCESS','UNKNOWN_EFFECT'),'OUTCOME_UNKNOWN')
    if outcome=='UNKNOWN_EFFECT':
        return {'effect':effect,'status':'BLOCKED','next':'RECONCILE_BEFORE_RETRY'}
    if effect=='READ_ONLY': return {'effect':effect,'status':'READY','next':'READ_WITHIN_SCOPE'}
    return {'effect':effect,'status':'BLOCKED','next':f'EXISTING_{effect}_ADMISSION_REQUIRED'}

def affected_work(nodes, failed):
    require(set(failed)<=set(nodes),'UNKNOWN_FAILED_NODE')
    pending=set(nodes); order=[]
    while pending:
        ready=sorted(n for n in pending if set(nodes[n])<=set(order))
        require(ready,'DAG_CYCLE_OR_UNKNOWN_DEPENDENCY')
        order.extend(ready); pending.difference_update(ready)
    affected=set(failed)
    for n in order:
        if set(nodes[n])&affected: affected.add(n)
    return {'order':order,'blocked':sorted(affected),'ready':[n for n in order if n not in affected]}

def runnable_obligations(rows):
    require(len({r['id'] for r in rows})==len(rows),'OBLIGATION_DUPLICATE')
    require(all(r.get('disposition') in ('REQUIRED','CONDITIONAL','DEFERRED') for r in rows),'OBLIGATION_STATE')
    return {'obligations':rows,'ready':[r['id'] for r in rows if
            r['disposition']=='REQUIRED' or (r['disposition']=='CONDITIONAL' and r.get('triggered') is True)]}

def claim_projection(package_state, ready_count, requested):
    require(type(ready_count)==int and ready_count>=0,'READY_COUNT')
    if requested in ('MISSION_COMPLETE','NATIVE_ACCEPTED','PRODUCTION_RELEASED','HOST_QUALIFIED','INDEPENDENT_PASS'):
        raise Refusal('EXTERNAL_RAW_AND_AUTHORITY_REQUIRED',requested)
    require(requested in ('DESIGN_CANDIDATE','PACKAGE_CANDIDATE'),'CLAIM_UNKNOWN')
    return {'package_state':package_state,'mission_state':'OPEN' if ready_count else 'REVIEW_REQUIRED',
            'claim':requested}

STATES=('UNDECIDED','ASKED_PENDING','DEFERRED','LOCAL_ONLY','PUBLISH_REQUESTED',
        'PUBLISH_ADMITTED','PUBLISHED_VERIFIED','PUBLISH_BLOCKED')

def decision_gate(data, operation='PLAN', expected_subject=None, expected_scope=None, now=0):
    require(data.get('schema')=='SBL.GitHubDeliveryDecision@1','DECISION_SCHEMA')
    require(bool(SHA.fullmatch(str(data.get('subject_sha256','')))),'DECISION_SUBJECT')
    require(data.get('question_key')=='github_publication_for_mission','QUESTION_KEY')
    require(data.get('state') in STATES,'DECISION_STATE')
    require(expected_subject is None or data['subject_sha256']==expected_subject,'DECISION_WRONG_SUBJECT')
    require(expected_scope is None or data.get('scope')==expected_scope,'DECISION_SCOPE_CHANGED')
    if data.get('expires_at') is not None: require(data['expires_at']>now,'DECISION_EXPIRED')
    state=data['state']
    if operation=='PLAN':
        return {'status':'PASS','ask':state=='UNDECIDED','remote_effect':False}
    if operation=='LOCAL_DELIVERY':
        return {'status':'PASS' if state=='LOCAL_ONLY' and data.get('owner_decision_ref') else 'BLOCKED',
                'remote_effect':False,'claim_ceiling':'LOCAL_CANDIDATE_ONLY'}
    require(operation=='REMOTE_PUBLICATION','OPERATION_UNKNOWN')
    # Even PUBLISH_ADMITTED text cannot replace the existing Publisher adapter.
    return {'status':'BLOCKED','first_fail':'EXTERNAL_PUBLISHER_GHP02_REQUIRED','remote_effect':False}

class QuestionLedger:
    def __init__(self, rows=None): self.rows=list(rows or [])
    def inspect(self, key, subject, scope, source_sha, now=0):
        for row in reversed(self.rows):
            if (row['key'],row['subject'],row['scope'],row['source_sha'])==(key,subject,scope,source_sha):
                if row.get('expires_at') is None or row['expires_at']>now:
                    return {'ask':False,'row':row}
        return {'ask':True}
    def record(self, key, subject, scope, source_sha, answer=None, **fields):
        self.rows.append(dict(key=key,subject=subject,scope=scope,source_sha=source_sha,answer=answer,**fields))

def remote_claim(operation, evidence, expected_sha):
    require(operation in ('PUSH','PR','MERGE','RELEASE'),'REMOTE_OPERATION')
    require(evidence.get('head_sha')==expected_sha,'REMOTE_WRONG_SHA')
    if operation=='PR': require(evidence.get('pr_url'),'PR_NOT_CREATED')
    if operation=='MERGE': require(evidence.get('merge_sha'),'MERGE_NOT_OBSERVED')
    if operation=='RELEASE': require(evidence.get('release_url'),'RELEASE_NOT_OBSERVED')
    return {'status':'BLOCKED','first_fail':'TRUSTED_REMOTE_READBACK_REQUIRED','operation':operation}

def handoff(data, expected_subject, expected_source_sha):
    require(data.get('schema')=='SBL.MissionHandoff@1' and data.get('abi_version')=='1','ABI_VERSION')
    require(data.get('subject_sha256')==expected_subject,'HANDOFF_SUBJECT')
    require(data.get('source_manifest_sha256')==expected_source_sha,'HANDOFF_SOURCE_SHA')
    require(data.get('receiver') not in (None,'sbl-commander-sp'),'NO_ADMITTED_ROUTE')
    require(all(data.get(k) for k in ('resume_predicate','affected_scope','artifact_refs')),'HANDOFF_FIELDS')
    require(data.get('effect_class') in EFFECTS,'UNKNOWN_EFFECT')
    require(not set(data)&{'token','credential','permit','checker_receipt','secret'},'HANDOFF_SECRET_OR_AUTHORITY')
    return {'status':'BLOCKED','first_fail':'NATIVE_RECEIVER_ACK_REQUIRED','claim_ceiling':'HANDOFF_CANDIDATE'}

def mode_for(*, risk_unknown=False, external_effect=False, owner_conflict=False, sources_complete=True):
    return 'Critical' if risk_unknown or external_effect or owner_conflict else ('Quick' if sources_complete else 'Guided')

def plan_spec(kind, data):
    """Materialize typed drafts from owner inputs; never compile canonical PI/PD."""
    require(kind in ('Product','Architecture','Program'),'SPEC_KIND')
    require(bool(SHA.fullmatch(str(data.get('source_sha256','')))),'SPEC_SOURCE_SHA')
    require(data.get('source_refs') and data.get('goal') and data.get('non_goals'),'SPEC_SOURCE_GOAL_SCOPE')
    acceptance=data.get('acceptance')
    require(isinstance(acceptance,list) and acceptance and all(
        isinstance(a,dict) and all(a.get(k) for k in ('requirement','positive','negative','oracle_ref')) for a in acceptance),
        'SPEC_ACCEPTANCE_ORPHAN')
    required={'Product':('persona','jtbd','fuo'),
              'Architecture':('adr','ownership_seams','abi_version','risk'),
              'Program':('dag','owners','work_packages','resume_predicate')}[kind]
    require(all(data.get(k) for k in required),'SPEC_REQUIRED_FIELDS')
    output={k:data[k] for k in ('source_sha256','source_refs','goal','non_goals','acceptance',*required)}
    if kind=='Architecture':
        seams=data['ownership_seams']
        require(isinstance(seams,list) and seams and all(
            isinstance(s,dict) and isinstance(s.get('writers'),list) and len(s['writers'])==1 for s in seams),
            'ONE_WRITER_PER_SEAM')
    if kind=='Program':
        graph=affected_work(data['dag'],[])
        require(set(data['owners'])==set(data['dag']),'DAG_OWNER_MISSING')
        require(set(data['work_packages'])==set(data['dag']),'DAG_WORK_PACKAGE_MISSING')
        output['topological_order']=graph['order']
    return {'schema':f'SBL.{kind}SPECDraft@1','status':'DESIGN_CANDIDATE',**output}

def validate_stage(contract, payload, *, formal=False):
    require(contract.get('status')=='DESIGN_PROJECTION','STAGE_CONTRACT_STATUS')
    require(all(payload.get(k) for k in contract['typed_input']),'STAGE_INPUT_MISSING',contract['id'])
    require(SHA.fullmatch(str(payload.get('source_sha256',''))),'STAGE_SOURCE_SHA')
    require(payload['source_sha256']==contract['source_ref']['sha256'],'STAGE_SOURCE_DRIFT')
    if contract['id'].endswith(':T2') and contract['role']=='TPgM':
        affected_work(payload.get('dag',{}),[])
        require(bool(payload.get('dag')),'DAG_EMPTY')
    if contract['stage']=='T5': require(payload.get('raw_refs'),'STAGE_RAW_MISSING')
    if formal:
        raise Refusal('OWNER_STAGE_MAP_RATIFICATION_REQUIRED',contract['id'])
    return {'status':'PASS','output_type':contract['typed_output'],'claim_ceiling':'STAGE_DRAFT_ONLY'}

def donor_route(slot):
    require(slot.get('state') in ('PROVIDER_OFF','EVAL','NOFIT','ADMITTED'),'DONOR_STATE')
    if slot['state']=='ADMITTED':
        require(all(slot.get(k) for k in ('full_sha','license','host_receipt','admission_ref')),'DONOR_ADMISSION_MISSING')
        return {'status':'BLOCKED','first_fail':'TRUSTED_DONOR_ADMISSION_READER_REQUIRED'}
    return {'status':'PASS','runtime_invoked':False,'fallback':'CORE_TPM_DRAFT','external_dependency':False}
