"""Prepared single neutral size workflow. Invoked only behind entry formal_gate."""
import dataclasses,json,math
from pathlib import Path
from .core import TemporalAdapter,need,W,H
from .projector import Projector
from . import oracle
from .entry import save,OUT
from experiments.as480.common import read,info,sha,append
from experiments.as480.oracle import decide as base_decide
from tools._s2uc_factor_recency import FactorRecencyArm
from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample
from tools.s2uc_continuous_comparison import state

NEUTRAL={'A':[310,680,1390,1750],'B':[330,700,2180,2490]}
CASES=(('A0','A',0),('A480','A',480),('A2400','A',2400),('B0','B',0),('B480','B',480),('B2400','B',2400))
class Ledger:
    def __init__(self,folder):
        self.folder=folder;self.counts=dict(sources=0,receptor=0,nj=0,arms=0,references=0,policy_admissions=0,reference_admissions=0,decisions=0,arms_closed=0,references_closed=0)
        need(not (folder/'counts.jsonl').exists(),'COUNTS_EXISTS');self.event('BEGIN')
    def event(self,event):append(self.folder/'counts.jsonl',dict(event=event,counts=self.counts))
    def bump(self,key):self.counts[key]+=1;self.event(key)

class Material:
    def __init__(self,folder,ledger):self.folder=folder;self.ledger=ledger;self.projector=Projector();self.manifest={}
    def emit(self,name,payload,start):
        self.ledger.bump('receptor');v=self.projector(payload,start);self.ledger.bump('nj')
        row=dict(start=start,pcm_sha256=__import__('hashlib').sha256(payload).hexdigest(),projection=self.projector.last)
        need(len(json.dumps(row).encode())<=8192,'PROJECTION_EXPORT');save(self.folder,'material/'+name+'.json',row)
        p=self.folder/'material'/ (name+'.json');self.manifest[name]=info(p);return v
    def prepare(self):
        from experiments.as480.material import source_pcm
        save(self.folder,'neutral-recipe.json',dict(kind='NEUTRAL_ONLY',frequencies=NEUTRAL,cases=CASES))
        sources={}
        for key,freq in NEUTRAL.items():
            self.ledger.bump('sources');sources[key]=source_pcm(freq);save(self.folder,'material/'+key+'.f32le',sources[key])
        for case,src,shift in CASES:
            for i in range(1,12):
                source='A' if i<=8 else src;begin=((i-1)%4)*W if i<=8 else shift+(i-9)*W
                self.emit(f'{case}-base-{i}',sources[source][4*begin:4*(begin+W)],(i-1)*W)
            for block in (0,1):
                for k in range(31):
                    if k%10:self.emit(f'{case}-bank-{block}-{k}',sources['A'][4*k*H:4*(k*H+W)],block*4*W+k*H)
        need(self.projector.calls==390 and self.projector.nj_calls==390,'390_CALLS')
        save(self.folder,'material/manifest.json',self.manifest)
    def row(self,name):
        p=self.folder/'material'/(name+'.json');need(info(p)==self.manifest[name],'MATERIAL_HASH');return read(p)
    def historical(self,case,payload,start):
        block,k=divmod(start,4*W);k//=H;need(block in (0,1) and 0<=k<=30 and k%10,'HISTORICAL_INTERVAL')
        row=self.row(f'{case}-bank-{block}-{k}')
        need(row['start']==start and row['pcm_sha256']==__import__('hashlib').sha256(payload).hexdigest(),'HISTORICAL_PCM_LINK')
        return tuple(row['projection']['values'])

def run(folder):
    """No caller may bypass the formal-use evidence check."""
    from .entry import formal_gate
    formal_gate()
    folder=Path(folder);ledger=Ledger(folder);material=Material(folder,ledger);material.prepare();peaks={};results={}
    for case,src,shift in CASES:
        sources={s:(folder/'material'/f'{s}.f32le').read_bytes() for s in ('A','B')}
        for enabled in (False,True):
            name='T' if enabled else 'N';records=[];ledger.bump('arms');ledger.bump('references')
            profile=material.row(f'{case}-base-1')['projection']['profile_digest']
            a=TemporalAdapter(FactorRecencyArm(profile,'owner'),'stream',project=lambda p,t:material.historical(case,p,t),enabled=enabled)
            ref=PairContextAdapter(FactorRecencyArm(profile,'owner'),'stream');frozen=None
            try:
                for i in range(1,12):
                    # Require a frozen decision BEFORE reading target values or raw target bytes.
                    if i>=3 and i%2:need(a.pending_prediction is not None and a.pending_prediction.target_index==i and frozen is not None,'FUTURE_GATE')
                    row=material.row(f'{case}-base-{i}');values=tuple(row['projection']['values'])
                    sample=PerceptionSample(values,profile,'owner','stream',i,(i-1)*W,i*W)
                    if a.pending_prediction:
                        forecast=dataclasses.asdict(a.pending_prediction)
                        base=base_decide(frozen['stock'],frozen['hint'],'signal_approx_v1',a.epsilon,a.tau)
                        selected=oracle.decide(frozen['hint'],frozen['bank_values'],base['status']) if enabled and base['status']=='ABSTAIN_NO_APPROX_CONTEXT' else None
                        expected_context=selected['value'] if selected else base['context'];expected_status=selected['status'] if selected else base['prediction']
                        need(forecast['status']==expected_status and forecast['context_values']==expected_context and forecast['persistence_values']==base['persistence'],'INDEPENDENT_DECISION')
                        receipt=json.loads(forecast['provenance_json']);need(receipt['status']==base['status'] and receipt['matches']==base['matches'],'BASE_RECEIPT')
                        if selected:need(receipt['alignment']['matches']==selected['matches'],'ALIGNMENT_RECEIPT')
                        output=expected_context if expected_context is not None else base['persistence']
                        records.append(dict(target=i,forecast=forecast,actual=values,error=math.fsum(abs(x-y) for x,y in zip(output,values))/48,
                            independent=True,read_before_target=True,bank_originals=frozen['bank_originals']))
                        ledger.bump('decisions');a.release_prediction()
                    if i%2==0:
                        stock=[dict(role=r,generation=g,formation=fs[0].segment,ordinals=[f.ordinal for f in fs],values=[f.values for f in fs]) for r,g,fs in a._sources()]
                        bank_sources=a.sources()
                        frozen=dict(stock=stock,hint=(a.pair[0].values,values),bank_values=[dict(values=b.values) for _,_,b in bank_sources],bank_originals=[b.originals for _,_,b in bank_sources])
                    source='A' if i<=8 else src;begin=((i-1)%4)*W if i<=8 else shift+(i-9)*W
                    payload=sources[source][4*begin:4*(begin+W)]
                    ledger.bump('policy_admissions');a.accept_audio(sample,payload,i*W)
                    ledger.bump('reference_admissions');ref.accept_perception(sample)
                    need(state(a.arm)==state(ref.arm),'CORE_REFERENCE')
                a.finish_story();ref.finish_story();need(not a.banks and a.buffer.closed and a.pending_prediction is None,'CLEANUP')
                results[case+'-'+name]=dict(records=records,resources=a.peaks,cleanup=True)
                save(folder,case+'-'+name+'.json',results[case+'-'+name])
                for k,v in a.peaks.items():peaks[k]=max(peaks.get(k,0),v)
            finally:
                if not a.closed:a._terminate()
                if not ref.closed:ref._terminate()
                ledger.bump('arms_closed');ledger.bump('references_closed')
    need(ledger.counts==dict(sources=2,receptor=390,nj=390,arms=12,references=12,policy_admissions=132,reference_admissions=132,decisions=60,arms_closed=12,references_closed=12),'FULL_COUNTS')
    save(folder,'neutral-result.json',dict(counts=ledger.counts,peaks=peaks,workspace_peak=material.projector.peak_workspace,scientific_verdict=None,neutral_only=True))
