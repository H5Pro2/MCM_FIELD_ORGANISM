"""Private S1-VN PPB-1 fixtures, baselines, and execution-locked matrix."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re

from ._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from ._ppb1_reference import (
    PPB1BankConfig,
    advance_ppb1_bank,
    initial_ppb1_bank_state,
    normalized_mean_l1_distance,
)
from .receptor_contract import ReceptorContactFrame


S1VN_SCHEMA_VERSION = "ppb1.s1vn.private.v1"
S1VN_PROFILE_ID = "controlled"
S1VN_PARAMETER_IDS = ("P0", "P1", "P2")
S1VN_FIXTURE_IDS = tuple(f"F{index:02d}" for index in range(1, 9))
S1VN_BASELINE_IDS = tuple(f"B{index:02d}" for index in range(1, 8))
S1VN_FAMILY_IDS = ("PPB1",) + S1VN_BASELINE_IDS
S1VN_MODALITY_IDS = ("auditory", "visual")
S1VN_EXPECTED_CASE_COUNT = 384
S1VN_EXPECTED_PPB_CALLS = 9296
S1VN_EXPECTED_BASELINE_CALLS = 65072
S1VN_EXPECTED_TOTAL_CALLS = 74368

S1VN_INVALID_CONTRACT = "S1VN_INVALID_CONTRACT"
S1VN_INVALID_FIXTURE = "S1VN_INVALID_FIXTURE"
S1VN_INVALID_BASELINE = "S1VN_INVALID_BASELINE"
S1VN_MATRIX_EXECUTION_BLOCKED = "S1VN_MATRIX_EXECUTION_BLOCKED"

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S1VNMatrixError(ValueError):
    """One fail-closed S1-VN private matrix contract violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def s1vn_parameter_records() -> dict[str, PPB1ProfileParameters]:
    """Return fresh canonical copies of the three pre-registered records."""

    return {
        "P0": PPB1ProfileParameters(
            PPB1ModalityParameters(8, 0.04, 0.10, 4, 512),
            PPB1ModalityParameters(4, 0.03, 0.10, 4, 128),
        ),
        "P1": PPB1ProfileParameters(
            PPB1ModalityParameters(16, 0.08, 0.20, 4, 1024),
            PPB1ModalityParameters(8, 0.06, 0.20, 4, 256),
        ),
        "P2": PPB1ProfileParameters(
            PPB1ModalityParameters(32, 0.16, 0.40, 8, 2048),
            PPB1ModalityParameters(16, 0.12, 0.40, 6, 512),
        ),
    }


def s1vn_config(parameter_id: str, modality_id: str) -> PPB1BankConfig:
    if parameter_id not in S1VN_PARAMETER_IDS:
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT, f"unknown parameter_id: {parameter_id!r}"
        )
    if modality_id not in S1VN_MODALITY_IDS:
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT, f"unknown modality_id: {modality_id!r}"
        )
    binding = bind_ppb1_receptor_profile(
        S1VN_PROFILE_ID, s1vn_parameter_records()[parameter_id]
    )
    return (
        binding.auditory_config
        if modality_id == "auditory"
        else binding.visual_config
    )


def s1vn_fixture_call_count(config: PPB1BankConfig, fixture_id: str) -> int:
    if fixture_id == "F01":
        return 9
    if fixture_id == "F02":
        return 6
    if fixture_id == "F03":
        return 10
    if fixture_id == "F04":
        return 3
    if fixture_id == "F05":
        return 11
    if fixture_id == "F06":
        return config.capacity + 2
    if fixture_id == "F07":
        return config.expire_after_steps + 1
    if fixture_id == "F08":
        return config.expire_after_steps
    raise S1VNMatrixError(
        S1VN_INVALID_FIXTURE, f"unknown fixture_id: {fixture_id!r}"
    )


def _constant(dimension: int, value: float) -> tuple[float, ...]:
    return (value,) * dimension


def _fill_codewords(count: int) -> tuple[int, ...]:
    selected: list[int] = []
    for candidate in range(1 << 12):
        if all((candidate ^ prior).bit_count() >= 3 for prior in selected):
            selected.append(candidate)
            if len(selected) == count:
                return tuple(selected)
    raise S1VNMatrixError(
        S1VN_INVALID_FIXTURE, "insufficient deterministic fill codewords"
    )


def _fill_vector(codeword: int, dimension: int) -> tuple[float, ...]:
    return tuple(
        0.9 if (codeword >> (index % 12)) & 1 else 0.1
        for index in range(dimension)
    )


def _fixture_values(
    config: PPB1BankConfig, fixture_id: str
) -> tuple[tuple[float, ...], ...]:
    dimension = len(config.carrier_ids)
    low = _constant(dimension, 0.20)
    high = _constant(dimension, 0.80)
    near_minus = _constant(dimension, 0.19)
    near_plus = _constant(dimension, 0.21)
    middle = _constant(dimension, 0.50)

    if fixture_id == "F01":
        return (low,) * 9
    if fixture_id == "F02":
        return (low, near_minus, near_plus, near_minus, near_plus, low)
    if fixture_id == "F03":
        return (low, high) * 4 + (low, high)
    if fixture_id == "F04":
        return (low, high, middle)
    if fixture_id == "F05":
        drift = tuple(
            _constant(dimension, 0.20 + 0.06 * index)
            for index in range(1, 10)
        )
        return drift + (low, high)
    if fixture_id == "F06":
        codewords = _fill_codewords(config.capacity + 1)
        fills = tuple(_fill_vector(code, dimension) for code in codewords)
        return fills + (fills[0],)
    if fixture_id == "F07":
        return (low,) + (high,) * (config.expire_after_steps - 1) + (low,)
    if fixture_id == "F08":
        return (low,) + (high,) * (config.expire_after_steps - 2) + (low,)
    raise S1VNMatrixError(
        S1VN_INVALID_FIXTURE, f"unknown fixture_id: {fixture_id!r}"
    )


def build_s1vn_fixture(
    config: PPB1BankConfig, fixture_id: str
) -> tuple[ReceptorContactFrame, ...]:
    """Materialize one registered history without advancing any state."""

    if not isinstance(config, PPB1BankConfig):
        raise S1VNMatrixError(S1VN_INVALID_FIXTURE, "config is required")
    values = _fixture_values(config, fixture_id)
    if len(values) != s1vn_fixture_call_count(config, fixture_id):
        raise S1VNMatrixError(
            S1VN_INVALID_FIXTURE, "fixture length does not match its contract"
        )
    clock_id = f"s1vn.{config.modality_id}.source"
    return tuple(
        ReceptorContactFrame(
            config.modality_id,
            config.geometry_id,
            f"s1vn.{fixture_id.lower()}.{config.modality_id}.{index:06d}",
            clock_id,
            index - 1,
            index,
            config.carrier_ids,
            vector,
        )
        for index, vector in enumerate(values, start=1)
    )


@dataclass(frozen=True, slots=True)
class S1VNBaselineState:
    adapter_id: str
    dimension: int
    capacity: int
    accepted_step_count: int
    history: tuple[tuple[float, ...], ...] = ()
    trace: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        if self.adapter_id not in S1VN_BASELINE_IDS:
            raise S1VNMatrixError(S1VN_INVALID_BASELINE, "unknown adapter_id")
        if self.dimension <= 0 or self.capacity <= 0 or self.accepted_step_count < 0:
            raise S1VNMatrixError(
                S1VN_INVALID_BASELINE, "invalid baseline dimensions or counters"
            )
        for vector in self.history:
            _validate_vector(vector, self.dimension)
        if len(self.history) > self.capacity:
            raise S1VNMatrixError(
                S1VN_INVALID_BASELINE, "baseline history exceeds capacity"
            )
        if self.trace is not None:
            _validate_vector(self.trace, self.dimension)

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VN_SCHEMA_VERSION,
            "adapter_id": self.adapter_id,
            "dimension": self.dimension,
            "capacity": self.capacity,
            "accepted_step_count": self.accepted_step_count,
            "history": [list(vector) for vector in self.history],
            "trace": None if self.trace is None else list(self.trace),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class S1VNBaselineReadout:
    adapter_id: str
    event: str
    distance: float | None
    logical_value_count: int
    poststate_digest: str

    def __post_init__(self) -> None:
        if self.adapter_id not in S1VN_BASELINE_IDS or not _DIGEST.fullmatch(
            self.poststate_digest
        ):
            raise S1VNMatrixError(S1VN_INVALID_BASELINE, "invalid baseline readout")
        if self.distance is not None and (
            not math.isfinite(self.distance) or self.distance < 0.0
        ):
            raise S1VNMatrixError(S1VN_INVALID_BASELINE, "invalid readout distance")


@dataclass(frozen=True, slots=True)
class S1VNBaselineStepResult:
    poststate: S1VNBaselineState
    readout: S1VNBaselineReadout

    def __post_init__(self) -> None:
        if self.readout.poststate_digest != self.poststate.digest():
            raise S1VNMatrixError(
                S1VN_INVALID_BASELINE, "baseline result is not atomic"
            )


def _validate_vector(values: object, dimension: int) -> tuple[float, ...]:
    try:
        vector = tuple(float(value) for value in values)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise S1VNMatrixError(
            S1VN_INVALID_BASELINE, "baseline vector must be numeric"
        ) from exc
    if (
        len(vector) != dimension
        or any(not math.isfinite(value) or abs(value) > 1.0 for value in vector)
    ):
        raise S1VNMatrixError(
            S1VN_INVALID_BASELINE,
            "baseline vector must match dimension and remain in [-1,1]",
        )
    return vector


def initial_s1vn_baseline_state(
    adapter_id: str, config: PPB1BankConfig
) -> S1VNBaselineState:
    if adapter_id not in S1VN_BASELINE_IDS:
        raise S1VNMatrixError(
            S1VN_INVALID_BASELINE, f"unknown adapter_id: {adapter_id!r}"
        )
    return S1VNBaselineState(
        adapter_id, len(config.carrier_ids), config.capacity, 0
    )


def _nearest(
    vector: tuple[float, ...], candidates: tuple[tuple[float, ...], ...]
) -> float | None:
    if not candidates:
        return None
    return min(normalized_mean_l1_distance(vector, item) for item in candidates)


def _mean(vectors: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    return tuple(
        math.fsum(vector[index] for vector in vectors) / len(vectors)
        for index in range(len(vectors[0]))
    )


def advance_s1vn_baseline(
    adapter_id: str,
    config: PPB1BankConfig,
    prestate: S1VNBaselineState,
    values: tuple[float, ...],
) -> S1VNBaselineStepResult:
    """Advance one pure comparison adapter on one reduced receptor vector."""

    vector = _validate_vector(values, len(config.carrier_ids))
    if (
        adapter_id != prestate.adapter_id
        or prestate.dimension != len(config.carrier_ids)
        or prestate.capacity != config.capacity
    ):
        raise S1VNMatrixError(
            S1VN_INVALID_BASELINE, "baseline prestate does not match config"
        )
    history = prestate.history
    trace = prestate.trace
    distance: float | None = None
    event = "UNMATCHED"

    if adapter_id == "B01":
        distance = _nearest(vector, history)
        event = "MATCHED" if distance is not None and distance <= config.match_threshold else "STORED"
        history = (history + (vector,))[-config.capacity :]
    elif adapter_id == "B02":
        distance = None if not history else normalized_mean_l1_distance(vector, _mean(history))
        event = "MATCHED" if distance is not None and distance <= config.match_threshold else "UPDATED"
        history = (history + (vector,))[-config.capacity :]
        trace = _mean(history)
    elif adapter_id == "B03":
        distance = _nearest(vector, history)
        if distance is not None and distance <= config.match_threshold:
            event = "MATCHED"
        elif len(history) < config.capacity:
            history = history + (vector,)
            event = "STORED"
        else:
            event = "FULL_UNMATCHED"
    elif adapter_id == "B04":
        distance = None if trace is None else normalized_mean_l1_distance(vector, trace)
        event = "MATCHED" if distance is not None and distance <= config.match_threshold else "UPDATED"
        trace = vector if trace is None else tuple(
            (1.0 - config.update_rate) * old + config.update_rate * current
            for old, current in zip(trace, vector, strict=True)
        )
    elif adapter_id == "B05":
        distance = None if trace is None else normalized_mean_l1_distance(vector, trace)
        event = "MATCHED" if distance is not None and distance <= config.match_threshold else "UPDATED"
        trace = vector if trace is None else tuple(
            max(-1.0, min(1.0, (1.0 - config.update_rate) * old + current))
            for old, current in zip(trace, vector, strict=True)
        )
    elif adapter_id == "B06":
        distance = None if trace is None else normalized_mean_l1_distance(vector, trace)
        event = "MATCHED" if distance is not None and distance <= config.match_threshold else "UPDATED"
        trace = vector if trace is None else tuple(
            max(-1.0, min(1.0, old + current))
            for old, current in zip(trace, vector, strict=True)
        )
    elif adapter_id == "B07":
        event = "OFF"
    else:
        raise S1VNMatrixError(
            S1VN_INVALID_BASELINE, f"unknown adapter_id: {adapter_id!r}"
        )

    poststate = S1VNBaselineState(
        adapter_id,
        prestate.dimension,
        prestate.capacity,
        prestate.accepted_step_count + 1,
        history,
        trace,
    )
    logical_values = sum(len(item) for item in history)
    if trace is not None:
        logical_values += len(trace)
    readout = S1VNBaselineReadout(
        adapter_id, event, distance, logical_values, poststate.digest()
    )
    return S1VNBaselineStepResult(poststate, readout)


@dataclass(frozen=True, slots=True)
class S1VNPathPlan:
    path_id: str
    family_id: str
    parameter_id: str
    modality_id: str
    fixture_id: str
    expected_call_count: int
    config_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VN_SCHEMA_VERSION,
            "path_id": self.path_id,
            "family_id": self.family_id,
            "parameter_id": self.parameter_id,
            "modality_id": self.modality_id,
            "fixture_id": self.fixture_id,
            "expected_call_count": self.expected_call_count,
            "config_digest": self.config_digest,
        }


def s1vn_matrix_plan() -> tuple[S1VNPathPlan, ...]:
    """Return all 384 registered paths without executing a state step."""

    paths: list[S1VNPathPlan] = []
    for family_id in S1VN_FAMILY_IDS:
        for parameter_id in S1VN_PARAMETER_IDS:
            for modality_id in S1VN_MODALITY_IDS:
                config = s1vn_config(parameter_id, modality_id)
                for fixture_id in S1VN_FIXTURE_IDS:
                    paths.append(
                        S1VNPathPlan(
                            f"S1VN-{len(paths) + 1:03d}",
                            family_id,
                            parameter_id,
                            modality_id,
                            fixture_id,
                            s1vn_fixture_call_count(config, fixture_id),
                            config.digest(),
                        )
                    )
    return tuple(paths)


@dataclass(frozen=True, slots=True)
class S1VNStepObservation:
    step: int
    event: str
    distance: float | None
    logical_value_count: int
    occupied_slot_count: int
    stabilized_slot_count: int
    selected_slot_id: str | None
    selected_state_displacement: float | None

    def canonical_payload(self) -> dict[str, object]:
        return {
            "step": self.step,
            "event": self.event,
            "distance": self.distance,
            "logical_value_count": self.logical_value_count,
            "occupied_slot_count": self.occupied_slot_count,
            "stabilized_slot_count": self.stabilized_slot_count,
            "selected_slot_id": self.selected_slot_id,
            "selected_state_displacement": self.selected_state_displacement,
        }


@dataclass(frozen=True, slots=True)
class S1VNCaseReceipt:
    path_id: str
    family_id: str
    accepted_call_count: int
    events: tuple[str, ...]
    observations: tuple[S1VNStepObservation, ...]
    input_history_digest: str
    final_state_digest: str

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VN_SCHEMA_VERSION,
            "path_id": self.path_id,
            "family_id": self.family_id,
            "accepted_call_count": self.accepted_call_count,
            "events": list(self.events),
            "observations": [item.canonical_payload() for item in self.observations],
            "input_history_digest": self.input_history_digest,
            "final_state_digest": self.final_state_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _execute_frames(
    path_id: str,
    family_id: str,
    config: PPB1BankConfig,
    frames: tuple[ReceptorContactFrame, ...],
) -> S1VNCaseReceipt:
    events: list[str] = []
    observations: list[S1VNStepObservation] = []
    if family_id == "PPB1":
        state = initial_ppb1_bank_state(config)
        formation_values: dict[str, tuple[float, ...]] = {}
        for frame in frames:
            result = advance_ppb1_bank(config, state, frame)
            state = result.poststate
            events.append(result.readout.event)
            selected_id = result.readout.slot_id
            if result.readout.event in {"CREATED", "REPLACED"}:
                formation_values[selected_id] = tuple(frame.values)
            formation = formation_values[selected_id]
            displacement = normalized_mean_l1_distance(
                result.readout.prototype_values, formation
            )
            occupied = tuple(slot for slot in state.slots if slot.occupied)
            observations.append(
                S1VNStepObservation(
                    state.accepted_step_count,
                    result.readout.event,
                    result.readout.match_distance,
                    sum(len(slot.prototype_values) for slot in occupied),
                    len(occupied),
                    sum(
                        slot.support_count == config.stable_after
                        for slot in occupied
                    ),
                    selected_id,
                    displacement,
                )
            )
        final_digest = state.digest()
    elif family_id in S1VN_BASELINE_IDS:
        baseline = initial_s1vn_baseline_state(family_id, config)
        for frame in frames:
            result = advance_s1vn_baseline(
                family_id, config, baseline, frame.values
            )
            baseline = result.poststate
            events.append(result.readout.event)
            observations.append(
                S1VNStepObservation(
                    baseline.accepted_step_count,
                    result.readout.event,
                    result.readout.distance,
                    result.readout.logical_value_count,
                    len(baseline.history),
                    0,
                    None,
                    None,
                )
            )
        final_digest = baseline.digest()
    else:
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT, f"unknown family_id: {family_id!r}"
        )
    history_digest = _digest(
        [
            {
                "modality_id": frame.modality_id,
                "geometry_id": frame.geometry_id,
                "clock_id": frame.clock_id,
                "window_start_tick": frame.window_start_tick,
                "window_end_tick": frame.window_end_tick,
                "carrier_ids": list(frame.carrier_ids),
                "values": list(frame.values),
            }
            for frame in frames
        ]
    )
    return S1VNCaseReceipt(
        path_id,
        family_id,
        len(frames),
        tuple(events),
        tuple(observations),
        history_digest,
        final_digest,
    )


def run_s1vn_miniature_contract(
    family_id: str,
    config: PPB1BankConfig,
    frames: tuple[ReceptorContactFrame, ...],
) -> S1VNCaseReceipt:
    """Run at most four non-matrix frames for private wiring tests."""

    if not frames or len(frames) > 4:
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT,
            "miniature contract requires one to four frames",
        )
    if any(not frame.snapshot_id.startswith("s1vn.contract.") for frame in frames):
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT,
            "registered matrix frames are forbidden in miniature execution",
        )
    return _execute_frames("S1VN-CONTRACT", family_id, config, frames)


def _execute_registered_path(path: S1VNPathPlan) -> S1VNCaseReceipt:
    config = s1vn_config(path.parameter_id, path.modality_id)
    if config.digest() != path.config_digest:
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT, "registered path config digest drifted"
        )
    frames = build_s1vn_fixture(config, path.fixture_id)
    if len(frames) != path.expected_call_count:
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT, "registered path call count drifted"
        )
    return _execute_frames(path.path_id, path.family_id, config, frames)


@dataclass(frozen=True, slots=True)
class S1VNMatrixResult:
    plan_digest: str
    case_receipts: tuple[S1VNCaseReceipt, ...]
    accepted_call_count: int

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema_version": S1VN_SCHEMA_VERSION,
            "plan_digest": self.plan_digest,
            "case_receipts": [item.canonical_payload() for item in self.case_receipts],
            "accepted_call_count": self.accepted_call_count,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _execute_registered_matrix() -> S1VNMatrixResult:
    """Complete execution body kept unreachable behind the S1-VN gate."""

    preparation = prepare_s1vn_matrix_runner()
    plan = s1vn_matrix_plan()
    receipts = tuple(_execute_registered_path(path) for path in plan)
    accepted = sum(receipt.accepted_call_count for receipt in receipts)
    if (
        len(receipts) != preparation.case_count
        or accepted != preparation.total_call_count
        or tuple(receipt.path_id for receipt in receipts)
        != tuple(path.path_id for path in plan)
    ):
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT, "executed matrix does not match its plan"
        )
    return S1VNMatrixResult(preparation.plan_digest, receipts, accepted)


@dataclass(frozen=True, slots=True)
class S1VNRunnerPreparation:
    plan_digest: str
    case_count: int
    ppb_call_count: int
    baseline_call_count: int
    total_call_count: int
    execution_authorized: bool
    accepted_call_count: int


def prepare_s1vn_matrix_runner() -> S1VNRunnerPreparation:
    plan = s1vn_matrix_plan()
    ppb_calls = sum(
        path.expected_call_count for path in plan if path.family_id == "PPB1"
    )
    baseline_calls = sum(
        path.expected_call_count for path in plan if path.family_id != "PPB1"
    )
    if (
        len(plan) != S1VN_EXPECTED_CASE_COUNT
        or ppb_calls != S1VN_EXPECTED_PPB_CALLS
        or baseline_calls != S1VN_EXPECTED_BASELINE_CALLS
        or ppb_calls + baseline_calls != S1VN_EXPECTED_TOTAL_CALLS
        or len({path.path_id for path in plan}) != len(plan)
    ):
        raise S1VNMatrixError(
            S1VN_INVALID_CONTRACT, "matrix plan does not match S1-VM"
        )
    return S1VNRunnerPreparation(
        _digest([path.canonical_payload() for path in plan]),
        len(plan),
        ppb_calls,
        baseline_calls,
        ppb_calls + baseline_calls,
        False,
        0,
    )


def execute_s1vn_matrix() -> None:
    """Refuse the 384-path execution until a later explicit release step."""

    raise S1VNMatrixError(
        S1VN_MATRIX_EXECUTION_BLOCKED,
        "S1-VN implements planning and wiring only; matrix execution is blocked",
    )
