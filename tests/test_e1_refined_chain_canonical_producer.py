from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_refined_chain_canonical_producer import (
    E1RefinedChainCanonicalProducerError,
    prepare_e1_refined_chain_canonical_producer,
    produce_e1_refined_chain_canonical_result,
)
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.attempt.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.lock",
)


class E1RefinedChainCanonicalProducerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM, TARGETS
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()
        TARGETS = tuple(REPORTS / path.name for path in TARGETS)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_preflight_binds_canonical_source_geometry_and_roles(self) -> None:
        result = prepare_e1_refined_chain_canonical_producer(REPORTS, UPSTREAM)

        self.assertEqual((220, 110, 200), (
            result.source_support_count,
            result.probe_support_count,
            result.completion_count,
        ))
        self.assertEqual((84, 145), (result.field_node_count, result.edge_count))
        self.assertEqual((
            ("r1", 200), ("r2", 400), ("r4", 800)
        ), result.step_counts)
        self.assertEqual(5, len(result.formation_arms))
        self.assertEqual(7, len(result.probe_arms))
        self.assertTrue(result.canonical_producer_bound)

    def test_preflight_is_repeatable_and_keeps_one_shot_paths_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        first = prepare_e1_refined_chain_canonical_producer(REPORTS, UPSTREAM)
        second = prepare_e1_refined_chain_canonical_producer(REPORTS, UPSTREAM)

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        self.assertEqual((False, False, False), before)

    def test_preflight_does_not_call_field_runtimes_or_producer(self) -> None:
        with patch(
            "mcm_field_organism.e1_refined_chain_canonical_producer."
            "produce_e1_refined_chain_canonical_result",
            side_effect=AssertionError("producer called"),
        ):
            prepare_e1_refined_chain_canonical_producer(REPORTS, UPSTREAM)
        source = inspect.getsource(prepare_e1_refined_chain_canonical_producer)
        for forbidden in (
            "run_e1_asynchronous_field",
            "run_neutral_asynchronous_field",
            "advance_frozen_e1",
            "produce_e1_refined_chain_canonical_result(",
        ):
            self.assertNotIn(forbidden, source)

    def test_preflight_does_not_release_execution_or_claims(self) -> None:
        result = prepare_e1_refined_chain_canonical_producer(REPORTS, UPSTREAM)

        self.assertFalse(result.execution_permitted)
        self.assertFalse(result.execution_started)
        self.assertFalse(result.memory_claim_permitted)
        self.assertFalse(result.ai_claim_permitted)
        with self.assertRaises(E1RefinedChainCanonicalProducerError):
            replace(result, execution_permitted=True)

    def test_reserved_entrypoint_fails_closed_without_s1dz(self) -> None:
        result = prepare_e1_refined_chain_canonical_producer(REPORTS, UPSTREAM)
        with self.assertRaisesRegex(
            E1RefinedChainCanonicalProducerError,
            "remains locked",
        ):
            produce_e1_refined_chain_canonical_result(result, _contract())

    def test_roles_remain_private(self) -> None:
        for role in (
            "E1RefinedChainCanonicalProducerBinding",
            "prepare_e1_refined_chain_canonical_producer",
            "produce_e1_refined_chain_canonical_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


def _contract():
    from mcm_field_organism.e1_refined_chain_one_shot_contract import (
        prepare_e1_refined_chain_one_shot_contract,
    )

    return prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)


if __name__ == "__main__":
    unittest.main()
