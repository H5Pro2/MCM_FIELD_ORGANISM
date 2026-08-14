"""Preregistered long-duration tail for the public AV return curve."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import NeutralFastAfterimageConfig, NeutralLocalFieldSubstrateConfig
from .public_av_return_replication_execution import _advance_contact_free, _linf
from .public_av_return_resolution_curve import ARM_IDS, _independent_arm_start_field, _shift_sequences
from .public_av_six_arm_field_execution import _sequences
from .public_av_two_stage_return_execution import _fresh_field, _steps
from .public_media_source_contract import PublicMediaSourceContract
from .shared_field_component_intervention import intervene_shared_field_component
from .shared_mcm_field import SharedMCMField


TAIL_RESOLUTION_DURATION_TICKS = (
    2_000_000_000,
    5_000_000_000,
    10_000_000_000,
    20_000_000_000,
)


class PublicAVReturnResolutionTailError(ValueError):
    pass


def _tail_arm_start_field(
    stage_one_field: SharedMCMField,
    arm_id: str,
    fresh_field_factory: Callable[[], SharedMCMField],
) -> SharedMCMField:
    return _independent_arm_start_field(stage_one_field, arm_id, fresh_field_factory)


@dataclass(frozen=True, slots=True)
class PublicAVReturnResolutionTailPoint:
    resolution_duration_ticks: int
    stage_one_event_count: int
    stage_two_event_count: int
    stage_one_snapshot_digest: str
    arm_ids: tuple[str, ...]
    activation_linf_to_fresh: tuple[float, ...]
    afterimage_linf_to_fresh: tuple[float, ...]
    layer_digests: tuple[str, ...]
    snapshot_digests: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.resolution_duration_ticks not in TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVReturnResolutionTailError("tail duration was not preregistered")
        if tuple(self.arm_ids) != ARM_IDS:
            raise PublicAVReturnResolutionTailError("tail point requires the four preregistered arms")
        if {
            len(self.activation_linf_to_fresh),
            len(self.afterimage_linf_to_fresh),
            len(self.layer_digests),
            len(self.snapshot_digests),
        } != {len(ARM_IDS)}:
            raise PublicAVReturnResolutionTailError("all tail measurements must align")


@dataclass(frozen=True, slots=True)
class PublicAVReturnResolutionTail:
    experiment_id: str
    source_id: str
    clock_id: str
    resolution_duration_ticks: tuple[int, ...]
    points: tuple[PublicAVReturnResolutionTailPoint, ...]
    raw_payload_retained: bool = False
    metadata_used_by_field: bool = False
    threshold_defined: bool = False
    memory_claim_allowed: bool = False
    meaning_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if tuple(self.resolution_duration_ticks) != TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVReturnResolutionTailError("tail duration axis differs from preregistration")
        if tuple(point.resolution_duration_ticks for point in self.points) != TAIL_RESOLUTION_DURATION_TICKS:
            raise PublicAVReturnResolutionTailError("tail points do not cover the duration axis")
        if any((
            self.raw_payload_retained,
            self.metadata_used_by_field,
            self.threshold_defined,
            self.memory_claim_allowed,
            self.meaning_claim_allowed,
            self.organization_claim_allowed,
            self.ai_claim_allowed,
        )):
            raise PublicAVReturnResolutionTailError("tail cannot retain payloads, define thresholds, or release claims")


def execute_public_av_return_resolution_tail(
    path: Path,
    contract: PublicMediaSourceContract,
) -> PublicAVReturnResolutionTail:
    if not isinstance(path, Path) or not path.is_file():
        raise PublicAVReturnResolutionTailError("audited media file is required")
    if not isinstance(contract, PublicMediaSourceContract):
        raise PublicAVReturnResolutionTailError("public media source contract is required")

    stage_one_sequences = _sequences(path, contract)
    stage_one_steps = _steps(stage_one_sequences, 0, 500_000_000)
    substrate = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage = NeutralFastAfterimageConfig(0.5)
    stage_one = run_neutral_asynchronous_field(
        _fresh_field(stage_one_sequences),
        stage_one_sequences,
        stage_one_steps,
        substrate,
        afterimage_config=afterimage,
    )
    stage_one_digest = stage_one.field.snapshot().digest()
    points = []

    for duration in TAIL_RESOLUTION_DURATION_TICKS:
        stage_two_start_tick = 500_000_000 + duration
        stage_two_end_tick = stage_two_start_tick + 500_000_000
        stage_two_sequences = _shift_sequences(stage_one_sequences, stage_two_start_tick)
        stage_two_steps = _steps(stage_two_sequences, stage_two_start_tick, stage_two_end_tick)
        arm_fields = []
        stage_two_count = 0

        for arm_id in ARM_IDS:
            start_field = _tail_arm_start_field(
                stage_one.field,
                arm_id,
                lambda: _fresh_field(stage_one_sequences),
            )
            if arm_id != "return.fresh_stage_two":
                start_field = _advance_contact_free(
                    start_field,
                    500_000_000,
                    stage_two_start_tick,
                    substrate,
                    afterimage,
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
                start_field,
                stage_two_sequences,
                stage_two_steps,
                substrate,
                afterimage_config=afterimage,
            )
            stage_two_count = stage_two.source_support_count
            arm_fields.append(stage_two.field)

        fresh = arm_fields[-1]
        fresh_activation = tuple(neuron.activation for neuron in fresh.layer.neurons)
        fresh_afterimage = tuple(neuron.afterimage for neuron in fresh.layer.neurons)
        points.append(PublicAVReturnResolutionTailPoint(
            resolution_duration_ticks=duration,
            stage_one_event_count=stage_one.source_support_count,
            stage_two_event_count=stage_two_count,
            stage_one_snapshot_digest=stage_one_digest,
            arm_ids=ARM_IDS,
            activation_linf_to_fresh=tuple(
                _linf(tuple(neuron.activation for neuron in field.layer.neurons), fresh_activation)
                for field in arm_fields
            ),
            afterimage_linf_to_fresh=tuple(
                _linf(tuple(neuron.afterimage for neuron in field.layer.neurons), fresh_afterimage)
                for field in arm_fields
            ),
            layer_digests=tuple(field.layer.digest() for field in arm_fields),
            snapshot_digests=tuple(field.snapshot().digest() for field in arm_fields),
        ))

    return PublicAVReturnResolutionTail(
        experiment_id="public.av.nasa-earthrise.return-resolution-tail.v1",
        source_id=contract.source_id,
        clock_id=stage_one_sequences[0].clock_id,
        resolution_duration_ticks=TAIL_RESOLUTION_DURATION_TICKS,
        points=tuple(points),
    )


def public_av_return_resolution_tail_to_jsonable(
    tail: PublicAVReturnResolutionTail,
) -> dict[str, object]:
    return {
        "experiment_id": tail.experiment_id,
        "source_id": tail.source_id,
        "clock_id": tail.clock_id,
        "resolution_duration_ticks": list(tail.resolution_duration_ticks),
        "points": [
            {
                "resolution_duration_ticks": point.resolution_duration_ticks,
                "stage_one_event_count": point.stage_one_event_count,
                "stage_two_event_count": point.stage_two_event_count,
                "stage_one_snapshot_digest": point.stage_one_snapshot_digest,
                "arm_ids": list(point.arm_ids),
                "activation_linf_to_fresh": list(point.activation_linf_to_fresh),
                "afterimage_linf_to_fresh": list(point.afterimage_linf_to_fresh),
                "layer_digests": list(point.layer_digests),
                "snapshot_digests": list(point.snapshot_digests),
            }
            for point in tail.points
        ],
        "threshold_defined": tail.threshold_defined,
        "memory_claim_allowed": tail.memory_claim_allowed,
        "meaning_claim_allowed": tail.meaning_claim_allowed,
        "organization_claim_allowed": tail.organization_claim_allowed,
        "ai_claim_allowed": tail.ai_claim_allowed,
    }
