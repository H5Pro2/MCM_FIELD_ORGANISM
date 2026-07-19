from __future__ import annotations

import unittest

from mcm_field_organism import (
    NeuronRadialFluxProposal,
    NeuronRadialMaterialState,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    RadialContactMaterialLayerState,
    RadialContactProfile,
    RadialInterfaceFlux,
    RadialMaterialCell,
    RadialProfileFluxProposal,
    RadialTransportProposal,
    audit_radial_transport_proposal,
    build_neutral_contact_material_layer,
    build_neutral_radial_contact_morphology,
    controlled_reentry_world_family,
    radial_transport_admissibility_public_roles,
    run_controlled_test_world,
)


EDGES = (0.0, 0.5, 1.0)
DIRECTIONS = ((-1,), (1,))


def profile(direction: tuple[int, ...], amounts=(0.0, 0.0)):
    return RadialContactProfile(
        direction,
        (
            RadialMaterialCell(0.0, 0.5, amounts[0]),
            RadialMaterialCell(0.5, 1.0, amounts[1]),
        ),
    )


def source_state(*, seeded: bool = False) -> RadialContactMaterialLayerState:
    owners = []
    for index, position in enumerate(((0,), (1,))):
        seeded_owner = seeded and index == 0
        owners.append(
            NeuronRadialMaterialState(
                owner_neuron_id=f"n.{index}",
                geometry_id="geometry.one",
                owner_position=position,
                field_tick=0,
                total_material=1.0,
                unbound_material=0.5 if seeded_owner else 1.0,
                profiles=(
                    profile((-1,)),
                    profile(
                        (1,),
                        (0.5, 0.0) if seeded_owner else (0.0, 0.0),
                    ),
                ),
            )
        )
    return RadialContactMaterialLayerState(
        source_layer_id="layer.one",
        geometry_id="geometry.one",
        field_tick=0,
        radial_edges=EDGES,
        source_contact_material_digest="contact.digest",
        substrates=tuple(owners),
    )


def flux_profile(
    direction: tuple[int, ...],
    rates=(0.0, 0.0, 0.0),
    edges=EDGES,
):
    return RadialProfileFluxProposal(
        direction,
        tuple(
            RadialInterfaceFlux(edge, rate)
            for edge, rate in zip(edges, rates, strict=True)
        ),
    )


def proposal(
    source: RadialContactMaterialLayerState,
    *,
    rates_by_owner_direction=None,
    edges=EDGES,
    reverse=False,
):
    rates_by_owner_direction = rates_by_owner_direction or {}
    owners = []
    source_owners = (
        reversed(source.substrates) if reverse else source.substrates
    )
    for owner in source_owners:
        directions = reversed(DIRECTIONS) if reverse else DIRECTIONS
        owners.append(
            NeuronRadialFluxProposal(
                owner.owner_neuron_id,
                tuple(
                    flux_profile(
                        direction,
                        rates_by_owner_direction.get(
                            (owner.owner_neuron_id, direction),
                            (0.0, 0.0, 0.0),
                        ),
                        edges,
                    )
                    for direction in directions
                ),
            )
        )
    return RadialTransportProposal(
        source.digest(),
        source.field_tick,
        1.0,
        tuple(owners),
    )


class RadialTransportAdmissibilityTests(unittest.TestCase):
    def test_zero_flux_preserves_neutral_distribution_without_runtime_release(
        self,
    ) -> None:
        source = source_state()
        audit = audit_radial_transport_proposal(source, proposal(source))

        self.assertTrue(audit.accepted)
        self.assertTrue(audit.zero_flux_applicable)
        self.assertTrue(audit.zero_flux_preserved)
        self.assertIsNotNone(audit.proposed_state)
        self.assertTrue(audit.proposed_state.is_neutral)
        self.assertEqual(1, audit.proposed_state.field_tick)
        self.assertFalse(audit.causal_source_verified)
        self.assertFalse(audit.runtime_release_granted)

    def test_core_flux_moves_unbound_material_into_first_radial_cell(self) -> None:
        source = source_state()
        audit = audit_radial_transport_proposal(
            source,
            proposal(
                source,
                rates_by_owner_direction={
                    ("n.0", (1,)): (0.2, 0.0, 0.0),
                },
            ),
        )

        self.assertTrue(audit.accepted)
        owner = {
            item.owner_neuron_id: item
            for item in audit.proposed_state.substrates
        }["n.0"]
        by_direction = {
            item.relative_position: item for item in owner.profiles
        }
        self.assertEqual(0.8, owner.unbound_material)
        self.assertEqual(
            (0.2, 0.0),
            tuple(
                item.material_amount for item in by_direction[(1,)].cells
            ),
        )
        self.assertEqual(1.0, owner.total_material)

    def test_internal_flux_moves_existing_support_between_neighbor_cells(
        self,
    ) -> None:
        source = source_state(seeded=True)
        audit = audit_radial_transport_proposal(
            source,
            proposal(
                source,
                rates_by_owner_direction={
                    ("n.0", (1,)): (0.0, 0.2, 0.0),
                },
            ),
        )

        self.assertTrue(audit.accepted)
        owner = {
            item.owner_neuron_id: item
            for item in audit.proposed_state.substrates
        }["n.0"]
        radial = {
            item.relative_position: item for item in owner.profiles
        }[(1,)]
        self.assertEqual(0.5, owner.unbound_material)
        self.assertEqual(
            (0.3, 0.2),
            tuple(item.material_amount for item in radial.cells),
        )

    def test_combined_core_fluxes_cannot_overdraw_shared_unbound_material(
        self,
    ) -> None:
        source = source_state()
        audit = audit_radial_transport_proposal(
            source,
            proposal(
                source,
                rates_by_owner_direction={
                    ("n.0", (-1,)): (0.6, 0.0, 0.0),
                    ("n.0", (1,)): (0.6, 0.0, 0.0),
                },
            ),
        )

        self.assertFalse(audit.reconstructed_nonnegative)
        self.assertFalse(audit.owner_balances_preserved)
        self.assertIsNone(audit.proposed_state)
        self.assertFalse(audit.accepted)

    def test_material_cannot_leave_owner_at_outer_boundary(self) -> None:
        source = source_state(seeded=True)
        audit = audit_radial_transport_proposal(
            source,
            proposal(
                source,
                rates_by_owner_direction={
                    ("n.0", (1,)): (0.0, 0.0, 0.1),
                },
            ),
        )

        self.assertFalse(audit.outer_boundaries_closed)
        self.assertIsNone(audit.proposed_state)
        self.assertFalse(audit.accepted)

    def test_flux_cannot_draw_from_an_empty_radial_cell(self) -> None:
        source = source_state()
        audit = audit_radial_transport_proposal(
            source,
            proposal(
                source,
                rates_by_owner_direction={
                    ("n.0", (1,)): (0.0, 0.2, 0.0),
                },
            ),
        )

        self.assertFalse(audit.reconstructed_nonnegative)
        self.assertIsNone(audit.proposed_state)

    def test_interface_geometry_must_match_source_resolution_exactly(self) -> None:
        source = source_state()
        audit = audit_radial_transport_proposal(
            source,
            proposal(
                source,
                edges=(0.0, 0.25, 1.0),
            ),
        )

        self.assertFalse(audit.radial_resolution_preserved)
        self.assertFalse(audit.interface_sets_complete)
        self.assertIsNone(audit.proposed_state)

    def test_complete_proposal_is_iteration_order_neutral(self) -> None:
        source = source_state()
        rates = {("n.0", (1,)): (0.2, 0.0, 0.0)}
        forward = proposal(source, rates_by_owner_direction=rates)
        reversed_order = proposal(
            source,
            rates_by_owner_direction=rates,
            reverse=True,
        )

        self.assertEqual(forward.digest(), reversed_order.digest())
        self.assertEqual(
            audit_radial_transport_proposal(source, forward).proposed_state,
            audit_radial_transport_proposal(
                source,
                reversed_order,
            ).proposed_state,
        )

    def test_zero_flux_contract_scales_to_current_84_neuron_anatomy(self) -> None:
        world, _ = controlled_reentry_world_family()
        field = run_controlled_test_world(
            world,
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        ).field_run.field
        contact = build_neutral_contact_material_layer(
            field.layer,
            material_per_neuron=1.0,
        )
        radial = build_neutral_radial_contact_morphology(
            contact,
            radial_edges=(0.0, 0.25, 0.5, 0.75, 1.0),
        )
        fluxes = RadialTransportProposal(
            radial.digest(),
            radial.field_tick,
            1.0,
            tuple(
                NeuronRadialFluxProposal(
                    owner.owner_neuron_id,
                    tuple(
                        RadialProfileFluxProposal(
                            item.relative_position,
                            tuple(
                                RadialInterfaceFlux(edge, 0.0)
                                for edge in radial.radial_edges
                            ),
                        )
                        for item in owner.profiles
                    ),
                )
                for owner in radial.substrates
            ),
        )

        audit = audit_radial_transport_proposal(radial, fluxes)

        self.assertTrue(audit.accepted)
        self.assertEqual(84, len(audit.proposed_state.substrates))
        self.assertEqual(336, audit.proposed_state.profile_count)
        self.assertEqual(1344, audit.proposed_state.radial_cell_count)

    def test_wrong_source_reference_is_rejected_without_mutation(self) -> None:
        source = source_state()
        valid = proposal(source)
        invalid = RadialTransportProposal(
            "wrong.digest",
            valid.source_tick,
            valid.duration_seconds,
            valid.neurons,
        )
        before = source.digest()

        audit = audit_radial_transport_proposal(source, invalid)

        self.assertFalse(audit.source_reference_valid)
        self.assertFalse(audit.accepted)
        self.assertEqual(before, source.digest())
        self.assertTrue(audit.source_state_preserved)

    def test_public_contract_contains_flux_but_no_velocity_or_field_rule(self) -> None:
        roles = set(radial_transport_admissibility_public_roles())
        forbidden = {
            "velocity",
            "field_cause",
            "receptor_cause",
            "growth_rate",
            "decay_rate",
            "target_position",
            "partner_id",
            "weight",
            "meaning",
            "apply_to_runtime",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
