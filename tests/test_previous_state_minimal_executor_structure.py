from __future__ import annotations

from dataclasses import replace
import unittest

import mcm_field_organism
from mcm_field_organism._previous_state_minimal_executor_structure import (
    build_locked_executor_structure,
    simulate_locked_abort,
)
from mcm_field_organism._previous_state_minimal_runner import (
    PreviousStateMinimalRunnerError,
    build_locked_previous_state_minimal_manifest,
)


class PreviousStateMinimalExecutorStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = build_locked_previous_state_minimal_manifest()
        self.structure = build_locked_executor_structure(self.manifest)

    def test_twenty_four_fresh_contexts_and_fixed_call_order(self) -> None:
        self.assertEqual(len(self.structure.runs), 24)
        tokens = tuple(run.context_token for run in self.structure.runs)
        self.assertEqual(len({id(token) for token in tokens}), 24)
        expected_roles = (
            "M0",
            "history",
            "history",
            "history",
            "M1",
            "c_distribution",
            "M2",
            "c_hook",
            "M3",
        )
        for run in self.structure.runs:
            self.assertEqual(tuple(call.role for call in run.calls), expected_roles)

    def test_history_never_uses_hook_and_c_uses_it_exactly_once(self) -> None:
        arms = {arm.run_id: arm for arm in self.manifest.arms}
        for run in self.structure.runs:
            history = tuple(call for call in run.calls if call.role == "history")
            hooks = tuple(call for call in run.calls if call.role == "c_hook")
            self.assertEqual(len(history), 3)
            self.assertTrue(all(call.operator is None for call in history))
            self.assertEqual(len(hooks), 1)
            self.assertEqual(hooks[0].contact_id, "contact.c.e1")
            self.assertEqual(hooks[0].operator, arms[run.run_id].previous_state_operator)

    def test_every_declared_field_call_has_explicit_none_dissipation(self) -> None:
        for run in self.structure.runs:
            field_calls = tuple(
                call for call in run.calls if call.role in {"history", "c_hook"}
            )
            self.assertEqual(len(field_calls), 4)
            self.assertTrue(all(call.dissipation_config is None for call in field_calls))

    def test_measurements_remain_unpublished(self) -> None:
        self.assertTrue(self.structure.execution_locked)
        self.assertFalse(self.structure.measurements_published)
        self.assertFalse(
            any(hasattr(call, "measurement") for run in self.structure.runs for call in run.calls)
        )

    def test_all_twelve_abort_conditions_stop_at_fixed_checkpoints(self) -> None:
        self.assertEqual(len(self.structure.abort_condition_ids), 12)
        total_calls = sum(len(run.calls) for run in self.structure.runs)
        for condition_id in self.structure.abort_condition_ids:
            with self.subTest(condition_id=condition_id):
                aborted = simulate_locked_abort(self.structure, condition_id)
                self.assertLess(len(aborted.calls_before_abort), total_calls)
                self.assertFalse(aborted.further_runs_started)
                self.assertFalse(aborted.measurements_published)

    def test_mutated_calls_run_order_and_abort_list_are_rejected(self) -> None:
        first_run = self.structure.runs[0]
        first_call = first_run.calls[0]
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "fixed executor calls"
        ):
            replace(
                first_run,
                calls=(replace(first_call, role="M1"), *first_run.calls[1:]),
            )
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "fixed executor calls"
        ):
            replace(
                first_run,
                calls=(
                    first_run.calls[0],
                    replace(first_run.calls[1], contact_id="changed"),
                    *first_run.calls[2:],
                ),
            )
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "executor run order"
        ):
            replace(self.structure, runs=tuple(reversed(self.structure.runs)))
        with self.assertRaisesRegex(
            PreviousStateMinimalRunnerError, "executor abort conditions"
        ):
            replace(
                self.structure,
                abort_condition_ids=self.structure.abort_condition_ids[:-1],
            )

    def test_structure_helpers_are_not_publicly_exported(self) -> None:
        self.assertFalse(hasattr(mcm_field_organism, "build_locked_executor_structure"))
        self.assertFalse(hasattr(mcm_field_organism, "simulate_locked_abort"))


if __name__ == "__main__":
    unittest.main()
