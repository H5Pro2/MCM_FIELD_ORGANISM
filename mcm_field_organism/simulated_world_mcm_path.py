"""Passive Methodik-031 path from simulated world contact to MCM window."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
import hashlib
import json
from typing import Callable, Iterable

from .mcm_distributor import MCMDistributor, MCMFieldWindow
from .mcm_neuron_layer import receptor_projection_baseline
from .sensor_mcm_field import (
    CommonFieldTime,
    ReceptorContactFrame,
    build_receptor_aligned_mcm_field,
)
from .simulated_effector_world import (
    InterventionCause,
    SimulatedWorldReceptorFrame,
    SimulatedWorldState,
    WorldIntervention,
    WORLD_CAUSES,
    WORLD_DELTAS,
    WORLD_POSITIONS,
    advance_simulated_world,
    receptor_frame_from_world,
)


class SimulatedWorldMCMPathError(ValueError):
    """Raised when the passive simulated receptor-to-MCM path is invalid."""


SIMULATED_RECEPTOR_CARRIER_IDS = tuple(
    f"contact.p{position}" for position in WORLD_POSITIONS
)

PathObserver = Callable[["SimulatedWorldMCMPathObservation"], object]


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _receptor_payload(frame: ReceptorContactFrame) -> dict[str, object]:
    return {
        "modality_id": frame.modality_id,
        "geometry_id": frame.geometry_id,
        "snapshot_id": frame.snapshot_id,
        "clock_id": frame.clock_id,
        "window_start_tick": frame.window_start_tick,
        "window_end_tick": frame.window_end_tick,
        "carrier_ids": frame.carrier_ids,
        "values": frame.values,
    }


def simulated_world_receptor_to_contact_frame(
    frame: SimulatedWorldReceptorFrame,
) -> ReceptorContactFrame:
    """Adapt only completed simulated contact values and source time."""

    if not isinstance(frame, SimulatedWorldReceptorFrame):
        raise SimulatedWorldMCMPathError(
            "adapter requires a completed simulated world receptor frame"
        )
    return ReceptorContactFrame(
        modality_id="simulated.contact",
        geometry_id="simulated.ring7.receptor.v1",
        snapshot_id=f"simulated.receptor.tick.{frame.source_tick}",
        clock_id="simulated.world",
        window_start_tick=frame.source_tick,
        window_end_tick=frame.source_tick + 1,
        carrier_ids=SIMULATED_RECEPTOR_CARRIER_IDS,
        values=frame.contact_values,
    )


@dataclass(frozen=True, slots=True)
class SimulatedWorldMCMPathObservation:
    start_position: int
    delta: int
    cause: str
    next_position: int
    provenance_digest: str
    simulated_receptor_digest: str
    adapted_receptor_digest: str
    field_window_digest: str
    constellation_digest: str
    simulated_to_adapter_lossless: bool
    adapter_to_field_lossless: bool
    afterimage_is_zero: bool
    distributed_state_equal: bool
    carrier_count: int

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class SimulatedWorldMCMCausePair:
    start_position: int
    delta: int
    provenance_distinct: bool
    simulated_receptor_equal: bool
    adapted_receptor_equal: bool
    field_window_equal: bool
    constellation_equal: bool

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}


@dataclass(frozen=True, slots=True)
class SimulatedWorldMCMPathResult:
    observations: tuple[SimulatedWorldMCMPathObservation, ...]
    cause_pairs: tuple[SimulatedWorldMCMCausePair, ...]
    all_simulated_to_adapter_lossless: bool
    all_adapter_to_field_lossless: bool
    all_afterimages_zero: bool
    all_distributor_states_equal: bool
    all_carrier_counts_seven: bool
    all_cause_pairs_collapse_after_provenance: bool
    wrap_targets_correct: bool
    adapter_roles_cause_free: bool
    observer_is_neutral: bool
    order_is_neutral: bool
    ring_topology_preserved: bool = False
    writes_back: bool = False
    field_rule_released: bool = False

    def __post_init__(self) -> None:
        if self.ring_topology_preserved:
            raise SimulatedWorldMCMPathError(
                "the line field cannot claim preserved ring topology"
            )
        if self.writes_back or self.field_rule_released:
            raise SimulatedWorldMCMPathError(
                "the passive path cannot write back or release a field rule"
            )
        if len(self.observations) != 42 or len(self.cause_pairs) != 21:
            raise SimulatedWorldMCMPathError(
                "result must contain every preregistered branch and pair"
            )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "observations": [item.canonical_payload() for item in self.observations],
            "cause_pairs": [item.canonical_payload() for item in self.cause_pairs],
            "all_simulated_to_adapter_lossless": (
                self.all_simulated_to_adapter_lossless
            ),
            "all_adapter_to_field_lossless": self.all_adapter_to_field_lossless,
            "all_afterimages_zero": self.all_afterimages_zero,
            "all_distributor_states_equal": self.all_distributor_states_equal,
            "all_carrier_counts_seven": self.all_carrier_counts_seven,
            "all_cause_pairs_collapse_after_provenance": (
                self.all_cause_pairs_collapse_after_provenance
            ),
            "wrap_targets_correct": self.wrap_targets_correct,
            "adapter_roles_cause_free": self.adapter_roles_cause_free,
            "observer_is_neutral": self.observer_is_neutral,
            "order_is_neutral": self.order_is_neutral,
            "ring_topology_preserved": self.ring_topology_preserved,
            "writes_back": self.writes_back,
            "field_rule_released": self.field_rule_released,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _validated_order(
    values: Iterable[object],
    expected: tuple[object, ...],
    role: str,
) -> tuple[object, ...]:
    result = tuple(values)
    if len(result) != len(expected) or set(result) != set(expected):
        raise SimulatedWorldMCMPathError(
            f"{role} must contain each preregistered value exactly once"
        )
    return result


def _fresh_field(reference: ReceptorContactFrame):
    return build_receptor_aligned_mcm_field(
        reference,
        positions=tuple((position,) for position in WORLD_POSITIONS),
        sample_offsets=((-1,), (1,)),
        dock_id="simulated",
        layer_id="simulated.layer",
        field_id="simulated.field",
        field_geometry_id="simulated.field.line7.v1",
    )


def _observe_branch(
    start_position: int,
    delta: int,
    cause: InterventionCause,
) -> SimulatedWorldMCMPathObservation:
    transition = advance_simulated_world(
        SimulatedWorldState(tick=0, position=start_position),
        WorldIntervention(source_tick=0, delta=delta, cause=cause),
    )
    simulated_receptor = receptor_frame_from_world(transition.next_world)
    receptor = simulated_world_receptor_to_contact_frame(simulated_receptor)
    field_time = CommonFieldTime(
        clock_id="organism.simulated",
        window_start_tick=simulated_receptor.source_tick,
        window_end_tick=simulated_receptor.source_tick + 1,
    )
    current = _fresh_field(receptor).advance(
        receptor,
        field_time,
        receptor_projection_baseline,
    )
    window = current.field_window()
    distributor = MCMDistributor()
    distributor.attach(current.distributor_dock())
    constellation = distributor.distribute((window,))
    adapted_digest = _digest(_receptor_payload(receptor))
    return SimulatedWorldMCMPathObservation(
        start_position=start_position,
        delta=delta,
        cause=cause.value,
        next_position=transition.next_world.position,
        provenance_digest=transition.provenance_digest(),
        simulated_receptor_digest=simulated_receptor.digest(),
        adapted_receptor_digest=adapted_digest,
        field_window_digest=window.digest(),
        constellation_digest=constellation.digest(),
        simulated_to_adapter_lossless=(
            simulated_receptor.contact_values == receptor.values
        ),
        adapter_to_field_lossless=(receptor.values == window.activation),
        afterimage_is_zero=(window.afterimage == (0.0,) * 7),
        distributed_state_equal=(
            len(constellation.states) == 1
            and constellation.states[0].digest() == window.digest()
        ),
        carrier_count=len(window.carrier_ids),
    )


def run_simulated_world_mcm_path_probe(
    *,
    position_order: Iterable[int] = WORLD_POSITIONS,
    delta_order: Iterable[int] = WORLD_DELTAS,
    cause_order: Iterable[InterventionCause] = WORLD_CAUSES,
    observer: PathObserver | None = None,
    _verify_controls: bool = True,
) -> SimulatedWorldMCMPathResult:
    """Run the fixed cause-neutral projection path from Methodik 031."""

    position_order = _validated_order(
        position_order,
        WORLD_POSITIONS,
        "position_order",
    )
    delta_order = _validated_order(delta_order, WORLD_DELTAS, "delta_order")
    try:
        normalized_causes = tuple(InterventionCause(value) for value in cause_order)
    except (TypeError, ValueError) as exc:
        raise SimulatedWorldMCMPathError("cause_order contains an unknown cause") from exc
    cause_order = _validated_order(normalized_causes, WORLD_CAUSES, "cause_order")

    observations = []
    for position in position_order:
        for delta in delta_order:
            for cause in cause_order:
                observation = _observe_branch(int(position), int(delta), cause)
                before = observation.digest()
                if observer is not None:
                    observer(observation)
                if observation.digest() != before:
                    raise SimulatedWorldMCMPathError(
                        "observer changed an immutable path observation"
                    )
                observations.append(observation)

    canonical_observations = tuple(
        sorted(
            observations,
            key=lambda item: (item.start_position, item.delta, item.cause),
        )
    )
    by_key = {
        (item.start_position, item.delta, item.cause): item
        for item in canonical_observations
    }
    cause_pairs = []
    for position in WORLD_POSITIONS:
        for delta in WORLD_DELTAS:
            external = by_key[(position, delta, "external")]
            effector = by_key[(position, delta, "effector")]
            cause_pairs.append(
                SimulatedWorldMCMCausePair(
                    start_position=position,
                    delta=delta,
                    provenance_distinct=(
                        external.provenance_digest != effector.provenance_digest
                    ),
                    simulated_receptor_equal=(
                        external.simulated_receptor_digest
                        == effector.simulated_receptor_digest
                    ),
                    adapted_receptor_equal=(
                        external.adapted_receptor_digest
                        == effector.adapted_receptor_digest
                    ),
                    field_window_equal=(
                        external.field_window_digest
                        == effector.field_window_digest
                    ),
                    constellation_equal=(
                        external.constellation_digest
                        == effector.constellation_digest
                    ),
                )
            )

    forbidden_roles = {"cause", "delta", "effort", "provenance_digest"}
    transported_roles = set(ReceptorContactFrame.__dataclass_fields__) | set(
        MCMFieldWindow.__dataclass_fields__
    )
    pairs_collapse = all(
        pair.provenance_distinct
        and pair.simulated_receptor_equal
        and pair.adapted_receptor_equal
        and pair.field_window_equal
        and pair.constellation_equal
        for pair in cause_pairs
    )
    wrap_targets = {
        (item.start_position, item.delta, item.next_position)
        for item in canonical_observations
        if (item.start_position, item.delta) in ((0, -1), (6, 1))
    }
    provisional = SimulatedWorldMCMPathResult(
        observations=canonical_observations,
        cause_pairs=tuple(cause_pairs),
        all_simulated_to_adapter_lossless=all(
            item.simulated_to_adapter_lossless for item in canonical_observations
        ),
        all_adapter_to_field_lossless=all(
            item.adapter_to_field_lossless for item in canonical_observations
        ),
        all_afterimages_zero=all(
            item.afterimage_is_zero for item in canonical_observations
        ),
        all_distributor_states_equal=all(
            item.distributed_state_equal for item in canonical_observations
        ),
        all_carrier_counts_seven=all(
            item.carrier_count == 7 for item in canonical_observations
        ),
        all_cause_pairs_collapse_after_provenance=pairs_collapse,
        wrap_targets_correct=(
            wrap_targets == {(0, -1, 6), (6, 1, 0)}
        ),
        adapter_roles_cause_free=forbidden_roles.isdisjoint(transported_roles),
        observer_is_neutral=False,
        order_is_neutral=False,
    )
    if not _verify_controls:
        return provisional

    reference = run_simulated_world_mcm_path_probe(_verify_controls=False)
    passive_observer = run_simulated_world_mcm_path_probe(
        observer=lambda observation: None,
        _verify_controls=False,
    )
    reversed_order = run_simulated_world_mcm_path_probe(
        position_order=reversed(WORLD_POSITIONS),
        delta_order=reversed(WORLD_DELTAS),
        cause_order=reversed(WORLD_CAUSES),
        _verify_controls=False,
    )
    current_digest = provisional.digest()
    reference_digest = reference.digest()
    return replace(
        provisional,
        observer_is_neutral=(
            current_digest == reference_digest == passive_observer.digest()
        ),
        order_is_neutral=(
            current_digest == reference_digest == reversed_order.digest()
        ),
    )


def simulated_world_mcm_path_public_roles(
) -> tuple[tuple[str, ...], ...]:
    classes = (
        SimulatedWorldMCMPathObservation,
        SimulatedWorldMCMCausePair,
        SimulatedWorldMCMPathResult,
    )
    return tuple(tuple(item.name for item in fields(cls)) for cls in classes)
