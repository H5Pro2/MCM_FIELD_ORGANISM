"""Private S1-CI E4 runner bindings for the shared F3 model family."""

from __future__ import annotations

import copy
from dataclasses import replace
import hashlib
import json
import math
from typing import Callable

import numpy as np

from .e1_e4_baseline_handoffs import (
    E1_E4_CHECKPOINT_IDS,
    E1E4CheckpointEffect,
    E1E4ObservableProfile,
    build_e1_e4_const_v_handoff,
    compute_e1_e4_const_v_coupling,
)
from .e1_e4_execution import (
    E1_E4_ABSOLUTE_TOLERANCE,
    E1E4ModelRun,
    build_frozen_e1_e4_f3_reader,
    without_e1_e4_f3_backreaction,
)
from .field_step_time import MCMFieldStepTime
from .mcm_f3_baseline_coupling import (
    compute_mcm_f3_linear_coupled_baseline,
    compute_mcm_f3_local_leaky_baseline,
)
from .mcm_f3_coupling import (
    MCMF3CouplingResult,
    compute_mcm_f3_coupling,
)
from .mcm_f3_runtime import (
    MCMF3AdvanceDiagnostics,
    MCMF3RuntimeError,
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field,
)
from .mcm_substrate_state import MCMSubstrateArmContract, MCMSubstrateState
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
)
from .receptor_contract import CommonFieldTime, ReceptorContactFrame
from .receptor_distributor import DistributedReceptorContact, ReceptorDistribution
from .shared_mcm_field import SharedMCMField


class E1E4F3RunnerError(ValueError):
    """Raised when an S1-CI F3 family runner leaves the S1-CG corridor."""


E1_E4_F3_MODEL_IDS = ("b3", "b4", "b5", "b6")
_LEFT_CONTACT = (1.0, 0.0, 0.0)
_RIGHT_CONTACT = (0.0, 0.0, 1.0)
_PREPARATION_CONTACT = (0.30, -0.20, 0.60)
_PROBE_CONTACT = (0.75, -0.25, 0.25)
_HISTORY_TICKS_PER_SECOND = 10.0
_PROBE_TICKS_PER_SECOND = 20.0

_CouplingCalculator = Callable[
    [object, MCMSubstrateState], MCMF3CouplingResult
]


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload, allow_nan=False, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _position_ids(field: SharedMCMField) -> tuple[str, ...]:
    if not isinstance(field, SharedMCMField):
        raise E1E4F3RunnerError("F3 E4 runner requires one shared field")
    ordered = tuple(sorted(field.layer.neurons, key=lambda item: item.position))
    if (
        len(ordered) != 3
        or tuple(item.position for item in ordered) != ((0,), (1,), (2,))
        or len(field.docks) != 1
        or field.substrate is not None
        or field.last_distribution is not None
        or field.layer.tick != 0
    ):
        raise E1E4F3RunnerError(
            "F3 E4 runner requires one fresh neutral three-node field"
        )
    neuron_ids = tuple(item.neuron_id for item in ordered)
    if set(field.docks[0].dock_map.neuron_ids) != set(neuron_ids):
        raise E1E4F3RunnerError("F3 E4 dock must cover all three nodes")
    return neuron_ids


def _distribution(
    field: SharedMCMField,
    position_ids: tuple[str, ...],
    values: tuple[float, ...] | None,
    snapshot_id: str,
    clock_id: str,
    start_tick: int,
    end_tick: int,
    ticks_per_second: float,
) -> tuple[ReceptorDistribution, MCMFieldStepTime]:
    contacts = ()
    if values is not None:
        dock = field.docks[0]
        value_by_neuron = dict(zip(position_ids, values, strict=True))
        neuron_by_carrier = dict(dock.dock_map.pairs)
        frame = ReceptorContactFrame(
            modality_id=dock.dock_map.modality_id,
            geometry_id=dock.dock_map.receptor_geometry_id,
            snapshot_id=snapshot_id,
            clock_id=f"{clock_id}.source",
            window_start_tick=start_tick,
            window_end_tick=end_tick,
            carrier_ids=dock.dock_map.carrier_ids,
            values=tuple(
                value_by_neuron[neuron_by_carrier[carrier_id]]
                for carrier_id in dock.dock_map.carrier_ids
            ),
        )
        contacts = (DistributedReceptorContact(dock.dock_id, frame),)
    return (
        ReceptorDistribution(
            CommonFieldTime(clock_id, start_tick, end_tick), contacts
        ),
        MCMFieldStepTime(clock_id, start_tick, end_tick, ticks_per_second),
    )


def _advance(
    field: SharedMCMField,
    position_ids: tuple[str, ...],
    values: tuple[float, ...] | None,
    snapshot_id: str,
    clock_id: str,
    start_tick: int,
    end_tick: int,
    ticks_per_second: float,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    refinement: int,
    calculator: _CouplingCalculator,
) -> tuple[SharedMCMField, MCMF3AdvanceDiagnostics]:
    distribution, step_time = _distribution(
        field,
        position_ids,
        values,
        snapshot_id,
        clock_id,
        start_tick,
        end_tick,
        ticks_per_second,
    )
    try:
        result = advance_mcm_f3_shared_field(
            field,
            distribution,
            step_time,
            substrate_config,
            afterimage_config,
            refinement=refinement,
            _coupling_calculator=calculator,
        )
    except (MCMF3RuntimeError, NeutralLocalFieldSubstrateError) as exc:
        raise E1E4F3RunnerError(str(exc)) from exc
    return result.field, result.diagnostics


def _history_checkpoints(
    initial_field: SharedMCMField,
    initial_substrate: MCMSubstrateState,
    position_ids: tuple[str, ...],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    refinement: int,
    calculator: _CouplingCalculator,
) -> tuple[tuple[str, MCMSubstrateState], tuple[MCMF3AdvanceDiagnostics, ...]]:
    field = replace(copy.deepcopy(initial_field), substrate=initial_substrate)
    diagnostics = []
    for index in range(8):
        field, item = _advance(
            field,
            position_ids,
            _LEFT_CONTACT,
            f"e1.e4.f3.h.{index + 1}",
            "e1.e4.f3.history",
            index * 10,
            (index + 1) * 10,
            _HISTORY_TICKS_PER_SECOND,
            substrate_config,
            afterimage_config,
            refinement,
            calculator,
        )
        diagnostics.append(item)
    checkpoints = [("h8", field.substrate)]

    gap_field = field
    gap_windows = (("g1", 80, 90), ("g4", 90, 120), ("g8", 120, 160))
    g4_field = None
    for checkpoint_id, start_tick, end_tick in gap_windows:
        gap_field, item = _advance(
            gap_field,
            position_ids,
            None,
            f"e1.e4.f3.{checkpoint_id}",
            "e1.e4.f3.history",
            start_tick,
            end_tick,
            _HISTORY_TICKS_PER_SECOND,
            substrate_config,
            afterimage_config,
            refinement,
            calculator,
        )
        diagnostics.append(item)
        checkpoints.append((checkpoint_id, gap_field.substrate))
        if checkpoint_id == "g4":
            g4_field = copy.deepcopy(gap_field)
    if g4_field is None:
        raise E1E4F3RunnerError("F3 E4 G4 fork was not materialized")

    compete_field = g4_field
    no_backreaction = without_e1_e4_f3_backreaction(calculator)
    for index in range(8):
        compete_field, item = _advance(
            compete_field,
            position_ids,
            _RIGHT_CONTACT,
            f"e1.e4.f3.c.{index + 1}",
            "e1.e4.f3.history",
            120 + index * 10,
            130 + index * 10,
            _HISTORY_TICKS_PER_SECOND,
            substrate_config,
            afterimage_config,
            refinement,
            no_backreaction,
        )
        diagnostics.append(item)
        checkpoints.append((f"c{index + 1}", compete_field.substrate))
    if tuple(item[0] for item in checkpoints) != E1_E4_CHECKPOINT_IDS:
        raise E1E4F3RunnerError("F3 E4 checkpoint order changed")
    return tuple(checkpoints), tuple(diagnostics)


def _field_values(field: SharedMCMField, role: str) -> np.ndarray:
    return np.asarray(
        [
            getattr(item, role)
            for item in sorted(field.layer.neurons, key=lambda item: item.position)
        ],
        dtype=np.float64,
    )


def _probe_profile(
    model_id: str,
    initial_field: SharedMCMField,
    checkpoints: tuple[tuple[str, MCMSubstrateState], ...],
    position_ids: tuple[str, ...],
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
    refinement: int,
    calculator: _CouplingCalculator,
) -> tuple[
    E1E4ObservableProfile,
    bool,
    bool,
    tuple[MCMF3AdvanceDiagnostics, ...],
]:
    preparation, preparation_time = _distribution(
        initial_field,
        position_ids,
        _PREPARATION_CONTACT,
        "e1.e4.f3.probe.preparation",
        "e1.e4.f3.probe",
        0,
        20,
        _PROBE_TICKS_PER_SECOND,
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
            "e1.e4.f3.probe.primary",
            "e1.e4.f3.probe",
            20,
            40,
            _PROBE_TICKS_PER_SECOND,
        )
        p0 = advance_neutral_fast_shared_field(
            copy.deepcopy(prepared),
            probe_distribution,
            probe_time,
            substrate_config,
            afterimage_config,
        )
        p0_control = advance_neutral_fast_shared_field(
            copy.deepcopy(prepared),
            probe_distribution,
            probe_time,
            substrate_config,
            afterimage_config,
        )
    except NeutralLocalFieldSubstrateError as exc:
        raise E1E4F3RunnerError(str(exc)) from exc

    p0_s = _field_values(p0, "activation")
    p0_h = _field_values(p0, "afterimage")
    effects = []
    ablation_hold = p0.snapshot().digest() == p0_control.snapshot().digest()
    fixed_hold = True
    diagnostics = []

    for checkpoint_id, fixed_substrate in checkpoints:
        active_initial = replace(copy.deepcopy(prepared), substrate=fixed_substrate)
        frozen_reader = build_frozen_e1_e4_f3_reader(calculator, fixed_substrate)
        try:
            active = advance_mcm_f3_shared_field(
                active_initial,
                probe_distribution,
                probe_time,
                substrate_config,
                afterimage_config,
                refinement=refinement,
                _coupling_calculator=frozen_reader,
            )
        except MCMF3RuntimeError as exc:
            raise E1E4F3RunnerError(str(exc)) from exc
        diagnostics.append(active.diagnostics)
        active_s = _field_values(active.field, "activation")
        active_h = _field_values(active.field, "afterimage")
        next_substrate = active.field.substrate
        fixed_hold = fixed_hold and bool(
            isinstance(next_substrate, MCMSubstrateState)
            and next_substrate.arm == fixed_substrate.arm
            and next_substrate.edge_inventory_digest
            == fixed_substrate.edge_inventory_digest
            and np.max(
                np.abs(
                    np.asarray(
                        [item.mass for item in next_substrate.masses],
                        dtype=np.float64,
                    )
                    - np.asarray(
                        [item.mass for item in fixed_substrate.masses],
                        dtype=np.float64,
                    )
                )
            )
            <= E1_E4_ABSOLUTE_TOLERANCE
        )
        effects.append(
            E1E4CheckpointEffect(
                checkpoint_id,
                tuple(float(value) for value in active_s - p0_s),
                tuple(float(value) for value in active_h - p0_h),
            )
        )
    return (
        E1E4ObservableProfile(model_id, tuple(effects)),
        ablation_hold,
        fixed_hold,
        tuple(diagnostics),
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
        raise E1E4F3RunnerError("F3 E4 refinement has no measurable scale")
    return residual / scale


def run_e1_e4_f3_model(
    model_id: str,
    initial_field: SharedMCMField,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
) -> E1E4ModelRun:
    """Run one isolated B3-B6 lifecycle without composing the E4 matrix."""

    if model_id not in E1_E4_F3_MODEL_IDS:
        raise E1E4F3RunnerError("unknown F3 E4 model id")
    if substrate_config != NeutralLocalFieldSubstrateConfig(1.0):
        raise E1E4F3RunnerError("F3 E4 S response contract changed")
    if afterimage_config != NeutralFastAfterimageConfig(0.5):
        raise E1E4F3RunnerError("F3 E4 H time contract changed")
    position_ids = _position_ids(initial_field)

    if model_id == "b6":
        handoff = build_e1_e4_const_v_handoff(initial_field.layer)
        initial_substrate = handoff.initial_substrate

        def calculator(layer, substrate):
            return compute_e1_e4_const_v_coupling(handoff, layer, substrate)

        calculator_id = "w7-n.const-v"
    else:
        arm = MCMSubstrateArmContract(
            f"e1.e4.{model_id}", 1.0, 0.5, 1.0, 1.0
        )
        active = activate_mcm_f3_field(copy.deepcopy(initial_field), arm)
        initial_substrate = active.substrate
        calculator = {
            "b3": compute_mcm_f3_local_leaky_baseline,
            "b4": compute_mcm_f3_linear_coupled_baseline,
            "b5": compute_mcm_f3_coupling,
        }[model_id]
        calculator_id = {
            "b3": "local-leaky",
            "b4": "linear-coupled-field",
            "b5": "f3-candidate",
        }[model_id]
    if not isinstance(initial_substrate, MCMSubstrateState):
        raise E1E4F3RunnerError("F3 E4 initial substrate is unavailable")

    profiles = []
    all_diagnostics = []
    ablation_controls = True
    fixed_controls = True
    for refinement in (2, 4):
        checkpoints, history_diagnostics = _history_checkpoints(
            initial_field,
            initial_substrate,
            position_ids,
            substrate_config,
            afterimage_config,
            refinement,
            calculator,
        )
        profile, ablation_hold, fixed_hold, probe_diagnostics = _probe_profile(
            model_id,
            initial_field,
            checkpoints,
            position_ids,
            substrate_config,
            afterimage_config,
            refinement,
            calculator,
        )
        profiles.append(profile)
        all_diagnostics.extend(history_diagnostics + probe_diagnostics)
        ablation_controls = ablation_controls and ablation_hold
        fixed_controls = fixed_controls and fixed_hold

    primary = profiles[1]
    control = profiles[0]
    maximum_mass_error = max(item.maximum_mass_error for item in all_diagnostics)
    minimum_resource = min(item.minimum_mass for item in all_diagnostics)
    parameter_digest = _digest(
        {
            "model_id": model_id,
            "calculator_id": calculator_id,
            "arm": {
                "lambda_sm_per_second": initial_substrate.arm.lambda_sm_per_second,
                "kappa": initial_substrate.arm.kappa,
                "eta": initial_substrate.arm.eta,
                "initial_total_mass": initial_substrate.arm.initial_total_mass,
            },
            "response_time_seconds": substrate_config.response_time_seconds,
            "afterimage_time_seconds": afterimage_config.time_constant_seconds,
            "geometry": initial_substrate.edge_inventory_digest,
            "refinements": (2, 4),
        }
    )
    return E1E4ModelRun(
        model_id=model_id,
        parameter_digest=parameter_digest,
        profile=primary,
        observation_schedule_matches=True,
        ablation_controls_hold=ablation_controls,
        fixed_reader_controls_hold=fixed_controls,
        invariants_hold=(
            math.isfinite(maximum_mass_error)
            and maximum_mass_error <= E1_E4_ABSOLUTE_TOLERANCE
            and math.isfinite(minimum_resource)
            and minimum_resource >= 0.0
        ),
        technically_compatible=True,
        relative_refinement_linf=_profile_refinement(primary, control),
        maximum_mass_or_budget_error=maximum_mass_error,
        minimum_internal_resource=minimum_resource,
    )


def build_e1_e4_f3_runner(
    model_id: str,
    initial_field: SharedMCMField,
    substrate_config: NeutralLocalFieldSubstrateConfig,
    afterimage_config: NeutralFastAfterimageConfig,
):
    """Bind one concrete private runner without executing it."""

    if model_id not in E1_E4_F3_MODEL_IDS:
        raise E1E4F3RunnerError("unknown F3 E4 model id")
    _position_ids(initial_field)

    def runner() -> E1E4ModelRun:
        return run_e1_e4_f3_model(
            model_id,
            copy.deepcopy(initial_field),
            substrate_config,
            afterimage_config,
        )

    return runner
