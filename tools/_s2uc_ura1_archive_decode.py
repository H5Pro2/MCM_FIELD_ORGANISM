"""Independent DAG reader and incremental canonical verifier. No encoder imports."""
import gzip
import hashlib
import io
import json


def _check(condition, reason):
    if not condition:
        raise ValueError(reason)


def _unique(pairs):
    result = {}
    for key, value in pairs:
        _check(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def read(blob, expected_sha256, expected_bytes, sink=None):
    """Validate against externally bound original digest; optionally stream bytes.

    A sink is provisional until successful return. The full history is never
    materialized here. Repeated dictionary references are expanded in order.
    """
    _check(len(blob) <= 524288, 'GZIP_LIMIT')
    with gzip.GzipFile(fileobj=io.BytesIO(blob)) as source:
        encoded = source.read(4194305)
    _check(len(encoded) <= 4194304, 'ENCODED_LIMIT')
    doc = json.loads(encoded, object_pairs_hook=_unique,
                     parse_constant=lambda x: (_ for _ in ()).throw(ValueError('NONFINITE')))
    _check(set(doc) == {'format', 'nodes', 'root', 'original_bytes', 'original_sha256'}, 'ENVELOPE')
    _check(doc['format'] == 'URA1_JSON_DAG_V1', 'FORMAT')
    _check(doc['original_sha256'] == expected_sha256 and
           type(doc['original_bytes']) is int and doc['original_bytes'] == expected_bytes, 'BINDING')
    nodes = doc['nodes']
    _check(type(nodes) is list and len(nodes) > 0, 'NODES')
    _check(type(doc['root']) is int and doc['root'] == len(nodes)-1, 'ROOT')
    depths = []
    for index, node in enumerate(nodes):
        _check(type(node) is list and len(node) == 2, 'NODE')
        kind, value = node
        refs = []
        if kind == 'scalar':
            _check(value is None or type(value) in (str, int, float, bool), 'SCALAR')
        elif kind == 'array':
            _check(type(value) is list, 'ARRAY')
            refs = value
        elif kind == 'object':
            _check(type(value) is list, 'OBJECT')
            keys = []
            for entry in value:
                _check(type(entry) is list and len(entry) == 2 and type(entry[0]) is str, 'MEMBER')
                keys.append(entry[0]); refs.append(entry[1])
            _check(keys == sorted(set(keys)), 'KEY_ORDER')
        else:
            raise ValueError('TAG')
        _check(all(type(ref) is int and 0 <= ref < index for ref in refs), 'REFERENCE')
        depth = 1 + max((depths[ref] for ref in refs), default=0)
        _check(depth <= 128, 'DEPTH')
        depths.append(depth)
    digest = hashlib.sha256(); count = 0

    def emit(data):
        nonlocal count
        count += len(data)
        _check(count <= expected_bytes, 'RECONSTRUCTED_LIMIT')
        digest.update(data)
        if sink is not None:
            sink(data)

    def literal(value):
        return json.dumps(value, ensure_ascii=True, allow_nan=False,
                          separators=(',', ':')).encode('utf-8')

    def walk(ref):
        kind, value = nodes[ref]
        if kind == 'scalar':
            emit(literal(value))
        elif kind == 'array':
            emit(b'[')
            for i, child in enumerate(value):
                if i: emit(b',')
                walk(child)
            emit(b']')
        else:
            emit(b'{')
            for i, (key, child) in enumerate(value):
                if i: emit(b',')
                emit(literal(key)); emit(b':'); walk(child)
            emit(b'}')

    walk(doc['root']); emit(b'\n')
    _check(count == expected_bytes and digest.hexdigest() == expected_sha256, 'RECONSTRUCTION_HASH')
    return dict(encoded_bytes=len(encoded), reconstructed_bytes=count,
                reconstructed_sha256=digest.hexdigest(), nodes=len(nodes),
                max_depth=max(depths))
