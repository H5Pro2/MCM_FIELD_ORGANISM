"""Post-verification evaluation only; targets never enter runtime adapters."""

from dataclasses import dataclass
from tools import _s2ng_private_runtime_comparison as run
from tools import _s2ng_private_comparison_verification as verification


@dataclass(frozen=True, slots=True)
class ExpectationV1:
    ordinal: int
    modality: str
    target_values_digests: tuple[str, ...]
    expected_context: bool
    variant: str
    competition: str


def summarize(rows):
    """Count each modality independently; gains never cancel losses."""
    groups = {}
    for modality in ("auditory", "visual"):
        subsets = {"ALL": [r for r in rows if r["modality"] == modality]}
        for key in ("variant", "competition"):
            for value in sorted({r[key] for r in subsets["ALL"]}):
                subsets[key + ":" + value] = [r for r in subsets["ALL"] if r[key] == value]
        groups[modality] = {}
        for name, subset in subsets.items():
            positive = [r for r in subset if r["expected_context"]]
            denominator = [r for r in positive if r["reference_correct"]]
            retained = sum(r["alternative_correct"] for r in denominator)
            losses = [r["ordinal"] for r in denominator if not r["alternative_correct"]]
            groups[modality][name] = dict(N=len(positive), D=len(denominator), R=retained, L=len(losses),
                retention_status="ERHALTUNG_NICHT_GEPRUEFT" if not denominator else "RETENTION_MEASURED",
                losses=losses,
                gains=[r["ordinal"] for r in positive if not r["reference_correct"] and r["alternative_correct"]],
                reference_false_admissions=sum(r["reference_false_admission"] for r in subset),
                alternative_false_admissions=sum(r["alternative_false_admission"] for r in subset),
                reference_abstentions=sum(r["reference_abstains"] for r in subset),
                alternative_abstentions=sum(r["alternative_abstains"] for r in subset),
                discarded_target_candidates=[dict(ordinal=r["ordinal"], candidates=r["discarded_target_candidates"])
                                             for r in subset if r["discarded_target_candidates"]])
    return groups


def evaluate(record, proof, expectations):
    verification.check(proof, "verification_digest")
    run.require(proof["record_digest"] == record["record_digest"] and proof["status"] == record["status"] == "RECORDING_COMPLETE"
                and proof["read_only"] and proof["baseline_equal"], "TECHNICAL_VERIFICATION_REQUIRED")
    verification.check(record, "record_digest")
    before = run.digest(record)
    cues = {i: p for i, p in enumerate(record["inputs"], 1) if p["event"]["event_type"] != "COMPLETE_AV_PERCEPTION"}
    run.require(type(expectations) is tuple and len(expectations) == len(cues)
                and all(type(e) is ExpectationV1 for e in expectations)
                and tuple(e.ordinal for e in expectations) == tuple(cues), "EXPECTATION_COVERAGE_INVALID")
    scans = {(s["arm"], s["ordinal"]): s["value"] for s in record["scans"] if s["role"] == "PRIMARY"}
    rows = []
    for e in expectations:
        modality = "auditory" if cues[e.ordinal]["event"]["event_type"] == "PARTIAL_AUDITORY_CUE" else "visual"
        run.require(e.modality == modality and type(e.expected_context) is bool
                    and type(e.target_values_digests) is tuple and all(run.audio.kz._valid_digest(d) for d in e.target_values_digests)
                    and (not e.expected_context or bool(e.target_values_digests)), "EXPECTATION_INVALID")
        row = dict(ordinal=e.ordinal, modality=modality, expected_context=e.expected_context,
                   variant=e.variant, competition=e.competition)
        findings = []
        for i, name in enumerate(("reference", "alternative")):
            result = scans[i, e.ordinal]
            result = result["evidence"] if modality == "auditory" else result
            findings.append(result)
            h = result["hypothesis"]
            correct = e.expected_context and h is not None and h["candidate_values_digest"] in e.target_values_digests
            row.update({name + "_decision": result["decision"], name + "_correct": correct,
                        name + "_false_admission": h is not None and not correct, name + "_abstains": h is None})
        discarded = []
        for left_bank, right_bank in zip(findings[0]["bank_scans"][:2], findings[1]["bank_scans"][:2], strict=True):
            for left, right in zip(left_bank["records"], right_bank["records"], strict=True):
                run.require((left["slot_id"], left["slot_digest"], left["candidate_values_digest"])
                            == (right["slot_id"], right["slot_digest"], right["candidate_values_digest"]), "CANDIDATE_PAIRING_INVALID")
                if left["candidate_values_digest"] in e.target_values_digests and left["observed_match"] and not right["observed_match"]:
                    discarded.append({k: left[k] for k in ("bank_role", "slot_id", "slot_digest", "candidate_values_digest")})
        row["discarded_target_candidates"] = discarded
        rows.append(row)
    run.require(before == run.digest(record), "EVALUATION_MUTATED_RECORD")
    return run.sealed(dict(record_digest=record["record_digest"], verification_digest=proof["verification_digest"],
        rows=rows, groups=summarize(rows), conclusion="BOUNDED_COMPARISON_ONLY"), "evaluation_digest")


__all__ = ()
