from __future__ import annotations

from dataclasses import replace
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
from mcm_field_organism.e1_formation_s1fk_real_coordinator_contract import (
    audit_e1_formation_s1fk_real_coordinator_contract,
)
from mcm_field_organism.e1_formation_s1fm_real_path_preflight import (
    E1FormationS1FMRealPathPreflightError,
    audit_e1_formation_s1fm_real_path_preflight,
)
from mcm_field_organism.e1_refined_formation_runner import _digest


def _resources(free_memory_bytes: int) -> E1FormationS1FIResourceSnapshot:
    payload = {"free_memory_bytes": free_memory_bytes}
    return E1FormationS1FIResourceSnapshot(
        **payload,
        snapshot_digest=_digest(payload),
    )


class E1FormationS1FMRealPathPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.one_shot = prepare_e1_formation_s1fh_fresh_capture_one_shot_contract()
        cls.contract = audit_e1_formation_s1fk_real_coordinator_contract(
            cls.one_shot
        )
        cls.inputs = prepare_e1_formation_s1fi_inputs(
            Path("reports/e1_refined_formation_transfer_s1ea_once_v1.json")
        )

    def _preflight(self, free_memory_bytes: int):
        return preflight_e1_formation_s1fi_fresh_capture(
            self.one_shot,
            self.inputs,
            _resources(free_memory_bytes),
        )

    def test_complete_real_path_is_ready_but_closed(self) -> None:
        result = audit_e1_formation_s1fm_real_path_preflight(
            self.one_shot,
            self.contract,
            self._preflight(6 * 1024**3),
            self.inputs,
        )
        self.assertTrue(result.technical_real_path_ready)
        self.assertEqual(12, len(result.checks))
        self.assertFalse(result.owner_authorization_present)
        self.assertFalse(result.execution_permitted)
        self.assertFalse(result.field_execution_performed)
        self.assertEqual(
            "REAL_PATH_TECHNICALLY_READY_AWAITING_EXPLICIT_OWNER_AUTHORIZATION",
            result.decision,
        )

    def test_failed_source_resource_gate_keeps_execution_closed(self) -> None:
        result = audit_e1_formation_s1fm_real_path_preflight(
            self.one_shot,
            self.contract,
            self._preflight(4 * 1024**3 - 1),
            self.inputs,
        )
        self.assertFalse(result.technical_real_path_ready)
        self.assertFalse(dict(result.checks)["s1fi-source-preflight-passed"])
        self.assertFalse(result.execution_permitted)
        self.assertEqual(
            "REAL_PATH_PREFLIGHT_FAILED_EXECUTION_CLOSED",
            result.decision,
        )

    def test_source_snapshot_is_never_future_run_authorization(self) -> None:
        result = audit_e1_formation_s1fm_real_path_preflight(
            self.one_shot,
            self.contract,
            self._preflight(6 * 1024**3),
            self.inputs,
        )
        self.assertTrue(result.source_resource_snapshot_point_in_time_only)
        self.assertTrue(result.immediate_resource_recheck_required)
        self.assertNotIn(
            "authorization_text",
            inspect.signature(
                audit_e1_formation_s1fm_real_path_preflight
            ).parameters,
        )

    def test_result_is_deterministic_and_tamper_evident(self) -> None:
        source = self._preflight(6 * 1024**3)
        first = audit_e1_formation_s1fm_real_path_preflight(
            self.one_shot, self.contract, source, self.inputs
        )
        second = audit_e1_formation_s1fm_real_path_preflight(
            self.one_shot, self.contract, source, self.inputs
        )
        self.assertEqual(first.preflight_digest, second.preflight_digest)
        with self.assertRaises(E1FormationS1FMRealPathPreflightError):
            replace(first, execution_permitted=True)

    def test_audit_does_not_read_resources_or_execute_field(self) -> None:
        source = inspect.getsource(audit_e1_formation_s1fm_real_path_preflight)
        for forbidden in (
            "read_e1_formation_s1fi_resource_snapshot(",
            "run_e1_formation_s1fl_once(",
            "run_small_five_arm_formation_in_memory(",
            "capture_e1_formation_s1ff_in_memory(",
            "evaluate_e1_formation_s1fd_state_convergence(",
            "open(",
            "write_text(",
            "write_bytes(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
