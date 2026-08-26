from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_repetition_pilot_quantitative_p0_schema import (
    E1RepetitionPilotQuantitativeP0SchemaError,
    build_quantitative_p0_refinement_profile,
    collect_quantitative_p0_pair,
    quantitative_p0_schema_roles,
)
from mcm_field_organism.receptor_contract import CommonFieldTime
from mcm_field_organism.receptor_distributor import ReceptorDistribution
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot
from tests.test_e1_repetition_pilot_real_adapter_fixture import (
    E1RepetitionPilotRealAdapterFixtureTests,
)


class E1RepetitionPilotQuantitativeP0SchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        E1RepetitionPilotRealAdapterFixtureTests.setUpClass()
        field = E1RepetitionPilotRealAdapterFixtureTests.values.initial_field
        neurons = tuple(
            replace(
                neuron,
                perception=replace(
                    neuron.perception,
                    tick=1,
                    receptor_contact=None,
                    local_samples=tuple(
                        replace(sample, source_tick=0)
                        for sample in neuron.perception.local_samples
                    ),
                ),
            )
            for neuron in field.layer.neurons
        )
        cls.snapshot = SharedMCMFieldSnapshot(
            schema_version=1,
            layer=replace(field.layer, neurons=neurons),
            docks=field.docks,
            last_distribution=ReceptorDistribution(
                CommonFieldTime("organism.e1.av-history", 0, 1),
                (),
            ),
        )

    def _changed_snapshot(self, amount: float):
        neurons = list(self.snapshot.layer.neurons)
        neuron = neurons[0]
        neurons[0] = replace(
            neuron,
            activation=neuron.activation + amount,
            afterimage=neuron.afterimage - 2.0 * amount,
        )
        return replace(
            self.snapshot,
            layer=replace(self.snapshot.layer, neurons=tuple(neurons)),
        )

    def test_pair_retains_signed_components_and_linf(self) -> None:
        pair = collect_quantitative_p0_pair(
            2, "r2", self._changed_snapshot(0.01), self.snapshot
        )
        self.assertEqual(0.01, pair.activation_contrast[0])
        self.assertEqual(-0.02, pair.afterimage_contrast[0])
        self.assertEqual(0.01, pair.activation_linf)
        self.assertEqual(0.02, pair.afterimage_linf)

    def test_profile_uses_componentwise_fine_residual(self) -> None:
        pairs = tuple(
            collect_quantitative_p0_pair(
                2, refinement, self._changed_snapshot(amount), self.snapshot
            )
            for refinement, amount in (
                ("r2", 0.01),
                ("r4", 0.006),
                ("r8", 0.005),
            )
        )
        profile = build_quantitative_p0_refinement_profile(pairs)
        self.assertAlmostEqual(0.004, profile.activation_r2_r4_linf)
        self.assertAlmostEqual(0.001, profile.activation_r4_r8_linf)
        self.assertAlmostEqual(0.002, profile.fine_residual)
        self.assertFalse(profile.field_execution_performed)

    def test_misaligned_refinement_order_is_rejected(self) -> None:
        pair = collect_quantitative_p0_pair(2, "r2", self.snapshot, self.snapshot)
        with self.assertRaises(E1RepetitionPilotQuantitativeP0SchemaError):
            build_quantitative_p0_refinement_profile((pair, pair, pair))

    def test_required_roles_are_explicit(self) -> None:
        roles = quantitative_p0_schema_roles()
        self.assertIn("activation_contrast", roles)
        self.assertIn("afterimage_contrast", roles)
        self.assertIn("activation_linf", roles)
        self.assertIn("afterimage_linf", roles)

    def test_collector_and_profile_do_not_execute_or_persist(self) -> None:
        source = (
            inspect.getsource(collect_quantitative_p0_pair)
            + inspect.getsource(build_quantitative_p0_refinement_profile)
        )
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_e1_repetition_pilot_once_in_memory",
            "write_text",
            "write_bytes",
            "open(",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
