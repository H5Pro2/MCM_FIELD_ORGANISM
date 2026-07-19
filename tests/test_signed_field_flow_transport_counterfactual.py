from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    build_neutral_contact_material_layer,
    build_neutral_radial_contact_morphology,
    build_shared_mcm_field,
    compare_signed_field_flow_polarities,
    map_structural_contact_drives,
    propose_signed_field_flow_entry,
    receptor_projection_baseline,
    signed_field_flow_counterfactual_public_roles,
)


class SignedFieldFlowTransportCounterfactualTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        geometry_id = "flow.counterfactual.v1"
        carrier_ids = ("c0", "c1", "c2")

        def frame(snapshot, values, start, end):
            return ReceptorContactFrame(
                "controlled",
                geometry_id,
                snapshot,
                "controlled.source",
                start,
                end,
                carrier_ids,
                values,
            )

        reference = frame("reference", (0.0, 0.0, 0.0), 0, 1)
        initial = build_shared_mcm_field(
            (reference,),
            {
                "controlled": ReceptorDockAnatomy(
                    "controlled",
                    "dock.controlled",
                    ((0,), (1,), (2,)),
                )
            },
            sample_offsets=((-1,), (1,)),
        )
        distributor = ReceptorDistributor()
        distributor.attach(
            ReceptorDock(
                "dock.controlled",
                "controlled",
                geometry_id,
            )
        )
        seeded = initial.advance(
            distributor.distribute(
                (frame("seed", (0.8, 0.0, -0.4), 0, 1),),
                CommonFieldTime("organism.flow", 0, 1),
            ),
            receptor_projection_baseline,
        )
        driven = seeded.advance(
            distributor.distribute(
                (frame("drive", (0.0, 0.0, 0.0), 1, 2),),
                CommonFieldTime("organism.flow", 1, 2),
            ),
            receptor_projection_baseline,
        )
        contact = build_neutral_contact_material_layer(
            seeded.layer,
            material_per_neuron=1.0,
        )
        cls.radial = build_neutral_radial_contact_morphology(
            contact,
            radial_edges=(0.0, 0.25, 0.5, 0.75, 1.0),
        )
        cls.drives = map_structural_contact_drives(
            contact,
            seeded.layer,
            driven.layer,
            response_time_seconds=1.0,
        )

    def test_both_polarity_conventions_are_kinematically_admissible(self) -> None:
        result = compare_signed_field_flow_polarities(
            self.radial,
            self.drives,
            velocity_scale=1.0,
            duration_seconds=0.1,
        )

        self.assertTrue(result.both_kinematically_admissible)
        self.assertTrue(result.aligned.audit.accepted)
        self.assertTrue(result.reversed.audit.accepted)
        self.assertGreater(result.aligned.moved_from_unbound_material, 0.0)
        self.assertGreater(result.reversed.moved_from_unbound_material, 0.0)

    def test_polarity_choice_changes_morphology_but_is_not_field_determined(
        self,
    ) -> None:
        result = compare_signed_field_flow_polarities(
            self.radial,
            self.drives,
            velocity_scale=1.0,
            duration_seconds=0.1,
        )

        self.assertTrue(result.resulting_morphologies_different)
        self.assertFalse(result.polarity_determined_by_field_contract)
        self.assertFalse(result.direct_mapping_released)

    def test_moved_amount_is_exact_time_integral_of_the_inserted_mapping(
        self,
    ) -> None:
        half = propose_signed_field_flow_entry(
            self.radial,
            self.drives,
            polarity=1,
            velocity_scale=0.5,
            duration_seconds=0.1,
        )
        full = propose_signed_field_flow_entry(
            self.radial,
            self.drives,
            polarity=1,
            velocity_scale=1.0,
            duration_seconds=0.1,
        )

        self.assertTrue(half.movement_fully_explained_by_mapping)
        self.assertTrue(full.movement_fully_explained_by_mapping)
        self.assertAlmostEqual(
            2.0 * half.moved_from_unbound_material,
            full.moved_from_unbound_material,
            places=15,
        )

    def test_scale_is_an_external_conversion_not_a_field_quantity(self) -> None:
        result = compare_signed_field_flow_polarities(
            self.radial,
            self.drives,
            velocity_scale=0.25,
            duration_seconds=0.1,
        )

        self.assertFalse(result.scale_determined_by_field_contract)
        self.assertFalse(result.aligned.audit.causal_source_verified)
        self.assertFalse(result.aligned.audit.runtime_release_granted)

    def test_counterfactual_preserves_field_drives_and_morphology(self) -> None:
        result = compare_signed_field_flow_polarities(
            self.radial,
            self.drives,
            velocity_scale=1.0,
            duration_seconds=0.1,
        )

        self.assertTrue(result.aligned.source_morphology_preserved)
        self.assertTrue(result.aligned.source_drive_preserved)
        self.assertTrue(result.reversed.source_morphology_preserved)
        self.assertTrue(result.reversed.source_drive_preserved)
        self.assertFalse(result.material_runtime_changed)

    def test_public_roles_contain_no_runtime_or_organic_claim(self) -> None:
        forbidden = {
            "memory",
            "meaning",
            "learning",
            "relationship",
            "field_intelligence",
            "apply_to_runtime",
            "selected_polarity",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                signed_field_flow_counterfactual_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
