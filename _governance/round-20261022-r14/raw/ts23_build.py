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
  p=Path(os.environ['TS23_FIXTURE']); data=p.read_bytes(); got=self.invoke(p)
  self.assertEqual(got.returncode,0,got.stderr)
  self.assertTrue(got.stdout.strip(),'program produced no output')
  self.assertEqual(json.loads(got.stdout),{'path':str(p.resolve()),'bytes':len(data),'newlines':data.count(b'\\n'),'sha256':hashlib.sha256(data).hexdigest()})
  empty=p.with_name('ts23-empty-input'); empty.write_bytes(b'')
  got2=self.invoke(empty); self.assertEqual(got2.returncode,0,got2.stderr)
  self.assertEqual(json.loads(got2.stdout),{'path':str(empty.resolve()),'bytes':0,'newlines':0,'sha256':hashlib.sha256(b'').hexdigest()})
  bad=self.invoke(p.with_name('nonexistent-cli-input'))
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
  second=p.with_name('ts23-headings-second.md'); second.write_text('# Alpha\\n\\ntext\\n\\n## Beta\\n### Gamma\\n',encoding='utf-8')
  got2=json.loads(self.invoke(second).stdout)
  expect=[{'line':i+1,'level':len(l)-len(l.lstrip('#')),'text':l.lstrip('#').strip()} for i,l in enumerate(second.read_text(encoding='utf-8').splitlines()) if l.startswith('#')]
  self.assertEqual(got2['path'],str(second.resolve()))
  self.assertEqual(json.loads(got.stdout)['path'],str(p.resolve()))
  self.assertEqual(got2['headings'],expect)
  self.assertNotEqual(got2['headings'],json.loads(got.stdout)['headings'])
  bad=self.invoke(p.with_name('nonexistent-skill-input'))
  self.assertNotEqual(bad.returncode,0); self.assertIn('ERR_INPUT',bad.stderr)
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
  bad=self.invoke(p,'--max-steps','3'); self.assertNotEqual(bad.returncode,0)
if __name__=='__main__': unittest.main(verbosity=2)
'''
}
codes={
 'CLI_TOOL':'''"""Read-only byte/newline census."""
import argparse,hashlib,json
from pathlib import Path
def main():
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('path',type=Path); args=parser.parse_args()
 try: data=args.path.read_bytes()
 except OSError as exc: parser.exit(2,'ERR_INPUT: '+str(exc)+'\\n')
 print(json.dumps({'path':str(args.path.resolve()),'bytes':len(data),'newlines':data.count(b'\\n'),'sha256':hashlib.sha256(data).hexdigest()},sort_keys=True))
 return 0
''',
 'AGENT_SKILL':'''"""Inventory ATX headings; fenced-code interpretation is outside scope."""
import argparse,json,re
from pathlib import Path
def inventory(path):
 lines=Path(path).read_text(encoding='utf-8').splitlines(); headings=[]
 for number,line in enumerate(lines,1):
  match=re.match(r'^(#{1,6})[ \\t]+(.+?)\\s*$',line)
  if match: headings.append({'line':number,'level':len(match[1]),'text':match[2]})
 return headings
def main():
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('path',type=Path); args=parser.parse_args()
 try: headings=inventory(args.path)
 except (OSError,UnicodeError) as exc: parser.exit(2,'ERR_INPUT: '+str(exc)+'\\n')
 print(json.dumps({'path':str(args.path.resolve()),'headings':headings},sort_keys=True)); return 0
''',
 'SIMPLE_AGENT':'''"""Bounded deterministic evidence-review agent; no LLM or external actions."""
import argparse,hashlib,json
from pathlib import Path
def review(queue,max_steps=2):
 reviews=[]; fixed=tuple(queue)
 for index,path in enumerate(fixed):
  if index>=max_steps: break
  data=Path(path).read_bytes(); reviews.append({'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
 return {'steps':len(reviews),'remaining':len(fixed)-len(reviews),'reviews':reviews,'halt_reason':'BUDGET' if len(reviews)<len(fixed) else 'QUEUE_EXHAUSTED'}
def main():
 parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('queue',type=Path); parser.add_argument('--max-steps',type=int,choices=[1,2],default=2); args=parser.parse_args()
 try:
  fixed=json.loads(args.queue.read_text(encoding='utf-8'))
  if not isinstance(fixed,list) or not all(isinstance(x,str) for x in fixed): raise ValueError('queue must be a JSON list of paths')
  result=review(fixed,args.max_steps)
 except (OSError,ValueError,UnicodeError) as exc: parser.exit(2,'ERR_INPUT: '+str(exc)+'\\n')
 print(json.dumps(result,sort_keys=True)); return 0
'''
}
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
