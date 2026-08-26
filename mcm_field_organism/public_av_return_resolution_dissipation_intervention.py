"""Preregistered content-neutral dissipation intervention for the AV return tail."""

from __future__ import annotations

from dataclasses import dataclass, replace
import math
from pathlib import Path

from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import NeutralFastAfterimageConfig, NeutralLocalFieldSubstrateConfig
from .public_av_return_replication_execution import _advance_contact_free
from .public_av_return_resolution_curve import ARM_IDS, _independent_arm_start_field, _shift_sequences
from .public_av_return_resolution_mode_audit import _mode_metrics
from .public_av_return_resolution_tail import TAIL_RESOLUTION_DURATION_TICKS
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract
from .shared_field_component_intervention import intervene_shared_field_component
from .shared_mcm_field import SharedMCMField


# Fixed before execution. The positive rates correspond to 20 s and 10 s time constants.
DISSIPATION_LEAK_RATES_PER_SECOND = (0.0, 0.05, 0.10)


class PublicAVReturnResolutionDissipationError(ValueError):
    pass


def _apply_content_neutral_leak(
    field: SharedMCMField,
    leak_rate_per_second: float,
    elapsed_seconds: float,
) -> SharedMCMField:
    """Apply the exact local solution of dx/dt = -leak*x to both field components."""

    if not isinstance(field, SharedMCMField):
        raise PublicAVReturnResolutionDissipationError("leak requires a shared field")
    rate = float(leak_rate_per_second)
    elapsed = float(elapsed_seconds)
    if rate not in DISSIPATION_LEAK_RATES_PER_SECOND:
        raise PublicAVReturnResolutionDissipationError("leak rate was not preregistered")
    if not math.isfinite(elapsed) or elapsed < 0.0:
        raise PublicAVReturnResolutionDissipationError("elapsed seconds must be finite and nonnegative")
    if rate == 0.0 or elapsed == 0.0:
        return field
    factor = math.exp(-rate * elapsed)
    neurons = tuple(
        replace(
            neuron,
            activation=neuron.activation * factor,
            afterimage=neuron.afterimage * factor,
        )
        for neuron in field.layer.neurons
    )
    return replace(field, layer=replace(field.layer, neurons=neurons))


@dataclass(frozen=True, slots=True)
class PublicAVReturnResolutionDissipationPoint:
    leak_rate_per_second: float
    resolution_duration_ticks: int
    stage_one_event_count: int
    stage_two_event_count: int
    arm_ids: tuple[str, ...]
    activation_mean_delta_to_fresh: tuple[float, ...]
    afterimage_mean_delta_to_fresh: tuple[float, ...]
    activation_centered_linf_to_fresh: tuple[float, ...]
    afterimage_centered_linf_to_fresh: tuple[float, ...]
    activation_constant_energy_fraction: tuple[float, ...]
    afterimage_constant_energy_fraction: tuple[float, ...]
    layer_digests: tuple[str, ...]
    snapshot_digests: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.leak_rate_per_second not in DISSIPATION_LEAK_RATES_PER_SECOND:
            raise PublicAVReturnResolutionDissipationError("point leak rate was not preregistered")
        if self.resolution_duration_ticks not in TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVReturnResolutionDissipationError("point duration was not preregistered")
        if tuple(self.arm_ids) != ARM_IDS:
            raise PublicAVReturnResolutionDissipationError("point requires the four fixed arms")
        vectors = (
            self.activation_mean_delta_to_fresh,
            self.afterimage_mean_delta_to_fresh,
            self.activation_centered_linf_to_fresh,
            self.afterimage_centered_linf_to_fresh,
            self.activation_constant_energy_fraction,
            self.afterimage_constant_energy_fraction,
            self.layer_digests,
            self.snapshot_digests,
        )
        if any(len(vector) != len(ARM_IDS) for vector in vectors):
            raise PublicAVReturnResolutionDissipationError("all point measurements must align")


@dataclass(frozen=True, slots=True)
class PublicAVReturnResolutionDissipationIntervention:
    experiment_id: str
    source_id: str
    clock_id: str
    leak_rates_per_second: tuple[float, ...]
    resolution_duration_ticks: tuple[int, ...]
    points: tuple[PublicAVReturnResolutionDissipationPoint, ...]
    intervention_scope: str = "contact_free_local_activation_and_afterimage"
    threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if tuple(self.leak_rates_per_second) != DISSIPATION_LEAK_RATES_PER_SECOND:
            raise PublicAVReturnResolutionDissipationError("leak-rate axis changed")
        if tuple(self.resolution_duration_ticks) != TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVReturnResolutionDissipationError("duration axis changed")
        expected = tuple(
            (rate, duration)
            for rate in DISSIPATION_LEAK_RATES_PER_SECOND
            for duration in TAIL_RESOLUTION_DURATION_TICKS
        )
        actual = tuple((point.leak_rate_per_second, point.resolution_duration_ticks) for point in self.points)
        if actual != expected:
            raise PublicAVReturnResolutionDissipationError("points do not cover fixed rate-duration axis")
        if self.intervention_scope != "contact_free_local_activation_and_afterimage":
            raise PublicAVReturnResolutionDissipationError("intervention scope changed")
        if any((self.threshold_defined, self.memory_claim_allowed, self.meaning_claim_allowed,
                self.organization_claim_allowed, self.ai_claim_allowed)):
            raise PublicAVReturnResolutionDissipationError("intervention cannot release claims")


def execute_public_av_return_resolution_dissipation_intervention(
    path: Path,
    contract: PublicMediaSourceContract,
) -> PublicAVReturnResolutionDissipationIntervention:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVReturnResolutionDissipationError("audited media file is required")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVReturnResolutionDissipationError("public media source contract is required")

    sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    stage_one = run_neutral_asynchronous_field(
        _fresh_field(sequences), sequences, _steps(sequences, 0, 500_000_000), substrate,
        afterimage_config=afterimage,
    )
    points = []
    for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
        for duration in TAIL_RESOLUTION_DURATION_TICKS:
            start_tick = 500_000_000 + duration
            shifted = _shift_sequences(sequences, start_tick)
            fields = []
            stage_two_count = 0
            for arm_id in ARM_IDS:
                start_field = _independent_arm_start_field(
                    stage_one.field, arm_id, lambda: _fresh_field(sequences)
                )
                if arm_id != "return.fresh_stage_two":
                    start_field = _advance_contact_free(
                        start_field, 500_000_000, start_tick, substrate, afterimage
                    )
                    start_field = _apply_content_neutral_leak(
                        start_field, rate, duration / 1_000_000_000
                    )
                    if arm_id == "control.activation_only_carry":
                        start_field = intervene_shared_field_component(
                            start_field, "reset_afterimage_preserve_activation"
                        ).field
                    elif arm_id == "control.afterimage_only_carry":
                        start_field = intervene_shared_field_component(
                            start_field, "reset_activation_preserve_afterimage"
                        ).field
                stage_two = run_neutral_asynchronous_field(
                    start_field, shifted, _steps(shifted, start_tick, start_tick + 500_000_000),
                    substrate, afterimage_config=afterimage,
                )
                stage_two_count = stage_two.source_support_count
                fields.append(stage_two.field)

            fresh_activation = tuple(neuron.activation for neuron in fields[-1].layer.neurons)
            fresh_afterimage = tuple(neuron.afterimage for neuron in fields[-1].layer.neurons)
            activation_metrics = tuple(_mode_metrics(
                tuple(neuron.activation for neuron in field.layer.neurons), fresh_activation
            ) for field in fields)
            afterimage_metrics = tuple(_mode_metrics(
                tuple(neuron.afterimage for neuron in field.layer.neurons), fresh_afterimage
            ) for field in fields)
            points.append(PublicAVReturnResolutionDissipationPoint(
                rate, duration, stage_one.source_support_count, stage_two_count, ARM_IDS,
                tuple(item[0] for item in activation_metrics),
                tuple(item[0] for item in afterimage_metrics),
                tuple(item[1] for item in activation_metrics),
                tuple(item[1] for item in afterimage_metrics),
                tuple(item[2] for item in activation_metrics),
                tuple(item[2] for item in afterimage_metrics),
                tuple(field.layer.digest() for field in fields),
                tuple(field.snapshot().digest() for field in fields),
            ))

    return PublicAVReturnResolutionDissipationIntervention(
        "public.av.nasa-earthrise.return-resolution-dissipation-intervention.v1",
        contract.source_id,
        sequences[0].clock_id,
        DISSIPATION_LEAK_RATES_PER_SECOND,
        TAIL_RESOLUTION_DURATION_TICKS,
        tuple(points),
    )


def public_av_return_resolution_dissipation_to_jsonable(
    result: PublicAVReturnResolutionDissipationIntervention,
) -> dict[str, object]:
    return {
        "experiment_id": result.experiment_id,
        "source_id": result.source_id,
        "clock_id": result.clock_id,
        "leak_rates_per_second": list(result.leak_rates_per_second),
        "resolution_duration_ticks": list(result.resolution_duration_ticks),
        "intervention_scope": result.intervention_scope,
        "points": [
            {
                "leak_rate_per_second": point.leak_rate_per_second,
                "resolution_duration_ticks": point.resolution_duration_ticks,
                "stage_one_event_count": point.stage_one_event_count,
                "stage_two_event_count": point.stage_two_event_count,
                "arm_ids": list(point.arm_ids),
                "activation_mean_delta_to_fresh": list(point.activation_mean_delta_to_fresh),
                "afterimage_mean_delta_to_fresh": list(point.afterimage_mean_delta_to_fresh),
                "activation_centered_linf_to_fresh": list(point.activation_centered_linf_to_fresh),
                "afterimage_centered_linf_to_fresh": list(point.afterimage_centered_linf_to_fresh),
                "activation_constant_energy_fraction": list(point.activation_constant_energy_fraction),
                "afterimage_constant_energy_fraction": list(point.afterimage_constant_energy_fraction),
                "layer_digests": list(point.layer_digests),
                "snapshot_digests": list(point.snapshot_digests),
            } for point in result.points
        ],
        "threshold_defined": result.threshold_defined,
        "memory_claim_allowed": result.memory_claim_allowed,
        "meaning_claim_allowed": result.meaning_claim_allowed,
        "organization_claim_allowed": result.organization_claim_allowed,
        "ai_claim_allowed": result.ai_claim_allowed,
    }
