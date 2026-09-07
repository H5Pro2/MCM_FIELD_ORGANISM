"""Sealed NH sources, new half-profile binding; no historical main entry reuse."""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from mcm_field_organism.broadband_hearing_path import BroadbandHearingPath
from mcm_field_organism.log_spectral_receptor import LogSpectralConfig, LogSpectralReceptor
from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
from mcm_field_organism.receptor_contract import from_visual_receptor_state
from tools import _s2nh_private_runtime_binding as nh
from tools import _s2nn_private_half_runtime_binding as nn

source, ng, half = nh.source, nn.ng, nn.half
ROOT, FIELD_CLOCK = nh.ROOT, nh.FIELD_CLOCK
canonical, digest, sealed = source.canonical, source.digest, source.sealed
MAIN_GATE = False
_MAIN_USED = False
SCHEMA = "s2no.half-profile-runtime.v1"
QUAL_ID = "s2no-half-materialization-qualification-20260907-01"
CONTRACT = "docs/S2NO_HALBPROFIL_FUNKTIONSPLAN_MIT_GEBUNDENEN_NH_QUELLEN.md"
NN_QUAL = "reports/s2nn/s2nn-half-profile-runtime-qualification-20260907-02/result.json"
NN_QUAL_SHA = "a335a190ab07b8de572ca4608b73eaf5d783bfb3afa229ffc13875accdccc374"
PROFILE_CONFIG = "55f1de8602c945749728ce17c74cdff8320d1b5fc72c800f239bc86737db1a1e"
VERSIONED = ("mcm_field_organism/_tspm1_private.py", "tools/_s2jw_default_live_av_pairing.py",
    "tools/_s2jw_default_live_profile.py", "tools/_s2jw_profiled_memory_coordinator.py")
OWN = ("tools/_s2no_private_half_materialization.py", "tools/_s2no_private_half_verification.py",
    "tests/test_s2no_private_half_materialization.py", "reports/s2no/qualify_once.py",
    "reports/s2no/QUALIFIKATIONSBINDUNG.md", CONTRACT)
MAX_ENVELOPE_BYTES = nh.MAX_ENVELOPE_BYTES
PHASES = ("BINDINGS", "INITIAL", "PAYLOAD_GENERATION", "PAYLOAD_HASH", "RECEPTOR_ANALYSIS",
          "RECEPTOR_BINDING", "NJ_CONTACT_BINDING", "RUNTIME", "SERIALIZATION")


class S2NOError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NOError(code)


def check(value, key):
    require(type(value) is dict and value.get(key) == digest({k:v for k,v in value.items() if k != key}),
            "DIGEST_INVALID")


def historical_bindings(execution, qualified):
    """Only four explicitly versioned paths use the pinned NL/NN qualification."""
    pins = execution["source_hashes"]
    require(set(VERSIONED) <= set(pins) and qualified["status"] == "S2NN_HALF_RUNTIME_QUALIFIED",
            "PROFILE_PROVENANCE_INVALID")
    expected = {p: qualified["hashes_after"][p] if p in VERSIONED else h for p,h in pins.items()}
    require(all(source.filehash(ROOT/p) == h for p,h in expected.items()), "HISTORICAL_SOURCE_CHANGED")
    return expected


def load_execution():
    require(all(source.filehash(ROOT/nh.SEAL_DIR/p) == h for p,h in nh.PINS.items()), "NH_SEAL_CHANGED")
    require(source.filehash(ROOT/NN_QUAL) == NN_QUAL_SHA, "NN_QUALIFICATION_CHANGED")
    execution = json.loads((ROOT/nh.SEAL_DIR/"execution-plan.json").read_bytes())
    historical_bindings(execution, json.loads((ROOT/NN_QUAL).read_bytes()))
    require(execution["generator_identity"] == source.identity(), "GENERATOR_IDENTITY_CHANGED")
    return nh.BoundExecution("MAIN", canonical(execution).decode("ascii"))


def watched():
    execution = json.loads((ROOT/nh.SEAL_DIR/"execution-plan.json").read_bytes())
    require(source.filehash(ROOT/NN_QUAL) == NN_QUAL_SHA, "NN_QUALIFICATION_CHANGED")
    old = historical_bindings(execution, json.loads((ROOT/NN_QUAL).read_bytes()))
    paths = set(old) | set(OWN) | {p for p,_ in nn.sources()} | {p for p,_ in ng.sources()}
    paths |= {NN_QUAL} | {nh.SEAL_DIR+"/"+p for p in nh.PINS}
    return {p:source.filehash(ROOT/p) for p in sorted(paths)}


def profile_binding(config):
    nn.validate_config(config)
    require(config.config_digest == PROFILE_CONFIG, "PROFILE_CONFIG_INVALID")
    return dict(schema="s2no.profile-binding.v1", config_digest=config.config_digest,
        raw_profile_digest=half.RAW_PROFILE_DIGEST, output_profile_digest=half.PROFILE_DIGEST,
        rank_binding=config.tspm_config.fast_config.rank_binding,
        rules=list(ng.audio.RULES), nn_sources=[list(p) for p in nn.sources()])


def compact_projection(projection):
    return {k:getattr(projection,k) for k in ("source_state_digest", "source_values_digest",
        "projection_digest", "subnormal_band_indices", "underflow_band_indices")}


@dataclass(frozen=True, slots=True)
class MaterializedV1:
    events: tuple
    receipts_json: str
    metrics_json: str
    execution_digest: str


class Materializer:
    def __init__(self, bound, config):
        require(type(bound) is nh.BoundExecution, "BOUND_EXECUTION_REQUIRED")
        require(bound.mode != "MAIN" or MAIN_GATE, "MAIN_GATE_CLOSED")
        profile_binding(config)
        self.bound, self.config, self.execution = bound, config, bound.payload()
        # The source plan retains its historical profile. Never rewrite it to pass validation.
        require(self.execution["profile"]["coordinator_config_digest"] == ng.ne.make_config().config_digest,
                "SOURCE_PROFILE_INVALID")
        self.used = False
        self.phase, self.ordinal, self.source_id = "INITIAL", None, None
        self.metrics = dict(audio_windows=0, visual_frames=0, audio_hops=0, audio_snapshots=0,
                            nj_projections=0, completed_events=0)

    def run_once(self):
        require(not self.used, "MATERIALIZATION_ALREADY_USED")
        require(self.bound.mode != "MAIN" or MAIN_GATE, "MAIN_GATE_CLOSED")
        self.used = True
        hearing = BroadbandHearingPath(LogSpectralReceptor(LogSpectralConfig()))
        visual_receptor = LocalChannelGridReceptor(VisualGridConfig())
        sources = {s["source_id"]:s for s in self.execution["sources"]}
        events, receipts = [], []
        for spec in self.execution["events"]:
            self.ordinal = spec["ordinal"]
            raw_audio = visual = None
            base = dict(spec_digest=digest(spec), auditory=None, visual=None)
            for modality in ("auditory", "visual"):
                part = spec[modality]
                if part is None:
                    continue
                s = sources[part["source_id"]]
                self.source_id, self.phase = s["source_id"], "PAYLOAD_GENERATION"
                payload = source.pcm_payload(s["recipe"]) if modality == "auditory" else source.rgb_payload(s["recipe"])
                try:
                    self.phase = "PAYLOAD_HASH"
                    view = memoryview(payload).cast("B")
                    try:
                        require(view.nbytes == s["byte_count"] and hashlib.sha256(view).hexdigest() == s["payload_sha256"],
                                "PAYLOAD_HASH_INVALID")
                    finally:
                        view.release()
                        del view
                    self.phase = "RECEPTOR_ANALYSIS"
                    if modality == "auditory":
                        require(self.metrics["audio_windows"] < 24, "AUDIO_LIMIT")
                        samples = np.frombuffer(payload, dtype="<f4")
                        try:
                            for hop in range(10):
                                raw_audio = hearing.push(tuple(float(v) for v in samples[hop*480:(hop+1)*480]))
                                self.metrics["audio_hops"] += 1
                                self.metrics["audio_snapshots"] = hearing.snapshot_count
                        finally:
                            del samples
                        self.metrics["audio_windows"] += 1
                        self.phase = "RECEPTOR_BINDING"
                        require(raw_audio is not None and (raw_audio.snapshot_index, raw_audio.window_start_sample,
                            raw_audio.window_end_sample) == (part["endpoint_snapshot_index"], part["start_tick"], part["end_tick"]),
                            "AUDIO_ENDPOINT_INVALID")
                    else:
                        require(self.metrics["visual_frames"] < 24, "VISUAL_LIMIT")
                        state = visual_receptor.analyze(payload, frame_index=part["start_tick"])
                        self.metrics["visual_frames"] += 1
                        visual = nn.OrganismTimedReceptorFrame(from_visual_receptor_state(state),
                            nn.CommonFieldTime(FIELD_CLOCK, *part["common_window"]))
                        del state
                finally:
                    del payload
                base[modality] = dict(source_id=s["source_id"], payload_sha256=s["payload_sha256"])
            self.phase = "NJ_CONTACT_BINDING"
            if spec["auditory"] is not None:
                self.source_id = spec["auditory"]["source_id"]
            part = spec["auditory"] or spec["visual"]
            common = nn.CommonFieldTime(FIELD_CLOCK, *part["common_window"])
            value = nn.bind_event(config=self.config, event_id="s2no-event-"+spec["event_id"], ordinal=self.ordinal,
                event_type=spec["event_type"], field_start_tick=(self.ordinal-1)*100000000, common_time=common,
                raw_audio=raw_audio, pcm_digest=None if raw_audio is None else base["auditory"]["payload_sha256"],
                visual=visual, rgb_digest=None if visual is None else base["visual"]["payload_sha256"],
                visual_time_binding=visual.field_time if spec["event_type"] == source.AV else None)
            nj = None if value.auditory_projection is None else compact_projection(value.auditory_projection)
            self.metrics["nj_projections"] += int(nj is not None)
            receipts.append(sealed(dict(base=base, nj=nj, event_digest=value.event.event_digest), "receipt_digest"))
            events.append(value.event)
            del raw_audio, visual, value
            self.metrics["completed_events"] += 1
        self.source_id = None
        return MaterializedV1(tuple(events), canonical(receipts).decode(), canonical(self.metrics).decode(),
                              self.execution["execution_digest"])


def compose(materialized, config, run_id, mode):
    require(type(materialized) is MaterializedV1 and mode in ("NEUTRAL", "MAIN"), "MATERIALIZED_TYPE_INVALID")
    require(mode != "MAIN" or MAIN_GATE, "MAIN_GATE_CLOSED")
    profile_binding(config)
    comparison = ng.RuntimeComparison.__new__(ng.RuntimeComparison)
    try:
        comparison.__init__(config=config, events=materialized.events, field_clock_id=FIELD_CLOCK,
                            comparison_id=run_id, mode=mode)
        for _ in materialized.events:
            comparison.process_next()
            if comparison.failed:
                break
        return comparison.finish()
    finally:
        for subject in getattr(comparison, "subjects", ()):
            if subject.snapshot().status == "OPEN":
                subject.close()


def envelope(run_id, bound, config, materialized=None, comparison=None, failure=None, binding_digest=None):
    result = sealed(dict(schema=SCHEMA, run_id=run_id, execution_digest=bound.payload()["execution_digest"],
        profile=profile_binding(config), binding_digest=binding_digest, main_gate_after=False,
        status="RECORDING_COMPLETE" if comparison is not None and comparison["status"] == "RECORDING_COMPLETE"
            and failure is None else "NOT_EVALUABLE", comparison=comparison,
        source_receipts=[] if materialized is None else json.loads(materialized.receipts_json),
        materialization=None if materialized is None else json.loads(materialized.metrics_json), failure=failure), "record_digest")
    require(len(canonical(result)) <= ng.MAX_BYTES
        and len(canonical({**result, "comparison":None})) <= MAX_ENVELOPE_BYTES, "RECORD_SIZE_EXCEEDED")
    return result


def failure_evidence(phase, error, materializer=None):
    return dict(phase=phase if materializer is None else materializer.phase,
        ordinal=None if materializer is None else materializer.ordinal,
        source_id=None if materializer is None else materializer.source_id,
        metrics=None if materializer is None else dict(materializer.metrics),
        error_class=type(error).__name__, code=error.code if isinstance(error, S2NOError) else "NO_TECHNICAL_ERROR")


def run_main_once(run_id, output):
    global MAIN_GATE, _MAIN_USED
    created = False
    bound = materializer = materialized = comparison = None
    phase, failure, hashes = "BINDINGS", None, None
    config = None
    try:
        require(MAIN_GATE and not _MAIN_USED and not ng.MAIN_GATE, "MAIN_GATE_CLOSED_OR_USED")
        require(re.fullmatch(r"s2no-half-runtime-[0-9]{8}-[0-9]{2}", run_id) is not None
            and Path(output).resolve() == (ROOT/"reports/s2no"/run_id).resolve(), "RUN_DESTINATION_INVALID")
        _MAIN_USED = True
        config = nn.profile.build_config()
        Path(output).mkdir(exist_ok=False)
        created = True
        hashes = watched()
        q = json.loads((ROOT/"reports/s2no"/QUAL_ID/"result.json").read_bytes())
        require(q["status"] == "S2NO_CONNECTION_QUALIFIED" and q["hashes_after"] == hashes,
                "QUALIFICATION_REQUIRED")
        bound = load_execution()
        phase = "INITIAL"
        materializer = Materializer(bound, config)
        materialized = materializer.run_once()
        phase = "RUNTIME"
        ng.MAIN_GATE = True
        comparison = compose(materialized, config, run_id, "MAIN")
        require(hashes == watched(), "SOURCES_CHANGED")
        phase = "SERIALIZATION"
        result = envelope(run_id, bound, config, materialized, comparison, binding_digest=digest(hashes))
    except Exception as error:
        if not created:
            raise
        failure = failure_evidence(phase, error, materializer if phase == "INITIAL" else None)
        # The fixed sealed root is sufficient to bind a pre-materialization failure.
        result = sealed(dict(schema=SCHEMA, run_id=run_id, execution_digest=nh.EXECUTION_DIGEST,
            profile=profile_binding(config), binding_digest=None if hashes is None else digest(hashes),
            main_gate_after=False, status="NOT_EVALUABLE", comparison=None, source_receipts=[],
            materialization=None, failure=failure), "record_digest")
    finally:
        MAIN_GATE = False
        ng.MAIN_GATE = False
    ng.ne.atomic_write(Path(output)/"recording.json", result)
    return result
