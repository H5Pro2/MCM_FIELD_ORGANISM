from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_refined_chain_one_shot_execution import (
    E1CanonicalRefinedChainOneShotExecutionError,
    execute_e1_canonical_refined_chain_once,
    prepare_e1_canonical_one_shot_release,
)
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.attempt.json",
    REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.lock",
)


class E1CanonicalRefinedChainOneShotExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM, TARGETS
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()
        TARGETS = tuple(REPORTS / path.name for path in TARGETS)

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_release_binds_ready_gate_without_touching_paths(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        release = prepare_e1_canonical_one_shot_release(REPORTS, UPSTREAM)

        self.assertTrue(release.execution_permitted)
        self.assertTrue(release.exactly_once)
        self.assertFalse(release.automatic_retry_permitted)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))
        self.assertEqual((False, False, False), before)

    def test_release_drift_fails_closed(self) -> None:
        release = prepare_e1_canonical_one_shot_release(REPORTS, UPSTREAM)
        with self.assertRaises(E1CanonicalRefinedChainOneShotExecutionError):
            replace(release, execution_permitted=False)

    def test_execution_source_orders_marker_before_producer_and_publish(self) -> None:
        source = inspect.getsource(execute_e1_canonical_refined_chain_once)
        self.assertLess(source.index("_exclusive_marker("), source.index(
            "produce_e1_canonical_refined_chain_result("
        ))
        self.assertLess(
            source.index("produce_e1_canonical_refined_chain_result("),
            source.index("_atomic_publish("),
        )

    def test_invalid_release_fails_before_producer(self) -> None:
        with patch(
            "mcm_field_organism.e1_canonical_refined_chain_one_shot_execution."
            "produce_e1_canonical_refined_chain_result",
            side_effect=AssertionError("producer called"),
        ):
            with self.assertRaises(E1CanonicalRefinedChainOneShotExecutionError):
                execute_e1_canonical_refined_chain_once(None, REPORTS, UPSTREAM)

    def test_roles_remain_private(self) -> None:
        for role in (
            "E1CanonicalOneShotRelease",
            "E1CanonicalOneShotReceipt",
            "prepare_e1_canonical_one_shot_release",
            "execute_e1_canonical_refined_chain_once",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
