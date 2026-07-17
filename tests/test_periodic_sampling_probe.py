from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import unittest

from mcm_field_organism import (
    MCMFieldPerception,
    MCMNeuron,
    MCMNeuronLayer,
    PeriodicSamplingProbeError,
    RING_OFFSETS,
    WORLD_POSITIONS,
    periodic_reference_perceptions,
    periodic_sampling_public_roles,
    run_periodic_sampling_probe,
)


def ring_layer(size: int) -> MCMNeuronLayer:
    return MCMNeuronLayer(
        layer_id="test.periodic.layer",
        neurons=tuple(
            MCMNeuron(
                neuron_id=f"test.periodic.n{position}",
                field_id="test.periodic",
                modality_id="simulated.contact",
                geometry_id=f"test.periodic.ring{size}.v1",
                position=(position,),
                activation=float(position) / max(1, size - 1),
                afterimage=0.0,
                perception=MCMFieldPerception(
                    tick=0,
                    receptor_contact=0.0,
                    local_samples=(),
                ),
            )
            for position in range(size)
        ),
        sample_offsets=RING_OFFSETS,
    )


class PeriodicSamplingProbeTests(unittest.TestCase):
    def test_complete_preregistered_families_are_present(self) -> None:
        result = run_periodic_sampling_probe()
        self.assertEqual(7, len(result.comparisons))
        self.assertEqual(42, len(result.world_observations))
        self.assertEqual(21, len(result.cause_pairs))
        self.assertEqual(14, len(result.transformations))

    def test_exactly_the_two_preregistered_wrap_samples_are_added(self) -> None:
        result = run_periodic_sampling_probe()
        self.assertTrue(result.open_reference_exact)
        self.assertTrue(result.exactly_two_wrap_samples)
        self.assertTrue(result.interior_samples_equal)
        self.assertTrue(result.wrap_payload_exact)
        added = {
            (
                sample.target_position,
                sample.offset,
                sample.source_position,
            )
            for comparison in result.comparisons
            for sample in comparison.added_samples
        }
        self.assertEqual({(0, -1, 6), (6, 1, 0)}, added)

    def test_wrap_samples_preserve_source_payload_exactly(self) -> None:
        result = run_periodic_sampling_probe()
        by_target = {item.target_position: item for item in result.comparisons}
        left = by_target[0].added_samples[0]
        right = by_target[6].added_samples[0]
        self.assertEqual(
            (6, "signature.n6", 0.6, 0.0),
            (
                left.source_position,
                left.source_neuron_id,
                left.activation,
                left.afterimage,
            ),
        )
        self.assertEqual(
            (0, "signature.n0", 0.0, 0.6),
            (
                right.source_position,
                right.source_neuron_id,
                right.activation,
                right.afterimage,
            ),
        )

    def test_all_rotations_and_reflections_are_equivariant(self) -> None:
        result = run_periodic_sampling_probe()
        self.assertTrue(result.all_transformations_equivariant)
        self.assertEqual(
            {(rotation, orientation) for rotation in range(7) for orientation in (-1, 1)},
            {
                (item.rotation, item.orientation)
                for item in result.transformations
            },
        )
        self.assertTrue(all(item.equals_reference for item in result.transformations))

    def test_ambiguous_small_periodic_geometry_is_rejected(self) -> None:
        result = run_periodic_sampling_probe()
        self.assertTrue(result.ambiguous_geometry_rejected)
        layer = ring_layer(2)
        contacts = {neuron.neuron_id: 0.0 for neuron in layer.neurons}
        with self.assertRaisesRegex(PeriodicSamplingProbeError, "alias"):
            periodic_reference_perceptions(layer, contacts, axis_size=2)

    def test_all_world_cause_pairs_collapse_after_provenance(self) -> None:
        result = run_periodic_sampling_probe()
        self.assertTrue(result.all_cause_pairs_collapse)
        for pair in result.cause_pairs:
            self.assertTrue(pair.provenance_distinct)
            self.assertTrue(pair.open_sampling_equal)
            self.assertTrue(pair.periodic_sampling_equal)

    def test_existing_baselines_keep_fast_state_equal(self) -> None:
        result = run_periodic_sampling_probe()
        self.assertTrue(result.hold_baseline_fast_state_equal)
        self.assertTrue(result.receptor_baseline_fast_state_equal)
        self.assertTrue(result.source_layer_immutable)

    def test_observer_order_and_repetition_are_neutral(self) -> None:
        observed = []
        reference = run_periodic_sampling_probe()
        permuted = run_periodic_sampling_probe(
            target_order=reversed(WORLD_POSITIONS),
            offset_order=reversed(RING_OFFSETS),
            observer=observed.append,
        )
        self.assertEqual(reference, permuted)
        self.assertEqual(reference.digest(), permuted.digest())
        self.assertTrue(permuted.observer_is_neutral)
        self.assertTrue(permuted.order_is_neutral)
        self.assertTrue(permuted.repeated_run_is_neutral)
        self.assertEqual(7, len(observed))
        with self.assertRaises(FrozenInstanceError):
            observed[0].target_position = 3  # type: ignore[misc]

    def test_invalid_reference_inputs_are_rejected(self) -> None:
        layer = ring_layer(7)
        contacts = {neuron.neuron_id: 0.0 for neuron in layer.neurons}
        invalid_calls = (
            lambda: periodic_reference_perceptions(
                object(), contacts, axis_size=7  # type: ignore[arg-type]
            ),
            lambda: periodic_reference_perceptions(layer, contacts, axis_size=True),
            lambda: periodic_reference_perceptions(layer, contacts, axis_size=6),
            lambda: periodic_reference_perceptions(
                layer, {}, axis_size=7
            ),
            lambda: run_periodic_sampling_probe(target_order=(0, 1)),
            lambda: run_periodic_sampling_probe(offset_order=((-1,), (-1,))),
        )
        for call in invalid_calls:
            with self.assertRaises(PeriodicSamplingProbeError):
                call()

    def test_result_cannot_claim_runtime_relationship_or_field_rule(self) -> None:
        result = run_periodic_sampling_probe()
        self.assertFalse(result.writes_runtime)
        self.assertFalse(result.stores_relationships)
        self.assertFalse(result.releases_field_rule)
        with self.assertRaises(PeriodicSamplingProbeError):
            replace(result, writes_runtime=True)
        with self.assertRaises(PeriodicSamplingProbeError):
            replace(result, stores_relationships=True)
        with self.assertRaises(PeriodicSamplingProbeError):
            replace(result, releases_field_rule=True)

    def test_periodic_sample_roles_contain_no_cause_action_or_semantics(self) -> None:
        sample_roles = set(periodic_sampling_public_roles()[0])
        forbidden = {
            "cause",
            "delta",
            "effort",
            "provenance_digest",
            "action",
            "reward",
            "winner",
            "semantic_label",
            "weight",
            "continuity",
            "relationship",
        }
        self.assertTrue(forbidden.isdisjoint(sample_roles))


if __name__ == "__main__":
    unittest.main()
