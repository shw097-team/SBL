from pathlib import Path
import os,sys,json,subprocess,hashlib
sys.dont_write_bytecode=True
W=Path('C:/Projects/Agent_Workspace'); R=W/'_r14_packet/raw'; S=R/'ts23_sandbox'; repo=S/'SBL'
sys.path.insert(0,str(repo))
from sbl_core.m04_bridge import GovernedBuildBridge,bind_repo_context
from sbl_core.dto import WriteSet
from sbl_core.errors import SBLError
bridge=GovernedBuildBridge(); order=bridge.prepare(bind_repo_context(str(repo)),WriteSet(('ts23_programs','ts23_tests')))
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PIP_DISABLE_PIP_VERSION_CHECK='1',PIP_CACHE_DIR=str(S/'pip_cache'),TEMP=str(S/'tmp'),TMP=str(S/'tmp'))
(S/'tmp').mkdir(exist_ok=True)
receipts=[]; failures=[]
def dump(p,o): p.write_text(json.dumps(o,indent=2),encoding='utf-8')
def write(path,text):
 global order
 order=bridge.apply(order,path,text)
def run(args,label,env=None,cwd=None):
 p=subprocess.run([str(a) for a in args],capture_output=True,text=True,encoding='utf-8',errors='replace',env=env or ENV,cwd=cwd or S,timeout=180)
 row={'label':label,'argv':[str(a) for a in args],'cwd':str(cwd or S),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 receipts.append(row); dump(R/'ts23_commands.json',receipts)
 if p.returncode: failures.append(row)
 print(json.dumps(row),flush=True); return row
# Real native bridge negative control: no write is attempted outside the declared scope.
try: bridge.apply(order,'outside_scope.py','blocked')
except SBLError as e:
 assert e.code=='SBL_E_WRITE_OUTSIDE_WRITESET'; guard={'rejected':True,'error':e.code}
else: raise AssertionError('bridge did not refuse outside scope')
queue=S/'workspace_queue.json'; queue.write_text(json.dumps([str(W/'SBL/README.md'),str(W/'PIPD/skills/pipd-pi-compile/schemas/output.schema.json'),str(W/'HG-KSEOS/scripts/pi_compile_h0.py')],indent=2),encoding='utf-8')
fixture=repo/'ts23_tests/headings.md'
write('ts23_tests/headings.md','# One\nbody\n## Two\n### Three\n')
common='''import unittest,sys,subprocess,json,os,hashlib
from pathlib import Path
class Behavior(unittest.TestCase):
 def invoke(self,*args):
  return subprocess.run([sys.executable,'-m',os.environ['TS23_MODULE'],*map(str,args)],capture_output=True,text=True,encoding='utf-8')
'''
tests={
 'CLI_TOOL':common+''' def test_census_and_missing_input(self):
  p=Path(os.environ['TS23_FIXTURE']); data=p.read_bytes()
  self.assertIn(b'\\n',data,'fixture must contain LF'); self.assertNotIn(b'\\r',data,'fixture must not contain CR')
  got=self.invoke(p)
  self.assertEqual(got.returncode,0,got.stderr)
  self.assertTrue(got.stdout.strip(),'program produced no output')
  self.assertEqual(json.loads(got.stdout),{'path':str(p.resolve()),'bytes':len(data),'newlines':data.count(b'\\n')+data.count(b'\\r')-data.count(b'\\r\\n'),'sha256':hashlib.sha256(data).hexdigest()})
  empty=p.with_name('ts23-empty-input'); empty.write_bytes(b'')
  got2=self.invoke(empty); self.assertEqual(got2.returncode,0,got2.stderr)
  self.assertEqual(json.loads(got2.stdout),{'path':str(empty.resolve()),'bytes':0,'newlines':0,'sha256':hashlib.sha256(b'').hexdigest()})
  import hashlib as _h
  crlf=p.with_name('ts23-crlf-input.md'); crlf.write_bytes(b'alpha\\r\\nbeta\\r\\ngamma\\r\\n')
  self.assertIn(b'\\r',crlf.read_bytes(),'fixture must really contain CR')
  got3=json.loads(self.invoke(crlf).stdout)
  self.assertEqual(got3['bytes'],crlf.stat().st_size)
  self.assertEqual(got3['newlines'],crlf.read_bytes().count(b'\\n'))
  self.assertEqual(got3['sha256'],_h.sha256(crlf.read_bytes()).hexdigest())
  lone=p.with_name('ts23-lone-cr-input.md'); lone.write_bytes(b'alpha\\rbeta\\rgamma\\r')
  self.assertIn(b'\\r',lone.read_bytes()); self.assertNotIn(b'\\n',lone.read_bytes())
  gotl=json.loads(self.invoke(lone).stdout)
  self.assertEqual(gotl['newlines'],3,'a lone CR is a line terminator')
  unterminated=p.with_name('ts23-unterminated-input.md'); unterminated.write_bytes(b'alpha\\nbeta')
  self.assertFalse(unterminated.read_bytes().endswith((b'\\n',b'\\r')),'fixture must not end with a terminator')
  gotu=json.loads(self.invoke(unterminated).stdout)
  self.assertEqual(gotu['newlines'],1,'only the terminator counts, the last partial line does not')
  self.assertEqual(gotu['bytes'],unterminated.stat().st_size)
  pair=p.with_name('ts23-lfcr-pair.md'); pair.write_bytes(b'a\\n\\rb')
  self.assertEqual(pair.read_bytes().count(b'\\n'),1); self.assertEqual(pair.read_bytes().count(b'\\r'),1)
  self.assertNotIn(b'\\r\\n',pair.read_bytes(),'the pair must not be a CRLF')
  self.assertEqual(json.loads(self.invoke(pair).stdout)['newlines'],2,'LF then CR is two terminators')
  only=p.with_name('ts23-terminators-only.md'); only.write_bytes(b'\\r\\n\\r\\n\\n\\r')
  self.assertEqual(only.read_bytes().strip(b'\\r\\n'),b'','fixture must contain nothing but terminators')
  self.assertEqual(json.loads(self.invoke(only).stdout)['newlines'],4,'three terminators plus one more')
  bom=p.with_name('ts23-bom.md'); bom.write_bytes(b'\\xef\\xbb\\xbf# Title\\n')
  self.assertTrue(bom.read_bytes().startswith(b'\\xef\\xbb\\xbf'),'fixture must start with a BOM')
  b=json.loads(self.invoke(bom).stdout)
  self.assertEqual((b['bytes'],b['newlines']),(bom.stat().st_size,1),'a BOM is bytes, not something to strip')
  binary=p.with_name('ts23-binary.bin'); binary.write_bytes(b'\\xff\\xfea\\n')
  before=_h.sha256(binary.read_bytes()).hexdigest()
  bd=json.loads(self.invoke(binary).stdout)
  self.assertEqual(bd['sha256'],before,'invalid UTF-8 must not be decoded')
  self.assertEqual(_h.sha256(binary.read_bytes()).hexdigest(),before,'the census must not rewrite its input')
  bad=self.invoke(p.with_name('nonexistent-cli-input'))
  self.assertEqual(bad.returncode,2,'an input error must exit 2')
  self.assertEqual(bad.stdout,'','an input error must write nothing to stdout')
  self.assertNotEqual(bad.returncode,0); self.assertIn('ERR_INPUT',bad.stderr)
if __name__=='__main__': unittest.main(verbosity=2)
''',
 'AGENT_SKILL':common+''' def test_heading_inventory_and_bundle(self):
  p=Path(os.environ['TS23_FIXTURE']); got=self.invoke(p)
  self.assertEqual(got.returncode,0,got.stderr)
  self.assertTrue(got.stdout.strip(),'program produced no output')
  self.assertEqual(json.loads(got.stdout)['headings'],[{'line':1,'level':1,'text':'One'},{'line':3,'level':2,'text':'Two'},{'line':4,'level':3,'text':'Three'}])
  import importlib.resources
  doc=importlib.resources.files('ts23_headings').joinpath('SKILL.md').read_text(encoding='utf-8')
  self.assertIn('name: ts23-heading-inventory',doc); self.assertIn('ts23-headings',doc)
  second=p.with_name('ts23-headings-second.md'); second.write_text('# Alpha\\n\\ntext\\n\\n## Beta ##\\n## 知識庫 heading\\n## Cafe\\u0301\\n## tag#\\n### Gamma\\n#### Delta\\n##### Epsilon\\n###### Six\\n####### Seven\\n',encoding='utf-8')
  raw=second.read_text(encoding='utf-8')
  self.assertIn('Cafe\\u0301',raw,'fixture must contain a decomposed sequence')
  self.assertIn('## tag#',raw,'fixture must contain a bare trailing hash with no closing sequence')
  self.assertIn('###### Six',raw,'fixture must contain a level-six heading')
  edge=p.with_name('ts23-headings-edge.md'); edge.write_text('#NoSpace\\n##	Tabbed\\n##   two  spaces   \\n## \\n```\\n## InFence\\n```\\n## ① circle\\n',encoding='utf-8')
  re_=edge.read_text(encoding='utf-8')
  self.assertIn('```',re_,'fixture must contain a fence')
  self.assertIn('##	Tabbed',re_,'fixture must contain a tab separator')
  texts=[h['text'] for h in json.loads(self.invoke(edge).stdout)['headings']]
  self.assertNotIn('NoSpace',texts,'a heading needs a separator')
  self.assertIn('Tabbed',texts,'a tab is a valid separator')
  self.assertIn('two  spaces',texts,'internal spaces are preserved, only the ends are trimmed')
  self.assertNotIn('',texts,'an empty heading text is not a heading')
  self.assertIn('InFence',texts,'fenced headings are still reported: fences are out of scope')
  self.assertIn('① circle',texts,'no Unicode normalisation')
  got2=json.loads(self.invoke(second).stdout)
  expect=[{'line':i+1,'level':len(l)-len(l.lstrip('#')),'text':l.lstrip('#').strip()} for i,l in enumerate(second.read_text(encoding='utf-8').splitlines()) if 1<=len(l)-len(l.lstrip('#'))<=6]
  import re as _re
  for h in expect:
   h['text']=_re.sub(r'[ \\t]+#+$','',h['text']).strip()
  self.assertNotIn('Seven',[h['text'] for h in got2['headings']])
  self.assertEqual(got2['path'],str(second.resolve()))
  self.assertEqual(json.loads(got.stdout)['path'],str(p.resolve()))
  self.assertEqual(got2['headings'],expect)
  self.assertNotEqual(got2['headings'],json.loads(got.stdout)['headings'])
  unde=p.with_name('ts23-undecodable.md'); unde.write_bytes(b'\\xff\\xfe# x\\n')
  self.assertIn(b'\\xff',unde.read_bytes(),'fixture must be undecodable as UTF-8')
  u=self.invoke(unde); self.assertEqual(u.returncode,2,'undecodable input exits 2, it does not crash')
  self.assertEqual(u.stdout,''); self.assertIn('ERR_INPUT',u.stderr)
  self.assertNotIn('Traceback',u.stderr,'no traceback on an input error')
  bad=self.invoke(p.with_name('nonexistent-skill-input'))
  self.assertNotEqual(bad.returncode,0); self.assertIn('ERR_INPUT',bad.stderr)
  self.assertEqual(bad.returncode,2,'a missing input must exit 2')
  self.assertEqual(bad.stdout,'','an input error must write nothing to stdout')
if __name__=='__main__': unittest.main(verbosity=2)
''',
 'SIMPLE_AGENT':common+''' def test_two_step_limit_and_hashes(self):
  p=Path(os.environ['TS23_QUEUE']); queue=json.loads(p.read_text()); got=self.invoke(p)
  self.assertEqual(got.returncode,0,got.stderr)
  self.assertTrue(got.stdout.strip(),'program produced no output'); data=json.loads(got.stdout)
  self.assertEqual(data['steps'],2); self.assertEqual(data['remaining'],1)
  self.assertEqual(data['halt_reason'],'BUDGET')
  self.assertEqual([r['bytes'] for r in data['reviews']],[len(Path(x).read_bytes()) for x in queue[:2]])
  self.assertTrue(all(len(r['sha256'])==64 for r in data['reviews']))
  self.assertEqual([r['path'] for r in data['reviews']],queue[:2])
  self.assertEqual([r['sha256'] for r in data['reviews']],[hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in queue[:2]])
  limited=self.invoke(p,'--max-steps','1'); self.assertEqual(limited.returncode,0,limited.stderr)
  lim=json.loads(limited.stdout); self.assertEqual(lim['steps'],1)
  self.assertEqual([r['bytes'] for r in lim['reviews']],[len(Path(x).read_bytes()) for x in queue[:1]])
  self.assertEqual([r['path'] for r in lim['reviews']],queue[:1])
  self.assertEqual([r['sha256'] for r in lim['reviews']],[hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in queue[:1]])
  self.assertEqual(lim['remaining'],len(queue)-1)
  self.assertEqual(lim['halt_reason'],'BUDGET')
  emptyq=p.with_name('ts23-empty-queue.json'); emptyq.write_text('[]',encoding='utf-8')
  self.assertEqual(json.loads(emptyq.read_text(encoding='utf-8')),[],'fixture must be an empty list')
  e=self.invoke(emptyq); self.assertEqual(e.returncode,0,e.stderr)
  ed=json.loads(e.stdout)
  self.assertEqual((ed['steps'],ed['remaining'],ed['reviews']),(0,0,[]))
  self.assertEqual(ed['halt_reason'],'QUEUE_EXHAUSTED','nothing was queued, so nothing was budget-limited')
  over=self.invoke(p,'--max-steps','20'); self.assertEqual(over.returncode,0,over.stderr)
  od=json.loads(over.stdout); self.assertEqual((od['steps'],od['remaining']),(3,0))
  self.assertEqual(od['halt_reason'],'QUEUE_EXHAUSTED','the queue ran out before the limit')
  badq=p.with_name('ts23-bad-queue.json'); badq.write_text('{"a":1}',encoding='utf-8')
  bq=self.invoke(badq); self.assertEqual(bq.returncode,2,bq.stderr); self.assertEqual(bq.stdout,'')
  miss=p.with_name('ts23-queue-missing-entry.json'); miss.write_text(json.dumps([str(p.with_name('nope'))]),encoding='utf-8')
  mq=self.invoke(miss); self.assertEqual(mq.returncode,2,'an unreadable entry must not be skipped'); self.assertEqual(mq.stdout,'')
if __name__=='__main__': unittest.main(verbosity=2)
'''
}
codes={k:(R/'ts23_src'/f'{k}.py').read_text(encoding='utf-8') for k in ('CLI_TOOL','AGENT_SKILL','SIMPLE_AGENT')}
assert all(len(v)>200 for v in codes.values()), codes
settings=[('CLI_TOOL','cli','ts23_newline','ts23-newlines'),('AGENT_SKILL','skill','ts23_headings','ts23-headings'),('SIMPLE_AGENT','agent','ts23_review','ts23-review')]
results=[]
for kind,directory,module,command in settings:
 root=repo/'ts23_programs'/directory; test=repo/'ts23_tests'/f'test_{directory}.py'
 write(f'ts23_tests/test_{directory}.py',tests[kind])
 env=dict(ENV,PYTHONPATH=str(root),TS23_MODULE=module,TS23_FIXTURE=str(fixture),TS23_QUEUE=str(queue))
 import shutil as _shutil
 _shutil.rmtree(root/module,ignore_errors=True)
 assert not (root/module/'__init__.py').exists()
 (root/module).mkdir(parents=True,exist_ok=True)
 write(f'ts23_programs/{directory}/{module}/__init__.py','''def main(*a,**k):
    # placeholder: runs, exits 0, prints nothing - so the RED fails on the expected OUTPUT,
    # not on an import or a missing entry point
    return 0
''')
 write(f'ts23_programs/{directory}/{module}/__main__.py','from . import main\nraise SystemExit(main())\n')
 red=run([sys.executable,test],kind+' RED with an importable but unimplemented module',env)
 assert red['exit_code']!=0,red
 assert 'No module named' not in red['stderr'],('RED must be behavioural, not a collection error',red)
 write(f'ts23_programs/{directory}/{module}/__init__.py',codes[kind])
 write(f'ts23_programs/{directory}/{module}/__main__.py','from . import main\nraise SystemExit(main())\n')
 pyproject=f'''[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"
[project]
name = "ts23-{directory}"
version = "0.0.1"
requires-python = ">=3.11"
[project.scripts]
{command} = "{module}:main"
[tool.setuptools]
packages = ["{module}"]
'''
 if kind=='AGENT_SKILL':
  pyproject+='[tool.setuptools.package-data]\nts23_headings = ["SKILL.md", "manifest.json"]\n'
  write(f'ts23_programs/{directory}/{module}/SKILL.md','---\nname: ts23-heading-inventory\ndescription: Use when extracting local Markdown ATX headings. Read-only deterministic inventory.\n---\n# Heading inventory\nRun `ts23-headings PATH` to print JSON headings with line and level.\nCallable entrypoint: `ts23_headings.inventory(path)`.\nOnly local UTF-8 input; no network or edits. Does not parse fenced-code contexts or Setext headings.\n')
  write(f'ts23_programs/{directory}/{module}/manifest.json',json.dumps({'name':'ts23-heading-inventory','triggers':['heading inventory'],'permissions':['local.read'],'forbidden':['net.write','repo.write']}))
 write(f'ts23_programs/{directory}/pyproject.toml',pyproject)
 green=run([sys.executable,test],kind+' GREEN after implementation',env)
 assert green['exit_code']==0,green
 results.append({'kind':kind,'source_root':str(root),'module':module,'command':command,'red':red,'green':green})
# Install real distributions into a sandbox venv. All build/cache/temp paths remain in sandbox.
venv=S/'venv'; created=run([sys.executable,'-m','venv',venv],'create HERMETIC sandbox venv (no system site-packages)'); assert created['exit_code']==0
vp0=venv/'Scripts/python.exe'
toolchain=run([vp0,'-m','pip','install','-q','setuptools>=68','wheel'],'install build toolchain INTO the hermetic venv (network, disclosed)')
assert toolchain['exit_code']==0,toolchain
vp=venv/'Scripts/python.exe'
for entry in results:
 install=run([vp,'-m','pip','install','--no-build-isolation','--no-deps','--no-index',entry['source_root']],entry['kind']+' INSTALL')
 entry['install']=install
 if install['exit_code']: continue
 command=venv/'Scripts'/(entry['command']+'.exe'); input_path=queue if entry['kind']=='SIMPLE_AGENT' else W/'SBL/README.md'
 use_env=dict(ENV); use_env.pop('PYTHONPATH',None)
 use=run([command,input_path],entry['kind']+' installed USE real workspace input',use_env)
 entry['usage']=use
 env=dict(use_env,TS23_MODULE=entry['module'],TS23_FIXTURE=str(fixture),TS23_QUEUE=str(queue))
 entry['installed_test']=run([vp,repo/'ts23_tests'/('test_'+{'CLI_TOOL':'cli','AGENT_SKILL':'skill','SIMPLE_AGENT':'agent'}[entry['kind']]+'.py')],entry['kind']+' installed behavioral TEST',env)
 location=run([vp,'-c',f'import {entry["module"]}; print({entry["module"]}.__file__)'],entry['kind']+' installed LOCATION',use_env)
 entry['installed_location']=location['stdout'].strip()
 entry['source_files']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in Path(entry['source_root']).rglob('*') if p.is_file() and 'build' not in p.parts and not any(x.endswith('.egg-info') for x in p.parts)]
 entry['installed_files']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in Path(entry['installed_location']).parent.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 entry['installed_launcher']={'path':str(command),'sha256':hashlib.sha256(command.read_bytes()).hexdigest()}
# Exercise the actual skill bridge against the installed bundle, not a preexisting sample skill.
from sbl_sp.bridge import SkillBridge
skill=next(e for e in results if e['kind']=='AGENT_SKILL')
if skill.get('installed_location'):
 sb=SkillBridge(str(Path(skill['installed_location']).with_name('manifest.json')))
 skill['native_skill_bridge']={'discover':sb.discover(),'match':sb.match('heading inventory'),'load':sb.effective_load({'provider_on':True,'name':'R14-isolated-host'}),'invoke_authorization':sb.invoke('local.read',True),'unload':sb.unload(),'limitation':'SkillBridge.invoke returns authorization metadata, not executable dispatch. Actual installed callable executed separately above.'}
# Native bridge control and all command output are durable even if a later assertion fails.
result={'programs':results,'bridge_order':order.to_dict(),'bridge_negative_control':guard,'commands_file':str(R/'ts23_commands.json'),'nonzero_commands':failures,'maker':'codex (this delegated openai-codex coding session; no standalone Codex CLI spawn)','all_programs_installed_used':all(e.get('install',{}).get('exit_code')==0 and e.get('usage',{}).get('exit_code')==0 and e.get('installed_test',{}).get('exit_code')==0 for e in results)}
dump(R/'ts23_build_receipt.json',result); print(json.dumps({'all_programs_installed_used':result['all_programs_installed_used'],'programs':len(results),'nonzero_commands':len(failures)}))
