"""Private half-profile inputs composed with unchanged NG/MR/LO adapters."""

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from mcm_field_organism.receptor_contract import ReceptorContactFrame, CommonFieldTime
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig
from tools import _s2nj_private_auditory_output_projection as half
from tools import _s2nl_private_half_profile_binding as profile
from tools import _s2ng_private_runtime_comparison as ng
from tools import _s2ng_private_comparison_verification as verification

MAIN_GATE = False
SCHEMA = "s2nn.private.half-profile-runtime-input.v1"
MAX_BOUND_INPUT_BYTES = 65536
ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATHS = ("tools/_s2nn_private_half_runtime_binding.py",
                "tools/_s2nj_private_auditory_output_projection.py",
                "tools/_s2nl_private_half_profile_binding.py")


class S2NNError(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise S2NNError(code)


def sources():
    return tuple((p, hashlib.sha256((ROOT/p).read_bytes()).hexdigest()) for p in SOURCE_PATHS)


def validate_config(config):
    ng.memory._validate_config(config)
    require(config == profile.build_config(), "HALF_PROFILE_REQUIRED")


@dataclass(frozen=True, slots=True)
class HalfRuntimeInputV1:
    event: ng.stream.PerceptionStreamEvent336V1
    auditory_projection: half.HalfScaleAuditory48V1 | None
    pcm_digest: str | None
    rgb_digest: str | None
    config_digest: str
    component_sources: tuple[tuple[str, str], ...]
    binding_digest: str
    schema: str = SCHEMA

    def payload_without_digest(self):
        return {k: v for k, v in asdict(self).items() if k != "binding_digest"}


def source_payload(config, projection, pcm_digest, rgb_digest, visual, component_sources):
    return dict(schema=SCHEMA, output_profile_digest=half.PROFILE_DIGEST,
        config_digest=config.config_digest,
        projection_digest=None if projection is None else projection.projection_digest,
        pcm_digest=pcm_digest, rgb_digest=rgb_digest,
        visual_digest=None if visual is None else half.digest(asdict(visual)),
        component_sources=[list(p) for p in component_sources])


def bind_event(*, config, event_id, ordinal, event_type, field_start_tick,
               common_time, raw_audio=None, pcm_digest=None, visual=None, rgb_digest=None):
    """Only raw receptor states enter the one NJ call, never NJ projections."""
    validate_config(config)
    require(event_type in ng.stream.EVENT_TYPES and type(common_time) is CommonFieldTime,
            "EVENT_FORM_INVALID")
    full = event_type == "COMPLETE_AV_PERCEPTION"
    has_audio = full or event_type == "PARTIAL_AUDITORY_CUE"
    has_visual = full or event_type == "PARTIAL_VISUAL_CUE"
    require((raw_audio is not None) == has_audio and (visual is not None) == has_visual,
            "MODALITY_FORM_INVALID")
    require((ng.audio.kz._valid_digest(pcm_digest) if has_audio else pcm_digest is None)
            and (ng.audio.kz._valid_digest(rgb_digest) if has_visual else rgb_digest is None),
            "SOURCE_DIGEST_INVALID")
    if has_visual:
        ng.pairing._validate_timed_frame(visual, modality="visual", profile=config.profile.profile)
        require(visual.field_time == common_time, "VISUAL_TIME_INVALID")
    projection = None
    if has_audio:
        projection = half.project_auditory_half_v1(raw_audio, config=LogSpectralConfig(),
                                                  source_profile_digest=half.RAW_PROFILE_DIGEST)
    if full:
        op = profile.bind_pair(projection=projection, visual=visual, common_time=common_time,
                               pcm_digest=pcm_digest, rgb_digest=rgb_digest, pair_id=event_id)
        frames, perception = (op.auditory.timed_frame, op.visual.timed_frame), op.pairing_digest
    elif has_audio:
        cue = profile.bind_cue(projection=projection, pcm_digest=pcm_digest, config=config)
        audio = OrganismTimedReceptorFrame(ReceptorContactFrame("auditory", projection.geometry_id,
            "half."+projection.projection_digest, projection.clock_id, projection.window_start_tick,
            projection.window_end_tick, projection.carrier_ids, projection.values), common_time)
        op = ng.stream.AuditoryCueOperationV1(cue, ng.audio.kz.build_auditory_band_plan_48())
        frames, perception = (audio,), cue.cue_digest
    else:
        require(all(visual.frame.values[i] == 0.0 for i in ng.visual.MASKED_POSITIONS),
                "VISUAL_CUE_NOT_OCCLUDED")
        op = ng.visual.build_masked_memory_cue_336(source_digest=rgb_digest, config_digest=config.config_digest,
            field_clock_id=common_time.clock_id, window_start_tick=common_time.window_start_tick,
            window_end_tick=common_time.window_end_tick, visual_source_clock_id=visual.frame.clock_id,
            visual_window_start_tick=visual.frame.window_start_tick, visual_window_end_tick=visual.frame.window_end_tick,
            values=tuple(visual.frame.values[i] if i in ng.visual.VISIBLE_POSITIONS else None for i in range(288)))
        frames, perception = (visual,), op.cue_digest
    component_sources = sources()
    source = half.digest(source_payload(config, projection, pcm_digest, rgb_digest, visual, component_sources))
    field = ng.field.S2LOFieldInputV1(perception, field_start_tick, common_time.window_end_tick, frames)
    event = ng.stream.build_perception_stream_event(event_id=event_id, ordinal=ordinal, event_type=event_type,
        source_digest=source, perception_digest=perception, field_projection_digest=perception,
        operation_projection_digest=perception, field_payload=field, operation_payload=op)
    value = HalfRuntimeInputV1(event, projection, pcm_digest, rgb_digest, config.config_digest,
                               component_sources, "")
    value = HalfRuntimeInputV1(event, projection, pcm_digest, rgb_digest, config.config_digest,
        component_sources, half.digest(value.payload_without_digest()))
    return validate_input(value, config)


def validate_input(value, config):
    validate_config(config)
    require(type(value) is HalfRuntimeInputV1 and value.schema == SCHEMA
            and value.config_digest == config.config_digest and value.component_sources == sources()
            and value.binding_digest == half.digest(value.payload_without_digest()), "INPUT_BINDING_INVALID")
    require(len(half.canonical(asdict(value))) <= MAX_BOUND_INPUT_BYTES, "INPUT_SIZE_EXCEEDED")
    ng.pack_input(value.event, config)
    frames = {t.frame.modality_id: t for t in value.event.field_payload.timed_frames}
    projection = value.auditory_projection
    if "auditory" in frames:
        require(projection is not None, "PROJECTION_MISSING")
        half.validate_projection(projection)
        t = frames["auditory"].frame
        require(t.values == projection.values and t.geometry_id == projection.geometry_id
                and t.snapshot_id == "half."+projection.projection_digest
                and (t.clock_id, t.window_start_tick, t.window_end_tick) ==
                    (projection.clock_id, projection.window_start_tick, projection.window_end_tick),
                "PROJECTION_FRAME_MISMATCH")
        op = value.event.operation_payload
        if value.event.event_type == "COMPLETE_AV_PERCEPTION":
            require(op.plan.auditory_payload_digest == value.pcm_digest
                    and op.plan.visual_payload_digest == value.rgb_digest, "PAIR_SOURCE_MISMATCH")
        else:
            require(op.cue.pcm_payload_digest == value.pcm_digest
                    and op.cue.receptor_state_digest == projection.projection_digest
                    and value.rgb_digest is None, "CUE_SOURCE_MISMATCH")
    else:
        require(projection is None and value.pcm_digest is None, "UNEXPECTED_AUDIO")
        require(value.event.operation_payload.source_digest == value.rgb_digest
                and all(frames["visual"].frame.values[i] == 0.0 for i in ng.visual.MASKED_POSITIONS),
                "VISUAL_SOURCE_MISMATCH")
    require(value.event.source_digest == half.digest(source_payload(config, projection,
        value.pcm_digest, value.rgb_digest, frames.get("visual"), value.component_sources)), "SOURCE_BINDING_INVALID")
    return value


def build_comparison(*, inputs, comparison_id, field_clock_id, config, mode="NEUTRAL"):
    require(mode == "NEUTRAL", "MAIN_GATE_CLOSED")
    require(type(inputs) is tuple, "IMMUTABLE_INPUTS_REQUIRED")
    validate_config(config)
    events = tuple(validate_input(v, config).event for v in inputs)
    return ng.RuntimeComparison(config=config, events=events, field_clock_id=field_clock_id,
                                comparison_id=comparison_id, mode="NEUTRAL")


def verify_comparison(record, *, inputs, config):
    validate_config(config)
    require(type(inputs) is tuple, "IMMUTABLE_INPUTS_REQUIRED")
    packed = [ng.pack_input(validate_input(v, config).event, config) for v in inputs]
    require(ng.canonical(packed) == ng.canonical(record["inputs"]), "RECORDED_INPUTS_DIFFER")
    return verification.verify_record(record, config=config)
