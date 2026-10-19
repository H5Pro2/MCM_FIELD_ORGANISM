"""AS480 boundaries, durable counters and bounded exclusive artifact writes."""
import hashlib,json,os,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PREP=ROOT/'reports/s2uc/as480-neutral-qualification-20261019-01'
RESEARCH=ROOT/'reports/s2uc/as480-comparison-01'
CONTRACT=ROOT/'docs/S2UC_AS480_AUDIO_FENSTERVERSATZ_PRUEFVERTRAG_20261019.txt'
CONTRACT_SHA='a63a33c6a844848933c1b55e93a2c63923d59284001282cec0fb6a6f4caee325'
EPS=float.fromhex('0x1.1a414d9cf9967p-15');TAU=1/32
LIMITS=dict(job=536870912,processes=2,worker_seconds=240,total_seconds=300,
            export=16777216,preparation=8388608,material=4194304,observer=3145728,closure=1048576,
            frames=18,outputs=2,combined=20,receipt=16384,utf8=32768)
CASES=('A0','A480','B0','B480')
NEUTRAL={'A':[260,620,1040,1580],'B':[280,640,2020,2260]}
RECIPE={'A':[380,740,1260,1820],'B':[400,760,2140,2380]}
COUNTERS=('sources','receptor_started','receptor_completed','nj_started','nj_completed',
          'arms_started','arms_completed','arms_closed','reference_started','reference_completed','reference_closed',
          'policy_admissions','reference_admissions','decisions_started','decisions_completed')
def need(ok,why):
    if not ok:raise ValueError(why)
def raw(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def read(p):return json.loads(Path(p).read_bytes())
def digest(b):return hashlib.sha256(b).hexdigest()
def sha(p):return digest(Path(p).read_bytes())
def size(p):return sum(x.stat().st_size for x in Path(p).rglob('*') if x.is_file()) if Path(p).exists() else 0
def info(p):return dict(bytes=p.stat().st_size,sha256=sha(p))
def exclusive(p,data):
    if not isinstance(data,bytes):data=raw(data)
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
def append(p,data):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('ab') as f:f.write(raw(data));f.flush();os.fsync(f.fileno())
class Ledger:
    def __init__(self,folder,kind):
        self.folder=Path(folder);self.counts={k:0 for k in COUNTERS};self.kind=kind
        self.path=self.folder/'execution.jsonl'
        need(not self.path.exists(),'LEDGER_EXISTS');self.event('BEGIN')
    def event(self,event,**kw):
        append(self.path,dict(event=event,kind=self.kind,counts=self.counts,monotonic=time.monotonic(),**kw))
    def bump(self,name):self.counts[name]+=1;self.event(name)
class Budget:
    def __init__(self,folder):self.folder=Path(folder)
    def check(self,p,n,final=False):
        p=Path(p).resolve();need(p.is_relative_to(self.folder.resolve()),'OUTPUT_PATH')
        group='material' if p.is_relative_to((self.folder/'material').resolve()) else 'closure' if final else 'observer'
        current=size(self.folder/'material') if group=='material' else sum(x.stat().st_size for x in self.folder.rglob('*') if x.is_file() and not x.is_relative_to(self.folder/'material'))
        need(n<=LIMITS[group] and current+n<= (LIMITS['observer']+LIMITS['closure'] if final else LIMITS[group]),'OUTPUT_'+group.upper())
        total=size(PREP)+(0 if self.folder.is_relative_to(PREP) else size(self.folder))
        need(total+n<=LIMITS['export']- (0 if final else 65536),'EXPORT_LIMIT')
        if self.folder.is_relative_to(PREP):need(size(PREP)+n<=LIMITS['preparation']-(0 if final else 65536),'PREPARATION_LIMIT')
    def save(self,name,x,final=False):
        data=x if isinstance(x,bytes) else raw(x);p=self.folder/name
        self.check(p,len(data),final);exclusive(p,data)

def authorize(mode,auth,binding_sha,target):
    need(mode in ('neutral','research'),'MODE')
    if mode=='neutral':need(auth is None,'NEUTRAL_AUTH_FORBIDDEN');return
    need(isinstance(auth,dict) and set(auth)=={'status','mode','binding_sha256','target','contract_sha256'},'RESEARCH_AUTH_REQUIRED')
    need(auth==dict(status='AUTHORIZED_ONCE',mode='research',binding_sha256=binding_sha,
                   target=str(RESEARCH),contract_sha256=CONTRACT_SHA) and Path(target)==RESEARCH,'RESEARCH_AUTH_MISMATCH')
