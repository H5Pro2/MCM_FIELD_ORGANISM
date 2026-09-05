"""Private image-driven sparse correspondence measurement for S2-MP."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import platform
import re
from typing import Any

import cv2
import numpy as np

from tools._s2mm_private_sparse_lk_preflight import (
    EPSILON,
    FLAGS,
    HEIGHT,
    MAX_ITERATIONS,
    MAX_LEVEL,
    MIN_EIG_THRESHOLD,
    QUALIFIED_BUILD_INFORMATION_SHA256,
    QUALIFIED_CV2_BINARY_SHA256,
    QUALIFIED_NUMPY_VERSION,
    QUALIFIED_OPENCV_VERSION,
    QUALIFIED_PYTHON_VERSION,
    WIDTH,
    WINDOW_SIZE,
    _bilinear_rgb,
    _loaded_binary_path,
    _rgb_to_y,
)


GRID_COLUMNS = 12
GRID_ROWS = 8
CELL_WIDTH = WIDTH // GRID_COLUMNS
CELL_HEIGHT = HEIGHT // GRID_ROWS
MAX_CORNERS_PER_CELL = 16
MAX_POINT_COUNT = GRID_COLUMNS * GRID_ROWS * MAX_CORNERS_PER_CELL
QUALITY_LEVEL = 0.01
MIN_DISTANCE = 8.0
BLOCK_SIZE = 7
USE_HARRIS_DETECTOR = False
HARRIS_K = 0.04
MIN_VALID_TRACKS = 32
MIN_VALID_CELLS = 4
MAX_RESULT_BYTES = 32_768
MAX_PEAK_BYTES = 134_217_728

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{7,95}$")


class S2MPMeasurementError(ValueError):
    """The source or sparse measurement violates the bound form."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MPMeasurementError(message)


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


def _array_digest(value: np.ndarray, dtype: str) -> str:
    canonical = np.ascontiguousarray(value, dtype=dtype)
    return hashlib.sha256(memoryview(canonical).cast("B")).hexdigest()


def _validate_digest(value: object, role: str) -> str:
    _require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None, f"{role} differs")
    return value


def _frame_digest(frame: np.ndarray) -> str:
    _require(frame.flags.c_contiguous, "frame layout differs")
    return hashlib.sha256(memoryview(frame).cast("B")).hexdigest()


def _summary(values: np.ndarray) -> dict[str, object]:
    _require(values.ndim == 1 and values.size > 0, "summary input differs")
    _require(bool(np.isfinite(values).all()) and bool((values >= 0.0).all()), "summary values differ")
    ordered = np.ascontiguousarray(values, dtype=np.float64)
    return {
        "count": int(ordered.size),
        "mean": float(np.sum(ordered, dtype=np.float64) / ordered.size),
        "median": float(np.percentile(ordered, 50.0, method="linear")),
        "p95": float(np.percentile(ordered, 95.0, method="linear")),
        "maximum": float(np.max(ordered)),
    }


def _algorithm_rules() -> dict[str, object]:
    return {
        "schema": "s2mp.feature-sparse-algorithm-binding.v1",
        "detector": "OPENCV_SHI_TOMASI_GOOD_FEATURES_TO_TRACK",
        "detector_scope": "ROW_MAJOR_12X8_NON_OVERLAPPING_CELLS",
        "max_corners_per_cell": MAX_CORNERS_PER_CELL,
        "max_point_count": MAX_POINT_COUNT,
        "quality_level": QUALITY_LEVEL,
        "minimum_distance": MIN_DISTANCE,
        "block_size": BLOCK_SIZE,
        "use_harris_detector": USE_HARRIS_DETECTOR,
        "harris_k": HARRIS_K,
        "candidate_order": "CELL_ROW_COLUMN_THEN_LOCAL_Y_X",
        "rgb_to_y_rule": "UINT32_77R_150G_29B_PLUS_128_SHIFT_8_V1",
        "lk_window_size": list(WINDOW_SIZE),
        "lk_max_level": MAX_LEVEL,
        "lk_max_iterations": MAX_ITERATIONS,
        "lk_epsilon": EPSILON,
        "lk_flags": FLAGS,
        "lk_min_eig_threshold": MIN_EIG_THRESHOLD,
        "minimum_valid_tracks": MIN_VALID_TRACKS,
        "minimum_valid_cells": MIN_VALID_CELLS,
        "invalid_track_values_interpreted": False,
    }


def algorithm_binding_digest() -> str:
    return _digest(_algorithm_rules())


def qualified_runtime_binding() -> dict[str, object]:
    cv2.setNumThreads(1)
    cv2.ocl.setUseOpenCL(False)
    binary = _loaded_binary_path(cv2)
    binary_digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    build_digest = hashlib.sha256(str(cv2.getBuildInformation()).encode("utf-8")).hexdigest()
    _require(platform.python_version() == QUALIFIED_PYTHON_VERSION, "Python runtime differs")
    _require(str(cv2.__version__) == QUALIFIED_OPENCV_VERSION, "OpenCV runtime differs")
    _require(str(np.__version__) == QUALIFIED_NUMPY_VERSION, "NumPy runtime differs")
    _require(binary_digest == QUALIFIED_CV2_BINARY_SHA256, "cv2 binary differs")
    _require(build_digest == QUALIFIED_BUILD_INFORMATION_SHA256, "OpenCV build differs")
    _require(int(cv2.getNumThreads()) == 1 and not bool(cv2.ocl.useOpenCL()), "OpenCV execution differs")
    return {
        "python_version": platform.python_version(),
        "opencv_version": str(cv2.__version__),
        "numpy_version": str(np.__version__),
        "cv2_binary_path": str(Path(binary).resolve()),
        "cv2_binary_sha256": binary_digest,
        "opencv_build_information_sha256": build_digest,
        "thread_count": int(cv2.getNumThreads()),
        "opencl_enabled": bool(cv2.ocl.useOpenCL()),
        "algorithm_binding_digest": algorithm_binding_digest(),
    }


@dataclass(frozen=True, slots=True)
class SparseVisualPairV1:
    pair_id: str
    frame_0_payload_digest: str
    frame_1_payload_digest: str
    visual_source_clock_id: str
    frame_0_window_start_tick: int
    frame_0_window_end_tick: int
    frame_1_window_start_tick: int
    frame_1_window_end_tick: int

    def __post_init__(self) -> None:
        _require(type(self.pair_id) is str and _IDENTIFIER.fullmatch(self.pair_id) is not None, "pair id differs")
        _validate_digest(self.frame_0_payload_digest, "frame 0 digest")
        _validate_digest(self.frame_1_payload_digest, "frame 1 digest")
        _require(
            type(self.visual_source_clock_id) is str and _IDENTIFIER.fullmatch(self.visual_source_clock_id) is not None,
            "visual source clock differs",
        )
        ticks = (
            self.frame_0_window_start_tick,
            self.frame_0_window_end_tick,
            self.frame_1_window_start_tick,
            self.frame_1_window_end_tick,
        )
        _require(all(type(value) is int and value >= 0 for value in ticks), "visual time differs")
        _require(self.frame_0_window_start_tick < self.frame_0_window_end_tick, "frame 0 time differs")
        _require(self.frame_1_window_start_tick < self.frame_1_window_end_tick, "frame 1 time differs")
        _require(self.frame_0_window_end_tick <= self.frame_1_window_start_tick, "visual time overlaps or regresses")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2mp.sparse-visual-pair.v1",
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
            "channels": 3,
            "pixel_format": "RGB8",
            "algorithm_binding_digest": algorithm_binding_digest(),
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


@dataclass(frozen=True, slots=True)
class FeatureSparseMotionEvidenceV1:
    pair_digest: str
    candidate_count: int
    candidate_covered_cell_count: int
    candidate_cell_counts: tuple[int, ...]
    valid_track_count: int
    valid_covered_cell_count: int
    valid_cell_counts: tuple[int, ...]
    component_digests: tuple[tuple[str, str], ...]
    summaries: tuple[tuple[str, dict[str, object]], ...]
    evidence_status: str
    forward_lk_calls: int
    reverse_lk_calls: int

    def __post_init__(self) -> None:
        _validate_digest(self.pair_digest, "pair digest")
        _require(0 <= self.candidate_count <= MAX_POINT_COUNT, "candidate count differs")
        _require(0 <= self.valid_track_count <= self.candidate_count, "valid track count differs")
        _require(len(self.candidate_cell_counts) == len(self.valid_cell_counts) == 96, "cell inventory differs")
        _require(sum(self.candidate_cell_counts) == self.candidate_count, "candidate cell counts differ")
        _require(sum(self.valid_cell_counts) == self.valid_track_count, "valid cell counts differ")
        _require(self.candidate_covered_cell_count == sum(value > 0 for value in self.candidate_cell_counts), "candidate coverage differs")
        _require(self.valid_covered_cell_count == sum(value > 0 for value in self.valid_cell_counts), "valid coverage differs")
        expected_status = (
            "MOTION_EVIDENCE_AVAILABLE"
            if self.valid_track_count >= MIN_VALID_TRACKS and self.valid_covered_cell_count >= MIN_VALID_CELLS
            else "INSUFFICIENT_MOTION_EVIDENCE"
        )
        _require(self.evidence_status == expected_status, "evidence status differs")
        expected_calls = 0 if self.candidate_count == 0 else 1
        _require(self.forward_lk_calls == self.reverse_lk_calls == expected_calls, "LK call count differs")
        _require(len(_canonical_bytes(self.canonical_payload())) <= MAX_RESULT_BYTES, "result exceeds byte limit")

    def canonical_payload(self) -> dict[str, object]:
        return {
            "schema": "s2mp.feature-sparse-motion-evidence.v1",
            "pair_digest": self.pair_digest,
            "algorithm_binding_digest": algorithm_binding_digest(),
            "candidate_count": self.candidate_count,
            "candidate_covered_cell_count": self.candidate_covered_cell_count,
            "candidate_cell_counts": list(self.candidate_cell_counts),
            "valid_track_count": self.valid_track_count,
            "valid_covered_cell_count": self.valid_covered_cell_count,
            "valid_cell_counts": list(self.valid_cell_counts),
            "component_digests": dict(self.component_digests),
            "summaries": dict(self.summaries),
            "evidence_status": self.evidence_status,
            "forward_lk_calls": self.forward_lk_calls,
            "reverse_lk_calls": self.reverse_lk_calls,
            "invalid_track_values_interpreted": False,
            "raw_frames_present": False,
            "point_arrays_present": False,
            "error_arrays_present": False,
        }

    def digest(self) -> str:
        return _digest(self.canonical_payload())


def _validate_frame(value: object, expected_digest: str, role: str) -> np.ndarray:
    _require(isinstance(value, np.ndarray), f"{role} is not an ndarray")
    _require(value.shape == (HEIGHT, WIDTH, 3), f"{role} geometry differs")
    _require(value.dtype == np.uint8 and value.flags.c_contiguous, f"{role} type differs")
    _require(_frame_digest(value) == expected_digest, f"{role} payload digest differs")
    return value


def detect_candidate_points(first_y: np.ndarray) -> tuple[np.ndarray, np.ndarray, tuple[int, ...]]:
    _require(isinstance(first_y, np.ndarray), "detector image is not an ndarray")
    _require(first_y.shape == (HEIGHT, WIDTH) and first_y.dtype == np.uint8, "detector image form differs")
    points: list[tuple[float, float]] = []
    cell_indices: list[int] = []
    cell_counts: list[int] = []
    for row in range(GRID_ROWS):
        top = row * CELL_HEIGHT
        bottom = top + CELL_HEIGHT
        for column in range(GRID_COLUMNS):
            left = column * CELL_WIDTH
            right = left + CELL_WIDTH
            corners = cv2.goodFeaturesToTrack(
                first_y[top:bottom, left:right],
                maxCorners=MAX_CORNERS_PER_CELL,
                qualityLevel=QUALITY_LEVEL,
                minDistance=MIN_DISTANCE,
                mask=None,
                blockSize=BLOCK_SIZE,
                useHarrisDetector=USE_HARRIS_DETECTOR,
                k=HARRIS_K,
            )
            local = [] if corners is None else [(float(item[0][0]), float(item[0][1])) for item in corners]
            local.sort(key=lambda item: (item[1], item[0]))
            cell_index = row * GRID_COLUMNS + column
            cell_counts.append(len(local))
            for x_value, y_value in local:
                points.append((x_value + left, y_value + top))
                cell_indices.append(cell_index)
    _require(len(points) <= MAX_POINT_COUNT, "candidate maximum differs")
    point_array = np.ascontiguousarray(points, dtype=np.float32).reshape(-1, 1, 2)
    cell_array = np.ascontiguousarray(cell_indices, dtype=np.int16)
    if point_array.shape[0] > 1:
        unique = np.unique(point_array.reshape(-1, 2), axis=0)
        _require(unique.shape[0] == point_array.shape[0], "candidate points are not unique")
    point_array.setflags(write=False)
    cell_array.setflags(write=False)
    return point_array, cell_array, tuple(cell_counts)


def _empty_evidence(pair: SparseVisualPairV1, cell_counts: tuple[int, ...]) -> FeatureSparseMotionEvidenceV1:
    return FeatureSparseMotionEvidenceV1(
        pair_digest=pair.digest(),
        candidate_count=0,
        candidate_covered_cell_count=0,
        candidate_cell_counts=cell_counts,
        valid_track_count=0,
        valid_covered_cell_count=0,
        valid_cell_counts=(0,) * 96,
        component_digests=(
            ("candidate_points", hashlib.sha256(b"").hexdigest()),
            ("candidate_cells", hashlib.sha256(b"").hexdigest()),
        ),
        summaries=(),
        evidence_status="INSUFFICIENT_MOTION_EVIDENCE",
        forward_lk_calls=0,
        reverse_lk_calls=0,
    )


def measure_sparse_pair(
    pair: SparseVisualPairV1,
    frame_0: np.ndarray,
    frame_1: np.ndarray,
) -> FeatureSparseMotionEvidenceV1:
    _require(type(pair) is SparseVisualPairV1, "pair type differs")
    first = _validate_frame(frame_0, pair.frame_0_payload_digest, "frame 0")
    second = _validate_frame(frame_1, pair.frame_1_payload_digest, "frame 1")
    frame_0_pre = _frame_digest(first)
    frame_1_pre = _frame_digest(second)
    first_y = _rgb_to_y(np, first)
    second_y = _rgb_to_y(np, second)
    points, point_cells, candidate_cell_counts = detect_candidate_points(first_y)
    candidate_count = int(points.shape[0])
    if candidate_count == 0:
        result = _empty_evidence(pair, candidate_cell_counts)
        _require(_frame_digest(first) == frame_0_pre and _frame_digest(second) == frame_1_pre, "input frame changed")
        return result

    criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, MAX_ITERATIONS, EPSILON)
    forward, forward_status, forward_error = cv2.calcOpticalFlowPyrLK(
        first_y,
        second_y,
        points,
        None,
        winSize=WINDOW_SIZE,
        maxLevel=MAX_LEVEL,
        criteria=criteria,
        flags=FLAGS,
        minEigThreshold=MIN_EIG_THRESHOLD,
    )
    backward, backward_status, backward_error = cv2.calcOpticalFlowPyrLK(
        second_y,
        first_y,
        forward,
        None,
        winSize=WINDOW_SIZE,
        maxLevel=MAX_LEVEL,
        criteria=criteria,
        flags=FLAGS,
        minEigThreshold=MIN_EIG_THRESHOLD,
    )
    expected_points = (candidate_count, 1, 2)
    expected_status = (candidate_count, 1)
    for role, value in (("forward points", forward), ("backward points", backward)):
        _require(isinstance(value, np.ndarray) and value.shape == expected_points and value.dtype == np.float32, f"{role} differs")
    for role, value in (("forward status", forward_status), ("backward status", backward_status)):
        _require(isinstance(value, np.ndarray) and value.shape == expected_status and value.dtype == np.uint8, f"{role} differs")
        _require(bool(np.isin(value, np.asarray((0, 1), dtype=np.uint8)).all()), f"{role} is not binary")
    for role, value in (("forward error", forward_error), ("backward error", backward_error)):
        _require(isinstance(value, np.ndarray) and value.shape == expected_status and value.dtype == np.float32, f"{role} differs")

    source_points = points.reshape(candidate_count, 2)
    forward_points = forward.reshape(candidate_count, 2)
    backward_points = backward.reshape(candidate_count, 2)
    joint = (forward_status.reshape(-1) == 1) & (backward_status.reshape(-1) == 1)
    joint_indices = np.flatnonzero(joint).astype(np.int32, copy=False)
    joint_forward = forward_points[joint_indices]
    joint_backward = backward_points[joint_indices]
    geometry = np.isfinite(joint_forward).all(axis=1) & np.isfinite(joint_backward).all(axis=1)
    geometry &= (joint_forward[:, 0] >= 0.0) & (joint_forward[:, 0] <= WIDTH - 1)
    geometry &= (joint_forward[:, 1] >= 0.0) & (joint_forward[:, 1] <= HEIGHT - 1)
    geometry &= (joint_backward[:, 0] >= 0.0) & (joint_backward[:, 0] <= WIDTH - 1)
    geometry &= (joint_backward[:, 1] >= 0.0) & (joint_backward[:, 1] <= HEIGHT - 1)
    valid_indices = np.ascontiguousarray(joint_indices[geometry], dtype=np.int32)
    valid_source = np.ascontiguousarray(source_points[valid_indices], dtype=np.float32)
    valid_forward = np.ascontiguousarray(forward_points[valid_indices], dtype=np.float32)
    valid_backward = np.ascontiguousarray(backward_points[valid_indices], dtype=np.float32)
    valid_forward_error = np.ascontiguousarray(forward_error.reshape(-1)[valid_indices], dtype=np.float32)
    valid_backward_error = np.ascontiguousarray(backward_error.reshape(-1)[valid_indices], dtype=np.float32)
    for role, value in (
        ("valid forward points", valid_forward),
        ("valid backward points", valid_backward),
        ("valid forward errors", valid_forward_error),
        ("valid backward errors", valid_backward_error),
    ):
        _require(bool(np.isfinite(value).all()), f"{role} is not finite")

    displacement = np.ascontiguousarray(np.linalg.norm(valid_forward - valid_source, axis=1), dtype=np.float32)
    cycle = np.ascontiguousarray(np.linalg.norm(valid_backward - valid_source, axis=1), dtype=np.float32)
    if valid_indices.size:
        source_rgb = _bilinear_rgb(np, first, valid_source)
        target_rgb = _bilinear_rgb(np, second, valid_forward)
        rgb_residual = np.ascontiguousarray(
            np.mean(np.abs(source_rgb - target_rgb), axis=1, dtype=np.float32) / np.float32(255.0),
            dtype=np.float32,
        )
    else:
        rgb_residual = np.empty((0,), dtype=np.float32)
    valid_cell_counts_array = np.bincount(point_cells[valid_indices].astype(np.int32), minlength=96)
    valid_cell_counts = tuple(int(value) for value in valid_cell_counts_array)
    valid_count = int(valid_indices.size)
    valid_covered_cells = sum(value > 0 for value in valid_cell_counts)
    component_digests = (
        ("candidate_points", _array_digest(points, "<f4")),
        ("candidate_cells", _array_digest(point_cells, "<i2")),
        ("forward_status", _array_digest(forward_status, "u1")),
        ("backward_status", _array_digest(backward_status, "u1")),
        ("valid_indices", _array_digest(valid_indices, "<i4")),
        ("forward_valid_points", _array_digest(valid_forward, "<f4")),
        ("backward_valid_points", _array_digest(valid_backward, "<f4")),
        ("forward_valid_errors", _array_digest(valid_forward_error, "<f4")),
        ("backward_valid_errors", _array_digest(valid_backward_error, "<f4")),
        ("displacement", _array_digest(displacement, "<f4")),
        ("cycle_residual", _array_digest(cycle, "<f4")),
        ("rgb_residual", _array_digest(rgb_residual, "<f4")),
    )
    summaries = () if valid_count == 0 else (
        ("displacement", _summary(displacement)),
        ("cycle_residual", _summary(cycle)),
        ("rgb_residual", _summary(rgb_residual)),
    )
    status = (
        "MOTION_EVIDENCE_AVAILABLE"
        if valid_count >= MIN_VALID_TRACKS and valid_covered_cells >= MIN_VALID_CELLS
        else "INSUFFICIENT_MOTION_EVIDENCE"
    )
    result = FeatureSparseMotionEvidenceV1(
        pair_digest=pair.digest(),
        candidate_count=candidate_count,
        candidate_covered_cell_count=sum(value > 0 for value in candidate_cell_counts),
        candidate_cell_counts=candidate_cell_counts,
        valid_track_count=valid_count,
        valid_covered_cell_count=valid_covered_cells,
        valid_cell_counts=valid_cell_counts,
        component_digests=component_digests,
        summaries=summaries,
        evidence_status=status,
        forward_lk_calls=1,
        reverse_lk_calls=1,
    )
    _require(_frame_digest(first) == frame_0_pre and _frame_digest(second) == frame_1_pre, "input frame changed")
    return result


__all__ = (
    "FeatureSparseMotionEvidenceV1",
    "SparseVisualPairV1",
    "S2MPMeasurementError",
    "algorithm_binding_digest",
    "detect_candidate_points",
    "measure_sparse_pair",
    "qualified_runtime_binding",
)
