from pathlib import Path
import hashlib,json
import sys
P=Path(sys.argv[1]).resolve(strict=True)
path=P/'sbom/manifest.json'; old=json.loads(path.read_text(encoding='utf-8'))
old['version']=json.loads((P/'plugin.json').read_text(encoding='utf-8'))['version']
old['files']=[]
for file in sorted(P.rglob('*')):
    if not file.is_file(): continue
    rel=file.relative_to(P)
    if any(x in ('.git','__pycache__','node_modules','.venv') for x in rel.parts) or file.suffix=='.pyc' or rel.as_posix()=='sbom/manifest.json': continue
    raw=file.read_bytes(); old['files'].append({'path':rel.as_posix(),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
for component in old.get('components',[]):
    if component.get('name')=='installed PIPD P4':
        component['license']='Apache-2.0_SOURCE_OWNER_ENGINEERING_GRANT'; component['license_conflict']='historical proprietary position superseded; raw DOC rights not asserted'
old['self_inventory_rule']='BOM excludes its own bytes; archive receipt pins the complete ZIP'
path.write_text(json.dumps(old,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated exact private BOM:',old['version'],len(old['files']),'files')
