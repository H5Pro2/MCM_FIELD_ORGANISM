"""Read-only masked-form comparison over the frozen S2-LV and S2-LW corpora."""

from __future__ import annotations

from itertools import combinations
import hashlib
import json
import math
import os
from pathlib import Path
from threading import Lock
from typing import Callable

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lv_private_pose_form_corpus as lv_corpus
from tools import _s2lv_private_pose_form_projection as full_projection
from tools import _s2lw_private_spatial_mask_corpus as lw_corpus
from tools import _s2lx_private_masked_pose_form_projection as masked_projection


SCHEMA = "s2lx.masked-pose-form-comparison.v1"
COMPARISON_ID = "s2lx-masked-pose-form-comparison-20260905-01"
MAX_RESULT_BYTES = 2_097_152
COMPARISON_ENABLED = False

LV_PLAN = (
    "reports/s2lv/s2lv-pose-form-corpus-20260905-01/presealed-plan.json",
    "1e8276f1a884549c783bccd63f2866bdb73714e11d9d6fbc4e4dc3c9112cfa61",
    "plan_digest",
    "eff02f90623be8bb92c999c17289a4a4d4e118b98173c3cfa36c25ee4b941521",
)
LV_RESULT = (
    "reports/s2lv/s2lv-pose-form-comparison-20260905-01/comparison.json",
    "3e5bdc0f0a88b92818048a464d9ca31cc137421c2b95e37879158adf9c610aa1",
    "comparison_digest",
    "4d968bed48335dd50517590c8319293b05125ca279f9b131a90ec0370e4653c1",
)
LW_PLAN = (
    "reports/s2lw/s2lw-spatial-mask-corpus-20260905-01/presealed-plan.json",
    "082dbeb8dd1c84980c7bb828812a58a14ca7752d9f7f5f9348b32d2da914fb7d",
    "plan_digest",
    "cec9a123c41358ff6837dc48731494cac8c02a49737689a089c3a0e641c2318d",
)
LW_RESULT = (
    "reports/s2lw/s2lw-spatial-mask-comparison-20260905-01/comparison.json",
    "0683c9c20086ada603a01d1aa658fd82bf8c611fb0229c4ff16aaed829bb4939",
    "comparison_digest",
    "1b8a99d0341b05bade0c5de7e57daa9add09462b57355db57af87e88f6026dcb",
)
MASK_IDS = ("TOP_ROW_32", "SPATIAL_SEEDED_32", "SPATIAL_SEEDED_96")
METHOD_IDS = (
    "FULL_288",
    "TOP_ROW_32",
    "SPATIAL_SEEDED_32",
    "SPATIAL_SEEDED_96",
    "FULL_FORM_DESCRIPTOR_12X12_V1",
    "MASKED_FORM_DESCRIPTOR_96_V1",
)

_LOCK = Lock()
_USED = False


class S2LXComparisonError(RuntimeError):
    """The frozen masked-form comparison cannot be evaluated exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LXComparisonError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_bound_record(workspace_root: Path, binding: tuple[str, str, str, str]) -> dict[str, object]:
    relative_path, expected_sha256, digest_key, expected_digest = binding
    raw = (workspace_root / relative_path).read_bytes()
    _require(hashlib.sha256(raw).hexdigest() == expected_sha256, "frozen artifact file changed")
    value = json.loads(raw.decode("ascii"))
    _require(type(value) is dict and raw == _canonical_bytes(value, newline=True), "frozen artifact is not canonical")
    payload = dict(value)
    _require(payload.pop(digest_key, None) == _digest(payload) == expected_digest, "frozen artifact digest differs")
    return value


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    _require(len(left) == len(right) and len(left) > 0, "distance dimensions differ")
    return math.fsum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


def _centroid(vectors: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    _require(bool(vectors) and len({len(item) for item in vectors}) == 1, "centroid inputs differ")
    return tuple(math.fsum(vector[index] for vector in vectors) / len(vectors) for index in range(len(vectors[0])))


def _select(values: tuple[float, ...], positions: tuple[int, ...]) -> tuple[float, ...]:
    _require(type(values) is tuple and len(values) == 288, "visual values differ")
    return tuple(values[position] for position in positions)


def _leave_one_out(
    method_id: str,
    vectors: dict[str, tuple[float, ...]],
    families: tuple[dict[str, object], ...],
) -> dict[str, object]:
    family_members = {str(family["family_id"]): tuple(str(item) for item in family["content_ids"]) for family in families}
    rows = []
    for expected_family, members in family_members.items():
        for content_id in members:
            distances = []
            for family_id, candidates in family_members.items():
                training = tuple(item for item in candidates if item != content_id)
                family_centroid = _centroid(tuple(vectors[item] for item in training))
                distances.append({"family_id": family_id, "mean_l1": _mean_l1(vectors[content_id], family_centroid)})
            minimum = min(item["mean_l1"] for item in distances)
            tied = tuple(item["family_id"] for item in distances if item["mean_l1"] == minimum)
            ordered = sorted(distances, key=lambda item: (item["mean_l1"], item["family_id"]))
            row = {
                "content_id": content_id,
                "expected_family_id": expected_family,
                "predicted_family_id": ordered[0]["family_id"],
                "correct": len(tied) == 1 and tied[0] == expected_family,
                "ambiguous": len(tied) > 1,
                "minimum_tie_count": len(tied),
                "nearest_margin": ordered[1]["mean_l1"] - ordered[0]["mean_l1"],
                "distances": distances,
            }
            rows.append({**row, "classification_digest": _digest(row)})
    payload = {
        "method_id": method_id,
        "method": "LEAVE_ONE_OUT_NEAREST_FAMILY_CENTROID",
        "correct": sum(bool(row["correct"]) for row in rows),
        "ambiguous": sum(bool(row["ambiguous"]) for row in rows),
        "total": len(rows),
        "rows": rows,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def _pair_rows(
    method_vectors: dict[str, dict[str, tuple[float, ...]]],
    family_by_content: dict[str, str],
) -> tuple[dict[str, object], ...]:
    rows = []
    content_ids = sorted(next(iter(method_vectors.values())))
    for left, right in combinations(content_ids, 2):
        distances = {method_id: _mean_l1(method_vectors[method_id][left], method_vectors[method_id][right]) for method_id in METHOD_IDS}
        payload = {
            "left_content_id": left,
            "right_content_id": right,
            "relation": "WITHIN_FAMILY" if family_by_content[left] == family_by_content[right] else "BETWEEN_FAMILY",
            "mean_l1": distances,
        }
        rows.append({**payload, "pair_digest": _digest(payload)})
    return tuple(rows)


def _pair_summaries(rows: tuple[dict[str, object], ...]) -> tuple[dict[str, object], ...]:
    results = []
    for relation in ("WITHIN_FAMILY", "BETWEEN_FAMILY"):
        selected = tuple(row for row in rows if row["relation"] == relation)
        methods = {}
        for method_id in METHOD_IDS:
            values = tuple(float(row["mean_l1"][method_id]) for row in selected)
            methods[method_id] = {
                "minimum": min(values),
                "maximum": max(values),
                "mean": math.fsum(values) / len(values),
                "pair_count": len(values),
            }
        payload = {"relation": relation, "pair_count": len(selected), "methods": methods}
        results.append({**payload, "summary_digest": _digest(payload)})
    return tuple(results)


def _historical_counts(record: dict[str, object], key: str) -> dict[str, int]:
    source = {str(item[key]): int(item["correct"]) for item in record["leave_one_out_evaluations"]}
    return source


def _evaluate_dataset(
    dataset_id: str,
    plan: dict[str, object],
    render_frame: Callable[[dict[str, object]], np.ndarray],
    masks: dict[str, tuple[int, ...]],
    mask_96_digest: str,
) -> dict[str, object]:
    recipes = {str(item["content_id"]): item for item in plan["generation_root"]["recipes"]}
    bindings = {str(item["content_id"]): item for item in plan["generation_root"]["source_bindings"]}
    family_by_content = {str(item["content_id"]): str(item["family_id"]) for item in recipes.values()}
    receptor = LocalChannelGridReceptor(VisualGridConfig())
    method_vectors: dict[str, dict[str, tuple[float, ...]]] = {method_id: {} for method_id in METHOD_IDS}
    state_bindings = []
    for frame_index, content_id in enumerate(sorted(recipes)):
        frame = render_frame(recipes[content_id])
        raw = frame.tobytes(order="C")
        _require(hashlib.sha256(raw).hexdigest() == bindings[content_id]["payload_sha256"], "source payload differs")
        state = receptor.analyze(frame, frame_index=frame_index)
        values = tuple(state.channel_values)
        full = full_projection.project_pose_form(values)
        masked_view = masked_projection.bind_masked_visual_view(values, masks["SPATIAL_SEEDED_96"], mask_96_digest)
        masked = masked_projection.project_masked_pose_form(masked_view)
        per_method = {
            "FULL_288": values,
            "TOP_ROW_32": _select(values, masks["TOP_ROW_32"]),
            "SPATIAL_SEEDED_32": _select(values, masks["SPATIAL_SEEDED_32"]),
            "SPATIAL_SEEDED_96": _select(values, masks["SPATIAL_SEEDED_96"]),
            "FULL_FORM_DESCRIPTOR_12X12_V1": full.form_descriptor.values,
            "MASKED_FORM_DESCRIPTOR_96_V1": masked.form_descriptor.values,
        }
        for method_id, representation_values in per_method.items():
            method_vectors[method_id][content_id] = representation_values
        state_payload = {
            "content_id": content_id,
            "source_payload_sha256": bindings[content_id]["payload_sha256"],
            "receptor_state_digest": state.digest(),
            "full_values_digest": _digest(list(values)),
            "full_form_descriptor_digest": full.form_descriptor.digest(),
            "masked_view_digest": masked_view.digest(),
            "masked_observed_values_digest": masked_view.observed_values_digest,
            "masked_pose_digest": masked.pose.digest(),
            "masked_form_descriptor": masked.form_descriptor.canonical_payload(),
            "masked_form_descriptor_digest": masked.form_descriptor.digest(),
        }
        state_bindings.append({**state_payload, "state_binding_digest": _digest(state_payload)})
        del raw, frame, state, values, full, masked_view, masked, per_method
    pairs = _pair_rows(method_vectors, family_by_content)
    _require(len(pairs) == 496, "dataset pair inventory differs")
    summaries = _pair_summaries(pairs)
    evaluations = [_leave_one_out(method_id, method_vectors[method_id], tuple(plan["evaluation_root"]["families"])) for method_id in METHOD_IDS]
    payload = {
        "dataset_id": dataset_id,
        "source_count": len(recipes),
        "state_bindings": state_bindings,
        "complete_pair_distances": list(pairs),
        "pair_summaries": list(summaries),
        "leave_one_out_evaluations": evaluations,
    }
    return {**payload, "dataset_digest": _digest(payload)}


def build_comparison(workspace_root: Path) -> dict[str, object]:
    lv_plan = _load_bound_record(workspace_root, LV_PLAN)
    lv_result = _load_bound_record(workspace_root, LV_RESULT)
    lw_plan = _load_bound_record(workspace_root, LW_PLAN)
    lw_result = _load_bound_record(workspace_root, LW_RESULT)
    masks = {str(item["mask_id"]): tuple(int(position) for position in item["positions"]) for item in lw_plan["mask_root"]["masks"]}
    _require(tuple(masks) == MASK_IDS, "frozen mask inventory differs")
    mask_96 = next(item for item in lw_plan["mask_root"]["masks"] if item["mask_id"] == "SPATIAL_SEEDED_96")
    _require(len(masks["SPATIAL_SEEDED_96"]) == 96, "frozen 96-value mask differs")

    lv_dataset = _evaluate_dataset("S2LV_CORPUS", lv_plan, lv_corpus.render_frame, masks, str(mask_96["mask_digest"]))
    lw_dataset = _evaluate_dataset("S2LW_CORPUS", lw_plan, lw_corpus.render_frame, masks, str(mask_96["mask_digest"]))
    lv_counts = {item["method_id"]: item["correct"] for item in lv_dataset["leave_one_out_evaluations"]}
    lw_counts = {item["method_id"]: item["correct"] for item in lw_dataset["leave_one_out_evaluations"]}
    historical_lv = _historical_counts(lv_result, "representation_id")
    historical_lw = _historical_counts(lw_result, "representation_id")
    reproduction = {
        "s2lv_full_288": lv_counts["FULL_288"] == historical_lv["BLOCK_MEAN_12X8_RGB"] == 14,
        "s2lv_full_form": lv_counts["FULL_FORM_DESCRIPTOR_12X12_V1"] == historical_lv["FORM_DESCRIPTOR_12X12_V1"] == 32,
        "s2lw_full_288": lw_counts["FULL_288"] == historical_lw["FULL_288"] == 18,
        "s2lw_top_row_32": lw_counts["TOP_ROW_32"] == historical_lw["TOP_ROW_32"] == 0,
        "s2lw_spatial_32": lw_counts["SPATIAL_SEEDED_32"] == historical_lw["SPATIAL_SEEDED_32"] == 7,
        "s2lw_spatial_96": lw_counts["SPATIAL_SEEDED_96"] == historical_lw["SPATIAL_SEEDED_96"] == 17,
    }
    _require(all(reproduction.values()), "historical baseline reproduction differs")
    payload = {
        "schema": SCHEMA,
        "comparison_id": COMPARISON_ID,
        "status": "S2LX_MASKED_POSE_FORM_COMPARISON_EVALUATED",
        "frozen_artifact_bindings": {
            "s2lv_plan_sha256": LV_PLAN[1],
            "s2lv_plan_digest": LV_PLAN[3],
            "s2lv_result_sha256": LV_RESULT[1],
            "s2lv_result_digest": LV_RESULT[3],
            "s2lw_plan_sha256": LW_PLAN[1],
            "s2lw_plan_digest": LW_PLAN[3],
            "s2lw_result_sha256": LW_RESULT[1],
            "s2lw_result_digest": LW_RESULT[3],
            "spatial_96_mask_digest": mask_96["mask_digest"],
        },
        "method_ids": list(METHOD_IDS),
        "mask_application": "IDENTICAL_SPATIAL_SEEDED_96_TO_EVERY_CUE_AND_CANDIDATE",
        "missing_values": "NOT_PRESENT_NOT_IMPUTED",
        "historical_baseline_reproduction": reproduction,
        "datasets": [lv_dataset, lw_dataset],
        "calls": {"visual_receptor": 64, "memory": 0, "context": 0, "field": 0},
        "thresholds_selected_or_changed": False,
        "training_or_parameter_search": False,
        "hidden_values_completed": False,
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
    _require(record.get("status") == "S2LX_MASKED_POSE_FORM_COMPARISON_EVALUATED", "comparison status differs")
    _require(record.get("method_ids") == list(METHOD_IDS), "method inventory differs")
    _require(len(record.get("datasets", ())) == 2 and all(len(item.get("complete_pair_distances", ())) == 496 for item in record["datasets"]), "dataset inventory differs")
    _require(record.get("calls") == {"visual_receptor": 64, "memory": 0, "context": 0, "field": 0}, "call boundary differs")
    _require(record.get("thresholds_selected_or_changed") is False and record.get("production_integration") is False, "scope boundary differs")
    _require(record.get("hidden_values_completed") is False and record.get("raw_payload_retained") is False, "hidden-value boundary differs")
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed comparison")
    return {"verification_status": "RECORDING_COMPLETE", "comparison_file_sha256": before, "comparison_digest": record["comparison_digest"]}


__all__: tuple[str, ...] = ()
