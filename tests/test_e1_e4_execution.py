from __future__ import annotations

from dataclasses import replace
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism.e1_e4_baseline_handoffs import (
    E1_E4_CHECKPOINT_IDS,
    E1E4CheckpointEffect,
    E1E4ObservableProfile,
)
from mcm_field_organism.e1_e4_execution import (
    E1_E4_CONTINUITY_ANCHORS,
    E1_E4_EXECUTION_CONTRACT_DIGEST,
    E1_E4_EXECUTION_MODEL_IDS,
    E1E4ExecutionError,
    E1E4ModelRun,
    build_frozen_e1_e4_f3_reader,
    compose_e1_e4_run_result,
    evaluate_e1_e4_run,
    preflight_e1_e4_runners,
    without_e1_e4_f3_backreaction,
)
from mcm_field_organism.mcm_f3_coupling import (
    MCMF3CouplingResult,
    MCMF3LocalRate,
)
from mcm_field_organism.mcm_substrate_state import (
    MCMSubstrateArmContract,
    build_uniform_mcm_substrate,
)
from tests.test_neutral_fast_afterimage import shared_field


def profile(model_id: str, scale: float) -> E1E4ObservableProfile:
    return E1E4ObservableProfile(
        model_id,
        tuple(
            E1E4CheckpointEffect(
                checkpoint_id,
                (scale * (index + 1), scale * 0.5, -scale * 0.25),
                (scale * 0.4, -scale * 0.2, scale * 0.1),
            )
            for index, checkpoint_id in enumerate(E1_E4_CHECKPOINT_IDS)
        ),
    )


def model_run(model_id: str, scale: float, **changes) -> E1E4ModelRun:
    values = dict(
        model_id=model_id,
        parameter_digest="a" * 64,
        profile=profile(model_id, scale),
        observation_schedule_matches=True,
        ablation_controls_hold=True,
        fixed_reader_controls_hold=True,
        invariants_hold=True,
        technically_compatible=True,
        relative_refinement_linf=0.0,
        maximum_mass_or_budget_error=0.0,
        minimum_internal_resource=0.0,
    )
    values.update(changes)
    return E1E4ModelRun(**values)


def runner_matrix(*, explained: bool = True):
    scales = {model_id: 0.2 for model_id in E1_E4_EXECUTION_MODEL_IDS}
    scales["e1"] = 1.0
    scales["b0"] = 0.0
    scales["oracle-g"] = 1.0
    if explained:
        scales["b2"] = 1.0
    return {
        model_id: (lambda model_id=model_id: model_run(model_id, scales[model_id]))
        for model_id in E1_E4_EXECUTION_MODEL_IDS
    }


class E1E4ExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.field = shared_field()
        self.substrate = build_uniform_mcm_substrate(
            self.field.layer,
            MCMSubstrateArmContract("e4.test", 1.0, 0.5, 1.0, 1.0),
        )

    def test_contract_digest_and_runner_order_are_fixed(self) -> None:
        self.assertEqual(64, len(E1_E4_EXECUTION_CONTRACT_DIGEST))
        ordered = preflight_e1_e4_runners(runner_matrix())
        self.assertEqual(len(E1_E4_EXECUTION_MODEL_IDS), len(ordered))

    def test_preflight_rejects_missing_or_extra_runner(self) -> None:
        runners = runner_matrix()
        runners.pop("b6")
        with self.assertRaises(E1E4ExecutionError):
            preflight_e1_e4_runners(runners)
        runners["b6"] = lambda: model_run("b6", 0.2)
        runners["extra"] = lambda: model_run("b6", 0.2)
        with self.assertRaises(E1E4ExecutionError):
            preflight_e1_e4_runners(runners)

    def test_phase_c_wrapper_keeps_rate_and_removes_backreaction(self) -> None:
        def calculator(layer, substrate):
            return MCMF3CouplingResult(
                tuple(
                    MCMF3LocalRate(neuron.neuron_id, index + 0.5, -index - 0.25)
                    for index, neuron in enumerate(layer.neurons)
                )
            )

        original = calculator(self.field.layer, self.substrate)
        intervened = without_e1_e4_f3_backreaction(calculator)(
            self.field.layer, self.substrate
        )
        self.assertEqual(original.mass_rate, intervened.mass_rate)
        self.assertEqual((0.0, 0.0, 0.0), intervened.activation_backreaction)

    def test_frozen_reader_keeps_backreaction_and_zeroes_rate(self) -> None:
        seen = []

        def calculator(layer, substrate):
            seen.append(substrate)
            return MCMF3CouplingResult(
                tuple(
                    MCMF3LocalRate(neuron.neuron_id, index + 1.0, index - 0.5)
                    for index, neuron in enumerate(layer.neurons)
                )
            )

        frozen = build_frozen_e1_e4_f3_reader(calculator, self.substrate)
        result = frozen(self.field.layer, self.substrate)
        self.assertIs(self.substrate, seen[0])
        self.assertEqual((0.0, 0.0, 0.0), result.mass_rate)
        self.assertEqual((-0.5, 0.5, 1.5), result.activation_backreaction)

    def test_frozen_reader_rejects_different_geometry(self) -> None:
        other = replace(self.substrate, edge_inventory_digest="b" * 64)
        frozen = build_frozen_e1_e4_f3_reader(
            lambda layer, substrate: MCMF3CouplingResult(
                tuple(MCMF3LocalRate(item.neuron_id, 0.0, 0.0) for item in layer.neurons)
            ),
            self.substrate,
        )
        with self.assertRaises(E1E4ExecutionError):
            frozen(self.field.layer, other)

    def test_synthetic_matrix_builds_all_profiles_and_distances(self) -> None:
        result = compose_e1_e4_run_result(
            runner_matrix(), E1_E4_CONTINUITY_ANCHORS
        )
        self.assertEqual(E1_E4_EXECUTION_MODEL_IDS, tuple(x.model_id for x in result.model_runs))
        self.assertEqual(6, len(result.baseline_measurements))
        self.assertTrue(result.continuity_anchors_hold)

    def test_incomplete_continuity_anchors_raise_contract_error(self) -> None:
        with self.assertRaises(E1E4ExecutionError):
            compose_e1_e4_run_result(
                runner_matrix(), E1_E4_CONTINUITY_ANCHORS[:-1]
            )

    def test_explaining_baseline_uses_registered_decision(self) -> None:
        result = compose_e1_e4_run_result(
            runner_matrix(explained=True), E1_E4_CONTINUITY_ANCHORS
        )
        self.assertEqual("E4_EXPLAINED_BY_NARROW_BASELINE", evaluate_e1_e4_run(result))

    def test_residual_decision_requires_complete_valid_matrix(self) -> None:
        result = compose_e1_e4_run_result(
            runner_matrix(explained=False), E1_E4_CONTINUITY_ANCHORS
        )
        self.assertEqual("E4_RESIDUAL_AFTER_REGISTERED_BASELINES", evaluate_e1_e4_run(result))

    def test_invalid_precedes_technical_incompatibility(self) -> None:
        runners = runner_matrix(explained=False)
        runners["b3"] = lambda: model_run(
            "b3", 0.2, invariants_hold=False, technically_compatible=False
        )
        result = compose_e1_e4_run_result(runners, E1_E4_CONTINUITY_ANCHORS)
        self.assertEqual("INVALID_E4_RUN", evaluate_e1_e4_run(result))

    def test_technical_incompatibility_precedes_profile_decisions(self) -> None:
        runners = runner_matrix(explained=True)
        runners["b3"] = lambda: model_run("b3", 0.2, technically_compatible=False)
        result = compose_e1_e4_run_result(runners, E1_E4_CONTINUITY_ANCHORS)
        self.assertEqual(
            "TECHNICALLY_INCOMPATIBLE_BASELINE_SET", evaluate_e1_e4_run(result)
        )

    def test_result_has_no_claim_or_embedded_decision_role(self) -> None:
        result = compose_e1_e4_run_result(
            runner_matrix(), E1_E4_CONTINUITY_ANCHORS
        )
        roles = set(result.__dataclass_fields__)
        self.assertTrue(
            {"decision", "memory", "learning", "meaning", "success"}.isdisjoint(roles)
        )

    def test_execution_roles_remain_private(self) -> None:
        for role in (
            "E1E4ModelRun",
            "E1E4BaselineMeasurement",
            "E1E4RunResult",
            "compose_e1_e4_run_result",
            "evaluate_e1_e4_run",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
