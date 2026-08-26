"""Preregistered constant-mode audit for the public AV resolution tail."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path

from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import NeutralFastAfterimageConfig, NeutralLocalFieldSubstrateConfig
from .public_av_return_replication_execution import _advance_contact_free
from .public_av_return_resolution_curve import ARM_IDS, _independent_arm_start_field, _shift_sequences
from .public_av_return_resolution_tail import TAIL_RESOLUTION_DURATION_TICKS
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract
from .shared_field_component_intervention import intervene_shared_field_component


class PublicAVReturnResolutionModeAuditError(ValueError):
    pass


def _mode_metrics(
    values: tuple[float, ...],
    fresh_values: tuple[float, ...],
) -> tuple[float, float, float]:
    """Return signed mean delta, centered L-inf, and constant L2 energy share."""

    if not values or len(values) != len(fresh_values):
        raise PublicAVReturnResolutionModeAuditError("mode metrics require aligned field vectors")
    delta = tuple(left - right for left, right in zip(values, fresh_values, strict=True))
    mean_delta = math.fsum(delta) / len(delta)
    centered_linf = max(abs(value - mean_delta) for value in delta)
    total_energy = math.fsum(value * value for value in delta)
    constant_energy = len(delta) * mean_delta * mean_delta
    fraction = 0.0 if total_energy == 0.0 else constant_energy / total_energy
    return mean_delta, centered_linf, min(1.0, max(0.0, fraction))


@dataclass(frozen=True, slots=True)
class PublicAVReturnResolutionModeAuditPoint:
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

    def __post_init__(self) -> None:
        if self.resolution_duration_ticks not in TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVReturnResolutionModeAuditError("mode audit duration was not preregistered")
        if tuple(self.arm_ids) != ARM_IDS:
            raise PublicAVReturnResolutionModeAuditError("mode audit requires the four fixed arms")
        vectors = (
            self.activation_mean_delta_to_fresh,
            self.afterimage_mean_delta_to_fresh,
            self.activation_centered_linf_to_fresh,
            self.afterimage_centered_linf_to_fresh,
            self.activation_constant_energy_fraction,
            self.afterimage_constant_energy_fraction,
        )
        if any(len(vector) != len(ARM_IDS) for vector in vectors):
            raise PublicAVReturnResolutionModeAuditError("all mode audit measurements must align")
        if any(not 0.0 <= value <= 1.0 for vector in vectors[-2:] for value in vector):
            raise PublicAVReturnResolutionModeAuditError("constant energy fractions must be normalized")


@dataclass(frozen=True, slots=True)
class PublicAVReturnResolutionModeAudit:
    audit_id: str
    source_id: str
    clock_id: str
    resolution_duration_ticks: tuple[int, ...]
    points: tuple[PublicAVReturnResolutionModeAuditPoint, ...]
    constant_component_measure: str = "l2_energy_fraction"
    threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if tuple(self.resolution_duration_ticks) != TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVReturnResolutionModeAuditError("mode audit duration axis changed")
        if tuple(point.resolution_duration_ticks for point in self.points) != TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVReturnResolutionModeAuditError("mode audit points do not cover the axis")
        if self.constant_component_measure != "l2_energy_fraction":
            raise PublicAVReturnResolutionModeAuditError("constant component measure changed")
        if any((
            self.threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )):
            raise PublicAVReturnResolutionModeAuditError("mode audit cannot define thresholds or release claims")


def execute_public_av_return_resolution_mode_audit(
    path: Path,
    contract: PublicMediaSourceContract,
) -> PublicAVReturnResolutionModeAudit:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVReturnResolutionModeAuditError("audited media file is required")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVReturnResolutionModeAuditError("public media source contract is required")

    stage_one_sequences = _sequences(path, contract)
    stage_one_steps = _steps(stage_one_sequences, 0, 500_000_000)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    stage_one = run_neutral_asynchronous_field(
        _fresh_field(stage_one_sequences), stage_one_sequences, stage_one_steps, substrate,
        afterimage_config=afterimage,
    )
    points = []
    for duration in TAIL_RESOLUTION_DURATION_TICKS:
        stage_two_start_tick = 500_000_000 + duration
        stage_two_end_tick = stage_two_start_tick + 500_000_000
        stage_two_sequences = _shift_sequences(stage_one_sequences, stage_two_start_tick)
        stage_two_steps = _steps(stage_two_sequences, stage_two_start_tick, stage_two_end_tick)
        fields = []
        stage_two_count = 0
        for arm_id in ARM_IDS:
            start_field = _independent_arm_start_field(
                stage_one.field, arm_id, lambda: _fresh_field(stage_one_sequences)
            )
            if arm_id != "return.fresh_stage_two":
                start_field = _advance_contact_free(
                    start_field, 500_000_000, stage_two_start_tick, substrate, afterimage
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
                start_field, stage_two_sequences, stage_two_steps, substrate,
                afterimage_config=afterimage,
            )
            stage_two_count = stage_two.source_support_count
            fields.append(stage_two.field)

        fresh = fields[-1]
        fresh_activation = tuple(neuron.activation for neuron in fresh.layer.neurons)
        fresh_afterimage = tuple(neuron.afterimage for neuron in fresh.layer.neurons)
        activation_metrics = tuple(
            _mode_metrics(
                tuple(neuron.activation for neuron in field.layer.neurons), fresh_activation
            ) for field in fields
        )
        afterimage_metrics = tuple(
            _mode_metrics(
                tuple(neuron.afterimage for neuron in field.layer.neurons), fresh_afterimage
            ) for field in fields
        )
        points.append(PublicAVReturnResolutionModeAuditPoint(
            resolution_duration_ticks=duration,
            stage_one_event_count=stage_one.source_support_count,
            stage_two_event_count=stage_two_count,
            arm_ids=ARM_IDS,
            activation_mean_delta_to_fresh=tuple(item[0] for item in activation_metrics),
            afterimage_mean_delta_to_fresh=tuple(item[0] for item in afterimage_metrics),
            activation_centered_linf_to_fresh=tuple(item[1] for item in activation_metrics),
            afterimage_centered_linf_to_fresh=tuple(item[1] for item in afterimage_metrics),
            activation_constant_energy_fraction=tuple(item[2] for item in activation_metrics),
            afterimage_constant_energy_fraction=tuple(item[2] for item in afterimage_metrics),
        ))

    return PublicAVReturnResolutionModeAudit(
        audit_id="public.av.nasa-earthrise.return-resolution-mode-audit.v1",
        source_id=contract.source_id,
        clock_id=stage_one_sequences[0].clock_id,
        resolution_duration_ticks=TAIL_RESOLUTION_DURATION_TICKS,
        points=tuple(points),
    )


def public_av_return_resolution_mode_audit_to_jsonable(
    audit: PublicAVReturnResolutionModeAudit,
) -> dict[str, object]:
    return {
        "audit_id": audit.audit_id,
        "source_id": audit.source_id,
        "clock_id": audit.clock_id,
        "resolution_duration_ticks": list(audit.resolution_duration_ticks),
        "constant_component_measure": audit.constant_component_measure,
        "points": [
            {
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
            } for point in audit.points
        ],
        "threshold_defined": audit.threshold_defined,
        "memory_claim_allowed": audit.memory_claim_allowed,
        "meaning_claim_allowed": audit.meaning_claim_allowed,
        "organization_claim_allowed": audit.organization_claim_allowed,
        "ai_claim_allowed": audit.ai_claim_allowed,
    }
