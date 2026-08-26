from __future__ import annotations

from dataclasses import replace
import inspect
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_refined_chain_one_shot_contract import (
    E1RefinedChainOneShotContractError,
    S1_DW_REPORT_FIELDS,
    current_s1_dl_transfer_implementation_digest,
    current_s1_dv_implementation_digest,
    prepare_e1_refined_chain_one_shot_contract,
)
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"
TARGET_NAMES = (
    "e1_refined_formation_transfer_s1ea_once_v1.json",
    "e1_refined_formation_transfer_s1ea_once_v1.attempt.json",
    "e1_refined_formation_transfer_s1ea_once_v1.lock",
)


class E1RefinedChainOneShotContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_contract_binds_chain_sources_evidence_and_paths(self) -> None:
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)

        self.assertEqual(
            "e1.refined-formation-transfer.s1ea.once.v1",
            contract.execution_id,
        )
        self.assertEqual(S1_DW_REPORT_FIELDS, contract.report_fields)
        self.assertEqual(
            TARGET_NAMES,
            tuple(Path(value).name for value in contract._target_path_values()),
        )
        self.assertEqual((("r1", 1), ("r2", 2), ("r4", 4)), contract.refinements)

    def test_contract_binds_current_formation_and_transfer_sources(self) -> None:
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)

        self.assertEqual(
            current_s1_dv_implementation_digest(),
            contract.formation_implementation_digest,
        )
        self.assertEqual(
            current_s1_dl_transfer_implementation_digest(),
            contract.transfer_implementation_digest,
        )

    def test_contract_does_not_release_execution_or_claims(self) -> None:
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)

        for role in (
            "execution_permitted",
            "execution_started",
            "canonical_producer_bound",
            "canonical_executor_bound",
            "old_history_rerun_permitted",
            "old_transfer_rerun_permitted",
            "memory_claim_permitted",
            "semantic_claim_permitted",
            "organization_claim_permitted",
            "topology_claim_permitted",
            "self_regulation_claim_permitted",
            "ai_claim_permitted",
        ):
            self.assertFalse(getattr(contract, role))

    def test_contract_digest_is_repeatable_and_paths_remain_unused(self) -> None:
        before = tuple((REPORTS / name).exists() for name in TARGET_NAMES)
        first = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        second = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        after = tuple((REPORTS / name).exists() for name in TARGET_NAMES)

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, after)

    def test_used_path_and_changed_release_fail_closed(self) -> None:
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with self.assertRaises(E1RefinedChainOneShotContractError):
            replace(contract, execution_permitted=True)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            upstream = root / UPSTREAM.name
            upstream.write_bytes(UPSTREAM.read_bytes())
            (root / TARGET_NAMES[0]).write_text("used\n", encoding="ascii")
            with self.assertRaisesRegex(
                E1RefinedChainOneShotContractError,
                "already used",
            ):
                prepare_e1_refined_chain_one_shot_contract(root, upstream)

    def test_changed_upstream_evidence_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            changed = json.loads(UPSTREAM.read_text(encoding="ascii"))
            changed["technical_status"] = "CHANGED"
            upstream = root / UPSTREAM.name
            upstream.write_text(json.dumps(changed) + "\n", encoding="ascii")
            with self.assertRaises(ValueError):
                prepare_e1_refined_chain_one_shot_contract(root, upstream)

    def test_preparation_has_no_formation_transfer_or_probe_execution(self) -> None:
        source = inspect.getsource(prepare_e1_refined_chain_one_shot_contract)
        for forbidden in (
            "run_synthetic_e1_refined_formation",
            "produce_e1_frozen_state_transfer",
            "execute_e1_frozen_state_transfer_one_shot",
            "run_e1_asynchronous_field",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1RefinedChainOneShotContract",
            "prepare_e1_refined_chain_one_shot_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
