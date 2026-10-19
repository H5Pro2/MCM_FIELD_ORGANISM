"""RW1 supervised material/observer connection; qualified core stays untouched."""
import dataclasses,json
from .common import *

class Material:
    def __init__(self,budget,ledger):self.budget=budget;self.ledger=ledger;self.manifest={}
    def prepare(self,permit):
        from .gateway import capability
        capability(self.budget.folder,permit)
        from experiments.as480.material import source_pcm
        from experiments.temporal_alignment.projector import Projector
        self.projector=Projector(on_event=self.ledger.bump)
        sources={}
        for s,f in FREQUENCIES.items():
            self.ledger.bump('sources');sources[s]=source_pcm(f);self.budget.save('material/'+s+'.f32le',sources[s])
        def emit(name,s,a,b,start):
            payload=sources[s][4*a:4*b];self.projector(payload,start)
            row=dict(source=s,source_interval=[a,b],source_sha256=digest(sources[s]),start=start,end=start+4800,
                     pcm_sha256=digest(payload),projection=self.projector.last)
            need(len(raw(row))<=8192,'PROJECTION_EXPORT');self.budget.save('material/'+name+'.json',row)
            self.manifest[name]=info(self.budget.folder/'material'/ (name+'.json'))
        for c in CASES:
            for i in range(1,12):
                s,a,b=interval(c,i);emit(key(c,i),s,a,b,(i-1)*4800)
            for block in (0,1):
                for k in range(31):
                    if k%10:emit(f'{c}-bank-{block}-{k}','A',k*480,k*480+4800,block*19200+k*480)
        self.budget.save('material/recipe.json',RECIPE)
        self.budget.save('material/manifest.json',dict(projections=self.manifest,sources={s:info(self.budget.folder/'material'/ (s+'.f32le')) for s in sources},recipe_sha256=sha(self.budget.folder/'material/recipe.json')))
    def row(self,name):
        p=self.budget.folder/'material'/(name+'.json');need(info(p)==self.manifest[name],'PROJECTION_HASH');return read(p)
    def read_input(self,case,i):
        row=self.row(key(case,i));s,a,b=interval(case,i)
        with (self.budget.folder/'material'/(s+'.f32le')).open('rb') as f:f.seek(4*a);payload=f.read(4*(b-a))
        need(digest(payload)==row['pcm_sha256'] and row['source_interval']==[a,b] and row['start']==(i-1)*4800,'INPUT_LINEAGE')
        return row,payload
    def historical(self,case,payload,start):
        block,k=divmod(start,19200);need(k%480==0,'HISTORY_GRID');k//=480
        need(block in (0,1) and 0<=k<=30 and k%10,'HISTORY_SCOPE')
        row=self.row(f'{case}-bank-{block}-{k}')
        need(row['start']==start and digest(payload)==row['pcm_sha256'],'HISTORY_LINEAGE')
        return vector(row['projection']['values'])

class Reader:
    def __init__(self,material,case):self.material=material;self.case=case;self.events=[];self.next=1;self.frozen={}
    def freeze(self,i,forecast,frozen):
        need(i==self.next and i in (3,5,7,9,11) and i not in self.frozen,'FREEZE_ORDER')
        need(forecast['target_index']==i,'FREEZE_TARGET')
        token=digest(raw(dict(forecast=forecast,frozen=frozen)))
        self.frozen[i]=token;self.events.append(dict(event='FREEZE',target=i,token=token));return token
    def take(self,i):
        need(i==self.next,'READ_ORDER')
        if i in (3,5,7,9,11):need(i in self.frozen,'FUTURE_BEFORE_FREEZE')
        # Gate executes before projection JSON and before source-window bytes.
        row,payload=self.material.read_input(self.case,i)
        self.events.append(dict(event='READ',target=i,freeze=self.frozen.get(i),pcm_sha256=row['pcm_sha256']))
        self.next+=1;return row,payload

def run_arm(case,enabled,material,ledger):
    from experiments.temporal_alignment.core import TemporalAdapter
    from tools._s2uc_factor_recency import FactorRecencyArm
    from tools._s2uc_pair_context_adapter import PairContextAdapter,PerceptionSample
    from tools.s2uc_continuous_comparison import state
    reader=Reader(material,case);records=[];states=[];frozen=None
    # Profile is invariant metadata, not a target read.
    profile=material.row(key(case,1))['projection']['profile_digest']
    a=TemporalAdapter(FactorRecencyArm(profile,'owner'),'stream',project=lambda p,t:material.historical(case,p,t),enabled=enabled)
    ref=PairContextAdapter(FactorRecencyArm(profile,'owner'),'stream');ledger.bump('arms');ledger.bump('references')
    def snapshot():
        result=[]
        for role,g,frames in a._sources():
            originals=[f.ordinal for f in frames];bank=a.banks[tuple(originals)]
            result.append(dict(role=role,generation=g,formation=frames[0].segment,ordinals=originals,
                bank_start=bank.start,bank_digests=list(bank.digests)))
        return result
    def bank_hash():return digest(raw([dict(role=s[0],generation=s[1],originals=s[2].originals,start=s[2].start,values=s[2].values,digests=s[2].digests) for s in a.sources()]))
    try:
        for i in range(1,12):
            row,payload=reader.take(i);values=vector(row['projection']['values'])
            if a.pending_prediction is not None:
                forecast=dataclasses.asdict(a.pending_prediction)
                records.append(dict(target=i,forecast=canonical(forecast),frozen=frozen,freeze_token=reader.frozen[i],actual=list(values)))
                ledger.bump('decisions');a.release_prediction()
            if i%2==0:frozen=dict(stock=snapshot(),hint_indices=[i-1,i],read_revision=a.revision)
            sample=PerceptionSample(values,profile,'owner','stream',i,(i-1)*4800,i*4800)
            ledger.bump('policy_admissions');a.accept_audio(sample,payload,i*4800)
            ledger.bump('reference_admissions');ref.accept_perception(sample)
            need(state(a.arm)==state(ref.arm),'REFERENCE_STATE')
            states.append(dict(index=i,core=digest(raw(state(a.arm))),reference=digest(raw(state(ref.arm))),banks=bank_hash()))
            if i%2==0:reader.freeze(i+1,canonical(dataclasses.asdict(a.pending_prediction)),frozen)
        a.finish_story();ref.finish_story()
        need(not a.banks and a.buffer.closed and a.pending_prediction is None and a.closed and ref.closed,'CLEANUP')
        result=dict(records=records,states=states,events=reader.events,resources=a.peaks,cleanup=True)
    finally:
        if not a.closed:a._terminate()
        if not ref.closed:ref._terminate()
        ledger.bump('arms_closed');ledger.bump('references_closed')
    return result

def run(folder,permit):
    from .gateway import enter
    enter(folder,permit)  # Includes one-time worker entry, before any material.
    budget=Budget(folder);ledger=Ledger(budget);material=Material(budget,ledger);material.prepare(permit)
    for c in CASES:
        n=run_arm(c,False,material,ledger);t=run_arm(c,True,material,ledger)
        need(n['states']==t['states'],'NT_CORE_BANK_STATES')
        budget.save('observer/'+c+'-N.json',n);budget.save('observer/'+c+'-T.json',t)
    ledger.complete()
    from .audit import reconstruct,independent_verdict,check_metrics
    from .evaluate import report
    archives=reconstruct(folder);result=report(archives);independent=independent_verdict(archives)
    need({k:result[k] for k in ('verdict','criteria','means')}==independent,'INDEPENDENT_VERDICT')
    checked=check_metrics(archives,result)
    budget.save('observer/evaluation.json',result);budget.save('observer/independent-evaluation.json',dict(**independent,verification=checked))
    budget.save('observer/result.json',dict(counts=ledger.counts,workspace_peak=material.projector.peak_workspace,
                independent_decisions=60,independent_evaluation=True,cleanup=True,verdict=result['verdict']))
