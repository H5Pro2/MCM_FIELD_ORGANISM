"""Passive interval map for the already reduced public visual world."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math

import numpy as np

from .field_step_time import MCMFieldStepTime
from .finite_video_path import LocalChannelGridReceptor
from .neutral_asynchronous_field_runtime import run_neutral_asynchronous_field
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .public_visual_world import (
    PublicVisualReceptorSequence,
    PublicVisualWorldError,
    _timed_sequence,
    _visual_anatomy,
)
from .receptor_time_alignment import ReceptorTimeSequence
from .shared_mcm_field import build_shared_mcm_field


@dataclass(frozen=True, slots=True)
class ExternalTimeSection:
    """One section fixed from outer clock boundaries before field evaluation."""

    start_ms: int
    end_ms: int

    def __post_init__(self) -> None:
        if (
            isinstance(self.start_ms, bool)
            or not isinstance(self.start_ms, int)
            or isinstance(self.end_ms, bool)
            or not isinstance(self.end_ms, int)
            or self.start_ms < 0
            or self.end_ms <= self.start_ms
        ):
            raise PublicVisualWorldError("external section bounds must advance")


@dataclass(frozen=True, slots=True)
class TemporalFieldInterval:
    """Observer copy of local values after one fixed receptor interval."""

    interval_index: int
    start_ms: int
    end_ms: int
    projection: tuple[float, ...]
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    activation_change_l2: float
    projection_change_l2: float
    projection_afterimage_dot: float


@dataclass(frozen=True, slots=True)
class TemporalSectionSummary:
    section_index: int
    start_ms: int
    end_ms: int
    first_interval_index: int
    last_interval_index: int
    activation_change_l2_sum: float
    projection_change_l2_sum: float
    projection_afterimage_dot_sum: float


@dataclass(frozen=True, slots=True)
class PublicVisualTemporalMap:
    """Complete passive maps and controls; never part of organism state."""

    receptor_geometry_id: str
    sampling_interval_ms: int
    duration_ms: int
    interval_count: int
    field_positions: tuple[tuple[int, ...], ...]
    diffusion_offsets: tuple[tuple[int, int], ...]
    response_time_seconds: float
    afterimage_time_constant_seconds: float
    sections: tuple[TemporalSectionSummary, ...]
    actual: tuple[TemporalFieldInterval, ...]
    static_baseline: tuple[TemporalFieldInterval, ...]
    reduced_sequence_digest: str
    repeated_sequence_digest: str
    actual_repeat_max_abs_residual: float
    static_repeat_max_abs_residual: float
    explanation_baseline: tuple[str, ...] = (
        "current_receptor_projection",
        "fixed_symmetric_diffusion",
        "fast_afterimage",
    )

    def digest(self) -> str:
        payload = json.dumps(
            _json_value(self),
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("ascii")
        return hashlib.sha256(payload).hexdigest()


def _json_value(value):
    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _json_value(getattr(value, name))
            for name in value.__dataclass_fields__
        }
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    return value


def temporal_map_json_value(result: PublicVisualTemporalMap) -> dict:
    """Return a JSON-ready observer artifact without adding runtime roles."""

    if not isinstance(result, PublicVisualTemporalMap):
        raise PublicVisualWorldError("temporal map result is required")
    return _json_value(result)


def _validate_inputs(
    reduced: PublicVisualReceptorSequence,
    repeated: PublicVisualReceptorSequence,
    receptor: LocalChannelGridReceptor,
    sections: tuple[ExternalTimeSection, ...],
) -> None:
    if not isinstance(reduced, PublicVisualReceptorSequence) or not isinstance(
        repeated, PublicVisualReceptorSequence
    ):
        raise PublicVisualWorldError("two reduced public visual sequences are required")
    if not isinstance(receptor, LocalChannelGridReceptor):
        raise PublicVisualWorldError("the existing local visual receptor is required")
    if reduced.reduced_digest() != repeated.reduced_digest():
        raise PublicVisualWorldError("public visual repeat changed the reduced sequence")
    if not sections or any(not isinstance(item, ExternalTimeSection) for item in sections):
        raise PublicVisualWorldError("external time sections are required")
    expected_start = 0
    for section in sections:
        if section.start_ms != expected_start:
            raise PublicVisualWorldError("external sections must be contiguous from zero")
        if section.start_ms % reduced.sampling_interval_ms or section.end_ms % reduced.sampling_interval_ms:
            raise PublicVisualWorldError("external sections must align to receptor intervals")
        expected_start = section.end_ms
    if expected_start != reduced.duration_ms:
        raise PublicVisualWorldError("external sections must cover the complete sequence")


def _run_interval_map(
    reduced: PublicVisualReceptorSequence,
    receptor: LocalChannelGridReceptor,
    *,
    static: bool,
) -> tuple[tuple[tuple[int, ...], ...], tuple[TemporalFieldInterval, ...]]:
    sequence = _timed_sequence(reduced, static=static)
    current = build_shared_mcm_field(
        (sequence.frames[0].frame,),
        {"visual": _visual_anatomy(receptor.config)},
        sample_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
    )
    positions = tuple(neuron.position for neuron in current.layer.neurons)
    previous_projection = np.zeros(len(current.layer.neurons), dtype=np.float64)
    previous_activation = np.zeros(len(current.layer.neurons), dtype=np.float64)
    previous_afterimage = np.zeros(len(current.layer.neurons), dtype=np.float64)
    records = []
    for index, timed in enumerate(sequence.frames):
        start = index * reduced.sampling_interval_ms
        end = start + reduced.sampling_interval_ms
        one = ReceptorTimeSequence(
            modality_id=sequence.modality_id,
            geometry_id=sequence.geometry_id,
            clock_id=sequence.clock_id,
            frames=(timed,),
        )
        current = run_neutral_asynchronous_field(
            current,
            (one,),
            (MCMFieldStepTime(sequence.clock_id, start, end, 1_000.0),),
            NeutralLocalFieldSubstrateConfig(1.0),
            afterimage_config=NeutralFastAfterimageConfig(0.5),
        ).field
        projection = np.asarray(timed.frame.values, dtype=np.float64)
        activation = np.asarray(
            [neuron.activation for neuron in current.layer.neurons], dtype=np.float64
        )
        afterimage = np.asarray(
            [neuron.afterimage for neuron in current.layer.neurons], dtype=np.float64
        )
        records.append(
            TemporalFieldInterval(
                interval_index=index,
                start_ms=start,
                end_ms=end,
                projection=tuple(float(value) for value in projection),
                activation=tuple(float(value) for value in activation),
                afterimage=tuple(float(value) for value in afterimage),
                activation_change_l2=float(np.linalg.norm(activation - previous_activation)),
                projection_change_l2=float(np.linalg.norm(projection - previous_projection)),
                projection_afterimage_dot=float(np.dot(projection, previous_afterimage)),
            )
        )
        previous_projection = projection
        previous_activation = activation
        previous_afterimage = afterimage
    return positions, tuple(records)


def _max_residual(
    first: tuple[TemporalFieldInterval, ...],
    second: tuple[TemporalFieldInterval, ...],
) -> float:
    values = []
    for left, right in zip(first, second, strict=True):
        values.extend(abs(a - b) for a, b in zip(left.activation, right.activation, strict=True))
        values.extend(abs(a - b) for a, b in zip(left.afterimage, right.afterimage, strict=True))
    return max(values, default=0.0)


def observe_public_visual_temporal_map(
    reduced: PublicVisualReceptorSequence,
    repeated: PublicVisualReceptorSequence,
    receptor: LocalChannelGridReceptor,
    sections: tuple[ExternalTimeSection, ...],
) -> PublicVisualTemporalMap:
    """Replay fixed mechanics and quantify trajectories outside the organism."""

    _validate_inputs(reduced, repeated, receptor, sections)
    positions, actual = _run_interval_map(reduced, receptor, static=False)
    repeated_positions, actual_repeat = _run_interval_map(repeated, receptor, static=False)
    static_positions, static = _run_interval_map(reduced, receptor, static=True)
    _, static_repeat = _run_interval_map(repeated, receptor, static=True)
    if positions != repeated_positions or positions != static_positions:
        raise PublicVisualWorldError("field geometry changed between controls")
    summaries = []
    interval_ms = reduced.sampling_interval_ms
    for section_index, section in enumerate(sections):
        first = section.start_ms // interval_ms
        stop = section.end_ms // interval_ms
        selected = actual[first:stop]
        summaries.append(
            TemporalSectionSummary(
                section_index=section_index,
                start_ms=section.start_ms,
                end_ms=section.end_ms,
                first_interval_index=first,
                last_interval_index=stop - 1,
                activation_change_l2_sum=math.fsum(item.activation_change_l2 for item in selected),
                projection_change_l2_sum=math.fsum(item.projection_change_l2 for item in selected),
                projection_afterimage_dot_sum=math.fsum(item.projection_afterimage_dot for item in selected),
            )
        )
    return PublicVisualTemporalMap(
        receptor_geometry_id=reduced.states[0].geometry_id,
        sampling_interval_ms=interval_ms,
        duration_ms=reduced.duration_ms,
        interval_count=len(reduced.states),
        field_positions=positions,
        diffusion_offsets=((-1, 0), (0, -1), (0, 1), (1, 0)),
        response_time_seconds=1.0,
        afterimage_time_constant_seconds=0.5,
        sections=tuple(summaries),
        actual=actual,
        static_baseline=static,
        reduced_sequence_digest=reduced.reduced_digest(),
        repeated_sequence_digest=repeated.reduced_digest(),
        actual_repeat_max_abs_residual=_max_residual(actual, actual_repeat),
        static_repeat_max_abs_residual=_max_residual(static, static_repeat),
    )
