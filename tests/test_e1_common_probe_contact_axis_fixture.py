from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_acceptance_contract import build_e1_common_probe_acceptance_contract
from mcm_field_organism.e1_common_probe_contact_axis_audit import audit_e1_common_probe_contact_axis
from mcm_field_organism.e1_common_probe_contact_axis_fixture import run_e1_common_probe_contact_axis_fixture


class E1CommonProbeContactAxisFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.result = run_e1_common_probe_contact_axis_fixture(
            build_e1_common_probe_acceptance_contract(),
            audit_e1_common_probe_contact_axis(),
        )

    def test_all_48_slots_are_separate(self) -> None:
        self.assertEqual((6, 48, 48), (
            self.result.formation_handoff_count,
            self.result.reset_slot_count,
            self.result.role_receipt_count,
        ))
        self.assertTrue(self.result.n1_n2_separated)
        self.assertTrue(self.result.all_slots_unique)
        self.assertEqual(0, self.result.field_steps_executed)

    def test_each_contact_branch_is_decided_separately(self) -> None:
        self.assertEqual(
            (
                (1, "NO_MEASURABLE_COMMON_PROBE_DIFFERENCE"),
                (2, "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE"),
            ),
            self.result.branch_decisions,
        )
        self.assertFalse(self.result.research_decision_permitted)

    def test_only_static_real_binding_is_released(self) -> None:
        self.assertTrue(self.result.static_real_binding_permitted)
        self.assertFalse(self.result.pilot_execution_performed)
        self.assertFalse(self.result.persistence_performed)
        self.assertFalse(self.result.memory_claim_permitted)

    def test_fixture_contains_no_real_kernel_or_write_path(self) -> None:
        source = inspect.getsource(run_e1_common_probe_contact_axis_fixture)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory",
            "advance_frozen_e1_fast_shared_field_transient",
            "advance_neutral_fast_shared_field_transient",
            "open(", "write_text", "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
