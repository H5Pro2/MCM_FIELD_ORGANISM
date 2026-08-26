"""Private atomic PPB-1 and static-prototype recognition comparator."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re

from ._ppb1_active_batch_formation_consumer import PPB1ActiveBatchFormationResult
from ._ppb1_active_batch_formation_probe_handoff import (
    PPB1ActiveBatchFormationProbeResult,
    probe_ppb1_active_batch_formation_result_read_only,
)
from ._ppb1_active_receptor_batch_binding import (
    PPB1ActiveReceptorBatchEnvelope,
    PPB1ActiveReceptorStreamBinding,
)
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_reference import PPB1BankConfig, PPB1BankState
from ._ppb1_s2bd_active_static_prototype_baseline import (
    S2BDBaselineFormationBundle,
    S2BBStaticPrototypeProbeFinding,
    S2BBStaticPrototypeState,
    form_s2bb_active_static_prototype_baseline,
    probe_s2bb_static_prototype_read_only,
)
from .receptor_contract import technical_identifier


S2BD_COMPARATOR_SCHEMA_VERSION = "ppb1.s2bd.paired-recognition-comparator.v1"
S2BD_COMPARATOR_INVALID_INPUT = "S2BD_COMPARATOR_INVALID_INPUT"
S2BD_COMPARATOR_CANDIDATE_INELIGIBLE = "S2BD_COMPARATOR_CANDIDATE_INELIGIBLE"
S2BD_COMPARATOR_ATOMIC_RESULT_REQUIRED = "S2BD_COMPARATOR_ATOMIC_RESULT_REQUIRED"

BASELINE_EXPLAINS_CURRENT_FIXTURE = "BASELINE_EXPLAINS_CURRENT_FIXTURE"
UNEXPECTED_DIFFERENCE_REQUIRES_STATIC_AUDIT = (
    "UNEXPECTED_DIFFERENCE_REQUIRES_STATIC_AUDIT_NO_ADVANTAGE_DECISION"
)

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


class S2BDPairedRecognitionComparatorError(ValueError):
    """One fail-closed paired-comparison contract violation."""

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
    return isinstance(value, str) and bool(_DIGEST.fullmatch(value))


def _identifier(value: object, role: str) -> str:
    try:
        return technical_identifier(value, role)
    except ValueError as exc:
        raise S2BDPairedRecognitionComparatorError(
            S2BD_COMPARATOR_INVALID_INPUT,
            str(exc),
        ) from exc


def _one_stabilized_slot(config: PPB1BankConfig, state: PPB1BankState) -> bool:
    occupied = tuple(slot for slot in state.slots if slot.occupied)
    return (
        len(occupied) == 1
        and occupied[0].support_count is not None
        and occupied[0].support_count >= config.stable_after
    )


@dataclass(frozen=True, slots=True)
class S2BBPairedRecognitionReceipt:
    pair_id: str
    candidate_handoff_result_digest: str
    candidate_finding_digests: tuple[str, str]
    baseline_formation_receipt_digests: tuple[str, str]
    baseline_finding_digests: tuple[str, str]
    baseline_probe_ids: tuple[str, str]
    shared_source_partition_digest: str
    budget_report_digest: str
    comparator_result: str
    paired_receipt_digest: str
    schema_version: str = S2BD_COMPARATOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        candidate = tuple(self.candidate_finding_digests)
        formation = tuple(self.baseline_formation_receipt_digests)
        baseline = tuple(self.baseline_finding_digests)
        probe_ids = tuple(self.baseline_probe_ids)
        if (
            self.schema_version != S2BD_COMPARATOR_SCHEMA_VERSION
            or not isinstance(self.pair_id, str)
            or not self.pair_id
            or len(candidate) != 2
            or len(formation) != 2
            or len(baseline) != 2
            or len(probe_ids) != 2
            or len(set(probe_ids)) != 2
            or any(not isinstance(value, str) or not value for value in probe_ids)
            or any(
                not _valid_digest(value)
                for value in (
                    self.candidate_handoff_result_digest,
                    *candidate,
                    *formation,
                    *baseline,
                    self.shared_source_partition_digest,
                    self.budget_report_digest,
                    self.paired_receipt_digest,
                )
            )
            or self.comparator_result
            not in {
                BASELINE_EXPLAINS_CURRENT_FIXTURE,
                UNEXPECTED_DIFFERENCE_REQUIRES_STATIC_AUDIT,
            }
            or self.paired_receipt_digest != _digest(self.payload_without_digest())
        ):
            raise S2BDPairedRecognitionComparatorError(
                S2BD_COMPARATOR_ATOMIC_RESULT_REQUIRED,
                "paired recognition receipt is incomplete or invalid",
            )
        object.__setattr__(self, "candidate_finding_digests", candidate)
        object.__setattr__(self, "baseline_formation_receipt_digests", formation)
        object.__setattr__(self, "baseline_finding_digests", baseline)
        object.__setattr__(self, "baseline_probe_ids", probe_ids)

    def payload_without_digest(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "pair_id": self.pair_id,
            "candidate_handoff_result_digest": self.candidate_handoff_result_digest,
            "candidate_finding_digests": list(self.candidate_finding_digests),
            "baseline_formation_receipt_digests": list(
                self.baseline_formation_receipt_digests
            ),
            "baseline_finding_digests": list(self.baseline_finding_digests),
            "baseline_probe_ids": list(self.baseline_probe_ids),
            "shared_source_partition_digest": self.shared_source_partition_digest,
            "budget_report_digest": self.budget_report_digest,
            "comparator_result": self.comparator_result,
        }


def _same_functional_result(
    candidate: PPB1ActiveBatchFormationProbeResult,
    auditory_baseline: S2BBStaticPrototypeProbeFinding,
    visual_baseline: S2BBStaticPrototypeProbeFinding,
) -> bool:
    pairs = (
        (candidate.auditory_finding, auditory_baseline),
        (candidate.visual_finding, visual_baseline),
    )
    return all(
        candidate_finding.recognized == baseline_finding.recognized
        and candidate_finding.match_distance == baseline_finding.match_distance
        for candidate_finding, baseline_finding in pairs
    )


def _budget_digest(
    profile: PPB1ReceptorProfileBinding,
    formation_envelope: PPB1ActiveReceptorBatchEnvelope,
    baseline: S2BDBaselineFormationBundle,
) -> str:
    return _digest(
        {
            "candidate_used_prototype_count": {
                "auditory": 1,
                "visual": 1,
            },
            "baseline_used_prototype_count": {
                "auditory": 1,
                "visual": 1,
            },
            "candidate_used_prototype_scalar_count": {
                "auditory": len(profile.auditory_config.carrier_ids),
                "visual": len(profile.visual_config.carrier_ids),
            },
            "baseline_used_prototype_scalar_count": {
                "auditory": len(baseline.auditory_state.prototype_values),
                "visual": len(baseline.visual_state.prototype_values),
            },
            "formation_input_vector_count": {
                "auditory": formation_envelope.auditory_stream.frame_count,
                "visual": formation_envelope.visual_stream.frame_count,
            },
            "candidate_metadata_reported_separately": True,
            "baseline_metadata_reported_separately": True,
            "raw_history_access": False,
        }
    )


def _probe_baseline_modality(
    state: S2BBStaticPrototypeState,
    stream: PPB1ActiveReceptorStreamBinding,
    config: PPB1BankConfig,
) -> S2BBStaticPrototypeProbeFinding:
    return probe_s2bb_static_prototype_read_only(state, stream, config)


def compare_s2bd_ppb1_with_static_prototype_baseline(
    pair_id: str,
    formation_result: PPB1ActiveBatchFormationResult,
    formation_envelope: PPB1ActiveReceptorBatchEnvelope,
    profile: PPB1ReceptorProfileBinding,
    later_probe_envelope: PPB1ActiveReceptorBatchEnvelope,
    candidate_auditory_probe_id: str,
    candidate_visual_probe_id: str,
    baseline_auditory_probe_id: str,
    baseline_visual_probe_id: str,
) -> S2BBPairedRecognitionReceipt:
    """Compare one complete candidate handoff with one independent baseline."""

    validated_pair_id = _identifier(pair_id, "pair_id")
    candidate_ids = (
        _identifier(candidate_auditory_probe_id, "candidate_auditory_probe_id"),
        _identifier(candidate_visual_probe_id, "candidate_visual_probe_id"),
    )
    baseline_ids = (
        _identifier(baseline_auditory_probe_id, "baseline_auditory_probe_id"),
        _identifier(baseline_visual_probe_id, "baseline_visual_probe_id"),
    )
    if len(set((*candidate_ids, *baseline_ids))) != 4:
        raise S2BDPairedRecognitionComparatorError(
            S2BD_COMPARATOR_INVALID_INPUT,
            "candidate and baseline probe identifiers must be separate",
        )
    if (
        type(formation_result) is not PPB1ActiveBatchFormationResult
        or type(formation_envelope) is not PPB1ActiveReceptorBatchEnvelope
        or type(profile) is not PPB1ReceptorProfileBinding
        or type(later_probe_envelope) is not PPB1ActiveReceptorBatchEnvelope
    ):
        raise S2BDPairedRecognitionComparatorError(
            S2BD_COMPARATOR_INVALID_INPUT,
            "exact candidate, envelope and profile types are required",
        )
    if not (
        _one_stabilized_slot(
            profile.auditory_config,
            formation_result.auditory_poststate,
        )
        and _one_stabilized_slot(
            profile.visual_config,
            formation_result.visual_poststate,
        )
    ):
        raise S2BDPairedRecognitionComparatorError(
            S2BD_COMPARATOR_CANDIDATE_INELIGIBLE,
            "exactly one stabilized candidate prototype per modality is required",
        )
    input_digests = (
        formation_result.formation_result_digest,
        formation_envelope.envelope_digest,
        profile.digest(),
        later_probe_envelope.envelope_digest,
        formation_result.auditory_poststate.digest(),
        formation_result.visual_poststate.digest(),
    )
    try:
        baseline = form_s2bb_active_static_prototype_baseline(
            formation_envelope,
            profile,
        )
        candidate = probe_ppb1_active_batch_formation_result_read_only(
            f"{validated_pair_id}.candidate",
            formation_result,
            formation_envelope,
            profile,
            later_probe_envelope,
            candidate_ids[0],
            candidate_ids[1],
        )
        auditory_baseline = _probe_baseline_modality(
            baseline.auditory_state,
            later_probe_envelope.auditory_stream,
            profile.auditory_config,
        )
        visual_baseline = _probe_baseline_modality(
            baseline.visual_state,
            later_probe_envelope.visual_stream,
            profile.visual_config,
        )
    except Exception as exc:
        raise S2BDPairedRecognitionComparatorError(
            S2BD_COMPARATOR_ATOMIC_RESULT_REQUIRED,
            "candidate and both baseline findings are required",
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
        or baseline.auditory_state.digest()
        != auditory_baseline.postprobe_state_digest
        or baseline.visual_state.digest() != visual_baseline.postprobe_state_digest
        or candidate.formation_result_digest != input_digests[0]
        or candidate.formation_envelope_digest != input_digests[1]
        or candidate.profile_binding_digest != input_digests[2]
        or candidate.later_probe_envelope_digest != input_digests[3]
        or auditory_baseline.probe_projection_digest
        != later_probe_envelope.auditory_stream.timed_frames[
            0
        ].ppb1_input_projection_digest
        or visual_baseline.probe_projection_digest
        != later_probe_envelope.visual_stream.timed_frames[
            0
        ].ppb1_input_projection_digest
    ):
        raise S2BDPairedRecognitionComparatorError(
            S2BD_COMPARATOR_ATOMIC_RESULT_REQUIRED,
            "paired sources or states changed during comparison",
        )
    comparator_result = (
        BASELINE_EXPLAINS_CURRENT_FIXTURE
        if _same_functional_result(candidate, auditory_baseline, visual_baseline)
        else UNEXPECTED_DIFFERENCE_REQUIRES_STATIC_AUDIT
    )
    values = {
        "pair_id": validated_pair_id,
        "candidate_handoff_result_digest": candidate.handoff_result_digest,
        "candidate_finding_digests": (
            candidate.auditory_finding.finding_digest,
            candidate.visual_finding.finding_digest,
        ),
        "baseline_formation_receipt_digests": (
            baseline.auditory_receipt.receipt_digest,
            baseline.visual_receipt.receipt_digest,
        ),
        "baseline_finding_digests": (
            auditory_baseline.finding_digest,
            visual_baseline.finding_digest,
        ),
        "baseline_probe_ids": baseline_ids,
        "shared_source_partition_digest": (
            candidate.formation_to_probe_partition_digest
        ),
        "budget_report_digest": _budget_digest(
            profile,
            formation_envelope,
            baseline,
        ),
        "comparator_result": comparator_result,
    }
    return S2BBPairedRecognitionReceipt(
        **values,
        paired_receipt_digest=_digest(
            {"schema_version": S2BD_COMPARATOR_SCHEMA_VERSION, **values}
        ),
    )
