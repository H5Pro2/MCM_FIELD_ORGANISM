from __future__ import annotations

import unittest

from mcm_field_organism import (
    CommonFieldTime,
    ControlledEndogenousSource,
    ControlledEndogenousSourceError,
    ControlledEndogenousStep,
    ReceptorContactFrame,
    ReceptorDock,
    ReceptorDockAnatomy,
    ReceptorDistributor,
    audit_endogenous_contact_continuity,
    build_shared_mcm_field,
    controlled_endogenous_source_public_roles,
    controlled_multiscale_endogenous_source,
    receptor_projection_baseline,
)


def external_frame() -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id="external.controlled",
        geometry_id="external.controlled.v1",
        snapshot_id="external.controlled.0",
        clock_id="external.sample",
        window_start_tick=0,
        window_end_tick=1,
        carrier_ids=("x0",),
        values=(0.6,),
    )


class ControlledEndogenousSourceTests(unittest.TestCase):
    def test_reference_source_is_repeatable_contiguous_and_finite(self) -> None:
        first = controlled_multiscale_endogenous_source()
        second = controlled_multiscale_endogenous_source()

        self.assertEqual(first.digest(), second.digest())
        self.assertEqual(first.frames(), second.frames())
        self.assertEqual(8, first.frame_count)
        self.assertEqual(8, first.end_tick)
        self.assertTrue(
            audit_endogenous_contact_continuity(first.frames()).is_contiguous
        )

    def test_reference_carriers_have_distinct_unlabelled_time_scales(self) -> None:
        values = tuple(frame.values for frame in controlled_multiscale_endogenous_source().frames())
        first = tuple(item[0] for item in values)
        second = tuple(item[1] for item in values)

        first_changes = sum(left != right for left, right in zip(first, first[1:]))
        second_changes = sum(left != right for left, right in zip(second, second[1:]))
        self.assertEqual((7, 7), (first_changes, second_changes))
        first_total_change = sum(
            abs(right - left) for left, right in zip(first, first[1:])
        )
        second_total_change = sum(
            abs(right - left) for left, right in zip(second, second[1:])
        )
        self.assertEqual(0, sum(value < 0.0 for value in first))
        self.assertEqual(2, sum(value < 0.0 for value in second))
        self.assertGreater(second_total_change, first_total_change)
        self.assertNotEqual(first, second)

    def test_values_are_explicit_and_no_random_state_is_retained(self) -> None:
        source = ControlledEndogenousSource(
            source_id="explicit",
            geometry_id="endogenous.explicit.v1",
            clock_id="organism.controlled",
            carrier_ids=("c0",),
            start_tick=10,
            steps=(
                ControlledEndogenousStep(2, (0.2,)),
                ControlledEndogenousStep(3, (-0.4,)),
            ),
        )

        first = source.frames()
        second = source.frames()
        self.assertEqual(first, second)
        self.assertEqual((10, 12), (
            first[0].window_start_tick,
            first[0].window_end_tick,
        ))
        self.assertEqual((12, 15), (
            first[1].window_start_tick,
            first[1].window_end_tick,
        ))
        self.assertFalse(hasattr(source, "cursor"))
        self.assertFalse(hasattr(source, "random_state"))

    def test_external_and_endogenous_contacts_share_one_field_without_fusion(
        self,
    ) -> None:
        endogenous = controlled_multiscale_endogenous_source().frames()[1]
        external = external_frame()
        anatomies = {
            endogenous.modality_id: ReceptorDockAnatomy(
                endogenous.modality_id,
                "dock.endogenous.controlled",
                ((0, 0), (0, 1)),
            ),
            external.modality_id: ReceptorDockAnatomy(
                external.modality_id,
                "dock.external.controlled",
                ((1, 0),),
            ),
        }
        field = build_shared_mcm_field(
            (endogenous, external),
            anatomies,
            sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
        )
        distributor = ReceptorDistributor()
        for frame in (endogenous, external):
            anatomy = anatomies[frame.modality_id]
            distributor.attach(
                ReceptorDock(
                    anatomy.dock_id,
                    frame.modality_id,
                    frame.geometry_id,
                )
            )
        distribution = distributor.distribute(
            (external, endogenous),
            CommonFieldTime("organism.clock", 0, 1),
        )

        advanced = field.advance(distribution, receptor_projection_baseline)
        activation_by_id = {
            neuron.neuron_id: neuron.activation
            for neuron in advanced.layer.neurons
        }

        self.assertEqual(
            {
                "organism.mcm_field.endogenous.controlled.n0": 0.25,
                "organism.mcm_field.endogenous.controlled.n1": 1.0,
                "organism.mcm_field.external.controlled.n0": 0.6,
            },
            activation_by_id,
        )
        self.assertEqual(
            ("endogenous.controlled", "external.controlled"),
            distribution.modality_ids,
        )

    def test_invalid_schedule_is_rejected_before_field_contact(self) -> None:
        invalid = (
            lambda: ControlledEndogenousStep(0, (0.0,)),
            lambda: ControlledEndogenousSource(
                "x",
                "endogenous.x.v1",
                "organism.controlled",
                ("c0",),
                0,
                (),
            ),
            lambda: ControlledEndogenousSource(
                "x",
                "endogenous.x.v1",
                "organism.controlled",
                ("c0",),
                0,
                (ControlledEndogenousStep(1, (0.0, 0.1)),),
            ),
        )
        for call in invalid:
            with self.assertRaises(ControlledEndogenousSourceError):
                call()

    def test_public_contract_contains_no_semantics_mood_memory_or_field_write(
        self,
    ) -> None:
        forbidden = {
            "label",
            "meaning",
            "mood",
            "pain",
            "fatigue",
            "noise",
            "memory",
            "field_effect",
            "material_velocity",
        }
        self.assertTrue(
            forbidden.isdisjoint(controlled_endogenous_source_public_roles())
        )


if __name__ == "__main__":
    unittest.main()
