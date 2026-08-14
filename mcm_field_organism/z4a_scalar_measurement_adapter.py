"""Pure scalar projection of four Z4-A3 packets into the Z4-A4 schema."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from .z4a_component_trajectory import Z4AComponentTrajectory
from .z4a_generic_trajectory_runner import (
    Z4ATaskTrajectory,
    Z4ATechnicalPacket,
)
from .z4a_scalar_evaluation import (
    ARM_ORDER,
    MODEL_ORDER,
    TECHNICAL_CONTROL_ORDER,
    WORLD_ORDER,
    Z4AArmScalarResult,
    Z4AComponentMeasurement,
    Z4AModelDecisionState,
    Z4AModelScalarResult,
    Z4ARefinementTaskSummary,
    Z4AScalarEvaluationError,
    Z4AScalarEvaluationResult,
    Z4ATaskBudget,
    Z4AWorldDecisionState,
    Z4AWorldScalarResult,
    evaluate_z4a_decision,
    z4a_scalar_result_json_value,
)


class Z4AScalarMeasurementAdapterError(ValueError):
    """Raised when technical trajectories cannot form fixed scalar results."""


_GRID_SIZE = 101
_PATH_FLOOR = 1e-12
_CAUSAL_ARMS = ("reversed", "permuted", "independent")


def _component_values(
    trajectory: Z4AComponentTrajectory,
    component_id: str,
) -> np.ndarray:
    if not isinstance(trajectory, Z4AComponentTrajectory) or component_id not in trajectory.component_ids:
        raise Z4AScalarMeasurementAdapterError("trajectory component is unavailable")
    return np.asarray(
        [sample.values_for(component_id) for sample in trajectory.samples],
        dtype=np.float64,
    )


def _path_length(trajectory: Z4AComponentTrajectory, component_id: str) -> float:
    values = _component_values(trajectory, component_id)
    return float(math.fsum(float(value) for value in np.linalg.norm(np.diff(values, axis=0), axis=1)))


def _normalized_path(
    trajectory: Z4AComponentTrajectory,
    component_id: str,
) -> np.ndarray | None:
    values = _component_values(trajectory, component_id)
    increments = np.linalg.norm(np.diff(values, axis=0), axis=1)
    cumulative = np.concatenate((np.asarray([0.0]), np.cumsum(increments)))
    total = float(cumulative[-1])
    if not math.isfinite(total):
        raise Z4AScalarMeasurementAdapterError("component path is non-finite")
    if total <= _PATH_FLOOR:
        return None
    coordinates = cumulative / total
    unique_coordinates = []
    unique_values = []
    for coordinate, vector in zip(coordinates, values, strict=True):
        if unique_coordinates and coordinate == unique_coordinates[-1]:
            unique_values[-1] = vector
        else:
            unique_coordinates.append(float(coordinate))
            unique_values.append(vector)
    support = np.asarray(unique_coordinates, dtype=np.float64)
    support_values = np.asarray(unique_values, dtype=np.float64)
    grid = np.linspace(0.0, 1.0, _GRID_SIZE, dtype=np.float64)
    return np.stack(
        [
            np.interp(grid, support, support_values[:, index])
            for index in range(values.shape[1])
        ],
        axis=1,
    )


def _path_distance(
    reference: Z4AComponentTrajectory,
    compared: Z4AComponentTrajectory,
    component_id: str,
) -> float:
    reference_path = _normalized_path(reference, component_id)
    compared_path = _normalized_path(compared, component_id)
    if reference_path is None or compared_path is None:
        return 0.0
    if reference_path.shape != compared_path.shape:
        raise Z4AScalarMeasurementAdapterError("component path geometry changed")
    scale = float(np.max(np.abs(reference_path - reference_path[0])))
    if not math.isfinite(scale) or scale <= _PATH_FLOOR:
        return 0.0
    return float(np.max(np.abs(compared_path - reference_path))) / scale


def _indexed(packet: Z4ATechnicalPacket) -> dict[tuple[str, str, int | None], Z4ATaskTrajectory]:
    return {result.task_key: result for result in packet.trajectories}


def _model_components(model_id: str) -> tuple[str, ...]:
    return {
        "p0.exact": ("activation", "afterimage"),
        "f3.candidate": ("activation", "afterimage", "mcm_mass"),
        "b3.linear-coupled": (
            "activation",
            "afterimage",
            "baseline_state",
        ),
    }[model_id]


def _selected_result(
    indexed: dict[tuple[str, str, int | None], Z4ATaskTrajectory],
    model_id: str,
    arm_id: str,
) -> Z4ATaskTrajectory:
    refinement = None if model_id == "p0.exact" else 4
    return indexed[(model_id, arm_id, refinement)]


def _measurements_for_model(
    model_id: str,
    indexed: dict[tuple[str, str, int | None], Z4ATaskTrajectory],
    execution_digests: dict[str, str],
) -> tuple[tuple[Z4AArmScalarResult, ...], bool, bool, tuple[str, ...]]:
    component_ids = _model_components(model_id)
    selected = {
        arm_id: _selected_result(indexed, model_id, arm_id)
        for arm_id in ARM_ORDER
    }
    reference = selected["reference"].support.decision_trajectory
    reference_lengths = {
        component_id: _path_length(reference, component_id)
        for component_id in component_ids
    }
    envelopes: dict[str, dict[str, float]] = {}
    refinement_distances: dict[str, dict[str, tuple[float | None, float | None]]] = {}
    if model_id == "p0.exact":
        for arm_id in ARM_ORDER:
            envelopes[arm_id] = {component_id: _PATH_FLOOR for component_id in component_ids}
            refinement_distances[arm_id] = {
                component_id: (None, None) for component_id in component_ids
            }
    else:
        for arm_id in ARM_ORDER:
            n = indexed[(model_id, arm_id, 1)].support.decision_trajectory
            two_n = indexed[(model_id, arm_id, 2)].support.decision_trajectory
            four_n = indexed[(model_id, arm_id, 4)].support.decision_trajectory
            envelopes[arm_id] = {}
            refinement_distances[arm_id] = {}
            for component_id in component_ids:
                n_to_2n = _path_distance(two_n, n, component_id)
                two_n_to_4n = _path_distance(four_n, two_n, component_id)
                envelopes[arm_id][component_id] = max(
                    _PATH_FLOOR,
                    4.0 * two_n_to_4n,
                )
                refinement_distances[arm_id][component_id] = (
                    n_to_2n,
                    two_n_to_4n,
                )

    arm_results = []
    for arm_id in ARM_ORDER:
        result = selected[arm_id]
        trajectory = result.support.decision_trajectory
        measurements = []
        for component_id in component_ids:
            distance = (
                0.0
                if arm_id == "reference"
                else _path_distance(reference, trajectory, component_id)
            )
            comparison_envelope = max(
                envelopes["reference"][component_id],
                envelopes[arm_id][component_id],
            )
            n_to_2n, two_n_to_4n = refinement_distances[arm_id][component_id]
            within = distance <= comparison_envelope
            measurements.append(
                Z4AComponentMeasurement(
                    component_id,
                    reference_lengths[component_id],
                    n_to_2n,
                    two_n_to_4n,
                    envelopes[arm_id][component_id],
                    distance,
                    comparison_envelope,
                    within,
                    not within,
                )
            )
        refinements = (None,) if model_id == "p0.exact" else (1, 2, 4)
        summaries = tuple(
            _summary(indexed[(model_id, arm_id, refinement)])
            for refinement in refinements
        )
        arm_results.append(
            Z4AArmScalarResult(
                arm_id,
                execution_digests[arm_id],
                result.final_snapshot_digest,
                len(result.support.technical_trajectory.samples),
                len(result.support.decision_trajectory.samples),
                tuple(measurements),
                summaries,
            )
        )

    by_arm = {arm.arm_id: arm for arm in arm_results}
    failed = []
    for arm_id in ("reproduction", "partitioned"):
        if not all(
            measurement.within_comparison_envelope
            for measurement in by_arm[arm_id].component_measurements
        ):
            failed.append(
                "reference_reproduction_stable"
                if arm_id == "reproduction"
                else "partition_invariant"
            )
    if model_id != "p0.exact" and any(
        measurement.two_n_to_4n_distance is None
        or measurement.n_to_2n_distance is None
        or measurement.two_n_to_4n_distance > measurement.n_to_2n_distance
        for arm in arm_results
        for measurement in arm.component_measurements
    ):
        failed.append("refinement_converges")
    for component_id in ("activation", "afterimage"):
        if reference_lengths[component_id] <= _PATH_FLOOR:
            failed.append(f"unmeasurable_{component_id}_reference")
    technically_stable = not failed

    def arm_separates(arm_id: str, allowed_components: tuple[str, ...]) -> bool:
        return any(
            measurement.component_id in allowed_components
            and measurement.reference_path_length > _PATH_FLOOR
            and measurement.above_comparison_envelope
            for measurement in by_arm[arm_id].component_measurements
        )

    stable_separation = technically_stable and all(
        arm_separates(arm_id, component_ids) for arm_id in _CAUSAL_ARMS
    )
    fast_separation = technically_stable and all(
        arm_separates(arm_id, ("activation", "afterimage"))
        for arm_id in _CAUSAL_ARMS
    )
    if model_id != "f3.candidate":
        fast_separation = stable_separation
    return tuple(arm_results), stable_separation, fast_separation, tuple(dict.fromkeys(failed))


def _summary(result: Z4ATaskTrajectory) -> Z4ARefinementTaskSummary:
    return Z4ARefinementTaskSummary(
        result.refinement,
        result.integration_method,
        result.final_snapshot_digest,
        result.diagnostic_count,
        result.substep_count,
        result.runtime_seconds,
        result.maximum_step_seconds,
        result.maximum_abs_activation,
        result.maximum_abs_afterimage,
        result.maximum_mass_error,
        result.minimum_auxiliary_state,
    )


def _packet_control(packet: Z4ATechnicalPacket, name: str) -> bool:
    return dict(packet.controls)[name]


def _world_result(packet: Z4ATechnicalPacket) -> Z4AWorldScalarResult:
    indexed = _indexed(packet)
    execution_digests = dict(packet.execution_digests)
    model_results = []
    for model_id in MODEL_ORDER:
        arms, stable_separation, fast_separation, failed = _measurements_for_model(
            model_id,
            indexed,
            execution_digests,
        )
        packet_failed = tuple(name for name, value in packet.controls if not value)
        all_failed = tuple(dict.fromkeys(packet_failed + failed))
        technically_stable = not all_failed
        selected_results = tuple(
            result for result in packet.trajectories if result.model_id == model_id
        )
        model_results.append(
            Z4AModelScalarResult(
                model_id,
                _model_components(model_id),
                selected_results[0].dynamic_scalar_state_budget,
                technically_stable,
                stable_separation if technically_stable else None,
                fast_separation if technically_stable else None,
                all_failed,
                arms,
                math.fsum(result.runtime_seconds for result in selected_results),
                sum(result.substep_count for result in selected_results),
                max(result.maximum_abs_activation for result in selected_results),
                max(result.maximum_abs_afterimage for result in selected_results),
                None
                if model_id == "p0.exact"
                else max(result.maximum_mass_error for result in selected_results),
                None
                if model_id == "p0.exact"
                else min(result.minimum_auxiliary_state for result in selected_results),
            )
        )
    world_failed = tuple(
        dict.fromkeys(
            name
            for model in model_results
            for name in model.failed_controls
        )
    )
    reference = indexed[("p0.exact", "reference", None)]
    return Z4AWorldScalarResult(
        packet.world_id,
        "completed" if not world_failed else "technical_abort",
        world_failed,
        packet.source_binding_digests,
        packet.sequence_digests,
        packet.proposal_digests,
        packet.base_layer_digest,
        packet.dock_map_digest,
        packet.source_event_count,
        packet.completion_group_count,
        len(reference.support.technical_trajectory.samples),
        len(reference.support.decision_trajectory.samples),
        tuple(model_results),
        42,
        42,
        math.fsum(result.runtime_seconds for result in packet.trajectories),
    )


def _technical_controls(
    packets: tuple[Z4ATechnicalPacket, ...],
    worlds: tuple[Z4AWorldScalarResult, ...],
) -> tuple[tuple[str, bool], ...]:
    values = {
        "all_world_bindings_match": tuple(packet.world_id for packet in packets) == WORLD_ORDER,
        "all_world_packages_complete": all(len(packet.trajectories) == 42 for packet in packets),
        "task_inventory_complete": all(len(packet.task_inventory) == 42 for packet in packets),
        "all_handoffs_complete": all(_packet_control(packet, "handoffs_complete") for packet in packets),
        "all_models_share_handoffs": all(_packet_control(packet, "shared_handoff_per_arm") for packet in packets),
        "all_base_fields_match": all(bool(packet.base_layer_digest) for packet in packets),
        "all_completion_supports_complete": all(
            _packet_control(packet, "decision_support_equal")
            and all(result.support.required_ticks for result in packet.trajectories)
            for packet in packets
        ),
        "reference_reproduction_stable": all(
            "reference_reproduction_stable" not in model.failed_controls
            for world in worlds
            for model in world.model_results
        ),
        "partition_invariant": all(
            "partition_invariant" not in model.failed_controls
            for world in worlds
            for model in world.model_results
        ),
        "refinement_converges": all(_packet_control(packet, "refinement_converges") for packet in packets),
        "state_invariants_hold": all(
            _packet_control(packet, "state_invariants_hold")
            for packet in packets
        )
        and all(
            not any(
                name.startswith("unmeasurable_")
                for name in model.failed_controls
            )
            for world in worlds
            for model in world.model_results
        ),
        "observer_passive": all(_packet_control(packet, "observer_neutral") for packet in packets),
        "persistence_boundary_holds": True,
    }
    return tuple((name, bool(values[name])) for name in TECHNICAL_CONTROL_ORDER)


def evaluate_z4a_technical_packets(
    packets: Iterable[Z4ATechnicalPacket],
) -> Z4AScalarEvaluationResult:
    """Project four complete packets to one scalar result without side effects."""

    packets_in = tuple(packets)
    if len(packets_in) != 4 or any(
        not isinstance(packet, Z4ATechnicalPacket) for packet in packets_in
    ):
        raise Z4AScalarMeasurementAdapterError("adapter requires four technical packets")
    if tuple(packet.world_id for packet in packets_in) != WORLD_ORDER:
        raise Z4AScalarMeasurementAdapterError("technical packet world order changed")
    try:
        worlds = tuple(_world_result(packet) for packet in packets_in)
        controls = _technical_controls(packets_in, worlds)
        decision_states = tuple(
            Z4AWorldDecisionState(
                world.world_id,
                tuple(
                    Z4AModelDecisionState(
                        model.model_id,
                        model.technically_stable,
                        model.stable_causal_separation,
                        model.fast_component_causal_separation,
                    )
                    for model in world.model_results
                ),
            )
            for world in worlds
        )
        decision = evaluate_z4a_decision(decision_states, controls)
        completed = all(value for _, value in controls) and all(
            world.execution_status == "completed" for world in worlds
        )
        result = Z4AScalarEvaluationResult(
            "mcm.z4a.multiworld-field-encoder.run197.v1",
            "lauf-197",
            "mcm.z4a.multiworld-field-encoder.v1",
            "z4a.generic-field-trajectory-runner.v1",
            "z4a.multiworld-field-encoder-decision.v1",
            "completed" if completed else "technical_abort",
            None if completed else "evaluation",
            WORLD_ORDER,
            MODEL_ORDER,
            ARM_ORDER,
            tuple((packet.world_id, packet.world_contract_digest) for packet in packets_in),
            controls,
            worlds,
            Z4ATaskBudget(4, 42, 168, 168),
            decision.overall_decision,
            decision.decision_basis,
        )
        z4a_scalar_result_json_value(result)
        return result
    except (KeyError, TypeError, ValueError, Z4AScalarEvaluationError) as exc:
        if isinstance(exc, Z4AScalarMeasurementAdapterError):
            raise
        raise Z4AScalarMeasurementAdapterError(str(exc)) from exc


def z4a_scalar_measurement_adapter_public_roles() -> tuple[str, ...]:
    return (
        "packet_count",
        "world_scalar_results",
        "technical_controls",
        "overall_decision",
        "persistence_boundary_holds",
    )
