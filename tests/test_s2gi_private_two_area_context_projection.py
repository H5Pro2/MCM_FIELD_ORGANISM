"""Fourteen neutral contract tests for the private S2-GI A/B projection."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

from tests import test_s2gb_private_perceptual_context_bundle as fixtures
from tools import _s2gb_private_perceptual_context_bundle as context
from tools import _s2gi_private_two_area_context_projection as two_area


def _partial_bundle() -> context.PerceptualContextBundle:
    binding = fixtures._binding()
    finding = fixtures._finding(
        binding,
        b4=fixtures._b4_slot(),
        auditory_slow=fixtures._slow_bank("auditory", recognized=True),
    )
    return context.project_perceptual_context_bundle(
        binding,
        finding,
        fixtures._sequence(binding, finding, available=False),
    )


def _empty_bundle() -> context.PerceptualContextBundle:
    binding = fixtures._binding()
    finding = fixtures._finding(binding)
    return context.project_perceptual_context_bundle(
        binding,
        finding,
        fixtures._sequence(binding, finding, available=False),
    )


def _same_values_bundle() -> context.PerceptualContextBundle:
    binding = fixtures._binding()
    values = fixtures._values(26, 0.25)
    finding = fixtures._finding(
        binding,
        b4=fixtures._b4_slot(values=values),
        fast=fixtures._fast_slot(
            auditory_values=values[:8],
            visual_values=values[8:],
        ),
    )
    return context.project_perceptual_context_bundle(
        binding,
        finding,
        fixtures._sequence(binding, finding),
    )


class S2GIPrivateTwoAreaContextProjectionTests(unittest.TestCase):
    def test_01_full_bundle_projects_exactly_two_areas(self) -> None:
        source = fixtures._full_bundle()
        result = two_area.project_two_area_context(source)
        self.assertEqual(two_area.AREAS, tuple(item.area for item in result.area_findings))
        self.assertEqual(2, result.resource_ledger.area_projection_count)
        self.assertIsNone(result.automatic_selection)

    def test_02_partial_slow_occupancy_remains_partial_in_b(self) -> None:
        source = _partial_bundle()
        result = two_area.project_two_area_context(source)
        stable = result.area_findings[1].stable_content
        self.assertEqual("AVAILABLE_PARTIAL", stable.status)
        self.assertEqual(("AUDITORY",), tuple(item.component_role for item in stable.candidate.components))

    def test_03_empty_bundle_preserves_valid_absence(self) -> None:
        result = two_area.project_two_area_context(_empty_bundle())
        area_a, area_b = result.area_findings
        self.assertEqual("ABSENT_VALID", area_a.recent_content.status)
        self.assertEqual("ABSENT_VALID", area_a.fast_internal.status)
        self.assertEqual("ABSENT_VALID", area_b.stable_content.status)
        self.assertEqual("NO_STABLE_SLOW_MATCH", area_b.stable_content.absence_reason)
        self.assertIsNone(area_b.stable_content.candidate)

    def test_04_a_keeps_b4_and_fast_as_separate_roles_without_merging(self) -> None:
        result = two_area.project_two_area_context(_same_values_bundle())
        area_a = result.area_findings[0]
        recent = area_a.recent_content.candidate
        fast = area_a.fast_internal.candidate
        self.assertEqual(recent.components[0].values, fast.components[0].values)
        self.assertNotEqual(recent.candidate_digest, fast.candidate_digest)
        self.assertNotEqual(recent.components[0].source_digest, fast.components[0].source_digest)

    def test_05_short_sequence_is_preserved_only_in_a(self) -> None:
        source = fixtures._full_bundle()
        result = two_area.project_two_area_context(source)
        area_a, area_b = result.area_findings
        self.assertIs(area_a.short_sequence, source.sequence_finding)
        self.assertEqual("AVAILABLE", area_a.short_sequence.status)
        self.assertFalse(hasattr(area_b, "short_sequence"))

    def test_06_complete_b_preserves_both_stable_slow_components(self) -> None:
        source = fixtures._full_bundle()
        result = two_area.project_two_area_context(source)
        stable = result.area_findings[1].stable_content
        self.assertIs(stable, source.role_findings[2])
        self.assertEqual("AVAILABLE_COMPLETE", stable.status)
        self.assertEqual(("AUDITORY", "VISUAL"), tuple(item.component_role for item in stable.candidate.components))
        self.assertTrue(all(item.stable is True for item in stable.candidate.components))

    def test_07_equal_inputs_produce_byte_equal_deterministic_outputs(self) -> None:
        first = two_area.project_two_area_context(fixtures._full_bundle())
        second = two_area.project_two_area_context(fixtures._full_bundle())
        self.assertEqual(first, second)
        self.assertEqual(first.bundle_digest, second.bundle_digest)
        self.assertEqual(first.resource_ledger.ledger_digest, second.resource_ledger.ledger_digest)

    def test_08_projection_is_immutable_and_does_not_change_input(self) -> None:
        source = fixtures._full_bundle()
        before = source.bundle_digest
        result = two_area.project_two_area_context(source)
        self.assertEqual(before, source.bundle_digest)
        self.assertEqual(source.prestate_digest, source.poststate_digest)
        with self.assertRaises(FrozenInstanceError):
            result.automatic_selection = "forbidden"
        with self.assertRaises(FrozenInstanceError):
            result.area_findings[0].recent_content = source.role_findings[1]

    def test_09_corrupt_bundle_digest_fails_closed(self) -> None:
        source = fixtures._full_bundle()
        object.__setattr__(source, "bundle_digest", fixtures._digest("corrupt-bundle"))
        with self.assertRaises(two_area.S2GIProjectionError) as caught:
            two_area.project_two_area_context(source)
        self.assertEqual(two_area.S2GI_DIGEST_MISMATCH, caught.exception.code)

    def test_10_wrong_role_order_fails_closed(self) -> None:
        source = fixtures._full_bundle()
        b4, fast, slow = source.role_findings
        object.__setattr__(source, "role_findings", (fast, b4, slow))
        with self.assertRaises(two_area.S2GIProjectionError) as caught:
            two_area.project_two_area_context(source)
        self.assertEqual(two_area.S2GI_ROLE_INVALID, caught.exception.code)

    def test_11_invalid_source_binding_fails_closed(self) -> None:
        source = fixtures._full_bundle()
        object.__setattr__(source, "source_digest", "not-a-digest")
        with self.assertRaises(two_area.S2GIProjectionError) as caught:
            two_area.project_two_area_context(source)
        self.assertEqual(two_area.S2GI_BINDING_INVALID, caught.exception.code)

    def test_12_wrong_component_dimension_fails_closed(self) -> None:
        source = fixtures._full_bundle()
        component = source.role_findings[0].candidate.components[0]
        object.__setattr__(component, "values", component.values[:-1])
        with self.assertRaises(two_area.S2GIProjectionError) as caught:
            two_area.project_two_area_context(source)
        self.assertEqual(two_area.S2GI_DIMENSION_INVALID, caught.exception.code)

    def test_13_sequence_capacity_overflow_fails_closed(self) -> None:
        source = fixtures._full_bundle()
        reference = source.sequence_finding.references[0]
        object.__setattr__(source.sequence_finding, "references", (reference,) * 10)
        with self.assertRaises(two_area.S2GIProjectionError) as caught:
            two_area.project_two_area_context(source)
        self.assertEqual(two_area.S2GI_CAPACITY_EXCEEDED, caught.exception.code)

    def test_14_output_type_rejects_a_third_public_area(self) -> None:
        valid = two_area.project_two_area_context(fixtures._full_bundle())
        with self.assertRaises(two_area.S2GIProjectionError) as caught:
            two_area.TwoAreaContextBundle(
                valid.contract_digest,
                valid.source_bundle_digest,
                valid.binding_digest,
                valid.config_digest,
                valid.composite_state_digest,
                valid.probe_digest,
                valid.source_digest,
                valid.area_findings + (valid.area_findings[0],),
                valid.resource_ledger,
                valid.prestate_digest,
                valid.poststate_digest,
                None,
                valid.bundle_digest,
            )
        self.assertEqual(two_area.S2GI_ROLE_INVALID, caught.exception.code)


if __name__ == "__main__":
    unittest.main()
