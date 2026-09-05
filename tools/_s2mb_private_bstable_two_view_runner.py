"""One bounded S2-MB run over real B_STABLE visual slots."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
from threading import Lock

import numpy as np

from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.receptor_contract import (
    CommonFieldTime,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2jx_default_live_memory_fixtures as pressure_fixtures
from tools import _s2ld_auditory_partial_cue_fixtures as audio_fixtures
from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2lo_private_role_free_stream_runner as field_runtime
from tools import _s2lz_private_open_set_comparison as open_set
from tools import _s2lz_private_open_set_corpus as corpus
from tools import _s2ly_private_two_view_projection as projection
from tools import _s2ma_private_arecent_two_view_integration as integration
from tools import _s2mb_private_bstable_two_view as bstable
from tools import _s2jw_profiled_memory_coordinator as coordinator
from tools._s2jw_default_live_av_pairing import (
    bind_s2jv_default_live_pair,
    build_s2jv_pairing_plan,
)
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits


SCHEMA = "s2mb.bstable-two-view-context-run.v1"
RUN_ID = "s2mb-bstable-two-view-context-20260905-01"
RUN_ENABLED = False
FORMATION_SOURCES = (
    ("source-001",) * 4
    + ("source-007",) * 4
    + ("source-013",) * 4
    + ("pressure-d1",) * 9
)
MAX_RESULT_BYTES = 524_288
PLAN_BINDING = open_set.PLAN_BINDING
S2LZ_RESULT_BINDING = (
    "reports/s2lz/s2lz-open-set-two-view-comparison-20260905-01/comparison.json",
    "d8308a45474f177f26d877b2e9b01f0aa3f23ce02f3793d9eeefc7bd9f0563ab",
    "efad341b38051730be78d6c44b34dc1bd82dfe207a7553659fc05cf3165a7892",
)
_LOCK = Lock()
_USED = False


class S2MBRunnerError(RuntimeError):
    """The bounded S2-MB run is invalid or already consumed."""


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
        raise S2MBRunnerError(message)


def _load_record(
    workspace_root: Path,
    binding: tuple[str, str, str],
    digest_key: str,
) -> dict[str, object]:
    raw = (workspace_root / binding[0]).read_bytes()
    _require(hashlib.sha256(raw).hexdigest() == binding[1], "bound file changed")
    value = json.loads(raw.decode("ascii"))
    _require(type(value) is dict and raw == _canonical_bytes(value, newline=True), "bound file is not canonical")
    payload = dict(value)
    _require(payload.pop(digest_key, None) == _digest(payload) == binding[2], "bound digest differs")
    return value


def _geometry_digest(config: VisualGridConfig, masks: dict[str, dict[str, object]]) -> str:
    return _digest(
        {
            "geometry_id": config.geometry_id,
            "source_width": config.source_width,
            "source_height": config.source_height,
            "grid_columns": config.grid_columns,
            "grid_rows": config.grid_rows,
            "mask_digests": {
                mask_id: masks[mask_id]["mask_digest"] for mask_id in sorted(masks)
            },
        }
    )


def _build_config() -> coordinator.S2JVCoordinatorConfigV1:
    profile = build_s2jw_default_live_profile()
    return coordinator.build_s2jv_coordinator_config(
        tspm_config=profile.tspm_config,
        b4_capacity=profile.b4_capacity,
        ledger_limits=build_s2jv_ledger_limits(profile),
    )


class _SourceStream:
    def __init__(
        self,
        *,
        config: coordinator.S2JVCoordinatorConfigV1,
        plan: dict[str, object],
        prior: dict[str, object],
    ) -> None:
        self.config = config
        self.recipes = {
            str(item["source_id"]): item
            for item in plan["generation_root"]["recipes"]  # type: ignore[index]
        }
        self.bindings = {
            str(item["source_id"]): item
            for item in plan["generation_root"]["source_bindings"]  # type: ignore[index]
        }
        self.value_digests = {
            str(item["source_id"]): str(item["visual_values_digest"])
            for item in prior["state_bindings"]  # type: ignore[index]
        }
        self.visual = LocalChannelGridReceptor(VisualGridConfig())
        self.hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        self.next_ordinal = 1

    def _visual_source(self, source_id: str) -> tuple[np.ndarray, str, str]:
        if source_id == "pressure-d1":
            spec = pressure_fixtures.FIXTURE_BY_LABEL["D1"]
            image = pressure_fixtures._visual_image(spec.ordinal)
            return image, spec.visual_payload_digest, spec.visual_values_digest
        recipe = self.recipes[source_id]
        image = corpus.render_frame(recipe)
        binding = self.bindings[source_id]
        return image, str(binding["payload_sha256"]), self.value_digests[source_id]

    def _audio_state(self, role: str):
        window = audio_fixtures.auditory_pcm(role)
        state = None
        for hop in range(10):
            state = self.hearing.push(window[hop * 480 : (hop + 1) * 480])
        _require(state is not None, "audio endpoint is absent")
        _require(
            _digest(list(state.energy)) == audio_fixtures._EXPECTED_VALUE_DIGESTS[role],
            "audio receptor values differ",
        )
        return window, state

    def formation(self, source_id: str):
        ordinal = self.next_ordinal
        _require(
            ordinal <= len(FORMATION_SOURCES)
            and source_id == FORMATION_SOURCES[ordinal - 1],
            "formation order differs",
        )
        audio_role = "D_FAR" if source_id == "pressure-d1" else "L"
        window, auditory_state = self._audio_state(audio_role)
        image, visual_payload_digest, visual_values_digest = self._visual_source(source_id)
        _require(hashlib.sha256(image.tobytes(order="C")).hexdigest() == visual_payload_digest, "visual payload differs")
        visual_state = self.visual.analyze(image, frame_index=(ordinal - 1) * 3 + 2)
        _require(_digest(list(visual_state.channel_values)) == visual_values_digest, "visual receptor values differ")
        end = ordinal * 100_000_000
        auditory = OrganismTimedReceptorFrame(
            from_auditory_receptor_state(auditory_state),
            CommonFieldTime(field_runtime.FIELD_CLOCK_ID, end - 10_000_000, end),
        )
        visual = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                field_runtime.FIELD_CLOCK_ID,
                (((ordinal - 1) * 3 + 2) * 1_000_000_000) // 30,
                end,
            ),
        )
        audio_digest = hashlib.sha256(np.asarray(window, dtype="<f4").tobytes()).hexdigest()
        plan = build_s2jv_pairing_plan(
            pair_id=f"s2mb-pair-{ordinal:03d}",
            source_contract_id="s2mb-source-contract",
            profile=self.config.profile,
            auditory=auditory,
            visual=visual,
            auditory_payload_digest=audio_digest,
            visual_payload_digest=visual_payload_digest,
        )
        pair = bind_s2jv_default_live_pair(
            pairing_plan=plan,
            profile=self.config.profile,
            auditory=auditory,
            visual=visual,
        )
        field_input = field_runtime.S2LOFieldInputV1(
            pair.pairing_digest,
            (ordinal - 1) * 100_000_000,
            end,
            (auditory, visual),
        )
        self.next_ordinal += 1
        del image, window
        return pair, field_input, tuple(visual_state.channel_values)

    def visual_look(
        self,
        *,
        source_id: str,
        case_plan_digest: str,
        mask: dict[str, object],
        geometry_digest: str,
        look_tick: int,
        field_contact_digest: str | None,
    ) -> tuple[integration.ARecentObservedLookV1, field_runtime.S2LOFieldInputV1]:
        ordinal = self.next_ordinal
        image, payload_digest, visual_values_digest = self._visual_source(source_id)
        _require(hashlib.sha256(image.tobytes(order="C")).hexdigest() == payload_digest, "look payload differs")
        visual_state = self.visual.analyze(image, frame_index=(ordinal - 1) * 3 + 2)
        values = tuple(visual_state.channel_values)
        _require(_digest(list(values)) == visual_values_digest, "look receptor values differ")
        end = ordinal * 100_000_000
        timed = OrganismTimedReceptorFrame(
            from_visual_receptor_state(visual_state),
            CommonFieldTime(
                field_runtime.FIELD_CLOCK_ID,
                (((ordinal - 1) * 3 + 2) * 1_000_000_000) // 30,
                end,
            ),
        )
        field_input = field_runtime.S2LOFieldInputV1(
            _digest({"source": source_id, "ordinal": ordinal}),
            (ordinal - 1) * 100_000_000,
            end,
            (timed,),
        )
        view = projection.bind_observed_view(
            values,
            str(mask["mask_id"]),
            tuple(mask["positions"]),
            str(mask["mask_digest"]),
        )
        observation_payload = {
            "source_id": source_id,
            "payload_sha256": payload_digest,
            "case_plan_digest": case_plan_digest,
            "mask_digest": mask["mask_digest"],
            "native_clock_id": timed.frame.clock_id,
            "native_window": [timed.frame.window_start_tick, timed.frame.window_end_tick],
            "look_tick": look_tick,
        }
        look = integration.ARecentObservedLookV1(
            owner_id=f"s2mb-look-owner-{look_tick:03d}",
            case_plan_digest=case_plan_digest,
            source_observation_digest=_digest(observation_payload),
            source_id=source_id,
            payload_sha256=payload_digest,
            geometry_digest=geometry_digest,
            tick=look_tick,
            mask_id=str(mask["mask_id"]),
            mask_digest=str(mask["mask_digest"]),
            observed_positions=view.observed_positions,
            observed_values=view.observed_values,
            observed_values_digest=view.observed_values_digest,
            source_values_digest=view.source_values_digest,
            field_contact_digest=field_contact_digest,
        )
        self.next_ordinal += 1
        del image, visual_state, values
        return look, field_input


def _field_event(
    *,
    ordinal: int,
    event_type: str,
    source_digest: str,
    perception_digest: str,
    field_input: field_runtime.S2LOFieldInputV1,
    operation_payload: object,
) -> stream.PerceptionStreamEvent336V1:
    return stream.build_perception_stream_event(
        event_id=f"s2mb-event-{ordinal:03d}",
        ordinal=ordinal,
        event_type=event_type,
        source_digest=source_digest,
        perception_digest=perception_digest,
        field_projection_digest=perception_digest,
        operation_projection_digest=perception_digest,
        field_payload=field_input,
        operation_payload=operation_payload,
    )


def _repeat_prototype(values: tuple[float, ...], match_count: int) -> tuple[float, ...]:
    prototype = values
    for _ in range(match_count):
        prototype = tuple(0.95 * previous + 0.05 * current for previous, current in zip(prototype, values, strict=True))
    return prototype


def _candidate_bindings(
    *,
    state: coordinator.S2JVCompositeStateV1,
    training_values: dict[str, tuple[float, ...]],
    prior: dict[str, object],
) -> tuple[bstable.BStableCalibrationBindingV1, ...]:
    rows = {
        str(item["model_id"]): item
        for item in prior["calibration_envelopes"]["representations"]["UNION_FORM_192"]  # type: ignore[index]
    }
    slot_ids = tuple(slot.slot_id for slot in state.tspm_state.visual_ppb1_state.slots)
    _require(len(slot_ids) == 4, "visual slot anatomy differs")
    result = []
    for index, (model_id, source_id, match_count) in enumerate(
        (
            ("model-01", "source-001", 2),
            ("model-02", "source-007", 3),
            ("model-03", "source-013", 3),
        )
    ):
        row = rows[model_id]
        prototype = _repeat_prototype(training_values[source_id], match_count)
        result.append(
            bstable.BStableCalibrationBindingV1(
                slot_ids[index],
                model_id,
                float(row["calibration_radius"]),
                str(row["envelope_digest"]),
                _digest(list(prototype)),
            )
        )
    pressure_prototype = _repeat_prototype(training_values["pressure-d1"], 7)
    pressure_payload = {
        "schema": "s2mb.identical-pressure-calibration.v1",
        "source_values_digest": _digest(list(training_values["pressure-d1"])),
        "reference_count": 4,
        "calibration_rule": "MAX_REFERENCE_TO_REFERENCE_CENTROID_MEAN_L1",
        "calibration_radius": 0.0,
        "test_sources_available": False,
    }
    result.append(
        bstable.BStableCalibrationBindingV1(
            slot_ids[3],
            "pressure-control",
            0.0,
            _digest(pressure_payload),
            _digest(list(pressure_prototype)),
        )
    )
    return tuple(result)


def _expected_slot(case_id: str, slot_ids: tuple[str, ...]) -> str | None:
    return {
        "case-001": slot_ids[0],
        "case-002": slot_ids[0],
        "case-004": slot_ids[1],
        "case-005": slot_ids[2],
        "case-006": slot_ids[2],
    }.get(case_id)


def build_run(workspace_root: Path) -> dict[str, object]:
    _require(isinstance(workspace_root, Path) and workspace_root.is_absolute(), "absolute workspace Path required")
    plan = _load_record(workspace_root, PLAN_BINDING, "plan_digest")
    prior = _load_record(workspace_root, S2LZ_RESULT_BINDING, "comparison_digest")
    masks = {
        str(item["mask_id"]): item
        for item in plan["mask_root"]["masks"]  # type: ignore[index]
    }
    cases = tuple(plan["execution_root"]["cases"])  # type: ignore[index]
    _require(len(cases) == 20, "case inventory differs")
    config = _build_config()
    sources = _SourceStream(config=config, plan=plan, prior=prior)
    memory_state = coordinator.initial_s2jv_composite_state(config)
    field_adapter = field_runtime.build_s2lo_field_adapter()
    field_state = None
    formation_records = []
    training_values: dict[str, tuple[float, ...]] = {}

    for ordinal, source_id in enumerate(FORMATION_SOURCES, start=1):
        pair, field_input, visual_values = sources.formation(source_id)
        training_values.setdefault(source_id, visual_values)
        field_event = _field_event(
            ordinal=ordinal,
            event_type="COMPLETE_AV_PERCEPTION",
            source_digest=_digest({"formation_source": source_id, "ordinal": ordinal}),
            perception_digest=pair.pairing_digest,
            field_input=field_input,
            operation_payload=pair,
        )
        if field_state is None:
            field_state = field_runtime.initial_s2lo_field_state(field_input)
        field_result = field_adapter(field_state, field_event)
        field_state = field_result.poststate
        bound = coordinator.bind_s2jv_coordinator_input(config=config, source=pair)
        owner = coordinator.S2JVFormationOwner(
            f"s2mb-memory-owner-{ordinal:03d}",
            f"s2mb-memory-auth-{ordinal:03d}",
            f"s2mb-memory-consume-{ordinal:03d}",
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
        formation_records.append(
            {
                "ordinal": ordinal,
                "source_role": "FAMILY" if source_id != "pressure-d1" else "PRESSURE",
                "source_digest": _digest({"source": source_id}),
                "prestate_digest": memory_state.state_digest,
                "poststate_digest": formed.poststate.state_digest,
                "formation_receipt_digest": formed.receipt.receipt_digest,
                "field_receipt_digest": field_result.receipt_digest,
            }
        )
        memory_state = formed.poststate

    _require(field_state is not None and memory_state.generation == 21, "formation closure differs")
    memory_before_retrieval = memory_state.state_digest
    occupied_b4 = tuple(item for item in memory_state.b4_state.entries if item.occupied)
    occupied_fast = tuple(item for item in memory_state.tspm_state.fast_state.slots if item.occupied)
    _require(
        len(occupied_b4) == 9
        and all(item.formation_index is not None and item.formation_index >= 13 for item in occupied_b4)
        and len(occupied_fast) == 1,
        "A_RECENT displacement differs",
    )

    candidate_bindings = _candidate_bindings(
        state=memory_state,
        training_values=training_values,
        prior=prior,
    )
    candidate_set = bstable.bind_visual_bstable_candidates(
        config=config,
        state=memory_state,
        bindings=candidate_bindings,
        union_mask_digest=str(masks["UNION_192"]["mask_digest"]),
        union_positions=tuple(masks["UNION_192"]["positions"]),
    )
    slot_ids = tuple(item.slot_id for item in candidate_set.candidates)
    _require(
        len(slot_ids) == 4
        and all(item.support == 3 for item in candidate_set.candidates)
        and candidate_set.prestate_digest == candidate_set.poststate_digest,
        "B_STABLE candidate closure differs",
    )

    geometry_digest = _geometry_digest(VisualGridConfig(), masks)
    subject = integration.ARecentTransientTwoViewIntegrator(
        geometry_digest=geometry_digest,
        view_a_mask_digest=str(masks["VIEW_A_96"]["mask_digest"]),
        view_b_mask_digest=str(masks["VIEW_B_96"]["mask_digest"]),
        union_mask_digest=str(masks["UNION_192"]["mask_digest"]),
        union_positions=tuple(masks["UNION_192"]["positions"]),
        model_envelopes=candidate_set.model_envelopes(),
    )
    case_records = []
    field_ordinal = 21
    for case_index, case in enumerate(cases):
        looks = []
        field_receipts = []
        for mask_id, source_key in (
            ("VIEW_A_96", "view_a_source_id"),
            ("VIEW_B_96", "view_b_source_id"),
        ):
            look_tick = case_index * 2 + len(looks) + 1
            provisional, field_input = sources.visual_look(
                source_id=str(case[source_key]),
                case_plan_digest=str(case["case_plan_digest"]),
                mask=masks[mask_id],
                geometry_digest=geometry_digest,
                look_tick=look_tick,
                field_contact_digest=None,
            )
            field_ordinal += 1
            field_event = _field_event(
                ordinal=field_ordinal,
                event_type="PARTIAL_VISUAL_CUE",
                source_digest=_digest({"look": provisional.source_observation_digest}),
                perception_digest=field_input.perception_digest,
                field_input=field_input,
                operation_payload=provisional,
            )
            field_result = field_adapter(field_state, field_event)
            field_state = field_result.poststate
            look = replace(provisional, field_contact_digest=field_result.receipt_digest)
            looks.append(look)
            field_receipts.append(field_result.receipt_digest)
        pending = subject.process(looks[0])
        context_result = subject.process(looks[1])
        direct = bstable.direct_bstable_two_view_baseline(
            first=looks[0],
            second=looks[1],
            candidates=candidate_set,
            geometry_digest=geometry_digest,
            view_a_mask_digest=str(masks["VIEW_A_96"]["mask_digest"]),
            view_b_mask_digest=str(masks["VIEW_B_96"]["mask_digest"]),
        )
        exact_baseline = (
            context_result.status == direct["status"]
            and context_result.selected_model_id == direct["selected_model_id"]
            and context_result.reason == direct["reason"]
            and context_result.open_set_decision_digest == direct["decision_digest"]
        )
        expected = _expected_slot(str(case["case_id"]), slot_ids)
        function_matches = context_result.selected_model_id == expected and (
            (expected is not None and context_result.status == "ADMITTED")
            or (expected is None and context_result.status == "ABSTAINED")
        )
        payload = {
            "case_id": case["case_id"],
            "current_only": {
                "status": "UNCHANGED_NO_CONTEXT_HYPOTHESIS",
                "selected_slot_id": None,
                "observed_value_count": 192,
            },
            "pending_result_digest": pending.digest(),
            "context_result": context_result.canonical_payload(),
            "context_result_digest": context_result.digest(),
            "direct_baseline": direct,
            "exact_direct_baseline": exact_baseline,
            "expected_slot_id": expected,
            "function_matches_prebound_expectation": function_matches,
            "field_contact_digests": field_receipts,
            "window_empty": subject.pending_count == 0,
        }
        case_records.append({**payload, "case_result_digest": _digest(payload)})

    memory_after_retrieval = memory_state.state_digest
    _require(
        memory_before_retrieval == memory_after_retrieval
        and all(item["exact_direct_baseline"] and item["function_matches_prebound_expectation"] for item in case_records)
        and all(item["window_empty"] for item in case_records),
        "S2-MB functional result differs",
    )
    candidate_records = [
        {**item.payload_without_digest(), "candidate_digest": item.candidate_digest}
        for item in candidate_set.candidates
    ]
    payload = {
        "schema": SCHEMA,
        "run_id": RUN_ID,
        "status": "S2MB_BSTABLE_TWO_VIEW_CONTEXT_CONFIRMED",
        "presealed_plan_digest": PLAN_BINDING[2],
        "s2lz_comparison_digest": S2LZ_RESULT_BINDING[2],
        "config_digest": config.config_digest,
        "formation_count": 21,
        "look_count": 40,
        "case_count": 20,
        "field_step_count": field_state.step_count,
        "field_contact_count": 82,
        "formation_records": formation_records,
        "candidate_set": {
            **candidate_set.payload_without_digest(),
            "candidate_set_digest": candidate_set.candidate_set_digest,
            "candidates": candidate_records,
        },
        "case_records": case_records,
        "known_stabilized_holdout_hits": 5,
        "known_stabilized_holdout_total": 6,
        "conservative_known_abstentions": 1,
        "nonmember_or_incompatible_abstentions": 14,
        "false_context_admissions": 0,
        "memory_pre_retrieval_digest": memory_before_retrieval,
        "memory_post_retrieval_digest": memory_after_retrieval,
        "field_final_state_digest": field_state.state_digest,
        "window_empty_at_end": subject.pending_count == 0,
        "raw_payload_retained": False,
        "new_descriptor_threshold_or_selection_rule": False,
        "calls": {
            "visual_receptor": 61,
            "audio_windows": 21,
            "memory_formations": 21,
            "memory_reads_during_retrieval": 0,
            "field_steps": 61,
            "a_recent_two_view": 40,
            "direct_baseline": 20,
            "current_only": 20,
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
    _require(
        value.get("status") == "S2MB_BSTABLE_TWO_VIEW_CONTEXT_CONFIRMED"
        and value.get("formation_count") == 21
        and value.get("look_count") == 40
        and value.get("case_count") == 20
        and value.get("field_step_count") == 61
        and value.get("field_contact_count") == 82,
        "run inventory differs",
    )
    _require(
        len(value.get("formation_records", ())) == 21
        and len(value.get("case_records", ())) == 20
        and len(value["candidate_set"]["candidates"]) == 4,
        "artifact inventory differs",
    )
    _require(
        value.get("memory_pre_retrieval_digest") == value.get("memory_post_retrieval_digest")
        and value.get("window_empty_at_end") is True
        and value.get("false_context_admissions") == 0
        and value.get("raw_payload_retained") is False
        and value.get("new_descriptor_threshold_or_selection_rule") is False,
        "read-only or scope boundary differs",
    )
    _require(
        all(
            item["exact_direct_baseline"]
            and item["function_matches_prebound_expectation"]
            and item["window_empty"]
            and len(item["field_contact_digests"]) == 2
            for item in value["case_records"]
        ),
        "case closure differs",
    )
    _require(before == hashlib.sha256(path.read_bytes()).hexdigest(), "verification changed result")
    return {
        "verification_status": "RECORDING_COMPLETE",
        "result_file_sha256": before,
        "result_digest": value["result_digest"],
    }


__all__: tuple[str, ...] = ()
