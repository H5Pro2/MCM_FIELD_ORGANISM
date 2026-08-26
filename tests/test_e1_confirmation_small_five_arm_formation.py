from __future__ import annotations

import hashlib
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_confirmation_small_five_arm_formation import (
    run_small_five_arm_formation_in_memory,
)
from mcm_field_organism.e1_local_edge_plasticity import build_neutral_e1_state
from mcm_field_organism.e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from tests.test_e1_a0_av_history_producer import contract, field, source
from tests.test_e1_confirmation_typed_prepared_inputs import CANONICAL_TARGETS


class E1ConfirmationSmallFiveArmFormationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = source()
        self.field = field()
        self.state = build_neutral_e1_state(self.field.layer, contract())
        clock_id = self.source.history_ab[0].clock_id
        self.steps = (
            MCMFieldStepTime(clock_id, 0, 1_000_000, 1_000_000.0),
            MCMFieldStepTime(
                clock_id,
                1_000_000,
                2_000_000,
                1_000_000.0,
            ),
        )

    def _run(self):
        return run_small_five_arm_formation_in_memory(
            "r2",
            self.source.history_ab,
            self.source.history_ba,
            self.steps,
            self.steps,
            self.field,
            self.state,
        )

    def test_all_five_real_arm_controls_hold(self) -> None:
        result = self._run()

        self.assertTrue(result.ab_identity_repeated)
        self.assertTrue(result.ablation_states_neutral)
        self.assertTrue(result.output_states_object_separated)
        self.assertTrue(result.history_backreaction_field_controls_equal)
        self.assertTrue(result.resource_budget_preserved)
        self.assertLessEqual(result.maximum_resource_budget_error, 1e-12)
        self.assertFalse(result.canonical_execution_permitted)

    def test_five_arm_result_is_repeatable_and_preserves_inputs(self) -> None:
        field_digest = _initial_field_digest(self.field)
        state_digest = _initial_state_digest(self.state)

        first = self._run()
        second = self._run()

        self.assertEqual(first.result_digest, second.result_digest)
        self.assertEqual(field_digest, _initial_field_digest(self.field))
        self.assertEqual(state_digest, _initial_state_digest(self.state))
        self.assertTrue(first.prepared_inputs_preserved)

    def test_compositor_contains_no_builder_or_persistence_path(self) -> None:
        source_text = inspect.getsource(run_small_five_arm_formation_in_memory)

        self.assertEqual(
            1,
            source_text.count("run_prepared_real_formation_arm_in_memory("),
        )
        for forbidden in (
            "build_e1_confirmation_research_corridor",
            "build_e1_av_history_permutation",
            "build_neutral_e1_state",
            "write_text",
            "write_bytes",
            "report_path",
            "attempt_path",
            "lock_path",
        ):
            self.assertNotIn(forbidden, source_text)

    def test_terminal_s1eb31_artifacts_remain_unchanged(self) -> None:
        before = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )
        self._run()
        after = tuple(
            (
                path.exists(),
                hashlib.sha256(path.read_bytes()).hexdigest()
                if path.exists()
                else None,
            )
            for path in CANONICAL_TARGETS
        )

        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
