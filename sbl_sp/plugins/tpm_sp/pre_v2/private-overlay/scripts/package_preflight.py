"""Deterministic private package creation; no publication or qualification."""
from pathlib import Path
import hashlib, json, re, sys, zipfile
try:
    from .core import canonical_order, corpus_manifest, read_contained, require
except ImportError:
    from core import canonical_order, corpus_manifest, read_contained, require

FORBIDDEN=('.git','__pycache__','node_modules','.venv')
PATTERNS=[rb'github_pat_[A-Za-z0-9_]{30,}',rb'gh[pousr]_[A-Za-z0-9]{30,}',
          rb'sk-(?:proj-)?[A-Za-z0-9_-]{32,}',rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']

def validate_bom(root, manifest, files):
    """Reject a stale inventory before sealing, excluding the BOM's own bytes."""
    bom=json.loads(read_contained(root,'sbom/manifest.json'))
    require(bom.get('schema')=='SBL.AdmittedEquivalentBOM@1' and
            bom.get('version')==manifest['version'],'BOM_VERSION')
    expected=[{'path':rel,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
              for rel,data in files if rel!='sbom/manifest.json']
    require(bom.get('files')==expected,'BOM_FILE_DRIFT')
def package(root, destination):
    root=Path(root).resolve(strict=True); destination=Path(destination).resolve()
    require(not destination.is_relative_to(root),'ARCHIVE_INSIDE_PACKAGE')
    corpus_manifest(root)
    manifest=json.loads((root/'plugin.json').read_text(encoding='utf-8'))
    compatibility=json.loads((root/'.codex-plugin/plugin.json').read_text(encoding='utf-8'))
    require(manifest['name']==compatibility['name']=='sbl-tpm-sp','MANIFEST_IDENTITY')
    require(manifest['version']==compatibility['version'],'MANIFEST_VERSION')
    require(len(compatibility['interface']['shortDescription'])<=30,'SUBTITLE_LENGTH')
    files=[]; names=[]
    import yaml
    for skill in sorted((root/'skills').glob('*/SKILL.md')):
        raw=skill.read_text(encoding='utf-8')
        require(raw.startswith('---\n'),'SKILL_FRONTMATTER')
        fm=yaml.safe_load(raw.split('---',2)[1])
        require(fm['name']==skill.parent.name and fm.get('description'),'SKILL_METADATA')
        names.append(fm['name'])
    require(len(names)==14 and len(set(names))==14,'SKILL_DENOMINATOR')
    for path in canonical_order(root,[p for p in root.rglob('*') if p.is_file()]):
        rel=path.relative_to(root)
        if any(p in FORBIDDEN for p in rel.parts) or path.suffix=='.pyc': continue
        require(path.suffix.lower() not in ('.db','.sqlite','.pem','.key','.pfx'), 'PRIVATE_RUNTIME_FILE')
        data=read_contained(root,rel.as_posix())
        require(not any(re.search(p,data) for p in PATTERNS),'SECRET_SCAN_FINDING',rel.as_posix())
        files.append((rel.as_posix(),data))
    validate_bom(root,manifest,files)
    destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for rel,data in files:
            info=zipfile.ZipInfo('sbl-tpm-sp/'+rel,date_time=(2026,10,28,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o100644<<16
            archive.writestr(info,data)
    with zipfile.ZipFile(destination) as archive:
        require(archive.testzip() is None,'ZIP_CRC')
        for rel,data in files:
            require(archive.read('sbl-tpm-sp/'+rel)==data,'ZIP_READBACK')
    return {'path':str(destination),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),
            'files':len(files),'skills':len(names),'status':'PACKAGE_CANDIDATE',
            'license':'PRIVATE_ONLY_PENDING_SOURCE_GRANTS','host_qualified':False}

if __name__=='__main__':
    result=package(Path(sys.argv[1]),Path(sys.argv[2]))
    print(json.dumps(result,indent=2))
