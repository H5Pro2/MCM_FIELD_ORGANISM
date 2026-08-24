"""Private read-only handoff from one formation result to later probes."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from ._ppb1_active_batch_formation_consumer import (
    PPB1ActiveBatchFormationResult,
)
from ._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorStreamBinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import PPB1BankConfig, PPB1BankState
from ._ppb1_s1wu_read_only_perceptual_probe import (
    S1WUReadOnlyPerceptualFinding,
    probe_s1wu_perceptual_state,
)
from .receptor_contract import technical_identifier


PPB1_FORMATION_PROBE_HANDOFF_SCHEMA_VERSION = (
    "ppb1.private.active-batch-formation-probe-handoff.v1"
)
PPB1_FORMATION_PROBE_HANDOFF_INVALID_INPUT = (
    "PPB1_FORMATION_PROBE_HANDOFF_INVALID_INPUT"
)
PPB1_FORMATION_PROBE_HANDOFF_FORMATION_MISMATCH = (
    "PPB1_FORMATION_PROBE_HANDOFF_FORMATION_MISMATCH"
)
PPB1_FORMATION_PROBE_HANDOFF_STABILIZATION_REQUIRED = (
    "PPB1_FORMATION_PROBE_HANDOFF_STABILIZATION_REQUIRED"
)
PPB1_FORMATION_PROBE_HANDOFF_PARTITION_MISMATCH = (
    "PPB1_FORMATION_PROBE_HANDOFF_PARTITION_MISMATCH"
)
PPB1_FORMATION_PROBE_HANDOFF_ATOMIC_RESULT_REQUIRED = (
    "PPB1_FORMATION_PROBE_HANDOFF_ATOMIC_RESULT_REQUIRED"
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class PPB1ActiveBatchFormationProbeHandoffError(ValueError):
    """One fail-closed private formation-to-probe handoff violation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and _DIGEST.fullmatch(value) is not None


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise PPB1ActiveBatchFormationProbeHandoffError(
            PPB1_FORMATION_PROBE_HANDOFF_INVALID_INPUT,
            str(exc),
        ) from exc


@dataclass(frozen=True, slots=True)
class PPB1ActiveBatchFormationProbeResult:
    handoff_id: str
    formation_result_digest: str
    formation_envelope_digest: str
    profile_binding_digest: str
    later_probe_envelope_digest: str
    formation_to_probe_partition_digest: str
    auditory_preprobe_state_digest: str
    visual_preprobe_state_digest: str
    auditory_finding: S1WUReadOnlyPerceptualFinding
    visual_finding: S1WUReadOnlyPerceptualFinding
    auditory_postprobe_state_digest: str
    visual_postprobe_state_digest: str
    handoff_result_digest: str

    def __post_init__(self) -> None:
        _identifier(self.handoff_id, "handoff_id")
        digests = (
            self.formation_result_digest,
            self.formation_envelope_digest,
            self.profile_binding_digest,
            self.later_probe_envelope_digest,
            self.formation_to_probe_partition_digest,
            self.auditory_preprobe_state_digest,
            self.visual_preprobe_state_digest,
            self.auditory_postprobe_state_digest,
            self.visual_postprobe_state_digest,
            self.handoff_result_digest,
        )
        if (
            not all(_valid_digest(value) for value in digests)
            or type(self.auditory_finding)
            is not S1WUReadOnlyPerceptualFinding
            or type(self.visual_finding) is not S1WUReadOnlyPerceptualFinding
            or self.auditory_finding.modality_id != "auditory"
            or self.visual_finding.modality_id != "visual"
            or self.auditory_finding.observed_bank_state_digest
            != self.auditory_preprobe_state_digest
            or self.visual_finding.observed_bank_state_digest
            != self.visual_preprobe_state_digest
            or self.auditory_postprobe_state_digest
            != self.auditory_preprobe_state_digest
            or self.visual_postprobe_state_digest
            != self.visual_preprobe_state_digest
            or self.handoff_result_digest != _digest(self.payload_without_digest())
        ):
            raise PPB1ActiveBatchFormationProbeHandoffError(
                PPB1_FORMATION_PROBE_HANDOFF_ATOMIC_RESULT_REQUIRED,
                "handoff result is incomplete or digest-inconsistent",
            )

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": PPB1_FORMATION_PROBE_HANDOFF_SCHEMA_VERSION,
            "handoff_id": self.handoff_id,
            "formation_result_digest": self.formation_result_digest,
            "formation_envelope_digest": self.formation_envelope_digest,
            "profile_binding_digest": self.profile_binding_digest,
            "later_probe_envelope_digest": self.later_probe_envelope_digest,
            "formation_to_probe_partition_digest": (
                self.formation_to_probe_partition_digest
            ),
            "auditory_preprobe_state_digest": (
                self.auditory_preprobe_state_digest
            ),
            "visual_preprobe_state_digest": self.visual_preprobe_state_digest,
            "auditory_finding_digest": self.auditory_finding.finding_digest,
            "visual_finding_digest": self.visual_finding.finding_digest,
            "auditory_postprobe_state_digest": (
                self.auditory_postprobe_state_digest
            ),
            "visual_postprobe_state_digest": self.visual_postprobe_state_digest,
        }

    def canonical_payload(self) -> dict[str, object]:
        return {
            **self.payload_without_digest(),
            "handoff_result_digest": self.handoff_result_digest,
        }


def _eligible(config: PPB1BankConfig, state: PPB1BankState) -> bool:
    return any(
        slot.occupied
        and slot.support_count is not None
        and slot.support_count >= config.stable_after
        for slot in state.slots
    )


def _formation_frames(
    envelope: PPB1ActiveReceptorBatchEnvelope,
) -> tuple[tuple[str, object], ...]:
    return tuple(
        (modality_id, item)
        for modality_id, stream in (
            ("auditory", envelope.auditory_stream),
            ("visual", envelope.visual_stream),
        )
        for item in stream.timed_frames
    )


def _validate_formation(
    result: PPB1ActiveBatchFormationResult,
    envelope: PPB1ActiveReceptorBatchEnvelope,
    profile: PPB1ReceptorProfileBinding,
) -> None:
    pairs = (
        (
            result.auditory_poststate,
            envelope.auditory_stream,
            profile.auditory_config,
        ),
        (
            result.visual_poststate,
            envelope.visual_stream,
            profile.visual_config,
        ),
    )
    if (
        result.envelope_digest != envelope.envelope_digest
        or result.profile_binding_digest != profile.digest()
        or result.authorization_poststate.status != "CONSUMED"
        or result.authorization_poststate.committed_result_digest
        != result.formation_result_digest
        or envelope.profile_id != profile.profile_id
        or envelope.profile_binding_digest != profile.digest()
        or envelope.parameter_digest != profile.parameter_digest
        or envelope.auditory_stream.bank_config_digest
        != profile.auditory_config.digest()
        or envelope.visual_stream.bank_config_digest
        != profile.visual_config.digest()
    ):
        raise PPB1ActiveBatchFormationProbeHandoffError(
            PPB1_FORMATION_PROBE_HANDOFF_FORMATION_MISMATCH,
            "formation result, envelope and profile do not share one source",
        )
    for state, stream, config in pairs:
        last = stream.timed_frames[-1]
        if (
            state.config_digest != config.digest()
            or state.accepted_step_count != stream.frame_count
            or state.source_clock_id != stream.source_clock_id
            or state.last_source_window_end_tick
            != last.source_window_end_tick
        ):
            raise PPB1ActiveBatchFormationProbeHandoffError(
                PPB1_FORMATION_PROBE_HANDOFF_FORMATION_MISMATCH,
                "formation poststate does not match its exact stream and config",
            )
        if not _eligible(config, state):
            raise PPB1ActiveBatchFormationProbeHandoffError(
                PPB1_FORMATION_PROBE_HANDOFF_STABILIZATION_REQUIRED,
                "both formation poststates require one stabilized eligible slot",
            )


def _validate_later_stream(
    stream: PPB1ActiveReceptorStreamBinding,
    state: PPB1BankState,
    config: PPB1BankConfig,
    formation_field_end: int,
) -> None:
    if stream.frame_count != 1:
        raise PPB1ActiveBatchFormationProbeHandoffError(
            PPB1_FORMATION_PROBE_HANDOFF_PARTITION_MISMATCH,
            "later probe stream must contain exactly one frame",
        )
    item = stream.timed_frames[0]
    if (
        stream.modality_id != config.modality_id
        or stream.geometry_id != config.geometry_id
        or stream.carrier_ids != config.carrier_ids
        or stream.bank_config_digest != config.digest()
        or stream.source_clock_id != state.source_clock_id
        or item.source_window_start_tick < state.last_source_window_end_tick
        or item.source_window_end_tick <= state.last_source_window_end_tick
        or item.field_window_start_tick < formation_field_end
    ):
        raise PPB1ActiveBatchFormationProbeHandoffError(
            PPB1_FORMATION_PROBE_HANDOFF_PARTITION_MISMATCH,
            "probe frame is not an exact disjoint causally later modality input",
        )


def _validate_probe_envelope(
    formation: PPB1ActiveReceptorBatchEnvelope,
    probe: PPB1ActiveReceptorBatchEnvelope,
    profile: PPB1ReceptorProfileBinding,
    result: PPB1ActiveBatchFormationResult,
) -> None:
    formation_frames = _formation_frames(formation)
    probe_frames = _formation_frames(probe)
    formation_pairs = {
        (modality, item.snapshot_id) for modality, item in formation_frames
    }
    probe_pairs = {(modality, item.snapshot_id) for modality, item in probe_frames}
    formation_provenance = {
        item.timed_frame_provenance_digest for _, item in formation_frames
    }
    probe_provenance = {
        item.timed_frame_provenance_digest for _, item in probe_frames
    }
    if (
        probe.envelope_digest == formation.envelope_digest
        or probe.source_batch_digest == formation.source_batch_digest
        or probe.source_contract_id != formation.source_contract_id
        or probe.source_contract_digest != formation.source_contract_digest
        or probe.profile_id != profile.profile_id
        or probe.profile_binding_digest != profile.digest()
        or probe.parameter_digest != profile.parameter_digest
        or probe.common_field_clock_id != formation.common_field_clock_id
        or formation_pairs & probe_pairs
        or formation_provenance & probe_provenance
    ):
        raise PPB1ActiveBatchFormationProbeHandoffError(
            PPB1_FORMATION_PROBE_HANDOFF_PARTITION_MISMATCH,
            "formation and probe envelopes are not source-bound and disjoint",
        )
    formation_field_end = max(
        item.field_window_end_tick for _, item in formation_frames
    )
    _validate_later_stream(
        probe.auditory_stream,
        result.auditory_poststate,
        profile.auditory_config,
        formation_field_end,
    )
    _validate_later_stream(
        probe.visual_stream,
        result.visual_poststate,
        profile.visual_config,
        formation_field_end,
    )


def _probe_modality_read_only(
    config: PPB1BankConfig,
    state: PPB1BankState,
    stream: PPB1ActiveReceptorStreamBinding,
    probe_id: str,
) -> S1WUReadOnlyPerceptualFinding:
    return probe_s1wu_perceptual_state(
        config,
        state,
        stream.timed_frames[0].timed_frame.frame,
        probe_id,
    )


def probe_ppb1_active_batch_formation_result_read_only(
    handoff_id: str,
    formation_result: object,
    formation_envelope: object,
    profile: object,
    later_probe_envelope: object,
    auditory_probe_id: str,
    visual_probe_id: str,
) -> PPB1ActiveBatchFormationProbeResult:
    """Probe both formed modality states without exposing or changing state."""

    validated_handoff_id = _identifier(handoff_id, "handoff_id")
    validated_auditory_probe_id = _identifier(
        auditory_probe_id,
        "auditory_probe_id",
    )
    validated_visual_probe_id = _identifier(
        visual_probe_id,
        "visual_probe_id",
    )
    if (
        type(formation_result) is not PPB1ActiveBatchFormationResult
        or type(formation_envelope) is not PPB1ActiveReceptorBatchEnvelope
        or type(profile) is not PPB1ReceptorProfileBinding
        or type(later_probe_envelope) is not PPB1ActiveReceptorBatchEnvelope
    ):
        raise PPB1ActiveBatchFormationProbeHandoffError(
            PPB1_FORMATION_PROBE_HANDOFF_INVALID_INPUT,
            "exact formation, envelope and profile types are required",
        )
    _validate_formation(formation_result, formation_envelope, profile)
    _validate_probe_envelope(
        formation_envelope,
        later_probe_envelope,
        profile,
        formation_result,
    )
    input_digests = (
        formation_result.formation_result_digest,
        formation_envelope.envelope_digest,
        profile.digest(),
        later_probe_envelope.envelope_digest,
        formation_result.auditory_poststate.digest(),
        formation_result.visual_poststate.digest(),
    )
    auditory_probe = later_probe_envelope.auditory_stream.timed_frames[0]
    visual_probe = later_probe_envelope.visual_stream.timed_frames[0]
    partition_values = {
        "schema_version": PPB1_FORMATION_PROBE_HANDOFF_SCHEMA_VERSION,
        "handoff_id": validated_handoff_id,
        "formation_result_digest": formation_result.formation_result_digest,
        "formation_envelope_digest": formation_envelope.envelope_digest,
        "profile_binding_digest": profile.digest(),
        "later_probe_envelope_digest": later_probe_envelope.envelope_digest,
        "auditory_probe_frame_provenance_digest": (
            auditory_probe.timed_frame_provenance_digest
        ),
        "visual_probe_frame_provenance_digest": (
            visual_probe.timed_frame_provenance_digest
        ),
        "auditory_probe_id": validated_auditory_probe_id,
        "visual_probe_id": validated_visual_probe_id,
    }
    partition_digest = _digest(partition_values)
    try:
        auditory_finding = _probe_modality_read_only(
            profile.auditory_config,
            formation_result.auditory_poststate,
            later_probe_envelope.auditory_stream,
            validated_auditory_probe_id,
        )
        visual_finding = _probe_modality_read_only(
            profile.visual_config,
            formation_result.visual_poststate,
            later_probe_envelope.visual_stream,
            validated_visual_probe_id,
        )
    except Exception as exc:
        raise PPB1ActiveBatchFormationProbeHandoffError(
            PPB1_FORMATION_PROBE_HANDOFF_ATOMIC_RESULT_REQUIRED,
            "both read-only findings are required for one handoff result",
        ) from exc
    after_digests = (
        formation_result.formation_result_digest,
        formation_envelope.envelope_digest,
        profile.digest(),
        later_probe_envelope.envelope_digest,
        formation_result.auditory_poststate.digest(),
        formation_result.visual_poststate.digest(),
    )
    if (
        after_digests != input_digests
        or auditory_finding.bank_config_digest
        != profile.auditory_config.digest()
        or visual_finding.bank_config_digest != profile.visual_config.digest()
        or auditory_finding.observed_bank_state_digest != input_digests[4]
        or visual_finding.observed_bank_state_digest != input_digests[5]
        or auditory_finding.probe_input_digest
        != auditory_probe.ppb1_input_projection_digest
        or visual_finding.probe_input_digest
        != visual_probe.ppb1_input_projection_digest
    ):
        raise PPB1ActiveBatchFormationProbeHandoffError(
            PPB1_FORMATION_PROBE_HANDOFF_ATOMIC_RESULT_REQUIRED,
            "probe findings or bound inputs changed during handoff",
        )
    values = {
        "handoff_id": validated_handoff_id,
        "formation_result_digest": input_digests[0],
        "formation_envelope_digest": input_digests[1],
        "profile_binding_digest": input_digests[2],
        "later_probe_envelope_digest": input_digests[3],
        "formation_to_probe_partition_digest": partition_digest,
        "auditory_preprobe_state_digest": input_digests[4],
        "visual_preprobe_state_digest": input_digests[5],
        "auditory_finding": auditory_finding,
        "visual_finding": visual_finding,
        "auditory_postprobe_state_digest": input_digests[4],
        "visual_postprobe_state_digest": input_digests[5],
    }
    payload = {
        "schema_version": PPB1_FORMATION_PROBE_HANDOFF_SCHEMA_VERSION,
        **{
            key: (
                value.finding_digest
                if key in {"auditory_finding", "visual_finding"}
                else value
            )
            for key, value in values.items()
        },
    }
    payload["auditory_finding_digest"] = payload.pop("auditory_finding")
    payload["visual_finding_digest"] = payload.pop("visual_finding")
    return PPB1ActiveBatchFormationProbeResult(
        **values,
        handoff_result_digest=_digest(payload),
    )
