"""Closed private S2-HU runner for the bounded S2-HS role-conflict run."""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
import hashlib
from pathlib import Path
import re
from typing import Callable

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
from mcm_field_organism.receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeSequence,
)
from tools import _s2fs_b4_tspm1_private_coordinator as coordinator
from tools import _s2gb_private_perceptual_context_bundle as context_bundle
from tools import _s2gi_private_two_area_context_projection as two_area
from tools import _s2gk_private_masked_visual_context_consumer as probe_contract
from tools import _s2hq_private_byte_block_conflict_fixture as conflict_fixture
from tools import _s2hq_private_direct_role_addressed_mask_fill_baseline as baseline
from tools import _s2hq_private_role_addressed_context_consumer as consumer
from tools import _s2hu_private_append_only_recorder as recording
from tools import _s2hu_private_fixture_registry as fixtures


RUNNER_SCHEMA = "s2hu.private.runner.v1"
MAIN_EXECUTION_ENABLED = False
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_PROFILE_PARAMETERS = PPB1ProfileParameters(
    PPB1ModalityParameters(8, 0.02, 0.05, 3, 256),
    PPB1ModalityParameters(4, 0.01, 0.05, 3, 64),
)
_VISUAL_CONFIG = VisualGridConfig(120, 80, 3, 2, 30.0)


class S2HURunnerError(RuntimeError):
    """One closed runner-boundary error."""


@dataclass(frozen=True, slots=True)
class EvaluationCaseBinding:
    case_id: str
    expected_visual_values: tuple[float, ...]
    binding_digest: str

    @classmethod
    def build(
        cls, case_id: str, expected_visual_values: tuple[float, ...]
    ) -> "EvaluationCaseBinding":
        if (
            case_id not in fixtures.CASE_BY_ID
            or type(expected_visual_values) is not tuple
            or len(expected_visual_values) != 18
            or any(type(value) is not float for value in expected_visual_values)
        ):
            raise S2HURunnerError("evaluation case binding differs")
        payload = {
            "schema": "s2hs.evaluation-case-binding.v1",
            "case_id": case_id,
            "expected_visual_values": expected_visual_values,
        }
        return cls(case_id, expected_visual_values, fixtures.canonical_digest(payload))


@dataclass(frozen=True, slots=True)
class EvaluationPlanSeal:
    plan_id: str
    case_bindings: tuple[EvaluationCaseBinding, ...]
    evaluation_source_digests: tuple[tuple[str, str], ...]
    seal_digest: str
    schema: str = "s2hs.evaluation-plan-seal.v1"


def bind_evaluation_plan(
    plan_id: str,
    case_bindings: tuple[EvaluationCaseBinding, ...],
    evaluation_source_digests: tuple[tuple[str, str], ...],
) -> EvaluationPlanSeal:
    """Bind an external evaluation root without execution provenance."""

    if (
        not isinstance(plan_id, str)
        or re.fullmatch(r"[a-z][a-z0-9-]{7,95}", plan_id) is None
        or type(case_bindings) is not tuple
        or tuple(item.case_id for item in case_bindings) != ("c01", "c02", "c03", "c04")
        or len({item.binding_digest for item in case_bindings}) != 4
        or type(evaluation_source_digests) is not tuple
        or not evaluation_source_digests
        or any(_DIGEST.fullmatch(digest) is None for _, digest in evaluation_source_digests)
    ):
        raise S2HURunnerError("evaluation plan is incomplete")
    payload = {
        "schema": "s2hs.evaluation-plan-seal.v1",
        "plan_id": plan_id,
        "case_binding_digests": tuple(item.binding_digest for item in case_bindings),
        "evaluation_source_digests": evaluation_source_digests,
    }
    return EvaluationPlanSeal(
        plan_id,
        case_bindings,
        evaluation_source_digests,
        fixtures.canonical_digest(payload),
    )


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
    raw_sha256: str
    source_digest: str


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
        raise S2HURunnerError(message)


def _source_paths(workspace_root: Path) -> tuple[tuple[str, Path], ...]:
    """Execution sources deliberately exclude the evaluation verifier."""

    return (
        ("fixture_registry", workspace_root / "tools/_s2hu_private_fixture_registry.py"),
        ("runner", workspace_root / "tools/_s2hu_private_runner.py"),
        ("recorder", workspace_root / "tools/_s2hu_private_append_only_recorder.py"),
        ("conflict_fixture", workspace_root / "tools/_s2hq_private_byte_block_conflict_fixture.py"),
        ("coordinator", workspace_root / "tools/_s2fs_b4_tspm1_private_coordinator.py"),
        ("context_bundle", workspace_root / "tools/_s2gb_private_perceptual_context_bundle.py"),
        ("two_area", workspace_root / "tools/_s2gi_private_two_area_context_projection.py"),
        ("consumer", workspace_root / "tools/_s2hq_private_role_addressed_context_consumer.py"),
        ("baseline", workspace_root / "tools/_s2hq_private_direct_role_addressed_mask_fill_baseline.py"),
    )


def materialize_execution_plan(
    workspace_root: Path, run_id: str, owner_id: str
) -> tuple[recording.ExecutionPlan, fixtures.RegistryBundle]:
    fixtures.validate_literal_fixtures()
    registry = fixtures.load_operation_registry(workspace_root)
    source_digests = tuple(
        (path.relative_to(workspace_root).as_posix(), fixtures.file_digest(path))
        for _, path in _source_paths(workspace_root)
    )
    return recording.ExecutionPlan.build(run_id, owner_id, registry, source_digests), registry


def _runtime() -> _Runtime:
    profile = bind_ppb1_receptor_profile("browser", _PROFILE_PARAMETERS)
    tspm_config = tspm1.TSPM1ConfigBinding.build(
        tspm1.TSPM1FastConfig("tspm1.fast", 3, 0.2, 0.2, 0.5, 2, 8),
        profile,
    )
    coordinator_config = coordinator.build_coordinator_config(tspm_config)
    world = BrowserWorldContract(
        contract_id="synthetic.s2hu.world.v1",
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
    return _Runtime(
        profile,
        tspm_config,
        coordinator_config,
        world,
        LocalChannelGridReceptor(_VISUAL_CONFIG),
    )


def _timed(
    frame: ReceptorContactFrame, field_time: CommonFieldTime
) -> ReceptorTimeSequence:
    return ReceptorTimeSequence(
        frame.modality_id,
        frame.geometry_id,
        field_time.clock_id,
        (OrganismTimedReceptorFrame(frame, field_time),),
    )


def _analyze(
    runtime: _Runtime,
    source_id: str,
    visual_id: str,
    auditory_id: str,
    start_tick: int,
    end_tick: int,
    role: str,
) -> _BoundSource:
    visual_fixture = conflict_fixture.VISUAL_BY_ID[visual_id]
    auditory_fixture = conflict_fixture.AUDITORY_BY_ID[auditory_id]
    image = conflict_fixture.materialize_uint8_image(visual_fixture)
    raw_sha256 = hashlib.sha256(image.tobytes()).hexdigest()
    receptor_state = runtime.receptor.analyze(image, frame_index=runtime.image_serial)
    runtime.image_serial += 1
    visual_values = tuple(receptor_state.channel_values)
    _require(
        visual_values == visual_fixture.receptor_values,
        "visual receptor values differ",
    )
    auditory_frame = ReceptorContactFrame(
        "auditory",
        runtime.profile.auditory_config.geometry_id,
        f"{source_id}.auditory",
        "s2hu.auditory.clock",
        start_tick,
        end_tick,
        runtime.profile.auditory_config.carrier_ids,
        auditory_fixture.values,
    )
    visual_frame = ReceptorContactFrame(
        "visual",
        runtime.profile.visual_config.geometry_id,
        f"{source_id}.visual",
        "s2hu.visual.clock",
        start_tick,
        end_tick,
        runtime.profile.visual_config.carrier_ids,
        visual_values,
    )
    field_time = CommonFieldTime("s2hu.field.clock", start_tick, end_tick)
    batch = BrowserReceptorSequenceBatch(
        runtime.world.contract_id,
        runtime.world.digest(),
        (_timed(auditory_frame, field_time), _timed(visual_frame, field_time)),
    )
    _require(batch.raw_payloads_retained is False, "raw payload retention differs")
    envelope = bind_ppb1_active_receptor_batch(
        f"{source_id}.binding", runtime.world, batch, runtime.profile
    )
    auditory = envelope.auditory_stream.timed_frames[0]
    visual = envelope.visual_stream.timed_frames[0]
    if role == "FORMATION":
        bound = coordinator.bind_coordinator_input(
            runtime.coordinator_config, envelope, auditory, visual
        )
        bound_digest = bound.input_digest
    elif role == "READ_ONLY":
        bound = coordinator.bind_coordinator_probe(
            runtime.coordinator_config, envelope, auditory, visual
        )
        bound_digest = bound.probe_digest
    else:
        raise S2HURunnerError("unknown source role")
    source_digest = fixtures.canonical_digest(
        {
            "schema": RUNNER_SCHEMA,
            "source_id": source_id,
            "role": role,
            "visual_fixture_id": visual_id,
            "auditory_fixture_id": auditory_id,
            "window": [start_tick, end_tick],
            "raw_sha256": raw_sha256,
            "bound_digest": bound_digest,
        }
    )
    return _BoundSource(
        role,
        source_id,
        visual_id,
        auditory_id,
        start_tick,
        end_tick,
        envelope,
        bound,
        raw_sha256,
        source_digest,
    )


def _formation(
    runtime: _Runtime,
    state: coordinator.B4TSPM1CompositeState,
    source: _BoundSource,
    owner_suffix: str,
) -> coordinator.B4TSPM1StepResult:
    _require(type(source.bound) is coordinator.B4TSPM1BoundInput, "formation source differs")
    owner = coordinator.B4TSPM1CoordinatorOwner(
        f"s2hu.owner.{owner_suffix}",
        f"s2hu.authorization.{owner_suffix}",
        f"s2hu.consumption.{owner_suffix}",
        runtime.coordinator_config.config_digest,
        state.state_digest,
        source.bound.input_digest,
    )
    return owner.consume_once(runtime.coordinator_config, state, source.bound)


def _probe(
    runtime: _Runtime,
    state: coordinator.B4TSPM1CompositeState,
    source: _BoundSource,
) -> coordinator.B4TSPM1ReadOnlyFinding:
    _require(type(source.bound) is coordinator.B4TSPM1BoundProbe, "probe source differs")
    return coordinator.probe_composite_read_only(
        runtime.coordinator_config, state, source.bound
    )


def _projection_binding(
    runtime: _Runtime,
    state: coordinator.B4TSPM1CompositeState,
    source: _BoundSource,
) -> context_bundle.PerceptualContextProjectionBinding:
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


def _record(
    recorder: recording.AppendOnlyRunRecorder,
    payload: dict[str, object],
    function: Callable[[], object],
    projector: Callable[[object], dict[str, object]],
    *,
    external_parent_digest: str | None = None,
) -> object:
    row = recorder.current_row()
    recorder.start(
        row.operation_id, payload, external_parent_digest=external_parent_digest
    )
    result = function()
    receipt = projector(result)
    recorder.finish(row.operation_id, {"result": receipt})
    return result


def _receptor_receipt(source: _BoundSource) -> dict[str, object]:
    bound = source.bound
    return {
        "schema": "s2hu.compact-receptor-receipt.v1",
        "source_id": source.source_id,
        "source_role": source.role,
        "visual_fixture_id": source.visual_fixture_id,
        "auditory_fixture_id": source.auditory_fixture_id,
        "window": [source.window_start, source.window_end],
        "raw_image_sha256": source.raw_sha256,
        "envelope_digest": source.envelope.envelope_digest,
        "config_digest": bound.config_digest,
        "auditory_values_digest": fixtures.canonical_digest(list(bound.auditory_values)),
        "visual_values_digest": fixtures.canonical_digest(list(bound.visual_values)),
        "av_values_digest": bound.values_digest,
        "bound_digest": (
            bound.input_digest
            if type(bound) is coordinator.B4TSPM1BoundInput
            else bound.probe_digest
        ),
        "source_digest": source.source_digest,
    }


def _formation_receipt(result: object) -> dict[str, object]:
    _require(type(result) is coordinator.B4TSPM1StepResult, "formation result differs")
    return {
        "schema": "s2hu.compact-formation-receipt.v1",
        "prestate_digest": result.receipt.composite_prestate_digest,
        "poststate_digest": result.poststate.state_digest,
        "input_digest": result.receipt.input_digest,
        "b4_event": result.receipt.b4_event,
        "b4_state_digest": result.receipt.b4_poststate_digest,
        "tspm_result_digest": result.receipt.tspm_result_digest,
        "tspm_state_digest": result.receipt.tspm_poststate_digest,
        "step_receipt_digest": result.receipt.receipt_digest,
        "owner_prestate_digest": result.receipt.owner_prestate_digest,
        "owner_poststate_digest": result.owner_poststate.owner_state_digest,
        "owner_status": result.owner_poststate.status,
        "generation": result.poststate.generation,
        "resource_ledger_digest": result.resource_ledger.ledger_digest,
        "result_digest": result.result_digest,
    }


def _finding_receipt(result: object) -> dict[str, object]:
    _require(type(result) is coordinator.B4TSPM1ReadOnlyFinding, "finding differs")
    fast = result.tspm_fast
    slow = result.tspm_slow
    return {
        "schema": "s2hu.read-only-finding-receipt.v1",
        "finding_digest": result.finding_digest,
        "probe_digest": result.probe_digest,
        "prestate_digest": result.prestate_digest,
        "poststate_digest": result.poststate_digest,
        "b4_recognized": result.b4_recent.recognized,
        "b4_values": (
            None if result.b4_recent.selected is None else result.b4_recent.selected.values
        ),
        "b4_state_digest": result.b4_recent.observed_state_digest,
        "fast_slot_digest": None if fast is None else fast.slot_digest,
        "fast_values": (
            None if fast is None else fast.auditory_values + fast.visual_values
        ),
        "slow_bank_state_digests": tuple(item.observed_bank_state_digest for item in slow),
        "slow_selected_prototype_digests": tuple(
            None if item.selected is None else item.selected.slot_digest
            for item in slow
        ),
        "slow_selected_values": tuple(
            None if item.selected is None else item.selected.prototype_values
            for item in slow
        ),
        "slow_selected_supports": tuple(
            None if item.selected is None else item.selected.support_count
            for item in slow
        ),
        "resource_ledger_digest": result.resource_ledger.ledger_digest,
    }


def _bundle_receipt(result: object) -> dict[str, object]:
    _require(type(result) is context_bundle.PerceptualContextBundle, "S2-GC bundle differs")
    return {
        "schema": "s2hu.compact-s2gc-receipt.v1",
        "bundle_digest": result.bundle_digest,
        "binding_digest": result.binding_digest,
        "state_digest": result.composite_state_digest,
        "probe_digest": result.probe_digest,
        "role_statuses": tuple(item.status for item in result.role_findings),
        "role_finding_digests": tuple(item.finding_digest for item in result.role_findings),
        "candidate_digests": tuple(
            None if item.candidate is None else item.candidate.candidate_digest
            for item in result.role_findings
        ),
        "component_values": tuple(
            tuple(component.values)
            for item in result.role_findings
            if item.candidate is not None
            for component in item.candidate.components
        ),
        "sequence_status": result.sequence_finding.status,
        "prestate_digest": result.prestate_digest,
        "poststate_digest": result.poststate_digest,
        "resource_ledger_digest": result.resource_ledger.ledger_digest,
    }


def _area_receipt(result: object) -> dict[str, object]:
    _require(type(result) is two_area.TwoAreaContextBundle, "S2-GI bundle differs")
    return {
        "schema": "s2hu.compact-s2gi-receipt.v1",
        "bundle_digest": result.bundle_digest,
        "source_bundle_digest": result.source_bundle_digest,
        "state_digest": result.composite_state_digest,
        "probe_digest": result.probe_digest,
        "areas": tuple(item.area for item in result.area_findings),
        "area_finding_digests": tuple(item.finding_digest for item in result.area_findings),
        "a_recent_status": result.area_findings[0].recent_content.status,
        "a_fast_status": result.area_findings[0].fast_internal.status,
        "b_stable_status": result.area_findings[1].stable_content.status,
        "b_candidate_digest": (
            None
            if result.area_findings[1].stable_content.candidate is None
            else result.area_findings[1].stable_content.candidate.candidate_digest
        ),
        "prestate_digest": result.prestate_digest,
        "poststate_digest": result.poststate_digest,
        "resource_ledger_digest": result.resource_ledger.ledger_digest,
        "automatic_selection": result.automatic_selection,
    }


def _result_receipt(result: object) -> dict[str, object]:
    return {
        "schema": "s2hu.role-arm-receipt.v1",
        "method": getattr(result, "method"),
        "status": getattr(result, "status"),
        "requested_area": getattr(result, "requested_area"),
        "probe_digest": getattr(result, "probe_digest"),
        "input_values": getattr(result, "input_values"),
        "output_values": getattr(result, "output_values"),
        "completed_positions": getattr(result, "completed_positions"),
        "context_bundle_digest": getattr(result, "context_bundle_digest"),
        "selected_area_finding_digest": getattr(result, "selected_area_finding_digest"),
        "prestate_digest": getattr(result, "prestate_digest"),
        "poststate_digest": getattr(result, "poststate_digest"),
        "resource_ledger_digest": getattr(result, "resource_ledger").ledger_digest,
        "result_digest": getattr(result, "result_digest"),
    }


def _masked_probe() -> probe_contract.MaskedVisualProbe:
    return probe_contract.MaskedVisualProbe.build(
        conflict_fixture.MASKED_VISUAL_VALUES,
        fixtures.MASKED_PROBE_SOURCE_DIGEST,
    )


def _execute(
    recorder: recording.AppendOnlyRunRecorder,
    runtime: _Runtime,
    evaluation_plan: EvaluationPlanSeal,
) -> None:
    manifest = {
        "execution_plan": recorder.plan.payload(),
        "registry_source_digest": recorder.registry.source_digest,
        "registry_bundle_digest": recorder.registry.bundle_digest,
        "execution_fixture_digest": fixtures.EXECUTION_FIXTURE_DIGEST,
    }
    _record(recorder, {"plan_digest": recorder.plan.plan_digest}, lambda: manifest, lambda value: value)
    masked_probe = _record(
        recorder,
        {"masked_probe_source_digest": fixtures.MASKED_PROBE_SOURCE_DIGEST},
        _masked_probe,
        lambda result: {
            "schema": "s2hu.masked-probe-receipt.v1",
            "probe_digest": result.probe_digest,
            "source_digest": result.source_digest,
            "mask": tuple(value is None for value in result.values),
        },
    )

    states: dict[str, coordinator.B4TSPM1CompositeState] = {}
    findings: dict[str, coordinator.B4TSPM1ReadOnlyFinding] = {}
    bundles: dict[str, context_bundle.PerceptualContextBundle] = {}
    areas: dict[str, two_area.TwoAreaContextBundle] = {}
    history_evidence: dict[str, dict[str, object]] = {}
    case_evidence: dict[str, dict[str, object]] = {}

    for history in fixtures.HISTORIES:
        state = _record(
            recorder,
            {"history_digest": history.history_digest},
            lambda: coordinator.initial_composite_state(runtime.coordinator_config),
            lambda result: {
                "schema": "s2hu.history-initial-receipt.v1",
                "history_digest": history.history_digest,
                "state_digest": result.state_digest,
                "generation": result.generation,
            },
        )
        _require(type(state) is coordinator.B4TSPM1CompositeState, "initial state differs")
        stable_before_recent: tuple[str, str] | None = None
        for step in history.steps:
            source_id = f"s2hu.{history.history_id}.formation.{step.ordinal:02d}"
            source = _record(
                recorder,
                {"source_id": source_id, "history_id": history.history_id},
                lambda s=step, sid=source_id: _analyze(
                    runtime,
                    sid,
                    s.visual_fixture_id,
                    s.auditory_fixture_id,
                    s.window_start,
                    s.window_end,
                    "FORMATION",
                ),
                lambda result: _receptor_receipt(result),
            )
            result = _record(
                recorder,
                {
                    "source_digest": source.source_digest,
                    "prestate_digest": state.state_digest,
                },
                lambda s=source, n=step.ordinal, pre=state: _formation(
                    runtime, pre, s, f"{history.history_id}.{n:02d}"
                ),
                _formation_receipt,
            )
            _require(type(result) is coordinator.B4TSPM1StepResult, "formation differs")
            state = result.poststate
            if step.ordinal == 4:
                stable_before_recent = (
                    state.tspm_state.auditory_ppb1_state.digest(),
                    state.tspm_state.visual_ppb1_state.digest(),
                )
        states[history.history_id] = state
        probe_id = f"s2hu.{history.history_id}.probe.full.01"
        source = _record(
            recorder,
            {"source_id": probe_id, "history_id": history.history_id},
            lambda h=history, sid=probe_id: _analyze(
                runtime,
                sid,
                h.full_probe_visual_id,
                h.full_probe_auditory_id,
                h.probe_window_start,
                h.probe_window_end,
                "READ_ONLY",
            ),
            lambda result: _receptor_receipt(result),
        )
        finding = _record(
            recorder,
            {"source_digest": source.source_digest, "state_digest": state.state_digest},
            lambda s=source, pre=state: _probe(runtime, pre, s),
            _finding_receipt,
        )
        findings[history.history_id] = finding
        binding = _projection_binding(runtime, state, source)
        sequence = context_bundle.ValidatedB4ShortSequenceEvidence.build(
            "NOT_REQUESTED",
            finding.b4_recent.observed_state_digest,
            finding.probe_digest,
        )
        bundle = _record(
            recorder,
            {"finding_digest": finding.finding_digest, "binding_digest": binding.binding_digest},
            lambda b=binding, f=finding, s=sequence: context_bundle.project_perceptual_context_bundle(b, f, s),
            _bundle_receipt,
        )
        bundles[history.history_id] = bundle
        area = _record(
            recorder,
            {"source_bundle_digest": bundle.bundle_digest},
            lambda b=bundle: two_area.project_two_area_context(b),
            _area_receipt,
        )
        areas[history.history_id] = area
        _require(stable_before_recent is not None, "stable checkpoint missing")
        stable_after_recent = (
            state.tspm_state.auditory_ppb1_state.digest(),
            state.tspm_state.visual_ppb1_state.digest(),
        )
        evidence = {
            "schema": "s2hu.history-evidence.v1",
            "history_id": history.history_id,
            "generation": state.generation,
            "stable_bank_unchanged_by_recent": stable_before_recent == stable_after_recent,
            "stable_bank_digests": stable_after_recent,
            "a_recent_status": area.area_findings[0].recent_content.status,
            "b_stable_status": area.area_findings[1].stable_content.status,
            "read_only": finding.prestate_digest == finding.poststate_digest == state.state_digest,
            "bundle_digest": bundle.bundle_digest,
            "area_bundle_digest": area.bundle_digest,
        }
        history_evidence[history.history_id] = _record(
            recorder,
            {"history_id": history.history_id},
            lambda e=evidence: e,
            lambda value: value,
        )

    for case in fixtures.DIRECTED_CASES:
        area = areas[case.history_id]
        binding = _record(
            recorder,
            {
                "case_digest": case.case_digest,
                "history_evidence_digest": fixtures.canonical_digest(history_evidence[case.history_id]),
            },
            lambda c=case, a=area: consumer.RoleAddressedContextUseBinding.build(
                masked_probe, a, c.requested_area
            ),
            lambda result: {
                "schema": "s2hu.role-binding-receipt.v1",
                "case_id": case.case_id,
                "requested_area": result.requested_area,
                "probe_digest": result.current_probe_digest,
                "context_bundle_digest": result.context_bundle_digest,
                "selected_area_finding_digest": result.selected_area_finding_digest,
                "binding_digest": result.binding_digest,
            },
        )
        consumer_result = _record(
            recorder,
            {"binding_digest": binding.binding_digest},
            lambda a=area, b=binding: consumer.complete_from_explicit_area(masked_probe, a, b),
            _result_receipt,
        )
        baseline_result = _record(
            recorder,
            {"binding_digest": binding.binding_digest},
            lambda a=area, b=binding: baseline.direct_fill_from_explicit_area(masked_probe, a, b),
            _result_receipt,
        )
        evidence = {
            "schema": "s2hu.case-evidence.v1",
            "case_id": case.case_id,
            "history_id": case.history_id,
            "requested_area": case.requested_area,
            "binding_digest": binding.binding_digest,
            "consumer_result_digest": consumer_result.result_digest,
            "baseline_result_digest": baseline_result.result_digest,
            "consumer_output": consumer_result.output_values,
            "baseline_output": baseline_result.output_values,
            "same_output": consumer_result.output_values == baseline_result.output_values,
            "consumer_read_only": consumer_result.prestate_digest == consumer_result.poststate_digest,
            "baseline_read_only": baseline_result.prestate_digest == baseline_result.poststate_digest,
        }
        case_evidence[case.case_id] = _record(
            recorder,
            {"case_id": case.case_id},
            lambda e=evidence: e,
            lambda value: value,
        )

    execution_package = _record(
        recorder,
        {"execution_operation_count": 51},
        lambda: {
            "schema": "s2hu.execution-evidence-package.v1",
            "execution_plan_digest": recorder.plan.plan_digest,
            "history_evidence_digests": tuple(
                fixtures.canonical_digest(history_evidence[key]) for key in ("h0", "h1")
            ),
            "case_evidence_digests": tuple(
                fixtures.canonical_digest(case_evidence[key])
                for key in ("c01", "c02", "c03", "c04")
            ),
            "last_execution_event_digest": recorder.previous_event_digest,
            "evaluation_plan_digest": None,
        },
        lambda value: value,
    )
    evaluation_binding = _record(
        recorder,
        {
            "execution_package_digest": fixtures.canonical_digest(execution_package),
            "evaluation_plan_digest": evaluation_plan.seal_digest,
        },
        lambda: {
            "schema": "s2hu.evaluation-run-binding.v1",
            "execution_package_digest": fixtures.canonical_digest(execution_package),
            "evaluation_plan_digest": evaluation_plan.seal_digest,
            "binding_digest": fixtures.canonical_digest(
                [fixtures.canonical_digest(execution_package), evaluation_plan.seal_digest]
            ),
        },
        lambda value: value,
        external_parent_digest=evaluation_plan.seal_digest,
    )
    evaluations: dict[str, dict[str, object]] = {}
    binding_by_case = {item.case_id: item for item in evaluation_plan.case_bindings}
    for case_id in ("c01", "c02", "c03", "c04"):
        evidence = case_evidence[case_id]
        expected = binding_by_case[case_id].expected_visual_values
        output = tuple(evidence["consumer_output"])
        baseline_output = tuple(evidence["baseline_output"])
        visible_unchanged = all(
            output[index] == conflict_fixture.MASKED_VISUAL_VALUES[index]
            for index in probe_contract.VISIBLE_POSITIONS
        )
        finding = {
            "schema": "s2hu.evaluation-finding.v1",
            "case_id": case_id,
            "evaluation_binding_digest": evaluation_binding["binding_digest"],
            "expected_values_digest": fixtures.canonical_digest(list(expected)),
            "consumer_matches_expected": output == expected,
            "baseline_matches_expected": baseline_output == expected,
            "consumer_equals_baseline": output == baseline_output,
            "visible_values_unchanged": visible_unchanged,
            "read_only": evidence["consumer_read_only"] and evidence["baseline_read_only"],
        }
        evaluations[case_id] = _record(
            recorder,
            {"case_id": case_id, "evaluation_binding_digest": evaluation_binding["binding_digest"]},
            lambda f=finding: f,
            lambda value: value,
        )
    aggregate = _record(
        recorder,
        {"finding_count": 4},
        lambda: {
            "schema": "s2hu.aggregate-finding.v1",
            "case_finding_digests": tuple(
                fixtures.canonical_digest(evaluations[key])
                for key in ("c01", "c02", "c03", "c04")
            ),
            "all_expected": all(item["consumer_matches_expected"] for item in evaluations.values()),
            "baseline_explains": all(item["consumer_equals_baseline"] for item in evaluations.values()),
            "all_read_only": all(item["read_only"] for item in evaluations.values()),
        },
        lambda value: value,
    )
    terminal = _record(
        recorder,
        {"aggregate_digest": fixtures.canonical_digest(aggregate)},
        lambda: {
            "schema": "s2hu.terminal-finding.v1",
            "status": "COMPLETING",
            "functional_status": (
                "S2HS_ROLE_CONFLICT_FUNCTION_CONFIRMED_BASELINE_EXPLAINS"
                if aggregate["all_expected"]
                and aggregate["baseline_explains"]
                and aggregate["all_read_only"]
                else "S2HS_ROLE_CONFLICT_FUNCTION_FALSIFIED"
            ),
            "aggregate_digest": fixtures.canonical_digest(aggregate),
        },
        lambda value: value,
    )
    _record(
        recorder,
        {"terminal_digest": fixtures.canonical_digest(terminal)},
        lambda: {
            "schema": "s2hu.completion-marker.v1",
            "status": "COMPLETE",
            "operation_count": 60,
            "event_count": 120,
            "terminal_digest": fixtures.canonical_digest(terminal),
        },
        lambda value: value,
    )


def run_main_once(
    output_root: Path,
    workspace_root: Path,
    run_id: str,
    owner_id: str,
    evaluation_plan: EvaluationPlanSeal,
) -> Path | recording.StartBlocked:
    """Execute once only when a caller explicitly opens this private gate."""

    global MAIN_EXECUTION_ENABLED
    try:
        if MAIN_EXECUTION_ENABLED is not True:
            raise S2HURunnerError("S2-HU main execution gate is closed")
        if (
            not isinstance(output_root, Path)
            or not output_root.is_absolute()
            or not isinstance(workspace_root, Path)
            or not workspace_root.is_absolute()
            or type(evaluation_plan) is not EvaluationPlanSeal
        ):
            raise S2HURunnerError("run boundary differs")
        plan, registry = materialize_execution_plan(workspace_root, run_id, owner_id)
        reserved = recording.AppendOnlyRunRecorder.reserve(output_root, plan, registry)
        if type(reserved) is recording.StartBlocked:
            return reserved
        recorder = reserved
        try:
            _execute(recorder, _runtime(), evaluation_plan)
        except Exception as error:
            code = error.code if isinstance(error, recording.S2HURecordingError) else "HS-E009"
            if recorder.state not in recording.TERMINAL_STATES:
                recorder.fail(code, recorder.current_row().operation_id)
            return recorder.run_directory
        _require(
            recorder.state == "COMPLETE"
            and recorder.next_operation_index == 61
            and recorder.event_count == 120,
            "completed run anatomy differs",
        )
        return recorder.run_directory
    finally:
        MAIN_EXECUTION_ENABLED = False


__all__: tuple[str, ...] = ()
