"""Isolated M1-M5 qualification; includes all 207 unchanged P2 obligations."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import _s2uc_productive as p
from tools import s2uc_p2_check as old
from tools import s2uc_productive_once as process
from tests.test_s2uc_productive import fixture

def preserve():
    inv=p.e.read_json(ROOT/'reports/s2uc/p2-supplier-correction-20260930-01/final/inventory.json')
    for row in inv['files']:
        p.need(p.ref(ROOT/row['path'])=={k:v for k,v in row.items() if k!='category'},'P3_P2_CODE_CHANGED')
    prior=[]
    for name in ('p2-supplier-correction-20260930-01','p2-development-20260930-01'):
        prior.extend(p.ref(f) for f in sorted((ROOT/'reports/s2uc'/name).rglob('*')) if f.is_file())
    # P1's original preservation inventory covers all earlier research evidence.
    historical=p.e.read_json(p.e.P1/'preserved-before.json')
    for row in historical:
        actual=p.ref(ROOT/row['path'])
        p.need(all(actual[k]==row[k] for k in actual),'P3_HISTORICAL_CHANGED')
    return dict(p2_code=inv['files'],prior_reports=prior,historical_files=len(historical),
                all_original_bytes_unchanged=True)

def close_ledger(root,inv,extra=()):
    inputs=p.e.inputs()
    # Original plan is independently used by P3; do not count an identical input twice.
    plan=p.plan_pin()
    if plan['path'] not in {r['ref']['path'] for r in inputs}:
        inputs.append(dict(ref=plan,category='static_shared'))
    ledger=p.e.resources.Ledger(inv,[root,*extra],inputs)
    path=root/'ledger.json';path.write_bytes(b'{}')
    for _ in range(16):
        result=ledger.admit()
        for row in result['files']:
            if row['path']==path.as_posix():row['sha256']=None
        data=p.e.canonical(result)
        if path.read_bytes()==data:return result
        path.write_bytes(data)
    raise ValueError('P3_LEDGER_FIXED_POINT')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('folder');ap.add_argument('--focus',action='store_true')
    args=ap.parse_args();root=Path(args.folder).resolve()
    p.need(root.is_relative_to(ROOT/'reports/s2uc'),'P3_QUALIFICATION_ROOT');root.mkdir()
    inv=p.current();p.need(len(p.e.canonical(inv))<=16384,'P3_INVENTORY_LIMIT')
    p.e.write_new(root/'inventory.json',p.e.canonical(inv))
    before=preserve();p.e.write_new(root/'preservation.json',p.e.canonical(before))
    ids=p.test_ids()
    if args.focus:ids=[n for n in ids if n.startswith('tests.test_s2uc_productive.')]
    os.environ['MCM_P2_QUALIFICATION_ROOT']=str(root)
    with (root/'unittest.log').open('x',encoding='utf-8') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=old.Result).run(
            unittest.defaultTestLoader.loadTestsFromNames(ids))
    unchanged=p.current()==inv;preserved=preserve()==before
    ok=result.wasSuccessful() and not result.skipped and set(result.outcomes)==set(ids) and unchanged and preserved
    summary=dict(version='s2uc.qualification.p3',test_ids=ids,results=result.outcomes,
        tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
        exit_code=0 if ok else 1,code_unchanged=unchanged,expected_ids_complete=set(result.outcomes)==set(ids),
        formal_qualification=False,real_execution_authorized=False,inventory=p.ref(root/'inventory.json'),
        preservation_unchanged=preserved)
    p.e.write_new(root/'test-result.json',p.e.canonical(summary))
    prefixes=sorted({n.rsplit('.',1)[0] for n in ids})
    protocol=dict(version='s2uc.test-protocol.p3',prefixes=prefixes,
        rows=[[prefixes.index(n.rsplit('.',1)[0]),n.rsplit('.',1)[1],result.outcomes.get(n,'MISSING')] for n in ids],
        inventory=p.ref(root/'inventory.json'),result=p.ref(root/'test-result.json'))
    p.need(len(p.e.canonical(protocol))<=32768,'P3_PROTOCOL_LIMIT')
    p.e.write_new(root/'protocol.json',p.e.canonical(protocol))
    extras=[]
    if ok and not args.focus:
        retained=Path(tempfile.mkdtemp(dir=ROOT/'reports/s2uc',prefix='p3-test-retained-'))
        path=fixture(retained,inv)
        outcome=process._run(path,test=True,case='original_bad_hash')
        p.need(outcome['status']=='NOT_EVALUABLE','P3_ORIGINAL_HASH_NOT_REJECTED')
        extras.append(retained)
        p.e.write_new(root/'result.json',p.e.canonical(dict(retained_test_root=retained.as_posix(),
            status='ORIGINAL_HASH_REJECTION_TEST_ONLY',outcome=outcome,real_execution_authorized=False)))
    ledger=close_ledger(root,inv,extras)
    print(json.dumps(dict(ok=ok,tests=result.testsRun,code_bytes=inv['code_bytes'],
                         actual=ledger['actual'],reserved=ledger['reserved_closure'])))
    return 0 if ok else 1

if __name__=='__main__':raise SystemExit(main())
