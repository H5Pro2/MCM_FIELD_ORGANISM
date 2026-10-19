"""Focused URA1 developer evidence only; deliberately no research entry point."""
import gzip,hashlib,io,json,unittest
from pathlib import Path
from tests import test_s2uc_ura1 as tests
from tools._s2uc_ura1_neutral import archive_bytes,verify_archive,raw

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/s2uc/ura1-neutral-development-20261014-01'
FILES=['tools/_s2uc_ura1.py','tools/_s2uc_ura1_reference.py','tools/_s2uc_ura1_neutral.py',
       'tools/s2uc_ura1_neutral_qualify.py','tests/test_s2uc_ura1.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_bytes(raw(v))

def main():
    if OUT.exists():raise FileExistsError('Evidence directory exists; preserve prior evidence')
    stream=io.StringIO()
    class Result(unittest.TextTestResult):
        def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.ids=[]
        def addSuccess(self,test):self.ids.append(dict(id=test.id(),status='PASS'));super().addSuccess(test)
    result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Result).run(unittest.defaultTestLoader.loadTestsFromTestCase(tests.URA1Tests))
    print(stream.getvalue())
    if not result.wasSuccessful():raise SystemExit(1)
    OUT.mkdir(parents=True)
    write(OUT/'tests.json',dict(status='PASS',tests=result.testsRun,ids=result.ids,neutral_only=True))
    (OUT/'tests.txt').write_text(stream.getvalue(),encoding='utf-8')
    facts=tests.FACTS;archives={}
    for key in ('D_hand_case','lifecycle_trace'):
        record=facts.pop(key);blob=archive_bytes(record);restored=verify_archive(blob,hashlib.sha256(blob).hexdigest())
        if raw(restored)!=raw(record):raise ValueError('ARCHIVE_ROUNDTRIP')
        (OUT/(key+'.json.gz')).write_bytes(blob)
        archives[key]=dict(sha256=hashlib.sha256(blob).hexdigest(),compressed=len(blob),expanded=len(gzip.decompress(blob)),
            frames=record['U']['frames'],outer_events_per_arm=len(record['U']['events']),internal_events_per_arm=len(record['U']['internal']))
        if key=='D_hand_case':
            write(OUT/'normal-resources.json',{arm:record[arm]['resources'] for arm in ('U','R')})
    errors=facts.pop('error_paths');write(OUT/'error-resources.json',errors)
    write(OUT/'evidence.json',facts|dict(archives=archives,no_research_sources=True,no_bootstrap_matrix=True,no_full_size_run=True))
    summary={}
    normal=json.loads((OUT/'normal-resources.json').read_text())
    for arm in ('U','R'):
        rs=[normal[arm]]+[x['resources'] for x in errors if x['arm']==arm]
        whole=normal[arm]['whole_operations']+[w for x in errors if x['arm']==arm for w in x['whole']]
        summary[arm]=dict(additional_heap_peak=max(x['additional_python_peak'] for x in rs),
            whole_before_after_peak=max(max(w['whole_before'],w['whole_after']) for w in whole),
            whole_conservative_traced_upper=max(w['whole_conservative'] for w in whole),
            traced_transient_peak=max(w['traced_transient'] for w in whole),
            original_frames_upper_bound=max(x['original_frames_upper_bound'] for x in rs),
            combined_upper_bound=max(x['combined_upper_bound'] for x in rs),
            receipt_bytes=normal[arm]['receipt_bytes_peak'],utf8_upper=normal[arm]['utf8_upper'],
            input_object_bytes=max(w['input_object_bytes'] for w in whole),packed=416)
    write(OUT/'resource-summary.json',summary)
    inherited=json.loads((ROOT/'docs/S2UC_UF1_V1_20261005_CODEBINDUNG.json').read_text())['files']
    for name,h in inherited.items():
        if sha(ROOT/name)!=h:raise ValueError('INHERITED_CHANGED:'+name)
    write(OUT/'development-binding.json',dict(status='DEVELOPMENT_ONLY_NOT_PRESTART',
        unchanged_predecessor_files=len(inherited),predecessor_binding_sha256=sha(ROOT/'docs/S2UC_UF1_V1_20261005_CODEBINDUNG.json'),
        files={n:sha(ROOT/n) for n in FILES},contract_sha256=sha(ROOT/'docs/S2UC_URA1_AUSWAHLABLATION_KONZEPT_20261014.md')))
    write(OUT/'closure.json',dict(status='PASS_FOCUSED_NEUTRAL_DEVELOPMENT',neutral_only=True,
        research_ready=False,research_runs=0,files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in OUT.iterdir()}))
    print(json.dumps(dict(resources=summary,archives=archives),indent=2))

if __name__=='__main__':main()
