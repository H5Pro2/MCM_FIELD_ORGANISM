"""Delta-capture fork: identical checks; bounded previous records."""
from tools._s2uc_ura1_delta_encode import collection
import gzip,hashlib,json,struct,sys
from tools._s2uc_ura1 import OriginalRecencyAdapter
from tools._s2uc_multi_error import MultiErrorAdapter,HEAD,ENTRY,POLICY
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import PerceptionSample
from tools._s2uc_k1_probe import snapshot,cellmap
from tools._s2uc_ulz1_resources import Meter,deep
from tools._s2uc_ura1_reference import Reference,mae

PROFILE='4309cfc91eb99fc2a999fdac99c5a7f1807ee654996e019ec0d94e3900bcbd4b'
def raw(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def need(ok,why):
    if not ok:raise ValueError(why)
def create(mode):
    cls=MultiErrorAdapter if mode=='U' else OriginalRecencyAdapter
    return cls(FactorRecencyArm(PROFILE,'comparison'),'stream',multi_policy=POLICY)
def vector(x):return tuple(x+j/4096 for j in range(48))
def blocks(items):
    """Explicit hand blocks only; no pseudorandomness or namespace access."""
    return [vector(x) for cue,target in items for x in (cue,.5,target,.0625)]

def common(a):
    bank=bytearray(a.bank);bank[202:204]=bytes(2) # choice/reason only
    frame=lambda f:None if f is None else dict(ordinal=f.ordinal,values=f.values,segment=f.segment,profile=f.profile,owner=f.owner)
    return dict(stock=snapshot(a.arm),bank=bank.hex(),pair=[frame(f) for f in a.pair],
        intervals=list(a.intervals),hints=[frame(f) for f in a.arm._hints],
        forming_frames=[frame(f) for f in a.arm._forming],
        forming_segment=a.arm._forming_segment,hint_segment=a.arm._hint_segment,
        frozen=[frame(f) for f in a._frozen],pframe=frame(a._pframe),
        next_index=a.next_index,accepted=a.accepted,admitted=a.admitted,
        revision=a.revision,closed=a.closed)

def equal_events(u,r):
    need(len(u)==len(r),'PAIRED_EVENT_COUNT')
    for n,(left,right) in enumerate(zip(u,r,strict=True)):
        need(raw(left)==raw(right),f'PAIRED_STATE_EVENT:{n}')

class ResourceMeter(Meter):
    def __init__(self,a):
        super().__init__(a);self.whole=[]
    def measure_full(self,name,fn,sample=None):
        before=deep((self.a,sample))
        try:return self.measure(name,fn)
        finally:
            after=deep((self.a,sample));c=self.calls[-1]
            self.whole.append(dict(operation=name,whole_before=before,whole_after=after,
                traced_transient=c['transient'],whole_conservative=max(before+c['transient'],after),
                input_object_bytes=deep(sample),additional_total=c['total']))

def run_arm(values,mode,*,trace=False,fault=None):
    need(mode in ('U','R'),'MODE')
    need(4<=len(values)<=128 and len(values)%4==0,'NEUTRAL_ONLY_MAX_128_FRAMES')
    a=create(mode);ref=Reference(mode);meter=ResourceMeter(a);events=collection();internal=collection();forecasts=collection();rows=collection()
    wanted={'_admit','_promote','_prune','form','close_segment','hint','consume_feedback','_release','close_owner'}
    oldprofile=sys.getprofile()
    def profile(frame,event,arg):
        if event not in ('call','return') or frame.f_code.co_name not in wanted:return
        obj=frame.f_locals.get('self')
        if obj is a or obj is a.arm:
            internal.append(dict(method=frame.f_code.co_name,event=event,state=common(a)))
    def operation(name,fn,sample=None):
        events.append(dict(stage=name+':before',state=common(a)))
        if trace:
            sys.setprofile(profile)
            try:result=fn()
            finally:sys.setprofile(oldprofile)
        else:result=meter.measure_full(name,fn,sample)
        events.append(dict(stage=name+':after',state=common(a)))
        return result
    try:
        for i,value in enumerate(values,1):
            sample=PerceptionSample(tuple(value),PROFILE,'comparison','stream',i,(i-1)*4800,i*4800)
            if a.pending_prediction:
                need(struct.pack('<48d',*a.selected_values)==struct.pack('<48d',*ref.pending['output']),'REFERENCE_FROZEN_OUTPUT')
                measured=mae(a.selected_values,value);expected=ref.feedback(i,value)
                operation('feedback',lambda:a.consume_feedback(sample),sample)
                if fault=='feedback' and i==7:
                    # Deliberate live feedback corruption, not a policy alternative.
                    a.bank[8]^=1
                need(cellmap(a)==ref.cells,'REFERENCE_FEEDBACK_CELLS')
                need(measured==expected['error'],'REFERENCE_ERROR')
                rows.append(dict(target=i,error=measured,updates=expected['updates']))
            receipt=operation('perception',lambda:a.accept_perception(sample),sample)
            expected=ref.perceive(i,value)
            if fault=='stock' and i==8:a.arm._observation_end[999]=i
            need(raw(snapshot(a.arm))==raw(ref.stock.snapshot()),'REFERENCE_STOCK')
            need(cellmap(a)==ref.cells,'REFERENCE_PROMOTION_CELLS')
            if expected:
                f=json.loads(receipt.json_text)
                actual=[dict(key=({'retained':0,'candidate':1}[m['role']],m['generation'],m['offset']),ordinals=m['ordinals'],factors=m['factors']) for m in f['matches']]
                need(actual==expected['matches'],'REFERENCE_MATCHES')
                hs=[(m,h) for m,h in zip(f['matches'],f['hypotheses'],strict=True) if h['eligible']]
                need(len(hs)==len(expected['hypotheses']),'REFERENCE_ELIGIBILITY')
                for j,((m,h),e) in enumerate(zip(hs,expected['hypotheses'],strict=True)):
                    need((None if h['ec'] is None else (h['ec'],h['ep']))==e['before'],'REFERENCE_PRE_CELLS')
                    need(h['ticket']==j and ENTRY.unpack_from(a.bank,208+16*j)[:3]==(e['key'][1],e['key'][0],e['key'][2]),'REFERENCE_TICKET')
                    need(a._frozen[j].ordinal==e['original'] and a._frozen[j].values==e['values'],'REFERENCE_ORIGINAL')
                selected=None if not f['choice'] else expected['hypotheses'][f['choice']-1]['key']
                need(selected==expected['chosen'],'REFERENCE_CHOICE')
                need(tuple(a.selected_values)==expected['output'],'REFERENCE_OUTPUT')
                need(f['input_indices']==[i-1,i] and f['source_intervals']==[[(i-2)*4800,(i-1)*4800],[(i-1)*4800,i*4800]],'REFERENCE_INPUT')
                need(f['profile']==PROFILE and f['owner']=='comparison' and f['stream']=='stream','REFERENCE_SCOPE')
                need(a.pending_prediction.provenance_json==receipt.json_text,'REFERENCE_RECEIPT')
                meter.receipt=max(meter.receipt,len(receipt.json_text.encode()))
                meter.slots=max(meter.slots,1+int(a.pending_prediction.context_values is not None))
                need(meter.receipt<=16384 and meter.slots<=2,'OUTPUT_RESOURCE')
                forecasts.append(dict(index=i,receipt=f,output=list(a.selected_values),selected=selected,
                    originals=[dict(key=e['key'],ordinal=e['original']) for e in expected['hypotheses']]))
        operation('finish',a.finish_story);ref.finish()
        need(a.closed and not any(a.bank) and not any(a._frozen) and not a.arm._forming and not a.arm._candidate and not a.arm._retained_many,'CLEANUP')
        return dict(mode=mode,neutral_only=True,frames=len(values),events=events,internal=internal,
            forecasts=forecasts,rows=rows,cleanup=True,reference_equal=True,
            resources=None if trace else meter.snapshot()|dict(whole_operations=meter.whole),
            censored_target=len(values)+1)
    finally:
        sys.setprofile(oldprofile)
        if not a.closed:a._terminate()

def pair(values,*,trace=False):
    u=run_arm(values,'U',trace=trace);r=run_arm(values,'R',trace=trace)
    equal_events(u['events'],r['events']);equal_events(u['internal'],r['internal'])
    for a,b in zip(u['rows'],r['rows'],strict=True):need(a['updates']==b['updates'],'PAIRED_FEEDBACK')
    for a,b in zip(u['forecasts'],r['forecasts'],strict=True):
        need(a['originals']==b['originals'],'PAIRED_ORIGINALS')
        for key in ('matches','hypotheses','input_indices','source_intervals','read_revision'):
            need(a['receipt'][key]==b['receipt'][key],'PAIRED_FORECAST:'+key)
    differences=[dict(target=a['index']+1,U=a['output'],R=b['output'],
        U_choice=a['selected'],R_choice=b['selected'],originals=a['originals'])
        for a,b in zip(u['forecasts'],r['forecasts'],strict=True) if a['output']!=b['output'] and a['index']<len(values)]
    return dict(neutral_only=True,source=[list(v) for v in values],U=u,R=r,
        paired_equal=True,differences=differences,performance_claim=False)

def archive_bytes(record):return gzip.compress(raw(record),compresslevel=9,mtime=0)
def verify_archive(blob,sha256):
    need(hashlib.sha256(blob).hexdigest()==sha256,'ARCHIVE_HASH')
    data=json.loads(gzip.decompress(blob));need(data['neutral_only'] and data['paired_equal'],'ARCHIVE_SCOPE')
    equal_events(data['U']['events'],data['R']['events']);equal_events(data['U']['internal'],data['R']['internal'])
    need(len(data['source'])==data['U']['frames']==data['R']['frames'],'ARCHIVE_LENGTH')
    for arm in ('U','R'):
        x=data[arm];need(x['cleanup'] and x['reference_equal'],'ARCHIVE_COMPLETE')
        need([r['target'] for r in x['rows']]==list(range(3,len(data['source']),2)),'ARCHIVE_TARGETS')
        for f,row in zip(x['forecasts'],x['rows']):
            need(f['index']+1==row['target'] and mae(f['output'],data['source'][row['target']-1])==row['error'],'ARCHIVE_ERROR')
    return data
