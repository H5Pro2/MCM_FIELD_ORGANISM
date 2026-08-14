"""W7-AS terminal W7-AN/AP/AR handoff without persistence or execution."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json

from .w7an_r124_resolution_container import W7ANR124ResolutionContainer
from .w7an_staged_r124_coordinator import (
    W7ANStagedR124CoordinatorError,
    _TOTAL_PHASES,
    _W7ANStagedR124Coordinator,
    _finalize_w7an_staged_r124_coordinator,
)
from .w7ao_resolution_comparison_contract import (
    W7AOResolutionComparisonContract,
)
from .w7ap_raw_resolution_distance_compositor import (
    W7APRawResolutionDistanceComposition,
    compose_w7ap_raw_resolution_distances,
)
from .w7aq_numerical_evaluation_contract import (
    W7AQNumericalEvaluationContract,
)
from .w7ar_numerical_resolution_evaluator import (
    W7ARNumericalResolutionEvaluation,
    evaluate_w7ar_numerical_resolution,
)


class W7ASTerminalHandoffError(RuntimeError):
    """Raised when the terminal in-memory handoff cannot complete."""


_HANDOFF_ID = "w7as.terminal-w7an-ap-ar-in-memory-handoff.v1"
_W7AN_CONTAINER_DIGEST = (
    "4f150aad9f5c3803f1432550aa4db79b40aea3f7a4975b49802694fad2fff3e5"
)
_W7AO_CONTRACT_DIGEST = (
    "14455f15e6f3d0f96106aa766ae544ec76f19b5c94308329ec45fd0cd12067dc"
)
_W7AQ_CONTRACT_DIGEST = (
    "66717c7bb1947d44253573a275f326944e5d9aa623389b55162b81a5ea886ee3"
)


def _digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def _payload(
    w7ap_composition_digest: str,
    w7ar_evaluation_digest: str,
) -> dict[str, object]:
    return {
        "handoff_id": _HANDOFF_ID,
        "coordinator_phase_receipt_count": _TOTAL_PHASES,
        "w7an_container_digest": _W7AN_CONTAINER_DIGEST,
        "w7ao_contract_digest": _W7AO_CONTRACT_DIGEST,
        "w7ap_composition_digest": w7ap_composition_digest,
        "w7aq_contract_digest": _W7AQ_CONTRACT_DIGEST,
        "w7ar_evaluation_digest": w7ar_evaluation_digest,
        "persisted": False,
        "field_function_decision_allowed": False,
        "memory_claim_allowed": False,
    }


@dataclass(frozen=True, slots=True)
class W7ASTerminalInMemoryHandoff:
    """Terminal digest chain retaining all three in-memory result objects."""

    handoff_id: str
    coordinator_phase_receipt_count: int
    resolution_container: W7ANR124ResolutionContainer = field(repr=False)
    distance_composition: W7APRawResolutionDistanceComposition = field(
        repr=False
    )
    numerical_evaluation: W7ARNumericalResolutionEvaluation = field(
        repr=False
    )
    w7an_container_digest: str
    w7ao_contract_digest: str
    w7ap_composition_digest: str
    w7aq_contract_digest: str
    w7ar_evaluation_digest: str
    persisted: bool
    field_function_decision_allowed: bool
    memory_claim_allowed: bool
    terminal_handoff_digest: str

    def __post_init__(self) -> None:
        if (
            self.handoff_id != _HANDOFF_ID
            or self.coordinator_phase_receipt_count != _TOTAL_PHASES
            or not isinstance(
                self.resolution_container,
                W7ANR124ResolutionContainer,
            )
            or not isinstance(
                self.distance_composition,
                W7APRawResolutionDistanceComposition,
            )
            or not isinstance(
                self.numerical_evaluation,
                W7ARNumericalResolutionEvaluation,
            )
            or self.w7an_container_digest != _W7AN_CONTAINER_DIGEST
            or self.resolution_container.resolution_container_digest
            != self.w7an_container_digest
            or self.w7ao_contract_digest != _W7AO_CONTRACT_DIGEST
            or self.distance_composition.w7an_container_digest
            != self.w7an_container_digest
            or self.distance_composition.w7ao_contract_digest
            != self.w7ao_contract_digest
            or self.w7ap_composition_digest
            != self.distance_composition.raw_resolution_distance_composition_digest
            or self.w7aq_contract_digest != _W7AQ_CONTRACT_DIGEST
            or self.numerical_evaluation.w7aq_contract_digest
            != self.w7aq_contract_digest
            or self.numerical_evaluation.raw_resolution_distance_composition_digest
            != self.w7ap_composition_digest
            or self.w7ar_evaluation_digest
            != self.numerical_evaluation.evaluation_result_digest
            or self.persisted is not False
            or self.field_function_decision_allowed is not False
            or self.memory_claim_allowed is not False
            or self.distance_composition.field_function_decision_allowed
            is not False
            or self.numerical_evaluation.field_function_decision_allowed
            is not False
            or self.numerical_evaluation.memory_claim_allowed is not False
        ):
            raise W7ASTerminalHandoffError(
                "terminal in-memory handoff binding is invalid"
            )
        payload = _payload(
            self.w7ap_composition_digest,
            self.w7ar_evaluation_digest,
        )
        if self.terminal_handoff_digest != _digest(payload):
            raise W7ASTerminalHandoffError(
                "terminal in-memory handoff digest differs"
            )


def _finalize_w7as_terminal_in_memory_handoff(
    state: _W7ANStagedR124Coordinator,
    canonical_cap,
    canonical_handoff,
    canonical_raw,
    comparison_contract: W7AOResolutionComparisonContract,
    evaluation_contract: W7AQNumericalEvaluationContract,
) -> W7ASTerminalInMemoryHandoff:
    """Finalize W7-AN and immediately compose and evaluate in memory."""

    if not isinstance(state, _W7ANStagedR124Coordinator):
        raise W7ASTerminalHandoffError(
            "terminal handoff requires the staged W7-AN coordinator"
        )
    if (
        getattr(state, "w7as_terminal_result", None) is not None
        or getattr(state, "w7as_terminal_error", None) is not None
    ):
        raise W7ASTerminalHandoffError(
            "terminal handoff was already attempted"
        )
    if (
        not state.completed
        or state.completed_phase_count != _TOTAL_PHASES
        or len(state.receipts) != _TOTAL_PHASES
        or state.resolution_container is not None
        or not isinstance(
            comparison_contract,
            W7AOResolutionComparisonContract,
        )
        or comparison_contract.contract_digest != _W7AO_CONTRACT_DIGEST
        or not isinstance(
            evaluation_contract,
            W7AQNumericalEvaluationContract,
        )
        or evaluation_contract.contract_digest != _W7AQ_CONTRACT_DIGEST
    ):
        raise W7ASTerminalHandoffError(
            "terminal handoff prerequisites differ"
        )
    try:
        container = _finalize_w7an_staged_r124_coordinator(
            state,
            canonical_cap,
            canonical_handoff,
            canonical_raw,
        )
        composition = compose_w7ap_raw_resolution_distances(
            container,
            comparison_contract,
        )
        evaluation = evaluate_w7ar_numerical_resolution(
            composition,
            evaluation_contract,
        )
        payload = _payload(
            composition.raw_resolution_distance_composition_digest,
            evaluation.evaluation_result_digest,
        )
        result = W7ASTerminalInMemoryHandoff(
            _HANDOFF_ID,
            _TOTAL_PHASES,
            container,
            composition,
            evaluation,
            _W7AN_CONTAINER_DIGEST,
            _W7AO_CONTRACT_DIGEST,
            composition.raw_resolution_distance_composition_digest,
            _W7AQ_CONTRACT_DIGEST,
            evaluation.evaluation_result_digest,
            False,
            False,
            False,
            _digest(payload),
        )
    except Exception as error:
        state.w7as_terminal_error = f"{type(error).__name__}: {error}"
        raise W7ASTerminalHandoffError(state.w7as_terminal_error) from error
    state.w7as_terminal_result = result
    return result
