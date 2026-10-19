"""Bounded direct DAG capture using the unchanged URA1_JSON_DAG_V1 format."""
import contextlib
import gzip
import json
from pathlib import Path

ACTIVE = None
MAX_NODES = 65536
MAX_EDGES = 262144
MAX_INDICES = 65536
MAX_COLLECTIONS = 16
MAX_RECORD = 262144
MAX_DICTIONARY = 4194304
MAX_TEMP = 67108864


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


class Store:
    def __init__(self, parent):
        self.parent = Path(parent)
        self.nodes = []; self.known = {}; self.items = []
        self.edges = 0; self.indices = 0; self.dictionary_bytes = 0
        self.max_record = 0; self.temp_peak = 0; self.closed = False
        self.limits = dict(nodes=MAX_NODES, edges=MAX_EDGES, indices=MAX_INDICES,
                           dictionary=MAX_DICTIONARY, collections=MAX_COLLECTIONS)

    def intern(self, tag, body, scalar_type=None):
        key = (tag, scalar_type, body)
        existing = self.known.get(key)
        if existing is not None: return existing
        references = len(body) if tag in ('object', 'array') else 0
        if len(self.nodes) >= self.limits['nodes']: raise ValueError('NODE_LIMIT')
        if self.edges + references > self.limits['edges']: raise ValueError('EDGE_LIMIT')
        # Actual serialized dictionary budget includes key strings and scalar values.
        data = canonical([tag, body])
        if self.dictionary_bytes + len(data) > self.limits['dictionary']:
            raise ValueError('DICTIONARY_LIMIT')
        index = len(self.nodes)
        self.known[key] = index; self.nodes.append((tag, body))
        self.edges += references; self.dictionary_bytes += len(data)
        return index

    def visit(self, value):
        if isinstance(value, Collection):
            if value.owner is not self: raise ValueError('FOREIGN_COLLECTION')
            return self.intern('array', tuple(value.ids))
        if isinstance(value, dict):
            # Existing records use integer generation keys. JSON round-trips
            # turn them into strings before the canonical baseline is sorted.
            if any(type(k) not in (str,int) for k in value): raise ValueError('KEY_TYPE')
            members=sorted((str(k),v) for k,v in value.items())
            if len({k for k,v in members})!=len(members): raise ValueError('KEY_COLLISION')
            return self.intern('object', tuple((k,self.visit(v)) for k,v in members))
        if isinstance(value, (list, tuple)):
            return self.intern('array', tuple(self.visit(v) for v in value))
        # The representation distinguishes booleans/integers/floats and signed zero.
        return self.intern('scalar', value, (type(value).__name__, repr(value)))

    def expand(self, index):
        kind, body = self.nodes[index]
        if kind == 'object': return {k:self.expand(v) for k,v in body}
        if kind == 'array': return [self.expand(v) for v in body]
        return body

    def stats(self):
        return dict(nodes=len(self.nodes), edges=self.edges, indices=self.indices,
                    dictionary_bytes=self.dictionary_bytes, collections=len(self.items),
                    max_record_bytes=self.max_record, temporary_file_peak=self.temp_peak,
                    retained_redundant_history=False, limits=self.limits.copy())

    def close(self):
        for item in self.items: item.ids.clear()
        self.items.clear(); self.nodes.clear(); self.known.clear(); self.closed=True


class Collection:
    def __init__(self, owner):
        if len(owner.items) >= owner.limits['collections']: raise ValueError('COLLECTION_LIMIT')
        self.owner=owner; self.ids=[]; owner.items.append(self)

    def append(self, value):
        if self.owner.closed: raise ValueError('CLOSED_STORE')
        if self.owner.indices >= self.owner.limits['indices']: raise ValueError('INDEX_LIMIT')
        size=len(canonical(value))+1
        if size>MAX_RECORD: raise ValueError('RECORD_LIMIT')
        self.owner.max_record=max(self.owner.max_record,size)
        self.ids.append(self.owner.visit(value)); self.owner.indices+=1

    def __len__(self): return len(self.ids)
    def __iter__(self):
        for index in self.ids: yield self.owner.expand(index)
    def __getitem__(self, index): return self.owner.expand(self.ids[index])


@contextlib.contextmanager
def store(parent):
    global ACTIVE
    if ACTIVE is not None: raise ValueError('NESTED_STORE')
    owner=Store(parent); ACTIVE=owner
    try: yield owner
    finally:
        ACTIVE=None; owner.close()


def collection():
    if ACTIVE is None: raise ValueError('STORE_REQUIRED')
    return Collection(ACTIVE)


def write_archive(record, destination, expected, fault=None):
    owner=ACTIVE
    if owner is None: raise ValueError('STORE_REQUIRED')
    root=owner.visit(record)
    if root != len(owner.nodes)-1: raise ValueError('ROOT_NOT_LAST')
    envelope=dict(format='URA1_JSON_DAG_V1',nodes=owner.nodes,root=root,
                  original_bytes=expected['original_bytes'],
                  original_sha256=expected['original_sha256'])
    encoded=canonical(envelope)+b'\n'
    if len(encoded)>4194304: raise ValueError('ENCODED_LIMIT')
    blob=gzip.compress(encoded,compresslevel=9,mtime=0)
    if len(blob)>524288: raise ValueError('GZIP_LIMIT')
    destination=Path(destination);temp=Path(str(destination)+'.partial')
    if destination.exists() or temp.exists(): raise FileExistsError(destination)
    # No disk dictionary, journal, raw history or reconstruction copy exists.
    # The sole temporary file never exceeds the known bounded gzip buffer.
    if len(blob)>MAX_TEMP: raise ValueError('TEMP_LIMIT')
    try:
        with temp.open('xb') as target:
            midpoint=max(1,len(blob)//2)
            written=target.write(blob[:midpoint]);target.flush()
            owner.temp_peak=max(owner.temp_peak,temp.stat().st_size)
            if written!=midpoint: raise OSError('SHORT_WRITE')
            if fault=='write': raise OSError('INJECTED_WRITE')
            if fault=='encoder': raise ValueError('INJECTED_ENCODER')
            written=target.write(blob[midpoint:]);target.flush()
            owner.temp_peak=max(owner.temp_peak,temp.stat().st_size)
            if written!=len(blob)-midpoint: raise OSError('SHORT_WRITE')
        temp.replace(destination)
    finally:
        if temp.exists(): temp.unlink()
    return dict(encoded_bytes=len(encoded),gzip_bytes=len(blob),**expected)
