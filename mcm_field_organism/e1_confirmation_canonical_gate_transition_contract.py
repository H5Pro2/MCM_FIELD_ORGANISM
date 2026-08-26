"""Private S1-EB29 static gate-transition contract; opens no gate."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path

from .e1_confirmation_canonical_dataflow_contract import (
    E1ConfirmationCanonicalDataflowContract,
)
from .e1_refined_formation_runner import _digest


class E1ConfirmationCanonicalGateTransitionContractError(ValueError):
    """Raised when an S1-EB29 transition or permanent closure changed."""


S1_EB28_CONTRACT_DIGEST = (
    "f14f301c5391c6f5052d486dcf0473d7e07caf7b070cfdc84e2038cef8c53ba6"
)
S1_EB28_IMPLEMENTATION_SHA256 = (
    "b6e483e4a0aaecb0eb584318e454ade19c11b0d09e378753c0f27f7162556b78"
)
S1_EB29_TRANSITIONS = (
    (
        "probe_execution",
        "after_fresh_preflight_lock_attempt_and_verified_formation_handoff",
        "probe_handoff.probe_execution_permitted",
        False,
        True,
    ),
    (
        "result_composition",
        "after_three_ordered_valid_r2_r4_r8_probe_results",
        "result_handoff.result_composition_permitted",
        False,
        True,
    ),
    (
        "report_execution",
        "after_verified_result_and_report_handoff",
        "report_handoff.execution_permitted",
        False,
        True,
    ),
    (
        "report_persistence",
        "with_report_execution_after_verified_result_and_report_handoff",
        "report_handoff.persistence_permitted",
        False,
        True,
    ),
)
S1_EB29_PERMANENT_CLOSURES = (
    "probe_handoff.decision_permitted",
    "probe_handoff.persistence_permitted",
    "probe_handoff.claims_permitted",
    "result_handoff.decision_permitted",
    "result_handoff.persistence_permitted",
    "result_handoff.claims_permitted",
    "report_handoff.retry_permitted",
    "report_handoff.claims_permitted",
    "release.s1_ea6_rerun_permitted",
    "release.posthoc_tuning_permitted",
)
S1_EB29_REQUIRED_EVIDENCE = (
    "same_process_preflight_younger_than_five_seconds",
    "exclusive_lock_created",
    "exclusive_attempt_created",
    "formation_matches_binding_chain_and_r2_r4_r8",
    "probe_handoff_matches_formation_and_probe_plans",
    "three_probe_results_match_handoff_and_r2_r4_r8",
    "result_handoff_matches_formation_probe_handoff_and_probe_results",
    "chain_result_matches_result_handoff_and_chain_contract",
    "report_handoff_matches_result_and_registered_targets",
    "resource_guard_active_for_entire_worker_process",
)
S1_EB29_FAILURE_POLICY = (
    ("before_attempt", "no_attempt_retained_no_execution_started"),
    ("after_attempt_before_publish", "retain_attempt_remove_lock_no_retry"),
    ("after_publish_before_verification", "retain_attempt_remove_lock_no_retry"),
    ("after_verified_publish", "remove_attempt_then_remove_lock_complete"),
)


@dataclass(frozen=True, slots=True)
class E1ConfirmationCanonicalGateTransitionContract:
    contract_id: str
    dataflow_contract_digest: str
    dataflow_implementation_sha256: str
    transitions: tuple[tuple[str, str, str, bool, bool], ...]
    permanent_closures: tuple[str, ...]
    required_evidence: tuple[str, ...]
    failure_policy: tuple[tuple[str, str], ...]
    transition_count: int
    permanent_closure_count: int
    gates_opened_now: bool
    objects_constructed: bool
    canonical_calls_performed: bool
    marker_creation_permitted: bool
    canonical_execution_permitted: bool
    canonical_persistence_permitted: bool
    retry_permitted: bool
    claims_permitted: bool
    contract_status: str
    contract_digest: str

    def __post_init__(self) -> None:
        if (
            self.contract_id != "e1.confirmation-gate-transition.s1eb29.v1"
            or self.dataflow_contract_digest != S1_EB28_CONTRACT_DIGEST
            or self.dataflow_implementation_sha256
            != S1_EB28_IMPLEMENTATION_SHA256
            or self.transitions != S1_EB29_TRANSITIONS
            or self.permanent_closures != S1_EB29_PERMANENT_CLOSURES
            or self.required_evidence != S1_EB29_REQUIRED_EVIDENCE
            or self.failure_policy != S1_EB29_FAILURE_POLICY
            or self.transition_count != 4
            or self.permanent_closure_count != 10
            or self.gates_opened_now is not False
            or self.objects_constructed is not False
            or self.canonical_calls_performed is not False
            or self.marker_creation_permitted is not False
            or self.canonical_execution_permitted is not False
            or self.canonical_persistence_permitted is not False
            or self.retry_permitted is not False
            or self.claims_permitted is not False
            or self.contract_status != "GATE_TRANSITIONS_BOUND_NOT_APPLIED"
        ):
            raise E1ConfirmationCanonicalGateTransitionContractError(
                "S1-EB29 gate-transition contract changed"
            )
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name != "contract_digest"
        }
        if self.contract_digest != _digest(payload):
            raise E1ConfirmationCanonicalGateTransitionContractError(
                "S1-EB29 contract digest does not match its payload"
            )

    def digest(self) -> str:
        return _digest(asdict(self))


def prepare_e1_confirmation_canonical_gate_transition_contract(
    dataflow: E1ConfirmationCanonicalDataflowContract,
) -> E1ConfirmationCanonicalGateTransitionContract:
    """Bind future transitions without constructing or changing handoffs."""

    if not isinstance(dataflow, E1ConfirmationCanonicalDataflowContract) or (
        dataflow.contract_digest != S1_EB28_CONTRACT_DIGEST
        or dataflow.objects_constructed is not False
        or dataflow.canonical_calls_performed is not False
        or dataflow.canonical_execution_permitted is not False
    ):
        raise E1ConfirmationCanonicalGateTransitionContractError(
            "S1-EB29 requires the unchanged closed S1-EB28 contract"
        )
    dataflow.__post_init__()
    path = Path(__file__).with_name(
        "e1_confirmation_canonical_dataflow_contract.py"
    )
    normalized = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if hashlib.sha256(normalized.encode("utf-8")).hexdigest() != (
        S1_EB28_IMPLEMENTATION_SHA256
    ):
        raise E1ConfirmationCanonicalGateTransitionContractError(
            "S1-EB29 S1-EB28 implementation changed"
        )
    values = {
        "contract_id": "e1.confirmation-gate-transition.s1eb29.v1",
        "dataflow_contract_digest": dataflow.contract_digest,
        "dataflow_implementation_sha256": S1_EB28_IMPLEMENTATION_SHA256,
        "transitions": S1_EB29_TRANSITIONS,
        "permanent_closures": S1_EB29_PERMANENT_CLOSURES,
        "required_evidence": S1_EB29_REQUIRED_EVIDENCE,
        "failure_policy": S1_EB29_FAILURE_POLICY,
        "transition_count": len(S1_EB29_TRANSITIONS),
        "permanent_closure_count": len(S1_EB29_PERMANENT_CLOSURES),
        "gates_opened_now": False,
        "objects_constructed": False,
        "canonical_calls_performed": False,
        "marker_creation_permitted": False,
        "canonical_execution_permitted": False,
        "canonical_persistence_permitted": False,
        "retry_permitted": False,
        "claims_permitted": False,
        "contract_status": "GATE_TRANSITIONS_BOUND_NOT_APPLIED",
    }
    return E1ConfirmationCanonicalGateTransitionContract(
        **values,
        contract_digest=_digest(values),
    )
