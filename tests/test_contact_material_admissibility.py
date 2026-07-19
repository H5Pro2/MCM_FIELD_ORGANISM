from __future__ import annotations

import unittest

from mcm_field_organism import (
    ContactMaterialLayerState,
    ContactMaterialTransitionProposal,
    LocalContactSurface,
    LocalContactSurfaceDrive,
    NeuronContactDrive,
    NeuronContactMaterialState,
    SignedAxisTransform,
    StructuralContactDriveMap,
    audit_contact_material_proposal,
    audit_contact_material_symmetry,
    contact_material_admissibility_public_roles,
)


class ContactMaterialAdmissibilityTests(unittest.TestCase):
    def _source(self, *, mirrored: bool = False) -> ContactMaterialLayerState:
        positions = ((0,), (-1,)) if mirrored else ((0,), (1,))
        return ContactMaterialLayerState(
            "layer.one",
            "geometry.one",
            0,
            tuple(
                NeuronContactMaterialState(
                    f"n.{index}",
                    "geometry.one",
                    position,
                    0,
                    1.0,
                    1.0,
                    (
                        LocalContactSurface((-1,), 0.0),
                        LocalContactSurface((1,), 0.0),
                    ),
                )
                for index, position in enumerate(positions)
            ),
        )

    def _drives(
        self,
        source: ContactMaterialLayerState,
        *,
        mirrored: bool = False,
        zero: bool = False,
    ) -> StructuralContactDriveMap:
        active_direction = (-1,) if mirrored else (1,)
        neurons = []
        for substrate in source.substrates:
            surfaces = []
            for surface in substrate.surfaces:
                active = (
                    not zero
                    and substrate.owner_position == (0,)
                    and surface.relative_position == active_direction
                )
                surfaces.append(
                    LocalContactSurfaceDrive(
                        surface.relative_position,
                        0.0,
                        active,
                        0.5 if active else None,
                        0.5 if active else None,
                    )
                )
            neurons.append(
                NeuronContactDrive(
                    substrate.owner_neuron_id,
                    substrate.owner_position,
                    0,
                    1,
                    0.0,
                    tuple(surfaces),
                )
            )
        return StructuralContactDriveMap(
            "layer.one",
            "geometry.one",
            0,
            1,
            1.0,
            "source.layer.digest",
            source.digest(),
            tuple(neurons),
        )

    def _target(
        self,
        source: ContactMaterialLayerState,
        *,
        direction: tuple[int, ...] | None,
        changed_total: bool = False,
    ) -> ContactMaterialLayerState:
        substrates = []
        for item in source.substrates:
            material = (
                0.25
                if item.owner_position == (0,) and direction is not None
                else 0.0
            )
            total = 2.0 if changed_total and item.owner_position == (0,) else 1.0
            substrates.append(
                NeuronContactMaterialState(
                    item.owner_neuron_id,
                    item.geometry_id,
                    item.owner_position,
                    1,
                    total,
                    total - material,
                    tuple(
                        LocalContactSurface(
                            surface.relative_position,
                            material
                            if surface.relative_position == direction
                            and item.owner_position == (0,)
                            else 0.0,
                        )
                        for surface in item.surfaces
                    ),
                )
            )
        return ContactMaterialLayerState(
            source.source_layer_id,
            source.geometry_id,
            1,
            tuple(substrates),
        )

    def _proposal(
        self,
        source: ContactMaterialLayerState,
        drives: StructuralContactDriveMap,
        target: ContactMaterialLayerState,
    ) -> ContactMaterialTransitionProposal:
        return ContactMaterialTransitionProposal(
            source.digest(),
            drives.digest(),
            0,
            1.0,
            target,
        )

    def test_conserving_local_proposal_is_admissible_but_not_released(self) -> None:
        source = self._source()
        drives = self._drives(source)
        proposal = self._proposal(
            source,
            drives,
            self._target(source, direction=(1,)),
        )
        audit = audit_contact_material_proposal(source, drives, proposal)
        self.assertTrue(audit.accepted)
        self.assertTrue(audit.owner_totals_preserved)
        self.assertTrue(audit.local_balance_valid)
        self.assertFalse(audit.runtime_release_granted)

    def test_changed_owner_total_is_rejected(self) -> None:
        source = self._source()
        drives = self._drives(source)
        proposal = self._proposal(
            source,
            drives,
            self._target(source, direction=(1,), changed_total=True),
        )
        audit = audit_contact_material_proposal(source, drives, proposal)
        self.assertFalse(audit.accepted)
        self.assertFalse(audit.owner_totals_preserved)

    def test_neutral_zero_cause_cannot_create_structure(self) -> None:
        source = self._source()
        drives = self._drives(source, zero=True)
        proposal = self._proposal(
            source,
            drives,
            self._target(source, direction=(1,)),
        )
        audit = audit_contact_material_proposal(source, drives, proposal)
        self.assertTrue(audit.neutral_null_applicable)
        self.assertFalse(audit.neutral_null_preserved)
        self.assertFalse(audit.accepted)

    def test_reflected_input_requires_reflected_material_proposal(self) -> None:
        source = self._source()
        drives = self._drives(source)
        proposal = self._proposal(
            source,
            drives,
            self._target(source, direction=(1,)),
        )
        reflected_source = self._source(mirrored=True)
        reflected_drives = self._drives(reflected_source, mirrored=True)
        reflected_proposal = self._proposal(
            reflected_source,
            reflected_drives,
            self._target(reflected_source, direction=(-1,)),
        )
        audit = audit_contact_material_symmetry(
            source,
            drives,
            proposal,
            reflected_source,
            reflected_drives,
            reflected_proposal,
            SignedAxisTransform((0,), (-1,)),
        )
        self.assertTrue(audit.accepted)
        self.assertFalse(audit.runtime_release_granted)

    def test_fixed_direction_bias_fails_reflection_audit(self) -> None:
        source = self._source()
        drives = self._drives(source)
        proposal = self._proposal(
            source,
            drives,
            self._target(source, direction=(1,)),
        )
        reflected_source = self._source(mirrored=True)
        reflected_drives = self._drives(reflected_source, mirrored=True)
        biased_proposal = self._proposal(
            reflected_source,
            reflected_drives,
            self._target(reflected_source, direction=(1,)),
        )
        audit = audit_contact_material_symmetry(
            source,
            drives,
            proposal,
            reflected_source,
            reflected_drives,
            biased_proposal,
            SignedAxisTransform((0,), (-1,)),
        )
        self.assertFalse(audit.proposal_equivalent)
        self.assertFalse(audit.accepted)

    def test_public_contract_contains_no_rule_or_runtime_effect(self) -> None:
        forbidden = {
            "weight",
            "winner",
            "meaning",
            "reward",
            "growth_rate",
            "decay_rate",
            "selected_surface",
            "field_effect",
            "apply_to_runtime",
        }
        self.assertTrue(
            forbidden.isdisjoint(contact_material_admissibility_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
