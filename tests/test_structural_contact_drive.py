from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    StructuralContactDriveError,
    build_neutral_contact_material_layer,
    build_shared_mcm_field,
    map_structural_contact_drives,
    receptor_projection_baseline,
    structural_contact_drive_public_roles,
)


class StructuralContactDriveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.geometry_id = "auditory.contact.drive.v1"
        cls.clock_id = "organism.contact.drive"
        cls.carrier_ids = (
            "auditory.carrier.0",
            "auditory.carrier.1",
            "auditory.carrier.2",
        )
        reference = cls._frame("reference", (0.0, 0.0, 0.0), 0, 1)
        initial = build_shared_mcm_field(
            (reference,),
            {
                "auditory": ReceptorDockAnatomy(
                    "auditory",
                    "dock.auditory",
                    ((0,), (1,), (2,)),
                )
            },
            sample_offsets=((-1,), (1,)),
        )
        distributor = ReceptorDistributor()
        distributor.attach(
            ReceptorDock("dock.auditory", "auditory", cls.geometry_id)
        )
        seeded = initial.advance(
            distributor.distribute(
                (cls._frame("seed", (0.8, 0.0, -0.4), 0, 1),),
                CommonFieldTime(cls.clock_id, 0, 1),
            ),
            receptor_projection_baseline,
        )
        driven = seeded.advance(
            distributor.distribute(
                (cls._frame("drive", (0.0, 0.0, 0.0), 1, 2),),
                CommonFieldTime(cls.clock_id, 1, 2),
            ),
            receptor_projection_baseline,
        )
        cls.seeded = seeded
        cls.driven = driven
        cls.material = build_neutral_contact_material_layer(
            seeded.layer,
            material_per_neuron=1.0,
        )
        cls.source_digest = seeded.layer.digest()
        cls.material_digest = cls.material.digest()
        cls.drive_map = map_structural_contact_drives(
            cls.material,
            seeded.layer,
            driven.layer,
            response_time_seconds=1.0,
        )

    @classmethod
    def _frame(
        cls,
        snapshot_id: str,
        values: tuple[float, ...],
        start_tick: int,
        end_tick: int,
    ) -> ReceptorContactFrame:
        return ReceptorContactFrame(
            "auditory",
            cls.geometry_id,
            snapshot_id,
            "auditory.source",
            start_tick,
            end_tick,
            cls.carrier_ids,
            values,
        )

    def test_every_neutral_surface_receives_only_aligned_existing_causes(self) -> None:
        self.assertEqual(6, self.drive_map.surface_count)
        self.assertEqual(4, self.drive_map.locally_sampled_surface_count)
        middle = next(
            item
            for item in self.drive_map.neurons
            if item.owner_position == (1,)
        )
        by_direction = {
            item.relative_position: item for item in middle.surfaces
        }
        self.assertEqual(0.8, by_direction[(-1,)].local_activation)
        self.assertEqual(0.8, by_direction[(-1,)].signed_field_flow)
        self.assertEqual(-0.4, by_direction[(1,)].local_activation)
        self.assertEqual(-0.4, by_direction[(1,)].signed_field_flow)

    def test_receptor_contact_remains_owner_local_not_surface_selected(self) -> None:
        self.assertTrue(
            all(item.receptor_contact == 0.0 for item in self.drive_map.neurons)
        )
        surface_roles = set(structural_contact_drive_public_roles())
        self.assertNotIn("surface_receptor_contact", surface_roles)
        self.assertNotIn("selected_surface", surface_roles)

    def test_mapping_changes_neither_field_nor_material(self) -> None:
        self.assertEqual(self.source_digest, self.seeded.layer.digest())
        self.assertEqual(self.material_digest, self.material.digest())
        repeated = map_structural_contact_drives(
            self.material,
            self.seeded.layer,
            self.driven.layer,
            response_time_seconds=1.0,
        )
        self.assertEqual(self.drive_map, repeated)
        self.assertEqual(self.drive_map.digest(), repeated.digest())

    def test_no_memory_relation_or_material_writer_role_is_introduced(self) -> None:
        forbidden = {
            "relation_id",
            "partner_id",
            "weight",
            "memory",
            "history",
            "winner",
            "meaning",
            "reward",
            "material_delta",
            "surface_material",
            "write_rate",
            "growth_rate",
        }
        self.assertTrue(
            forbidden.isdisjoint(structural_contact_drive_public_roles())
        )
        self.assertFalse(hasattr(self.drive_map, "advance"))
        self.assertFalse(hasattr(self.drive_map, "write"))

    def test_anatomy_from_another_tick_is_rejected(self) -> None:
        stale = build_neutral_contact_material_layer(
            self.driven.layer,
            material_per_neuron=1.0,
        )
        with self.assertRaises(StructuralContactDriveError):
            map_structural_contact_drives(
                stale,
                self.seeded.layer,
                self.driven.layer,
                response_time_seconds=1.0,
            )


if __name__ == "__main__":
    unittest.main()
