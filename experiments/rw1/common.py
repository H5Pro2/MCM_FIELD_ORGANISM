"""RW1 fixed observer protocol. Importing this module never creates material."""
from pathlib import Path
import math
from experiments.as480.common import need, raw, read, sha, info, digest, size, exclusive, append

ROOT=Path(__file__).resolve().parents[2]
DEV_ORDER='a179a252-51ec-48fa-be65-e5f32d41f858'
CHAT='01a0beeb-9c11-7510-95a7-f0d1409eadc7'
PROJECT='8eb30afb-7ff5-4edd-bc0a-51391db2a39d'
CONTRACT=ROOT/'docs/S2UC_RASTERWIEDERERKENNUNG_FORSCHUNGSPRUEFVERTRAG_20261019.txt'
CONTRACT_SHA='f8150752bb0008bafef95dad301c25022f4aae83b523c2ed60d3d3f2f7cc2bfe'
OLD=ROOT/'reports/s2uc/temporal-alignment-development-20261019-01'
OLD_Q=OLD/'qualification-6d248902'
OLD_SHA='cccadae5a649066941246dbd6cbe2179c4d8c36d7db28109cbd83042c57285c8'
DOC=ROOT/'reports/s2uc/raster-recognition-contract-documentation-20261019-01'
PREP=ROOT/'reports/s2uc/rw1-development-20261019-01'
TARGET=ROOT/'reports/s2uc/rw1-research-01'
SOURCE_ROOT=Path('C:/Users/TV/Documents/Codex_Workflow_Tool/data/projects/f6f2c2a07540e9c4c19834bca1bcb9be9a658572f2201b1bf7434330631c8fda/order-context')
FREQUENCIES={'A':[430,830,1470,1930],'B':[450,850,2330,2710]}
CASES=('A0','A480','A2400','B0','B480','B2400')
RECIPE=dict(kind='RW1_RESEARCH',frequencies=FREQUENCIES,cases=CASES,fs=48000,samples=19200,window=4800,hop=480,formula='RW1_SECTION_3',contract_sha256=CONTRACT_SHA)
LIMITS=dict(preparation=8388608,material=4194304,observer=3145728,closure=1048576,export=16777216,
            job=536870912,processes=2,worker_seconds=240,total_seconds=300,slots=128,matches=63,
            sample_buffer=76800,provenance=65536,receipt=16384,utf8=32768,workspace=16777216)
EXPECTED=dict(sources=2,receptor=390,receptor_completed=390,nj=390,nj_completed=390,
              arms=12,references=12,policy_admissions=132,reference_admissions=132,decisions=60,arms_closed=12,references_closed=12)

def canonical(x):return read_bytes(raw(x))
def read_bytes(x):
    import json
    return json.loads(x)
def interval(case,i):
    need(case in CASES and type(i) is int and 1<=i<=11,'INTERVAL_SCOPE')
    s='A' if i<=8 else case[0]
    a=((i-1)%4)*4800 if i<=8 else int(case[1:])+(i-9)*4800
    return s,a,a+4800
def key(case,i):return f'{case}-base-{i}'
def bank_keys(case,originals):
    need(originals in ([1,2,3,4],[5,6,7,8]),'BANK_ORIGINALS')
    block=(originals[0]-1)//4
    return [key(case,originals[k//10]) if k%10==0 else f'{case}-bank-{block}-{k}' for k in range(31)]
def vector(v):
    need(len(v)==48 and all(type(x) is float and math.isfinite(x) for x in v),'VECTOR');return tuple(v)
def preparation_size():
    return size(OLD)+size(DOC)+size(PREP)+CONTRACT.stat().st_size+size(ROOT/'experiments/rw1')
def total_size():return preparation_size()+size(TARGET)

class Budget:
    def __init__(self,folder):self.folder=Path(folder).resolve()
    def check(self,name,n):
        p=(self.folder/name).resolve();need(p.is_relative_to(self.folder),'OUTPUT_SCOPE')
        need(n>=0,'OUTPUT_SIZE')
        if self.folder.is_relative_to(PREP):
            need(preparation_size()+n<=LIMITS['preparation']-65536,'PREPARATION_LIMIT')
        else:
            need(self.folder==TARGET,'OUTPUT_TARGET')
            group=Path(name).parts[0];need(group in ('material','observer','closure'),'OUTPUT_PARTITION')
            need(size(self.folder/group)+n<=LIMITS[group],'PARTITION_'+group)
        need(total_size()+n<=LIMITS['export']-32768,'TOTAL_EXPORT')
        return p
    def save(self,name,data):
        payload=data if isinstance(data,bytes) else raw(data)
        if self.folder==TARGET and name.startswith('observer/'):
            leaf=Path(name).name
            cap=327680 if leaf=='request.json' else 393216 if leaf=='evaluation.json' else 65536 if leaf=='independent-evaluation.json' else 98304 if any(leaf==c+'-'+a+'.json' for c in CASES for a in ('N','T')) else 49152
            need(len(payload)<=cap,'OBSERVER_RECORD_SIZE')
        exclusive(self.check(name,len(payload)),payload)
    def event(self,name,data):
        payload=raw(data)
        if name=='observer/counts.jsonl':
            need(len(payload)<=512,'COUNTER_EVENT_SIZE')
            p=self.folder/name;need((p.stat().st_size if p.exists() else 0)+len(payload)<=990720,'COUNTER_EXPORT')
        p=self.check(name,len(payload));append(p,data)

class Ledger:
    def __init__(self,budget):
        self.budget=budget;self.counts={k:0 for k in EXPECTED}
        need(not (budget.folder/'observer/counts.jsonl').exists(),'LEDGER_EXISTS');self.event('BEGIN')
    def event(self,event):self.budget.event('observer/counts.jsonl',dict(event=event,counts=self.counts))
    def bump(self,k):
        need(k in EXPECTED and self.counts[k]<EXPECTED[k],'COUNT_LIMIT:'+k)
        self.counts[k]+=1;self.event(k)
    def complete(self):need(self.counts==EXPECTED,'FULL_COUNTS')
