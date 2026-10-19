"""Cumulative time/export controls and fresh-state case execution."""
import hashlib
import json
import time
from pathlib import Path

LIMITS=dict(total_seconds=57600,worker_seconds=54000,completion_reserve=3600,job=536870912,
    preparation=8388608,source_total=2097152,source_case=32768,archives=33554432,gzip=524288,
    encoded=4194304,dictionary=4194304,record=262144,nodes=65536,edges=262144,indices=65536,
    collections=16,temp=67108864,export=67108864,administration=2097152,closure=1048576)


def raw(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()


class Ledger:
    def __init__(self,folder,started,prep_bytes,clock=time.monotonic,limits=None):
        self.folder=Path(folder);self.started=started;self.prep_bytes=prep_bytes;self.clock=clock
        self.limits=LIMITS.copy() if limits is None else limits.copy();self.entries={};self.final=False
        if prep_bytes>self.limits['preparation']:raise ValueError('PREPARATION_LIMIT')
    def check(self):
        elapsed=self.clock()-self.started
        if elapsed>self.limits['total_seconds']:raise TimeoutError('GLOBAL_TIMEOUT')
        if not self.final and elapsed>self.limits['worker_seconds']:raise TimeoutError('WORKER_DEADLINE')
        files=[p for p in self.folder.rglob('*') if p.is_file()]
        if self.prep_bytes+sum(p.stat().st_size for p in files)>self.limits['export']:raise ValueError('EXPORT_LIMIT')
        if sum(p.stat().st_size for p in files if p.name.endswith('.partial'))>self.limits['temp']:raise ValueError('TEMP_LIMIT')
        groups=dict(source=0,archive=0,admin=0,closure=0)
        for p in files:
            if p.name.endswith('.partial'):continue
            category=self.entries.get(str(p.resolve()),('admin',0))[0]
            groups[category]+=p.stat().st_size
        for category,limit in [('source','source_total'),('archive','archives'),('admin','administration'),('closure','closure')]:
            if groups[category]>self.limits[limit]:raise ValueError('CATEGORY_LIMIT:'+category)
    def register(self,path,category):
        path=Path(path).resolve()
        if not path.is_relative_to(self.folder.resolve()) or category not in ('source','archive','admin','closure'):raise ValueError('LEDGER_PATH')
        size=path.stat().st_size
        individual={'source':'source_case','archive':'gzip','admin':'administration','closure':'closure'}[category]
        if size>self.limits[individual]:raise ValueError('FILE_LIMIT:'+category)
        key=str(path);new=self.entries|{key:(category,size)}
        group={'source':'source_total','archive':'archives','admin':'administration','closure':'closure'}[category]
        if sum(n for c,n in new.values() if c==category)>self.limits[group]:raise ValueError('CATEGORY_LIMIT:'+category)
        previous=self.entries;self.entries=new
        try:self.check()
        except Exception:self.entries=previous;raise
        return hashlib.sha256(path.read_bytes()).hexdigest()
    def write(self,name,value,category='admin'):
        self.check();path=self.folder/name
        if path.exists():raise FileExistsError(path)
        data=raw(value)
        cap=self.limits[{'source':'source_case','archive':'gzip','admin':'administration','closure':'closure'}[category]]
        if len(data)>cap:raise ValueError('FILE_LIMIT:'+category)
        temp=path.with_name(path.name+'.partial')
        try:
            with temp.open('xb') as f:f.write(data)
            self.check();temp.replace(path)
            return self.register(path,category)
        except Exception:
            temp.unlink(missing_ok=True);path.unlink(missing_ok=True);raise


def execute(cases,run_case,ledger,expected):
    if len(cases)!=len(expected) or [x[0] for x in cases]!=expected or len(set(expected))!=len(expected):raise ValueError('SERIES_CASES')
    outputs=[]
    try:
        for number,material in cases:
            ledger.check();result=run_case(number,material,ledger)
            if not result['cleanup'] or result['replicate']!=number:raise ValueError('SERIES_CLEANUP_OR_ID')
            outputs.append(result);ledger.check()
        if len(outputs)!=len(expected):raise ValueError('SERIES_INCOMPLETE')
        return outputs
    finally:
        for path in ledger.folder.glob('*.partial'):path.unlink()


def policy_case(number,source,ledger,*,neutral=False):
    from tools import _s2uc_ura1_v2_engine as engine
    from tools import _s2uc_ura1_delta_encode as codec
    from tools._s2uc_ura1_v2_fused import finish,live_sequences
    from tools._s2uc_ura1_delta_fast_decode import verify
    from tools._s2uc_ura1_capture_integrity import manifest
    from tools._s2uc_ura1_v2_sources import frames
    values=frames(source);encoded=raw(values)
    if len(values)>128 if neutral else len(values)!=1024:raise ValueError('CASE_FRAME_SCOPE')
    engine.VALIDATE=lambda v:None if raw(v)==encoded else (_ for _ in ()).throw(ValueError('CASE_MATERIAL'))
    engine.CHECKPOINT=lambda *args:ledger.check()
    arms=[];original=engine.create
    def create(mode):
        arm=original(mode);arms.append(arm);return arm
    engine.create=create
    try:
        with codec.store(ledger.folder) as owner:
            u=engine.run_arm(values,'U',trace=True);r=engine.run_arm(values,'R',trace=True)
            record=dict(neutral_only=neutral,source=[list(v) for v in values],U=u,R=r,paired_equal=True,differences=[],performance_claim=False)
            expected,checks=finish(record,live_sequences(record),build=True);proof=manifest(record)
            ledger.write(f'case-{number:02d}-capture.json',proof)
            path=ledger.folder/f'case-{number:02d}.delta.json.gz'
            codec.write_archive(record,path,expected);ledger.register(path,'archive');ledger.check()
            verified=verify(path.read_bytes(),proof,expected);ledger.check()
            rows=[]
            for uf,rf,ur,rr in zip(u['forecasts'],r['forecasts'],u['rows'],r['rows']):
                target=ur['target'];hs=[h for h in uf['receipt']['hypotheses'] if h['eligible']]
                warm=sum(h['ec'] is not None for h in hs)
                klass='none' if not hs else 'cold' if warm==0 else 'warm' if warm==len(hs) else 'mixed'
                uc,rc=uf['selected'],rf['selected']
                choice='both_persistence' if uc is None and rc is None else 'mixed' if (uc is None)!=(rc is None) else 'same_context' if uc==rc else 'different_context'
                rows.append(dict(target=target,U=ur['error'],R=rr['error'],cue=('X' if source['ids'][target-3]==0 else 'Y') if target%4==3 else None,
                    eligible=min(2,len(hs)),warm=klass,same_output=uf['output']==rf['output'],choice=choice))
            del record,u,r
        if not owner.closed or owner.pool.nodes or owner.deltas:raise ValueError('STORE_CLEANUP')
        return dict(replicate=number,orientation=(number-1)%2,complete=True,rows=rows,cleanup=True,
            source_neutral=neutral,integrity=verified['status'],counts=checks['counts'])
    finally:
        engine.create=original;engine.CHECKPOINT=lambda *args:None
        engine.VALIDATE=lambda _:(_ for _ in ()).throw(ValueError('UNARMED'))
        for arm in arms:
            if not arm.closed:arm._terminate()
        if any(not a.closed or any(a.bank) for a in arms):raise ValueError('ARM_CLEANUP')
