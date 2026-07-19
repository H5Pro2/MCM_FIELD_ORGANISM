from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    RadialTransportCauseDisposition,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    audit_radial_transport_cause_roles,
    build_neutral_contact_material_layer,
    build_shared_mcm_field,
    map_structural_contact_drives,
    radial_transport_cause_audit_public_roles,
    receptor_projection_baseline,
)


class RadialTransportCauseAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        geometry_id = "cause.audit.v1"
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
                CommonFieldTime("organism.cause", 0, 1),
            ),
            receptor_projection_baseline,
        )
        driven = seeded.advance(
            distributor.distribute(
                (frame("drive", (0.0, 0.0, 0.0), 1, 2),),
                CommonFieldTime("organism.cause", 1, 2),
            ),
            receptor_projection_baseline,
        )
        material = build_neutral_contact_material_layer(
            seeded.layer,
            material_per_neuron=1.0,
        )
        cls.source = seeded.layer
        cls.drives = map_structural_contact_drives(
            material,
            seeded.layer,
            driven.layer,
            response_time_seconds=1.0,
        )
        cls.result = audit_radial_transport_cause_roles(
            cls.source,
            cls.drives,
        )

    def test_direct_receptor_contact_has_no_surface_direction(self) -> None:
        item = self.result.assessment("current_receptor_contact")
        self.assertTrue(self.result.receptor_surface_selector_absent)
        self.assertTrue(self.result.direct_receptor_cause_rejected)
        self.assertTrue(item.owner_local)
        self.assertFalse(item.direction_resolved)
        self.assertTrue(item.requires_added_direction_rule)
        self.assertEqual(
            RadialTransportCauseDisposition.REJECTED_AS_DIRECT_CAUSE,
            item.disposition,
        )

    def test_owner_activation_is_repeated_not_direction_selecting(self) -> None:
        item = self.result.assessment("owner_activation")
        self.assertTrue(
            self.result.owner_activation_surface_selector_absent
        )
        self.assertTrue(item.owner_local)
        self.assertFalse(item.direction_resolved)
        self.assertTrue(item.requires_added_direction_rule)

    def test_owner_afterimage_is_fast_leaky_and_not_surface_resolved(self) -> None:
        item = self.result.assessment("owner_fast_afterimage")
        self.assertTrue(
            self.result.owner_afterimage_surface_selector_absent
        )
        self.assertTrue(self.result.direct_afterimage_cause_rejected)
        self.assertTrue(item.carries_fast_history)
        self.assertTrue(item.inherits_fixed_leak)
        self.assertFalse(item.direction_resolved)

    def test_sampled_afterimage_is_not_an_existing_contact_drive_role(self) -> None:
        item = self.result.assessment("sampled_fast_afterimage")
        self.assertTrue(self.result.sampled_afterimage_excluded_from_drive)
        self.assertFalse(item.present_in_contact_drive)
        self.assertEqual(
            RadialTransportCauseDisposition.NOT_PRESENT_IN_DRIVE_CONTRACT,
            item.disposition,
        )

    def test_only_signed_local_field_flow_remains_open_for_isolation(self) -> None:
        item = self.result.assessment("signed_local_field_flow")
        self.assertTrue(
            self.result.signed_local_field_flow_direction_available
        )
        self.assertEqual(
            ("signed_local_field_flow",),
            self.result.open_candidate_ids,
        )
        self.assertTrue(item.direction_resolved)
        self.assertTrue(item.geometric_sign_available)
        self.assertFalse(item.selected_as_material_cause)
        self.assertEqual(
            RadialTransportCauseDisposition.OPEN_FOR_PASSIVE_ISOLATION,
            item.disposition,
        )

    def test_audit_preserves_sources_and_moves_no_material(self) -> None:
        self.assertTrue(self.result.source_layer_preserved)
        self.assertTrue(self.result.drive_map_preserved)
        self.assertFalse(self.result.material_motion_performed)
        self.assertFalse(self.result.runtime_candidate_released)

    def test_public_roles_contain_no_flux_or_velocity_selection(self) -> None:
        forbidden = {
            "selected_velocity",
            "selected_sign",
            "material_delta",
            "radial_flux",
            "apply_to_runtime",
            "learning_rate",
            "meaning",
            "reward",
        }
        self.assertTrue(
            forbidden.isdisjoint(
                radial_transport_cause_audit_public_roles()
            )
        )


if __name__ == "__main__":
    unittest.main()
