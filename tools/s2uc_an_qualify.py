"""Explicit neutral qualification with exclusive report directory, no AN seeds."""
import json
import sys
import unittest
from pathlib import Path
from tools import s2uc_an_material as m
from tests import test_s2uc_an_material as tests


def main(folder):
    out=Path(folder).resolve()
    m.need(out.is_relative_to((m.ROOT/'reports/s2uc').resolve()),'REPORT_SCOPE')
    out.mkdir(exist_ok=False);tests.REPORT=out
    binding,_=m.load_binding()
    before={name:m.sha(m.ROOT/name) for name in binding['code']}
    tests.save(out/'prequalification.json',dict(code=before,binding_sha256=m.sha(m.BINDING),
        plan_sha256=m.sha(m.PLAN),scope='neutral only; no AN production; single neutral tau=1/32'))
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(tests.ANMaterialTests)
    with (out/'tests.txt').open('x',encoding='utf-8') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    unchanged=before=={name:m.sha(m.ROOT/name) for name in before}
    tests.save(out/'facts.json',tests.FACTS)
    report=dict(tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),
        successful=result.wasSuccessful() and unchanged,code_unchanged=unchanged,
        failure_details=result.failures,error_details=result.errors)
    # Test identifiers are strings in the machine-readable result.
    report['failure_details']=[(str(t),s) for t,s in result.failures]
    report['error_details']=[(str(t),s) for t,s in result.errors]
    tests.save(out/'test-result.json',report)
    tests.save(out/'inventory.json',{str(f.relative_to(out)).replace('\\','/'):m.sha(f) for f in out.rglob('*') if f.is_file()})
    print(json.dumps(report,indent=2))
    return 0 if report['successful'] else 1


if __name__=='__main__':raise SystemExit(main(sys.argv[1]))
