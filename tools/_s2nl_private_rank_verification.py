"""Independent ranked full-scan arithmetic; no transition or probe execution."""

from dataclasses import asdict, dataclass
import math

from mcm_field_organism import _tspm1_private as core
from tools import _s2jw_profiled_memory_coordinator as memory

MAX_RANK_BYTES = 16384
MAX_FAST_TERMS = 1008
MAX_B4_TERMS = 3024


class RankBindingError(ValueError):
    pass


def require(ok):
    if not ok:
        raise RankBindingError("S2NL_RANK_BINDING_INVALID")


@dataclass(frozen=True, slots=True)
class RankRow:
    slot_id: str
    slot_digest: str
    auditory_distance: float
    visual_distance: float
    applicable: bool
    key: tuple


@dataclass(frozen=True, slots=True)
class RankEvidence:
    config_digest: str
    state_digest: str
    source_digest: str
    mode: str
    rows: tuple[RankRow, ...]
    selected_slot_id: str | None
    selected_slot_digest: str | None
    selected_key: tuple | None
    term_count: int
    evidence_digest: str

    def payload(self):
        result = asdict(self)
        del result["evidence_digest"]
        return result


def direct_key(config, audio, visual, slot_id, *, formation_index=None):
    # Deliberately no core joint_rank_prefix, scan helper or selected-candidate input.
    core._validate_config(config)
    if config.schema_version == "tspm1.private.v1":
        a = audio
    elif config.schema_version == "tspm1.private.audio-half.v2":
        a = audio * 2.0
    else:
        raise RankBindingError("S2NL_RANK_VERSION_INVALID")
    tail = (slot_id,) if formation_index is None else (-formation_index, slot_id)
    return (max(a, visual), a + visual) + tail


def direct_scan(config, state, source, *, mode):
    memory._validate_config(config)
    memory._validate_state(config, state)
    require(mode in ("FAST_FORMATION", "FAST_PROBE", "B4_PROBE"))
    if mode == "FAST_FORMATION":
        memory._validate_input(config, source)
        native = source.tspm_exposure
    else:
        memory._validate_probe(config, source)
        native = source.tspm_probe
    core._validate_bound_source_time(state.tspm_state.fast_state, native, strictly_later=True)
    rows = []
    slots = state.b4_state.entries if mode == "B4_PROBE" else state.tspm_state.fast_state.slots
    step = state.generation + 1
    for slot in slots:
        if not slot.occupied:
            continue
        if mode == "FAST_FORMATION" and step-slot.last_selected_step >= config.tspm_config.fast_config.expire_after_exposures:
            continue
        av = slot.values if mode == "B4_PROBE" else slot.auditory_values + slot.visual_values
        require(len(av) == 336)
        audio = math.fsum(abs(x-y) for x, y in zip(source.auditory_values, av[:48], strict=True))/48
        visual = math.fsum(abs(x-y) for x, y in zip(source.visual_values, av[48:], strict=True))/288
        matched = (audio <= config.tspm_config.fast_config.auditory_match_threshold
                   and visual <= config.tspm_config.fast_config.visual_match_threshold)
        slot_digest = (memory._digest(dict(slot_id=slot.slot_id, formation_index=slot.formation_index,
            values_digest=memory._digest(list(slot.values)))) if mode == "B4_PROBE" else slot.digest())
        key = direct_key(config.tspm_config, audio, visual, slot.slot_id,
                         formation_index=slot.formation_index if mode == "B4_PROBE" else None)
        rows.append(RankRow(slot.slot_id, slot_digest, audio, visual, matched, key))
    chosen = min((r for r in rows if r.applicable), key=lambda r: r.key, default=None)
    payload = dict(config_digest=config.config_digest, state_digest=state.state_digest,
        source_digest=source.input_digest if mode == "FAST_FORMATION" else source.probe_digest,
        mode=mode, rows=tuple(rows), selected_slot_id=chosen.slot_id if chosen else None,
        selected_slot_digest=chosen.slot_digest if chosen else None,
        selected_key=chosen.key if chosen else None, term_count=len(rows)*336)
    from tools._s2nj_private_auditory_output_projection import canonical
    evidence = RankEvidence(**payload, evidence_digest="")
    evidence = RankEvidence(**payload, evidence_digest=memory._digest(evidence.payload()))
    require(evidence.term_count <= (MAX_B4_TERMS if mode == "B4_PROBE" else MAX_FAST_TERMS))
    require(len(canonical(asdict(evidence))) <= MAX_RANK_BYTES)
    return evidence


def verify_evidence(config, state, source, evidence):
    require(type(evidence) is RankEvidence)
    require(evidence == direct_scan(config, state, source, mode=evidence.mode))
    return evidence


def verify_probe(config, state, source, finding, b4_evidence, fast_evidence):
    b4 = verify_evidence(config, state, source, b4_evidence)
    fast = verify_evidence(config, state, source, fast_evidence)
    require(b4.mode == "B4_PROBE" and fast.mode == "FAST_PROBE")
    require(finding.prestate_digest == finding.poststate_digest == state.state_digest)
    require(finding.config_digest == config.config_digest and finding.probe_digest == source.probe_digest)
    require(finding.finding_digest == memory._digest(finding.payload_without_digest()))
    for evidence, selected, observations in (
        (b4, finding.b4_selected, finding.b4_observations),
        (fast, finding.fast_selected, finding.fast_observations),
    ):
        require((selected.slot_id if selected else None) == evidence.selected_slot_id)
        require((getattr(selected, "entry_digest", None) if evidence.mode == "B4_PROBE"
                 else getattr(selected, "slot_digest", None)) == evidence.selected_slot_digest)
        require(len(observations) == len(evidence.rows))
        for row, observed in zip(evidence.rows, observations, strict=True):
            require((row.slot_id, row.auditory_distance.hex(), row.visual_distance.hex(), row.applicable) ==
                    (observed.slot_id, observed.auditory_distance.hex(), observed.visual_distance.hex(), observed.mechanical_match))
    return True


def verify_fast_candidate(config, state, source, candidate, evidence):
    evidence = verify_evidence(config, state, source, evidence)
    require(evidence.mode == "FAST_FORMATION")
    core._validate_fast_state(config.tspm_config, candidate.poststate)
    require(candidate.candidate_digest == core._digest(candidate.payload_without_digest()))
    if evidence.selected_slot_id is not None:
        require(candidate.primary_event == "FAST_UPDATED" and candidate.selected_slot_id == evidence.selected_slot_id)
        previous = next(s for s in state.tspm_state.fast_state.slots if s.slot_id == evidence.selected_slot_id)
        actual = next(s for s in candidate.poststate.slots if s.slot_id == candidate.selected_slot_id)
        rate = config.tspm_config.fast_config.update_factor
        expected = tuple((1.0-rate)*x + rate*y for x, y in zip(
            previous.auditory_values + previous.visual_values, source.av_values, strict=True))
        require(tuple(v.hex() for v in actual.auditory_values+actual.visual_values) == tuple(v.hex() for v in expected))
        require(actual.support_count == min(config.tspm_config.fast_config.consolidate_after, previous.support_count+1))
        require(candidate.consolidation_eligible == (actual.support_count >= config.tspm_config.fast_config.consolidate_after))
        row = next(r for r in evidence.rows if r.slot_id == candidate.selected_slot_id)
        require((candidate.auditory_match_distance, candidate.visual_match_distance) == (row.auditory_distance, row.visual_distance))
    else:
        slots = state.tspm_state.fast_state.slots
        step = state.generation+1
        free = [s for s in slots if not s.occupied or step-s.last_selected_step >= config.tspm_config.fast_config.expire_after_exposures]
        selected = min(free, key=lambda s: s.slot_id) if free else min(slots, key=lambda s: (s.last_selected_step, s.slot_id))
        require(candidate.selected_slot_id == selected.slot_id)
        require(candidate.primary_event == ("FAST_CREATED" if free else "FAST_REPLACED"))
        actual = next(s for s in candidate.poststate.slots if s.slot_id == selected.slot_id)
        require(actual.auditory_values+actual.visual_values == source.av_values)
        require(actual.support_count == 1 and not candidate.consolidation_eligible)
    return True
