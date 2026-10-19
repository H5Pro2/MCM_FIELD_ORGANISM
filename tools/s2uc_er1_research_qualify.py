"""Only focused neutral integration checks; never authorize research."""
import json,time,unittest
from tools import s2uc_er1_research_prepare as entry
from tools.s2uc_ura1_runtime_qualify import install_job

def main():
    if entry.AUTH.exists() or entry.TARGET.exists() or (entry.PREP/'prestart.json').exists():raise PermissionError('PREPARATION_ONLY')
    install_job();entry.PREP.mkdir(exist_ok=True)
    matrix=entry.ROOT/'reports/s2uc/ura1-v4-preparation-20261015-01/bootstrap.bin'
    from tools._s2uc_er1_stats import MATRIX_SHA
    if entry.sha(matrix)!=MATRIX_SHA:raise ValueError('MATRIX_BINDING')
    if not (entry.PREP/'bootstrap.bin').exists():(entry.PREP/'bootstrap.bin').write_bytes(matrix.read_bytes())
    suite=unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_er1_research_entry')
    def ids(node):return [i for t in node for i in (ids(t) if isinstance(t,unittest.TestSuite) else [t.id()])]
    names=ids(suite);started=time.monotonic()
    path=entry.PREP/'integration-tests.json'
    if path.exists():
        n=1
        while (entry.PREP/f'integration-tests-attempt-{n}.json').exists():n+=1
        for suffix in ('json','log'):(entry.PREP/f'integration-tests.{suffix}').rename(entry.PREP/f'integration-tests-attempt-{n}.{suffix}')
    with (entry.PREP/'integration-tests.log').open('w',encoding='utf-8') as log:result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    from tools import _s2uc_hx1_windows as win
    report=dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,ids=names,failures=[(t.id(),e) for t,e in result.failures],errors=[(t.id(),e) for t,e in result.errors],seconds=time.monotonic()-started,job=win.snapshot(),research_authorization_created=False,research_sources_created=False,full_policy_cases_executed=0)
    path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8');print(json.dumps(report))
    if not result.wasSuccessful():raise SystemExit(1)
if __name__=='__main__':main()
