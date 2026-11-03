"""Original receipt-free Sidecar reader rejects source/authority substitutions."""
import copy,json,subprocess,tempfile,unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from pipd_ls_sp import pipeline,pre_v2_adapter as a
from pipd_ls_sp.errors import TqTraceFail

class PlannedReader(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(); cls.root=Path(cls.tmp.name)
        source=cls.root/'source.txt'; source.write_text('Planning MUST preserve requirement identity.\n')
        card=pipeline.intake('PRE-V2 fixture',sources=[str(source)]); cls.pi=pipeline.compile_pi(card)
        # A real repo is required for this demonstration.
        for args in [('init',),('add','source.txt'),('-c','user.name=fixture','-c','user.email=fixture@example.test','commit','-m','fixture')]:
            subprocess.run(['git','-C',str(cls.root),*args],check=True,capture_output=True)
        cls.pd=pipeline.bind_pd(cls.pi,{'root':str(cls.root),'writable_scope':'src/**'})
        cls.ecp=pipeline.compile_ecp(cls.pd,cls.pi)
        atom=cls.pi['stable_semantic_contract']['atoms'][0]
        clause=pipeline.req_compile.resolve_source_clause(atom,cls.pi['stable_semantic_contract']['sources'])
        context=a.identity(cls.pi['subject_id'],a.sha(a.encoded({'PI-PKG':cls.pi,'PD-PKG':cls.pd,'ECP':cls.ecp})),['source.txt'],'HOST-TEST','EPOCH-1')
        case={'case_id':'SYNTHETIC-1','original_requirement_id':atom['req_id'],'original_oracle_id':atom['risk_guard']['oracle']['id'],
              'clause_id':clause['clause_id'],'source_sha256':clause['source_sha256'],'fuo_id':'SYNTHETIC-FUO',
              'positive_fixture':'pos.json','negative_fixture':'neg.json','raw_schema':'raw.json',
              'expected_world_raw':'original runner observation','evidence_expectation':'same exact context',
              'checker_role':'original protected checker','requalify_selector':'SYNTHETIC-1','runner_owner':'original runner owner',
              'applicability':{'host':'HOST-TEST','profile':'LITE','kind':'SKILL_PLUGIN','mode':'DESIGN'},'runner_binding':'RUNNER_UNBOUND'}
        for key in ('positive_fixture','negative_fixture','raw_schema'):
            path=cls.root/case[key]; path.write_text('{"synthetic":"'+key+'"}')
            case[key+'_sha256']=a.sha(path.read_bytes())
        cls.plan={'schema':'SBL.PlannedTQAEP@2',**context,'canonical_pi_sha256':a.sha(a.encoded(cls.pi)),
                  'required_fuo':['SYNTHETIC-FUO'],'cases':[case],'planning_state':'PLAN_VALID',
                  'runner_state':'RUNNER_UNBOUND','live_acceptance':'NOT_RUN','independent_acceptance':'NOT_GRANTED',
                  'claim_ceiling':'AUTHOR_DESIGN_ONLY','source_authority':'SYNTHETIC_ONLY'}
    @classmethod
    def tearDownClass(cls): cls.tmp.cleanup()
    def test_receipt_free_plan_accepted_without_live_claim(self):
        out=pipeline.read_planned_tqaep(self.pi,self.pd,self.ecp,self.plan,self.root)
        self.assertEqual(out['independent_acceptance'],'NOT_GRANTED')
    def attack(self,mutate):
        plan=copy.deepcopy(self.plan); mutate(plan)
        with self.assertRaises(TqTraceFail): pipeline.read_planned_tqaep(self.pi,self.pd,self.ecp,plan,self.root)
    def test_fake_oracle(self): self.attack(lambda p:p['cases'][0].update(original_oracle_id='FORGED'))
    def test_nested_receipt(self): self.attack(lambda p:p['cases'][0].update(checker_execution_receipt='FORGED'))
    def test_false_qualified(self): self.attack(lambda p:p.update(claim_ceiling='QUALIFIED'))
    def test_wrong_candidate(self): self.attack(lambda p:p.update(candidate_sha256='0'*64))
    def test_wrong_host(self): self.attack(lambda p:p['cases'][0]['applicability'].update(host='OTHER'))
    def test_missing_negative(self): self.attack(lambda p:p['cases'][0].pop('negative_fixture'))
    def test_empty_cases(self): self.attack(lambda p:p.update(cases=[]))
    def test_empty_pd(self):
        with self.assertRaises(TqTraceFail): pipeline.read_planned_tqaep(self.pi,{},self.ecp,self.plan,self.root)
    def test_empty_ecp(self):
        with self.assertRaises(TqTraceFail): pipeline.read_planned_tqaep(self.pi,self.pd,{},self.plan,self.root)
    def test_source_drift(self):
        source=self.root/'source.txt'; original=source.read_bytes()
        try:
            source.write_text('Changed source.')
            with self.assertRaises(TqTraceFail): pipeline.read_planned_tqaep(self.pi,self.pd,self.ecp,self.plan,self.root)
        finally: source.write_bytes(original)
    def test_fixture_drift(self):
        path=self.root/'pos.json'; original=path.read_bytes()
        try:
            path.write_text('{}')
            with self.assertRaises(TqTraceFail): pipeline.read_planned_tqaep(self.pi,self.pd,self.ecp,self.plan,self.root)
        finally: path.write_bytes(original)
    def test_missing_negative_bytes(self):
        path=self.root/'neg.json'; original=path.read_bytes()
        try:
            path.unlink()
            with self.assertRaises(TqTraceFail): pipeline.read_planned_tqaep(self.pi,self.pd,self.ecp,self.plan,self.root)
        finally: path.write_bytes(original)

if __name__=='__main__': unittest.main()
