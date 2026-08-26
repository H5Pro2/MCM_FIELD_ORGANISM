from __future__ import annotations

import math
from pathlib import Path
import unittest

from mcm_field_organism.local_adaptive_receptivity import (
    ADAPTIVE_RECEPTIVITY_ALPHA_AXIS,
    LocalAdaptiveReceptivityConfig,
    LocalAdaptiveReceptivityError,
    LocalReceptivityState,
    advance_local_receptivity,
    advance_receptivity_state,
    run_adaptive_receptivity_field,
)
from mcm_field_organism.neutral_asynchronous_field_runtime import (
    run_neutral_asynchronous_field,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
)
from mcm_field_organism.public_av_six_arm_field_execution import _sequences
from mcm_field_organism.public_av_two_stage_return_execution import _fresh_field, _steps
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


class LocalAdaptiveReceptivityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sequences = _sequences(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
        )
        cls.substrate = NeutralLocalFieldSubstrateConfig(1.0)
        cls.afterimage = NeutralFastAfterimageConfig(0.5)
        cls.dissipation = NeutralFieldDissipationConfig(0.0)

    def test_preregistered_axis_and_constants_are_rejected_if_changed(self) -> None:
        self.assertEqual((0.0, 0.5, 1.0), ADAPTIVE_RECEPTIVITY_ALPHA_AXIS)
        with self.assertRaises(LocalAdaptiveReceptivityError):
            LocalAdaptiveReceptivityConfig(0.25)
        with self.assertRaises(LocalAdaptiveReceptivityError):
            LocalAdaptiveReceptivityConfig(0.5, beta_per_second=0.5)

    def test_analytic_update_matches_closed_form(self) -> None:
        config = LocalAdaptiveReceptivityConfig(0.5)
        actual = advance_local_receptivity(0.8, 0.4, 2.0, config)
        rate = 0.25 + 0.5 * 0.4
        equilibrium = 0.25 / rate
        expected = equilibrium + (0.8 - equilibrium) * math.exp(-rate * 2.0)
        self.assertAlmostEqual(expected, actual, places=15)

    def test_update_is_bounded_and_zero_energy_recovers_toward_one(self) -> None:
        config = LocalAdaptiveReceptivityConfig(1.0)
        adapted = advance_local_receptivity(1.0, 100.0, 100.0, config)
        self.assertEqual(0.25, adapted)
        recovered = advance_local_receptivity(adapted, 0.0, 2.0, config)
        self.assertGreater(recovered, adapted)
        self.assertLessEqual(recovered, 1.0)

    def test_alpha_zero_is_digest_and_metric_identical_to_neutral_runtime(self) -> None:
        field = _fresh_field(self.sequences)
        steps = _steps(self.sequences, 0, 500_000_000)
        neutral = run_neutral_asynchronous_field(
            field, self.sequences, steps, self.substrate,
            afterimage_config=self.afterimage,
            dissipation_config=self.dissipation,
        )
        adaptive = run_adaptive_receptivity_field(
            field, LocalReceptivityState.fresh(field), self.sequences, steps,
            self.substrate, self.afterimage, LocalAdaptiveReceptivityConfig(0.0),
            self.dissipation,
        )
        self.assertEqual(neutral.field.layer.digest(), adaptive.field.layer.digest())
        self.assertEqual(neutral.field.snapshot().digest(), adaptive.field.snapshot().digest())
        self.assertEqual((1.0,) * len(adaptive.receptivity.values), adaptive.receptivity.values)

    def test_state_update_is_local_and_does_not_mutate_input_state(self) -> None:
        field = _fresh_field(self.sequences)
        state = LocalReceptivityState.fresh(field)
        updated = advance_receptivity_state(
            state, field, 1.0, LocalAdaptiveReceptivityConfig(1.0)
        )
        self.assertIsNot(state, updated)
        self.assertEqual((1.0,) * len(state.values), state.values)
        self.assertEqual(state.neuron_ids, updated.neuron_ids)


if __name__ == "__main__":
    unittest.main()
