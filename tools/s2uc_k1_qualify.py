"""Neutral K01-K10 qualification only; does not import or materialize F/T1 cases."""
import io
import json
import sys
import time
import unittest
from pathlib import Path
from tools import s2uc_t1_start_v3 as prior

ROOT=prior.ROOT
FILES=('tools/_s2uc_k1.py','tools/_s2uc_k1_reference.py','tools/_s2uc_k1_probe.py',
       'tools/s2uc_k1_qualify.py','tests/test_s2uc_k1.py')


def main():
    prior.verify()
    from tests import test_s2uc_k1 as tests
    parent=ROOT/'reports/s2uc'
    number=1
    while (parent/f'k1-neutral-qualification-20261003-{number:02}').exists():number+=1
    folder=parent/f'k1-neutral-qualification-20261003-{number:02}'
    folder.mkdir()
    tests.OUTPUT=folder
    binding=dict(files={n:prior.p.q.old.sha(ROOT/n) for n in FILES},
        prior_start_binding_sha256=prior.p.q.old.sha(prior.BINDING),
        contract_sha256=prior.p.q.old.sha(ROOT/'docs/S2UC_KANDIDATENERHALTUNG_K1_KONZEPTVERTRAG_20261003.md'),
        python=sys.version,executable_sha256=prior.p.q.old.sha(sys.executable))
    prior.p.q.old.save(folder/'binding.json',binding)
    log=io.StringIO();begin=time.monotonic()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    prior.p.q.old.save(folder/'tests.json',dict(count=result.testsRun,success=result.wasSuccessful(),
        failures=len(result.failures),errors=len(result.errors),skips=len(result.skipped),output=log.getvalue()))
    prior.p.q.old.save(folder/'facts.json',tests.FACTS)
    prior.verify()
    prior.p.q.old.save(folder/'closure.json',dict(status='PASS' if result.wasSuccessful() and not result.skipped else 'FAILED',
        duration_seconds=time.monotonic()-begin,files={x.name:dict(bytes=x.stat().st_size,sha256=prior.p.q.old.sha(x)) for x in folder.iterdir()},
        reserved_research_cases_generated=0,T1_replays=0,neutral_probe_completions=len(tests.FACTS)))
    print(log.getvalue());print(str(folder))
    if not result.wasSuccessful() or result.skipped:raise SystemExit(1)


if __name__=='__main__':main()
