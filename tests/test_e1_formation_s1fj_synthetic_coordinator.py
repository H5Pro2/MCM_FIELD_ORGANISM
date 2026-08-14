from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_formation_s1fh_fresh_capture_one_shot_contract import (
    prepare_e1_formation_s1fh_fresh_capture_one_shot_contract,
)
from mcm_field_organism.e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIResourceSnapshot,
    prepare_e1_formation_s1fi_inputs,
    preflight_e1_formation_s1fi_fresh_capture,
)
from mcm_field_organism.e1_formation_s1fj_synthetic_coordinator import (
    E1FormationS1FJSyntheticCoordinatorError,
    build_e1_formation_s1fj_synthetic_inventory,
    coordinate_e1_formation_s1fj_synthetically,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


class E1FormationS1FJSyntheticCoordinatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        cls.inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        resource_payload = {"free_memory_bytes": 6 * 1024**3}
        resources = E1FormationS1FIResourceSnapshot(
            **resource_payload,
            snapshot_digest=_digest(resource_payload),
        )
        cls.preflight = preflight_e1_formation_s1fi_fresh_capture(
            cls.contract, cls.inputs, resources
        )

    def test_full_dry_integration_reaches_diagnostic_only(self) -> None:
        inventory = build_e1_formation_s1fj_synthetic_inventory(self.inputs)
        result = coordinate_e1_formation_s1fj_synthetically(
            self.contract, self.preflight, inventory
        )
        self.assertEqual((15, 15), (
            result.formation_results_consumed,
            result.captured_state_vectors,
        ))
        self.assertEqual(
            "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY",
            result.evaluation.decision,
        )
        self.assertEqual(
            "SYNTHETIC_COORDINATION_CONFIRMED_FRESH_EXECUTION_STILL_CLOSED",
            result.decision,
        )
        self.assertTrue(result.dry_integration_confirmed)

    def test_inventory_is_typed_separate_and_zero_step(self) -> None:
        inventory = build_e1_formation_s1fj_synthetic_inventory(self.inputs)
        self.assertEqual(15, len(inventory.results))
        self.assertEqual(15, len({id(item.output_state) for item in inventory.results}))
        self.assertEqual(0, inventory.field_steps_executed)
        self.assertEqual(0, inventory.probe_objects_created)
        self.assertFalse(inventory.persistence_performed)

    def test_coordinator_keeps_execution_claims_and_probe_closed(self) -> None:
        result = coordinate_e1_formation_s1fj_synthetically(
            self.contract,
            self.preflight,
            build_e1_formation_s1fj_synthetic_inventory(self.inputs),
        )
        self.assertFalse(result.owner_authorization_present)
        self.assertFalse(result.execution_permitted)
        self.assertEqual(0, result.field_steps_executed)
        self.assertEqual(0, result.probe_objects_created)
        self.assertFalse(result.persistence_performed)
        self.assertFalse(result.memory_claim_permitted)

    def test_failed_preflight_is_rejected(self) -> None:
        payload = {"free_memory_bytes": 4 * 1024**3 - 1}
        resources = E1FormationS1FIResourceSnapshot(
            **payload,
            snapshot_digest=_digest(payload),
        )
        failed = preflight_e1_formation_s1fi_fresh_capture(
            self.contract, self.inputs, resources
        )
        with self.assertRaises(E1FormationS1FJSyntheticCoordinatorError):
            coordinate_e1_formation_s1fj_synthetically(
                self.contract,
                failed,
                build_e1_formation_s1fj_synthetic_inventory(self.inputs),
            )

    def test_integration_is_deterministic(self) -> None:
        first = coordinate_e1_formation_s1fj_synthetically(
            self.contract,
            self.preflight,
            build_e1_formation_s1fj_synthetic_inventory(self.inputs),
        )
        second = coordinate_e1_formation_s1fj_synthetically(
            self.contract,
            self.preflight,
            build_e1_formation_s1fj_synthetic_inventory(self.inputs),
        )
        self.assertEqual(first.result_digest, second.result_digest)

    def test_fixture_and_coordinator_call_no_field_probe_or_writer(self) -> None:
        sources = (
            inspect.getsource(build_e1_formation_s1fj_synthetic_inventory),
            inspect.getsource(coordinate_e1_formation_s1fj_synthetically),
        )
        for source in sources:
            for forbidden in (
                "consume_prepared_full_formation(",
                "run_small_five_arm_formation_in_memory(",
                "run_prepared_real_formation_arm_in_memory(",
                "run_full_persistent_probe(",
                "write_text(",
                "write_bytes(",
                "open(",
            ):
                self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
