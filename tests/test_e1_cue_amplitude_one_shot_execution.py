from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_cue_amplitude_curve_contract import build_e1_cue_amplitude_curve_contract
from mcm_field_organism.e1_cue_amplitude_one_shot_contract import (
    S1_CW_RUNNER_INVENTORY_DIGEST,
    prepare_e1_cue_amplitude_one_shot_contract,
)
from mcm_field_organism.e1_cue_amplitude_one_shot_execution import (
    E1CueAmplitudeOneShotExecutionError,
    execute_e1_cue_amplitude_one_shot,
)
from tests.test_e1_cue_amplitude_curve_execution import synthetic_observations


def synthetic_inventory():
    return {key: (lambda item=item: item) for key, item in synthetic_observations().items()}


class E1CueAmplitudeOneShotExecutionTests(unittest.TestCase):
    def test_synthetic_attempt_publishes_complete_report_once(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_cue_amplitude_one_shot_contract(root)
            curve = build_e1_cue_amplitude_curve_contract()
            receipt = execute_e1_cue_amplitude_one_shot(
                contract, curve, synthetic_inventory(), S1_CW_RUNNER_INVENTORY_DIGEST
            )
            report = json.loads(Path(contract.report_path).read_text(encoding="ascii"))
            self.assertEqual(tuple(report), contract.report_fields)
            self.assertEqual(72, receipt.observation_count)
            self.assertEqual("AMPLITUDE_CURVE_EXPLAINED_BY_LINEAR_SCALING", receipt.technical_decision)
            self.assertEqual(receipt.result_sha256, report["result_digest"])
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(E1CueAmplitudeOneShotExecutionError, "already used"):
                execute_e1_cue_amplitude_one_shot(
                    contract, curve, synthetic_inventory(), S1_CW_RUNNER_INVENTORY_DIGEST
                )

    def test_started_failure_retains_attempt_and_blocks_retry(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_cue_amplitude_one_shot_contract(root)
            curve = build_e1_cue_amplitude_curve_contract()
            inventory = synthetic_inventory()
            first = next(iter(inventory))
            inventory[first] = lambda: (_ for _ in ()).throw(RuntimeError("started"))
            with self.assertRaisesRegex(RuntimeError, "started"):
                execute_e1_cue_amplitude_one_shot(
                    contract, curve, inventory, S1_CW_RUNNER_INVENTORY_DIGEST
                )
            self.assertTrue(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(E1CueAmplitudeOneShotExecutionError, "already used"):
                execute_e1_cue_amplitude_one_shot(
                    contract, curve, synthetic_inventory(), S1_CW_RUNNER_INVENTORY_DIGEST
                )

    def test_wrong_digest_and_incomplete_inventory_fail_before_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_cue_amplitude_one_shot_contract(root)
            curve = build_e1_cue_amplitude_curve_contract()
            with self.assertRaisesRegex(E1CueAmplitudeOneShotExecutionError, "digest"):
                execute_e1_cue_amplitude_one_shot(contract, curve, synthetic_inventory(), "0" * 64)
            incomplete = synthetic_inventory()
            incomplete.pop(next(iter(incomplete)))
            with self.assertRaisesRegex(E1CueAmplitudeOneShotExecutionError, "incomplete"):
                execute_e1_cue_amplitude_one_shot(
                    contract, curve, incomplete, S1_CW_RUNNER_INVENTORY_DIGEST
                )
            self.assertEqual((), tuple(root.iterdir()))

    def test_execution_roles_remain_private(self) -> None:
        for role in (
            "E1CueAmplitudeOneShotReceipt",
            "E1CueAmplitudeOneShotExecutionError",
            "execute_e1_cue_amplitude_one_shot",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
