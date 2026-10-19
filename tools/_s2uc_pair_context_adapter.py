"""Local synchronous causal pair adapter; no payload-bearing context output."""
from dataclasses import dataclass
import json,math
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2tu_retained_trace import Frame

class AdapterError(ValueError):pass
@dataclass(frozen=True,slots=True)
class PerceptionSample:
    values:tuple
    profile:str
    owner:str
    stream:str
    index:int
    start_sample:int
    end_sample:int
@dataclass(frozen=True,slots=True)
class ContextReceipt:
    json_text:str

class PairContextAdapter:
    def __init__(self,arm,stream,*,hop=4800,window=4800,start_sample=0,first_ordinal=1):
        if type(arm) is not FactorRecencyArm or arm._closed or arm._forming or arm._hints:raise AdapterError('ARM_NOT_IDLE')
        if any(type(x) is not int or x<1 for x in (hop,window,first_ordinal)):raise AdapterError('CONFIG_INVALID')
        if type(start_sample) is not int or start_sample<0:raise AdapterError('CONFIG_INVALID')
        for x in (stream,arm.owner):
            if type(x) is not str or not x or len(x.encode())>96:raise AdapterError('ID_INVALID')
        self.arm=arm;self.stream=stream;self.hop=hop;self.window=window;self.start_sample=start_sample;self.first_ordinal=first_ordinal
        self.next_index=1;self.pair=[];self.intervals=[];self.closed=False;self.revision=0;self.accepted=0;self.admitted=0;self.discarded_on_error=0
    def _terminate(self):
        self.pair.clear();self.intervals.clear();self.arm.close_owner();self.closed=True
    def _receipt(self,status,indices,intervals,matches):
        data=dict(status=status,stream=self.stream,owner=self.arm.owner,profile=self.arm.profile,input_indices=indices,source_intervals=intervals,read_revision=self.revision,matches=matches)
        raw=json.dumps(data,allow_nan=False,separators=(',',':'))
        if len(raw.encode())>16384:raise AdapterError('RECEIPT_LIMIT')
        return ContextReceipt(raw)
    def _admit(self,frame):
        self.arm.form(frame);self.admitted+=1;self.revision+=1
        if (frame.ordinal-self.first_ordinal+1)%4==0:
            self.arm.close_segment(frame.segment);self.revision+=1
    def accept_perception(self,sample):
        if self.closed:raise AdapterError('CLOSED')
        try:
            if type(sample) is not PerceptionSample:raise AdapterError('PERCEPTION_TYPE_REQUIRED')
            i=sample.index
            if type(i) is not int or i!=self.next_index or i>=2**63:raise AdapterError('INDEX_GAP_OR_REORDER')
            if (sample.profile,sample.owner,sample.stream)!=(self.arm.profile,self.arm.owner,self.stream):raise AdapterError('SCOPE_CHANGED')
            start=self.start_sample+(i-1)*self.hop
            if type(sample.start_sample) is not int or type(sample.end_sample) is not int or (sample.start_sample,sample.end_sample)!=(start,start+self.window):raise AdapterError('TIME_DISCONTINUITY')
            if type(sample.values) is not tuple or len(sample.values)!=48 or any(type(x) is not float or not math.isfinite(x) for x in sample.values):raise AdapterError('VALUES_INVALID')
            ordinal=self.first_ordinal+i-1
            if ordinal>=2**63:raise AdapterError('ORDINAL_LIMIT')
            frame=Frame(sample.values,sample.profile,sample.owner,f'p{(i-1)//4+1}',ordinal)
            self.pair.append(frame);self.intervals.append((sample.start_sample,sample.end_sample));self.next_index+=1;self.accepted+=1
            if len(self.pair)==1:return None
            if self.arm.hint(self.pair[0]) is not None:raise AdapterError('HINT_PHASE')
            result=self.arm.hint(self.pair[1])
            receipt=self._receipt(result['decision'],[i-1,i],list(self.intervals),result['matches'])
            # Exact same Frame objects are admitted; no receipt or match enters form.
            for frame in self.pair:self._admit(frame)
            self.pair.clear();self.intervals.clear()
            return receipt
        except Exception:
            self.discarded_on_error=self.accepted-self.admitted
            self._terminate();raise
    def finish_story(self):
        if self.closed:raise AdapterError('CLOSED')
        try:
            receipt=None
            if self.pair:
                receipt=self._receipt('INSUFFICIENT_PAIR',[self.next_index-1],list(self.intervals),[])
                self._admit(self.pair[0]);self.pair.clear();self.intervals.clear()
            if self.arm._forming:self.arm.close_segment(self.arm._forming_segment)
            return receipt
        finally:self._terminate()
