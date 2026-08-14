"""Parametric synthetic audio-video rate, partition, and order probe."""

from __future__ import annotations

from dataclasses import dataclass

from .asynchronous_audio_video_partition_probe import (
    AsynchronousPartitionArm,
    run_asynchronous_partition_arm,
)


RATE_PAIRS = ((50.0, 5.0), (100.0, 10.0), (200.0, 20.0))


@dataclass(frozen=True, slots=True)
class AsynchronousRateCase:
    case_id: str
    coarse: AsynchronousPartitionArm
    fine: AsynchronousPartitionArm
    reproduction: AsynchronousPartitionArm
    permutation: AsynchronousPartitionArm
    activation_equal: bool
    afterimage_equal: bool
    layer_digest_equal: bool
    snapshot_digest_equal: bool
    reproduction_exact: bool
    permutation_layer_equal: bool


@dataclass(frozen=True, slots=True)
class AsynchronousAudioVideoRateProbeResult:
    cases: tuple[AsynchronousRateCase, ...]
    deterministic: bool


def run_asynchronous_audio_video_rate_probe() -> AsynchronousAudioVideoRateProbeResult:
    cases = []
    for audio_rate, video_rate in RATE_PAIRS:
        kwargs = {"audio_rate_hz": audio_rate, "video_rate_hz": video_rate}
        coarse = run_asynchronous_partition_arm("wav", "coarse", **kwargs)
        fine = run_asynchronous_partition_arm("wav", "fine", **kwargs)
        reproduction = run_asynchronous_partition_arm(
            "wav", "fine", reproduction_id=f"rate.{audio_rate}.{video_rate}.reproduction", **kwargs
        )
        permutation = run_asynchronous_partition_arm(
            "wav", "fine", reverse_sequences=True, **kwargs
        )
        cases.append(
            AsynchronousRateCase(
                case_id=f"audio.{audio_rate}.video.{video_rate}",
                coarse=coarse,
                fine=fine,
                reproduction=reproduction,
                permutation=permutation,
                activation_equal=coarse.activation == fine.activation,
                afterimage_equal=coarse.afterimage == fine.afterimage,
                layer_digest_equal=coarse.layer_digest == fine.layer_digest,
                snapshot_digest_equal=coarse.snapshot_digest == fine.snapshot_digest,
                reproduction_exact=(fine.activation, fine.afterimage, fine.layer_digest) == (reproduction.activation, reproduction.afterimage, reproduction.layer_digest),
                permutation_layer_equal=fine.layer_digest == permutation.layer_digest,
            )
        )
    first = tuple(cases)
    second = tuple(
        run_asynchronous_partition_arm("wav", "fine", audio_rate_hz=a, video_rate_hz=v).layer_digest
        for a, v in RATE_PAIRS
    )
    return AsynchronousAudioVideoRateProbeResult(
        cases=first,
        deterministic=tuple(case.fine.layer_digest for case in first) == second,
    )
