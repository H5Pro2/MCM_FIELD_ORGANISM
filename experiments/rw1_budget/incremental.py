"""Separate fail-closed incremental export ledger; no RW1 integration or restart."""
import os,json,time,hashlib,msvcrt
from pathlib import Path
from contextlib import contextmanager
from .workload import BASE,PACKAGE,materialize_action

CAPS=dict(preparation=8388608,material=4194304,observer=3145728,closure=1048576,total=16777216)
RESERVE=dict(preparation=65536,total=32768,transaction=2048)
CONTROL='observer/_budget/'
def require(ok,why):
    if not ok:raise ValueError(why)
def encode(x):return (json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode()
def hashbytes(x):return hashlib.sha256(x).hexdigest()
def stamp(p):
    s=p.stat();return dict(bytes=s.st_size,mtime=s.st_mtime_ns)

class JournalBudget:
    """All cooperative writers share a lock and durable BEGIN/COMMIT journal.

    Foreign additions are detected by independent reconciliation, not by scanning
    every write. This requires exclusive ownership of output roots. Any failed
    transaction poisons this session; journal recovery/retry is deliberately absent.
    """
    def __init__(self,target,inherited=(),*,create=False,caps=None,expected_snapshot=None):
        self.target=Path(target).resolve();self.inherited=tuple(Path(x).resolve() for x in inherited)
        self.caps=dict(CAPS if caps is None else caps);self.dead=False
        self.metrics=dict(scan_calls=0,scan_seconds=0.,serialization_calls=0,serialization_seconds=0.,write_calls=0,write_seconds=0.,journal_reads=0)
        self.control=self.target/CONTROL;self.snapshot=self.control/'snapshot.json';self.journal=self.control/'journal.jsonl';self.lockpath=self.control/'lock.bin'
        self.seq=0;self.pending=None;self.offset=0;self.chain='0'*64
        if create:self._create()
        raw_snapshot=self.snapshot.read_bytes();self.snapshot_hash=hashbytes(raw_snapshot)
        require(expected_snapshot is None or self.snapshot_hash==expected_snapshot,'SNAPSHOT_HASH')
        data=json.loads(raw_snapshot);require(data['caps']==self.caps and data['target']==str(self.target) and data['inherited_roots']==list(map(str,self.inherited)),'LEDGER_SCOPE')
        self.files=data['files'];self.base=data['base'];self.snapshot_stamp=stamp(self.snapshot)
        self.totals=dict(preparation=sum(x['bytes'] for group in self.base for x in group.values()),material=0,observer=0,closure=0)
        for n,s in self.files.items():self.totals[n.split('/')[0]]+=s['bytes']
        self.totals['observer']+=len(raw_snapshot)+1
        with self._locked():self._sync();require(self.pending is None,'INCOMPLETE_TRANSACTION')

    def _scan(self,root):
        t=time.perf_counter();self.metrics['scan_calls']+=1
        try:
            result={}
            if root.exists():
                for p in root.rglob('*'):
                    require(not p.is_symlink(),'UNEXPECTED_LINK')
                    if p.is_file():result[p.relative_to(root).as_posix()]=stamp(p)
            return result
        finally:self.metrics['scan_seconds']+=time.perf_counter()-t
    def _serialize(self,x):
        t=time.perf_counter()
        try:return encode(x)
        finally:self.metrics['serialization_calls']+=1;self.metrics['serialization_seconds']+=time.perf_counter()-t
    def _write(self,p,data,mode):
        t=time.perf_counter();self.metrics['write_calls']+=1
        try:
            p.parent.mkdir(parents=True,exist_ok=True)
            with p.open(mode) as f:
                written=f.write(data);require(written==len(data),'PARTIAL_WRITE');f.flush();os.fsync(f.fileno())
        finally:self.metrics['write_seconds']+=time.perf_counter()-t
    def _create(self):
        require(not self.control.exists(),'CONTROL_ALREADY_EXISTS')
        files=self._scan(self.target);require(all(n.split('/')[0] in ('material','observer','closure') for n in files),'INITIAL_PARTITION')
        base=[self._scan(p) for p in self.inherited]
        data=self._serialize(dict(version=1,target=str(self.target),inherited_roots=list(map(str,self.inherited)),caps=self.caps,files=files,base=base))
        sizes=dict(preparation=sum(x['bytes'] for group in base for x in group.values()),material=0,observer=len(data)+1,closure=0)
        for n,s in files.items():sizes[n.split('/')[0]]+=s['bytes']
        self._limits(sizes)
        self._write(self.snapshot,data,'xb');self._write(self.lockpath,b'L','xb');self._write(self.journal,b'','xb')
    def _limits(self,totals):
        for group in ('preparation','material','observer','closure'):
            require(totals[group]<=self.caps[group]-(RESERVE['preparation'] if group=='preparation' else 0),'LIMIT_'+group)
        require(sum(totals.values())<=self.caps['total']-RESERVE['total'],'LIMIT_total')

    @contextmanager
    def _locked(self):
        require(not self.dead,'LEDGER_POISONED')
        with self.lockpath.open('r+b') as lock:
            until=time.monotonic()+5
            while True:
                try:lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);break
                except OSError:
                    require(time.monotonic()<until,'LOCK_TIMEOUT');time.sleep(.005)
            try:yield
            except BaseException:self.dead=True;raise
            finally:lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)

    def _sync(self):
        require(stamp(self.snapshot)==self.snapshot_stamp,'SNAPSHOT_CHANGED')
        require(self.journal.stat().st_size>=self.offset,'JOURNAL_TRUNCATED')
        with self.journal.open('rb') as f:f.seek(self.offset);tail=f.read()
        self.metrics['journal_reads']+=1
        require(not tail or tail.endswith(b'\n'),'PARTIAL_JOURNAL')
        for line in tail.splitlines(keepends=True):
            item=json.loads(line);require(item['previous']==self.chain,'JOURNAL_CHAIN')
            if item['kind']=='BEGIN':
                require(self.pending is None and item['seq']==self.seq+1,'TRANSACTION_ORDER');self.pending=item
            elif item['kind']=='COMMIT':
                require(self.pending is not None and item['seq']==self.pending['seq'],'COMMIT_WITHOUT_BEGIN')
                name=self.pending['name'];new=item['stamp'];old=self.files.get(name,dict(bytes=0))
                require(new['bytes']==old['bytes']+self.pending['bytes'],'COMMIT_SIZE')
                self.files[name]=new;self.totals[name.split('/')[0]]+=new['bytes']-old['bytes']
                self.seq=item['seq'];self.pending=None
            else:raise ValueError('JOURNAL_KIND')
            self.totals['observer']+=len(line);self.offset+=len(line);self.chain=hashbytes(line)
        self._limits(self.totals)

    def _record(self,kind,**fields):
        data=self._serialize(dict(kind=kind,previous=self.chain,**fields));self._write(self.journal,data,'ab');self._sync();return len(data)

    def write(self,name,data,*,append=False,role='worker'):
        # Serialization is measured independently of data/journal writes.
        payload=data if isinstance(data,bytes) else self._serialize(data)
        with self._locked():
            self._sync();require(self.pending is None,'INCOMPLETE_TRANSACTION')
            require(role in ('worker','supervisor'),'WRITER_ROLE')
            p=(self.target/name).resolve()
            require(p.is_relative_to(self.target) and not name.startswith(CONTROL) and len(name.encode())<=160,'OUTPUT_SCOPE')
            require(p.relative_to(self.target).as_posix()==name,'CANONICAL_PATH')
            group=name.split('/')[0];require(group in ('material','observer','closure'),'PARTITION')
            require(not any(x.is_symlink() for x in [p,*p.parents] if x.is_relative_to(self.target)),'OUTPUT_LINK')
            old=self.files.get(name)
            if old is None:require(not p.exists(),'UNACCOUNTED_FILE')
            else:
                require(append,'EXCLUSIVE_EXISTS');require(p.is_file() and stamp(p)==old,'EXISTING_FILE_CHANGED')
            size_after=(old['bytes'] if old else 0)+len(payload)
            leaf=p.name
            if name=='observer/counts.jsonl':require(append and len(payload)<=512 and size_after<=990720,'COUNTER_SIZE')
            elif group=='material':
                require(not append,'MATERIAL_APPEND')
                if leaf.startswith('projection-'):require(size_after<=8192,'PROJECTION_SIZE')
            elif group=='observer':
                cap=327680 if leaf=='request.json' else 393216 if leaf=='evaluation.json' else 65536 if leaf=='independent-evaluation.json' else 98304 if leaf.endswith(('-N.json','-T.json')) else 49152
                require(size_after<=cap,'OBSERVER_FILE_SIZE')
            reserved=dict(self.totals);reserved[group]+=len(payload);reserved['observer']+=RESERVE['transaction'];self._limits(reserved)
            begin_len=self._record('BEGIN',seq=self.seq+1,name=name,bytes=len(payload),append=append,role=role)
            # From durable BEGIN until COMMIT, failure is non-recoverable in this API.
            self._write(p,payload,'ab' if append and old is not None else 'xb')
            actual=stamp(p);require(actual['bytes']==size_after,'POSTWRITE_SIZE')
            commit_len=self._record('COMMIT',seq=self.pending['seq'],stamp=actual)
            require(begin_len+commit_len<=RESERVE['transaction'],'JOURNAL_RESERVATION')
    def reconcile(self):
        """Independent scandir implementation, mandatory before successful handoff."""
        with self._locked():
            self._sync();require(self.pending is None,'INCOMPLETE_TRANSACTION')
            def walk(root):
                t=time.perf_counter();self.metrics['scan_calls']+=1
                try:
                    found={};stack=[root] if root.exists() else []
                    while stack:
                        with os.scandir(stack.pop()) as it:
                            for e in it:
                                require(not e.is_symlink(),'AUDIT_LINK')
                                if e.is_dir(follow_symlinks=False):stack.append(Path(e.path))
                                else:
                                    s=e.stat(follow_symlinks=False);found[Path(e.path).relative_to(root).as_posix()]=dict(bytes=s.st_size,mtime=s.st_mtime_ns)
                    return found
                finally:self.metrics['scan_seconds']+=time.perf_counter()-t
            actual=walk(self.target);control={k:actual.pop(k) for k in list(actual) if k.startswith(CONTROL)}
            require(actual==self.files,'INDEPENDENT_INVENTORY_MISMATCH')
            require(set(control)=={CONTROL+n for n in ('snapshot.json','lock.bin','journal.jsonl')},'CONTROL_INVENTORY')
            require(hashbytes(self.snapshot.read_bytes())==self.snapshot_hash and control[CONTROL+'journal.jsonl']['bytes']==self.offset and control[CONTROL+'lock.bin']['bytes']==1,'CONTROL_INTEGRITY')
            verified_chain='0'*64
            for line in self.journal.read_bytes().splitlines(keepends=True):
                require(line.endswith(b'\n') and json.loads(line)['previous']==verified_chain,'FULL_JOURNAL_INTEGRITY')
                verified_chain=hashbytes(line)
            require(verified_chain==self.chain,'FULL_JOURNAL_INTEGRITY')
            for root,expected in zip(self.inherited,self.base,strict=True):require(walk(root)==expected,'INHERITED_INVENTORY_MISMATCH')
            require(sum(self.totals.values())==sum(x['bytes'] for x in actual.values())+sum(x['bytes'] for x in control.values())+sum(x['bytes'] for group in self.base for x in group.values()),'TOTAL_RECONCILIATION')
            return dict(files=len(actual),totals=dict(self.totals),journal_bytes=self.offset,snapshot_sha256=self.snapshot_hash,matched=True)

class MeasuredIncremental:
    def __init__(self,target,base):self.target=target;self.base=base
    def __enter__(self):
        create=not (self.target/CONTROL).exists()
        expected=None
        if not create:
            first=json.loads((PACKAGE/'incremental-1/result.json').read_bytes());expected=first['snapshot_sha256']
        self.budget=JournalBudget(self.target,[self.base],create=create,expected_snapshot=expected)
        self.metrics=self.budget.metrics;self.initial_scan=dict(self.metrics);return self
    def apply(self,a):self.budget.write(a['name'],materialize_action(a),append=a['kind']=='append',role=a['role'])
    def verify(self):self.final=self.budget.reconcile()
    def __exit__(self,*args):pass
