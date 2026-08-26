from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_ec100_atomic_vector_handoff import (
    E1CommonProbeEC100AtomicVectorHandoffError,
    build_e1_common_probe_ec100_atomic_vector_handoff,
    run_e1_common_probe_ec100_synthetic_fixture,
)


class E1CommonProbeEC100AtomicVectorHandoffTests(unittest.TestCase):
    def test_complete_same_process_handoff_is_atomic(self) -> None:
        result = run_e1_common_probe_ec100_synthetic_fixture()
        self.assertEqual((24, 24, 6), (
            result.source_probe_count,
            result.vector_input_count,
            result.active_vector_count,
        ))
        self.assertTrue(result.same_process_handoff)
        self.assertTrue(result.source_adapter_and_vector_receipt_returned_together)
        self.assertIs(result.vector_receipt, result.adapter_result.vector_receipt)
        self.assertEqual(0, result.field_steps_executed)

    def test_fixture_is_deterministic(self) -> None:
        first = run_e1_common_probe_ec100_synthetic_fixture()
        second = run_e1_common_probe_ec100_synthetic_fixture()
        self.assertEqual(first.result_digest, second.result_digest)
        self.assertEqual(first.ec98_vector_receipt_digest, second.ec98_vector_receipt_digest)

    def test_changed_source_or_result_fails_closed(self) -> None:
        result = run_e1_common_probe_ec100_synthetic_fixture()
        with self.assertRaises(E1CommonProbeEC100AtomicVectorHandoffError):
            replace(result.source_bundle, field_execution_permitted=True)
        with self.assertRaises(E1CommonProbeEC100AtomicVectorHandoffError):
            replace(result, source_probe_count=23)

    def test_untyped_source_fails_before_adapter(self) -> None:
        with self.assertRaises(E1CommonProbeEC100AtomicVectorHandoffError):
            build_e1_common_probe_ec100_atomic_vector_handoff(None)  # type: ignore[arg-type]

    def test_handoff_has_no_kernel_decider_retry_or_writer(self) -> None:
        source = inspect.getsource(build_e1_common_probe_ec100_atomic_vector_handoff)
        for forbidden in (
            "run_e1_common_probe_real_formation_wrapper(",
            "run_e1_common_probe_real_probe_wrapper(",
            "run_e1_common_probe_ec96_authorized_r4_r8_once(",
            "decide_common_probe_evidence(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
