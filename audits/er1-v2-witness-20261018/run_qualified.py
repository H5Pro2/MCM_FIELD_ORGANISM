"""Single-process bounded archive audit; never executes a policy or bootstrap."""
import gc,hashlib,json,sys,time,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from checker_qualified import project,reconstruct,compare,counts
from tools.s2uc_ura1_runtime_qualify import install_job,runtime
from tools._s2uc_ura1_delta_fast_decode import Reader
from tools import _s2uc_hx1_windows as win
SOURCE=ROOT/'reports/s2uc/er1-v2-comparison-16h-01'
OUT=ROOT/'reports/s2uc/er1-v2-witness-audit-20261018-03'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    install_job();started=time.monotonic();OUT.mkdir(exist_ok=False)
    terminal=OUT/'terminal.json';terminal.write_bytes(b'{"status":"RUNNING"}'+b' '*(16384-20))
    def checkpoint():
        if time.monotonic()-started>54000:raise TimeoutError('WORKER_DEADLINE')
    def save(name,value):
        data=json.dumps(value,indent=2,sort_keys=True).encode()
        if len(data)>1048576 or sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())+len(data)>2097152:
            raise ValueError('REPORT_BUDGET')
        (OUT/name).write_bytes(data)
    result=dict(status='RUNNING',policy_executions=0,new_sources=0,bootstrap_draws=0,cases=[])
    try:
        import test_qualified
        suite=unittest.defaultTestLoader.loadTestsFromModule(test_qualified)
        ids=[t.id() for group in suite for t in group]
        with (OUT/'tests.log').open('w',encoding='utf-8') as f:tested=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
        save('tests.json',dict(status='PASS' if tested.wasSuccessful() else 'FAIL',count=tested.testsRun,ids=ids))
        if not tested.wasSuccessful():raise ValueError('QUALIFICATION_FAILED')
        manifest=json.loads((SOURCE/'delivery-closure.json').read_bytes())
        if sha(SOURCE/'delivery-closure.json')!='fc0633293f9c5d92e45e69cca9d1959c546d2252abce2c1daa8c76da90ed4bbd':raise ValueError('SOURCE_DELIVERY_BINDING')
        bindings={str((SOURCE/'delivery-closure.json').relative_to(ROOT)):sha(SOURCE/'delivery-closure.json')}
        for name,v in manifest['files'].items():
            checkpoint();p=SOURCE/name
            if sha(p)!=v['sha256']:raise ValueError('SOURCE_HASH:'+name)
            bindings[str(p.relative_to(ROOT))]=v['sha256']
        for p in list(HERE.glob('*.py'))+[ROOT/'tools/_s2uc_ura1_delta_fast_decode.py',ROOT/'tools/s2uc_ura1_runtime_qualify.py',ROOT/'tools/_s2uc_hx1_windows.py',ROOT/'docs/S2UC_ER1_ERFAHRUNGSERHALTUNG_KONZEPTVERTRAG_20261017.md']:
            bindings[str(p.relative_to(ROOT))]=sha(p)
        save('bindings.json',dict(files=bindings,runtime=runtime(),limits=dict(job=536870912,worker_seconds=54000,total_seconds=57600,administration=2097152,closure=1048576,export=67108864),method='SHA-bound prior archive integrity; independent semantic reconstruction, no policy/reference replay'))
        for i in range(1,33):
            checkpoint();tick=time.monotonic();path=SOURCE/f'case-{i:02d}.gz'
            reader=Reader(path.read_bytes());root=reader.value(reader.doc['root'])
            if root['entry_revision']!='ER1_V2' or root['neutral_only'] is not False:raise ValueError('ARCHIVE_SCOPE')
            source=root['source']
            if len(source)!=1024:raise ValueError('SOURCE_FRAMES')
            data={m:project(reader,root[m],source,checkpoint) for m in ('E','F')}
            expected,rejected=reconstruct(data,source)
            reported=[json.loads(x) for x in reader.records(root['mechanisms']['$sequence'])]
            differences=compare(expected,reported)
            for values in differences.values():
                for record in values:
                    if 'output' in record:
                        record['output_sha256']=hashlib.sha256(json.dumps(record.pop('output')).encode()).hexdigest()
            record=dict(case=i,archive_sha256=sha(path),expected=counts(expected),reported=counts(reported),differences=differences,rejected_candidates=rejected,seconds=time.monotonic()-tick,decoder=reader.stats)
            record['status']='PASS' if not any(differences.values()) else 'DISCREPANCY'
            save(f'case-{i:02d}.json',record)
            result['cases'].append(record)
            print(json.dumps(dict(case=i,status=record['status'],seconds=record['seconds'])),flush=True)
            del reader,root,source,data,expected,reported;gc.collect()
        # Recheck all source and checker hashes after the audit.
        for name,h in bindings.items():
            if sha(ROOT/name)!=h:raise ValueError('POST_HASH:'+name)
        forbidden=('tools._s2uc_er1_run_mechanisms','tools._s2uc_er1_run_observer','tools._s2uc_er1_run_engine','tools._s2uc_er1_engine')
        if any(n in sys.modules for n in forbidden):raise ValueError('FORBIDDEN_IMPORT')
        result['status']='PASS' if all(x['status']=='PASS' for x in result['cases']) else 'DISCREPANCY'
        result['forbidden_imports_absent']=True
    except Exception as exc:
        result.update(status='ERROR',error=repr(exc))
        raise
    finally:
        result.update(seconds=time.monotonic()-started,job=win.snapshot(),partial_files=[str(p) for p in OUT.glob('*.partial')])
        summary={k:v for k,v in result.items() if k!='cases'}
        summary['completed_cases']=[x['case'] for x in result['cases']]
        terminal_data=json.dumps(summary).encode()
        if len(terminal_data)>16384:raise ValueError('TERMINAL_SIZE')
        terminal.write_bytes(terminal_data+b' '*(16384-len(terminal_data)))
        save('result.json',summary)
    print(json.dumps(dict(status=result['status'],seconds=result['seconds'],job=result['job'])))

if __name__=='__main__':main()
