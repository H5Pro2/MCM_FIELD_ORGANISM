"""Private same-probe value binding for S2-KJ 336-value findings."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools import _s2jw_profiled_memory_read_only as read_only
from tools._s2jw_profiled_memory_ledger import validate_s2jv_resource_ledger


S2KJ_BINDING_SCHEMA = "s2kj.validated-perceptual-finding-336.v1"
S2KJ_BINDING_INVALID = "S2KJ_BINDING_INVALID"
S2KJ_DIMENSION_INVALID = "S2KJ_DIMENSION_INVALID"
S2KJ_DIGEST_MISMATCH = "S2KJ_DIGEST_MISMATCH"
S2KJ_ROLE_INVALID = "S2KJ_ROLE_INVALID"
S2KJ_STATE_MISMATCH = "S2KJ_STATE_MISMATCH"
S2KJ_STABILITY_INVALID = "S2KJ_STABILITY_INVALID"
S2KJ_CAPACITY_EXCEEDED = "S2KJ_CAPACITY_EXCEEDED"

ROLE_ORDER = (
    "B4_RECENT",
    "TSPM_FAST",
    "B_STABLE_AUDITORY",
    "B_STABLE_VISUAL",
)
ABSENCE_REASONS = (
    "NO_OCCUPIED_SOURCE",
    "NO_FUNCTIONAL_MATCH",
    "NO_STABLE_MATCH",
)
MAX_CANDIDATES = 4
MAX_REFERENCED_VALUES = 1008
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2KJBindingError(ValueError):
    """The same-probe value binding is incomplete or contradictory."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code


def _require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise S2KJBindingError(code, message)


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


def _values(values: object, length: int, role: str) -> tuple[float, ...]:
    _require(
        type(values) is tuple and len(values) == length,
        S2KJ_DIMENSION_INVALID,
        f"{role} must contain exactly {length} values",
    )
    _require(
        all(type(value) in (int, float) for value in values),
        S2KJ_DIMENSION_INVALID,
        f"{role} contains a nonnumeric or boolean value",
    )
    result = tuple(float(value) for value in values)
    _require(
        all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in result),
        S2KJ_DIMENSION_INVALID,
        f"{role} differs from the receptor domain",
    )
    return result


@dataclass(frozen=True, slots=True)
class AVContextCandidate336V1:
    role: str
    slot_id: str
    slot_digest: str
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    auditory_values_digest: str
    visual_values_digest: str
    av_values_digest: str
    formation_index: int | None
    support: int | None
    last_selected_step: int | None
    auditory_distance: float
    visual_distance: float
    mechanical_match: bool
    observed_state_digest: str
    probe_digest: str
    source_digest: str
    candidate_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "role": self.role,
            "slot_id": self.slot_id,
            "slot_digest": self.slot_digest,
            "auditory_values": list(self.auditory_values),
            "visual_values": list(self.visual_values),
            "auditory_values_digest": self.auditory_values_digest,
            "visual_values_digest": self.visual_values_digest,
            "av_values_digest": self.av_values_digest,
            "formation_index": self.formation_index,
            "support": self.support,
            "last_selected_step": self.last_selected_step,
            "auditory_distance": self.auditory_distance,
            "visual_distance": self.visual_distance,
            "mechanical_match": self.mechanical_match,
            "observed_state_digest": self.observed_state_digest,
            "probe_digest": self.probe_digest,
            "source_digest": self.source_digest,
        }


@dataclass(frozen=True, slots=True)
class StableModalityCandidate336V1:
    role: str
    modality: str
    dimension: int
    slot_id: str
    slot_digest: str
    values: tuple[float, ...]
    values_digest: str
    support: int
    stable: bool
    native_distance: float
    mechanical_match: bool
    observed_state_digest: str
    probe_digest: str
    source_digest: str
    candidate_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "role": self.role,
            "modality": self.modality,
            "dimension": self.dimension,
            "slot_id": self.slot_id,
            "slot_digest": self.slot_digest,
            "values": list(self.values),
            "values_digest": self.values_digest,
            "support": self.support,
            "stable": self.stable,
            "native_distance": self.native_distance,
            "mechanical_match": self.mechanical_match,
            "observed_state_digest": self.observed_state_digest,
            "probe_digest": self.probe_digest,
            "source_digest": self.source_digest,
        }


Candidate336 = AVContextCandidate336V1 | StableModalityCandidate336V1


@dataclass(frozen=True, slots=True)
class RoleFinding336V1:
    role: str
    status: str
    absence_reason: str | None
    candidate: Candidate336 | None
    observed_state_digest: str
    probe_digest: str
    source_finding_digest: str
    finding_digest: str

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "role": self.role,
            "status": self.status,
            "absence_reason": self.absence_reason,
            "candidate_digest": self.candidate.candidate_digest if self.candidate else None,
            "observed_state_digest": self.observed_state_digest,
            "probe_digest": self.probe_digest,
            "source_finding_digest": self.source_finding_digest,
        }


@dataclass(frozen=True, slots=True)
class ValidatedPerceptualFinding336V1:
    config_digest: str
    composite_state_digest: str
    probe_digest: str
    source_digest: str
    auditory_source_digest: str
    visual_source_digest: str
    source_time_geometry_digest: str
    source_finding_digest: str
    role_findings: tuple[RoleFinding336V1, ...]
    prestate_digest: str
    poststate_digest: str
    source_ledger_digest: str
    candidate_count: int
    referenced_value_count: int
    binding_digest: str
    schema: str = S2KJ_BINDING_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "config_digest": self.config_digest,
            "composite_state_digest": self.composite_state_digest,
            "probe_digest": self.probe_digest,
            "source_digest": self.source_digest,
            "auditory_source_digest": self.auditory_source_digest,
            "visual_source_digest": self.visual_source_digest,
            "source_time_geometry_digest": self.source_time_geometry_digest,
            "source_finding_digest": self.source_finding_digest,
            "role_finding_digests": [item.finding_digest for item in self.role_findings],
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "source_ledger_digest": self.source_ledger_digest,
            "candidate_count": self.candidate_count,
            "referenced_value_count": self.referenced_value_count,
        }


def _validate_candidate(candidate: Candidate336, expected_role: str) -> int:
    _require(candidate.role == expected_role, S2KJ_ROLE_INVALID, "candidate role differs")
    _require(
        all(
            _valid_digest(value)
            for value in (
                candidate.slot_digest,
                candidate.observed_state_digest,
                candidate.probe_digest,
                candidate.source_digest,
                candidate.candidate_digest,
            )
        ),
        S2KJ_DIGEST_MISMATCH,
        "candidate digest binding is invalid",
    )
    if type(candidate) is AVContextCandidate336V1:
        auditory = _values(candidate.auditory_values, 48, "AV auditory candidate")
        visual = _values(candidate.visual_values, 288, "AV visual candidate")
        _require(
            expected_role in ROLE_ORDER[:2]
            and candidate.mechanical_match is True
            and math.isfinite(candidate.auditory_distance)
            and candidate.auditory_distance >= 0.0
            and math.isfinite(candidate.visual_distance)
            and candidate.visual_distance >= 0.0
            and candidate.auditory_values_digest == _digest(list(auditory))
            and candidate.visual_values_digest == _digest(list(visual))
            and candidate.av_values_digest == _digest(list(auditory + visual))
            and candidate.candidate_digest == _digest(candidate.payload_without_digest()),
            S2KJ_BINDING_INVALID,
            "AV candidate relation differs",
        )
        if expected_role == "B4_RECENT":
            _require(
                type(candidate.formation_index) is int
                and candidate.formation_index > 0
                and candidate.support is None
                and candidate.last_selected_step is None,
                S2KJ_BINDING_INVALID,
                "B4 candidate anatomy differs",
            )
        else:
            _require(
                candidate.formation_index is None
                and type(candidate.support) is int
                and candidate.support > 0
                and type(candidate.last_selected_step) is int
                and candidate.last_selected_step > 0,
                S2KJ_BINDING_INVALID,
                "Fast candidate anatomy differs",
            )
        return 336
    _require(
        type(candidate) is StableModalityCandidate336V1,
        S2KJ_ROLE_INVALID,
        "unknown candidate type",
    )
    expected = {
        "B_STABLE_AUDITORY": ("AUDITORY", 48),
        "B_STABLE_VISUAL": ("VISUAL", 288),
    }.get(expected_role)
    _require(expected is not None, S2KJ_ROLE_INVALID, "stable candidate role differs")
    modality, dimension = expected
    values = _values(candidate.values, dimension, "stable modality candidate")
    _require(
        candidate.modality == modality
        and candidate.dimension == dimension
        and type(candidate.support) is int
        and candidate.support >= 3
        and candidate.stable is True
        and candidate.mechanical_match is True
        and math.isfinite(candidate.native_distance)
        and candidate.native_distance >= 0.0
        and candidate.values_digest == _digest(list(values))
        and candidate.candidate_digest == _digest(candidate.payload_without_digest()),
        S2KJ_STABILITY_INVALID,
        "stable candidate relation differs",
    )
    return dimension


def _validate_role_finding(
    finding: RoleFinding336V1,
    expected_role: str,
    binding: ValidatedPerceptualFinding336V1 | None = None,
) -> int:
    _require(type(finding) is RoleFinding336V1, S2KJ_ROLE_INVALID, "exact role finding required")
    _require(finding.role == expected_role, S2KJ_ROLE_INVALID, "role order differs")
    _require(
        _valid_digest(finding.observed_state_digest)
        and _valid_digest(finding.probe_digest)
        and _valid_digest(finding.source_finding_digest)
        and finding.finding_digest == _digest(finding.payload_without_digest()),
        S2KJ_DIGEST_MISMATCH,
        "role finding digest differs",
    )
    if binding is not None:
        _require(
            finding.observed_state_digest == binding.composite_state_digest
            and finding.probe_digest == binding.probe_digest
            and finding.source_finding_digest == binding.source_finding_digest,
            S2KJ_BINDING_INVALID,
            "role finding source relation differs",
        )
    if finding.status == "ABSENT_VALID":
        _require(
            finding.candidate is None and finding.absence_reason in ABSENCE_REASONS,
            S2KJ_BINDING_INVALID,
            "valid absence anatomy differs",
        )
        return 0
    _require(
        finding.status == "AVAILABLE"
        and finding.absence_reason is None
        and finding.candidate is not None,
        S2KJ_BINDING_INVALID,
        "available finding anatomy differs",
    )
    return _validate_candidate(finding.candidate, expected_role)


def _validate_validated_finding(
    value: object,
) -> ValidatedPerceptualFinding336V1:
    _require(
        type(value) is ValidatedPerceptualFinding336V1,
        S2KJ_BINDING_INVALID,
        "exact validated finding required",
    )
    assert isinstance(value, ValidatedPerceptualFinding336V1)
    _require(
        value.schema == S2KJ_BINDING_SCHEMA
        and tuple(item.role for item in value.role_findings) == ROLE_ORDER
        and value.prestate_digest == value.composite_state_digest == value.poststate_digest
        and all(
            _valid_digest(item)
            for item in (
                value.config_digest,
                value.composite_state_digest,
                value.probe_digest,
                value.source_digest,
                value.auditory_source_digest,
                value.visual_source_digest,
                value.source_time_geometry_digest,
                value.source_finding_digest,
                value.source_ledger_digest,
                value.binding_digest,
            )
        ),
        S2KJ_BINDING_INVALID,
        "validated finding header differs",
    )
    referenced = sum(
        _validate_role_finding(item, role, value)
        for item, role in zip(value.role_findings, ROLE_ORDER, strict=True)
    )
    candidates = sum(item.candidate is not None for item in value.role_findings)
    _require(
        value.candidate_count == candidates <= MAX_CANDIDATES
        and value.referenced_value_count == referenced <= MAX_REFERENCED_VALUES,
        S2KJ_CAPACITY_EXCEEDED,
        "candidate or value capacity differs",
    )
    _require(
        value.binding_digest == _digest(value.payload_without_digest()),
        S2KJ_DIGEST_MISMATCH,
        "validated finding digest differs",
    )
    return value


def _make_av_candidate(
    role: str,
    observation: read_only.S2JVB4ObservationV1 | read_only.S2JVFastObservationV1,
    auditory: tuple[float, ...],
    visual: tuple[float, ...],
    state_digest: str,
    probe_digest: str,
    source_digest: str,
) -> AVContextCandidate336V1:
    payload = {
        "role": role,
        "slot_id": observation.slot_id,
        "slot_digest": observation.entry_digest if role == "B4_RECENT" else observation.slot_digest,
        "auditory_values": list(auditory),
        "visual_values": list(visual),
        "auditory_values_digest": _digest(list(auditory)),
        "visual_values_digest": _digest(list(visual)),
        "av_values_digest": _digest(list(auditory + visual)),
        "formation_index": observation.formation_index if role == "B4_RECENT" else None,
        "support": observation.support if role == "TSPM_FAST" else None,
        "last_selected_step": observation.last_selected_step if role == "TSPM_FAST" else None,
        "auditory_distance": observation.auditory_distance,
        "visual_distance": observation.visual_distance,
        "mechanical_match": observation.mechanical_match,
        "observed_state_digest": state_digest,
        "probe_digest": probe_digest,
        "source_digest": source_digest,
    }
    result = AVContextCandidate336V1(**payload, candidate_digest=_digest(payload))
    _validate_candidate(result, role)
    return result


def _make_stable_candidate(
    role: str,
    observation: read_only.S2JVSlowObservationV1,
    values: tuple[float, ...],
    state_digest: str,
    probe_digest: str,
    source_digest: str,
) -> StableModalityCandidate336V1:
    modality = "AUDITORY" if role == "B_STABLE_AUDITORY" else "VISUAL"
    payload = {
        "role": role,
        "modality": modality,
        "dimension": len(values),
        "slot_id": observation.slot_id,
        "slot_digest": observation.slot_digest,
        "values": list(values),
        "values_digest": _digest(list(values)),
        "support": observation.support,
        "stable": observation.stable,
        "native_distance": observation.native_distance,
        "mechanical_match": observation.mechanical_match,
        "observed_state_digest": state_digest,
        "probe_digest": probe_digest,
        "source_digest": source_digest,
    }
    result = StableModalityCandidate336V1(**payload, candidate_digest=_digest(payload))
    _validate_candidate(result, role)
    return result


def _make_role_finding(
    role: str,
    candidate: Candidate336 | None,
    absence_reason: str | None,
    state_digest: str,
    probe_digest: str,
    source_finding_digest: str,
) -> RoleFinding336V1:
    payload = {
        "role": role,
        "status": "AVAILABLE" if candidate is not None else "ABSENT_VALID",
        "absence_reason": absence_reason,
        "candidate_digest": candidate.candidate_digest if candidate else None,
        "observed_state_digest": state_digest,
        "probe_digest": probe_digest,
        "source_finding_digest": source_finding_digest,
    }
    result = RoleFinding336V1(
        role,
        payload["status"],
        absence_reason,
        candidate,
        state_digest,
        probe_digest,
        source_finding_digest,
        _digest(payload),
    )
    _validate_role_finding(result, role)
    return result


def _absence_reason(occupied: int, stable: int, role: str) -> str:
    if occupied == 0:
        return "NO_OCCUPIED_SOURCE"
    if role.startswith("B_STABLE") and stable == 0:
        return "NO_STABLE_MATCH"
    return "NO_FUNCTIONAL_MATCH"


def bind_validated_perceptual_finding_336(
    *,
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    probe: coordinator.S2JVBoundProbeV1,
    finding: read_only.S2JVReadOnlyFindingV1,
) -> ValidatedPerceptualFinding336V1:
    """Bind candidate values to one already completed read-only probe."""

    try:
        config = coordinator._validate_config(config)
        state = coordinator._validate_state(config, state)
        probe = coordinator._validate_probe(config, probe)
    except Exception as exc:
        raise S2KJBindingError(S2KJ_BINDING_INVALID, "source validation failed") from exc
    _require(type(finding) is read_only.S2JVReadOnlyFindingV1, S2KJ_BINDING_INVALID, "exact source finding required")
    _require(
        finding.schema == read_only.S2JW_READ_SCHEMA
        and finding.roles
        == ("B4_RECENT", "TSPM_FAST", "TSPM_SLOW_AUDITORY", "TSPM_SLOW_VISUAL")
        and finding.config_digest == config.config_digest
        and finding.observed_state_digest == state.state_digest
        and finding.probe_digest == probe.probe_digest
        and finding.prestate_digest == state.state_digest == finding.poststate_digest
        and finding.finding_digest == read_only._digest(finding.payload_without_digest()),
        S2KJ_STATE_MISMATCH,
        "source finding does not bind this read-only state and probe",
    )
    try:
        validate_s2jv_resource_ledger(
            profile=config.profile,
            limits=config.ledger_limits,
            ledger=finding.ledger,
            expected_role="READ_ONLY",
        )
    except Exception as exc:
        raise S2KJBindingError(S2KJ_BINDING_INVALID, "source ledger differs") from exc

    expected_b4 = read_only._b4_observations(config, state, probe)
    expected_fast = read_only._fast_observations(config, state, probe)
    expected_auditory = read_only._slow_observations(
        modality="auditory",
        config=config.profile.profile.auditory_config,
        state=state.tspm_state.auditory_ppb1_state,
        probe_values=probe.auditory_values,
    )
    expected_visual = read_only._slow_observations(
        modality="visual",
        config=config.profile.profile.visual_config,
        state=state.tspm_state.visual_ppb1_state,
        probe_values=probe.visual_values,
    )
    _require(
        (finding.b4_observations, finding.b4_selected) == expected_b4
        and (finding.fast_observations, finding.fast_selected) == expected_fast
        and (finding.auditory_slow_observations, finding.auditory_slow_selected)
        == expected_auditory
        and (finding.visual_slow_observations, finding.visual_slow_selected)
        == expected_visual,
        S2KJ_BINDING_INVALID,
        "source observations differ from the bound state",
    )

    source_digest = probe.source.pairing_digest
    b4_candidate = None
    if finding.b4_selected is not None:
        entry = next(
            item for item in state.b4_state.entries if item.slot_id == finding.b4_selected.slot_id
        )
        values = _values(entry.values, config.av_dimension, "selected B4 values")
        b4_candidate = _make_av_candidate(
            "B4_RECENT",
            finding.b4_selected,
            values[: config.auditory_dimension],
            values[config.auditory_dimension :],
            state.state_digest,
            probe.probe_digest,
            source_digest,
        )
    fast_candidate = None
    if finding.fast_selected is not None:
        slot = next(
            item
            for item in state.tspm_state.fast_state.slots
            if item.slot_id == finding.fast_selected.slot_id
        )
        fast_candidate = _make_av_candidate(
            "TSPM_FAST",
            finding.fast_selected,
            _values(slot.auditory_values, config.auditory_dimension, "selected Fast auditory values"),
            _values(slot.visual_values, config.visual_dimension, "selected Fast visual values"),
            state.state_digest,
            probe.probe_digest,
            source_digest,
        )

    slow_candidates: list[StableModalityCandidate336V1 | None] = []
    for role, selected, bank, dimension in (
        (
            "B_STABLE_AUDITORY",
            finding.auditory_slow_selected,
            state.tspm_state.auditory_ppb1_state,
            config.auditory_dimension,
        ),
        (
            "B_STABLE_VISUAL",
            finding.visual_slow_selected,
            state.tspm_state.visual_ppb1_state,
            config.visual_dimension,
        ),
    ):
        if selected is None:
            slow_candidates.append(None)
            continue
        slot = next(item for item in bank.slots if item.slot_id == selected.slot_id)
        slow_candidates.append(
            _make_stable_candidate(
                role,
                selected,
                _values(slot.prototype_values, dimension, f"selected {role} values"),
                state.state_digest,
                probe.probe_digest,
                source_digest,
            )
        )

    selected_candidates: tuple[Candidate336 | None, ...] = (
        b4_candidate,
        fast_candidate,
        slow_candidates[0],
        slow_candidates[1],
    )
    observation_groups = (
        finding.b4_observations,
        finding.fast_observations,
        finding.auditory_slow_observations,
        finding.visual_slow_observations,
    )
    role_findings = tuple(
        _make_role_finding(
            role,
            candidate,
            None
            if candidate is not None
            else _absence_reason(
                len(observations),
                sum(getattr(item, "stable", False) is True for item in observations),
                role,
            ),
            state.state_digest,
            probe.probe_digest,
            finding.finding_digest,
        )
        for role, candidate, observations in zip(
            ROLE_ORDER, selected_candidates, observation_groups, strict=True
        )
    )
    auditory_source_digest = probe.source.auditory.timed_frame_provenance_digest
    visual_source_digest = probe.source.visual.timed_frame_provenance_digest
    source_time_geometry_digest = _digest(
        {
            "source_digest": source_digest,
            "auditory_source_digest": auditory_source_digest,
            "visual_source_digest": visual_source_digest,
            "auditory_geometry_id": config.profile.profile.auditory_config.geometry_id,
            "visual_geometry_id": config.profile.profile.visual_config.geometry_id,
            "common_field_clock_id": probe.source.plan.common_field_clock_id,
            "overlap_start_tick": probe.source.plan.overlap_start_tick,
            "overlap_end_tick": probe.source.plan.overlap_end_tick,
        }
    )
    candidate_count = sum(item is not None for item in selected_candidates)
    referenced_value_count = sum(
        336 if type(item) is AVContextCandidate336V1 else item.dimension
        for item in selected_candidates
        if item is not None
    )
    payload = {
        "schema": S2KJ_BINDING_SCHEMA,
        "config_digest": config.config_digest,
        "composite_state_digest": state.state_digest,
        "probe_digest": probe.probe_digest,
        "source_digest": source_digest,
        "auditory_source_digest": auditory_source_digest,
        "visual_source_digest": visual_source_digest,
        "source_time_geometry_digest": source_time_geometry_digest,
        "source_finding_digest": finding.finding_digest,
        "role_finding_digests": [item.finding_digest for item in role_findings],
        "prestate_digest": finding.prestate_digest,
        "poststate_digest": finding.poststate_digest,
        "source_ledger_digest": finding.ledger.ledger_digest,
        "candidate_count": candidate_count,
        "referenced_value_count": referenced_value_count,
    }
    result = ValidatedPerceptualFinding336V1(
        config.config_digest,
        state.state_digest,
        probe.probe_digest,
        source_digest,
        auditory_source_digest,
        visual_source_digest,
        source_time_geometry_digest,
        finding.finding_digest,
        role_findings,
        finding.prestate_digest,
        finding.poststate_digest,
        finding.ledger.ledger_digest,
        candidate_count,
        referenced_value_count,
        _digest(payload),
    )
    _require(state.state_digest == finding.poststate_digest, S2KJ_STATE_MISMATCH, "binding changed state")
    return _validate_validated_finding(result)


__all__ = ()
