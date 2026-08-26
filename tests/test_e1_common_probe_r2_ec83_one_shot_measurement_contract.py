from __future__ import annotations

import inspect
from pathlib import Path
import shutil
import tempfile
import unittest

from mcm_field_organism.e1_common_probe_r2_ec82_coordinator_handoff import (
    build_e1_common_probe_r2_ec82_coordinator_handoff_contract,
)
from mcm_field_organism.e1_common_probe_r2_ec83_one_shot_measurement_contract import (
    E1CommonProbeR2EC83OneShotMeasurementContractError,
    S1_EC83_EC82_SOURCE_RELATIVE_PATH,
    build_e1_common_probe_r2_ec83_one_shot_measurement_contract,
)


class E1CommonProbeR2EC83OneShotMeasurementContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]
        cls.handoff = build_e1_common_probe_r2_ec82_coordinator_handoff_contract(
            cls.root
        )

    def test_contract_binds_one_closed_measurement_attempt(self) -> None:
        contract = build_e1_common_probe_r2_ec83_one_shot_measurement_contract(
            self.root, self.handoff
        )
        self.assertEqual((1, 0), (
            contract.planned_execution_count,
            contract.authorized_execution_count,
        ))
        self.assertEqual(3208, contract.maximum_total_field_steps)
        self.assertEqual(6, contract.expected_scalar_contrast_count)
        self.assertTrue(contract.scalar_receipt_required_before_result_release)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.ec46_decision_permitted)

    def test_changed_ec82_source_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / S1_EC83_EC82_SOURCE_RELATIVE_PATH
            target.parent.mkdir(parents=True)
            shutil.copyfile(
                self.root / S1_EC83_EC82_SOURCE_RELATIVE_PATH, target
            )
            target.write_text(
                target.read_text(encoding="utf-8") + "\n# mutation\n",
                encoding="utf-8",
            )
            with self.assertRaises(
                E1CommonProbeR2EC83OneShotMeasurementContractError
            ):
                build_e1_common_probe_r2_ec83_one_shot_measurement_contract(
                    root, self.handoff
                )

    def test_untyped_handoff_is_rejected(self) -> None:
        with self.assertRaisesRegex(
            E1CommonProbeR2EC83OneShotMeasurementContractError, "typed EC82"
        ):
            build_e1_common_probe_r2_ec83_one_shot_measurement_contract(
                self.root, object()
            )

    def test_builder_calls_no_execution_reducer_or_writer(self) -> None:
        source = inspect.getsource(
            build_e1_common_probe_r2_ec83_one_shot_measurement_contract
        )
        for forbidden in (
            "run_e1_common_probe_n2_r2_real_mode_coordinator(",
            "reduce_e1_common_probe_r2_ec82_completed_result(",
            "build_e1_common_probe_r2_ec80_scalar_receipt(",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
