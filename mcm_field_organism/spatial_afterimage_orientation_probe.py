"""Passive probe for trajectory information in a spatial afterimage field."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .carrier_baselines import BaselineValidationError, CarrierFrame, run_independent_history
from .local_neuron_function_probe import observe_local_mcm_function
from .mcm_neuron import MCMFieldPerception, MCMFieldSample, MCMNeuron
from .mcm_neuron_layer import MCMNeuronDrive


@dataclass(frozen=True, slots=True)
class SpatialAfterimageSnapshot:
    """One center-local readout of a completed passive carrier frame."""

    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    center_activation: float
    center_afterimage: float
    left_afterimage: float
    right_afterimage: float
    spatial_orientation: float


@dataclass(frozen=True, slots=True)
class SpatialAfterimageOrientationResult:
    """Matched mirrored histories before and after passive relaxation."""

    width: int
    center_index: int
    pause_steps: int
    forward_contacts: tuple[tuple[float, ...], ...]
    reverse_contacts: tuple[tuple[float, ...], ...]
    forward_endpoint: SpatialAfterimageSnapshot
    reverse_endpoint: SpatialAfterimageSnapshot
    forward_relaxed: SpatialAfterimageSnapshot
    reverse_relaxed: SpatialAfterimageSnapshot
    reset: SpatialAfterimageSnapshot


def _contact(width: int, index: int, amplitude: float) -> tuple[float, ...]:
    return tuple(amplitude if position == index else 0.0 for position in range(width))


def _snapshot(frame: CarrierFrame, center: int, tick: int) -> SpatialAfterimageSnapshot:
    previous = MCMNeuron(
        neuron_id="n.center",
        field_id="probe.spatial",
        modality_id="probe",
        geometry_id="line.local.v1",
        position=(center,),
        activation=frame.activation[center],
        afterimage=frame.afterimage[center],
        perception=MCMFieldPerception(
            tick=tick,
            receptor_contact=None,
            local_samples=(),
        ),
    )
    samples = tuple(
        MCMFieldSample(
            sample_id=f"sample.n{position}",
            source_field_id="probe.spatial",
            source_tick=tick,
            relative_position=(position - center,),
            activation=frame.activation[position],
            afterimage=frame.afterimage[position],
        )
        for position in (center - 1, center + 1)
    )
    observation = observe_local_mcm_function(
        MCMNeuronDrive(
            previous=previous,
            perception=MCMFieldPerception(
                tick=tick + 1,
                receptor_contact=0.0,
                local_samples=samples,
            ),
        )
    )
    differences = {
        item.relative_position: item.afterimage_difference
        for item in observation.pair_differences
    }
    orientation = differences[(1,)] - differences[(-1,)]
    return SpatialAfterimageSnapshot(
        activation=frame.activation,
        afterimage=frame.afterimage,
        center_activation=frame.activation[center],
        center_afterimage=frame.afterimage[center],
        left_afterimage=frame.afterimage[center - 1],
        right_afterimage=frame.afterimage[center + 1],
        spatial_orientation=orientation,
    )


def run_spatial_afterimage_orientation_probe(
    *,
    width: int = 5,
    amplitude: float = 1.0,
    dt: float = 1.0,
    tau: float = 2.0,
    pause_steps: int = 2,
) -> SpatialAfterimageOrientationResult:
    """Compare mirrored three-contact trajectories using the unchanged B1 trace."""

    if isinstance(width, bool) or not isinstance(width, int) or width < 5 or width % 2 == 0:
        raise BaselineValidationError("width must be an odd integer of at least five")
    try:
        amplitude = float(amplitude)
    except (TypeError, ValueError) as exc:
        raise BaselineValidationError("amplitude must be numeric") from exc
    if not math.isfinite(amplitude) or amplitude <= 0.0 or amplitude > 1.0:
        raise BaselineValidationError("amplitude must be within the 0..1 probe domain")
    if isinstance(pause_steps, bool) or not isinstance(pause_steps, int) or pause_steps < 0:
        raise BaselineValidationError("pause_steps must be a non-negative integer")

    center = width // 2
    forward_positions = (center - 2, center - 1, center)
    reverse_positions = (center + 2, center + 1, center)
    forward_contacts = tuple(_contact(width, index, amplitude) for index in forward_positions)
    reverse_contacts = tuple(_contact(width, index, amplitude) for index in reverse_positions)
    silence = (_contact(width, center, 0.0),) * pause_steps

    forward_frames = run_independent_history(
        forward_contacts + silence,
        dt=dt,
        tau=tau,
    )
    reverse_frames = run_independent_history(
        reverse_contacts + silence,
        dt=dt,
        tau=tau,
    )
    endpoint_tick = len(forward_contacts) - 1
    relaxed_tick = len(forward_frames) - 1
    zero_frame = CarrierFrame(
        activation=(0.0,) * width,
        afterimage=(0.0,) * width,
    )
    return SpatialAfterimageOrientationResult(
        width=width,
        center_index=center,
        pause_steps=pause_steps,
        forward_contacts=forward_contacts,
        reverse_contacts=reverse_contacts,
        forward_endpoint=_snapshot(forward_frames[endpoint_tick], center, endpoint_tick),
        reverse_endpoint=_snapshot(reverse_frames[endpoint_tick], center, endpoint_tick),
        forward_relaxed=_snapshot(forward_frames[relaxed_tick], center, relaxed_tick),
        reverse_relaxed=_snapshot(reverse_frames[relaxed_tick], center, relaxed_tick),
        reset=_snapshot(zero_frame, center, relaxed_tick),
    )
