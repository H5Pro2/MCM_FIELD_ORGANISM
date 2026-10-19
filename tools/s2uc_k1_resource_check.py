"""Supplemental neutral K08 trace: an actual selected context uses two outputs."""
import json
from pathlib import Path
from tools._s2uc_k1_probe import probe


def main():
    root=Path(__file__).resolve().parents[1]
    folder=root/'reports/s2uc/k1-two-output-qualification-20261003-01'
    folder.mkdir(exist_ok=False)
    def vector(i):return tuple(.25+(i+1)/256+j/65536 for j in range(48))
    indices=(0,1,2,3,0,1,2,12,0,1,0,14)
    result=probe([vector(i) for i in indices],enabled=True,trace=True)
    assert any(x['decision']=='SELECTED_BY_ERROR' for x in result['outputs'])
    assert result['resources']['output_slots_peak']==2
    assert result['resources']['original_frames_peak']<=18
    assert result['resources']['combined_peak']<=20
    (folder/'trace.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
    (folder/'result.json').write_bytes((json.dumps(dict(id='K08b',status='PASS',
        neutral_frames=12,resources=result['resources'],cleanup=result['cleanup'],
        reserved_research_cases_generated=0),indent=2)+'\n').encode())
    print(json.dumps(result['resources']))


if __name__=='__main__':main()
