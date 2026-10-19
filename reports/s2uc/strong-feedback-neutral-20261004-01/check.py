"""Exactly four authorized 28-frame neutral lifecycle cases; no production edits."""
import hashlib
import json
import time
from pathlib import Path
from tools._s2uc_a1_compare_engine import replay

OUT=Path(__file__).resolve().parent
def save(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

def main():
    assert not (OUT/'verification.json').exists(), 'ALREADY_COMPLETED'
    start=time.perf_counter()
    v={k:tuple(x+j/4096 for j in range(48)) for k,x in
       dict(H1=1/8,H2=1/2,A=1/4,B=3/4,Z=3/8).items()}
    summaries=[]
    for older in ('A','B'):
        for ending in ('A','B'):
            name=older+'-'+ending
            blocks=['A','A','B','B',older,'Z',ending]
            values=[v[k] for y in blocks for k in ('H1','H2',y,'H1')]
            r=replay(values,hashlib.sha256(('neutral-strength:'+name).encode()).hexdigest(),False,lambda:None)
            save(name+'.json',r)
            assert r['frames']==28 and r['reference_advances']==28
            assert r['reference_equal'] and r['cleanup'] and r['censored_target']==29
            row=next(x for x in r['rows'] if x['target']==27)
            hs={h['original']:h for h in row['hypotheses']}
            assert set(hs)=={3,11,23}
            assert hs[3]['ordinals']==[1,2,3,4] and hs[11]['ordinals']==[9,10,11,12]
            assert hs[23]['ordinals']==[21,22,23,24]
            assert hs[23]['before'] is None and hs[23]['prior_feedback']==[]
            expected=((5/32,3/16),(5/16,3/16)) if older=='A' else ((9/32,3/16),(3/16,3/16))
            assert tuple(hs[3]['before'])==expected[0] and tuple(hs[11]['before'])==expected[1]
            assert (None if row['selected'] is None else row['selected']['original'])==(3 if older=='A' else None)
            forecast=next(f for f in r['forecasts'] if f['input_indices']==[25,26])
            zh=next(h for m,h in zip(forecast['matches'],forecast['hypotheses']) if m['ordinals']==[21,22,23,24])
            assert zh['eligible'] and zh['evaluation']=='COLD'
            # Independent last-feedback computation by immutable original lineage;
            # all eligible feedback, selected or not. No production L arm/state.
            past={}
            for x in r['rows']:
                if x['target']>=27:break
                for h,u in zip(x['hypotheses'],x['updates'],strict=True):
                    if u['live']:past[h['original']]=(u['ec'],u['ep'],x['target'])
            pairs={o:past.get(o) for o in hs}
            assert pairs[3]==(1/8,1/8,23) and pairs[11]==(3/8,1/8,23) and pairs[23] is None
            negatives=[(p[0]-p[1],o) for o,p in pairs.items() if p is not None and p[0]<p[1]]
            assert not negatives
            l_error=sum(abs(a-b) for a,b in zip(v['H2'],v[ending]))/48
            assert l_error==.25
            assert row['error']==(0. if ending=='A' else .5) if older=='A' else row['error']==.25
            post=next(e for e in r['events'] if e['index']==27)['before_cells']
            zcell=next(c for c in post if c['key']==hs[23]['key'])
            assert zcell['prior_feedback']==[27]
            assert zcell['values']==[1/8 if ending=='A' else 3/8,1/4]
            assert all(u['live'] for u in row['updates']) and len(row['updates'])==3
            for at in (16,20,24,26,28):
                stock=next(e for e in r['events'] if e['index']==at)['after']
                assert sorted(t['ordinals'] for t in stock['retained'])==[[1,2,3,4],[9,10,11,12]]
            assert {c['at'] for c in r['full_confirmations']}=={8,16,20,28}
            summaries.append(dict(case=name,blocks=blocks,reference_equal=True,cleanup=True,
                U='A' if older=='A' else 'P',L='P',U_error=row['error'],L_error=l_error,
                delta=row['error']-l_error,pretarget_errors=expected,L_last_feedback=pairs,
                Z_first_feedback=zcell,resources=r['resources'],confirmations=r['full_confirmations']))
    save('verification.json',dict(status='PASS',cases=summaries,frames=112,
         independent_reference_advances=112,production_arms=4,L_production_arms=0,
         research_cases=0,seconds=time.perf_counter()-start,
         script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    print(json.dumps(summaries,indent=2))

if __name__=='__main__':main()
