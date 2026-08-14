"""S1-FJ synthetic dry integration of formation capture and evaluation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .e1_confirmation_formation_runner import E1ConfirmationFormationArmAudit
from .e1_confirmation_prepared_formation_consumer import (
    S1_EC7_FORMATION_ARMS,
    S1_EC7_REFINEMENTS,
)
from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
)
from .e1_formation_s1fd_state_convergence_evaluator import (
    E1FormationS1FDStateConvergenceResult,
    evaluate_e1_formation_s1fd_state_convergence,
)
from .e1_formation_s1ff_in_memory_capture_adapter import (
    E1FormationS1FFCaptureResult,
    capture_e1_formation_s1ff_in_memory,
)
from .e1_formation_s1fh_fresh_capture_one_shot_contract import (
    E1FormationS1FHFreshCaptureOneShotContract,
)
from .e1_formation_s1fi_fresh_capture_preflight import (
    E1FormationS1FIFreshCapturePreflight,
    E1FormationS1FIPreparedInputs,
)
from .e1_local_edge_plasticity import (
    E1EdgeBinding,
    E1LocalEdgePlasticityState,
)
from .e1_refined_chain_canonical_producer import (
    _initial_field_digest,
    _initial_state_digest,
)
from .e1_refined_formation_runner import _digest, _state_payload


class E1FormationS1FJSyntheticCoordinatorError(ValueError):
    """Raised when the S1-FJ dry integration boundary changes."""


S1_FJ_FIXTURE_ID = "e1.formation-capture-synthetic-inventory.s1fj.v1"
S1_FJ_COORDINATOR_ID = "e1.formation-capture-synthetic-coordinator.s1fj.v1"
S1_FJ_REFINEMENT_AMPLITUDES = (
    ("r2", 0.000101),
    ("r4", 0.00010004),
    ("r8", 0.0001),
)


def _valid_digest(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        char in "0123456789abcdef" for char in value
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FJSyntheticInventory:
    fixture_id: str
    source_input_manifest_digest: str
    results: tuple[E1PreparedRealFormationArmResult, ...] = field(repr=False)
    formation_arm_count: int
    synthetic_result_count: int
    field_steps_executed: int
    probe_objects_created: int
    persistence_performed: bool
    fixture_digest: str

    def __post_init__(self) -> None:
        results = tuple(self.results)
        expected = tuple(
            (refinement, arm)
            for refinement, _ in S1_EC7_REFINEMENTS
            for arm in S1_EC7_FORMATION_ARMS
        )
        payload = {
            "fixture_id": self.fixture_id,
            "source_input_manifest_digest": self.source_input_manifest_digest,
            "result_digests": tuple(item.result_digest for item in results),
            "formation_arm_count": len(results),
            "synthetic_result_count": len(results),
            "field_steps_executed": 0,
            "probe_objects_created": 0,
            "persistence_performed": False,
        }
        if (
            self.fixture_id != S1_FJ_FIXTURE_ID
            or not _valid_digest(self.source_input_manifest_digest)
            or len(results) != 15
            or not all(isinstance(item, E1PreparedRealFormationArmResult) for item in results)
            or tuple((item.refinement_id, item.arm_id) for item in results) != expected
            or len({id(item.output_state) for item in results}) != 15
            or len({item.result_digest for item in results}) != 15
            or self.formation_arm_count != 15
            or self.synthetic_result_count != 15
            or self.field_steps_executed != 0
            or self.probe_objects_created != 0
            or self.persistence_performed is not False
            or self.fixture_digest != _digest(payload)
        ):
            raise E1FormationS1FJSyntheticCoordinatorError(
                "S1-FJ synthetic inventory changed or contains execution"
            )
        for item in results:
            item.__post_init__()
        object.__setattr__(self, "results", results)


def _synthetic_values(
    edge_count: int,
    arm_id: str,
    amplitude: float,
) -> tuple[float, ...]:
    values = [0.0] * edge_count
    if arm_id in {"ab", "ab_identity"}:
        values[0] = amplitude
    elif arm_id == "ba":
        values[1] = amplitude
    return tuple(values)


def _synthetic_result(
    inputs: E1FormationS1FIPreparedInputs,
    refinement_id: str,
    arm_id: str,
    amplitude: float,
) -> E1PreparedRealFormationArmResult:
    initial = inputs.initial_state
    values = _synthetic_values(len(initial.edge_bindings), arm_id, amplitude)
    state = E1LocalEdgePlasticityState(
        contract=initial.contract,
        edge_bindings=tuple(
            E1EdgeBinding(item.first_neuron_id, item.second_neuron_id, value)
            for item, value in zip(initial.edge_bindings, values, strict=True)
        ),
        edge_inventory_digest=initial.edge_inventory_digest,
    )
    formation_enabled = not arm_id.endswith("formation_ablated")
    source_sequences = (
        inputs.av_permutation.history_ba
        if arm_id.startswith("ba")
        else inputs.av_permutation.history_ab
    )
    support_count = sum(len(item.frames) for item in source_sequences)
    audit = E1ConfirmationFormationArmAudit(
        refinement_id=refinement_id,
        arm_id=arm_id,
        handoff_digest=_digest((S1_FJ_FIXTURE_ID, "handoff", refinement_id, arm_id)),
        field_digest=_digest((S1_FJ_FIXTURE_ID, "field", refinement_id, arm_id)),
        source_support_count=support_count,
        assigned_event_count=support_count,
        resource_budget_error=0.0,
        formation_enabled=formation_enabled,
        history_backreaction_enabled=False,
        state_remained_neutral=not formation_enabled,
    )
    result_values = {
        "arm_id": arm_id,
        "refinement_id": refinement_id,
        "formation_enabled": formation_enabled,
        "initial_field_digest": _initial_field_digest(inputs.initial_field),
        "initial_state_digest": _initial_state_digest(inputs.initial_state),
        "output_state": state,
        "output_state_digest": _digest(_state_payload(state)),
        "audit": audit,
        "input_objects_preserved": True,
        "copied_inputs_used": True,
        "canonical_execution_permitted": False,
        "claims_permitted": False,
    }
    digest_payload = {
        name: value
        for name, value in result_values.items()
        if name not in {"output_state", "audit"}
    }
    digest_payload["output_state"] = _state_payload(state)
    digest_payload["audit"] = asdict(audit)
    return E1PreparedRealFormationArmResult(
        **result_values,
        result_digest=_digest(digest_payload),
    )


def build_e1_formation_s1fj_synthetic_inventory(
    inputs: E1FormationS1FIPreparedInputs,
) -> E1FormationS1FJSyntheticInventory:
    """Build typed fixture outputs without calling a formation kernel."""

    if not isinstance(inputs, E1FormationS1FIPreparedInputs):
        raise E1FormationS1FJSyntheticCoordinatorError(
            "S1-FJ requires typed formation-only inputs"
        )
    inputs.__post_init__()
    if len(inputs.initial_state.edge_bindings) < 2:
        raise E1FormationS1FJSyntheticCoordinatorError(
            "S1-FJ fixture requires at least two canonical edges"
        )
    amplitudes = dict(S1_FJ_REFINEMENT_AMPLITUDES)
    results = tuple(
        _synthetic_result(inputs, refinement, arm, amplitudes[refinement])
        for refinement, _ in S1_EC7_REFINEMENTS
        for arm in S1_EC7_FORMATION_ARMS
    )
    values = {
        "fixture_id": S1_FJ_FIXTURE_ID,
        "source_input_manifest_digest": inputs.input_manifest_digest,
        "results": results,
        "formation_arm_count": 15,
        "synthetic_result_count": 15,
        "field_steps_executed": 0,
        "probe_objects_created": 0,
        "persistence_performed": False,
    }
    digest_payload = dict(values)
    del digest_payload["results"]
    digest_payload["result_digests"] = tuple(item.result_digest for item in results)
    return E1FormationS1FJSyntheticInventory(
        **values,
        fixture_digest=_digest(digest_payload),
    )


@dataclass(frozen=True, slots=True)
class E1FormationS1FJSyntheticCoordinatorResult:
    coordinator_id: str
    source_s1fh_contract_digest: str
    source_s1fi_preflight_digest: str
    source_inventory_digest: str
    capture: E1FormationS1FFCaptureResult = field(repr=False)
    evaluation: E1FormationS1FDStateConvergenceResult = field(repr=False)
    formation_results_consumed: int
    captured_state_vectors: int
    dry_integration_confirmed: bool
    owner_authorization_present: bool
    execution_permitted: bool
    field_steps_executed: int
    probe_objects_created: int
    persistence_performed: bool
    memory_claim_permitted: bool
    decision: str
    reason: str
    result_digest: str

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"capture", "evaluation", "result_digest"}
        }
        payload["capture_digest"] = self.capture.capture_digest
        payload["evaluation_digest"] = self.evaluation.result_digest
        if (
            self.coordinator_id != S1_FJ_COORDINATOR_ID
            or not all(
                _valid_digest(value)
                for value in (
                    self.source_s1fh_contract_digest,
                    self.source_s1fi_preflight_digest,
                    self.source_inventory_digest,
                )
            )
            or not isinstance(self.capture, E1FormationS1FFCaptureResult)
            or not isinstance(self.evaluation, E1FormationS1FDStateConvergenceResult)
            or self.evaluation.decision
            != "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY"
            or (self.formation_results_consumed, self.captured_state_vectors)
            != (15, 15)
            or self.dry_integration_confirmed is not True
            or self.owner_authorization_present is not False
            or self.execution_permitted is not False
            or self.field_steps_executed != 0
            or self.probe_objects_created != 0
            or self.persistence_performed is not False
            or self.memory_claim_permitted is not False
            or self.decision
            != "SYNTHETIC_COORDINATION_CONFIRMED_FRESH_EXECUTION_STILL_CLOSED"
            or not self.reason
            or self.result_digest != _digest(payload)
        ):
            raise E1FormationS1FJSyntheticCoordinatorError(
                "S1-FJ coordinator result changed or opened execution"
            )


def coordinate_e1_formation_s1fj_synthetically(
    contract: E1FormationS1FHFreshCaptureOneShotContract,
    preflight: E1FormationS1FIFreshCapturePreflight,
    inventory: E1FormationS1FJSyntheticInventory,
) -> E1FormationS1FJSyntheticCoordinatorResult:
    """Dry-integrate supplied typed results; never invoke a result provider."""

    if not isinstance(contract, E1FormationS1FHFreshCaptureOneShotContract):
        raise E1FormationS1FJSyntheticCoordinatorError(
            "S1-FJ requires the typed S1-FH contract"
        )
    if not isinstance(preflight, E1FormationS1FIFreshCapturePreflight):
        raise E1FormationS1FJSyntheticCoordinatorError(
            "S1-FJ requires the typed S1-FI preflight"
        )
    if not isinstance(inventory, E1FormationS1FJSyntheticInventory):
        raise E1FormationS1FJSyntheticCoordinatorError(
            "S1-FJ requires one prebuilt synthetic inventory"
        )
    contract.__post_init__()
    preflight.__post_init__()
    inventory.__post_init__()
    if (
        preflight.source_s1fh_contract_digest != contract.contract_digest
        or preflight.technical_preflight_passed is not True
        or preflight.owner_authorization_present is not False
        or preflight.execution_permitted is not False
        or inventory.source_input_manifest_digest
        != preflight.input_manifest_digest
        or inventory.field_steps_executed != 0
    ):
        raise E1FormationS1FJSyntheticCoordinatorError(
            "S1-FJ source bindings are incomplete or not closed"
        )
    capture = capture_e1_formation_s1ff_in_memory(inventory.results)
    evaluation = evaluate_e1_formation_s1fd_state_convergence(
        capture.state_vectors
    )
    if evaluation.decision != "FORMATION_STATE_CONVERGED_DIAGNOSTIC_ONLY":
        raise E1FormationS1FJSyntheticCoordinatorError(
            "S1-FJ synthetic fixture did not reach its registered diagnostic"
        )
    values = {
        "coordinator_id": S1_FJ_COORDINATOR_ID,
        "source_s1fh_contract_digest": contract.contract_digest,
        "source_s1fi_preflight_digest": preflight.preflight_digest,
        "source_inventory_digest": inventory.fixture_digest,
        "capture": capture,
        "evaluation": evaluation,
        "formation_results_consumed": 15,
        "captured_state_vectors": 15,
        "dry_integration_confirmed": True,
        "owner_authorization_present": False,
        "execution_permitted": False,
        "field_steps_executed": 0,
        "probe_objects_created": 0,
        "persistence_performed": False,
        "memory_claim_permitted": False,
        "decision": (
            "SYNTHETIC_COORDINATION_CONFIRMED_FRESH_EXECUTION_STILL_CLOSED"
        ),
        "reason": (
            "formation-only-input-preflight-to-fifteen-result-capture-and-"
            "diagnostic-evaluation-dry-integrated;no-field-execution"
        ),
    }
    digest_payload = {
        name: value
        for name, value in values.items()
        if name not in {"capture", "evaluation"}
    }
    digest_payload["capture_digest"] = capture.capture_digest
    digest_payload["evaluation_digest"] = evaluation.result_digest
    return E1FormationS1FJSyntheticCoordinatorResult(
        **values,
        result_digest=_digest(digest_payload),
    )
