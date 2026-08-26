from __future__ import annotations

import unittest

import mcm_field_organism as root_api
from mcm_field_organism import audio_video_field_geometry
from mcm_field_organism import audio_video_neutral_field_runtime
from mcm_field_organism import current_api
from mcm_field_organism import finite_audio_video_field_run


class AudioVideoFieldGeometryBoundaryTests(unittest.TestCase):
    def test_legacy_root_current_and_runtime_roles_keep_identity(self) -> None:
        roles = (
            audio_video_field_geometry.ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
            audio_video_field_geometry.audio_video_dock_anatomies,
        )
        names = (
            "ORTHOGONAL_FIELD_SAMPLE_OFFSETS",
            "audio_video_dock_anatomies",
        )
        for name, role in zip(names, roles):
            with self.subTest(role=name):
                self.assertIs(role, getattr(finite_audio_video_field_run, name))
                self.assertIs(role, getattr(root_api, name))
                self.assertIs(role, getattr(current_api, name))
                self.assertIs(
                    role,
                    getattr(audio_video_neutral_field_runtime, name),
                )

    def test_legacy_error_contract_keeps_identity(self) -> None:
        self.assertIs(
            audio_video_field_geometry.FiniteAudioVideoFieldError,
            finite_audio_video_field_run.FiniteAudioVideoFieldError,
        )
        self.assertIs(
            audio_video_field_geometry.FiniteAudioVideoFieldError,
            root_api.FiniteAudioVideoFieldError,
        )

    def test_geometry_boundary_does_not_expose_capture_roles(self) -> None:
        self.assertFalse(
            hasattr(audio_video_field_geometry, "capture_finite_audio_video_field")
        )
        self.assertFalse(
            hasattr(audio_video_field_geometry, "FiniteAudioVideoFieldResult")
        )
        self.assertFalse(
            hasattr(audio_video_field_geometry, "capture_overlapping_receptor_frames")
        )


if __name__ == "__main__":
    unittest.main()
