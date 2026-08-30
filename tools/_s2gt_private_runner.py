"""Closed private S2-GT runner for the materialized S2-GJ comparison."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
from pathlib import Path
import re
from typing import Any, Callable

import numpy as np

from mcm_field_organism import _tspm1_private as tspm1
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
from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2gb_private_perceptual_context_bundle as context_bundle
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_direct_mask_fill_baseline as direct_baseline
from tools import _s2gk_private_masked_visual_completion_evaluator as evaluator
from tools import _s2gk_private_masked_visual_context_consumer as consumer
from tools import _s2gt_private_append_only_recorder as recording
from tools import _s2gt_private_fixture_registry as fixtures


RUNNER_SCHEMA = "s2gt.private.runner.v1"
COMPACT_RECEPTOR_RECEIPT_SCHEMA = "s2gy.private.compact-receptor-receipt.v1"
COMPACT_RECEPTOR_MAX_ARTIFACT_BYTES = 2_765
COMPACT_FORMATION_RECEIPT_SCHEMA = "s2he.compact-composite-formation-receipt.v1"
COMPACT_S2GC_RECEIPT_SCHEMA = "s2he.compact-s2gc-projection-receipt.v1"
COMPACT_S2GI_RECEIPT_SCHEMA = "s2he.compact-s2gi-projection-receipt.v1"
COMPACT_PROJECTION_MAX_ARTIFACT_BYTES = 3_200
COMPACT_FORMATION_MAX_ARTIFACT_BYTES = 2_801
COMPACT_S2GC_MAX_ARTIFACT_BYTES = 3_174
COMPACT_S2GI_MAX_ARTIFACT_BYTES = 2_977
MAIN_EXECUTION_ENABLED = False
_PROFILE_PARAMETERS = PPB1ProfileParameters(
    PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
    PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
)
_VISUAL_CONFIG = VisualGridConfig(120, 80, 3, 2, 30.0)


class S2GTRunnerError(RuntimeError):
    """A terminal runner or method-boundary error."""


@dataclass(frozen=True, slots=True)
class EvaluationPlanSeal:
    plan_id: str
    case_bindings: tuple[tuple[str, str, tuple[str, ...], str], ...]
    fixture_digest: str
    seal_digest: str
    schema: str = "s2gt.private.evaluation-plan.v1"


@dataclass(frozen=True, slots=True)
class _BoundSource:
    role: str
    source_id: str
    visual_fixture_id: str
    auditory_fixture_id: str
    window_start: int
    window_end: int
    envelope: PPB1ActiveReceptorBatchEnvelope
    bound: coordinator.B4TSPM1BoundInput | coordinator.B4TSPM1BoundProbe
    raw_payload_retained: bool
    raw_sha256: str
    source_digest: str


@dataclass(frozen=True, slots=True)
class CompactReceptorReceiptV1:
    operation_id: str
    operation_index: int
    operation_class: str
    source_role: str
    source_id: str
    history_id: str
    source_ordinal: str
    execution_plan_digest: str
    manifest_artifact_digest: str
    registry_bundle_digest: str
    fixture_set_digest: str
    coordinator_config_digest: str
    visual_fixture_id: str
    auditory_fixture_id: str
    auditory_dimension: int
    visual_dimension: int
    av_dimension: int
    auditory_geometry_id: str
    visual_geometry_id: str
    auditory_snapshot_id: str
    visual_snapshot_id: str
    auditory_source_clock_id: str
    visual_source_clock_id: str
    field_clock_id: str
    source_window_start_tick: int
    source_window_end_tick: int
    field_window_start_tick: int
    field_window_end_tick: int
    raw_image_sha256: str
    raw_payload_retained: bool
    auditory_values_digest: str
    visual_values_digest: str
    av_projection_digest: str
    auditory_input_projection_digest: str
    visual_input_projection_digest: str
    auditory_timed_frame_provenance_digest: str
    visual_timed_frame_provenance_digest: str
    envelope_digest: str
    tspm_source_digest: str
    bound_source_digest: str
    source_digest: str
    schema: str = COMPACT_RECEPTOR_RECEIPT_SCHEMA


@dataclass(frozen=True, slots=True)
class _RecordedReceptorSource:
    source: _BoundSource
    receptor_receipt_digest: str
    result_event_digest: str


@dataclass(frozen=True, slots=True)
class CompactCompositeFormationReceiptV1:
    execution_plan_digest: str
    source_digest: str
    receptor_receipt_artifact_digest: str
    config_digest: str
    owner_prestate_digest: str
    input_digest: str
    composite_prestate_digest: str
    composite_poststate_digest: str
    b4_event: str
    b4_slot_id: str
    b4_poststate_digest: str
    tspm_result_digest: str
    tspm_receipt_digest: str
    tspm_poststate_digest: str
    step_receipt_digest: str
    generation: int
    parent_state_digest: str
    last_input_digest: str
    ledger_operation: str
    ledger_counts: tuple[int, ...]
    resource_ledger_digest: str
    coordinator_owner_ids: tuple[str, str, str]
    owner_authorized_digests: tuple[str, str, str]
    owner_status: str
    owner_attempt_count: int
    owner_use_count: int
    owner_committed_result_digest: str
    owner_state_digest: str
    result_digest: str
    projection_digest: str
    schema: str = COMPACT_FORMATION_RECEIPT_SCHEMA


@dataclass(frozen=True, slots=True)
class CompactS2GCProjectionReceiptV1:
    execution_plan_digest: str
    source_finding_artifact_digest: str
    source_finding_digest: str
    contract_digest: str
    binding_digest: str
    config_digest: str
    composite_state_digest: str
    probe_digest: str
    source_digest: str
    role_statuses: tuple[str, str, str]
    role_absence_reasons: tuple[str | None, str | None, str | None]
    role_finding_digests: tuple[str, str, str]
    candidate_digests: tuple[str, ...]
    component_roles: tuple[str, ...]
    component_digests: tuple[str, ...]
    component_source_digests: tuple[str, ...]
    component_values_digests: tuple[str, ...]
    component_native_distances: tuple[tuple[float, ...] | None, ...]
    component_functional_distances: tuple[tuple[float, ...], ...]
    component_support_counts: tuple[int | None, ...]
    component_stable_flags: tuple[bool | None, ...]
    component_last_selected_steps: tuple[int | None, ...]
    component_formation_indices: tuple[int | None, ...]
    sequence_status: str
    sequence_reference_digests: tuple[str, ...]
    sequence_digests: tuple[str, str]
    ledger_counts: tuple[int, ...]
    resource_ledger_digest: str
    prestate_digest: str
    poststate_digest: str
    automatic_selection: None
    bundle_digest: str
    projection_digest: str
    schema: str = COMPACT_S2GC_RECEIPT_SCHEMA


@dataclass(frozen=True, slots=True)
class CompactS2GIProjectionReceiptV1:
    execution_plan_digest: str
    source_s2gc_artifact_digest: str
    source_bundle_digest: str
    contract_digest: str
    binding_digest: str
    config_digest: str
    composite_state_digest: str
    probe_digest: str
    source_digest: str
    area_roles: tuple[str, str]
    area_finding_digests: tuple[str, str]
    a_recent_status: str
    a_recent_finding_digest: str
    a_fast_status: str
    a_fast_finding_digest: str
    a_sequence_status: str
    a_sequence_finding_digest: str
    b_stable_status: str
    b_candidate_digest: str | None
    b_component_digests: tuple[str, ...]
    b_values_digests: tuple[str, ...]
    b_source_digests: tuple[str, ...]
    ledger_counts: tuple[int, ...]
    source_ledger_digest: str
    resource_ledger_digest: str
    prestate_digest: str
    poststate_digest: str
    automatic_selection: None
    bundle_digest: str
    projection_digest: str
    schema: str = COMPACT_S2GI_RECEIPT_SCHEMA


@dataclass(frozen=True, slots=True)
class _RecordedCompactResult:
    result: object
    receipt_artifact_digest: str
    result_event_digest: str


@dataclass(slots=True)
class _Runtime:
    profile: object
    tspm_config: tspm1.TSPM1ConfigBinding
    coordinator_config: coordinator.B4TSPM1CoordinatorConfig
    world: BrowserWorldContract
    receptor: LocalChannelGridReceptor
    image_serial: int = 0


def _canonical(value: object) -> object:
    if is_dataclass(value):
        return _canonical(asdict(value))
    if isinstance(value, dict):
        return {str(key): _canonical(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonical(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise S2GTRunnerError(message)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def build_evaluation_plan_seal() -> EvaluationPlanSeal:
    """Build the independent evaluation root without execution provenance."""

    case_bindings = (
        ("e01", "CORRECT_CONTEXT", ("a01", "a02", "a03"), "J1-T"),
        ("e02", "FOREIGN_CONTEXT", ("a01", "a04", "a05"), "J1-T"),
        ("e03", "ABSENT_CONTEXT", ("a01", "a06"), "J1-T"),
        ("e04", "CONFLICT_CONTEXT", ("a01", "a07"), "J1-T"),
    )
    payload = {
        "schema": "s2gt.private.evaluation-plan.v1",
        "plan_id": "s2gt-evaluation-plan-01",
        "case_bindings": case_bindings,
        "fixture_digest": fixtures.FIXTURE_SET_DIGEST,
    }
    return EvaluationPlanSeal(payload["plan_id"], case_bindings, fixtures.FIXTURE_SET_DIGEST, fixtures.canonical_digest(payload))


def _source_paths(workspace_root: Path) -> tuple[tuple[str, Path], ...]:
    return (
        ("fixture_registry", workspace_root / "tools/_s2gt_private_fixture_registry.py"),
        ("runner", workspace_root / "tools/_s2gt_private_runner.py"),
        ("recorder", workspace_root / "tools/_s2gt_private_append_only_recorder.py"),
        ("verifier", workspace_root / "tools/_s2gt_private_result_verifier.py"),
        ("coordinator", workspace_root / "tools/_s2fs_b4_tspm1_private_coordinator.py"),
        ("context_bundle", workspace_root / "tools/_s2gb_private_perceptual_context_bundle.py"),
        ("two_area", workspace_root / "tools/_s2gi_private_two_area_context_projection.py"),
        ("consumer", workspace_root / "tools/_s2gk_private_masked_visual_context_consumer.py"),
        ("baseline", workspace_root / "tools/_s2gk_private_direct_mask_fill_baseline.py"),
        ("evaluator", workspace_root / "tools/_s2gk_private_masked_visual_completion_evaluator.py"),
    )


def materialize_execution_plan(workspace_root: Path, run_id: str, owner_id: str) -> tuple[recording.ExecutionPlan, fixtures.RegistryBundle]:
    fixtures.validate_literal_fixtures()
    registry = fixtures.load_bound_registries(workspace_root)
    source_digests = tuple((path.relative_to(workspace_root).as_posix(), fixtures.file_digest(path)) for _, path in _source_paths(workspace_root))
    return recording.ExecutionPlan.build(run_id, owner_id, registry, source_digests), registry


def _runtime() -> _Runtime:
    profile = bind_ppb1_receptor_profile("browser", _PROFILE_PARAMETERS)
    tspm_config = tspm1.TSPM1ConfigBinding.build(
        tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        profile,
    )
    coordinator_config = coordinator.build_coordinator_config(tspm_config)
    world = BrowserWorldContract(
        contract_id="synthetic.s2gt.world.v1",
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
    return _Runtime(profile, tspm_config, coordinator_config, world, LocalChannelGridReceptor(_VISUAL_CONFIG))


def _image(fixture: fixtures.VisualFixture) -> np.ndarray:
    cells = np.asarray(tuple(int(value) * 255 for value in fixture.bits), dtype=np.uint8).reshape(2, 3, 3)
    image = np.repeat(np.repeat(cells, 40, axis=0), 40, axis=1)
    image.setflags(write=False)
    return image


def _timed(frame: ReceptorContactFrame, field_time: CommonFieldTime) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(frame.modality_id, frame.geometry_id, field_time.clock_id, (OrganismTimedReceptorFrame(frame, field_time),))


def _analyze(runtime: _Runtime, source_id: str, visual_id: str, auditory_id: str, start_tick: int, end_tick: int, role: str) -> _BoundSource:
    visual_fixture = fixtures.VISUAL_BY_ID[visual_id]
    auditory_values = fixtures.AUDITORY_BY_ID[auditory_id]
    image = _image(visual_fixture)
    raw_sha256 = hashlib.sha256(image.tobytes()).hexdigest()
    _require(raw_sha256 == visual_fixture.raw_sha256, "raw visual fixture digest differs")
    receptor_state = runtime.receptor.analyze(image, frame_index=runtime.image_serial)
    runtime.image_serial += 1
    visual_values = tuple(receptor_state.channel_values)
    _require(visual_values == visual_fixture.values, "visual receptor values differ")
    auditory_frame = ReceptorContactFrame("auditory", runtime.profile.auditory_config.geometry_id, f"{source_id}.auditory", "s2gt.auditory.clock", start_tick, end_tick, runtime.profile.auditory_config.carrier_ids, auditory_values)
    visual_frame = ReceptorContactFrame("visual", runtime.profile.visual_config.geometry_id, f"{source_id}.visual", "s2gt.visual.clock", start_tick, end_tick, runtime.profile.visual_config.carrier_ids, visual_values)
    field_time = CommonFieldTime("s2gt.field.clock", start_tick, end_tick)
    batch = BrowserReceptorSequenceBatch(runtime.world.contract_id, runtime.world.digest(), (_timed(auditory_frame, field_time), _timed(visual_frame, field_time)))
    _require(batch.raw_payloads_retained is False, "raw receptor payload retention differs")
    envelope = bind_ppb1_active_receptor_batch(f"{source_id}.binding", runtime.world, batch, runtime.profile)
    auditory_binding = envelope.auditory_stream.timed_frames[0]
    visual_binding = envelope.visual_stream.timed_frames[0]
    if role == "FORMATION":
        bound = coordinator.bind_coordinator_input(runtime.coordinator_config, envelope, auditory_binding, visual_binding)
        bound_digest = bound.input_digest
    elif role == "READ_ONLY":
        bound = coordinator.bind_coordinator_probe(runtime.coordinator_config, envelope, auditory_binding, visual_binding)
        bound_digest = bound.probe_digest
    else:
        raise S2GTRunnerError("unknown receptor source role")
    source_digest = fixtures.canonical_digest({"schema": RUNNER_SCHEMA, "source_id": source_id, "role": role, "visual_fixture_id": visual_id, "auditory_fixture_id": auditory_id, "window": [start_tick, end_tick], "raw_sha256": raw_sha256, "bound_digest": bound_digest})
    return _BoundSource(role, source_id, visual_id, auditory_id, start_tick, end_tick, envelope, bound, batch.raw_payloads_retained, raw_sha256, source_digest)


def _formation(runtime: _Runtime, state: coordinator.B4TSPM1CompositeState, source: _BoundSource, owner_suffix: str) -> coordinator.B4TSPM1StepResult:
    _require(type(source.bound) is coordinator.B4TSPM1BoundInput, "formation source differs")
    owner = coordinator.B4TSPM1CoordinatorOwner(f"s2gt.owner.{owner_suffix}", f"s2gt.authorization.{owner_suffix}", f"s2gt.consumption.{owner_suffix}", runtime.coordinator_config.config_digest, state.state_digest, source.bound.input_digest)
    return owner.consume_once(runtime.coordinator_config, state, source.bound)


def _probe(runtime: _Runtime, state: coordinator.B4TSPM1CompositeState, source: _BoundSource) -> coordinator.B4TSPM1ReadOnlyFinding:
    _require(type(source.bound) is coordinator.B4TSPM1BoundProbe, "read-only source differs")
    return coordinator.probe_composite_read_only(runtime.coordinator_config, state, source.bound)


def _projection_binding(runtime: _Runtime, state: coordinator.B4TSPM1CompositeState, source: _BoundSource) -> context_bundle.PerceptualContextProjectionBinding:
    _require(type(source.bound) is coordinator.B4TSPM1BoundProbe, "projection source differs")
    return context_bundle.PerceptualContextProjectionBinding.build(
        config_digest=runtime.coordinator_config.config_digest,
        composite_state_digest=state.state_digest,
        probe_digest=source.bound.probe_digest,
        probe_values_digest=source.bound.values_digest,
        auditory_source_digest=source.bound.auditory.timed_frame_provenance_digest,
        visual_source_digest=source.bound.visual.timed_frame_provenance_digest,
        auditory_geometry_id=source.bound.auditory.timed_frame.frame.geometry_id,
        visual_geometry_id=source.bound.visual.timed_frame.frame.geometry_id,
        field_clock_id=source.bound.auditory.field_clock_id,
        window_start=source.window_start,
        window_end=source.window_end,
    )


def _compact_receptor_receipt(
    recorder: recording.AppendOnlyRunRecorder,
    row: dict[str, str],
    source: _BoundSource,
) -> CompactReceptorReceiptV1:
    if type(source) is not _BoundSource:
        raise recording.S2GTRecordingError("E006", "input source binding is invalid")
    expected_role = (
        "FORMATION"
        if row["operation_class"] == "FORMATION_RECEPTOR_ANALYSIS"
        else "READ_ONLY"
    )
    if row["operation_class"] not in {
        "FORMATION_RECEPTOR_ANALYSIS",
        "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS",
        "CONSUMER_RECEPTOR_ANALYSIS",
    } or source.role != expected_role:
        raise recording.S2GTRecordingError("E002", "operation registry binding is invalid")
    if row["operation_class"] == "FORMATION_RECEPTOR_ANALYSIS":
        expected_source_id = (
            f"s2gt.{row['history']}.formation.{int(row['source_ordinal']):02d}"
        )
    elif row["operation_class"] == "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS":
        expected_source_id = f"s2gt.{row['history']}.probe.full.01"
    else:
        expected_source_id = "s2gt.shared.consumer.01"
    if source.source_id != expected_source_id:
        raise recording.S2GTRecordingError("E006", "input source binding is invalid")
    if recorder.pending_start is None or recorder.pending_start[0] != row["operation_id"]:
        raise recording.S2GTRecordingError("E002", "operation registry binding is invalid")

    if source.role == "FORMATION":
        if type(source.bound) is not coordinator.B4TSPM1BoundInput:
            raise recording.S2GTRecordingError("E006", "input source binding is invalid")
        tspm_source_digest = source.bound.tspm_exposure.exposure_digest
        bound_source_digest = source.bound.input_digest
    else:
        if type(source.bound) is not coordinator.B4TSPM1BoundProbe:
            raise recording.S2GTRecordingError("E006", "input source binding is invalid")
        tspm_source_digest = source.bound.tspm_probe.probe_digest
        bound_source_digest = source.bound.probe_digest

    auditory = source.bound.auditory
    visual = source.bound.visual
    auditory_frame = auditory.timed_frame.frame
    visual_frame = visual.timed_frame.frame
    if (
        source.bound.envelope is not source.envelope
        or source.bound.auditory is not source.envelope.auditory_stream.timed_frames[0]
        or source.bound.visual is not source.envelope.visual_stream.timed_frames[0]
        or source.raw_payload_retained is not False
        or len(source.bound.auditory_values) != 8
        or len(source.bound.visual_values) != 18
        or len(source.bound.av_values) != 26
        or source.bound.av_values
        != source.bound.auditory_values + source.bound.visual_values
        or source.window_start != auditory.source_window_start_tick
        or source.window_start != visual.source_window_start_tick
        or source.window_end != auditory.source_window_end_tick
        or source.window_end != visual.source_window_end_tick
        or auditory.field_window_start_tick != visual.field_window_start_tick
        or auditory.field_window_end_tick != visual.field_window_end_tick
        or auditory.field_clock_id != visual.field_clock_id
    ):
        raise recording.S2GTRecordingError("E006", "input source binding is invalid")

    expected_source_digest = fixtures.canonical_digest(
        {
            "schema": RUNNER_SCHEMA,
            "source_id": source.source_id,
            "role": source.role,
            "visual_fixture_id": source.visual_fixture_id,
            "auditory_fixture_id": source.auditory_fixture_id,
            "window": [source.window_start, source.window_end],
            "raw_sha256": source.raw_sha256,
            "bound_digest": bound_source_digest,
        }
    )
    auditory_values_digest = fixtures.canonical_digest(
        list(source.bound.auditory_values)
    )
    visual_values_digest = fixtures.canonical_digest(list(source.bound.visual_values))
    manifest_artifact_digest = recorder.result_digests.get("manifest")
    digests = (
        recorder.plan.plan_digest,
        manifest_artifact_digest,
        recorder.registry.bundle_digest,
        recorder.plan.fixture_digest,
        source.bound.config_digest,
        source.raw_sha256,
        auditory_values_digest,
        visual_values_digest,
        source.bound.values_digest,
        auditory.ppb1_input_projection_digest,
        visual.ppb1_input_projection_digest,
        auditory.timed_frame_provenance_digest,
        visual.timed_frame_provenance_digest,
        source.envelope.envelope_digest,
        tspm_source_digest,
        bound_source_digest,
        source.source_digest,
    )
    if (
        expected_source_digest != source.source_digest
        or any(not _valid_digest(value) for value in digests)
    ):
        raise recording.S2GTRecordingError("E007", "artifact digest binding is invalid")

    receipt = CompactReceptorReceiptV1(
        operation_id=row["operation_id"],
        operation_index=int(row["index"]),
        operation_class=row["operation_class"],
        source_role=source.role,
        source_id=source.source_id,
        history_id=row["history"],
        source_ordinal=row["source_ordinal"],
        execution_plan_digest=recorder.plan.plan_digest,
        manifest_artifact_digest=manifest_artifact_digest,
        registry_bundle_digest=recorder.registry.bundle_digest,
        fixture_set_digest=recorder.plan.fixture_digest,
        coordinator_config_digest=source.bound.config_digest,
        visual_fixture_id=source.visual_fixture_id,
        auditory_fixture_id=source.auditory_fixture_id,
        auditory_dimension=8,
        visual_dimension=18,
        av_dimension=26,
        auditory_geometry_id=auditory_frame.geometry_id,
        visual_geometry_id=visual_frame.geometry_id,
        auditory_snapshot_id=auditory_frame.snapshot_id,
        visual_snapshot_id=visual_frame.snapshot_id,
        auditory_source_clock_id=auditory.source_clock_id,
        visual_source_clock_id=visual.source_clock_id,
        field_clock_id=auditory.field_clock_id,
        source_window_start_tick=source.window_start,
        source_window_end_tick=source.window_end,
        field_window_start_tick=auditory.field_window_start_tick,
        field_window_end_tick=auditory.field_window_end_tick,
        raw_image_sha256=source.raw_sha256,
        raw_payload_retained=source.raw_payload_retained,
        auditory_values_digest=auditory_values_digest,
        visual_values_digest=visual_values_digest,
        av_projection_digest=source.bound.values_digest,
        auditory_input_projection_digest=auditory.ppb1_input_projection_digest,
        visual_input_projection_digest=visual.ppb1_input_projection_digest,
        auditory_timed_frame_provenance_digest=auditory.timed_frame_provenance_digest,
        visual_timed_frame_provenance_digest=visual.timed_frame_provenance_digest,
        envelope_digest=source.envelope.envelope_digest,
        tspm_source_digest=tspm_source_digest,
        bound_source_digest=bound_source_digest,
        source_digest=source.source_digest,
    )
    artifact = {"result": _canonical(receipt)}
    envelope = {
        "schema": recording.RECORDER_SCHEMA,
        "operation_id": row["operation_id"],
        "owner_id": recorder.plan.owner_id,
        "reservation_digest": recorder.reservation_digest,
        "start_event_digest": recorder.pending_start[1],
        "artifact": artifact,
    }
    if len(recording._canonical_bytes(envelope)) > COMPACT_RECEPTOR_MAX_ARTIFACT_BYTES:
        raise recording.S2GTRecordingError(
            "E008", "registered resource limit was exceeded"
        )
    return receipt


def _record_receptor(
    recorder: recording.AppendOnlyRunRecorder,
    operation_class: str,
    start_payload: dict[str, object],
    function: Callable[[], _BoundSource],
    *,
    history: str,
    source_ordinal: str,
) -> _RecordedReceptorSource:
    row = recorder._row()
    if (
        row["operation_class"] != operation_class
        or row["history"] != history
        or row["source_ordinal"] != source_ordinal
    ):
        raise recording.S2GTRecordingError("E002", "operation registry binding is invalid")
    operation_id = row["operation_id"]
    recorder.start(operation_id, start_payload)
    source = function()
    source_identity = id(source)
    receipt = _compact_receptor_receipt(recorder, row, source)
    result_event_digest = recorder.finish(
        operation_id, {"result": _canonical(receipt)}
    )
    receptor_receipt_digest = recorder.result_digests.get(operation_id)
    if (
        id(source) != source_identity
        or not _valid_digest(receptor_receipt_digest)
        or not _valid_digest(result_event_digest)
        or recorder.previous_event_digest != result_event_digest
    ):
        raise recording.S2GTRecordingError("E007", "artifact digest binding is invalid")
    return _RecordedReceptorSource(
        source,
        receptor_receipt_digest,
        result_event_digest,
    )


def _projection_digest(payload: dict[str, object]) -> str:
    return fixtures.canonical_digest(payload)


def _validate_compact_envelope_size(
    recorder: recording.AppendOnlyRunRecorder,
    row: dict[str, str],
    receipt: object,
    role_maximum: int,
) -> None:
    if recorder.pending_start is None or recorder.pending_start[0] != row["operation_id"]:
        raise recording.S2GTRecordingError("E002", "operation registry binding is invalid")
    envelope = {
        "schema": recording.RECORDER_SCHEMA,
        "operation_id": row["operation_id"],
        "owner_id": recorder.plan.owner_id,
        "reservation_digest": recorder.reservation_digest,
        "start_event_digest": recorder.pending_start[1],
        "artifact": {"result": _canonical(receipt)},
    }
    encoded_size = len(recording._canonical_bytes(envelope))
    if (
        encoded_size > role_maximum
        or encoded_size > COMPACT_PROJECTION_MAX_ARTIFACT_BYTES
        or encoded_size >= int(row["output_max_bytes"])
    ):
        raise recording.S2GTRecordingError("E008", "registered resource limit was exceeded")


def _compact_formation_receipt(
    recorder: recording.AppendOnlyRunRecorder,
    row: dict[str, str],
    source: _BoundSource,
    receptor_receipt_artifact_digest: str,
    result: coordinator.B4TSPM1StepResult,
) -> CompactCompositeFormationReceiptV1:
    if (
        row["operation_class"] != "COMPOSITE_FORMATION"
        or type(source) is not _BoundSource
        or type(source.bound) is not coordinator.B4TSPM1BoundInput
        or type(result) is not coordinator.B4TSPM1StepResult
        or not _valid_digest(receptor_receipt_artifact_digest)
    ):
        raise recording.S2GTRecordingError("E006", "formation projection source is invalid")
    receipt = result.receipt
    ledger = result.resource_ledger
    owner = result.owner_poststate
    poststate = result.poststate
    if (
        receipt.input_digest != source.bound.input_digest
        or receipt.composite_poststate_digest != poststate.state_digest
        or receipt.resource_ledger_digest != ledger.ledger_digest
        or owner.committed_result_digest != result.result_digest
        or owner.status != "CONSUMED"
        or owner.failure_code is not None
        or owner.failure_digest is not None
    ):
        raise recording.S2GTRecordingError("E007", "formation projection binding is invalid")
    payload: dict[str, object] = {
        "schema": COMPACT_FORMATION_RECEIPT_SCHEMA,
        "execution_plan_digest": recorder.plan.plan_digest,
        "source_digest": source.source_digest,
        "receptor_receipt_artifact_digest": receptor_receipt_artifact_digest,
        "config_digest": receipt.config_digest,
        "owner_prestate_digest": receipt.owner_prestate_digest,
        "input_digest": receipt.input_digest,
        "composite_prestate_digest": receipt.composite_prestate_digest,
        "composite_poststate_digest": receipt.composite_poststate_digest,
        "b4_event": receipt.b4_event,
        "b4_slot_id": receipt.b4_slot_id,
        "b4_poststate_digest": receipt.b4_poststate_digest,
        "tspm_result_digest": receipt.tspm_result_digest,
        "tspm_receipt_digest": receipt.tspm_receipt_digest,
        "tspm_poststate_digest": receipt.tspm_poststate_digest,
        "step_receipt_digest": receipt.receipt_digest,
        "generation": poststate.generation,
        "parent_state_digest": poststate.parent_state_digest,
        "last_input_digest": poststate.last_input_digest,
        "ledger_operation": ledger.operation,
        "ledger_counts": (
            ledger.common_projection_terms,
            ledger.b4_functional_write_words,
            ledger.b4_functional_distance_terms,
            ledger.tspm_functional_write_words,
            ledger.tspm_functional_distance_terms,
            ledger.coordinator_validation_terms,
            ledger.coordinator_digest_operations,
            ledger.coordinator_write_words,
            ledger.total_functional_write_words,
            ledger.total_functional_distance_terms,
            ledger.total_control_terms,
        ),
        "resource_ledger_digest": ledger.ledger_digest,
        "coordinator_owner_ids": (
            owner.owner_id,
            owner.authorization_id,
            owner.consumption_id,
        ),
        "owner_authorized_digests": (
            owner.authorized_config_digest,
            owner.authorized_prestate_digest,
            owner.authorized_input_digest,
        ),
        "owner_status": owner.status,
        "owner_attempt_count": owner.attempt_count,
        "owner_use_count": owner.use_count,
        "owner_committed_result_digest": owner.committed_result_digest,
        "owner_state_digest": owner.owner_state_digest,
        "result_digest": result.result_digest,
    }
    return CompactCompositeFormationReceiptV1(
        **payload, projection_digest=_projection_digest(payload)  # type: ignore[arg-type]
    )


def _compact_s2gc_receipt(
    recorder: recording.AppendOnlyRunRecorder,
    row: dict[str, str],
    source_finding_artifact_digest: str,
    finding: coordinator.B4TSPM1ReadOnlyFinding,
    sequence_evidence: context_bundle.ValidatedB4ShortSequenceEvidence,
    bundle: context_bundle.PerceptualContextBundle,
) -> CompactS2GCProjectionReceiptV1:
    if (
        row["operation_class"] != "S2GC_PROJECTION"
        or type(finding) is not coordinator.B4TSPM1ReadOnlyFinding
        or type(sequence_evidence) is not context_bundle.ValidatedB4ShortSequenceEvidence
        or type(bundle) is not context_bundle.PerceptualContextBundle
        or not _valid_digest(source_finding_artifact_digest)
        or bundle.sequence_finding.source_evidence_digest != sequence_evidence.evidence_digest
        or bundle.sequence_finding.observed_b4_state_digest != finding.b4_recent.observed_state_digest
        or bundle.prestate_digest != finding.prestate_digest
        or bundle.poststate_digest != finding.poststate_digest
    ):
        raise recording.S2GTRecordingError("E007", "S2-GC projection binding is invalid")
    roles = bundle.role_findings
    candidates = tuple(item.candidate for item in roles if item.candidate is not None)
    components = tuple(component for candidate in candidates for component in candidate.components)
    ledger = bundle.resource_ledger
    payload: dict[str, object] = {
        "schema": COMPACT_S2GC_RECEIPT_SCHEMA,
        "execution_plan_digest": recorder.plan.plan_digest,
        "source_finding_artifact_digest": source_finding_artifact_digest,
        "source_finding_digest": finding.finding_digest,
        "contract_digest": bundle.contract_digest,
        "binding_digest": bundle.binding_digest,
        "config_digest": bundle.config_digest,
        "composite_state_digest": bundle.composite_state_digest,
        "probe_digest": bundle.probe_digest,
        "source_digest": bundle.source_digest,
        "role_statuses": tuple(item.status for item in roles),
        "role_absence_reasons": tuple(item.absence_reason for item in roles),
        "role_finding_digests": tuple(item.finding_digest for item in roles),
        "candidate_digests": tuple(item.candidate_digest for item in candidates),
        "component_roles": tuple(item.component_role for item in components),
        "component_digests": tuple(item.component_digest for item in components),
        "component_source_digests": tuple(item.source_digest for item in components),
        "component_values_digests": tuple(item.values_digest for item in components),
        "component_native_distances": tuple(item.native_distances for item in components),
        "component_functional_distances": tuple(item.functional_distances for item in components),
        "component_support_counts": tuple(item.support_count for item in components),
        "component_stable_flags": tuple(item.stable for item in components),
        "component_last_selected_steps": tuple(item.last_selected_step for item in components),
        "component_formation_indices": tuple(item.formation_index for item in components),
        "sequence_status": bundle.sequence_finding.status,
        "sequence_reference_digests": tuple(
            item.reference_digest for item in bundle.sequence_finding.references
        ),
        "sequence_digests": (
            sequence_evidence.evidence_digest,
            bundle.sequence_finding.finding_digest,
        ),
        "ledger_counts": (
            ledger.validated_evidence_records,
            ledger.validated_digest_count,
            ledger.role_projection_count,
            ledger.candidate_count,
            ledger.component_count,
            ledger.value_count,
            ledger.sequence_reference_count,
            ledger.digest_operation_count,
        ),
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": bundle.prestate_digest,
        "poststate_digest": bundle.poststate_digest,
        "automatic_selection": bundle.automatic_selection,
        "bundle_digest": bundle.bundle_digest,
    }
    return CompactS2GCProjectionReceiptV1(
        **payload, projection_digest=_projection_digest(payload)  # type: ignore[arg-type]
    )


def _compact_s2gi_receipt(
    recorder: recording.AppendOnlyRunRecorder,
    row: dict[str, str],
    source_s2gc_artifact_digest: str,
    source_bundle: context_bundle.PerceptualContextBundle,
    bundle: two_area.TwoAreaContextBundle,
) -> CompactS2GIProjectionReceiptV1:
    if (
        row["operation_class"] != "S2GI_PROJECTION"
        or type(source_bundle) is not context_bundle.PerceptualContextBundle
        or type(bundle) is not two_area.TwoAreaContextBundle
        or not _valid_digest(source_s2gc_artifact_digest)
        or bundle.source_bundle_digest != source_bundle.bundle_digest
    ):
        raise recording.S2GTRecordingError("E007", "S2-GI projection binding is invalid")
    area_a, area_b = bundle.area_findings
    b_role = area_b.stable_content
    b_candidate = b_role.candidate
    b_components = () if b_candidate is None else b_candidate.components
    ledger = bundle.resource_ledger
    payload: dict[str, object] = {
        "schema": COMPACT_S2GI_RECEIPT_SCHEMA,
        "execution_plan_digest": recorder.plan.plan_digest,
        "source_s2gc_artifact_digest": source_s2gc_artifact_digest,
        "source_bundle_digest": bundle.source_bundle_digest,
        "contract_digest": bundle.contract_digest,
        "binding_digest": bundle.binding_digest,
        "config_digest": bundle.config_digest,
        "composite_state_digest": bundle.composite_state_digest,
        "probe_digest": bundle.probe_digest,
        "source_digest": bundle.source_digest,
        "area_roles": tuple(item.area for item in bundle.area_findings),
        "area_finding_digests": tuple(item.finding_digest for item in bundle.area_findings),
        "a_recent_status": area_a.recent_content.status,
        "a_recent_finding_digest": area_a.recent_content.finding_digest,
        "a_fast_status": area_a.fast_internal.status,
        "a_fast_finding_digest": area_a.fast_internal.finding_digest,
        "a_sequence_status": area_a.short_sequence.status,
        "a_sequence_finding_digest": area_a.short_sequence.finding_digest,
        "b_stable_status": b_role.status,
        "b_candidate_digest": None if b_candidate is None else b_candidate.candidate_digest,
        "b_component_digests": tuple(item.component_digest for item in b_components),
        "b_values_digests": tuple(item.values_digest for item in b_components),
        "b_source_digests": tuple(item.source_digest for item in b_components),
        "ledger_counts": (
            ledger.validated_bundle_count,
            ledger.validated_role_count,
            ledger.candidate_reference_count,
            ledger.component_reference_count,
            ledger.value_reference_count,
            ledger.sequence_reference_count,
            ledger.area_projection_count,
            ledger.digest_operation_count,
        ),
        "source_ledger_digest": ledger.source_ledger_digest,
        "resource_ledger_digest": ledger.ledger_digest,
        "prestate_digest": bundle.prestate_digest,
        "poststate_digest": bundle.poststate_digest,
        "automatic_selection": bundle.automatic_selection,
        "bundle_digest": bundle.bundle_digest,
    }
    return CompactS2GIProjectionReceiptV1(
        **payload, projection_digest=_projection_digest(payload)  # type: ignore[arg-type]
    )


def _finish_compact(
    recorder: recording.AppendOnlyRunRecorder,
    row: dict[str, str],
    result: object,
    receipt: object,
    semantic_digest: str,
    role_maximum: int,
) -> _RecordedCompactResult:
    identity = id(result)
    _validate_compact_envelope_size(recorder, row, receipt, role_maximum)
    result_event_digest = recorder.finish(
        row["operation_id"], {"result": _canonical(receipt)}
    )
    artifact_digest = recorder.result_digests.get(row["operation_id"])
    if (
        id(result) != identity
        or not _valid_digest(semantic_digest)
        or not _valid_digest(artifact_digest)
        or not _valid_digest(result_event_digest)
        or recorder.previous_event_digest != result_event_digest
    ):
        raise recording.S2GTRecordingError("E007", "compact artifact binding is invalid")
    return _RecordedCompactResult(result, artifact_digest, result_event_digest)


def _record_compact_formation(
    recorder: recording.AppendOnlyRunRecorder,
    start_payload: dict[str, object],
    function: Callable[[], coordinator.B4TSPM1StepResult],
    source: _BoundSource,
    receptor_receipt_artifact_digest: str,
    *,
    history: str,
    source_ordinal: str,
) -> _RecordedCompactResult:
    row = recorder._row()
    _require(
        row["operation_class"] == "COMPOSITE_FORMATION"
        and row["history"] == history
        and row["source_ordinal"] == source_ordinal,
        "registered compact formation differs",
    )
    recorder.start(row["operation_id"], start_payload)
    result = function()
    result_identity = id(result)
    semantic_digest = result.result_digest
    receipt = _compact_formation_receipt(
        recorder, row, source, receptor_receipt_artifact_digest, result
    )
    if id(result) != result_identity or result.result_digest != semantic_digest:
        raise recording.S2GTRecordingError("E007", "formation result changed during projection")
    return _finish_compact(
        recorder, row, result, receipt, semantic_digest, COMPACT_FORMATION_MAX_ARTIFACT_BYTES
    )


def _record_compact_s2gc(
    recorder: recording.AppendOnlyRunRecorder,
    start_payload: dict[str, object],
    function: Callable[[], context_bundle.PerceptualContextBundle],
    finding: coordinator.B4TSPM1ReadOnlyFinding,
    sequence_evidence: context_bundle.ValidatedB4ShortSequenceEvidence,
    source_finding_artifact_digest: str,
    *,
    history: str,
) -> _RecordedCompactResult:
    row = recorder._row()
    _require(
        row["operation_class"] == "S2GC_PROJECTION" and row["history"] == history,
        "registered compact S2-GC projection differs",
    )
    recorder.start(row["operation_id"], start_payload)
    result = function()
    result_identity = id(result)
    semantic_digest = result.bundle_digest
    receipt = _compact_s2gc_receipt(
        recorder,
        row,
        source_finding_artifact_digest,
        finding,
        sequence_evidence,
        result,
    )
    if id(result) != result_identity or result.bundle_digest != semantic_digest:
        raise recording.S2GTRecordingError("E007", "S2-GC result changed during projection")
    return _finish_compact(
        recorder, row, result, receipt, semantic_digest, COMPACT_S2GC_MAX_ARTIFACT_BYTES
    )


def _record_compact_s2gi(
    recorder: recording.AppendOnlyRunRecorder,
    start_payload: dict[str, object],
    function: Callable[[], two_area.TwoAreaContextBundle],
    source_bundle: context_bundle.PerceptualContextBundle,
    source_s2gc_artifact_digest: str,
    *,
    history: str,
) -> _RecordedCompactResult:
    row = recorder._row()
    _require(
        row["operation_class"] == "S2GI_PROJECTION" and row["history"] == history,
        "registered compact S2-GI projection differs",
    )
    recorder.start(row["operation_id"], start_payload)
    result = function()
    result_identity = id(result)
    semantic_digest = result.bundle_digest
    receipt = _compact_s2gi_receipt(
        recorder, row, source_s2gc_artifact_digest, source_bundle, result
    )
    if id(result) != result_identity or result.bundle_digest != semantic_digest:
        raise recording.S2GTRecordingError("E007", "S2-GI result changed during projection")
    return _finish_compact(
        recorder, row, result, receipt, semantic_digest, COMPACT_S2GI_MAX_ARTIFACT_BYTES
    )


def _record(
    recorder: recording.AppendOnlyRunRecorder,
    operation_class: str,
    source: dict[str, object],
    function: Callable[[], object],
    *,
    history: str | None = None,
    source_ordinal: str | None = None,
) -> object:
    row = recorder._row()
    _require(row["operation_class"] == operation_class, "registered operation class differs")
    if history is not None:
        _require(row["history"] == history, "registered operation history differs")
    if source_ordinal is not None:
        _require(row["source_ordinal"] == source_ordinal, "registered source ordinal differs")
    operation_id = row["operation_id"]
    recorder.start(operation_id, source)
    result = function()
    recorder.finish(operation_id, {"result": _canonical(result)})
    return result


def _masked_probe(source: _BoundSource) -> consumer.MaskedVisualProbe:
    _require(type(source.bound) is coordinator.B4TSPM1BoundProbe, "masked source differs")
    values = tuple(value if index in consumer.VISIBLE_POSITIONS else None for index, value in enumerate(source.bound.visual_values))
    return consumer.MaskedVisualProbe.build(values, fixtures.MASKED_SOURCE_DIGEST)


def _execute(recorder: recording.AppendOnlyRunRecorder, runtime: _Runtime, evaluation_plan: EvaluationPlanSeal) -> None:
    states = {history.history_id: coordinator.initial_composite_state(runtime.coordinator_config) for history in fixtures.HISTORIES}
    findings: dict[str, coordinator.B4TSPM1ReadOnlyFinding] = {}
    finding_artifact_digests: dict[str, str] = {}
    full_sources: dict[str, _BoundSource] = {}
    bundles: dict[str, context_bundle.PerceptualContextBundle] = {}
    bundle_artifact_digests: dict[str, str] = {}
    projections: dict[str, two_area.TwoAreaContextBundle] = {}
    projection_artifact_digests: dict[str, str] = {}
    formation_artifact_digests: dict[str, str] = {}
    arms: dict[str, object] = {}

    for history in fixtures.HISTORIES:
        for step in history.steps:
            source_id = f"s2gt.{history.history_id}.formation.{step.ordinal:02d}"
            recorded_source = _record_receptor(recorder, "FORMATION_RECEPTOR_ANALYSIS", {"source_id": source_id, "history": history.history_id, "ordinal": step.ordinal}, lambda h=history, s=step, sid=source_id: _analyze(runtime, sid, s.visual_fixture_id, s.auditory_fixture_id, s.window_start, s.window_end, "FORMATION"), history=history.history_id, source_ordinal=f"{step.ordinal:03d}")
            source = recorded_source.source
            recorded_result = _record_compact_formation(
                recorder,
                {
                    "source_digest": source.source_digest,
                    "receptor_receipt_digest": recorded_source.receptor_receipt_digest,
                    "prestate_digest": states[history.history_id].state_digest,
                    "previous_formation_receipt_digest": formation_artifact_digests.get(history.history_id),
                },
                lambda h=history, s=source, n=step.ordinal: _formation(runtime, states[h.history_id], s, f"{h.history_id}.{n:02d}"),
                source,
                recorded_source.receptor_receipt_digest,
                history=history.history_id,
                source_ordinal=f"{step.ordinal:03d}",
            )
            _require(type(recorded_result.result) is coordinator.B4TSPM1StepResult, "formation result type differs")
            result = recorded_result.result
            formation_artifact_digests[history.history_id] = recorded_result.receipt_artifact_digest
            states[history.history_id] = result.poststate

    for history in fixtures.HISTORIES:
        source_id = f"s2gt.{history.history_id}.probe.full.01"
        recorded_source = _record_receptor(recorder, "CONTEXT_RETRIEVAL_RECEPTOR_ANALYSIS", {"source_id": source_id, "history": history.history_id, "ordinal": 14}, lambda h=history, sid=source_id: _analyze(runtime, sid, h.full_probe_visual_id, h.full_probe_auditory_id, 13, 14, "READ_ONLY"), history=history.history_id, source_ordinal="014")
        source = recorded_source.source
        full_sources[history.history_id] = source
        finding_operation_id = recorder._row()["operation_id"]
        finding = _record(recorder, "COMPOSITE_READ_ONLY_PROBE", {"source_digest": source.source_digest, "receptor_receipt_digest": recorded_source.receptor_receipt_digest, "state_digest": states[history.history_id].state_digest}, lambda h=history, s=source: _probe(runtime, states[h.history_id], s), history=history.history_id, source_ordinal="014")
        _require(type(finding) is coordinator.B4TSPM1ReadOnlyFinding, "read-only finding type differs")
        findings[history.history_id] = finding
        finding_artifact_digest = recorder.result_digests.get(finding_operation_id)
        _require(_valid_digest(finding_artifact_digest), "read-only finding artifact digest differs")
        finding_artifact_digests[history.history_id] = finding_artifact_digest

    recorded_shared_source = _record_receptor(recorder, "CONSUMER_RECEPTOR_ANALYSIS", {"source_id": "s2gt.shared.consumer.01"}, lambda: _analyze(runtime, "s2gt.shared.consumer.01", "J1-T", "Q0", 14, 15, "READ_ONLY"), history="shared", source_ordinal="001")
    shared_source = recorded_shared_source.source
    masked_probe = _record(recorder, "MASKED_PROBE_BIND", {"source_digest": shared_source.source_digest, "receptor_receipt_digest": recorded_shared_source.receptor_receipt_digest}, lambda: _masked_probe(shared_source), history="shared", source_ordinal="001")

    for history in fixtures.HISTORIES:
        binding = _projection_binding(runtime, states[history.history_id], full_sources[history.history_id])
        sequence = context_bundle.ValidatedB4ShortSequenceEvidence.build("NOT_REQUESTED", findings[history.history_id].b4_recent.observed_state_digest, findings[history.history_id].probe_digest)
        recorded_bundle = _record_compact_s2gc(
            recorder,
            {
                "finding_digest": findings[history.history_id].finding_digest,
                "finding_receipt_digest": finding_artifact_digests[history.history_id],
            },
            lambda b=binding, h=history, s=sequence: context_bundle.project_perceptual_context_bundle(b, findings[h.history_id], s),
            findings[history.history_id],
            sequence,
            finding_artifact_digests[history.history_id],
            history=history.history_id,
        )
        _require(type(recorded_bundle.result) is context_bundle.PerceptualContextBundle, "S2-GC result type differs")
        bundles[history.history_id] = recorded_bundle.result
        bundle_artifact_digests[history.history_id] = recorded_bundle.receipt_artifact_digest
    for history in fixtures.HISTORIES:
        recorded_projection = _record_compact_s2gi(
            recorder,
            {
                "bundle_digest": bundles[history.history_id].bundle_digest,
                "s2gc_receipt_digest": bundle_artifact_digests[history.history_id],
            },
            lambda h=history: two_area.project_two_area_context(bundles[h.history_id]),
            bundles[history.history_id],
            bundle_artifact_digests[history.history_id],
            history=history.history_id,
        )
        _require(type(recorded_projection.result) is two_area.TwoAreaContextBundle, "S2-GI result type differs")
        projections[history.history_id] = recorded_projection.result
        projection_artifact_digests[history.history_id] = recorded_projection.receipt_artifact_digest

    arms["a01"] = _record(recorder, "ARM_EXECUTION", {"masked_probe_digest": masked_probe.probe_digest}, lambda: consumer.current_perception_only(masked_probe), history="a01")
    for arm_id, method, history_id in fixtures.ARM_BINDINGS[1:]:
        projection = projections[history_id]
        binding = consumer.ContextUseBinding.build(masked_probe, projection)
        if method == "CONTEXT_CONSUMER":
            function = lambda p=projection, b=binding: consumer.complete_with_named_b_stable(masked_probe, p, b)
        else:
            function = lambda p=projection, b=binding: direct_baseline.direct_b_stable_mask_fill(masked_probe, p, b)
        arms[arm_id] = _record(recorder, "ARM_EXECUTION", {"masked_probe_digest": masked_probe.probe_digest, "context_bundle_digest": projection.bundle_digest, "context_receipt_digest": projection_artifact_digests[history_id]}, function, history=arm_id)

    execution_package = _record(
        recorder,
        "EXECUTION_EVIDENCE_SEAL",
        {"receipt_count": 130},
        lambda: {
            "operation_result_digests": tuple(
                sorted(
                    (key, value)
                    for key, value in recorder.result_digests.items()
                    if key.startswith("op-") and int(key[3:]) <= 130
                )
            ),
            "last_execution_event_digest": recorder.previous_event_digest,
            "execution_only": True,
        },
    )
    evaluation_binding = _record(recorder, "EVALUATION_RUN_BIND", {"execution_package_digest": fixtures.canonical_digest(_canonical(execution_package)), "external_evaluation_plan_digest": evaluation_plan.seal_digest}, lambda: {"execution_package_digest": fixtures.canonical_digest(_canonical(execution_package)), "evaluation_plan_digest": evaluation_plan.seal_digest})

    evaluations: dict[str, object] = {}
    for evaluation_id, case_kind, arm_ids, target_id in evaluation_plan.case_bindings:
        target = evaluator.MaskedVisualTargetFixture.build(fixtures.VISUAL_BY_ID[target_id].values)
        current = arms[arm_ids[0]]
        context_result = arms[arm_ids[1]]
        baseline_result = arms[arm_ids[2]] if len(arm_ids) == 3 else None
        evaluations[evaluation_id] = _record(recorder, "PURE_EVALUATION", {"evaluation_binding": evaluation_binding, "case_id": evaluation_id}, lambda k=case_kind, t=target, c=current, r=context_result, b=baseline_result: evaluator.evaluate_completion_case(k, t, c, r, b), history=evaluation_id)

    final_evidence = _record(recorder, "FINAL_EVIDENCE_PUBLISH", {"evaluation_count": 4}, lambda: {"execution_package": execution_package, "evaluation_binding": evaluation_binding, "evaluations": _canonical(evaluations)})
    completion_candidate = _record(recorder, "TERMINAL_PUBLISH", {"final_evidence_digest": fixtures.canonical_digest(_canonical(final_evidence))}, lambda: {"status": "COMPLETING", "final_evidence_digest": fixtures.canonical_digest(_canonical(final_evidence)), "recorded_operations": 138})
    _record(recorder, "COMPLETION_MARKER_PUBLISH", {"completion_candidate_digest": fixtures.canonical_digest(_canonical(completion_candidate))}, lambda: {"status": "COMPLETE", "recorded_operations": 139, "recorded_events": 278})


def _failure_code_for_exception(
    recorder: recording.AppendOnlyRunRecorder,
    error: Exception,
) -> str:
    if not isinstance(error, recording.S2GTRecordingError):
        return "E009"
    matches = tuple(
        row
        for row in recorder.registry.error_code_rows
        if row["error_code"] == error.code
    )
    if len(matches) != 1:
        return "E009"
    registered = matches[0]
    if recorder.state not in registered["allowed_phase"].split("|"):
        return "E002"
    try:
        current = recorder._row()
    except recording.S2GTRecordingError:
        return "E002"
    if (
        current["failure_successor"] != registered["failure_successor"]
        or (
            recorder.pending_start is not None
            and recorder.pending_start[0] != current["operation_id"]
        )
    ):
        return "E002"
    return error.code


def run_main_once(output_root: Path, workspace_root: Path, run_id: str, owner_id: str, evaluation_plan: EvaluationPlanSeal) -> Path:
    """Future one-shot entry. S2-GT intentionally leaves this gate closed."""

    if MAIN_EXECUTION_ENABLED is not True:
        raise S2GTRunnerError("S2-GT main execution is not authorized")
    if type(evaluation_plan) is not EvaluationPlanSeal or evaluation_plan != build_evaluation_plan_seal():
        raise S2GTRunnerError("independent evaluation plan binding differs")
    plan, registry = materialize_execution_plan(workspace_root, run_id, owner_id)
    recorder = recording.AppendOnlyRunRecorder.reserve(output_root, plan, registry)
    if isinstance(recorder, recording.StartBlocked):
        raise S2GTRunnerError("S2-GT start blocked before run reservation")
    if recorder.state == "NOT_EVALUABLE":
        raise S2GTRunnerError("S2-GT stopped after reservation")
    try:
        _execute(recorder, _runtime(), evaluation_plan)
    except Exception as error:
        if recorder.state not in recording.TERMINAL_STATES:
            recorder.fail(
                _failure_code_for_exception(recorder, error),
                recorder._row()["operation_id"],
            )
        raise
    _require(recorder.state == "COMPLETE" and recorder.event_count == 278, "S2-GT completion evidence differs")
    return recorder.run_directory


__all__: tuple[str, ...] = ()
