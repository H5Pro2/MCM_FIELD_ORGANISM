import copy
import hashlib
import unittest

from tools import _s2ty_audio_materialization as materialization
from tools import _s2ty_real_source_supplier as supplier
from tools import _s2ty_source_time_binding as binding


class Tests(unittest.TestCase):
    def test_binding_resolves_all_sealed_endpoints_without_opening_pcm(self):
        manifest = binding.source_manifest()
        resolved = supplier.source_binding(manifest)
        self.assertEqual(resolved["endpoint_ordinals"], tuple(item["ordinal"] for item in manifest["events"] if "endpoint" in item))
        self.assertEqual(len(resolved["source_rows"]), 22)

    def test_supplier_is_lazy_and_uses_one_requested_native_window(self):
        manifest = binding.source_manifest()
        calls = []

        def neutral_window(spec):
            calls.append((spec.stream, spec.window))
            return bytearray(19_200)

        supply = supplier.create_payload_supplier(manifest, pcm_window=neutral_window)
        self.assertEqual(calls, [])
        event = manifest["events"][0]
        payload = supply(event["ordinal"], event["endpoint"])
        self.assertEqual((calls, len(payload)), ([(2, 0)], 19_200))
        del payload

    def test_supplier_rejects_swapped_or_non_endpoint_request_before_opening_pcm(self):
        manifest = binding.source_manifest()
        calls = []

        def neutral_window(spec):
            calls.append(spec)
            return bytearray(19_200)

        supply = supplier.create_payload_supplier(manifest, pcm_window=neutral_window)
        first, second = manifest["events"][0], manifest["events"][1]
        with self.assertRaises(supplier.S2TYRealSourceError) as raised:
            supply(first["ordinal"], second["endpoint"])
        self.assertEqual(raised.exception.code, "SOURCE_ENDPOINT_INVALID")
        self.assertEqual(calls, [])

    def test_materialization_accepts_generator_native_bytearray_without_copy_contract_change(self):
        manifest = binding.source_manifest()
        endpoint = copy.deepcopy(manifest["events"][0]["endpoint"])
        payload = bytearray(19_200)
        endpoint["pcm_sha256"] = hashlib.sha256(payload).hexdigest()
        counters = materialization.MaterializationCounters()
        measured = materialization.materialize(endpoint, payload, counters=counters)
        self.assertEqual(counters.snapshot(), {"pcm_hashes": 1, "audio_analyses": 1, "nj_projections": 1})
        self.assertEqual(measured["payload_bytes"], 19_200)
        del payload
