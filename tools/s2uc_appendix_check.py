"""Fresh neutral appendix integration and affected-suite regression evidence."""
import argparse
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import _s2uc_provenance_appendix as appendix
from tools import _s2uc_provenance_inventory as previous
from tools import _s2uc_source_execution_binding as binding
from tests import test_s2uc_provenance_appendix as cases

AFFECTED = ('tests/test_s2uc_provenance_evaluation.py', 'tests/test_s2uc_source_execution.py',
            'tests/test_s2uc_resource_contract_v7.py',
            'tests/test_s2uc_source_process_guard.py', 'tests/test_s2uc_publication_v7.py')


def save(path, value):
    path.write_bytes(binding.old.canonical(value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--focused', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True)
    inv = appendix.current()
    if inv['code_bytes'] > 851968:
        raise ValueError('CODE_CAP_EXCEEDED')
    save(args.output / 'dependency-inventory.json', inv)
    cases.ARTIFACT_ROOT = args.output / 'cases'
    names = (appendix.TEST,) if args.focused else AFFECTED + (appendix.TEST,)
    prefixes = tuple(name[:-3].replace('/', '.') + '.' for name in names)
    expected = [n for n in appendix.test_ids() if n.startswith(prefixes)]
    suite = unittest.defaultTestLoader.loadTestsFromNames([n[:-3].replace('/', '.') for n in names])
    statuses = {}
    class Result(unittest.TextTestResult):
        def addSuccess(self, test):
            statuses[test.id()] = 'PASS'
            super().addSuccess(test)
        def addFailure(self, test, err):
            statuses[test.id()] = 'FAIL'
            super().addFailure(test, err)
        def addError(self, test, err):
            statuses[test.id()] = 'ERROR'
            super().addError(test, err)
        def addSkip(self, test, reason):
            statuses[test.id()] = 'SKIP'
            super().addSkip(test, reason)
    begin = time.monotonic()
    with (args.output / 'unittest.log').open('w', encoding='utf-8') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
    unchanged = appendix.current() == inv
    complete = sorted(statuses) == expected
    code = 0 if result.wasSuccessful() and not result.skipped and unchanged and complete else 1
    evidence = {'version': 's2uc.appendix-development.v1', 'test_ids': sorted(statuses), 'results': statuses,
                'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
                'skips': len(result.skipped), 'exit_code': code, 'expected_ids_complete': complete,
                'code_unchanged': unchanged, 'seconds': time.monotonic()-begin, 'focused': args.focused,
                'preserved_previous_test_ids': previous.test_ids(), 'preserved_previous_count': len(previous.test_ids()),
                'inventory': appendix._ref(binding.old.canonical(inv)), 'code_bytes': inv['code_bytes'],
                'code_limit': 851968, 'formal_qualification': False, 'real_execution_authorized': False}
    save(args.output / 'test-result.json', evidence)
    rows = []
    for path in sorted(args.output.rglob('*')):
        if path.is_file():
            data = path.read_bytes()
            rows.append({'path': path.relative_to(args.output).as_posix(), **appendix._ref(data)})
    save(args.output / 'evidence-hashes.json', rows)
    print(json.dumps({k: evidence[k] for k in ('tests_run','failures','errors','skips','exit_code','code_bytes','seconds')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
