"""Bounded technical fixtures; never construct the 48-position contrast."""
import dataclasses
import json
import sys
import tracemalloc
import unittest

from tools._s2uc_multi_error import MultiErrorAdapter, POLICY, CELL, HEAD, ENTRY, REASONS
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2tu_retained_trace import Frame, RetainedTrace
from tools._s2ub_candidate_confirmation import CandidateTrace
from tools._s2uc_continuation_adapter import consume_prediction
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2uc_promotion_ema import PromotionAdapter
from tools.s2uc_continuous_comparison import state
from tests.test_s2uc_paired_error_ema import vec, sample, feed, PROFILE
from tools._s2uc_multi_observer import Meter

FACTS = {}


def adapter(cls=MultiErrorAdapter):
    return cls(FactorRecencyArm(PROFILE, 'owner'), 'stream', multi_policy=POLICY)


def frames(values, start, segment):
    return tuple(Frame(vec(v), PROFILE, 'owner', segment, start+i) for i, v in enumerate(values))


def fixture(six=False, zero=False):
    a = adapter()
    for j in range(3):
        vals = (0.,)*4 if zero else (.2, .2, .2, .6+j*.1) if six else (.2, .3, .6+j*.1, .9)
        fs = frames(vals, j*4+1, 'r'+str(j))
        if j < 2:
            a.arm._retained_many.append(RetainedTrace(j+1, fs))
        else:
            a.arm._candidate = CandidateTrace(3, fs)
    a.arm._retained_generation = 2
    a.arm._candidate_generation = 3
    vals = (0., 0.) if zero else (.2, .2) if six else (.2, .3)
    a.pair = list(frames(vals, 13, 'p4'))
    a.intervals = [(12*4800, 13*4800), (13*4800, 14*4800)]
    a.next_index = 15
    return a


def freeze(a):
    assert a.arm.hint(a.pair[0]) is None
    r = a.arm.hint(a.pair[1])
    return json.loads(a._receipt(r['decision'], [13, 14], a.intervals, r['matches']).json_text)


def seed(a, slot, role, generation, off, ec, ep):
    CELL.pack_into(a.bank, slot*32, generation, ec, ep, role, off, 0, 1)


def cells(a):
    return [list(CELL.unpack_from(a.bank, i*32)) for i in range(6) if a.bank[i*32+27]]


def owned(a):
    """Count retained adapter metadata; original payloads have separate slot accounting."""
    seen = set()
    def size(v):
        if v is None or id(v) in seen:
            return 0
        seen.add(id(v))
        if isinstance(v, Frame):
            return 0  # Original frames/payloads counted by identity, not new metadata.
        n = sys.getsizeof(v)
        if isinstance(v, (tuple, list)):
            n += sum(size(x) for x in v)
        return n
    n = sys.getsizeof(a)+sys.getsizeof(vars(a))
    for key, v in vars(a).items():
        if key in ('arm', 'pair', 'intervals', 'pending_prediction', '_checkpoint'):
            continue
        n += size(v)
    if a.pending_prediction:
        n += sys.getsizeof(a.pending_prediction)+size(a.pending_prediction.provenance_json)
    return n


def measure(a, operation):
    retained = owned(a)
    tracemalloc.start()
    base = tracemalloc.get_traced_memory()[0]
    result = None
    try:
        result = operation()
    finally:
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        FACTS.setdefault('heap', []).append(dict(retained=retained, transient=peak-base, total=retained+max(0, peak-base)))
        if hasattr(result, 'json_text'):
            FACTS['receipt_max'] = max(FACTS.get('receipt_max', 0), len(result.json_text.encode()))
    return result


class MultiTests(unittest.TestCase):
    def clean(self, a):
        self.assertTrue(a.closed)
        self.assertFalse(any(a.bank))
        self.assertEqual(a._frozen, [None]*6)
        self.assertIsNone(a._pframe)
        self.assertIsNone(a.pending_prediction)

    def test_T01_all_alternatives(self):
        a = fixture()
        seed(a, 0, 0, 1, 0, 0., .4)
        r = freeze(a)
        self.assertEqual(r['status'], 'ABSTAIN_AMBIGUOUS')
        self.assertEqual(r['decision'], 'SELECTED_BY_ERROR')
        self.assertEqual(len(r['matches']), 3)
        a.consume_feedback(sample(a, vec(.7)))
        actual = {(r[3], r[0], r[4]): (r[1], r[2]) for r in cells(a)}
        self.assertEqual(len(actual), 3)
        self.assertAlmostEqual(actual[0, 1, 0][0], .05)
        self.assertEqual(actual[0, 2, 0][0], 0.)
        self.assertAlmostEqual(actual[1, 3, 0][0], .1)
        FACTS['T1'] = dict(receipt=r, all_three_updated=True)
        a._terminate()

    def test_T02_cold(self):
        a = fixture(); r = freeze(a)
        self.assertEqual(r['decision'], 'COLD_ONLY')
        self.assertTrue(all(x['ec'] is None for x in r['hypotheses']))
        a.consume_feedback(sample(a, vec(.7)))
        self.assertEqual(len(cells(a)), 3)
        FACTS['T2'] = r
        a._terminate()

    def test_T03_ties_and_negative_zero(self):
        reasons = []
        for pairs, reason in [(((.25, .25),), 'NO_ESTIMATED_IMPROVEMENT'),
                              (((0., .5), (.25, .75)), 'TIED_IMPROVEMENT'),
                              (((-0., 0.),), 'NO_ESTIMATED_IMPROVEMENT'),
                              (((.5, 0.),), 'NO_ESTIMATED_IMPROVEMENT')]:
            a = fixture()
            for i, (ec, ep) in enumerate(pairs): seed(a, i, 0, i+1, 0, ec, ep)
            r = freeze(a); self.assertEqual(r['decision'], reason)
            self.assertEqual(r['choice'], 0)
            reasons.append(r); a._terminate()
        FACTS['T3'] = reasons

    def test_T04_different_history_and_order(self):
        for reverse in (False, True):
            a = fixture()
            seed(a, 0, 0, 1, 0, .5, 1.)
            seed(a, 1, 0, 2, 0, 0., .25)
            if reverse: a.arm._retained_many.reverse()
            r = freeze(a)
            g = ENTRY.unpack_from(a.bank, 208+16*(r['choice']-1))[0]
            self.assertEqual(g, 1)  # EC alone would prefer generation2.
            a._terminate()

    def test_T05_six_and_nine(self):
        a = fixture(six=True); r = freeze(a)
        self.assertEqual(HEAD.unpack_from(a.bank, 192)[2], 6)
        expected = {(ENTRY.unpack_from(a.bank,208+16*i)[1],ENTRY.unpack_from(a.bank,208+16*i)[0],
                     ENTRY.unpack_from(a.bank,208+16*i)[2]): abs(a._frozen[i].values[0]-.45) for i in range(6)}
        a.consume_feedback(sample(a, vec(.45)))
        self.assertEqual(len(cells(a)), 6)
        for c in cells(a):
            self.assertAlmostEqual(c[1],expected[c[3],c[0],c[4]])
            self.assertAlmostEqual(c[2],.25)
        FACTS['T5_six'] = r; a._terminate()
        a = fixture(zero=True); r = freeze(a)
        self.assertEqual(len(r['matches']), 9)
        self.assertEqual(r['decision'], 'NO_ELIGIBLE_CONTEXT')
        self.assertTrue(all(not x['eligible'] for x in r['hypotheses']))
        FACTS['T5_nine'] = r; a._terminate()

    def test_T06_loss_no_resurrection(self):
        a = fixture(); freeze(a)
        original = a._frozen[0]
        a.arm._retained_many.pop(0)
        a.arm._candidate = CandidateTrace(4, a.arm._candidate.frames)
        a._prune()
        self.assertIs(a._frozen[0], original)
        a.consume_feedback(sample(a, vec(.7)))
        self.assertEqual([(r[3], r[0]) for r in cells(a)], [(0, 2)])
        a._terminate()

    def test_T07_promotion_open_ticket(self):
        a = fixture(); seed(a, 0, 1, 3, 0, -0., .5); freeze(a)
        ticket = bytes(a.bank[192:304]); frozen = tuple(a._frozen)
        c = a.arm._candidate
        # Complete normal confirmation admission at an even boundary.
        a.arm._forming = list(frames([f.values[0] for f in c.frames[:3]], 17, 'p5'))
        a.arm._forming_segment = 'p5'
        a._admit(Frame(c.frames[3].values, PROFILE, 'owner', 'p5', 20))
        self.assertEqual(bytes(a.bank[192:304]), ticket)
        self.assertEqual(tuple(a._frozen), frozen)
        self.assertEqual(cells(a)[0][0:3], [3, -0., .5])
        a.consume_feedback(sample(a, vec(.6)))
        self.assertEqual(next(r for r in cells(a) if r[0] == 3)[1:3], [-0., .5])
        FACTS['T7'] = dict(ticket_unchanged=True, no_candidate_redirect=True)
        a._terminate()

    def test_T08_original_not_current_store(self):
        a = fixture(); freeze(a)
        old = a._frozen[0]
        a.arm._retained_many[0] = RetainedTrace(1, frames((.2, .3, .99, .9), 101, 'changed'))
        a.consume_feedback(sample(a, old.values))
        self.assertEqual(cells(a)[0][1], 0.)
        a._terminate()

    def test_T09_invalid(self):
        for bad in ('duplicate', 'nan', 'scope', 'target', 'values'):
            a = fixture()
            if bad in ('duplicate', 'nan'):
                seed(a, 0, 0, 1, 0, float('nan') if bad == 'nan' else 0., .5)
                if bad == 'duplicate': seed(a, 1, 0, 1, 0, 0., .5)
                with self.assertRaises(Exception): freeze(a)
            else:
                freeze(a); s = sample(a, vec(.5))
                s = dataclasses.replace(s, **({'owner': 'wrong'} if bad == 'scope' else
                    {'index': 16} if bad == 'target' else {'values': vec(float('inf'))}))
                with self.assertRaises(Exception): a.consume_feedback(s)
            self.clean(a)
        a = fixture(); a.arm.hint(a.pair[0]); r = a.arm.hint(a.pair[1])
        r['matches'].append(r['matches'][0])
        with self.assertRaises(Exception): a._receipt(r['decision'], [13, 14], a.intervals, r['matches'])
        self.clean(a)
        for config in ({'policy': 'factor_scaled_v1'}, {'retrieval_policy': 'signal_approx_v1', 'epsilon': .01, 'tau': .01}):
            with self.assertRaises(Exception):
                MultiErrorAdapter(FactorRecencyArm(PROFILE, 'owner'), 'stream', multi_policy=POLICY, **config)

    def test_T10_every_publication_field(self):
        points = [('validated', -1), ('published', -1)] + [
            (s, i) for i in range(6) for s in ('generation', 'ec', 'ep', 'role', 'offset', 'quality', 'valid')]
        for point in points:
            a = fixture(six=True); freeze(a)
            def fail(stage, index):
                if (stage, index) == point: raise KeyboardInterrupt('technical interruption')
            a._checkpoint = fail
            with self.assertRaises(KeyboardInterrupt): a.consume_feedback(sample(a, vec(.4)))
            self.clean(a)
        FACTS['T10'] = dict(interruption_points=len(points), all_terminal=True)

    def test_T11_reentrancy_end_and_double(self):
        stages = []
        a = fixture()
        def check(stage, index):
            with self.assertRaises(Exception): _ = a.selected_values
            with self.assertRaises(Exception): a.release_prediction()
            with self.assertRaises(Exception): a.finish_story()
            stages.append(stage)
        a._checkpoint = check; freeze(a); a.consume_feedback(sample(a, vec(.4)))
        self.assertIn('frozen', stages); self.assertIn('published', stages)
        with self.assertRaises(Exception): a.consume_feedback(sample(a, vec(.4)))
        self.clean(a)
        a = fixture(); freeze(a); a.pair.clear(); a.finish_story(); self.clean(a)

    def test_R01_defaults_and_neutral_regression(self):
        a = MultiErrorAdapter(FactorRecencyArm(PROFILE, 'owner'), 'stream')
        b = SignalApproxAdapter(FactorRecencyArm(PROFILE, 'owner'), 'stream')
        for x in (.11, .23, .67, .89)*3:
            for z in (a, b):
                s = sample(z, vec(x))
                if z.pending_prediction: consume_prediction(z, s)
                r = z.accept_perception(s)
                if z is a: ar = r
                else: self.assertEqual(ar, r)
            self.assertEqual(state(a.arm), state(b.arm))
        a.finish_story(); b.finish_story()
        u = adapter()
        m = PromotionAdapter(FactorRecencyArm(PROFILE, 'owner'), 'stream',
            selection_policy='paired_error_ema_v1', promotion_policy='direct_promotion_v1')
        for x in (.11, .23, .67, .89)*3:
            for z in (u, m): feed(z, vec(x))
            self.assertEqual(state(u.arm), state(m.arm))
            self.assertEqual(u.selected_values, m.selected_values)
            old = [list(CELL.unpack_from(m._errors.cells, i*32)) for i in range(12) if m._errors.cells[i*32+27]]
            self.assertEqual(sorted(cells(u)), sorted(old))
        u.finish_story(); m.finish_story()

    def test_R02_resources(self):
        a = fixture(six=True)
        # Measure production freeze only; JSON decoding is external observer work.
        a.arm.hint(a.pair[0]); r = a.arm.hint(a.pair[1])
        receipt = measure(a, lambda: a._receipt(r['decision'], [13, 14], a.intervals, r['matches']))
        size = len(receipt.json_text.encode())
        self.assertEqual(len(a.bank), 416)
        s = sample(a, vec(.45)); measure(a, lambda: a.consume_feedback(s))
        a._terminate()
        a = fixture(six=True); freeze(a)
        def fail(stage, index):
            if stage == 'quality' and index == 4: raise KeyboardInterrupt()
        a._checkpoint = fail; s = sample(a, vec(.45))
        with self.assertRaises(KeyboardInterrupt): measure(a, lambda: a.consume_feedback(s))
        self.clean(a)
        # Complete normal admission includes actual factor scan and receipt construction.
        a = adapter()
        for x in (.17, .29, .61, .83)*4:
            s = sample(a, vec(x))
            if a.pending_prediction: measure(a, lambda: a.consume_feedback(s))
            measure(a, lambda: a.accept_perception(s))
        measure(a, a.finish_story)
        peak = max(x['total'] for x in FACTS['heap'])
        FACTS['R2'] = dict(additional_python_peak=peak, packed=416, receipt_bytes=size,
                            transient_utf8_upper=2*size)
        self.assertLessEqual(peak, 16384)
        self.assertLessEqual(size, 16384)

    def test_R02_full_scan_and_transient_frames(self):
        # Six warm hypotheses: production factor scan AND expanded receipt in the same call.
        a = fixture(six=True)
        for i in range(6): seed(a, i, 0 if i < 4 else 1, i//2+1, i%2, .1234567890123456, .9876543210987654)
        a.pair.clear(); a.intervals.clear(); a.next_index = 13
        for _ in range(2):
            s = sample(a, vec(.2)); measure(a, lambda: a.accept_perception(s))
        a._terminate()
        # Independent frame tracing, including all production-stack locals and held evictions.
        meter_facts = []
        for case in ('six', 'promotion', 'neutral'):
            a = adapter() if case == 'neutral' else fixture(six=case == 'six')
            meter = Meter(a)
            sys.settrace(meter.trace)
            try:
                if case == 'neutral':
                    for x in (.13, .27, .59, .91)*4: feed(a, vec(x))
                    a.finish_story()
                elif case == 'six':
                    freeze(a); a.consume_feedback(sample(a, vec(.4))); a._terminate()
                else:
                    seed(a, 0, 1, 3, 0, 0., .5); freeze(a)
                    c = a.arm._candidate
                    a.arm._forming = list(frames([f.values[0] for f in c.frames[:3]], 17, 'p5'))
                    a.arm._forming_segment = 'p5'
                    a._admit(Frame(c.frames[3].values, PROFILE, 'owner', 'p5', 20))
                    a.consume_feedback(sample(a, vec(.4))); a._terminate()
            finally: sys.settrace(None)
            meter_facts.append(dict(case=case, frames=meter.frames, slots=meter.slots, combined=meter.combined))
        FACTS['R2_frames'] = meter_facts
        FACTS.setdefault('R2', {})['additional_python_peak'] = max(x['total'] for x in FACTS['heap'])
        self.assertLessEqual(FACTS['R2']['additional_python_peak'], 16384)

    def test_R02_maximum_metadata(self):
        a = fixture(six=True)
        a.arm.owner = 'o'*96; a.stream = 's'*96
        for i, t in enumerate(a.arm._retained_many):
            a.arm._retained_many[i] = RetainedTrace(2**64-3+i, tuple(dataclasses.replace(f, owner=a.arm.owner) for f in t.frames))
        a.arm._candidate = CandidateTrace(2**64-1, tuple(dataclasses.replace(f, owner=a.arm.owner) for f in a.arm._candidate.frames))
        a._feedback_scope = a._scope()
        a.pair.clear(); a.intervals.clear(); a.next_index = 13
        for i in range(6): seed(a, i, 0 if i<4 else 1, 2**64-3+i//2, i%2, .1234567890123456+i*.001, .9876543210987654)
        for _ in range(2):
            s = dataclasses.replace(sample(a, vec(.2)), owner=a.arm.owner, stream=a.stream)
            measure(a, lambda: a.accept_perception(s))
        s = dataclasses.replace(sample(a, vec(.5)), owner=a.arm.owner, stream=a.stream)
        measure(a, lambda: a.consume_feedback(s))
        a._terminate()
        self.assertLessEqual(max(x['total'] for x in FACTS['heap']), 16384)


if __name__ == '__main__':
    unittest.main()
