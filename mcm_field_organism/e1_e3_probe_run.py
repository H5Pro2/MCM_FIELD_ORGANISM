"""Pre-registered E1 E3 identical-probe composition."""

from __future__ import annotations

import copy
from dataclasses import dataclass, fields
import math

import numpy as np

from .e1_e3_state_arms import (
    E1E3StateArmsError,
    E1E3StateArmsResult,
    build_e1_e3_state_arms,
    evaluate_e1_e3_state_arms,
)
from .e1_frozen_history_probe import (
    FrozenE1ProbeError,
    FrozenE1ProbeResult,
    advance_fixed_e1_adapter_probe,
    advance_frozen_e1_probe,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_mirrored_history import E1MirroredHistoryError, produce_e1_mirrored_histories
from .field_step_time import MCMFieldStepTime
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import DistributedReceptorContact, ReceptorDistribution
from .shared_mcm_field import SharedMCMField


class E1E3ProbeRunError(ValueError):
    """Raised when the pre-registered E3 probe run is incomplete."""


E1_E3_PROBE_ABSOLUTE_TOLERANCE = 1e-12
_PREPARATION_CONTACT = (0.30, -0.20, 0.60)
_PROBE_CONTACT = (0.75, -0.25, 0.25)
_TICKS_PER_SECOND = 20.0


def _nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise E1E3ProbeRunError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise E1E3ProbeRunError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise E1E3ProbeRunError(f"{role} must be finite and nonnegative")
    return result


@dataclass(frozen=True, slots=True)
class E1E3ProbeMetrics:
    """Raw E3 probe distances without an embedded interpretation."""

    pre_probe_s_linf: float
    pre_probe_h_linf: float
    ablation_p0_s_linf: float
    ablation_p0_h_linf: float
    fixed_gain_s_linf: float
    fixed_gain_h_linf: float
    refinement_s_linf: float
    refinement_h_linf: float
    hold_p0_s_linf: float
    hold_p0_h_linf: float
    release_p0_s_linf: float
    release_p0_h_linf: float
    compete_p0_s_linf: float
    compete_p0_h_linf: float
    release_hold_s_linf: float
    release_hold_h_linf: float
    compete_release_s_linf: float
    compete_release_h_linf: float
    compete_hold_s_linf: float
    compete_hold_h_linf: float

    def __post_init__(self) -> None:
        for item in fields(self):
            object.__setattr__(
                self, item.name, _nonnegative(getattr(self, item.name), item.name)
            )


@dataclass(frozen=True, slots=True)
class E1E3ProbeRunResult:
    """Complete E3 state and probe data without an embedded decision."""

    state_arms: E1E3StateArmsResult
    pre_probe_snapshot_digest: str
    p0_field: SharedMCMField
    hold_ablated_field: SharedMCMField
    release_ablated_field: SharedMCMField
    compete_ablated_field: SharedMCMField
    hold_active_field: SharedMCMField
    release_active_field: SharedMCMField
    compete_active_field: SharedMCMField
    hold_fixed_gain_field: SharedMCMField
    release_fixed_gain_field: SharedMCMField
    compete_fixed_gain_field: SharedMCMField
    hold_n2_field: SharedMCMField
    hold_n4_field: SharedMCMField
    release_n2_field: SharedMCMField
    release_n4_field: SharedMCMField
    compete_n2_field: SharedMCMField
    compete_n4_field: SharedMCMField
    metrics: E1E3ProbeMetrics

    def __post_init__(self) -> None:
        if not isinstance(self.state_arms, E1E3StateArmsResult):
            raise E1E3ProbeRunError("E3 probe result requires state arms")
        if (
            not isinstance(self.pre_probe_snapshot_digest, str)
            or len(self.pre_probe_snapshot_digest) != 64
        ):
            raise E1E3ProbeRunError("E3 probe result requires one snapshot digest")
        for item in fields(self):
            if item.name.endswith("_field") and not isinstance(
                getattr(self, item.name), SharedMCMField
            ):
                raise E1E3ProbeRunError(f"{item.name} must be one completed field")
        if not isinstance(self.metrics, E1E3ProbeMetrics):
            raise E1E3ProbeRunError("E3 probe result requires raw metrics")


def _position_ids(field: SharedMCMField) -> tuple[str, ...]:
    ordered = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if len(ordered) != 3 or len(field.docks) != 1:
        raise E1E3ProbeRunError("E3 probe requires one dock and three neurons")
    return tuple(item.neuron_id for item in ordered)


def _distribution(
    field: SharedMCMField,
    position_ids: tuple[str, ...],
    values: tuple[float, ...],
    snapshot_id: str,
    start_tick: int,
    end_tick: int,
) -> tuple[ReceptorDistribution, MCMFieldStepTime]:
    dock = field.docks[0]
    value_by_neuron = dict(zip(position_ids, values, strict=True))
    neuron_by_carrier = dict(dock.dock_map.pairs)
    frame = ReceptorContactFrame(
        modality_id=dock.dock_map.modality_id,
        geometry_id=dock.dock_map.receptor_geometry_id,
        snapshot_id=snapshot_id,
        clock_id="e1.e3.probe.source",
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=dock.dock_map.carrier_ids,
        values=tuple(
            value_by_neuron[neuron_by_carrier[carrier_id]]
            for carrier_id in dock.dock_map.carrier_ids
        ),
    )
    return (
        ReceptorDistribution(
            CommonFieldTime("e1.e3.probe.organism", start_tick, end_tick),
            (DistributedReceptorContact(dock.dock_id, frame),),
        ),
        MCMFieldStepTime(
            "e1.e3.probe.organism", start_tick, end_tick, _TICKS_PER_SECOND
        ),
    )


def _values(field: SharedMCMField, role: str) -> np.ndarray:
    return np.asarray(
        [
            getattr(neuron, role)
            for neuron in sorted(field.layer.neurons, key=lambda item: item.position)
        ],
        dtype=np.float64,
    )


def _linf(first: SharedMCMField, second: SharedMCMField, role: str) -> float:
    return float(np.max(np.abs(_values(first, role) - _values(second, role))))


def _run_fixed_partition(
    initial_field: SharedMCMField,
    fixed_adapter,
    position_ids: tuple[str, ...],
    parts: int,
    arm: str,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None,
) -> SharedMCMField:
    field = copy.deepcopy(initial_field)
    width = 20 // parts
    for index in range(parts):
        start = 20 + index * width
        end = start + width
        distribution, interval = _distribution(
            field,
            position_ids,
            _PROBE_CONTACT,
            f"e1.e3.probe.{arm}.n{parts}.{index}",
            start,
            end,
        )
        field = advance_fixed_e1_adapter_probe(
            field,
            fixed_adapter,
            distribution,
            interval,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
    return field


def run_e1_e3_probe_once(
    initial_field: SharedMCMField,
    initial_e1_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> E1E3ProbeRunResult:
    """Compose the registered state arms and all identical probe controls."""

    try:
        history = produce_e1_mirrored_histories(
            initial_field,
            initial_e1_state,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
        state_arms = build_e1_e3_state_arms(
            initial_field,
            history.left_e1_state,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
    except (E1MirroredHistoryError, E1E3StateArmsError) as exc:
        raise E1E3ProbeRunError(str(exc)) from exc
    if evaluate_e1_e3_state_arms(state_arms) != "E3_STATE_ARMS_READY_FOR_PROBE":
        raise E1E3ProbeRunError("E3 state arms are not ready for the probe")

    position_ids = _position_ids(initial_field)
    preparation, preparation_time = _distribution(
        initial_field,
        position_ids,
        _PREPARATION_CONTACT,
        "e1.e3.probe.preparation",
        0,
        20,
    )
    try:
        probe_field = advance_neutral_fast_shared_field(
            copy.deepcopy(initial_field),
            preparation,
            preparation_time,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
    except NeutralLocalFieldSubstrateError as exc:
        raise E1E3ProbeRunError(str(exc)) from exc
    pre_digest = probe_field.snapshot().digest()
    pre_copies = [copy.deepcopy(probe_field) for _ in range(10)]
    if any(item.snapshot().digest() != pre_digest for item in pre_copies):
        raise E1E3ProbeRunError("pre-probe field copies are not identical")
    pre_s = max(_linf(pre_copies[0], item, "activation") for item in pre_copies[1:])
    pre_h = max(_linf(pre_copies[0], item, "afterimage") for item in pre_copies[1:])

    def probe_input() -> tuple[ReceptorDistribution, MCMFieldStepTime]:
        return _distribution(
            probe_field,
            position_ids,
            _PROBE_CONTACT,
            "e1.e3.probe.primary",
            20,
            40,
        )

    states = (
        state_arms.hold_state,
        state_arms.release_state,
        state_arms.compete_state,
    )
    try:
        distribution, interval = probe_input()
        p0 = advance_neutral_fast_shared_field(
            pre_copies[0],
            distribution,
            interval,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
        ablated: list[FrozenE1ProbeResult] = []
        active: list[FrozenE1ProbeResult] = []
        fixed: list[SharedMCMField] = []
        for index, state in enumerate(states):
            distribution, interval = probe_input()
            ablated.append(
                advance_frozen_e1_probe(
                    pre_copies[1 + index],
                    state,
                    distribution,
                    interval,
                    substrate_config,
                    afterimage_config,
                    dissipation_config,
                    backreaction_enabled=False,
                )
            )
            distribution, interval = probe_input()
            active.append(
                advance_frozen_e1_probe(
                    pre_copies[4 + index],
                    state,
                    distribution,
                    interval,
                    substrate_config,
                    afterimage_config,
                    dissipation_config,
                    backreaction_enabled=True,
                )
            )
        for index, active_result in enumerate(active):
            distribution, interval = probe_input()
            fixed.append(
                advance_fixed_e1_adapter_probe(
                    pre_copies[7 + index],
                    active_result.applied_adapter,
                    distribution,
                    interval,
                    substrate_config,
                    afterimage_config,
                    dissipation_config,
                )
            )
    except (FrozenE1ProbeError, NeutralLocalFieldSubstrateError) as exc:
        raise E1E3ProbeRunError(str(exc)) from exc

    p0_digest = p0.snapshot().digest()
    if any(item.field.snapshot().digest() != p0_digest for item in ablated):
        raise E1E3ProbeRunError("P0 and E3 ablated fields are not bit identical")
    if any(
        active[index].field.snapshot().digest() != fixed[index].snapshot().digest()
        for index in range(3)
    ):
        raise E1E3ProbeRunError("active and fixed-gain E3 fields differ")
    if any(
        active[index].e1_state is not states[index]
        or ablated[index].e1_state is not states[index]
        for index in range(3)
    ):
        raise E1E3ProbeRunError("a frozen E3 probe changed state identity")

    refinements = []
    for index, arm in enumerate(("hold", "release", "compete")):
        n2 = _run_fixed_partition(
            probe_field,
            active[index].applied_adapter,
            position_ids,
            2,
            arm,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
        n4 = _run_fixed_partition(
            probe_field,
            active[index].applied_adapter,
            position_ids,
            4,
            arm,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
        refinements.append((n2, n4))

    def max_distance(pairs, role: str) -> float:
        return max(_linf(first, second, role) for first, second in pairs)

    metrics = E1E3ProbeMetrics(
        pre_probe_s_linf=pre_s,
        pre_probe_h_linf=pre_h,
        ablation_p0_s_linf=max(_linf(p0, item.field, "activation") for item in ablated),
        ablation_p0_h_linf=max(_linf(p0, item.field, "afterimage") for item in ablated),
        fixed_gain_s_linf=max(
            _linf(active[index].field, fixed[index], "activation") for index in range(3)
        ),
        fixed_gain_h_linf=max(
            _linf(active[index].field, fixed[index], "afterimage") for index in range(3)
        ),
        refinement_s_linf=max_distance(refinements, "activation"),
        refinement_h_linf=max_distance(refinements, "afterimage"),
        hold_p0_s_linf=_linf(active[0].field, p0, "activation"),
        hold_p0_h_linf=_linf(active[0].field, p0, "afterimage"),
        release_p0_s_linf=_linf(active[1].field, p0, "activation"),
        release_p0_h_linf=_linf(active[1].field, p0, "afterimage"),
        compete_p0_s_linf=_linf(active[2].field, p0, "activation"),
        compete_p0_h_linf=_linf(active[2].field, p0, "afterimage"),
        release_hold_s_linf=_linf(active[1].field, active[0].field, "activation"),
        release_hold_h_linf=_linf(active[1].field, active[0].field, "afterimage"),
        compete_release_s_linf=_linf(active[2].field, active[1].field, "activation"),
        compete_release_h_linf=_linf(active[2].field, active[1].field, "afterimage"),
        compete_hold_s_linf=_linf(active[2].field, active[0].field, "activation"),
        compete_hold_h_linf=_linf(active[2].field, active[0].field, "afterimage"),
    )
    return E1E3ProbeRunResult(
        state_arms,
        pre_digest,
        p0,
        ablated[0].field,
        ablated[1].field,
        ablated[2].field,
        active[0].field,
        active[1].field,
        active[2].field,
        fixed[0],
        fixed[1],
        fixed[2],
        refinements[0][0],
        refinements[0][1],
        refinements[1][0],
        refinements[1][1],
        refinements[2][0],
        refinements[2][1],
        metrics,
    )


def evaluate_e1_e3_probe_run(result: E1E3ProbeRunResult) -> str:
    """Apply only the fixed S1-CC technical decision order."""

    if not isinstance(result, E1E3ProbeRunResult):
        raise E1E3ProbeRunError("E3 evaluation requires one complete result")
    if evaluate_e1_e3_state_arms(result.state_arms) != "E3_STATE_ARMS_READY_FOR_PROBE":
        return "INVALID_RUN"
    m = result.metrics
    exact = (
        m.pre_probe_s_linf == 0.0
        and m.pre_probe_h_linf == 0.0
        and m.ablation_p0_s_linf == 0.0
        and m.ablation_p0_h_linf == 0.0
    )
    bounded = (
        m.fixed_gain_s_linf <= E1_E3_PROBE_ABSOLUTE_TOLERANCE
        and m.fixed_gain_h_linf <= E1_E3_PROBE_ABSOLUTE_TOLERANCE
        and m.refinement_s_linf <= E1_E3_PROBE_ABSOLUTE_TOLERANCE
        and m.refinement_h_linf <= E1_E3_PROBE_ABSOLUTE_TOLERANCE
    )
    if not exact or not bounded:
        return "INVALID_RUN"
    floor_s = max(m.refinement_s_linf, E1_E3_PROBE_ABSOLUTE_TOLERANCE)
    floor_h = max(m.refinement_h_linf, E1_E3_PROBE_ABSOLUTE_TOLERANCE)
    release_effect = m.release_hold_s_linf > floor_s or m.release_hold_h_linf > floor_h
    if not release_effect:
        return "NO_E3_EFFECT_IN_FIRST_CORRIDOR"
    compete_effect = (
        m.compete_release_s_linf > floor_s
        or m.compete_release_h_linf > floor_h
    )
    if compete_effect:
        return "E3_RELEASE_AND_RESOURCE_REUSE"
    return "E3_RELEASE_ONLY"
