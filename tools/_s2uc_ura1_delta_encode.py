"""One format: complete initial record plus ordered typed structural deltas."""
import contextlib
import copy
import gzip
import hashlib
import json
from pathlib import Path
from tools import _s2uc_ura1_direct_archive as dag
from tools._s2uc_ura1_capture_integrity import Collection as Anchored,canonical

ACTIVE=None


class Pool(dag.Store):
    def __init__(self,owner):super().__init__(owner.parent);self.owner=owner
    def intern(self,tag,body,scalar_type=None):
        if (tag,scalar_type,body) not in self.known:
            self.owner.reserve(len(dag.canonical([tag,body])),1,len(body) if tag in ('object','array') else 0)
        return super().intern(tag,body,scalar_type)


class Store:
    def __init__(self,parent):
        self.parent=Path(parent);self.items=[];self.paths=[];self.path_ids={}
        self.deltas=[];self.delta_ids={};self.bytes=0;self.entries=0;self.edges=0;self.indices=0
        self.previous_bytes=0;self.previous_peak=0;self.record_peak=0;self.temp_peak=0;self.closed=False
        self.limits=dict(dictionary=4194304,nodes=65536,edges=262144,indices=65536,collections=16)
        self.pool=Pool(self)
    def reserve(self,size,entries=0,edges=0):
        if self.bytes+size>self.limits['dictionary']:raise ValueError('DICTIONARY_LIMIT')
        if self.entries+entries>self.limits['nodes']:raise ValueError('TABLE_LIMIT')
        if self.edges+edges>self.limits['edges']:raise ValueError('REFERENCE_LIMIT')
        self.bytes+=size;self.entries+=entries;self.edges+=edges
    def path(self,value):
        value=tuple(value)
        if value not in self.path_ids:
            self.reserve(len(dag.canonical(value)),1)
            self.path_ids[value]=len(self.paths);self.paths.append(value)
        return self.path_ids[value]
    def delta(self,ops):
        key=dag.canonical(ops)
        if key not in self.delta_ids:
            refs=sum(1+(len(op[2]) if op[1]==2 else int(op[1]==0)) for op in ops)
            self.reserve(len(key),1,refs)
            self.delta_ids[key]=len(self.deltas);self.deltas.append(ops)
        return self.delta_ids[key]
    def stats(self):
        return dict(dictionary_bytes=self.bytes,table_entries=self.entries,value_nodes=len(self.pool.nodes),
                    paths=len(self.paths),deltas=len(self.deltas),reference_edges=self.edges,
                    record_indices=self.indices,collections=len(self.items),previous_records_bytes=self.previous_bytes,
                    previous_records_peak_bytes=self.previous_peak,max_record_bytes=self.record_peak,
                    temporary_file_peak=self.temp_peak,limits=self.limits.copy())
    def close(self):
        for seq in self.items:seq.previous=None;seq.ids.clear()
        self.pool.close();self.items.clear();self.paths.clear();self.path_ids.clear()
        self.deltas.clear();self.delta_ids.clear();self.previous_bytes=0;self.closed=True


def same(a,b):
    if type(a) is not type(b):return False
    if isinstance(a,(dict,list)):return dag.canonical(a)==dag.canonical(b)
    return repr(a)==repr(b) if type(a) is float else a==b


class Collection(Anchored):
    def __init__(self,owner):
        if len(owner.items)>=owner.limits['collections']:raise ValueError('COLLECTION_LIMIT')
        self.owner=owner;self.initial=-1;self.ids=[];self.previous=None;self.previous_size=0
        self.digest=hashlib.sha256(b'[');self.byte_count=1;self.record_count=0;owner.items.append(self)
    def append(self,value):
        data=canonical(value) # independent capture anchor input before codec logic
        if len(data)+1>262144:raise ValueError('RECORD_LIMIT')
        if self.owner.indices>=self.owner.limits['indices']:raise ValueError('INDEX_LIMIT')
        fresh=json.loads(data);ops=[];pool=self.owner.pool
        def replace(path,new):ops.append([self.owner.path(path),0,pool.visit(new)])
        def diff(old,new,path):
            if type(old) is dict and type(new) is dict:
                for key in sorted(old.keys()-new.keys()):ops.append([self.owner.path(path+[key]),1])
                for key in sorted(new):
                    if key not in old:replace(path+[key],new[key])
                    else:diff(old[key],new[key],path+[key])
            elif type(old) is list and type(new) is list and len(old)==len(new) and len(new)<=8:
                for i,(a,b) in enumerate(zip(old,new)):diff(a,b,path+[i])
            elif type(old) is str and type(new) is str and len(old)==len(new) and len(new)>=128:
                spans=[];i=0
                while i<len(new):
                    if old[i]==new[i]:i+=1;continue
                    start=i
                    while i<len(new) and old[i]!=new[i]:i+=1
                    spans.append([start,pool.visit(new[start:i])])
                if spans:ops.append([self.owner.path(path),2,spans])
            elif not same(old,new):replace(path,new)
        if self.record_count==0:
            self.initial=pool.visit(fresh);self.owner.reserve(0,0,1)
        else:
            diff(self.previous,fresh,[])
            delta=self.owner.delta(ops);self.owner.reserve(0,0,1);self.ids.append(delta)
        if self.record_count:self.digest.update(b',');self.byte_count+=1
        self.digest.update(data);self.byte_count+=len(data);self.record_count+=1;self.owner.indices+=1
        self.owner.previous_bytes+=len(data)-self.previous_size;self.previous_size=len(data)
        if self.owner.previous_bytes>16*262144:raise ValueError('PREVIOUS_BUFFER_LIMIT')
        self.owner.previous_peak=max(self.owner.previous_peak,self.owner.previous_bytes)
        self.owner.record_peak=max(self.owner.record_peak,len(data)+1);self.previous=fresh
    def __len__(self):return self.record_count
    def __iter__(self):
        if self.initial<0:return
        state=self.owner.pool.expand(self.initial);yield copy.deepcopy(state)
        for ref in self.ids:
            for op in self.owner.deltas[ref]:
                path=self.owner.paths[op[0]];tag=op[1]
                parent=state
                for key in path[:-1]:parent=parent[key]
                value=state if not path else parent[path[-1]] if tag!=0 else None
                if tag==0:
                    new=self.owner.pool.expand(op[2])
                    if not path:state=new
                    else:parent[path[-1]]=new
                elif tag==1:del parent[path[-1]]
                else:
                    for start,textref in op[2]:
                        text=self.owner.pool.expand(textref);value=value[:start]+text+value[start+len(text):]
                    if not path:state=value
                    else:parent[path[-1]]=value
            yield copy.deepcopy(state)
    def __getitem__(self,index):
        if index<0:index+=len(self)
        for i,value in enumerate(self):
            if i==index:return value
        raise IndexError(index)


@contextlib.contextmanager
def store(parent):
    global ACTIVE
    if ACTIVE is not None:raise ValueError('NESTED_STORE')
    owner=Store(parent);ACTIVE=owner
    try:yield owner
    finally:ACTIVE=None;owner.close()


def collection():
    if ACTIVE is None:raise ValueError('STORE_REQUIRED')
    return Collection(ACTIVE)


def write_archive(record,path,expected,fault=None):
    owner=ACTIVE
    def skeleton(value):
        if isinstance(value,Collection):return {'$sequence':owner.items.index(value)}
        if isinstance(value,dict):return {k:skeleton(v) for k,v in value.items()}
        if isinstance(value,(list,tuple)):return [skeleton(v) for v in value]
        return value
    root=owner.pool.visit(skeleton(record))
    owner.reserve(0,0,1)
    sequences=[[seq.initial,seq.ids] for seq in owner.items]
    document=dict(format='URA1_STATE_DELTA_V1',values=owner.pool.nodes,paths=owner.paths,
                  deltas=owner.deltas,sequences=sequences,root=root,**expected)
    encoded=dag.canonical(document)+b'\n'
    if len(encoded)>4194304:raise ValueError('ENCODED_LIMIT')
    blob=gzip.compress(encoded,compresslevel=9,mtime=0)
    if len(blob)>524288:raise ValueError('GZIP_LIMIT')
    path=Path(path);temp=Path(str(path)+'.partial')
    if path.exists() or temp.exists():raise FileExistsError(path)
    try:
        with temp.open('xb') as target:
            target.write(blob[:len(blob)//2]);target.flush();owner.temp_peak=max(owner.temp_peak,temp.stat().st_size)
            if fault:raise OSError('INJECTED_WRITE')
            target.write(blob[len(blob)//2:]);target.flush();owner.temp_peak=max(owner.temp_peak,temp.stat().st_size)
        temp.replace(path)
    finally:
        if temp.exists():temp.unlink()
    return dict(encoded_bytes=len(encoded),gzip_bytes=len(blob),**expected)
