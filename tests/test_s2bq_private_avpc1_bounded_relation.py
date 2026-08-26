from __future__ import annotations

from dataclasses import FrozenInstanceError, replace
from pathlib import Path
import unittest

from mcm_field_organism import current_api
from mcm_field_organism._avpc1_audio_only_probe_envelope import (
    _timed_frame_binding,
    bind_avpc1_frozen_relation_history_partition,
    bind_avpc1_private_auditory_only_probe_envelope,
    bind_avpc1_private_auditory_probe_source,
)
from mcm_field_organism._avpc1_bounded_relation import (
    AVPC1_RELATION_PROVENANCE_MISMATCH,
    AVPC1BoundedRelationError,
    advance_avpc1_bounded_relation_state,
    bind_avpc1_unambiguous_overlap_exposure_receipt,
    initial_avpc1_bounded_relation_state,
    probe_avpc1_bounded_relation_read_only,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism._ppb1_reference import (
    PPB1BankState,
    PPB1PrototypeSlot,
)
from mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe import (
    probe_s1wu_perceptual_state,
)
from mcm_field_organism.browser_receptor_bridge import (
    BrowserReceptorSequenceBatch,
)
from mcm_field_organism.browser_world_contract import (
    BrowserWorldContract,
    BrowserWorldPhase,
)
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
)
from mcm_field_organism.receptor_time_alignment import (
    audit_receptor_time_alignment,
)
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from mcm_field_organism.root_lazy_exports import ROOT_LAZY_EXPORTS


ROOT = Path(__file__).resolve().parents[1]


def _parameters() -> PPB1ProfileParameters:
    return PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )


def _contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        "synthetic.avpc1.relation.v1",
        1,
        1,
        1,
        100.0,
        (
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def _bank_state(config, values: tuple[float, ...]) -> PPB1BankState:
    occupied = tuple(
        PPB1PrototypeSlot(
            f"{config.bank_id}.slot.{index:03d}",
            True,
            tuple(value for _ in config.carrier_ids),
            3,
            3,
        )
        for index, value in enumerate(values)
    )
    free = tuple(
        PPB1PrototypeSlot.free(f"{config.bank_id}.slot.{index:03d}")
        for index in range(len(occupied), config.capacity)
    )
    return PPB1BankState(
        config.bank_id,
        config.digest(),
        3,
        f"source.{config.modality_id}",
        10,
        occupied + free,
    )


def _timed(
    config,
    *,
    token: str,
    source_start: int,
    field_start: int,
    value: float,
) -> OrganismTimedReceptorFrame:
    return OrganismTimedReceptorFrame(
        ReceptorContactFrame(
            config.modality_id,
            config.geometry_id,
            f"synthetic.{token}.{config.modality_id}",
            f"source.{config.modality_id}",
            source_start,
            source_start + 10,
            config.carrier_ids,
            tuple(value for _ in config.carrier_ids),
        ),
        CommonFieldTime("field.synthetic", field_start, field_start + 10),
    )


def _sequence(item: OrganismTimedReceptorFrame) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        item.frame.modality_id,
        item.frame.geometry_id,
        item.field_time.clock_id,
        (item,),
    )


class _Fixture:
    def __init__(self, pairs: tuple[tuple[float, float], ...]) -> None:
        self.contract = _contract()
        self.profile = bind_ppb1_receptor_profile("browser", _parameters())
        self.auditory_state = _bank_state(
            self.profile.auditory_config,
            (-0.5, 0.0, 0.5),
        )
        self.visual_state = _bank_state(
            self.profile.visual_config,
            (-0.5, 0.0, 0.5),
        )
        self.items = []
        partition_items = []
        for index, (auditory_value, visual_value) in enumerate(pairs, start=1):
            auditory = _timed(
                self.profile.auditory_config,
                token=f"exposure.{index}",
                source_start=index * 10,
                field_start=(index - 1) * 10,
                value=auditory_value,
            )
            visual = _timed(
                self.profile.visual_config,
                token=f"exposure.{index}",
                source_start=index * 10,
                field_start=(index - 1) * 10,
                value=visual_value,
            )
            auditory_binding = _timed_frame_binding(auditory)
            visual_binding = _timed_frame_binding(visual)
            self.items.append(
                (auditory, visual, auditory_binding, visual_binding)
            )
            partition_items.extend(
                (
                    ("auditory", auditory_binding),
                    ("visual", visual_binding),
                )
            )
        self.partition = bind_avpc1_frozen_relation_history_partition(
            tuple(partition_items)
        )

    def state(self, table_id: str):
        return initial_avpc1_bounded_relation_state(
            table_id,
            self.profile,
            self.auditory_state,
            self.visual_state,
            self.partition,
        )

    def receipt(self, index: int, state):
        auditory, visual, auditory_binding, visual_binding = self.items[index]
        auditory_finding = probe_s1wu_perceptual_state(
            self.profile.auditory_config,
            self.auditory_state,
            auditory.frame,
            f"probe.exposure.{index + 1}.auditory",
        )
        visual_finding = probe_s1wu_perceptual_state(
            self.profile.visual_config,
            self.visual_state,
            visual.frame,
            f"probe.exposure.{index + 1}.visual",
        )
        return bind_avpc1_unambiguous_overlap_exposure_receipt(
            f"exposure.receipt.{index + 1}",
            audit_receptor_time_alignment(
                _sequence(auditory),
                _sequence(visual),
            ),
            auditory_binding,
            visual_binding,
            auditory_finding,
            visual_finding,
            state,
        )

    def audio_only_probe(self, value: float, state):
        field_start = self.partition.max_relation_field_window_end_tick + 10
        source_start = 100
        auditory = _timed(
            self.profile.auditory_config,
            token="later.probe",
            source_start=source_start,
            field_start=field_start,
            value=value,
        )
        visual = _timed(
            self.profile.visual_config,
            token="later.parent",
            source_start=source_start,
            field_start=field_start + 10,
            value=0.25,
        )
        auditory_sequence = _sequence(auditory)
        batch = BrowserReceptorSequenceBatch(
            self.contract.contract_id,
            self.contract.digest(),
            (auditory_sequence, _sequence(visual)),
        )
        source = bind_avpc1_private_auditory_probe_source(
            self.contract,
            batch,
        )
        envelope = bind_avpc1_private_auditory_only_probe_envelope(
            "binding.synthetic.relation.audio-only.v1",
            source,
            auditory_sequence,
            self.profile,
            self.auditory_state,
            self.partition,
        )
        finding = probe_s1wu_perceptual_state(
            self.profile.auditory_config,
            self.auditory_state,
            auditory.frame,
            "probe.synthetic.relation.later.auditory",
        )
        return probe_avpc1_bounded_relation_read_only(
            "probe.synthetic.relation.lookup",
            envelope,
            finding,
            state,
            self.visual_state,
            self.profile,
        )


def _advance_all(fixture: _Fixture, state):
    events = []
    for index in range(len(fixture.items)):
        result = advance_avpc1_bounded_relation_state(
            f"transition.{state.relation_table_id}.{index + 1}",
            state,
            fixture.receipt(index, state),
        )
        state = result.state
        events.append(result.receipt.event)
    return state, tuple(events)


class S2BQPrivateAVPC1BoundedRelationTests(unittest.TestCase):
    def test_initial_state_binds_frozen_content_and_partition(self) -> None:
        fixture = _Fixture(((-0.5, -0.5),))
        state = fixture.state("candidate.relation.table")
        self.assertEqual(2, len(state.slots))
        self.assertTrue(all(slot.status == "FREE" for slot in state.slots))
        self.assertIs(fixture.partition, state.relation_partition)
        self.assertEqual(3, len(state.auditory_prototype_inventory))
        self.assertEqual(3, len(state.visual_prototype_inventory))
        with self.assertRaises((FrozenInstanceError, AttributeError)):
            state.state_digest = "0" * 64  # type: ignore[misc]

    def test_duplicate_stabilized_prototype_fails_before_state(self) -> None:
        fixture = _Fixture(((-0.5, -0.5),))
        config = fixture.profile.auditory_config
        duplicate = replace(
            fixture.auditory_state,
            slots=(
                replace(fixture.auditory_state.slots[0], prototype_values=(0.0,) * len(config.carrier_ids)),
                replace(fixture.auditory_state.slots[1], prototype_values=(0.0,) * len(config.carrier_ids)),
                *fixture.auditory_state.slots[2:],
            ),
        )
        with self.assertRaises(AVPC1BoundedRelationError):
            initial_avpc1_bounded_relation_state(
                "candidate.relation.table",
                fixture.profile,
                duplicate,
                fixture.visual_state,
                fixture.partition,
            )

    def test_create_confirm_and_read_only_match(self) -> None:
        fixture = _Fixture(((-0.5, 0.5), (-0.5, 0.5)))
        state, events = _advance_all(
            fixture,
            fixture.state("candidate.relation.table"),
        )
        self.assertEqual(
            ("PAIR_CREATED_PENDING", "PAIR_CONFIRMED_STABLE"),
            events,
        )
        before = (state.state_digest, fixture.visual_state.digest())
        finding = fixture.audio_only_probe(-0.5, state)
        self.assertEqual("MATCH", finding.result_role)
        self.assertEqual(state.slots[0].visual_target_digest, finding.visual_prototype_identity_digest)
        self.assertEqual(before, (state.state_digest, fixture.visual_state.digest()))

    def test_crossed_histories_and_equal_generic_baseline_are_separate(self) -> None:
        fixture = _Fixture(
            ((-0.5, -0.5), (-0.5, -0.5), (0.5, 0.5), (0.5, 0.5))
        )
        candidate, candidate_events = _advance_all(
            fixture,
            fixture.state("candidate.relation.table"),
        )
        baseline, baseline_events = _advance_all(
            fixture,
            fixture.state("baseline.relation.table"),
        )
        self.assertNotEqual(candidate.state_identity_digest, baseline.state_identity_digest)
        self.assertEqual(candidate_events, baseline_events)
        for value in (-0.5, 0.5):
            candidate_finding = fixture.audio_only_probe(value, candidate)
            baseline_finding = fixture.audio_only_probe(value, baseline)
            self.assertEqual(candidate_finding.result_role, baseline_finding.result_role)
            self.assertEqual(
                candidate_finding.visual_prototype_identity_digest,
                baseline_finding.visual_prototype_identity_digest,
            )
        self.assertNotEqual(
            fixture.audio_only_probe(-0.5, candidate).visual_prototype_identity_digest,
            fixture.audio_only_probe(0.5, candidate).visual_prototype_identity_digest,
        )

    def test_conflict_is_absorbing_and_read_only_reports_no_match(self) -> None:
        fixture = _Fixture(((-0.5, -0.5), (-0.5, 0.5), (-0.5, -0.5)))
        state = fixture.state("candidate.relation.table")
        first = advance_avpc1_bounded_relation_state(
            "transition.conflict.1", state, fixture.receipt(0, state)
        )
        second = advance_avpc1_bounded_relation_state(
            "transition.conflict.2", first.state, fixture.receipt(1, first.state)
        )
        third = advance_avpc1_bounded_relation_state(
            "transition.conflict.3", second.state, fixture.receipt(2, second.state)
        )
        self.assertEqual("KEY_MARKED_CONFLICTED", second.receipt.event)
        self.assertEqual("CONFLICT_LOCKED_REJECTED", third.receipt.event)
        self.assertIs(third.state, second.state)
        self.assertEqual(
            "NO_MATCH_CONFLICT",
            fixture.audio_only_probe(-0.5, second.state).result_role,
        )

    def test_duplicate_capacity_saturation_and_budget_preserve_state(self) -> None:
        capacity_fixture = _Fixture(((-0.5, -0.5), (0.0, 0.0), (0.5, 0.5)))
        state = capacity_fixture.state("candidate.capacity.table")
        first_receipt = capacity_fixture.receipt(0, state)
        first = advance_avpc1_bounded_relation_state(
            "transition.capacity.1", state, first_receipt
        )
        duplicate = advance_avpc1_bounded_relation_state(
            "transition.capacity.duplicate", first.state, first_receipt
        )
        self.assertEqual("DUPLICATE_EXPOSURE_REJECTED", duplicate.receipt.event)
        self.assertIs(first.state, duplicate.state)
        second = advance_avpc1_bounded_relation_state(
            "transition.capacity.2",
            first.state,
            capacity_fixture.receipt(1, first.state),
        )
        full = advance_avpc1_bounded_relation_state(
            "transition.capacity.3",
            second.state,
            capacity_fixture.receipt(2, second.state),
        )
        self.assertEqual("CAPACITY_FULL_NEW_KEY_REJECTED", full.receipt.event)
        self.assertIs(second.state, full.state)

        budget_fixture = _Fixture(
            ((-0.5, -0.5), (-0.5, -0.5), (0.5, 0.5), (0.5, 0.5), (-0.5, -0.5))
        )
        budget_state = budget_fixture.state("candidate.budget.table")
        for index in range(4):
            budget_state = advance_avpc1_bounded_relation_state(
                f"transition.budget.{index + 1}",
                budget_state,
                budget_fixture.receipt(index, budget_state),
            ).state
        exhausted = advance_avpc1_bounded_relation_state(
            "transition.budget.5",
            budget_state,
            budget_fixture.receipt(4, budget_state),
        )
        self.assertEqual("EXPOSURE_BUDGET_EXHAUSTED_REJECTED", exhausted.receipt.event)
        self.assertIs(budget_state, exhausted.state)

        saturation_fixture = _Fixture(((-0.5, -0.5), (-0.5, -0.5), (-0.5, -0.5)))
        saturation_state = saturation_fixture.state("candidate.saturation.table")
        for index in range(2):
            saturation_state = advance_avpc1_bounded_relation_state(
                f"transition.saturation.{index + 1}",
                saturation_state,
                saturation_fixture.receipt(index, saturation_state),
            ).state
        saturated = advance_avpc1_bounded_relation_state(
            "transition.saturation.3",
            saturation_state,
            saturation_fixture.receipt(2, saturation_state),
        )
        self.assertEqual("SUPPORT_SATURATED_REJECTED", saturated.receipt.event)
        self.assertIs(saturation_state, saturated.state)

    def test_pending_and_unknown_read_only_results_are_exact(self) -> None:
        fixture = _Fixture(((-0.5, -0.5),))
        state = fixture.state("candidate.relation.table")
        pending = advance_avpc1_bounded_relation_state(
            "transition.pending.1", state, fixture.receipt(0, state)
        ).state
        self.assertEqual("NO_MATCH", fixture.audio_only_probe(-0.5, pending).result_role)
        unknown = fixture.audio_only_probe(0.5, pending)
        self.assertEqual("NO_MATCH", unknown.result_role)
        self.assertIsNone(unknown.selected_relation_slot_id)

    def test_wrong_partition_provenance_fails_closed(self) -> None:
        fixture = _Fixture(((-0.5, -0.5),))
        state = fixture.state("candidate.relation.table")
        _, visual, _, visual_binding = fixture.items[0]
        foreign = _timed(
            fixture.profile.auditory_config,
            token="foreign",
            source_start=20,
            field_start=0,
            value=-0.5,
        )
        with self.assertRaises(AVPC1BoundedRelationError) as caught:
            bind_avpc1_unambiguous_overlap_exposure_receipt(
                "exposure.receipt.foreign",
                audit_receptor_time_alignment(_sequence(foreign), _sequence(visual)),
                _timed_frame_binding(foreign),
                visual_binding,
                probe_s1wu_perceptual_state(
                    fixture.profile.auditory_config,
                    fixture.auditory_state,
                    foreign.frame,
                    "probe.foreign.auditory",
                ),
                probe_s1wu_perceptual_state(
                    fixture.profile.visual_config,
                    fixture.visual_state,
                    visual.frame,
                    "probe.foreign.visual",
                ),
                state,
            )
        self.assertEqual(AVPC1_RELATION_PROVENANCE_MISMATCH, caught.exception.code)

    def test_private_module_has_no_public_field_or_production_path(self) -> None:
        source = (
            ROOT / "mcm_field_organism" / "_avpc1_bounded_relation.py"
        ).read_text(encoding="ascii")
        for forbidden in (
            "advance_ppb1_bank",
            "SharedMCMField",
            "MCMNeuronDrive",
            "current_api",
            "root_lazy_exports",
            "live_audio",
            "live_video",
            "field_snapshot",
            "public_snapshot",
        ):
            self.assertNotIn(forbidden, source)
        public_names = set(getattr(current_api, "__all__", ())) | set(ROOT_LAZY_EXPORTS)
        self.assertFalse(any("avpc1" in name.lower() for name in public_names))


if __name__ == "__main__":
    unittest.main()
