from __future__ import annotations

from dataclasses import replace
import unittest

import numpy as np

from mcm_field_organism import neutral_local_field_substrate as substrate
from mcm_field_organism.previous_state_contribution_hook import (
    apply_previous_state_operator,
    advance_with_previous_state_operator,
)
from mcm_field_organism import (
    CommonFieldTime,
    MCMFieldStepTime,
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    ReceptorContactFrame,
    ReceptorDistributor,
    ReceptorDock,
    ReceptorDockAnatomy,
    advance_neutral_fast_shared_field,
    build_shared_mcm_field,
)


def _fixture():
    frame = ReceptorContactFrame(
        "auditory",
        "auditory.line.v1",
        "contact",
        "auditory.source",
        0,
        10,
        ("carrier.0", "carrier.1", "carrier.2"),
        (0.7, -0.1, 0.4),
    )
    field = build_shared_mcm_field(
        (frame,),
        {
            "auditory": ReceptorDockAnatomy(
                "auditory", "dock.auditory", ((0,), (1,), (2,))
            )
        },
        sample_offsets=((-1,), (1,)),
    )
    neurons = tuple(
        replace(neuron, activation=activation, afterimage=afterimage)
        for neuron, activation, afterimage in zip(
            field.layer.neurons,
            (0.3, -0.2, 0.1),
            (-0.1, 0.25, 0.4),
            strict=True,
        )
    )
    field = replace(field, layer=replace(field.layer, neurons=neurons))
    distributor = ReceptorDistributor()
    distributor.attach(ReceptorDock("dock.auditory", "auditory", "auditory.line.v1"))
    distribution = distributor.distribute(
        (frame,), CommonFieldTime("organism.test", 0, 10)
    )
    return (
        field,
        distribution,
        MCMFieldStepTime("organism.test", 0, 10, 10.0),
        NeutralLocalFieldSubstrateConfig(1.0),
        NeutralFastAfterimageConfig(0.5),
    )


def _state(field) -> np.ndarray:
    return np.asarray(
        [(neuron.activation, neuron.afterimage) for neuron in field.layer.neurons],
        dtype=np.float64,
    )


class PreviousStateContributionHookTests(unittest.TestCase):
    def test_field_operator_zeroes_only_fast_state(self) -> None:
        field, *_ = _fixture()
        none = apply_previous_state_operator(field, previous_state_operator=None)
        identity = apply_previous_state_operator(
            field, previous_state_operator="identity"
        )
        zero = apply_previous_state_operator(field, previous_state_operator="zero")

        self.assertIs(field, none)
        self.assertIs(field, identity)
        self.assertEqual(field.docks, zero.docks)
        self.assertEqual(field.last_distribution, zero.last_distribution)
        self.assertTrue(np.all(_state(zero) == 0.0))
        self.assertFalse(np.all(_state(field) == 0.0))

    def test_none_is_exactly_the_legacy_path(self) -> None:
        args = _fixture()
        legacy = advance_neutral_fast_shared_field(*args)
        hooked = advance_with_previous_state_operator(
            *args, previous_state_operator=None
        )
        self.assertEqual(legacy.snapshot().digest(), hooked.snapshot().digest())

    def test_identity_is_exactly_none(self) -> None:
        args = _fixture()
        none = advance_with_previous_state_operator(
            *args, previous_state_operator=None
        )
        identity = advance_with_previous_state_operator(
            *args, previous_state_operator="identity"
        )
        self.assertEqual(none.snapshot().digest(), identity.snapshot().digest())

    def test_zero_changes_only_the_integrator_initial_condition(self) -> None:
        field, distribution, step_time, config, afterimage_config = _fixture()
        before_digest = field.layer.digest()
        result = advance_with_previous_state_operator(
            field,
            distribution,
            step_time,
            config,
            afterimage_config,
            previous_state_operator="zero",
        )

        generator, boundary = substrate._generator_and_boundary(field, distribution, config)
        eigenvalues, eigenvectors = np.linalg.eigh(generator)
        expected = substrate._integrate_activation_afterimage_with_spectrum(
            np.zeros(len(field.layer.neurons), dtype=np.float64),
            np.zeros(len(field.layer.neurons), dtype=np.float64),
            eigenvalues,
            eigenvectors,
            boundary,
            step_time.elapsed_seconds,
            afterimage_config.time_constant_seconds,
        )
        np.testing.assert_array_equal(_state(result)[:, 0], expected[0])
        np.testing.assert_array_equal(_state(result)[:, 1], expected[1])
        self.assertEqual(before_digest, field.layer.digest())
        self.assertEqual(result.docks, field.docks)
        self.assertEqual(result.last_distribution, distribution)
        self.assertEqual(result.layer.sample_offsets, field.layer.sample_offsets)
        self.assertEqual(result.layer.periodic_axes, field.layer.periodic_axes)

    def test_hook_is_deterministic_and_rejects_other_operators(self) -> None:
        args = _fixture()
        first = advance_with_previous_state_operator(
            *args, previous_state_operator="zero"
        )
        second = advance_with_previous_state_operator(
            *args, previous_state_operator="zero"
        )
        self.assertEqual(first.snapshot().digest(), second.snapshot().digest())
        with self.assertRaisesRegex(ValueError, "None, identity, or zero"):
            advance_with_previous_state_operator(
                *args, previous_state_operator="selective"
            )


if __name__ == "__main__":
    unittest.main()
