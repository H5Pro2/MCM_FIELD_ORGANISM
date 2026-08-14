from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.z4a_generic_trajectory_runner import (
    execute_z4a_technical_packet,
)
from mcm_field_organism.z4a_scalar_evaluation import (
    ARM_ORDER,
    MODEL_ORDER,
    WORLD_ORDER,
    z4a_scalar_result_json_text,
)
from mcm_field_organism.z4a_scalar_measurement_adapter import (
    Z4AScalarMeasurementAdapterError,
    evaluate_z4a_technical_packets,
    z4a_scalar_measurement_adapter_public_roles,
)
from tests.test_z4a_generic_trajectory_runner import world


class Z4AScalarMeasurementAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packets = tuple(
            execute_z4a_technical_packet(world(world_id))
            for world_id in WORLD_ORDER
        )
        cls.result = evaluate_z4a_technical_packets(cls.packets)

    def test_four_packets_form_complete_168_task_scalar_result(self) -> None:
        self.assertEqual("completed", self.result.execution_status)
        self.assertEqual(168, self.result.task_budget.task_count_completed)
        self.assertEqual(WORLD_ORDER, tuple(item.world_id for item in self.result.world_results))
        self.assertTrue(all(value for _, value in self.result.technical_controls))
        self.assertIn(
            self.result.overall_decision,
            {
                "F3_TECHNICAL_TRAJECTORY_ADVANTAGE",
                "FIELD_ENCODER_CAUSAL_BUT_BASELINE_EQUIVALENT",
                "NO_STABLE_CAUSAL_FIELD_SEPARATION",
                "Z4A_DECISION_UNRESOLVED",
            },
        )

    def test_world_model_arm_and_component_orders_are_preserved(self) -> None:
        for world_result in self.result.world_results:
            self.assertEqual(MODEL_ORDER, tuple(item.model_id for item in world_result.model_results))
            for model_result in world_result.model_results:
                self.assertEqual(ARM_ORDER, tuple(item.arm_id for item in model_result.arm_results))
                for arm_result in model_result.arm_results:
                    self.assertEqual(
                        model_result.component_ids,
                        tuple(item.component_id for item in arm_result.component_measurements),
                    )

    def test_partition_has_larger_technical_but_equal_decision_support(self) -> None:
        for world_result in self.result.world_results:
            for model_result in world_result.model_results:
                arms = {item.arm_id: item for item in model_result.arm_results}
                self.assertGreater(
                    arms["partitioned"].technical_support_count,
                    arms["reference"].technical_support_count,
                )
                self.assertEqual(
                    arms["partitioned"].decision_support_count,
                    arms["reference"].decision_support_count,
                )

    def test_projection_is_deterministic_for_fixed_packets(self) -> None:
        repeated = evaluate_z4a_technical_packets(self.packets)
        self.assertEqual(self.result, repeated)

    def test_scalar_json_retains_no_trajectory_or_vector(self) -> None:
        text = z4a_scalar_result_json_text(self.result)
        text.encode("ascii")
        for forbidden in (
            '"samples"',
            '"full_trajectories"',
            '"decision_trajectories"',
            '"field_vectors"',
            '"activation_vector"',
            '"mass_vector"',
        ):
            self.assertNotIn(forbidden, text)

    def test_failed_packet_control_forces_technical_abort(self) -> None:
        controls = tuple(
            (name, False if name == "observer_neutral" else value)
            for name, value in self.packets[0].controls
        )
        changed = (replace(self.packets[0], controls=controls), *self.packets[1:])
        result = evaluate_z4a_technical_packets(changed)
        self.assertEqual("technical_abort", result.execution_status)
        self.assertEqual(
            "FIELD_ENCODER_NOT_TECHNICALLY_STABLE",
            result.overall_decision,
        )
        self.assertFalse(dict(result.technical_controls)["observer_passive"])

    def test_missing_or_reordered_world_is_rejected(self) -> None:
        with self.assertRaises(Z4AScalarMeasurementAdapterError):
            evaluate_z4a_technical_packets(self.packets[:3])
        with self.assertRaises(Z4AScalarMeasurementAdapterError):
            evaluate_z4a_technical_packets(tuple(reversed(self.packets)))

    def test_public_roles_are_scalar_only(self) -> None:
        roles = set(z4a_scalar_measurement_adapter_public_roles())
        self.assertTrue(
            {
                "samples",
                "frames",
                "trajectories",
                "field_vectors",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
