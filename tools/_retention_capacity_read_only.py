"""Private read-only content inspection for B4 and TSPM-1 states.

No function in this module advances a bank. TSPM-1 inspection performs exactly
one native read-only probe and derives the remaining evidence from that probe's
already validated source state.
"""

from __future__ import annotations

from dataclasses import dataclass
import math

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from mcm_field_organism._ppb1_reference import (
    PPB1BankConfig,
    PPB1BankState,
    _digest as ppb_digest,
    normalized_mean_l1_distance,
)

from tools._retention_capacity_fixtures import (
    FUNCTIONAL_AUDITORY_THRESHOLD,
    FUNCTIONAL_VISUAL_THRESHOLD,
)


ADAPTER_SCHEMA = "retention.capacity.private.read-only.v1"
AUDITORY_DIMENSION = 8
VISUAL_DIMENSION = 18
AV_DIMENSION = AUDITORY_DIMENSION + VISUAL_DIMENSION


class RetentionReadOnlyError(ValueError):
    """One fail-closed private inspection boundary violation."""


@dataclass(frozen=True, slots=True)
class B4SlotObservation:
    slot_id: str
    formation_index: int
    values: tuple[float, ...]
    auditory_distance: float
    visual_distance: float
    functional_match: bool


@dataclass(frozen=True, slots=True)
class B4ContentFinding:
    observed_state_digest: str
    probe_values_digest: str
    occupied_slot_count: int
    candidates: tuple[B4SlotObservation, ...]
    recognized: bool
    selected: B4SlotObservation | None
    functional_auditory_threshold_numerator: int
    functional_auditory_threshold_denominator: int
    functional_visual_threshold_numerator: int
    functional_visual_threshold_denominator: int
    prestate_digest: str
    poststate_digest: str


@dataclass(frozen=True, slots=True)
class FastSlotObservation:
    slot_id: str
    slot_digest: str
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    support_count: int
    last_selected_step: int
    consolidation_count: int
    auditory_distance: float
    visual_distance: float
    native_match: bool
    functional_match: bool


@dataclass(frozen=True, slots=True)
class SlowSlotObservation:
    slot_id: str
    slot_digest: str
    prototype_values: tuple[float, ...]
    support_count: int
    last_selected_step: int
    stable: bool
    native_distance: float


@dataclass(frozen=True, slots=True)
class SlowBankFinding:
    modality_id: str
    bank_id: str
    observed_bank_state_digest: str
    accepted_step_count: int
    occupied_slot_count: int
    eligible_slot_count: int
    native_status: str
    native_finding_digest: str | None
    native_match_threshold: float
    functional_match_threshold_numerator: int
    functional_match_threshold_denominator: int
    slots: tuple[SlowSlotObservation, ...]
    selected: SlowSlotObservation | None
    native_recognized: bool
    functional_recognized: bool


@dataclass(frozen=True, slots=True)
class TSPM1ContentFinding:
    observed_composite_state_digest: str
    probe_digest: str
    native_finding_digest: str
    native_context_source: str
    fast_slots: tuple[FastSlotObservation, ...]
    native_fast_recognized: bool
    native_fast_selected: FastSlotObservation | None
    functional_fast_recognized: bool
    functional_fast_selected: FastSlotObservation | None
    auditory_slow: SlowBankFinding
    visual_slow: SlowBankFinding
    functional_slow_recognized: bool
    functional_context_source: str
    functional_auditory_threshold_numerator: int
    functional_auditory_threshold_denominator: int
    functional_visual_threshold_numerator: int
    functional_visual_threshold_denominator: int
    prestate_component_digests: tuple[str, str, str, str]
    poststate_component_digests: tuple[str, str, str, str]
    prestate_digest: str
    poststate_digest: str


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RetentionReadOnlyError(message)


def _values(values: object, length: int, role: str) -> tuple[float, ...]:
    try:
        normalized = tuple(float(value) for value in values)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise RetentionReadOnlyError(f"{role} must be numeric") from exc
    _require(len(normalized) == length, f"{role} dimension differs")
    _require(
        all(math.isfinite(value) and -1.0 <= value <= 1.0 for value in normalized),
        f"{role} values are not finite and bounded",
    )
    return normalized


def _split(values: tuple[float, ...]) -> tuple[tuple[float, ...], tuple[float, ...]]:
    _require(len(values) == AV_DIMENSION, "AV value dimension differs")
    return values[:AUDITORY_DIMENSION], values[AUDITORY_DIMENSION:]


def _functional_match(auditory_distance: float, visual_distance: float) -> bool:
    return (
        auditory_distance <= float(FUNCTIONAL_AUDITORY_THRESHOLD)
        and visual_distance <= float(FUNCTIONAL_VISUAL_THRESHOLD)
    )


def _b4_state_digest(state: comparison._B4State) -> str:
    return comparison._digest(comparison._canonical(state))


def _validate_b4_state(state: object) -> comparison._B4State:
    _require(type(state) is comparison._B4State, "exact private B4 state required")
    _require(
        not isinstance(state.accepted_count, bool)
        and isinstance(state.accepted_count, int)
        and state.accepted_count >= 0,
        "B4 accepted count is invalid",
    )
    _require(len(state.entries) == 9, "B4 capacity differs")
    _require(
        all(type(entry) is comparison._FIFOEntry for entry in state.entries),
        "exact private B4 entries required",
    )
    expected_ids = tuple(f"b4.slot.{index:03d}" for index in range(9))
    _require(tuple(entry.slot_id for entry in state.entries) == expected_ids, "B4 slot identity differs")
    formation_indexes = []
    for entry in state.entries:
        if entry.occupied:
            _values(entry.values, AV_DIMENSION, "B4 stored values")
            _require(
                not isinstance(entry.formation_index, bool)
                and isinstance(entry.formation_index, int)
                and 1 <= entry.formation_index <= state.accepted_count,
                "occupied B4 entry has invalid formation index",
            )
            formation_indexes.append(entry.formation_index)
        else:
            _require(
                entry.values == () and entry.formation_index is None,
                "free B4 entry carries state",
            )
    _require(len(formation_indexes) == len(set(formation_indexes)), "B4 formation index is ambiguous")
    return state


def probe_b4_content_read_only(
    state: comparison._B4State,
    probe_values: tuple[float, ...],
) -> B4ContentFinding:
    """Inspect current B4 entries without advancing or rewriting the bank."""

    state = _validate_b4_state(state)
    probe = _values(probe_values, AV_DIMENSION, "B4 probe")
    probe_auditory, probe_visual = _split(probe)
    before = _b4_state_digest(state)
    candidates = []
    for entry in state.entries:
        if not entry.occupied:
            continue
        assert entry.formation_index is not None
        stored = _values(entry.values, AV_DIMENSION, "B4 stored values")
        stored_auditory, stored_visual = _split(stored)
        auditory_distance = normalized_mean_l1_distance(probe_auditory, stored_auditory)
        visual_distance = normalized_mean_l1_distance(probe_visual, stored_visual)
        candidates.append(
            B4SlotObservation(
                entry.slot_id,
                entry.formation_index,
                stored,
                auditory_distance,
                visual_distance,
                _functional_match(auditory_distance, visual_distance),
            )
        )
    candidates_tuple = tuple(sorted(candidates, key=lambda item: item.slot_id))
    matching = tuple(item for item in candidates_tuple if item.functional_match)
    selected = min(
        matching,
        key=lambda item: (
            max(item.auditory_distance, item.visual_distance),
            item.auditory_distance + item.visual_distance,
            -item.formation_index,
            item.slot_id,
        ),
        default=None,
    )
    after = _b4_state_digest(state)
    _require(before == after, "B4 read-only inspection changed state")
    return B4ContentFinding(
        before,
        comparison._digest(probe),
        len(candidates_tuple),
        candidates_tuple,
        selected is not None,
        selected,
        FUNCTIONAL_AUDITORY_THRESHOLD.numerator,
        FUNCTIONAL_AUDITORY_THRESHOLD.denominator,
        FUNCTIONAL_VISUAL_THRESHOLD.numerator,
        FUNCTIONAL_VISUAL_THRESHOLD.denominator,
        before,
        after,
    )


def _fast_observations(
    config: tspm1.TSPM1ConfigBinding,
    state: tspm1.TSPM1CompositeState,
    auditory_values: tuple[float, ...],
    visual_values: tuple[float, ...],
) -> tuple[FastSlotObservation, ...]:
    observations = []
    for slot in state.fast_state.slots:
        if not slot.occupied:
            continue
        stored_auditory = _values(slot.auditory_values, AUDITORY_DIMENSION, "Fast auditory values")
        stored_visual = _values(slot.visual_values, VISUAL_DIMENSION, "Fast visual values")
        _require(
            slot.support_count is not None and slot.last_selected_step is not None,
            "occupied Fast slot lacks lifecycle state",
        )
        auditory_distance = normalized_mean_l1_distance(auditory_values, stored_auditory)
        visual_distance = normalized_mean_l1_distance(visual_values, stored_visual)
        observations.append(
            FastSlotObservation(
                slot.slot_id,
                slot.digest(),
                stored_auditory,
                stored_visual,
                slot.support_count,
                slot.last_selected_step,
                slot.consolidation_count,
                auditory_distance,
                visual_distance,
                auditory_distance <= config.fast_config.auditory_match_threshold
                and visual_distance <= config.fast_config.visual_match_threshold,
                _functional_match(auditory_distance, visual_distance),
            )
        )
    return tuple(sorted(observations, key=lambda item: item.slot_id))


def _rank_fast(slots: tuple[FastSlotObservation, ...], *, functional: bool) -> FastSlotObservation | None:
    matching = (
        tuple(slot for slot in slots if slot.functional_match)
        if functional
        else tuple(slot for slot in slots if slot.native_match)
    )
    return min(
        matching,
        key=lambda item: (
            max(item.auditory_distance, item.visual_distance),
            item.auditory_distance + item.visual_distance,
            item.slot_id,
        ),
        default=None,
    )


def _inspect_slow_bank(
    config: PPB1BankConfig,
    state: PPB1BankState,
    probe_values: tuple[float, ...],
    native_status: str,
    native_finding_digest: str | None,
) -> SlowBankFinding:
    functional_threshold = (
        FUNCTIONAL_AUDITORY_THRESHOLD
        if config.modality_id == "auditory"
        else FUNCTIONAL_VISUAL_THRESHOLD
    )
    slots = []
    for slot in state.slots:
        if not slot.occupied:
            continue
        _require(
            slot.support_count is not None and slot.last_selected_step is not None,
            "occupied Slow slot lacks lifecycle state",
        )
        prototype = _values(slot.prototype_values, len(probe_values), "Slow prototype")
        slots.append(
            SlowSlotObservation(
                slot.slot_id,
                ppb_digest(slot.canonical_payload()),
                prototype,
                slot.support_count,
                slot.last_selected_step,
                slot.support_count >= config.stable_after,
                normalized_mean_l1_distance(probe_values, prototype),
            )
        )
    slots_tuple = tuple(sorted(slots, key=lambda item: item.slot_id))
    eligible = tuple(slot for slot in slots_tuple if slot.stable)
    selected = min(eligible, key=lambda item: (item.native_distance, item.slot_id), default=None)
    native_recognized = selected is not None and selected.native_distance <= config.match_threshold
    functional_recognized = (
        selected is not None and selected.native_distance <= float(functional_threshold)
    )
    if state.accepted_step_count == 0:
        expected_status = "SLOW_UNAVAILABLE"
        _require(native_finding_digest is None, "unavailable Slow result carries a finding digest")
    else:
        expected_status = "SLOW_RECOGNIZED" if native_recognized else "SLOW_NOT_RECOGNIZED"
        _require(
            isinstance(native_finding_digest, str) and len(native_finding_digest) == 64,
            "queried Slow result lacks its native finding digest",
        )
    _require(native_status == expected_status, "native Slow status differs from validated state")
    return SlowBankFinding(
        config.modality_id,
        config.bank_id,
        state.digest(),
        state.accepted_step_count,
        len(slots_tuple),
        len(eligible),
        native_status,
        native_finding_digest,
        config.match_threshold,
        functional_threshold.numerator,
        functional_threshold.denominator,
        slots_tuple,
        selected,
        native_recognized,
        functional_recognized,
    )


def _tspm_state_digest_tuple(state: tspm1.TSPM1CompositeState) -> tuple[str, str, str, str]:
    return (
        state.fast_state.fast_state_digest,
        state.auditory_ppb1_state.digest(),
        state.visual_ppb1_state.digest(),
        state.composite_state_digest,
    )


def probe_tspm1_content_read_only(
    config: tspm1.TSPM1ConfigBinding,
    state: tspm1.TSPM1CompositeState,
    probe: tspm1.TSPM1BoundProbe,
) -> TSPM1ContentFinding:
    """Run exactly one native TSPM-1 probe and inspect its unchanged state."""

    _require(type(config) is tspm1.TSPM1ConfigBinding, "exact TSPM-1 config required")
    _require(type(state) is tspm1.TSPM1CompositeState, "exact TSPM-1 state required")
    _require(type(probe) is tspm1.TSPM1BoundProbe, "exact TSPM-1 bound probe required")
    before = _tspm_state_digest_tuple(state)

    native = tspm1.probe_tspm1_read_only(config, state, probe)

    after = _tspm_state_digest_tuple(state)
    _require(before == after, "TSPM-1 native probe changed source state")
    auditory_values = _values(
        probe.auditory.timed_frame.frame.values,
        AUDITORY_DIMENSION,
        "TSPM-1 auditory probe",
    )
    visual_values = _values(
        probe.visual.timed_frame.frame.values,
        VISUAL_DIMENSION,
        "TSPM-1 visual probe",
    )
    fast_slots = _fast_observations(config, state, auditory_values, visual_values)
    native_fast = _rank_fast(fast_slots, functional=False)
    functional_fast = _rank_fast(fast_slots, functional=True)
    _require(
        native.fast_recognized == (native_fast is not None),
        "native Fast decision differs from validated state",
    )
    if native_fast is not None:
        _require(
            native.fast_slot_id == native_fast.slot_id
            and native.fast_slot_digest == native_fast.slot_digest
            and native.auditory_fast_distance == native_fast.auditory_distance
            and native.visual_fast_distance == native_fast.visual_distance,
            "native Fast selection differs from validated state",
        )
    auditory_slow = _inspect_slow_bank(
        config.profile.auditory_config,
        state.auditory_ppb1_state,
        auditory_values,
        native.auditory_slow_status,
        native.auditory_s1wu_finding_digest,
    )
    visual_slow = _inspect_slow_bank(
        config.profile.visual_config,
        state.visual_ppb1_state,
        visual_values,
        native.visual_slow_status,
        native.visual_s1wu_finding_digest,
    )
    functional_slow = auditory_slow.functional_recognized and visual_slow.functional_recognized
    if functional_slow:
        functional_source = "SLOW_PPB1_CONTEXT"
    elif functional_fast is not None:
        functional_source = "FAST_ASSOCIATIVE_CONTEXT"
    else:
        functional_source = "NO_COMPLETE_CONTEXT"
    return TSPM1ContentFinding(
        state.composite_state_digest,
        probe.probe_digest,
        native.finding_digest,
        native.context_source,
        fast_slots,
        native.fast_recognized,
        native_fast,
        functional_fast is not None,
        functional_fast,
        auditory_slow,
        visual_slow,
        functional_slow,
        functional_source,
        FUNCTIONAL_AUDITORY_THRESHOLD.numerator,
        FUNCTIONAL_AUDITORY_THRESHOLD.denominator,
        FUNCTIONAL_VISUAL_THRESHOLD.numerator,
        FUNCTIONAL_VISUAL_THRESHOLD.denominator,
        before,
        after,
        before[-1],
        after[-1],
    )
