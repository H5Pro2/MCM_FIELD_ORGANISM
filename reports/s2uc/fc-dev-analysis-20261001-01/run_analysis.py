"""Observer orchestration for authorized FC-DEV; never generates material."""
import json
from pathlib import Path
from tools import s2uc_factor_material as m
from tools._s2uc_factor_continuation_compare import compare,summarize
from tools._s2uc_origin_judge import Truth,judge
OUT=Path(__file__).resolve().parent
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
b,p=m.load_binding(m.BINDING);spec=p['partitions']['FC-DEV'];folder=m.ROOT/spec['output_directory']
rows=m.read_verified(folder,spec,'FC-DEV',p['profile'])
assert not (m.ROOT/p['partitions']['FC-EVAL']['output_directory']).exists()
save('preanalysis.json',dict(plan_sha256=m.sha(m.PLAN),production_binding_sha256=m.sha(m.BINDING),
    runner_sha256=m.sha(__file__),material={f.name:m.sha(f) for f in folder.iterdir()},profile=p['profile']))
cases={};learning={};deviations=[]
for cid,row in rows.items():
    roots={tuple(range(4*i+1,4*i+5)):spec['episodes'][k]['root'] for i,k in enumerate(spec['cases'][cid]['learn'])}
    result=compare(row['values'],row['profile']['digest'],Truth(row['truth'],row['positive'],roots,cid),measure_resources=True)
    save(cid+'.json',result);cases[cid]=result
    for n,t in enumerate(result['systems']['legacy']['targets'][:-1]):
        target=t['target'];root=row['origins'][target-1]['root']
        available={ix:r for ix,r in roots.items() if ix[-1]<=target-3}
        truth=Truth(root,root in available.values(),available,cid+'@'+str(target))
        learning[cid+'@'+str(target)]=dict(target=target,learning_targets=[],rows={policy:judge(system['targets'][n],truth) for policy,system in result['systems'].items()})
    expected={'AM':'AMBIGUOUS','NM':'ABSTAIN','ZF':'CORRECT'}.get(cid,'CORRECT')
    for policy in ('legacy','scaled'):
        r=result['rows'][policy]
        if r['origin_category']!=expected:deviations.append(dict(case_id=cid,policy=policy,expected=expected,actual=r['origin_category']))
    print(cid,result['rows']['scaled']['prediction_status'],flush=True)
assert len(cases)==11 and len(learning)==48
for policy in ('legacy','scaled'):
    for group in [('FH','GH','GR','GP'),('FD','GD')]:
        first=cases[group[0]]['systems'][policy]
        for cid in group[1:]:
            other=cases[cid]['systems'][policy]
            assert first['targets'][-1]['forecast']==other['targets'][-1]['forecast']
            assert first['states'][:10]==other['states'][:10]
    assert sum(len(c['systems'][policy]['admitted']) for c in cases.values())==129
# Separate candidate-role probe uses existing A material, no new synthesis.
a=m.read(folder/'base-A.json')['values'];q=rows['FH']['values'][-3:]
probe=compare(a+q,rows['FH']['profile']['digest'],Truth('FC-DEV/A',True,{(1,2,3,4):'FC-DEV/A'},'candidate_probe'),measure_resources=True)
save('candidate-probe.json',probe)
assert probe['rows']['scaled']['role']=='candidate'
summary=dict(status='COMPLETE',test_targets=summarize(cases),learning_targets=summarize(learning),
    learning_origin_definition='True root of target; positive only if in a prior completed four-frame block before the hint pair.',
    candidate_probe_separate=True,setup_deviations=deviations,causal_equal_prefix_checks=True,
    primary_frames_per_policy=129,primary_test_targets_per_policy=11,learning_targets_per_policy=48,
    candidate_frames_per_policy=7,FC_EVAL_unproduced=True)
save('result.json',summary)
pre=m.read(OUT/'preanalysis.json')
assert all(m.sha(folder/k)==h for k,h in pre['material'].items())
m.load_binding(m.BINDING)
assert not (m.ROOT/p['partitions']['FC-EVAL']['output_directory']).exists()
save('verification.json',dict(status='PASS',material_unchanged=True,code_plan_bindings_unchanged=True,
    FC_EVAL_unproduced=True,resources={cid:{k:r['resources'] for k,r in c['systems'].items()} for cid,c in cases.items()},
    material_bytes=sum(f.stat().st_size for f in folder.iterdir()),closure=m.read(folder/'closure.json')))
print(json.dumps(summary['test_targets']['full_means']),flush=True)
