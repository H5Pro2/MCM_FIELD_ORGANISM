from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7n_capacity_function_baselines import (
    advance_w7n_local_baseline,
)
from mcm_field_organism.w7r_p0_s_completion_producer import (
    build_initial_w7r_p0_state,
    compose_w7r_observer_driver,
    produce_w7r_p0_s_completion_states,
)
from mcm_field_organism.w7t_observer_continuation import (
    W7TObserverContinuationError,
    advance_w7t_observer_continuation,
    branch_w7t_observer_state,
    build_initial_w7t_observer_state,
    checkpoint_w7t_observer_state,
)


class W7TObserverContinuationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.source = cls.adapter.source
        p0_initial = build_initial_w7r_p0_state(cls.adapter, "ub", 4_000_000)
        cls.first_production = produce_w7r_p0_s_completion_states(
            cls.adapter,
            cls.source.contact_b_step_digests[0],
            cls.source.contact_b_steps[0],
            (4_000_000, 5_000_000),
            p0_initial,
        )
        cls.second_production = produce_w7r_p0_s_completion_states(
            cls.adapter,
            cls.source.contact_b_step_digests[1],
            cls.source.contact_b_steps[1],
            (5_000_000, 6_000_000),
            cls.first_production.end_state,
        )
        cls.first_driver = compose_w7r_observer_driver(
            cls.adapter, cls.first_production
        )
        cls.second_driver = compose_w7r_observer_driver(
            cls.adapter, cls.second_production
        )

    def _chain(self, model_id: str):
        initial = build_initial_w7t_observer_state(
            self.adapter, "ub", model_id, 4_000_000
        )
        first = advance_w7t_observer_continuation(
            self.adapter,
            initial,
            self.first_production,
            self.first_driver,
        )
        second = advance_w7t_observer_continuation(
            self.adapter,
            first.next_state,
            self.second_production,
            self.second_driver,
        )
        return initial, first, second

    def test_each_model_has_one_independent_zero_start(self) -> None:
        states = tuple(
            build_initial_w7t_observer_state(
                self.adapter, "ub", model_id, 4_000_000
            )
            for model_id in ("leak", "sat", "norm")
        )

        self.assertEqual({"leak", "sat", "norm"}, {item.model_id for item in states})
        self.assertTrue(all(set(item.baseline_state.latent) == {0.0} for item in states))
        self.assertEqual(3, len({item.state_digest for item in states}))

    def test_all_models_receive_the_same_driver_digest_sequence(self) -> None:
        chains = tuple(self._chain(model_id) for model_id in ("leak", "sat", "norm"))

        self.assertEqual(
            {(self.first_driver.driver_digest, self.second_driver.driver_digest)},
            {item[2].next_state.processed_driver_digests for item in chains},
        )
        self.assertEqual(3, len({item[2].next_state.state_digest for item in chains}))

    def test_segmented_continuation_matches_direct_exact_kernel_updates(self) -> None:
        _, first, second = self._chain("leak")
        spec = {item.model_id: item for item in self.adapter.baselines}["leak"]
        direct = first.previous_state.baseline_state
        for driver in (self.first_driver, self.second_driver):
            for segment in driver.segments:
                direct = advance_w7n_local_baseline(
                    spec,
                    direct,
                    segment.s_values,
                    (segment.end_tick - segment.start_tick) / driver.ticks_per_second,
                ).state

        self.assertEqual(direct.latent, second.next_state.baseline_state.latent)

    def test_norm_continues_latent_state_not_normalized_output(self) -> None:
        _, first, second = self._chain("norm")

        self.assertNotEqual(
            first.measurement.observer_output_trace[-1],
            first.next_state.baseline_state.latent,
        )
        self.assertEqual(
            first.next_state.state_digest,
            second.previous_state.state_digest,
        )
        self.assertNotEqual(
            second.next_state.baseline_state.latent,
            second.measurement.observer_output_trace[-1],
        )

    def test_checkpoint_is_passive_and_keeps_state_digest(self) -> None:
        _, first, _ = self._chain("sat")
        before = first.next_state.state_digest
        checkpoint = checkpoint_w7t_observer_state(first.next_state, 1)

        self.assertEqual(before, checkpoint.state_digest)
        self.assertEqual(before, first.next_state.state_digest)
        self.assertEqual(5_000_000, checkpoint.end_tick)

    def test_branch_copies_prefix_into_independent_path_bindings(self) -> None:
        prefix = build_initial_w7t_observer_state(
            self.adapter, "ua", "leak", 4_000_000
        )
        ub, ug = branch_w7t_observer_state(
            self.adapter, prefix, ("ub", "ug")
        )

        self.assertEqual(ub.baseline_state, ug.baseline_state)
        self.assertEqual(prefix.state_digest, ub.branch_source_state_digest)
        self.assertEqual(prefix.state_digest, ug.branch_source_state_digest)
        self.assertNotEqual(ub.state_digest, ug.state_digest)
        self.assertIsNot(ub, ug)

    def test_continuation_is_exactly_deterministic(self) -> None:
        initial = build_initial_w7t_observer_state(
            self.adapter, "ub", "leak", 4_000_000
        )
        first = advance_w7t_observer_continuation(
            self.adapter, initial, self.first_production, self.first_driver
        )
        repeated = advance_w7t_observer_continuation(
            self.adapter, initial, self.first_production, self.first_driver
        )

        self.assertEqual(first, repeated)
        self.assertEqual(first.continuation_digest, repeated.continuation_digest)

    def test_duplicate_driver_and_noncontiguous_interval_are_rejected(self) -> None:
        _, first, _ = self._chain("leak")
        with self.assertRaisesRegex(W7TObserverContinuationError, "already processed"):
            advance_w7t_observer_continuation(
                self.adapter,
                first.next_state,
                self.first_production,
                self.first_driver,
            )
        initial = build_initial_w7t_observer_state(
            self.adapter, "ub", "leak", 4_000_000
        )
        with self.assertRaisesRegex(W7TObserverContinuationError, "not contiguous"):
            advance_w7t_observer_continuation(
                self.adapter,
                initial,
                self.second_production,
                self.second_driver,
            )

    def test_model_and_path_crossing_are_rejected(self) -> None:
        valid = build_initial_w7t_observer_state(
            self.adapter, "ub", "sat", 4_000_000
        )
        wrong_path = build_initial_w7t_observer_state(
            self.adapter, "ug", "leak", 4_000_000
        )
        with self.assertRaisesRegex(W7TObserverContinuationError, "state digest"):
            replace(
                valid,
                equation_id="changed",
                state_digest=valid.state_digest,
            )
        with self.assertRaisesRegex(W7TObserverContinuationError, "source path"):
            advance_w7t_observer_continuation(
                self.adapter,
                wrong_path,
                self.first_production,
                self.first_driver,
            )

    def test_inputs_remain_unchanged(self) -> None:
        initial = build_initial_w7t_observer_state(
            self.adapter, "ub", "leak", 4_000_000
        )
        state_digest = initial.state_digest
        production_digest = self.first_production.production_digest
        driver_digest = self.first_driver.driver_digest

        advance_w7t_observer_continuation(
            self.adapter, initial, self.first_production, self.first_driver
        )

        self.assertEqual(state_digest, initial.state_digest)
        self.assertEqual(production_digest, self.first_production.production_digest)
        self.assertEqual(driver_digest, self.first_driver.driver_digest)

    def test_module_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "advance_w7t_observer_continuation"))
        self.assertFalse(hasattr(current_api, "branch_w7t_observer_state"))


if __name__ == "__main__":
    unittest.main()
