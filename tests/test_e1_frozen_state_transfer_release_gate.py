from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_state_transfer_release_gate import (
    E1FrozenStateTransferReleaseGate,
    E1FrozenStateTransferReleaseGateError,
    S1_DN_EXECUTOR_DIGEST,
    S1_DO_PRODUCER_DIGEST,
    current_s1_dn_executor_digest,
    current_s1_do_producer_digest,
    prepare_e1_frozen_state_transfer_release_gate,
    validate_e1_frozen_state_transfer_release_gate,
)


REPORTS = Path("reports")
HISTORY = REPORTS / "e1_a0_av_history_s1di_once_v1.json"
TARGET_NAMES = (
    "e1_frozen_state_transfer_s1dn_once_v1.json",
    "e1_frozen_state_transfer_s1dn_once_v1.attempt.json",
    "e1_frozen_state_transfer_s1dn_once_v1.lock",
)


class E1FrozenStateTransferReleaseGateTests(unittest.TestCase):
    @staticmethod
    def _unused_gate(root: Path) -> E1FrozenStateTransferReleaseGate:
        history = root / HISTORY.name
        history.write_bytes(HISTORY.read_bytes())
        targets = tuple(root / name for name in TARGET_NAMES)
        return E1FrozenStateTransferReleaseGate(
            release_id="e1.frozen-state-transfer.s1dp.release.v1",
            execution_id="e1.frozen-state-transfer.s1dn.once.v1",
            history_report_path=str(history),
            report_path=str(targets[0]),
            attempt_path=str(targets[1]),
            lock_path=str(targets[2]),
            one_shot_contract_digest=(
                "3b98967f3922f8f06fdf0576be5e09043e7f230858f2e9f45bf5e5b02dc93d9c"
            ),
            s1_dk_contract_digest=(
                "4574cf1caae3792a3721249dac73b4a589062051bb944fcf2f43f317b4e347f8"
            ),
            producer_digest=S1_DO_PRODUCER_DIGEST,
            executor_digest=S1_DN_EXECUTOR_DIGEST,
            probe_digest=(
                "c0a9a59fb93996bdfd95247a1f6feec19723aeb36c84bd8bc8a423e677fbea7d"
            ),
            geometry_digest=(
                "6cc885c3b6cb41efcdb48cea0aecb02f980f582115e505534679beb3c427b8e6"
            ),
            initial_field_digest=(
                "26a53d5a379ecefb7d707df0336c0f7da1b70d0cd8484e7b6221add9a65b4ce1"
            ),
            source_support_count=110,
            field_node_count=84,
            edge_count=145,
            canonical_execution_permitted=True,
            execution_started=False,
            history_rerun_permitted=False,
            full_s1_dc_decision_permitted=False,
            memory_claim_permitted=False,
            semantic_claim_permitted=False,
            organization_claim_permitted=False,
            topology_claim_permitted=False,
            self_regulation_claim_permitted=False,
            ai_claim_permitted=False,
        )

    def test_project_gate_is_consumed_after_canonical_execution(self) -> None:
        self.assertEqual(
            (True, False, False),
            tuple((REPORTS / name).exists() for name in TARGET_NAMES),
        )
        with self.assertRaisesRegex(ValueError, "already used"):
            prepare_e1_frozen_state_transfer_release_gate(REPORTS, HISTORY)

    def test_unused_gate_binds_sources_inventory_and_boundaries(self) -> None:
        with TemporaryDirectory() as directory:
            gate = self._unused_gate(Path(directory))

            self.assertEqual(S1_DO_PRODUCER_DIGEST, gate.producer_digest)
            self.assertEqual(S1_DN_EXECUTOR_DIGEST, gate.executor_digest)
            self.assertEqual(
                (110, 84, 145),
                (gate.source_support_count, gate.field_node_count, gate.edge_count),
            )
            self.assertTrue(gate.canonical_execution_permitted)
            self.assertFalse(gate.execution_started)
            self.assertEqual(64, len(gate.digest()))

    def test_current_producer_and_executor_sources_match_release(self) -> None:
        self.assertEqual(S1_DO_PRODUCER_DIGEST, current_s1_do_producer_digest())
        self.assertEqual(S1_DN_EXECUTOR_DIGEST, current_s1_dn_executor_digest())

    def test_changed_digest_state_or_claim_release_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            gate = self._unused_gate(Path(directory))
            invalid = (
                {"producer_digest": "0" * 64},
                {"executor_digest": "0" * 64},
                {"canonical_execution_permitted": False},
                {"execution_started": True},
                {"history_rerun_permitted": True},
                {"full_s1_dc_decision_permitted": True},
                {"memory_claim_permitted": True},
                {"ai_claim_permitted": True},
            )
            for change in invalid:
                with self.subTest(change=change), self.assertRaises(
                    E1FrozenStateTransferReleaseGateError
                ):
                    replace(gate, **change)

    def test_target_path_drift_and_used_path_fail_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            gate = self._unused_gate(root)
            with self.assertRaisesRegex(
                E1FrozenStateTransferReleaseGateError,
                "path binding",
            ):
                replace(gate, report_path=str(root / "other.json"))

            Path(gate.report_path).write_text("used\n", encoding="ascii")
            with self.assertRaisesRegex(
                E1FrozenStateTransferReleaseGateError,
                "already used",
            ):
                gate.__post_init__()

    def test_validation_rebuilds_the_complete_current_gate(self) -> None:
        with self.assertRaisesRegex(
            E1FrozenStateTransferReleaseGateError,
            "requires one S1-DP gate",
        ):
            validate_e1_frozen_state_transfer_release_gate(object())

        with TemporaryDirectory() as directory:
            gate = self._unused_gate(Path(directory))
            with self.assertRaisesRegex(
                E1FrozenStateTransferReleaseGateError,
                "project one-shot contract digest changed",
            ):
                validate_e1_frozen_state_transfer_release_gate(gate)

    def test_preparation_and_validation_have_no_execution_reference(self) -> None:
        source = inspect.getsource(prepare_e1_frozen_state_transfer_release_gate)
        source += inspect.getsource(validate_e1_frozen_state_transfer_release_gate)
        for forbidden in (
            "produce_e1_frozen_state_transfer(",
            "execute_e1_frozen_state_transfer_one_shot(",
            "_partition_run(",
        ):
            self.assertNotIn(forbidden, source)

    def test_release_roles_remain_private(self) -> None:
        for role in (
            "E1FrozenStateTransferReleaseGate",
            "prepare_e1_frozen_state_transfer_release_gate",
            "validate_e1_frozen_state_transfer_release_gate",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
