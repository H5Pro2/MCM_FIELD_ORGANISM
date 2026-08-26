from pathlib import Path
import unittest

from mcm_field_organism.public_av_local_adaptive_receptivity import (
    ADAPTIVE_RECEPTIVITY_ARM_IDS,
    ADAPTIVE_RECEPTIVITY_FIXED_LEAK_RATE,
    ADAPTIVE_RECEPTIVITY_GAP_TICKS,
)
from mcm_field_organism.local_adaptive_receptivity import LocalReceptivityState
from mcm_field_organism.public_av_six_arm_field_execution import _sequences
from mcm_field_organism.public_av_two_stage_return_execution import _fresh_field
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


class PublicAVLocalAdaptiveReceptivityTests(unittest.TestCase):
    def test_axes_and_four_arms_are_fixed(self) -> None:
        self.assertEqual(2_000_000_000, ADAPTIVE_RECEPTIVITY_GAP_TICKS)
        self.assertEqual(0.0, ADAPTIVE_RECEPTIVITY_FIXED_LEAK_RATE)
        self.assertEqual(4, len(ADAPTIVE_RECEPTIVITY_ARM_IDS))
        self.assertEqual(4, len(set(ADAPTIVE_RECEPTIVITY_ARM_IDS)))

    def test_measurement_contract_separates_all_three_components(self) -> None:
        sequences = _sequences(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
        )
        field = _fresh_field(sequences)
        state = LocalReceptivityState.fresh(field)
        self.assertEqual(len(field.layer.neurons), len(state.values))
        source = Path(
            "mcm_field_organism/public_av_local_adaptive_receptivity.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"activation": _metrics(activation)', source)
        self.assertIn('"afterimage": _metrics(afterimage)', source)
        self.assertIn('"receptivity": _metrics(receptivity.values)', source)
        self.assertIn("identity_stage_one", source)
        self.assertIn("identity_carried_field", source)

    def test_source_disables_threshold_selection_and_all_claims(self) -> None:
        source = Path(
            "mcm_field_organism/public_av_local_adaptive_receptivity.py"
        ).read_text(encoding="utf-8")
        for field in (
            '"threshold_defined": False',
            '"preferred_rate_selected": False',
            '"memory_claim_allowed": False',
            '"meaning_claim_allowed": False',
            '"organization_claim_allowed": False',
            '"ai_claim_allowed": False',
        ):
            self.assertIn(field, source)
        self.assertNotIn("reward", source.lower())
        self.assertNotIn("label", source.lower())


if __name__ == "__main__":
    unittest.main()
