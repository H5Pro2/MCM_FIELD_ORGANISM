"""Private S1-CK S2-B2 and ORACLE-G E4 runner bindings."""

from __future__ import annotations

import copy
from dataclasses import asdict
import hashlib
import json
import math

import numpy as np

from .e1_e3_probe_run import _distribution
from .e1_e4_baseline_handoffs import (
    E1_E4_CHECKPOINT_IDS,
    E1E4CheckpointEffect,
    E1E4ObservableProfile,
    advance_e1_e4_s2_b2,
    advance_frozen_e1_e4_s2_b2_probe,
    build_e1_e4_s2_b2_handoff,
    build_zero_e1_e4_s2_state,
)
from .e1_e4_execution import E1E4ModelRun
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    _diffusion_generator,
    _generator_and_boundary,
    advance_neutral_fast_shared_field,
)
from .s2_reference_baselines import S2ReferenceState
from .shared_mcm_field import SharedMCMField


class E1E4S2OracleRunnerError(ValueError):
    """Raised when S2-B2 or ORACLE-G leaves the S1-CG corridor."""


_LEFT_CONTACT = (1.0, 0.0, 0.0)
_RIGHT_CONTACT = (0.0, 0.0, 1.0)
_PREPARATION_CONTACT = (0.30, -0.20, 0.60)
_PROBE_CONTACT = (0.75, -0.25, 0.25)


def _digest(value: object) -> str:
    encoded = json.dumps(
        value, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _position_ids(field: SharedMCMField) -> tuple[str, ...]:
    if not isinstance(field, SharedMCMField):
        raise E1E4S2OracleRunnerError("S2 E4 runner requires one shared field")
    ordered = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if (
        len(ordered) != 3
        or tuple(item.position for item in ordered) != ((0,), (1,), (2,))
        or len(field.docks) != 1
        or field.last_distribution is not None
        or field.layer.tick != 0
        or field.substrate is not None
    ):
        raise E1E4S2OracleRunnerError(
            "S2 E4 runner requires one fresh neutral three-node field"
        )
    return tuple(item.neuron_id for item in ordered)


def _contact_matrices(
    field: SharedMCMField,
    position_ids: tuple[str, ...],
    values: tuple[float, ...],
    snapshot_id: str,
    substrate_config: NeutralLocalFieldSubstrateConfig,
) -> tuple[np.ndarray, np.ndarray]:
    distribution, _ = _distribution(
        field, position_ids, values, snapshot_id, 0, 20
    )
    try:
        return _generator_and_boundary(field, distribution, substrate_config)
    except NeutralLocalFieldSubstrateError as exc:
        raise E1E4S2OracleRunnerError(str(exc)) from exc


def _history_checkpoints(
    initial_field: SharedMCMField,
    position_ids: tuple[str, ...],
    substrate_config: NeutralLocalFieldSubstrateConfig,
):
    handoff = build_e1_e4_s2_b2_handoff(initial_field.layer)
    state = build_zero_e1_e4_s2_state(handoff)
    left_generator, left_boundary = _contact_matrices(
        initial_field,
        position_ids,
        _LEFT_CONTACT,
        "e1.e4.s2.left",
        substrate_config,
    )
    right_generator, right_boundary = _contact_matrices(
        initial_field,
        position_ids,
        _RIGHT_CONTACT,
        "e1.e4.s2.right",
        substrate_config,
    )
    null_generator = _diffusion_generator(initial_field, substrate_config)
    null_boundary = np.zeros(3, dtype=np.float64)
    errors = []
    for _ in range(8):
        advanced = advance_e1_e4_s2_b2(
            handoff,
            state,
            left_generator,
            left_boundary,
            1.0,
            backreaction_enabled=True,
        )
        state = advanced.state
        errors.append(advanced.partition_error)
    checkpoints = [("h8", state)]

    gap_state = state
    g4_state = None
    for checkpoint_id, elapsed in (("g1", 1.0), ("g4", 3.0), ("g8", 4.0)):
        advanced = advance_e1_e4_s2_b2(
            handoff,
            gap_state,
            null_generator,
            null_boundary,
            elapsed,
            backreaction_enabled=True,
        )
        gap_state = advanced.state
        errors.append(advanced.partition_error)
        checkpoints.append((checkpoint_id, gap_state))
        if checkpoint_id == "g4":
            g4_state = gap_state
    if g4_state is None:
        raise E1E4S2OracleRunnerError("S2 E4 G4 fork is unavailable")

    compete_state = g4_state
    for index in range(8):
        advanced = advance_e1_e4_s2_b2(
            handoff,
            compete_state,
            right_generator,
            right_boundary,
            1.0,
            backreaction_enabled=False,
        )
        compete_state = advanced.state
        errors.append(advanced.partition_error)
        checkpoints.append((f"c{index + 1}", compete_state))
    if tuple(item[0] for item in checkpoints) != E1_E4_CHECKPOINT_IDS:
        raise E1E4S2OracleRunnerError("S2 E4 checkpoint order changed")
    return handoff, tuple(checkpoints), max(errors, default=0.0)


def _advance_frozen_parts(
    handoff,
    initial: S2ReferenceState,
    generator: np.ndarray,
    boundary: np.ndarray,
    parts: int,
    *,
    backreaction_enabled: bool,
) -> S2ReferenceState:
    state = initial
    for _ in range(parts):
        state = advance_frozen_e1_e4_s2_b2_probe(
            handoff,
            state,
            generator,
            boundary,
            1.0 / parts,
            backreaction_enabled=backreaction_enabled,
        ).state
    return state


def _effect(
    checkpoint_id: str,
    active: S2ReferenceState,
    p0: S2ReferenceState,
) -> E1E4CheckpointEffect:
    return E1E4CheckpointEffect(
        checkpoint_id,
        tuple(
            float(first - second)
            for first, second in zip(active.activation, p0.activation, strict=True)
        ),
        tuple(
            float(first - second)
            for first, second in zip(active.afterimage, p0.afterimage, strict=True)
        ),
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
        raise E1E4S2OracleRunnerError("S2 E4 refinement has no measurable scale")
    return residual / scale


def run_e1_e4_s2_b2_model(
    initial_field: SharedMCMField,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1E4ModelRun:
    """Run one isolated S2-B2 lifecycle without composing the E4 matrix."""

    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0):
        raise E1E4S2OracleRunnerError("S2 E4 S response contract changed")
    if afterimage_config != NeutralFastAfterimageConfig(0.5):
        raise E1E4S2OracleRunnerError("S2 E4 H time contract changed")
    position_ids = _position_ids(initial_field)
    handoff, checkpoints, maximum_partition_error = _history_checkpoints(
        initial_field, position_ids, substrate_config
    )

    preparation, preparation_time = _distribution(
        initial_field,
        position_ids,
        _PREPARATION_CONTACT,
        "e1.e4.s2.probe.preparation",
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
    except NeutralLocalFieldSubstrateError as exc:
        raise E1E4S2OracleRunnerError(str(exc)) from exc
    probe_generator, probe_boundary = _contact_matrices(
        prepared,
        position_ids,
        _PROBE_CONTACT,
        "e1.e4.s2.probe.primary",
        substrate_config,
    )
    prepared_s = tuple(
        item.activation
        for item in sorted(prepared.layer.neurons, key=lambda item: item.position)
    )
    prepared_h = tuple(
        item.afterimage
        for item in sorted(prepared.layer.neurons, key=lambda item: item.position)
    )
    primary_effects = []
    control_effects = []
    ablation_hold = True
    fixed_hold = True
    all_values = []
    internal_values = []
    for checkpoint_id, checkpoint in checkpoints:
        probe_initial = S2ReferenceState(
            prepared_s, prepared_h, checkpoint.development
        )
        p0 = _advance_frozen_parts(
            handoff,
            probe_initial,
            probe_generator,
            probe_boundary,
            1,
            backreaction_enabled=False,
        )
        active_once = _advance_frozen_parts(
            handoff,
            probe_initial,
            probe_generator,
            probe_boundary,
            1,
            backreaction_enabled=True,
        )
        n2 = _advance_frozen_parts(
            handoff,
            probe_initial,
            probe_generator,
            probe_boundary,
            2,
            backreaction_enabled=True,
        )
        n4 = _advance_frozen_parts(
            handoff,
            probe_initial,
            probe_generator,
            probe_boundary,
            4,
            backreaction_enabled=True,
        )
        direct_ablation = advance_frozen_e1_e4_s2_b2_probe(
            handoff,
            probe_initial,
            probe_generator,
            probe_boundary,
            1.0,
            backreaction_enabled=False,
        ).state
        ablation_hold = ablation_hold and p0 == direct_ablation
        fixed_hold = fixed_hold and bool(
            active_once.development
            == n2.development
            == n4.development
            == checkpoint.development
        )
        primary_effects.append(_effect(checkpoint_id, n4, p0))
        control_effects.append(_effect(checkpoint_id, n2, p0))
        all_values.extend(
            value
            for state in (checkpoint, active_once, n2, n4, p0)
            for vector in (state.activation, state.afterimage, state.development)
            for value in vector
        )
        internal_values.extend(
            value
            for state in (checkpoint, active_once, n2, n4, p0)
            for value in state.development
        )
    primary = E1E4ObservableProfile("b2", tuple(primary_effects))
    control = E1E4ObservableProfile("b2", tuple(control_effects))
    finite_and_bounded = all(
        math.isfinite(value) and abs(value) <= 1.0 + 1e-12
        for value in all_values
    )
    return E1E4ModelRun(
        "b2",
        _digest(
            {
                "model": "s2-b2",
                "handoff_id": handoff.handoff_id,
                "geometry": handoff.geometry_digest,
                "config": asdict(handoff.config),
                "response_time_seconds": substrate_config.response_time_seconds,
                "afterimage_time_seconds": afterimage_config.time_constant_seconds,
            }
        ),
        primary,
        True,
        ablation_hold,
        fixed_hold,
        finite_and_bounded,
        True,
        _profile_refinement(primary, control),
        maximum_partition_error,
        min(internal_values),
    )


def build_e1_e4_oracle_g_run(e1_run: E1E4ModelRun) -> E1E4ModelRun:
    """Copy only an already Fixed-Gain-valid E1 profile into ORACLE-G."""

    if (
        not isinstance(e1_run, E1E4ModelRun)
        or e1_run.model_id != "e1"
        or not e1_run.fixed_reader_controls_hold
        or not e1_run.controls_hold
    ):
        raise E1E4S2OracleRunnerError(
            "ORACLE-G requires one technically valid fixed-gain E1 run"
        )
    profile = E1E4ObservableProfile(
        "oracle-g",
        tuple(
            E1E4CheckpointEffect(
                item.checkpoint_id,
                item.activation_effect,
                item.afterimage_effect,
            )
            for item in e1_run.profile.checkpoints
        ),
    )
    return E1E4ModelRun(
        "oracle-g",
        _digest(
            {
                "model": "checkpointwise-e1-fixed-gain-oracle",
                "source_profile_digest": e1_run.profile.digest(),
            }
        ),
        profile,
        True,
        True,
        True,
        True,
        True,
        0.0,
        0.0,
        0.0,
    )
