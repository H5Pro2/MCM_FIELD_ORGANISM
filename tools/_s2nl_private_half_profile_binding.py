"""Closed half-profile connection to existing atomic memory; no runtime or field."""

from dataclasses import asdict

from mcm_field_organism.receptor_contract import ReceptorContactFrame, CommonFieldTime
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from tools import _s2nj_private_auditory_output_projection as half
from tools import _s2jw_default_live_av_pairing as pairing
from tools import _s2jw_profiled_memory_coordinator as memory
from tools._s2jw_default_live_profile import build_private_half_profile
from tools._s2jw_profiled_memory_ledger import build_s2jv_ledger_limits
from tools import _s2kz_private_auditory_partial_cue_retrieval_336 as cues

MAIN_GATE = False
MAX_PAIR_BYTES = 65536


def build_config():
    profile = build_private_half_profile()
    limits = build_s2jv_ledger_limits(profile)
    payload = dict(schema=memory.HALF_COORDINATOR_SCHEMA, profile_digest=profile.binding_digest,
        tspm_config_digest=profile.tspm_config.config_binding_digest,
        ledger_limits_digest=limits.limits_digest, b4_capacity=9,
        auditory_dimension=48, visual_dimension=288, av_dimension=336)
    return memory.S2JVCoordinatorConfigV1(profile, profile.tspm_config, limits, 9, 48, 288, 336,
                                         memory._digest(payload), memory.HALF_COORDINATOR_SCHEMA)


def bind_pair(*, projection, visual, common_time, pcm_digest, rgb_digest, pair_id):
    """Consume the NJ projection, never multiply it again or recreate raw spectra."""
    half.validate_projection(projection)
    if type(common_time) is not CommonFieldTime:
        raise half.S2NJProjectionError("COMMON_TIME_INVALID")
    audio = OrganismTimedReceptorFrame(ReceptorContactFrame(
        "auditory", projection.geometry_id, "half." + projection.projection_digest,
        projection.clock_id, projection.window_start_tick, projection.window_end_tick,
        projection.carrier_ids, projection.values), common_time)
    profile = build_private_half_profile()
    # The source contract binds the NJ result as well as the canonical PCM identity.
    source_id = "half." + half.digest(dict(projection=projection.projection_digest, pcm=pcm_digest))
    plan = pairing.build_s2jv_pairing_plan(pair_id=pair_id, source_contract_id=source_id,
        profile=profile, auditory=audio, visual=visual,
        auditory_payload_digest=pcm_digest, visual_payload_digest=rgb_digest)
    result = pairing.bind_s2jv_default_live_pair(pairing_plan=plan, profile=profile,
                                               auditory=audio, visual=visual)
    if len(half.canonical(asdict(result))) > MAX_PAIR_BYTES:
        raise half.S2NJProjectionError("PAIR_SIZE_LIMIT")
    return result


def bind_cue(*, projection, pcm_digest, config):
    half.validate_projection(projection)
    memory._validate_config(config)
    if config != build_config():
        raise half.S2NJProjectionError("CUE_PROFILE_MIXED")
    return cues.build_masked_auditory_cue_48(
        pcm_payload_digest=pcm_digest, receptor_state_digest=projection.projection_digest,
        receptor_values_digest=half.digest(list(projection.values)), config_digest=config.config_digest,
        auditory_source_clock_id=projection.clock_id,
        auditory_window_start_tick=projection.window_start_tick,
        auditory_window_end_tick=projection.window_end_tick,
        observed_values=projection.values[:24], band_plan=cues.build_auditory_band_plan_48())
