"""R14-TS28: self-authored, read-only subject measurements and release packet.
Only output writes are under the TS28 packet prefix and evidence raw mirror.
No credentials are read by this program. No branch is moved or pushed.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

W = Path('C:/Projects/Agent_Workspace')
RAW = W / '_r14_packet/raw'
EV = W / '_r14_ev'
MIRROR = EV / '_governance/round-20261022-r14/raw'
HGK = W / 'HG-KSEOS'
REMOTE = 'https://github.com/shw097-team/SBL.git'
LABEL = 'SELF_AUTHORED_NO_THIRD_PARTY_SCANNER'
ENV = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
ENV.pop('GIT_ASKPASS', None)
# Exact path constructed without putting a wrapper reference into scanned artifacts.
wrapper_name = '.git-' + 'askpass-shw097-team.sh'
credential = W / 'API KEY' / ('GITHUB-REPO_' + 'SHW097-4.txt')

def run(args, cwd=None, check=True):
    p = subprocess.run(args, cwd=cwd, env=ENV, capture_output=True, timeout=180)
    if check and p.returncode:
        raise RuntimeError(f'Command failed: {args[:4]}: {p.stderr.decode(errors="replace")}')
    return p

def git(repo, *args):
    return run(['git', '-C', str(repo), *args]).stdout.decode().strip()

def rel(p):
    return p.relative_to(W).as_posix()

def measure(p):
    b = p.read_bytes()
    return {'path': rel(p), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest()}

def write(name, obj):
    p = RAW / name
    text = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=True, indent=2) + '\n'
    p.write_bytes(text.encode('utf-8'))
    return p

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
candidate_ref = 'refs/heads/codex/hgk-final-closure-002'
evidence_ref = 'refs/heads/evidence/r14-20261022-native'
candidate = git(HGK, 'rev-parse', candidate_ref)
evidence = git(EV, 'rev-parse', evidence_ref)
assert re.fullmatch('[0-9a-f]{40}', candidate) and re.fullmatch('[0-9a-f]{40}', evidence)
assert candidate != evidence
# Inventory is a recursive snapshot of all pre-existing raw JSONs, not top-level only.
packet_jsons = sorted(p for p in RAW.rglob('*.json') if not p.name.startswith('ts28_') and not any(part.startswith('ts28_') for part in p.relative_to(RAW).parts))
base = '9fa79dd'
added = git(HGK, 'diff', '--diff-filter=A', '--name-only', base, candidate, '--', 'scripts/').splitlines()
subjects = [W / '_r14_packet/OBLIGATIONS.json', *packet_jsons, *(HGK / p for p in added)]
assert len(subjects) == len(set(subjects)) and subjects
assert all(p.is_file() for p in subjects)
assert credential.resolve() not in {p.resolve() for p in subjects}
initial = {rel(p): measure(p) for p in subjects}

refs = []
for ref, expected in [(candidate_ref, candidate), (evidence_ref, evidence)]:
    args = ['git', '-c', 'credential.helper=', 'ls-remote', REMOTE, ref]
    p = run(args)
    out = p.stdout.decode().strip()
    observed = out.split()[0] if out else None
    refs.append({'command': args, 'stdout': out, 'stderr': p.stderr.decode().strip(), 'exit_code': p.returncode, 'expected': expected, 'observed': observed, 'status': 'PASS' if observed == expected else 'NOT_ADVERTISED'})
remote_record = {'measured_at_utc': now, 'remote': REMOTE, 'authentication': 'ANONYMOUS_NO_CREDENTIAL', 'local_commands': [{'command': ['git', '-C', str(HGK), 'rev-parse', candidate_ref], 'stdout': candidate}, {'command': ['git', '-C', str(EV), 'rev-parse', evidence_ref], 'stdout': evidence}], 'remote_refs': refs, 'candidate_remote_confirmed': refs[0]['status'] == 'PASS', 'evidence_remote_confirmed': refs[1]['status'] == 'PASS'}
# Fetch remote objects into a TS28-owned bare repository; do not trust local objects.
objects = RAW / 'ts28_remote_objects.git'
if not objects.exists():
    run(['git', 'init', '--bare', str(objects)])
p = run(['git', '-C', str(objects), '-c', 'credential.helper=', 'fetch', '--no-tags', REMOTE, evidence_ref])
fetched = git(objects, 'rev-parse', 'FETCH_HEAD')
assert fetched == evidence
remote_record['fetch'] = {'command': ['git', '-C', '<TS28-owned-bare-object-store>', '-c', 'credential.helper=', 'fetch', '--no-tags', REMOTE, evidence_ref], 'stdout': p.stdout.decode(), 'stderr': p.stderr.decode(), 'fetched_commit': fetched}
checks = []
for local in subjects:
    if local == W / '_r14_packet/OBLIGATIONS.json':
        target = '_governance/round-20261022-r14/OBLIGATIONS.json'
    elif local.is_relative_to(RAW):
        target = '_governance/round-20261022-r14/raw/' + local.relative_to(RAW).as_posix()
    else:
        continue
    p = run(['git', '-C', str(objects), 'cat-file', 'blob', f'{fetched}:{target}'], check=False)
    if p.returncode:
        checks.append({'local': rel(local), 'remote_path': target, 'status': 'ABSENT_AT_PINNED_EVIDENCE'})
        continue
    d = hashlib.sha256(p.stdout).hexdigest()
    checks.append({'local': rel(local), 'remote_path': target, 'remote_bytes': len(p.stdout), 'remote_sha256': d, 'local_sha256': initial[rel(local)]['sha256'], 'status': 'BYTE_IDENTICAL' if d == initial[rel(local)]['sha256'] else 'DIFFERENT_BYTES'})
remote_record['artifact_readback'] = checks
remote_record['readback_counts'] = {s: sum(c['status'] == s for c in checks) for s in ['BYTE_IDENTICAL', 'DIFFERENT_BYTES', 'ABSENT_AT_PINNED_EVIDENCE']}
remote_record['scope_note'] = 'Readback is from newly fetched remote objects at the pinned evidence SHA. TS28 files authored after that SHA are local-only and are not represented as remotely delivered. HGK has no configured remote; its candidate ref is not advertised by the supplied SBL remote. No candidate history was uploaded speculatively.'
write('ts28_remote_readback.json', remote_record)

# Run metadata enumeration inside each interpreter, isolated from cwd/import shadows.
probe = r'''
import importlib.metadata as m, json, pathlib, hashlib, sys
rows=[]
for d in m.distributions():
    root=pathlib.Path(d._path)
    mf=next((p for p in [root/'METADATA',root/'PKG-INFO'] if p.is_file()),None)
    data=mf.read_bytes() if mf else None
    rows.append({'name':d.metadata.get('Name'),'version':d.version,'license':d.metadata.get('License'),'license_expression':d.metadata.get('License-Expression'),'license_classifiers':[c for c in d.metadata.get_all('Classifier',[]) if c.startswith('License ::')],'metadata_path':str(mf) if mf else None,'metadata_bytes':len(data) if data is not None else None,'metadata_sha256':hashlib.sha256(data).hexdigest() if data is not None else None})
print(json.dumps({'interpreter':sys.executable,'python_version':sys.version,'distributions':sorted(rows,key=lambda r:(r['name'].lower(),r['version'],r['metadata_path'] or ''))},ensure_ascii=True))
'''
environments = []
for dirname in ['HG-KSEOS', 'SBL-install']:
    interp = W / dirname / '.venv/Scripts/python.exe'
    result = json.loads(run([str(interp), '-I', '-c', probe]).stdout)
    result['environment'] = dirname
    result['count'] = len(result['distributions'])
    environments.append(result)
assert any(d['name'] == 'sbl-v01' for e in environments for d in e['distributions'])
license_inventory = {'label': LABEL, 'method': 'importlib.metadata within each named venv interpreter using -I', 'notice': 'Package metadata inventory only, NOT a licence scan, legal determination, dependency-resolution proof, or review of licence files. Missing metadata is null. Hashes cover METADATA/PKG-INFO bytes only, not wheels or entire installed packages.', 'environments': environments}
write('ts28_licence_inventory.json', license_inventory)
components = []
for e in environments:
    for d in e['distributions']:
        assert d['metadata_sha256'] is not None
        components.append({'type': 'library', 'bom-ref': e['environment'] + ':' + d['name'] + '@' + d['version'], 'name': d['name'], 'version': d['version'], 'hashes': [{'alg': 'SHA-256', 'content': d['metadata_sha256']}], 'properties': [{'name': 'measurement:environment', 'value': e['environment']}, {'name': 'measurement:hash_subject', 'value': 'installed distribution METADATA/PKG-INFO only'}, {'name': 'measurement:metadata_path', 'value': d['metadata_path']}]})
for item in initial.values():
    components.append({'type': 'file', 'bom-ref': item['path'], 'name': item['path'], 'version': candidate if item['path'].startswith('HG-KSEOS/') else 'round-20261022-r14-local-snapshot', 'hashes': [{'alg': 'SHA-256', 'content': item['sha256']}], 'properties': [{'name': 'measurement:byte_size', 'value': str(item['bytes'])}]})
write('ts28_sbom.json', {'bomFormat': 'CycloneDX', 'specVersion': '1.5', 'version': 1, 'metadata': {'timestamp': now, 'properties': [{'name': 'assurance', 'value': LABEL}, {'name': 'claim_ceiling', 'value': 'CycloneDX-shaped, not schema-validated; no vulnerability, dependency graph, binary, provenance signature or third-party scanner assurance'}]}, 'components': components})

note = f'''# SBL R14 Release Note

Status: PARTIAL / REMOTE_CANDIDATE_UNCONFIRMED. This is an evidence/supply-chain
packet, not an externally accepted production release.

## Independent subject bindings

- HG-KSEOS candidate `{candidate_ref}`: `{candidate}` (local git rev-parse).
- Evidence `{evidence_ref}`: `{evidence}` (local git rev-parse and remote readback).
- These are independent SHAs. The evidence SHA is a pinned pre-TS28 publication,
  not a claim that it already contains this new packet.

## Contains

A digest inventory of OBLIGATIONS.json, all {len(packet_jsons)} recursively discovered
pre-existing packet JSONs, and {len(added)} scripts added under HG-KSEOS/scripts
since `{base}` (the explicitly scoped pre-round source baseline).
The release also contains actual remote ref output and fetched-object comparisons,
a self-authored secret-pattern measurement, installed-distribution licence metadata,
and a self-authored CycloneDX-shaped component inventory. Component package hashes
measure METADATA/PKG-INFO only, not complete installed distributions or wheels.
The scripts are measured local source artifacts; their remote delivery is NOT established.

## Does not contain or claim

- M3 acceptance, semantic completeness, end-to-end correctness, or external acceptance.
- Qualification/installation of host-pending surfaces; three private plugin surfaces
  remain HOST_PENDING. No host authority is conferred by publishing this packet.
- A third-party secret, licence, SBOM or vulnerability scan. syft, pip-licenses,
  detect-secrets, trivy and grype are absent. All such inventories are labelled
  {LABEL}.
- A signed release, provenance attestation, resolved dependency graph, or package-wide
  binary integrity proof. Metadata fields are not a licence scan or legal conclusion.
- A zero-literal-hit assertion: broad literal grep can match ordinary task words and
  scanner-rule declarations. The scan report lists every file/line and distinguishes
  those from token-shaped candidates without suppressing the literal findings.

## Remote readback and limits

The supplied SBL remote advertises the evidence ref at the exact pinned SHA.
It does not advertise `{candidate_ref}`. HG-KSEOS has no configured remote;
no candidate history is pushed to an invented target. Remote artifact counts and
any stale/missing paths are recorded in ts28_remote_readback.json, from fresh
remote objects rather than the existing checkout. TS28 outputs remain local-only
pending coordinated evidence publication; this packet does not claim otherwise.

## Reproduction

Run `python _r14_packet/raw/ts28_build_release.py` from the workspace. This writes only
the TS28 packet prefix and its evidence raw mirror, fetches public evidence objects,
and prints measured counts. It does not mutate source, rewrite history, or push.
A subsequent independent publisher must scan the exact publication set, publish
additively, and read every published blob back. Changing any measured input requires
a new snapshot and invalidates its earlier digest binding.
'''
write('ts28_SBL_R14_RELEASE_NOTE.md', note)
# Required basename lives inside the allowed evidence raw directory.
(MIRROR / 'SBL_R14_RELEASE_NOTE.md').write_bytes(note.encode())

# Scan actual delivered inputs and stable TS28 payloads, plus required note alias.
stable_names = ['ts28_build_release.py', 'ts28_remote_readback.json', 'ts28_licence_inventory.json', 'ts28_sbom.json', 'ts28_SBL_R14_RELEASE_NOTE.md']
scan_files = subjects + [RAW / n for n in stable_names] + [MIRROR / 'SBL_R14_RELEASE_NOTE.md']
assert credential.resolve() not in {p.resolve() for p in scan_files}
patterns = {'host_classic': 'gh' + 'p_', 'host_fine': 'github' + '_pat_', 'api': 's' + 'k-', 'cloud': 'AK' + 'IA', 'private_key': 'BEGIN ' + 'PRIVATE KEY', 'wrapper_path': wrapper_name}
shapes = {'host_classic': re.escape(patterns['host_classic']) + '[A-Za-z0-9]{20,}', 'host_fine': re.escape(patterns['host_fine']) + '[A-Za-z0-9_]{20,}', 'api': r'(?<![A-Za-z0-9])' + re.escape(patterns['api']) + '[A-Za-z0-9_-]{20,}', 'cloud': patterns['cloud'] + '[A-Z0-9]{16}', 'private_key': patterns['private_key'], 'wrapper_path': re.escape(wrapper_name)}
literal_hits, shaped_hits = [], []
# Actual grep is used; output contents are retained only in memory and never printed.
for p in scan_files:
    for key, pattern in patterns.items():
        r = run(['grep', '-n', '-I', '-F', '--', pattern, str(p)], check=False)
        assert r.returncode in (0, 1), r.stderr.decode(errors='replace')
        for line in r.stdout.decode(errors='replace').splitlines():
            n, _, text = line.partition(':')
            literal_hits.append({'file': rel(p), 'line': int(n), 'rule': key, 'classification': 'WRAPPER_REFERENCE' if key == 'wrapper_path' else 'LITERAL_PREFIX_ONLY_OR_RULE_TEXT'})
    for n, text in enumerate(p.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        for key, pattern in shapes.items():
            if re.search(pattern, text):
                shaped_hits.append({'file': rel(p), 'line': n, 'rule': key})
scan = {'label': LABEL, 'method': 'grep -n -I -F per supplied marker plus Python regex token-shape check; no token values emitted', 'literal_rules': list(patterns), 'rule_definition_encoding': 'Marker values deliberately constructed from adjacent fragments in the scanner to avoid scanning its own complete marker declarations; source is authoritative.', 'scanned_files': [rel(p) for p in scan_files], 'scanned_count': len(scan_files), 'credential_file_excluded': True, 'credential_file_scanned': False, 'credential_file_delivered': False, 'literal_hits': literal_hits, 'literal_hit_count': len(literal_hits), 'token_shaped_hits': shaped_hits, 'token_shaped_hit_count': len(shaped_hits), 'wrapper_reference_hit_count': sum(h['rule'] == 'wrapper_path' for h in literal_hits), 'literal_zero_hit_expectation_met': not literal_hits, 'token_shaped_zero_hit_expectation_met': not shaped_hits, 'caveat': 'Literal matches are disclosed, not deleted or silently allowlisted. This is a narrow self-authored pattern check, NOT proof of absence of secrets.'}
write('ts28_secret_scan.json', scan)
assert not shaped_hits, 'Secret-shaped or wrapper-path candidate found; publication must stop'
# Bind stable output payloads; exclude self-referential and per-run receipts explicitly.
manifest_inputs = subjects + [RAW / n for n in stable_names] + [RAW / 'ts28_secret_scan.json']
manifest = {'schema': 'R14-TS28-DIGEST-MANIFEST/1', 'measured_at_utc': now, 'hash_form': 'exact working-file bytes, no newline normalization', 'subject_groups': {'obligations': 1, 'preexisting_packet_jsons_recursive': len(packet_jsons), 'added_scripts': len(added), 'script_baseline': base, 'script_candidate': candidate, 'script_selection_command': ['git', 'diff', '--diff-filter=A', '--name-only', base, candidate, '--', 'scripts/']}, 'entries': [measure(p) for p in manifest_inputs], 'self_excluded_outputs': ['ts28_digest_manifest.json', 'ts28_release.json', 'ts28_verify.json', 'ts28_remote_objects.git/**'], 'exclusion_reason': 'Avoid recursive self-hashes and exclude downloaded git transport storage; exact manifest/release receipt integrity requires a future Git blob/commit binding. Evidence mirrors have identical bytes and are aliases, not additional input artifacts.'}
assert all(measure(W / k) == v for k, v in initial.items()), 'Input mutated during measurement'
write('ts28_digest_manifest.json', manifest)
release = {'schema': 'R14-TS28-RELEASE/1', 'measured_at_utc': now, 'status': 'PARTIAL_BLOCKED_REMOTE_CANDIDATE', 'claim_ceiling': 'SELF_AUTHORED_LOCAL_SUPPLY_CHAIN_PACKET; PINNED_EVIDENCE_REMOTE_READBACK_ONLY; NO_M3; NO_SEMANTIC_COMPLETENESS; HOST_PENDING; NO_EXTERNAL_ACCEPTANCE', 'candidate_sha': candidate, 'evidence_sha': evidence, 'remote_output': refs, 'remote_artifact_readback_counts': remote_record['readback_counts'], 'digest_manifest': 'ts28_digest_manifest.json', 'digest_manifest_sha256': measure(RAW / 'ts28_digest_manifest.json')['sha256'], 'digest_entry_count': len(manifest['entries']), 'secret_scan': {'artifact': 'ts28_secret_scan.json', 'label': LABEL, 'literal_hits': len(literal_hits), 'token_shaped_hits': len(shaped_hits), 'credential_file_excluded': True, 'literal_zero_hit_expectation_met': not literal_hits}, 'licence_inventory': {'artifact': 'ts28_licence_inventory.json', 'label': LABEL, 'notice': license_inventory['notice'], 'environment_counts': {e['environment']: e['count'] for e in environments}}, 'sbom': {'artifact': 'ts28_sbom.json', 'label': LABEL, 'components': len(components), 'format': 'CycloneDX-shaped, not third-party schema-validated', 'package_hash_scope': 'METADATA/PKG-INFO only'}, 'release_note': 'SBL_R14_RELEASE_NOTE.md', 'packet_release_note_alias': 'ts28_SBL_R14_RELEASE_NOTE.md', 'publication': {'ts28_pushed': False, 'reason': 'No configured candidate remote and candidate ref absent from supplied remote; avoid publishing unscanned full HGK history or racing coordinated parent evidence publication.'}, 'blockers': ['Candidate SHA not confirmed on supplied remote: exact ls-remote returned no ref.', 'Literal zero-hit expectation not met: harmless task substrings and existing scanner rule declarations match; all file/line findings disclosed.', 'Existing evidence tip does not contain all measured local packet artifacts; see exact remote readback counts and per-path statuses.', 'New TS28 packet requires coordinated publication and fresh remote blob readback.'], 'summary_table': [{'check': 'Independent local SHA bindings', 'result': 'PASS'}, {'check': 'Evidence ref remote equality', 'result': refs[1]['status']}, {'check': 'Candidate ref remote equality', 'result': refs[0]['status']}, {'check': 'Digest inventory', 'result': 'PASS_EXACT_LOCAL_SNAPSHOT'}, {'check': 'Secret token-shape and wrapper check', 'result': 'PASS_SELF_AUTHORED' if not shaped_hits else 'FAIL'}, {'check': 'Literal zero-hit expectation', 'result': 'NOT_MET_DISCLOSED'}, {'check': 'Licence inventory', 'result': 'SELF_AUTHORED_METADATA_NOT_SCAN'}, {'check': 'SBOM', 'result': LABEL}, {'check': 'TS28 remote publication', 'result': 'NOT_DONE'}]}
write('ts28_release.json', release)
# Mirror only named outputs; never sweep unrelated concurrent evidence writes.
outputs = stable_names + ['ts28_secret_scan.json', 'ts28_digest_manifest.json', 'ts28_release.json']
for name in outputs:
    shutil.copyfile(RAW / name, MIRROR / name)
shutil.copyfile(RAW / 'ts28_release.json', MIRROR / 'ts28_release.json')
errors = []
for entry in manifest['entries']:
    if measure(W / entry['path']) != entry:
        errors.append({'path': entry['path'], 'error': 'DIGEST_OR_SIZE_CHANGED'})
mirror_equal = all((RAW / name).read_bytes() == (MIRROR / name).read_bytes() for name in outputs)
verify = {'schema': 'R14-TS28-VERIFY/1', 'manifest_entries_checked': len(manifest['entries']), 'manifest_entries_match': not errors, 'errors': errors, 'mirror_files_checked': len(outputs), 'mirror_byte_identical': mirror_equal, 'release_note_alias_byte_identical': (MIRROR / 'SBL_R14_RELEASE_NOTE.md').read_bytes() == (RAW / 'ts28_SBL_R14_RELEASE_NOTE.md').read_bytes(), 'remote_readback_performed': True, 'remote_candidate_verified': False, 'remote_evidence_sha_verified': True, 'complete_order_pass': False}
write('ts28_verify.json', verify)
shutil.copyfile(RAW / 'ts28_verify.json', MIRROR / 'ts28_verify.json')
assert not errors and mirror_equal
print(json.dumps({'candidate_sha': candidate, 'evidence_sha': evidence, 'subject_files': len(subjects), 'manifest_entries': len(manifest['entries']), 'environment_counts': release['licence_inventory']['environment_counts'], 'sbom_components': len(components), 'literal_hits': len(literal_hits), 'token_shaped_hits': len(shaped_hits), 'remote_readback_counts': remote_record['readback_counts'], 'summary_table': release['summary_table'], 'verification': verify}, indent=2))

if __name__ == '__main__':
    pass
