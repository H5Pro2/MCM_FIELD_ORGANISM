"""Pure experimental A-applicability rules; no corpus loading or memory calls."""

from dataclasses import asdict, dataclass, replace
import hashlib
import json
import math
import re
from statistics import mean
import struct


RULES = ("MEAN_L1_24", "ALL_BANDS_24")
THRESHOLD = 0.2
OBSERVED_BANDS = tuple(range(24))
MAX_OUTPUT_BYTES = 4_194_304
CASES_PER_RULE = 48
RELATIONS_PER_RULE = 528
DIFFERENCES_PER_RULE = 12_672
POSITIONS = tuple(("B4", i) for i in range(9)) + tuple(("FAST", i) for i in range(3))
STATUSES = ("A_RECENT_APPLICABLE", "A_RECENT_INTERNAL_AMBIGUITY",
            "A_RECENT_INTERNAL_CONFLICT", "A_RECENT_ABSENT_VALID", "A_RECENT_NOT_APPLICABLE")
EXECUTION_DIGEST = "00a0f5d177d11702b6ac08056d08b0501f125cefa8f0c0f1e3b651b894c67ae2"
MATERIALIZATION_DIGEST = "b335416ea03284e59c2eda83586d19081eaeef4885644e2c12ff97e2ab6ad236"


class ComparisonError(ValueError):
    pass


def require(condition, code):
    if not condition:
        raise ComparisonError(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def payload(value):
    return {k: v for k, v in asdict(value).items() if k != "digest"}


def sealed(value):
    return replace(value, digest=digest(payload(value)))


def check_digest(value):
    require(value.digest == digest(payload(value)), "DIGEST_INVALID")


def valid_digest(value):
    return type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def identifier(value):
    return type(value) is str and re.fullmatch(r"[a-z][a-z0-9-]{0,95}", value) is not None


def check_values(values, count):
    require(type(values) is tuple and len(values) == count, "VALUE_SHAPE_INVALID")
    require(all(type(v) is float and math.isfinite(v) and 0.0 <= v <= 1.0
                for v in values), "VALUE_DOMAIN_INVALID")


@dataclass(frozen=True, slots=True)
class Source48:
    source_id: str
    root_digest: str
    profile_digest: str
    parent_digest: str
    clock_id: str
    start_tick: int
    end_tick: int
    values: tuple[float, ...]
    values_digest: str
    digest: str = ""


@dataclass(frozen=True, slots=True)
class Cue24:
    source_id: str
    root_digest: str
    profile_digest: str
    parent_digest: str
    clock_id: str
    start_tick: int
    end_tick: int
    values: tuple[float, ...]
    digest: str = ""


def check_source(source, count):
    require(type(source) is (Source48 if count == 48 else Cue24), "SOURCE_TYPE_INVALID")
    check_digest(source)
    require(identifier(source.source_id) and identifier(source.clock_id), "SOURCE_ID_INVALID")
    require(all(valid_digest(v) for v in (source.root_digest, source.profile_digest,
                                         source.parent_digest)), "SOURCE_BINDING_INVALID")
    require(type(source.start_tick) is int and type(source.end_tick) is int
            and 0 <= source.start_tick < source.end_tick, "SOURCE_TIME_INVALID")
    check_values(source.values, count)
    if count == 48:
        require(source.values_digest == digest(source.values), "VALUES_DIGEST_INVALID")


def project_cue(source):
    check_source(source, 48)
    return sealed(Cue24(source.source_id, source.root_digest, source.profile_digest,
                        source.digest, source.clock_id, source.start_tick, source.end_tick,
                        source.values[:24]))


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    panel_id: str
    root_digest: str
    cue: Cue24
    b4: tuple[Source48 | None, ...]
    fast: tuple[Source48 | None, ...]
    digest: str = ""


def validate_case(case):
    require(type(case) is Case, "CASE_TYPE_INVALID")
    check_digest(case)
    require(identifier(case.case_id) and identifier(case.panel_id), "CASE_ID_INVALID")
    check_source(case.cue, 24)
    require(valid_digest(case.root_digest) and case.root_digest == case.cue.root_digest,
            "ROOT_BINDING_INVALID")
    seen = {case.cue.source_id: case.cue.parent_digest}
    for bank, capacity in ((case.b4, 9), (case.fast, 3)):
        require(type(bank) is tuple and len(bank) == capacity, "BANK_SHAPE_INVALID")
        for source in bank:
            if source is None:
                continue
            check_source(source, 48)
            require(source.root_digest == case.root_digest
                    and source.profile_digest == case.cue.profile_digest
                    and source.clock_id == case.cue.clock_id, "SOURCE_BINDING_INVALID")
            require(source.end_tick <= case.cue.start_tick, "SOURCE_NOT_PRECEDING_CUE")
            require(source.source_id != case.cue.source_id, "CUE_USED_AS_REFERENCE")
            require(source.source_id not in seen or seen[source.source_id] == source.digest,
                    "CONTRADICTORY_SOURCE_ID")
            seen[source.source_id] = source.digest


@dataclass(frozen=True, slots=True)
class Relation:
    bank: str
    position: int
    source_id: str
    source_digest: str
    terms: tuple[float, ...]
    mean_distance: float
    maximum_distance: float
    statistic: float
    reserve: float
    matched: bool
    digest: str = ""


@dataclass(frozen=True, slots=True)
class Decision:
    status: str
    source_ids: tuple[str, ...]
    common_values_digest: str | None


@dataclass(frozen=True, slots=True)
class CaseResult:
    case_id: str
    rule: str
    input_digest: str
    visited_positions: tuple[tuple[str, int], ...]
    rows: tuple[Relation, ...]
    b4_matches: tuple[int, ...]
    fast_matches: tuple[int, ...]
    decision: Decision
    equality_terms: int
    band_differences: int
    prestate_digest: str
    poststate_digest: str
    digest: str = ""


def _resolve(case, b4, fast):
    if len(b4) > 1 or len(fast) > 1:
        return Decision("A_RECENT_INTERNAL_AMBIGUITY", (), None), 0
    candidates = tuple(bank[hits[0]] for bank, hits in ((case.b4, b4), (case.fast, fast)) if hits)
    if len(candidates) == 2:
        left, right = candidates
        equal_terms = tuple(a == b for a, b in zip(left.values, right.values, strict=True))
        if left.values_digest != right.values_digest or not all(equal_terms):
            return Decision("A_RECENT_INTERNAL_CONFLICT", (), None), 48
        return Decision("A_RECENT_APPLICABLE", tuple(s.source_id for s in candidates),
                        left.values_digest), 48
    if candidates:
        source = candidates[0]
        return Decision("A_RECENT_APPLICABLE", (source.source_id,), source.values_digest), 0
    empty = all(source is None for source in case.b4 + case.fast)
    return Decision("A_RECENT_ABSENT_VALID" if empty else "A_RECENT_NOT_APPLICABLE", (), None), 0


def compare_case(case, rule):
    validate_case(case)
    require(rule in RULES, "RULE_INVALID")
    before = digest(payload(case))
    rows = []
    hits = {"B4": [], "FAST": []}
    for bank_name, bank in (("B4", case.b4), ("FAST", case.fast)):
        for position, source in enumerate(bank):
            if source is None:
                continue
            terms = tuple(abs(source.values[i] - case.cue.values[i]) for i in OBSERVED_BANDS)
            # Correctly rounded arithmetic mean avoids a boundary overshoot from sum/24.
            average, maximum = mean(terms), max(terms)
            statistic = average if rule == RULES[0] else maximum
            matched = statistic <= THRESHOLD
            rows.append(sealed(Relation(bank_name, position, source.source_id, source.digest,
                                        terms, average, maximum, statistic, THRESHOLD - statistic, matched)))
            if matched:
                hits[bank_name].append(position)
    b4, fast = tuple(hits["B4"]), tuple(hits["FAST"])
    decision, equality = _resolve(case, b4, fast)
    after = digest(payload(case))
    require(before == after, "INPUT_MUTATED")
    result = sealed(CaseResult(case.case_id, rule, case.digest, POSITIONS, tuple(rows),
                               b4, fast, decision, equality, len(rows) * 24, before, after))
    require(len(canonical(asdict(result))) <= MAX_OUTPUT_BYTES, "OUTPUT_TOO_LARGE")
    return result


def verify_case(case, result, expected_digest):
    """Verify a sealed trace without expectations or another distance calculation."""
    validate_case(case)
    require(type(result) is CaseResult, "RESULT_TYPE_INVALID")
    check_digest(result)
    require(valid_digest(expected_digest) and result.digest == expected_digest,
            "RESULT_PARENT_BINDING_INVALID")
    require(result.case_id == case.case_id and result.rule in RULES
            and result.input_digest == case.digest, "RESULT_BINDING_INVALID")
    require(result.prestate_digest == result.poststate_digest == case.digest, "READ_ONLY_INVALID")
    require(type(result.rows) is tuple and result.visited_positions == POSITIONS, "SCAN_INCOMPLETE")
    expected = tuple((name, i, s) for name, bank in (("B4", case.b4), ("FAST", case.fast))
                     for i, s in enumerate(bank) if s is not None)
    require(len(expected) == len(result.rows), "RELATION_COUNT_INVALID")
    for row, (name, i, source) in zip(result.rows, expected, strict=True):
        require(type(row) is Relation, "RELATION_TYPE_INVALID")
        check_digest(row)
        require((row.bank, row.position, row.source_id, row.source_digest)
                == (name, i, source.source_id, source.digest), "RELATION_BINDING_INVALID")
        check_values(row.terms, 24)
        require(row.mean_distance == mean(row.terms) and row.maximum_distance == max(row.terms),
                "REDUCTION_INVALID")
        statistic = row.mean_distance if result.rule == RULES[0] else row.maximum_distance
        require(row.statistic == statistic and row.reserve == THRESHOLD - statistic
                and type(row.matched) is bool and row.matched == (statistic <= THRESHOLD), "MATCH_INVALID")
    require(result.b4_matches == tuple(r.position for r in result.rows if r.bank == "B4" and r.matched)
            and result.fast_matches == tuple(r.position for r in result.rows if r.bank == "FAST" and r.matched),
            "HIT_SET_INVALID")
    require(result.band_differences == len(result.rows) * 24
            and result.equality_terms == (48 if len(result.b4_matches) == len(result.fast_matches) == 1 else 0),
            "COUNTERS_INVALID")
    require(type(result.decision) is Decision and result.decision.status in STATUSES, "STATUS_INVALID")
    require(type(result.decision.source_ids) is tuple, "PROVENANCE_INVALID")
    present = result.decision.status == "A_RECENT_APPLICABLE"
    require(bool(result.decision.source_ids) == present
            and (valid_digest(result.decision.common_values_digest) if present
                 else result.decision.common_values_digest is None), "DECISION_FORM_INVALID")
    from tools._s2nc_private_decision_baseline import decide
    expected, equality_terms = decide(case, result.b4_matches, result.fast_matches)
    require(result.decision == expected and result.equality_terms == equality_terms,
            "DECISION_TABLE_DIFFERS")
    require(len(canonical(asdict(result))) <= MAX_OUTPUT_BYTES, "OUTPUT_TOO_LARGE")
    return "TECHNICALLY_VALID"


def encode_complete_comparison(results, baseline_decisions, evaluation):
    require(type(results) is tuple and len(results) == 96, "BATCH_COUNT_INVALID")
    require(type(baseline_decisions) is tuple and len(baseline_decisions) == 96, "BASELINE_COUNT_INVALID")
    for rule in RULES:
        arm = tuple(r for r in results if r.rule == rule)
        require(len(arm) == CASES_PER_RULE and len({r.case_id for r in arm}) == CASES_PER_RULE,
                "ARM_CASES_INVALID")
        require(sum(len(r.rows) for r in arm) == RELATIONS_PER_RULE
                and sum(r.band_differences for r in arm) == DIFFERENCES_PER_RULE
                and sum(len(r.visited_positions) for r in arm) == 576
                and sum(r.equality_terms for r in arm) <= 2304, "BATCH_BUDGET_INVALID")
    require(tuple(r.case_id for r in results if r.rule == RULES[0])
            == tuple(r.case_id for r in results if r.rule == RULES[1]), "ARM_ORDER_INVALID")
    for result, baseline in zip(results, baseline_decisions, strict=True):
        check_digest(result)
        require(result.decision == baseline, "BASELINE_DIFFERS")
    data = canonical({"results": [asdict(r) for r in results],
                      "baseline_decisions": [asdict(d) for d in baseline_decisions],
                      "evaluation": evaluation})
    require(len(data) <= MAX_OUTPUT_BYTES, "OUTPUT_TOO_LARGE")
    return data


def bind_materialized_sources(record, expected_digest=MATERIALIZATION_DIGEST):
    """Accept an already verified materialization root; perform no analysis."""
    require(type(record) is dict and valid_digest(expected_digest)
            and record.get("record_digest") == expected_digest
            and digest({k: v for k, v in record.items() if k != "record_digest"}) == expected_digest,
            "MATERIALIZATION_BINDING_INVALID")
    require(record.get("technical_status") == "RECEPTOR_MATERIALIZATION_COMPLETE"
            and record.get("failure") is None and record.get("sources_unchanged") is True,
            "MATERIALIZATION_INCOMPLETE")
    require(record.get("execution_digest") == EXECUTION_DIGEST, "MATERIALIZATION_PLAN_INVALID")
    profile = record["receptor_profile"]
    require(profile["profile_digest"] == digest({k: v for k, v in profile.items() if k != "profile_digest"}),
            "PROFILE_DIGEST_INVALID")
    require(profile["config"] == dict(sample_rate=48000, window_size=4800, hop_size=480,
                                       min_frequency=50.0, max_frequency=18000.0, band_count=48),
            "PROFILE_INVALID")
    require(type(record["states"]) is list and len(record["states"]) == 23,
            "MATERIALIZED_COUNT_INVALID")
    sources = []
    for ordinal, state in enumerate(record["states"], 1):
        parent = state["materialized_state_digest"]
        require(parent == digest({k: v for k, v in state.items() if k != "materialized_state_digest"}),
                "MATERIALIZED_STATE_INVALID")
        require(state["source_id"] == f"s{ordinal:03d}" and state["ordinal"] == ordinal
                and state["execution_digest"] == EXECUTION_DIGEST
                and state["profile_digest"] == profile["profile_digest"], "MATERIALIZED_SOURCE_INVALID")
        values = tuple(state["values"])
        check_values(values, 48)
        require(state["values_digest"] == digest(values)
                and state["values_f64le_sha256"] == hashlib.sha256(struct.pack("<48d", *values)).hexdigest(),
                "MATERIALIZED_VALUES_INVALID")
        source = sealed(Source48(state["source_id"], expected_digest, profile["profile_digest"],
                                 parent, state["clock_id"], state["window_start_sample"],
                                 state["window_end_sample"], values, state["values_digest"]))
        check_source(source, 48)
        sources.append(source)
    return tuple(sources)


def bind_fixed_cases(execution_plan, sources):
    """Use exactly the sealed panel positions, empty slots and case order."""
    require(type(execution_plan) is dict and execution_plan.get("execution_digest") == EXECUTION_DIGEST
            and digest({k: v for k, v in execution_plan.items() if k != "execution_digest"}) == EXECUTION_DIGEST,
            "EXECUTION_PLAN_INVALID")
    require(type(sources) is tuple and len(sources) == 23, "SOURCE_INVENTORY_INVALID")
    for n, source in enumerate(sources, 1):
        check_source(source, 48)
        require(source.source_id == f"s{n:03d}" and source.clock_id == "s2nc-source-sample-clock"
                and (source.start_tick, source.end_tick) == ((n - 1) * 4800, n * 4800),
                "INVENTORY_TIME_INVALID")
    source_map = {source.source_id: source for source in sources}
    panels = {panel["panel_id"]: panel for panel in execution_plan["panels"]}
    cases = []
    for spec in execution_plan["cases"]:
        panel = panels[spec["panel_id"]]
        b4, fast = (tuple(None if entry["source_id"] is None else source_map[entry["source_id"]]
                          for entry in panel[bank]) for bank in ("b4", "fast"))
        cue = project_cue(source_map[spec["cue_source_id"]])
        case = sealed(Case(spec["case_id"], spec["panel_id"], cue.root_digest, cue, b4, fast))
        validate_case(case)
        cases.append(case)
    require(len(cases) == 48 and sum(s is not None for c in cases for s in c.b4 + c.fast) == 528,
            "FIXED_PANEL_BUDGET_INVALID")
    return tuple(cases)
