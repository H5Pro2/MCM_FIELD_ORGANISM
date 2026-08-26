from __future__ import annotations

from dataclasses import replace
import inspect
from pathlib import Path
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_confirmation_chain_contract import (
    S1_EB4_FORMATION_ARMS,
    S1_EB4_METRICS,
    S1_EB4_PROBE_ARMS,
    prepare_e1_confirmation_chain_contract,
)
from mcm_field_organism.e1_confirmation_result_core import (
    E1ConfirmationRefinementResult,
    E1ConfirmationResultCoreError,
    build_e1_confirmation_chain_result,
)
from mcm_field_organism.e1_refined_confirmation_contract import (
    S1_EB_REFINEMENTS,
)
from mcm_field_organism.e1_refined_world_formation_contract import (
    S1_DS_REQUIRED_CONTROLS,
)


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_refined_formation_transfer_s1ea_once_v1.json"
TARGETS = (
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.attempt.json",
    REPORTS / "e1_refined_confirmation_s1eb_once_v1.lock",
)


def _contract():
    return prepare_e1_confirmation_chain_contract(REPORTS, UPSTREAM)


def _refinement(role: str, factor: int, signal: float):
    return E1ConfirmationRefinementResult(
        refinement_id=role,
        factor=factor,
        formation_state_digests=tuple(
            (name, chr(97 + index) * 64)
            for index, name in enumerate(S1_EB4_FORMATION_ARMS)
        ),
        probe_field_digests=tuple(
            (name, str(index + 1) * 64)
            for index, name in enumerate(S1_EB4_PROBE_ARMS)
        ),
        d_state=signal,
        d_total_binding=signal / 2.0,
        d_probe_s=signal * 0.9,
        d_probe_h=signal * 0.8,
    )


def _result(
    *,
    signals=(0.7, 0.8, 1.0),
    state_residuals=(0.2, 0.1),
    probe_residuals=(0.2, 0.09),
    controls=None,
):
    refinements = tuple(
        _refinement(role, factor, signal)
        for (role, factor), signal in zip(
            S1_EB_REFINEMENTS,
            signals,
            strict=True,
        )
    )
    fine = refinements[-1]
    values = {
        "d_state": fine.d_state,
        "d_total_binding": fine.d_total_binding,
        "d_probe_s": fine.d_probe_s,
        "d_probe_h": fine.d_probe_h,
        "state_refinement_r2_r4": state_residuals[0],
        "state_refinement_r4_r8": state_residuals[1],
        "probe_refinement_r2_r4": probe_residuals[0],
        "probe_refinement_r4_r8": probe_residuals[1],
        "identity_residual": 0.0,
        "formation_ablation_residual": 0.0,
        "probe_ablation_residual": 0.0,
        "fixed_adapter_residual": 0.0,
        "resource_budget_error": 1e-15,
    }
    controls_in = (
        tuple((role, True) for role in S1_DS_REQUIRED_CONTROLS)
        if controls is None
        else controls
    )
    return build_e1_confirmation_chain_result(
        _contract(),
        refinements,
        tuple((role, values[role]) for role in S1_EB4_METRICS),
        controls_in,
    )


class E1ConfirmationResultCoreTests(unittest.TestCase):
    def test_confirmed_decision_uses_strict_fine_residual_rule(self) -> None:
        result = _result()

        self.assertEqual(
            "CONFIRMED_REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
            result.technical_decision,
        )

    def test_zero_decision_requires_all_state_and_probe_signals_zero(self) -> None:
        result = _result(
            signals=(0.0, 0.0, 0.0),
            state_residuals=(0.0, 0.0),
            probe_residuals=(0.0, 0.0),
        )

        self.assertEqual(
            "NO_CONFIRMED_REFINED_EFFECT",
            result.technical_decision,
        )

    def test_boundary_equality_is_numerically_undecidable(self) -> None:
        result = _result(
            signals=(0.7, 0.8, 0.8),
            state_residuals=(0.2, 0.1),
            probe_residuals=(0.2, 0.09),
        )

        self.assertEqual("NUMERICALLY_UNDECIDABLE", result.technical_decision)

    def test_control_failure_has_priority_over_signal(self) -> None:
        controls = tuple(
            (role, index != 0)
            for index, role in enumerate(S1_DS_REQUIRED_CONTROLS)
        )
        result = _result(controls=controls)

        self.assertEqual("TECHNICALLY_INVALID", result.technical_decision)

    def test_decision_metric_and_order_drift_fail_closed(self) -> None:
        result = _result()
        with self.assertRaises(E1ConfirmationResultCoreError):
            replace(result, technical_decision="NUMERICALLY_UNDECIDABLE")
        metrics = dict(result.metrics)
        metrics["identity_residual"] = 0.1
        with self.assertRaisesRegex(
            E1ConfirmationResultCoreError,
            "contradicts",
        ):
            build_e1_confirmation_chain_result(
                _contract(),
                result.refinements,
                tuple((role, metrics[role]) for role in S1_EB4_METRICS),
                result.controls,
            )
        with self.assertRaisesRegex(
            E1ConfirmationResultCoreError,
            "ordered r2, r4, and r8",
        ):
            build_e1_confirmation_chain_result(
                _contract(),
                tuple(reversed(result.refinements)),
                result.metrics,
                result.controls,
            )

    def test_result_and_digest_are_repeatable(self) -> None:
        first = _result()
        second = _result()

        self.assertEqual(first, second)
        self.assertEqual(64, len(first.result_digest))

    def test_incomplete_metric_inventory_fails_as_contract_error(self) -> None:
        result = _result()

        with self.assertRaisesRegex(
            E1ConfirmationResultCoreError,
            "metrics are incomplete",
        ):
            build_e1_confirmation_chain_result(
                _contract(),
                result.refinements,
                result.metrics[:-1],
                result.controls,
            )

    def test_result_core_keeps_registered_paths_free(self) -> None:
        before = tuple(path.exists() for path in TARGETS)
        _result()

        self.assertEqual((False, False, False), before)
        self.assertEqual(before, tuple(path.exists() for path in TARGETS))

    def test_result_core_has_no_runtime_persistence_and_remains_private(self) -> None:
        source = inspect.getsource(build_e1_confirmation_chain_result)
        for forbidden in (
            "run_e1_asynchronous_field",
            "run_private_e1_refined_seven_arm_probe",
            "open(",
            "write_text",
            "write_bytes",
        ):
            self.assertNotIn(forbidden, source)
        for role in (
            "E1ConfirmationRefinementResult",
            "E1ConfirmationChainResult",
            "build_e1_confirmation_chain_result",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
