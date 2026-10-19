"""Neutral qualification for the private identity-preserving PPB update."""

from __future__ import annotations

import unittest

from mcm_field_organism import _ppb1_reference as ppb
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from tools import _s2jw_default_live_profile as profile_module
from tools import _s2sp_private_memory_compare as core


def _frame(config: ppb.PPB1BankConfig, values: tuple[float, ...], tick: int) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        "visual",
        config.geometry_id,
        f"neutral.snapshot.{tick}",
        "neutral.clock",
        tick,
        tick + 1,
        config.carrier_ids,
        values,
    )


class S2SPIdentityPreservingUpdateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = profile_module.build_s2jw_default_live_profile().profile.visual_config
        self.values = tuple(0.09411764705882353 if index % 3 == 0 else 0.25 for index in range(len(self.config.carrier_ids)))

    def test_identical_input_keeps_each_identity_component_bitstable(self) -> None:
        state = ppb.initial_ppb1_bank_state(self.config)
        state = ppb.advance_ppb1_bank_identity_preserving(self.config, state, _frame(self.config, self.values, 0)).poststate
        result = ppb.advance_ppb1_bank_identity_preserving(self.config, state, _frame(self.config, self.values, 1))
        slot = next(slot for slot in result.poststate.slots if slot.occupied)
        self.assertEqual(slot.prototype_values, self.values)
        self.assertEqual(slot.support_count, 2)
        self.assertEqual(result.poststate.accepted_step_count, 2)
        self.assertEqual(result.poststate.last_source_window_end_tick, 2)

    def test_different_components_keep_the_historical_expression(self) -> None:
        initial = ppb.initial_ppb1_bank_state(self.config)
        first = ppb.advance_ppb1_bank_identity_preserving(self.config, initial, _frame(self.config, self.values, 0)).poststate
        mixed = list(self.values)
        mixed[1] = 0.5
        result = ppb.advance_ppb1_bank_identity_preserving(self.config, first, _frame(self.config, tuple(mixed), 1))
        slot = next(slot for slot in result.poststate.slots if slot.occupied)
        self.assertEqual(slot.prototype_values[0], self.values[0])
        self.assertEqual(slot.prototype_values[1], 0.95 * self.values[1] + 0.05 * mixed[1])
        self.assertEqual(slot.prototype_values[2], self.values[2])

    def test_historical_mode_retains_the_existing_formula(self) -> None:
        initial = ppb.initial_ppb1_bank_state(self.config)
        first = ppb.advance_ppb1_bank(self.config, initial, _frame(self.config, self.values, 0)).poststate
        result = ppb.advance_ppb1_bank(self.config, first, _frame(self.config, self.values, 1))
        slot = next(slot for slot in result.poststate.slots if slot.occupied)
        self.assertEqual(slot.prototype_values[0], 0.95 * self.values[0] + 0.05 * self.values[0])
        self.assertNotEqual(slot.prototype_values[0], self.values[0])

    def test_atomic_formation_keeps_fast_and_ppb_progression(self) -> None:
        profile = profile_module.build_s2jw_default_live_profile()
        config = core.build_config()
        sources = core.Sources(profile)
        state = core.coordinator.initial_s2jv_composite_state(config)
        for ordinal, event_id in enumerate(("neutral.e01", "neutral.e02", "neutral.e03")):
            pair, _ = sources.formation(event_id=event_id, ordinal=ordinal, cells=core.TARGET)
            state = core.form(
                config=config,
                state=state,
                pair=pair,
                event_id=event_id,
                run_id="s2sp-identity-neutral",
                ppb_update_mode=core.coordinator.tspm1.PPB_UPDATE_IDENTITY_PRESERVING,
            ).poststate
        self.assertEqual(state.generation, 3)
        self.assertEqual(state.tspm_state.fast_state.accepted_exposure_count, 3)
        self.assertEqual(state.tspm_state.visual_ppb1_state.accepted_step_count, 2)


if __name__ == "__main__":
    unittest.main()
