"""Prospective read-only two-view consensus comparison for S2-LY."""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
from threading import Lock

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lv_private_pose_form_projection as full_projection
from tools import _s2ly_private_two_view_corpus as corpus
from tools import _s2ly_private_two_view_projection as masked_projection


SCHEMA = "s2ly.two-view-consensus-comparison.v1"
COMPARISON_ID = "s2ly-two-view-consensus-comparison-20260905-01"
PLAN_BINDING = (
    "reports/s2ly/s2ly-two-view-corpus-20260905-01/presealed-plan.json",
    "9c8d3e5f9aba866481e638a3354bb741d73b40c178d2342d0387a6f965c34348",
    "e499e87daf5e1d23a0a154e04e11935830dd5eb02ea37b05a79fb601dd5f8a9d",
)
ARM_IDS = (
    "VIEW_A_MASKED_FORM_96",
    "VIEW_B_MASKED_FORM_96",
    "TWO_VIEW_CONSENSUS",
    "UNION_MASKED_FORM_192",
    "FULL_288",
    "FULL_FORM_UPPER_BOUND",
)
MAX_RESULT_BYTES = 1_048_576
COMPARISON_ENABLED = False

_LOCK = Lock()
_USED = False


class S2LYComparisonError(RuntimeError):
    """The presealed two-view comparison cannot be evaluated exactly."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2LYComparisonError(message)


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


def _nearest_unique(cue: tuple[float, ...], candidates: dict[str, tuple[float, ...]]) -> dict[str, object]:
    _require(type(candidates) is dict and len(candidates) == 4, "candidate inventory differs")
    distances = tuple(
        {"candidate_id": candidate_id, "mean_l1": _mean_l1(cue, candidates[candidate_id])}
        for candidate_id in sorted(candidates)
    )
    minimum = min(float(item["mean_l1"]) for item in distances)
    tied = tuple(str(item["candidate_id"]) for item in distances if item["mean_l1"] == minimum)
    payload = {
        "status": "UNIQUE" if len(tied) == 1 else "AMBIGUOUS",
        "selected_candidate_id": tied[0] if len(tied) == 1 else None,
        "minimum_tie_count": len(tied),
        "distances": list(distances),
    }
    return {**payload, "decision_digest": _digest(payload)}


def _consensus(first: dict[str, object], second: dict[str, object]) -> dict[str, object]:
    first_id = first["selected_candidate_id"] if first["status"] == "UNIQUE" else None
    second_id = second["selected_candidate_id"] if second["status"] == "UNIQUE" else None
    admitted = first_id is not None and first_id == second_id
    if admitted:
        reason = "SAME_UNIQUE_CANDIDATE"
    elif first_id is None or second_id is None:
        reason = "AT_LEAST_ONE_VIEW_AMBIGUOUS"
    else:
        reason = "UNIQUE_VIEWS_DISAGREE"
    payload = {
        "status": "ADMITTED" if admitted else "ABSTAINED",
        "selected_candidate_id": first_id if admitted else None,
        "reason": reason,
        "view_a_decision_digest": first["decision_digest"],
        "view_b_decision_digest": second["decision_digest"],
    }
    return {**payload, "decision_digest": _digest(payload)}


def _evaluate_arm(arm_id: str, decisions: tuple[dict[str, object], ...], expected_candidate_by_cue: dict[str, str]) -> dict[str, object]:
    rows = []
    for decision in decisions:
        cue_id = str(decision["cue_id"])
        selected = decision["selected_candidate_id"]
        expected = expected_candidate_by_cue[cue_id]
        admitted = selected is not None
        row = {
            "cue_id": cue_id,
            "expected_candidate_id": expected,
            "selected_candidate_id": selected,
            "correct_admission": admitted and selected == expected,
            "false_admission": admitted and selected != expected,
            "abstained": not admitted,
            "decision_digest": decision["decision_digest"],
        }
        rows.append({**row, "evaluation_row_digest": _digest(row)})
    correct = sum(bool(row["correct_admission"]) for row in rows)
    false = sum(bool(row["false_admission"]) for row in rows)
    abstained = sum(bool(row["abstained"]) for row in rows)
    admitted = correct + false
    payload = {
        "arm_id": arm_id,
        "correct_admissions": correct,
        "false_admissions": false,
        "abstentions": abstained,
        "total": len(rows),
        "correct_coverage": correct / len(rows),
        "admission_precision": (correct / admitted) if admitted else None,
        "rows": rows,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def build_comparison(workspace_root: Path) -> dict[str, object]:
    plan = _load_plan(workspace_root)
    recipes = {str(item["content_id"]): item for item in plan["generation_root"]["recipes"]}
    bindings = {str(item["content_id"]): item for item in plan["generation_root"]["source_bindings"]}
    masks = {str(item["mask_id"]): item for item in plan["mask_root"]["masks"]}
    candidate_ids = tuple(str(item) for item in plan["execution_root"]["candidate_ids"])
    cue_ids = tuple(str(item) for item in plan["execution_root"]["cue_ids"])
    observations = tuple(plan["execution_root"]["observations"])
    _require(len(recipes) == 32 and len(candidate_ids) == 4 and len(cue_ids) == 28 and len(observations) == 56, "plan inventory differs")
    _require(set(masks) == {"VIEW_A_96", "VIEW_B_96", "UNION_192"}, "mask inventory differs")

    receptor = LocalChannelGridReceptor(VisualGridConfig())
    representations: dict[str, dict[str, tuple[float, ...]]] = {
        "VIEW_A_MASKED_FORM_96": {},
        "VIEW_B_MASKED_FORM_96": {},
        "UNION_MASKED_FORM_192": {},
        "FULL_288": {},
        "FULL_FORM_UPPER_BOUND": {},
    }
    state_bindings = []

    def analyze_source(content_id: str, frame_index: int, observation: dict[str, object] | None) -> tuple[float, ...]:
        frame = corpus.render_frame(recipes[content_id])
        raw = frame.tobytes(order="C")
        _require(hashlib.sha256(raw).hexdigest() == bindings[content_id]["payload_sha256"], "source payload differs")
        state = receptor.analyze(frame, frame_index=frame_index)
        values = tuple(state.channel_values)
        _require(len(values) == 288, "receptor dimension differs")
        state_payload = {
            "content_id": content_id,
            "source_payload_sha256": bindings[content_id]["payload_sha256"],
            "receptor_state_digest": state.digest(),
            "visual_values_digest": _digest(list(values)),
            "observation_digest": observation["observation_digest"] if observation is not None else None,
            "observation_tick": observation["tick"] if observation is not None else None,
            "mask_id": observation["mask_id"] if observation is not None else None,
        }
        state_bindings.append({**state_payload, "state_binding_digest": _digest(state_payload)})
        del raw, frame, state
        return values

    for frame_index, content_id in enumerate(candidate_ids):
        values = analyze_source(content_id, frame_index, None)
        full = full_projection.project_pose_form(values)
        for mask_id, arm_id in (
            ("VIEW_A_96", "VIEW_A_MASKED_FORM_96"),
            ("VIEW_B_96", "VIEW_B_MASKED_FORM_96"),
            ("UNION_192", "UNION_MASKED_FORM_192"),
        ):
            mask = masks[mask_id]
            view = masked_projection.bind_observed_view(values, mask_id, tuple(mask["positions"]), str(mask["mask_digest"]))
            projected = masked_projection.project_mask_conditioned_form(view)
            representations[arm_id][content_id] = projected.values
        representations["FULL_288"][content_id] = values
        representations["FULL_FORM_UPPER_BOUND"][content_id] = full.form_descriptor.values
        del values, full, view, projected

    observation_by_content_mask = {(str(item["content_id"]), str(item["mask_id"])): item for item in observations}
    next_frame_index = len(candidate_ids)
    for cue_id in cue_ids:
        a_observation = observation_by_content_mask[(cue_id, "VIEW_A_96")]
        b_observation = observation_by_content_mask[(cue_id, "VIEW_B_96")]
        _require(int(a_observation["tick"]) < int(b_observation["tick"]), "two-view temporal order differs")
        values_a = analyze_source(cue_id, next_frame_index, a_observation)
        values_b = analyze_source(cue_id, next_frame_index + 1, b_observation)
        next_frame_index += 2
        _require(values_a == values_b and _digest(list(values_a)) == _digest(list(values_b)), "repeated cue receptor values differ")
        mask_a = masks["VIEW_A_96"]
        mask_b = masks["VIEW_B_96"]
        union_mask = masks["UNION_192"]
        view_a = masked_projection.bind_observed_view(values_a, "VIEW_A_96", tuple(mask_a["positions"]), str(mask_a["mask_digest"]))
        view_b = masked_projection.bind_observed_view(values_b, "VIEW_B_96", tuple(mask_b["positions"]), str(mask_b["mask_digest"]))
        union_values = view_a.observed_values + view_b.observed_values
        union_view = masked_projection.ObservedVisualViewV1(
            mask_id="UNION_192",
            mask_digest=str(union_mask["mask_digest"]),
            source_values_digest=view_a.source_values_digest,
            observed_positions=tuple(union_mask["positions"]),
            observed_values=union_values,
            observed_values_digest=masked_projection._digest(list(union_values)),
        )
        _require(tuple(union_mask["positions"]) == view_a.observed_positions + view_b.observed_positions, "union position order differs")
        representations["VIEW_A_MASKED_FORM_96"][cue_id] = masked_projection.project_mask_conditioned_form(view_a).values
        representations["VIEW_B_MASKED_FORM_96"][cue_id] = masked_projection.project_mask_conditioned_form(view_b).values
        representations["UNION_MASKED_FORM_192"][cue_id] = masked_projection.project_mask_conditioned_form(union_view).values
        representations["FULL_288"][cue_id] = values_b
        representations["FULL_FORM_UPPER_BOUND"][cue_id] = full_projection.project_pose_form(values_b).form_descriptor.values
        del values_a, values_b, view_a, view_b, union_view, union_values

    candidate_vectors = {
        arm_id: {candidate_id: representations[arm_id][candidate_id] for candidate_id in candidate_ids}
        for arm_id in representations
    }
    decisions: dict[str, list[dict[str, object]]] = {arm_id: [] for arm_id in ARM_IDS}
    for cue_id in cue_ids:
        view_a = _nearest_unique(representations["VIEW_A_MASKED_FORM_96"][cue_id], candidate_vectors["VIEW_A_MASKED_FORM_96"])
        view_b = _nearest_unique(representations["VIEW_B_MASKED_FORM_96"][cue_id], candidate_vectors["VIEW_B_MASKED_FORM_96"])
        a_observation = observation_by_content_mask[(cue_id, "VIEW_A_96")]
        b_observation = observation_by_content_mask[(cue_id, "VIEW_B_96")]
        for arm_id, decision in (
            ("VIEW_A_MASKED_FORM_96", view_a),
            ("VIEW_B_MASKED_FORM_96", view_b),
            ("TWO_VIEW_CONSENSUS", _consensus(view_a, view_b)),
            ("UNION_MASKED_FORM_192", _nearest_unique(representations["UNION_MASKED_FORM_192"][cue_id], candidate_vectors["UNION_MASKED_FORM_192"])),
            ("FULL_288", _nearest_unique(representations["FULL_288"][cue_id], candidate_vectors["FULL_288"])),
            ("FULL_FORM_UPPER_BOUND", _nearest_unique(representations["FULL_FORM_UPPER_BOUND"][cue_id], candidate_vectors["FULL_FORM_UPPER_BOUND"])),
        ):
            row = {
                "cue_id": cue_id,
                "arm_id": arm_id,
                "selected_candidate_id": decision["selected_candidate_id"],
                "status": decision["status"],
                "reason": decision.get("reason"),
                "source_decision_digest": decision["decision_digest"],
                "view_a_observation_digest": a_observation["observation_digest"],
                "view_b_observation_digest": b_observation["observation_digest"],
            }
            decisions[arm_id].append({**row, "decision_digest": _digest(row)})

    expected_candidate_by_cue = {}
    for family in plan["evaluation_root"]["families"]:
        for content_id in family["content_ids"]:
            if content_id in cue_ids:
                expected_candidate_by_cue[str(content_id)] = str(family["candidate_id"])
    _require(len(expected_candidate_by_cue) == 28, "evaluation role inventory differs")
    evaluations = tuple(_evaluate_arm(arm_id, tuple(decisions[arm_id]), expected_candidate_by_cue) for arm_id in ARM_IDS)
    payload = {
        "schema": SCHEMA,
        "comparison_id": COMPARISON_ID,
        "status": "S2LY_TWO_VIEW_COMPARISON_EVALUATED",
        "presealed_plan_file_sha256": PLAN_BINDING[1],
        "presealed_plan_digest": PLAN_BINDING[2],
        "mask_bindings": {mask_id: masks[mask_id]["mask_digest"] for mask_id in sorted(masks)},
        "source_count": 32,
        "candidate_count": 4,
        "cue_count": 28,
        "observation_count": 56,
        "state_bindings": state_bindings,
        "decisions": {arm_id: decisions[arm_id] for arm_id in ARM_IDS},
        "evaluations": list(evaluations),
        "rules": {
            "per_view": "UNIQUE_MINIMUM_EXACT_CANDIDATE_NO_THRESHOLD",
            "two_view": "ADMIT_ONLY_SAME_UNIQUE_CANDIDATE_ID",
            "union": "SAME_MASK_CONDITIONED_FORM_OVER_DISJOINT_192_VALUE_UNION",
            "full_form": "S2LV_FULL_FORM_DESCRIPTOR_UPPER_BOUND",
            "hidden_values": "NOT_PRESENT_NOT_IMPUTED",
        },
        "calls": {"visual_receptor": 60, "memory": 0, "context": 0, "field": 0},
        "thresholds_selected_or_changed": False,
        "training_or_parameter_search": False,
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
    _require(record.get("status") == "S2LY_TWO_VIEW_COMPARISON_EVALUATED", "comparison status differs")
    _require(record.get("presealed_plan_file_sha256") == PLAN_BINDING[1] and record.get("presealed_plan_digest") == PLAN_BINDING[2], "plan binding differs")
    _require(record.get("source_count") == 32 and record.get("candidate_count") == 4 and record.get("cue_count") == 28, "source inventory differs")
    _require(record.get("observation_count") == 56 and len(record.get("state_bindings", ())) == 60, "observation inventory differs")
    _require(set(record.get("decisions", {})) == set(ARM_IDS) and all(len(rows) == 28 for rows in record["decisions"].values()), "decision inventory differs")
    _require(tuple(item["arm_id"] for item in record.get("evaluations", ())) == ARM_IDS, "evaluation inventory differs")
    _require(record.get("calls") == {"visual_receptor": 60, "memory": 0, "context": 0, "field": 0}, "call boundary differs")
    _require(record.get("thresholds_selected_or_changed") is False and record.get("training_or_parameter_search") is False, "method boundary differs")
    _require(record.get("raw_payload_retained") is False and record.get("production_integration") is False, "scope boundary differs")
    for cue_index in range(28):
        a = record["decisions"]["VIEW_A_MASKED_FORM_96"][cue_index]
        b = record["decisions"]["VIEW_B_MASKED_FORM_96"][cue_index]
        consensus = record["decisions"]["TWO_VIEW_CONSENSUS"][cue_index]
        expected = a["selected_candidate_id"] if a["status"] == "UNIQUE" and a["selected_candidate_id"] == b["selected_candidate_id"] and b["status"] == "UNIQUE" else None
        _require(consensus["selected_candidate_id"] == expected, "consensus decision differs")
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed comparison")
    return {"verification_status": "RECORDING_COMPLETE", "comparison_file_sha256": before, "comparison_digest": record["comparison_digest"]}


__all__: tuple[str, ...] = ()
