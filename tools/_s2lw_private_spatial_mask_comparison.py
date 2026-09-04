"""Private read-only comparison of coordinate-bound visual masks."""

from __future__ import annotations

from itertools import combinations
import hashlib
import json
import math
import os
from pathlib import Path
from threading import Lock

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lw_private_spatial_mask_corpus as corpus


SCHEMA = "s2lw.spatial-mask-comparison.v1"
COMPARISON_ID = "s2lw-spatial-mask-comparison-20260905-01"
PLAN_RELATIVE_PATH = "reports/s2lw/s2lw-spatial-mask-corpus-20260905-01/presealed-plan.json"
EXPECTED_PLAN_SHA256 = "082dbeb8dd1c84980c7bb828812a58a14ca7752d9f7f5f9348b32d2da914fb7d"
EXPECTED_PLAN_DIGEST = "cec9a123c41358ff6837dc48731494cac8c02a49737689a089c3a0e641c2318d"
MAX_RESULT_BYTES = 1_048_576
COMPARISON_ENABLED = False

_LOCK = Lock()
_USED = False


class S2LWComparisonError(RuntimeError):
    """The sealed spatial-mask comparison cannot be evaluated exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LWComparisonError(message)


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


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    _require(len(left) == len(right) and len(left) > 0, "distance dimensions differ")
    return math.fsum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


def _centroid(vectors: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    _require(bool(vectors) and len({len(item) for item in vectors}) == 1, "centroid inputs differ")
    return tuple(math.fsum(vector[index] for vector in vectors) / len(vectors) for index in range(len(vectors[0])))


def _select(values: tuple[float, ...], positions: tuple[int, ...]) -> tuple[float, ...]:
    _require(type(values) is tuple and len(values) == 288, "visual values differ")
    _require(len(positions) == len(set(positions)) and all(0 <= item < 288 for item in positions), "mask positions differ")
    return tuple(values[position] for position in positions)


def _pair_rows(
    vectors: dict[str, tuple[float, ...]],
    masks: tuple[dict[str, object], ...],
    family_by_content: dict[str, str],
    variant_by_content: dict[str, str],
) -> tuple[dict[str, object], ...]:
    rows = []
    mask_positions = {str(mask["mask_id"]): tuple(int(item) for item in mask["positions"]) for mask in masks}
    for left, right in combinations(sorted(vectors), 2):
        masked = {}
        for mask_id, positions in mask_positions.items():
            left_values = _select(vectors[left], positions)
            right_values = _select(vectors[right], positions)
            masked[mask_id] = {
                "mean_l1": _mean_l1(left_values, right_values),
                "exact_equal": left_values == right_values,
            }
        payload = {
            "left_content_id": left,
            "right_content_id": right,
            "left_variant_id": variant_by_content[left],
            "right_variant_id": variant_by_content[right],
            "relation": "WITHIN_FAMILY" if family_by_content[left] == family_by_content[right] else "BETWEEN_FAMILY",
            "full_288_mean_l1": _mean_l1(vectors[left], vectors[right]),
            "masks": masked,
        }
        rows.append({**payload, "pair_digest": _digest(payload)})
    return tuple(rows)


def _metric_summary(values: tuple[float, ...]) -> dict[str, object]:
    _require(bool(values), "metric inventory is empty")
    return {
        "minimum": min(values),
        "maximum": max(values),
        "mean": math.fsum(values) / len(values),
        "count_at_or_below_visual_slow_0_01": sum(value <= 0.01 for value in values),
        "count_at_or_below_fast_0_2": sum(value <= 0.2 for value in values),
        "pair_count": len(values),
    }


def _relation_summaries(rows: tuple[dict[str, object], ...], masks: tuple[dict[str, object], ...]) -> tuple[dict[str, object], ...]:
    summaries = []
    for relation in ("WITHIN_FAMILY", "BETWEEN_FAMILY"):
        selected = tuple(row for row in rows if row["relation"] == relation)
        mask_summaries = {}
        for mask in masks:
            mask_id = str(mask["mask_id"])
            metric = tuple(float(row["masks"][mask_id]["mean_l1"]) for row in selected)
            mask_payload = {
                "metric": _metric_summary(metric),
                "exact_equal_count": sum(bool(row["masks"][mask_id]["exact_equal"]) for row in selected),
            }
            mask_summaries[mask_id] = {**mask_payload, "summary_digest": _digest(mask_payload)}
        payload = {
            "relation": relation,
            "pair_count": len(selected),
            "full_288_mean_l1": _metric_summary(tuple(float(row["full_288_mean_l1"]) for row in selected)),
            "masks": mask_summaries,
        }
        summaries.append({**payload, "relation_summary_digest": _digest(payload)})
    return tuple(summaries)


def _masked_vectors(vectors: dict[str, tuple[float, ...]], positions: tuple[int, ...]) -> dict[str, tuple[float, ...]]:
    return {content_id: _select(values, positions) for content_id, values in vectors.items()}


def _leave_one_out(
    representation_id: str,
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
        "representation_id": representation_id,
        "method": "LEAVE_ONE_OUT_NEAREST_FAMILY_CENTROID",
        "correct": sum(bool(row["correct"]) for row in rows),
        "ambiguous": sum(bool(row["ambiguous"]) for row in rows),
        "total": len(rows),
        "rows": rows,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def _collision_inventory(
    vectors: dict[str, tuple[float, ...]],
    positions: tuple[int, ...],
    family_by_content: dict[str, str],
) -> dict[str, object]:
    groups: dict[str, list[str]] = {}
    for content_id, values in vectors.items():
        key = _digest(list(_select(values, positions)))
        groups.setdefault(key, []).append(content_id)
    ambiguous = []
    for values_digest, content_ids in sorted(groups.items()):
        families = sorted({family_by_content[content_id] for content_id in content_ids})
        if len(families) > 1:
            payload = {
                "masked_values_digest": values_digest,
                "content_ids": sorted(content_ids),
                "family_ids": families,
            }
            ambiguous.append({**payload, "collision_digest": _digest(payload)})
    result = {
        "unique_masked_vectors": len(groups),
        "cross_family_collision_groups": len(ambiguous),
        "sources_in_cross_family_collision_groups": sum(len(item["content_ids"]) for item in ambiguous),
        "groups": ambiguous,
    }
    return {**result, "inventory_digest": _digest(result)}


def build_comparison(workspace_root: Path) -> dict[str, object]:
    plan = _load_plan(workspace_root)
    recipes = {str(item["content_id"]): item for item in plan["generation_root"]["recipes"]}
    bindings = {str(item["content_id"]): item for item in plan["generation_root"]["source_bindings"]}
    masks = tuple(plan["mask_root"]["masks"])
    _require(tuple(str(mask["mask_id"]) for mask in masks) == ("TOP_ROW_32", "SPATIAL_SEEDED_32", "SPATIAL_SEEDED_96"), "mask inventory differs")
    _require(set(masks[1]["positions"]).issubset(masks[2]["positions"]), "distributed masks are not nested")
    family_by_content = {str(item["content_id"]): str(item["family_id"]) for item in recipes.values()}
    variant_by_content = {str(item["content_id"]): str(item["variant_id"]) for item in recipes.values()}

    receptor = LocalChannelGridReceptor(VisualGridConfig())
    vectors: dict[str, tuple[float, ...]] = {}
    state_bindings = []
    for frame_index, content_id in enumerate(sorted(recipes)):
        frame = corpus.render_frame(recipes[content_id])
        raw = frame.tobytes(order="C")
        _require(hashlib.sha256(raw).hexdigest() == bindings[content_id]["payload_sha256"], "source payload differs")
        state = receptor.analyze(frame, frame_index=frame_index)
        values = tuple(state.channel_values)
        _require(len(values) == 288, "receptor dimension differs")
        vectors[content_id] = values
        masked_digests = {
            str(mask["mask_id"]): _digest(list(_select(values, tuple(int(item) for item in mask["positions"]))))
            for mask in masks
        }
        state_payload = {
            "content_id": content_id,
            "family_id": family_by_content[content_id],
            "variant_id": variant_by_content[content_id],
            "source_payload_sha256": bindings[content_id]["payload_sha256"],
            "receptor_state_digest": state.digest(),
            "full_values_digest": _digest(list(values)),
            "masked_values_digests": masked_digests,
        }
        state_bindings.append({**state_payload, "state_binding_digest": _digest(state_payload)})
        del raw, frame, state, values

    pairs = _pair_rows(vectors, masks, family_by_content, variant_by_content)
    _require(len(pairs) == 496, "complete pair inventory differs")
    summaries = _relation_summaries(pairs, masks)
    _require(tuple(item["pair_count"] for item in summaries) == (112, 384), "pair partition differs")
    families = tuple(plan["evaluation_root"]["families"])
    evaluations = [_leave_one_out("FULL_288", vectors, families)]
    collisions = {}
    for mask in masks:
        mask_id = str(mask["mask_id"])
        positions = tuple(int(item) for item in mask["positions"])
        evaluations.append(_leave_one_out(mask_id, _masked_vectors(vectors, positions), families))
        collisions[mask_id] = _collision_inventory(vectors, positions, family_by_content)
    payload = {
        "schema": SCHEMA,
        "comparison_id": COMPARISON_ID,
        "status": "S2LW_SPATIAL_MASK_COMPARISON_EVALUATED",
        "plan_binding": {"plan_digest": EXPECTED_PLAN_DIGEST, "plan_file_sha256": EXPECTED_PLAN_SHA256},
        "source_count": len(recipes),
        "mask_bindings": [
            {
                "mask_id": mask["mask_id"],
                "mask_digest": mask["mask_digest"],
                "value_count": mask["value_count"],
                "rows_represented": mask["rows_represented"],
                "columns_represented": mask["columns_represented"],
                "channel_counts": mask["channel_counts"],
                "unique_cell_count": mask["unique_cell_count"],
            }
            for mask in masks
        ],
        "state_bindings": state_bindings,
        "complete_pair_distances": list(pairs),
        "relation_summaries": list(summaries),
        "leave_one_out_evaluations": evaluations,
        "masked_collision_inventories": collisions,
        "diagnostic_thresholds": {"visual_slow": 0.01, "fast": 0.2},
        "calls": {"visual_receptor": len(recipes), "memory": 0, "context": 0, "field": 0},
        "thresholds_selected_or_changed": False,
        "result_controls_source_or_mask_inclusion": False,
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
    _require(record.get("status") == "S2LW_SPATIAL_MASK_COMPARISON_EVALUATED", "comparison status differs")
    _require(record.get("plan_binding") == {"plan_digest": EXPECTED_PLAN_DIGEST, "plan_file_sha256": EXPECTED_PLAN_SHA256}, "plan binding differs")
    _require(record.get("source_count") == 32 and len(record.get("state_bindings", ())) == 32, "source count differs")
    _require(len(record.get("complete_pair_distances", ())) == 496, "pair count differs")
    _require(tuple(item.get("mask_id") for item in record.get("mask_bindings", ())) == ("TOP_ROW_32", "SPATIAL_SEEDED_32", "SPATIAL_SEEDED_96"), "mask binding differs")
    _require(record.get("calls") == {"visual_receptor": 32, "memory": 0, "context": 0, "field": 0}, "call boundary differs")
    _require(record.get("thresholds_selected_or_changed") is False and record.get("production_integration") is False, "scope boundary differs")
    _require(record.get("raw_payload_retained") is False, "raw payload boundary differs")
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed comparison")
    return {"verification_status": "RECORDING_COMPLETE", "comparison_file_sha256": before, "comparison_digest": record["comparison_digest"]}


__all__: tuple[str, ...] = ()
