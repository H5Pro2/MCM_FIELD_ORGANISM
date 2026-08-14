from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_a0_av_history_one_shot_contract import (
    S1_DE_HISTORY_AB_DIGEST,
    S1_DE_HISTORY_BA_DIGEST,
    S1_DE_PERMUTATION_DIGEST,
    S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
    prepare_e1_a0_av_history_one_shot_contract,
)
from mcm_field_organism.e1_a0_av_history_one_shot_execution import (
    E1A0AVHistoryOneShotExecutionError,
    execute_e1_a0_av_history_one_shot,
)
from tests.test_e1_a0_av_history_producer import produce


def synthetic_canonical_result():
    result = produce()
    audits = tuple(
        replace(
            item,
            source_support_count=220,
            assigned_event_count=220,
        )
        for item in result.arm_audits
    )
    return replace(
        result,
        history_ab_digest=S1_DE_HISTORY_AB_DIGEST,
        history_ba_digest=S1_DE_HISTORY_BA_DIGEST,
        permutation_digest=S1_DE_PERMUTATION_DIGEST,
        arm_audits=audits,
        production_digest="f" * 64,
    )


class E1A0AVHistoryOneShotExecutionTests(unittest.TestCase):
    def test_synthetic_attempt_publishes_complete_report_once(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_a0_av_history_one_shot_contract(
                Path(directory)
            )
            receipt = execute_e1_a0_av_history_one_shot(
                contract,
                synthetic_canonical_result,
                S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
            )
            report = json.loads(
                Path(contract.report_path).read_text(encoding="ascii")
            )

            self.assertEqual(tuple(report), contract.report_fields)
            self.assertEqual(
                "E1_A0_AV_HISTORY_STATES_PRODUCED",
                receipt.technical_status,
            )
            self.assertEqual(receipt.result_sha256, report["result_digest"])
            self.assertEqual(receipt.d_state, report["d_state"])
            self.assertEqual(receipt.d_total_binding, report["d_total_binding"])
            self.assertGreaterEqual(receipt.d_state, 0.0)
            self.assertGreaterEqual(receipt.d_total_binding, 0.0)
            self.assertNotIn("field", report["result"])
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(
                E1A0AVHistoryOneShotExecutionError,
                "already used",
            ):
                execute_e1_a0_av_history_one_shot(
                    contract,
                    synthetic_canonical_result,
                    S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
                )

    def test_started_failure_retains_attempt_and_blocks_retry(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_a0_av_history_one_shot_contract(
                Path(directory)
            )

            def fail():
                raise RuntimeError("synthetic started failure")

            with self.assertRaisesRegex(RuntimeError, "started failure"):
                execute_e1_a0_av_history_one_shot(
                    contract,
                    fail,
                    S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
                )
            self.assertTrue(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(
                E1A0AVHistoryOneShotExecutionError,
                "already used",
            ):
                execute_e1_a0_av_history_one_shot(
                    contract,
                    synthetic_canonical_result,
                    S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
                )

    def test_wrong_digest_and_noncallable_fail_before_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_a0_av_history_one_shot_contract(root)
            with self.assertRaisesRegex(
                E1A0AVHistoryOneShotExecutionError,
                "implementation digest",
            ):
                execute_e1_a0_av_history_one_shot(
                    contract,
                    synthetic_canonical_result,
                    "0" * 64,
                )
            with self.assertRaisesRegex(
                E1A0AVHistoryOneShotExecutionError,
                "not callable",
            ):
                execute_e1_a0_av_history_one_shot(
                    contract,
                    None,
                    S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
                )
            self.assertEqual((), tuple(root.iterdir()))

    def test_invalid_started_result_retains_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_a0_av_history_one_shot_contract(
                Path(directory)
            )

            def changed_result():
                return replace(
                    synthetic_canonical_result(),
                    history_ab_digest="0" * 64,
                )

            with self.assertRaisesRegex(
                E1A0AVHistoryOneShotExecutionError,
                "source binding",
            ):
                execute_e1_a0_av_history_one_shot(
                    contract,
                    changed_result,
                    S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
                )
            self.assertTrue(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())

    def test_execution_roles_remain_private(self) -> None:
        for role in (
            "E1A0AVHistoryOneShotReceipt",
            "E1A0AVHistoryOneShotExecutionError",
            "execute_e1_a0_av_history_one_shot",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
