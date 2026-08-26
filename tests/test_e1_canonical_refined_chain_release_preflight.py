from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_refined_chain_release_preflight import (
    E1CanonicalRefinedChainReleasePreflightError,
    prepare_e1_canonical_refined_chain_release_preflight,
)
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"
TARGET_NAMES = (
    "e1_refined_formation_transfer_s1ea_once_v1.json",
    "e1_refined_formation_transfer_s1ea_once_v1.attempt.json",
    "e1_refined_formation_transfer_s1ea_once_v1.lock",
)


class E1CanonicalRefinedChainReleasePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_preflight_binds_producer_executor_core_and_free_paths(self) -> None:
        result = prepare_e1_canonical_refined_chain_release_preflight(
            REPORTS, UPSTREAM
        )

        self.assertTrue(result.producer_bound)
        self.assertTrue(result.executor_core_bound)
        self.assertTrue(result.target_paths_free)
        self.assertFalse(result.canonical_executor_bound)
        self.assertEqual(TARGET_NAMES, tuple(
            Path(value).name for value in (
                result.report_path, result.attempt_path, result.lock_path
            )
        ))

    def test_preflight_calls_neither_producer_nor_executor(self) -> None:
        with patch(
            "mcm_field_organism.e1_canonical_refined_chain_wiring."
            "produce_e1_canonical_refined_chain_result",
            side_effect=AssertionError("producer called"),
        ), patch(
            "mcm_field_organism.e1_refined_chain_one_shot_execution."
            "execute_synthetic_e1_refined_chain_one_shot",
            side_effect=AssertionError("executor called"),
        ):
            prepare_e1_canonical_refined_chain_release_preflight(
                REPORTS, UPSTREAM
            )
        source = inspect.getsource(
            prepare_e1_canonical_refined_chain_release_preflight
        )
        self.assertNotIn("produce_e1_canonical_refined_chain_result(", source)
        self.assertNotIn("execute_synthetic_e1_refined_chain_one_shot(", source)

    def test_release_flags_fail_closed(self) -> None:
        result = prepare_e1_canonical_refined_chain_release_preflight(
            REPORTS, UPSTREAM
        )
        for role in (
            "canonical_executor_bound",
            "execution_permitted",
            "persistence_permitted",
            "memory_claim_permitted",
            "ai_claim_permitted",
        ):
            with self.subTest(role=role):
                with self.assertRaises(E1CanonicalRefinedChainReleasePreflightError):
                    replace(result, **{role: True})

    def test_used_target_fails_closed(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            upstream = root / UPSTREAM.name
            upstream.write_bytes(UPSTREAM.read_bytes())
            (root / TARGET_NAMES[0]).write_text("used\n", encoding="ascii")
            with self.assertRaises(ValueError):
                prepare_e1_canonical_refined_chain_release_preflight(
                    root, upstream
                )

    def test_preflight_is_repeatable_and_private(self) -> None:
        first = prepare_e1_canonical_refined_chain_release_preflight(
            REPORTS, UPSTREAM
        )
        second = prepare_e1_canonical_refined_chain_release_preflight(
            REPORTS, UPSTREAM
        )
        self.assertEqual(first, second)
        for role in (
            "E1CanonicalRefinedChainReleasePreflight",
            "prepare_e1_canonical_refined_chain_release_preflight",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
