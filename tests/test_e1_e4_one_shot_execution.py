from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_execution import E1_E4_CONTINUITY_ANCHORS
from mcm_field_organism.e1_e4_one_shot_contract import (
    E1_E4_RUNNER_INVENTORY_DIGEST,
    prepare_e1_e4_one_shot_contract,
)
from mcm_field_organism.e1_e4_one_shot_execution import (
    E1E4OneShotExecutionError,
    build_canonical_e1_e4_inputs,
    execute_e1_e4_one_shot,
)
from tests.test_e1_e4_execution import runner_matrix


class E1E4OneShotExecutionTests(unittest.TestCase):
    def test_synthetic_attempt_publishes_complete_report_once(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_e4_one_shot_contract(Path(directory))
            receipt = execute_e1_e4_one_shot(
                contract,
                runner_matrix(),
                lambda: E1_E4_CONTINUITY_ANCHORS,
                E1_E4_RUNNER_INVENTORY_DIGEST,
            )
            report = json.loads(Path(contract.report_path).read_text(encoding="ascii"))

            self.assertEqual(tuple(report), contract.report_fields)
            self.assertEqual(receipt.result_sha256, report["result_digest"])
            self.assertEqual(
                "E4_EXPLAINED_BY_NARROW_BASELINE",
                report["technical_decision"],
            )
            self.assertEqual(9, len(report["result"]["model_runs"]))
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(E1E4OneShotExecutionError, "already used"):
                execute_e1_e4_one_shot(
                    contract,
                    runner_matrix(),
                    lambda: E1_E4_CONTINUITY_ANCHORS,
                    E1_E4_RUNNER_INVENTORY_DIGEST,
                )

    def test_started_failure_retains_attempt_and_blocks_retry(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_e4_one_shot_contract(Path(directory))
            runners = runner_matrix()

            def fail():
                raise RuntimeError("synthetic started failure")

            runners["e1"] = fail
            with self.assertRaisesRegex(RuntimeError, "synthetic started failure"):
                execute_e1_e4_one_shot(
                    contract,
                    runners,
                    lambda: E1_E4_CONTINUITY_ANCHORS,
                    E1_E4_RUNNER_INVENTORY_DIGEST,
                )

            self.assertTrue(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(E1E4OneShotExecutionError, "already used"):
                execute_e1_e4_one_shot(
                    contract,
                    runner_matrix(),
                    lambda: E1_E4_CONTINUITY_ANCHORS,
                    E1_E4_RUNNER_INVENTORY_DIGEST,
                )

    def test_wrong_inventory_is_rejected_before_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_e4_one_shot_contract(Path(directory))
            with self.assertRaisesRegex(E1E4OneShotExecutionError, "inventory"):
                execute_e1_e4_one_shot(
                    contract,
                    runner_matrix(),
                    lambda: E1_E4_CONTINUITY_ANCHORS,
                    "0" * 64,
                )
            self.assertEqual((), tuple(Path(directory).iterdir()))

    def test_canonical_inputs_match_registered_three_node_contract(self) -> None:
        field, state, substrate, afterimage = build_canonical_e1_e4_inputs()
        self.assertEqual(3, len(field.layer.neurons))
        self.assertEqual(0, field.layer.tick)
        self.assertIsNone(field.last_distribution)
        self.assertTrue(all(item.binding == 0.0 for item in state.edge_bindings))
        self.assertEqual(1.0, substrate.response_time_seconds)
        self.assertEqual(0.5, afterimage.time_constant_seconds)

    def test_execution_roles_remain_private(self) -> None:
        for role in (
            "execute_e1_e4_one_shot",
            "E1E4OneShotExecutionError",
            "E1E4OneShotReceipt",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
