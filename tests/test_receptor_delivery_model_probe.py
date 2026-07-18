from __future__ import annotations

import unittest

from mcm_field_organism.receptor_delivery_model_probe import (
    ReceptorDeliveryModelProbeError,
    ReceptorDeliveryRepresentation,
    TimedReceptorDelivery,
    receptor_delivery_model_probe_public_roles,
    run_receptor_delivery_model_probe,
)


class ReceptorDeliveryModelProbeTests(unittest.TestCase):
    def test_point_events_are_rate_dependent(self) -> None:
        result = run_receptor_delivery_model_probe()
        self.assertEqual(80.0, result.known_audio_support.point_event_difference)
        self.assertEqual(80.0, result.unknown_video_support.point_event_difference)

    def test_holding_is_invariant_but_remains_an_explicit_baseline(self) -> None:
        result = run_receptor_delivery_model_probe()
        self.assertAlmostEqual(0.0, result.known_audio_support.hold_integral_difference)
        self.assertAlmostEqual(1.0, result.known_audio_support.dense.hold_integral)
        self.assertAlmostEqual(1.0, result.known_audio_support.sparse.hold_integral)

    def test_overlapping_audio_windows_overcount_dense_delivery(self) -> None:
        result = run_receptor_delivery_model_probe()
        comparison = result.known_audio_support
        self.assertAlmostEqual(10.0, comparison.dense.source_window_total)
        self.assertAlmostEqual(2.0, comparison.sparse.source_window_total)
        self.assertAlmostEqual(8.0, comparison.source_window_difference)

    def test_audio_source_advance_is_invariant_when_fully_known(self) -> None:
        result = run_receptor_delivery_model_probe()
        comparison = result.known_audio_support
        self.assertAlmostEqual(1.0, comparison.dense.source_advance_total)
        self.assertAlmostEqual(1.0, comparison.sparse.source_advance_total)
        self.assertAlmostEqual(0.0, comparison.source_advance_difference)

    def test_unknown_video_support_stays_unknown(self) -> None:
        comparison = run_receptor_delivery_model_probe().unknown_video_support
        self.assertIsNone(comparison.dense.source_window_total)
        self.assertIsNone(comparison.dense.source_advance_total)
        self.assertIsNone(comparison.source_window_difference)
        self.assertIsNone(comparison.source_advance_difference)

    def test_noncausal_or_disordered_delivery_sequence_is_rejected(self) -> None:
        with self.assertRaisesRegex(ReceptorDeliveryModelProbeError, "strictly"):
            ReceptorDeliveryRepresentation(
                "broken",
                10,
                0.1,
                (
                    TimedReceptorDelivery(0, 1.0),
                    TimedReceptorDelivery(0, 1.0),
                ),
            )

    def test_public_roles_do_not_select_runtime_or_field_semantics(self) -> None:
        forbidden = {
            "selected_model",
            "field_activation",
            "modality_weight",
            "valid_until",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(
            forbidden.isdisjoint(receptor_delivery_model_probe_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
