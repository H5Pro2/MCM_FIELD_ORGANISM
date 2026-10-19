"""Run the bounded REV1 unit suite only; never research or policy series."""
import hashlib
import json
from pathlib import Path
import time
import unittest
from tools.s2uc_ura1_prepare_rev1 import PREP, ROOT, AUTH, TARGET
from tools.s2uc_ura1_runtime_qualify import install_job


def main():
    if AUTH.exists() or TARGET.exists():
        raise PermissionError('PREPARATION_ONLY')
    install_job()
    PREP.mkdir(exist_ok=True)
    data = (ROOT/'reports/s2uc/ura1-v4-preparation-20261015-01/bootstrap.bin').read_bytes()
    if hashlib.sha256(data).hexdigest() != '0b9fbf483e870adac01ded7d2d0d0a651a11474a4ac2e4fbae1c14e793d7d965':
        raise ValueError('MATRIX_BINDING')
    destination = PREP/'bootstrap.bin'
    if destination.exists() and destination.read_bytes() != data:
        raise ValueError('MATRIX_CHANGED')
    destination.write_bytes(data)
    suite = unittest.defaultTestLoader.loadTestsFromName('tests.test_s2uc_ura1_rev1')
    ids = []
    def visit(node):
        if isinstance(node, unittest.TestSuite):
            for child in node: visit(child)
        else: ids.append(node.id())
    visit(suite)
    if (PREP/'unit-tests.json').exists():
        number=1
        while (PREP/f'unit-tests-attempt-{number:02d}.json').exists(): number+=1
        for suffix in ('json','log'):
            (PREP/f'unit-tests-attempt-{number:02d}.{suffix}').write_bytes((PREP/f'unit-tests.{suffix}').read_bytes())
    begin = time.monotonic()
    with (PREP/'unit-tests.log').open('w', encoding='utf-8') as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    from tools import _s2uc_hx1_windows as win
    value = dict(neutral_only=True, test_ids=ids, tests=result.testsRun,
                 errors=[(t.id(), s) for t, s in result.errors], failures=[(t.id(), s) for t, s in result.failures],
                 skipped=[(t.id(), s) for t, s in result.skipped], seconds=time.monotonic()-begin,
                 job=win.snapshot(), status='PASS' if result.wasSuccessful() else 'FAIL',
                 research_sources_generated=False, policy_frames=0)
    (PREP/'unit-tests.json').write_text(json.dumps(value, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(value))
    if not result.wasSuccessful(): raise SystemExit(1)


if __name__ == '__main__': main()
