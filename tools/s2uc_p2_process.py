"""Stdlib-only bootstrap; exclusive consumption precedes Windows Job admission."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'reports/s2uc/v8-process-limit-corrected-20260920/limit.py'
CASES=('success','memoryerror','bad_hash','abort')

def need(ok,reason):
    if not ok: raise ValueError(reason)

def save(path,value):
    data=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
    with Path(path).open('xb') as f:
        need(f.write(data)==len(data),'P2_SHORT_WRITE');f.flush();os.fsync(f.fileno())

def clean_imports():
    return not any(n in ('numpy','tools','tests','mcm_field_organism') or
        n.startswith(('numpy.','tools.','tests.','mcm_field_organism.')) for n in sys.modules)

def verify_current_job(proof):
    """Re-query the OS; a caller-provided success dictionary is not admission."""
    need(type(proof.get('job_name')) is str,'P2_JOB_REQUIRED')
    api=runpy.run_path(str(HELPER),run_name='p2_limit_helpers')
    job=api['openjob'](4,False,proof['job_name']);need(bool(job),'P2_JOB_REQUIRED')
    try: actual=api['evidence'](job,api['current']())
    finally: api['close'](job)
    need(all(actual[k]==proof.get(k) for k in ('member','limit','flags')),'P2_JOB_REQUIRED')
    return actual

def child(config):
    need(sys.flags.no_site and clean_imports(),'P2_PREIMPORT')
    need(set(config)=={'binding','folder','job','case','inventory_sha256','binding_sha256'}
         and config['case'] in CASES,'P2_CHILD_CONFIG')
    folder=Path(config['folder']);path=Path(config['binding'])
    save(folder/'bootstrap.json',dict(ns=time.perf_counter_ns(),no_site=True,product_numpy_absent=True))
    need(sys.stdin.readline().strip()=='admit','P2_ADMISSION_MISSING')
    need(hashlib.sha256(path.read_bytes()).hexdigest()==config['binding_sha256'],'P2_BOOT_BINDING_CHANGED')
    data=(path.parent/'inventory.json').read_bytes()
    need(hashlib.sha256(data).hexdigest()==config['inventory_sha256'],'P2_BOOT_INVENTORY_CHANGED')
    inv=json.loads(data)
    for row in inv['files']:
        p=ROOT/row['path']
        need(p.resolve().is_relative_to(ROOT) and not p.is_symlink() and not p.is_junction(),'P2_BOOT_PATH')
        raw=p.read_bytes()
        need(len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],'P2_BOOT_CODE_CHANGED')
    api=runpy.run_path(str(HELPER),run_name='p2_limit_helpers')
    job=api['openjob'](4,False,config['job']);need(bool(job),'P2_JOB_MISSING')
    try: proof=api['evidence'](job,api['current']())
    finally: api['close'](job)
    need(clean_imports(),'P2_IMPORTED_BEFORE_ADMISSION')
    proof['job_name']=config['job']
    save(folder/'child-admission.json',dict(proof,product_numpy_absent=True))
    if config['case']=='abort': os._exit(17)
    import site
    site.main();sys.path.insert(0,str(ROOT))
    from tools import _s2uc_p2_execution as e
    from tools import _s2nu_private_source_binding as nu
    calls=0;real_calls=0;production_receipts=[];first_supplier_ns=None;first_production_ns=None
    def forbidden(*args,**kwargs):
        nonlocal real_calls
        real_calls+=1;raise AssertionError('P2_REAL_PRODUCTION_FORBIDDEN')
    nu.pcm_window=forbidden
    value=e.read_json(path)
    e.check_claim(path,value)
    source_admission_ns=time.perf_counter_ns()
    bound=None;rejected_endpoints=0
    if value['source_identity']==e.BOUND_TEST:
        # The sole replacement seam is the production interface used by the
        # unchanged context.prepare_nu_supplier closure. Never invoke NU synthesis.
        def replacement(spec):
            nonlocal first_production_ns
            verify_current_job(proof)
            need(type(spec) is nu.WindowSpec and spec.stream==2 and 0<=spec.window<5,'P2_TEST_WINDOW')
            if first_production_ns is None:first_production_ns=time.perf_counter_ns()
            if config['case']=='memoryerror' and len(production_receipts)==57:
                raise MemoryError('P2_INJECTED_NOT_EXHAUSTION')
            data=e.context.neutral_payload(f'neutral-v9-{spec.window}')
            if config['case']=='bad_hash' and not production_receipts:data[0]^=1
            production_receipts.append([spec.stream,spec.window,e.sha(data)])
            return data
        nu.pcm_window=replacement
        source_context=e.read_json(ROOT/value['source_context']['path'])
        manifest=e.read_json(path.parent/'manifest.json')
        bound=e.prepare_bound_supplier(source_context,proof,binding_path=path,test_manifest=manifest)
        before_calls=bound.calls
        # Exercise all endpoint fields before the first production replacement.
        endpoint=next(ev['endpoint'] for ev in manifest['events'] if 'endpoint' in ev)
        for key in (*endpoint,'extra'):
            wrong=dict(endpoint);wrong[key]='INVALID'
            try:bound(wrong)
            except ValueError as exc:
                need(str(exc)=='P2_TEST_ENDPOINT_INVALID','P2_WRONG_ENDPOINT_REASON');rejected_endpoints+=1
            else:raise AssertionError('P2_WRONG_ENDPOINT_ACCEPTED')
        need(bound.calls==before_calls==0 and not production_receipts,'P2_EAGER_PRODUCTION')
    def supplier(endpoint):
        nonlocal calls,first_supplier_ns
        calls+=1
        if first_supplier_ns is None:first_supplier_ns=time.perf_counter_ns()
        if bound is not None:return bound(endpoint)
        if config['case']=='memoryerror' and calls==58: raise MemoryError('P2_INJECTED_NOT_EXHAUSTION')
        data=e.context.neutral_payload(endpoint['source_id'])
        if config['case']=='bad_hash' and calls==1: data[0]^=1
        return data
    save(folder/'after-imports.json',dict(ns=time.perf_counter_ns()))
    try:result=e.execute_child(path,supplier,proof)
    finally:nu.pcm_window=forbidden
    save(folder/'result.json',result)
    save(folder/'facts.json',dict(calls=calls,real_production_calls=real_calls,gate=e.core.GATE,
         scope=e.scope(value),test_evidence=True,source_admission_ns=source_admission_ns,
         first_supplier_ns=first_supplier_ns,first_production_ns=first_production_ns,
         bound_supplier_calls=0 if bound is None else bound.calls,
         replacement_calls=len(production_receipts),production_receipts=production_receipts,
         rejected_endpoints_before_production=rejected_endpoints,
         source_supplier_constructed_after_admission=bound is not None))

def run_neutral(path, *, case='success', timeout=180):
    from tools import _s2uc_p2_execution as e
    need(case in CASES,'P2_CASE')
    value,ledger=e.load(path)
    e.claim(path,value,ledger)
    folder=Path(path).parent/'observer';folder.mkdir()
    cfg=dict(binding=str(Path(path).absolute()),folder=str(folder.absolute()),
        job='Local\\MCM-P2-'+os.urandom(16).hex(),case=case,
        inventory_sha256=value['inventory']['sha256'],binding_sha256=e.p1.reference(path)['sha256'])
    save(folder/'config.json',cfg);ledger.admit()
    job=None;process=None;primary=None;code=None
    api=runpy.run_path(str(HELPER),run_name='p2_limit_helpers')
    try:
        job=api['create'](None,cfg['job'])
        need(bool(job) and api['c'].get_last_error()!=183,'P2_JOB_CREATE_FAILED')
        limit=api['Extended']();limit.basic.flags=0x2100;limit.limit=640*1048576
        api['need'](api['setjob'](job,9,api['c'].byref(limit),api['c'].sizeof(limit)))
        with (folder/'stdout.txt').open('xb') as out,(folder/'stderr.txt').open('xb') as err:
            config_path=folder/'config.json'
            process=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),
                str(config_path),hashlib.sha256(config_path.read_bytes()).hexdigest()],
                stdin=subprocess.PIPE,stdout=out,stderr=err,text=True,cwd=ROOT,
                creationflags=subprocess.CREATE_NO_WINDOW)
            api['need'](api['assign'](job,int(process._handle)))
            proof=api['evidence'](job,int(process._handle))
            save(folder/'parent-admission.json',proof)
            process.communicate('admit\n',timeout=timeout)
            code=process.returncode
        need(code==0,'P2_CHILD_EXIT:'+str(code))
        product=e.read_json(folder/'result.json')
        ledger.admit()
        result=dict(status=product['status'],product=product,exit_code=code,
            evaluation_allowed=product['evaluation_allowed'],real_execution_authorized=False)
    except Exception as exc:
        primary=str(exc) or type(exc).__name__
        if process is not None and process.poll() is None: process.kill();process.wait()
        result=dict(status='NOT_EVALUABLE',primary_failure=primary,exit_code=code,
                    evaluation_allowed=False,real_execution_authorized=False)
    finally:
        if job: api['close'](job)
    result.update(scope=e.scope(value),test_evidence=True)
    try: e.atomic(folder/'process-exit.json',e.canonical(result),ledger)
    except Exception as exc:
        result=dict(status='NOT_EVALUABLE',primary_failure=primary or str(exc),
            scope=e.scope(value),test_evidence=True,
            evaluation_allowed=False,real_execution_authorized=False)
    return result

if __name__=='__main__':
    try:
        need(len(sys.argv)==3,'P2_PUBLIC_REAL_ENTRY_DISABLED')
        data=Path(sys.argv[1]).read_bytes()
        need(hashlib.sha256(data).hexdigest()==sys.argv[2],'P2_CONFIG_CHANGED')
        child(json.loads(data))
    except Exception as exc:
        # Bounded diagnostic; parent records an unsuccessful exit without retry.
        sys.stderr.write((str(exc) or type(exc).__name__)[:2048]);raise SystemExit(1)
