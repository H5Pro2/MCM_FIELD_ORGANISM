"""NQ-only literal source/time binding; historical entry points are never called."""
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from tools import _s2nq_private_mask_scan as s
from tools import _s2ne_private_run as io
from tools import _s2np_private_receptor_materialization as np_material
from mcm_field_organism.receptor_contract import ReceptorContactFrame, CommonFieldTime, from_visual_receptor_state
from mcm_field_organism.receptor_time_model import OrganismTimedReceptorFrame

ROOT = io.ROOT
MATERIAL = ROOT / "reports/s2np/s2np-receptor-nj-materialization-20260907-01/result.json"
MATERIAL_DIGEST = "f548fa82983390465854b1c1b4824c2a32f5b73669cb85c01dc0de853151b9f7"
MATERIAL_HASH = "59796211f0203216a9c71c5b1e93a0326ebcc6d947e7c7ad7d4910d97307f430"


@dataclass(frozen=True, slots=True)
class Event:
    history: str
    event_id: str
    ordinal: int
    audio_source: str
    visual_ordinal: int | None

    @property
    def kind(self):
        return "CUE" if self.visual_ordinal is None else "FORMATION"


_ROWS = (
    (1,"np-a02",0), (1,"np-a01",2),
    (1,"np-a07",None), (1,"np-a08",None), (1,"np-a09",None), (1,"np-a10",None), (1,"np-a11",None), (1,"np-a12",None),
    (2,"np-a01",2),
    (2,"np-a07",None), (2,"np-a08",None), (2,"np-a09",None), (2,"np-a10",None), (2,"np-a11",None), (2,"np-a12",None),
    (3,"np-a02",0), (3,"np-a02",0), (3,"np-a02",0), (3,"np-a02",0),
    (3,"np-a01",2), (3,"np-a01",3), (3,"np-a01",4), (3,"np-a01",5), (3,"np-a01",6),
    (3,"np-a01",7), (3,"np-a01",8), (3,"np-a01",9), (3,"np-a01",10),
    (3,"np-a07",None), (3,"np-a08",None), (3,"np-a09",None), (3,"np-a10",None), (3,"np-a11",None), (3,"np-a12",None),
    (4,"np-a07",None), (4,"np-a12",None),
)
EVENTS = tuple(Event(f"s2nq-h{h:02d}", f"s2nq-e{i+1:02d}", i, a, v) for i,(h,a,v) in enumerate(_ROWS))


def validate_plan(events, neutral=False):
    s.require(type(events) is tuple and 0 < len(events) <= (6 if neutral else 36), "EVENT_PLAN_INVALID")
    seen, histories = set(), []
    for i, e in enumerate(events):
        s.require(type(e) is Event and type(e.ordinal) is int and e.ordinal == i, "EVENT_TIME_INVALID")
        for name in (e.history, e.event_id, e.audio_source):
            s.require(type(name) is str and s.re.fullmatch(r"[a-z][a-z0-9-]{1,63}", name) is not None, "EVENT_ID_INVALID")
        s.require(e.event_id not in seen and (e.visual_ordinal is None or type(e.visual_ordinal) is int
                                            and 0 <= e.visual_ordinal <= 10), "EVENT_FORM_INVALID")
        seen.add(e.event_id)
        if not histories or histories[-1] != e.history:
            s.require(e.history not in histories, "HISTORY_ORDER_INVALID")
            histories.append(e.history)
    s.require(sum(e.kind == "FORMATION" for e in events) <= (4 if neutral else 16), "FORMATION_LIMIT")
    if not neutral:
        s.require(events == EVENTS, "MAIN_PLAN_INVALID")
    else:
        s.require(all(not e.audio_source.startswith("np-") for e in events), "NEUTRAL_SOURCE_INVALID")


def load_catalog():
    execution = np_material.source_plan()
    s.require(io.filehash(MATERIAL) == MATERIAL_HASH, "MATERIAL_FILE_INVALID")
    material = np_material.read_root(MATERIAL, "record_digest")
    s.require(material["record_digest"] == MATERIAL_DIGEST and material["status"] == "RECEPTOR_NJ_MATERIALIZATION_COMPLETE"
              and material["execution_digest"] == execution["execution_digest"], "MATERIAL_BINDING_INVALID")
    s.require(material["source_hashes_before"] == material["source_hashes_after"]
              and all(io.filehash(ROOT/p) == h for p,h in material["source_hashes_before"].items()), "MATERIAL_CODE_CHANGED")
    from tools import _s2jx_default_live_memory_fixtures as visual
    rows = {r["source_id"]: r for r in material["states"]}
    audio = {}
    for source in execution["sources"]:
        sid = source["source_id"]
        if sid in {e.audio_source for e in EVENTS}:
            row = rows[sid]
            s.require(row["pcm_sha256"] == source["pcm_sha256"] and row["source_digest"] == source["source_digest"], "SOURCE_BINDING_INVALID")
            audio[sid] = dict(recipe=source["recipe"], pcm_digest=source["pcm_sha256"],
                source_digest=source["source_digest"], values_digest=s.digest(row["projection"]["values"]))
    images = {str(f.ordinal): dict(payload_digest=f.visual_payload_digest, values_digest=f.visual_values_digest)
              for f in visual.FIXTURES if f.ordinal != 1}
    return dict(audio=audio, visual=images, source_root=execution["execution_digest"], material_root=MATERIAL_DIGEST,
                environment=execution["environment"], generator=execution["generator"])


def projection_decode(p):
    return s.profile.half.HalfScaleAuditory48V1(**{**p, **{k: tuple(p[k]) for k in (
        "carrier_ids", "values", "subnormal_band_indices", "underflow_band_indices")}})


def bind(spec, config, catalog, projection, visual):
    s.require(config == s.profile.build_config(), "PROFILE_INVALID")
    s.profile.half.validate_projection(projection)
    g = spec.ordinal
    s.require((projection.clock_id, projection.snapshot_index, projection.window_start_tick, projection.window_end_tick)
              == ("audio.sample", 20*g, 9600*g, 9600*g+4800), "SOURCE_TIME_INVALID")
    entry = catalog["audio"][spec.audio_source]
    s.require(s.hash_form(entry["pcm_digest"]) and s.hash_form(entry["source_digest"])
              and s.digest(list(projection.values)) == entry["values_digest"], "SOURCE_VALUES_INVALID")
    if spec.kind == "FORMATION":
        s.require(type(visual) is ReceptorContactFrame, "VISUAL_FORM_INVALID")
        vp = config.profile.profile.visual_config
        s.require(visual.modality_id == "visual" and visual.geometry_id == vp.geometry_id and visual.carrier_ids == vp.carrier_ids
                  and (visual.clock_id, visual.window_start_tick, visual.window_end_tick) == ("video.frame", 6*g+2, 6*g+3), "VISUAL_TIME_INVALID")
        image = catalog["visual"][str(spec.visual_ordinal)]
        s.require(s.digest(list(visual.values)) == image["values_digest"], "VISUAL_SOURCE_INVALID")
        at = CommonFieldTime("s2nq-pair-clock", 200000000*g, 200000000*g+100000000)
        vt = CommonFieldTime("s2nq-pair-clock", ((6*g+2)*1000000000)//30, 200000000*g+100000000)
        paired = s.profile.bind_pair(projection=projection, visual=OrganismTimedReceptorFrame(visual,vt),
            common_time=at, pcm_digest=entry["pcm_digest"], rgb_digest=image["payload_digest"], pair_id=spec.event_id)
        bound = s.memory.bind_s2jv_coordinator_input(config=config, source=paired)
    else:
        s.require(visual is None, "CUE_VISUAL_FORBIDDEN")
        bound = tuple(s.bind_cue(projection, entry["pcm_digest"], config, view) for view in s.VIEWS)
    receipt = io.sealed(dict(event=asdict(spec), source_root=catalog["source_root"], source_digest=entry["source_digest"],
        pcm_digest=entry["pcm_digest"], projection=asdict(projection), visual=None if visual is None else asdict(visual),
        visual_payload_digest=None if visual is None else catalog["visual"][str(spec.visual_ordinal)]["payload_digest"]), "binding_digest")
    return receipt, bound


def restore(spec, receipt, config, catalog):
    try:
        s.require(type(receipt) is dict and receipt["binding_digest"] == s.digest({k:v for k,v in receipt.items() if k != "binding_digest"}), "SOURCE_BINDING_INVALID")
        # Check event-specific shape BEFORE any catalog lookup or historical delegation.
        s.require(receipt["event"] == asdict(spec) and (receipt["visual"] is None) == (spec.kind == "CUE")
                  and (receipt["visual_payload_digest"] is None) == (spec.kind == "CUE"), "SOURCE_FORM_INVALID")
        p = projection_decode(receipt["projection"])
        v = receipt["visual"]
        visual = None if v is None else ReceptorContactFrame(**{**v, "carrier_ids":tuple(v["carrier_ids"]), "values":tuple(v["values"])})
        expected, bound = bind(spec, config, catalog, p, visual)
        s.require(s.canonical(expected) == s.canonical(receipt), "SOURCE_BINDING_INVALID")
        return bound
    except s.S2NQError:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        raise s.S2NQError("SOURCE_BINDING_INVALID") from exc


class Sources:
    def __init__(self, config):
        self.config, self.catalog = config, load_catalog()
        self.audio_analyses = self.visual_analyses = self.nj_projections = 0
        self.generate, generator = np_material.b.pure_generator()
        s.require(generator == self.catalog["generator"], "GENERATOR_CHANGED")

    def materialize(self, spec):
        import numpy as np
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from mcm_field_organism.broadband_hearing_path import AuditoryReceptorState, AuditoryReceptorContact
        from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
        from tools import _s2jx_default_live_memory_fixtures as images
        source = self.catalog["audio"][spec.audio_source]
        payload = self.generate(source["recipe"])
        try:
            s.require(len(payload) == 19200 and hashlib.sha256(payload).hexdigest() == source["pcm_digest"], "PCM_PAYLOAD_INVALID")
            samples = np.frombuffer(payload, dtype="<f4")
            try:
                s.require(samples.shape == (4800,) and np.all(np.isfinite(samples)) and np.all(np.abs(samples) <= 1), "PCM_FORM_INVALID")
                self.audio_analyses += 1
                values = LogSpectralReceptor(LogSpectralConfig()).analyze(samples)
            finally:
                del samples
        finally:
            del payload
        nj = s.profile.half
        activity = AuditoryReceptorContact.ACTIVE_ENERGY if any(x != 0 for x in values) else AuditoryReceptorContact.ACTIVE_ZERO
        carriers = self.config.profile.profile.auditory_config.carrier_ids
        raw = AuditoryReceptorState("auditory", nj.RAW_GEOMETRY, 20*spec.ordinal, 9600*spec.ordinal,
            9600*spec.ordinal+4800, carriers, values, activity)
        self.nj_projections += 1
        projection = nj.project_auditory_half_v1(raw, config=LogSpectralConfig(), source_profile_digest=nj.RAW_PROFILE_DIGEST)
        visual = None
        if spec.kind == "FORMATION":
            rgb = images._visual_image(spec.visual_ordinal)
            try:
                image = self.catalog["visual"][str(spec.visual_ordinal)]
                s.require(rgb.shape == (1080,1920,3) and rgb.dtype == np.uint8
                          and hashlib.sha256(memoryview(rgb).cast("B")).hexdigest() == image["payload_digest"], "RGB_PAYLOAD_INVALID")
                self.visual_analyses += 1
                visual = from_visual_receptor_state(LocalChannelGridReceptor(VisualGridConfig()).analyze(rgb,frame_index=6*spec.ordinal+2))
            finally:
                del rgb
        return bind(spec,self.config,self.catalog,projection,visual)
