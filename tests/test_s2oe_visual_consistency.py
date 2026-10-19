"""Neutral diagnostic connectors only; never opens the selected media."""
from fractions import Fraction
from types import SimpleNamespace as NS
import inspect
import unittest
from unittest.mock import patch
import numpy as np
from tools import _s2oe_visual_consistency as v


class Frame:
    def __init__(self, pts):
        self.pts, self.time_base = pts, Fraction(1,30000)
        self.width,self.height = 3840,2160
        self.colorspace,self.color_range = 1,1
        self.calls=[]

    def reformat(self, **kwargs):
        self.calls.append(kwargs)
        return NS(to_ndarray=lambda: np.full((1080,1920,3),17,dtype=np.uint8))


def fixture(points):
    d = object.__new__(v.VideoDecoder)
    d.source=NS(video_time_base=(1,30000),video_size=(3840,2160))
    d.vi=iter([Frame(x) for x in points])
    d.video_next=d.video_last_time=d.rgb=None
    d.progress=lambda *args: None
    d.bind_native=lambda frame: dict(pts=frame.pts)
    return d


class Qualification(unittest.TestCase):
    def test_01_selection_both_points(self):
        for w,(p,n) in v.POINTS.items():
            with self.subTest(window=w):
                d=fixture([0,p,n])
                d._select_video(Fraction(w,2)+Fraction(1,20))
                self.assertEqual((d.frame_pts,d.next_pts),(p,n))

    def test_02_shared_routine(self):
        self.assertIs(v.VideoDecoder._select_video,v.media.Decoder._select_video)
        self.assertIn('self._select_video(center)',inspect.getsource(v.media.Decoder.select))
        self.assertIn('self._select_audio(window)',inspect.getsource(v.media.Decoder.select))

    def test_03_independent_states(self):
        a,b=fixture([0,31031,32032]),fixture([0,31031,32032])
        a._select_video(Fraction(21,20))
        self.assertIsNone(b.rgb)
        b._select_video(Fraction(21,20))
        self.assertIsNot(a.rgb,b.rgb)
        self.assertEqual(a.native,b.native)

    def test_04_converter(self):
        d=fixture([]); f=Frame(31031)
        d.vi=iter([f,Frame(32032)])
        d._select_video(Fraction(21,20))
        self.assertEqual(f.calls,[dict(width=1920,height=1080,format='rgb24',
            interpolation='AREA',src_colorspace=1,dst_colorspace=1,
            src_color_range='MPEG',dst_color_range='JPEG')])

    def test_05_bad_time(self):
        d=fixture([]); f=Frame(31031); f.time_base=Fraction(1,30)
        d.vi=iter([f])
        with self.assertRaises(v.worker.WorkerError) as cm:
            d._select_video(Fraction(21,20))
        self.assertEqual(cm.exception.code,'FRAME_TIME_BASE_INVALID')

    def test_06_missing_frame(self):
        with self.assertRaises(v.worker.WorkerError) as cm:
            fixture([])._select_video(Fraction(21,20))
        self.assertEqual(cm.exception.code,'FRAME_COVERAGE_MISSING')

    def test_07_mask(self):
        rgb=np.full((1080,1920,3),17,dtype=np.uint8); rgb.flags.writeable=False
        masked=v.occlude(rgb)
        cells=masked.reshape(8,135,12,160,3)
        for i in range(288):
            cell,ch=divmod(i,3); row,col=divmod(cell,12)
            self.assertTrue(np.all(cells[row,:,col,:,ch] == (17 if i<32 else 0)))
        self.assertTrue(np.all(rgb==17))

    def test_08_equal_and_different(self):
        a=(0.5,)*288; b=(0.6,)+a[1:]
        self.assertTrue(all(x['equal'] for x in v.compare(a,a,tuple(range(288)))))
        self.assertFalse(v.compare(a,b,tuple(range(32)))[0]['equal'])
        frame=dict(version=v.VERSION,window=2,pts=31031,next_pts=32032,
                   time_base=[1,30000],native={'neutral':1},rgb_sha256='a'*64)
        self.assertTrue(v.compare_frames(frame,frame)['rgb_equal'])
        self.assertFalse(v.compare_frames(frame,dict(frame,rgb_sha256='b'*64))['rgb_equal'])
        with self.assertRaises(v.worker.WorkerError) as cm:
            v.compare_frames(frame,dict(frame,pts=33000))
        self.assertEqual(cm.exception.code,'FRAME_EVIDENCE_INVALID')

    def test_09_value_errors(self):
        for bad in ((float('nan'),)*288,(1.1,)*288,(0.5,)*287):
            with self.subTest(bad=repr(bad[:1])):
                with self.assertRaises(v.worker.WorkerError) as cm: v.bind_values(bad)
                self.assertEqual(cm.exception.code,'VALUES_INVALID')

    def test_10_profile_and_gate(self):
        self.assertEqual(v.uhd.CONFIG['process_commit_bytes'],1073741824)
        self.assertEqual(v.uhd.CONFIG['job_commit_bytes'],1073741824)
        with self.assertRaises(v.worker.WorkerError) as cm: v.open_video(None,None,'neutral')
        self.assertEqual(cm.exception.code,'DIAGNOSTIC_GATE_CLOSED')
        with patch.object(v,'MAIN_GATE',True),patch.object(v.uhd,'validate') as check, \
             patch.object(v,'VideoWorker') as create:
            v.open_video('source','profile','neutral-bound')
            check.assert_called_once_with('profile','source','neutral-bound')
            create.assert_called_once_with('source',diagnostic_arm='COMMIT_1024')

    def test_11_native_padding(self):
        class Plane(bytearray):
            width=2; height=2; line_size=3
        f=NS(format=NS(name='yuv420p'),width=2,height=2,colorspace=1,color_range=1)
        f.planes=[Plane([1,2,99,3,4,99]) for _ in range(3)]
        a=v.native_binding(f)
        f.planes=[Plane([1,2,88,3,4,88]) for _ in range(3)]
        self.assertEqual(a,v.native_binding(f))
        f.format.name='unknown'
        with self.assertRaises(v.worker.WorkerError) as cm: v.native_binding(f)
        self.assertEqual(cm.exception.code,'NATIVE_FORMAT_UNSUPPORTED')

    def test_12_closed_and_bad_point(self):
        for w in (True,3,2):
            d=object.__new__(v.VideoDecoder); d.repeat=0; d.closed=True
            with self.subTest(window=w):
                with self.assertRaises(v.worker.WorkerError) as cm: d.video_point(w)
                self.assertEqual(cm.exception.code,'VIDEO_POINT_INVALID')
