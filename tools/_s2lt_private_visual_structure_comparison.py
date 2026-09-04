"""Private read-only comparison of visual structure representations."""

from __future__ import annotations

from itertools import combinations, product
import hashlib
import json
import math
import os
from pathlib import Path
from threading import Lock

import numpy as np

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lt_private_visual_structure_corpus as corpus


SCHEMA = "s2lt.visual-structure-comparison.v1"
COMPARISON_ID = "s2lt-visual-structure-comparison-20260904-01"
PLAN_RELATIVE_PATH = "reports/s2lt/s2lt-visual-structure-corpus-20260904-01/presealed-plan.json"
EXPECTED_PLAN_SHA256 = "828a9fe5ec6b5077a4437eef3fc4b2d7f5d244caa638f4a9a8cde5cb4de026c3"
EXPECTED_PLAN_DIGEST = "c72853f8bcf08441f438acb885129f1a5beb1d15dd487ba78ddac216ccb24176"
MAX_RESULT_BYTES = 262_144
COMPARISON_ENABLED = False

_LOCK = Lock()
_USED = False


class S2LTComparisonError(RuntimeError):
    """The sealed visual comparison cannot be evaluated exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LTComparisonError(message)


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


def _subblock_means(frame: np.ndarray) -> tuple[float, ...]:
    _require(frame.shape == (1080, 1920, 3) and frame.dtype == np.uint8, "subblock input differs")
    means = frame.reshape(24, 45, 24, 80, 3).mean(axis=(1, 3), dtype=np.float64)
    return tuple(float(value) / 255.0 for value in means.reshape(-1))


def _local_gradients(frame: np.ndarray) -> tuple[float, ...]:
    _require(frame.shape == (1080, 1920, 3) and frame.dtype == np.uint8, "gradient input differs")
    blocks = frame.reshape(8, 135, 12, 160, 3).transpose(0, 2, 1, 3, 4).astype(np.int16)
    horizontal = np.abs(np.diff(blocks, axis=3)).mean(axis=(2, 3), dtype=np.float64) / 255.0
    vertical = np.abs(np.diff(blocks, axis=2)).mean(axis=(2, 3), dtype=np.float64) / 255.0
    values = np.stack((horizontal, vertical), axis=-1).reshape(-1)
    return tuple(float(value) for value in values)


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    _require(len(left) == len(right) and len(left) > 0, "distance dimensions differ")
    return math.fsum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


def _centroid(vectors: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    _require(bool(vectors) and len({len(item) for item in vectors}) == 1, "centroid inputs differ")
    return tuple(math.fsum(item[index] for item in vectors) / len(vectors) for index in range(len(vectors[0])))


def _pair_rows(
    vectors: dict[str, tuple[float, ...]],
    pairs: tuple[tuple[str, str], ...],
) -> list[dict[str, object]]:
    return [
        {
            "left_content_id": left,
            "right_content_id": right,
            "normalized_mean_l1": _mean_l1(vectors[left], vectors[right]),
        }
        for left, right in pairs
    ]


def _representation_evaluation(
    representation_id: str,
    vectors: dict[str, tuple[float, ...]],
    families: tuple[dict[str, object], ...],
) -> dict[str, object]:
    training = tuple(tuple(str(item) for item in family["training_content_ids"]) for family in families)
    holdouts = tuple(tuple(str(item) for item in family["holdout_content_ids"]) for family in families)
    within_pairs = tuple(pair for members in training for pair in combinations(members, 2))
    cross_pairs = tuple(product(training[0], training[1]))
    within = _pair_rows(vectors, within_pairs)
    cross = _pair_rows(vectors, cross_pairs)
    maximum_within = max(item["normalized_mean_l1"] for item in within)
    minimum_cross = min(item["normalized_mean_l1"] for item in cross)
    centroids = tuple(_centroid(tuple(vectors[item] for item in members)) for members in training)
    holdout_rows = []
    for family_index, members in enumerate(holdouts):
        for content_id in members:
            distances = tuple(_mean_l1(vectors[content_id], centroid) for centroid in centroids)
            predicted = min(range(len(distances)), key=lambda index: (distances[index], families[index]["family_id"]))
            row = {
                "content_id": content_id,
                "expected_family_id": families[family_index]["family_id"],
                "centroid_distances": [
                    {"family_id": families[index]["family_id"], "normalized_mean_l1": distance}
                    for index, distance in enumerate(distances)
                ],
                "predicted_family_id": families[predicted]["family_id"],
                "correct": predicted == family_index,
            }
            holdout_rows.append({**row, "classification_digest": _digest(row)})
    criteria = {
        "minimum_cross_exceeds_maximum_within": minimum_cross > maximum_within,
        "all_holdouts_nearest_own_centroid": all(item["correct"] for item in holdout_rows),
    }
    payload = {
        "representation_id": representation_id,
        "dimension": len(next(iter(vectors.values()))),
        "within_training_pairs": within,
        "cross_training_pairs": cross,
        "maximum_within_training_distance": maximum_within,
        "minimum_cross_training_distance": minimum_cross,
        "separation_margin": minimum_cross - maximum_within,
        "holdout_classifications": holdout_rows,
        "criteria": criteria,
        "meets_presealed_criteria": all(criteria.values()),
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def build_comparison(workspace_root: Path) -> dict[str, object]:
    plan = _load_plan(workspace_root)
    recipes = {str(item["content_id"]): item for item in plan["generation_root"]["recipes"]}
    bindings = {str(item["content_id"]): item for item in plan["generation_root"]["source_bindings"]}
    receptor = LocalChannelGridReceptor(VisualGridConfig())
    vectors: dict[str, dict[str, tuple[float, ...]]] = {
        "BLOCK_MEAN_12X8_RGB": {},
        "SUBBLOCK_MEAN_24X24_RGB": {},
        "LOCAL_GRADIENT_12X8_RGB_XY": {},
    }
    state_bindings = []
    common_histogram_digest = None
    for frame_index, content_id in enumerate(sorted(recipes)):
        frame = corpus.render_frame(recipes[content_id])
        raw = frame.tobytes(order="C")
        binding = bindings[content_id]
        _require(hashlib.sha256(raw).hexdigest() == binding["payload_sha256"], "source payload differs")
        _require(len(raw) == binding["payload_bytes"], "source size differs")
        histogram_digest = binding["histogram_digest"]
        common_histogram_digest = histogram_digest if common_histogram_digest is None else common_histogram_digest
        _require(histogram_digest == common_histogram_digest, "source brightness distribution differs")
        baseline_state = receptor.analyze(frame, frame_index=frame_index)
        frame_vectors = {
            "BLOCK_MEAN_12X8_RGB": tuple(baseline_state.channel_values),
            "SUBBLOCK_MEAN_24X24_RGB": _subblock_means(frame),
            "LOCAL_GRADIENT_12X8_RGB_XY": _local_gradients(frame),
        }
        for representation_id, values in frame_vectors.items():
            _require(all(math.isfinite(value) and 0.0 <= value <= 1.0 for value in values), "representation value differs")
            vectors[representation_id][content_id] = values
        state_payload = {
            "content_id": content_id,
            "source_payload_sha256": binding["payload_sha256"],
            "baseline_receptor_state_digest": baseline_state.digest(),
            "representation_value_digests": {
                representation_id: _digest(list(values))
                for representation_id, values in frame_vectors.items()
            },
        }
        state_bindings.append({**state_payload, "state_binding_digest": _digest(state_payload)})
        del raw, frame, frame_vectors, baseline_state
    families = tuple(plan["evaluation_root"]["families"])
    evaluations = [
        _representation_evaluation(representation_id, representation_vectors, families)
        for representation_id, representation_vectors in vectors.items()
    ]
    payload = {
        "schema": SCHEMA,
        "comparison_id": COMPARISON_ID,
        "status": "S2LT_VISUAL_STRUCTURE_COMPARISON_EVALUATED",
        "plan_binding": {
            "plan_digest": EXPECTED_PLAN_DIGEST,
            "plan_file_sha256": EXPECTED_PLAN_SHA256,
        },
        "source_count": len(recipes),
        "common_histogram_digest": common_histogram_digest,
        "state_bindings": state_bindings,
        "representation_evaluations": evaluations,
        "calls": {"baseline_visual_receptor": len(recipes), "memory": 0, "context": 0, "field": 0},
        "thresholds_used_for_selection": False,
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
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    raw = path.read_bytes()
    _require(len(raw) <= MAX_RESULT_BYTES, "comparison file exceeds bounded envelope")
    record = json.loads(raw.decode("ascii"))
    _require(raw == _canonical_bytes(record, newline=True), "comparison file is not canonical")
    payload = dict(record)
    _require(payload.pop("comparison_digest", None) == _digest(payload), "comparison digest differs")
    _require(record.get("status") == "S2LT_VISUAL_STRUCTURE_COMPARISON_EVALUATED", "comparison status differs")
    _require(record.get("plan_binding") == {"plan_digest": EXPECTED_PLAN_DIGEST, "plan_file_sha256": EXPECTED_PLAN_SHA256}, "plan binding differs")
    _require(record.get("source_count") == 12 and len(record.get("state_bindings", ())) == 12, "source count differs")
    _require(len(record.get("representation_evaluations", ())) == 3, "representation count differs")
    _require(record.get("calls") == {"baseline_visual_receptor": 12, "memory": 0, "context": 0, "field": 0}, "call boundary differs")
    _require(record.get("raw_payload_retained") is False and record.get("production_integration") is False, "scope boundary differs")
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed comparison")
    return {
        "verification_status": "RECORDING_COMPLETE",
        "comparison_file_sha256": before,
        "comparison_digest": record["comparison_digest"],
    }


__all__: tuple[str, ...] = ()
