from __future__ import annotations

import inspect
import unittest

from mcm_field_organism import (
    LocalContactSurface,
    NeuronContactMaterialState,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    RadialContactMorphologyError,
    build_neutral_contact_material_layer,
    build_neutral_radial_contact_morphology,
    controlled_reentry_world_family,
    radial_contact_morphology_public_roles,
    run_controlled_test_world,
)


class RadialContactMorphologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        world, _ = controlled_reentry_world_family()
        cls.field = run_controlled_test_world(
            world,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        ).field_run.field
        cls.field_digest = cls.field.snapshot().digest()
        cls.contact_material = build_neutral_contact_material_layer(
            cls.field.layer,
            material_per_neuron=1.0,
        )
        cls.contact_digest = cls.contact_material.digest()
        cls.radial = build_neutral_radial_contact_morphology(
            cls.contact_material,
            radial_edges=(0.0, 0.25, 0.5, 0.75, 1.0),
        )

    def test_real_anatomy_expands_to_empty_owner_local_profiles(self) -> None:
        self.assertEqual(84, len(self.radial.substrates))
        self.assertEqual(336, self.radial.profile_count)
        self.assertEqual(1344, self.radial.radial_cell_count)
        self.assertTrue(self.radial.is_neutral)
        self.assertFalse(self.radial.has_boundary_material)
        self.assertTrue(
            all(
                item.unbound_material == item.total_material == 1.0
                for item in self.radial.substrates
            )
        )

    def test_profile_geometry_is_shared_explicit_and_direction_neutral(self) -> None:
        expected = ((0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.0))
        for item in self.radial.substrates:
            by_direction = {
                profile.relative_position: profile for profile in item.profiles
            }
            self.assertEqual(
                {(-1, 0), (0, -1), (0, 1), (1, 0)},
                set(by_direction),
            )
            for profile in by_direction.values():
                self.assertEqual(
                    expected,
                    tuple((cell.q_start, cell.q_end) for cell in profile.cells),
                )
                self.assertEqual(0.0, profile.material_amount)
                self.assertEqual(0.0, profile.boundary_material)

    def test_old_surface_balance_is_exactly_reconstructed_at_zero(self) -> None:
        old_by_owner = {
            item.owner_neuron_id: item for item in self.contact_material.substrates
        }
        for item in self.radial.substrates:
            old_surfaces = {
                surface.relative_position: surface.surface_material
                for surface in old_by_owner[item.owner_neuron_id].surfaces
            }
            radial_totals = {
                profile.relative_position: profile.material_amount
                for profile in item.profiles
            }
            self.assertEqual(old_surfaces, radial_totals)

    def test_build_is_passive_reproducible_and_snapshotable(self) -> None:
        repeated = build_neutral_radial_contact_morphology(
            self.contact_material,
            radial_edges=(0.0, 0.25, 0.5, 0.75, 1.0),
        )
        self.assertEqual(self.radial, repeated)
        self.assertEqual(self.radial.digest(), repeated.digest())
        self.assertEqual(self.contact_digest, self.contact_material.digest())
        self.assertEqual(self.field_digest, self.field.snapshot().digest())

    def test_radial_resolution_has_no_hidden_default(self) -> None:
        parameter = inspect.signature(
            build_neutral_radial_contact_morphology
        ).parameters["radial_edges"]
        self.assertIs(parameter.default, inspect.Parameter.empty)

    def test_invalid_or_non_neutral_source_is_rejected(self) -> None:
        with self.assertRaises(RadialContactMorphologyError):
            build_neutral_radial_contact_morphology(
                self.contact_material,
                radial_edges=(0.0, 0.5, 0.5, 1.0),
            )
        original = self.contact_material.substrates[0]
        changed = NeuronContactMaterialState(
            original.owner_neuron_id,
            original.geometry_id,
            original.owner_position,
            original.field_tick,
            original.total_material,
            0.9,
            tuple(
                LocalContactSurface(
                    surface.relative_position,
                    0.1 if index == 0 else 0.0,
                )
                for index, surface in enumerate(original.surfaces)
            ),
        )
        non_neutral = type(self.contact_material)(
            self.contact_material.source_layer_id,
            self.contact_material.geometry_id,
            self.contact_material.field_tick,
            (changed,) + self.contact_material.substrates[1:],
        )
        with self.assertRaises(RadialContactMorphologyError):
            build_neutral_radial_contact_morphology(
                non_neutral,
                radial_edges=(0.0, 0.5, 1.0),
            )

    def test_public_roles_contain_no_particle_relation_or_dynamics(self) -> None:
        forbidden = {
            "particle_id",
            "partner_id",
            "relation_id",
            "weight",
            "growth_rate",
            "transport_rate",
            "field_effect",
            "meaning",
            "winner",
        }
        self.assertTrue(
            forbidden.isdisjoint(radial_contact_morphology_public_roles())
        )
        self.assertFalse(hasattr(self.radial, "advance"))
        self.assertFalse(hasattr(self.radial, "contact_effect"))


if __name__ == "__main__":
    unittest.main()
