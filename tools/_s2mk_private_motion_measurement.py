"""Private S2-MK visual motion measurement and independent baselines."""

from __future__ import annotations

from dataclasses import dataclass, fields
import hashlib
import json
import math
from pathlib import Path
import platform
import re
from typing import Iterable

import cv2
import numpy as np

from mcm_field_organism.finite_video_path import (
    LocalChannelGridReceptor,
    VisualGridConfig,
)
from tools._s2lv_private_pose_form_projection import PoseV1, project_pose_form


SCHEMA = "s2mk.private-motion-measurement.v1"
WIDTH = 1920
HEIGHT = 1080
CHANNELS = 3
GRID_ROWS = 8
GRID_COLUMNS = 12
CELL_HEIGHT = HEIGHT // GRID_ROWS
CELL_WIDTH = WIDTH // GRID_COLUMNS
PIXEL_COUNT = WIDTH * HEIGHT
MAX_PEAK_OWNED_ARRAY_BYTES = 134_217_728
MAX_RESULT_BYTES = 98_304

QUALIFIED_PYTHON_VERSION = "3.14.4"
QUALIFIED_OPENCV_VERSION = "4.13.0"
QUALIFIED_NUMPY_VERSION = "2.5.1"
QUALIFIED_CV2_BINARY_SHA256 = "78db0c836b952d9d5510140677463687c357a7166fddfa6ac7e31abb2d7d9bbd"
QUALIFIED_BUILD_INFORMATION_SHA256 = "8a55f551e40cf84d0fa7e2509bb9544da66782a8cbc017d7ce27a9de0ef9c1ac"
QUALIFIED_PREFLIGHT_CAPABILITY_DIGEST = "1bfd6c568e2e55903f15a7234a038160f666d90dc954a4be77f97fc9fdb61eb1"

FLOW_PARAMETERS = {
    "pyr_scale": 0.5,
    "levels": 5,
    "winsize": 21,
    "iterations": 5,
    "poly_n": 7,
    "poly_sigma": 1.5,
    "flags": 0,
}
RGB_TO_Y_RULE = "UINT32_77R_150G_29B_PLUS_128_SHIFT_8_V1"
FLOW_CANONICALIZATION = "C_CONTIGUOUS_LITTLE_ENDIAN_FLOAT32_ROW_MAJOR_V1"
PERCENTILE_RULE = "NUMPY_LINEAR_V1"
SUMMATION_RULE = "NUMPY_C_ORDER_FLOAT64_SUM_V1"

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")


class S2MKMeasurementError(ValueError):
    """The visual pair cannot produce a valid S2-MK measurement."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MKMeasurementError(message)


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _validate_digest(value: object, role: str) -> str:
    _require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None, f"{role} differs")
    return value


@dataclass(frozen=True, slots=True)
class DenseFlowAlgorithmBindingV1:
    python_version: str
    opencv_version: str
    numpy_version: str
    cv2_binary_sha256: str
    build_information_sha256: str
    preflight_capability_digest: str
    thread_count: int
    opencl_enabled: bool
    parameters_digest: str

    def __post_init__(self) -> None:
        _require(self.python_version == QUALIFIED_PYTHON_VERSION, "Python version differs")
        _require(self.opencv_version == QUALIFIED_OPENCV_VERSION, "OpenCV version differs")
        _require(self.numpy_version == QUALIFIED_NUMPY_VERSION, "NumPy version differs")
        _require(self.cv2_binary_sha256 == QUALIFIED_CV2_BINARY_SHA256, "cv2 binary differs")
        _require(self.build_information_sha256 == QUALIFIED_BUILD_INFORMATION_SHA256, "OpenCV build differs")
        _require(self.preflight_capability_digest == QUALIFIED_PREFLIGHT_CAPABILITY_DIGEST, "preflight binding differs")
        _require(self.thread_count == 1 and self.opencl_enabled is False, "runtime parallelism differs")
        _require(self.parameters_digest == _digest(_algorithm_rules()), "flow parameters differ")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2mk.dense-flow-algorithm-binding.v1",
            "python_version": self.python_version,
            "opencv_version": self.opencv_version,
            "numpy_version": self.numpy_version,
            "cv2_binary_sha256": self.cv2_binary_sha256,
            "build_information_sha256": self.build_information_sha256,
            "preflight_capability_digest": self.preflight_capability_digest,
            "thread_count": self.thread_count,
            "opencl_enabled": self.opencl_enabled,
            "parameters_digest": self.parameters_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class VisualMotionPairV1:
    pair_id: str
    frame_0_payload_digest: str
    frame_1_payload_digest: str
    visual_source_clock_id: str
    frame_0_window_start_tick: int
    frame_0_window_end_tick: int
    frame_1_window_start_tick: int
    frame_1_window_end_tick: int
    algorithm_binding_digest: str

    def __post_init__(self) -> None:
        _require(type(self.pair_id) is str and _IDENTIFIER.fullmatch(self.pair_id) is not None, "pair id differs")
        _validate_digest(self.frame_0_payload_digest, "frame 0 payload digest")
        _validate_digest(self.frame_1_payload_digest, "frame 1 payload digest")
        _validate_digest(self.algorithm_binding_digest, "algorithm binding digest")
        _require(
            type(self.visual_source_clock_id) is str
            and _IDENTIFIER.fullmatch(self.visual_source_clock_id) is not None,
            "visual source clock differs",
        )
        ticks = (
            self.frame_0_window_start_tick,
            self.frame_0_window_end_tick,
            self.frame_1_window_start_tick,
            self.frame_1_window_end_tick,
        )
        _require(all(type(value) is int and value >= 0 for value in ticks), "visual time differs")
        _require(self.frame_0_window_start_tick < self.frame_0_window_end_tick, "frame 0 window differs")
        _require(self.frame_1_window_start_tick < self.frame_1_window_end_tick, "frame 1 window differs")
        _require(self.frame_0_window_end_tick <= self.frame_1_window_start_tick, "visual windows overlap or regress")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2mk.visual-motion-pair.v1",
            "pair_id": self.pair_id,
            "frame_0_payload_digest": self.frame_0_payload_digest,
            "frame_1_payload_digest": self.frame_1_payload_digest,
            "visual_source_clock_id": self.visual_source_clock_id,
            "frame_0_window_start_tick": self.frame_0_window_start_tick,
            "frame_0_window_end_tick": self.frame_0_window_end_tick,
            "frame_1_window_start_tick": self.frame_1_window_start_tick,
            "frame_1_window_end_tick": self.frame_1_window_end_tick,
            "width": WIDTH,
            "height": HEIGHT,
            "channels": CHANNELS,
            "pixel_format": "RGB8",
            "algorithm_binding_digest": self.algorithm_binding_digest,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class DistributionSummaryV1:
    count: int
    mean: float
    median: float
    p95: float

    def __post_init__(self) -> None:
        _require(type(self.count) is int and self.count > 0, "summary count differs")
        values = (self.mean, self.median, self.p95)
        _require(all(type(value) is float and math.isfinite(value) and value >= 0.0 for value in values), "summary value differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "count": self.count,
            "mean": self.mean,
            "median": self.median,
            "p95": self.p95,
            "percentile_rule": PERCENTILE_RULE,
            "summation_rule": SUMMATION_RULE,
        }


@dataclass(frozen=True, slots=True)
class MotionCellSummaryV1:
    row: int
    column: int
    pixel_count: int
    valid_correspondence_count: int
    mean_dx: float
    mean_dy: float
    magnitude: DistributionSummaryV1
    cycle_residual: DistributionSummaryV1
    warped_rgb_residual: DistributionSummaryV1

    def __post_init__(self) -> None:
        _require(type(self.row) is int and 0 <= self.row < GRID_ROWS, "cell row differs")
        _require(type(self.column) is int and 0 <= self.column < GRID_COLUMNS, "cell column differs")
        _require(self.pixel_count == CELL_HEIGHT * CELL_WIDTH, "cell pixel count differs")
        _require(0 < self.valid_correspondence_count <= self.pixel_count, "cell valid count differs")
        _require(type(self.mean_dx) is float and math.isfinite(self.mean_dx), "cell dx differs")
        _require(type(self.mean_dy) is float and math.isfinite(self.mean_dy), "cell dy differs")
        _require(self.magnitude.count == self.pixel_count, "cell magnitude count differs")
        _require(self.cycle_residual.count == self.valid_correspondence_count, "cell cycle count differs")
        _require(self.warped_rgb_residual.count == self.valid_correspondence_count, "cell RGB count differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2mk.motion-cell-summary.v1",
            "row": self.row,
            "column": self.column,
            "pixel_count": self.pixel_count,
            "valid_correspondence_count": self.valid_correspondence_count,
            "mean_dx": self.mean_dx,
            "mean_dy": self.mean_dy,
            "magnitude": self.magnitude.canonical_payload(),
            "cycle_residual": self.cycle_residual.canonical_payload(),
            "warped_rgb_residual": self.warped_rgb_residual.canonical_payload(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class MeasuredVisualMotionV1:
    pair_digest: str
    algorithm_binding_digest: str
    frame_0_pre_digest: str
    frame_0_post_digest: str
    frame_1_pre_digest: str
    frame_1_post_digest: str
    forward_flow_digest: str
    reverse_flow_digest: str
    pixel_count: int
    valid_correspondence_count: int
    valid_correspondence_fraction: float
    magnitude: DistributionSummaryV1
    cycle_residual: DistributionSummaryV1
    warped_rgb_residual: DistributionSummaryV1
    cells: tuple[MotionCellSummaryV1, ...]
    cell_set_digest: str
    peak_owned_array_bytes: int

    def __post_init__(self) -> None:
        for role in (
            "pair_digest",
            "algorithm_binding_digest",
            "frame_0_pre_digest",
            "frame_0_post_digest",
            "frame_1_pre_digest",
            "frame_1_post_digest",
            "forward_flow_digest",
            "reverse_flow_digest",
            "cell_set_digest",
        ):
            _validate_digest(getattr(self, role), role)
        _require(self.frame_0_pre_digest == self.frame_0_post_digest, "frame 0 changed")
        _require(self.frame_1_pre_digest == self.frame_1_post_digest, "frame 1 changed")
        _require(self.pixel_count == PIXEL_COUNT, "global pixel count differs")
        _require(0 < self.valid_correspondence_count <= self.pixel_count, "global valid count differs")
        _require(
            type(self.valid_correspondence_fraction) is float
            and self.valid_correspondence_fraction == self.valid_correspondence_count / self.pixel_count,
            "valid fraction differs",
        )
        _require(type(self.cells) is tuple and len(self.cells) == GRID_ROWS * GRID_COLUMNS, "cell inventory differs")
        _require(sum(cell.pixel_count for cell in self.cells) == self.pixel_count, "cell coverage differs")
        _require(
            tuple((cell.row, cell.column) for cell in self.cells)
            == tuple((row, column) for row in range(GRID_ROWS) for column in range(GRID_COLUMNS)),
            "cell order differs",
        )
        _require(self.cell_set_digest == _digest([cell.digest() for cell in self.cells]), "cell set digest differs")
        _require(
            type(self.peak_owned_array_bytes) is int
            and 0 < self.peak_owned_array_bytes < MAX_PEAK_OWNED_ARRAY_BYTES,
            "owned array peak exceeds bound",
        )

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "pair_digest": self.pair_digest,
            "algorithm_binding_digest": self.algorithm_binding_digest,
            "frame_0_pre_digest": self.frame_0_pre_digest,
            "frame_0_post_digest": self.frame_0_post_digest,
            "frame_1_pre_digest": self.frame_1_pre_digest,
            "frame_1_post_digest": self.frame_1_post_digest,
            "forward_flow_digest": self.forward_flow_digest,
            "reverse_flow_digest": self.reverse_flow_digest,
            "pixel_count": self.pixel_count,
            "valid_correspondence_count": self.valid_correspondence_count,
            "valid_correspondence_fraction": self.valid_correspondence_fraction,
            "magnitude": self.magnitude.canonical_payload(),
            "cycle_residual": self.cycle_residual.canonical_payload(),
            "warped_rgb_residual": self.warped_rgb_residual.canonical_payload(),
            "cells": [cell.canonical_payload() for cell in self.cells],
            "cell_digests": [cell.digest() for cell in self.cells],
            "cell_set_digest": self.cell_set_digest,
            "peak_owned_array_bytes": self.peak_owned_array_bytes,
            "raw_frames_present": False,
            "flow_fields_present": False,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class VisualBaselineComparisonV1:
    pair_digest: str
    frame_0_receptor_digest: str
    frame_1_receptor_digest: str
    frame_0_pose_digest: str
    frame_1_pose_digest: str
    frame_0_form_digest: str
    frame_1_form_digest: str
    pixel_mean_l1: float
    receptor_mean_l1: float
    pose_absolute_differences: tuple[tuple[str, float], ...]
    form_mean_l1: float
    frame_0_pre_digest: str
    frame_0_post_digest: str
    frame_1_pre_digest: str
    frame_1_post_digest: str
    peak_owned_array_bytes: int

    def __post_init__(self) -> None:
        for role in (
            "pair_digest",
            "frame_0_receptor_digest",
            "frame_1_receptor_digest",
            "frame_0_pose_digest",
            "frame_1_pose_digest",
            "frame_0_form_digest",
            "frame_1_form_digest",
            "frame_0_pre_digest",
            "frame_0_post_digest",
            "frame_1_pre_digest",
            "frame_1_post_digest",
        ):
            _validate_digest(getattr(self, role), role)
        _require(self.frame_0_pre_digest == self.frame_0_post_digest, "baseline frame 0 changed")
        _require(self.frame_1_pre_digest == self.frame_1_post_digest, "baseline frame 1 changed")
        scalars = (self.pixel_mean_l1, self.receptor_mean_l1, self.form_mean_l1)
        _require(all(type(value) is float and math.isfinite(value) and value >= 0.0 for value in scalars), "baseline distance differs")
        expected_pose_roles = (
            "background_r",
            "background_g",
            "background_b",
        ) + tuple(
            field.name
            for field in fields(PoseV1)
            if field.name not in {"background_channels", "support_cell_count"}
        ) + ("support_cell_count",)
        _require(tuple(role for role, _ in self.pose_absolute_differences) == expected_pose_roles, "pose roles differ")
        _require(all(type(value) is float and math.isfinite(value) and value >= 0.0 for _, value in self.pose_absolute_differences), "pose difference differs")
        _require(type(self.peak_owned_array_bytes) is int and self.peak_owned_array_bytes > 0, "baseline peak differs")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2mk.visual-baseline-comparison.v1",
            "pair_digest": self.pair_digest,
            "frame_0_receptor_digest": self.frame_0_receptor_digest,
            "frame_1_receptor_digest": self.frame_1_receptor_digest,
            "frame_0_pose_digest": self.frame_0_pose_digest,
            "frame_1_pose_digest": self.frame_1_pose_digest,
            "frame_0_form_digest": self.frame_0_form_digest,
            "frame_1_form_digest": self.frame_1_form_digest,
            "pixel_mean_l1": self.pixel_mean_l1,
            "receptor_mean_l1": self.receptor_mean_l1,
            "pose_absolute_differences": [list(item) for item in self.pose_absolute_differences],
            "form_mean_l1": self.form_mean_l1,
            "frame_0_pre_digest": self.frame_0_pre_digest,
            "frame_0_post_digest": self.frame_0_post_digest,
            "frame_1_pre_digest": self.frame_1_pre_digest,
            "frame_1_post_digest": self.frame_1_post_digest,
            "peak_owned_array_bytes": self.peak_owned_array_bytes,
            "raw_frames_present": False,
            "flow_fields_present": False,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class S2MKPairResultV1:
    pair_digest: str
    measurement: MeasuredVisualMotionV1
    baselines: VisualBaselineComparisonV1

    def __post_init__(self) -> None:
        _validate_digest(self.pair_digest, "result pair digest")
        _require(self.measurement.pair_digest == self.pair_digest, "measurement pair differs")
        _require(self.baselines.pair_digest == self.pair_digest, "baseline pair differs")
        _require(len(_canonical_bytes(self.canonical_payload())) <= MAX_RESULT_BYTES, "result exceeds byte limit")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2mk.pair-result.v1",
            "pair_digest": self.pair_digest,
            "measurement": self.measurement.canonical_payload(),
            "baselines": self.baselines.canonical_payload(),
            "measurement_digest": self.measurement.digest(),
            "baselines_digest": self.baselines.digest(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


class _ArrayPeakLedger:
    def __init__(self) -> None:
        self.peak_bytes = 0

    def observe(self, arrays: Iterable[object]) -> None:
        seen: set[int] = set()
        total = 0
        for value in arrays:
            if isinstance(value, np.ndarray):
                root = value
                while isinstance(root.base, np.ndarray):
                    root = root.base
                identity = id(root)
                if identity not in seen:
                    seen.add(identity)
                    total += int(root.nbytes)
        self.peak_bytes = max(self.peak_bytes, total)


def _algorithm_rules() -> dict[str, object]:
    return {
        "algorithm": "OPENCV_CALC_OPTICAL_FLOW_FARNEBACK",
        "parameters": FLOW_PARAMETERS,
        "rgb_to_y_rule": RGB_TO_Y_RULE,
        "flow_canonicalization": FLOW_CANONICALIZATION,
        "percentile_rule": PERCENTILE_RULE,
        "summation_rule": SUMMATION_RULE,
        "bilinear_rule": "FLOAT32_TOP_THEN_BOTTOM_THEN_VERTICAL_CLAMPED_EDGE_V1",
    }


def _loaded_cv2_binary() -> Path:
    package_file = Path(str(cv2.__file__)).resolve()
    candidates = tuple(sorted(package_file.parent.glob("cv2*.pyd")))
    _require(len(candidates) == 1 and candidates[0].is_file(), "cv2 binary path differs")
    return candidates[0]


def qualified_algorithm_binding() -> DenseFlowAlgorithmBindingV1:
    cv2.setNumThreads(1)
    cv2.ocl.setUseOpenCL(False)
    binary = _loaded_cv2_binary()
    binary_digest = _digest_bytes(binary.read_bytes())
    build_digest = _digest_bytes(str(cv2.getBuildInformation()).encode("utf-8"))
    _require(platform.python_version() == QUALIFIED_PYTHON_VERSION, "Python runtime is not qualified")
    _require(str(cv2.__version__) == QUALIFIED_OPENCV_VERSION, "OpenCV runtime is not qualified")
    _require(str(np.__version__) == QUALIFIED_NUMPY_VERSION, "NumPy runtime is not qualified")
    _require(binary_digest == QUALIFIED_CV2_BINARY_SHA256, "cv2 binary is not qualified")
    _require(build_digest == QUALIFIED_BUILD_INFORMATION_SHA256, "OpenCV build is not qualified")
    _require(int(cv2.getNumThreads()) == 1, "OpenCV thread count differs")
    _require(bool(cv2.ocl.useOpenCL()) is False, "OpenCL differs")
    return DenseFlowAlgorithmBindingV1(
        python_version=platform.python_version(),
        opencv_version=str(cv2.__version__),
        numpy_version=str(np.__version__),
        cv2_binary_sha256=binary_digest,
        build_information_sha256=build_digest,
        preflight_capability_digest=QUALIFIED_PREFLIGHT_CAPABILITY_DIGEST,
        thread_count=int(cv2.getNumThreads()),
        opencl_enabled=bool(cv2.ocl.useOpenCL()),
        parameters_digest=_digest(_algorithm_rules()),
    )


def _frame_digest(frame: np.ndarray) -> str:
    return _digest_bytes(frame.tobytes(order="C"))


def _validate_frame(frame: object, expected_digest: str, role: str) -> np.ndarray:
    _require(isinstance(frame, np.ndarray), f"{role} is not an ndarray")
    _require(frame.dtype == np.uint8, f"{role} dtype differs")
    _require(frame.shape == (HEIGHT, WIDTH, CHANNELS), f"{role} geometry differs")
    _require(bool(frame.flags.c_contiguous), f"{role} layout differs")
    _require(_frame_digest(frame) == expected_digest, f"{role} payload digest differs")
    return frame


def _rgb_to_y(
    frame: np.ndarray,
    ledger: _ArrayPeakLedger | None = None,
    companions: tuple[np.ndarray, ...] = (),
) -> np.ndarray:
    _require(isinstance(frame, np.ndarray) and frame.dtype == np.uint8, "RGB input type differs")
    _require(frame.ndim == 3 and frame.shape[2] == 3, "RGB input geometry differs")
    result = np.empty(frame.shape[:2], dtype=np.uint8)
    for row_start in range(0, frame.shape[0], CELL_HEIGHT):
        row_end = min(row_start + CELL_HEIGHT, frame.shape[0])
        red = frame[row_start:row_end, :, 0].astype(np.uint32)
        green = frame[row_start:row_end, :, 1].astype(np.uint32)
        blue = frame[row_start:row_end, :, 2].astype(np.uint32)
        projected = 77 * red + 150 * green + 29 * blue + 128
        projected >>= 8
        result[row_start:row_end] = projected.astype(np.uint8)
        if ledger is not None:
            ledger.observe((*companions, frame, result, red, green, blue, projected))
    _require(result.shape == frame.shape[:2] and result.dtype == np.uint8, "Y projection differs")
    return result


def _calculate_flow(first_y: np.ndarray, second_y: np.ndarray) -> np.ndarray:
    flow = cv2.calcOpticalFlowFarneback(
        first_y,
        second_y,
        None,
        FLOW_PARAMETERS["pyr_scale"],
        FLOW_PARAMETERS["levels"],
        FLOW_PARAMETERS["winsize"],
        FLOW_PARAMETERS["iterations"],
        FLOW_PARAMETERS["poly_n"],
        FLOW_PARAMETERS["poly_sigma"],
        FLOW_PARAMETERS["flags"],
    )
    return flow


def _validate_flow(flow: object, *, height: int, width: int, role: str) -> np.ndarray:
    _require(isinstance(flow, np.ndarray), f"{role} is not an ndarray")
    _require(flow.shape == (height, width, 2), f"{role} geometry differs")
    _require(flow.dtype == np.float32, f"{role} dtype differs")
    _require(bool(flow.flags.c_contiguous), f"{role} layout differs")
    _require(bool(np.isfinite(flow).all()), f"{role} contains non-finite values")
    return flow


def _flow_bytes(flow: np.ndarray) -> bytes:
    _require(isinstance(flow, np.ndarray) and flow.ndim == 3, "flow canonical input differs")
    validated = _validate_flow(flow, height=flow.shape[0], width=flow.shape[1], role="flow")
    canonical = validated.astype("<f4", copy=False)
    _require(bool(canonical.flags.c_contiguous), "flow canonical layout differs")
    return canonical.tobytes(order="C")


def _bilinear_sample_points(source: np.ndarray, x: np.ndarray, y: np.ndarray) -> np.ndarray:
    _require(isinstance(source, np.ndarray) and source.ndim in {2, 3}, "bilinear source differs")
    _require(x.shape == y.shape and x.ndim == 1, "bilinear coordinates differ")
    height, width = source.shape[:2]
    _require(
        bool(np.isfinite(x).all())
        and bool(np.isfinite(y).all())
        and bool(((x >= 0.0) & (x <= width - 1) & (y >= 0.0) & (y <= height - 1)).all()),
        "bilinear coordinates leave source",
    )
    x0 = np.floor(x).astype(np.int32)
    y0 = np.floor(y).astype(np.int32)
    x1 = np.minimum(x0 + 1, width - 1)
    y1 = np.minimum(y0 + 1, height - 1)
    fx = (x - x0.astype(np.float32)).astype(np.float32)
    fy = (y - y0.astype(np.float32)).astype(np.float32)
    source32 = source.astype(np.float32, copy=False)
    if source.ndim == 3:
        fx = fx[:, None]
        fy = fy[:, None]
    top = source32[y0, x0] * (np.float32(1.0) - fx) + source32[y0, x1] * fx
    bottom = source32[y1, x0] * (np.float32(1.0) - fx) + source32[y1, x1] * fx
    return np.ascontiguousarray(top * (np.float32(1.0) - fy) + bottom * fy, dtype=np.float32)


def _summary(values: np.ndarray) -> DistributionSummaryV1:
    _require(isinstance(values, np.ndarray) and values.ndim == 1 and values.size > 0, "summary input differs")
    _require(bool(np.isfinite(values).all()) and bool((values >= 0.0).all()), "summary domain differs")
    ordered = np.ascontiguousarray(values, dtype=np.float64)
    return DistributionSummaryV1(
        count=int(ordered.size),
        mean=float(np.sum(ordered, dtype=np.float64) / ordered.size),
        median=float(np.percentile(ordered, 50.0, method="linear")),
        p95=float(np.percentile(ordered, 95.0, method="linear")),
    )


def _signed_mean(values: np.ndarray) -> float:
    _require(values.ndim == 1 and values.size > 0 and bool(np.isfinite(values).all()), "signed mean input differs")
    return float(np.sum(np.ascontiguousarray(values, dtype=np.float64), dtype=np.float64) / values.size)


def _residual_arrays(
    frame_0: np.ndarray,
    frame_1: np.ndarray,
    forward: np.ndarray,
    reverse: np.ndarray,
    ledger: _ArrayPeakLedger,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    magnitude = np.ascontiguousarray(np.hypot(forward[:, :, 0], forward[:, :, 1]), dtype=np.float32)
    valid = np.zeros((HEIGHT, WIDTH), dtype=bool)
    cycle = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    warped_rgb = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    x_axis = np.arange(WIDTH, dtype=np.float32)[None, :]
    ledger.observe((frame_0, frame_1, forward, reverse, magnitude, valid, cycle, warped_rgb, x_axis))
    for row_start in range(0, HEIGHT, CELL_HEIGHT):
        row_end = min(row_start + CELL_HEIGHT, HEIGHT)
        forward_chunk = forward[row_start:row_end]
        y_axis = np.arange(row_start, row_end, dtype=np.float32)[:, None]
        query_x = np.ascontiguousarray(x_axis + forward_chunk[:, :, 0], dtype=np.float32)
        query_y = np.ascontiguousarray(y_axis + forward_chunk[:, :, 1], dtype=np.float32)
        chunk_valid = (
            (query_x >= 0.0)
            & (query_x <= np.float32(WIDTH - 1))
            & (query_y >= 0.0)
            & (query_y <= np.float32(HEIGHT - 1))
        )
        _require(bool(chunk_valid.any()), "row chunk has no valid correspondence")
        valid[row_start:row_end] = chunk_valid
        valid_x = np.ascontiguousarray(query_x[chunk_valid], dtype=np.float32)
        valid_y = np.ascontiguousarray(query_y[chunk_valid], dtype=np.float32)
        reverse_sample = _bilinear_sample_points(reverse, valid_x, valid_y)
        cycle_vectors = np.ascontiguousarray(forward_chunk[chunk_valid] + reverse_sample, dtype=np.float32)
        cycle_values = np.ascontiguousarray(np.hypot(cycle_vectors[:, 0], cycle_vectors[:, 1]), dtype=np.float32)
        cycle[row_start:row_end][chunk_valid] = cycle_values
        rgb_sample = _bilinear_sample_points(frame_1, valid_x, valid_y)
        source_rgb = np.ascontiguousarray(frame_0[row_start:row_end][chunk_valid], dtype=np.float32)
        rgb_values = np.ascontiguousarray(
            np.mean(np.abs(source_rgb - rgb_sample), axis=1, dtype=np.float32) / np.float32(255.0),
            dtype=np.float32,
        )
        warped_rgb[row_start:row_end][chunk_valid] = rgb_values
        ledger.observe(
            (
                frame_0,
                frame_1,
                forward,
                reverse,
                magnitude,
                valid,
                cycle,
                warped_rgb,
                x_axis,
                y_axis,
                query_x,
                query_y,
                chunk_valid,
                valid_x,
                valid_y,
                reverse_sample,
                cycle_vectors,
                cycle_values,
                rgb_sample,
                source_rgb,
                rgb_values,
            )
        )
    return magnitude, valid, cycle, warped_rgb


def _cell_summaries(
    forward: np.ndarray,
    magnitude: np.ndarray,
    valid: np.ndarray,
    cycle: np.ndarray,
    warped_rgb: np.ndarray,
) -> tuple[MotionCellSummaryV1, ...]:
    summaries = []
    for row in range(GRID_ROWS):
        row_slice = slice(row * CELL_HEIGHT, (row + 1) * CELL_HEIGHT)
        for column in range(GRID_COLUMNS):
            column_slice = slice(column * CELL_WIDTH, (column + 1) * CELL_WIDTH)
            local_valid = valid[row_slice, column_slice]
            valid_count = int(local_valid.sum(dtype=np.int64))
            _require(valid_count > 0, "cell has no valid correspondence")
            local_forward = forward[row_slice, column_slice]
            local_magnitude = np.ascontiguousarray(magnitude[row_slice, column_slice].reshape(-1))
            local_cycle = np.ascontiguousarray(cycle[row_slice, column_slice][local_valid])
            local_rgb = np.ascontiguousarray(warped_rgb[row_slice, column_slice][local_valid])
            summaries.append(
                MotionCellSummaryV1(
                    row=row,
                    column=column,
                    pixel_count=CELL_HEIGHT * CELL_WIDTH,
                    valid_correspondence_count=valid_count,
                    mean_dx=_signed_mean(np.ascontiguousarray(local_forward[:, :, 0].reshape(-1))),
                    mean_dy=_signed_mean(np.ascontiguousarray(local_forward[:, :, 1].reshape(-1))),
                    magnitude=_summary(local_magnitude),
                    cycle_residual=_summary(local_cycle),
                    warped_rgb_residual=_summary(local_rgb),
                )
            )
    return tuple(summaries)


def measure_motion(
    frame_0: object,
    frame_1: object,
    pair: VisualMotionPairV1,
    algorithm: DenseFlowAlgorithmBindingV1,
) -> MeasuredVisualMotionV1:
    _require(type(pair) is VisualMotionPairV1, "pair binding differs")
    _require(type(algorithm) is DenseFlowAlgorithmBindingV1, "algorithm binding differs")
    _require(pair.algorithm_binding_digest == algorithm.digest(), "pair algorithm binding differs")
    first = _validate_frame(frame_0, pair.frame_0_payload_digest, "frame 0")
    second = _validate_frame(frame_1, pair.frame_1_payload_digest, "frame 1")
    first_pre = _frame_digest(first)
    second_pre = _frame_digest(second)
    ledger = _ArrayPeakLedger()
    ledger.observe((first, second))
    first_y = _rgb_to_y(first, ledger, (second,))
    second_y = _rgb_to_y(second, ledger, (first, first_y))
    ledger.observe((first, second, first_y, second_y))
    forward = _validate_flow(_calculate_flow(first_y, second_y), height=HEIGHT, width=WIDTH, role="forward flow")
    ledger.observe((first, second, first_y, second_y, forward))
    reverse = _validate_flow(_calculate_flow(second_y, first_y), height=HEIGHT, width=WIDTH, role="reverse flow")
    ledger.observe((first, second, first_y, second_y, forward, reverse))
    forward_digest = _digest_bytes(_flow_bytes(forward))
    reverse_digest = _digest_bytes(_flow_bytes(reverse))
    del first_y
    del second_y
    magnitude, valid, cycle, warped_rgb = _residual_arrays(first, second, forward, reverse, ledger)
    valid_values = valid.reshape(-1)
    valid_count = int(valid_values.sum(dtype=np.int64))
    _require(valid_count > 0, "no valid correspondence")
    cells = _cell_summaries(forward, magnitude, valid, cycle, warped_rgb)
    first_post = _frame_digest(first)
    second_post = _frame_digest(second)
    return MeasuredVisualMotionV1(
        pair_digest=pair.digest(),
        algorithm_binding_digest=algorithm.digest(),
        frame_0_pre_digest=first_pre,
        frame_0_post_digest=first_post,
        frame_1_pre_digest=second_pre,
        frame_1_post_digest=second_post,
        forward_flow_digest=forward_digest,
        reverse_flow_digest=reverse_digest,
        pixel_count=PIXEL_COUNT,
        valid_correspondence_count=valid_count,
        valid_correspondence_fraction=valid_count / PIXEL_COUNT,
        magnitude=_summary(np.ascontiguousarray(magnitude.reshape(-1))),
        cycle_residual=_summary(np.ascontiguousarray(cycle.reshape(-1)[valid_values])),
        warped_rgb_residual=_summary(np.ascontiguousarray(warped_rgb.reshape(-1)[valid_values])),
        cells=cells,
        cell_set_digest=_digest([cell.digest() for cell in cells]),
        peak_owned_array_bytes=ledger.peak_bytes,
    )


def _chunked_pixel_mean_l1(first: np.ndarray, second: np.ndarray, ledger: _ArrayPeakLedger) -> float:
    total = 0.0
    count = 0
    for row_start in range(0, HEIGHT, CELL_HEIGHT):
        row_end = min(row_start + CELL_HEIGHT, HEIGHT)
        left = first[row_start:row_end].astype(np.int16)
        right = second[row_start:row_end].astype(np.int16)
        difference = np.ascontiguousarray(np.abs(left - right), dtype=np.int16)
        ledger.observe((first, second, left, right, difference))
        total += float(np.sum(difference, dtype=np.float64))
        count += int(difference.size)
    _require(count == PIXEL_COUNT * CHANNELS, "pixel comparison count differs")
    return float(total / count / 255.0)


def compute_independent_baselines(
    frame_0: object,
    frame_1: object,
    pair: VisualMotionPairV1,
) -> VisualBaselineComparisonV1:
    _require(type(pair) is VisualMotionPairV1, "baseline pair differs")
    first = _validate_frame(frame_0, pair.frame_0_payload_digest, "baseline frame 0")
    second = _validate_frame(frame_1, pair.frame_1_payload_digest, "baseline frame 1")
    first_pre = _frame_digest(first)
    second_pre = _frame_digest(second)
    ledger = _ArrayPeakLedger()
    ledger.observe((first, second))
    pixel_l1 = _chunked_pixel_mean_l1(first, second, ledger)
    receptor = LocalChannelGridReceptor(VisualGridConfig())
    state_0 = receptor.analyze(first, frame_index=0)
    state_1 = receptor.analyze(second, frame_index=1)
    values_0 = tuple(state_0.channel_values)
    values_1 = tuple(state_1.channel_values)
    _require(len(values_0) == len(values_1) == 288, "receptor dimension differs")
    receptor_l1 = float(math.fsum(abs(left - right) for left, right in zip(values_0, values_1, strict=True)) / 288)
    projection_0 = project_pose_form(values_0)
    projection_1 = project_pose_form(values_1)
    background_differences = tuple(
        (
            role,
            float(abs(projection_0.pose.background_channels[index] - projection_1.pose.background_channels[index])),
        )
        for index, role in enumerate(("background_r", "background_g", "background_b"))
    )
    pose_roles = tuple(
        field.name
        for field in fields(PoseV1)
        if field.name not in {"background_channels", "support_cell_count"}
    )
    pose_differences = background_differences + tuple(
        (role, float(abs(getattr(projection_0.pose, role) - getattr(projection_1.pose, role))))
        for role in pose_roles
    ) + (("support_cell_count", float(abs(projection_0.pose.support_cell_count - projection_1.pose.support_cell_count))),)
    form_l1 = float(
        math.fsum(
            abs(left - right)
            for left, right in zip(
                projection_0.form_descriptor.values,
                projection_1.form_descriptor.values,
                strict=True,
            )
        )
        / len(projection_0.form_descriptor.values)
    )
    first_post = _frame_digest(first)
    second_post = _frame_digest(second)
    return VisualBaselineComparisonV1(
        pair_digest=pair.digest(),
        frame_0_receptor_digest=state_0.digest(),
        frame_1_receptor_digest=state_1.digest(),
        frame_0_pose_digest=projection_0.pose.digest(),
        frame_1_pose_digest=projection_1.pose.digest(),
        frame_0_form_digest=projection_0.form_descriptor.digest(),
        frame_1_form_digest=projection_1.form_descriptor.digest(),
        pixel_mean_l1=pixel_l1,
        receptor_mean_l1=receptor_l1,
        pose_absolute_differences=pose_differences,
        form_mean_l1=form_l1,
        frame_0_pre_digest=first_pre,
        frame_0_post_digest=first_post,
        frame_1_pre_digest=second_pre,
        frame_1_post_digest=second_post,
        peak_owned_array_bytes=ledger.peak_bytes,
    )


def measure_and_compare(
    frame_0: object,
    frame_1: object,
    pair: VisualMotionPairV1,
    algorithm: DenseFlowAlgorithmBindingV1,
) -> S2MKPairResultV1:
    measurement = measure_motion(frame_0, frame_1, pair, algorithm)
    baselines = compute_independent_baselines(frame_0, frame_1, pair)
    return S2MKPairResultV1(pair_digest=pair.digest(), measurement=measurement, baselines=baselines)


__all__ = (
    "DenseFlowAlgorithmBindingV1",
    "MeasuredVisualMotionV1",
    "MotionCellSummaryV1",
    "S2MKMeasurementError",
    "S2MKPairResultV1",
    "VisualBaselineComparisonV1",
    "VisualMotionPairV1",
    "compute_independent_baselines",
    "measure_and_compare",
    "measure_motion",
    "qualified_algorithm_binding",
)
