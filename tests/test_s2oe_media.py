"""One focused qualification; controlled synthetic endpoints, no selected video."""
from dataclasses import asdict, replace
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch
from types import SimpleNamespace
import numpy as np

from tools import _s2oe_media_session as m
from tools import _s2oe_media_decoder as d
from tools import _s2oe_media_verification as verify

p, b, s = m.p, m.b, m.s
OUT = Path(os.environ["MEDIA_QUAL_OUT"])


class FixtureDecoder:
    """Explicit neutral endpoint supplier, not a claim of container decoding."""
    def __init__(self, source):
        self.counters = dict(container_read_bytes=0, packets=0, video_frames=0,
            audio_frames=0, audio_samples=0, selected_windows=0, passes=0)
        self.key, self.closed = None, False
        self.pcm = np.zeros(4800, dtype="<f4")
        self.rgb = np.full((1080, 1920, 3), 32, dtype=np.uint8)

    def select(self, repeat, window):
        if self.pcm is None:
            self.pcm = np.zeros(4800, dtype="<f4")
            self.rgb = np.full((1080,1920,3),32,dtype=np.uint8)
        if (repeat, window) != self.key:
            self.counters["selected_windows"] += 1
            self.counters["passes"] = repeat
            self.key = (repeat, window)
        pts = ((window*15000+1500)//1001)*1001
        return self.pcm, self.rgb, pts, pts+1001

    def release(self):
        self.pcm = self.rgb = None

    def close(self):
        self.closed = True
        self.pcm = self.rgb = None


def inputs(name):
    src = b.ROOT/"sources/s2oe-neutral"/name
    src.parent.mkdir(exist_ok=True)
    with src.open("xb") as f:
        f.write(b"neutral media binding fixture\x00\x01\x02")
    raw = src.read_bytes()
    manifest = p.build("media-neutral-"+name.replace(".", "-"),
        p.Source(str(src), hashlib.sha256(raw).hexdigest(), len(raw)), b.digest(m.inventory()))
    base_dir = b.ROOT/"reports/s2oc"/s.QUAL_ID
    anchor = s.read_json(base_dir/"caller-common.json")
    base, inv = s.qualified_common(b.decode_manifest(anchor["manifest"]), base_dir)
    refs = base["references"] + [s.file_reference("sources", b.ROOT/n) for n in m.OWN if
        not any(r[1] == n for r in base["references"])]
    refs.append(s.file_reference("metadata", base_dir/"caller-common.json"))
    refs.append(s.file_reference("sources", OUT/"inventory.json"))
    return manifest, m.bind_common(manifest, base, refs), inv


def failure_proof(folder, inv):
    common=s.load_common(OUT/folder)
    record,session=s.unpack(s.read_json(OUT/folder/"record.json"),s.read_json(OUT/folder/"session.json"),common)
    return verify.verify_record(record,session,common,inv)


class MediaQualification(unittest.TestCase):
    def error(self, code, fn):
        with self.assertRaises(p.MediaError) as cm:
            fn()
        self.assertEqual(cm.exception.code, code)

    def test_01_selection_and_counts(self):
        rows = p.sequence()
        self.assertEqual(p.counts(rows), dict(events=24, formations=20, auditory_cues=2,
            visual_cues=2, audio=22, nj=22, visual=22, payloads=44, scans=8, contacts=7392))
        self.assertEqual([(x.ordinal, x.kind, x.window_number) for x in rows if x.kind != b.AV],
            [(13,b.A,2),(14,b.V,2),(21,b.A,8),(22,b.V,8)])

    def test_02_time_mapping_and_second_pass(self):
        times = [p.runtime_times(e) for e in p.sequence()]
        self.assertEqual(times[-1]["field_window"][1], 4700000000)
        self.assertTrue(all(x["field_window"][1] <= y["field_window"][0] for x,y in zip(times,times[1:])))
        self.assertEqual(p.sequence()[10].window_number, 0)
        self.assertGreater(times[10]["field_window"][0], times[0]["field_window"][1])

    def test_03_pts_boundary(self):
        source = p.Source("unused", "0"*64, 1)
        manifest = p.build("media-time-fixture", source, "0"*64)
        e = manifest.events[0]
        valid = p.selection_receipt(manifest,e,1001,2002,"0"*64,"1"*64)
        self.assertEqual(valid["frame_pts"],1001)
        self.error("FRAME_SELECTION_INVALID",lambda:p.selection_receipt(manifest,e,2002,3003,"0"*64,"1"*64))
        self.error("FRAME_SELECTION_INVALID",lambda:p.selection_receipt(manifest,e,0,1001,"0"*64,"1"*64))

    def test_04_invalid_times(self):
        for pts,tb in ((None,(1,30000)),(-1,(1,30000)),(1,(1,0)),(True,(1,30000))):
            with self.subTest(pts=pts,tb=tb):
                self.error("PTS_INVALID",lambda:p.moment(pts,tb))

    def test_05_profiles_and_immutability(self):
        source=p.Source("unused","0"*64,1)
        self.error("MEDIA_PROFILE_INVALID",lambda:p.build("media-wrong-rate",replace(source,frame_rate=(30,1)),"0"*64))
        manifest=p.build("media-fixed-input",source,"0"*64)
        with self.assertRaises(AttributeError):
            manifest.events[0].pass_number=2

    def test_06_downmix_and_single_rounding(self):
        x=np.array([[0.25,-0.5,1.0],[0.125,0.25,-1.0]],dtype=np.float32)
        before=x.tobytes()
        got=d.mono(x)
        expected=np.array([0.5*(float(x[0,i])+float(x[1,i])) for i in range(3)],dtype="<f4")
        self.assertEqual(got.tobytes(),expected.tobytes())
        self.assertEqual(x.tobytes(),before)
        self.error("AUDIO_BLOCK_INVALID",lambda:d.mono(np.array([[np.inf],[0]],dtype=np.float32)))

    def test_07_hash_before_decode_and_read_count(self):
        manifest,_,_=inputs("hash.bin")
        counters={"container_read_bytes":0}
        with d.CountedFile(manifest.source,counters).file as f:
            self.assertEqual(f.tell(),0)
        self.assertEqual(counters["container_read_bytes"],manifest.source.size)
        counters={"container_read_bytes":0}
        self.error("MEDIA_HASH_INVALID",lambda:d.CountedFile(replace(manifest.source,sha256="0"*64),counters))
        self.assertEqual(counters["container_read_bytes"],manifest.source.size)

    def test_08_native_frame_and_audio_selection(self):
        av=d.load_av()
        frames=[]
        for pts in (0,1001,2002):
            f=av.VideoFrame(3840,2160,"yuv420p")
            for plane in f.planes: plane.update(bytes(plane.buffer_size))
            f.pts,f.time_base,f.colorspace,f.color_range=pts,Fraction(1,30000),1,1
            frames.append(f)
        audio=[]
        for i in range(5):
            f=av.AudioFrame.from_ndarray(np.zeros((2,1024),np.float32),format="fltp",layout="stereo")
            f.pts,f.time_base,f.sample_rate=i*1024,Fraction(1,48000),48000
            audio.append(f)
        decoder=d.Decoder.__new__(d.Decoder)
        decoder.source=p.Source("unused","0"*64,1)
        decoder.closed=False;decoder.repeat=1;decoder.window=-1
        decoder.video_next=decoder.audio_next=decoder.rgb=decoder.pcm=None
        decoder.video_last_time=decoder.audio_last_end=None
        decoder.vi,decoder.ai=iter(frames),iter(audio)
        decoder.counters={"audio_samples":0,"selected_windows":0}
        pcm,rgb,pts,nxt=decoder.select(1,0)
        self.assertEqual((pts,nxt),(1001,2002))
        self.assertEqual((pcm.shape,rgb.shape),((4800,),(1080,1920,3)))
        self.assertEqual(pcm.tobytes(),bytes(19200))
        self.assertEqual(decoder.select(1,0)[2:],(1001,2002))

    def test_09_native_full_session_and_readonly_cues(self):
        manifest,common,inv=inputs("full.bin")
        p.MAIN_GATE=True
        with patch.object(m,"Decoder",FixtureDecoder):
            session=m.start(manifest,common,inv,OUT/"native-full",neutral=True)
        previous=session._runtime.subject.snapshot().memory_state_digest
        for event in manifest.events:
            status=session.status()
            self.assertEqual(status,session.status())
            result=json.loads(session.next())
            current=session._runtime.subject.snapshot().memory_state_digest
            if event.kind!=b.AV:
                self.assertEqual(current,previous)
                self.assertEqual(result["memory_status"],"READ_ONLY_UNCHANGED")
            previous=current
        result=json.loads(session.stop())
        self.assertEqual(result["status"],"RECORDING_COMPLETE")
        self.assertEqual(session.stop(),b.canonical(result))
        self.assertTrue(session._materializer.decoder.closed)
        proof=verify.verify_once(OUT/"native-full",inv)
        self.assertTrue(proof["evaluation_allowed"])
        self.assertEqual(proof["native"]["field_contacts"],7392)
        self.error("SESSION_CLOSED",session.next)

    def test_10_native_controlled_stop_and_primary_failure(self):
        manifest,common,inv=inputs("stop.bin")
        p.MAIN_GATE=True
        with patch.object(m,"Decoder",FixtureDecoder):
            session=m.start(manifest,common,inv,OUT/"native-stop",neutral=True)
        self.error("EVENT_ORDER_INVALID",lambda:session.process(manifest.events[1]))
        session.next()
        before=session._runtime.subject.snapshot()
        result=json.loads(session.stop())
        self.assertEqual(result["status"],"NOT_EVALUABLE")
        self.assertEqual(result["failure"]["code"],"INCOMPLETE")
        self.assertEqual(result["failure"]["final"]["field_state_digest"],before.field_state_digest)
        self.assertEqual(result["failure"]["final"]["memory_state_digest"],before.memory_state_digest)
        self.assertFalse(failure_proof("native-stop",inv)["evaluation_allowed"])

    def test_11_gate_and_manifest_rejection(self):
        p.MAIN_GATE=False
        self.error("MAIN_GATE_CLOSED",lambda:m.start(None,None,None,OUT/"never"))
        self.assertFalse((OUT/"never").exists())
        self.assertFalse(p.MAIN_GATE)

    def test_12_full_budget_positions(self):
        self.assertEqual((p.SESSION_LIMITS["sources"],p.SESSION_LIMITS["metadata"],p.QUAL_LIMITS["metadata"]),
            (180224,65536,98304))
        self.assertEqual(b.LIMITS["sources"],174080)
        from reports.prepare_direct_media_budget import prepare
        upper=prepare()
        self.assertEqual(len(upper["positions"]),25)
        for row in upper["positions"]:
            for name in ("success","failure"):
                self.assertEqual(row[name]["violations"],[])
        from reports.qualify_direct_media_once import fixture_binding, shapes
        c,_=fixture_binding(s.file_reference("sources",OUT/"inventory.json"))
        pair=shapes.synthetic_forms(c,0)[1]
        for key,limit in (("sources",180224),("metadata",65536)):
            base=p.ledger(*pair,c)["totals"][key]
            for delta in (0,1):
                value=p.ledger(*pair,c,attachments=((key,"@boundary",limit-base+delta),))
                self.assertEqual(value["violations"],[] if delta==0 else [key.upper()+"_LIMIT"])

    def test_13_decoder_pass_reset_and_stop(self):
        manifest,_,_=inputs("passes.bin")
        decoder=d.Decoder(manifest.source)
        def container(*args,**kwargs):
            video=SimpleNamespace(type="video",time_base=Fraction(1,30000),average_rate=Fraction(30000,1001),
                codec_context=SimpleNamespace(width=3840,height=2160,thread_count=0))
            audio=SimpleNamespace(type="audio",time_base=Fraction(1,48000),codec_context=SimpleNamespace(sample_rate=48000))
            return SimpleNamespace(streams=[video,audio],demux=lambda stream:iter(()),close=lambda:None)
        with patch.object(decoder.av,"open",container):
            decoder.begin(1)
            decoder.begin(2)
            self.error("PASS_INVALID",lambda:decoder.begin(2))
            decoder.close()
            decoder.close()
        self.assertTrue(decoder.closed)
        self.assertEqual(decoder.handles,[])
        self.assertEqual(decoder.counters["container_read_bytes"],4*manifest.source.size)

    def test_14_primary_error_after_formation(self):
        manifest,common,inv=inputs("failure.bin")
        p.MAIN_GATE=True
        with patch.object(m,"Decoder",FixtureDecoder):
            session=m.start(manifest,common,inv,OUT/"native-failure",neutral=True)
        session.next()
        previous=session._runtime.subject.snapshot()
        with patch.object(session._materializer.decoder,"select",side_effect=p.MediaError("NEUTRAL_READ_FAILURE")):
            self.error("NEUTRAL_READ_FAILURE",session.next)
        record=json.loads(session.stop())
        self.assertEqual(record["status"],"NOT_EVALUABLE")
        self.assertEqual(record["failure"]["code"],"NEUTRAL_READ_FAILURE")
        self.assertEqual(record["failure"]["completed_events"],1)
        self.assertEqual(record["failure"]["final"]["field_state_digest"],previous.field_state_digest)
        self.assertFalse(failure_proof("native-failure",inv)["evaluation_allowed"])


if __name__=="__main__":
    unittest.main()
