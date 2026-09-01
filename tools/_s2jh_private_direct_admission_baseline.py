"""Independent direct decision-table baseline for S2-JH admission."""

from __future__ import annotations

from tools import _s2ic_private_two_area_conflict_contract as signal_contract
from tools import _s2jh_private_controlled_context_admission as admission


_DIRECT_TABLE = {
    "CONFLICT": ("PROCEED_WITHOUT_CONTEXT", "CONFLICT_WITHHELD"),
    "NO_CONTEXT": ("PROCEED_WITHOUT_CONTEXT", "CONTEXT_ABSENT"),
    "NO_APPLICABLE_CONTEXT": (
        "PROCEED_WITHOUT_CONTEXT",
        "CONTEXT_INAPPLICABLE",
    ),
}


def _direct_projection(
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
) -> tuple[str, str, str | None, str | None, str | None, str | None]:
    status = signal_commit.result.status
    if status == "SINGLE_SOURCE":
        applicable = tuple(
            finding for finding in (a_finding, b_finding) if finding.status == "APPLICABLE"
        )
        admission.require(len(applicable) == 1, "S2JH-E004", "J2")
        finding = applicable[0]
        admission.require(admission.valid_digest(finding.masked_values_digest), "S2JH-E004", "J2")
        context_binding = admission.digest(
            {
                "schema": admission.S2JH_SCHEMA,
                "binding_kind": "UNIQUE_APPLICABLE_CONTEXT",
                "area": finding.area,
                "finding_digest": finding.finding_digest,
                "candidate_digest": finding.candidate_digest,
                "masked_values_digest": finding.masked_values_digest,
            }
        )
        return (
            "ALLOW_CONTEXT",
            "UNIQUE_APPLICABLE_CONTEXT",
            finding.area,
            None,
            finding.masked_values_digest,
            context_binding,
        )
    if status == "CONSISTENT":
        left_digest = a_finding.masked_values_digest
        right_digest = b_finding.masked_values_digest
        admission.require(
            a_finding.status == b_finding.status == "APPLICABLE"
            and admission.valid_digest(left_digest)
            and left_digest == right_digest,
            "S2JH-E004",
            "J2",
        )
        pair_set = frozenset(
            (
                (a_finding.area, a_finding.finding_digest),
                (b_finding.area, b_finding.finding_digest),
            )
        )
        admission.require(len(pair_set) == 2, "S2JH-E004", "J2")
        role_set_digest = admission.digest(
            {
                "schema": admission.S2JH_SCHEMA,
                "binding_kind": "UNORDERED_EQUIVALENT_ROLE_SET",
                "role_finding_pairs": sorted(pair_set),
            }
        )
        equivalence_binding = admission.digest(
            {
                "schema": admission.S2JH_SCHEMA,
                "binding_kind": "UNORDERED_EQUIVALENT_CONTEXTS",
                "equivalent_role_set_digest": role_set_digest,
                "common_masked_values_digest": left_digest,
            }
        )
        return (
            "ALLOW_CONTEXT",
            "EQUIVALENT_CONTEXTS",
            None,
            role_set_digest,
            left_digest,
            equivalence_binding,
        )
    admission.require(status in _DIRECT_TABLE, "S2JH-E004", "J2")
    decision, reason = _DIRECT_TABLE[status]
    return decision, reason, None, None, None, None


def form_direct_context_admission_baseline(
    admission_input: admission.ControlledContextAdmissionInput,
    signal_input: signal_contract.TwoAreaConflictSignalInput,
    signal_commit: signal_contract.TwoAreaConflictSignalCommit,
    a_finding: signal_contract.AreaApplicabilityFinding,
    b_finding: signal_contract.AreaApplicabilityFinding,
    comparison: signal_contract.MaskedSupplementComparison,
    owner: admission.ContextAdmissionOwner,
) -> admission.ControlledContextAdmissionCommit:
    """Apply a separate literal table without invoking the admission function."""

    if type(owner) is not admission.ContextAdmissionOwner or owner.state != "READY":
        admission.fail("S2JH-E006", "J1")
    try:
        before = tuple(
            item
            for item in (
                signal_input.input_digest,
                signal_commit.result.result_digest,
                signal_commit.receipt.receipt_digest,
                signal_commit.owner_poststate.owner_poststate_digest,
                a_finding.finding_digest,
                b_finding.finding_digest,
                comparison.comparison_digest,
                signal_commit.result.prestate_digest,
                signal_commit.result.poststate_digest,
            )
        )
        admission.validate_admission_sources(
            admission_input,
            signal_input,
            signal_commit,
            a_finding,
            b_finding,
            comparison,
            owner,
            "DIRECT_TABLE_BASELINE",
        )
        projection = _direct_projection(signal_commit, a_finding, b_finding)
        admitted_count = 2 if projection[3] is not None else (1 if projection[2] is not None else 0)
        ledger = admission.ContextAdmissionLedger.build(admitted_count)
        after = (
            signal_input.input_digest,
            signal_commit.result.result_digest,
            signal_commit.receipt.receipt_digest,
            signal_commit.owner_poststate.owner_poststate_digest,
            a_finding.finding_digest,
            b_finding.finding_digest,
            comparison.comparison_digest,
            signal_commit.result.prestate_digest,
            signal_commit.result.poststate_digest,
        )
        admission.require(before == after, "S2JH-E005", "J3")
        result = admission.build_admission_result(
            admission_input,
            signal_commit,
            *projection,
            ledger,
        )
        return admission.publish_success(owner, admission_input, ledger, result)
    except admission.S2JHAdmissionFailure:
        raise
    except admission.S2JHAdmissionError as error:
        admission.publish_failure(owner, admission_input, error)
    except Exception as error:
        admission.publish_failure(
            owner,
            admission_input,
            admission.S2JHAdmissionError("S2JH-E001", "J1"),
        )
        raise AssertionError("unreachable") from error


__all__: tuple[str, ...] = ()
