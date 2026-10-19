"""Causal historical alignment; existing perception/memory modules stay unchanged."""
import dataclasses,json,math,hashlib
from tools._s2uc_signal_approx_adapter import SignalApproxAdapter
from tools._s2uc_pair_context_adapter import ContextReceipt
from experiments.as480.common import EPS,TAU

W=4800;H=480;BUFFER=76800
def need(ok,message):
    if not ok:raise ValueError(message)
def encoded(x):return json.dumps(x,separators=(',',':'),allow_nan=False).encode()
def vector(v):
    need(isinstance(v,tuple) and len(v)==48 and all(type(x) is float and math.isfinite(x) for x in v),'VECTOR')
    return v
def signal(v):return math.fsum(abs(x) for x in v)/48>EPS

class SampleBuffer:
    def __init__(self):self.data=bytearray(BUFFER);self.used=0;self.start=None;self.closed=False;self.peak=0
    def push(self,payload,start,end,observed_until):
        need(not self.closed,'BUFFER_CLOSED')
        need(end<=observed_until and end-start==W and len(payload)==W*4,'CAUSAL_SAMPLE_WINDOW')
        need(self.used+len(payload)<=BUFFER,'SAMPLE_BUFFER_LIMIT')
        need(self.start is None or start==self.start+self.used//4,'SAMPLE_GAP')
        if self.start is None:self.start=start
        self.data[self.used:self.used+len(payload)]=payload;self.used+=len(payload);self.peak=max(self.peak,self.used)
    def window(self,k):
        need(self.used==BUFFER and 0<=k<=30,'BANK_WINDOW')
        return memoryview(self.data)[4*k*H:4*(k*H+W)]
    def clear(self):self.used=0;self.start=None
    def close(self):self.data.clear();self.used=0;self.start=None;self.closed=True

@dataclasses.dataclass(frozen=True)
class Bank:
    originals:tuple
    values:tuple
    start:int
    digests:tuple
    def __post_init__(self):
        need(len(self.originals)==4 and len(set(self.originals))==4 and len(self.values)==31 and len(self.digests)==31,'BANK_SHAPE')
        need(all(type(i) is int and 0<i<2**63 for i in self.originals) and self.originals==tuple(range(self.originals[0],self.originals[0]+4)),'BANK_ORDINALS')
        need(type(self.start) is int and 0<=self.start<2**63 and self.start%480==0,'BANK_TIME')
        for v in self.values:vector(v)
        need(all(isinstance(x,str) and len(x)==64 and set(x)<=set('0123456789abcdef') for x in self.digests),'BANK_DIGESTS')

def make_bank(buffer,frames,project):
    need(buffer.used==BUFFER and len(frames)==4,'BANK_NOT_COMPLETE')
    values=[];digests=[]
    for k in range(31):
        view=buffer.window(k);digests.append(hashlib.sha256(view).hexdigest())
        v=frames[k//10].values if k%10==0 else project(view,buffer.start+k*H)
        values.append(vector(v))
    return Bank(tuple(f.ordinal for f in frames),tuple(values),buffer.start,tuple(digests))

def select(hint,sources,base_status):
    """Sources are (role,generation,Bank); no frame admission, labels or targets."""
    if base_status!='ABSTAIN_NO_APPROX_CONTEXT':return dict(status='NOT_ELIGIBLE',matches=[],value=None)
    need(len(sources)<=3,'SOURCE_LIMIT');need(len(hint)==2,'HINT')
    for v in hint:vector(v)
    if not all(signal(v) for v in hint):return dict(status='ABSTAIN_ALIGNMENT_LOW_SIGNAL',matches=[],value=None)
    matches=[]
    for si,(role,g,bank) in enumerate(sources):
        for k in range(21):
            a,b=bank.values[k],bank.values[k+10]
            if not signal(a) or not signal(b):continue
            factors=[]
            for exponent in (-1,0,1):
                try:equal=all(math.ldexp(bank.values[k+j*10][c],exponent)==hint[j][c] for j in range(2) for c in range(48))
                except OverflowError:equal=False
                if equal:factors.append(math.ldexp(1.,exponent))
            if factors:matches.append([si,k,factors]);need(len(matches)<=63,'MATCH_LIMIT')
    status='ABSTAIN_ALIGNMENT_NO_MATCH';value=None
    if len({m[0] for m in matches})>1:status='ABSTAIN_TRACE_AMBIGUOUS'
    elif len(matches)>1:status='ABSTAIN_ALIGNMENT_AMBIGUOUS'
    elif matches:
        si,k,factors=matches[0]
        if factors!=[1.]:status='FACTOR_CONTINUATION_NOT_SPECIFIED'
        elif k>10:status='ABSTAIN_ALIGNMENT_NO_SUCCESSOR'
        else:status='PREDICTED_ALIGNMENT';value=sources[si][2].values[k+20]
    return dict(status=status,matches=matches,value=value)

class TemporalAdapter(SignalApproxAdapter):
    def __init__(self,*args,project,enabled=True,**kw):
        super().__init__(*args,retrieval_policy='signal_approx_v1',epsilon=EPS,tau=TAU,**kw)
        self.project=project;self.enabled=enabled;self.buffer=SampleBuffer();self.banks={};self.base_forecast=None
        self.peaks=dict(vector_slots=0,sample_buffer=0,provenance=0,receipt=0,utf8=0,matches=0)
    def sources(self):
        result=[]
        for role,g,frames in self._sources():
            key=tuple(f.ordinal for f in frames);need(key in self.banks,'MISSING_BANK')
            result.append((role,g,self.banks[key]))
        return result
    def budget(self,building=None,receipt=None,old_receipt=None):
        banks=list(self.banks.values())+([building] if building is not None else [])
        unique={id(b):b for b in banks};need(len(unique)<=4,'BANK_COUNT')
        # Banks include their four originals. Count all additional live base vectors.
        vectors={id(v) for b in unique.values() for v in b.values}
        for f in list(self.arm._forming)+list(self.arm._hints)+list(self.pair):vectors.add(id(f.values))
        for _,_,fs in self._sources():
            for f in fs:vectors.add(id(f.values))
        outputs=0 if self.pending_prediction is None else 1+(self.pending_prediction.context_values is not None)
        count=len(vectors)+outputs;need(count<=128,'VECTOR_SLOT_LIMIT')
        prov=len(encoded([dict(originals=b.originals,start=b.start,digests=b.digests) for b in unique.values()]))
        need(prov<=65536,'PROVENANCE_LIMIT')
        self.peaks['vector_slots']=max(self.peaks['vector_slots'],count);self.peaks['provenance']=max(self.peaks['provenance'],prov)
        self.peaks['sample_buffer']=max(self.peaks['sample_buffer'],self.buffer.peak)
        if receipt is not None:
            n=len(receipt.encode());u=n+(len(old_receipt.encode()) if old_receipt else 0)
            need(n<=16384 and u<=32768,'RECEIPT_LIMIT');self.peaks['receipt']=max(self.peaks['receipt'],n);self.peaks['utf8']=max(self.peaks['utf8'],u)
    def accept_audio(self,sample,payload,observed_until):
        try:
            need(self.pending_prediction is None,'TARGET_NOT_RELEASED')
            need(sample.index==self.next_index,'INDEX')
            self.buffer.push(payload,sample.start_sample,sample.end_sample,observed_until)
            result=super().accept_perception(sample);self.budget();return result
        except BaseException:self._terminate();raise
    def accept_perception(self,sample):raise ValueError('AUDIO_ADMISSION_REQUIRED')
    def _admit(self,frame):
        closing=(frame.ordinal-self.first_ordinal+1)%4==0
        frames=tuple(self.arm._forming)+(frame,) if closing else None
        # Pair prediction is already frozen by _receipt; original lifecycle runs unchanged.
        super()._admit(frame)
        if closing:
            bank=make_bank(self.buffer,frames,self.project);self.budget(building=bank)
            live={tuple(f.ordinal for f in fs) for _,_,fs in self._sources()}
            if bank.originals in live:self.banks[bank.originals]=bank
            self.banks={k:v for k,v in self.banks.items() if k in live};self.buffer.clear()
    def _receipt(self,status,indices,intervals,matches):
        base=super()._receipt(status,indices,intervals,matches)
        self.base_forecast=self.pending_prediction
        if len(indices)!=2 or not self.enabled:return base
        body=json.loads(base.json_text)
        if body['status']!='ABSTAIN_NO_APPROX_CONTEXT':return base
        src=self.sources();answer=select(tuple(f.values for f in self.pair),src,body['status'])
        body['alignment']=dict(status=answer['status'],matches=answer['matches'],sources=[[r,g,list(b.originals)] for r,g,b in src])
        message=encoded(body).decode();self.budget(receipt=message,old_receipt=base.json_text)
        self.peaks['matches']=max(self.peaks['matches'],len(answer['matches']))
        self.pending_prediction=dataclasses.replace(self.pending_prediction,status=answer['status'],context_values=answer['value'],provenance_json=message)
        return ContextReceipt(message)
    def release_prediction(self):super().release_prediction();self.base_forecast=None
    def _terminate(self):
        super()._terminate()
        if hasattr(self,'banks'):self.banks.clear();self.buffer.close();self.base_forecast=None
