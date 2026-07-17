"""Passive null probe for fixed sensory receptors under different histories."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
import re
from typing import Callable, Iterable

import numpy as np

from .auditory_baselines import (
    AuditoryProbeConfig,
    auditory_receptor_frame,
    synthesize_tone_frame,
)
from .finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from .receptor_surface import ControlledReceptorSurface, stateless_surface_frame


class SensoryLoadRecoveryNullProbeError(ValueError):
    """Raised when the passive null-probe program is invalid."""


SENSORY_NULL_FAMILY_IDS = ("auditory", "controlled_surface", "visual")
SENSORY_NULL_HISTORY_IDS = (
    "rest_history",
    "local_load",
    "neighbor_load",
    "distributed_load",
)
SENSORY_NULL_RECOVERY_STEPS = (("r0", 0), ("r1", 1), ("r2", 4))

ProbeObserver = Callable[["SensoryNullObservation"], object]
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def _digest_payload(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _vector_digest(vectors: Iterable[tuple[float, ...]]) -> str:
    return _digest_payload([list(vector) for vector in vectors])


@dataclass(frozen=True, slots=True)
class SensoryNullObservation:
    """One identical final probe after one controlled receptor history."""

    family_id: str
    history_id: str
    recovery_id: str
    history_steps: int
    recovery_steps: int
    probe_tick: int
    carrier_ids: tuple[str, ...]
    receptor_values: tuple[float, ...]
    probe_index: int
    neighbor_index: int
    history_receptor_digest: str
    receptor_digest: str

    def __post_init__(self) -> None:
        if self.family_id not in SENSORY_NULL_FAMILY_IDS:
            raise SensoryLoadRecoveryNullProbeError("unknown receptor family")
        if self.history_id not in SENSORY_NULL_HISTORY_IDS:
            raise SensoryLoadRecoveryNullProbeError("unknown receptor history")
        recovery = dict(SENSORY_NULL_RECOVERY_STEPS)
        if (
            self.recovery_id not in recovery
            or self.recovery_steps != recovery[self.recovery_id]
        ):
            raise SensoryLoadRecoveryNullProbeError(
                "recovery identity and steps must match"
            )
        if self.history_steps != 4:
            raise SensoryLoadRecoveryNullProbeError(
                "the preregistered history has exactly four steps"
            )
        if self.probe_tick != self.history_steps + self.recovery_steps:
            raise SensoryLoadRecoveryNullProbeError(
                "probe_tick must follow history and recovery"
            )
        if (
            not self.carrier_ids
            or len(set(self.carrier_ids)) != len(self.carrier_ids)
            or len(self.carrier_ids) != len(self.receptor_values)
        ):
            raise SensoryLoadRecoveryNullProbeError(
                "receptor values must match a unique finite carrier geometry"
            )
        if any(not math.isfinite(value) for value in self.receptor_values):
            raise SensoryLoadRecoveryNullProbeError(
                "receptor values must be finite"
            )
        if (
            self.probe_index == self.neighbor_index
            or not 0 <= self.probe_index < len(self.receptor_values)
            or not 0 <= self.neighbor_index < len(self.receptor_values)
        ):
            raise SensoryLoadRecoveryNullProbeError(
                "probe and neighbor indices must be distinct valid carriers"
            )
        if not _DIGEST.fullmatch(self.history_receptor_digest):
            raise SensoryLoadRecoveryNullProbeError(
                "history_receptor_digest must be a SHA-256 digest"
            )
        if not _DIGEST.fullmatch(self.receptor_digest):
            raise SensoryLoadRecoveryNullProbeError(
                "receptor_digest must be a SHA-256 digest"
            )

    @property
    def local_probe_value(self) -> float:
        return self.receptor_values[self.probe_index]

    @property
    def neighbor_probe_value(self) -> float:
        return self.receptor_values[self.neighbor_index]

    @property
    def receptor_magnitude(self) -> float:
        return sum(abs(value) for value in self.receptor_values)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "family_id": self.family_id,
            "history_id": self.history_id,
            "recovery_id": self.recovery_id,
            "history_steps": self.history_steps,
            "recovery_steps": self.recovery_steps,
            "probe_tick": self.probe_tick,
            "carrier_ids": list(self.carrier_ids),
            "receptor_values": list(self.receptor_values),
            "probe_index": self.probe_index,
            "neighbor_index": self.neighbor_index,
            "history_receptor_digest": self.history_receptor_digest,
            "receptor_digest": self.receptor_digest,
        }

    def digest(self) -> str:
        return _digest_payload(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class SensoryLoadRecoveryNullResult:
    """Canonical observer result; it contains no receptor writeback."""

    observations: tuple[SensoryNullObservation, ...]
    exact_receptor_collision: bool
    fixed_gain_collision: bool
    static_clipping_collision: bool
    max_value_difference: float
    max_local_difference: float
    max_neighbor_difference: float
    max_magnitude_difference: float
    writes_back: bool = False
    mechanism_released: bool = False

    def __post_init__(self) -> None:
        if self.writes_back or self.mechanism_released:
            raise SensoryLoadRecoveryNullProbeError(
                "a passive null result cannot write back or release a mechanism"
            )
        expected_keys = {
            (family_id, recovery_id, history_id)
            for family_id in SENSORY_NULL_FAMILY_IDS
            for recovery_id, _ in SENSORY_NULL_RECOVERY_STEPS
            for history_id in SENSORY_NULL_HISTORY_IDS
        }
        actual_keys = {
            (
                observation.family_id,
                observation.recovery_id,
                observation.history_id,
            )
            for observation in self.observations
        }
        if len(self.observations) != len(expected_keys) or actual_keys != expected_keys:
            raise SensoryLoadRecoveryNullProbeError(
                "result must contain every preregistered branch exactly once"
            )
        if tuple(
            sorted(
                self.observations,
                key=lambda item: (
                    item.family_id,
                    item.recovery_id,
                    item.history_id,
                ),
            )
        ) != self.observations:
            raise SensoryLoadRecoveryNullProbeError(
                "result observations must use canonical order"
            )
        expected_metrics = _group_metrics(self.observations)
        actual_metrics = (
            self.exact_receptor_collision,
            self.max_value_difference,
            self.max_local_difference,
            self.max_neighbor_difference,
            self.max_magnitude_difference,
        )
        if actual_metrics != expected_metrics:
            raise SensoryLoadRecoveryNullProbeError(
                "reported null metrics must match the observations"
            )
        if self.fixed_gain_collision != _transformed_collision(
            self.observations,
            lambda value: value * 0.5,
        ):
            raise SensoryLoadRecoveryNullProbeError(
                "fixed-gain baseline result is inconsistent"
            )
        if self.static_clipping_collision != _transformed_collision(
            self.observations,
            lambda value: max(-0.25, min(0.25, value)),
        ):
            raise SensoryLoadRecoveryNullProbeError(
                "static-clipping baseline result is inconsistent"
            )

    @property
    def observation_count(self) -> int:
        return len(self.observations)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "observations": [
                observation.canonical_payload()
                for observation in self.observations
            ],
            "exact_receptor_collision": self.exact_receptor_collision,
            "fixed_gain_collision": self.fixed_gain_collision,
            "static_clipping_collision": self.static_clipping_collision,
            "max_value_difference": self.max_value_difference,
            "max_local_difference": self.max_local_difference,
            "max_neighbor_difference": self.max_neighbor_difference,
            "max_magnitude_difference": self.max_magnitude_difference,
            "writes_back": self.writes_back,
            "mechanism_released": self.mechanism_released,
        }

    def digest(self) -> str:
        return _digest_payload(self.canonical_payload())


def _validated_order(
    values: Iterable[str],
    expected: tuple[str, ...],
    role: str,
) -> tuple[str, ...]:
    result = tuple(values)
    if len(result) != len(expected) or set(result) != set(expected):
        raise SensoryLoadRecoveryNullProbeError(
            f"{role} must contain each registered identifier exactly once"
        )
    return result


def _auditory_branch(
    history_id: str,
    recovery_steps: int,
) -> tuple[tuple[str, ...], tuple[float, ...], int, int, str]:
    config = AuditoryProbeConfig()
    silence = (0.0,) * config.frame_size
    local = synthesize_tone_frame(config, ((200.0, 0.8, 0.0),))
    neighbor = synthesize_tone_frame(config, ((400.0, 0.8, 0.0),))
    distributed = synthesize_tone_frame(
        config,
        (
            (200.0, 0.2, 0.0),
            (400.0, 0.2, 0.0),
            (800.0, 0.2, 0.0),
        ),
    )
    history_frame = {
        "rest_history": silence,
        "local_load": local,
        "neighbor_load": neighbor,
        "distributed_load": distributed,
    }[history_id]
    history = (history_frame,) * 4
    history_outputs = tuple(
        auditory_receptor_frame(frame, config)
        for frame in history
    )
    for frame in (silence,) * recovery_steps:
        auditory_receptor_frame(frame, config)
    probe = synthesize_tone_frame(config, ((200.0, 0.4, 0.0),))
    values = auditory_receptor_frame(probe, config)
    return config.channel_ids, values, 0, 1, _vector_digest(history_outputs)


_VISUAL_CONFIG = VisualGridConfig(
    source_width=8,
    source_height=6,
    grid_columns=4,
    grid_rows=3,
    frames_per_second=10.0,
)


def _visual_frame(
    contacts: dict[tuple[int, int, int], int],
) -> np.ndarray:
    frame = np.zeros(
        (_VISUAL_CONFIG.source_height, _VISUAL_CONFIG.source_width, 3),
        dtype=np.uint8,
    )
    block_height = _VISUAL_CONFIG.source_height // _VISUAL_CONFIG.grid_rows
    block_width = _VISUAL_CONFIG.source_width // _VISUAL_CONFIG.grid_columns
    for (row, column, channel), value in contacts.items():
        frame[
            row * block_height : (row + 1) * block_height,
            column * block_width : (column + 1) * block_width,
            channel,
        ] = value
    return frame


def _visual_index(row: int, column: int, channel: int) -> int:
    return (
        ((row * _VISUAL_CONFIG.grid_columns) + column) * 3
    ) + channel


def _visual_branch(
    history_id: str,
    recovery_steps: int,
) -> tuple[tuple[str, ...], tuple[float, ...], int, int, str]:
    receptor = LocalChannelGridReceptor(_VISUAL_CONFIG)
    history_frame = {
        "rest_history": _visual_frame({}),
        "local_load": _visual_frame({(1, 1, 1): 255}),
        "neighbor_load": _visual_frame({(1, 2, 1): 255}),
        "distributed_load": _visual_frame(
            {(1, 1, 1): 85, (1, 2, 1): 85, (0, 1, 1): 85}
        ),
    }[history_id]
    history_outputs = []
    frame_index = 0
    for _ in range(4):
        state = receptor.analyze(history_frame, frame_index=frame_index)
        history_outputs.append(state.channel_values)
        frame_index += 1
    for _ in range(recovery_steps):
        receptor.analyze(_visual_frame({}), frame_index=frame_index)
        frame_index += 1
    probe = _visual_frame({(1, 1, 1): 128})
    state = receptor.analyze(probe, frame_index=frame_index)
    return (
        state.carrier_ids,
        state.channel_values,
        _visual_index(1, 1, 1),
        _visual_index(1, 2, 1),
        _vector_digest(history_outputs),
    )


def _surface_branch(
    history_id: str,
    recovery_steps: int,
) -> tuple[tuple[str, ...], tuple[float, ...], int, int, str]:
    surface = ControlledReceptorSurface()
    history_contacts = {
        "rest_history": {},
        "local_load": {(1, 1): 0.9},
        "neighbor_load": {(1, 2): 0.9},
        "distributed_load": {
            (1, 1): 0.3,
            (1, 2): 0.3,
            (0, 1): 0.3,
        },
    }[history_id]
    history_outputs = tuple(
        stateless_surface_frame(surface, history_contacts).activation
        for _ in range(4)
    )
    for _ in range(recovery_steps):
        stateless_surface_frame(surface, {})
    frame = stateless_surface_frame(surface, {(1, 1): 0.4})
    return (
        surface.carrier_ids,
        frame.activation,
        surface.index((1, 1)),
        surface.index((1, 2)),
        _vector_digest(history_outputs),
    )


def _receptor_digest(
    family_id: str,
    probe_tick: int,
    carrier_ids: tuple[str, ...],
    values: tuple[float, ...],
) -> str:
    return _digest_payload(
        {
            "family_id": family_id,
            "probe_tick": probe_tick,
            "carrier_ids": list(carrier_ids),
            "receptor_values": list(values),
        }
    )


def _group_metrics(
    observations: tuple[SensoryNullObservation, ...],
) -> tuple[bool, float, float, float, float]:
    exact = True
    max_value = 0.0
    max_local = 0.0
    max_neighbor = 0.0
    max_magnitude = 0.0
    for family_id in SENSORY_NULL_FAMILY_IDS:
        for recovery_id, _ in SENSORY_NULL_RECOVERY_STEPS:
            group = tuple(
                observation
                for observation in observations
                if observation.family_id == family_id
                and observation.recovery_id == recovery_id
            )
            reference = next(
                observation
                for observation in group
                if observation.history_id == "rest_history"
            )
            for observation in group:
                exact = exact and (
                    observation.receptor_digest == reference.receptor_digest
                )
                max_value = max(
                    max_value,
                    max(
                        abs(left - right)
                        for left, right in zip(
                            reference.receptor_values,
                            observation.receptor_values,
                            strict=True,
                        )
                    ),
                )
                max_local = max(
                    max_local,
                    abs(
                        reference.local_probe_value
                        - observation.local_probe_value
                    ),
                )
                max_neighbor = max(
                    max_neighbor,
                    abs(
                        reference.neighbor_probe_value
                        - observation.neighbor_probe_value
                    ),
                )
                max_magnitude = max(
                    max_magnitude,
                    abs(
                        reference.receptor_magnitude
                        - observation.receptor_magnitude
                    ),
                )
    return exact, max_value, max_local, max_neighbor, max_magnitude


def _transformed_collision(
    observations: tuple[SensoryNullObservation, ...],
    transform: Callable[[float], float],
) -> bool:
    for family_id in SENSORY_NULL_FAMILY_IDS:
        for recovery_id, _ in SENSORY_NULL_RECOVERY_STEPS:
            group = tuple(
                observation
                for observation in observations
                if observation.family_id == family_id
                and observation.recovery_id == recovery_id
            )
            transformed = {
                tuple(transform(value) for value in observation.receptor_values)
                for observation in group
            }
            if len(transformed) != 1:
                return False
    return True


def run_sensory_load_recovery_null_probe(
    *,
    family_order: Iterable[str] = SENSORY_NULL_FAMILY_IDS,
    history_order: Iterable[str] = SENSORY_NULL_HISTORY_IDS,
    recovery_order: Iterable[str] = tuple(
        recovery_id for recovery_id, _ in SENSORY_NULL_RECOVERY_STEPS
    ),
    observer: ProbeObserver | None = None,
) -> SensoryLoadRecoveryNullResult:
    """Run Methodik 025 without introducing receptor state or writeback."""

    family_order = _validated_order(
        family_order,
        SENSORY_NULL_FAMILY_IDS,
        "family_order",
    )
    history_order = _validated_order(
        history_order,
        SENSORY_NULL_HISTORY_IDS,
        "history_order",
    )
    recovery_ids = tuple(item[0] for item in SENSORY_NULL_RECOVERY_STEPS)
    recovery_order = _validated_order(
        recovery_order,
        recovery_ids,
        "recovery_order",
    )
    recovery_steps_by_id = dict(SENSORY_NULL_RECOVERY_STEPS)
    runners = {
        "auditory": _auditory_branch,
        "controlled_surface": _surface_branch,
        "visual": _visual_branch,
    }

    observations = []
    for family_id in family_order:
        for recovery_id in recovery_order:
            recovery_steps = recovery_steps_by_id[recovery_id]
            for history_id in history_order:
                (
                    carrier_ids,
                    values,
                    probe_index,
                    neighbor_index,
                    history_digest,
                ) = runners[family_id](history_id, recovery_steps)
                probe_tick = 4 + recovery_steps
                observation = SensoryNullObservation(
                    family_id=family_id,
                    history_id=history_id,
                    recovery_id=recovery_id,
                    history_steps=4,
                    recovery_steps=recovery_steps,
                    probe_tick=probe_tick,
                    carrier_ids=carrier_ids,
                    receptor_values=values,
                    probe_index=probe_index,
                    neighbor_index=neighbor_index,
                    history_receptor_digest=history_digest,
                    receptor_digest=_receptor_digest(
                        family_id,
                        probe_tick,
                        carrier_ids,
                        values,
                    ),
                )
                before = observation.digest()
                if observer is not None:
                    observer(observation)
                if observation.digest() != before:
                    raise SensoryLoadRecoveryNullProbeError(
                        "observer changed an immutable null-probe observation"
                    )
                observations.append(observation)

    canonical = tuple(
        sorted(
            observations,
            key=lambda item: (
                item.family_id,
                item.recovery_id,
                item.history_id,
            ),
        )
    )
    (
        exact,
        max_value,
        max_local,
        max_neighbor,
        max_magnitude,
    ) = _group_metrics(canonical)
    return SensoryLoadRecoveryNullResult(
        observations=canonical,
        exact_receptor_collision=exact,
        fixed_gain_collision=_transformed_collision(
            canonical,
            lambda value: value * 0.5,
        ),
        static_clipping_collision=_transformed_collision(
            canonical,
            lambda value: max(-0.25, min(0.25, value)),
        ),
        max_value_difference=max_value,
        max_local_difference=max_local,
        max_neighbor_difference=max_neighbor,
        max_magnitude_difference=max_magnitude,
    )


def sensory_load_recovery_null_public_roles(
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    return (
        tuple(item.name for item in fields(SensoryNullObservation)),
        tuple(item.name for item in fields(SensoryLoadRecoveryNullResult)),
    )
