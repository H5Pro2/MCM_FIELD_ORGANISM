"""Bounded-record disk spooling and incremental subtree encoder."""
import contextlib
import gzip
import hashlib
import json
from pathlib import Path
import tempfile

ACTIVE = None


class Spool:
    def __init__(self, owner):
        self.owner = owner
        self.path = owner.path / (str(len(owner.items)) + '.jsonl')
        self.file = self.path.open('wb')
        self.count = 0
        owner.items.append(self)

    def append(self, value):
        data = (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()
        if len(data) > 262144 or self.owner.bytes + len(data) > 67108864:
            raise ValueError('SPOOL_LIMIT')
        self.file.write(data)
        self.count += 1
        self.owner.bytes += len(data)
        self.owner.max_record = max(self.owner.max_record, len(data))

    def __len__(self):
        return self.count

    def __iter__(self):
        self.file.flush()
        with self.path.open('rb') as source:
            for line in source:
                yield json.loads(line)

    def __getitem__(self, index):
        if index < 0: index += self.count
        for i, value in enumerate(self):
            if i == index: return value
        raise IndexError(index)


class Store:
    def __init__(self, parent):
        self.temp = tempfile.TemporaryDirectory(prefix='spool-', dir=parent)
        self.path = Path(self.temp.name)
        self.items = []; self.bytes = 0; self.max_record = 0

    def close(self):
        for item in self.items: item.file.close()
        self.temp.cleanup()


@contextlib.contextmanager
def store(parent):
    global ACTIVE
    if ACTIVE is not None: raise RuntimeError('NESTED_STORE')
    owner = Store(parent); ACTIVE = owner
    try: yield owner
    finally:
        ACTIVE = None; owner.close()


def collection():
    if ACTIVE is None: raise RuntimeError('STORE_REQUIRED')
    return Spool(ACTIVE)


def pieces(value):
    """Canonical source serialization, independent of dictionary node traversal."""
    if isinstance(value, dict):
        yield b'{'
        for i, key in enumerate(sorted(value)):
            if i: yield b','
            yield json.dumps(key).encode(); yield b':'
            yield from pieces(value[key])
        yield b'}'
    elif isinstance(value, (list, tuple, Spool)):
        yield b'['
        for i, item in enumerate(value):
            if i: yield b','
            yield from pieces(item)
        yield b']'
    else:
        yield json.dumps(value, allow_nan=False, separators=(',', ':')).encode()


def write_archive(record, destination, fault=False):
    digest = hashlib.sha256(); size = 0
    for part in pieces(record): digest.update(part); size += len(part)
    digest.update(b'\n'); size += 1
    nodes = []; known = {}; dictionary_bytes = 0

    def visit(value):
        nonlocal dictionary_bytes
        if isinstance(value, dict):
            node = ['object', [[k, visit(value[k])] for k in sorted(value)]]
        elif isinstance(value, (list, tuple, Spool)):
            node = ['array', [visit(v) for v in value]]
        else: node = ['scalar', value]
        key = json.dumps(node, separators=(',', ':'), allow_nan=False)
        if key not in known:
            dictionary_bytes += len(key.encode())
            if dictionary_bytes > 4194304: raise ValueError('DICTIONARY_LIMIT')
            known[key] = len(nodes); nodes.append(node)
        return known[key]

    root = visit(record)
    envelope = dict(format='URA1_JSON_DAG_V1', nodes=nodes, root=root,
                    original_bytes=size, original_sha256=digest.hexdigest())
    temp = Path(str(destination)+'.partial'); encoded = 0
    try:
        with temp.open('wb') as target:
            with gzip.GzipFile(fileobj=target, mode='wb', mtime=0) as zipped:
                for part in json.JSONEncoder(sort_keys=True, separators=(',', ':'), allow_nan=False).iterencode(envelope):
                    data = part.encode(); encoded += len(data)
                    if encoded > 4194303: raise ValueError('ENCODED_LIMIT')
                    zipped.write(data)
                    if fault: raise ValueError('INJECTED_ENCODER')
                zipped.write(b'\n'); encoded += 1
        if temp.stat().st_size > 524288: raise ValueError('GZIP_LIMIT')
        temp.replace(destination)
    finally:
        if temp.exists(): temp.unlink()
    return dict(original_sha256=digest.hexdigest(), original_bytes=size,
                encoded_bytes=encoded, gzip_bytes=Path(destination).stat().st_size,
                nodes=len(nodes))
