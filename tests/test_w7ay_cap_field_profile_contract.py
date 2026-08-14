from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.w7ay_cap_field_profile_contract import (
    W7AYCAPFieldProfileContractError,
    build_w7ay_cap_field_profile_contract,
)


class W7AYCAPFieldProfileContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = build_w7ay_cap_field_profile_contract()

    def test_contract_binds_existing_cap_sources_and_w7at_floor(self) -> None:
        self.assertEqual(
            "898e94bdbc2b5b0f893c5c512a684fd15544845d25de1a97febc83ffc8bcccd8",
            self.contract.required_w7ag_handoff_digest,
        )
        self.assertEqual(
            "ca047546d37a0ebd5728ee6adcf27d083c2a7fce3aad82f882284f08629f1fc3",
            self.contract.required_w7ak_composition_digest,
        )
        self.assertEqual(1.8915768951188738e-07, self.contract.w7at_effect_floor)
        self.assertEqual(
            "08f229d21891bdf55f7274439303fdae312c2ddec03883b6a04db4f5949a89f9",
            self.contract.contract_digest,
        )

    def test_all_eight_path_contrasts_are_fixed(self) -> None:
        self.assertEqual(8, len(self.contract.contrast_inventory))
        self.assertEqual(
            ("ab_old_a_under_b", "ab", "ub"),
            self.contract.contrast_inventory[0],
        )
        self.assertEqual(
            ("ba_new_a_after_neutral", "ua", "ug"),
            self.contract.contrast_inventory[-1],
        )

    def test_effect_metric_uses_joint_samplewise_fast_state_linf(self) -> None:
        self.assertEqual(
            "max-of-samplewise-S-linf-and-H-linf",
            self.contract.effect_metric,
        )
        self.assertEqual(
            "ticks-and-s-h-geometry-must-match-exactly",
            self.contract.alignment_rule,
        )

    def test_profile_mapping_is_symmetric_and_uses_own_denominator(self) -> None:
        self.assertEqual(("ab", "ba"), tuple(row[0] for row in self.contract.profile_mapping))
        self.assertEqual(
            "initial-old-effect-strictly-above-w7at-floor",
            self.contract.denominator_rule,
        )
        self.assertEqual("no-epsilon-rescue", self.contract.unresolved_policy)

    def test_w7ak_is_control_not_lifecycle_effect_source(self) -> None:
        self.assertEqual(
            "cap-p0-provenance-and-alignment-control-only",
            self.contract.w7ak_role,
        )
        self.assertFalse(self.contract.w7ak_values_used_as_path_effects)

    def test_contract_accepts_no_values_or_decisions(self) -> None:
        self.assertEqual(
            0,
            len(inspect.signature(build_w7ay_cap_field_profile_contract).parameters),
        )
        self.assertFalse(self.contract.accept_result_values)
        self.assertFalse(self.contract.profile_composition_allowed)
        self.assertFalse(self.contract.observer_explanation_allowed)
        self.assertFalse(self.contract.field_function_decision_allowed)
        self.assertFalse(self.contract.memory_claim_allowed)

    def test_tampering_is_rejected(self) -> None:
        with self.assertRaises(W7AYCAPFieldProfileContractError):
            replace(self.contract, w7ak_values_used_as_path_effects=True)

    def test_contract_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "build_w7ay_cap_field_profile_contract"))


if __name__ == "__main__":
    unittest.main()
