from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from mcm_field_organism import (
    ContactMaterialLayerState,
    LocalContactSurface,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    NeuronContactMaterialState,
    StructuralContactSubstrateError,
    build_neutral_contact_material_layer,
    controlled_reentry_world_family,
    run_controlled_test_world,
    structural_contact_substrate_public_roles,
)


class StructuralContactSubstrateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        world, _ = controlled_reentry_world_family()
        cls.field = run_controlled_test_world(
            world,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        ).field_run.field
        cls.before_digest = cls.field.snapshot().digest()
        cls.state = build_neutral_contact_material_layer(
            cls.field.layer,
            material_per_neuron=1.0,
        )

    def test_real_shared_field_builds_owner_local_neutral_anatomy(self) -> None:
        self.assertEqual(84, len(self.state.substrates))
        self.assertEqual(336, self.state.surface_slot_count)
        self.assertTrue(self.state.is_neutral)
        self.assertTrue(
            all(item.unbound_material == 1.0 for item in self.state.substrates)
        )
        self.assertTrue(
            all(
                surface.surface_material == 0.0
                for item in self.state.substrates
                for surface in item.surfaces
            )
        )

    def test_anatomy_does_not_construct_the_old_relation_set(self) -> None:
        roles = set(structural_contact_substrate_public_roles())
        forbidden = {
            "relation_id",
            "partner_id",
            "source_neuron_id",
            "target_neuron_id",
            "weight",
            "coupling",
            "winner",
            "meaning",
            "reward",
            "target_topology",
        }
        self.assertTrue(forbidden.isdisjoint(roles))
        self.assertFalse(hasattr(self.state, "relations"))
        self.assertFalse(hasattr(self.state, "edges"))

    def test_neutral_contract_has_no_transition_or_field_effect(self) -> None:
        self.assertFalse(hasattr(self.state, "advance"))
        self.assertFalse(hasattr(self.state, "field_effect"))
        self.assertFalse(hasattr(self.state, "couple"))

    def test_build_is_passive_reproducible_and_ordered(self) -> None:
        repeated = build_neutral_contact_material_layer(
            self.field.layer,
            material_per_neuron=1.0,
        )
        self.assertEqual(self.state, repeated)
        self.assertEqual(self.state.digest(), repeated.digest())
        self.assertEqual(self.before_digest, self.field.snapshot().digest())

    def test_material_conservation_is_required(self) -> None:
        with self.assertRaises(StructuralContactSubstrateError):
            NeuronContactMaterialState(
                owner_neuron_id="n.one",
                geometry_id="geometry.one",
                owner_position=(0, 0),
                field_tick=0,
                total_material=1.0,
                unbound_material=0.75,
                surfaces=(
                    LocalContactSurface((-1, 0), 0.1),
                    LocalContactSurface((1, 0), 0.1),
                ),
            )

    def test_surface_directions_must_be_local_unique_and_dimension_matched(self) -> None:
        with self.assertRaises(StructuralContactSubstrateError):
            LocalContactSurface((0, 0), 0.0)
        with self.assertRaises(StructuralContactSubstrateError):
            NeuronContactMaterialState(
                owner_neuron_id="n.one",
                geometry_id="geometry.one",
                owner_position=(0, 0),
                field_tick=0,
                total_material=1.0,
                unbound_material=1.0,
                surfaces=(
                    LocalContactSurface((-1,), 0.0),
                    LocalContactSurface((1,), 0.0),
                ),
            )
        with self.assertRaises(StructuralContactSubstrateError):
            NeuronContactMaterialState(
                owner_neuron_id="n.one",
                geometry_id="geometry.one",
                owner_position=(0,),
                field_tick=0,
                total_material=1.0,
                unbound_material=1.0,
                surfaces=(
                    LocalContactSurface((-1,), 0.0),
                    LocalContactSurface((-1,), 0.0),
                ),
            )

    def test_snapshot_is_immutable(self) -> None:
        with self.assertRaises(FrozenInstanceError):
            self.state.field_tick = 9  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            self.state.substrates[0].unbound_material = 0.0  # type: ignore[misc]

    def test_layer_rejects_mixed_surface_anatomy(self) -> None:
        first = NeuronContactMaterialState(
            "n.one",
            "geometry.one",
            (0, 0),
            0,
            1.0,
            1.0,
            (
                LocalContactSurface((-1, 0), 0.0),
                LocalContactSurface((1, 0), 0.0),
            ),
        )
        second = NeuronContactMaterialState(
            "n.two",
            "geometry.one",
            (1, 0),
            0,
            1.0,
            1.0,
            (
                LocalContactSurface((0, -1), 0.0),
                LocalContactSurface((0, 1), 0.0),
            ),
        )
        with self.assertRaises(StructuralContactSubstrateError):
            ContactMaterialLayerState(
                "layer.one",
                "geometry.one",
                0,
                (first, second),
            )


if __name__ == "__main__":
    unittest.main()
