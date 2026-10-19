import dataclasses,hashlib,json,tempfile,time,unittest,wave,subprocess,sys
from pathlib import Path
from fractions import Fraction
import numpy as np
from tools._s2uc_bounded_audio import WindowAssembler,Limits,AudioError,BoundFile,OutputLedger
from tools.s2uc_audio_worker import LimitedWorker,ROOT,BINDING,sha,MEMORY
FIX=ROOT/'reports/s2uc/audio-reader-development-20260930/fixtures'
FACTS=[]

def config(path):
    return dict(mode='neutral',binding=str(BINDING),binding_sha256=sha(BINDING),source=dict(path=str(path),size=path.stat().st_size,sha256=sha(path)))

def generate():
    FIX.mkdir(parents=True,exist_ok=True)
    for name,count in [('full.wav',484800),('short.wav',4800)]:
        p=FIX/name
        if not p.exists():
            with wave.open(str(p),'wb') as f:
                f.setnchannels(2);f.setsampwidth(2);f.setframerate(48000)
                for start in range(0,count,4800):f.writeframes(np.zeros((min(4800,count-start),2),dtype='<i2').tobytes())
    p=FIX/'priming.m4a'
    if not p.exists():
        from tools._s2oe_media_decoder import load_av
        av=load_av()
        with av.open(str(p),'w',format='mp4') as c:
            stream=c.add_stream('aac',rate=48000);stream.layout='stereo'
            for start in range(0,484800,1024):
                f=av.AudioFrame.from_ndarray(np.zeros((2,min(1024,484800-start)),dtype=np.float32),format='fltp',layout='stereo')
                f.sample_rate=48000;f.pts=start;f.time_base=Fraction(1,48000)
                for packet in stream.encode(f):c.mux(packet)
            for packet in stream.encode():c.mux(packet)
    from tools._s2oe_media_decoder import load_av
    av=load_av()
    for kind,delta in [('gap',1024),('overlap',-512)]:
        path=FIX/(kind+'.nut')
        if not path.exists():
            with av.open(str(path),'w',format='nut') as c:
                stream=c.add_stream('pcm_s16le',rate=48000);stream.layout='stereo'
                for start in range(0,20480,1024):
                    f=av.AudioFrame.from_ndarray(np.zeros((1,2048),dtype=np.int16),format='s16',layout='stereo')
                    f.sample_rate=48000;f.pts=start+(delta if start>=10240 else 0);f.time_base=Fraction(1,48000)
                    for packet in stream.encode(f):c.mux(packet)
                for packet in stream.encode():c.mux(packet)
    path=FIX/'multistream.nut'
    if not path.exists():
        with av.open(str(path),'w',format='nut') as c:
            video=c.add_stream('mpeg4',rate=10);video.width=16;video.height=16;video.pix_fmt='yuv420p'
            first=c.add_stream('pcm_s16le',rate=48000);first.layout='stereo'
            second=c.add_stream('pcm_s16le',rate=48000);second.layout='stereo'
            for i in range(3):
                vf=av.VideoFrame.from_ndarray(np.zeros((16,16,3),dtype=np.uint8),format='rgb24');vf.pts=i
                for pkt in video.encode(vf):c.mux(pkt)
                for stream,value in [(first,0),(second,10000)]:
                    f=av.AudioFrame.from_ndarray(np.full((1,9600),value,dtype=np.int16),format='s16',layout='stereo')
                    f.sample_rate=48000;f.pts=i*4800;f.time_base=Fraction(1,48000)
                    for pkt in stream.encode(f):c.mux(pkt)
            for stream in (video,first,second):
                for pkt in stream.encode():c.mux(pkt)
    (FIX/'time-cases.json').write_text(json.dumps({'negative_preroll':[-1024,2048],'gap':[0,1024,2048],'overlap':[0,1024,512],'missing_pts':None,'fractional_pts':[1,96000],'early_eof':4800,'end_overhang':[479232,2048]}))

class AudioCoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):generate()
    def push(self,a,start,count=1024,rate=48000,base=Fraction(1,48000),channels=2):
        return list(a.push(np.zeros((channels,count),dtype=np.float32),start,base,rate,'stereo' if channels==2 else 'mono'))
    def test_zero_contiguous_and_end_overhang(self):
        a=WindowAssembler();out=[]
        for start in range(0,480000,1024):out.extend(self.push(a,start))
        a.finish();self.assertEqual(len(out),100);self.assertEqual(a.accepted,480000);self.assertEqual(a.buffer_peak,4800)
        self.assertEqual(out[0][1]['start_sample'],0);self.assertEqual(out[-1][1]['end_sample'],480000)
        a.close();self.assertIsNone(a.buffer)
    def test_negative_preroll_no_double_shift(self):
        a=WindowAssembler();out=[]
        fixture=json.loads((FIX/'time-cases.json').read_text())
        for start in range(fixture['negative_preroll'][0],480000,1024):out.extend(self.push(a,start))
        a.finish();self.assertEqual(out[0][1]['decoder_fragments'][0]['source_start'],0);self.assertEqual(a.accepted,480000)
        a.close()
    def test_missing_fractional_pts_and_positive_start(self):
        for pts,base,code in [(None,Fraction(1,48000),'PTS_MISSING'),(1,Fraction(1,96000),'PTS_NOT_SAMPLE_ALIGNED'),(1024,Fraction(1,48000),'START_NOT_ZERO')]:
            with self.subTest(code=code):
                a=WindowAssembler()
                with self.assertRaisesRegex(AudioError,code):self.push(a,pts,base=base)
                a.close()
    def test_gaps_overlaps_and_early_eof(self):
        for start,code in [(2048,'PTS_GAP'),(512,'PTS_OVERLAP')]:
            a=WindowAssembler();self.push(a,0)
            with self.assertRaisesRegex(AudioError,code):self.push(a,start)
            a.close()
        a=WindowAssembler();self.push(a,0)
        with self.assertRaisesRegex(AudioError,'EARLY_EOF'):a.finish()
        a.close()
    def test_reader_requires_job_before_open(self):
        from tools._s2uc_bounded_audio import AudioReader
        with self.assertRaisesRegex(ValueError,'JOB_REQUIRED'):AudioReader(FIX/'full.wav',0,'0'*64)
    def test_limits_cannot_be_enlarged(self):
        with self.assertRaisesRegex(ValueError,'WATCHDOG_LIMIT_INVALID'):LimitedWorker({'mode':'helper'},request_seconds=31)
        with self.assertRaisesRegex(ValueError,'WATCHDOG_LIMIT_INVALID'):LimitedWorker({'mode':'helper'},total_seconds=301)
    def test_counter_limits(self):
        cases=[(dict(frames=0),1024,2,'FRAME_LIMIT'),(dict(samples=1023),1024,2,'SAMPLE_LIMIT'),(dict(batch_samples=1023),1024,2,'BATCH_SAMPLE_LIMIT'),(dict(channels=1),1024,2,'CHANNEL_LIMIT')]
        for kw,count,ch,code in cases:
            a=WindowAssembler(dataclasses.replace(Limits(),**kw))
            with self.assertRaisesRegex(AudioError,code):self.push(a,0,count=count,channels=ch)
            a.close()
    def test_pcm_rate_and_layout_rejection(self):
        a=WindowAssembler()
        with self.assertRaisesRegex(AudioError,'SAMPLE_RATE'):self.push(a,0,rate=44100)
        a.close();a=WindowAssembler();self.push(a,0)
        with self.assertRaisesRegex(AudioError,'LAYOUT_CHANGED'):self.push(a,1024,channels=1)
        a.close()
        for x in [float('nan'),1.01]:
            a=WindowAssembler()
            with self.assertRaisesRegex(AudioError,'PCM_DOMAIN'):list(a.push(np.full((1,1),x),0,Fraction(1,48000),48000,'mono'))
            a.close()
    def test_read_hash_budget_and_close(self):
        p=FIX/'short.wav'
        with self.assertRaisesRegex(AudioError,'SOURCE_HASH'):BoundFile(p,p.stat().st_size,'0'*64,Limits())
        f=BoundFile(p,p.stat().st_size,sha(p),dataclasses.replace(Limits(),read_bytes=10))
        self.assertEqual(len(f.read(10)),10)
        with self.assertRaisesRegex(AudioError,'READ_BUDGET'):f.read(1)
        self.assertEqual(f.read_bytes,10);f.close();self.assertTrue(f.file.closed)
    def test_source_locked_until_close(self):
        p=FIX/'short.wav';f=BoundFile(p,p.stat().st_size,sha(p),Limits())
        try:
            with self.assertRaises(PermissionError):
                with p.open('r+b'):pass
        finally:f.close()
        with p.open('r+b'):pass
    def test_output_reserve_and_exclusive_write(self):
        with tempfile.TemporaryDirectory() as d:
            ledger=OutputLedger(Path(d)/'out');ledger.LIMIT=300;ledger.RESERVE=100
            with self.assertRaisesRegex(AudioError,'OUTPUT_LIMIT'):ledger.write('data.json',{'data':'x'*200})
            ledger.write('data.json',{'ok':True})
            with self.assertRaises(FileExistsError):ledger.write('data.json',{})
            ledger.write('closure.json',{'status':'NOT_EVALUABLE'},final=True)
            self.assertLessEqual(sum(p.stat().st_size for p in ledger.folder.iterdir()),300)
            with self.assertRaisesRegex(AudioError,'OUTPUT_FINALIZED'):ledger.write('after.json',{})

class OrchestrationTests(unittest.TestCase):
    def exercise(self,failure):
        from unittest.mock import patch
        from tools import s2uc_audio_worker as module
        class NeutralWorker:
            def __init__(self,*args,**kwargs):self.proof={'neutral_stub':True};self.closed=False
            def request(self,value):
                if failure and value['index']==7:raise ValueError('NEUTRAL_FAILURE')
                return {'index':value['index'],'neutral_stub':True}
            def finish(self):return {'closed':True,'neutral_stub':True}
            def close(self):self.closed=True
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);binding=root/'binding.json';binding.write_text('{"files":[]}')
            output='reports/s2uc/nasa-contiguous-materialization-20260930-01'
            (root/output).parent.mkdir(parents=True)
            auth=root/'authorization.json'
            auth.write_text(json.dumps(dict(status='AUTHORIZED_ONCE',action='NASA_FIRST_10S_MATERIALIZE_ONLY',binding_sha256=sha(binding),output=output)))
            with patch.object(module,'ROOT',root),patch.object(module,'BINDING',binding),patch.object(module,'LimitedWorker',NeutralWorker):
                status=module.materialize(auth)
                self.assertEqual(status,'NOT_EVALUABLE' if failure else 'MATERIALIZATION_COMPLETE')
                closure=json.loads((root/output/'closure.json').read_text())
                self.assertEqual(closure['windows'],6 if failure else 100)
                self.assertLessEqual(sum(p.stat().st_size for p in (root/output).iterdir()),4*1048576)
                self.assertLessEqual((root/output/'closure.json').stat().st_size,256*1024)
                self.assertFalse(closure['comparison_executed'])
                with self.assertRaises(FileExistsError):module.materialize(auth)
    def test_success_closure_and_no_retry(self):self.exercise(False)
    def test_partial_failure_reserved_closure_and_no_retry(self):self.exercise(True)

class ProcessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):generate()
    def test_real_wav_reader(self):
        cfg=config(FIX/'full.wav');cfg['neutral_project']=True
        w=LimitedWorker(cfg)
        try:
            for i in range(1,101):
                row=w.request({'op':'next','index':i});self.assertEqual(row['index'],i);self.assertEqual(len(row['projection']['values']),48)
                self.assertEqual(row['projection']['snapshot_index'],(i-1)*10)
                self.assertEqual(row['projection']['window_start_tick'],(i-1)*4800)
                self.assertEqual(row['projection']['window_end_tick'],i*4800)
            facts=w.finish();FACTS.append(dict(case='wav',result=facts,job=w.proof))
            self.assertEqual(facts['facts']['accepted'],480000);self.assertEqual(facts['facts']['windows'],100)
            self.assertEqual(facts['projection_calls'],{'receptor':100,'nj':100})
            self.assertTrue(w.closed and facts['facts']['closed']);self.assertIsNotNone(w.process.poll())
        finally:w.close()
    def test_aac_edit_list_and_priming(self):
        p=FIX/'priming.m4a';self.assertIn(b'elst',p.read_bytes())
        w=LimitedWorker(config(p))
        try:
            first=w.request({'op':'next','index':1})
            self.assertEqual(first['origin']['decoder_fragments'][0]['source_start'],0)
            for i in range(2,101):w.request({'op':'next','index':i})
            facts=w.finish();FACTS.append(dict(case='aac_edit_priming',first=first,result=facts,job=w.proof))
            self.assertEqual(facts['facts']['accepted'],480000)
        finally:w.close()
    def test_only_first_audio_stream(self):
        w=LimitedWorker(config(FIX/'multistream.nut'))
        try:
            row=w.request({'op':'next','index':1})
            self.assertEqual(row['pcm_sha256'],hashlib.sha256(bytes(19200)).hexdigest())
            result=w.finish();self.assertEqual(result['facts']['first_audio_stream'],1)
            self.assertGreater(result['facts']['skipped_non_audio_packets'],0)
            FACTS.append(dict(case='first_audio_only',result=result))
        finally:w.close()
    def test_pending_authorization_cannot_open_nasa(self):
        from tools.s2uc_audio_worker import materialize
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'auth.json';p.write_text('{}')
            with self.assertRaisesRegex(ValueError,'AUTHORIZATION_REQUIRED'):materialize(p)
    def test_eof_closes_child(self):
        w=LimitedWorker(config(FIX/'short.wav'))
        w.request({'op':'next','index':1})
        with self.assertRaisesRegex(ValueError,'EARLY_EOF'):w.request({'op':'next','index':2})
        self.assertTrue(w.closed);self.assertIsNotNone(w.process.poll())
    def test_memory_limit_real_allocation(self):
        w=LimitedWorker({'mode':'helper'})
        try:
            self.assertFalse(w.ready['decoder_imported']);self.assertEqual(w.ready['job']['process_commit_limit'],MEMORY)
            row=w.request({'op':'memory'});self.assertTrue(row['allocation_denied'])
            FACTS.append(dict(case='memory',result=row,job=w.job.snapshot()))
        finally:w.close()
    def test_request_watchdog(self):
        w=LimitedWorker({'mode':'helper'},request_seconds=0.5)
        with self.assertRaisesRegex(ValueError,'TIMEOUT'):w.request({'op':'sleep','seconds':5})
        self.assertTrue(w.closed);self.assertIsNotNone(w.process.poll());FACTS.append(dict(case='request_timeout',job=w.proof))
    def test_total_watchdog_while_parent_idle(self):
        w=LimitedWorker({'mode':'helper'},total_seconds=1.)
        time.sleep(1.2)
        self.assertTrue(w.total_expired);self.assertIsNotNone(w.process.poll());w.close()
        FACTS.append(dict(case='total_timeout',job=w.proof))
    def test_unadmitted_child_cannot_start(self):
        from tools._s2oe_decoder_worker import DecoderJob
        job=DecoderJob()
        try:
            result=subprocess.run([sys.executable,'-S',str(ROOT/'tools/s2uc_audio_worker.py'),'child'],
                input=json.dumps({'mode':'helper','job':job.name})+'\n',capture_output=True,text=True,timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertNotEqual(result.returncode,0);self.assertIn('JOB_MEMBERSHIP',result.stdout)
            self.assertNotIn('ready',result.stdout)
        finally:job.close()
    def test_real_container_gap_and_overlap(self):
        for name,code in [('gap','PTS_GAP'),('overlap','PTS_OVERLAP')]:
            with self.subTest(name=name):
                w=LimitedWorker(config(FIX/(name+'.nut')))
                try:
                    w.request({'op':'next','index':1});w.request({'op':'next','index':2})
                    with self.assertRaisesRegex(ValueError,code):w.request({'op':'next','index':3})
                    self.assertTrue(w.closed);self.assertIsNotNone(w.process.poll())
                finally:w.close()
    def test_real_decoder_tight_budgets(self):
        for key,val,code in [('packets',1,'PACKET_LIMIT'),('frames',1,'FRAME_LIMIT'),('samples',1024,'SAMPLE_LIMIT'),('batch_samples',1,'BATCH_SAMPLE_LIMIT'),('read_bytes',1,'READ_BUDGET')]:
            with self.subTest(limit=key):
                cfg=config(FIX/'priming.m4a');cfg['limits']={key:val};w=None
                try:
                    with self.assertRaisesRegex(ValueError,code):
                        w=LimitedWorker(cfg);w.request({'op':'next','index':1})
                finally:
                    if w:w.close()
    def test_wrong_source_hash_before_decoder(self):
        cfg=config(FIX/'full.wav');cfg['source']['sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'SOURCE_HASH'):LimitedWorker(cfg)
    def test_changed_runtime_binding_rejected(self):
        cfg=config(FIX/'full.wav');cfg['binding_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'WORKER_CHANNEL|BINDING_CHANGED'):LimitedWorker(cfg)

if __name__=='__main__':unittest.main()
