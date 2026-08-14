from __future__ import annotations

from dataclasses import replace
import inspect
import unittest

from mcm_field_organism.e1_common_probe_acceptance_contract import (
    E1CommonProbeAcceptanceContractError,
    build_e1_common_probe_acceptance_contract,
    decide_common_probe_evidence,
)


def metrics(**updates: float) -> dict[str, float]:
    values = {
        "active_s": 1e-3,
        "active_h": 2e-3,
        "coarse_s": 2e-6,
        "coarse_h": 4e-6,
        "fine_s": 1e-6,
        "fine_h": 2e-6,
        "p0_reset_s": 0.0,
        "p0_reset_h": 0.0,
        "feedback_ablation_s": 0.0,
        "feedback_ablation_h": 0.0,
        "formation_ablation_s": 0.0,
        "formation_ablation_h": 0.0,
    }
    values.update(updates)
    return values


class E1CommonProbeAcceptanceContractTests(unittest.TestCase):
    def test_contract_inherits_existing_numerical_rules(self) -> None:
        result = build_e1_common_probe_acceptance_contract()
        self.assertEqual(1e-12, result.absolute_control_tolerance)
        self.assertEqual(8.0, result.strict_signal_margin)
        self.assertEqual(0.01, result.relative_refinement_limit)
        self.assertFalse(result.posthoc_change_permitted)
        self.assertTrue(result.common_probe_implementation_permitted)
        self.assertFalse(result.field_execution_permitted)

    def test_clear_difference_requires_both_components(self) -> None:
        self.assertEqual(
            "NUMERICALLY_CLEAR_STATE_DEPENDENT_COMMON_PROBE_DIFFERENCE",
            decide_common_probe_evidence(**metrics()),
        )
        self.assertEqual(
            "NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE",
            decide_common_probe_evidence(**metrics(active_h=1e-13)),
        )

    def test_nonzero_control_invalidates_decision(self) -> None:
        self.assertEqual(
            "INVALID_COMMON_PROBE_CONTROLS",
            decide_common_probe_evidence(**metrics(p0_reset_s=1.1e-12)),
        )

    def test_zero_active_response_is_a_bounded_null(self) -> None:
        self.assertEqual(
            "NO_MEASURABLE_COMMON_PROBE_DIFFERENCE",
            decide_common_probe_evidence(**metrics(active_s=0.0, active_h=0.0)),
        )

    def test_refinement_failure_is_undecidable(self) -> None:
        self.assertEqual(
            "NUMERICALLY_UNDECIDABLE_COMMON_PROBE_DIFFERENCE",
            decide_common_probe_evidence(**metrics(fine_s=2e-5)),
        )

    def test_changed_bound_fails_closed(self) -> None:
        result = build_e1_common_probe_acceptance_contract()
        with self.assertRaises(E1CommonProbeAcceptanceContractError):
            replace(result, strict_signal_margin=7.0)

    def test_builder_and_decider_contain_no_execution_or_writes(self) -> None:
        source = inspect.getsource(build_e1_common_probe_acceptance_contract)
        source += inspect.getsource(decide_common_probe_evidence)
        for forbidden in (
            "run_neutral_asynchronous_field",
            "run_prepared_real_formation_arm_in_memory",
            "open(",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()
