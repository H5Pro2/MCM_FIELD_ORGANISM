"""S1-FF pure in-memory adapter for typed E1 formation results."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_confirmation_prepared_real_formation_kernel import (
    E1PreparedRealFormationArmResult,
    E1ConfirmationPreparedRealFormationKernelError,
)
from .e1_formation_s1fd_state_convergence_evaluator import (
    E1FormationS1FDSyntheticStateVector,
)
from .e1_formation_s1fe_endpoint_capture_contract import (
    E1FormationS1FEEndpointCaptureContract,
    S1_FE_ROLE_MAP,
    audit_e1_formation_s1fe_endpoint_capture_contract,
)
from .e1_refined_formation_runner import _digest


class E1FormationS1FFInMemoryCaptureAdapterError(ValueError):
    """Raised when typed formation outputs cannot be captured atomically."""


S1_FF_ADAPTER_ID = "e1.formation-endpoint-in-memory-capture-adapter.s1ff.v1"


@dataclass(frozen=True, slots=True)
class E1FormationS1FFCaptureResult:
    adapter_id: str
    contract_digest: str
    source_result_digests: tuple[str, ...]
    state_vectors: tuple[E1FormationS1FDSyntheticStateVector, ...] = field(
        repr=False
    )
    source_result_count: int
    each_source_result_consumed_once: bool
    source_state_objects_separated: bool
    synthetic_in_memory_capture_performed: bool
    formation_execution_performed: bool
    probe_execution_performed: bool
    persistence_performed: bool
    memory_claim_allowed: bool
    capture_digest: str

    def __post_init__(self) -> None:
        vectors = tuple(self.state_vectors)
        source_digests = tuple(self.source_result_digests)
        payload = {
            "adapter_id": self.adapter_id,
            "contract_digest": self.contract_digest,
            "source_result_digests": source_digests,
            "state_digests": tuple(item.state_digest for item in vectors),
            "source_result_count": len(source_digests),
            "each_source_result_consumed_once": len(set(source_digests)) == 15,
            "source_state_objects_separated": self.source_state_objects_separated,
            "synthetic_in_memory_capture_performed": True,
            "formation_execution_performed": False,
            "probe_execution_performed": False,
            "persistence_performed": False,
            "memory_claim_allowed": False,
        }
        if (
            self.adapter_id != S1_FF_ADAPTER_ID
            or len(source_digests) != 15
            or len(vectors) != 15
            or self.source_result_count != 15
            or self.each_source_result_consumed_once is not True
            or len(set(source_digests)) != 15
            or tuple(item.source_formation_result_digest for item in vectors)
            != source_digests
            or self.source_state_objects_separated is not True
            or self.synthetic_in_memory_capture_performed is not True
            or any(
                value is not False
                for value in (
                    self.formation_execution_performed,
                    self.probe_execution_performed,
                    self.persistence_performed,
                    self.memory_claim_allowed,
                )
            )
            or self.capture_digest != _digest(payload)
        ):
            raise E1FormationS1FFInMemoryCaptureAdapterError(
                "S1-FF capture result differs from its atomic source inventory"
            )
        for item in vectors:
            item.__post_init__()
        object.__setattr__(self, "source_result_digests", source_digests)
        object.__setattr__(self, "state_vectors", vectors)


def _capture_vector(
    result: E1PreparedRealFormationArmResult,
    formation_role: str,
) -> E1FormationS1FDSyntheticStateVector:
    edge_ids = tuple(_digest(item.edge) for item in result.output_state.edge_bindings)
    bindings = tuple(item.binding for item in result.output_state.edge_bindings)
    state_payload = {
        "refinement_id": result.refinement_id,
        "formation_role": formation_role,
        "edge_inventory_digest": _digest(edge_ids),
        "ordered_edge_ids": edge_ids,
        "ordered_binding_vector": bindings,
        "source_formation_result_digest": result.result_digest,
        "resource_budget_error": result.audit.resource_budget_error,
    }
    return E1FormationS1FDSyntheticStateVector(
        **state_payload,
        state_digest=_digest(state_payload),
    )


def capture_e1_formation_s1ff_in_memory(
    results: tuple[E1PreparedRealFormationArmResult, ...],
    contract: E1FormationS1FEEndpointCaptureContract | None = None,
) -> E1FormationS1FFCaptureResult:
    """Convert exactly 15 existing typed results without running formation."""

    source = contract or audit_e1_formation_s1fe_endpoint_capture_contract()
    if not isinstance(source, E1FormationS1FEEndpointCaptureContract):
        raise E1FormationS1FFInMemoryCaptureAdapterError(
            "S1-FF requires the typed S1-FE contract"
        )
    source.__post_init__()
    results = tuple(results)
    role_map = dict(S1_FE_ROLE_MAP)
    expected = tuple(
        (refinement_id, arm_id)
        for refinement_id, _ in source.source_refinements
        for arm_id in source.source_formation_arms
    )
    if (
        len(results) != source.required_source_result_count
        or not all(isinstance(item, E1PreparedRealFormationArmResult) for item in results)
        or tuple((item.refinement_id, item.arm_id) for item in results) != expected
    ):
        raise E1FormationS1FFInMemoryCaptureAdapterError(
            "S1-FF requires the canonical atomic 15-result inventory"
        )
    try:
        for item in results:
            item.__post_init__()
    except E1ConfirmationPreparedRealFormationKernelError as exc:
        raise E1FormationS1FFInMemoryCaptureAdapterError(
            "S1-FF source result validation failed"
        ) from exc
    result_digests = tuple(item.result_digest for item in results)
    state_object_ids = tuple(id(item.output_state) for item in results)
    if len(set(result_digests)) != 15 or len(set(state_object_ids)) != 15:
        raise E1FormationS1FFInMemoryCaptureAdapterError(
            "S1-FF source results or state objects are not separated"
        )
    source_edge_inventory = results[0].output_state.edge_inventory_digest
    source_edges = results[0].output_state.edges
    if any(
        item.output_state.edge_inventory_digest != source_edge_inventory
        or item.output_state.edges != source_edges
        for item in results[1:]
    ):
        raise E1FormationS1FFInMemoryCaptureAdapterError(
            "S1-FF source edge inventory differs across formation results"
        )
    vectors = tuple(
        _capture_vector(item, role_map[item.arm_id]) for item in results
    )
    capture_values = {
        "adapter_id": S1_FF_ADAPTER_ID,
        "contract_digest": source.contract_digest,
        "source_result_digests": result_digests,
        "state_vectors": vectors,
        "source_result_count": 15,
        "each_source_result_consumed_once": True,
        "source_state_objects_separated": True,
        "synthetic_in_memory_capture_performed": True,
        "formation_execution_performed": False,
        "probe_execution_performed": False,
        "persistence_performed": False,
        "memory_claim_allowed": False,
    }
    digest_payload = dict(capture_values)
    del digest_payload["state_vectors"]
    digest_payload["state_digests"] = tuple(
        item.state_digest for item in vectors
    )
    return E1FormationS1FFCaptureResult(
        **capture_values,
        capture_digest=_digest(digest_payload),
    )
