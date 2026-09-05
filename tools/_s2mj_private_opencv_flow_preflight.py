"""Isolated one-shot OpenCV dense-flow capability preflight for S2-MJ."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import platform
from pathlib import Path
import sys
from typing import Any


RUN_ID = "s2mj-opencv-flow-capability-preflight-20260905-01"
STATUS_AVAILABLE = "S2MJ_DENSE_FLOW_PATH_AVAILABLE"
STATUS_UNAVAILABLE = "S2MJ_DENSE_FLOW_PATH_UNAVAILABLE"
MAX_ARTIFACT_BYTES = 65_536


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
        package_root = cv2_file.parent
        for pattern in ("cv2*.pyd", "cv2*.so", "cv2*.dll", "cv2*.dylib"):
            candidates.update(path.resolve() for path in package_root.glob(pattern) if path.is_file())
    if len(candidates) != 1:
        raise RuntimeError("loaded cv2 binary module is not uniquely bound")
    return next(iter(candidates))


def _neutral_fixture(np: Any) -> tuple[Any, Any, dict[str, object]]:
    height = 64
    width = 80
    first = np.zeros((height, width), dtype=np.uint8)
    rows, columns = np.ogrid[:height, :width]
    panel = (columns >= 18) & (columns < 54) & (rows >= 14) & (rows < 48)
    texture = (((columns // 4) + (rows // 4)) & 1) == 0
    first[panel & texture] = 224
    first[panel & ~texture] = 72
    second = np.zeros_like(first)
    second[3:, 5:] = first[:-3, :-5]
    receipt = {
        "schema": "s2mj.neutral-flow-fixture.v1",
        "width": width,
        "height": height,
        "dtype": "uint8",
        "frame_0_sha256": _digest_bytes(first.tobytes(order="C")),
        "frame_1_sha256": _digest_bytes(second.tobytes(order="C")),
        "source": "INTERNAL_NEUTRAL_PREFLIGHT_ONLY",
        "corpus_frame_used": False,
    }
    return first, second, {**receipt, "fixture_digest": _digest(receipt)}


def _flow(cv2: Any, first: Any, second: Any) -> Any:
    return cv2.calcOpticalFlowFarneback(
        first,
        second,
        None,
        0.5,
        5,
        21,
        5,
        7,
        1.5,
        0,
    )


def run_once(
    output_root: Path,
    *,
    preseal_receipt_digest: str,
    preseal_receipt_file_sha256: str,
) -> int:
    if not isinstance(output_root, Path) or not output_root.is_absolute():
        raise ValueError("output root must be an absolute Path")
    if len(preseal_receipt_digest) != 64 or len(preseal_receipt_file_sha256) != 64:
        raise ValueError("preseal digest binding differs")
    run_dir = output_root / RUN_ID
    run_dir.mkdir(parents=True, exist_ok=False)
    plan = {
        "schema": "s2mj.opencv-flow-capability-preflight-plan.v1",
        "run_id": RUN_ID,
        "preseal_receipt_digest": preseal_receipt_digest,
        "preseal_receipt_file_sha256": preseal_receipt_file_sha256,
        "preseal_receipt_opened": False,
        "corpus_files_opened": 0,
        "project_modules_imported": 0,
        "fixture_kind": "INTERNAL_NEUTRAL_80X64_UINT8",
        "flow_call_count": 2,
        "replacement_install_or_update_allowed": False,
    }
    _atomic_json(run_dir / "plan.json", {**plan, "plan_digest": _digest(plan)})

    status = STATUS_UNAVAILABLE
    error_code: str | None = None
    capability: dict[str, object] = {}
    try:
        np = importlib.import_module("numpy")
        cv2 = importlib.import_module("cv2")
        function = getattr(cv2, "calcOpticalFlowFarneback", None)
        if not callable(function):
            raise RuntimeError("calcOpticalFlowFarneback is unavailable")
        cv2.setNumThreads(1)
        cv2.ocl.setUseOpenCL(False)
        thread_count = int(cv2.getNumThreads())
        opencl_enabled = bool(cv2.ocl.useOpenCL())
        if thread_count != 1:
            raise RuntimeError("OpenCV single-thread binding differs")
        if opencl_enabled:
            raise RuntimeError("OpenCL remains enabled")
        binary_path = _loaded_binary_path(cv2)
        build_information = str(cv2.getBuildInformation())
        first, second, fixture = _neutral_fixture(np)
        flow_first = _flow(cv2, first, second)
        flow_second = _flow(cv2, first, second)
        expected_shape = (64, 80, 2)
        if flow_first.shape != expected_shape or flow_second.shape != expected_shape:
            raise RuntimeError("flow shape differs")
        if flow_first.dtype != np.float32 or flow_second.dtype != np.float32:
            raise RuntimeError("flow dtype differs")
        if not bool(np.isfinite(flow_first).all()) or not bool(np.isfinite(flow_second).all()):
            raise RuntimeError("flow contains non-finite values")
        flow_first_bytes = flow_first.astype("<f4", copy=False).tobytes(order="C")
        flow_second_bytes = flow_second.astype("<f4", copy=False).tobytes(order="C")
        flow_first_digest = _digest_bytes(flow_first_bytes)
        flow_second_digest = _digest_bytes(flow_second_bytes)
        if flow_first_bytes != flow_second_bytes:
            raise RuntimeError("repeated flow output is not bit-identical")
        capability = {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "python_executable": str(Path(sys.executable).resolve()),
            "opencv_version": str(cv2.__version__),
            "numpy_version": str(np.__version__),
            "cv2_binary_path": str(binary_path),
            "cv2_binary_size_bytes": binary_path.stat().st_size,
            "cv2_binary_sha256": _digest_bytes(binary_path.read_bytes()),
            "opencv_build_information_sha256": _digest_bytes(build_information.encode("utf-8")),
            "calc_optical_flow_farneback_present": True,
            "opencv_thread_count": thread_count,
            "opencl_enabled": opencl_enabled,
            "fixture": fixture,
            "flow_shape": list(expected_shape),
            "flow_dtype": "float32",
            "flow_0_sha256": flow_first_digest,
            "flow_1_sha256": flow_second_digest,
            "flow_outputs_bit_identical": True,
            "flow_bytes_per_result": len(flow_first_bytes),
            "corpus_frames_opened": 0,
            "project_function_calls": 0,
        }
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
        "schema": "s2mj.opencv-flow-capability-preflight-result.v1",
        "run_id": RUN_ID,
        "status": status,
        "error_code": error_code,
        "preseal_receipt_digest": preseal_receipt_digest,
        "preseal_receipt_file_sha256": preseal_receipt_file_sha256,
        "capability": capability,
        "capability_digest": capability_digest,
        "corpus_frames_opened": 0,
        "project_modules_imported": 0,
        "project_function_calls": 0,
        "install_update_or_fallback_calls": 0,
    }
    _atomic_json(run_dir / "result.json", result)
    exit_code = 0 if status == STATUS_AVAILABLE else 3
    terminal = {
        "schema": "s2mj.opencv-flow-capability-preflight-terminal.v1",
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
    parser.add_argument("--preseal-receipt-digest", required=True)
    parser.add_argument("--preseal-receipt-file-sha256", required=True)
    arguments = parser.parse_args()
    return run_once(
        arguments.output_root.resolve(),
        preseal_receipt_digest=arguments.preseal_receipt_digest,
        preseal_receipt_file_sha256=arguments.preseal_receipt_file_sha256,
    )


if __name__ == "__main__":
    raise SystemExit(main())
