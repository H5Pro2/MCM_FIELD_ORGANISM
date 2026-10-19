"""Administrative preflight only; no receptors, native history or test invocation."""
import ast
import hashlib
import json
from pathlib import Path
from tools import _checkpoint_transfer_metadata as model
from tools import _checkpoint_transfer_budget as budget

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/checkpoint-authorization-precondition-20260912-01'
OWN=['tools/_checkpoint_transfer_entry.py','tools/_checkpoint_transfer_budget.py',
     'tools/_checkpoint_transfer_metadata.py','tests/test_checkpoint_authorization.py',
     'reports/prepare_checkpoint_authorization.py']

def ident(p):
    b=p.read_bytes();return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest())

def main():
    if OUT.exists():raise RuntimeError('unused preparation required')
    old=json.loads((ROOT/'reports/checkpoint-entry-qualification-20260912-02/preregistration.json').read_bytes())
    inputs=json.loads((ROOT/'reports/memory-restart-transfer-ready-20260912-01/settings.json').read_bytes())
    files=dict(old['inventory']['files'])
    for p in OWN:files[p]=ident(ROOT/p)
    tests=sorted(n.name for n in ast.walk(ast.parse((ROOT/OWN[3]).read_text()))
                 if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
    # This is deliberately a lower administrative contribution: existing required
    # evidence only. New qualification/authorization/final-balance costs are listed
    # as not yet added. An excess already here cannot be cured by adding them.
    admin={}
    for ref in inputs['qualification_references']:
        path=ROOT/ref['path'];raw=path.read_bytes()
        try:value=json.loads(raw)
        except ValueError:value=None
        admin[ref['path']]=model.ledger.classify(len(raw),value)['metadata']
    path=ROOT/'reports/memory-restart-transfer-ready-20260912-01/settings.json'
    admin['existing_binding']=model.ledger.classify(path.stat().st_size,inputs)['metadata']
    charge=list(dict.fromkeys(old['charged_sources']+OWN))
    shapes=model.derive(inputs['manifest']['run_id'],admin,charge,
                        [r['path'] for r in inputs['qualification_references']])
    value=dict(status='PRECONDITION_STOP' if shapes['violations'] else 'INCOMPLETE_PREFLIGHT',
        test_calls=0,tests=tests,files=files,metadata_derivation=shapes,
        omitted_additions=['new qualification','new authorization and consumption',
                          'runtime common/preregistration/dispatch','final ledger and parent error'],
        interpretation='An overrun of the derived protective envelope, not a measured runtime or an unavoidable lower bound.',
        historical_24_unchanged=True,main_gate=False)
    OUT.mkdir();(OUT/'precondition.json').write_text(json.dumps(value,sort_keys=True,indent=2))
    peak=max(shapes['rows'],key=lambda x:x['metadata'])
    print(json.dumps(dict(status=value['status'],test_calls=0,maximum=peak,files=len(files)),indent=2))

if __name__=='__main__':main()
