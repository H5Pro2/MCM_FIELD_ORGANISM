"""Neutral correction qualification only; does not read research archives."""
import json,time,unittest,tracemalloc
from pathlib import Path
from unittest.mock import patch
from tools import _s2uc_er1_engine as engine
from tools import _s2uc_ura1_delta_encode as codec
from tools._s2uc_er1_run_observer import compare,archive_form
from tools._s2uc_er1_run_mechanisms import witnesses
from tools._s2uc_er1_structural_archive import verify
from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest
from tools.s2uc_ura1_runtime_qualify import install_job
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2uc/er1-structural-correction-20261017-01'
def main():
    install_job();OUT.mkdir(exist_ok=False);started=time.monotonic()
    suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_er1_stock_structural')
    def ids(s):return [n for t in s for n in (ids(t) if isinstance(t,unittest.TestSuite) else [t.id()])]
    names=ids(suite)
    with (OUT/'tests.log').open('w',encoding='utf-8') as log:tested=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    report=dict(test_ids=names,tests=tested.testsRun,failures=[(t.id(),e) for t,e in tested.failures],errors=[(t.id(),e) for t,e in tested.errors])
    if not tested.wasSuccessful():
        (OUT/'result.json').write_text(json.dumps(report));raise AssertionError('UNIT_FAILURE')
    # Ten genuinely distinct promotions in 80 neutral frames; no seeded research state.
    values=engine.blocks([(cue/32,.25 if cue%2 else .75) for cue in range(1,11) for _ in range(2)])
    assert len(values)==80
    engine.VALIDATE=lambda v:engine.need(v==values,'NEUTRAL_FIXTURE_ONLY')
    arms=[];original=engine.create
    def tracked(mode):
        a=original(mode);arms.append(a);return a
    try:
        with patch.object(engine,'create',tracked),codec.store(OUT) as owner:
            e=engine.run_arm(values,'E',trace=False);f=engine.run_arm(values,'F',trace=False)
            observer=compare(e,f);mechanisms=codec.collection()
            for item in witnesses(observer,values):mechanisms.append(item)
            record=dict(neutral_only=True,source=values,E=e,F=f,observer=archive_form(observer,codec.collection),mechanisms=mechanisms)
            proof=manifest(record);expected=full_record_digest(record);path=OUT/'neutral-80.gz'
            sizes=codec.write_archive(record,path,expected)
            (OUT/'capture.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8')
            tracemalloc.start();before=time.monotonic()
            try:verified=verify(path.read_bytes(),proof,expected);peak=tracemalloc.get_traced_memory()[1]
            finally:tracemalloc.stop()
            report['archive']=dict(verification=verified,sizes=sizes,verify_seconds=time.monotonic()-before,verify_python_peak=peak,collections=len(owner.items),record_peak=owner.record_peak,dictionary=owner.bytes,nodes=owner.entries,edges=owner.edges,indices=owner.indices)
            report['generation_endmarks']={m:list(a['events'])[-3]['state']['stock']['observation_end'] for m,a in (('E',e),('F',f))}
            report['policy_resources']={m:{k:v for k,v in a['resources'].items() if k not in ('calls','whole_operations','allocation_boundaries')} for m,a in (('E',e),('F',f))}
            # Forge capture hashes as well: semantic checks must still reject a false endmark.
            original_events=e['events'];bad=codec.collection()
            for event in original_events:
                if event['stage']=='perception:after' and event['state']['accepted']==80:
                    marks=event['state']['stock']['observation_end'];marks[next(iter(marks))]+=1
                bad.append(event)
            e['events']=bad;record['negative_original_events']=original_events;badproof=manifest(record);badexpected=full_record_digest(record);badpath=OUT/'negative-endmark.gz'
            codec.write_archive(record,badpath,badexpected)
            try:verify(badpath.read_bytes(),badproof,badexpected)
            except ValueError as error:
                if str(error)!='ARCHIVE_STOCK':raise
                report['forged_endmark_rejected']=True
            else:raise AssertionError('UNDETECTED_ENDMARK_CHANGE')
        report['cleanup']=dict(arms=len(arms),all_closed=all(a.closed and not any(a.bank) for a in arms),codec_inactive=codec.ACTIVE is None,partial_files=[p.name for p in OUT.glob('*.partial')])
        from tools import _s2uc_hx1_windows as win
        report.update(status='PASS',frames_per_arm=80,job=win.snapshot(),seconds=time.monotonic()-started,research_archive_read=False,new_authorization=False)
    except Exception as error:
        report.update(status='FAIL',error=repr(error));raise
    finally:
        (OUT/'result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('policy_resources','test_ids')}))
if __name__=='__main__':main()
