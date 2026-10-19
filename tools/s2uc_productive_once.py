"""Stdlib bootstrap for one authorized original-NU attempt; never authors authority."""
import ctypes as c
from ctypes import wintypes as w
import hashlib
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time
import winreg

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'reports/s2uc/v8-process-limit-corrected-20260920/limit.py'
TRUST_KEY=r'SOFTWARE\MCM_FIELD_ORGANISM\S2UC\ApprovedOneShots'
TRUST_SIDS={'S-1-5-18','S-1-5-32-544'}
WRITE_RIGHTS=0x10000000|0x40000000|0x000D0026

def need(ok,reason):
    if not ok:raise ValueError(reason)

def acl_rules(owner,aces):
    need(owner in TRUST_SIDS and aces is not None,'P3_UNTRUSTED_OWNER_OR_NULL_DACL')
    for kind,mask,sid in aces:
        need(kind in (0,1),'P3_UNSUPPORTED_TRUST_ACE')
        need(kind!=0 or not mask&WRITE_RIGHTS or sid in TRUST_SIDS,'P3_WRITABLE_TRUST_STORE')

def registry_acl(key):
    """Require admin/SYSTEM ownership and no other write/delete/DACL grants."""
    adv=c.WinDLL('advapi32',use_last_error=True);kernel=c.WinDLL('kernel32',use_last_error=True)
    get=adv.GetSecurityInfo;get.argtypes=[w.HANDLE,c.c_int,w.DWORD]+[c.POINTER(c.c_void_p)]*5;get.restype=w.DWORD
    free=kernel.LocalFree;free.argtypes=[c.c_void_p];free.restype=c.c_void_p
    sidtext=adv.ConvertSidToStringSidW;sidtext.argtypes=[c.c_void_p,c.POINTER(c.c_void_p)];sidtext.restype=w.BOOL
    getace=adv.GetAce;getace.argtypes=[c.c_void_p,w.DWORD,c.POINTER(c.c_void_p)];getace.restype=w.BOOL
    owner=c.c_void_p();dacl=c.c_void_p();sd=c.c_void_p()
    def sid(ptr):
        out=c.c_void_p();need(sidtext(ptr,c.byref(out)),'P3_SID_READ')
        try:return c.wstring_at(out)
        finally:free(out)
    need(get(int(key),4,5,c.byref(owner),None,c.byref(dacl),None,c.byref(sd))==0,'P3_TRUST_ACL_READ')
    try:
        need(bool(dacl.value),'P3_NULL_DACL')
        count=c.c_ushort.from_address(dacl.value+4).value;aces=[]
        for i in range(count):
            ptr=c.c_void_p();need(getace(dacl,i,c.byref(ptr)),'P3_ACE_READ')
            kind=c.c_ubyte.from_address(ptr.value).value
            need(kind in (0,1),'P3_UNSUPPORTED_TRUST_ACE')
            aces.append((kind,c.c_uint32.from_address(ptr.value+4).value,sid(ptr.value+8)))
        acl_rules(sid(owner),aces)
    finally:free(sd)

def authority(path,value):
    """Independent operator receipt in HKLM64. No path/env/key supplied by grant."""
    need(value.get('kind')=='OPERATIVE_ONE_SHOT','P3_OPERATIVE_AUTHORITY_REQUIRED')
    raw=Path(path).read_bytes();digest=hashlib.sha256(raw).hexdigest()
    try:
        # Parents could otherwise replace a protected leaf. SOFTWARE is the OS boundary.
        for part in (r'SOFTWARE\MCM_FIELD_ORGANISM',r'SOFTWARE\MCM_FIELD_ORGANISM\S2UC',TRUST_KEY):
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,part,0,
                    winreg.KEY_READ|winreg.KEY_WOW64_64KEY) as key:
                registry_acl(key)
                if part==TRUST_KEY:
                    raw_receipt,kind=winreg.QueryValueEx(key,value['run_id'])
                    need(kind==winreg.REG_SZ,'P3_TRUST_RECEIPT_TYPE')
        receipt=json.loads(raw_receipt)
    except (OSError,ValueError,KeyError) as exc:
        raise ValueError('P3_OPERATIVE_AUTHORITY_ABSENT_OR_UNTRUSTED') from exc
    expected=dict(binding_sha256=digest,authorization_id=value['authorization_id'],
                  decision=value['decision'],max_uses=1)
    need(json.dumps(receipt,sort_keys=True)==json.dumps(expected,sort_keys=True),'P3_OPERATOR_RECEIPT_MISMATCH')
    return receipt

def save(path,value):
    data=json.dumps(value,sort_keys=True,separators=(',',':')).encode()
    with Path(path).open('xb') as f:
        need(f.write(data)==len(data),'P3_SHORT_WRITE');f.flush();os.fsync(f.fileno())

def clean():
    return not any(n in ('numpy','tools','tests','mcm_field_organism') or
                   n.startswith(('numpy.','tools.','tests.','mcm_field_organism.')) for n in sys.modules)

def boot_pins(config):
    path=Path(config['binding']);raw=path.read_bytes()
    need(hashlib.sha256(raw).hexdigest()==config['binding_sha256'],'P3_BOOT_BINDING')
    value=json.loads(raw);pin=value['inventory'];data=(ROOT/pin['path']).read_bytes()
    need(len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256'],'P3_BOOT_INVENTORY')
    inv=json.loads(data)
    for row in inv['files']:
        p=ROOT/row['path']
        need(p.resolve().is_relative_to(ROOT) and not p.is_symlink() and not p.is_junction(),'P3_BOOT_PATH')
        data=p.read_bytes()
        need(len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],'P3_BOOT_CODE')
    need(hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()==inv['external']['interpreter']['sha256'],
         'P3_BOOT_RUNTIME')
    return value

def child_identity(value,test):
    """Check the domain and all output paths before even a bootstrap receipt."""
    run='s2uc-source-comparison-real-20260920-02'
    if test:
        import re
        need(re.fullmatch(r'S2UC-P3-TEST-[0-9a-f]{32}',value['run_id']) is not None,'P3_TEST_ID')
        base=ROOT/value['test_root']
        need(base.parent==ROOT/'reports/s2uc' and base.name.startswith('p3-test-')
             and base.resolve()==base,'P3_TEST_ROOT')
        expected={k:(base/k).relative_to(ROOT).as_posix() for k in ('product','observer','appendix','admission')}
    else:
        need(value['run_id']==run and value['test_root'] is None and value['test_payload'] is None,'P3_RUN_ID')
        expected={k:'reports/'+run+s for k,s in [('product',''),('observer','-observer'),
                                               ('appendix','-appendix'),('admission','-admission')]}
    need(value['outputs']==expected,'P3_OUTPUTS')
    for rel in expected.values():
        p=ROOT/rel
        need(p.resolve()==p and not p.is_symlink() and not p.is_junction(),'P3_PATH_ALIAS')

def child(config,*,test=False):
    need(sys.flags.no_site and clean(),'P3_PREIMPORT')
    need(set(config)=={'binding','binding_sha256','folder','job','test_case'},'P3_CONFIG')
    need(config['test_case'] in ('synthetic','original_bad_hash','abort','timeout') if test
         else config['test_case'] is None,'P3_TEST_CASE_FORBIDDEN')
    path=Path(config['binding']);value=boot_pins(config)
    need(value['kind']==('ISOLATED_TEST' if test else 'OPERATIVE_ONE_SHOT'),'P3_CHILD_DOMAIN')
    child_identity(value,test)
    if not test:authority(path,value)
    folder=ROOT/value['outputs']['observer']
    need(str(folder)==config['folder'],'P3_CHILD_FOLDER')
    save(folder/'bootstrap.json',dict(ns=time.perf_counter_ns(),no_site=True,product_numpy_absent=True))
    need(sys.stdin.readline().strip()=='admit','P3_HANDSHAKE')
    boot_pins(config)
    api=runpy.run_path(str(HELPER),run_name='p3_limit_helpers')
    job=api['openjob'](4,False,config['job']);need(bool(job),'P3_JOB_MISSING')
    try:proof=api['evidence'](job,api['current']())
    finally:api['close'](job)
    need(clean(),'P3_EARLY_IMPORT');proof['job_name']=config['job']
    save(folder/'child-admission.json',dict(proof,product_numpy_absent=True))
    if test and config['test_case']=='abort':os._exit(17)
    if test and config['test_case']=='timeout':time.sleep(30)
    import site
    site.main();sys.path.insert(0,str(ROOT))
    from tools import _s2uc_productive as p
    if test:
        from tools import _s2nu_private_source_binding as nu
        def replacement(spec):
            need(type(spec) is nu.WindowSpec and spec.stream==2 and 0<=spec.window<5,'P3_TEST_WINDOW')
            return p.e.context.neutral_payload(f'neutral-v9-{spec.window}')
        nu.pcm_window=replacement
    save(folder/'after-imports.json',dict(ns=time.perf_counter_ns()))
    result=p._execute(path,proof,test=True) if test else p.execute_child(path,proof)
    save(folder/'result.json',result)

def _run(path,*,test=False,case=None,timeout=180):
    from tools import _s2uc_productive as p
    value,ledger=p._test_load(path) if test else p.load(path)
    need(case in ('synthetic','original_bad_hash','abort','timeout') if test else case is None,'P3_TEST_CASE_FORBIDDEN')
    p.claim(path,value,ledger) # Persisted before any process/Job is created.
    folder=p.paths(value)['observer'];folder.mkdir()
    cfg=dict(binding=str(Path(path).absolute()),binding_sha256=p.ref(path)['sha256'],folder=str(folder),
             job='Local\\MCM-P3-'+os.urandom(16).hex(),test_case=case)
    save(folder/'config.json',cfg);ledger.admit()
    job=None;process=None;code=None;primary=None
    try:
        api=runpy.run_path(str(HELPER),run_name='p3_limit_helpers')
        job=api['create'](None,cfg['job'])
        need(bool(job) and api['c'].get_last_error()!=183,'P3_JOB_CREATE')
        limit=api['Extended']();limit.basic.flags=0x2100;limit.limit=640*1048576
        api['need'](api['setjob'](job,9,api['c'].byref(limit),api['c'].sizeof(limit)))
        with (folder/'stdout.txt').open('xb') as out,(folder/'stderr.txt').open('xb') as err:
            config_path=folder/'config.json'
            process=subprocess.Popen([sys.executable,'-S',str(Path(__file__).resolve()),
                '--test-child' if test else '--child',str(config_path),
                hashlib.sha256(config_path.read_bytes()).hexdigest()],stdin=subprocess.PIPE,
                stdout=out,stderr=err,text=True,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
            api['need'](api['assign'](job,int(process._handle)))
            save(folder/'parent-admission.json',api['evidence'](job,int(process._handle)))
            process.communicate('admit\n',timeout=timeout);code=process.returncode
        need(code==0,'P3_CHILD_EXIT:'+str(code))
        result=p.e.read_json(folder/'result.json');ledger.admit()
        result=dict(result,exit_code=code)
    except Exception as exc:
        primary=str(exc) or type(exc).__name__
        if process is not None and process.poll() is None:process.kill();process.wait()
        result=dict(status='NOT_EVALUABLE',primary_failure=primary,exit_code=code,
                    evaluation_allowed=False,**p.stamp(value))
    finally:
        if job:api['close'](job)
    try:p.e.atomic(folder/'process-exit.json',p.e.canonical(result),ledger)
    except Exception as exc:
        result=dict(status='NOT_EVALUABLE',primary_failure=primary or str(exc),
                    evaluation_allowed=False,**p.stamp(value))
    return result

def start(path):
    result=_run(path)
    if result.get('evaluation_allowed'):
        from tools import _s2uc_productive as p
        # A failed annex neither changes the product nor reruns its sources.
        annex=p.publish_appendix(path)
        result=dict(result,appendix_status=annex['status'])
    return result

def main():
    try:
        if len(sys.argv)==4 and sys.argv[1] in ('--child','--test-child'):
            data=Path(sys.argv[2]).read_bytes()
            need(hashlib.sha256(data).hexdigest()==sys.argv[3],'P3_CONFIG_HASH')
            child(json.loads(data),test=sys.argv[1]=='--test-child');return 0
        need(len(sys.argv)==2,'P3_ARGUMENTS')
        sys.path.insert(0,str(ROOT));result=start(sys.argv[1])
        print(json.dumps(result));return 0 if result.get('evaluation_allowed') else 1
    except Exception as exc:
        sys.stderr.write((str(exc) or type(exc).__name__)[:2048]);return 1

if __name__=='__main__':raise SystemExit(main())
