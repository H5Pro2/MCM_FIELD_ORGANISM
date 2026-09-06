"""Pure S2-ND binding; reuse S2-NC rules without its corpus-specific helpers."""

from dataclasses import asdict, dataclass
import hashlib
import struct

from tools import _s2nc_private_rule_comparison as c


@dataclass(frozen=True, slots=True)
class Roots:
    execution: str
    evaluation: str
    seal: str
    materialization: str
    profile: str
    verification: str


BOUND_ROOTS = Roots(
    "e29682fe7606f533c068b3a57c5f986a18934cea2b7c0ca977c0c538a6052f22",
    "6f0474cf98ab5cdfa6f3554914b4b0d34c59086198f19c81a11e64381873ecf6",
    "333f15e8ba0a69e50c12481503f089a348a367eec0c8bb2489cc9f184393b61a",
    "705f34e547916057e4aefbc52fcf2a7710958b013d4a9501a6ad628194f243d6",
    "3d9c7d8ca7a400c8bdfeb35cb8395015a5f48979614d303cd1dbab1972f3a855",
    "b794ab2a702ea21515b8d13ebbc9c88de5057eecafadbf95cda0ccecfb0dbcec",
)
PROFILE = dict(sample_rate=48000, window_size=4800, hop_size=480,
               min_frequency=50.0, max_frequency=18000.0, band_count=48)


@dataclass(frozen=True, slots=True)
class BoundInputs:
    roots: Roots
    sources: tuple[c.Source48, ...]
    cases: tuple[c.Case, ...]
    digest: str = ""


def check_root(value, key, expected):
    c.require(type(value) is dict and c.valid_digest(expected)
              and value.get(key) == expected
              and c.digest({k: v for k, v in value.items() if k != key}) == expected, "ND_ROOT_INVALID")


def _bind(execution, seal, record, verification, roots):
    c.require(type(roots) is Roots and all(c.valid_digest(v) for v in asdict(roots).values()), "ND_ROOT_FORM_INVALID")
    for obj, key, expected in ((execution, "execution_digest", roots.execution), (seal, "seal_digest", roots.seal),
                               (record, "record_digest", roots.materialization),
                               (verification, "verification_digest", roots.verification)):
        check_root(obj, key, expected)
    c.require(seal["status"] == "SOURCE_INVENTORY_AND_PANELS_PRESEALED"
              and seal["execution_digest"] == roots.execution and seal["evaluation_digest"] == roots.evaluation
              and seal["execution_file_sha256"] == hashlib.sha256(c.canonical(execution)).hexdigest(), "ND_SEAL_INVALID")
    c.require(record["technical_status"] == "RECEPTOR_MATERIALIZATION_COMPLETE" and record["failure"] is None
              and record["sources_unchanged"] is True and record["input_hashes"] == record["source_hashes_after"]
              and record["execution_digest"] == roots.execution and record["seal_digest"] == roots.seal,
              "ND_MATERIALIZATION_INVALID")
    c.require(all(record["input_hashes"][p] == h for p, h in seal["source_hashes_before"].items())
              and seal["source_hashes_before"] == seal["source_hashes_after"], "ND_SOURCE_HASH_INVALID")
    c.require(verification["verification_status"] == "MATERIALIZATION_EVIDENCE_VALID"
              and verification["record_digest"] == roots.materialization and verification["run_id"] == record["run_id"]
              and verification["result_file_sha256"] == hashlib.sha256(c.canonical(record)).hexdigest()
              and all(verification[k] is True for k in ("read_only", "result_unchanged", "source_hashes_unchanged"))
              and verification["state_count"] == 18 and verification["value_count"] == 864,
              "ND_VERIFICATION_INVALID")
    counts = record["counts"]
    c.require(all(type(counts[k]) is int and counts[k] == 18 for k in
                  ("analyze_attempt_count", "analyze_return_count", "completed_analyses"))
              and counts["receptor_values"] == 864
              and all(counts[k] == 0 for k in ("distance_calculations", "rule_calls", "memory_calls",
                                              "context_calls", "field_calls", "runtime_calls", "pcm_payloads_persisted")),
              "ND_MATERIALIZATION_COUNTS_INVALID")
    profile = record["receptor_profile"]
    check_root(profile, "profile_digest", roots.profile)
    c.require(profile["config"] == execution["receptor_profile"] == PROFILE
              and profile["config_digest"] == execution["receptor_profile_digest"] == c.digest(PROFILE)
              and profile["method"] == "LogSpectralReceptor.analyze"
              and profile["receptor_source_sha256"] == seal["source_hashes_before"]["mcm_field_organism/log_spectral_receptor.py"],
              "ND_PROFILE_INVALID")
    c.require(len(profile["channel_ids"]) == len(set(profile["channel_ids"])) == len(profile["bands"]) == 48
              and profile["channel_ids"] == [b["channel_id"] for b in profile["bands"]], "ND_CHANNELS_INVALID")
    c.require(type(record["states"]) is list and len(record["states"]) == len(execution["sources"]) == 18,
              "ND_SOURCE_COUNT_INVALID")
    sources = []
    recipe_keys = ("source_id", "format", "channels", "sample_rate", "sample_count", "algorithm", "seed", "partials")
    for n, (state, spec) in enumerate(zip(record["states"], execution["sources"], strict=True), 1):
        check_root(state, "materialized_state_digest", state["materialized_state_digest"])
        c.require(state["source_id"] == spec["source_id"] == f"s{n:03d}" and state["ordinal"] == spec["ordinal"] == n,
                  "ND_SOURCE_ORDER_INVALID")
        c.require(spec["recipe_digest"] == c.digest({k: spec[k] for k in recipe_keys})
                  and all(state[k] == spec[k] for k in ("recipe_digest", "pcm_sha256", "clock_id", "window_start_sample",
                                                       "window_end_sample", "sample_count")), "ND_SOURCE_PARENT_INVALID")
        c.require(state["clock_id"] == "s2nd-source-sample-clock"
                  and type(state["window_start_sample"]) is type(state["window_end_sample"]) is int
                  and (state["window_start_sample"], state["window_end_sample"]) == ((n - 1) * 4800, n * 4800),
                  "ND_SOURCE_TIME_INVALID")
        c.require(state["execution_digest"] == roots.execution and state["profile_digest"] == roots.profile
                  and state["payload_validated_before_analysis"] is True
                  and state["time_semantics"] == "DECLARED_PCM_SOURCE_WINDOW_NOT_RECEPTOR_TIMESTAMP", "ND_STATE_BINDING_INVALID")
        c.require(type(state["values"]) is list, "ND_VALUES_FORM_INVALID")
        values = tuple(state["values"])
        c.check_values(values, 48)
        c.require(state["values_digest"] == c.digest(values)
                  and state["values_f64le_sha256"] == hashlib.sha256(struct.pack("<48d", *values)).hexdigest(),
                  "ND_VALUES_DIGEST_INVALID")
        source = c.sealed(c.Source48(state["source_id"], roots.materialization, roots.profile,
                                    state["materialized_state_digest"], state["clock_id"],
                                    state["window_start_sample"], state["window_end_sample"], values, state["values_digest"]))
        c.check_source(source, 48)
        sources.append(source)
    mapping = {s.source_id: s for s in sources}
    c.require(execution["candidate_sources"] == [f"s{i:03d}" for i in range(1, 7)]
              and execution["cue_sources"] == [f"s{i:03d}" for i in range(7, 19)], "ND_INVENTORY_INVALID")
    c.require(len(execution["panels"]) == 12 and len(execution["cases"]) == 48, "ND_PANEL_COUNT_INVALID")
    panels = {}
    for n, panel in enumerate(execution["panels"], 1):
        c.require(panel["panel_id"] == f"p{n:02d}", "ND_PANEL_ORDER_INVALID")
        banks = []
        for bank, size in (("b4", 9), ("fast", 3)):
            c.require(type(panel[bank]) is list and len(panel[bank]) == size
                      and [entry["position"] for entry in panel[bank]] == list(range(size)), "ND_PANEL_FORM_INVALID")
            c.require(all(entry["source_id"] is None or entry["source_id"] in execution["candidate_sources"]
                          for entry in panel[bank]), "ND_PANEL_SOURCE_INVALID")
            banks.append(tuple(None if entry["source_id"] is None else mapping[entry["source_id"]] for entry in panel[bank]))
        panels[panel["panel_id"]] = banks
    cases = []
    for n, spec in enumerate(execution["cases"], 1):
        c.require(spec["case_id"] == f"c{n:03d}" and spec["panel_id"] == f"p{(n - 1) // 4 + 1:02d}"
                  and spec["cue_source_id"] in execution["cue_sources"], "ND_CASE_ORDER_INVALID")
        b4, fast = panels[spec["panel_id"]]
        case = c.sealed(c.Case(spec["case_id"], spec["panel_id"], roots.materialization,
                               c.project_cue(mapping[spec["cue_source_id"]]), b4, fast))
        c.validate_case(case)
        cases.append(case)
    result = c.sealed(BoundInputs(roots, tuple(sources), tuple(cases)))
    check_inputs(result)
    return result


def bind_inputs(execution, seal, record, verification, roots=BOUND_ROOTS):
    try:
        return _bind(execution, seal, record, verification, roots)
    except c.ComparisonError:
        raise
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as error:
        raise c.ComparisonError("ND_BINDING_FORM_INVALID") from error


def check_inputs(bound):
    c.require(type(bound) is BoundInputs, "ND_INPUT_TYPE_INVALID")
    c.check_digest(bound)
    c.require(type(bound.sources) is tuple and len(bound.sources) == 18
              and type(bound.cases) is tuple and len(bound.cases) == 48, "ND_INPUT_COUNT_INVALID")
    mapping = {s.source_id: s for s in bound.sources}
    for source in bound.sources:
        c.check_source(source, 48)
        c.require(source.root_digest == bound.roots.materialization and source.profile_digest == bound.roots.profile,
                  "ND_INPUT_SOURCE_INVALID")
    for i, case in enumerate(bound.cases, 1):
        c.validate_case(case)
        cue = mapping[case.cue.source_id]
        c.require(case.case_id == f"c{i:03d}" and case.cue == c.project_cue(cue)
                  and all(s is None or s == mapping[s.source_id] for s in case.b4 + case.fast), "ND_CASE_SOURCE_INVALID")
    c.require(sum(s is not None for case in bound.cases for s in case.b4 + case.fast) == 72, "ND_OCCUPANCY_INVALID")


def check_batch(bound, results, decisions):
    check_inputs(bound)
    c.require(type(results) is type(decisions) is tuple and len(results) == len(decisions) == 96, "ND_BATCH_COUNT_INVALID")
    for i, (case, result, decision) in enumerate(zip(bound.cases + bound.cases, results, decisions, strict=True)):
        c.require(type(result) is c.CaseResult and type(decision) is c.Decision, "ND_RESULT_TYPE_INVALID")
        c.check_digest(result)
        c.require(result.case_id == case.case_id and result.rule == c.RULES[i // 48]
                  and result.input_digest == result.prestate_digest == result.poststate_digest == case.digest
                  and result.visited_positions == c.POSITIONS and result.decision == decision, "ND_RESULT_BINDING_INVALID")
        expected = tuple((bank, p, s) for bank, slots in (("B4", case.b4), ("FAST", case.fast))
                         for p, s in enumerate(slots) if s is not None)
        c.require(type(result.rows) is tuple and len(result.rows) == len(expected), "ND_ROWS_INVALID")
        for row, (bank, position, source) in zip(result.rows, expected, strict=True):
            c.check_digest(row)
            c.require((row.bank, row.position, row.source_id, row.source_digest)
                      == (bank, position, source.source_id, source.digest), "ND_ROW_SOURCE_INVALID")
        c.require(result.band_differences == len(expected) * 24, "ND_BAND_COUNT_INVALID")
    for arm in (results[:48], results[48:]):
        c.require(sum(len(r.rows) for r in arm) == 72 and sum(r.band_differences for r in arm) == 1728
                  and sum(len(r.visited_positions) for r in arm) == 576, "ND_ARM_BUDGET_INVALID")
    equality_terms = sum(r.equality_terms for r in results)
    c.require(all(type(r.equality_terms) is int and r.equality_terms >= 0 for r in results)
              and equality_terms <= 2304 and 3 * equality_terms <= 6912 <= 9216,
              "ND_EQUALITY_BUDGET_INVALID")


def encode_comparison(bound, results, decisions, evaluation=None):
    check_batch(bound, results, decisions)
    data = c.canonical({"schema": "s2nd.rule-comparison.v1", "input_digest": bound.digest,
                        "roots": asdict(bound.roots), "results": [asdict(r) for r in results],
                        "baseline_decisions": [asdict(d) for d in decisions], "evaluation": evaluation})
    c.require(len(data) <= c.MAX_OUTPUT_BYTES, "OUTPUT_TOO_LARGE")
    return data


def verify_comparison(bound, results, decisions):
    check_batch(bound, results, decisions)
    for case, result in zip(bound.cases + bound.cases, results, strict=True):
        c.verify_case(case, result, result.digest)
    for left, right in zip(results[:48], results[48:], strict=True):
        c.require(tuple(r.terms for r in left.rows) == tuple(r.terms for r in right.rows)
                  and set(right.b4_matches) <= set(left.b4_matches) and set(right.fast_matches) <= set(left.fast_matches),
                  "ND_ARM_INPUT_OR_SUBSET_INVALID")
    encode_comparison(bound, results, decisions)
    return "TECHNICALLY_VALID"
