"""Private locked runner for retention, consolidation, and capacity pressure.

The main execution gate is intentionally closed. This module materializes the
bound 146/170/16/316/1296 run, but it is not a command-line entry point and it
does not run during import.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path

import numpy as np

from mcm_field_organism import _tspm1_private as tspm1
from mcm_field_organism import _tspm1_s2dr_private_comparison as comparison
from mcm_field_organism._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    bind_ppb1_active_receptor_batch,
)
from mcm_field_organism._ppb1_receptor_profiles import (
    PPB1ModalityParameters,
    PPB1ProfileParameters,
    bind_ppb1_receptor_profile,
)
from mcm_field_organism.browser_receptor_bridge import BrowserReceptorSequenceBatch
from mcm_field_organism.browser_world_contract import BrowserWorldContract, BrowserWorldPhase
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import CommonFieldTime, ReceptorContactFrame
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame, ReceptorTimeSequence
from tools import _retention_capacity_fixtures as fixtures
from tools import _retention_capacity_read_only as read_only
from tools._retention_capacity_recording import (
    PrivateEvidenceRecorder,
    RecordingPlan,
    digest,
    file_digest,
)


RUNNER_SCHEMA = "retention.capacity.private.runner.v1"
EXPERIMENT_ID = "retention.capacity.functional.v1"
MAIN_EXECUTION_ENABLED = False

_PROFILE_PARAMETERS = PPB1ProfileParameters(
    PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
    PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
)
_VISUAL_CONFIG = VisualGridConfig(120, 80, 3, 2, 30.0)
_EXPECTED_COUNTS = (146, 170, 16, 316, 1296)


class RetentionCapacityRunnerError(RuntimeError):
    """One technical or method boundary violation."""


@dataclass(frozen=True, slots=True)
class _BoundPerceptualInput:
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    av_values: tuple[float, ...]
    envelope: PPB1ActiveReceptorBatchEnvelope
    source_digest: str
    values_digest: str
    image_event_digest: str


@dataclass(slots=True)
class _RunContext:
    recorder: PrivateEvidenceRecorder
    profile: object
    tspm_config: tspm1.TSPM1ConfigBinding
    world: BrowserWorldContract
    receptor: LocalChannelGridReceptor
    image_serial: int = 0


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise RetentionCapacityRunnerError(message)


def _profile_and_config():
    profile = bind_ppb1_receptor_profile("browser", _PROFILE_PARAMETERS)
    config = tspm1.TSPM1ConfigBinding.build(
        tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        profile,
    )
    return profile, config


def _world() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="synthetic.retention.capacity.world.v1",
        startup_frame_count=1,
        start_lead_ns=1,
        movement_cycles=1,
        tone_frequency_hz=100.0,
        phases=(
            BrowserWorldPhase("rest.before", 10, "static", 0.0),
            BrowserWorldPhase("change", 10, "moving", 0.2),
            BrowserWorldPhase("rest.after", 10, "static", 0.0),
        ),
    )


def _source_paths() -> tuple[tuple[str, Path], ...]:
    root = Path(__file__).resolve().parents[1]
    return (
        ("fixture.source", root / "tools" / "_retention_capacity_fixtures.py"),
        ("read.only.adapter.source", root / "tools" / "_retention_capacity_read_only.py"),
        ("runner.source", root / "tools" / "_retention_capacity_runner.py"),
        ("recording.source", root / "tools" / "_retention_capacity_recording.py"),
        ("verifier.source", root / "tools" / "_retention_capacity_result_verifier.py"),
        ("b4.source", root / "mcm_field_organism" / "_tspm1_s2dr_private_comparison.py"),
        ("tspm1.source", root / "mcm_field_organism" / "_tspm1_private.py"),
        ("ppb1.source", root / "mcm_field_organism" / "_ppb1_reference.py"),
        ("visual.receptor.source", root / "mcm_field_organism" / "finite_video_path.py"),
    )


def _configuration_payload() -> dict[str, object]:
    return {
        "schema": RUNNER_SCHEMA,
        "fixture_schema": fixtures.FIXTURE_SCHEMA,
        "adapter_schema": read_only.ADAPTER_SCHEMA,
        "stories": [story.story_id for story in fixtures.STORIES],
        "arms": ["B4", "TSPM1"],
        "budgets": fixtures.BUDGET,
        "profile_parameters": _PROFILE_PARAMETERS,
        "fast_config": {
            "capacity": 3,
            "auditory_match_threshold": 0.2,
            "visual_match_threshold": 0.2,
            "update_rate": 0.5,
            "consolidate_after": 2,
            "expire_after_exposures": 8,
        },
        "functional_thresholds": {
            "auditory": [
                fixtures.FUNCTIONAL_AUDITORY_THRESHOLD.numerator,
                fixtures.FUNCTIONAL_AUDITORY_THRESHOLD.denominator,
            ],
            "visual": [
                fixtures.FUNCTIONAL_VISUAL_THRESHOLD.numerator,
                fixtures.FUNCTIONAL_VISUAL_THRESHOLD.denominator,
            ],
        },
        "functional_scoring": None,
    }


def materialize_recording_plan(run_id: str) -> RecordingPlan:
    """Bind source bytes and the exact scope without invoking memory functions."""

    source_digests = tuple((role, file_digest(path)) for role, path in _source_paths())
    return RecordingPlan(
        run_id,
        EXPERIMENT_ID,
        source_digests,
        digest(_configuration_payload()),
    )


def _image_array(pattern: fixtures.PatternFixture) -> np.ndarray:
    cells = np.asarray(pattern.cell_values, dtype=np.uint8).reshape(2, 3)
    image = np.repeat(np.repeat(cells, 40, axis=0), 40, axis=1)
    image = np.repeat(image[:, :, None], 3, axis=2)
    image.setflags(write=False)
    return image


def _timed_sequence(frame: ReceptorContactFrame, field_time: CommonFieldTime) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        frame.modality_id,
        frame.geometry_id,
        field_time.clock_id,
        (OrganismTimedReceptorFrame(frame, field_time),),
    )


def _analyze_input(
    context: _RunContext,
    *,
    arm_id: str,
    story_id: str,
    phase: str,
    operation_ordinal: int,
    window_start: int,
    window_end: int,
    pattern: fixtures.PatternFixture,
) -> _BoundPerceptualInput:
    metadata = {
        "arm_id": arm_id,
        "story_id": story_id,
        "phase": phase,
        "operation_ordinal": operation_ordinal,
        "pattern_id": pattern.pattern_id,
        "window_start_tick": window_start,
        "window_end_tick": window_end,
    }
    start_digest = context.recorder.emit(
        "IMAGE_ANALYSIS_START",
        {"experiment_metadata": metadata, "raw_payload_retained": False},
    )
    image = _image_array(pattern)
    raw_sha256 = hashlib.sha256(image.tobytes()).hexdigest()
    receptor_state = context.receptor.analyze(image, frame_index=context.image_serial)
    context.image_serial += 1
    visual_values = tuple(receptor_state.channel_values)
    auditory_values = tuple(0.0 for _ in context.profile.auditory_config.carrier_ids)
    _require(visual_values == pattern.visual_values, "visual receptor changed fixture values")
    _require(auditory_values == pattern.auditory_values, "auditory fixture values differ")

    stem = f"retention.{arm_id.lower()}.{story_id.lower()}.{phase}.{operation_ordinal:03d}"
    auditory_frame = ReceptorContactFrame(
        "auditory",
        context.profile.auditory_config.geometry_id,
        f"{stem}.auditory",
        "retention.capacity.auditory.clock",
        window_start,
        window_end,
        context.profile.auditory_config.carrier_ids,
        auditory_values,
    )
    visual_frame = ReceptorContactFrame(
        "visual",
        context.profile.visual_config.geometry_id,
        f"{stem}.visual",
        "retention.capacity.visual.clock",
        window_start,
        window_end,
        context.profile.visual_config.carrier_ids,
        visual_values,
    )
    field_time = CommonFieldTime("retention.capacity.field.clock", window_start, window_end)
    batch = BrowserReceptorSequenceBatch(
        context.world.contract_id,
        context.world.digest(),
        (
            _timed_sequence(auditory_frame, field_time),
            _timed_sequence(visual_frame, field_time),
        ),
    )
    envelope = bind_ppb1_active_receptor_batch(
        f"{stem}.binding",
        context.world,
        batch,
        context.profile,
    )
    values = auditory_values + visual_values
    values_digest = digest({"auditory": auditory_values, "visual": visual_values})
    result_digest = context.recorder.emit(
        "IMAGE_ANALYSIS_RESULT",
        {
            "experiment_metadata": metadata,
            "start_event_digest": start_digest,
            "raw_image_sha256": raw_sha256,
            "raw_payload_retained": False,
            "receptor_state": receptor_state.canonical_payload(),
            "auditory_frame": {
                "snapshot_id": auditory_frame.snapshot_id,
                "clock_id": auditory_frame.clock_id,
                "window_start_tick": auditory_frame.window_start_tick,
                "window_end_tick": auditory_frame.window_end_tick,
                "carrier_ids": auditory_frame.carrier_ids,
                "values": auditory_frame.values,
            },
            "visual_frame": {
                "snapshot_id": visual_frame.snapshot_id,
                "clock_id": visual_frame.clock_id,
                "window_start_tick": visual_frame.window_start_tick,
                "window_end_tick": visual_frame.window_end_tick,
                "carrier_ids": visual_frame.carrier_ids,
                "values": visual_frame.values,
            },
            "source_envelope_digest": envelope.envelope_digest,
            "values_digest": values_digest,
            "costs": {
                "image_bytes": int(image.nbytes),
                "receptor_channel_samples": int(image.size),
                "retained_raw_bytes": 0,
            },
        },
    )
    return _BoundPerceptualInput(
        auditory_values,
        visual_values,
        values,
        envelope,
        envelope.envelope_digest,
        values_digest,
        result_digest,
    )


def _fresh_b4_state() -> comparison._B4State:
    return comparison._B4State(
        0,
        tuple(
            comparison._FIFOEntry(f"b4.slot.{index:03d}", False, (), None)
            for index in range(9)
        ),
    )


def _b4_snapshot(state: comparison._B4State) -> dict[str, object]:
    return {
        "state_digest": comparison._digest(comparison._canonical(state)),
        "accepted_count": state.accepted_count,
        "entries": [comparison._canonical(entry) for entry in state.entries],
    }


def _tspm_snapshot(state: tspm1.TSPM1CompositeState) -> dict[str, object]:
    return {
        "composite": state.canonical_payload(),
        "fast": state.fast_state.canonical_payload(),
        "auditory_slow": state.auditory_ppb1_state.canonical_payload(),
        "visual_slow": state.visual_ppb1_state.canonical_payload(),
    }


def _slow_transition(prestate, poststate) -> dict[str, object]:
    if prestate.accepted_step_count == poststate.accepted_step_count:
        return {"called": False, "event": "NOT_CALLED", "changed_slots": []}
    _require(
        poststate.accepted_step_count == prestate.accepted_step_count + 1,
        "PPB-1 generation changed by more than one",
    )
    changed = tuple(
        (before, after)
        for before, after in zip(prestate.slots, poststate.slots, strict=True)
        if before.canonical_payload() != after.canonical_payload()
    )
    selected = tuple(
        after
        for _, after in changed
        if after.occupied and after.last_selected_step == poststate.accepted_step_count
    )
    _require(len(selected) == 1, "PPB-1 transition has no unique selected slot")
    selected_slot = selected[0]
    before_selected = next(slot for slot in prestate.slots if slot.slot_id == selected_slot.slot_id)
    if not before_selected.occupied:
        event = "CREATED"
    elif (
        selected_slot.support_count == 1
        and selected_slot.prototype_values != before_selected.prototype_values
    ):
        event = "REPLACED"
    else:
        event = "MATCHED"
    return {
        "called": True,
        "event": event,
        "selected_slot_id": selected_slot.slot_id,
        "support_count": selected_slot.support_count,
        "stable": selected_slot.support_count is not None and selected_slot.support_count >= 3,
        "changed_slots": [
            {"pre": before.canonical_payload(), "post": after.canonical_payload()}
            for before, after in changed
        ],
    }


def _advance_b4(
    context: _RunContext,
    state: comparison._B4State,
    sample: _BoundPerceptualInput,
    *,
    story_id: str,
    step: int,
) -> comparison._B4State:
    before = _b4_snapshot(state)
    start = context.recorder.emit(
        "STATE_OPERATION_START",
        {
            "operation": "EXPOSURE",
            "arm_id": "B4",
            "story_id": story_id,
            "step": step,
            "source_digest": sample.source_digest,
            "values_digest": sample.values_digest,
            "image_event_digest": sample.image_event_digest,
            "prestate_digest": before["state_digest"],
            "operator_input": {"values": sample.av_values, "formation_index": state.accepted_count + 1},
        },
    )
    poststate, event, native_cost = comparison._advance_b4(
        state,
        sample.av_values,
        state.accepted_count + 1,
    )
    after = _b4_snapshot(poststate)
    context.recorder.emit(
        "STATE_OPERATION_RESULT",
        {
            "operation": "EXPOSURE",
            "arm_id": "B4",
            "story_id": story_id,
            "step": step,
            "start_event_digest": start,
            "prestate_digest": before["state_digest"],
            "poststate_digest": after["state_digest"],
            "transition": event,
            "prestate": before,
            "poststate": after,
            "native_cost": {"write_words": native_cost[0], "distance_terms": native_cost[1]},
            "functional_budget": {"write_words": 293, "distance_terms": 234},
        },
    )
    return poststate


def _advance_tspm1(
    context: _RunContext,
    state: tspm1.TSPM1CompositeState,
    sample: _BoundPerceptualInput,
    *,
    story: fixtures.StoryFixture,
    step: int,
) -> tspm1.TSPM1CompositeState:
    exposure = tspm1.bind_tspm1_exposure(
        context.tspm_config,
        sample.envelope,
        sample.envelope.auditory_stream.timed_frames[0],
        sample.envelope.visual_stream.timed_frames[0],
    )
    before = _tspm_snapshot(state)
    owner = tspm1.TSPM1CoordinatorOwner(
        f"retention.owner.{story.story_id.lower()}.{step:03d}",
        f"retention.authorization.{story.story_id.lower()}.{step:03d}",
        f"retention.consumption.{story.story_id.lower()}.{step:03d}",
        context.tspm_config.config_binding_digest,
        state.composite_state_digest,
        exposure.exposure_digest,
    )
    start = context.recorder.emit(
        "STATE_OPERATION_START",
        {
            "operation": "EXPOSURE",
            "arm_id": "TSPM1",
            "story_id": story.story_id,
            "step": step,
            "source_digest": sample.source_digest,
            "values_digest": sample.values_digest,
            "image_event_digest": sample.image_event_digest,
            "prestate_digest": state.composite_state_digest,
            "operator_input": {
                "config_binding_digest": context.tspm_config.config_binding_digest,
                "exposure_digest": exposure.exposure_digest,
            },
        },
    )
    result = owner.consume_once(context.tspm_config, state, exposure)
    poststate = result.poststate
    after = _tspm_snapshot(poststate)
    expected = story.fast_expectations[step - 1]
    context.recorder.emit(
        "STATE_OPERATION_RESULT",
        {
            "operation": "EXPOSURE",
            "arm_id": "TSPM1",
            "story_id": story.story_id,
            "step": step,
            "start_event_digest": start,
            "prestate_digest": state.composite_state_digest,
            "poststate_digest": poststate.composite_state_digest,
            "transition_receipt": result.receipt.canonical_payload(),
            "owner_poststate": result.owner_poststate.canonical_payload(),
            "result_digest": result.result_digest,
            "prestate": before,
            "poststate": after,
            "auditory_slow_transition": _slow_transition(
                state.auditory_ppb1_state, poststate.auditory_ppb1_state
            ),
            "visual_slow_transition": _slow_transition(
                state.visual_ppb1_state, poststate.visual_ppb1_state
            ),
            "evaluation_metadata": {
                "expected_primary_event": expected.primary_event,
                "expected_ppb_calls_per_modality_after_step": expected.ppb_calls_per_modality_after_step,
                "expected_expired_pattern_ids": expected.expired_pattern_ids,
                "expected_replaced_pattern_id": expected.replaced_pattern_id,
                "expected_visual_slow_replaced_pattern_id": expected.visual_slow_replaced_pattern_id,
            },
            "functional_budget": {"write_words": 293, "distance_terms": 234},
        },
    )
    return poststate


def _probe_b4(
    context: _RunContext,
    state: comparison._B4State,
    sample: _BoundPerceptualInput,
    *,
    story_id: str,
    checkpoint: int,
    probe_ordinal: int,
) -> read_only.B4ContentFinding:
    before = comparison._digest(comparison._canonical(state))
    start = context.recorder.emit(
        "STATE_OPERATION_START",
        {
            "operation": "CONTENT_PROBE",
            "arm_id": "B4",
            "story_id": story_id,
            "checkpoint": checkpoint,
            "probe_ordinal": probe_ordinal,
            "source_digest": sample.source_digest,
            "values_digest": sample.values_digest,
            "image_event_digest": sample.image_event_digest,
            "prestate_digest": before,
            "operator_input": {"values": sample.av_values},
        },
    )
    finding = read_only.probe_b4_content_read_only(state, sample.av_values)
    after = comparison._digest(comparison._canonical(state))
    _require(before == after == finding.prestate_digest == finding.poststate_digest, "B4 probe mutated state")
    context.recorder.emit(
        "STATE_OPERATION_RESULT",
        {
            "operation": "CONTENT_PROBE",
            "arm_id": "B4",
            "story_id": story_id,
            "checkpoint": checkpoint,
            "probe_ordinal": probe_ordinal,
            "start_event_digest": start,
            "prestate_digest": before,
            "poststate_digest": after,
            "finding": finding,
            "probe_write_words": 0,
            "functional_distance_limit": 234,
        },
    )
    return finding


def _probe_tspm1(
    context: _RunContext,
    state: tspm1.TSPM1CompositeState,
    sample: _BoundPerceptualInput,
    *,
    story_id: str,
    checkpoint: int,
    probe_ordinal: int,
) -> read_only.TSPM1ContentFinding:
    probe = tspm1.bind_tspm1_probe(
        context.tspm_config,
        sample.envelope,
        sample.envelope.auditory_stream.timed_frames[0],
        sample.envelope.visual_stream.timed_frames[0],
    )
    before = state.composite_state_digest
    start = context.recorder.emit(
        "STATE_OPERATION_START",
        {
            "operation": "CONTENT_PROBE",
            "arm_id": "TSPM1",
            "story_id": story_id,
            "checkpoint": checkpoint,
            "probe_ordinal": probe_ordinal,
            "source_digest": sample.source_digest,
            "values_digest": sample.values_digest,
            "image_event_digest": sample.image_event_digest,
            "prestate_digest": before,
            "operator_input": {
                "config_binding_digest": context.tspm_config.config_binding_digest,
                "probe_digest": probe.probe_digest,
            },
        },
    )
    finding = read_only.probe_tspm1_content_read_only(context.tspm_config, state, probe)
    after = state.composite_state_digest
    _require(before == after == finding.prestate_digest == finding.poststate_digest, "TSPM-1 probe mutated state")
    _require(
        finding.prestate_component_digests == finding.poststate_component_digests,
        "TSPM-1 component changed during probe",
    )
    context.recorder.emit(
        "STATE_OPERATION_RESULT",
        {
            "operation": "CONTENT_PROBE",
            "arm_id": "TSPM1",
            "story_id": story_id,
            "checkpoint": checkpoint,
            "probe_ordinal": probe_ordinal,
            "start_event_digest": start,
            "prestate_digest": before,
            "poststate_digest": after,
            "prestate_component_digests": finding.prestate_component_digests,
            "poststate_component_digests": finding.poststate_component_digests,
            "finding": finding,
            "probe_write_words": 0,
            "functional_distance_limit": 234,
        },
    )
    return finding


def _emit_sequence_status(
    context: _RunContext,
    *,
    arm_id: str,
    story_id: str,
    checkpoint: int,
    state_digest: str,
    probe_value_digests: tuple[str, ...],
    findings: tuple[object, ...],
) -> None:
    start = context.recorder.emit(
        "SEQUENCE_STATUS_START",
        {
            "arm_id": arm_id,
            "story_id": story_id,
            "checkpoint": checkpoint,
            "state_digest": state_digest,
            "probe_value_digests": probe_value_digests,
            "history_input": None,
        },
    )
    if arm_id == "TSPM1":
        status = "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE"
        ordered_value_digests: tuple[str, ...] = ()
        functional_distance_terms = 0
    else:
        b4_findings = tuple(finding for finding in findings if type(finding) is read_only.B4ContentFinding)
        selected = tuple(finding.selected for finding in b4_findings)
        valid = (
            len(b4_findings) == 4
            and all(item is not None for item in selected)
            and len({item.slot_id for item in selected if item is not None}) == 4
            and len({item.formation_index for item in selected if item is not None}) == 4
        )
        if valid:
            indexed = tuple(
                (item.formation_index, value_digest)
                for item, value_digest in zip(selected, probe_value_digests, strict=True)
                if item is not None
            )
            ordered_value_digests = tuple(value for _, value in sorted(indexed))
            status = "ORDER_RECONSTRUCTED"
            functional_distance_terms = 416
        else:
            ordered_value_digests = ()
            status = "ORDER_UNAVAILABLE_MISSING_OR_AMBIGUOUS_CONTENT"
            functional_distance_terms = 416
    context.recorder.emit(
        "SEQUENCE_STATUS_RESULT",
        {
            "arm_id": arm_id,
            "story_id": story_id,
            "checkpoint": checkpoint,
            "start_event_digest": start,
            "prestate_digest": state_digest,
            "poststate_digest": state_digest,
            "status": status,
            "ordered_probe_value_digests": ordered_value_digests,
            "functional_distance_terms": functional_distance_terms,
            "validation_distance_limit": 416 if arm_id == "B4" else 0,
            "state_transition_called": False,
        },
    )


def _execute_story_arm(context: _RunContext, arm_id: str, story: fixtures.StoryFixture) -> str:
    if arm_id == "B4":
        state: object = _fresh_b4_state()
    else:
        state = tspm1.initial_tspm1_composite_state(context.tspm_config)
    checkpoint_map = {checkpoint.after_step: checkpoint for checkpoint in story.checkpoints}
    probe_ordinal = 0
    for exposure in story.exposures:
        pattern = fixtures.pattern_fixture(exposure.pattern_id)
        sample = _analyze_input(
            context,
            arm_id=arm_id,
            story_id=story.story_id,
            phase="exposure",
            operation_ordinal=exposure.step,
            window_start=exposure.window_start_tick,
            window_end=exposure.window_end_tick,
            pattern=pattern,
        )
        if arm_id == "B4":
            state = _advance_b4(context, state, sample, story_id=story.story_id, step=exposure.step)
        else:
            state = _advance_tspm1(context, state, sample, story=story, step=exposure.step)

        checkpoint = checkpoint_map.get(exposure.step)
        if checkpoint is None:
            continue
        checkpoint_findings = []
        checkpoint_value_digests = []
        for target_id in checkpoint.target_pattern_ids:
            probe_ordinal += 1
            target = fixtures.pattern_fixture(target_id)
            probe_tick = 1000 + exposure.step * 100 + probe_ordinal
            probe_sample = _analyze_input(
                context,
                arm_id=arm_id,
                story_id=story.story_id,
                phase="probe",
                operation_ordinal=probe_ordinal,
                window_start=probe_tick,
                window_end=probe_tick + 1,
                pattern=target,
            )
            if arm_id == "B4":
                finding = _probe_b4(
                    context,
                    state,
                    probe_sample,
                    story_id=story.story_id,
                    checkpoint=exposure.step,
                    probe_ordinal=probe_ordinal,
                )
            else:
                finding = _probe_tspm1(
                    context,
                    state,
                    probe_sample,
                    story_id=story.story_id,
                    checkpoint=exposure.step,
                    probe_ordinal=probe_ordinal,
                )
            checkpoint_findings.append(finding)
            checkpoint_value_digests.append(probe_sample.values_digest)
        if story.story_id in {"S1", "S2"}:
            state_digest = (
                comparison._digest(comparison._canonical(state))
                if arm_id == "B4"
                else state.composite_state_digest
            )
            _emit_sequence_status(
                context,
                arm_id=arm_id,
                story_id=story.story_id,
                checkpoint=exposure.step,
                state_digest=state_digest,
                probe_value_digests=tuple(checkpoint_value_digests),
                findings=tuple(checkpoint_findings),
            )
    return (
        comparison._digest(comparison._canonical(state))
        if arm_id == "B4"
        else state.composite_state_digest
    )


def _validate_bound_scope() -> None:
    exposures_per_arm = sum(story.exposure_count for story in fixtures.STORIES)
    probes_per_arm = sum(story.content_probe_count for story in fixtures.STORIES)
    sequence_per_arm = sum(len(story.checkpoints) for story in fixtures.STORIES if story.story_id in {"S1", "S2"})
    actual = (
        exposures_per_arm * 2,
        probes_per_arm * 2,
        sequence_per_arm * 2,
        (exposures_per_arm + probes_per_arm) * 2,
        (exposures_per_arm + probes_per_arm) * 8 + sequence_per_arm * 4,
    )
    _require(actual == _EXPECTED_COUNTS, "fixture materialization differs from bound scope")
    _require(
        actual
        == (
            fixtures.BUDGET.exposure_count_total,
            fixtures.BUDGET.content_probe_count_total,
            fixtures.BUDGET.sequence_status_count_total,
            fixtures.BUDGET.image_analysis_count_total,
            fixtures.BUDGET.event_count_total,
        ),
        "fixture budget and runner scope differ",
    )


def run_main_once(output_root: Path, run_id: str) -> Path:
    """Execute once only after a future explicit code-level gate change."""

    if MAIN_EXECUTION_ENABLED is not True:
        raise RetentionCapacityRunnerError("main execution gate is closed")
    _validate_bound_scope()
    plan = materialize_recording_plan(run_id)
    recorder = PrivateEvidenceRecorder(output_root, plan)
    try:
        profile, config = _profile_and_config()
        context = _RunContext(recorder, profile, config, _world(), LocalChannelGridReceptor(_VISUAL_CONFIG))
        terminal_states = {}
        for arm_id in ("B4", "TSPM1"):
            for story in fixtures.STORIES:
                terminal_states[f"{arm_id}.{story.story_id}"] = _execute_story_arm(context, arm_id, story)
        _require(
            tuple(recorder.event_counts.values()) == (316, 316, 316, 316, 16, 16),
            "recorded event inventory differs",
        )
        return recorder.finalize(
            {
                "runner_schema": RUNNER_SCHEMA,
                "terminal_state_digests": terminal_states,
                "image_analyses": context.image_serial,
                "functional_assessment": None,
                "labels_used_as_memory_input": False,
                "automatic_retry": False,
            }
        )
    except BaseException:
        recorder.leave_not_evaluable()
        raise
