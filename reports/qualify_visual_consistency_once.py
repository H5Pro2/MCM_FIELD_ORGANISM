"""One neutral qualification; prebound complete reserves, no real media."""
import hashlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2oe/visual-consistency-qualification-20260912-01'
FILES=('docs/VISUELLER_EINGANGSKONSISTENZVERGLEICH.md',
       'docs/VISUELLER_DIAGNOSEANSCHLUSS.md',
       'tools/_s2oe_media_decoder.py','tools/_s2oe_decoder_worker.py',
       'tools/_s2oe_isolation_log.py','tools/_s2oe_uhd_profile.py',
       'tools/_s2oe_visual_consistency.py','mcm_field_organism/finite_video_path.py',
       'tests/test_s2oe_visual_consistency.py','reports/qualify_visual_consistency_once.py')


def raw(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()


def inventory():
    return {p:dict(bytes=(ROOT/p).stat().st_size,sha256=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in FILES}


def save(name,value):
    with (OUT/name).open('xb') as f: f.write(raw(value))


def main():
    if sys.argv[1:]==['prepare']:
        OUT.mkdir(exist_ok=False)
        inv=inventory()
        sources=sum(x['bytes'] for x in inv.values())
        # Full maximum tables, logs and binding documents, not a successful example size.
        limits=dict(sources=327680,metadata=131072,shared=393216,total=4194304)
        budget=dict(sources=sources,metadata=114688,shared=sources,total=sources+114688)
        assert all(budget[k]<=limits[k] for k in limits)
        save('preregistration.json',dict(sources=inv,tests=[f'test_{n:02}' for n in range(1,13)],
            budget=budget,limits=limits,reserves=dict(binding_and_report=16384,full_log=32768,
            result=8192,numeric_tables=57344),real_media=False,gate=False))
        print('BOUND',budget)
    elif sys.argv[1:]==['qualify']:
        bound=json.loads((OUT/'preregistration.json').read_bytes())
        assert bound['sources']==inventory()
        with (OUT/'qualification.claim').open('xb') as f: f.write(b'once')
        log=io.StringIO()
        suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2oe_visual_consistency')
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
        text=log.getvalue().encode()
        with (OUT/'qualification.log').open('xb') as f: f.write(text)
        sources_same=bound['sources']==inventory()
        good=result.wasSuccessful() and result.testsRun==12 and sources_same and len(text)<=32768
        save('result.json',dict(status='QUALIFIED' if good else 'NOT_QUALIFIED',
            tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
            sources_unchanged=sources_same,sources=inventory(),log_sha256=hashlib.sha256(text).hexdigest(),
            log_bytes=len(text),real_media=False,gate=False))
        print(text.decode()); print('QUALIFIED' if good else 'NOT_QUALIFIED')
    else:
        raise SystemExit('prepare or qualify')


if __name__=='__main__': main()
