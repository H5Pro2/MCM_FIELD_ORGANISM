"""Private profile-derived atomic B4/TSPM-1 coordinator for S2-JW."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from threading import Lock

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from tools._s2jw_default_live_av_pairing import S2JVBoundAVPairV1
from tools._s2jw_default_live_profile import (
    B4_CAPACITY,
    S2JWDefaultLiveProfileV1,
    build_s2jw_default_live_profile,
)
from tools._s2jw_profiled_memory_ledger import (
    S2JVLedgerLimitsV1,
    S2JVResourceLedgerV1,
    build_s2jv_ledger_limits,
    derive_s2jv_resource_ledger,
    validate_s2jv_resource_ledger,
)


S2JW_COORDINATOR_SCHEMA = "s2jw.profiled-memory-coordinator.v1"
S2JW_INVALID = "S2JW_INVALID"
S2JW_CONFIG_MISMATCH = "S2JW_CONFIG_MISMATCH"
S2JW_SOURCE_INVALID = "S2JW_SOURCE_INVALID"
S2JW_PRESTATE_INVALID = "S2JW_PRESTATE_INVALID"
S2JW_OWNER_MISMATCH = "S2JW_OWNER_MISMATCH"
S2JW_OWNER_TERMINAL = "S2JW_OWNER_TERMINAL"
S2JW_OWNER_BUSY = "S2JW_OWNER_BUSY"
S2JW_B4_FAILED = "S2JW_B4_FAILED"
S2JW_TSPM_FAILED = "S2JW_TSPM_FAILED"
S2JW_RELATION_FAILED = "S2JW_RELATION_FAILED"
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_IDENTIFIER = re.compile(r"^[a-z][a-z0-9.-]{1,95}$")


class S2JWCoordinatorError(RuntimeError):
    """One private coordinator contract violation."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2JWCoordinatorError(code, message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _identifier(value: object, role: str) -> str:
    _require(
        isinstance(value, str) and _IDENTIFIER.fullmatch(value) is not None,
        S2JW_INVALID,
        f"{role} is not a canonical identifier",
    )
    return value


def _values(values: object, length: int, role: str) -> tuple[float, ...]:
    _require(
        type(values) is tuple and len(values) == length,
        S2JW_SOURCE_INVALID,
        f"{role} must be one exact {length}-value tuple",
    )
    _require(
        all(type(value) in (int, float) for value in values),
        S2JW_SOURCE_INVALID,
        f"{role} contains a nonnumeric or boolean value",
    )
    result = tuple(float(value) for value in values)
    _require(
        all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in result),
        S2JW_SOURCE_INVALID,
        f"{role} is outside the receptor value domain",
    )
    return result


def _b4_digest(state: comparison._B4State) -> str:
    return _digest(comparison._canonical(state))


@dataclass(frozen=True, slots=True)
class S2JVCoordinatorConfigV1:
    profile: S2JWDefaultLiveProfileV1
    tspm_config: tspm1.TSPM1ConfigBinding
    ledger_limits: S2JVLedgerLimitsV1
    b4_capacity: int
    auditory_dimension: int
    visual_dimension: int
    av_dimension: int
    config_digest: str
    schema: str = S2JW_COORDINATOR_SCHEMA

    def __post_init__(self) -> None:
        _require(
            self.schema == S2JW_COORDINATOR_SCHEMA
            and type(self.profile) is S2JWDefaultLiveProfileV1
            and type(self.tspm_config) is tspm1.TSPM1ConfigBinding
            and type(self.ledger_limits) is S2JVLedgerLimitsV1
            and self.tspm_config == self.profile.tspm_config
            and self.ledger_limits == build_s2jv_ledger_limits(self.profile)
            and self.b4_capacity == self.profile.b4_capacity == B4_CAPACITY
            and self.auditory_dimension == self.profile.auditory_dimension
            and self.visual_dimension == self.profile.visual_dimension
            and self.av_dimension == self.profile.av_dimension
            and self.config_digest == _digest(self.payload_without_digest()),
            S2JW_CONFIG_MISMATCH,
            "coordinator config is incomplete or not profile-derived",
        )
        tspm1._validate_config(self.tspm_config)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "profile_digest": self.profile.binding_digest,
            "tspm_config_digest": self.tspm_config.config_binding_digest,
            "ledger_limits_digest": self.ledger_limits.limits_digest,
            "b4_capacity": self.b4_capacity,
            "auditory_dimension": self.auditory_dimension,
            "visual_dimension": self.visual_dimension,
            "av_dimension": self.av_dimension,
        }


def build_s2jv_coordinator_config(
    *,
    tspm_config: tspm1.TSPM1ConfigBinding,
    b4_capacity: int,
    ledger_limits: S2JVLedgerLimitsV1,
) -> S2JVCoordinatorConfigV1:
    profile = build_s2jw_default_live_profile()
    _require(
        type(tspm_config) is tspm1.TSPM1ConfigBinding
        and tspm_config == profile.tspm_config
        and b4_capacity == B4_CAPACITY
        and ledger_limits == build_s2jv_ledger_limits(profile),
        S2JW_CONFIG_MISMATCH,
        "coordinator inputs differ from the validated default-live profile",
    )
    payload = {
        "schema": S2JW_COORDINATOR_SCHEMA,
        "profile_digest": profile.binding_digest,
        "tspm_config_digest": tspm_config.config_binding_digest,
        "ledger_limits_digest": ledger_limits.limits_digest,
        "b4_capacity": b4_capacity,
        "auditory_dimension": profile.auditory_dimension,
        "visual_dimension": profile.visual_dimension,
        "av_dimension": profile.av_dimension,
    }
    return S2JVCoordinatorConfigV1(
        profile,
        tspm_config,
        ledger_limits,
        b4_capacity,
        profile.auditory_dimension,
        profile.visual_dimension,
        profile.av_dimension,
        _digest(payload),
    )


def _validate_config(config: object) -> S2JVCoordinatorConfigV1:
    _require(type(config) is S2JVCoordinatorConfigV1, S2JW_INVALID, "exact config required")
    assert isinstance(config, S2JVCoordinatorConfigV1)
    _require(
        config.config_digest == _digest(config.payload_without_digest()),
        S2JW_CONFIG_MISMATCH,
        "config digest changed",
    )
    tspm1._validate_config(config.tspm_config)
    return config


def _validate_b4_state(
    config: S2JVCoordinatorConfigV1,
    state: object,
) -> comparison._B4State:
    _require(type(state) is comparison._B4State, S2JW_PRESTATE_INVALID, "exact B4 state required")
    assert isinstance(state, comparison._B4State)
    _require(
        type(state.accepted_count) is int
        and state.accepted_count >= 0
        and len(state.entries) == config.b4_capacity
        and all(type(entry) is comparison._FIFOEntry for entry in state.entries),
        S2JW_PRESTATE_INVALID,
        "B4 state shape differs",
    )
    expected_ids = tuple(f"b4.slot.{index:03d}" for index in range(config.b4_capacity))
    _require(
        tuple(entry.slot_id for entry in state.entries) == expected_ids,
        S2JW_PRESTATE_INVALID,
        "B4 slot identities differ",
    )
    indexes: list[int] = []
    for entry in state.entries:
        if entry.occupied:
            _values(entry.values, config.av_dimension, "B4 entry")
            _require(
                type(entry.formation_index) is int
                and 1 <= entry.formation_index <= state.accepted_count,
                S2JW_PRESTATE_INVALID,
                "occupied B4 entry has invalid index",
            )
            indexes.append(entry.formation_index)
        else:
            _require(
                entry.values == () and entry.formation_index is None,
                S2JW_PRESTATE_INVALID,
                "free B4 entry carries state",
            )
    expected_count = min(state.accepted_count, config.b4_capacity)
    expected_indexes = set(
        range(
            max(1, state.accepted_count - config.b4_capacity + 1),
            state.accepted_count + 1,
        )
    )
    _require(
        len(indexes) == expected_count
        and len(indexes) == len(set(indexes))
        and set(indexes) == expected_indexes,
        S2JW_PRESTATE_INVALID,
        "B4 FIFO anatomy differs",
    )
    return state


@dataclass(frozen=True, slots=True)
class S2JVCompositeStateV1:
    config_digest: str
    generation: int
    parent_state_digest: str | None
    last_input_digest: str | None
    b4_state: comparison._B4State
    tspm_state: tspm1.TSPM1CompositeState
    state_digest: str
    schema: str = S2JW_COORDINATOR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "config_digest": self.config_digest,
            "generation": self.generation,
            "parent_state_digest": self.parent_state_digest,
            "last_input_digest": self.last_input_digest,
            "b4_state_digest": _b4_digest(self.b4_state),
            "tspm_state_digest": self.tspm_state.composite_state_digest,
        }


def _make_state(
    config: S2JVCoordinatorConfigV1,
    generation: int,
    parent_state_digest: str | None,
    last_input_digest: str | None,
    b4_state: comparison._B4State,
    tspm_state: tspm1.TSPM1CompositeState,
) -> S2JVCompositeStateV1:
    payload = {
        "schema": S2JW_COORDINATOR_SCHEMA,
        "config_digest": config.config_digest,
        "generation": generation,
        "parent_state_digest": parent_state_digest,
        "last_input_digest": last_input_digest,
        "b4_state_digest": _b4_digest(b4_state),
        "tspm_state_digest": tspm_state.composite_state_digest,
    }
    return S2JVCompositeStateV1(
        config.config_digest,
        generation,
        parent_state_digest,
        last_input_digest,
        b4_state,
        tspm_state,
        _digest(payload),
    )


def _validate_state(
    config: S2JVCoordinatorConfigV1,
    state: object,
) -> S2JVCompositeStateV1:
    _require(type(state) is S2JVCompositeStateV1, S2JW_INVALID, "exact composite state required")
    assert isinstance(state, S2JVCompositeStateV1)
    _validate_b4_state(config, state.b4_state)
    tspm1._validate_composite_state(config.tspm_config, state.tspm_state)
    lineage = (
        state.generation == 0
        and state.parent_state_digest is None
        and state.last_input_digest is None
    ) or (
        state.generation > 0
        and _valid_digest(state.parent_state_digest)
        and _valid_digest(state.last_input_digest)
    )
    _require(
        state.schema == S2JW_COORDINATOR_SCHEMA
        and state.config_digest == config.config_digest
        and type(state.generation) is int
        and state.generation >= 0
        and state.generation == state.b4_state.accepted_count
        and state.generation == state.tspm_state.generation
        and state.generation == state.tspm_state.fast_state.accepted_exposure_count
        and lineage
        and state.state_digest == _digest(state.payload_without_digest()),
        S2JW_PRESTATE_INVALID,
        "composite state relation differs",
    )
    return state


def initial_s2jv_composite_state(
    config: S2JVCoordinatorConfigV1,
) -> S2JVCompositeStateV1:
    config = _validate_config(config)
    b4_state = comparison._B4State(
        0,
        tuple(
            comparison._FIFOEntry(f"b4.slot.{index:03d}", False, (), None)
            for index in range(config.b4_capacity)
        ),
    )
    tspm_state = tspm1.initial_tspm1_composite_state(config.tspm_config)
    return _validate_state(
        config,
        _make_state(config, 0, None, None, b4_state, tspm_state),
    )


def _source_values(
    config: S2JVCoordinatorConfigV1,
    source: S2JVBoundAVPairV1,
) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
    auditory = _values(
        source.auditory.timed_frame.frame.values,
        config.auditory_dimension,
        "auditory source",
    )
    visual = _values(
        source.visual.timed_frame.frame.values,
        config.visual_dimension,
        "visual source",
    )
    av = auditory + visual
    _require(
        source.envelope.profile_id == "default-live"
        and source.envelope.profile_binding_digest == config.profile.profile.digest()
        and source.plan.profile_binding_digest == config.profile.profile.digest()
        and source.av_values_digest == _digest(list(av)),
        S2JW_SOURCE_INVALID,
        "source profile or value binding differs",
    )
    return auditory, visual, av


@dataclass(frozen=True, slots=True)
class S2JVBoundInputV1:
    config_digest: str
    source: S2JVBoundAVPairV1
    tspm_exposure: tspm1.TSPM1BoundExposure
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    av_values: tuple[float, ...]
    input_digest: str
    schema: str = S2JW_COORDINATOR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "role": "FORMATION",
            "config_digest": self.config_digest,
            "pairing_digest": self.source.pairing_digest,
            "tspm_exposure_digest": self.tspm_exposure.exposure_digest,
            "av_values_digest": _digest(list(self.av_values)),
        }


@dataclass(frozen=True, slots=True)
class S2JVBoundProbeV1:
    config_digest: str
    source: S2JVBoundAVPairV1
    tspm_probe: tspm1.TSPM1BoundProbe
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    av_values: tuple[float, ...]
    probe_digest: str
    schema: str = S2JW_COORDINATOR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "role": "READ_ONLY",
            "config_digest": self.config_digest,
            "pairing_digest": self.source.pairing_digest,
            "tspm_probe_digest": self.tspm_probe.probe_digest,
            "av_values_digest": _digest(list(self.av_values)),
        }


def bind_s2jv_coordinator_input(
    *,
    config: S2JVCoordinatorConfigV1,
    source: S2JVBoundAVPairV1,
) -> S2JVBoundInputV1:
    config = _validate_config(config)
    _require(type(source) is S2JVBoundAVPairV1, S2JW_SOURCE_INVALID, "exact AV pair required")
    auditory, visual, av = _source_values(config, source)
    exposure = tspm1.bind_tspm1_exposure(
        config.tspm_config,
        source.envelope,
        source.auditory,
        source.visual,
    )
    result = S2JVBoundInputV1(
        config.config_digest,
        source,
        exposure,
        auditory,
        visual,
        av,
        "",
    )
    object.__setattr__(result, "input_digest", _digest(result.payload_without_digest()))
    return _validate_input(config, result)


def bind_s2jv_probe(
    *,
    config: S2JVCoordinatorConfigV1,
    source: S2JVBoundAVPairV1,
) -> S2JVBoundProbeV1:
    config = _validate_config(config)
    _require(type(source) is S2JVBoundAVPairV1, S2JW_SOURCE_INVALID, "exact AV pair required")
    auditory, visual, av = _source_values(config, source)
    probe = tspm1.bind_tspm1_probe(
        config.tspm_config,
        source.envelope,
        source.auditory,
        source.visual,
    )
    result = S2JVBoundProbeV1(
        config.config_digest,
        source,
        probe,
        auditory,
        visual,
        av,
        "",
    )
    object.__setattr__(result, "probe_digest", _digest(result.payload_without_digest()))
    return _validate_probe(config, result)


def _validate_input(
    config: S2JVCoordinatorConfigV1,
    source: object,
) -> S2JVBoundInputV1:
    _require(type(source) is S2JVBoundInputV1, S2JW_SOURCE_INVALID, "exact input required")
    assert isinstance(source, S2JVBoundInputV1)
    auditory, visual, av = _source_values(config, source.source)
    _require(
        source.schema == S2JW_COORDINATOR_SCHEMA
        and source.config_digest == config.config_digest
        and source.tspm_exposure.envelope is source.source.envelope
        and source.tspm_exposure.auditory is source.source.auditory
        and source.tspm_exposure.visual is source.source.visual
        and source.auditory_values == auditory
        and source.visual_values == visual
        and source.av_values == av
        and source.input_digest == _digest(source.payload_without_digest()),
        S2JW_SOURCE_INVALID,
        "bound formation input differs",
    )
    tspm1._validate_bound_source_provenance(config.tspm_config, source.tspm_exposure)
    tspm1._validate_bound_source_geometry(config.tspm_config, source.tspm_exposure)
    return source


def _validate_probe(
    config: S2JVCoordinatorConfigV1,
    source: object,
) -> S2JVBoundProbeV1:
    _require(type(source) is S2JVBoundProbeV1, S2JW_SOURCE_INVALID, "exact probe required")
    assert isinstance(source, S2JVBoundProbeV1)
    auditory, visual, av = _source_values(config, source.source)
    _require(
        source.schema == S2JW_COORDINATOR_SCHEMA
        and source.config_digest == config.config_digest
        and source.tspm_probe.envelope is source.source.envelope
        and source.tspm_probe.auditory is source.source.auditory
        and source.tspm_probe.visual is source.source.visual
        and source.auditory_values == auditory
        and source.visual_values == visual
        and source.av_values == av
        and source.probe_digest == _digest(source.payload_without_digest()),
        S2JW_SOURCE_INVALID,
        "bound read-only probe differs",
    )
    tspm1._validate_bound_source_provenance(config.tspm_config, source.tspm_probe)
    tspm1._validate_bound_source_geometry(config.tspm_config, source.tspm_probe)
    return source


@dataclass(frozen=True, slots=True)
class S2JVFormationReceiptV1:
    config_digest: str
    owner_prestate_digest: str
    input_digest: str
    composite_prestate_digest: str
    b4_event: str
    b4_slot_id: str
    b4_poststate_digest: str
    tspm_result_digest: str
    tspm_poststate_digest: str
    ledger_digest: str
    composite_poststate_digest: str
    receipt_digest: str
    schema: str = S2JW_COORDINATOR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "config_digest": self.config_digest,
            "owner_prestate_digest": self.owner_prestate_digest,
            "input_digest": self.input_digest,
            "composite_prestate_digest": self.composite_prestate_digest,
            "b4_event": self.b4_event,
            "b4_slot_id": self.b4_slot_id,
            "b4_poststate_digest": self.b4_poststate_digest,
            "tspm_result_digest": self.tspm_result_digest,
            "tspm_poststate_digest": self.tspm_poststate_digest,
            "ledger_digest": self.ledger_digest,
            "composite_poststate_digest": self.composite_poststate_digest,
        }


@dataclass(frozen=True, slots=True)
class S2JVFormationOwnerSnapshotV1:
    owner_id: str
    authorization_id: str
    consumption_id: str
    authorized_config_digest: str
    authorized_prestate_digest: str
    authorized_input_digest: str
    status: str
    attempt_count: int
    use_count: int
    committed_result_digest: str | None
    failure_code: str | None
    owner_state_digest: str
    schema: str = S2JW_COORDINATOR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "owner_id": self.owner_id,
            "authorization_id": self.authorization_id,
            "consumption_id": self.consumption_id,
            "authorized_config_digest": self.authorized_config_digest,
            "authorized_prestate_digest": self.authorized_prestate_digest,
            "authorized_input_digest": self.authorized_input_digest,
            "status": self.status,
            "attempt_count": self.attempt_count,
            "use_count": self.use_count,
            "committed_result_digest": self.committed_result_digest,
            "failure_code": self.failure_code,
        }


@dataclass(frozen=True, slots=True)
class S2JVFormationResultV1:
    poststate: S2JVCompositeStateV1
    receipt: S2JVFormationReceiptV1
    ledger: S2JVResourceLedgerV1
    owner_poststate: S2JVFormationOwnerSnapshotV1
    result_digest: str
    schema: str = S2JW_COORDINATOR_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        owner = self.owner_poststate.payload_without_digest()
        owner["committed_result_digest"] = None
        return {
            "schema": self.schema,
            "poststate_digest": self.poststate.state_digest,
            "receipt_digest": self.receipt.receipt_digest,
            "ledger_digest": self.ledger.ledger_digest,
            "owner_poststate_without_commit_digest": owner,
        }


def _owner_snapshot(owner: "S2JVFormationOwner") -> S2JVFormationOwnerSnapshotV1:
    values = {
        "schema": S2JW_COORDINATOR_SCHEMA,
        "owner_id": owner._owner_id,
        "authorization_id": owner._authorization_id,
        "consumption_id": owner._consumption_id,
        "authorized_config_digest": owner._authorized_config_digest,
        "authorized_prestate_digest": owner._authorized_prestate_digest,
        "authorized_input_digest": owner._authorized_input_digest,
        "status": owner._status,
        "attempt_count": owner._attempt_count,
        "use_count": owner._use_count,
        "committed_result_digest": owner._committed_result_digest,
        "failure_code": owner._failure_code,
    }
    return S2JVFormationOwnerSnapshotV1(
        owner._owner_id,
        owner._authorization_id,
        owner._consumption_id,
        owner._authorized_config_digest,
        owner._authorized_prestate_digest,
        owner._authorized_input_digest,
        owner._status,
        owner._attempt_count,
        owner._use_count,
        owner._committed_result_digest,
        owner._failure_code,
        _digest(values),
    )


def _advance_b4_candidate(
    state: comparison._B4State,
    source: S2JVBoundInputV1,
) -> tuple[comparison._B4State, dict[str, object], tuple[int, int]]:
    return comparison._advance_b4(state, source.av_values, state.accepted_count + 1)


def _advance_tspm_candidate(
    config: S2JVCoordinatorConfigV1,
    state: tspm1.TSPM1CompositeState,
    source: S2JVBoundInputV1,
    owner: "S2JVFormationOwner",
) -> tspm1.TSPM1StepResult:
    tspm_owner = tspm1.TSPM1CoordinatorOwner(
        f"{owner._owner_id}.tspm",
        f"{owner._authorization_id}.tspm",
        f"{owner._consumption_id}.tspm",
        config.tspm_config.config_binding_digest,
        state.composite_state_digest,
        source.tspm_exposure.exposure_digest,
    )
    return tspm_owner.consume_once(config.tspm_config, state, source.tspm_exposure)


class S2JVFormationOwner:
    """One-use authority for one atomic B4/TSPM formation."""

    def __init__(
        self,
        owner_id: str,
        authorization_id: str,
        consumption_id: str,
        authorized_config_digest: str,
        authorized_prestate_digest: str,
        authorized_input_digest: str,
    ) -> None:
        self._owner_id = _identifier(owner_id, "owner_id")
        self._authorization_id = _identifier(authorization_id, "authorization_id")
        self._consumption_id = _identifier(consumption_id, "consumption_id")
        _require(
            all(
                _valid_digest(value)
                for value in (
                    authorized_config_digest,
                    authorized_prestate_digest,
                    authorized_input_digest,
                )
            ),
            S2JW_OWNER_MISMATCH,
            "owner authorization digests are invalid",
        )
        self._authorized_config_digest = authorized_config_digest
        self._authorized_prestate_digest = authorized_prestate_digest
        self._authorized_input_digest = authorized_input_digest
        self._status = "AUTHORIZED"
        self._attempt_count = 0
        self._use_count = 0
        self._committed_result_digest: str | None = None
        self._failure_code: str | None = None
        self._lock = Lock()

    def snapshot(self) -> S2JVFormationOwnerSnapshotV1:
        _require(self._status != "IN_PROGRESS", S2JW_OWNER_BUSY, "owner is busy")
        return _owner_snapshot(self)

    def consume_once(
        self,
        config: S2JVCoordinatorConfigV1,
        prestate: S2JVCompositeStateV1,
        source: S2JVBoundInputV1,
    ) -> S2JVFormationResultV1:
        if not self._lock.acquire(blocking=False):
            raise S2JWCoordinatorError(S2JW_OWNER_BUSY, "owner is busy")
        try:
            if self._status in {"CONSUMED", "FAILED"}:
                raise S2JWCoordinatorError(S2JW_OWNER_TERMINAL, "owner is terminal")
            owner_prestate_digest = _owner_snapshot(self).owner_state_digest
            self._status = "IN_PROGRESS"
            self._attempt_count = 1
            phase = "PREVALIDATION"
            try:
                config = _validate_config(config)
                prestate = _validate_state(config, prestate)
                source = _validate_input(config, source)
                _require(
                    config.config_digest == self._authorized_config_digest
                    and prestate.state_digest == self._authorized_prestate_digest
                    and source.input_digest == self._authorized_input_digest,
                    S2JW_OWNER_MISMATCH,
                    "owner authorization does not match inputs",
                )
                tspm1._validate_bound_source_time(
                    prestate.tspm_state.fast_state,
                    source.tspm_exposure,
                    strictly_later=True,
                )
                phase = "B4"
                b4_poststate, b4_event, _ = _advance_b4_candidate(prestate.b4_state, source)
                phase = "TSPM"
                tspm_result = _advance_tspm_candidate(
                    config,
                    prestate.tspm_state,
                    source,
                    self,
                )
                phase = "RELATION"
                _validate_b4_state(config, b4_poststate)
                tspm1._validate_step_result_relations(
                    config.tspm_config,
                    prestate.tspm_state,
                    source.tspm_exposure,
                    tspm_result,
                )
                _require(
                    b4_poststate.accepted_count == prestate.generation + 1
                    and tspm_result.poststate.generation == prestate.generation + 1,
                    S2JW_RELATION_FAILED,
                    "candidate generations differ",
                )
                poststate = _validate_state(
                    config,
                    _make_state(
                        config,
                        prestate.generation + 1,
                        prestate.state_digest,
                        source.input_digest,
                        b4_poststate,
                        tspm_result.poststate,
                    ),
                )
                relation_digest = _digest(
                    {
                        "schema": S2JW_COORDINATOR_SCHEMA,
                        "prestate_digest": prestate.state_digest,
                        "input_digest": source.input_digest,
                        "b4_poststate_digest": _b4_digest(b4_poststate),
                        "tspm_poststate_digest": tspm_result.poststate.composite_state_digest,
                        "composite_poststate_digest": poststate.state_digest,
                    }
                )
                ledger = derive_s2jv_resource_ledger(
                    profile=config.profile,
                    limits=config.ledger_limits,
                    operation_id=self._consumption_id,
                    operation_role="FORMATION",
                    result_digest=relation_digest,
                )
                validate_s2jv_resource_ledger(
                    profile=config.profile,
                    limits=config.ledger_limits,
                    ledger=ledger,
                    expected_role="FORMATION",
                )
                receipt_payload = {
                    "schema": S2JW_COORDINATOR_SCHEMA,
                    "config_digest": config.config_digest,
                    "owner_prestate_digest": owner_prestate_digest,
                    "input_digest": source.input_digest,
                    "composite_prestate_digest": prestate.state_digest,
                    "b4_event": b4_event["event"],
                    "b4_slot_id": b4_event["slot_id"],
                    "b4_poststate_digest": _b4_digest(b4_poststate),
                    "tspm_result_digest": tspm_result.result_digest,
                    "tspm_poststate_digest": tspm_result.poststate.composite_state_digest,
                    "ledger_digest": ledger.ledger_digest,
                    "composite_poststate_digest": poststate.state_digest,
                }
                receipt = S2JVFormationReceiptV1(
                    config.config_digest,
                    owner_prestate_digest,
                    source.input_digest,
                    prestate.state_digest,
                    b4_event["event"],
                    b4_event["slot_id"],
                    _b4_digest(b4_poststate),
                    tspm_result.result_digest,
                    tspm_result.poststate.composite_state_digest,
                    ledger.ledger_digest,
                    poststate.state_digest,
                    _digest(receipt_payload),
                )
                _require(
                    receipt.receipt_digest == _digest(receipt.payload_without_digest()),
                    S2JW_RELATION_FAILED,
                    "formation receipt differs",
                )
                self._status = "CONSUMED"
                self._use_count = 1
                projected_owner = _owner_snapshot(self)
                temporary = S2JVFormationResultV1(
                    poststate,
                    receipt,
                    ledger,
                    projected_owner,
                    "",
                )
                result_digest = _digest(temporary.payload_without_digest())
                self._committed_result_digest = result_digest
                result = S2JVFormationResultV1(
                    poststate,
                    receipt,
                    ledger,
                    _owner_snapshot(self),
                    result_digest,
                )
                _require(
                    result.result_digest == _digest(result.payload_without_digest())
                    and result.owner_poststate.status == "CONSUMED"
                    and result.owner_poststate.committed_result_digest == result.result_digest,
                    S2JW_RELATION_FAILED,
                    "formation result differs",
                )
                return result
            except Exception as exc:
                if self._status == "CONSUMED":
                    self._use_count = 0
                    self._committed_result_digest = None
                if isinstance(exc, S2JWCoordinatorError):
                    code = exc.code
                elif phase == "B4":
                    code = S2JW_B4_FAILED
                elif phase == "TSPM":
                    code = S2JW_TSPM_FAILED
                elif phase == "PREVALIDATION":
                    code = S2JW_PRESTATE_INVALID
                else:
                    code = S2JW_RELATION_FAILED
                self._status = "FAILED"
                self._use_count = 0
                self._committed_result_digest = None
                self._failure_code = code
                if isinstance(exc, S2JWCoordinatorError):
                    raise
                raise S2JWCoordinatorError(code, f"atomic step stopped during {phase}") from exc
        finally:
            self._lock.release()


def advance_s2jv_atomic(
    *,
    config: S2JVCoordinatorConfigV1,
    prestate: S2JVCompositeStateV1,
    source: S2JVBoundInputV1,
    owner: S2JVFormationOwner,
) -> S2JVFormationResultV1:
    _require(type(owner) is S2JVFormationOwner, S2JW_INVALID, "exact owner required")
    return owner.consume_once(config, prestate, source)
