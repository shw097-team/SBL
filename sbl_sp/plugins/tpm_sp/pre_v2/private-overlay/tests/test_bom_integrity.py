import hashlib,json,tempfile,unittest
from pathlib import Path
from scripts.package_preflight import validate_bom
from scripts.core import Refusal

class BOMIntegrity(unittest.TestCase):
    def test_exact_inventory_and_version_then_stale_bytes_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'sbom').mkdir(); raw=b'candidate'
            bom={'schema':'SBL.AdmittedEquivalentBOM@1','version':'0.3.0-rc.1',
                 'files':[{'path':'candidate.txt','sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}]}
            (root/'sbom/manifest.json').write_text(json.dumps(bom),encoding='utf-8')
            validate_bom(root,{'version':'0.3.0-rc.1'},[('candidate.txt',raw)])
            with self.assertRaisesRegex(Refusal,'BOM_FILE_DRIFT'):
                validate_bom(root,{'version':'0.3.0-rc.1'},[('candidate.txt',b'changed')])
    def test_wrong_version_and_unlisted_file_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'sbom').mkdir()
            (root/'sbom/manifest.json').write_text(json.dumps({'schema':'SBL.AdmittedEquivalentBOM@1',
                'version':'0.2.0rc1','files':[]}),encoding='utf-8')
            with self.assertRaisesRegex(Refusal,'BOM_VERSION'):
                validate_bom(root,{'version':'0.3.0-rc.1'},[('extra.txt',b'extra')])
