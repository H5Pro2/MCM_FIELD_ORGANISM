"""Focused full-file connection; no selected media file or old test suite."""
from dataclasses import asdict, replace
from fractions import Fraction
import io
import json
import os
from pathlib import Path
import threading
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np

from tools import _s2oe_media_session as m
from tools import _s2oe_media_decoder as d
from tools import _s2oe_decoder_worker as worker
from tools import _s2oe_media_verification as verifier

p,b,s=m.p,m.b,m.s
OUT=Path(os.environ["FULL_FILE_QUAL_OUT"])


def manifest():
    return p.build("full-file-neutral-fixture", p.Source(str(b.ROOT/"sources/s2oe-worker-neutral/full-file-unused.bin"),
        "0"*64, 32), b.digest(m.inventory(True)), mode=p.FULL_VERSION)


class EndpointDecoder:
    """Neutral endpoints only; no assertion of real container or OS decoding."""
    def __init__(self, spec, common):
        self.counters=dict(container_read_bytes=0,packets=0,video_frames=0,audio_frames=0,
                           audio_samples=0,selected_windows=0,passes=0)
        self.resources=dict(m.full.resources(), flags=0x2308,active_process_limit=1,
            process_commit_limit=1073741824,job_commit_limit=1073741824,
            job_confirmed_before_media=True,read_counters_complete=True,
            private_profile=m.full.VERSION,private_profile_digest=common["decoder_profile"]["profile_digest"],
            private_run_id=spec.run_id)
        self.closed=False

    def select(self,repeat,window):
        self.counters.update(passes=1,selected_windows=window+1)
        pts=((42000*window+1500)//1001)*1001
        return np.zeros(4800,dtype="<f4"),np.full((1080,1920,3),32,dtype=np.uint8),pts,pts+1001

    def release(self): pass

    def drain(self):
        value=dict(video_eof=True,audio_eof=True,last_video_pts=800800,
                   audio_end_sample=1284080,selected_windows=20)
        self.resources["stream_ends"]=value
        return value

    def close(self):
        self.closed=True
        self.resources["worker_closed"]=True


def neutral_session(folder):
    spec=manifest()
    common=s.read_json(OUT/"neutral-common.json")
    inv=s.inventory()
    p.MAIN_GATE=True
    with patch.object(m.full,"open_decoder",side_effect=lambda x,c:EndpointDecoder(x,c)):
        return m.start(spec,common,inv,OUT/folder,neutral=True),inv


class FullFileChecks(unittest.TestCase):
    def code(self,expected,call):
        with self.assertRaises((p.MediaError,worker.WorkerError)) as caught: call()
        self.assertEqual(caught.exception.code,expected)

    def test_01_selection_and_clocks(self):
        spec=manifest()
        self.assertEqual(len(spec.events),20)
        self.assertEqual(p.selection_time(spec,spec.events[-1]),Fraction(133,5))
        self.assertEqual(p.runtime_times(spec.events[-1])["field_window"][1],3900000000)
        self.assertEqual(p.counts(spec.events)["contacts"],6720)
        self.assertEqual(p.counts(spec.events)["scans"],0)
        self.assertEqual(len(p.sequence()),24)

    def test_02_frame_selection(self):
        spec=manifest(); e=spec.events[-1]
        pts=((42000*19+1500)//1001)*1001
        p.selection_receipt(spec,e,pts,pts+1001,"0"*64,"1"*64)
        self.code("FRAME_SELECTION_INVALID",lambda:p.selection_receipt(spec,e,pts+1001,pts+2002,"0"*64,"1"*64))

    def test_03_mode_mixing(self):
        spec=manifest()
        self.code("SELECTION_INVALID",lambda:p.validate(replace(spec,schema=p.VERSION)))
        self.code("MEDIA_PROFILE_INVALID",lambda:p.build("full-file-wrong-rate",replace(spec.source,frame_rate=(30,1)),"0"*64,mode=p.FULL_VERSION))

    def test_04_decoder_limits(self):
        for modality,key,cap in (("video","video_frames",1024),("audio","audio_frames",2048)):
            with self.subTest(modality=modality):
                decoder=d.Decoder.__new__(d.Decoder);decoder.mode=d.FULL_MODE
                decoder.progress=lambda *x:None
                decoder.counters=dict(packets=0,video_frames=0,audio_frames=0)
                decoder.counters[key]=cap-1
                frame=SimpleNamespace(pts=0,time_base=Fraction(1,30000))
                container=SimpleNamespace(demux=lambda stream:iter([SimpleNamespace(size=1,decode=lambda:iter([frame,frame]))]))
                iterator=decoder._frames(container,None,modality)
                self.assertIs(next(iterator),frame)
                self.code("DECODE_LIMIT",lambda:next(iterator))

    def test_05_packet_limit(self):
        decoder=d.Decoder.__new__(d.Decoder);decoder.mode=d.FULL_MODE;decoder.progress=lambda *x:None
        decoder.counters=dict(packets=4095,video_frames=0,audio_frames=0)
        frame=SimpleNamespace(pts=0,time_base=Fraction(1,30000))
        container=SimpleNamespace(demux=lambda stream:iter([SimpleNamespace(size=1,decode=lambda:iter([frame]))]*2))
        iterator=decoder._frames(container,None,"video")
        next(iterator);self.code("PACKET_LIMIT",lambda:next(iterator))

    def test_06_early_eof(self):
        decoder=d.Decoder.__new__(d.Decoder);decoder.progress=lambda *x:None
        decoder.source=manifest().source;decoder.vi=iter(());decoder.video_next=None
        self.code("FRAME_COVERAGE_MISSING",lambda:decoder._select_video(Fraction(1,20)))

    def test_07_drain_without_conversion(self):
        decoder=d.Decoder.__new__(d.Decoder);decoder.mode=d.FULL_MODE;decoder.closed=False
        decoder.window=19;decoder.stream_ends=None;decoder.progress=lambda *x:None
        decoder.source=manifest().source;decoder.video_next=None;decoder.frame_pts=799799
        decoder.video_last_time=Fraction(799799,30000);decoder.audio_last_end=1281600
        frame=SimpleNamespace(pts=800800,time_base=Fraction(1,30000),width=3840,height=2160,colorspace=1,color_range=1)
        audio=SimpleNamespace(pts=1281600,samples=2480,time_base=Fraction(1,48000),sample_rate=48000,
                              layout=SimpleNamespace(name="stereo"),format=SimpleNamespace(name="fltp"))
        decoder.vi=iter([frame]);decoder.ai=iter([audio]);decoder.audio_next=None
        decoder.counters=dict(selected_windows=20,audio_samples=1281600)
        ends=decoder.drain()
        self.assertEqual((ends["last_video_pts"],ends["audio_end_sample"]),(800800,1284080))
        self.assertIsNone(decoder.rgb);self.assertIsNone(decoder.pcm)
        self.code("DRAIN_ORDER_INVALID",decoder.drain)

    def test_08_worker_drain_protocol(self):
        ends=dict(video_eof=True,audio_eof=True,last_video_pts=1,audio_end_sample=2,selected_windows=20)
        decoder=SimpleNamespace(progress=None,counters={},drain=lambda:ends,close=lambda:None)
        messages=iter([dict(op="init",version=worker.VERSION,sequence=1,mode=d.FULL_MODE,job="neutral",slot="neutral",source=asdict(manifest().source)),dict(op="drain",sequence=2)])
        output=io.BytesIO()
        with patch.object(worker,"confirm_worker_job"),patch.object(worker,"read_message",side_effect=lambda x:next(messages)),patch.object(worker.mmap,"mmap",return_value=SimpleNamespace(close=lambda:None)),patch.object(worker.sys,"stdout",SimpleNamespace(buffer=output)):
            worker.worker_main(decoder_factory=lambda source,mode:decoder)
        responses=[json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([x["stream_ends"] for x in responses if "stream_ends" in x],[ends])

    def test_09_stop_during_drain(self):
        decoder=worker.WorkerDecoder.__new__(worker.WorkerDecoder)
        decoder.mode=d.FULL_MODE;decoder._call_lock=threading.Lock();decoder.resources={}
        started=threading.Event();cancelled=threading.Event();errors=[]
        def rpc(message):
            started.set();cancelled.wait(2);raise worker.WorkerError("DECODER_CANCELLED")
        decoder._rpc=rpc
        def run():
            try: decoder.drain()
            except worker.WorkerError as exc: errors.append(exc.code)
        thread=threading.Thread(target=run);thread.start();self.assertTrue(started.wait(2))
        cancelled.set();thread.join(2)
        self.assertFalse(thread.is_alive());self.assertEqual(errors,["DECODER_CANCELLED"])
        self.assertFalse(decoder._call_lock.locked())

    def test_10_all_envelopes(self):
        common=s.read_json(OUT/"neutral-common.json")
        upper=m.full.envelope(common)
        self.assertEqual(len(upper["positions"]),21);self.assertEqual(upper["violations"],[])
        overflow=m.full.envelope(common,metadata_reserve=p.SESSION_LIMITS["metadata"])
        self.assertTrue(overflow["violations"])

    def test_11_native_full_session(self):
        session,inv=neutral_session("native-full")
        try:
            for _ in range(20): session.next()
            before=session._runtime.subject.snapshot()
            session.drain()
            self.assertEqual(session._runtime.subject.snapshot(),before)
            result=json.loads(session.close())
            self.assertEqual(result["status"],"RECORDING_COMPLETE")
            self.assertEqual(session.close(),b.canonical(result))
            proof=verifier.verify_once(OUT/"native-full",inv)
            self.assertEqual(proof["native"]["field_contacts"],6720)
            self.assertTrue(proof["evaluation_allowed"])
        finally:
            session.stop();p.MAIN_GATE=False

    def test_12_failure_after_formation(self):
        session,_=neutral_session("native-failure")
        try:
            session.next();before=session._runtime.subject.snapshot()
            with patch.object(session._materializer.decoder,"select",side_effect=p.MediaError("FRAME_COVERAGE_MISSING")):
                self.code("FRAME_COVERAGE_MISSING",session.next)
            result=json.loads(session.stop())
            self.assertEqual(result["status"],"NOT_EVALUABLE")
            self.assertEqual(result["failure"]["code"],"FRAME_COVERAGE_MISSING")
            self.assertEqual(result["failure"]["final"]["field_state_digest"],before.field_state_digest)
        finally:
            session.stop();p.MAIN_GATE=False

    def test_13_player_stop_phase(self):
        from tools import _s2oe_local_player as player
        obj=player.Player.__new__(player.Player)
        obj.lock=threading.Lock();obj.stop_event=threading.Event();obj.thread=None
        obj.state=dict(phase="DRAINING",closure_cause="UNKNOWN")
        calls=[];obj.session=SimpleNamespace(stop=lambda:calls.append("stop"))
        obj.status=lambda:b.canonical(obj.state)
        result=json.loads(obj.stop())
        self.assertEqual(result["closure_cause"],"USER_STOP")
        self.assertEqual(calls,["stop"]);self.assertTrue(obj.stop_event.is_set())

    def test_14_qualification_scope_and_boundaries(self):
        from reports import qualify_full_file_once as q
        self.assertEqual(q.QUAL_LIMITS["metadata"],262144)
        self.assertEqual(p.SESSION_LIMITS["metadata"],131072)
        self.assertEqual(sum(q.BASE_CAPS.values()),131072)
        for key,limit in q.QUAL_LIMITS.items():
            with self.subTest(key=key):
                self.assertEqual(q.limit_violations({key:limit},q.QUAL_LIMITS),[])
                self.assertEqual(q.limit_violations({key:limit+1},q.QUAL_LIMITS),[key])
        common=s.read_json(OUT/"neutral-common.json")
        self.assertTrue(m.full.envelope(common,metadata_reserve=131072)["violations"])

    def test_15_bounded_logs_and_temporary_accounting(self):
        from reports import qualify_full_file_once as q
        with tempfile.TemporaryDirectory(dir=OUT) as tmp:
            path=Path(tmp)
            for n in (8,9):
                with self.subTest(bytes=n):
                    target=path/"stdout.txt"
                    row=q.collect_log(io.BytesIO(b"a"*n),target,8)
                    self.assertEqual(row["received"],n)
                    self.assertEqual(row["stored"],8)
                    self.assertEqual(row["complete"],n==8)
                    self.assertEqual(target.read_bytes(),b"a"*8)
                    target.unlink()
            (path/"orphan.pending").write_bytes(b"retained")
            row=q.actual_balance(path)
            self.assertEqual(row["physical_bytes"],8)
            self.assertEqual(row["totals"]["metadata"],8)
            self.assertIn("orphan.pending:UNEXPECTED_OR_TEMPORARY_FILE",row["violations"])

    def test_16_combined_closure_and_reference_integrity(self):
        from reports import qualify_full_file_once as q
        # Independent administration fixture, not dependent on native test 11.
        common=s.read_json(OUT/"neutral-common.json")
        from tools._s2oc_shared_verification import synthetic_forms
        success,failure=synthetic_forms(common,0)
        rows=[p.ledger(*pair,common,proof_bytes=0,report_bytes=0) for pair in (success,failure)]
        self.assertTrue(all(not row["violations"] for row in rows))
        # Zero-prefix administrative fixture, with no native memory bodies.
        with tempfile.TemporaryDirectory(dir=OUT) as tmp:
            path=Path(tmp)
            record,binding=failure
            wire,session=s.pack(record,binding,common)
            native=path/"native-failure";native.mkdir()
            values={native/"common.json":common,native/"record.json":wire,native/"session.json":session}
            for target,value in values.items():
                s.prior.save(target,value)
            self.assertLessEqual(sum(x.stat().st_size for x in path.rglob("*") if x.is_file()),q.TEMP_RESERVE)
            balance=q.actual_balance(path)
            self.assertEqual(balance["violations"],[])
            self.assertEqual(balance["totals"],rows[1]["totals"])
            # A modified reference is rejected, not omitted from the ledger.
            with patch.object(s,"file_reference",return_value=["sources","invalid",0,"0"*64]):
                self.code("REFERENCE_CHANGED",lambda:q.actual_balance(path))


if __name__=="__main__": unittest.main(verbosity=2)
