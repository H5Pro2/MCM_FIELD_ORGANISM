"""Neutral six-cell stock: measure admission, eviction and warm-key transfer."""
import json
import sys
from pathlib import Path
from tests.test_s2uc_a1 import ready,vector
from tools._s2tu_retained_trace import Frame
from tools._s2uc_multi_observer import Meter
from tools._s2uc_multi_error import CELL


def main():
    out=Path(__file__).resolve().parents[1]/'reports/s2uc/a1-warm-stock-20261004-01'
    out.mkdir(exist_ok=False);results={}
    for trace in (False,True):
        a,n=ready([(4,5,6,7),(8,9,10,11)])
        try:
            original=a.arm._candidate.frames
            sources=[(0,t.generation) for t in a.arm._retained_many]+[(1,a.arm._candidate.candidate_generation)]
            for slot,(role,generation) in enumerate(sources):
                for off in (0,1):CELL.pack_into(a.bank,(slot*2+off)*32,generation,.001,.002,role,off,0,1)
            for i in (n+1,n+2):a.arm.form(Frame(vector(30),'a'*64,'neutral-a1','hint',i))
            a.pair=[Frame(vector(v),'a'*64,'neutral-a1','hint',n+3+j) for j,v in enumerate((0,1))]
            a.arm.hint(a.pair[0]);matched=a.arm.hint(a.pair[1]);meter=Meter(a)
            def call():return a._receipt(matched['decision'],[n+3,n+4],[(0,4800),(4800,9600)],matched['matches'])
            if trace:
                old=sys.gettrace();sys.settrace(meter.trace)
                try:receipt=call()
                finally:sys.settrace(old)
            else:receipt=meter.measure('receipt',call)
            data=json.loads(receipt.json_text)
            assert data['decision']=='SELECTED_BY_ERROR' and data['a1_admission']['victim']['generation']==1
            assert a.arm._retained_many[-1].frames is original
            meter.receipt=len(receipt.json_text.encode())
            assert meter.receipt<=16384
            results['trace' if trace else 'heap']=dict(resources=meter.snapshot(),receipt=data)
        finally:
            a._terminate();assert a.closed and not any(a.bank) and not any(a._frozen)
    (out/'result.json').write_text(json.dumps(dict(status='PASS',initial_cells=6,original_identity=True,
        measurements=results,cleanup=True,neutral_only=True),indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v['resources'] for k,v in results.items()}))


if __name__=='__main__':main()
