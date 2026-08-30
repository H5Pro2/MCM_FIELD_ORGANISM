"""Twelve neutral contract tests for the private S2-GB bundle projection."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import hashlib
import json
import unittest

from tools import _retention_capacity_read_only as read_only
from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2gb_private_perceptual_context_bundle as context


def _digest(value: object) -> str:
    if isinstance(value, str):
        value = {"neutral": value}
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _values(length: int, value: float) -> tuple[float, ...]:
    return tuple(value for _ in range(length))


def _binding(
    *,
    state_digest: str | None = None,
    probe_digest: str | None = None,
    probe_values_digest: str | None = None,
) -> context.PerceptualContextProjectionBinding:
    return context.PerceptualContextProjectionBinding.build(
        config_digest=_digest("config"),
        composite_state_digest=state_digest or _digest("composite-state"),
        probe_digest=probe_digest or _digest("probe"),
        probe_values_digest=probe_values_digest or _digest("probe-values"),
        auditory_source_digest=_digest("auditory-source"),
        visual_source_digest=_digest("visual-source"),
        auditory_geometry_id="neutral.auditory.geometry",
        visual_geometry_id="neutral.visual.geometry",
        field_clock_id="neutral.field.clock",
        window_start=100,
        window_end=110,
    )


def _b4_slot(
    *,
    slot_id: str = "neutral.b4.slot",
    values: tuple[float, ...] | None = None,
) -> read_only.B4SlotObservation:
    return read_only.B4SlotObservation(
        slot_id,
        4,
        values if values is not None else _values(26, 0.25),
        0.01,
        0.02,
        True,
    )


def _fast_slot(
    *,
    slot_id: str = "neutral.fast.slot",
    auditory_values: tuple[float, ...] | None = None,
    visual_values: tuple[float, ...] | None = None,
) -> read_only.FastSlotObservation:
    return read_only.FastSlotObservation(
        slot_id,
        _digest(f"{slot_id}.digest"),
        auditory_values if auditory_values is not None else _values(8, 0.25),
        visual_values if visual_values is not None else _values(18, 0.25),
        2,
        5,
        1,
        0.01,
        0.02,
        True,
        True,
    )


def _slow_bank(
    modality: str,
    *,
    recognized: bool,
    bank_id: str | None = None,
) -> read_only.SlowBankFinding:
    dimension = 8 if modality == "auditory" else 18
    bank = bank_id or f"neutral.{modality}.bank"
    slots: tuple[read_only.SlowSlotObservation, ...]
    selected: read_only.SlowSlotObservation | None
    if recognized:
        selected = read_only.SlowSlotObservation(
            f"neutral.{modality}.slot",
            _digest(f"{modality}.slot"),
            _values(dimension, 0.375),
            3,
            6,
            True,
            0.01,
        )
        slots = (selected,)
    else:
        selected = None
        slots = ()
    return read_only.SlowBankFinding(
        modality,
        bank,
        _digest(f"{bank}.state"),
        3 if recognized else 0,
        len(slots),
        len(slots),
        "SLOW_RECOGNIZED" if recognized else "SLOW_UNAVAILABLE",
        _digest(f"{bank}.finding") if recognized else None,
        0.2,
        1,
        5,
        slots,
        selected,
        recognized,
        recognized,
    )


def _finding(
    binding: context.PerceptualContextProjectionBinding,
    *,
    b4: read_only.B4SlotObservation | None = None,
    fast: read_only.FastSlotObservation | None = None,
    auditory_slow: read_only.SlowBankFinding | None = None,
    visual_slow: read_only.SlowBankFinding | None = None,
    composite_state_digest: str | None = None,
    probe_digest: str | None = None,
) -> coordinator.B4TSPM1ReadOnlyFinding:
    state = composite_state_digest or binding.composite_state_digest
    probe = probe_digest or binding.probe_digest
    b4_state = _digest("b4-state")
    b4_candidates = () if b4 is None else (b4,)
    b4_finding = read_only.B4ContentFinding(
        b4_state,
        binding.probe_values_digest,
        len(b4_candidates),
        b4_candidates,
        b4 is not None,
        b4,
        1,
        5,
        44,
        765,
        b4_state,
        b4_state,
    )
    auditory = auditory_slow or _slow_bank("auditory", recognized=False)
    visual = visual_slow or _slow_bank("visual", recognized=False)
    ledger = coordinator._make_resource_ledger("READ_ONLY")
    payload = {
        "schema": coordinator.S2FS_SCHEMA,
        "observed_state_digest": state,
        "probe_digest": probe,
        "roles": list(context.ROLES),
        "b4_recent_prestate_digest": b4_state,
        "b4_recent_poststate_digest": b4_state,
        "tspm_fast_slot_digest": None if fast is None else fast.slot_digest,
        "tspm_slow_bank_digests": [
            auditory.observed_bank_state_digest,
            visual.observed_bank_state_digest,
        ],
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": state,
        "poststate_digest": state,
    }
    return coordinator.B4TSPM1ReadOnlyFinding(
        state,
        probe,
        context.ROLES,
        b4_finding,
        fast,
        (auditory, visual),
        ledger,
        state,
        state,
        coordinator._digest(payload),
    )


def _sequence(
    binding: context.PerceptualContextProjectionBinding,
    finding: coordinator.B4TSPM1ReadOnlyFinding,
    *,
    available: bool = True,
) -> context.ValidatedB4ShortSequenceEvidence:
    references = ()
    status = "NOT_REQUESTED"
    if available:
        source = finding.b4_recent.candidates[0]
        reference = context.B4SequenceReference.build(
            source.formation_index,
            source.slot_id,
            context._b4_sequence_slot_digest(
                finding.b4_recent.observed_state_digest,
                source,
            ),
            _digest(list(source.values)),
        )
        references = (reference,)
        status = "AVAILABLE"
    return context.ValidatedB4ShortSequenceEvidence.build(
        status,
        finding.b4_recent.observed_state_digest,
        binding.probe_digest,
        references,
    )


def _full_bundle() -> context.PerceptualContextBundle:
    binding = _binding()
    finding = _finding(
        binding,
        b4=_b4_slot(),
        fast=_fast_slot(),
        auditory_slow=_slow_bank("auditory", recognized=True),
        visual_slow=_slow_bank("visual", recognized=True),
    )
    return context.project_perceptual_context_bundle(
        binding,
        finding,
        _sequence(binding, finding),
    )


class S2GBPrivatePerceptualContextBundleTests(unittest.TestCase):
    def test_01_full_occupancy_projects_three_separate_candidates(self) -> None:
        bundle = _full_bundle()
        self.assertEqual(context.ROLES, tuple(item.role for item in bundle.role_findings))
        self.assertEqual(("AVAILABLE_COMPLETE",) * 3, tuple(item.status for item in bundle.role_findings))
        self.assertEqual((3, 4, 78), (bundle.resource_ledger.candidate_count, bundle.resource_ledger.component_count, bundle.resource_ledger.value_count))
        self.assertIsNone(bundle.automatic_selection)

    def test_02_partial_occupancy_preserves_one_slow_modality(self) -> None:
        binding = _binding()
        finding = _finding(binding, b4=_b4_slot(), auditory_slow=_slow_bank("auditory", recognized=True))
        bundle = context.project_perceptual_context_bundle(binding, finding, _sequence(binding, finding, available=False))
        self.assertEqual(("AVAILABLE_COMPLETE", "ABSENT_VALID", "AVAILABLE_PARTIAL"), tuple(item.status for item in bundle.role_findings))
        slow = bundle.role_findings[2].candidate
        self.assertIsNotNone(slow)
        self.assertEqual(("AUDITORY",), tuple(item.component_role for item in slow.components))
        self.assertEqual("CROSS_MODAL_RELATION_NOT_REPRESENTED", slow.cross_modal_relation)

    def test_03_valid_absence_is_transparent_and_creates_no_candidate(self) -> None:
        binding = _binding()
        finding = _finding(binding)
        bundle = context.project_perceptual_context_bundle(binding, finding, _sequence(binding, finding, available=False))
        self.assertEqual(("ABSENT_VALID",) * 3, tuple(item.status for item in bundle.role_findings))
        self.assertEqual(("NO_OCCUPIED_SOURCE", "NO_FUNCTIONAL_MATCH", "NO_STABLE_SLOW_MATCH"), tuple(item.absence_reason for item in bundle.role_findings))
        self.assertEqual(0, bundle.resource_ledger.candidate_count)

    def test_04_projection_order_and_digest_are_deterministic(self) -> None:
        first = _full_bundle()
        second = _full_bundle()
        self.assertEqual(first, second)
        self.assertEqual(first.bundle_digest, second.bundle_digest)
        self.assertEqual(context.ROLES, tuple(item.role for item in first.role_findings))

    def test_05_equal_values_from_distinct_sources_are_not_merged(self) -> None:
        binding = _binding()
        same = _values(26, 0.25)
        finding = _finding(
            binding,
            b4=_b4_slot(values=same),
            fast=_fast_slot(auditory_values=same[:8], visual_values=same[8:]),
        )
        bundle = context.project_perceptual_context_bundle(binding, finding, _sequence(binding, finding))
        b4 = bundle.role_findings[0].candidate
        fast = bundle.role_findings[1].candidate
        self.assertEqual(b4.components[0].values, fast.components[0].values)
        self.assertNotEqual(b4.components[0].source_digest, fast.components[0].source_digest)
        self.assertNotEqual(b4.candidate_digest, fast.candidate_digest)

    def test_06_bundle_candidates_and_values_are_immutable(self) -> None:
        bundle = _full_bundle()
        with self.assertRaises(FrozenInstanceError):
            bundle.automatic_selection = "forbidden"
        with self.assertRaises(FrozenInstanceError):
            bundle.role_findings[0].candidate.components[0].values = ()
        self.assertIsInstance(bundle.role_findings, tuple)
        self.assertIsInstance(bundle.role_findings[0].candidate.components[0].values, tuple)

    def test_07_corrupt_source_provenance_fails_closed(self) -> None:
        valid = _binding()
        with self.assertRaises(context.S2GBProjectionError) as caught:
            context.PerceptualContextProjectionBinding(
                valid.config_digest,
                valid.composite_state_digest,
                valid.probe_digest,
                valid.probe_values_digest,
                valid.auditory_source_digest,
                valid.visual_source_digest,
                valid.auditory_geometry_id,
                valid.visual_geometry_id,
                valid.field_clock_id,
                valid.window_start,
                valid.window_end,
                _digest("forged-source"),
                valid.binding_digest,
            )
        self.assertEqual(context.S2GB_SOURCE_BINDING_INVALID, caught.exception.code)

    def test_08_foreign_probe_fails_closed_without_partial_bundle(self) -> None:
        binding = _binding()
        finding = _finding(binding, probe_digest=_digest("foreign-probe"))
        with self.assertRaises(context.S2GBProjectionError) as caught:
            context.project_perceptual_context_bundle(
                binding,
                finding,
                _sequence(binding, finding, available=False),
            )
        self.assertEqual(context.S2GB_PROBE_MISMATCH, caught.exception.code)

    def test_09_contradictory_state_digest_fails_closed(self) -> None:
        binding = _binding()
        finding = _finding(binding, composite_state_digest=_digest("foreign-state"))
        with self.assertRaises(context.S2GBProjectionError) as caught:
            context.project_perceptual_context_bundle(
                binding,
                finding,
                _sequence(binding, finding, available=False),
            )
        self.assertEqual(context.S2GB_STATE_DIGEST_MISMATCH, caught.exception.code)

    def test_10_wrong_component_dimension_fails_closed(self) -> None:
        binding = _binding()
        finding = _finding(binding, b4=_b4_slot(values=_values(25, 0.25)))
        with self.assertRaises(context.S2GBProjectionError) as caught:
            context.project_perceptual_context_bundle(binding, finding, _sequence(binding, finding))
        self.assertEqual(context.S2GB_DIMENSION_INVALID, caught.exception.code)

    def test_11_duplicate_selected_source_fails_closed(self) -> None:
        binding = _binding()
        shared_id = "neutral.shared.slot"
        finding = _finding(binding, b4=_b4_slot(slot_id=shared_id), fast=_fast_slot(slot_id=shared_id))
        with self.assertRaises(context.S2GBProjectionError) as caught:
            context.project_perceptual_context_bundle(binding, finding, _sequence(binding, finding))
        self.assertEqual(context.S2GB_DUPLICATE_SOURCE, caught.exception.code)

    def test_12_more_than_three_bundle_roles_is_rejected(self) -> None:
        bundle = _full_bundle()
        with self.assertRaises(context.S2GBProjectionError) as caught:
            context.PerceptualContextBundle(
                bundle.contract_digest,
                bundle.binding_digest,
                bundle.config_digest,
                bundle.composite_state_digest,
                bundle.probe_digest,
                bundle.source_digest,
                bundle.role_findings + (bundle.role_findings[0],),
                bundle.sequence_finding,
                bundle.resource_ledger,
                bundle.prestate_digest,
                bundle.poststate_digest,
                None,
                bundle.bundle_digest,
            )
        self.assertEqual(context.S2GB_CAPACITY_EXCEEDED, caught.exception.code)


if __name__ == "__main__":
    unittest.main()
