"""Exclusive ER1 neutral entry. Research remains unconditionally disabled."""
import argparse,hashlib,json,sys,time,traceback,unittest,tracemalloc
from pathlib import Path
from unittest.mock import patch
from tools import _s2uc_er1_engine as engine
from tools import _s2uc_ura1_delta_encode as codec
from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest
from tools._s2uc_er1_observer import compare,archive_form
from tools._s2uc_er1_archive import verify
from tools._s2uc_ulz1_resources import deep
from tools import s2uc_ura1_runtime_qualify as runtime
from tools._s2uc_ura1_fs_accounting_v4 import inventory,Terminal,Ledger
ROOT=Path(__file__).resolve().parents[1]
PREP=ROOT/'reports/s2uc/er1-preparation-20261017-01'
def raw(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def save(path,v):
    data=raw(v)
    if len(data)>1048576:raise ValueError('CLOSURE_LIMIT')
    if inventory(PREP)['total']+len(data)>8388608:raise ValueError('PREPARATION_LIMIT')
    path.write_bytes(data)
def fixture(tail):return engine.blocks([(.125,.25)]*2+[(.875,.75)]*2+[(.125,.25)]+[(.375,.25)]*2+tail)
def worker(out,mode):
    from tools import _s2uc_hx1_windows as win
    win.worker_membership();deadline=time.monotonic()+10
    while not (out/'gate').exists():
        if time.monotonic()>deadline:raise TimeoutError('GATE_TIMEOUT')
        time.sleep(.01)
    arms=[];start=time.monotonic();result=dict(mode=mode,neutral_only=True,cases=[])
    def checkpoint(a,m,i,s):
        if not any(a is x for x in arms):arms.append(a)
        if time.monotonic()-start>54000:raise TimeoutError('WORKER_LIMIT')
        if len(a.arm._observation_end)>2:raise ValueError('ENDMARK_LIMIT')
    engine.CHECKPOINT=checkpoint
    try:
        if mode=='tests':
            suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_er1')
            def ids(s):
                return [i for t in s for i in (ids(t) if isinstance(t,unittest.TestSuite) else [t.id()])]
            names=ids(suite)
            with (out/'tests.log').open('w',encoding='utf-8') as log:tested=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
            result['tests']=dict(ids=names,count=tested.testsRun,failures=[(t.id(),e) for t,e in tested.failures],errors=[(t.id(),e) for t,e in tested.errors])
            if not tested.wasSuccessful():raise AssertionError('TEST_FAILURE')
        else:
            tails=[[ (.125,.25)],[(.875,.75)],[(.125,.25)]*2+[(.875,.75)]*2]
            for n,tail in enumerate(tails,1):
                (out/'phase.txt').write_text('neutral_case_'+str(n))
                values=fixture(tail);expected_input=engine.raw(values)
                engine.VALIDATE=lambda v:engine.need(engine.raw(v)==expected_input,'BOUND_NEUTRAL_INPUT')
                resources={}
                for m in ('E','F'):
                    with patch.object(engine,'collection',list):measured=engine.run_arm(values,m,trace=False)['resources']
                    resources[m]={k:v for k,v in measured.items() if k not in ('calls','whole_operations','allocation_boundaries')}
                    resources[m]['measured_operations']=len(measured['calls'])
                    resources[m]['whole_conservative_peak']=max(x['whole_conservative'] for x in measured['whole_operations'])
                tracemalloc.start();base=tracemalloc.get_traced_memory()[0]
                try:
                    with codec.store(out) as owner:
                        e=engine.run_arm(values,'E',trace=True);f=engine.run_arm(values,'F',trace=True)
                        observer=compare(e,f)
                        record=dict(source=values,E=e,F=f,observer=archive_form(observer,codec.collection),neutral_only=True)
                        proof=manifest(record);expected=full_record_digest(record);archive=out/f'case-{n:02d}.gz'
                        if mode=='write_failure':
                            codec.write_archive(record,archive,expected,fault=True)
                            raise AssertionError('FAULT_NOT_RAISED')
                        sizes=codec.write_archive(record,archive,expected)
                        verified=verify(archive.read_bytes(),proof,expected)
                        save(out/f'case-{n:02d}-capture.json',proof)
                        save(out/f'case-{n:02d}-observer.json',dict(counts=observer['counts'],cost_balance=observer['cost_balance'],full_provenance_archive=archive.name))
                        current,peak=tracemalloc.get_traced_memory()
                        resource=dict(observer_deep_bytes=deep(observer),observer_json_bytes=len(raw(observer)),capture_decode_python_peak=peak-base,codec_dictionary=owner.bytes,codec_nodes=owner.entries,codec_edges=owner.edges,codec_indices=owner.indices,codec_record_peak=owner.record_peak,codec_temp_peak=owner.temp_peak,codec_collections=len(owner.items))
                finally:tracemalloc.stop()
                result['cases'].append(dict(case=n,frames=len(values),resources=resources,observer_resources=resource,archive=sizes,verification=verified))
        result['status']='PASS'
    except Exception as exc:
        result['status']='EXPECTED_FAILURE' if mode=='write_failure' and str(exc)=='INJECTED_WRITE' else 'FAIL'
        result['error']=repr(exc);result['traceback']=traceback.format_exc()
    finally:
        result['cleanup']=dict(arms=len(arms),all_closed=all(a.closed and not any(a.bank) for a in arms),codec_inactive=codec.ACTIVE is None,partial_files=[p.name for p in out.glob('*.partial')])
        result['seconds']=time.monotonic()-start;save(out/'worker.json',result)
    if result['status']=='FAIL':raise SystemExit(1)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['neutral','tests','write_failure','research']);parser.add_argument('--worker',action='store_true');args=parser.parse_args()
    if args.mode=='research':raise PermissionError('ER1_RESEARCH_NOT_AUTHORIZED_OR_BOUND')
    out=PREP/args.mode
    if args.worker:return worker(out,args.mode)
    runtime.install_job();PREP.mkdir(exist_ok=True);out.mkdir(exist_ok=False)
    runtime.PREP=PREP;runtime.TARGET=PREP
    terminal=Terminal(out,time.monotonic(),prep=inventory(PREP)['total'])
    ledger=Ledger(terminal,prep=inventory(PREP)['total']-inventory(out)['total'])
    result=dict(worker_terminated=False,seconds=0);ok=False
    try:
        result=runtime.child_job(out,[sys.executable,'-m','tools.s2uc_er1_prepare',args.mode,'--worker'],worker_limit=54000,total_limit=57600)
        evidence=json.loads((out/'worker.json').read_text()) if (out/'worker.json').exists() else {}
        inv=ledger.check();cleanup=evidence.get('cleanup',{})
        ok=result['failure'] is None and result['worker_terminated'] and cleanup.get('all_closed') and cleanup.get('codec_inactive') and cleanup.get('partial_files')==[] and inventory(PREP)['total']<=8388608
        terminal.value.update(status='PASS' if ok else 'FAIL',worker_ended=result['worker_terminated'],cleanup=cleanup,final_research_binding=False)
        if not ok:terminal.fail(result.get('failure') or 'WORKER_OR_CLEANUP_FAILURE')
    except Exception as exc:
        terminal.diagnose(exc,'neutral_supervision')
        terminal.value.update(status='FAIL',worker_ended=True)
    finally:terminal.save()
    print(json.dumps(dict(mode=args.mode,status='PASS' if ok else 'FAIL',seconds=result['seconds'],folder=str(out))))
    if not ok:raise SystemExit(1)
if __name__=='__main__':main()
