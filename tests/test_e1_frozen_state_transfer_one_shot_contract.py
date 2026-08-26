from __future__ import annotations

from dataclasses import replace
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_frozen_state_transfer_contract import (
    S1_DK_ARMS,
    S1_DK_B_AB_DIGEST,
    S1_DK_B_BA_DIGEST,
    S1_DK_METRICS,
    S1_DK_PROBE_DIGEST,
)
from mcm_field_organism.e1_frozen_state_transfer_one_shot_contract import (
    E1FrozenStateTransferOneShotContractError,
    S1_DK_CONTRACT_DIGEST,
    S1_DL_IMPLEMENTATION_DIGEST,
    S1_DM_PARTITIONS,
    S1_DM_REPORT_FIELDS,
    S1_DM_TECHNICAL_STATUSES,
    current_s1_dl_implementation_digest,
    prepare_e1_frozen_state_transfer_one_shot_contract,
    s1_dm_configuration_digest,
)


HISTORY = Path("reports/e1_a0_av_history_s1di_once_v1.json")
TARGET_NAMES = (
    "e1_frozen_state_transfer_s1dn_once_v1.json",
    "e1_frozen_state_transfer_s1dn_once_v1.attempt.json",
    "e1_frozen_state_transfer_s1dn_once_v1.lock",
)


class E1FrozenStateTransferOneShotContractTests(unittest.TestCase):
    def test_contract_binds_evidence_implementation_partitions_and_metrics(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_frozen_state_transfer_one_shot_contract(
                Path(directory), HISTORY
            )

        self.assertEqual("e1.frozen-state-transfer.s1dn.once.v1", contract.execution_id)
        self.assertEqual(S1_DK_CONTRACT_DIGEST, contract.s1_dk_contract_digest)
        self.assertEqual(
            S1_DL_IMPLEMENTATION_DIGEST,
            contract.transfer_implementation_digest,
        )
        self.assertEqual(S1_DK_B_AB_DIGEST, contract.b_ab_digest)
        self.assertEqual(S1_DK_B_BA_DIGEST, contract.b_ba_digest)
        self.assertEqual(S1_DK_PROBE_DIGEST, contract.probe_digest)
        self.assertEqual(S1_DM_PARTITIONS, contract.partitions)
        self.assertEqual(S1_DK_ARMS, contract.arms)
        self.assertEqual(S1_DK_METRICS, contract.metrics)
        self.assertEqual(S1_DM_REPORT_FIELDS, contract.report_fields)
        self.assertEqual(S1_DM_TECHNICAL_STATUSES, contract.technical_statuses)
        self.assertEqual(s1_dm_configuration_digest(), contract.configuration_digest)
        self.assertEqual(64, len(contract.digest()))

    def test_preparation_creates_no_file_and_starts_no_execution(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_frozen_state_transfer_one_shot_contract(
                root, HISTORY
            )

            self.assertEqual((), tuple(root.iterdir()))
            self.assertTrue(contract.execution_permitted)
            self.assertFalse(contract.execution_started)
            self.assertFalse(contract.history_rerun_permitted)
            self.assertFalse(contract.full_s1_dc_decision_permitted)

    def test_any_used_target_path_blocks_the_one_shot(self) -> None:
        for name in TARGET_NAMES:
            with self.subTest(name=name), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / name).write_text("used\n", encoding="ascii")
                with self.assertRaisesRegex(
                    E1FrozenStateTransferOneShotContractError,
                    "already used",
                ):
                    prepare_e1_frozen_state_transfer_one_shot_contract(
                        root, HISTORY
                    )

    def test_contract_digest_is_repeatable_and_path_bound(self) -> None:
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            left = prepare_e1_frozen_state_transfer_one_shot_contract(
                Path(first), HISTORY
            )
            repeated = prepare_e1_frozen_state_transfer_one_shot_contract(
                Path(first), HISTORY
            )
            right = prepare_e1_frozen_state_transfer_one_shot_contract(
                Path(second), HISTORY
            )

        self.assertEqual(left.digest(), repeated.digest())
        self.assertNotEqual(left.digest(), right.digest())

    def test_current_transfer_source_matches_registered_digest(self) -> None:
        self.assertEqual(
            S1_DL_IMPLEMENTATION_DIGEST,
            current_s1_dl_implementation_digest(),
        )

    def test_missing_or_changed_history_evidence_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                E1FrozenStateTransferOneShotContractError,
                "history evidence",
            ):
                prepare_e1_frozen_state_transfer_one_shot_contract(
                    root, root / "missing.json"
                )

            changed = json.loads(HISTORY.read_text(encoding="ascii"))
            changed["d_state"] = 0.0
            changed_path = root / "changed.json"
            changed_path.write_text(
                json.dumps(changed, separators=(",", ":")) + "\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(
                E1FrozenStateTransferOneShotContractError,
                "history evidence",
            ):
                prepare_e1_frozen_state_transfer_one_shot_contract(
                    root, changed_path
                )

    def test_changed_binding_state_or_claim_release_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_frozen_state_transfer_one_shot_contract(
                Path(directory), HISTORY
            )

        invalid = (
            {"transfer_implementation_digest": "0" * 64},
            {"configuration_digest": "0" * 64},
            {"execution_started": True},
            {"history_rerun_permitted": True},
            {"full_s1_dc_decision_permitted": True},
            {"memory_claim_permitted": True},
            {"ai_claim_permitted": True},
        )
        for change in invalid:
            with self.subTest(change=change), self.assertRaises(
                E1FrozenStateTransferOneShotContractError
            ):
                replace(contract, **change)

    def test_static_preparation_has_no_state_load_or_probe_execution_reference(self) -> None:
        source = inspect.getsource(
            prepare_e1_frozen_state_transfer_one_shot_contract
        )
        for forbidden in (
            "load_e1_frozen_states",
            "run_synthetic_e1_frozen_state_transfer_arms",
            "advance_frozen_e1_fast_shared_field_transient",
            "build_e1_av_history_permutation",
            "produce_e1_a0_av_histories",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1FrozenStateTransferOneShotContract",
            "prepare_e1_frozen_state_transfer_one_shot_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
