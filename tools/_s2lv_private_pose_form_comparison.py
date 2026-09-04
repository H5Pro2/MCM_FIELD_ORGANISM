"""Private read-only comparison of pose/form views and the unchanged baseline."""

from __future__ import annotations

from itertools import combinations
import hashlib
import json
import math
import os
from pathlib import Path
from threading import Lock

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lv_private_pose_form_corpus as corpus
from tools import _s2lv_private_pose_form_projection as projection


SCHEMA = "s2lv.pose-form-comparison.v1"
COMPARISON_ID = "s2lv-pose-form-comparison-20260905-01"
PLAN_RELATIVE_PATH = "reports/s2lv/s2lv-pose-form-corpus-20260905-01/presealed-plan.json"
EXPECTED_PLAN_SHA256 = "1e8276f1a884549c783bccd63f2866bdb73714e11d9d6fbc4e4dc3c9112cfa61"
EXPECTED_PLAN_DIGEST = "eff02f90623be8bb92c999c17289a4a4d4e118b98173c3cfa36c25ee4b941521"
MAX_RESULT_BYTES = 1_048_576
COMPARISON_ENABLED = False

_LOCK = Lock()
_USED = False


class S2LVComparisonError(RuntimeError):
    """The sealed pose/form comparison cannot be evaluated exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LVComparisonError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_plan(workspace_root: Path) -> dict[str, object]:
    raw = (workspace_root / PLAN_RELATIVE_PATH).read_bytes()
    _require(hashlib.sha256(raw).hexdigest() == EXPECTED_PLAN_SHA256, "sealed plan file changed")
    value = json.loads(raw.decode("ascii"))
    _require(type(value) is dict and raw == _canonical_bytes(value, newline=True), "sealed plan is not canonical")
    payload = dict(value)
    _require(payload.pop("plan_digest", None) == _digest(payload) == EXPECTED_PLAN_DIGEST, "sealed plan digest differs")
    return value


def _local_gradients(frame: np.ndarray) -> tuple[float, ...]:
    _require(frame.shape == (1080, 1920, 3) and frame.dtype == np.uint8, "gradient input differs")
    blocks = frame.reshape(8, 135, 12, 160, 3).transpose(0, 2, 1, 3, 4).astype(np.int16)
    horizontal = np.abs(np.diff(blocks, axis=3)).mean(axis=(2, 3), dtype=np.float64) / 255.0
    vertical = np.abs(np.diff(blocks, axis=2)).mean(axis=(2, 3), dtype=np.float64) / 255.0
    return tuple(float(value) for value in np.stack((horizontal, vertical), axis=-1).reshape(-1))


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    _require(len(left) == len(right) and len(left) > 0, "distance dimensions differ")
    return math.fsum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


def _centroid(vectors: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    _require(bool(vectors) and len({len(item) for item in vectors}) == 1, "centroid inputs differ")
    return tuple(math.fsum(vector[index] for vector in vectors) / len(vectors) for index in range(len(vectors[0])))


def _metric_summary(rows: tuple[dict[str, object], ...], field: str, *, include_memory_thresholds: bool) -> dict[str, object]:
    values = tuple(float(row[field]) for row in rows)
    result: dict[str, object] = {
        "minimum": min(values),
        "maximum": max(values),
        "mean": math.fsum(values) / len(values),
        "pair_count": len(values),
    }
    if include_memory_thresholds:
        result.update({
            "count_at_or_below_visual_slow_0_01": sum(value <= 0.01 for value in values),
            "count_at_or_below_fast_0_2": sum(value <= 0.2 for value in values),
        })
    return result


def _pair_rows(
    baseline: dict[str, tuple[float, ...]],
    forms: dict[str, tuple[float, ...]],
    gradients: dict[str, tuple[float, ...]],
    poses: dict[str, projection.PoseV1],
    family_by_content: dict[str, str],
    variant_by_content: dict[str, str],
    visible: tuple[int, ...],
) -> tuple[dict[str, object], ...]:
    rows = []
    for left, right in combinations(sorted(baseline), 2):
        left_visible = tuple(baseline[left][index] for index in visible)
        right_visible = tuple(baseline[right][index] for index in visible)
        left_pose, right_pose = poses[left], poses[right]
        payload = {
            "left_content_id": left,
            "right_content_id": right,
            "left_variant_id": variant_by_content[left],
            "right_variant_id": variant_by_content[right],
            "relation": "WITHIN_FAMILY" if family_by_content[left] == family_by_content[right] else "BETWEEN_FAMILY",
            "same_variant": variant_by_content[left] == variant_by_content[right],
            "baseline_full_mean_l1": _mean_l1(baseline[left], baseline[right]),
            "form_descriptor_mean_l1": _mean_l1(forms[left], forms[right]),
            "diagnostic_gradient_mean_l1": _mean_l1(gradients[left], gradients[right]),
            "fixed_mask_visible_mean_l1": _mean_l1(left_visible, right_visible),
            "fixed_mask_visible_exact_equal": left_visible == right_visible,
            "pose_centroid_mean_l1": (abs(left_pose.centroid_x - right_pose.centroid_x) + abs(left_pose.centroid_y - right_pose.centroid_y)) / 2.0,
            "pose_extent_mean_l1": (abs(left_pose.extent_width - right_pose.extent_width) + abs(left_pose.extent_height - right_pose.extent_height)) / 2.0,
            "pose_activation_absolute_difference": abs(left_pose.total_activation - right_pose.total_activation),
        }
        rows.append({**payload, "pair_digest": _digest(payload)})
    return tuple(rows)


def _relation_summary(rows: tuple[dict[str, object], ...], relation: str) -> dict[str, object]:
    selected = tuple(row for row in rows if row["relation"] == relation)
    payload = {
        "relation": relation,
        "pair_count": len(selected),
        "baseline_full_mean_l1": _metric_summary(selected, "baseline_full_mean_l1", include_memory_thresholds=True),
        "form_descriptor_mean_l1": _metric_summary(selected, "form_descriptor_mean_l1", include_memory_thresholds=False),
        "diagnostic_gradient_mean_l1": _metric_summary(selected, "diagnostic_gradient_mean_l1", include_memory_thresholds=False),
        "fixed_mask_visible_mean_l1": _metric_summary(selected, "fixed_mask_visible_mean_l1", include_memory_thresholds=True),
        "fixed_mask_visible_exact_equal_count": sum(bool(row["fixed_mask_visible_exact_equal"]) for row in selected),
        "pose_centroid_mean_l1": _metric_summary(selected, "pose_centroid_mean_l1", include_memory_thresholds=False),
        "pose_extent_mean_l1": _metric_summary(selected, "pose_extent_mean_l1", include_memory_thresholds=False),
    }
    return {**payload, "summary_digest": _digest(payload)}


def _leave_one_out(
    representation_id: str,
    vectors: dict[str, tuple[float, ...]],
    families: tuple[dict[str, object], ...],
) -> dict[str, object]:
    rows = []
    family_members = {str(family["family_id"]): tuple(str(item) for item in family["content_ids"]) for family in families}
    for expected_family, members in family_members.items():
        for content_id in members:
            distances = []
            for family_id, candidates in family_members.items():
                training = tuple(item for item in candidates if item != content_id)
                candidate_centroid = _centroid(tuple(vectors[item] for item in training))
                distances.append({"family_id": family_id, "mean_l1": _mean_l1(vectors[content_id], candidate_centroid)})
            predicted = min(distances, key=lambda item: (item["mean_l1"], item["family_id"]))["family_id"]
            row = {
                "content_id": content_id,
                "expected_family_id": expected_family,
                "predicted_family_id": predicted,
                "correct": predicted == expected_family,
                "distances": distances,
            }
            rows.append({**row, "classification_digest": _digest(row)})
    payload = {
        "representation_id": representation_id,
        "method": "LEAVE_ONE_OUT_NEAREST_FAMILY_CENTROID",
        "correct": sum(bool(row["correct"]) for row in rows),
        "total": len(rows),
        "rows": rows,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def build_comparison(workspace_root: Path) -> dict[str, object]:
    plan = _load_plan(workspace_root)
    recipes = {str(item["content_id"]): item for item in plan["generation_root"]["recipes"]}
    bindings = {str(item["content_id"]): item for item in plan["generation_root"]["source_bindings"]}
    family_by_content = {str(item["content_id"]): str(item["family_id"]) for item in recipes.values()}
    variant_by_content = {str(item["content_id"]): str(item["variant_id"]) for item in recipes.values()}
    visible = tuple(int(item) for item in plan["evaluation_root"]["fixed_visual_mask"]["visible_positions"])
    _require(visible == tuple(range(32)), "fixed visible positions differ")

    receptor = LocalChannelGridReceptor(VisualGridConfig())
    baseline: dict[str, tuple[float, ...]] = {}
    forms: dict[str, tuple[float, ...]] = {}
    gradients: dict[str, tuple[float, ...]] = {}
    poses: dict[str, projection.PoseV1] = {}
    state_bindings = []
    for frame_index, content_id in enumerate(sorted(recipes)):
        frame = corpus.render_frame(recipes[content_id])
        raw = frame.tobytes(order="C")
        _require(hashlib.sha256(raw).hexdigest() == bindings[content_id]["payload_sha256"], "source payload differs")
        state = receptor.analyze(frame, frame_index=frame_index)
        baseline_values = tuple(state.channel_values)
        projected = projection.project_pose_form(baseline_values)
        gradient_values = _local_gradients(frame)
        baseline[content_id] = baseline_values
        forms[content_id] = projected.form_descriptor.values
        gradients[content_id] = gradient_values
        poses[content_id] = projected.pose
        state_payload = {
            "content_id": content_id,
            "family_id": family_by_content[content_id],
            "variant_id": variant_by_content[content_id],
            "source_payload_sha256": bindings[content_id]["payload_sha256"],
            "receptor_state_digest": state.digest(),
            "baseline_values_digest": projected.input_values_digest,
            "pose": projected.pose.canonical_payload(),
            "pose_digest": projected.pose.digest(),
            "form_descriptor": projected.form_descriptor.canonical_payload(),
            "form_descriptor_digest": projected.form_descriptor.digest(),
            "gradient_values_digest": _digest(list(gradient_values)),
            "projection_digest": projected.digest(),
        }
        state_bindings.append({**state_payload, "state_binding_digest": _digest(state_payload)})
        del raw, frame, state, baseline_values, projected, gradient_values

    pairs = _pair_rows(baseline, forms, gradients, poses, family_by_content, variant_by_content, visible)
    _require(len(pairs) == 496, "complete pair inventory differs")
    summaries = tuple(_relation_summary(pairs, relation) for relation in ("WITHIN_FAMILY", "BETWEEN_FAMILY"))
    within = next(item for item in summaries if item["relation"] == "WITHIN_FAMILY")
    between = next(item for item in summaries if item["relation"] == "BETWEEN_FAMILY")
    _require(within["pair_count"] == 112 and between["pair_count"] == 384, "pair partition differs")
    overlap = {
        "baseline": {
            "maximum_within": within["baseline_full_mean_l1"]["maximum"],
            "minimum_between": between["baseline_full_mean_l1"]["minimum"],
            "separation_margin": between["baseline_full_mean_l1"]["minimum"] - within["baseline_full_mean_l1"]["maximum"],
        },
        "form_descriptor": {
            "maximum_within": within["form_descriptor_mean_l1"]["maximum"],
            "minimum_between": between["form_descriptor_mean_l1"]["minimum"],
            "separation_margin": between["form_descriptor_mean_l1"]["minimum"] - within["form_descriptor_mean_l1"]["maximum"],
        },
    }
    mask_analysis = {
        "mask_plan_digest": plan["evaluation_root"]["fixed_visual_mask"]["mask_plan_digest"],
        "visible_positions": list(visible),
        "visible_rows": [0],
        "visible_value_fraction": len(visible) / 288,
        "within_exact_equal_count": within["fixed_mask_visible_exact_equal_count"],
        "between_exact_collision_count": between["fixed_mask_visible_exact_equal_count"],
        "within_metric_at_or_below_visual_slow_count": within["fixed_mask_visible_mean_l1"]["count_at_or_below_visual_slow_0_01"],
        "between_metric_at_or_below_visual_slow_count": between["fixed_mask_visible_mean_l1"]["count_at_or_below_visual_slow_0_01"],
    }
    families = tuple(plan["evaluation_root"]["families"])
    payload = {
        "schema": SCHEMA,
        "comparison_id": COMPARISON_ID,
        "status": "S2LV_POSE_FORM_COMPARISON_EVALUATED",
        "plan_binding": {"plan_digest": EXPECTED_PLAN_DIGEST, "plan_file_sha256": EXPECTED_PLAN_SHA256},
        "source_count": len(recipes),
        "state_bindings": state_bindings,
        "complete_pair_distances": list(pairs),
        "relation_summaries": list(summaries),
        "distribution_overlap": overlap,
        "leave_one_out_evaluations": [
            _leave_one_out("BLOCK_MEAN_12X8_RGB", baseline, families),
            _leave_one_out("FORM_DESCRIPTOR_12X12_V1", forms, families),
        ],
        "fixed_partial_cue_mask_analysis": {**mask_analysis, "analysis_digest": _digest(mask_analysis)},
        "diagnostic_thresholds": {"visual_slow": 0.01, "fast": 0.2},
        "calls": {"baseline_visual_receptor": len(recipes), "memory": 0, "context": 0, "field": 0},
        "thresholds_selected_or_changed": False,
        "result_controls_source_inclusion": False,
        "raw_payload_retained": False,
        "production_integration": False,
    }
    return {**payload, "comparison_digest": _digest(payload)}


def write_comparison_once(workspace_root: Path, output_root: Path, *, comparison_id: str) -> Path:
    global COMPARISON_ENABLED, _USED
    _require(COMPARISON_ENABLED is True and comparison_id == COMPARISON_ID, "comparison is not authorized")
    _require(not _USED and _LOCK.acquire(blocking=False), "comparison is already consumed")
    _USED = True
    try:
        record = build_comparison(workspace_root)
        run_dir = output_root / comparison_id
        run_dir.mkdir(parents=True, exist_ok=False)
        target = run_dir / "comparison.json"
        temporary = run_dir / ".comparison.json.tmp"
        data = _canonical_bytes(record, newline=True)
        _require(len(data) <= MAX_RESULT_BYTES, "comparison exceeds bounded envelope")
        descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, target)
        except Exception:
            if temporary.exists():
                temporary.unlink()
            raise
        return target
    finally:
        COMPARISON_ENABLED = False
        _LOCK.release()


def verify_comparison_file(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    before = hashlib.sha256(raw).hexdigest()
    _require(len(raw) <= MAX_RESULT_BYTES, "comparison file exceeds bounded envelope")
    record = json.loads(raw.decode("ascii"))
    _require(raw == _canonical_bytes(record, newline=True), "comparison file is not canonical")
    payload = dict(record)
    _require(payload.pop("comparison_digest", None) == _digest(payload), "comparison digest differs")
    _require(record.get("status") == "S2LV_POSE_FORM_COMPARISON_EVALUATED", "comparison status differs")
    _require(record.get("plan_binding") == {"plan_digest": EXPECTED_PLAN_DIGEST, "plan_file_sha256": EXPECTED_PLAN_SHA256}, "plan binding differs")
    _require(record.get("source_count") == 32 and len(record.get("state_bindings", ())) == 32, "source count differs")
    pairs = record.get("complete_pair_distances", ())
    _require(len(pairs) == 496, "pair count differs")
    _require(sum(row.get("relation") == "WITHIN_FAMILY" for row in pairs) == 112, "within count differs")
    _require(sum(row.get("relation") == "BETWEEN_FAMILY" for row in pairs) == 384, "between count differs")
    _require(record.get("calls") == {"baseline_visual_receptor": 32, "memory": 0, "context": 0, "field": 0}, "call boundary differs")
    _require(record.get("thresholds_selected_or_changed") is False and record.get("production_integration") is False, "scope boundary differs")
    _require(record.get("raw_payload_retained") is False, "raw payload boundary differs")
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed comparison")
    return {
        "verification_status": "RECORDING_COMPLETE",
        "comparison_file_sha256": before,
        "comparison_digest": record["comparison_digest"],
    }


__all__: tuple[str, ...] = ()
