"""Private controlled audio-video previous-state contribution probe."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
import threading
import time

import numpy as np

from .audio_video_neutral_field_runtime import advance_audio_video_receptor_sequences
from .controlled_audio_video_test_world import (
    _scheduled_phase_sequences,
    controlled_history_holdout_world_family,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .previous_state_contribution_hook import apply_previous_state_operator


_CLOCK_ID = "organism.controlled_previous_state"
_TICKS_PER_SECOND = 1_000_000.0
_OPERATORS = (None, "identity", "zero")
_FORWARD = tuple(
    (world_id, operator)
    for operator in _OPERATORS
    for world_id in ("same", "changed")
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("ascii")).hexdigest()


def _sequence_payload(sequences) -> list[dict[str, object]]:
    return [
        {
            "modality_id": sequence.modality_id,
            "geometry_id": sequence.geometry_id,
            "clock_id": sequence.clock_id,
            "frames": [
                {
                    "start": item.field_time.window_start_tick,
                    "end": item.field_time.window_end_tick,
                    "carrier_ids": list(item.frame.carrier_ids),
                    "values": list(item.frame.values),
                }
                for item in sequence.frames
            ],
        }
        for sequence in sequences
    ]


def _state(field) -> tuple[np.ndarray, np.ndarray]:
    activation = np.asarray(
        [neuron.activation for neuron in field.layer.neurons], dtype=np.float64
    )
    afterimage = np.asarray(
        [neuron.afterimage for neuron in field.layer.neurons], dtype=np.float64
    )
    return activation, afterimage


def _state_summary(field) -> dict[str, object]:
    activation, afterimage = _state(field)
    return {
        "field_digest": field.snapshot().digest(),
        "layer_digest": field.layer.digest(),
        "activation_digest": hashlib.sha256(activation.tobytes()).hexdigest(),
        "afterimage_digest": hashlib.sha256(afterimage.tobytes()).hexdigest(),
        "activation": activation.tolist(),
        "afterimage": afterimage.tolist(),
    }


def _observed_process_counts() -> dict[str, int | None]:
    handles = None
    if os.name == "nt":
        import ctypes

        count = ctypes.c_ulong()
        kernel32 = ctypes.windll.kernel32
        if kernel32.GetProcessHandleCount(kernel32.GetCurrentProcess(), ctypes.byref(count)):
            handles = int(count.value)
    return {
        "thread_count": threading.active_count(),
        "handle_count": handles,
    }


@dataclass(frozen=True, slots=True)
class _ArmResult:
    pass_id: int
    order_index: int
    world_key: str
    operator: str | None
    world_digest: str
    history_sequence_digest: str
    holdout_sequence_digest: str
    history_state: dict[str, object]
    holdout_state: dict[str, object]
    receptor_contract: dict[str, object]
    duration_seconds: float

    def payload(self) -> dict[str, object]:
        return {
            "pass_id": self.pass_id,
            "order_index": self.order_index,
            "world_key": self.world_key,
            "operator": self.operator,
            "world_digest": self.world_digest,
            "history_sequence_digest": self.history_sequence_digest,
            "holdout_sequence_digest": self.holdout_sequence_digest,
            "history_state": self.history_state,
            "holdout_state": self.holdout_state,
            "receptor_contract": self.receptor_contract,
            "duration_seconds": self.duration_seconds,
        }


def _run_arm(pass_id: int, order_index: int, world_key: str, operator: str | None):
    worlds = dict(zip(("same", "changed"), controlled_history_holdout_world_family()))
    world = worlds[world_key]
    field_config = NeutralLocalFieldSubstrateConfig(1.0)
    afterimage_config = NeutralFastAfterimageConfig(0.5)
    audio_source, video_source, auditory_path, visual_receptor = world.open_sources()
    field = None
    audio_cursor = 0
    video_cursor = 0
    history_payloads = []
    holdout_payload = None
    history_state = None
    started = time.perf_counter()
    for phase_index, phase in enumerate(world.phases):
        sequences = _scheduled_phase_sequences(
            world,
            phase,
            audio_source,
            video_source,
            auditory_path,
            visual_receptor,
            audio_frame_start=audio_cursor,
            video_frame_start=video_cursor,
            clock_id=_CLOCK_ID,
            ticks_per_second=_TICKS_PER_SECOND,
        )
        payload = _sequence_payload(sequences)
        if phase_index < len(world.phases) - 1:
            history_payloads.append(payload)
        else:
            holdout_payload = payload
            history_state = _state_summary(field)
            field = apply_previous_state_operator(
                field, previous_state_operator=operator
            )
        run = advance_audio_video_receptor_sequences(
            sequences,
            visual_receptor,
            field_config,
            afterimage_config=afterimage_config,
            initial_field=field,
            ticks_per_second=_TICKS_PER_SECOND,
        )
        field = run.field_run.field
        audio_cursor += round(phase.duration_seconds / world.audio_config.hop_seconds)
        video_cursor += round(
            phase.duration_seconds * world.visual_config.frames_per_second
        )
    if history_state is None or holdout_payload is None:
        raise RuntimeError("probe did not reach its fixed holdout")
    elapsed = time.perf_counter() - started
    return _ArmResult(
        pass_id,
        order_index,
        world_key,
        operator,
        world.digest(),
        _digest(history_payloads),
        _digest(holdout_payload),
        history_state,
        _state_summary(field),
        {
            "clock_id": _CLOCK_ID,
            "ticks_per_second": _TICKS_PER_SECOND,
            "audio_sample_rate": world.audio_config.sample_rate,
            "audio_hop_size": world.audio_config.hop_size,
            "audio_hop_seconds": world.audio_config.hop_seconds,
            "video_frames_per_second": world.visual_config.frames_per_second,
            "audio_holdout_frames": len(holdout_payload[0]["frames"]),
            "video_holdout_frames": len(holdout_payload[1]["frames"]),
            "neuron_count": len(field.layer.neurons),
        },
        elapsed,
    )


def _difference(left: dict[str, object], right: dict[str, object]) -> dict[str, object]:
    result = {}
    for component in ("activation", "afterimage"):
        delta = np.asarray(left[component]) - np.asarray(right[component])
        result[f"{component}_l2"] = float(np.linalg.norm(delta))
        result[f"{component}_linf"] = float(np.max(np.abs(delta)))
    result["field_digest_equal"] = left["field_digest"] == right["field_digest"]
    result["layer_digest_equal"] = left["layer_digest"] == right["layer_digest"]
    return result


def run_controlled_av_previous_state_probe() -> dict[str, object]:
    """Execute the twelve preregistered arms and evaluate fixed controls."""

    process_before = _observed_process_counts()
    started = time.perf_counter()
    arms = []
    for pass_id, order in ((1, _FORWARD), (2, tuple(reversed(_FORWARD)))):
        for order_index, (world_key, operator) in enumerate(order):
            arms.append(_run_arm(pass_id, order_index, world_key, operator))

    lookup = {
        (arm.pass_id, arm.world_key, arm.operator): arm for arm in arms
    }
    contrasts = {}
    for pass_id in (1, 2):
        for operator in _OPERATORS:
            same = lookup[(pass_id, "same", operator)].holdout_state
            changed = lookup[(pass_id, "changed", operator)].holdout_state
            contrasts[f"pass_{pass_id}.{operator or 'none'}.same_vs_changed"] = (
                _difference(same, changed)
            )

    holdout_equal = len({arm.holdout_sequence_digest for arm in arms}) == 1
    none_identity_equal = all(
        lookup[(pass_id, world_key, None)].holdout_state
        == lookup[(pass_id, world_key, "identity")].holdout_state
        for pass_id in (1, 2)
        for world_key in ("same", "changed")
    )
    repeat_equal = all(
        lookup[(1, world_key, operator)].holdout_state
        == lookup[(2, world_key, operator)].holdout_state
        for world_key in ("same", "changed")
        for operator in _OPERATORS
    )
    zero_equal = all(
        lookup[(pass_id, "same", "zero")].holdout_state
        == lookup[(pass_id, "changed", "zero")].holdout_state
        for pass_id in (1, 2)
    )
    none_differs = all(
        lookup[(pass_id, "same", None)].holdout_state["field_digest"]
        != lookup[(pass_id, "changed", None)].holdout_state["field_digest"]
        for pass_id in (1, 2)
    )
    controls = {
        "holdout_receptor_sequences_exactly_equal": holdout_equal,
        "none_identity_exactly_equal": none_identity_equal,
        "reverse_order_repetition_exactly_equal": repeat_equal,
        "zero_same_changed_exactly_equal": zero_equal,
        "none_same_changed_different": none_differs,
    }
    decision = (
        "CAUSAL_FAST_PREVIOUS_STATE_CONTRIBUTION"
        if all(controls.values())
        else "TECHNICALLY_UNDECIDABLE"
    )
    return {
        "schema": "controlled_av_previous_state_probe.v1",
        "run_number": 187,
        "arm_count": len(arms),
        "fresh_field_per_arm": True,
        "dissipation_config": None,
        "arms": [arm.payload() for arm in arms],
        "contrasts": contrasts,
        "controls": controls,
        "decision": decision,
        "process_observation": {
            "before": process_before,
            "after": _observed_process_counts(),
            "elapsed_seconds": time.perf_counter() - started,
        },
        "claims": {
            "fast_previous_state_contribution": all(controls.values()),
            "memory": False,
            "organization": False,
            "topology": False,
            "meaning": False,
            "semantics": False,
            "ai": False,
        },
    }
