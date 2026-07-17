"""Passive Methodik-027 probe for causal inertia of local field samples."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from typing import Callable, Iterable

from .local_neuron_function_probe import observe_local_mcm_function
from .mcm_neuron import MCMFieldPerception, MCMFieldSample, MCMNeuron
from .mcm_neuron_layer import (
    MCMNeuronDrive,
    advance_mcm_neuron,
    hold_state_baseline,
    receptor_projection_baseline,
)
from .spatial_afterimage_orientation_probe import (
    SpatialAfterimageSnapshot,
    run_spatial_afterimage_orientation_probe,
)


class LocalFieldInertiaProbeError(ValueError):
    """Raised when the preregistered inertia probe is changed or invalid."""


FIELD_INERTIA_AMPLITUDES = (0.25, 0.5, 1.0)
FIELD_INERTIA_TAUS = (1.0, 2.0, 4.0)
FIELD_INERTIA_PAUSE_STEPS = (0, 1, 3)
FIELD_INERTIA_BRANCH_IDS = ("forward", "reverse")

InertiaObserver = Callable[["LocalFieldInertiaObservation"], object]


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True, slots=True)
class LocalFieldInertiaObservation:
    amplitude: float
    tau: float
    pause_steps: int
    branch_id: str
    passive_orientation: float
    previous_digest: str
    perception_digest: str
    hold_activation: float
    hold_afterimage: float
    hold_output_digest: str
    hold_neuron_digest: str
    projection_activation: float
    projection_afterimage: float
    projection_output_digest: str
    projection_neuron_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {item.name: getattr(self, item.name) for item in fields(self)}

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class LocalFieldInertiaResult:
    observations: tuple[LocalFieldInertiaObservation, ...]
    all_previous_centers_equal: bool
    all_perceptions_distinct: bool
    all_orientations_mirrored: bool
    all_hold_outputs_collide: bool
    all_projection_outputs_collide: bool
    all_next_neuron_provenance_distinct: bool
    all_resets_neutral: bool
    max_hold_activation_difference: float
    max_hold_afterimage_difference: float
    max_projection_activation_difference: float
    max_projection_afterimage_difference: float
    writes_back: bool = False
    mechanism_released: bool = False

    def __post_init__(self) -> None:
        if self.writes_back or self.mechanism_released:
            raise LocalFieldInertiaProbeError(
                "a passive inertia result cannot write back or release a mechanism"
            )
        expected = (
            len(FIELD_INERTIA_AMPLITUDES)
            * len(FIELD_INERTIA_TAUS)
            * len(FIELD_INERTIA_PAUSE_STEPS)
            * len(FIELD_INERTIA_BRANCH_IDS)
        )
        if len(self.observations) != expected:
            raise LocalFieldInertiaProbeError(
                "result must contain every preregistered branch"
            )

    @property
    def parameter_pair_count(self) -> int:
        return len(self.observations) // 2

    def canonical_payload(self) -> dict[str, object]:
        return {
            "observations": [
                observation.canonical_payload()
                for observation in self.observations
            ],
            "all_previous_centers_equal": self.all_previous_centers_equal,
            "all_perceptions_distinct": self.all_perceptions_distinct,
            "all_orientations_mirrored": self.all_orientations_mirrored,
            "all_hold_outputs_collide": self.all_hold_outputs_collide,
            "all_projection_outputs_collide": self.all_projection_outputs_collide,
            "all_next_neuron_provenance_distinct": (
                self.all_next_neuron_provenance_distinct
            ),
            "all_resets_neutral": self.all_resets_neutral,
            "max_hold_activation_difference": (
                self.max_hold_activation_difference
            ),
            "max_hold_afterimage_difference": (
                self.max_hold_afterimage_difference
            ),
            "max_projection_activation_difference": (
                self.max_projection_activation_difference
            ),
            "max_projection_afterimage_difference": (
                self.max_projection_afterimage_difference
            ),
            "writes_back": self.writes_back,
            "mechanism_released": self.mechanism_released,
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
        raise LocalFieldInertiaProbeError(
            f"{role} must contain each preregistered value exactly once"
        )
    return result


def _drive(
    snapshot: SpatialAfterimageSnapshot,
    *,
    center_index: int,
    source_tick: int,
) -> MCMNeuronDrive:
    previous = MCMNeuron(
        neuron_id="n.center",
        field_id="probe.inertia",
        modality_id="probe",
        geometry_id="line.local.v1",
        position=(center_index,),
        activation=snapshot.center_activation,
        afterimage=snapshot.center_afterimage,
        perception=MCMFieldPerception(
            tick=source_tick,
            receptor_contact=None,
            local_samples=(),
        ),
    )
    samples = tuple(
        MCMFieldSample(
            sample_id=f"sample.offset{offset}",
            source_field_id="probe.inertia",
            source_tick=source_tick,
            relative_position=(offset,),
            activation=snapshot.activation[center_index + offset],
            afterimage=snapshot.afterimage[center_index + offset],
        )
        for offset in (-1, 1)
    )
    return MCMNeuronDrive(
        previous=previous,
        perception=MCMFieldPerception(
            tick=source_tick + 1,
            receptor_contact=0.0,
            local_samples=samples,
        ),
    )


def _passive_orientation(drive: MCMNeuronDrive) -> float:
    observed = observe_local_mcm_function(drive)
    differences = {
        item.relative_position: item.afterimage_difference
        for item in observed.pair_differences
    }
    return differences[(1,)] - differences[(-1,)]


def _output_digest(activation: float, afterimage: float) -> str:
    return _digest({"activation": activation, "afterimage": afterimage})


def _observe_branch(
    snapshot: SpatialAfterimageSnapshot,
    *,
    amplitude: float,
    tau: float,
    pause_steps: int,
    branch_id: str,
    center_index: int,
) -> LocalFieldInertiaObservation:
    source_tick = 2 + pause_steps
    drive = _drive(
        snapshot,
        center_index=center_index,
        source_tick=source_tick,
    )
    hold_next = advance_mcm_neuron(
        drive.previous,
        drive.perception,
        hold_state_baseline,
    )
    projection_next = advance_mcm_neuron(
        drive.previous,
        drive.perception,
        receptor_projection_baseline,
    )
    return LocalFieldInertiaObservation(
        amplitude=amplitude,
        tau=tau,
        pause_steps=pause_steps,
        branch_id=branch_id,
        passive_orientation=_passive_orientation(drive),
        previous_digest=drive.previous.digest(),
        perception_digest=_digest(drive.perception.canonical_payload()),
        hold_activation=hold_next.activation,
        hold_afterimage=hold_next.afterimage,
        hold_output_digest=_output_digest(
            hold_next.activation,
            hold_next.afterimage,
        ),
        hold_neuron_digest=hold_next.digest(),
        projection_activation=projection_next.activation,
        projection_afterimage=projection_next.afterimage,
        projection_output_digest=_output_digest(
            projection_next.activation,
            projection_next.afterimage,
        ),
        projection_neuron_digest=projection_next.digest(),
    )


def _pairs(
    observations: tuple[LocalFieldInertiaObservation, ...],
) -> tuple[
    tuple[LocalFieldInertiaObservation, LocalFieldInertiaObservation],
    ...,
]:
    result = []
    for amplitude in FIELD_INERTIA_AMPLITUDES:
        for tau in FIELD_INERTIA_TAUS:
            for pause_steps in FIELD_INERTIA_PAUSE_STEPS:
                pair = tuple(
                    observation
                    for observation in observations
                    if observation.amplitude == amplitude
                    and observation.tau == tau
                    and observation.pause_steps == pause_steps
                )
                forward = next(
                    item for item in pair if item.branch_id == "forward"
                )
                reverse = next(
                    item for item in pair if item.branch_id == "reverse"
                )
                result.append((forward, reverse))
    return tuple(result)


def run_local_field_inertia_probe(
    *,
    amplitude_order: Iterable[float] = FIELD_INERTIA_AMPLITUDES,
    tau_order: Iterable[float] = FIELD_INERTIA_TAUS,
    pause_order: Iterable[int] = FIELD_INERTIA_PAUSE_STEPS,
    branch_order: Iterable[str] = FIELD_INERTIA_BRANCH_IDS,
    observer: InertiaObserver | None = None,
) -> LocalFieldInertiaResult:
    """Run existing transitions against mirrored, locally readable field states."""

    amplitude_order = _validated_order(
        amplitude_order,
        FIELD_INERTIA_AMPLITUDES,
        "amplitude_order",
    )
    tau_order = _validated_order(tau_order, FIELD_INERTIA_TAUS, "tau_order")
    pause_order = _validated_order(
        pause_order,
        FIELD_INERTIA_PAUSE_STEPS,
        "pause_order",
    )
    branch_order = _validated_order(
        branch_order,
        FIELD_INERTIA_BRANCH_IDS,
        "branch_order",
    )

    observations = []
    resets_neutral = True
    for amplitude in amplitude_order:
        for tau in tau_order:
            for pause_steps in pause_order:
                spatial = run_spatial_afterimage_orientation_probe(
                    amplitude=float(amplitude),
                    tau=float(tau),
                    pause_steps=int(pause_steps),
                )
                snapshots = {
                    "forward": spatial.forward_relaxed,
                    "reverse": spatial.reverse_relaxed,
                }
                for branch_id in branch_order:
                    observation = _observe_branch(
                        snapshots[str(branch_id)],
                        amplitude=float(amplitude),
                        tau=float(tau),
                        pause_steps=int(pause_steps),
                        branch_id=str(branch_id),
                        center_index=spatial.center_index,
                    )
                    before = observation.digest()
                    if observer is not None:
                        observer(observation)
                    if observation.digest() != before:
                        raise LocalFieldInertiaProbeError(
                            "observer changed an immutable inertia observation"
                        )
                    observations.append(observation)

                reset_drive = _drive(
                    spatial.reset,
                    center_index=spatial.center_index,
                    source_tick=2 + int(pause_steps),
                )
                reset_hold = hold_state_baseline(reset_drive)
                reset_projection = receptor_projection_baseline(reset_drive)
                resets_neutral = resets_neutral and (
                    _passive_orientation(reset_drive) == 0.0
                    and reset_hold.activation == 0.0
                    and reset_hold.afterimage == 0.0
                    and reset_projection.activation == 0.0
                    and reset_projection.afterimage == 0.0
                )

    canonical = tuple(
        sorted(
            observations,
            key=lambda item: (
                item.amplitude,
                item.tau,
                item.pause_steps,
                item.branch_id,
            ),
        )
    )
    pairs = _pairs(canonical)
    hold_activation_differences = tuple(
        abs(forward.hold_activation - reverse.hold_activation)
        for forward, reverse in pairs
    )
    hold_afterimage_differences = tuple(
        abs(forward.hold_afterimage - reverse.hold_afterimage)
        for forward, reverse in pairs
    )
    projection_activation_differences = tuple(
        abs(forward.projection_activation - reverse.projection_activation)
        for forward, reverse in pairs
    )
    projection_afterimage_differences = tuple(
        abs(forward.projection_afterimage - reverse.projection_afterimage)
        for forward, reverse in pairs
    )
    return LocalFieldInertiaResult(
        observations=canonical,
        all_previous_centers_equal=all(
            forward.previous_digest == reverse.previous_digest
            for forward, reverse in pairs
        ),
        all_perceptions_distinct=all(
            forward.perception_digest != reverse.perception_digest
            for forward, reverse in pairs
        ),
        all_orientations_mirrored=all(
            forward.passive_orientation < 0.0
            and reverse.passive_orientation > 0.0
            and math.isclose(
                forward.passive_orientation,
                -reverse.passive_orientation,
                rel_tol=1e-12,
                abs_tol=1e-15,
            )
            for forward, reverse in pairs
        ),
        all_hold_outputs_collide=all(
            forward.hold_output_digest == reverse.hold_output_digest
            for forward, reverse in pairs
        ),
        all_projection_outputs_collide=all(
            forward.projection_output_digest
            == reverse.projection_output_digest
            for forward, reverse in pairs
        ),
        all_next_neuron_provenance_distinct=all(
            forward.hold_neuron_digest != reverse.hold_neuron_digest
            and forward.projection_neuron_digest
            != reverse.projection_neuron_digest
            for forward, reverse in pairs
        ),
        all_resets_neutral=resets_neutral,
        max_hold_activation_difference=max(hold_activation_differences),
        max_hold_afterimage_difference=max(hold_afterimage_differences),
        max_projection_activation_difference=max(
            projection_activation_differences
        ),
        max_projection_afterimage_difference=max(
            projection_afterimage_differences
        ),
    )


def local_field_inertia_public_roles(
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(item.name for item in fields(LocalFieldInertiaObservation)),
        tuple(item.name for item in fields(LocalFieldInertiaResult)),
    )
