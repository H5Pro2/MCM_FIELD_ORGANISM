from __future__ import annotations

from dataclasses import replace
import math
import unittest

import numpy as np

from mcm_field_organism import MCMSubstrateArmContract
from mcm_field_organism.capacity_limited_mcm_f3_coupling import (
    compute_capacity_limited_mcm_f3_coupling,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    W7MBaselineSpec,
    build_w7m_capacity_function_matrix_adapter,
)
from mcm_field_organism.w7n_capacity_function_baselines import (
    W7NCapacityFunctionBaselineError,
    advance_w7n_local_baseline,
    build_zero_w7n_local_baseline,
    compute_w7n_coupling_baseline,
)
from tests.test_capacity_limited_mcm_f3_coupling import _layer, _substrate


class W7NCapacityFunctionBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()
        cls.specs = {item.model_id: item for item in cls.adapter.baselines}

    def test_local_exact_updates_match_the_frozen_equations(self) -> None:
        evidence = (1.0, -1.0, 0.5)
        expected_latent = tuple(
            (1.0 - math.exp(-1.0)) * value for value in evidence
        )

        leak = advance_w7n_local_baseline(
            self.specs["leak"],
            build_zero_w7n_local_baseline(self.specs["leak"], 3),
            evidence,
            1.0,
        )
        sat = advance_w7n_local_baseline(
            self.specs["sat"],
            build_zero_w7n_local_baseline(self.specs["sat"], 3),
            evidence,
            1.0,
        )

        np.testing.assert_allclose(expected_latent, leak.state.latent)
        self.assertEqual(leak.state.latent, leak.output)
        np.testing.assert_allclose(expected_latent, sat.state.latent)
        np.testing.assert_allclose(
            tuple(math.tanh(value) for value in expected_latent),
            sat.output,
        )

    def test_local_split_time_is_exact_and_inputs_are_immutable(self) -> None:
        spec = self.specs["leak"]
        initial = build_zero_w7n_local_baseline(spec, 2)
        evidence = (0.8, -0.3)

        whole = advance_w7n_local_baseline(spec, initial, evidence, 1.0)
        half = advance_w7n_local_baseline(spec, initial, evidence, 0.5)
        split = advance_w7n_local_baseline(spec, half.state, evidence, 0.5)

        np.testing.assert_allclose(whole.state.latent, split.state.latent)
        self.assertEqual((0.0, 0.0), initial.latent)
        self.assertEqual((0.8, -0.3), evidence)

    def test_norm_is_only_a_global_observer_projection(self) -> None:
        spec = self.specs["norm"]
        state = build_zero_w7n_local_baseline(spec, 3)
        result = advance_w7n_local_baseline(
            spec,
            state,
            (1.0, -0.5, 0.25),
            1.0,
        )

        self.assertNotEqual(result.state.latent, result.output)
        self.assertLess(math.fsum(abs(value) for value in result.output), 1.0)
        self.assertEqual(
            tuple(
                value
                / (
                    1e-12
                    + math.fsum(abs(item) for item in result.state.latent)
                )
                for value in result.state.latent
            ),
            result.output,
        )

    def test_changed_equation_or_mismatched_state_is_rejected(self) -> None:
        leak = self.specs["leak"]
        changed = replace(leak, equation_contract="changed")
        state = build_zero_w7n_local_baseline(leak, 2)

        with self.assertRaisesRegex(
            W7NCapacityFunctionBaselineError,
            "differs from its frozen contract",
        ):
            build_zero_w7n_local_baseline(changed, 2)
        with self.assertRaisesRegex(
            W7NCapacityFunctionBaselineError,
            "state and specification differ",
        ):
            advance_w7n_local_baseline(
                self.specs["sat"],
                state,
                (0.0, 0.0),
                1.0,
            )

    def test_cap_const_v_and_mob_match_at_the_homogeneous_start(self) -> None:
        adapter = self.adapter
        layer = adapter.initial_field.layer
        substrate = adapter.initial_field.substrate
        layer_digest = layer.digest()
        substrate_digest = substrate.digest()

        cap = compute_capacity_limited_mcm_f3_coupling(
            layer,
            substrate,
            adapter.runtime_contract.coupling_contract,
        )
        const_v = compute_w7n_coupling_baseline(
            self.specs["const-v"],
            layer,
            substrate,
        )
        mob = compute_w7n_coupling_baseline(
            self.specs["mob"],
            layer,
            substrate,
        )

        np.testing.assert_allclose(cap.mass_rate, const_v.mass_rate, atol=1e-15)
        np.testing.assert_allclose(cap.mass_rate, mob.mass_rate, atol=1e-15)
        np.testing.assert_allclose(
            cap.activation_backreaction,
            const_v.activation_backreaction,
            atol=1e-15,
        )
        np.testing.assert_allclose(
            cap.activation_backreaction,
            mob.activation_backreaction,
            atol=1e-15,
        )
        self.assertEqual(layer_digest, layer.digest())
        self.assertEqual(substrate_digest, substrate.digest())

    def test_mob_is_conservative_but_does_not_protect_a_full_target(self) -> None:
        layer = _layer(-0.5, 0.5)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7n.mob", 1.0, 0.5, 1.0),
            (0.8, 0.2),
        )
        spec = W7MBaselineSpec(
            "mob",
            "baseline.source-mobility.v1",
            "q_i_to_j=lambda*M_i*(1-M_i/C_site)*(1+kappa*dS_ij)",
            1,
            (
                ("eta", 1.0),
                ("initial_mobility", 0.5),
                ("kappa", 0.5),
                ("lambda_sm", 1.0),
                ("site_capacity", 0.8),
            ),
            False,
        )

        result = compute_w7n_coupling_baseline(spec, layer, substrate)

        self.assertAlmostEqual(0.0, math.fsum(result.mass_rate), places=15)
        self.assertGreater(result.mass_rate[0], 0.0)

    def test_lin_f3_and_const_v_adapters_preserve_input_state(self) -> None:
        layer = _layer(-0.4, 0.7)
        substrate = _substrate(
            layer,
            MCMSubstrateArmContract("w7n.adapters", 1.0, 0.4, 0.7),
            (0.35, 0.65),
        )
        layer_digest = layer.digest()
        substrate_digest = substrate.digest()

        for model_id in ("lin", "f3", "const-v"):
            with self.subTest(model_id=model_id):
                result = compute_w7n_coupling_baseline(
                    self.specs[model_id],
                    layer,
                    substrate,
                )
                self.assertEqual(2, len(result.mass_rate))
                self.assertAlmostEqual(0.0, math.fsum(result.mass_rate), places=15)
        self.assertEqual(layer_digest, layer.digest())
        self.assertEqual(substrate_digest, substrate.digest())

    def test_module_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(hasattr(current_api, "advance_w7n_local_baseline"))
        self.assertFalse(hasattr(current_api, "compute_w7n_coupling_baseline"))


if __name__ == "__main__":
    unittest.main()
