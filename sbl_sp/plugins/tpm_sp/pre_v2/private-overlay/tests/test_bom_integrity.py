import hashlib,json,tempfile,unittest
from pathlib import Path
from scripts.package_preflight import validate_bom
from scripts.core import Refusal, canonical_order

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

    def test_inventory_order_is_platform_independent(self):
        # BUG-BOM-ORDER: Path ordering is casefolded on Windows and byte-ordered on
        # POSIX, so a BOM built on one host failed validate_bom on the other. The
        # canonical key must yield casefold order on every OS.
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for name in ('B.txt','a.txt','C.txt','d/x.txt'):
                p=root/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(b'x')
            got=[p.relative_to(root).as_posix()
                 for p in canonical_order(root,[p for p in root.rglob('*') if p.is_file()])]
            self.assertEqual(got,['a.txt','B.txt','C.txt','d/x.txt'])

    def test_inventory_duplicate_path_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); (root/'a.txt').write_bytes(b'x')
            with self.assertRaisesRegex(Refusal,'DUPLICATE_PATH'):
                canonical_order(root,[root/'a.txt',root/'a.txt'])
