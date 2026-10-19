"""Existing receptor/NJ chain at the private S2-TY materialization boundary."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass

import numpy as np

from mcm_field_organism.broadband_hearing_path import AuditoryReceptorContact, AuditoryReceptorState
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from tools import _s2nj_private_auditory_output_projection as nj


class S2TYMaterializationError(ValueError):
    def __init__(self, code, phase, counters):
        self.code, self.phase, self.counters, self.reached_step = code, phase, counters.snapshot(), counters.reached_step
        super().__init__(code)


@dataclass
class MaterializationCounters:
    """Counts direct calls at their call sites, including calls that fail."""

    pcm_hashes: int = 0
    audio_analyses: int = 0
    nj_projections: int = 0
    reached_step: str = "NONE"

    def snapshot(self):
        return {
            "pcm_hashes": self.pcm_hashes,
            "audio_analyses": self.audio_analyses,
            "nj_projections": self.nj_projections,
        }


def _need(ok, code, phase, counters):
    if not ok:
        raise S2TYMaterializationError(code, phase, counters)


def _pcm_sha256(payload):
    return hashlib.sha256(payload).hexdigest()


def materialize(endpoint, payload, *, counters):
    """Hash, analyze and project exactly one PCM_F32LE endpoint."""
    _need(type(counters) is MaterializationCounters, "COUNTER_FORM_INVALID", "PCM", counters)
    counters.reached_step = "NONE"
    # The sealed NU generator returns its one live PCM window as bytearray.
    # Accept it directly so the source adapter does not need a second full-size copy.
    _need(type(endpoint) is dict and type(payload) in (bytes, bytearray), "PCM_FORM_INVALID", "PCM", counters)
    counters.pcm_hashes += 1
    counters.reached_step = "HASH"
    actual_hash = _pcm_sha256(payload)
    _need(actual_hash == endpoint.get("pcm_sha256"), "PCM_HASH_INVALID", "PCM", counters)
    _need(len(payload) == 4800 * 4, "PCM_SIZE_INVALID", "PCM", counters)
    try:
        samples = np.frombuffer(payload, dtype="<f4")
        _need(samples.shape == (4800,) and bool(np.isfinite(samples).all()) and bool((np.abs(samples) <= 1.0).all()), "PCM_FORM_INVALID", "PCM", counters)
        receptor = LogSpectralReceptor(LogSpectralConfig(**nj.raw_profile_payload()["config"]))
        counters.audio_analyses += 1
        counters.reached_step = "ANALYZE"
        raw = receptor.analyze(samples)
    except S2TYMaterializationError:
        raise
    except Exception as exc:
        raise S2TYMaterializationError(type(exc).__name__, "RECEPTOR", counters) from exc
    try:
        state = AuditoryReceptorState(
            "auditory", nj.RAW_GEOMETRY, int(endpoint["nj_snapshot_index"]),
            int(endpoint["window_start_sample"]), int(endpoint["window_end_sample"]),
            receptor.channel_ids, raw,
            AuditoryReceptorContact.ACTIVE_ENERGY if any(raw) else AuditoryReceptorContact.ACTIVE_ZERO,
        )
        counters.nj_projections += 1
        counters.reached_step = "NJ"
        half = nj.project_auditory_half_v1(state, config=receptor.config, source_profile_digest=nj.RAW_PROFILE_DIGEST)
        _need(half.profile_digest == endpoint.get("profile"), "NJ_PROFILE_INVALID", "NJ", counters)
    except S2TYMaterializationError:
        raise
    except Exception as exc:
        raise S2TYMaterializationError(type(exc).__name__, "NJ", counters) from exc
    projection_binding = {key: value for key, value in half.payload().items() if key != "values"}
    return {
        "pcm_sha256": actual_hash,
        "payload_bytes": len(payload),
        "raw_state_digest": state.digest(),
        "projection_digest": half.projection_digest,
        "source_values_digest": half.source_values_digest,
        "projection_binding": projection_binding,
        "subnormal_band_indices": list(half.subnormal_band_indices),
        "underflow_band_indices": list(half.underflow_band_indices),
        "values": half.values,
    }
