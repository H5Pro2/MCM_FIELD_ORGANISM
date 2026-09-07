"""Independent direct arithmetic and cardinality table; no primary scan helpers."""

from dataclasses import asdict
from tools import _s2np_private_coverage_comparison as types


def _direct(panel_id, cue, references, diagnostic):
    # Only input validation and record types are shared, not arithmetic or decisions.
    types.check_input(panel_id, cue, references, diagnostic=diagnostic)
    rows, hit_lists = [], [[], [], []]
    for ref in references:
        differences = []
        for position in range(len(cue.indices)):
            differences.append(abs(ref.values[position] - cue.values[position]))
        average = sum(differences) / len(differences)
        largest = max(differences)
        flags = (average <= 0.1, largest <= 0.1, average <= 0.01)
        for k in range(3):
            if flags[k]:
                hit_lists[k].append(ref.source_id)
        rows.append(types.Relation(ref.source_id, ref.digest,
            tuple(types.BandDifference(cue.indices[k], differences[k]) for k in range(len(differences))),
            average, largest, flags))
    table = {0: "NO_APPLICABILITY", 1: "UNIQUE_APPLICABILITY", 2: "AMBIGUOUS_APPLICABILITY"}
    findings = tuple(types.Finding(condition, threshold, tuple(hits), table[len(hits)]) for condition, threshold, hits
        in zip(("A_HISTORICAL_SUM", "A_ALL_BANDS", "SLOW_HISTORICAL_SUM"), (0.1, 0.1, 0.01), hit_lists, strict=True))
    fields = dict(panel_id=panel_id, view_id=cue.view_id, cue_id=cue.source_id, cue_digest=cue.digest,
        input_digest=types.digest(dict(panel_id=panel_id, cue=asdict(cue), references=[asdict(r) for r in references])),
        relations=tuple(rows), findings=findings, difference_count=sum(len(r.differences) for r in rows))
    result = types.PanelResult(**fields, record_digest=types.digest({**fields,
        "relations": [asdict(r) for r in rows], "findings": [asdict(f) for f in findings]}))
    types.require(len(types.canonical(asdict(result))) <= types.MAX_PANEL_BYTES, "PANEL_SIZE_EXCEEDED")
    return result


def direct_partial(panel_id, cue, references):
    return _direct(panel_id, cue, references, False)


def direct_diagnostic(panel_id, cue, references):
    return _direct(panel_id, cue, references, True)
