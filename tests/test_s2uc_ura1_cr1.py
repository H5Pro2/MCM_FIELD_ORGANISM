"""Focused CR1 qualification: neutral namespaces and synthetic errors only."""
import copy
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import _s2uc_ura1_cr1_sources as src
from tools import _s2uc_ura1_cr1_source_reference as source_ref
from tools import _s2uc_ura1_cr1_stats as stats
from tools import _s2uc_ura1_cr1_stats_reference as stats_ref
from tools import s2uc_ura1_prepare_cr1 as entry


def artificial():
    """No source realization or policy; errors and labels chosen by test author."""
    reports = []
    for r in range(1, 33):
        rows = []
        for t in range(3, 1024, 2):
            q = t % 4 == 3
            b = (t+1)//4
            rows.append(dict(target=t, C=0.0, U=0.0, cue=('X' if b % 2 else 'Y') if q else None,
                             eligible=b % 3, warm=('none', 'cold', 'mixed', 'warm')[b % 4],
                             same_output=bool(b % 2), choice=('both_persistence', 'mixed', 'same_context', 'different_context')[b % 4]))
        reports.append(dict(replicate=r, orientation=(r-1) % 2, complete=True, rows=rows))
    return reports


class CR1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = (entry.ROOT/'reports/s2uc/ura1-v4-preparation-20261015-01/bootstrap.bin').read_bytes()

    def test_S01_research_locked_before_hash(self):
        with patch.object(src.hashlib, 'sha256', side_effect=AssertionError('RESEARCH_HASH_FORBIDDEN')):
            with self.assertRaises(PermissionError): src.generate(1, neutral=False)
            with self.assertRaises(PermissionError): source_ref.verify({}, 1, neutral=False)
            with self.assertRaises(PermissionError): src.admit(entry.AUTH, entry.TARGET) if entry.AUTH.exists() else src.gate(False)

    def test_S02_all_neutral_recipes_match_independent_reference(self):
        for r in range(1, 33):
            value = src.generate(r)
            self.assertEqual(value, src.generate(r))
            proof = source_ref.verify(value, r)
            self.assertTrue(proof['reference_equal'])
            self.assertEqual(len(value['ids']), 1024)
            self.assertTrue(value['neutral_only'])
            self.assertLessEqual(len(entry.raw(value)), entry.LIMITS['source_case'])
            self.assertEqual([a+b for a,b in zip(*proof['contingencies'])], [64]*4)
            for p in (0, 1):
                ids = value['ids'][p*512:(p+1)*512]
                self.assertEqual([ids[::4].count(k) for k in (0, 1)], [64, 64])
                self.assertEqual([ids[2::4].count(k) for k in (3, 4)], [64, 64])
                self.assertEqual(ids[1::4], [2]*128)
                self.assertEqual(ids[3::4], [5]*128)

    def test_S03_source_mutation_and_extra_signal_rejected(self):
        original = src.generate(1)
        for mutation in ('boundary', 'catalog', 'draws', 'extra', 'flag', 'orientation'):
            value = copy.deepcopy(original)
            if mutation == 'boundary': value['ids'][512] = 1-value['ids'][512]
            elif mutation == 'catalog': value['catalog'][0][0] += .125
            elif mutation == 'draws': value['draws']['1']['continuation'] += 1
            elif mutation == 'extra': value['phase_signal'] = True
            elif mutation == 'flag': value['neutral_only'] = False
            else: value['orientation'] = 1
            with self.assertRaises(ValueError): source_ref.verify(value, 1)

    def test_S04_rejection_sampling_and_draw_cap(self):
        stream = src.Stream(1, 0, 'continuation', draw=lambda cursor: 2**64-1 if cursor == 0 else 4)
        self.assertEqual(stream.below(3), 1)
        self.assertEqual(stream.cursor, 2)
        stream = src.Stream(1, 1, 'continuation', draw=lambda _: 2**64-1)
        with self.assertRaisesRegex(ValueError, 'DRAW_LIMIT'): stream.below(3)
        self.assertEqual(stream.cursor, 4096)
        class Rejected:
            def hexdigest(self): return 'f'*64
        with patch.object(source_ref.hashlib, 'sha256', return_value=Rejected()):
            with self.assertRaisesRegex(ValueError, 'REFERENCE_DRAW_LIMIT'): source_ref.verify({}, 1)

    def test_S05_invalid_inputs_and_no_short_research_option(self):
        for r in (0, 33, True):
            with self.assertRaises(ValueError): src.generate(r)
        for n in (0, 129, True):
            with self.assertRaises(ValueError): src.Stream(1, 0, 'continuation').below(n)
        for value in (-1, 2**64, True):
            with self.assertRaises(ValueError): src.Stream(1, 0, 'continuation', draw=lambda _: value).below(3)
        with self.assertRaises(TypeError): src.generate(1, boundary=4)
        with self.assertRaises(TypeError): src.generate(1, phase_length=4)
        with self.assertRaises(ValueError): src.Stream(1, 2, 'continuation')
        with self.assertRaises(ValueError): src.generate(1, neutral=1)

    def test_S06_neutral_hash_namespace_only(self):
        original = hashlib.sha256
        seen = []
        def checked(value):
            self.assertTrue(value.startswith(b'MCM-URA1-CR1/neutral/v1/'))
            seen.append(value)
            return original(value)
        with patch.object(src.hashlib, 'sha256', side_effect=checked):
            source_ref.verify(src.generate(1), 1)
        self.assertTrue(any(b'/phase=0/' in x for x in seen))
        self.assertTrue(any(b'/phase=1/' in x for x in seen))

    def test_T01_matrix_identity_and_stratification(self):
        self.assertEqual(hashlib.sha256(self.matrix).hexdigest(), stats.MATRIX_SHA)
        self.assertTrue(stats_ref.verify_matrix(self.matrix))
        for start in range(0, len(self.matrix), 32):
            row = self.matrix[start:start+32]
            self.assertTrue(all(v % 2 == 0 and v < 32 for v in row[:16]))
            self.assertTrue(all(v % 2 == 1 and v < 32 for v in row[16:]))
        broken = bytes([1])+self.matrix[1:]
        with self.assertRaises(ValueError): stats.aggregate(artificial(), broken)
        with self.assertRaises(ValueError): stats_ref.verify_matrix(broken)

    def test_T02_window_boundaries_and_denominators(self):
        rows = artificial()[0]['rows']
        expected = {'Q_early_post':(515,639,32), 'Q_pre':(387,511,32),
                    'Q_late_post':(643,1023,96), 'Q_all_post':(515,1023,128)}
        for mask, (first, last, count) in expected.items():
            selected = stats.select(rows, mask)
            self.assertEqual((selected[0]['target'], selected[-1]['target'], len(selected)), (first,last,count))
        early = {x['target'] for x in stats.select(rows, 'Q_early_post')}
        self.assertNotIn(511, early)  # Q128
        self.assertIn(515, early)     # Q129
        self.assertIn(639, early)     # Q160
        self.assertNotIn(643, early)  # Q161

    def test_T03_positive_negative_and_zero_full_reference(self):
        for delta, verdict in ((.25, 'U_EARLY_POST_BETTER'), (-.25, 'C_EARLY_POST_BETTER'), (0., 'INCONCLUSIVE')):
            reports = artificial()
            for rep in reports:
                for row in rep['rows']:
                    if row['target'] % 4 == 3 and 515 <= row['target'] <= 639:
                        row['C'], row['U'] = (.5+delta, .5)
                    else:
                        row['C'], row['U'] = (0., .75)  # strong opposite outside window
            actual = stats.aggregate(reports, self.matrix)
            self.assertTrue(stats_ref.verify(reports, self.matrix, actual))
            primary = actual['primary']
            self.assertEqual(F(primary['mean']), F(delta))
            self.assertEqual(primary['ci'], [str(F(delta))]*2)
            self.assertEqual(primary['verdict'], verdict)
            self.assertEqual(actual['secondary'][0]['count'], 1024)
            self.assertEqual(sum(x['count'] for x in actual['diagnosis'] if x['partition'] == 'warm'), 1024)

    def test_T04_orientation_balance_and_independent_nonconstant_quantiles(self):
        values = [F((i % 7)-3, 16) for i in range(32)]
        self.assertEqual(stats.interval(values, self.matrix), stats_ref.interval(values, self.matrix))
        self.assertEqual(stats.quantile([0, 10, 20, 30], F(1,4)), F(15,2))
        reports = artificial()
        for rep in reports:
            for row in rep['rows']:
                row['C'], row['U'] = (.75 if rep['orientation'] == 0 else .25, .5)
        actual = stats.aggregate(reports, self.matrix)
        self.assertTrue(stats_ref.verify(reports, self.matrix, actual))
        self.assertEqual(actual['primary']['ci'], ['0','0'])
        self.assertEqual(actual['secondary'][1]['mean'], '1/4')
        self.assertEqual(actual['secondary'][2]['mean'], '-1/4')

    def test_T05_decision_zero_touches_and_crossings(self):
        for ci in (['0','1/4'], ['-1/4','0'], ['0','0'], ['-1/4','1/4']):
            self.assertEqual(stats.decision(ci), 'INCONCLUSIVE')
        self.assertEqual(stats.decision(['1/8','1/4']), 'U_EARLY_POST_BETTER')
        self.assertEqual(stats.decision(['-1/4','-1/8']), 'C_EARLY_POST_BETTER')
        with self.assertRaises(ValueError): stats.decision(['1','0'])

    def test_T06_incomplete_and_invalid_data_no_verdict(self):
        for mutation in ('case', 'target', 'orientation', 'complete', 'nan', 'cue'):
            reports = artificial()
            if mutation == 'case': reports.pop()
            elif mutation == 'target': reports[0]['rows'].pop(256)
            elif mutation == 'orientation': reports[0]['orientation'] = 1
            elif mutation == 'complete': reports[0]['complete'] = False
            elif mutation == 'nan': reports[0]['rows'][256]['C'] = float('nan')
            else: reports[0]['rows'][256]['cue'] = None
            with self.assertRaises(ValueError): stats.aggregate(reports, self.matrix)
            with self.assertRaises(ValueError): stats_ref.verify(reports, self.matrix, {})

    def test_T07_reference_detects_window_output_corruption(self):
        reports = artificial()
        actual = stats.aggregate(reports, self.matrix)
        actual['primary']['mean'] = '1/32'
        with self.assertRaises(ValueError): stats_ref.verify(reports, self.matrix, actual)

    def test_T08_nontrivial_intervals_touch_zero_full_reference(self):
        for arm in ('C','U'):
            reports=artificial()
            for row in stats.select(reports[0]['rows'],'Q_early_post'):
                row[arm]=.25
            actual=stats.aggregate(reports,self.matrix)
            self.assertTrue(stats_ref.verify(reports,self.matrix,actual))
            ci=list(map(F,actual['primary']['ci']))
            self.assertEqual(actual['primary']['verdict'],'INCONCLUSIVE')
            if arm=='C':self.assertEqual(ci[0],0);self.assertGreater(ci[1],0)
            else:self.assertLess(ci[0],0);self.assertEqual(ci[1],0)

    def test_T09_no_cold_stories_retained_and_empty_partition(self):
        reports=artificial()
        for rep in reports:
            for row in rep['rows']:
                row.update(warm='warm',eligible=1,same_output=True,choice='same_context',C=.25,U=.25)
        actual=stats.aggregate(reports,self.matrix)
        self.assertTrue(stats_ref.verify(reports,self.matrix,actual))
        self.assertEqual(actual['primary']['pairs'],['0']*32)
        self.assertEqual(actual['secondary'][0]['count'],1024)
        cold=next(x for x in actual['diagnosis'] if x['partition']=='warm' and x['label']=='cold')
        self.assertEqual(cold['count'],0)
        self.assertIsNone(cold['mean_delta'])
        self.assertEqual(actual['primary']['name'],'CR1:Q129-160:C-U')

    def test_E01_exclusive_target_no_authorization(self):
        self.assertFalse(entry.TARGET.exists())
        self.assertFalse(entry.AUTH.exists())
        self.assertEqual(entry.NAMESPACE, 'MCM-URA1-CR1/source/v1')
        with self.assertRaises(FileNotFoundError): entry.authorization(entry.AUTH, 'a'*64)

    def test_E02_existing_target_cannot_resume(self):
        with tempfile.TemporaryDirectory() as d, patch.object(entry,'TARGET',Path(d)), patch.object(entry,'install_job'), patch.object(entry,'validate_binding',return_value=({},'a'*64)), patch.object(entry,'authorization'), patch.object(entry,'launch',side_effect=AssertionError('NO_LAUNCH')):
            with self.assertRaises(FileExistsError): entry.run('unused','unused')

    def test_E03_unchanged_protection_objects_and_research_faults_disabled(self):
        import time
        from tools import _s2uc_ura1_fs_accounting_v4 as fs
        from tools import _s2uc_ura1_v2_series as series
        from tools import _s2uc_ura1_terminal_v3 as terminal
        self.assertIs(entry.LIMITS, series.LIMITS)
        from tools import _s2uc_ura1_cr1_series as cr1_series
        self.assertIs(entry.policy_case, cr1_series.policy_case)
        self.assertIs(entry.execute_with_receipts, terminal.execute_with_receipts)
        self.assertIs(entry.supervise, fs.supervise)
        self.assertIs(entry.Terminal, fs.Terminal)
        with tempfile.TemporaryDirectory() as d:
            t=entry.Terminal(d,time.monotonic());t.begin(2)
            ledger=entry.IntegratedLedger(t,0,'research');ledger.arm_started=True;ledger.check()
            self.assertFalse(ledger.fired)
            self.assertFalse(list(Path(d).glob('neutral-*')))

    def test_E04_no_legacy_entry_or_shortcut_in_research(self):
        import ast
        tree=ast.parse(Path(entry.__file__).read_text())
        worker=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='worker')
        research=next(n for n in ast.walk(worker) if isinstance(n,ast.If) and ast.unparse(n.test)=="mode == 'research'" and any(isinstance(x,ast.Assign) for x in n.body))
        text=ast.unparse(ast.Module(body=research.body,type_ignores=[]))
        self.assertNotIn('fixtures',text)
        self.assertIn('neutral=False',text)
        self.assertNotIn('boundary',text)
        self.assertNotIn('s2uc_ura1_prepare_v4',Path(entry.__file__).read_text())
        with self.assertRaises(PermissionError): entry.worker(entry.PREP,0,'unknown')


if __name__ == '__main__':
    unittest.main()
