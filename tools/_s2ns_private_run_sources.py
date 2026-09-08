"""NS-only direct endpoints. Historical index and native NJ index stay distinct."""
from dataclasses import asdict, dataclass
import hashlib
import json
import math

from tools import _s2ns_private_source_binding as b
from tools import _s2ns_private_two_view as s
from tools import _s2ne_private_run as io
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState, AuditoryReceptorContact
from mcm_field_organism.receptor_contract import ReceptorContactFrame, CommonFieldTime, from_visual_receptor_state
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame

SCHEMA = "s2ns.direct-endpoint-native-index.v2"
SEAL_DIR = b.ROOT / "reports/s2ns/s2ns-source-preseal-20260908-01"
FILES = {
    "execution-plan.json": "af2397dd7728426179d4bd2ef2dc9b91504f868aa2d78687913ec9bdcab42c83",
    "evaluation-plan.json": "be812f1f4f9a4155ac517b0a8b9bfafd3fdf2134bd60794fd078e87a8abbcb33",
    "seal.json": "3ea13fda3e74ca7c52048351e78385bf551aa3a90c7f315fb25ac43bf614b705",
}
EXECUTION_DIGEST = "bd21e9e5f564e3a11dc2bb0a3dcb40d92a6a5336e863fa10a57c2eb86aa92816"


def check(value, key):
    s.require(type(value) is dict and value.get(key) == s.digest({k:v for k,v in value.items() if k != key}), "BINDING_DIGEST_INVALID")


def load_plan():
    from tools._s2ns_private_preseal_verification import check_plans
    s.require(all(b.filehash(SEAL_DIR/n) == h for n,h in FILES.items()), "SEALED_FILE_CHANGED")
    x, y, seal = [json.loads((SEAL_DIR/n).read_bytes()) for n in FILES]
    check_plans(x,y)
    check(seal,"seal_digest")
    proof_path = SEAL_DIR/"verification.json"
    s.require(b.filehash(proof_path) == "5ddd9aff54a354f7ee627d3053bc65847d2be4c3a9067793fae0ecb8278aa496","PRESEAL_VERIFICATION_CHANGED")
    s.require(x["execution_digest"] == EXECUTION_DIGEST and seal["execution_digest"] == EXECUTION_DIGEST
        and seal["evaluation_digest"] == y["evaluation_digest"]
        and seal["hashes_before"] == seal["hashes_after"] == b.watched(), "HISTORICAL_BINDING_CHANGED")
    s.require(x["profiles"] == b.profiles() and x["environment"] == b.environment(), "PROFILE_ENVIRONMENT_CHANGED")
    _, _, identities = b.generators()
    s.require(identities == x["generators"], "GENERATOR_CHANGED")
    return x


@dataclass(frozen=True, slots=True)
class TimeBinding:
    plan_digest: str
    event_digest: str
    event_id: str
    endpoint_snapshot_index: int
    nj_snapshot_index: int
    window_start_sample: int
    window_end_sample: int
    schema: str = SCHEMA


def bind_time(event, plan_digest):
    a = event["auditory"]
    start, end, historical = a["start_tick"], a["end_tick"], a["endpoint_snapshot_index"]
    s.require(type(start) is type(end) is type(historical) is int and start >= 0 and historical >= 0
        and start % 480 == 0 and end-start == 4800 and a["clock_id"] == "audio.sample", "NATIVE_TIME_INVALID")
    s.require(s.hashes(plan_digest) and s.identifier(event["event_id"]), "TIME_SOURCE_INVALID")
    return TimeBinding(plan_digest,s.digest(event),event["event_id"],historical,start//480,start,end)


def validate_time(binding, event, plan_digest):
    s.require(type(binding) is TimeBinding and binding == bind_time(event,plan_digest)
        and type(binding.nj_snapshot_index) is int, "TIME_BINDING_INVALID")


def analyze_endpoint(samples, *, event, plan_digest, binding):
    # analyze() is index-free; validate first and construct the raw state only once.
    validate_time(binding,event,plan_digest)
    receptor = LogSpectralReceptor(LogSpectralConfig())
    values = receptor.analyze(samples)
    activity = AuditoryReceptorContact.ACTIVE_ENERGY if any(x != 0 for x in values) else AuditoryReceptorContact.ACTIVE_ZERO
    return AuditoryReceptorState("auditory",s.profile.half.RAW_GEOMETRY,binding.nj_snapshot_index,
        binding.window_start_sample,binding.window_end_sample,receptor.channel_ids,values,activity)


def projection_decode(p):
    return s.profile.half.HalfScaleAuditory48V1(**{**p, **{k:tuple(p[k]) for k in
        ("carrier_ids","values","subnormal_band_indices","underflow_band_indices")}})


def raw_decode(p):
    return AuditoryReceptorState(p["modality_id"],p["geometry_id"],p["snapshot_index"],
        p["window_start_sample"],p["window_end_sample"],tuple(p["carrier_ids"]),tuple(p["energy"]),
        AuditoryReceptorContact(p["contact"]))


def row(plan, source_id):
    found = [x for x in plan["sources"] if x["source_id"] == source_id]
    s.require(len(found) == 1, "SOURCE_ID_INVALID")
    check(found[0],"source_digest")
    return found[0]


def bind_reduced(event, plan, config, binding, raw, projection, visual):
    validate_time(binding,event,plan["execution_digest"])
    s.profile.half.validate_projection(projection)
    s.require(raw.modality_id == "auditory" and raw.geometry_id == s.profile.half.RAW_GEOMETRY
        and raw.carrier_ids == projection.carrier_ids and raw.contact is
        (AuditoryReceptorContact.ACTIVE_ENERGY if any(x != 0 for x in raw.energy) else AuditoryReceptorContact.ACTIVE_ZERO),"RAW_PROFILE_INVALID")
    s.require((raw.snapshot_index,raw.window_start_sample,raw.window_end_sample) ==
        (binding.nj_snapshot_index,binding.window_start_sample,binding.window_end_sample), "RAW_TIME_INVALID")
    s.require(projection.source_state_digest == raw.digest() and projection.source_values_digest == s.digest(list(raw.energy))
        and (projection.snapshot_index,projection.window_start_tick,projection.window_end_tick) ==
        (binding.nj_snapshot_index,binding.window_start_sample,binding.window_end_sample), "RAW_PROJECTION_INVALID")
    a = row(plan,event["auditory"]["source_id"])
    if event["event_type"] == b.AV:
        v = event["visual"]
        s.require(type(visual) is ReceptorContactFrame and v is not None and
            (visual.clock_id,visual.window_start_tick,visual.window_end_tick) ==
            (v["clock_id"],v["start_tick"],v["end_tick"]), "VISUAL_TIME_INVALID")
        image = row(plan,v["source_id"])
        at = CommonFieldTime(event["pairing_clock_id"],*event["auditory"]["common_window"])
        vt = CommonFieldTime(event["pairing_clock_id"],*v["common_window"])
        paired = s.profile.bind_pair(projection=projection,visual=OrganismTimedReceptorFrame(visual,vt),
            common_time=at,pcm_digest=a["payload_sha256"],rgb_digest=image["payload_sha256"],pair_id=event["event_id"])
        bound = s.memory.bind_s2jv_coordinator_input(config=config,source=paired)
    else:
        s.require(event["event_type"] == b.A and visual is None and event["visual"] is None,"CUE_SOURCE_FORM_INVALID")
        bound = s.bind_views(projection=projection,config=config,source_id=a["source_id"],
            source_digest=a["source_digest"],pcm_digest=a["payload_sha256"])
    receipt = io.sealed(dict(schema=SCHEMA,event_digest=s.digest(event),plan_digest=plan["execution_digest"],
        time_binding=asdict(binding),audio_source_digest=a["source_digest"],pcm_digest=a["payload_sha256"],
        raw_state=raw.canonical_payload(),raw_state_digest=raw.digest(),projection=asdict(projection),
        visual=None if visual is None else {k:v for k,v in asdict(visual).items() if k != "carrier_ids"},
        visual_source_digest=None if visual is None else image["source_digest"],
        rgb_digest=None if visual is None else image["payload_sha256"]),"source_binding_digest")
    return receipt,bound


def restore(event, receipt, plan, config):
    try:
        check(receipt,"source_binding_digest")
        s.require((receipt["visual"] is None) == (event["event_type"] == b.A)
            and (receipt["visual_source_digest"] is None) == (event["event_type"] == b.A)
            and (receipt["rgb_digest"] is None) == (event["event_type"] == b.A),"SOURCE_FORM_INVALID")
        raw = raw_decode(receipt["raw_state"])
        p = projection_decode(receipt["projection"])
        # Independent numeric projection check from stored originals, not inverse scaling.
        s.require(len(raw.energy) == 48 and all(type(x) is float and math.isfinite(x) and x >= 0 for x in raw.energy),"RAW_VALUES_INVALID")
        s.require(tuple((x*0.5).hex() for x in raw.energy) == tuple(x.hex() for x in p.values),"HALVING_INVALID")
        s.require(p.underflow_band_indices == tuple(i for i,(x,y) in enumerate(zip(raw.energy,p.values,strict=True))
            if x > 0 and y == 0),"UNDERFLOW_BINDING_INVALID")
        v = receipt["visual"]
        s.require(v is None or "carrier_ids" not in v,"VISUAL_PROFILE_FORM_INVALID")
        visual = None if v is None else ReceptorContactFrame(**{**v,
            "carrier_ids":config.profile.profile.visual_config.carrier_ids,"values":tuple(v["values"])})
        rebuilt,bound = bind_reduced(event,plan,config,TimeBinding(**receipt["time_binding"]),raw,p,visual)
        s.require(s.canonical(rebuilt) == s.canonical(receipt),"SOURCE_BINDING_INVALID")
        return bound
    except s.S2NSError:
        raise
    except (KeyError,TypeError,ValueError,AttributeError) as exc:
        raise s.S2NSError("SOURCE_BINDING_INVALID") from exc


class Sources:
    def __init__(self, config, plan):
        self.config,self.plan = config,plan
        self.audio_analyses = self.nj_projections = self.visual_analyses = 0
        self.phase = "SOURCE_BINDING"
        self.pcm,self.rgb,identities = b.generators()
        s.require(identities == plan["generators"],"GENERATOR_CHANGED")

    def materialize(self,event):
        import numpy as np
        from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
        binding = bind_time(event,self.plan["execution_digest"])
        a = row(self.plan,event["auditory"]["source_id"])
        self.phase = "PCM_PAYLOAD"
        payload = self.pcm(a["recipe"])
        try:
            s.require(len(payload) == 19200 and hashlib.sha256(payload).hexdigest() == a["payload_sha256"],"PCM_PAYLOAD_INVALID")
            samples = np.frombuffer(payload,dtype="<f4")
            try:
                s.require(samples.shape == (4800,) and np.all(np.isfinite(samples)) and np.all(np.abs(samples) <= 1),"PCM_FORM_INVALID")
                self.phase = "AUDIO_ANALYSIS"
                self.audio_analyses += 1
                raw = analyze_endpoint(samples,event=event,plan_digest=self.plan["execution_digest"],binding=binding)
            finally:
                del samples
        finally:
            del payload
        self.phase = "NJ_PROJECTION"
        self.nj_projections += 1
        projection = s.profile.half.project_auditory_half_v1(raw,config=LogSpectralConfig(),source_profile_digest=s.profile.half.RAW_PROFILE_DIGEST)
        visual = None
        if event["visual"] is not None:
            v = event["visual"]
            image = row(self.plan,v["source_id"])
            self.phase = "RGB_PAYLOAD"
            rgb = self.rgb(image["recipe"])
            try:
                s.require(rgb.shape == (1080,1920,3) and rgb.dtype == np.uint8 and
                    hashlib.sha256(memoryview(rgb).cast("B")).hexdigest() == image["payload_sha256"],"RGB_PAYLOAD_INVALID")
                self.phase = "VISUAL_ANALYSIS"
                self.visual_analyses += 1
                visual = from_visual_receptor_state(LocalChannelGridReceptor(VisualGridConfig()).analyze(rgb,frame_index=v["start_tick"]))
            finally:
                del rgb
        self.phase = "SOURCE_CONTACT_BINDING"
        return bind_reduced(event,self.plan,self.config,binding,raw,projection,visual)
