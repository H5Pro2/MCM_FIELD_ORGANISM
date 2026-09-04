"""Private read-only receptor-to-memory compatibility comparison."""

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
from tools import _s2lu_private_visual_memory_compatibility_corpus as corpus


SCHEMA = "s2lu.visual-memory-compatibility-comparison.v1"
COMPARISON_ID = "s2lu-visual-memory-compatibility-comparison-20260905-01"
PLAN_RELATIVE_PATH = "reports/s2lu/s2lu-visual-memory-compatibility-corpus-20260905-01/presealed-plan.json"
EXPECTED_PLAN_SHA256 = "12d6507c292681191a23cfa56ae3d8fa5e3c51403b58dc12396e7bfdd2ee55bb"
EXPECTED_PLAN_DIGEST = "92ebf3a622af2aa8d4f754f3142d400bb80da381a220b5139eee70b1deb89c20"
MAX_RESULT_BYTES = 262_144
COMPARISON_ENABLED = False

_LOCK = Lock()
_USED = False


class S2LUComparisonError(RuntimeError):
    """The sealed compatibility comparison cannot be evaluated exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LUComparisonError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_plan(workspace_root: Path) -> dict[str, object]:
    path = workspace_root / PLAN_RELATIVE_PATH
    raw = path.read_bytes()
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


def _selected(values: tuple[float, ...], positions: tuple[int, ...]) -> tuple[float, ...]:
    _require(bool(positions) and len(set(positions)) == len(positions), "mask positions differ")
    _require(min(positions) >= 0 and max(positions) < len(values), "mask position is outside representation")
    return tuple(values[index] for index in positions)


def _metric_summary(rows: tuple[dict[str, object], ...], field: str) -> dict[str, object]:
    values = tuple(float(row[field]) for row in rows)
    _require(bool(values) and all(math.isfinite(value) and value >= 0.0 for value in values), "metric values differ")
    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": math.fsum(values) / len(values),
        "count_at_or_below_visual_slow_0_01": sum(value <= 0.01 for value in values),
        "count_at_or_below_fast_0_2": sum(value <= 0.2 for value in values),
        "pair_count": len(values),
    }


def _mask_coverage(config: VisualGridConfig, visible: tuple[int, ...]) -> dict[str, object]:
    mapped = tuple(
        {
            "position": position,
            "row": position // (config.grid_columns * 3),
            "column": (position % (config.grid_columns * 3)) // 3,
            "channel": position % 3,
        }
        for position in visible
    )
    full_cells = tuple(
        {"row": row, "column": column}
        for row in range(config.grid_rows)
        for column in range(config.grid_columns)
        if sum(item["row"] == row and item["column"] == column for item in mapped) == 3
    )
    partial_cells = tuple(
        {
            "row": row,
            "column": column,
            "channels": [item["channel"] for item in mapped if item["row"] == row and item["column"] == column],
        }
        for row in range(config.grid_rows)
        for column in range(config.grid_columns)
        if 0 < sum(item["row"] == row and item["column"] == column for item in mapped) < 3
    )
    payload = {
        "visible_value_count": len(visible),
        "visible_fraction": len(visible) / config.carrier_count,
        "rows_represented": sorted({item["row"] for item in mapped}),
        "full_cells": list(full_cells),
        "partial_cells": list(partial_cells),
        "position_bindings": list(mapped),
    }
    return {**payload, "coverage_digest": _digest(payload)}


def _pair_rows(
    baseline: dict[str, tuple[float, ...]],
    gradients: dict[str, tuple[float, ...]],
    family_by_content: dict[str, str],
    variant_by_content: dict[str, str],
    visible: tuple[int, ...],
) -> tuple[dict[str, object], ...]:
    rows = []
    for left, right in combinations(sorted(baseline), 2):
        left_visible = _selected(baseline[left], visible)
        right_visible = _selected(baseline[right], visible)
        payload = {
            "left_content_id": left,
            "right_content_id": right,
            "left_variant_id": variant_by_content[left],
            "right_variant_id": variant_by_content[right],
            "relation": "WITHIN_FAMILY" if family_by_content[left] == family_by_content[right] else "BETWEEN_FAMILY",
            "baseline_full_mean_l1": _mean_l1(baseline[left], baseline[right]),
            "baseline_visible_mean_l1": _mean_l1(left_visible, right_visible),
            "baseline_visible_exact_equal": left_visible == right_visible,
            "diagnostic_gradient_full_mean_l1": _mean_l1(gradients[left], gradients[right]),
        }
        rows.append({**payload, "pair_digest": _digest(payload)})
    return tuple(rows)


def _relation_summary(rows: tuple[dict[str, object], ...], relation: str) -> dict[str, object]:
    selected = tuple(row for row in rows if row["relation"] == relation)
    _require(bool(selected), "pair relation is empty")
    payload = {
        "relation": relation,
        "pair_count": len(selected),
        "baseline_full_mean_l1": _metric_summary(selected, "baseline_full_mean_l1"),
        "baseline_visible_mean_l1": _metric_summary(selected, "baseline_visible_mean_l1"),
        "diagnostic_gradient_full_mean_l1": _metric_summary(selected, "diagnostic_gradient_full_mean_l1"),
        "baseline_visible_exact_equal_count": sum(bool(row["baseline_visible_exact_equal"]) for row in selected),
    }
    return {**payload, "summary_digest": _digest(payload)}


def build_comparison(workspace_root: Path) -> dict[str, object]:
    plan = _load_plan(workspace_root)
    recipes = {str(item["content_id"]): item for item in plan["generation_root"]["recipes"]}
    bindings = {str(item["content_id"]): item for item in plan["generation_root"]["source_bindings"]}
    family_by_content = {
        str(content_id): str(family["family_id"])
        for family in plan["evaluation_root"]["families"]
        for content_id in family["content_ids"]
    }
    variant_by_content = {str(item["content_id"]): str(item["variant_id"]) for item in recipes.values()}
    visible = tuple(int(value) for value in plan["evaluation_root"]["fixed_visual_mask"]["visible_positions"])
    masked = tuple(int(value) for value in plan["evaluation_root"]["fixed_visual_mask"]["masked_positions"])
    _require(visible == tuple(range(32)) and masked == tuple(range(32, 288)), "fixed mask differs")
    _require(set(visible).isdisjoint(masked) and tuple(sorted(visible + masked)) == tuple(range(288)), "mask partition differs")

    config = VisualGridConfig()
    receptor = LocalChannelGridReceptor(config)
    baseline: dict[str, tuple[float, ...]] = {}
    gradients: dict[str, tuple[float, ...]] = {}
    state_bindings = []
    for frame_index, content_id in enumerate(sorted(recipes)):
        frame = corpus.render_frame(recipes[content_id])
        raw = frame.tobytes(order="C")
        binding = bindings[content_id]
        _require(hashlib.sha256(raw).hexdigest() == binding["payload_sha256"], "source payload differs")
        _require(len(raw) == binding["payload_bytes"], "source size differs")
        receptor_state = receptor.analyze(frame, frame_index=frame_index)
        baseline_values = tuple(receptor_state.channel_values)
        gradient_values = _local_gradients(frame)
        _require(len(baseline_values) == 288 and len(gradient_values) == 576, "representation dimension differs")
        _require(all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in baseline_values + gradient_values), "representation value differs")
        baseline[content_id] = baseline_values
        gradients[content_id] = gradient_values
        state_payload = {
            "content_id": content_id,
            "family_id": family_by_content[content_id],
            "variant_id": variant_by_content[content_id],
            "source_payload_sha256": binding["payload_sha256"],
            "baseline_receptor_state_digest": receptor_state.digest(),
            "baseline_values_digest": _digest(list(baseline_values)),
            "diagnostic_gradient_values_digest": _digest(list(gradient_values)),
        }
        state_bindings.append({**state_payload, "state_binding_digest": _digest(state_payload)})
        del raw, frame, receptor_state, baseline_values, gradient_values

    pairs = _pair_rows(baseline, gradients, family_by_content, variant_by_content, visible)
    _require(len(pairs) == 120, "complete pair inventory differs")
    summaries = tuple(_relation_summary(pairs, relation) for relation in ("WITHIN_FAMILY", "BETWEEN_FAMILY"))
    within = next(item for item in summaries if item["relation"] == "WITHIN_FAMILY")
    between = next(item for item in summaries if item["relation"] == "BETWEEN_FAMILY")
    _require(within["pair_count"] == 56 and between["pair_count"] == 64, "pair partition differs")

    information = {
        "full_vector_different_but_visible_exact_equal_count": sum(
            row["baseline_full_mean_l1"] > 0.0 and row["baseline_visible_exact_equal"] for row in pairs
        ),
        "between_family_visible_exact_collision_count": between["baseline_visible_exact_equal_count"],
        "within_family_visible_exact_equal_count": within["baseline_visible_exact_equal_count"],
        "between_family_visible_metric_at_or_below_visual_slow_count": between["baseline_visible_mean_l1"]["count_at_or_below_visual_slow_0_01"],
        "within_family_full_metric_above_visual_slow_count": within["pair_count"] - within["baseline_full_mean_l1"]["count_at_or_below_visual_slow_0_01"],
    }
    mask_payload = {
        "mask_plan_digest": plan["evaluation_root"]["fixed_visual_mask"]["mask_plan_digest"],
        "visible_positions": list(visible),
        "masked_positions": list(masked),
        "coverage": _mask_coverage(config, visible),
        "information": information,
    }
    payload = {
        "schema": SCHEMA,
        "comparison_id": COMPARISON_ID,
        "status": "S2LU_VISUAL_MEMORY_COMPATIBILITY_EVALUATED",
        "plan_binding": {
            "plan_digest": EXPECTED_PLAN_DIGEST,
            "plan_file_sha256": EXPECTED_PLAN_SHA256,
        },
        "source_count": len(recipes),
        "state_bindings": state_bindings,
        "complete_pair_distances": list(pairs),
        "relation_summaries": list(summaries),
        "fixed_partial_cue_mask_analysis": {**mask_payload, "analysis_digest": _digest(mask_payload)},
        "diagnostic_thresholds": {"visual_slow": 0.01, "fast": 0.2},
        "calls": {"baseline_visual_receptor": len(recipes), "memory": 0, "context": 0, "field": 0},
        "thresholds_changed": False,
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
    _require(record.get("status") == "S2LU_VISUAL_MEMORY_COMPATIBILITY_EVALUATED", "comparison status differs")
    _require(record.get("plan_binding") == {"plan_digest": EXPECTED_PLAN_DIGEST, "plan_file_sha256": EXPECTED_PLAN_SHA256}, "plan binding differs")
    _require(record.get("source_count") == 16 and len(record.get("state_bindings", ())) == 16, "source count differs")
    pairs = record.get("complete_pair_distances", ())
    _require(len(pairs) == 120, "pair count differs")
    _require(sum(row.get("relation") == "WITHIN_FAMILY" for row in pairs) == 56, "within pair count differs")
    _require(sum(row.get("relation") == "BETWEEN_FAMILY" for row in pairs) == 64, "between pair count differs")
    _require(record.get("calls") == {"baseline_visual_receptor": 16, "memory": 0, "context": 0, "field": 0}, "call boundary differs")
    _require(record.get("thresholds_changed") is False and record.get("production_integration") is False, "scope boundary differs")
    _require(record.get("raw_payload_retained") is False, "raw payload boundary differs")
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed comparison")
    return {
        "verification_status": "RECORDING_COMPLETE",
        "comparison_file_sha256": before,
        "comparison_digest": record["comparison_digest"],
    }


__all__: tuple[str, ...] = ()
