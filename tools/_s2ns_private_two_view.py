"""Private complementary evidence, generation join, and admission only."""
from dataclasses import asdict, dataclass, replace
import math
import re

from tools import _s2nq_private_mask_scan as existing

profile, memory = existing.profile, existing.memory
canonical, digest = existing.canonical, existing.digest
MAIN_GATE = False
SCHEMA = "s2ns.two-view-admission.v1"
VIEWS = ("LOWER_24", "UPPER_24")
INDICES = (tuple(range(24)), tuple(range(24, 48)))
BANKS = existing.ROLES
MAX_SCAN_BYTES, MAX_RESULT_BYTES = 32768, 49152
MAX_SHARED_BYTES, MAX_STATE_BYTES, MAX_TOTAL_BYTES = 32768, 98304, 4194304


class S2NSError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def require(ok, code):
    if not ok:
        raise S2NSError(code)


def identifier(x):
    return type(x) is str and re.fullmatch(r"[a-zA-Z0-9_.-]{1,64}", x) is not None


def hashes(*items):
    return all(existing.hash_form(x) for x in items)


@dataclass(frozen=True, slots=True)
class Endpoint:
    source_id: str
    source_digest: str
    pcm_digest: str
    raw_state_digest: str
    projection_digest: str
    profile_digest: str
    config_digest: str
    clock_id: str
    start: int
    end: int

    def __post_init__(self):
        require(identifier(self.source_id) and hashes(self.source_digest, self.pcm_digest,
            self.raw_state_digest, self.projection_digest, self.config_digest), "SOURCE_BINDING_INVALID")
        require(self.profile_digest == profile.half.PROFILE_DIGEST, "PROFILE_INVALID")
        require(self.clock_id == "audio.sample" and type(self.start) is type(self.end) is int
            and 0 <= self.start < self.end <= 10**15 and self.start % 480 == 0
            and self.end-self.start == 4800, "CUE_TIME_INVALID")


@dataclass(frozen=True, slots=True)
class View:
    endpoint: Endpoint
    name: str
    indices: tuple[int, ...]
    values: tuple[float, ...]
    schema: str = SCHEMA

    def __post_init__(self):
        require(type(self.endpoint) is Endpoint, "SOURCE_BINDING_INVALID")
        self.endpoint.__post_init__()
        require(self.schema == SCHEMA and self.name in VIEWS and type(self.indices) is tuple
            and self.indices == INDICES[VIEWS.index(self.name)]
            and all(type(i) is int for i in self.indices), "VIEW_BINDING_INVALID")
        require(type(self.values) is tuple and len(self.values) == 24
            and all(type(x) is float and math.isfinite(x) and 0 <= x <= 1 for x in self.values),
            "VALUE_DOMAIN_INVALID")

    @property
    def view_digest(self):
        return digest(asdict(self))


def bind_views(*, projection, config, source_id, source_digest, pcm_digest):
    """Only partition an already validated NJ endpoint; never analyze or project."""
    try:
        profile.half.validate_projection(projection)
    except profile.half.S2NJProjectionError as exc:
        raise S2NSError("PROJECTION_BINDING_INVALID") from exc
    require(config == profile.build_config(), "PROFILE_INVALID")
    endpoint = Endpoint(source_id, source_digest, pcm_digest, projection.source_state_digest,
        projection.projection_digest, projection.profile_digest, config.config_digest,
        projection.clock_id, projection.window_start_tick, projection.window_end_tick)
    return tuple(View(endpoint, name, indices, tuple(projection.values[i] for i in indices))
                 for name, indices in zip(VIEWS, INDICES, strict=True))


@dataclass(frozen=True, slots=True)
class Generation:
    """Birth binding supplied by the separately verified formation-chain adapter."""
    history_id: str
    bank: str
    slot_id: str
    event_id: str
    ordinal: int
    transition: str
    prestate_digest: str
    input_digest: str
    created_slot_digest: str
    transition_digest: str

    def __post_init__(self):
        require(all(identifier(x) for x in (self.history_id, self.slot_id, self.event_id))
            and self.bank in BANKS and self.transition in ("CREATED", "REPLACED")
            and type(self.ordinal) is int and 1 <= self.ordinal <= 31
            and hashes(self.prestate_digest, self.input_digest, self.created_slot_digest,
                       self.transition_digest), "GENERATION_BINDING_INVALID")

    @property
    def generation_digest(self):
        return digest(asdict(self))


@dataclass(frozen=True, slots=True)
class SlotBinding:
    bank: str
    slot_id: str
    slot_digest: str
    values_digest: str | None
    generation: Generation | None


@dataclass(frozen=True, slots=True)
class Inventory:
    history_id: str
    config_digest: str
    profile_digest: str
    state_digest: str
    verified_chain_digest: str
    slots: tuple[SlotBinding, ...]
    schema: str = SCHEMA

    @property
    def inventory_digest(self):
        return digest(asdict(self))


def slot_items(state):
    banks = (state.b4_state.entries, state.tspm_state.fast_state.slots,
             state.tspm_state.auditory_ppb1_state.slots)
    require(tuple(map(len, banks)) == (9, 3, 8), "BANK_SHAPE_INVALID")
    return tuple((b, slot) for b, slots in enumerate(banks) for slot in slots)


def slot_values(bank, slot):
    if not slot.occupied:
        return None
    return slot.values[:48] if bank == 0 else slot.auditory_values if bank == 1 else slot.prototype_values


def slot_hash(bank, slot):
    return (digest(existing.ne.comparison._canonical(slot)) if bank == 0
            else slot.digest() if bank == 1 else digest(slot.canonical_payload()))


def validate_inventory(config, state, inventory):
    require(config == profile.build_config(), "PROFILE_INVALID")
    try:
        memory._validate_config(config)
        memory._validate_state(config, state)
    except (memory.S2JWCoordinatorError, memory.tspm1.TSPM1Error) as exc:
        raise S2NSError("STATE_BINDING_INVALID") from exc
    require(type(inventory) is Inventory and inventory.schema == SCHEMA
        and identifier(inventory.history_id) and inventory.config_digest == config.config_digest
        and inventory.profile_digest == profile.half.PROFILE_DIGEST
        and inventory.state_digest == state.state_digest and hashes(inventory.verified_chain_digest)
        and type(inventory.slots) is tuple and len(inventory.slots) == 20, "INVENTORY_BINDING_INVALID")
    require(len(canonical(asdict(state))) <= MAX_STATE_BYTES, "STATE_SIZE_EXCEEDED")
    for (b, slot), bound in zip(slot_items(state), inventory.slots, strict=True):
        require(type(bound) is SlotBinding and (bound.bank, bound.slot_id, bound.slot_digest)
            == (BANKS[b], slot.slot_id, slot_hash(b, slot)), "SLOT_BINDING_INVALID")
        values = slot_values(b, slot)
        require(bound.values_digest == (None if values is None else digest(list(values))), "SLOT_VALUES_INVALID")
        if slot.occupied:
            require(type(bound.generation) is Generation, "GENERATION_BINDING_INVALID")
            bound.generation.__post_init__()
            require((bound.generation.history_id, bound.generation.bank, bound.generation.slot_id)
                == (inventory.history_id, bound.bank, bound.slot_id), "GENERATION_BINDING_INVALID")
        else:
            require(bound.generation is None, "FREE_SLOT_GENERATION_INVALID")
    require(len(canonical(asdict(inventory))) <= MAX_SHARED_BYTES, "INVENTORY_SIZE_EXCEEDED")


def validate_view(config, state, view):
    require(type(view) is View, "VIEW_BINDING_INVALID")
    view.__post_init__()
    require(view.endpoint.config_digest == config.config_digest, "PROFILE_INVALID")
    if state.generation:
        fast = state.tspm_state.fast_state
        require(view.endpoint.clock_id == fast.auditory_source_clock_id
            and view.endpoint.start >= fast.auditory_last_end_tick
            and view.endpoint.end > fast.auditory_last_end_tick, "CUE_TIME_INVALID")


def validate_shared(inventory, lower, upper):
    require(type(inventory) is Inventory and all(v is None or type(v) is View for v in (lower, upper)),
            "SHARED_BINDING_INVALID")
    payload = dict(inventory=asdict(inventory), views=[None if v is None else asdict(v) for v in (lower, upper)])
    require(len(canonical(payload)) <= MAX_SHARED_BYTES, "SHARED_SIZE_EXCEEDED")


@dataclass(frozen=True, slots=True)
class Row:
    index: int
    generation_digest: str | None
    eligible: bool
    terms: tuple[float, ...]
    statistic: float | None
    threshold: float
    matched: bool


@dataclass(frozen=True, slots=True)
class Scan:
    implementation: str
    view: str
    view_digest: str
    endpoint_digest: str
    inventory_digest: str
    prestate_digest: str
    poststate_digest: str
    rows: tuple[Row, ...]
    comparisons: int
    scan_digest: str = ""

    def payload(self):
        return {k: v for k, v in asdict(self).items() if k != "scan_digest"}


def seal_scan(**kwargs):
    scan = Scan(**kwargs)
    require(len(scan.rows) == 20 and scan.comparisons <= 480, "SCAN_BUDGET_INVALID")
    scan = replace(scan, scan_digest=digest(scan.payload()))
    require(len(canonical(asdict(scan))) <= MAX_SCAN_BYTES, "SCAN_SIZE_EXCEEDED")
    return scan


def scan_view(*, config, state, inventory, view):
    validate_inventory(config, state, inventory)
    validate_view(config, state, view)
    before = digest(asdict(state))
    rows = []
    for index, (b, slot) in enumerate(slot_items(state)):
        eligible = slot.occupied and (b != 2 or slot.support_count >= config.profile.profile.auditory_config.stable_after)
        values = slot_values(b, slot) if eligible else None
        terms = tuple(abs(values[i]-v) for i, v in zip(view.indices, view.values, strict=True)) if eligible else ()
        stat = (max(terms) if b < 2 else sum(terms)/24) if terms else None
        threshold = 0.1 if b < 2 else 0.01
        g = inventory.slots[index].generation
        rows.append(Row(index, None if g is None else g.generation_digest, eligible, terms, stat,
            threshold, stat is not None and stat <= threshold))
    require(before == digest(asdict(state)), "STATE_MUTATED")
    return seal_scan(implementation="PRIMARY", view=view.name, view_digest=view.view_digest,
        endpoint_digest=digest(asdict(view.endpoint)), inventory_digest=inventory.inventory_digest,
        prestate_digest=state.state_digest, poststate_digest=state.state_digest, rows=tuple(rows),
        comparisons=sum(len(r.terms) for r in rows))


def validate_scan(scan, inventory, view):
    require(type(scan) is Scan and scan.implementation in ("PRIMARY", "DIRECT_BASELINE")
        and scan.scan_digest == digest(scan.payload()), "SCAN_DIGEST_INVALID")
    require((scan.view, scan.view_digest, scan.endpoint_digest, scan.inventory_digest,
             scan.prestate_digest, scan.poststate_digest) == (view.name, view.view_digest,
             digest(asdict(view.endpoint)), inventory.inventory_digest, inventory.state_digest,
             inventory.state_digest), "SCAN_BINDING_INVALID")
    require(type(scan.rows) is tuple and len(scan.rows) == 20, "SCAN_COMPLETENESS_INVALID")
    for index, (row, slot) in enumerate(zip(scan.rows, inventory.slots, strict=True)):
        require(type(row) is Row and row.index == index and type(row.eligible) is bool
            and type(row.matched) is bool and row.generation_digest ==
            (None if slot.generation is None else slot.generation.generation_digest), "SCAN_GENERATION_INVALID")
        require(type(row.terms) is tuple and len(row.terms) == (24 if row.eligible else 0)
            and all(type(t) is float and math.isfinite(t) and 0 <= t <= 1 for t in row.terms)
            and row.threshold == (0.1 if index < 12 else 0.01)
            and (not row.eligible or slot.generation is not None), "SCAN_ROW_INVALID")
        require((row.eligible and type(row.statistic) is float and math.isfinite(row.statistic)
                 and 0 <= row.statistic <= 1) or (not row.eligible and row.statistic is None), "SCAN_ROW_INVALID")
        require(row.matched == (row.statistic is not None and row.statistic <= row.threshold), "SCAN_ROW_INVALID")
    require(scan.comparisons == sum(len(r.terms) for r in scan.rows) <= 480
        and len(canonical(asdict(scan))) <= MAX_SCAN_BYTES, "SCAN_BUDGET_INVALID")


@dataclass(frozen=True, slots=True)
class Admission:
    arm: str
    a_status: str
    b_status: str
    decision: str
    area: str | None
    provenance: tuple[int, ...]
    matched_slots: tuple[int, ...]
    equality_comparisons: int


@dataclass(frozen=True, slots=True)
class _Area:
    status: str
    public_candidate_count: int


def resolve(arm, rows, state):
    hits = [[r.index for r in rows if r.matched and lo <= r.index < hi]
            for lo, hi in ((0, 9), (9, 12), (12, 20))]
    counts = [sum(r.eligible for r in rows[lo:hi]) for lo, hi in ((0, 9), (9, 12), (12, 20))]
    equality, selected = 0, []
    if len(hits[0]) > 1 or len(hits[1]) > 1:
        ast = "A_RECENT_INTERNAL_AMBIGUITY"
    elif hits[0] and hits[1]:
        values = [slot_values(*slot_items(state)[i]) for i in hits[0]+hits[1]]
        equality = 48
        # Evaluate all components, including those outside either single view.
        same = [x == y for x, y in zip(*values, strict=True)]
        if all(same) and digest(list(values[0])) == digest(list(values[1])):
            ast, selected = "A_RECENT_APPLICABLE", hits[0]+hits[1]
        else:
            ast = "A_RECENT_INTERNAL_CONFLICT"
    elif hits[0] or hits[1]:
        ast, selected = "A_RECENT_APPLICABLE", hits[0]+hits[1]
    else:
        ast = "A_RECENT_ABSENT_VALID" if not sum(counts[:2]) else "A_RECENT_NOT_APPLICABLE"
    bst = "B_STABLE_AUDITORY_" + ("INTERNAL_AMBIGUITY" if len(hits[2]) > 1 else
        "APPLICABLE" if hits[2] else "ABSENT_VALID" if not counts[2] else "NOT_APPLICABLE")
    decision, area = existing.ne.kz._decide(_Area(ast, int(bool(selected))), _Area(bst, int(len(hits[2]) == 1)))
    provenance = selected if area == "A_RECENT" else hits[2] if area else []
    return Admission(arm, ast, bst, decision, area, tuple(provenance),
        tuple(i for group in hits for i in group), equality)


def combine(*, config, state, inventory, lower, upper, lower_scan, upper_scan):
    validate_inventory(config, state, inventory)
    for view, scan, name in ((lower, lower_scan, VIEWS[0]), (upper, upper_scan, VIEWS[1])):
        require((view is None) == (scan is None), "MISSING_SCAN_INVALID")
        if view is not None:
            validate_view(config, state, view)
            require(view.name == name, "VIEW_BINDING_INVALID")
            validate_scan(scan, inventory, view)
    if lower is None or upper is None:
        return Admission("CONFIRMED", "NOT_EVALUATED", "NOT_EVALUATED",
            "ABSTAIN_INSUFFICIENT_EVIDENCE", None, (), (), 0)
    require(lower.endpoint == upper.endpoint, "ENDPOINT_MISMATCH")
    require(lower_scan.implementation == upper_scan.implementation, "IMPLEMENTATION_MISMATCH")
    rows = []
    for a, b in zip(lower_scan.rows, upper_scan.rows, strict=True):
        require((a.index, a.generation_digest, a.eligible) == (b.index, b.generation_digest, b.eligible),
            "GENERATION_JOIN_INVALID")
        rows.append(replace(a, matched=a.matched and b.matched))
    return resolve("CONFIRMED", tuple(rows), state)


@dataclass(frozen=True, slots=True)
class Result:
    implementation: str
    inventory_digest: str
    scans: tuple[Scan, ...]
    admissions: tuple[Admission, ...]
    band_differences: int
    equality_comparisons: int
    result_digest: str = ""
    schema: str = SCHEMA

    def payload(self):
        return {k: v for k, v in asdict(self).items() if k != "result_digest"}


def finish(implementation, inventory, scans, admissions):
    r = Result(implementation, inventory.inventory_digest, tuple(scans), tuple(admissions),
        sum(s.comparisons for s in scans), sum(a.equality_comparisons for a in admissions))
    require(len(scans) <= 2 and r.band_differences <= 960 and r.equality_comparisons <= 144,
        "RESULT_BUDGET_INVALID")
    r = replace(r, result_digest=digest(r.payload()))
    require(len(canonical(asdict(r))) <= MAX_RESULT_BYTES, "RESULT_SIZE_EXCEEDED")
    return r


def retrieve(*, config, state, inventory, lower, upper):
    scans, singles = [], []
    for view in (lower, upper):
        if view is not None:
            scan = scan_view(config=config, state=state, inventory=inventory, view=view)
            scans.append(scan)
            singles.append(resolve(view.name, scan.rows, state))
    joined = combine(config=config, state=state, inventory=inventory, lower=lower, upper=upper,
        lower_scan=next((s for s in scans if s.view == VIEWS[0]), None),
        upper_scan=next((s for s in scans if s.view == VIEWS[1]), None))
    validate_shared(inventory, lower, upper)
    return finish("PRIMARY", inventory, scans, singles+[joined])
