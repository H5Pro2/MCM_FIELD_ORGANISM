import copy
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace as NS
from unittest.mock import patch
import numpy as np
from tools import _s2oe_detail_closure as c


def binding():return dict(source_path='neutral',source_sha256='a'*64,source_bytes=1,spatial=c.d.SPATIAL)


def controls(_):
    rows=[dict(control=k,arm=a,pixel_sha256=('b' if k=='K0' else 'c')*64,rgb_sha256='d'*64,values_hex=['0x0.0p+0']*288)
          for k in ('K0','K1') for a in ('OVERVIEW','DETAIL')]
    return rows,dict(pixel_hashes=['b'*64,'c'*64],equal=[[True]*288,[True]*288],primary_comparisons=576)


class Child:
    def __init__(self,fail=False):self.closed=False;self.n=0;self.fail=fail
    def view(self,w,arm):
        if self.fail and self.n==3:raise c.d.worker.WorkerError('NEUTRAL_STOP')
        self.n+=1;rgb=np.zeros((1080,1920,3),np.uint8)
        native=dict(format='yuv420p',width=3840,height=2160,colorspace=1,color_range=1,
            planes=[dict(width=x,height=y,sha256='e'*64) for x,y in ((3840,2160),(1920,1080),(1920,1080))])
        pts=1001*((1500+15000*w)//1001)
        return rgb,c.d.evidence('a'*64,w,arm,pts,pts+1001,native,rgb)
    def close(self):self.closed=True
    def status(self):return dict(closed=self.closed,status='CLOSED_COMPLETE' if self.n==20 else 'CLOSED_INCOMPLETE',views_returned=self.n,
        counters=dict(selected_windows=self.n//2,passes=1,video_frames=140,packets=140,audio_frames=0,audio_samples=0,container_read_bytes=1),
        resources=dict(worker_closed=True,job_confirmed_before_media=True,slot_bytes=6240000,queue_capacity=1,
            process_commit_limit=1073741824,job_commit_limit=1073741824,peak_process_commit=1000,peak_job_commit=1000))


class Tests(unittest.TestCase):
    def execute(self,fail=False):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);p=Path(temp.name)/'run';child=Child(fail)
        result=c.execute(binding(),p,1000,opener=lambda *a:child,control_builder=controls,
            receptor=NS(analyze=lambda *a,**k:NS(channel_values=(0.0,)*288)))
        return result,p
    def test_success_once(self):
        record,p=self.execute();self.assertEqual(record['status'],'RECORDING_COMPLETE')
        self.assertTrue((p/'verification.claim').exists())
        with self.assertRaisesRegex(c.d.worker.WorkerError,'OUTPUT_EXISTS'):c.execute(binding(),p,1000)
    def test_partial_stop(self):
        with self.assertRaisesRegex(c.d.worker.WorkerError,'NEUTRAL_STOP'):self.execute(True)
        self.assertFalse(c.d.MAIN_GATE)
    def test_manipulated_binding(self):
        record,_=self.execute();record['views'][0]['spatial']['source_sha256']='f'*64
        with self.assertRaisesRegex(c.d.worker.WorkerError,'SPATIAL_INVALID'):c.verify(record,binding())
    def test_pair_mismatch(self):
        record,_=self.execute();record['views'][1]['spatial']['native']['planes'][0]['sha256']='f'*64
        with self.assertRaisesRegex(c.d.worker.WorkerError,'FRAME_PAIR_INVALID'):c.verify(record,binding())
    def test_incomplete(self):
        record,_=self.execute();record['views'].pop()
        with self.assertRaisesRegex(c.d.worker.WorkerError,'INCOMPLETE'):c.verify(record,binding())
    def test_budget(self):
        p=Path('unused-neutral-closure')
        self.assertIn('TOTAL',c.ledger(p,4194304)['violations'])
        self.assertIn('record.json',c.ledger(p,0,{'record.json':327681})['violations'])
    def test_evaluation_gate(self):
        with self.assertRaisesRegex(c.d.worker.WorkerError,'EVALUATION_FORBIDDEN'):
            c.evaluate({},dict(status='NOT_EVALUABLE',evaluation_allowed=False))
    def test_equal_and_different_regular(self):
        record,_=self.execute();proof=c.verify(record,binding());result=c.evaluate(record,proof)
        self.assertEqual(result['detail_advantage'],'NOT_ESTABLISHED')
        record['controls'][2]['values_hex'][0]='0x1.0000000000000p+0';record['control']['equal'][0][0]=False
        proof=c.verify(record,binding());self.assertFalse(c.evaluate(record,proof)['control']['equal_by_arm'][0])
