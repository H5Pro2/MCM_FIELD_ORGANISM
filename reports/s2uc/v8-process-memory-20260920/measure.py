"""Three predeclared one-shot neutral measurements; Windows observer is external."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))

def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def child(config):
    from contextlib import contextmanager
    folder = Path(config['folder'])
    log = (folder / 'phases.jsonl').open('x', encoding='utf-8', buffering=1)
    sequence = 0
    def mark(event, phase, **extra):
        nonlocal sequence
        sequence += 1
        log.write(json.dumps(dict(sequence=sequence, ns=time.perf_counter_ns(), event=event, phase=phase, **extra))+'\n')
    @contextmanager
    def phase(name, **extra):
        mark('begin', name, **extra)
        try: yield
        finally: mark('end', name, **extra)
    with phase('INTERPRETER_BASE'):
        time.sleep(.1)
    with phase('IMPORTS'):
        from tools import _s2uc_execution_v8 as e
        from tools import _s2uc_run_entry as entry
        import numpy
    with phase('IMPORTED_BASE'):
        time.sleep(.1)
    mark('environment', 'IDENTITY', pid=os.getpid(), python=sys.version,
         numpy=numpy.__version__, executable=sys.executable)
    def wrap(obj, name, label):
        original = getattr(obj, name)
        def call(*args, **kwargs):
            with phase(label): return original(*args, **kwargs)
        setattr(obj, name, call)
    wrap(e.binding, 'validate', 'PRESTART_VALIDATION')
    wrap(e.connection, 'execute', 'CONNECTION')
    wrap(e._Source, '__call__', 'MATERIALIZATION')
    wrap(e._Source, 'snapshot', 'SOURCE_COMPLETION')
    wrap(e._Owners, 'close', 'OWNER_CLEANUP')
    wrap(e.publication.codec, 'dumps', 'CODEC_ENCODE')
    wrap(e.publication.codec, 'loads', 'CODEC_DECODE')
    wrap(e._Publication, 'verify_record', 'TECHNICAL_VERIFICATION')
    wrap(e.publication.evaluation, 'evaluate', 'EVALUATION')
    wrap(e.publication._Publication, 'finish', 'PUBLICATION_FINISH')
    wrap(e.publication._Publication, 'failure', 'ERROR_CLOSURE')
    original_read = e.publication._read
    def read(path):
        with phase('REREAD_'+path.name): return original_read(path)
    e.publication._read = read
    original_atomic = e.publication._Publication.atomic
    def atomic(instance, name, data):
        with phase('PUBLISH_'+name): return original_atomic(instance, name, data)
    e.publication._Publication.atomic = atomic
    original_replace = e.publication.os.replace
    injected = 0
    def replace(source, target):
        nonlocal injected
        original_replace(source, target)
        if config['case'] == 'post_verification' and target.name == 'terminal.json' and injected == 0:
            injected += 1
            mark('fault', 'TERMINAL_AFTER_RENAME')
            raise OSError('TERMINAL_AFTER_RENAME')
    e.publication.os.replace = replace
    calls = 0
    def supplier(endpoint):
        nonlocal calls
        calls += 1
        if config['case'] == 'abort_58' and calls == 58:
            raise e.connection.S2UCConnectionError('LAST_ENDPOINT_FAILURE')
        return e.binding.ZERO_PCM
    with phase('RUN'):
        result = e.run_neutral(config['binding'], supplier, run_id=config['run_id'], output_directory=config['output'])
    with phase('RESULT_EXPORT'):
        save(folder/'result.json', result)
        facts = dict(supplier_calls=calls, injections=injected, neutral_gate=e.GATE,
                     public_gate=entry.MAIN_GATE, pid=os.getpid())
        save(folder/'facts.json', facts)
    with phase('FINAL_HOLD'):
        mark('ready', 'FINAL_SNAPSHOT')
        # Observer takes a final native snapshot before releasing the process.
        if sys.stdin.readline().strip() != 'release': raise RuntimeError('observer handshake lost')
    log.close()

def native_api():
    import ctypes as c
    from ctypes import wintypes as w
    class Counters(c.Structure):
        _fields_ = [('cb', w.DWORD), ('PageFaultCount', w.DWORD)] + [(name,c.c_size_t) for name in
          ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage',
           'QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
    kernel=c.WinDLL('kernel32',use_last_error=True); psapi=c.WinDLL('psapi',use_last_error=True)
    kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD]; kernel.OpenProcess.restype=w.HANDLE
    kernel.CloseHandle.argtypes=[w.HANDLE]; kernel.CloseHandle.restype=w.BOOL
    psapi.GetProcessMemoryInfo.argtypes=[w.HANDLE,c.POINTER(Counters),w.DWORD]
    psapi.GetProcessMemoryInfo.restype=w.BOOL
    def open_process(pid):
        handle=kernel.OpenProcess(0x410,False,pid)
        if not handle: raise c.WinError(c.get_last_error())
        return handle
    def read(handle):
        values=Counters(); values.cb=c.sizeof(values)
        if not psapi.GetProcessMemoryInfo(handle,c.byref(values),values.cb): raise c.WinError(c.get_last_error())
        return dict(working_set=values.WorkingSetSize,private_commit=values.PrivateUsage,
                    os_peak_working_set=values.PeakWorkingSetSize,os_peak_private_commit=values.PeakPagefileUsage)
    return open_process,read,kernel.CloseHandle

def prepare():
    import platform
    import numpy
    from tests.test_s2uc_execution_v8 import fixture
    from tools import _s2uc_binding_v8 as b
    from tools import _s2uc_dependencies as deps
    assert not (HERE/'plan.json').exists(), 'Do not overwrite a registered measurement'
    inv=b.current()
    accepted=json.loads((ROOT/'reports/s2uc/v8-neutral-integration-development-20260920/final/dependency-inventory.json').read_text())
    assert inv==accepted, 'Accepted code changed'
    scan=deps._scan(ROOT,Path(__file__).relative_to(ROOT).as_posix())
    union={r['path']:r for r in inv['files']}
    union.update({r['path']:r for r in scan['files']})
    code=sum(r['bytes'] for r in union.values())
    assert code<=720896
    save(HERE/'tool-code-inventory.json',dict(product_code_bytes=inv['code_bytes'],total_code_bytes=code,
         additional_files=[r for k,r in union.items() if k not in {x['path'] for x in inv['files']}],
         files=list(union.values()),external=scan['external']))
    save(HERE/'product-inventory.json',inv)
    save(HERE/'environment.json',dict(python=sys.version,executable=sys.executable,executable_sha256=sha(Path(sys.executable)),
         platform=platform.platform(),windows_version=list(sys.getwindowsversion()),machine=platform.machine(),
         numpy=numpy.__version__,numpy_config=str(numpy.show_config(mode='dicts')),
         clock=vars(time.get_clock_info('perf_counter')),observer='same interpreter, separate PID',
         environment={k:os.environ.get(k) for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','PYTHONMALLOC','PYTHONHASHSEED')}))
    cases=[]
    for name in ('success','abort_58','post_verification'):
        folder=HERE/name; folder.mkdir()
        path,run_id,output=fixture(folder,inv)
        case=dict(case=name,folder=str(folder),binding=str(path),run_id=run_id,output=str(output))
        save(folder/'case.json',case); cases.append(case)
    save(HERE/'plan.json',dict(version=1,created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
         scope='NEUTRAL_PROCESS_MEMORY_ONLY',cases=cases,runs_per_case=1,sampling_interval_ms=10,
         baseline_holds_ms=100,case_3_fault='existing terminal-after-rename fault, after verification publication',
         mechanism='external GetProcessMemoryInfo PROCESS_MEMORY_COUNTERS_EX; target phase markers only',
         metric_units='bytes',tool_sha256=sha(Path(__file__)),product_code_bytes=inv['code_bytes'],
         total_code_bytes_with_tool=code,guaranteed_ram_ceiling=False))

def observe():
    import subprocess
    plan=json.loads((HERE/'plan.json').read_text())
    assert sha(Path(__file__))==plan['tool_sha256']
    inventory=json.loads((HERE/'tool-code-inventory.json').read_text())
    assert all(sha(ROOT/r['path'])==r['sha256'] for r in inventory['files'])
    open_process,read,close=native_api()
    own=open_process(os.getpid())
    save(HERE/'observer-start.json',dict(pid=os.getpid(),memory=read(own)))
    for case in plan['cases']:
        folder=Path(case['folder'])
        # Exclusive start marker prevents silently rerunning any case.
        with (folder/'started.json').open('x') as f:
            json.dump(dict(ns=time.perf_counter_ns(),observer_pid=os.getpid()),f)
        with (folder/'stdout.txt').open('x') as out, (folder/'stderr.txt').open('x') as err:
            proc=subprocess.Popen([sys.executable,str(Path(__file__)),'child',str(folder/'case.json')],
                                  cwd=ROOT,stdin=subprocess.PIPE,stdout=out,stderr=err,text=True,
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            handle=open_process(proc.pid)
            released=False; errors=[]; count=0
            with (folder/'samples.jsonl').open('x',buffering=1) as raw:
                while proc.poll() is None:
                    begin=time.perf_counter_ns()
                    try:
                        target=read(handle); sampled=time.perf_counter_ns(); observer=read(own)
                        raw.write(json.dumps(dict(ns=sampled,query_start_ns=begin,target=target,observer=observer))+'\n')
                        count+=1
                    except OSError as exc:
                        errors.append(dict(ns=time.perf_counter_ns(),error=str(exc)))
                    phasefile=folder/'phases.jsonl'
                    if not released and phasefile.exists() and '"FINAL_SNAPSHOT"' in phasefile.read_text():
                        save(folder/'final-native-snapshot.json',dict(ns=time.perf_counter_ns(),target=read(handle),observer=read(own)))
                        proc.stdin.write('release\n');proc.stdin.flush(); released=True
                    time.sleep(max(0,.01-(time.perf_counter_ns()-begin)/1e9))
            close(handle); proc.stdin.close()
            save(folder/'process-exit.json',dict(pid=proc.pid,exit_code=proc.wait(),samples=count,errors=errors,
                                               final_handshake=released,observer_pid=os.getpid()))
    save(HERE/'observer-end.json',dict(pid=os.getpid(),memory=read(own)));close(own)

if __name__=='__main__':
    if sys.argv[1]=='prepare': prepare()
    elif sys.argv[1]=='observe': observe()
    elif sys.argv[1]=='child': child(json.loads(Path(sys.argv[2]).read_text()))
    elif sys.argv[1]=='api-check':
        op,read,close=native_api();h=op(os.getpid());print(read(h));close(h)
    else: raise ValueError('unknown mode')
