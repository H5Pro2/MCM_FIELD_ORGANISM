from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import _s2uc_comparison_preparation as p

def main():
    out=Path(sys.argv[1]).resolve(); out.mkdir()
    inv=p.current()
    p.need(inv['code_bytes']<=868340,'P1_CODE_LIMIT')
    def save(name,value): (out/name).write_bytes(p.canonical(value))
    save('dependency-inventory.json',inv)
    ids=[n for n in p.test_ids() if n.startswith('tests.test_s2uc_comparison_preparation.')]
    with (out/'unittest.log').open('w',encoding='utf-8') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(ids))
    unchanged=inv==p.current()
    ok=result.wasSuccessful() and not result.skipped and result.testsRun==len(ids) and unchanged
    save('test-result.json',dict(test_ids=ids,results=dict.fromkeys(ids,'PASS' if ok else 'NOT_QUALIFIED'),
         tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
         exit_code=0 if ok else 1,code_unchanged=unchanged,expected_ids_complete=result.testsRun==len(ids),
         formal_qualification=False,real_execution_authorized=False,inventory=p.reference(out/'dependency-inventory.json')))
    if ok:
        groups=[dict(result=p.reference(folder/'test-result.json'),inventory=p.reference(folder/'dependency-inventory.json'))
                for folder in [ROOT/'reports/s2uc/provenance-appendix-repeat-20260929-01',
                               ROOT/'reports/s2uc/regression-105-20260930-01',out]]
        save('preparation-result.json',p.prepare(out/'preparation',groups,out/'dependency-inventory.json'))
    return 0 if ok else 1

if __name__=='__main__': raise SystemExit(main())
