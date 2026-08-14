from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_formation_s1fi_fresh_capture_preflight import (
    prepare_e1_formation_s1fi_inputs,
)
from mcm_field_organism.e1_formation_s1fj_synthetic_coordinator import (
    build_e1_formation_s1fj_synthetic_inventory,
)
from mcm_field_organism.e1_formation_s1fp_common_probe_contract import (
    audit_e1_formation_s1fp_common_probe_contract,
)
from mcm_field_organism.e1_formation_s1fq_synthetic_common_probe_coordinator import (
    E1FormationS1FQSyntheticCoordinatorError,
    build_e1_formation_s1fq_synthetic_probe_sample,
    coordinate_e1_formation_s1fq_synthetically,
)


class E1FormationS1FQSyntheticCoordinatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = audit_e1_formation_s1fp_common_probe_contract()
        cls.inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        cls.inventory = build_e1_formation_s1fj_synthetic_inventory(cls.inputs)

    def test_all_fifteen_states_and_thirty_probe_slots_are_integrated(self) -> None:
        result = coordinate_e1_formation_s1fq_synthetically(
            self.contract, self.inventory
        )
        self.assertEqual(15, result.formation_result_count)
        self.assertEqual(30, result.probe_sample_count)
        self.assertEqual(30, result.fresh_probe_field_object_count)
        self.assertTrue(result.formation_states_preserved)
        self.assertEqual(0, result.field_steps_executed)

    def test_registered_signal_is_fully_fixed_adapter_explained(self) -> None:
        result = coordinate_e1_formation_s1fq_synthetically(
            self.contract, self.inventory
        )
        self.assertGreater(result.active_activation_by_refinement[-1], 0.0)
        self.assertGreater(result.active_afterimage_by_refinement[-1], 0.0)
        self.assertEqual(0.0, result.maximum_p0_reset_error)
        self.assertEqual(0.0, result.maximum_feedback_ablation_error)
        self.assertEqual(0.0, result.maximum_formation_ablation_error)
        self.assertEqual(0.0, result.maximum_fixed_adapter_error)
        self.assertEqual(
            "SYNTHETIC_FRESH_FORMATION_COMMON_PROBE_FIXED_ADAPTER_EXPLAINED",
            result.decision,
        )

    def test_fixture_is_deterministic(self) -> None:
        first = coordinate_e1_formation_s1fq_synthetically(
            self.contract, self.inventory
        )
        second = coordinate_e1_formation_s1fq_synthetically(
            self.contract, self.inventory
        )
        self.assertEqual(first.result_digest, second.result_digest)

    def test_changed_sample_identity_fails_closed_without_partial_result(self) -> None:
        calls = []

        def changed(refinement, role, source_state_digest):
            calls.append((refinement, role))
            sample = build_e1_formation_s1fq_synthetic_probe_sample(
                refinement, role, source_state_digest
            )
            if len(calls) == 12:
                return replace(sample, role_id="p0-reset-ab")
            return sample

        with self.assertRaises(E1FormationS1FQSyntheticCoordinatorError):
            coordinate_e1_formation_s1fq_synthetically(
                self.contract, self.inventory, probe_kernel=changed
            )
        self.assertEqual(12, len(calls))

    def test_result_is_tamper_evident(self) -> None:
        result = coordinate_e1_formation_s1fq_synthetically(
            self.contract, self.inventory
        )
        with self.assertRaises(E1FormationS1FQSyntheticCoordinatorError):
            replace(result, real_probe_performed=True)

    def test_coordinator_calls_no_real_formation_probe_or_writer(self) -> None:
        source = inspect.getsource(coordinate_e1_formation_s1fq_synthetically)
        for forbidden in (
            "run_e1_formation_s1fl_once(",
            "run_small_five_arm_formation_in_memory(",
            "advance_neutral_fast_shared_field_transient(",
            "advance_frozen_e1_fast_shared_field_transient(",
            "advance_fixed_e1_adapter_fast_shared_field_transient(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
