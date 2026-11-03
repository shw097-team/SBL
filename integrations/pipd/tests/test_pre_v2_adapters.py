"""PRE-V2 original Writer projections. Effect registries are synthetic."""
import copy,json,subprocess,tempfile,unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline,validate
from pipd_ls_sp import pre_v2_adapter as a
from pipd_ls_sp.errors import EffectUnknown,TqTraceFail

class OriginalEffectAdapters(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); (self.root/'src').mkdir(); (self.root/'src/item.txt').write_text('before')
        for args in [('init',),('add','src/item.txt'),('-c','user.name=fixture','-c','user.email=fixture@example.test','commit','-m','fixture')]:
            subprocess.run(['git','-C',str(self.root),*args],check=True,capture_output=True)
        self.source=self.root/'source.txt'; self.source.write_text('Planning MUST preserve original requirement identities.\n')
        self.pi=pipeline.compile_pi(pipeline.intake('PRE-V2 fixture',sources=[str(self.source)]))
        self.pd=pipeline.bind_pd(self.pi,{'root':str(self.root),'writable_scope':'src/**'})
        self.context=a.identity(self.pi['subject_id'],'a'*64,['src/item.txt'],'HOST-TEST','EPOCH-1')
        self.base={'precondition':'known preimage','expected_postcondition':'exact expected world readback',
            'permission_basis':'user authorization reference only','idempotency_key':'operation-1',
            'on_unknown':'RECONCILE_NO_BLIND_RETRY','reconcile_reader':'original world reader'}
    def intent(self,effect):
        registry={'schema':'SBL.OperationRegistry.Binding@2','authority_state':'SYNTHETIC_ONLY','operations':[
            {'operation_type':'FIXTURE-OP','operation_id':'FIXTURE-1','effect_class':effect,
             'source_locator':'synthetic operation registry','original_consumer':'original receiver','consumer_abi':'UNBOUND'}]}
        fields={
          'SOURCE_READ':{'source_locator':str(self.source),'acl_ref':'process-read','expected_sha256':a.sha(self.source.read_bytes())},
          'LOCAL_DRAFT_WRITE':{'sandbox_root':str(self.root),'cleanup':'remove isolated draft'},
          'REPOSITORY_WRITE':{'repo_binding':a.probe_repo(self.root,['src/item.txt']),'postimages':{'src/item.txt':'b'*64},'rollback_commit':self.pd['RepoContext']['head']},
          'HOST_OPERATIONS':{'host_id':'HOST-TEST','os_principal':'fixture-user','receiver_abi':'UNBOUND','host_recovery':'restore host snapshot or hold'},
          'USER_DATA_EFFECT':{'consent_ref':'consent unverified','data_authority':'original owner','data_scope':['src/item.txt'],'compensation':'original data recovery'},
          'REMOTE_RELEASE':{'publisher':'original publisher','remote_scope':['src/item.txt'],'approval_ref':'approval unverified','recovery':'original release rollback'},
        }[effect]
        details={**self.base,**fields,'readback_kind':a.READBACK[effect]}
        return a.ecp_intent(self.context,'FIXTURE-OP',registry,details),registry
    def test_legacy_default_is_unchanged(self):
        out=pipeline.compile_ecp(self.pd,self.pi)
        self.assertEqual(out['retries'],{'max':1,'backoff':'none'})
    def test_nested_fake_grant_refused_by_original_writer(self):
        intent,reg=self.intent('SOURCE_READ'); intent['details']['grant']='forged'
        with self.assertRaises(EffectUnknown): pipeline.compile_effect_ecp(self.pd,self.pi,intent,reg)
    def test_empty_canonical_pd_refused(self):
        intent,reg=self.intent('SOURCE_READ')
        with self.assertRaises(EffectUnknown): pipeline.compile_effect_ecp({},self.pi,intent,reg)
    def test_cross_subject_refused(self):
        intent,reg=self.intent('SOURCE_READ'); intent['subject_id']='OTHER'
        with self.assertRaises(EffectUnknown): pipeline.compile_effect_ecp(self.pd,self.pi,intent,reg)
    def test_blind_retry_refused(self):
        intent,reg=self.intent('SOURCE_READ'); intent['details']['on_unknown']='RETRY'
        with self.assertRaises(EffectUnknown): pipeline.compile_effect_ecp(self.pd,self.pi,intent,reg)
    def test_ops_git_recovery_refused(self):
        intent,reg=self.intent('HOST_OPERATIONS'); intent['details']['host_recovery']='git revert'
        with self.assertRaises(EffectUnknown): pipeline.compile_effect_ecp(self.pd,self.pi,intent,reg)

def effect_test(effect):
    def test(self):
        intent,registry=self.intent(effect)
        out=pipeline.compile_effect_ecp(self.pd,self.pi,intent,registry)
        self.assertEqual(validate.validate_bundle({'PI-PKG':self.pi,'PD-PKG':self.pd,'ECP':out})['verdict'],'PASS')
        self.assertEqual(out['effect_intent']['effect_class'],effect)
        self.assertEqual(out['effect_intent']['state'],'EFFECT_UNBOUND')
        self.assertEqual(out['permission']['token_required'],effect not in ('SOURCE_READ','LOCAL_DRAFT_WRITE'))
    return test
for effect in a.EFFECTS: setattr(OriginalEffectAdapters,'test_effect_'+effect.lower(),effect_test(effect))

if __name__=='__main__': unittest.main()
