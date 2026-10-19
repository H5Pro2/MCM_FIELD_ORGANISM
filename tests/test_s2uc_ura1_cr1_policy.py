"""CR1 neutral hand cases: selection, lifecycle, validation and archive controls."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import _s2uc_ura1_cr1_engine as engine
from tools._s2uc_ura1_cr1 import ColdRecencyAdapter
from tools._s2uc_multi_error import MultiErrorAdapter, CELL, HEAD, POLICY
from tools._s2uc_ura1_cr1_reference import Reference
from tools._s2uc_k1_probe import cellmap
from tools._s2uc_pair_context_adapter import PerceptionSample
from tools._s2tu_retained_trace import Frame, RetainedTrace
from tools._s2ub_candidate_confirmation import CandidateTrace


def sample(i,v):
    return PerceptionSample(tuple(v),engine.PROFILE,'comparison','stream',i,(i-1)*4800,i*4800)


def advance(a, values, start=1):
    for i,v in enumerate(values,start):
        s=sample(i,v)
        if a.pending_prediction: a.consume_feedback(s)
        a.accept_perception(s)


def short(values, mode, **kwargs):
    if not 4<=len(values)<=128: raise ValueError('SHORT_ONLY')
    with patch.object(engine,'collection',list), patch.object(engine,'VALIDATE',lambda v: None if v==values else (_ for _ in ()).throw(ValueError('MATERIAL'))):
        return engine.run_arm(values,mode,trace=True,**kwargs)


def synthetic(mode, before, start=5, reverse=False, mutation=None):
    a=engine.create(mode)
    fs=lambda first,segment,target: tuple(Frame(v,engine.PROFILE,'comparison',segment,first+k) for k,v in enumerate(engine.blocks([(.125,target)])))
    retained,candidate=fs(1,'p1',.25),fs(start,'p2',.75)
    a.arm._retained_many=[RetainedTrace(1,retained)]
    a.arm._candidate=CandidateTrace(2,candidate)
    a.pair=[Frame(engine.vector(.125),engine.PROFILE,'comparison','p9',33),Frame(engine.vector(.5),engine.PROFILE,'comparison','p9',34)]
    matches=[dict(role=role,generation=g,formation=frames[0].segment,ordinals=[f.ordinal for f in frames],offset=0,factors=[1.0]) for role,g,frames in [('retained',1,retained),('candidate',2,candidate)]]
    for slot,ec_ep in enumerate(before):
        if ec_ep is not None: CELL.pack_into(a.bank,slot*32,slot+1,*ec_ep,slot,0,0,1)
    if reverse: matches.reverse()
    if mutation: mutation(a,matches)
    try:
        receipt=json.loads(a._receipt('NEUTRAL',[33,34],[[153600,158400],[158400,163200]],matches).json_text)
        hs=[dict(key=({'retained':0,'candidate':1}[m['role']],m['generation'],m['offset']),original=a._frozen[h['ticket']].ordinal,before=None if h['ec'] is None else (h['ec'],h['ep'])) for m,h in zip(matches,receipt['hypotheses']) if h['eligible']]
        chosen,reason=Reference.select(hs,mode)
        selected=None if not receipt['choice'] else hs[receipt['choice']-1]['key']
        if (selected,receipt['decision'])!=(chosen,reason):raise AssertionError('INDEPENDENT_SELECTION')
        return receipt,a.selected_values,engine.common(a),HEAD.unpack_from(a.bank,192)
    finally: a._terminate()


class CR1PolicyTests(unittest.TestCase):
    def test_P10_only_choice_reason_bytes_are_normalized(self):
        a=engine.create('C')
        try:
            base=engine.common(a)
            for i in range(416):
                a.bank[i]^=1
                self.assertEqual(engine.common(a)==base,i in (202,203),i)
                a.bank[i]^=1
        finally:a._terminate()

    def test_P01_inherited_feedback_and_no_new_instance_state(self):
        for name in ('consume_feedback','_admit','_promote','_prune','_terminate','accept_perception'):
            self.assertIs(getattr(ColdRecencyAdapter,name),getattr(MultiErrorAdapter,name))
        u,c=engine.create('U'),engine.create('C')
        try:
            self.assertEqual(set(vars(u)),set(vars(c)))
            self.assertEqual(len(c.bank),416)
        finally:u._terminate();c._terminate()

    def test_P02_all_selection_branches(self):
        cases=[((None,None),'SELECTED_COLD_ORIGINAL_RECENCY',engine.vector(.75)),
               (((.25,.25),None),'NO_ESTIMATED_IMPROVEMENT',engine.vector(.5)),
               ((None,(.5,.25)),'NO_ESTIMATED_IMPROVEMENT',engine.vector(.5)),
               (((0.,.5),None),'SELECTED_BY_ERROR',engine.vector(.25)),
               (((0.,.5),(0.,.5)),'TIED_IMPROVEMENT',engine.vector(.5)),
               (((.125,.5),(0.,.5)),'SELECTED_BY_ERROR',engine.vector(.75)),
               (((.25,.25),(.25,.25)),'NO_ESTIMATED_IMPROVEMENT',engine.vector(.5))]
        for before,reason,output in cases:
            with self.subTest(before=before):
                c=synthetic('C',before);u=synthetic('U',before)
                self.assertEqual(c[0]['decision'],reason);self.assertEqual(c[1],output)
                self.assertEqual(c[2],u[2])
                self.assertEqual(c[3][:3],u[3][:3])
                if any(x is not None for x in before): self.assertEqual(c,u)
                else:self.assertEqual(c[3][-2:],(2,6));self.assertEqual(u[3][-2:],(0,2))

    def test_P03_original_tie_and_match_order(self):
        for reverse in (False,True):
            self.assertEqual(synthetic('C',(None,None),start=1,reverse=reverse)[1],engine.vector(.25))
        # Same ordinal: retained before candidate, then generation, then offset.
        hs=[dict(key=k,original=10,before=None) for k in ((1,1,0),(0,2,0),(0,1,1),(0,1,0))]
        self.assertEqual(Reference.select(hs,'C')[0],(0,1,0))

    def test_P04_cold_feedback_warm_and_lifecycle(self):
        values=engine.blocks([(.125,.25)]*2+[(.125,.75)]*2+[(.125,.25)]*2+[(.875,.25)]*2+[(.875,.75)]*2+[(.125,.75)]*2)
        u,c=(short(values,m) for m in ('U','C'))
        engine.equal_events(u['events'],c['events']);engine.equal_events(u['internal'],c['internal'])
        self.assertEqual(u['forecasts'][2]['receipt']['decision'],'COLD_ONLY')
        self.assertEqual(c['forecasts'][2]['receipt']['decision'],'SELECTED_COLD_ORIGINAL_RECENCY')
        self.assertEqual(c['forecasts'][4]['receipt']['decision'],'SELECTED_BY_ERROR')
        self.assertTrue(c['forecasts'][4]['receipt']['hypotheses'][0]['ec'] is not None)
        self.assertEqual([r['updates'] for r in u['rows']],[r['updates'] for r in c['rows']])
        events=c['internal']
        self.assertTrue(any(e['method']=='_promote' for e in events))
        self.assertGreater(max(e['state']['stock']['retained_serial'] for e in events),2)
        self.assertGreaterEqual(max(e['state']['stock']['candidate_serial'] for e in events),3)
        for uf,cf in zip(u['forecasts'],c['forecasts']):
            if uf['receipt']['decision']!='COLD_ONLY':self.assertEqual(uf,cf)

    def test_P05_empty_factor_offset_and_disabled(self):
        for mutation in (lambda a,m:m.clear(),lambda a,m:[x.update(offset=2) for x in m],lambda a,m:[x.update(factors=[2.0]) for x in m]):
            u=synthetic('U',(None,None),mutation=mutation);c=synthetic('C',(None,None),mutation=mutation)
            self.assertEqual(u,c);self.assertEqual(c[0]['decision'],'NO_ELIGIBLE_CONTEXT')
        u=MultiErrorAdapter(engine.create('U').arm,'stream',multi_policy='disabled')
        c=ColdRecencyAdapter(engine.create('C').arm,'stream',multi_policy='disabled')
        try:
            for i,v in enumerate(engine.blocks([(.125,.25)]*2),1):
                ur=u.accept_perception(sample(i,v));cr=c.accept_perception(sample(i,v))
                self.assertEqual(ur,cr)
                u.release_prediction();c.release_prediction()
        finally:u._terminate();c._terminate()

    def test_P06_invalid_selection_paths_match_U(self):
        mutations=[lambda a,m:m.append(dict(m[0])),lambda a,m:m[0].update(generation=999),
                   lambda a,m:m[0].update(formation='wrong'),lambda a,m:m[0].update(generation=True),
                   lambda a,m:CELL.pack_into(a.bank,0,1,float('nan'),.25,0,0,0,1),
                   lambda a,m:CELL.pack_into(a.bank,0,999,0.,.25,0,0,0,1),
                   lambda a,m:CELL.pack_into(a.bank,0,1,0.,.25,0,0,0,2)]
        for mutation in mutations:
            errors=[]
            for mode in ('U','C'):
                try:synthetic(mode,(None,None),mutation=mutation)
                except Exception as e:errors.append((type(e),str(e)))
            self.assertEqual(len(errors),2);self.assertEqual(*errors)

    def test_P07_coupling_negative_controls(self):
        values=engine.blocks([(.125,.25)]*2)
        for fault,reason in (('stock','REFERENCE_STOCK'),('feedback','REFERENCE_FEEDBACK_CELLS')):
            with self.assertRaisesRegex(ValueError,reason):short(values,'C',fault=fault)
        with patch.object(Reference,'newest',return_value=None):
            with self.assertRaisesRegex(ValueError,'REFERENCE_CHOICE'):short(values,'C')
        # Selected-only feedback is forbidden, including when other tickets are warm.
        inherited=MultiErrorAdapter.consume_feedback
        def corrupted(a,s):
            count,choice=HEAD.unpack_from(a.bank,192)[2:4]
            inherited(a,s)
            if count>1:a._zero(0,192)
        with patch.object(ColdRecencyAdapter,'consume_feedback',corrupted):
            with self.assertRaisesRegex(ValueError,'REFERENCE_FEEDBACK_CELLS'):
                short(engine.blocks([(.125,.25)]*2+[(.125,.75)]*2+[(.125,.25)]*2),'C')

    def test_P08_fault_cleanup_single_receipt(self):
        stages=('frozen','validated','published','promotion_validated','promotion_generation','promotion_role')
        for stage in stages:
            a=engine.create('C');seen=[]
            def checkpoint(name,index):
                seen.append(name)
                if name==stage:raise RuntimeError('INJECTED')
            a._checkpoint=checkpoint
            try:
                with self.assertRaisesRegex(RuntimeError,'INJECTED'):advance(a,engine.blocks([(.125,.25)]*3))
                self.assertTrue(a.closed);self.assertFalse(any(a.bank));self.assertIsNone(a.pending_prediction)
            finally:a._terminate()
        a=engine.create('C');seen=[];a._checkpoint=lambda name,index:seen.append(name)
        try:
            advance(a,engine.blocks([(.125,.25)])+[engine.vector(.125)])
            seen.clear();a.accept_perception(sample(6,engine.vector(.5)))
            self.assertEqual(seen.count('frozen'),1)
        finally:a._terminate()

    def test_P09_archive_semantics_and_corruption(self):
        from tools import _s2uc_ura1_delta_encode as codec
        from tools._s2uc_ura1_capture_integrity import manifest
        from tools._s2uc_ura1_cr1_fused import finish,live_sequences
        from tools._s2uc_ura1_cr1_archive import verify
        values=engine.blocks([(.125,.25)]*2)
        with tempfile.TemporaryDirectory() as directory,codec.store(Path(directory)):
            with patch.object(engine,'VALIDATE',lambda v:None):
                u,c=(engine.run_arm(values,m,trace=True) for m in ('U','C'))
            record=dict(neutral_only=True,source=values,U=u,C=c,paired_equal=True,differences=[],performance_claim=False)
            expected,_=finish(record,live_sequences(record),build=True);proof=manifest(record)
            path=Path(directory)/'neutral.gz';codec.write_archive(record,path,expected)
            self.assertTrue(verify(path.read_bytes(),proof,expected)['cr1_reference_equal'])
            # Re-encode with valid new hashes: semantic corruption still must fail.
            for kind in ('error','cold_output','decision','arm'):
                bad=dict(record)
                bad['C']=dict(c)
                if kind=='arm':bad['C']['mode']='R'
                else:
                    field='rows' if kind=='error' else 'forecasts'
                    seq=codec.collection()
                    for i,row in enumerate(c[field]):
                        row=copy.deepcopy(row)
                        if i==(0 if kind=='error' else 2):
                            if kind=='error':row['error']+=.125
                            elif kind=='cold_output':row['output']=[.99]*48
                            else:row['receipt']['decision']='SELECTED_BY_ORIGINAL_RECENCY'
                        seq.append(row)
                    bad['C'][field]=seq
                # Full digest independent of paired verifier permits malformed semantics.
                from tools._s2uc_ura1_capture_integrity import full_record_digest
                expected_bad=full_record_digest(bad);proof_bad=manifest(bad)
                out=Path(directory)/(kind+'.gz');codec.write_archive(bad,out,expected_bad)
                with self.assertRaises(ValueError):verify(out.read_bytes(),proof_bad,expected_bad)
