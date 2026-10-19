"""Execute bound neutral development tests, retaining only newly made provenance inputs."""
import argparse
import json
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import _s2uc_provenance_inventory as inventory
from tools import _s2uc_provenance_evaluation as evaluator
from tools import _s2uc_source_execution_binding as baseline


def save(path, value):
    path.write_bytes(baseline.old.canonical(value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('output', type=Path)
    parser.add_argument('--focused', action='store_true')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    before = inventory.current()
    save(args.output / 'dependency-inventory.json', before)
    if before['code_bytes'] > baseline.resources.LIMITS['code']:
        raise ValueError('UNCHANGED_CODE_CAP_EXCEEDED')
    names = (inventory.TEST,) if args.focused else baseline.TESTS + (inventory.TEST,)
    suite = unittest.defaultTestLoader.loadTestsFromNames([name[:-3].replace('/', '.') for name in names])
    statuses, captures = {}, []
    active = {'test': None}
    class Result(unittest.TextTestResult):
        def startTest(self, test):
            active['test'] = test.id()
            super().startTest(test)
        def stopTest(self, test):
            active['test'] = None
            super().stopTest(test)
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
    original = evaluator._evaluate_artifacts
    def capture(packet, **kwargs):
        if not (active['test'] or '').startswith('tests.test_s2uc_provenance_evaluation.'):
            raise AssertionError('PROVENANCE_EVALUATION_OUTSIDE_NEW_TESTS')
        result = original(packet, **kwargs)
        folder = args.output / 'fresh-evaluations' / f'{len(captures)+1:03}'
        folder.mkdir(parents=True)
        if type(packet) is dict:
            for key, data in packet.items():
                if key in evaluator.FILENAMES and type(data) is bytes:
                    (folder / evaluator.FILENAMES[key]).write_bytes(data)
        save(folder / 'evaluation.json', result)
        captures.append({'test_id': active['test'], 'path': folder.relative_to(args.output).as_posix(),
                         'status': result['status'], 'scope': result['scope']})
        return result
    begin = time.monotonic()
    with (args.output / 'unittest.log').open('w', encoding='utf-8') as log:
        with patch.object(evaluator, '_evaluate_artifacts', capture):
            result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Result).run(suite)
    unchanged = inventory.current() == before
    expected = inventory.test_ids()
    if args.focused:
        expected = [name for name in expected if name.startswith('tests.test_s2uc_provenance_evaluation.')]
    complete = sorted(statuses) == expected
    code = 0 if result.wasSuccessful() and not result.skipped and unchanged and complete else 1
    save(args.output / 'captures.json', captures)
    evidence = {'version': 's2uc.provenance-development-evidence.v1', 'scope': 'EXECUTED_NEUTRAL_DEVELOPMENT',
                'inventory_sha256': baseline.discovery.sha(baseline.old.canonical(before)),
                'test_ids': sorted(statuses), 'results': statuses, 'tests_run': result.testsRun,
                'failures': len(result.failures), 'errors': len(result.errors), 'skips': len(result.skipped),
                'expected_ids_complete': complete, 'code_unchanged': unchanged, 'exit_code': code,
                'seconds': time.monotonic() - begin, 'focused': args.focused,
                'old_obligations': len(baseline.test_ids()), 'code_files': len(before['files']),
                'code_bytes': before['code_bytes'], 'code_limit': baseline.resources.LIMITS['code'],
                'real_execution_authorized': False, 'formal_qualification': False, 'independent_acceptance': 'OPEN'}
    save(args.output / 'test-result.json', evidence)
    hashes = []
    for path in sorted(args.output.rglob('*')):
        if path.is_file():
            data = path.read_bytes()
            hashes.append({'path': path.relative_to(args.output).as_posix(), 'bytes': len(data),
                           'sha256': baseline.discovery.sha(data)})
    save(args.output / 'evidence-hashes.json', hashes)
    print(json.dumps({k: evidence[k] for k in ('tests_run', 'failures', 'errors', 'skips', 'exit_code', 'code_bytes', 'seconds')}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
