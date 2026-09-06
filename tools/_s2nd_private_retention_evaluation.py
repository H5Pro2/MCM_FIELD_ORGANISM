"""Post-comparison N/D/R/L; no matching, receptor or corpus loading."""

from tools import _s2nc_private_rule_comparison as c
from tools import _s2nc_private_rule_evaluation as original
from tools import _s2nd_private_comparison_binding as binding


SUBTYPES = ("EXACT", "UNIFORM_GAIN", "FREQUENCY", "SPECTRAL_REWEIGHT")


def evaluate(bound, mean_results, all_results, plan):
    binding.check_inputs(bound)
    binding.check_root(plan, "evaluation_digest", bound.roots.evaluation)
    c.require(plan["execution_digest"] == bound.roots.execution and len(plan["cases"]) == 48
              and type(mean_results) is type(all_results) is tuple and len(mean_results) == len(all_results) == 48,
              "ND_EVALUATION_COUNT_INVALID")
    sources = {s.source_id: s for s in bound.sources}
    expected, annotations = [], []
    for case, spec, left, right in zip(bound.cases, plan["cases"], mean_results, all_results, strict=True):
        c.require(spec["case_id"] == case.case_id and spec["panel_id"] == case.panel_id
                  and spec["cue_source_id"] == case.cue.source_id
                  and left.input_digest == right.input_digest == case.digest, "ND_EVALUATION_CASE_INVALID")
        subtype, competition = spec["variant_subtype"], spec["competition"]
        c.require(subtype in SUBTYPES and competition in ("NO_COMPETITOR", "COMPETITOR_PRESENT"), "ND_SUBTYPE_INVALID")
        reference = sources[spec["related_reference"]]
        present = any(s is not None and s.source_id == reference.source_id for s in case.b4 + case.fast)
        c.require(spec["reference_present"] is present
                  and spec["accepted_source_ids"] == ([reference.source_id] if present else []), "ND_EXPECTATION_INVALID")
        competing = any(s is not None and s.source_id != reference.source_id for s in case.b4 + case.fast)
        c.require(competing == (competition == "COMPETITOR_PRESENT"), "ND_COMPETITION_INVALID")
        cue = sources[case.cue.source_id]
        # Canonical finite Binary64 value digests preserve even signed-zero differences.
        variation = "BITIDENTICAL" if cue.values_digest == reference.values_digest else "NON_BITIDENTICAL"
        expected.append(original.Expectation(case.case_id, spec["category"], tuple(spec["accepted_source_ids"])))
        annotations.append({"case_id": case.case_id, "variant_subtype": subtype, "competition": competition,
                            "reference_present": present, "receptor_variation": variation,
                            "cue_values_digest": cue.values_digest, "reference_values_digest": reference.values_digest})
    comparison = original.evaluate(mean_results, all_results, tuple(expected))
    rows = [{**row, **annotation} for row, annotation in zip(comparison["cases"], annotations, strict=True)]
    groups = []
    for subtype in SUBTYPES + ("ALL_VARIANTS",):
        for competition in ("ALL", "NO_COMPETITOR", "COMPETITOR_PRESENT"):
            for variation in ("ALL", "BITIDENTICAL", "NON_BITIDENTICAL"):
                selected = [r for r in rows if r["reference_present"]
                            and (r["variant_subtype"] != "EXACT" if subtype == "ALL_VARIANTS" else r["variant_subtype"] == subtype)
                            and (competition == "ALL" or r["competition"] == competition)
                            and (variation == "ALL" or r["receptor_variation"] == variation)]
                denominator = [r for r in selected if r["mean"]["correct_known"]]
                retained = sum(r["all_bands"]["correct_known"] for r in denominator)
                lost = len(denominator) - retained
                status = ("ERHALTUNG_NICHT_GEPRUEFT" if not denominator else
                          "RETENTION_FALSIFIED" if lost else "RETENTION_CONFIRMED_ON_OBSERVED_SUBSET")
                group = {"variant_subtype": subtype, "competition": competition, "receptor_variation": variation,
                         "N": len(selected), "D": len(denominator), "R": retained, "L": lost,
                         "lost_to_abstention": sum(r["lost_known"] and r["all_bands"]["abstention"] for r in denominator),
                         "lost_to_false_admission": sum(r["lost_known"] and r["all_bands"]["false_admission"] for r in denominator),
                         "status": status}
                c.require(group["D"] == group["R"] + group["L"]
                          and lost == group["lost_to_abstention"] + group["lost_to_false_admission"], "ND_RETENTION_ACCOUNTING_INVALID")
                groups.append(group)
    result = {"input_digest": bound.digest, "evaluation_plan_digest": bound.roots.evaluation,
              "comparison": comparison, "cases": rows, "retention_groups": groups}
    result["evaluation_digest"] = c.digest(result)
    c.require(len(c.canonical(result)) <= c.MAX_OUTPUT_BYTES, "OUTPUT_TOO_LARGE")
    return result
