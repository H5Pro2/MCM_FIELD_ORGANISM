from __future__ import annotations

from dataclasses import fields
import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMNeuronDrive,
    MCMNeuronOutput,
    VisualGridConfig,
    VisualMCMInterfaceError,
    VisualReceptorContact,
    build_visual_mcm_interface,
    receptor_projection_baseline,
    visual_mcm_interface_public_roles,
)


class VisualMCMInterfaceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = VisualGridConfig(
            source_width=6,
            source_height=6,
            grid_columns=3,
            grid_rows=3,
            frames_per_second=10.0,
        )

    def field_time(self, index: int) -> CommonFieldTime:
        return CommonFieldTime("organism.test", index * 100, (index + 1) * 100)

    def test_one_frame_crosses_receptor_and_field_boundary_losslessly(self) -> None:
        frame = np.zeros((6, 6, 3), dtype=np.uint8)
        frame[2:4, 2:4, 1] = 255
        interface = build_visual_mcm_interface(self.config)
        next_interface, output = interface.advance(
            frame, self.field_time(0), receptor_projection_baseline
        )
        self.assertEqual(0, output.frame_index)
        self.assertEqual(VisualReceptorContact.ACTIVE_LIGHT, output.receptor_contact)
        self.assertEqual(27, len(output.field_window.carrier_ids))
        activation = dict(zip(
            output.field_window.carrier_ids,
            output.field_window.activation,
            strict=True,
        ))
        self.assertEqual(1.0, activation["field.visual.n13"])
        self.assertEqual(1, sum(value != 0.0 for value in output.field_window.activation))
        self.assertEqual((0.0,) * 27, output.field_window.afterimage)
        self.assertIsNone(interface.current_field)
        self.assertEqual(1, next_interface.current_field.layer.tick)

    def test_raw_frame_is_not_retained_or_changed(self) -> None:
        frame = np.arange(108, dtype=np.uint8).reshape((6, 6, 3))
        before = frame.copy()
        interface, output = build_visual_mcm_interface(self.config).advance(
            frame, self.field_time(0), receptor_projection_baseline
        )
        self.assertTrue(np.array_equal(before, frame))
        self.assertFalse(any(
            isinstance(getattr(interface, item.name), np.ndarray)
            for item in fields(type(interface))
        ))
        self.assertFalse(any(
            isinstance(getattr(output, item.name), np.ndarray)
            for item in fields(type(output))
        ))
        self.assertNotIn("frame", type(output).__dataclass_fields__)
        self.assertEqual(27, len(output.field_window.activation))

    def test_field_time_and_frame_index_advance_without_hidden_skips(self) -> None:
        zero = np.zeros((6, 6, 3), dtype=np.uint8)
        interface = build_visual_mcm_interface(self.config)
        interface, first = interface.advance(zero, self.field_time(0), receptor_projection_baseline)
        interface, second = interface.advance(zero, self.field_time(1), receptor_projection_baseline)
        self.assertEqual((0, 1), (first.frame_index, second.frame_index))
        self.assertEqual(2, interface.next_frame_index)
        self.assertEqual(2, interface.current_field.layer.tick)
        self.assertEqual((100, 200), (second.field_window.window_start_tick, second.field_window.window_end_tick))
        with self.assertRaises(VisualMCMInterfaceError):
            interface.advance(zero, self.field_time(1), receptor_projection_baseline)

    def test_local_samples_preserve_spatial_neighbors_and_channel_identity(self) -> None:
        first_frame = np.zeros((6, 6, 3), dtype=np.uint8)
        first_frame[0:2, 2:4, 0] = 255
        first_frame[2:4, 0:2, 0] = 128
        first_frame[2:4, 4:6, 0] = 64
        first_frame[4:6, 2:4, 0] = 32
        interface, _ = build_visual_mcm_interface(self.config).advance(
            first_frame, self.field_time(0), receptor_projection_baseline
        )
        observed: dict[str, MCMNeuronDrive] = {}

        def transition(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            observed[drive.previous.neuron_id] = drive
            return receptor_projection_baseline(drive)

        interface, _ = interface.advance(
            np.zeros((6, 6, 3), dtype=np.uint8),
            self.field_time(1),
            transition,
        )
        center = observed["field.visual.n12"]
        self.assertEqual(
            {(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0)},
            {sample.relative_position for sample in center.perception.local_samples},
        )
        self.assertEqual(4, len(center.perception.local_samples))
        self.assertTrue(all(sample.activation > 0.0 for sample in center.perception.local_samples))

    def test_transition_is_explicit_and_can_observe_prior_local_field(self) -> None:
        interface = build_visual_mcm_interface(self.config)
        with self.assertRaises(TypeError):
            interface.advance(np.zeros((6, 6, 3), dtype=np.uint8), self.field_time(0))

    def test_invalid_offsets_and_incompatible_time_are_rejected(self) -> None:
        with self.assertRaises(VisualMCMInterfaceError):
            build_visual_mcm_interface(self.config, sample_offsets=((1, 0, 0),))
        interface = build_visual_mcm_interface(self.config)
        with self.assertRaises(VisualMCMInterfaceError):
            interface.advance(np.zeros((6, 6, 3), dtype=np.uint8), object(), receptor_projection_baseline)
        with self.assertRaises(VisualMCMInterfaceError):
            interface.advance(np.zeros((2, 2, 3), dtype=np.uint8), self.field_time(0), receptor_projection_baseline)

    def test_public_roles_exclude_raw_content_and_semantics(self) -> None:
        roles = set(visual_mcm_interface_public_roles())
        forbidden = {
            "frame", "image", "pixels", "raw_video", "object", "person",
            "scene", "label", "meaning", "class_id", "attention", "memory",
            "pattern_id", "reward",
        }
        self.assertTrue(forbidden.isdisjoint(roles))
        self.assertNotIn("transition", roles)


if __name__ == "__main__":
    unittest.main()
