"""Recompute memory phases and functional checks from preserved files; no runs."""
import hashlib
import json
from pathlib import Path
import statistics
import csv
from collections import defaultdict

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def load(path): return json.loads(path.read_text())
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value): path.write_text(json.dumps(value,indent=2)+'\n')
plan=load(HERE/'plan.json')
inventory=load(HERE/'tool-code-inventory.json')
assert all(sha(ROOT/r['path'])==r['sha256'] for r in inventory['files'])
summary=[]
for config in plan['cases']:
    folder=Path(config['folder']); output=Path(config['output'])
    events=[json.loads(s) for s in (folder/'phases.jsonl').read_text().splitlines()]
    samples=[json.loads(s) for s in (folder/'samples.jsonl').read_text().splitlines()]
    stack=[]; intervals=[]
    for event in events:
        if event['event']=='begin': stack.append(event)
        if event['event']=='end':
            start=stack.pop(); assert start['phase']==event['phase']
            intervals.append(dict(phase=start['phase'],start_ns=start['ns'],end_ns=event['ns'],
                                  duration_ms=(event['ns']-start['ns'])/1e6))
    assert not stack
    phases=defaultdict(list)
    for interval in intervals:
        values=[s for s in samples if interval['start_ns']<=s['ns']<=interval['end_ns']]
        interval.update(samples=len(values),sampled_max={key:max((s['target'][key] for s in values),default=None)
                         for key in ('working_set','private_commit')})
        phases[interval['phase']].append(interval)
    phase_summary={name:dict(intervals=len(rows),duration_ms=sum(r['duration_ms'] for r in rows),
        sampled_intervals=sum(bool(r['samples']) for r in rows),sample_count=sum(r['samples'] for r in rows),
        sampled_max={k:max((r['sampled_max'][k] for r in rows if r['samples']),default=None)
                     for k in ('working_set','private_commit')}) for name,rows in phases.items()}
    save(folder/'phase-intervals.json',sorted(intervals,key=lambda r:r['start_ns']))
    save(folder/'phase-summary.json',phase_summary)
    with (folder/'timeline.csv').open('w',newline='') as stream:
        writer=csv.writer(stream)
        writer.writerow(('phase','start_ms','end_ms','samples','sampled_ws_bytes','sampled_commit_bytes'))
        for r in sorted(intervals,key=lambda r:r['start_ns']):
            writer.writerow((r['phase'],(r['start_ns']-events[0]['ns'])/1e6,(r['end_ns']-events[0]['ns'])/1e6,
                             r['samples'],r['sampled_max']['working_set'],r['sampled_max']['private_commit']))
    result=load(folder/'result.json'); facts=load(folder/'facts.json'); process=load(folder/'process-exit.json')
    expected_success=config['case']=='success'; expected_count=57 if config['case']=='abort_58' else 58
    expected_error={'success':None,'abort_58':'LAST_ENDPOINT_FAILURE','post_verification':'TERMINAL_AFTER_RENAME'}[config['case']]
    assert process['exit_code']==0 and process['errors']==[] and process['final_handshake']
    assert process['pid']==facts['pid'] and process['pid']!=process['observer_pid']
    assert result['status']==('CLOSED_NEUTRAL_VERIFIED' if expected_success else 'NOT_EVALUABLE')
    assert result['primary_error']==expected_error and result['evaluation_allowed']==expected_success
    assert facts['supplier_calls']==58 and facts['injections']==int(config['case']=='post_verification')
    assert facts['neutral_gate']==facts['public_gate']==False and all(r['closed'] for r in result['owner_cleanup'])
    assert len(result['owner_cleanup'])==6
    source=result['source_completion']; assert source['attempts']==58 and source['successes']==expected_count
    assert all(v==expected_count for v in source['counters'].values())
    assert source['status']==('PARTIAL' if expected_count==57 else 'COMPLETE')
    assert result['accounting_complete'] and result['actual']['within_limits']
    amount=defaultdict(int)
    for ref in result['inputs']:
        path=Path(ref['root'])/ref['path'];assert path.stat().st_size==ref['bytes'] and sha(path)==ref['sha256']
        amount[ref['category']]+=path.stat().st_size
    for ref in result['result_inventory']:
        path=output/ref['path'];assert path.stat().st_size==ref['bytes'] and sha(path)==ref['sha256']
        amount[ref['category']]+=path.stat().st_size
    assert set(p.name for p in output.iterdir())=={r['path'] for r in result['result_inventory']}
    assert dict(amount)=={k:v for k,v in result['actual']['categories'].items() if v}
    assert sum(amount.values())==result['actual']['total_bytes']
    proof=load(output/'verification.json'); assert proof['record']['sha256']==sha(output/'record.json')
    assert proof['technical']['status']==('VERIFIED_FAILURE' if expected_count==57 else 'VERIFIED')
    if config['case']=='post_verification':
        assert {'record.json','verification.json','error.json','terminal.json','terminal-minimal.json'}==set(p.name for p in output.iterdir())
        assert load(output/'error.json')['primary_error']==expected_error
    gaps=[(b['ns']-a['ns'])/1e6 for a,b in zip(samples,samples[1:])]
    last=load(folder/'final-native-snapshot.json')
    row=dict(case=config['case'],pid=process['pid'],observer_pid=process['observer_pid'],samples=len(samples),
       sampled_target_max={k:max(s['target'][k] for s in samples) for k in ('working_set','private_commit')},
       final_native=last['target'],sampled_observer_max={k:max(s['observer'][k] for s in samples) for k in ('working_set','private_commit')},
       intervals_ms=dict(min=min(gaps),median=statistics.median(gaps),max=max(gaps),over_20_ms=sum(g>20 for g in gaps)),
       max_query_duration_ms=max((s['ns']-s['query_start_ns'])/1e6 for s in samples),
       phases=phase_summary,status=result['status'],primary_error=result['primary_error'],source=source,
       functional_checks='PASS',actual=result['actual'],missing_durable_evidence=result['missing_durable_evidence'])
    summary.append(row)
save(HERE/'summary.json',summary)
tool_files=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)) for p in (HERE/'measure.py',Path(__file__))]
total=inventory['product_code_bytes']+sum(r['bytes'] for r in tool_files)
assert total<=720896
save(HERE/'complete-tool-scope.json',dict(product_code_bytes=inventory['product_code_bytes'],tool_files=tool_files,
     tool_bytes=sum(r['bytes'] for r in tool_files),total_code_bytes=total,limit=720896,remaining=720896-total,
     additional_project_dependencies=[],product_and_tests_unchanged=True))
print(json.dumps([dict(case=r['case'],sampled=r['sampled_target_max'],native=r['final_native'],
      observer=r['sampled_observer_max'],gaps=r['intervals_ms'],status=r['status']) for r in summary],indent=2))
