"""Sixteen neutral tests for the private S2-GK consumer boundary."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import inspect
import unittest

from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_direct_mask_fill_baseline as direct
from tools import _s2gk_private_masked_visual_completion_evaluator as evaluator
from tools import _s2gk_private_masked_visual_context_consumer as consumer


TARGET = (1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0)
FOREIGN = (1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0)
CONFLICT = (0.0,) + TARGET[1:]


def _digest(label: str) -> str:
    return context._digest({"neutral": label})


def _values(length: int, value: float) -> tuple[float, ...]:
    return tuple(value for _ in range(length))


def _masked_probe() -> consumer.MaskedVisualProbe:
    values = tuple(
        TARGET[index] if index in consumer.VISIBLE_POSITIONS else None
        for index in range(18)
    )
    return consumer.MaskedVisualProbe.build(values, _digest("current-probe-source"))


def _source_bundle(
    visual: tuple[float, ...] | None,
    *,
    a_value: float = 0.25,
) -> context.PerceptualContextBundle:
    state_digest = _digest("composite-state")
    b4_component = context._component(
        "AV_JOINT",
        _values(26, a_value),
        "neutral.b4.slot",
        _digest(f"b4-state-{a_value}"),
        None,
        (0.1, 0.1),
        None,
        None,
        None,
        13,
    )
    fast_component = context._component(
        "AV_JOINT",
        _values(26, 1.0 - a_value),
        "neutral.fast.slot",
        _digest(f"fast-state-{a_value}"),
        (0.1, 0.1),
        (0.1, 0.1),
        1,
        None,
        12,
        None,
    )
    b4 = context._role_finding(
        "B4_RECENT",
        "AVAILABLE_COMPLETE",
        context._candidate("B4_RECENT", (b4_component,)),
        None,
    )
    fast = context._role_finding(
        "TSPM_FAST",
        "AVAILABLE_COMPLETE",
        context._candidate("TSPM_FAST", (fast_component,)),
        None,
    )
    components = [b4_component, fast_component]
    if visual is None:
        slow = context._role_finding(
            "TSPM_SLOW",
            "ABSENT_VALID",
            None,
            "NO_STABLE_SLOW_MATCH",
        )
    else:
        slow_component = context._component(
            "VISUAL",
            visual,
            "neutral.visual.slow.slot",
            _digest(f"slow-state-{visual}"),
            (0.01,),
            (0.01,),
            3,
            True,
            13,
            None,
        )
        components.append(slow_component)
        slow = context._role_finding(
            "TSPM_SLOW",
            "AVAILABLE_PARTIAL",
            context._candidate("TSPM_SLOW", (slow_component,)),
            None,
        )
    roles = (b4, fast, slow)
    sequence_payload = {
        "schema": context.S2GB_SCHEMA,
        "status": "NOT_REQUESTED",
        "reference_digests": [],
        "observed_b4_state_digest": _digest("b4-observed-state"),
        "source_evidence_digest": _digest("sequence-evidence"),
    }
    sequence = context.B4ShortSequenceFinding(
        "NOT_REQUESTED",
        (),
        sequence_payload["observed_b4_state_digest"],
        sequence_payload["source_evidence_digest"],
        context._digest(sequence_payload),
    )
    candidates = tuple(item.candidate for item in roles if item.candidate is not None)
    value_count = sum(len(item.values) for item in components)
    ledger_payload = {
        "schema": context.S2GB_SCHEMA,
        "validated_evidence_records": len(components),
        "validated_digest_count": 8 + len(components),
        "role_projection_count": 3,
        "candidate_count": len(candidates),
        "component_count": len(components),
        "value_count": value_count,
        "sequence_reference_count": 0,
        "digest_operation_count": 10,
    }
    ledger = context.PerceptualContextResourceLedger(
        len(components),
        8 + len(components),
        3,
        len(candidates),
        len(components),
        value_count,
        0,
        10,
        context._digest(ledger_payload),
    )
    bundle_payload = {
        "schema": context.S2GB_SCHEMA,
        "contract_digest": context.S2GA_CONTRACT_DIGEST,
        "binding_digest": _digest("binding"),
        "config_digest": _digest("config"),
        "composite_state_digest": state_digest,
        "probe_digest": _digest("historical-context-probe"),
        "source_digest": _digest("historical-context-source"),
        "role_finding_digests": [item.finding_digest for item in roles],
        "sequence_finding_digest": sequence.finding_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": state_digest,
        "poststate_digest": state_digest,
        "automatic_selection": None,
    }
    return context.PerceptualContextBundle(
        context.S2GA_CONTRACT_DIGEST,
        bundle_payload["binding_digest"],
        bundle_payload["config_digest"],
        state_digest,
        bundle_payload["probe_digest"],
        bundle_payload["source_digest"],
        roles,
        sequence,
        ledger,
        state_digest,
        state_digest,
        None,
        context._digest(bundle_payload),
    )


def _bundle(
    visual: tuple[float, ...] | None,
    *,
    a_value: float = 0.25,
) -> two_area.TwoAreaContextBundle:
    return two_area.project_two_area_context(_source_bundle(visual, a_value=a_value))


def _results(visual: tuple[float, ...]) -> tuple[
    consumer.MaskedVisualProbe,
    two_area.TwoAreaContextBundle,
    consumer.MaskedVisualCompletionResult,
    consumer.MaskedVisualCompletionResult,
    direct.DirectMaskFillResult,
]:
    probe = _masked_probe()
    bundle = _bundle(visual)
    binding = consumer.ContextUseBinding.build(probe, bundle)
    current = consumer.current_perception_only(probe)
    contextual = consumer.complete_with_named_b_stable(probe, bundle, binding)
    baseline = direct.direct_b_stable_mask_fill(probe, bundle, binding)
    return probe, bundle, current, contextual, baseline


class S2GKPrivateMaskedVisualContextTests(unittest.TestCase):
    def test_01_current_perception_only_does_not_guess(self) -> None:
        result = consumer.current_perception_only(_masked_probe())
        self.assertEqual("INSUFFICIENT_INFORMATION", result.status)
        self.assertEqual((), result.completed_positions)
        self.assertEqual(9, sum(value is None for value in result.output_values))

    def test_02_correct_b_context_completes_the_mask(self) -> None:
        _, _, _, result, _ = _results(TARGET)
        self.assertEqual("CONTEXT_COMPLETED", result.status)
        self.assertEqual(TARGET, result.output_values)

    def test_03_direct_baseline_is_functionally_equal(self) -> None:
        _, _, _, result, baseline = _results(TARGET)
        self.assertEqual("DIRECT_COMPLETED", baseline.status)
        self.assertEqual(result.output_values, baseline.output_values)
        self.assertEqual(result.completed_positions, baseline.completed_positions)
        self.assertEqual(result.resource_ledger.masked_copy_count, baseline.resource_ledger.masked_copy_count)

    def test_04_foreign_context_completes_in_both_arms_and_is_reported(self) -> None:
        _, _, current, result, baseline = _results(FOREIGN)
        finding = evaluator.evaluate_completion_case(
            "FOREIGN_CONTEXT",
            evaluator.MaskedVisualTargetFixture.build(TARGET),
            current,
            result,
            baseline,
        )
        self.assertEqual(FOREIGN, result.output_values)
        self.assertEqual(FOREIGN, baseline.output_values)
        self.assertEqual("S2GJ_FOREIGN_CONTEXT_LIMIT_OBSERVED", finding.status)
        self.assertGreater(finding.masked_mean_absolute_error, 0.0)

    def test_05_absent_valid_context_does_not_fill(self) -> None:
        probe = _masked_probe()
        bundle = _bundle(None)
        result = consumer.complete_with_named_b_stable(
            probe,
            bundle,
            consumer.ContextUseBinding.build(probe, bundle),
        )
        self.assertEqual("CONTEXT_ABSENT", result.status)
        self.assertEqual(probe.values, result.output_values)
        self.assertIsNone(result.context_candidate_digest)

    def test_06_visible_conflict_stops_without_partial_fill(self) -> None:
        probe = _masked_probe()
        bundle = _bundle(CONFLICT)
        binding = consumer.ContextUseBinding.build(probe, bundle)
        result = consumer.complete_with_named_b_stable(probe, bundle, binding)
        baseline = direct.direct_b_stable_mask_fill(probe, bundle, binding)
        self.assertEqual("CONTEXT_CONFLICT", result.status)
        self.assertEqual("DIRECT_CONFLICT", baseline.status)
        self.assertEqual((), result.completed_positions)
        self.assertEqual(probe.values, result.output_values)

    def test_07_a_interference_is_validated_but_ignored_for_completion(self) -> None:
        probe = _masked_probe()
        first = _bundle(TARGET, a_value=0.25)
        second = _bundle(TARGET, a_value=0.75)
        one = consumer.complete_with_named_b_stable(
            probe,
            first,
            consumer.ContextUseBinding.build(probe, first),
        )
        two = consumer.complete_with_named_b_stable(
            probe,
            second,
            consumer.ContextUseBinding.build(probe, second),
        )
        self.assertEqual(one.output_values, two.output_values)
        self.assertNotEqual(first.bundle_digest, second.bundle_digest)

    def test_08_visible_values_are_unchanged_for_correct_and_foreign_context(self) -> None:
        probe = _masked_probe()
        for visual in (TARGET, FOREIGN):
            with self.subTest(visual=visual):
                bundle = _bundle(visual)
                result = consumer.complete_with_named_b_stable(
                    probe,
                    bundle,
                    consumer.ContextUseBinding.build(probe, bundle),
                )
                self.assertTrue(all(result.output_values[index] == probe.values[index] for index in consumer.VISIBLE_POSITIONS))

    def test_09_only_the_nine_masked_positions_are_copied(self) -> None:
        _, _, _, result, baseline = _results(TARGET)
        self.assertEqual(consumer.MASKED_POSITIONS, result.completed_positions)
        self.assertEqual(9, result.resource_ledger.masked_copy_count)
        self.assertEqual(9, baseline.resource_ledger.masked_copy_count)

    def test_10_only_explicit_b_stable_role_is_accepted(self) -> None:
        probe = _masked_probe()
        bundle = _bundle(TARGET)
        with self.assertRaises(consumer.S2GKConsumerError) as caught:
            consumer.ContextUseBinding.build(probe, bundle, requested_area="A_RECENT")
        self.assertEqual(consumer.S2GK_ROLE_INVALID, caught.exception.code)

    def test_11_mask_dimension_and_marker_errors_fail_closed(self) -> None:
        valid = _masked_probe()
        cases = []
        cases.append(valid.values[:-1])
        numeric_mask = list(valid.values)
        numeric_mask[1] = 0.0
        cases.append(tuple(numeric_mask))
        missing_visible = list(valid.values)
        missing_visible[0] = None
        cases.append(tuple(missing_visible))
        for values in cases:
            with self.subTest(values=values):
                with self.assertRaises(consumer.S2GKConsumerError):
                    consumer.MaskedVisualProbe.build(values, _digest("invalid-probe"))
        object.__setattr__(valid, "visible_positions", tuple(range(9)))
        with self.assertRaises(consumer.S2GKConsumerError):
            consumer.current_perception_only(valid)

    def test_12_source_probe_bundle_and_state_digest_errors_fail_closed(self) -> None:
        mutations = ("source", "probe", "bundle", "state")
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                probe = _masked_probe()
                bundle = _bundle(TARGET)
                binding = consumer.ContextUseBinding.build(probe, bundle)
                if mutation == "source":
                    object.__setattr__(probe, "source_digest", "invalid")
                elif mutation == "probe":
                    object.__setattr__(probe, "probe_digest", _digest("foreign-probe"))
                elif mutation == "bundle":
                    object.__setattr__(bundle, "bundle_digest", _digest("foreign-bundle"))
                else:
                    object.__setattr__(binding, "context_state_digest", _digest("foreign-state"))
                    object.__setattr__(binding, "binding_digest", consumer._digest(binding.payload_without_digest()))
                with self.assertRaises(consumer.S2GKConsumerError):
                    consumer.complete_with_named_b_stable(probe, bundle, binding)

    def test_13_resource_overflow_fails_closed(self) -> None:
        probe = _masked_probe()
        bundle = _bundle(TARGET)
        binding = consumer.ContextUseBinding.build(probe, bundle)
        object.__setattr__(bundle.resource_ledger, "value_reference_count", 79)
        with self.assertRaises(consumer.S2GKConsumerError) as caught:
            consumer.complete_with_named_b_stable(probe, bundle, binding)
        self.assertEqual(consumer.S2GK_CAPACITY_EXCEEDED, caught.exception.code)

    def test_14_probe_bundle_and_results_are_immutable(self) -> None:
        probe, bundle, _, result, baseline = _results(TARGET)
        before = (probe.probe_digest, bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        self.assertEqual(before, (probe.probe_digest, bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest))
        with self.assertRaises(FrozenInstanceError):
            probe.values = ()
        with self.assertRaises(FrozenInstanceError):
            result.output_values = ()
        with self.assertRaises(FrozenInstanceError):
            baseline.output_values = ()

    def test_15_complete_values_exist_only_in_the_evaluator_fixture(self) -> None:
        consumer_parameters = inspect.signature(consumer.complete_with_named_b_stable).parameters
        baseline_parameters = inspect.signature(direct.direct_b_stable_mask_fill).parameters
        self.assertNotIn("target", consumer_parameters)
        self.assertNotIn("fixture", consumer_parameters)
        self.assertNotIn("target", baseline_parameters)
        self.assertNotIn("fixture", baseline_parameters)
        self.assertFalse(hasattr(consumer, "MaskedVisualTargetFixture"))
        self.assertFalse(hasattr(direct, "MaskedVisualTargetFixture"))
        self.assertTrue(hasattr(evaluator, "MaskedVisualTargetFixture"))

    def test_16_evaluator_separates_functional_failure_from_not_evaluable(self) -> None:
        _, _, current, result, baseline = _results(TARGET)
        fixture = evaluator.MaskedVisualTargetFixture.build(TARGET)
        valid = evaluator.evaluate_completion_case("CORRECT_CONTEXT", fixture, current, result, baseline)
        self.assertEqual("S2GJ_FUNCTION_VALID_DIRECT_MASK_FILL_EXPLAINS", valid.status)

        wrong_fixture = evaluator.MaskedVisualTargetFixture.build(FOREIGN)
        falsified = evaluator.evaluate_completion_case("CORRECT_CONTEXT", wrong_fixture, current, result, baseline)
        self.assertEqual("S2GJ_FUNCTION_FALSIFIED", falsified.status)

        corrupt = consumer.complete_with_named_b_stable(
            _masked_probe(),
            _bundle(TARGET),
            consumer.ContextUseBinding.build(_masked_probe(), _bundle(TARGET)),
        )
        object.__setattr__(corrupt, "result_digest", _digest("corrupt-result"))
        not_evaluable = evaluator.evaluate_completion_case("CORRECT_CONTEXT", fixture, current, corrupt, baseline)
        self.assertEqual("S2GJ_NOT_EVALUABLE", not_evaluable.status)


if __name__ == "__main__":
    unittest.main()
