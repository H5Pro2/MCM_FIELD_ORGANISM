"""Private atomic owner for one later AVPC-1 relation exposure."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import re
from threading import Lock

from ._avpc1_audio_only_probe_envelope import (
    AVPC1FrozenRelationHistoryPartitionBinding,
)
from ._avpc1_bounded_relation import (
    AVPC1BoundedRelationError,
    AVPC1BoundedRelationState,
    AVPC1RelationSlot,
    AVPC1RelationTransitionResult,
    AVPC1UnambiguousOverlapExposureReceipt,
    _alignment_payload,
    _stable_inventory,
    advance_avpc1_bounded_relation_state,
    bind_avpc1_unambiguous_overlap_exposure_receipt,
)
from ._ppb1_active_batch_formation_consumer import (
    PPB1ActiveBatchFormationResult,
)
from ._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorTimedFrameBinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import PPB1BankConfig, PPB1BankState, normalized_mean_l1_distance
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
    _prototype_digest,
    probe_s1wu_perceptual_state,
)
from .receptor_contract import ReceptorContactFrame, technical_identifier
from .receptor_time_alignment import (
    ReceptorTimeAlignmentAudit,
    ReceptorTimeOverlap,
    audit_receptor_time_alignment,
)
from .receptor_time_model import ReceptorTimeSequence


AVPC1_ATOMIC_RELATION_FORMATION_SCHEMA_VERSION = (
    "avpc1.private.atomic-relation-formation-consumer.v1"
)
AVPC1_ATOMIC_RELATION_FORMATION_CONTRACT_DIGEST = (
    "753f8865b028356317d149f78542d2da272245433eec0b2c066bdda2712aed1d"
)
AVPC1_ATOMIC_RELATION_FORMATION_PREFLIGHT_DIGEST = (
    "6c1005d3f4502d2c5482a44604423915f6aa1f1ff1f28bdca3f32a6ec763aed6"
)

AVPC1_ATOMIC_RELATION_FORMATION_INVALID_INPUT = (
    "AVPC1_ATOMIC_RELATION_FORMATION_INVALID_INPUT"
)
AVPC1_ATOMIC_RELATION_FORMATION_OWNER_BUSY = (
    "AVPC1_ATOMIC_RELATION_FORMATION_OWNER_BUSY"
)
AVPC1_ATOMIC_RELATION_FORMATION_OWNER_TERMINAL = (
    "AVPC1_ATOMIC_RELATION_FORMATION_OWNER_TERMINAL"
)
AVPC1_ATOMIC_RELATION_FORMATION_SOURCE_MISMATCH = (
    "AVPC1_ATOMIC_RELATION_FORMATION_SOURCE_MISMATCH"
)
AVPC1_ATOMIC_RELATION_FORMATION_CAUSALITY_MISMATCH = (
    "AVPC1_ATOMIC_RELATION_FORMATION_CAUSALITY_MISMATCH"
)
AVPC1_ATOMIC_RELATION_FORMATION_ALIGNMENT_MISMATCH = (
    "AVPC1_ATOMIC_RELATION_FORMATION_ALIGNMENT_MISMATCH"
)
AVPC1_ATOMIC_RELATION_FORMATION_FINDING_MISMATCH = (
    "AVPC1_ATOMIC_RELATION_FORMATION_FINDING_MISMATCH"
)
AVPC1_ATOMIC_RELATION_FORMATION_EXPOSURE_MISMATCH = (
    "AVPC1_ATOMIC_RELATION_FORMATION_EXPOSURE_MISMATCH"
)
AVPC1_ATOMIC_RELATION_FORMATION_TRANSITION_MISMATCH = (
    "AVPC1_ATOMIC_RELATION_FORMATION_TRANSITION_MISMATCH"
)
AVPC1_ATOMIC_RELATION_FORMATION_TRANSITION_REJECTED = (
    "AVPC1_ATOMIC_RELATION_FORMATION_TRANSITION_REJECTED"
)
AVPC1_ATOMIC_RELATION_FORMATION_ATTEMPT_FAILED = (
    "AVPC1_ATOMIC_RELATION_FORMATION_ATTEMPT_FAILED"
)
AVPC1_ATOMIC_RELATION_FORMATION_ATOMIC_RESULT_REQUIRED = (
    "AVPC1_ATOMIC_RELATION_FORMATION_ATOMIC_RESULT_REQUIRED"
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_ACCEPTED_EVENTS = {
    "PAIR_CREATED_PENDING",
    "PAIR_CONFIRMED_STABLE",
    "KEY_MARKED_CONFLICTED",
}


class AVPC1AtomicRelationFormationConsumerError(ValueError):
    """One fail-closed private relation-formation boundary violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST_RE.fullmatch(value) is not None


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise AVPC1AtomicRelationFormationConsumerError(
            AVPC1_ATOMIC_RELATION_FORMATION_INVALID_INPUT,
            str(exc),
        ) from exc


def _state_identity_digest(state: PPB1BankState) -> str:
    return _digest(_state_identity_payload(state))


def _sequence_from_stream(
    envelope: PPB1ActiveReceptorBatchEnvelope,
    modality_id: str,
) -> ReceptorTimeSequence:
    stream = (
        envelope.auditory_stream
        if modality_id == "auditory"
        else envelope.visual_stream
    )
    return ReceptorTimeSequence(
        stream.modality_id,
        stream.geometry_id,
        envelope.common_field_clock_id,
        tuple(item.timed_frame for item in stream.timed_frames),
    )


def _canonical_partition_inventory(
    envelope: PPB1ActiveReceptorBatchEnvelope,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    int,
]:
    items = tuple(
        (modality_id, binding)
        for modality_id, stream in (
            ("auditory", envelope.auditory_stream),
            ("visual", envelope.visual_stream),
        )
        for binding in stream.timed_frames
    )
    return (
        tuple(modality for modality, _ in items),
        tuple(binding.snapshot_id for _, binding in items),
        tuple(binding.timed_frame_provenance_digest for _, binding in items),
        max(binding.field_window_end_tick for _, binding in items),
    )


def _expected_alignment_audit(
    envelope: PPB1ActiveReceptorBatchEnvelope,
) -> ReceptorTimeAlignmentAudit:
    auditory = envelope.auditory_stream.timed_frames
    visual = envelope.visual_stream.timed_frames
    degree = {
        binding.snapshot_id: 0
        for stream in (auditory, visual)
        for binding in stream
    }
    overlaps: list[ReceptorTimeOverlap] = []
    for auditory_item in auditory:
        for visual_item in visual:
            start = max(
                auditory_item.field_window_start_tick,
                visual_item.field_window_start_tick,
            )
            end = min(
                auditory_item.field_window_end_tick,
                visual_item.field_window_end_tick,
            )
            if start >= end:
                continue
            overlap = ReceptorTimeOverlap(
                auditory_item.snapshot_id,
                visual_item.snapshot_id,
                start,
                end,
            )
            overlaps.append(overlap)
            degree[overlap.first_snapshot_id] += 1
            degree[overlap.second_snapshot_id] += 1
    unambiguous = tuple(
        item
        for item in overlaps
        if degree[item.first_snapshot_id] == 1
        and degree[item.second_snapshot_id] == 1
    )
    ambiguous = {
        snapshot_id
        for item in overlaps
        if degree[item.first_snapshot_id] > 1
        or degree[item.second_snapshot_id] > 1
        for snapshot_id in (item.first_snapshot_id, item.second_snapshot_id)
    }
    return ReceptorTimeAlignmentAudit(
        clock_id=envelope.common_field_clock_id,
        modality_ids=("auditory", "visual"),
        frame_counts=(len(auditory), len(visual)),
        overlaps=tuple(overlaps),
        unambiguous_overlaps=unambiguous,
        ambiguous_snapshot_ids=tuple(sorted(ambiguous)),
        unmatched_snapshot_ids=tuple(
            sorted(snapshot_id for snapshot_id, count in degree.items() if count == 0)
        ),
    )


def _source_snapshot(
    formation_result: PPB1ActiveBatchFormationResult,
    formation_envelope: PPB1ActiveReceptorBatchEnvelope,
    later_envelope: PPB1ActiveReceptorBatchEnvelope,
    profile: PPB1ReceptorProfileBinding,
    partition: AVPC1FrozenRelationHistoryPartitionBinding,
    auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
    relation_state: AVPC1BoundedRelationState,
) -> tuple[str, ...]:
    return (
        formation_result.formation_result_digest,
        formation_envelope.envelope_digest,
        later_envelope.envelope_digest,
        profile.digest(),
        partition.relation_history_partition_digest,
        auditory.timed_frame_provenance_digest,
        visual.timed_frame_provenance_digest,
        relation_state.state_identity_digest,
        relation_state.state_digest,
        formation_result.auditory_poststate.digest(),
        formation_result.visual_poststate.digest(),
    )


def _finding_payload(finding: S1WUReadOnlyPerceptualFinding) -> dict[str, object]:
    return finding.canonical_payload()


def _exposure_payload(
    exposure: AVPC1UnambiguousOverlapExposureReceipt,
) -> dict[str, object]:
    return {
        **exposure.payload_without_digest(),
        "exposure_receipt_digest": exposure.exposure_receipt_digest,
    }


def _transition_payload(result: AVPC1RelationTransitionResult) -> dict[str, object]:
    return {
        "state_digest": result.state.state_digest,
        "transition_receipt": {
            **result.receipt.payload_without_digest(),
            "transition_receipt_digest": result.receipt.transition_receipt_digest,
        },
    }


@dataclass(frozen=True, slots=True)
class AVPC1AtomicRelationFormationOwnerSnapshot:
    owner_id: str
    consumption_id: str
    auditory_probe_id: str
    visual_probe_id: str
    exposure_id: str
    transition_id: str
    authorized_formation_result_digest: str
    authorized_formation_envelope_digest: str
    authorized_later_exposure_envelope_digest: str
    authorized_profile_binding_digest: str
    authorized_relation_partition_digest: str
    authorized_auditory_frame_provenance_digest: str
    authorized_visual_frame_provenance_digest: str
    authorized_relation_prestate_identity_digest: str
    authorized_relation_prestate_digest: str
    status: str
    attempt_count: int
    use_count: int
    generation: int
    committed_result_digest: str | None
    failure_code: str | None
    failure_digest: str | None
    owner_state_digest: str

    def __post_init__(self) -> None:
        for role in (
            "owner_id",
            "consumption_id",
            "auditory_probe_id",
            "visual_probe_id",
            "exposure_id",
            "transition_id",
        ):
            _identifier(getattr(self, role), role)
        digests = (
            self.authorized_formation_result_digest,
            self.authorized_formation_envelope_digest,
            self.authorized_later_exposure_envelope_digest,
            self.authorized_profile_binding_digest,
            self.authorized_relation_partition_digest,
            self.authorized_auditory_frame_provenance_digest,
            self.authorized_visual_frame_provenance_digest,
            self.authorized_relation_prestate_identity_digest,
            self.authorized_relation_prestate_digest,
        )
        valid_shape = (
            self.status in {"AUTHORIZED", "IN_PROGRESS", "CONSUMED", "FAILED"}
            and self.attempt_count in {0, 1}
            and self.use_count in {0, 1}
            and self.generation in {0, 1}
            and all(_valid_digest(value) for value in digests)
        )
        if self.status == "AUTHORIZED":
            valid_shape = valid_shape and (
                self.attempt_count,
                self.use_count,
                self.generation,
                self.committed_result_digest,
                self.failure_code,
                self.failure_digest,
            ) == (0, 0, 0, None, None, None)
        elif self.status == "IN_PROGRESS":
            valid_shape = valid_shape and (
                self.attempt_count,
                self.use_count,
                self.generation,
                self.committed_result_digest,
                self.failure_code,
                self.failure_digest,
            ) == (1, 0, 0, None, None, None)
        elif self.status == "CONSUMED":
            valid_shape = valid_shape and (
                self.attempt_count == self.use_count == self.generation == 1
                and _valid_digest(self.committed_result_digest)
                and self.failure_code is None
                and self.failure_digest is None
            )
        else:
            valid_shape = valid_shape and (
                self.attempt_count == self.generation == 1
                and self.use_count == 0
                and self.committed_result_digest is None
                and isinstance(self.failure_code, str)
                and bool(self.failure_code)
                and _valid_digest(self.failure_digest)
            )
        if (
            not valid_shape
            or not _valid_digest(self.owner_state_digest)
            or self.owner_state_digest != _digest(self.payload_without_digest())
        ):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_ATOMIC_RESULT_REQUIRED,
                "owner snapshot is incomplete or inconsistent",
            )

    def result_projection_payload(self) -> dict[str, object]:
        payload = self.payload_without_digest()
        payload.pop("committed_result_digest")
        return payload

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": AVPC1_ATOMIC_RELATION_FORMATION_SCHEMA_VERSION,
            **{
                name: getattr(self, name)
                for name in self.__dataclass_fields__
                if name != "owner_state_digest"
            },
        }


@dataclass(frozen=True, slots=True)
class AVPC1AtomicRelationFormationResult:
    consumption_id: str
    formation_result_digest: str
    formation_envelope_digest: str
    later_exposure_envelope_digest: str
    profile_binding_digest: str
    relation_partition_digest: str
    auditory_frame_provenance_digest: str
    visual_frame_provenance_digest: str
    alignment_audit_digest: str
    auditory_finding: S1WUReadOnlyPerceptualFinding
    visual_finding: S1WUReadOnlyPerceptualFinding
    exposure_receipt: AVPC1UnambiguousOverlapExposureReceipt
    relation_prestate_identity_digest: str
    relation_prestate_digest: str
    transition: AVPC1RelationTransitionResult
    authorization_poststate: AVPC1AtomicRelationFormationOwnerSnapshot
    result_digest: str

    def __post_init__(self) -> None:
        _identifier(self.consumption_id, "consumption_id")
        digest_roles = (
            self.formation_result_digest,
            self.formation_envelope_digest,
            self.later_exposure_envelope_digest,
            self.profile_binding_digest,
            self.relation_partition_digest,
            self.auditory_frame_provenance_digest,
            self.visual_frame_provenance_digest,
            self.alignment_audit_digest,
            self.relation_prestate_identity_digest,
            self.relation_prestate_digest,
            self.result_digest,
        )
        if (
            not all(_valid_digest(value) for value in digest_roles)
            or type(self.auditory_finding) is not S1WUReadOnlyPerceptualFinding
            or type(self.visual_finding) is not S1WUReadOnlyPerceptualFinding
            or type(self.exposure_receipt)
            is not AVPC1UnambiguousOverlapExposureReceipt
            or type(self.transition) is not AVPC1RelationTransitionResult
            or type(self.authorization_poststate)
            is not AVPC1AtomicRelationFormationOwnerSnapshot
            or self.authorization_poststate.status != "CONSUMED"
            or self.authorization_poststate.consumption_id != self.consumption_id
            or self.authorization_poststate.committed_result_digest
            != self.result_digest
            or self.exposure_receipt.auditory_finding_digest
            != self.auditory_finding.finding_digest
            or self.exposure_receipt.visual_finding_digest
            != self.visual_finding.finding_digest
            or self.transition.receipt.exposure_receipt_digest
            != self.exposure_receipt.exposure_receipt_digest
            or self.transition.receipt.prestate_digest != self.relation_prestate_digest
            or not self.transition.receipt.state_changed
            or self.transition.receipt.event not in _ACCEPTED_EVENTS
            or self.result_digest != _digest(self.payload_without_digest())
        ):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_ATOMIC_RESULT_REQUIRED,
                "relation formation result is incomplete or inconsistent",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": AVPC1_ATOMIC_RELATION_FORMATION_SCHEMA_VERSION,
            "contract_digest": AVPC1_ATOMIC_RELATION_FORMATION_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_ATOMIC_RELATION_FORMATION_PREFLIGHT_DIGEST,
            "consumption_id": self.consumption_id,
            "formation_result_digest": self.formation_result_digest,
            "formation_envelope_digest": self.formation_envelope_digest,
            "later_exposure_envelope_digest": self.later_exposure_envelope_digest,
            "profile_binding_digest": self.profile_binding_digest,
            "relation_partition_digest": self.relation_partition_digest,
            "auditory_frame_provenance_digest": (
                self.auditory_frame_provenance_digest
            ),
            "visual_frame_provenance_digest": self.visual_frame_provenance_digest,
            "alignment_audit_digest": self.alignment_audit_digest,
            "auditory_finding": _finding_payload(self.auditory_finding),
            "visual_finding": _finding_payload(self.visual_finding),
            "exposure_receipt": _exposure_payload(self.exposure_receipt),
            "relation_prestate_identity_digest": self.relation_prestate_identity_digest,
            "relation_prestate_digest": self.relation_prestate_digest,
            "transition": _transition_payload(self.transition),
            "authorization_poststate": (
                self.authorization_poststate.result_projection_payload()
            ),
        }


def _snapshot_values(
    owner: AVPC1AtomicRelationFormationConsumerOwner,
) -> dict[str, object]:
    return {
        "owner_id": owner._owner_id,
        "consumption_id": owner._consumption_id,
        "auditory_probe_id": owner._auditory_probe_id,
        "visual_probe_id": owner._visual_probe_id,
        "exposure_id": owner._exposure_id,
        "transition_id": owner._transition_id,
        "authorized_formation_result_digest": owner._formation_result_digest,
        "authorized_formation_envelope_digest": owner._formation_envelope_digest,
        "authorized_later_exposure_envelope_digest": owner._later_envelope_digest,
        "authorized_profile_binding_digest": owner._profile_digest,
        "authorized_relation_partition_digest": owner._partition_digest,
        "authorized_auditory_frame_provenance_digest": owner._auditory_digest,
        "authorized_visual_frame_provenance_digest": owner._visual_digest,
        "authorized_relation_prestate_identity_digest": owner._relation_identity,
        "authorized_relation_prestate_digest": owner._relation_digest,
        "status": owner._status,
        "attempt_count": owner._attempt_count,
        "use_count": owner._use_count,
        "generation": owner._generation,
        "committed_result_digest": owner._committed_result_digest,
        "failure_code": owner._failure_code,
        "failure_digest": owner._failure_digest,
    }


def _make_snapshot(
    owner: AVPC1AtomicRelationFormationConsumerOwner,
) -> AVPC1AtomicRelationFormationOwnerSnapshot:
    values = _snapshot_values(owner)
    payload = {
        "schema_version": AVPC1_ATOMIC_RELATION_FORMATION_SCHEMA_VERSION,
        **values,
    }
    return AVPC1AtomicRelationFormationOwnerSnapshot(
        **values,
        owner_state_digest=_digest(payload),
    )


def _expected_finding(
    probe_id: str,
    config: PPB1BankConfig,
    state: PPB1BankState,
    frame: ReceptorContactFrame,
) -> tuple[object, ...]:
    eligible = tuple(
        slot
        for slot in state.slots
        if (
            slot.occupied
            and slot.support_count is not None
            and slot.support_count >= config.stable_after
        )
    )
    candidates = tuple(
        (
            normalized_mean_l1_distance(frame.values, slot.prototype_values),
            slot.slot_id,
            slot,
        )
        for slot in eligible
    )
    if candidates:
        distance, slot_id, selected = min(candidates)
        recognized = distance <= config.match_threshold
        prototype_digest = _prototype_digest(selected.prototype_values)
    else:
        distance = None
        slot_id = None
        recognized = False
        prototype_digest = None
    return (
        probe_id,
        config.bank_id,
        config.modality_id,
        config.digest(),
        state.digest(),
        _state_identity_digest(state),
        len(eligible),
        recognized,
        slot_id,
        distance,
        prototype_digest,
    )


def _validate_finding(
    finding: object,
    probe_id: str,
    config: PPB1BankConfig,
    state: PPB1BankState,
    binding: PPB1ActiveReceptorTimedFrameBinding,
) -> S1WUReadOnlyPerceptualFinding:
    if type(finding) is not S1WUReadOnlyPerceptualFinding:
        raise AVPC1AtomicRelationFormationConsumerError(
            AVPC1_ATOMIC_RELATION_FORMATION_FINDING_MISMATCH,
            "read-only child returned the wrong type",
        )
    observed = (
        finding.probe_id,
        finding.bank_id,
        finding.modality_id,
        finding.bank_config_digest,
        finding.observed_bank_state_digest,
        finding.state_identity_digest,
        finding.eligible_slot_count,
        finding.recognized,
        finding.selected_slot_id,
        finding.match_distance,
        finding.selected_prototype_digest,
    )
    if (
        observed != _expected_finding(probe_id, config, state, binding.timed_frame.frame)
        or finding.probe_input_digest != binding.ppb1_input_projection_digest
        or not finding.recognized
    ):
        raise AVPC1AtomicRelationFormationConsumerError(
            AVPC1_ATOMIC_RELATION_FORMATION_FINDING_MISMATCH,
            "read-only finding does not match the frozen exposure source",
        )
    return finding


def _expected_transition(
    state: AVPC1BoundedRelationState,
    exposure: AVPC1UnambiguousOverlapExposureReceipt,
) -> tuple[str, str | None, bool, tuple[AVPC1RelationSlot, ...]]:
    slots = list(state.slots)
    existing = next(
        (
            slot
            for slot in slots
            if slot.auditory_key_digest == exposure.auditory_prototype_digest
        ),
        None,
    )
    selected = None
    changed = False
    if exposure.exposure_receipt_digest in state.consumed_exposure_receipt_digests:
        event = "DUPLICATE_EXPOSURE_REJECTED"
    elif state.accepted_exposure_count >= 4:
        event = "EXPOSURE_BUDGET_EXHAUSTED_REJECTED"
    elif existing and existing.status == "CONFLICTED":
        event = "CONFLICT_LOCKED_REJECTED"
        selected = existing.slot_id
    elif (
        existing
        and existing.visual_target_digest == exposure.visual_prototype_digest
        and existing.status == "PENDING"
    ):
        event = "PAIR_CONFIRMED_STABLE"
        selected = existing.slot_id
        changed = True
        slots[slots.index(existing)] = replace(
            existing,
            status="STABLE",
            support_count=2,
        )
    elif (
        existing
        and existing.visual_target_digest == exposure.visual_prototype_digest
        and existing.status == "STABLE"
    ):
        event = "SUPPORT_SATURATED_REJECTED"
        selected = existing.slot_id
    elif existing:
        event = "KEY_MARKED_CONFLICTED"
        selected = existing.slot_id
        changed = True
        conflict = _digest(
            {
                "visual_target_digests": sorted(
                    (
                        existing.visual_target_digest,
                        exposure.visual_prototype_digest,
                    )
                )
            }
        )
        slots[slots.index(existing)] = AVPC1RelationSlot(
            existing.slot_id,
            "CONFLICTED",
            existing.auditory_key_digest,
            None,
            None,
            conflict,
        )
    else:
        free = next((slot for slot in slots if slot.status == "FREE"), None)
        if free is None:
            event = "CAPACITY_FULL_NEW_KEY_REJECTED"
        else:
            event = "PAIR_CREATED_PENDING"
            selected = free.slot_id
            changed = True
            slots[slots.index(free)] = AVPC1RelationSlot(
                free.slot_id,
                "PENDING",
                exposure.auditory_prototype_digest,
                exposure.visual_prototype_digest,
                1,
                None,
            )
    return event, selected, changed, tuple(slots)


def _validate_transition(
    result: object,
    transition_id: str,
    prestate: AVPC1BoundedRelationState,
    exposure: AVPC1UnambiguousOverlapExposureReceipt,
) -> AVPC1RelationTransitionResult:
    if type(result) is not AVPC1RelationTransitionResult:
        raise AVPC1AtomicRelationFormationConsumerError(
            AVPC1_ATOMIC_RELATION_FORMATION_TRANSITION_MISMATCH,
            "relation child returned the wrong type",
        )
    event, selected, changed, slots = _expected_transition(prestate, exposure)
    receipt = result.receipt
    poststate = result.state
    static_equal = (
        poststate.relation_table_id == prestate.relation_table_id
        and poststate.profile_binding_digest == prestate.profile_binding_digest
        and poststate.auditory_bank_config_digest
        == prestate.auditory_bank_config_digest
        and poststate.auditory_bank_state_identity_digest
        == prestate.auditory_bank_state_identity_digest
        and poststate.auditory_bank_state_digest
        == prestate.auditory_bank_state_digest
        and poststate.auditory_prototype_inventory
        == prestate.auditory_prototype_inventory
        and poststate.visual_bank_config_digest == prestate.visual_bank_config_digest
        and poststate.visual_bank_state_identity_digest
        == prestate.visual_bank_state_identity_digest
        and poststate.visual_bank_state_digest == prestate.visual_bank_state_digest
        and poststate.visual_prototype_inventory
        == prestate.visual_prototype_inventory
        and poststate.relation_partition is prestate.relation_partition
        and poststate.relation_history_partition_digest
        == prestate.relation_history_partition_digest
        and poststate.state_identity_digest == prestate.state_identity_digest
    )
    if changed:
        dynamic_equal = (
            poststate.accepted_exposure_count == prestate.accepted_exposure_count + 1
            and poststate.consumed_exposure_receipt_digests
            == prestate.consumed_exposure_receipt_digests
            + (exposure.exposure_receipt_digest,)
            and poststate.slots == slots
        )
    else:
        dynamic_equal = poststate is prestate
    if (
        not static_equal
        or not dynamic_equal
        or receipt.transition_id != transition_id
        or receipt.exposure_receipt_digest != exposure.exposure_receipt_digest
        or receipt.prestate_digest != prestate.state_digest
        or receipt.event != event
        or receipt.selected_slot_id != selected
        or receipt.poststate_digest != poststate.state_digest
        or receipt.state_changed is not changed
    ):
        raise AVPC1AtomicRelationFormationConsumerError(
            AVPC1_ATOMIC_RELATION_FORMATION_TRANSITION_MISMATCH,
            "relation transition does not match the frozen prestate and exposure",
        )
    if not changed or event not in _ACCEPTED_EVENTS:
        raise AVPC1AtomicRelationFormationConsumerError(
            AVPC1_ATOMIC_RELATION_FORMATION_TRANSITION_REJECTED,
            f"relation transition was rejected: {event}",
        )
    return result


class AVPC1AtomicRelationFormationConsumerOwner:
    """Private authority for one terminal later-exposure relation attempt."""

    def __init__(
        self,
        owner_id: str,
        consumption_id: str,
        auditory_probe_id: str,
        visual_probe_id: str,
        exposure_id: str,
        transition_id: str,
        authorized_formation_result_digest: str,
        authorized_formation_envelope_digest: str,
        authorized_later_exposure_envelope_digest: str,
        authorized_profile_binding_digest: str,
        authorized_relation_partition_digest: str,
        authorized_auditory_frame_provenance_digest: str,
        authorized_visual_frame_provenance_digest: str,
        authorized_relation_prestate_identity_digest: str,
        authorized_relation_prestate_digest: str,
    ) -> None:
        self._owner_id = _identifier(owner_id, "owner_id")
        self._consumption_id = _identifier(consumption_id, "consumption_id")
        self._auditory_probe_id = _identifier(auditory_probe_id, "auditory_probe_id")
        self._visual_probe_id = _identifier(visual_probe_id, "visual_probe_id")
        self._exposure_id = _identifier(exposure_id, "exposure_id")
        self._transition_id = _identifier(transition_id, "transition_id")
        digests = (
            authorized_formation_result_digest,
            authorized_formation_envelope_digest,
            authorized_later_exposure_envelope_digest,
            authorized_profile_binding_digest,
            authorized_relation_partition_digest,
            authorized_auditory_frame_provenance_digest,
            authorized_visual_frame_provenance_digest,
            authorized_relation_prestate_identity_digest,
            authorized_relation_prestate_digest,
        )
        if not all(_valid_digest(value) for value in digests):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_INVALID_INPUT,
                "all authorized source roles must be SHA-256 digests",
            )
        (
            self._formation_result_digest,
            self._formation_envelope_digest,
            self._later_envelope_digest,
            self._profile_digest,
            self._partition_digest,
            self._auditory_digest,
            self._visual_digest,
            self._relation_identity,
            self._relation_digest,
        ) = digests
        self._status = "AUTHORIZED"
        self._attempt_count = 0
        self._use_count = 0
        self._generation = 0
        self._committed_result_digest: str | None = None
        self._failure_code: str | None = None
        self._failure_digest: str | None = None
        self._lock = Lock()

    def snapshot(self) -> AVPC1AtomicRelationFormationOwnerSnapshot:
        with self._lock:
            return _make_snapshot(self)

    def _validate_sources(
        self,
        formation_result: object,
        formation_envelope: object,
        later_envelope: object,
        profile: object,
        partition: object,
        auditory: object,
        visual: object,
        relation_state: object,
    ) -> tuple[
        PPB1ActiveBatchFormationResult,
        PPB1ActiveReceptorBatchEnvelope,
        PPB1ActiveReceptorBatchEnvelope,
        PPB1ReceptorProfileBinding,
        AVPC1FrozenRelationHistoryPartitionBinding,
        PPB1ActiveReceptorTimedFrameBinding,
        PPB1ActiveReceptorTimedFrameBinding,
        AVPC1BoundedRelationState,
    ]:
        expected_types = (
            (formation_result, PPB1ActiveBatchFormationResult),
            (formation_envelope, PPB1ActiveReceptorBatchEnvelope),
            (later_envelope, PPB1ActiveReceptorBatchEnvelope),
            (profile, PPB1ReceptorProfileBinding),
            (partition, AVPC1FrozenRelationHistoryPartitionBinding),
            (auditory, PPB1ActiveReceptorTimedFrameBinding),
            (visual, PPB1ActiveReceptorTimedFrameBinding),
            (relation_state, AVPC1BoundedRelationState),
        )
        if not all(type(value) is expected for value, expected in expected_types):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_INVALID_INPUT,
                "exact relation-formation source types are required",
            )
        authorized = _source_snapshot(
            formation_result,
            formation_envelope,
            later_envelope,
            profile,
            partition,
            auditory,
            visual,
            relation_state,
        )[:9]
        expected_authorized = (
            self._formation_result_digest,
            self._formation_envelope_digest,
            self._later_envelope_digest,
            self._profile_digest,
            self._partition_digest,
            self._auditory_digest,
            self._visual_digest,
            self._relation_identity,
            self._relation_digest,
        )
        auditory_state = formation_result.auditory_poststate
        visual_state = formation_result.visual_poststate
        if (
            authorized != expected_authorized
            or formation_result.envelope_digest != formation_envelope.envelope_digest
            or formation_result.profile_binding_digest != profile.digest()
            or formation_envelope.profile_binding_digest != profile.digest()
            or later_envelope.profile_binding_digest != profile.digest()
            or later_envelope.parameter_digest != profile.parameter_digest
            or later_envelope.envelope_digest == formation_envelope.envelope_digest
            or later_envelope.common_field_clock_id
            != formation_envelope.common_field_clock_id
            or relation_state.profile_binding_digest != profile.digest()
            or relation_state.auditory_bank_config_digest
            != profile.auditory_config.digest()
            or relation_state.visual_bank_config_digest
            != profile.visual_config.digest()
            or relation_state.auditory_bank_state_digest != auditory_state.digest()
            or relation_state.visual_bank_state_digest != visual_state.digest()
            or relation_state.auditory_bank_state_identity_digest
            != _state_identity_digest(auditory_state)
            or relation_state.visual_bank_state_identity_digest
            != _state_identity_digest(visual_state)
            or relation_state.auditory_prototype_inventory
            != _stable_inventory(profile.auditory_config, auditory_state)
            or relation_state.visual_prototype_inventory
            != _stable_inventory(profile.visual_config, visual_state)
            or relation_state.relation_partition is not partition
        ):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_SOURCE_MISMATCH,
                "formation, profile, relation or owner source binding mismatch",
            )
        auditory_members = later_envelope.auditory_stream.timed_frames
        visual_members = later_envelope.visual_stream.timed_frames
        formation_provenance = {
            item.timed_frame_provenance_digest
            for stream in (
                formation_envelope.auditory_stream,
                formation_envelope.visual_stream,
            )
            for item in stream.timed_frames
        }
        later_provenance = {
            item.timed_frame_provenance_digest
            for stream in (
                later_envelope.auditory_stream,
                later_envelope.visual_stream,
            )
            for item in stream.timed_frames
        }
        if (
            not any(item is auditory for item in auditory_members)
            or not any(item is visual for item in visual_members)
            or auditory.timed_frame.frame.modality_id != "auditory"
            or visual.timed_frame.frame.modality_id != "visual"
            or formation_provenance.intersection(later_provenance)
        ):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_SOURCE_MISMATCH,
                "selected frames are not exact later-envelope members",
            )
        later_streams = (
            (later_envelope.auditory_stream, auditory_state),
            (later_envelope.visual_stream, visual_state),
        )
        if any(
            state.source_clock_id is None
            or state.last_source_window_end_tick is None
            or stream.source_clock_id != state.source_clock_id
            or any(
                item.source_window_start_tick < state.last_source_window_end_tick
                for item in stream.timed_frames
            )
            for stream, state in later_streams
        ):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_CAUSALITY_MISMATCH,
                "relation exposure is not strictly after formation",
            )
        modalities, snapshots, provenance, maximum_end = (
            _canonical_partition_inventory(later_envelope)
        )
        if (
            partition.field_clock_id != later_envelope.common_field_clock_id
            or partition.exposure_count != len(provenance)
            or partition.ordered_modality_ids != modalities
            or partition.ordered_snapshot_ids != snapshots
            or partition.ordered_timed_frame_provenance_digests != provenance
            or partition.max_relation_field_window_end_tick != maximum_end
            or provenance.count(auditory.timed_frame_provenance_digest) != 1
            or provenance.count(visual.timed_frame_provenance_digest) != 1
        ):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_SOURCE_MISMATCH,
                "relation partition does not equal the later exposure envelope",
            )
        return (
            formation_result,
            formation_envelope,
            later_envelope,
            profile,
            partition,
            auditory,
            visual,
            relation_state,
        )

    def consume_once(
        self,
        formation_result: object,
        formation_envelope: object,
        later_exposure_envelope: object,
        profile: object,
        relation_partition: object,
        auditory_frame: object,
        visual_frame: object,
        relation_prestate: object,
    ) -> AVPC1AtomicRelationFormationResult:
        if not self._lock.acquire(blocking=False):
            raise AVPC1AtomicRelationFormationConsumerError(
                AVPC1_ATOMIC_RELATION_FORMATION_OWNER_BUSY,
                "relation formation owner already has an active call",
            )
        try:
            if self._status != "AUTHORIZED":
                raise AVPC1AtomicRelationFormationConsumerError(
                    AVPC1_ATOMIC_RELATION_FORMATION_OWNER_TERMINAL,
                    f"relation formation owner is terminal: {self._status}",
                )
            self._status = "IN_PROGRESS"
            self._attempt_count = 1
            try:
                bound = self._validate_sources(
                    formation_result,
                    formation_envelope,
                    later_exposure_envelope,
                    profile,
                    relation_partition,
                    auditory_frame,
                    visual_frame,
                    relation_prestate,
                )
                (
                    result,
                    formation,
                    later,
                    bound_profile,
                    partition,
                    auditory,
                    visual,
                    prestate,
                ) = bound
                source_before = _source_snapshot(
                    result,
                    formation,
                    later,
                    bound_profile,
                    partition,
                    auditory,
                    visual,
                    prestate,
                )
                audit = audit_receptor_time_alignment(
                    _sequence_from_stream(later, "auditory"),
                    _sequence_from_stream(later, "visual"),
                )
                if type(audit) is not ReceptorTimeAlignmentAudit:
                    raise AVPC1AtomicRelationFormationConsumerError(
                        AVPC1_ATOMIC_RELATION_FORMATION_ALIGNMENT_MISMATCH,
                        "alignment child returned the wrong type",
                    )
                expected_audit = _expected_alignment_audit(later)
                if audit != expected_audit:
                    raise AVPC1AtomicRelationFormationConsumerError(
                        AVPC1_ATOMIC_RELATION_FORMATION_ALIGNMENT_MISMATCH,
                        "alignment child does not match the frozen later streams",
                    )
                pair = tuple(
                    overlap
                    for overlap in audit.unambiguous_overlaps
                    if overlap.first_snapshot_id == auditory.snapshot_id
                    and overlap.second_snapshot_id == visual.snapshot_id
                )
                if (
                    not audit.has_complete_one_to_one_alignment
                    or audit.ambiguous_snapshot_ids
                    or audit.unmatched_snapshot_ids
                    or len(pair) != 1
                ):
                    raise AVPC1AtomicRelationFormationConsumerError(
                        AVPC1_ATOMIC_RELATION_FORMATION_ALIGNMENT_MISMATCH,
                        "later exposure does not bind one complete selected overlap",
                    )
                auditory_finding = _validate_finding(
                    probe_s1wu_perceptual_state(
                        bound_profile.auditory_config,
                        result.auditory_poststate,
                        auditory.timed_frame.frame,
                        self._auditory_probe_id,
                    ),
                    self._auditory_probe_id,
                    bound_profile.auditory_config,
                    result.auditory_poststate,
                    auditory,
                )
                visual_finding = _validate_finding(
                    probe_s1wu_perceptual_state(
                        bound_profile.visual_config,
                        result.visual_poststate,
                        visual.timed_frame.frame,
                        self._visual_probe_id,
                    ),
                    self._visual_probe_id,
                    bound_profile.visual_config,
                    result.visual_poststate,
                    visual,
                )
                try:
                    exposure = bind_avpc1_unambiguous_overlap_exposure_receipt(
                        self._exposure_id,
                        audit,
                        auditory,
                        visual,
                        auditory_finding,
                        visual_finding,
                        prestate,
                    )
                except AVPC1BoundedRelationError as exc:
                    raise AVPC1AtomicRelationFormationConsumerError(
                        AVPC1_ATOMIC_RELATION_FORMATION_EXPOSURE_MISMATCH,
                        "exposure receipt child failed",
                    ) from exc
                overlap = pair[0]
                if (
                    type(exposure) is not AVPC1UnambiguousOverlapExposureReceipt
                    or exposure.exposure_id != self._exposure_id
                    or exposure.alignment_audit_digest
                    != _digest(_alignment_payload(audit))
                    or exposure.auditory_frame_provenance_digest
                    != auditory.timed_frame_provenance_digest
                    or exposure.visual_frame_provenance_digest
                    != visual.timed_frame_provenance_digest
                    or exposure.intersection_start_tick != overlap.window_start_tick
                    or exposure.intersection_end_tick != overlap.window_end_tick
                    or exposure.auditory_finding_digest
                    != auditory_finding.finding_digest
                    or exposure.visual_finding_digest != visual_finding.finding_digest
                    or exposure.auditory_prototype_digest
                    != auditory_finding.selected_prototype_digest
                    or exposure.visual_prototype_digest
                    != visual_finding.selected_prototype_digest
                    or exposure.auditory_bank_state_digest
                    != prestate.auditory_bank_state_digest
                    or exposure.visual_bank_state_digest
                    != prestate.visual_bank_state_digest
                ):
                    raise AVPC1AtomicRelationFormationConsumerError(
                        AVPC1_ATOMIC_RELATION_FORMATION_EXPOSURE_MISMATCH,
                        "exposure receipt does not match the selected source pair",
                    )
                try:
                    transition = _validate_transition(
                        advance_avpc1_bounded_relation_state(
                            self._transition_id,
                            prestate,
                            exposure,
                        ),
                        self._transition_id,
                        prestate,
                        exposure,
                    )
                except AVPC1BoundedRelationError as exc:
                    raise AVPC1AtomicRelationFormationConsumerError(
                        AVPC1_ATOMIC_RELATION_FORMATION_TRANSITION_MISMATCH,
                        "relation transition child failed",
                    ) from exc
                if source_before != _source_snapshot(
                    result,
                    formation,
                    later,
                    bound_profile,
                    partition,
                    auditory,
                    visual,
                    prestate,
                ):
                    raise AVPC1AtomicRelationFormationConsumerError(
                        AVPC1_ATOMIC_RELATION_FORMATION_SOURCE_MISMATCH,
                        "relation formation sources changed during the attempt",
                    )
                alignment_digest = _digest(_alignment_payload(audit))
                values = {
                    "consumption_id": self._consumption_id,
                    "formation_result_digest": result.formation_result_digest,
                    "formation_envelope_digest": formation.envelope_digest,
                    "later_exposure_envelope_digest": later.envelope_digest,
                    "profile_binding_digest": bound_profile.digest(),
                    "relation_partition_digest": (
                        partition.relation_history_partition_digest
                    ),
                    "auditory_frame_provenance_digest": (
                        auditory.timed_frame_provenance_digest
                    ),
                    "visual_frame_provenance_digest": (
                        visual.timed_frame_provenance_digest
                    ),
                    "alignment_audit_digest": alignment_digest,
                    "auditory_finding": auditory_finding,
                    "visual_finding": visual_finding,
                    "exposure_receipt": exposure,
                    "relation_prestate_identity_digest": prestate.state_identity_digest,
                    "relation_prestate_digest": prestate.state_digest,
                    "transition": transition,
                }
                projection = {
                    "schema_version": AVPC1_ATOMIC_RELATION_FORMATION_SCHEMA_VERSION,
                    **_snapshot_values(self),
                }
                projection.update(
                    status="CONSUMED",
                    use_count=1,
                    generation=1,
                )
                projection.pop("committed_result_digest")
                payload = {
                    "schema_version": AVPC1_ATOMIC_RELATION_FORMATION_SCHEMA_VERSION,
                    "contract_digest": AVPC1_ATOMIC_RELATION_FORMATION_CONTRACT_DIGEST,
                    "preflight_digest": AVPC1_ATOMIC_RELATION_FORMATION_PREFLIGHT_DIGEST,
                    **{
                        key: (
                            _finding_payload(value)
                            if key in {"auditory_finding", "visual_finding"}
                            else _exposure_payload(value)
                            if key == "exposure_receipt"
                            else _transition_payload(value)
                            if key == "transition"
                            else value
                        )
                        for key, value in values.items()
                    },
                    "authorization_poststate": projection,
                }
                result_digest = _digest(payload)
                self._status = "CONSUMED"
                self._use_count = 1
                self._generation = 1
                self._committed_result_digest = result_digest
                complete = AVPC1AtomicRelationFormationResult(
                    **values,
                    authorization_poststate=_make_snapshot(self),
                    result_digest=result_digest,
                )
                return complete
            except Exception as exc:
                if self._status == "CONSUMED":
                    self._status = "IN_PROGRESS"
                    self._use_count = 0
                    self._committed_result_digest = None
                failure_code = getattr(
                    exc,
                    "code",
                    AVPC1_ATOMIC_RELATION_FORMATION_ATTEMPT_FAILED,
                )
                self._status = "FAILED"
                self._generation = 1
                self._failure_code = str(failure_code)
                self._failure_digest = _digest(
                    {
                        "schema_version": (
                            AVPC1_ATOMIC_RELATION_FORMATION_SCHEMA_VERSION
                        ),
                        "owner_id": self._owner_id,
                        "consumption_id": self._consumption_id,
                        "failure_code": self._failure_code,
                        "exception_type": type(exc).__name__,
                    }
                )
                raise AVPC1AtomicRelationFormationConsumerError(
                    AVPC1_ATOMIC_RELATION_FORMATION_ATTEMPT_FAILED,
                    "relation formation attempt failed without publishing a result",
                ) from exc
        finally:
            self._lock.release()


def prepare_avpc1_atomic_relation_formation_consumer_owner(
    owner_id: str,
    consumption_id: str,
    auditory_probe_id: str,
    visual_probe_id: str,
    exposure_id: str,
    transition_id: str,
    authorized_formation_result_digest: str,
    authorized_formation_envelope_digest: str,
    authorized_later_exposure_envelope_digest: str,
    authorized_profile_binding_digest: str,
    authorized_relation_partition_digest: str,
    authorized_auditory_frame_provenance_digest: str,
    authorized_visual_frame_provenance_digest: str,
    authorized_relation_prestate_identity_digest: str,
    authorized_relation_prestate_digest: str,
) -> AVPC1AtomicRelationFormationConsumerOwner:
    """Prepare one private, process-local relation-formation authority."""

    return AVPC1AtomicRelationFormationConsumerOwner(
        owner_id,
        consumption_id,
        auditory_probe_id,
        visual_probe_id,
        exposure_id,
        transition_id,
        authorized_formation_result_digest,
        authorized_formation_envelope_digest,
        authorized_later_exposure_envelope_digest,
        authorized_profile_binding_digest,
        authorized_relation_partition_digest,
        authorized_auditory_frame_provenance_digest,
        authorized_visual_frame_provenance_digest,
        authorized_relation_prestate_identity_digest,
        authorized_relation_prestate_digest,
    )
