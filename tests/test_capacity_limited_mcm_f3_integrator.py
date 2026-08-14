from __future__ import annotations

import math
import unittest

from mcm_field_organism import (
    MCMSubstrateArmContract,
    build_uniform_mcm_substrate,
)
from mcm_field_organism.capacity_limited_mcm_f3_coupling import (
    MCMCapacityLimitedCouplingContract,
)
from mcm_field_organism.capacity_limited_mcm_f3_integrator import (
    MCMCapacityLimitedIntegratorError,
    integrate_capacity_limited_mcm_f3_coupling,
)
from tests.test_capacity_limited_mcm_f3_coupling import _layer, _substrate


def _distance(first, second) -> float:
    return math.sqrt(
        math.fsum(
            (left - right) ** 2
            for left, right in zip(
                (*first.activation, *first.mass),
                (*second.activation, *second.mass),
                strict=True,
            )
        )
    )


class CapacityLimitedMCMF3IntegratorTests(unittest.TestCase):
    def test_null_arm_is_an_exact_zero_step_path(self) -> None:
        layer = _layer(-0.5, 0.5)
        substrate = build_uniform_mcm_substrate(
            layer,
            MCMSubstrateArmContract("p0.null", 0.0, 0.5, 2.0),
        )
        layer_digest = layer.digest()
        substrate_digest = substrate.digest()

        result = integrate_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(0.75),
            2.0,
        )

        self.assertEqual("p0.exact", result.diagnostics.method_id)
        self.assertEqual(0, result.diagnostics.substep_count)
        self.assertEqual(0, result.diagnostics.stage_count)
        self.assertIsNone(result.diagnostics.safe_step_seconds)
        self.assertEqual(
            tuple(neuron.activation for neuron in layer.neurons),
            result.activation,
        )
        self.assertEqual(
            tuple(neuron.afterimage for neuron in layer.neurons),
            result.afterimage,
        )
        self.assertEqual(
            tuple(item.mass for item in substrate.masses),
            result.mass,
        )
        self.assertEqual(layer_digest, layer.digest())
        self.assertEqual(substrate_digest, substrate.digest())

    def test_active_ssprk_preserves_all_isolated_invariants(self) -> None:
        layer = _layer(-0.6, 0.7)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7i.active", 1.2, 0.45, 0.8),
            (0.35, 0.65),
        )
        capacity = 0.8

        result = integrate_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(capacity),
            1.0,
        )

        self.assertGreater(result.diagnostics.substep_count, 0)
        self.assertEqual(
            3 * result.diagnostics.substep_count,
            result.diagnostics.stage_count,
        )
        self.assertLessEqual(
            result.diagnostics.maximum_step_seconds,
            result.diagnostics.safe_step_seconds,
        )
        self.assertAlmostEqual(1.0, math.fsum(result.mass), places=12)
        self.assertGreaterEqual(min(result.mass), 0.0)
        self.assertLessEqual(max(result.mass), capacity)
        self.assertGreaterEqual(result.diagnostics.minimum_mass, 0.0)
        self.assertLessEqual(result.diagnostics.maximum_mass, capacity)
        self.assertGreaterEqual(result.diagnostics.minimum_free_capacity, 0.0)
        self.assertEqual(0.0, result.diagnostics.maximum_capacity_excess)
        self.assertLessEqual(max(abs(value) for value in result.activation), 1.0)
        self.assertEqual(
            tuple(neuron.afterimage for neuron in layer.neurons),
            result.afterimage,
        )

    def test_repeated_execution_is_exactly_deterministic(self) -> None:
        layer = _layer(-0.4, 0.8)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7i.active", 0.9, -0.35, 1.1),
            (0.45, 0.55),
        )
        contract = MCMCapacityLimitedCouplingContract(0.85)

        first = integrate_capacity_limited_mcm_f3_coupling(
            layer, substrate, contract, 0.75, refinement=2
        )
        second = integrate_capacity_limited_mcm_f3_coupling(
            layer, substrate, contract, 0.75, refinement=2
        )

        self.assertEqual(first, second)

    def test_refinement_converges_in_order(self) -> None:
        layer = _layer(-0.55, 0.65)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7i.active", 1.1, 0.4, 0.7),
            (0.3, 0.7),
        )
        contract = MCMCapacityLimitedCouplingContract(0.8)

        n = integrate_capacity_limited_mcm_f3_coupling(
            layer, substrate, contract, 0.9, refinement=1
        )
        two_n = integrate_capacity_limited_mcm_f3_coupling(
            layer, substrate, contract, 0.9, refinement=2
        )
        four_n = integrate_capacity_limited_mcm_f3_coupling(
            layer, substrate, contract, 0.9, refinement=4
        )

        self.assertGreater(_distance(n, two_n), _distance(two_n, four_n))
        self.assertEqual(
            2 * n.diagnostics.substep_count,
            two_n.diagnostics.substep_count,
        )
        self.assertEqual(
            2 * two_n.diagnostics.substep_count,
            four_n.diagnostics.substep_count,
        )

    def test_zero_duration_holds_active_vectors_without_stages(self) -> None:
        layer = _layer(-0.5, 0.5)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7i.active", 1.0, 0.5, 1.0),
            (0.4, 0.6),
        )

        result = integrate_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            MCMCapacityLimitedCouplingContract(0.8),
            0.0,
        )

        self.assertEqual(0, result.diagnostics.substep_count)
        self.assertEqual(0, result.diagnostics.stage_count)
        self.assertEqual((-0.5, 0.5), result.activation)
        self.assertEqual((0.4, 0.6), result.mass)

    def test_invalid_integration_or_capacity_contract_is_rejected(self) -> None:
        layer = _layer(-0.5, 0.5)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7i.active", 1.0, 0.5, 1.0),
            (0.2, 0.8),
        )

        with self.assertRaisesRegex(
            MCMCapacityLimitedIntegratorError,
            "exceeded site_capacity",
        ):
            integrate_capacity_limited_mcm_f3_coupling(
                layer,
                substrate,
                MCMCapacityLimitedCouplingContract(0.7),
                0.5,
            )
        with self.assertRaisesRegex(
            MCMCapacityLimitedIntegratorError,
            "duration_seconds must be nonnegative",
        ):
            integrate_capacity_limited_mcm_f3_coupling(
                layer,
                substrate,
                MCMCapacityLimitedCouplingContract(0.8),
                -0.1,
            )

    def test_module_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "integrate_capacity_limited_mcm_f3_coupling")
        )


if __name__ == "__main__":
    unittest.main()
