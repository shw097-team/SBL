import copy, json, tempfile, unittest
from pathlib import Path
from sbl_tpm_adapters import *

class ExtendedTests(unittest.TestCase):
    def test_graph_resolves_actual_objects_with_pinned_catalog(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); objects=[]
            for value in ('A','B'):
                body={'value':value}; h=json_digest(body)
                objects.append(dict(body,subject_id='ATOM-'+h[:16],content_hash=h,version='1',schema_version='RequirementAtom@1'))
            body={'goal':'two atoms'}; h=json_digest(body)
            parent=dict(body,subject_id='PI-'+h[:16],content_hash=h,version='1',schema_version='PI-PKG@1')
            parent['trace']=[{'from_id':parent['subject_id'],'from_hash':h,'from_type':'PI-PKG',
                'to_id':o['subject_id'],'to_hash':o['content_hash'],'to_type':'RequirementAtom'} for o in objects]
            objects.append(parent); catalog={'schema':'SBL.ArtifactCatalog@1','encoding':'pipd-python-json@1','records':[]}
            for i,obj in enumerate(objects):
                raw=json.dumps(obj).encode(); (root/f'{i}.json').write_bytes(raw)
                catalog['records'].append({'subject_id':obj['subject_id'],'content_hash':obj['content_hash'],
                    'path':f'{i}.json','file_sha256':digest(raw),'version':'1','schema_version':obj['schema_version'],'currentness':'CURRENT'})
            raw=json.dumps(catalog).encode(); (root/'catalog.json').write_bytes(raw)
            resolver=ArtifactResolver(root,'catalog.json',digest(raw))
            self.assertEqual(resolver.graph([parent],2)['edges'],2)
            with self.assertRaisesRegex(Refusal,'GRAPH_EDGE_COUNT'): resolver.graph([parent],0)
            catalog['records'][0]['currentness']='STALE'
            raw=json.dumps(catalog).encode(); (root/'catalog.json').write_bytes(raw)
            stale=ArtifactResolver(root,'catalog.json',digest(raw))
            with self.assertRaisesRegex(Refusal,'STALE_ARTIFACT'): stale.graph([parent],2)

    def test_three_real_spec_drafts_and_negative_cases(self):
        base={'source_sha256':'a'*64,'source_refs':['source://owner'],'goal':'bounded outcome',
              'non_goals':['no remote effect'],'acceptance':[{'requirement':'r1','positive':'observable result',
                'negative':'reject wrong subject','oracle_ref':'owner://oracle'}]}
        variants={'Product':{'persona':'maintainer','jtbd':'manage todo records','fuo':'add list delete'},
                  'Architecture':{'adr':[{'option':'single reader','tradeoff':'external formal gate'}],
                    'ownership_seams':[{'writers':['existing PIPD'],'readers':['adapter']}],
                    'abi_version':'1','risk':{'unknown':'owner hold'}},
                  'Program':{'dag':{'A':[],'B':['A']},'owners':{'A':'owner','B':'owner'},
                    'work_packages':{'A':'source','B':'candidate'},'resume_predicate':'fresh evidence'}}
        for kind,values in variants.items():
            d={**copy.deepcopy(base),**values}
            self.assertEqual(plan_spec(kind,d)['status'],'DESIGN_CANDIDATE')
            d['acceptance'][0].pop('negative')
            with self.assertRaisesRegex(Refusal,'SPEC_ACCEPTANCE_ORPHAN'): plan_spec(kind,d)
        d={**base,**variants['Architecture']}; d['ownership_seams']=[{'writers':['PIPD','shadow']}]
        with self.assertRaisesRegex(Refusal,'ONE_WRITER_PER_SEAM'): plan_spec('Architecture',d)

    def test_risk_projection_retains_all_twelve_facts(self):
        d={'schema':'SBL.RiskMapping@1','requested_profile':'LITE','target':'SKILL_PLUGIN',
           'provider_off_required':False,'source_ref':'DOC06',
           'scores':{a:{'score':0,'rationale':'observable','evidence_refs':['fixture']} for a in RISK_AXES}}
        low=risk_mapping(d); self.assertEqual(low['context_axes'],['intent','profile'])
        d['scores']['data_sensitivity']['score']=2
        d['scores']['side_effect_risk']['score']=2
        high=risk_mapping(d)
        self.assertEqual(high['effective_profile_candidate'],'ASSURED')
        self.assertEqual(len(high['source_scores']),12)
        self.assertIn('knowledge',high['context_axes'])
        self.assertEqual(high['formal_profile_state'],'HOLD_FOR_PROFILE_OWNER')

if __name__=='__main__': unittest.main()
