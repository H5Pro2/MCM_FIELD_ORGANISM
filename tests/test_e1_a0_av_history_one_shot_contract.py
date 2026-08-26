from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_a0_av_history_one_shot_contract import (
    E1A0AVHistoryOneShotContractError,
    S1_DE_HISTORY_AB_DIGEST,
    S1_DE_HISTORY_BA_DIGEST,
    S1_DE_PERMUTATION_DIGEST,
    S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
    S1_DH_ALLOWED_METRICS,
    S1_DH_REPORT_FIELDS,
    S1_DH_TECHNICAL_STATUSES,
    current_s1_dg_producer_implementation_digest,
    prepare_e1_a0_av_history_one_shot_contract,
    s1_dh_configuration_digest,
)


class E1A0AVHistoryOneShotContractTests(unittest.TestCase):
    def test_contract_binds_source_implementation_configuration_and_metrics(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_a0_av_history_one_shot_contract(
                Path(directory)
            )

        self.assertEqual("e1.a0-av-history.s1di.once.v1", contract.execution_id)
        self.assertEqual(S1_DE_HISTORY_AB_DIGEST, contract.history_ab_digest)
        self.assertEqual(S1_DE_HISTORY_BA_DIGEST, contract.history_ba_digest)
        self.assertEqual(S1_DE_PERMUTATION_DIGEST, contract.permutation_digest)
        self.assertEqual(
            S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
            contract.producer_implementation_digest,
        )
        self.assertEqual(s1_dh_configuration_digest(), contract.configuration_digest)
        self.assertEqual(S1_DH_ALLOWED_METRICS, contract.allowed_metrics)
        self.assertEqual(S1_DH_REPORT_FIELDS, contract.report_fields)
        self.assertEqual(S1_DH_TECHNICAL_STATUSES, contract.technical_statuses)
        self.assertEqual(64, len(contract.digest()))

    def test_preparation_creates_no_file_and_starts_no_execution(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            contract = prepare_e1_a0_av_history_one_shot_contract(root)

            self.assertEqual((), tuple(root.iterdir()))
            self.assertTrue(contract.execution_permitted)
            self.assertFalse(contract.execution_started)

    def test_any_used_path_blocks_the_one_shot(self) -> None:
        for name in (
            "e1_a0_av_history_s1di_once_v1.json",
            "e1_a0_av_history_s1di_once_v1.attempt.json",
            "e1_a0_av_history_s1di_once_v1.lock",
        ):
            with self.subTest(name=name), TemporaryDirectory() as directory:
                root = Path(directory)
                (root / name).write_text("used\n", encoding="ascii")
                with self.assertRaisesRegex(
                    E1A0AVHistoryOneShotContractError,
                    "already used",
                ):
                    prepare_e1_a0_av_history_one_shot_contract(root)

    def test_contract_digest_is_repeatable_and_path_bound(self) -> None:
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            first_contract = prepare_e1_a0_av_history_one_shot_contract(
                Path(first)
            )
            repeated = prepare_e1_a0_av_history_one_shot_contract(Path(first))
            second_contract = prepare_e1_a0_av_history_one_shot_contract(
                Path(second)
            )

        self.assertEqual(first_contract.digest(), repeated.digest())
        self.assertNotEqual(first_contract.digest(), second_contract.digest())

    def test_current_producer_source_matches_the_registered_digest(self) -> None:
        self.assertEqual(
            S1_DG_PRODUCER_IMPLEMENTATION_DIGEST,
            current_s1_dg_producer_implementation_digest(),
        )

    def test_changed_digest_state_or_claim_release_is_rejected(self) -> None:
        with TemporaryDirectory() as directory:
            contract = prepare_e1_a0_av_history_one_shot_contract(
                Path(directory)
            )
            invalid = (
                {"producer_implementation_digest": "0" * 64},
                {"configuration_digest": "0" * 64},
                {"execution_started": True},
                {"probe_permitted": True},
                {"memory_claim_permitted": True},
                {"ai_claim_permitted": True},
            )
            for change in invalid:
                with self.subTest(change=change), self.assertRaises(
                    E1A0AVHistoryOneShotContractError
                ):
                    replace(contract, **change)

    def test_static_preparation_has_no_history_or_probe_execution_reference(self) -> None:
        source = inspect.getsource(
            prepare_e1_a0_av_history_one_shot_contract
        )
        for forbidden in (
            "produce_e1_a0_av_histories",
            "build_e1_av_history_permutation",
            "advance_frozen_e1_fast_shared_field_transient",
            "run_e1_asynchronous_field",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1A0AVHistoryOneShotContract",
            "prepare_e1_a0_av_history_one_shot_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
