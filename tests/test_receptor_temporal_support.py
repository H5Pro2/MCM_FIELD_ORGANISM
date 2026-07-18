from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    OrganismTimedReceptorFrame,
    ReceptorContactFrame,
    ReceptorTemporalSupportError,
    ReceptorTimeSequence,
    audit_auditory_temporal_support,
    audit_visual_temporal_support,
    receptor_temporal_support_public_roles,
)


def sequence(
    modality: str,
    source_clock_id: str,
    source_intervals: tuple[tuple[int, int], ...],
    read_intervals: tuple[tuple[int, int], ...],
) -> ReceptorTimeSequence:
    frames = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                modality_id=modality,
                geometry_id=f"{modality}.geometry.v1",
                snapshot_id=f"{modality}.receptor.{index}",
                clock_id=source_clock_id,
                window_start_tick=source_start,
                window_end_tick=source_end,
                carrier_ids=(f"{modality}.carrier.0",),
                values=(0.25,),
            ),
            CommonFieldTime("organism.test", read_start, read_end),
        )
        for index, ((source_start, source_end), (read_start, read_end))
        in enumerate(zip(source_intervals, read_intervals, strict=True))
    )
    return ReceptorTimeSequence(
        modality,
        f"{modality}.geometry.v1",
        "organism.test",
        frames,
    )


class ReceptorTemporalSupportTests(unittest.TestCase):
    def test_audio_reports_rolling_window_stride_and_overlap(self) -> None:
        audit = audit_auditory_temporal_support(
            sequence(
                "auditory",
                "audio.sample",
                ((0, 100), (10, 110), (20, 120)),
                ((0, 2), (2, 4), (4, 6)),
            ),
            sample_rate=1000,
            organism_ticks_per_second=1000.0,
        )
        self.assertEqual("rolling_analysis_window", audit.source_window_role)
        self.assertEqual(0.1, audit.source_window_seconds)
        self.assertEqual(0.01, audit.nominal_output_period_seconds)
        self.assertAlmostEqual(0.9, audit.source_overlap_fraction)
        self.assertEqual(0.002, audit.organism_read_median_seconds)

    def test_visual_frame_period_is_not_claimed_as_exposure_support(self) -> None:
        audit = audit_visual_temporal_support(
            sequence(
                "visual",
                "video.frame",
                ((0, 1), (1, 2), (2, 3)),
                ((0, 20), (20, 40), (40, 60)),
            ),
            nominal_frames_per_second=30.0,
            organism_ticks_per_second=1000.0,
        )
        self.assertEqual("frame_identity_interval", audit.source_window_role)
        self.assertIsNone(audit.source_window_seconds)
        self.assertAlmostEqual(1.0 / 30.0, audit.nominal_output_period_seconds)
        self.assertFalse(audit.organism_support_is_mapped)

    def test_read_duration_never_becomes_world_support(self) -> None:
        auditory = audit_auditory_temporal_support(
            sequence(
                "auditory",
                "audio.sample",
                ((0, 100), (10, 110)),
                ((0, 1), (10, 30)),
            ),
            sample_rate=1000,
            organism_ticks_per_second=1000.0,
        )
        self.assertFalse(auditory.organism_read_interval_is_world_support)
        self.assertFalse(auditory.organism_support_is_mapped)

    def test_inconsistent_source_stride_is_rejected(self) -> None:
        with self.assertRaisesRegex(ReceptorTemporalSupportError, "stable positive stride"):
            audit_auditory_temporal_support(
                sequence(
                    "auditory",
                    "audio.sample",
                    ((0, 100), (10, 110), (30, 130)),
                    ((0, 2), (2, 4), (4, 6)),
                ),
                sample_rate=1000,
            )

    def test_wrong_source_clock_is_rejected(self) -> None:
        with self.assertRaisesRegex(ReceptorTemporalSupportError, "video.frame"):
            audit_visual_temporal_support(
                sequence(
                    "visual",
                    "other.clock",
                    ((0, 1), (1, 2)),
                    ((0, 2), (2, 4)),
                ),
                nominal_frames_per_second=30.0,
            )

    def test_public_roles_do_not_claim_hold_or_field_effect(self) -> None:
        roles = set(receptor_temporal_support_public_roles())
        forbidden = {
            "held_value",
            "valid_until",
            "field_activation",
            "afterimage",
            "weight",
            "meaning",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
