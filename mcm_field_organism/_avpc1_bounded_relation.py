"""Private bounded exact-identity relation kernel for AVPC-1 engineering."""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
import re

from ._avpc1_audio_only_probe_envelope import (
    AVPC1FrozenRelationHistoryPartitionBinding,
    AVPC1PrivateAuditoryOnlyProbeEnvelope,
)
from ._ppb1_active_receptor_batch_binding import PPB1ActiveReceptorTimedFrameBinding
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import PPB1BankConfig, PPB1BankState, _validate_state
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
    _prototype_digest,
)
from .receptor_contract import technical_identifier
from .receptor_time_alignment import ReceptorTimeAlignmentAudit


AVPC1_RELATION_SCHEMA_VERSION = "avpc1.private.bounded-relation.v1"
AVPC1_RELATION_CONTRACT_DIGEST = (
    "64de777e9048b888cb0a701cbd54ed63e23a494a6736c02aa6870ab2db84080d"
)
AVPC1_RELATION_PREFLIGHT_DIGEST = (
    "9a11025bb0b06e30cd5f724330bd12c2914f95360c63e8c26fced3d581c2b1f5"
)
AVPC1_RELATION_INVALID_INPUT = "AVPC1_RELATION_INVALID_INPUT"
AVPC1_RELATION_CONTENT_MISMATCH = "AVPC1_RELATION_CONTENT_MISMATCH"
AVPC1_RELATION_PROVENANCE_MISMATCH = "AVPC1_RELATION_PROVENANCE_MISMATCH"
AVPC1_RELATION_ATOMIC_RESULT_REQUIRED = "AVPC1_RELATION_ATOMIC_RESULT_REQUIRED"

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_SLOT_IDS = ("avpc1.relation.slot.000", "avpc1.relation.slot.001")
_ACCEPTED = {"PAIR_CREATED_PENDING", "PAIR_CONFIRMED_STABLE", "KEY_MARKED_CONFLICTED"}


class AVPC1BoundedRelationError(ValueError):
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
        raise AVPC1BoundedRelationError(AVPC1_RELATION_INVALID_INPUT, str(exc)) from exc


def _identity_digest(table_id: str) -> str:
    return _digest({"schema_version": AVPC1_RELATION_SCHEMA_VERSION,
        "relation_table_id": table_id, "slot_ids": list(_SLOT_IDS),
        "relation_slot_capacity": 2, "support_required": 2,
        "exposure_budget": 4})


def _stable_inventory(
    profile_config: PPB1BankConfig,
    state: PPB1BankState,
) -> tuple[str, ...]:
    if (
        type(profile_config) is not PPB1BankConfig
        or type(state) is not PPB1BankState
    ):
        raise AVPC1BoundedRelationError(
            AVPC1_RELATION_INVALID_INPUT,
            "exact bank config and state are required",
        )
    try:
        valid = _validate_state(profile_config, state)
    except Exception as exc:
        raise AVPC1BoundedRelationError(
            AVPC1_RELATION_CONTENT_MISMATCH, "frozen bank state is invalid"
        ) from exc
    values = tuple(_prototype_digest(slot.prototype_values) for slot in valid.slots
        if slot.occupied and slot.support_count is not None
        and slot.support_count >= profile_config.stable_after)
    if not values or len(set(values)) != len(values):
        raise AVPC1BoundedRelationError(
            AVPC1_RELATION_CONTENT_MISMATCH,
            "stabilized prototype digests must be nonempty and unique",
        )
    return values


@dataclass(frozen=True, slots=True)
class AVPC1RelationSlot:
    slot_id: str
    status: str = "FREE"
    auditory_key_digest: str | None = None
    visual_target_digest: str | None = None
    support_count: int | None = None
    conflict_identity_digest: str | None = None

    def __post_init__(self) -> None:
        if self.slot_id not in _SLOT_IDS or self.status not in {
            "FREE", "PENDING", "STABLE", "CONFLICTED"
        }:
            raise AVPC1BoundedRelationError(AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,
                "relation slot identity or status is invalid")
        key, target, support, conflict = (self.auditory_key_digest,
            self.visual_target_digest, self.support_count, self.conflict_identity_digest)
        valid = ((self.status == "FREE" and key is target is support is conflict is None)
            or (self.status == "PENDING" and _valid_digest(key) and _valid_digest(target)
                and support == 1 and conflict is None)
            or (self.status == "STABLE" and _valid_digest(key) and _valid_digest(target)
                and support == 2 and conflict is None)
            or (self.status == "CONFLICTED" and _valid_digest(key) and target is None
                and support is None and _valid_digest(conflict)))
        if not valid:
            raise AVPC1BoundedRelationError(AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,
                "relation slot payload does not match status")

    def payload(self) -> dict[str, object]:
        return {"slot_id": self.slot_id, "status": self.status,
            "auditory_key_digest": self.auditory_key_digest,
            "visual_target_digest": self.visual_target_digest,
            "support_count": self.support_count,
            "conflict_identity_digest": self.conflict_identity_digest}


@dataclass(frozen=True, slots=True)
class AVPC1BoundedRelationState:
    relation_table_id: str
    profile_binding_digest: str
    auditory_bank_config_digest: str
    auditory_bank_state_identity_digest: str
    auditory_bank_state_digest: str
    auditory_prototype_inventory: tuple[str, ...]
    visual_bank_config_digest: str
    visual_bank_state_identity_digest: str
    visual_bank_state_digest: str
    visual_prototype_inventory: tuple[str, ...]
    relation_partition: AVPC1FrozenRelationHistoryPartitionBinding
    relation_history_partition_digest: str
    state_identity_digest: str
    accepted_exposure_count: int
    consumed_exposure_receipt_digests: tuple[str, ...]
    slots: tuple[AVPC1RelationSlot, AVPC1RelationSlot]
    state_digest: str

    def __post_init__(self) -> None:
        _identifier(self.relation_table_id, "relation_table_id")
        auditory_inventory = tuple(self.auditory_prototype_inventory)
        visual_inventory = tuple(self.visual_prototype_inventory)
        consumed = tuple(self.consumed_exposure_receipt_digests)
        slots = tuple(self.slots)
        if (not all(_valid_digest(v) for v in (self.profile_binding_digest,
            self.auditory_bank_config_digest, self.auditory_bank_state_identity_digest,
            self.auditory_bank_state_digest, self.visual_bank_config_digest,
            self.visual_bank_state_identity_digest, self.visual_bank_state_digest,
            self.relation_history_partition_digest, self.state_identity_digest,
            self.state_digest, *auditory_inventory, *visual_inventory))
            or type(self.relation_partition)
            is not AVPC1FrozenRelationHistoryPartitionBinding
            or self.relation_history_partition_digest
            != self.relation_partition.relation_history_partition_digest
            or not auditory_inventory or not visual_inventory
            or len(set(auditory_inventory)) != len(auditory_inventory)
            or len(set(visual_inventory)) != len(visual_inventory)
            or self.state_identity_digest != _identity_digest(self.relation_table_id)
            or isinstance(self.accepted_exposure_count, bool)
            or not isinstance(self.accepted_exposure_count, int)
            or self.accepted_exposure_count != len(consumed)
            or not 0 <= self.accepted_exposure_count <= 4 or len(set(consumed)) != len(consumed)
            or any(not _valid_digest(v) for v in consumed) or len(slots) != 2
            or any(type(slot) is not AVPC1RelationSlot for slot in slots)
            or tuple(s.slot_id for s in slots) != _SLOT_IDS
            or self.state_digest != _digest(self.payload_without_digest())):
            raise AVPC1BoundedRelationError(AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,
                "relation state is incomplete or digest-inconsistent")
        object.__setattr__(self, "auditory_prototype_inventory", auditory_inventory)
        object.__setattr__(self, "visual_prototype_inventory", visual_inventory)
        object.__setattr__(self, "consumed_exposure_receipt_digests", consumed)
        object.__setattr__(self, "slots", slots)

    def payload_without_digest(self) -> dict[str, object]:
        return {"schema_version": AVPC1_RELATION_SCHEMA_VERSION,
            "contract_digest": AVPC1_RELATION_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_RELATION_PREFLIGHT_DIGEST,
            "relation_table_id": self.relation_table_id,
            "profile_binding_digest": self.profile_binding_digest,
            "auditory_bank_config_digest": self.auditory_bank_config_digest,
            "auditory_bank_state_identity_digest": self.auditory_bank_state_identity_digest,
            "auditory_bank_state_digest": self.auditory_bank_state_digest,
            "auditory_prototype_inventory": list(self.auditory_prototype_inventory),
            "visual_bank_config_digest": self.visual_bank_config_digest,
            "visual_bank_state_identity_digest": self.visual_bank_state_identity_digest,
            "visual_bank_state_digest": self.visual_bank_state_digest,
            "visual_prototype_inventory": list(self.visual_prototype_inventory),
            "relation_history_partition_digest": self.relation_history_partition_digest,
            "state_identity_digest": self.state_identity_digest,
            "accepted_exposure_count": self.accepted_exposure_count,
            "consumed_exposure_receipt_digests": list(self.consumed_exposure_receipt_digests),
            "slots": [slot.payload() for slot in self.slots]}


@dataclass(frozen=True, slots=True)
class AVPC1UnambiguousOverlapExposureReceipt:
    exposure_id: str
    alignment_audit_digest: str
    auditory_frame_provenance_digest: str
    visual_frame_provenance_digest: str
    intersection_start_tick: int
    intersection_end_tick: int
    auditory_finding_digest: str
    visual_finding_digest: str
    auditory_prototype_digest: str
    visual_prototype_digest: str
    auditory_bank_state_digest: str
    visual_bank_state_digest: str
    exposure_receipt_digest: str

    def __post_init__(self) -> None:
        _identifier(self.exposure_id, "exposure_id")
        values = tuple(getattr(self, name) for name in self.__dataclass_fields__
            if name.endswith("digest"))
        if (not all(_valid_digest(v) for v in values)
            or isinstance(self.intersection_start_tick, bool)
            or isinstance(self.intersection_end_tick, bool)
            or not isinstance(self.intersection_start_tick, int)
            or not isinstance(self.intersection_end_tick, int)
            or self.intersection_start_tick < 0
            or self.intersection_end_tick <= self.intersection_start_tick
            or self.exposure_receipt_digest != _digest(self.payload_without_digest())):
            raise AVPC1BoundedRelationError(AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,
                "exposure receipt is incomplete")

    def payload_without_digest(self) -> dict[str, object]:
        return {"schema_version": AVPC1_RELATION_SCHEMA_VERSION,
            **{name: getattr(self, name) for name in self.__dataclass_fields__
                if name != "exposure_receipt_digest"}}


@dataclass(frozen=True, slots=True)
class AVPC1RelationTransitionReceipt:
    transition_id: str
    exposure_receipt_digest: str
    prestate_digest: str
    event: str
    selected_slot_id: str | None
    poststate_digest: str
    state_changed: bool
    transition_receipt_digest: str

    def __post_init__(self) -> None:
        _identifier(self.transition_id, "transition_id")
        events = _ACCEPTED | {
            "DUPLICATE_EXPOSURE_REJECTED",
            "EXPOSURE_BUDGET_EXHAUSTED_REJECTED",
            "CONFLICT_LOCKED_REJECTED",
            "SUPPORT_SATURATED_REJECTED",
            "CAPACITY_FULL_NEW_KEY_REJECTED",
        }
        if (
            not all(
                _valid_digest(value)
                for value in (
                    self.exposure_receipt_digest,
                    self.prestate_digest,
                    self.poststate_digest,
                    self.transition_receipt_digest,
                )
            )
            or self.event not in events
            or (
                self.selected_slot_id is not None
                and self.selected_slot_id not in _SLOT_IDS
            )
            or not isinstance(self.state_changed, bool)
            or self.state_changed != (self.event in _ACCEPTED)
            or (not self.state_changed and self.prestate_digest != self.poststate_digest)
            or self.transition_receipt_digest
            != _digest(self.payload_without_digest())
        ):
            raise AVPC1BoundedRelationError(
                AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,
                "transition receipt is incomplete or non-atomic",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": AVPC1_RELATION_SCHEMA_VERSION,
            "transition_id": self.transition_id,
            "exposure_receipt_digest": self.exposure_receipt_digest,
            "prestate_digest": self.prestate_digest,
            "event": self.event,
            "selected_slot_id": self.selected_slot_id,
            "poststate_digest": self.poststate_digest,
            "state_changed": self.state_changed,
        }


@dataclass(frozen=True, slots=True)
class AVPC1RelationTransitionResult:
    state: AVPC1BoundedRelationState
    receipt: AVPC1RelationTransitionReceipt

    def __post_init__(self) -> None:
        if (
            type(self.state) is not AVPC1BoundedRelationState
            or type(self.receipt) is not AVPC1RelationTransitionReceipt
            or self.receipt.poststate_digest != self.state.state_digest
        ):
            raise AVPC1BoundedRelationError(
                AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,
                "transition result does not bind one complete poststate",
            )


@dataclass(frozen=True, slots=True)
class AVPC1ReadOnlyRelationFinding:
    probe_id: str
    audio_only_envelope_digest: str
    auditory_finding_digest: str
    relation_state_identity_digest: str
    observed_relation_state_digest: str
    result_role: str
    selected_relation_slot_id: str | None
    visual_prototype_identity_digest: str | None
    frozen_visual_bank_state_digest: str
    finding_digest: str

    def __post_init__(self) -> None:
        _identifier(self.probe_id, "probe_id")
        digests = (
            self.audio_only_envelope_digest,
            self.auditory_finding_digest,
            self.relation_state_identity_digest,
            self.observed_relation_state_digest,
            self.frozen_visual_bank_state_digest,
            self.finding_digest,
        )
        role_is_valid = (
            self.result_role == "MATCH"
            and self.selected_relation_slot_id in _SLOT_IDS
            and _valid_digest(self.visual_prototype_identity_digest)
        ) or (
            self.result_role == "NO_MATCH"
            and (
                self.selected_relation_slot_id is None
                or self.selected_relation_slot_id in _SLOT_IDS
            )
            and self.visual_prototype_identity_digest is None
        ) or (
            self.result_role == "NO_MATCH_CONFLICT"
            and self.selected_relation_slot_id in _SLOT_IDS
            and self.visual_prototype_identity_digest is None
        )
        if (
            not all(_valid_digest(value) for value in digests)
            or not role_is_valid
            or self.finding_digest != _digest(self.payload_without_digest())
        ):
            raise AVPC1BoundedRelationError(
                AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,
                "read-only relation finding is incomplete",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": AVPC1_RELATION_SCHEMA_VERSION,
            "probe_id": self.probe_id,
            "audio_only_envelope_digest": self.audio_only_envelope_digest,
            "auditory_finding_digest": self.auditory_finding_digest,
            "relation_state_identity_digest": self.relation_state_identity_digest,
            "observed_relation_state_digest": self.observed_relation_state_digest,
            "result_role": self.result_role,
            "selected_relation_slot_id": self.selected_relation_slot_id,
            "visual_prototype_identity_digest": self.visual_prototype_identity_digest,
            "frozen_visual_bank_state_digest": self.frozen_visual_bank_state_digest,
        }


def initial_avpc1_bounded_relation_state(table_id: str,
    profile: PPB1ReceptorProfileBinding, auditory_state: PPB1BankState,
    visual_state: PPB1BankState,
    partition: AVPC1FrozenRelationHistoryPartitionBinding) -> AVPC1BoundedRelationState:
    if (type(profile) is not PPB1ReceptorProfileBinding
        or type(auditory_state) is not PPB1BankState
        or type(visual_state) is not PPB1BankState
        or type(partition) is not AVPC1FrozenRelationHistoryPartitionBinding):
        raise AVPC1BoundedRelationError(
            AVPC1_RELATION_INVALID_INPUT,
            "exact profile, states and relation partition are required",
        )
    table_id = _identifier(table_id, "relation_table_id")
    auditory_inventory = _stable_inventory(
        profile.auditory_config, auditory_state
    )
    visual_inventory = _stable_inventory(profile.visual_config, visual_state)
    values = dict(relation_table_id=table_id, profile_binding_digest=profile.digest(),
        auditory_bank_config_digest=profile.auditory_config.digest(),
        auditory_bank_state_identity_digest=_digest(_state_identity_payload(auditory_state)),
        auditory_bank_state_digest=auditory_state.digest(),
        auditory_prototype_inventory=auditory_inventory,
        visual_bank_config_digest=profile.visual_config.digest(),
        visual_bank_state_identity_digest=_digest(_state_identity_payload(visual_state)),
        visual_bank_state_digest=visual_state.digest(),
        visual_prototype_inventory=visual_inventory,
        relation_partition=partition,
        relation_history_partition_digest=partition.relation_history_partition_digest,
        state_identity_digest=_identity_digest(table_id), accepted_exposure_count=0,
        consumed_exposure_receipt_digests=(),
        slots=tuple(AVPC1RelationSlot(s) for s in _SLOT_IDS))
    digest_values = {k: v for k, v in values.items() if k != "relation_partition"}
    payload={"schema_version":AVPC1_RELATION_SCHEMA_VERSION,
        "contract_digest":AVPC1_RELATION_CONTRACT_DIGEST,
        "preflight_digest":AVPC1_RELATION_PREFLIGHT_DIGEST,
        **{k:([s.payload() for s in v] if k=="slots" else list(v)
            if k in {"consumed_exposure_receipt_digests",
                "auditory_prototype_inventory", "visual_prototype_inventory"}
            else v) for k,v in digest_values.items()}}
    return AVPC1BoundedRelationState(**values, state_digest=_digest(payload))


def _alignment_payload(audit: ReceptorTimeAlignmentAudit) -> dict[str, object]:
    overlap=lambda o:{"first_snapshot_id":o.first_snapshot_id,
        "second_snapshot_id":o.second_snapshot_id,"window_start_tick":o.window_start_tick,
        "window_end_tick":o.window_end_tick}
    return {"clock_id":audit.clock_id,"modality_ids":list(audit.modality_ids),
        "frame_counts":list(audit.frame_counts),"overlaps":[overlap(o) for o in audit.overlaps],
        "unambiguous_overlaps":[overlap(o) for o in audit.unambiguous_overlaps],
        "ambiguous_snapshot_ids":list(audit.ambiguous_snapshot_ids),
        "unmatched_snapshot_ids":list(audit.unmatched_snapshot_ids)}


def bind_avpc1_unambiguous_overlap_exposure_receipt(exposure_id: str,
    audit: ReceptorTimeAlignmentAudit, auditory: PPB1ActiveReceptorTimedFrameBinding,
    visual: PPB1ActiveReceptorTimedFrameBinding,
    auditory_finding: S1WUReadOnlyPerceptualFinding,
    visual_finding: S1WUReadOnlyPerceptualFinding,
    state: AVPC1BoundedRelationState) -> AVPC1UnambiguousOverlapExposureReceipt:
    if not all(type(v) is t for v,t in ((audit,ReceptorTimeAlignmentAudit),
        (auditory,PPB1ActiveReceptorTimedFrameBinding),(visual,PPB1ActiveReceptorTimedFrameBinding),
        (auditory_finding,S1WUReadOnlyPerceptualFinding),(visual_finding,S1WUReadOnlyPerceptualFinding),
        (state,AVPC1BoundedRelationState))):
        raise AVPC1BoundedRelationError(AVPC1_RELATION_INVALID_INPUT,"exact receipt inputs required")
    pair=[o for o in audit.unambiguous_overlaps if
        {o.first_snapshot_id,o.second_snapshot_id}=={auditory.snapshot_id,visual.snapshot_id}]
    partition_provenance = set(
        state.relation_partition.ordered_timed_frame_provenance_digests
    )
    if (len(pair)!=1 or audit.ambiguous_snapshot_ids or audit.unmatched_snapshot_ids
        or not audit.has_complete_one_to_one_alignment or auditory.field_clock_id!=audit.clock_id
        or visual.field_clock_id!=audit.clock_id
        or auditory.timed_frame_provenance_digest not in partition_provenance
        or visual.timed_frame_provenance_digest not in partition_provenance
        or not auditory_finding.recognized
        or not visual_finding.recognized or auditory_finding.modality_id!="auditory"
        or visual_finding.modality_id!="visual"
        or auditory_finding.probe_input_digest!=auditory.ppb1_input_projection_digest
        or visual_finding.probe_input_digest!=visual.ppb1_input_projection_digest
        or auditory_finding.bank_config_digest!=state.auditory_bank_config_digest
        or visual_finding.bank_config_digest!=state.visual_bank_config_digest
        or auditory_finding.observed_bank_state_digest!=state.auditory_bank_state_digest
        or visual_finding.observed_bank_state_digest!=state.visual_bank_state_digest
        or auditory_finding.state_identity_digest
        != state.auditory_bank_state_identity_digest
        or visual_finding.state_identity_digest
        != state.visual_bank_state_identity_digest
        or auditory_finding.selected_prototype_digest
        not in state.auditory_prototype_inventory
        or visual_finding.selected_prototype_digest
        not in state.visual_prototype_inventory):
        raise AVPC1BoundedRelationError(AVPC1_RELATION_PROVENANCE_MISMATCH,
            "overlap or read-only findings do not bind one frozen pair")
    overlap=pair[0]
    values=dict(exposure_id=_identifier(exposure_id,"exposure_id"),
        alignment_audit_digest=_digest(_alignment_payload(audit)),
        auditory_frame_provenance_digest=auditory.timed_frame_provenance_digest,
        visual_frame_provenance_digest=visual.timed_frame_provenance_digest,
        intersection_start_tick=overlap.window_start_tick,
        intersection_end_tick=overlap.window_end_tick,
        auditory_finding_digest=auditory_finding.finding_digest,
        visual_finding_digest=visual_finding.finding_digest,
        auditory_prototype_digest=auditory_finding.selected_prototype_digest,
        visual_prototype_digest=visual_finding.selected_prototype_digest,
        auditory_bank_state_digest=state.auditory_bank_state_digest,
        visual_bank_state_digest=state.visual_bank_state_digest)
    payload={"schema_version":AVPC1_RELATION_SCHEMA_VERSION,**values}
    return AVPC1UnambiguousOverlapExposureReceipt(**values,
        exposure_receipt_digest=_digest(payload))


def _new_state(state, slots, consumed):
    values=state.payload_without_digest(); values.pop("schema_version");
    values.pop("contract_digest"); values.pop("preflight_digest")
    values["relation_partition"] = state.relation_partition
    values["auditory_prototype_inventory"] = tuple(
        values["auditory_prototype_inventory"]
    )
    values["visual_prototype_inventory"] = tuple(
        values["visual_prototype_inventory"]
    )
    values.update(accepted_exposure_count=len(consumed),
        consumed_exposure_receipt_digests=tuple(consumed),slots=tuple(slots))
    digest_values = {k: v for k, v in values.items() if k != "relation_partition"}
    payload={"schema_version":AVPC1_RELATION_SCHEMA_VERSION,
        "contract_digest":AVPC1_RELATION_CONTRACT_DIGEST,
        "preflight_digest":AVPC1_RELATION_PREFLIGHT_DIGEST,
        **{k:([s.payload() for s in v] if k=="slots" else list(v)
            if k in {"consumed_exposure_receipt_digests",
                "auditory_prototype_inventory", "visual_prototype_inventory"}
            else v) for k,v in digest_values.items()}}
    return AVPC1BoundedRelationState(**values,state_digest=_digest(payload))


def advance_avpc1_bounded_relation_state(transition_id: str,
    state: AVPC1BoundedRelationState,
    exposure: AVPC1UnambiguousOverlapExposureReceipt) -> AVPC1RelationTransitionResult:
    if type(state) is not AVPC1BoundedRelationState or type(exposure) is not AVPC1UnambiguousOverlapExposureReceipt:
        raise AVPC1BoundedRelationError(AVPC1_RELATION_INVALID_INPUT,"exact state and exposure required")
    transition_id=_identifier(transition_id,"transition_id")
    if (exposure.auditory_bank_state_digest != state.auditory_bank_state_digest
        or exposure.visual_bank_state_digest != state.visual_bank_state_digest
        or exposure.auditory_prototype_digest
        not in state.auditory_prototype_inventory
        or exposure.visual_prototype_digest
        not in state.visual_prototype_inventory):
        raise AVPC1BoundedRelationError(
            AVPC1_RELATION_PROVENANCE_MISMATCH,
            "exposure receipt does not bind the frozen relation state",
        )
    slots=list(state.slots); selected=None; event=""; changed=False
    existing=next((s for s in slots if s.auditory_key_digest==exposure.auditory_prototype_digest),None)
    if exposure.exposure_receipt_digest in state.consumed_exposure_receipt_digests: event="DUPLICATE_EXPOSURE_REJECTED"
    elif state.accepted_exposure_count>=4: event="EXPOSURE_BUDGET_EXHAUSTED_REJECTED"
    elif existing and existing.status=="CONFLICTED": event="CONFLICT_LOCKED_REJECTED"; selected=existing.slot_id
    elif existing and existing.visual_target_digest==exposure.visual_prototype_digest and existing.status=="PENDING":
        event="PAIR_CONFIRMED_STABLE"; selected=existing.slot_id; changed=True
        slots[slots.index(existing)]=replace(existing,status="STABLE",support_count=2)
    elif existing and existing.visual_target_digest==exposure.visual_prototype_digest and existing.status=="STABLE": event="SUPPORT_SATURATED_REJECTED"; selected=existing.slot_id
    elif existing:
        event="KEY_MARKED_CONFLICTED"; selected=existing.slot_id; changed=True
        conflict=_digest({"visual_target_digests":sorted((existing.visual_target_digest,exposure.visual_prototype_digest))})
        slots[slots.index(existing)]=AVPC1RelationSlot(existing.slot_id,"CONFLICTED",
            existing.auditory_key_digest,None,None,conflict)
    else:
        free=next((s for s in slots if s.status=="FREE"),None)
        if free is None: event="CAPACITY_FULL_NEW_KEY_REJECTED"
        else:
            event="PAIR_CREATED_PENDING"; selected=free.slot_id; changed=True
            slots[slots.index(free)]=AVPC1RelationSlot(free.slot_id,"PENDING",
                exposure.auditory_prototype_digest,exposure.visual_prototype_digest,1,None)
    post=_new_state(state,slots,state.consumed_exposure_receipt_digests+(exposure.exposure_receipt_digest,)) if changed else state
    receipt_values={"transition_id":transition_id,"exposure_receipt_digest":exposure.exposure_receipt_digest,
        "prestate_digest":state.state_digest,"event":event,"selected_slot_id":selected,
        "poststate_digest":post.state_digest,"state_changed":changed}
    receipt=AVPC1RelationTransitionReceipt(**receipt_values,
        transition_receipt_digest=_digest({"schema_version":AVPC1_RELATION_SCHEMA_VERSION,**receipt_values}))
    if (changed!=(event in _ACCEPTED) or (not changed and post.state_digest!=state.state_digest)):
        raise AVPC1BoundedRelationError(AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,"transition atomicity failed")
    return AVPC1RelationTransitionResult(post,receipt)


def probe_avpc1_bounded_relation_read_only(probe_id: str,
    envelope: AVPC1PrivateAuditoryOnlyProbeEnvelope,
    auditory_finding: S1WUReadOnlyPerceptualFinding,
    state: AVPC1BoundedRelationState, visual_state: PPB1BankState,
    profile: PPB1ReceptorProfileBinding) -> AVPC1ReadOnlyRelationFinding:
    if (type(envelope) is not AVPC1PrivateAuditoryOnlyProbeEnvelope
        or type(auditory_finding) is not S1WUReadOnlyPerceptualFinding
        or type(state) is not AVPC1BoundedRelationState
        or type(visual_state) is not PPB1BankState
        or type(profile) is not PPB1ReceptorProfileBinding):
        raise AVPC1BoundedRelationError(
            AVPC1_RELATION_INVALID_INPUT, "exact read-only inputs required"
        )
    probe_id=_identifier(probe_id,"probe_id")
    before=(state.state_digest,
        state.relation_partition.relation_history_partition_digest,
        visual_state.digest())
    if (
        profile.digest()!=state.profile_binding_digest
        or not auditory_finding.recognized or auditory_finding.modality_id!="auditory"
        or auditory_finding.probe_input_digest!=envelope.auditory_input_projection_digest
        or auditory_finding.bank_config_digest!=state.auditory_bank_config_digest
        or auditory_finding.observed_bank_state_digest!=state.auditory_bank_state_digest
        or auditory_finding.state_identity_digest
        !=state.auditory_bank_state_identity_digest
        or auditory_finding.selected_prototype_digest
        not in state.auditory_prototype_inventory
        or envelope.profile_binding_digest!=state.profile_binding_digest
        or envelope.auditory_bank_config_digest
        !=state.auditory_bank_config_digest
        or envelope.auditory_bank_state_identity_digest
        !=state.auditory_bank_state_identity_digest
        or envelope.auditory_bank_state_digest!=state.auditory_bank_state_digest
        or envelope.relation_history_partition_digest
        !=state.relation_history_partition_digest
        or _digest(_state_identity_payload(visual_state))
        !=state.visual_bank_state_identity_digest
        or visual_state.digest()!=state.visual_bank_state_digest
        or profile.visual_config.digest()!=state.visual_bank_config_digest):
        raise AVPC1BoundedRelationError(AVPC1_RELATION_PROVENANCE_MISMATCH,"probe provenance mismatch")
    visual_inventory=_stable_inventory(profile.visual_config,visual_state)
    if visual_inventory != state.visual_prototype_inventory:
        raise AVPC1BoundedRelationError(
            AVPC1_RELATION_CONTENT_MISMATCH,
            "frozen visual prototype inventory changed",
        )
    slot=next((s for s in state.slots if s.auditory_key_digest==auditory_finding.selected_prototype_digest),None)
    if slot is None or slot.status=="PENDING": role,target="NO_MATCH",None
    elif slot.status=="CONFLICTED": role,target="NO_MATCH_CONFLICT",None
    elif slot.status=="STABLE" and slot.visual_target_digest in visual_inventory: role,target="MATCH",slot.visual_target_digest
    else: raise AVPC1BoundedRelationError(AVPC1_RELATION_CONTENT_MISMATCH,"stable visual target is absent")
    values={"probe_id":probe_id,"audio_only_envelope_digest":envelope.envelope_digest,
        "auditory_finding_digest":auditory_finding.finding_digest,
        "relation_state_identity_digest":state.state_identity_digest,
        "observed_relation_state_digest":state.state_digest,"result_role":role,
        "selected_relation_slot_id":slot.slot_id if slot else None,
        "visual_prototype_identity_digest":target,
        "frozen_visual_bank_state_digest":visual_state.digest()}
    finding=AVPC1ReadOnlyRelationFinding(**values,
        finding_digest=_digest({"schema_version":AVPC1_RELATION_SCHEMA_VERSION,**values}))
    if before!=(state.state_digest,
        state.relation_partition.relation_history_partition_digest,
        visual_state.digest()):
        raise AVPC1BoundedRelationError(AVPC1_RELATION_ATOMIC_RESULT_REQUIRED,"read-only state changed")
    return finding
