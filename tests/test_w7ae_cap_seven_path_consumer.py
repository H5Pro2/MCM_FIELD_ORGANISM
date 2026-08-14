from __future__ import annotations

from dataclasses import replace
import math
import unittest

from mcm_field_organism.w7aa_p0_seven_path_consumer import (
    consume_w7aa_p0_seven_path_plan,
)
from mcm_field_organism.w7ac_observer_seven_path_consumer import (
    consume_w7ac_observer_seven_path_result,
)
from mcm_field_organism.w7ae_cap_seven_path_consumer import (
    W7AECAPSevenPathConsumerError,
    consume_w7ae_cap_seven_path_plan,
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


class W7AECAPSevenPathConsumerTests(unittest.TestCase):
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
        cls.observer_result = consume_w7ac_observer_seven_path_result(
            cls.adapter,
            cls.authorization,
            cls.plan,
            cls.p0_result,
        )
        cls.result = consume_w7ae_cap_seven_path_plan(
            cls.adapter,
            cls.family,
            cls.authorization,
            cls.plan,
            cls.p0_result,
            cls.observer_result,
        )

    def test_global_result_and_digest_are_bound(self) -> None:
        self.assertEqual(
            "w7ae.cap-seven-path-consumer.v1",
            self.result.consumer_id,
        )
        self.assertEqual(
            "b70a4b4563bb73d50685d1a8475376f0b00377d72369c030027f44f2725af013",
            self.result.cap_seven_path_consumption_digest,
        )
        self.assertEqual(
            self.plan.seven_path_plan_digest,
            self.result.plan_digest,
        )

    def test_seven_paths_have_32_main_and_35_probe_productions(self) -> None:
        self.assertEqual(
            ("ab", "ag", "ba", "bg", "ua", "ub", "ug"),
            tuple(item.path_id for item in self.result.path_results),
        )
        self.assertEqual(
            (5, 5, 5, 5, 4, 4, 4),
            tuple(len(item.main_productions) for item in self.result.path_results),
        )
        self.assertEqual(
            35,
            sum(len(item.checkpoints) for item in self.result.path_results),
        )

    def test_main_productions_follow_w7y_sources_and_intervals(self) -> None:
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
                tuple(item.segment_digest for item in segments),
                tuple(item.segment_digest for item in result_path.main_productions),
            )
            self.assertEqual(
                tuple(item.interval for item in segments),
                tuple(item.interval for item in result_path.main_productions),
            )

    def test_initial_and_completed_binding_roles_are_exact(self) -> None:
        for path in self.result.path_results:
            self.assertIsNone(path.initial_state.continuation_binding)
            self.assertIsNone(path.initial_state.field.last_distribution)
            checkpoint_zero = path.checkpoints[0]
            if path.path_id.startswith("u"):
                self.assertIsNone(checkpoint_zero.main_state.continuation_binding)
            else:
                self.assertIsNotNone(checkpoint_zero.main_state.continuation_binding)
            for production in path.main_productions:
                binding = production.end_state.continuation_binding
                self.assertIsNotNone(binding)
                self.assertEqual(
                    production.end_state.field.snapshot().digest(),
                    binding.snapshot_digest,
                )

    def test_checkpoint_copies_are_deep_and_digest_equal(self) -> None:
        for path in self.result.path_results:
            for checkpoint in path.checkpoints:
                main = checkpoint.main_state
                probe = checkpoint.probe_initial_state
                self.assertEqual(main.state_digest, probe.state_digest)
                self.assertIsNot(main, probe)
                self.assertIsNot(main.field, probe.field)
                self.assertIsNot(main.field.layer, probe.field.layer)
                self.assertIsNot(main.field.docks, probe.field.docks)
                self.assertIsNot(main.field.substrate, probe.field.substrate)
                if main.continuation_binding is not None:
                    self.assertIsNot(
                        main.continuation_binding,
                        probe.continuation_binding,
                    )

    def test_mass_capacity_geometry_and_model_arm_are_preserved(self) -> None:
        capacity = self.adapter.runtime_contract.site_capacity
        edge_digest = self.adapter.initial_field.substrate.edge_inventory_digest
        for path in self.result.path_results:
            states = [path.initial_state, path.terminal_main_state]
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
            for state in states:
                substrate = state.field.substrate
                masses = tuple(item.mass for item in substrate.masses)
                self.assertEqual("w7m.cap", substrate.arm.arm_id)
                self.assertAlmostEqual(1.0, math.fsum(masses), places=12)
                self.assertGreaterEqual(min(masses), 0.0)
                self.assertLessEqual(max(masses), capacity + 1e-12)
                self.assertEqual(edge_digest, substrate.edge_inventory_digest)

    def test_main_and_probe_chains_are_contiguous_and_isolated(self) -> None:
        for path in self.result.path_results:
            previous = path.initial_state
            for production in path.main_productions:
                self.assertIs(previous, production.initial_state)
                previous = production.end_state
            self.assertIs(previous, path.terminal_main_state)
            self.assertEqual(8_000_000, previous.tick)
            for checkpoint in path.checkpoints:
                self.assertIs(
                    checkpoint.probe_initial_state,
                    checkpoint.probe_production.initial_state,
                )
                self.assertIsNot(
                    checkpoint.probe_production.end_state,
                    checkpoint.main_state,
                )

    def test_order_countercontrols_bind_canonical_results(self) -> None:
        controls = self.result.countercontrols
        self.assertEqual(
            tuple(
                item.cap_path_consumption_digest
                for item in self.result.path_results
            ),
            controls.path_digests,
        )
        ab = self.result.path_results[0]
        self.assertEqual(
            ab.main_productions[1].production_digest,
            controls.main_production_digest,
        )
        self.assertEqual(
            ab.checkpoints[0].probe_production.production_digest,
            controls.probe_production_digest,
        )

    def test_p0_observer_plan_and_initial_adapter_remain_unchanged(self) -> None:
        self.assertEqual(
            self.p0_result.p0_seven_path_consumption_digest,
            self.result.p0_consumption_digest,
        )
        self.assertEqual(
            self.observer_result.observer_seven_path_consumption_digest,
            self.result.observer_consumption_digest,
        )
        self.assertEqual(
            "c771a3c28c04e04a61fa24d187416ef65b17597f9af759682deb576a28c25b32",
            self.plan.seven_path_plan_digest,
        )
        self.assertIsNone(self.adapter.initial_field.last_distribution)

    def test_tampered_checkpoint_path_and_global_digests_are_rejected(self) -> None:
        path = self.result.path_results[0]
        with self.assertRaisesRegex(
            W7AECAPSevenPathConsumerError,
            "checkpoint digest",
        ):
            replace(path.checkpoints[0], checkpoint_result_digest="changed")
        with self.assertRaisesRegex(
            W7AECAPSevenPathConsumerError,
            "path consumption digest",
        ):
            replace(path, cap_path_consumption_digest="changed")
        with self.assertRaisesRegex(
            W7AECAPSevenPathConsumerError,
            "seven-path consumption digest",
        ):
            replace(self.result, cap_seven_path_consumption_digest="changed")

    def test_module_is_not_reexported(self) -> None:
        import mcm_field_organism
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(mcm_field_organism, "consume_w7ae_cap_seven_path_plan")
        )
        self.assertFalse(
            hasattr(current_api, "consume_w7ae_cap_seven_path_plan")
        )


if __name__ == "__main__":
    unittest.main()
