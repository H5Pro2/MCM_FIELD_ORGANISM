from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7au_baseline_connection_inventory import (
    W7AUBaselineConnectionInventoryError,
    build_w7au_baseline_connection_inventory,
)


class W7AUBaselineConnectionInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = build_w7au_baseline_connection_inventory()

    def test_all_ten_w7l_baseline_equations_are_implemented(self):
        self.assertEqual(10, len(self.inventory.connections))
        self.assertEqual(10, self.inventory.equation_implementation_count)
        self.assertTrue(
            all(item.equation_implemented for item in self.inventory.connections)
        )

    def test_no_baseline_is_yet_terminally_w7at_comparable(self):
        self.assertEqual(0, self.inventory.terminally_comparable_count)
        self.assertTrue(
            all(
                not item.current_w7at_comparable
                for item in self.inventory.connections
            )
        )

    def test_observer_results_are_reusable_without_new_integration(self):
        self.assertEqual(
            ("LEAK", "SAT", "NORM"),
            self.inventory.reuse_without_new_integration,
        )
        observer = self.inventory.connections[:3]
        self.assertTrue(all(not item.requires_new_integration for item in observer))

    def test_four_coupling_models_need_a_trajectory_consumer(self):
        self.assertEqual(
            ("LIN", "F3", "CONST-V", "MOB"),
            self.inventory.field_trajectory_gap,
        )
        self.assertTrue(
            all(
                item.connection_status
                == "DERIVATIVE_ONLY_NO_TRAJECTORY_CONSUMER"
                for item in self.inventory.connections[3:7]
            )
        )

    def test_three_cap_interventions_need_a_trajectory_consumer(self):
        self.assertEqual(
            ("ETA0", "KAPPA0", "SIGN"),
            self.inventory.cap_intervention_trajectory_gap,
        )
        self.assertTrue(
            all(
                item.connection_status
                == "INTERVENTION_ONLY_NO_TRAJECTORY_CONSUMER"
                for item in self.inventory.connections[7:]
            )
        )

    def test_const_v_remains_the_primary_narrow_field_baseline(self):
        self.assertEqual("CONST-V", self.inventory.primary_narrow_baseline)

    def test_audit_accepts_no_values_and_rejects_tampering(self):
        self.assertEqual(
            0,
            len(
                inspect.signature(
                    build_w7au_baseline_connection_inventory
                ).parameters
            ),
        )
        self.assertFalse(self.inventory.accept_result_values)
        self.assertFalse(self.inventory.field_function_decision_allowed)
        self.assertFalse(self.inventory.memory_claim_allowed)
        with self.assertRaises(W7AUBaselineConnectionInventoryError):
            replace(self.inventory, terminally_comparable_count=10)

    def test_inventory_is_not_publicly_exported(self):
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7au_baseline_connection_inventory")
        )


if __name__ == "__main__":
    unittest.main()
