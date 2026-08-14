"""Private S1-CJ E1, P0, and static H8-gain E4 runner bindings."""

from __future__ import annotations

import copy
import hashlib
import json
import math

import numpy as np

from .e1_e3_probe_run import _distribution, _run_fixed_partition
from .e1_e3_state_arms import (
    _resource_budget_error,
    _total_binding,
    produce_e1_competing_checkpoints,
    produce_e1_uniform_release_checkpoints,
)
from .e1_e4_baseline_handoffs import (
    E1_E4_CHECKPOINT_IDS,
    E1E4CheckpointEffect,
    E1E4ObservableProfile,
)
from .e1_e4_execution import E1E4ModelRun
from .e1_frozen_history_probe import (
    FrozenE1ProbeError,
    advance_fixed_e1_adapter_probe,
    advance_frozen_e1_probe,
)
from .e1_local_edge_plasticity import (
    E1LocalEdgePlasticityState,
    e1_free_node_resources,
)
from .e1_mirrored_history import E1MirroredHistoryError, produce_e1_mirrored_histories
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
)
from .shared_mcm_field import SharedMCMField


class E1E4E1RunnerError(ValueError):
    """Raised when E1, B0, or B1 leaves the registered E4 corridor."""


_PREPARATION_CONTACT = (0.30, -0.20, 0.60)
_PROBE_CONTACT = (0.75, -0.25, 0.25)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _position_ids(field: SharedMCMField) -> tuple[str, ...]:
    if not isinstance(field, SharedMCMField):
        raise E1E4E1RunnerError("E1 E4 runner requires one shared field")
    ordered = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if (
        len(ordered) != 3
        or tuple(item.position for item in ordered) != ((0,), (1,), (2,))
        or len(field.docks) != 1
        or field.last_distribution is not None
        or field.layer.tick != 0
        or field.substrate is not None
    ):
        raise E1E4E1RunnerError(
            "E1 E4 runner requires one fresh neutral three-node field"
        )
    return tuple(item.neuron_id for item in ordered)


def _values(field: SharedMCMField, role: str) -> np.ndarray:
    return np.asarray(
        [
            getattr(item, role)
            for item in sorted(field.layer.neurons, key=lambda item: item.position)
        ],
        dtype=np.float64,
    )


def _linf_vectors(first: tuple[float, ...], second: tuple[float, ...]) -> float:
    return float(
        np.max(
            np.abs(
                np.asarray(first, dtype=np.float64)
                - np.asarray(second, dtype=np.float64)
            )
        )
    )


def _profile_refinement(
    primary: E1E4ObservableProfile,
    control: E1E4ObservableProfile,
) -> float:
    first = np.asarray(primary.components, dtype=np.float64)
    second = np.asarray(control.components, dtype=np.float64)
    scale = float(np.max(np.abs(first)))
    residual = float(np.max(np.abs(first - second)))
    if scale == 0.0:
        if residual == 0.0:
            return 0.0
        raise E1E4E1RunnerError("E1 E4 refinement has no measurable scale")
    return residual / scale


def _effect(
    checkpoint_id: str,
    field: SharedMCMField,
    p0_s: np.ndarray,
    p0_h: np.ndarray,
) -> E1E4CheckpointEffect:
    return E1E4CheckpointEffect(
        checkpoint_id,
        tuple(float(value) for value in _values(field, "activation") - p0_s),
        tuple(float(value) for value in _values(field, "afterimage") - p0_h),
    )


def _checkpoint_states(
    initial_field: SharedMCMField,
    initial_e1_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> tuple[
    tuple[tuple[str, E1LocalEdgePlasticityState], ...],
    float,
    float,
    float,
    float,
    float,
]:
    try:
        history = produce_e1_mirrored_histories(
            initial_field,
            initial_e1_state,
            substrate_config,
            afterimage_config,
        )
        release = produce_e1_uniform_release_checkpoints(
            initial_field, history.left_e1_state
        )
        compete = produce_e1_competing_checkpoints(
            initial_field,
            release[2].state,
            substrate_config,
            afterimage_config,
        )
    except (E1MirroredHistoryError, ValueError) as exc:
        raise E1E4E1RunnerError(str(exc)) from exc
    checkpoints = (
        ("h8", history.left_e1_state),
        ("g1", release[1].state),
        ("g4", release[2].state),
        ("g8", release[3].state),
        *((f"c{index + 1}", item[1]) for index, item in enumerate(compete)),
    )
    if tuple(item[0] for item in checkpoints) != E1_E4_CHECKPOINT_IDS:
        raise E1E4E1RunnerError("E1 E4 checkpoint order changed")
    states = tuple(item[1] for item in checkpoints)
    budget_error = max(_resource_budget_error(initial_field, state) for state in states)
    minimum_resource = min(
        value
        for state in states
        for _, value in e1_free_node_resources(initial_field.layer, state)
    )
    release_drop = _total_binding(history.left_e1_state) - _total_binding(
        release[2].state
    )
    compete_rebound = _total_binding(compete[-1][1]) - _total_binding(
        release[2].state
    )
    release_analytic = max(item.analytic_linf for item in release)
    return checkpoints, budget_error, minimum_resource, max(
        release_analytic, 0.0
    ), release_drop, compete_rebound


def run_e1_e4_e1_b0_b1_models(
    initial_field: SharedMCMField,
    initial_e1_state: E1LocalEdgePlasticityState,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> tuple[
    tuple[E1E4ModelRun, E1E4ModelRun, E1E4ModelRun],
    tuple[tuple[str, float], ...],
]:
    """Produce E1, exact P0, static H8 gain, and actual continuity anchors."""

    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0):
        raise E1E4E1RunnerError("E1 E4 S response contract changed")
    if afterimage_config != NeutralFastAfterimageConfig(0.5):
        raise E1E4E1RunnerError("E1 E4 H time contract changed")
    position_ids = _position_ids(initial_field)
    if not isinstance(initial_e1_state, E1LocalEdgePlasticityState):
        raise E1E4E1RunnerError("E1 E4 runner requires one initial E1 state")
    (
        checkpoints,
        budget_error,
        minimum_resource,
        release_analytic,
        release_drop,
        compete_rebound,
    ) = _checkpoint_states(
        initial_field,
        initial_e1_state,
        substrate_config,
        afterimage_config,
    )

    preparation, preparation_time = _distribution(
        initial_field,
        position_ids,
        _PREPARATION_CONTACT,
        "e1.e4.probe.preparation",
        0,
        20,
    )
    try:
        prepared = advance_neutral_fast_shared_field(
            copy.deepcopy(initial_field),
            preparation,
            preparation_time,
            substrate_config,
            afterimage_config,
        )
        probe_distribution, probe_time = _distribution(
            prepared,
            position_ids,
            _PROBE_CONTACT,
            "e1.e4.probe.primary",
            20,
            40,
        )
        p0 = advance_neutral_fast_shared_field(
            copy.deepcopy(prepared),
            probe_distribution,
            probe_time,
            substrate_config,
            afterimage_config,
        )
    except NeutralLocalFieldSubstrateError as exc:
        raise E1E4E1RunnerError(str(exc)) from exc
    p0_s = _values(p0, "activation")
    p0_h = _values(p0, "afterimage")

    primary_effects = []
    control_effects = []
    absolute_refinements = {}
    ablation_hold = True
    fixed_hold = True
    h8_adapter = None
    try:
        for checkpoint_id, state in checkpoints:
            active = advance_frozen_e1_probe(
                copy.deepcopy(prepared),
                state,
                probe_distribution,
                probe_time,
                substrate_config,
                afterimage_config,
                backreaction_enabled=True,
            )
            ablated = advance_frozen_e1_probe(
                copy.deepcopy(prepared),
                state,
                probe_distribution,
                probe_time,
                substrate_config,
                afterimage_config,
                backreaction_enabled=False,
            )
            fixed = advance_fixed_e1_adapter_probe(
                copy.deepcopy(prepared),
                active.applied_adapter,
                probe_distribution,
                probe_time,
                substrate_config,
                afterimage_config,
            )
            n2 = _run_fixed_partition(
                prepared,
                active.applied_adapter,
                position_ids,
                2,
                f"e4.{checkpoint_id}",
                substrate_config,
                afterimage_config,
                None,
            )
            n4 = _run_fixed_partition(
                prepared,
                active.applied_adapter,
                position_ids,
                4,
                f"e4.{checkpoint_id}",
                substrate_config,
                afterimage_config,
                None,
            )
            ablation_hold = ablation_hold and ablated.field.snapshot().digest() == p0.snapshot().digest()
            fixed_hold = fixed_hold and active.field.snapshot().digest() == fixed.snapshot().digest()
            primary_effects.append(_effect(checkpoint_id, n4, p0_s, p0_h))
            control_effects.append(_effect(checkpoint_id, n2, p0_s, p0_h))
            absolute_refinements[checkpoint_id] = max(
                float(np.max(np.abs(_values(n4, "activation") - _values(n2, "activation")))),
                float(np.max(np.abs(_values(n4, "afterimage") - _values(n2, "afterimage")))),
            )
            if checkpoint_id == "h8":
                h8_adapter = active.applied_adapter
    except FrozenE1ProbeError as exc:
        raise E1E4E1RunnerError(str(exc)) from exc
    if h8_adapter is None:
        raise E1E4E1RunnerError("E1 E4 H8 adapter is unavailable")

    e1_profile = E1E4ObservableProfile("e1", tuple(primary_effects))
    e1_control = E1E4ObservableProfile("e1", tuple(control_effects))
    zero_effects = tuple(
        E1E4CheckpointEffect(checkpoint_id, (0.0,) * 3, (0.0,) * 3)
        for checkpoint_id in E1_E4_CHECKPOINT_IDS
    )
    b0_profile = E1E4ObservableProfile("b0", zero_effects)
    b1_n2 = _run_fixed_partition(
        prepared,
        h8_adapter,
        position_ids,
        2,
        "e4.b1",
        substrate_config,
        afterimage_config,
        None,
    )
    b1_n4 = _run_fixed_partition(
        prepared,
        h8_adapter,
        position_ids,
        4,
        "e4.b1",
        substrate_config,
        afterimage_config,
        None,
    )
    b1_primary_effect = _effect("h8", b1_n4, p0_s, p0_h)
    b1_control_effect = _effect("h8", b1_n2, p0_s, p0_h)
    b1_profile = E1E4ObservableProfile(
        "b1",
        tuple(
            E1E4CheckpointEffect(
                checkpoint_id,
                b1_primary_effect.activation_effect,
                b1_primary_effect.afterimage_effect,
            )
            for checkpoint_id in E1_E4_CHECKPOINT_IDS
        ),
    )
    b1_control = E1E4ObservableProfile(
        "b1",
        tuple(
            E1E4CheckpointEffect(
                checkpoint_id,
                b1_control_effect.activation_effect,
                b1_control_effect.afterimage_effect,
            )
            for checkpoint_id in E1_E4_CHECKPOINT_IDS
        ),
    )
    contract_payload = {
        "contract": {
            "node_capacity": initial_e1_state.contract.node_capacity,
            "binding_rate_per_second": initial_e1_state.contract.binding_rate_per_second,
            "release_rate_per_second": initial_e1_state.contract.release_rate_per_second,
            "backreaction_gain": initial_e1_state.contract.backreaction_gain,
        },
        "geometry": initial_e1_state.edge_inventory_digest,
        "response_time_seconds": substrate_config.response_time_seconds,
        "afterimage_time_seconds": afterimage_config.time_constant_seconds,
    }
    e1_run = E1E4ModelRun(
        "e1",
        _digest({"model": "e1", **contract_payload}),
        e1_profile,
        True,
        ablation_hold,
        fixed_hold,
        budget_error <= 1e-12 and minimum_resource >= 0.0,
        True,
        _profile_refinement(e1_profile, e1_control),
        budget_error,
        minimum_resource,
    )
    b0_run = E1E4ModelRun(
        "b0",
        _digest({"model": "p0.exact", **contract_payload}),
        b0_profile,
        True,
        True,
        True,
        True,
        True,
        0.0,
        0.0,
        0.0,
    )
    b1_run = E1E4ModelRun(
        "b1",
        _digest(
            {
                "model": "static-h8-gain",
                "edge_rates": tuple(
                    (item.first_neuron_id, item.second_neuron_id, item.rate_per_second)
                    for item in h8_adapter.edge_rates
                ),
                **contract_payload,
            }
        ),
        b1_profile,
        True,
        True,
        True,
        True,
        True,
        _profile_refinement(b1_profile, b1_control),
        0.0,
        0.0,
    )

    effects = {item.checkpoint_id: item for item in e1_profile.checkpoints}
    continuity_anchors = (
        ("release_hold_s_linf", _linf_vectors(effects["g4"].activation_effect, effects["h8"].activation_effect)),
        ("release_hold_h_linf", _linf_vectors(effects["g4"].afterimage_effect, effects["h8"].afterimage_effect)),
        ("compete_release_s_linf", _linf_vectors(effects["c8"].activation_effect, effects["g4"].activation_effect)),
        ("compete_release_h_linf", _linf_vectors(effects["c8"].afterimage_effect, effects["g4"].afterimage_effect)),
        ("hold_p0_s_linf", max(abs(value) for value in effects["h8"].activation_effect)),
        ("hold_p0_h_linf", max(abs(value) for value in effects["h8"].afterimage_effect)),
        ("release_p0_s_linf", max(abs(value) for value in effects["g4"].activation_effect)),
        ("release_p0_h_linf", max(abs(value) for value in effects["g4"].afterimage_effect)),
        ("compete_p0_s_linf", max(abs(value) for value in effects["c8"].activation_effect)),
        ("compete_p0_h_linf", max(abs(value) for value in effects["c8"].afterimage_effect)),
        ("release_analytic_linf", release_analytic),
        ("resource_budget_linf", budget_error),
        ("release_total_binding_drop", release_drop),
        ("compete_total_binding_rebound", compete_rebound),
        (
            "maximum_refinement_linf",
            max(absolute_refinements[item] for item in ("h8", "g4", "c8")),
        ),
    )
    if any(not math.isfinite(value) for _, value in continuity_anchors):
        raise E1E4E1RunnerError("E1 E4 continuity anchors must remain finite")
    return (e1_run, b0_run, b1_run), continuity_anchors
