"""Isolated one-shot sparse Lucas-Kanade output-semantics preflight for S2-MN."""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import importlib
import json
import math
import os
import platform
from pathlib import Path
import sys
import threading
import time
from typing import Any


RUN_ID = "s2mn-sparse-lk-output-semantics-preflight-20260905-01"
STATUS_AVAILABLE = "S2MN_SPARSE_LK_PATH_AVAILABLE"
STATUS_UNAVAILABLE = "S2MN_SPARSE_LK_PATH_UNAVAILABLE"
MAX_PEAK_BYTES = 134_217_728
MAX_ARTIFACT_BYTES = 65_536
WIDTH = 1920
HEIGHT = 1080
GRID_COLUMNS = 12
GRID_ROWS = 8
SUBGRID_COLUMNS = 4
SUBGRID_ROWS = 4
POINT_COUNT = 1_536
MIN_VALID_TRACKS = 1_152
WINDOW_SIZE = (21, 21)
MAX_LEVEL = 3
MAX_ITERATIONS = 30
EPSILON = 0.01
MIN_EIG_THRESHOLD = 0.0001
FLAGS = 0
COMPONENT_ROLES = (
    "forward_status",
    "backward_status",
    "valid_indices",
    "forward_valid_points",
    "backward_valid_points",
    "forward_valid_errors",
    "backward_valid_errors",
    "displacement",
    "cycle_residual",
    "rgb_residual",
)
QUALIFIED_PYTHON_VERSION = "3.14.4"
QUALIFIED_OPENCV_VERSION = "4.13.0"
QUALIFIED_NUMPY_VERSION = "2.5.1"
QUALIFIED_CV2_BINARY_SHA256 = "78db0c836b952d9d5510140677463687c357a7166fddfa6ac7e31abb2d7d9bbd"
QUALIFIED_BUILD_INFORMATION_SHA256 = "8a55f551e40cf84d0fa7e2509bb9544da66782a8cbc017d7ce27a9de0ef9c1ac"


class _ProcessMemoryCounters(ctypes.Structure):
    _fields_ = (
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    )


_EXPECTED_X64_OFFSETS = {
    "cb": 0,
    "PageFaultCount": 4,
    "PeakWorkingSetSize": 8,
    "WorkingSetSize": 16,
    "QuotaPeakPagedPoolUsage": 24,
    "QuotaPagedPoolUsage": 32,
    "QuotaPeakNonPagedPoolUsage": 40,
    "QuotaNonPagedPoolUsage": 48,
    "PagefileUsage": 56,
    "PeakPagefileUsage": 64,
}


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _digest(value: object) -> str:
    return _digest_bytes(_canonical_bytes(value))


def _array_digest(value: Any, dtype: str) -> str:
    canonical = value.astype(dtype, copy=False)
    if not bool(canonical.flags.c_contiguous):
        raise RuntimeError("canonical array is not contiguous")
    return _digest_bytes(memoryview(canonical).cast("B"))


def _atomic_json(path: Path, value: object) -> None:
    data = _canonical_bytes(value, newline=True)
    if len(data) > MAX_ARTIFACT_BYTES:
        raise RuntimeError("preflight artifact exceeds byte limit")
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _bind_process_memory_api() -> tuple[object, object]:
    if ctypes.sizeof(ctypes.c_void_p) != 8:
        raise RuntimeError("S2-MN preflight requires the bound x64 ABI")
    if ctypes.sizeof(_ProcessMemoryCounters) != 72:
        raise RuntimeError("PROCESS_MEMORY_COUNTERS x64 size differs")
    observed = {
        name: int(getattr(_ProcessMemoryCounters, name).offset)
        for name, _ in _ProcessMemoryCounters._fields_
    }
    if observed != _EXPECTED_X64_OFFSETS:
        raise RuntimeError("PROCESS_MEMORY_COUNTERS x64 offsets differ")
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    psapi = ctypes.WinDLL("psapi", use_last_error=True)
    kernel32.GetCurrentProcess.argtypes = []
    kernel32.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [
        wintypes.HANDLE,
        ctypes.POINTER(_ProcessMemoryCounters),
        wintypes.DWORD,
    ]
    psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
    return kernel32, psapi


def _working_set_bytes(kernel32: object, psapi: object) -> int:
    counters = _ProcessMemoryCounters()
    counters.cb = ctypes.sizeof(counters)
    process = kernel32.GetCurrentProcess()
    ctypes.set_last_error(0)
    ok = psapi.GetProcessMemoryInfo(process, ctypes.byref(counters), counters.cb)
    if not ok:
        raise ctypes.WinError(ctypes.get_last_error())
    return int(counters.WorkingSetSize)


def _loaded_binary_path(cv2: Any) -> Path:
    suffixes = {".pyd", ".so", ".dll", ".dylib"}
    candidates: set[Path] = set()
    for name, module in tuple(sys.modules.items()):
        if name != "cv2" and not name.startswith("cv2."):
            continue
        module_file = getattr(module, "__file__", None)
        if module_file is None:
            continue
        path = Path(module_file).resolve()
        if path.suffix.lower() in suffixes and path.is_file():
            candidates.add(path)
    cv2_file = Path(str(cv2.__file__)).resolve()
    if cv2_file.suffix.lower() in suffixes and cv2_file.is_file():
        candidates.add(cv2_file)
    if not candidates and cv2_file.is_file():
        for pattern in ("cv2*.pyd", "cv2*.so", "cv2*.dll", "cv2*.dylib"):
            candidates.update(path.resolve() for path in cv2_file.parent.glob(pattern) if path.is_file())
    if len(candidates) != 1:
        raise RuntimeError("loaded cv2 binary module is not uniquely bound")
    return next(iter(candidates))


def _neutral_full_format_fixture(np: Any) -> tuple[Any, Any]:
    first = np.empty((HEIGHT, WIDTH, 3), dtype=np.uint8)
    rows, columns = np.ogrid[:HEIGHT, :WIDTH]
    checker = (((columns // 8) + (rows // 8)) & 1).astype(np.uint8)
    first[:, :, 0] = 28 + checker * 176
    first[:, :, 1] = 44 + (1 - checker) * 164
    first[:, :, 2] = 60 + checker * 92
    second = np.empty_like(first)
    second[:, :, :] = np.asarray((28, 44, 60), dtype=np.uint8)
    second[3:, 5:, :] = first[:-3, :-5, :]
    first.setflags(write=False)
    second.setflags(write=False)
    return first, second


def _rgb_to_y(np: Any, frame: Any) -> Any:
    result = np.empty((HEIGHT, WIDTH), dtype=np.uint8)
    for start in range(0, HEIGHT, 135):
        end = min(start + 135, HEIGHT)
        red = frame[start:end, :, 0].astype(np.uint32)
        green = frame[start:end, :, 1].astype(np.uint32)
        blue = frame[start:end, :, 2].astype(np.uint32)
        projected = 77 * red + 150 * green + 29 * blue + 128
        projected >>= 8
        result[start:end] = projected.astype(np.uint8)
    result.setflags(write=False)
    return result


def _point_grid(np: Any) -> Any:
    points = []
    cell_width = WIDTH / GRID_COLUMNS
    cell_height = HEIGHT / GRID_ROWS
    for cell_row in range(GRID_ROWS):
        for cell_column in range(GRID_COLUMNS):
            for sub_row in range(SUBGRID_ROWS):
                for sub_column in range(SUBGRID_COLUMNS):
                    points.append(
                        (
                            (cell_column + (sub_column + 0.5) / SUBGRID_COLUMNS) * cell_width,
                            (cell_row + (sub_row + 0.5) / SUBGRID_ROWS) * cell_height,
                        )
                    )
    result = np.asarray(points, dtype=np.float32).reshape(POINT_COUNT, 1, 2)
    result.setflags(write=False)
    return result


def _linear_percentile(ordered: list[float], percentile: float) -> float:
    if not ordered:
        raise RuntimeError("empty summary")
    position = (len(ordered) - 1) * percentile / 100.0
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return float(ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction)


def _summary(values: Any) -> dict[str, object]:
    ordered = sorted(float(value) for value in values)
    if not ordered or not all(math.isfinite(value) and value >= 0.0 for value in ordered):
        raise RuntimeError("summary values differ")
    return {
        "count": len(ordered),
        "mean": math.fsum(ordered) / len(ordered),
        "median": _linear_percentile(ordered, 50.0),
        "p95": _linear_percentile(ordered, 95.0),
        "maximum": ordered[-1],
    }


def _bilinear_rgb(np: Any, frame: Any, points: Any) -> Any:
    x = points[:, 0].astype(np.float32, copy=False)
    y = points[:, 1].astype(np.float32, copy=False)
    x0 = np.floor(x).astype(np.int32)
    y0 = np.floor(y).astype(np.int32)
    x1 = np.minimum(x0 + 1, WIDTH - 1)
    y1 = np.minimum(y0 + 1, HEIGHT - 1)
    fx = (x - x0.astype(np.float32))[:, None]
    fy = (y - y0.astype(np.float32))[:, None]
    top = frame[y0, x0].astype(np.float32) * (1.0 - fx) + frame[y0, x1].astype(np.float32) * fx
    bottom = frame[y1, x0].astype(np.float32) * (1.0 - fx) + frame[y1, x1].astype(np.float32) * fx
    return np.ascontiguousarray(top * (1.0 - fy) + bottom * fy, dtype=np.float32)


def _track_pass(cv2: Any, np: Any, first: Any, second: Any, points: Any) -> dict[str, object]:
    criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, MAX_ITERATIONS, EPSILON)
    forward, forward_status, forward_error = cv2.calcOpticalFlowPyrLK(
        first,
        second,
        points,
        None,
        winSize=WINDOW_SIZE,
        maxLevel=MAX_LEVEL,
        criteria=criteria,
        flags=FLAGS,
        minEigThreshold=MIN_EIG_THRESHOLD,
    )
    backward, backward_status, backward_error = cv2.calcOpticalFlowPyrLK(
        second,
        first,
        forward,
        None,
        winSize=WINDOW_SIZE,
        maxLevel=MAX_LEVEL,
        criteria=criteria,
        flags=FLAGS,
        minEigThreshold=MIN_EIG_THRESHOLD,
    )
    expected_points = (POINT_COUNT, 1, 2)
    expected_status = (POINT_COUNT, 1)
    for role, value in (("forward", forward), ("backward", backward)):
        if value is None or value.shape != expected_points or value.dtype != np.float32:
            raise RuntimeError(f"{role} point output differs")
    for role, value in (("forward status", forward_status), ("backward status", backward_status)):
        if value is None or value.shape != expected_status or value.dtype != np.uint8:
            raise RuntimeError(f"{role} differs")
        if not bool(np.isin(value, np.asarray((0, 1), dtype=np.uint8)).all()):
            raise RuntimeError(f"{role} contains a non-binary value")
    for role, value in (("forward error", forward_error), ("backward error", backward_error)):
        if value is None or value.shape != expected_status or value.dtype != np.float32:
            raise RuntimeError(f"{role} differs")
    source_points = points.reshape(POINT_COUNT, 2)
    forward_points = forward.reshape(POINT_COUNT, 2)
    backward_points = backward.reshape(POINT_COUNT, 2)
    joint_status = (forward_status.reshape(-1) == 1) & (backward_status.reshape(-1) == 1)
    joint_indices = np.flatnonzero(joint_status).astype(np.int32, copy=False)
    joint_forward = forward_points[joint_indices]
    joint_backward = backward_points[joint_indices]
    finite = np.isfinite(joint_forward).all(axis=1) & np.isfinite(joint_backward).all(axis=1)
    geometry = finite.copy()
    geometry &= (joint_forward[:, 0] >= 0.0) & (joint_forward[:, 0] <= WIDTH - 1)
    geometry &= (joint_forward[:, 1] >= 0.0) & (joint_forward[:, 1] <= HEIGHT - 1)
    geometry &= (joint_backward[:, 0] >= 0.0) & (joint_backward[:, 0] <= WIDTH - 1)
    geometry &= (joint_backward[:, 1] >= 0.0) & (joint_backward[:, 1] <= HEIGHT - 1)
    valid_indices = np.ascontiguousarray(joint_indices[geometry], dtype=np.int32)
    if valid_indices.size > 1 and not bool(np.all(valid_indices[1:] > valid_indices[:-1])):
        raise RuntimeError("valid grid indices are not strictly increasing")
    valid_count = int(valid_indices.size)
    if valid_count < MIN_VALID_TRACKS:
        raise RuntimeError("INSUFFICIENT_VALID_TRACKS")
    valid_source = np.ascontiguousarray(source_points[valid_indices], dtype=np.float32)
    valid_forward = np.ascontiguousarray(forward_points[valid_indices], dtype=np.float32)
    valid_backward = np.ascontiguousarray(backward_points[valid_indices], dtype=np.float32)
    valid_forward_error = np.ascontiguousarray(forward_error.reshape(-1)[valid_indices], dtype=np.float32)
    valid_backward_error = np.ascontiguousarray(backward_error.reshape(-1)[valid_indices], dtype=np.float32)
    for role, value in (
        ("forward valid points", valid_forward),
        ("backward valid points", valid_backward),
        ("forward valid errors", valid_forward_error),
        ("backward valid errors", valid_backward_error),
    ):
        if not bool(np.isfinite(value).all()):
            raise RuntimeError(f"{role} is not finite")
    displacement = np.ascontiguousarray(
        np.linalg.norm(valid_forward - valid_source, axis=1), dtype=np.float32
    )
    cycle = np.ascontiguousarray(
        np.linalg.norm(valid_backward - valid_source, axis=1), dtype=np.float32
    )
    source_rgb = _bilinear_rgb(np, first, valid_source)
    target_rgb = _bilinear_rgb(np, second, valid_forward)
    rgb_residual = np.ascontiguousarray(
        np.mean(np.abs(source_rgb - target_rgb), axis=1, dtype=np.float32) / np.float32(255.0),
        dtype=np.float32,
    )
    component_digests = {
        "forward_status": _array_digest(forward_status, "u1"),
        "backward_status": _array_digest(backward_status, "u1"),
        "valid_indices": _array_digest(valid_indices, "<i4"),
        "forward_valid_points": _array_digest(valid_forward, "<f4"),
        "backward_valid_points": _array_digest(valid_backward, "<f4"),
        "forward_valid_errors": _array_digest(valid_forward_error, "<f4"),
        "backward_valid_errors": _array_digest(valid_backward_error, "<f4"),
        "displacement": _array_digest(displacement, "<f4"),
        "cycle_residual": _array_digest(cycle, "<f4"),
        "rgb_residual": _array_digest(rgb_residual, "<f4"),
    }
    if tuple(component_digests) != COMPONENT_ROLES:
        raise RuntimeError("semantic component registry differs")
    return {
        "valid_track_count": valid_count,
        "valid_track_fraction": valid_count / POINT_COUNT,
        "component_digests": component_digests,
        "summaries": {
            "displacement": _summary(displacement),
            "cycle_residual": _summary(cycle),
            "rgb_residual": _summary(rgb_residual),
        },
    }


def run_once(output_root: Path, *, contract_file_sha256: str) -> int:
    if not isinstance(output_root, Path) or not output_root.is_absolute():
        raise ValueError("output root must be an absolute Path")
    if len(contract_file_sha256) != 64:
        raise ValueError("contract digest binding differs")
    run_dir = output_root / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=False)
    plan = {
        "schema": "s2mn.sparse-lk-output-semantics-preflight-plan.v1",
        "run_id": RUN_ID,
        "contract_file_sha256": contract_file_sha256,
        "fixture_kind": "INTERNAL_NEUTRAL_FULL_FORMAT_RGB8",
        "point_count": POINT_COUNT,
        "minimum_valid_tracks": MIN_VALID_TRACKS,
        "window_size": list(WINDOW_SIZE),
        "max_level": MAX_LEVEL,
        "max_iterations": MAX_ITERATIONS,
        "epsilon": EPSILON,
        "min_eig_threshold": MIN_EIG_THRESHOLD,
        "flags": FLAGS,
        "component_roles": list(COMPONENT_ROLES),
        "invalid_point_error_values_interpreted": False,
        "valid_index_order": "ASCENDING_ORIGINAL_GRID_INDEX",
        "comparison_rule": "EXACT_COMPONENT_DIGEST_EQUALITY",
        "forward_reverse_call_count": 4,
        "prewarming_allowed": False,
        "corpus_files_opened": 0,
        "project_modules_imported": 0,
    }
    _atomic_json(run_dir / "plan.json", {**plan, "plan_digest": _digest(plan)})
    status = STATUS_UNAVAILABLE
    error_code: str | None = None
    capability: dict[str, object] = {}
    try:
        np = importlib.import_module("numpy")
        cv2 = importlib.import_module("cv2")
        if not callable(getattr(cv2, "calcOpticalFlowPyrLK", None)):
            raise RuntimeError("calcOpticalFlowPyrLK is unavailable")
        if platform.python_version() != QUALIFIED_PYTHON_VERSION:
            raise RuntimeError("Python runtime differs")
        if str(cv2.__version__) != QUALIFIED_OPENCV_VERSION:
            raise RuntimeError("OpenCV runtime differs")
        if str(np.__version__) != QUALIFIED_NUMPY_VERSION:
            raise RuntimeError("NumPy runtime differs")
        cv2.setNumThreads(1)
        cv2.ocl.setUseOpenCL(False)
        if int(cv2.getNumThreads()) != 1 or bool(cv2.ocl.useOpenCL()):
            raise RuntimeError("OpenCV execution binding differs")
        binary_path = _loaded_binary_path(cv2)
        binary_digest = _digest_bytes(binary_path.read_bytes())
        build_information = str(cv2.getBuildInformation())
        build_digest = _digest_bytes(build_information.encode("utf-8"))
        if binary_digest != QUALIFIED_CV2_BINARY_SHA256 or build_digest != QUALIFIED_BUILD_INFORMATION_SHA256:
            raise RuntimeError("OpenCV binary binding differs")
        first_rgb, second_rgb = _neutral_full_format_fixture(np)
        points = _point_grid(np)
        fixture = {
            "schema": "s2mm.neutral-full-format-fixture.v1",
            "width": WIDTH,
            "height": HEIGHT,
            "channels": 3,
            "dtype": "uint8",
            "frame_0_sha256": _array_digest(first_rgb, "u1"),
            "frame_1_sha256": _array_digest(second_rgb, "u1"),
            "point_grid_sha256": _array_digest(points, "<f4"),
            "point_count": POINT_COUNT,
            "corpus_frame_used": False,
        }
        kernel32, psapi = _bind_process_memory_api()
        baseline_working_set = _working_set_bytes(kernel32, psapi)
        samples = [baseline_working_set]
        sampling_errors: list[BaseException] = []
        stop = threading.Event()

        def sample_memory() -> None:
            try:
                while not stop.is_set():
                    samples.append(_working_set_bytes(kernel32, psapi))
                    time.sleep(0.001)
            except BaseException as exc:
                sampling_errors.append(exc)
                stop.set()

        sampler = threading.Thread(target=sample_memory, daemon=True)
        sampler.start()
        try:
            first_y = _rgb_to_y(np, first_rgb)
            second_y = _rgb_to_y(np, second_rgb)
            first_pass = _track_pass(cv2, np, first_y, second_y, points)
            second_pass = _track_pass(cv2, np, first_y, second_y, points)
        finally:
            stop.set()
            sampler.join(timeout=2.0)
        if sampler.is_alive():
            raise RuntimeError("working-set sampler did not terminate")
        if sampling_errors:
            raise sampling_errors[0]
        process_peak_delta = max(samples) - baseline_working_set
        measured_peak_with_inputs = process_peak_delta + int(first_rgb.nbytes + second_rgb.nbytes)
        component_comparison = {
            role: {
                "first_sha256": first_pass["component_digests"][role],
                "second_sha256": second_pass["component_digests"][role],
                "bit_identical": first_pass["component_digests"][role]
                == second_pass["component_digests"][role],
            }
            for role in COMPONENT_ROLES
        }
        repeated_valid_output_bit_identical = all(
            comparison["bit_identical"] for comparison in component_comparison.values()
        )
        capability = {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_executable": str(Path(sys.executable).resolve()),
            "opencv_version": str(cv2.__version__),
            "numpy_version": str(np.__version__),
            "cv2_binary_path": str(binary_path),
            "cv2_binary_size_bytes": binary_path.stat().st_size,
            "cv2_binary_sha256": binary_digest,
            "opencv_build_information_sha256": build_digest,
            "calc_optical_flow_pyr_lk_present": True,
            "opencv_thread_count": int(cv2.getNumThreads()),
            "opencl_enabled": bool(cv2.ocl.useOpenCL()),
            "fixture": fixture,
            "frame_0_y_sha256": _array_digest(first_y, "u1"),
            "frame_1_y_sha256": _array_digest(second_y, "u1"),
            "first_measurement": first_pass,
            "second_measurement": second_pass,
            "component_comparison": component_comparison,
            "repeated_valid_output_bit_identical": repeated_valid_output_bit_identical,
            "full_status_masks_bound": True,
            "invalid_point_error_values_interpreted": False,
            "baseline_working_set_bytes": baseline_working_set,
            "process_peak_delta_bytes": process_peak_delta,
            "resident_input_frame_bytes": int(first_rgb.nbytes + second_rgb.nbytes),
            "measured_peak_with_inputs_bytes": measured_peak_with_inputs,
            "peak_bound_bytes": MAX_PEAK_BYTES,
            "corpus_frames_opened": 0,
            "project_function_calls": 0,
        }
        if measured_peak_with_inputs >= MAX_PEAK_BYTES:
            error_code = "PEAK_BOUND_EXCEEDED"
        elif not repeated_valid_output_bit_identical:
            error_code = "VALID_COMPONENTS_DIFFER"
        else:
            status = STATUS_AVAILABLE
    except Exception as exc:
        error_code = type(exc).__name__
        capability = {
            **capability,
            "failure_type": type(exc).__name__,
            "failure_message": str(exc),
            "corpus_frames_opened": 0,
            "project_function_calls": 0,
        }
    capability_digest = _digest(capability)
    result = {
        "schema": "s2mn.sparse-lk-output-semantics-preflight-result.v1",
        "run_id": RUN_ID,
        "status": status,
        "error_code": error_code,
        "contract_file_sha256": contract_file_sha256,
        "capability": capability,
        "capability_digest": capability_digest,
        "corpus_frames_opened": 0,
        "project_modules_imported": 0,
        "project_function_calls": 0,
        "memory_context_field_calls": 0,
        "install_update_fallback_calls": 0,
    }
    _atomic_json(run_dir / "result.json", result)
    exit_code = 0 if status == STATUS_AVAILABLE else 3
    terminal = {
        "schema": "s2mn.sparse-lk-output-semantics-preflight-terminal.v1",
        "run_id": RUN_ID,
        "status": status,
        "exit_code": exit_code,
        "result_file_sha256": _digest_bytes((run_dir / "result.json").read_bytes()),
        "capability_digest": capability_digest,
    }
    _atomic_json(run_dir / "terminal.json", terminal)
    marker = "AVAILABLE" if status == STATUS_AVAILABLE else "UNAVAILABLE"
    (run_dir / marker).write_text(_digest(terminal) + "\n", encoding="ascii", newline="\n")
    print(json.dumps(terminal, allow_nan=False, sort_keys=True))
    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--contract-file-sha256", required=True)
    arguments = parser.parse_args()
    return run_once(
        arguments.output_root.resolve(),
        contract_file_sha256=arguments.contract_file_sha256,
    )


if __name__ == "__main__":
    raise SystemExit(main())
