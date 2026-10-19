"""Predetermined synthetic export workload; no research payloads or policy calls."""
import json
from pathlib import Path
from experiments.as480.common import raw
ROOT=Path(__file__).resolve().parents[2]
PACKAGE=ROOT/'reports/s2uc/rw1-budget-diagnosis-20261019-01'
BASE=PACKAGE/'artificial-base'
COUNTS=dict(sources=0,receptor=0,receptor_completed=0,nj=0,nj_completed=0,arms=0,references=0,
            policy_admissions=0,reference_admissions=0,decisions=0,arms_closed=0,references_closed=0)
CASES=('A0','A480','A2400','B0','B480','B2400')

def payload(n):
    obj={'kind':'ARTIFICIAL_EXPORT_ONLY','pad':''}
    obj['pad']='x'*(n-len(raw(obj)))
    assert len(raw(obj))==n
    return obj

def actions():
    """Exactly the same immutable operations for legacy and incremental paths."""
    out=[];counts=dict(COUNTS)
    def save(name,value,role='worker'):out.append(dict(kind='save',name=name,value=value,role=role))
    def event(key):
        if key!='BEGIN':counts[key]+=1
        out.append(dict(kind='append',name='observer/counts.jsonl',value=dict(event=key,counts=dict(counts)),role='worker'))
    save('observer/request.json',payload(250000),'supervisor')
    save('observer/gate.json',payload(128),'supervisor');save('observer/worker-entered.json',payload(128))
    event('BEGIN')
    for i in range(2):event('sources');out.append(dict(kind='bytes',name=f'material/source-{i}.fixture',bytes=76800,role='worker'))
    for i in range(390):
        for name in ('receptor','receptor_completed','nj','nj_completed'):event(name)
        save(f'material/projection-{i:03}.json',payload(3400+32*(i%8)))
    save('material/recipe.json',payload(512));save('material/manifest.json',payload(60000))
    for c in CASES:
        for arm in ('N','T'):
            event('arms');event('references')
            for i in range(1,12):
                if i in (3,5,7,9,11):event('decisions')
                event('policy_admissions');event('reference_admissions')
            event('arms_closed');event('references_closed')
            save(f'observer/{c}-{arm}.json',payload(28000))
    save('observer/evaluation.json',payload(280000));save('observer/independent-evaluation.json',payload(4096))
    save('observer/result.json',payload(1024));save('observer/worker-result.json',payload(128))
    save('closure/terminal.json',payload(2048),'supervisor');save('closure/technical-closure.json',payload(55000),'supervisor')
    save('closure/completion.json',payload(512),'supervisor')
    return out

def materialize_action(a):return b'F'*a['bytes'] if a['kind']=='bytes' else a['value']
def expected_files(stop):
    files={}
    for a in actions()[:stop]:
        n=a['bytes'] if a['kind']=='bytes' else len(raw(a['value']))
        files[a['name']]=files.get(a['name'],0)+n if a['kind']=='append' else n
    return files
def boundaries():return (0,800,1600,len(actions()))
