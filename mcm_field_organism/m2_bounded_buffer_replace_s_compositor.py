"""Private atomic M2 bounded-buffer REPLACE_S baseline compositor."""

from __future__ import annotations

from dataclasses import dataclass
import math
import re

from .field_step_time import MCMFieldStepTime
from .local_state_replace_s_compositor_core import (
    advance_fast_proposal as _advance_fast_proposal,
    canonical_digest as _digest,
    field_digest as _field_digest,
    field_time_advance_count as _field_time_advance_count,
    fast_proposal_valid as _a1_proposal_valid,
    final_identity_valid as _final_identity_valid,
    geometry_digest as _geometry_digest,
    interval_matches as _interval_matches,
    interval_payload as _interval_payload,
    materialize_replace_s as _materialize_replace_s,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_distributor import ReceptorDistribution
from .shared_mcm_field import SharedMCMField, SharedMCMFieldError
from .transient_neuron_input import TransientNeuronInputSet


CONTRACT_ID = "m2-bounded-buffer-replace-s/s1qw.v1"
SOURCE_S1QV_DIGEST = (
    "6abe7781ffd1d1b238b5e3302960b41d8e98dc880432869187f8eafdb8b95810"
)
CAPACITY_RECORDS = 2
MODE_IDS = ("DELAY", "REPLAY")
RECORD_SCHEMA_ID = "canonical-a1-s-evidence/v1"
CURRENT_FALLBACK_ID = "current-a1-s/v1"

REPLAY_PHASES = ("CAPTURE", "EMIT", "EXHAUSTED")
NOT_APPLICABLE = "NOT_APPLICABLE"
OUTPUT_ROLES = (
    "CURRENT_A1_WARMUP",
    "DELAY_OLDEST_RECORD",
    "CURRENT_A1_CAPTURE",
    "REPLAY_PREFIX_RECORD",
    "CURRENT_A1_EXHAUSTED",
)

COMPLETED = "COMPLETED"
NOT_COMPUTABLE = "NOT_COMPUTABLE"
STATUSES = (COMPLETED, NOT_COMPUTABLE)
FAILURE_CODES = (
    "QW_INPUT_TYPE_INVALID",
    "QW_FIELD_ROLE_INVALID",
    "QW_DISTRIBUTION_OR_INTERVAL_INVALID",
    "QW_CONFIGURATION_INVALID",
    "QW_M2_PRESTATE_INVALID",
    "QW_GEOMETRY_OR_ORDER_MISMATCH",
    "QW_A1_ADVANCE_FAILED",
    "QW_A1_PROPOSAL_INVALID",
    "QW_RECORD_MATERIALIZATION_FAILED",
    "QW_RECORD_INVALID",
    "QW_DELAY_TRANSITION_INVALID",
    "QW_REPLAY_TRANSITION_INVALID",
    "QW_SOURCE_SELECTION_INVALID",
    "QW_S_REPLACEMENT_FAILED",
    "QW_H_OR_PROVENANCE_CHANGED",
    "QW_FIELD_TIME_CARDINALITY_FAILED",
    "QW_NEXT_STATE_INVALID",
    "QW_ATOMIC_OUTPUT_FAILED",
)
PHASES = (
    "api_intake",
    "common_identity_validation",
    "interval_discrimination",
    "a1_fast_proposal",
    "a1_proposal_validation",
    "evidence_record_materialization",
    "mode_transition",
    "source_selection_validation",
    "replace_s_materialization",
    "final_field_validation",
    "next_state_validation",
    "atomic_receipt",
)

_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class M2BoundedBufferCompositorError(ValueError):
    """Raised when a private M2 value violates its structural surface."""


def s1qv_registration_payload() -> dict[str, object]:
    """Return the exact compact registration bound by S1-QV."""

    return {
        "capacity_records": 2,
        "contract_id": "m2-capacity-position-divergence/s1qv.v1",
        "first_divergence_position": "P4",
        "pairwise_distinct_record_digests": True,
        "position_order": ["P0", "P1", "P2", "P3", "P4"],
        "record_order": ["A", "B", "C", "D", "E"],
        "required_equal_output_sources_through": "P3",
        "required_s_distinctions": [["A", "B"], ["C", "E"]],
        "source_schedule": [
            {
                "delay_role": "CURRENT_A1_WARMUP",
                "delay_source": "A",
                "position_id": "P0",
                "replay_phase_after": "CAPTURE",
                "replay_role": "CURRENT_A1_CAPTURE",
                "replay_source": "A",
            },
            {
                "delay_role": "CURRENT_A1_WARMUP",
                "delay_source": "B",
                "position_id": "P1",
                "replay_phase_after": "EMIT",
                "replay_role": "CURRENT_A1_CAPTURE",
                "replay_source": "B",
            },
            {
                "delay_role": "DELAY_OLDEST_RECORD",
                "delay_source": "A",
                "position_id": "P2",
                "replay_phase_after": "EMIT",
                "replay_role": "REPLAY_PREFIX_RECORD",
                "replay_source": "A",
            },
            {
                "delay_role": "DELAY_OLDEST_RECORD",
                "delay_source": "B",
                "position_id": "P3",
                "replay_phase_after": "EXHAUSTED",
                "replay_role": "REPLAY_PREFIX_RECORD",
                "replay_source": "B",
            },
            {
                "delay_role": "DELAY_OLDEST_RECORD",
                "delay_source": "C",
                "position_id": "P4",
                "replay_phase_after": "EXHAUSTED",
                "replay_role": "CURRENT_A1_EXHAUSTED",
                "replay_source": "E",
            },
        ],
    }


@dataclass(frozen=True, slots=True)
class M2BoundedBufferConfiguration:
    source_registration_digest: str
    mode_id: str
    capacity_records: int
    record_schema_id: str
    current_fallback_id: str

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str)
            for value in (
                self.source_registration_digest,
                self.mode_id,
                self.record_schema_id,
                self.current_fallback_id,
            )
        ):
            raise M2BoundedBufferCompositorError(
                "M2 configuration string roles are invalid"
            )
        if isinstance(self.capacity_records, bool) or not isinstance(
            self.capacity_records, int
        ):
            raise M2BoundedBufferCompositorError(
                "M2 capacity must be an integer"
            )


def build_registered_m2_configuration(
    mode_id: str,
) -> M2BoundedBufferConfiguration:
    """Build one exact private S1-QV mode configuration."""

    if mode_id not in MODE_IDS:
        raise M2BoundedBufferCompositorError("M2 mode is not registered")
    return M2BoundedBufferConfiguration(
        SOURCE_S1QV_DIGEST,
        mode_id,
        CAPACITY_RECORDS,
        RECORD_SCHEMA_ID,
        CURRENT_FALLBACK_ID,
    )


def _configuration_valid(configuration: M2BoundedBufferConfiguration) -> bool:
    return (
        configuration.mode_id in MODE_IDS
        and configuration == build_registered_m2_configuration(
            configuration.mode_id
        )
        and _digest(s1qv_registration_payload()) == SOURCE_S1QV_DIGEST
    )


@dataclass(frozen=True, slots=True)
class M2EvidenceRecord:
    s_evidence: tuple[float, ...]
    input_field_digest: str
    geometry_digest: str
    neuron_order: tuple[str, ...]
    distribution_digest: str
    interval_digest: str
    a1_proposal_digest: str
    record_digest: str = ""

    def __post_init__(self) -> None:
        evidence = tuple(float(value) for value in self.s_evidence)
        order = tuple(self.neuron_order)
        if not evidence or len(evidence) != len(order):
            raise M2BoundedBufferCompositorError(
                "M2 record evidence and neuron order must align"
            )
        if any(not math.isfinite(value) or abs(value) > 1.0 for value in evidence):
            raise M2BoundedBufferCompositorError(
                "M2 record evidence must be finite and normalized"
            )
        if any(not isinstance(item, str) or not item for item in order):
            raise M2BoundedBufferCompositorError(
                "M2 record neuron identities are invalid"
            )
        if len(set(order)) != len(order):
            raise M2BoundedBufferCompositorError(
                "M2 record neuron identities must be unique"
            )
        digests = (
            self.input_field_digest,
            self.geometry_digest,
            self.distribution_digest,
            self.interval_digest,
            self.a1_proposal_digest,
        )
        if any(not isinstance(value, str) or not _SHA256.fullmatch(value) for value in digests):
            raise M2BoundedBufferCompositorError(
                "M2 record source digests are invalid"
            )
        object.__setattr__(self, "s_evidence", evidence)
        object.__setattr__(self, "neuron_order", order)
        expected = _digest(self.canonical_payload())
        if self.record_digest and self.record_digest != expected:
            raise M2BoundedBufferCompositorError("M2 record digest mismatch")
        object.__setattr__(self, "record_digest", expected)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "s_evidence": list(self.s_evidence),
            "input_field_digest": self.input_field_digest,
            "geometry_digest": self.geometry_digest,
            "neuron_order": list(self.neuron_order),
            "distribution_digest": self.distribution_digest,
            "interval_digest": self.interval_digest,
            "a1_proposal_digest": self.a1_proposal_digest,
        }


@dataclass(frozen=True, slots=True)
class M2BoundedBufferState:
    mode_id: str
    geometry_digest: str
    neuron_order: tuple[str, ...]
    records: tuple[M2EvidenceRecord, ...]
    replay_phase: str
    replay_cursor: int

    def __post_init__(self) -> None:
        if not isinstance(self.mode_id, str) or not isinstance(
            self.geometry_digest, str
        ):
            raise M2BoundedBufferCompositorError("M2 state identity is invalid")
        order = tuple(self.neuron_order)
        records = tuple(self.records)
        if any(not isinstance(item, str) for item in order):
            raise M2BoundedBufferCompositorError(
                "M2 state neuron order is invalid"
            )
        if any(not isinstance(item, M2EvidenceRecord) for item in records):
            raise M2BoundedBufferCompositorError(
                "M2 state requires evidence records"
            )
        if not isinstance(self.replay_phase, str):
            raise M2BoundedBufferCompositorError("M2 replay phase is invalid")
        if isinstance(self.replay_cursor, bool) or not isinstance(
            self.replay_cursor, int
        ):
            raise M2BoundedBufferCompositorError("M2 replay cursor is invalid")
        object.__setattr__(self, "neuron_order", order)
        object.__setattr__(self, "records", records)


def _neuron_order(field: SharedMCMField) -> tuple[str, ...]:
    return tuple(item.neuron_id for item in field.layer.neurons)


def build_empty_m2_buffer(
    configuration: M2BoundedBufferConfiguration,
    field: SharedMCMField,
) -> M2BoundedBufferState:
    """Build one empty mode-specific M2 state for a neutral field."""

    if not isinstance(configuration, M2BoundedBufferConfiguration) or not (
        isinstance(field, SharedMCMField)
    ):
        raise M2BoundedBufferCompositorError(
            "M2 fresh state requires configuration and field"
        )
    if not _configuration_valid(configuration):
        raise M2BoundedBufferCompositorError(
            "M2 fresh state requires the S1-QV registration"
        )
    return M2BoundedBufferState(
        configuration.mode_id,
        _geometry_digest(field),
        _neuron_order(field),
        (),
        NOT_APPLICABLE if configuration.mode_id == "DELAY" else "CAPTURE",
        0,
    )


def _record_valid(
    record: object,
    geometry_digest: str,
    neuron_order: tuple[str, ...],
) -> bool:
    if not isinstance(record, M2EvidenceRecord):
        return False
    return (
        record.geometry_digest == geometry_digest
        and record.neuron_order == neuron_order
        and len(record.s_evidence) == len(neuron_order)
        and record.record_digest == _digest(record.canonical_payload())
        and all(math.isfinite(value) and abs(value) <= 1.0 for value in record.s_evidence)
    )


def _prestate_valid(
    state: M2BoundedBufferState,
    configuration: M2BoundedBufferConfiguration,
) -> bool:
    if state.mode_id != configuration.mode_id:
        return False
    if len(state.records) > CAPACITY_RECORDS:
        return False
    if len(set(state.neuron_order)) != len(state.neuron_order):
        return False
    if not _SHA256.fullmatch(state.geometry_digest):
        return False
    if any(
        not _record_valid(item, state.geometry_digest, state.neuron_order)
        for item in state.records
    ):
        return False
    if state.mode_id == "DELAY":
        return state.replay_phase == NOT_APPLICABLE and state.replay_cursor == 0
    if state.mode_id != "REPLAY":
        return False
    if state.replay_phase == "CAPTURE":
        return len(state.records) < CAPACITY_RECORDS and state.replay_cursor == 0
    if state.replay_phase == "EMIT":
        return (
            len(state.records) == CAPACITY_RECORDS
            and state.replay_cursor in (0, 1)
        )
    if state.replay_phase == "EXHAUSTED":
        return (
            len(state.records) == CAPACITY_RECORDS
            and state.replay_cursor == CAPACITY_RECORDS
        )
    return False


def _state_payload(state: M2BoundedBufferState) -> dict[str, object]:
    return {
        "mode_id": state.mode_id,
        "geometry_digest": state.geometry_digest,
        "neuron_order": list(state.neuron_order),
        "records": [item.canonical_payload() | {"record_digest": item.record_digest} for item in state.records],
        "replay_phase": state.replay_phase,
        "replay_cursor": state.replay_cursor,
    }


def _state_digest(state: M2BoundedBufferState) -> str:
    return _digest(_state_payload(state))


def _configuration_digest(
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
    configuration: M2BoundedBufferConfiguration,
) -> str:
    return _digest(
        {
            "neutral_response_seconds": substrate_config.response_time_seconds,
            "fast_afterimage_seconds": afterimage_config.time_constant_seconds,
            "dissipation_per_second": (
                None
                if dissipation_config is None
                else dissipation_config.leak_rate_per_second
            ),
            "m2_configuration": {
                "source_registration_digest": configuration.source_registration_digest,
                "mode_id": configuration.mode_id,
                "capacity_records": configuration.capacity_records,
                "record_schema_id": configuration.record_schema_id,
                "current_fallback_id": configuration.current_fallback_id,
            },
        }
    )


def _build_record(
    proposal: SharedMCMField,
    input_field_digest: str,
    geometry_digest: str,
    neuron_order: tuple[str, ...],
    distribution_digest: str,
    interval_digest: str,
) -> M2EvidenceRecord:
    return M2EvidenceRecord(
        tuple(item.activation for item in proposal.layer.neurons),
        input_field_digest,
        geometry_digest,
        neuron_order,
        distribution_digest,
        interval_digest,
        _field_digest(proposal),
    )


@dataclass(frozen=True, slots=True)
class _M2Transition:
    next_state: M2BoundedBufferState
    output_role: str
    output: tuple[float, ...]
    source_record: M2EvidenceRecord | None
    selection_position: int | None


def _advance_delay(
    state: M2BoundedBufferState,
    current: M2EvidenceRecord,
) -> _M2Transition:
    if len(state.records) < CAPACITY_RECORDS:
        return _M2Transition(
            M2BoundedBufferState(
                state.mode_id,
                state.geometry_digest,
                state.neuron_order,
                (*state.records, current),
                NOT_APPLICABLE,
                0,
            ),
            "CURRENT_A1_WARMUP",
            current.s_evidence,
            None,
            None,
        )
    source = state.records[0]
    return _M2Transition(
        M2BoundedBufferState(
            state.mode_id,
            state.geometry_digest,
            state.neuron_order,
            (state.records[1], current),
            NOT_APPLICABLE,
            0,
        ),
        "DELAY_OLDEST_RECORD",
        source.s_evidence,
        source,
        0,
    )


def _advance_replay(
    state: M2BoundedBufferState,
    current: M2EvidenceRecord,
) -> _M2Transition:
    if state.replay_phase == "CAPTURE":
        records = (*state.records, current)
        phase = "EMIT" if len(records) == CAPACITY_RECORDS else "CAPTURE"
        return _M2Transition(
            M2BoundedBufferState(
                state.mode_id,
                state.geometry_digest,
                state.neuron_order,
                records,
                phase,
                0,
            ),
            "CURRENT_A1_CAPTURE",
            current.s_evidence,
            None,
            None,
        )
    if state.replay_phase == "EMIT":
        source = state.records[state.replay_cursor]
        cursor = state.replay_cursor + 1
        phase = "EXHAUSTED" if cursor == CAPACITY_RECORDS else "EMIT"
        return _M2Transition(
            M2BoundedBufferState(
                state.mode_id,
                state.geometry_digest,
                state.neuron_order,
                state.records,
                phase,
                cursor,
            ),
            "REPLAY_PREFIX_RECORD",
            source.s_evidence,
            source,
            state.replay_cursor,
        )
    if state.replay_phase == "EXHAUSTED":
        return _M2Transition(
            state,
            "CURRENT_A1_EXHAUSTED",
            current.s_evidence,
            None,
            None,
        )
    raise M2BoundedBufferCompositorError("M2 replay phase is invalid")


def _selection_valid(
    state: M2BoundedBufferState,
    current: M2EvidenceRecord,
    transition: object,
) -> bool:
    if not isinstance(transition, _M2Transition):
        return False
    if transition.output_role not in OUTPUT_ROLES:
        return False
    if len(transition.output) != len(state.neuron_order):
        return False
    if any(not math.isfinite(value) or abs(value) > 1.0 for value in transition.output):
        return False
    if state.mode_id == "DELAY":
        if len(state.records) < CAPACITY_RECORDS:
            return (
                transition.output_role == "CURRENT_A1_WARMUP"
                and transition.output == current.s_evidence
                and transition.source_record is None
                and transition.selection_position is None
            )
        return (
            transition.output_role == "DELAY_OLDEST_RECORD"
            and transition.source_record is state.records[0]
            and transition.output == state.records[0].s_evidence
            and transition.selection_position == 0
        )
    if state.replay_phase == "CAPTURE":
        return (
            transition.output_role == "CURRENT_A1_CAPTURE"
            and transition.output == current.s_evidence
            and transition.source_record is None
            and transition.selection_position is None
        )
    if state.replay_phase == "EMIT":
        source = state.records[state.replay_cursor]
        return (
            transition.output_role == "REPLAY_PREFIX_RECORD"
            and transition.source_record is source
            and transition.output == source.s_evidence
            and transition.selection_position == state.replay_cursor
        )
    return (
        state.replay_phase == "EXHAUSTED"
        and transition.output_role == "CURRENT_A1_EXHAUSTED"
        and transition.output == current.s_evidence
        and transition.source_record is None
        and transition.selection_position is None
    )


def _next_state_valid(
    state: object,
    configuration: M2BoundedBufferConfiguration,
    geometry_digest: str,
    neuron_order: tuple[str, ...],
) -> bool:
    return (
        isinstance(state, M2BoundedBufferState)
        and state.geometry_digest == geometry_digest
        and state.neuron_order == neuron_order
        and _prestate_valid(state, configuration)
    )


@dataclass(frozen=True, slots=True)
class M2BoundedBufferReplaceSReceipt:
    contract_id: str
    source_registration_digest: str
    mode_id: str | None
    interval_kind: str | None
    input_field_digest: str | None
    distribution_digest: str | None
    interval_digest: str | None
    configuration_digest: str | None
    geometry_digest: str | None
    neuron_order: tuple[str, ...]
    m2_prestate_digest: str | None
    a1_proposal_digest: str | None
    current_record_digest: str | None
    output_role: str | None
    selection_position: int | None
    source_record_digest: str | None
    source_input_field_digest: str | None
    source_distribution_digest: str | None
    source_interval_digest: str | None
    source_a1_proposal_digest: str | None
    selected_s_digest: str | None
    m2_next_state_digest: str | None
    next_replay_phase: str | None
    next_replay_cursor: int | None
    final_field_digest: str | None
    s_replacement_confirmed: bool
    h_identity_confirmed: bool
    field_time_advance_count: int
    phases: tuple[str, ...]
    status: str
    failure_codes: tuple[str, ...]
    receipt_digest: str = ""

    def __post_init__(self) -> None:
        if self.contract_id != CONTRACT_ID:
            raise M2BoundedBufferCompositorError("receipt contract mismatch")
        if self.source_registration_digest != SOURCE_S1QV_DIGEST:
            raise M2BoundedBufferCompositorError(
                "receipt source registration mismatch"
            )
        if self.status not in STATUSES:
            raise M2BoundedBufferCompositorError("receipt status is invalid")
        if tuple(self.phases) != PHASES[: len(self.phases)]:
            raise M2BoundedBufferCompositorError(
                "receipt phases are not a canonical prefix"
            )
        if any(code not in FAILURE_CODES for code in self.failure_codes):
            raise M2BoundedBufferCompositorError(
                "receipt contains an unknown failure code"
            )
        if tuple(sorted(self.failure_codes, key=FAILURE_CODES.index)) != tuple(
            self.failure_codes
        ):
            raise M2BoundedBufferCompositorError(
                "receipt failure codes are not canonical"
            )
        if self.status == COMPLETED and self.failure_codes:
            raise M2BoundedBufferCompositorError(
                "completed receipt cannot contain failures"
            )
        if self.status == NOT_COMPUTABLE and not self.failure_codes:
            raise M2BoundedBufferCompositorError(
                "failed receipt requires one failure code"
            )
        object.__setattr__(self, "neuron_order", tuple(self.neuron_order))
        object.__setattr__(self, "phases", tuple(self.phases))
        object.__setattr__(self, "failure_codes", tuple(self.failure_codes))
        expected = _digest(self.canonical_payload())
        if self.receipt_digest and self.receipt_digest != expected:
            raise M2BoundedBufferCompositorError("receipt digest mismatch")
        object.__setattr__(self, "receipt_digest", expected)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "contract_id": self.contract_id,
            "source_registration_digest": self.source_registration_digest,
            "mode_id": self.mode_id,
            "interval_kind": self.interval_kind,
            "input_field_digest": self.input_field_digest,
            "distribution_digest": self.distribution_digest,
            "interval_digest": self.interval_digest,
            "configuration_digest": self.configuration_digest,
            "geometry_digest": self.geometry_digest,
            "neuron_order": list(self.neuron_order),
            "m2_prestate_digest": self.m2_prestate_digest,
            "a1_proposal_digest": self.a1_proposal_digest,
            "current_record_digest": self.current_record_digest,
            "output_role": self.output_role,
            "selection_position": self.selection_position,
            "source_record_digest": self.source_record_digest,
            "source_input_field_digest": self.source_input_field_digest,
            "source_distribution_digest": self.source_distribution_digest,
            "source_interval_digest": self.source_interval_digest,
            "source_a1_proposal_digest": self.source_a1_proposal_digest,
            "selected_s_digest": self.selected_s_digest,
            "m2_next_state_digest": self.m2_next_state_digest,
            "next_replay_phase": self.next_replay_phase,
            "next_replay_cursor": self.next_replay_cursor,
            "final_field_digest": self.final_field_digest,
            "s_replacement_confirmed": self.s_replacement_confirmed,
            "h_identity_confirmed": self.h_identity_confirmed,
            "field_time_advance_count": self.field_time_advance_count,
            "phases": list(self.phases),
            "status": self.status,
            "failure_codes": list(self.failure_codes),
        }


@dataclass(frozen=True, slots=True)
class M2BoundedBufferReplaceSResult:
    field: SharedMCMField | str
    next_m2_state: M2BoundedBufferState | str
    receipt: M2BoundedBufferReplaceSReceipt

    def __post_init__(self) -> None:
        if not isinstance(self.receipt, M2BoundedBufferReplaceSReceipt):
            raise M2BoundedBufferCompositorError("result requires one receipt")
        if self.receipt.status == COMPLETED:
            if not isinstance(self.field, SharedMCMField) or not isinstance(
                self.next_m2_state, M2BoundedBufferState
            ):
                raise M2BoundedBufferCompositorError(
                    "completed result requires field and M2 state"
                )
        elif self.field != NOT_COMPUTABLE or self.next_m2_state != NOT_COMPUTABLE:
            raise M2BoundedBufferCompositorError(
                "failed result cannot publish partial state"
            )


_RECEIPT_DEFAULTS = {
    "mode_id": None,
    "interval_kind": None,
    "input_field_digest": None,
    "distribution_digest": None,
    "interval_digest": None,
    "configuration_digest": None,
    "geometry_digest": None,
    "neuron_order": (),
    "m2_prestate_digest": None,
    "a1_proposal_digest": None,
    "current_record_digest": None,
    "output_role": None,
    "selection_position": None,
    "source_record_digest": None,
    "source_input_field_digest": None,
    "source_distribution_digest": None,
    "source_interval_digest": None,
    "source_a1_proposal_digest": None,
    "selected_s_digest": None,
    "m2_next_state_digest": None,
    "next_replay_phase": None,
    "next_replay_cursor": None,
    "final_field_digest": None,
}


def _failure(code: str, phase_count: int, **values) -> M2BoundedBufferReplaceSResult:
    payload = {**_RECEIPT_DEFAULTS, **values}
    receipt = M2BoundedBufferReplaceSReceipt(
        contract_id=CONTRACT_ID,
        source_registration_digest=SOURCE_S1QV_DIGEST,
        **payload,
        s_replacement_confirmed=False,
        h_identity_confirmed=False,
        field_time_advance_count=0,
        phases=PHASES[:phase_count],
        status=NOT_COMPUTABLE,
        failure_codes=(code,),
    )
    return M2BoundedBufferReplaceSResult(
        NOT_COMPUTABLE, NOT_COMPUTABLE, receipt
    )


def _atomic_output_valid(
    final: SharedMCMField,
    next_state: M2BoundedBufferState,
    receipt: M2BoundedBufferReplaceSReceipt,
) -> bool:
    return (
        receipt.status == COMPLETED
        and receipt.final_field_digest == _field_digest(final)
        and receipt.m2_next_state_digest == _state_digest(next_state)
        and receipt.s_replacement_confirmed
        and receipt.h_identity_confirmed
        and receipt.field_time_advance_count == 1
    )


def advance_m2_bounded_buffer_replace_s(
    field,
    distribution,
    interval_input,
    neutral_substrate_config,
    fast_afterimage_config,
    m2_configuration,
    m2_prestate,
    dissipation_config=None,
) -> M2BoundedBufferReplaceSResult:
    """Advance one private M2 bounded-buffer field interval atomically."""

    required_types_valid = (
        isinstance(field, SharedMCMField)
        and isinstance(distribution, ReceptorDistribution)
        and isinstance(interval_input, (MCMFieldStepTime, TransientNeuronInputSet))
        and isinstance(neutral_substrate_config, NeutralLocalFieldSubstrateConfig)
        and isinstance(fast_afterimage_config, NeutralFastAfterimageConfig)
        and isinstance(m2_configuration, M2BoundedBufferConfiguration)
        and isinstance(m2_prestate, M2BoundedBufferState)
        and (
            dissipation_config is None
            or isinstance(dissipation_config, NeutralFieldDissipationConfig)
        )
    )
    if not required_types_valid:
        return _failure("QW_INPUT_TYPE_INVALID", 1)

    interval_kind = (
        "sync" if isinstance(interval_input, MCMFieldStepTime) else "transient"
    )
    input_field_digest = _field_digest(field)
    distribution_digest = distribution.digest()
    interval_digest = _digest(_interval_payload(interval_input))
    configuration_digest = _configuration_digest(
        neutral_substrate_config,
        fast_afterimage_config,
        dissipation_config,
        m2_configuration,
    )
    geometry_digest = _geometry_digest(field)
    neuron_order = _neuron_order(field)
    m2_prestate_digest = _state_digest(m2_prestate)
    common = {
        "mode_id": m2_configuration.mode_id,
        "interval_kind": interval_kind,
        "input_field_digest": input_field_digest,
        "distribution_digest": distribution_digest,
        "interval_digest": interval_digest,
        "configuration_digest": configuration_digest,
        "geometry_digest": geometry_digest,
        "neuron_order": neuron_order,
        "m2_prestate_digest": m2_prestate_digest,
    }

    if field.substrate is not None or field.development is not None:
        return _failure("QW_FIELD_ROLE_INVALID", 2, **common)
    if not _configuration_valid(m2_configuration):
        return _failure("QW_CONFIGURATION_INVALID", 2, **common)
    if not _prestate_valid(m2_prestate, m2_configuration):
        return _failure("QW_M2_PRESTATE_INVALID", 2, **common)
    if (
        m2_prestate.geometry_digest != geometry_digest
        or m2_prestate.neuron_order != neuron_order
    ):
        return _failure("QW_GEOMETRY_OR_ORDER_MISMATCH", 2, **common)
    if not _interval_matches(field, distribution, interval_input):
        return _failure(
            "QW_DISTRIBUTION_OR_INTERVAL_INVALID", 3, **common
        )

    try:
        proposal = _advance_fast_proposal(
            field,
            distribution,
            interval_input,
            neutral_substrate_config,
            fast_afterimage_config,
            dissipation_config,
            advance_neutral_fast_shared_field,
            advance_neutral_fast_shared_field_transient,
        )
    except NeutralLocalFieldSubstrateError:
        return _failure("QW_A1_ADVANCE_FAILED", 4, **common)
    if not _a1_proposal_valid(field, proposal, distribution):
        return _failure("QW_A1_PROPOSAL_INVALID", 5, **common)
    a1_proposal_digest = _field_digest(proposal)
    with_proposal = {**common, "a1_proposal_digest": a1_proposal_digest}

    try:
        current_record = _build_record(
            proposal,
            input_field_digest,
            geometry_digest,
            neuron_order,
            distribution_digest,
            interval_digest,
        )
    except (M2BoundedBufferCompositorError, TypeError, ValueError, OverflowError):
        return _failure("QW_RECORD_MATERIALIZATION_FAILED", 6, **with_proposal)
    if not _record_valid(current_record, geometry_digest, neuron_order):
        return _failure("QW_RECORD_INVALID", 6, **with_proposal)
    with_record = {
        **with_proposal,
        "current_record_digest": current_record.record_digest,
    }

    try:
        if m2_configuration.mode_id == "DELAY":
            transition = _advance_delay(m2_prestate, current_record)
        else:
            transition = _advance_replay(m2_prestate, current_record)
    except (M2BoundedBufferCompositorError, IndexError, TypeError, ValueError):
        code = (
            "QW_DELAY_TRANSITION_INVALID"
            if m2_configuration.mode_id == "DELAY"
            else "QW_REPLAY_TRANSITION_INVALID"
        )
        return _failure(code, 7, **with_record)

    if not _selection_valid(m2_prestate, current_record, transition):
        return _failure("QW_SOURCE_SELECTION_INVALID", 8, **with_record)
    source = transition.source_record
    selected_s_digest = _digest({"signed_output": list(transition.output)})
    transition_values = {
        **with_record,
        "output_role": transition.output_role,
        "selection_position": transition.selection_position,
        "source_record_digest": None if source is None else source.record_digest,
        "source_input_field_digest": (
            None if source is None else source.input_field_digest
        ),
        "source_distribution_digest": (
            None if source is None else source.distribution_digest
        ),
        "source_interval_digest": None if source is None else source.interval_digest,
        "source_a1_proposal_digest": (
            None if source is None else source.a1_proposal_digest
        ),
        "selected_s_digest": selected_s_digest,
        "m2_next_state_digest": _state_digest(transition.next_state),
        "next_replay_phase": transition.next_state.replay_phase,
        "next_replay_cursor": transition.next_state.replay_cursor,
    }

    try:
        final = _materialize_replace_s(proposal, transition.output)
    except (SharedMCMFieldError, TypeError, ValueError):
        return _failure("QW_S_REPLACEMENT_FAILED", 9, **transition_values)
    if not _final_identity_valid(proposal, final, transition.output):
        return _failure("QW_H_OR_PROVENANCE_CHANGED", 10, **transition_values)
    advance_count = _field_time_advance_count(field, final)
    if advance_count != 1:
        return _failure(
            "QW_FIELD_TIME_CARDINALITY_FAILED", 10, **transition_values
        )
    if not _next_state_valid(
        transition.next_state,
        m2_configuration,
        geometry_digest,
        neuron_order,
    ):
        return _failure("QW_NEXT_STATE_INVALID", 11, **transition_values)

    receipt = M2BoundedBufferReplaceSReceipt(
        contract_id=CONTRACT_ID,
        source_registration_digest=SOURCE_S1QV_DIGEST,
        **transition_values,
        final_field_digest=_field_digest(final),
        s_replacement_confirmed=True,
        h_identity_confirmed=True,
        field_time_advance_count=advance_count,
        phases=PHASES,
        status=COMPLETED,
        failure_codes=(),
    )
    if not _atomic_output_valid(final, transition.next_state, receipt):
        return _failure("QW_ATOMIC_OUTPUT_FAILED", 12, **transition_values)
    return M2BoundedBufferReplaceSResult(final, transition.next_state, receipt)
