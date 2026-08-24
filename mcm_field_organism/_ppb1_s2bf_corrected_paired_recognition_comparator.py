"""Corrected private entry with complete source preflight before derivation."""

from __future__ import annotations

from ._ppb1_active_batch_formation_consumer import PPB1ActiveBatchFormationResult
from ._ppb1_active_batch_formation_probe_handoff import (
    _validate_formation,
    _validate_probe_envelope,
)
from ._ppb1_active_receptor_batch_binding import PPB1ActiveReceptorBatchEnvelope
from ._ppb1_receptor_profiles import PPB1ReceptorProfileBinding
from ._ppb1_s2bd_paired_recognition_comparator import (
    S2BBPairedRecognitionReceipt,
    S2BDPairedRecognitionComparatorError,
    S2BD_COMPARATOR_INVALID_INPUT,
    compare_s2bd_ppb1_with_static_prototype_baseline,
)


def compare_s2bf_ppb1_with_static_prototype_baseline(
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
    """Reject all source mismatches before entering the deriving comparator."""

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
    _validate_formation(formation_result, formation_envelope, profile)
    _validate_probe_envelope(
        formation_envelope,
        later_probe_envelope,
        profile,
        formation_result,
    )
    return compare_s2bd_ppb1_with_static_prototype_baseline(
        pair_id,
        formation_result,
        formation_envelope,
        profile,
        later_probe_envelope,
        candidate_auditory_probe_id,
        candidate_visual_probe_id,
        baseline_auditory_probe_id,
        baseline_visual_probe_id,
    )
