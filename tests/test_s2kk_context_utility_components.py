"""Fourteen focused neutral qualification tests for S2-KK components."""

from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
import hashlib
from pathlib import Path
import unittest

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2kj_two_area_perceptual_context_336 as context336
from tools import _s2kj_validated_perceptual_finding_336 as finding336
from tools import _s2jw_profiled_memory_read_only as read_only
from tools import _s2kk_context_utility_baselines as baselines
from tools import _s2kk_context_utility_evaluator as evaluator
from tools import _s2kk_context_utility_fixtures as fixtures
from tools import _s2kk_visual_context_consumer as consumer
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile


ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_ID = "s2kk-components-qualification-20260903-01"


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _visual_values(common: int, variable: int) -> tuple[float, ...]:
    return (0.0,) * 32 + (common / 255.0,) * 128 + (variable / 255.0,) * 128


def _masked_probe(visible: float = 0.0) -> fixtures.MaskedVisualPerception336V1:
    values: tuple[float | None, ...] = (visible,) * 32 + (None,) * 256
    payload = {
        "schema": fixtures.S2KK_MASKED_SCHEMA,
        "contract_digest": fixtures.S2KK_CONTRACT_DIGEST,
        "source_fixture_digest": _sha(f"masked-fixture-{visible}"),
        "source_pairing_digest": _sha(f"masked-pair-{visible}"),
        "raw_visual_values_digest": _sha(f"masked-visual-{visible}"),
        "auditory_values_digest": _sha("masked-auditory"),
        "mask_plan_digest": fixtures.MASK_PLAN_DIGEST,
        "values": list(values),
        "visible_positions": list(fixtures.VISIBLE_POSITIONS),
        "masked_positions": list(fixtures.MASKED_POSITIONS),
    }
    return fixtures._validate_masked(
        fixtures.MaskedVisualPerception336V1(
            payload["source_fixture_digest"],
            payload["source_pairing_digest"],
            payload["raw_visual_values_digest"],
            payload["auditory_values_digest"],
            fixtures.MASK_PLAN_DIGEST,
            values,
            fixtures.VISIBLE_POSITIONS,
            fixtures.MASKED_POSITIONS,
            fixtures._digest(payload),
        )
    )


def _context(visual_values: tuple[float, ...] | None) -> context336.TwoAreaPerceptualContext336:
    state_digest = _sha("neutral-state")
    probe_digest = _sha("neutral-full-probe")
    source_digest = _sha("neutral-source")
    source_finding_digest = _sha("neutral-source-finding")
    roles = []
    for role in finding336.ROLE_ORDER:
        candidate = None
        reason = "NO_OCCUPIED_SOURCE"
        if role == "B_STABLE_VISUAL" and visual_values is not None:
            observation = read_only.S2JVSlowObservationV1(
                "visual",
                "visual-slot-0",
                3,
                True,
                0.0,
                True,
                _sha("visual-slot"),
            )
            candidate = finding336._make_stable_candidate(
                role,
                observation,
                visual_values,
                state_digest,
                probe_digest,
                source_digest,
            )
            reason = None
        roles.append(
            finding336._make_role_finding(
                role,
                candidate,
                reason,
                state_digest,
                probe_digest,
                source_finding_digest,
            )
        )
    candidate_count = 1 if visual_values is not None else 0
    referenced = 288 if visual_values is not None else 0
    payload = {
        "schema": finding336.S2KJ_BINDING_SCHEMA,
        "config_digest": _sha("neutral-config"),
        "composite_state_digest": state_digest,
        "probe_digest": probe_digest,
        "source_digest": source_digest,
        "auditory_source_digest": _sha("neutral-auditory-source"),
        "visual_source_digest": _sha("neutral-visual-source"),
        "source_time_geometry_digest": _sha("neutral-time-geometry"),
        "source_finding_digest": source_finding_digest,
        "role_finding_digests": [item.finding_digest for item in roles],
        "prestate_digest": state_digest,
        "poststate_digest": state_digest,
        "source_ledger_digest": _sha("neutral-ledger"),
        "candidate_count": candidate_count,
        "referenced_value_count": referenced,
    }
    bound = finding336.ValidatedPerceptualFinding336V1(
        payload["config_digest"],
        state_digest,
        probe_digest,
        source_digest,
        payload["auditory_source_digest"],
        payload["visual_source_digest"],
        payload["source_time_geometry_digest"],
        source_finding_digest,
        tuple(roles),
        state_digest,
        state_digest,
        payload["source_ledger_digest"],
        candidate_count,
        referenced,
        finding336._digest(payload),
    )
    return context336.project_two_area_perceptual_context_336(bound)


def _trained_baselines() -> tuple[
    baselines.S2KKBaselineStateV1,
    baselines.BaselineProbe336V1,
    tuple[baselines.BaselineRetrieval336V1, ...],
]:
    auditory = (0.5,) * 48
    plus = _visual_values(132, 130)
    minus = _visual_values(132, 126)
    distractor = (1.0,) * 288
    state = baselines.initial_baseline_state()
    for ordinal in range(1, 18):
        visual = plus if ordinal <= 2 else minus if ordinal <= 8 else distractor
        training = baselines.bind_training_input(
            formation_ordinal=ordinal,
            auditory_values=auditory if ordinal <= 8 else (1.0,) * 48,
            visual_values=visual,
            source_digest=_sha(f"neutral-training-{ordinal:02d}"),
        )
        state = baselines.advance_baselines(state, training)
    probe = baselines.bind_full_probe(
        auditory_values=auditory,
        visual_values=_visual_values(128, 128),
        source_digest=_sha("neutral-full-probe-source"),
    )
    return state, probe, baselines.probe_baselines(state, probe)


class S2KKContextUtilityComponentsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.masked = _masked_probe()
        cls.baseline_state, cls.full_probe, retrievals = _trained_baselines()
        cls.frozen_retrieval, cls.replay_retrieval, cls.adaptive_retrieval = retrievals
        cls.frozen = baselines.complete_from_baseline(
            retrieval=cls.frozen_retrieval,
            masked_probe=cls.masked,
        )
        cls.replay = baselines.complete_from_baseline(
            retrieval=cls.replay_retrieval,
            masked_probe=cls.masked,
        )
        cls.direct = baselines.complete_from_baseline(
            retrieval=cls.adaptive_retrieval,
            masked_probe=cls.masked,
        )
        assert cls.baseline_state.adaptive_visual is not None
        cls.context = _context(cls.baseline_state.adaptive_visual)
        cls.empty_context = _context(None)
        cls.current = consumer.current_perception_only(cls.masked)
        cls.context_result = consumer.consume_b_stable_visual(
            probe=cls.masked,
            context=cls.context,
            requested_role=consumer.REQUESTED_ROLE,
        )
        cls.target = evaluator.bind_evaluation_target(
            visual_values=_visual_values(128, 128),
            visual_payload_digest=_sha("evaluation-only-target-frame"),
            evaluation_plan_digest=_sha("sealed-evaluation-plan"),
        )

    def test_01_mask_is_independent_literal_and_has_bound_geometry(self) -> None:
        self.assertEqual((32, 256), (len(fixtures.VISIBLE_POSITIONS), len(fixtures.MASKED_POSITIONS)))
        self.assertEqual(tuple(range(32)), fixtures.VISIBLE_POSITIONS)
        self.assertEqual(tuple(range(32, 288)), fixtures.MASKED_POSITIONS)
        self.assertNotEqual(self.masked.raw_visual_values_digest, self.masked.mask_plan_digest)
        with self.assertRaises(fixtures.S2KKFixtureError):
            fixtures._validate_masked(replace(self.masked, mask_plan_digest=_sha("derived-mask")))

    def test_02_real_visual_receptor_materializes_bound_geometry(self) -> None:
        receptor = LocalChannelGridReceptor(VisualGridConfig())
        plus = tuple(receptor.analyze(fixtures._visual_image("T_PLUS"), frame_index=0).channel_values)
        minus = tuple(receptor.analyze(fixtures._visual_image("T_MINUS"), frame_index=1).channel_values)
        holdout = tuple(receptor.analyze(fixtures._visual_image("H_FULL"), frame_index=2).channel_values)
        self.assertEqual(_visual_values(132, 130), plus)
        self.assertEqual(_visual_values(132, 126), minus)
        self.assertEqual(_visual_values(128, 128), holdout)
        self.assertAlmostEqual(8 / 765, baselines._distance(holdout, plus), places=15)
        self.assertAlmostEqual(16 / 2295, baselines._distance(plus, minus), places=15)

    def test_03_real_masked_source_binds_only_with_independent_mask(self) -> None:
        stream = fixtures.S2KKFixtureStream(build_s2jw_default_live_profile())
        source = stream.materialize("H_MASKED", 0)
        masked = fixtures.bind_masked_visual_perception(
            source,
            mask_plan_digest=fixtures.MASK_PLAN_DIGEST,
        )
        self.assertEqual((0.0,) * 32, masked.values[:32])
        self.assertEqual((None,) * 256, masked.values[32:])
        with self.assertRaises(fixtures.S2KKFixtureError):
            fixtures.bind_masked_visual_perception(source, mask_plan_digest=_sha("wrong-mask"))

    def test_04_independent_baselines_match_only_after_adaptation(self) -> None:
        self.assertEqual(17, self.baseline_state.formation_count)
        self.assertEqual(3, self.baseline_state.adaptive_support)
        self.assertEqual(("NO_MATCH", "NO_MATCH", "MATCH"), tuple(
            item.status for item in (
                self.frozen_retrieval,
                self.replay_retrieval,
                self.adaptive_retrieval,
            )
        ))
        self.assertGreater(self.frozen_retrieval.visual_distance, baselines.VISUAL_THRESHOLD)
        self.assertLessEqual(self.adaptive_retrieval.visual_distance, baselines.VISUAL_THRESHOLD)

    def test_05_current_only_never_infers_masked_values(self) -> None:
        self.assertEqual("INSUFFICIENT_INFORMATION", self.current.status)
        self.assertEqual((), self.current.completed_positions)
        self.assertEqual((None,) * 256, self.current.output_values[32:])
        self.assertIsNone(self.current.context_bundle_digest)

    def test_06_explicit_visual_b_context_fills_only_masked_positions(self) -> None:
        result = self.context_result
        self.assertEqual("COMPLETED", result.status)
        self.assertEqual(consumer.REQUESTED_ROLE, result.requested_role)
        self.assertEqual(fixtures.MASKED_POSITIONS, result.completed_positions)
        self.assertEqual(self.masked.values[:32], result.output_values[:32])
        self.assertEqual(self.context.b_stable.visual.candidate.values[32:], result.output_values[32:])
        self.assertEqual((32, 256), (result.visible_compare_count, result.masked_copy_count))

    def test_07_absent_or_unbound_context_fails_without_fallback(self) -> None:
        absent = consumer.consume_b_stable_visual(
            probe=self.masked,
            context=self.empty_context,
            requested_role=consumer.REQUESTED_ROLE,
        )
        self.assertEqual("CONTEXT_ABSENT", absent.status)
        self.assertEqual((None,) * 256, absent.output_values[32:])
        with self.assertRaises(consumer.S2KKConsumerError):
            consumer.consume_b_stable_visual(
                probe=self.masked,
                context=self.context,
                requested_role="A_RECENT",
            )

    def test_08_visible_conflict_causes_no_partial_fill(self) -> None:
        conflicting = _masked_probe(1 / 255)
        result = consumer.consume_b_stable_visual(
            probe=conflicting,
            context=self.context,
            requested_role=consumer.REQUESTED_ROLE,
        )
        self.assertEqual("VISIBLE_CONFLICT", result.status)
        self.assertEqual((), result.completed_positions)
        self.assertEqual((None,) * 256, result.output_values[32:])

    def test_09_direct_baseline_is_independent_and_equals_context_output(self) -> None:
        source = (ROOT / "tools/_s2kk_context_utility_baselines.py").read_text(encoding="ascii")
        self.assertNotIn("_s2kk_visual_context_consumer", source)
        self.assertEqual("COMPLETED", self.direct.status)
        self.assertEqual(self.context_result.output_values, self.direct.output_values)
        self.assertEqual(self.context_result.completed_positions, self.direct.completed_positions)

    def test_10_posthoc_evaluation_confirms_limited_utility(self) -> None:
        result = evaluator.evaluate_context_utility(
            current_only=self.current,
            frozen=self.frozen,
            replay=self.replay,
            adaptive_context=self.context_result,
            direct_adaptive=self.direct,
            target=self.target,
        )
        self.assertEqual(evaluator.CONFIRMED_STATUS, result.status)
        self.assertEqual((0, 0, 0, 256, 256), tuple(score.delivered_masked_values for score in result.scores))
        self.assertTrue(result.context_improves_current_only)
        self.assertTrue(result.context_equals_direct_baseline)

    def test_11_valid_functional_deviation_is_falsification(self) -> None:
        changed = list(self.direct.output_values)
        changed[-1] = min(1.0, float(changed[-1]) + 0.01)
        divergent = replace(self.direct, output_values=tuple(changed), result_digest="")
        divergent = replace(
            divergent,
            result_digest=baselines._digest(divergent.payload_without_digest()),
        )
        result = evaluator.evaluate_context_utility(
            current_only=self.current,
            frozen=self.frozen,
            replay=self.replay,
            adaptive_context=self.context_result,
            direct_adaptive=divergent,
            target=self.target,
        )
        self.assertEqual(evaluator.FALSIFIED_STATUS, result.status)
        self.assertFalse(result.context_equals_direct_baseline)

    def test_12_target_is_late_and_invalid_binding_is_not_evaluable(self) -> None:
        for path in (
            ROOT / "tools/_s2kk_visual_context_consumer.py",
            ROOT / "tools/_s2kk_context_utility_baselines.py",
        ):
            source = path.read_text(encoding="ascii")
            self.assertNotIn("EvaluationTarget336V1", source)
            self.assertNotIn("evaluation_plan_digest", source)
        with self.assertRaises(evaluator.S2KKEvaluationError):
            evaluator.evaluate_context_utility(
                current_only=self.current,
                frozen=self.frozen,
                replay=self.replay,
                adaptive_context=self.context_result,
                direct_adaptive=self.direct,
                target=replace(self.target, target_digest="0" * 64),
            )

    def test_13_all_inputs_are_immutable_and_read_only(self) -> None:
        before = (
            self.baseline_state.state_digest,
            self.context.bundle_digest,
            self.masked.probe_digest,
        )
        consumer.consume_b_stable_visual(
            probe=self.masked,
            context=self.context,
            requested_role=consumer.REQUESTED_ROLE,
        )
        baselines.probe_baselines(self.baseline_state, self.full_probe)
        self.assertEqual(before, (
            self.baseline_state.state_digest,
            self.context.bundle_digest,
            self.masked.probe_digest,
        ))
        with self.assertRaises(FrozenInstanceError):
            self.masked.values = ()

    def test_14_boundary_has_no_runner_recorder_memory_or_field_path(self) -> None:
        sources = "\n".join(
            (ROOT / path).read_text(encoding="ascii")
            for path in (
                "tools/_s2kk_context_utility_fixtures.py",
                "tools/_s2kk_visual_context_consumer.py",
                "tools/_s2kk_context_utility_baselines.py",
                "tools/_s2kk_context_utility_evaluator.py",
            )
        )
        for forbidden in (
            "run_main_once",
            "append_only",
            "field_snapshot",
            "advance_s2jv_atomic",
            "probe_s2jv_composite_read_only",
            "BEST_MEMORY",
        ):
            self.assertNotIn(forbidden, sources)
        self.assertEqual((), fixtures.__all__)
        self.assertEqual((), consumer.__all__)
        self.assertEqual((), baselines.__all__)
        self.assertEqual((), evaluator.__all__)


if __name__ == "__main__":
    unittest.main()
