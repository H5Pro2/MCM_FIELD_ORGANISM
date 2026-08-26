from __future__ import annotations

from dataclasses import dataclass
import inspect
from pathlib import Path
import unittest

from mcm_field_organism.e1_confirmation_small_five_arm_formation import (
    E1SmallFiveArmFormationResult,
)
from mcm_field_organism.e1_formation_s1fh_fresh_capture_one_shot_contract import (
    prepare_e1_formation_s1fh_fresh_capture_one_shot_contract,
)
from mcm_field_organism.e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIResourceSnapshot,
    prepare_e1_formation_s1fi_inputs,
    preflight_e1_formation_s1fi_fresh_capture,
)
from mcm_field_organism.e1_formation_s1fj_synthetic_coordinator import (
    build_e1_formation_s1fj_synthetic_inventory,
)
from mcm_field_organism.e1_formation_s1fk_real_coordinator_contract import (
    S1_FK_REQUIRED_AUTHORIZATION_TEXT,
    audit_e1_formation_s1fk_real_coordinator_contract,
)
from mcm_field_organism.e1_formation_s1fl_real_coordinator import (
    E1FormationS1FLRealCoordinatorError,
    coordinate_e1_formation_s1fl_with_counting_adapters,
    run_e1_formation_s1fl_once,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


def _resources(free_memory_bytes: int) -> E1FormationS1FIResourceSnapshot:
    payload = {"free_memory_bytes": free_memory_bytes}
    return E1FormationS1FIResourceSnapshot(
        **payload, snapshot_digest=_digest(payload)
    )


@dataclass
class _CountingFormationAdapter:
    grouped: dict[str, E1SmallFiveArmFormationResult]
    calls: list[str]
    fail_on: str | None = None

    def __call__(
        self,
        refinement_id,
        history_ab,
        history_ba,
        ab_proposal_steps,
        ba_proposal_steps,
        initial_field,
        initial_state,
    ):
        self.calls.append(refinement_id)
        if refinement_id == self.fail_on:
            raise E1FormationS1FLRealCoordinatorError("injected adapter failure")
        return self.grouped[refinement_id]


def _grouped_results(inputs):
    inventory = build_e1_formation_s1fj_synthetic_inventory(inputs)
    grouped = {}
    for index, refinement_id in enumerate(("r2", "r4", "r8")):
        arms = inventory.results[index * 5 : (index + 1) * 5]
        values = {
            "refinement_id": refinement_id,
            "arms": arms,
            "ab_identity_repeated": True,
            "ablation_states_neutral": True,
            "output_states_object_separated": True,
            "history_backreaction_field_controls_equal": True,
            "resource_budget_preserved": True,
            "prepared_inputs_preserved": True,
            "maximum_resource_budget_error": 0.0,
            "canonical_execution_permitted": False,
            "claims_permitted": False,
        }
        payload = {
            name: value for name, value in values.items() if name != "arms"
        }
        payload["arm_result_digests"] = tuple(item.result_digest for item in arms)
        grouped[refinement_id] = E1SmallFiveArmFormationResult(
            **values, result_digest=_digest(payload)
        )
    return grouped


class E1FormationS1FLRealCoordinatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.one_shot = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        cls.contract = audit_e1_formation_s1fk_real_coordinator_contract(
            cls.one_shot
        )
        cls.inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )
        cls.preflight = preflight_e1_formation_s1fi_fresh_capture(
            cls.one_shot, cls.inputs, _resources(6 * 1024**3)
        )

    def test_counting_adapters_follow_exact_three_refinement_order(self) -> None:
        adapter = _CountingFormationAdapter(_grouped_results(self.inputs), [])
        result = coordinate_e1_formation_s1fl_with_counting_adapters(
            self.contract,
            self.one_shot,
            self.preflight,
            self.inputs,
            S1_FK_REQUIRED_AUTHORIZATION_TEXT,
            lambda: _resources(6 * 1024**3),
            adapter,
        )
        self.assertEqual(["r2", "r4", "r8"], adapter.calls)
        self.assertEqual(3, result.formation_runner_call_count)
        self.assertEqual(15, result.formation_result_count)
        self.assertEqual(15, result.captured_state_count)
        self.assertEqual(0, result.field_steps_executed)
        self.assertEqual(
            "COUNTING_ADAPTER_COORDINATION_CONFIRMED_REAL_EXECUTION_CLOSED",
            result.decision,
        )

    def test_immediate_resource_failure_prevents_first_adapter_call(self) -> None:
        adapter = _CountingFormationAdapter(_grouped_results(self.inputs), [])
        with self.assertRaises(E1FormationS1FLRealCoordinatorError):
            coordinate_e1_formation_s1fl_with_counting_adapters(
                self.contract,
                self.one_shot,
                self.preflight,
                self.inputs,
                S1_FK_REQUIRED_AUTHORIZATION_TEXT,
                lambda: _resources(4 * 1024**3 - 1),
                adapter,
            )
        self.assertEqual([], adapter.calls)

    def test_wrong_authorization_prevents_first_adapter_call(self) -> None:
        adapter = _CountingFormationAdapter(_grouped_results(self.inputs), [])
        with self.assertRaises(ValueError):
            coordinate_e1_formation_s1fl_with_counting_adapters(
                self.contract,
                self.one_shot,
                self.preflight,
                self.inputs,
                "ok weiter",
                lambda: _resources(6 * 1024**3),
                adapter,
            )
        self.assertEqual([], adapter.calls)

    def test_adapter_failure_returns_no_partial_result_and_no_retry(self) -> None:
        adapter = _CountingFormationAdapter(
            _grouped_results(self.inputs), [], fail_on="r4"
        )
        with self.assertRaises(E1FormationS1FLRealCoordinatorError):
            coordinate_e1_formation_s1fl_with_counting_adapters(
                self.contract,
                self.one_shot,
                self.preflight,
                self.inputs,
                S1_FK_REQUIRED_AUTHORIZATION_TEXT,
                lambda: _resources(6 * 1024**3),
                adapter,
            )
        self.assertEqual(["r2", "r4"], adapter.calls)

    def test_counting_integration_is_deterministic(self) -> None:
        digests = []
        for _ in range(2):
            result = coordinate_e1_formation_s1fl_with_counting_adapters(
                self.contract,
                self.one_shot,
                self.preflight,
                self.inputs,
                S1_FK_REQUIRED_AUTHORIZATION_TEXT,
                lambda: _resources(6 * 1024**3),
                _CountingFormationAdapter(_grouped_results(self.inputs), []),
            )
            digests.append(result.result_digest)
        self.assertEqual(digests[0], digests[1])

    def test_real_entry_is_not_called_by_counting_tests(self) -> None:
        source = inspect.getsource(run_e1_formation_s1fl_once)
        self.assertIn("execution_mode=\"real\"", source)
        counting_source = inspect.getsource(
            coordinate_e1_formation_s1fl_with_counting_adapters
        )
        self.assertNotIn("run_small_five_arm_formation_in_memory", counting_source)
        self.assertNotIn("read_e1_formation_s1fi_resource_snapshot", counting_source)


if __name__ == "__main__":
    unittest.main()
