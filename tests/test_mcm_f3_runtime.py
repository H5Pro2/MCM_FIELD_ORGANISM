from __future__ import annotations

import unittest

import numpy as np

from mcm_field_organism import (
    CommonFieldTime,
    DistributedReceptorContact,
    MCMF3RuntimeError,
    MCMFieldStepTime,
    MCMSubstrateArmContract,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    ReceptorContactFrame,
    ReceptorDistribution,
    ReceptorDockAnatomy,
    SharedMCMFieldError,
    SharedMCMFieldSnapshot,
    TransientLocalReceptorContact,
    TransientNeuronDockInput,
    TransientNeuronInputSet,
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field,
    advance_mcm_f3_shared_field_transient,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
    attach_uniform_mcm_substrate,
    build_shared_mcm_field,
    restore_shared_mcm_field,
)


def frame(modality: str, value: float, index: int = 0) -> ReceptorContactFrame:
    return ReceptorContactFrame(
        modality_id=modality,
        geometry_id=f"{modality}.geometry.v1",
        snapshot_id=f"{modality}.snapshot.{index}",
        clock_id=f"{modality}.source",
        window_start_tick=index,
        window_end_tick=index + 1,
        carrier_ids=(f"{modality}.carrier.0",),
        values=(value,),
    )


def field():
    return build_shared_mcm_field(
        (frame("auditory", 0.0), frame("visual", 0.0)),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory",
                "dock.auditory",
                ((0,),),
            ),
            "visual": ReceptorDockAnatomy(
                "visual",
                "dock.visual",
                ((1,),),
            ),
        },
        sample_offsets=((-1,), (1,)),
    )


def distribution(start: int, end: int, auditory: float, visual: float):
    return ReceptorDistribution(
        CommonFieldTime("organism.f3", start, end),
        (
            DistributedReceptorContact(
                "dock.auditory",
                frame("auditory", auditory, start),
            ),
            DistributedReceptorContact(
                "dock.visual",
                frame("visual", visual, start),
            ),
        ),
    )


def step(start: int, end: int):
    return MCMFieldStepTime("organism.f3", start, end, 10.0)


def state_vector(current) -> np.ndarray:
    return np.asarray(
        [
            *(neuron.activation for neuron in current.layer.neurons),
            *(neuron.afterimage for neuron in current.layer.neurons),
            *(item.mass for item in current.substrate.masses),
        ],
        dtype=np.float64,
    )


def transient_inputs(current, start: int, end: int, *, contact_at_end: bool):
    field_step = step(start, end)
    values = []
    for dock in current.docks:
        carrier_id, neuron_id = dock.dock_map.pairs[0]
        contacts = ()
        if dock.dock_id == "dock.auditory" and contact_at_end:
            contacts = (
                TransientLocalReceptorContact(
                    snapshot_id=f"auditory.transient.{end}",
                    source_clock_id="auditory.source",
                    source_window_start_tick=start,
                    source_window_end_tick=end,
                    organism_read_time=CommonFieldTime(
                        "organism.f3",
                        end - 1,
                        end,
                    ),
                    value=1.0,
                ),
            )
        values.append(
            TransientNeuronDockInput(
                neuron_id=neuron_id,
                dock_id=dock.dock_id,
                carrier_id=carrier_id,
                step_time=field_step,
                contacts=contacts,
            )
        )
    return TransientNeuronInputSet(field_step, tuple(values))


class MCMF3RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.substrate_config = NeutralLocalFieldSubstrateConfig(1.0)
        self.afterimage_config = NeutralFastAfterimageConfig(0.5)

    def test_p0_continuous_path_is_the_existing_exact_fast_path(self) -> None:
        legacy = field()
        null = attach_uniform_mcm_substrate(
            field(),
            MCMSubstrateArmContract("p0.null", 0.0, 0.5, 2.0),
        )
        current_distribution = distribution(0, 10, 0.8, -0.4)

        expected = advance_neutral_fast_shared_field(
            legacy,
            current_distribution,
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
        )
        actual = advance_mcm_f3_shared_field(
            null,
            current_distribution,
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
        )

        self.assertEqual("p0.exact", actual.diagnostics.method_id)
        self.assertEqual(0, actual.diagnostics.substep_count)
        self.assertEqual(
            expected.snapshot().digest(),
            actual.field.snapshot().fast_state_projection_digest(),
        )

    def test_active_ssprk_preserves_mass_positivity_and_field_intervals(self) -> None:
        active = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("p1.active", 0.5, 0.5, 0.75),
        )

        result = advance_mcm_f3_shared_field(
            active,
            distribution(0, 10, 1.0, -1.0),
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
        )

        self.assertEqual("ssprk33", result.diagnostics.method_id)
        self.assertGreater(result.diagnostics.substep_count, 0)
        self.assertLessEqual(
            result.diagnostics.maximum_step_seconds,
            result.diagnostics.safe_step_seconds,
        )
        self.assertLessEqual(result.diagnostics.maximum_mass_error, 1e-12)
        self.assertGreaterEqual(result.diagnostics.minimum_mass, 0.0)
        self.assertAlmostEqual(1.0, result.field.substrate.total_mass, places=12)
        self.assertTrue(
            all(-1.0 <= neuron.activation <= 1.0 for neuron in result.field.layer.neurons)
        )
        self.assertTrue(
            all(-1.0 <= neuron.afterimage <= 1.0 for neuron in result.field.layer.neurons)
        )
        self.assertNotEqual((0.5, 0.5), result.field.snapshot().substrate_mass)

    def test_eta_ablation_changes_s_but_keeps_the_same_initial_nature_contract(self) -> None:
        active = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("p1.active", 0.5, 0.5, 1.0),
        )
        eta_null = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("b.eta-null", 0.5, 0.5, 0.0),
        )
        current_distribution = distribution(0, 10, 1.0, -1.0)

        coupled = advance_mcm_f3_shared_field(
            active,
            current_distribution,
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
            refinement=2,
        ).field
        one_way = advance_mcm_f3_shared_field(
            eta_null,
            current_distribution,
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
            refinement=2,
        ).field

        self.assertFalse(
            np.array_equal(
                [item.activation for item in coupled.layer.neurons],
                [item.activation for item in one_way.layer.neurons],
            )
        )

    def test_n_2n_4n_refinement_is_ordered(self) -> None:
        initial = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("p1.active", 0.5, 0.4, 0.75),
        )
        current_distribution = distribution(0, 10, 0.9, -0.7)
        results = [
            advance_mcm_f3_shared_field(
                initial,
                current_distribution,
                step(0, 10),
                self.substrate_config,
                self.afterimage_config,
                refinement=refinement,
            ).field
            for refinement in (1, 2, 4)
        ]
        coarse_error = np.linalg.norm(state_vector(results[0]) - state_vector(results[1]))
        fine_error = np.linalg.norm(state_vector(results[1]) - state_vector(results[2]))

        self.assertGreater(coarse_error, 0.0)
        self.assertGreater(fine_error, 0.0)
        self.assertLess(fine_error, coarse_error)

    def test_schema_two_restore_has_the_same_next_active_boundary(self) -> None:
        initial = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("p1.active", 0.5, 0.4, 0.75),
        )
        first = advance_mcm_f3_shared_field(
            initial,
            distribution(0, 10, 0.9, -0.7),
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
            refinement=2,
        ).field
        restored = restore_shared_mcm_field(
            SharedMCMFieldSnapshot.from_json(first.snapshot().to_json())
        )

        uninterrupted = advance_mcm_f3_shared_field(
            first,
            distribution(10, 20, -0.2, 0.8),
            step(10, 20),
            self.substrate_config,
            self.afterimage_config,
            refinement=2,
        ).field
        resumed = advance_mcm_f3_shared_field(
            restored,
            distribution(10, 20, -0.2, 0.8),
            step(10, 20),
            self.substrate_config,
            self.afterimage_config,
            refinement=2,
        ).field

        self.assertEqual(uninterrupted.snapshot().digest(), resumed.snapshot().digest())

    def test_diagnostics_are_not_persisted_in_schema_two(self) -> None:
        active = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("p1.active", 0.5, 0.4, 0.75),
        )
        result = advance_mcm_f3_shared_field(
            active,
            distribution(0, 10, 0.9, -0.7),
            step(0, 10),
            self.substrate_config,
            self.afterimage_config,
        )
        encoded = result.field.snapshot().to_json()

        for forbidden in (
            "diagnostics",
            "substep_count",
            "safe_step_seconds",
            "maximum_mass_error",
            "refinement",
        ):
            self.assertNotIn(forbidden, encoded)

    def test_active_substrate_cannot_bypass_the_coupled_runtime(self) -> None:
        active = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("p1.active", 0.5, 0.4, 0.75),
        )
        with self.assertRaisesRegex(SharedMCMFieldError, "dedicated F3"):
            active.advance(distribution(0, 10, 1.0, -1.0), lambda drive: None)

    def test_transient_event_does_not_change_m_until_later_field_time(self) -> None:
        active = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("p1.active", 0.5, 0.5, 0.75),
        )
        first_inputs = transient_inputs(active, 0, 10, contact_at_end=True)
        first = advance_mcm_f3_shared_field_transient(
            active,
            ReceptorDistribution(CommonFieldTime("organism.f3", 0, 10), ()),
            first_inputs,
            self.substrate_config,
            self.afterimage_config,
        ).field

        self.assertEqual((0.5, 0.5), first.snapshot().substrate_mass)
        self.assertNotEqual((0.0, 0.0), tuple(item.activation for item in first.layer.neurons))

        second_inputs = transient_inputs(first, 10, 20, contact_at_end=False)
        second = advance_mcm_f3_shared_field_transient(
            first,
            ReceptorDistribution(CommonFieldTime("organism.f3", 10, 20), ()),
            second_inputs,
            self.substrate_config,
            self.afterimage_config,
        ).field

        self.assertNotEqual((0.5, 0.5), second.snapshot().substrate_mass)
        self.assertAlmostEqual(1.0, second.substrate.total_mass, places=12)

    def test_p0_transient_path_is_the_existing_exact_fast_path(self) -> None:
        legacy = field()
        null = attach_uniform_mcm_substrate(
            field(),
            MCMSubstrateArmContract("p0.null", 0.0, 0.5, 2.0),
        )
        inputs = transient_inputs(null, 0, 10, contact_at_end=True)
        contact_free = ReceptorDistribution(CommonFieldTime("organism.f3", 0, 10), ())

        expected = advance_neutral_fast_shared_field_transient(
            legacy,
            contact_free,
            inputs,
            self.substrate_config,
            self.afterimage_config,
        )
        actual = advance_mcm_f3_shared_field_transient(
            null,
            contact_free,
            inputs,
            self.substrate_config,
            self.afterimage_config,
        )

        self.assertEqual("p0.exact", actual.diagnostics.method_id)
        self.assertEqual(
            expected.snapshot().digest(),
            actual.field.snapshot().fast_state_projection_digest(),
        )

    def test_invalid_refinement_is_rejected_before_integration(self) -> None:
        active = activate_mcm_f3_field(
            field(),
            MCMSubstrateArmContract("p1.active", 0.5, 0.4, 0.75),
        )
        for refinement in (0, -1, True):
            with self.subTest(refinement=refinement), self.assertRaises(
                MCMF3RuntimeError
            ):
                advance_mcm_f3_shared_field(
                    active,
                    distribution(0, 10, 0.9, -0.7),
                    step(0, 10),
                    self.substrate_config,
                    self.afterimage_config,
                    refinement=refinement,
                )


if __name__ == "__main__":
    unittest.main()
