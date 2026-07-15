from __future__ import annotations

from dataclasses import fields
import unittest

from mcm_field_organism import (
    AuditoryFieldFunctionProbeResult,
    BaselineValidationError,
    compensated_transition_histories,
    run_auditory_field_function_probe,
)


class AuditoryFieldFunctionProbeTests(unittest.TestCase):
    def test_compensated_histories_collide_in_b0_b1_and_global_energy(self) -> None:
        for dt, tau in ((0.01, 0.05), (0.02, 0.2), (0.1, 1.0)):
            result = run_auditory_field_function_probe(dt=dt, tau=tau)
            self.assertTrue(result.current_contact_equal)
            self.assertTrue(result.stateless_equal)
            self.assertTrue(result.independent_leaky_equal)
            self.assertTrue(result.global_energy_chronology_equal)

    def test_fixed_one_step_delay_already_separates_the_histories(self) -> None:
        result = run_auditory_field_function_probe(dt=0.01, tau=0.05)
        self.assertFalse(result.fixed_one_step_delay_equal)

    def test_histories_reverse_carrier_order_without_changing_step_totals(self) -> None:
        forward, reverse = compensated_transition_histories(dt=0.01, tau=0.05)
        self.assertEqual(forward[0], tuple(reversed(reverse[0])))
        self.assertEqual(forward[1], tuple(reversed(reverse[1])))
        self.assertEqual(forward[-1], reverse[-1])
        self.assertEqual(
            tuple(sum(frame) for frame in forward),
            tuple(sum(frame) for frame in reverse),
        )

    def test_result_is_immutable_and_declares_only_passive_comparisons(self) -> None:
        result = run_auditory_field_function_probe(dt=0.01, tau=0.05)
        with self.assertRaises((AttributeError, TypeError)):
            result.decay = 0.0  # type: ignore[misc]
        forbidden = {
            "mcm_activation",
            "mcm_afterimage",
            "coupling",
            "relationship",
            "meaning",
            "pattern_class",
            "reward",
        }
        self.assertTrue(forbidden.isdisjoint(item.name for item in fields(result)))
        self.assertIsInstance(result, AuditoryFieldFunctionProbeResult)

    def test_invalid_probe_domains_are_rejected(self) -> None:
        invalid = (
            (),
            (0.1,),
            (0.1, 0.2, 0.3),
            (-0.1, 0.2),
            (0.1, 1.1),
            (float("nan"), 0.2),
        )
        for probe in invalid:
            with self.assertRaises(BaselineValidationError):
                compensated_transition_histories(
                    dt=0.01,
                    tau=0.05,
                    common_probe=probe,
                )


if __name__ == "__main__":
    unittest.main()
