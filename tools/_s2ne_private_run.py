"""Closed S2-NE one-shot execution; one bounded atomic recording, no evaluation."""

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys

from mcm_field_organism.receptor_contract import ReceptorContactFrame, from_visual_receptor_state
from tools import _s2jw_default_live_profile as profiles
from tools import _s2jw_profiled_memory_coordinator as memory
from tools import _s2jw_profiled_memory_ledger as ledgers
from tools import _s2ne_private_auditory_transfer as arms
from tools import _s2ne_private_direct_and_verification as direct
from tools import _s2ne_private_source_binding as pairing

ROOT = Path(__file__).resolve().parents[1]
MAIN_GATE = False
SCHEMA = "s2ne.complete-transfer-recording.v1"
MAX_BYTES = 4194304
PHASES = ("BINDINGS", "INITIAL_STATE", "SOURCE", "FORMATION", "RETRIEVAL", "FINAL_BINDINGS", "PUBLICATION")
PRESEAL = "reports/s2nd/s2nd-source-panel-preseal-20260906-02/"
MATERIALIZED = "reports/s2nd/s2nd-receptor-materialization-20260906-01/result.json"
CONTRACT = "docs/S2NE_PRIVATER_AUDITIVER_MEMORY_TRANSFER_VERTRAG.md"


@dataclass(frozen=True, slots=True)
class Event:
    history_id: str
    event_id: str
    ordinal: int
    audio_source: str
    visual_ordinal: int | None

    @property
    def kind(self):
        return "FORMATION" if self.visual_ordinal is not None else "CUE"


# Source identifiers and positions only; expected decisions live in the evaluator.
_ROWS = (
    (1, "s001", 0), (1, "s007", None), (1, "s008", None), (1, "s009", None), (1, "s010", None),
    (2, "s001", 0), (2, "s004", 2), (2, "s007", None), (2, "s008", None), (2, "s009", None), (2, "s010", None),
    (3, "s004", 2), (3, "s007", None),
    (4, "s001", 0), (4, "s001", 0), (4, "s001", 0), (4, "s001", 0),
    (4, "s004", 2), (4, "s004", 3), (4, "s004", 4), (4, "s004", 5), (4, "s004", 6),
    (4, "s004", 7), (4, "s004", 8), (4, "s004", 9), (4, "s004", 10),
    (4, "s007", None), (4, "s001", 0), (4, "s007", None),
    (5, "s001", 0), (5, "s001", 0), (5, "s007", None), (6, "s007", None),
)


def _literal_events():
    counts, result = {}, []
    for history, audio, visual in _ROWS:
        j = counts.get(history, 0)
        result.append(Event(f"s2ne-h{history:02d}", f"s2ne-h{history:02d}-e{j + 1:02d}", j, audio, visual))
        counts[history] = j + 1
    return tuple(result)


EVENTS = _literal_events()
ARM_ORDER = ((arms.REFERENCE, "PRIMARY"), (arms.REFERENCE, "DIRECT_BASELINE"),
             (arms.ALTERNATIVE, "PRIMARY"), (arms.ALTERNATIVE, "DIRECT_BASELINE"))


def require(ok, code):
    if not ok:
        raise RunError(code)


class RunError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


canonical = arms.kz.canonical_bytes
digest = arms.kz.digest


def sealed(value, key):
    return {**value, key: digest(value)}


def filehash(path):
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def make_config():
    profile = profiles.build_s2jw_default_live_profile()
    return memory.build_s2jv_coordinator_config(tspm_config=profile.tspm_config, b4_capacity=9,
                                               ledger_limits=ledgers.build_s2jv_ledger_limits(profile))


def source_hashes():
    historical = dict(re.findall(r"- `([^`]+)`: `([0-9a-f]{64})`", (ROOT / CONTRACT).read_text(encoding="utf-8")))
    require(len(historical) == 13 and all(filehash(ROOT / p) == h for p, h in historical.items()), "SOURCE_BINDING_INVALID")
    paths = set(historical) | set(arms.SOURCE_PATHS) | {
        "tools/_s2ne_private_run.py", "tools/_s2ne_private_run_verification.py",
        "tools/_s2ne_private_run_evaluation.py", PRESEAL + "seal.json",
        "mcm_field_organism/log_spectral_receptor.py", "mcm_field_organism/finite_video_path.py",
        "mcm_field_organism/receptor_contract.py", "mcm_field_organism/receptor_time_model.py",
    }
    return {p: filehash(ROOT / p) for p in sorted(paths)}


def load_catalog():
    """Read the sealed identities and values; no generation or comparisons."""
    source_hashes()
    execution = json.loads((ROOT / PRESEAL / "execution-plan.json").read_bytes())
    seal = json.loads((ROOT / PRESEAL / "seal.json").read_bytes())
    material = json.loads((ROOT / MATERIALIZED).read_bytes())
    for obj, key in ((execution, "execution_digest"), (seal, "seal_digest"), (material, "record_digest")):
        require(obj[key] == digest({k: v for k, v in obj.items() if k != key}), "SOURCE_ROOT_INVALID")
    require(seal["execution_digest"] == execution["execution_digest"] == material["execution_digest"]
            and seal["seal_digest"] == material["seal_digest"]
            and seal["execution_file_sha256"] == filehash(ROOT / PRESEAL / "execution-plan.json")
            and material["technical_status"] == "RECEPTOR_MATERIALIZATION_COMPLETE", "SOURCE_ROOT_INVALID")
    require(material["input_hashes"] == material["source_hashes_after"]
            and all(filehash(ROOT / p) == h for p, h in material["input_hashes"].items()), "RECEPTOR_SOURCE_CHANGED")
    from tools import _s2jx_default_live_memory_fixtures as visual
    records = {s["source_id"]: s for s in material["states"]}
    audio = {}
    for recipe in execution["sources"]:
        sid = recipe["source_id"]
        if sid in ("s001", "s004", "s007", "s008", "s009", "s010"):
            old = records[sid]
            require(old["pcm_sha256"] == recipe["pcm_sha256"]
                    and old["recipe_digest"] == recipe["recipe_digest"]
                    and digest(old["values"]) == old["values_digest"], "SOURCE_VALUES_INVALID")
            audio[sid] = dict(recipe=recipe, payload_digest=recipe["pcm_sha256"],
                              values_digest=old["values_digest"], values=old["values"],
                              parent_digest=old["materialized_state_digest"])
    images = {str(s.ordinal): dict(payload_digest=s.visual_payload_digest, values_digest=s.visual_values_digest)
              for s in visual.FIXTURES if s.ordinal != 1}
    return dict(audio=audio, visual=images, identity=execution["generator_identity"],
                profile=execution["receptor_profile"], materialization_digest=material["record_digest"])


def check_plan(plan):
    require(type(plan) is tuple and 0 < len(plan) <= 33, "EVENT_PLAN_INVALID")
    seen, histories, counts = set(), [], {}
    for e in plan:
        require(type(e) is Event and type(e.ordinal) is int and e.ordinal >= 0, "EVENT_PLAN_INVALID")
        require(re.fullmatch(r"[a-z][a-z0-9-]{7,83}", e.event_id) is not None
                and re.fullmatch(r"[a-z][a-z0-9-]{7,80}", e.history_id) is not None
                and e.event_id not in seen, "EVENT_ID_INVALID")
        if not histories or histories[-1] != e.history_id:
            require(e.history_id not in histories, "HISTORY_ORDER_INVALID")
            histories.append(e.history_id)
        require(e.ordinal == counts.get(e.history_id, 0), "EVENT_TIME_INVALID")
        counts[e.history_id] = e.ordinal + 1
        seen.add(e.event_id)


def source_record(spec, audio, visual, catalog):
    a = catalog["audio"][spec.audio_source]
    require(digest(list(audio.values)) == a["values_digest"], "AUDIO_VALUES_INVALID")
    return sealed(dict(event=asdict(spec), audio_payload_digest=a["payload_digest"],
                       audio_parent_digest=a["parent_digest"], audio_values_digest=a["values_digest"],
                       audio_frame_digest=digest(asdict(audio)),
                       audio_clock=audio.clock_id, audio_start=audio.window_start_tick, audio_end=audio.window_end_tick,
                       visual_payload_digest=None if visual is None else catalog["visual"][str(spec.visual_ordinal)]["payload_digest"],
                       visual=None if visual is None else asdict(visual)), "source_digest")


def materialized_from_frames(spec, config, catalog, audio, visual):
    require(type(audio) is ReceptorContactFrame and audio.modality_id == "auditory"
            and audio.clock_id == spec.history_id + "-audio-sample"
            and (audio.window_start_tick, audio.window_end_tick) == (9600 * spec.ordinal, 9600 * spec.ordinal + 4800),
            "AUDIO_TIME_INVALID")
    p = config.profile.profile.auditory_config
    require(audio.geometry_id == p.geometry_id and audio.carrier_ids == p.carrier_ids, "AUDIO_GEOMETRY_INVALID")
    receipt = source_record(spec, audio, visual, catalog)
    if spec.kind == "FORMATION":
        require(visual is not None and digest(list(visual.values)) == catalog["visual"][str(spec.visual_ordinal)]["values_digest"],
                "VISUAL_VALUES_INVALID")
        pair = pairing.bind_pair(config=config, auditory=audio, visual=visual, ordinal=spec.ordinal,
            history_id=spec.history_id, event_id=spec.event_id,
            auditory_payload_digest=receipt["audio_payload_digest"], visual_payload_digest=receipt["visual_payload_digest"])
        bound = memory.bind_s2jv_coordinator_input(config=config, source=pair)
    else:
        require(visual is None, "CUE_FORM_INVALID")
        bound = arms.kz.build_masked_auditory_cue_48(
            pcm_payload_digest=receipt["audio_payload_digest"], receptor_state_digest=receipt["audio_frame_digest"],
            receptor_values_digest=receipt["audio_values_digest"], config_digest=config.config_digest,
            auditory_source_clock_id=audio.clock_id, auditory_window_start_tick=audio.window_start_tick,
            auditory_window_end_tick=audio.window_end_tick, observed_values=audio.values[:24],
            band_plan=arms.kz.build_auditory_band_plan_48())
    return receipt, bound


class Sources:
    def __init__(self, config):
        self.catalog = load_catalog()
        identity = self.catalog["identity"]
        require(sys.version == identity["python_version"] and sys.executable == identity["python_executable"]
                and filehash(sys.executable) == identity["python_executable_sha256"], "INTERPRETER_INVALID")
        from reports.s2nd import seal_inventory as generator
        require(generator.math_identity(math, sys.builtin_module_names) == identity["math_module"], "GENERATOR_INVALID")
        self.config = config
        self.audio_analyses = self.visual_analyses = 0

    def materialize(self, spec):
        import numpy as np
        from reports.s2nd import seal_inventory as generator
        from mcm_field_organism.log_spectral_receptor import LogSpectralReceptor, LogSpectralConfig
        from mcm_field_organism.finite_video_path import LocalChannelGridReceptor, VisualGridConfig
        from tools import _s2jx_default_live_memory_fixtures as images
        source = self.catalog["audio"][spec.audio_source]
        payload = generator.pcm_payload(source["recipe"])
        try:
            require(len(payload) == 19200 and hashlib.sha256(payload).hexdigest() == source["payload_digest"], "PCM_PAYLOAD_INVALID")
            samples = np.frombuffer(payload, dtype="<f4")
            try:
                self.audio_analyses += 1
                values = LogSpectralReceptor(LogSpectralConfig(**self.catalog["profile"])).analyze(samples)
            finally:
                del samples
        finally:
            del payload
        values = memory._values(values, 48, "audio source")
        p = self.config.profile.profile.auditory_config
        audio = ReceptorContactFrame("auditory", p.geometry_id, spec.event_id, spec.history_id + "-audio-sample",
                                     9600 * spec.ordinal, 9600 * spec.ordinal + 4800, p.carrier_ids, values)
        visual = None
        if spec.kind == "FORMATION":
            rgb = images._visual_image(spec.visual_ordinal)
            try:
                require(rgb.shape == (1080, 1920, 3) and rgb.dtype == np.uint8
                        and hashlib.sha256(memoryview(rgb).cast("B")).hexdigest()
                        == self.catalog["visual"][str(spec.visual_ordinal)]["payload_digest"], "RGB_PAYLOAD_INVALID")
                self.visual_analyses += 1
                state = LocalChannelGridReceptor(VisualGridConfig()).analyze(rgb, frame_index=6 * spec.ordinal + 2)
                visual = from_visual_receptor_state(state)
            finally:
                del rgb
        return materialized_from_frames(spec, self.config, self.catalog, audio, visual)


def atomic_write(path, record, limit=MAX_BYTES):
    data = canonical(record)
    require(len(data) <= limit, "RECORDING_SIZE_EXCEEDED")
    pending = path.with_name(path.name + ".pending")
    with pending.open("xb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    # A hard link publishes complete bytes without replacing an existing destination.
    os.link(pending, path)
    pending.unlink()


def counts(events):
    formations = [e for e in events if e["kind"] == "FORMATION"]
    cues = [e for e in events if e["kind"] == "CUE"]
    led = [a["evidence"]["resource_ledger"] for e in cues for a in e["arms"]]
    return dict(events=len(events), formations=len(formations), cues=len(cues), arms=len(led),
                slot_visits=sum(l["total_slot_scan_count"] for l in led),
                band_differences=sum(l["observed_comparison_count"] for l in led),
                equality_comparisons=sum(l["internal_equality_comparison_count"] for l in led),
                retrieval_comparisons=sum(l["total_value_comparison_count"] for l in led),
                logical_operations=sum(l["logical_operation_count"] for l in led),
                formation_l1_limit=sum(e["formation"]["ledger"]["functional_l1_term_limit"] for e in formations))


def execute_once(*, run_id, output_root, plan, provider_factory, mode="NEUTRAL", size_limit=MAX_BYTES):
    """Shared bounded loop. MAIN use is restricted to run_main_once below."""
    require(type(run_id) is str and re.fullmatch(r"[a-z][a-z0-9-]{7,89}", run_id) is not None, "RUN_ID_INVALID")
    check_plan(plan)
    require(mode in ("MAIN", "NEUTRAL"), "MODE_INVALID")
    if mode == "MAIN":
        require(MAIN_GATE is True and plan == EVENTS and provider_factory is Sources and size_limit == MAX_BYTES, "MAIN_GATE_CLOSED")
    else:
        require(len(plan) <= 5 and sum(e.kind == "FORMATION" for e in plan) <= 2, "NEUTRAL_LIMIT_EXCEEDED")
    parent = Path(output_root).resolve(strict=True)
    require(mode != "MAIN" or parent == (ROOT / "reports/s2ne").resolve(), "MAIN_OUTPUT_ROOT_INVALID")
    target = parent / run_id
    target.mkdir(exist_ok=False)
    base = dict(schema=SCHEMA, run_id=run_id, mode=mode, plan=[asdict(e) for e in plan],
                plan_digest=digest([asdict(e) for e in plan]), config_digest=None,
                output_directory=str(target), code_before={}, code_after={}, catalog_digest=None)
    events, states, initial, current = [], {}, {}, {}
    phase, index, last_digest, source = "BINDINGS", None, None, None
    attempted_formations = attempted_arms = 0
    try:
        base["code_before"] = source_hashes()
        config = make_config()
        base["config_digest"] = config.config_digest
        source = provider_factory(config)
        base["catalog_digest"] = digest(source.catalog)
        for index, spec in enumerate(plan):
            phase = "INITIAL_STATE"
            if spec.history_id not in current:
                current[spec.history_id] = memory.initial_s2jv_composite_state(config)
                initial[spec.history_id] = current[spec.history_id].state_digest
                states[current[spec.history_id].state_digest] = asdict(current[spec.history_id])
            pre = current[spec.history_id]
            last_digest = pre.state_digest
            before = digest(asdict(pre))
            phase = "SOURCE"
            source_evidence, bound = source.materialize(spec)
            event = dict(spec=asdict(spec), kind=spec.kind, source=source_evidence, prestate=pre.state_digest,
                         poststate=pre.state_digest, formation=None, owner_before=None, cue=None, arms=[])
            if spec.kind == "FORMATION":
                phase = "FORMATION"
                owner = memory.S2JVFormationOwner(spec.event_id + "-owner", run_id,
                    spec.event_id + "-consume", config.config_digest, pre.state_digest, bound.input_digest)
                event["owner_before"] = asdict(owner.snapshot())
                attempted_formations += 1
                formed = memory.advance_s2jv_atomic(config=config, prestate=pre, source=bound, owner=owner)
                event["formation"] = asdict(formed)
                del event["formation"]["poststate"]
                current[spec.history_id] = formed.poststate
                event["poststate"] = formed.poststate.state_digest
                states[formed.poststate.state_digest] = asdict(formed.poststate)
            else:
                phase = "RETRIEVAL"
                event["cue"] = asdict(bound)
                for rule, implementation in ARM_ORDER:
                    function = arms.retrieve if implementation == "PRIMARY" else direct.direct_retrieve
                    attempted_arms += 1
                    result = function(rule=rule, config=config, state=pre, cue=bound,
                                      band_plan=arms.kz.build_auditory_band_plan_48())
                    event["arms"].append(asdict(result))
            require(before == digest(asdict(pre)), "PRESTATE_MUTATED")
            events.append(sealed(event, "event_digest"))
            last_digest = event["poststate"]
        phase = "FINAL_BINDINGS"
        base["code_after"] = source_hashes()
        require(base["code_after"] == base["code_before"], "SOURCE_CHANGED_DURING_RUN")
        metrics = counts(events)
        require(metrics["retrieval_comparisons"] <= 27456 and metrics["formation_l1_limit"] <= 71040, "COUNTER_LIMIT_EXCEEDED")
        if mode == "MAIN":
            require((metrics["events"], metrics["formations"], metrics["cues"], metrics["arms"], metrics["slot_visits"])
                    == (33, 20, 13, 52, 1040)
                    and (source.audio_analyses, source.visual_analyses) == (33, 20), "COMPLETE_COUNTS_INVALID")
        phase = "PUBLICATION"
        record = sealed({**base, "status": "RECORDING_COMPLETE", "initial_states": initial, "states": states,
                         "events": events, "counts": metrics, "failure": None,
                         "attempts": dict(formations=attempted_formations, arms=attempted_arms,
                                          audio=source.audio_analyses, visual=source.visual_analyses)}, "record_digest")
        require(len(canonical(record)) <= size_limit, "RECORDING_SIZE_EXCEEDED")
    except Exception as error:
        base["code_after"] = {p: filehash(ROOT / p) if (ROOT / p).is_file() else None for p in base["code_before"]}
        failure = dict(phase=phase, event_index=index, completed_events=len(events),
                       event_id=None if index is None else plan[index].event_id,
                       last_state_digest=last_digest, error_class=type(error).__name__,
                       code=error.code if isinstance(error, RunError) else "EXECUTION_ERROR")
        record = sealed({**base, "status": "NOT_EVALUABLE", "initial_states": {}, "states": {}, "events": [],
                         "counts": counts(events), "failure": failure,
                         "attempts": dict(formations=attempted_formations, arms=attempted_arms,
                             audio=getattr(source, "audio_analyses", 0), visual=getattr(source, "visual_analyses", 0))}, "record_digest")
    atomic_write(target / "recording.json", record)
    return target / "recording.json"


def run_main_once(*, run_id, output_root=ROOT / "reports/s2ne"):
    global MAIN_GATE
    try:
        require(MAIN_GATE is True, "MAIN_GATE_CLOSED")
        require(Path(output_root).resolve() == (ROOT / "reports/s2ne").resolve(), "MAIN_OUTPUT_ROOT_INVALID")
        return execute_once(run_id=run_id, output_root=output_root, plan=EVENTS,
                            provider_factory=Sources, mode="MAIN")
    finally:
        MAIN_GATE = False


__all__ = ()
