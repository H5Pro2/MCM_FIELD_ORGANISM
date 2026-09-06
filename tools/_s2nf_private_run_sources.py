"""S2-NF sealed source adapter. Materialization is inside the gated future run."""

import hashlib
import json
import math
import struct

from tools import _s2nf_private_source_binding as binding
from tools import _s2nf_private_preseal_verification as preseal
from tools import _s2ne_private_run as ne

ROOT = binding.ROOT
PRESEAL = "reports/s2nf/s2nf-source-preseal-20260906-01/"
PINS = {
    "execution-plan.json": "f4818993d9994cd5044e99c59b7ee792e4ae2197618afdd9d8d96a8ef6298aee",
    "evaluation-plan.json": "5e8a6a5b0eccb7abe24404a76d0e74453b6eb80ff41a97010d9a37ac27bdb1ae",
    "seal.json": "5ea8c5e9bb387940cffb4129668f77780883abf2ebe5299b98b8e96f9768fd0f",
}
NEW_PATHS = (
    "tools/_s2nf_private_run_sources.py", "tools/_s2nf_private_run.py",
    "tools/_s2nf_private_run_verification.py", "tools/_s2nf_private_run_evaluation.py",
    "tests/test_s2nf_private_run.py", "reports/s2nf/qualify_run_once.py",
)
require, digest = ne.require, ne.digest


def source_hashes():
    history = binding.watched()
    for name, expected in PINS.items():
        require(ne.filehash(ROOT / PRESEAL / name) == expected, "NF_PRESEAL_FILE_CHANGED")
        history[PRESEAL + name] = expected
    return {**history, **{p: ne.filehash(ROOT / p) for p in NEW_PATHS}}


def load_plan():
    source_hashes()
    execution, evaluation, seal = [json.loads((ROOT / PRESEAL / n).read_bytes()) for n in PINS]
    preseal.check_plans(execution, evaluation)
    preseal.check_digest(seal, "seal_digest")
    require(seal["status"] == "S2NF_SOURCES_PRESEALED"
            and seal["execution_digest"] == execution["execution_digest"]
            and seal["evaluation_digest"] == evaluation["evaluation_digest"], "NF_PRESEAL_INVALID")
    return execution


def events_from_plan(execution):
    return tuple(ne.Event(e["history_id"], e["event_id"], e["ordinal"], e["audio_source_id"],
                         None if e["visual_source_id"] is None else {"nf-v01": 0, "nf-v02": 2}[e["visual_source_id"]])
                 for e in execution["events"])


def validate_catalog(catalog, *, main):
    require(set(catalog) == {"audio", "visual", "plan_binding"}, "CATALOG_FORM_INVALID")
    for item in catalog["audio"].values():
        require(set(item) == {"payload_digest", "parent_digest", "values", "values_digest"}, "AUDIO_CATALOG_INVALID")
        require(type(item["values"]) is list, "AUDIO_VALUES_FORM_INVALID")
        ne.memory._values(tuple(item["values"]), 48, "recorded audio")
        require(digest(item["values"]) == item["values_digest"]
                and all(ne.arms.kz._valid_digest(item[k]) for k in ("payload_digest", "parent_digest")), "AUDIO_CATALOG_INVALID")
    if main:
        execution = load_plan()
        require(catalog["plan_binding"] == execution["execution_digest"]
                and set(catalog["audio"]) == {s["source_id"] for s in execution["sources"]}, "CATALOG_PLAN_INVALID")
        for s in execution["sources"]:
            item = catalog["audio"][s["source_id"]]
            require(item["payload_digest"] == s["pcm_sha256"] and item["parent_digest"] == s["source_digest"], "CATALOG_SOURCE_INVALID")
        require(catalog["visual"] == {str(s["ordinal"]): dict(payload_digest=s["payload_sha256"],
                values_digest=s["receptor_values_digest"]) for s in execution["visual_sources"]}, "VISUAL_CATALOG_INVALID")


def bind_values(catalog, source_id, payload_digest, parent_digest, values):
    values = ne.memory._values(values, 48, "audio source")
    item = dict(payload_digest=payload_digest, parent_digest=parent_digest,
                values=list(values), values_digest=digest(list(values)))
    require(source_id not in catalog["audio"] or catalog["audio"][source_id] == item, "REPEATED_SOURCE_DIFFERS")
    catalog["audio"][source_id] = item
    return values


class Sources:
    def __init__(self, config):
        self.config, self.plan = config, load_plan()
        require(self.plan["generator_identity"] == binding.identity(), "NF_INTERPRETER_OR_GENERATOR_CHANGED")
        self.specs = {s.source_id: s for s in binding.source_specs()}
        self.audio_rows = {s["source_id"]: s for s in self.plan["sources"]}
        self.catalog = dict(audio={}, visual={str(s["ordinal"]): dict(payload_digest=s["payload_sha256"],
            values_digest=s["receptor_values_digest"]) for s in self.plan["visual_sources"]},
            plan_binding=self.plan["execution_digest"])
        self.audio_analyses = self.visual_analyses = 0

    def materialize(self, event):
        import numpy as np
        from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
        from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
        from tools import _s2jx_default_live_memory_fixtures as images
        require(event in events_from_plan(self.plan), "SOURCE_EVENT_INVALID")
        spec, row = self.specs[event.audio_source], self.audio_rows[event.audio_source]
        if spec.kind == "HARMONIC":
            payload = binding.harmonic.pcm_payload(json.loads(spec.recipe_json))
            try:
                require(len(payload) == 19200 and hashlib.sha256(payload).hexdigest() == row["pcm_sha256"], "PCM_PAYLOAD_INVALID")
                samples = np.frombuffer(payload, dtype="<f4")
                try:
                    self.audio_analyses += 1
                    values = LogSpectralReceptor(LogSpectralConfig(**self.plan["receptor_profile"])).analyze(samples)
                finally:
                    del samples
            finally:
                del payload
        else:
            function, _ = binding.chirp_functions()
            samples = function({"recipe": json.loads(spec.recipe_json)})
            try:
                sha = hashlib.sha256()
                require(len(samples) == 4800, "PCM_SIZE_INVALID")
                for value in samples:
                    require(math.isfinite(value) and -1 <= value <= 1, "PCM_VALUE_INVALID")
                    sha.update(struct.pack("<f", value))
                require(sha.hexdigest() == row["pcm_sha256"], "PCM_PAYLOAD_INVALID")
                self.audio_analyses += 1
                values = LogSpectralReceptor(LogSpectralConfig(**self.plan["receptor_profile"])).analyze(samples)
            finally:
                del samples
        values = bind_values(self.catalog, event.audio_source, row["pcm_sha256"], row["source_digest"], values)
        p = self.config.profile.profile.auditory_config
        audio = ne.ReceptorContactFrame("auditory", p.geometry_id, event.event_id, event.history_id + "-audio-sample",
            9600 * event.ordinal, 9600 * event.ordinal + 4800, p.carrier_ids, values)
        visual = None
        if event.kind == "FORMATION":
            rgb = images._visual_image(event.visual_ordinal)
            try:
                require(rgb.shape == (1080, 1920, 3) and rgb.dtype == np.uint8
                        and hashlib.sha256(memoryview(rgb).cast("B")).hexdigest()
                        == self.catalog["visual"][str(event.visual_ordinal)]["payload_digest"], "RGB_PAYLOAD_INVALID")
                self.visual_analyses += 1
                state = LocalChannelGridReceptor(VisualGridConfig()).analyze(rgb, frame_index=6 * event.ordinal + 2)
                visual = ne.from_visual_receptor_state(state)
            finally:
                del rgb
        return ne.materialized_from_frames(event, self.config, self.catalog, audio, visual)
