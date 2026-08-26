from __future__ import annotations

import unittest

import mcm_field_organism as root_api
from mcm_field_organism import audio_video_neutral_field_runtime
from mcm_field_organism import controlled_receptor_capture
from mcm_field_organism import receptor_time_alignment


class ControlledReceptorCaptureBoundaryTests(unittest.TestCase):
    def test_legacy_root_and_runtime_keep_capture_function_identity(self) -> None:
        role = controlled_receptor_capture.capture_timed_audio_video_receptor_sequences
        self.assertIs(
            role,
            receptor_time_alignment.capture_timed_audio_video_receptor_sequences,
        )
        self.assertIs(role, root_api.capture_timed_audio_video_receptor_sequences)
        self.assertIs(
            role,
            audio_video_neutral_field_runtime.capture_timed_audio_video_receptor_sequences,
        )

    def test_controlled_capture_does_not_expose_alignment_audit(self) -> None:
        self.assertFalse(
            hasattr(controlled_receptor_capture, "audit_receptor_time_alignment")
        )
        self.assertFalse(
            hasattr(controlled_receptor_capture, "ReceptorTimeAlignmentAudit")
        )
        self.assertFalse(
            hasattr(controlled_receptor_capture, "CapturedReceptorTimeAudit")
        )


if __name__ == "__main__":
    unittest.main()
