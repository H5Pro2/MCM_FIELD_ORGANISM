"""Precision controls for asynchronous coarse/fine field partitioning."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from .asynchronous_audio_video_partition_probe import (
    _sequences,
    _world,
    run_asynchronous_partition_arm,
)
from .asynchronous_audio_video_rate_probe import RATE_PAIRS
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .neutral_local_field_substrate import (
    NeutralLocalFieldSubstrateConfig,
    _diffusion_generator,
)
from .shared_mcm_field import build_shared_mcm_field


@dataclass(frozen=True, slots=True)
class AsynchronousPrecisionCase:
    audio_rate_hz: float
    video_rate_hz: float
    fine_step_count: int
    signal_activation_linf: float
    signal_afterimage_linf: float
    null_activation_linf: float
    null_afterimage_linf: float


@dataclass(frozen=True, slots=True)
class AsynchronousPrecisionProbeResult:
    cases: tuple[AsynchronousPrecisionCase, ...]
    neuron_count: int
    numpy_orthogonality_linf: float
    fsum_orthogonality_linf: float
    deterministic: bool


def _linf(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    return max(abs(a - b) for a, b in zip(left, right, strict=True))


def _eigenbasis() -> np.ndarray:
    world = _world("wav")
    sequences = _sequences(
        world,
        clock_id="organism.asynchronous_precision",
        ticks_per_second=1_000_000.0,
    )
    visual_receptor = world.open_sources()[3]
    reference_frames = tuple(sequence.frames[0].frame for sequence in sequences)
    field = build_shared_mcm_field(
        reference_frames,
        audio_video_dock_anatomies(
            auditory_carrier_count=len(reference_frames[0].carrier_ids),
            visual_grid_columns=visual_receptor.config.grid_columns,
            visual_grid_rows=visual_receptor.config.grid_rows,
        ),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    generator = _diffusion_generator(field, NeutralLocalFieldSubstrateConfig(1.0))
    return np.linalg.eigh(generator)[1]


def _fsum_orthogonality_linf(eigenvectors: np.ndarray) -> float:
    size = eigenvectors.shape[1]
    return max(
        abs(
            math.fsum(
                float(eigenvectors[row, left]) * float(eigenvectors[row, right])
                for row in range(eigenvectors.shape[0])
            )
            - (1.0 if left == right else 0.0)
        )
        for left in range(size)
        for right in range(size)
    )


def run_asynchronous_audio_video_precision_probe(
) -> AsynchronousPrecisionProbeResult:
    """Compare active and null partitions against the spectral basis residual."""

    cases = []
    for audio_rate, video_rate in RATE_PAIRS:
        kwargs = {"audio_rate_hz": audio_rate, "video_rate_hz": video_rate}
        signal_coarse = run_asynchronous_partition_arm("wav", "coarse", **kwargs)
        signal_fine = run_asynchronous_partition_arm("wav", "fine", **kwargs)
        null_coarse = run_asynchronous_partition_arm("w0", "coarse", **kwargs)
        null_fine = run_asynchronous_partition_arm("w0", "fine", **kwargs)
        cases.append(
            AsynchronousPrecisionCase(
                audio_rate_hz=audio_rate,
                video_rate_hz=video_rate,
                fine_step_count=signal_fine.proposal_step_count,
                signal_activation_linf=_linf(signal_coarse.activation, signal_fine.activation),
                signal_afterimage_linf=_linf(signal_coarse.afterimage, signal_fine.afterimage),
                null_activation_linf=_linf(null_coarse.activation, null_fine.activation),
                null_afterimage_linf=_linf(null_coarse.afterimage, null_fine.afterimage),
            )
        )
    eigenvectors = _eigenbasis()
    identity = np.eye(eigenvectors.shape[1])
    numpy_residual = float(np.max(np.abs(eigenvectors.T @ eigenvectors - identity)))
    first = tuple(cases)
    repeated = run_asynchronous_partition_arm(
        "w0", "fine", audio_rate_hz=RATE_PAIRS[-1][0], video_rate_hz=RATE_PAIRS[-1][1]
    )
    check = run_asynchronous_partition_arm(
        "w0", "fine", audio_rate_hz=RATE_PAIRS[-1][0], video_rate_hz=RATE_PAIRS[-1][1]
    )
    return AsynchronousPrecisionProbeResult(
        cases=first,
        neuron_count=eigenvectors.shape[0],
        numpy_orthogonality_linf=numpy_residual,
        fsum_orthogonality_linf=_fsum_orthogonality_linf(eigenvectors),
        deterministic=(repeated.activation, repeated.afterimage) == (check.activation, check.afterimage),
    )
