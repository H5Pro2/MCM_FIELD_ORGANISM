from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    EndogenousReceptorError,
    EndogenousReceptorSurface,
    ReceptorDock,
    ReceptorDockAnatomy,
    ReceptorDistributor,
    audit_endogenous_contact_continuity,
    build_shared_mcm_field,
    endogenous_receptor_public_roles,
    receptor_projection_baseline,
)


class EndogenousReceptorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.surface = EndogenousReceptorSurface(
            source_id="body",
            geometry_id="endogenous.body.v1",
            carrier_ids=("c0", "c1"),
        )

    def frame(
        self,
        values: tuple[float, float],
        *,
        index: int,
        start: int,
        end: int,
    ):
        return self.surface.complete_contact(
            values,
            snapshot_id=f"endogenous.body.{index}",
            clock_id="organism.sample",
            window_start_tick=start,
            window_end_tick=end,
        )

    def test_surface_preserves_local_signed_measurements_without_interpretation(
        self,
    ) -> None:
        frame = self.frame((0.25, -0.5), index=0, start=0, end=10)

        self.assertEqual("endogenous.body", frame.modality_id)
        self.assertEqual(("c0", "c1"), frame.carrier_ids)
        self.assertEqual((0.25, -0.5), frame.values)

    def test_surface_does_not_hold_or_generate_a_previous_contact(self) -> None:
        first = self.frame((0.7, -0.2), index=0, start=0, end=10)
        second = self.frame((0.0, 0.0), index=1, start=10, end=20)

        self.assertEqual((0.7, -0.2), first.values)
        self.assertEqual((0.0, 0.0), second.values)

    def test_continuity_audit_reports_but_does_not_fill_a_gap(self) -> None:
        first = self.frame((0.1, 0.2), index=0, start=0, end=10)
        second = self.frame((0.3, 0.4), index=1, start=15, end=20)

        audit = audit_endogenous_contact_continuity((first, second))

        self.assertFalse(audit.is_contiguous)
        self.assertEqual(1, len(audit.gaps))
        self.assertEqual((10, 15), (
            audit.gaps[0].previous_end_tick,
            audit.gaps[0].next_start_tick,
        ))
        self.assertEqual((0.3, 0.4), second.values)

    def test_contiguous_contact_is_observed_without_persistence_state(self) -> None:
        audit = audit_endogenous_contact_continuity(
            (
                self.frame((0.1, 0.2), index=0, start=0, end=10),
                self.frame((0.2, 0.1), index=1, start=10, end=20),
            )
        )

        self.assertTrue(audit.is_contiguous)
        self.assertEqual(2, audit.frame_count)
        self.assertEqual((), audit.gaps)

    def test_endogenous_contact_uses_normal_distributor_and_shared_field(
        self,
    ) -> None:
        frame = self.frame((0.3, -0.4), index=0, start=0, end=10)
        anatomy = ReceptorDockAnatomy(
            modality_id=frame.modality_id,
            dock_id="dock.endogenous.body",
            positions=((0,), (1,)),
        )
        field = build_shared_mcm_field(
            (frame,),
            {frame.modality_id: anatomy},
            sample_offsets=((-1,), (1,)),
        )
        distributor = ReceptorDistributor()
        distributor.attach(
            ReceptorDock(
                dock_id=anatomy.dock_id,
                modality_id=frame.modality_id,
                receptor_geometry_id=frame.geometry_id,
            )
        )
        distribution = distributor.distribute(
            (frame,),
            CommonFieldTime("organism.clock", 0, 1),
        )

        advanced = field.advance(distribution, receptor_projection_baseline)

        self.assertEqual(
            (0.3, -0.4),
            tuple(neuron.activation for neuron in advanced.layer.neurons),
        )
        self.assertEqual(("dock.endogenous.body",), distribution.dock_ids)

    def test_invalid_values_and_mixed_sources_are_rejected(self) -> None:
        with self.assertRaises(EndogenousReceptorError):
            self.frame((1.1, 0.0), index=0, start=0, end=10)

        other = EndogenousReceptorSurface(
            source_id="other",
            geometry_id="endogenous.other.v1",
            carrier_ids=("c0", "c1"),
        ).complete_contact(
            (0.0, 0.0),
            snapshot_id="endogenous.other.0",
            clock_id="organism.sample",
            window_start_tick=10,
            window_end_tick=20,
        )
        with self.assertRaises(EndogenousReceptorError):
            audit_endogenous_contact_continuity(
                (self.frame((0.0, 0.0), index=0, start=0, end=10), other)
            )

    def test_contract_exposes_no_mood_noise_memory_or_field_write_role(self) -> None:
        forbidden = {
            "mood",
            "noise",
            "memory",
            "meaning",
            "weight",
            "winner",
            "field_effect",
            "material_velocity",
        }
        self.assertTrue(forbidden.isdisjoint(endogenous_receptor_public_roles()))


if __name__ == "__main__":
    unittest.main()
