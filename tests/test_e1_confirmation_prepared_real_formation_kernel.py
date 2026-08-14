from __future__ import annotations

import inspect
import unittest

from mcm_field_organism.e1_confirmation_prepared_real_formation_kernel import (
    prepared_real_formation_kernel_digest,
    run_prepared_real_formation_arm_in_memory,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from tests.test_e1_a0_av_history_producer import contract, field, source


class E1ConfirmationPreparedRealFormationKernelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.field = field()
        self.state = build_neutral_e1_state(self.field.layer, contract())
        self.sequences = source().history_ab
        clock_id = self.sequences[0].clock_id
        self.proposals = (
            MCMFieldStepTime(clock_id, 0, 1_000_000, 1_000_000.0),
            MCMFieldStepTime(
                clock_id,
                1_000_000,
                2_000_000,
                1_000_000.0,
            ),
        )
        self.field_digest = _initial_field_digest(self.field)
        self.state_digest = _initial_state_digest(self.state)

    def test_active_real_arm_changes_copied_state_and_preserves_inputs(self) -> None:
        result = run_prepared_real_formation_arm_in_memory(
            "ab",
            "r2",
            self.sequences,
            self.proposals,
            self.field,
            self.state,
            True,
        )

        self.assertNotEqual(self.state, result.output_state)
        self.assertIsNot(self.state, result.output_state)
        self.assertEqual(self.field_digest, _initial_field_digest(self.field))
        self.assertEqual(self.state_digest, _initial_state_digest(self.state))
        self.assertTrue(result.input_objects_preserved)
        self.assertFalse(result.canonical_execution_permitted)

    def test_ablated_real_arm_remains_neutral_and_separate(self) -> None:
        result = run_prepared_real_formation_arm_in_memory(
            "ab_formation_ablated",
            "r2",
            self.sequences,
            self.proposals,
            self.field,
            self.state,
            False,
        )

        self.assertEqual(self.state, result.output_state)
        self.assertIsNot(self.state, result.output_state)
        self.assertTrue(
            all(item.binding == 0.0 for item in result.output_state.edge_bindings)
        )
        self.assertTrue(result.audit.state_remained_neutral)

    def test_real_kernel_digest_is_repeatable_on_fresh_copies(self) -> None:
        args = (
            "ab",
            "r2",
            self.sequences,
            self.proposals,
            self.field,
            self.state,
            True,
        )

        self.assertEqual(
            prepared_real_formation_kernel_digest(*args),
            prepared_real_formation_kernel_digest(*args),
        )

    def test_adapter_uses_real_core_but_no_builder_or_persistence(self) -> None:
        source_text = inspect.getsource(run_prepared_real_formation_arm_in_memory)

        self.assertIn("_run_arm(", source_text)
        for forbidden in (
            "build_e1_confirmation_research_corridor",
            "build_e1_av_history_permutation",
            "build_e1_confirmation_descriptor_refinement_plans",
            "_fresh_canonical_field",
            "build_neutral_e1_state",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source_text)


if __name__ == "__main__":
    unittest.main()
