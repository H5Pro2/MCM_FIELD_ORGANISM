from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_state_transfer_contract import (
    S1_DK_ARMS,
    S1_DK_METRICS,
    S1_DK_REQUIRED_IDENTITIES,
)
from mcm_field_organism.e1_frozen_state_transfer_one_shot_contract import (
    S1_DL_IMPLEMENTATION_DIGEST,
    prepare_e1_frozen_state_transfer_one_shot_contract,
)
from mcm_field_organism.e1_frozen_state_transfer_one_shot_execution import (
    E1FrozenStateTransferExecutionResult,
    E1FrozenStateTransferOneShotExecutionError,
    E1FrozenStateTransferPartitionResult,
    execute_e1_frozen_state_transfer_one_shot,
)


HISTORY = Path("reports/e1_a0_av_history_s1di_once_v1.json")


def partition(partition_id: str, boundaries: tuple[int, ...]):
    values = {
        "p0": "a" * 64,
        "ab0": "a" * 64,
        "ba0": "a" * 64,
        "ab1": "b" * 64,
        "ba1": "c" * 64,
        "abf": "b" * 64,
        "baf": "c" * 64,
    }
    return E1FrozenStateTransferPartitionResult(
        partition_id,
        boundaries,
        tuple((role, values[role]) for role in S1_DK_ARMS),
    )


def synthetic_result(
    *,
    d_active_s: float = 0.2,
    d_active_h: float = 0.1,
    d_probe_partition: float = 0.01,
    status: str = "REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE",
):
    metric_values = {
        "d_pre_s": 0.0,
        "d_pre_h": 0.0,
        "d_active_s": d_active_s,
        "d_active_h": d_active_h,
        "d_ablation": 0.0,
        "d_fixed_adapter": 0.0,
        "d_probe_partition": d_probe_partition,
        "frozen_state_change": 0.0,
    }
    return E1FrozenStateTransferExecutionResult(
        partitions=(
            partition("coarse", (0, 1_000_000)),
            partition("split", (0, 500_000, 1_000_000)),
        ),
        metrics=tuple((role, metric_values[role]) for role in S1_DK_METRICS),
        controls=tuple((role, True) for role in S1_DK_REQUIRED_IDENTITIES),
        technical_status=status,
    )


class E1FrozenStateTransferOneShotExecutionTests(unittest.TestCase):
    def test_synthetic_attempt_publishes_complete_report_once(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_frozen_state_transfer_one_shot_contract(
                Path(directory), HISTORY
            )
            receipt = execute_e1_frozen_state_transfer_one_shot(
                contract,
                synthetic_result,
                S1_DL_IMPLEMENTATION_DIGEST,
            )
            report = json.loads(
                Path(contract.report_path).read_text(encoding="ascii")
            )

            self.assertEqual(tuple(report), contract.report_fields)
            self.assertEqual(
                "REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE",
                receipt.technical_status,
            )
            self.assertEqual(receipt.technical_status, report["technical_status"])
            self.assertEqual(2, len(report["partition_result_digests"]))
            self.assertEqual(8, len(report["metrics"]))
            self.assertEqual(8, len(report["controls"]))
            self.assertFalse(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(
                E1FrozenStateTransferOneShotExecutionError,
                "already used",
            ):
                execute_e1_frozen_state_transfer_one_shot(
                    contract,
                    synthetic_result,
                    S1_DL_IMPLEMENTATION_DIGEST,
                )

    def test_started_failure_retains_attempt_and_blocks_retry(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_frozen_state_transfer_one_shot_contract(
                Path(directory), HISTORY
            )

            def fail():
                raise RuntimeError("synthetic started failure")

            with self.assertRaisesRegex(RuntimeError, "started failure"):
                execute_e1_frozen_state_transfer_one_shot(
                    contract, fail, S1_DL_IMPLEMENTATION_DIGEST
                )
            self.assertTrue(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())
            with self.assertRaisesRegex(
                E1FrozenStateTransferOneShotExecutionError,
                "already used",
            ):
                execute_e1_frozen_state_transfer_one_shot(
                    contract, synthetic_result, S1_DL_IMPLEMENTATION_DIGEST
                )

    def test_wrong_digest_and_noncallable_fail_before_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_frozen_state_transfer_one_shot_contract(
                root, HISTORY
            )
            with self.assertRaisesRegex(
                E1FrozenStateTransferOneShotExecutionError,
                "implementation digest",
            ):
                execute_e1_frozen_state_transfer_one_shot(
                    contract, synthetic_result, "0" * 64
                )
            with self.assertRaisesRegex(
                E1FrozenStateTransferOneShotExecutionError,
                "not callable",
            ):
                execute_e1_frozen_state_transfer_one_shot(
                    contract, None, S1_DL_IMPLEMENTATION_DIGEST
                )
            self.assertEqual((), tuple(root.iterdir()))

    def test_invalid_started_result_retains_attempt(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_frozen_state_transfer_one_shot_contract(
                Path(directory), HISTORY
            )

            with self.assertRaisesRegex(
                E1FrozenStateTransferOneShotExecutionError,
                "invalid result",
            ):
                execute_e1_frozen_state_transfer_one_shot(
                    contract, lambda: object(), S1_DL_IMPLEMENTATION_DIGEST
                )
            self.assertTrue(Path(contract.attempt_path).exists())
            self.assertFalse(Path(contract.report_path).exists())
            self.assertFalse(Path(contract.lock_path).exists())

    def test_status_is_determined_by_active_and_partition_metrics(self) -> None:
        self.assertEqual(
            "NO_REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE",
            synthetic_result(
                d_active_s=0.0,
                d_active_h=0.0,
                d_probe_partition=0.0,
                status="NO_REGISTERED_FROZEN_STATE_TRANSFER_DIFFERENCE",
            ).technical_status,
        )
        self.assertEqual(
            "TECHNICALLY_UNDECIDABLE",
            synthetic_result(
                d_active_s=0.01,
                d_active_h=0.0,
                d_probe_partition=0.02,
                status="TECHNICALLY_UNDECIDABLE",
            ).technical_status,
        )
        with self.assertRaisesRegex(
            E1FrozenStateTransferOneShotExecutionError,
            "does not follow",
        ):
            synthetic_result(status="TECHNICALLY_UNDECIDABLE")

    def test_partition_and_control_identity_fail_closed(self) -> None:
        valid = partition("coarse", (0, 1_000_000))
        changed_arms = tuple(
            (role, "d" * 64 if role == "ab0" else digest)
            for role, digest in valid.arm_field_digests
        )
        with self.assertRaisesRegex(
            E1FrozenStateTransferOneShotExecutionError,
            "identity control",
        ):
            replace(valid, arm_field_digests=changed_arms)
        result = synthetic_result()
        with self.assertRaisesRegex(
            E1FrozenStateTransferOneShotExecutionError,
            "controls failed",
        ):
            replace(
                result,
                controls=tuple(
                    (role, index != 0)
                    for index, role in enumerate(S1_DK_REQUIRED_IDENTITIES)
                ),
            )

    def test_execution_roles_remain_private(self) -> None:
        for role in (
            "E1FrozenStateTransferPartitionResult",
            "E1FrozenStateTransferExecutionResult",
            "E1FrozenStateTransferOneShotReceipt",
            "execute_e1_frozen_state_transfer_one_shot",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
