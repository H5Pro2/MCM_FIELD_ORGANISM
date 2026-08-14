from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_canonical_refined_chain_final_gate import (
    E1CanonicalRefinedChainFinalGateError,
    prepare_e1_canonical_refined_chain_final_gate,
)
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"
TARGET_NAMES = (
    "e1_refined_formation_transfer_s1ea_once_v1.json",
    "e1_refined_formation_transfer_s1ea_once_v1.attempt.json",
    "e1_refined_formation_transfer_s1ea_once_v1.lock",
)


class E1CanonicalRefinedChainFinalGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_gate_reports_static_readiness_without_release(self) -> None:
        gate = prepare_e1_canonical_refined_chain_final_gate(REPORTS, UPSTREAM)

        self.assertEqual("READY_FOR_EXPLICIT_ONE_SHOT_RELEASE", gate.status)
        self.assertTrue(gate.technical_one_shot_ready)
        self.assertTrue(gate.exactly_once_policy_bound)
        self.assertFalse(gate.execution_permitted)
        self.assertFalse(gate.execution_started)
        self.assertEqual(TARGET_NAMES, tuple(
            Path(value).name for value in (
                gate.report_path, gate.attempt_path, gate.lock_path
            )
        ))

    def test_gate_calls_neither_producer_nor_executor(self) -> None:
        with patch(
            "mcm_field_organism.e1_canonical_refined_chain_wiring."
            "produce_e1_canonical_refined_chain_result",
            side_effect=AssertionError("producer called"),
        ), patch(
            "mcm_field_organism.e1_canonical_refined_chain_executor_adapter."
            "execute_e1_canonical_refined_chain_one_shot",
            side_effect=AssertionError("executor called"),
        ):
            prepare_e1_canonical_refined_chain_final_gate(REPORTS, UPSTREAM)
        source = inspect.getsource(prepare_e1_canonical_refined_chain_final_gate)
        self.assertNotIn("produce_e1_canonical_refined_chain_result(", source)
        self.assertNotIn("execute_e1_canonical_refined_chain_one_shot(", source)

    def test_any_release_flag_change_fails_closed(self) -> None:
        gate = prepare_e1_canonical_refined_chain_final_gate(REPORTS, UPSTREAM)
        for role in (
            "execution_permitted",
            "execution_started",
            "persistence_started",
            "automatic_retry_permitted",
            "memory_claim_permitted",
            "ai_claim_permitted",
        ):
            with self.subTest(role=role):
                with self.assertRaises(E1CanonicalRefinedChainFinalGateError):
                    replace(gate, **{role: True})

    def test_used_target_fails_before_gate(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            upstream = root / UPSTREAM.name
            upstream.write_bytes(UPSTREAM.read_bytes())
            (root / TARGET_NAMES[0]).write_text("used\n", encoding="ascii")
            with self.assertRaises(ValueError):
                prepare_e1_canonical_refined_chain_final_gate(root, upstream)

    def test_gate_is_repeatable_and_private(self) -> None:
        first = prepare_e1_canonical_refined_chain_final_gate(REPORTS, UPSTREAM)
        second = prepare_e1_canonical_refined_chain_final_gate(REPORTS, UPSTREAM)
        self.assertEqual(first.digest(), second.digest())
        for role in (
            "E1CanonicalRefinedChainFinalGate",
            "prepare_e1_canonical_refined_chain_final_gate",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
