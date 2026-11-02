"""Reproduce original PIPD compatibility without the private DOC Corpus."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from sbl_sp.plugins.tpm_sp.pre_v2 import adapter as a

def main():
    p=argparse.ArgumentParser(); p.add_argument('--pipd-root',type=Path,required=True)
    p.add_argument('--python',default=sys.executable); p.add_argument('--out',type=Path,required=True)
    args=p.parse_args(); root=args.pipd_root.resolve(strict=True); out=args.out.resolve()
    if out.is_relative_to(root): raise SystemExit('output must be outside original Reader tree')
    out.mkdir(parents=True,exist_ok=True)
    source=Path(__file__).resolve().parents[1]/'sbl_sp/plugins/tpm_sp/pre_v2/acceptance-source.txt'
    pins={x.relative_to(root).as_posix():a.sha(x.read_bytes()) for folder,glob in [('src/pipd_ls_sp','*.py'),('schemas','*.json')]
          for x in (root/folder).rglob(glob)}
    reader=a.OriginalPipd(root,args.python,pins); ledger=[]
    def call(name,*argv,allow_failure=False):
        r=reader.invoke(*argv); path=out/(name+'.json'); path.write_text(r['stdout'],encoding='utf-8')
        ledger.append({'name':name,'args':list(map(str,argv)),'exit':r['exit'],'sha256':a.sha(path.read_bytes())})
        if r['exit'] and not allow_failure: raise RuntimeError(name+': original Reader refused')
        return path,json.loads(r['stdout'])
    card,_=call('IntentCard','intake','--goal','Bounded PRE-V2 regression','--source',source)
    pi_path,pi=call('PI','compile-pi','--intent',card,'--profile','LITE')
    cross=a.crosswalk(pi,[source.parent],reader,card,'LITE')
    (out/'PI.crosswalk.json').write_bytes(a.encoded(cross))
    pd_path,pd=call('PD','bind-pd','--pi',pi_path,'--repo-root',Path(__file__).resolve().parents[1])
    ecp_path,ecp=call('ECP','compile-ecp','--pi',pi_path,'--pd',pd_path)
    bundle=out/'bundle.json'; bundle.write_bytes(a.encoded({'PI-PKG':pi,'PD-PKG':pd,'ECP':ecp}))
    _,validation=call('validation','validate','--bundle',bundle)
    _,tq=call('TQAEP-no-receipt','compile-tqaep','--pi',pi_path,'--ecp',ecp_path,allow_failure=True)
    result={'claim_ceiling':'AUTHOR_DESIGN_ONLY','scope':'COMPATIBILITY_FIXTURE_ONLY',
            'validation':validation,'original_tqaep_without_receipt':tq,'commands':ledger,
            'reader_pins':pins,'Host':'NOT_TESTED_BY_THIS_SCRIPT'}
    (out/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'original_validate':validation['verdict'],'closure':validation.get('closure'),
                      'no_receipt':tq.get('code'),'claim_ceiling':'AUTHOR_DESIGN_ONLY'}))
if __name__=='__main__': main()
