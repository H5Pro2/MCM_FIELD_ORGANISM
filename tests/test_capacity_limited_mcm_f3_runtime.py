from __future__ import annotations

import math
import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    MCMF3RuntimeError,
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    ReceptorDistribution,
    SharedMCMField,
    SharedMCMFieldSnapshot,
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field,
    attach_uniform_mcm_substrate,
    restore_shared_mcm_field,
)
from mcm_field_organism.capacity_limited_mcm_f3_runtime import (
    MCMCapacityLimitedRuntimeContract,
    MCMCapacityLimitedRuntimeError,
    advance_capacity_limited_mcm_f3_shared_field,
    advance_capacity_limited_mcm_f3_shared_field_transient,
)
from tests.test_mcm_f3_runtime import (
    distribution,
    field,
    state_vector,
    step,
    transient_inputs,
)


class CapacityLimitedMCMF3RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.substrate_config = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage_config = NeutralFastAfterimageConfig(0.5)
        self.contract = MCMCapacityLimitedRuntimeContract(0.8)

    def active_field(self):
        return activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("w7k.active", 0.5, 0.4, 0.75),
        )

    def test_p0_matches_base_exact_path_and_holds_mass(self) -> None:
        arm = MCMSubstrateArmContract("p0.null", 0.0, 0.5, 2.0)
        expected_initial = attach_uniform_mcm_substrate(field(), arm)
        actual_initial = attach_uniform_mcm_substrate(field(), arm)
        current_distribution = distribution(0, 10, 0.8, -0.4)

        expected = advance_mcm_f3_shared_field(
            expected_initial,
            current_distribution,
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
        )
        actual = advance_capacity_limited_mcm_f3_shared_field(
            actual_initial,
            current_distribution,
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
            self.contract,
        )

        self.assertEqual("p0.exact", actual.capacity_diagnostics.method_id)
        self.assertEqual(2, actual.capacity_diagnostics.validation_count)
        self.assertEqual(
            expected.field.snapshot().digest(),
            actual.field.snapshot().digest(),
        )
        self.assertEqual((0.5, 0.5), actual.field.snapshot().substrate_mass)

    def test_active_runtime_preserves_capacity_mass_and_field_domains(self) -> None:
        result = advance_capacity_limited_mcm_f3_shared_field(
            self.active_field(),
            distribution(0, 10, 1.0, -1.0),
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
            self.contract,
        )

        masses = result.field.snapshot().substrate_mass
        self.assertEqual(
            "w7k.capacity-limited-shared-mcm-field.v1",
            result.capacity_diagnostics.method_id,
        )
        self.assertGreater(result.advance.diagnostics.substep_count, 0)
        self.assertEqual(
            2 + 3 * result.advance.diagnostics.substep_count,
            result.capacity_diagnostics.validation_count,
        )
        self.assertAlmostEqual(1.0, math.fsum(masses), places=12)
        self.assertGreaterEqual(min(masses), 0.0)
        self.assertLessEqual(max(masses), self.contract.site_capacity)
        self.assertGreaterEqual(
            result.capacity_diagnostics.minimum_free_capacity,
            0.0,
        )
        self.assertEqual(
            0.0,
            result.capacity_diagnostics.maximum_capacity_excess,
        )
        self.assertTrue(
            all(
                -1.0 <= neuron.activation <= 1.0
                and -1.0 <= neuron.afterimage <= 1.0
                for neuron in result.field.layer.neurons
            )
        )

    def test_transient_event_path_validates_event_and_commit_boundaries(self) -> None:
        active = self.active_field()
        inputs = transient_inputs(active, 0, 10, contact_at_end=True)
        result = advance_capacity_limited_mcm_f3_shared_field_transient(
            active,
            ReceptorDistribution(CommonFieldTime("organism.f3", 0, 10), ()),
            inputs,
            self.substrate_config,
            self.afterimage_config,
            self.contract,
        )

        masses = result.field.snapshot().substrate_mass
        self.assertEqual((0.5, 0.5), masses)
        self.assertGreaterEqual(
            result.capacity_diagnostics.validation_count,
            3,
        )
        self.assertLessEqual(max(masses), self.contract.site_capacity)

    def test_restore_requires_the_same_external_binding(self) -> None:
        first = advance_capacity_limited_mcm_f3_shared_field(
            self.active_field(),
            distribution(0, 10, 0.9, -0.7),
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
            self.contract,
            refinement=2,
        )
        restored = restore_shared_mcm_field(
            SharedMCMFieldSnapshot.from_json(first.field.snapshot().to_json())
        )

        uninterrupted = advance_capacity_limited_mcm_f3_shared_field(
            first.field,
            distribution(10, 20, -0.2, 0.8),
            step(10, 20),
            self.substrate_config,
            self.afterimage_config,
            self.contract,
            refinement=2,
            continuation_binding=first.continuation_binding,
        )
        resumed = advance_capacity_limited_mcm_f3_shared_field(
            restored,
            distribution(10, 20, -0.2, 0.8),
            step(10, 20),
            self.substrate_config,
            self.afterimage_config,
            self.contract,
            refinement=2,
            continuation_binding=first.continuation_binding,
        )

        self.assertEqual(
            uninterrupted.field.snapshot().digest(),
            resumed.field.snapshot().digest(),
        )
        with self.assertRaisesRegex(
            MCMCapacityLimitedRuntimeError,
            "requires its continuation binding",
        ):
            advance_capacity_limited_mcm_f3_shared_field(
                first.field,
                distribution(10, 20, -0.2, 0.8),
                step(10, 20),
                self.substrate_config,
                self.afterimage_config,
                self.contract,
            )
        with self.assertRaisesRegex(
            MCMCapacityLimitedRuntimeError,
            "configuration does not match",
        ):
            advance_capacity_limited_mcm_f3_shared_field(
                first.field,
                distribution(10, 20, -0.2, 0.8),
                step(10, 20),
                self.substrate_config,
                self.afterimage_config,
                MCMCapacityLimitedRuntimeContract(0.9),
                continuation_binding=first.continuation_binding,
            )

    def test_n_2n_4n_refinement_is_ordered_and_deterministic(self) -> None:
        current_distribution = distribution(0, 10, 0.9, -0.7)
        results = [
            advance_capacity_limited_mcm_f3_shared_field(
                self.active_field(),
                current_distribution,
                step(0, 10),
                self.substrate_config,
                self.afterimage_config,
                self.contract,
                refinement=refinement,
            )
            for refinement in (1, 2, 4)
        ]
        repeated = advance_capacity_limited_mcm_f3_shared_field(
            self.active_field(),
            current_distribution,
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
            self.contract,
            refinement=1,
        )
        coarse_error = np.linalg.norm(
            state_vector(results[0].field) - state_vector(results[1].field)
        )
        fine_error = np.linalg.norm(
            state_vector(results[1].field) - state_vector(results[2].field)
        )

        self.assertGreater(coarse_error, fine_error)
        self.assertEqual(
            results[0].field.snapshot().digest(),
            repeated.field.snapshot().digest(),
        )

    def test_over_capacity_input_is_rejected_before_runtime_commit(self) -> None:
        active = self.active_field()
        masses = tuple(
            MCMSubstrateMass(item.neuron_id, value)
            for item, value in zip(
                active.substrate.masses,
                (0.75, 0.25),
                strict=True,
            )
        )
        over_capacity = SharedMCMField(
            layer=active.layer,
            docks=active.docks,
            last_distribution=active.last_distribution,
            substrate=MCMSubstrateState(
                arm=active.substrate.arm,
                masses=masses,
                edge_inventory_digest=active.substrate.edge_inventory_digest,
            ),
        )
        before = state_vector(over_capacity)

        with self.assertRaisesRegex(
            MCMCapacityLimitedRuntimeError,
            "exceeds the declared site_capacity",
        ):
            advance_capacity_limited_mcm_f3_shared_field(
                over_capacity,
                distribution(0, 10, 1.0, -1.0),
                step(0, 10),
                self.substrate_config,
                self.afterimage_config,
                MCMCapacityLimitedRuntimeContract(0.7),
            )
        np.testing.assert_array_equal(before, state_vector(over_capacity))

    def test_private_stage_validator_is_read_only_and_cannot_return_state(self) -> None:
        active = self.active_field()
        writeable_flags = []

        def observe(activation, afterimage, mass):
            writeable_flags.append(
                (
                    activation.flags.writeable,
                    afterimage.flags.writeable,
                    mass.flags.writeable,
                )
            )

        advance_mcm_f3_shared_field(
            active,
            distribution(0, 10, 1.0, -1.0),
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
            _stage_validator=observe,
        )
        self.assertTrue(writeable_flags)
        self.assertTrue(
            all(flags == (False, False, False) for flags in writeable_flags)
        )

        with self.assertRaisesRegex(
            MCMF3RuntimeError,
            "stage validator must not return state",
        ):
            advance_mcm_f3_shared_field(
                active,
                distribution(0, 10, 1.0, -1.0),
                step(0, 10),
                self.substrate_config,
                self.afterimage_config,
                _stage_validator=lambda *_: object(),
            )

    def test_module_is_not_reexported_from_current_api(self) -> None:
        from mcm_field_organism import current_api

        self.assertFalse(
            hasattr(
                current_api,
                "advance_capacity_limited_mcm_f3_shared_field",
            )
        )


if __name__ == "__main__":
    unittest.main()
