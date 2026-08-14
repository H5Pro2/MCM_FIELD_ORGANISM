from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7aa_p0_seven_path_consumer import (
    consume_w7aa_p0_seven_path_plan,
)
from mcm_field_organism.w7ac_observer_seven_path_consumer import (
    W7ACObserverSevenPathConsumerError,
    consume_w7ac_observer_seven_path_result,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7p_measurement_compositor import (
    W7PMeasurementCompositorError,
)
from mcm_field_organism.w7r_p0_s_completion_producer import (
    compose_w7r_observer_driver,
)
from mcm_field_organism.w7w_symmetric_source_family import (
    build_w7w_source_authorization,
    build_w7w_symmetric_source_family,
)
from mcm_field_organism.w7y_seven_path_source_plan import (
    build_w7y_seven_path_source_plan,
)


class W7ACObserverSevenPathConsumerTests(unittest.TestCase):
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
        cls.p0_result = consume_w7aa_p0_seven_path_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
        )
        cls.result = consume_w7ac_observer_seven_path_result(
            cls.adapter,
            cls.authorization,
            cls.plan,
            cls.p0_result,
        )

    def test_global_result_binding_and_digest_are_frozen(self) -> None:
        self.assertEqual(
            "w7ac.observer-seven-path-consumer.v1",
            self.result.consumer_id,
        )
        self.assertEqual(
            self.p0_result.p0_seven_path_consumption_digest,
            self.result.p0_consumption_digest,
        )
        self.assertEqual(
            "8c3c296ddbb911346fa649a9e7529f9be86abb67444b4041ee76c8745d778ad7",
            self.result.observer_seven_path_consumption_digest,
        )

    def test_twenty_one_canonical_model_path_results_are_present(self) -> None:
        self.assertEqual(
            tuple(
                (path_id, model_id)
                for path_id in ("ab", "ag", "ba", "bg", "ua", "ub", "ug")
                for model_id in ("leak", "sat", "norm")
            ),
            tuple(
                (item.path_id, item.model_id)
                for item in self.result.model_path_results
            ),
        )
        self.assertEqual(
            105,
            sum(len(item.checkpoints) for item in self.result.model_path_results),
        )

    def test_contact_and_u_observers_start_once_at_bound_ticks(self) -> None:
        for result in self.result.model_path_results:
            expected_tick = 4_000_000 if result.path_id.startswith("u") else 0
            self.assertEqual(expected_tick, result.initial_state.end_tick)
            self.assertEqual((), result.initial_state.processed_driver_digests)
            self.assertEqual(
                {0.0},
                set(result.initial_state.baseline_state.latent),
            )

    def test_all_models_of_one_path_share_the_same_driver_objects(self) -> None:
        for offset in range(0, 21, 3):
            leak, sat, norm = self.result.model_path_results[offset : offset + 3]
            self.assertIs(leak.main_drivers, sat.main_drivers)
            self.assertIs(leak.main_drivers, norm.main_drivers)
            self.assertEqual(
                tuple(item.driver_digest for item in leak.main_drivers),
                tuple(item.driver_digest for item in sat.main_drivers),
            )
            for checkpoint_index in range(5):
                self.assertIs(
                    leak.checkpoints[checkpoint_index].probe_driver,
                    sat.checkpoints[checkpoint_index].probe_driver,
                )
                self.assertIs(
                    leak.checkpoints[checkpoint_index].probe_driver,
                    norm.checkpoints[checkpoint_index].probe_driver,
                )

    def test_main_observer_chains_are_contiguous_and_end_at_tick_eight(self) -> None:
        for result in self.result.model_path_results:
            previous = result.initial_state
            for continuation in result.main_continuations:
                self.assertIs(previous, continuation.previous_state)
                previous = continuation.next_state
            self.assertIs(previous, result.terminal_state)
            self.assertEqual(8_000_000, previous.end_tick)
            self.assertEqual(
                tuple(item.driver_digest for item in result.main_drivers),
                previous.processed_driver_digests,
            )

    def test_probe_envelopes_are_digest_equal_but_object_distinct(self) -> None:
        for result in self.result.model_path_results:
            for checkpoint in result.checkpoints:
                main = checkpoint.main_state
                copied = checkpoint.probe_envelope.copied_state
                self.assertEqual(main.state_digest, copied.state_digest)
                self.assertEqual(
                    main.baseline_state.latent,
                    copied.baseline_state.latent,
                )
                self.assertIsNot(main, copied)
                self.assertIsNot(main.baseline_state, copied.baseline_state)
                self.assertIs(
                    copied,
                    checkpoint.probe_continuation.previous_state,
                )

    def test_passive_checkpoints_and_probes_do_not_change_main_states(self) -> None:
        for result in self.result.model_path_results:
            for checkpoint in result.checkpoints:
                self.assertEqual(
                    checkpoint.main_state.state_digest,
                    checkpoint.passive_checkpoint.state_digest,
                )
                self.assertEqual(
                    checkpoint.main_state.state_digest,
                    checkpoint.probe_envelope.source_state_digest,
                )
                self.assertIsNot(
                    checkpoint.main_state,
                    checkpoint.probe_continuation.next_state,
                )

    def test_probe_driver_and_production_bindings_match_w7aa(self) -> None:
        p0_paths = {item.path_id: item for item in self.p0_result.path_results}
        for result in self.result.model_path_results:
            p0_path = p0_paths[result.path_id]
            for index, checkpoint in enumerate(result.checkpoints):
                production = p0_path.checkpoints[index].probe_production
                self.assertEqual(
                    production.production_digest,
                    checkpoint.probe_continuation.production_digest,
                )
                self.assertEqual(
                    production.source_digest,
                    checkpoint.probe_driver.source_digest,
                )

    def test_norm_continues_latent_state_not_normalized_output(self) -> None:
        norm_results = [
            item for item in self.result.model_path_results if item.model_id == "norm"
        ]
        for result in norm_results:
            for continuation in result.main_continuations:
                self.assertNotEqual(
                    continuation.next_state.baseline_state.latent,
                    continuation.measurement.observer_output_trace[-1],
                )

    def test_only_observer_measurement_roles_are_exposed(self) -> None:
        measurement_fields = {
            "model_id",
            "driver_digest",
            "observer_output_linf",
            "observer_output_trajectory_l2",
            "observer_state_linf",
            "observer_ticks",
            "observer_output_trace",
        }
        for result in self.result.model_path_results:
            for continuation in result.main_continuations:
                self.assertEqual(
                    measurement_fields,
                    set(continuation.measurement.__dataclass_fields__),
                )

    def test_additive_driver_gate_requires_the_exact_authorization(self) -> None:
        ba_prefix = self.p0_result.path_results[2].main_productions[0]
        with self.assertRaisesRegex(
            W7PMeasurementCompositorError,
            "not bound",
        ):
            compose_w7r_observer_driver(self.adapter, ba_prefix)

        driver = compose_w7r_observer_driver(
            self.adapter,
            ba_prefix,
            source_authorization=self.authorization,
        )
        self.assertEqual(ba_prefix.source_digest, driver.source_digest)

    def test_countercontrols_bind_model_and_main_probe_order(self) -> None:
        controls = self.result.countercontrols
        ab = self.result.model_path_results[:3]

        self.assertEqual(
            tuple(item.observer_path_consumption_digest for item in ab),
            controls.model_order_digests,
        )
        self.assertEqual(
            ab[0].main_continuations[1].continuation_digest,
            controls.main_continuation_digest,
        )
        self.assertEqual(
            ab[0].checkpoints[0].probe_continuation.continuation_digest,
            controls.probe_continuation_digest,
        )

    def test_repeated_observer_consumption_is_exact_and_keeps_p0_unchanged(
        self,
    ) -> None:
        p0_digest = self.p0_result.p0_seven_path_consumption_digest
        repeated = consume_w7ac_observer_seven_path_result(
            self.adapter,
            self.authorization,
            self.plan,
            self.p0_result,
        )

        self.assertEqual(
            self.result.observer_seven_path_consumption_digest,
            repeated.observer_seven_path_consumption_digest,
        )
        self.assertEqual(
            tuple(
                item.observer_path_consumption_digest
                for item in self.result.model_path_results
            ),
            tuple(
                item.observer_path_consumption_digest
                for item in repeated.model_path_results
            ),
        )
        self.assertEqual(
            p0_digest,
            self.p0_result.p0_seven_path_consumption_digest,
        )

    def test_tampered_envelope_path_and_global_digests_are_rejected(self) -> None:
        result = self.result.model_path_results[0]
        with self.assertRaisesRegex(
            W7ACObserverSevenPathConsumerError,
            "envelope digest",
        ):
            replace(result.checkpoints[0].probe_envelope, envelope_digest="changed")
        with self.assertRaisesRegex(
            W7ACObserverSevenPathConsumerError,
            "path consumption digest",
        ):
            replace(result, observer_path_consumption_digest="changed")
        with self.assertRaisesRegex(
            W7ACObserverSevenPathConsumerError,
            "seven-path consumption digest",
        ):
            replace(
                self.result,
                observer_seven_path_consumption_digest="changed",
            )

    def test_invalid_inputs_and_public_exports_remain_closed(self) -> None:
        with self.assertRaisesRegex(
            W7ACObserverSevenPathConsumerError,
            "requires complete",
        ):
            consume_w7ac_observer_seven_path_result(
                self.adapter,
                self.authorization,
                self.plan,
                object(),
            )
        import mcm_field_organism
        from mcm_field_organism import current_api

        for name in (
            "consume_w7ac_observer_seven_path_result",
            "W7ACObserverSevenPathResult",
        ):
            self.assertFalse(hasattr(mcm_field_organism, name))
            self.assertFalse(hasattr(current_api, name))


if __name__ == "__main__":
    unittest.main()
