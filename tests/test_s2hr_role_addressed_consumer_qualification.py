"""Sixteen neutral qualification tests for the private S2-HQ boundary."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import unittest

from tests import test_s2gb_private_perceptual_context_bundle as base
from tools import _retention_capacity_read_only as read_only
from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2hq_private_byte_block_conflict_fixture as fixtures
from tools import _s2hq_private_direct_role_addressed_mask_fill_baseline as baseline
from tools import _s2hq_private_role_addressed_context_consumer as consumer


QUALIFICATION_ID = "s2hr-role-consumer-qualification-20260831-01"


def _digest(value: object) -> str:
    if isinstance(value, str):
        value = {"neutral": value}
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _slow_bank(
    modality: str,
    values: tuple[float, ...] | None,
    source_tag: str,
) -> read_only.SlowBankFinding:
    dimension = 8 if modality == "auditory" else 18
    bank_id = f"neutral.{source_tag}.{modality}.bank"
    if values is None:
        return read_only.SlowBankFinding(
            modality,
            bank_id,
            _digest(f"{bank_id}.state"),
            0,
            0,
            0,
            "SLOW_UNAVAILABLE",
            None,
            0.2,
            1 if modality == "auditory" else 44,
            5 if modality == "auditory" else 765,
            (),
            None,
            False,
            False,
        )
    if len(values) != dimension:
        raise AssertionError("neutral slow fixture dimension differs")
    selected = read_only.SlowSlotObservation(
        f"neutral.{source_tag}.{modality}.slot",
        _digest(f"{source_tag}.{modality}.slot"),
        values,
        3,
        4,
        True,
        0.01,
    )
    return read_only.SlowBankFinding(
        modality,
        bank_id,
        _digest(f"{bank_id}.state"),
        3,
        1,
        1,
        "SLOW_RECOGNIZED",
        _digest(f"{bank_id}.finding"),
        0.2,
        1 if modality == "auditory" else 44,
        5 if modality == "auditory" else 765,
        (selected,),
        selected,
        True,
        True,
    )


def _bundle(
    a_visual: tuple[float, ...] | None,
    b_visual: tuple[float, ...] | None,
    *,
    source_tag: str,
) -> two_area.TwoAreaContextBundle:
    binding = base._binding(
        state_digest=_digest(f"{source_tag}.state"),
        probe_digest=_digest(f"{source_tag}.full-probe"),
        probe_values_digest=_digest(f"{source_tag}.full-probe-values"),
    )
    auditory_a = fixtures.M0.values
    auditory_b = fixtures.M1.values if b_visual is not None else None
    b4 = None
    fast = None
    if a_visual is not None:
        b4 = base._b4_slot(
            slot_id=f"neutral.{source_tag}.b4.slot",
            values=auditory_a + a_visual,
        )
        fast = base._fast_slot(
            slot_id=f"neutral.{source_tag}.fast.slot",
            auditory_values=auditory_a,
            visual_values=a_visual,
        )
    finding = base._finding(
        binding,
        b4=b4,
        fast=fast,
        auditory_slow=_slow_bank("auditory", auditory_b, source_tag),
        visual_slow=_slow_bank("visual", b_visual, source_tag),
    )
    projected = context.project_perceptual_context_bundle(
        binding,
        finding,
        base._sequence(binding, finding, available=False),
    )
    return two_area.project_two_area_context(projected)


def _probe(*, conflicting: bool = False) -> probe_contract.MaskedVisualProbe:
    values = list(fixtures.MASKED_VISUAL_VALUES)
    if conflicting:
        values[0] = 0.0
    return probe_contract.MaskedVisualProbe.build(
        tuple(values),
        _digest("neutral.masked-probe-source.conflict" if conflicting else "neutral.masked-probe-source"),
    )


def _distance_bytes(left: tuple[int, ...], right: tuple[int, ...]) -> Fraction:
    return Fraction(sum(abs(a - b) for a, b in zip(left, right, strict=True)), 255 * 18)


def _exercise(
    a_visual: tuple[float, ...],
    b_visual: tuple[float, ...],
    requested_area: str,
    *,
    source_tag: str,
) -> tuple[
    two_area.TwoAreaContextBundle,
    consumer.RoleAddressedCompletionResult,
    baseline.DirectRoleAddressedResult,
]:
    bundle = _bundle(a_visual, b_visual, source_tag=source_tag)
    probe = _probe()
    binding = consumer.RoleAddressedContextUseBinding.build(probe, bundle, requested_area)
    before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
    result = consumer.complete_from_explicit_area(probe, bundle, binding)
    direct = baseline.direct_fill_from_explicit_area(probe, bundle, binding)
    expected = a_visual if requested_area == "A_RECENT" else b_visual
    after = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)

    if result.output_values != direct.output_values:
        raise AssertionError("consumer and direct baseline outputs differ")
    if result.completed_positions != direct.completed_positions:
        raise AssertionError("consumer and direct baseline completion differs")
    if result.selected_candidate_digest != direct.selected_candidate_digest:
        raise AssertionError("consumer and direct baseline candidate differs")
    if result.selected_component_digest != direct.selected_component_digest:
        raise AssertionError("consumer and direct baseline component differs")
    if tuple(result.output_values[index] for index in probe_contract.MASKED_POSITIONS) != tuple(
        expected[index] for index in probe_contract.MASKED_POSITIONS
    ):
        raise AssertionError("role-addressed mask values differ")
    if any(
        result.output_values[index] != probe.values[index]
        for index in probe_contract.VISIBLE_POSITIONS
    ):
        raise AssertionError("visible values changed")
    if before != after or bundle.prestate_digest != bundle.poststate_digest:
        raise AssertionError("role-addressed call changed its source state")
    return bundle, result, direct


class S2HRRoleAddressedConsumerQualificationTests(unittest.TestCase):
    def test_01_q0_q1_values_hashes_and_exact_distances(self) -> None:
        q0 = fixtures.materialize_uint8_image(fixtures.Q0)
        q1 = fixtures.materialize_uint8_image(fixtures.Q1)
        self.assertEqual((80, 120, 3), q0.shape)
        self.assertEqual((80, 120, 3), q1.shape)
        self.assertFalse(q0.flags.writeable)
        self.assertFalse(q1.flags.writeable)
        self.assertEqual(Fraction(85, 765), _distance_bytes(fixtures.V0.block_values, fixtures.V1.block_values))
        self.assertEqual(Fraction(127, 2295), _distance_bytes(fixtures.Q0.block_values, fixtures.V0.block_values))
        self.assertEqual(Fraction(128, 2295), _distance_bytes(fixtures.Q0.block_values, fixtures.V1.block_values))
        self.assertEqual(Fraction(127, 2295), _distance_bytes(fixtures.Q1.block_values, fixtures.V1.block_values))
        self.assertEqual(Fraction(128, 2295), _distance_bytes(fixtures.Q1.block_values, fixtures.V0.block_values))
        self.assertLessEqual(Fraction(128, 2295), Fraction(44, 765))

    def test_02_two_directions_and_four_neutral_role_cases_are_bound(self) -> None:
        self.assertEqual(("d0", "d1"), tuple(item.direction_id for item in fixtures.DIRECTIONS))
        self.assertEqual(("c01", "c02", "c03", "c04"), tuple(item.case_id for item in fixtures.ROLE_CASES))
        self.assertEqual(
            ("A_RECENT", "B_STABLE", "A_RECENT", "B_STABLE"),
            tuple(item.requested_area for item in fixtures.ROLE_CASES),
        )
        self.assertFalse(hasattr(consumer.RoleAddressedContextUseBinding, "expected_visual_id"))

    def test_03_c01_selects_only_a_recent_in_direction_d0(self) -> None:
        _, result, direct = _exercise(fixtures.V0.receptor_values, fixtures.V1.receptor_values, "A_RECENT", source_tag="n01")
        self.assertEqual("ROLE_CONTEXT_COMPLETED", result.status)
        self.assertEqual("DIRECT_ROLE_COMPLETED", direct.status)

    def test_04_c02_selects_only_b_stable_in_direction_d0(self) -> None:
        _, result, direct = _exercise(fixtures.V0.receptor_values, fixtures.V1.receptor_values, "B_STABLE", source_tag="n02")
        self.assertEqual("ROLE_CONTEXT_COMPLETED", result.status)
        self.assertEqual("DIRECT_ROLE_COMPLETED", direct.status)

    def test_05_c03_selects_only_a_recent_in_direction_d1(self) -> None:
        _, result, direct = _exercise(fixtures.V1.receptor_values, fixtures.V0.receptor_values, "A_RECENT", source_tag="n03")
        self.assertEqual("ROLE_CONTEXT_COMPLETED", result.status)
        self.assertEqual("DIRECT_ROLE_COMPLETED", direct.status)

    def test_06_c04_selects_only_b_stable_in_direction_d1(self) -> None:
        _, result, direct = _exercise(fixtures.V1.receptor_values, fixtures.V0.receptor_values, "B_STABLE", source_tag="n04")
        self.assertEqual("ROLE_CONTEXT_COMPLETED", result.status)
        self.assertEqual("DIRECT_ROLE_COMPLETED", direct.status)

    def test_07_unselected_b_cannot_change_a_functional_output(self) -> None:
        alternate_b = tuple(
            value if index in probe_contract.VISIBLE_POSITIONS else 0.25
            for index, value in enumerate(fixtures.V1.receptor_values)
        )
        _, first, _ = _exercise(fixtures.V0.receptor_values, fixtures.V1.receptor_values, "A_RECENT", source_tag="n05")
        _, second, _ = _exercise(fixtures.V0.receptor_values, alternate_b, "A_RECENT", source_tag="n06")
        self.assertEqual(first.output_values, second.output_values)
        self.assertEqual(first.status, second.status)
        self.assertEqual(first.resource_ledger.payload_without_digest(), second.resource_ledger.payload_without_digest())

    def test_08_unselected_a_cannot_change_b_functional_output(self) -> None:
        alternate_a = tuple(
            value if index in probe_contract.VISIBLE_POSITIONS else 0.75
            for index, value in enumerate(fixtures.V0.receptor_values)
        )
        _, first, _ = _exercise(fixtures.V0.receptor_values, fixtures.V1.receptor_values, "B_STABLE", source_tag="n07")
        _, second, _ = _exercise(alternate_a, fixtures.V1.receptor_values, "B_STABLE", source_tag="n08")
        self.assertEqual(first.output_values, second.output_values)
        self.assertEqual(first.status, second.status)
        self.assertEqual(first.resource_ledger.payload_without_digest(), second.resource_ledger.payload_without_digest())

    def test_09_only_masked_positions_are_written(self) -> None:
        _, result, direct = _exercise(fixtures.V0.receptor_values, fixtures.V1.receptor_values, "A_RECENT", source_tag="n09")
        self.assertEqual(probe_contract.MASKED_POSITIONS, result.completed_positions)
        self.assertEqual(probe_contract.MASKED_POSITIONS, direct.completed_positions)
        self.assertEqual(9, result.resource_ledger.masked_copy_count)
        self.assertEqual(9, direct.resource_ledger.masked_copy_count)

    def test_10_missing_selected_role_fails_closed_without_fallback(self) -> None:
        probe = _probe()
        for requested, a_values, b_values in (
            ("A_RECENT", None, fixtures.V1.receptor_values),
            ("B_STABLE", fixtures.V0.receptor_values, None),
        ):
            with self.subTest(requested=requested):
                bundle = _bundle(a_values, b_values, source_tag=f"n10.{requested.lower()}")
                binding = consumer.RoleAddressedContextUseBinding.build(probe, bundle, requested)
                with self.assertRaises(consumer.S2HQConsumerError) as consumer_error:
                    consumer.complete_from_explicit_area(probe, bundle, binding)
                self.assertEqual(consumer.S2HQ_ROLE_UNAVAILABLE, consumer_error.exception.code)
                with self.assertRaises(baseline.S2HQBaselineError) as baseline_error:
                    baseline.direct_fill_from_explicit_area(probe, bundle, binding)
                self.assertEqual(baseline.S2HQ_BASELINE_ROLE_UNAVAILABLE, baseline_error.exception.code)

    def test_11_damaged_role_digest_fails_closed(self) -> None:
        bundle = _bundle(fixtures.V0.receptor_values, fixtures.V1.receptor_values, source_tag="n11")
        probe = _probe()
        binding = consumer.RoleAddressedContextUseBinding.build(probe, bundle, "A_RECENT")
        object.__setattr__(bundle.area_findings[0].recent_content, "finding_digest", "0" * 64)
        with self.assertRaises(consumer.S2HQConsumerError):
            consumer.complete_from_explicit_area(probe, bundle, binding)
        with self.assertRaises(baseline.S2HQBaselineError):
            baseline.direct_fill_from_explicit_area(probe, bundle, binding)

    def test_12_foreign_or_swapped_bundle_binding_fails_closed(self) -> None:
        first = _bundle(fixtures.V0.receptor_values, fixtures.V1.receptor_values, source_tag="n12.first")
        second = _bundle(fixtures.V0.receptor_values, fixtures.V1.receptor_values, source_tag="n12.second")
        probe = _probe()
        binding = consumer.RoleAddressedContextUseBinding.build(probe, first, "A_RECENT")
        with self.assertRaises(consumer.S2HQConsumerError) as consumer_error:
            consumer.complete_from_explicit_area(probe, second, binding)
        self.assertEqual(consumer.S2HQ_BINDING_INVALID, consumer_error.exception.code)
        with self.assertRaises(baseline.S2HQBaselineError) as baseline_error:
            baseline.direct_fill_from_explicit_area(probe, second, binding)
        self.assertEqual(baseline.S2HQ_BASELINE_BINDING_INVALID, baseline_error.exception.code)

    def test_13_contradictory_requested_role_binding_fails_closed(self) -> None:
        bundle = _bundle(fixtures.V0.receptor_values, fixtures.V1.receptor_values, source_tag="n13")
        probe = _probe()
        binding = consumer.RoleAddressedContextUseBinding.build(probe, bundle, "A_RECENT")
        object.__setattr__(binding, "requested_area", "B_STABLE")
        with self.assertRaises(consumer.S2HQConsumerError):
            consumer.complete_from_explicit_area(probe, bundle, binding)
        with self.assertRaises(baseline.S2HQBaselineError):
            baseline.direct_fill_from_explicit_area(probe, bundle, binding)

    def test_14_visible_conflict_never_partially_fills(self) -> None:
        bundle = _bundle(fixtures.V0.receptor_values, fixtures.V1.receptor_values, source_tag="n14")
        probe = _probe(conflicting=True)
        binding = consumer.RoleAddressedContextUseBinding.build(probe, bundle, "B_STABLE")
        result = consumer.complete_from_explicit_area(probe, bundle, binding)
        direct = baseline.direct_fill_from_explicit_area(probe, bundle, binding)
        self.assertEqual("ROLE_CONTEXT_CONFLICT", result.status)
        self.assertEqual("DIRECT_ROLE_CONFLICT", direct.status)
        self.assertEqual((), result.completed_positions)
        self.assertEqual((), direct.completed_positions)
        self.assertEqual(probe.values, result.output_values)
        self.assertEqual(probe.values, direct.output_values)

    def test_15_all_calls_preserve_bundle_and_state_digests(self) -> None:
        bundle = _bundle(fixtures.V0.receptor_values, fixtures.V1.receptor_values, source_tag="n15")
        probe = _probe()
        before = (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest)
        for requested in consumer.ALLOWED_AREAS:
            binding = consumer.RoleAddressedContextUseBinding.build(probe, bundle, requested)
            consumer.complete_from_explicit_area(probe, bundle, binding)
            baseline.direct_fill_from_explicit_area(probe, bundle, binding)
        self.assertEqual(before, (bundle.bundle_digest, bundle.prestate_digest, bundle.poststate_digest))
        self.assertEqual(bundle.prestate_digest, bundle.poststate_digest)

    def test_16_function_modules_cannot_read_evaluation_expectations(self) -> None:
        consumer_source = Path(consumer.__file__).read_text(encoding="utf-8")
        baseline_source = Path(baseline.__file__).read_text(encoding="utf-8")
        for source in (consumer_source, baseline_source):
            self.assertNotIn("EVALUATION_EXPECTATIONS", source)
            self.assertNotIn("_s2hq_private_byte_block_conflict_fixture", source)
        self.assertNotIn("complete_from_explicit_area(", baseline_source)


if __name__ == "__main__":
    unittest.main()
