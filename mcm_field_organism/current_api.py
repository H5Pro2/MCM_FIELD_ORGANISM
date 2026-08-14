"""Curated active field API plus explicitly classified reference exports.

Names in the reference manifests remain importable for controlled technical
comparisons; their presence is not a substrate, memory, or learning claim.
"""

from __future__ import annotations

from dataclasses import fields
import hashlib
import json

from .architecture_contract import EvidenceLevel, RuntimePermission
from .asynchronous_receptor_events import (
    AsynchronousReceptorEventAudit,
    AsynchronousReceptorEventError,
    ReceptorCompletionEvent,
    ReceptorCompletionGroup,
    audit_asynchronous_receptor_events,
)
from .audio_video_field_geometry import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .audio_video_neutral_field_runtime import (
    AUDIO_VIDEO_MODALITY_IDS,
    AudioVideoNeutralFieldRuntimeError,
    CapturedAudioVideoNeutralFieldRun,
    advance_audio_video_receptor_sequences,
    capture_audio_video_into_neutral_field,
)
from .broadband_hearing_path import (
    AuditoryReceptorContact,
    AuditoryReceptorState,
    BroadbandHearingPath,
    BroadbandHearingSummary,
    capture_finite_broadband_hearing,
)
from .browser_payload_runtime import (
    BrowserPayloadRuntimeBinding,
    BrowserPayloadRuntimeBindingError,
    bind_browser_payload_runtime,
    bind_installed_browser_payload_runtime,
    verify_browser_payload_runtime_binding,
)
from .browser_payload_source import (
    BrowserPayloadCapturePreflight,
    BrowserPayloadCaptureReceipt,
    BrowserPayloadSourceConfig,
    BrowserPayloadSourceError,
    browser_payload_asset_digests,
    capture_browser_payload_page,
)
from .browser_receptor_bridge import (
    BrowserReceptorBridge,
    BrowserReceptorBridgeConfig,
    BrowserReceptorBridgeError,
    BrowserReceptorSequenceBatch,
)
from .browser_world_contract import (
    BrowserWorldContract,
    BrowserWorldContractError,
    BrowserWorldPhase,
)
from .controlled_audio_phase_source import (
    AudioGainPhase,
    ControlledAudioGateSource,
    ControlledAudioPhaseSource,
)
from .controlled_probe_baseline_comparison import (
    ControlledProbeComparisonError,
    ControlledProbeSnapshotComparison,
    compare_controlled_probe_baseline_set,
    compare_controlled_probe_snapshots,
)
from .ci_accommodation_baseline import (
    CIAccommodationBaselineError,
    CIAccommodationConfig,
    CIAdvanceResult,
    CIState,
    apply_ci_backreaction,
    advance_ci_accommodation,
    advance_ci_from_field_snapshot,
    advance_ci_null_exposure,
)
from .controlled_audio_source import (
    AudioCaptureError,
    AudioFrameSource,
    SyntheticAudioFrameSource,
)
from .field_step_time import MCMFieldStepTime, MCMFieldStepTimeError
from .field_time_partition import (
    FieldTimePartition,
    FieldTimePartitionError,
    FieldTimeSlice,
    partition_receptor_completion_time,
)
from .finite_multimodal_field_run import (
    FiniteMultimodalFieldError,
    FiniteSharedMCMFieldResult,
    TimedReceptorFrame,
    assemble_shared_mcm_field,
)
from .finite_video_path import (
    FiniteVideoSummary,
    LocalChannelGridReceptor,
    SyntheticVideoFrameSource,
    VideoFrameSource,
    VisualCaptureError,
    VisualGridConfig,
    VisualReceptorContact,
    VisualReceptorState,
    capture_finite_video,
)
from .log_spectral_receptor import (
    LogFrequencyBand,
    LogSpectralConfig,
    LogSpectralReceptor,
    RollingLogSpectralReceptor,
    logarithmic_bands,
)
from .mcm_f3_coupling import (
    MCMF3CouplingError,
    MCMF3CouplingResult,
    MCMF3LocalRate,
    compute_mcm_f3_coupling,
)
from .mcm_f3_baseline_coupling import compute_mcm_f3_local_leaky_baseline
from .mcm_f3_runtime import (
    MCMF3AdvanceDiagnostics,
    MCMF3AdvanceResult,
    MCMF3RuntimeError,
    activate_mcm_f3_field,
    advance_mcm_f3_shared_field,
    advance_mcm_f3_shared_field_transient,
)
from .mcm_substrate_state import (
    MCMSubstrateArmContract,
    MCMSubstrateMass,
    MCMSubstrateState,
    MCMSubstrateStateError,
    build_uniform_mcm_substrate,
)
from .neutral_asynchronous_field_runtime import (
    NeutralAsynchronousFieldRun,
    NeutralAsynchronousFieldRuntimeError,
    run_neutral_asynchronous_field,
)
from .neutral_field_session import (
    NeutralFieldSessionError,
    NeutralFieldSessionResult,
    NeutralFieldSessionWindow,
    run_neutral_field_session,
)
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
    NeutralLocalFieldSubstrateError,
    advance_neutral_fast_shared_field,
    advance_neutral_fast_shared_field_transient,
)
from .receptor_contract import (
    CommonFieldTime,
    ReceptorContactFrame,
    ReceptorContractError,
    ReceptorNeuronDockMap,
    from_auditory_receptor_state,
    from_visual_receptor_state,
)
from .receptor_distributor import (
    DistributedReceptorContact,
    ReceptorDistribution,
    ReceptorDistributionError,
    ReceptorDistributor,
    ReceptorDock,
)
from .receptor_process_contract import (
    ReceptorProcessContract,
    ReceptorProcessContractError,
    reference_receptor_process_contract,
)
from .receptor_proposal_handoff import (
    ReceptorProposalBatch,
    ReceptorProposalCompletionGroup,
    ReceptorProposalHandoff,
    ReceptorProposalHandoffError,
    handoff_receptor_completion_groups,
)
from .receptor_temporal_support import (
    ReceptorTemporalSupportAudit,
    ReceptorTemporalSupportError,
    audit_auditory_temporal_support,
    audit_visual_temporal_support,
)
from .receptor_time_model import (
    OrganismTimedReceptorFrame,
    ReceptorTimeAlignmentError,
    ReceptorTimeSequence,
)
from .mcm_local_development_state import MCMLocalDevelopmentContract
from .s1b_asynchronous_field_runtime import (
    S1BAsynchronousFieldRun,
    S1BAsynchronousFieldRuntimeError,
    run_s1b_asynchronous_field,
)
from .s1b_causal_two_stage import (
    S1BCausalProbeSample,
    S1BCausalProbeTrace,
    S1BCausalTwoStageError,
    S1BCausalTwoStageResult,
    run_s1b_causal_two_stage,
)
from .s1b_causal_browser_world import (
    S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST,
    S1BCausalBrowserWorldError,
    S1BCausalBrowserWorldSet,
    s1b_causal_browser_world_set,
)
from .s1b_causal_capture_handoff import (
    S1BCausalCaptureHandoff,
    S1BCausalCaptureHandoffError,
    S1BCausalCaptureSchedule,
    prepare_s1b_causal_capture_handoff,
    run_s1b_causal_capture_handoff,
    s1b_causal_capture_schedule,
)
from .s1b_causal_browser_execution_contract import (
    S1BCausalBrowserExecutionContract,
    S1BCausalBrowserExecutionContractError,
    prepare_s1b_causal_browser_execution_contract,
)
from .s1b_causal_browser_one_shot import (
    S1BCausalBrowserOneShotError,
    S1BCausalBrowserOneShotReceipt,
    execute_s1b_causal_browser_one_shot,
)
from .shared_field_session import (
    SharedFieldSessionError,
    SharedFieldSessionResult,
    SharedFieldSessionStep,
    SharedFieldSessionWindow,
    run_shared_mcm_field_session,
)
from .shared_mcm_field import (
    NEUTRAL_SNAPSHOT_ROOT_KEYS,
    NEUTRAL_SNAPSHOT_SCHEMA_VERSION,
    SNAPSHOT_REFERENCE_STATE_FIELDS,
    ReceptorDockAnatomy,
    SharedFieldDock,
    SharedMCMField,
    SharedMCMFieldError,
    SharedMCMFieldSnapshot,
    attach_uniform_mcm_substrate,
    build_shared_mcm_field,
    migrate_shared_mcm_field_snapshot_to_schema2,
    restore_shared_mcm_field,
)
from .transient_dock_trajectory import (
    TransientDockCompletionGroup,
    TransientDockFrame,
    TransientDockTrajectory,
    TransientDockTrajectoryError,
    map_proposal_batch_to_transient_docks,
)
from .transient_neuron_input import (
    TransientLocalReceptorContact,
    TransientNeuronDockInput,
    TransientNeuronInputError,
    TransientNeuronInputSet,
    project_transient_docks_to_neuron_inputs,
)
from .w7b_linear_history_discrimination import (
    W7BLinearHistoryDiscriminationError,
    W7BLinearHistoryDiscriminationResult,
    run_w7b_linear_history_discrimination,
)


CURRENT_CONTROLLED_FIELD_EXPORTS = (
    "EvidenceLevel",
    "RuntimePermission",
    "ORTHOGONAL_FIELD_SAMPLE_OFFSETS",
    "audio_video_dock_anatomies",
    "AudioCaptureError",
    "AudioFrameSource",
    "SyntheticAudioFrameSource",
    "AudioGainPhase",
    "ControlledAudioGateSource",
    "ControlledAudioPhaseSource",
    "LogFrequencyBand",
    "LogSpectralConfig",
    "LogSpectralReceptor",
    "RollingLogSpectralReceptor",
    "logarithmic_bands",
    "AuditoryReceptorContact",
    "AuditoryReceptorState",
    "BroadbandHearingPath",
    "BroadbandHearingSummary",
    "capture_finite_broadband_hearing",
    "VideoFrameSource",
    "SyntheticVideoFrameSource",
    "VisualCaptureError",
    "VisualGridConfig",
    "VisualReceptorContact",
    "VisualReceptorState",
    "FiniteVideoSummary",
    "LocalChannelGridReceptor",
    "capture_finite_video",
    "BrowserWorldContract",
    "BrowserWorldContractError",
    "BrowserWorldPhase",
    "BrowserReceptorBridge",
    "BrowserReceptorBridgeConfig",
    "BrowserReceptorBridgeError",
    "BrowserReceptorSequenceBatch",
    "BrowserPayloadSourceConfig",
    "BrowserPayloadSourceError",
    "BrowserPayloadCapturePreflight",
    "BrowserPayloadCaptureReceipt",
    "browser_payload_asset_digests",
    "capture_browser_payload_page",
    "BrowserPayloadRuntimeBinding",
    "BrowserPayloadRuntimeBindingError",
    "bind_browser_payload_runtime",
    "bind_installed_browser_payload_runtime",
    "verify_browser_payload_runtime_binding",
    "CommonFieldTime",
    "ReceptorContactFrame",
    "ReceptorContractError",
    "ReceptorNeuronDockMap",
    "from_auditory_receptor_state",
    "from_visual_receptor_state",
    "DistributedReceptorContact",
    "ReceptorDistribution",
    "ReceptorDistributionError",
    "ReceptorDistributor",
    "ReceptorDock",
    "ReceptorProcessContract",
    "ReceptorProcessContractError",
    "reference_receptor_process_contract",
    "ReceptorProposalHandoffError",
    "ReceptorProposalCompletionGroup",
    "ReceptorProposalBatch",
    "ReceptorProposalHandoff",
    "handoff_receptor_completion_groups",
    "ReceptorTemporalSupportAudit",
    "ReceptorTemporalSupportError",
    "audit_auditory_temporal_support",
    "audit_visual_temporal_support",
    "ReceptorTimeAlignmentError",
    "OrganismTimedReceptorFrame",
    "ReceptorTimeSequence",
    "MCMFieldStepTime",
    "MCMFieldStepTimeError",
    "FieldTimePartition",
    "FieldTimePartitionError",
    "FieldTimeSlice",
    "partition_receptor_completion_time",
    "ReceptorCompletionEvent",
    "ReceptorCompletionGroup",
    "AsynchronousReceptorEventAudit",
    "AsynchronousReceptorEventError",
    "audit_asynchronous_receptor_events",
    "TransientDockCompletionGroup",
    "TransientDockFrame",
    "TransientDockTrajectory",
    "TransientDockTrajectoryError",
    "map_proposal_batch_to_transient_docks",
    "TransientLocalReceptorContact",
    "TransientNeuronDockInput",
    "TransientNeuronInputError",
    "TransientNeuronInputSet",
    "project_transient_docks_to_neuron_inputs",
    "ReceptorDockAnatomy",
    "SharedFieldDock",
    "SharedMCMField",
    "SharedMCMFieldError",
    "SharedMCMFieldSnapshot",
    "build_shared_mcm_field",
    "restore_shared_mcm_field",
    "migrate_shared_mcm_field_snapshot_to_schema2",
    "NeutralFastAfterimageConfig",
    "NeutralLocalFieldSubstrateConfig",
    "NeutralLocalFieldSubstrateError",
    "advance_neutral_fast_shared_field",
    "advance_neutral_fast_shared_field_transient",
    "NeutralAsynchronousFieldRun",
    "NeutralAsynchronousFieldRuntimeError",
    "run_neutral_asynchronous_field",
    "NeutralFieldSessionError",
    "NeutralFieldSessionResult",
    "NeutralFieldSessionWindow",
    "run_neutral_field_session",
    "SharedFieldSessionError",
    "SharedFieldSessionResult",
    "SharedFieldSessionStep",
    "SharedFieldSessionWindow",
    "run_shared_mcm_field_session",
    "FiniteMultimodalFieldError",
    "FiniteSharedMCMFieldResult",
    "TimedReceptorFrame",
    "assemble_shared_mcm_field",
    "AudioVideoNeutralFieldRuntimeError",
    "CapturedAudioVideoNeutralFieldRun",
    "advance_audio_video_receptor_sequences",
    "capture_audio_video_into_neutral_field",
    "active_field_state_contract",
    "active_field_state_contract_digest",
)

PASSIVE_COMPARISON_EXPORTS = (
    "ControlledProbeComparisonError",
    "ControlledProbeSnapshotComparison",
    "compare_controlled_probe_baseline_set",
    "compare_controlled_probe_snapshots",
)

CI_REFERENCE_EXPORTS = (
    "CIAccommodationBaselineError",
    "CIAccommodationConfig",
    "CIAdvanceResult",
    "CIState",
    "apply_ci_backreaction",
    "advance_ci_accommodation",
    "advance_ci_from_field_snapshot",
    "advance_ci_null_exposure",
)

F3_REFERENCE_EXPORTS = (
    "MCMSubstrateArmContract",
    "MCMSubstrateMass",
    "MCMSubstrateState",
    "MCMSubstrateStateError",
    "build_uniform_mcm_substrate",
    "attach_uniform_mcm_substrate",
    "MCMF3CouplingError",
    "MCMF3CouplingResult",
    "MCMF3LocalRate",
    "compute_mcm_f3_coupling",
    "compute_mcm_f3_local_leaky_baseline",
    "MCMF3AdvanceDiagnostics",
    "MCMF3AdvanceResult",
    "MCMF3RuntimeError",
    "activate_mcm_f3_field",
    "advance_mcm_f3_shared_field",
    "advance_mcm_f3_shared_field_transient",
)

S1B_REFERENCE_EXPORTS = (
    "MCMLocalDevelopmentContract",
    "S1BAsynchronousFieldRun",
    "S1BAsynchronousFieldRuntimeError",
    "run_s1b_asynchronous_field",
    "S1BCausalProbeSample",
    "S1BCausalProbeTrace",
    "S1BCausalTwoStageError",
    "S1BCausalTwoStageResult",
    "run_s1b_causal_two_stage",
    "S1BCausalBrowserWorldError",
    "S1BCausalBrowserWorldSet",
    "s1b_causal_browser_world_set",
    "S1B_CAUSAL_BROWSER_WORLD_SET_DIGEST",
    "S1BCausalCaptureHandoff",
    "S1BCausalCaptureHandoffError",
    "S1BCausalCaptureSchedule",
    "prepare_s1b_causal_capture_handoff",
    "run_s1b_causal_capture_handoff",
    "s1b_causal_capture_schedule",
    "S1BCausalBrowserExecutionContract",
    "S1BCausalBrowserExecutionContractError",
    "prepare_s1b_causal_browser_execution_contract",
    "S1BCausalBrowserOneShotError",
    "S1BCausalBrowserOneShotReceipt",
    "execute_s1b_causal_browser_one_shot",
    "W7BLinearHistoryDiscriminationError",
    "W7BLinearHistoryDiscriminationResult",
    "run_w7b_linear_history_discrimination",
)


def active_field_state_contract() -> dict[str, object]:
    """Return the active device-neutral field contract as JSON-safe values."""

    return {
        "contract_id": "mcm.active_av_field_state.v1",
        "modalities": list(AUDIO_VIDEO_MODALITY_IDS),
        "active_export_names": list(CURRENT_CONTROLLED_FIELD_EXPORTS),
        "receptor_sequence_fields": [
            item.name for item in fields(ReceptorTimeSequence)
        ],
        "timed_receptor_frame_fields": [
            item.name for item in fields(OrganismTimedReceptorFrame)
        ],
        "handoff_fields": [item.name for item in fields(ReceptorProposalHandoff)],
        "field_run_fields": [item.name for item in fields(NeutralAsynchronousFieldRun)],
        "snapshot": {
            "schema_version": NEUTRAL_SNAPSHOT_SCHEMA_VERSION,
            "root_keys": list(NEUTRAL_SNAPSHOT_ROOT_KEYS),
            "reference_state_fields": list(SNAPSHOT_REFERENCE_STATE_FIELDS),
        },
        "reference_manifests": {
            "passive_comparison": list(PASSIVE_COMPARISON_EXPORTS),
            "ci": list(CI_REFERENCE_EXPORTS),
            "f3": list(F3_REFERENCE_EXPORTS),
            "s1b": list(S1B_REFERENCE_EXPORTS),
        },
        "memory_claim": False,
    }


def active_field_state_contract_digest() -> str:
    """Return the SHA-256 digest of the canonical active contract JSON."""

    encoded = json.dumps(
        active_field_state_contract(),
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()

__all__ = (
    CURRENT_CONTROLLED_FIELD_EXPORTS
    + PASSIVE_COMPARISON_EXPORTS
    + CI_REFERENCE_EXPORTS
    + F3_REFERENCE_EXPORTS
    + S1B_REFERENCE_EXPORTS
)
