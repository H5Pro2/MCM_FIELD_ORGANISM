"""Neutral worst-case six-hypothesis receipt and factor exclusion."""
import json
import sys
from pathlib import Path
from tests.test_s2uc_a1 import ready,receipt,vector
from tools._s2tu_retained_trace import Frame
from tools._s2uc_multi_observer import Meter


def main():
    out=Path(__file__).resolve().parents[1]/'reports/s2uc/a1-six-hypotheses-20261004-01'
    out.mkdir(exist_ok=False);results={}
    for traced in (False,True):
        a,n=ready([(0,0,0,1),(0,0,0,2)],(0,0,0,3))
        try:
            for i in (n+1,n+2):a.arm.form(Frame(vector(7),'a'*64,'neutral-a1','hint',i))
            # Existing observed pair; no hidden extra Frame allocation during receipt.
            a.pair=[Frame(vector(0),'a'*64,'neutral-a1','hint',i) for i in (n+3,n+4)]
            a.arm.hint(a.pair[0]);matches=a.arm.hint(a.pair[1]);meter=Meter(a)
            def call():return a._receipt(matches['decision'],[n+3,n+4],[(0,4800),(4800,9600)],matches['matches'])
            if traced:
                old=sys.gettrace();sys.settrace(meter.trace)
                try:r=call()
                finally:sys.settrace(old)
            else:r=meter.measure('receipt',call)
            data=json.loads(r.json_text);assert sum(h['eligible'] for h in data['hypotheses'])==6
            assert data['a1_admission'] is None
            meter.receipt=len(r.json_text.encode());assert meter.receipt<=16384
            results['trace' if traced else 'heap']=dict(resources=meter.snapshot(),receipt=data)
        finally:
            a._terminate();assert not any(a.bank) and not a.arm._retained_many and a.arm._candidate is None
    # Nonzero dyadic scaling produces a raw match but never an eligible A1 admission.
    a,n=ready()
    try:
        a.pair=[Frame(tuple(2*x for x in vector(v)),'a'*64,'neutral-a1','hint',n+i+1) for i,v in enumerate((0,1))]
        a.arm.hint(a.pair[0]);m=a.arm.hint(a.pair[1])
        assert m['matches'] and all(x['factors']==[2.0] for x in m['matches'])
        assert a._admission_match(m['matches']) is None
    finally:a._terminate()
    (out/'result.json').write_text(json.dumps(dict(status='PASS',six_eligible=True,factor_excluded=True,
        cleanup=True,measurements=results,neutral_only=True),indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v['resources'] for k,v in results.items()}))


if __name__=='__main__':main()
