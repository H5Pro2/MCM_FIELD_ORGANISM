"""Fixed analyst control view, in the existing isolated decoder worker."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from tools import _s2oe_media_decoder as media
from tools import _s2oe_decoder_worker as worker
from tools import _s2oe_visual_consistency as old

VERSION='s2oe.fixed-central-detail.v1'
RECT=(960,540,1920,1080)
MAIN_GATE=False
COLOR=dict(format='rgb24',interpolation='AREA',src_colorspace=1,dst_colorspace=1,
           src_color_range='MPEG',dst_color_range='JPEG')
SPATIAL=dict(version=VERSION,selected_by='analyst_control',original=[3840,2160],rectangle=list(RECT),
             overview=[0,0,3840,2160],output=[1920,1080],time_base=[1,30000],native_rate=[30000,1001],
             detail_order='native-frame/full-size-rgb/crop',overview_order='unchanged-native-frame/area-rgb',color=COLOR)


def raw(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def digest(x):return hashlib.sha256(raw(x)).hexdigest()
def need(ok,code):worker.require(ok,code)


def rectangle(value):
    need(type(value) in (tuple,list) and len(value)==4 and all(type(x) is int for x in value), 'RECTANGLE_FORM_INVALID')
    x,y,w,h=value
    need(x>=0 and y>=0 and w>0 and h>0 and x+w<=3840 and y+h<=2160,'RECTANGLE_BOUNDS_INVALID')
    need(tuple(value)==RECT,'FIXED_RECTANGLE_CHANGED')
    return x,y,w,h


def crop(original,rect=RECT):
    x,y,w,h=rectangle(rect)
    need(type(original) is np.ndarray and original.dtype==np.uint8 and original.shape==(2160,3840,3),'ORIGINAL_RGB_INVALID')
    result=original[y:y+h,x:x+w].copy()
    need(result.nbytes==worker.RGB_BYTES,'RGB_SIZE_INVALID')
    return result


def project(frame):
    need((frame.width,frame.height)==(3840,2160) and frame.colorspace==frame.color_range==1,'NATIVE_PROFILE_INVALID')
    # Detail is cut from full-resolution RGB before the unchanged overview call.
    full=frame.reformat(width=3840,height=2160,**COLOR).to_ndarray()
    detail=crop(full);del full
    overview=frame.reformat(width=1920,height=1080,**COLOR).to_ndarray()
    need(overview.shape==(1080,1920,3) and overview.dtype==np.uint8,'OVERVIEW_INVALID')
    return overview,detail


def evidence(source,window,arm,pts,next_pts,native,rgb):
    value=dict(version=VERSION,profile_digest=digest(SPATIAL),source_sha256=source,
        window=window,selection=[10*window+1,20],pts=pts,next_pts=next_pts,time_base=[1,30000],
        arm=arm,rectangle=list(RECT) if arm=='DETAIL' else [0,0,3840,2160],
        scale=[1,1] if arm=='DETAIL' else [1,2],native=native,rgb_sha256=hashlib.sha256(rgb).hexdigest())
    need(len(raw(value))<=2048,'SPATIAL_EVIDENCE_LIMIT')
    return value


def validate_evidence(value,window,arm,source):
    need(type(value) is dict and set(value)=={'version','profile_digest','source_sha256','window','selection',
        'pts','next_pts','time_base','arm','rectangle','scale','native','rgb_sha256'},'EVIDENCE_FORM_INVALID')
    need(value['version']==VERSION and value['profile_digest']==digest(SPATIAL) and value['source_sha256']==source
         and value['window']==window and value['arm']==arm and value['selection']==[10*window+1,20]
         and value['time_base']==[1,30000] and value['rectangle']==(list(RECT) if arm=='DETAIL' else [0,0,3840,2160])
         and value['scale']==([1,1] if arm=='DETAIL' else [1,2]),'SPATIAL_BINDING_INVALID')
    a,b=value['pts'],value['next_pts']
    need(type(a) is int and type(b) is int and 0<=20*a<=(10*window+1)*30000<20*b,'PTS_SELECTION_INVALID')
    need(len(raw(value))<=2048,'SPATIAL_EVIDENCE_LIMIT')


class DetailDecoder(media.Decoder):
    def __init__(self,source):
        super().__init__(source)
        self.request_index=0;self.pending=None;self.pair_native=None

    def begin_video(self):
        h=media.CountedFile(self.source,self.counters);self.handles.append(h)
        c=self.av.open(h,mode='r');self.containers.append(c);stream=c.streams[0]
        need(stream.type=='video' and stream.time_base==Fraction(1,30000)
             and stream.average_rate==Fraction(30000,1001)
             and (stream.codec_context.width,stream.codec_context.height)==(3840,2160),'VIDEO_PROFILE_INVALID')
        stream.codec_context.thread_count=1
        self.vi=iter(self._frames(c,stream,'video'));self.video_last_time=None
        self.counters['passes']=1

    def select_native(self,window):
        center=Fraction(10*window+1,20);selected=None
        while True:
            frame=self.video_next if self.video_next is not None else next(self.vi,None)
            need(frame is not None,'FRAME_COVERAGE_MISSING')
            need(frame.pts is not None and frame.time_base==Fraction(1,30000),'FRAME_TIME_BASE_INVALID')
            time=Fraction(frame.pts,30000)
            if time>center:
                self.video_next=frame;self.next_pts=frame.pts;break
            need(self.video_last_time is None or time>self.video_last_time,'FRAME_ORDER_INVALID')
            self.video_last_time=time;self.video_next=None;selected=frame
        need(selected is not None,'FRAME_SELECTION_MISSING')
        self.frame_pts=selected.pts
        self.pair_native=old.native_binding(selected)
        self.rgb,self.pending=project(selected)

    def video_point(self,request,frame_budget=400):
        need(type(request) is int and request==self.request_index and 0<=request<20 and not self.closed,'VIEW_ORDER_INVALID')
        need(type(frame_budget) is int and frame_budget==400,'FRAME_BUDGET_INVALID')
        window,side=divmod(request,2)
        if not side:
            if request==0:self.begin_video()
            need(self.pending is None,'PENDING_VIEW_INVALID')
            self.select_native(window);rgb=self.rgb;self.rgb=None
            self.counters['selected_windows']+=1
        else:
            need(self.pending is not None,'DETAIL_MISSING');rgb=self.pending;self.pending=None
        proof=evidence(self.source.sha256,window,'DETAIL' if side else 'OVERVIEW',self.frame_pts,self.next_pts,self.pair_native,rgb)
        self.request_index+=1
        return rgb,proof

    def close(self):
        self.pending=self.pair_native=None
        super().close()


class DetailWorker(worker.WorkerDecoder):
    def __init__(self,source,**kwargs):
        self.source_hash=source.sha256;self.views_returned=0
        super().__init__(source,**kwargs)

    @staticmethod
    def _launch(args,**kwargs):
        return worker.WorkerDecoder._launch([args[0],'-m','tools._s2oe_fixed_detail','--worker'],**kwargs)

    def view(self,window,arm):
        need(type(window) is int and 0<=window<10 and arm in ('OVERVIEW','DETAIL'),'VIEW_INVALID')
        need(self._call_lock.acquire(blocking=False),'DECODER_BUSY')
        try:
            request=2*window+int(arm=='DETAIL')
            value=self._rpc(dict(op='video_point',window=request,frame_budget=400))['video']
            validate_evidence(value,window,arm,self.source_hash)
            rgb=np.frombuffer(self.slot,dtype=np.uint8,count=worker.RGB_BYTES,offset=worker.PCM_BYTES).copy().reshape(1080,1920,3)
            need(hashlib.sha256(rgb).hexdigest()==value['rgb_sha256'],'RGB_BINDING_INVALID')
            rgb.flags.writeable=False
            self.views_returned+=1
            return rgb,json.loads(raw(value))
        except BaseException:
            self.close();raise
        finally:self._call_lock.release()

    def status(self):
        return json.loads(raw(dict(closed=self.closed,views_returned=self.views_returned,
            status=('CLOSED_COMPLETE' if self.views_returned==20 else 'CLOSED_INCOMPLETE') if self.closed else 'OPEN',
            counters=self.counters,resources=self.resources)))


def start(source,binding):
    global MAIN_GATE
    need(MAIN_GATE,'DETAIL_GATE_CLOSED')
    MAIN_GATE=False
    need(binding['spatial']==SPATIAL and binding['source_sha256']==source.sha256,'DETAIL_START_BINDING_INVALID')
    root=Path(__file__).resolve().parents[1]
    need(type(binding.get('code')) is dict and 'tools/_s2oe_fixed_detail.py' in binding['code'],'DETAIL_CODE_MISSING')
    for name,bound in binding['code'].items():
        path=(root/name).resolve()
        need(path.is_relative_to(root),'DETAIL_CODE_PATH_INVALID')
        data=path.read_bytes()
        need([hashlib.sha256(data).hexdigest(),len(data)]==bound,'DETAIL_CODE_CHANGED')
    child=DetailWorker(source,diagnostic_arm='COMMIT_1024');child.source_hash=source.sha256
    return child


def pack_view(proof,values):
    need(len(values)==288 and all(type(v) is float and np.isfinite(v) and 0<=v<=1 for v in values),'RECEPTOR_VALUES_INVALID')
    result=dict(spatial=proof,values_hex=[v.hex() for v in values])
    need(len(raw(result))<=12288,'VIEW_ENVELOPE_LIMIT')
    return result


def pack_total(views,resources,control):
    need(len(views)<=24 and all(len(raw(v))<=12288 for v in views),'TOTAL_VIEWS_LIMIT')
    need(len(raw(resources))<=8192 and len(raw(control))<=8192,'SUPPLEMENT_LIMIT')
    result=dict(version=VERSION,spatial=SPATIAL,views=views,resources=resources,control=control,gates=False)
    need(len(raw(result))<=327680,'TOTAL_ENVELOPE_LIMIT')
    return result


if __name__=='__main__':
    need(sys.argv[1:]==['--worker'],'DETAIL_ENTRY_INVALID')
    worker.worker_main(DetailDecoder)
