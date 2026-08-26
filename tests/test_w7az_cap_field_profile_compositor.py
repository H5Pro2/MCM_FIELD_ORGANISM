from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.w7aa_p0_seven_path_consumer import consume_w7aa_p0_seven_path_plan
from mcm_field_organism.w7ac_observer_seven_path_consumer import consume_w7ac_observer_seven_path_result
from mcm_field_organism.w7ae_cap_seven_path_consumer import consume_w7ae_cap_seven_path_plan
from mcm_field_organism.w7ag_passive_cap_measurement_handoff import compose_w7ag_passive_cap_measurement_handoff
from mcm_field_organism.w7ai_p0_zero_start_measurement_reference import compose_w7ai_p0_zero_start_measurement_references
from mcm_field_organism.w7ak_cap_p0_raw_contrast_compositor import compose_w7ak_cap_p0_raw_contrasts
from mcm_field_organism.w7ay_cap_field_profile_contract import build_w7ay_cap_field_profile_contract
from mcm_field_organism.w7az_cap_field_profile_compositor import (
    W7AZCAPFieldProfileCompositorError,
    compose_w7az_cap_field_profiles,
)
from mcm_field_organism.w7m_capacity_function_matrix import build_w7m_capacity_function_matrix_adapter
from mcm_field_organism.w7w_symmetric_source_family import build_w7w_source_authorization, build_w7w_symmetric_source_family
from mcm_field_organism.w7y_seven_path_source_plan import build_w7y_seven_path_source_plan


class W7AZCAPFieldProfileCompositorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        adapter = build_w7m_capacity_function_matrix_adapter()
        family = build_w7w_symmetric_source_family(adapter)
        authorization = build_w7w_source_authorization(adapter, family)
        plan = build_w7y_seven_path_source_plan(adapter, family, authorization)
        p0 = consume_w7aa_p0_seven_path_plan(adapter, family, authorization, plan)
        observer = consume_w7ac_observer_seven_path_result(
            adapter, authorization, plan, p0
        )
        cap = consume_w7ae_cap_seven_path_plan(
            adapter, family, authorization, plan, p0, observer
        )
        cls.handoff = compose_w7ag_passive_cap_measurement_handoff(
            adapter, family, authorization, plan, cap
        )
        p0_references = compose_w7ai_p0_zero_start_measurement_references(
            adapter,
            family,
            authorization,
            plan,
            p0,
            observer,
            cap,
            cls.handoff,
        )
        cls.control = compose_w7ak_cap_p0_raw_contrasts(
            cls.handoff, p0_references
        )
        cls.contract = build_w7ay_cap_field_profile_contract()
        cls.result = compose_w7az_cap_field_profiles(
            cls.contract, cls.handoff, cls.control
        )

    def test_eight_raw_contrast_curves_are_present(self) -> None:
        self.assertEqual(8, len(self.result.contrasts))
        self.assertTrue(
            all(len(item.checkpoint_effect_linf) == 5 for item in self.result.contrasts)
        )

    def test_joint_effect_is_maximum_of_s_and_h_linf(self) -> None:
        for item in self.result.contrasts:
            self.assertEqual(
                item.checkpoint_effect_linf,
                tuple(
                    max(s, h)
                    for s, h in zip(item.checkpoint_S_linf, item.checkpoint_H_linf)
                ),
            )

    def test_two_cap_profiles_are_composed_without_observer_comparison(self) -> None:
        self.assertEqual(
            ("ab", "ba"),
            tuple(item.profile.direction for item in self.result.profiles),
        )
        self.assertTrue(
            all(item.profile.resolution == "RESOLVED" for item in self.result.profiles)
        )
        self.assertFalse(self.result.observer_comparison_performed)
        self.assertEqual(
            "ecb14d76ab49a05010c4d988308f729415d7583570d0908f2588df0964254d9f",
            self.result.composition_digest,
        )

    def test_cap_p0_values_are_only_controls_and_inputs_stay_unchanged(self) -> None:
        self.assertFalse(self.result.cap_p0_values_used_as_path_effects)
        self.assertEqual(
            self.handoff.measurement_handoff_digest,
            self.result.cap_handoff_digest,
        )
        self.assertEqual(
            self.control.raw_contrast_composition_digest,
            self.result.cap_p0_control_digest,
        )

    def test_composition_is_passive_and_claims_remain_locked(self) -> None:
        self.assertFalse(self.result.writes_back)
        self.assertFalse(self.result.field_function_decision_allowed)
        self.assertFalse(self.result.memory_claim_allowed)

    def test_tampering_is_rejected(self) -> None:
        with self.assertRaises(W7AZCAPFieldProfileCompositorError):
            replace(self.result, observer_comparison_performed=True)
        with self.assertRaises(W7AZCAPFieldProfileCompositorError):
            replace(self.result.contrasts[0], normalized=True)

    def test_compositor_is_not_publicly_exported(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "compose_w7az_cap_field_profiles"))


if __name__ == "__main__":
    unittest.main()
