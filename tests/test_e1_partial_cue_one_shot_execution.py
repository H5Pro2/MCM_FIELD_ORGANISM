from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_partial_cue_contract import build_e1_partial_cue_contract
from mcm_field_organism.e1_partial_cue_one_shot_contract import (
    S1_CR_RUNNER_INVENTORY_DIGEST,
    prepare_e1_partial_cue_one_shot_contract,
)
from mcm_field_organism.e1_partial_cue_one_shot_execution import (
    E1PartialCueOneShotExecutionError,
    execute_e1_partial_cue_one_shot,
)
from tests.test_e1_partial_cue_execution import observations


def synthetic_inventory():
    return {
        key: (lambda item=item: item)
        for key, item in observations().items()
    }


class E1PartialCueOneShotExecutionTests(unittest.TestCase):
    def test_synthetic_attempt_publishes_complete_report_once(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_partial_cue_one_shot_contract(root)
            cue = build_e1_partial_cue_contract()
            receipt = execute_e1_partial_cue_one_shot(
                contract, cue, synthetic_inventory(), S1_CR_RUNNER_INVENTORY_DIGEST
            )
            report = json.loads(Path(contract.report_path).read_text(encoding="ascii"))
            self.assertEqual(tuple(report), contract.report_fields)
            self.assertEqual(36, receipt.observation_count)
            self.assertEqual("HISTORY_SPECIFIC_PARTIAL_CUE_EFFECT", receipt.technical_decision)
            self.assertEqual(receipt.result_sha256, report["result_digest"])
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(E1PartialCueOneShotExecutionError, "already used"):
                execute_e1_partial_cue_one_shot(
                    contract, cue, synthetic_inventory(), S1_CR_RUNNER_INVENTORY_DIGEST
                )

    def test_started_failure_retains_attempt_and_blocks_retry(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_partial_cue_one_shot_contract(root)
            cue = build_e1_partial_cue_contract()
            inventory = synthetic_inventory()
            first_key = next(iter(inventory))
            inventory[first_key] = lambda: (_ for _ in ()).throw(RuntimeError("started"))
            with self.assertRaisesRegex(RuntimeError, "started"):
                execute_e1_partial_cue_one_shot(
                    contract, cue, inventory, S1_CR_RUNNER_INVENTORY_DIGEST
                )
            self.assertTrue(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(E1PartialCueOneShotExecutionError, "already used"):
                execute_e1_partial_cue_one_shot(
                    contract, cue, synthetic_inventory(), S1_CR_RUNNER_INVENTORY_DIGEST
                )

    def test_wrong_digest_and_incomplete_inventory_fail_before_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_partial_cue_one_shot_contract(root)
            cue = build_e1_partial_cue_contract()
            with self.assertRaisesRegex(E1PartialCueOneShotExecutionError, "digest"):
                execute_e1_partial_cue_one_shot(contract, cue, synthetic_inventory(), "0" * 64)
            incomplete = synthetic_inventory()
            incomplete.pop(next(iter(incomplete)))
            with self.assertRaisesRegex(E1PartialCueOneShotExecutionError, "incomplete"):
                execute_e1_partial_cue_one_shot(
                    contract, cue, incomplete, S1_CR_RUNNER_INVENTORY_DIGEST
                )
            self.assertEqual((), tuple(root.iterdir()))

    def test_execution_roles_remain_private(self) -> None:
        for role in (
            "E1PartialCueOneShotReceipt",
            "E1PartialCueOneShotExecutionError",
            "execute_e1_partial_cue_one_shot",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
