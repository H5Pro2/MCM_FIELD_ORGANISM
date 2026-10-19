"""Only new composition checks, using neutral caller files."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import _structure_av_integration as x

s,b=x.s,x.b


class Tests(unittest.TestCase):
    def test_native_five_event_composition(self):
        out=Path(os.environ['STRUCTURE_AV_QUAL']);ip=Path(os.environ['STRUCTURE_AV_INVENTORY']);inv=s.read_json(ip)
        with tempfile.TemporaryDirectory(dir=b.ROOT/'reports/s2oe') as tmp:
            root=Path(tmp);files={}
            for key,data in (('pcm',bytes(19200)),('rgb',bytes(6220800))):
                path=root/(key+'.bin');path.write_bytes(data)
                files[key]=(path.relative_to(b.ROOT).as_posix(),s.sha(data),len(data))
            events=[]
            for n in range(1,6):
                kind=b.AV if n<5 else b.V
                payload=lambda key:b.Payload(f'neutral-str-{key}-{n}',*files[key])
                events.append(b.Event(f'neutral-str-event-{n}',n,kind,**b.expected_times(n,kind),
                    pcm=payload('pcm') if n<5 else None,rgb=payload('rgb')))
            m=b.build_manifest('neutral-structure-system',tuple(events),b.digest(inv['ob']))
            common=s.build_common(m,inv,[s.file_reference('sources',ip)])
            cp=root/'common.json';s.prior.save(cp,common)
            original=Path.open
            def guard(path,mode='r',*args,**kwargs):
                if 'r' in mode and path.suffix in ('.pcm','.rgb','.bin'):
                    self.assertTrue(path.resolve().is_relative_to(root))
                return original(path,mode,*args,**kwargs)
            try:
                with patch.object(Path,'open',guard):
                    x.caller.entry.MAIN_GATE=True
                    result=x.caller.run(cp,s.sha(b.canonical(common)),ip,root/'session',neutral=True)
                self.assertEqual(result['status'],'RECORDING_COMPLETE')
                record,_=s.unpack(s.read_json(root/'session/record.json'),s.read_json(root/'session/session.json'),common)
                proof=s.read_json(root/'session/verification.json')
                self.assertTrue(proof['evaluation_allowed'])
                self.assertEqual(len(record['execution']['rows']),5)
                self.assertEqual(record['execution']['rows'][3]['memory'],record['execution']['rows'][4]['memory'])
                core=record['execution']
                native=lambda key:b.state_wire.decode(core['states'][key])
                reference=dict(chains=[dict(states=[x.visual(native(core['initial']['memory']))]+
                    [x.visual(native(row['memory'])) for row in core['rows'][1:4]],
                    steps=[dict(frame=next(t['frame'] for t in inp['field']['timed_frames']
                        if t['frame']['modality_id']=='visual')) for inp in core['inputs'][1:4]])])
                evaluated=x.assessment(record,proof,reference)
                self.assertEqual([r['ppb_steps'] for r in evaluated['formations']],[0,1,2,3])
                self.assertEqual([r['advanced'] for r in evaluated['formations']],[False,True,True,True])
                self.assertTrue(all(r['slots_equal_direct'] for r in evaluated['formations']))
                self.assertLessEqual(len(b.canonical(evaluated)),3000)
                reference['chains'][0]['states'][3]['slots'][0]['prototype_values'][0]=0.25
                negative=x.assessment(record,proof,reference)
                self.assertFalse(negative['formations'][3]['slots_equal_direct'])
                self.assertEqual(negative['status'],'DESCRIPTIVE_ONLY')
            finally:x.caller.entry.MAIN_GATE=False

    def test_evaluation_gate(self):
        with self.assertRaises(x.caller.entry.budget.BudgetError):x.assessment({},dict(evaluation_allowed=False),{})

    def test_main_gate(self):
        x.MAIN_GATE=False
        with self.assertRaises(x.caller.entry.budget.BudgetError):x.run(None,None,None,None,None)

    def test_no_direct_advance_in_composition(self):
        source=Path(x.__file__).read_text()
        self.assertNotIn('advance_ppb1_bank',source)
        self.assertNotIn('initial_ppb1_bank_state',source)
