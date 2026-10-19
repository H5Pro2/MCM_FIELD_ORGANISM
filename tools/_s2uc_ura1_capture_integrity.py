"""Capture-time canonical anchors; JSON normalization independent of DAG encoding."""
import hashlib
import json
from tools import _s2uc_ura1_direct_archive as archive


def canonical(value):
    # JSON roundtrip normalizes integer metadata keys without using the encoder.
    normalized=json.loads(json.dumps(value,allow_nan=False,separators=(',',':')))
    return json.dumps(normalized,sort_keys=True,allow_nan=False,separators=(',',':')).encode()


class Collection(archive.Collection):
    def __init__(self,owner):
        super().__init__(owner)
        self.digest=hashlib.sha256(b'[');self.byte_count=1;self.record_count=0

    def append(self,value):
        data=canonical(value)  # before any encoder traversal or mutation
        if len(data)+1>archive.MAX_RECORD:raise ValueError('RECORD_LIMIT')
        super().append(value)
        if self.record_count:self.digest.update(b',');self.byte_count+=1
        self.digest.update(data);self.byte_count+=len(data);self.record_count+=1

    def anchor(self):
        digest=self.digest.copy();digest.update(b']')
        return dict(sha256=digest.hexdigest(),bytes=self.byte_count+1,count=self.record_count)


def collection():
    if archive.ACTIVE is None:raise ValueError('STORE_REQUIRED')
    return Collection(archive.ACTIVE)


def manifest(record):
    anchors={}
    def fold(value,path):
        if isinstance(value,Collection):
            anchors[path]=value.anchor()
            return {'$capture':value.anchor()}
        if isinstance(value,dict):return {k:fold(v,path+'/'+str(k)) for k,v in value.items()}
        if isinstance(value,(list,tuple)):return [fold(v,path+'/'+str(i)) for i,v in enumerate(value)]
        return value
    folded=fold(record,'')
    return dict(format='URA1_CAPTURE_ANCHORS_V1',collections=anchors,
                folded_sha256=hashlib.sha256(canonical(folded)+b'\n').hexdigest(),
                origin='canonical records before reference encoder traversal')


def full_record_digest(record):
    """Envelope checksum only; independently captured anchors are authoritative."""
    digest=hashlib.sha256();size=0
    def emit(data):
        nonlocal size
        digest.update(data);size+=len(data)
    def visit(value):
        if isinstance(value,Collection):
            emit(b'[')
            for i,item in enumerate(value):
                if i:emit(b',')
                emit(canonical(item))
            emit(b']')
        elif isinstance(value,dict):
            emit(b'{')
            for i,key in enumerate(sorted(value)):
                if i:emit(b',')
                emit(canonical(key));emit(b':');visit(value[key])
            emit(b'}')
        else:emit(canonical(value))
    visit(record);emit(b'\n')
    return dict(original_sha256=digest.hexdigest(),original_bytes=size)
