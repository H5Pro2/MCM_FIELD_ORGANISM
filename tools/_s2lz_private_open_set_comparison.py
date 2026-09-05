"""Read-only prospective open-set comparison over two temporal visual views."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from threading import Lock

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lv_private_pose_form_projection as full_projection
from tools import _s2ly_private_two_view_projection as masked_projection
from tools import _s2lz_private_open_set_corpus as corpus


SCHEMA = "s2lz.open-set-two-view-comparison.v1"
COMPARISON_ID = "s2lz-open-set-two-view-comparison-20260905-01"
PLAN_BINDING = (
    "reports/s2lz/s2lz-open-set-corpus-20260905-01/presealed-plan.json",
    "69fec956b6e68bcde41367308fd9a4d785969fdbf1b62ef3eed5641de20b6fe7",
    "ae5bbba16138673e429817f32d9cb1f6bd695f58590ef23740ec5e3e3391d06c",
)
REPRESENTATION_IDS = (
    "VIEW_A_FORM_96",
    "VIEW_B_FORM_96",
    "UNION_FORM_192",
    "FULL_FORM_UPPER_BOUND",
)
ARM_IDS = (
    "VIEW_A_OPEN_SET",
    "VIEW_B_OPEN_SET",
    "TWO_VIEW_CONSENSUS_OPEN_SET",
    "UNION_192_OPEN_SET",
    "FULL_FORM_OPEN_SET_UPPER_BOUND",
)
MAX_RESULT_BYTES = 1_048_576
COMPARISON_ENABLED = False

_LOCK = Lock()
_USED = False


class S2LZComparisonError(RuntimeError):
    """The presealed open-set comparison cannot be evaluated exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LZComparisonError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_plan(workspace_root: Path) -> dict[str, object]:
    path = workspace_root / PLAN_BINDING[0]
    raw = path.read_bytes()
    _require(hashlib.sha256(raw).hexdigest() == PLAN_BINDING[1], "presealed plan file changed")
    value = json.loads(raw.decode("ascii"))
    _require(type(value) is dict and raw == _canonical_bytes(value, newline=True), "presealed plan is not canonical")
    payload = dict(value)
    _require(payload.pop("plan_digest", None) == _digest(payload) == PLAN_BINDING[2], "presealed plan digest differs")
    return value


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    _require(type(left) is tuple and type(right) is tuple and len(left) == len(right) and len(left) > 0, "distance dimensions differ")
    return math.fsum(abs(a - b) for a, b in zip(left, right, strict=True)) / len(left)


def _centroid(vectors: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    _require(len(vectors) == 4 and len({len(item) for item in vectors}) == 1, "reference vectors differ")
    return tuple(math.fsum(vector[index] for vector in vectors) / len(vectors) for index in range(len(vectors[0])))


def _build_envelopes(
    representations: dict[str, dict[str, tuple[float, ...]]],
    reference_groups: tuple[dict[str, object], ...],
) -> tuple[dict[str, object], dict[str, dict[str, tuple[float, ...] | float]]]:
    records: dict[str, object] = {}
    runtime: dict[str, dict[str, tuple[float, ...] | float]] = {}
    for representation_id in REPRESENTATION_IDS:
        records[representation_id] = []
        runtime[representation_id] = {}
        for group in reference_groups:
            model_id = str(group["model_id"])
            source_ids = tuple(str(item) for item in group["reference_source_ids"])
            vectors = tuple(representations[representation_id][source_id] for source_id in source_ids)
            centroid = _centroid(vectors)
            distances = tuple(_mean_l1(vector, centroid) for vector in vectors)
            radius = max(distances)
            runtime[representation_id][model_id] = (centroid, radius)
            payload = {
                "model_id": model_id,
                "reference_source_ids": list(source_ids),
                "reference_value_digests": [_digest(list(vector)) for vector in vectors],
                "centroid_digest": _digest(list(centroid)),
                "calibration_radius": radius,
                "reference_distances": list(distances),
                "rule": "MAX_REFERENCE_TO_REFERENCE_CENTROID_MEAN_L1",
            }
            records[representation_id].append({**payload, "envelope_digest": _digest(payload)})
    payload = {"representations": records, "test_sources_available": False}
    return {**payload, "envelope_set_digest": _digest(payload)}, runtime


def _open_set_decision(values: tuple[float, ...], models: dict[str, tuple[float, ...] | float]) -> dict[str, object]:
    rows = []
    eligible = []
    for model_id in sorted(models):
        centroid, radius = models[model_id]
        _require(type(centroid) is tuple and type(radius) is float and radius >= 0.0, "model envelope differs")
        distance = _mean_l1(values, centroid)
        accepted = distance <= radius
        rows.append({"model_id": model_id, "mean_l1": distance, "calibration_radius": radius, "within_envelope": accepted})
        if accepted:
            eligible.append(model_id)
    if len(eligible) == 1:
        status, selected, reason = "ADMITTED", eligible[0], "EXACTLY_ONE_MODEL_WITHIN_ENVELOPE"
    elif not eligible:
        status, selected, reason = "ABSTAINED", None, "NO_MODEL_WITHIN_ENVELOPE"
    else:
        status, selected, reason = "ABSTAINED", None, "MULTIPLE_MODELS_WITHIN_ENVELOPE"
    payload = {"status": status, "selected_model_id": selected, "reason": reason, "eligible_model_ids": eligible, "distances": rows}
    return {**payload, "decision_digest": _digest(payload)}


def _pair_compatibility(case: dict[str, object], first: dict[str, object], second: dict[str, object]) -> dict[str, object]:
    same_source = first["source_id"] == second["source_id"] == case["view_a_source_id"] == case["view_b_source_id"]
    same_payload = first["payload_sha256"] == second["payload_sha256"]
    tick_gap = int(second["tick"]) - int(first["tick"])
    compatible = same_source and same_payload and 0 < tick_gap <= int(case["maximum_tick_gap"])
    payload = {
        "case_plan_digest": case["case_plan_digest"],
        "view_a_observation_digest": first["observation_digest"],
        "view_b_observation_digest": second["observation_digest"],
        "same_source_id": same_source,
        "same_payload_digest": same_payload,
        "tick_gap": tick_gap,
        "maximum_tick_gap": case["maximum_tick_gap"],
        "compatible": compatible,
    }
    return {**payload, "pair_compatibility_digest": _digest(payload)}


def _pair_abstention(reason: str, parent_digest: str) -> dict[str, object]:
    payload = {"status": "ABSTAINED", "selected_model_id": None, "reason": reason, "parent_digest": parent_digest}
    return {**payload, "decision_digest": _digest(payload)}


def _consensus(first: dict[str, object], second: dict[str, object], compatibility: dict[str, object]) -> dict[str, object]:
    if not compatibility["compatible"]:
        return _pair_abstention("PAIR_INCOMPATIBLE", str(compatibility["pair_compatibility_digest"]))
    first_id = first["selected_model_id"] if first["status"] == "ADMITTED" else None
    second_id = second["selected_model_id"] if second["status"] == "ADMITTED" else None
    if first_id is not None and first_id == second_id:
        payload = {
            "status": "ADMITTED",
            "selected_model_id": first_id,
            "reason": "SAME_ADMITTED_MODEL",
            "view_a_decision_digest": first["decision_digest"],
            "view_b_decision_digest": second["decision_digest"],
            "pair_compatibility_digest": compatibility["pair_compatibility_digest"],
        }
        return {**payload, "decision_digest": _digest(payload)}
    reason = "AT_LEAST_ONE_VIEW_ABSTAINED" if first_id is None or second_id is None else "ADMITTED_MODELS_DISAGREE"
    payload = {
        "status": "ABSTAINED",
        "selected_model_id": None,
        "reason": reason,
        "view_a_decision_digest": first["decision_digest"],
        "view_b_decision_digest": second["decision_digest"],
        "pair_compatibility_digest": compatibility["pair_compatibility_digest"],
    }
    return {**payload, "decision_digest": _digest(payload)}


def _evaluate(
    arm_id: str,
    decisions: tuple[dict[str, object], ...],
    evaluation_by_case: dict[str, dict[str, object]],
) -> dict[str, object]:
    single_view = arm_id in {"VIEW_A_OPEN_SET", "VIEW_B_OPEN_SET"}
    rows = []
    for decision in decisions:
        evaluation = evaluation_by_case[str(decision["case_id"])]
        if single_view and evaluation["expected_kind"] == "INCOMPATIBLE_PAIR":
            continue
        expected = evaluation["expected_model_id"]
        selected = decision["selected_model_id"]
        known = evaluation["expected_kind"] == "KNOWN_HOLDOUT"
        correct_known_hit = known and selected == expected
        known_wrong_admission = known and selected is not None and selected != expected
        known_abstention = known and selected is None
        correct_open_set_abstention = not known and selected is None
        open_set_false_admission = not known and selected is not None
        row = {
            "case_id": decision["case_id"],
            "expected_kind": evaluation["expected_kind"],
            "expected_model_id": expected,
            "selected_model_id": selected,
            "correct_known_hit": correct_known_hit,
            "known_wrong_admission": known_wrong_admission,
            "known_abstention": known_abstention,
            "correct_open_set_abstention": correct_open_set_abstention,
            "open_set_false_admission": open_set_false_admission,
            "decision_digest": decision["decision_digest"],
        }
        rows.append({**row, "evaluation_row_digest": _digest(row)})
    category_counts = {}
    for category in ("KNOWN_HOLDOUT", "UNKNOWN_FORM", "AMBIGUOUS_INTERMEDIATE", "INCOMPATIBLE_PAIR"):
        selected_rows = tuple(row for row in rows if row["expected_kind"] == category)
        category_counts[category] = {
            "total": len(selected_rows),
            "admitted": sum(row["selected_model_id"] is not None for row in selected_rows),
            "abstained": sum(row["selected_model_id"] is None for row in selected_rows),
        }
    payload = {
        "arm_id": arm_id,
        "known_hits": sum(bool(row["correct_known_hit"]) for row in rows),
        "known_wrong_admissions": sum(bool(row["known_wrong_admission"]) for row in rows),
        "known_abstentions": sum(bool(row["known_abstention"]) for row in rows),
        "open_set_correct_abstentions": sum(bool(row["correct_open_set_abstention"]) for row in rows),
        "open_set_false_admissions": sum(bool(row["open_set_false_admission"]) for row in rows),
        "category_counts": category_counts,
        "evaluated_case_count": len(rows),
        "rows": rows,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def build_comparison(workspace_root: Path) -> dict[str, object]:
    plan = _load_plan(workspace_root)
    recipes = {str(item["source_id"]): item for item in plan["generation_root"]["recipes"]}
    bindings = {str(item["source_id"]): item for item in plan["generation_root"]["source_bindings"]}
    masks = {str(item["mask_id"]): item for item in plan["mask_root"]["masks"]}
    groups = tuple(plan["execution_root"]["reference_groups"])
    cases = tuple(plan["execution_root"]["cases"])
    observations = tuple(plan["execution_root"]["observations"])
    _require(len(recipes) == 32 and len(groups) == 4 and len(cases) == 20 and len(observations) == 40, "plan inventory differs")

    receptor = LocalChannelGridReceptor(VisualGridConfig())
    representations = {representation_id: {} for representation_id in REPRESENTATION_IDS}
    state_bindings = []

    def analyze(source_id: str, frame_index: int, observation: dict[str, object] | None) -> tuple[float, ...]:
        frame = corpus.render_frame(recipes[source_id])
        raw = frame.tobytes(order="C")
        _require(hashlib.sha256(raw).hexdigest() == bindings[source_id]["payload_sha256"], "source payload differs")
        state = receptor.analyze(frame, frame_index=frame_index)
        values = tuple(state.channel_values)
        payload = {
            "source_id": source_id,
            "source_payload_sha256": bindings[source_id]["payload_sha256"],
            "receptor_state_digest": state.digest(),
            "visual_values_digest": _digest(list(values)),
            "observation_digest": observation["observation_digest"] if observation is not None else None,
        }
        state_bindings.append({**payload, "state_binding_digest": _digest(payload)})
        del frame, raw, state
        return values

    reference_source_ids = tuple(str(source_id) for group in groups for source_id in group["reference_source_ids"])
    for frame_index, source_id in enumerate(reference_source_ids):
        values = analyze(source_id, frame_index, None)
        for mask_id, representation_id in (("VIEW_A_96", "VIEW_A_FORM_96"), ("VIEW_B_96", "VIEW_B_FORM_96"), ("UNION_192", "UNION_FORM_192")):
            mask = masks[mask_id]
            view = masked_projection.bind_observed_view(values, mask_id, tuple(mask["positions"]), str(mask["mask_digest"]))
            representations[representation_id][source_id] = masked_projection.project_mask_conditioned_form(view).values
        representations["FULL_FORM_UPPER_BOUND"][source_id] = full_projection.project_pose_form(values).form_descriptor.values
    envelope_record, runtime_envelopes = _build_envelopes(representations, groups)

    observation_by_case_mask = {(str(item["case_id"]), str(item["mask_id"])): item for item in observations}
    decisions = {arm_id: [] for arm_id in ARM_IDS}
    pair_bindings = []
    next_frame_index = len(reference_source_ids)
    for case in cases:
        case_id = str(case["case_id"])
        first_observation = observation_by_case_mask[(case_id, "VIEW_A_96")]
        second_observation = observation_by_case_mask[(case_id, "VIEW_B_96")]
        values_a = analyze(str(first_observation["source_id"]), next_frame_index, first_observation)
        values_b = analyze(str(second_observation["source_id"]), next_frame_index + 1, second_observation)
        next_frame_index += 2
        mask_a, mask_b, union_mask = masks["VIEW_A_96"], masks["VIEW_B_96"], masks["UNION_192"]
        view_a = masked_projection.bind_observed_view(values_a, "VIEW_A_96", tuple(mask_a["positions"]), str(mask_a["mask_digest"]))
        view_b = masked_projection.bind_observed_view(values_b, "VIEW_B_96", tuple(mask_b["positions"]), str(mask_b["mask_digest"]))
        form_a = masked_projection.project_mask_conditioned_form(view_a).values
        form_b = masked_projection.project_mask_conditioned_form(view_b).values
        decision_a = _open_set_decision(form_a, runtime_envelopes["VIEW_A_FORM_96"])
        decision_b = _open_set_decision(form_b, runtime_envelopes["VIEW_B_FORM_96"])
        compatibility = _pair_compatibility(case, first_observation, second_observation)
        pair_bindings.append({"case_id": case_id, **compatibility})
        consensus = _consensus(decision_a, decision_b, compatibility)
        if compatibility["compatible"]:
            _require(view_a.source_values_digest == view_b.source_values_digest, "compatible pair source values differ")
            union_values = view_a.observed_values + view_b.observed_values
            union_view = masked_projection.ObservedVisualViewV1(
                mask_id="UNION_192",
                mask_digest=str(union_mask["mask_digest"]),
                source_values_digest=view_a.source_values_digest,
                observed_positions=tuple(union_mask["positions"]),
                observed_values=union_values,
                observed_values_digest=masked_projection._digest(list(union_values)),
            )
            union_form = masked_projection.project_mask_conditioned_form(union_view).values
            union_decision = _open_set_decision(union_form, runtime_envelopes["UNION_FORM_192"])
            full_form = full_projection.project_pose_form(values_b).form_descriptor.values
            full_decision = _open_set_decision(full_form, runtime_envelopes["FULL_FORM_UPPER_BOUND"])
        else:
            union_decision = _pair_abstention("PAIR_INCOMPATIBLE_NO_UNION", str(compatibility["pair_compatibility_digest"]))
            full_decision = _pair_abstention("PAIR_INCOMPATIBLE_NO_FULL_FORM", str(compatibility["pair_compatibility_digest"]))
        for arm_id, decision in (
            ("VIEW_A_OPEN_SET", decision_a),
            ("VIEW_B_OPEN_SET", decision_b),
            ("TWO_VIEW_CONSENSUS_OPEN_SET", consensus),
            ("UNION_192_OPEN_SET", union_decision),
            ("FULL_FORM_OPEN_SET_UPPER_BOUND", full_decision),
        ):
            payload = {
                "case_id": case_id,
                "arm_id": arm_id,
                "status": decision["status"],
                "selected_model_id": decision["selected_model_id"],
                "reason": decision["reason"],
                "source_decision_digest": decision["decision_digest"],
                "pair_compatibility_digest": compatibility["pair_compatibility_digest"],
            }
            decisions[arm_id].append({**payload, "decision_digest": _digest(payload)})
        del values_a, values_b, view_a, view_b, form_a, form_b

    evaluation_by_case = {str(item["case_id"]): item for item in plan["evaluation_root"]["cases"]}
    evaluations = tuple(_evaluate(arm_id, tuple(decisions[arm_id]), evaluation_by_case) for arm_id in ARM_IDS)
    payload = {
        "schema": SCHEMA,
        "comparison_id": COMPARISON_ID,
        "status": "S2LZ_OPEN_SET_COMPARISON_EVALUATED",
        "presealed_plan_file_sha256": PLAN_BINDING[1],
        "presealed_plan_digest": PLAN_BINDING[2],
        "source_count": 32,
        "reference_source_count": 16,
        "case_count": 20,
        "observation_count": 40,
        "state_bindings": state_bindings,
        "calibration_envelopes": envelope_record,
        "pair_bindings": pair_bindings,
        "decisions": decisions,
        "evaluations": list(evaluations),
        "rules": {
            "calibration": "REFERENCE_ONLY_MAX_DISTANCE_TO_REFERENCE_CENTROID",
            "admission": "EXACTLY_ONE_MODEL_WITHIN_ITS_PRETEST_CALIBRATION_RADIUS",
            "union": "SAME_SOURCE_AND_PAYLOAD_WITHIN_ONE_TICK_DISJOINT_OBSERVED_VALUES_ONLY",
            "missing_values": "NOT_PRESENT_NOT_IMPUTED",
        },
        "calls": {"visual_receptor": 56, "memory": 0, "context": 0, "field": 0},
        "post_test_threshold_selection": False,
        "test_source_used_for_calibration": False,
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
    _require(record.get("status") == "S2LZ_OPEN_SET_COMPARISON_EVALUATED", "comparison status differs")
    _require(record.get("presealed_plan_file_sha256") == PLAN_BINDING[1] and record.get("presealed_plan_digest") == PLAN_BINDING[2], "plan binding differs")
    _require(record.get("source_count") == 32 and record.get("reference_source_count") == 16 and record.get("case_count") == 20, "inventory differs")
    _require(record.get("observation_count") == 40 and len(record.get("state_bindings", ())) == 56, "state inventory differs")
    _require(set(record.get("decisions", {})) == set(ARM_IDS) and all(len(rows) == 20 for rows in record["decisions"].values()), "decision inventory differs")
    _require(tuple(item["arm_id"] for item in record.get("evaluations", ())) == ARM_IDS, "evaluation inventory differs")
    _require(record.get("calls") == {"visual_receptor": 56, "memory": 0, "context": 0, "field": 0}, "call boundary differs")
    _require(record.get("post_test_threshold_selection") is False and record.get("test_source_used_for_calibration") is False, "open-set boundary differs")
    _require(record.get("raw_payload_retained") is False and record.get("production_integration") is False, "scope boundary differs")
    incompatible = {item["case_id"] for item in record["pair_bindings"] if not item["compatible"]}
    _require(len(incompatible) == 4, "incompatible pair inventory differs")
    for arm_id in ("TWO_VIEW_CONSENSUS_OPEN_SET", "UNION_192_OPEN_SET", "FULL_FORM_OPEN_SET_UPPER_BOUND"):
        _require(all(item["selected_model_id"] is None for item in record["decisions"][arm_id] if item["case_id"] in incompatible), "incompatible pair was admitted")
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed comparison")
    return {"verification_status": "RECORDING_COMPLETE", "comparison_file_sha256": before, "comparison_digest": record["comparison_digest"]}


__all__: tuple[str, ...] = ()
