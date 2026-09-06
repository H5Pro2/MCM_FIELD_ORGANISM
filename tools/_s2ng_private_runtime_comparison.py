"""Bound audio-rule composition over unchanged MR/LM; no source generation."""

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from tools import _s2mr_private_minimal_mcm_runtime as runtime
from tools import _s2lo_private_role_free_stream_runner as field
from tools import _s2ne_private_auditory_transfer as audio
from tools import _s2ne_private_direct_and_verification as direct
from tools import _s2ne_private_run as ne
from tools import _s2kq_private_partial_cue_retrieval_336 as visual
from tools import _s2kq_private_direct_slot_scan_baseline as visual_direct
from tools import _s2jw_default_live_av_pairing as pairing

stream, memory = runtime.stream, ne.memory
digest, canonical = ne.digest, ne.canonical
SCHEMA = "s2ng.runtime-rule-comparison.v1"
MAIN_GATE = False
ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 4_194_304
MAX_STATE_BYTES, MAX_INPUT_BYTES, MAX_PAIR_BYTES = 98_304, 16_384, 16_384
MAX_SCAN_BYTES, MAX_METADATA_BYTES = 32_768, 65_536
MAX_EVENTS, MAX_FORMATIONS, MAX_AUDIO_CUES, MAX_VISUAL_CUES = 28, 20, 4, 4
# 21 states + 28 inputs + 28 paired steps + 32 scans + metadata; JSON framing fits the remainder.
SERIALIZATION_BOUND = 21 * MAX_STATE_BYTES + 28 * (MAX_INPUT_BYTES + MAX_PAIR_BYTES) + 32 * MAX_SCAN_BYTES + MAX_METADATA_BYTES
SOURCE_PATHS = tuple(dict.fromkeys((*audio.SOURCE_PATHS, *field.SOURCE_PATHS,
    "tools/_s2ne_private_run.py", "tools/_s2ne_private_run_verification.py",
    "tools/_s2mr_private_minimal_mcm_runtime.py", "tools/_s2lm_private_role_free_stream_processor.py",
    "tools/_s2lo_private_role_free_stream_runner.py", "tools/_s2kq_private_partial_cue_retrieval_336.py",
    "tools/_s2kq_private_direct_slot_scan_baseline.py", "tools/_s2ng_private_runtime_comparison.py",
    "tools/_s2ng_private_comparison_verification.py", "tools/_s2ng_private_comparison_evaluation.py",
    "docs/S2NG_STATISCHER_RUNTIME_ANBINDUNGSPLAN_AUDITIVE_A_REGEL.md")))


class S2NGError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(condition, code):
    if not condition:
        raise S2NGError(code)


def sealed(payload, key):
    return {**payload, key: digest(payload)}


def sources():
    return tuple((p, hashlib.sha256((ROOT / p).read_bytes()).hexdigest()) for p in SOURCE_PATHS)


@dataclass(frozen=True, slots=True)
class AudioRuleBindingV1:
    rule: str
    config_digest: str
    band_plan_digest: str
    component_sources: tuple[tuple[str, str], ...]
    binding_digest: str

    def payload_without_digest(self):
        return dict(rule=self.rule, config_digest=self.config_digest, band_plan_digest=self.band_plan_digest,
                    component_sources=[list(p) for p in self.component_sources])


def build_binding(config, rule):
    require(rule in audio.RULES, "RULE_INVALID")
    plan = audio.kz.build_auditory_band_plan_48()
    payload = dict(rule=rule, config_digest=config.config_digest, band_plan_digest=plan.plan_digest,
                   component_sources=[list(p) for p in sources()])
    return AudioRuleBindingV1(rule, config.config_digest, plan.plan_digest, sources(), digest(payload))


def validate_binding(binding, config):
    require(type(binding) is AudioRuleBindingV1 and binding.rule in audio.RULES
            and binding.config_digest == config.config_digest
            and binding.band_plan_digest == audio.kz.build_auditory_band_plan_48().plan_digest
            and binding.component_sources == sources()
            and binding.binding_digest == digest(binding.payload_without_digest()), "RULE_BINDING_INVALID")


def budget(event_types):
    require(type(event_types) is tuple and 0 < len(event_types) <= MAX_EVENTS
            and all(t in stream.EVENT_TYPES for t in event_types), "EVENT_BUDGET_INVALID")
    n = event_types.count("COMPLETE_AV_PERCEPTION")
    a, v = event_types.count("PARTIAL_AUDITORY_CUE"), event_types.count("PARTIAL_VISUAL_CUE")
    require(n <= MAX_FORMATIONS and a <= MAX_AUDIO_CUES and v <= MAX_VISUAL_CUES, "SCAN_BUDGET_INVALID")
    return dict(events_per_runtime=len(event_types), formations_total=2*n, auditory_scans=4*a, visual_scans=4*v,
        slot_visits=80*a+64*v, band_differences=1920*a, visual_comparisons=2048*v,
        equality_comparisons=192*a+1152*v, value_comparisons=2112*a+3200*v,
        verification_value_comparisons=2112*a+3200*v, logical_scan_operations=56*a+48*v,
        field_contacts=2*(336*n+48*a+288*v), formation_l1_limit=2*n*3552,
        serialization_bound=SERIALIZATION_BOUND, recording_bytes=MAX_BYTES)


def pack_input(event, config):
    require(type(event) is stream.PerceptionStreamEvent336V1 and event.event_type in stream.EVENT_TYPES
            and event.event_digest == digest(event.payload_without_digest()), "EVENT_INVALID")
    f = event.field_payload
    require(type(f) is field.S2LOFieldInputV1 and type(f.timed_frames) is tuple
            and f.perception_digest == event.perception_digest == event.field_projection_digest
            == event.operation_projection_digest and 0 <= f.start_tick < f.end_tick, "INPUT_BINDING_INVALID")
    frames = {t.frame.modality_id: t for t in f.timed_frames}
    require(len(frames) == len(f.timed_frames), "FRAME_DUPLICATED")
    for modality, timed in frames.items():
        pairing._validate_timed_frame(timed, modality=modality, profile=config.profile.profile)
        require(f.start_tick <= timed.field_time.window_start_tick < timed.field_time.window_end_tick == f.end_tick,
                "FIELD_TIME_INVALID")
    op = event.operation_payload
    if event.event_type == "COMPLETE_AV_PERCEPTION":
        require(type(op) is pairing.S2JVBoundAVPairV1 and set(frames) == {"auditory", "visual"}
                and op.auditory.timed_frame == frames["auditory"] and op.visual.timed_frame == frames["visual"]
                and op.pairing_digest == event.perception_digest, "FORMATION_INPUT_INVALID")
        memory.bind_s2jv_coordinator_input(config=config, source=op)
        operation = asdict(op.plan)
    elif event.event_type == "PARTIAL_AUDITORY_CUE":
        require(type(op) is stream.AuditoryCueOperationV1 and set(frames) == {"auditory"}, "AUDIO_INPUT_INVALID")
        cue = op.cue
        audio.kz._validate_cue(cue, op.band_plan)
        t = frames["auditory"].frame
        require(op.band_plan == audio.kz.build_auditory_band_plan_48() and cue.cue_digest == event.perception_digest
                and cue.config_digest == config.config_digest
                and cue.receptor_values_digest == digest(list(t.values))
                and (cue.auditory_source_clock_id, cue.auditory_window_start_tick, cue.auditory_window_end_tick)
                == (t.clock_id, t.window_start_tick, t.window_end_tick)
                and tuple(cue.values[i] for i in audio.kz.OBSERVED_BANDS) == tuple(t.values[i] for i in audio.kz.OBSERVED_BANDS),
                "AUDIO_SOURCE_INVALID")
        operation = asdict(op)
    else:
        require(type(op) is visual.MaskedMemoryCue336V1 and set(frames) == {"visual"}, "VISUAL_INPUT_INVALID")
        visual._validate_cue(op)
        t = frames["visual"].frame
        require(op.cue_digest == event.perception_digest and op.config_digest == config.config_digest
                and (op.visual_source_clock_id, op.visual_window_start_tick, op.visual_window_end_tick)
                == (t.clock_id, t.window_start_tick, t.window_end_tick)
                and all(op.values[i] == t.values[i] for i in visual.VISIBLE_POSITIONS), "VISUAL_SOURCE_INVALID")
        operation = asdict(op)
    packed_field = asdict(f)
    # Carrier identities are uniquely supplied by the already validated profile.
    for timed in packed_field["timed_frames"]:
        del timed["frame"]["carrier_ids"]
    payload = dict(event={**event.payload_without_digest(), "event_digest": event.event_digest},
                   field=packed_field, operation=operation)
    require(len(canonical(payload)) <= MAX_INPUT_BYTES, "INPUT_SIZE_EXCEEDED")
    return payload


@dataclass(frozen=True, slots=True)
class AudioAdapter:
    binding: AudioRuleBindingV1
    config: object
    baseline: bool
    receipts: dict

    def __call__(self, state, event):
        validate_binding(self.binding, self.config)
        operation = event.operation_payload
        require(type(operation) is stream.AuditoryCueOperationV1, "AUDIO_OPERATION_INVALID")
        key = (event.ordinal, "DIRECT_BASELINE" if self.baseline else "PRIMARY")
        require(key not in self.receipts, "SCAN_ALREADY_USED")
        before = digest(asdict(state))
        function = direct.direct_retrieve if self.baseline else audio.retrieve
        arm = function(rule=self.binding.rule, config=self.config, state=state, cue=operation.cue,
                       band_plan=operation.band_plan)
        require(before == digest(asdict(state)), "SCAN_MUTATED_MEMORY")
        self.receipts[key] = arm
        result = arm.evidence
        return stream.StreamScanResultV1(key[1], event.operation_projection_digest,
            result.prestate_digest, result.poststate_digest, result.decision,
            None if result.hypothesis is None else result.hypothesis.hypothesis_digest,
            arm.arm_digest, result.hypothesis)


@dataclass(frozen=True, slots=True)
class VisualAdapter:
    config: object
    baseline: bool
    receipts: dict

    def __call__(self, state, event):
        key = (event.ordinal, "DIRECT_BASELINE" if self.baseline else "PRIMARY")
        require(key not in self.receipts, "SCAN_ALREADY_USED")
        function = visual_direct.form_direct_partial_cue_slot_scan_baseline_336 if self.baseline else visual.form_partial_cue_retrieval_336
        before = digest(asdict(state))
        result = function(config=self.config, state=state, cue=event.operation_payload)
        require(before == digest(asdict(state)), "SCAN_MUTATED_MEMORY")
        self.receipts[key] = result
        return stream.StreamScanResultV1(key[1], event.operation_projection_digest,
            result.prestate_digest, result.poststate_digest, result.decision,
            None if result.hypothesis is None else result.hypothesis.hypothesis_digest,
            result.result_digest, result.hypothesis)


class ObservedBranch:
    def __init__(self, function, state):
        self.function, self.state, self.last = function, state, None

    def __call__(self, state, event):
        require(state is self.state, "BRANCH_STATE_NOT_OWNED")
        result = self.function(state, event)
        self.state, self.last = result.poststate, result
        return result


def field_record(state):
    return dict(phase=state.phase, field_component_digest=state.field_component_digest,
                last_end_tick=state.last_end_tick, step_count=state.step_count, state_digest=state.state_digest)


class RuntimeComparison:
    """Two independent runtimes, fixed rules and shared immutable reduced inputs."""

    def __init__(self, *, config, events, field_clock_id, comparison_id, mode="NEUTRAL"):
        require(type(events) is tuple and all(type(e) is stream.PerceptionStreamEvent336V1 for e in events), "EVENTS_NOT_IMMUTABLE")
        require(mode in ("NEUTRAL", "MAIN") and (mode == "NEUTRAL" or MAIN_GATE), "MAIN_GATE_CLOSED")
        self.limits = budget(tuple(e.event_type for e in events))
        if mode == "NEUTRAL":
            require(len(events) <= 6 and self.limits["formations_total"] <= 4, "NEUTRAL_LIMIT_EXCEEDED")
        stream._identifier(comparison_id, "comparison id")
        require([e.ordinal for e in events] == list(range(1, len(events)+1)), "EVENT_ORDER_INVALID")
        self.inputs = tuple(pack_input(e, config) for e in events)
        require(all(t.field_time.clock_id == field_clock_id for e in events for t in e.field_payload.timed_frames), "CLOCK_BINDING_INVALID")
        require(events[0].event_type == "COMPLETE_AV_PERCEPTION", "FIRST_EVENT_INVALID")
        self.events, self.config, self.comparison_id, self.mode = events, config, comparison_id, mode
        self.input_digest, self.source_hashes = digest(self.inputs), sources()
        self.rows, self.states, self.subjects, self.branches, self.scans, self.bindings = [], {}, [], [], [], []
        self.initial, self.configs = [], []
        self.failed = self.closed = False
        for i, rule in enumerate(audio.RULES):
            binding = build_binding(config, rule)
            fs = field.initial_s2lo_field_state(events[0].field_payload)
            ms = memory.initial_s2jv_composite_state(config)
            initial = stream.initial_perception_stream_state(stream_id=f"{comparison_id}-arm-{i}",
                field_state=fs, field_state_digest=fs.state_digest, memory_state=ms, memory_state_digest=ms.state_digest)
            fb = ObservedBranch(field.build_s2lo_field_adapter(field_clock_id), fs)
            mb = ObservedBranch(stream.build_s2jw_memory_adapter(config), ms)
            receipts = {}
            processor = stream.RoleFreePerceptionStreamProcessor(field_adapter=fb, memory_adapter=mb,
                auditory_scan=AudioAdapter(binding, config, False, receipts),
                auditory_baseline=AudioAdapter(binding, config, True, receipts),
                visual_scan=VisualAdapter(config, False, receipts), visual_baseline=VisualAdapter(config, True, receipts))
            rc = runtime.build_minimal_runtime_config(runtime_id=f"{comparison_id}-arm-{i}", max_event_count=len(events),
                source_binding_digest=self.input_digest, component_binding_digest=binding.binding_digest)
            subject = runtime.MinimalMCMRuntime336(config=rc, processor=processor, initial_state=initial)
            self.bindings.append(binding)
            self.subjects.append(subject)
            self.branches.append((fb, mb))
            self.scans.append(receipts)
            self.initial.append(dict(snapshot=asdict(subject.snapshot()), field=field_record(fs), memory=ms.state_digest))
            self.configs.append(asdict(rc))
            self._remember(ms)
        self._isolation()

    def _remember(self, state):
        value = asdict(state)
        require(len(canonical(value)) <= MAX_STATE_BYTES, "STATE_SIZE_EXCEEDED")
        require(state.state_digest not in self.states or self.states[state.state_digest] == value, "STATE_DIGEST_COLLISION")
        self.states[state.state_digest] = value
        require(len(self.states) <= MAX_FORMATIONS+1, "STATE_POOL_EXCEEDED")

    def _isolation(self):
        a, b = self.branches
        require(a[0].state is not b[0].state and a[0].state.field is not b[0].state.field
                and a[1].state is not b[1].state and a[1].state.b4_state is not b[1].state.b4_state
                and a[1].state.tspm_state is not b[1].state.tspm_state, "INSTANCE_SHARED")
        require(field_record(a[0].state) == field_record(b[0].state)
                and asdict(a[1].state) == asdict(b[1].state), "SIBLING_STATE_DIFFERS")

    def process_next(self):
        require(not self.closed and not self.failed and len(self.rows) < len(self.events), "COMPARISON_NOT_OPEN")
        index = len(self.rows)
        event = self.events[index]
        require(pack_input(event, self.config) == self.inputs[index], "INPUT_CHANGED")
        pair = []
        for i, subject in enumerate(self.subjects):
            before = subject.snapshot()
            step = subject.process_once(event)
            fs, ms = self.branches[i][0].state, self.branches[i][1].state
            self._remember(ms)
            pair.append(dict(pre=asdict(before), step=asdict(step), post=asdict(subject.snapshot()),
                             field=field_record(fs), memory=ms.state_digest))
        self._isolation()
        require(pack_input(event, self.config) == self.inputs[index], "INPUT_MUTATED")
        row = sealed(dict(event_digest=event.event_digest, arms=pair), "pair_digest")
        require(len(canonical(row)) <= MAX_PAIR_BYTES, "PAIR_SIZE_EXCEEDED")
        self.rows.append(row)
        self.failed = any(a["step"]["error_codes"] for a in pair)
        return row

    def finish(self):
        require(not self.closed and (self.failed or len(self.rows) == len(self.events)), "COMPARISON_INCOMPLETE")
        final = [asdict(s.close()) for s in self.subjects]
        self.closed = True
        scans = []
        for i, receipts in enumerate(self.scans):
            for (ordinal, role), result in sorted(receipts.items()):
                value = asdict(result)
                require(len(canonical(value)) < MAX_SCAN_BYTES, "SCAN_SIZE_EXCEEDED")
                scans.append(dict(arm=i, ordinal=ordinal, role=role, value=value))
        metadata = dict(schema=SCHEMA, comparison_id=self.comparison_id, mode=self.mode,
            status="NOT_EVALUABLE" if self.failed else "RECORDING_COMPLETE",
            input_digest=self.input_digest, config_digest=self.config.config_digest, field_clock_id=self.events[0].field_payload.timed_frames[0].field_time.clock_id,
            sources=[list(p) for p in self.source_hashes], bindings=[asdict(b) for b in self.bindings],
            runtime_configs=self.configs, initial=self.initial, final=final, limits=self.limits)
        require(sources() == self.source_hashes, "SOURCES_CHANGED")
        require(len(canonical(metadata)) <= MAX_METADATA_BYTES, "METADATA_SIZE_EXCEEDED")
        record = sealed({**metadata, "inputs": list(self.inputs), "pairs": self.rows, "states": self.states, "scans": scans}, "record_digest")
        require(len(canonical(record)) <= MAX_BYTES, "RECORD_SIZE_EXCEEDED")
        return record


__all__ = ()
