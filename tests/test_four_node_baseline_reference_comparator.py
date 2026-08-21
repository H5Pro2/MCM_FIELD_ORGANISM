"""S1-SV synthetic tests. Bound here, first execution reserved for S1-SW."""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path
import unittest

from mcm_field_organism.four_node_baseline_reference_comparator import (
    CANDIDATE_NOT_APPLICABLE, COMPUTABLE, CONTRACT_DIGEST, CONTRAST_ROLES,
    INVALID, MODEL_ROLES, PLAN_ROLES, PROFILE_DISTINCT, PROFILE_EQUIVALENT,
    SOURCE_ARTIFACT_DIGEST, SOURCE_MATRIX_RESULT_DIGEST,
    FourNodeBaselineCheckpointVector, build_comparator_input, build_profile,
    compare_four_node_baseline_reference,
)


SHA = "1" * 64
CHECKPOINTS = {
    role: (("PRE_COMPETITION", "POST_COMPETITION", "ALIGNED_PRE_PROBE", "POST_PROBE_READOUT")
           if role.startswith("C_") else ("ALIGNED_PRE_PROBE", "POST_PROBE_READOUT"))
    for role in PLAN_ROLES
}


def synthetic_input():
    profiles = []
    for role_position, model_role in enumerate(MODEL_ROLES, 1):
        checkpoints = []
        for plan_position, plan_role in enumerate(PLAN_ROLES, 1):
            for index, checkpoint_role in enumerate(CHECKPOINTS[plan_role]):
                zero = (0.0, 0.0, 0.0, 0.0)
                checkpoints.append(FourNodeBaselineCheckpointVector(
                    plan_position, plan_role, checkpoint_role, plan_position * 10 + index,
                    f"{plan_position + index:064x}"[-64:], zero, zero, zero,
                    f"{role_position * 100 + plan_position * 4 + index:064x}"[-64:],
                ))
        profiles.append(build_profile(role_position, model_role, SHA, tuple(checkpoints)))
    return build_comparator_input(SOURCE_ARTIFACT_DIGEST, SOURCE_MATRIX_RESULT_DIGEST, tuple(profiles))


def change_profile(source, profile_index, checkpoint_index, *, activation=None,
                   afterimage=None, contact=None, rebuild_input=True):
    profiles = list(source.profiles)
    profile = profiles[profile_index]
    checkpoints = list(profile.checkpoints)
    checkpoints[checkpoint_index] = replace(
        checkpoints[checkpoint_index],
        activation=checkpoints[checkpoint_index].activation if activation is None else activation,
        afterimage=checkpoints[checkpoint_index].afterimage if afterimage is None else afterimage,
        receptor_contact=checkpoints[checkpoint_index].receptor_contact if contact is None else contact,
    )
    profiles[profile_index] = build_profile(profile.role_position, profile.model_role,
                                            profile.configuration_digest, tuple(checkpoints))
    if rebuild_input:
        return build_comparator_input(source.artifact_digest, source.matrix_result_digest, tuple(profiles))
    return replace(source, profiles=tuple(profiles))


class FourNodeBaselineReferenceComparatorTests(unittest.TestCase):
    def test_01_contract_digest_is_bound(self):
        self.assertEqual(CONTRACT_DIGEST, "639cf70ab24892fb0e59e5baaba6c952b99b8ad16c498acf2a399841d44c5a50")

    def test_02_valid_synthetic_input_is_computable(self):
        result = compare_four_node_baseline_reference(synthetic_input())
        self.assertEqual((result.status, result.candidate_gate_status), (COMPUTABLE, CANDIDATE_NOT_APPLICABLE))

    def test_03_complete_output_cardinalities(self):
        result = compare_four_node_baseline_reference(synthetic_input())
        self.assertEqual((len(result.contrasts), len(result.pairs)), (14 * 23, 91))

    def test_04_output_is_deterministic(self):
        self.assertEqual(compare_four_node_baseline_reference(synthetic_input()),
                         compare_four_node_baseline_reference(synthetic_input()))

    def test_05_identical_profiles_are_equivalent(self):
        self.assertTrue(all(pair.status == PROFILE_EQUIVALENT for pair in compare_four_node_baseline_reference(synthetic_input()).pairs))

    def test_06_profile_above_limit_is_distinct(self):
        source = change_profile(synthetic_input(), 1, 1, activation=(1.0, 0.0, 0.0, 0.0))
        pair = compare_four_node_baseline_reference(source).pairs[0]
        self.assertEqual(pair.status, PROFILE_DISTINCT)

    def test_07_relative_metric_below_limit_is_equivalent(self):
        source = synthetic_input()
        source = change_profile(source, 0, 1, activation=(1.0, 0.0, 0.0, 0.0))
        source = change_profile(source, 1, 1, activation=(0.96, 0.0, 0.0, 0.0))
        self.assertEqual(compare_four_node_baseline_reference(source).pairs[0].status, PROFILE_EQUIVALENT)

    def test_08_residual_is_left_minus_right(self):
        source = change_profile(synthetic_input(), 0, 1, activation=(0.75, 0.0, 0.0, 0.0))
        self.assertEqual(compare_four_node_baseline_reference(source).pairs[0].signed_residual[8], 0.75)

    def test_09_full_residual_is_retained(self):
        self.assertTrue(all(len(pair.signed_residual) == 320 for pair in compare_four_node_baseline_reference(synthetic_input()).pairs))

    def test_10_contrast_axis_is_complete_and_ordered(self):
        result = compare_four_node_baseline_reference(synthetic_input())
        self.assertEqual(tuple(item.contrast_role for item in result.contrasts[:23]), CONTRAST_ROLES)

    def test_11_u_released_early_is_diagnostic_only(self):
        result = compare_four_node_baseline_reference(synthetic_input())
        selected = [item for item in result.contrasts if item.contrast_role == "U_RELEASED_EARLY"]
        self.assertTrue(all(item.diagnostic_only for item in selected))

    def test_12_c_delta_uses_post_minus_pre(self):
        source = synthetic_input()
        c_local_pre = next(i for i, cp in enumerate(source.profiles[0].checkpoints) if (cp.plan_role, cp.checkpoint_role) == ("C_LOCAL", "PRE_COMPETITION"))
        c_local_post = next(i for i, cp in enumerate(source.profiles[0].checkpoints) if (cp.plan_role, cp.checkpoint_role) == ("C_LOCAL", "POST_COMPETITION"))
        source = change_profile(source, 0, c_local_pre, activation=(0.25, 0.0, 0.0, 0.0))
        source = change_profile(source, 0, c_local_post, activation=(0.75, 0.0, 0.0, 0.0))
        item = next(x for x in compare_four_node_baseline_reference(source).contrasts if x.model_role == MODEL_ROLES[0] and x.contrast_role == "C_DELTA_LR")
        self.assertEqual(item.activation_residual[0], 0.5)

    def test_13_alignment_difference_fails_closed(self):
        source = change_profile(synthetic_input(), 1, 0, activation=(1e-6, 0.0, 0.0, 0.0))
        result = compare_four_node_baseline_reference(source)
        self.assertEqual((result.status, result.contrasts, result.pairs), (INVALID, (), ()))

    def test_14_public_contact_difference_fails_closed(self):
        source = change_profile(synthetic_input(), 1, 1, contact=(1.0, 0.0, 0.0, 0.0))
        self.assertEqual(compare_four_node_baseline_reference(source).status, INVALID)

    def test_15_missing_model_fails_closed(self):
        source = synthetic_input()
        source = build_comparator_input(source.artifact_digest, source.matrix_result_digest, source.profiles[:-1])
        self.assertEqual(compare_four_node_baseline_reference(source).status, INVALID)

    def test_16_nonfinite_value_fails_closed(self):
        source = synthetic_input()
        profile = source.profiles[0]
        checkpoints = list(profile.checkpoints)
        checkpoints[1] = replace(checkpoints[1], activation=(float("nan"), 0.0, 0.0, 0.0))
        profiles = list(source.profiles)
        profiles[0] = replace(profile, checkpoints=tuple(checkpoints))
        source = replace(source, profiles=tuple(profiles))
        self.assertEqual(compare_four_node_baseline_reference(source).status, INVALID)

    def test_17_stale_input_digest_fails_closed(self):
        source = change_profile(synthetic_input(), 0, 1, activation=(1.0, 0.0, 0.0, 0.0), rebuild_input=False)
        self.assertEqual(compare_four_node_baseline_reference(source).status, INVALID)

    def test_18_invalid_output_contains_no_partial_arrays(self):
        result = compare_four_node_baseline_reference(None)
        self.assertEqual((result.status, result.candidate_gate_status, result.contrasts, result.pairs), (INVALID, None, (), ()))

    def test_19_comparator_has_no_execution_imports(self):
        path = Path(__file__).parents[1] / "mcm_field_organism" / "four_node_baseline_reference_comparator.py"
        imports = {node.module or "" for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))) if isinstance(node, ast.ImportFrom)}
        self.assertFalse(any(any(token in module for token in ("runner", "lifecycle", "fixture", "model_invocation")) for module in imports))


if __name__ == "__main__":
    unittest.main()
