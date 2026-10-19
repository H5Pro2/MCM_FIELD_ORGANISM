"""Explicit neutral P2 qualification, old 188 and new obligations on final code."""
import argparse
import json
import os
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools import _s2uc_p2_execution as e
from tools import _s2uc_p2_appendix as appendix
from tools import s2uc_p2_process as process

class Result(unittest.TextTestResult):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.outcomes={}
    def startTest(self,test):
        super().startTest(test);self.outcomes[test.id()]='RUNNING'
    def addSuccess(self,test):super().addSuccess(test);self.outcomes[test.id()]='PASS'
    def addFailure(self,test,err):super().addFailure(test,err);self.outcomes[test.id()]='FAIL'
    def addError(self,test,err):super().addError(test,err);self.outcomes[test.id()]='ERROR'
    def addSkip(self,test,reason):super().addSkip(test,reason);self.outcomes[test.id()]='SKIP'
    def addSubTest(self,test,subtest,err):
        super().addSubTest(test,subtest,err)
        if err is not None:self.outcomes[test.id()]='FAIL'

def preservation(root):
    baseline=e.read_json(root/'preservation.json')
    for row in baseline['code']+baseline['p1']:
        ref=e.p1.reference(ROOT/row['path'])
        e.need(all(ref[k]==row[k] for k in ref),'P2_BASELINE_CHANGED:'+row['path'])
    # The original P1 preservation inventory also covers all prior retained reports.
    historical=e.read_json(e.P1/'preserved-before.json')
    for row in historical:
        ref=e.p1.reference(ROOT/row['path'])
        e.need(all(ref[k]==row[k] for k in ref),'P2_HISTORICAL_CHANGED:'+row['path'])
    for row in baseline.get('prior_reports',[]):
        ref=e.p1.reference(ROOT/row['path'])
        e.need(all(ref[k]==row[k] for k in ref),'P2_PRIOR_REPORT_CHANGED:'+row['path'])
    for row in baseline.get('prior_p2_code',[]):
        data=row['text'].encode('utf-8')
        e.need(len(data)==row['ref']['bytes'] and e.sha(data)==row['ref']['sha256'],
               'P2_PRIOR_SOURCE_COPY_CHANGED')
    return dict(code_files=len(baseline['code']),p1_files=len(baseline['p1']),
                historical_files=len(historical),prior_p2_files=len(baseline.get('prior_reports',[])),
                prior_p2_source_versions=len(baseline.get('prior_p2_code',[])),
                all_original_bytes_unchanged=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder');parser.add_argument('--focus',action='store_true')
    parser.add_argument('--supplier-focus',action='store_true')
    args=parser.parse_args();root=Path(args.folder).resolve()
    root.mkdir(exist_ok=True)
    q=root.parent if (root.parent/'preservation.json').exists() else root
    inv=e.current()
    inventory_path=root/'inventory.json'
    e.write_new(inventory_path,e.canonical(inv))
    e.need(len(inventory_path.read_bytes())<=16384,'P2_INVENTORY_LIMIT')
    ids=e.test_ids()
    if args.focus:ids=[n for n in ids if n.startswith('tests.test_s2uc_p2.')]
    if args.supplier_focus:ids=[n for n in ids if '.test_bound_' in n and n.startswith('tests.test_s2uc_p2.')]
    os.environ['MCM_P2_QUALIFICATION_ROOT']=str(q)
    with (root/'unittest.log').open('x',encoding='utf-8') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(
            unittest.defaultTestLoader.loadTestsFromNames(ids))
    unchanged=e.current()==inv
    ok=result.wasSuccessful() and not result.skipped and set(result.outcomes)==set(ids) and unchanged
    summary=dict(version='s2uc.qualification.p2',test_ids=ids,results=result.outcomes,
        tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
        exit_code=0 if ok else 1,code_unchanged=unchanged,expected_ids_complete=set(result.outcomes)==set(ids),
        formal_qualification=False,real_execution_authorized=False,inventory=e.p1.reference(inventory_path),
        preservation=preservation(q) if (q/'preservation.json').exists() else None)
    e.write_new(root/'test-result.json',e.canonical(summary))
    prefixes=sorted({n.rsplit('.',1)[0] for n in ids})
    protocol=dict(version='s2uc.test-protocol.p2',prefixes=prefixes,
        rows=[[prefixes.index(n.rsplit('.',1)[0]),n.rsplit('.',1)[1],result.outcomes.get(n,'MISSING')] for n in ids],
        inventory=e.p1.reference(inventory_path),result=e.p1.reference(root/'test-result.json'))
    e.need(len(e.canonical(protocol))<=32768,'P2_PROTOCOL_LIMIT')
    e.write_new(root/'protocol.json',e.canonical(protocol))
    if ok and not args.focus and not args.supplier_focus:
        path=e.prepare(root/'retained-success',q,source_test=True)
        product=process.run_neutral(path)
        e.need(product['status']=='CLOSED_NEUTRAL_P2_VERIFIED','P2_FINAL_PRODUCT')
        annex=appendix.publish(path);appendix.read(path)
        e.need(annex['status']=='CLOSED_NEUTRAL_PROVENANCE','P2_FINAL_APPENDIX')
    ledger=e.resources.Ledger(inv,[q],e.inputs())
    # The ledger includes its own bytes; only the accounting file is replaced.
    ledger_path=root/'ledger.json';ledger_path.write_bytes(b'{}')
    for _ in range(12):
        value=ledger.admit()
        # Exclude its self-hash (no cryptographic fixed point); retain exact size.
        for row in value['files']:
            if row['path']==ledger_path.as_posix():row['sha256']=None
        data=e.canonical(value)
        if ledger_path.read_bytes()==data:break
        ledger_path.write_bytes(data)
    else:raise ValueError('P2_LEDGER_FIXED_POINT')
    print(json.dumps(dict(ok=ok,tests=result.testsRun,code_bytes=inv['code_bytes'],actual=value['actual'])))
    return 0 if ok else 1

if __name__=='__main__':raise SystemExit(main())
