"""Private one-shot S2-MQ corpus comparison and read-only verifier."""

from __future__ import annotations

from dataclasses import fields
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Any

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools._s2lv_private_pose_form_projection import PoseV1, project_pose_form
from tools import _s2mp_private_feature_sparse_correspondence as sparse
from tools import _s2mq_private_presealed_motion_corpus as corpus


AUTHORIZED_RUN_ID = "s2mq-feature-sparse-corpus-comparison-20260905-03"
MAIN_GATE = False
PAIR_COUNT = 8
MAX_RESULT_BYTES = 262_144
_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2MQRunError(ValueError):
    """The sealed S2-MQ comparison cannot be completed or verified."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MQRunError(message)


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


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="ascii"))
    _require(type(value) is dict, f"{path.name} root differs")
    return value


def _frame_digest(frame: np.ndarray) -> str:
    _require(frame.shape == (corpus.HEIGHT, corpus.WIDTH, 3), "frame geometry differs")
    _require(frame.dtype == np.uint8 and frame.flags.c_contiguous, "frame representation differs")
    return hashlib.sha256(memoryview(frame).cast("B")).hexdigest()


def _chunked_pixel_mean_l1(first: np.ndarray, second: np.ndarray) -> float:
    total = 0.0
    count = 0
    for start in range(0, corpus.HEIGHT, 135):
        left = first[start : start + 135].astype(np.int16)
        right = second[start : start + 135].astype(np.int16)
        difference = np.abs(left - right)
        total += float(np.sum(difference, dtype=np.float64))
        count += int(difference.size)
    _require(count == corpus.WIDTH * corpus.HEIGHT * 3, "pixel comparison count differs")
    return float(total / count / 255.0)


def _pose_differences(first: PoseV1, second: PoseV1) -> tuple[tuple[str, float], ...]:
    result: list[tuple[str, float]] = []
    for index, role in enumerate(("background_r", "background_g", "background_b")):
        result.append((role, float(abs(first.background_channels[index] - second.background_channels[index]))))
    for field in fields(PoseV1):
        if field.name not in {"background_channels", "support_cell_count"}:
            result.append((field.name, float(abs(getattr(first, field.name) - getattr(second, field.name)))))
    result.append(("support_cell_count", float(abs(first.support_cell_count - second.support_cell_count))))
    _require(len(result) == 16 and len({role for role, _ in result}) == 16, "pose comparison roles differ")
    return tuple(result)


def _static_baseline(first: np.ndarray, second: np.ndarray) -> dict[str, object]:
    first_pre = _frame_digest(first)
    second_pre = _frame_digest(second)
    pixel_l1 = _chunked_pixel_mean_l1(first, second)
    receptor = LocalChannelGridReceptor(VisualGridConfig())
    first_state = receptor.analyze(first, frame_index=0)
    second_state = receptor.analyze(second, frame_index=1)
    first_values = tuple(first_state.channel_values)
    second_values = tuple(second_state.channel_values)
    _require(len(first_values) == len(second_values) == 288, "visual receptor dimension differs")
    receptor_l1 = float(math.fsum(abs(a - b) for a, b in zip(first_values, second_values, strict=True)) / 288)
    first_projection = project_pose_form(first_values)
    second_projection = project_pose_form(second_values)
    pose_differences = _pose_differences(first_projection.pose, second_projection.pose)
    pose_mean = float(math.fsum(value for _, value in pose_differences) / len(pose_differences))
    form_l1 = float(
        math.fsum(
            abs(a - b)
            for a, b in zip(
                first_projection.form_descriptor.values,
                second_projection.form_descriptor.values,
                strict=True,
            )
        )
        / len(first_projection.form_descriptor.values)
    )
    result = {
        "schema": "s2mq.static-visual-baseline.v1",
        "frame_0_receptor_digest": first_state.digest(),
        "frame_1_receptor_digest": second_state.digest(),
        "frame_0_pose_digest": first_projection.pose.digest(),
        "frame_1_pose_digest": second_projection.pose.digest(),
        "frame_0_form_digest": first_projection.form_descriptor.digest(),
        "frame_1_form_digest": second_projection.form_descriptor.digest(),
        "pixel_mean_l1": pixel_l1,
        "receptor_mean_l1": receptor_l1,
        "pose_absolute_differences": [list(item) for item in pose_differences],
        "pose_mean_absolute_difference": pose_mean,
        "form_mean_l1": form_l1,
        "frame_0_pre_digest": first_pre,
        "frame_0_post_digest": _frame_digest(first),
        "frame_1_pre_digest": second_pre,
        "frame_1_post_digest": _frame_digest(second),
        "raw_frames_present": False,
    }
    _require(result["frame_0_pre_digest"] == result["frame_0_post_digest"], "baseline changed frame 0")
    _require(result["frame_1_pre_digest"] == result["frame_1_post_digest"], "baseline changed frame 1")
    return {**result, "digest": _digest(result)}


def _load_execution_preseal(preseal_root: Path) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    _require(isinstance(preseal_root, Path) and preseal_root.is_dir(), "preseal root differs")
    source = _load_json(preseal_root / "source_plan.json")
    execution = _load_json(preseal_root / "execution_plan.json")
    receipt = _load_json(preseal_root / "preseal_receipt.json")
    _require(receipt.get("preseal_id") == corpus.PRESEAL_ID, "preseal id differs")
    _require(receipt.get("source_plan_digest") == _digest(source), "source plan digest differs")
    _require(receipt.get("execution_plan_digest") == _digest(execution), "execution plan digest differs")
    source_path = Path(str(receipt.get("preseal_source_path"))).resolve()
    _require(source_path == Path(corpus.__file__).resolve(), "preseal source path differs")
    _require(receipt.get("preseal_source_sha256") == _file_digest(source_path), "preseal source changed")
    _require(execution.get("evaluation_roles_available") is False, "execution root exposes evaluation roles")
    _require(all(receipt.get(role) == 0 for role in ("pixel_analysis_calls", "receptor_calls", "pose_form_calls", "s2mp_calls", "memory_calls", "context_calls", "field_calls")), "preseal opened a forbidden function")
    return source, execution, receipt


def _load_evaluation_plan(preseal_root: Path, receipt: dict[str, object]) -> dict[str, object]:
    evaluation = _load_json(preseal_root / "evaluation_plan.json")
    _require(receipt.get("evaluation_plan_digest") == _digest(evaluation), "evaluation plan digest differs")
    return evaluation


def _source_items(source: dict[str, object]) -> dict[str, dict[str, object]]:
    frames = source.get("frames")
    _require(type(frames) is list and len(frames) == 16, "source frame inventory differs")
    result: dict[str, dict[str, object]] = {}
    for item in frames:
        _require(type(item) is dict and type(item.get("frame_id")) is str, "source frame item differs")
        _require(item["frame_id"] not in result, "duplicate source frame id")
        _require(type(item.get("payload_sha256")) is str and _DIGEST.fullmatch(item["payload_sha256"]) is not None, "source frame digest differs")
        result[item["frame_id"]] = item
    _require(source.get("frame_set_digest") == _digest(frames), "source frame set differs")
    return result


def _measure_pairs(source: dict[str, object], execution: dict[str, object]) -> list[dict[str, object]]:
    frames = _source_items(source)
    pairs = execution.get("pairs")
    _require(type(pairs) is list and len(pairs) == PAIR_COUNT, "execution pair inventory differs")
    results: list[dict[str, object]] = []
    for item in pairs:
        _require(type(item) is dict, "execution pair differs")
        first_source = frames.get(item.get("frame_0_id"))
        second_source = frames.get(item.get("frame_1_id"))
        _require(first_source is not None and second_source is not None, "execution frame source differs")
        _require(item.get("frame_0_payload_digest") == first_source.get("payload_sha256"), "frame 0 binding differs")
        _require(item.get("frame_1_payload_digest") == second_source.get("payload_sha256"), "frame 1 binding differs")
        first = corpus.render_frame(first_source["recipe"])
        second = corpus.render_frame(second_source["recipe"])
        _require(_frame_digest(first) == item["frame_0_payload_digest"], "materialized frame 0 differs")
        _require(_frame_digest(second) == item["frame_1_payload_digest"], "materialized frame 1 differs")
        pair = sparse.SparseVisualPairV1(
            pair_id=item["pair_id"],
            frame_0_payload_digest=item["frame_0_payload_digest"],
            frame_1_payload_digest=item["frame_1_payload_digest"],
            visual_source_clock_id=item["visual_source_clock_id"],
            frame_0_window_start_tick=item["frame_0_window_start_tick"],
            frame_0_window_end_tick=item["frame_0_window_end_tick"],
            frame_1_window_start_tick=item["frame_1_window_start_tick"],
            frame_1_window_end_tick=item["frame_1_window_end_tick"],
        )
        first_pre = _frame_digest(first)
        second_pre = _frame_digest(second)
        motion = sparse.measure_sparse_pair(pair, first, second)
        baseline = _static_baseline(first, second)
        _require(_frame_digest(first) == first_pre and _frame_digest(second) == second_pre, "measurement changed a frame")
        result = {
            "schema": "s2mq.pair-result.v1",
            "pair_id": item["pair_id"],
            "pair_digest": pair.digest(),
            "motion": motion.canonical_payload(),
            "motion_digest": motion.digest(),
            "baseline": baseline,
        }
        results.append({**result, "pair_result_digest": _digest(result)})
        del first, second
    return results


def _summary_mean(pair_result: dict[str, object], role: str) -> float | None:
    motion = pair_result["motion"]
    _require(type(motion) is dict, "motion result differs")
    if motion.get("evidence_status") != "MOTION_EVIDENCE_AVAILABLE":
        return None
    summaries = motion.get("summaries")
    _require(type(summaries) is dict and type(summaries.get(role)) is dict, "motion summary differs")
    value = summaries[role].get("mean")
    _require(type(value) is float and math.isfinite(value) and value >= 0.0, "motion mean differs")
    return value


def _metric_value(pair_result: dict[str, object], metric: str) -> float | None:
    if metric == "cycle_residual_mean":
        return _summary_mean(pair_result, "cycle_residual")
    if metric == "rgb_residual_mean":
        return _summary_mean(pair_result, "rgb_residual")
    baseline = pair_result["baseline"]
    _require(type(baseline) is dict, "baseline result differs")
    key = {
        "pixel_mean_l1": "pixel_mean_l1",
        "pose_mean_absolute_difference": "pose_mean_absolute_difference",
        "form_mean_l1": "form_mean_l1",
    }[metric]
    value = baseline.get(key)
    _require(type(value) is float and math.isfinite(value) and value >= 0.0, "baseline metric differs")
    return value


def _evaluate(pair_results: list[dict[str, object]], evaluation: dict[str, object]) -> dict[str, object]:
    roles = evaluation.get("roles")
    _require(type(roles) is list and len(roles) == PAIR_COUNT, "evaluation role inventory differs")
    by_pair = {item["pair_id"]: item for item in pair_results}
    by_role: dict[tuple[str, str], dict[str, object]] = {}
    for role in roles:
        _require(type(role) is dict, "evaluation role differs")
        key = (role.get("structure_stratum"), role.get("case_role"))
        _require(key not in by_role and role.get("pair_id") in by_pair, "evaluation role binding differs")
        by_role[key] = by_pair[role["pair_id"]]
    expected_keys = {(stratum, case) for stratum in ("STRUCTURE_RICH", "EDGE_POOR") for case in ("CONTINUATION", "FORM_CHANGE", "PARTIAL_OCCLUSION", "SCENE_CUT")}
    _require(set(by_role) == expected_keys, "evaluation matrix differs")

    metric_groups = {
        "TEMPORAL": ("cycle_residual_mean", "rgb_residual_mean"),
        "PIXEL": ("pixel_mean_l1",),
        "POSE": ("pose_mean_absolute_difference",),
        "FORM": ("form_mean_l1",),
    }
    relations: list[dict[str, object]] = []
    scores: dict[str, dict[str, int]] = {}
    for group, metrics in metric_groups.items():
        passed = applicable = total = 0
        for stratum in ("STRUCTURE_RICH", "EDGE_POOR"):
            continuation = by_role[(stratum, "CONTINUATION")]
            for metric in metrics:
                left = _metric_value(continuation, metric)
                for right_role in ("FORM_CHANGE", "SCENE_CUT", "PARTIAL_OCCLUSION"):
                    total += 1
                    right = _metric_value(by_role[(stratum, right_role)], metric)
                    if left is None or right is None:
                        outcome = "INSUFFICIENT_EVIDENCE"
                    else:
                        applicable += 1
                        outcome = "PASS" if left < right else "FAIL"
                        passed += int(outcome == "PASS")
                    relations.append(
                        {
                            "group": group,
                            "metric": metric,
                            "structure_stratum": stratum,
                            "left_role": "CONTINUATION",
                            "right_role": right_role,
                            "left_value": left,
                            "right_value": right,
                            "relation": "STRICTLY_LESS_THAN",
                            "outcome": outcome,
                        }
                    )
        scores[group] = {"passed": passed, "applicable": applicable, "total": total}
    all_motion_available = all(item["motion"]["evidence_status"] == "MOTION_EVIDENCE_AVAILABLE" for item in pair_results)
    temporal = scores["TEMPORAL"]
    strictly_above_each_static = all(
        temporal["passed"] * scores[group]["total"] > scores[group]["passed"] * temporal["total"]
        for group in ("PIXEL", "POSE", "FORM")
    )
    if all_motion_available and temporal["passed"] == temporal["total"] and strictly_above_each_static:
        functional_status = "S2MQ_TEMPORAL_ADDITIONAL_VALUE_OBSERVED"
    elif not any(item["motion"]["evidence_status"] == "MOTION_EVIDENCE_AVAILABLE" for item in pair_results):
        functional_status = "S2MQ_INSUFFICIENT_MOTION_EVIDENCE"
    else:
        functional_status = "S2MQ_MIXED_OR_NO_TEMPORAL_ADVANTAGE"
    result = {
        "schema": "s2mq.separate-evaluation.v1",
        "functional_status": functional_status,
        "all_motion_evidence_available": all_motion_available,
        "scores": scores,
        "relations": relations,
        "object_identity_claimed": False,
        "memory_calls": 0,
        "context_calls": 0,
        "field_calls": 0,
    }
    return {**result, "evaluation_digest": _digest(result)}


def _atomic_write(path: Path, value: dict[str, object]) -> None:
    _require(not path.exists(), "result path already exists")
    temporary = path.with_suffix(path.suffix + ".tmp")
    _require(not temporary.exists(), "temporary result path already exists")
    encoded = _canonical_bytes(value) + b"\n"
    _require(len(encoded) <= MAX_RESULT_BYTES, "result exceeds byte limit")
    temporary.write_bytes(encoded)
    temporary.replace(path)


def run_main_once(*, run_id: str, preseal_root: Path, output_root: Path) -> Path:
    global MAIN_GATE
    _require(MAIN_GATE is True, "main gate is closed")
    _require(run_id == AUTHORIZED_RUN_ID, "run id is not authorized")
    _require(isinstance(preseal_root, Path) and isinstance(output_root, Path), "path type differs")
    _require(not output_root.exists(), "output root already exists")
    output_root.mkdir(parents=True, exist_ok=False)
    try:
        source, execution, receipt = _load_execution_preseal(preseal_root)
        runtime = sparse.qualified_runtime_binding()
        runner_path = Path(__file__).resolve()
        sparse_path = Path(sparse.__file__).resolve()
        source_hashes_before = {
            "runner": _file_digest(runner_path),
            "s2mp": _file_digest(sparse_path),
            "preseal": _file_digest(Path(corpus.__file__).resolve()),
        }
        pair_results = _measure_pairs(source, execution)
        _require(len(pair_results) == PAIR_COUNT, "pair result count differs")
        evaluation_plan = _load_evaluation_plan(preseal_root, receipt)
        evaluation = _evaluate(pair_results, evaluation_plan)
        source_hashes_after = {
            "runner": _file_digest(runner_path),
            "s2mp": _file_digest(sparse_path),
            "preseal": _file_digest(Path(corpus.__file__).resolve()),
        }
        _require(source_hashes_after == source_hashes_before, "source changed during run")
        payload = {
            "schema": "s2mq.motion-corpus-comparison-result.v1",
            "run_id": run_id,
            "terminal_state": "RECORDING_COMPLETE",
            "preseal_receipt_digest": _digest(receipt),
            "source_plan_digest": _digest(source),
            "execution_plan_digest": _digest(execution),
            "evaluation_plan_digest": _digest(evaluation_plan),
            "runtime_binding": runtime,
            "source_hashes_before": source_hashes_before,
            "source_hashes_after": source_hashes_after,
            "pair_count": PAIR_COUNT,
            "pair_results": pair_results,
            "evaluation": evaluation,
            "raw_frames_present": False,
            "track_arrays_present": False,
            "object_identity_claimed": False,
            "memory_calls": 0,
            "context_calls": 0,
            "field_calls": 0,
        }
        result = {**payload, "result_digest": _digest(payload)}
        result_path = output_root / "result.json"
        _atomic_write(result_path, result)
        return result_path
    finally:
        MAIN_GATE = False


def _contains_forbidden_key(value: object) -> bool:
    forbidden = {"raw_frame", "raw_frames", "flow_field", "flow_fields", "point_array", "track_array"}
    if type(value) is dict:
        return any(key in forbidden or _contains_forbidden_key(item) for key, item in value.items())
    if type(value) is list:
        return any(_contains_forbidden_key(item) for item in value)
    return False


def verify_result_read_only(result_path: Path, preseal_root: Path) -> dict[str, object]:
    _require(isinstance(result_path, Path) and isinstance(preseal_root, Path), "verification path type differs")
    before = _file_digest(result_path)
    result = _load_json(result_path)
    source, execution, receipt = _load_execution_preseal(preseal_root)
    evaluation_plan = _load_evaluation_plan(preseal_root, receipt)
    _require(result.get("schema") == "s2mq.motion-corpus-comparison-result.v1", "result schema differs")
    _require(result.get("run_id") == AUTHORIZED_RUN_ID, "result run id differs")
    _require(result.get("terminal_state") == "RECORDING_COMPLETE", "terminal state differs")
    payload = dict(result)
    result_digest = payload.pop("result_digest", None)
    _require(type(result_digest) is str and result_digest == _digest(payload), "result digest differs")
    _require(result.get("preseal_receipt_digest") == _digest(receipt), "preseal receipt binding differs")
    _require(result.get("source_plan_digest") == _digest(source), "source plan binding differs")
    _require(result.get("execution_plan_digest") == _digest(execution), "execution plan binding differs")
    _require(result.get("evaluation_plan_digest") == _digest(evaluation_plan), "evaluation plan binding differs")
    _require(result.get("source_hashes_before") == result.get("source_hashes_after"), "source hashes differ")
    pairs = result.get("pair_results")
    _require(type(pairs) is list and len(pairs) == PAIR_COUNT, "verified pair count differs")
    expected_ids = [item["pair_id"] for item in execution["pairs"]]
    _require([item.get("pair_id") for item in pairs] == expected_ids, "verified pair order differs")
    for item in pairs:
        _require(type(item) is dict, "verified pair result differs")
        pair_payload = dict(item)
        pair_digest = pair_payload.pop("pair_result_digest", None)
        _require(pair_digest == _digest(pair_payload), "pair result digest differs")
        motion = item.get("motion")
        baseline = item.get("baseline")
        _require(type(motion) is dict and item.get("motion_digest") == _digest(motion), "motion evidence digest differs")
        _require(type(baseline) is dict, "baseline evidence differs")
        baseline_payload = dict(baseline)
        baseline_digest = baseline_payload.pop("digest", None)
        _require(baseline_digest == _digest(baseline_payload), "baseline evidence digest differs")
        _require(baseline.get("frame_0_pre_digest") == baseline.get("frame_0_post_digest"), "verified frame 0 changed")
        _require(baseline.get("frame_1_pre_digest") == baseline.get("frame_1_post_digest"), "verified frame 1 changed")
    rebuilt_evaluation = _evaluate(pairs, evaluation_plan)
    _require(result.get("evaluation") == rebuilt_evaluation, "evaluation reconstruction differs")
    _require(not _contains_forbidden_key(result), "result contains forbidden raw data")
    _require(result.get("memory_calls") == result.get("context_calls") == result.get("field_calls") == 0, "forbidden system branch was called")
    after = _file_digest(result_path)
    _require(after == before, "read-only verification changed the result")
    return {
        "schema": "s2mq.read-only-verification.v1",
        "status": "OK",
        "result_sha256_before": before,
        "result_sha256_after": after,
        "pair_count": PAIR_COUNT,
        "functional_status": result["evaluation"]["functional_status"],
    }


__all__: tuple[str, ...] = ()
