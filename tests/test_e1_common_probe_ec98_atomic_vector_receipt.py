from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec98_atomic_vector_receipt import (
    E1CommonProbeEC98AtomicVectorReceiptError,
    build_e1_common_probe_ec98_atomic_vector_receipt,
    run_e1_common_probe_ec98_synthetic_fixture,
)


class E1CommonProbeEC98AtomicVectorReceiptTests(unittest.TestCase):
    def test_six_active_vectors_and_reduced_controls_are_exact(self) -> None:
        result = run_e1_common_probe_ec98_synthetic_fixture()
        self.assertTrue(result.all_six_vectors_exact)
        self.assertTrue(result.controls_zero)
        self.assertEqual(6, result.receipt.active_vector_count)
        self.assertEqual(24, result.receipt.source_probe_count)
        self.assertFalse(result.receipt.raw_role_vectors_retained)
        self.assertEqual(0, result.field_steps_executed)

    def test_fixture_is_deterministic(self) -> None:
        first = run_e1_common_probe_ec98_synthetic_fixture()
        second = run_e1_common_probe_ec98_synthetic_fixture()
        self.assertEqual(first.result_digest, second.result_digest)

    def test_changed_geometry_fails_closed(self) -> None:
        result = run_e1_common_probe_ec98_synthetic_fixture()
        inputs = tuple()
        with self.assertRaises(E1CommonProbeEC98AtomicVectorReceiptError):
            build_e1_common_probe_ec98_atomic_vector_receipt(inputs)
        with self.assertRaises(E1CommonProbeEC98AtomicVectorReceiptError):
            replace(result.receipt, neuron_count=result.receipt.neuron_count + 1)

    def test_reducer_has_no_field_decider_or_writer(self) -> None:
        source = inspect.getsource(build_e1_common_probe_ec98_atomic_vector_receipt)
        for forbidden in (
            "decide_common_probe_evidence(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
