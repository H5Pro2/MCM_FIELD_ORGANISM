from __future__ import annotations

import unittest

from mcm_field_organism.public_av_repeated_participation_linearity_audit import (
    REPEATED_PARTICIPATION_ARM_IDS,
    REPEATED_PARTICIPATION_CYCLE_COUNTS,
    REPEATED_PARTICIPATION_GAP_TICKS,
    REPEATED_PARTICIPATION_HISTORY_CYCLE_COUNTS,
    PublicAVRepeatedParticipationLinearityError,
    _affine_residual,
    _component_record,
    _cycle_delta,
    _rate_history,
    _state_record,
    _vector_metrics,
    _zero_value_sequences,
)
from mcm_field_organism.public_av_six_arm_field_execution import _sequences
from mcm_field_organism.public_av_two_stage_return_execution import _fresh_field
from mcm_field_organism.public_media_source_contract import nasa_earthrise_av_source_contract
from pathlib import Path


class PublicAVRepeatedParticipationLinearityAuditTests(unittest.TestCase):
    def test_axes_gap_and_arms_are_fixed(self) -> None:
        self.assertEqual((1, 2, 4, 8), REPEATED_PARTICIPATION_CYCLE_COUNTS)
        self.assertEqual(tuple(range(1, 9)), REPEATED_PARTICIPATION_HISTORY_CYCLE_COUNTS)
        self.assertEqual(2_000_000_000, REPEATED_PARTICIPATION_GAP_TICKS)
        self.assertEqual(3, len(REPEATED_PARTICIPATION_ARM_IDS))

    def test_zero_input_preserves_events_and_only_resets_values(self) -> None:
        sequences = _sequences(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
        )
        zero = _zero_value_sequences(sequences)
        self.assertEqual(tuple(len(item.frames) for item in sequences),
                         tuple(len(item.frames) for item in zero))
        for original_sequence, zero_sequence in zip(sequences, zero, strict=True):
            for original, changed in zip(original_sequence.frames, zero_sequence.frames, strict=True):
                self.assertEqual(original.field_time, changed.field_time)
                self.assertEqual(original.frame.carrier_ids, changed.frame.carrier_ids)
                self.assertEqual((0.0,) * len(original.frame.values), changed.frame.values)

    def test_affine_residual_is_zero_for_exact_superposition(self) -> None:
        residual = _affine_residual((3.0, -1.0), (1.0, 2.0), (2.0, -3.0))
        self.assertEqual({"l1": 0.0, "l2": 0.0, "linf": 0.0}, residual)

    def test_affine_residual_rejects_unaligned_vectors(self) -> None:
        with self.assertRaises(PublicAVRepeatedParticipationLinearityError):
            _affine_residual((1.0,), (1.0, 2.0), (0.0,))

    def test_component_record_keeps_components_and_residual_separate(self) -> None:
        record = _component_record((3.0, 1.0), (1.0, 1.0), (2.0, 0.0))
        self.assertIn("carry_centered_linf_to_fresh", record)
        self.assertIn("carry_constant_energy_fraction", record)
        self.assertEqual(0.0, record["affine_residual"]["linf"])

    def test_vector_metrics_include_norms_mean_and_maximum_amplitude(self) -> None:
        metrics = _vector_metrics((3.0, -4.0))
        self.assertEqual(7.0, metrics["l1"])
        self.assertEqual(5.0, metrics["l2"])
        self.assertEqual(4.0, metrics["linf"])
        self.assertEqual(-0.5, metrics["mean"])

    def test_cycle_delta_is_component_local_and_rejects_misalignment(self) -> None:
        delta = _cycle_delta((3.0, -1.0), (1.0, 2.0))
        self.assertEqual(5.0, delta["l1"])
        self.assertEqual(3.0, delta["linf"])
        with self.assertRaises(PublicAVRepeatedParticipationLinearityError):
            _cycle_delta((1.0,), (1.0, 2.0))

    def test_state_record_contains_component_norms_and_both_digests(self) -> None:
        sequences = _sequences(
            Path("sources/media/NASA Earthrise Realtime Apollo 8.mp4"),
            nasa_earthrise_av_source_contract(),
        )
        record = _state_record(_fresh_field(sequences))
        self.assertEqual({"l1", "l2", "linf", "mean"}, set(record["activation"]))
        self.assertEqual({"l1", "l2", "linf", "mean"}, set(record["afterimage"]))
        self.assertRegex(record["layer_digest"], r"^[0-9a-f]{64}$")
        self.assertIsNone(record["snapshot_digest"])
        self.assertFalse(record["snapshot_available"])

    def test_rate_history_requires_all_eight_cycles_and_has_boundedness_series(self) -> None:
        cycles = [
            {
                "cycle": cycle,
                "maximum_amplitude": {"activation": float(cycle), "afterimage": cycle / 2},
            }
            for cycle in REPEATED_PARTICIPATION_HISTORY_CYCLE_COUNTS
        ]
        history = _rate_history(0.05, cycles)
        self.assertEqual(8, len(history["cycles"]))
        self.assertEqual(list(range(1, 9)), [item["cycle"] for item in history["boundedness_series"]])
        with self.assertRaises(PublicAVRepeatedParticipationLinearityError):
            _rate_history(0.05, cycles[:-1])

    def test_source_records_every_cycle_state_delta_and_boundedness_axis(self) -> None:
        source = Path(
            "mcm_field_organism/public_av_repeated_participation_linearity_audit.py"
        ).read_text(encoding="utf-8")
        for field in (
            '"before_contact"',
            '"after_contact"',
            '"after_contact_free_interval"',
            '"layer_digest"',
            '"snapshot_digest"',
            '"cycle_to_cycle_post_contact_delta"',
            '"maximum_amplitude"',
            '"boundedness_series"',
        ):
            self.assertIn(field, source)
        self.assertIn('"history_cycle_counts"', source)

    def test_source_disables_threshold_rate_selection_and_claims(self) -> None:
        source = Path(
            "mcm_field_organism/public_av_repeated_participation_linearity_audit.py"
        ).read_text(encoding="utf-8")
        self.assertIn('"threshold_defined": False', source)
        self.assertIn('"preferred_rate_selected": False', source)
        self.assertIn('"organization_claim_allowed": False', source)


if __name__ == "__main__":
    unittest.main()
