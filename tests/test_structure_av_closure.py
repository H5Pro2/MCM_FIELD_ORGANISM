"""New outer entry and candidate/closure tests, not historical source tests."""
from dataclasses import asdict
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import _structure_av_integration as x

s,b=x.s,x.b


class Tests(unittest.TestCase):
    def binding(self,root):
        ip=Path(os.environ['STRUCTURE_AV_INVENTORY']);inv=s.read_json(ip)
        files={}
        for key,count in (('pcm',19200),('rgb',6220800)):
            path=root/(key+'.bin');path.write_bytes(bytes(count))
            files[key]=(path.relative_to(b.ROOT).as_posix(),s.sha(bytes(count)),count)
        events=[]
        for n in range(1,6):
            kind=b.AV if n<5 else b.V
            p=lambda key:b.Payload(f'closure-neutral-{key}-{n}',*files[key])
            events.append(b.Event(f'closure-neutral-event-{n}',n,kind,**b.expected_times(n,kind),
                                  pcm=p('pcm') if n<5 else None,rgb=p('rgb')))
        m=b.build_manifest('closure-neutral-system',tuple(events),b.digest(inv['ob']))
        common=s.build_common(m,inv,[s.file_reference('sources',ip)])
        cp=root/'common.json';s.prior.save(cp,common)
        # Deliberately negative reference: no assumed stabilization success.
        direct=dict(chains=[dict(states=[dict(slots=[]) for _ in range(4)],
            steps=[dict(source_index=i,frame=dict(values=[0.0]*288)) for i in (3,4,5)])])
        dp=root/'direct.json';s.prior.save(dp,direct)
        vp=root/'direct-proof.json';s.prior.save(vp,dict(status='EVIDENCE_VALID',record_digest=b.digest(direct)))
        qp=root/'qualification.json';s.prior.save(qp,dict(status='QUALIFIED'))
        permit=dict(version=x.VERSION,authorized=True,neutral=True,run_id=m.run_id,
            output=(root/'session').relative_to(b.ROOT).as_posix(),chain=0,source_indices=[3,4,5],
            files={k:x.pin(p) for k,p in dict(common=cp,inventory=ip,direct=dp,direct_proof=vp,qualification=qp).items()})
        ap=root/'admission.json';s.prior.save(ap,permit)
        return ap,permit

    def test_outer_native_entry_negative_reference_and_once(self):
        with tempfile.TemporaryDirectory(dir=b.ROOT/'reports/s2oe') as tmp:
            root=Path(tmp);ap,p=self.binding(root)
            original=Path.open
            def guarded(path,mode='r',*args,**kwargs):
                if 'r' in mode and path.suffix in ('.pcm','.rgb','.bin'):
                    self.assertTrue(path.resolve().is_relative_to(root))
                return original(path,mode,*args,**kwargs)
            with patch.object(Path,'open',guarded):
                x.MAIN_GATE=True
                result=x.run(ap,s.sha(b.canonical(p)),root/'session',neutral=True)
            self.assertEqual(result['status'],'RECORDING_COMPLETE')
            evaluation=s.read_json(root/'session/evaluation.json')
            self.assertTrue(evaluation['cue_readonly'])
            self.assertFalse(evaluation['formations'][3]['slots_equal_direct'])
            self.assertIn('SLOW',evaluation['candidates'])
            self.assertEqual(len(list((root/'session').glob('verification.claim'))),1)
            with self.assertRaises(x.caller.entry.budget.BudgetError):
                x.admission(ap,s.sha(b.canonical(p)),root/'session',True)
            self.assertFalse(x.MAIN_GATE)

    def test_admission_wrong_pin_and_unavailable_reference(self):
        with tempfile.TemporaryDirectory(dir=b.ROOT/'reports/s2oe') as tmp:
            root=Path(tmp);ap,p=self.binding(root)
            with self.assertRaises(x.caller.entry.budget.BudgetError):x.admission(ap,'0'*64,root/'session',True)
            (root/'direct.json').unlink()
            with self.assertRaises(x.caller.entry.budget.BudgetError):x.admission(ap,s.sha(b.canonical(p)),root/'session',True)

    def test_direct_assignment_rejected(self):
        with tempfile.TemporaryDirectory(dir=b.ROOT/'reports/s2oe') as tmp:
            root=Path(tmp);ap,p=self.binding(root);p['source_indices']=[4,3,5]
            changed=root/'wrong.json';s.prior.save(changed,p)
            with self.assertRaises(x.caller.entry.budget.BudgetError):x.admission(changed,s.sha(b.canonical(p)),root/'session',True)

    def test_candidate_visibility_is_not_public_admission(self):
        slot=lambda count:dict(prototype_values=[0.0]*288,support_count=count)
        state=dict(b4_state=dict(entries=[dict(values=[1.0]*48+[0.0]*288)]),
            tspm_state=dict(fast_state=dict(slots=[dict(visual_values=[0.0]*288)]),
                            visual_ppb1_state=dict(slots=[slot(2),slot(3)])))
        result=x.candidates(state,[0.0]*288)
        self.assertEqual(result['SLOW'],dict(available=[1],visible_equal=[1]))
        self.assertEqual(result['B4']['visible_equal'],[0])
        self.assertNotIn('hypothesis',result)

    def test_outer_write_failure_retains_primary(self):
        with tempfile.TemporaryDirectory(dir=b.ROOT/'reports/s2oe') as tmp:
            root=Path(tmp);ap,p=self.binding(root)
            with patch.object(x.caller,'run',side_effect=OSError('neutral disk failure')):
                x.MAIN_GATE=True;result=x.run(ap,s.sha(b.canonical(p)),root/'session',neutral=True)
            self.assertEqual(result['status'],'CLOSURE_NOT_SECURED')
            self.assertEqual(result['primary']['primary_code'],'SESSION_ERROR')
            self.assertFalse(x.MAIN_GATE)
