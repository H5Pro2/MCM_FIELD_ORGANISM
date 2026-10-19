"""Neutral direct candidate-full-repeat priority at a complete block boundary."""
import json
from pathlib import Path
from tests.test_s2uc_a1 import ready,receipt,vector
from tools._s2tu_retained_trace import Frame


def main():
    out=Path(__file__).resolve().parents[1]/'reports/s2uc/a1-full-candidate-20261004-01'
    out.mkdir(exist_ok=False)
    a,n=ready(candidate=(0,1,0,1));original=a.arm._candidate.frames
    try:
        for i,v in enumerate((0,1),n+1):a.arm.form(Frame(vector(v),'a'*64,'neutral-a1','hint',i))
        f=json.loads(receipt(a,n+2,(0,1)).json_text)
        assert sum(h['eligible'] for h in f['hypotheses'])==1
        assert f['a1_admission'] is None and a.arm._candidate is not None
        for frame in a.pair:a._admit(frame)
        assert a.arm._candidate is None and a.arm._retained_many[-1].frames is original
        (out/'result.json').write_text(json.dumps(dict(status='PASS',exact_full_candidate_priority=True,
            no_partial_admission=True,original_identity=True,receipt=f,neutral_only=True),indent=2)+'\n',encoding='utf-8')
    finally:
        a._terminate();assert not any(a.bank) and not any(a._frozen)


if __name__=='__main__':main()
