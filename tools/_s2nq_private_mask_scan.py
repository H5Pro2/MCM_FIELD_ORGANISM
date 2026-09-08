"""Two closed auditory views; immutable, read-only, no hidden cue values."""
from dataclasses import asdict, dataclass, replace
import math
import re

from tools import _s2nl_private_half_profile_binding as profile
from tools import _s2ne_private_auditory_transfer as ne

memory, canonical, digest = profile.memory, ne.kz.canonical_bytes, ne.kz.digest
VIEWS = ("CONTIGUOUS_24", "DISTRIBUTED_24")
INDICES = (tuple(range(24)), (0,3,4,7,8,11,12,15,16,19,20,23,24,27,28,31,32,35,36,39,40,43,44,47))
ROLES = ("A_RECENT_B4", "A_RECENT_FAST", "B_STABLE_AUDITORY")
SCHEMA = "s2nq.masked-auditory.v1"
MAX_ARM_BYTES = 32768


class S2NQError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NQError(code)


def hash_form(v):
    return type(v) is str and re.fullmatch(r"[0-9a-f]{64}", v) is not None


@dataclass(frozen=True, slots=True)
class BandPlan:
    view: str
    observed: tuple[int, ...]
    complement: tuple[int, ...]
    schema: str = SCHEMA

    def __post_init__(self):
        require(self.schema == SCHEMA and self.view in VIEWS, "MASK_BINDING_INVALID")
        require(type(self.observed) is tuple and self.observed == INDICES[VIEWS.index(self.view)]
                and all(type(i) is int for i in self.observed), "MASK_BINDING_INVALID")
        require(type(self.complement) is tuple and self.complement == tuple(i for i in range(48) if i not in self.observed)
                and all(type(i) is int for i in self.complement), "COMPLEMENT_INVALID")

    @property
    def plan_digest(self):
        return digest(asdict(self))


def plan(view):
    require(view in VIEWS, "MASK_BINDING_INVALID")
    indices = INDICES[VIEWS.index(view)]
    return BandPlan(view, indices, tuple(i for i in range(48) if i not in indices))


@dataclass(frozen=True, slots=True)
class Cue:
    band_plan: BandPlan
    values: tuple[float, ...]
    config_digest: str
    profile_digest: str
    pcm_digest: str
    parent_digest: str
    parent_values_digest: str
    clock_id: str
    start: int
    end: int
    schema: str = SCHEMA

    def __post_init__(self):
        require(type(self.band_plan) is BandPlan, "MASK_BINDING_INVALID")
        self.band_plan.__post_init__()
        require(self.schema == SCHEMA and self.profile_digest == profile.half.PROFILE_DIGEST, "PROFILE_INVALID")
        require(type(self.values) is tuple and len(self.values) == 24
                and all(type(x) is float and math.isfinite(x) and 0 <= x <= 1 for x in self.values), "VALUE_DOMAIN_INVALID")
        require(all(hash_form(h) for h in (self.config_digest, self.pcm_digest, self.parent_digest,
                                          self.parent_values_digest)), "SOURCE_BINDING_INVALID")
        require(self.clock_id == "audio.sample" and type(self.start) is type(self.end) is int
                and self.start >= 0 and self.start % 480 == 0 and self.end == self.start + 4800, "CUE_TIME_INVALID")

    @property
    def cue_digest(self):
        return digest(asdict(self))


def bind_cue(projection, pcm_digest, config, view):
    profile.half.validate_projection(projection)
    bp = plan(view)
    return Cue(bp, tuple(projection.values[i] for i in bp.observed), config.config_digest,
        projection.profile_digest, pcm_digest, projection.projection_digest,
        digest(list(projection.values)), projection.clock_id, projection.window_start_tick, projection.window_end_tick)


def validate_inputs(config, state, cue):
    require(type(cue) is Cue, "CUE_TYPE_INVALID")
    cue.__post_init__()
    require(config == profile.build_config() and cue.config_digest == config.config_digest, "PROFILE_INVALID")
    try:
        memory._validate_config(config)
        memory._validate_state(config, state)
    except memory.S2JWCoordinatorError as exc:
        raise S2NQError("STATE_BINDING_INVALID") from exc
    if state.generation:
        fast = state.tspm_state.fast_state
        require(cue.clock_id == fast.auditory_source_clock_id and cue.start >= fast.auditory_last_end_tick
                and cue.end > fast.auditory_last_end_tick, "CUE_TIME_INVALID")


@dataclass(frozen=True, slots=True)
class Row:
    bank: str
    slot_id: str
    slot_digest: str
    eligible: bool
    support: int | None
    candidate_digest: str | None
    terms: tuple[float, ...]
    statistic: float | None
    threshold: float
    matched: bool


@dataclass(frozen=True, slots=True)
class Hypothesis:
    area: str
    provenance: tuple[str, ...]
    candidate_digest: str
    indices: tuple[int, ...]
    values: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class Result:
    implementation: str
    view: str
    config_digest: str
    cue_digest: str
    prestate_digest: str
    poststate_digest: str
    rows: tuple[Row, ...]
    a_status: str
    b_status: str
    decision: str
    hypothesis: Hypothesis | None
    comparisons: int
    equality_comparisons: int
    result_digest: str = ""
    schema: str = SCHEMA

    def payload(self):
        p = asdict(self)
        del p["result_digest"]
        return p


def finish(**kwargs):
    result = Result(**kwargs)
    result = replace(result, result_digest=digest(result.payload()))
    require(len(result.rows) == 20 and result.comparisons <= 480
            and result.equality_comparisons in (0, 48), "SCAN_BUDGET_INVALID")
    require(len(canonical(asdict(result))) <= MAX_ARM_BYTES, "ARM_SIZE_EXCEEDED")
    return result


def retrieve(*, config, state, cue):
    validate_inputs(config, state, cue)
    before = digest(asdict(state))
    banks = (state.b4_state.entries, state.tspm_state.fast_state.slots, state.tspm_state.auditory_ppb1_state.slots)
    rows, hits, eligible_counts = [], [], []
    for b, slots in enumerate(banks):
        matches, count = [], 0
        for slot in slots:
            eligible = slot.occupied and (b != 2 or slot.support_count >= config.profile.profile.auditory_config.stable_after)
            support = slot.support_count if b and slot.occupied else None
            h = digest(ne.comparison._canonical(slot)) if b == 0 else slot.digest() if b == 1 else digest(slot.canonical_payload())
            values = (slot.values[:48] if b == 0 else slot.auditory_values if b == 1 else slot.prototype_values) if eligible else None
            terms = tuple(abs(values[i] - x) for i, x in zip(cue.band_plan.observed, cue.values, strict=True)) if eligible else ()
            statistic = (max(terms) if b < 2 else sum(terms)/24) if terms else None
            threshold = 0.1 if b < 2 else 0.01
            matched = statistic is not None and statistic <= threshold
            vh = digest(list(values)) if eligible else None
            rows.append(Row(ROLES[b], slot.slot_id, h, eligible, support, vh, terms, statistic, threshold, matched))
            count += int(eligible)
            if matched:
                matches.append((h, values, vh))
        hits.append(matches)
        eligible_counts.append(count)
    a, b = None, None
    equality = 0
    if len(hits[0]) > 1 or len(hits[1]) > 1:
        ast = "A_RECENT_INTERNAL_AMBIGUITY"
    elif hits[0] and hits[1]:
        equality = 48
        if hits[0][0][1] == hits[1][0][1] and hits[0][0][2] == hits[1][0][2]:
            ast, a = "A_RECENT_APPLICABLE", hits[0] + hits[1]
        else:
            ast = "A_RECENT_INTERNAL_CONFLICT"
    elif hits[0] or hits[1]:
        ast, a = "A_RECENT_APPLICABLE", hits[0] + hits[1]
    else:
        ast = "A_RECENT_ABSENT_VALID" if not any(eligible_counts[:2]) else "A_RECENT_NOT_APPLICABLE"
    if len(hits[2]) > 1:
        bst = "B_STABLE_AUDITORY_INTERNAL_AMBIGUITY"
    elif hits[2]:
        bst, b = "B_STABLE_AUDITORY_APPLICABLE", hits[2]
    else:
        bst = "B_STABLE_AUDITORY_ABSENT_VALID" if not eligible_counts[2] else "B_STABLE_AUDITORY_NOT_APPLICABLE"
    if ast.endswith("INTERNAL_AMBIGUITY") or bst.endswith("INTERNAL_AMBIGUITY"):
        decision = "ABSTAIN_INTERNAL_AMBIGUITY"
    elif ast.endswith("INTERNAL_CONFLICT"):
        decision = "ABSTAIN_INTERNAL_CONFLICT"
    elif a and b:
        decision = "ABSTAIN_AMBIGUOUS_CONTEXT"
    elif a or b:
        decision = "ADMIT_SINGLE_CONTEXT"
    else:
        decision = "ABSTAIN_NO_CONTEXT" if ast.endswith("ABSENT_VALID") and bst.endswith("ABSENT_VALID") else "ABSTAIN_NO_APPLICABLE_CONTEXT"
    hypothesis = None
    if decision == "ADMIT_SINGLE_CONTEXT":
        selected = a or b
        hypothesis = Hypothesis("A_RECENT" if a else "B_STABLE_AUDITORY", tuple(x[0] for x in selected),
            selected[0][2], cue.band_plan.complement, tuple(selected[0][1][i] for i in cue.band_plan.complement))
    require(before == digest(asdict(state)), "STATE_MUTATED")
    return finish(implementation="PRIMARY", view=cue.band_plan.view, config_digest=config.config_digest,
        cue_digest=cue.cue_digest, prestate_digest=state.state_digest, poststate_digest=state.state_digest,
        rows=tuple(rows), a_status=ast, b_status=bst, decision=decision, hypothesis=hypothesis,
        comparisons=sum(len(r.terms) for r in rows), equality_comparisons=equality)


def decode_result(p):
    try:
        rows = tuple(Row(**{**r, "terms": tuple(r["terms"])}) for r in p["rows"])
        h = p["hypothesis"]
        hypothesis = None if h is None else Hypothesis(**{**h, **{k: tuple(h[k]) for k in ("provenance", "indices", "values")}})
        result = Result(**{**p, "rows": rows, "hypothesis": hypothesis})
        require(result.schema == SCHEMA and result.result_digest == digest(result.payload()), "RESULT_DIGEST_INVALID")
        require(canonical(asdict(result)) == canonical(p), "RESULT_FORM_INVALID")
        return result
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, S2NQError):
            raise
        raise S2NQError("RESULT_FORM_INVALID") from exc
