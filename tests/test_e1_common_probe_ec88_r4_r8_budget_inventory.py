from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_common_probe_acceptance_contract import (
    build_e1_common_probe_acceptance_contract,
)
from mcm_field_organism.e1_common_probe_ec87_r2_ec46_complement_contract import (
    build_e1_common_probe_ec87_r2_ec46_complement_contract,
)
from mcm_field_organism.e1_common_probe_ec88_r4_r8_budget_inventory import (
    E1CommonProbeEC88R4R8BudgetInventoryError,
    build_e1_common_probe_ec88_r4_r8_budget_inventory,
)
from tests.test_e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffTests,
)


class E1CommonProbeEC88R4R8BudgetInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        E1CommonProbeN2R2ObjectHandoffTests.setUpClass()
        source = E1CommonProbeN2R2ObjectHandoffTests
        cls.binding = source.contract
        cls.formation_plans = source.formation_plans
        cls.probe_plans = source.inputs.probe_plans
        cls.complement = build_e1_common_probe_ec87_r2_ec46_complement_contract(
            cls.root, build_e1_common_probe_acceptance_contract()
        )

    def test_exact_r4_and_r8_budgets_are_derived(self) -> None:
        result = build_e1_common_probe_ec88_r4_r8_budget_inventory(
            self.complement,
            self.binding,
            self.formation_plans,
            self.probe_plans,
        )
        self.assertEqual((6416, 12832), tuple(item[7] for item in result.budgets))
        self.assertEqual((9648, 9600, 19248), (
            result.combined_formation_steps,
            result.combined_probe_steps,
            result.combined_total_steps,
        ))
        self.assertTrue(result.all_supports_assigned_once)
        self.assertFalse(result.concrete_object_handoffs_ready)
        self.assertFalse(result.runtime_caps_bound)
        self.assertFalse(result.field_execution_permitted)

    def test_untyped_input_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeEC88R4R8BudgetInventoryError, "typed EC52"
        ):
            build_e1_common_probe_ec88_r4_r8_budget_inventory(
                self.complement,
                object(),
                self.formation_plans,
                self.probe_plans,
            )

    def test_builder_calls_no_resolver_execution_or_writer(self) -> None:
        source = inspect.getsource(build_e1_common_probe_ec88_r4_r8_budget_inventory)
        for forbidden in (
            "resolve_e1_common_probe_real_slot(",
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "run_prepared_real_formation_arm_in_memory(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
