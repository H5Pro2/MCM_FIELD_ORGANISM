"""No research entry. Matrix generation and focused neutral qualification only."""
import hashlib,json,time,unittest
from pathlib import Path
from . import matrix,integration,statistics
from tools.s2uc_ura1_runtime_qualify import install_job
from tools import _s2uc_hx1_windows as win

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/s2uc/zw1-neutral-preparation-20261018-01'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    install_job();started=time.monotonic();OUT.mkdir(exist_ok=True)
    if (OUT/'result.json').exists():raise FileExistsError('QUALIFICATION_ALREADY_FINISHED')
    recipe=ROOT/'experiments/zw1/MATRIX_RECIPE.md'
    if not recipe.exists():raise ValueError('RECIPE_BEFORE_MATRIX')
    path=OUT/'bootstrap.bin'
    if not path.exists():
        data=matrix.generate();digest=matrix.verify(data)
        with path.open('xb') as f:f.write(data)
        (OUT/'matrix-binding.json').write_text(json.dumps(dict(sha256=digest,bytes=len(data),recipe_sha256=sha(recipe),recipe_preceded_matrix=recipe.stat().st_mtime_ns<path.stat().st_mtime_ns,rows=10000,columns=16,draws_per_orientation=8,selection_attempts=1),indent=2),encoding='utf-8')
    bound=json.loads((OUT/'matrix-binding.json').read_bytes())
    if matrix.verify(path.read_bytes())!=bound['sha256'] or sha(recipe)!=bound['recipe_sha256']:raise ValueError('MATRIX_OR_RECIPE_CHANGED')
    from . import test_package
    suite=unittest.defaultTestLoader.loadTestsFromModule(test_package)
    ids=[t.id() for group in suite for t in group]
    with (OUT/'tests.log').open('w',encoding='utf-8') as f:tested=unittest.TextTestRunner(stream=f,verbosity=2).run(suite)
    (OUT/'tests.json').write_text(json.dumps(dict(status='PASS' if tested.wasSuccessful() else 'FAIL',tests=tested.testsRun,ids=ids,errors=[(t.id(),e) for t,e in tested.errors],failures=[(t.id(),e) for t,e in tested.failures]),indent=2),encoding='utf-8')
    if not tested.wasSuccessful():raise ValueError('UNIT_QUALIFICATION_FAILED')
    runs={};prep=sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())
    for mode in ('complete','archive_failure','source_failure'):
        folder=OUT/f'integration-{mode}'
        terminal,receipts=integration.run(folder,mode,prep)
        if mode=='complete':
            assert terminal['status']=='TERMINAL_COMPLETE' and terminal['completed_cases']==[1,2] and terminal['distinct_arms']==8
            assert terminal['executions']['archive_reference_completed']==8
        elif mode=='archive_failure':
            assert terminal['status']=='TECHNICAL_ABORT' and terminal['completed_cases']==[1] and terminal['active_case']==2 and terminal['distinct_arms']==8
            assert 'PRIOR_RECORD_HASH' in terminal['first_failure']
            assert not (folder/'pair-02-receipt.json').exists()
        else:
            assert terminal['status']=='TECHNICAL_ABORT' and terminal['completed_cases']==[] and terminal['distinct_arms']==0
            assert 'SOURCE_CHANGED' in terminal['first_failure']
        assert terminal['cleanup']=='CONFIRMED' and not terminal['partial_files']
        # Neutral partial or short pairs cannot become a complete research verdict.
        try:statistics.primary(receipts,path.read_bytes(),bound['sha256'])
        except ValueError:pass
        else:raise AssertionError('NEUTRAL_BECAME_RESEARCH_VERDICT')
        runs[mode]=terminal
        print(json.dumps(dict(mode=mode,status=terminal['status'],executions=terminal['executions'])),flush=True)
    result=dict(status='PASS',tests=tested.testsRun,integration=runs,seconds=time.monotonic()-started,job=win.snapshot(),research_sources_created=False,research_authorization_created=False,full_policy_cases_executed=0,neutral_frames_per_arm=96,neutral_policy_arms=sum(v['executions']['policy_started'] for v in runs.values()),matrix_sha256=bound['sha256'])
    (OUT/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    assert sum(p.stat().st_size for p in OUT.rglob('*') if p.is_file())<8388608
    print(json.dumps({k:v for k,v in result.items() if k!='integration'}))

if __name__=='__main__':main()
