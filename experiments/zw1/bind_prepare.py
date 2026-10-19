"""Bind preparation only; never authorize or start research."""
import json
from . import prepare as e

def main():
    if e.AUTH.exists() or e.TARGET.exists() or (e.PREP/'CONSUMED.json').exists():raise PermissionError('BIND_BEFORE_RESEARCH_ONLY')
    for mode in e.MODES:
        t=json.loads((e.PREP/f'integration-{mode}/terminal.json').read_bytes())
        expected='TERMINAL_COMPLETE' if mode=='complete' else 'TECHNICAL_ABORT'
        if t['status']!=expected or not t['worker_ended'] or not t['file_cleanup_confirmed'] or t['cleanup']!='CONFIRMED':raise ValueError('INTEGRATION:'+mode)
    if json.loads((e.PREP/'integration-tests.json').read_bytes())['status']!='PASS':raise ValueError('TESTS')
    path=e.PREP/'prestart.json'
    if path.exists() or path.with_suffix('.sha256').exists():raise FileExistsError('BINDING_EXCLUSIVE')
    b=dict(kind='ZW1_PRESTART',runtime=e.runtime(),limits=e.LIMITS,target=str(e.TARGET),namespace=e.NAMESPACE,execution_plan=e.EXECUTION_PLAN,call=e.exact_call(),
        files={n:e.sha(e.ROOT/n) for n in e.binding_paths()},
        qualification={p.relative_to(e.ROOT).as_posix():e.sha(p) for p in e.PREP.rglob('*') if p.is_file() and p.name not in ('REPORT.md','prestart.json','prestart.sha256')},
        research_authorized=False,research_sources_created=False,matrix_sha256=e.MATRIX_SHA)
    with path.open('xb') as f:f.write(e.raw(b))
    with path.with_suffix('.sha256').open('x') as f:f.write(e.sha(path)+'\n')
    _,digest=e.validate_binding(path)
    print(json.dumps(dict(sha256=digest,files=len(b['files']),qualification=len(b['qualification']),call=b['call'])))

if __name__=='__main__':main()
