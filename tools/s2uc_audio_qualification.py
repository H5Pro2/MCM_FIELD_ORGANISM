"""Neutral qualification only; durable IDs, errors and OS resource observations."""
import io,json,time,unittest,hashlib
from pathlib import Path
from tools.s2uc_audio_worker import ROOT

def main():
    from tests import test_s2uc_bounded_audio as tests
    folder=ROOT/'reports/s2uc/audio-reader-development-20260930'
    folder.mkdir(parents=True,exist_ok=True)
    # Exclusive numbered qualification records; preserve any earlier failures.
    n=1
    while (folder/f'tests-{n:02d}.json').exists():n+=1
    class Recorded(unittest.TextTestResult):
        def __init__(self,*args,**kwargs):super().__init__(*args,**kwargs);self.rows=[]
        def addSuccess(self,test):super().addSuccess(test);self.rows.append({'id':test.id(),'status':'PASS'})
        def addError(self,test,err):super().addError(test,err);self.rows.append({'id':test.id(),'status':'ERROR','error':self._exc_info_to_string(err,test)})
        def addFailure(self,test,err):super().addFailure(test,err);self.rows.append({'id':test.id(),'status':'FAIL','error':self._exc_info_to_string(err,test)})
    buffer=io.StringIO();start=time.monotonic()
    suite=unittest.defaultTestLoader.loadTestsFromModule(tests)
    result=unittest.TextTestRunner(stream=buffer,verbosity=2,resultclass=Recorded).run(suite)
    (folder/f'tests-{n:02d}.txt').write_text(buffer.getvalue(),encoding='utf-8')
    record=dict(tests_run=result.testsRun,passed=result.wasSuccessful(),errors=len(result.errors),failures=len(result.failures),skips=len(result.skipped),elapsed_seconds=time.monotonic()-start,
        tests=result.rows,os_and_decoder_facts=tests.FACTS,nasa_decoded=False,neutral_only=True,
        fixture_bindings=[dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(tests.FIX.iterdir())])
    (folder/f'tests-{n:02d}.json').write_text(json.dumps(record,indent=2)+'\n')
    print(buffer.getvalue());print('Evidence',folder/f'tests-{n:02d}.json')
    return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
