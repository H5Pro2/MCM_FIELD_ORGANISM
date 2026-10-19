"""Neutral K05/K06 supplement: capture tickets BEFORE admission mutates stock."""
import hashlib
import json
from pathlib import Path
from tools._s2uc_k1 import create,POLICY
from tools._s2uc_multi_error import POLICY as MULTI
from tools._s2uc_pair_context_adapter import PerceptionSample


def main():
    root=Path(__file__).resolve().parents[1]
    folder=root/'reports/s2uc/k1-ticket-qualification-20261003-01'
    folder.mkdir(exist_ok=False)
    scenarios=dict(expiry=[0,1,0,1]*2+[0,1,2,3]+[0,1,0,1]*2+[4,5,6,7],
        promotion=[0]*8+[4,5,6,7],replacement=[0]*4+[0,1,2,3]+[4,5,0,0]+[4,5,6,7])
    evidence={}
    for name,indices in scenarios.items():
        a=create('2'*64,'neutral','stream',candidate_policy=POLICY,multi_policy=MULTI)
        captured={};rows=[]
        def checkpoint(stage,index):
            if stage=='frozen':
                captured['prediction_id']=id(a.pending_prediction)
                captured['ticket']=bytes(a.bank[192:400])
                captured['frames']=tuple(id(x) for x in a._frozen)
                captured['selected_id']=id(a.pending_prediction.context_values)
        a._checkpoint=checkpoint  # qualification observer, not a production dispatch
        try:
            for i,n in enumerate(indices,1):
                v=tuple(.25+(n+1)/256+j/65536 for j in range(48))
                sample=PerceptionSample(v,'2'*64,'neutral','stream',i,(i-1)*4800,i*4800)
                if a.pending_prediction:a.consume_feedback(sample)
                receipt=a.accept_perception(sample)
                if receipt:
                    assert id(a.pending_prediction)==captured['prediction_id']
                    assert bytes(a.bank[192:400])==captured['ticket']
                    assert tuple(id(x) for x in a._frozen)==captured['frames']
                    assert id(a.pending_prediction.context_values)==captured['selected_id']
                    rows.append(dict(target=i+1,ticket_sha256=hashlib.sha256(captured['ticket']).hexdigest(),
                        unchanged_across_admission=True))
            a.finish_story();assert a.closed and not any(a.bank) and not any(a._frozen)
        finally:
            if not a.closed:a._terminate()
        evidence[name]=dict(frames=len(indices),forecasts=rows,cleanup=True)
    (folder/'result.json').write_bytes((json.dumps(dict(id='K05c_K06c',status='PASS',
        evidence=evidence,reserved_research_cases_generated=0),indent=2)+'\n').encode())
    print('PASS: all frozen tickets and output identities unchanged across expiry, replacement and promotion')


if __name__=='__main__':main()
