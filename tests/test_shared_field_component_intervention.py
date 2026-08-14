from __future__ import annotations

from dataclasses import replace
import unittest

from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_distributor import ReceptorDistributor, ReceptorDock
from mcm_field_organism.shared_field_component_intervention import (
    SharedFieldComponentInterventionError,
    intervene_shared_field_component,
    shared_field_component_intervention_public_roles,
)
from mcm_field_organism.shared_mcm_field import ReceptorDockAnatomy, build_shared_mcm_field


def completed_field():
    frame = ReceptorContactFrame(
        "auditory", "auditory.test", "snapshot.test", "source.test", 0, 10,
        ("carrier.0", "carrier.1"), (0.8, 0.2),
    )
    field = build_shared_mcm_field(
        (frame,),
        {"auditory": ReceptorDockAnatomy("auditory", "dock.auditory", ((0,), (1,)))},
        sample_offsets=((-1,), (1,)),
    )
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.auditory", "auditory", "auditory.test"))
    distribution = distributor.distribute((frame,), CommonFieldTime("organism.test", 0, 10))
    return advance_neutral_fast_shared_field(
        field,
        distribution,
        MCMFieldStepTime("organism.test", 0, 10, 10.0),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


class SharedFieldComponentInterventionTests(unittest.TestCase):
    def test_reset_afterimage_preserves_activation_and_every_structural_role(self) -> None:
        field = completed_field()
        result = intervene_shared_field_component(field, "reset_afterimage_preserve_activation")
        self.assertEqual(
            [item.activation for item in field.layer.neurons],
            [item.activation for item in result.field.layer.neurons],
        )
        self.assertTrue(all(item.afterimage == 0.0 for item in result.field.layer.neurons))
        self.assertTrue(result.audit.geometry_preserved)
        self.assertTrue(result.audit.perception_preserved)
        self.assertTrue(result.audit.tick_preserved)

    def test_reset_activation_preserves_afterimage_and_input_field(self) -> None:
        field = completed_field()
        before = field.layer.digest()
        result = intervene_shared_field_component(field, "reset_activation_preserve_afterimage")
        self.assertTrue(all(item.activation == 0.0 for item in result.field.layer.neurons))
        self.assertEqual(
            [item.afterimage for item in field.layer.neurons],
            [item.afterimage for item in result.field.layer.neurons],
        )
        self.assertEqual(before, field.layer.digest())
        self.assertTrue(result.audit.input_field_unchanged)

    def test_intervention_does_not_advance_time_or_add_contacts(self) -> None:
        result = intervene_shared_field_component(completed_field(), "reset_activation_preserve_afterimage")
        self.assertFalse(result.audit.field_time_advanced)
        self.assertFalse(result.audit.receptor_events_introduced)
        self.assertFalse(result.audit.organism_function_added)
        self.assertTrue(result.audit.last_distribution_preserved)

    def test_initial_field_and_unknown_mode_are_rejected(self) -> None:
        field = completed_field()
        initial = replace(field, last_distribution=None)
        with self.assertRaisesRegex(SharedFieldComponentInterventionError, "completed"):
            intervene_shared_field_component(initial, "reset_activation_preserve_afterimage")
        with self.assertRaisesRegex(SharedFieldComponentInterventionError, "mode"):
            intervene_shared_field_component(field, "select_by_result")

    def test_public_contract_excludes_content_and_claim_scores(self) -> None:
        forbidden = {"label", "meaning", "reward", "target_topology", "memory_score", "organization_score"}
        self.assertTrue(forbidden.isdisjoint(shared_field_component_intervention_public_roles()))


if __name__ == "__main__":
    unittest.main()
