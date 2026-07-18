from __future__ import annotations

import unittest

from mcm_field_organism import (
    MCMFieldStepTime,
    MCMFieldStepTimeError,
    MCMNeuronDrive,
    MCMNeuronOutput,
    field_step_time_public_roles,
    hold_state_baseline,
)
from tests.test_mcm_neuron_layer import line_layer


class MCMFieldStepTimeTests(unittest.TestCase):
    def test_contract_exposes_measured_duration_without_rounding(self) -> None:
        step_time = MCMFieldStepTime(
            "organism.monotonic_ns",
            1_000_000_000,
            1_125_000_000,
            1_000_000_000,
        )
        self.assertEqual(125_000_000, step_time.elapsed_ticks)
        self.assertEqual(0.125, step_time.elapsed_seconds)

    def test_every_atomic_neuron_proposal_receives_the_same_contract(self) -> None:
        step_time = MCMFieldStepTime("organism.test", 100, 180, 100.0)
        observed: dict[str, MCMFieldStepTime | None] = {}

        def observer(drive: MCMNeuronDrive) -> MCMNeuronOutput:
            observed[drive.previous.neuron_id] = drive.step_time
            return MCMNeuronOutput(
                drive.previous.activation,
                drive.previous.afterimage,
            )

        line_layer().advance(
            {"n.left": 0.1, "n.right": 0.2},
            observer,
            step_time=step_time,
        )
        self.assertEqual(
            {"n.left", "n.center", "n.right"},
            set(observed),
        )
        self.assertTrue(all(value is step_time for value in observed.values()))

    def test_existing_transition_is_unchanged_and_time_is_not_stored(self) -> None:
        layer = line_layer()
        contacts = {"n.left": 0.1, "n.right": 0.2}
        without_time = layer.advance(contacts, hold_state_baseline)
        with_time = layer.advance(
            contacts,
            hold_state_baseline,
            step_time=MCMFieldStepTime("organism.test", 100, 180, 100.0),
        )
        self.assertEqual(without_time.digest(), with_time.digest())
        self.assertFalse(any(
            hasattr(neuron, "step_time") for neuron in with_time.neurons
        ))

    def test_invalid_intervals_and_rates_are_rejected(self) -> None:
        for args in (
            ("organism.test", 10, 10, 100.0),
            ("organism.test", 11, 10, 100.0),
            ("organism.test", 10, 11, 0.0),
        ):
            with self.subTest(args=args):
                with self.assertRaises(MCMFieldStepTimeError):
                    MCMFieldStepTime(*args)

    def test_contract_has_no_activity_relation_or_memory_roles(self) -> None:
        roles = set(field_step_time_public_roles())
        forbidden = {
            "activation",
            "afterimage",
            "contact",
            "weight",
            "relation",
            "memory",
            "topology",
            "meaning",
        }
        self.assertTrue(forbidden.isdisjoint(roles))


if __name__ == "__main__":
    unittest.main()
