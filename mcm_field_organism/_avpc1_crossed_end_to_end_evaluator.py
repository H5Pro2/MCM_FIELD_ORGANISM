"""Private pure in-memory evaluation of the crossed AVPC-1 path."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from threading import Lock

from ._avpc1_atomic_readout_consumer import (
    AVPC1AtomicAuditoryCuedVisualReadoutOutcome,
    consume_avpc1_auditory_cued_visual_readout,
)
from ._avpc1_atomic_relation_formation_consumer import (
    AVPC1AtomicRelationFormationResult,
    prepare_avpc1_atomic_relation_formation_consumer_owner,
)
from ._avpc1_audio_only_probe_envelope import (
    AVPC1FrozenRelationHistoryPartitionBinding,
    AVPC1PrivateAuditoryOnlyProbeEnvelope,
    AVPC1PrivateAuditoryProbeSourceBinding,
    _sequence_digest,
    bind_avpc1_private_auditory_only_probe_envelope,
)
from ._avpc1_bounded_relation import (
    AVPC1BoundedRelationState,
    _identity_digest as _relation_identity_digest,
    _stable_inventory,
    initial_avpc1_bounded_relation_state,
)
from ._ppb1_active_batch_formation_consumer import (
    PPB1ActiveBatchFormationResult,
    prepare_ppb1_active_batch_formation_consumer_owner,
)
from ._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorTimedFrameBinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import PPB1BankState, _input_projection
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
    probe_s1wu_perceptual_state,
)
from ._ppb1_s1wq_perceptual_state_lifecycle import _state_identity_payload
from .receptor_contract import technical_identifier
from .receptor_time_model import ReceptorTimeSequence


AVPC1_CROSSED_EVALUATION_SCHEMA_VERSION = (
    "avpc1.private.crossed-end-to-end-evaluation.v1"
)
AVPC1_CROSSED_EVALUATION_CONTRACT_DIGEST = (
    "97c8810b1f3268c05467c8e9b364044cbb66909617c9244bf841c84442328c36"
)
AVPC1_CROSSED_EVALUATION_PREFLIGHT_DIGEST = (
    "09b1f68663a4986d47c98bf3cc3c12330202305bba347fa1afc739465a6f8bba"
)

AVPC1_CROSSED_EVALUATION_INVALID_INPUT = "AVPC1_CROSSED_EVALUATION_INVALID_INPUT"
AVPC1_CROSSED_EVALUATION_SOURCE_MISMATCH = (
    "AVPC1_CROSSED_EVALUATION_SOURCE_MISMATCH"
)
AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH = (
    "AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH"
)
AVPC1_CROSSED_EVALUATION_METHOD_INVALID = (
    "AVPC1_CROSSED_EVALUATION_METHOD_INVALID"
)
AVPC1_CROSSED_EVALUATION_OWNER_BUSY = "AVPC1_CROSSED_EVALUATION_OWNER_BUSY"
AVPC1_CROSSED_EVALUATION_OWNER_TERMINAL = (
    "AVPC1_CROSSED_EVALUATION_OWNER_TERMINAL"
)
AVPC1_CROSSED_EVALUATION_ATTEMPT_FAILED = (
    "AVPC1_CROSSED_EVALUATION_ATTEMPT_FAILED"
)

_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")
_HISTORY_IDS = ("h-left", "h-right")
_TRACK_ROLES = ("candidate", "baseline")
_PROBE_ROLES = ("a-key", "b-control-key")
_EXPECTED_EVENTS = (
    "PAIR_CREATED_PENDING",
    "PAIR_CREATED_PENDING",
    "PAIR_CONFIRMED_STABLE",
    "PAIR_CONFIRMED_STABLE",
)


class AVPC1CrossedEvaluationError(ValueError):
    """One private crossed-evaluation boundary violation."""

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


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_INVALID_INPUT,
            str(exc),
        ) from exc


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST_RE.fullmatch(value) is not None


@dataclass(frozen=True, slots=True)
class AVPC1CrossedProbeSource:
    probe_role: str
    source_binding: AVPC1PrivateAuditoryProbeSourceBinding
    source_sequence: ReceptorTimeSequence

    def __post_init__(self) -> None:
        if (
            self.probe_role not in _PROBE_ROLES
            or type(self.source_binding) is not AVPC1PrivateAuditoryProbeSourceBinding
            or type(self.source_sequence) is not ReceptorTimeSequence
            or self.source_sequence.modality_id != "auditory"
            or len(self.source_sequence.frames) != 1
            or self.source_binding.source_sequence_digest
            != _sequence_digest(self.source_sequence)
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_INVALID_INPUT,
                "probe source is not one exact bound auditory-only source",
            )

    def payload(self) -> dict[str, object]:
        return {
            "probe_role": self.probe_role,
            "source_binding_digest": self.source_binding.source_binding_digest,
            "source_sequence_digest": _sequence_digest(self.source_sequence),
        }


@dataclass(frozen=True, slots=True)
class AVPC1CrossedHistorySource:
    history_id: str
    later_envelope: PPB1ActiveReceptorBatchEnvelope
    relation_partition: AVPC1FrozenRelationHistoryPartitionBinding
    ordered_pairs: tuple[
        tuple[
            PPB1ActiveReceptorTimedFrameBinding,
            PPB1ActiveReceptorTimedFrameBinding,
        ],
        ...,
    ]
    probes: tuple[AVPC1CrossedProbeSource, AVPC1CrossedProbeSource]

    def __post_init__(self) -> None:
        pairs = tuple(self.ordered_pairs)
        probes = tuple(self.probes)
        if (
            self.history_id not in _HISTORY_IDS
            or type(self.later_envelope) is not PPB1ActiveReceptorBatchEnvelope
            or type(self.relation_partition)
            is not AVPC1FrozenRelationHistoryPartitionBinding
            or len(pairs) != 4
            or any(
                not isinstance(pair, tuple)
                or len(pair) != 2
                or type(pair[0]) is not PPB1ActiveReceptorTimedFrameBinding
                or type(pair[1]) is not PPB1ActiveReceptorTimedFrameBinding
                or pair[0].timed_frame.frame.modality_id != "auditory"
                or pair[1].timed_frame.frame.modality_id != "visual"
                for pair in pairs
            )
            or len(probes) != 2
            or any(type(item) is not AVPC1CrossedProbeSource for item in probes)
            or tuple(item.probe_role for item in probes) != _PROBE_ROLES
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_INVALID_INPUT,
                "history source does not match the fixed crossed evaluation shape",
            )
        object.__setattr__(self, "ordered_pairs", pairs)
        object.__setattr__(self, "probes", probes)

    def payload(self) -> dict[str, object]:
        return {
            "history_id": self.history_id,
            "later_envelope_digest": self.later_envelope.envelope_digest,
            "relation_partition_digest": (
                self.relation_partition.relation_history_partition_digest
            ),
            "ordered_pairs": [
                [
                    auditory.timed_frame_provenance_digest,
                    visual.timed_frame_provenance_digest,
                ]
                for auditory, visual in self.ordered_pairs
            ],
            "probes": [probe.payload() for probe in self.probes],
        }


@dataclass(frozen=True, slots=True)
class AVPC1CrossedEvaluationInput:
    evaluation_id: str
    formation_envelope: PPB1ActiveReceptorBatchEnvelope
    profile: PPB1ReceptorProfileBinding
    auditory_fresh_state: PPB1BankState
    visual_fresh_state: PPB1BankState
    histories: tuple[AVPC1CrossedHistorySource, AVPC1CrossedHistorySource]
    input_digest: str

    def __post_init__(self) -> None:
        evaluation_id = _identifier(self.evaluation_id, "evaluation_id")
        histories = tuple(self.histories)
        if (
            type(self.formation_envelope) is not PPB1ActiveReceptorBatchEnvelope
            or type(self.profile) is not PPB1ReceptorProfileBinding
            or type(self.auditory_fresh_state) is not PPB1BankState
            or type(self.visual_fresh_state) is not PPB1BankState
            or len(histories) != 2
            or any(type(item) is not AVPC1CrossedHistorySource for item in histories)
            or tuple(item.history_id for item in histories) != _HISTORY_IDS
            or not _valid_digest(self.input_digest)
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_INVALID_INPUT,
                "evaluation input has the wrong exact source shape",
            )
        object.__setattr__(self, "evaluation_id", evaluation_id)
        object.__setattr__(self, "histories", histories)
        if self.input_digest != _digest(self.payload_without_digest()):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_SOURCE_MISMATCH,
                "evaluation input digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": AVPC1_CROSSED_EVALUATION_SCHEMA_VERSION,
            "contract_digest": AVPC1_CROSSED_EVALUATION_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_CROSSED_EVALUATION_PREFLIGHT_DIGEST,
            "evaluation_id": self.evaluation_id,
            "formation_envelope_digest": self.formation_envelope.envelope_digest,
            "profile_binding_digest": self.profile.digest(),
            "auditory_fresh_state_digest": self.auditory_fresh_state.digest(),
            "visual_fresh_state_digest": self.visual_fresh_state.digest(),
            "histories": [history.payload() for history in self.histories],
        }


def bind_avpc1_crossed_evaluation_input(
    evaluation_id: str,
    formation_envelope: PPB1ActiveReceptorBatchEnvelope,
    profile: PPB1ReceptorProfileBinding,
    auditory_fresh_state: PPB1BankState,
    visual_fresh_state: PPB1BankState,
    histories: tuple[AVPC1CrossedHistorySource, AVPC1CrossedHistorySource],
) -> AVPC1CrossedEvaluationInput:
    values = {
        "evaluation_id": evaluation_id,
        "formation_envelope": formation_envelope,
        "profile": profile,
        "auditory_fresh_state": auditory_fresh_state,
        "visual_fresh_state": visual_fresh_state,
        "histories": tuple(histories),
    }
    provisional = {
        "schema_version": AVPC1_CROSSED_EVALUATION_SCHEMA_VERSION,
        "contract_digest": AVPC1_CROSSED_EVALUATION_CONTRACT_DIGEST,
        "preflight_digest": AVPC1_CROSSED_EVALUATION_PREFLIGHT_DIGEST,
        "evaluation_id": evaluation_id,
        "formation_envelope_digest": formation_envelope.envelope_digest,
        "profile_binding_digest": profile.digest(),
        "auditory_fresh_state_digest": auditory_fresh_state.digest(),
        "visual_fresh_state_digest": visual_fresh_state.digest(),
        "histories": [history.payload() for history in histories],
    }
    return AVPC1CrossedEvaluationInput(
        **values,
        input_digest=_digest(provisional),
    )


@dataclass(frozen=True, slots=True)
class AVPC1TransitionProjection:
    event: str
    slot_status: str
    auditory_key_digest: str
    visual_target_digest: str
    support_count: int
    conflict_identity_digest: str | None

    def __post_init__(self) -> None:
        expected = {
            "PAIR_CREATED_PENDING": ("PENDING", 1),
            "PAIR_CONFIRMED_STABLE": ("STABLE", 2),
        }
        if (
            self.event not in expected
            or (self.slot_status, self.support_count) != expected[self.event]
            or not _valid_digest(self.auditory_key_digest)
            or not _valid_digest(self.visual_target_digest)
            or self.conflict_identity_digest is not None
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                "transition projection is incomplete or outside the core path",
            )

    def payload(self) -> dict[str, object]:
        return {
            "event": self.event,
            "slot_status": self.slot_status,
            "auditory_key_digest": self.auditory_key_digest,
            "visual_target_digest": self.visual_target_digest,
            "support_count": self.support_count,
            "conflict_identity_digest": self.conflict_identity_digest,
        }


@dataclass(frozen=True, slots=True)
class AVPC1ReadoutProjection:
    probe_role: str
    result_role: str
    visual_target_digest: str

    def __post_init__(self) -> None:
        if (
            self.probe_role not in _PROBE_ROLES
            or self.result_role != "MATCH"
            or not _valid_digest(self.visual_target_digest)
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                "readout projection is incomplete or outside the core path",
            )

    def payload(self) -> dict[str, object]:
        return {
            "probe_role": self.probe_role,
            "result_role": self.result_role,
            "visual_target_digest": self.visual_target_digest,
        }


@dataclass(frozen=True, slots=True)
class AVPC1TrackEvaluationResult:
    history_id: str
    track_role: str
    relation_state_identity_digest: str
    relation_state_digest: str
    exposure_receipt_digests: tuple[str, ...]
    transitions: tuple[AVPC1TransitionProjection, ...]
    readouts: tuple[AVPC1ReadoutProjection, ...]
    track_digest: str

    def __post_init__(self) -> None:
        exposures = tuple(self.exposure_receipt_digests)
        transitions = tuple(self.transitions)
        readouts = tuple(self.readouts)
        if (
            self.history_id not in _HISTORY_IDS
            or self.track_role not in _TRACK_ROLES
            or not _valid_digest(self.relation_state_identity_digest)
            or not _valid_digest(self.relation_state_digest)
            or len(exposures) != 4
            or len(set(exposures)) != 4
            or any(not _valid_digest(item) for item in exposures)
            or len(transitions) != 4
            or any(type(item) is not AVPC1TransitionProjection for item in transitions)
            or tuple(item.event for item in transitions) != _EXPECTED_EVENTS
            or len(readouts) != 2
            or any(type(item) is not AVPC1ReadoutProjection for item in readouts)
            or tuple(item.probe_role for item in readouts) != _PROBE_ROLES
            or not _valid_digest(self.track_digest)
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                "track result is incomplete or outside the bound evaluation",
            )
        object.__setattr__(self, "exposure_receipt_digests", exposures)
        object.__setattr__(self, "transitions", transitions)
        object.__setattr__(self, "readouts", readouts)
        if self.track_digest != _digest(self.payload_without_digest()):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                "track result digest mismatch",
            )

    def functional_payload(self) -> dict[str, object]:
        return {
            "history_id": self.history_id,
            "transitions": [item.payload() for item in self.transitions],
            "readouts": [item.payload() for item in self.readouts],
        }

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "history_id": self.history_id,
            "track_role": self.track_role,
            "relation_state_identity_digest": self.relation_state_identity_digest,
            "relation_state_digest": self.relation_state_digest,
            "exposure_receipt_digests": list(self.exposure_receipt_digests),
            "transitions": [item.payload() for item in self.transitions],
            "readouts": [item.payload() for item in self.readouts],
        }


@dataclass(frozen=True, slots=True)
class AVPC1CrossedEvaluationResult:
    evaluation_id: str
    input_digest: str
    formation_result_digest: str
    auditory_bank_state_digest: str
    visual_bank_state_digest: str
    tracks: tuple[AVPC1TrackEvaluationResult, ...]
    decision: str
    result_digest: str

    def __post_init__(self) -> None:
        tracks = tuple(self.tracks)
        if (
            _identifier(self.evaluation_id, "evaluation_id") != self.evaluation_id
            or not all(
                _valid_digest(item)
                for item in (
                    self.input_digest,
                    self.formation_result_digest,
                    self.auditory_bank_state_digest,
                    self.visual_bank_state_digest,
                    self.result_digest,
                )
            )
            or len(tracks) != 4
            or any(type(item) is not AVPC1TrackEvaluationResult for item in tracks)
            or tuple((item.history_id, item.track_role) for item in tracks)
            != (
                ("h-left", "candidate"),
                ("h-left", "baseline"),
                ("h-right", "candidate"),
                ("h-right", "baseline"),
            )
            or self.decision != "FUNCTION_VALID_BASELINE_EXPLAINS"
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                "evaluation result is incomplete or outside the bound decision",
            )
        object.__setattr__(self, "tracks", tracks)
        if self.result_digest != _digest(self.payload_without_digest()):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                "evaluation result digest mismatch",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": AVPC1_CROSSED_EVALUATION_SCHEMA_VERSION,
            "contract_digest": AVPC1_CROSSED_EVALUATION_CONTRACT_DIGEST,
            "preflight_digest": AVPC1_CROSSED_EVALUATION_PREFLIGHT_DIGEST,
            "evaluation_id": self.evaluation_id,
            "input_digest": self.input_digest,
            "formation_result_digest": self.formation_result_digest,
            "auditory_bank_state_digest": self.auditory_bank_state_digest,
            "visual_bank_state_digest": self.visual_bank_state_digest,
            "tracks": [
                {**item.payload_without_digest(), "track_digest": item.track_digest}
                for item in self.tracks
            ],
            "decision": self.decision,
        }


def _source_snapshot(source: AVPC1CrossedEvaluationInput) -> tuple[str, ...]:
    return (
        source.input_digest,
        source.formation_envelope.envelope_digest,
        source.profile.digest(),
        source.auditory_fresh_state.digest(),
        source.visual_fresh_state.digest(),
        *(history.later_envelope.envelope_digest for history in source.histories),
        *(
            history.relation_partition.relation_history_partition_digest
            for history in source.histories
        ),
        *(
            probe.source_binding.source_binding_digest
            for history in source.histories
            for probe in history.probes
        ),
    )


def _transition_projection(
    result: AVPC1AtomicRelationFormationResult,
) -> AVPC1TransitionProjection:
    receipt = result.transition.receipt
    if receipt.event not in _EXPECTED_EVENTS or receipt.selected_slot_id is None:
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
            "relation formation returned a non-core transition",
        )
    selected = tuple(
        slot
        for slot in result.transition.state.slots
        if slot.slot_id == receipt.selected_slot_id
    )
    if len(selected) != 1:
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
            "relation formation did not select one exact slot",
        )
    slot = selected[0]
    if (
        slot.auditory_key_digest is None
        or slot.visual_target_digest is None
        or slot.support_count is None
    ):
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
            "core transition selected an incomplete slot",
        )
    return AVPC1TransitionProjection(
        receipt.event,
        slot.status,
        slot.auditory_key_digest,
        slot.visual_target_digest,
        slot.support_count,
        slot.conflict_identity_digest,
    )


def _require_bound_initial_relation(
    relation: object,
    table_id: str,
    source: AVPC1CrossedEvaluationInput,
    formation: PPB1ActiveBatchFormationResult,
    history: AVPC1CrossedHistorySource,
) -> AVPC1BoundedRelationState:
    auditory_state = formation.auditory_poststate
    visual_state = formation.visual_poststate
    if (
        type(relation) is not AVPC1BoundedRelationState
        or relation.relation_table_id != table_id
        or relation.profile_binding_digest != source.profile.digest()
        or relation.auditory_bank_config_digest
        != source.profile.auditory_config.digest()
        or relation.auditory_bank_state_identity_digest
        != _digest(_state_identity_payload(auditory_state))
        or relation.auditory_bank_state_digest != auditory_state.digest()
        or relation.auditory_prototype_inventory
        != _stable_inventory(source.profile.auditory_config, auditory_state)
        or relation.visual_bank_config_digest != source.profile.visual_config.digest()
        or relation.visual_bank_state_identity_digest
        != _digest(_state_identity_payload(visual_state))
        or relation.visual_bank_state_digest != visual_state.digest()
        or relation.visual_prototype_inventory
        != _stable_inventory(source.profile.visual_config, visual_state)
        or relation.relation_partition is not history.relation_partition
        or relation.relation_history_partition_digest
        != history.relation_partition.relation_history_partition_digest
        or relation.state_identity_digest != _relation_identity_digest(table_id)
        or relation.accepted_exposure_count != 0
        or relation.consumed_exposure_receipt_digests != ()
        or tuple(slot.status for slot in relation.slots) != ("FREE", "FREE")
    ):
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
            "initial relation state does not match the bound track sources",
        )
    return relation


def _require_bound_audio_only_envelope(
    envelope: object,
    envelope_id: str,
    probe: AVPC1CrossedProbeSource,
    source: AVPC1CrossedEvaluationInput,
    formation: PPB1ActiveBatchFormationResult,
    history: AVPC1CrossedHistorySource,
) -> AVPC1PrivateAuditoryOnlyProbeEnvelope:
    timed = probe.source_sequence.frames[0]
    frame = timed.frame
    field_time = timed.field_time
    state = formation.auditory_poststate
    if (
        type(envelope) is not AVPC1PrivateAuditoryOnlyProbeEnvelope
        or envelope.binding_id != envelope_id
        or envelope.source_binding is not probe.source_binding
        or envelope.relation_partition is not history.relation_partition
        or envelope.timed_frame_binding.timed_frame != timed
        or envelope.source_contract_id != probe.source_binding.source_contract_id
        or envelope.source_contract_digest
        != probe.source_binding.source_contract_digest
        or envelope.source_sequence_digest != _sequence_digest(probe.source_sequence)
        or envelope.profile_id != source.profile.profile_id
        or envelope.profile_binding_digest != source.profile.digest()
        or envelope.parameter_digest != source.profile.parameter_digest
        or envelope.auditory_bank_config_digest
        != source.profile.auditory_config.digest()
        or envelope.auditory_bank_state_identity_digest
        != _digest(_state_identity_payload(state))
        or envelope.auditory_bank_state_digest != state.digest()
        or envelope.relation_history_partition_digest
        != history.relation_partition.relation_history_partition_digest
        or envelope.source_clock_id != frame.clock_id
        or envelope.field_clock_id != field_time.clock_id
        or envelope.snapshot_id != frame.snapshot_id
        or envelope.source_window_start_tick != frame.window_start_tick
        or envelope.source_window_end_tick != frame.window_end_tick
        or envelope.field_window_start_tick != field_time.window_start_tick
        or envelope.field_window_end_tick != field_time.window_end_tick
        or envelope.auditory_input_projection_digest
        != _digest(_input_projection(frame))
        or envelope.auditory_input_count != 1
        or envelope.visual_input_count != 0
    ):
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
            "audio-only envelope does not match the bound probe sources",
        )
    return envelope


def _require_bound_auditory_finding(
    finding: object,
    perceptual_probe_id: str,
    probe: AVPC1CrossedProbeSource,
    source: AVPC1CrossedEvaluationInput,
    formation: PPB1ActiveBatchFormationResult,
) -> S1WUReadOnlyPerceptualFinding:
    config = source.profile.auditory_config
    state = formation.auditory_poststate
    frame = probe.source_sequence.frames[0].frame
    if (
        type(finding) is not S1WUReadOnlyPerceptualFinding
        or finding.probe_id != perceptual_probe_id
        or finding.bank_id != config.bank_id
        or finding.modality_id != "auditory"
        or finding.bank_config_digest != config.digest()
        or finding.observed_bank_state_digest != state.digest()
        or finding.state_identity_digest != _digest(_state_identity_payload(state))
        or finding.probe_input_digest != _digest(_input_projection(frame))
    ):
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
            "auditory finding does not match the bound probe and bank sources",
        )
    return finding


def _run_track(
    source: AVPC1CrossedEvaluationInput,
    formation: PPB1ActiveBatchFormationResult,
    history: AVPC1CrossedHistorySource,
    track_role: str,
) -> AVPC1TrackEvaluationResult:
    prefix = f"{source.evaluation_id}.{history.history_id}.{track_role}"
    relation_table_id = f"{prefix}.relation"
    relation = initial_avpc1_bounded_relation_state(
        relation_table_id,
        source.profile,
        formation.auditory_poststate,
        formation.visual_poststate,
        history.relation_partition,
    )
    relation = _require_bound_initial_relation(
        relation,
        relation_table_id,
        source,
        formation,
        history,
    )
    transitions: list[AVPC1TransitionProjection] = []
    exposure_digests: list[str] = []
    for index, (auditory, visual) in enumerate(history.ordered_pairs):
        owner_id = f"{prefix}.relation-owner.{index}"
        consumption_id = f"{prefix}.relation-consumption.{index}"
        auditory_probe_id = (
            f"{source.evaluation_id}.{history.history_id}.auditory-probe.{index}"
        )
        visual_probe_id = (
            f"{source.evaluation_id}.{history.history_id}.visual-probe.{index}"
        )
        exposure_id = f"{source.evaluation_id}.{history.history_id}.exposure.{index}"
        transition_id = f"{prefix}.transition.{index}"
        owner = prepare_avpc1_atomic_relation_formation_consumer_owner(
            owner_id,
            consumption_id,
            auditory_probe_id,
            visual_probe_id,
            exposure_id,
            transition_id,
            formation.formation_result_digest,
            source.formation_envelope.envelope_digest,
            history.later_envelope.envelope_digest,
            source.profile.digest(),
            history.relation_partition.relation_history_partition_digest,
            auditory.timed_frame_provenance_digest,
            visual.timed_frame_provenance_digest,
            relation.state_identity_digest,
            relation.state_digest,
        )
        child = owner.consume_once(
            formation,
            source.formation_envelope,
            history.later_envelope,
            source.profile,
            history.relation_partition,
            auditory,
            visual,
            relation,
        )
        if (
            type(child) is not AVPC1AtomicRelationFormationResult
            or child.consumption_id != consumption_id
            or child.formation_result_digest != formation.formation_result_digest
            or child.formation_envelope_digest
            != source.formation_envelope.envelope_digest
            or child.later_exposure_envelope_digest
            != history.later_envelope.envelope_digest
            or child.profile_binding_digest != source.profile.digest()
            or child.relation_partition_digest
            != history.relation_partition.relation_history_partition_digest
            or child.auditory_frame_provenance_digest
            != auditory.timed_frame_provenance_digest
            or child.visual_frame_provenance_digest
            != visual.timed_frame_provenance_digest
            or child.relation_prestate_identity_digest
            != relation.state_identity_digest
            or child.relation_prestate_digest != relation.state_digest
            or child.transition.receipt.event != _EXPECTED_EVENTS[index]
            or child.authorization_poststate.owner_id != owner_id
            or child.authorization_poststate.consumption_id != consumption_id
            or child.authorization_poststate.auditory_probe_id != auditory_probe_id
            or child.authorization_poststate.visual_probe_id != visual_probe_id
            or child.authorization_poststate.exposure_id != exposure_id
            or child.authorization_poststate.transition_id != transition_id
            or child.authorization_poststate.status != "CONSUMED"
            or child.authorization_poststate.committed_result_digest
            != child.result_digest
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                "relation child does not match the bound track step",
            )
        transitions.append(_transition_projection(child))
        exposure_digests.append(child.exposure_receipt.exposure_receipt_digest)
        relation = child.transition.state

    if relation.accepted_exposure_count != 4:
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
            "track did not consume exactly four relation exposures",
        )
    frozen_before = (
        formation.auditory_poststate.digest(),
        formation.visual_poststate.digest(),
        relation.state_digest,
    )
    readouts: list[AVPC1ReadoutProjection] = []
    for probe in history.probes:
        envelope_id = f"{prefix}.{probe.probe_role}.envelope"
        perceptual_probe_id = f"{prefix}.{probe.probe_role}.perceptual-probe"
        consumer_id = f"{prefix}.{probe.probe_role}.readout"
        relation_probe_id = f"{prefix}.{probe.probe_role}.relation-probe"
        visual_resolver_id = f"{prefix}.{probe.probe_role}.visual-resolver"
        envelope = bind_avpc1_private_auditory_only_probe_envelope(
            envelope_id,
            probe.source_binding,
            probe.source_sequence,
            source.profile,
            formation.auditory_poststate,
            history.relation_partition,
        )
        envelope = _require_bound_audio_only_envelope(
            envelope,
            envelope_id,
            probe,
            source,
            formation,
            history,
        )
        finding = probe_s1wu_perceptual_state(
            source.profile.auditory_config,
            formation.auditory_poststate,
            probe.source_sequence.frames[0].frame,
            perceptual_probe_id,
        )
        finding = _require_bound_auditory_finding(
            finding,
            perceptual_probe_id,
            probe,
            source,
            formation,
        )
        outcome = consume_avpc1_auditory_cued_visual_readout(
            consumer_id,
            relation_probe_id,
            visual_resolver_id,
            envelope,
            finding,
            relation,
            formation.visual_poststate,
            source.profile,
        )
        if (
            type(outcome) is not AVPC1AtomicAuditoryCuedVisualReadoutOutcome
            or outcome.consumer_id != consumer_id
            or outcome.audio_only_envelope_digest != envelope.envelope_digest
            or outcome.auditory_finding_digest != finding.finding_digest
            or outcome.relation_state_identity_digest
            != relation.state_identity_digest
            or outcome.observed_relation_state_digest != relation.state_digest
            or outcome.profile_binding_digest != source.profile.digest()
            or outcome.visual_bank_state_identity_digest
            != relation.visual_bank_state_identity_digest
            or outcome.visual_bank_state_digest
            != formation.visual_poststate.digest()
            or outcome.result_role != "MATCH"
            or outcome.relation_finding.probe_id != relation_probe_id
            or outcome.visual_prototype_state is None
            or outcome.visual_prototype_state.resolver_id != visual_resolver_id
            or outcome.relation_finding.visual_prototype_identity_digest is None
            or outcome.relation_finding.visual_prototype_identity_digest
            != outcome.visual_prototype_state.visual_prototype_identity_digest
        ):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                "core readout did not return one exact visual match",
            )
        readouts.append(
            AVPC1ReadoutProjection(
                probe.probe_role,
                outcome.result_role,
                outcome.relation_finding.visual_prototype_identity_digest,
            )
        )
    if frozen_before != (
        formation.auditory_poststate.digest(),
        formation.visual_poststate.digest(),
        relation.state_digest,
    ):
        raise AVPC1CrossedEvaluationError(
            AVPC1_CROSSED_EVALUATION_METHOD_INVALID,
            "content or relation state changed during read-only probes",
        )
    values = {
        "history_id": history.history_id,
        "track_role": track_role,
        "relation_state_identity_digest": relation.state_identity_digest,
        "relation_state_digest": relation.state_digest,
        "exposure_receipt_digests": tuple(exposure_digests),
        "transitions": tuple(transitions),
        "readouts": tuple(readouts),
    }
    payload = {
        **values,
        "exposure_receipt_digests": exposure_digests,
        "transitions": [item.payload() for item in transitions],
        "readouts": [item.payload() for item in readouts],
    }
    return AVPC1TrackEvaluationResult(**values, track_digest=_digest(payload))


class AVPC1CrossedEvaluationOwner:
    """Single-use owner for one private crossed evaluation."""

    def __init__(self, owner_id: str, authorized_input_digest: str) -> None:
        self._owner_id = _identifier(owner_id, "owner_id")
        if not _valid_digest(authorized_input_digest):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_INVALID_INPUT,
                "authorized input digest is invalid",
            )
        self._authorized_input_digest = authorized_input_digest
        self._status = "AUTHORIZED"
        self._attempt_count = 0
        self._result_digest: str | None = None
        self._failure_code: str | None = None
        self._lock = Lock()

    @property
    def status(self) -> str:
        return self._status

    @property
    def result_digest(self) -> str | None:
        return self._result_digest

    @property
    def failure_code(self) -> str | None:
        return self._failure_code

    @property
    def attempt_count(self) -> int:
        return self._attempt_count

    def consume_once(
        self,
        evaluation_input: AVPC1CrossedEvaluationInput,
    ) -> AVPC1CrossedEvaluationResult:
        if not self._lock.acquire(blocking=False):
            raise AVPC1CrossedEvaluationError(
                AVPC1_CROSSED_EVALUATION_OWNER_BUSY,
                "crossed evaluation owner already has an active call",
            )
        try:
            if self._status != "AUTHORIZED":
                raise AVPC1CrossedEvaluationError(
                    AVPC1_CROSSED_EVALUATION_OWNER_TERMINAL,
                    f"crossed evaluation owner is terminal: {self._status}",
                )
            self._status = "IN_PROGRESS"
            self._attempt_count = 1
            try:
                if (
                    type(evaluation_input) is not AVPC1CrossedEvaluationInput
                    or evaluation_input.input_digest
                    != self._authorized_input_digest
                ):
                    raise AVPC1CrossedEvaluationError(
                        AVPC1_CROSSED_EVALUATION_SOURCE_MISMATCH,
                        "evaluation input does not match owner authorization",
                    )
                before = _source_snapshot(evaluation_input)
                formation_owner_id = (
                    f"{evaluation_input.evaluation_id}.formation-owner"
                )
                formation_authorization_id = (
                    f"{evaluation_input.evaluation_id}.formation-authorization"
                )
                formation_consumption_id = (
                    f"{evaluation_input.evaluation_id}.formation-consumption"
                )
                formation_owner = prepare_ppb1_active_batch_formation_consumer_owner(
                    formation_owner_id,
                    formation_authorization_id,
                    formation_consumption_id,
                    evaluation_input.formation_envelope.envelope_digest,
                    evaluation_input.profile.digest(),
                    evaluation_input.auditory_fresh_state.digest(),
                    evaluation_input.visual_fresh_state.digest(),
                )
                formation = formation_owner.consume_once(
                    evaluation_input.formation_envelope,
                    evaluation_input.profile,
                    evaluation_input.auditory_fresh_state,
                    evaluation_input.visual_fresh_state,
                )
                if (
                    type(formation) is not PPB1ActiveBatchFormationResult
                    or formation.consumption_id != formation_consumption_id
                    or formation.envelope_digest
                    != evaluation_input.formation_envelope.envelope_digest
                    or formation.profile_binding_digest
                    != evaluation_input.profile.digest()
                    or formation.auditory_prestate_digest
                    != evaluation_input.auditory_fresh_state.digest()
                    or formation.visual_prestate_digest
                    != evaluation_input.visual_fresh_state.digest()
                    or formation.authorization_poststate.owner_id
                    != formation_owner_id
                    or formation.authorization_poststate.authorization_id
                    != formation_authorization_id
                    or formation.authorization_poststate.consumption_id
                    != formation_consumption_id
                    or formation.authorization_poststate.status != "CONSUMED"
                    or formation.authorization_poststate.committed_result_digest
                    != formation.formation_result_digest
                ):
                    raise AVPC1CrossedEvaluationError(
                        AVPC1_CROSSED_EVALUATION_CHILD_MISMATCH,
                        "formation child does not bind the evaluation source",
                    )
                tracks = tuple(
                    _run_track(evaluation_input, formation, history, role)
                    for history in evaluation_input.histories
                    for role in _TRACK_ROLES
                )
                for offset in (0, 2):
                    candidate, baseline = tracks[offset : offset + 2]
                    if (
                        candidate.functional_payload()
                        != baseline.functional_payload()
                        or candidate.exposure_receipt_digests
                        != baseline.exposure_receipt_digests
                        or candidate.relation_state_identity_digest
                        == baseline.relation_state_identity_digest
                    ):
                        raise AVPC1CrossedEvaluationError(
                            AVPC1_CROSSED_EVALUATION_METHOD_INVALID,
                            "candidate and generic baseline are not fairly projected",
                        )
                left = tracks[0].readouts
                right = tracks[2].readouts
                if (
                    len(left) != 2
                    or len(right) != 2
                    or left[0].visual_target_digest == left[1].visual_target_digest
                    or right[0].visual_target_digest == right[1].visual_target_digest
                    or left[0].visual_target_digest == right[0].visual_target_digest
                    or left[1].visual_target_digest == right[1].visual_target_digest
                ):
                    raise AVPC1CrossedEvaluationError(
                        AVPC1_CROSSED_EVALUATION_METHOD_INVALID,
                        "core readouts do not materialize two crossed histories",
                    )
                if before != _source_snapshot(evaluation_input):
                    raise AVPC1CrossedEvaluationError(
                        AVPC1_CROSSED_EVALUATION_SOURCE_MISMATCH,
                        "evaluation sources changed during the attempt",
                    )
                values = {
                    "evaluation_id": evaluation_input.evaluation_id,
                    "input_digest": evaluation_input.input_digest,
                    "formation_result_digest": formation.formation_result_digest,
                    "auditory_bank_state_digest": formation.auditory_poststate.digest(),
                    "visual_bank_state_digest": formation.visual_poststate.digest(),
                    "tracks": tracks,
                    "decision": "FUNCTION_VALID_BASELINE_EXPLAINS",
                }
                payload = {
                    "schema_version": AVPC1_CROSSED_EVALUATION_SCHEMA_VERSION,
                    "contract_digest": AVPC1_CROSSED_EVALUATION_CONTRACT_DIGEST,
                    "preflight_digest": AVPC1_CROSSED_EVALUATION_PREFLIGHT_DIGEST,
                    **values,
                    "tracks": [
                        {**track.payload_without_digest(), "track_digest": track.track_digest}
                        for track in tracks
                    ],
                }
                result = AVPC1CrossedEvaluationResult(
                    **values,
                    result_digest=_digest(payload),
                )
                self._status = "CONSUMED"
                self._result_digest = result.result_digest
                return result
            except Exception as exc:
                self._status = "FAILED"
                self._failure_code = str(
                    getattr(
                        exc,
                        "code",
                        AVPC1_CROSSED_EVALUATION_ATTEMPT_FAILED,
                    )
                )
                self._result_digest = None
                raise AVPC1CrossedEvaluationError(
                    AVPC1_CROSSED_EVALUATION_ATTEMPT_FAILED,
                    "crossed evaluation failed without publishing a result",
                ) from exc
        finally:
            self._lock.release()


def prepare_avpc1_crossed_evaluation_owner(
    owner_id: str,
    authorized_input_digest: str,
) -> AVPC1CrossedEvaluationOwner:
    return AVPC1CrossedEvaluationOwner(owner_id, authorized_input_digest)
