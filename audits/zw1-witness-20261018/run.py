"""Bounded sequential ZW1 archive audit; unchanged ER1 semantic checker."""
import gc,hashlib,json,sys,time,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
BASE=ROOT/'audits/er1-v2-witness-20261018'
sys.path[:0]=[str(ROOT),str(BASE)]
from checker_qualified import project,reconstruct,compare,counts
from adapter import bind_case,descriptive,examples,digest,need
from tools.s2uc_ura1_runtime_qualify import install_job,runtime
from tools._s2uc_ura1_delta_fast_decode import Reader
from tools import _s2uc_hx1_windows as win

SOURCE=ROOT/'reports/s2uc/zw1-comparison-16h-01'
OLD=ROOT/'reports/s2uc/er1-v2-witness-audit-20261018-03'
OUT=ROOT/'reports/s2uc/zw1-witness-audit-20261018-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_bytes())

def main():
    install_job();started=time.monotonic();OUT.mkdir(exist_ok=False)
    terminal=OUT/'terminal.json'
    terminal.write_bytes(b'{"status":"RUNNING"}'+b' '*16364)
    bindings={};active=None;reader=None
    def checkpoint():
        if time.monotonic()-started>54000:raise TimeoutError('WORKER_DEADLINE')
    def save(name,value):
        checkpoint();data=json.dumps(value,sort_keys=True,indent=2).encode()
        need(len(data)<=1048576,'FILE_BUDGET')
        need(sum(p.stat().st_size for p in OUT.iterdir() if p.is_file())+len(data)<=2097152,'REPORT_BUDGET')
        with (OUT/name).open('xb') as f:f.write(data)
    def bind(path,expected=None):
        h=sha(path);need(expected is None or h==expected,'BINDING:'+str(path))
        bindings[path.relative_to(ROOT).as_posix()]=h
    def manifest(path,expected):
        bind(path,expected);v=load(path)
        for n,x in v['files'].items():
            checkpoint();p=path.parent/n;need(p.stat().st_size==x['bytes'],'SIZE:'+n);bind(p,x['sha256'])
        return v
    result=dict(status='RUNNING',workflow='0f057ea1-94b9-496c-a771-0987161a1186',policy_executions=0,new_research_sources=0,bootstrap_draws=0,completed_cases=[],cases=[])
    try:
        original=manifest(SOURCE/'delivery-closure.json','bad2f49c9f46a5e743767c0ee37091ddde7e254d6b5063050ae1c941965c2731')
        for n,x in original['admission_files'].items():bind(ROOT/n,x['sha256'])
        manifest(OLD/'delivery-manifest.json','71eb768ffc30ee15144df276c0f105a4f875bc19a7ec86b8a54e580f36314392')
        oldbindings=load(OLD/'bindings.json')
        for n,h in oldbindings['files'].items():bind(ROOT/n,h)
        need(load(OLD/'tests.json')['status']=='PASS' and load(OLD/'tests.json')['count']==12,'INHERITED_TESTS')
        need(sha(BASE/'checker_qualified.py')=='4ea7148b1bcc581c00e039c05b229760753a5a35a19c2afe55f6c712dd41c518','SEMANTIC_CORE')
        for p in list(HERE.glob('*.py'))+[ROOT/'tools/_s2uc_ura1_delta_fast_decode.py',ROOT/'tools/s2uc_ura1_runtime_qualify.py',ROOT/'tools/_s2uc_hx1_windows.py',ROOT/'docs/S2UC_ZW1_ZEITLICHE_WIEDERKEHR_KONZEPTVERTRAG_20261018.md']:
            bind(p)
        save('bindings.json',dict(files=bindings,runtime=runtime(),limits=dict(job=536870912,processes=1,worker_seconds=54000,total_seconds=57600,administration=2097152,closure=1048576,export=67108864),inherited_tests=dict(count=12,status='PASS',rerun=False,path=str(OLD/'tests.json')),semantic_core_changed=False))
        import test_adapter
        suite=unittest.defaultTestLoader.loadTestsFromModule(test_adapter)
        ids=[t.id() for group in suite for t in group]
        with (OUT/'tests.log').open('x',encoding='utf-8') as f:tested=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
        save('tests.json',dict(status='PASS' if tested.wasSuccessful() else 'FAIL',count=tested.testsRun,ids=ids,errors=len(tested.errors),failures=len(tested.failures)))
        need(tested.wasSuccessful(),'NEW_MAPPING_QUALIFICATION')
        entries=load(SOURCE/'sources-manifest.json')
        need(entries['namespace']=='MCM-ZW1/source/v1' and entries['all_before_policy'],'SOURCE_MANIFEST')
        need([(e['pair'],e['condition']) for e in entries['entries']]==[(i,c) for i in range(1,17) for c in ('A','B')],'MANIFEST_COVERAGE')
        for i in range(1,33):
            checkpoint();active=i;tick=time.monotonic();path=SOURCE/f'case-{i:02d}.gz'
            need(sha(path)==original['files'][path.name]['sha256'],'ARCHIVE_HASH')
            reader=Reader(path.read_bytes());root=reader.value(reader.doc['root'])
            entry=entries['entries'][i-1];source_path=SOURCE/entry['path']
            summary=load(SOURCE/f'case-{i:02d}-summary.json');receipt=load(SOURCE/f'pair-{(i+1)//2:02d}-receipt.json')
            pair,label,source,condition=bind_case(i,entry,load(source_path),root,summary,receipt,sha(source_path))
            data={m:project(reader,root[m],source,checkpoint) for m in ('E','F')}
            for m in ('E','F'):
                need([data[m]['targets'][k]['error'] for k in condition['targets']]==condition[m],'RECEIPT_ERROR_BINDING')
            expected,rejected=reconstruct(data,source);checkpoint()
            reported=[json.loads(x) for x in reader.records(root['mechanisms']['$sequence'])]
            differences=compare(expected,reported)
            for group in differences.values():
                for record in group:
                    x=record.get('record',record)
                    if 'output' in x:x['output_sha256']=digest(x.pop('output'))
            c=counts(expected)
            for m in ('E','F'):
                for k in ('retention_events','warm_uses','local_gains'):need(c[m][k]==summary['mechanisms'][m][k],'SUMMARY_WITNESS_COUNT')
            record=dict(case=i,pair=pair,condition=label,archive_sha256=sha(path),source_sha256=sha(source_path),expected=c,reported=counts(reported),descriptive=descriptive(expected),differences=differences,rejected_candidates=rejected,
                expected_multiset_sha256=digest(sorted(expected,key=lambda x:json.dumps(x,sort_keys=True))),examples=examples(expected),seconds=time.monotonic()-tick,decoder=reader.stats)
            record['status']='PASS' if not any(differences.values()) else 'DISCREPANCY'
            save(f'case-{i:02d}.json',record);result['cases'].append(record);result['completed_cases'].append(i)
            print(json.dumps(dict(case=i,status=record['status'],seconds=record['seconds'])),flush=True)
            del reader,root,source,data,expected,reported,receipt,condition,summary;reader=None;gc.collect();active=None
        for n,h in bindings.items():need(sha(ROOT/n)==h,'POST_BINDING:'+n)
        forbidden=('tools._s2uc_er1_run_mechanisms','tools._s2uc_er1_run_observer','tools._s2uc_er1_run_engine','tools._s2uc_er1_engine')
        need(not any(n in sys.modules for n in forbidden),'FORBIDDEN_IMPORT')
        totals={}
        for label in ('A','B'):
            for arm in ('E','F'):
                rows=[c for c in result['cases'] if c['condition']==label];values=[c['descriptive'][arm] for c in rows]
                sums={k:sum(x[k] for x in values) for k in values[0] if k!='multi_assigned_targets'}
                sums['multi_assigned_targets']=[dict(pair=c['pair'],target=int(k),count=n) for c in rows for k,n in c['descriptive'][arm]['multi_assigned_targets'].items()]
                sums.update(stories=16,target_denominator=8176,block_ends=4096)
                totals[label+'/'+arm]=sums
        save('totals.json',dict(groups=totals,unit='unique targets are (pair,condition,arm,target); no cross-arm summation',inference='descriptive only; no causal decomposition or new significance tests'))
        result.update(status='PASS' if all(x['status']=='PASS' for x in result['cases']) else 'DISCREPANCY',forbidden_imports_absent=True,post_bindings='PASS')
    except Exception as exc:
        result.update(status='ERROR',error=repr(exc),active_case=active)
        raise
    finally:
        reader=None;gc.collect()
        result.update(seconds=time.monotonic()-started,job=win.snapshot(),actual_processes=1,partial_files=[p.name for p in OUT.glob('*.partial')],active_case=active)
        final={k:v for k,v in result.items() if k!='cases'}
        data=json.dumps(final).encode();need(len(data)<=16384,'TERMINAL_SIZE')
        terminal.write_bytes(data+b' '*(16384-len(data)))
        save('result.json',final)
    print(json.dumps(final))

if __name__=='__main__':main()
