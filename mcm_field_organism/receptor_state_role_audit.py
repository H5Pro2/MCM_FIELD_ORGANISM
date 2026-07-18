"""Behavioral audit of state ownership across current receptor boundaries."""

from __future__ import annotations

from dataclasses import dataclass, fields
import math

import numpy as np

from .broadband_hearing_path import BroadbandHearingPath
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from .receptor_contract import CommonFieldTime, from_visual_receptor_state
from .receptor_distributor import ReceptorDistributor, ReceptorDock


@dataclass(frozen=True, slots=True)
class ReceptorStateRoleAudit:
    auditory_window_seconds: float
    auditory_hop_seconds: float
    auditory_one_hop_history_difference: float
    auditory_history_cleared_after_window: bool
    visual_probe_history_difference: float
    visual_probe_digest_equal_after_contrasting_history: bool
    distributor_probe_digest_equal_after_prior_distribution: bool
    distributor_attached_dock_count_after_probe: int


def _auditory_history_observation() -> tuple[float, float, float, bool]:
    config = LogSpectralConfig(
        sample_rate=1000,
        window_size=100,
        hop_size=10,
        min_frequency=10.0,
        max_frequency=400.0,
        band_count=8,
    )
    carried = BroadbandHearingPath(LogSpectralReceptor(config))
    fresh = BroadbandHearingPath(LogSpectralReceptor(config))
    sample_index = np.arange(config.window_size)
    signal = 0.5 * np.sin(2.0 * np.pi * 100.0 * sample_index / config.sample_rate)
    signal_chunks = np.split(signal, config.warmup_hops)
    zero = tuple(0.0 for _ in range(config.hop_size))

    for chunk in signal_chunks:
        carried.push(tuple(float(value) for value in chunk))
    carried_probe = carried.push(zero)

    fresh_probe = None
    for _ in range(config.warmup_hops + 1):
        fresh_probe = fresh.push(zero)
    if carried_probe is None or fresh_probe is None:
        raise RuntimeError("auditory role audit requires completed probe states")
    difference = max(
        abs(left - right)
        for left, right in zip(carried_probe.energy, fresh_probe.energy, strict=True)
    )

    cleared = carried_probe
    for _ in range(config.warmup_hops - 1):
        cleared = carried.push(zero)
    if cleared is None:
        raise RuntimeError("auditory role audit lost its rolling output")
    return (
        config.window_seconds,
        config.hop_seconds,
        difference,
        all(value == 0.0 for value in cleared.energy),
    )


def _visual_and_distributor_observation() -> tuple[float, bool, bool, int]:
    config = VisualGridConfig(
        source_width=4,
        source_height=2,
        grid_columns=2,
        grid_rows=1,
        frames_per_second=10.0,
    )
    historical = LocalChannelGridReceptor(config)
    fresh = LocalChannelGridReceptor(config)
    contrast = np.zeros((2, 4, 3), dtype=np.uint8)
    contrast[:, :2, 0] = 255
    probe = np.full((2, 4, 3), 64, dtype=np.uint8)
    historical.analyze(contrast, frame_index=0)
    historical_probe = historical.analyze(probe, frame_index=1)
    fresh_probe = fresh.analyze(probe, frame_index=1)
    difference = max(
        abs(left - right)
        for left, right in zip(
            historical_probe.channel_values,
            fresh_probe.channel_values,
            strict=True,
        )
    )

    dock = ReceptorDock("dock.visual", "visual", config.geometry_id)
    used = ReceptorDistributor()
    reference = ReceptorDistributor()
    used.attach(dock)
    reference.attach(dock)
    used.distribute(
        (from_visual_receptor_state(fresh.analyze(contrast, frame_index=0)),),
        CommonFieldTime("organism.test", 0, 1),
    )
    probe_frame = from_visual_receptor_state(fresh_probe)
    used_probe = used.distribute(
        (probe_frame,), CommonFieldTime("organism.test", 1, 2)
    )
    reference_probe = reference.distribute(
        (probe_frame,), CommonFieldTime("organism.test", 1, 2)
    )
    return (
        difference,
        historical_probe.digest() == fresh_probe.digest(),
        used_probe.digest() == reference_probe.digest(),
        len(used.docks),
    )


def run_receptor_state_role_audit() -> ReceptorStateRoleAudit:
    """Contrast prior histories without introducing receptor persistence."""

    window, hop, auditory_difference, auditory_cleared = (
        _auditory_history_observation()
    )
    visual_difference, visual_equal, distributor_equal, dock_count = (
        _visual_and_distributor_observation()
    )
    if not all(
        math.isfinite(value)
        for value in (auditory_difference, visual_difference)
    ):
        raise RuntimeError("receptor state role audit produced a non-finite result")
    return ReceptorStateRoleAudit(
        auditory_window_seconds=window,
        auditory_hop_seconds=hop,
        auditory_one_hop_history_difference=auditory_difference,
        auditory_history_cleared_after_window=auditory_cleared,
        visual_probe_history_difference=visual_difference,
        visual_probe_digest_equal_after_contrasting_history=visual_equal,
        distributor_probe_digest_equal_after_prior_distribution=distributor_equal,
        distributor_attached_dock_count_after_probe=dock_count,
    )


def receptor_state_role_audit_public_roles() -> tuple[str, ...]:
    return tuple(item.name for item in fields(ReceptorStateRoleAudit))
