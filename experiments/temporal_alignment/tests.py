"""Small hand-written fixtures only: no PCM sources/receptor/NJ experiment."""
import unittest,json,dataclasses
from .core import *
from . import oracle
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import PerceptionSample,PairContextAdapter
from tools.s2uc_continuous_comparison import state

PROFILE='55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e'
def v(x):return tuple(float(x+i*.00001) for i in range(48))
def bank(values=None,ids=(1,2,3,4)):
    return Bank(ids,tuple(values or [v(.1+k*.017) for k in range(31)]),0,('0'*64,)*31)
def sample(i,value):return PerceptionSample(value,PROFILE,'owner','stream',i,(i-1)*4800,i*4800)
def project(payload,start):return v(.11+(start//480%40)*.013)

class Tests(unittest.TestCase):
    def compare(self,h,s,status='ABSTAIN_NO_APPROX_CONTEXT'):
        a=select(h,s,status);b=oracle.decide(h,[dict(values=x[2].values) for x in s],status);self.assertEqual(a,b);return a
    def test_q1_buffer_causality(self):
        b=SampleBuffer()
        with self.assertRaisesRegex(ValueError,'CAUSAL'):b.push(bytes(19200),0,4800,4799)
        self.assertEqual(b.used,0)
    def test_q1_buffer_gap(self):
        b=SampleBuffer();b.push(bytes(19200),0,4800,4800)
        with self.assertRaisesRegex(ValueError,'GAP'):b.push(bytes(19200),9600,14400,14400)
    def test_q1_all_windows(self):
        b=SampleBuffer()
        for i in range(4):b.push(bytes([i])*19200,i*4800,(i+1)*4800,(i+1)*4800)
        self.assertEqual(len(b.data),76800);self.assertEqual(bytes(b.window(30)),bytes([3])*19200)
        self.assertEqual(bytes(b.window(1))[:4*4320],bytes(4*4320))
        self.assertEqual(bytes(b.window(1))[4*4320:],bytes([1])*(4*480))
        with self.assertRaisesRegex(ValueError,'LIMIT'):b.push(bytes(19200),19200,24000,24000)
        with self.assertRaisesRegex(ValueError,'BANK_WINDOW'):b.window(31)
        b.close();self.assertEqual(len(b.data),0)
    def test_q1_bank_27_calls_original_identity(self):
        from tools._s2tu_retained_trace import Frame
        b=SampleBuffer();fs=[];calls=[]
        for i in range(4):
            b.push(bytes(19200),i*4800,(i+1)*4800,(i+1)*4800);fs.append(Frame(v(.1+i),PROFILE,'owner','p1',i+1))
        result=make_bank(b,fs,lambda p,t:(calls.append(t) or v(.2)))
        self.assertEqual(len(calls),27)
        for i in range(4):self.assertIs(result.values[i*10],fs[i].values)
    def test_q3_unique_and_horizon(self):
        b=bank();r=self.compare((b.values[1],b.values[11]),[('retained',1,b)])
        self.assertEqual(r['status'],'PREDICTED_ALIGNMENT');self.assertIs(r['value'],b.values[21]);self.assertEqual(r['matches'],[[0,1,[1.]]])
    def test_q3_no_match(self):self.assertEqual(self.compare((v(9),v(11)),[('retained',1,bank())])['status'],'ABSTAIN_ALIGNMENT_NO_MATCH')
    def test_q3_same_trace_many_positions(self):
        xs=list(bank().values);xs[2]=xs[1];xs[12]=xs[11];b=bank(xs)
        self.assertEqual(self.compare((xs[1],xs[11]),[('retained',1,b)])['status'],'ABSTAIN_ALIGNMENT_AMBIGUOUS')
    def test_q3_competing_traces(self):
        b=bank();other=bank(ids=(5,6,7,8))
        self.assertEqual(self.compare((b.values[1],b.values[11]),[('retained',1,b),('candidate',2,other)])['status'],'ABSTAIN_TRACE_AMBIGUOUS')
    def test_q3_no_successor(self):
        b=bank();self.assertEqual(self.compare((b.values[11],b.values[21]),[('retained',1,b)])['status'],'ABSTAIN_ALIGNMENT_NO_SUCCESSOR')
    def test_q3_factor(self):
        b=bank();hint=tuple(tuple(2*x for x in b.values[k]) for k in (1,11))
        self.assertEqual(self.compare(hint,[('retained',1,b)])['status'],'FACTOR_CONTINUATION_NOT_SPECIFIED')
    def test_q3_signal(self):
        z=(0.,)*48;self.assertEqual(self.compare((z,z),[('retained',1,bank())])['status'],'ABSTAIN_ALIGNMENT_LOW_SIGNAL')
    def test_q3_eligibility_only(self):
        b=bank()
        for status in ('CONFIRMED_RETAINED_MATCH','ABSTAIN_APPROX_AMBIGUOUS','ABSTAIN_LOW_SIGNAL','ABSTAIN_APPROX_NUMERIC','ABSTAIN_NO_SUCCESSOR'):
            self.assertEqual(self.compare((b.values[1],b.values[11]),[('retained',1,b)],status)['status'],'NOT_ELIGIBLE')
    def test_q4_63_matches(self):
        b=bank([v(.2)]*31);r=self.compare((v(.2),v(.2)),[('retained',1,b),('retained',2,bank(b.values,(5,6,7,8))),('candidate',3,bank(b.values,(9,10,11,12)))])
        self.assertEqual(len(r['matches']),63);self.assertLess(len(encoded(r)),16384)
        with self.assertRaisesRegex(ValueError,'SOURCE_LIMIT'):select((v(.2),v(.2)),[('retained',i,b) for i in range(4)],'ABSTAIN_NO_APPROX_CONTEXT')
    def test_q4_receipt_limit(self):
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        try:
            with self.assertRaisesRegex(ValueError,'RECEIPT_LIMIT'):a.budget(receipt='x'*16385)
            with self.assertRaisesRegex(ValueError,'RECEIPT_LIMIT'):a.budget(receipt='x'*16000,old_receipt='x'*17000)
        finally:a._terminate()
    def test_q4_vector_limit(self):
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        try:
            a.banks={tuple(range(i,i+4)):bank(ids=tuple(range(i,i+4))) for i in (1,5,9,13)}
            a.budget();self.assertEqual(a.peaks['vector_slots'],124)
            with self.assertRaisesRegex(ValueError,'BANK_COUNT'):a.budget(building=bank(ids=(17,18,19,20)))
        finally:a._terminate()
    def test_q2_lifecycle_reference_and_original_promotion(self):
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        ref=PairContextAdapter(FactorRecencyArm(PROFILE,'owner'),'stream');original=None
        try:
            for i in range(1,9):
                if a.pending_prediction:a.release_prediction()
                s=sample(i,v(.1+((i-1)%4)*.1));a.accept_audio(s,bytes(19200),s.end_sample);ref.accept_perception(s)
                self.assertEqual(state(a.arm),state(ref.arm))
                if i==4:original=a.banks[(1,2,3,4)]
            self.assertIs(a.banks[(1,2,3,4)],original);self.assertEqual(a.arm.inventory,(1,));self.assertEqual(a.buffer.used,0)
        finally:a.finish_story();ref.finish_story()
        self.assertFalse(a.banks);self.assertTrue(a.buffer.closed);self.assertFalse(a.pending_prediction)
    def test_q2_replacement_eviction_cleanup(self):
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        blocks=[0,1,1,2,2,3,3]
        try:
            for i in range(1,len(blocks)*4+1):
                if a.pending_prediction:a.release_prediction()
                s=sample(i,v(.1+blocks[(i-1)//4]+((i-1)%4)*.1));a.accept_audio(s,bytes(19200),s.end_sample)
                self.assertEqual(set(a.banks),{tuple(f.ordinal for f in fs) for _,_,fs in a._sources()})
            self.assertNotIn((1,2,3,4),a.banks);self.assertNotIn((5,6,7,8),a.banks);self.assertEqual(len(a.banks),2)
        finally:a.finish_story()
        self.assertFalse(a.banks)
    def test_q2_future_target_rejected_cleanup(self):
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        for i in (1,2):a.accept_audio(sample(i,v(.1*i)),bytes(19200),i*4800)
        self.assertEqual(a.pending_prediction.target_index,3)
        with self.assertRaisesRegex(ValueError,'TARGET_NOT_RELEASED'):a.accept_audio(sample(3,v(.3)),bytes(19200),14400)
        self.assertTrue(a.closed);self.assertFalse(a.banks);self.assertEqual(len(a.buffer.data),0)
    def test_q2_actual_alignment_receipt(self):
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        try:
            for i in range(1,9):
                if a.pending_prediction:a.release_prediction()
                a.accept_audio(sample(i,v(.1+((i-1)%4)*.1)),bytes(19200),i*4800)
            b=a.banks[(1,2,3,4)]
            for i,k in ((9,1),(10,11)):
                if a.pending_prediction:a.release_prediction()
                a.accept_audio(sample(i,b.values[k]),bytes(19200),i*4800)
            self.assertEqual(a.pending_prediction.target_index,11)
            base=json.loads(a.base_forecast.provenance_json)['status'];expected=oracle.decide((b.values[1],b.values[11]),[dict(values=b.values)],base)
            self.assertEqual(base,'ABSTAIN_NO_APPROX_CONTEXT');self.assertEqual(a.pending_prediction.status,expected['status'])
            self.assertEqual(a.pending_prediction.context_values,expected['value']);self.assertEqual(a.pending_prediction.status,'PREDICTED_ALIGNMENT')
        finally:a._terminate()
    def test_q5_incomplete_discards_buffer(self):
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        a.accept_audio(sample(1,v(.1)),bytes(19200),4800);a.finish_story()
        self.assertTrue(a.buffer.closed);self.assertFalse(a.banks)

class ExtraTests(unittest.TestCase):
    def test_q4_128_slots(self):
        from tools._s2tu_retained_trace import Frame
        from tools._s2uc_continuation_adapter import PredictionReceipt
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        try:
            a.banks={tuple(range(i,i+4)):bank(ids=tuple(range(i,i+4))) for i in (1,5,9,13)}
            a.pair=[Frame(v(8),PROFILE,'owner','p5',17),Frame(v(9),PROFILE,'owner','p5',18)]
            a.pending_prediction=PredictionReceipt(19,1,'TEST',v(10),a.pair[1].values,'{}')
            a.budget();self.assertEqual(a.peaks['vector_slots'],128)
            a.arm._forming.append(Frame(v(11),PROFILE,'owner','p5',19))
            with self.assertRaisesRegex(ValueError,'VECTOR_SLOT_LIMIT'):a.budget()
        finally:a._terminate()
    def test_q4_provenance_rejection(self):
        from unittest.mock import patch
        a=TemporalAdapter(FactorRecencyArm(PROFILE,'owner'),'stream',project=project)
        try:
            with patch('experiments.temporal_alignment.core.encoded',return_value=bytes(65537)):
                with self.assertRaisesRegex(ValueError,'PROVENANCE_LIMIT'):a.budget()
        finally:a._terminate()
    def test_q5_bounds_and_formal_gate(self):
        from .entry import formal_gate,timeout,export_check
        from . import full
        export_check(16777215,1)
        with self.assertRaisesRegex(ValueError,'EXPORT'):export_check(16777216,1)
        self.assertEqual(timeout(301,0,100),'TOTAL_TIMEOUT');self.assertEqual(timeout(241,0,0),'WORKER_TIMEOUT')
        with self.assertRaisesRegex(ValueError,'PRIOR_CONSUMPTION_UNPROVEN'):formal_gate()
        with self.assertRaisesRegex(ValueError,'PRIOR_CONSUMPTION_UNPROVEN'):full.run(__import__('pathlib').Path('not-created'))
    def test_q5_bank_integrity(self):
        b=bank()
        with self.assertRaisesRegex(ValueError,'BANK_TIME'):Bank(b.originals,b.values,1,b.digests)
        with self.assertRaisesRegex(ValueError,'BANK_ORDINALS'):Bank((1,2,3,5),b.values,0,b.digests)
        with self.assertRaisesRegex(ValueError,'BANK_DIGESTS'):Bank(b.originals,b.values,0,('z'*64,)*31)
        with self.assertRaisesRegex(ValueError,'VECTOR'):Bank(b.originals,((float('nan'),)*48,)+b.values[1:],0,b.digests)
    def test_q2_promotion_after_validation_change(self):
        Tests('test_q2_lifecycle_reference_and_original_promotion').test_q2_lifecycle_reference_and_original_promotion()
    def test_q3_alignment_after_validation_change(self):
        Tests('test_q2_actual_alignment_receipt').test_q2_actual_alignment_receipt()

PROJECTOR_MEASUREMENTS={}
class ProjectorTests(unittest.TestCase):
    def test_q1_q4_single_artificial_zero_window(self):
        from .projector import Projector
        p=Projector();out=p(bytes(19200),0)
        self.assertEqual(out,(0.,)*48);self.assertEqual((p.calls,p.nj_calls),(1,1));self.assertLessEqual(p.peak_workspace,16*1048576)
        PROJECTOR_MEASUREMENTS.update(receptor_calls=p.calls,nj_calls=p.nj_calls,traced_workspace_bytes=p.peak_workspace)
        # Counter admission must reject before a second real call.
        p.calls=390
        with self.assertRaisesRegex(ValueError,'PROJECTION_SCOPE'):p(bytes(19200),0)

def run(extra=False,projector=False):
    import io
    log=io.StringIO();result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProjectorTests if projector else ExtraTests if extra else Tests))
    return dict(tests=result.testsRun,passed=result.wasSuccessful(),failures=len(result.failures),errors=len(result.errors),log=log.getvalue(),receptor_calls=PROJECTOR_MEASUREMENTS.get('receptor_calls',0),nj_calls=PROJECTOR_MEASUREMENTS.get('nj_calls',0),formal_size_runs=0,projector_measurements=PROJECTOR_MEASUREMENTS)
