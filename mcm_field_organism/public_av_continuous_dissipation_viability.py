"""Preregistered viability audit for continuous content-neutral field dissipation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .field_step_time import MCMFieldStepTime
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralFieldDissipationConfig,
    NeutralLocalFieldSubstrateConfig,
    advance_neutral_fast_shared_field,
)
from .public_av_return_resolution_curve import ARM_IDS, _independent_arm_start_field, _shift_sequences
from .public_av_return_resolution_dissipation_intervention import DISSIPATION_LEAK_RATES_PER_SECOND
from .public_av_return_resolution_mode_audit import _mode_metrics
from .public_av_return_resolution_tail import TAIL_RESOLUTION_DURATION_TICKS
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_av_container_source import PUBLIC_MEDIA_TICKS_PER_SECOND
from .public_media_source_contract import PublicMediaSourceContract
from .receptor_contract import CommonFieldTime
from .receptor_distributor import ReceptorDistribution
from .shared_field_component_intervention import intervene_shared_field_component


class PublicAVContinuousDissipationViabilityError(ValueError):
    pass


def _continuous_gap(field, start_tick, end_tick, substrate, afterimage, dissipation):
    return advance_neutral_fast_shared_field(
        field,
        ReceptorDistribution(CommonFieldTime("public.media.pts_ns", start_tick, end_tick), ()),
        MCMFieldStepTime(
            "public.media.pts_ns", start_tick, end_tick, PUBLIC_MEDIA_TICKS_PER_SECOND
        ),
        substrate,
        afterimage,
        dissipation,
    )


@dataclass(frozen=True, slots=True)
class ContinuousDissipationStageOneMeasurement:
    leak_rate_per_second: float
    event_count: int
    activation_mean_delta_to_zero: float
    afterimage_mean_delta_to_zero: float
    activation_centered_linf_to_zero: float
    afterimage_centered_linf_to_zero: float
    activation_constant_energy_fraction: float
    afterimage_constant_energy_fraction: float
    layer_digest: str
    snapshot_digest: str

    def __post_init__(self) -> None:
        if self.leak_rate_per_second not in DISSIPATION_LEAK_RATES_PER_SECOND:
            raise PublicAVContinuousDissipationViabilityError("stage-one rate was not fixed")


@dataclass(frozen=True, slots=True)
class ContinuousDissipationViabilityPoint:
    leak_rate_per_second: float
    resolution_duration_ticks: int
    stage_two_event_count: int
    arm_ids: tuple[str, ...]
    fresh_activation_mean_delta_to_zero: float
    fresh_afterimage_mean_delta_to_zero: float
    fresh_activation_centered_linf_to_zero: float
    fresh_afterimage_centered_linf_to_zero: float
    fresh_activation_constant_energy_fraction: float
    fresh_afterimage_constant_energy_fraction: float
    carry_activation_mean_delta_to_rate_fresh: tuple[float, ...]
    carry_afterimage_mean_delta_to_rate_fresh: tuple[float, ...]
    carry_activation_centered_linf_to_rate_fresh: tuple[float, ...]
    carry_afterimage_centered_linf_to_rate_fresh: tuple[float, ...]
    carry_activation_constant_energy_fraction: tuple[float, ...]
    carry_afterimage_constant_energy_fraction: tuple[float, ...]
    layer_digests: tuple[str, ...]
    snapshot_digests: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.leak_rate_per_second not in DISSIPATION_LEAK_RATES_PER_SECOND:
            raise PublicAVContinuousDissipationViabilityError("point rate was not fixed")
        if self.resolution_duration_ticks not in TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVContinuousDissipationViabilityError("point duration was not fixed")
        if tuple(self.arm_ids) != ARM_IDS:
            raise PublicAVContinuousDissipationViabilityError("four fixed arms are required")
        vectors = (
            self.carry_activation_mean_delta_to_rate_fresh,
            self.carry_afterimage_mean_delta_to_rate_fresh,
            self.carry_activation_centered_linf_to_rate_fresh,
            self.carry_afterimage_centered_linf_to_rate_fresh,
            self.carry_activation_constant_energy_fraction,
            self.carry_afterimage_constant_energy_fraction,
            self.layer_digests,
            self.snapshot_digests,
        )
        if any(len(vector) != len(ARM_IDS) for vector in vectors):
            raise PublicAVContinuousDissipationViabilityError("point measurements must align")


@dataclass(frozen=True, slots=True)
class PublicAVContinuousDissipationViability:
    experiment_id: str
    source_id: str
    clock_id: str
    leak_rates_per_second: tuple[float, ...]
    resolution_duration_ticks: tuple[int, ...]
    stage_one_measurements: tuple[ContinuousDissipationStageOneMeasurement, ...]
    points: tuple[ContinuousDissipationViabilityPoint, ...]
    intervention_scope: str = "all_world_contact_and_contact_free_intervals"
    threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if tuple(self.leak_rates_per_second) != DISSIPATION_LEAK_RATES_PER_SECOND:
            raise PublicAVContinuousDissipationViabilityError("rate axis changed")
        if tuple(self.resolution_duration_ticks) != TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVContinuousDissipationViabilityError("duration axis changed")
        if tuple(item.leak_rate_per_second for item in self.stage_one_measurements) != DISSIPATION_LEAK_RATES_PER_SECOND:
            raise PublicAVContinuousDissipationViabilityError("stage one does not cover rates")
        expected = tuple((duration, rate) for duration in TAIL_RESOLUTION_DURATION_TICKS
                         for rate in DISSIPATION_LEAK_RATES_PER_SECOND)
        actual = tuple((item.resolution_duration_ticks, item.leak_rate_per_second) for item in self.points)
        if actual != expected:
            raise PublicAVContinuousDissipationViabilityError("points do not cover fixed axes")
        if self.intervention_scope != "all_world_contact_and_contact_free_intervals":
            raise PublicAVContinuousDissipationViabilityError("continuous scope changed")
        if any((self.threshold_defined, self.memory_claim_allowed, self.meaning_claim_allowed,
                self.organization_claim_allowed, self.ai_claim_allowed)):
            raise PublicAVContinuousDissipationViabilityError("viability audit cannot release claims")


def _field_components(field):
    return (
        tuple(neuron.activation for neuron in field.layer.neurons),
        tuple(neuron.afterimage for neuron in field.layer.neurons),
    )


def execute_public_av_continuous_dissipation_viability(
    path: Path, contract: PublicMediaSourceContract
) -> PublicAVContinuousDissipationViability:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVContinuousDissipationViabilityError("audited media file is required")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVContinuousDissipationViabilityError("source contract is required")
    sequences = _sequences(path, contract)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    stage_ones = {}
    for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
        stage_ones[rate] = run_neutral_asynchronous_field(
            _fresh_field(sequences), sequences, _steps(sequences, 0, 500_000_000), substrate,
            afterimage_config=afterimage,
            dissipation_config=NeutralFieldDissipationConfig(rate),
        )
    zero_activation, zero_afterimage = _field_components(stage_ones[0.0].field)
    stage_one_measurements = []
    for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
        run = stage_ones[rate]
        activation, afterimage_values = _field_components(run.field)
        am = _mode_metrics(activation, zero_activation)
        hm = _mode_metrics(afterimage_values, zero_afterimage)
        stage_one_measurements.append(ContinuousDissipationStageOneMeasurement(
            rate, run.source_support_count, am[0], hm[0], am[1], hm[1], am[2], hm[2],
            run.field.layer.digest(), run.field.snapshot().digest(),
        ))

    points = []
    for duration in TAIL_RESOLUTION_DURATION_TICKS:
        start_tick = 500_000_000 + duration
        shifted = _shift_sequences(sequences, start_tick)
        steps = _steps(shifted, start_tick, start_tick + 500_000_000)
        fields_by_rate = {}
        counts = {}
        for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
            dissipation = NeutralFieldDissipationConfig(rate)
            arm_fields = []
            for arm_id in ARM_IDS:
                start_field = _independent_arm_start_field(
                    stage_ones[rate].field, arm_id, lambda: _fresh_field(sequences)
                )
                if arm_id != "return.fresh_stage_two":
                    start_field = _continuous_gap(
                        start_field, 500_000_000, start_tick, substrate, afterimage, dissipation
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
                    start_field, shifted, steps, substrate, afterimage_config=afterimage,
                    dissipation_config=dissipation,
                )
                counts[rate] = stage_two.source_support_count
                arm_fields.append(stage_two.field)
            fields_by_rate[rate] = tuple(arm_fields)

        zero_fresh_activation, zero_fresh_afterimage = _field_components(fields_by_rate[0.0][-1])
        for rate in DISSIPATION_LEAK_RATES_PER_SECOND:
            fields = fields_by_rate[rate]
            fresh_activation, fresh_afterimage = _field_components(fields[-1])
            fresh_am = _mode_metrics(fresh_activation, zero_fresh_activation)
            fresh_hm = _mode_metrics(fresh_afterimage, zero_fresh_afterimage)
            carry_am = tuple(_mode_metrics(_field_components(field)[0], fresh_activation) for field in fields)
            carry_hm = tuple(_mode_metrics(_field_components(field)[1], fresh_afterimage) for field in fields)
            points.append(ContinuousDissipationViabilityPoint(
                rate, duration, counts[rate], ARM_IDS,
                fresh_am[0], fresh_hm[0], fresh_am[1], fresh_hm[1], fresh_am[2], fresh_hm[2],
                tuple(item[0] for item in carry_am), tuple(item[0] for item in carry_hm),
                tuple(item[1] for item in carry_am), tuple(item[1] for item in carry_hm),
                tuple(item[2] for item in carry_am), tuple(item[2] for item in carry_hm),
                tuple(field.layer.digest() for field in fields),
                tuple(field.snapshot().digest() for field in fields),
            ))
    return PublicAVContinuousDissipationViability(
        "public.av.nasa-earthrise.continuous-dissipation-viability.v1",
        contract.source_id, sequences[0].clock_id, DISSIPATION_LEAK_RATES_PER_SECOND,
        TAIL_RESOLUTION_DURATION_TICKS, tuple(stage_one_measurements), tuple(points),
    )


def public_av_continuous_dissipation_viability_to_jsonable(result):
    def measurement(item):
        return {name: getattr(item, name) for name in item.__dataclass_fields__}
    return {
        "experiment_id": result.experiment_id,
        "source_id": result.source_id,
        "clock_id": result.clock_id,
        "leak_rates_per_second": list(result.leak_rates_per_second),
        "resolution_duration_ticks": list(result.resolution_duration_ticks),
        "intervention_scope": result.intervention_scope,
        "stage_one_measurements": [measurement(item) for item in result.stage_one_measurements],
        "points": [
            {key: list(value) if isinstance(value, tuple) else value
             for key, value in measurement(item).items()} for item in result.points
        ],
        "threshold_defined": result.threshold_defined,
        "memory_claim_allowed": result.memory_claim_allowed,
        "meaning_claim_allowed": result.meaning_claim_allowed,
        "organization_claim_allowed": result.organization_claim_allowed,
        "ai_claim_allowed": result.ai_claim_allowed,
    }
