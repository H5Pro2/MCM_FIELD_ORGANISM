"""Finite detail comparison closure, no memory or field operations."""
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import traceback
import numpy as np
from tools import _s2oe_fixed_detail as d
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor
from reports.run_immediate_visual_once import publish

VERSION='s2oe.detail-comparison-closure.v1'
CAPS={'record.json':327680,'partial.json':327680,'verification.json':8192,'evaluation.json':8192,
      'failure.json':8192,'balance.json':4096,'run.claim':5,'verification.claim':5}


@dataclass(frozen=True)
class Source:
    path:str
    sha256:str
    size:int
    video_time_base:tuple=(1,30000)
    audio_time_base:tuple=(1,48000)
    frame_rate:tuple=(30000,1001)
    video_size:tuple=(3840,2160)


def controls(receptor):
    av=d.media.load_av();out=[];pixels=[]
    for reverse in (False,True):
        row=((np.arange(3840)//80)%2).astype(np.uint8)*255
        if reverse:row=255-row
        rgb=np.broadcast_to(row[None,:,None],(2160,3840,3)).copy()
        pixels.append(hashlib.sha256(rgb).hexdigest())
        f=av.VideoFrame.from_ndarray(rgb,format='rgb24');del rgb
        f=f.reformat(format='yuv420p',src_colorspace=1,dst_colorspace=1,src_color_range='JPEG',dst_color_range='MPEG')
        f.colorspace=f.color_range=1
        overview,detail=d.project(f)
        for arm,image in (('OVERVIEW',overview),('DETAIL',detail)):
            values=receptor.analyze(image,frame_index=0).channel_values
            out.append(dict(control='K1' if reverse else 'K0',arm=arm,pixel_sha256=pixels[-1],
                rgb_sha256=hashlib.sha256(image).hexdigest(),values_hex=[v.hex() for v in values]))
        del overview,detail,f
    equal=[[out[i]['values_hex'][j]==out[i+2]['values_hex'][j] for j in range(288)] for i in (0,1)]
    return out,dict(pixel_hashes=pixels,equal=equal,primary_comparisons=576)


def verify(record,binding):
    """Independent receipt and control verification, without media or receptors."""
    d.need(record['version']==VERSION and record['binding_digest']==d.digest(binding),'TOTAL_BINDING_INVALID')
    d.need(record['status']=='RECORDING_COMPLETE' and len(record['views'])==20 and len(record['controls'])==4,'INCOMPLETE')
    source=binding['source_sha256'];last=-1
    for index,item in enumerate(record['views']):
        p=item['spatial'];window,side=divmod(index,2);arm=('OVERVIEW','DETAIL')[side]
        d.need(p['version']==d.VERSION and p['source_sha256']==source and p['profile_digest']==d.digest(binding['spatial'])
            and p['window']==window and p['arm']==arm and p['selection']==[10*window+1,20]
            and p['time_base']==[1,30000] and p['rectangle']==([0,0,3840,2160] if side==0 else [960,540,1920,1080])
            and p['scale']==([1,2] if side==0 else [1,1]),'SPATIAL_INVALID')
        d.need(type(p['pts']) is int and type(p['next_pts']) is int
            and 0<=20*p['pts']<=(10*window+1)*30000<20*p['next_pts'],'TIME_INVALID')
        n=p['native']
        d.need(n['format']=='yuv420p' and n['width']==3840 and n['height']==2160
            and n['colorspace']==n['color_range']==1 and len(n['planes'])==3,'NATIVE_INVALID')
        for plane,(w,h) in zip(n['planes'],((3840,2160),(1920,1080),(1920,1080)),strict=True):
            d.need((plane['width'],plane['height'])==(w,h) and len(plane['sha256'])==64,'PLANE_INVALID')
        if side:
            a=record['views'][index-1]['spatial']
            d.need(all(p[k]==a[k] for k in ('pts','next_pts','native','source_sha256')),'FRAME_PAIR_INVALID')
        else:
            d.need(p['pts']>last,'TIME_ORDER_INVALID');last=p['pts']
        d.need(len(d.raw(item))<=12288 and len(p['rgb_sha256'])==64,'VIEW_LIMIT')
    for item in [*record['views'],*record['controls']]:
        xs=item['values_hex'];d.need(len(xs)==288,'VALUES_INCOMPLETE')
        d.need(all(type(x) is str and math.isfinite(float.fromhex(x)) and 0<=float.fromhex(x)<=1
                   and float.fromhex(x).hex()==x for x in xs),'VALUES_INVALID')
    for i,item in enumerate(record['controls']):
        d.need((item['control'],item['arm'])==(('K0','K1')[i//2],('OVERVIEW','DETAIL')[i%2])
            and item['pixel_sha256']==record['control']['pixel_hashes'][i//2],'CONTROL_BINDING_INVALID')
    flags=[]
    for arm in (0,1):
        a=record['controls'][arm]['values_hex'];b=record['controls'][arm+2]['values_hex']
        flags.append([a[i]==b[i] for i in range(288)])
    d.need(flags==record['control']['equal'] and record['control']['primary_comparisons']==576,'CONTROL_COMPARISON_INVALID')
    r=record['resources'];c=r['counters'];job=r['resources']
    d.need(r['closed'] and r['status']=='CLOSED_COMPLETE' and r['views_returned']==20
        and c['selected_windows']==10 and c['passes']==1 and 0<c['video_frames']<=400 and c['packets']<=2048
        and c['audio_frames']==c['audio_samples']==0 and 0<c['container_read_bytes']<=12*binding['source_bytes'],'COUNTS_INVALID')
    d.need(job['worker_closed'] and job['job_confirmed_before_media'] and job['slot_bytes']==6240000
        and job['queue_capacity']==1 and job['process_commit_limit']==job['job_commit_limit']==1073741824
        and job['peak_process_commit']<=1073741824 and job['peak_job_commit']<=1073741824,'RESOURCE_INVALID')
    d.need(record['counts']==dict(media_analyses=20,control_analyses=4,values=6912)
        and len(d.raw(record))<=327680,'TOTAL_LIMIT')
    return dict(status='EVIDENCE_VALID',evaluation_allowed=True,record_digest=d.digest(record),
        read_only=True,control_comparisons=576,numerical_receptor_reconstruction=False)


def evaluate(record,proof):
    d.need(proof['status']=='EVIDENCE_VALID' and proof['evaluation_allowed']
        and proof['record_digest']==d.digest(record),'EVALUATION_FORBIDDEN')
    return dict(status='DESCRIPTIVE_ONLY',media=[dict(window=i,
        overview_rectangle=[0,0,3840,2160],detail_rectangle=[960,540,1920,1080],
        same_original=record['views'][2*i]['spatial']['native']==record['views'][2*i+1]['spatial']['native'],
        rgb_payloads_equal=record['views'][2*i]['spatial']['rgb_sha256']==record['views'][2*i+1]['spatial']['rgb_sha256']) for i in range(10)],
        control=dict(pixels_different=record['control']['pixel_hashes'][0]!=record['control']['pixel_hashes'][1],
            equal_by_arm=[all(x) for x in record['control']['equal']]),
        detail_advantage='NOT_ESTABLISHED',memory_stabilization='NOT_TESTED',
        boundary='Different original footprints; no cross-view L1 or temporal metric. Values retained in record.')


def ledger(directory,reference_bytes,prospective=None):
    files={p.name:p.stat().st_size for p in directory.iterdir() if p.is_file()} if directory.exists() else {}
    if prospective:files.update(prospective)
    d.need(all(n in CAPS for n in files),'OUTPUT_CLASS_INVALID')
    meta=sum(n for p,n in files.items() if p not in ('record.json','partial.json'))
    violations=[p for p,n in files.items() if n>CAPS[p]]
    total=reference_bytes+sum(files.values())
    if meta+24576>65536:violations.append('METADATA')
    if total+24576>4194304:violations.append('TOTAL')
    return dict(files=files,reference_bytes=reference_bytes,metadata=meta,binding_and_report_reserve=24576,total=total,violations=violations)


def execute(binding,directory,reference_bytes,*,opener=d.start,control_builder=controls,receptor=None):
    d.need(not directory.exists(),'OUTPUT_EXISTS')
    for names in (('record.json','verification.json','evaluation.json','balance.json','run.claim','verification.claim'),
                  ('partial.json','failure.json','balance.json','run.claim'),
                  tuple(CAPS)):
        d.need(not ledger(directory,reference_bytes,{n:CAPS[n] for n in names})['violations'],'PREFLIGHT_LIMIT')
    directory.mkdir()
    with (directory/'run.claim').open('xb') as f:f.write(b'once\n')
    # Claims use the existing exclusive file convention; keep their fixed budget.
    child=None;phase='START';views=[];record=None;resource=None
    try:
        d.MAIN_GATE=True
        try:child=opener(Source(binding['source_path'],binding['source_sha256'],binding['source_bytes']),binding)
        finally:d.MAIN_GATE=False
        receptor=LocalChannelGridReceptor() if receptor is None else receptor
        for window in range(10):
            for arm in ('OVERVIEW','DETAIL'):
                phase='MEDIA_VIEW';rgb,e=child.view(window,arm)
                phase='RECEPTOR';values=receptor.analyze(rgb,frame_index=window).channel_values
                views.append(d.pack_view(e,values));del rgb
        child.close();resource=child.status();phase='CONTROLS'
        c,findings=control_builder(receptor)
        record=dict(version=VERSION,binding_digest=d.digest(binding),status='RECORDING_COMPLETE',views=views,
            controls=c,control=findings,resources=resource,counts=dict(media_analyses=20,control_analyses=4,values=6912))
        phase='RECORD';d.need(not ledger(directory,reference_bytes,{'record.json':len(d.raw(record))})['violations'],'RECORD_LIMIT')
        publish(directory/'record.json',record);phase='VERIFY'
        with (directory/'verification.claim').open('xb') as f:f.write(b'once\n')
        stored=json.loads((directory/'record.json').read_bytes());proof=verify(stored,binding)
        publish(directory/'verification.json',proof);phase='EVALUATION'
        publish(directory/'evaluation.json',evaluate(stored,proof))
    except Exception as exc:
        if child is not None:
            try:child.close();resource=child.status()
            except Exception:pass
        publish(directory/'partial.json',dict(views=views,resources=resource))
        publish(directory/'failure.json',dict(status='NOT_EVALUABLE',phase=phase,completed_views=len(views),
            error=getattr(exc,'code',type(exc).__name__),traceback=traceback.format_exc(),gates=False))
        raise
    finally:
        d.MAIN_GATE=False
        if child is not None:child.close()
        value=ledger(directory,reference_bytes,{'balance.json':4096})
        publish(directory/'balance.json',value)
    return record
