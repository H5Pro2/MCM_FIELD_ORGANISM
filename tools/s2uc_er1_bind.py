"""Create a preparation binding only. Never create authorization or research sources."""
import json,sys
from tools import s2uc_er1_research_prepare as entry
from tools.s2uc_ura1_runtime_qualify import runtime,sha
from tools._s2uc_ura1_v2_series import LIMITS,raw

def main():
    if entry.AUTH.exists() or entry.TARGET.exists() or (entry.PREP/'CONSUMED.json').exists():raise PermissionError('BINDING_BEFORE_RESEARCH_ONLY')
    for mode,status in (('complete','TERMINAL_COMPLETE'),('admin','TECHNICAL_ABORT'),('export','TECHNICAL_ABORT')):
        record=json.loads((entry.PREP/f'integration-{mode}/terminal.json').read_bytes())
        if record['status']!=status or not record['worker_ended'] or not record['file_cleanup_confirmed'] or record['cleanup']!='CONFIRMED':raise ValueError('INTEGRATION_EVIDENCE:'+mode)
    tests=json.loads((entry.PREP/'integration-tests.json').read_bytes())
    if tests['status']!='PASS':raise ValueError('TEST_EVIDENCE')
    path=entry.PREP/'prestart.json'
    if path.exists() or path.with_suffix('.sha256').exists():raise FileExistsError('PRESTART_EXCLUSIVE')
    bound=dict(kind='ER1_RESEARCH_PRESTART',runtime=runtime(),limits=LIMITS,target=str(entry.TARGET),namespace=entry.NAMESPACE,execution_plan=entry.EXECUTION_PLAN,
        call=[sys.executable,'-m','tools.s2uc_er1_research_prepare','run',str(path),str(entry.AUTH)],
        files={name:sha(entry.ROOT/name) for name in entry.binding_paths()},
        qualification={p.relative_to(entry.ROOT).as_posix():sha(p) for p in entry.PREP.rglob('*') if p.is_file() and p.name not in ('prestart.json','prestart.sha256','REPORT.md')},
        authorization_created=False,research_sources_created=False)
    with path.open('xb') as out:out.write(raw(bound))
    with path.with_suffix('.sha256').open('x') as out:out.write(sha(path)+'\n')
    _,digest=entry.validate_binding(path)
    print(json.dumps(dict(prestart_sha256=digest,files=len(bound['files']),call=bound['call'],authorization_exists=entry.AUTH.exists(),target_exists=entry.TARGET.exists())))
if __name__=='__main__':main()
