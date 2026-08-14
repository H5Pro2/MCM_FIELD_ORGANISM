"""Pre-registered frozen E1 identical-probe composition."""

from __future__ import annotations

import copy
from dataclasses import dataclass, fields
import math

import numpy as np

from .e1_frozen_history_probe import (
    FrozenE1ProbeError,
    FrozenE1ProbeResult,
    advance_fixed_e1_adapter_probe,
    advance_frozen_e1_probe,
)
from .e1_local_edge_plasticity import E1LocalEdgePlasticityState
from .e1_mirrored_history import (
    E1MirroredHistoryError,
    E1MirroredHistoryResult,
    produce_e1_mirrored_histories,
)
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


class E1FrozenE2RunError(ValueError):
    """Raised when the pre-registered frozen E2 run is incomplete."""


E1_FROZEN_E2_ABSOLUTE_TOLERANCE = 1e-12
_PREPARATION_CONTACT = (0.30, -0.20, 0.60)
_PROBE_CONTACT = (0.75, -0.25, 0.25)
_PROBE_TICKS_PER_SECOND = 20.0


def _finite_nonnegative(value: object, role: str) -> float:
    if isinstance(value, bool):
        raise E1FrozenE2RunError(f"{role} must be numeric, not boolean")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise E1FrozenE2RunError(f"{role} must be numeric") from exc
    if not math.isfinite(result) or result < 0.0:
        raise E1FrozenE2RunError(f"{role} must be finite and nonnegative")
    return result


@dataclass(frozen=True, slots=True)
class E1FrozenE2Metrics:
    """Raw nonnegative distances without interpretation roles."""

    pre_s_linf: float
    pre_h_linf: float
    state_linf: float
    total_binding_difference: float
    mirror_binding_error: float
    active_s_linf: float
    active_h_linf: float
    ablated_s_linf: float
    ablated_h_linf: float
    p0_a0_s_linf: float
    p0_a0_h_linf: float
    fixed_gain_s_linf: float
    fixed_gain_h_linf: float
    refinement_s_linf: float
    refinement_h_linf: float

    def __post_init__(self) -> None:
        for item in fields(self):
            object.__setattr__(
                self,
                item.name,
                _finite_nonnegative(getattr(self, item.name), item.name),
            )


@dataclass(frozen=True, slots=True)
class E1FrozenE2RunResult:
    """Complete frozen E2 run data without an embedded decision."""

    history_result: E1MirroredHistoryResult
    pre_probe_snapshot_digest: str
    p0_field: SharedMCMField
    left_ablated_field: SharedMCMField
    right_ablated_field: SharedMCMField
    left_active_field: SharedMCMField
    right_active_field: SharedMCMField
    left_fixed_gain_field: SharedMCMField
    right_fixed_gain_field: SharedMCMField
    left_active_n2_field: SharedMCMField
    right_active_n2_field: SharedMCMField
    left_active_n4_field: SharedMCMField
    right_active_n4_field: SharedMCMField
    metrics: E1FrozenE2Metrics

    def __post_init__(self) -> None:
        if not isinstance(self.history_result, E1MirroredHistoryResult):
            raise E1FrozenE2RunError("E2 result requires one history result")
        if (
            not isinstance(self.pre_probe_snapshot_digest, str)
            or len(self.pre_probe_snapshot_digest) != 64
        ):
            raise E1FrozenE2RunError(
                "E2 result requires one pre-probe snapshot digest"
            )
        for role in (
            "p0_field",
            "left_ablated_field",
            "right_ablated_field",
            "left_active_field",
            "right_active_field",
            "left_fixed_gain_field",
            "right_fixed_gain_field",
            "left_active_n2_field",
            "right_active_n2_field",
            "left_active_n4_field",
            "right_active_n4_field",
        ):
            if not isinstance(getattr(self, role), SharedMCMField):
                raise E1FrozenE2RunError(f"{role} must be one completed field")
        if not isinstance(self.metrics, E1FrozenE2Metrics):
            raise E1FrozenE2RunError("E2 result requires raw metrics")


def _position_ids(field: SharedMCMField) -> tuple[str, ...]:
    ordered = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if len(ordered) != 3 or len(field.docks) != 1:
        raise E1FrozenE2RunError(
            "first frozen E2 run requires one dock on a three-neuron field"
        )
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
    carrier_ids = dock.dock_map.carrier_ids
    frame = ReceptorContactFrame(
        modality_id=dock.dock_map.modality_id,
        geometry_id=dock.dock_map.receptor_geometry_id,
        snapshot_id=snapshot_id,
        clock_id="e1.probe.source",
        window_start_tick=start_tick,
        window_end_tick=end_tick,
        carrier_ids=carrier_ids,
        values=tuple(
            value_by_neuron[neuron_by_carrier[carrier_id]]
            for carrier_id in carrier_ids
        ),
    )
    return (
        ReceptorDistribution(
            CommonFieldTime("e1.probe.organism", start_tick, end_tick),
            (DistributedReceptorContact(dock.dock_id, frame),),
        ),
        MCMFieldStepTime(
            "e1.probe.organism",
            start_tick,
            end_tick,
            _PROBE_TICKS_PER_SECOND,
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


def _linf(first: np.ndarray, second: np.ndarray) -> float:
    return float(np.max(np.abs(first - second)))


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
            f"e1.probe.{arm}.n{parts}.{index}",
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


def run_e1_frozen_e2_once(
    initial_field: SharedMCMField,
    initial_e1_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    dissipation_config: NeutralFieldDissipationConfig | None = None,
) -> E1FrozenE2RunResult:
    """Compose the fixed histories and all pre-registered frozen probe arms."""

    try:
        history = produce_e1_mirrored_histories(
            initial_field,
            initial_e1_state,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
    except E1MirroredHistoryError as exc:
        raise E1FrozenE2RunError(str(exc)) from exc
    if (
        history.total_binding_difference > E1_FROZEN_E2_ABSOLUTE_TOLERANCE
        or history.maximum_mirror_binding_error > E1_FROZEN_E2_ABSOLUTE_TOLERANCE
    ):
        raise E1FrozenE2RunError("mirrored history controls failed")

    position_ids = _position_ids(initial_field)
    preparation_distribution, preparation_interval = _distribution(
        initial_field,
        position_ids,
        _PREPARATION_CONTACT,
        "e1.probe.preparation",
        0,
        20,
    )
    try:
        probe_field = advance_neutral_fast_shared_field(
            copy.deepcopy(initial_field),
            preparation_distribution,
            preparation_interval,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
    except NeutralLocalFieldSubstrateError as exc:
        raise E1FrozenE2RunError(str(exc)) from exc
    pre_digest = probe_field.snapshot().digest()
    pre_copies = [copy.deepcopy(probe_field) for _ in range(7)]
    if any(item.snapshot().digest() != pre_digest for item in pre_copies):
        raise E1FrozenE2RunError("pre-probe field copies are not identical")
    pre_s = _linf(_values(pre_copies[0], "activation"), _values(pre_copies[1], "activation"))
    pre_h = _linf(_values(pre_copies[0], "afterimage"), _values(pre_copies[1], "afterimage"))

    def probe_input(_arm: str):
        return _distribution(
            probe_field,
            position_ids,
            _PROBE_CONTACT,
            "e1.probe.primary",
            20,
            40,
        )

    try:
        p0_distribution, p0_interval = probe_input("p0")
        p0 = advance_neutral_fast_shared_field(
            pre_copies[0],
            p0_distribution,
            p0_interval,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )

        def frozen(field, state, arm: str, enabled: bool) -> FrozenE1ProbeResult:
            distribution, interval = probe_input(arm)
            return advance_frozen_e1_probe(
                field,
                state,
                distribution,
                interval,
                substrate_config,
                afterimage_config,
                dissipation_config,
                backreaction_enabled=enabled,
            )

        left_ablated = frozen(
            pre_copies[1], history.left_e1_state, "left.ablated", False
        )
        right_ablated = frozen(
            pre_copies[2], history.right_e1_state, "right.ablated", False
        )
        left_active = frozen(
            pre_copies[3], history.left_e1_state, "left.active", True
        )
        right_active = frozen(
            pre_copies[4], history.right_e1_state, "right.active", True
        )
        left_fixed_distribution, left_fixed_interval = probe_input("left.fixed")
        left_fixed = advance_fixed_e1_adapter_probe(
            pre_copies[5],
            left_active.applied_adapter,
            left_fixed_distribution,
            left_fixed_interval,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
        right_fixed_distribution, right_fixed_interval = probe_input("right.fixed")
        right_fixed = advance_fixed_e1_adapter_probe(
            pre_copies[6],
            right_active.applied_adapter,
            right_fixed_distribution,
            right_fixed_interval,
            substrate_config,
            afterimage_config,
            dissipation_config,
        )
    except (FrozenE1ProbeError, NeutralLocalFieldSubstrateError) as exc:
        raise E1FrozenE2RunError(str(exc)) from exc

    if p0.snapshot().digest() != left_ablated.field.snapshot().digest() or (
        p0.snapshot().digest() != right_ablated.field.snapshot().digest()
    ):
        raise E1FrozenE2RunError("P0 and ablated fields are not bit identical")
    if left_active.field.snapshot().digest() != left_fixed.snapshot().digest():
        raise E1FrozenE2RunError("left active and fixed-gain fields differ")
    if right_active.field.snapshot().digest() != right_fixed.snapshot().digest():
        raise E1FrozenE2RunError("right active and fixed-gain fields differ")
    if left_active.e1_state is not history.left_e1_state or (
        right_active.e1_state is not history.right_e1_state
    ):
        raise E1FrozenE2RunError("active probe changed a frozen E1 state")

    left_n2 = _run_fixed_partition(
        probe_field, left_active.applied_adapter, position_ids, 2, "left",
        substrate_config, afterimage_config, dissipation_config,
    )
    right_n2 = _run_fixed_partition(
        probe_field, right_active.applied_adapter, position_ids, 2, "right",
        substrate_config, afterimage_config, dissipation_config,
    )
    left_n4 = _run_fixed_partition(
        probe_field, left_active.applied_adapter, position_ids, 4, "left",
        substrate_config, afterimage_config, dissipation_config,
    )
    right_n4 = _run_fixed_partition(
        probe_field, right_active.applied_adapter, position_ids, 4, "right",
        substrate_config, afterimage_config, dissipation_config,
    )

    left_bindings = np.asarray(
        [item.binding for item in history.left_e1_state.edge_bindings]
    )
    right_bindings = np.asarray(
        [item.binding for item in history.right_e1_state.edge_bindings]
    )
    metrics = E1FrozenE2Metrics(
        pre_s_linf=pre_s,
        pre_h_linf=pre_h,
        state_linf=_linf(left_bindings, right_bindings),
        total_binding_difference=history.total_binding_difference,
        mirror_binding_error=history.maximum_mirror_binding_error,
        active_s_linf=_linf(
            _values(left_active.field, "activation"),
            _values(right_active.field, "activation"),
        ),
        active_h_linf=_linf(
            _values(left_active.field, "afterimage"),
            _values(right_active.field, "afterimage"),
        ),
        ablated_s_linf=_linf(
            _values(left_ablated.field, "activation"),
            _values(right_ablated.field, "activation"),
        ),
        ablated_h_linf=_linf(
            _values(left_ablated.field, "afterimage"),
            _values(right_ablated.field, "afterimage"),
        ),
        p0_a0_s_linf=max(
            _linf(_values(p0, "activation"), _values(left_ablated.field, "activation")),
            _linf(_values(p0, "activation"), _values(right_ablated.field, "activation")),
        ),
        p0_a0_h_linf=max(
            _linf(_values(p0, "afterimage"), _values(left_ablated.field, "afterimage")),
            _linf(_values(p0, "afterimage"), _values(right_ablated.field, "afterimage")),
        ),
        fixed_gain_s_linf=max(
            _linf(_values(left_active.field, "activation"), _values(left_fixed, "activation")),
            _linf(_values(right_active.field, "activation"), _values(right_fixed, "activation")),
        ),
        fixed_gain_h_linf=max(
            _linf(_values(left_active.field, "afterimage"), _values(left_fixed, "afterimage")),
            _linf(_values(right_active.field, "afterimage"), _values(right_fixed, "afterimage")),
        ),
        refinement_s_linf=max(
            _linf(_values(left_n2, "activation"), _values(left_n4, "activation")),
            _linf(_values(right_n2, "activation"), _values(right_n4, "activation")),
        ),
        refinement_h_linf=max(
            _linf(_values(left_n2, "afterimage"), _values(left_n4, "afterimage")),
            _linf(_values(right_n2, "afterimage"), _values(right_n4, "afterimage")),
        ),
    )
    return E1FrozenE2RunResult(
        history,
        pre_digest,
        p0,
        left_ablated.field,
        right_ablated.field,
        left_active.field,
        right_active.field,
        left_fixed,
        right_fixed,
        left_n2,
        right_n2,
        left_n4,
        right_n4,
        metrics,
    )


def evaluate_e1_frozen_e2_run(result: E1FrozenE2RunResult) -> str:
    """Apply only the pre-registered bounded technical decision."""

    if not isinstance(result, E1FrozenE2RunResult):
        raise E1FrozenE2RunError("E2 evaluation requires one complete result")
    m = result.metrics
    exact_controls = (
        m.pre_s_linf == 0.0
        and m.pre_h_linf == 0.0
        and m.ablated_s_linf == 0.0
        and m.ablated_h_linf == 0.0
        and m.p0_a0_s_linf == 0.0
        and m.p0_a0_h_linf == 0.0
    )
    tolerance_controls = (
        m.total_binding_difference <= E1_FROZEN_E2_ABSOLUTE_TOLERANCE
        and m.mirror_binding_error <= E1_FROZEN_E2_ABSOLUTE_TOLERANCE
        and m.fixed_gain_s_linf <= E1_FROZEN_E2_ABSOLUTE_TOLERANCE
        and m.fixed_gain_h_linf <= E1_FROZEN_E2_ABSOLUTE_TOLERANCE
    )
    if not exact_controls or not tolerance_controls:
        return "INVALID_RUN"
    if m.state_linf <= max(
        m.refinement_s_linf,
        m.refinement_h_linf,
        E1_FROZEN_E2_ABSOLUTE_TOLERANCE,
    ):
        return "NO_E2_EFFECT_IN_FIRST_CORRIDOR"
    if (
        m.active_s_linf
        > max(m.refinement_s_linf, E1_FROZEN_E2_ABSOLUTE_TOLERANCE)
        or m.active_h_linf
        > max(m.refinement_h_linf, E1_FROZEN_E2_ABSOLUTE_TOLERANCE)
    ):
        return "E2_TECHNICAL_CAUSAL_EFFECT"
    return "NO_E2_EFFECT_IN_FIRST_CORRIDOR"
