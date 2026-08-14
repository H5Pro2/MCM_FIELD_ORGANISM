from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.finite_video_path import VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig
from mcm_field_organism.public_av_field_path_compatibility import (
    PublicAVFieldPathCompatibilityError,
    audit_public_av_field_path_compatibility,
    public_av_field_path_compatibility_json_value,
    public_av_field_path_compatibility_public_roles,
)
from mcm_field_organism.public_av_receptor_run import run_public_av_receptor_run
from mcm_field_organism.public_media_source_contract import (
    nasa_earthrise_av_source_contract,
)


MEDIA_PATH = Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4")


class PublicAVFieldPathCompatibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.auditory_config = LogSpectralConfig()
        cls.visual_config = VisualGridConfig(320, 240, 10, 8, 29.97)
        cls.receptor_run = run_public_av_receptor_run(
            MEDIA_PATH,
            nasa_earthrise_av_source_contract(),
            cls.auditory_config,
            cls.visual_config,
            duration_seconds=0.5,
        )

    def test_joint_and_single_modality_arms_share_one_dock_geometry(self) -> None:
        audit = audit_public_av_field_path_compatibility(
            self.receptor_run,
            auditory_config=self.auditory_config,
        )

        self.assertEqual(
            [
                ["auditory", "dock.auditory", 48],
                ["visual", "dock.visual", 240],
            ],
            public_av_field_path_compatibility_json_value(audit)[
                "dock_geometry_digest"
            ],
        )
        accepted = {
            arm.arm_id
            for arm in audit.arms
            if arm.existing_runtime_accepts_arm
        }
        self.assertIn("joint.coarse", accepted)
        self.assertIn("joint.fine", accepted)
        self.assertIn("auditory_only.fine", accepted)
        self.assertIn("visual_only.fine", accepted)
        self.assertTrue(audit.single_modality_arms_supported)

    def test_all_corrected_arms_are_supported_without_special_rules(self) -> None:
        audit = audit_public_av_field_path_compatibility(
            self.receptor_run,
            auditory_config=self.auditory_config,
        )

        self.assertTrue(
            all(arm.existing_runtime_accepts_arm for arm in audit.arms)
        )
        self.assertTrue(audit.all_preregistered_arms_representable_by_existing_runtime)
        self.assertTrue(all(not arm.requires_special_rule for arm in audit.arms))

    def test_audit_does_not_release_runner_field_or_claims(self) -> None:
        audit = audit_public_av_field_path_compatibility(
            self.receptor_run,
            auditory_config=self.auditory_config,
        )

        self.assertFalse(audit.field_runner_implementation_allowed)
        self.assertFalse(audit.field_run_allowed)
        self.assertFalse(audit.synthetic_media_introduced)
        self.assertFalse(audit.special_rules_introduced)
        self.assertFalse(audit.memory_claim_allowed)
        self.assertFalse(audit.meaning_claim_allowed)
        self.assertFalse(audit.organization_claim_allowed)
        self.assertFalse(audit.ai_claim_allowed)

    def test_release_flags_are_rejected(self) -> None:
        audit = audit_public_av_field_path_compatibility(
            self.receptor_run,
            auditory_config=self.auditory_config,
        )

        with self.assertRaisesRegex(
            PublicAVFieldPathCompatibilityError,
            "cannot release",
        ):
            replace(audit, field_run_allowed=True)

    def test_public_roles_exclude_media_payloads_and_field_claims(self) -> None:
        forbidden = {
            "raw_samples",
            "pixels",
            "metadata",
            "label",
            "meaning",
            "reward",
            "memory",
            "organization",
            "ai",
            "target_topology",
        }
        self.assertTrue(
            forbidden.isdisjoint(public_av_field_path_compatibility_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
