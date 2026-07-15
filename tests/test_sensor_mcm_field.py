from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    MCMDock,
    MCMDistributor,
    MCMFieldPerception,
    MCMNeuron,
    MCMNeuronDrive,
    MCMNeuronLayer,
    MCMNeuronOutput,
    ReceptorContactFrame,
    ReceptorNeuronDockMap,
    SensorMCMField,
    SensorMCMFieldError,
    build_receptor_aligned_mcm_field,
    receptor_projection_baseline,
    sensor_mcm_field_public_roles,
)


def frame(
    values: tuple[float, ...] = (0.2, 0.4, 0.6),
    *,
    snapshot: int = 0,
    carriers: tuple[str, ...] = ("band.low", "band.mid", "band.high"),
) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="auditory",
        geometry_id="auditory.test.v1",
        snapshot_id=f"auditory.receptor.{snapshot}",
        clock_id="audio.sample",
        window_start_tick=snapshot * 10,
        window_end_tick=(snapshot + 1) * 10,
        carrier_ids=carriers,
        values=values,
    )


def field(reference: ReceptorContactFrame | None = None):
    return build_receptor_aligned_mcm_field(
        reference or frame(),
        positions=((0,), (1,), (2,)),
        sample_offsets=((-1,), (1,)),
        dock_id="auditory",
        layer_id="auditory.layer",
        field_id="auditory.field",
        field_geometry_id="auditory.field.line3.v1",
    )


def field_time(snapshot: int = 0) -> CommonFieldTime:
    return CommonFieldTime(
        clock_id="organism.monotonic",
        window_start_tick=snapshot * 100,
        window_end_tick=(snapshot + 1) * 100,
    )


class SensorMCMFieldTests(unittest.TestCase):
    def test_receptor_projection_reaches_completed_field_window_losslessly(self) -> None:
        current = field().advance(frame(), field_time(), receptor_projection_baseline)
        window = current.field_window()
        self.assertEqual((0.2, 0.4, 0.6), window.activation)
        self.assertEqual((0.0, 0.0, 0.0), window.afterimage)
        self.assertEqual("auditory.field.tick.1", window.snapshot_id)
        self.assertEqual(3, len(window.carrier_ids))

    def test_completed_field_window_is_accepted_by_existing_distributor(self) -> None:
        current = field().advance(frame(), field_time(), receptor_projection_baseline)
        distributor = MCMDistributor()
        distributor.attach(current.distributor_dock())
        constellation = distributor.distribute((current.field_window(),))
        self.assertEqual(("auditory",), constellation.modality_ids)
        self.assertEqual(current.field_window().digest(), constellation.states[0].digest())

    def test_local_field_samples_reach_explicit_transition_on_next_frame(self) -> None:
        current = field().advance(frame(), field_time(), receptor_projection_baseline)
        observed: dict[str, MCMNeuronDrive] = {}

        def observer(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            observed[drive.previous.neuron_id] = drive
            return MCMNeuronOutput(
                activation=drive.previous.activation,
                afterimage=drive.previous.afterimage,
            )

        next_field = current.advance(
            frame((0.0, 0.0, 0.0), snapshot=1),
            field_time(1),
            observer,
        )
        center = observed["auditory.field.n1"]
        self.assertEqual((0.2, 0.6), tuple(
            sample.activation for sample in center.perception.local_samples
        ))
        self.assertEqual(2, next_field.layer.tick)

    def test_dock_map_rejects_copy_fusion_and_incomplete_frames(self) -> None:
        with self.assertRaises(SensorMCMFieldError):
            ReceptorNeuronDockMap(
                modality_id="auditory",
                receptor_geometry_id="auditory.test.v1",
                pairs=(("band.low", "n.0"), ("band.low", "n.1")),
            )
        current = field()
        incomplete = frame((0.2, 0.4), carriers=("band.low", "band.mid"))
        with self.assertRaises(SensorMCMFieldError):
            current.advance(incomplete, field_time(), receptor_projection_baseline)

    def test_field_cannot_export_or_attach_before_first_completed_frame(self) -> None:
        current = field()
        with self.assertRaises(SensorMCMFieldError):
            current.field_window()
        with self.assertRaises(SensorMCMFieldError):
            current.distributor_dock()

    def test_reference_frame_defines_anatomy_but_is_not_silently_consumed(self) -> None:
        current = field(frame((0.9, 0.8, 0.7)))
        self.assertEqual(0, current.layer.tick)
        self.assertIsNone(current.last_receptor_frame)
        self.assertIsNone(current.last_field_time)
        self.assertTrue(all(neuron.activation == 0.0 for neuron in current.layer.neurons))

    def test_public_bridge_roles_contain_no_raw_data_or_semantics(self) -> None:
        receptor_roles, field_roles = sensor_mcm_field_public_roles()
        forbidden = {
            "raw_audio",
            "raw_video",
            "samples",
            "frames",
            "meaning",
            "label",
            "reward",
            "weight",
            "memory",
        }
        self.assertTrue(forbidden.isdisjoint(receptor_roles))
        self.assertTrue(forbidden.isdisjoint(field_roles))
        self.assertNotIn("weight", ReceptorNeuronDockMap.__dataclass_fields__)

    def test_distributor_dock_matches_exported_window(self) -> None:
        current = field().advance(frame(), field_time(), receptor_projection_baseline)
        dock = current.distributor_dock()
        window = current.field_window()
        self.assertIsInstance(dock, MCMDock)
        self.assertEqual(
            (dock.dock_id, dock.modality_id, dock.geometry_id, dock.clock_id),
            (window.dock_id, window.modality_id, window.geometry_id, window.clock_id),
        )

    def test_export_uses_common_field_time_not_sensor_specific_clock(self) -> None:
        current = field().advance(frame(), field_time(), receptor_projection_baseline)
        window = current.field_window()
        self.assertEqual("audio.sample", current.last_receptor_frame.clock_id)
        self.assertEqual("organism.monotonic", window.clock_id)
        self.assertEqual((0, 100), (window.window_start_tick, window.window_end_tick))

    def test_common_field_clock_cannot_change_or_move_backwards(self) -> None:
        current = field().advance(frame(), field_time(), receptor_projection_baseline)
        changed_clock = CommonFieldTime("other.clock", 100, 200)
        with self.assertRaises(SensorMCMFieldError):
            current.advance(frame(snapshot=1), changed_clock, receptor_projection_baseline)
        with self.assertRaises(SensorMCMFieldError):
            current.advance(frame(snapshot=1), field_time(), receptor_projection_baseline)

    def test_field_may_contain_internal_neurons_without_receptor_dock(self) -> None:
        docked = MCMNeuron(
            neuron_id="auditory.field.docked",
            field_id="auditory.field",
            modality_id="auditory",
            geometry_id="auditory.field.internal.v1",
            position=(0,),
            activation=0.0,
            afterimage=0.0,
            perception=MCMFieldPerception(0, 0.0, ()),
        )
        internal = MCMNeuron(
            neuron_id="auditory.field.internal",
            field_id="auditory.field",
            modality_id="auditory",
            geometry_id="auditory.field.internal.v1",
            position=(1,),
            activation=0.0,
            afterimage=0.0,
            perception=MCMFieldPerception(0, None, ()),
        )
        layer = MCMNeuronLayer("auditory.layer", (docked, internal), ((-1,), (1,)))
        dock_map = ReceptorNeuronDockMap(
            "auditory",
            "auditory.test.v1",
            (("band.low", "auditory.field.docked"),),
        )
        current = SensorMCMField("auditory", layer, dock_map).advance(
            frame((0.5,), carriers=("band.low",)),
            field_time(),
            receptor_projection_baseline,
        )
        self.assertEqual(2, len(current.field_window().carrier_ids))
        self.assertEqual(0.0, current.layer.neuron("auditory.field.internal").activation)

    def test_different_sensor_clocks_can_share_explicit_common_field_time(self) -> None:
        auditory = field().advance(frame(), field_time(), receptor_projection_baseline)
        visual_frame = ReceptorContactFrame(
            modality_id="visual",
            geometry_id="visual.test.v1",
            snapshot_id="visual.receptor.0",
            clock_id="video.frame",
            window_start_tick=0,
            window_end_tick=1,
            carrier_ids=("pixel.left", "pixel.right"),
            values=(0.3, 0.7),
        )
        visual = build_receptor_aligned_mcm_field(
            visual_frame,
            positions=((0,), (1,)),
            sample_offsets=((-1,), (1,)),
            dock_id="visual",
            layer_id="visual.layer",
            field_id="visual.field",
            field_geometry_id="visual.field.line2.v1",
        ).advance(visual_frame, field_time(), receptor_projection_baseline)
        distributor = MCMDistributor()
        distributor.attach(auditory.distributor_dock())
        distributor.attach(visual.distributor_dock())
        constellation = distributor.distribute(
            (auditory.field_window(), visual.field_window())
        )
        self.assertEqual(("auditory", "visual"), constellation.modality_ids)
        self.assertEqual("organism.monotonic", constellation.clock_id)


if __name__ == "__main__":
    unittest.main()
