"""Pure B0-B5 state references for the S2 technical runner."""

from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np


class S2ReferenceBaselineError(ValueError):
    """Raised when an S2 reference model leaves its bound technical domain."""


_MODEL_IDS = ("b0", "b1", "b2", "b3", "b4", "b5")
_BOUND_TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class S2ReferenceModelConfig:
    capacity_ratio: float = 8.0
    coupling_rate_per_second: float = 0.25
    afterimage_time_seconds: float = 0.5
    leak_rate_per_second: float = 0.0
    gain_reference_seconds: float = 1.0
    rk4_substeps: int = 16

    def __post_init__(self) -> None:
        values = (
            self.capacity_ratio,
            self.coupling_rate_per_second,
            self.afterimage_time_seconds,
            self.leak_rate_per_second,
            self.gain_reference_seconds,
        )
        if any(not math.isfinite(float(value)) for value in values):
            raise S2ReferenceBaselineError("S2 model values must be finite")
        if self.capacity_ratio <= 1.0:
            raise S2ReferenceBaselineError("capacity ratio must exceed one")
        if self.coupling_rate_per_second < 0.0:
            raise S2ReferenceBaselineError("coupling rate must be nonnegative")
        if self.afterimage_time_seconds <= 0.0:
            raise S2ReferenceBaselineError("afterimage time must be positive")
        if self.leak_rate_per_second < 0.0:
            raise S2ReferenceBaselineError("leak rate must be nonnegative")
        if self.gain_reference_seconds <= 0.0:
            raise S2ReferenceBaselineError("gain reference time must be positive")
        if (
            isinstance(self.rk4_substeps, bool)
            or not isinstance(self.rk4_substeps, int)
            or self.rk4_substeps < 1
        ):
            raise S2ReferenceBaselineError("RK4 substeps must be a positive integer")

    @property
    def local_rate(self) -> float:
        return self.coupling_rate_per_second / self.capacity_ratio

    @property
    def gain(self) -> float:
        return self.local_rate * self.gain_reference_seconds


@dataclass(frozen=True, slots=True)
class S2ReferenceState:
    activation: tuple[float, ...]
    afterimage: tuple[float, ...]
    development: tuple[float, ...]

    def __post_init__(self) -> None:
        vectors = tuple(tuple(float(value) for value in item) for item in (
            self.activation,
            self.afterimage,
            self.development,
        ))
        if not vectors[0] or any(len(item) != len(vectors[0]) for item in vectors):
            raise S2ReferenceBaselineError("S/H/L must share one nonempty shape")
        if any(not math.isfinite(value) for item in vectors for value in item):
            raise S2ReferenceBaselineError("S/H/L values must be finite")
        if any(abs(value) > 1.0 + _BOUND_TOLERANCE for item in vectors for value in item):
            raise S2ReferenceBaselineError("S/H/L must remain within -1..1")
        object.__setattr__(self, "activation", vectors[0])
        object.__setattr__(self, "afterimage", vectors[1])
        object.__setattr__(self, "development", vectors[2])

    def arrays(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return tuple(np.asarray(item, dtype=np.float64) for item in (
            self.activation,
            self.afterimage,
            self.development,
        ))


@dataclass(frozen=True, slots=True)
class S2ReferenceAdvance:
    model_id: str
    state: S2ReferenceState
    partition_error: float

    def __post_init__(self) -> None:
        if self.model_id not in _MODEL_IDS:
            raise S2ReferenceBaselineError("unknown S2 model id")
        error = float(self.partition_error)
        if not math.isfinite(error) or error < 0.0:
            raise S2ReferenceBaselineError("partition error must be finite and nonnegative")
        object.__setattr__(self, "partition_error", error)


def _matrix_exponential(matrix: np.ndarray) -> np.ndarray:
    """Scaling-and-squaring Pade-13 exponential using only NumPy."""

    matrix = np.asarray(matrix, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise S2ReferenceBaselineError("matrix exponential requires a square matrix")
    size = matrix.shape[0]
    identity = np.eye(size, dtype=np.float64)
    norm = float(np.linalg.norm(matrix, 1))
    theta = 5.371920351148152
    scale = 0 if norm <= theta else max(0, math.ceil(math.log2(norm / theta)))
    scaled = matrix / (2**scale)
    a2 = scaled @ scaled
    a4 = a2 @ a2
    a6 = a4 @ a2
    b = (
        64764752532480000.0,
        32382376266240000.0,
        7771770303897600.0,
        1187353796428800.0,
        129060195264000.0,
        10559470521600.0,
        670442572800.0,
        33522128640.0,
        1323241920.0,
        40840800.0,
        960960.0,
        16380.0,
        182.0,
        1.0,
    )
    u = scaled @ (
        a6 @ (b[13] * a6 + b[11] * a4 + b[9] * a2)
        + b[7] * a6
        + b[5] * a4
        + b[3] * a2
        + b[1] * identity
    )
    v = (
        a6 @ (b[12] * a6 + b[10] * a4 + b[8] * a2)
        + b[6] * a6
        + b[4] * a4
        + b[2] * a2
        + b[0] * identity
    )
    try:
        result = np.linalg.solve(v - u, v + u)
    except np.linalg.LinAlgError as exc:
        raise S2ReferenceBaselineError("matrix exponential solve failed") from exc
    for _ in range(scale):
        result = result @ result
    if not np.all(np.isfinite(result)):
        raise S2ReferenceBaselineError("matrix exponential is non-finite")
    return result


def _validate_inputs(
    state: S2ReferenceState,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
) -> tuple[np.ndarray, np.ndarray, float]:
    if not isinstance(state, S2ReferenceState):
        raise S2ReferenceBaselineError("S2 advance requires one reference state")
    generator = np.asarray(generator, dtype=np.float64)
    boundary = np.asarray(boundary, dtype=np.float64)
    size = len(state.activation)
    if generator.shape != (size, size) or boundary.shape != (size,):
        raise S2ReferenceBaselineError("generator and boundary must match S/H/L")
    if not np.all(np.isfinite(generator)) or not np.all(np.isfinite(boundary)):
        raise S2ReferenceBaselineError("generator and boundary must be finite")
    if not np.allclose(generator, generator.T, rtol=0.0, atol=1e-14):
        raise S2ReferenceBaselineError("S2 requires one symmetric fast generator")
    elapsed = float(elapsed_seconds)
    if not math.isfinite(elapsed) or elapsed <= 0.0:
        raise S2ReferenceBaselineError("elapsed time must be finite and positive")
    return generator, boundary, elapsed


def _linear_system(
    model_id: str,
    state: S2ReferenceState,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed: float,
    config: S2ReferenceModelConfig,
) -> S2ReferenceState:
    s, h, local = state.arrays()
    count = len(s)
    identity = np.eye(count, dtype=np.float64)
    zero = np.zeros((count, count), dtype=np.float64)
    fast = generator - config.leak_rate_per_second * identity
    tracking = 1.0 / config.afterimage_time_seconds
    h_decay = tracking + config.leak_rate_per_second
    coupling = config.coupling_rate_per_second
    local_rate = config.local_rate
    if model_id == "b0":
        s_s, s_l, l_s, l_l = fast, zero, zero, zero
    elif model_id == "b1":
        s_s, s_l, l_s, l_l = fast, zero, local_rate * identity, -local_rate * identity
    elif model_id == "b2":
        s_s = fast - coupling * identity
        s_l = coupling * identity
        l_s = local_rate * identity
        l_l = -local_rate * identity
    elif model_id == "b5":
        s_s = fast - coupling * identity
        s_l = zero
        l_s = local_rate * identity
        l_l = -local_rate * identity
    else:
        raise S2ReferenceBaselineError("linear solver received a nonlinear model")
    matrix = np.block(
        [
            [s_s, zero, s_l, boundary[:, None]],
            [tracking * identity, -h_decay * identity, zero, np.zeros((count, 1))],
            [l_s, zero, l_l, np.zeros((count, 1))],
            [np.zeros((1, count)), np.zeros((1, count)), np.zeros((1, count)), np.ones((1, 1)) * 0.0],
        ]
    )
    combined = np.concatenate((s, h, local, np.ones(1, dtype=np.float64)))
    next_values = _matrix_exponential(matrix * elapsed) @ combined
    next_local = local if model_id == "b0" else next_values[2*count:3*count]
    return _bounded_state(
        next_values[:count],
        next_values[count:2*count],
        next_local,
    )


def _bounded_state(s: np.ndarray, h: np.ndarray, local: np.ndarray) -> S2ReferenceState:
    vectors = (np.asarray(s), np.asarray(h), np.asarray(local))
    if any(not np.all(np.isfinite(item)) for item in vectors):
        raise S2ReferenceBaselineError("S2 integration produced a non-finite state")
    if any(np.any(np.abs(item) > 1.0 + _BOUND_TOLERANCE) for item in vectors):
        raise S2ReferenceBaselineError("S2 integration left the normalized domain")
    return S2ReferenceState(
        tuple(float(value) for value in np.clip(vectors[0], -1.0, 1.0)),
        tuple(float(value) for value in np.clip(vectors[1], -1.0, 1.0)),
        tuple(float(value) for value in np.clip(vectors[2], -1.0, 1.0)),
    )


def _activation_integral(
    state: np.ndarray,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed: float,
    leak: float,
) -> np.ndarray:
    count = len(state)
    fast = generator - leak * np.eye(count, dtype=np.float64)
    augmented = np.block(
        [
            [fast, np.zeros((count, count)), boundary[:, None]],
            [np.eye(count), np.zeros((count, count)), np.zeros((count, 1))],
            [np.zeros((1, count)), np.zeros((1, count)), np.zeros((1, 1))],
        ]
    )
    initial = np.concatenate((state, np.zeros(count), np.ones(1)))
    result = _matrix_exponential(augmented * elapsed) @ initial
    return result[count:2*count]


def _b3_system(
    state: S2ReferenceState,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed: float,
    config: S2ReferenceModelConfig,
) -> S2ReferenceState:
    fast = _linear_system("b0", state, generator, boundary, elapsed, config)
    s0, _, local0 = state.arrays()
    integral = _activation_integral(
        s0,
        generator,
        boundary,
        elapsed,
        config.leak_rate_per_second,
    )
    local = np.empty_like(local0)
    for index, value in enumerate(local0):
        if abs(value) >= 1.0:
            local[index] = value
        else:
            local[index] = math.tanh(
                math.atanh(float(value)) + config.local_rate * integral[index]
            )
    return _bounded_state(
        np.asarray(fast.activation),
        np.asarray(fast.afterimage),
        local,
    )


def _b4_rhs(
    values: np.ndarray,
    generator: np.ndarray,
    boundary: np.ndarray,
    config: S2ReferenceModelConfig,
) -> np.ndarray:
    count = len(boundary)
    s = values[:count]
    h = values[count:2*count]
    local = values[2*count:]
    fast = generator @ s + boundary - config.leak_rate_per_second * s
    tracking = 1.0 / config.afterimage_time_seconds
    return np.concatenate(
        (
            (1.0 + config.gain * local) * fast,
            tracking * s - (tracking + config.leak_rate_per_second) * h,
            config.local_rate * (s - local),
        )
    )


def _rk4(
    initial: np.ndarray,
    elapsed: float,
    steps: int,
    generator: np.ndarray,
    boundary: np.ndarray,
    config: S2ReferenceModelConfig,
) -> np.ndarray:
    values = np.array(initial, copy=True)
    width = elapsed / steps
    for _ in range(steps):
        k1 = _b4_rhs(values, generator, boundary, config)
        k2 = _b4_rhs(values + 0.5 * width * k1, generator, boundary, config)
        k3 = _b4_rhs(values + 0.5 * width * k2, generator, boundary, config)
        k4 = _b4_rhs(values + width * k3, generator, boundary, config)
        values += (width / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return values


def apply_s2_reference_point_contacts(
    state: S2ReferenceState,
    contacts: tuple[tuple[int, float, float], ...],
    response_time_seconds: float,
    leak_rate_per_second: float = 0.0,
) -> S2ReferenceState:
    """Apply one simultaneous transient receptor completion to S only."""

    if not isinstance(state, S2ReferenceState):
        raise S2ReferenceBaselineError("point contacts require one S2 state")
    response_time = float(response_time_seconds)
    leak_rate = float(leak_rate_per_second)
    if not math.isfinite(response_time) or response_time <= 0.0:
        raise S2ReferenceBaselineError("response time must be finite and positive")
    if not math.isfinite(leak_rate) or leak_rate < 0.0:
        raise S2ReferenceBaselineError("leak rate must be finite and nonnegative")
    activation, afterimage, local = state.arrays()
    before = np.array(activation, copy=True)
    next_values: dict[int, float] = {}
    for index, read_duration, value in contacts:
        if isinstance(index, bool) or not isinstance(index, int):
            raise S2ReferenceBaselineError("contact index must be an integer")
        if index < 0 or index >= len(activation):
            raise S2ReferenceBaselineError("contact index lies outside S")
        duration = float(read_duration)
        contact_value = float(value)
        if not math.isfinite(duration) or duration <= 0.0:
            raise S2ReferenceBaselineError("contact duration must be positive")
        if not math.isfinite(contact_value) or abs(contact_value) > 1.0:
            raise S2ReferenceBaselineError("contact value must stay within -1..1")
        response_rate = 1.0 / response_time
        total_rate = response_rate + leak_rate
        retention = math.exp(-total_rate * duration)
        equilibrium = response_rate * contact_value / total_rate
        next_values[index] = (
            retention * before[index] + (1.0 - retention) * equilibrium
        )
    for index, value in next_values.items():
        activation[index] = value
    return _bounded_state(activation, afterimage, local)


def advance_s2_reference_model(
    model_id: str,
    state: S2ReferenceState,
    generator: np.ndarray,
    boundary: np.ndarray,
    elapsed_seconds: float,
    config: S2ReferenceModelConfig = S2ReferenceModelConfig(),
) -> S2ReferenceAdvance:
    """Advance one fixed-generator interval without world or runner effects."""

    if model_id not in _MODEL_IDS:
        raise S2ReferenceBaselineError("unknown S2 model id")
    if not isinstance(config, S2ReferenceModelConfig):
        raise S2ReferenceBaselineError("invalid S2 model config")
    generator, boundary, elapsed = _validate_inputs(
        state, generator, boundary, elapsed_seconds
    )
    if model_id in ("b0", "b1", "b2", "b5"):
        result = _linear_system(model_id, state, generator, boundary, elapsed, config)
        return S2ReferenceAdvance(model_id, result, 0.0)
    if model_id == "b3":
        result = _b3_system(state, generator, boundary, elapsed, config)
        return S2ReferenceAdvance(model_id, result, 0.0)
    initial = np.concatenate(state.arrays())
    primary = _rk4(
        initial,
        elapsed,
        config.rk4_substeps,
        generator,
        boundary,
        config,
    )
    control = _rk4(
        initial,
        elapsed,
        2 * config.rk4_substeps,
        generator,
        boundary,
        config,
    )
    count = len(state.activation)
    result = _bounded_state(
        primary[:count], primary[count:2*count], primary[2*count:]
    )
    error = float(np.max(np.abs(primary - control)))
    return S2ReferenceAdvance(model_id, result, error)
