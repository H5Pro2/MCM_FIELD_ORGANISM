"""Evaluation routing only; unchanged Development judge and case procedure."""
from tools.s2uc_known_origin_development import *
OUT = ROOT/'reports/s2uc/known-origin-evaluation-analysis-20260930-01'

def evaluate():
    assert read(NEUTRAL/'tests.json')['status']=='PASS'
    p=read(gen.PLAN_PATH); gen.validate(p); spec=p['partitions']['evaluation']
    integrity,vectors=verify(ROOT/'reports/s2uc/known-origin-evaluation-20260930-01',spec)
    OUT.mkdir(exist_ok=False); save(OUT/'integrity.json',integrity)
    results={}; learning=[]
    for cid in ['T0','P1','P2','P3','N1','N2','N3','N4']:
        case=spec['cases'][cid]; values=[]; origins={}; roots=[]
        for key in case['learn']:
            n=len(values); origins[tuple(range(n+1,n+5))]=spec['episodes'][key]['root']
            values.extend(vectors[key]); roots.extend([spec['episodes'][key]['root']]*4)
        values.extend(vectors[case['query']][:3]); roots.extend([case['truth']]*3)
        result=evaluate_case(values,nj.PROFILE_DIGEST,len(values),len(values),Truth(case['truth'],case['positive'],origins,cid),measure_resources=True)
        save(OUT/(cid+'.json'),result); results[cid]=result
        for target in result['system']['targets'][:-1]:
            root=roots[target['target']-1]
            available={indices:r for indices,r in origins.items() if indices[-1]<=target['target']-3}
            learning.append(judge(target,Truth(root,root in available.values(),available,cid)))
        print(cid,result['evaluation']['origin_category'],flush=True)
    assert len(learning)==36
    assert results['T0']['system']['targets'][-1]['forecast']==results['N3']['system']['targets'][-1]['forecast']
    assert results['T0']['system']['states'][:10]==results['N3']['system']['states'][:10]
    rows=[r['evaluation'] for r in results.values()]
    summary=dict(status='COMPLETE',test_targets=aggregate(rows),test_rows=rows,
                 learning_targets=aggregate(learning),learning_rows=learning,
                 learning_definition='All other reachable targets, including the pair crossing learning/query boundary; positive means root available in a completed prior four-frame block.',
                 T0_N3_forecasts_and_pre_future_states_identical=True,
                 total_frames=sum(len(r['system']['admitted']) for r in results.values()),
                 partition='evaluation',
                 evaluation_authorization=read(ROOT/'docs/S2UC_HERKUNFT_EVALUATION_AUTORISIERUNG_20260930.json')['status'])
    assert summary['total_frames']==96 and summary['evaluation_authorization']=='AUTHORIZED_ONCE'
    gen.validate(read(gen.PLAN_PATH)); save(OUT/'result.json',summary)
    save(OUT/'bindings.json',dict(plan_sha256=sha(gen.PLAN_PATH),generator_sha256=sha(Path(gen.__file__)),
        observer_sha256=sha(Path(__file__)),implementation_bindings=p['implementation_bindings'],
        judge_sha256=sha(ROOT/'tools/_s2uc_origin_judge.py'),python=sys.version,
        profiles=dict(nj=nj.PROFILE_DIGEST,raw=nj.RAW_PROFILE_DIGEST)))
    print(json.dumps(summary['test_targets'],indent=2))


if __name__=='__main__': evaluate()
