"""S1-EC100 closed same-process handoff from typed probes through EC99/EC98."""

from __future__ import annotations

from dataclasses import dataclass, field

from .e1_common_probe_ec91_refinement_receipts_converters import (
    E1CommonProbeEC91ProbeReceipt,
)
from .e1_common_probe_ec98_atomic_vector_receipt import (
    E1CommonProbeEC98AtomicVectorReceipt,
)
from .e1_common_probe_ec99_typed_vector_input_adapters import (
    E1CommonProbeEC99TypedVectorAdapterResult,
    _synthetic_r2_receipt,
    _synthetic_refined_receipt,
    adapt_e1_common_probe_ec99_typed_vector_inputs,
)
from .e1_common_probe_identifiability_contract import S1_EC45_PROBE_ROLES
from .e1_common_probe_n2_r2_positive_step_receipt_contract import (
    E1PositiveStepProbeReceipt,
)
from .e1_refined_formation_runner import _digest


class E1CommonProbeEC100AtomicVectorHandoffError(ValueError):
    """Raised when the EC100 source or atomic result leaves its closed scope."""


S1_EC100_SOURCE_ID = "e1.common-probe-vector-source-bundle.s1ec100.v1"
S1_EC100_HANDOFF_ID = "e1.common-probe-atomic-vector-handoff.s1ec100.v1"
S1_EC100_FIXTURE_ID = "e1.common-probe-atomic-vector-handoff-fixture.s1ec100.v1"


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC100SourceBundle:
    source_id: str
    r2_receipt_digests: tuple[str, ...]
    r4_r8_receipt_digests: tuple[str, ...]
    refinement_counts: tuple[tuple[str, int], ...]
    all_receipts_typed: bool
    all_roles_ordered: bool
    field_execution_permitted: bool
    persistence_permitted: bool
    ec46_decision_permitted: bool
    claims_permitted: bool
    bundle_digest: str
    r2_probes: tuple[E1PositiveStepProbeReceipt, ...] = field(
        repr=False, compare=False
    )
    r4_r8_probes: tuple[E1CommonProbeEC91ProbeReceipt, ...] = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name not in {"bundle_digest", "r2_probes", "r4_r8_probes"}
        }
        expected_refined_order = tuple(
            (refinement, role)
            for refinement in ("r4", "r8")
            for role in S1_EC45_PROBE_ROLES
        )
        if (
            self.source_id != S1_EC100_SOURCE_ID
            or len(self.r2_probes) != 8
            or not all(
                isinstance(item, E1PositiveStepProbeReceipt)
                for item in self.r2_probes
            )
            or tuple(item.role_id for item in self.r2_probes)
            != S1_EC45_PROBE_ROLES
            or len(self.r4_r8_probes) != 16
            or not all(
                isinstance(item, E1CommonProbeEC91ProbeReceipt)
                for item in self.r4_r8_probes
            )
            or tuple(
                (item.refinement_id, item.role_id) for item in self.r4_r8_probes
            )
            != expected_refined_order
            or self.r2_receipt_digests
            != tuple(item.receipt_digest for item in self.r2_probes)
            or self.r4_r8_receipt_digests
            != tuple(item.receipt_digest for item in self.r4_r8_probes)
            or len(set((*self.r2_receipt_digests, *self.r4_r8_receipt_digests)))
            != 24
            or self.refinement_counts != (("r2", 8), ("r4", 8), ("r8", 8))
            or self.all_receipts_typed is not True
            or self.all_roles_ordered is not True
            or any(
                value is not False
                for value in (
                    self.field_execution_permitted,
                    self.persistence_permitted,
                    self.ec46_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.bundle_digest != _digest(payload)
        ):
            raise E1CommonProbeEC100AtomicVectorHandoffError(
                "S1-EC100 source bundle changed or opened execution"
            )
        for item in (*self.r2_probes, *self.r4_r8_probes):
            item.__post_init__()


def build_e1_common_probe_ec100_source_bundle(
    r2_probes: tuple[E1PositiveStepProbeReceipt, ...],
    r4_r8_probes: tuple[E1CommonProbeEC91ProbeReceipt, ...],
) -> E1CommonProbeEC100SourceBundle:
    """Bind all typed source receipts before any adapter is called."""

    r2 = tuple(r2_probes)
    refined = tuple(r4_r8_probes)
    values = {
        "source_id": S1_EC100_SOURCE_ID,
        "r2_receipt_digests": tuple(item.receipt_digest for item in r2),
        "r4_r8_receipt_digests": tuple(item.receipt_digest for item in refined),
        "refinement_counts": (("r2", len(r2)), ("r4", 8), ("r8", 8)),
        "all_receipts_typed": all(
            isinstance(item, E1PositiveStepProbeReceipt) for item in r2
        )
        and all(isinstance(item, E1CommonProbeEC91ProbeReceipt) for item in refined),
        "all_roles_ordered": tuple(item.role_id for item in r2)
        == S1_EC45_PROBE_ROLES
        and tuple((item.refinement_id, item.role_id) for item in refined)
        == tuple(
            (refinement, role)
            for refinement in ("r4", "r8")
            for role in S1_EC45_PROBE_ROLES
        ),
        "field_execution_permitted": False,
        "persistence_permitted": False,
        "ec46_decision_permitted": False,
        "claims_permitted": False,
    }
    return E1CommonProbeEC100SourceBundle(
        **values,
        bundle_digest=_digest(values),
        r2_probes=r2,
        r4_r8_probes=refined,
    )


@dataclass(frozen=True, slots=True)
class E1CommonProbeEC100AtomicVectorHandoffResult:
    handoff_id: str
    source_bundle_digest: str
    source_receipt_digests: tuple[str, ...]
    ec99_adapter_result_digest: str
    ec98_vector_receipt_digest: str
    handoff_sequence: tuple[str, ...]
    source_probe_count: int
    vector_input_count: int
    active_vector_count: int
    same_process_handoff: bool
    source_adapter_and_vector_receipt_returned_together: bool
    field_steps_executed: int
    persistence_performed: bool
    retry_permitted: bool
    ec46_decision_permitted: bool
    research_decision_permitted: bool
    claims_permitted: bool
    status: str
    result_digest: str
    source_bundle: E1CommonProbeEC100SourceBundle = field(
        repr=False, compare=False
    )
    adapter_result: E1CommonProbeEC99TypedVectorAdapterResult = field(
        repr=False, compare=False
    )
    vector_receipt: E1CommonProbeEC98AtomicVectorReceipt = field(
        repr=False, compare=False
    )

    def __post_init__(self) -> None:
        payload = {
            name: getattr(self, name)
            for name in self.__dataclass_fields__
            if name
            not in {
                "result_digest",
                "source_bundle",
                "adapter_result",
                "vector_receipt",
            }
        }
        expected_source_digests = (
            *self.source_bundle.r2_receipt_digests,
            *self.source_bundle.r4_r8_receipt_digests,
        )
        if (
            self.handoff_id != S1_EC100_HANDOFF_ID
            or self.source_bundle_digest != self.source_bundle.bundle_digest
            or self.source_receipt_digests != expected_source_digests
            or self.source_receipt_digests
            != self.adapter_result.source_receipt_digests
            or self.ec99_adapter_result_digest != self.adapter_result.result_digest
            or self.ec98_vector_receipt_digest != self.vector_receipt.receipt_digest
            or self.vector_receipt is not self.adapter_result.vector_receipt
            or self.handoff_sequence
            != (S1_EC100_SOURCE_ID, self.adapter_result.adapter_id, self.vector_receipt.contract_id)
            or (
                self.source_probe_count,
                self.vector_input_count,
                self.active_vector_count,
            )
            != (24, 24, 6)
            or self.same_process_handoff is not True
            or self.source_adapter_and_vector_receipt_returned_together is not True
            or self.field_steps_executed != 0
            or any(
                value is not False
                for value in (
                    self.persistence_performed,
                    self.retry_permitted,
                    self.ec46_decision_permitted,
                    self.research_decision_permitted,
                    self.claims_permitted,
                )
            )
            or self.status != "ATOMIC_EC99_TO_EC98_HANDOFF_READY_NO_EXECUTION"
            or self.result_digest != _digest(payload)
        ):
            raise E1CommonProbeEC100AtomicVectorHandoffError(
                "S1-EC100 atomic handoff changed or crossed closed scope"
            )


def build_e1_common_probe_ec100_atomic_vector_handoff(
    source_bundle: E1CommonProbeEC100SourceBundle,
) -> E1CommonProbeEC100AtomicVectorHandoffResult:
    """Synchronously return the source, EC99 result, and EC98 receipt together."""

    if not isinstance(source_bundle, E1CommonProbeEC100SourceBundle):
        raise E1CommonProbeEC100AtomicVectorHandoffError(
            "S1-EC100 requires one typed closed source bundle"
        )
    source_bundle.__post_init__()
    adapter_result = adapt_e1_common_probe_ec99_typed_vector_inputs(
        source_bundle.r2_probes, source_bundle.r4_r8_probes
    )
    vector_receipt = adapter_result.vector_receipt
    values = {
        "handoff_id": S1_EC100_HANDOFF_ID,
        "source_bundle_digest": source_bundle.bundle_digest,
        "source_receipt_digests": adapter_result.source_receipt_digests,
        "ec99_adapter_result_digest": adapter_result.result_digest,
        "ec98_vector_receipt_digest": vector_receipt.receipt_digest,
        "handoff_sequence": (
            source_bundle.source_id,
            adapter_result.adapter_id,
            vector_receipt.contract_id,
        ),
        "source_probe_count": len(adapter_result.source_receipt_digests),
        "vector_input_count": len(adapter_result.inputs),
        "active_vector_count": vector_receipt.active_vector_count,
        "same_process_handoff": True,
        "source_adapter_and_vector_receipt_returned_together": True,
        "field_steps_executed": 0,
        "persistence_performed": False,
        "retry_permitted": False,
        "ec46_decision_permitted": False,
        "research_decision_permitted": False,
        "claims_permitted": False,
        "status": "ATOMIC_EC99_TO_EC98_HANDOFF_READY_NO_EXECUTION",
    }
    return E1CommonProbeEC100AtomicVectorHandoffResult(
        **values,
        result_digest=_digest(values),
        source_bundle=source_bundle,
        adapter_result=adapter_result,
        vector_receipt=vector_receipt,
    )


def run_e1_common_probe_ec100_synthetic_fixture(
) -> E1CommonProbeEC100AtomicVectorHandoffResult:
    """Exercise the complete handoff using typed synthetic receipts only."""

    r2 = tuple(_synthetic_r2_receipt(role) for role in S1_EC45_PROBE_ROLES)
    refined = tuple(
        _synthetic_refined_receipt(refinement, role)
        for refinement in ("r4", "r8")
        for role in S1_EC45_PROBE_ROLES
    )
    source = build_e1_common_probe_ec100_source_bundle(r2, refined)
    return build_e1_common_probe_ec100_atomic_vector_handoff(source)
