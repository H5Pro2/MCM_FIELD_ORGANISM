"""Verify completed neutral evidence and reject self-consistently re-encoded corruptions."""
import json,unittest,hashlib,struct
from pathlib import Path
from unittest.mock import patch
from . import archive,qualify
from .test_contract import event
from tools._s2uc_ura1_delta_fast_decode import Reader
from tools import _s2uc_ura1_delta_encode as codec
from tools._s2uc_ura1_capture_integrity import manifest,full_record_digest

class Evidence(unittest.TestCase):
    def test_13_five_integrations(self):
        count=0
        for mode,arms,reason in [('complete',8,None),('source_failure',0,'SOURCE_CHANGED'),('incomplete_pair',8,'PAIR_INCOMPLETE'),('deadline',4,'WORKER_DEADLINE'),('write_budget',8,'PAIR_INCOMPLETE')]:
            folder=qualify.PREP/('pass01-'+mode);t=json.loads((folder/'terminal.json').read_bytes())
            self.assertEqual(t['arms_created'],arms);self.assertEqual(t['arms_closed'],arms);count+=arms
            self.assertEqual(t['executions']['policy_completed'],arms);self.assertEqual(t['executions']['live_reference_completed'],arms);self.assertEqual(t['executions']['archive_reference_completed'],arms)
            self.assertEqual(t['cleanup'],'CONFIRMED');self.assertTrue(t['worker_ended']);self.assertTrue(t['file_cleanup_confirmed']);self.assertFalse(t['partial_files'])
            self.assertTrue(t['job']['hard_job_limit']);self.assertLess(t['job']['peak_job_committed_bytes'],qualify.LIMITS['job'])
            self.assertEqual(t['completed_cases'],[1,2] if mode=='complete' else [] if mode=='source_failure' else [1])
            self.assertEqual(t['status'],'TERMINAL_COMPLETE' if mode=='complete' else 'TECHNICAL_ABORT')
            if reason:self.assertIn(reason,t['first_failure'])
            else:self.assertIsNone(t['first_failure'])
            if mode!='complete':self.assertFalse((folder/'pair-02-receipt.json').exists())
        self.assertEqual(count,28)
        budget=json.loads((qualify.PREP/'pass01-write_budget/terminal.json').read_bytes())
        self.assertTrue(budget['followup_failures']);self.assertFalse((qualify.PREP/'pass01-write_budget/worker.json').exists())

    def test_14_archive_semantic_corruption(self):
        self.mutations([('reset','ARCHIVE_CELLS'),('output','ARCHIVE_OUTPUT'),('stock','ARCHIVE_STOCK')])

    def test_15_active_ticket_corruption(self):
        self.mutations([('ticket','ARCHIVE_FROZEN_KEY')],suffix='-02')

    def mutations(self,cases,suffix=''):
        base=qualify.PREP/'pass01-complete/case-01.gz'
        for fault,reason in cases:
            reader=Reader(base.read_bytes());root=reader.value(reader.doc['root']);folder=qualify.PREP/('mutation-'+fault+suffix);folder.mkdir(exist_ok=False)
            changed=False
            with codec.store(folder):
                for mode in ('KEEP','RESET'):
                    for name in ('events','internal','forecasts','rows'):
                        seq=codec.collection()
                        for raw in reader.records(root[mode][name]['$sequence']):
                            row=json.loads(raw)
                            if mode=='RESET' and not changed:
                                if fault=='output' and name=='forecasts':row['output'][0]+=.125;changed=True
                                elif name=='events' and row['stage']=='perception:after':
                                    state=row['state']
                                    if fault=='stock' and state['accepted']==36:state['stock']['observation_end']={};changed=True
                                    elif fault=='reset' and state['accepted']==36:
                                        bank=bytearray.fromhex(state['bank']);struct.pack_into('<QddBBBB4x',bank,0,2,0.,0.,0,0,0,1);state['bank']=bank.hex();changed=True
                                    elif fault=='ticket' and bytes.fromhex(state['bank'])[201]>0:
                                        bank=bytearray.fromhex(state['bank']);struct.pack_into('<Q',bank,208,999);state['bank']=bank.hex();changed=True
                            seq.append(row)
                        root[mode][name]=seq
                self.assertTrue(changed);proof=manifest(root);expected=full_record_digest(root);path=folder/'changed.gz';codec.write_archive(root,path,expected)
                counts=dict(started=0,completed=0);original=archive.Reference
                class Counted(original):
                    def __init__(self,*args):counts['started']+=1;super().__init__(*args)
                    def finish(self):super().finish();counts['completed']+=1
                try:
                    with patch.object(archive,'Reference',Counted),self.assertRaisesRegex(ValueError,reason):archive.verify(path.read_bytes(),proof,expected)
                finally:event(event='archive_mutation',fault=fault,**counts,policy=0)

if __name__=='__main__':
    qualify.install_job()
    unittest.main()
