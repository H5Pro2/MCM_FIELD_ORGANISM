from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_real_binding_contract import (
    E1CommonProbeRealBindingContractError,
    build_e1_common_probe_real_binding_contract,
)


class E1CommonProbeRealBindingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = build_e1_common_probe_real_binding_contract()

    def test_all_contact_aware_real_slots_are_bound(self) -> None:
        self.assertEqual((1, 2), self.contract.contact_counts)
        self.assertEqual(24, self.contract.formation_state_count)
        self.assertEqual(48, self.contract.probe_slot_count)
        self.assertEqual(48, len(self.contract.slot_bindings))
        self.assertTrue(self.contract.contact_axis_bound_to_plan_pairs)

    def test_p0_and_e1_routes_use_separate_kernels(self) -> None:
        routes = {item.role_id: item for item in self.contract.slot_bindings[:8]}
        self.assertEqual(
            "advance_neutral_fast_shared_field_transient",
            routes["p0-reset-ab"].probe_kernel,
        )
        self.assertIsNone(routes["p0-reset-ab"].state_role)
        self.assertEqual(
            "advance_frozen_e1_fast_shared_field_transient",
            routes["e1-active-ab"].probe_kernel,
        )
        self.assertTrue(routes["e1-active-ab"].backreaction_enabled)
        self.assertFalse(
            routes["e1-probe-feedback-ablated-ab"].backreaction_enabled
        )
        self.assertEqual(
            "formation-ablated-ab",
            routes["e1-formation-ablated-ab"].state_role,
        )

    def test_execution_or_claim_release_fails_closed(self) -> None:
        for update in (
            {"field_execution_permitted": True},
            {"persistence_permitted": True},
            {"memory_claim_permitted": True},
        ):
            with self.subTest(update=update):
                with self.assertRaises(E1CommonProbeRealBindingContractError):
                    replace(self.contract, **update)

    def test_builder_does_not_invoke_bound_kernels_or_write(self) -> None:
        source = inspect.getsource(build_e1_common_probe_real_binding_contract)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_neutral_fast_shared_field_transient(",
            "open(", "write_text", "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
