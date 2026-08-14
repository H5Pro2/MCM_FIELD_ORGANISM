from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_canonical_producer_binding import (
    E1ConfirmationCanonicalProducerBindingError,
    S1_EB9_IMPLEMENTATION_DIGESTS,
    current_s1_eb9_implementation_digests,
    prepare_e1_confirmation_canonical_producer_binding,
    produce_e1_confirmation_canonical_result,
)
from mcm_field_organism.e1_confirmation_chain_contract import (
    prepare_e1_confirmation_chain_contract,
)


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


class E1ConfirmationCanonicalProducerBindingTests(unittest.TestCase):
    def test_preflight_binds_source_geometry_state_and_plans(self) -> None:
        result = prepare_e1_confirmation_canonical_producer_binding(
            REPORTS,
            UPSTREAM,
        )

        self.assertEqual((220, 110, 200, 100), (
            result.history_support_count,
            result.probe_support_count,
            result.history_completion_count,
            result.probe_completion_count,
        ))
        self.assertEqual((84, 145), (result.field_node_count, result.edge_count))
        self.assertEqual((
            ("r2", 400), ("r4", 800), ("r8", 1600)
        ), result.history_step_counts)
        self.assertEqual((
            ("r2", 200), ("r4", 400), ("r8", 800)
        ), result.probe_step_counts)
        self.assertTrue(result.canonical_producer_bound)

    def test_preflight_binds_all_new_chain_implementations(self) -> None:
        result = prepare_e1_confirmation_canonical_producer_binding(
            REPORTS,
            UPSTREAM,
        )

        self.assertEqual(
            S1_EB9_IMPLEMENTATION_DIGESTS,
            current_s1_eb9_implementation_digests(),
        )
        self.assertEqual(
            current_s1_eb9_implementation_digests(),
            result.implementation_digests,
        )

    def test_preflight_is_repeatable_and_keeps_paths_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = prepare_e1_confirmation_canonical_producer_binding(
            REPORTS,
            UPSTREAM,
        )
        second = prepare_e1_confirmation_canonical_producer_binding(
            REPORTS,
            UPSTREAM,
        )

        self.assertEqual(first, second)
        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_preflight_does_not_call_runtime_or_producer(self) -> None:
        with patch(
            "mcm_field_organism.e1_confirmation_canonical_producer_binding."
            "produce_e1_confirmation_canonical_result",
            side_effect=AssertionError("producer called"),
        ):
            prepare_e1_confirmation_canonical_producer_binding(
                REPORTS,
                UPSTREAM,
            )
        source = inspect.getsource(
            prepare_e1_confirmation_canonical_producer_binding
        )
        for forbidden in (
            "run_e1_asynchronous_field",
            "run_synthetic_e1_confirmation_seven_arm_probe",
            "compose_synthetic_e1_confirmation_chain",
            "produce_e1_confirmation_canonical_result(",
        ):
            self.assertNotIn(forbidden, source)

    def test_execution_persistence_rerun_and_claims_remain_closed(self) -> None:
        result = prepare_e1_confirmation_canonical_producer_binding(
            REPORTS,
            UPSTREAM,
        )

        for role in (
            "execution_permitted",
            "execution_started",
            "persistence_permitted",
            "s1_ea6_rerun_permitted",
            "memory_claim_permitted",
            "semantic_claim_permitted",
            "organization_claim_permitted",
            "topology_claim_permitted",
            "self_regulation_claim_permitted",
            "ai_claim_permitted",
        ):
            self.assertFalse(getattr(result, role))
        with self.assertRaises(E1ConfirmationCanonicalProducerBindingError):
            replace(result, execution_permitted=True)

    def test_reserved_entrypoint_remains_locked(self) -> None:
        binding = prepare_e1_confirmation_canonical_producer_binding(
            REPORTS,
            UPSTREAM,
        )
        contract = prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)

        with self.assertRaisesRegex(
            E1ConfirmationCanonicalProducerBindingError,
            "remains locked",
        ):
            produce_e1_confirmation_canonical_result(binding, contract)

    def test_roles_remain_private(self) -> None:
        for role in (
            "E1ConfirmationCanonicalProducerBinding",
            "prepare_e1_confirmation_canonical_producer_binding",
            "produce_e1_confirmation_canonical_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
