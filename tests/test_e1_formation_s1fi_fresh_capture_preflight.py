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
from mcm_field_organism.e1_refined_formation_runner import _digest


_UPSTREAM = Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")


def _resources(free_memory_bytes: int) -> E1FormationS1FIResourceSnapshot:
    payload = {"free_memory_bytes": free_memory_bytes}
    return E1FormationS1FIResourceSnapshot(
        **payload,
        snapshot_digest=_digest(payload),
    )


class E1FormationS1FIFreshCapturePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        cls.inputs = prepare_e1_formation_s1fi_inputs(_UPSTREAM)

    def test_manifest_contains_only_six_formation_inputs(self) -> None:
        self.assertEqual(
            (
                "corridor",
                "av_permutation",
                "history_ab_plans",
                "history_ba_plans",
                "initial_field",
                "initial_state",
            ),
            tuple(role for role, _ in self.inputs.input_manifest),
        )
        self.assertTrue(
            all("probe" not in role for role, _ in self.inputs.input_manifest)
        )

    def test_sufficient_resource_fixture_is_technically_ready_only(self) -> None:
        result = preflight_e1_formation_s1fi_fresh_capture(
            self.contract,
            self.inputs,
            _resources(6 * 1024**3),
        )
        self.assertTrue(result.technical_preflight_passed)
        self.assertEqual(14_000, result.total_formation_field_steps)
        self.assertEqual((84, 145), (result.field_node_count, result.state_edge_count))
        self.assertEqual(2_175, result.retained_binding_count)
        self.assertEqual(
            "TECHNICALLY_READY_AWAITING_EXPLICIT_OWNER_AUTHORIZATION",
            result.decision,
        )
        self.assertFalse(result.owner_authorization_present)
        self.assertFalse(result.execution_permitted)

    def test_insufficient_memory_fails_without_partial_start(self) -> None:
        result = preflight_e1_formation_s1fi_fresh_capture(
            self.contract,
            self.inputs,
            _resources(4 * 1024**3 - 1),
        )
        self.assertFalse(result.technical_preflight_passed)
        self.assertEqual("RESOURCE_OR_INPUT_PREFLIGHT_FAILED", result.decision)
        self.assertFalse(result.field_execution_performed)
        self.assertFalse(result.capture_performed)

    def test_preflight_is_deterministic_for_same_snapshot(self) -> None:
        resources = _resources(6 * 1024**3)
        first = preflight_e1_formation_s1fi_fresh_capture(
            self.contract, self.inputs, resources
        )
        second = preflight_e1_formation_s1fi_fresh_capture(
            self.contract, self.inputs, resources
        )
        self.assertEqual(first.preflight_digest, second.preflight_digest)

    def test_input_builder_does_not_resolve_probe_data_or_run_paths(self) -> None:
        source = inspect.getsource(prepare_e1_formation_s1fi_inputs)
        for forbidden in (
            "_fixed_probe_sequences(",
            "probe_plans",
            "prepare_e1_confirmation_synthetic_run_contract(",
            "attempt_path",
            "lock_path",
            ".report_path",
            "report_path=",
        ):
            self.assertNotIn(forbidden, source)

    def test_preflight_calls_no_formation_capture_probe_or_writer(self) -> None:
        source = inspect.getsource(preflight_e1_formation_s1fi_fresh_capture)
        for forbidden in (
            "consume_prepared_full_formation(",
            "run_small_five_arm_formation_in_memory(",
            "capture_e1_formation_s1ff_in_memory(",
            "evaluate_e1_formation_s1fd_state_convergence(",
            "write_text(",
            "write_bytes(",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
