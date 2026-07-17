from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    BEFUND_035_DIGEST,
    CommonFieldTime,
    MCMFieldPerception,
    MCMNeuron,
    MCMNeuronLayer,
    MCMNeuronLayerError,
    PeriodicLayerAxisProbeError,
    PeriodicSamplingAxis,
    ReceptorContactFrame,
    periodic_layer_axis_public_roles,
    receptor_projection_baseline,
    run_periodic_layer_axis_probe,
    run_periodic_sampling_probe,
)
from mcm_field_organism.sensor_mcm_field import (
    build_receptor_aligned_mcm_field,
)


def small_layer(
    positions: tuple[int, ...],
    *,
    axes: tuple[PeriodicSamplingAxis, ...] = (),
) -> MCMNeuronLayer:
    return MCMNeuronLayer(
        layer_id="test.axis.layer",
        neurons=tuple(
            MCMNeuron(
                neuron_id=f"test.axis.n{position}",
                field_id="test.axis",
                modality_id="simulated.contact",
                geometry_id="test.axis.geometry.v1",
                position=(position,),
                activation=float(position) / max(1, len(positions) - 1),
                afterimage=0.0,
                perception=MCMFieldPerception(
                    tick=0,
                    receptor_contact=0.0,
                    local_samples=(),
                ),
            )
            for position in positions
        ),
        sample_offsets=((-1,), (1,)),
        periodic_axes=axes,
    )


class PeriodicLayerAxisProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = run_periodic_layer_axis_probe()

    def test_complete_preregistered_families_are_present(self) -> None:
        result = self.result
        self.assertEqual(7, len(result.targets))
        self.assertEqual(42, len(result.world_observations))
        self.assertEqual(21, len(result.cause_pairs))
        self.assertEqual(14, len(result.transformations))

    def test_legacy_open_digest_and_behavior_remain_unchanged(self) -> None:
        result = self.result
        self.assertTrue(result.legacy_digest_unchanged)
        self.assertTrue(result.explicit_open_equals_legacy)
        self.assertEqual(BEFUND_035_DIGEST, run_periodic_sampling_probe().digest())

    def test_runtime_matches_isolated_reference_with_two_wrap_samples(self) -> None:
        result = self.result
        self.assertTrue(result.runtime_matches_reference)
        self.assertTrue(result.exactly_two_wrap_samples)
        self.assertTrue(result.interior_runtime_unchanged)
        self.assertEqual(
            {0: 1, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1},
            {item.target_position: item.added_wrap_samples for item in result.targets},
        )

    def test_baselines_keep_fast_state_equal(self) -> None:
        result = self.result
        self.assertTrue(result.hold_baseline_fast_state_equal)
        self.assertTrue(result.receptor_baseline_fast_state_equal)

    def test_all_world_branches_and_cause_pairs_match(self) -> None:
        result = self.result
        self.assertTrue(result.all_world_branches_match_reference)
        self.assertTrue(result.all_cause_pairs_collapse)
        self.assertTrue(all(item.runtime_matches_reference for item in result.world_observations))
        self.assertTrue(
            all(
                pair.provenance_distinct and pair.runtime_sampling_equal
                for pair in result.cause_pairs
            )
        )

    def test_all_rotations_and_reflections_are_equivariant(self) -> None:
        result = self.result
        self.assertTrue(result.all_transformations_equivariant)
        self.assertEqual(
            {(rotation, orientation) for rotation in range(7) for orientation in (-1, 1)},
            {(item.rotation, item.orientation) for item in result.transformations},
        )

    def test_negative_axis_families_are_rejected(self) -> None:
        result = self.result
        self.assertTrue(result.negative_families_rejected)
        invalid_axes = (
            lambda: PeriodicSamplingAxis(True, 0, 7),
            lambda: PeriodicSamplingAxis(0, False, 7),
            lambda: PeriodicSamplingAxis(0, 0, True),
            lambda: PeriodicSamplingAxis(0, 0, 1),
        )
        for call in invalid_axes:
            with self.assertRaises(MCMNeuronLayerError):
                call()
        with self.assertRaisesRegex(MCMNeuronLayerError, "alias"):
            small_layer(
                (0, 1),
                axes=(PeriodicSamplingAxis(0, 0, 2),),
            )

    def test_axis_anatomy_is_preserved_and_failure_is_atomic(self) -> None:
        result = self.result
        self.assertTrue(result.anatomy_preserved_on_advance)
        self.assertTrue(result.atomic_failure_preserves_source)

    def test_sensor_field_builder_passes_only_explicit_periodic_anatomy(self) -> None:
        frame = ReceptorContactFrame(
            modality_id="simulated.contact",
            geometry_id="simulated.ring7.receptor.v1",
            snapshot_id="simulated.receptor.tick.0",
            clock_id="simulated.world",
            window_start_tick=0,
            window_end_tick=1,
            carrier_ids=tuple(f"contact.p{position}" for position in range(7)),
            values=(1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        )
        axis = PeriodicSamplingAxis(0, 0, 7)
        field = build_receptor_aligned_mcm_field(
            frame,
            positions=tuple((position,) for position in range(7)),
            sample_offsets=((-1,), (1,)),
            dock_id="simulated",
            layer_id="simulated.layer",
            field_id="simulated.field",
            field_geometry_id="simulated.field.ring7.v1",
            periodic_axes=(axis,),
        )
        self.assertEqual((axis,), field.layer.periodic_axes)
        advanced = field.advance(
            frame,
            CommonFieldTime(
                clock_id="organism.simulated",
                window_start_tick=0,
                window_end_tick=1,
            ),
            receptor_projection_baseline,
        )
        self.assertEqual((axis,), advanced.layer.periodic_axes)

    def test_independent_periodic_axis_order_is_canonical(self) -> None:
        neurons = tuple(
            MCMNeuron(
                neuron_id=f"grid.n{x}.{y}",
                field_id="grid.field",
                modality_id="grid",
                geometry_id="grid.torus3.v1",
                position=(x, y),
                activation=0.0,
                afterimage=0.0,
                perception=MCMFieldPerception(
                    tick=0,
                    receptor_contact=None,
                    local_samples=(),
                ),
            )
            for x in range(3)
            for y in range(3)
        )
        x_axis = PeriodicSamplingAxis(0, 0, 3)
        y_axis = PeriodicSamplingAxis(1, 0, 3)
        first = MCMNeuronLayer(
            layer_id="grid.layer",
            neurons=neurons,
            sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
            periodic_axes=(x_axis, y_axis),
        )
        reversed_axes = MCMNeuronLayer(
            layer_id="grid.layer",
            neurons=tuple(reversed(neurons)),
            sample_offsets=((1, 0), (0, 1), (0, -1), (-1, 0)),
            periodic_axes=(y_axis, x_axis),
        )
        self.assertEqual(first, reversed_axes)
        self.assertEqual(first.digest(), reversed_axes.digest())

    def test_observer_order_and_repetition_are_neutral(self) -> None:
        observed = []
        reference = run_periodic_layer_axis_probe()
        permuted = run_periodic_layer_axis_probe(
            reverse_neurons=True,
            reverse_offsets=True,
            observer=observed.append,
        )
        self.assertEqual(reference, permuted)
        self.assertEqual(reference.digest(), permuted.digest())
        self.assertTrue(permuted.observer_is_neutral)
        self.assertTrue(permuted.order_is_neutral)
        self.assertTrue(permuted.repeated_run_is_neutral)
        self.assertEqual(7, len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].target_position = 1  # type: ignore[misc]

    def test_result_cannot_claim_world_activation_relationship_or_rule(self) -> None:
        result = self.result
        self.assertFalse(result.productive_world_path_activated)
        self.assertFalse(result.stores_relationships)
        self.assertFalse(result.releases_field_rule)
        with self.assertRaises(PeriodicLayerAxisProbeError):
            replace(result, productive_world_path_activated=True)
        with self.assertRaises(PeriodicLayerAxisProbeError):
            replace(result, stores_relationships=True)
        with self.assertRaises(PeriodicLayerAxisProbeError):
            replace(result, releases_field_rule=True)

    def test_axis_public_roles_are_strictly_technical(self) -> None:
        self.assertEqual(
            ("axis_index", "origin", "size"),
            periodic_layer_axis_public_roles()[0],
        )
        forbidden = {
            "activation",
            "afterimage",
            "weight",
            "continuity",
            "cause",
            "delta",
            "reward",
            "semantic_label",
            "effector",
        }
        self.assertTrue(
            forbidden.isdisjoint(periodic_layer_axis_public_roles()[0])
        )


if __name__ == "__main__":
    unittest.main()
