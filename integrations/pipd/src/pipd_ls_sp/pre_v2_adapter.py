"""Source-bound design sidecars; canonical records stay with the original PIPD CLI.

This module emits no Grant, checker receipt, queue entry, or Qualified verdict.
Registry pins are supplied by the owning source reader, outside candidate bytes.
Synthetic or owner-unverified registries can establish design consistency only.
"""
from __future__ import annotations
import copy, hashlib, json, os, re, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath

EFFECTS=('SOURCE_READ','LOCAL_DRAFT_WRITE','REPOSITORY_WRITE','HOST_OPERATIONS','USER_DATA_EFFECT','REMOTE_RELEASE')
FORBIDDEN={'checker_execution_receipt','checker_receipt','issuer_token','grant','permit','token','signed_verdict','access_token','password','private_key','maker_self_signed'}
ESCALATIONS={'QUALIFIED','INDEPENDENT_QUALIFIED','INDEPENDENT_PASS','INDEPENDENT_CASE_PASS','USABLE_PASS','RELEASED','EXECUTABLE','HOST_QUALIFIED'}

class Refusal(ValueError): pass
def need(value,code):
    if not value: raise Refusal(code)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(obj): return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def nonempty(x): return isinstance(x,str) and bool(x.strip())
def hash64(x): return isinstance(x,str) and re.fullmatch('[0-9a-f]{64}',x) is not None
def validate_design(name,body):
    from jsonschema import Draft202012Validator
    parent=Path(__file__).resolve().parent
    options=[parent/'schemas'/name,parent/'schemas/pre-v2'/name,parent.parent/'schemas/pre-v2'/name]
    path=next((p for p in options if p.is_file()),None)
    need(path is not None,'SIDECAR_SCHEMA_UNBOUND')
    schema=json.loads(path.read_text(encoding='utf-8'))
    Draft202012Validator.check_schema(schema)
    need(not list(Draft202012Validator(schema).iter_errors(body)),'SIDECAR_SCHEMA_INVALID:'+name)
    return body
def deny_authority(obj):
    if isinstance(obj,dict):
        for key,value in obj.items():
            need(key.casefold() not in FORBIDDEN,'FORBIDDEN_AUTHORITY_KEY:'+key)
            deny_authority(value)
    elif isinstance(obj,list):
        for value in obj: deny_authority(value)
    elif isinstance(obj,str):
        need(obj.upper() not in ESCALATIONS,'FORBIDDEN_DESIGN_CLAIM')
        need(not re.search(r'github_pat_[A-Za-z0-9_]{30,}|gh[pousr]_[A-Za-z0-9]{30,}|-----BEGIN .*PRIVATE KEY',obj),'SECRET_IN_DESIGN')

def relative_scope(value):
    need(nonempty(value) and '\\' not in value and ':' not in value,'SCOPE_INVALID')
    parts=PurePosixPath(value).parts
    need(not PurePosixPath(value).is_absolute() and all(p not in ('.','..') for p in parts)
         and not any(c in value for c in '*?[]') and value.rstrip('/')==value,'SCOPE_ESCAPE_OR_WILDCARD')
    return value

def read(root,relative):
    relative_scope(relative); root=Path(root).resolve(strict=True); cursor=root
    for part in PurePosixPath(relative).parts:
        cursor=cursor/part; st=cursor.lstat()
        need(not cursor.is_symlink() and not getattr(st,'st_file_attributes',0)&0x400,'REPARSE_POINT')
    need(cursor.resolve(strict=True).is_relative_to(root),'PATH_ESCAPE')
    before=cursor.stat(); need(cursor.is_file() and before.st_nlink==1,'HARDLINK_OR_NOT_FILE')
    data=cursor.read_bytes(); after=cursor.stat()
    need((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns)==
         (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns),'SOURCE_RACE')
    return data

def pinned_json(root,path,expected_sha):
    data=read(root,path); need(hash64(expected_sha) and sha(data)==expected_sha,'SOURCE_PIN_MISMATCH')
    return json.loads(data)

def git(root,*args):
    p=subprocess.run(['git','-C',str(root),*args],capture_output=True,timeout=30)
    need(p.returncode==0,'REPO_PROBE_FAILED')
    return p.stdout

def probe_repo(root,scope):
    """Live exact Git root, HEAD, tracked+untracked state and scoped preimages.

    os.access reports process access only; it never proves an HGK effect grant.
    Re-probe before a world write. No receipt string can replace this probe.
    """
    need(isinstance(scope,list) and scope and len(set(scope))==len(scope),'SCOPE_EMPTY_OR_DUPLICATE')
    for path in scope: relative_scope(path)
    if root is None or not Path(root).is_dir():
        return validate_design('PD.binding.schema.json',{'binding_state':'UNBOUND_CANDIDATE','binding_request':{'required':['real Repo root','HEAD','exact scope','currentness probe']},'repo':None})
    root=Path(root).resolve(strict=True)
    top=Path(git(root,'rev-parse','--show-toplevel').decode().strip()).resolve(strict=True)
    need(top==root,'REPO_ROOT_MISMATCH')
    head=git(root,'rev-parse','HEAD').decode().strip()
    need(re.fullmatch('[0-9a-f]{40,64}',head),'HEAD_INVALID')
    branch=git(root,'rev-parse','--abbrev-ref','HEAD').decode().strip()
    status=git(root,'status','--porcelain=v1','-z','--untracked-files=all')
    tracked=git(root,'ls-files','-z').split(b'\0'); tracked=[x for x in tracked if x]
    untracked=git(root,'ls-files','--others','--exclude-standard','-z').split(b'\0')
    images={}
    for rel in scope:
        target=root/rel
        if target.exists(): images[rel]=sha(read(root,rel))
        else:
            # Existing ancestors must also be contained and free of reparses.
            current=root
            for part in PurePosixPath(rel).parts:
                current=current/part
                if current.exists() or current.is_symlink():
                    st=current.lstat(); need(not current.is_symlink() and not getattr(st,'st_file_attributes',0)&0x400,'REPARSE_POINT')
                    need(current.resolve().is_relative_to(root),'PATH_ESCAPE')
            images[rel]='ABSENT'
    state={'root':str(root),'head':head,'branch':branch,'dirty':bool(status),
           'status_sha256':sha(status),'tracked':len(tracked),'untracked':len([x for x in untracked if x]),
           'write_scope':scope,'preimages':images,'process_writable':os.access(root,os.W_OK)}
    return validate_design('PD.binding.schema.json',{'binding_state':'PROBE_OBSERVED','repo':state,'currentness_epoch':sha(encoded(state)),
            'observed_at':datetime.now(timezone.utc).isoformat(),'permission_basis':'PROCESS_ACL_ONLY_NOT_EFFECT_GRANT'})

def require_current(binding):
    need(binding.get('binding_state')=='PROBE_OBSERVED' and isinstance(binding.get('repo'),dict),'REPO_UNBOUND')
    now=probe_repo(binding['repo']['root'],binding['repo']['write_scope'])
    need(binding.get('currentness_epoch')==now['currentness_epoch'] and binding['repo']==now['repo'],'STALE_REPO')
    return now

class OriginalPipd:
    """Thin subprocess bridge, pinned to original code+schemas, using its own CLI.

    Compiler errors are returned unchanged. In particular missing TQAEP receipts
    are never synthesized to make the legacy compiler return success.
    """
    def __init__(self,root,python,pins):
        self.root=Path(root).resolve(strict=True); self.python=str(python); self.pins=dict(pins)
        required={p.relative_to(self.root).as_posix() for folder,glob in [('src/pipd_ls_sp','*.py'),('schemas','*.json')]
                  for p in (self.root/folder).rglob(glob)}
        need(required and set(pins)==required,'ORIGINAL_READER_PIN_SET')
        self.check()
    def check(self):
        for path,digest in self.pins.items(): need(sha(read(self.root,path))==digest,'ORIGINAL_READER_DRIFT')
    def invoke(self,*args):
        need(args and args[0] in ('intake','compile-pi','bind-pd','compile-ecp','compile-tqaep','validate','doctor'),'ORIGINAL_COMMAND_SCOPE')
        self.check()
        env=dict(os.environ,PYTHONPATH=str(self.root/'src'),PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
        p=subprocess.run([self.python,'-B','-m','pipd_ls_sp.cli','--root',str(self.root),*map(str,args)],
                         cwd=self.root,env=env,capture_output=True,timeout=90)
        self.check()
        return {'exit':p.returncode,'stdout':p.stdout.decode('utf-8'),'stderr':p.stderr.decode('utf-8'),
                'reader_pin_sha256':sha(encoded(self.pins))}
    def replay_pi(self,pi,card_path,profile):
        result=self.invoke('compile-pi','--intent',card_path,'--profile',profile)
        need(result['exit']==0,'ORIGINAL_PI_COMPILER_REFUSED')
        expected=json.loads(result['stdout'])
        need(pi==expected,'PI_ORIGINAL_REPLAY_MISMATCH')
        return result

def crosswalk(pi,source_roots,original_reader,card_path,profile):
    """Recover every original atom ID, source/parent/child, polarity and oracle.

    Requires source roots pinned by the caller. Does not ratify their authority.
    Full canonical authenticity is separately checked by OriginalPipd.replay_pi.
    """
    need(isinstance(original_reader,OriginalPipd),'ORIGINAL_READER_UNBOUND')
    original_reader.replay_pi(pi,card_path,profile)
    need(pi.get('schema_version')=='PI-PKG@1','PI_SCHEMA')
    contract=pi.get('stable_semantic_contract',{}); atoms=contract.get('atoms'); table=contract.get('sources',[])
    need(isinstance(atoms,list) and atoms,'PI_EMPTY')
    rows=[]
    for atom in atoms:
        sc=atom.get('source_clause',{}); source=next((s for s in table if s.get('source_id')==sc.get('source_ref')),None)
        need(source is not None and hash64(source.get('sha256')),'SOURCE_REF_UNBOUND')
        file=Path(sc.get('file','')).resolve(strict=True)
        roots=[Path(p).resolve(strict=True) for p in source_roots]
        root=next((r for r in roots if file.is_relative_to(r)),None)
        need(root is not None,'SOURCE_OUTSIDE_AUTHORIZED_ROOT')
        data=read(root,file.relative_to(root).as_posix())
        need(sha(data)==source['sha256'],'SOURCE_SHA_MISMATCH')
        text=data.decode('utf-8'); span=sc.get('span')
        need(isinstance(span,list) and len(span)==2 and all(type(x)==int for x in span)
             and 0<=span[0]<span[1]<=len(text) and text[span[0]:span[1]]==source['text'],'SOURCE_SPAN_MISMATCH')
        rg=atom.get('risk_guard',{}); oracle=rg.get('oracle',{})
        need(nonempty(atom.get('req_id')) and atom['req_id'] not in ('REQ-INTENT','REQ-VERIFY','REQ-KNOWLEDGE','REQ-GOVERN','REQ-DELIVER'),'CATEGORY_AS_ID')
        need(rg.get('polarity') in ('MUST','MUST NOT') and nonempty(oracle.get('id')),'ORACLE_OR_POLARITY_MISSING')
        need(type(sc.get('child'))==int and sc['child']>=0,'CHILD_ID_MISSING')
        rows.append({'original_requirement_id':atom['req_id'],'original_oracle_id':oracle['id'],
                     'source_sha256':source['sha256'],'source_file':str(file),'clause_id':sc['clause_id'],
                     'span':span,'parent_id':sc['source_ref'],'child':sc['child'],
                     'polarity':rg['polarity'],'statement':sc['text'],'oracle_predicate':oracle.get('predicate'),
                     'taxonomy':'ADVISORY_ONLY'})
    need(len({r['original_requirement_id'] for r in rows})==len(rows),'REQUIREMENT_COLLISION')
    return validate_design('PI.crosswalk.schema.json',{'schema':'SBL.PI.Crosswalk@2','canonical_pi_sha256':sha(encoded(pi)),
            'requirements':rows,'claim_ceiling':'AUTHOR_DESIGN_ONLY'})

def registry(root,path,pin,kind):
    obj=pinned_json(root,path,pin); deny_authority(obj)
    need(obj.get('schema')==kind,'REGISTRY_SCHEMA')
    need(obj.get('authority_state') in ('SYNTHETIC_ONLY','SOURCE_BOUND_OWNER_UNVERIFIED'),'REGISTRY_AUTHORITY_NOT_PROVEN')
    return obj

def identity(subject,candidate,scope,host,epoch):
    need(nonempty(subject) and hash64(candidate) and isinstance(scope,list) and scope and len(set(scope))==len(scope),'IDENTITY_INVALID')
    for path in scope: relative_scope(path)
    need(nonempty(host) and nonempty(epoch),'HOST_POLICY_UNBOUND')
    return {'subject_id':subject,'candidate_sha256':candidate,'scope':scope,'host':host,'policy_epoch':epoch}

SPECIFIC={
 'SOURCE_READ':('source_locator','acl_ref','expected_sha256'),
 'LOCAL_DRAFT_WRITE':('sandbox_root','cleanup'),
 'REPOSITORY_WRITE':('repo_binding','postimages','rollback_commit'),
 'HOST_OPERATIONS':('host_id','os_principal','receiver_abi','host_recovery'),
 'USER_DATA_EFFECT':('consent_ref','data_authority','data_scope','compensation'),
 'REMOTE_RELEASE':('publisher','remote_scope','approval_ref','recovery'),
}
READBACK={'SOURCE_READ':'SOURCE_SHA256','LOCAL_DRAFT_WRITE':'DRAFT_DIFF','REPOSITORY_WRITE':'GIT_POSTIMAGE',
          'HOST_OPERATIONS':'HOST_WORLD_RAW','USER_DATA_EFFECT':'DATA_WORLD_RAW','REMOTE_RELEASE':'PUBLISHER_WORLD_RAW'}

def ecp_intent(context,operation,operation_registry,details):
    """OperationType registry determines effect; never inspect a path for effect."""
    deny_authority([context,details,operation_registry])
    need(context==identity(context.get('subject_id'),context.get('candidate_sha256'),context.get('scope'),context.get('host'),context.get('policy_epoch')),'CONTEXT_INVALID')
    need(operation_registry.get('schema')=='SBL.OperationRegistry.Binding@2' and operation_registry.get('authority_state') in ('SYNTHETIC_ONLY','SOURCE_BOUND_OWNER_UNVERIFIED'),'OPERATION_REGISTRY_UNBOUND')
    rows=[r for r in operation_registry.get('operations',[]) if r.get('operation_type')==operation]
    need(len(rows)==1,'OPERATION_TYPE_UNKNOWN_OR_DUPLICATE'); row=rows[0]; effect=row.get('effect_class')
    need(effect in EFFECTS and all(nonempty(row.get(k)) for k in ('operation_id','source_locator','original_consumer','consumer_abi')),'EFFECT_REGISTRY_INCOMPLETE')
    need(isinstance(details,dict) and all(details.get(k) for k in SPECIFIC[effect]),'EFFECT_FIELDS_MISSING:'+effect)
    need(all(nonempty(details.get(k)) for k in ('precondition','expected_postcondition','permission_basis','idempotency_key')),'ECP_CONDITION_PERMISSION_MISSING')
    need(details.get('on_unknown')=='RECONCILE_NO_BLIND_RETRY','UNKNOWN_BLIND_RETRY')
    need(nonempty(details.get('reconcile_reader')),'RECONCILE_READER_UNBOUND')
    if effect=='SOURCE_READ': need(hash64(details['expected_sha256']),'READ_SOURCE_SHA_INVALID')
    if effect=='LOCAL_DRAFT_WRITE':
        sandbox=Path(details['sandbox_root']).resolve(strict=True); need(sandbox.is_dir(),'DRAFT_ROOT_MISSING')
    if effect=='REPOSITORY_WRITE':
        current=require_current(details['repo_binding']); state=current['repo']
        need(set(context['scope'])<=set(state['write_scope']),'ECP_CROSS_SCOPE')
        need(set(details['postimages'])==set(context['scope']) and all(hash64(v) or v=='ABSENT' for v in details['postimages'].values()),'POSTIMAGE_SCOPE')
        need(details['rollback_commit']==state['head'],'ROLLBACK_PREIMAGE_MISMATCH')
    if effect=='HOST_OPERATIONS':
        need(details['host_id']==context['host'],'HOST_MISMATCH')
        need(not re.search(r'\bgit\b',details['host_recovery'],re.I),'HOST_GIT_RECOVERY')
    if effect=='USER_DATA_EFFECT':
        need(details['data_scope']==context['scope'],'DATA_CROSS_SCOPE')
    if effect=='REMOTE_RELEASE':
        need(details['remote_scope']==context['scope'],'RELEASE_CROSS_SCOPE')
    need(details.get('readback_kind')==READBACK[effect],'EFFECT_READBACK_MISMATCH')
    return validate_design('ECP.intent.schema.json',{'schema':'SBL.ECP.INTENT@2',**context,'operation':copy.deepcopy(row),'details':copy.deepcopy(details),
            'effect_state':'EFFECT_UNBOUND','registry_authority':operation_registry['authority_state'],
            'retry_policy':'ACL_BOUNDED_RETRY' if effect=='SOURCE_READ' else 'ISOLATED_DRAFT_REPLAY' if effect=='LOCAL_DRAFT_WRITE' else 'RECONCILE_THEN_ORIGINAL_ISSUER_DECIDES',
            'claim_ceiling':'AUTHOR_DESIGN_ONLY','grant_state':'NOT_GRANTED'})

CASE_FIELDS=('case_id','original_requirement_id','original_oracle_id','clause_id','fuo_id','positive_fixture',
             'negative_fixture','raw_schema','expected_world_raw','evidence_expectation','checker_role','requalify_selector')

def planned_tqaep(context,pi_crosswalk,ecp,case_registry,fixture_root):
    deny_authority([context,pi_crosswalk,ecp,case_registry])
    need(ecp.get('schema')=='SBL.ECP.INTENT@2' and all(ecp.get(k)==v for k,v in context.items()),'PLAN_ECP_SUBJECT_SCOPE_HOST_EPOCH')
    need(case_registry.get('schema')=='SBL.CaseRegistry.Binding@2' and case_registry.get('authority_state') in ('SYNTHETIC_ONLY','SOURCE_BOUND_OWNER_UNVERIFIED'),'CASE_REGISTRY_UNBOUND')
    need(all(case_registry.get(k)==v for k,v in context.items()),'CASE_REGISTRY_CONTEXT_MISMATCH')
    reqs={r['original_requirement_id']:r for r in pi_crosswalk.get('requirements',[])}
    need(reqs,'PLAN_PI_EMPTY')
    required=case_registry.get('required_cases'); fuos=case_registry.get('required_fuo')
    need(isinstance(required,list) and required and len(set(required))==len(required),'REQUIRED_CASES_EMPTY_OR_DUPLICATE')
    need(isinstance(fuos,list) and fuos and len(set(fuos))==len(fuos),'REQUIRED_FUO_EMPTY_OR_DUPLICATE')
    cases=[]
    for row in case_registry.get('cases',[]):
        need(all(nonempty(row.get(k)) for k in CASE_FIELDS),'CASE_REQUIRED_FIELD')
        rid=row['original_requirement_id']; need(rid in reqs,'CASE_REQUIREMENT_UNKNOWN'); req=reqs[rid]
        need(row['original_oracle_id']==req['original_oracle_id'] and row['clause_id']==req['clause_id'],'CASE_ORACLE_CLAUSE_MISMATCH')
        need(row.get('source_sha256')==req['source_sha256'],'CASE_SOURCE_MISMATCH')
        app=row.get('applicability',{})
        need(all(nonempty(app.get(k)) for k in ('host','profile','kind','mode')),'HOST_APPLICABILITY_MISSING')
        need(app['host']==context['host'],'CASE_WRONG_HOST')
        need(row.get('runner_binding')=='RUNNER_UNBOUND','ORIGINAL_RUNNER_RECEIPT_REQUIRED')
        need(nonempty(row.get('runner_owner')),'RUNNER_OWNER_MISSING')
        for key in ('positive_fixture','negative_fixture','raw_schema'):
            ref=row[key]; need(hash64(row.get(key+'_sha256')),'FIXTURE_PIN_MISSING')
            need(sha(read(fixture_root,ref))==row[key+'_sha256'],'FIXTURE_DRIFT')
        need(row['positive_fixture']!=row['negative_fixture'],'POS_NEG_COLLISION')
        cases.append(copy.deepcopy(row))
    need(cases and len({r['case_id'] for r in cases})==len(cases),'CASE_EMPTY_OR_DUPLICATE')
    need(set(r['case_id'] for r in cases)==set(required),'CASE_COVERAGE_GAP')
    need(set(r['fuo_id'] for r in cases)==set(fuos),'FUO_COVERAGE_GAP')
    need(set(r['original_requirement_id'] for r in cases)==set(reqs),'REQUIREMENT_CASE_GAP')
    return validate_design('PlannedTQAEP.schema.json',{'schema':'SBL.PlannedTQAEP@2',**context,'canonical_pi_sha256':pi_crosswalk['canonical_pi_sha256'],
            'required_fuo':fuos,'cases':cases,'planning_state':'PLAN_VALID',
            'runner_state':'RUNNER_UNBOUND','live_acceptance':'NOT_RUN','independent_acceptance':'NOT_GRANTED',
            'claim_ceiling':'AUTHOR_DESIGN_ONLY','source_authority':case_registry['authority_state']})

def package_design(context,artifacts,plan,original_reader):
    deny_authority([context,artifacts,plan])
    need(isinstance(artifacts,dict) and artifacts,'EMPTY_PACKAGE')
    need(all(isinstance(v,dict) and v for v in artifacts.values()),'EMPTY_ARTIFACT')
    need(plan.get('schema')=='SBL.PlannedTQAEP@2' and plan.get('cases'),'EMPTY_PLAN_EVIDENCE')
    validate_design('PlannedTQAEP.schema.json',plan)
    need(all(plan.get(k)==v for k,v in context.items()),'PACKAGE_PLAN_CONTEXT')
    need(isinstance(original_reader,OriginalPipd),'ORIGINAL_READER_HOLD')
    digest=sha(encoded(artifacts)); need(digest==context['candidate_sha256'],'PACKAGE_CANDIDATE_DRIFT')
    pi=artifacts.get('PI-PKG',{})
    need(sha(encoded(pi))==plan['canonical_pi_sha256'],'PACKAGE_PI_PLAN_DRIFT')
    atoms={x['req_id']:x for x in pi.get('stable_semantic_contract',{}).get('atoms',[])}
    need(atoms and {c['original_requirement_id'] for c in plan['cases']}==set(atoms),'PACKAGE_REQUIREMENT_CASE_GAP')
    need(all(c['original_oracle_id']==atoms[c['original_requirement_id']].get('risk_guard',{}).get('oracle',{}).get('id')
             for c in plan['cases']),'PACKAGE_ORACLE_MISMATCH')
    with tempfile.TemporaryDirectory(prefix='sbl-reader-') as td:
        path=Path(td)/'bundle.json'; path.write_bytes(encoded(artifacts))
        reader_result=original_reader.invoke('validate','--bundle',path)
    need(reader_result['exit']==0,'ORIGINAL_READER_REFUSED')
    result=json.loads(reader_result['stdout'])
    need(result.get('verdict')=='PASS' and not result.get('findings') and result.get('checked',0)>0
         and result.get('closure')=='FULL','ORIGINAL_READER_EMPTY_OR_INVALID')
    return {'schema':'SBL.PackageDesign@2',**context,'artifacts_sha256':digest,
            'evidence_expectations':[{'case_id':c['case_id'],'expectation':c['evidence_expectation'],
                                     'state':'EXPECTED_NOT_OBSERVED'} for c in plan['cases']],
            'claim_ceiling':'AUTHOR_DESIGN_ONLY','mission_state':'OPEN','release':'PUBLISHER_REQUIRED'}

def handoff(context,artifacts):
    deny_authority(artifacts)
    need(artifacts and all(isinstance(v,dict) and v for v in artifacts.values()),'HANDOFF_EMPTY')
    return {'schema':'SBL.ReceiverHandoff@2',**context,'artifacts_sha256':sha(encoded(artifacts)),
            'route':['FABRIC_POLICY_CONSUMER','HGK_ORIGINAL_ISSUER_AND_SHAREDSPINE','SBL_ORIGINAL_RECEIVER'],
            'receiver_state':'RECEIVER_UNBOUND','claim_ceiling':'AUTHOR_DESIGN_ONLY',
            'resume_when':['original operation registry bound','original receiver ABI readback','original effect grant if applicable'],
            'checker':'ORIGINAL_PROTECTED_CHECKER_REQUIRED','publisher':'ORIGINAL_PUBLISHER_REQUIRED'}
