from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch
import numpy as np
from tools import _s2oe_fixed_detail as d
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor

OUT=Path(os.environ['DETAIL_QUAL_OUT'])


@dataclass(frozen=True)
class Source:
    path:str='neutral-detail-flat-128'
    sha256:str='a'*64
    size:int=0
    video_time_base:tuple=(1,30000)
    audio_time_base:tuple=(1,48000)
    frame_rate:tuple=(30000,1001)
    video_size:tuple=(3840,2160)


class Frame:
    width=3840;height=2160;colorspace=1;color_range=1
    def __init__(self,pts=1001):self.calls=[];self.pts=pts;self.time_base=Fraction(1,30000)
    def reformat(self,**kw):
        self.calls.append(kw)
        return NS(to_ndarray=lambda:np.full((kw['height'],kw['width'],3),17,dtype=np.uint8))


def fixture():
    x=object.__new__(d.DetailDecoder)
    x.source=Source();x.closed=False;x.request_index=0;x.pending=x.rgb=x.video_next=None
    x.counters={'selected_windows':0};x.video_last_time=None;x.vi=iter([Frame(0),Frame(1001),Frame(2002)])
    x.begin_video=lambda:None
    return x


class Tests(unittest.TestCase):
    def test_01_coordinates(self):
        self.assertEqual(d.rectangle([960,540,1920,1080]),d.RECT)
        for rect in ((True,540,1920,1080),(-1,540,1920,1080),(960,540,1921,1080),(0,0,3841,2160)):
            with self.subTest(rect=rect),self.assertRaises(d.worker.WorkerError):d.rectangle(rect)
    def test_02_pixel_mapping(self):
        image=np.zeros((2160,3840,3),np.uint8);image[540,960]=[1,2,3];image[1619,2879]=[4,5,6]
        crop=d.crop(image);self.assertEqual(crop[0,0].tolist(),[1,2,3]);self.assertEqual(crop[-1,-1].tolist(),[4,5,6])
        crop[0,0]=0;self.assertEqual(image[540,960].tolist(),[1,2,3])
    def test_03_conversion_order_and_legacy(self):
        f=Frame();a,b=d.project(f)
        self.assertEqual(f.calls,[dict(width=3840,height=2160,**d.COLOR),dict(width=1920,height=1080,**d.COLOR)])
        legacy=Frame().reformat(width=1920,height=1080,format='rgb24',interpolation='AREA',src_colorspace=1,
            dst_colorspace=1,src_color_range='MPEG',dst_color_range='JPEG').to_ndarray()
        self.assertTrue(np.array_equal(a,legacy));self.assertEqual(b.shape,(1080,1920,3))
    def test_04_native_selection(self):
        x=fixture()
        x.vi=iter(Frame(n*1001) for n in range(150))
        with patch.object(d.old,'native_binding',return_value={'neutral':True}):
            for window in range(10):
                a,p=x.video_point(2*window);b,q=x.video_point(2*window+1)
                self.assertEqual(p['pts'],q['pts']);d.validate_evidence(p,window,'OVERVIEW',Source().sha256)
        self.assertEqual(x.counters['selected_windows'],10);self.assertIsNone(x.pending)
    def test_05_order_and_limits(self):
        x=fixture()
        for request,budget in ((1,400),(20,400),(0,401)):
            with self.subTest(request=request,budget=budget),self.assertRaises(d.worker.WorkerError):x.video_point(request,budget)
        self.assertEqual(x.request_index,0)
    def test_06_missing_frame(self):
        x=fixture();x.vi=iter([])
        with self.assertRaisesRegex(d.worker.WorkerError,'FRAME_COVERAGE_MISSING'):x.select_native(0)
    def test_07_bad_time(self):
        x=fixture();f=Frame();f.time_base=Fraction(1,30);x.vi=iter([f])
        with self.assertRaisesRegex(d.worker.WorkerError,'FRAME_TIME_BASE_INVALID'):x.select_native(0)
    def test_08_spatial_evidence(self):
        rgb=np.zeros((1080,1920,3),np.uint8)
        p=d.evidence('a'*64,0,'DETAIL',1001,2002,{'neutral':True},rgb)
        d.validate_evidence(p,0,'DETAIL','a'*64)
        p['rectangle'][0]=0
        with self.assertRaisesRegex(d.worker.WorkerError,'SPATIAL_BINDING_INVALID'):d.validate_evidence(p,0,'DETAIL','a'*64)
    def test_09_gate_closed(self):
        with self.assertRaisesRegex(d.worker.WorkerError,'DETAIL_GATE_CLOSED'):d.start(Source(),{})
    def test_10_real_native_worker_and_close(self):
        class Worker(d.DetailWorker):
            @staticmethod
            def _launch(args,**kw):return d.worker.WorkerDecoder._launch([args[0],'-m','tests.s2oe_detail_worker'],**kw)
        w=Worker(Source(),diagnostic_arm='COMMIT_1024');w.source_hash=Source().sha256
        try:
            a,p=w.view(0,'OVERVIEW');b,q=w.view(0,'DETAIL')
            self.assertEqual(p['native'],q['native']);self.assertEqual(p['pts'],q['pts'])
            self.assertFalse(a.flags.writeable);self.assertFalse(b.flags.writeable)
            status=w.status();status['counters']['passes']=900
            self.assertEqual(w.counters['passes'],1)
            receptor=LocalChannelGridReceptor()
            va=receptor.analyze(a,frame_index=0).channel_values;vb=receptor.analyze(b,frame_index=0).channel_values
            with (OUT/'native-views.json').open('xb') as f:f.write(d.raw([d.pack_view(p,va),d.pack_view(q,vb)]))
        finally:w.close()
        w.close();self.assertTrue(w.resources['worker_closed']);self.assertIsNone(w.pending if hasattr(w,'pending') else None)
        self.assertEqual(w.status()['status'],'CLOSED_INCOMPLETE')
        with (OUT/'native-resources.json').open('xb') as f:f.write(d.raw(w.status()))
        with self.assertRaises(d.worker.WorkerError):w.view(0,'DETAIL')
    def test_11_information_loss_control(self):
        av=d.media.load_av();pairs=[];pixels=[];receptor=LocalChannelGridReceptor()
        for reverse in (False,True):
            row=((np.arange(3840)//80)%2).astype(np.uint8)*255
            if reverse:row=255-row
            rgb=np.broadcast_to(row[None,:,None],(2160,3840,3)).copy();pixels.append(hashlib.sha256(rgb).hexdigest())
            f=av.VideoFrame.from_ndarray(rgb,format='rgb24');del rgb
            f=f.reformat(format='yuv420p',src_colorspace=1,dst_colorspace=1,src_color_range='JPEG',dst_color_range='MPEG')
            f.colorspace=f.color_range=1
            a,b=d.project(f)
            pairs.append([[v.hex() for v in receptor.analyze(x,frame_index=0).channel_values] for x in (a,b)])
        result=dict(pixel_hashes=pixels,pixels_different=pixels[0]!=pixels[1],
            receptor_equal=[pairs[0][i]==pairs[1][i] for i in (0,1)],values=pairs,
            interpretation='diagnostic collision only; not general preservation')
        with (OUT/'information-control.json').open('xb') as f:f.write(d.raw(result))
        self.assertNotEqual(pixels[0],pixels[1])
        # Equality/non-equality is a diagnostic result, not a technical success gate.
    def test_12_complete_envelope(self):
        rgb=np.zeros((1080,1920,3),np.uint8)
        p=d.evidence('f'*64,9,'DETAIL',136136,137137,{'planes':[{'sha256':'f'*64}]*3},rgb)
        views=[d.pack_view(p,(float.fromhex('0x1.fffffffffffffp-1'),)*288) for _ in range(24)]
        complete=d.pack_total(views,{'resource':'x'*8000},{'control':'x'*8000})
        with (OUT/'complete-envelope.json').open('xb') as f:f.write(d.raw(complete))
        self.assertLessEqual(len(d.raw(complete)),327680)
    def test_13_envelope_overflow(self):
        with self.assertRaisesRegex(d.worker.WorkerError,'TOTAL_VIEWS_LIMIT'):d.pack_total([{}]*25,{}, {})
        with self.assertRaisesRegex(d.worker.WorkerError,'SUPPLEMENT_LIMIT'):d.pack_total([],{'x':'x'*8192},{})
    def test_14_profile_rejection(self):
        f=Frame();f.colorspace=2
        with self.assertRaisesRegex(d.worker.WorkerError,'NATIVE_PROFILE_INVALID'):d.project(f)
    def test_15_legacy_selection_equal(self):
        x=fixture();legacy=fixture();legacy.progress=lambda *args:None
        with patch.object(d.old,'native_binding',return_value={'neutral':True}):x.select_native(0)
        d.media.Decoder._select_video(legacy,Fraction(1,20))
        self.assertEqual((x.frame_pts,x.next_pts),(legacy.frame_pts,legacy.next_pts));self.assertTrue(np.array_equal(x.rgb,legacy.rgb))
    def test_16_start_binding_and_status(self):
        with patch.object(d,'MAIN_GATE',True):
            with self.assertRaisesRegex(d.worker.WorkerError,'DETAIL_CODE_MISSING'):
                d.start(Source(),dict(spatial=d.SPATIAL,source_sha256=Source().sha256))


if __name__=='__main__':unittest.main(verbosity=2)
