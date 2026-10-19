"""Fresh bounded V9 processes and separate appendix publication counterexamples."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools import _s2uc_provenance_appendix as a
from tools import _s2uc_source_execution_binding as b
from tests.test_s2uc_source_execution import fixture

ARTIFACT_ROOT = None


class AppendixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base, cls.inv = b.current(), a.current()

    def setUp(self):
        if ARTIFACT_ROOT is None:
            tmp = tempfile.TemporaryDirectory()
            self.addCleanup(tmp.cleanup)
            self.root = Path(tmp.name)
        else:
            index = unittest.defaultTestLoader.getTestCaseNames(type(self)).index(self._testMethodName) + 1
            self.root = Path(ARTIFACT_ROOT) / str(index)
            self.root.mkdir(parents=True)
        self.path, self.rid, self.product = fixture(self.root, self.base)
        self.observer, self.appendix = self.root / 'observer', self.root / 'appendix'
        patcher = patch.object(a, 'current', return_value=self.inv)
        patcher.start()
        self.addCleanup(patcher.stop)

    def files(self):
        return {p.name: p.read_bytes() for p in self.product.iterdir()}

    def run_product(self, case='success'):
        result = a.process.run_neutral(self.path, case=case, folder=self.observer)
        self.assertEqual(result['exit_code'], 0, (self.observer / 'stderr.txt').read_text())
        self.assertEqual(result['product']['status'], 'CLOSED_NEUTRAL_VERIFIED' if case == 'success' else 'NOT_EVALUABLE')
        self.before = self.files()
        return result

    def remember(self, result):
        (self.root / 'appendix-result.json').write_bytes(b.old.canonical(result))
        return result

    def publish(self):
        return self.remember(a.publish(self.path, observer=self.observer, directory=self.appendix))

    def test_bounded_process_to_seven_hint_report_with_full_budget(self):
        original = a.process.run_neutral
        def observed(*args, **kwargs):
            result = original(*args, **kwargs)
            self.before = self.files()
            return result
        with patch.object(a.process, 'run_neutral', side_effect=observed):
            result = self.remember(a.run_neutral(self.path, observer=self.observer, directory=self.appendix))
        self.assertEqual(result['appendix_status'], 'PUBLISHED', result['reason'])
        self.assertEqual(result['product_status_reported'], 'CLOSED_NEUTRAL_VERIFIED')
        self.assertEqual(self.before, self.files())
        read = a.read_appendix(self.path, observer=self.observer, directory=self.appendix)
        self.assertTrue(read['appendix_usable'], read.get('reason'))
        self.assertEqual(len(read['evaluation']['hints']), 7)
        sizes = result['budget']['actual']['categories']
        report = (self.appendix / 'provenance.json').stat().st_size
        proof = (self.product / 'verification.json').stat().st_size
        self.assertEqual(sizes['verification'], proof + report)
        self.assertLessEqual(proof + report, 131072)
        self.assertEqual(sum(sizes.values()), result['budget']['actual']['total_bytes'])
        self.assertEqual(sizes['staging'], 0)
        self.assertTrue(result['budget']['actual']['within_limits'])
        for category in b.resources.CATEGORIES:
            measured = sum(r['bytes'] for r in result['budget']['files'] if r['category'] == category)
            self.assertEqual(sizes[category], self.inv['code_bytes'] if category == 'code' else measured)
        observed_files = {r['path'] for r in result['budget']['files'] if r['space'] == 'observer'}
        self.assertEqual(observed_files, {p.name for p in self.observer.iterdir()})
        self.assertTrue(all(s['account']['within_limits'] for s in result['publication_steps']))
        self.assertTrue(any(s['placement'] == 'staging' and s['account']['categories']['staging'] == report
                            for s in result['publication_steps']))
        self.assertEqual(len(result['publication_steps']), 6)

    def test_incomplete_product_never_calls_evaluator(self):
        self.run_product('memoryerror')
        with patch.object(a.evaluator, 'read_closed') as evaluate:
            result = self.publish()
            evaluate.assert_not_called()
        self.assertEqual(result['product_status_reported'], 'NOT_EVALUABLE')
        self.assertEqual(result['appendix_status'], 'NOT_PUBLISHED')
        self.assertEqual(self.before, self.files())
        self.assertFalse((self.appendix / 'provenance.json').exists())

    def test_invalid_product_terminal_never_calls_evaluator(self):
        self.run_product()
        terminal = self.product / 'terminal.json'
        value = json.loads(terminal.read_bytes())
        value['evaluation_allowed'] = False
        terminal.write_bytes(b.old.canonical(value))
        altered = self.files()
        with patch.object(a.evaluator, 'read_closed') as evaluate:
            result = self.publish()
            evaluate.assert_not_called()
        self.assertEqual(result['product_status_reported'], 'CLOSED_NEUTRAL_VERIFIED')
        self.assertFalse(result['product_validated_before_appendix'])
        self.assertFalse(result['appendix_usable'])
        self.assertEqual(altered, self.files())

    def test_input_changed_during_publication_invalidates_appendix_only(self):
        self.run_product()
        replace = a._replace
        def mutate(stage, target):
            replace(stage, target)
            if target.name == 'provenance.json':
                record = self.product / 'record.json'
                record.write_bytes(record.read_bytes() + b' ')
        with patch.object(a, '_replace', side_effect=mutate):
            result = self.publish()
        self.assertEqual(result['product_status_reported'], 'CLOSED_NEUTRAL_VERIFIED')
        self.assertTrue(result['product_validated_before_appendix'])
        self.assertFalse(result['product_inputs_unchanged'])
        self.assertFalse(result['appendix_usable'])
        self.assertIn('INPUTS_CHANGED', result['reason'])
        self.assertFalse(a.read_appendix(self.path, observer=self.observer, directory=self.appendix)['appendix_usable'])
        self.assertEqual(self.before['terminal.json'], (self.product / 'terminal.json').read_bytes())

    def test_input_changed_after_publication_is_rejected_by_reader(self):
        self.run_product()
        result = self.publish()
        self.assertTrue(result['appendix_usable'], result['reason'])
        record = self.product / 'record.json'
        record.write_bytes(record.read_bytes() + b' ')
        read = a.read_appendix(self.path, observer=self.observer, directory=self.appendix)
        (self.root / 'reader-result.json').write_bytes(b.old.canonical(read))
        self.assertEqual(read['appendix_status'], 'INVALID')
        self.assertFalse(read['appendix_usable'])
        self.assertEqual(self.before['terminal.json'], (self.product / 'terminal.json').read_bytes())

    def test_failed_appendix_rename_counts_staging_preserves_product(self):
        self.run_product()
        replace = a._replace
        def fail(stage, target):
            if target.name == 'provenance.json':
                raise OSError('INJECTED_APPENDIX_RENAME_FAILURE')
            replace(stage, target)
        with patch.object(a, '_replace', side_effect=fail):
            result = self.publish()
        self.assertEqual(self.before, self.files())
        self.assertEqual(result['product_status_reported'], 'CLOSED_NEUTRAL_VERIFIED')
        self.assertEqual(result['appendix_status'], 'NOT_PUBLISHED')
        self.assertTrue((self.appendix / 'appendix-error.json').exists(), result)
        self.assertFalse((self.appendix / 'provenance.json').exists())
        observations = [s['failed_staging_observation'] for s in result['publication_steps'] if 'failed_staging_observation' in s]
        self.assertEqual(len(observations), 1)
        self.assertGreater(observations[0]['actual']['categories']['staging'], 0)
        self.assertEqual(observations[0]['files'][0]['bytes'], observations[0]['actual']['categories']['staging'])
        self.assertEqual(result['budget']['actual']['categories']['staging'], 0)

    def test_joint_verification_reserve_plus_one_rejects_individually_small_report(self):
        self.run_product()
        original = a.evaluator.read_closed
        proof_size = (self.product / 'verification.json').stat().st_size
        def large(*args):
            value = original(*args)
            value['neutral_padding'] = ''
            envelope = {'version': a.VERSION, 'evaluator_version': a.evaluator.VERSION,
                        'inventory': a._ref(b.old.canonical(self.inv)), 'input_snapshot_sha256': '0' * 64,
                        'evaluation': value}
            size = 131072 - proof_size - len(b.old.canonical(envelope)) + 1
            self.assertGreater(size, 0)
            value['neutral_padding'] = 'x' * size
            self.assertEqual(len(b.old.canonical(envelope)) + proof_size, 131073)
            self.assertLess(len(b.old.canonical(envelope)), 131072)
            return value
        with patch.object(a.evaluator, 'read_closed', side_effect=large):
            result = self.publish()
        self.assertEqual(self.before, self.files())
        self.assertEqual(result['appendix_status'], 'NOT_PUBLISHED')
        self.assertIn('reserve:verification', result['reason'])
        self.assertFalse((self.appendix / 'provenance.json').exists())

    def test_observer_metadata_is_counted_and_overflow_blocks_evaluation(self):
        self.run_product()
        (self.observer / 'stdout.txt').write_bytes(b'x' * 65536)
        with patch.object(a.evaluator, 'read_closed') as evaluate:
            result = self.publish()
            evaluate.assert_not_called()
        self.assertFalse(result['appendix_usable'])
        self.assertGreater(result['budget']['actual']['categories']['metadata'], 65536)
        self.assertIn('limit:metadata', result['budget']['actual']['violations'])
        self.assertEqual(self.before, self.files())

    def test_product_directory_cannot_be_used_as_appendix(self):
        with self.assertRaisesRegex(ValueError, 'ROOTS_MUST_BE_DISJOINT'):
            a.publish(self.path, observer=self.observer, directory=self.product)
        self.assertFalse(self.product.exists())


if __name__ == '__main__':
    unittest.main()
