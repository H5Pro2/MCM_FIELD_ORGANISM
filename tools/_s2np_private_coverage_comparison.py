"""Bound, reduced-value coverage diagnostics. No corpus IO or receptor imports."""

from dataclasses import asdict, dataclass
import math
import re

from tools import _s2np_private_source_binding as binding

canonical, digest = binding.canonical, binding.digest
VIEWS = binding.VIEWS
CONDITIONS = ("A_HISTORICAL_SUM", "A_ALL_BANDS", "SLOW_HISTORICAL_SUM")
THRESHOLDS = (0.1, 0.1, 0.01)
PROFILE = binding.profile_binding()["half_profile_digest"]
MAIN_GATE = False
MAX_OUTPUT_BYTES = 2097152
MAX_PANEL_BYTES = 32768
MAX_DIFFERENCES_PER_IMPLEMENTATION = 3840
MAX_PANEL_FINDINGS_PER_IMPLEMENTATION = 360


class S2NPCoverageError(ValueError):
    pass


def require(ok, code):
    if not ok:
        raise S2NPCoverageError(code)


def check_hash(value):
    require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value), "DIGEST_INVALID")


def identifier(value):
    require(type(value) is str and re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value), "IDENTITY_INVALID")


def values_check(values, size):
    require(type(values) is tuple and len(values) == size, "VALUE_SHAPE_INVALID")
    require(all(type(v) is float and math.isfinite(v) and 0.0 <= v <= 1.0 for v in values),
            "VALUE_DOMAIN_INVALID")


@dataclass(frozen=True, slots=True)
class ViewValues:
    source_id: str
    source_digest: str
    payload_digest: str
    projection_digest: str
    profile_digest: str
    clock_id: str
    start_tick: int
    end_tick: int
    snapshot_index: int
    view_id: str
    indices: tuple[int, ...]
    values: tuple[float, ...]

    def __post_init__(self):
        identifier(self.source_id)
        for h in (self.source_digest, self.payload_digest, self.projection_digest, self.profile_digest):
            check_hash(h)
        require(self.profile_digest == PROFILE, "PROFILE_INVALID")
        require(self.clock_id == "audio.sample", "CLOCK_INVALID")
        require(all(type(v) is int for v in (self.start_tick, self.end_tick, self.snapshot_index))
                and self.start_tick >= 0 and self.start_tick % 4800 == 0
                and self.end_tick == self.start_tick + 4800
                and self.snapshot_index == self.start_tick // 480, "TIME_INVALID")
        require(type(self.indices) is tuple and all(type(i) is int for i in self.indices)
                and (self.view_id, self.indices) in VIEWS, "MASK_INVALID")
        values_check(self.values, len(self.indices))

    @property
    def digest(self):
        return digest(asdict(self))


def project_values(*, source_id, source_digest, payload_digest, projection_digest, profile_digest,
                   start_tick, end_tick, snapshot_index, values, view_id):
    """Projection boundary only; caller supplies an already verified NJ source binding.

    This does not authenticate the parent materialization or recover raw values.
    Only the selected tuple crosses into either comparison implementation.
    """
    values_check(values, 48)
    require(view_id in dict(VIEWS), "MASK_INVALID")
    indices = dict(VIEWS)[view_id]
    return ViewValues(source_id, source_digest, payload_digest, projection_digest, profile_digest,
                      "audio.sample", start_tick, end_tick, snapshot_index,
                      view_id, indices, tuple(values[i] for i in indices))


@dataclass(frozen=True, slots=True)
class BandDifference:
    original_index: int
    value: float


@dataclass(frozen=True, slots=True)
class Relation:
    reference_id: str
    reference_digest: str
    differences: tuple[BandDifference, ...]
    mean: float
    maximum: float
    applicable: tuple[bool, bool, bool]


@dataclass(frozen=True, slots=True)
class Finding:
    condition_id: str
    threshold: float
    hits: tuple[str, ...]
    status: str


@dataclass(frozen=True, slots=True)
class PanelResult:
    panel_id: str
    view_id: str
    cue_id: str
    cue_digest: str
    input_digest: str
    relations: tuple[Relation, ...]
    findings: tuple[Finding, ...]
    difference_count: int
    record_digest: str


def input_binding(panel_id, cue, references):
    return digest(dict(panel_id=panel_id, cue=asdict(cue), references=[asdict(r) for r in references]))


def check_input(panel_id, cue, references, *, diagnostic):
    identifier(panel_id)
    require(type(cue) is ViewValues and type(references) is tuple and len(references) <= 2,
            "INPUT_FORM_INVALID")
    require(all(type(r) is ViewValues for r in references), "INPUT_FORM_INVALID")
    for v in (cue,) + references:
        v.__post_init__()
    require((cue.view_id == "FULL_48_DIAGNOSTIC") is diagnostic, "DIAGNOSTIC_ISOLATION")
    require(len(set(r.source_id for r in references)) == len(references), "PANEL_DUPLICATE_ID")
    for r in references:
        require(r.view_id == cue.view_id and r.indices == cue.indices, "MASK_MISMATCH")
        require(r.source_id != cue.source_id and r.end_tick <= cue.start_tick, "SOURCE_TIME_MISMATCH")


def _compare(panel_id, cue, references, diagnostic):
    check_input(panel_id, cue, references, diagnostic=diagnostic)
    relations = []
    for reference in references:
        terms = tuple(abs(r - q) for r, q in zip(reference.values, cue.values, strict=True))
        mean, maximum = sum(terms) / len(cue.indices), max(terms)
        relations.append(Relation(reference.source_id, reference.digest,
            tuple(BandDifference(i, v) for i, v in zip(cue.indices, terms, strict=True)),
            mean, maximum, (mean <= 0.1, maximum <= 0.1, mean <= 0.01)))
    findings = []
    for k, (condition, threshold) in enumerate(zip(CONDITIONS, THRESHOLDS, strict=True)):
        hits = tuple(r.reference_id for r in relations if r.applicable[k])
        status = ("NO_APPLICABILITY", "UNIQUE_APPLICABILITY", "AMBIGUOUS_APPLICABILITY")[len(hits)]
        findings.append(Finding(condition, threshold, hits, status))
    fields = dict(panel_id=panel_id, view_id=cue.view_id, cue_id=cue.source_id, cue_digest=cue.digest,
        input_digest=input_binding(panel_id, cue, references), relations=tuple(relations),
        findings=tuple(findings), difference_count=len(references) * len(cue.indices))
    result = PanelResult(**fields, record_digest=digest({**fields,
        "relations": [asdict(r) for r in relations], "findings": [asdict(f) for f in findings]}))
    require(len(canonical(asdict(result))) <= MAX_PANEL_BYTES, "PANEL_SIZE_EXCEEDED")
    return result


def compare_partial(panel_id, cue, references):
    return _compare(panel_id, cue, references, False)


def compare_diagnostic(panel_id, cue, references):
    return _compare(panel_id, cue, references, True)


def verify_panel(panel_id, cue, references, primary, direct):
    """Evidence check only: never subtract source values or repeat a scan."""
    check_input(panel_id, cue, references, diagnostic=cue.view_id == "FULL_48_DIAGNOSTIC")
    for result in (primary, direct):
        require(type(result) is PanelResult, "RECORD_TYPE_INVALID")
        require(len(canonical(asdict(result))) <= MAX_PANEL_BYTES, "PANEL_SIZE_EXCEEDED")
        payload = asdict(result)
        recorded = payload.pop("record_digest")
        require(recorded == digest(payload), "RECORD_DIGEST_INVALID")
        require((result.panel_id, result.view_id, result.cue_id, result.cue_digest, result.input_digest) ==
                (panel_id, cue.view_id, cue.source_id, cue.digest, input_binding(panel_id, cue, references)),
                "SOURCE_BINDING_INVALID")
        require(type(result.relations) is tuple and len(result.relations) == len(references)
                and type(result.findings) is tuple and len(result.findings) == 3
                and type(result.difference_count) is int
                and result.difference_count == len(references) * len(cue.indices), "SCAN_INCOMPLETE")
        for ref, rel in zip(references, result.relations, strict=True):
            require(type(rel) is Relation and (rel.reference_id, rel.reference_digest) == (ref.source_id, ref.digest),
                    "RELATION_BINDING_INVALID")
            require(type(rel.differences) is tuple and all(type(d) is BandDifference for d in rel.differences)
                    and tuple(d.original_index for d in rel.differences) == cue.indices
                    and all(type(d.original_index) is int for d in rel.differences), "BAND_BINDING_INVALID")
            terms = tuple(d.value for d in rel.differences)
            values_check(terms, len(cue.indices))
            require(type(rel.mean) is type(rel.maximum) is float
                    and rel.mean.hex() == (sum(terms) / len(terms)).hex()
                    and rel.maximum.hex() == max(terms).hex(), "STATISTIC_INVALID")
            require(type(rel.applicable) is tuple and all(type(x) is bool for x in rel.applicable)
                    and rel.applicable == (rel.mean <= 0.1, rel.maximum <= 0.1, rel.mean <= 0.01),
                    "CONDITION_INVALID")
        for k, finding in enumerate(result.findings):
            require(type(finding) is Finding, "FINDING_TYPE_INVALID")
            expected_hits = tuple(r.reference_id for r in result.relations if r.applicable[k])
            require(finding.condition_id == CONDITIONS[k] and type(finding.threshold) is float
                    and finding.threshold == THRESHOLDS[k] and type(finding.hits) is tuple
                    and finding.hits == expected_hits and finding.status ==
                    ("NO_APPLICABILITY", "UNIQUE_APPLICABILITY", "AMBIGUOUS_APPLICABILITY")[len(expected_hits)],
                    "FINDING_INVALID")
    require(canonical(asdict(primary)) == canonical(asdict(direct)), "DIRECT_BASELINE_DIFFERS")
    return digest(dict(primary=primary.record_digest, direct=direct.record_digest, verified=True,
                       source_differences_recomputed=0, expected_outcome_checked=False))


def fixed_inputs(catalog):
    """Literal NP panel traversal. Only metadata and projected inputs, no file loading."""
    require(type(catalog) is tuple and len(catalog) == 36, "CATALOG_INVALID")
    expected = tuple((name, f"np-a{n:02d}") for name, _ in VIEWS for n in range(1, 13))
    require(all(type(v) is ViewValues for v in catalog)
            and tuple((v.view_id, v.source_id) for v in catalog) == expected, "CATALOG_ORDER_INVALID")
    for offset, v in enumerate(catalog):
        v.__post_init__()
        require(v.start_tick == (offset % 12) * 4800, "CATALOG_TIME_INVALID")
    for n in range(12):
        origins = [tuple(getattr(catalog[n + j * 12], k) for k in (
            "source_digest", "payload_digest", "projection_digest", "profile_digest", "clock_id", "start_tick", "end_tick", "snapshot_index"))
            for j in range(3)]
        require(origins[0] == origins[1] == origins[2], "CROSS_VIEW_SOURCE_INVALID")
        full = catalog[24 + n]
        for partial in (catalog[n], catalog[12 + n]):
            require(tuple(v.hex() for v in partial.values) == tuple(full.values[i].hex() for i in partial.indices),
                    "CROSS_VIEW_VALUES_INVALID")
    by_id = {(v.view_id, v.source_id): v for v in catalog}
    return tuple((p, by_id[view, cue], tuple(by_id[view, r] for r in refs))
                 for view, _ in VIEWS for p, refs in binding.PANELS for cue in binding.CUES)


def compare_fixed(catalog, implementation):
    require(implementation in ("PRIMARY", "DIRECT"), "IMPLEMENTATION_INVALID")
    inputs = fixed_inputs(catalog)
    if implementation == "DIRECT":
        from tools import _s2np_private_coverage_baseline as baseline
        partial, full = baseline.direct_partial, baseline.direct_diagnostic
    else:
        partial, full = compare_partial, compare_diagnostic
    results = tuple((full if q.view_id == "FULL_48_DIAGNOSTIC" else partial)(p, q, refs)
                    for p, q, refs in inputs)
    require(sum(r.difference_count for r in results) == 3840
            and sum(len(r.findings) for r in results) == 360
            and sum(len(r.relations) * 3 for r in results) == 360, "BUDGET_INVALID")
    return results


def verify_fixed(catalog, primary, direct):
    inputs = fixed_inputs(catalog)
    require(type(primary) is type(direct) is tuple and len(primary) == len(direct) == 120,
            "RESULT_COUNT_INVALID")
    receipts = tuple(verify_panel(*args, p, d) for args, p, d in zip(inputs, primary, direct, strict=True))
    evidence = dict(status="TECHNICALLY_VALID", receipts=receipts, panel_findings=720,
                band_differences=7680, verification_band_differences=0,
                catalog_digest=digest([asdict(v) for v in catalog]),
                primary_digest=digest([asdict(r) for r in primary]),
                direct_digest=digest([asdict(r) for r in direct]))
    return {**evidence, "verification_digest": digest(evidence)}


def bounded_payload(value):
    encoded = canonical(value)
    require(len(encoded) <= MAX_OUTPUT_BYTES, "OUTPUT_SIZE_EXCEEDED")
    return encoded
