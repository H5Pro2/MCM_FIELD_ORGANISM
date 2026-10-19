import unittest

from tools import _s2ty_resource_ledger as ledger
from tools import _s2ty_source_time_binding as binding


def copied_manifest():
    import copy
    return copy.deepcopy(binding.source_manifest())


class Tests(unittest.TestCase):
    def test_s2tw_shape_reuse_and_native_time_are_bound(self):
        manifest = binding.source_manifest()
        endpoints = [item["endpoint"] for item in manifest["events"] if "endpoint" in item]
        self.assertEqual((len(manifest["events"]), len(endpoints), [item["arm"] for item in manifest["owner_closes"]]), (26, 22, ["adapter", "direct"]))
        self.assertTrue(manifest["source_reused"])
        self.assertTrue(all(item["window_start_sample"] == item["nj_snapshot_index"] * 480 for item in endpoints))

    def test_logical_clock_is_complete_and_separate_from_native_time(self):
        manifest = binding.source_manifest()
        self.assertEqual([item["runtime_time"] for item in manifest["events"]], list(range(26)))
        self.assertEqual([item["runtime_time"] for item in manifest["owner_closes"]], [26, 27])
        self.assertNotIn("runtime_time", manifest["events"][0]["endpoint"])

    def test_missing_duplicate_reverse_and_manipulated_runtime_times_fail_closed(self):
        cases = (
            ("missing", lambda manifest: manifest["events"][0].pop("runtime_time"), "RUNTIME_TIME_INVALID"),
            ("duplicate", lambda manifest: manifest["events"][1].update(runtime_time=0), "RUNTIME_TIME_INVALID"),
            ("reverse", lambda manifest: manifest["events"][2].update(runtime_time=1), "RUNTIME_TIME_INVALID"),
            ("manipulated", lambda manifest: manifest["events"][3].update(runtime_time=99), "RUNTIME_TIME_INVALID"),
            ("owner-close", lambda manifest: manifest["owner_closes"][0].update(runtime_time=25), "OWNER_CLOSE_TIME_INVALID"),
        )
        for name, mutate, code in cases:
            with self.subTest(name=name):
                manifest = copied_manifest()
                mutate(manifest)
                with self.assertRaises(binding.S2TYBindingError) as raised:
                    binding.validate_static(manifest)
                self.assertEqual(raised.exception.code, code)

    def test_payload_profile_time_and_endpoint_failures_are_typed(self):
        manifest = binding.source_manifest()
        endpoint = binding.endpoint_at(manifest, 1)
        values = (0.0,) * 48
        cases = (
            ("hash", dict(payload_sha256="0" * 64, profile=endpoint["profile"], snapshot_index=endpoint["nj_snapshot_index"], window_start_sample=endpoint["window_start_sample"], window_end_sample=endpoint["window_end_sample"], values=values), "PAYLOAD_HASH_INVALID"),
            ("profile", dict(payload_sha256=endpoint["pcm_sha256"], profile="wrong", snapshot_index=endpoint["nj_snapshot_index"], window_start_sample=endpoint["window_start_sample"], window_end_sample=endpoint["window_end_sample"], values=values), "PROFILE_INVALID"),
            ("time", dict(payload_sha256=endpoint["pcm_sha256"], profile=endpoint["profile"], snapshot_index=endpoint["nj_snapshot_index"], window_start_sample=endpoint["window_start_sample"] + 1, window_end_sample=endpoint["window_end_sample"], values=values), "NATIVE_TIME_INVALID"),
        )
        for name, kwargs, code in cases:
            with self.subTest(name=name):
                with self.assertRaises(binding.S2TYBindingError) as raised:
                    binding.handoff(manifest, 1, **kwargs)
                self.assertEqual(raised.exception.code, code)
        with self.assertRaises(binding.S2TYBindingError) as raised:
            binding.endpoint_at(manifest, 5)
        self.assertEqual(raised.exception.code, "ENDPOINT_MISSING")

    def test_once_created_half_values_are_shared_by_both_arms(self):
        manifest = binding.source_manifest()
        endpoint = binding.endpoint_at(manifest, 1)
        values = tuple(float(index) / 100 for index in range(48))
        adapter_values, direct_values, receipt = binding.handoff(manifest, 1, payload_sha256=endpoint["pcm_sha256"], profile=endpoint["profile"], snapshot_index=endpoint["nj_snapshot_index"], window_start_sample=endpoint["window_start_sample"], window_end_sample=endpoint["window_end_sample"], values=values)
        self.assertIs(adapter_values, values)
        self.assertIs(direct_values, values)
        self.assertTrue(receipt["same_instance"])

    def test_source_binding_artifact_is_counted_by_ledger(self):
        manifest = binding.source_manifest()
        result = ledger.ledger(ledger.planned_shape(), source_bytes=manifest["binding_bytes"], metadata_bytes=0, shared_bytes=0, success_record_bytes=0, failure_record_bytes=0, verification_bytes=0)
        self.assertEqual(result["branches"]["success"]["contributions"]["sources"], manifest["binding_bytes"])
