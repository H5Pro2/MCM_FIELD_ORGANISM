"""Preregistered first F3 comparison over the audited NASA AV source."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import math
from pathlib import Path

import numpy as np

from .field_step_time import MCMFieldStepTime
from .field_time_partition import partition_receptor_completion_time
from .finite_audio_video_field_run import (
    ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    audio_video_dock_anatomies,
)
from .finite_video_path import VisualGridConfig
from .log_spectral_receptor import LogSpectralConfig
from .mcm_f3_causal_runner import run_mcm_f3_causal_comparison
from .mcm_substrate_state import MCMSubstrateArmContract
from .neutral_local_field_substrate import (
    NeutralFastAfterimageConfig,
    NeutralLocalFieldSubstrateConfig,
)
from .public_av_container_source import (
    PUBLIC_MEDIA_CLOCK_ID,
    PUBLIC_MEDIA_TICKS_PER_SECOND,
)
from .public_av_receptor_run import run_public_av_receptor_run
from .public_av_six_arm_field_execution import public_av_receptor_sequences
from .public_media_source_contract import PublicMediaSourceContract
from .shared_mcm_field import build_shared_mcm_field


class MCMF3PublicAVRunError(ValueError):
    """Raised when the preregistered source, parameters, or result drift."""


@dataclass(frozen=True, slots=True)
class MCMF3PublicAVPreregistration:
    preregistration_id: str
    source_id: str
    source_relative_path: str
    clock_id: str
    start_tick: int
    end_tick: int
    auditory_sequence_digest: str
    visual_sequence_digest: str
    expected_auditory_frames: int
    expected_visual_frames: int
    proposal_partition: str
    response_time_seconds: float
    afterimage_time_constant_seconds: float
    dissipation_enabled: bool
    active_arm: MCMSubstrateArmContract
    arm_keys: tuple[str, ...]
    measurements: tuple[str, ...]
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False

    def __post_init__(self) -> None:
        if self.start_tick != 0 or self.end_tick != 500_000_000:
            raise MCMF3PublicAVRunError("NASA F3 interval must remain 0..0.5 s")
        if self.clock_id != PUBLIC_MEDIA_CLOCK_ID:
            raise MCMF3PublicAVRunError("NASA F3 clock changed")
        if self.proposal_partition != "completion_fine":
            raise MCMF3PublicAVRunError("NASA F3 proposal partition changed")
        if self.dissipation_enabled:
            raise MCMF3PublicAVRunError("first NASA F3 run has no dissipation")
        if any(
            (
                self.memory_claim_allowed,
                self.organization_claim_allowed,
                self.topology_claim_allowed,
                self.semantics_claim_allowed,
                self.ai_claim_allowed,
            )
        ):
            raise MCMF3PublicAVRunError("first NASA F3 run cannot release claims")


@dataclass(frozen=True, slots=True)
class MCMF3PublicAVArmMeasurement:
    arm_key: str
    refinement: int
    snapshot_digest: str
    substep_count: int
    maximum_step_seconds: float
    maximum_mass_error: float
    minimum_mass: float
    mass_linf_from_uniform: float
    mass_l2_from_uniform: float
    maximum_abs_activation: float
    maximum_abs_afterimage: float


@dataclass(frozen=True, slots=True)
class MCMF3PublicAVRunResult:
    run_id: str
    preregistration_id: str
    source_id: str
    clock_id: str
    source_support_count: int
    proposal_step_count: int
    auditory_frames: int
    visual_frames: int
    arms: tuple[MCMF3PublicAVArmMeasurement, ...]
    p1_mass_linf_from_uniform: float
    p1_vs_p0_activation_linf: float
    p1_vs_p0_afterimage_linf: float
    p1_vs_eta_null_activation_linf: float
    p1_vs_eta_null_afterimage_linf: float
    p1_vs_kappa_null_mass_linf: float
    p1_vs_kappa_inverted_mass_linf: float
    refinement_n_to_2n_l2: float
    refinement_2n_to_4n_l2: float
    refinement_error_decreased: bool
    raw_payload_retained: bool = False
    memory_claim_allowed: bool = False
    organization_claim_allowed: bool = False
    topology_claim_allowed: bool = False
    semantics_claim_allowed: bool = False
    ai_claim_allowed: bool = False


_ARM_KEYS = (
    "p0.exact",
    "p1.n",
    "p1.2n",
    "p1.4n",
    "b.eta-null",
    "b.kappa-null",
    "b.kappa-inverted",
)


def nasa_mcm_f3_preregistration() -> MCMF3PublicAVPreregistration:
    """Return the fixed contract chosen before inspecting any F3 AV result."""

    return MCMF3PublicAVPreregistration(
        preregistration_id="mcm.f3.nasa-earthrise.causal.v1",
        source_id="public.audiovisual.nasa-earthrise-realtime.svs.2013-12-20",
        source_relative_path="sources/media/NASA Earthrise Realtime Apollo 8.mp4",
        clock_id=PUBLIC_MEDIA_CLOCK_ID,
        start_tick=0,
        end_tick=500_000_000,
        auditory_sequence_digest=(
            "501476111cdd3d17e9b5249b3774dc7918c8ffb8123264c16ce775ba5f6a175f"
        ),
        visual_sequence_digest=(
            "86e9d1a2b1c01959f52d2446f855078dc313341f638bc8e23f43fcf79ea48d93"
        ),
        expected_auditory_frames=41,
        expected_visual_frames=15,
        proposal_partition="completion_fine",
        response_time_seconds=1.0,
        afterimage_time_constant_seconds=0.5,
        dissipation_enabled=False,
        active_arm=MCMSubstrateArmContract(
            "p1.active",
            lambda_sm_per_second=1.0,
            kappa=0.5,
            eta=1.0,
        ),
        arm_keys=_ARM_KEYS,
        measurements=(
            "mass_displacement",
            "eta_dependent_fast_state_contrast",
            "kappa_null_mass_contrast",
            "kappa_sign_mass_contrast",
            "n_2n_4n_refinement",
            "mass_invariants",
        ),
    )


def _linf(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.max(np.abs(left - right)))


def _field_vectors(arm) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([item.activation for item in arm.field.layer.neurons]),
        np.asarray([item.afterimage for item in arm.field.layer.neurons]),
        np.asarray([item.mass for item in arm.field.substrate.masses]),
    )


def _state_vector(arm) -> np.ndarray:
    return np.concatenate(_field_vectors(arm))


def execute_nasa_mcm_f3_causal_run(
    path: Path,
    contract: PublicMediaSourceContract,
) -> MCMF3PublicAVRunResult:
    """Execute exactly the preregistered 0.5 s seven-arm comparison once."""

    plan = nasa_mcm_f3_preregistration()
    if Path(path).as_posix().split("/")[-1] != Path(plan.source_relative_path).name:
        raise MCMF3PublicAVRunError("NASA F3 source filename changed")
    if contract.source_id != plan.source_id:
        raise MCMF3PublicAVRunError("NASA F3 source contract changed")

    audio_config = LogSpectralConfig()
    visual_config = VisualGridConfig(320, 240, 10, 8, 29.97)
    receptor_audit = run_public_av_receptor_run(
        path,
        contract,
        audio_config,
        visual_config,
        duration_seconds=0.5,
        start_tick=0,
    )
    if not receptor_audit.repeatable:
        raise MCMF3PublicAVRunError("NASA receptor reduction is not repeatable")
    if (
        receptor_audit.auditory_sequence_digest
        != plan.auditory_sequence_digest
        or receptor_audit.visual_sequence_digest != plan.visual_sequence_digest
        or len(receptor_audit.auditory_frames) != plan.expected_auditory_frames
        or len(receptor_audit.visual_frames) != plan.expected_visual_frames
    ):
        raise MCMF3PublicAVRunError("NASA receptor sequence differs from preregistration")

    sequences = public_av_receptor_sequences(path, contract, start_tick=0)
    reference = tuple(sequence.frames[0].frame for sequence in sequences)
    anatomies = audio_video_dock_anatomies(
        auditory_carrier_count=len(reference[0].carrier_ids),
        visual_grid_columns=10,
        visual_grid_rows=8,
    )
    base_field = build_shared_mcm_field(
        reference,
        anatomies,
        sample_offsets=ORTHOGONAL_FIELD_SAMPLE_OFFSETS,
    )
    steps = tuple(
        item.step_time
        for item in partition_receptor_completion_time(
            sequences,
            horizon_start_tick=plan.start_tick,
            horizon_end_tick=plan.end_tick,
            ticks_per_second=PUBLIC_MEDIA_TICKS_PER_SECOND,
        ).slices
    )
    if not steps or any(not isinstance(item, MCMFieldStepTime) for item in steps):
        raise MCMF3PublicAVRunError("NASA F3 proposal partition is empty")

    comparison = run_mcm_f3_causal_comparison(
        base_field,
        sequences,
        steps,
        NeutralLocalFieldSubstrateConfig(plan.response_time_seconds),
        NeutralFastAfterimageConfig(plan.afterimage_time_constant_seconds),
        plan.active_arm,
    )
    if tuple(item.arm_key for item in comparison.arms) != plan.arm_keys:
        raise MCMF3PublicAVRunError("NASA F3 arm set changed")

    measurements = []
    for arm in comparison.arms:
        activation, afterimage, mass = _field_vectors(arm)
        uniform = plan.active_arm.initial_total_mass / len(mass)
        measurements.append(
            MCMF3PublicAVArmMeasurement(
                arm_key=arm.arm_key,
                refinement=arm.refinement,
                snapshot_digest=arm.field.snapshot().digest(),
                substep_count=sum(item.substep_count for item in arm.diagnostics),
                maximum_step_seconds=max(
                    item.maximum_step_seconds or 0.0 for item in arm.diagnostics
                ),
                maximum_mass_error=max(
                    item.maximum_mass_error for item in arm.diagnostics
                ),
                minimum_mass=float(np.min(mass)),
                mass_linf_from_uniform=float(np.max(np.abs(mass - uniform))),
                mass_l2_from_uniform=float(np.linalg.norm(mass - uniform)),
                maximum_abs_activation=float(np.max(np.abs(activation))),
                maximum_abs_afterimage=float(np.max(np.abs(afterimage))),
            )
        )

    p0 = comparison.arm("p0.exact")
    p1_n = comparison.arm("p1.n")
    p1_2n = comparison.arm("p1.2n")
    p1 = comparison.arm("p1.4n")
    eta_null = comparison.arm("b.eta-null")
    kappa_null = comparison.arm("b.kappa-null")
    kappa_inverted = comparison.arm("b.kappa-inverted")
    p0_s, p0_h, _ = _field_vectors(p0)
    p1_s, p1_h, p1_m = _field_vectors(p1)
    eta_s, eta_h, _ = _field_vectors(eta_null)
    _, _, kappa_null_m = _field_vectors(kappa_null)
    _, _, kappa_inverted_m = _field_vectors(kappa_inverted)
    uniform = plan.active_arm.initial_total_mass / len(p1_m)
    coarse_error = float(np.linalg.norm(_state_vector(p1_n) - _state_vector(p1_2n)))
    fine_error = float(np.linalg.norm(_state_vector(p1_2n) - _state_vector(p1)))

    values = (
        coarse_error,
        fine_error,
        _linf(p1_s, p0_s),
        _linf(p1_h, p0_h),
        _linf(p1_s, eta_s),
        _linf(p1_h, eta_h),
        _linf(p1_m, kappa_null_m),
        _linf(p1_m, kappa_inverted_m),
    )
    if not all(math.isfinite(value) for value in values):
        raise MCMF3PublicAVRunError("NASA F3 measurements must be finite")

    return MCMF3PublicAVRunResult(
        run_id="lauf.188.mcm.f3.nasa-earthrise.causal.v1",
        preregistration_id=plan.preregistration_id,
        source_id=plan.source_id,
        clock_id=plan.clock_id,
        source_support_count=comparison.source_support_count,
        proposal_step_count=len(steps),
        auditory_frames=len(sequences[0].frames),
        visual_frames=len(sequences[1].frames),
        arms=tuple(measurements),
        p1_mass_linf_from_uniform=float(np.max(np.abs(p1_m - uniform))),
        p1_vs_p0_activation_linf=_linf(p1_s, p0_s),
        p1_vs_p0_afterimage_linf=_linf(p1_h, p0_h),
        p1_vs_eta_null_activation_linf=_linf(p1_s, eta_s),
        p1_vs_eta_null_afterimage_linf=_linf(p1_h, eta_h),
        p1_vs_kappa_null_mass_linf=_linf(p1_m, kappa_null_m),
        p1_vs_kappa_inverted_mass_linf=_linf(p1_m, kappa_inverted_m),
        refinement_n_to_2n_l2=coarse_error,
        refinement_2n_to_4n_l2=fine_error,
        refinement_error_decreased=fine_error < coarse_error,
    )


def mcm_f3_public_av_run_json_value(result: MCMF3PublicAVRunResult) -> dict:
    if not isinstance(result, MCMF3PublicAVRunResult):
        raise MCMF3PublicAVRunError("NASA F3 result type is invalid")
    return asdict(result)


def mcm_f3_public_av_run_public_roles() -> tuple[str, ...]:
    return tuple(
        item.name
        for cls in (
            MCMF3PublicAVPreregistration,
            MCMF3PublicAVArmMeasurement,
            MCMF3PublicAVRunResult,
        )
        for item in fields(cls)
    )
