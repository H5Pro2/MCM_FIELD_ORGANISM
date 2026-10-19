"""Complete prospective administrative binding, then at most one focused suite."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from tools import _checkpoint_transfer_entry as entry
from tools import _checkpoint_transfer_metadata as model

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/checkpoint-authorization-qualification-20260912-04'
OWN=['tools/_checkpoint_transfer_entry.py','tools/_checkpoint_transfer_budget.py',
     'tools/_checkpoint_transfer_metadata.py','tests/test_checkpoint_authorization.py',
     'reports/qualify_checkpoint_authorization_once.py']
H='f'*64

def raw(v):return json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')
def ident(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

def prepare():
    if OUT.exists():raise RuntimeError('unused qualification directory required')
    old=json.loads((ROOT/'reports/checkpoint-entry-qualification-20260912-02/preregistration.json').read_bytes())
    prior=json.loads((ROOT/'reports/memory-restart-transfer-ready-20260912-01/settings.json').read_bytes())
    files=dict(old['inventory']['files'])
    for name in OWN:files[name]=ident(ROOT/name)
    inventory=dict(files=files)
    charged=list(dict.fromkeys(old['charged_sources']+OWN))
    tests=sorted(n.name for n in ast.walk(ast.parse((ROOT/OWN[3]).read_text()))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
    refs=list(prior['qualification_references'])
    admin={}
    source=sum(files[p]['bytes'] for p in charged)+3*len(raw(inventory))
    for ref in refs:
        data=(ROOT/ref['path']).read_bytes()
        if ident(ROOT/ref['path'])!={k:ref[k] for k in ('bytes','sha256')}:raise RuntimeError('reference changed')
        try:v=json.loads(data)
        except ValueError:v=None
        classes=model.ledger.classify(len(data),v)
        admin[ref['path']]=classes['metadata'];source+=classes['sources']
    prefix=OUT.relative_to(ROOT).as_posix()
    for name,role in [('preregistration.json','authorization-preregistration'),('result.json','authorization-result'),('stderr.log','authorization-log')]:
        refs.append(dict(path=prefix+'/'+name,role=role,bytes=9999999999,sha256=H))
    manifest=entry.c.b.decode_manifest(prior['manifest'])
    common=entry.c.common_values(manifest)
    admin['runtime_common']=len(raw(dict(values=common,sha256=H)))
    authorization=entry.expected_authorization(ROOT/'reports/memory-restart-transfer-ready-20260912-01/settings.json',prior,manifest)
    admin['authorization']=len(raw(authorization));admin['authorization_consumed']=64
    dispatch=dict(run_id=manifest.run_id,binding_sha256=H)
    admin['dispatch']=len(raw(dispatch))
    extra=[dict(path='reports/memory-restart-transfer-final/settings.json',bytes=9999999999,sha256=H),
           dict(path='reports/memory-restart-transfer-final/authorization.json',bytes=9999999999,sha256=H),
           dict(path='reports/memory-restart-transfer-final/authorization.json.used',bytes=64,sha256=H)]
    runtime_prereg=dict(inventory=inventory,charged_sources=charged,external_evidence=refs+extra)
    admin['runtime_preregistration']=len(raw(runtime_prereg))-len(raw(inventory))
    success_log=sum(len(f'{n} (tests.test_checkpoint_authorization.AuthorizationTests.{n}) ... ok\n') for n in tests)+256
    admin['new_qualification_success_log']=success_log
    result_shape=dict(status='NOT_QUALIFIED',test_calls=1,exit_code=-4294967295,
        hashes_unchanged=False,log_bytes=9999999999,gates=False,preregistration_sha256=H)
    admin['new_qualification_result']=len(raw(result_shape))
    reserves=dict(full_failure_log=65536,report=4096,ledger=16384,claim=4)
    settings=dict(prior,version=entry.VERSION,ready=False,inventory=inventory,charged_sources=charged,
        required_sources=charged,qualification_references=refs,source_charge=source,
        authorization_path=extra[1]['path'],metadata_upper=0)
    q=dict(inventory=inventory,charged_sources=charged,tests=tests,references=refs[:-3],reserves=reserves,
        success_log_bound=success_log,test_calls=0,status='PRECONDITION_STOP',qualification_metadata_upper=0)
    admin['new_qualification_preregistration']=0;admin['new_settings']=0
    for _ in range(32):
        shapes=model.derive(manifest.run_id,admin,charged,[r['path'] for r in refs+extra])
        by_phase={r['phase']:r['metadata'] for r in shapes['rows']}
        envelope=entry.budget.envelope(source,by_phase)
        settings['metadata_upper']=shapes['maximum'];settings['metadata_by_phase']=by_phase;settings['budget']=envelope
        q['metadata_derivation']=shapes;q['runtime_budget']=envelope
        new_q=len(raw(q))-len(raw(inventory))
        new_settings=len(raw(settings))-len(raw(inventory))
        q['qualification_metadata_upper']=new_q+sum(reserves.values())
        if (new_q,new_settings)==(admin['new_qualification_preregistration'],admin['new_settings']):break
        admin=dict(admin,new_qualification_preregistration=new_q,new_settings=new_settings)
    else:raise RuntimeError('format-bound fixed point did not converge')
    q['qualification_metadata_upper']=new_q+sum(reserves.values())
    q['status']='READY' if not shapes['violations'] and not envelope['violations'] and q['qualification_metadata_upper']<=entry.budget.LIMITS['metadata'] else 'PRECONDITION_STOP'
    OUT.mkdir();(OUT/'preregistration.json').write_bytes(raw(q))
    (OUT/'settings-proposal.json').write_bytes(raw(settings))
    peak=max(envelope['rows'],key=lambda r:r['totals']['total'])
    print(json.dumps(dict(status=q['status'],tests=len(tests),test_calls=0,
        metadata_peak=shapes['maximum'],qualification_metadata=q['qualification_metadata_upper'],
        source_bytes=source,total_peak=peak,administrative_parts=admin),indent=2))

def run():
    q=json.loads((OUT/'preregistration.json').read_bytes())
    if q['status']!='READY':raise RuntimeError('precondition failed; no test invocation')
    for p,v in q['inventory']['files'].items():
        if ident(ROOT/p)!=v:raise RuntimeError('source changed')
    with (OUT/'invocation.claim').open('xb') as f:f.write(b'once')
    with (OUT/'stdout.log').open('xb') as out,(OUT/'stderr.log').open('xb') as err:
        p=subprocess.run([sys.executable,'-m','unittest','tests.test_checkpoint_authorization','-v'],cwd=ROOT,stdout=out,stderr=err)
    unchanged=all(ident(ROOT/n)==v for n,v in q['inventory']['files'].items())
    size=(OUT/'stderr.log').stat().st_size+(OUT/'stdout.log').stat().st_size
    result=dict(status='QUALIFIED' if p.returncode==0 and unchanged and size<=q['success_log_bound'] else 'NOT_QUALIFIED',
        test_calls=1,exit_code=p.returncode,hashes_unchanged=unchanged,log_bytes=size,gates=False,
        preregistration_sha256=ident(OUT/'preregistration.json')['sha256'])
    (OUT/'result.json').write_bytes(raw(result));print(json.dumps(result,indent=2))

if __name__=='__main__':{'prepare':prepare,'run':run}[sys.argv[1]]()
