from __future__ import annotations

from dataclasses import FrozenInstanceError
import math
import unittest

import mcm_field_organism
from mcm_field_organism import current_api
from mcm_field_organism._acm1h_reference import (
    ACM1H_ATOMIC_RESULT_REQUIRED,
    ACM1H_EDGE_INVENTORY_MISMATCH,
    ACM1H_INVALID_CONFIG,
    ACM1H_INVALID_FIELD_PRESTATE,
    ACM1H_INVALID_STEP_TIME,
    ACM1H_NEGATIVE_EDGE_RATE,
    ACM1H_NODE_IDS,
    ACM1H_PARAMETER_CANDIDATES,
    ACM1H_SHARED_EDGE_COMPOSITION_MISMATCH,
    ACM1H_STEP_TIME_MISMATCH,
    ACM1H_UNSUPPORTED_GEOMETRY,
    ACM1HConfigRecord,
    ACM1HDecisionRecord,
    ACM1HPrestateRecord,
    ACM1HReferenceError,
    acm1h_edge_inventory_digest,
    advance_iag2_gain,
    build_acm1h_off_generator,
    compose_acm1h_proposals,
    run_acm1h_readout_ablation,
    run_acm1h_reference,
    run_acm1h_write_ablation,
)
from mcm_field_organism.field_step_time import MCMFieldStepTime
from mcm_field_organism.shared_mcm_field import SharedMCMFieldSnapshot


def step(start: int = 0, end: int = 1) -> MCMFieldStepTime:
    return MCMFieldStepTime("field-clock", start, end, 1.0)


def prestate(
    activations: tuple[float, ...] = (1.0, 0.5, 0.0, -0.5),
    motif_states: tuple[float, ...] = (0.25, -0.5),
    rates: tuple[float, ...] = (1.0, 1.0, 1.0),
    *,
    start: int = 0,
    end: int = 1,
) -> ACM1HPrestateRecord:
    return ACM1HPrestateRecord(
        "field-acm",
        "open-four-node-line",
        ACM1H_NODE_IDS,
        activations,
        rates,
        motif_states,
        acm1h_edge_inventory_digest(),
        "field-clock",
        start,
        end,
    )


class ACM1HReferenceTests(unittest.TestCase):
    def test_all_six_registered_parameter_candidates_complete(self) -> None:
        self.assertEqual(6, len(ACM1H_PARAMETER_CANDIDATES))
        for gamma_z, beta in ACM1H_PARAMETER_CANDIDATES:
            config = ACM1HConfigRecord(gamma_z, beta)
            result = run_acm1h_reference(config, prestate(), step())
            self.assertEqual("COMPLETED", result.status)
            self.assertIsNone(result.error_code)
            self.assertEqual(64, len(config.digest()))
            self.assertEqual(64, len(result.digest()))

    def test_primary_flows_and_generator_match_the_bound_edge_formula(self) -> None:
        result = run_acm1h_reference(
            ACM1HConfigRecord(0.5, 0.25), prestate(), step()
        )
        self.assertEqual((0.5, 0.5, 0.5), result.edge_fluxes.primary_flows_per_second)
        composition = result.composition
        self.assertIsNotNone(composition)
        assert composition is not None
        for row in composition.generator:
            self.assertAlmostEqual(0.0, sum(row), places=15)
        for first in range(4):
            for second in range(4):
                self.assertEqual(
                    composition.generator[first][second],
                    composition.generator[second][first],
                )

    def test_state_update_is_bounded_directional_and_uses_prestate_readout(self) -> None:
        result = run_acm1h_reference(
            ACM1HConfigRecord(1.0, 0.5),
            prestate(motif_states=(0.0, 0.0)),
            step(),
        )
        for proposal in result.motif_proposals:
            self.assertGreater(proposal.z_next, 0.0)
            self.assertLess(proposal.z_next, 1.0)
            self.assertEqual(1.0, proposal.factor)

        opposite = run_acm1h_reference(
            ACM1HConfigRecord(1.0, 0.5),
            prestate(
                activations=(1.0, 0.5, 1.0, 0.5),
                motif_states=(0.5, -0.5),
            ),
            step(),
        )
        self.assertEqual((-1, -1), tuple(x.parity for x in opposite.motif_proposals))
        self.assertLess(opposite.motif_proposals[0].z_next, 0.5)
        self.assertGreater(opposite.motif_proposals[1].z_next, -1.0)

    def test_single_inactive_edge_holds_state_and_neutralizes_motif_factor(self) -> None:
        result = run_acm1h_reference(
            ACM1HConfigRecord(1.0, 0.5),
            prestate(
                activations=(1.0, 1.0, 0.0, -0.5),
                motif_states=(0.75, -0.25),
            ),
            step(),
        )
        left = result.motif_proposals[0]
        self.assertEqual(0, left.parity)
        self.assertEqual(0.75, left.z_next)
        self.assertEqual(1.0, left.factor)

    def test_all_four_fixed_ablations_have_distinct_exact_oracles(self) -> None:
        config = ACM1HConfigRecord(1.0, 0.5)
        state = prestate(motif_states=(0.25, -0.5))
        active = run_acm1h_reference(config, state, step())

        off_generator = build_acm1h_off_generator(state, step())
        neutral_z = run_acm1h_reference(
            config, prestate(motif_states=(0.0, 0.0)), step()
        )
        readout_off = run_acm1h_readout_ablation(config, state, step())
        write_off = run_acm1h_write_ablation(config, state, step())

        self.assertNotEqual(off_generator, active.composition.generator)
        self.assertEqual((1.0, 1.0), tuple(x.factor for x in neutral_z.motif_proposals))
        self.assertEqual((1.0, 1.0), tuple(x.factor for x in readout_off.motif_proposals))
        self.assertNotEqual(
            state.motif_states,
            tuple(x.z_next for x in readout_off.motif_proposals),
        )
        self.assertEqual(
            state.motif_states,
            tuple(x.z_next for x in write_off.motif_proposals),
        )
        self.assertEqual(
            tuple(x.factor for x in active.motif_proposals),
            tuple(x.factor for x in write_off.motif_proposals),
        )

    def test_shared_edge_is_composed_once_and_order_independently(self) -> None:
        state = prestate()
        result = run_acm1h_reference(ACM1HConfigRecord(1.0, 0.5), state, step())
        composition = result.composition
        assert composition is not None
        left, right = result.motif_proposals
        self.assertEqual(left.factor * right.factor, composition.edge_factors[1])
        self.assertEqual(
            composition.edge_factors[1] * result.edge_fluxes.primary_flows_per_second[1],
            composition.composed_flows_per_second[1],
        )
        reversed_result = compose_acm1h_proposals(
            state, result.edge_fluxes, tuple(reversed(result.motif_proposals))
        )
        self.assertEqual(composition.canonical_payload(), reversed_result.canonical_payload())

    def test_common_sign_reversal_preserves_factors_and_reverses_flows(self) -> None:
        config = ACM1HConfigRecord(0.5, 0.5)
        forward = run_acm1h_reference(config, prestate(), step())
        reverse = run_acm1h_reference(
            config,
            prestate(activations=(-1.0, -0.5, 0.0, 0.5)),
            step(),
        )
        self.assertEqual(
            tuple(x.factor for x in forward.motif_proposals),
            tuple(x.factor for x in reverse.motif_proposals),
        )
        self.assertEqual(
            forward.composition.edge_factors, reverse.composition.edge_factors
        )
        self.assertEqual(
            forward.composition.composed_flows_per_second,
            tuple(-value for value in reverse.composition.composed_flows_per_second),
        )

    def test_line_mirror_swaps_motif_and_outer_edge_roles(self) -> None:
        config = ACM1HConfigRecord(0.5, 0.5)
        forward = run_acm1h_reference(config, prestate(), step())
        mirrored = run_acm1h_reference(
            config,
            prestate(
                activations=(-0.5, 0.0, 0.5, 1.0),
                motif_states=(-0.5, 0.25),
            ),
            step(),
        )
        self.assertEqual(
            tuple(reversed(tuple(x.factor for x in forward.motif_proposals))),
            tuple(x.factor for x in mirrored.motif_proposals),
        )
        self.assertEqual(
            tuple(reversed(forward.composition.edge_factors)),
            mirrored.composition.edge_factors,
        )

    def test_go_histories_separate_acm_and_match_iag2_for_all_candidates(self) -> None:
        flow = 0.5
        for gamma_z, beta in ACM1H_PARAMETER_CANDIDATES:
            z_g = 0.0
            z_o = 0.0
            config = ACM1HConfigRecord(gamma_z, beta)
            history_g = (
                (1.0, 0.5, 0.0, 0.0),
                (0.0, 0.5, 1.0, 1.0),
            )
            history_o = (
                (1.0, 0.5, 1.0, 1.0),
                (0.0, 0.5, 0.0, 0.0),
            )
            for activations in history_g:
                result = run_acm1h_reference(
                    config,
                    prestate(activations=activations, motif_states=(z_g, 0.0)),
                    step(),
                )
                z_g = result.motif_proposals[0].z_next
            for activations in history_o:
                result = run_acm1h_reference(
                    config,
                    prestate(activations=activations, motif_states=(z_o, 0.0)),
                    step(),
                )
                z_o = result.motif_proposals[0].z_next
            theta = 1.0 - math.exp(-gamma_z * flow)
            expected = 1.0 - (1.0 - theta) ** 2
            self.assertAlmostEqual(expected, z_g)
            self.assertAlmostEqual(-expected, z_o)
            self.assertNotEqual(1.0 + beta * z_g, 1.0 + beta * z_o)

            gains_g = [0.0, 0.0]
            gains_o = [0.0, 0.0]
            iag_history_g = ((flow, flow), (-flow, -flow))
            iag_history_o = ((flow, -flow), (-flow, flow))
            for pair in iag_history_g:
                gains_g = [
                    advance_iag2_gain(value, edge_flow, 1.0, gamma_z)
                    for value, edge_flow in zip(gains_g, pair, strict=True)
                ]
            for pair in iag_history_o:
                gains_o = [
                    advance_iag2_gain(value, edge_flow, 1.0, gamma_z)
                    for value, edge_flow in zip(gains_o, pair, strict=True)
                ]
            self.assertEqual(gains_g, gains_o)
            self.assertEqual(
                tuple(1.0 + beta * gain for gain in gains_g),
                tuple(1.0 + beta * gain for gain in gains_o),
            )

    def test_fail_closed_runner_returns_only_one_error_code(self) -> None:
        valid = prestate()
        cases = (
            (object(), valid, step(), ACM1H_INVALID_CONFIG),
            (ACM1HConfigRecord(0.5, 0.5), object(), step(), ACM1H_INVALID_FIELD_PRESTATE),
            (ACM1HConfigRecord(0.5, 0.5), valid, object(), ACM1H_INVALID_STEP_TIME),
            (ACM1HConfigRecord(0.5, 0.5), valid, step(1, 2), ACM1H_STEP_TIME_MISMATCH),
        )
        for config, state, field_step, expected in cases:
            result = run_acm1h_reference(config, state, field_step)
            self.assertEqual("FAILED", result.status)
            self.assertEqual(expected, result.error_code)
            self.assertIsNone(result.edge_fluxes)
            self.assertEqual((), result.motif_proposals)
            self.assertIsNone(result.composition)

    def test_record_constructors_cover_bound_validation_errors(self) -> None:
        with self.assertRaisesRegex(ACM1HReferenceError, ACM1H_INVALID_CONFIG):
            ACM1HConfigRecord(0.0, 0.5)
        with self.assertRaisesRegex(ACM1HReferenceError, ACM1H_UNSUPPORTED_GEOMETRY):
            ACM1HPrestateRecord(
                "field-acm", "wrong", ("a", "b"), (0.0,) * 4, (1.0,) * 3,
                (0.0, 0.0), acm1h_edge_inventory_digest(), "field-clock", 0, 1
            )
        with self.assertRaisesRegex(ACM1HReferenceError, ACM1H_NEGATIVE_EDGE_RATE):
            prestate(rates=(1.0, -1.0, 1.0))
        with self.assertRaisesRegex(ACM1HReferenceError, ACM1H_EDGE_INVENTORY_MISMATCH):
            ACM1HPrestateRecord(
                "field-acm", "open-four-node-line", ACM1H_NODE_IDS, (0.0,) * 4,
                (1.0,) * 3, (0.0, 0.0), "0" * 64, "field-clock", 0, 1
            )

    def test_atomic_decision_rejects_partial_records(self) -> None:
        with self.assertRaisesRegex(
            ACM1HReferenceError, ACM1H_ATOMIC_RESULT_REQUIRED
        ):
            ACM1HDecisionRecord("COMPLETED", None, None, None, None, (), None)

    def test_composition_rejects_missing_motif_without_partial_result(self) -> None:
        state = prestate()
        result = run_acm1h_reference(
            ACM1HConfigRecord(0.5, 0.5), state, step()
        )
        with self.assertRaisesRegex(
            ACM1HReferenceError, ACM1H_SHARED_EDGE_COMPOSITION_MISMATCH
        ):
            compose_acm1h_proposals(
                state, result.edge_fluxes, result.motif_proposals[:1]
            )

    def test_records_are_immutable_and_private_api_remains_unchanged(self) -> None:
        config = ACM1HConfigRecord(0.5, 0.5)
        state = prestate()
        with self.assertRaises(FrozenInstanceError):
            config.beta = 0.25  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            state.motif_states = (0.0, 0.0)  # type: ignore[misc]
        self.assertNotIn("acm", SharedMCMFieldSnapshot.__dataclass_fields__)
        for role in (
            "ACM1HConfigRecord",
            "ACM1HPrestateRecord",
            "run_acm1h_reference",
        ):
            self.assertFalse(hasattr(mcm_field_organism, role))
            self.assertFalse(hasattr(current_api, role))


if __name__ == "__main__":
    unittest.main()
