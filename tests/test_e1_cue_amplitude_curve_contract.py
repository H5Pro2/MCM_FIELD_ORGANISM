from __future__ import annotations

from dataclasses import replace
import inspect
import math
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_cue_amplitude_curve_contract import (
    E1CueAmplitudeCurveContractError,
    S1_CT_REPORT_SHA256,
    S1_CU_AMPLITUDES,
    S1_CU_DECISIONS,
    build_e1_cue_amplitude_curve_contract,
)


class E1CueAmplitudeCurveContractTests(unittest.TestCase):
    def test_contract_binds_amplitudes_arms_and_decisions(self) -> None:
        contract = build_e1_cue_amplitude_curve_contract()
        self.assertEqual((0.125, 0.25, 0.5, 1.0), contract.amplitudes)
        self.assertEqual(S1_CU_DECISIONS, contract.decision_order)
        self.assertEqual(72, len(contract.model_arms) * len(contract.history_arms) * len(contract.cue_sides) * len(contract.amplitudes))
        self.assertFalse(contract.execution_permitted)
        self.assertFalse(contract.executed)

    def test_mirrored_cues_are_energy_matched_at_every_amplitude(self) -> None:
        contract = build_e1_cue_amplitude_curve_contract()
        for amplitude in S1_CU_AMPLITUDES:
            left = contract.cue("left", amplitude)
            right = contract.cue("right", amplitude)
            self.assertEqual(left, tuple(reversed(right)))
            self.assertEqual(
                math.fsum(value * value for value in left),
                math.fsum(value * value for value in right),
            )

    def test_linear_null_and_s1ct_anchor_are_fixed(self) -> None:
        contract = build_e1_cue_amplitude_curve_contract()
        self.assertEqual("interaction(q)=q*interaction(1.0)", contract.linear_null_model)
        self.assertEqual(S1_CT_REPORT_SHA256, contract.s1ct_report_sha256)
        self.assertEqual(0.0021516247701185154, contract.s1ct_full_interaction_linf)

    def test_contract_digest_is_deterministic(self) -> None:
        first = build_e1_cue_amplitude_curve_contract().digest()
        second = build_e1_cue_amplitude_curve_contract().digest()
        self.assertEqual(first, second)
        self.assertEqual(
            "88e56327c18c2c39244befff17747e99dbf0110e68a5ecb99c32cb63c625cbe0",
            first,
        )

    def test_changed_amplitude_or_permission_is_rejected(self) -> None:
        contract = build_e1_cue_amplitude_curve_contract()
        with self.assertRaises(E1CueAmplitudeCurveContractError):
            replace(contract, amplitudes=(0.25, 0.5, 1.0))
        with self.assertRaises(E1CueAmplitudeCurveContractError):
            replace(contract, execution_permitted=True)

    def test_builder_has_no_execution_references(self) -> None:
        source = inspect.getsource(build_e1_cue_amplitude_curve_contract)
        self.assertNotIn("run_", source)
        self.assertNotIn("compose_", source)
        self.assertNotIn("evaluate_", source)

    def test_contract_roles_remain_private(self) -> None:
        for role in (
            "E1CueAmplitudeCurveContract",
            "build_e1_cue_amplitude_curve_contract",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
