"""Single supplementary native qualification; not the previous twelve tests."""
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2oe/visual-completion-qualification-20260912-01'
FILES=('tools/_s2oe_visual_completion.py','tools/_s2oe_visual_consistency.py',
       'tools/_s2oe_media_decoder.py','tools/_s2oe_decoder_worker.py',
       'tools/_s2oe_uhd_profile.py','tools/_s2oe_isolation_log.py',
       'tests/test_s2oe_visual_completion.py','reports/qualify_visual_completion_once.py',
       'docs/VISUELLER_DIAGNOSEANSCHLUSS.md','docs/VISUELLE_DIAGNOSE_FERTIGSTELLUNG.md',
       'mcm_field_organism/finite_video_path.py',
       'reports/s2oe/visual-consistency-qualification-20260912-01/preregistration.json',
       'reports/s2oe/visual-consistency-qualification-20260912-01/result.json',
       'reports/s2oe/visual-consistency-qualification-20260912-01/qualification.log')


def inventory():
    return {p:dict(bytes=(ROOT/p).stat().st_size,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in FILES}


def save(name,data):
    with (OUT/name).open('xb') as f:
        f.write(json.dumps(data,sort_keys=True,ensure_ascii=False,allow_nan=False).encode())


def main():
    if sys.argv[1:]==['prepare']:
        OUT.mkdir(exist_ok=False)
        inv=inventory()
        sources=sum(x['bytes'] for x in inv.values())+196608
        limits=dict(sources=327680,metadata=131072,shared=393216,total=4194304)
        totals=dict(sources=sources,metadata=114688,shared=sources,total=sources+114688)
        assert all(totals[k]<=limits[k] for k in limits),totals
        save('preregistration.json',dict(inventory=inv,limits=limits,totals=totals,
            neutral_input_reserve=196608,metadata_reserves=dict(log=32768,result=8192,
            binding_report_and_native_evidence=16384,numeric_table=57344),
            tests=['native_four_workers','native_error_forwarding','all_envelopes','envelope_overflow',
                   'exact_joint_boundary','joint_overflow_and_precheck','early_stop_and_failure',
                   'child_remaining_limit'],
            neutral_video=dict(frames=124,width=3840,height=2160,rate=[30000,1001],
                codec='libx264',preset='ultrafast',tune='zerolatency',crf='30',
                yuv_planes_constant=128,colorspace=1,color_range=1),
            selected_media_access=False,main_gate=False))
        print('BOUND',totals)
    elif sys.argv[1:]==['qualify']:
        bound=json.loads((OUT/'preregistration.json').read_bytes())
        assert inventory()==bound['inventory']
        with (OUT/'qualification.claim').open('xb') as f: f.write(b'once')
        os.environ['VISUAL_COMPLETION_OUT']=str(OUT)
        log=io.StringIO()
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2oe_visual_completion')
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
        raw=log.getvalue().encode()
        with (OUT/'qualification.log').open('xb') as f: f.write(raw)
        same=inventory()==bound['inventory']
        good=result.wasSuccessful() and result.testsRun==8 and same and len(raw)<=32768
        save('result.json',dict(status='QUALIFIED' if good else 'NOT_QUALIFIED',tests=result.testsRun,
            errors=len(result.errors),failures=len(result.failures),sources_unchanged=same,
            inventory=inventory(),log_bytes=len(raw),selected_media_access=False,main_gate=False))
        print(raw.decode()); print('QUALIFIED' if good else 'NOT_QUALIFIED')
    else: raise SystemExit('prepare or qualify')


if __name__=='__main__': main()
