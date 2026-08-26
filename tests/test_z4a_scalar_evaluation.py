from __future__ import annotations

from dataclasses import replace
import math
import unittest

from mcm_field_organism.z4a_scalar_evaluation import (
    ARM_ORDER,
    MODEL_ORDER,
    TECHNICAL_CONTROL_ORDER,
    WORLD_ORDER,
    Z4AComponentMeasurement,
    Z4ADecisionBasis,
    Z4AModelDecisionState,
    Z4AScalarEvaluationError,
    Z4AScalarEvaluationResult,
    Z4ATaskBudget,
    Z4AWorldDecisionState,
    Z4AWorldScalarResult,
    evaluate_z4a_decision,
    z4a_scalar_evaluation_public_roles,
    z4a_scalar_result_json_text,
    z4a_scalar_result_json_value,
)


def controls(*, failed=None):
    return tuple((name, name != failed) for name in TECHNICAL_CONTROL_ORDER)


def world_state(world_id, *, p0=False, f3=False, f3_fast=False, b3=False):
    return Z4AWorldDecisionState(
        world_id,
        (
            Z4AModelDecisionState("p0.exact", True, p0, p0),
            Z4AModelDecisionState("f3.candidate", True, f3, f3_fast),
            Z4AModelDecisionState("b3.linear-coupled", True, b3, b3),
        ),
    )


def states(patterns):
    return tuple(
        world_state(world_id, **pattern)
        for world_id, pattern in zip(WORLD_ORDER, patterns, strict=True)
    )


def not_started_world(world_id):
    digest = "0" * 64
    return Z4AWorldScalarResult(
        world_id,
        "not_started",
        (),
        (),
        (),
        (),
        digest,
        digest,
        0,
        0,
        0,
        0,
        (),
        42,
        0,
        0.0,
    )


def abort_result():
    decision = evaluate_z4a_decision(
        states(({}, {}, {}, {})),
        controls(failed="all_world_bindings_match"),
    )
    return Z4AScalarEvaluationResult(
        "mcm.z4a.multiworld-field-encoder.run197.v1",
        "lauf-197",
        "mcm.z4a.multiworld-field-encoder.v1",
        "z4a.generic-field-trajectory-runner.v1",
        "z4a.multiworld-field-encoder-decision.v1",
        "technical_abort",
        "source_preflight",
        WORLD_ORDER,
        MODEL_ORDER,
        ARM_ORDER,
        (),
        controls(failed="all_world_bindings_match"),
        tuple(not_started_world(world_id) for world_id in WORLD_ORDER),
        Z4ATaskBudget(4, 42, 168, 0),
        decision.overall_decision,
        decision.decision_basis,
    )


class Z4AScalarEvaluationTests(unittest.TestCase):
    def test_technical_failure_has_absolute_precedence(self) -> None:
        decision = evaluate_z4a_decision(
            states(
                (
                    {"f3": True, "f3_fast": True},
                    {"f3": True, "f3_fast": True},
                    {"p0": True},
                    {"b3": True},
                )
            ),
            controls(failed="observer_passive"),
        )
        self.assertEqual(
            "FIELD_ENCODER_NOT_TECHNICALLY_STABLE",
            decision.overall_decision,
        )
        self.assertTrue(
            all(not world_ids for _, world_ids in decision.decision_basis.stable_world_ids_by_model)
        )

    def test_f3_advantage_precedes_other_decisions(self) -> None:
        decision = evaluate_z4a_decision(
            states(
                (
                    {"f3": True, "f3_fast": True},
                    {"f3": True, "f3_fast": True},
                    {},
                    {},
                )
            ),
            controls(),
        )
        self.assertEqual(
            "F3_TECHNICAL_TRAJECTORY_ADVANTAGE",
            decision.overall_decision,
        )
        self.assertEqual(WORLD_ORDER[:2], decision.decision_basis.f3_advantage_world_ids)

    def test_baseline_equivalent_requires_three_world_breadth(self) -> None:
        decision = evaluate_z4a_decision(
            states(({"p0": True}, {"p0": True}, {"p0": True}, {})),
            controls(),
        )
        self.assertEqual(
            "FIELD_ENCODER_CAUSAL_BUT_BASELINE_EQUIVALENT",
            decision.overall_decision,
        )

    def test_no_stable_separation_when_every_model_stays_below_three(self) -> None:
        decision = evaluate_z4a_decision(
            states(({"p0": True}, {"p0": True}, {"b3": True}, {})),
            controls(),
        )
        self.assertEqual(
            "NO_STABLE_CAUSAL_FIELD_SEPARATION",
            decision.overall_decision,
        )

    def test_unregistered_mixed_pattern_remains_unresolved(self) -> None:
        decision = evaluate_z4a_decision(
            states(
                (
                    {"f3": True, "b3": True},
                    {"f3": True},
                    {"f3": True},
                    {},
                )
            ),
            controls(),
        )
        self.assertEqual("Z4A_DECISION_UNRESOLVED", decision.overall_decision)
        self.assertEqual(
            "mixed_stable_separation_not_preregistered",
            decision.decision_basis.unresolved_reason_id,
        )

    def test_envelope_equality_counts_as_within_not_above(self) -> None:
        measurement = Z4AComponentMeasurement(
            "activation",
            1.0,
            None,
            None,
            1e-12,
            1e-12,
            1e-12,
            True,
            False,
        )
        self.assertTrue(measurement.within_comparison_envelope)
        self.assertFalse(measurement.above_comparison_envelope)

    def test_scalar_abort_json_has_exact_top_level_and_no_raw_values(self) -> None:
        result = abort_result()
        value = z4a_scalar_result_json_value(result)
        expected = {
            "schema_id",
            "run_id",
            "preregistration_id",
            "runner_contract_id",
            "decision_contract_id",
            "execution_status",
            "technical_abort_stage",
            "world_order",
            "model_order",
            "arm_order",
            "binding_digests",
            "technical_controls",
            "world_results",
            "task_budget",
            "overall_decision",
            "decision_basis",
            "raw_payload_retained",
            "raw_receptor_sequences_retained",
            "raw_trajectories_retained",
            "memory_claim_allowed",
            "organization_claim_allowed",
            "topology_claim_allowed",
            "semantics_claim_allowed",
            "self_regulation_claim_allowed",
            "ai_claim_allowed",
        }
        self.assertEqual(expected, set(value))
        text = z4a_scalar_result_json_text(result)
        text.encode("ascii")
        for forbidden in (
            '"samples"',
            '"frames"',
            '"full_trajectories"',
            '"activation_vector"',
        ):
            self.assertNotIn(forbidden, text)

    def test_nonfinite_scalar_and_claim_flag_are_rejected(self) -> None:
        with self.assertRaises(Z4AScalarEvaluationError):
            Z4AComponentMeasurement(
                "activation",
                math.nan,
                None,
                None,
                1e-12,
                0.0,
                1e-12,
                True,
                False,
            )
        with self.assertRaises(Z4AScalarEvaluationError):
            replace(abort_result(), ai_claim_allowed=True)

    def test_public_roles_expose_no_raw_trajectory_storage(self) -> None:
        roles = set(z4a_scalar_evaluation_public_roles())
        self.assertTrue(
            {
                "samples",
                "frames",
                "full_trajectories",
                "decision_trajectories",
                "field_vectors",
            }.isdisjoint(roles)
        )


if __name__ == "__main__":
    unittest.main()
