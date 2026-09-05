"""One-shot S2-MO run over the presealed S2-MJ motion corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from threading import Event, Lock, Thread
import time
from typing import Any

import cv2
import numpy as np

from _s2mj_private_presealed_motion_corpus import _render
from _s2mm_private_sparse_lk_preflight import (
    COMPONENT_ROLES,
    MAX_PEAK_BYTES,
    MIN_VALID_TRACKS,
    QUALIFIED_BUILD_INFORMATION_SHA256,
    QUALIFIED_CV2_BINARY_SHA256,
    QUALIFIED_NUMPY_VERSION,
    QUALIFIED_OPENCV_VERSION,
    QUALIFIED_PYTHON_VERSION,
    _bind_process_memory_api,
    _loaded_binary_path,
    _point_grid,
    _rgb_to_y,
    _track_pass,
    _working_set_bytes,
)


RUN_ID = "s2mo-presealed-sparse-motion-corpus-20260905-01"
MAIN_GATE = False
MAX_ARTIFACT_BYTES = 1_048_576
S2MJ_PRESEAL_RELATIVE = Path("reports/s2mj/s2mj-motion-corpus-preseal-20260905-01")
S2MN_RESULT_RELATIVE = Path(
    "reports/s2mn/s2mn-sparse-lk-output-semantics-preflight-20260905-01/result.json"
)

SOURCE_PLAN_SHA256 = "e39fabcd207b45812cac80d9228d45e14740eba8e5329dfe92784e4c14f34b5d"
SOURCE_PLAN_DIGEST = "5a77dab593e7168afc210ccb7eccc4e7c50d3237868385e6d90dda68fa22849c"
EXECUTION_PLAN_SHA256 = "eb459bd1ade3b3f7eddd46d28b5354f1ddc5de624de760a608ead03ecace7780"
EXECUTION_PLAN_DIGEST = "561ae5179be4be724356588a5891e1748493b78df141a8a9914917743f61cd69"
EVALUATION_PLAN_SHA256 = "73ff71915293587113a3ddfac28a7c1dfdbb0453ba05f371cb91f353e90b85fc"
EVALUATION_PLAN_DIGEST = "412d128841b87d583e8fb22e35d28e21dcbf195d8c6f06b2b2f31aba181a44db"
PRESEAL_RECEIPT_SHA256 = "7fafdc7e4d092add3dd78bd2015682e9094f4ba5aa2555ef2fec3bb986548034"
PRESEAL_RECEIPT_DIGEST = "d4f614aef4240babaaa7b1659cc60696f835ad9edb151b225023bc33fdc8fad5"
GENERATOR_SOURCE_SHA256 = "f55a2b1a1d920caec59941419b95fc21aa6bcb70fc8f06152df20bac9c9113a9"
SPARSE_SOURCE_SHA256 = "5bdde67336196ccc5abad85a503289339957122f8c9a81e35a3697db20dd2b88"
S2MN_RESULT_SHA256 = "7c05df7f3d4475c842da1ba4c0e24ba3a2e4d9689cbf99ef5d7a6af1dfa8384a"
S2MN_CAPABILITY_DIGEST = "2b6092b0d8b4165de60931d3e82747ef014085f6c1c5ee6120425f8b87fc6500"

_LOCK = Lock()
_USED = False


class S2MORunError(RuntimeError):
    """The bound S2-MO run cannot continue."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MORunError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _array_digest(value: np.ndarray) -> str:
    _require(value.flags.c_contiguous, "frame layout differs")
    return hashlib.sha256(memoryview(value).cast("B")).hexdigest()


def _atomic_json(path: Path, value: object) -> None:
    data = _canonical_bytes(value, newline=True)
    _require(len(data) <= MAX_ARTIFACT_BYTES, "artifact exceeds byte limit")
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _read_json(path: Path, expected_file_sha256: str) -> dict[str, object]:
    _require(path.is_file(), f"missing bound file: {path.name}")
    _require(_file_digest(path) == expected_file_sha256, f"file digest differs: {path.name}")
    value = json.loads(path.read_text(encoding="ascii"))
    _require(type(value) is dict, f"JSON root differs: {path.name}")
    return value


def _validate_object_digest(value: dict[str, object], field: str, expected: str) -> None:
    _require(value.get(field) == expected, f"{field} binding differs")
    body = {key: item for key, item in value.items() if key != field}
    _require(_digest(body) == expected, f"{field} canonical digest differs")


def _validate_source_material(source: dict[str, object]) -> tuple[dict[str, object], dict[str, object]]:
    _validate_object_digest(source, "source_plan_digest", SOURCE_PLAN_DIGEST)
    recipes = source.get("recipes")
    bindings = source.get("frame_bindings")
    _require(type(recipes) is list and len(recipes) == 16, "source recipe inventory differs")
    _require(type(bindings) is list and len(bindings) == 16, "source binding inventory differs")
    recipe_by_id = {str(item["frame_id"]): item for item in recipes}
    binding_by_id = {str(item["frame_id"]): item for item in bindings}
    _require(len(recipe_by_id) == len(binding_by_id) == 16, "source frame ids differ")
    _require(set(recipe_by_id) == set(binding_by_id), "source recipe binding differs")
    return recipe_by_id, binding_by_id


def _validate_frame_binding(binding: dict[str, object]) -> None:
    expected = str(binding.get("frame_binding_digest"))
    body = {key: value for key, value in binding.items() if key != "frame_binding_digest"}
    _require(_digest(body) == expected, "frame binding digest differs")
    _require(binding.get("pixel_format") == "RGB8", "frame pixel format differs")
    _require(binding.get("width") == 1920 and binding.get("height") == 1080, "frame geometry differs")
    _require(binding.get("channels") == 3 and binding.get("payload_bytes") == 6_220_800, "frame form differs")


def _validate_execution(execution: dict[str, object]) -> list[dict[str, object]]:
    _validate_object_digest(execution, "execution_plan_digest", EXECUTION_PLAN_DIGEST)
    _require(execution.get("evaluation_roles_available") is False, "evaluation roles leak into execution")
    pairs = execution.get("pairs")
    _require(type(pairs) is list and len(pairs) == 8, "execution pair inventory differs")
    _require([item.get("pair_id") for item in pairs] == [f"pair-{index:03d}" for index in range(1, 9)], "pair order differs")
    for pair in pairs:
        expected = str(pair.get("pair_source_digest"))
        body = {key: value for key, value in pair.items() if key != "pair_source_digest"}
        _require(_digest(body) == expected, "pair source digest differs")
        _require(pair["frame_0_window_end_tick"] <= pair["frame_1_window_start_tick"], "pair time differs")
    return pairs


def _runtime_binding(workspace_root: Path) -> dict[str, object]:
    generator_source = workspace_root / "tools/_s2mj_private_presealed_motion_corpus.py"
    sparse_source = workspace_root / "tools/_s2mm_private_sparse_lk_preflight.py"
    _require(_file_digest(generator_source) == GENERATOR_SOURCE_SHA256, "generator source differs")
    _require(_file_digest(sparse_source) == SPARSE_SOURCE_SHA256, "sparse source differs")
    s2mn_result = _read_json(workspace_root / S2MN_RESULT_RELATIVE, S2MN_RESULT_SHA256)
    _require(s2mn_result.get("status") == "S2MN_SPARSE_LK_PATH_AVAILABLE", "S2-MN status differs")
    _require(s2mn_result.get("capability_digest") == S2MN_CAPABILITY_DIGEST, "S2-MN capability differs")
    cv2.setNumThreads(1)
    cv2.ocl.setUseOpenCL(False)
    binary_path = _loaded_binary_path(cv2)
    binary_sha256 = _file_digest(binary_path)
    build_sha256 = hashlib.sha256(str(cv2.getBuildInformation()).encode("utf-8")).hexdigest()
    import platform

    _require(platform.python_version() == QUALIFIED_PYTHON_VERSION, "Python runtime differs")
    _require(str(cv2.__version__) == QUALIFIED_OPENCV_VERSION, "OpenCV runtime differs")
    _require(str(np.__version__) == QUALIFIED_NUMPY_VERSION, "NumPy runtime differs")
    _require(binary_sha256 == QUALIFIED_CV2_BINARY_SHA256, "cv2 binary differs")
    _require(build_sha256 == QUALIFIED_BUILD_INFORMATION_SHA256, "OpenCV build differs")
    _require(int(cv2.getNumThreads()) == 1 and not bool(cv2.ocl.useOpenCL()), "OpenCV execution differs")
    return {
        "python_version": platform.python_version(),
        "opencv_version": str(cv2.__version__),
        "numpy_version": str(np.__version__),
        "cv2_binary_sha256": binary_sha256,
        "opencv_build_information_sha256": build_sha256,
        "s2mn_capability_digest": S2MN_CAPABILITY_DIGEST,
        "sparse_source_sha256": SPARSE_SOURCE_SHA256,
        "generator_source_sha256": GENERATOR_SOURCE_SHA256,
        "opencv_thread_count": int(cv2.getNumThreads()),
        "opencl_enabled": bool(cv2.ocl.useOpenCL()),
    }


def _materialize_frame(
    recipe: dict[str, object],
    binding: dict[str, object],
) -> np.ndarray:
    _validate_frame_binding(binding)
    _require(recipe.get("frame_id") == binding.get("frame_id"), "frame recipe id differs")
    _require(recipe.get("pair_id") == binding.get("pair_id"), "frame recipe pair differs")
    frame = _render(recipe)
    _require(frame.shape == (1080, 1920, 3) and frame.dtype == np.uint8, "rendered frame differs")
    _require(_array_digest(frame) == binding.get("payload_sha256"), "rendered payload differs")
    return frame


def _pair_receipt(
    pair: dict[str, object],
    frame_0_binding: dict[str, object],
    frame_1_binding: dict[str, object],
    measurement: dict[str, object],
) -> dict[str, object]:
    _require(measurement.get("valid_track_count", 0) >= MIN_VALID_TRACKS, "INSUFFICIENT_VALID_TRACKS")
    component_digests = measurement.get("component_digests")
    _require(type(component_digests) is dict, "component digest form differs")
    _require(tuple(component_digests) == COMPONENT_ROLES, "component digest roles differ")
    body = {
        "schema": "s2mo.sparse-motion-pair-receipt.v1",
        "pair_id": pair["pair_id"],
        "pair_source_digest": pair["pair_source_digest"],
        "frame_0_binding_digest": frame_0_binding["frame_binding_digest"],
        "frame_1_binding_digest": frame_1_binding["frame_binding_digest"],
        "frame_0_payload_sha256": frame_0_binding["payload_sha256"],
        "frame_1_payload_sha256": frame_1_binding["payload_sha256"],
        "visual_source_clock_id": pair["visual_source_clock_id"],
        "valid_track_count": measurement["valid_track_count"],
        "valid_track_fraction": measurement["valid_track_fraction"],
        "component_digests": component_digests,
        "summaries": measurement["summaries"],
        "invalid_track_values_interpreted": False,
        "forward_lk_calls": 1,
        "reverse_lk_calls": 1,
        "raw_arrays_present": False,
    }
    return {**body, "pair_measurement_digest": _digest(body)}


def _execute_pairs(
    source: dict[str, object],
    execution: dict[str, object],
    runtime_binding: dict[str, object],
    contract_file_sha256: str,
) -> tuple[dict[str, object], int]:
    recipe_by_id, binding_by_id = _validate_source_material(source)
    pairs = _validate_execution(execution)
    points = _point_grid(np)
    kernel32, psapi = _bind_process_memory_api()
    baseline_working_set = _working_set_bytes(kernel32, psapi)
    samples = [baseline_working_set]
    sampling_errors: list[BaseException] = []
    stop = Event()

    def sample_memory() -> None:
        try:
            while not stop.is_set():
                samples.append(_working_set_bytes(kernel32, psapi))
                time.sleep(0.001)
        except BaseException as exc:
            sampling_errors.append(exc)
            stop.set()

    receipts: list[dict[str, object]] = []
    sampler = Thread(target=sample_memory, daemon=True)
    sampler.start()
    try:
        for pair in pairs:
            first_id = str(pair["frame_0_id"])
            second_id = str(pair["frame_1_id"])
            first_binding = binding_by_id[first_id]
            second_binding = binding_by_id[second_id]
            _require(first_binding["frame_binding_digest"] == pair["frame_0_binding_digest"], "frame 0 pair binding differs")
            _require(second_binding["frame_binding_digest"] == pair["frame_1_binding_digest"], "frame 1 pair binding differs")
            first_rgb = _materialize_frame(recipe_by_id[first_id], first_binding)
            second_rgb = _materialize_frame(recipe_by_id[second_id], second_binding)
            first_y = _rgb_to_y(np, first_rgb)
            second_y = _rgb_to_y(np, second_rgb)
            measurement = _track_pass(cv2, np, first_y, second_y, points)
            receipts.append(_pair_receipt(pair, first_binding, second_binding, measurement))
            del measurement, first_y, second_y, first_rgb, second_rgb
    finally:
        stop.set()
        sampler.join(timeout=2.0)
    _require(not sampler.is_alive(), "working-set sampler did not terminate")
    if sampling_errors:
        raise sampling_errors[0]
    peak_delta = max(samples) - baseline_working_set
    _require(peak_delta < MAX_PEAK_BYTES, "sparse corpus process peak exceeds bound")
    _require(len(receipts) == 8, "pair receipt count differs")
    body = {
        "schema": "s2mo.sparse-motion-execution-evidence.v1",
        "run_id": RUN_ID,
        "contract_file_sha256": contract_file_sha256,
        "source_plan_digest": SOURCE_PLAN_DIGEST,
        "execution_plan_digest": EXECUTION_PLAN_DIGEST,
        "preseal_receipt_digest": PRESEAL_RECEIPT_DIGEST,
        "runtime_binding": runtime_binding,
        "pair_receipts": receipts,
        "pair_measurement_digests": [item["pair_measurement_digest"] for item in receipts],
        "pair_count": 8,
        "frame_count": 16,
        "forward_lk_calls": 8,
        "reverse_lk_calls": 8,
        "minimum_valid_tracks_per_pair": MIN_VALID_TRACKS,
        "process_peak_delta_bytes": peak_delta,
        "process_peak_bound_bytes": MAX_PEAK_BYTES,
        "raw_payloads_persisted": 0,
        "receptor_calls": 0,
        "memory_calls": 0,
        "context_calls": 0,
        "field_calls": 0,
    }
    return {**body, "execution_evidence_digest": _digest(body)}, peak_delta


def _metric(receipts: dict[str, dict[str, object]], pair_id: str, role: str, statistic: str) -> float:
    return float(receipts[pair_id]["summaries"][role][statistic])


def _evaluate(
    evaluation: dict[str, object],
    evidence: dict[str, object],
) -> dict[str, object]:
    _validate_object_digest(evaluation, "evaluation_plan_digest", EVALUATION_PLAN_DIGEST)
    _require(evaluation.get("numeric_match_threshold") is None, "numeric match threshold is forbidden")
    cases = evaluation.get("cases")
    _require(type(cases) is list and len(cases) == 8, "evaluation case inventory differs")
    receipts = {str(item["pair_id"]): item for item in evidence["pair_receipts"]}
    _require(len(receipts) == 8, "execution receipt inventory differs")
    by_group: dict[str, dict[str, str]] = {}
    for case in cases:
        body = {key: value for key, value in case.items() if key != "evaluation_case_digest"}
        _require(_digest(body) == case.get("evaluation_case_digest"), "evaluation case digest differs")
        by_group.setdefault(str(case["comparison_group_id"]), {})[str(case["evaluation_role"])] = str(case["pair_id"])
    expected_roles = {"CONTINUED_MOTION", "FORM_CHANGE", "PARTIAL_OCCLUSION", "SCENE_CUT"}
    _require(set(by_group) == {"comparison-group-01", "comparison-group-02"}, "evaluation groups differ")
    _require(all(set(group) == expected_roles for group in by_group.values()), "evaluation roles differ")
    checks: list[dict[str, object]] = []
    for group_id in sorted(by_group):
        roles = by_group[group_id]
        continued = roles["CONTINUED_MOTION"]
        form_change = roles["FORM_CHANGE"]
        occlusion = roles["PARTIAL_OCCLUSION"]
        scene_cut = roles["SCENE_CUT"]
        continued_cycle = _metric(receipts, continued, "cycle_residual", "mean")
        form_cycle = _metric(receipts, form_change, "cycle_residual", "mean")
        scene_cycle = _metric(receipts, scene_cut, "cycle_residual", "mean")
        continued_rgb = _metric(receipts, continued, "rgb_residual", "mean")
        form_rgb = _metric(receipts, form_change, "rgb_residual", "mean")
        scene_rgb = _metric(receipts, scene_cut, "rgb_residual", "mean")
        continued_rgb_p95 = _metric(receipts, continued, "rgb_residual", "p95")
        occlusion_rgb_p95 = _metric(receipts, occlusion, "rgb_residual", "p95")
        rows = (
            (
                "CONTINUED_CYCLE_LT_FORM_CHANGE_AND_SCENE_CUT",
                continued_cycle < form_cycle and continued_cycle < scene_cycle,
                {"continued": continued_cycle, "form_change": form_cycle, "scene_cut": scene_cycle},
            ),
            (
                "CONTINUED_WARPED_RGB_LT_FORM_CHANGE_AND_SCENE_CUT",
                continued_rgb < form_rgb and continued_rgb < scene_rgb,
                {"continued": continued_rgb, "form_change": form_rgb, "scene_cut": scene_rgb},
            ),
            (
                "OCCLUSION_RGB_P95_GT_CONTINUED_RGB_P95",
                occlusion_rgb_p95 > continued_rgb_p95,
                {"continued": continued_rgb_p95, "partial_occlusion": occlusion_rgb_p95},
            ),
            (
                "SCENE_CUT_NOT_EQUAL_OR_BETTER_THAN_CONTINUED_ON_BOTH_CORE_METRICS",
                not (scene_cycle <= continued_cycle and scene_rgb <= continued_rgb),
                {
                    "continued_cycle": continued_cycle,
                    "scene_cut_cycle": scene_cycle,
                    "continued_rgb": continued_rgb,
                    "scene_cut_rgb": scene_rgb,
                },
            ),
        )
        for rule, passed, values in rows:
            checks.append({"comparison_group_id": group_id, "rule": rule, "passed": passed, "values": values})
    passed_count = sum(1 for item in checks if item["passed"])
    if passed_count == 8:
        functional_status = "S2MO_MOTION_CORRESPONDENCE_OBSERVABLE"
    elif passed_count == 0:
        functional_status = "S2MO_MOTION_CORRESPONDENCE_NOT_SEPARABLE"
    else:
        functional_status = "S2MO_MOTION_CORRESPONDENCE_MIXED"
    run_binding_body = {
        "run_id": RUN_ID,
        "execution_evidence_digest": evidence["execution_evidence_digest"],
        "evaluation_plan_digest": EVALUATION_PLAN_DIGEST,
    }
    body = {
        "schema": "s2mo.sparse-motion-evaluation-result.v1",
        "run_id": RUN_ID,
        "evaluation_run_binding": {
            **run_binding_body,
            "evaluation_run_binding_digest": _digest(run_binding_body),
        },
        "checks": checks,
        "passed_rule_count": passed_count,
        "rule_count": 8,
        "functional_status": functional_status,
        "numeric_match_threshold": None,
        "object_identity_claimed": False,
    }
    return {**body, "evaluation_result_digest": _digest(body)}


def run_main_once(workspace_root: Path, output_root: Path, *, contract_file_sha256: str) -> int:
    global _USED
    _require(MAIN_GATE is True, "main gate is closed")
    _require(isinstance(workspace_root, Path) and workspace_root.is_absolute(), "workspace root differs")
    _require(isinstance(output_root, Path) and output_root.is_absolute(), "output root differs")
    _require(len(contract_file_sha256) == 64, "contract digest differs")
    _require(not _USED and _LOCK.acquire(blocking=False), "run is consumed")
    _USED = True
    run_dir = output_root / RUN_ID
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
        preseal = workspace_root / S2MJ_PRESEAL_RELATIVE
        receipt = _read_json(preseal / "preseal-receipt.json", PRESEAL_RECEIPT_SHA256)
        _validate_object_digest(receipt, "preseal_receipt_digest", PRESEAL_RECEIPT_DIGEST)
        source = _read_json(preseal / "source-plan.json", SOURCE_PLAN_SHA256)
        execution = _read_json(preseal / "execution-plan.json", EXECUTION_PLAN_SHA256)
        runtime_binding = _runtime_binding(workspace_root)
        evidence, _ = _execute_pairs(source, execution, runtime_binding, contract_file_sha256)
        _atomic_json(run_dir / "execution-evidence.json", evidence)

        evaluation = _read_json(preseal / "evaluation-plan.json", EVALUATION_PLAN_SHA256)
        evaluation_result = _evaluate(evaluation, evidence)
        _atomic_json(run_dir / "evaluation-result.json", evaluation_result)
        terminal_body = {
            "schema": "s2mo.sparse-motion-terminal.v1",
            "run_id": RUN_ID,
            "recording_status": "RECORDING_COMPLETE",
            "functional_status": evaluation_result["functional_status"],
            "execution_evidence_file_sha256": _file_digest(run_dir / "execution-evidence.json"),
            "evaluation_result_file_sha256": _file_digest(run_dir / "evaluation-result.json"),
            "exit_code": 0,
        }
        terminal = {**terminal_body, "terminal_digest": _digest(terminal_body)}
        _atomic_json(run_dir / "terminal.json", terminal)
        (run_dir / "COMPLETE").write_text(_digest(terminal) + "\n", encoding="ascii", newline="\n")
        print(json.dumps(terminal, allow_nan=False, sort_keys=True))
        return 0
    except Exception as exc:
        terminal_body = {
            "schema": "s2mo.sparse-motion-terminal.v1",
            "run_id": RUN_ID,
            "recording_status": "NOT_EVALUABLE",
            "functional_status": None,
            "failure_type": type(exc).__name__,
            "failure_message": str(exc),
            "exit_code": 3,
        }
        terminal = {**terminal_body, "terminal_digest": _digest(terminal_body)}
        if run_dir.is_dir() and not (run_dir / "terminal.json").exists():
            _atomic_json(run_dir / "terminal.json", terminal)
            (run_dir / "NOT_EVALUABLE").write_text(_digest(terminal) + "\n", encoding="ascii", newline="\n")
        print(json.dumps(terminal, allow_nan=False, sort_keys=True))
        return 3
    finally:
        _LOCK.release()


def main() -> int:
    global MAIN_GATE
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--contract-file-sha256", required=True)
    arguments = parser.parse_args()
    MAIN_GATE = True
    try:
        return run_main_once(
            arguments.workspace_root.resolve(),
            arguments.output_root.resolve(),
            contract_file_sha256=arguments.contract_file_sha256,
        )
    finally:
        MAIN_GATE = False


if __name__ == "__main__":
    raise SystemExit(main())
