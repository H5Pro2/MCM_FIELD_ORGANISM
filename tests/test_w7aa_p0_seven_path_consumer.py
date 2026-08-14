from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7aa_p0_seven_path_consumer import (
    W7AAP0SevenPathConsumerError,
    consume_w7aa_p0_seven_path_plan,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7w_symmetric_source_family import (
    build_w7w_source_authorization,
    build_w7w_symmetric_source_family,
)
from mcm_field_organism.w7y_seven_path_source_plan import (
    build_w7y_seven_path_source_plan,
)


class W7AAP0SevenPathConsumerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.family = build_w7w_symmetric_source_family(cls.adapter)
        cls.authorization = build_w7w_source_authorization(
            cls.adapter,
            cls.family,
        )
        cls.plan = build_w7y_seven_path_source_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
        )
        cls.result = consume_w7aa_p0_seven_path_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
        )

    def test_global_result_binding_and_digest_are_frozen(self) -> None:
        self.assertEqual(
            "w7aa.p0-seven-path-consumer.v1",
            self.result.consumer_id,
        )
        self.assertEqual(
            self.plan.seven_path_plan_digest,
            self.result.plan_digest,
        )
        self.assertEqual(
            "2303230f9dfc2837d0043c6e1b6c7e0aa72042ff6c271eb025a971d4501c0440",
            self.result.p0_seven_path_consumption_digest,
        )

    def test_all_seven_paths_and_expected_main_counts_are_present(self) -> None:
        self.assertEqual(
            ("ab", "ag", "ba", "bg", "ua", "ub", "ug"),
            tuple(item.path_id for item in self.result.path_results),
        )
        self.assertEqual(
            (5, 5, 5, 5, 4, 4, 4),
            tuple(len(item.main_productions) for item in self.result.path_results),
        )
        self.assertTrue(
            all(len(item.checkpoints) == 5 for item in self.result.path_results)
        )

    def test_contact_and_u_starts_are_separate_zero_fast_states(self) -> None:
        starts = [item.initial_state for item in self.result.path_results]

        self.assertEqual(
            (0, 0, 0, 0, 4_000_000, 4_000_000, 4_000_000),
            tuple(item.end_tick for item in starts),
        )
        self.assertEqual(7, len({id(item) for item in starts}))
        self.assertEqual(7, len({id(item.p0_field) for item in starts}))
        for state in starts:
            self.assertEqual((0.0,) * 84, state.s_values)
            self.assertEqual((0.0,) * 84, state.h_values)
            self.assertIsNone(state.p0_field.substrate)
            self.assertIsNone(state.p0_field.development)

    def test_main_productions_follow_w7y_segments_exactly(self) -> None:
        for plan_path, result_path in zip(
            self.plan.paths,
            self.result.path_results,
            strict=True,
        ):
            segments = (
                (() if plan_path.prefix is None else (plan_path.prefix,))
                + plan_path.continuations
            )
            self.assertEqual(
                tuple(item.source_digest for item in segments),
                tuple(
                    item.source_digest for item in result_path.main_productions
                ),
            )
            self.assertEqual(
                tuple(item.interval for item in segments),
                tuple(item.interval for item in result_path.main_productions),
            )

    def test_every_main_chain_is_contiguous_and_ends_at_tick_eight(self) -> None:
        for path in self.result.path_results:
            previous = path.initial_state
            for production in path.main_productions:
                self.assertIs(previous, production.initial_state)
                self.assertEqual(previous.end_tick, production.interval[0])
                previous = production.end_state
            self.assertIs(previous, path.terminal_main_state)
            self.assertEqual(8_000_000, previous.end_tick)

    def test_checkpoint_probe_starts_are_digest_equal_but_object_distinct(self) -> None:
        for path in self.result.path_results:
            for checkpoint in path.checkpoints:
                main = checkpoint.main_state
                probe = checkpoint.probe_initial_state
                self.assertEqual(main.state_digest, probe.state_digest)
                self.assertEqual(main.s_values, probe.s_values)
                self.assertEqual(main.h_values, probe.h_values)
                self.assertIsNot(main, probe)
                self.assertIsNot(main.p0_field, probe.p0_field)
                self.assertIsNot(main.p0_field.layer, probe.p0_field.layer)
                self.assertIsNot(main.p0_field.docks, probe.p0_field.docks)

    def test_probe_productions_are_isolated_and_match_checkpoint_plans(self) -> None:
        for plan_path, result_path in zip(
            self.plan.paths,
            self.result.path_results,
            strict=True,
        ):
            for plan_checkpoint, checkpoint in zip(
                plan_path.checkpoints,
                result_path.checkpoints,
                strict=True,
            ):
                production = checkpoint.probe_production
                self.assertIs(
                    checkpoint.probe_initial_state,
                    production.initial_state,
                )
                self.assertEqual(
                    plan_checkpoint.probe.source_digest,
                    production.source_digest,
                )
                self.assertEqual(
                    plan_checkpoint.probe.interval,
                    production.interval,
                )
                self.assertIsNot(
                    checkpoint.main_state.p0_field,
                    production.end_state.p0_field,
                )

    def test_every_reachable_p0_state_is_substrate_and_development_free(self) -> None:
        states = []
        for path in self.result.path_results:
            states.extend((path.initial_state, path.terminal_main_state))
            for production in path.main_productions:
                states.extend((production.initial_state, production.end_state))
            for checkpoint in path.checkpoints:
                states.extend(
                    (
                        checkpoint.main_state,
                        checkpoint.probe_initial_state,
                        checkpoint.probe_production.end_state,
                    )
                )
        self.assertTrue(states)
        self.assertTrue(
            all(
                state.p0_field.substrate is None
                and state.p0_field.development is None
                for state in states
            )
        )

    def test_order_countercontrol_matches_actual_ab_branches(self) -> None:
        countercontrol = self.result.order_countercontrol
        ab = self.result.path_results[0]

        self.assertEqual("ab", countercontrol.path_id)
        self.assertEqual(0, countercontrol.checkpoint)
        self.assertEqual(
            ab.main_productions[1].production_digest,
            countercontrol.main_production_digest,
        )
        self.assertEqual(
            ab.checkpoints[0].probe_production.production_digest,
            countercontrol.probe_production_digest,
        )

    def test_repeated_consumption_is_exact_and_leaves_inputs_unchanged(self) -> None:
        matrix_digest = self.adapter.matrix_digest
        plan_digest = self.plan.seven_path_plan_digest
        layer_digest = self.adapter.initial_field.layer.digest()
        repeated = consume_w7aa_p0_seven_path_plan(
            self.adapter,
            self.family,
            self.authorization,
            self.plan,
        )

        self.assertEqual(
            self.result.p0_seven_path_consumption_digest,
            repeated.p0_seven_path_consumption_digest,
        )
        self.assertEqual(
            tuple(
                item.p0_path_consumption_digest
                for item in self.result.path_results
            ),
            tuple(
                item.p0_path_consumption_digest
                for item in repeated.path_results
            ),
        )
        self.assertEqual(matrix_digest, self.adapter.matrix_digest)
        self.assertEqual(plan_digest, self.plan.seven_path_plan_digest)
        self.assertEqual(layer_digest, self.adapter.initial_field.layer.digest())
        self.assertIsNone(self.adapter.initial_field.last_distribution)

    def test_tampered_checkpoint_path_and_global_digests_are_rejected(self) -> None:
        path = self.result.path_results[0]
        with self.assertRaisesRegex(
            W7AAP0SevenPathConsumerError,
            "checkpoint result digest",
        ):
            replace(path.checkpoints[0], checkpoint_result_digest="changed")
        with self.assertRaisesRegex(
            W7AAP0SevenPathConsumerError,
            "path consumption digest",
        ):
            replace(path, p0_path_consumption_digest="changed")
        with self.assertRaisesRegex(
            W7AAP0SevenPathConsumerError,
            "seven-path consumption digest",
        ):
            replace(self.result, p0_seven_path_consumption_digest="changed")

    def test_invalid_bindings_are_rejected_before_consumption(self) -> None:
        with self.assertRaisesRegex(
            W7AAP0SevenPathConsumerError,
            "requires complete",
        ):
            consume_w7aa_p0_seven_path_plan(
                self.adapter,
                self.family,
                self.authorization,
                object(),
            )

    def test_module_is_not_reexported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        for name in (
            "consume_w7aa_p0_seven_path_plan",
            "W7AAP0SevenPathResult",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))


if __name__ == "__main__":
    unittest.main()
