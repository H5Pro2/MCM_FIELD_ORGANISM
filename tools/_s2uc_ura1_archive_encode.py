"""Lossless JSON subtree dictionary; no policy imports or inner compression."""
import gzip
import hashlib
import json


def encode(canonical_record):
    record = json.loads(canonical_record)
    nodes, known = [], {}

    def visit(value):
        if isinstance(value, dict):
            node = ['object', [[key, visit(value[key])] for key in sorted(value)]]
        elif isinstance(value, list):
            node = ['array', [visit(item) for item in value]]
        else:
            node = ['scalar', value]
        key = json.dumps(node, ensure_ascii=True, allow_nan=False, separators=(',', ':'))
        if key not in known:
            known[key] = len(nodes)
            nodes.append(node)
        return known[key]

    root = visit(record)
    envelope = dict(format='URA1_JSON_DAG_V1', nodes=nodes, root=root,
                    original_bytes=len(canonical_record),
                    original_sha256=hashlib.sha256(canonical_record).hexdigest())
    expanded = (json.dumps(envelope, sort_keys=True, allow_nan=False,
                           separators=(',', ':')) + '\n').encode('utf-8')
    if len(expanded) > 4 * 1024 * 1024:
        raise ValueError('ENCODED_LIMIT')
    blob = gzip.compress(expanded, compresslevel=9, mtime=0)
    if len(blob) > 512 * 1024:
        raise ValueError('GZIP_LIMIT')
    return blob
