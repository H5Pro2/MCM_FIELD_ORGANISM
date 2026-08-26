from __future__ import annotations

import unittest

import mcm_field_organism as root_api
from mcm_field_organism import asynchronous_receptor_events
from mcm_field_organism import browser_receptor_bridge
from mcm_field_organism import current_api
from mcm_field_organism import field_time_partition
from mcm_field_organism import neutral_asynchronous_field_runtime
from mcm_field_organism import neutral_field_session
from mcm_field_organism import receptor_proposal_handoff_audit
from mcm_field_organism import receptor_temporal_support
from mcm_field_organism import receptor_time_alignment
from mcm_field_organism import transient_dock_trajectory
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeAlignmentError,
    ReceptorTimeSequence,
)


class ReceptorTimeModelBoundaryTests(unittest.TestCase):
    def test_legacy_root_and_current_exports_keep_identity(self) -> None:
        roles = (
            ReceptorTimeAlignmentError,
            OrganismTimedReceptorFrame,
            ReceptorTimeSequence,
        )
        for role in roles:
            with self.subTest(role=role.__name__):
                self.assertIs(role, getattr(receptor_time_alignment, role.__name__))
                self.assertIs(role, getattr(root_api, role.__name__))
                self.assertIs(role, getattr(current_api, role.__name__))

    def test_core_consumers_use_the_device_neutral_time_model(self) -> None:
        sequence_consumers = (
            asynchronous_receptor_events,
            browser_receptor_bridge,
            field_time_partition,
            neutral_asynchronous_field_runtime,
            neutral_field_session,
            receptor_proposal_handoff_audit,
            receptor_temporal_support,
        )
        for module in sequence_consumers:
            with self.subTest(module=module.__name__):
                self.assertIs(ReceptorTimeSequence, module.ReceptorTimeSequence)
        frame_consumers = (
            browser_receptor_bridge,
            receptor_proposal_handoff_audit,
            transient_dock_trajectory,
        )
        for module in frame_consumers:
            with self.subTest(module=module.__name__):
                self.assertIs(OrganismTimedReceptorFrame, module.OrganismTimedReceptorFrame)

    def test_time_model_does_not_expose_capture_roles(self) -> None:
        import mcm_field_organism.receptor_time_model as model

        self.assertFalse(hasattr(model, "capture_timed_audio_video_receptors"))
        self.assertFalse(
            hasattr(model, "capture_timed_audio_video_receptor_sequences")
        )
        self.assertFalse(hasattr(model, "ReceptorTimeAlignmentAudit"))


if __name__ == "__main__":
    unittest.main()
