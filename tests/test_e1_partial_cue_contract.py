from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_partial_cue_contract import (
    E1PartialCueContractError,
    S1_CO_DECISIONS,
    build_e1_partial_cue_contract,
)


class E1PartialCueContractTests(unittest.TestCase):
    def test_contract_binds_world_arms_and_decision_order(self) -> None:
        contract = build_e1_partial_cue_contract()
        self.assertEqual(("left-g4", "right-g4", "neutral"), contract.history_arms)
        self.assertEqual(("e1", "p0", "b1-static-h8"), contract.model_arms)
        self.assertEqual(S1_CO_DECISIONS, contract.decision_order)
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.executed)

    def test_partial_cues_are_mirrored_energy_matched_and_weaker(self) -> None:
        contract = build_e1_partial_cue_contract()
        left = contract.left_partial_cue
        right = contract.right_partial_cue
        left_energy = math.fsum(value * value for value in left)
        right_energy = math.fsum(value * value for value in right)
        full_energy = math.fsum(value * value for value in contract.left_full_cue)
        self.assertEqual(left, tuple(reversed(right)))
        self.assertEqual(left_energy, right_energy)
        self.assertLess(left_energy, full_energy)

    def test_history_and_cue_timing_are_fixed(self) -> None:
        contract = build_e1_partial_cue_contract()
        self.assertEqual(8, contract.history_repetitions)
        self.assertEqual(1.0, contract.history_interval_seconds)
        self.assertEqual(4.0, contract.gap_seconds)
        self.assertEqual(1.0, contract.cue_interval_seconds)
        self.assertEqual(20.0, contract.ticks_per_second)

    def test_contract_digest_is_deterministic(self) -> None:
        self.assertEqual(
            build_e1_partial_cue_contract().digest(),
            build_e1_partial_cue_contract().digest(),
        )
        self.assertEqual(64, len(build_e1_partial_cue_contract().digest()))
        self.assertEqual(
            "a69eb30b91fb3cb69bb319b8a514be761eb4c2700e3ad720b2042dc7c63a7528",
            build_e1_partial_cue_contract().digest(),
        )

    def test_changed_partial_cue_or_execution_permission_is_rejected(self) -> None:
        contract = build_e1_partial_cue_contract()
        with self.assertRaises(E1PartialCueContractError):
            replace(contract, left_partial_cue=(0.5, 0.0, 0.0))
        with self.assertRaises(E1PartialCueContractError):
            replace(contract, execution_permitted=True)

    def test_builder_has_no_runner_or_evaluator_reference(self) -> None:
        source = inspect.getsource(build_e1_partial_cue_contract)
        self.assertNotIn("advance_", source)
        self.assertNotIn("produce_", source)
        self.assertNotIn("evaluate_", source)

    def test_contract_roles_remain_private(self) -> None:
        for role in ("E1PartialCueContract", "build_e1_partial_cue_contract"):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
