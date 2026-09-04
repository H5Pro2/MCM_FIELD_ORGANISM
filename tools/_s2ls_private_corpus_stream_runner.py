"""Private closed runner for the presealed S2-LS corpus stream."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
from threading import Lock

from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2kq_private_partial_cue_retrieval_336 as visual_scan
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_scan
from tools import _s2lm_private_role_free_stream_processor as stream
from tools import _s2lo_private_role_free_stream_runner as stream_shell
from tools import _s2jw_profiled_memory_coordinator as memory
from tools._s2jw_default_live_av_pairing import (
    S2JVBoundAVPairV1,
    bind_s2jv_default_live_pair,
    build_s2jv_pairing_plan,
)


SCHEMA = "s2ls.presealed-corpus-stream.v1"
RESULT_SCHEMA = "s2ls.presealed-corpus-stream-result.v1"
QUALIFICATION_ID = "s2ls-neutral-stream-qualification-20260904-02"
AUTHORIZED_RUN_ID = "s2ls-real-presealed-av-corpus-20260904-01"
MAIN_EXECUTION_ENABLED = False
MAX_RESULT_BYTES = 2_097_152
EXPECTED_PLAN_DIGEST = "1ad42964295cce44b87f6c3d02479983878ca7c403eee21440783fe3326e661a"
EXPECTED_PLAN_FILE_SHA256 = "d1453b4abefdccb6425e4faf5b2d434cfda842f608d75bed585f5b12dd7338ae"
EXPECTED_EVIDENCE_DIGEST = "0840c261f91f824cd913fb1bc5ccdd9ba21b75d6680e61948561a986e2443f9b"
EXPECTED_EVIDENCE_FILE_SHA256 = "e09583f995f75ff4d9454af969133b51d9b4852a404af24befa61fadb8757e8a"
PLAN_RELATIVE_PATH = "reports/s2ls/s2ls-presealed-av-corpus-plan-20260904-01/presealed-corpus-plan.json"
EVIDENCE_RELATIVE_PATH = "reports/s2ls/s2ls-corpus-receptor-materialization-20260904-01/receptor-materialization.json"

_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_LOCK = Lock()
_USED = False

SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2kq_private_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2lm_private_role_free_stream_processor.py",
    "tools/_s2lo_private_role_free_stream_runner.py",
    "tools/_s2ls_private_presealed_av_corpus_plan.py",
    "tools/_s2ls_private_corpus_receptor_materialization.py",
    "tools/_s2ls_private_corpus_stream_runner.py",
    "tools/_s2ls_private_corpus_stream_verifier.py",
)


class S2LSStreamError(RuntimeError):
    """The frozen source, stream, transition, or result relation is invalid."""


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
        raise S2LSStreamError(message)


def _valid_digest(value: object) -> bool:
    return type(value) is str and _DIGEST.fullmatch(value) is not None


def _load_canonical(path: Path, expected_sha256: str) -> dict[str, object]:
    data = path.read_bytes()
    _require(hashlib.sha256(data).hexdigest() == expected_sha256, "frozen file digest differs")
    value = json.loads(data.decode("ascii"))
    _require(data == _canonical_bytes(value, newline=True), "frozen file is not canonical")
    _require(type(value) is dict, "frozen root differs")
    return value


@dataclass(frozen=True, slots=True)
class FrozenCorpusV1:
    plan: dict[str, object]
    evidence: dict[str, object]
    content: dict[str, dict[str, object]]
    visual_cues: dict[str, dict[str, object]]
    events: tuple[dict[str, object], ...]


def load_frozen_corpus(workspace_root: Path) -> FrozenCorpusV1:
    _require(isinstance(workspace_root, Path) and workspace_root.is_absolute(), "absolute workspace Path required")
    plan = _load_canonical(workspace_root / PLAN_RELATIVE_PATH, EXPECTED_PLAN_FILE_SHA256)
    evidence = _load_canonical(workspace_root / EVIDENCE_RELATIVE_PATH, EXPECTED_EVIDENCE_FILE_SHA256)
    plan_payload = dict(plan)
    plan_digest = plan_payload.pop("plan_digest", None)
    evidence_payload = dict(evidence)
    evidence_digest = evidence_payload.pop("evidence_digest", None)
    _require(plan_digest == EXPECTED_PLAN_DIGEST == _digest(plan_payload), "plan digest differs")
    _require(evidence_digest == EXPECTED_EVIDENCE_DIGEST == _digest(evidence_payload), "evidence digest differs")
    _require(evidence.get("plan_digest") == EXPECTED_PLAN_DIGEST, "evidence plan binding differs")
    _require(evidence.get("status") == "S2LS_RECEPTOR_GEOMETRY_MATERIALIZED", "evidence status differs")
    _require(evidence.get("distance_acceptance_gate_used") is False, "distance gate entered materialization")
    _require(
        (evidence.get("memory_calls"), evidence.get("field_calls"), evidence.get("context_calls")) == (0, 0, 0),
        "materialization crossed a functional boundary",
    )
    content_rows = evidence.get("content_receptor_states")
    cue_rows = evidence.get("visual_cue_receptor_states")
    event_rows = evidence.get("event_receptor_bindings")
    _require(type(content_rows) is list and len(content_rows) == 21, "content receptor inventory differs")
    _require(type(cue_rows) is list and len(cue_rows) == 4, "visual cue inventory differs")
    _require(type(event_rows) is list and len(event_rows) == 25, "event receptor inventory differs")
    content = {str(row["content_id"]): row for row in content_rows}
    visual_cues = {str(row["content_id"]): row for row in cue_rows}
    _require(len(content) == 21 and len(visual_cues) == 4, "frozen source identifiers are not unique")
    for row in content_rows:
        for modality, expected in (("auditory", 48), ("visual", 288)):
            state = row.get(modality)
            _require(type(state) is dict and len(state.get("values", ())) == expected, "receptor dimension differs")
            _require(state.get("values_digest") == _digest(state["values"]), "receptor values digest differs")
            _require(all(math.isfinite(float(item)) and 0.0 <= float(item) <= 1.0 for item in state["values"]), "receptor value differs")
    return FrozenCorpusV1(plan, evidence, content, visual_cues, tuple(event_rows))


def source_hashes(workspace_root: Path) -> dict[str, str]:
    result = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        _require(path.is_file(), f"bound source missing: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _spec(ordinal: int, event: dict[str, object], *, qualification: bool) -> stream_shell.S2LOEventSpecV1:
    event_type = {
        "FULL_AV_FORMATION": "COMPLETE_AV_PERCEPTION",
        "VISUAL_PARTIAL_CUE": "PARTIAL_VISUAL_CUE",
        "AUDITORY_PARTIAL_CUE": "PARTIAL_AUDITORY_CUE",
    }[str(event["event_kind"])]
    code = f"q{ordinal:02d}" if qualification else f"e{ordinal:02d}"
    event_id = f"s2ls-qualification-{code}" if qualification else f"s2ls-stream-{code}"
    payload = {
        "schema": stream_shell.S2LO_SCHEMA,
        "event_code": code,
        "event_id": event_id,
        "ordinal": ordinal,
        "event_type": event_type,
        "content_id": event["content_id"],
    }
    return stream_shell.S2LOEventSpecV1(code, event_id, ordinal, event_type, str(event["content_id"]), _digest(payload))


def _frame(
    state: dict[str, object],
    event: dict[str, object],
    modality: str,
    common_start: int,
    common_end: int,
) -> OrganismTimedReceptorFrame:
    if modality == "auditory":
        start = int(event["auditory_window_start_sample"])
        end = int(event["auditory_window_end_sample"])
        clock = str(event["auditory_source_clock_id"])
        snapshot = f"s2ls-auditory-{event['event_id']}"
    else:
        start = int(event["visual_frame_index"])
        end = start + 1
        clock = str(event["visual_source_clock_id"])
        snapshot = f"s2ls-visual-{event['event_id']}"
    receptor = ReceptorContactFrame(
        modality,
        str(state["geometry_id"]),
        snapshot,
        clock,
        start,
        end,
        tuple(str(item) for item in state["carrier_ids"]),
        tuple(float(item) for item in state["values"]),
    )
    return OrganismTimedReceptorFrame(
        receptor,
        CommonFieldTime(stream_shell.FIELD_CLOCK_ID, common_start, common_end),
    )


class FrozenCorpusSource:
    """Project frozen receptor evidence into the qualified stream adapters."""

    def __init__(self, corpus: FrozenCorpusV1, config: memory.S2JVCoordinatorConfigV1, *, qualification: bool) -> None:
        self._corpus = corpus
        self._config = config
        self._qualification = qualification
        self._indexes = (0, 17, 18) if qualification else tuple(range(25))
        self._next = 0
        self._band_plan = auditory_scan.build_auditory_band_plan_48()

    def _materialize(self, source_index: int, ordinal: int) -> stream_shell.S2LOMaterializedEventV1:
        binding = self._corpus.events[source_index]
        content_id = str(binding["content_id"])
        content = self._corpus.content[content_id]
        spec = _spec(ordinal, binding, qualification=self._qualification)
        start = (ordinal - 1) * 100_000_000 if self._qualification else int(binding["common_start_ns"])
        end = ordinal * 100_000_000 if self._qualification else int(binding["common_end_ns"])
        frames: tuple[OrganismTimedReceptorFrame, ...]
        if spec.event_type == "COMPLETE_AV_PERCEPTION":
            auditory = _frame(content["auditory"], binding, "auditory", start, end)
            visual = _frame(content["visual"], binding, "visual", start, end)
            plan = build_s2jv_pairing_plan(
                pair_id=f"s2ls-pair-{ordinal:03d}",
                source_contract_id="s2ls-frozen-receptor-evidence",
                profile=self._config.profile,
                auditory=auditory,
                visual=visual,
                auditory_payload_digest=str(content["source_bindings"]["AUDITORY"]["payload_sha256"]),
                visual_payload_digest=str(content["source_bindings"]["VISUAL"]["payload_sha256"]),
            )
            operation = bind_s2jv_default_live_pair(
                pairing_plan=plan,
                profile=self._config.profile,
                auditory=auditory,
                visual=visual,
            )
            perception_digest = operation.pairing_digest
            frames = (auditory, visual)
        elif spec.event_type == "PARTIAL_VISUAL_CUE":
            cue_state = self._corpus.visual_cues[content_id]["state"]
            visual = _frame(cue_state, binding, "visual", start, end)
            values = tuple(float(item) for item in cue_state["values"])
            source_digest = _digest({"schema": SCHEMA, "event_binding_digest": binding["event_receptor_binding_digest"]})
            operation = visual_scan.build_masked_memory_cue_336(
                source_digest=source_digest,
                config_digest=self._config.config_digest,
                field_clock_id=stream_shell.FIELD_CLOCK_ID,
                window_start_tick=start,
                window_end_tick=end,
                visual_source_clock_id=visual.frame.clock_id,
                visual_window_start_tick=visual.frame.window_start_tick,
                visual_window_end_tick=visual.frame.window_end_tick,
                values=tuple(values[index] if index in visual_scan.VISIBLE_POSITIONS else None for index in range(288)),
            )
            perception_digest = operation.cue_digest
            frames = (visual,)
        else:
            auditory = _frame(content["auditory"], binding, "auditory", start, end)
            values = tuple(float(item) for item in content["auditory"]["values"])
            operation = stream.AuditoryCueOperationV1(
                auditory_scan.build_masked_auditory_cue_48(
                    pcm_payload_digest=str(content["source_bindings"]["AUDITORY"]["payload_sha256"]),
                    receptor_state_digest=str(content["auditory"]["receptor_state_digest"]),
                    receptor_values_digest=str(content["auditory"]["values_digest"]),
                    config_digest=self._config.config_digest,
                    auditory_source_clock_id=auditory.frame.clock_id,
                    auditory_window_start_tick=auditory.frame.window_start_tick,
                    auditory_window_end_tick=auditory.frame.window_end_tick,
                    observed_values=tuple(values[index] for index in auditory_scan.OBSERVED_BANDS),
                    band_plan=self._band_plan,
                ),
                self._band_plan,
            )
            perception_digest = operation.cue.cue_digest
            frames = (auditory,)
        source_payload = {
            "schema": SCHEMA,
            "event_spec_digest": spec.spec_digest,
            "frozen_event_id": binding["event_id"],
            "event_receptor_binding_digest": binding["event_receptor_binding_digest"],
            "receptor_evidence_digest": EXPECTED_EVIDENCE_DIGEST,
            "perception_digest": perception_digest,
        }
        source_digest = _digest(source_payload)
        field_input = stream_shell.S2LOFieldInputV1(perception_digest, start, end, frames)
        return stream_shell.S2LOMaterializedEventV1(
            spec,
            source_digest,
            perception_digest,
            _digest({**source_payload, "source_digest": source_digest}),
            field_input,
            operation,
        )

    def materialize_next(self) -> tuple[stream_shell.S2LOMaterializedEventV1, dict[str, object]]:
        _require(self._next < len(self._indexes), "frozen source is exhausted")
        source_index = self._indexes[self._next]
        ordinal = self._next + 1
        value = self._materialize(source_index, ordinal)
        binding = self._corpus.events[source_index]
        self._next += 1
        return value, binding


def _slot_projection(slot: object, *, fast: bool) -> dict[str, object]:
    if fast:
        return {
            "slot_id": slot.slot_id,
            "occupied": slot.occupied,
            "support_count": slot.support_count,
            "last_selected_step": slot.last_selected_step,
            "consolidation_count": slot.consolidation_count,
            "auditory_values_digest": _digest(list(slot.auditory_values)),
            "visual_values_digest": _digest(list(slot.visual_values)),
            "slot_digest": slot.digest(),
        }
    return {
        "slot_id": slot.slot_id,
        "occupied": slot.occupied,
        "support_count": slot.support_count,
        "last_selected_step": slot.last_selected_step,
        "prototype_digest": _digest(list(slot.prototype_values)),
        "slot_digest": _ppb_slot_digest(slot),
    }


def _ppb_slot_digest(slot: object) -> str:
    payload_builder = getattr(slot, "canonical_payload", None)
    _require(callable(payload_builder), "PPB slot canonical payload is unavailable")
    payload = payload_builder()
    _require(type(payload) is dict, "PPB slot canonical payload differs")
    return _digest(payload)


def _ppb_transition(pre: object, post: object, source_values: tuple[float, ...], threshold: float) -> dict[str, object]:
    changed = [
        index
        for index, pair in enumerate(zip(pre.slots, post.slots, strict=True))
        if _ppb_slot_digest(pair[0]) != _ppb_slot_digest(pair[1])
    ]
    _require(len(changed) <= 1, "one formation changed multiple PPB slots")
    if not changed:
        payload = {"event": "NO_UPDATE", "slot_id": None, "pre_slot": None, "post_slot": None, "source_distance": None, "match_threshold": threshold}
        return {**payload, "transition_digest": _digest(payload)}
    index = changed[0]
    before, after = pre.slots[index], post.slots[index]
    if not before.occupied:
        event = "CREATED"
    elif after.support_count == before.support_count + 1:
        event = "MATCHED"
    else:
        event = "REPLACED"
    distance = None
    if before.occupied:
        distance = math.fsum(abs(left - right) for left, right in zip(before.prototype_values, source_values, strict=True)) / len(source_values)
    payload = {
        "event": event,
        "slot_id": after.slot_id,
        "pre_slot": _slot_projection(before, fast=False),
        "post_slot": _slot_projection(after, fast=False),
        "source_distance": distance,
        "match_threshold": threshold,
    }
    return {**payload, "transition_digest": _digest(payload)}


def formation_transition_record(
    prestate: memory.S2JVCompositeStateV1,
    poststate: memory.S2JVCompositeStateV1,
    source: S2JVBoundAVPairV1,
) -> dict[str, object]:
    _require(poststate.generation == prestate.generation + 1, "formation generation differs")
    pre_fast = prestate.tspm_state.fast_state
    post_fast = poststate.tspm_state.fast_state
    selected = [slot for slot in post_fast.slots if slot.occupied and slot.last_selected_step == post_fast.accepted_exposure_count]
    _require(len(selected) == 1, "Fast selection is not unique")
    chosen = selected[0]
    before = next(slot for slot in pre_fast.slots if slot.slot_id == chosen.slot_id)
    if not before.occupied:
        fast_event = "CREATED"
    elif chosen.support_count == before.support_count + 1:
        fast_event = "MATCHED"
    else:
        fast_event = "REPLACED"
    auditory_values = tuple(source.auditory.timed_frame.frame.values)
    visual_values = tuple(source.visual.timed_frame.frame.values)
    fast_payload = {
        "event": fast_event,
        "selected_slot_id": chosen.slot_id,
        "pre_slot": _slot_projection(before, fast=True),
        "post_slot": _slot_projection(chosen, fast=True),
        "expired_slot_digests": [
            old.digest()
            for old, new in zip(pre_fast.slots, post_fast.slots, strict=True)
            if old.occupied and not new.occupied
        ],
        "auditory_source_distance": None if not before.occupied else math.fsum(abs(a - b) for a, b in zip(before.auditory_values, auditory_values, strict=True)) / 48,
        "visual_source_distance": None if not before.occupied else math.fsum(abs(a - b) for a, b in zip(before.visual_values, visual_values, strict=True)) / 288,
    }
    fast_record = {**fast_payload, "transition_digest": _digest(fast_payload)}
    config = poststate.tspm_state
    auditory = _ppb_transition(
        prestate.tspm_state.auditory_ppb1_state,
        config.auditory_ppb1_state,
        auditory_values,
        0.02,
    )
    visual = _ppb_transition(
        prestate.tspm_state.visual_ppb1_state,
        config.visual_ppb1_state,
        visual_values,
        0.01,
    )
    payload = {
        "formation_index": poststate.generation,
        "prestate_digest": prestate.state_digest,
        "poststate_digest": poststate.state_digest,
        "source_pairing_digest": source.pairing_digest,
        "fast": fast_record,
        "auditory_ppb": auditory,
        "visual_ppb": visual,
    }
    return {**payload, "formation_transition_digest": _digest(payload)}


def _run_stream(workspace_root: Path, *, qualification: bool) -> tuple[dict[str, object], stream.PerceptionStreamStateV1]:
    corpus = load_frozen_corpus(workspace_root)
    config = stream_shell._build_config()
    source = FrozenCorpusSource(corpus, config, qualification=qualification)
    first, first_binding = source.materialize_next()
    state = stream_shell._initial_stream(config, first)
    initial_field = stream_shell._field_observation(state.field_state)
    processor = stream_shell._processor(config)
    expected_count = 3 if qualification else 25
    records = []
    materialized, binding = first, first_binding
    for index in range(expected_count):
        if index:
            materialized, binding = source.materialize_next()
        event = stream_shell.build_stream_event(materialized)
        pre_memory = state.memory_state
        owner = stream.PerceptionEventOwner(
            f"s2ls-event-owner-{materialized.spec.ordinal:03d}",
            state.state_digest,
            event.event_digest,
        )
        result = processor.process_once(state=state, event=event, owner=owner)
        record = stream_shell._event_record(materialized, event, result)
        record["frozen_event_id"] = binding["event_id"]
        record["event_receptor_binding_digest"] = binding["event_receptor_binding_digest"]
        if result.memory_result is not None:
            record["formation_transition"] = formation_transition_record(
                pre_memory,
                result.memory_result.poststate,
                materialized.operation_payload,
            )
        else:
            record["formation_transition"] = None
        records.append(record)
        state = result.poststate
        _require(not result.error_codes, "one stream branch failed")
    execution_payload = {
        "schema": SCHEMA,
        "initial_field_observation": initial_field,
        "events": records,
        "counters": {
            "event_count": state.processed_event_count,
            "field_attempt_count": state.field_attempt_count,
            "memory_formation_attempt_count": state.memory_formation_attempt_count,
            "scan_attempt_count": state.scan_attempt_count,
            "final_field_digest": state.field_state_digest,
            "final_memory_digest": state.memory_state_digest,
            "stream_status": state.status,
        },
    }
    return {**execution_payload, "execution_digest": _digest(execution_payload)}, state


def _mean_l1(left: tuple[float, ...], right: tuple[float, ...], positions: tuple[int, ...] | None = None) -> float:
    indexes = tuple(range(len(left))) if positions is None else positions
    return math.fsum(abs(left[index] - right[index]) for index in indexes) / len(indexes)


def _arm_result(
    candidates: tuple[tuple[str, tuple[float, ...]], ...],
    target: tuple[float, ...],
    observed: tuple[int, ...],
    threshold: float,
) -> dict[str, object]:
    rows = []
    for candidate_id, values in candidates:
        rows.append({
            "candidate_id": candidate_id,
            "candidate_digest": _digest(list(values)),
            "full_mean_l1": _mean_l1(target, values),
            "observed_mean_l1": _mean_l1(target, values, observed),
        })
    rows.sort(key=lambda item: (item["observed_mean_l1"], item["candidate_id"]))
    payload = {
        "candidate_count": len(rows),
        "threshold": threshold,
        "rows": rows,
        "accepted_candidate_ids": [item["candidate_id"] for item in rows if item["observed_mean_l1"] <= threshold],
        "nearest_candidate_id": None if not rows else rows[0]["candidate_id"],
        "nearest_observed_mean_l1": None if not rows else rows[0]["observed_mean_l1"],
    }
    return {**payload, "arm_digest": _digest(payload)}


def evaluate_completed_stream(
    corpus: FrozenCorpusV1,
    execution: dict[str, object],
    state: stream.PerceptionStreamStateV1,
) -> dict[str, object]:
    _require(execution["counters"]["event_count"] == 25, "main execution is incomplete")
    stored = state.memory_state
    stable_after = {
        "AUDITORY": 3,
        "VISUAL": 3,
    }
    adaptive = {
        "AUDITORY": tuple(
            (slot.slot_id, tuple(slot.prototype_values))
            for slot in stored.tspm_state.auditory_ppb1_state.slots
            if slot.occupied and slot.support_count >= stable_after["AUDITORY"]
        ),
        "VISUAL": tuple(
            (slot.slot_id, tuple(slot.prototype_values))
            for slot in stored.tspm_state.visual_ppb1_state.slots
            if slot.occupied and slot.support_count >= stable_after["VISUAL"]
        ),
    }
    families = corpus.plan["evaluation_root"]["families"]
    cases = []
    for family in families:
        training = tuple(str(item) for item in family["training_content_ids"])
        for holdout in family["holdout_content_ids"]:
            for modality, key, observed, threshold in (
                ("AUDITORY", "auditory", tuple(range(24)), 0.02),
                ("VISUAL", "visual", tuple(range(32)), 0.01),
            ):
                target = tuple(float(item) for item in corpus.content[str(holdout)][key]["values"])
                frozen = ((training[0], tuple(float(item) for item in corpus.content[training[0]][key]["values"])),)
                replay = tuple((item, tuple(float(value) for value in corpus.content[item][key]["values"])) for item in training)
                payload = {
                    "family_id": family["family_id"],
                    "holdout_content_id": holdout,
                    "modality": modality,
                    "target_values_digest": _digest(list(target)),
                    "adaptive": _arm_result(adaptive[modality], target, observed, threshold),
                    "frozen": _arm_result(frozen, target, observed, threshold),
                    "replay": _arm_result(replay, target, observed, threshold),
                }
                cases.append({**payload, "case_digest": _digest(payload)})
    lineages: dict[str, dict[str, list[str]]] = {"AUDITORY": {}, "VISUAL": {}}
    for event in execution["events"][:17]:
        transition = event["formation_transition"]
        for modality, key in (("AUDITORY", "auditory_ppb"), ("VISUAL", "visual_ppb")):
            item = transition[key]
            if item["slot_id"] is not None:
                lineages[modality].setdefault(item["slot_id"], []).append(event["content_id"])
    modality_findings = {}
    family_sets = {
        str(family["family_id"]): set(str(item) for item in family["training_content_ids"])
        for family in families
    }
    for modality in ("AUDITORY", "VISUAL"):
        slot_relations = []
        for slot_id, contents in sorted(lineages[modality].items()):
            touched = sorted(name for name, members in family_sets.items() if members.intersection(contents))
            slot_relations.append({"slot_id": slot_id, "content_ids": contents, "family_ids": touched})
        mixed = any(len(item["family_ids"]) > 1 for item in slot_relations)
        represented = {name for item in slot_relations for name in item["family_ids"]}
        status = "CROSS_FAMILY_MERGE" if mixed else ("FAMILY_SEPARATED" if represented == set(family_sets) else "PARTIAL_OR_FRAGMENTED")
        modality_findings[modality] = {"status": status, "slot_relations": slot_relations}
    payload = {
        "status": "S2LS_FUNCTION_EVALUATED",
        "technical_success_depends_on_function": False,
        "adaptive_win_required": False,
        "negative_results_are_evaluable": True,
        "modalities": modality_findings,
        "cases": cases,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def neutral_qualification_record(workspace_root: Path) -> dict[str, object]:
    execution, _ = _run_stream(workspace_root, qualification=True)
    payload = {
        "schema": RESULT_SCHEMA,
        "mode": "QUALIFICATION",
        "technical_status": "RECORDING_COMPLETE",
        "run_id": QUALIFICATION_ID,
        "frozen_binding": {
            "plan_digest": EXPECTED_PLAN_DIGEST,
            "plan_file_sha256": EXPECTED_PLAN_FILE_SHA256,
            "evidence_digest": EXPECTED_EVIDENCE_DIGEST,
            "evidence_file_sha256": EXPECTED_EVIDENCE_FILE_SHA256,
        },
        "plan": {"event_count": 3, "formation_count": 1, "cue_count": 2, "main_story_executed": False, "main_execution_enabled": False},
        "execution": execution,
        "evaluation": None,
        "source_hashes": source_hashes(workspace_root),
        "raw_payload_retained": False,
    }
    return {**payload, "record_digest": _digest(payload)}


def _main_record(workspace_root: Path, run_id: str) -> dict[str, object]:
    corpus = load_frozen_corpus(workspace_root)
    execution, state = _run_stream(workspace_root, qualification=False)
    evaluation = evaluate_completed_stream(corpus, execution, state)
    payload = {
        "schema": RESULT_SCHEMA,
        "mode": "MAIN",
        "technical_status": "RECORDING_COMPLETE",
        "run_id": run_id,
        "frozen_binding": {
            "plan_digest": EXPECTED_PLAN_DIGEST,
            "plan_file_sha256": EXPECTED_PLAN_FILE_SHA256,
            "evidence_digest": EXPECTED_EVIDENCE_DIGEST,
            "evidence_file_sha256": EXPECTED_EVIDENCE_FILE_SHA256,
        },
        "plan": {"event_count": 25, "formation_count": 17, "cue_count": 8, "main_execution_enabled": True},
        "execution": execution,
        "evaluation": evaluation,
        "source_hashes": source_hashes(workspace_root),
        "raw_payload_retained": False,
    }
    return {**payload, "record_digest": _digest(payload)}


def write_result_once(output_root: Path, run_id: str, record: dict[str, object]) -> Path:
    _require(isinstance(output_root, Path) and output_root.is_absolute(), "absolute output Path required")
    _require(type(run_id) is str and _RUN_ID.fullmatch(run_id) is not None, "run id differs")
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


def run_main_once(*, workspace_root: Path, output_root: Path, run_id: str) -> Path:
    global MAIN_EXECUTION_ENABLED, _USED
    _require(MAIN_EXECUTION_ENABLED is True, "main execution gate is closed")
    _require(run_id == AUTHORIZED_RUN_ID, "run id is not authorized")
    _require(not _USED and _LOCK.acquire(blocking=False), "main execution is already consumed")
    _USED = True
    try:
        return write_result_once(output_root, run_id, _main_record(workspace_root, run_id))
    finally:
        MAIN_EXECUTION_ENABLED = False
        _LOCK.release()


__all__: tuple[str, ...] = ()
