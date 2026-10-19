"""Versioned historical reference resolution; no numerical diagnosis here."""
import hashlib
import json
import importlib.abc
import sys
from pathlib import Path


class _NoDecoderImport(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in ('tools._s2oe_media_decoder', 'tools._s2oe_decoder_worker'):
            raise ImportError('DECODER_IMPORT_FORBIDDEN')
        return None


if any(n in sys.modules for n in ('tools._s2oe_media_decoder', 'tools._s2oe_decoder_worker')):
    raise ImportError('DECODER_ALREADY_IMPORTED')
sys.meta_path.insert(0, _NoDecoderImport())
from tools import _s2oc_shared_binding as shared

VERSION = 's2oe.visual-diagnostic-reference.v3'
HISTORICAL_ONLY = {
    'tools/_s2oe_media_decoder.py': ['76a5fc5a2964e55997598cac5523d5d5195a2f228abd2c4f776336e786db52be', 9560],
    'tools/_s2oe_decoder_worker.py': ['834347e9e6aa1399a7d35907e5cb7fab5b5314da1ef2b408194e5dfe67eacd5a', 22928],
}
LIMITS = dict(metadata=65536, table=262144, total=4194304)
CAPS = dict(binding=28672, log=8192, qualification=2048, failure=8192,
            report=8192, balance=8192, claims=20, table=196608, proof=4096)


class ReferenceError(ValueError):
    pass


def need(ok, code):
    if not ok:
        raise ReferenceError(code)


def raw(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def checked(root, name, bindings):
    path = (root/name).resolve()
    need(not Path(name).is_absolute() and path.is_relative_to(root.resolve()), 'REFERENCE_PATH_INVALID')
    need(name in bindings, 'REFERENCE_UNBOUND')
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise ReferenceError('REFERENCE_MISSING') from exc
    need([sha(data), len(data)] == bindings[name], 'REFERENCE_CHANGED')
    return data


def flatten(inv):
    need(set(inv) == {'ob', 'connector', 'version'} and 'files' in inv['ob'], 'INVENTORY_FORM_INVALID')
    result = dict(inv['ob']['files'])
    for path, bound in inv['connector'].items():
        need(path not in result or result[path] == bound, 'SOURCE_CONFLICT')
        result[path] = bound
    return result


def historical_source(root, name, expected, bindings, unavailable, active):
    if name in unavailable:
        need(name in HISTORICAL_ONLY and unavailable[name] == expected == HISTORICAL_ONLY[name]
             and name not in active and name not in bindings, 'HISTORICAL_ROLE_INVALID')
        return
    need(name in bindings and bindings[name] == expected, 'SOURCE_BINDING_INVALID')
    checked(root, name, bindings)


def resolve(root, parent, bindings, unavailable=None, active=()):
    """File integrity, all references, expansion, then native canonical digests."""
    unavailable = {} if unavailable is None else unavailable
    need(set(unavailable) <= set(HISTORICAL_ONLY) and not set(unavailable).intersection(active), 'HISTORICAL_ROLE_INVALID')
    loaded = {n: json.loads(checked(root, parent+n, bindings))
              for n in ('record.json', 'session.json', 'common.json', 'verification.json')}
    common = loaded['common.json']
    shared.b.check_root(common, 'common_digest')
    seen = set()
    for kind, name, size, digest in common['references']:
        need(kind in ('metadata', 'sources') and name not in seen, 'REFERENCE_DUPLICATE_OR_CLASS')
        seen.add(name)
        if name in unavailable:
            need(kind == 'sources', 'HISTORICAL_ROLE_INVALID')
            historical_source(root, name, [digest,size], bindings, unavailable, active)
        else:
            content = checked(root, name, bindings)
            need(len(content) == size and sha(content) == digest, 'REFERENCE_CONFLICT')
    refs = common['references']
    hits = [r for r in refs if r[0] == 'sources' and r[3] == common['inventory_sha256']]
    need(len(hits) == 1, 'INVENTORY_REFERENCE_MISSING')
    inv = json.loads(checked(root, hits[0][1], bindings))
    source_files = flatten(inv)
    media = [r for r in refs if r[0] == 'sources' and r[3] == common['manifest']['code_digest']]
    need(len(media) == 1, 'MEDIA_INVENTORY_MISSING')
    for path, bound in json.loads(checked(root, media[0][1], bindings)).items():
        need(path not in source_files or source_files[path] == bound, 'SOURCE_CONFLICT')
        source_files[path] = bound
    for path, bound in source_files.items():
        historical_source(root, path, bound, bindings, unavailable, active)
    # The existing resolver reads its bound inventory from the project root.
    need(root.resolve() == shared.b.ROOT.resolve(), 'RESOLVER_ROOT_INVALID')
    record, session = shared.unpack(loaded['record.json'], loaded['session.json'], common)
    proof = loaded['verification.json']
    shared.b.check_root(proof, 'verification_digest')
    need(proof['record_digest'] == record['record_digest'] and proof['evaluation_allowed'], 'PARENT_PROOF_INVALID')
    return dict(record=record), proof, common


def alternatives(reference_bytes, source_bytes, metadata_fixed=0):
    """Full retained outputs, including a failure after successful verification."""
    administrative = sum(CAPS[k] for k in ('binding', 'log', 'qualification', 'report', 'balance', 'claims'))
    result = {}
    for name, table, proof, failure in (
            ('success', CAPS['table'], CAPS['proof'], 0),
            ('input_failure', 0, 0, CAPS['failure']),
            ('table_failure', CAPS['table'], 0, CAPS['failure']),
            ('verification_failure', CAPS['table'], CAPS['proof'], CAPS['failure'])):
        metadata = metadata_fixed+administrative+failure
        parts = dict(references=reference_bytes, sources=source_bytes, metadata=metadata, table=table, proof=proof)
        total = sum(parts.values())
        violations = [k for k, value in (('metadata', metadata), ('table', table+proof), ('total', total)) if value > LIMITS[k]]
        result[name] = dict(parts=parts, total=total, limits=LIMITS, violations=violations)
    return result
