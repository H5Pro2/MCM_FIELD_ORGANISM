from __future__ import annotations

import unittest
from dataclasses import replace

import numpy as np

from mcm_field_organism.mcm_f3_baseline_coupling import (
    compute_mcm_f3_linear_coupled_baseline,
    compute_mcm_f3_local_countervariable_baseline,
    compute_mcm_f3_local_leaky_baseline,
    mcm_f3_e3_baseline_calculators,
)
from mcm_field_organism.mcm_f3_coupling import compute_mcm_f3_coupling
from mcm_field_organism.mcm_f3_history_run import mcm_f3_history_preregistration
from tests.test_mcm_f3_coupling import line_layer, uniform_substrate


class MCMF3BaselineCouplingTests(unittest.TestCase):
    def _active_pair(self):
        layer = line_layer((0.0, 0.0, 0.0, 0.0))
        return (
            layer,
            uniform_substrate(
                layer,
                mcm_f3_history_preregistration().active_arm,
            ),
        )

    def test_fixed_inventory_has_three_equal_state_budget_classes(self) -> None:
        self.assertEqual(
            ("local-leaky", "local-countervariable", "linear-coupled-field"),
            tuple(name for name, _ in mcm_f3_e3_baseline_calculators()),
        )

    def test_all_baselines_are_neutral_at_uniform_m_and_zero_s(self) -> None:
        layer, substrate = self._active_pair()

        for _, calculator in mcm_f3_e3_baseline_calculators():
            with self.subTest(calculator=calculator.__name__):
                result = calculator(layer, substrate)
                self.assertTrue(np.array_equal(np.zeros(len(result.rates)), result.mass_rate))
                self.assertTrue(
                    np.array_equal(
                        np.zeros(len(result.rates)),
                        result.activation_backreaction,
                    )
                )

    def test_every_baseline_state_rate_is_globally_conservative(self) -> None:
        layer, substrate = self._active_pair()
        activation = np.linspace(-0.2, 0.2, len(layer.neurons))
        layer = replace(
            layer,
            neurons=tuple(
                replace(neuron, activation=float(activation[index]))
                for index, neuron in enumerate(layer.neurons)
            ),
        )

        for _, calculator in mcm_f3_e3_baseline_calculators():
            with self.subTest(calculator=calculator.__name__):
                result = calculator(layer, substrate)
                self.assertAlmostEqual(0.0, sum(result.mass_rate), places=14)

    def test_linear_coupled_is_first_order_f3_derivative(self) -> None:
        layer, substrate = self._active_pair()
        direction = np.linspace(-1.0, 1.0, len(layer.neurons))
        direction -= np.mean(direction)
        epsilon = 1e-7
        layer = replace(
            layer,
            neurons=tuple(
                replace(neuron, activation=float(epsilon * direction[index]))
                for index, neuron in enumerate(layer.neurons)
            ),
        )
        exact = compute_mcm_f3_coupling(layer, substrate)
        linear = compute_mcm_f3_linear_coupled_baseline(layer, substrate)

        self.assertLess(
            np.max(np.abs(np.asarray(exact.mass_rate) - np.asarray(linear.mass_rate))),
            1e-13,
        )
        self.assertLess(
            np.max(
                np.abs(
                    np.asarray(exact.activation_backreaction)
                    - np.asarray(linear.activation_backreaction)
                )
            ),
            1e-13,
        )


if __name__ == "__main__":
    unittest.main()
