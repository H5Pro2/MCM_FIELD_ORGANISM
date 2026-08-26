from __future__ import annotations

import unittest

from mcm_field_organism.ci_accommodation_baseline import (
    CIAccommodationBaselineError,
    CIAccommodationConfig,
    CIState,
    apply_ci_backreaction,
    advance_ci_accommodation,
    advance_ci_from_field_snapshot,
    advance_ci_null_exposure,
)
from mcm_field_organism.controlled_audio_video_test_world import (
    controlled_reentry_world_family,
    run_controlled_test_world,
)
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)


class CIAccommodationBaselineTests(unittest.TestCase):
    def test_step_is_bounded_and_returns_conjugate_response(self) -> None:
        result = advance_ci_accommodation(
            CIState(("c.0", "c.1"), (0.0, -0.5)),
            (1.0, 0.5),
            CIAccommodationConfig(alpha=1.0, beta=2.0),
            0.1,
        )

        self.assertTrue(all(-1.0 <= value <= 1.0 for value in result.state.values))
        self.assertEqual(2, len(result.exchange))
        self.assertEqual(
            tuple(-2.0 * value for value in result.exchange),
            result.backreaction,
        )
        self.assertGreater(result.state.values[0], 0.0)

    def test_identical_input_is_deterministic(self) -> None:
        state = CIState(("c.0",), (0.2,))
        config = CIAccommodationConfig(alpha=0.5, beta=1.0)
        first = advance_ci_accommodation(state, (0.8,), config, 0.1)
        second = advance_ci_accommodation(state, (0.8,), config, 0.1)
        self.assertEqual(first, second)

    def test_invalid_step_size_is_rejected_instead_of_clipped(self) -> None:
        with self.assertRaises(CIAccommodationBaselineError):
            advance_ci_accommodation(
                CIState(("c.0",), (0.0,)),
                (1.0,),
                CIAccommodationConfig(alpha=2.0, beta=1.0),
                0.2,
            )

    def test_no_raw_or_semantic_payload_is_retained(self) -> None:
        result = advance_ci_accommodation(
            CIState(("c.0",), (0.0,)),
            (0.5,),
            CIAccommodationConfig(alpha=1.0, beta=1.0),
            0.1,
        )
        self.assertEqual(("c.0",), result.state.component_ids)
        self.assertFalse(hasattr(result, "raw_audio"))
        self.assertFalse(hasattr(result, "label"))
        self.assertFalse(hasattr(result, "memory"))

    def test_field_snapshot_can_drive_one_passive_ci_step(self) -> None:
        world, _ = controlled_reentry_world_family()
        run = run_controlled_test_world(
            world,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        )
        snapshot = run.field_run.field.snapshot()
        state = CIState(
            tuple(neuron.neuron_id for neuron in snapshot.layer.neurons),
            tuple(0.0 for _ in snapshot.layer.neurons),
        )
        result = advance_ci_from_field_snapshot(
            snapshot,
            state,
            CIAccommodationConfig(alpha=0.5, beta=1.0),
            0.1,
        )
        self.assertEqual(state.component_ids, result.state.component_ids)
        self.assertEqual(len(snapshot.layer.neurons), len(result.exchange))

    def test_backreaction_projection_is_separate_and_deterministic(self) -> None:
        state = CIState(("c.0",), (0.0,))
        advance = advance_ci_accommodation(
            state,
            (1.0,),
            CIAccommodationConfig(alpha=1.0, beta=2.0),
            0.1,
        )
        projected = apply_ci_backreaction((0.5,), advance, 0.1)
        self.assertLess(projected[0], 0.5)
        self.assertEqual(projected, apply_ci_backreaction((0.5,), advance, 0.1))

    def test_null_exposure_is_explicit_zero_input(self) -> None:
        state = CIState(("n0", "n1"), (0.4, -0.2))
        config = CIAccommodationConfig(alpha=0.5, beta=0.25)
        result = advance_ci_null_exposure(state, config, 0.1)
        expected = advance_ci_accommodation(
            state, (0.0, 0.0), config, 0.1
        )
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
