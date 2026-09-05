"""Bound S2-MA integration comparison against the qualified S2-LZ arm."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from threading import Lock

from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from tools import _s2lv_private_pose_form_projection as full_projection
from tools import _s2ly_private_two_view_projection as masked_projection
from tools import _s2lz_private_open_set_comparison as baseline
from tools import _s2lz_private_open_set_corpus as corpus
from tools import _s2ma_private_arecent_two_view_integration as integration


SCHEMA = "s2ma.arecent-two-view-integration-comparison.v1"
COMPARISON_ID = "s2ma-arecent-two-view-integration-20260905-01"
PLAN_BINDING = baseline.PLAN_BINDING
BASELINE_BINDING = (
    "reports/s2lz/s2lz-open-set-two-view-comparison-20260905-01/comparison.json",
    "d8308a45474f177f26d877b2e9b01f0aa3f23ce02f3793d9eeefc7bd9f0563ab",
    "efad341b38051730be78d6c44b34dc1bd82dfe207a7553659fc05cf3165a7892",
)
MAX_RESULT_BYTES = 524_288
COMPARISON_ENABLED = False

_LOCK = Lock()
_USED = False


class S2MAComparisonError(RuntimeError):
    """The bounded A_RECENT integration comparison is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MAComparisonError(message)


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    data = json.dumps(value, allow_nan=False, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    return data + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _load_record(workspace_root: Path, binding: tuple[str, str, str], digest_key: str) -> dict[str, object]:
    raw = (workspace_root / binding[0]).read_bytes()
    _require(hashlib.sha256(raw).hexdigest() == binding[1], "bound artifact file changed")
    value = json.loads(raw.decode("ascii"))
    _require(type(value) is dict and raw == _canonical_bytes(value, newline=True), "bound artifact is not canonical")
    payload = dict(value)
    _require(payload.pop(digest_key, None) == _digest(payload) == binding[2], "bound artifact digest differs")
    return value


def _geometry_digest(config: VisualGridConfig, masks: dict[str, dict[str, object]]) -> str:
    return _digest(
        {
            "geometry_id": config.geometry_id,
            "source_width": config.source_width,
            "source_height": config.source_height,
            "grid_columns": config.grid_columns,
            "grid_rows": config.grid_rows,
            "mask_digests": {mask_id: masks[mask_id]["mask_digest"] for mask_id in sorted(masks)},
        }
    )


def build_comparison(workspace_root: Path) -> dict[str, object]:
    plan = _load_record(workspace_root, PLAN_BINDING, "plan_digest")
    prior = _load_record(workspace_root, BASELINE_BINDING, "comparison_digest")
    recipes = {str(item["source_id"]): item for item in plan["generation_root"]["recipes"]}
    bindings = {str(item["source_id"]): item for item in plan["generation_root"]["source_bindings"]}
    masks = {str(item["mask_id"]): item for item in plan["mask_root"]["masks"]}
    groups = tuple(plan["execution_root"]["reference_groups"])
    cases = tuple(plan["execution_root"]["cases"])
    observations = tuple(plan["execution_root"]["observations"])
    prior_rows = {str(item["case_id"]): item for item in prior["decisions"]["UNION_192_OPEN_SET"]}
    _require(len(cases) == len(prior_rows) == 20 and len(observations) == 40, "case inventory differs")

    config = VisualGridConfig()
    receptor = LocalChannelGridReceptor(config)
    representations = {representation_id: {} for representation_id in baseline.REPRESENTATION_IDS}
    receptor_bindings = []

    def analyze(source_id: str, frame_index: int, observation_digest: str | None) -> tuple[float, ...]:
        frame = corpus.render_frame(recipes[source_id])
        raw = frame.tobytes(order="C")
        _require(hashlib.sha256(raw).hexdigest() == bindings[source_id]["payload_sha256"], "source payload differs")
        state = receptor.analyze(frame, frame_index=frame_index)
        values = tuple(state.channel_values)
        payload = {
            "source_id": source_id,
            "source_payload_sha256": bindings[source_id]["payload_sha256"],
            "observation_digest": observation_digest,
            "receptor_state_digest": state.digest(),
            "visual_values_digest": _digest(list(values)),
        }
        receptor_bindings.append({**payload, "binding_digest": _digest(payload)})
        del frame, raw, state
        return values

    reference_ids = tuple(str(source_id) for group in groups for source_id in group["reference_source_ids"])
    for frame_index, source_id in enumerate(reference_ids):
        values = analyze(source_id, frame_index, None)
        for mask_id, representation_id in (("VIEW_A_96", "VIEW_A_FORM_96"), ("VIEW_B_96", "VIEW_B_FORM_96"), ("UNION_192", "UNION_FORM_192")):
            mask = masks[mask_id]
            view = masked_projection.bind_observed_view(values, mask_id, tuple(mask["positions"]), str(mask["mask_digest"]))
            representations[representation_id][source_id] = masked_projection.project_mask_conditioned_form(view).values
        representations["FULL_FORM_UPPER_BOUND"][source_id] = full_projection.project_pose_form(values).form_descriptor.values
    _, runtime_envelopes = baseline._build_envelopes(representations, groups)
    union_models = runtime_envelopes["UNION_FORM_192"]
    geometry_digest = _geometry_digest(config, masks)
    integrator = integration.ARecentTransientTwoViewIntegrator(
        geometry_digest=geometry_digest,
        view_a_mask_digest=str(masks["VIEW_A_96"]["mask_digest"]),
        view_b_mask_digest=str(masks["VIEW_B_96"]["mask_digest"]),
        union_mask_digest=str(masks["UNION_192"]["mask_digest"]),
        union_positions=tuple(masks["UNION_192"]["positions"]),
        model_envelopes=union_models,
    )
    observation_by_case_mask = {(str(item["case_id"]), str(item["mask_id"])): item for item in observations}
    case_results = []
    next_frame_index = len(reference_ids)
    for case in cases:
        case_id = str(case["case_id"])
        looks = []
        for mask_id in ("VIEW_A_96", "VIEW_B_96"):
            observation = observation_by_case_mask[(case_id, mask_id)]
            source_id = str(observation["source_id"])
            values = analyze(source_id, next_frame_index, str(observation["observation_digest"]))
            next_frame_index += 1
            mask = masks[mask_id]
            view = masked_projection.bind_observed_view(values, mask_id, tuple(mask["positions"]), str(mask["mask_digest"]))
            looks.append(
                integration.ARecentObservedLookV1(
                    owner_id=f"s2ma-owner-{case_id}-{mask_id.lower().replace('_', '-')}",
                    case_plan_digest=str(case["case_plan_digest"]),
                    source_observation_digest=str(observation["observation_digest"]),
                    source_id=source_id,
                    payload_sha256=str(observation["payload_sha256"]),
                    geometry_digest=geometry_digest,
                    tick=int(observation["tick"]),
                    mask_id=mask_id,
                    mask_digest=str(mask["mask_digest"]),
                    observed_positions=view.observed_positions,
                    observed_values=view.observed_values,
                    observed_values_digest=view.observed_values_digest,
                    source_values_digest=view.source_values_digest,
                    field_contact_digest=None,
                )
            )
        pending = integrator.process(looks[0])
        final = integrator.process(looks[1])
        prior_row = prior_rows[case_id]
        exact = (
            final.status == prior_row["status"]
            and final.selected_model_id == prior_row["selected_model_id"]
            and final.reason == prior_row["reason"]
            and final.open_set_decision_digest == prior_row["source_decision_digest"]
        )
        payload = {
            "case_id": case_id,
            "pending_result_digest": pending.digest(),
            "final_result": final.canonical_payload(),
            "final_result_digest": final.digest(),
            "baseline_decision_digest": prior_row["decision_digest"],
            "baseline_source_decision_digest": prior_row["source_decision_digest"],
            "exact_baseline_match": exact,
            "window_empty_after_case": integrator.pending_count == 0,
        }
        case_results.append({**payload, "case_result_digest": _digest(payload)})
    _require(all(item["exact_baseline_match"] and item["window_empty_after_case"] for item in case_results), "S2-LZ baseline reproduction differs")
    payload = {
        "schema": SCHEMA,
        "comparison_id": COMPARISON_ID,
        "status": "S2MA_TRANSIENT_A_RECENT_INTEGRATION_CONFIRMED",
        "presealed_plan_file_sha256": PLAN_BINDING[1],
        "presealed_plan_digest": PLAN_BINDING[2],
        "baseline_file_sha256": BASELINE_BINDING[1],
        "baseline_comparison_digest": BASELINE_BINDING[2],
        "geometry_digest": geometry_digest,
        "case_count": 20,
        "look_count": 40,
        "receptor_bindings": receptor_bindings,
        "case_results": case_results,
        "window_empty_at_end": integrator.pending_count == 0,
        "retained_for_b_stable": False,
        "field_contacts_created_or_reverted": 0,
        "calls": {"visual_receptor": 56, "a_recent_transient_integration": 40, "memory_core": 0, "context": 0, "field": 0},
        "new_threshold_or_selection_rule": False,
        "raw_payload_retained": False,
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
    _require(len(raw) <= MAX_RESULT_BYTES, "comparison exceeds bounded envelope")
    record = json.loads(raw.decode("ascii"))
    _require(raw == _canonical_bytes(record, newline=True), "comparison is not canonical")
    payload = dict(record)
    _require(payload.pop("comparison_digest", None) == _digest(payload), "comparison digest differs")
    _require(record.get("status") == "S2MA_TRANSIENT_A_RECENT_INTEGRATION_CONFIRMED", "status differs")
    _require(record.get("case_count") == 20 and record.get("look_count") == 40 and len(record.get("case_results", ())) == 20, "case inventory differs")
    _require(all(item["exact_baseline_match"] and item["window_empty_after_case"] for item in record["case_results"]), "baseline equivalence differs")
    _require(record.get("window_empty_at_end") is True and record.get("retained_for_b_stable") is False, "retention boundary differs")
    _require(record.get("field_contacts_created_or_reverted") == 0, "field independence differs")
    _require(record.get("calls") == {"visual_receptor": 56, "a_recent_transient_integration": 40, "memory_core": 0, "context": 0, "field": 0}, "call boundary differs")
    _require(record.get("new_threshold_or_selection_rule") is False and record.get("raw_payload_retained") is False, "scope boundary differs")
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed comparison")
    return {"verification_status": "RECORDING_COMPLETE", "comparison_file_sha256": before, "comparison_digest": record["comparison_digest"]}


__all__: tuple[str, ...] = ()
