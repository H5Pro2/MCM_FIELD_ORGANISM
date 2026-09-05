"""One bounded role-free S2-MC learning-lifecycle run."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
from threading import Lock

import numpy as np

from mcm_field_organism.audio_video_field_geometry import ORTHOGONAL_FIELD_SAMPLE_OFFSETS
from mcm_field_organism.receptor_contract import ReceptorContactFrame
from mcm_field_organism.shared_mcm_field import build_shared_mcm_field
from tools import _s2mb_private_bstable_two_view as bstable
from tools import _s2mb_private_bstable_two_view_runner as s2mb
from tools import _s2mc_private_learning_lifecycle as lifecycle
from tools import _s2jw_profiled_memory_coordinator as coordinator


SCHEMA = "s2mc.role-free-learning-lifecycle-run.v1"
RUN_ID = "s2mc-role-free-learning-lifecycle-20260905-02"
RUN_ENABLED = False
MAX_RESULT_BYTES = 262_144
EVENT_SPECS = (
    ("e01", "PARTIAL_VISUAL_CUE", "source-005", "VIEW_A_96"),
    ("e02", "PARTIAL_VISUAL_CUE", "source-005", "VIEW_B_96"),
    ("e03", "COMPLETE_AV_PERCEPTION", "source-001", None),
    ("e04", "COMPLETE_AV_PERCEPTION", "source-001", None),
    ("e05", "COMPLETE_AV_PERCEPTION", "source-001", None),
    ("e06", "COMPLETE_AV_PERCEPTION", "source-001", None),
    ("e07", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e08", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e09", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e10", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e11", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e12", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e13", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e14", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e15", "COMPLETE_AV_PERCEPTION", "source-033", None),
    ("e16", "PARTIAL_VISUAL_CUE", "source-005", "VIEW_A_96"),
    ("e17", "PARTIAL_VISUAL_CUE", "source-005", "VIEW_B_96"),
    ("e18", "PARTIAL_VISUAL_CUE", "source-025", "VIEW_A_96"),
    ("e19", "PARTIAL_VISUAL_CUE", "source-025", "VIEW_B_96"),
    ("e20", "PARTIAL_VISUAL_CUE", "source-005", "VIEW_A_96"),
    ("e21", "PARTIAL_VISUAL_CUE", "source-011", "VIEW_B_96"),
)
_LOCK = Lock()
_USED = False


class S2MCRunnerError(RuntimeError):
    """The bounded S2-MC run is invalid or already consumed."""


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


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2MCRunnerError(message)


def _initial_pre_contact_field_state(
    config: coordinator.S2JVCoordinatorConfigV1,
) -> object:
    profile = config.profile.profile
    reference_frames = tuple(
        ReceptorContactFrame(
            modality_id=bank.modality_id,
            geometry_id=bank.geometry_id,
            snapshot_id=f"s2mc-pre-contact-{bank.modality_id}",
            clock_id=s2mb.field_runtime.FIELD_CLOCK_ID,
            window_start_tick=0,
            window_end_tick=1,
            carrier_ids=bank.carrier_ids,
            values=tuple(0.0 for _ in bank.carrier_ids),
        )
        for bank in (profile.auditory_config, profile.visual_config)
    )
    field = build_shared_mcm_field(
        reference_frames,
        s2mb.field_runtime.field_path.s2jt_default_dock_anatomies(),
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    state = s2mb.field_runtime._field_state(field, 0, 0)
    _require(
        state.phase == "PRE_CONTACT"
        and state.step_count == 0
        and state.last_end_tick == 0
        and state.field.last_distribution is None,
        "PRE_CONTACT initialization differs",
    )
    return state


def _formation(
    sources: s2mb._SourceStream,
    source_id: str,
) -> tuple[object, object, tuple[float, ...]]:
    ordinal = sources.next_ordinal
    material_source_id = "pressure-d1" if source_id == "source-033" else source_id
    audio_role = "D_FAR" if source_id == "source-033" else "L"
    window, auditory_state = sources._audio_state(audio_role)
    image, visual_payload_digest, visual_values_digest = sources._visual_source(
        material_source_id
    )
    _require(
        hashlib.sha256(image.tobytes(order="C")).hexdigest() == visual_payload_digest,
        "visual payload differs",
    )
    visual_state = sources.visual.analyze(image, frame_index=(ordinal - 1) * 3 + 2)
    _require(
        _digest(list(visual_state.channel_values)) == visual_values_digest,
        "visual receptor values differ",
    )
    end = ordinal * 100_000_000
    auditory = s2mb.OrganismTimedReceptorFrame(
        s2mb.from_auditory_receptor_state(auditory_state),
        s2mb.CommonFieldTime(s2mb.field_runtime.FIELD_CLOCK_ID, end - 10_000_000, end),
    )
    visual = s2mb.OrganismTimedReceptorFrame(
        s2mb.from_visual_receptor_state(visual_state),
        s2mb.CommonFieldTime(
            s2mb.field_runtime.FIELD_CLOCK_ID,
            (((ordinal - 1) * 3 + 2) * 1_000_000_000) // 30,
            end,
        ),
    )
    audio_digest = hashlib.sha256(np.asarray(window, dtype="<f4").tobytes()).hexdigest()
    plan = s2mb.build_s2jv_pairing_plan(
        pair_id=f"s2mc-pair-{ordinal:03d}",
        source_contract_id="s2mc-source-contract",
        profile=sources.config.profile,
        auditory=auditory,
        visual=visual,
        auditory_payload_digest=audio_digest,
        visual_payload_digest=visual_payload_digest,
    )
    pair = s2mb.bind_s2jv_default_live_pair(
        pairing_plan=plan,
        profile=sources.config.profile,
        auditory=auditory,
        visual=visual,
    )
    field_input = s2mb.field_runtime.S2LOFieldInputV1(
        pair.pairing_digest,
        (ordinal - 1) * 100_000_000,
        end,
        (auditory, visual),
    )
    sources.next_ordinal += 1
    values = tuple(visual_state.channel_values)
    del image, window
    return pair, field_input, values


def _candidate_bindings(
    *,
    state: coordinator.S2JVCompositeStateV1,
    training_values: dict[str, tuple[float, ...]],
    prior: dict[str, object],
) -> tuple[bstable.BStableCalibrationBindingV1, ...]:
    occupied = tuple(
        slot
        for slot in state.tspm_state.visual_ppb1_state.slots
        if slot.occupied
    )
    _require(len(occupied) == 2, "visual stable inventory differs")
    rows = {
        str(item["model_id"]): item
        for item in prior["calibration_envelopes"]["representations"]["UNION_FORM_192"]  # type: ignore[index]
    }
    source_001_prototype = s2mb._repeat_prototype(training_values["source-001"], 2)
    source_033_prototype = s2mb._repeat_prototype(training_values["source-033"], 7)
    target_row = rows["model-01"]
    source_033_payload = {
        "schema": "s2mc.identical-source-calibration.v1",
        "source_values_digest": _digest(list(training_values["source-033"])),
        "reference_count": 4,
        "calibration_rule": "MAX_REFERENCE_TO_REFERENCE_CENTROID_MEAN_L1",
        "calibration_radius": 0.0,
        "test_sources_available": False,
    }
    return (
        bstable.BStableCalibrationBindingV1(
            occupied[0].slot_id,
            "model-01",
            float(target_row["calibration_radius"]),
            str(target_row["envelope_digest"]),
            _digest(list(source_001_prototype)),
        ),
        bstable.BStableCalibrationBindingV1(
            occupied[1].slot_id,
            "source-033-calibration",
            0.0,
            _digest(source_033_payload),
            _digest(list(source_033_prototype)),
        ),
    )


def _pair_plan(cases: dict[str, dict[str, object]], segment_id: str) -> dict[str, object]:
    return {
        "s01": cases["case-001"],
        "s02": cases["case-001"],
        "s03": cases["case-009"],
        "s04": cases["case-017"],
    }[segment_id]


def _evaluate_pair(
    *,
    segment_id: str,
    looks: tuple[object, object],
    candidates: bstable.BStableVisualCandidateSetV1 | None,
    masks: dict[str, dict[str, object]],
    geometry_digest: str,
    memory_digest: str,
) -> dict[str, object]:
    first, second = looks
    product = lifecycle.decide_lifecycle_context(
        first=first,
        second=second,
        candidates=candidates,
        geometry_digest=geometry_digest,
        view_a_mask_digest=str(masks["VIEW_A_96"]["mask_digest"]),
        view_b_mask_digest=str(masks["VIEW_B_96"]["mask_digest"]),
        union_mask_digest=str(masks["UNION_192"]["mask_digest"]),
        union_positions=tuple(masks["UNION_192"]["positions"]),
        memory_prestate_digest=memory_digest,
        memory_poststate_digest=memory_digest,
    )
    direct = lifecycle.direct_lifecycle_baseline(
        first=first,
        second=second,
        candidates=candidates,
        geometry_digest=geometry_digest,
        view_a_mask_digest=str(masks["VIEW_A_96"]["mask_digest"]),
        view_b_mask_digest=str(masks["VIEW_B_96"]["mask_digest"]),
        union_mask_digest=str(masks["UNION_192"]["mask_digest"]),
        union_positions=tuple(masks["UNION_192"]["positions"]),
        memory_prestate_digest=memory_digest,
        memory_poststate_digest=memory_digest,
    )
    _require(product.decision_digest == direct.decision_digest, "direct baseline differs")
    payload = {
        "segment_id": segment_id,
        "current_only": {
            "status": "UNCHANGED_NO_CONTEXT_HYPOTHESIS",
            "observed_value_count": 192,
        },
        "context": product.canonical_payload(),
        "direct_baseline": direct.canonical_payload(),
        "memory_prestate_digest": memory_digest,
        "memory_poststate_digest": memory_digest,
    }
    return {**payload, "segment_result_digest": _digest(payload)}


def _evaluate_execution(
    records: tuple[dict[str, object], ...],
    target_slot_id: str,
) -> dict[str, object]:
    by_id = {str(item["segment_id"]): item for item in records}
    expectations = {
        "s01": ("ABSTAINED", None, "ABSENT_VALID"),
        "s02": ("ADMITTED", target_slot_id, "VALID_CANDIDATES"),
        "s03": ("ABSTAINED", None, "VALID_CANDIDATES"),
        "s04": ("ABSTAINED", None, "PAIR_INVALID"),
    }
    rows = []
    for segment_id, expected in expectations.items():
        actual = by_id[segment_id]["context"]
        observed = (
            actual["status"],
            actual["selected_slot_id"],
            actual["evidence_status"],
        )
        row = {
            "segment_id": segment_id,
            "expected_status": expected[0],
            "expected_slot_id": expected[1],
            "expected_evidence_status": expected[2],
            "observed_status": observed[0],
            "observed_slot_id": observed[1],
            "observed_evidence_status": observed[2],
            "matches": observed == expected,
        }
        rows.append({**row, "evaluation_row_digest": _digest(row)})
    payload = {
        "schema": "s2mc.evaluation.v1",
        "rows": rows,
        "all_match": all(item["matches"] for item in rows),
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def build_run(workspace_root: Path) -> dict[str, object]:
    _require(
        isinstance(workspace_root, Path) and workspace_root.is_absolute(),
        "absolute workspace Path required",
    )
    plan = s2mb._load_record(workspace_root, s2mb.PLAN_BINDING, "plan_digest")
    prior = s2mb._load_record(
        workspace_root,
        s2mb.S2LZ_RESULT_BINDING,
        "comparison_digest",
    )
    masks = {
        str(item["mask_id"]): item
        for item in plan["mask_root"]["masks"]  # type: ignore[index]
    }
    cases = {
        str(item["case_id"]): item
        for item in plan["execution_root"]["cases"]  # type: ignore[index]
    }
    config = s2mb._build_config()
    sources = s2mb._SourceStream(config=config, plan=plan, prior=prior)
    memory_state = coordinator.initial_s2jv_composite_state(config)
    field_adapter = s2mb.field_runtime.build_s2lo_field_adapter()
    field_state = None
    event_records: list[dict[str, object]] = []
    segment_records: list[dict[str, object]] = []
    pending_looks: list[object] = []
    training_values: dict[str, tuple[float, ...]] = {}
    candidates = None
    geometry_digest = s2mb._geometry_digest(s2mb.VisualGridConfig(), masks)
    segment_by_event = {
        1: "s01",
        2: "s01",
        16: "s02",
        17: "s02",
        18: "s03",
        19: "s03",
        20: "s04",
        21: "s04",
    }
    segment_closures = {2: "s01", 17: "s02", 19: "s03", 21: "s04"}

    for ordinal, (event_id, event_type, source_id, mask_id) in enumerate(
        EVENT_SPECS,
        start=1,
    ):
        memory_before = memory_state.state_digest
        if event_type == "COMPLETE_AV_PERCEPTION":
            pair, field_input, visual_values = _formation(sources, source_id)
            training_values.setdefault(source_id, visual_values)
            operation_payload = pair
            perception_digest = pair.pairing_digest
        else:
            segment_id = segment_by_event[ordinal]
            pair_plan = _pair_plan(cases, segment_id)
            provisional, field_input = sources.visual_look(
                source_id=source_id,
                case_plan_digest=str(pair_plan["case_plan_digest"]),
                mask=masks[str(mask_id)],
                geometry_digest=geometry_digest,
                look_tick=ordinal,
                field_contact_digest=None,
            )
            operation_payload = provisional
            perception_digest = field_input.perception_digest

        field_event = s2mb._field_event(
            ordinal=ordinal,
            event_type=event_type,
            source_digest=_digest({"event_id": event_id, "source_id": source_id}),
            perception_digest=perception_digest,
            field_input=field_input,
            operation_payload=operation_payload,
        )
        if field_state is None:
            field_state = _initial_pre_contact_field_state(config)
        field_result = field_adapter(field_state, field_event)
        field_state = field_result.poststate

        memory_receipt_digest = None
        if event_type == "COMPLETE_AV_PERCEPTION":
            bound = coordinator.bind_s2jv_coordinator_input(config=config, source=pair)
            owner = coordinator.S2JVFormationOwner(
                f"s2mc-owner-{ordinal:03d}",
                f"s2mc-auth-{ordinal:03d}",
                f"s2mc-consume-{ordinal:03d}",
                config.config_digest,
                memory_state.state_digest,
                bound.input_digest,
            )
            formed = coordinator.advance_s2jv_atomic(
                config=config,
                prestate=memory_state,
                source=bound,
                owner=owner,
            )
            memory_state = formed.poststate
            memory_receipt_digest = formed.receipt.receipt_digest
        else:
            look = replace(provisional, field_contact_digest=field_result.receipt_digest)
            pending_looks.append(look)

        memory_after = memory_state.state_digest
        if event_type == "PARTIAL_VISUAL_CUE":
            _require(memory_before == memory_after, "partial cue changed memory")
        event_payload = {
            "event_id": event_id,
            "ordinal": ordinal,
            "event_type": event_type,
            "source_digest": _digest({"source_id": source_id}),
            "field_receipt_digest": field_result.receipt_digest,
            "memory_receipt_digest": memory_receipt_digest,
            "memory_prestate_digest": memory_before,
            "memory_poststate_digest": memory_after,
        }
        event_records.append({**event_payload, "event_result_digest": _digest(event_payload)})

        if ordinal in segment_closures:
            segment_id = segment_closures[ordinal]
            _require(len(pending_looks) == 2, "two-view window anatomy differs")
            pair_candidates = None if segment_id == "s01" else candidates
            segment_records.append(
                _evaluate_pair(
                    segment_id=segment_id,
                    looks=(pending_looks[0], pending_looks[1]),
                    candidates=pair_candidates,
                    masks=masks,
                    geometry_digest=geometry_digest,
                    memory_digest=memory_state.state_digest,
                )
            )
            pending_looks.clear()

        if ordinal == 15:
            occupied_b4 = tuple(item for item in memory_state.b4_state.entries if item.occupied)
            occupied_fast = tuple(
                item
                for item in memory_state.tspm_state.fast_state.slots
                if item.occupied
            )
            _require(
                len(occupied_b4) == 9
                and all(
                    item.formation_index is not None and item.formation_index >= 5
                    for item in occupied_b4
                )
                and len(occupied_fast) == 1,
                "A_RECENT displacement differs",
            )
            bindings = _candidate_bindings(
                state=memory_state,
                training_values=training_values,
                prior=prior,
            )
            candidates = bstable.bind_visual_bstable_candidates(
                config=config,
                state=memory_state,
                bindings=bindings,
                union_mask_digest=str(masks["UNION_192"]["mask_digest"]),
                union_positions=tuple(masks["UNION_192"]["positions"]),
            )
            _require(
                len(candidates.candidates) == 2
                and all(item.support == 3 for item in candidates.candidates),
                "stable candidate closure differs",
            )

    _require(
        field_state is not None
        and field_state.step_count == 21
        and memory_state.generation == 13
        and candidates is not None
        and not pending_looks,
        "execution closure differs",
    )
    target_slot_id = candidates.candidates[0].slot_id
    evaluation = _evaluate_execution(tuple(segment_records), target_slot_id)
    _require(evaluation["all_match"] is True, "functional lifecycle differs")
    payload = {
        "schema": SCHEMA,
        "run_id": RUN_ID,
        "status": "S2MC_ROLE_FREE_LEARNING_LIFECYCLE_CONFIRMED",
        "execution_root": {
            "event_count": 21,
            "formation_count": 13,
            "partial_look_count": 8,
            "field_step_count": 21,
            "event_records": event_records,
            "segment_records": segment_records,
            "candidate_set_digest": candidates.candidate_set_digest,
            "candidate_count": 2,
            "final_memory_digest": memory_state.state_digest,
            "final_field_digest": field_state.state_digest,
        },
        "evaluation_root": evaluation,
        "raw_payload_retained": False,
        "new_mask_descriptor_threshold_or_memory_rule": False,
        "calls": {
            "visual_receptor": 21,
            "audio_windows": 13,
            "audio_hops": 130,
            "memory_formations": 13,
            "field_steps": 21,
            "two_view_closures": 4,
            "context_decisions": 4,
            "direct_baseline_decisions": 4,
            "current_only_results": 4,
        },
    }
    return {**payload, "result_digest": _digest(payload)}


def write_run_once(workspace_root: Path, output_root: Path, *, run_id: str) -> Path:
    global RUN_ENABLED, _USED
    _require(RUN_ENABLED is True and run_id == RUN_ID, "run is not authorized")
    _require(not _USED and _LOCK.acquire(blocking=False), "run is already consumed")
    _USED = True
    try:
        record = build_run(workspace_root)
        run_dir = output_root / run_id
        run_dir.mkdir(parents=True, exist_ok=False)
        target = run_dir / "result.json"
        temporary = run_dir / ".result.json.tmp"
        data = _canonical_bytes(record, newline=True)
        _require(len(data) <= MAX_RESULT_BYTES, "result exceeds bounded envelope")
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
        RUN_ENABLED = False
        _LOCK.release()


def verify_result_file(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    before = hashlib.sha256(raw).hexdigest()
    _require(len(raw) <= MAX_RESULT_BYTES, "result exceeds bounded envelope")
    value = json.loads(raw.decode("ascii"))
    _require(raw == _canonical_bytes(value, newline=True), "result is not canonical")
    payload = dict(value)
    _require(payload.pop("result_digest", None) == _digest(payload), "result digest differs")
    execution = value.get("execution_root", {})
    evaluation = value.get("evaluation_root", {})
    _require(
        value.get("status") == "S2MC_ROLE_FREE_LEARNING_LIFECYCLE_CONFIRMED"
        and execution.get("event_count") == 21
        and execution.get("formation_count") == 13
        and execution.get("partial_look_count") == 8
        and execution.get("field_step_count") == 21
        and len(execution.get("event_records", ())) == 21
        and len(execution.get("segment_records", ())) == 4,
        "execution inventory differs",
    )
    _require(
        evaluation.get("all_match") is True
        and len(evaluation.get("rows", ())) == 4
        and all(item["matches"] for item in evaluation["rows"])
        and all(
            item["context"]["decision_digest"]
            == item["direct_baseline"]["decision_digest"]
            and item["memory_prestate_digest"] == item["memory_poststate_digest"]
            for item in execution["segment_records"]
        ),
        "evaluation or read-only closure differs",
    )
    _require(
        value.get("raw_payload_retained") is False
        and value.get("new_mask_descriptor_threshold_or_memory_rule") is False,
        "scope boundary differs",
    )
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed result")
    return {
        "verification_status": "RECORDING_COMPLETE",
        "result_file_sha256": before,
        "result_digest": value["result_digest"],
    }


__all__: tuple[str, ...] = ()
