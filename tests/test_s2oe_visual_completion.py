"""New worker, envelope and joint-counter coverage only."""
from dataclasses import dataclass, replace
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from tools import _s2oe_visual_completion as c
v=c.v
OUT=Path(os.environ['VISUAL_COMPLETION_OUT'])


@dataclass(frozen=True)
class Source:
    path: str
    sha256: str
    size: int
    video_stream: int=0
    audio_stream: int=1
    video_time_base: tuple=(1,30000)
    audio_time_base: tuple=(1,48000)
    frame_rate: tuple=(30000,1001)
    video_size: tuple=(3840,2160)


def save(name,data):
    with (OUT/name).open('xb') as f: f.write(c.canonical(data))


def neutral_video():
    path=OUT/'neutral.mp4'
    av=v.media.load_av()
    with path.open('xb') as file:
        with av.open(file,mode='w',format='mp4') as container:
            stream=container.add_stream('libx264',rate=Fraction(30000,1001))
            stream.width,stream.height=3840,2160
            stream.pix_fmt='yuv420p'
            stream.time_base=Fraction(1,30000)
            stream.codec_context.thread_count=1
            stream.codec_context.colorspace=1
            stream.codec_context.color_range=1
            stream.options={'preset':'ultrafast','tune':'zerolatency','crf':'30'}
            frame=av.VideoFrame(3840,2160,'yuv420p')
            frame.colorspace=frame.color_range=1
            for plane in frame.planes: plane.update(bytes([128])*plane.buffer_size)
            for i in range(124):
                frame.pts=i*1001
                frame.time_base=Fraction(1,30000)
                for packet in stream.encode(frame): container.mux(packet)
            for packet in stream.encode(): container.mux(packet)
    v.need(path.stat().st_size<=196608,'NEUTRAL_SOURCE_LIMIT')
    return Source(str(path),hashlib.sha256(path.read_bytes()).hexdigest(),path.stat().st_size)


def fake(n,fail=False):
    class Fake:
        counters=dict(video_frames=0)
        resources={}
        def video_point(self,window,remaining):
            self.counters=dict(video_frames=n)
            if fail: raise v.worker.WorkerError('NEUTRAL_DECODE_ERROR')
            return b'neutral',dict(window=window,remaining=remaining)
        def close(self): self.resources={'worker_closed':True}
    return Fake()


class Completion(unittest.TestCase):
    def test_01_native_four_workers(self):
        source=neutral_video()
        profile=v.uhd.bind(source,'neutral-visual-completion')
        group=c.FourWorkers()
        try:
            with patch.object(v,'MAIN_GATE',True):
                for window in c.ORDER:
                    rgb,receipt=group.next(source,profile,'neutral-visual-completion')
                    self.assertEqual((receipt['pts'],receipt['next_pts']),v.POINTS[window])
                    self.assertEqual(receipt['native']['format'],'yuv420p')
                    self.assertFalse(rgb.flags.writeable)
                    del rgb
        finally:
            final=group.close()
            save('native-workers.json',dict(source=source.__dict__,records=group.records,final=final))
        self.assertTrue(final['complete'])
        self.assertLessEqual(final['frames'],400)
        for row in group.records:
            self.assertTrue(row['resources']['worker_closed'])
            self.assertEqual(row['resources']['job_commit_limit'],1073741824)
            self.assertEqual(row['resources']['process_commit_limit'],1073741824)
            self.assertEqual(row['counters']['audio_frames'],0)

    def test_02_native_error_forwarding(self):
        src=Source(str(OUT/'neutral.mp4'),'0'*64,(OUT/'neutral.mp4').stat().st_size)
        group=c.FourWorkers()
        profile=v.uhd.bind(src,'neutral-visual-hash-failure')
        try:
            with patch.object(v,'MAIN_GATE',True):
                with self.assertRaises(v.worker.WorkerError) as found:
                    group.next(src,profile,'neutral-visual-hash-failure')
                self.assertEqual(found.exception.code,'MEDIA_HASH_INVALID')
        finally:
            final=group.close()
            save('native-error.json',dict(records=group.records,final=final))
        self.assertFalse(final['complete'])
        self.assertTrue(group.records[0]['resources']['worker_closed'])

    def test_03_all_envelopes(self):
        base=(float.fromhex('0x0.0000000000001p-1022'),-0.0,0.5)*96
        alternative=(0.75,)*288
        workers=json.loads((OUT/'native-workers.json').read_bytes())['records']
        self.assertEqual(len(workers),4)
        for row in workers:
            row['budget_padding']=''
            row['budget_padding']='w'*(3072-len(c.canonical(row)))
        bindings={'references':'x'*2000}
        results=[]
        for name,vectors,error in (
            ('equal',[base]*8,None),('different',[base,alternative]*4,None),
            ('failure',[base]*8,{'primary':'x'*4000})):
            raw=c.envelope(vectors,workers,bindings,error)
            restored,data=c.restore(raw)
            self.assertEqual([c.pack_values(x) for x in restored],[c.pack_values(x) for x in vectors])
            self.assertLessEqual(len(raw),c.TABLE_LIMIT)
            results.append(dict(name=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
        save('envelope-sizes.json',dict(cases=results,upper=c.TABLE_UPPER))

    def test_04_envelope_overflow(self):
        with self.assertRaises(v.worker.WorkerError) as found:
            c.envelope([],[],{}, {'primary':'x'*4096})
        self.assertEqual(found.exception.code,'ERROR_LIMIT')
        with self.assertRaises(v.worker.WorkerError) as found:
            c.envelope([],[],{'binding':'x'*2048}, {'primary':'error'})
        self.assertEqual(found.exception.code,'BINDINGS_LIMIT')

    def test_05_exact_joint_boundary(self):
        group=c.FourWorkers()
        with patch.object(v,'open_video',side_effect=lambda *args:fake(100)) as opened:
            for _ in range(4): group.next(None,None,None)
            self.assertEqual(group.used,400)
            with self.assertRaises(v.worker.WorkerError): group.next(None,None,None)
            self.assertEqual(opened.call_count,4)
        self.assertTrue(group.close()['complete'])

    def test_06_joint_overflow_and_precheck(self):
        group=c.FourWorkers()
        with patch.object(v,'open_video',return_value=fake(401)):
            with self.assertRaises(v.worker.WorkerError) as found: group.next(None,None,None)
            self.assertEqual(found.exception.code,'GLOBAL_FRAME_LIMIT')
        self.assertEqual(group.used,401)
        with patch.object(v,'open_video') as opened:
            with self.assertRaises(v.worker.WorkerError): group.next(None,None,None)
            opened.assert_not_called()

    def test_07_early_stop_and_failure(self):
        for failure in (False,True):
            with self.subTest(failure=failure):
                group=c.FourWorkers()
                with patch.object(v,'open_video',return_value=fake(7,failure)):
                    if failure:
                        with self.assertRaises(v.worker.WorkerError): group.next(None,None,None)
                    else: group.next(None,None,None)
                self.assertEqual(group.used,7)
                self.assertFalse(group.close()['complete'])
                with patch.object(v,'open_video') as opened:
                    with self.assertRaises(v.worker.WorkerError): group.next(None,None,None)
                    opened.assert_not_called()

    def test_08_child_remaining_limit(self):
        decoder=object.__new__(v.VideoDecoder)
        decoder.frame_budget=1
        decoder.counters={'video_frames':1}
        with self.assertRaises(v.worker.WorkerError) as found:
            next(decoder._frames(None,None,'video'))
        self.assertEqual(found.exception.code,'GLOBAL_FRAME_LIMIT')
