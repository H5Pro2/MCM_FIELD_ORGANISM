from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_chain_contract import (
    E1ConfirmationChainContractError,
    S1_EB4_METRICS,
    S1_EB4_REPORT_FIELDS,
    S1_EB_IMPLEMENTATION_DIGESTS,
    current_s1_eb_implementation_digests,
    prepare_e1_confirmation_chain_contract,
)


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGET_NAMES = (
    "e1_refined_confirmation_s1eb_once_v1.json",
    "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    "e1_refined_confirmation_s1eb_once_v1.lock",
)


class E1ConfirmationChainContractTests(unittest.TestCase):
    def test_contract_binds_sources_plans_and_result_surface(self) -> None:
        result = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)

        self.assertEqual(
            "e1.refined-confirmation.s1eb.once.v1",
            result.execution_id,
        )
        self.assertEqual((("r2", 2), ("r4", 4), ("r8", 8)), result.refinements)
        self.assertEqual(S1_EB4_METRICS, result.metrics)
        self.assertEqual(S1_EB4_REPORT_FIELDS, result.report_fields)
        self.assertEqual(
            TARGET_NAMES,
            tuple(Path(value).name for value in result._target_path_values()),
        )

    def test_contract_binds_all_current_implementation_sources(self) -> None:
        result = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)

        self.assertEqual(
            S1_EB_IMPLEMENTATION_DIGESTS,
            current_s1_eb_implementation_digests(),
        )
        self.assertEqual(
            current_s1_eb_implementation_digests(),
            result.implementation_digests,
        )

    def test_contract_keeps_execution_tuning_and_claims_closed(self) -> None:
        result = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)

        for role in (
            "canonical_producer_bound",
            "canonical_executor_bound",
            "execution_permitted",
            "execution_started",
            "s1_ea6_rerun_permitted",
            "posthoc_threshold_change_permitted",
            "memory_claim_permitted",
            "semantic_claim_permitted",
            "organization_claim_permitted",
            "topology_claim_permitted",
            "self_regulation_claim_permitted",
            "ai_claim_permitted",
        ):
            self.assertFalse(getattr(result, role))

    def test_contract_is_repeatable_and_keeps_paths_free(self) -> None:
        before = tuple((REPORTS / name).exists() for name in TARGET_NAMES)
        first = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)
        second = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(64, len(first.digest()))
        self.assertEqual((False, False, False), before)
        self.assertEqual(
            before,
            tuple((REPORTS / name).exists() for name in TARGET_NAMES),
        )

    def test_changed_release_fails_closed(self) -> None:
        result = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)

        for change in (
            {"execution_permitted": True},
            {"canonical_producer_bound": True},
            {"posthoc_threshold_change_permitted": True},
            {"memory_claim_permitted": True},
        ):
            with self.assertRaises(E1ConfirmationChainContractError):
                replace(result, **change)

    def test_used_target_path_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            upstream = root / UPSTREAM.name
            upstream.write_bytes(UPSTREAM.read_bytes())
            (root / TARGET_NAMES[0]).write_text("used\n", encoding="ascii")

            with self.assertRaises(ValueError):
                prepare_e1_confirmation_chain_contract(root, upstream)

    def test_preparation_contains_no_chain_execution(self) -> None:
        source = inspect.getsource(prepare_e1_confirmation_chain_contract)
        for forbidden in (
            "run_synthetic_e1_confirmation_formation",
            "run_private_e1_refined_seven_arm_probe",
            "run_e1_asynchronous_field",
            "execute_e1_refined_chain_one_shot",
        ):
            self.assertNotIn(forbidden, source)

    def test_contract_remains_private(self) -> None:
        for role in (
            "E1ConfirmationChainContract",
            "prepare_e1_confirmation_chain_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
