from __future__ import annotations

from pathlib import Path
import unittest

from mcm_field_organism.public_av_six_arm_field_execution import (
    execute_public_av_six_arm_field_run,
    public_av_six_arm_field_execution_public_roles,
)
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract


class PublicAVSixArmFieldExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = execute_public_av_six_arm_field_run(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
        )

    def test_executes_exact_fixed_arms_and_counts(self) -> None:
        self.assertEqual(
            [56, 56, 56, 56, 41, 15],
            [arm.source_event_count for arm in self.result.arms],
        )
        self.assertEqual(500_000_000, self.result.duration_limit_ticks)

    def test_reproduction_and_permutation_controls_are_exact(self) -> None:
        self.assertTrue(self.result.joint_reproduction_exact)
        self.assertEqual(0.0, self.result.permutation_activation_linf)
        self.assertEqual(0.0, self.result.permutation_afterimage_linf)

    def test_outputs_remain_technical_and_claims_blocked(self) -> None:
        self.assertFalse(self.result.raw_payload_retained)
        self.assertFalse(self.result.metadata_used_by_field)
        self.assertFalse(self.result.memory_claim_allowed)
        self.assertFalse(self.result.organization_claim_allowed)
        forbidden = {"samples", "pixels", "label", "meaning", "reward", "target_topology"}
        self.assertTrue(forbidden.isdisjoint(public_av_six_arm_field_execution_public_roles()))


if __name__ == "__main__":
    unittest.main()
