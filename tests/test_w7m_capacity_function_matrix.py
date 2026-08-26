from __future__ import annotations

from dataclasses import replace
import math
import unittest

from mcm_field_organism import MCMSubstrateArmContract
from mcm_field_organism.capacity_limited_mcm_f3_runtime import (
    MCMCapacityLimitedRuntimeContract,
    advance_capacity_limited_mcm_f3_shared_field,
)
from mcm_field_organism.w7m_capacity_function_matrix import (
    W7MCapacityFunctionMatrixError,
    ablate_w7m_eta,
    ablate_w7m_kappa,
    align_w7m_fast_state,
    build_w7m_capacity_function_matrix_adapter,
    invert_w7m_kappa,
    measure_w7m_regional_capacity,
    neutralize_w7m_mass,
    transplant_w7m_mass,
)
from tests.test_mcm_f3_runtime import distribution, field, step
from mcm_field_organism import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    activate_mcm_f3_field,
)


class W7MCapacityFunctionMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.adapter = build_w7m_capacity_function_matrix_adapter()

    def test_source_regions_and_matrix_digest_are_frozen_before_runtime(self) -> None:
        adapter = self.adapter

        self.assertEqual(84, len(adapter.initial_field.layer.neurons))
        self.assertIsNone(adapter.initial_field.last_distribution)
        self.assertEqual(
            (38, 34, 12),
            tuple(len(item) for item in adapter.regions.groups),
        )
        self.assertEqual(
            "e88fd217abd969af87e28d4e0faee7364930f6fc3a1f0d21cd908874ca51bbf2",
            adapter.regions.region_digest,
        )
        self.assertEqual(
            "a1e3f8a08fbef760c8f0b147f99cbebfcc05621c2265a70d853dd3d4863ffb6a",
            adapter.matrix_digest,
        )
        self.assertEqual(2.0 / 84.0, adapter.runtime_contract.site_capacity)

    def test_baseline_and_path_inventories_are_complete_and_canonical(self) -> None:
        baselines = {item.model_id: item for item in self.adapter.baselines}

        self.assertEqual(
            {
                "cap",
                "const-v",
                "eta0",
                "f3",
                "kappa0",
                "leak",
                "lin",
                "mob",
                "norm",
                "p0",
                "sat",
                "sign",
            },
            set(baselines),
        )
        self.assertEqual(
            0.5,
            dict(baselines["const-v"].parameter_bindings)["lambda_sm"],
        )
        self.assertFalse(baselines["norm"].organism_runtime_allowed)
        self.assertTrue(baselines["cap"].organism_runtime_allowed)
        self.assertEqual(
            "q_i_to_j=lambda*M_i*(1-M_i/C_site)*(1+kappa*dS_ij)",
            baselines["mob"].equation_contract,
        )
        self.assertEqual(
            ("ab", "ag", "ba", "bg", "ua", "ub", "ug"),
            tuple(item.path_id for item in self.adapter.paths),
        )
        self.assertTrue(all(item.checkpoint_count == 5 for item in self.adapter.paths))

    def test_uniform_regional_ledger_closes_mass_and_free_capacity(self) -> None:
        ledger = measure_w7m_regional_capacity(
            self.adapter.initial_field,
            self.adapter.regions,
            self.adapter.runtime_contract,
        )

        self.assertEqual(1.0, ledger.total_mass)
        self.assertEqual(1.0, ledger.total_free_capacity)
        self.assertAlmostEqual(ledger.a_mass, ledger.a_free_capacity, places=15)
        self.assertAlmostEqual(ledger.b_mass, ledger.b_free_capacity, places=15)
        self.assertAlmostEqual(
            ledger.tied_mass,
            ledger.tied_free_capacity,
            places=15,
        )

    def test_source_adapter_is_exactly_deterministic(self) -> None:
        repeated = build_w7m_capacity_function_matrix_adapter()

        self.assertEqual(self.adapter.matrix_digest, repeated.matrix_digest)
        self.assertEqual(self.adapter.regions, repeated.regions)
        self.assertEqual(self.adapter.baselines, repeated.baselines)
        self.assertEqual(self.adapter.paths, repeated.paths)

    def test_interventions_preserve_capacity_and_renew_binding(self) -> None:
        first, second, contract = self._completed_pair()
        original_mass = first.field.snapshot().substrate_mass
        source_mass = second.field.snapshot().substrate_mass

        aligned = align_w7m_fast_state(first.field, contract)
        neutral = neutralize_w7m_mass(first.field, contract)
        transplanted = transplant_w7m_mass(first.field, second.field, contract)
        eta0 = ablate_w7m_eta(first.field, contract)
        kappa0 = ablate_w7m_kappa(first.field, contract)
        sign = invert_w7m_kappa(first.field, contract)

        self.assertTrue(
            all(
                neuron.activation == 0.0 and neuron.afterimage == 0.0
                for neuron in aligned.field.layer.neurons
            )
        )
        self.assertEqual(original_mass, aligned.field.snapshot().substrate_mass)
        self.assertEqual((0.5, 0.5), neutral.field.snapshot().substrate_mass)
        self.assertEqual(source_mass, transplanted.field.snapshot().substrate_mass)
        self.assertEqual(original_mass, eta0.field.snapshot().substrate_mass)
        self.assertEqual(original_mass, kappa0.field.snapshot().substrate_mass)
        self.assertEqual(original_mass, sign.field.snapshot().substrate_mass)
        self.assertEqual(0.0, eta0.field.substrate.arm.eta)
        self.assertEqual(0.0, kappa0.field.substrate.arm.kappa)
        self.assertEqual(
            -first.field.substrate.arm.kappa,
            sign.field.substrate.arm.kappa,
        )

        for intervention in (aligned, neutral, transplanted, eta0, kappa0, sign):
            self.assertEqual(
                intervention.field.snapshot().digest(),
                intervention.continuation_binding.snapshot_digest,
            )
            self.assertEqual(
                contract.configuration_digest,
                intervention.continuation_binding.configuration_digest,
            )
            self.assertLessEqual(
                max(intervention.field.snapshot().substrate_mass),
                contract.site_capacity,
            )

        continued = advance_capacity_limited_mcm_f3_shared_field(
            neutral.field,
            distribution(10, 20, -0.2, 0.8),
            step(10, 20),
            NeutralLocalFieldSubstrateConfig(1.0),
            NeutralFastAfterimageConfig(0.5),
            contract,
            continuation_binding=neutral.continuation_binding,
        )
        self.assertAlmostEqual(
            1.0,
            math.fsum(continued.field.snapshot().substrate_mass),
            places=12,
        )

    def test_transplant_rejects_different_model_arms(self) -> None:
        first, second, contract = self._completed_pair()
        mismatched = replace(
            second.field,
            substrate=replace(
                second.field.substrate,
                arm=MCMSubstrateArmContract("w7m.other", 0.5, 0.4, 0.75),
            ),
        )

        with self.assertRaisesRegex(
            W7MCapacityFunctionMatrixError,
            "same model arm",
        ):
            transplant_w7m_mass(first.field, mismatched, contract)

    def test_module_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(current_api, "build_w7m_capacity_function_matrix_adapter")
        )

    @staticmethod
    def _completed_pair():
        contract = MCMCapacityLimitedRuntimeContract(0.8)
        config = NeutralLocalFieldSubstrateConfig(1.0)
        afterimage = NeutralFastAfterimageConfig(0.5)

        def completed(auditory: float, visual: float):
            active = activate_mcm_f3_field(
                field(),
                MCMSubstrateArmContract("w7m.test", 0.5, 0.4, 0.75),
            )
            return advance_capacity_limited_mcm_f3_shared_field(
                active,
                distribution(0, 10, auditory, visual),
                step(0, 10),
                config,
                afterimage,
                contract,
            )

        return completed(1.0, -1.0), completed(-0.4, 0.9), contract


if __name__ == "__main__":
    unittest.main()
