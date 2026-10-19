import dataclasses
import json
import math
import struct
import sys
import tracemalloc
import unittest
from unittest.mock import patch

from tools import _s2uc_paired_error_ema as e
from tools import _s2uc_paired_error_replay as replay
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import PerceptionSample, AdapterError
from tools._s2uc_continuation_adapter import PredictionReceipt, consume_prediction
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2tu_retained_trace import Frame, RetainedTrace
from tools._s2ub_candidate_confirmation import CandidateTrace
from tools.s2uc_continuous_comparison import state

PROFILE='b'*64
FACTS={}


def vec(x):return (float(x),)*48


def adapter(**kwargs):
    return e.PairedErrorAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',selection_policy='paired_error_ema_v1',**kwargs)


def sample(a,v,**changes):
    i=a.next_index;start=a.start_sample+(i-1)*a.hop
    s=PerceptionSample(v,PROFILE,'owner','stream',i,start,start+a.window)
    return dataclasses.replace(s,**changes)


def feed(a,v):
    s=sample(a,v)
    if a.pending_prediction is not None:a.consume_feedback(s)
    return a.accept_perception(s)


def seeded():
    a=adapter();basis=[vec(x) for x in (.11,.23,.67,.89)]
    for v in basis*2:feed(a,v)
    # Retained generation is fresh after promotion; no inherited candidate error.
    return a,basis


def isolated_pending(role=0,generation=1,offset=0,quality=0,ec=None,ep=None):
    a=adapter();frames=tuple(Frame(vec(.1+i*.1),PROFILE,'owner','p1',i+1) for i in range(4))
    if role==0:a.arm._retained_many=[RetainedTrace(generation,frames)]
    else:a.arm._candidate=CandidateTrace(generation,frames)
    if ec is not None:a._errors.update(role,generation,offset,quality,ec,ep)
    a._errors.prepare(role,generation,offset,quality,1)
    a.pending_prediction=PredictionReceipt(1,0,'PREDICTED',vec(.7),vec(.2),'{}')
    return a


def addon_owned(a):
    # Conservative Python retained footprint: includes complete instance dict,
    # owned state and all scope scalar/string objects even when shared.
    seen=set()
    def size(obj):
        if id(obj) in seen:return 0
        seen.add(id(obj));n=sys.getsizeof(obj)
        if isinstance(obj,(tuple,list)):n+=sum(size(x) for x in obj)
        elif isinstance(obj,e.ErrorMemory):n+=size(obj.cells)+size(obj.ticket)
        return n
    return sys.getsizeof(vars(a))+sum(size(getattr(a,k)) for k in ('_errors','_feedback_scope','_selection_policy'))


def measured(a,operation):
    retained=addon_owned(a)
    tracemalloc.start();before=tracemalloc.get_traced_memory()[0]
    failure=None
    try:operation()
    except AdapterError as exc:failure=str(exc)
    finally:
        current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return dict(retained_python_bytes=retained,temporary_allocation_peak=peak-before,
        total_additional_upper=retained+max(0,peak-before),error=failure)


class PairedErrorTests(unittest.TestCase):
    def test_E1_explicit_policy_first_choice_shadow_and_delay(self):
        off=e.PairedErrorAdapter(FactorRecencyArm(PROFILE,'owner'),'stream')
        self.assertIsNone(off._errors);self.assertEqual(off.selection_policy,'disabled')
        a,basis=seeded();self.assertFalse(any(a._errors.cells))
        for v in basis[:2]:feed(a,v)
        p=a.pending_prediction;before=bytes(a._errors.cells)
        self.assertIs(a.selected_values,p.persistence_values)
        self.assertEqual(before,bytes(384))
        next_sample=sample(a,basis[2]);a.consume_feedback(next_sample)
        self.assertEqual(a._errors.errors(0,1,0,0),(0.,e.mae48(basis[1],basis[2])))
        self.assertIsNone(a.selected_values)
        a.accept_perception(next_sample);feed(a,basis[3])
        for v in basis[:2]:feed(a,v)
        self.assertIs(a.selected_values,a.pending_prediction.context_values)
        self.assertEqual(a.pending_prediction.context_values,p.context_values)
        with self.assertRaisesRegex(AdapterError,'IMMUTABLE'):a.selection_policy='disabled'
        a._terminate();self.assertFalse(any(a._errors.cells+a._errors.ticket))
        FACTS['E1']='cold retained key selects persistence; unselected context is scored; next query can select context; no early update'

    def test_E2_tie_ema_and_numerical_order(self):
        a=isolated_pending(ec=.25,ep=.25)
        self.assertIs(a.selected_values,a.pending_prediction.persistence_values)
        a.consume_feedback(sample(a,vec(.7)))
        self.assertEqual(a._errors.errors(0,1,0,0),(.125,.125+.5*e.mae48(vec(.2),vec(.7))))
        x=tuple([1e16]+[1.]*47);y=vec(0.)
        left=0.
        for k in range(48):left=left+abs(x[k]-y[k])
        self.assertEqual(e.mae48(x,y),left/48.)
        self.assertNotEqual(e.mae48(x,y),math.fsum(abs(x[k]-y[k]) for k in range(48))/48.)
        self.assertIs(replay.mae48,e.mae48)
        FACTS['E2']='alpha1/2; ties persist; ordered binary64 differs deliberately from fsum; one shared function for E/K/P'

    def test_E3_complete_validation_before_atomic_update(self):
        mutations=[dict(index=2),dict(index=True),dict(owner='other'),dict(profile='c'*64),dict(stream='other'),
            dict(start_sample=1),dict(end_sample=4801),dict(start_sample=0.0),dict(values=(0.,)*47),
            dict(values=vec(float('nan'))),dict(values=(1,)*48)]
        for changes in mutations:
            a=isolated_pending(ec=.1,ep=.4);s=sample(a,vec(.7),**changes)
            with patch.object(e.ErrorMemory,'update',side_effect=AssertionError('UPDATE_BEFORE_VALIDATION')):
                with self.assertRaises(AdapterError):a.consume_feedback(s)
            self.assertTrue(a.closed);self.assertFalse(any(a._errors.cells+a._errors.ticket))
        a=isolated_pending();s=sample(a,vec(.7));a.consume_feedback(s)
        with patch.object(e.ErrorMemory,'update',side_effect=AssertionError('DOUBLE_UPDATE')):
            with self.assertRaises(AdapterError):a.consume_feedback(s)
        a=isolated_pending();a.stream='changed'
        with self.assertRaisesRegex(AdapterError,'SCOPE_CHANGED'):a.consume_feedback(sample(a,vec(.7)))
        FACTS['E3']=dict(invalid_variants=len(mutations),time_checked_before_update=True,duplicate_rejected=True,scope_state_cleared=True)

    def test_E4_numerical_failure_no_partial_commit(self):
        memory=e.ErrorMemory();memory.update(0,1,0,0,.2,.4);before=bytes(memory.cells)
        for ec,ep in [(float('inf'),.1),(.1,float('nan')),(-.1,.2)]:
            with self.assertRaises(AdapterError):memory.update(0,1,0,0,ec,ep)
            self.assertEqual(bytes(memory.cells),before)
        a=isolated_pending(ec=.2,ep=.4)
        # Context error finite, persistence difference overflows. Neither EMA commits.
        a.pending_prediction=dataclasses.replace(a.pending_prediction,context_values=vec(1e308),persistence_values=vec(-1e308))
        with patch.object(e.ErrorMemory,'update',side_effect=AssertionError('PARTIAL_UPDATE')):
            with self.assertRaisesRegex(AdapterError,'MAE_NONFINITE'):a.consume_feedback(sample(a,vec(1e308)))
        self.assertFalse(any(a._errors.cells+a._errors.ticket));self.assertTrue(a.closed)
        with self.assertRaisesRegex(AdapterError,'MAE_NONFINITE'):e.mae48(vec(1e308),vec(0.))
        FACTS['E4']='difference/sum overflow and invalid errors rejected; no partial pair commit'

    def test_E5_role_generation_offset_quality_and_promotion(self):
        memory=e.ErrorMemory()
        for role,g in [(0,1),(0,2),(1,1)]:
            for offset in (0,1):
                for quality in (0,1):memory.update(role,g,offset,quality,float(g+offset+quality+role),.25)
        self.assertEqual(sum(e.CELL.unpack_from(memory.cells,i*32)[-1] for i in range(12)),12)
        with self.assertRaisesRegex(AdapterError,'EMA_CELL_LIMIT'):memory.update(0,3,0,0,.1,.2)
        self.assertNotEqual(memory.errors(0,1,0,0),memory.errors(1,1,0,0))
        self.assertNotEqual(memory.errors(0,1,0,0),memory.errors(0,1,1,0))
        self.assertNotEqual(memory.errors(0,1,0,0),memory.errors(0,1,0,1))
        a,basis=seeded();self.assertFalse(any(a._errors.cells))
        # Real promotion: candidate key receives feedback at target7, disappears at8.
        c=adapter()
        for v in basis+basis[:3]:feed(c,v)
        self.assertIsNotNone(c._errors.errors(1,1,0,0))
        feed(c,basis[3]);self.assertIsNone(c._errors.errors(1,1,0,0));self.assertIsNone(c._errors.errors(0,1,0,0))
        FACTS['E5']='12 independent cells; roles/generations/offsets/qualities separated; actual candidate promotion resets'

    def test_E6_evicted_pending_ticket_and_confirmation_lifetime(self):
        a=isolated_pending(ec=.1,ep=.2)
        frames=a.arm._retained_many[0].frames
        a.arm._retained_many=[RetainedTrace(2,frames)];a._errors.prune(a)
        a.consume_feedback(sample(a,vec(.7)))
        self.assertFalse(any(a._errors.cells));self.assertIsNone(a._errors.errors(0,2,0,0))
        a,basis=seeded()
        for v in basis[:3]:feed(a,v)
        errors=a._errors.errors(0,1,0,0)
        feed(a,basis[3]);self.assertEqual(a._errors.errors(0,1,0,0),errors)
        # Real memory eviction through two other repeatedly perceived episodes.
        for j in (1,2):
            block=[vec(.31+j*.013+k*.027) for k in range(4)]
            for v in block*2:feed(a,v)
        self.assertFalse(a._generation_live(0,1));self.assertIsNone(a._errors.errors(0,1,0,0))
        FACTS['E6']='stale ticket does not revive deleted generation; exact confirmation retains errors; real FIFO eviction removes them'

    def test_E7_missing_context_end_censorship_and_default_path(self):
        a=adapter()
        feed(a,vec(.18));feed(a,vec(.29))
        self.assertIsNone(a.pending_prediction.context_values);self.assertIs(a.selected_values,a.pending_prediction.persistence_values)
        a.consume_feedback(sample(a,vec(.39)));self.assertFalse(any(a._errors.cells))
        a,basis=seeded()
        for v in basis[:2]:feed(a,v)
        self.assertIsNotNone(a.pending_prediction)
        with patch.object(e.ErrorMemory,'update',side_effect=AssertionError('NO_END_TARGET')):a.finish_story()
        self.assertTrue(a.closed);self.assertIsNone(a.selected_values);self.assertFalse(any(a._errors.cells+a._errors.ticket))
        off=e.PairedErrorAdapter(FactorRecencyArm(PROFILE,'owner'),'stream')
        ref=SignalApproxAdapter(FactorRecencyArm(PROFILE,'owner'),'stream')
        for v in basis*3:
            for obj in (off,ref):
                s=sample(obj,v)
                if obj.pending_prediction:consume_prediction(obj,s)
                obj.accept_perception(s)
            self.assertEqual(state(off.arm),state(ref.arm));self.assertEqual(off.pending_prediction,ref.pending_prediction)
        FACTS['E7']='missing comparison creates no error; absent final target censored; disabled path matches previous adapter'

    def test_E8_neutral_continuous_200_and_standard_bound(self):
        # Neutral monotone values, NOT either planned U/V/W/Z phase story.
        values=[vec(.003+i/2048) for i in range(200)]
        with self.assertRaisesRegex(AdapterError,'REPLAY_BOUND'):replay.replay(values,PROFILE,count=200)
        with self.assertRaisesRegex(AdapterError,'REPLAY_BOUND'):replay.replay(values,PROFILE,count=201,bounded_contract=replay.EXTENSION)
        result=replay.replay(values,PROFILE,count=200,bounded_contract=replay.EXTENSION)
        self.assertEqual(len(result['rows']),99);self.assertEqual(result['censored_target'],201)
        self.assertEqual(result['admitted'],list(range(1,201)));self.assertTrue(result['states_identical'])
        self.assertTrue(result['ema_cleared']);self.assertTrue(result['slots_released'])
        for arm in ('K','P'):
            short=replay.replay(values[:20],PROFILE,count=20,arm=arm)
            self.assertEqual(len(short['rows']),9);self.assertTrue(short['states_identical'])
        from tools._s2uc_signal_approx_compare import replay as old
        with self.assertRaisesRegex(ValueError,'REPLAY_BOUND'):old(values,PROFILE)
        FACTS['E8']=dict(neutral_frames=200,rows=99,censored=201,no_reset=True,old_cap_unchanged=True,planned_stories_executed=False)

    def test_E9_actual_additional_memory_including_temporaries(self):
        a=isolated_pending(ec=.1,ep=.2);frames=a.arm._retained_many[0].frames
        a.arm._retained_many.append(RetainedTrace(2,frames));a.arm._candidate=CandidateTrace(3,frames)
        for role,g in [(0,1),(0,2),(1,3)]:
            for offset in (0,1):
                for quality in (0,1):a._errors.update(role,g,offset,quality,.1,.3)
        a._errors.release()
        measurements=[]
        measurements.append(measured(a,lambda:a._errors.prepare(0,1,0,0,1)))
        measurements.append(measured(a,lambda:a.consume_feedback(sample(a,vec(.4)))))
        measurements.append(measured(a,lambda:a._errors.prune(a)))
        # Include JSON/key temporaries in the real receipt-to-choice connection.
        a,basis=seeded()
        for v in basis[:2]:feed(a,v)
        a._errors.release()
        measurements.append(measured(a,a._freeze_choice))
        measurements.append(measured(a,lambda:a.consume_feedback(sample(a,vec(.42)))))
        measurements.append(measured(a,a._terminate))
        # Maximum admitted key/time/id widths, no additional vector allocations.
        large=2**63-1000
        a=e.PairedErrorAdapter(FactorRecencyArm(PROFILE,'o'*96),'s'*96,
            selection_policy='paired_error_ema_v1',start_sample=large-4800,first_ordinal=large)
        receipt=dict(status='PREDICTED_RETAINED',stream=a.stream,owner=a.arm.owner,profile=PROFILE,
            input_indices=[large,large+1],source_intervals=[[large,large+1],[large+2,large+3]],
            read_revision=large,matches=[dict(role='retained',generation=2**64-1,formation='p'+str(large),
                ordinals=[large+i for i in range(4)],offset=1,factors=[1.],match_quality='APPROXIMATE',distance=.125)],
            retrieval=dict(policy='signal_approx_v1',epsilon=1e-6,tau=.125,exact_match_count=0,signal_lost_exact_single=False))
        a.pending_prediction=PredictionReceipt(1,large,'PREDICTED_RETAINED',vec(.7),vec(.2),json.dumps(receipt))
        measurements.append(measured(a,a._freeze_choice))
        measurements.append(measured(a,lambda:a.consume_feedback(sample(a,vec(.4),owner=a.arm.owner,stream=a.stream,end_sample=1))))
        self.assertEqual(measurements[-1]['error'],'TIME_DISCONTINUITY')
        self.assertTrue(all(row['error'] is None for row in measurements[:-1]))
        self.assertEqual(e.CELL.size*12+e.TICKET.size,416)
        for row in measurements:self.assertLessEqual(row['total_additional_upper'],16384)
        FACTS['E9']=dict(packed_bytes=416,measurements=measurements,maximum=max(x['total_additional_upper'] for x in measurements),
            cap=16384,method='deep conservative retained Python size plus tracemalloc peak above pre-call baseline, isolated added operations; includes temporary JSON/key/pack/EMA objects',
            limitation='Python allocation upper measurement for neutral exercised paths; not whole-process RSS/native-stack bound')

    def test_E12_scoped_integer_limits_and_offset_without_successor(self):
        with self.assertRaisesRegex(AdapterError,'EMA_TIME_RANGE'):adapter(start_sample=2**63)
        a=adapter(start_sample=2**63-100)
        with self.assertRaisesRegex(AdapterError,'EMA_TIME_RANGE'):feed(a,vec(.2))
        self.assertTrue(a.closed)
        a,basis=seeded()
        for v in basis[2:]:feed(a,v)
        self.assertIsNone(a.pending_prediction.context_values)
        self.assertFalse(any(a._errors.ticket))
        with self.assertRaisesRegex(AdapterError,'EMA_KEY'):a._errors.prepare(0,1,2,0,13)
        with self.assertRaisesRegex(AdapterError,'EMA_GENERATION'):a._errors.prepare(0,2**64,0,0,13)
        FACTS['E12']='active variant bounds metadata integers; no successor creates no ticket; no generation wrap'

    def test_E10_approximate_key_and_output_identity(self):
        a=adapter(retrieval_policy='signal_approx_v1',epsilon=1e-6,tau=.125)
        basis=[vec(x) for x in (.11,.23,.67,.89)]
        for v in basis*2:feed(a,v)
        feed(a,vec(.111));feed(a,vec(.231))
        p=a.pending_prediction;self.assertIsNotNone(p.context_values)
        self.assertEqual(e.TICKET.unpack(a._errors.ticket)[4],1)
        self.assertIs(a.selected_values,p.persistence_values)
        a.consume_feedback(sample(a,basis[2]))
        self.assertIsNotNone(a._errors.errors(0,1,0,1));self.assertIsNone(a._errors.errors(0,1,0,0))
        FACTS['E10']='real approximate retrieval creates separate APPROXIMATE cell; output alias, no third vector'

    def test_E11_active_memory_identity_and_existing_frame_budget(self):
        from tools._s2uc_signal_approx_compare import ApproxBudgetObserver
        meter=ApproxBudgetObserver();values=[vec(x) for x in (.11,.23,.67,.89)]*4
        a=adapter();ref=SignalApproxAdapter(FactorRecencyArm(PROFILE,'owner'),'stream');choices=[]
        # Existing meter expects fully initialized adapters; observe all input,
        # feedback and termination operations, not constructor attribute writes.
        sys.settrace(meter.trace)
        try:
            for v in values:
                s=sample(a,v)
                if a.pending_prediction:
                    choices.append(a.selected_values is a.pending_prediction.context_values)
                    a.consume_feedback(s);consume_prediction(ref,s)
                a.accept_perception(s);ref.accept_perception(s)
                self.assertEqual(state(a.arm),state(ref.arm))
            a.release_prediction();ref.release_prediction();a.finish_story();ref.finish_story()
        finally:sys.settrace(None)
        self.assertIsNone(a.pending_prediction);self.assertIn(True,choices)
        self.assertLessEqual(meter.frame_peak,18);self.assertLessEqual(meter.output_slots_peak,2)
        self.assertLessEqual(meter.combined_peak,20)
        FACTS['E11']=dict(frames=16,states_identical=True,active_context_selected=True,resources=vars(meter))
