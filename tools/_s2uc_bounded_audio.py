"""Bounded audio-only reader. No source is opened at module import."""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path

RATE = 48000
WINDOW = 4800
TOTAL = 480000
SOURCE = 'sources/media/NASA Earthrise Realtime Apollo 8.mp4'
SOURCE_SHA = '9a061d639c17849e52ace712c8752b5d377123a9eec99df896728098bd783d74'
SOURCE_SIZE = 13547755
CONFIG = dict(sample_rate=48000,window_size=4800,hop_size=480,band_count=48,min_frequency=50.,max_frequency=18000.)

class AudioError(ValueError): pass

def need(ok, code):
    if not ok: raise AudioError(code)

@dataclass(frozen=True)
class Limits:
    read_bytes:int=32*1048576
    packets:int=2048
    frames:int=512
    samples:int=524288
    batch_samples:int=65536
    channels:int=8

def locked_read(path):
    if os.name!='nt':return Path(path).open('rb')
    import ctypes as ct
    from ctypes import wintypes as wt
    import msvcrt
    api=ct.WinDLL('kernel32',use_last_error=True)
    api.CreateFileW.argtypes=[wt.LPCWSTR,wt.DWORD,wt.DWORD,ct.c_void_p,wt.DWORD,wt.DWORD,wt.HANDLE]
    api.CreateFileW.restype=wt.HANDLE
    handle=api.CreateFileW(str(Path(path).resolve()),0x80000000,1,None,3,128,None)
    if handle==wt.HANDLE(-1).value:raise ct.WinError(ct.get_last_error())
    try:fd=msvcrt.open_osfhandle(handle,os.O_RDONLY|os.O_BINARY)
    except BaseException:
        api.CloseHandle.argtypes=[wt.HANDLE];api.CloseHandle(handle);raise
    return os.fdopen(fd,'rb')

class BoundFile:
    def __init__(self,path,size,sha,limits):
        self.file=locked_read(path); self.read_bytes=0; self.hash_bytes=0; self.limits=limits
        try:
            h=hashlib.sha256()
            while block:=self.file.read(65536):
                self.hash_bytes+=len(block)
                need(self.hash_bytes<=size,'SOURCE_SIZE')
                h.update(block)
            need(self.hash_bytes==size and h.hexdigest()==sha,'SOURCE_HASH')
            self.file.seek(0)
        except BaseException:self.close();raise
    def read(self,n=-1):
        need(type(n) is int and 0<=n<=1048576,'READ_REQUEST')
        # No read can overshoot the byte ceiling, including repeated seeks.
        need(n<=self.limits.read_bytes-self.read_bytes,'READ_BUDGET')
        raw=self.file.read(n);self.read_bytes+=len(raw);return raw
    def seek(self,*args):return self.file.seek(*args)
    def tell(self):return self.file.tell()
    def readable(self):return True
    def seekable(self):return True
    def close(self):self.file.close()

class WindowAssembler:
    """One 4800-sample buffer plus the current decoder frame; no whole PCM list."""
    def __init__(self,limits=Limits()):
        import numpy as np
        self.limits=limits;self.buffer=np.empty(WINDOW,dtype='<f4');self.used=0
        self.accepted=0;self.windows=0;self.previous_end=None;self.frames=0;self.samples=0
        self.layout=None;self.closed=False;self.origin_rows=[];self.buffer_peak=0
    def push(self,planes,pts,time_base,rate,layout):
        import numpy as np
        need(not self.closed,'ASSEMBLER_CLOSED')
        need(type(pts) is int and time_base is not None,'PTS_MISSING')
        base=Fraction(time_base);need(base>0,'TIME_BASE')
        tick=pts*base*RATE;need(tick.denominator==1,'PTS_NOT_SAMPLE_ALIGNED');start=int(tick)
        need(rate==RATE,'SAMPLE_RATE')
        need(planes.ndim==2 and 1<=planes.shape[0]<=self.limits.channels,'CHANNEL_LIMIT')
        count=planes.shape[1];need(0<count<=self.limits.batch_samples,'BATCH_SAMPLE_LIMIT')
        self.frames+=1;self.samples+=count
        need(self.frames<=self.limits.frames,'FRAME_LIMIT');need(self.samples<=self.limits.samples,'SAMPLE_LIMIT')
        need(np.isfinite(planes).all() and (np.abs(planes)<=1).all(),'PCM_DOMAIN')
        if self.layout is None:self.layout=(layout,planes.shape[0])
        need(self.layout==(layout,planes.shape[0]),'LAYOUT_CHANGED')
        if self.previous_end is not None:
            need(start==self.previous_end,'PTS_GAP' if start>self.previous_end else 'PTS_OVERLAP')
        else:need(start<=0,'START_NOT_ZERO')
        self.previous_end=start+count
        # Decoder owns edit lists and skip-sample/priming; no manual offset subtraction.
        lo=max(0,-start);hi=min(count,TOTAL-start)
        if hi<=lo:return
        need(start+lo==self.accepted,'ACCEPTED_TIME_GAP')
        mono=planes[:,lo:hi].astype(np.float64).mean(axis=0).astype('<f4')
        offset=0
        while offset<len(mono):
            n=min(WINDOW-self.used,len(mono)-offset)
            self.buffer[self.used:self.used+n]=mono[offset:offset+n]
            self.origin_rows.append(dict(pts=pts,time_base=[base.numerator,base.denominator],source_start=start+lo+offset,samples=n))
            self.used+=n;self.accepted+=n;offset+=n;self.buffer_peak=max(self.buffer_peak,self.used)
            if self.used==WINDOW:
                self.windows+=1
                payload=self.buffer.tobytes()
                provenance=self.origin_rows;self.origin_rows=[];self.used=0
                yield payload,dict(index=self.windows,start_sample=(self.windows-1)*WINDOW,end_sample=self.windows*WINDOW,decoder_fragments=provenance)
    def finish(self):need(self.accepted==TOTAL and self.windows==100 and self.used==0,'EARLY_EOF')
    def close(self):self.buffer=None;self.origin_rows.clear();self.used=0;self.closed=True

def normalized_planes(frame):
    """No resampling, gain, dither or timestamp rewrite; exact PCM format scaling."""
    import numpy as np
    a=frame.to_ndarray();channels=len(frame.layout.channels)
    need(1<=channels<=8,'CHANNEL_LIMIT')
    if frame.format.is_planar:a=a.reshape(channels,frame.samples)
    else:a=a.reshape(frame.samples,channels).T
    if a.dtype.kind=='i':a=a.astype(np.float64)/(2.**(8*a.dtype.itemsize-1))
    elif a.dtype==np.uint8:a=(a.astype(np.float64)-128.)/128.
    else:need(a.dtype.kind=='f','PCM_FORMAT')
    return a

class AudioReader:
    def __init__(self,path,size,sha,limits=Limits(),*,job_name=None):
        from tools.s2uc_audio_worker import confirm_job
        confirm_job(job_name)
        self.handle=None;self.container=None;self.closed=False;self.packets=0;self.skipped_packets=0;self.decoded_frames=0;self.decoded_samples=0;self.batch_peak=0
        self.limits=limits;self.assembler=WindowAssembler(limits)
        try:
            from tools._s2oe_media_decoder import load_av
            av=load_av();self.handle=BoundFile(path,size,sha,limits)
            self.container=av.open(self.handle,mode='r',options={'ignore_editlist':'0','advanced_editlist':'1','protocol_whitelist':'file,pipe','enable_drefs':'0','use_absolute_path':'0'})
            need(len(self.container.streams.audio)>0,'NO_AUDIO')
            self.stream=self.container.streams.audio[0];self.stream.codec_context.thread_count=1
            need(self.stream.codec_context.sample_rate==RATE,'SAMPLE_RATE')
            self.iterator=self._windows()
        except BaseException:self.close();raise
    def _windows(self):
        try:
            for packet in self.container.demux():
                self.packets+=1;need(self.packets<=self.limits.packets,'PACKET_LIMIT')
                if packet.stream.index!=self.stream.index:
                    self.skipped_packets+=1;continue
                batch=packet.decode()
                batch_samples=sum(f.samples for f in batch);self.batch_peak=max(self.batch_peak,batch_samples)
                need(batch_samples<=self.limits.batch_samples,'BATCH_SAMPLE_LIMIT')
                self.decoded_frames+=len(batch);self.decoded_samples+=batch_samples
                need(self.decoded_frames<=self.limits.frames,'FRAME_LIMIT')
                need(self.decoded_samples<=self.limits.samples,'SAMPLE_LIMIT')
                for frame in batch:
                    need(frame.samples<=self.limits.batch_samples,'BATCH_SAMPLE_LIMIT')
                    for result in self.assembler.push(normalized_planes(frame),frame.pts,frame.time_base,frame.sample_rate,frame.layout.name):
                        yield result
                        if self.assembler.accepted==TOTAL:
                            self.assembler.finish();return
            self.assembler.finish()
        finally:self.close()
    def take(self):
        need(not self.closed,'READER_CLOSED')
        try:return next(self.iterator)
        except BaseException:self.close();raise
    def facts(self):
        a=self.assembler
        return dict(packets=self.packets,skipped_non_audio_packets=self.skipped_packets,frames=self.decoded_frames,decoded_samples_per_channel=self.decoded_samples,accepted=a.accepted,windows=a.windows,
                    buffer_peak_samples=a.buffer_peak,batch_peak_samples=self.batch_peak,layout=a.layout,
                    read_bytes=self.handle.read_bytes if self.handle else 0,hash_bytes=self.handle.hash_bytes if self.handle else 0,
                    first_audio_stream=self.stream.index if hasattr(self,'stream') else None,closed=self.closed)
    def close(self):
        if self.closed:return
        self.closed=True
        iterator=getattr(self,'iterator',None)
        if iterator is not None and not iterator.gi_running:iterator.close()
        try:
            if self.container is not None:self.container.close()
        finally:
            if self.handle is not None:self.handle.close()
            self.assembler.close()

class OutputLedger:
    LIMIT=4*1048576
    RESERVE=256*1024
    def __init__(self,folder):
        self.folder=Path(folder);self.folder.mkdir(exist_ok=False);self.used=0;self.finalized=False
    def write(self,name,value,final=False):
        need(not self.finalized,'OUTPUT_FINALIZED')
        need(Path(name).name==name,'OUTPUT_NAME')
        raw=json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()+b'\n'
        cap=self.LIMIT if final else self.LIMIT-self.RESERVE
        need(self.used+len(raw)<=cap and (not final or len(raw)<=self.RESERVE),'OUTPUT_LIMIT')
        # Account before open/write, so a partial failed write remains charged.
        self.used+=len(raw)
        with (self.folder/name).open('xb') as f:
            need(f.write(raw)==len(raw),'SHORT_WRITE')
        if final:self.finalized=True


def project_window(payload,origin,calls):
    from dataclasses import asdict
    import numpy as np
    from mcm_field_organism.log_spectral_receptor import LogSpectralConfig,LogSpectralReceptor
    from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState,AuditoryReceptorContact
    from tools import _s2nj_private_auditory_output_projection as nj
    need(len(payload)==19200,'WINDOW_LENGTH')
    config=LogSpectralConfig(**CONFIG);receptor=LogSpectralReceptor(config)
    need(calls['receptor']<100 and calls['nj']<100,'PROJECTION_CALL_LIMIT')
    calls['receptor']+=1
    raw=receptor.analyze(np.frombuffer(payload,dtype='<f4'))
    contact=AuditoryReceptorContact.ACTIVE_ENERGY if any(raw) else AuditoryReceptorContact.ACTIVE_ZERO
    need(origin['start_sample']%480==0,'PROFILE_TIME_ALIGNMENT')
    state=AuditoryReceptorState('auditory',nj.RAW_GEOMETRY,origin['start_sample']//480,origin['start_sample'],origin['end_sample'],receptor.channel_ids,raw,contact)
    calls['nj']+=1
    projection=nj.project_auditory_half_v1(state,config=config,source_profile_digest=nj.RAW_PROFILE_DIGEST)
    return asdict(projection)
