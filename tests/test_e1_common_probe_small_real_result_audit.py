from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_small_real_result_audit import (
    E1CommonProbeSmallRealResultAuditError,
    audit_e1_common_probe_small_real_result,
)


class E1CommonProbeSmallRealResultAuditTests(unittest.TestCase):
    def test_ec55_is_bounded_to_wrapper_backreaction(self) -> None:
        result = audit_e1_common_probe_small_real_result()
        self.assertEqual(
            "real-wrapper-backreaction-route-technically-observable",
            result.bounded_finding,
        )
        self.assertFalse(result.research_decision_permitted)
        self.assertFalse(result.memory_claim_permitted)

    def test_next_fixture_is_exactly_n2_r2_eight_roles(self) -> None:
        result = audit_e1_common_probe_small_real_result()
        self.assertEqual((2, "r2"), (
            result.next_fixture_contact_count,
            result.next_fixture_refinement_id,
        ))
        self.assertEqual(8, result.next_probe_slot_count)
        self.assertEqual(4, result.next_formation_state_count)
        self.assertEqual(3208, result.next_total_field_steps)
        self.assertFalse(result.next_fixture_execution_permitted)

    def test_larger_release_fails_closed(self) -> None:
        result = audit_e1_common_probe_small_real_result()
        for update in (
            {"next_fixture_execution_permitted": True},
            {"full_matrix_execution_permitted": True},
            {"research_decision_permitted": True},
        ):
            with self.subTest(update=update):
                with self.assertRaises(E1CommonProbeSmallRealResultAuditError):
                    replace(result, **update)

    def test_audit_has_no_ec55_or_field_execution_or_write(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_small_real_result)
        for forbidden in (
            "run_e1_common_probe_small_real_fixture",
            "run_e1_common_probe_real_probe_wrapper",
            "run_e1_common_probe_real_formation_wrapper",
            "open(", "write_text", "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
