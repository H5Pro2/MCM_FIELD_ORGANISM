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
    build_e1_common_probe_ec88_r4_r8_budget_inventory,
)
from mcm_field_organism.e1_common_probe_ec89_r4_r8_object_handoffs import (
    E1CommonProbeEC89R4R8ObjectHandoffsError,
    prepare_e1_common_probe_ec89_r4_r8_object_handoffs,
)
from tests.test_e1_common_probe_n2_r2_object_handoff import (
    E1CommonProbeN2R2ObjectHandoffTests,
)


class E1CommonProbeEC89R4R8ObjectHandoffsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        E1CommonProbeN2R2ObjectHandoffTests.setUpClass()
        cls.source = E1CommonProbeN2R2ObjectHandoffTests
        complement = build_e1_common_probe_ec87_r2_ec46_complement_contract(
            cls.root, build_e1_common_probe_acceptance_contract()
        )
        cls.inventory = build_e1_common_probe_ec88_r4_r8_budget_inventory(
            complement,
            cls.source.contract,
            cls.source.formation_plans,
            cls.source.inputs.probe_plans,
        )

    def _prepare(self, **kwargs):
        return prepare_e1_common_probe_ec89_r4_r8_object_handoffs(
            self.inventory,
            self.source.contract,
            self.source.formation_plans,
            self.source.inputs.probe_sequences,
            self.source.inputs.probe_plans,
            self.source.inputs.initial_field,
            self.source.inputs.initial_state,
            **kwargs,
        )

    def test_r4_and_r8_objects_are_resolved_without_steps(self) -> None:
        result = self._prepare()
        self.assertEqual(("r4", "r8"), result.refinement_ids)
        self.assertEqual((6416, 12832), tuple(
            item.maximum_total_steps for item in result.handoffs
        ))
        self.assertTrue(all(len(item.resolved_slots) == 8 for item in result.handoffs))
        self.assertTrue(all(len(item.formation_slots) == 4 for item in result.handoffs))
        self.assertEqual(0, result.field_steps_executed)
        self.assertFalse(result.execution_permitted)

    def test_initial_objects_are_carried_by_identity(self) -> None:
        result = self._prepare()
        self.assertTrue(all(
            item.initial_field is self.source.inputs.initial_field
            and item.initial_state is self.source.inputs.initial_state
            for item in result.handoffs
        ))
        self.assertTrue(result.all_handoffs_object_separate)

    def test_untyped_resolver_result_fails_closed(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeEC89R4R8ObjectHandoffsError, "resolver lost"
        ):
            self._prepare(resolver=lambda *args: None)

    def test_builder_calls_no_field_path_or_writer(self) -> None:
        source = inspect.getsource(prepare_e1_common_probe_ec89_r4_r8_object_handoffs)
        for forbidden in (
            "run_prepared_real_formation_arm_in_memory(",
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_neutral_fast_shared_field_transient(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
