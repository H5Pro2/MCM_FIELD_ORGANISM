from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_common_probe_acceptance_contract import (
    build_e1_common_probe_acceptance_contract,
)
from mcm_field_organism.e1_common_probe_eight_role_adapter_fixture import (
    E1CommonProbeEightRoleAdapterFixtureError,
    run_e1_common_probe_eight_role_adapter_fixture,
)
from mcm_field_organism.e1_common_probe_real_kernel_audit import (
    audit_e1_common_probe_real_kernels,
)


class E1CommonProbeEightRoleAdapterFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_e1_common_probe_acceptance_contract()
        self.audit = audit_e1_common_probe_real_kernels()

    def test_all_injected_slots_and_routes_are_complete(self) -> None:
        result = run_e1_common_probe_eight_role_adapter_fixture(
            self.contract, self.audit
        )
        self.assertEqual(3, result.formation_handoff_count)
        self.assertEqual(24, result.reset_slot_count)
        self.assertEqual(24, result.role_receipt_count)
        self.assertTrue(result.all_reset_fields_identical_and_slots_separate)
        self.assertTrue(result.all_state_routes_exact)
        self.assertTrue(result.all_backreaction_routes_exact)
        self.assertEqual(0, result.field_steps_executed)

    def test_integrated_decision_remains_synthetic_only(self) -> None:
        result = run_e1_common_probe_eight_role_adapter_fixture(
            self.contract, self.audit
        )
        self.assertEqual(
            "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE",
            result.integrated_synthetic_decision,
        )
        self.assertFalse(result.research_decision_permitted)
        self.assertFalse(result.memory_claim_permitted)

    def test_untyped_formation_kernel_fails_closed(self) -> None:
        with self.assertRaises(E1CommonProbeEightRoleAdapterFixtureError):
            run_e1_common_probe_eight_role_adapter_fixture(
                self.contract,
                self.audit,
                formation_kernel=lambda refinement: None,
            )

    def test_adapter_has_no_direct_real_kernel_or_write_path(self) -> None:
        source = inspect.getsource(run_e1_common_probe_eight_role_adapter_fixture)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory",
            "advance_frozen_e1_fast_shared_field_transient",
            "advance_neutral_fast_shared_field_transient",
            "open(",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
