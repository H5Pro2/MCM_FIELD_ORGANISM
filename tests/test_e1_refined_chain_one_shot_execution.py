from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_refined_chain_one_shot_contract import (
    prepare_e1_refined_chain_one_shot_contract,
)
from mcm_field_organism.e1_refined_chain_one_shot_execution import (
    E1RefinedChainExecutionResult,
    E1RefinedChainOneShotExecutionError,
    E1RefinedChainRefinementResult,
    execute_synthetic_e1_refined_chain_one_shot,
)
from mcm_field_organism.e1_refined_world_formation_contract import (
    S1_DS_METRICS,
    S1_DS_REQUIRED_CONTROLS,
)
from tests.e1_refined_chain_test_paths import make_unused_refined_chain_paths


REPORTS = Path("reports")
UPSTREAM = REPORTS / "e1_frozen_state_transfer_s1dn_once_v1.json"


def refinement(role: str, factor: int, signal: float):
    formation_roles = (
        "ab",
        "ba",
        "ab_identity",
        "ab_formation_ablated",
        "ba_formation_ablated",
    )
    probe_roles = (
        "p0",
        "ab_active",
        "ba_active",
        "ab_probe_ablated",
        "ba_probe_ablated",
        "ab_fixed",
        "ba_fixed",
    )
    return E1RefinedChainRefinementResult(
        refinement_id=role,
        factor=factor,
        formation_state_digests=tuple(
            (name, chr(97 + index) * 64)
            for index, name in enumerate(formation_roles)
        ),
        probe_field_digests=tuple(
            (name, str(index + 1) * 64)
            for index, name in enumerate(probe_roles)
        ),
        d_state=signal,
        d_total_binding=signal / 2.0,
        d_probe_s=signal * 0.8,
        d_probe_h=signal * 0.6,
    )


def synthetic_result(
    *,
    signals=(0.10, 0.09, 0.08),
    state_residuals=(0.02, 0.001),
    probe_residuals=(0.01, 0.0005),
    controls=None,
    decision="REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
):
    refinements = tuple(
        refinement(role, factor, signal)
        for (role, factor), signal in zip(
            (("r1", 1), ("r2", 2), ("r4", 4)),
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
        "state_refinement_r1_r2": state_residuals[0],
        "state_refinement_r2_r4": state_residuals[1],
        "probe_refinement_r1_r2": probe_residuals[0],
        "probe_refinement_r2_r4": probe_residuals[1],
        "identity_residual": 0.0,
        "formation_ablation_residual": 0.0,
        "probe_ablation_residual": 0.0,
        "fixed_adapter_residual": 0.0,
        "resource_budget_error": 1e-15,
    }
    control_values = (
        tuple((role, True) for role in S1_DS_REQUIRED_CONTROLS)
        if controls is None
        else controls
    )
    return E1RefinedChainExecutionResult(
        refinements=refinements,
        metrics=tuple((role, values[role]) for role in S1_DS_METRICS),
        controls=control_values,
        technical_decision=decision,
    )


class E1RefinedChainOneShotExecutionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        global REPORTS, UPSTREAM
        cls._temporary, REPORTS, UPSTREAM = make_unused_refined_chain_paths()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._temporary.cleanup()

    def test_synthetic_result_publishes_once_outside_project_targets(self) -> None:
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            receipt = execute_synthetic_e1_refined_chain_one_shot(
                contract, synthetic_result, root
            )
            report = json.loads(Path(receipt.report_path).read_text(encoding="ascii"))

            self.assertEqual(tuple(report), contract.report_fields)
            self.assertEqual(
                "REFINED_WORLD_FORMATION_AND_TRANSFER_EFFECT",
                receipt.technical_decision,
            )
            self.assertTrue(receipt.synthetic_only)
            self.assertFalse(
                (root / "e1_refined_chain_s1dx_synthetic_once_v1.attempt.json").exists()
            )
            self.assertFalse(
                (root / "e1_refined_chain_s1dx_synthetic_once_v1.lock").exists()
            )
            with self.assertRaisesRegex(
                E1RefinedChainOneShotExecutionError, "already used"
            ):
                execute_synthetic_e1_refined_chain_one_shot(
                    contract, synthetic_result, root
                )

    def test_started_failure_retains_attempt_and_blocks_retry(self) -> None:
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with TemporaryDirectory() as directory:
            root = Path(directory)

            def fail():
                raise RuntimeError("synthetic started failure")

            with self.assertRaisesRegex(RuntimeError, "started failure"):
                execute_synthetic_e1_refined_chain_one_shot(contract, fail, root)
            attempt = root / "e1_refined_chain_s1dx_synthetic_once_v1.attempt.json"
            self.assertTrue(attempt.exists())
            self.assertFalse(
                (root / "e1_refined_chain_s1dx_synthetic_once_v1.lock").exists()
            )
            with self.assertRaisesRegex(
                E1RefinedChainOneShotExecutionError, "already used"
            ):
                execute_synthetic_e1_refined_chain_one_shot(
                    contract, synthetic_result, root
                )

    def test_noncallable_and_project_target_fail_before_attempt(self) -> None:
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                E1RefinedChainOneShotExecutionError, "not callable"
            ):
                execute_synthetic_e1_refined_chain_one_shot(contract, None, root)
            self.assertEqual((), tuple(root.iterdir()))
        with self.assertRaisesRegex(
            E1RefinedChainOneShotExecutionError, "canonical target directory"
        ):
            execute_synthetic_e1_refined_chain_one_shot(
                contract, synthetic_result, REPORTS
            )

    def test_invalid_started_result_retains_attempt(self) -> None:
        contract = prepare_e1_refined_chain_one_shot_contract(REPORTS, UPSTREAM)
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(
                E1RefinedChainOneShotExecutionError, "invalid result"
            ):
                execute_synthetic_e1_refined_chain_one_shot(
                    contract, lambda: object(), root
                )
            self.assertTrue(
                (root / "e1_refined_chain_s1dx_synthetic_once_v1.attempt.json").exists()
            )

    def test_zero_and_undecidable_decisions_follow_rules(self) -> None:
        self.assertEqual(
            "NO_REFINED_WORLD_FORMATION_EFFECT",
            synthetic_result(
                signals=(0.0, 0.0, 0.0),
                state_residuals=(0.0, 0.0),
                probe_residuals=(0.0, 0.0),
                decision="NO_REFINED_WORLD_FORMATION_EFFECT",
            ).technical_decision,
        )
        self.assertEqual(
            "NUMERICALLY_UNDECIDABLE",
            synthetic_result(
                state_residuals=(0.02, 0.02),
                probe_residuals=(0.01, 0.01),
                decision="NUMERICALLY_UNDECIDABLE",
            ).technical_decision,
        )

    def test_control_failure_maps_only_to_technical_invalid(self) -> None:
        controls = tuple(
            (role, index != 0)
            for index, role in enumerate(S1_DS_REQUIRED_CONTROLS)
        )
        result = synthetic_result(
            controls=controls,
            decision="TECHNICALLY_INVALID",
        )
        self.assertEqual("TECHNICALLY_INVALID", result.technical_decision)
        with self.assertRaisesRegex(
            E1RefinedChainOneShotExecutionError, "does not follow"
        ):
            replace(result, technical_decision="NUMERICALLY_UNDECIDABLE")

    def test_metric_control_and_refinement_drift_fail_closed(self) -> None:
        result = synthetic_result()
        metrics = dict(result.metrics)
        metrics["identity_residual"] = 0.1
        with self.assertRaisesRegex(
            E1RefinedChainOneShotExecutionError, "contradicts"
        ):
            replace(
                result,
                metrics=tuple((role, metrics[role]) for role in S1_DS_METRICS),
            )
        with self.assertRaisesRegex(
            E1RefinedChainOneShotExecutionError, "ordered r1, r2, and r4"
        ):
            replace(result, refinements=tuple(reversed(result.refinements)))

    def test_execution_roles_remain_private(self) -> None:
        for role in (
            "E1RefinedChainRefinementResult",
            "E1RefinedChainExecutionResult",
            "E1RefinedChainOneShotReceipt",
            "execute_synthetic_e1_refined_chain_one_shot",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
