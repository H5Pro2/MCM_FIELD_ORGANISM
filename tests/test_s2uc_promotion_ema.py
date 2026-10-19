"""Technical fixtures and unrelated neutral admissions; never generate S/W/L."""
import dataclasses
import json
import sys
import tracemalloc
import unittest
from unittest.mock import patch
from tools._s2uc_promotion_ema import PromotionAdapter,POLICY
from tools._s2uc_paired_error_ema import PairedErrorAdapter,CELL,TICKET
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2tu_retained_trace import Frame,RetainedTrace
from tools._s2ub_candidate_confirmation import CandidateTrace
from tools._s2uc_continuation_adapter import PredictionReceipt,consume_prediction
from tools._s2uc_pair_context_adapter import AdapterError
from tools.s2uc_continuous_comparison import state
from tools._s2uc_signal_approx_compare import ApproxBudgetObserver
from tests.test_s2uc_paired_error_ema import vec,sample,feed,addon_owned

PROFILE='b'*64
FACTS={}


def adapter(**kwargs):
    return PromotionAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',
        selection_policy='paired_error_ema_v1',promotion_policy=POLICY,**kwargs)


def fixture(pairs=((0,0,0.,.5),),*,maximum=False):
    """Declared unit prestate, not naturally acquired evidence or a replay."""
    a=adapter();arm=a.arm
    def frames(values,start,segment):
        return tuple(Frame(vec(x),PROFILE,'owner',segment,start+i) for i,x in enumerate(values))
    fs=frames((.11,.23,.67,.89),1,'p1')
    low=2**64-3 if maximum else 3
    candidate_gen=2**64-1 if maximum else 7
    arm._retained_many=[RetainedTrace(low,frames((.13,.29,.61,.87),101,'r1')),
        RetainedTrace(low+1,frames((.17,.37,.71,.97),201,'r2'))]
    arm._retained_generation=low+1
    arm._candidate=CandidateTrace(candidate_gen,fs);arm._candidate_generation=candidate_gen
    for i in range(3):arm.form(Frame(fs[i].values,PROFILE,'owner','p2',i+5))
    for offset,quality,ec,ep in pairs:a._errors.update(1,candidate_gen,offset,quality,ec,ep)
    a._errors.update(0,low,0,0,.25,.5);a._errors.update(0,low+1,0,0,.125,.75)
    return a,Frame(fs[3].values,PROFILE,'owner','p2',8)


def payloads(a,role,g):
    return {(row[4],row[5]):bytes(a._errors.cells[i*32+8:i*32+24])
        for i in range(12) if (row:=CELL.unpack_from(a._errors.cells,i*32))[-1] and (row[3],row[0])==(role,g)}


def measured(a,operation):
    # Entire new call measured, including capture closure, bound methods,
    # metadata and all allocations of the underlying normal admission.
    owned=addon_owned(a)+sys.getsizeof(a.promotion_policy)+sys.getsizeof(a._last_promoted)+sys.getsizeof(a._promotion_busy)
    tracemalloc.start();base=tracemalloc.get_traced_memory()[0]
    try:operation()
    finally:
        _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
    return dict(retained_upper=owned,transient_peak=peak-base,total=owned+max(0,peak-base))


class PromotionTests(unittest.TestCase):
    def check_pair(self,ec,ep,choice):
        a,f=fixture(((0,0,ec,ep),));before=payloads(a,1,7);candidate=a.arm._candidate
        cells_id=id(a._errors.cells);ticket=bytes(a._errors.ticket)
        a._admit(f)
        self.assertIs(a.arm._retained_many[-1].frames,candidate.frames)
        self.assertEqual(payloads(a,0,5),before);self.assertEqual(payloads(a,1,7),{})
        self.assertIsNone(a._errors.errors(0,3,0,0));self.assertEqual(a._errors.errors(0,4,0,0),(.125,.75))
        self.assertEqual(id(a._errors.cells),cells_id);self.assertEqual(bytes(a._errors.ticket),ticket)
        a._errors.prepare(0,5,0,0,1);self.assertEqual(TICKET.unpack(a._errors.ticket)[-2],choice)
        self.assertNotIn('close_segment',vars(a.arm));a._terminate()

    def test_T01_positive(self):self.check_pair(0.,.5,1)
    def test_T02_negative(self):self.check_pair(.5,0.,0)
    def test_T03_tie(self):self.check_pair(.25,.25,0)

    def test_T04_multiple_cells_bitwise_and_sign(self):
        pairs=((0,0,-0.,.5),(0,1,.5,0.),(1,0,.25,.25),(1,1,.75,.125))
        a,f=fixture(pairs);before=payloads(a,1,7);a._admit(f)
        self.assertEqual(payloads(a,0,5),before);self.assertEqual(len(before),4)
        FACTS['T4']=dict(cells=4,negative_zero_bits_preserved=True,no_shadow_bank=True)
        a._terminate()

    def test_T05_empty(self):
        a,f=fixture(());a._admit(f);self.assertEqual(payloads(a,0,5),{});a._terminate()

    def test_T06_conflicts_and_invalid_pair(self):
        for kind in ('target','duplicate','nan'):
            a,f=fixture()
            if kind=='target':a._errors.update(0,5,0,0,0.,.5)
            elif kind=='duplicate':a._errors.cells[3*32:4*32]=a._errors.cells[:32]
            else:CELL.pack_into(a._errors.cells,0,7,float('nan'),.5,1,0,0,1)
            before=bytes(a._errors.cells)
            original=a._validate_promotion
            def validate(*args):
                try:return original(*args)
                finally:self.assertEqual(bytes(a._errors.cells),before)
            with patch.object(a,'_validate_promotion',validate),self.assertRaises(AdapterError):a._admit(f)
            self.assertTrue(a.closed);self.assertFalse(any(a._errors.cells+a._errors.ticket))

    def test_T07_identity_scope_and_regular_reappearance(self):
        for kind in ('copied_tuple','new_frames','scope'):
            a,f=fixture();original=a.arm.close_segment
            def bad(segment):
                result=original(segment);t=a.arm._retained_many[-1]
                if kind=='scope':a.stream='other'
                else:
                    fs=tuple(list(t.frames)) if kind=='copied_tuple' else tuple(dataclasses.replace(x) for x in t.frames)
                    a.arm._retained_many[-1]=RetainedTrace(t.generation,fs)
                return result
            with patch.object(a.arm,'close_segment',bad),self.assertRaisesRegex(AdapterError,'PROMOTION_'):a._admit(f)
            self.assertTrue(a.closed);self.assertFalse(any(a._errors.cells))
        # A live replacement with equal payload is cold; no archive mechanism.
        a,f=fixture();a._admit(f);old=a.arm._retained_many.pop();a._errors.prune(a)
        a.arm._candidate=CandidateTrace(8,tuple(dataclasses.replace(x,ordinal=x.ordinal+1000) for x in old.frames))
        self.assertIsNone(a._errors.errors(1,8,0,0));self.assertIsNone(a._errors.errors(0,5,0,0));a._terminate()

    def test_T08_pending_tickets_and_frozen_alias(self):
        for role,g in ((1,7),(0,4)):
            a,f=fixture();a._errors.prepare(role,g,0,0,1)
            a.pending_prediction=PredictionReceipt(1,0,'FIXTURE',vec(.7),vec(.2),'{}')
            frozen=a.pending_prediction;chosen=a.selected_values;ticket=bytes(a._errors.ticket)
            a._admit(f)
            self.assertIs(a.pending_prediction,frozen);self.assertIs(a.selected_values,chosen)
            self.assertEqual(bytes(a._errors.ticket),ticket)
            transferred=payloads(a,0,5)
            a.consume_feedback(sample(a,vec(.4)))
            self.assertEqual(payloads(a,0,5),transferred)
            if role==0:self.assertNotEqual(a._errors.errors(0,4,0,0),(.125,.75))
            self.assertIsNone(a.pending_prediction);self.assertFalse(any(a._errors.ticket));a._terminate()

    def test_T09_duplicate_event(self):
        a,f=fixture();candidate=a.arm._candidate;previous=tuple(a.arm._retained_many);scope=a._feedback_scope
        a._admit(f);before=bytes(a._errors.cells);a._promotion_busy=True
        result=dict(action='TRACE_PROMOTED',generation=5,candidate_generation=7,evicted=3)
        with self.assertRaisesRegex(AdapterError,'PROMOTION_GENERATION_OR_REPLAY'):
            a._publish_promotion(candidate,previous,result,scope)
        self.assertEqual(bytes(a._errors.cells),before);a._promotion_busy=False;a._terminate()

    def test_T10_interruption_every_publication_boundary_and_read_guard(self):
        pairs=tuple((o,q,float(o)/2,float(q)/2) for o in (0,1) for q in (0,1))
        points=[('validated',-1),('evicted',-1)]+[(s,i) for i in range(4)
            for s in ('before_key','generation_written','after_key')]+[('published',-1)]
        for point in points:
            a,f=fixture(pairs)
            def stop(stage,index):
                with self.assertRaisesRegex(AdapterError,'PROMOTION_PUBLICATION_BUSY'):_=a.selected_values
                with self.assertRaisesRegex(AdapterError,'PROMOTION_PUBLICATION_BUSY'):a.release_prediction()
                if (stage,index)==point:raise KeyboardInterrupt('NEUTRAL_PUBLICATION_INTERRUPT')
            with patch.object(a,'_promotion_checkpoint',stop),self.assertRaises(KeyboardInterrupt):a._admit(f)
            self.assertTrue(a.closed);self.assertFalse(a._promotion_busy)
            self.assertFalse(any(a._errors.cells+a._errors.ticket));self.assertIsNone(a.pending_prediction)
            self.assertNotIn('close_segment',vars(a.arm))
        FACTS['T10']=dict(interruption_points=len(points),includes_between_generation_and_role=True,
            partial_state_never_usable=True,reentrant_read_rejected=True)

    def test_R01_default_and_disabled_path_identical(self):
        for selection in ('disabled','paired_error_ema_v1'):
            a=PromotionAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',selection_policy=selection)
            b=PairedErrorAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',selection_policy=selection)
            for v in [vec(x) for x in (.11,.23,.67,.89)]*3:
                sa=sample(a,v);sb=sample(b,v)
                if a.pending_prediction:
                    self.assertEqual(a.pending_prediction,b.pending_prediction)
                    self.assertEqual(a.selected_values,b.selected_values)
                    if selection=='disabled':consume_prediction(a,sa);consume_prediction(b,sb)
                    else:a.consume_feedback(sa);b.consume_feedback(sb)
                ra=a.accept_perception(sa);rb=b.accept_perception(sb)
                self.assertEqual(ra,rb);self.assertEqual(state(a.arm),state(b.arm))
                if a._errors:self.assertEqual(a._errors.cells,b._errors.cells)
            a.finish_story();b.finish_story()
        off=PromotionAdapter(FactorRecencyArm(PROFILE,'owner'),'stream')
        self.assertIsNone(off._errors);self.assertEqual(off.promotion_policy,'disabled')
        with self.assertRaises(AdapterError):off.promotion_policy=POLICY
        off.finish_story()

    def test_R02_neutral_integration_and_resources(self):
        from tests.test_s2uc_ema_stock import neutral
        values=neutral()  # independent X/Y/Q/Z/W fixture, not planned S/W/L
        a=adapter();b=PairedErrorAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',selection_policy='paired_error_ema_v1')
        meter=ApproxBudgetObserver();promotions=[];receipt_peak=0;extra_frames_peak=0
        original=a._publish_promotion
        def observed(*args):
            before=payloads(a,1,args[0].candidate_generation)
            result=original(*args)
            self.assertEqual(payloads(a,0,args[2]['generation']),before)
            promotions.append(dict(candidate=args[0].candidate_generation,retained=args[2]['generation'],cells=len(before)))
            return result
        def trace(frame,event,arg):
            nonlocal extra_frames_peak
            meter.trace(frame,event,arg)
            if frame.f_code.co_filename.endswith('_s2uc_promotion_ema.py'):
                objects=list(a.arm._forming)+list(a.arm._hints)+list(a.pair)
                for t in a.arm._retained_many:objects.extend(t.frames)
                if a.arm._candidate:objects.extend(a.arm._candidate.frames)
                cursor=frame
                while cursor:
                    if cursor.f_code.co_filename.endswith('_s2uc_promotion_ema.py'):
                        c=cursor.f_locals.get('candidate')
                        if c:objects.extend(c.frames)
                        for t in cursor.f_locals.get('previous',()):objects.extend(t.frames)
                    cursor=cursor.f_back
                extra_frames_peak=max(extra_frames_peak,len({id(x) for x in objects}))
                self.assertLessEqual(extra_frames_peak,18)
            return trace
        with patch.object(a,'_publish_promotion',observed):
            for v in values:
                sa=sample(a,v);sb=sample(b,v)
                if a.pending_prediction:
                    self.assertEqual(a.pending_prediction,b.pending_prediction)
                    a.consume_feedback(sa);b.consume_feedback(sb)
                sys.settrace(trace)
                try:ra=a.accept_perception(sa)
                finally:sys.settrace(None)
                rb=b.accept_perception(sb)
                self.assertEqual(ra,rb);self.assertEqual(state(a.arm),state(b.arm))
                if ra:receipt_peak=max(receipt_peak,len(ra.json_text.encode()))
        a.finish_story();b.finish_story()
        self.assertTrue(promotions);self.assertLessEqual(receipt_peak,16384)
        self.assertLessEqual(meter.output_slots_peak,2)
        FACTS['R2']=dict(neutral_frames=64,promotions=promotions,original_frames_including_transient_refs=extra_frames_peak,
            meter=vars(meter),receipt_bytes=receipt_peak,transient_utf8_upper=2*receipt_peak,
            S_W_L_generated=False,memory_and_receipts_identical=True)

    def test_R03_full_table_maximum_ids_and_transient_memory(self):
        measurements=[]
        for maximum in (False,True):
            pairs=tuple((o,q,.25,.5) for o in (0,1) for q in (0,1))
            a,f=fixture(pairs,maximum=maximum)
            for t in a.arm._retained_many:
                for o in (0,1):
                    for q in (0,1):a._errors.update(0,t.generation,o,q,.25,.5)
            self.assertEqual(sum(CELL.unpack_from(a._errors.cells,i*32)[-1] for i in range(12)),12)
            measurement=measured(a,lambda:a._admit(f));measurements.append(measurement)
            self.assertLessEqual(measurement['total'],16384)
            self.assertEqual(len(a._errors.cells)+len(a._errors.ticket),416);a._terminate()
        a,f=fixture(tuple((o,q,.25,.5) for o in (0,1) for q in (0,1)))
        def fail(stage,index):
            if stage=='generation_written':raise KeyboardInterrupt('MEASURE_FAILURE_CLEANUP')
        def interrupted():
            try:a._admit(f)
            except KeyboardInterrupt:pass
        with patch.object(a,'_promotion_checkpoint',fail):measurements.append(measured(a,interrupted))
        self.assertTrue(a.closed);self.assertFalse(any(a._errors.cells+a._errors.ticket))
        self.assertTrue(all(m['total']<=16384 for m in measurements))
        FACTS['R3']=dict(measurements=measurements,maximum=max(m['total'] for m in measurements),cap=16384,
            whole_admission_including_promotion_temporaries=True,packed_bytes=416,
            limitation='isolated Python allocation measurement, not whole-process RAM')


if __name__=='__main__':unittest.main()
