"""Small closed S2-LJ runner; the 13-formation main gate stays disabled."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re

from mcm_field_organism.field_time_partition import partition_receptor_completion_time
from mcm_field_organism.receptor_time_model import ReceptorTimeSequence
from tools import _s2jt_private_timed_field_projection as field_path
from tools import _s2jw_profiled_memory_coordinator as memory
from tools import _s2kq_private_direct_slot_scan_baseline as visual_baseline
from tools import _s2kq_private_partial_cue_retrieval_336 as visual_scan
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as auditory_scan
from tools import _s2kz_private_direct_auditory_slot_scan_baseline as auditory_baseline
from tools._s2jw_default_live_profile import build_s2jw_default_live_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools._s2lj_coherent_av_fixtures import (
    FIELD_CLOCK_ID,
    MAIN_FORMATION_COUNT,
    S2LJSourceStream,
)


S2LJ_RESULT_SCHEMA = "s2lj.coherent-av-end-to-end-result.v1"
S2LJ_TRANSITION_SCHEMA = "s2lj.ppb-transition-proof.v1"
S2LJ_COMPLETION_SCHEMA = "s2lj.masked-context-completion.v1"
MAIN_EXECUTION_ENABLED = False
AUTHORIZED_RUN_ID: str | None = None
MAIN_FIELD_GROUP_COUNT = 15
MAIN_MAX_FUNCTIONAL_OPERATIONS = 240
MAIN_RAW_BYTES = 87_360_000
MAIN_FIELD_CONTACTS_PER_ARM = 4_704
UPDATE_RATE = 0.05
EVENT_CHAIN = ("CREATED", "MATCHED", "MATCHED")
SUPPORT_CHAIN = (1, 2, 3)
MAX_RESULT_BYTES = 524_288
_RUN_ID = re.compile(r"^[a-z][a-z0-9-]{7,95}$")

SOURCE_PATHS = (
    "mcm_field_organism/_ppb1_reference.py",
    "mcm_field_organism/_tspm1_private.py",
    "mcm_field_organism/finite_video_path.py",
    "mcm_field_organism/log_spectral_receptor.py",
    "mcm_field_organism/broadband_hearing_path.py",
    "tools/_s2jt_private_timed_field_projection.py",
    "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_profiled_memory_coordinator.py",
    "tools/_s2kq_private_partial_cue_retrieval_336.py",
    "tools/_s2kq_private_direct_slot_scan_baseline.py",
    "tools/_s2kz_private_auditory_partial_cue_retrieval_336.py",
    "tools/_s2kz_private_direct_auditory_slot_scan_baseline.py",
    "tools/_s2lj_coherent_av_fixtures.py",
    "tools/_s2lj_coherent_av_runner.py",
    "tools/_s2lj_coherent_av_verifier.py",
)


class S2LJRunnerError(RuntimeError):
    """The bounded integration path cannot produce one valid result."""


def _canonical_bytes(value: object, *, newline: bool = False) -> bytes:
    encoded = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return encoded + (b"\n" if newline else b"")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def source_hashes(workspace_root: Path) -> dict[str, str]:
    if not isinstance(workspace_root, Path) or not workspace_root.is_absolute():
        raise S2LJRunnerError("workspace_root must be one absolute Path")
    result: dict[str, str] = {}
    for relative in SOURCE_PATHS:
        path = workspace_root / relative
        if not path.is_file():
            raise S2LJRunnerError(f"bound source missing: {relative}")
        result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _build_config() -> memory.S2JVCoordinatorConfigV1:
    profile = build_s2jw_default_live_profile()
    return memory.build_s2jv_coordinator_config(
        tspm_config=profile.tspm_config,
        b4_capacity=profile.b4_capacity,
        ledger_limits=build_s2jv_ledger_limits(profile),
    )


def _numeric_tuple(value: object, dimension: int, role: str) -> tuple[float, ...]:
    if (
        type(value) is not tuple
        or len(value) != dimension
        or any(type(item) not in (int, float) for item in value)
    ):
        raise S2LJRunnerError(f"{role} must be one exact numeric tuple")
    result = tuple(float(item) for item in value)
    if any(not math.isfinite(item) or abs(item) > 1.0 for item in result):
        raise S2LJRunnerError(f"{role} differs from the receptor domain")
    return result


def _matched_update(previous: tuple[float, ...], current: tuple[float, ...]) -> tuple[float, ...]:
    return tuple(
        (1.0 - UPDATE_RATE) * old + UPDATE_RATE * new
        for old, new in zip(previous, current, strict=True)
    )


@dataclass(frozen=True, slots=True)
class S2LJPPBTransitionProofV1:
    modality: str
    dimension: int
    event_chain: tuple[str, ...]
    support_chain: tuple[int, ...]
    input_values: tuple[tuple[float, ...], ...]
    recorded_prototype_values: tuple[tuple[float, ...], ...]
    input_digests: tuple[str, ...]
    prototype_digests: tuple[str, ...]
    final_masked_digest: str
    integrity_status: str
    proof_digest: str
    schema: str = S2LJ_TRANSITION_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "modality": self.modality,
            "dimension": self.dimension,
            "event_chain": list(self.event_chain),
            "support_chain": list(self.support_chain),
            "input_values": [list(item) for item in self.input_values],
            "recorded_prototype_values": [
                list(item) for item in self.recorded_prototype_values
            ],
            "input_digests": list(self.input_digests),
            "prototype_digests": list(self.prototype_digests),
            "final_masked_digest": self.final_masked_digest,
            "integrity_status": self.integrity_status,
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "proof_digest": self.proof_digest}


def derive_ppb_transition_proof(
    *,
    modality: str,
    ppb_inputs: tuple[tuple[float, ...], ...],
    recorded_prototypes: tuple[tuple[float, ...], ...],
) -> S2LJPPBTransitionProofV1:
    dimension = 48 if modality == "AUDITORY" else 288 if modality == "VISUAL" else 0
    if dimension == 0 or type(ppb_inputs) is not tuple or type(recorded_prototypes) is not tuple:
        raise S2LJRunnerError("transition modality or container differs")
    if len(ppb_inputs) != 3 or len(recorded_prototypes) != 3:
        raise S2LJRunnerError("exactly three PPB transition steps are required")
    inputs = tuple(_numeric_tuple(item, dimension, "PPB input") for item in ppb_inputs)
    recorded = tuple(
        _numeric_tuple(item, dimension, "recorded PPB prototype")
        for item in recorded_prototypes
    )
    derived = (inputs[0],)
    derived += (_matched_update(derived[-1], inputs[1]),)
    derived += (_matched_update(derived[-1], inputs[2]),)
    if recorded != derived:
        raise S2LJRunnerError("recorded prototype differs from CREATED/MATCHED/MATCHED")
    masked = recorded[-1][24:] if modality == "AUDITORY" else recorded[-1][32:]
    payload = {
        "schema": S2LJ_TRANSITION_SCHEMA,
        "modality": modality,
        "dimension": dimension,
        "event_chain": list(EVENT_CHAIN),
        "support_chain": list(SUPPORT_CHAIN),
        "input_values": [list(item) for item in inputs],
        "recorded_prototype_values": [list(item) for item in recorded],
        "input_digests": [_digest(list(item)) for item in inputs],
        "prototype_digests": [_digest(list(item)) for item in recorded],
        "final_masked_digest": _digest(list(masked)),
        "integrity_status": "PPB_TRANSITION_INTEGRITY_VALID",
    }
    return S2LJPPBTransitionProofV1(
        modality,
        dimension,
        EVENT_CHAIN,
        SUPPORT_CHAIN,
        inputs,
        recorded,
        tuple(payload["input_digests"]),  # type: ignore[arg-type]
        tuple(payload["prototype_digests"]),  # type: ignore[arg-type]
        payload["final_masked_digest"],  # type: ignore[arg-type]
        "PPB_TRANSITION_INTEGRITY_VALID",
        _digest(payload),
    )


@dataclass(frozen=True, slots=True)
class S2LJCompletionV1:
    modality: str
    arm: str
    cue_digest: str
    retrieval_result_digest: str | None
    decision: str | None
    admitted_area: str | None
    input_values: tuple[float | None, ...]
    output_values: tuple[float | None, ...]
    completed_positions: tuple[int, ...]
    visible_unchanged: bool
    prestate_digest: str
    poststate_digest: str
    field_digest: str
    result_digest: str
    schema: str = S2LJ_COMPLETION_SCHEMA

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "modality": self.modality,
            "arm": self.arm,
            "cue_digest": self.cue_digest,
            "retrieval_result_digest": self.retrieval_result_digest,
            "decision": self.decision,
            "admitted_area": self.admitted_area,
            "input_values": list(self.input_values),
            "output_values": list(self.output_values),
            "completed_positions": list(self.completed_positions),
            "visible_unchanged": self.visible_unchanged,
            "prestate_digest": self.prestate_digest,
            "poststate_digest": self.poststate_digest,
            "field_digest": self.field_digest,
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_digest(), "result_digest": self.result_digest}


def _completion(
    *,
    modality: str,
    arm: str,
    cue,
    retrieval,
    state_digest: str,
    field_digest: str,
) -> S2LJCompletionV1:
    if modality == "AUDITORY":
        positions = auditory_scan.MASKED_BANDS
        visible = auditory_scan.OBSERVED_BANDS
        expected_area = "B_STABLE_AUDITORY"
    elif modality == "VISUAL":
        positions = visual_scan.MASKED_POSITIONS
        visible = visual_scan.VISIBLE_POSITIONS
        expected_area = "B_STABLE"
    else:
        raise S2LJRunnerError("completion modality differs")
    input_values = tuple(cue.values)
    output = list(input_values)
    retrieval_digest = None
    decision = None
    admitted = None
    completed: tuple[int, ...] = ()
    if arm != "CURRENT_PERCEPTION_ONLY":
        retrieval_digest = retrieval.result_digest
        decision = retrieval.decision
        hypothesis = retrieval.hypothesis
        admitted = None if hypothesis is None else hypothesis.area
        if decision == "ADMIT_SINGLE_CONTEXT":
            if hypothesis is None or admitted != expected_area:
                raise S2LJRunnerError("admitted hypothesis area differs")
            for position, value in zip(positions, hypothesis.proposed_values, strict=True):
                output[position] = value
            completed = positions
    output_values = tuple(output)
    unchanged = all(output_values[index] == input_values[index] for index in visible)
    payload = {
        "schema": S2LJ_COMPLETION_SCHEMA,
        "modality": modality,
        "arm": arm,
        "cue_digest": cue.cue_digest,
        "retrieval_result_digest": retrieval_digest,
        "decision": decision,
        "admitted_area": admitted,
        "input_values": list(input_values),
        "output_values": list(output_values),
        "completed_positions": list(completed),
        "visible_unchanged": unchanged,
        "prestate_digest": state_digest,
        "poststate_digest": state_digest,
        "field_digest": field_digest,
    }
    return S2LJCompletionV1(
        modality,
        arm,
        cue.cue_digest,
        retrieval_digest,
        decision,
        admitted,
        input_values,
        output_values,
        completed,
        unchanged,
        state_digest,
        state_digest,
        field_digest,
        _digest(payload),
    )


def _field_result(auditory_frames: tuple, visual_frames: tuple) -> dict[str, object]:
    profile = build_s2jw_default_live_profile()
    sequences = (
        ReceptorTimeSequence(
            "auditory",
            profile.profile.auditory_config.geometry_id,
            FIELD_CLOCK_ID,
            auditory_frames,
        ),
        ReceptorTimeSequence(
            "visual",
            profile.profile.visual_config.geometry_id,
            FIELD_CLOCK_ID,
            visual_frames,
        ),
    )
    end_tick = max(frame.field_time.window_end_tick for seq in sequences for frame in seq.frames)
    partition = partition_receptor_completion_time(
        sequences,
        horizon_start_tick=0,
        horizon_end_tick=end_tick,
        ticks_per_second=1_000_000_000.0,
    )
    steps = tuple(item.step_time for item in partition.slices)
    result = field_path.run_observed_field_pair(
        sequences,
        steps,
        field_path.s2jt_default_dock_anatomies(),
        expected_dock_count=336,
    )
    nontrivial = any(
        any(value != 0.0 for value in point.activation + point.afterimage)
        for point in result.trajectory
    )
    return {
        "group_count": len(result.trajectory),
        "event_count": result.handoff.source_event_count,
        "point_digests": [item.point_digest for item in result.trajectory],
        "observed_final_digest": result.observed_field.snapshot().digest(),
        "direct_final_digest": result.direct_run.field.snapshot().digest(),
        "initial_fields_distinct": result.initial_fields_distinct,
        "initial_fields_zero": result.initial_fields_zero,
        "final_components_equal": result.final_components_equal,
        "final_digests_equal": result.final_digests_equal,
        "nontrivial": nontrivial,
        "result_digest": result.result_digest,
    }


def _advance_one(
    config: memory.S2JVCoordinatorConfigV1,
    state: memory.S2JVCompositeStateV1,
    pair,
    ordinal: int,
):
    bound = memory.bind_s2jv_coordinator_input(config=config, source=pair)
    owner = memory.S2JVFormationOwner(
        f"s2lj-owner-{ordinal:03d}",
        f"s2lj-authorize-{ordinal:03d}",
        f"s2lj-consume-{ordinal:03d}",
        config.config_digest,
        state.state_digest,
        bound.input_digest,
    )
    return memory.advance_s2jv_atomic(
        config=config,
        prestate=state,
        source=bound,
        owner=owner,
    )


def _occupied_prototype(state: memory.S2JVCompositeStateV1, modality: str, support: int) -> tuple[float, ...]:
    bank = (
        state.tspm_state.auditory_ppb1_state
        if modality == "AUDITORY"
        else state.tspm_state.visual_ppb1_state
    )
    occupied = tuple(slot for slot in bank.slots if slot.occupied)
    if len(occupied) != 1 or occupied[0].support_count != support:
        raise S2LJRunnerError("PPB slot or support chain differs")
    return tuple(occupied[0].prototype_values)


def _formation_record(source, result) -> dict[str, object]:
    return {
        "source_id": source.source_id,
        "ordinal": source.ordinal,
        "source_digest": source.source_digest,
        "pairing_digest": source.pairing_digest,
        "auditory_values_digest": source.auditory_values_digest,
        "visual_values_digest": source.visual_values_digest,
        "formation_receipt_digest": result.receipt.receipt_digest,
        "formation_result_digest": result.result_digest,
        "prestate_digest": result.receipt.composite_prestate_digest,
        "poststate_digest": result.poststate.state_digest,
        "owner_status": result.owner_poststate.status,
    }


def _score(output: tuple[float | None, ...], target: tuple[float, ...], visible: tuple[int, ...]) -> dict[str, object]:
    visible_set = set(visible)
    errors = 0.0
    unresolved = 0
    for index, target_value in enumerate(target):
        value = output[index]
        if value is None:
            unresolved += 1
            errors += 1.0
        else:
            errors += abs(float(value) - target_value)
    return {
        "unresolved_count": unresolved,
        "visible_unchanged": all(output[index] is not None for index in visible_set),
        "loss": errors / len(target),
    }


def _evaluate(
    *,
    state: memory.S2JVCompositeStateV1,
    field: dict[str, object],
    transitions: tuple[S2LJPPBTransitionProofV1, ...],
    completions: tuple[S2LJCompletionV1, ...],
    auditory_target: tuple[float, ...],
    visual_target: tuple[float, ...],
) -> dict[str, object]:
    by_key = {(item.modality, item.arm): item for item in completions}
    scores = {
        "auditory_current": _score(
            by_key[("AUDITORY", "CURRENT_PERCEPTION_ONLY")].output_values,
            auditory_target,
            auditory_scan.OBSERVED_BANDS,
        ),
        "auditory_plus": _score(
            by_key[("AUDITORY", "PLUS_ADMITTED_CONTEXT")].output_values,
            auditory_target,
            auditory_scan.OBSERVED_BANDS,
        ),
        "auditory_baseline": _score(
            by_key[("AUDITORY", "DIRECT_BASELINE")].output_values,
            auditory_target,
            auditory_scan.OBSERVED_BANDS,
        ),
        "visual_current": _score(
            by_key[("VISUAL", "CURRENT_PERCEPTION_ONLY")].output_values,
            visual_target,
            visual_scan.VISIBLE_POSITIONS,
        ),
        "visual_plus": _score(
            by_key[("VISUAL", "PLUS_ADMITTED_CONTEXT")].output_values,
            visual_target,
            visual_scan.VISIBLE_POSITIONS,
        ),
        "visual_baseline": _score(
            by_key[("VISUAL", "DIRECT_BASELINE")].output_values,
            visual_target,
            visual_scan.VISIBLE_POSITIONS,
        ),
    }
    target_absent_a = all(
        not slot.occupied
        or (
            tuple(slot.auditory_values) != auditory_target
            and tuple(slot.visual_values) != visual_target
        )
        for slot in state.tspm_state.fast_state.slots
    ) and all(
        not entry.occupied or tuple(entry.values) != auditory_target + visual_target
        for entry in state.b4_state.entries
    )
    completions_read_only = all(
        item.prestate_digest == item.poststate_digest == state.state_digest
        for item in completions
    )
    baseline_equal = (
        by_key[("AUDITORY", "PLUS_ADMITTED_CONTEXT")].output_values
        == by_key[("AUDITORY", "DIRECT_BASELINE")].output_values
        and by_key[("VISUAL", "PLUS_ADMITTED_CONTEXT")].output_values
        == by_key[("VISUAL", "DIRECT_BASELINE")].output_values
    )
    confirmed = (
        len(transitions) == 2
        and all(item.integrity_status == "PPB_TRANSITION_INTEGRITY_VALID" for item in transitions)
        and target_absent_a
        and all(
            by_key[(modality, arm)].visible_unchanged
            for modality in ("AUDITORY", "VISUAL")
            for arm in ("CURRENT_PERCEPTION_ONLY", "PLUS_ADMITTED_CONTEXT", "DIRECT_BASELINE")
        )
        and len(by_key[("AUDITORY", "PLUS_ADMITTED_CONTEXT")].completed_positions) == 24
        and len(by_key[("VISUAL", "PLUS_ADMITTED_CONTEXT")].completed_positions) == 256
        and scores["auditory_plus"]["loss"] < scores["auditory_current"]["loss"]
        and scores["visual_plus"]["loss"] < scores["visual_current"]["loss"]
        and baseline_equal
        and completions_read_only
        and field["group_count"] == MAIN_FIELD_GROUP_COUNT
        and field["final_digests_equal"] is True
        and field["nontrivial"] is True
    )
    payload = {
        "status": (
            "S2LJ_COHERENT_AV_MEMORY_CONTEXT_UTILITY_CONFIRMED"
            if confirmed
            else "S2LJ_FUNCTION_FALSIFIED"
        ),
        "scores": scores,
        "target_absent_from_a_recent": target_absent_a,
        "transition_integrity": all(
            item.integrity_status == "PPB_TRANSITION_INTEGRITY_VALID" for item in transitions
        ),
        "baseline_equal": baseline_equal,
        "all_read_only": completions_read_only,
        "field_unchanged_by_context": len({item.field_digest for item in completions}) == 1,
    }
    return {**payload, "evaluation_digest": _digest(payload)}


def _execute_main() -> dict[str, object]:
    config = _build_config()
    stream = S2LJSourceStream(config.profile, mode="MAIN")
    state = memory.initial_s2jv_composite_state(config)
    formations: list[dict[str, object]] = []
    auditory_frames = []
    visual_frames = []
    ppb_inputs = {"AUDITORY": [], "VISUAL": []}
    ppb_recorded = {"AUDITORY": [], "VISUAL": []}
    for ordinal in range(1, MAIN_FORMATION_COUNT + 1):
        pair, source = stream.materialize_next_formation()
        auditory_frames.append(pair.auditory.timed_frame)
        visual_frames.append(pair.visual.timed_frame)
        result = _advance_one(config, state, pair, ordinal)
        state = result.poststate
        formations.append(_formation_record(source, result))
        if ordinal in (2, 3, 4):
            ppb_inputs["AUDITORY"].append(tuple(pair.auditory.timed_frame.frame.values))
            ppb_inputs["VISUAL"].append(tuple(pair.visual.timed_frame.frame.values))
            support = ordinal - 1
            ppb_recorded["AUDITORY"].append(_occupied_prototype(state, "AUDITORY", support))
            ppb_recorded["VISUAL"].append(_occupied_prototype(state, "VISUAL", support))
    transitions = tuple(
        derive_ppb_transition_proof(
            modality=modality,
            ppb_inputs=tuple(ppb_inputs[modality]),
            recorded_prototypes=tuple(ppb_recorded[modality]),
        )
        for modality in ("AUDITORY", "VISUAL")
    )
    band_plan = auditory_scan.build_auditory_band_plan_48()
    auditory_cue, auditory_timed, auditory_source = stream.materialize_auditory_cue(
        config_digest=config.config_digest,
        band_plan=band_plan,
    )
    visual_cue, visual_timed, visual_source = stream.materialize_visual_cue(
        config_digest=config.config_digest,
    )
    auditory_frames.append(auditory_timed)
    visual_frames.append(visual_timed)
    field = _field_result(tuple(auditory_frames), tuple(visual_frames))
    field_digest = field["observed_final_digest"]
    state_before = state.state_digest
    auditory_primary = auditory_scan.form_auditory_partial_cue_retrieval_336(
        config=config,
        state=state,
        cue=auditory_cue,
        band_plan=band_plan,
    )
    auditory_direct = auditory_baseline.form_direct_auditory_slot_scan_baseline_336(
        config=config,
        state=state,
        cue=auditory_cue,
        band_plan=band_plan,
    )
    visual_primary = visual_scan.form_partial_cue_retrieval_336(
        config=config,
        state=state,
        cue=visual_cue,
    )
    visual_direct = visual_baseline.form_direct_partial_cue_slot_scan_baseline_336(
        config=config,
        state=state,
        cue=visual_cue,
    )
    completions = (
        _completion(
            modality="AUDITORY",
            arm="CURRENT_PERCEPTION_ONLY",
            cue=auditory_cue,
            retrieval=None,
            state_digest=state.state_digest,
            field_digest=field_digest,
        ),
        _completion(
            modality="AUDITORY",
            arm="PLUS_ADMITTED_CONTEXT",
            cue=auditory_cue,
            retrieval=auditory_primary,
            state_digest=state.state_digest,
            field_digest=field_digest,
        ),
        _completion(
            modality="AUDITORY",
            arm="DIRECT_BASELINE",
            cue=auditory_cue,
            retrieval=auditory_direct,
            state_digest=state.state_digest,
            field_digest=field_digest,
        ),
        _completion(
            modality="VISUAL",
            arm="CURRENT_PERCEPTION_ONLY",
            cue=visual_cue,
            retrieval=None,
            state_digest=state.state_digest,
            field_digest=field_digest,
        ),
        _completion(
            modality="VISUAL",
            arm="PLUS_ADMITTED_CONTEXT",
            cue=visual_cue,
            retrieval=visual_primary,
            state_digest=state.state_digest,
            field_digest=field_digest,
        ),
        _completion(
            modality="VISUAL",
            arm="DIRECT_BASELINE",
            cue=visual_cue,
            retrieval=visual_direct,
            state_digest=state.state_digest,
            field_digest=field_digest,
        ),
    )
    if state.state_digest != state_before:
        raise S2LJRunnerError("read-only context path changed memory")
    auditory_target, visual_target = stream.evaluation_targets()
    evaluation = _evaluate(
        state=state,
        field=field,
        transitions=transitions,
        completions=completions,
        auditory_target=auditory_target,
        visual_target=visual_target,
    )
    return {
        "config_digest": config.config_digest,
        "formations": formations,
        "transitions": [item.payload() for item in transitions],
        "field": field,
        "cue_sources": [
            {**auditory_source.payload_without_digest(), "source_digest": auditory_source.source_digest},
            {**visual_source.payload_without_digest(), "source_digest": visual_source.source_digest},
        ],
        "scan_results": {
            "auditory_primary": auditory_primary.result_digest,
            "auditory_baseline": auditory_direct.result_digest,
            "visual_primary": visual_primary.result_digest,
            "visual_baseline": visual_direct.result_digest,
        },
        "completions": [item.payload() for item in completions],
        "final_memory_digest": state.state_digest,
        "evaluation": evaluation,
    }


def neutral_qualification_record(workspace_root: Path) -> dict[str, object]:
    config = _build_config()
    stream = S2LJSourceStream(config.profile, mode="QUALIFICATION")
    pair, source = stream.materialize_next_formation()
    initial = memory.initial_s2jv_composite_state(config)
    result = _advance_one(config, initial, pair, 1)
    field = _field_result((pair.auditory.timed_frame,), (pair.visual.timed_frame,))
    auditory = tuple(pair.auditory.timed_frame.frame.values)
    visual = tuple(pair.visual.timed_frame.frame.values)
    audio_chain = (auditory, _matched_update(auditory, auditory))
    audio_chain += (_matched_update(audio_chain[-1], auditory),)
    visual_chain = (visual, _matched_update(visual, visual))
    visual_chain += (_matched_update(visual_chain[-1], visual),)
    transitions = (
        derive_ppb_transition_proof(
            modality="AUDITORY",
            ppb_inputs=(auditory, auditory, auditory),
            recorded_prototypes=audio_chain,
        ),
        derive_ppb_transition_proof(
            modality="VISUAL",
            ppb_inputs=(visual, visual, visual),
            recorded_prototypes=visual_chain,
        ),
    )
    payload = {
        "schema": S2LJ_RESULT_SCHEMA,
        "mode": "QUALIFICATION",
        "run_id": "s2lj-neutral-qualification-record",
        "technical_status": "RECORDING_COMPLETE",
        "source_hashes": source_hashes(workspace_root),
        "plan": {
            "main_execution_enabled": MAIN_EXECUTION_ENABLED,
            "main_authorized_run_id": AUTHORIZED_RUN_ID,
            "formation_count": 1,
            "field_group_count": 1,
            "main_story_executed": False,
            "raw_payload_retained": False,
        },
        "config_digest": config.config_digest,
        "formations": [_formation_record(source, result)],
        "transitions": [item.payload() for item in transitions],
        "field": field,
        "cue_sources": [],
        "scan_results": {},
        "completions": [],
        "final_memory_digest": result.poststate.state_digest,
        "evaluation": None,
    }
    return {**payload, "record_digest": _digest(payload)}


def _main_plan() -> dict[str, object]:
    return {
        "formation_count": MAIN_FORMATION_COUNT,
        "field_group_count": MAIN_FIELD_GROUP_COUNT,
        "auditory_partial_cue_count": 1,
        "visual_partial_cue_count": 1,
        "full_probe_count": 0,
        "completion_arm_count": 6,
        "field_contacts_per_arm": MAIN_FIELD_CONTACTS_PER_ARM,
        "maximum_functional_operations": MAIN_MAX_FUNCTIONAL_OPERATIONS,
        "streamed_raw_bytes": MAIN_RAW_BYTES,
        "raw_payload_retained": False,
        "automatic_context_ranking": False,
        "field_feedback": False,
    }


def write_atomic_result(directory: Path, record: dict[str, object]) -> Path:
    if not isinstance(directory, Path) or not directory.is_absolute() or directory.exists():
        raise S2LJRunnerError("result directory must be one new absolute Path")
    data = _canonical_bytes(record, newline=True)
    if len(data) > MAX_RESULT_BYTES:
        raise S2LJRunnerError("result exceeds the bounded atomic envelope")
    directory.mkdir(parents=True, exist_ok=False)
    pending = directory / ".result.json.pending"
    target = directory / "result.json"
    with pending.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(pending, target)
    return target


def run_main_once(output_root: Path, workspace_root: Path, run_id: str) -> Path:
    global MAIN_EXECUTION_ENABLED
    if not MAIN_EXECUTION_ENABLED:
        raise S2LJRunnerError("S2-LJ main execution gate is closed")
    try:
        if AUTHORIZED_RUN_ID is None or run_id != AUTHORIZED_RUN_ID or _RUN_ID.fullmatch(run_id) is None:
            raise S2LJRunnerError("run_id is not authorized for S2-LJ")
        if not isinstance(output_root, Path) or not output_root.is_absolute():
            raise S2LJRunnerError("output_root must be one absolute Path")
        sources = source_hashes(workspace_root)
        try:
            execution = _execute_main()
            technical_status = "RECORDING_COMPLETE"
            failure_code = None
        except Exception:
            execution = None
            technical_status = "NOT_EVALUABLE"
            failure_code = "S2LJ_EXECUTION_FAILED"
        payload = {
            "schema": S2LJ_RESULT_SCHEMA,
            "mode": "MAIN",
            "run_id": run_id,
            "technical_status": technical_status,
            "failure_code": failure_code,
            "source_hashes": sources,
            "plan": _main_plan(),
            "execution": execution,
        }
        record = {**payload, "record_digest": _digest(payload)}
        return write_atomic_result(output_root / run_id, record).parent
    finally:
        MAIN_EXECUTION_ENABLED = False


__all__: tuple[str, ...] = ()
