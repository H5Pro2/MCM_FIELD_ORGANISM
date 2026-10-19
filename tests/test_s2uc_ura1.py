"""URA1 focused neutral tests. No research recipe or bootstrap imports."""
import copy,gzip,hashlib,json,unittest
from pathlib import Path
from unittest.mock import patch
from tools._s2uc_ura1 import OriginalRecencyAdapter
from tools._s2uc_ura1_neutral import (pair,blocks,vector,create,common,equal_events,
    run_arm,archive_bytes,verify_archive,ResourceMeter,PROFILE,raw)
from tools._s2uc_ura1_reference import Reference
from tools._s2uc_multi_error import CELL,HEAD,ENTRY,MultiErrorAdapter
from tools._s2uc_pair_context_adapter import PerceptionSample
from tools._s2tu_retained_trace import Frame,RetainedTrace
from tools._s2ub_candidate_confirmation import CandidateTrace

FACTS={}
# Fixed hand-written prefixes, never selected by U/R performance.
D_ITEMS=[(.125,.25),(.125,.25),(.875,.75),(.875,.75),(.125,.25),(.125,.75),(.875,.75),(.875,.25)]*2
LIFECYCLE=[(.125,.25)]*2+[(.125,.75)]*2+[(.125,.25)]*2+[(.875,.25)]*2+[(.875,.75)]*2+[(.125,.75)]*2
def sample(i,v):return PerceptionSample(tuple(v),PROFILE,'comparison','stream',i,(i-1)*4800,i*4800)
def advance(a,values):
    for i,v in enumerate(values,1):
        s=sample(i,v)
        if a.pending_prediction:a.consume_feedback(s)
        a.accept_perception(s)
def prepare_hint(mode='R'):
    a=create(mode);advance(a,blocks([(.125,.25)])+[vector(.125)])
    return a

class URA1Tests(unittest.TestCase):
    def test_N01_unchanged_U_bindings(self):
        root=Path(__file__).resolve().parents[1]
        binding=json.loads((root/'docs/S2UC_UF1_V1_20261005_CODEBINDUNG.json').read_text())
        for name,digest in binding['files'].items():
            self.assertEqual(hashlib.sha256((root/name).read_bytes()).hexdigest(),digest,name)
        self.assertIs(OriginalRecencyAdapter.consume_feedback,MultiErrorAdapter.consume_feedback)
        self.assertIs(OriginalRecencyAdapter._admit,MultiErrorAdapter._admit)
        self.assertIs(OriginalRecencyAdapter._promote,MultiErrorAdapter._promote)
        FACTS['unchanged_bound_files']=len(binding['files'])

    def test_N02_regular_non_equivalence_and_resources(self):
        record=pair(blocks(D_ITEMS))
        self.assertTrue(record['differences'])
        first=record['differences'][0]
        self.assertEqual(first['target'],7)
        self.assertEqual(first['U'],list(vector(.5)))
        self.assertEqual(first['R'],list(vector(.25)))
        FACTS['D_hand_case']=record
        FACTS['non_equivalence']=first

    def test_N03_internal_lifecycle_events(self):
        record=pair(blocks(LIFECYCLE),trace=True)
        events=record['U']['internal']
        self.assertTrue(any(e['method']=='_promote' for e in events))
        self.assertGreater(max(e['state']['stock']['retained_serial'] for e in events),2)
        self.assertTrue(any(e['state']['stock']['candidate_serial']>=3 for e in events))
        # Promotion changes role, while originals and all feedback remain paired.
        FACTS['lifecycle_trace']=record

    def test_N04_error_and_warm_mutation_invariance(self):
        outputs=[];diagnoses=[]
        for before in (None,(0.0,.5),(.5,0.0),(.25,.25)):
            a=prepare_hint()
            try:
                if before is not None:CELL.pack_into(a.bank,0,1,*before,1,0,0,1)
                receipt=a.accept_perception(sample(6,vector(.5)))
                outputs.append(a.selected_values);diagnoses.append(json.loads(receipt.json_text)['hypotheses'][0]['evaluation'])
            finally:a._terminate()
        self.assertEqual(outputs,[vector(.25)]*4)
        self.assertEqual(set(diagnoses),{'COLD','BETTER_THAN_P','WORSE_THAN_P','TIE_P'})
        FACTS['error_mutations']=dict(variants=diagnoses,output_invariant=True)

    def test_N05_recent_original_not_confirmation(self):
        # A older, B newer; another A confirmation must not turn A into newer original.
        values=blocks([(.125,.25)]*2+[(.125,.75)]*2+[(.125,.25)]*2+[(.125,.75)])
        record=pair(values)
        f=record['R']['forecasts'][12] # i=26, next target 27
        self.assertEqual(f['index'],26)
        self.assertEqual(f['output'],list(vector(.75)))
        self.assertEqual(max(x['ordinal'] for x in f['originals']),11)
        # For this same state, invert all shadow preferences; newest still B.
        a=create('R');advance(a,values[:25])
        try:
            for slot in range(6):
                g,ec,ep,role,off,q,valid=CELL.unpack_from(a.bank,slot*32)
                if valid:CELL.pack_into(a.bank,slot*32,g,0.0 if g==1 else .5,.5 if g==1 else 0.0,role,off,q,valid)
            a.accept_perception(sample(26,values[25]));self.assertEqual(a.selected_values,vector(.75))
        finally:a._terminate()
        FACTS['recent_original_after_confirmation']=f

    def test_N06_age_and_tie_order(self):
        # Synthetic metadata edge test; regular non-equivalence is N02, not this.
        def decision(candidate_start,reverse=False):
            a=create('R')
            fs=lambda start,segment,target:tuple(Frame(v,PROFILE,'comparison',segment,start+k) for k,v in enumerate(blocks([(.125,target)])))
            retained=fs(1,'p1',.25);candidate=fs(candidate_start,'p2',.75)
            a.arm._retained_many=[RetainedTrace(1,retained)]
            a.arm._candidate=CandidateTrace(2,candidate)
            a.pair=[Frame(vector(.125),PROFILE,'comparison','p9',33),Frame(vector(.5),PROFILE,'comparison','p9',34)]
            matches=[dict(role=role,generation=g,formation=frames[0].segment,ordinals=[f.ordinal for f in frames],offset=0,factors=[1.0])
                for role,g,frames in [('retained',1,retained),('candidate',2,candidate)]]
            if reverse:matches.reverse()
            try:
                a._receipt('NEUTRAL',[33,34],[[153600,158400],[158400,163200]],matches)
                return a.selected_values
            finally:a._terminate()
        self.assertEqual(decision(5),vector(.75))
        self.assertEqual(decision(1),vector(.25))
        self.assertEqual(decision(1,True),vector(.25))
        hs=[dict(key=(1,2,0),original=3),dict(key=(0,1,0),original=3)]
        self.assertEqual(Reference.newest(hs),(0,1,0))

    def test_N07_no_successor_and_factor_rejection(self):
        a=create('R');advance(a,blocks([(.125,.25)]))
        try:
            # Current pair equals old last two frames: offset=2 has no successor.
            a.consume_feedback(sample(5,vector(.25)));a.accept_perception(sample(5,vector(.25)))
            f=json.loads(a.accept_perception(sample(6,vector(.0625))).json_text)
            self.assertEqual(f['choice'],0);self.assertTrue(any(h['reason']=='NO_SUCCESSOR' for h in f['hypotheses']))
        finally:a._terminate()
        # Full scaled vectors, not V(2x) (the j/4096 offset also scales).
        values=blocks([(.125,.25)])+[tuple(2*x for x in vector(.125)),tuple(2*x for x in vector(.5)),vector(.25),vector(.0625)]
        result=pair(values)
        f=result['R']['forecasts'][2]['receipt']
        self.assertEqual(f['choice'],0);self.assertTrue(any(h['reason']=='FACTOR_UNSPECIFIED' for h in f['hypotheses']))

    def test_N08_injected_couplings_rejected(self):
        for fault,reason in [('stock','REFERENCE_STOCK'),('feedback','REFERENCE_FEEDBACK_CELLS')]:
            with self.subTest(fault=fault),self.assertRaisesRegex(ValueError,reason):run_arm(blocks([(.125,.25)]*2),'R',fault=fault)
        record=pair(blocks([(.125,.25)]*2))
        altered=copy.deepcopy(record['R']['events']);altered[1]['state']['stock']['candidate_serial']+=1
        with self.assertRaisesRegex(ValueError,'PAIRED_STATE_EVENT'):equal_events(record['U']['events'],altered)
        FACTS['coupling_negative_controls']=['stock rejected','feedback rejected','paired event mutation rejected']

    def test_N09_reference_divergence_rejected(self):
        with patch.object(Reference,'newest',staticmethod(lambda hs:None)):
            with self.assertRaisesRegex(ValueError,'REFERENCE_CHOICE'):run_arm(blocks([(.125,.25)]*2),'R')

    def test_N10_error_cleanup_and_resource_paths(self):
        measurements=[]
        stages=['frozen','validated','generation','ec','ep','role','offset','quality','valid','published','promotion_validated','promotion_generation']
        for mode in ('U','R'):
            for stage in stages:
                a=create(mode);meter=ResourceMeter(a);triggered=False
                def checkpoint(self,name,index):
                    if name==stage:raise RuntimeError('INJECTED_'+stage)
                try:
                    with patch.object(type(a),'_checkpoint',checkpoint):
                        for i,value in enumerate(blocks([(.125,.25)]*3),1):
                            s=sample(i,value)
                            if a.pending_prediction:meter.measure_full('feedback',lambda:a.consume_feedback(s),s)
                            meter.measure_full('perception',lambda:a.accept_perception(s),s)
                except RuntimeError as error:
                    self.assertIn('INJECTED_',str(error));triggered=True
                finally:
                    if not a.closed:a._terminate()
                self.assertTrue(triggered,stage)
                self.assertFalse(any(a.bank));self.assertIsNone(a.pending_prediction)
                self.assertFalse(a.arm._retained_many);self.assertIsNone(a.arm._candidate)
                measurements.append(dict(arm=mode,stage=stage,resources=meter.snapshot(),whole=meter.whole))
        FACTS['error_paths']=measurements

    def test_N11_bad_input_ticket_and_boundaries(self):
        for mode in ('U','R'):
            for fault in ('index','dimension','nonfinite','feedback_target'):
                a=create(mode)
                try:
                    with self.assertRaises((ValueError,Exception)):
                        if fault=='feedback_target':
                            advance(a,[vector(.125),vector(.5)])
                            a.consume_feedback(sample(4,vector(.25)))
                        else:
                            v=vector(.125) if fault=='index' else (1.0,)*47 if fault=='dimension' else (float('nan'),)*48
                            a.accept_perception(sample(2 if fault=='index' else 1,v))
                    self.assertTrue(a.closed);self.assertFalse(any(a.bank))
                finally:
                    if not a.closed:a._terminate()
        with self.assertRaisesRegex(ValueError,'NEUTRAL_ONLY_MAX'):pair(blocks(D_ITEMS*3))

    def test_N12_lossless_archive_and_corruption(self):
        record=pair(blocks([(.125,.25)]*2),trace=True)
        blob=archive_bytes(record);digest=hashlib.sha256(blob).hexdigest()
        restored=verify_archive(blob,digest)
        self.assertEqual(raw(record),raw(restored))
        with self.assertRaisesRegex(ValueError,'ARCHIVE_HASH'):verify_archive(blob[:-1]+bytes([blob[-1]^1]),digest)
        altered=copy.deepcopy(record);altered['R']['rows'][0]['error']+=.125
        damaged=archive_bytes(altered)
        with self.assertRaisesRegex(ValueError,'ARCHIVE_ERROR'):verify_archive(damaged,hashlib.sha256(damaged).hexdigest())
        FACTS['archive_check']=dict(compressed=len(blob),expanded=len(gzip.decompress(blob)),lossless=True,hash_corruption_rejected=True,error_corruption_rejected=True)

    def test_N13_selected_only_feedback_coupling(self):
        inherited=MultiErrorAdapter.consume_feedback
        triggered=[]
        def selected_only(a,s):
            count,choice=HEAD.unpack_from(a.bank,192)[2:4]
            chosen=None if not choice else ENTRY.unpack_from(a.bank,208+16*(choice-1))[:3]
            inherited(a,s)
            if count>1:
                for slot in range(6):
                    g,ec,ep,role,off,q,valid=CELL.unpack_from(a.bank,slot*32)
                    if valid and (g,role,off)!=chosen:
                        a._zero(slot*32,(slot+1)*32);triggered.append(s.index)
        values=blocks([(.125,.25)]*2+[(.125,.75)]*2+[(.125,.25)]*2)
        with patch.object(OriginalRecencyAdapter,'consume_feedback',selected_only):
            with self.assertRaisesRegex(ValueError,'REFERENCE_FEEDBACK_CELLS'):run_arm(values,'R')
        self.assertTrue(triggered)
        FACTS['selected_only_feedback_rejected_at']=triggered[0]

    def test_N14_heap_limit_and_terminal_cleanup(self):
        a=create('R')
        with patch('tools._s2uc_ura1_neutral.create',return_value=a),patch('tools._s2uc_multi_observer.owned',return_value=16385):
            with self.assertRaisesRegex(ValueError,'MULTI_PYTHON_BUDGET'):run_arm(blocks([(.125,.25)]),'R')
        self.assertTrue(a.closed);self.assertFalse(any(a.bank))

if __name__=='__main__':unittest.main()
