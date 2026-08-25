from __future__ import annotations

from dataclasses import replace
from unittest.mock import patch
import unittest

import mcm_field_organism
import mcm_field_organism._avpc1_atomic_relation_formation_consumer as consumer
import mcm_field_organism._avpc1_bounded_relation as relation
import mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe as probe_module
from mcm_field_organism import current_api
from mcm_field_organism._avpc1_audio_only_probe_envelope import (
    bind_avpc1_frozen_relation_history_partition,
)
from mcm_field_organism._avpc1_bounded_relation import (
    AVPC1RelationTransitionReceipt,
    AVPC1RelationTransitionResult,
    AVPC1UnambiguousOverlapExposureReceipt,
    initial_avpc1_bounded_relation_state,
)
from mcm_field_organism._ppb1_active_batch_formation_consumer import (
    prepare_ppb1_active_batch_formation_consumer_owner,
)
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism._ppb1_reference import initial_ppb1_bank_state
from mcm_field_organism._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
)
from mcm_field_organism.browser_receptor_bridge import BrowserReceptorSequenceBatch
from mcm_field_organism.browser_world_contract import (
    BrowserWorldContract,
    BrowserWorldPhase,
)
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)


def _parameters() -> PPB1ProfileParameters:
    return PPB1ProfileParameters(
        PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
        PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
    )


def _world_contract() -> BrowserWorldContract:
    return BrowserWorldContract(
        "synthetic.s2cl.browser.world.v1",
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


def _sequence(
    config,
    values: tuple[float, ...],
    *,
    token: str,
    source_base: int,
    field_base: int,
) -> ReceptorTimeSequence:
    frames = tuple(
        OrganismTimedReceptorFrame(
            ReceptorContactFrame(
                config.modality_id,
                config.geometry_id,
                f"synthetic.{token}.{config.modality_id}.{index}",
                f"source.{config.modality_id}",
                source_base + index * 10,
                source_base + (index + 1) * 10,
                config.carrier_ids,
                tuple(value for _ in config.carrier_ids),
            ),
            CommonFieldTime(
                "field.synthetic",
                field_base + index * 20,
                field_base + index * 20 + 10,
            ),
        )
        for index, value in enumerate(values)
    )
    return ReceptorTimeSequence(
        config.modality_id,
        config.geometry_id,
        "field.synthetic",
        frames,
    )


def _envelope(contract, profile, binding_id, auditory, visual):
    batch = BrowserReceptorSequenceBatch(
        contract.contract_id,
        contract.digest(),
        (auditory, visual),
    )
    return bind_ppb1_active_receptor_batch(
        binding_id,
        contract,
        batch,
        profile,
    )


def _wrong_finding(
    finding: S1WUReadOnlyPerceptualFinding,
) -> S1WUReadOnlyPerceptualFinding:
    values = {
        name: getattr(finding, name)
        for name in finding.__dataclass_fields__
        if name not in {"finding_digest", "schema_version"}
    }
    values["recognized"] = not finding.recognized
    payload = finding.payload_without_digest()
    payload["recognized"] = values["recognized"]
    return S1WUReadOnlyPerceptualFinding(
        **values,
        finding_digest=probe_module._digest(payload),
    )


class _Fixture:
    def __init__(self, *, later_source_base: int = 100) -> None:
        self.contract = _world_contract()
        self.profile = bind_ppb1_receptor_profile("browser", _parameters())
        auditory_formation = _sequence(
            self.profile.auditory_config,
            (0.0,) * 6,
            token="formation",
            source_base=0,
            field_base=0,
        )
        visual_formation = _sequence(
            self.profile.visual_config,
            (-0.5, -0.5, -0.5, 0.5, 0.5, 0.5),
            token="formation",
            source_base=0,
            field_base=0,
        )
        self.formation_envelope = _envelope(
            self.contract,
            self.profile,
            "binding.s2cl.formation.v1",
            auditory_formation,
            visual_formation,
        )
        auditory_fresh = initial_ppb1_bank_state(self.profile.auditory_config)
        visual_fresh = initial_ppb1_bank_state(self.profile.visual_config)
        formation_owner = prepare_ppb1_active_batch_formation_consumer_owner(
            "owner.s2cl.formation.v1",
            "authorization.s2cl.formation.v1",
            "consumption.s2cl.formation.v1",
            self.formation_envelope.envelope_digest,
            self.profile.digest(),
            auditory_fresh.digest(),
            visual_fresh.digest(),
        )
        self.formation_result = formation_owner.consume_once(
            self.formation_envelope,
            self.profile,
            auditory_fresh,
            visual_fresh,
        )
        auditory_later = _sequence(
            self.profile.auditory_config,
            (0.0, 0.0, 0.0),
            token=f"later.{later_source_base}",
            source_base=later_source_base,
            field_base=200,
        )
        visual_later = _sequence(
            self.profile.visual_config,
            (-0.5, -0.5, 0.5),
            token=f"later.{later_source_base}",
            source_base=later_source_base,
            field_base=200,
        )
        self.later_envelope = _envelope(
            self.contract,
            self.profile,
            f"binding.s2cl.later.{later_source_base}.v1",
            auditory_later,
            visual_later,
        )
        partition_items = tuple(
            (modality, binding)
            for modality, stream in (
                ("auditory", self.later_envelope.auditory_stream),
                ("visual", self.later_envelope.visual_stream),
            )
            for binding in stream.timed_frames
        )
        self.partition = bind_avpc1_frozen_relation_history_partition(
            partition_items
        )
        self.initial_state = initial_avpc1_bounded_relation_state(
            "relation.s2cl.candidate.v1",
            self.profile,
            self.formation_result.auditory_poststate,
            self.formation_result.visual_poststate,
            self.partition,
        )

    def bindings(self, index: int):
        return (
            self.later_envelope.auditory_stream.timed_frames[index],
            self.later_envelope.visual_stream.timed_frames[index],
        )

    def owner(self, index: int, state, *, auditory=None, visual=None, partition=None):
        bound_auditory, bound_visual = self.bindings(index)
        auditory = bound_auditory if auditory is None else auditory
        visual = bound_visual if visual is None else visual
        partition = self.partition if partition is None else partition
        return consumer.prepare_avpc1_atomic_relation_formation_consumer_owner(
            f"owner.s2cl.relation.{index}.{state.accepted_exposure_count}",
            f"consumption.s2cl.relation.{index}.{state.accepted_exposure_count}",
            f"probe.s2cl.auditory.{index}",
            f"probe.s2cl.visual.{index}",
            f"exposure.s2cl.{index}",
            f"transition.s2cl.{index}.{state.accepted_exposure_count}",
            self.formation_result.formation_result_digest,
            self.formation_envelope.envelope_digest,
            self.later_envelope.envelope_digest,
            self.profile.digest(),
            partition.relation_history_partition_digest,
            auditory.timed_frame_provenance_digest,
            visual.timed_frame_provenance_digest,
            state.state_identity_digest,
            state.state_digest,
        )

    def consume(
        self,
        owner,
        state,
        index: int,
        *,
        auditory=None,
        visual=None,
        partition=None,
        formation_envelope=None,
    ):
        bound_auditory, bound_visual = self.bindings(index)
        return owner.consume_once(
            self.formation_result,
            self.formation_envelope if formation_envelope is None else formation_envelope,
            self.later_envelope,
            self.profile,
            self.partition if partition is None else partition,
            bound_auditory if auditory is None else auditory,
            bound_visual if visual is None else visual,
            state,
        )


class S2CLPrivateAtomicRelationFormationConsumerTests(unittest.TestCase):
    def test_valid_first_later_overlap_creates_pending_pair(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner(0, fixture.initial_state)
        result = fixture.consume(owner, fixture.initial_state, 0)
        self.assertEqual("PAIR_CREATED_PENDING", result.transition.receipt.event)
        self.assertEqual("CONSUMED", owner.snapshot().status)
        self.assertEqual(1, result.transition.state.accepted_exposure_count)

    def test_valid_second_distinct_later_overlap_confirms_pair_stable(self) -> None:
        fixture = _Fixture()
        first = fixture.consume(
            fixture.owner(0, fixture.initial_state), fixture.initial_state, 0
        )
        state = first.transition.state
        second = fixture.consume(fixture.owner(1, state), state, 1)
        self.assertEqual("PAIR_CONFIRMED_STABLE", second.transition.receipt.event)
        selected = next(
            slot
            for slot in second.transition.state.slots
            if slot.slot_id == second.transition.receipt.selected_slot_id
        )
        self.assertEqual(("STABLE", 2), (selected.status, selected.support_count))

    def test_valid_third_conflicting_target_marks_key_conflicted(self) -> None:
        fixture = _Fixture()
        first = fixture.consume(
            fixture.owner(0, fixture.initial_state), fixture.initial_state, 0
        )
        second = fixture.consume(
            fixture.owner(1, first.transition.state), first.transition.state, 1
        )
        third = fixture.consume(
            fixture.owner(2, second.transition.state), second.transition.state, 2
        )
        self.assertEqual("KEY_MARKED_CONFLICTED", third.transition.receipt.event)
        selected = next(
            slot
            for slot in third.transition.state.slots
            if slot.slot_id == third.transition.receipt.selected_slot_id
        )
        self.assertEqual("CONFLICTED", selected.status)

    def test_formation_history_frame_is_rejected_before_probe(self) -> None:
        fixture = _Fixture()
        auditory = fixture.formation_envelope.auditory_stream.timed_frames[-1]
        visual = fixture.bindings(0)[1]
        owner = fixture.owner(
            0, fixture.initial_state, auditory=auditory, visual=visual
        )
        with patch.object(consumer, "probe_s1wu_perceptual_state") as probe:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(
                    owner,
                    fixture.initial_state,
                    0,
                    auditory=auditory,
                    visual=visual,
                )
        probe.assert_not_called()
        self.assertEqual("FAILED", owner.snapshot().status)

    def test_wrong_formation_result_envelope_or_profile_is_terminal_before_child(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner(0, fixture.initial_state)
        with patch.object(consumer, "audit_receptor_time_alignment") as audit:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(
                    owner,
                    fixture.initial_state,
                    0,
                    formation_envelope=fixture.later_envelope,
                )
        audit.assert_not_called()
        self.assertEqual("FAILED", owner.snapshot().status)

    def test_not_causally_later_exposure_is_terminal_before_child(self) -> None:
        fixture = _Fixture(later_source_base=20)
        owner = fixture.owner(0, fixture.initial_state)
        with patch.object(consumer, "audit_receptor_time_alignment") as audit:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(owner, fixture.initial_state, 0)
        audit.assert_not_called()

    def test_later_envelope_membership_mismatch_is_terminal_before_child(self) -> None:
        fixture = _Fixture()
        visual = fixture.bindings(0)[1]
        owner = fixture.owner(
            0, fixture.initial_state, auditory=visual, visual=visual
        )
        with patch.object(consumer, "audit_receptor_time_alignment") as audit:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(
                    owner,
                    fixture.initial_state,
                    0,
                    auditory=visual,
                    visual=visual,
                )
        audit.assert_not_called()

    def test_partition_inventory_or_object_mismatch_is_terminal_before_child(self) -> None:
        fixture = _Fixture()
        items = tuple(
            reversed(
                tuple(
                    (modality, binding)
                    for modality, stream in (
                        ("auditory", fixture.later_envelope.auditory_stream),
                        ("visual", fixture.later_envelope.visual_stream),
                    )
                    for binding in stream.timed_frames
                )
            )
        )
        wrong_partition = bind_avpc1_frozen_relation_history_partition(items)
        owner = fixture.owner(
            0, fixture.initial_state, partition=wrong_partition
        )
        with patch.object(consumer, "audit_receptor_time_alignment") as audit:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(
                    owner,
                    fixture.initial_state,
                    0,
                    partition=wrong_partition,
                )
        audit.assert_not_called()

    def test_derived_ambiguous_audit_stops_before_probes(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner(0, fixture.initial_state)
        original = consumer.audit_receptor_time_alignment

        def ambiguous(*args, **kwargs):
            audit = original(*args, **kwargs)
            return replace(
                audit,
                ambiguous_snapshot_ids=(fixture.bindings(0)[0].snapshot_id,),
            )

        with patch.object(
            consumer, "audit_receptor_time_alignment", side_effect=ambiguous
        ), patch.object(consumer, "probe_s1wu_perceptual_state") as probe:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(owner, fixture.initial_state, 0)
        probe.assert_not_called()

    def test_digest_consistent_wrong_finding_stops_before_exposure_binder(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner(0, fixture.initial_state)
        original = consumer.probe_s1wu_perceptual_state
        call_count = 0

        def wrong_second(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            finding = original(*args, **kwargs)
            return finding if call_count == 1 else _wrong_finding(finding)

        with patch.object(
            consumer, "probe_s1wu_perceptual_state", side_effect=wrong_second
        ), patch.object(
            consumer, "bind_avpc1_unambiguous_overlap_exposure_receipt"
        ) as binder:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(owner, fixture.initial_state, 0)
        binder.assert_not_called()

    def test_wrong_exposure_transition_or_child_exception_exposes_no_result(self) -> None:
        fixture = _Fixture()
        original_binder = consumer.bind_avpc1_unambiguous_overlap_exposure_receipt

        def wrong_exposure(*args, **kwargs):
            value = original_binder(*args, **kwargs)
            fields = {
                name: getattr(value, name)
                for name in value.__dataclass_fields__
                if name != "exposure_receipt_digest"
            }
            fields["visual_prototype_digest"] = (
                fixture.initial_state.visual_prototype_inventory[1]
            )
            return AVPC1UnambiguousOverlapExposureReceipt(
                **fields,
                exposure_receipt_digest=relation._digest(
                    {"schema_version": relation.AVPC1_RELATION_SCHEMA_VERSION, **fields}
                ),
            )

        owner = fixture.owner(0, fixture.initial_state)
        with patch.object(
            consumer,
            "bind_avpc1_unambiguous_overlap_exposure_receipt",
            side_effect=wrong_exposure,
        ), patch.object(consumer, "advance_avpc1_bounded_relation_state") as advance:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(owner, fixture.initial_state, 0)
        advance.assert_not_called()
        self.assertIsNone(owner.snapshot().committed_result_digest)

        fixture = _Fixture()
        owner = fixture.owner(0, fixture.initial_state)
        original_advance = consumer.advance_avpc1_bounded_relation_state

        def wrong_transition(*args, **kwargs):
            result = original_advance(*args, **kwargs)
            receipt_values = result.receipt.payload_without_digest()
            receipt_values.pop("schema_version")
            receipt_values["selected_slot_id"] = "avpc1.relation.slot.001"
            receipt = AVPC1RelationTransitionReceipt(
                **receipt_values,
                transition_receipt_digest=relation._digest(
                    {
                        "schema_version": relation.AVPC1_RELATION_SCHEMA_VERSION,
                        **receipt_values,
                    }
                ),
            )
            return AVPC1RelationTransitionResult(result.state, receipt)

        with patch.object(
            consumer,
            "advance_avpc1_bounded_relation_state",
            side_effect=wrong_transition,
        ):
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(owner, fixture.initial_state, 0)
        self.assertIsNone(owner.snapshot().committed_result_digest)

        fixture = _Fixture()
        owner = fixture.owner(0, fixture.initial_state)
        with patch.object(
            consumer,
            "audit_receptor_time_alignment",
            side_effect=RuntimeError("synthetic child failure"),
        ):
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError):
                fixture.consume(owner, fixture.initial_state, 0)
        self.assertEqual("FAILED", owner.snapshot().status)

    def test_recursive_retry_and_terminal_reuse_reach_no_extra_child(self) -> None:
        fixture = _Fixture()
        owner = fixture.owner(0, fixture.initial_state)
        original = consumer.audit_receptor_time_alignment
        recursive_codes: list[str] = []

        def recursive(*args, **kwargs):
            try:
                fixture.consume(owner, fixture.initial_state, 0)
            except consumer.AVPC1AtomicRelationFormationConsumerError as exc:
                recursive_codes.append(exc.code)
            return original(*args, **kwargs)

        with patch.object(
            consumer, "audit_receptor_time_alignment", side_effect=recursive
        ) as audit:
            result = fixture.consume(owner, fixture.initial_state, 0)
        self.assertEqual([consumer.AVPC1_ATOMIC_RELATION_FORMATION_OWNER_BUSY], recursive_codes)
        self.assertEqual(1, audit.call_count)
        self.assertEqual("CONSUMED", result.authorization_poststate.status)

        with patch.object(consumer, "audit_receptor_time_alignment") as retry_audit:
            with self.assertRaises(consumer.AVPC1AtomicRelationFormationConsumerError) as caught:
                fixture.consume(owner, fixture.initial_state, 0)
        self.assertEqual(
            consumer.AVPC1_ATOMIC_RELATION_FORMATION_OWNER_TERMINAL,
            caught.exception.code,
        )
        retry_audit.assert_not_called()
        self.assertFalse(
            hasattr(mcm_field_organism, "AVPC1AtomicRelationFormationConsumerOwner")
        )
        self.assertNotIn(
            "AVPC1AtomicRelationFormationConsumerOwner",
            current_api.__all__,
        )


if __name__ == "__main__":
    unittest.main()
