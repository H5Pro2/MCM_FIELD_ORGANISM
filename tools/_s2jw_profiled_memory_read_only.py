"""Read-only B4/Fast/Slow findings for the profile-derived S2-JW state."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism._ppb1_reference import normalized_mean_l1_distance
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools._s2jw_profiled_memory_ledger import (
    S2JVResourceLedgerV1,
    derive_s2jv_resource_ledger,
    validate_s2jv_resource_ledger,
)


S2JW_READ_SCHEMA = "s2jw.profiled-memory-read-only.v1"


class S2JWReadOnlyError(ValueError):
    """A read-only source or relation is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2JWReadOnlyError(message)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _values(values: object, length: int, role: str) -> tuple[float, ...]:
    _require(type(values) is tuple and len(values) == length, f"{role} dimension differs")
    _require(
        all(type(value) in (int, float) for value in values),
        f"{role} contains a nonnumeric or boolean value",
    )
    result = tuple(float(value) for value in values)
    _require(
        all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in result),
        f"{role} values differ from receptor domain",
    )
    return result


@dataclass(frozen=True, slots=True)
class S2JVB4ObservationV1:
    slot_id: str
    formation_index: int
    auditory_distance: float
    visual_distance: float
    mechanical_match: bool
    entry_digest: str


@dataclass(frozen=True, slots=True)
class S2JVFastObservationV1:
    slot_id: str
    support: int
    last_selected_step: int
    auditory_distance: float
    visual_distance: float
    mechanical_match: bool
    slot_digest: str


@dataclass(frozen=True, slots=True)
class S2JVSlowObservationV1:
    modality_id: str
    slot_id: str
    support: int
    stable: bool
    native_distance: float
    mechanical_match: bool
    slot_digest: str


@dataclass(frozen=True, slots=True)
class S2JVReadOnlyFindingV1:
    config_digest: str
    observed_state_digest: str
    probe_digest: str
    roles: tuple[str, str, str, str]
    b4_observations: tuple[S2JVB4ObservationV1, ...]
    b4_selected: S2JVB4ObservationV1 | None
    fast_observations: tuple[S2JVFastObservationV1, ...]
    fast_selected: S2JVFastObservationV1 | None
    auditory_slow_observations: tuple[S2JVSlowObservationV1, ...]
    visual_slow_observations: tuple[S2JVSlowObservationV1, ...]
    auditory_slow_selected: S2JVSlowObservationV1 | None
    visual_slow_selected: S2JVSlowObservationV1 | None
    native_tspm_finding_digest: str
    prestate_digest: str
    poststate_digest: str
    ledger: S2JVResourceLedgerV1
    finding_digest: str
    schema: str = S2JW_READ_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        def observation_payload(value: object) -> dict[str, object]:
            return {
                name: getattr(value, name)
                for name in value.__dataclass_fields__  # type: ignore[attr-defined]
            }

        return {
            "schema": self.schema,
            "config_digest": self.config_digest,
            "observed_state_digest": self.observed_state_digest,
            "probe_digest": self.probe_digest,
            "roles": list(self.roles),
            "b4_observations": [observation_payload(item) for item in self.b4_observations],
            "b4_selected_digest": self.b4_selected.entry_digest if self.b4_selected else None,
            "fast_observations": [observation_payload(item) for item in self.fast_observations],
            "fast_selected_digest": self.fast_selected.slot_digest if self.fast_selected else None,
            "auditory_slow_observations": [
                observation_payload(item) for item in self.auditory_slow_observations
            ],
            "visual_slow_observations": [
                observation_payload(item) for item in self.visual_slow_observations
            ],
            "auditory_slow_selected_digest": (
                self.auditory_slow_selected.slot_digest
                if self.auditory_slow_selected
                else None
            ),
            "visual_slow_selected_digest": (
                self.visual_slow_selected.slot_digest if self.visual_slow_selected else None
            ),
            "native_tspm_finding_digest": self.native_tspm_finding_digest,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "ledger_digest": self.ledger.ledger_digest,
        }


def _b4_observations(
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    probe: coordinator.S2JVBoundProbeV1,
) -> tuple[tuple[S2JVB4ObservationV1, ...], S2JVB4ObservationV1 | None]:
    result = []
    for entry in state.b4_state.entries:
        if not entry.occupied:
            continue
        assert entry.formation_index is not None
        values = _values(entry.values, config.av_dimension, "B4 values")
        auditory = values[: config.auditory_dimension]
        visual = values[config.auditory_dimension :]
        auditory_distance = normalized_mean_l1_distance(probe.auditory_values, auditory)
        visual_distance = normalized_mean_l1_distance(probe.visual_values, visual)
        result.append(
            S2JVB4ObservationV1(
                entry.slot_id,
                entry.formation_index,
                auditory_distance,
                visual_distance,
                auditory_distance <= config.tspm_config.fast_config.auditory_match_threshold
                and visual_distance <= config.tspm_config.fast_config.visual_match_threshold,
                _digest(
                    {
                        "slot_id": entry.slot_id,
                        "formation_index": entry.formation_index,
                        "values_digest": _digest(list(values)),
                    }
                ),
            )
        )
    observations = tuple(sorted(result, key=lambda item: item.slot_id))
    selected = min(
        (item for item in observations if item.mechanical_match),
        key=lambda item: (
            max(item.auditory_distance, item.visual_distance),
            item.auditory_distance + item.visual_distance,
            -item.formation_index,
            item.slot_id,
        ),
        default=None,
    )
    return observations, selected


def _fast_observations(
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    probe: coordinator.S2JVBoundProbeV1,
) -> tuple[tuple[S2JVFastObservationV1, ...], S2JVFastObservationV1 | None]:
    result = []
    for slot in state.tspm_state.fast_state.slots:
        if not slot.occupied:
            continue
        auditory = _values(slot.auditory_values, config.auditory_dimension, "Fast auditory")
        visual = _values(slot.visual_values, config.visual_dimension, "Fast visual")
        assert slot.support_count is not None and slot.last_selected_step is not None
        auditory_distance = normalized_mean_l1_distance(probe.auditory_values, auditory)
        visual_distance = normalized_mean_l1_distance(probe.visual_values, visual)
        result.append(
            S2JVFastObservationV1(
                slot.slot_id,
                slot.support_count,
                slot.last_selected_step,
                auditory_distance,
                visual_distance,
                auditory_distance <= config.tspm_config.fast_config.auditory_match_threshold
                and visual_distance <= config.tspm_config.fast_config.visual_match_threshold,
                slot.digest(),
            )
        )
    observations = tuple(sorted(result, key=lambda item: item.slot_id))
    selected = min(
        (item for item in observations if item.mechanical_match),
        key=lambda item: (
            max(item.auditory_distance, item.visual_distance),
            item.auditory_distance + item.visual_distance,
            item.slot_id,
        ),
        default=None,
    )
    return observations, selected


def _slow_observations(
    *,
    modality: str,
    config: object,
    state: object,
    probe_values: tuple[float, ...],
) -> tuple[tuple[S2JVSlowObservationV1, ...], S2JVSlowObservationV1 | None]:
    result = []
    for slot in state.slots:  # type: ignore[attr-defined]
        if not slot.occupied:
            continue
        assert slot.support_count is not None
        prototype = _values(slot.prototype_values, len(probe_values), f"{modality} Slow")
        distance = normalized_mean_l1_distance(probe_values, prototype)
        stable = slot.support_count >= config.stable_after  # type: ignore[attr-defined]
        result.append(
            S2JVSlowObservationV1(
                modality,
                slot.slot_id,
                slot.support_count,
                stable,
                distance,
                stable and distance <= config.match_threshold,  # type: ignore[attr-defined]
                _digest(slot.canonical_payload()),
            )
        )
    observations = tuple(sorted(result, key=lambda item: item.slot_id))
    selected = min(
        (item for item in observations if item.mechanical_match),
        key=lambda item: (item.native_distance, item.slot_id),
        default=None,
    )
    return observations, selected


def probe_s2jv_composite_read_only(
    *,
    config: coordinator.S2JVCoordinatorConfigV1,
    state: coordinator.S2JVCompositeStateV1,
    probe: coordinator.S2JVBoundProbeV1,
) -> S2JVReadOnlyFindingV1:
    config = coordinator._validate_config(config)
    state = coordinator._validate_state(config, state)
    probe = coordinator._validate_probe(config, probe)
    tspm1._validate_bound_source_time(
        state.tspm_state.fast_state,
        probe.tspm_probe,
        strictly_later=True,
    )
    before = state.state_digest
    native = tspm1.probe_tspm1_read_only(config.tspm_config, state.tspm_state, probe.tspm_probe)
    b4_observations, b4_selected = _b4_observations(config, state, probe)
    fast_observations, fast_selected = _fast_observations(config, state, probe)
    auditory_slow, auditory_selected = _slow_observations(
        modality="auditory",
        config=config.profile.profile.auditory_config,
        state=state.tspm_state.auditory_ppb1_state,
        probe_values=probe.auditory_values,
    )
    visual_slow, visual_selected = _slow_observations(
        modality="visual",
        config=config.profile.profile.visual_config,
        state=state.tspm_state.visual_ppb1_state,
        probe_values=probe.visual_values,
    )
    _require(
        native.fast_recognized == (fast_selected is not None),
        "native Fast result differs from validated state",
    )
    expected_auditory_status = (
        "SLOW_UNAVAILABLE"
        if state.tspm_state.auditory_ppb1_state.accepted_step_count == 0
        else "SLOW_RECOGNIZED" if auditory_selected else "SLOW_NOT_RECOGNIZED"
    )
    expected_visual_status = (
        "SLOW_UNAVAILABLE"
        if state.tspm_state.visual_ppb1_state.accepted_step_count == 0
        else "SLOW_RECOGNIZED" if visual_selected else "SLOW_NOT_RECOGNIZED"
    )
    _require(
        native.auditory_slow_status == expected_auditory_status
        and native.visual_slow_status == expected_visual_status,
        "native Slow result differs from validated state",
    )
    after = state.state_digest
    _require(before == after, "read-only inspection changed composite state")
    core_payload = {
        "schema": S2JW_READ_SCHEMA,
        "config_digest": config.config_digest,
        "observed_state_digest": before,
        "probe_digest": probe.probe_digest,
        "native_tspm_finding_digest": native.finding_digest,
        "b4_selected_digest": b4_selected.entry_digest if b4_selected else None,
        "fast_selected_digest": fast_selected.slot_digest if fast_selected else None,
        "auditory_slow_selected_digest": auditory_selected.slot_digest if auditory_selected else None,
        "visual_slow_selected_digest": visual_selected.slot_digest if visual_selected else None,
        "prestate_digest": before,
        "poststate_digest": after,
    }
    core_digest = _digest(core_payload)
    ledger = derive_s2jv_resource_ledger(
        profile=config.profile,
        limits=config.ledger_limits,
        operation_id=f"probe-{probe.probe_digest[:24]}",
        operation_role="READ_ONLY",
        result_digest=core_digest,
    )
    validate_s2jv_resource_ledger(
        profile=config.profile,
        limits=config.ledger_limits,
        ledger=ledger,
        expected_role="READ_ONLY",
    )
    finding = S2JVReadOnlyFindingV1(
        config.config_digest,
        before,
        probe.probe_digest,
        ("B4_RECENT", "TSPM_FAST", "TSPM_SLOW_AUDITORY", "TSPM_SLOW_VISUAL"),
        b4_observations,
        b4_selected,
        fast_observations,
        fast_selected,
        auditory_slow,
        visual_slow,
        auditory_selected,
        visual_selected,
        native.finding_digest,
        before,
        after,
        ledger,
        "",
    )
    object.__setattr__(finding, "finding_digest", _digest(finding.payload_without_digest()))
    _require(
        finding.finding_digest == _digest(finding.payload_without_digest())
        and finding.prestate_digest == finding.poststate_digest,
        "read-only finding relation differs",
    )
    return finding
