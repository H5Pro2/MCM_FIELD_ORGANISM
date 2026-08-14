from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism.e1_common_probe_r2_ec82_coordinator_handoff import (
    build_e1_common_probe_r2_ec82_coordinator_handoff_contract,
)
from mcm_field_organism.e1_common_probe_r2_ec83_one_shot_measurement_contract import (
    build_e1_common_probe_r2_ec83_one_shot_measurement_contract,
)
from mcm_field_organism.e1_common_probe_r2_ec85_measurement_preflight import (
    S1_EC85_EC84_SOURCE_RELATIVE_PATH,
    audit_e1_common_probe_r2_ec85_measurement_preflight,
)


class E1CommonProbeR2EC85MeasurementPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from tests.test_e1_common_probe_n2_r2_corrected_final_preflight import (
            E1CommonProbeN2R2CorrectedFinalPreflightTests,
        )
        from mcm_field_organism.e1_common_probe_n2_r2_corrected_final_preflight import (
            audit_e1_common_probe_n2_r2_corrected_final_preflight,
        )

        cls.root = Path(__file__).resolve().parents[1]
        E1CommonProbeN2R2CorrectedFinalPreflightTests.setUpClass()
        source = E1CommonProbeN2R2CorrectedFinalPreflightTests()
        cls.technical = audit_e1_common_probe_n2_r2_corrected_final_preflight(
            source.source._audit(), source.integrity
        )
        handoff = build_e1_common_probe_r2_ec82_coordinator_handoff_contract(
            cls.root
        )
        cls.contract = build_e1_common_probe_r2_ec83_one_shot_measurement_contract(
            cls.root, handoff
        )

    def test_all_technical_gates_ready_but_authorization_absent(self) -> None:
        result = audit_e1_common_probe_r2_ec85_measurement_preflight(
            self.root, self.technical, self.contract
        )
        self.assertTrue(result.technical_request_ready)
        self.assertFalse(result.owner_authorization_present)
        self.assertFalse(result.execution_permitted)
        self.assertEqual(3208, result.planned_total_steps)
        self.assertEqual(6, result.expected_scalar_contrast_count)

    def test_changed_ec84_source_blocks_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / S1_EC85_EC84_SOURCE_RELATIVE_PATH
            target.parent.mkdir(parents=True)
            shutil.copyfile(
                self.root / S1_EC85_EC84_SOURCE_RELATIVE_PATH, target
            )
            target.write_text(
                target.read_text(encoding="utf-8") + "\n# mutation\n",
                encoding="utf-8",
            )
            result = audit_e1_common_probe_r2_ec85_measurement_preflight(
                root, self.technical, self.contract
            )
        self.assertFalse(result.technical_request_ready)
        self.assertEqual("CORRECT_MEASUREMENT_PREFLIGHT_GATES", result.decision)

    def test_changed_step_budget_fails_closed(self) -> None:
        with self.assertRaises(Exception):
            changed = replace(self.contract, maximum_total_field_steps=3209)
            audit_e1_common_probe_r2_ec85_measurement_preflight(
                self.root, self.technical, changed
            )

    def test_preflight_calls_no_execution_reducer_or_writer(self) -> None:
        source = inspect.getsource(audit_e1_common_probe_r2_ec85_measurement_preflight)
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "build_e1_common_probe_r2_ec84_atomic_return(",
            "reduce_e1_common_probe_r2_ec82_completed_result(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
