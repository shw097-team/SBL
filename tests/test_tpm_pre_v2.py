"""Author-side attacks. Synthetic registries never stand for owner authority."""
import copy,json,subprocess,tempfile,unittest
from pathlib import Path
from sbl_sp.plugins.tpm_sp.pre_v2 import adapter as a

class PreV2Controls(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); (self.root/'pos.json').write_text('{"value":1}')
        (self.root/'neg.json').write_text('{"value":null}')
        (self.root/'raw.json').write_text('{"type":"object"}')
        self.context=a.identity('PRE-V2-SYNTHETIC','a'*64,['src/item.txt'],'HOST-TEST','POLICY-1')
        self.xwalk={'canonical_pi_sha256':'b'*64,'requirements':[
            {'original_requirement_id':'ORIGINAL-1','original_oracle_id':'ORACLE-1','clause_id':'CLAUSE-1','source_sha256':'c'*64}]}
        self.ops={'schema':'SBL.OperationRegistry.Binding@2','authority_state':'SYNTHETIC_ONLY','operations':[
            {'operation_type':'READ_FIXTURE','operation_id':'OP-1','effect_class':'SOURCE_READ','source_locator':'test:operation-1',
             'original_consumer':'ORIGINAL-SOURCE-READER','consumer_abi':'READ-1'}]}
        self.details={'source_locator':'fixture:source','acl_ref':'test-process-acl','expected_sha256':'c'*64,
            'precondition':'source exists','expected_postcondition':'same source hash','permission_basis':'test read ACL',
            'idempotency_key':'read-1','on_unknown':'RECONCILE_NO_BLIND_RETRY','reconcile_reader':'source hash reader',
            'readback_kind':'SOURCE_SHA256'}
        case={'case_id':'CASE-1','original_requirement_id':'ORIGINAL-1','original_oracle_id':'ORACLE-1','clause_id':'CLAUSE-1',
              'fuo_id':'FUO-1','source_sha256':'c'*64,'positive_fixture':'pos.json','negative_fixture':'neg.json','raw_schema':'raw.json',
              'expected_world_raw':'value with exact source hash','evidence_expectation':'same subject/candidate/scope/host/epoch',
              'checker_role':'existing protected checker','requalify_selector':'CASE-1 only',
              'applicability':{'host':'HOST-TEST','profile':'LITE','kind':'SKILL_PLUGIN','mode':'DESIGN'},
              'runner_binding':'RUNNER_UNBOUND','runner_owner':'original runner owner'}
        for key in ('positive_fixture','negative_fixture','raw_schema'): case[key+'_sha256']=a.sha((self.root/case[key]).read_bytes())
        self.cases={'schema':'SBL.CaseRegistry.Binding@2','authority_state':'SYNTHETIC_ONLY',**self.context,
                    'required_cases':['CASE-1'],'required_fuo':['FUO-1'],'cases':[case]}

    def effect(self): return a.ecp_intent(self.context,'READ_FIXTURE',self.ops,self.details)
    def plan(self): return a.planned_tqaep(self.context,self.xwalk,self.effect(),self.cases,self.root)
    def refuse(self,code,fn,*args):
        with self.assertRaisesRegex(a.Refusal,code): fn(*args)
    def gitrepo(self):
        root=self.root/'repo'; root.mkdir(); (root/'src').mkdir(); (root/'src/item.txt').write_text('before')
        for args in [('init',),('add','src/item.txt'),('-c','user.name=fixture','-c','user.email=fixture@example.test','commit','-m','fixture')]:
            subprocess.run(['git','-C',str(root),*args],check=True,capture_output=True)
        return root

    def test_receipt_free_plan_is_not_qualification(self):
        plan=self.plan(); self.assertEqual(plan['planning_state'],'PLAN_VALID')
        self.assertEqual(plan['independent_acceptance'],'NOT_GRANTED'); self.assertEqual(plan['runner_state'],'RUNNER_UNBOUND')
        self.assertEqual(plan['source_authority'],'SYNTHETIC_ONLY')
    def test_nested_checker_receipt(self):
        self.cases['cases'][0]['nested']={'checker_execution_receipt':'fake'}
        self.refuse('FORBIDDEN_AUTHORITY_KEY',self.plan)
    def test_fake_grant(self):
        self.details['grant']='forged'; self.refuse('FORBIDDEN_AUTHORITY_KEY',self.effect)
    def test_fake_qualified(self):
        self.cases['cases'][0]['claim']='QUALIFIED'; self.refuse('FORBIDDEN_DESIGN_CLAIM',self.plan)
    def test_empty_requirements(self):
        self.xwalk['requirements']=[]; self.refuse('PLAN_PI_EMPTY',self.plan)
    def test_empty_cases(self):
        self.cases['cases']=[]; self.refuse('CASE_EMPTY_OR_DUPLICATE',self.plan)
    def test_empty_required_fuo(self):
        self.cases['required_fuo']=[]; self.refuse('REQUIRED_FUO',self.plan)
    def test_duplicate_cases(self):
        self.cases['cases']*=2; self.refuse('CASE_EMPTY_OR_DUPLICATE',self.plan)
    def test_missing_negative(self):
        del self.cases['cases'][0]['negative_fixture']; self.refuse('CASE_REQUIRED_FIELD',self.plan)
    def test_fake_oracle(self):
        self.cases['cases'][0]['original_oracle_id']='forged'; self.refuse('CASE_ORACLE_CLAUSE_MISMATCH',self.plan)
    def test_fake_source(self):
        self.cases['cases'][0]['source_sha256']='d'*64; self.refuse('CASE_SOURCE_MISMATCH',self.plan)
    def test_fake_fuo(self):
        self.cases['cases'][0]['fuo_id']='forged'; self.refuse('FUO_COVERAGE_GAP',self.plan)
    def test_required_case_omission(self):
        self.cases['required_cases'].append('CASE-2'); self.refuse('CASE_COVERAGE_GAP',self.plan)
    def test_requirement_without_case(self):
        self.xwalk['requirements'].append({**self.xwalk['requirements'][0],'original_requirement_id':'ORIGINAL-2'})
        self.refuse('REQUIREMENT_CASE_GAP',self.plan)
    def test_wrong_case_host(self):
        self.cases['cases'][0]['applicability']['host']='OTHER'; self.refuse('CASE_WRONG_HOST',self.plan)
    def test_wrong_candidate(self):
        self.cases['candidate_sha256']='d'*64; self.refuse('CASE_REGISTRY_CONTEXT_MISMATCH',self.plan)
    def test_wrong_scope(self):
        self.cases['scope']=['elsewhere']; self.refuse('CASE_REGISTRY_CONTEXT_MISMATCH',self.plan)
    def test_wrong_policy(self):
        self.cases['policy_epoch']='POLICY-2'; self.refuse('CASE_REGISTRY_CONTEXT_MISMATCH',self.plan)
    def test_forged_runner_binding(self):
        self.cases['cases'][0]['runner_binding']='RUNNER_BOUND'; self.refuse('ORIGINAL_RUNNER_RECEIPT_REQUIRED',self.plan)
    def test_missing_fixture_bytes(self):
        (self.root/'neg.json').unlink()
        with self.assertRaises(OSError): self.plan()
    def test_fixture_drift(self):
        (self.root/'pos.json').write_text('{}'); self.refuse('FIXTURE_DRIFT',self.plan)
    def test_fixture_path_escape(self):
        self.cases['cases'][0]['negative_fixture']='../neg.json'; self.refuse('SCOPE_ESCAPE',self.plan)
    def test_unknown_blind_retry(self):
        self.details['on_unknown']='RETRY'; self.refuse('UNKNOWN_BLIND_RETRY',self.effect)
    def test_unknown_operation(self): self.refuse('OPERATION_TYPE_UNKNOWN',a.ecp_intent,self.context,'GUESS_PATH',self.ops,self.details)
    def test_same_operation_has_no_path_effect_guessing(self):
        for path in ('relative/source','C:/source','//server/share/source'):
            self.details['source_locator']=path
            self.assertEqual(self.effect()['operation']['effect_class'],'SOURCE_READ')
    def test_source_read_does_not_require_ops_token(self):
        self.assertEqual(self.effect()['retry_policy'],'ACL_BOUNDED_RETRY')
    def test_cross_effect_readback(self):
        self.details['readback_kind']='HOST_WORLD_RAW'; self.refuse('EFFECT_READBACK_MISMATCH',self.effect)
    def test_unbound_repo_is_explicit(self):
        self.assertEqual(a.probe_repo(None,['src/item.txt'])['binding_state'],'UNBOUND_CANDIDATE')
    def test_real_repo_stale_preimage_and_head(self):
        root=self.gitrepo(); binding=a.probe_repo(root,['src/item.txt']); a.require_current(binding)
        (root/'src/item.txt').write_text('after'); self.refuse('STALE_REPO',a.require_current,binding)
    def test_fake_head(self):
        root=self.gitrepo(); binding=a.probe_repo(root,['src/item.txt']); binding['repo']['head']='0'*40
        self.refuse('STALE_REPO',a.require_current,binding)
    def test_untracked_state_change(self):
        root=self.gitrepo(); binding=a.probe_repo(root,['src/item.txt']); (root/'new.txt').write_text('new')
        self.refuse('STALE_REPO',a.require_current,binding)
    def test_repo_root_subdirectory_refused(self):
        root=self.gitrepo(); self.refuse('REPO_ROOT_MISMATCH',a.probe_repo,root/'src',['item.txt'])
    def test_empty_package(self): self.refuse('EMPTY_PACKAGE',a.package_design,self.context,{},self.plan(),{})
    def test_fake_reader_receipt_refused(self):
        artifacts={'PI':{'synthetic':True}}; self.context['candidate_sha256']=a.sha(a.encoded(artifacts))
        self.cases['candidate_sha256']=self.context['candidate_sha256']
        self.refuse('ORIGINAL_READER_HOLD',a.package_design,self.context,artifacts,self.plan(),{'exit':0,'stdout':'synthetic','reader_pin_sha256':'c'*64})
    def test_empty_reader_result(self): self.refuse('ORIGINAL_READER_HOLD',a.package_design,self.context,{'PI':{'synthetic':True}},self.plan(),{})
    def test_handoff_has_original_route_without_queue(self):
        out=a.handoff(self.context,{'PI':{'synthetic':True}})
        self.assertEqual(out['receiver_state'],'RECEIVER_UNBOUND'); self.assertEqual(len(out['route']),3)
    def test_source_pin_tamper(self):
        path=self.root/'registry.json'; path.write_bytes(a.encoded(self.ops)); digest=a.sha(path.read_bytes())
        a.registry(self.root,'registry.json',digest,'SBL.OperationRegistry.Binding@2')
        path.write_text('{}'); self.refuse('SOURCE_PIN_MISMATCH',a.registry,self.root,'registry.json',digest,'SBL.OperationRegistry.Binding@2')
    def test_claimed_registry_authority_refused(self):
        self.ops['authority_state']='RATIFIED'; self.refuse('OPERATION_REGISTRY_UNBOUND',self.effect)
    def test_original_reader_is_required_for_crosswalk(self):
        self.refuse('ORIGINAL_READER_UNBOUND',a.crosswalk,{},[],None,None,'LITE')

def _path_test(value):
    def test(self): self.refuse('SCOPE_',a.relative_scope,value)
    return test
for index,value in enumerate(('../escape','C:/absolute','//unc/share','*','src/**','a\\b','a:stream','/absolute')):
    setattr(PreV2Controls,f'test_scope_attack_{index:02d}',_path_test(value))

if __name__=='__main__': unittest.main()
