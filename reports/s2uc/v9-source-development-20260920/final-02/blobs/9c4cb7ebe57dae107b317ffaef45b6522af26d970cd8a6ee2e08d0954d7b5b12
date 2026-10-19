import ctypes as c
from ctypes import wintypes as w
import json, os, runpy, sys, time
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLD=HERE.parent/'v8-process-memory-20260920/measure.py'
reuse=runpy.run_path(str(OLD),run_name='memory_helpers')
save,sha=reuse['save'],reuse['sha']
LIMIT=640*1048576
WARN=96*1048576

class Basic(c.Structure):
  _fields_=[('times',c.c_longlong*2),('flags',w.DWORD),('min_ws',c.c_size_t),('max_ws',c.c_size_t),
       ('active',w.DWORD),('affinity',c.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
class Extended(c.Structure):
  _fields_=[('basic',Basic),('io',c.c_ulonglong*6),('limit',c.c_size_t),('job_limit',c.c_size_t),
       ('peak_process',c.c_size_t),('peak_job',c.c_size_t)]
K=c.WinDLL('kernel32',use_last_error=True)
def api(name,args,r=w.BOOL):
  f=getattr(K,name);f.argtypes=args;f.restype=r;return f
create=api('CreateJobObjectW',[c.c_void_p,w.LPCWSTR],w.HANDLE)
openjob=api('OpenJobObjectW',[w.DWORD,w.BOOL,w.LPCWSTR],w.HANDLE)
setjob=api('SetInformationJobObject',[w.HANDLE,c.c_int,c.c_void_p,w.DWORD])
query=api('QueryInformationJobObject',[w.HANDLE,c.c_int,c.c_void_p,w.DWORD,c.c_void_p])
assign=api('AssignProcessToJobObject',[w.HANDLE,w.HANDLE])
injob=api('IsProcessInJob',[w.HANDLE,w.HANDLE,c.POINTER(w.BOOL)])
current=api('GetCurrentProcess',[],w.HANDLE)
close=api('CloseHandle',[w.HANDLE])
def need(ok):
  if not ok: raise RuntimeError('LIMIT_CHECK: '+str(c.get_last_error()))
def evidence(job,process):
  e=Extended();member=w.BOOL()
  need(query(job,9,c.byref(e),c.sizeof(e),None));need(injob(process,job,c.byref(member)))
  need(member.value and e.limit==LIMIT and e.basic.flags==0x2100)
  return dict(ns=time.perf_counter_ns(),member=True,flags=e.basic.flags,limit=e.limit,
        peak_process_commit=e.peak_process,peak_job_commit=e.peak_job)

def load(p): return json.loads(p.read_text())

def child(cfg):
  d=Path(cfg['folder'])
  before=not any(n=='numpy' or n.startswith(('numpy.','tools.','mcm_field_organism.','tests.')) for n in sys.modules)
  need(sys.flags.no_site and before)
  save(d/'bootstrap.json',dict(ns=time.perf_counter_ns(),pid=os.getpid(),no_site=sys.flags.no_site,
                  isolated=sys.flags.isolated,product_numpy_absent=before))
  need(sys.stdin.readline().strip()=='admit')
  job=openjob(4,False,cfg['job']);need(job)
  proof=evidence(job,current());close(job)
  proof['product_numpy_absent']=before
  save(d/'child-admission.json',proof)
  if cfg['case']=='allocation':
    alloc=api('VirtualAlloc',[c.c_void_p,c.c_size_t,w.DWORD,w.DWORD],c.c_void_p)
    free=api('VirtualFree',[c.c_void_p,c.c_size_t,w.DWORD])
    class Memory(c.Structure):
      _fields_=[('length',w.DWORD),('sizes',c.c_size_t*10),('counts',w.DWORD*3)]
    status=api('K32GetPerformanceInfo',[c.POINTER(Memory),w.DWORD])
    ptrs=[];chunk=16*1048576
    for _ in range(41):
      ptr=alloc(None,chunk,0x3000,4)
      if not ptr:
        error=c.get_last_error();mem=Memory();mem.length=c.sizeof(mem);need(status(c.byref(mem),mem.length))
        op,read,cl=reuse['native_api']();h=op(os.getpid());used=read(h);cl(h)
        reject=dict(request_bytes=chunk,successful_bytes=len(ptrs)*chunk,winerror=error,
               available_system_commit=(mem.sizes[1]-mem.sizes[0])*mem.sizes[9],memory=used,simulated=False)
        break
      ptrs.append(ptr)
    else: raise RuntimeError('allocation limit NOT enforced')
    for ptr in ptrs: need(free(ptr,0,0x8000))
    need(reject['available_system_commit']>chunk and used['private_commit']+chunk>LIMIT)
    save(d/'allocation-rejection.json',reject)
  else:
    save(d/'before-imports.json',dict(ns=time.perf_counter_ns(),limit_verified=True))
    import site
    site.main()
    from tools import _s2uc_execution_v8 as e
    from tools import _s2uc_run_entry as entry
    save(d/'after-imports.json',dict(ns=time.perf_counter_ns()))
    calls=0
    def supplier(endpoint):
      nonlocal calls
      calls+=1
      if cfg['case']=='memoryerror' and calls==58:
        raise MemoryError('INJECTED_NOT_EXHAUSTION')
      return e.binding.ZERO_PCM
    r=e.run_neutral(cfg['binding'],supplier,run_id=cfg['run_id'],output_directory=cfg['output'])
    save(d/'result.json',r)
    save(d/'facts.json',dict(calls=calls,gate=e.GATE,public_gate=entry.MAIN_GATE,
                  injected=cfg['case']=='memoryerror',actual_exhaustion=False))
  save(d/'ready.json',dict(ns=time.perf_counter_ns()))
  need(sys.stdin.readline().strip()=='release')

def prepare():
  from tests.test_s2uc_execution_v8 import fixture
  from tools import _s2uc_binding_v8 as b
  need(not (HERE/'plan.json').exists())
  inv=b.current();accepted=ROOT/'reports/s2uc/v8-neutral-integration-development-20260920/final/dependency-inventory.json'
  need(inv==load(accepted))
  oldplan=load(OLD.parent/'plan.json');need(sha(OLD)==oldplan['tool_sha256'])
  files=inv['files']+[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in (OLD,Path(__file__))]
  size=sum(r['bytes'] for r in files);need(size<=720896)
  save(HERE/'used-inventory.json',dict(files=files,code_bytes=size,product_bytes=inv['code_bytes'],
    tools_bytes=size-inv['code_bytes'],external=inv['external']))
  cases=[]
  for name in ('success','memoryerror'):
    d=HERE/name;d.mkdir()
    cfg=dict(case=name,folder=str(d),job='Local\\MCM-V8-'+os.urandom(16).hex())
    if name!='allocation':
      path,rid,out=fixture(d,inv);cfg.update(binding=str(path),run_id=rid,output=str(out))
    save(d/'case.json',cfg);cases.append(cfg)
  save(HERE/'plan.json',dict(cases=cases,limit_bytes=LIMIT,warning_ws_bytes=WARN,interval_ms=10,
    runs_per_case=1,allocation_chunk=16777216,
    memoryerror_at=58,bootstrap='-S; preimport handshake',
    tool_sha256=sha(Path(__file__)),created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())))

def observe():
  import subprocess
  plan=load(HERE/'plan.json');inv=load(HERE/'used-inventory.json')
  need(all(sha(ROOT/r['path'])==r['sha256'] for r in inv['files']))
  op,read,cl=reuse['native_api']();own=op(os.getpid())
  for cfg in plan['cases']:
    d=Path(cfg['folder']);(d/'started.json').open('x').close()
    job=create(None,cfg['job']);need(job and c.get_last_error()!=183)
    lim=Extended();lim.basic.flags=0x2100;lim.limit=LIMIT
    need(setjob(job,9,c.byref(lim),c.sizeof(lim)))
    p=None;done=False;errs=[];count=0;proof=None
    try:
      with (d/'stdout.txt').open('x') as out,(d/'stderr.txt').open('x') as err:
        p=subprocess.Popen([sys.executable,'-S',str(Path(__file__)),'child',str(d/'case.json')],
          stdin=subprocess.PIPE,stdout=out,stderr=err,text=True,cwd=ROOT,creationflags=subprocess.CREATE_NO_WINDOW)
        need(assign(job,int(p._handle)))
        proof=evidence(job,int(p._handle));save(d/'parent-admission.json',proof)
        p.stdin.write('admit\n');p.stdin.flush()
        h=op(p.pid);deadline=time.monotonic()+120
        try:
          with (d/'samples.jsonl').open('x',buffering=1) as raw:
            while p.poll() is None:
              begin=time.perf_counter_ns()
              try:
                target=read(h);watch=read(own)
                raw.write(json.dumps(dict(ns=begin,target=target,observer=watch,ws_warning=target['working_set']>WARN))+'\n');count+=1
              except OSError as exc: errs.append(str(exc))
              if not done and (d/'ready.json').exists():
                peak=dict(target=read(h),observer=read(own),job=evidence(job,int(p._handle)))
                save(d/'final-native.json',peak)
                p.stdin.write('release\n');p.stdin.flush();done=True
              if time.monotonic()>deadline: raise TimeoutError('observer deadline')
              time.sleep(max(0,.01-(time.perf_counter_ns()-begin)/1e9))
        finally: cl(h)
        p.stdin.close();p.wait()
    except Exception as exc:
      errs.append(repr(exc))
      if p is not None and p.poll() is None: p.kill();p.wait()
    finally:
      close(job)
      save(d/'process-exit.json',dict(pid=None if p is None else p.pid,observer_pid=os.getpid(),
        exit_code=None if p is None else p.returncode,admitted=proof is not None,
        final_handshake=done,samples=count,errors=errs,product_result_present=(d/'result.json').exists()))
  cl(own)

def analyze():
  plan=load(HERE/'plan.json');inv=load(HERE/'used-inventory.json')
  need(all(sha(ROOT/r['path'])==r['sha256'] for r in inv['files']))
  rows=[]
  for cfg in plan['cases']:
    d=Path(cfg['folder'])
    readcase=lambda name:load(d/name)
    p=readcase('process-exit.json');valid=p['exit_code']==0 and p['final_handshake'] and not p['errors']
    row=dict(case=cfg['case'],process=p,valid=valid)
    if not valid:
      row['status']='EXTERNAL_ABORT_NO_PRODUCT_SUCCESS';rows.append(row);continue
    admit=readcase('child-admission.json');need(admit['limit']==LIMIT and admit['product_numpy_absent'])
    native=readcase('final-native.json');need(native['job']['limit']==LIMIT)
    ss=[json.loads(s) for s in (d/'samples.jsonl').read_text().splitlines()]
    row.update(native=native,sampled_max={role:{k:max(s[role][k] for s in ss) for k in ('working_set','private_commit')} for role in ('target','observer')},
         warnings=sum(s['ws_warning'] for s in ss))
    if cfg['case']=='allocation':
      reject=readcase('allocation-rejection.json');need(not reject['simulated'] and reject['winerror']!=0)
      need(not (d/'result.json').exists());row.update(status='REAL_ALLOCATION_REJECTED',rejection=reject)
    else:
      r=readcase('result.json');facts=readcase('facts.json');good=cfg['case']=='success';n=58 if good else 57
      need(readcase('before-imports.json')['ns']>admit['ns'])
      need(facts['calls']==58 and not facts['gate'] and not facts['public_gate'])
      need(len(r['owner_cleanup'])==6 and all(r['closed'] for r in r['owner_cleanup']))
      src=r['source_completion'];need(src['attempts']==58 and src['successes']==n and all(v==n for v in src['counters'].values()))
      need(r['evaluation_allowed']==good and r['primary_error']==(None if good else 'MemoryError'))
      need(r['accounting_complete'] and r['actual']['within_limits'])
      refs=r['inputs']+[dict(r,root=cfg['output']) for r in r['result_inventory']]
      need(all((Path(r['root'])/r['path']).stat().st_size==r['bytes'] and sha(Path(r['root'])/r['path'])==r['sha256'] for r in refs))
      need(sum(r['bytes'] for r in refs)==r['actual']['total_bytes'])
      row.update(status=r['status'],primary_error=r['primary_error'],source=src,actual=r['actual'])
    rows.append(row)
  save(HERE/'summary.json',rows)
  print('Checks complete')

if __name__=='__main__':
  mode=sys.argv[1]
  if mode=='child': child(load(Path(sys.argv[2])))
  else: {'prepare':prepare,'observe':observe,'analyze':analyze}[mode]()
