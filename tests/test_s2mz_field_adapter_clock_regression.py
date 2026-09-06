"""Focused regression for the S2-MT field-clock adapter binding."""

from __future__ import annotations

import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

from tools import _s2lo_private_role_free_stream_runner as field_source
from tools import _s2mt_private_transfer_runtime_runner as transfer


ROOT = Path(__file__).resolve().parents[1]


class S2MZFieldAdapterClockRegressionTests(unittest.TestCase):
    def test_e01_uses_bound_clock_and_default_remains_s2ln(self) -> None:
        parameter = inspect.signature(field_source.build_s2lo_field_adapter).parameters[
            "field_clock_id"
        ]
        self.assertEqual(field_source.FIELD_CLOCK_ID, parameter.default)
        default_adapter = field_source.build_s2lo_field_adapter()
        self.assertEqual(
            field_source.FIELD_CLOCK_ID,
            inspect.getclosurevars(default_adapter).nonlocals["field_clock_id"],
        )

        plan = transfer.raw_source.build_presealed_plan()
        config = transfer.field_source._build_config()
        materialized = transfer._materialize_events(plan, config)
        e01 = materialized[0]
        self.assertEqual(("e01", 1), (e01.spec.event_code, e01.spec.ordinal))

        field_input = e01.field_input
        self.assertEqual(2, len(field_input.timed_frames))
        self.assertTrue(
            all(
                item.field_time.clock_id == transfer.FIELD_CLOCK_ID
                for item in field_input.timed_frames
            )
        )
        initial = field_source.initial_s2lo_field_state(field_input)
        event = transfer._build_event(e01)

        captured: dict[str, object] = {}
        original_handoff = field_source.handoff_receptor_completion_groups
        original_projection = field_source.project_transient_docks_to_neuron_inputs

        def observe_handoff(sequences, steps):
            captured["sequences"] = sequences
            captured["steps"] = steps
            return original_handoff(sequences, steps)

        def observe_projection(trajectory, docks):
            projected = original_projection(trajectory, docks)
            captured["projected"] = projected
            return projected

        with (
            patch.object(
                field_source,
                "handoff_receptor_completion_groups",
                side_effect=observe_handoff,
            ),
            patch.object(
                field_source,
                "project_transient_docks_to_neuron_inputs",
                side_effect=observe_projection,
            ),
        ):
            branch = field_source.build_s2lo_field_adapter(
                field_clock_id=transfer.FIELD_CLOCK_ID
            )(initial, event)

        sequences = captured["sequences"]
        steps = captured["steps"]
        projected = captured["projected"]
        self.assertEqual(2, len(sequences))
        self.assertTrue(
            all(sequence.clock_id == transfer.FIELD_CLOCK_ID for sequence in sequences)
        )
        self.assertEqual(1, len(steps))
        self.assertEqual(
            (
                transfer.FIELD_CLOCK_ID,
                field_input.start_tick,
                field_input.end_tick,
            ),
            (steps[0].clock_id, steps[0].start_tick, steps[0].end_tick),
        )
        self.assertEqual((336, 336), (projected.contact_count, len(projected.neuron_inputs)))

        self.assertEqual("FIELD", branch.branch)
        self.assertEqual(("COMPLETED", 1), (branch.poststate.phase, branch.poststate.step_count))
        self.assertEqual(field_input.end_tick, branch.poststate.last_end_tick)
        distribution_time = branch.poststate.field.last_distribution.field_time
        self.assertEqual(
            (
                transfer.FIELD_CLOCK_ID,
                field_input.start_tick,
                field_input.end_tick,
            ),
            (
                distribution_time.clock_id,
                distribution_time.window_start_tick,
                distribution_time.window_end_tick,
            ),
        )

        self.assertEqual((), branch.poststate.field.last_distribution.contacts)
        self.assertNotEqual(initial.state_digest, branch.poststate.state_digest)


if __name__ == "__main__":
    unittest.main()
