"""Locked private S2-FV runner for the bound 18-step S2-FU history.

The runner materializes one future execution path but does not run on import.
Its main gate is closed. It never imports or calls the S2-FU evaluator and it
does not choose a preferred memory view.
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
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from tools import _retention_capacity_read_only as read_only
from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2fu_private_fixtures as fixtures
from tools import _visual_sequence_memory_probe as sequence_probe
from tools._s2fv_private_recording import (
    EVIDENCE_PACKAGE_SCHEMA,
    EXPECTED_EVENT_COUNTS,
    S2FVAppendOnlyRecorder,
    S2FVRecordingPlan,
    digest,
    file_digest,
)


RUNNER_SCHEMA = "s2fv.private.runner.v1"
EXPERIMENT_ID = "s2fv.private.functional.v1"
MAIN_EXECUTION_ENABLED = False
_EXPECTED_COUNTS = (24, 54, 18, 1, 6, 103, 206)
_PROFILE_PARAMETERS = PPB1ProfileParameters(
    PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
    PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
)
_VISUAL_CONFIG = VisualGridConfig(120, 80, 3, 2, 30.0)


class S2FVRunnerError(RuntimeError):
    """One technical or method boundary violation."""


@dataclass(frozen=True, slots=True)
class _BoundPerceptualSource:
    role: str
    fixture_id: str
    evaluation_pattern_id: str
    window_start_tick: int
    window_end_tick: int
    auditory_values: tuple[float, ...]
    visual_values: tuple[float, ...]
    av_values: tuple[float, ...]
    envelope: PPB1ActiveReceptorBatchEnvelope
    coordinator_source: coordinator.B4TSPM1BoundInput | coordinator.B4TSPM1BoundProbe
    source_digest: str
    auditory_fixture_binding_digest: str
    visual_analysis_digest: str
    receptor_result_event_digest: str


@dataclass(slots=True)
class _RunContext:
    recorder: S2FVAppendOnlyRecorder
    profile: object
    tspm_config: tspm1.TSPM1ConfigBinding
    coordinator_config: coordinator.B4TSPM1CoordinatorConfig
    world: BrowserWorldContract
    receptor: LocalChannelGridReceptor
    operation_index: int = 0
    image_serial: int = 0


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2FVRunnerError(message)


def _profile_and_configs():
    profile = bind_ppb1_receptor_profile("browser", _PROFILE_PARAMETERS)
    tspm_config = tspm1.TSPM1ConfigBinding.build(
        tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        profile,
    )
    coordinator_config = coordinator.build_coordinator_config(tspm_config)
    return profile, tspm_config, coordinator_config


def _world() -> BrowserWorldContract:
    return BrowserWorldContract(
        contract_id="synthetic.s2fv.world.v1",
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
        ("runner.source", root / "tools" / "_s2fv_private_runner.py"),
        ("recording.source", root / "tools" / "_s2fv_private_recording.py"),
        (
            "verifier.source",
            root / "tools" / "_s2fv_private_result_verifier.py",
        ),
        ("fixture.source", root / "tools" / "_s2fu_private_fixtures.py"),
        ("coordinator.source", root / "tools" / "_s2fs_b4_tspm1_private_coordinator.py"),
        ("content.adapter.source", root / "tools" / "_retention_capacity_read_only.py"),
        ("sequence.adapter.source", root / "tools" / "_visual_sequence_memory_probe.py"),
        ("b4.source", root / "mcm_field_organism" / "_tspm1_s2dr_private_comparison.py"),
        ("tspm1.source", root / "mcm_field_organism" / "_tspm1_private.py"),
        ("ppb1.source", root / "mcm_field_organism" / "_ppb1_reference.py"),
        ("visual.receptor.source", root / "mcm_field_organism" / "finite_video_path.py"),
    )


def _configuration_payload() -> dict[str, object]:
    return {
        "schema": RUNNER_SCHEMA,
        "experiment_id": EXPERIMENT_ID,
        "fixture_digest": fixtures.FIXTURE_DIGEST,
        "exposure_steps": [item.step for item in fixtures.EXPOSURES],
        "probe_ids": [item.probe_id for item in fixtures.PROBES],
        "arms": ["COMPOSITE", "B4", "TSPM1"],
        "views": ["B4_RECENT", "TSPM_FAST", "TSPM_SLOW"],
        "functional_visual_threshold": [44, 765],
        "native_tspm_threshold": [1, 5],
        "expected_counts": _EXPECTED_COUNTS,
        "automatic_view_selection": None,
        "functional_assessment": None,
    }


def materialize_recording_plan(run_id: str) -> S2FVRecordingPlan:
    """Bind exact source bytes without invoking a project state function."""

    source_digests = tuple((role, file_digest(path)) for role, path in _source_paths())
    return S2FVRecordingPlan(
        run_id,
        EXPERIMENT_ID,
        source_digests,
        digest(_configuration_payload()),
        fixtures.FIXTURE_DIGEST,
    )


def _start_operation(
    context: _RunContext,
    operation: str,
    operation_id: str,
    source_digest: str,
    payload: dict[str, object],
) -> str:
    _require(context.operation_index < 103, "operation budget exhausted")
    return context.recorder.emit(
        f"{operation}_START",
        {
            "operation_id": operation_id,
            "operation_index": context.operation_index,
            "source_digest": source_digest,
            **payload,
        },
    )


def _finish_operation(
    context: _RunContext,
    operation: str,
    operation_id: str,
    source_digest: str,
    start_event_digest: str,
    payload: dict[str, object],
) -> str:
    event_digest = context.recorder.emit(
        f"{operation}_RESULT",
        {
            "operation_id": operation_id,
            "operation_index": context.operation_index,
            "source_digest": source_digest,
            "start_event_digest": start_event_digest,
            **payload,
        },
    )
    context.operation_index += 1
    return event_digest


def _image_array(pattern: fixtures.S2FUPatternFixture) -> np.ndarray:
    cells = np.asarray(pattern.visual_cell_values, dtype=np.uint8).reshape(2, 3)
    image = np.repeat(np.repeat(cells, 40, axis=0), 40, axis=1)
    image = np.repeat(image[:, :, None], 3, axis=2)
    image.setflags(write=False)
    return image


def _timed_sequence(
    frame: ReceptorContactFrame,
    field_time: CommonFieldTime,
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        frame.modality_id,
        frame.geometry_id,
        field_time.clock_id,
        (OrganismTimedReceptorFrame(frame, field_time),),
    )


def _analyze_source(
    context: _RunContext,
    *,
    fixture_id: str,
    pattern_id: str,
    role: str,
    ordinal: int,
    window_start_tick: int,
    window_end_tick: int,
) -> _BoundPerceptualSource:
    pattern = fixtures.PATTERN_BY_ID[pattern_id]
    source_digest = digest(
        {
            "schema": RUNNER_SCHEMA,
            "fixture_digest": fixtures.FIXTURE_DIGEST,
            "fixture_id": fixture_id,
            "role": role,
            "ordinal": ordinal,
            "window_start_tick": window_start_tick,
            "window_end_tick": window_end_tick,
            "pattern_digest": pattern.pattern_digest,
        }
    )
    operation_id = f"s2fv.receptor-analysis.{ordinal:03d}"
    start = _start_operation(
        context,
        "RECEPTOR_ANALYSIS",
        operation_id,
        source_digest,
        {
            "role": role,
            "fixture_id": fixture_id,
            "evaluation_pattern_id": pattern_id,
            "raw_payload_retained": False,
        },
    )
    image = _image_array(pattern)
    raw_sha256 = hashlib.sha256(image.tobytes()).hexdigest()
    receptor_state = context.receptor.analyze(image, frame_index=context.image_serial)
    context.image_serial += 1
    visual_values = tuple(receptor_state.channel_values)
    auditory_values = tuple(float(value) for value in pattern.auditory_values)
    _require(visual_values == pattern.visual_values, "visual receptor changed fixture values")
    _require(len(auditory_values) == 8 and len(visual_values) == 18, "source dimensions differ")

    stem = f"s2fv.source.{ordinal:03d}"
    auditory_frame = ReceptorContactFrame(
        "auditory",
        context.profile.auditory_config.geometry_id,
        f"{stem}.auditory",
        "s2fv.auditory.clock",
        window_start_tick,
        window_end_tick,
        context.profile.auditory_config.carrier_ids,
        auditory_values,
    )
    visual_frame = ReceptorContactFrame(
        "visual",
        context.profile.visual_config.geometry_id,
        f"{stem}.visual",
        "s2fv.visual.clock",
        window_start_tick,
        window_end_tick,
        context.profile.visual_config.carrier_ids,
        visual_values,
    )
    field_time = CommonFieldTime(
        "s2fv.field.clock", window_start_tick, window_end_tick
    )
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
    auditory_binding = envelope.auditory_stream.timed_frames[0]
    visual_binding = envelope.visual_stream.timed_frames[0]
    if role == "FORMATION":
        bound = coordinator.bind_coordinator_input(
            context.coordinator_config,
            envelope,
            auditory_binding,
            visual_binding,
        )
        bound_digest = bound.input_digest
    elif role == "READ_ONLY":
        bound = coordinator.bind_coordinator_probe(
            context.coordinator_config,
            envelope,
            auditory_binding,
            visual_binding,
        )
        bound_digest = bound.probe_digest
    else:
        raise S2FVRunnerError("source role differs from the bound protocol")
    auditory_fixture_binding_digest = digest(
        {
            "fixture_id": fixture_id,
            "auditory_values": auditory_values,
            "timed_frame_digest": auditory_binding.timed_frame_provenance_digest,
        }
    )
    visual_analysis_digest = digest(
        {
            "fixture_id": fixture_id,
            "raw_image_sha256": raw_sha256,
            "receptor_values": visual_values,
            "timed_frame_digest": visual_binding.timed_frame_provenance_digest,
        }
    )
    result_event = _finish_operation(
        context,
        "RECEPTOR_ANALYSIS",
        operation_id,
        source_digest,
        start,
        {
            "role": role,
            "fixture_id": fixture_id,
            "evaluation_pattern_id": pattern_id,
            "window_start_tick": window_start_tick,
            "window_end_tick": window_end_tick,
            "raw_image_sha256": raw_sha256,
            "raw_payload_retained": False,
            "synthetic_auditory_receptor_values": auditory_values,
            "visual_receptor_values": visual_values,
            "auditory_fixture_binding_digest": auditory_fixture_binding_digest,
            "visual_analysis_digest": visual_analysis_digest,
            "source_envelope_digest": envelope.envelope_digest,
            "bound_source_digest": bound_digest,
            "costs": {
                "image_bytes": int(image.nbytes),
                "receptor_channel_samples": int(image.size),
                "retained_raw_bytes": 0,
            },
        },
    )
    return _BoundPerceptualSource(
        role,
        fixture_id,
        pattern_id,
        window_start_tick,
        window_end_tick,
        auditory_values,
        visual_values,
        auditory_values + visual_values,
        envelope,
        bound,
        source_digest,
        auditory_fixture_binding_digest,
        visual_analysis_digest,
        result_event,
    )


def _fresh_b4_state() -> comparison._B4State:
    return comparison._B4State(
        0,
        tuple(
            comparison._FIFOEntry(f"b4.slot.{index:03d}", False, (), None)
            for index in range(9)
        ),
    )


def _b4_digest(state: comparison._B4State) -> str:
    return comparison._digest(comparison._canonical(state))


def _composite_snapshot(state: coordinator.B4TSPM1CompositeState) -> dict[str, object]:
    return {
        "state_digest": state.state_digest,
        "generation": state.generation,
        "b4_state_digest": _b4_digest(state.b4_state),
        "tspm_state_digest": state.tspm_state.composite_state_digest,
    }


def _standalone_tspm_result(
    context: _RunContext,
    state: tspm1.TSPM1CompositeState,
    source: _BoundPerceptualSource,
    step: int,
) -> tspm1.TSPM1StepResult:
    _require(
        type(source.coordinator_source) is coordinator.B4TSPM1BoundInput,
        "formation source required",
    )
    exposure = source.coordinator_source.tspm_exposure
    owner = tspm1.TSPM1CoordinatorOwner(
        f"s2fv.tspm.owner.{step:03d}",
        f"s2fv.tspm.authorization.{step:03d}",
        f"s2fv.tspm.consumption.{step:03d}",
        context.tspm_config.config_binding_digest,
        state.composite_state_digest,
        exposure.exposure_digest,
    )
    return owner.consume_once(context.tspm_config, state, exposure)


def _form_composite(
    context: _RunContext,
    state: coordinator.B4TSPM1CompositeState,
    source: _BoundPerceptualSource,
    step: int,
) -> coordinator.B4TSPM1StepResult:
    _require(
        type(source.coordinator_source) is coordinator.B4TSPM1BoundInput,
        "composite formation requires one bound input",
    )
    operation_id = f"s2fv.formation.{step:03d}.composite"
    before = state.state_digest
    start = _start_operation(
        context,
        "FORMATION",
        operation_id,
        source.source_digest,
        {
            "arm": "COMPOSITE",
            "step": step,
            "prestate_digest": before,
            "bound_source_digest": source.coordinator_source.input_digest,
        },
    )
    owner = coordinator.B4TSPM1CoordinatorOwner(
        f"s2fv.composite.owner.{step:03d}",
        f"s2fv.composite.authorization.{step:03d}",
        f"s2fv.composite.consumption.{step:03d}",
        context.coordinator_config.config_digest,
        state.state_digest,
        source.coordinator_source.input_digest,
    )
    result = owner.consume_once(
        context.coordinator_config,
        state,
        source.coordinator_source,
    )
    _finish_operation(
        context,
        "FORMATION",
        operation_id,
        source.source_digest,
        start,
        {
            "arm": "COMPOSITE",
            "step": step,
            "prestate_digest": before,
            "poststate_digest": result.poststate.state_digest,
            "result": result,
            "component_snapshot": _composite_snapshot(result.poststate),
        },
    )
    return result


def _form_b4(
    context: _RunContext,
    state: comparison._B4State,
    source: _BoundPerceptualSource,
    step: int,
):
    operation_id = f"s2fv.formation.{step:03d}.b4"
    before = _b4_digest(state)
    start = _start_operation(
        context,
        "FORMATION",
        operation_id,
        source.source_digest,
        {
            "arm": "B4",
            "step": step,
            "prestate_digest": before,
            "bound_source_digest": source.coordinator_source.input_digest,
        },
    )
    poststate, event, native_cost = comparison._advance_b4(
        state,
        source.av_values,
        state.accepted_count + 1,
    )
    after = _b4_digest(poststate)
    _finish_operation(
        context,
        "FORMATION",
        operation_id,
        source.source_digest,
        start,
        {
            "arm": "B4",
            "step": step,
            "prestate_digest": before,
            "poststate_digest": after,
            "event": event,
            "native_cost": native_cost,
            "state": comparison._canonical(poststate),
        },
    )
    return poststate, event, native_cost


def _form_tspm(
    context: _RunContext,
    state: tspm1.TSPM1CompositeState,
    source: _BoundPerceptualSource,
    step: int,
) -> tspm1.TSPM1StepResult:
    operation_id = f"s2fv.formation.{step:03d}.tspm1"
    before = state.composite_state_digest
    start = _start_operation(
        context,
        "FORMATION",
        operation_id,
        source.source_digest,
        {
            "arm": "TSPM1",
            "step": step,
            "prestate_digest": before,
            "bound_source_digest": source.coordinator_source.input_digest,
        },
    )
    result = _standalone_tspm_result(context, state, source, step)
    _finish_operation(
        context,
        "FORMATION",
        operation_id,
        source.source_digest,
        start,
        {
            "arm": "TSPM1",
            "step": step,
            "prestate_digest": before,
            "poststate_digest": result.poststate.composite_state_digest,
            "result": result.canonical_payload(),
            "receipt": result.receipt.canonical_payload(),
            "state": result.poststate.canonical_payload(),
        },
    )
    return result


def _component_identity(
    context: _RunContext,
    composite_state: coordinator.B4TSPM1CompositeState,
    b4_state: comparison._B4State,
    tspm_state: tspm1.TSPM1CompositeState,
    source: _BoundPerceptualSource,
    step: int,
) -> dict[str, object]:
    operation_id = f"s2fv.component-identity.{step:03d}"
    start = _start_operation(
        context,
        "COMPONENT_IDENTITY",
        operation_id,
        source.source_digest,
        {"step": step, "composite_state_digest": composite_state.state_digest},
    )
    composite_b4 = _b4_digest(composite_state.b4_state)
    standalone_b4 = _b4_digest(b4_state)
    composite_tspm = composite_state.tspm_state.composite_state_digest
    standalone_tspm = tspm_state.composite_state_digest
    valid = (
        composite_state.generation == step
        and b4_state.accepted_count == step
        and tspm_state.generation == step
        and composite_b4 == standalone_b4
        and composite_tspm == standalone_tspm
    )
    payload = {
        "step": step,
        "identity_valid": valid,
        "composite_generation": composite_state.generation,
        "standalone_b4_generation": b4_state.accepted_count,
        "standalone_tspm_generation": tspm_state.generation,
        "composite_b4_state_digest": composite_b4,
        "standalone_b4_state_digest": standalone_b4,
        "composite_tspm_state_digest": composite_tspm,
        "standalone_tspm_state_digest": standalone_tspm,
        "prestate_digest": composite_state.state_digest,
        "poststate_digest": composite_state.state_digest,
    }
    result_digest = _finish_operation(
        context,
        "COMPONENT_IDENTITY",
        operation_id,
        source.source_digest,
        start,
        payload,
    )
    _require(valid, "composite component identity differs from standalone arms")
    return {**payload, "result_event_digest": result_digest}


def _slot_pattern_id(slot: tspm1.TSPM1FastSlot) -> str | None:
    if not slot.occupied:
        return None
    matches = tuple(
        pattern.pattern_id
        for pattern in fixtures.PATTERNS
        if slot.auditory_values
        == tuple(float(value) for value in pattern.auditory_values)
        and slot.visual_values == pattern.visual_values
    )
    return matches[0] if len(matches) == 1 else None


def _replaced_pattern_id(
    prestate: tspm1.TSPM1CompositeState,
    receipt: tspm1.TSPM1TransitionReceipt,
) -> str | None:
    if receipt.replaced_slot_digest is None:
        return None
    matches = tuple(
        _slot_pattern_id(slot)
        for slot in prestate.fast_state.slots
        if slot.digest() == receipt.replaced_slot_digest
    )
    return matches[0] if len(matches) == 1 else None


def _slow_supports(
    state: tspm1.TSPM1CompositeState,
    pattern_id: str,
) -> tuple[int, int]:
    pattern = fixtures.PATTERN_BY_ID[pattern_id]
    targets = (
        (
            state.auditory_ppb1_state,
            tuple(float(value) for value in pattern.auditory_values),
        ),
        (state.visual_ppb1_state, pattern.visual_values),
    )
    values = []
    for bank, target in targets:
        supports = tuple(
            slot.support_count
            for slot in bank.slots
            if slot.occupied and slot.prototype_values == target
        )
        _require(len(supports) <= 1, "slow support identity is ambiguous")
        values.append(supports[0] if supports else 0)
    return values[0], values[1]


def _sequence_read_only(
    context: _RunContext,
    composite_state: coordinator.B4TSPM1CompositeState,
    sources: tuple[_BoundPerceptualSource, ...],
) -> dict[str, object]:
    _require(len(sources) == 4, "four early sequence probes required")
    operation_id = "s2fv.sequence-probe.001"
    source_digest = digest([source.source_digest for source in sources])
    before = _b4_digest(composite_state.b4_state)
    start = _start_operation(
        context,
        "SEQUENCE_PROBE",
        operation_id,
        source_digest,
        {
            "checkpoint_after_step": 4,
            "prestate_digest": before,
            "probe_source_digests": [source.source_digest for source in sources],
            "source_view": "B4_RECENT",
        },
    )
    finding = sequence_probe.probe_visual_sequence_read_only(
        composite_state.b4_state,
        tuple(source.av_values for source in sources),
    )
    after = _b4_digest(composite_state.b4_state)
    _require(before == after, "sequence probe changed B4 state")
    result_event = _finish_operation(
        context,
        "SEQUENCE_PROBE",
        operation_id,
        source_digest,
        start,
        {
            "checkpoint_after_step": 4,
            "prestate_digest": before,
            "poststate_digest": after,
            "probe_source_digests": [source.source_digest for source in sources],
            "probe_fixture_ids": [source.fixture_id for source in sources],
            "finding": finding,
            "tspm_sequence_status": "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE",
            "automatic_view_selection": None,
        },
    )
    return {
        "checkpoint_after_step": 4,
        "prestate_digest": before,
        "poststate_digest": after,
        "probe_source_digests": tuple(source.source_digest for source in sources),
        "probe_fixture_ids": tuple(source.fixture_id for source in sources),
        "finding": finding,
        "tspm_sequence_status": "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE",
        "result_event_digest": result_event,
    }


def _content_probe(
    context: _RunContext,
    arm: str,
    composite_state: coordinator.B4TSPM1CompositeState,
    b4_state: comparison._B4State,
    tspm_state: tspm1.TSPM1CompositeState,
    source: _BoundPerceptualSource,
    ordinal: int,
) -> dict[str, object]:
    _require(
        type(source.coordinator_source) is coordinator.B4TSPM1BoundProbe,
        "content probe requires one bound probe",
    )
    operation_id = f"s2fv.content-probe.{ordinal:02d}.{arm.lower()}"
    if arm == "COMPOSITE":
        before = composite_state.state_digest
    elif arm == "B4":
        before = _b4_digest(b4_state)
    elif arm == "TSPM1":
        before = tspm_state.composite_state_digest
    else:
        raise S2FVRunnerError("unknown content arm")
    start = _start_operation(
        context,
        "CONTENT_PROBE",
        operation_id,
        source.source_digest,
        {
            "arm": arm,
            "probe_fixture_id": source.fixture_id,
            "evaluation_pattern_id": source.evaluation_pattern_id,
            "prestate_digest": before,
        },
    )
    if arm == "COMPOSITE":
        finding = coordinator.probe_composite_read_only(
            context.coordinator_config,
            composite_state,
            source.coordinator_source,
        )
        after = composite_state.state_digest
    elif arm == "B4":
        finding = read_only.probe_b4_content_read_only(b4_state, source.av_values)
        after = _b4_digest(b4_state)
    else:
        finding = read_only.probe_tspm1_content_read_only(
            context.tspm_config,
            tspm_state,
            source.coordinator_source.tspm_probe,
        )
        after = tspm_state.composite_state_digest
    _require(before == after, "content probe changed source state")
    result_event = _finish_operation(
        context,
        "CONTENT_PROBE",
        operation_id,
        source.source_digest,
        start,
        {
            "arm": arm,
            "probe_fixture_id": source.fixture_id,
            "evaluation_pattern_id": source.evaluation_pattern_id,
            "prestate_digest": before,
            "poststate_digest": after,
            "finding": finding,
            "automatic_view_selection": None,
        },
    )
    return {
        "arm": arm,
        "probe_fixture_id": source.fixture_id,
        "evaluation_pattern_id": source.evaluation_pattern_id,
        "prestate_digest": before,
        "poststate_digest": after,
        "finding": finding,
        "result_event_digest": result_event,
    }


def _validate_bound_scope() -> None:
    actual = (
        len(fixtures.EXPOSURES) + len(fixtures.PROBES),
        len(fixtures.EXPOSURES) * 3,
        len(fixtures.EXPOSURES),
        1,
        2 * 3,
        len(fixtures.EXPOSURES) + len(fixtures.PROBES)
        + len(fixtures.EXPOSURES) * 3
        + len(fixtures.EXPOSURES)
        + 1
        + 6,
        206,
    )
    _require(actual == _EXPECTED_COUNTS, "S2-FV materialization differs from bound scope")
    _require(sum(EXPECTED_EVENT_COUNTS.values()) == 206, "event budget differs")


def _execute(context: _RunContext) -> dict[str, object]:
    composite_state = coordinator.initial_composite_state(context.coordinator_config)
    b4_state = _fresh_b4_state()
    tspm_state = tspm1.initial_tspm1_composite_state(context.tspm_config)
    formation_evidence = []
    identity_evidence = []
    probe_source_evidence = []
    early_probe_sources: tuple[_BoundPerceptualSource, ...] = ()
    sequence_evidence: dict[str, object] | None = None
    analysis_ordinal = 0

    for exposure, expectation in zip(
        fixtures.EXPOSURES,
        fixtures.STEP_EXPECTATIONS,
        strict=True,
    ):
        analysis_ordinal += 1
        source = _analyze_source(
            context,
            fixture_id=f"s2fu.exposure.{exposure.step:02d}",
            pattern_id=exposure.pattern_id,
            role="FORMATION",
            ordinal=analysis_ordinal,
            window_start_tick=exposure.window_start_tick,
            window_end_tick=exposure.window_end_tick,
        )
        composite_prestate = composite_state
        tspm_prestate = tspm_state
        composite_result = _form_composite(
            context, composite_state, source, exposure.step
        )
        composite_state = composite_result.poststate
        b4_state, b4_event, b4_cost = _form_b4(
            context, b4_state, source, exposure.step
        )
        tspm_result = _form_tspm(
            context, tspm_state, source, exposure.step
        )
        tspm_state = tspm_result.poststate
        identity = _component_identity(
            context,
            composite_state,
            b4_state,
            tspm_state,
            source,
            exposure.step,
        )
        identity_evidence.append(identity)
        p1_auditory, p1_visual = _slow_supports(tspm_state, "P1")
        p2_auditory, p2_visual = _slow_supports(tspm_state, "P2")
        formation_evidence.append(
            {
                "step": exposure.step,
                "evaluation_pattern_id": exposure.pattern_id,
                "source_digest": source.source_digest,
                "bound_input_digest": source.coordinator_source.input_digest,
                "window_start_tick": exposure.window_start_tick,
                "window_end_tick": exposure.window_end_tick,
                "auditory_fixture_binding_digest": source.auditory_fixture_binding_digest,
                "visual_analysis_digest": source.visual_analysis_digest,
                "synthetic_auditory_receptor_values": source.auditory_values,
                "visual_receptor_values": source.visual_values,
                "composite_prestate_digest": composite_prestate.state_digest,
                "composite_poststate_digest": composite_state.state_digest,
                "b4_poststate_digest": _b4_digest(b4_state),
                "tspm_poststate_digest": tspm_state.composite_state_digest,
                "b4_event": b4_event,
                "b4_native_cost": b4_cost,
                "tspm_fast_event": tspm_result.receipt.primary_event,
                "fast_loss_pattern_id": _replaced_pattern_id(
                    tspm_prestate,
                    tspm_result.receipt,
                ),
                "ppb_calls_per_modality": tspm_state.auditory_ppb1_state.accepted_step_count,
                "p1_auditory_slow_support": p1_auditory,
                "p1_visual_slow_support": p1_visual,
                "p2_auditory_slow_support": p2_auditory,
                "p2_visual_slow_support": p2_visual,
                "expected_evaluation_metadata": {
                    "b4_event": expectation.b4_event,
                    "tspm_fast_event": expectation.tspm_fast_event,
                    "fast_loss_pattern_id": expectation.fast_loss_pattern_id,
                    "ppb_calls_per_modality": expectation.ppb_calls_per_modality,
                    "p1_slow_support": expectation.p1_slow_support,
                    "p2_slow_support": expectation.p2_slow_support,
                },
                "labels_used_as_operator_input": False,
            }
        )

        if exposure.step == 4:
            sources = []
            for probe in fixtures.PROBES[:4]:
                analysis_ordinal += 1
                probe_source = _analyze_source(
                    context,
                    fixture_id=probe.probe_id,
                    pattern_id=probe.pattern_id,
                    role="READ_ONLY",
                    ordinal=analysis_ordinal,
                    window_start_tick=probe.window_start_tick,
                    window_end_tick=probe.window_end_tick,
                )
                sources.append(probe_source)
                probe_source_evidence.append(
                    {
                        "fixture_probe_id": probe.probe_id,
                        "role": probe.role,
                        "evaluation_pattern_id": probe.pattern_id,
                        "source_digest": probe_source.source_digest,
                        "probe_digest": probe_source.coordinator_source.probe_digest,
                        "window_start_tick": probe.window_start_tick,
                        "window_end_tick": probe.window_end_tick,
                        "auditory_fixture_binding_digest": probe_source.auditory_fixture_binding_digest,
                        "visual_analysis_digest": probe_source.visual_analysis_digest,
                        "synthetic_auditory_receptor_values": probe_source.auditory_values,
                        "visual_receptor_values": probe_source.visual_values,
                    }
                )
            early_probe_sources = tuple(sources)
            sequence_evidence = _sequence_read_only(
                context,
                composite_state,
                early_probe_sources,
            )

    final_probe_sources = []
    for probe in fixtures.PROBES[4:]:
        analysis_ordinal += 1
        probe_source = _analyze_source(
            context,
            fixture_id=probe.probe_id,
            pattern_id=probe.pattern_id,
            role="READ_ONLY",
            ordinal=analysis_ordinal,
            window_start_tick=probe.window_start_tick,
            window_end_tick=probe.window_end_tick,
        )
        final_probe_sources.append(probe_source)
        probe_source_evidence.append(
            {
                "fixture_probe_id": probe.probe_id,
                "role": probe.role,
                "evaluation_pattern_id": probe.pattern_id,
                "source_digest": probe_source.source_digest,
                "probe_digest": probe_source.coordinator_source.probe_digest,
                "window_start_tick": probe.window_start_tick,
                "window_end_tick": probe.window_end_tick,
                "auditory_fixture_binding_digest": probe_source.auditory_fixture_binding_digest,
                "visual_analysis_digest": probe_source.visual_analysis_digest,
                "synthetic_auditory_receptor_values": probe_source.auditory_values,
                "visual_receptor_values": probe_source.visual_values,
            }
        )

    content_evidence = []
    for ordinal, source in enumerate(final_probe_sources, start=1):
        for arm in ("COMPOSITE", "B4", "TSPM1"):
            content_evidence.append(
                _content_probe(
                    context,
                    arm,
                    composite_state,
                    b4_state,
                    tspm_state,
                    source,
                    ordinal,
                )
            )

    _require(len(early_probe_sources) == 4, "early probe source set is incomplete")
    _require(sequence_evidence is not None, "sequence evidence is absent")
    _require(analysis_ordinal == 24, "receptor analysis count differs")
    _require(context.operation_index == 103, "operation count differs")
    _require(context.recorder.event_count == 206, "event count differs")
    _require(context.recorder.event_counts == EXPECTED_EVENT_COUNTS, "event kinds differ")
    return {
        "schema": EVIDENCE_PACKAGE_SCHEMA,
        "runner_schema": RUNNER_SCHEMA,
        "fixture_digest": fixtures.FIXTURE_DIGEST,
        "configuration_digest": context.coordinator_config.config_digest,
        "operation_count": context.operation_index,
        "event_count": context.recorder.event_count,
        "receptor_analysis_count": analysis_ordinal,
        "formation_count": len(formation_evidence) * 3,
        "component_identity_count": len(identity_evidence),
        "sequence_probe_count": 1,
        "content_probe_count": len(content_evidence),
        "formation_evidence": formation_evidence,
        "component_identity_evidence": identity_evidence,
        "probe_source_evidence": probe_source_evidence,
        "sequence_evidence": sequence_evidence,
        "content_evidence": content_evidence,
        "resource_binding": fixtures.RESOURCES,
        "tspm_sequence_status": "NOT_REPRESENTABLE_BY_CURRENT_TSPM1_STATE",
        "automatic_view_selection": None,
        "functional_assessment": None,
        "labels_used_as_operator_input": False,
        "raw_payload_retained": False,
    }


def run_main_once(output_root: Path, run_id: str) -> Path:
    """Execute exactly once only after a future explicit gate change."""

    if MAIN_EXECUTION_ENABLED is not True:
        raise S2FVRunnerError("S2-FV main execution gate is closed")
    _validate_bound_scope()
    plan = materialize_recording_plan(run_id)
    recorder = S2FVAppendOnlyRecorder(output_root, plan)
    try:
        profile, tspm_config, coordinator_config = _profile_and_configs()
        context = _RunContext(
            recorder,
            profile,
            tspm_config,
            coordinator_config,
            _world(),
            LocalChannelGridReceptor(_VISUAL_CONFIG),
        )
        evidence = _execute(context)
        return recorder.finalize(evidence)
    except BaseException as exc:
        recorder.leave_not_evaluable(type(exc).__name__)
        raise
