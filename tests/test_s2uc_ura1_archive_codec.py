"""Codec-only tests against preserved neutral archives; no policy execution."""
import copy
import gc
import gzip
import hashlib
import io
import json
from pathlib import Path
import tracemalloc
import unittest

from tools._s2uc_ura1_archive_encode import encode
from tools._s2uc_ura1_archive_decode import read

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'reports/s2uc/ura1-neutral-development-20261014-01'
FACTS = {}


def pack(doc):
    return gzip.compress(json.dumps(doc, separators=(',', ':')).encode(), mtime=0)


class CodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {}
        for name in ('D_hand_case', 'lifecycle_trace'):
            original = (SOURCE / (name + '.json.gz')).read_bytes()
            canonical = gzip.decompress(original)
            cls.cases[name] = (original, canonical, encode(canonical))

    def test_C01_full_byte_reconstruction_and_limits(self):
        for name, (original, raw, blob) in self.cases.items():
            with self.subTest(case=name):
                sink = io.BytesIO()
                result = read(blob, hashlib.sha256(raw).hexdigest(), len(raw), sink.write)
                self.assertEqual(sink.getvalue(), raw)
                self.assertLessEqual(len(blob), 524288)
                self.assertLessEqual(result['encoded_bytes'], 4194304)
                FACTS[name] = result | dict(original_gzip_bytes=len(original), gzip_bytes=len(blob),
                    original_archive_sha256=hashlib.sha256(original).hexdigest(),
                    compact_archive_sha256=hashlib.sha256(blob).hexdigest())

    def altered_events(self, mutation):
        _, raw, blob = self.cases['lifecycle_trace']
        doc = json.loads(gzip.decompress(blob)); nodes = doc['nodes']
        root = dict(nodes[doc['root']][1]); arm = dict(nodes[root['U']][1])
        events = nodes[arm['internal']][1]
        mutation(events)
        with self.assertRaises(ValueError):
            read(pack(doc), hashlib.sha256(raw).hexdigest(), len(raw))

    def test_C02_missing_event(self):
        self.altered_events(lambda events: events.pop(10))

    def test_C03_swapped_events(self):
        def swap(events):
            self.assertNotEqual(events[10], events[11])
            events[10], events[11] = events[11], events[10]
        self.altered_events(swap)

    def test_C04_invalid_and_cyclic_references(self):
        _, raw, blob = self.cases['lifecycle_trace']
        for bad in (-1, 100000000, True):
            doc = json.loads(gzip.decompress(blob))
            doc['nodes'][-1][1][0][1] = bad
            with self.assertRaisesRegex(ValueError, 'REFERENCE'):
                read(pack(doc), hashlib.sha256(raw).hexdigest(), len(raw))
        doc = json.loads(gzip.decompress(blob)); doc['nodes'][-1][1][0][1] = len(doc['nodes'])-1
        with self.assertRaisesRegex(ValueError, 'REFERENCE'):
            read(pack(doc), hashlib.sha256(raw).hexdigest(), len(raw))

    def test_C05_damaged_state_reference(self):
        # No delta opcodes: corrupt the analogous event->state substitution.
        _, raw, blob = self.cases['lifecycle_trace']
        doc = json.loads(gzip.decompress(blob)); nodes = doc['nodes']
        for node in nodes:
            if node[0] == 'object' and 'state' in dict(node[1]):
                member = next(x for x in node[1] if x[0] == 'state')
                member[1] = 0
                break
        with self.assertRaises(ValueError):
            read(pack(doc), hashlib.sha256(raw).hexdigest(), len(raw))

    def test_C06_manipulated_value_and_binding(self):
        _, raw, blob = self.cases['lifecycle_trace']
        doc = json.loads(gzip.decompress(blob))
        node = next(n for n in doc['nodes'] if n[0] == 'scalar' and type(n[1]) is float)
        node[1] += 0.125
        with self.assertRaises(ValueError):
            read(pack(doc), hashlib.sha256(raw).hexdigest(), len(raw))
        doc['original_sha256'] = '0'*64
        with self.assertRaisesRegex(ValueError, 'BINDING'):
            read(pack(doc), hashlib.sha256(raw).hexdigest(), len(raw))

    def test_C07_stream_and_materialized_memory(self):
        for name, (_, raw, blob) in self.cases.items():
            digest = hashlib.sha256(raw).hexdigest()
            readings = {}
            for mode in ('stream', 'materialized'):
                gc.collect(); tracemalloc.start()
                if mode == 'stream':
                    read(blob, digest, len(raw))
                else:
                    sink = io.BytesIO()
                    read(blob, digest, len(raw), sink.write)
                    tree = json.loads(sink.getvalue())
                    self.assertIsInstance(tree, dict)
                current, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
                readings[mode] = dict(python_current_bytes=current, python_peak_bytes=peak)
                if mode == 'materialized': del tree, sink
            FACTS[name]['reconstruction_memory'] = readings

    def test_C08_original_bindings_unchanged(self):
        closure = json.loads((SOURCE/'closure.json').read_text())
        for name, entry in closure['files'].items():
            data = (SOURCE/name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry['sha256'], name)
        binding = json.loads((SOURCE/'development-binding.json').read_text())
        for name, digest in binding['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest, name)
        old = json.loads((ROOT/'docs/S2UC_UF1_V1_20261005_CODEBINDUNG.json').read_text())
        for name, digest in old['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(), digest, name)

    def test_C09_scalar_types_and_repeated_identity_metadata(self):
        record = dict(values=[True, 1, 1.0, -0.0, None, 'ä', {}, []],
                      originals=[dict(ordinal=3, values=[0.25]), dict(ordinal=7, values=[0.25])])
        raw = (json.dumps(record, sort_keys=True, separators=(',', ':'))+'\n').encode()
        sink = io.BytesIO()
        read(encode(raw), hashlib.sha256(raw).hexdigest(), len(raw), sink.write)
        self.assertEqual(raw, sink.getvalue())


if __name__ == '__main__':
    unittest.main()
