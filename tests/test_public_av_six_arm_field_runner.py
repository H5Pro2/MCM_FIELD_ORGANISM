from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.finite_video_path import VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig
from mcm_field_organism.public_av_field_path_compatibility import (
    audit_public_av_field_path_compatibility,
)
from mcm_field_organism.public_av_receptor_run import run_public_av_receptor_run
from mcm_field_organism.public_av_six_arm_field_runner import (
    PublicAVSixArmFieldRunnerError,
    execute_public_av_six_arm_field_runner,
    public_av_six_arm_field_runner_json_value,
    public_av_six_arm_field_runner_public_roles,
    wire_public_av_six_arm_field_runner,
)
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


MEDIA_PATH = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


class PublicAVSixArmFieldRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        auditory_config = LogSpectralConfig()
        receptor_run = run_public_av_receptor_run(
            MEDIA_PATH,
            nasa_earthrise_av_source_contract(),
            auditory_config,
            VisualGridConfig(320, 240, 10, 8, 29.97),
            duration_seconds=0.5,
        )
        cls.compatibility = audit_public_av_field_path_compatibility(
            receptor_run,
            auditory_config=auditory_config,
        )

    def test_runner_wires_exactly_the_corrected_six_arms(self) -> None:
        wiring = wire_public_av_six_arm_field_runner(self.compatibility)

        self.assertTrue(wiring.wiring_complete)
        self.assertTrue(wiring.all_arms_structurally_supported)
        self.assertTrue(wiring.implementation_allowed_for_wiring_only)
        self.assertEqual(
            [
                "joint.coarse",
                "joint.fine",
                "joint.fine.reproduction",
                "joint.fine.permuted",
                "auditory_only.fine",
                "visual_only.fine",
            ],
            [arm.arm_id for arm in wiring.arms],
        )

    def test_every_arm_carries_fixed_field_contracts_and_measurements(self) -> None:
        wiring = wire_public_av_six_arm_field_runner(self.compatibility)

        for arm in wiring.arms:
            self.assertFalse(arm.executable)
            self.assertTrue(arm.fresh_field_required)
            self.assertEqual(
                (
                    ("auditory", "dock.auditory", 48),
                    ("visual", "dock.visual", 240),
                ),
                arm.dock_geometry_digest,
            )
            self.assertIn("snapshot_digest", arm.measured_roles)
            self.assertIn(
                "neutral_local_field_substrate_config_1.0",
                arm.field_parameter_contract,
            )

    def test_execution_and_claim_release_stay_constructively_blocked(self) -> None:
        wiring = wire_public_av_six_arm_field_runner(self.compatibility)

        self.assertFalse(wiring.executable)
        self.assertFalse(wiring.field_run_allowed)
        self.assertFalse(wiring.raw_payload_retained)
        self.assertFalse(wiring.metadata_used_by_field)
        self.assertFalse(wiring.memory_claim_allowed)
        self.assertFalse(wiring.meaning_claim_allowed)
        self.assertFalse(wiring.organization_claim_allowed)
        self.assertFalse(wiring.ai_claim_allowed)
        with self.assertRaisesRegex(PublicAVSixArmFieldRunnerError, "not released"):
            execute_public_av_six_arm_field_runner(wiring)

    def test_release_flags_are_rejected(self) -> None:
        wiring = wire_public_av_six_arm_field_runner(self.compatibility)

        with self.assertRaisesRegex(PublicAVSixArmFieldRunnerError, "cannot release"):
            replace(wiring, field_run_allowed=True)

    def test_json_and_public_roles_exclude_raw_payloads_and_claims(self) -> None:
        wiring = wire_public_av_six_arm_field_runner(self.compatibility)
        payload = public_av_six_arm_field_runner_json_value(wiring)
        encoded = repr(payload)

        self.assertIn("joint.fine", encoded)
        self.assertNotIn("raw_samples", encoded)
        self.assertNotIn("pixels", encoded)
        forbidden = {
            "raw_samples",
            "pixels",
            "metadata",
            "label",
            "reward",
            "target_topology",
            "field_snapshot",
            "field_state",
        }
        self.assertTrue(forbidden.isdisjoint(public_av_six_arm_field_runner_public_roles()))


if __name__ == "__main__":
    unittest.main()
